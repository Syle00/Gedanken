# Algo Live-Status-Loop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ein `/loop 10m /algo-live-status`-Zyklus, der den laufenden MNQ-Handelstag per yfinance
aktuell haelt und einen Statusbericht liefert (Stand / Abgleich mit Algo-Signalen / Ausblick).

**Architecture:** `algo/live_status.py` zieht den heutigen Handelstag (alle Timeframes) nach
`algo/live/<datum>/` (transient, ueberschreibend), laesst dieselben Detektoren wie
`algo/backtest_ohlc.py` (`fvgs`, `sweeps`, `structure_breaks`, `macro_windows` aus
`tools/analyze_ohlc.py`) plus `plan_trade()` aus `algo/rules.py` auf den 5m-Daten laufen und
diffed das Ergebnis gegen den letzten gespeicherten Snapshot (`state.json`), um nur *neue*
Ereignisse seit dem letzten Zyklus auszugeben. `.claude/commands/algo-live-status.md` ruft das
Skript auf und laesst Claude daraus den Prosa-Report schreiben. `/loop` haelt den 10-Minuten-Takt,
session-gebunden, Start/Stop manuell.

**Tech Stack:** Python (stdlib + pandas/yfinance, bereits in `algo/requirements.txt`), keine
neuen Abhaengigkeiten. Kein pytest im Projekt — Tests folgen dem bestehenden Muster
(assert-basierte Selbstchecks, siehe `algo/rules.py::demo()`), hier als `--selftest`-CLI-Flag.

**Referenz-Spec:** `docs/superpowers/specs/2026-08-04-algo-live-status-loop-design.md`

## Global Constraints

- `raw/marktdaten/` bleibt vollstaendig unveraendert — kein Schreibzugriff aus diesem Feature.
- Basis-Timeframe fuer alle Detektoren ist **5m**, wie in `algo/backtest_ohlc.py` — dieselbe
  CFG-Skalierung (`min_age=max(3, round(15/5))=3`, `confirm=max(2, round(5/5))=2`) muss beim
  Import angewendet werden, sonst laufen Live-Report und Tagesreport/Backtest mit
  unterschiedlichen Schwellen (siehe `algo/PLAN.md`, bereits einmal als Bug passiert).
  `CFG["swing"]` und `CFG["min_pen"]` bleiben Default (2 bzw. 0.75).
  `CFG["min_pen"] * med_bar` wird als absoluter Wert an `sweeps()` uebergeben (Median-Kerzenrange
  der jeweils betrachteten `bars`-Liste), exakt wie in `algo/backtest_ohlc.py::analyze_day`.
- Keine Neuimplementierung bestehender Detektoren — nur importieren aus
  `tools/analyze_ohlc.py` und `algo/rules.py`.
- Keine pytest-Abhaengigkeit einfuehren. Tests sind `assert`-Bloecke in einer `selftest()`-
  Funktion, ausgeloest ueber `python algo/live_status.py --selftest`.
- Alle neuen Dateien/Kommentare/Ausgaben auf Deutsch, wie der Rest des Projekts.
- `algo/live/*/` (die taeglichen Datenordner) gehoeren nicht in Git — `raw/marktdaten/` ist die
  einzige versionierte Rohdatenquelle. Die Text-Statusberichte (`algo/live/<datum>-status-log.md`)
  bleiben dagegen versioniert.

---

### Task 1: Diff-Logik gegen den letzten Snapshot

**Files:**
- Create: `algo/live_status.py`

**Interfaces:**
- Produces: `event_key(d: dict, field: str) -> list`, `load_state(path: Path) -> dict`,
  `diff_events(current: dict, prev_state: dict) -> tuple[list[dict], dict]`,
  `selftest() -> None`, `main(argv=None) -> int` (Minimal-Stub, wird in Task 4 ausgebaut)
- Consumes: nichts (reine Stdlib: `json`, `pathlib`, `datetime` nur im Selftest)

`current`/`prev_state`/Rueckgabe von `diff_events` sind Dicts mit den Schluesseln `"fvgs"`,
`"sweeps"`, `"structure_breaks"` (je eine Liste von Detektor-Dicts mit mindestens `"t"` +
`"side"` bzw. `"dir"`) und `"setup"` (Dict oder `None`). Diese Form wird von `run_detectors()`
in Task 2 exakt so erzeugt.

- [ ] **Step 1: Datei mit fehlschlagendem Selftest anlegen**

