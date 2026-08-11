#!/usr/bin/env python3
"""These (Jannes, 2026-08-11): Werden mit den **STD-Projektionen der ORG** die Extrema
festgesetzt -- also Session-High/Low oder Daily-High/Low?

ORG = Close der letzten Vortags-Candle 16:14 NY -> Open 9:30 heute
(wiki/concepts/ORG (Opening Range Gap) & 1st Presented FVG.md). Die Gap-Groesse dient als
1 STD; projiziert wird in 0,5er-Schritten nach oben und unten (ICT-Praxis: 0,5/1,0/1,5/
2,0/2,5).

Testlogik: liegt das Extrem naeher an einem STD-Level, als der Zufall erwarten laesst?
Die Level stehen im Abstand 0,5*gap. Ein Trefferfenster von +-tol*gap um jedes Level deckt
also 2*tol/0,5 der Preisachse ab -- bei tol=0,05 sind das **20 %**. Genau gegen diese
Nullerwartung laeuft der Binomialtest. Ohne diese Baseline waere jede Trefferquote
bedeutungslos, weil ein enges Levelraster zwangslaeufig oft "trifft".

Geprueft werden vier Extrema pro Tag:
  - Daily High / Low (RTH 9:30-16:00)
  - NY-AM-Session High / Low (9:30-11:00)

Aufruf:
    python algo/backtest_org_std_extrema.py               # 5m
    python algo/backtest_org_std_extrema.py --tf 1m --tol 0.05
    python algo/backtest_org_std_extrema.py --selfcheck
"""
from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

from scipy.stats import binomtest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "algo"))
from analyze_ohlc import Bar, at, load  # noqa: E402
from backtest_common import write_result  # noqa: E402

STD_STEPS = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
# Zwei Basen, weil das Wiki BEIDE kennt:
#  org = Gap Vortagsschluss 16:14 -> Open 9:30 (Partial-Leiter -0,2/-0,5/-1,0 STD)
#  or_ = Opening RANGE 9:30-10:00 High/Low ("liefert die Ziele des Tages")
# Fuer or_ duerfen nur Extrema AB 10:00 zaehlen -- die Range definiert sonst ihr eigenes
# High/Low und der Treffer waere zirkular.
BASES = {"org": ["daily_high", "daily_low", "am_high", "am_low"],
         "or_": ["post_daily_high", "post_daily_low", "post_am_high", "post_am_low"]}


def find_days(symbol: str, tf: str) -> dict[date, Path]:
    out = {}
    for f in sorted(ROOT.glob(f"raw/marktdaten/*/*/*/{symbol} * {tf}.csv")):
        try:
            out[date(*map(int, f.stem.split()[1].split("-")))] = f
        except (ValueError, IndexError):
            continue
    return out


def org_anchor(bars: list[Bar], day: date) -> float | None:
    """Close der letzten Kerze bis 16:14 NY. Bei 1m exakt die 16:14er, bei groeberen
    TFs die letzte davor beginnende (5m -> 16:10) -- Abweichung bewusst in Kauf genommen,
    daher ist 1m die genauere Variante."""
    kand = [b for b in bars if at(day, 9, 30) <= b.t <= at(day, 16, 14)]
    return kand[-1].c if kand else None


def std_levels(lo_anchor: float, open930: float) -> tuple[float, list[float]]:
    """(Gap, STD-Level beidseitig). Gap kann negativ sein (Discount Gap) -- die Level
    werden vom ORG-Rand aus in beide Richtungen projiziert."""
    gap = abs(open930 - lo_anchor)
    lo, hi = min(lo_anchor, open930), max(lo_anchor, open930)
    lv = [lo, hi]
    for k in STD_STEPS:
        lv += [lo - gap * k, hi + gap * k]
    return gap, sorted(lv)


def naechster(level: list[float], p: float) -> float:
    return min(abs(p - x) for x in level)


