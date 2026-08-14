#!/usr/bin/env python3
"""Verdichtet raw/marktdaten-tief/ (73.100 CSVs, histdata.com-Bulk-Import, siehe PLAN.md
2026-08-14) zu 10 Parquet-Dateien -- eine je Symbol. Grund: 92 Mio. Zeilen als CSV zu
parsen kostet Minuten pro Backtest-Lauf, Parquet Sekunden.

Idempotent und jederzeit aus raw/ neu baubar -- algo/cache/ ist gitignored (siehe
.gitignore-Kommentar), kein Datenverlust bei Loeschung.

Aufruf:
    python algo/build_parquet.py                 # alle 10 Symbole
    python algo/build_parquet.py EURUSD GBPUSD    # nur diese
    python algo/build_parquet.py --demo           # Selbstcheck ohne Netz/Dateien
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
TIEF_DIR = ROOT / "raw" / "marktdaten-tief"
CACHE = Path(__file__).resolve().parent / "cache"

SYMBOLE = ("EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD",
           "USDCAD", "NZDUSD", "EURJPY", "EURGBP", "GBPJPY")


def build(symbol: str, tief_dir: Path = TIEF_DIR, cache_dir: Path = CACHE) -> Path:
    dateien = sorted(tief_dir.glob(f"*/*/*/{symbol} *-*-* 1m (bid).csv"))
    if not dateien:
        raise FileNotFoundError(f"Keine histdata-Dateien fuer {symbol} unter {tief_dir}")

    frames = [pd.read_csv(p, usecols=["time", "open", "high", "low", "close"])
              for p in dateien]
    df = pd.concat(frames, ignore_index=True)
    df = df.sort_values("time").drop_duplicates(subset="time", keep="first")
    df["time"] = df["time"].astype("int64")
    for spalte in ("open", "high", "low", "close"):
        df[spalte] = df[spalte].astype("float64")

    cache_dir.mkdir(parents=True, exist_ok=True)
    ziel = cache_dir / f"{symbol}_1m.parquet"
    df.to_parquet(ziel, index=False)
    return ziel


def _demo() -> None:
    """Selbstcheck ohne echte histdata-Dateien -- baut zwei winzige CSVs in ein Tempdir."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        tief = Path(tmp) / "marktdaten-tief" / "2026" / "01" / "01.01.2026"
        tief.mkdir(parents=True)
        (tief / "TEST 2026-01-01 1m (bid).csv").write_text(
            "time,open,high,low,close\n"
            "1735689600,1.1,1.1,1.1,1.1\n"
            "1735689660,1.2,1.2,1.2,1.2\n"
            "1735689600,1.1,1.1,1.1,1.1\n",  # Duplikat -- muss verworfen werden
            encoding="utf-8",
        )
        cache = Path(tmp) / "cache"
        ziel = build("TEST", tief_dir=Path(tmp) / "marktdaten-tief", cache_dir=cache)
        df = pd.read_parquet(ziel)
        assert len(df) == 2, f"Duplikat nicht entfernt: {len(df)} Zeilen"
        assert list(df["time"]) == [1735689600, 1735689660], "nicht sortiert"
        assert df["open"].dtype == "float64" and df["time"].dtype == "int64"
    print("build_parquet: Selbstcheck ok")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("symbole", nargs="*", help="z.B. EURUSD GBPUSD (Default: alle 10)")
    ap.add_argument("--demo", action="store_true")
    a = ap.parse_args()

    if a.demo:
        _demo()
        return 0

    for sym in (a.symbole or SYMBOLE):
        ziel = build(sym)
        groesse_mb = ziel.stat().st_size / 1_000_000
        print(f"[{sym}] {ziel.name}: {groesse_mb:.1f} MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