```python
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
import sys
from pathlib import Path

LIVE_DIR = Path(__file__).resolve().parent / "live"


def event_key(d: dict, field: str) -> list:
    raise NotImplementedError


def load_state(path: Path) -> dict:
    raise NotImplementedError


def diff_events(current: dict, prev_state: dict) -> tuple[list[dict], dict]:
    raise NotImplementedError


def selftest() -> None:
    from datetime import datetime

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

    print("selftest (Task 1: diff_events) ok")


def main(argv=None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if "--selftest" in args:
        selftest()
        return 0
    print("noch nicht implementiert", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Fehlschlag verifizieren**

Run: `python algo/live_status.py --selftest`
Expected: `NotImplementedError` (aus `diff_events`, ueber `event_key`/`load_state` propagiert)

- [ ] **Step 3: Implementierung**

`event_key`, `load_state`, `diff_events` ersetzen die `raise NotImplementedError`-Stubs:

```python
def event_key(d: dict, field: str) -> list:
    """Identitaet eines Ereignisses ueber Laeufe hinweg: Kerzenzeit + Seite/Richtung."""
    t = d["t"]
    return [t.isoformat() if hasattr(t, "isoformat") else t, d[field]]


def load_state(path: Path) -> dict:
    if not path.exists():
        return {"fvgs": [], "sweeps": [], "structure_breaks": [], "setup": None}
    return json.loads(path.read_text(encoding="utf-8"))


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
    if cur_setup and cur_setup != prev_setup:
        new_events.append({"kind": "setup_entered", **cur_setup})
    elif prev_setup and not cur_setup:
        new_events.append({"kind": "setup_exited", **prev_setup})
    new_state["setup"] = cur_setup

    return new_events, new_state
```

- [ ] **Step 4: Erfolg verifizieren**

Run: `python algo/live_status.py --selftest`
Expected: `selftest (Task 1: diff_events) ok`

- [ ] **Step 5: Commit**

```bash
git add algo/live_status.py
git commit -m "feat: diff_events fuer Live-Status-Loop (Task 1)"
```

---

### Task 2: Detektor-Wrapper `run_detectors()`

**Files:**
- Modify: `algo/live_status.py`

**Interfaces:**
- Consumes: `analyze_ohlc.Bar`, `load`, `fvgs`, `sweeps`, `structure_breaks`, `macro_windows`,
  `TF_MINUTES`, `CFG` (aus `tools/analyze_ohlc.py`); `plan_trade`, `_active_window`
  (aus `algo/rules.py`)
- Produces: `run_detectors(bars: list[Bar], day: date, now: datetime) -> dict` mit Schluesseln
  `"price"` (`{"last": float, "t": str} | None`), `"active_macro_window"`
  (`{"name": str, "start": str, "end": str} | None`), `"active_silver_bullet_window"`
  (`str | None`), `"setup"` (`dict | None`, via `dataclasses.asdict`), `"fvgs"`, `"sweeps"`,
  `"structure_breaks"` (Listen, Form kompatibel zu Task 1s `diff_events`)

- [ ] **Step 1: Selftest um fehlschlagenden Aufruf erweitern**

Direkt nach den Imports am Dateianfang ergaenzen (nach `from pathlib import Path`):

```python
import statistics
from dataclasses import asdict
from datetime import date, datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from analyze_ohlc import (  # noqa: E402
    Bar, load, fvgs, sweeps, structure_breaks, macro_windows, TF_MINUTES, CFG,
)
from rules import plan_trade, _active_window  # noqa: E402

BASE_TF = "5m"
_tf_min = TF_MINUTES[BASE_TF]
CFG.update(min_age=max(3, round(15 / _tf_min)), confirm=max(2, round(5 / _tf_min)))


def run_detectors(bars: list[Bar], day: date, now: datetime) -> dict:
    raise NotImplementedError
```

In `selftest()`, vor `print("selftest (Task 1: diff_events) ok")` einfuegen:

```python
    # Task 2: run_detectors gegen echte, bereits abgeschlossene Daten (31.07.2026).
    day_path = (Path(__file__).resolve().parent.parent / "raw" / "marktdaten"
                / "2026" / "07" / "31.07.2026" / "MNQ 2026-07-31 5m.csv")
    real_bars = load(day_path)
    det = run_detectors(real_bars, date(2026, 7, 31), real_bars[-1].t)
    assert det["price"]["last"] == real_bars[-1].c
    assert isinstance(det["fvgs"], list) and isinstance(det["sweeps"], list)
    empty_det = run_detectors([], date(2026, 7, 31), real_bars[-1].t)
    assert empty_det["price"] is None and empty_det["fvgs"] == []
    print("selftest (Task 2: run_detectors) ok")
