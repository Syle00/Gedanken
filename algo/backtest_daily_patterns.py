#!/usr/bin/env python3
"""Grossflaechige Version von explore_patterns.py: dieselben vier Fragen (Wochentag-Effekt,
Range-/Richtungs-Autokorrelation, Rundzahl-Magnetismus), aber auf allen verfuegbaren 1d-Baren
(volle Globex-Session, kein RTH-Ausschnitt) statt nur den ~34 Tagen mit 1m/5m-Aufloesung --
1d hat bei yfinance kein 30/60-Tage-Limit, deshalb reicht die Stichprobe hier bis Jan. 2026
zurueck (n~150 statt ~34). Nur "Stunde des Extrems" braucht Intraday-Aufloesung und bleibt
explore_patterns.py vorbehalten.

Aufruf:
    python algo/backtest_daily_patterns.py
"""
from __future__ import annotations

import statistics
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from analyze_ohlc import load  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "raw" / "marktdaten"
WEEKDAY_NAMES = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]


def find_1d_days(symbol: str = "MNQ") -> list[tuple]:
    out = []
    for day_dir in sorted(DATA_DIR.glob("*/*/*")):
        if not day_dir.is_dir():
            continue
        try:
            day = datetime.strptime(day_dir.name, "%d.%m.%Y").date()
        except ValueError:
            continue
        files = sorted(day_dir.glob(f"{symbol} * 1d.csv"))
        if files:
            out.append((day, files[0]))
    return sorted(out)


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
    rows = []
    for day, path in find_1d_days():
        bars = load(path)
        if not bars:
            continue
        b = bars[-1]
        if b.h <= b.l:
            continue
        rows.append({"day": day, "weekday": day.weekday(), "open": b.o, "close": b.c,
                      "high": b.h, "low": b.l, "range": b.h - b.l, "bullish": b.c > b.o})
    rows.sort(key=lambda r: r["day"])
    assert all(rows[i]["day"] < rows[i + 1]["day"] for i in range(len(rows) - 1))
    print(f"{len(rows)} Handelstage mit 1d-Daten ({rows[0]['day']} bis {rows[-1]['day']}).\n")

    print("-- 1. Wochentag-Effekt (volle Globex-Session) --")
    by_wd: dict[int, list[dict]] = {}
    for r in rows:
        by_wd.setdefault(r["weekday"], []).append(r)
    for wd in sorted(by_wd):
        rs = by_wd[wd]
        med_range = statistics.median(r["range"] for r in rs)
        pct_bull = 100 * sum(r["bullish"] for r in rs) / len(rs)
        print(f"  {WEEKDAY_NAMES[wd]}: n={len(rs):>3}  Median-Range={med_range:>7.2f}  "
              f"Bullish%={pct_bull:>5.1f}")

    print("\n-- 2. Range-Autokorrelation (Tag[i] vs. Tag[i-1]) --")
    ranges = [r["range"] for r in rows]
    r_corr = pearson(ranges[:-1], ranges[1:])
    print(f"  Pearson r = {r_corr:.3f}  (n={len(ranges) - 1})" if r_corr is not None else "  n/a")

    print("\n-- 3. Richtungs-Autokorrelation --")
    pairs = list(zip(rows[:-1], rows[1:]))
    after_bull = [p[1]["bullish"] for p in pairs if p[0]["bullish"]]
    after_bear = [p[1]["bullish"] for p in pairs if not p[0]["bullish"]]
    print(f"  Nach bullishem Tag: {100 * sum(after_bull) / len(after_bull):.1f}% bullish "
          f"am naechsten Tag (n={len(after_bull)})")
    print(f"  Nach bearishem Tag: {100 * sum(after_bear) / len(after_bear):.1f}% bullish "
          f"am naechsten Tag (n={len(after_bear)})")

    print("\n-- 4. Rundzahl-Magnetismus (Abstand High/Low zur naechsten 50er-Marke) --")
    dists = []
    for r in rows:
        for level in (r["high"], r["low"]):
            m = level % 50
            dists.append(min(m, 50 - m))
    print(f"  Durchschnittsabstand: {statistics.mean(dists):.2f} Punkte "
          f"(Erwartung bei Gleichverteilung: 12,5 Punkte, n={len(dists)})")


if __name__ == "__main__":
    main()
