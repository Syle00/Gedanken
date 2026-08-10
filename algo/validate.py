#!/usr/bin/env python3
"""Generalisierte Walk-Forward/Monte-Carlo/Parameter-Sensitivitaet -- geloest von
SilverBulletStrategy (frueher hart in backtest_walkforward.py), damit dieselben drei
Verfahren auch fuer EnsembleStrategy (algo/validate_ensemble.py) laufen. Verhalten fuer
den SilverBulletStrategy-Fall bleibt unveraendert (siehe Regressionscheck in Task 7 des
Implementierungsplans docs/superpowers/plans/2026-08-05-algo-rentec-ensemble.md).

`on_fold_train(train_df) -> dict` ist ein optionaler Hook: statt eines Parameter-Grids wird
er vor jedem Walk-Forward-Fold aufgerufen und liefert Attribut-Name/Wert-Paare, die auf die
Strategie-Klasse gesetzt werden (z.B. ein frisch gefittetes Modell) -- ersetzt die
In-Sample-Grid-Search fuer Strategien, deren "Parameter" kein Skalar ist.

Der optionale `fmt`-Dict-Parameter ist ein reiner Text-/Format-Override mit generischen
Defaults; er existiert, damit backtest_walkforward.py (SilverBulletStrategy, Skalarparameter
stop_buffer_pct) Wort-fuer-Wort dieselbe Ausgabe wie vor dem Refactor erzeugt. Ohne ihn
faellt man auf eine generische Beschriftung zurueck (siehe Defaults unten).
"""
from __future__ import annotations

import random

import numpy as np
import pandas as pd
from backtesting import Backtest
from pnl import dubious_pct
from masters import drawdown_bound, dd_to_pct


def run(df: pd.DataFrame, strategy_cls, bt_kwargs: dict, param_name: str | None = None,
        param_value=None, on_fold_train=None, train_df: pd.DataFrame | None = None):
    if on_fold_train is not None and train_df is not None:
        for name, value in on_fold_train(train_df).items():
            setattr(strategy_cls, name, value)
    elif param_name is not None:
        setattr(strategy_cls, param_name, param_value)
    return Backtest(df, strategy_cls, **bt_kwargs).run()


def parameter_sensitivity(df, strategy_cls, param_name: str, candidates: list,
                           bt_kwargs: dict, baseline=None, baseline_value=None,
                           fmt: dict | None = None) -> None:
    fmt = fmt or {}
    title = fmt.get("title", param_name)
    col_label = fmt.get("col_label", "value")
    col_width = fmt.get("col_width", 8)
    value_fmt = fmt.get("value_fmt")
    print(f"1. Parameter-Sensitivitaet ({title})")
    print(f"   {col_label:>{col_width}}  {'Trades':>7}  {'WinRate%':>9}  {'ProfitFactor':>13}  "
          f"{'Expectancy%':>12}  {'Dubious%':>9}")
    for value in candidates:
        stats = baseline if (baseline is not None and value == baseline_value) else \
            run(df, strategy_cls, bt_kwargs, param_name, value)
        pf = stats["Profit Factor"]
        pf_str = f"{pf:.3f}" if pf == pf else "n/a"
        value_str = value_fmt(value) if value_fmt else str(value)
        print(f"   {value_str:>{col_width}}  {stats['# Trades']:>7}  {stats['Win Rate [%]']:>9.1f}  "
              f"{pf_str:>13}  {stats['Expectancy [%]']:>12.3f}  {dubious_pct(stats._trades):>9.1f}")


def slice_days(df: pd.DataFrame, days: list) -> pd.DataFrame:
    day_set = set(days)
    return df[[d in day_set for d in df.index.date]]


