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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from backtest_common import load_rows  # noqa: E402

MONTH_NAMES = ["", "Jan", "Feb", "Mrz", "Apr", "Mai", "Jun", "Jul", "Aug",
               "Sep", "Okt", "Nov", "Dez"]
WEEKDAY_NAMES = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
OUT_PATH = Path(__file__).resolve().parent / "seasonal_tendency.json"


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
    tom = []
    for i, (y, m) in enumerate(months):
        rs = trading_days_of_month(rows, y, m)
        if not rs:
            continue
        tom.append(rs[-1])
        if i + 1 < len(months):
            ny, nm = months[i + 1]
            nrs = trading_days_of_month(rows, ny, nm)
            tom.extend(nrs[:3])
    # Bugfix 2026-08-07 (siehe algo/PLAN.md-Log): rest = alles ausserhalb des TOM-Fensters,
    # direkt aus rows berechnet statt inkrementell akkumuliert -- die alte rest_of_month-
    # Akkumulation zaehlte Tage 4..n-1 jedes Monats doppelt (rs[:-1] der eigenen Iteration
    # UND nrs[3:] der Vor-Iteration ueberschnitten sich), der tom_days-Filter danach entfernte
    # nur die TOM/rest-Ueberschneidung, nicht die rest/rest-Selbstdopplung.
    tom_days = {r["day"] for r in tom}
    rest = [r for r in rows if r["day"] not in tom_days]
    return {"window": group_stats(tom), "rest": group_stats(rest)}


def week_of_month_table(rows: list[dict]) -> dict:
    by_week: dict[int, list[dict]] = {}
    for r in rows:
        wk = min((r["day"].day - 1) // 7 + 1, 5)
        by_week.setdefault(wk, []).append(r)
    return {str(wk): group_stats(rs) for wk, rs in sorted(by_week.items())}


def run(symbol: str = "MNQ") -> dict:
    rows = load_rows(symbol)
    return {
        "symbol": symbol, "n_days": len(rows), "date_range": [rows[0]["day"], rows[-1]["day"]],
        "weekday": weekday_table(rows), "month": month_table(rows),
        "turn_of_month": turn_of_month(rows), "week_of_month": week_of_month_table(rows),
    }


def out_path(symbol: str) -> Path:
    """MNQ behaelt den bestehenden Namen (Protokollartefakt, siehe CLAUDE.md) -- jedes
    andere Symbol bekommt einen eigenen, damit ein Forex-Lauf die MNQ-Datenbank nicht
    ueberschreibt."""
    if symbol == "MNQ":
        return OUT_PATH
    return OUT_PATH.parent / f"seasonal_tendency_{symbol}.json"


def main(symbol: str = "MNQ") -> None:
    result = run(symbol)
    rng = result["date_range"]
    print(f"{result['n_days']} Handelstage ({rng[0]} bis {rng[1]}).\n")

    print("-- Wochentag --")
    for name, s in result["weekday"].items():
        print(f"  {name}: n={s['n']:>3}  Bullish%={s['bullish_pct']:>5.1f}  "
              f"Median-Range={s['median_range']:>7.2f}")

    jahre = rng[1].year - rng[0].year + 1
    if jahre <= 1:
        print("\n-- Monat (Rohbefund, n=1 Jahr -- kein Mehrjahres-Seasonality-Test) --")
    else:
        print(f"\n-- Monat (echter Mehrjahres-Befund, n={jahre} Jahre) --")
    for key, s in result["month"].items():
        y, m = key.split("-")
        print(f"  {MONTH_NAMES[int(m)]} {y}: n={s['n']:>2}  Bullish%={s['bullish_pct']:>5.1f}  "
              f"Tagesrendite(Avg)={s['avg_return_pct']:>+.2f}%")

    tom = result["turn_of_month"]
    print("\n-- Turn-of-Month (letzter Handelstag + erste 3 des Folgemonats) --")
    print(f"  Fenster (n={tom['window']['n']}): Tagesrendite(Avg) "
          f"{tom['window']['avg_return_pct']:+.3f}%, Bullish% {tom['window']['bullish_pct']}, "
          f"Range(Avg) {tom['window']['avg_range']}")
    print(f"  Rest    (n={tom['rest']['n']}): Tagesrendite(Avg) "
          f"{tom['rest']['avg_return_pct']:+.3f}%, Bullish% {tom['rest']['bullish_pct']}, "
          f"Range(Avg) {tom['rest']['avg_range']}")

    print("\n-- Woche-im-Monat (1=Tage 1-7, 2=8-14, 3=15-21, 4=22-28, 5=29-31) --")
    for wk, s in result["week_of_month"].items():
        print(f"  Woche {wk}: n={s['n']:>3}  Bullish%={s['bullish_pct']:>5.1f}  "
              f"Median-Range={s['median_range']:>7.2f}")

    db = {"generated_at": datetime.now(timezone.utc).isoformat(), **result}
    ziel = out_path(symbol)
    ziel.write_text(json.dumps(db, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"\nDatenbank geschrieben: {ziel.relative_to(ziel.parent.parent)}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "MNQ")
