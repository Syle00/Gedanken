"""Qs/Os/Hs-Raster fuer eine beliebige Range (Wick, FVG, OB, ORG, NDOG/NWOG, ...).

Die Konzepte sind fraktal: dasselbe Raster gilt auf jedem Timeframe und fuer Premium-
wie Discount-Seite. Ausgabe ist immer die volle 16tel-Tabelle -- Qs (/4) und Os (/8)
sind Teilmengen davon und werden in der Spalte "Stufe" markiert. Alle Level auf das
Tick-Raster gerundet (siehe analyze_ohlc.TICK_SIZE), sonst sind es keine handelbaren Preise.

  python tools/qoh_levels.py 30001.5 29807.25 --label "Premium Wick 12.08."
  python tools/qoh_levels.py 30001.5 29807.25 --touch "raw/marktdaten/.../MNQ 2026-08-13 1m.csv"
"""
import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from analyze_ohlc import to_tick  # noqa: E402


def grid(high: float, low: float, symbol: str = "MNQ"):
    """16 Schritte von low nach high. Gibt (Bruch, Stufe, Name, Preis) je Level."""
    rng = high - low
    out = []
    for i in range(17):
        f = i / 16
        stufe = "Qs" if i % 4 == 0 else "Os" if i % 2 == 0 else "Hs"
        if i == 0:
            name = "Low (0,0)"
        elif i == 16:
            name = "High (1,0)"
        elif i == 8:
            name = "C.E / Mean Threshold (0,5)"
        else:
            name = f"{f:.4f}".rstrip("0").replace(".", ",")
        out.append((f, stufe, name, to_tick(low + f * rng, symbol)))
    return out


def touched(levels, bars):
    """Welche Level hat der Preis beruehrt? bars = Liste von (high, low)."""
    return {p for _, _, _, p in levels if any(l <= p <= h for h, l in bars)}


def wick(o: float, h: float, l: float, c: float, seite: str):
    """Wick-Range einer Kerze. Body-Grenze ist der aeussere von Open/Close -- bei einer
    bearishen Kerze ist das Body-High das OPEN, nicht der Close (haeufigster Denkfehler)."""
    if seite == "premium":
        return h, max(o, c)          # Body-High -> High
    return min(o, c), l              # Low -> Body-Low


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("high", type=float)
    ap.add_argument("low", type=float)
    ap.add_argument("--label", default="Range")
    ap.add_argument("--symbol", default="MNQ")
    ap.add_argument("--touch", help="OHLC-CSV: markiert bereits beruehrte Level")
    ap.add_argument("--wick", choices=("premium", "discount"),
                    help="high/low als Kerzen-High/-Low deuten; --ocl liefert Open/Close")
    ap.add_argument("--oc", nargs=2, type=float, metavar=("OPEN", "CLOSE"))
    a = ap.parse_args()

    if a.wick:
        if not a.oc:
            ap.error("--wick braucht --oc OPEN CLOSE")
        a.high, a.low = wick(a.oc[0], a.high, a.low, a.oc[1], a.wick)

    lv = grid(a.high, a.low, a.symbol)
    hit = set()
    if a.touch:
        rows = list(csv.DictReader(open(a.touch)))
        hit = touched(lv, [(float(r["high"]), float(r["low"])) for r in rows])

    rng = a.high - a.low
    print(f"{a.label}: {a.low:.2f} -> {a.high:.2f}  ({rng:.2f} Punkte, {a.symbol})\n")
    print(f"{'Stufe':<6}{'Fib':<8}{'Level':<28}{'Preis':>10}  {'beruehrt' if hit else ''}")
    for f, stufe, name, p in lv:
        mark = "x" if p in hit else ""
        print(f"{stufe:<6}{f:<8.4f}{name:<28}{p:>10.2f}  {mark}")


def _selfcheck():
    """Regressionscheck gegen die Daily-Kerze 05.08.2026 (bearish!) -- Nutzerkorrektur
    2026-08-13: bei einer bearishen Kerze ist das Body-High das OPEN, nicht der Close."""
    o, h, l, c = 29781.25, 30073.25, 29530.75, 29615.00
    assert wick(o, h, l, c, "premium") == (30073.25, 29781.25)
    assert wick(o, h, l, c, "discount") == (29615.00, 29530.75)   # (high, low) = Body-Low -> Low
    # bullish zur Gegenprobe: Body-High ist der Close
    assert wick(29663.0, 30001.5, 29625.0, 29807.25, "premium") == (30001.5, 29807.25)
    lv = grid(30073.25, 29781.25)
    assert lv[8][3] == 29927.25, lv[8]                 # C.E
    assert [p for _, s, _, p in lv if s == "Qs"] == [29781.25, 29854.25, 29927.25,
                                                     30000.25, 30073.25]
    assert all(p * 4 == int(p * 4) for _, _, _, p in lv)   # alles auf dem 0,25-Raster
    print("selfcheck ok")


if __name__ == "__main__":
    if "--selfcheck" in sys.argv:
        _selfcheck()
    else:
        main()
