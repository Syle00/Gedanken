#!/usr/bin/env python3
"""Backtest: legt die Midnight/London Opening Range (0:00-0:30 NY) per Standard-Deviation-
Projektion das Tages-High/-Low fest?

These aus wiki/concepts/Midnight Opening Range.md: der Fib ueber die 0:00-0:30-Range wird
mit negativen Standard Deviations (Vielfache der Range-Groesse) nach unten verlaengert, um
Tages-High/-Low zu antizipieren. Maximale Manipulation waehrend London (1:00-5:00 NY) soll
bei -1 STD liegen -- geht der Preis weiter, ist es kein Manipulation-Swing mehr, sondern der
eigentliche Move.

Gemessen wird k = wie viele Range-Vielfache der Tages-Low/-High ueber die Range-Grenze
hinausgeht (k=0: bleibt innerhalb der Range, k=1: genau -1/+1 STD, k=2: -2/+2 STD, ...) --
sowohl fuer die komplette London-Session als auch fuer den ganzen Tag.

Aufruf:
    python algo/backtest_midnight_range_std.py
"""
from __future__ import annotations

import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from analyze_ohlc import load, at  # noqa: E402
from backtest_org_ce import find_days  # noqa: E402

BUCKETS = [0.5, 1.0, 1.5, 2.0, 3.0, 5.0, float("inf")]


def session_range(bars, day, start_hm: tuple[int, int], end_hm: tuple[int, int]):
    """Kerzen-High/Low ueber ein Zeitfenster (z.B. eine Opening Range). None, wenn keine
    Kerzen im Fenster liegen oder das Fenster keine echte Range hat (rng <= 0)."""
    win = [b for b in bars if at(day, *start_hm) <= b.t < at(day, *end_hm)]
    if not win:
        return None
    rh, rl = max(b.h for b in win), min(b.l for b in win)
    rng = rh - rl
    return (rh, rl, rng) if rng > 0 else None


def midnight_range(bars, day):
    """Rueckwaertskompatibler Spezialfall: Midnight/London Opening Range 0:00-0:30 NY."""
    return session_range(bars, day, (0, 0), (0, 30))


def k_extension(bars, day, start, end, rh, rl, rng):
    seg = [b for b in bars if start <= b.t < end]
    if not seg:
        return None, None
    day_high = max(b.h for b in seg)
    day_low = min(b.l for b in seg)
    k_high = max(0.0, (day_high - rh) / rng)
    k_low = max(0.0, (rl - day_low) / rng)
    return k_high, k_low


def bucket(k: float) -> str:
    for b in BUCKETS:
        if k <= b:
            return f"<= {b} STD" if b != float("inf") else "> 5 STD"
    return "> 5 STD"


def report(name: str, ks: list[float]) -> None:
    if not ks:
        print(f"{name}: keine Tage")
        return
    print(f"\n{name} (n={len(ks)}): Median {statistics.median(ks):.2f} STD, "
          f"Mittelwert {statistics.mean(ks):.2f} STD, Max {max(ks):.2f} STD")
    counts: dict[str, int] = {}
    for k in ks:
        counts[bucket(k)] = counts.get(bucket(k), 0) + 1
    for b in BUCKETS:
        label = f"<= {b} STD" if b != float("inf") else "> 5 STD"
        c = counts.get(label, 0)
        print(f"  {label:<12}{c:>4}  ({100 * c / len(ks):.1f}%)")


def main() -> None:
    london_high, london_low, day_high, day_low = [], [], [], []
    days_used = 0
    for day, path in find_days():
        bars = load(path)
        mr = midnight_range(bars, day)
        if mr is None:
            continue
        rh, rl, rng = mr
        lh, ll = k_extension(bars, day, at(day, 1, 0), at(day, 5, 0), rh, rl, rng)
        dh, dl = k_extension(bars, day, at(day, 0, 30), at(day, 17, 0), rh, rl, rng)
        if lh is None or dh is None:
            continue
        days_used += 1
        london_high.append(lh)
        london_low.append(ll)
        day_high.append(dh)
        day_low.append(dl)

    print(f"{days_used} Handelstage mit Midnight-Range-Daten.")
    print("\n-- Waehrend London (1:00-5:00 NY) -- These: 'max. Manipulation bis -1 STD' --")
    report("London-Low unter Range-Tief", london_low)
    report("London-High ueber Range-Hoch", london_high)
    print("\n-- Ganzer Tag (0:30-17:00 NY) --")
    report("Tages-Low unter Range-Tief", day_low)
    report("Tages-High ueber Range-Hoch", day_high)

    exceed_1std = sum(1 for k in london_low if k > 1.0) / len(london_low)
    print(f"\nLondon-Low geht bei {100 * exceed_1std:.1f}% der Tage ueber -1 STD hinaus "
          f"(These behauptet: das soll waehrend London selten/nie passieren).")


if __name__ == "__main__":
    main()
