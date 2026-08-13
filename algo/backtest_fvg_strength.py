#!/usr/bin/env python3
"""Backtest zu Jannes' FVG-Staerke-Thesen vom 13.08.2026.

Getestet werden vier Behauptungen:

  T1  Die FVG-Groesse haengt an Session/Volatilitaet -- kurz nach 9:30 sind die Kerzen
      deutlich groesser als in London, Richtung NY PM faellt die Vola wieder auf
      London-Niveau. Folge fuer den Algo: "gross" darf keine absolute Punktzahl sein.
  T2  Ein starkes FVG bricht einen Swing High/Low (MSS/BOS) -- bereits in
      analyze_ohlc.fvgs() implementiert, hier auf Trefferquote geprueft.
  T3  Groesse zaehlt zusaetzlich: grosses FVG + MSS/BOS = High Probability.
  T4  Ueberlappung mit einer Higher-Timeframe-PD-Array (deren Qs/C.E.) oder mit
      NDOG/NWOG hebt die Wahrscheinlichkeit weiter.

Ergebnis-Metrik ist ein echter Trade, kein Prozent-auf-Notional (siehe CLAUDE.md
"Korrektheit vor Features"): Limit-Entry am C.E. des FVG, Stop an der fernen Kante,
Ziel = 2R. P&L in echten Dollar ueber pnl.POINT_VALUE. Kerzen, in denen Stop UND Ziel
liegen, gelten konservativ als Verlust und werden als `dubious_pct` ausgewiesen.

Kein Lookahead: Volatilitaet und Confluence stammen ausschliesslich aus Kerzen vor dem
FVG bzw. aus Arrays, die zum Zeitpunkt des FVG bereits fertig waren.

Aufruf:
    python algo/backtest_fvg_strength.py            # voller Lauf ueber raw/marktdaten
    python algo/backtest_fvg_strength.py --selfcheck
"""
from __future__ import annotations

import argparse
import statistics
import sys
from collections import defaultdict
from datetime import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from analyze_ohlc import Bar, fvgs, load, ndog_gap, to_tick  # noqa: E402
from backtest_common import find_days, write_result  # noqa: E402
from pnl import POINT_VALUE  # noqa: E402
from qoh_levels import grid  # noqa: E402

SYMBOL = "MNQ"
VOL_LOOKBACK = 30      # Kerzen vor dem FVG fuer die lokale Volatilitaet
RR = 2.0               # Ziel in Vielfachen des Risikos (C.E. -> ferne Kante)

# Sessions nach Jannes' Aufteilung -- der 9:30-Open bewusst als eigenes Fenster, weil
# genau dort die These "viel groessere Kerzen" haengt.
SESSIONS = [
    ("Asia",        time(18, 0), time(23, 59)),
    ("Asia",        time(0, 0),  time(3, 0)),
    ("London",      time(3, 0),  time(8, 30)),
    ("Premarket",   time(8, 30), time(9, 30)),
    ("NY Open",     time(9, 30), time(10, 30)),
    ("NY AM",       time(10, 30), time(12, 0)),
    ("Lunch",       time(12, 0), time(13, 30)),
    ("NY PM",       time(13, 30), time(16, 0)),
]


def session_of(t) -> str:
    for name, a, b in SESSIONS:
        if a <= t.time() < b or (b == time(23, 59) and t.time() >= a):
            return name
    return "Off"


def local_vol(bars: list[Bar], i: int) -> float:
    """Median-Kerzenrange der `VOL_LOOKBACK` Kerzen VOR dem FVG. Der Massstab, an dem
    sich 'gross' misst -- absolute Punkte sind sessionabhaengig wertlos (T1)."""
    prev = bars[max(0, i - VOL_LOOKBACK):i]
    rng = [b.rng for b in prev if b.rng > 0]
    return statistics.median(rng) if rng else 0.0


def higher_tf_levels(day_dir: Path, upto) -> list[float]:
    """Qs + Kanten aller Higher-TF-FVGs, die vor `upto` fertig waren. Das sind die
    Level, mit denen ein 1m-FVG ueberlappen kann (T4)."""
    out: list[float] = []
    for tf in ("15m", "1h"):
        files = sorted(day_dir.glob(f"{SYMBOL} * {tf}.csv"))
        if not files:
            continue
        for g in fvgs(load(files[0]), tick=SYMBOL):
            if g["t_end"] >= upto:          # noch nicht bestaetigt -> waere Lookahead
                continue
            out += [p for _, stufe, _, p in grid(g["hi"], g["lo"], SYMBOL)
                    if stufe == "Qs"]
    return out


