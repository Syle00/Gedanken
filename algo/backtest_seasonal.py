#!/usr/bin/env python3
"""Saisonale Muster auf Wochen-/Monatsebene, plus Turn-of-Month-Effekt (extern gut belegt,
siehe wiki-Seite fuer Quellen) gegen die eigenen MNQ-Daten getestet.

Nutzt dieselben 1d-Baren wie backtest_daily_patterns.py (n=147, kein yfinance-Lookback-Limit).
Mit nur 7 Monaten Historie (Jan-Aug 2026, ein einziges Jahr) ist das KEIN echter
Jahres-Seasonality-Test (dafuer braeuchte es mehrere Jahre desselben Kalendermonats) --
stattdessen: (1) Turn-of-Month, ein Tage-seit-Monatsgrenze-Effekt, der auch innerhalb eines
Jahres mehrfach auftritt und deshalb mit dieser Stichprobe testbar ist; (2) Woche-im-Monat;
(3) die eigenen Monatszahlen als Rohbefund, mit dem sich naechstes Jahr echte Jahres-
Seasonality bilden laesst.

Aufruf:
    python algo/backtest_seasonal.py
"""
from __future__ import annotations

import calendar
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from analyze_ohlc import load  # noqa: E402
from backtest_daily_patterns import find_1d_days  # noqa: E402

MONTH_NAMES = ["", "Jan", "Feb", "Mrz", "Apr", "Mai", "Jun", "Jul", "Aug",
               "Sep", "Okt", "Nov", "Dez"]


def load_rows() -> list[dict]:
    rows = []
    for day, path in find_1d_days():
        bars = load(path)
        if not bars:
            continue
        b = bars[-1]
        if b.h <= b.l:
            continue
        rows.append({"day": day, "open": b.o, "close": b.c, "high": b.h, "low": b.l,
                      "range": b.h - b.l, "ret_pct": 100 * (b.c - b.o) / b.o,
                      "bullish": b.c > b.o})
    rows.sort(key=lambda r: r["day"])
    return rows


def trading_days_of_month(rows: list[dict], year: int, month: int) -> list[dict]:
    return [r for r in rows if r["day"].year == year and r["day"].month == month]


def main() -> None:
    rows = load_rows()
    print(f"{len(rows)} Handelstage ({rows[0]['day']} bis {rows[-1]['day']}).\n")

    print("-- 1. Monatszahlen (Rohbefund, n=1 Jahr -- kein Mehrjahres-Seasonality-Test) --")
    months = sorted({(r["day"].year, r["day"].month) for r in rows})
    for y, m in months:
        rs = trading_days_of_month(rows, y, m)
        pct_bull = 100 * sum(r["bullish"] for r in rs) / len(rs)
        avg_ret = statistics.mean(r["ret_pct"] for r in rs)
        print(f"  {MONTH_NAMES[m]} {y}: n={len(rs):>2}  Bullish%={pct_bull:>5.1f}  "
              f"Tagesrendite(Avg)={avg_ret:>+.2f}%")

    print("\n-- 2. Turn-of-Month-Effekt (letzter Handelstag + erste 3 des Folgemonats) --")
    tom, rest = [], []
    for i, y_m in enumerate(months):
        y, m = y_m
        rs = trading_days_of_month(rows, y, m)
        if not rs:
            continue
        # letzter Handelstag dieses Monats zaehlt zum TOM-Fenster des NAECHSTEN Monats
        rest_of_month = rs[:-1]
        tom.append(rs[-1])
        if i + 1 < len(months):
            ny, nm = months[i + 1]
            nrs = trading_days_of_month(rows, ny, nm)
            tom.extend(nrs[:3])
            rest_of_month.extend(nrs[3:])
        rest.extend(rest_of_month)
    tom_days = {r["day"] for r in tom}
    rest = [r for r in rest if r["day"] not in tom_days]  # keine Doppelzaehlung an Monatsuebergaengen

    print(f"  TOM-Fenster (n={len(tom)}): Tagesrendite(Avg) {statistics.mean(r['ret_pct'] for r in tom):+.3f}%, "
          f"Bullish% {100 * sum(r['bullish'] for r in tom) / len(tom):.1f}, "
          f"Range(Avg) {statistics.mean(r['range'] for r in tom):.1f}")
    print(f"  Rest-Monat  (n={len(rest)}): Tagesrendite(Avg) {statistics.mean(r['ret_pct'] for r in rest):+.3f}%, "
          f"Bullish% {100 * sum(r['bullish'] for r in rest) / len(rest):.1f}, "
          f"Range(Avg) {statistics.mean(r['range'] for r in rest):.1f}")

    print("\n-- 3. Woche-im-Monat (1=Tage 1-7, 2=8-14, 3=15-21, 4=22-28, 5=29-31) --")
    by_week: dict[int, list[dict]] = {}
    for r in rows:
        wk = min((r["day"].day - 1) // 7 + 1, 5)
        by_week.setdefault(wk, []).append(r)
    for wk in sorted(by_week):
        rs = by_week[wk]
        pct_bull = 100 * sum(r["bullish"] for r in rs) / len(rs)
        med_range = statistics.median(r["range"] for r in rs)
        print(f"  Woche {wk}: n={len(rs):>3}  Bullish%={pct_bull:>5.1f}  Median-Range={med_range:>7.2f}")


if __name__ == "__main__":
    main()
