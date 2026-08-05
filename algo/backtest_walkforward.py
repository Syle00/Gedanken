#!/usr/bin/env python3
"""Duenner Wrapper um algo/validate.py fuer SilverBulletStrategy -- Verhalten/Ausgabe
identisch zur Vorgaenger-Version (Regressionscheck: siehe
docs/superpowers/plans/2026-08-05-algo-rentec-ensemble.md Task 7). Die generalisierten
Walk-Forward/Monte-Carlo/Parameter-Sensitivitaet-Funktionen leben jetzt in validate.py und
werden auch von algo/validate_ensemble.py genutzt.

Aufruf:
    python algo/backtest_walkforward.py MNQ
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from backtest_bt import load_series, SilverBulletStrategy  # noqa: E402
from validate import run, parameter_sensitivity, walk_forward, monte_carlo  # noqa: E402

STOP_BUFFER_CANDIDATES = [0.05, 0.1, 0.2, 0.3, 0.5]
BT_KWARGS = dict(cash=100_000, margin=0.05, commission=0.0002)


def main(argv=None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    symbol = args[0] if args else None
    sys.stdout.reconfigure(encoding="utf-8")

    df = load_series(symbol)
    all_days = sorted(set(df.index.date))
    print(f"{len(df)} Kerzen, {len(all_days)} Handelstage ({all_days[0]} bis {all_days[-1]})")
    print("Kleine Stichprobe -- alle Zahlen unten sind Groessenordnungen, keine belastbaren "
          "Ergebnisse (siehe Docstring).\n")

    baseline = run(df, SilverBulletStrategy, BT_KWARGS, "stop_buffer_pct", 0.1)
    # fmt reproduziert wortwoertlich das Format der Vorgaenger-Version (siehe
    # validate.py-Docstring) -- fuer den Byte-Identisch-Regressionscheck in Task 7 notwendig.
    pct_value_fmt = lambda v: f"{v:.2f}"  # noqa: E731
    parameter_sensitivity(df, SilverBulletStrategy, "stop_buffer_pct", STOP_BUFFER_CANDIDATES,
                           BT_KWARGS, baseline=baseline, baseline_value=0.1,
                           fmt={"title": "stop_buffer_pct, Anteil der FVG-Groesse als SL-Puffer",
                                "col_label": "pct", "col_width": 6, "value_fmt": pct_value_fmt})
    print()
    walk_forward(df, SilverBulletStrategy, "stop_buffer_pct", STOP_BUFFER_CANDIDATES, BT_KWARGS,
                 fmt={"col_label": "IS bester pct", "col_width": 13, "value_fmt": pct_value_fmt})
    print()
    monte_carlo(baseline, fmt={"header_prefix": "Baseline stop_buffer_pct=0.10, "})
    return 0


if __name__ == "__main__":
    sys.exit(main())
