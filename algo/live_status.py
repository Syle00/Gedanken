#!/usr/bin/env python3
"""Live-Status-Zyklus fuer MNQ: zieht den heutigen Handelstag per yfinance, laesst die
bestehenden Detektoren aus tools/analyze_ohlc.py + algo/rules.py darueber laufen und
gibt eine JSON-Zusammenfassung der *neuen* Ereignisse seit dem letzten Lauf aus.
Siehe docs/superpowers/specs/2026-08-04-algo-live-status-loop-design.md.

Aufruf:
    python algo/live_status.py                       # live: heutiger Handelstag
    python algo/live_status.py --dry-run 2026-07-31   # Pipeline gegen einen fertigen Tag testen
    python algo/live_status.py --selftest             # reine Funktions-Selbstchecks
"""

from __future__ import annotations

import json
import statistics
import sys
from dataclasses import asdict
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from analyze_ohlc import (  # noqa: E402
    Bar, load, fvgs, sweeps, structure_breaks, untouched_levels, macro_windows, org_gap,
    ndog_gap, nwog_gap, at, TF_MINUTES, CFG,
)
from rules import plan_trade, _active_window  # noqa: E402

import pandas as pd
import yfinance as yf

from fetch_yfinance import trading_day, flatten, SYMBOL  # noqa: E402

DISPLAY_SYMBOL = "MNQ"
# Tick-Raster des gehandelten Kontrakts -- abgeleitete Preise (FVG-C.E., ORG-C.E.)
# muessen darauf liegen, sonst sind es keine handelbaren Preise.
SYMBOL_TICK = DISPLAY_SYMBOL
INTERVALS = ["1m", "5m", "15m", "1h", "1d"]

BASE_TF = "5m"
_tf_min = TF_MINUTES[BASE_TF]
CFG.update(min_age=max(3, round(15 / _tf_min)), confirm=max(2, round(5 / _tf_min)))

LIVE_DIR = Path(__file__).resolve().parent / "live"
NY = ZoneInfo("America/New_York")


def _download(tf: str, start: str, end: str) -> pd.DataFrame:
    try:
        return flatten(yf.download(SYMBOL, start=start, end=end, interval=tf, progress=False))
    except Exception as exc:  # Netzwerk-/yfinance-Fehler sollen den Loop nicht abbrechen
        print(f"  ! {tf}: Download fehlgeschlagen ({exc})", file=sys.stderr)
        return pd.DataFrame()


def fetch_today(target_day: date) -> dict[str, pd.DataFrame]:
    """Alle INTERVALS + 4h (aus 1h resampled), gefiltert auf target_day ueber trading_day()
    (aus fetch_yfinance.py) -- die Globex-Session startet 18:00 NY am Vortag, ohne die
    Filterung landen Vorabend-Kerzen sonst unter dem falschen Kalendertag.

    `5m_unfiltered` ist bewusst die ungefilterte 5m-Rohspanne (mehrere Tage) -- org_gap()
    braucht die ~16:14-Schlusskerze des *Vortags*, die die Tages-Filterung sonst wegwirft."""
    start = (target_day - timedelta(days=3)).isoformat()
    end = (target_day + timedelta(days=1)).isoformat()
    dfs: dict[str, pd.DataFrame] = {}
    for tf in INTERVALS:
        raw = _download(tf, start, end)
        if tf == "5m":
            dfs["5m_unfiltered"] = raw
        if not raw.empty:
            daily = tf == "1d"
            raw = raw[raw.index.map(lambda ts: trading_day(ts, daily)) == target_day]
        dfs[tf] = raw

    hourly = dfs["1h"]
    if not hourly.empty:
        dfs["4h"] = (hourly.resample("4h").agg(
            {"Open": "first", "High": "max", "Low": "min", "Close": "last"}).dropna())
    else:
        dfs["4h"] = pd.DataFrame()
    return dfs


def write_live_day(tf: str, day: date, rows: pd.DataFrame) -> Path:
    dest = LIVE_DIR / day.isoformat() / f"{DISPLAY_SYMBOL} {day.isoformat()} {tf}.csv"
    dest.parent.mkdir(parents=True, exist_ok=True)
    out = pd.DataFrame({
        "time": rows.index.as_unit("s").astype("int64"),
        "open": rows["Open"].to_numpy(),
        "high": rows["High"].to_numpy(),
        "low": rows["Low"].to_numpy(),
        "close": rows["Close"].to_numpy(),
    })
    out.to_csv(dest, index=False)
    return dest


