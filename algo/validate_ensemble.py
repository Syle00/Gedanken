#!/usr/bin/env python3
"""Duenner Wrapper um algo/validate.py fuer EnsembleStrategy -- nutzt den on_fold_train-
Hook um vor jedem Walk-Forward-Fold ein neues LogisticRegression-Modell NUR auf den
In-Sample-Tagen zu fitten (kein statischer Fit auf allen Daten, siehe
docs/superpowers/specs/2026-08-05-algo-rentec-ensemble-design.md Phase 2/3).

Aufruf:
    python algo/validate_ensemble.py MNQ
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from backtest_bt import load_series  # noqa: E402
from backtest_ensemble import EnsembleStrategy, fit_model, bias_series  # noqa: E402
from backtest_seasonal import load_rows  # noqa: E402
from validate import run, walk_forward, monte_carlo  # noqa: E402

BT_KWARGS = dict(cash=100_000, margin=0.05, commission=0.0002)


MIN_HISTORY = 25  # muss zu backtest_ensemble.bias_series()'s Default passen


def _make_fold_hook(es_rows: list[dict], mnq_rows: list[dict]):
    def on_fold_train(train_df: pd.DataFrame) -> dict:
        train_days = set(train_df.index.date)
        fold_mnq = [r for r in mnq_rows if r["day"] in train_days]
        fold_es = [r for r in es_rows if r["day"] in train_days]
        if len(fold_mnq) - 1 <= MIN_HISTORY:
            # build_features() liefert bei so wenigen In-Sample-Tagen keine einzige Zeile
            # (range(min_history, len(rows)-1) waere leer) -- LogisticRegression.fit() auf
            # leerem X wuerde crashen. Leerer Bias = neutral fuer den ganzen Fold (0 OOS-Trades),
            # analog zu validate.py's eigenem "zu wenig Handelstage"-Skip.
            return {"bias": {}}
        # Fit NUR auf dem In-Sample-Fold (kein Lookahead in den Fit). bias_series() dagegen
        # bekommt die vollen mnq_rows/es_rows: signals.py::_row_features schaut pro Tag i nur
        # rueckwaerts (mnq_rows[:i+1]), daher liefert der breitere Tagesbereich lediglich mehr
        # Vorhersagen desselben (fold-gefitteten) Modells -- u.a. fuer die OOS-Testtage, ohne
        # die je einziges Feature in die Zukunft schauen zu lassen. Mit fold_mnq/fold_es waeren
        # alle target_days zwangslaeufig im Trainingsfold selbst (build_features() nimmt
        # mnq_rows[i+1] als target), sodass der OOS-Backtest nie einen Bias-Treffer haette.
        model = fit_model(fold_mnq, fold_es)
        return {"bias": bias_series(model, mnq_rows, es_rows)}
    return on_fold_train


def main(argv=None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    symbol = args[0] if args else None
    sys.stdout.reconfigure(encoding="utf-8")

    df = load_series(symbol)
    all_days = sorted(set(df.index.date))
    print(f"{len(df)} Kerzen, {len(all_days)} Handelstage ({all_days[0]} bis {all_days[-1]})")
    print("Kleine Stichprobe (~150 Tage, 8 Features) -- Overfitting-Risiko trotz "
          "Regularisierung, siehe backtest_ensemble.py Docstring.\n")

    mnq_rows, es_rows = load_rows("MNQ"), load_rows("ES")
    model = fit_model(mnq_rows, es_rows)
    EnsembleStrategy.bias = bias_series(model, mnq_rows, es_rows)
    EnsembleStrategy.intraday = True
    baseline = run(df, EnsembleStrategy, BT_KWARGS)
    print(baseline)
    print()
    walk_forward(df, EnsembleStrategy, None, None, BT_KWARGS,
                 on_fold_train=_make_fold_hook(es_rows, mnq_rows))
    print()
    monte_carlo(baseline)
    return 0


if __name__ == "__main__":
    sys.exit(main())
