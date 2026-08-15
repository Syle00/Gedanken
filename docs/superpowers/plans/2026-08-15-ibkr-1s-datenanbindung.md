# IBKR 1s-Datenanbindung (NQ/ES) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Sekundengenaue OHLC-Daten für NQ und ES autonom über die IBKR-TWS/Gateway-API
beschaffen, im bestehenden `raw/marktdaten/`-Baum als Tages-Parquet ablegen und über
`algo/marktdaten.py::bars()` für Backtests verfügbar machen — inklusive Pacing-Limiter,
Abdeckungs-Register, Nulltoleranz-Gate-Anpassung für 1s-Auflösung und Doku-Nachzug.

**Architecture:** Neues, eigenständiges Modul `algo/fetch_ibkr.py` im Stil von
`algo/fetch_yfinance.py` (Reuse: `trading_day()` wird von dort importiert, nicht
dupliziert). Alle netzunabhängigen Bausteine (Front-Monat-Auflösung, Fenster-Zerlegung,
Pacing-Limiter, Register, Parquet-I/O) sind pure Funktionen/Klassen mit injizierbaren
Abhängigkeiten (Uhr, IB-Client) und werden vollständig ohne Netzzugriff getestet. Die
eigentliche IBKR-Verbindung (`ib_async.IB().connect(...)`) läuft nur im CLI-Pfad und wird
**nicht** in der Agenten-Sandbox getestet — das ist laut Spec §12.2 explizit ein manueller
Schritt auf dem Windows-Rechner des Nutzers (Task 9 dieses Plans).

**Tech Stack:** Python (Standardbibliothek + `pandas`, `pyarrow` für Parquet), `ib_async`
(neu), bestehende Module `tools/analyze_ohlc.py`, `algo/fetch_yfinance.py`,
`algo/marktdaten.py`, `algo/selfcheck.py`.

**Spec:** `docs/superpowers/specs/2026-08-15-ibkr-1s-datenanbindung-design.md`

## Global Constraints

- Kein Lookahead, keine Netzabhängigkeit in Selbstchecks (`algo/selfcheck.py` muss
  netzfrei laufen) — siehe CLAUDE.md „Algo-Trading: Arbeitsstandards".
- `readonly=True`, Verbindung nur über Port 4002 (Paper) — siehe Spec §9. Kein Code in
  diesem Plan darf `place_order` o.ä. aufrufen oder Port 4001 fest verdrahten.
- Punktwerte NQ=$20, ES=$50 sind in `algo/pnl.py::POINT_VALUE` **bereits vorhanden** —
  keine Änderung an `pnl.py` nötig (verifiziert, siehe Recherche zu diesem Plan).
- Tages-Parquet-Dateien werden nie überschrieben (`dest.exists()`-Guard, wie
  `fetch_yfinance.py::write_day()`).
- `tools/analyze_ohlc.py` bleibt Standardbibliothek-only (kein `pandas`-Import dort).

---

## Task 1: `algo/fetch_ibkr.py` — Front-Monat-Auflösung + Pacing-Limiter

**Files:**
- Create: `algo/fetch_ibkr.py`
- Modify: `algo/requirements.txt` (Zeile `ib_async>=1.0` ergänzen, alphabetisch/thematisch
  bei den übrigen Fetch-Abhängigkeiten wie `yfinance`)

**Interfaces:**
- Produces: `front_month(d: date, symbol: str) -> str`, `PacingLimiter` Klasse mit
  `.wait() -> None`, Konstruktor `PacingLimiter(clock=time.monotonic, sleep=time.sleep,
  max_requests: int = 60, window: float = 600.0, min_gap: float = 0.5)`

- [ ] **Step 1: Modul-Grundgerüst + Requirements anlegen**

`algo/requirements.txt` — Zeile ergänzen (nach der `yfinance`-Zeile):

```
ib_async>=1.0         # IBKR TWS/Gateway-API-Client, Nachfolger von ib_insync (algo/fetch_ibkr.py)
```

`algo/fetch_ibkr.py` neu anlegen:

```python
#!/usr/bin/env python3
"""Laedt sekundengenaue OHLC-Daten fuer NQ und ES ueber die IBKR-TWS/Gateway-API und legt sie
im bestehenden raw/marktdaten/-Baum als Tages-Parquet ab (Schema wie das TradingView-CSV,
plus volume/contract). Siehe docs/superpowers/specs/2026-08-15-ibkr-1s-datenanbindung-design.md.

Drei Betriebsarten:
    python algo/fetch_ibkr.py --verify [--symbol NQ]      # ein 30-Min-Fenster, schreibt nichts
    python algo/fetch_ibkr.py --backfill 2026-02-17 2026-08-14
    python algo/fetch_ibkr.py                             # Nachlad: letzter Registereintrag bis gestern

Verbindet sich ausschliesslich readonly gegen Port 4002 (Paper-Gateway) -- dieser Datenpfad
hat konstruktionsbedingt keinen Weg zu echtem Kapital (Spec Design SS9).
"""
from __future__ import annotations

import argparse
import csv
import sys
import time
from collections import deque
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from analyze_ohlc import pruefe_kerzen, OHLCDefekt  # noqa: E402
from fetch_yfinance import trading_day  # noqa: E402

NY = ZoneInfo("America/New_York")
UTC = ZoneInfo("UTC")
DATA_DIR = Path(__file__).resolve().parent.parent / "raw" / "marktdaten"
REGISTER = DATA_DIR / "1s-abdeckung.csv"
REGISTER_HEADER = ["symbol", "von", "bis", "kontrakt", "kerzen", "geholt_am"]
SYMBOLS = ["NQ", "ES"]
WINDOW_SECONDS = 1800

# Verfallsmonate NQ/ES: H (Maerz), M (Juni), U (September), Z (Dezember).
QUARTER_MONTHS = [(3, "H"), (6, "M"), (9, "U"), (12, "Z")]


def _third_friday(year: int, month: int) -> date:
    d = date(year, month, 1)
    first_friday = d + timedelta(days=(4 - d.weekday()) % 7)
    return first_friday + timedelta(weeks=2)


def front_month(d: date, symbol: str) -> str:
    """Front-Monat-Kontrakt (z.B. 'NQU2026') fuer Datum `d`: der erste Quartalskontrakt,
    dessen Roll-Termin (Verfall - 8 Tage) nach `d` liegt. Deterministisch, netzfrei."""
    for year in (d.year, d.year + 1):
        for month, code in QUARTER_MONTHS:
            verfall = _third_friday(year, month)
            roll = verfall - timedelta(days=8)
            if roll > d:
                return f"{symbol}{code}{year}"
    raise ValueError(f"kein Front-Monat fuer {d} gefunden")


class PacingLimiter:
    """IBKR-Pacing: max. `max_requests` je `window` Sekunden, mindestens `min_gap`
    Sekunden zwischen zwei Requests (deckt die 6-je-2s-Regel mit Reserve ab).
    `clock`/`sleep` sind injizierbar, damit Tests ohne echtes Warten laufen."""

    def __init__(self, clock=time.monotonic, sleep=time.sleep,
                 max_requests: int = 60, window: float = 600.0, min_gap: float = 0.5):
        self._clock = clock
        self._sleep = sleep
        self._max = max_requests
        self._window = window
        self._min_gap = min_gap
        self._times: deque[float] = deque(maxlen=max_requests)

    def wait(self) -> None:
        now = self._clock()
        if self._times and now - self._times[-1] < self._min_gap:
            self._sleep(self._min_gap - (now - self._times[-1]))
        if len(self._times) == self._max:
            wait_for = self._window - (self._clock() - self._times[0])
            if wait_for > 0:
                self._sleep(wait_for)
        self._times.append(self._clock())


def _demo() -> None:
    # Front-Monat: Tag vor und nach einem bekannten Roll (Verfall - 8 Tage) muss
    # unterschiedliche Kontrakte liefern, und der Roll-Termin selbst zaehlt schon zum
    # naechsten Kontrakt (roll > d ist strikt).
    verfall_maerz_2026 = _third_friday(2026, 3)
    roll = verfall_maerz_2026 - timedelta(days=8)
    assert front_month(roll - timedelta(days=1), "NQ") == "NQH2026", \
        "Tag vor dem Roll muss noch der alte Front-Monat sein"
    assert front_month(roll, "NQ") == "NQM2026", \
        "der Roll-Tag selbst zaehlt schon zum naechsten Quartalskontrakt"
    assert front_month(roll + timedelta(days=1), "ES") == "ESM2026"
    # Jahreswechsel: kurz vor dem Dezember-Roll noch Z, danach H des Folgejahres.
    verfall_dez_2026 = _third_friday(2026, 12)
    roll_dez = verfall_dez_2026 - timedelta(days=8)
    assert front_month(roll_dez - timedelta(days=1), "NQ") == "NQZ2026"
    assert front_month(roll_dez, "NQ") == "NQH2027"

    # Pacing-Limiter: 61 Requests duerfen mit einer simulierten Uhr nicht in unter 600s
    # durchgehen -- der 61. Request muss auf das Verlassen des 60er-Fensters warten.
    clock_state = {"t": 0.0}

    def fake_clock():
        return clock_state["t"]

    def fake_sleep(seconds):
        clock_state["t"] += seconds

    limiter = PacingLimiter(clock=fake_clock, sleep=fake_sleep)
    start = clock_state["t"]
    for _ in range(61):
        limiter.wait()
    assert clock_state["t"] - start >= 600.0, \
        f"61 Requests dauerten nur {clock_state['t'] - start}s, muessen >= 600s sein"
    print("fetch_ibkr front_month/PacingLimiter demo ok")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        _demo()
    else:
        print(__doc__)
```

