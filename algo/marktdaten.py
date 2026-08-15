#!/usr/bin/env python3
"""Ein Einstieg fuer alle Backtest-Module: `bars(symbol, tf, von, bis)` liefert die bestehende
`Bar`-Liste, egal ob das Symbol aus raw/marktdaten/ (Futures, CSV je Timeframe) oder aus dem
histdata-Parquet-Cache (Forex, resampled aus 1m) stammt. Kein Detektor merkt den Unterschied.

Aufruf:
    python algo/marktdaten.py --demo
"""
from __future__ import annotations

import sys
from datetime import date, datetime
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from analyze_ohlc import Bar, DATA_DIR, NY, SESSION_TYP, load  # noqa: E402
from build_parquet import CACHE  # noqa: E402

PANDAS_FREQ = {"1m": "1min", "5m": "5min", "15m": "15min", "1h": "1h", "4h": "4h", "1d": "1D"}


def bars(symbol: str, tf: str, von: date | None = None, bis: date | None = None) -> list[Bar]:
    if SESSION_TYP.get(symbol) == "24x5":
        return _forex_bars(symbol, tf, von, bis)
    return _futures_bars(symbol, tf, von, bis)


def _futures_bars(symbol: str, tf: str, von: date | None, bis: date | None) -> list[Bar]:
    """Unveraendertes Verhalten gegenueber backtest_common.find_days()/load() -- ein Bar
    je Tagesordner-Datei, im Bestand bereits im Ziel-Timeframe vorliegend."""
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
        dateien = sorted(f for f in day_dir.glob(f"{symbol} * {tf}.csv") if "RTH" not in f.name)
        if dateien:
            out.extend(load(dateien[0]))
    out.sort(key=lambda b: b.t)
    return out


def _forex_bars(symbol: str, tf: str, von: date | None, bis: date | None) -> list[Bar]:
    """Liest den 1m-Parquet-Cache, resampled bei Bedarf. Anker an NY-Mitternacht: der Index
    ist bereits NY-lokalisiert, `origin="start_day"` verankert Resample-Buckets deshalb an
    NY-00:00, nicht UTC-Mitternacht (Spec §5.3)."""
    df = pd.read_parquet(CACHE / f"{symbol}_1m.parquet")
    idx = pd.to_datetime(df["time"], unit="s", utc=True).dt.tz_convert(NY)
    df = df.set_index(idx).drop(columns="time").sort_index()

    if tf != "1m":
        df = df.resample(PANDAS_FREQ[tf], label="left", closed="left",
                         origin="start_day").agg(
            {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()

    if von:
        df = df[df.index.date >= von]
    if bis:
        df = df[df.index.date <= bis]

    return [Bar(t.to_pydatetime(), r.open, r.high, r.low, r.close) for t, r in df.iterrows()]


def _demo() -> None:
    """Selbstcheck: winziger Parquet-Cache in ein Tempdir, prueft Resample-Anker (NY-
    Mitternacht) und von/bis-Filter. Futures-Pfad wird NICHT hier getestet (der laeuft
    unveraendert ueber tools.analyze_ohlc.load(), bereits durch selfcheck.py abgedeckt)."""
    import tempfile
    import build_parquet as bp

    with tempfile.TemporaryDirectory() as tmp:
        tief = Path(tmp) / "marktdaten-tief" / "2026" / "01" / "05.01.2026"
        tief.mkdir(parents=True)
        basis = int(datetime(2026, 1, 5, 0, 0, tzinfo=NY).timestamp())
        zeilen = ["time,open,high,low,close"]
        for i in range(240):  # 0:00-3:59 NY, in 1m-Schritten
            zeilen.append(f"{basis + i * 60},1.1,1.1001,1.0999,1.1")
        (tief / "TEST 2026-01-05 1m (bid).csv").write_text("\n".join(zeilen), encoding="utf-8")

        cache = Path(tmp) / "cache"
        bp.build("TEST", tief_dir=Path(tmp) / "marktdaten-tief", cache_dir=cache)

        global CACHE
        orig = CACHE
        CACHE = cache
        SESSION_TYP["TEST"] = "24x5"
        try:
            b1m = bars("TEST", "1m")
            assert len(b1m) == 240, len(b1m)
            assert b1m[0].t == datetime(2026, 1, 5, 0, 0, tzinfo=NY), b1m[0].t

            b4h = bars("TEST", "4h")
            # Anker an NY-Mitternacht: die erste 4h-Kerze muss um 0:00 beginnen, nicht
            # verschoben durch UTC-Anker (waere hier 19:00 des Vortags, siehe Spec §5.3).
            assert b4h[0].t == datetime(2026, 1, 5, 0, 0, tzinfo=NY), b4h[0].t
            assert len(b4h) == 1, len(b4h)  # 4 Stunden Daten -> genau eine 4h-Kerze

            gefiltert = bars("TEST", "1m", von=date(2026, 1, 6))
            assert gefiltert == [], "von-Filter muss ausserhalb liegende Tage ausschliessen"
        finally:
            CACHE = orig
            del SESSION_TYP["TEST"]
    print("marktdaten: Selbstcheck ok")


def main() -> int:
    if "--demo" in sys.argv:
        _demo()
        return 0
    print(__doc__)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
