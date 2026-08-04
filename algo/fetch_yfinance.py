#!/usr/bin/env python3
"""Laedt MNQ-Marktdaten per yfinance und legt sie im raw/marktdaten/-Format ab
(gleiches Schema wie die TradingView-Exporte: time,open,high,low,close).

Intraday-TFs werden geladen, wo yfinance es hergibt -- 1m nur die letzten ~30 Tage
(7-Tage-Haeppchen pro Request), 5m/15m nur die letzten ~60 Tage (55-Tage-Haeppchen,
siehe `CHUNK_DAYS`/`download_interval`). Fuer aeltere Tage bleiben sie leer, das ist
eine harte Yahoo-Grenze, kein Bug hier. 4h gibt es bei yfinance nicht nativ und wird
aus 1h resampled (naiv ab Tagesstart, nicht CME-Session-aligned).

Zusaetzlich zur vollen Session schreibt das Skript fuer 5m/15m/1h je einen
RTH-Ausschnitt (09:30-16:00 NY, wie das bestehende manuelle Referenzfile) als
eigene "<tf> RTH.csv" -- yfinance liefert keinen separaten RTH-Feed, das ist
derselbe Datenstrom, nur auf das Zeitfenster gefiltert.
# ponytail: 4h-Resampling ist ein grobes Raster, kein exaktes Session-Grid;
# falls das mal einen Unterschied macht: an CME-Session-Start (18:00 NY) ausrichten.

Aufruf:
    python algo/fetch_yfinance.py 2026-07-01 2026-08-01   # end exklusiv
"""

from __future__ import annotations

import sys
from datetime import date, time as dtime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import yfinance as yf

NY = ZoneInfo("America/New_York")
DATA_DIR = Path(__file__).resolve().parent.parent / "raw" / "marktdaten"
SYMBOL = "MNQ=F"
INTERVALS = ["1m", "5m", "15m", "1h", "1d"]
RTH_TFS = ["1m", "5m", "15m", "1h"]  # wie beim bestehenden manuellen Export: 09:30-16:00 NY
RTH_START, RTH_END = dtime(9, 30), dtime(16, 0)
# yfinance lehnt Requests ab, die aelter als dieses Fenster sind -- ausserhalb
# davon bleibt der jeweilige Timeframe leer, das ist eine harte Yahoo-Grenze.
CHUNK_DAYS = {"1m": 7, "5m": 55, "15m": 55}  # 55 statt 60, Sicherheitsabstand zum Limit


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


def download_interval(tf: str, start: str, end: str) -> pd.DataFrame:
    """Intraday-TFs (1m/5m/15m) in CHUNK_DAYS-Haeppchen anfragen (yfinance lehnt einen
    Request sonst komplett ab, wenn die Spanne aelter als sein Limit ist -- nicht nur
    den zu alten Teil); ein Chunk ausserhalb des jeweiligen Fensters liefert leer zurueck."""
    if tf not in CHUNK_DAYS:
        return flatten(yf.download(SYMBOL, start=start, end=end, interval=tf, progress=False))
    cur, end_d = date.fromisoformat(start), date.fromisoformat(end)
    chunks = []
    while cur < end_d:
        nxt = min(cur + timedelta(days=CHUNK_DAYS[tf]), end_d)
        df = flatten(yf.download(SYMBOL, start=cur.isoformat(), end=nxt.isoformat(),
                                  interval=tf, progress=False))
        if not df.empty:
            chunks.append(df)
        cur = nxt
    return pd.concat(chunks) if chunks else pd.DataFrame()


def fetch(start: str, end: str) -> list[Path]:
    written = []
    hourly = None
    for tf in INTERVALS:
        df = download_interval(tf, start, end)
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

        if tf in RTH_TFS:
            ny_time = df.index.tz_convert(NY).time
            rth = df[(ny_time >= RTH_START) & (ny_time <= RTH_END)]
            for day, rows in rth.groupby(rth.index.tz_convert(NY).date):
                f = write_day(f"{tf} RTH", day, rows)
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
