#!/usr/bin/env python3
"""These (Jannes, 2026-08-14): Das 1.p FVG der NY-AM-Session nach dem Opening Range Gap
muss eine **absolute Mindestgroesse** haben -- genannt: mindestens 10 Punkte. Kleinere
Kandidaten seien kein gueltiges 1.p FVG.

Im Vault gibt es dafuer bisher **keine Quelle**: die einzigen "10 Handle" im Bestand sind
ICTs *Mindestziel* fuer NASDAQ-Scalps und Jannes' eigene Setup-Regel (Entry->Target >= 10
Punkte Potenzial) -- beides eine Aussage ueber den **Move**, nicht ueber die FVG-Groesse.
Gegenposition steht in wiki/synthesis/FVG-Staerke, Session-Volatilitaet & Confluence
(laufend).md: ein Groessen-Schwellwert gehoert relativ zur Session-Volatilitaet, nie auf
feste Punkte.

Dieses Skript misst daher zwei Dinge:

  (A) **Verteilung**: wie gross ist das 1.p FVG der NY AM tatsaechlich? Wie viel Prozent
      der Tage haetten mit einer 10-Punkte-Untergrenze gar kein 1.p FVG mehr?
  (B) **Kante**: bringt der Filter etwas? Limit-Entry am C.E., Stop an der fernen Kante,
      Ziel 2R -- identisch zu backtest_fvg_strength.py, dessen simulate() wiederverwendet
      wird, damit die Zahlen vergleichbar bleiben.

Zwei Lesarten des "1.p" werden getrennt ausgewiesen, weil das Wiki beide kennt:
  - **chrono**: das erste FVG mit kompletter 3-Kerzen-Formation im Fenster.
  - **max**:    das groesste FVG des Fensters ("1. presented *Displacement*").

Bekannte Grenzen: Trefferquoten mit Stop+Ziel in derselben 1m-Kerze zaehlen konservativ
als Verlust und stehen als `dubious%` daneben. n ist tagesbasiert (ein 1.p pro Tag), also
klein -- die Verteilung (A) traegt, die Kante (B) ist bei diesen Fallzahlen bestenfalls
ein Hinweis.

Aufruf:
    python algo/backtest_1p_mindestgroesse.py
    python algo/backtest_1p_mindestgroesse.py --schwelle 10 --ende 10:00
    python algo/backtest_1p_mindestgroesse.py --selfcheck
"""
from __future__ import annotations

import argparse
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "algo"))

from analyze_ohlc import Bar, at, fvgs, load  # noqa: E402
from backtest_1p_fvg_woche import find_days  # noqa: E402
from backtest_common import write_result  # noqa: E402
from backtest_fvg_strength import COMMISSION_RT, simulate  # noqa: E402
from pnl import POINT_VALUE  # noqa: E402

SYMBOL = "MNQ"
START = (9, 30)


def window_fvgs(bars: list[Bar], day, ende: tuple[int, int]) -> tuple[list[dict], list[Bar]]:
    """FVGs, deren komplette 3-Kerzen-Formation im Fenster liegt, plus die Fensterkerzen.

    fvgs() nur auf das Fenster anzuwenden ist genau die Wiki-Regel: ein FVG, dessen
    mittlere Kerze auf 9:30 faellt, beginnt um 9:29 und zaehlt nicht.
    """
    win = [b for b in bars if at(day, *START) <= b.t < at(day, *ende)]
    return (fvgs(win, tick=SYMBOL) if len(win) >= 3 else []), win


def pick(found: list[dict], modus: str) -> dict | None:
    if not found:
        return None
    return found[0] if modus == "chrono" else max(found, key=lambda g: g["size"])


def collect(ende: tuple[int, int], tf: str = "1m") -> list[dict]:
    rows = []
    for day, path in sorted(find_days(SYMBOL, tf).items()):
        bars = load(path)
        found, win = window_fvgs(bars, day, ende)
        if not found:
            continue
        # Ausfuehrung ueber den ganzen Resttag messen, nicht nur im Fenster -- sonst wird
        # jeder Trade kuenstlich bei 10:00 abgeschnitten.
        rest = [b for b in bars if b.t >= at(day, *START)]
        for modus in ("chrono", "max"):
            g = pick(found, modus)
            i = next((k for k, b in enumerate(rest) if b.t == g["t"]), None)
            if i is None:
                continue
            rows.append({"day": day, "modus": modus, "size": g["size"],
                         "size_rel": g.get("size_rel"), "side": g["side"],
                         "trade": simulate(rest, i, g)})
    return rows


