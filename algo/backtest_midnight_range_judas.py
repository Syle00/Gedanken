#!/usr/bin/env python3
"""Backtest: Judas-Swing-Klassifikation fuer Session-Opening-Ranges (Midnight/London,
NY Pre-Session, NY PM -- alle drei per Rohquelle als eigene "Opening Range mit 1. presented
FVG" bestaetigt, siehe Log-Eintrag).

Der reine Min/Max-Test in backtest_midnight_range_std.py kann "Manipulation, die sich wieder
zurueckdreht" nicht von "das war der echte Move" unterscheiden -- genau die Ausnahme, die die
Quelle (wiki/concepts/Midnight Opening Range.md) fuer Ueberschreitungen nennt. Dieses Skript
trennt beides: eine Seite der Range (Low fuer Sellside, High fuer Buyside) gilt nur dann als
"Manipulation" (Judas Swing), wenn der Preis sie innerhalb des Test-Fensters durchbricht UND
per Schlusskurs noch innerhalb desselben Fensters zurueckerobert. Haelt der Durchbruch bis
Fensterende, ist es laut Quelle kein Manipulation-Swing mehr, sondern der echte Move ("Trend").

Beantwortet drei Fragen direkt:
1. Wie tief geht eine *echte* Manipulation (Median/Muster), wenn nicht immer genau -1 STD?
2. Wie oft wird High/Low tatsaechlich schon in der Opening Range festgelegt (Range-Seite im
   Testfenster nie durchbrochen)?
3. Gilt dasselbe Muster auch fuer NY Pre-Session (7:00-7:30) und NY PM (13:30-14:00), nicht
   nur fuer Midnight/London?

Aufruf:
    python algo/backtest_midnight_range_judas.py
"""
from __future__ import annotations

import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from analyze_ohlc import load, at, fvgs  # noqa: E402
from backtest_org_ce import find_days  # noqa: E402
from backtest_midnight_range_std import session_range  # noqa: E402
from backtest_common import write_result  # noqa: E402

# (Label, Range-Fenster, Test-Fenster) -- alle drei per Rohquelle als eigene Opening Range
# mit "1. presented FVG" bestaetigt (siehe algo/PLAN.md-Log).
SESSIONS = [
    ("Midnight/London ORG", (0, 0), (0, 30), (0, 30), (5, 0)),
    ("NY Pre-Session ORG", (7, 0), (7, 30), (7, 30), (9, 30)),
    ("NY PM ORG", (13, 30), (14, 0), (14, 0), (16, 0)),
]


def classify_side(bars, day, rh, rl, rng, side: str, start, end) -> dict:
    """side='low' (Sellside-Manipulation unter Rl) oder 'high' (Buyside-Manipulation ueber Rh).
    `start`/`end` ist das Testfenster, in dem Durchbruch + Rueckeroberung geprueft werden."""
    seg = [b for b in bars if start <= b.t < end]
    level = rl if side == "low" else rh
    penetrating = [b for b in seg if (b.l < level if side == "low" else b.h > level)]
    if not penetrating:
        return {"status": "no_extension", "k": 0.0}

    extreme_bar = min(penetrating, key=lambda b: b.l) if side == "low" \
        else max(penetrating, key=lambda b: b.h)
    depth = (level - extreme_bar.l) if side == "low" else (extreme_bar.h - level)
    k = depth / rng

    after = [b for b in seg if b.t > extreme_bar.t]
    reclaimed = any((b.c >= level) if side == "low" else (b.c <= level) for b in after)
    return {"status": "manipulation" if reclaimed else "trend", "k": k, "t": extreme_bar.t}


def fvg_range(bars, day, start_hm, end_hm):
    """Groesstes FVG (nicht zwingend das erste, siehe wiki/concepts/ORG.../1st Presented FVG)
    mit Startzeit im Fenster -- dessen eigene Lo/Hi als STD-Basiseinheit statt der Kerzen-Range."""
    start, end = at(day, *start_hm), at(day, *end_hm)
    cand = [g for g in fvgs(bars) if start <= g["t"] < end]
    if not cand:
        return None
    biggest = max(cand, key=lambda g: g["size"])
    return biggest["hi"], biggest["lo"], biggest["size"]


