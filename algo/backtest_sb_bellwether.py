#!/usr/bin/env python3
"""Testet Jannes' Timeframe-These (2026-08-14, siehe wiki/concepts/Open Float & Liquidity
Pools.md, "Timeframe-Wahl zur Pool-Erkennung"): 15m als Bellwether-Chart, 1m fuer grosse/gute
Liquidity Pools -- bezogen auf das Silver Bullet Model (algo/rules.py::plan_trade).

Haelt Entry/Stop (5m-FVG im SB-Fenster) UNVERAENDERT und variiert nur die Bar-Reihe, aus der
`untouched_levels()` die Ziel-Liquiditaet zieht (`plan_trade(..., levels_bars=...)`,
2026-08-14 in rules.py ergaenzt, Default None = altes Verhalten). Reuse-first: Entry-Logik
und Ziel-Erkennung kommen unveraendert aus rules.py/analyze_ohlc.py, hier nur die
Trade-Simulation (Konvention wie backtest_hp_fvg.py::simulate -- konservative Fill-Reihenfolge,
dubious bei Stop+Ziel in derselben Kerze).

Nur Tage gezaehlt, an denen 1m, 5m UND 15m gleichzeitig vorliegen (1m begrenzt via yfinance auf
~30 Tage) -- sonst waeren die drei Varianten nicht auf denselben Trades vergleichbar. Bei
Silver-Bullet-Basisrate von ~16 Trades/100 Tage bedeutet das eine SEHR kleine Stichprobe;
das Ergebnis ist entsprechend vorsichtig zu lesen (siehe Report-Fussnote).

Aufruf:
    python algo/backtest_sb_bellwether.py
    python algo/backtest_sb_bellwether.py --selfcheck
"""
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "algo"))

from analyze_ohlc import Bar, at, load  # noqa: E402
from backtest_1p_fvg_woche import find_days  # noqa: E402
from backtest_common import write_result  # noqa: E402
from pnl import POINT_VALUE  # noqa: E402
from rules import WINDOWS, plan_trade  # noqa: E402

SYMBOL = "MNQ"
COMMISSION_RT = 1.24  # gleiche Kostenannahme wie backtest_hp_fvg.py


def load_concat(days: dict[date, Path]) -> list[Bar]:
    bars: list[Bar] = []
    for d in sorted(days):
        bars.extend(load(days[d]))
    bars.sort(key=lambda b: b.t)
    return bars


def find_entry(bars_5m: list[Bar], day: date, win_start_h: int, win_end_h: int) -> object:
    """Erstes plan_trade()-Signal (Baseline-Levels, 5m) innerhalb des Fensters an diesem Tag,
    oder None. Baseline = levels_bars=None -> exakt das bisherige SB-Verhalten."""
    win_bars = [b for b in bars_5m if at(day, win_start_h) <= b.t < at(day, win_end_h)]
    for b in win_bars:
        setup = plan_trade(bars_5m, b.t)
        if setup is not None:
            return setup
    return None


def simulate(bars_5m: list[Bar], after_t, side: str, entry: float, stop: float,
             target: float) -> dict | None:
    """Wie backtest_hp_fvg.simulate: Limit-Fill am Entry, danach konservatives Stop/Ziel-Rennen
    auf 5m-Kerzen. None = Entry nie erreicht (kein Trade, kein Verlierer)."""
    bull = side == "long"
    future = [b for b in bars_5m if b.t > after_t]
    gefuellt = False
    for b in future:
        if not gefuellt:
            if b.l <= entry <= b.h:
                gefuellt = True
            else:
                continue
        hit_stop = b.l <= stop if bull else b.h >= stop
        hit_ziel = b.h >= target if bull else b.l <= target
        if hit_stop and hit_ziel:
            return {"won": False, "dubious": True, "pts": -abs(entry - stop)}
        if hit_stop:
            return {"won": False, "dubious": False, "pts": -abs(entry - stop)}
        if hit_ziel:
            return {"won": True, "dubious": False, "pts": abs(target - entry)}
    return None


def collect() -> list[dict]:
    d5 = find_days(SYMBOL, "5m")
    d15 = find_days(SYMBOL, "15m")
    d1 = find_days(SYMBOL, "1m")
    common = sorted(set(d5) & set(d15) & set(d1))
    if not common:
        return []

    bars_5m = load_concat({d: d5[d] for d in common})
    bars_15m = load_concat({d: d15[d] for d in common})
    bars_1m = load_concat({d: d1[d] for d in common})

    rows = []
    for day in common:
        for name, h0, h1 in WINDOWS:
            entry_setup = find_entry(bars_5m, day, h0, h1)
            if entry_setup is None:
                continue  # kein FVG mit gueltiger 5m-Zielliquiditaet -> auch fuer die anderen
                          # Varianten irrelevant, denn Entry/Stop stammen aus derselben Quelle
            side, entry, stop = entry_setup.side, entry_setup.entry, entry_setup.stop
            when = entry_setup.t

            for variant, lvl_bars in (("5m (Baseline)", None), ("15m (Bellwether)", bars_15m),
                                       ("1m (grosse Pools)", bars_1m)):
                s = plan_trade(bars_5m, when, levels_bars=lvl_bars)
                if s is None:
                    rows.append({"day": day, "window": name, "variant": variant,
                                 "target": None, "trade": None})
                    continue
                trade = simulate(bars_5m, when, side, entry, stop, s.target)
                rows.append({"day": day, "window": name, "variant": variant,
                             "target": s.target, "trade": trade})
    return rows