```

- [ ] **Step 2: Fehlschlag verifizieren**

Run: `python algo/live_status.py --selftest`
Expected: `NotImplementedError` aus `run_detectors`

- [ ] **Step 3: Implementierung**

```python
def run_detectors(bars: list[Bar], day: date, now: datetime) -> dict:
    """Reine Funktion: bestehende Detektoren auf `bars` (Basis-TF 5m, siehe BASE_TF) +
    plan_trade(). Feldnamen matchen die Kategorien aus diff_events() (Task 1)."""
    if not bars:
        return {"price": None, "active_macro_window": None,
                "active_silver_bullet_window": None, "setup": None,
                "fvgs": [], "sweeps": [], "structure_breaks": []}

    med_bar = statistics.median(b.rng for b in bars) or 1.0
    fg = fvgs(bars)
    sw = sweeps(bars, CFG["swing"], CFG["min_age"], CFG["min_pen"] * med_bar, CFG["confirm"])
    sb = structure_breaks(bars, CFG["swing"], CFG["min_age"])
    setup = plan_trade(bars, now)

    active_macro = None
    for name, start, end in macro_windows(day):
        if start <= now < end:
            active_macro = {"name": name, "start": start.isoformat(), "end": end.isoformat()}
            break
    win = _active_window(day, now)

    last = bars[-1]
    return {
        "price": {"last": last.c, "t": last.t.isoformat()},
        "active_macro_window": active_macro,
        "active_silver_bullet_window": win[0] if win else None,
        "setup": asdict(setup) if setup else None,
        "fvgs": fg, "sweeps": sw, "structure_breaks": sb,
    }
```

- [ ] **Step 4: Erfolg verifizieren**

Run: `python algo/live_status.py --selftest`
Expected: `selftest (Task 1: diff_events) ok` gefolgt von `selftest (Task 2: run_detectors) ok`

- [ ] **Step 5: Commit**

```bash
git add algo/live_status.py
git commit -m "feat: run_detectors fuer Live-Status-Loop (Task 2)"
```

---

### Task 3: Live-Fetch + Schreiben nach `algo/live/`

**Files:**
- Modify: `algo/live_status.py`

**Interfaces:**
- Consumes: `trading_day`, `flatten`, `SYMBOL` (aus `algo/fetch_yfinance.py`)
- Produces: `_download(tf: str, start: str, end: str) -> pd.DataFrame`,
  `fetch_today(target_day: date) -> dict[str, pd.DataFrame]` (Schluessel: `INTERVALS` +
  `"4h"`), `write_live_day(tf: str, day: date, rows: pd.DataFrame) -> Path`

- [ ] **Step 1: Selftest um fehlschlagenden Aufruf erweitern**

Nach dem Task-2-Importblock ergaenzen:

```python
from datetime import timedelta

import pandas as pd
import yfinance as yf

from fetch_yfinance import trading_day, flatten, SYMBOL  # noqa: E402

DISPLAY_SYMBOL = "MNQ"
INTERVALS = ["1m", "5m", "15m", "1h", "1d"]


def _download(tf: str, start: str, end: str) -> pd.DataFrame:
    raise NotImplementedError


def fetch_today(target_day: date) -> dict[str, pd.DataFrame]:
    raise NotImplementedError


def write_live_day(tf: str, day: date, rows: pd.DataFrame) -> Path:
    raise NotImplementedError
```

In `selftest()`, vor der `print("selftest (Task 2: ...")`-Zeile (also zwischen Task-1- und
Task-2-Block, Reihenfolge ist egal, hier ans Ende) ergaenzen — direkt vor
`print("selftest (Task 2: run_detectors) ok")` einfuegen, damit die Ausgabereihenfolge den
Tasks folgt:

```python
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
```

- [ ] **Step 2: Fehlschlag verifizieren**

Run: `python algo/live_status.py --selftest`
Expected: `selftest (Task 1: diff_events) ok`, dann `NotImplementedError` aus `write_live_day`

- [ ] **Step 3: Implementierung**

```python
def _download(tf: str, start: str, end: str) -> pd.DataFrame:
    try:
        return flatten(yf.download(SYMBOL, start=start, end=end, interval=tf, progress=False))
    except Exception as exc:  # Netzwerk-/yfinance-Fehler sollen den Loop nicht abbrechen
        print(f"  ! {tf}: Download fehlgeschlagen ({exc})", file=sys.stderr)
        return pd.DataFrame()