def simulate(bars: list[Bar], i: int, g: dict) -> dict | None:
    """Limit-Entry am C.E., Stop an der fernen Kante, Ziel 2R. None, wenn der C.E. nie
    erreicht wurde (dann gab es keinen Trade, nicht etwa einen Gewinner)."""
    bull = g["side"] == "bullish"
    entry = g["ce"]
    stop = g["lo"] if bull else g["hi"]
    risk = abs(entry - stop)
    if risk <= 0:
        return None
    target = to_tick(entry + RR * risk if bull else entry - RR * risk, SYMBOL)

    filled = False
    for b in bars[i + 2:]:
        if not filled:
            if b.l <= entry <= b.h:
                filled = True
            else:
                continue
        hit_stop = b.l <= stop if bull else b.h >= stop
        hit_target = b.h >= target if bull else b.l <= target
        if hit_stop and hit_target:
            return {"won": False, "dubious": True, "pts": -risk}
        if hit_stop:
            return {"won": False, "dubious": False, "pts": -risk}
        if hit_target:
            return {"won": True, "dubious": False, "pts": RR * risk}
    return None if not filled else {"won": None, "dubious": False, "pts": 0.0}


def collect() -> list[dict]:
    rows = []
    for day, path in find_days(SYMBOL, "1m"):
        bars = load(path)
        if len(bars) < VOL_LOOKBACK + 3:
            continue
        day_dir = path.parent
        gap = ndog_gap(bars, day)
        ndog_levels = [gap["prev_close"], gap["today_open"]] if gap else []

        for g in fvgs(bars, tick=SYMBOL):
            i = g["i"]
            vol = local_vol(bars, i)
            if vol <= 0:
                continue
            hi_levels = higher_tf_levels(day_dir, g["t_end"])
            rows.append({
                "day": str(day),
                "t": g["t"].strftime("%Y-%m-%d %H:%M"),
                "session": session_of(g["t"]),
                "side": g["side"],
                "size": g["size"],
                "size_rel": g["size"] / vol,
                "vol": vol,
                "strong": bool(g["strong"]),
                "ms": g["ms"],
                "htf": any(g["lo"] <= p <= g["hi"] for p in hi_levels),
                "ndog": any(g["lo"] <= p <= g["hi"] for p in ndog_levels),
                "trade": simulate(bars, i, g),
            })
    return rows


def _stats(rows: list[dict]) -> dict:
    done = [r for r in rows if r["trade"] and r["trade"]["won"] is not None]
    if not done:
        return {"n_fvg": len(rows), "n_trades": 0}
    wins = [r for r in done if r["trade"]["won"]]
    pts = sum(r["trade"]["pts"] for r in done)
    dub = [r for r in done if r["trade"]["dubious"]]
    # Sensitivitaet: kleine FVGs loesen Stop UND Ziel viel haeufiger in derselben 1m-Kerze
    # auf als grosse. Da die konservative Regel die alle als Verlust wertet, koennte der
    # Groesseneffekt ein Messartefakt sein -- darum die Quote ohne die strittigen Faelle.
    clean = [r for r in done if not r["trade"]["dubious"]]
    return {
        "n_fvg": len(rows),
        "n_trades": len(done),
        "win_rate": round(100 * len(wins) / len(done), 1),
        "win_rate_ohne_dubious": (round(100 * sum(r["trade"]["won"] for r in clean)
                                        / len(clean), 1) if clean else None),
        "pnl_usd": round(pts * POINT_VALUE[SYMBOL], 2),
        "pnl_per_trade_usd": round(pts * POINT_VALUE[SYMBOL] / len(done), 2),
        "dubious_pct": round(100 * len(dub) / len(done), 1),
    }


