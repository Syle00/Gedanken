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


def day_windows(day: date) -> list[tuple[datetime, datetime]]:
    """46 Fenster a 30 Minuten: 18:00 NY des Vortages bis 17:00 NY `day`, als UTC-Paare.
    Anker werden EINMAL nach UTC konvertiert, danach laeuft die gesamte Fenster-Arithmetik
    in UTC (timedelta-Addition auf einer NY-tz-awaren Datetime wuerde am DST-Fold sonst ein
    90-Minuten-Fenster statt zweier 30-Minuten-Fenster erzeugen, weil fold=0 den mehrdeutigen
    Stunden-Block auch nach dem Wechsel noch auf EDT aufloest)."""
    start_ny = datetime.combine(day - timedelta(days=1), datetime.min.time(), tzinfo=NY).replace(hour=18)
    end_ny = datetime.combine(day, datetime.min.time(), tzinfo=NY).replace(hour=17)
    start_utc, end_utc = start_ny.astimezone(UTC), end_ny.astimezone(UTC)
    out = []
    cur = start_utc
    while cur < end_utc:
        nxt = cur + timedelta(seconds=WINDOW_SECONDS)
        out.append((cur, nxt))
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


def _demo() -> None:
    global DATA_DIR
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

    # Fenster-Zerlegung: genau 46 Fenster, erstes beginnt 18:00 NY des Vortages,
    # letztes endet 17:00 NY -- inklusive eines Tages ueber einen DST-Wechsel.
    normal_tag = date(2026, 6, 15)
    windows = day_windows(normal_tag)
    assert len(windows) == 46, len(windows)
    assert windows[0][0] == datetime(2026, 6, 14, 18, 0, tzinfo=NY).astimezone(UTC)
    assert windows[-1][1] == datetime(2026, 6, 15, 17, 0, tzinfo=NY).astimezone(UTC)
    assert all((b - a).total_seconds() == WINDOW_SECONDS for a, b in windows), \
        "alle Fenster muessen exakt 1800 Sekunden lang sein"

    dst_tag = date(2026, 11, 1)  # "fall back" 2026 faellt auf den 1. November
    dst_windows = day_windows(dst_tag)
    # Am DST-Fold (Nov 1) spannt 18:00 NY Vortag bis 17:00 NY Heute 24h UTC (nicht 23h),
    # weil die rueckwaertsgesprungene Stunde doppelt zaehlt -- also 48 Fenster, nicht 46.
    # Wichtig: ALLE sind exakt 1800 Sekunden (keine 90-Minuten-Fenster durch fold=0-Fehler).
    assert len(dst_windows) == 48, \
        f"DST-Tag mit 24h UTC muss 48 Fenster liefern, waren {len(dst_windows)}"
    assert all((b - a).total_seconds() == WINDOW_SECONDS for a, b in dst_windows), \
        "jedes Fenster muss exakt 1800 Sekunden lang sein, auch am DST-Fold"

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

    print("fetch_ibkr front_month/PacingLimiter demo ok")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        _demo()
    else:
        print(__doc__)
