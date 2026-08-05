#!/usr/bin/env python3
"""Walk-Forward, Monte-Carlo und Parameter-Sensitivitaet fuer SilverBulletStrategy
(algo/backtest_bt.py, Regel aus algo/rules.py). Nutzerauftrag: diese drei Verfahren als
Standard-Backtestwerkzeuge hinterlegen, nicht nur die einmalige `bt.run()`-Zahl aus
backtest_bt.py.

Datengrundlage: dieselben 5m-Tagesdateien wie backtest_bt.py -- aktuell n=42 Handelstage
(2026-06-08 bis 2026-08-04). Das ist bereits das yfinance-Limit fuer 5m (~60 Tage rueckwirkend,
siehe algo/fetch_yfinance.py); ein erneuter Download-Versuch fuer mehr Historie lieferte 0 neue
Dateien -- mehr Intraday-Historie ist ohne eine zweite Datenquelle nicht zu bekommen. Mit ~97
Trades insgesamt und noch weniger je Fold sind alle drei Analysen hier explizit
Groessenordnungs-Schaetzungen, keine belastbaren Ergebnisse.

1. Parameter-Sensitivitaet: rastert stop_buffer_pct (siehe rules.py::plan_trade, PLAN.md
   "Stop-Puffer vergroessern/testen") ueber bt.optimize(), zeigt Profit Factor/Win Rate/Trades
   je Wert.
2. Walk-Forward: Tage in rollierende Folds geteilt. Je Fold: In-Sample (bester
   stop_buffer_pct per Grid-Search) -> Out-of-Sample (derselbe Wert auf dem naechsten,
   ungesehenen Fold, kein Refit). Rollierend statt expandierend, weil ein wachsendes Fenster
   bei nur 42 Tagen die letzten Folds ohnehin fast auf denselben Daten liefe.
3. Monte Carlo: die 97 Trade-Returns der Baseline (Standardparameter) 1000x mit Zuruecklegen
   resampled -- Verteilung von kumulierter Rendite und Max Drawdown, zeigt wie sehr das
   Ergebnis von der zufaelligen Trade-Reihenfolge abhaengt statt von echtem Edge.

# ponytail: ein einzelner bt.run() ueber die vollen 42 Tage (~11000 5m-Kerzen) dauert
# gemessen ~3-3.5 Minuten (SilverBulletStrategy.next() baut bei jeder Kerze die Bar-Liste neu
# auf, siehe backtest_bt.py -- nicht hier geaendert, ein Cache waere ein Umbau der Regel-
# Schicht). Sensitivitaet + Walk-Forward brauchen dutzende Laeufe (teils auf kleineren
# Fold-Ausschnitten, entsprechend schneller) -- als Hintergrundlauf einplanen (~20-30 Min
# gesamt), nicht interaktiv warten.

Aufruf:
    python algo/backtest_walkforward.py MNQ
"""
from __future__ import annotations

import random
import sys
from pathlib import Path

import pandas as pd
from backtesting import Backtest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from backtest_bt import load_series, SilverBulletStrategy  # noqa: E402

STOP_BUFFER_CANDIDATES = [0.05, 0.1, 0.2, 0.3, 0.5]
BT_KWARGS = dict(cash=100_000, margin=0.05, commission=0.0002)


def run(df: pd.DataFrame, stop_buffer_pct: float) -> pd.Series:
    SilverBulletStrategy.stop_buffer_pct = stop_buffer_pct
    return Backtest(df, SilverBulletStrategy, **BT_KWARGS).run()


# --- 1. Parameter-Sensitivitaet ---------------------------------------------------------

def parameter_sensitivity(df: pd.DataFrame, baseline: pd.Series | None = None) -> None:
    print("1. Parameter-Sensitivitaet (stop_buffer_pct, Anteil der FVG-Groesse als SL-Puffer)")
    print(f"   {'pct':>6}  {'Trades':>7}  {'WinRate%':>9}  {'ProfitFactor':>13}  {'Expectancy%':>12}")
    for pct in STOP_BUFFER_CANDIDATES:
        stats = baseline if (baseline is not None and pct == 0.1) else run(df, pct)
        pf = stats["Profit Factor"]
        pf_str = f"{pf:.3f}" if pf == pf else "n/a"  # NaN bei 0 Verlust-Trades
        print(f"   {pct:>6.2f}  {stats['# Trades']:>7}  {stats['Win Rate [%]']:>9.1f}  "
              f"{pf_str:>13}  {stats['Expectancy [%]']:>12.3f}")