- [ ] **Step 2: Demo ausführen**

Run: `python algo/fetch_ibkr.py`
Expected: `fetch_ibkr front_month/PacingLimiter demo ok`

- [ ] **Step 3: Commit**

```bash
git add algo/fetch_ibkr.py algo/requirements.txt
git commit -m "feat(algo): fetch_ibkr Front-Monat-Aufloesung + Pacing-Limiter"
```

---

## Task 2: `algo/fetch_ibkr.py` — Fenster-Zerlegung + Abdeckungs-Register

**Files:**
- Modify: `algo/fetch_ibkr.py`

**Interfaces:**
- Consumes: `NY`, `UTC`, `DATA_DIR`, `REGISTER`, `REGISTER_HEADER`, `WINDOW_SECONDS` aus Task 1
- Produces: `day_windows(day: date) -> list[tuple[datetime, datetime]]` (UTC-Paare),
  `register_load(path: Path = REGISTER) -> set[tuple[str, int, int]]`,
  `register_append(rows: list[dict], path: Path = REGISTER) -> None`

- [ ] **Step 1: `day_windows()` + Register-Funktionen ergänzen**

In `algo/fetch_ibkr.py`, nach `class PacingLimiter` (vor `def _demo()`) einfügen:

```python
def day_windows(day: date) -> list[tuple[datetime, datetime]]:
    """46 Fenster a 30 Minuten: 18:00 NY des Vortages bis 17:00 NY `day`, als UTC-Paare.
    Arithmetik laeuft auf tz-awaren NY-Zeitstempeln -- ein Fenster ueber einen DST-Wechsel
    bleibt dadurch korrekt (kein manueller Offset noetig, siehe marktdaten.py-Kommentar
    zum WANDUHR_TF-Fehlertyp, den wir hier bewusst vermeiden)."""
    start = datetime.combine(day - timedelta(days=1), datetime.min.time(), tzinfo=NY).replace(hour=18)
    end = datetime.combine(day, datetime.min.time(), tzinfo=NY).replace(hour=17)
    out = []
    cur = start
    while cur < end:
        nxt = cur + timedelta(seconds=WINDOW_SECONDS)
        out.append((cur.astimezone(UTC), nxt.astimezone(UTC)))
        cur = nxt
    return out


def register_load(path: Path = REGISTER) -> set[tuple[str, int, int]]:
    """(symbol, von, bis) aller bereits erfolgreich geholten Fenster, als UNIX-Sekunden."""
    if not path.exists():
        return set()
    with path.open(newline="", encoding="utf-8") as fh:
        return {(r["symbol"], int(r["von"]), int(r["bis"])) for r in csv.DictReader(fh)}


def register_append(rows: list[dict], path: Path = REGISTER) -> None:
    """Haengt Zeilen an -- schreibt den Header nur, wenn die Datei neu angelegt wird."""
    neu = not path.exists()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=REGISTER_HEADER)
        if neu:
            w.writeheader()
        w.writerows(rows)
```

- [ ] **Step 2: `_demo()` um Fenster- und Register-Checks erweitern**

In `_demo()`, vor `print("fetch_ibkr ... demo ok")` einfügen:

```python
    # Fenster-Zerlegung: genau 46 Fenster, erstes beginnt 18:00 NY des Vortages,
    # letztes endet 17:00 NY -- inklusive eines Tages ueber einen DST-Wechsel.
    normal_tag = date(2026, 6, 15)
    windows = day_windows(normal_tag)
    assert len(windows) == 46, len(windows)
    assert windows[0][0] == datetime(2026, 6, 14, 18, 0, tzinfo=NY).astimezone(UTC)
    assert windows[-1][1] == datetime(2026, 6, 15, 17, 0, tzinfo=NY).astimezone(UTC)

    dst_tag = date(2026, 11, 2)  # "fall back" 2026 faellt auf den 1. November
    dst_windows = day_windows(dst_tag)
    assert len(dst_windows) == 46, \
        f"DST-Tag muss trotzdem 46 Fenster liefern, waren {len(dst_windows)}"

    # Register-Resume: nach simuliertem Abbruch werden nur die fehlenden Fenster erkannt.
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        reg_path = Path(tmp) / "1s-abdeckung.csv"
        alle_fenster = {(int(a.timestamp()), int(b.timestamp())) for a, b in windows[:10]}
        geholt = set(list(alle_fenster)[:6])
        register_append(
            [{"symbol": "NQ", "von": v, "bis": b, "kontrakt": "NQU2026",
              "kerzen": 1800, "geholt_am": 1786838400} for v, b in geholt],
            path=reg_path)
        vorhanden = register_load(reg_path)
        assert vorhanden == {("NQ", v, b) for v, b in geholt}
        fehlend = alle_fenster - {(v, b) for _, v, b in vorhanden}
        assert len(fehlend) == 4, "nur die 4 nicht geholten Fenster duerfen fehlend sein"
```