def _bars_from_df(df: pd.DataFrame) -> list[Bar]:
    """Wie load(), nur direkt aus einem yfinance-DataFrame statt einer CSV-Datei."""
    idx = df.index.tz_convert(NY)
    return [Bar(t.to_pydatetime(), float(o), float(h), float(l), float(c))
            for t, o, h, l, c in zip(idx, df["Open"], df["High"], df["Low"], df["Close"])]


def event_key(d: dict, field: str) -> list:
    """Identitaet eines Ereignisses ueber Laeufe hinweg: Kerzenzeit + Seite/Richtung."""
    t = d["t"]
    return [t.isoformat() if hasattr(t, "isoformat") else t, d[field]]


def load_state(path: Path) -> dict:
    if not path.exists():
        return {"fvgs": [], "sweeps": [], "structure_breaks": [], "setup": None}
    return json.loads(path.read_text(encoding="utf-8"))


def run_detectors(bars: list[Bar], day: date, now: datetime,
                   org_bars: list[Bar] | None = None) -> dict:
    """Reine Funktion: bestehende Detektoren auf `bars` (Basis-TF 5m, siehe BASE_TF) +
    plan_trade(). Feldnamen matchen die Kategorien aus diff_events() (Task 1).

    `org_bars` (optional, faellt sonst auf `bars` zurueck): breitere, ungescopte Kerzenreihe
    fuer org_gap() -- die braucht die ~16:14-Kerze des Vortags, die im Live-Betrieb VOR dem
    Tages-Filter von fetch_today() liegt und in `bars` (bereits auf `day` gescoped) fehlt."""
    if not bars:
        return {"price": None, "active_macro_window": None,
                "active_silver_bullet_window": None, "setup": None,
                "fvgs": [], "sweeps": [], "structure_breaks": [], "untouched_levels": [],
                "org_ce": None, "ndog": None, "nwog": None}

    # Detektor-Scope: die Globex-Session *dieses* Handelstages (18:00 NY am Vorabend bis
    # `now`) -- sonst tauchen Ereignisse vom Vortag in einem Bericht auf, der mit `day`
    # beschriftet ist, und die Zahlen sind nicht mit backtest_ohlc.py vergleichbar.
    # Die letzte Kerze wird abgeschnitten: sie ist im Live-Betrieb noch am Entstehen, und
    # ein daraus abgeleitetes Ereignis kann sich wieder aufloesen -- diff_events() kann
    # aber nur hinzufuegen, nie zuruecknehmen.
    session_start = at(day - timedelta(days=1), 18)
    scoped = [b for b in bars if session_start <= b.t <= now]
    stable_bars = scoped[:-1] if len(scoped) > 1 else scoped

    med_bar = (statistics.median(b.rng for b in stable_bars) or 1.0) if stable_bars else 1.0
    fg = fvgs(stable_bars, tick=SYMBOL_TICK)
    sw = sweeps(stable_bars, CFG["swing"], CFG["min_age"], CFG["min_pen"] * med_bar,
                CFG["confirm"])
    sb = structure_breaks(stable_bars, CFG["swing"], CFG["min_age"])
    setup = plan_trade(stable_bars, now)
    lv = untouched_levels(stable_bars, CFG["swing"])

    # Vor 18:00 NY liegt `now` noch in den Fenstern des *vorherigen* Handelstages --
    # `day` ist bereits globex-verschoben, deshalb beide Tage durchsuchen.
    active_macro = None
    for candidate_day in (day - timedelta(days=1), day):
        for name, start, end in macro_windows(candidate_day):
            if start <= now < end:
                active_macro = {"name": name, "start": start.isoformat(), "end": end.isoformat()}
                break
        if active_macro:
            break
    win = _active_window(day, now)

    last = bars[-1]  # Preis kommt bewusst von der *echten* letzten Kerze, inkl. laufender
    # org_gap()/ndog_gap() brauchen Kerzen des Vortags -- die liegen VOR session_start (18:00
    # Vorabend), deshalb hier bewusst auf `org_bars` (Default: `bars`) gerechnet, nicht stable_bars.
    wide_bars = org_bars if org_bars is not None else bars
    org = org_gap(wide_bars, day, tick=SYMBOL_TICK)
    ndog = ndog_gap(wide_bars, day)
    nwog = nwog_gap(wide_bars, day)  # None ausser montags, siehe nwog_gap()
    return {
        "price": {"last": last.c, "t": last.t.isoformat()},
        "active_macro_window": active_macro,
        "active_silver_bullet_window": win[0] if win else None,
        "setup": asdict(setup) if setup else None,
        "fvgs": fg, "sweeps": sw, "structure_breaks": sb, "untouched_levels": lv,
        "org_ce": org, "ndog": ndog, "nwog": nwog,
    }


