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

    print("fetch_ibkr front_month/PacingLimiter demo ok")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        _demo()
    else:
        print(__doc__)
