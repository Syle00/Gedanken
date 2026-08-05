#!/usr/bin/env python3
"""Stress-Test: EnsembleStrategy(intraday=False) gegen historische Krisenfenster, auf
NQ=F/ES=F-Tagesdaten (MNQ existiert als Instrument erst seit 2019). Verhaltens-Kennzahlen
(Drawdown, Trades) auf einem Preis-Proxy, KEINE echte MNQ-$-P&L (siehe
docs/superpowers/specs/2026-08-05-algo-rentec-ensemble-design.md Phase 4). Intraday-Daten
existieren fuer keines der fuenf Fenster (yfinance-Limit) -- deshalb laeuft
EnsembleStrategy hier durchgehend im Tages-Open/Close-Fallback-Modus.

Der Bias-Modell-Fit ist strikt auf Vorlauf-Daten VOR Fenster-Start beschraenkt (Tage
`< start`, nicht `< end`) -- sonst wuerde das Modell auf den Labels der Krise selbst
trainiert und "sagt" anschliessend etwas voraus, das es schon gelernt hat (Data-Leakage,
analog zum Task-8-Fix in algo/validate.py::on_fold_train). bias_series() bekommt dagegen
weiterhin den vollen Bereich bis `end`, damit das (nur auf Vorlauf-Daten gefittete) Modell
auch fuer die Krisentage selbst Vorhersagen liefert -- signals.py::_row_features schaut pro
Tag nur rueckwaerts, ein breiterer Bereich fuer bias_series() leakt also nichts.

Aufruf:
    python algo/stress_test.py                # alle 5 Fenster
    python algo/stress_test.py covid 2008      # nur bestimmte Fenster
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pandas as pd
from backtesting import Backtest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from backtest_seasonal import load_rows  # noqa: E402
from backtest_ensemble import EnsembleStrategy, fit_model, bias_series  # noqa: E402

BT_KWARGS = dict(cash=100_000, margin=0.05, commission=0.0002)

WINDOWS = {
    "2008": (date(2008, 9, 1), date(2009, 4, 1)),
    "covid": (date(2020, 2, 15), date(2020, 4, 16)),
    "flash2010": (date(2010, 5, 1), date(2010, 5, 14)),
    "china2015": (date(2015, 8, 17), date(2015, 8, 27)),
    "volmageddon2018": (date(2018, 2, 1), date(2018, 2, 10)),
}


def load_daily_df(symbol: str, start: date, end: date) -> pd.DataFrame:
    rows = [r for r in load_rows(symbol) if start <= r["day"] < end]
    return pd.DataFrame({
        "Open": [r["open"] for r in rows], "High": [r["high"] for r in rows],
        "Low": [r["low"] for r in rows], "Close": [r["close"] for r in rows],
    }, index=pd.DatetimeIndex([r["day"] for r in rows], name="t"))


def run_window(name: str, start: date, end: date) -> None:
    df = load_daily_df("NQ", start, end)
    if df.empty:
        print(f"{name}: keine NQ=F-Daten geladen (siehe Task 9) -- uebersprungen.")
        return
    px_rows = [r for r in load_rows("NQ") if r["day"] < end]     # voller Bereich, fuer bias_series
    es_rows = [r for r in load_rows("ES") if r["day"] < end]     # voller Bereich, fuer bias_series
    pre_crisis_px = [r for r in px_rows if r["day"] < start]     # Trainingsdaten: nur Vorlauf
    pre_crisis_es = [r for r in es_rows if r["day"] < start]
    if len(pre_crisis_px) < 30 or len(pre_crisis_es) < 30:
        print(f"{name}: zu wenig Vorlauf-Historie fuer Signale (NQ n={len(pre_crisis_px)}, "
              f"ES n={len(pre_crisis_es)}) -- uebersprungen.")
        return
    model = fit_model(pre_crisis_px, pre_crisis_es)
    EnsembleStrategy.bias = bias_series(model, px_rows, es_rows)  # voller Bereich -> Vorhersagen decken die Krise ab
    EnsembleStrategy.intraday = False
    stats = Backtest(df, EnsembleStrategy, **BT_KWARGS).run()
    pf = stats["Profit Factor"]
    pf_str = f"{pf:.3f}" if pf == pf else "n/a"
    print(f"-- {name} ({start} bis {end}, n={len(df)} Tage, NQ=F-Proxy, keine echte "
          f"MNQ-P&L, margin=0.05 (20x Hebel), Tages-Fallback (intraday=False) OHNE "
          f"Stop-Loss -- die Drawdown-Zahl unten ist Hebel-Mechanik, kein Modellversagen) --")
    print(f"   Trades={stats['# Trades']}  Max-Drawdown={stats['Max. Drawdown [%]']:.1f}%  "
          f"Profit-Factor={pf_str}")


def main(argv=None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    sys.stdout.reconfigure(encoding="utf-8")
    names = args or list(WINDOWS)
    for name in names:
        if name not in WINDOWS:
            print(f"Unbekanntes Fenster: {name} (verfuegbar: {', '.join(WINDOWS)})")
            continue
        run_window(name, *WINDOWS[name])
    return 0


if __name__ == "__main__":
    sys.exit(main())
