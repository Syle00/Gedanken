#!/usr/bin/env python3
"""Messen, ob ICTs "High Probability FVG"-Kriterien in MNQ-Daten wirklich etwas bringen.

Zwei Quellen, beide am 2026-08-14 ingestet:
  * ICT Private Mentorship "High Probability FVG's" (Masterclass) -- die **Kontext**-Regeln:
    Bias/Draw on Liquidity muss vorher feststehen, das FVG muss in der richtigen Haelfte der
    **Vortagesrange** liegen (bearish untere, bullish obere), und es muss in einer
    **Killzone** entstehen. Implementiert als `analyze_ohlc.hp_context()`.
  * ICT 2024 Mentorship "How To Trade ICT FVGs Correctly" -- die **Ausfuehrungs**-Regeln:
    Entry einen Tick vor der nahen Kante (Kerze 3), Stop hinter Kerze 2 (aggressiv) bzw.
    Kerze 1 (konservativ), Quadrantenraster, und als Qualitaetssignal die **ferne Haelfte
    bleibt offen**. Implementiert als Felder von `analyze_ohlc.fvgs()`.

Ausserdem ICTs eigene Groessenvorgabe aus derselben Session: mindestens **20 Handles**
Bewegungspotenzial zwischen Entry und erstem Ziel -- *"if it can't make at least 15 handles
I don't want him to take a trade"*. Deshalb ist das Standardziel hier 20 Punkte fest und
nicht 2R: es ist ICTs Zahl, nicht eine aus der Statistik gefittete.

⚠️ **Der Bias ist ein Proxy, keine Nachbildung.** ICT setzt den Draw on Liquidity von Hand
("you have to know what it's reaching for"). Automatisiert wird hier ersatzweise die
Premium/Discount-Lage des **Midnight Open (0:00 NY)** zur Vortages-Equilibrium genommen:
unter EQ -> bearish, darueber -> bullish. Das ist zum Zeitpunkt 0:00 bekannt (kein
Lookahead), aber es ist *nicht* ICTs Bias. Die Spalte "ohne Bias" steht daneben, damit
sichtbar bleibt, was der Proxy ueberhaupt beitraegt.

⚠️ `far_half_open` ist ein **Ausgangs-**, kein Eingangsfilter: es steht erst nach dem Trade
fest. Es wird deshalb getrennt ausgewiesen und nie mit den Kontextfiltern vermischt.

Aufruf:
    python algo/backtest_hp_fvg.py
    python algo/backtest_hp_fvg.py --stop c1 --ziel 20
    python algo/backtest_hp_fvg.py --selfcheck
"""
from __future__ import annotations

import argparse
import statistics
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "algo"))

from analyze_ohlc import Bar, at, fvgs, hp_context, killzone_of, load  # noqa: E402
from backtest_1p_fvg_woche import find_days  # noqa: E402
from backtest_common import write_result  # noqa: E402
from pnl import POINT_VALUE  # noqa: E402

SYMBOL = "MNQ"
ZIEL_PKT = 20.0        # ICTs eigene Untergrenze fuer den Bewegungsraum
COMMISSION_RT = 1.24   # gleiche Kostenannahme wie backtest_fvg_strength.py


def vortagesrange(tagesdateien: dict[date, Path], tag: date) -> tuple[float, float] | None:
    """(High, Low) des letzten Handelstags VOR `tag` aus dessen 1d-Datei."""
    frueher = [d for d in tagesdateien if d < tag]
    if not frueher:
        return None
    zeilen = load(tagesdateien[max(frueher)])
    return (max(b.h for b in zeilen), min(b.l for b in zeilen)) if zeilen else None


def bias_proxy(bars: list[Bar], tag: date, prev_hi: float, prev_lo: float) -> str | None:
    """Premium/Discount des Midnight Open zur Vortages-Equilibrium. None ohne 0:00-Kerze."""
    mo = next((b.o for b in bars if b.t >= at(tag, 0, 0)), None)
    if mo is None:
        return None
    return "bullish" if mo > (prev_hi + prev_lo) / 2 else "bearish"


