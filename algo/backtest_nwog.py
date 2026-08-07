#!/usr/bin/env python3
"""Backtest: NWOG (New Week Opening Gap) -- Gap zwischen Freitag-Close und Montag-Open,
Spezialfall von NDOG (siehe algo/backtest_ndog.py). Gleiche Machart, auf Wochenebene.

Wiki-Regel (wiki/concepts/New Week Opening Gap (NWOG) Bias.md): bleibt der Kurs die ganze
Woche auf einer Seite des NWOG, gilt der Wochen-Bias als intakt; wird es intraweek gekreuzt,
"kippt" der Bias. Ausserdem zwei Timing-Behauptungen: Weekly High/Low bildet sich meist
Montag, Donnerstag ist ein wahrscheinlicher Reversal-Kandidat.

Getestet an allen 1d-Baren (Wochen = Mo-Fr-Gruppen):
1. Korrelation |Gap| vs. Wochenrange.
2. Bias-intakt-Quote: NWOG wird intraweek NICHT wieder erreicht (Kehrseite von "gefuellt").
3. Gap-Richtung vs. Wochenrichtung (Montag-Open bis Freitag-Close) -- Fortsetzung oder Fade?
4. Wochentag des Wochen-Highs/-Lows -- direkter Test der beiden Timing-Behauptungen.

Aufruf:
    python algo/backtest_nwog.py
"""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from backtest_common import load_rows, pearson, write_result  # noqa: E402
from backtest_seasonal import WEEKDAY_NAMES  # noqa: E402


def group_weeks(rows: list[dict]) -> list[list[dict]]:
    weeks: list[list[dict]] = []
    for r in rows:
        if r["day"].weekday() == 0 or not weeks:
            weeks.append([r])
        else:
            weeks[-1].append(r)
    return weeks


def run() -> dict:
    rows = load_rows()
    weeks = group_weeks(rows)
    weeks = [w for w in weeks if w[0]["day"].weekday() == 0]

    nwogs = []
    for week in weeks:
        mon = week[0]
        idx = rows.index(mon)
        if idx == 0:
            continue
        prev_close = rows[idx - 1]["close"]
        gap = mon["open"] - prev_close
        week_high = max(r["high"] for r in week)
        week_low = min(r["low"] for r in week)
        week_range = week_high - week_low
        touched = any(r["low"] <= prev_close <= r["high"] for r in week)
        touched_after_monday = any(r["low"] <= prev_close <= r["high"] for r in week[1:])
        week_ret = week[-1]["close"] - mon["open"]
        high_day = next(r for r in week if r["high"] == week_high)["day"].weekday()
        low_day = next(r for r in week if r["low"] == week_low)["day"].weekday()
        nwogs.append({"week_start": mon["day"], "gap": gap, "range": week_range,
                      "touched": touched, "touched_after_monday": touched_after_monday,
                      "week_ret": week_ret, "high_day": high_day, "low_day": low_day})

    abs_gaps = [abs(n["gap"]) for n in nwogs]
    ranges = [n["range"] for n in nwogs]
    corr = pearson(abs_gaps, ranges)

    intact = sum(1 for n in nwogs if not n["touched"])
    intact_after_mon = sum(1 for n in nwogs if not n["touched_after_monday"])
    same_dir = sum(1 for n in nwogs if (n["gap"] > 0) == (n["week_ret"] > 0))
    high_days = Counter(n["high_day"] for n in nwogs)
    low_days = Counter(n["low_day"] for n in nwogs)

    return {
        "n_weeks": len(nwogs), "gap_range_corr": corr,
        "intact_pct": 100 * intact / len(nwogs), "intact_n": intact,
        "intact_after_monday_pct": 100 * intact_after_mon / len(nwogs),
        "intact_after_monday_n": intact_after_mon,
        "same_dir_pct": 100 * same_dir / len(nwogs), "same_dir_n": same_dir,
        "high_day_counts": {WEEKDAY_NAMES[wd]: high_days.get(wd, 0) for wd in range(5)},
        "low_day_counts": {WEEKDAY_NAMES[wd]: low_days.get(wd, 0) for wd in range(5)},
    }


def main() -> None:
    result = run()
    n = result["n_weeks"]
    print(f"{n} Wochen mit NWOG-Daten.\n")

    corr = result["gap_range_corr"]
    print(f"1. Korrelation |NWOG-Gap| vs. Wochenrange: r={corr:.3f} (n={n})")

    print(f"\n2. Bias-intakt-Quote (NWOG intraweek NICHT wieder erreicht, Mo-Fr): "
          f"{result['intact_n']}/{n} = {result['intact_pct']:.1f}%")
    print(f"   ... davon nur Montags eigene Kerze beruehrt, Di-Fr NICHT mehr: "
          f"{result['intact_after_monday_n']}/{n} = {result['intact_after_monday_pct']:.1f}% "
          f"(Bias haelt ab Dienstag)")

    print(f"\n3. Gap-Richtung = Wochenrichtung (Fortsetzung statt Fade): "
          f"{result['same_dir_n']}/{n} = {result['same_dir_pct']:.1f}%")

    print("\n4. Wochentag des Wochen-Highs / -Lows:")
    for wd in range(5):
        wd_name = WEEKDAY_NAMES[wd]
        h, low = result["high_day_counts"][wd_name], result["low_day_counts"][wd_name]
        print(f"   {wd_name}: High {h:>3} ({100 * h / n:.1f}%)   "
              f"Low {low:>3} ({100 * low / n:.1f}%)")

    write_result("backtest_nwog", result)


if __name__ == "__main__":
    main()
