#!/usr/bin/env python3
"""Eigene Seasonal-Tendency-Datenbank aus den MNQ-Daten: Wochentag, Monat, Turn-of-Month,
Woche-im-Monat. Schreibt sowohl einen Report auf stdout als auch eine strukturierte
`algo/seasonal_tendency.json` -- die JSON ist die "Datenbank" (maschinell weiterverwendbar,
z.B. naechstes Jahr Jahr-1 gegen Jahr-2 vergleichen), der Report speist
wiki/synthesis/Seasonal Tendency (Eigene Daten, laufend).md.

Nutzt dieselben 1d-Baren wie backtest_daily_patterns.py (n=147, kein yfinance-Lookback-Limit).
Mit nur 7 Monaten Historie (Jan-Aug 2026, ein einziges Jahr) ist der Monatsvergleich KEIN
echter Mehrjahres-Seasonality-Test (dafuer braeuchte es mehrere Jahre desselben
Kalendermonats) -- Turn-of-Month und Woche-im-Monat sind dagegen testbar, weil sie auch
innerhalb eines Jahres mehrfach auftreten.

Aufruf:
    python algo/backtest_seasonal.py
"""
from __future__ import annotations

import json
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from analyze_ohlc import load  # noqa: E402
from backtest_daily_patterns import find_1d_days  # noqa: E402

MONTH_NAMES = ["", "Jan", "Feb", "Mrz", "Apr", "Mai", "Jun", "Jul", "Aug",
               "Sep", "Okt", "Nov", "Dez"]
WEEKDAY_NAMES = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
OUT_PATH = Path(__file__).resolve().parent / "seasonal_tendency.json"


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


def group_stats(rs: list[dict]) -> dict:
    return {
        "n": len(rs),
        "bullish_pct": round(100 * sum(r["bullish"] for r in rs) / len(rs), 1),
        "avg_return_pct": round(statistics.mean(r["ret_pct"] for r in rs), 3),
        "median_range": round(statistics.median(r["range"] for r in rs), 2),
        "avg_range": round(statistics.mean(r["range"] for r in rs), 2),
    }


def weekday_table(rows: list[dict]) -> dict:
    by_wd: dict[int, list[dict]] = {}
    for r in rows:
        by_wd.setdefault(r["day"].weekday(), []).append(r)
    return {WEEKDAY_NAMES[wd]: group_stats(rs) for wd, rs in sorted(by_wd.items())}


def month_table(rows: list[dict]) -> dict:
    months = sorted({(r["day"].year, r["day"].month) for r in rows})
    out = {}
    for y, m in months:
        rs = trading_days_of_month(rows, y, m)
        out[f"{y}-{m:02d}"] = group_stats(rs)
    return out


def turn_of_month(rows: list[dict]) -> dict:
    months = sorted({(r["day"].year, r["day"].month) for r in rows})
    tom, rest = [], []
    for i, (y, m) in enumerate(months):
        rs = trading_days_of_month(rows, y, m)
        if not rs:
            continue
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
    return {"window": group_stats(tom), "rest": group_stats(rest)}


def week_of_month_table(rows: list[dict]) -> dict:
    by_week: dict[int, list[dict]] = {}
    for r in rows:
        wk = min((r["day"].day - 1) // 7 + 1, 5)
        by_week.setdefault(wk, []).append(r)
    return {str(wk): group_stats(rs) for wk, rs in sorted(by_week.items())}


def main() -> None:
    rows = load_rows()
    print(f"{len(rows)} Handelstage ({rows[0]['day']} bis {rows[-1]['day']}).\n")

    weekday = weekday_table(rows)
    print("-- Wochentag --")
    for name, s in weekday.items():
        print(f"  {name}: n={s['n']:>3}  Bullish%={s['bullish_pct']:>5.1f}  "
              f"Median-Range={s['median_range']:>7.2f}")

    month = month_table(rows)
    print("\n-- Monat (Rohbefund, n=1 Jahr -- kein Mehrjahres-Seasonality-Test) --")
    for key, s in month.items():
        y, m = key.split("-")
        print(f"  {MONTH_NAMES[int(m)]} {y}: n={s['n']:>2}  Bullish%={s['bullish_pct']:>5.1f}  "
              f"Tagesrendite(Avg)={s['avg_return_pct']:>+.2f}%")

    tom = turn_of_month(rows)
    print("\n-- Turn-of-Month (letzter Handelstag + erste 3 des Folgemonats) --")
    print(f"  Fenster (n={tom['window']['n']}): Tagesrendite(Avg) "
          f"{tom['window']['avg_return_pct']:+.3f}%, Bullish% {tom['window']['bullish_pct']}, "
          f"Range(Avg) {tom['window']['avg_range']}")
    print(f"  Rest    (n={tom['rest']['n']}): Tagesrendite(Avg) "
          f"{tom['rest']['avg_return_pct']:+.3f}%, Bullish% {tom['rest']['bullish_pct']}, "
          f"Range(Avg) {tom['rest']['avg_range']}")

    week = week_of_month_table(rows)
    print("\n-- Woche-im-Monat (1=Tage 1-7, 2=8-14, 3=15-21, 4=22-28, 5=29-31) --")
    for wk, s in week.items():
        print(f"  Woche {wk}: n={s['n']:>3}  Bullish%={s['bullish_pct']:>5.1f}  "
              f"Median-Range={s['median_range']:>7.2f}")

    db = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "n_days": len(rows),
        "date_range": [rows[0]["day"].isoformat(), rows[-1]["day"].isoformat()],
        "weekday": weekday,
        "month": month,
        "turn_of_month": tom,
        "week_of_month": week,
    }
    OUT_PATH.write_text(json.dumps(db, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nDatenbank geschrieben: {OUT_PATH.relative_to(OUT_PATH.parent.parent)}")


if __name__ == "__main__":
    main()
