#!/usr/bin/env python3
"""Wie selten ist ein grosses Vakuum zwischen zwei aufeinanderfolgenden 1m-Kerzen?

Anlass: Jannes sah am 2026-08-10 um 12:31/12:32 NY im MNQ einen ~19-Punkte-Bereich,
in dem gar nicht gehandelt wurde, und hielt ihn fuer unnatuerlich / Anzeigefehler.
Dieses Script beziffert, wie haeufig so ein Vakuum in den vorhandenen Daten ist.

Gezaehlt wird nur zwischen echt benachbarten Minuten (t2 - t1 == 60s), damit
Session-Pausen und Tagesgrenzen nicht als Gap durchgehen. Ein Vakuum ist der
Preisbereich, den weder Kerze i noch Kerze i+1 beruehrt hat:
    bullish:  low(i+1)  > high(i)   -> Groesse = low(i+1) - high(i)
    bearish:  high(i+1) < low(i)    -> Groesse = low(i)   - high(i+1)

Aufruf:
    python algo/backtest_1m_gaps.py                # alle Symbole
    python algo/backtest_1m_gaps.py --symbol MNQ
    python algo/backtest_1m_gaps.py --min-pts 10   # nur grosse Vakuen listen
    python algo/backtest_1m_gaps.py --selfcheck
"""

from __future__ import annotations

import argparse
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.analyze_ohlc import DATA_DIR, Bar, load  # noqa: E402


def gaps_in(bars: list[Bar]) -> list[tuple[Bar, float, str]]:
    """(Kerze i+1, Vakuumgroesse in Punkten, Richtung) fuer benachbarte Minuten."""
    out = []
    for a, b in zip(bars, bars[1:]):
        if (b.t - a.t).total_seconds() != 60:
            continue  # Session-Pause / Tagesgrenze, kein handelbares Vakuum
        if b.l > a.h:
            out.append((b, b.l - a.h, "up"))
        elif b.h < a.l:
            out.append((b, a.l - b.h, "down"))
    return out


def filled_within(bars: list[Bar], idx: int, lo: float, hi: float) -> int | None:
    """Nach wie vielen Minuten wird das Vakuum [lo, hi] wieder komplett durchhandelt?"""
    for n, b in enumerate(bars[idx + 1:], start=1):
        if b.l <= lo and b.h >= hi:
            return n
        if b.l <= lo or b.h >= hi:
            return n  # beruehrt reicht als Fuellung (ICT-Konvention: erste Beruehrung)
    return None


def collect(symbol: str) -> tuple[list[tuple], int, int]:
    """(alle Vakuen, Anzahl Tage, Anzahl Minutenpaare)."""
    found, days, pairs = [], 0, 0
    files = sorted(DATA_DIR.rglob(f"{symbol} *-*-* 1m.csv"))
    for path in files:
        bars = load(path)
        if len(bars) < 2:
            continue
        days += 1
        pairs += sum(1 for a, b in zip(bars, bars[1:])
                     if (b.t - a.t).total_seconds() == 60)
        index = {b.t: i for i, b in enumerate(bars)}
        for bar, size, direction in gaps_in(bars):
            i = index[bar.t]
            prev = bars[i - 1]
            lo, hi = (prev.h, bar.l) if direction == "up" else (bar.h, prev.l)
            found.append((bar.t, size, direction, lo, hi,
                          filled_within(bars, i, lo, hi)))
    return found, days, pairs


def report(symbol: str, min_pts: float) -> None:
    found, days, pairs = collect(symbol)
    if not days:
        print(f"{symbol}: keine 1m-Dateien in {DATA_DIR}")
        return
    sizes = sorted(g[1] for g in found)
    print(f"\n=== {symbol} — Vakuen zwischen benachbarten 1m-Kerzen ===")
    print(f"Datenbasis: {days} Tage, {pairs:,} Minutenpaare")
    print(f"Vakuen gesamt: {len(found)}  ({len(found) / pairs * 100:.3f} % aller Minuten)")
    if not sizes:
        return
    print(f"Median {statistics.median(sizes):.2f} Pkt | "
          f"p90 {sizes[int(len(sizes) * 0.90)]:.2f} | "
          f"p99 {sizes[int(len(sizes) * 0.99)]:.2f} | max {sizes[-1]:.2f}")

    for schwelle in (5, 10, 15, 20, 30):
        n = sum(1 for s in sizes if s >= schwelle)
        alle_n_tage = days / n if n else float("inf")
        print(f"  >= {schwelle:2d} Pkt: {n:4d}  "
              f"({'nie' if not n else f'alle {alle_n_tage:.1f} Handelstage'})")

    gross = sorted((g for g in found if g[1] >= min_pts), key=lambda g: -g[1])
    if gross:
        print(f"\n  Vakuen >= {min_pts} Pkt (groesste zuerst):")
        for t, size, direction, lo, hi, fill in gross[:25]:
            wann = "offen geblieben" if fill is None else f"nach {fill} min beruehrt"
            print(f"    {t:%Y-%m-%d %H:%M} {direction:4s} {size:6.2f} Pkt  "
                  f"[{lo:.2f}-{hi:.2f}]  {wann}")

    offen = [g for g in found if g[1] >= min_pts and g[5] is None]
    print(f"\n  davon am selben Tag nie beruehrt: {len(offen)} von {len(gross)}")


def selfcheck() -> None:
    from datetime import datetime, timedelta
    from zoneinfo import ZoneInfo
    ny = ZoneInfo("America/New_York")
    t0 = datetime(2026, 8, 10, 12, 30, tzinfo=ny)

    def bar(minute, o, h, l, c):
        return Bar(t0 + timedelta(minutes=minute), o, h, l, c)

    # 1) sauberes Abwaerts-Vakuum von 10 Punkten zwischen Minute 0 und 1
    bars = [bar(0, 100, 110, 100, 105), bar(1, 90, 90, 80, 85)]
    g = gaps_in(bars)
    assert len(g) == 1 and g[0][1] == 10 and g[0][2] == "down", g

    # 2) ueberlappende Kerzen -> kein Vakuum
    assert gaps_in([bar(0, 100, 110, 100, 105), bar(1, 104, 108, 95, 100)]) == []

    # 3) Zeitluecke (Session-Pause) zaehlt nicht als Vakuum
    assert gaps_in([bar(0, 100, 110, 100, 105), bar(60, 90, 90, 80, 85)]) == []

    # 4) Fuellung wird erkannt bzw. als offen gemeldet
    b = [bar(0, 100, 110, 100, 105), bar(1, 90, 90, 80, 85), bar(2, 85, 95, 84, 94)]
    assert filled_within(b, 1, 90, 100) == 1
    assert filled_within(b[:2], 1, 90, 100) is None

    print("selfcheck ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", default=None, help="MNQ, ES, ... (Default: alle gefundenen)")
    ap.add_argument("--min-pts", type=float, default=10.0)
    ap.add_argument("--selfcheck", action="store_true")
    a = ap.parse_args()
    if a.selfcheck:
        selfcheck()
    else:
        symbole = [a.symbol] if a.symbol else sorted(
            {p.name.split()[0] for p in DATA_DIR.rglob("* 1m.csv")})
        for s in symbole:
            report(s, a.min_pts)
