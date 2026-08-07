#!/usr/bin/env python3
"""Backtest: NDOG (New Day Opening Gap) -- Gap zwischen Vortages-Close und Tages-Open.

Nutzer-Vorgabe (siehe Merkzettel): NDOG/NWOG sind relevante PD Arrays, Opening-/Closing-Preise
sollen dafuer immer mitgefuehrt werden. Bislang gab es dafuer noch keinen Detektor (Backlog in
algo/PLAN.md).

Rechnet direkt auf den 1d-Baren (wie backtest_seasonal.py/backtest_daily_patterns.py) statt
ueber ndog_gap() in tools/analyze_ohlc.py: die 1d-CSVs haben pro Datei nur eine Kerze mit
Open-Zeit 18:00 des VORABENDS (Globex-Konvention, siehe trading_day() in fetch_yfinance.py) --
`bar.t.date()` zeigt deshalb auf den Vortag, nicht den eigentlichen Handelstag. ndog_gap() ist
fuer echte Intraday-Mehrkerzen-Tage gebaut (z.B. live_status.py) und dort weiterhin richtig;
fuer die 1d-Einzelkerze pro Datei ist die direkte Positions-Logik (wie in find_1d_days()) die
korrekte, nicht die datumsbasierte.

Getestet an allen 1d-Baren (n=146, volle Globex-Session, kein yfinance-Lookback-Limit):
1. Korrelation |Gap| vs. Tagesrange -- setzt ein grosses NDOG den Ton fuer einen grossen Tag?
2. Fill-Quote (Preis erreicht den Vortages-Close noch am selben Tag) insgesamt und nach
   Gap-Groesse gestaffelt -- Gegenprobe zur bereits dokumentierten ORG-Regel "Gap-Groesse
   entscheidet ueber den Fill" (wiki/concepts/ORG.../1st Presented FVG.md), hier fuer NDOG.
3. Gap-Richtung vs. Tagesrichtung -- setzt sich die Gap-Richtung fort (Momentum) oder wird sie
   eher gefadet (Reversion)?

Aufruf:
    python algo/backtest_ndog.py
"""
from __future__ import annotations

import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from backtest_common import load_rows, pearson, write_result  # noqa: E402


def run() -> dict:
    rows = load_rows()
    gaps = []
    for i in range(1, len(rows)):
        prev_close, today_open = rows[i - 1]["close"], rows[i]["open"]
        gap = today_open - prev_close
        filled = rows[i]["low"] <= prev_close <= rows[i]["high"]
        gaps.append({"day": rows[i]["day"], "gap": gap, "filled": filled,
                      "range": rows[i]["range"], "day_ret": rows[i]["close"] - rows[i]["open"]})

    abs_gaps = [abs(g["gap"]) for g in gaps]
    ranges = [g["range"] for g in gaps]
    corr = pearson(abs_gaps, ranges)

    filled = sum(1 for g in gaps if g["filled"])
    med_gap = statistics.median(abs_gaps)
    small = [g for g in gaps if abs(g["gap"]) <= med_gap]
    big = [g for g in gaps if abs(g["gap"]) > med_gap]
    same_dir = sum(1 for g in gaps if (g["gap"] > 0) == (g["day_ret"] > 0))

    return {
        "n_days": len(gaps), "gap_range_corr": corr, "fill_pct": 100 * filled / len(gaps),
        "fill_n": filled, "median_abs_gap": med_gap,
        "small_gap_fill_pct": 100 * sum(1 for g in small if g["filled"]) / len(small),
        "small_gap_n": len(small),
        "big_gap_fill_pct": 100 * sum(1 for g in big if g["filled"]) / len(big),
        "big_gap_n": len(big),
        "same_dir_pct": 100 * same_dir / len(gaps), "same_dir_n": same_dir,
    }


def main() -> None:
    result = run()
    n = result["n_days"]
    print(f"{n} Handelstage mit NDOG-Daten.\n")

    print(f"1. Korrelation |NDOG-Gap| vs. Tagesrange: r={result['gap_range_corr']:.3f} (n={n})")

    print(f"\n2. NDOG-Fill-Quote (selber Tag): {result['fill_n']}/{n} = {result['fill_pct']:.1f}%")
    small_count = int(result['small_gap_n'] * result['small_gap_fill_pct'] / 100)
    big_count = int(result['big_gap_n'] * result['big_gap_fill_pct'] / 100)
    print(f"   Kleine Gaps (<= Median {result['median_abs_gap']:.1f} Pkt.): "
          f"{small_count}/{result['small_gap_n']} = {result['small_gap_fill_pct']:.1f}% (n={result['small_gap_n']})")
    print(f"   Grosse Gaps (> Median {result['median_abs_gap']:.1f} Pkt.): "
          f"{big_count}/{result['big_gap_n']} = {result['big_gap_fill_pct']:.1f}% (n={result['big_gap_n']})")

    print(f"\n3. Gap-Richtung = Tagesrichtung (Fortsetzung statt Fade): "
          f"{result['same_dir_n']}/{n} = {result['same_dir_pct']:.1f}%")

    write_result("backtest_ndog", result)


if __name__ == "__main__":
    main()
