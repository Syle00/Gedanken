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

Die `title`/`col_label`/`col_width`/`value_fmt`/`is_col_label`/`is_col_width`/`is_value_fmt`/
`header_prefix`-Parameter sind reine Text-/Format-Overrides mit generischen Defaults; sie
existieren, damit backtest_walkforward.py (SilverBulletStrategy, Skalarparameter
stop_buffer_pct) Wort-fuer-Wort dieselbe Ausgabe wie vor dem Refactor erzeugt. Ohne sie
faellt man auf eine generische Beschriftung zurueck (siehe Defaults unten).
"""
from __future__ import annotations

import random

import pandas as pd
from backtesting import Backtest


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
                           title: str | None = None, col_label: str = "value",
                           col_width: int = 8, value_fmt=None) -> None:
    print(f"1. Parameter-Sensitivitaet ({title if title is not None else param_name})")
    print(f"   {col_label:>{col_width}}  {'Trades':>7}  {'WinRate%':>9}  {'ProfitFactor':>13}  {'Expectancy%':>12}")
    for value in candidates:
        stats = baseline if (baseline is not None and value == baseline_value) else \
            run(df, strategy_cls, bt_kwargs, param_name, value)
        pf = stats["Profit Factor"]
        pf_str = f"{pf:.3f}" if pf == pf else "n/a"
        value_str = value_fmt(value) if value_fmt else str(value)
        print(f"   {value_str:>{col_width}}  {stats['# Trades']:>7}  {stats['Win Rate [%]']:>9.1f}  "
              f"{pf_str:>13}  {stats['Expectancy [%]']:>12.3f}")


def slice_days(df: pd.DataFrame, days: list) -> pd.DataFrame:
    day_set = set(days)
    return df[[d in day_set for d in df.index.date]]


def walk_forward(df, strategy_cls, param_name: str | None, candidates: list | None,
                  bt_kwargs: dict, n_folds: int = 6, on_fold_train=None,
                  is_col_label: str | None = None, is_col_width: int = 16,
                  is_value_fmt=None) -> list[float]:
    all_days = sorted(set(df.index.date))
    fold_len = len(all_days) // n_folds
    if fold_len < 2:
        print(f"2. Walk-Forward uebersprungen: nur {len(all_days)} Handelstage, "
              f"zu wenig fuer {n_folds} Folds.")
        return []
    folds = [all_days[i * fold_len:(i + 1) * fold_len] for i in range(n_folds)]
    folds[-1] = folds[-1] + all_days[n_folds * fold_len:]

    print(f"2. Walk-Forward ({n_folds} rollierende Folds, ~{fold_len} Handelstage je Fold)")
    header = is_col_label if is_col_label is not None else ("IS " + (param_name or "Modell"))
    print(f"   {'Fold':>4}  {header:>{is_col_width}}  {'OOS Trades':>10}  "
          f"{'OOS WinRate%':>12}  {'OOS ProfitFactor':>16}  {'OOS Expectancy%':>15}")
    oos_returns = []
    for i in range(n_folds - 1):
        train, test = slice_days(df, folds[i]), slice_days(df, folds[i + 1])
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
              f"{oos['Win Rate [%]']:>12.1f}  {oos_pf_str:>16}  {oos['Expectancy [%]']:>15.3f}")
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


def monte_carlo(baseline, n_sims: int = 1000, seed: int = 42, header_prefix: str = "") -> None:
    returns = baseline._trades["ReturnPct"].tolist()
    n = len(returns)
    print(f"3. Monte Carlo ({header_prefix}n={n} Trades, {n_sims} Resamples der Trade-Reihenfolge)")
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
    print(f"   Max. Drawdown:        5.%={100*pctl(max_dds,5):.1f}%  "
          f"50.%={100*pctl(max_dds,50):.1f}%  95.%={100*pctl(max_dds,95):.1f}%")