- [ ] **Step 3: Demo ausführen**

Run: `python algo/fetch_ibkr.py`
Expected: `fetch_ibkr front_month/PacingLimiter demo ok` (weiterhin, keine neue Ausgabezeile
nötig — die neuen Asserts laufen im selben `_demo()`)

- [ ] **Step 4: Commit**

```bash
git add algo/fetch_ibkr.py
git commit -m "feat(algo): fetch_ibkr Fenster-Zerlegung + Abdeckungs-Register"
```

---

## Task 3: `algo/fetch_ibkr.py` — Parquet-Schreiben + Fetch-Orchestrierung (CLI)

**Files:**
- Modify: `algo/fetch_ibkr.py`

**Interfaces:**
- Consumes: `pruefe_kerzen`, `OHLCDefekt` (aus `analyze_ohlc`), `trading_day` (aus
  `fetch_yfinance`), `front_month`, `day_windows`, `PacingLimiter`, `register_load`,
  `register_append` aus Task 1/2
- Produces: `write_day_1s(symbol: str, day: date, rows: pd.DataFrame, contract: str) ->
  Path | None`, `fetch_window(ib, contract: str, end_utc: datetime, pacing: PacingLimiter)
  -> pd.DataFrame`, `fetch_symbol_day(ib, symbol: str, day: date, pacing: PacingLimiter,
  register_path: Path = REGISTER) -> Path | None`, `main(argv=None) -> int`

Die eigentliche IBKR-Verbindung (`ib_async.IB`) wird über den Parameter `ib` injiziert.
`fetch_window`/`fetch_symbol_day` rufen nur `ib.reqHistoricalData(...)` auf — in Tests wird
ein einfacher Stub übergeben, der kanonische Testdaten zurückgibt, ganz ohne Netzzugriff.

- [ ] **Step 1: `write_day_1s()`, `fetch_window()`, `fetch_symbol_day()`, `main()` ergänzen**

In `algo/fetch_ibkr.py`, nach `register_append()` (vor `def _demo()`) einfügen:

```python
def write_day_1s(symbol: str, day: date, rows: pd.DataFrame, contract: str) -> Path | None:
    """Schreibt eine Tagesdatei als Parquet, niemals ueberschreibend (wie
    fetch_yfinance.write_day()). Fuehrt vorher das Nulltoleranz-Gate aus -- wirft es
    OHLCDefekt, entsteht keine Datei (Aufrufer faengt das ab, siehe fetch_symbol_day)."""
    dest = (DATA_DIR / f"{day:%Y}" / f"{day:%m}" / f"{day:%d.%m.%Y}"
            / f"{symbol} {day.isoformat()} 1s.parquet")
    if dest.exists():
        return None
    for hinweis in pruefe_kerzen(
            rows[["time", "open", "high", "low", "close"]].itertuples(index=False, name=None),
            symbol, str(dest.name)):
        print(f"  ? {hinweis}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    out = rows.copy()
    out["contract"] = contract
    out.to_parquet(dest, index=False)
    return dest


def fetch_window(ib, contract: str, end_utc: datetime, pacing: PacingLimiter) -> pd.DataFrame:
    """Ein 30-Minuten-Fenster ueber `ib.reqHistoricalData`. `ib` ist injizierbar (echter
    ib_async.IB im CLI-Pfad, Stub in Tests). formatDate=2 liefert UNIX-Sekunden UTC direkt --
    keine Zeitzonen-Umrechnung noetig (schaedlichster Fehlertyp dieses Projekts, siehe
    CLAUDE.md 'Zeit vor Preis')."""
    pacing.wait()
    bars = ib.reqHistoricalData(
        contract, endDateTime=end_utc, durationStr=f"{WINDOW_SECONDS} S",
        barSizeSetting="1 secs", whatToShow="TRADES", useRTH=False, formatDate=2)
    rows = [{"time": int(b.date.timestamp()) if hasattr(b.date, "timestamp") else int(b.date),
             "open": b.open, "high": b.high, "low": b.low, "close": b.close,
             "volume": b.volume} for b in bars]
    df = pd.DataFrame(rows, columns=["time", "open", "high", "low", "close", "volume"])
    return df.sort_values("time").drop_duplicates("time", keep="first").reset_index(drop=True)


def fetch_symbol_day(ib, symbol: str, day: date, pacing: PacingLimiter,
                      register_path: Path = REGISTER) -> Path | None:
    """Ein Handelstag, ein Symbol: bereits abgedeckte Fenster ueberspringen, Rest holen,
    zusammensetzen, Gate, schreiben, Register anhaengen. Gibt den geschriebenen Pfad zurueck
    (None, wenn die Datei schon existierte oder gar kein Fenster geholt werden konnte)."""
    contract = front_month(day, symbol)
    vorhanden = {(v, b) for s, v, b in register_load(register_path) if s == symbol}
    frames, neue_register_zeilen = [], []
    for start_utc, end_utc in day_windows(day):
        key = (int(start_utc.timestamp()), int(end_utc.timestamp()))
        if key in vorhanden:
            continue
        df = fetch_window(ib, contract, end_utc, pacing)
        if df.empty:
            continue
        frames.append(df)
        neue_register_zeilen.append({
            "symbol": symbol, "von": key[0], "bis": key[1], "kontrakt": contract,
            "kerzen": len(df), "geholt_am": int(time.time())})
    if not frames:
        return None
    rows = pd.concat(frames).sort_values("time").drop_duplicates("time", keep="first")
    try:
        dest = write_day_1s(symbol, day, rows, contract)
    except OHLCDefekt as exc:
        print(f"  ! {symbol} {day}: {exc} -- keine Datei, keine Registerzeilen")
        return None
    if dest is not None:
        register_append(neue_register_zeilen, register_path)
    return dest


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--backfill", nargs=2, metavar=("VON", "BIS"))
    ap.add_argument("--symbol", help="Komma-Liste, z.B. NQ oder NQ,ES (Default: beide)")
    a = ap.parse_args(argv)
    symbols = a.symbol.split(",") if a.symbol else SYMBOLS

    from ib_async import IB  # lokal importiert: Selbstcheck/Tests brauchen kein ib_async-Netz
    ib = IB()
    ib.connect("127.0.0.1", 4002, clientId=7, readonly=True)
    pacing = PacingLimiter()
    try:
        if a.verify:
            for symbol in symbols:
                dest = fetch_symbol_day(ib, symbol, date.today() - timedelta(days=1), pacing)
                print(f"{symbol}: Verify-Fenster geholt, nichts geschrieben (--verify)"
                      if dest is None else f"{symbol}: unerwartet geschrieben nach {dest}")
        elif a.backfill:
            von, bis = date.fromisoformat(a.backfill[0]), date.fromisoformat(a.backfill[1])
            tag = von
            while tag <= bis:
                for symbol in symbols:
                    fetch_symbol_day(ib, symbol, tag, pacing)
                tag += timedelta(days=1)
        else:
            for symbol in symbols:
                fetch_symbol_day(ib, symbol, date.today() - timedelta(days=1), pacing)
    finally:
        ib.disconnect()
    return 0
```

