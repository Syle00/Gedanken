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
from backtest_seasonal import load_rows  # noqa: E402


def pearson(xs: list[float], ys: list[float]) -> float | None:
    n = len(xs)
    if n < 3:
        return None
    mx, my = statistics.mean(xs), statistics.mean(ys)
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sx = sum((x - mx) ** 2 for x in xs) ** 0.5
    sy = sum((y - my) ** 2 for y in ys) ** 0.5
    return cov / (sx * sy) if sx > 0 and sy > 0 else None


def main() -> None:
    rows = load_rows()
    gaps = []
    for i in range(1, len(rows)):
        prev_close, today_open = rows[i - 1]["close"], rows[i]["open"]
        gap = today_open - prev_close
        filled = rows[i]["low"] <= prev_close <= rows[i]["high"]
        gaps.append({"day": rows[i]["day"], "gap": gap, "filled": filled,
                      "range": rows[i]["range"], "day_ret": rows[i]["close"] - rows[i]["open"]})

    print(f"{len(gaps)} Handelstage mit NDOG-Daten.\n")

    abs_gaps = [abs(g["gap"]) for g in gaps]
    ranges = [g["range"] for g in gaps]
    corr = pearson(abs_gaps, ranges)
    print(f"1. Korrelation |NDOG-Gap| vs. Tagesrange: r={corr:.3f} (n={len(gaps)})")

    filled = sum(1 for g in gaps if g["filled"])
    print(f"\n2. NDOG-Fill-Quote (selber Tag): {filled}/{len(gaps)} = "
          f"{100 * filled / len(gaps):.1f}%")
    med_gap = statistics.median(abs_gaps)
    small = [g for g in gaps if abs(g["gap"]) <= med_gap]
    big = [g for g in gaps if abs(g["gap"]) > med_gap]
    for label, sub, op in (("Kleine Gaps", small, "<="), ("Grosse Gaps", big, ">")):
        f = sum(1 for g in sub if g["filled"])
        print(f"   {label} ({op} Median {med_gap:.1f} Pkt.): "
              f"{f}/{len(sub)} = {100 * f / len(sub):.1f}% (n={len(sub)})")

    same_dir = sum(1 for g in gaps if (g["gap"] > 0) == (g["day_ret"] > 0))
    print(f"\n3. Gap-Richtung = Tagesrichtung (Fortsetzung statt Fade): "
          f"{same_dir}/{len(gaps)} = {100 * same_dir / len(gaps):.1f}%")


if __name__ == "__main__":
    main()
