#!/usr/bin/env python3
"""Backtest: Wird das 1st presented Displacement (groesstes FVG im 0:00-0:30-MOR-Fenster)
ueber den restlichen Handelstag respektiert?

These (Jannes, 2026-08-13; wiki/concepts/Midnight Opening Range.md: "wird nach rechts ausgezogen
und ueber den gesamten Tag mitgefuehrt"): der 1.p wirkt als Referenz -- laeuft Preis spaeter am
Tag an das FVG (v.a. dessen C.E.) zurueck, reagiert er dort (dreht ab), statt einfach durchzulaufen.

Operationalisierung, bewusst mehrere Kennzahlen statt ein Pass/Fail:
- 1.p = groesstes FVG in 0:00-0:30 (analyze_ohlc.fvgs, Koerper-Disjunkt-VII-Regel).
- Formationsende = Zeit der 3. FVG-Kerze (Displacement-Minute + 1). Tracking NUR danach bis 16:00 NY
  -> kein Lookahead, keine Data-Leakage.
- touch_zone: Preis kehrt in [lo, hi] zurueck.
- touch_ce:   Preis beruehrt das C.E. (0,5-Level).
- Reaktion:   ab erster C.E.-Beruehrung ueber die naechsten REACT_MIN Minuten die max. Bewegung in
              "Respekt-Richtung" (bullish=hoch, bearish=runter) vs. ob das FVG "haelt" (Preis
              handelt nicht ueber die ferne Grenze hinaus: bullish nicht unter lo, bearish nicht ueber hi).
- respektiert: C.E. beruehrt UND gehalten UND Reaktion >= REACT_PTS.
"""
from __future__ import annotations

import sys
from pathlib import Path
from datetime import time as dtime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from analyze_ohlc import load, fvgs  # noqa: E402

REACT_MIN = 15     # Reaktionsfenster nach erster C.E.-Beruehrung (Minuten)
REACT_PTS = 10.0   # Mindest-Reaktion in Punkten, damit "reagiert" gilt


def _mor_1p(day_bars):
    mor = [b for b in day_bars if dtime(0, 0) <= b.t.time() < dtime(0, 30)]
    if len(mor) < 3:
        return None
    fl = fvgs(mor, 0.0)
    if not fl:
        return None
    big = max(fl, key=lambda z: z["size"])
    return big


def analyze_day(day_bars):
    f = _mor_1p(day_bars)
    if f is None:
        return None
    lo, hi, ce, side = f["lo"], f["hi"], (f["lo"] + f["hi"]) / 2, f["side"]
    form_end = f["t"]  # Displacement-Kerze; 3. Kerze ist +1min. Tracking ab der Kerze DANACH.
    post = [b for b in day_bars
            if b.t > form_end and b.t.time() < dtime(16, 0) and b.t.date() == form_end.date()]
    post = post[1:]  # 3. FVG-Kerze selbst ueberspringen (Formation abgeschlossen erst danach)
    if not post:
        return None
    touch_zone = any(b.l <= hi and b.h >= lo for b in post)
    ce_idx = next((i for i, b in enumerate(post) if b.l <= ce <= b.h), None)
    res = {"side": side, "size": f["size"], "ce": ce, "touch_zone": touch_zone,
           "touch_ce": ce_idx is not None, "held": None, "react": None, "respected": False}
    if ce_idx is not None:
        win = post[ce_idx: ce_idx + REACT_MIN + 1]
        # Reaktion = max. Bewegung in Respekt-Richtung, BEVOR die ferne Grenze gebrochen wird.
        react = 0.0
        held = True
        for bar in win:
            if side == "bullish":
                react = max(react, bar.h - ce)
                if bar.l < lo - 1e-9:      # ferne Grenze (lo) gebrochen
                    held = False
                    break
            else:
                react = max(react, ce - bar.l)
                if bar.h > hi + 1e-9:      # ferne Grenze (hi) gebrochen
                    held = False
                    break
        res["react"] = react
        res["held"] = held
        res["respected"] = bool(react >= REACT_PTS)  # reagierte >= Schwelle vor dem Bruch
    return res


def find_day_files():
    out = {}
    for f in sorted(Path("raw/marktdaten").rglob("MNQ * 1m.csv")):
        if "RTH" in f.name:
            continue
        try:
            b = load(f)
        except Exception:
            continue
        for d in set(x.t.date() for x in b):
            day = [x for x in b if x.t.date() == d]
            has_mor = any(dtime(0, 0) <= x.t.time() < dtime(0, 30) for x in day)
            has_rth = any(dtime(9, 30) <= x.t.time() < dtime(16, 0) for x in day)
            if has_mor and has_rth:
                out[d] = day
    return dict(sorted(out.items()))


def run():
    days = find_day_files()
    rows = []
    for d, bars in days.items():
        r = analyze_day(bars)
        if r:
            r["day"] = d
            rows.append(r)
    n = len(rows)
    if not n:
        return {"days": 0}
    tz = sum(r["touch_zone"] for r in rows)
    tce = sum(r["touch_ce"] for r in rows)
    ce_rows = [r for r in rows if r["touch_ce"]]
    held = sum(r["held"] for r in ce_rows)
    resp = sum(r["respected"] for r in rows)
    reacts = sorted(r["react"] for r in ce_rows)
    med_react = reacts[len(reacts) // 2] if reacts else None
    return {"days": n, "touch_zone": tz, "touch_ce": tce, "held_of_ce": held,
            "respected": resp, "median_react": med_react, "rows": rows}


def main():
    r = run()
    if not r.get("days"):
        print("Keine Tage mit MOR+RTH-Daten.")
        return
    n = r["days"]
    print(f"1st-presented-Displacement -- Respekt ueber die Daily Range  (n={n} Tage)\n")
    print(f"  Zone spaeter beruehrt:        {r['touch_zone']:2d}/{n}  ({r['touch_zone']/n:.0%})")
    print(f"  C.E. spaeter beruehrt:        {r['touch_ce']:2d}/{n}  ({r['touch_ce']/n:.0%})")
    ce = r["touch_ce"] or 1
    print(f"  davon FVG gehalten:           {r['held_of_ce']:2d}/{r['touch_ce']}  ({r['held_of_ce']/ce:.0%})")
    print(f"  FVG haelt (kein Bruch {REACT_MIN}m):  {r['held_of_ce']:2d}/{r['touch_ce']}  ({r['held_of_ce']/ce:.0%})")
    print(f"  Median-Reaktion vor Bruch:    {r['median_react']:.2f} Pkt  (Fenster {REACT_MIN}m)")
    print(f"  Reaktion >= {REACT_PTS:.0f} Pkt vor Bruch:   {r['respected']:2d}/{n}  ({r['respected']/n:.0%})")
    print("\n  Pro Tag:")
    for row in r["rows"]:
        rc = f"{row['react']:.1f}" if row['react'] is not None else "  - "
        print(f"    {row['day']}  {row['side']:7} 1.p={row['size']:5.2f}Pkt  "
              f"ce_touch={'J' if row['touch_ce'] else 'n'}  "
              f"halten={'J' if row['held'] else ('n' if row['held'] is not None else '-')}  "
              f"react={rc:>5}  respektiert={'JA' if row['respected'] else 'nein'}")


if __name__ == "__main__":
    main()