- [ ] **Step 2: `_demo()` um einen Fetch-Stub-Test erweitern**

In `_demo()`, vor `print("fetch_ibkr ... demo ok")` einfügen:

```python
    # Fetch-Orchestrierung ohne Netz: Stub-IB liefert kanonische Bars, register_load()
    # muss bereits geholte Fenster ueberspringen (kein zweiter reqHistoricalData-Aufruf).
    class _FakeBar:
        def __init__(self, ts, o, h, l, c, v):
            self.date, self.open, self.high, self.low, self.close, self.volume = ts, o, h, l, c, v

    class _StubIB:
        def __init__(self):
            self.calls = 0

        def reqHistoricalData(self, contract, endDateTime, **kw):
            self.calls += 1
            start = int(endDateTime.timestamp()) - WINDOW_SECONDS
            return [_FakeBar(start + i, 100.0 + i, 100.5 + i, 99.5 + i, 100.0 + i, 5)
                    for i in range(0, WINDOW_SECONDS, 900)]

    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        global DATA_DIR
        orig_data_dir = DATA_DIR
        DATA_DIR = Path(tmp)
        try:
            stub = _StubIB()
            pacing = PacingLimiter(clock=lambda: 0.0, sleep=lambda s: None)
            tag = date(2026, 6, 15)
            reg_path = DATA_DIR / "1s-abdeckung.csv"
            dest = fetch_symbol_day(stub, "NQ", tag, pacing, register_path=reg_path)
            assert dest is not None and dest.exists(), "erster Lauf muss eine Datei schreiben"
            erster_call_count = stub.calls
            assert erster_call_count == 46, erster_call_count

            # Zweiter Lauf: Datei existiert schon -> write_day_1s() liefert None, aber
            # fetch_symbol_day holt die Fenster trotzdem erneut an (Register schuetzt nur
            # vor Doppel-Requests INNERHALB eines Laufs, nicht vor einem Re-Lauf auf eine
            # bereits fertige Datei). Stattdessen: Register simuliert einen Abbruch nach
            # 6 Fenstern, zweiter Lauf darf nur die restlichen 40 anfragen.
            dest.unlink()
            reg_path.unlink()
            teil_fenster = day_windows(tag)[:6]
            register_append(
                [{"symbol": "NQ", "von": int(a.timestamp()), "bis": int(b.timestamp()),
                  "kontrakt": "NQU2026", "kerzen": 1800, "geholt_am": 0}
                 for a, b in teil_fenster],
                path=reg_path)
            stub2 = _StubIB()
            fetch_symbol_day(stub2, "NQ", tag, pacing, register_path=reg_path)
            assert stub2.calls == 40, \
                f"Resume nach Abbruch bei 6/46 Fenstern muss 40 Requests machen, waren {stub2.calls}"
        finally:
            DATA_DIR = orig_data_dir

    # Parquet-Roundtrip: Schreiben und Zurücklesen erhaelt Typen und Zeitstempel.
    with tempfile.TemporaryDirectory() as tmp:
        global DATA_DIR
        orig_data_dir = DATA_DIR
        DATA_DIR = Path(tmp)
        try:
            df = pd.DataFrame({"time": [1786752000, 1786752001], "open": [100.0, 100.25],
                               "high": [100.5, 100.5], "low": [99.75, 100.0],
                               "close": [100.25, 100.25], "volume": [3, 5]})
            dest = write_day_1s("NQ", date(2026, 6, 15), df, "NQU2026")
            zurueck = pd.read_parquet(dest)
            assert zurueck["time"].tolist() == [1786752000, 1786752001]
            assert zurueck["contract"].tolist() == ["NQU2026", "NQU2026"]
            assert write_day_1s("NQ", date(2026, 6, 15), df, "NQU2026") is None, \
                "bestehende Datei darf nie ueberschrieben werden"
        finally:
            DATA_DIR = orig_data_dir
```

- [ ] **Step 3: Demo ausführen**

Run: `python algo/fetch_ibkr.py`
Expected: `fetch_ibkr front_month/PacingLimiter demo ok` (alle Asserts in `_demo()` müssen
ohne Exception durchlaufen — `ib_async` wird dabei **nicht** importiert, da `main()` das
erst zur Laufzeit tut)

- [ ] **Step 4: Commit**

```bash
git add algo/fetch_ibkr.py
git commit -m "feat(algo): fetch_ibkr Parquet-Schreiben + Fetch-Orchestrierung (CLI)"
```

---

## Task 4: Nulltoleranz-Gate für 1s-Auflösung anpassen (`tools/analyze_ohlc.py`)

**Files:**
- Modify: `tools/analyze_ohlc.py:193-200` (Degeneriert-Block in `pruefe_kerzen()`)
- Modify: `tools/analyze_ohlc.py` (`demo_pruefe_kerzen()`, Regressionstest ergänzen)

**Interfaces:**
- Consumes: nichts Neues — reine Änderung an bestehender Logik
- Produces: `pruefe_kerzen()` überspringt den Degeneriert-Block, wenn der Median-Abstand
  der Zeitstempel ≤ 5s beträgt (unverändertes Verhalten für alle anderen Checks)

- [ ] **Step 1: Fehlschlagenden Regressionstest zuerst schreiben**

In `tools/analyze_ohlc.py`, in `demo_pruefe_kerzen()`, nach dem Block
`assert pruefe_kerzen(viele_1m), "Intraday-Haeufung muss als weicher Hinweis kommen"`
einfügen:

```python
    # 1s-Aufloesung: derselbe hohe Degeneriert-Anteil ist der NORMALE Abwaerts-Tick
    # (erster Trade der Sekunde ist der hoechste, letzter der tiefste) und darf ueberhaupt
    # keinen Hinweis ausloesen -- weder hart noch weich. Median-Abstand 1s liegt bei
    # DEGEN_MIN_BARS=20 Kerzen klar unter der 5s-Schwelle aus Design SS7.
    viele_1s = [(i * 1, 100 + i, 100 + i, 98 + i, 98 + i) for i in range(50)]
    assert pruefe_kerzen(viele_1s) == [], \
        "1s-Daten mit hohem Degeneriert-Anteil muessen komplett durchgehen"
```

- [ ] **Step 2: Test ausführen, sicherstellen dass er fehlschlägt**

Run: `python -c "from tools.analyze_ohlc import demo_pruefe_kerzen; demo_pruefe_kerzen()"`
(aus dem Repo-Root; alternativ `cd tools && python -c "from analyze_ohlc import
demo_pruefe_kerzen; demo_pruefe_kerzen()"`)
Expected: `AssertionError: 1s-Daten mit hohem Degeneriert-Anteil muessen komplett durchgehen`
(der aktuelle Code liefert bei `viele_1s` denselben weichen Hinweis wie bei `viele_1m`,
weil beide unter `DAILY_SEKUNDEN` liegen und daher als "weich" statt komplett übersprungen
markiert werden)

- [ ] **Step 3: `pruefe_kerzen()` anpassen**

In `tools/analyze_ohlc.py`, den bestehenden Block