def _setup_identity(s: dict | None):
    """Identitaet eines Setups *ohne* `t`: plan_trade() setzt t = Abfragezeitpunkt, nicht
    den Beginn des Setups. Ein unveraendertes Setup waere sonst in jedem Zyklus 'neu'."""
    if s is None:
        return None
    return (s["window"], s["side"], s["entry"], s["stop"], s["target"])


def diff_events(current: dict, prev_state: dict) -> tuple[list[dict], dict]:
    """Vergleicht aktuelle Detektor-Ergebnisse mit dem letzten gespeicherten Snapshot.
    Liefert (neue Ereignisse seit dem letzten Lauf, neuer Snapshot fuer state.json)."""
    new_events: list[dict] = []
    new_state: dict = {}
    categories = [("fvgs", "side"), ("sweeps", "side"), ("structure_breaks", "dir")]
    for field, side_field in categories:
        prev_keys = {tuple(k) for k in prev_state.get(field, [])}
        keys = []
        for d in current[field]:
            k = tuple(event_key(d, side_field))
            keys.append(list(k))
            if k not in prev_keys:
                new_events.append({"kind": field[:-1], **d})
        new_state[field] = keys

    prev_setup, cur_setup = prev_state.get("setup"), current["setup"]
    if cur_setup and _setup_identity(cur_setup) != _setup_identity(prev_setup):
        new_events.append({"kind": "setup_entered", **cur_setup})
    elif prev_setup and not cur_setup:
        new_events.append({"kind": "setup_exited", **prev_setup})
    new_state["setup"] = cur_setup

    return new_events, new_state


