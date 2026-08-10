#!/usr/bin/env python3
"""Konfidenz-/Bar-Renditen-Report -- verdrahtet den masters.py-Werkzeugkasten (Kapitel 6) in
die algo/backtest_*.py-Reports. Loest die Backlog-Punkte 7 (Bar- statt Trade-Renditen) und
9a (BCa-Untergrenze statt reiner Punktschaetzer) aus algo/PLAN.md.

Warum getrennt von masters.py: masters.py bleibt die reine Portierung der Buchverfahren,
dieses Modul ist die projektspezifische Verdrahtung -- es kennt die Spalten der
`backtesting`-Lib (`stats._trades`: EntryBar/ExitBar/Size/ReturnPct) und die
Report-Formatierung. So bleibt masters.py backtesting-Lib-unabhaengig und einzeln testbar.

Kernaussage des Reports (Masters Kap. 6): auf Trade-Basis gerechnete Kennzahlen sind
systematisch extremer als bar-basierte (sein Beispiel: Profit Factor unendlich statt 1,01),
und ein reiner Punktschaetzer sagt nichts darueber, ob die Zahl ueberhaupt von null zu
unterscheiden ist -- dafuer die einseitige BCa-Untergrenze.
"""
from __future__ import annotations

import math

import numpy as np

from masters import (bar_returns_from_trades, profit_factor, log_profit_factor,
                     sharpe_ratio, lower_bound_t, lower_bound_bca)


def _fmt(x, nd: int = 3) -> str:
    """NaN-sichere Zahlenformatierung fuer den Report (Bar-Kennzahlen sind NaN, wenn es keine
    Bars mit offener Position gibt)."""
    if x is None or (isinstance(x, float) and x != x):
        return "n/a"
    return f"{x:.{nd}f}"


def bar_metrics(trades, df, n_resamples: int = 10_000, seed: int | None = 20260811) -> dict:
    """Kennzahlen auf BAR- und TRADE-Basis plus einseitige 95%-Untergrenzen fuer die
    mittlere Bar-Rendite.

    `trades` = `stats._trades` der `backtesting`-Lib (braucht EntryBar/ExitBar/Size/ReturnPct),
    `df`     = exakt die Bars-DataFrame, die an `Backtest()` ging (Spalte 'Close').

    BCa nur, wenn >=8 Bars vorliegen UND sowohl Gewinn- als auch Verlust-Bars existieren --
    sonst ist die Bootstrap-Verteilung entartet. Der t-Test laeuft schon ab 2 Bars, ist aber
    laut Masters bei einem einzigen wilden Ausreisser wertlos; darum steht die BCa-Zahl
    daneben, sobald sie berechenbar ist."""
    trade_ret = np.asarray(trades["ReturnPct"], dtype=float)
    bar_ret = bar_returns_from_trades(trades, df, only_open=True)
    out: dict = {
        "n_trades": int(trade_ret.size),
        "n_bars": int(bar_ret.size),
        "pf_trade": profit_factor(trade_ret) if trade_ret.size else float("nan"),
        "pf_bar": profit_factor(bar_ret) if bar_ret.size else float("nan"),
        "sharpe_trade": sharpe_ratio(trade_ret) if trade_ret.size > 1 else float("nan"),
        "sharpe_bar": sharpe_ratio(bar_ret) if bar_ret.size > 1 else float("nan"),
    }
    if bar_ret.size >= 2:
        mean, t, pval, lb_t = lower_bound_t(bar_ret)
        out.update(mean_bar=mean, t=t, pval=pval, lb_mean_t=lb_t)
        if bar_ret.size >= 8 and np.any(bar_ret > 0) and np.any(bar_ret < 0):
            rng = np.random.default_rng(seed)
            out["lb_mean_bca"] = lower_bound_bca(bar_ret, np.mean,
                                                 n_resamples=n_resamples, rng=rng)
            out["lb_logpf_bca"] = lower_bound_bca(bar_ret, log_profit_factor,
                                                  n_resamples=n_resamples, rng=rng)
            out["pf_lower_bca"] = math.exp(out["lb_logpf_bca"])
    return out