def simulate(bars: list[Bar], i: int, g: dict, stop_feld: str, ziel_pkt: float,
             rr: float | None = None) -> dict | None:
    """Limit am `entry`, Stop laut `stop_feld`, Ziel fest in Punkten oder als RR-Vielfaches.

    `rr` setzt das Ziel auf ein Vielfaches des Stopabstands. Noetig fuer den Vergleich
    zwischen Killzones: bei festem Punktziel handelt ein volatiles Fenster mit weitem Stop
    faktisch 1R und ein ruhiges 2R -- die Trefferquoten sind dann nicht vergleichbar.

    None, wenn der Entry nie erreicht wurde -- das ist kein Gewinner, sondern kein Trade.
    Stop und Ziel in derselben Kerze zaehlen konservativ als Verlust und werden als
    `dubious` markiert (CLAUDE.md, Korrektheitsstandard).
    """
    bull = g["side"] == "bullish"
    entry, stop = g["entry"], g[stop_feld]
    risk = abs(entry - stop)
    if risk <= 0:
        return None
    spanne = rr * risk if rr else ziel_pkt
    ziel = entry + spanne if bull else entry - spanne

    gefuellt = False
    for b in bars[i + 2:]:
        if not gefuellt:
            if b.l <= entry <= b.h:
                gefuellt = True
            else:
                continue
        hit_stop = b.l <= stop if bull else b.h >= stop
        hit_ziel = b.h >= ziel if bull else b.l <= ziel
        if hit_stop and hit_ziel:
            return {"won": False, "dubious": True, "pts": -risk}
        if hit_stop:
            return {"won": False, "dubious": False, "pts": -risk}
        if hit_ziel:
            return {"won": True, "dubious": False, "pts": spanne}
    return None if not gefuellt else {"won": None, "dubious": False, "pts": 0.0}


def collect(stop_feld: str, ziel_pkt: float, rr: float | None = None) -> list[dict]:
    m1 = find_days(SYMBOL, "1m")
    d1 = find_days(SYMBOL, "1d")
    rows = []
    for tag, pfad in sorted(m1.items()):
        pr = vortagesrange(d1, tag)
        if not pr:
            continue
        prev_hi, prev_lo = pr
        if prev_hi <= prev_lo:
            continue
        bars = load(pfad)
        bias = bias_proxy(bars, tag, prev_hi, prev_lo)
        for g in fvgs(bars, tick=SYMBOL):
            ctx = hp_context(g, prev_hi, prev_lo, bias)
            rows.append({"tag": tag, "side": g["side"], "size": g["size"],
                         "zone_ok": ctx["zone_ok"], "kz_ok": ctx["kz_ok"],
                         "bias_ok": ctx["bias_ok"], "hp": ctx["hp"],
                         "killzone": ctx["killzone"], "fast": g["fast"],
                         "far_half_open": g["far_half_open"],
                         "risk": abs(g["entry"] - g[stop_feld]),
                         "trade": simulate(bars, g["i"], g, stop_feld, ziel_pkt, rr)})
    return rows


def stats(rows: list[dict]) -> dict:
    done = [r for r in rows if r["trade"] and r["trade"]["won"] is not None]
    dub = [r for r in done if r["trade"]["dubious"]]
    clean = [r for r in done if not r["trade"]["dubious"]]
    pnl = sum(r["trade"]["pts"] * POINT_VALUE[SYMBOL] - COMMISSION_RT for r in done)
    return {
        "n": len(rows), "trades": len(done),
        "median_size": round(statistics.median([r["size"] for r in rows]), 2) if rows else None,
        # Bei festem Punktziel entscheidet der Stopabstand ueber das effektive RR -- ohne
        # diese Spalte liest man Volatilitaetsunterschiede als Kante.
        "median_risk": round(statistics.median([r["risk"] for r in rows]), 2) if rows else None,
        "win_pct": round(100 * sum(r["trade"]["won"] for r in done) / len(done), 1) if done else None,
        "win_pct_ohne_dubious": (round(100 * sum(r["trade"]["won"] for r in clean) / len(clean), 1)
                                 if clean else None),
        "dubious_pct": round(100 * len(dub) / len(done), 1) if done else None,
        "usd_pro_trade": round(pnl / len(done), 2) if done else None,
        "usd_gesamt": round(pnl, 2),
    }


GRUPPEN = [
    ("alle FVG", lambda r: True),
    ("nur Killzone", lambda r: r["kz_ok"]),
    ("nur Vortageshaelfte", lambda r: r["zone_ok"]),
    ("nur Bias-Proxy", lambda r: bool(r["bias_ok"])),
    ("Zone + Killzone", lambda r: r["zone_ok"] and r["kz_ok"]),
    ("HP (alle drei)", lambda r: r["hp"]),
    ("HP + sofort (fast)", lambda r: r["hp"] and r["fast"]),
]


def run(stop_feld: str, ziel_pkt: float, rr: float | None = None) -> dict:
    rows = collect(stop_feld, ziel_pkt, rr)
    out = {"stop": stop_feld, "ziel_pkt": ziel_pkt, "rr": rr, "gruppen": {},
           "killzonen": {}, "ausgangssignal": {}}
    for name, f in GRUPPEN:
        out["gruppen"][name] = stats([r for r in rows if f(r)])
    for kz in sorted({r["killzone"] for r in rows if r["killzone"]}):
        out["killzonen"][kz] = stats([r for r in rows if r["killzone"] == kz])
    # Getrennt, weil far_half_open erst NACH dem Trade feststeht -- kein Eingangsfilter.
    beruehrt = [r for r in rows if r["trade"] and r["trade"]["won"] is not None]
    out["ausgangssignal"]["ferne Haelfte offen"] = stats([r for r in beruehrt if r["far_half_open"]])
    out["ausgangssignal"]["ferne Haelfte verletzt"] = stats(
        [r for r in beruehrt if not r["far_half_open"]])
    return out