def selftest() -> None:
    t1 = datetime(2026, 8, 4, 10, 5)
    fvg = {"t": t1, "side": "bullish", "lo": 100.0, "hi": 101.0, "ce": 100.5}

    current = {"fvgs": [fvg], "sweeps": [], "structure_breaks": [], "setup": None}
    empty_state = {"fvgs": [], "sweeps": [], "structure_breaks": [], "setup": None}
    events, state = diff_events(current, empty_state)
    assert len(events) == 1 and events[0]["kind"] == "fvg", events

    events2, _ = diff_events(current, state)
    assert events2 == [], events2

    setup = {"t": t1, "window": "NY AM Silver Bullet", "side": "long",
             "entry": 100.5, "stop": 99.0, "target": 105.0}
    with_setup = {"fvgs": [], "sweeps": [], "structure_breaks": [], "setup": setup}
    events3, state3 = diff_events(with_setup, empty_state)
    assert any(e["kind"] == "setup_entered" for e in events3), events3

    without_setup = {"fvgs": [], "sweeps": [], "structure_breaks": [], "setup": None}
    events4, _ = diff_events(without_setup, state3)
    assert any(e["kind"] == "setup_exited" for e in events4), events4

    # Fix 1: gleiches Setup, nur ein anderer Abfragezeitpunkt -> kein neues Ereignis.
    same_setup_later = {**setup, "t": t1 + timedelta(minutes=10)}
    events5, state5 = diff_events(
        {"fvgs": [], "sweeps": [], "structure_breaks": [], "setup": same_setup_later}, state3)
    assert not any(e["kind"] == "setup_entered" for e in events5), events5
    assert state5["setup"]["t"] == same_setup_later["t"], state5  # `t` wird trotzdem persistiert
    # ...ein echt anderes Setup (anderer Entry) aber schon.
    moved_setup = {**same_setup_later, "entry": 101.5}
    events6, _ = diff_events(
        {"fvgs": [], "sweeps": [], "structure_breaks": [], "setup": moved_setup}, state5)
    assert any(e["kind"] == "setup_entered" for e in events6), events6

    print("selftest (Task 1: diff_events) ok")

    # Task 3: write_live_day mit synthetischen Daten -- kein Netzwerk noetig.
    idx = pd.date_range("2026-01-02 10:00", periods=2, freq="5min", tz="America/New_York")
    synth = pd.DataFrame({"Open": [100.0, 101.0], "High": [101.0, 102.0],
                           "Low": [99.5, 100.5], "Close": [100.5, 101.5]}, index=idx)
    dest = write_live_day("5m", date(2026, 1, 2), synth)
    assert dest.exists()
    written_bars = load(dest)
    assert len(written_bars) == 2 and written_bars[0].o == 100.0
    dest.unlink()
    dest.parent.rmdir()
    print("selftest (Task 3: write_live_day) ok")

    # Task 2: run_detectors gegen echte, bereits abgeschlossene Daten (31.07.2026).
    day_path = (Path(__file__).resolve().parent.parent / "raw" / "marktdaten"
                / "2026" / "07" / "31.07.2026" / "MNQ 2026-07-31 5m.csv")
    real_bars = load(day_path)
    day31 = date(2026, 7, 31)
    det = run_detectors(real_bars, day31, real_bars[-1].t)
    assert det["price"]["last"] == real_bars[-1].c
    assert isinstance(det["fvgs"], list) and isinstance(det["sweeps"], list)
    assert isinstance(det["untouched_levels"], list)  # Fix 5
    assert det["org_ce"] is not None and det["org_ce"]["filled_30m"] is True  # ORG-C.E.-Tracking
    assert det["ndog"] is not None and isinstance(det["ndog"]["filled"], bool)  # NDOG-Tracking
    assert day31.weekday() == 4 and det["nwog"] is None  # Freitag -> kein NWOG (nur montags)
    monday_path = (Path(__file__).resolve().parent.parent / "raw" / "marktdaten"
                   / "2026" / "07" / "20.07.2026" / "MNQ 2026-07-20 5m.csv")
    monday_bars = load(monday_path)
    monday_det = run_detectors(monday_bars, date(2026, 7, 20), monday_bars[-1].t)
    assert monday_det["nwog"] is not None and isinstance(monday_det["nwog"]["filled"], bool)
    empty_det = run_detectors([], day31, real_bars[-1].t)
    assert empty_det["price"] is None and empty_det["fvgs"] == []
    assert empty_det["untouched_levels"] == [] and empty_det["org_ce"] is None
    assert empty_det["ndog"] is None and empty_det["nwog"] is None

    # Fix 6: kein Ereignis vor Session-Start (18:00 NY am Vorabend), obwohl die CSV
    # bis 2026-07-30 15:00 zurueckreicht. `price` bleibt die echte letzte Kerze.
    session_start = at(day31 - timedelta(days=1), 18)
    assert real_bars[0].t < session_start, real_bars[0].t  # Vorbedingung des Tests
    for cat in ("fvgs", "sweeps", "structure_breaks", "untouched_levels"):
        assert all(e["t"] >= session_start for e in det[cat]), (cat, det[cat][:2])
    assert det["price"]["t"] == real_bars[-1].t.isoformat()

    # Fix 2: 20:00 NY am Vorabend gehoert per Globex bereits zu day31 -- das aktive
    # Makro-Fenster liegt dann in macro_windows(day31 - 1 Tag) und war frueher `null`.
    evening = run_detectors(real_bars, day31, at(day31 - timedelta(days=1), 20))
    assert evening["active_macro_window"] is not None, evening["active_macro_window"]
    assert evening["active_macro_window"]["name"] == "19:50-20:10", evening["active_macro_window"]
    print("selftest (Task 2: run_detectors) ok")