def print_bar_metrics(d: dict) -> None:
    """Formatiert das Ergebnis von bar_metrics() als Report-Block."""
    print("\nBar- vs. Trade-Kennzahlen (Masters Kap. 6 -- Trade-basiert ist systematisch "
          "extremer):")
    print(f"   n: {d['n_trades']} Trades, {d['n_bars']} Bars mit offener Position")
    print(f"   Profit Factor:  Trade {_fmt(d['pf_trade'])}   Bar {_fmt(d['pf_bar'])}")
    print(f"   Sharpe (roh):   Trade {_fmt(d['sharpe_trade'])}   Bar {_fmt(d['sharpe_bar'])}")
    if "mean_bar" not in d:
        print("   Zu wenig Bars fuer eine Untergrenze der mittleren Bar-Rendite.")
        return
    print(f"   Mittlere Bar-Rendite {d['mean_bar'] * 100:+.4f}%   t={d['t']:.2f}   "
          f"p={d['pval']:.3f}  (einseitig, H0: wahres Mittel <= 0)")
    if "lb_mean_bca" in d:
        verdict = ("> 0 -> von null unterscheidbar" if d["lb_mean_bca"] > 0
                   else "<= 0 -> NICHT von null unterscheidbar")
        print(f"   95%-Untergrenze Mittel:  t-Test {d['lb_mean_t'] * 100:+.4f}%   "
              f"BCa {d['lb_mean_bca'] * 100:+.4f}%  ({verdict})")
        print(f"   95%-Untergrenze Profit Factor (BCa auf log PF): {d['pf_lower_bca']:.3f}")
    else:
        print(f"   95%-Untergrenze Mittel (t-Test): {d['lb_mean_t'] * 100:+.4f}%   "
              f"(BCa uebersprungen: <8 Bars oder nur eine Vorzeichenklasse)")


def demo() -> None:
    """Selbstcheck fuer algo/selfcheck.py: baut kuenstliche Trades + Bars und prueft, dass
    bar_metrics() sinnvolle Werte liefert und die dokumentierten Kernaussagen halten.
    Bewusst kleines n_resamples, damit der Check schnell bleibt."""
    import pandas as pd

    # 20 Bars, deterministischer Close-Pfad mit klarer Aufwaertstendenz + Ruecksetzern.
    rng = np.random.default_rng(0)
    close = 100.0 * np.exp(np.cumsum(rng.normal(0.002, 0.01, 20)))
    df = pd.DataFrame({"Open": close, "High": close, "Low": close, "Close": close})

    # Zwei long-Trades, jeweils ueber mehrere Bars gehalten (Size > 0 = long).
    trades = pd.DataFrame({
        "EntryBar": [1, 11], "ExitBar": [8, 18], "Size": [1, 1],
        "ReturnPct": [(close[8] / close[1] - 1), (close[18] / close[11] - 1)],
    })

    d = bar_metrics(trades, df, n_resamples=500)
    assert d["n_trades"] == 2, d
    # only_open=True: Bars 1..7 und 11..17 mit offener Position -> 14 Bar-Renditen.
    assert d["n_bars"] == 14, d["n_bars"]
    # Bar-basierte Bar-Renditen != Trade-Renditen -> Profit Factor unterscheidet sich.
    assert d["pf_bar"] == d["pf_bar"], "pf_bar darf nicht NaN sein"
    assert "mean_bar" in d and "lb_mean_t" in d, "t-Untergrenze muss ab 2 Bars da sein"
    # Untergrenze <= Punktschaetzer (per Konstruktion einer einseitigen Untergrenze).
    assert d["lb_mean_t"] <= d["mean_bar"] + 1e-12, (d["lb_mean_t"], d["mean_bar"])
    if "lb_mean_bca" in d:
        assert d["pf_lower_bca"] > 0, d["pf_lower_bca"]

    # Kein Bar mit offener Position -> nur Trade-Kennzahlen, keine Bar-Untergrenze.
    empty = pd.DataFrame({"EntryBar": [], "ExitBar": [], "Size": [], "ReturnPct": []})
    d2 = bar_metrics(empty, df, n_resamples=200)
    assert d2["n_bars"] == 0 and "mean_bar" not in d2, d2
    print("confidence.demo: OK")


if __name__ == "__main__":
    demo()
