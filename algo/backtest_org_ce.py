#!/usr/bin/env python3
"""Backtest: ICT-These "der ORG-C.E. wird zu ~70% in den ersten 30 Minuten (9:30-10:00 NY)
gefuellt" gegen alle verfuegbaren Handelstage in raw/marktdaten/.

ORG = Gap zwischen der ~16:14-Schlusskerze des Vortags und der 9:30-Open-Kerze, siehe
org_gap() in tools/analyze_ohlc.py und wiki/concepts/ORG (Opening Range Gap) & 1st
Presented FVG.md. C.E. = Mittelpunkt.

Ein Tagesordner allein reicht org_gap() nicht: sowohl die yfinance- als auch die manuellen
TradingView-Exporte grenzen den "Handelstag" teils erst ab 18:00 des Vorabends ab, die
~16:14-Schlusskerze des Vortags liegt also im Nachbarordner -- deshalb wird hier immer
Vortag + Tag zusammen geladen.

Aufruf:
    python algo/backtest_org_ce.py
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from analyze_ohlc import load, org_gap  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "raw" / "marktdaten"


def find_days() -> list[tuple]:
    """(Tag, Datei) -- 1m bevorzugt, sonst 5m als naechstbeste Aufloesung."""
    out = []
    for day_dir in sorted(DATA_DIR.glob("*/*/*")):
        if not day_dir.is_dir():
            continue
        try:
            day = datetime.strptime(day_dir.name, "%d.%m.%Y").date()
        except ValueError:
            continue
        for tf in ("1m", "5m"):
            files = [f for f in day_dir.glob(f"* {tf}.csv") if "RTH" not in f.name]
            if files:
                out.append((day, files[0]))
                break
    return sorted(out)


def main() -> None:
    days = find_days()
    results = []
    for i in range(1, len(days)):
        day, path = days[i]
        _, prev_path = days[i - 1]
        combined = sorted(load(prev_path) + load(path), key=lambda b: b.t)
        r = org_gap(combined, day)
        if r is not None:
            results.append((day, r))

    if not results:
        print("keine Tage mit vollstaendigen ORG-Daten gefunden")
        return

    # Regressionscheck: 2026-07-23 ist gegen den manuell im Journal genannten Wert
    # verifiziert (28.984,00) -- bricht der Detektor, faellt das hier zuerst auf.
    known = next((r for d, r in results if d.isoformat() == "2026-07-23"), None)
    if known is not None:
        assert abs(known["ce"] - 28984.00) < 0.01, known

    hit = [r for _, r in results if r["filled_30m"]]
    print(f"{len(results)} Tage mit ORG-Daten, C.E. gefuellt in 9:30-10:00: "
          f"{len(hit)}/{len(results)} = {100 * len(hit) / len(results):.1f}%\n")

    print(f"{'Tag':<12}{'PrevClose':>11}{'Open':>11}{'Gap':>9}{'C.E.':>11}{'Fill':>7}{'Zeit':>8}")
    for day, r in results:
        print(f"{day.isoformat():<12}{r['prev_close']:>11.2f}{r['today_open']:>11.2f}"
              f"{r['gap']:>9.2f}{r['ce']:>11.2f}{'JA' if r['filled_30m'] else 'nein':>7}"
              f"{r['filled_t'].strftime('%H:%M') if r['filled_t'] else '':>8}")

    for min_gap in (5, 15, 30):
        sub = [r for _, r in results if r["gap"] >= min_gap]
        if sub:
            h = sum(1 for r in sub if r["filled_30m"])
            print(f"\nNur Gap >= {min_gap} Pkt.: {h}/{len(sub)} = {100 * h / len(sub):.1f}%")


if __name__ == "__main__":
    main()