def stats(rows: list[dict]) -> dict:
    kein_ziel = sum(1 for r in rows if r["target"] is None)
    done = [r for r in rows if r["trade"] and r["trade"]["won"] is not None]
    dub = [r for r in done if r["trade"]["dubious"]]
    pnl = sum(r["trade"]["pts"] * POINT_VALUE[SYMBOL] - COMMISSION_RT for r in done)
    return {
        "tage_x_fenster": len(rows), "ohne_zielliquiditaet": kein_ziel,
        "trades": len(done),
        "win_pct": round(100 * sum(r["trade"]["won"] for r in done) / len(done), 1) if done else None,
        "dubious_pct": round(100 * len(dub) / len(done), 1) if done else None,
        "usd_pro_trade": round(pnl / len(done), 2) if done else None,
        "usd_gesamt": round(pnl, 2),
    }


def run() -> dict:
    rows = collect()
    tage = sorted({r["day"] for r in rows}) if rows else []
    out = {"symbol": SYMBOL, "tage_mit_1m+5m+15m": len(tage), "varianten": {}}
    for variant in ("5m (Baseline)", "15m (Bellwether)", "1m (grosse Pools)"):
        out["varianten"][variant] = stats([r for r in rows if r["variant"] == variant])
    return out


def report(res: dict) -> list[str]:
    L = [f"=== Silver Bullet: Ziel-Liquiditaet nach Timeframe ({res['symbol']}) ===", "",
         f"Tage mit gleichzeitig 1m+5m+15m-Daten: {res['tage_mit_1m+5m+15m']} "
         "(begrenzt durch yfinance-1m-Limit ~30 Tage)", "",
         f"  {'Variante':<20}{'Fenster':>9}{'ohne Ziel':>11}{'Trades':>8}{'Win%':>7}"
         f"{'dub%':>6}{'$/Trade':>10}{'$ ges':>9}"]
    for name, s in res["varianten"].items():
        if not s["trades"]:
            L.append(f"  {name:<20}{s['tage_x_fenster']:>9}{s['ohne_zielliquiditaet']:>11}"
                      f"{'0':>8}")
            continue
        L.append(f"  {name:<20}{s['tage_x_fenster']:>9}{s['ohne_zielliquiditaet']:>11}"
                  f"{s['trades']:>8}{s['win_pct']:>7}{s['dubious_pct']:>6}"
                  f"{s['usd_pro_trade']:>10}{s['usd_gesamt']:>9}")
    n = max((s["trades"] for s in res["varianten"].values()), default=0)
    if n < 20:
        L += ["", f"⚠️  n={n} Trades in der groessten Variante -- bei dieser Groesse ist "
              "keine der Varianten von Rauschen unterscheidbar (siehe CLAUDE.md,\n"
              "   'Proaktiv gegenpruefen'). Ergebnis als vorlaeufig behandeln, nicht als "
              "entschiedene These."]
    return L


def selfcheck() -> None:
    day = date(2026, 1, 5)
    bar = lambda hh, mm, o, h, l, c: Bar(at(day, hh, mm), o, h, l, c)  # noqa: E731
    bars = [
        bar(9, 55, 97, 97.5, 96.5, 97.2),
        bar(10, 0, 97.2, 98, 97, 97.8),
        bar(10, 5, 97.8, 101, 97.4, 100),
        bar(10, 10, 100, 102, 99, 101),
        bar(10, 15, 101, 102, 98, 99),        # Retracement zurueck in die FVG-Zone (Entry 98.5)
        bar(10, 20, 99, 111, 98.5, 110),      # fuellt Entry, laeuft zum Ziel 110
    ]
    # Padding VOR und NACH dem Spike: swings() verlangt n=2 Nachbarn auf beiden Seiten
    # (analyze_ohlc.swings), ein Randbalken kann also nie als Swing erkannt werden.
    padding_vor = [bar(9, 15, 95, 95.5, 94.5, 95), bar(9, 20, 95, 95.5, 94.5, 95.2)]
    padding_nach = [bar(9, 35, 96, 96.5, 95.5, 96), bar(9, 40, 96, 96.5, 95.5, 96),
                     bar(9, 45, 96, 96.5, 95.5, 96), bar(9, 50, 96, 96.5, 95.5, 96)]
    spike = (padding_vor + [bar(9, 30, 95.5, 110, 95, 96)] + padding_nach
             + bars)  # unberuehrte Buyside 110
    setup = plan_trade(spike, at(day, 10, 10))
    assert setup is not None and setup.target == 110
    tr = simulate(spike, setup.t, setup.side, setup.entry, setup.stop, setup.target)
    assert tr is not None and tr["won"] is True, tr

    # levels_bars mit identischer Reihe -> gleiches Ergebnis (Reuse-Kontrakt aus rules.py)
    s2 = plan_trade(spike, at(day, 10, 10), levels_bars=spike)
    assert s2 is not None and s2.target == setup.target
    print("selfcheck ok")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selfcheck", action="store_true")
    a = ap.parse_args(argv)
    if a.selfcheck:
        selfcheck()
        return 0
    res = run()
    print("\n".join(report(res)))
    write_result("sb_bellwether", res)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