def report(name: str, results: list[dict], range_label: str, window_label: str) -> None:
    n = len(results)
    if n == 0:
        print(f"{name}: keine Tage")
        return
    counts = {"no_extension": 0, "manipulation": 0, "trend": 0}
    for r in results:
        counts[r["status"]] += 1
    assert sum(counts.values()) == n, counts  # jeder Tag faellt in genau eine Kategorie
    print(f"\n{name} (n={n}):")
    for status, label in [
        ("no_extension", f"High/Low bereits in {range_label} gesetzt (keine Extension)"),
        ("manipulation", f"Manipulation (Durchbruch + Rueckeroberung in {window_label})"),
        ("trend", "Trend/echter Move (Durchbruch haelt bis Fensterende)"),
    ]:
        c = counts[status]
        print(f"  {label:<62}{c:>4}  ({100 * c / n:.1f}%)")

    manip_ks = [r["k"] for r in results if r["status"] == "manipulation"]
    if manip_ks:
        print(f"  -> Manipulationstiefe (nur 'manipulation'-Tage, n={len(manip_ks)}): "
              f"Median {statistics.median(manip_ks):.2f} STD, "
              f"Mittelwert {statistics.mean(manip_ks):.2f} STD")
        buckets = [0.5, 1.0, 1.5, 2.0, 3.0, float("inf")]
        for b in buckets:
            lo = 0 if b == buckets[0] else buckets[buckets.index(b) - 1]
            c = sum(1 for k in manip_ks if lo < k <= b) if b != buckets[0] else sum(1 for k in manip_ks if k <= b)
            label = f"<= {b} STD" if b != float("inf") else "> 3 STD"
            print(f"     {label:<12}{c:>4}  ({100 * c / len(manip_ks):.1f}%)")


def compute_session(label: str, range_hm: tuple, range_end_hm: tuple,
                     test_start_hm: tuple, test_end_hm: tuple, use_fvg: bool = False) -> dict:
    low_results, high_results = [], []
    either_count = both_count = days_used = 0
    for day, path in find_days():
        bars = load(path)
        rr = (fvg_range(bars, day, range_hm, range_end_hm) if use_fvg
              else session_range(bars, day, range_hm, range_end_hm))
        if rr is None:
            continue
        rh, rl, rng = rr
        test_start, test_end = at(day, *test_start_hm), at(day, *test_end_hm)
        lo = classify_side(bars, day, rh, rl, rng, "low", test_start, test_end)
        hi = classify_side(bars, day, rh, rl, rng, "high", test_start, test_end)
        low_results.append(lo)
        high_results.append(hi)
        lo_ne, hi_ne = lo["status"] == "no_extension", hi["status"] == "no_extension"
        either_count += lo_ne or hi_ne
        both_count += lo_ne and hi_ne
        days_used += 1

    range_label = f"{range_hm[0]:02d}:{range_hm[1]:02d}-{range_end_hm[0]:02d}:{range_end_hm[1]:02d}"
    window_label = f"{test_start_hm[0]:02d}:{test_start_hm[1]:02d}-{test_end_hm[0]:02d}:{test_end_hm[1]:02d}"
    return {"label": label, "range_label": range_label, "window_label": window_label,
            "use_fvg": use_fvg, "days_used": days_used, "low_results": low_results,
            "high_results": high_results, "either_count": either_count, "both_count": both_count}


def print_session(data: dict) -> None:
    print(f"\n{'=' * 70}\n{data['label']} (Range {data['range_label']}"
          f"{' , groesstes FVG darin' if data['use_fvg'] else ''}, Testfenster {data['window_label']}) "
          f"-- {data['days_used']} Tage")
    report("Sellside (unter Range-Low)", data["low_results"], data["range_label"], data["window_label"])
    report("Buyside (ueber Range-High)", data["high_results"], data["range_label"], data["window_label"])

    if data["days_used"] == 0:
        return
    days_used = data["days_used"]
    set_in_range = sum(1 for r in data["low_results"] + data["high_results"]
                        if r["status"] == "no_extension")
    print(f"\nInsgesamt {set_in_range}/{2 * days_used} Seiten "
          f"({100 * set_in_range / (2 * days_used):.1f}%) im Testfenster ueberhaupt nicht "
          f"durchbrochen -- fuer diese haelt die These 'High/Low in {data['range_label']} gesetzt' woertlich.")
    print(f"Pro Tag (High ODER Low): an {data['either_count']}/{days_used} Tagen "
          f"({100 * data['either_count'] / days_used:.1f}%) wurde mindestens eine Seite nicht "
          f"durchbrochen -- an {data['both_count']}/{days_used} Tagen beide.")


def run() -> dict:
    sessions = [compute_session(label, r_start, r_end, t_start, t_end)
                for label, r_start, r_end, t_start, t_end in SESSIONS]
    # Zusatzthese: nicht die rohe Kerzen-Range, sondern das groesste FVG *innerhalb* der
    # Midnight Range als STD-Basiseinheit (wiki: "gerade beim 1. presented Displacement
    # werden diese Level ueber die London Session hinweg respektiert").
    sessions.append(compute_session(
        "Midnight/London ORG -- groesstes FVG statt Kerzen-Range",
        (0, 0), (0, 30), (0, 30), (5, 0), use_fvg=True))
    return {"sessions": sessions}


def main() -> None:
    result = run()
    for data in result["sessions"]:
        print_session(data)

    summary = [{"label": s["label"], "days_used": s["days_used"],
                "either_pct": 100 * s["either_count"] / s["days_used"] if s["days_used"] else None,
                "both_pct": 100 * s["both_count"] / s["days_used"] if s["days_used"] else None}
               for s in result["sessions"]]
    write_result("backtest_midnight_range_judas", {"sessions": summary})


if __name__ == "__main__":
    main()