def fetch_today(target_day: date) -> dict[str, pd.DataFrame]:
    """Alle INTERVALS + 4h (aus 1h resampled), gefiltert auf target_day ueber trading_day()
    (aus fetch_yfinance.py) -- die Globex-Session startet 18:00 NY am Vortag, ohne die
    Filterung landen Vorabend-Kerzen sonst unter dem falschen Kalendertag."""
    start = (target_day - timedelta(days=3)).isoformat()
    end = (target_day + timedelta(days=1)).isoformat()
    dfs: dict[str, pd.DataFrame] = {}
    for tf in INTERVALS:
        raw = _download(tf, start, end)
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
```

- [ ] **Step 4: Erfolg verifizieren**

Run: `python algo/live_status.py --selftest`
Expected: alle drei Zeilen (`Task 1`, `Task 3`, `Task 2` -- in dieser Reihenfolge, siehe Step 1)
mit `ok`. `fetch_today()` bleibt an dieser Stelle ungetestet (Netzwerkabhaengigkeit) — wird in
Task 4 ueber den Live-Pfad manuell verifiziert.

- [ ] **Step 5: Commit**

```bash
git add algo/live_status.py
git commit -m "feat: yfinance-Fetch + Schreiben nach algo/live/ (Task 3)"
```

---

### Task 4: CLI — `--dry-run` / `--selftest` / Live-Modus

**Files:**
- Modify: `algo/live_status.py`

**Interfaces:**
- Consumes: alles aus Task 1–3
- Produces: finales `main(argv=None) -> int`, druckt eine JSON-Zeile mit Schluesseln
  `generated_at`, `day`, `market_data`, `error`, `price`, `active_macro_window`,
  `active_silver_bullet_window`, `setup`, `new_events` auf stdout — das ist der Vertrag, den
  `.claude/commands/algo-live-status.md` (Task 5) konsumiert.

- [ ] **Step 1: Bestehenden Minimal-`main()` durch fehlschlagenden Aufruf ersetzen**

`from zoneinfo import ZoneInfo` zu den Imports ganz oben hinzufuegen, `NY = ZoneInfo("America/New_York")`
direkt unter `LIVE_DIR = ...` ergaenzen. Alles ab der Zeile `def main(argv=None) -> int:` bis
zum Dateiende (das ist der komplette `main()`-Stub aus Task 1 samt seinem
`if __name__ == "__main__": sys.exit(main())`-Block) loeschen und durch Folgendes ersetzen:

```python
def _dry_run(day_str: str) -> dict:
    raise NotImplementedError


def _live_run() -> dict:
    raise NotImplementedError


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
```

- [ ] **Step 2: Fehlschlag verifizieren**

Run: `python algo/live_status.py --dry-run 2026-07-31`
Expected: `NotImplementedError` aus `_dry_run`

- [ ] **Step 3: Implementierung**

```python
def _dry_run(day_str: str) -> dict:
    day = date.fromisoformat(day_str)
    path = (Path(__file__).resolve().parent.parent / "raw" / "marktdaten"
            / f"{day:%Y}" / f"{day:%m}" / f"{day:%d.%m.%Y}"
            / f"{DISPLAY_SYMBOL} {day.isoformat()} {BASE_TF}.csv")
    if not path.exists():
        return {"generated_at": datetime.now(NY).isoformat(), "day": day_str,
                "market_data": False, "error": f"keine {BASE_TF}-Datei fuer {day_str} gefunden",
                "price": None, "active_macro_window": None,
                "active_silver_bullet_window": None, "setup": None, "new_events": []}
    bars = load(path)
    now = bars[-1].t
    det = run_detectors(bars, day, now)
    empty_state = {"fvgs": [], "sweeps": [], "structure_breaks": [], "setup": None}
    new_events, _ = diff_events(det, empty_state)
    return {"generated_at": now.isoformat(), "day": day_str, "market_data": True, "error": None,
            "price": det["price"], "active_macro_window": det["active_macro_window"],
            "active_silver_bullet_window": det["active_silver_bullet_window"],
            "setup": det["setup"], "new_events": new_events}