# --- 2. Walk-Forward ---------------------------------------------------------------------

def slice_days(df: pd.DataFrame, days: list) -> pd.DataFrame:
    day_set = set(days)
    return df[[d in day_set for d in df.index.date]]


def walk_forward(df: pd.DataFrame, n_folds: int = 6) -> None:
    all_days = sorted(set(df.index.date))
    fold_len = len(all_days) // n_folds
    if fold_len < 2:
        print(f"2. Walk-Forward uebersprungen: nur {len(all_days)} Handelstage, "
              f"zu wenig fuer {n_folds} Folds.")
        return
    folds = [all_days[i * fold_len:(i + 1) * fold_len] for i in range(n_folds)]
    folds[-1] = folds[-1] + all_days[n_folds * fold_len:]  # Rest an letzten Fold

    print(f"2. Walk-Forward ({n_folds} rollierende Folds, ~{fold_len} Handelstage je Fold)")
    print(f"   {'Fold':>4}  {'IS bester pct':>13}  {'OOS Trades':>10}  "
          f"{'OOS WinRate%':>12}  {'OOS ProfitFactor':>16}  {'OOS Expectancy%':>15}")
    oos_returns = []
    for i in range(n_folds - 1):
        train, test = slice_days(df, folds[i]), slice_days(df, folds[i + 1])
        if train.empty or test.empty:
            continue
        best_pct, best_pf = STOP_BUFFER_CANDIDATES[0], -1.0
        for pct in STOP_BUFFER_CANDIDATES:
            s = run(train, pct)
            pf = s["Profit Factor"]
            if pf == pf and pf > best_pf:  # pf==pf verwirft NaN
                best_pf, best_pct = pf, pct
        oos = run(test, best_pct)
        oos_pf = oos["Profit Factor"]
        oos_pf_str = f"{oos_pf:.3f}" if oos_pf == oos_pf else "n/a"
        print(f"   {i + 1:>4}  {best_pct:>13.2f}  {oos['# Trades']:>10}  "
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


# --- 3. Monte Carlo ------------------------------------------------------------------------

def monte_carlo(df: pd.DataFrame, baseline: pd.Series, n_sims: int = 1000, seed: int = 42) -> None:
    returns = baseline._trades["ReturnPct"].tolist()
    n = len(returns)
    print(f"3. Monte Carlo (Baseline stop_buffer_pct=0.10, n={n} Trades, {n_sims} Resamples "
          f"der Trade-Reihenfolge)")
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

    def pctl(lst: list[float], p: float) -> float:
        return lst[int(p / 100 * (len(lst) - 1))]

    print(f"   Kumulierte Rendite:   5.%={100*pctl(finals,5):+.1f}%  "
          f"50.%={100*pctl(finals,50):+.1f}%  95.%={100*pctl(finals,95):+.1f}%")
    print(f"   Max. Drawdown:        5.%={100*pctl(max_dds,5):.1f}%  "
          f"50.%={100*pctl(max_dds,50):.1f}%  95.%={100*pctl(max_dds,95):.1f}%")


def main(argv=None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    symbol = args[0] if args else None
    sys.stdout.reconfigure(encoding="utf-8")

    df = load_series(symbol)
    all_days = sorted(set(df.index.date))
    print(f"{len(df)} Kerzen, {len(all_days)} Handelstage ({all_days[0]} bis {all_days[-1]})")
    print("Kleine Stichprobe -- alle Zahlen unten sind Groessenordnungen, keine belastbaren "
          "Ergebnisse (siehe Docstring).\n")

    baseline = run(df, 0.1)  # einmal rechnen, in Sensitivitaet + Monte Carlo wiederverwendet
    parameter_sensitivity(df, baseline)
    print()
    walk_forward(df)
    print()
    monte_carlo(df, baseline)
    return 0


if __name__ == "__main__":
    sys.exit(main())
