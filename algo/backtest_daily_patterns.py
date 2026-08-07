from __future__ import annotations

import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from backtest_common import find_1d_days, pearson, write_result  # noqa: E402
from analyze_ohlc import load  # noqa: E402

WEEKDAY_NAMES = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]


def run() -> dict:
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

    by_wd: dict[int, list[dict]] = {}
    for r in rows:
        by_wd.setdefault(r["weekday"], []).append(r)
    weekday = {WEEKDAY_NAMES[wd]: {
        "n": len(rs), "median_range": round(statistics.median(r["range"] for r in rs), 2),
        "bullish_pct": round(100 * sum(r["bullish"] for r in rs) / len(rs), 1),
    } for wd, rs in sorted(by_wd.items())}

    ranges = [r["range"] for r in rows]
    range_autocorr = pearson(ranges[:-1], ranges[1:])

    pairs = list(zip(rows[:-1], rows[1:]))
    after_bull = [p[1]["bullish"] for p in pairs if p[0]["bullish"]]
    after_bear = [p[1]["bullish"] for p in pairs if not p[0]["bullish"]]

    dists = []
    for r in rows:
        for level in (r["high"], r["low"]):
            m = level % 50
            dists.append(min(m, 50 - m))

    return {
        "n_days": len(rows), "date_range": [rows[0]["day"], rows[-1]["day"]],
        "weekday": weekday, "range_autocorr": range_autocorr, "range_autocorr_n": len(ranges) - 1,
        "after_bull_pct": 100 * sum(after_bull) / len(after_bull), "after_bull_n": len(after_bull),
        "after_bear_pct": 100 * sum(after_bear) / len(after_bear), "after_bear_n": len(after_bear),
        "round_number_avg_dist": statistics.mean(dists), "round_number_n": len(dists),
    }


def main() -> None:
    result = run()
    print(f"{result['n_days']} Handelstage mit 1d-Daten ({result['date_range'][0]} bis "
          f"{result['date_range'][1]}).\n")

    print("-- 1. Wochentag-Effekt (volle Globex-Session) --")
    for name, s in result["weekday"].items():
        print(f"  {name}: n={s['n']:>3}  Median-Range={s['median_range']:>7.2f}  "
              f"Bullish%={s['bullish_pct']:>5.1f}")

    print("\n-- 2. Range-Autokorrelation (Tag[i] vs. Tag[i-1]) --")
    r_corr = result["range_autocorr"]
    print(f"  Pearson r = {r_corr:.3f}  (n={result['range_autocorr_n']})"
          if r_corr is not None else "  n/a")

    print("\n-- 3. Richtungs-Autokorrelation --")
    print(f"  Nach bullishem Tag: {result['after_bull_pct']:.1f}% bullish "
          f"am naechsten Tag (n={result['after_bull_n']})")
    print(f"  Nach bearishem Tag: {result['after_bear_pct']:.1f}% bullish "
          f"am naechsten Tag (n={result['after_bear_n']})")

    print("\n-- 4. Rundzahl-Magnetismus (Abstand High/Low zur naechsten 50er-Marke) --")
    print(f"  Durchschnittsabstand: {result['round_number_avg_dist']:.2f} Punkte "
          f"(Erwartung bei Gleichverteilung: 12,5 Punkte, n={result['round_number_n']})")

    write_result("backtest_daily_patterns", result)


if __name__ == "__main__":
    main()