def _dry_run(day_str: str) -> dict:
    day = date.fromisoformat(day_str)
    path = (Path(__file__).resolve().parent.parent / "raw" / "marktdaten"
            / f"{day:%Y}" / f"{day:%m}" / f"{day:%d.%m.%Y}"
            / f"{DISPLAY_SYMBOL} {day.isoformat()} {BASE_TF}.csv")
    if not path.exists():
        return {"generated_at": datetime.now(NY).isoformat(), "day": day_str,
                "market_data": False, "error": f"keine {BASE_TF}-Datei fuer {day_str} gefunden",
                "price": None, "active_macro_window": None,
                "active_silver_bullet_window": None, "setup": None, "new_events": [],
                "first_run": False, "untouched_levels": [], "org_ce": None, "ndog": None,
                "nwog": None}
    bars = load(path)
    now = bars[-1].t
    det = run_detectors(bars, day, now)
    empty_state = {"fvgs": [], "sweeps": [], "structure_breaks": [], "setup": None}
    new_events, _ = diff_events(det, empty_state)
    # --dry-run vergleicht per Konstruktion immer gegen einen leeren State.
    return {"generated_at": now.isoformat(), "day": day_str, "market_data": True, "error": None,
            "price": det["price"], "active_macro_window": det["active_macro_window"],
            "active_silver_bullet_window": det["active_silver_bullet_window"],
            "setup": det["setup"], "new_events": new_events,
            "first_run": True, "untouched_levels": det["untouched_levels"], "org_ce": det["org_ce"],
            "ndog": det["ndog"], "nwog": det["nwog"]}


def _live_run() -> dict:
    now = datetime.now(NY)
    day = trading_day(pd.Timestamp(now))
    dfs = fetch_today(day)
    if dfs["5m"].empty:
        return {"generated_at": now.isoformat(), "day": day.isoformat(), "market_data": False,
                "error": "keine 5m-Daten (Markt geschlossen oder yfinance-Fehler)",
                "price": None, "active_macro_window": None,
                "active_silver_bullet_window": None, "setup": None, "new_events": [],
                "first_run": False, "untouched_levels": [], "org_ce": None, "ndog": None,
                "nwog": None}

    for tf, df in dfs.items():
        if tf != "5m_unfiltered" and not df.empty:
            write_live_day(tf, day, df)

    bars = load(LIVE_DIR / day.isoformat() / f"{DISPLAY_SYMBOL} {day.isoformat()} 5m.csv")
    org_bars = _bars_from_df(dfs["5m_unfiltered"]) if not dfs["5m_unfiltered"].empty else bars
    det = run_detectors(bars, day, now, org_bars=org_bars)

    state_path = LIVE_DIR / day.isoformat() / "state.json"
    first_run = not state_path.exists()  # vor dem Schreiben des neuen States pruefen
    prev_state = load_state(state_path)
    new_events, new_state = diff_events(det, prev_state)
    state_path.write_text(json.dumps(new_state, default=str, ensure_ascii=False, indent=2),
                          encoding="utf-8")

    return {"generated_at": now.isoformat(), "day": day.isoformat(), "market_data": True,
            "error": None, "price": det["price"], "active_macro_window": det["active_macro_window"],
            "active_silver_bullet_window": det["active_silver_bullet_window"],
            "setup": det["setup"], "new_events": new_events,
            "first_run": first_run, "untouched_levels": det["untouched_levels"], "org_ce": det["org_ce"],
            "ndog": det["ndog"], "nwog": det["nwog"]}


def main(argv=None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    ap = _build_arg_parser()
    a = ap.parse_args(args)
    sys.stdout.reconfigure(encoding="utf-8")

    if a.selftest:
        selftest()
        return 0

    summary = _dry_run(a.dry_run) if a.dry_run else _live_run()
    print(json.dumps(summary, default=str, ensure_ascii=False, indent=2))
    return 0


def _build_arg_parser():
    import argparse
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", metavar="YYYY-MM-DD",
                    help="Pipeline gegen einen fertigen Handelstag aus raw/marktdaten/ testen")
    ap.add_argument("--selftest", action="store_true",
                    help="Reine Funktions-Selbstchecks, kein Netzwerk/Dateizugriff")
    return ap


if __name__ == "__main__":
    sys.exit(main())
