#!/usr/bin/env python3
"""Live-Status-Zyklus fuer NQ: liest den heutigen Handelstag als IBKR-1s-Balken (ueber
marktdaten.bars(), bei Bedarf per fetch_ibkr nachgeholt), verdichtet ihn auf die noetigen
Timeframes, laesst die bestehenden Detektoren aus tools/analyze_ohlc.py + algo/rules.py
darueber laufen und gibt eine JSON-Zusammenfassung der *neuen* Ereignisse seit dem letzten
Lauf aus. Siehe docs/superpowers/specs/2026-08-04-algo-live-status-loop-design.md und
docs/superpowers/specs/2026-08-15-ibkr-1s-datenanbindung-design.md.

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

from marktdaten import resample_bars, bars as markt_bars  # noqa: E402
import fetch_ibkr  # noqa: E402

DISPLAY_SYMBOL = "NQ"
# Tick-Raster des gehandelten Kontrakts -- abgeleitete Preise (FVG-C.E., ORG-C.E.)
# muessen darauf liegen, sonst sind es keine handelbaren Preise. NQ laeuft wie MNQ in
# 0,25-Schritten, der Symbolwechsel aendert daran nichts.
SYMBOL_TICK = DISPLAY_SYMBOL
INTRADAY_TFS = ["1m", "5m", "15m", "1h", "4h"]
# Historie fuer open_gap_history(): 5 Handelstage (NDOG) + 5 Handelswochen (NWOG).
# 70 Kalendertage decken beides, und der von-Filter erspart markt_bars() das Einlesen
# aller ~6540 NQ-Tagesdateien bei jedem Zyklus.
DAILY_LOOKBACK_DAYS = 70

BASE_TF = "5m"
_tf_min = TF_MINUTES[BASE_TF]
CFG.update(min_age=max(3, round(15 / _tf_min)), confirm=max(2, round(5 / _tf_min)))

LIVE_DIR = Path(__file__).resolve().parent / "live"
NY = ZoneInfo("America/New_York")


def _live_1s(day: date) -> list[Bar]:
    """Laufender Handelstag: bereits geholte 1s-Kerzen aus dem transienten Puffer unter
    algo/live/ plus die seither entstandenen, ueber fetch_ibkr.live_fenster() (kein
    raw/marktdaten/-Schreibvorgang, keine Registerzeile -- Begruendung dort). Der Puffer
    macht den Abruf inkrementell: je Zyklus 1-2 Fenster statt 46, nur der erste Lauf eines
    Tages holt die bis dahin verstrichene Session am Stueck.

    Der Puffer wird jedes Mal komplett neu geschrieben und liegt bewusst NICHT in
    raw/marktdaten/ -- er ist ein Zwischenstand, keine Tagesdatei, und kann deshalb weder
    einfrieren noch mit einer echten verwechselt werden."""
    puffer = LIVE_DIR / day.isoformat() / f"{DISPLAY_SYMBOL} {day.isoformat()} 1s-live.csv"
    bisher = load(puffer) if puffer.exists() else []
    # Sessionbeginn 18:00 NY am Vorabend, siehe fetch_ibkr.day_windows().
    seit = bisher[-1].t if bisher else at(day - timedelta(days=1), 18)
    zeilen = fetch_ibkr.live_fenster(DISPLAY_SYMBOL, day, seit)
    neu = [Bar(datetime.fromtimestamp(z["time"], NY), float(z["open"]), float(z["high"]),
               float(z["low"]), float(z["close"])) for z in zeilen]
    alle = bisher + neu
    if neu:
        write_live_day("1s-live", day, alle)
    return alle


def _download_1s(day: date, holen: bool = True) -> list[Bar]:
    """Handelstag als 1s-Balken, je nach Tag aus zwei Quellen.

    **Abgeschlossener Tag:** aus raw/marktdaten/ -- hat /daten-1s den Tag schon gezogen,
    kostet das keinen IBKR-Request. Sonst denselben Weg nehmen, den /daten-1s nutzt:
    fetch_ibkr.main() schreibt die Tagesdatei (und startet dabei selbst das Gateway), danach
    wird sie gelesen. Bewusst der Umweg ueber die Datei statt eines direkten Rueckgabewerts:
    Live-Betrieb und Backtest sehen so garantiert dieselben Bytes.

    **Laufender Tag:** ueber _live_1s()/fetch_ibkr.live_fenster(), also ohne jede Datei in
    raw/marktdaten/ -- eine mitten am Tag geschriebene Tagesdatei waere dauerhaft als
    vollstaendiger Handelstag eingefroren (Begruendung in live_fenster()). Eine trotzdem
    vorhandene Tagesdatei des laufenden Tages wird bewusst ignoriert: sie kann nur ein
    solcher Teiltag sein.

    Fehler duerfen den Loop nicht abbrechen -- dann bleibt die Liste leer und der Aufrufer
    meldet "keine Daten", statt zu raten. `holen=False` unterbindet jeden Abruf (--dry-run).
    Am laufenden Tag gilt zusaetzlich eine Frischegrenze von 20 Minuten: aeltere Kerzen sind
    kein Live-Stand, und eine Zahl, die aktuell aussieht und es nicht ist, ist schlechter als
    gar keine (CLAUDE.md, "Frische Live-Daten bei Zukunftsfragen")."""
    jetzt = datetime.now(NY)
    laeuft_noch = jetzt < at(day, 17)  # Session endet 17:00 NY, siehe fetch_ibkr.day_windows()
    if laeuft_noch:
        if not holen:
            return []
        try:
            kerzen = _live_1s(day)
        except Exception as exc:  # Gateway nicht erreichbar, Fenster fehlgeschlagen, ...
            print(f"  ! 1s: IBKR-Livefenster fehlgeschlagen ({exc})", file=sys.stderr)
            return []
        if not kerzen:
            print(f"  ! 1s: IBKR liefert fuer {day} noch keine Kerzen", file=sys.stderr)
            return []
        alter = jetzt - kerzen[-1].t
        if alter > timedelta(minutes=20):
            print(f"  ! 1s: letzte Kerze {kerzen[-1].t:%H:%M:%S} NY, jetzt ist "
                  f"{jetzt:%H:%M:%S} NY ({alter} alt) -- kein Live-Stand", file=sys.stderr)
            return []
        return kerzen
    vorhanden = markt_bars(DISPLAY_SYMBOL, "1s", von=day, bis=day)
    if vorhanden or not holen:
        if not vorhanden:
            print(f"  ! 1s: keine Tagesdatei fuer {day} in raw/marktdaten/", file=sys.stderr)
        return vorhanden
    try:
        fetch_ibkr.main(["--backfill", day.isoformat(), day.isoformat(),
                         "--symbol", DISPLAY_SYMBOL, "--kein-fenster"])
    except Exception as exc:  # Gateway-/Netzwerkfehler sollen den Loop nicht abbrechen
        print(f"  ! 1s: IBKR-Abruf fehlgeschlagen ({exc})", file=sys.stderr)
        return []
    return markt_bars(DISPLAY_SYMBOL, "1s", von=day, bis=day)


def fetch_today(target_day: date, holen: bool = True) -> dict[str, list[Bar]]:
    """Alle INTRADAY_TFS aus dem 1s-Strom des Tages, 1d aus dem CSV-Bestand. Die
    Globex-Session startet 18:00 NY am Vortag -- markt_bars()/_load_1s_parquet() liefern
    bereits NY-lokalisierte Zeitstempel und die Tagesdatei enthaelt genau einen Handelstag,
    deshalb entfaellt die frueher noetige trading_day()-Nachfilterung des
    yfinance-Kalenderschnitts.

    `5m_weit` haengt die Vortage vor die heutigen 5m-Kerzen -- org_gap() braucht die
    ~16:14-Schlusskerze des *Vortags*, die vor dem Beginn der heutigen Tagesdatei (18:00
    Vorabend) liegt. Die Vortage werden nur gelesen, nie geholt: fehlen sie, bleibt org_ce
    None, statt falsch zu werden."""
    eins = _download_1s(target_day, holen=holen)
    out: dict[str, list[Bar]] = {tf: (resample_bars(eins, tf) if eins else [])
                                 for tf in INTRADAY_TFS}
    vortage = markt_bars(DISPLAY_SYMBOL, "1s", von=target_day - timedelta(days=3),
                         bis=target_day - timedelta(days=1))
    out["5m_weit"] = (resample_bars(vortage, "5m") + out["5m"]) if vortage else out["5m"]
    out["1d"] = markt_bars(DISPLAY_SYMBOL, "1d",
                           von=target_day - timedelta(days=DAILY_LOOKBACK_DAYS),
                           bis=target_day)
    return out


def write_live_day(tf: str, day: date, rows: list[Bar]) -> Path:
    """Schreibt die Kerzen im CSV-Format von tools/analyze_ohlc.py::load() (UNIX-Sekunden)
    nach algo/live/<tag>/ -- transienter Zwischenstand fuer Nachschau/Debugging, nicht Teil
    von raw/marktdaten/."""
    dest = LIVE_DIR / day.isoformat() / f"{DISPLAY_SYMBOL} {day.isoformat()} {tf}.csv"
    dest.parent.mkdir(parents=True, exist_ok=True)
    zeilen = ["time,open,high,low,close"]
    zeilen += [f"{int(b.t.timestamp())},{b.o},{b.h},{b.l},{b.c}" for b in rows]
    dest.write_text("\n".join(zeilen) + "\n", encoding="utf-8")
    return dest


def open_gap_history(daily_bars: list[Bar], upto_day: date, n: int, weekly: bool) -> list[dict]:
    """Noch nicht gefuellte NDOG- (weekly=False) bzw. NWOG-Level (weekly=True) der letzten `n`
    Handelstage/-wochen vor `upto_day` -- die DOL-These aus dem Daily-Bias-Journal vom 2026-08-13:
    NDOG bleibt mind. 5 Handelstage, NWOG mind. 5 Handelswochen aktiv, siehe
    wiki/concepts/New Day Opening Gap (NDOG).md. `ndog_gap()`/`nwog_gap()` selbst pruefen nur
    den Fill am Gap-Tag; hier wird stattdessen ueber alle Tage bis `upto_day` geprueft."""
    all_days = sorted({b.t.date() for b in daily_bars})
    prior_days = [d for d in all_days if d < upto_day]
    if weekly:
        prior_days = [d for d in prior_days if d.weekday() == 0]
    out = []
    for d in prior_days[-n:]:
        gap = (nwog_gap if weekly else ndog_gap)(daily_bars, d)
        if gap is None:
            continue
        level = gap["prev_close"]
        later = [b for b in daily_bars if d < b.t.date() <= upto_day]
        if not any(b.l <= level <= b.h for b in later):
            out.append({"day": d.isoformat(), "level": level, "gap": gap["gap"]})
    return out


def event_key(d: dict, field: str) -> list:
    """Identitaet eines Ereignisses ueber Laeufe hinweg: Kerzenzeit + Seite/Richtung."""
    t = d["t"]
    return [t.isoformat() if hasattr(t, "isoformat") else t, d[field]]


def load_state(path: Path) -> dict:
    if not path.exists():
        return {"fvgs": [], "sweeps": [], "structure_breaks": [], "setup": None}
    return json.loads(path.read_text(encoding="utf-8"))


def run_detectors(bars: list[Bar], day: date, now: datetime,
                   org_bars: list[Bar] | None = None,
                   daily_bars: list[Bar] | None = None) -> dict:
    """Reine Funktion: bestehende Detektoren auf `bars` (Basis-TF 5m, siehe BASE_TF) +
    plan_trade(). Feldnamen matchen die Kategorien aus diff_events() (Task 1).

    `org_bars` (optional, faellt sonst auf `bars` zurueck): breitere, ungescopte Kerzenreihe
    fuer org_gap() -- die braucht die ~16:14-Kerze des Vortags, die im Live-Betrieb VOR dem
    Tages-Filter von fetch_today() liegt und in `bars` (bereits auf `day` gescoped) fehlt.

    `daily_bars` (optional): 1d-Kerzen ueber ~70 Tage fuer open_gap_history() (noch offene
    NDOG/NWOG-Level der letzten 5 Handelstage/-wochen). None -> beide Historien leer."""
    # Kein Lookahead: `bars` wird unten auf `now` gescoped, `daily_bars` braucht dieselbe
    # Grenze. Eine 1d-Kerze von `day` selbst ist am laufenden Tag noch nicht fertig -- ihre
    # High/Low wuerden in open_gap_history() ueber "Gap gefuellt oder nicht" entscheiden,
    # obwohl der Tag noch laeuft. Das ist die einzige Stelle im Live-Bericht, an der eine
    # fertige Zukunftskerze auftauchen koennte; ganze Tageskerzen sind erst ab dem Folgetag
    # bekannt, deshalb der Schnitt am Kalendertag statt an `now`.
    if daily_bars:
        daily_bars = [b for b in daily_bars if b.t.date() < day]
    ndog_open_hist = open_gap_history(daily_bars, day, 5, weekly=False) if daily_bars else []
    nwog_open_hist = open_gap_history(daily_bars, day, 5, weekly=True) if daily_bars else []
    if not bars:
        return {"price": None, "active_macro_window": None,
                "active_silver_bullet_window": None, "setup": None,
                "fvgs": [], "sweeps": [], "structure_breaks": [], "untouched_levels": [],
                "org_ce": None, "ndog_today": None, "nwog_today": None,
                "ndog_open_history": ndog_open_hist, "nwog_open_history": nwog_open_hist}

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
    org = org_gap(wide_bars, day, tick=SYMBOL_TICK, symbol=DISPLAY_SYMBOL)
    ndog = ndog_gap(wide_bars, day, symbol=DISPLAY_SYMBOL)
    nwog = nwog_gap(wide_bars, day)  # None ausser montags, siehe nwog_gap()
    return {
        "price": {"last": last.c, "t": last.t.isoformat()},
        "active_macro_window": active_macro,
        "active_silver_bullet_window": win[0] if win else None,
        "setup": asdict(setup) if setup else None,
        "fvgs": fg, "sweeps": sw, "structure_breaks": sb, "untouched_levels": lv,
        "org_ce": org, "ndog_today": ndog, "nwog_today": nwog,
        "ndog_open_history": ndog_open_hist, "nwog_open_history": nwog_open_hist,
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
    synth = [Bar(datetime(2026, 1, 2, 10, 0, tzinfo=NY), 100.0, 101.0, 99.5, 100.5),
             Bar(datetime(2026, 1, 2, 10, 5, tzinfo=NY), 101.0, 102.0, 100.5, 101.5)]
    dest = write_live_day("5m", date(2026, 1, 2), synth)
    assert dest.exists()
    written_bars = load(dest)
    assert len(written_bars) == 2 and written_bars[0].o == 100.0
    dest.unlink()
    dest.parent.rmdir()
    print("selftest (Task 3: write_live_day) ok")

    # Task 2: run_detectors gegen echte, bereits abgeschlossene Daten (31.07.2026).
    # ⚠️ Letzter Micro/Mini-Beruehrungspunkt im Code: hier laufen MNQ-CSVs durch
    # run_detectors(), das intern mit DISPLAY_SYMBOL == "NQ" rechnet (SYMBOL_TICK,
    # org_gap(symbol=...), ndog_gap(symbol=...)). Numerisch folgenlos -- beide Kontrakte
    # haben Tickgroesse 0,25 und denselben Sessiontyp -- und bewusst so belassen, weil es
    # fuer NQ keine 5m-CSVs mit dieser Historie gibt. Keine Vorlage: im Produktivpfad
    # duerfen Micro- und Mini-Kerzen nie in derselben Reihe landen.
    # Bewusst Vortag + Tag zusammen: die Tagesdatei beginnt 18:00 NY am Vorabend, org_gap()
    # braucht aber die ~16:14-Schlusskerze des Vortags -- genau der Grund, warum
    # fetch_today() im Betrieb `5m_weit` mitliefert. Frueher reichte die 31.07-Datei allein
    # zurueck bis 30.07 15:00; seit sie auf die Globex-Session gekuerzt wurde (Commit
    # 6135627ee, "aus 1m neu resampled") lief dieser Selbstcheck auf None.
    def _mnq(tag: date) -> list[Bar]:
        return load(Path(__file__).resolve().parent.parent / "raw" / "marktdaten"
                    / f"{tag:%Y}" / f"{tag:%m}" / f"{tag:%d.%m.%Y}"
                    / f"MNQ {tag.isoformat()} 5m.csv")

    day31 = date(2026, 7, 31)
    real_bars = sorted(_mnq(date(2026, 7, 30)) + _mnq(day31), key=lambda b: b.t)
    det = run_detectors(real_bars, day31, real_bars[-1].t)
    assert det["price"]["last"] == real_bars[-1].c
    assert isinstance(det["fvgs"], list) and isinstance(det["sweeps"], list)
    assert isinstance(det["untouched_levels"], list)  # Fix 5
    assert det["org_ce"] is not None and det["org_ce"]["filled_30m"] is True  # ORG-C.E.-Tracking
    assert det["ndog_today"] is not None and isinstance(det["ndog_today"]["filled"], bool)  # NDOG-Tracking
    assert day31.weekday() == 4 and det["nwog_today"] is None  # Freitag -> kein NWOG (nur montags)
    monday_bars = _mnq(date(2026, 7, 20))
    monday_det = run_detectors(monday_bars, date(2026, 7, 20), monday_bars[-1].t)
    assert monday_det["nwog_today"] is not None and isinstance(monday_det["nwog_today"]["filled"], bool)
    empty_det = run_detectors([], day31, real_bars[-1].t)
    assert empty_det["price"] is None and empty_det["fvgs"] == []
    assert empty_det["untouched_levels"] == [] and empty_det["org_ce"] is None
    assert empty_det["ndog_today"] is None and empty_det["nwog_today"] is None

    # Fix 6: kein Ereignis vor Session-Start (18:00 NY am Vorabend), obwohl die Kerzenreihe
    # bis 2026-07-29 18:00 zurueckreicht. `price` bleibt die echte letzte Kerze.
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

    # open_gap_history(): synthetische Tageskerzen. Aug3 (Montag) hat keinen Vortag ->
    # sein eigenes Gap ist None und wird uebersprungen; die Gaps von Aug4-Aug6 bleiben alle
    # unerreicht (kein spaeteres Low/High beruehrt das jeweilige Vortages-Close-Level).
    def db(d, o, h, l, c):
        return Bar(datetime(d.year, d.month, d.day, tzinfo=NY), o, h, l, c)
    daily = [
        db(date(2026, 8, 3), 99, 101, 98, 100),    # Montag, Close 100
        db(date(2026, 8, 4), 103, 104, 102, 103),  # Gap-Level 100 (Aug3-Close), nie wieder beruehrt
        db(date(2026, 8, 5), 104, 106, 103, 105),  # Gap-Level 103 (Aug4-Close), nie wieder beruehrt
        db(date(2026, 8, 6), 110, 112, 108, 111),  # Gap-Level 105 (Aug5-Close), nie wieder beruehrt
    ]
    ndh = open_gap_history(daily, date(2026, 8, 7), 5, weekly=False)
    assert {g["day"] for g in ndh} == {"2026-08-04", "2026-08-05", "2026-08-06"}, ndh
    assert {g["level"] for g in ndh} == {100.0, 103.0, 105.0}, ndh
    nwh = open_gap_history(daily, date(2026, 8, 7), 5, weekly=True)
    assert nwh == [], nwh  # einzig vorhandener Montag (Aug3) hat selbst keinen Vortag -> kein Gap
    print("selftest (open_gap_history) ok")

    # --- Symbol und Datenquelle ------------------------------------------
    assert DISPLAY_SYMBOL == "NQ", f"live_status laeuft auf NQ, nicht {DISPLAY_SYMBOL}"
    assert "yfinance" not in sys.modules, "live_status darf yfinance nicht mehr importieren"

    # --- 1s -> 5m ohne Netz: resample_bars liefert BASE_TF ----------------
    # 300 aufeinanderfolgende 1s-Kerzen ab 9:30:00 (per timedelta statt Sekundenfeld -- ueber
    # 59 waere das ein ValueError).
    eine_min = [Bar(datetime(2026, 8, 14, 9, 30, tzinfo=NY) + timedelta(seconds=s),
                    23000.0 + s, 23001.0 + s, 22999.0 + s, 23000.5 + s)
                for s in range(0, 300, 1)]
    fuenf = resample_bars(eine_min, "5m")
    assert len(fuenf) == 1, f"300 1s-Kerzen ergeben 1 5m-Kerze, nicht {len(fuenf)}"
    assert fuenf[0].h == max(b.h for b in eine_min), "high der 5m-Kerze = Maximum der 1s-Kerzen"

    # --- laufender Handelstag: Livefenster statt Tagesdatei -----------------
    # Gegen einen Stub statt gegen IBKR: der Live-Pfad muss auch ohne Gateway pruefbar sein.
    # `morgen` liegt garantiert vor 17:00 NY seines eigenen Tages, gilt also als "laeuft noch",
    # und hat sicher keine Tagesdatei in raw/marktdaten/.
    morgen = datetime.now(NY).date() + timedelta(days=1)
    puffer = LIVE_DIR / morgen.isoformat() / f"{DISPLAY_SYMBOL} {morgen.isoformat()} 1s-live.csv"
    orig_live_fenster = fetch_ibkr.live_fenster

    def _zeilen(sekunden_alt: int) -> list[dict]:
        ts = int((datetime.now(NY) - timedelta(seconds=sekunden_alt)).timestamp())
        return [{"time": ts, "open": 23000.0, "high": 23001.0, "low": 22999.0,
                 "close": 23000.5, "volume": 7}]

    try:
        # Gateway nicht erreichbar -> leere Liste + Meldung, niemals ein alter Stand.
        fetch_ibkr.live_fenster = lambda *a, **k: (_ for _ in ()).throw(
            ConnectionRefusedError("kein Gateway"))
        assert _download_1s(morgen) == [], "ohne Gateway darf kein Stand zurueckkommen"
        assert not puffer.exists(), "ein fehlgeschlagener Abruf darf keinen Puffer schreiben"

        # Frische Kerzen -> Bar-Liste + transienter Puffer unter algo/live/ (nicht raw/).
        fetch_ibkr.live_fenster = lambda *a, **k: _zeilen(1)
        frisch = _download_1s(morgen)
        assert len(frisch) == 1 and frisch[0].o == 23000.0, frisch
        assert puffer.exists(), "geholte Livekerzen muessen in den Puffer geschrieben werden"
        assert not markt_bars(DISPLAY_SYMBOL, "1s", von=morgen, bis=morgen), \
            "der laufende Tag darf keine Tagesdatei in raw/marktdaten/ hinterlassen"
        puffer.unlink()

        # Zu alte Kerzen -> kein Live-Stand (20-Minuten-Frischegrenze).
        fetch_ibkr.live_fenster = lambda *a, **k: _zeilen(3600)
        assert _download_1s(morgen) == [], "eine Stunde alte Kerzen sind kein Live-Stand"
    finally:
        fetch_ibkr.live_fenster = orig_live_fenster
        if puffer.exists():
            puffer.unlink()
        if puffer.parent.exists():
            puffer.parent.rmdir()
    print("selftest (Task 6: NQ ueber IBKR-1s) ok")


def _dry_run(day_str: str) -> dict:
    """Pipeline gegen einen fertigen Handelstag -- bewusst ohne Abruf (`holen=False`), ein
    Trockenlauf soll keinen 46-Fenster-Backfill ausloesen."""
    day = date.fromisoformat(day_str)
    daten = fetch_today(day, holen=False)
    bars = daten[BASE_TF]
    if not bars:
        return {"generated_at": datetime.now(NY).isoformat(), "day": day_str,
                "market_data": False,
                "error": f"keine 1s-Daten fuer {day_str} in raw/marktdaten/",
                "price": None, "active_macro_window": None,
                "active_silver_bullet_window": None, "setup": None, "new_events": [],
                "first_run": False, "untouched_levels": [], "org_ce": None, "ndog_today": None,
                "nwog_today": None, "ndog_open_history": [], "nwog_open_history": []}
    now = bars[-1].t
    det = run_detectors(bars, day, now, org_bars=daten["5m_weit"],
                        daily_bars=daten["1d"] or None)
    empty_state = {"fvgs": [], "sweeps": [], "structure_breaks": [], "setup": None}
    new_events, _ = diff_events(det, empty_state)
    # --dry-run vergleicht per Konstruktion immer gegen einen leeren State.
    return {"generated_at": now.isoformat(), "day": day_str, "market_data": True, "error": None,
            "price": det["price"], "active_macro_window": det["active_macro_window"],
            "active_silver_bullet_window": det["active_silver_bullet_window"],
            "setup": det["setup"], "new_events": new_events,
            "first_run": True, "untouched_levels": det["untouched_levels"], "org_ce": det["org_ce"],
            "ndog_today": det["ndog_today"], "nwog_today": det["nwog_today"],
            "ndog_open_history": det["ndog_open_history"], "nwog_open_history": det["nwog_open_history"]}


def _live_run() -> dict:
    now = datetime.now(NY)
    # Globex-Handelstag: ab 18:00 NY laeuft bereits die Session des Folgetages (wie
    # marktdaten.trading_day(), hier ohne pandas-Timestamp-Umweg).
    day = now.date() + timedelta(days=1) if now.hour >= 18 else now.date()
    daten = fetch_today(day)
    if not daten[BASE_TF]:
        return {"generated_at": now.isoformat(), "day": day.isoformat(), "market_data": False,
                "error": f"keine {BASE_TF}-Daten (Markt geschlossen oder IBKR-Gateway nicht "
                         f"erreichbar)",
                "price": None, "active_macro_window": None,
                "active_silver_bullet_window": None, "setup": None, "new_events": [],
                "first_run": False, "untouched_levels": [], "org_ce": None, "ndog_today": None,
                "nwog_today": None, "ndog_open_history": [], "nwog_open_history": []}

    # Nur die Intraday-Timeframes. `1d` wird -- anders als frueher -- nicht mehr nach
    # algo/live/ gespiegelt: es kommt jetzt unveraendert aus raw/marktdaten/ (bis 2026-08-16
    # war es ein frischer yfinance-Download, den es ohne Kopie nicht mehr gab). Eine Kopie
    # waere eine zweite, alternde Fassung derselben Datei.
    for tf in INTRADAY_TFS:
        if daten[tf]:
            write_live_day(tf, day, daten[tf])

    bars = daten[BASE_TF]
    det = run_detectors(bars, day, now, org_bars=daten["5m_weit"],
                        daily_bars=daten["1d"] or None)

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
            "ndog_today": det["ndog_today"], "nwog_today": det["nwog_today"],
            "ndog_open_history": det["ndog_open_history"], "nwog_open_history": det["nwog_open_history"]}


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