def run(symbol: str, tf: str, tol: float) -> dict:
    days = find_days(symbol, tf)
    bars_of = {d: load(p) for d, p in days.items()}
    recs = []
    for d in sorted(days):
        if d.weekday() > 4:
            continue
        vor = max((x for x in days if x < d), default=None)
        if vor is None:
            continue
        anker = org_anchor(bars_of[vor], vor)
        heute = [b for b in bars_of[d] if b.t.date() == d]
        o = next((b for b in heute if b.t == at(d, 9, 30)), None)
        if anker is None or o is None:
            continue
        gap, lv = std_levels(anker, o.o)
        rth = [b for b in heute if at(d, 9, 30) <= b.t < at(d, 16, 0)]
        am = [b for b in heute if at(d, 9, 30) <= b.t < at(d, 11, 0)]
        oran = [b for b in heute if at(d, 9, 30) <= b.t < at(d, 10, 0)]
        p_rth = [b for b in rth if b.t >= at(d, 10, 0)]
        p_am = [b for b in am if b.t >= at(d, 10, 0)]
        if gap <= 0 or not rth or not am or not oran or not p_rth or not p_am:
            continue
        or_lo, or_hi = min(b.l for b in oran), max(b.h for b in oran)
        or_gap, or_lv = std_levels(or_lo, or_hi)
        if or_gap <= 0:
            continue

        r = {"day": d, "gap": gap, "anker": anker, "open930": o.o,
             "or_gap": or_gap, "or_lo": or_lo, "or_hi": or_hi}
        werte = {
            "org": {"daily_high": max(b.h for b in rth), "daily_low": min(b.l for b in rth),
                     "am_high": max(b.h for b in am), "am_low": min(b.l for b in am)},
            "or_": {"post_daily_high": max(b.h for b in p_rth),
                     "post_daily_low": min(b.l for b in p_rth),
                     "post_am_high": max(b.h for b in p_am),
                     "post_am_low": min(b.l for b in p_am)},
        }
        for basis, ws in werte.items():
            g, L = (gap, lv) if basis == "org" else (or_gap, or_lv)
            for k, v in ws.items():
                dist = naechster(L, v)
                r[k] = v
                r[f"{k}_dist"] = dist
                r[f"{k}_rel"] = dist / g
                r[f"{k}_hit"] = dist <= tol * g
        recs.append(r)

    erwartet = min(1.0, 2 * tol / 0.5)  # Abdeckung des Trefferfensters im 0,5er-Raster
    out = {"symbol": symbol, "tf": tf, "tol": tol, "n": len(recs),
           "erwartungswert_zufall": erwartet,
           "zeitraum": [str(recs[0]["day"]), str(recs[-1]["day"])] if recs else None,
           "tests": {}}
    for basis, keys in BASES.items():
        for k in keys:
            hits = sum(r[f"{k}_hit"] for r in recs)
            rel = sorted(r[f"{k}_rel"] for r in recs)
            p = binomtest(hits, len(recs), erwartet,
                          alternative="greater").pvalue if recs else None
            out["tests"][f"{basis}:{k}"] = {
                "hits": hits, "n": len(recs),
                "quote": hits / len(recs) if recs else None,
                "median_rel_abstand": rel[len(rel) // 2] if rel else None,
                "p_binomial": p,
            }
    out["records"] = recs
    return out


def report(res: dict) -> list[str]:
    L = [f"# ORG-STD-Projektionen vs. Extrema ({res['symbol']}, {res['tf']})", ""]
    if not res["n"]:
        return L + ["keine auswertbaren Tage"]
    L.append(f"{res['n']} Tage ({res['zeitraum'][0]} .. {res['zeitraum'][1]}), "
             f"Trefferfenster +-{res['tol']:.0%} der Gap-Groesse.")
    L.append(f"Nullerwartung bei Zufall: **{res['erwartungswert_zufall']:.0%}** "
             f"(Level alle 0,5 STD).")
    L.append("")
    L.append("Basis org = Gap 16:14->9:30 | Basis or_ = Opening Range 9:30-10:00 "
             "(Extrema erst ab 10:00, sonst zirkular). Median-Abstand bei Zufall: 0,125 STD.")
    L.append("")
    L.append(f"| Basis:Extremum | Treffer | Quote | Median-Abstand | p (einseitig) |")
    L.append("|---|---|---|---|---|")
    for k, t in res["tests"].items():
        L.append(f"| {k} | {t['hits']}/{t['n']} | {t['quote']:.0%} | "
                 f"{t['median_rel_abstand']:.3f} STD | {t['p_binomial']:.3f} |")
    return L


def selfcheck() -> None:
    lo, op = 100.0, 110.0          # Gap 10 -> Level alle 5 Punkte
    gap, lv = std_levels(lo, op)
    assert gap == 10.0
    assert 100.0 in lv and 110.0 in lv
    assert 95.0 in lv and 115.0 in lv, "0,5-STD-Level fehlen"
    assert 70.0 in lv and 140.0 in lv, "3,0-STD-Level fehlen (Projektion je vom Rand)"
    # Floats nie exakt vergleichen -- 95.4-95.0 ist 0.3999999999999986
    assert abs(naechster(lv, 95.4) - 0.4) < 1e-9
    assert abs(naechster(lv, 112.5) - 2.5) < 1e-9

    # Discount Gap (Open unter Vortagsschluss) muss dieselbe Gap-Groesse liefern
    g2, lv2 = std_levels(110.0, 100.0)
    assert g2 == 10.0 and sorted(lv2) == sorted(lv), "Richtung darf das Raster nicht aendern"

    d = date(2026, 8, 3)
    mk = lambda hh, mm, o, h, l, c: Bar(at(d, hh, mm), o, h, l, c, 0)
    assert org_anchor([mk(16, 10, 1, 1, 1, 5), mk(16, 20, 1, 1, 1, 9)], d) == 5, \
        "Kerze nach 16:14 darf nicht Anker sein"
    assert org_anchor([mk(9, 0, 1, 1, 1, 5)], d) is None, "vor 9:30 ist kein RTH-Anker"
    print("backtest_org_std_extrema selfcheck ok")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--symbol", default="MNQ")
    ap.add_argument("--tf", default="5m", choices=["1m", "5m", "15m"])
    ap.add_argument("--tol", type=float, default=0.05, help="Trefferfenster als Anteil der Gap")
    ap.add_argument("--selfcheck", action="store_true")
    a = ap.parse_args(argv)
    if a.selfcheck:
        selfcheck()
        return 0
    res = run(a.symbol, a.tf, a.tol)
    print("\n".join(report(res)))
    write_result(f"backtest_org_std_extrema_{a.tf}", res)
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