def _live_run() -> dict:
    now = datetime.now(NY)
    day = trading_day(pd.Timestamp(now))
    dfs = fetch_today(day)
    if dfs["5m"].empty:
        return {"generated_at": now.isoformat(), "day": day.isoformat(), "market_data": False,
                "error": "keine 5m-Daten (Markt geschlossen oder yfinance-Fehler)",
                "price": None, "active_macro_window": None,
                "active_silver_bullet_window": None, "setup": None, "new_events": []}

    for tf, df in dfs.items():
        if not df.empty:
            write_live_day(tf, day, df)

    bars = load(LIVE_DIR / day.isoformat() / f"{DISPLAY_SYMBOL} {day.isoformat()} 5m.csv")
    det = run_detectors(bars, day, now)

    state_path = LIVE_DIR / day.isoformat() / "state.json"
    prev_state = load_state(state_path)
    new_events, new_state = diff_events(det, prev_state)
    state_path.write_text(json.dumps(new_state, default=str, ensure_ascii=False, indent=2),
                          encoding="utf-8")

    return {"generated_at": now.isoformat(), "day": day.isoformat(), "market_data": True,
            "error": None, "price": det["price"], "active_macro_window": det["active_macro_window"],
            "active_silver_bullet_window": det["active_silver_bullet_window"],
            "setup": det["setup"], "new_events": new_events}
```

- [ ] **Step 4: Erfolg verifizieren**

Run: `python algo/live_status.py --selftest`
Expected: alle drei `selftest (...) ok`-Zeilen weiterhin

Run:
```bash
python algo/live_status.py --dry-run 2026-07-31 | python -c "
import json, sys
d = json.load(sys.stdin)
assert d['market_data'] is True
assert d['day'] == '2026-07-31'
assert 'new_events' in d and isinstance(d['new_events'], list)
print('dry-run JSON ok,', len(d['new_events']), 'Ereignisse')
"
```
Expected: `dry-run JSON ok, N Ereignisse` (kein Traceback)

**Manuelle Verifikation (Netzwerk, nicht automatisierbar):** `python algo/live_status.py`
einmal ohne Flags ausfuehren. Waehrend der Markt offen ist: `algo/live/<heutiges Datum>/`
entsteht mit CSVs + `state.json`, JSON-Ausgabe zeigt `"market_data": true`. Ausserhalb der
Handelszeiten (Wochenende/Feiertag) ist `"market_data": false` mit Fehlermeldung das korrekte,
erwartete Ergebnis — kein Bug.

- [ ] **Step 5: Commit**

```bash
git add algo/live_status.py
git commit -m "feat: CLI (--dry-run/--selftest/live) fuer Live-Status-Loop (Task 4)"
```

---

### Task 5: Slash-Command `.claude/commands/algo-live-status.md`

**Files:**
- Create: `.claude/commands/algo-live-status.md`

**Interfaces:**
- Consumes: die JSON-Ausgabe von `python algo/live_status.py` (Vertrag aus Task 4)
- Produces: Textbericht, angehaengt an `algo/live/<day>-status-log.md`

- [ ] **Step 1: Datei anlegen**

```markdown
---
description: Ein Live-Status-Zyklus fuer MNQ -- frische Daten ziehen, mit den Algo-Signalen abgleichen, Bericht schreiben (fuer /loop 10m /algo-live-status)
---

Fuehre einen einzelnen Live-Status-Zyklus fuer MNQ aus.

1. `python algo/live_status.py` ausfuehren und die JSON-Ausgabe lesen.
2. Falls `market_data: false`: kurz vermerken, dass der Markt vermutlich geschlossen ist
   (oder der Datenabruf fehlgeschlagen ist) und den Zyklus damit beenden -- keinen
   Bericht erfinden.
3. Die letzten Zeilen von `algo/live/<day>-status-log.md` lesen (falls vorhanden;
   `<day>` ist das `day`-Feld aus der JSON-Ausgabe), um an die letzte Einschaetzung
   anzuknuepfen.
4. Einen kurzen deutschen Statusbericht schreiben mit drei Teilen:
   - **Stand**: aktueller Preis, aktives Makro-/Silver-Bullet-Fenster (falls eins aktiv ist).
   - **Abgleich**: die Eintraege in `new_events` gegen das, was die Algo-Signale fuer
     diese Fenster/Uhrzeit erwarten lassen wuerden -- deckt sich das oder nicht?
     Bei leerem `new_events`: kurz sagen, dass sich seit dem letzten Lauf nichts
     Neues ergeben hat.
   - **Ausblick**: eigene Einschaetzung, was als naechstes plausibel ist (z.B. naechstes
     Zeitfenster, offenes `setup`-Target, unberuehrte Liquiditaet in der Naehe).
