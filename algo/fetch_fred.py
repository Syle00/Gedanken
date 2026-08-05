#!/usr/bin/env python3
"""Laedt Wirtschaftsdaten von FRED (stlouisfed.org) und legt sie in raw/marktdaten/fred/
als <series_id>.csv (date,value) ab. Ein Fetch ueberschreibt die Datei komplett -- anders
als bei den OHLC-Tagesdateien ist das hier richtig, weil FRED Reihen rueckwirkend revidiert
(z.B. CPI). Fehlende Werte liefert FRED als "." und werden als leerer value uebernommen,
nicht stillschweigend weggelassen (sonst verschieben sich Datumszeilen).

API-Key liegt in algo/.secrets.yaml (gitignored, nie committen).

Aufruf:
    python algo/fetch_fred.py                  # Starter-Set (siehe DEFAULT_SERIES)
    python algo/fetch_fred.py DGS10 UNRATE      # bestimmte Serien
"""

from __future__ import annotations

import sys
from pathlib import Path

import requests
import yaml

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "raw" / "marktdaten" / "fred"
SECRETS_FILE = Path(__file__).resolve().parent / ".secrets.yaml"

# Makro-Starter-Set mit Bezug zu Nasdaq-Futures (MNQ): Zinsen, Inflation, Arbeitsmarkt,
# Volatilitaet, Fed-Bilanz (Liquiditaet). Weitere Serien einfach per Argument nachladen.
DEFAULT_SERIES = ["DFF", "CPIAUCSL", "UNRATE", "VIXCLS", "DGS10", "WALCL"]


def fetch_series(series_id: str, api_key: str) -> list[dict]:
    r = requests.get(
        "https://api.stlouisfed.org/fred/series/observations",
        params={"series_id": series_id, "api_key": api_key, "file_type": "json"},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["observations"]


def write_series(series_id: str, observations: list[dict]) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    dest = OUT_DIR / f"{series_id}.csv"
    with dest.open("w", encoding="utf-8") as f:
        f.write("date,value\n")
        for obs in observations:
            value = "" if obs["value"] == "." else obs["value"]
            f.write(f"{obs['date']},{value}\n")
    return dest


def main(argv=None) -> int:
    series_ids = (argv if argv is not None else sys.argv[1:]) or DEFAULT_SERIES
    api_key = yaml.safe_load(SECRETS_FILE.read_text(encoding="utf-8"))["fred_api_key"]

    for series_id in series_ids:
        obs = fetch_series(series_id, api_key)
        dest = write_series(series_id, obs)
        print(f"  {series_id}: {len(obs)} Beobachtungen -> {dest.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
