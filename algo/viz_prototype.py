#!/usr/bin/env python3
"""Prototyp: pandas als Backtest-/Auswertungsschicht ueber raw/marktdaten/.

Beantwortet die Frage "kann pandas das?" praktisch statt theoretisch: laedt
einen Tag aus raw/marktdaten/, macht die Zeitzonen-/Resampling-Arbeit, die in
tools/analyze_ohlc.py noch von Hand in Schleifen passiert, in wenigen
DataFrame-Zeilen, und exportiert das Ergebnis als JSON fuer den Chart in
algo/viz_prototype.html.

Nur fuer diesen Ordner gedacht -- tools/analyze_ohlc.py bleibt bewusst
Standardbibliothek (siehe dessen Docstring). Abhaengigkeiten: algo/requirements.txt.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

DATA = (Path(__file__).resolve().parent.parent
        / "raw" / "marktdaten" / "2026" / "08" / "03.08.2026" / "MNQ 2026-08-03 5m.csv")
OUT = Path(__file__).resolve().parent / "viz_prototype_data.json"


def load(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["time"] = pd.to_datetime(df["time"], unit="s", utc=True).dt.tz_convert("America/New_York")
    return df.set_index("time").sort_index()


def main() -> None:
    df = load(DATA)
    day = df.loc["2026-08-03 00:00":"2026-08-03 16:15"]

    # Das ist der Punkt, an dem pandas gegenueber der Stdlib-Schleife gewinnt:
    # Resampling auf ein beliebiges Fenster ist eine Zeile statt eines Detektors.
    macro_window = day.loc["2026-08-03 09:50":"2026-08-03 10:10"]
    macro_range = float(macro_window["high"].max() - macro_window["low"].min())

    series = [{"t": ts.strftime("%H:%M"), "c": float(c)} for ts, c in day["close"].items()]

    events = [
        {"t": "09:30", "label": "Sweep sellside @ 28 382,75\n(Level seit 08:05, Tages-Low)",
         "y": float(day.loc["2026-08-03 09:30", "low"]), "kind": "sweep"},
        {"t": "09:35", "label": "Displacement +166,25 Pkt\n(5,5x Median)",
         "y": float(day.loc["2026-08-03 09:35", "close"]), "kind": "displacement"},
        {"t": "14:10", "label": "Tages-High 28 965,00",
         "y": float(day["high"].max()), "kind": "high"},
    ]
    band = {"start": "09:50", "end": "10:10",
            "label": f"Macro-Expansion ({macro_range:.2f} Pkt)"}

    OUT.write_text(json.dumps({"series": series, "events": events, "band": band},
                               ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(series)} Kerzen exportiert -> {OUT}")
    print(f"Macro-Fenster 09:50-10:10: {macro_range:.2f} Pkt Range (pandas: 2 Zeilen statt Detektor)")


if __name__ == "__main__":
    main()
