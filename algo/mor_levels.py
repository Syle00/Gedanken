#!/usr/bin/env python3
"""Tages-Lesekopf fuer die Midnight Opening Range (0:00-0:30 NY).

Gibt fuer einen Handelstag aus, was `wiki/concepts/Midnight Opening Range.md` als die drei
markanten Punkte nennt (Midnight Opening Price, Range High, Range Low), dazu die Quarters
(0,25 / 0,5 / 0,75), die Standard-Deviation-Projektionen (Vielfache der Range ueber beide
Grenzen hinaus) und die "first presentation" -- das **erste FVG innerhalb der 0:00-0:30-Range**,
das laut Wiki den ganzen Tag mitgefuehrt wird.

Beantwortet ausserdem die Frage, die Jannes am 2026-08-11 gestellt hat: **wurde das Tages-High
oder das Tages-Low von einem STD-Level festgelegt?** Dafuer wird k gemessen (wie viele
Range-Vielfache das Extrem ueber die Grenze hinausgeht) und der Abstand zum naechsten
STD-Level in Punkten ausgewiesen -- "auf dem Level" ist eine Behauptung, die eine Zahl braucht.

Abgrenzung: das ist der Einzeltag-Readout. Die Statistik ueber viele Tage (wie oft liegt das
Extrem bei welchem k) macht `backtest_midnight_range_std.py`, dessen `session_range()` hier
wiederverwendet wird.

Aufruf:
    python algo/mor_levels.py 2026-08-11
    python algo/mor_levels.py 2026-08-11 --symbol MNQ
    python algo/mor_levels.py --selfcheck
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.analyze_ohlc import DATA_DIR, at, fvgs, load  # noqa: E402

from backtest_midnight_range_std import session_range, window_gaps  # noqa: E402

STDS = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0]


def load_day(symbol: str, day):
    hits = list(DATA_DIR.rglob(f"{symbol} {day:%Y-%m-%d} 1m.csv"))
    if not hits:
        raise SystemExit(f"Keine 1m-Datei fuer {symbol} am {day}. Erst nachladen:\n"
                         f"  python algo/fetch_yfinance.py {day - timedelta(days=1)} "
                         f"{day + timedelta(days=1)}")
    return load(hits[0])


def levels(rh: float, rl: float) -> list[tuple[str, float]]:
    """Quarters innerhalb der Range + STD-Projektionen nach oben und unten."""
    rng = rh - rl
    out = [("Range Low (0)", rl)]
    out += [(f"Q {q:.2f}", rl + q * rng) for q in (0.25, 0.5, 0.75)]
    out += [("Range High (1)", rh)]
    out += [(f"+{s:g} STD", rh + s * rng) for s in STDS]
    out += [(f"-{s:g} STD", rl - s * rng) for s in STDS]
    return out


def first_presentation(bars, day):
    """Erstes FVG *innerhalb* der 0:00-0:30-Range (Wiki: "first presentation")."""
    win = [b for b in bars if at(day, 0, 0) <= b.t < at(day, 0, 30)]
    found = sorted(fvgs(win), key=lambda f: f["t"] if "t" in f else 0)
    return found[0] if found else None


def report(symbol: str, day) -> None:
    bars = load_day(symbol, day)
    sess = [b for b in bars if at(day, 0, 0) <= b.t]
    if not sess:
        raise SystemExit(f"Keine Kerzen ab 0:00 NY am {day}.")
    gaps = window_gaps(bars, day, (0, 0), (0, 30))
    if gaps:
        raise SystemExit(
            f"MOR am {day} nicht berechenbar: {len(gaps)} von 30 Minuten fehlen in den Daten\n"
            f"  fehlende Minuten (Offset ab 0:00): {gaps}\n"
            f"  {'Die 0:00-Kerze fehlt -- der Midnight Opening Price ist damit unbekannt.' if 0 in gaps else ''}\n"
            f"  Ursache: yfinance liefert fuer MNQ=F die ersten Minuten nach Mitternacht NY\n"
            f"  systematisch nicht (am 2026-08-11 gegen den Rohabruf verifiziert -- die Luecke\n"
            f"  steckt in der Quelle, nicht in fetch_yfinance.py).\n"
            f"  Ausweg: 1m-Export aus TradingView fuer diesen Tag nach raw/marktdaten/ legen.\n"
            f"  Bewusst kein --force: eine aus 21 von 30 Minuten gerechnete Opening Range faellt\n"
            f"  zu klein aus und blaeht jede STD-Ableitung auf. Falsche Zahlen sind hier\n"
            f"  schaedlicher als gar keine.")
    mor = session_range(bars, day, (0, 0), (0, 30), expect_complete=True)
    if not mor:
        raise SystemExit(f"Keine Midnight Opening Range am {day} (Range <= 0).")
    rh, rl, rng = mor
    op = next(b.o for b in bars if b.t >= at(day, 0, 0))

    hi_bar = max(sess, key=lambda b: b.h)
    lo_bar = min(sess, key=lambda b: b.l)
    k_high = max(0.0, (hi_bar.h - rh) / rng)
    k_low = max(0.0, (rl - lo_bar.l) / rng)

    print(f"=== Midnight Opening Range {symbol} {day} (0:00-0:30 NY) ===")
    print(f"  Midnight Open : {op:10.2f}")
    print(f"  Range High    : {rh:10.2f}")
    print(f"  Range Low     : {rl:10.2f}")
    print(f"  Range         : {rng:10.2f} Pkt")
    print(f"\n  Daten bis     : {bars[-1].t:%H:%M} NY"
          f"{'  (Session noch offen!)' if bars[-1].t < at(day, 17, 0) else ''}")
    print(f"  Tages-High    : {hi_bar.h:10.2f} um {hi_bar.t:%H:%M}   k = {k_high:.2f} STD")
    print(f"  Tages-Low     : {lo_bar.l:10.2f} um {lo_bar.t:%H:%M}   k = {k_low:.2f} STD")

    lv = levels(rh, rl)
    # Naechstes Level je Extrem, statt einer festen Punkt-Toleranz: bei einer 18-Pkt-Range
    # liegen die STDs so dicht, dass jede absolute Schwelle mehrere Treffer meldet und
    # damit Praezision vortaeuscht, die es nicht gibt. Der Abstand wird zusaetzlich in
    # Range-Anteilen ausgewiesen -- nur das ist ueber verschieden grosse Ranges vergleichbar.
    for lbl, px_x in (("Tages-High", hi_bar.h), ("Tages-Low", lo_bar.l)):
        name, px = min(lv, key=lambda x: abs(x[1] - px_x))
        d = abs(px - px_x)
        print(f"\n  {lbl} naechstes Level: {name} @ {px:.2f}"
              f"   Abstand {d:.2f} Pkt = {d / rng:.2f} x Range")

    print("\n  Level:")
    for name, px in sorted(lv, key=lambda x: -x[1]):
        print(f"    {name:16s} {px:10.2f}")

    fp = first_presentation(bars, day)
    print("\n  First Presentation (erstes FVG in 0:00-0:30):")
    if fp:
        print(f"    {fp['side']}  {fp['lo']:.2f} - {fp['hi']:.2f}   C.E. {fp['ce']:.2f}"
              f"   Groesse {fp['size']:.2f} Pkt   entstanden {fp['t']:%H:%M}"
              f"   {'gefuellt ' + format(fp['fill_t'], '%H:%M') if fp['filled'] else 'offen'}")
    else:
        print("    keine -- laut Wiki tritt dann der Breaker Block an ihre Stelle")


def selfcheck() -> None:
    rh, rl = 200.0, 100.0  # Range 100
    d = dict(levels(rh, rl))
    assert d["Range Low (0)"] == 100.0 and d["Range High (1)"] == 200.0, d
    assert d["Q 0.50"] == 150.0, d
    assert d["+1 STD"] == 300.0 and d["-1 STD"] == 0.0, d
    assert d["+2 STD"] == 400.0 and d["-2 STD"] == -100.0, d
    # k muss bei genau -1 STD auch 1.0 ergeben, nicht 0.99 oder 2.0
    assert max(0.0, (rl - 0.0) / (rh - rl)) == 1.0
    print("selfcheck ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("datum", nargs="?", help="YYYY-MM-DD")
    ap.add_argument("--symbol", default="MNQ")
    ap.add_argument("--selfcheck", action="store_true")
    a = ap.parse_args()
    if a.selfcheck:
        selfcheck()
    elif a.datum:
        report(a.symbol, datetime.strptime(a.datum, "%Y-%m-%d").date())
    else:
        ap.error("Datum fehlt (oder --selfcheck)")
