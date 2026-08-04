#!/usr/bin/env python3
"""Backtest: sind bestimmte FVGs staerker/verlaesslicher (haltender) als der Rest?

Drei Nutzer-Thesen:
1. Das 1. FVG nach 9:30 NY (NY-AM-Session-Start, "1st presented FVG").
2. Das 1. FVG nach 0:00 NY (Midnight-/London-ORG-Start).
3. Das 1. FVG jeder neuen Stunde im 1m-Chart.

"Staerker/verlaesslicher, haelt" wird ueber die bereits im fvgs()-Detektor mitgelieferten
Kennzahlen gemessen: Fuellrate (niedriger = haelt oefter als Support/Resistance statt
durchlaufen zu werden), C.E.-Hit-Rate, durchschnittliche Groesse (Displacement-Staerke).
Jede Kategorie wird gegen den Rest ("normale" FVGs, die in keine der drei Kategorien fallen)
verglichen. Kategorien ueberlappen bewusst (ein FVG kann z.B. sowohl "1. nach 9:30" als auch
"1. seiner Stunde" sein).

Aufruf:
    python algo/backtest_fvg_specialness.py
"""
from __future__ import annotations

import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from analyze_ohlc import load, fvgs, at  # noqa: E402
from backtest_org_ce import find_days  # noqa: E402


def classify(day, gaps):
    first_930 = min((g for g in gaps if g["t"] >= at(day, 9, 30)), key=lambda g: g["t"], default=None)
    first_midnight = min((g for g in gaps if g["t"] >= at(day, 0, 0)), key=lambda g: g["t"], default=None)
    by_hour: dict[tuple, dict] = {}
    for g in gaps:
        key = (g["t"].date(), g["t"].hour)
        if key not in by_hour or g["t"] < by_hour[key]["t"]:
            by_hour[key] = g
    return first_930, first_midnight, {id(g) for g in by_hour.values()}


def stats(gaps: list[dict]) -> dict:
    n = len(gaps)
    if n == 0:
        return {"n": 0, "filled": 0.0, "ce_hit": 0.0, "avg_size": 0.0}
    return {
        "n": n,
        "filled": 100 * sum(1 for g in gaps if g["filled"]) / n,
        "ce_hit": 100 * sum(1 for g in gaps if g["ce_hit"]) / n,
        "avg_size": sum(g["size"] for g in gaps) / n,
    }


def main() -> None:
    groups: dict[str, list[dict]] = {"first_930": [], "first_midnight": [],
                                      "first_of_hour": [], "rest": []}
    days_used = 0
    for day, path in find_days():
        bars = load(path)
        gaps = fvgs(bars)
        # nur FVGs, die tatsaechlich zu dieser Datei/diesem Handelstag gehoeren, nicht
        # zufaellige Lookback-Reste vom Rand der CSV.
        gaps = [g for g in gaps if g["t"].date() in {day, day - timedelta(days=1)}]
        if not gaps:
            continue
        days_used += 1
        first_930, first_midnight, hour_ids = classify(day, gaps)
        for g in gaps:
            tagged = False
            if first_930 is not None and g is first_930:
                groups["first_930"].append(g)
                tagged = True
            if first_midnight is not None and g is first_midnight:
                groups["first_midnight"].append(g)
                tagged = True
            if id(g) in hour_ids:
                groups["first_of_hour"].append(g)
                tagged = True
            if not tagged:
                groups["rest"].append(g)

    # Sanity-Check: hoechstens ein "1. FVG nach X" pro Tag, sonst ist classify() kaputt.
    assert len(groups["first_930"]) <= days_used, groups["first_930"]
    assert len(groups["first_midnight"]) <= days_used, groups["first_midnight"]

    print(f"{days_used} Handelstage mit FVG-Daten.\n")
    print(f"{'Gruppe':<16}{'n':>6}{'Fill%':>8}{'CE-Hit%':>10}{'AvgSize':>10}")
    for name, gaps in groups.items():
        s = stats(gaps)
        print(f"{name:<16}{s['n']:>6}{s['filled']:>8.1f}{s['ce_hit']:>10.1f}{s['avg_size']:>10.2f}")


if __name__ == "__main__":
    main()