def run() -> dict:
    rows = collect()
    big = statistics.median([r["size_rel"] for r in rows]) if rows else 0.0

    by_session = {}
    for name in dict.fromkeys(n for n, _, _ in SESSIONS):
        sel = [r for r in rows if r["session"] == name]
        if sel:
            by_session[name] = {
                "n": len(sel),
                "median_size_pts": round(statistics.median(r["size"] for r in sel), 2),
                "median_vol_pts": round(statistics.median(r["vol"] for r in sel), 2),
                "median_size_rel": round(statistics.median(r["size_rel"] for r in sel), 2),
            }

    groups = {
        "alle": rows,
        "normal": [r for r in rows if not r["strong"]],
        "stark (Swing-Break)": [r for r in rows if r["strong"]],
        "stark + gross": [r for r in rows if r["strong"] and r["size_rel"] >= big],
        "stark + gross + HTF-Qs": [r for r in rows if r["strong"] and r["size_rel"] >= big
                                   and r["htf"]],
        "stark + gross + NDOG": [r for r in rows if r["strong"] and r["size_rel"] >= big
                                 and r["ndog"]],
        "nur gross": [r for r in rows if r["size_rel"] >= big],
        "nur HTF-Qs": [r for r in rows if r["htf"]],
        "MSS/BOS-Event": [r for r in rows if r["ms"]],
    }
    return {
        "symbol": SYMBOL, "rr": RR, "vol_lookback": VOL_LOOKBACK,
        "median_size_rel": round(big, 2),
        "days": len({r["day"] for r in rows}),
        "sessions": by_session,
        "groups": {k: _stats(v) for k, v in groups.items()},
    }


def selfcheck() -> None:
    """Synthetik: ein bullishes FVG, dessen C.E. spaeter angelaufen wird und dann das
    2R-Ziel erreicht -- muss als Gewinner mit +2R zaehlen."""
    from datetime import datetime, timedelta
    T = datetime(2026, 1, 1, 9, 30)
    rows = [(100, 101, 99, 100)] * 3 + [(100, 101, 99, 100),
                                        (101, 110, 100, 109), (109, 112, 108, 111)]
    bars = [Bar(t=T + timedelta(minutes=k), o=o, h=h, l=lo, c=c)
            for k, (o, h, lo, c) in enumerate(rows)]
    g = next(x for x in fvgs(bars, tick=SYMBOL) if x["side"] == "bullish")
    # Ruecklauf auf den C.E. und danach durch das Ziel
    ce, lo_edge = g["ce"], g["lo"]
    risk = ce - lo_edge
    bars += [Bar(t=bars[-1].t + timedelta(minutes=1), o=ce, h=ce, l=ce - 0.25, c=ce),
             Bar(t=bars[-1].t + timedelta(minutes=2), o=ce, h=ce + 3 * risk,
                 l=ce, c=ce + 3 * risk)]
    tr = simulate(bars, g["i"], g)
    assert tr and tr["won"] is True and not tr["dubious"], tr
    assert abs(tr["pts"] - RR * risk) < 1e-9, tr

    # Stop und Ziel in derselben Kerze -> konservativ Verlust, als dubious markiert
    bars2 = bars[:-1] + [Bar(t=bars[-1].t, o=ce, h=ce + 3 * risk, l=lo_edge - 1,
                             c=ce)]
    tr2 = simulate(bars2, g["i"], g)
    assert tr2 and tr2["won"] is False and tr2["dubious"], tr2
    assert session_of(datetime(2026, 1, 1, 9, 45)) == "NY Open"
    assert session_of(datetime(2026, 1, 1, 4, 0)) == "London"
    assert session_of(datetime(2026, 1, 1, 20, 0)) == "Asia"
    print("backtest_fvg_strength.selfcheck: OK")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selfcheck", action="store_true")
    if ap.parse_args().selfcheck:
        selfcheck()
        return
    res = run()
    write_result("fvg_strength", res)
    print(f"{SYMBOL} 1m, {res['days']} Handelstage, Median size_rel = {res['median_size_rel']}\n")
    print(f"{'Session':<11}{'n FVG':>7}{'Median Groesse':>16}{'Median Kerze':>14}{'x Kerze':>9}")
    for name, s in res["sessions"].items():
        print(f"{name:<11}{s['n']:>7}{s['median_size_pts']:>16.2f}"
              f"{s['median_vol_pts']:>14.2f}{s['median_size_rel']:>9.2f}")
    print(f"\n{'Gruppe':<26}{'n FVG':>7}{'Trades':>8}{'Win%':>7}{'Win% o.dub':>11}"
          f"{'$/Trade':>10}{'$ ges.':>11}{'dubious%':>10}")
    for name, s in res["groups"].items():
        if not s.get("n_trades"):
            print(f"{name:<26}{s['n_fvg']:>7}{0:>8}{'-':>7}{'-':>11}{'-':>10}{'-':>11}{'-':>10}")
            continue
        print(f"{name:<26}{s['n_fvg']:>7}{s['n_trades']:>8}{s['win_rate']:>7.1f}"
              f"{s['win_rate_ohne_dubious']:>11.1f}{s['pnl_per_trade_usd']:>10.2f}"
              f"{s['pnl_usd']:>11.2f}{s['dubious_pct']:>10.1f}")


if __name__ == "__main__":
    main()
