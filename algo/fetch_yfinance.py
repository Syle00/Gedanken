#!/usr/bin/env python3
"""Laedt MNQ-Marktdaten per yfinance und legt sie im raw/marktdaten/-Format ab
(gleiches Schema wie die TradingView-Exporte: time,open,high,low,close).

1m fehlt bewusst: yfinance liefert Minutendaten nur fuer die letzten ~7 Tage,
fuer Backfills also ungeeignet. 4h gibt es bei yfinance nicht nativ und wird
aus 1h resampled (naiv ab Tagesstart, nicht CME-Session-aligned).
# ponytail: 4h-Resampling ist ein grobes Raster, kein exaktes Session-Grid;
# falls das mal einen Unterschied macht: an CME-Session-Start (18:00 NY) ausrichten.

Aufruf:
    python algo/fetch_yfinance.py 2026-07-01 2026-08-01   # end exklusiv
"""

from __future__ import annotations

import sys
from datetime import timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import yfinance as yf

NY = ZoneInfo("America/New_York")
DATA_DIR = Path(__file__).resolve().parent.parent / "raw" / "marktdaten"
SYMBOL = "MNQ=F"
INTERVALS = ["5m", "15m", "1h", "1d"]


def trading_day(ts: pd.Timestamp, daily: bool = False):
    if daily:
        return ts.date()
    ts = ts.tz_convert(NY)
    return ts.date() + timedelta(days=1) if ts.hour >= 18 else ts.date()


def flatten(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df


def write_day(tf: str, day, rows: pd.DataFrame) -> Path | None:
    dest = (DATA_DIR / f"{day:%Y}" / f"{day:%m}" / f"{day:%d.%m.%Y}"
            / f"MNQ {day.isoformat()} {tf}.csv")
    if dest.exists():
        # raw/ ist unveraenderlich -- bestehende Exporte (z.B. von TradingView) nie ueberschreiben.
        print(f"  = {dest.relative_to(DATA_DIR)} existiert bereits, uebersprungen")
        return None
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


def fetch(start: str, end: str) -> list[Path]:
    written = []
    hourly = None
    for tf in INTERVALS:
        df = flatten(yf.download(SYMBOL, start=start, end=end, interval=tf, progress=False))
        if df.empty:
            print(f"  ! {tf}: keine Daten (yfinance-Limit fuer diesen Zeitraum?)")
            continue
        daily = tf == "1d"
        if tf == "1h":
            hourly = df
        for day, rows in df.groupby(df.index.map(lambda ts: trading_day(ts, daily))):
            f = write_day(tf, day, rows)
            if f:
                written.append(f)

    if hourly is not None:
        h4 = (hourly.resample("4h").agg(
            {"Open": "first", "High": "max", "Low": "min", "Close": "last"}).dropna())
        for day, rows in h4.groupby(h4.index.map(trading_day)):
            f = write_day("4h", day, rows)
            if f:
                written.append(f)
    return written


def main(argv=None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) != 2:
        print("Nutzung: python algo/fetch_yfinance.py <start YYYY-MM-DD> <end YYYY-MM-DD (exklusiv)>")
        return 1
    files = fetch(*args)
    print(f"{len(files)} Datei(en) geschrieben.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