5. Den Bericht mit Zeitstempel an `algo/live/<day>-status-log.md` anhaengen (Datei
   anlegen, falls sie noch nicht existiert) und ihn auch im Chat ausgeben.
```

- [ ] **Step 2: Manuelle Verifikation**

In einer echten Claude-Code-Session (waehrend der Markt offen ist) `/algo-live-status` einmal
aufrufen. Erwartet: das Skript laeuft durch, `algo/live/<heutiges Datum>-status-log.md` enthaelt
einen neuen Eintrag mit den drei Teilen (Stand/Abgleich/Ausblick), der Bericht erscheint auch
im Chat. Kein automatisierter Test moeglich — dies ist ein LLM-Prompt, kein Code.

- [ ] **Step 3: Commit**

```bash
git add .claude/commands/algo-live-status.md
git commit -m "feat: Slash-Command /algo-live-status (Task 5)"
```

---

### Task 6: `.gitignore` + `algo/PLAN.md` dokumentieren

**Files:**
- Modify: `.gitignore`
- Modify: `algo/PLAN.md`

**Interfaces:** keine (reine Dokumentation/Konfiguration)

- [ ] **Step 1: `.gitignore` ergaenzen**

Neue Sektion am Ende von `.gitignore` anhaengen:

```
# --- Algo Live-Loop ---
# algo/live_status.py schreibt bei jedem 10-Minuten-Zyklus CSVs + state.json neu --
# reiner Ableitungs-Output, keine Historie wert (anders als raw/marktdaten/).
# Die Text-Statusberichte (algo/live/<datum>-status-log.md) bleiben bewusst versioniert.
algo/live/*/
```

- [ ] **Step 2: `algo/PLAN.md` — neuer Backlog-Punkt**

Nach Backlog-Punkt 5 (Detektor-Schwellen) einen neuen Punkt 6 einfuegen:

```markdown
6. **Live-Status-Loop — umgesetzt:** `algo/live_status.py` + `.claude/commands/algo-live-status.md`
   + `/loop 10m /algo-live-status` (Design: `docs/superpowers/specs/2026-08-04-algo-live-status-loop-design.md`,
   Plan: `docs/superpowers/plans/2026-08-04-algo-live-status-loop.md`). Zieht den laufenden
   Handelstag alle 10 Minuten per yfinance nach `algo/live/<datum>/` (transient, ueberschreibend,
   `raw/marktdaten/` bleibt unangetastet), laesst dieselben Detektoren wie `backtest_ohlc.py`
   auf den 5m-Daten laufen plus `plan_trade()`, und meldet nur *neue* Ereignisse seit dem
   letzten Zyklus. Session-gebunden (`/loop`), kein Cloud-Schedule (Mindest-Takt dort 1h,
   keine lokale Dateizugriff) — Start/Stop manuell per Zuruf.
```

- [ ] **Step 3: `algo/PLAN.md` — Log-Zeile anhaengen**

Neue Zeile ans Ende der Log-Tabelle (nach der letzten bestehenden Zeile):

```markdown
| 2026-08-04 | Live-Status-Loop gebaut: `algo/live_status.py` (Fetch heutiger Handelstag per yfinance nach `algo/live/<datum>/`, Detektoren wie `backtest_ohlc.py` auf 5m + `plan_trade()`, Diff gegen `state.json` fuer neue Ereignisse seit letztem Zyklus) + `.claude/commands/algo-live-status.md` + `/loop 10m /algo-live-status`. Session-gebunden statt Cloud-Schedule (Mindest-Takt dort 1h, kein lokaler Dateizugriff). `algo/live/*/` neu in `.gitignore` (transient, ueberschreibend); die Text-Statusberichte `algo/live/<datum>-status-log.md` bleiben versioniert. |
```

- [ ] **Step 4: Verifikation**

Run: `grep -n "algo/live" .gitignore && grep -n "Live-Status-Loop" algo/PLAN.md`
Expected: Treffer in beiden Dateien, keine Fehlermeldung

- [ ] **Step 5: Commit**

```bash
git add .gitignore algo/PLAN.md
git commit -m "docs: Live-Status-Loop in PLAN.md + gitignore dokumentieren (Task 6)"
```

---

## Nach der Implementierung

Der Loop ist danach jederzeit nutzbar mit: `/loop 10m /algo-live-status` (starten),
normaler Zuruf zum Stoppen. Keine weitere Einrichtung noetig — `algo/requirements.txt`
(`pandas`, `yfinance`) deckt alle Abhaengigkeiten bereits ab.
