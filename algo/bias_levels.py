#!/usr/bin/env python3
"""Wochen-/Tages-Range-Kennzahlen fuer die Bias-Vorlage (raw/journal/Daily Bias */Weekly
Bias *). Reuse: load_rows() aus backtest_common.py (Open/High/Low/Close pro Handelstag) --
kein eigenes CSV-Parsing.

Aufruf:
    python algo/bias_levels.py                  # Levels fuer heute (Daily-Modus)
    python algo/bias_levels.py 2026-08-14        # Levels fuer diesen Handelstag
    python algo/bias_levels.py 2026-08-14 --weekly  # nur Wochen-Range, keine Vortages-Range
    python algo/bias_levels.py --demo            # reiner Funktions-Selbstcheck
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from backtest_common import load_rows  # noqa: E402


def week_range(rows: list[dict], target_day: date) -> dict | None:
    """High/Low aller Handelstage in der ISO-Woche von target_day, bis einschliesslich
    des letzten verfuegbaren Tages <= target_day. None wenn kein Tag der Woche vorliegt
    (z.B. Montagfrueh vor dem ersten Tick)."""
    iso_week = target_day.isocalendar()[:2]
    week_rows = [r for r in rows
                 if r["day"] <= target_day and r["day"].isocalendar()[:2] == iso_week]
    if not week_rows:
        return None
    return {"high": max(r["high"] for r in week_rows),
            "low": min(r["low"] for r in week_rows),
            "days": len(week_rows)}


def yesterday_range(rows: list[dict], target_day: date) -> dict | None:
    """H/L/C des letzten Handelstages vor target_day. None wenn keiner vorliegt."""
    prior = [r for r in rows if r["day"] < target_day]
    if not prior:
        return None
    r = prior[-1]
    return {"day": r["day"].isoformat(), "high": r["high"], "low": r["low"], "close": r["close"]}


def compute(target_day: date, weekly: bool) -> dict:
    rows = load_rows("MNQ")
    out = {"day": target_day.isoformat(), "weekly_range": week_range(rows, target_day)}
    if not weekly:
        out["yesterday_range"] = yesterday_range(rows, target_day)
    return out


def demo() -> None:
    rows = [
        {"day": date(2026, 8, 10), "open": 100.0, "close": 105.0, "high": 106.0, "low": 99.0},
        {"day": date(2026, 8, 11), "open": 105.0, "close": 103.0, "high": 107.0, "low": 102.0},
        {"day": date(2026, 8, 12), "open": 103.0, "close": 110.0, "high": 111.0, "low": 103.0},
    ]
    wr = week_range(rows, date(2026, 8, 12))
    assert wr == {"high": 111.0, "low": 99.0, "days": 3}, wr
    yr = yesterday_range(rows, date(2026, 8, 12))
    assert yr == {"day": "2026-08-11", "high": 107.0, "low": 102.0, "close": 103.0}, yr
    assert week_range(rows, date(2026, 8, 3)) is None, "andere ISO-Woche muss None liefern"
    assert yesterday_range(rows, date(2026, 8, 10)) is None, "kein Vortag in rows -> None"
    print("demo ok")


def main(argv: list[str] | None = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("day", nargs="?", help="YYYY-MM-DD, Default: heute")
    ap.add_argument("--weekly", action="store_true", help="nur weekly_range berechnen")
    ap.add_argument("--demo", action="store_true", help="Funktions-Selbstcheck, kein Dateizugriff")
    a = ap.parse_args(argv)

    if a.demo:
        demo()
        return 0

    target = date.fromisoformat(a.day) if a.day else date.today()
    print(json.dumps(compute(target, a.weekly), default=str, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