```python
    anteil = degeneriert / len(kerzen)
    if len(kerzen) >= DEGEN_MIN_BARS and anteil > DEGEN_MAX_ANTEIL:
        meldung = (f"{degeneriert} von {len(kerzen)} Kerzen degeneriert "
                   f"(open==high & low==close, {anteil:.0%})")
        abstaende = [b - a for a, b in zip(ts_liste, ts_liste[1:])]
        taeglich = abstaende and statistics.median(abstaende) >= DAILY_SEKUNDEN
        (hart if taeglich else weich).append(
            meldung + (" -- Feed-Defekt" if taeglich else " -- duenner Intraday-Feed?"))
```

ersetzen durch:

```python
    anteil = degeneriert / len(kerzen)
    abstaende = [b - a for a, b in zip(ts_liste, ts_liste[1:])]
    median_abstand = statistics.median(abstaende) if abstaende else None
    # Auf 1s-Aufloesung ist ein degenerierter Bar der normale Abwaerts-Tick (erster Trade
    # ist Hoechst-, letzter Tiefstpreis der Sekunde) -- kein Rauschen, das den Nutzer
    # interessiert. Median-Abstand <=5s ist das verlaessliche Signal dafuer (Design SS7).
    if (len(kerzen) >= DEGEN_MIN_BARS and anteil > DEGEN_MAX_ANTEIL
            and (median_abstand is None or median_abstand > 5)):
        meldung = (f"{degeneriert} von {len(kerzen)} Kerzen degeneriert "
                   f"(open==high & low==close, {anteil:.0%})")
        taeglich = median_abstand is not None and median_abstand >= DAILY_SEKUNDEN
        (hart if taeglich else weich).append(
            meldung + (" -- Feed-Defekt" if taeglich else " -- duenner Intraday-Feed?"))
```

- [ ] **Step 4: Test erneut ausführen, sicherstellen dass alles passt**

Run: `python -c "from tools.analyze_ohlc import demo_pruefe_kerzen; demo_pruefe_kerzen()"`
Expected: `analyze_ohlc.pruefe_kerzen demo: OK` (kein Traceback) — insbesondere bleibt der
bestehende Assert für `viele_tgl` (Daily, weiterhin `OHLCDefekt`) und `viele_1m`
(Intraday-Minutenraster, weiterhin weicher Hinweis) unverändert bestehen, weil deren
Median-Abstand (60s bzw. 86400s) über der 5s-Schwelle liegt.

- [ ] **Step 5: Commit**

```bash
git add tools/analyze_ohlc.py
git commit -m "fix(gate): Degeneriert-Check bei <=5s Median-Abstand ueberspringen (1s-Daten)"
```

---

## Task 5: 1s-Parquet-Zweig in `algo/marktdaten.py::_futures_bars()`

**Files:**
- Modify: `algo/marktdaten.py:41-60` (`_futures_bars()`)
- Modify: `algo/marktdaten.py` (`_demo()`, neuen Testfall ergänzen)

**Interfaces:**
- Consumes: `Bar`, `DATA_DIR`, `NY` aus `tools/analyze_ohlc` (bereits importiert),
  `pandas as pd` (bereits importiert)
- Produces: `bars("NQ", "1s", von, bis)` liefert `list[Bar]` mit `v` (Volume) gesetzt

- [ ] **Step 1: `_load_1s_parquet()` + Verzweigung in `_futures_bars()` ergänzen**

In `algo/marktdaten.py`, `_futures_bars()` ersetzen:

```python
def _futures_bars(symbol: str, tf: str, von: date | None, bis: date | None) -> list[Bar]:
    """Unveraendertes Verhalten gegenueber backtest_common.find_days()/load() fuer CSV-TFs --
    ein Bar je Tagesordner-Datei. Fuer tf == '1s' wird stattdessen die Tages-Parquet-Datei
    aus algo/fetch_ibkr.py gelesen (siehe _load_1s_parquet)."""
    out: list[Bar] = []
    for day_dir in sorted(DATA_DIR.glob("*/*/*")):
        if not day_dir.is_dir():
            continue
        try:
            day = datetime.strptime(day_dir.name, "%d.%m.%Y").date()
        except ValueError:
            continue
        if von and day < von:
            continue
        if bis and day > bis:
            continue
        if tf == "1s":
            dateien = sorted(day_dir.glob(f"{symbol} * 1s.parquet"))
            if dateien:
                out.extend(_load_1s_parquet(dateien[0]))
            continue
        dateien = sorted(f for f in day_dir.glob(f"{symbol} * {tf}.csv") if "RTH" not in f.name)
        if dateien:
            out.extend(load(dateien[0]))
    out.sort(key=lambda b: b.t)
    return out


def _load_1s_parquet(path: Path) -> list[Bar]:
    """IBKR-1s-Tagesdatei -> Bar-Liste. `time` ist UNIX-Sekunden UTC (formatDate=2 in
    fetch_ibkr.py), deshalb direkte tz_convert(NY) ohne Zwischenschritt."""
    df = pd.read_parquet(path)
    idx = pd.to_datetime(df["time"], unit="s", utc=True).dt.tz_convert(NY).to_pydatetime()
    return [Bar(t, float(o), float(h), float(l), float(c), float(v))
            for t, o, h, l, c, v in zip(idx, df["open"], df["high"], df["low"],
                                        df["close"], df["volume"])]
```

- [ ] **Step 2: `_demo()` um 1s-Parquet-Testfall erweitern**

In `algo/marktdaten.py`, `_demo()`, nach dem Block zum `von`-Filter (vor `_demo_dst()`
am Ende der Funktion) einfügen:

```python
    # 1s-Parquet-Zweig (IBKR-Anbindung, algo/fetch_ibkr.py): eigenes Tempdir als DATA_DIR,
    # weil _futures_bars() (anders als der Forex-Pfad oben) direkt gegen das importierte
    # DATA_DIR aus analyze_ohlc glob't.
    import analyze_ohlc as ao
    with tempfile.TemporaryDirectory() as tmp:
        orig_dd = ao.DATA_DIR
        global DATA_DIR
        try:
            ao.DATA_DIR = DATA_DIR = Path(tmp)
            tag_dir = DATA_DIR / "2026" / "06" / "15.06.2026"
            tag_dir.mkdir(parents=True)
            df = pd.DataFrame({
                "time": [1781629800, 1781629801, 1781629802],
                "open": [100.0, 100.25, 100.5], "high": [100.5, 100.5, 100.75],
                "low": [99.75, 100.0, 100.25], "close": [100.25, 100.5, 100.5],
                "volume": [3, 5, 2], "contract": ["NQU2026"] * 3,
            })
            df.to_parquet(tag_dir / "NQ 2026-06-15 1s.parquet", index=False)
            b1s = bars("NQ", "1s")
            assert len(b1s) == 3, len(b1s)
            assert b1s[0].t == datetime(2026, 6, 15, 13, 30, tzinfo=NY), b1s[0].t
            assert b1s[0].v == 3.0, b1s[0].v
        finally:
            ao.DATA_DIR = DATA_DIR = orig_dd
```

Am Kopf von `_demo()` (bzw. der Datei) sicherstellen, dass `import tempfile` bereits
vorhanden ist — ist es (siehe bestehender Forex-Testblock).

