#!/usr/bin/env python3
"""Explorative Mustersuche: welche statistischen Regelmaessigkeiten stecken in den Daten,
die NICHT schon als benanntes ICT-Konzept im Wiki stehen? Reiner Blick auf die Zahlen ohne
vorab formulierte These -- Gegenstueck zu den anderen backtest_*.py-Skripten, die eine
konkrete Nutzerthese pruefen.

Getestet:
1. Wochentag-Effekt auf Tagesrange/Richtung (jenseits von TGIF, das nur Freitag beschreibt).
2. Zu welcher Tagesstunde faellt am haeufigsten das Tages-High/-Low (rein empirisch, nicht
   an ein benanntes Session-Fenster gebunden).
3. Range-Autokorrelation: folgt auf einen Tag mit grosser Range eher ein Tag mit kleiner
   oder wieder grosser Range (Volatility Clustering vs. Mean Reversion)?
4. Richtungs-Autokorrelation: sagt ein bullisher/bearisher Tag den naechsten Tag voraus
   (Momentum) oder eher das Gegenteil (Reversion)?
5. Rundzahl-Magnetismus: clustern Tages-High/-Low in der Naehe runder 50-Punkte-Marken?

Aufruf:
    python algo/explore_patterns.py
"""
from __future__ import annotations

import statistics
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from analyze_ohlc import load, at  # noqa: E402
from backtest_common import pearson  # noqa: E402
from backtest_org_ce import find_days  # noqa: E402

WEEKDAY_NAMES = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]


def day_stats(bars, day) -> dict | None:
    rth = [b for b in bars if at(day, 9, 30) <= b.t < at(day, 16, 0)]
    if not rth:
        return None
    hi_bar = max(rth, key=lambda b: b.h)
    lo_bar = min(rth, key=lambda b: b.l)
    return {
        "day": day, "weekday": day.weekday(), "open": rth[0].o, "close": rth[-1].c,
        "range": hi_bar.h - lo_bar.l, "bullish": rth[-1].c > rth[0].o,
        "high": hi_bar.h, "low": lo_bar.l,
        "high_hour": hi_bar.t.hour, "low_hour": lo_bar.t.hour,
    }


def main() -> None:
    rows = []
    for day, path in find_days():
        bars = load(path)
        s = day_stats(bars, day)
        if s:
            rows.append(s)
    rows.sort(key=lambda r: r["day"])
    assert all(rows[i]["day"] < rows[i + 1]["day"] for i in range(len(rows) - 1))  # Sanity: sortiert, keine Duplikate
    print(f"{len(rows)} Handelstage mit RTH-Daten (9:30-16:00 NY).\n")

    print("-- 1. Wochentag-Effekt --")
    by_wd: dict[int, list[dict]] = {}
    for r in rows:
        by_wd.setdefault(r["weekday"], []).append(r)
    for wd in sorted(by_wd):
        rs = by_wd[wd]
        med_range = statistics.median(r["range"] for r in rs)
        pct_bull = 100 * sum(r["bullish"] for r in rs) / len(rs)
        print(f"  {WEEKDAY_NAMES[wd]}: n={len(rs):>2}  Median-Range={med_range:>7.2f}  "
              f"Bullish%={pct_bull:>5.1f}")

    print("\n-- 2. Zu welcher Stunde faellt High/Low (RTH 9:30-16:00) --")
    high_hours = Counter(r["high_hour"] for r in rows)
    low_hours = Counter(r["low_hour"] for r in rows)
    for h in range(9, 16):
        print(f"  {h:02d}:00  High: {high_hours.get(h, 0):>3}  "
              f"({100 * high_hours.get(h, 0) / len(rows):.1f}%)   "
              f"Low: {low_hours.get(h, 0):>3}  ({100 * low_hours.get(h, 0) / len(rows):.1f}%)")

    print("\n-- 3. Range-Autokorrelation (Tag[i] vs. Tag[i-1]) --")
    ranges = [r["range"] for r in rows]
    r_corr = pearson(ranges[:-1], ranges[1:])
    print(f"  Pearson r = {r_corr:.3f}" if r_corr is not None else "  nicht genug Tage")

    print("\n-- 4. Richtungs-Autokorrelation --")
    pairs = list(zip(rows[:-1], rows[1:]))
    after_bull = [p[1]["bullish"] for p in pairs if p[0]["bullish"]]
    after_bear = [p[1]["bullish"] for p in pairs if not p[0]["bullish"]]
    if after_bull:
        print(f"  Nach bullishem Tag: {100 * sum(after_bull) / len(after_bull):.1f}% "
              f"bullish am naechsten Tag (n={len(after_bull)})")
    if after_bear:
        print(f"  Nach bearishem Tag: {100 * sum(after_bear) / len(after_bear):.1f}% "
              f"bullish am naechsten Tag (n={len(after_bear)})")

    print("\n-- 5. Rundzahl-Magnetismus (Abstand High/Low zur naechsten 50er-Marke) --")
    dists = []
    for r in rows:
        for level in (r["high"], r["low"]):
            m = level % 50
            dists.append(min(m, 50 - m))
    print(f"  Durchschnittsabstand zur naechsten 50er-Marke: {statistics.mean(dists):.2f} Punkte "
          f"(Erwartung bei Gleichverteilung: 12,5 Punkte)")


if __name__ == "__main__":
    main()