def report(res: dict) -> list[str]:
    kopf = (f"  {'Gruppe':<24}{'n':>6}{'Trades':>8}{'Win%':>8}{'ohne dub':>10}"
            f"{'$/Trade':>10}{'$ ges':>11}{'dub%':>7}{'Med Risk':>10}")

    def zeile(name, s):
        if not s["trades"]:
            return f"  {name:<24}{s['n']:>6}{'0':>8}"
        return (f"  {name:<24}{s['n']:>6}{s['trades']:>8}{s['win_pct']:>8}"
                f"{s['win_pct_ohne_dubious']:>10}{s['usd_pro_trade']:>10}"
                f"{s['usd_gesamt']:>11}{s['dubious_pct']:>7}{s['median_risk']:>10}")

    ziel = f"Ziel {res['rr']:g}R" if res.get("rr") else f"Ziel {res['ziel_pkt']:g} Pkt"
    L = [f"=== High-Probability-FVG {SYMBOL} (Stop {res['stop']}, {ziel}) ===",
         "", "Kontextfilter (alle zum Entry bekannt):", kopf]
    L += [zeile(n, s) for n, s in res["gruppen"].items()]
    L += ["", "Nach Killzone:", kopf]
    L += [zeile(n, s) for n, s in res["killzonen"].items()]
    L += ["", "Ausgangssignal (KEIN Eingangsfilter -- steht erst nach dem Trade fest):", kopf]
    L += [zeile(n, s) for n, s in res["ausgangssignal"].items()]
    return L


def selfcheck() -> None:
    t = datetime(2026, 1, 1, 3, 0)
    b = lambda o, h, l, c, tt=t: Bar(t=tt, o=o, h=h, l=l, c=c)  # noqa: E731
    assert killzone_of(t) == "London"

    # Gewinner: Entry 104.25, Ziel +20 = 124.25, Stop unter Kerze 2
    bars = [b(99, 100, 98, 99.75), b(99.75, 105, 99.5, 104.75), b(104.75, 106, 104, 105.5),
            b(105, 104.5, 104.0, 104.25), b(104.25, 125, 104.0, 124.5)]
    g = fvgs(bars, tick=SYMBOL)[0]
    tr = simulate(bars, g["i"], g, "stop_c2", 20.0)
    assert tr and tr["won"] is True and not tr["dubious"], (tr, g)

    # Stop und Ziel in derselben Kerze -> konservativ Verlust, als dubious markiert
    bars2 = bars[:3] + [b(105, 125, 99, 104.25)]
    g2 = fvgs(bars2, tick=SYMBOL)[0]
    tr2 = simulate(bars2, g2["i"], g2, "stop_c2", 20.0)
    assert tr2 and tr2["won"] is False and tr2["dubious"], (tr2, g2)

    # Entry nie erreicht -> None, nicht "Gewinn"
    bars3 = bars[:3] + [b(200, 201, 199, 200.5)]
    g3 = fvgs(bars3, tick=SYMBOL)[0]
    assert simulate(bars3, g3["i"], g3, "stop_c2", 20.0) is None

    # hp_context: bearishes Gap in der oberen Vortageshaelfte ist NICHT HP
    ctx = hp_context({"side": "bearish", "ce": 110.0, "t": t}, 120.0, 80.0, "bearish")
    assert not ctx["zone_ok"] and not ctx["hp"], ctx

    # stats() darf ohne Trades nicht durch 0 teilen
    s = stats([{"size": 5.0, "risk": 3.0, "trade": None, "far_half_open": False}])
    assert s["trades"] == 0 and s["win_pct"] is None, s
    print("selfcheck ok")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stop", choices=["c2", "c1"], default="c2",
                    help="c2 = aggressiv hinter Kerze 2, c1 = konservativ hinter Kerze 1")
    ap.add_argument("--ziel", type=float, default=ZIEL_PKT)
    ap.add_argument("--rr", type=float, default=None,
                    help="Ziel als RR-Vielfaches statt fester Punkte (fairer Killzone-Vergleich)")
    ap.add_argument("--selfcheck", action="store_true")
    a = ap.parse_args(argv)
    if a.selfcheck:
        selfcheck()
        return 0
    res = run(f"stop_{a.stop}", a.ziel, a.rr)
    print("\n".join(report(res)))
    write_result(f"hp_fvg_{'rr' + format(a.rr, 'g') if a.rr else 'pkt'}", res)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