def stats(rows: list[dict]) -> dict:
    sizes = [r["size"] for r in rows]
    done = [r for r in rows if r["trade"] and r["trade"]["won"] is not None]
    dub = [r for r in done if r["trade"]["dubious"]]
    clean = [r for r in done if not r["trade"]["dubious"]]
    pnl = sum(r["trade"]["pts"] * POINT_VALUE[SYMBOL] - COMMISSION_RT for r in done)
    q = statistics.quantiles(sizes, n=4) if len(sizes) > 1 else [0, 0, 0]
    return {
        "n": len(rows),
        "median": round(statistics.median(sizes), 2) if sizes else 0.0,
        "q25": round(q[0], 2), "q75": round(q[2], 2),
        "min": round(min(sizes), 2) if sizes else 0.0,
        "max": round(max(sizes), 2) if sizes else 0.0,
        "trades": len(done),
        "win_pct": round(100 * sum(r["trade"]["won"] for r in done) / len(done), 1) if done else None,
        "win_pct_ohne_dubious": (round(100 * sum(r["trade"]["won"] for r in clean) / len(clean), 1)
                                 if clean else None),
        "dubious_pct": round(100 * len(dub) / len(done), 1) if done else None,
        "usd_pro_trade": round(pnl / len(done), 2) if done else None,
        "usd_gesamt": round(pnl, 2),
    }


def run(ende: tuple[int, int], schwelle: float, tf: str) -> dict:
    rows = collect(ende, tf)
    out = {"fenster": f"{START[0]}:{START[1]:02d}-{ende[0]}:{ende[1]:02d}",
           "schwelle_pkt": schwelle, "tf": tf, "gruppen": {}}
    for modus in ("chrono", "max"):
        sel = [r for r in rows if r["modus"] == modus]
        unter = [r for r in sel if r["size"] < schwelle]
        out["gruppen"][modus] = {
            "alle": stats(sel),
            f"unter_{schwelle:g}": stats(unter) if unter else None,
            f"ab_{schwelle:g}": stats([r for r in sel if r["size"] >= schwelle]) or None,
            "anteil_unter_schwelle_pct": round(100 * len(unter) / len(sel), 1) if sel else None,
        }
    return out


def report(res: dict) -> list[str]:
    L = [f"=== 1.p FVG {SYMBOL} NY AM, Fenster {res['fenster']} ({res['tf']}) ===",
         f"Schwelle der These: {res['schwelle_pkt']:g} Punkte", ""]
    for modus, g in res["gruppen"].items():
        titel = ("chronologisch erstes FVG" if modus == "chrono"
                 else "groesstes FVG des Fensters (1. presented Displacement)")
        L += [f"-- {titel} --",
              f"  Tage mit 1.p FVG: {g['alle']['n']}",
              f"  Groesse: Median {g['alle']['median']} Pkt "
              f"(Q25 {g['alle']['q25']} / Q75 {g['alle']['q75']}, "
              f"min {g['alle']['min']} / max {g['alle']['max']})",
              f"  unter {res['schwelle_pkt']:g} Pkt: {g['anteil_unter_schwelle_pct']} % der Tage", ""]
        L.append(f"  {'Gruppe':<16}{'n':>4}{'Trades':>8}{'Win%':>8}{'ohne dub':>10}"
                 f"{'$/Trade':>10}{'$ ges':>10}{'dub%':>8}")
        for key in ("alle", f"unter_{res['schwelle_pkt']:g}", f"ab_{res['schwelle_pkt']:g}"):
            s = g.get(key)
            if not s or not s["n"]:
                L.append(f"  {key:<16}{'-':>4}")
                continue
            L.append(f"  {key:<16}{s['n']:>4}{s['trades']:>8}"
                     f"{(s['win_pct'] if s['win_pct'] is not None else float('nan')):>8}"
                     f"{(s['win_pct_ohne_dubious'] if s['win_pct_ohne_dubious'] is not None else float('nan')):>10}"
                     f"{(s['usd_pro_trade'] if s['usd_pro_trade'] is not None else float('nan')):>10}"
                     f"{s['usd_gesamt']:>10}"
                     f"{(s['dubious_pct'] if s['dubious_pct'] is not None else float('nan')):>8}")
        L.append("")
    return L


def selfcheck() -> None:
    # pick() muss bei "max" das groesste nehmen, auch wenn es das letzte ist -- genau der
    # Fall aus SMC Midnight Opening Range (Source), wo das 1.p das letzte FVG der Range ist
    found = [{"size": 2.0, "t": 1}, {"size": 9.0, "t": 3}]
    assert pick(found, "chrono")["t"] == 1
    assert pick(found, "max")["t"] == 3
    assert pick([], "max") is None
    # stats() darf bei leerer Trade-Liste nicht durch 0 teilen
    s = stats([{"size": 5.0, "trade": None}])
    assert s["n"] == 1 and s["trades"] == 0 and s["win_pct"] is None, s
    print("selfcheck ok")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--schwelle", type=float, default=10.0, help="Mindestgroesse in Punkten")
    ap.add_argument("--ende", default="10:00", help="Fensterende NY, HH:MM")
    ap.add_argument("--tf", default="1m")
    ap.add_argument("--selfcheck", action="store_true")
    a = ap.parse_args(argv)
    if a.selfcheck:
        selfcheck()
        return 0
    ende = tuple(int(x) for x in a.ende.split(":"))
    res = run(ende, a.schwelle, a.tf)
    print("\n".join(report(res)))
    write_result("1p_mindestgroesse", res)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