- [ ] **Step 3: Demo ausführen**

Run: `python algo/marktdaten.py --demo`
Expected: `marktdaten: Selbstcheck ok`

- [ ] **Step 4: Commit**

```bash
git add algo/marktdaten.py
git commit -m "feat(algo): 1s-Parquet-Zweig in marktdaten.py::_futures_bars()"
```

---

## Task 6: `algo/selfcheck.py` — neue Checks einbinden

**Files:**
- Modify: `algo/selfcheck.py`

**Interfaces:**
- Consumes: `fetch_ibkr._demo` (aus Task 1-3), `demo_pruefe_kerzen` (bereits importiert,
  jetzt mit dem 1s-Testfall aus Task 4), `marktdaten._demo` (bereits importiert, jetzt mit
  dem 1s-Testfall aus Task 5) — Task 4 und 5 brauchen also **keinen** neuen Eintrag in
  `CHECKS`, nur Task 1-3 (neues Modul) tut das.

- [ ] **Step 1: Import + CHECKS-Eintrag ergänzen**

In `algo/selfcheck.py`, nach der Zeile `from bias_levels import demo as bias_levels_demo`
einfügen:

```python
from fetch_ibkr import _demo as fetch_ibkr_demo  # noqa: E402
```

In der `CHECKS`-Liste, nach `("bias_levels", bias_levels_demo),` einfügen:

```python
    ("fetch_ibkr", fetch_ibkr_demo),
```

- [ ] **Step 2: Vollen Selbstcheck ausführen**

Run: `python algo/selfcheck.py`
Expected: `Alle N Selbstchecks bestanden.` mit `[OK]   fetch_ibkr` in der Ausgabe, kein
`[FAIL]` — insbesondere **kein** Versuch, `ib_async` zu importieren oder eine Netzverbindung
aufzubauen (der `_demo()`-Pfad aus Task 1-3 tut das nicht, `main()` bleibt ungetestet).

- [ ] **Step 3: Commit**

```bash
git add algo/selfcheck.py
git commit -m "test(algo): fetch_ibkr-Selbstcheck in selfcheck.py einbinden"
```

---

## Task 7: Slash-Command `/daten-1s` + `.gitignore`

**Files:**
- Create: `.claude/commands/daten-1s.md`
- Modify: `.gitignore`

**Interfaces:**
- Consumes: `algo/fetch_ibkr.py` CLI (`--verify`, `--backfill VON BIS`, `--symbol`) aus
  Task 3

- [ ] **Step 1: `.gitignore` ergänzen**

In `.gitignore`, im Abschnitt `# --- Zugangsdaten ---` nach der Zeile
`algo/.secrets.yaml` einfügen:

```
# IBC-Konfiguration (IB-Gateway-Auto-Login) landet hier NIE direkt -- die eigentliche
# Config liegt unter %USERPROFILE%\ibc\, dieser Eintrag faengt nur einen versehentlichen
# Kopiervorgang ins Repo ab (Design SS9).
algo/ibc/
```

- [ ] **Step 2: `.claude/commands/daten-1s.md` anlegen**

Muster wie `.claude/commands/algo-live-status.md` (siehe dortiges Frontmatter-Format):

```markdown
---
description: 1s-Datenanbindung fuer NQ/ES ueber IBKR -- Nachlad, Verify oder Backfill, je nach Argument (Design docs/superpowers/specs/2026-08-15-ibkr-1s-datenanbindung-design.md)
---

Fuehre einen Datenabruf ueber `algo/fetch_ibkr.py` aus. Argumente (siehe `$ARGUMENTS`,
alle optional, Default = Nachlad):

- kein Argument: Nachlad (letzter Registereintrag bis gestern, beide Symbole)
- `verify`: Einzelfenster-Verifikation, schreibt nichts
- `NQ` oder `ES`: schraenkt jede Betriebsart auf ein Symbol ein
- `backfill <von> <bis>`: Backfill fuer den Zeitraum (ISO-Daten, z.B. `2026-02-17 2026-08-14`)

Kombinierbar, z.B. `verify ES` oder `backfill 2026-02-17 2026-08-14 NQ`.

1. Pruefe, ob Port 4002 (IB Gateway, Paper) erreichbar ist (z.B. per kurzem TCP-Connect-Test).
   Nicht erreichbar: melde, dass IB Gateway nicht laeuft, und brich ab -- lauf nicht in
   einen Timeout.
2. Baue daraus den passenden Aufruf von `python algo/fetch_ibkr.py [--verify|--backfill VON BIS]
   [--symbol SYM]` und starte ihn. Bei `backfill`: im Hintergrund, weil die Laufzeit in
   Stunden liegt (siehe Design SS3.4) -- nicht auf den Abschluss warten, sondern das Anlaufen
   bestaetigen und mitteilen, wie der Fortschritt spaeter geprueft werden kann (Registerzeilen
   in `raw/marktdaten/1s-abdeckung.csv`).
3. Verdichte die Konsolenausgabe zu einem Bericht statt sie durchzureichen: geholte Fenster
   je Symbol, geschriebene Tagesdateien, Kerzenzahl, Quote handelsloser Sekunden je Session
   (falls ausgegeben), alle Hinweise aus `pruefe_kerzen()`, fehlgeschlagene Fenster,
   verbleibende Luecken laut Register.
4. Kein `push.ps1` -- Veroeffentlichen bleibt manuell (siehe CLAUDE.md, Versionskontrolle).
```

- [ ] **Step 3: Commit**

```bash
git add .claude/commands/daten-1s.md .gitignore
git commit -m "feat: Slash-Command /daten-1s + gitignore fuer algo/ibc/"
```

---

## Task 8: Dokumentation nachziehen (README, PLAN, wiki/log, CLAUDE.md)

**Files:**
- Modify: `algo/README.md`
- Modify: `algo/PLAN.md`
- Modify: `wiki/log.md`
- Modify: `CLAUDE.md`

**Interfaces:** keine (reine Doku, keine Code-Abhängigkeiten)

- [ ] **Step 1: `algo/README.md` — neuen Modulabschnitt ergänzen**

Nach dem Abschnitt `## \`bias_levels.py\` -- Levels + News fuer die Bias-Vorlage` (Ende der
Datei) anfügen, im etablierten Was/Wie/Warum-Muster der übrigen Abschnitte:

