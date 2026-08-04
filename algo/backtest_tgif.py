#!/usr/bin/env python3
"""Backtest: TGIF (Thank God it's Friday) -- retraced der Preis am Freitag 20-30% in die
laufende Weekly Range zurueck? Siehe wiki/concepts/TGIF (Thank God its Friday).md.

Operationalisierung (die Quelle nennt keine exakte Berechnungsvorschrift, nur "Fib ueber die
Woche, Close zwischen 20% und 30%"): Wochenrichtung wird ueber Montag-Open vs. Close des
vorletzten Handelstags bestimmt (statt hart "Donnerstag", damit auch feiertagsverkuerzte
Wochen zaehlen). Bei bullisher Wochenrichtung wird erwartet, dass der Freitag-Close
20-30% der Wochenrange UNTER dem Wochen-High liegt (Retracement von oben); bei bearisher
Richtung 20-30% UEBER dem Wochen-Low (Retracement von unten).

Getestet an allen 1d-Baren, Wochen = Mo-Fr-Gruppen (siehe backtest_nwog.py):
1. Trefferquote: Freitag-Retracement landet im 20-30%-Fenster.
2. Verteilung/Median des tatsaechlichen Retracements, falls die Quote niedrig ist -- wo landet
   es tatsaechlich?

Aufruf:
    python algo/backtest_tgif.py
"""
from __future__ import annotations

import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from backtest_seasonal import load_rows  # noqa: E402
from backtest_nwog import group_weeks  # noqa: E402


def main() -> None:
    rows = load_rows()
    weeks_raw = group_weeks(rows)
    weeks = [w for w in weeks_raw if w[0]["day"].weekday() == 0 and len(w) >= 3]

    results = []
    for w in weeks:
        week_open = w[0]["open"]
        pre_last_close = w[-2]["close"]
        last = w[-1]
        week_high = max(r["high"] for r in w)
        week_low = min(r["low"] for r in w)
        rng = week_high - week_low
        if rng <= 0:
            continue
        bullish = pre_last_close > week_open
        if bullish:
            retrace_pct = 100 * (week_high - last["close"]) / rng
        else:
            retrace_pct = 100 * (last["close"] - week_low) / rng
        results.append({"week_start": w[0]["day"], "bullish": bullish,
                         "retrace_pct": retrace_pct, "in_zone": 20 <= retrace_pct <= 30})

    print(f"{len(results)} Wochen mit TGIF-Daten.\n")

    hits = sum(1 for r in results if r["in_zone"])
    print(f"1. Freitag-Close im 20-30%-Retracement-Fenster: {hits}/{len(results)} = "
          f"{100 * hits / len(results):.1f}%")

    retraces = [r["retrace_pct"] for r in results]
    print(f"\n2. Verteilung des tatsaechlichen Retracements (Median "
          f"{statistics.median(retraces):.1f}%, Mittelwert {statistics.mean(retraces):.1f}%):")
    buckets = [10, 20, 30, 40, 50, 70, 100]
    prev = 0
    for b in buckets:
        c = sum(1 for r in retraces if prev <= r < b)
        print(f"   {prev:>3}-{b:<3}%: {c:>3}  ({100 * c / len(retraces):.1f}%)")
        prev = b

    print(f"\n   Wochen bullish (Montag->vorletzter Tag): "
          f"{sum(1 for r in results if r['bullish'])}/{len(results)}")

    wide = sum(1 for r in retraces if 15 <= r <= 35)
    print(f"\n3. Grosszuegigeres Fenster (15-35%, statt exakt 20-30%): "
          f"{wide}/{len(retraces)} = {100 * wide / len(retraces):.1f}%")


if __name__ == "__main__":
    main()