def walk_forward(df, strategy_cls, param_name: str | None, candidates: list | None,
                  bt_kwargs: dict, n_folds: int = 6, on_fold_train=None,
                  fmt: dict | None = None, omit: int = 0) -> list[float]:
    """`omit` = Guard Buffer nach Masters (siehe algo/masters.py::guard_buffer): so viele
    juengste Handelstage werden am ENDE des Trainingsfolds gestrichen, damit keine seriell
    korrelierte Information ueber den direkt anschliessenden Testfold ins Training leckt.

    Default 0, und das ist fuer die beiden bestehenden Strategien nachweislich korrekt, nicht
    nur bequem: guard_buffer = min(Lookback, Lookahead) - 1, und der Lookahead ist hier 1 --
    SilverBulletStrategy entscheidet pro Kerze nur aus bars[t<=when] innerhalb eines harten
    1h-Fensters (kein tagesuebergreifender Zustand), und die Ensemble-Zielgroesse ist die
    Richtung des Folgetags (signals.py::build_features: y[i] = Tag i+1), also Lookahead genau
    1 -> omit 0. Wird die Zielgroesse spaeter auf einen Mehrtageshorizont H erweitert, hier
    omit=H-1 setzen, sonst werden alle Signifikanztests anti-konservativ. Bei omit=0 ist die
    Ausgabe byte-identisch zur Version vor dem Guard-Buffer-Parameter."""
    fmt = fmt or {}
    is_col_label = fmt.get("col_label")
    is_col_width = fmt.get("col_width", 16)
    is_value_fmt = fmt.get("value_fmt")
    all_days = sorted(set(df.index.date))
    fold_len = len(all_days) // n_folds
    if fold_len < 2:
        print(f"2. Walk-Forward uebersprungen: nur {len(all_days)} Handelstage, "
              f"zu wenig fuer {n_folds} Folds.")
        return []
    folds = [all_days[i * fold_len:(i + 1) * fold_len] for i in range(n_folds)]
    folds[-1] = folds[-1] + all_days[n_folds * fold_len:]

    print(f"2. Walk-Forward ({n_folds} rollierende Folds, ~{fold_len} Handelstage je Fold"
          + (f", Guard Buffer omit={omit}" if omit else "") + ")")
    header = is_col_label if is_col_label is not None else ("IS " + (param_name or "Modell"))
    print(f"   {'Fold':>4}  {header:>{is_col_width}}  {'OOS Trades':>10}  "
          f"{'OOS WinRate%':>12}  {'OOS ProfitFactor':>16}  {'OOS Expectancy%':>15}  {'OOS Dubious%':>13}")
    oos_returns = []
    for i in range(n_folds - 1):
        train_days = folds[i][:-omit] if omit else folds[i]   # Guard Buffer: Trailing-Tage streichen
        train, test = slice_days(df, train_days), slice_days(df, folds[i + 1])
        if train.empty or test.empty:
            continue
        if on_fold_train is not None:
            fold_label = "Modell"
            oos = run(test, strategy_cls, bt_kwargs, on_fold_train=on_fold_train, train_df=train)
        else:
            best_value, best_pf = candidates[0], -1.0
            for value in candidates:
                s = run(train, strategy_cls, bt_kwargs, param_name, value)
                pf = s["Profit Factor"]
                if pf == pf and pf > best_pf:
                    best_pf, best_value = pf, value
            fold_label = is_value_fmt(best_value) if is_value_fmt else best_value
            oos = run(test, strategy_cls, bt_kwargs, param_name, best_value)
        oos_pf = oos["Profit Factor"]
        oos_pf_str = f"{oos_pf:.3f}" if oos_pf == oos_pf else "n/a"
        print(f"   {i + 1:>4}  {fold_label!s:>{is_col_width}}  {oos['# Trades']:>10}  "
              f"{oos['Win Rate [%]']:>12.1f}  {oos_pf_str:>16}  {oos['Expectancy [%]']:>15.3f}  "
              f"{dubious_pct(oos._trades):>13.1f}")
        if oos["# Trades"] > 0:
            oos_returns.extend(oos._trades["ReturnPct"].tolist())
    if oos_returns:
        compounded = 1.0
        for r in oos_returns:
            compounded *= (1 + r)
        print(f"   Alle Out-of-Sample-Folds zusammen: n={len(oos_returns)} Trades, "
              f"kumulierte Rendite {100 * (compounded - 1):+.2f}%")
    else:
        print("   Keine Out-of-Sample-Trades in irgendeinem Fold.")
    return oos_returns