```markdown
## `fetch_ibkr.py` -- Sekundengenaue NQ/ES-Daten ueber IBKR

**Was:** Laedt 1s-OHLC-Bars fuer NQ und ES ueber die IBKR-TWS/Gateway-API und legt sie als
Tages-Parquet in `raw/marktdaten/<jjjj>/<mm>/<tt.mm.jjjj>/<SYM> <jjjj-mm-tt> 1s.parquet` ab
-- gleiche Ordnerstruktur wie die TradingView-/yfinance-CSVs, nur Parquet statt CSV wegen
Volumen (~5x kleiner, siehe Design SS4). Drei Betriebsarten: `--verify` (ein Fenster, schreibt
nichts), `--backfill VON BIS`, ohne Argumente = Nachlad seit dem letzten Registereintrag.
Siehe `docs/superpowers/specs/2026-08-15-ibkr-1s-datenanbindung-design.md` fuer die volle
Entscheidungshistorie (E1-E11).

**Wie:** `front_month()` bestimmt den aktiven Quartalskontrakt deterministisch und netzfrei
(Roll = Verfall - 8 Tage). `day_windows()` zerlegt einen Handelstag in 46 Fenster a 30 Minuten
(18:00 NY Vortag - 17:00 NY), DST-sicher ueber tz-awares NY-Datetime-Arithmetik.
`PacingLimiter` haelt die IBKR-Grenze (60 Requests/10 Min, min. 0,5s Abstand) ein, mit
injizierbarer Uhr fuer Tests. `raw/marktdaten/1s-abdeckung.csv` (append-only) loest drei
Probleme: "kein Trade" vs. "nicht geholt" unterscheidbar machen, Backfill wiederaufnehmbar
machen, Nachlad zustandslos machen.

**Warum:** IBKR ist dieselbe Quelle wie die spaetere Order-Ausfuehrung -- keine Quellen-Drift
zwischen Backtest und Live-Betrieb (E1). NQ/ES statt MNQ, weil beide vom gebuchten
CME-L1-Paket abgedeckt sind und deutlich liquider (E2); MNQ-Backtests bleiben unveraendert
gueltig, MNQ ist derselbe Index mit derselben Tickgroesse.

**Bekannte Grenzen:** `main()`/die echte `ib_async.IB()`-Verbindung ist NICHT durch
`selfcheck.py` abgedeckt -- das braucht ein laufendes IB Gateway und wird ausschliesslich
manuell auf dem Windows-Rechner des Nutzers verifiziert (`--verify` vor jedem Backfill).
Verbindet sich ausschliesslich readonly gegen Port 4002 (Paper) -- siehe Design SS9 fuer die
beiden Absicherungen gegen einen Live-Order-Pfad. Ob IBKR 1s-Bars fuer bereits verfallene
Kontrakte liefert (`includeExpired=True`), war zum Zeitpunkt der Implementierung ungeprueft
(Design R1) -- Ergebnis der Verifikation in `algo/PLAN.md` nachtragen.
```

- [ ] **Step 2: `algo/PLAN.md` — Log-Eintrag anhängen**

Am Ende der Backlog-/Log-Abschnitte (vor `## Naechster Schritt`) einfügen:

```markdown
### Erledigt: IBKR 1s-Datenanbindung fuer NQ/ES implementiert (2026-08-15)

Design `docs/superpowers/specs/2026-08-15-ibkr-1s-datenanbindung-design.md` umgesetzt:
`algo/fetch_ibkr.py` (Front-Monat-Aufloesung, Pacing-Limiter, Fenster-Zerlegung,
Abdeckungs-Register, Parquet-Schreiben), Nulltoleranz-Gate ueberspringt den
Degeneriert-Check bei <=5s Median-Abstand (`tools/analyze_ohlc.py`), 1s-Parquet-Zweig in
`algo/marktdaten.py::_futures_bars()`, Slash-Command `/daten-1s`, alle Selbstchecks in
`algo/selfcheck.py` eingebunden.

**Noch offen (nicht agentisch ausfuehrbar, siehe Design SS12.2):** TradingView-1m-Referenz-
Export fuer NQ/ES, Client-Portal-Haken fuer Paper-Datenspiegelung, IB-Gateway+IBC-Einrichtung,
`--verify` auf dem Windows-Rechner des Nutzers, danach Backfill (~34h). Ergebnis der
Verifikation (insbesondere R1: liefert IBKR 1s fuer verfallene Kontrakte?) hier nachtragen,
sobald durchgefuehrt. `raw/algo-pruefung/IBKR 1s-Datenanbindung -- Uebergabestand
2026-08-15.md` erst nach erfolgreicher Verifikation loeschen (Design SS1).
```

- [ ] **Step 3: `wiki/log.md` — Eintrag Typ `setup` anhängen**

Ans Ende von `wiki/log.md` anfügen (Format siehe CLAUDE.md `log.md`-Format):

```markdown
## [2026-08-15] setup | IBKR 1s-Datenanbindung NQ/ES
- Seiten aktualisiert: keine (reine Code-/Infrastruktur-Aenderung, siehe algo/PLAN.md)
- `algo/fetch_ibkr.py` neu; `tools/analyze_ohlc.py`, `algo/marktdaten.py`,
  `algo/selfcheck.py`, `CLAUDE.md` geaendert; `.claude/commands/daten-1s.md` neu
- Details: docs/superpowers/specs/2026-08-15-ibkr-1s-datenanbindung-design.md,
  algo/PLAN.md (Eintrag 2026-08-15)
```

- [ ] **Step 4: `CLAUDE.md` — Layer 0, Layer 1, Roadmap Punkt 1, Domänenkontext algo (§12.1)**

In `CLAUDE.md`, Abschnitt `## Layer 0 — Übergeordnetes Ziel: autonomer IBKR-Handelsalgorithmus`,
im ersten Absatz die Formulierung

```
Baue aus den täglich wachsenden OHLC-Daten in `raw/marktdaten/` einen regelbasierten, statistisch
validierten Handelsalgorithmus, der sich per IBKR-API selbstständig ausführt.
```

wird nicht verändert (bleibt Symbol-agnostisch formuliert) — stattdessen im ersten Satz des
Abschnitts (`einen Handelsalgorithmus für MNQ`) MNQ durch NQ und ES ersetzen:

Alt:
```
**Verfolge als Ziel von allem in diesem Repo** — Wiki, `raw/marktdaten/`, `tools/analyze_ohlc.py`,
`algo/` — einen Handelsalgorithmus für MNQ, der **selbstständig und allein über Interactive
Brokers** (TWS/IB-Gateway-API) handelt.
```

Neu:
```
**Verfolge als Ziel von allem in diesem Repo** — Wiki, `raw/marktdaten/`, `tools/analyze_ohlc.py`,
`algo/` — einen Handelsalgorithmus für NQ und ES, der **selbstständig und allein über Interactive
Brokers** (TWS/IB-Gateway-API) handelt. NQ/ES statt MNQ seit 2026-08-15: sekundengenaue
IBKR-Daten liegen für beide vor (`algo/fetch_ibkr.py`), beide sind deutlich liquider, und die
Punktwerte (NQ $20, ES $50) sind in `algo/pnl.py` bereits hinterlegt — siehe
`docs/superpowers/specs/2026-08-15-ibkr-1s-datenanbindung-design.md`.
```

In `## Layer 1`, im `raw/`-Baumdiagramm, die Zeile

```
    marktdaten/          OHLC-Rohdaten für den Algo (siehe Layer 0), TradingView-Exporte +
                          yfinance-Nachlad, Jahr/Monat/Tag verschachtelt — **wie Gold behandeln**,
                          siehe [[Algo-Trading: Arbeitsstandards]]
```

ersetzen durch:

```
    marktdaten/          OHLC-Rohdaten für den Algo (siehe Layer 0), TradingView-Exporte +
                          yfinance-Nachlad + IBKR-1s-Anbindung (NQ/ES, `algo/fetch_ibkr.py`),
                          Jahr/Monat/Tag verschachtelt — **wie Gold behandeln**,
                          siehe [[Algo-Trading: Arbeitsstandards]]
```

