"""Importiert histdata.com-XLSX-Exporte (Generic ASCII/XLSX, M1) nach raw/marktdaten-tief/.

Aufruf:
    python algo/ingest_histdata_xlsx.py raw/HISTDATA_COM_XLSX_EURUSD_M12000.zip

Warum ein eigenes Ingest-Skript statt direktem Nachbau in fetch_dukascopy.py: histdata.com liefert
fertige M1-Bars (keine Ticks) in einer voellig anderen Konvention -- feste EST-Zeitzone ohne DST
("The timezone of all data is: Eastern Standard Time (EST) time-zone WITHOUT Day Light Savings
adjustments.", histdata.com FAQ) und **Bid-Preise statt Mid** ("the bar prices ... are based on the
tick Bid price."). Das ist bewusst NICHT die gleiche Preisbasis wie fetch_dukascopy.py (dort Mid,
weil IBKR Devisen als Midpoint-Bars liefert) -- deshalb eigene Dateiendung ' 1m (bid).csv' statt
' 1m.csv', damit Bid- und Mid-Bestand nie versehentlich vermischt werden.

Zeitkonvertierung: naive Zeitstempel + 5h = UTC (feste EST-Verschiebung, keine DST-Fallunterscheidung
noetig). Tagesordner richten sich trotzdem nach dem echten NY-Kalendertag (ZoneInfo, mit DST) --
gleiche Begruendung wie in fetch_dukascopy.py: die Ablage-Grenze ist vault-weit einheitlich der
NY-Handelstag, unabhaengig von der Zeitzonen-Konvention der Quelle.
"""
from __future__ import annotations

import argparse
import csv
import sys
import zipfile
from collections import defaultdict
from datetime import timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from analyze_ohlc import pruefe_kerzen  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT_ROOT = ROOT / "raw" / "marktdaten-tief"
NY = ZoneInfo("America/New_York")
EST_OFFSET = timedelta(hours=5)  # histdata.com: feste EST, keine Sommerzeit


def lade_xlsx_aus_zip(zip_pfad: Path) -> tuple[str, pd.DataFrame]:
    with zipfile.ZipFile(zip_pfad) as zf:
        xlsx_namen = [n for n in zf.namelist() if n.lower().endswith(".xlsx")]
        if len(xlsx_namen) != 1:
            sys.exit(f"{zip_pfad}: erwarte genau eine .xlsx im Archiv, gefunden: {xlsx_namen}")
        with zf.open(xlsx_namen[0]) as fh:
            df = pd.read_excel(fh, sheet_name=0, header=None,
                                names=["time", "open", "high", "low", "close", "vol"])
    symbol = xlsx_namen[0].split("_")[2].upper()  # DAT_XLSX_<SYMBOL>_M1_<JAHR>.xlsx
    return symbol, df


def konvertiere(df: pd.DataFrame) -> pd.DataFrame:
    """Zeitspalten in Sekundenaufloesung halten -- .as_unit("s") statt manueller Division, siehe
    CLAUDE.md: ein stiller Pandas-Aufloesungswechsel (ns/us/s) ist genau der Fehlertyp, der bei
    Zeitstempeln am meisten schadet."""
    df = df.sort_values("time").reset_index(drop=True)
    zeit_utc = (pd.to_datetime(df["time"]) + EST_OFFSET).dt.as_unit("s").dt.tz_localize("UTC")
    df["time_utc"] = zeit_utc
    df["ny_tag"] = zeit_utc.dt.tz_convert(NY).dt.date
    df["epoch"] = zeit_utc.astype("int64")
    return df


def schreibe_tage(symbol: str, df: pd.DataFrame) -> dict:
    bericht = {"symbol": symbol, "tage_geschrieben": 0, "kerzen": 0}
    for ny_tag, gruppe in df.groupby("ny_tag"):
        ordner = OUT_ROOT / f"{ny_tag.year:04d}" / f"{ny_tag.month:02d}" / ny_tag.strftime("%d.%m.%Y")
        ordner.mkdir(parents=True, exist_ok=True)
        ziel = ordner / f"{symbol} {ny_tag.isoformat()} 1m (bid).csv"
        for hinweis in pruefe_kerzen(
                ((r.epoch, r.open, r.high, r.low, r.close) for r in gruppe.itertuples()),
                symbol, ziel.name):
            print(f"  ? {hinweis}")
        with ziel.open("w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["time", "open", "high", "low", "close"])
            for row in gruppe.itertuples():
                w.writerow([row.epoch, row.open, row.high, row.low, row.close])
        bericht["tage_geschrieben"] += 1
        bericht["kerzen"] += len(gruppe)
    return bericht


def _demo() -> None:
    """Selbstcheck ohne Netz/Datei -- prueft die EST->UTC-Verschiebung und OHLC-Konsistenz."""
    df = pd.DataFrame({
        "time": pd.to_datetime(["2000-05-31 00:50:00", "2000-05-31 00:51:00"]),
        "open": [0.9315, 0.9315], "high": [0.9315, 0.9315],
        "low": [0.9315, 0.9315], "close": [0.9315, 0.9315], "vol": [0, 0],
    })
    out = konvertiere(df)
    # 2000-05-31 00:50 EST (UTC-5, ohne DST) == 05:50 UTC
    erwartet = pd.Timestamp("2000-05-31 05:50:00", tz="UTC")
    assert out["time_utc"].iloc[0] == erwartet, out["time_utc"].iloc[0]
    assert out["epoch"].iloc[1] - out["epoch"].iloc[0] == 60
    assert out["epoch"].iloc[0] == int(erwartet.timestamp())
    print("ingest_histdata_xlsx: Selbstcheck ok")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("zips", nargs="*", help="Pfad(e) zu HISTDATA_COM_XLSX_*.zip")
    ap.add_argument("--demo", action="store_true", help="Nur Selbstcheck, keine Datei noetig")
    a = ap.parse_args()

    if a.demo or not a.zips:
        _demo()
        return 0

    for zip_pfad_str in a.zips:
        zip_pfad = Path(zip_pfad_str)
        symbol, roh = lade_xlsx_aus_zip(zip_pfad)
        df = konvertiere(roh)
        b = schreibe_tage(symbol, df)
        zeitraum = f"{df['ny_tag'].min()} .. {df['ny_tag'].max()}"
        print(f"[{symbol}] {zip_pfad.name}: {b['tage_geschrieben']} Tage, "
              f"{b['kerzen']} Minutenkerzen, Zeitraum {zeitraum}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