def monte_carlo(baseline, n_sims: int = 1000, seed: int = 42, fmt: dict | None = None) -> None:
    header_prefix = (fmt or {}).get("header_prefix", "")
    returns = baseline._trades["ReturnPct"].tolist()
    n = len(returns)
    print(f"3. Monte Carlo ({header_prefix}n={n} Trades, {n_sims} Resamples der Trade-Reihenfolge)")
    print(f"   Baseline mehrdeutige Trades (Stop/Ziel in derselben Kerze, Fill-Reihenfolge "
          f"unbekannt): {dubious_pct(baseline._trades):.1f}%")
    if n < 10:
        print(f"   Zu wenig Trades (n={n}) fuer eine aussagekraeftige Verteilung.")
        return
    rng = random.Random(seed)
    finals, max_dds = [], []
    for _ in range(n_sims):
        sample = rng.choices(returns, k=n)
        equity = peak = 1.0
        max_dd = 0.0
        for r in sample:
            equity *= (1 + r)
            peak = max(peak, equity)
            max_dd = max(max_dd, (peak - equity) / peak)
        finals.append(equity - 1)
        max_dds.append(max_dd)
    finals.sort()
    max_dds.sort()

    def pctl(lst, p):
        return lst[int(p / 100 * (len(lst) - 1))]

    print(f"   Kumulierte Rendite:   5.%={100*pctl(finals,5):+.1f}%  "
          f"50.%={100*pctl(finals,50):+.1f}%  95.%={100*pctl(finals,95):+.1f}%")
    print(f"   Max. Drawdown (naiv): 5.%={100*pctl(max_dds,5):.1f}%  "
          f"50.%={100*pctl(max_dds,50):.1f}%  95.%={100*pctl(max_dds,95):.1f}%")

    # Backlog 9b (siehe algo/PLAN.md): die Zeile darueber ist exakt der von Masters als
    # "incorrect" bezeichnete naive Drawdown-Bootstrap -- er erfasst nur die Zusammensetzung
    # kuenftiger Trades, ignoriert aber, dass die OOS-Stichprobe selbst eine Zufallsziehung
    # ist, und unterschaetzt das Risiko dadurch systematisch (bei kleiner Stichprobe bis
    # Faktor 13,65). Fuer Kapitalentscheidungen gilt die korrekte Doppel-Bootstrap-Grenze:
    dd95, dd99 = double_bootstrap_drawdown(returns, seed=seed)
    print(f"   Max. Drawdown (Doppel-Bootstrap, korrekt): dd_conf=0,95 -> {dd95:.1f}%  "
          f"dd_conf=0,99 -> {dd99:.1f}%  (bound_conf=0,8, Horizont n={n} Trades)")


def double_bootstrap_drawdown(returns, seed: int = 42, dd_conf=(0.95, 0.99),
                               bound_conf: float = 0.8) -> tuple[float, ...]:
    """Korrekte Doppel-Bootstrap-Drawdown-Grenze(n) in Prozent (Masters Kap. 6, delegiert an
    masters.drawdown_bound). Getrennt von monte_carlo(), damit selfcheck.py sie ohne ein
    backtesting-Stats-Objekt pruefen kann.

    Trade-Renditen werden per log1p in additive Log-Aenderungen ueberfuehrt (masters.drawdown
    rechnet additiv, damit es auch bei negativem Eigenkapital gilt). Der Horizont ist die
    beobachtete Trade-Zahl."""
    changes = np.log1p(np.asarray(returns, dtype=float))
    n = changes.size
    return tuple(
        dd_to_pct(drawdown_bound(changes, n, dd_conf=c, bound_conf=bound_conf,
                                 rng=np.random.default_rng(seed)))
        for c in dd_conf
    )


def demo() -> None:
    """Selbstcheck fuer algo/selfcheck.py: die Doppel-Bootstrap-Grenze muss konservativer
    (groesser) sein als der naive Bootstrap -- das ist der ganze Grund fuer Backlog 9b."""
    from masters import drawdown_bound_naive
    rng_r = np.random.default_rng(7)
    returns = rng_r.normal(-0.001, 0.02, 60).tolist()   # 60 leicht verlustige Trades
    changes = np.log1p(np.asarray(returns))
    naive = dd_to_pct(drawdown_bound_naive(changes, len(returns), 0.95,
                                           rng=np.random.default_rng(9)))
    dd95, dd99 = double_bootstrap_drawdown(returns, seed=9)
    assert dd95 > naive, f"Doppel-Bootstrap {dd95:.2f}% muss > naiv {naive:.2f}% sein"
    assert dd99 >= dd95, f"dd_conf=0,99 ({dd99:.2f}%) muss >= dd_conf=0,95 ({dd95:.2f}%) sein"
    print("validate.demo: OK (Doppel-Bootstrap konservativer als naiv)")


if __name__ == "__main__":
    demo()