In `## Algo-Trading: Roadmap zur IBKR-Anbindung`, Punkt 1, den Satz

```
Ziehe für mehr Historie in Intraday-Auflösung perspektivisch eine zweite Datenquelle heran
(Kandidat: IBKR selbst, sobald die API-Anbindung aus Punkt 4 steht — historische Daten und
Live-Order-Ausführung über denselben Broker zu beziehen vermeidet Datenquellen-Drift zwischen
Backtest und Live-Betrieb).
```

ersetzen durch:

```
Für NQ/ES steht seit 2026-08-15 sekundengenaue IBKR-Historie zur Verfügung
(`algo/fetch_ibkr.py`, `/daten-1s`) — IBKR ist damit die primäre Intraday-Quelle für diese
beiden Symbole, nicht mehr nur ein perspektivischer Kandidat; historische Daten und
Live-Order-Ausführung laufen über denselben Broker, das vermeidet Datenquellen-Drift zwischen
Backtest und Live-Betrieb.
```

In `## Domänenkontext: algo (MNQ-Backtesting)`, die Überschrift und den ersten Satz:

Alt:
```
## Domänenkontext: algo (MNQ-Backtesting)

`algo/` enthält den gesamten Backtesting-/Validierungs-Stack für Layer 0 (siehe `algo/README.md`
```

Neu:
```
## Domänenkontext: algo (NQ/ES-Backtesting)

`algo/` enthält den gesamten Backtesting-/Validierungs-Stack für Layer 0 (siehe `algo/README.md`
```

Die Sperre gegen Live-Handel ohne gesonderte Freigabe (Roadmap Punkt 5) bleibt wortgleich —
keine Änderung an diesem Abschnitt.

- [ ] **Step 5: Commit**

```bash
git add algo/README.md algo/PLAN.md wiki/log.md CLAUDE.md
git commit -m "docs: IBKR-1s-Datenanbindung in README/PLAN/wiki/log/CLAUDE.md nachziehen"
```

---

## Task 9: Manuelle Inbetriebnahme (User, außerhalb der Agenten-Sandbox)

**Files:** keine Code-Änderung — dieser Task ist eine Checkliste für den Nutzer, kein
Agenten-Task. Er wird hier dokumentiert, damit der Plan vollständig ist (Design §12.2,
Schritte 2-5), aber **kein Subagent sollte versuchen, ihn auszuführen** — die Sandbox hat
keinen Netzzugriff auf eine lokale IB-Gateway-Instanz.

**Interfaces:** keine

- [ ] **Schritt A: Referenzdaten beschaffen (Design §6.1)**

Je ein manueller TradingView-1m-Export für NQ und ES eines beliebigen der letzten
Handelstage besorgen, nach `raw/` legen, einspielen:

```bash
python algo/ingest_tvexport.py <datei> NQ --tf 1m
python algo/ingest_tvexport.py <datei> ES --tf 1m
```

- [ ] **Schritt B: Client-Portal-Haken setzen**

Im IBKR Client Portal „Share real-time market data with paper account" aktivieren (Design §9)
— sonst liefert Port 4002 keine gespiegelten Marktdaten (Risiko R2).

- [ ] **Schritt C: IB Gateway + IBC einrichten**

IB Gateway (nicht TWS) installieren, IBC für automatischen Login + Tages-Restart-Handling
konfigurieren. Config liegt unter `%USERPROFILE%\ibc\`, außerhalb des Repos (Design §9,
Secrets-Absatz).

- [ ] **Schritt D: `--verify` ausführen**

Auf dem Windows-Rechner mit laufendem Gateway:

```bash
python algo/fetch_ibkr.py --verify
```

Gegen die Checkliste aus Design §6 prüfen: (1) liefert IBKR 1s-Bars, (2) auch für verfallene
Kontrakte (`includeExpired=True`), (3) Zeitstempel gegen den TradingView-Export aus Schritt A,
(4) Preise per `pruefe_gegen_referenz(toleranz=0.01)`, (5) Quote handelsloser Sekunden je
Session, (6) `pruefe_kerzen()` grün. **Nicht weitermachen, bevor dieser Schritt grün ist** —
34 Stunden Backfill auf einer ungeprüften Annahme sind teuer (Design §6).

Ergebnis (insbesondere zu R1: verfallene Kontrakte) in `algo/PLAN.md` nachtragen (siehe
Task 8, Step 2).

- [ ] **Schritt E: Backfill**

```bash
python algo/fetch_ibkr.py --backfill 2026-02-17 2026-08-14
```

Läuft ~34h, unterbrechbar (Register macht den Lauf resumable). Danach: geplante tägliche
Windows-Aufgabe (17:30 NY) für den Nachlad einrichten (Design §9).

- [ ] **Schritt F: Übergabestand-Dokument löschen**

Erst nachdem Schritt D erfolgreich war und Schritt E läuft/abgeschlossen ist:

```bash
git rm "raw/algo-pruefung/IBKR 1s-Datenanbindung — Übergabestand 2026-08-15.md"
git commit -m "chore: IBKR-1s-Uebergabestand geloescht, in algo/PLAN.md/README.md aufgegangen"
```

---

## Self-Review-Notizen (bereits eingearbeitet)

- **Spec-Abdeckung:** Alle 13 Lieferpunkte aus Design §12 sind abgedeckt: 1-2 (Task 1), 3
  (Task 4), 4 (Task 5), 5 (Task 6), 6 (Task 7), 7 (Task 7), 8 (Task 9, manuell), 9-12
  (Task 8), 13 (Task 9, Schritt F, bedingt auf erfolgreiche Verifikation).
- **Typkonsistenz geprüft:** `fetch_symbol_day(ib, symbol, day, pacing, register_path=...)`
  wird in Task 2/3 konsistent verwendet; `write_day_1s()`-Signatur identisch in Definition
  und allen Aufrufstellen (Task 3, Task 8-README).
- **Kein Platzhalter:** jeder Step enthält lauffähigen Code oder eine konkrete
  Bash-/CLI-Anweisung, keine „TODO"/„siehe oben"-Verweise auf Code außerhalb des jeweiligen
  Tasks (Code aus Task N wird in Task N+1 vollständig wiederholt zitiert, wo referenziert).
- **Bewusste Abweichung von Design §12, Punkt 1 (`algo/requirements.txt`):** ist kein
  eigener Task, sondern in Task 1 gefaltet — der Reviewer kann Task 1 nicht sinnvoll ohne
  die Dependency-Zeile akzeptieren (Task Right-Sizing).

---

## Execution Handoff

Zwei Ausführungsoptionen:

**1. Subagent-Driven (empfohlen)** — Ich dispatche pro Task einen frischen Subagenten,
Review zwischen den Tasks, schnelle Iteration.

**2. Inline Execution** — Ich führe die Tasks in dieser Session aus, mit
Batch-Ausführung und Checkpoints zur Durchsicht.

Task 9 (manuelle Inbetriebnahme) läuft in beiden Fällen **nicht** automatisiert — das ist
eine Checkliste für dich auf deinem Windows-Rechner, siehe Design §12.2.

Welchen Ansatz möchtest du?
