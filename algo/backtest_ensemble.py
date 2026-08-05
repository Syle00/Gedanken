#!/usr/bin/env python3
"""RenTec-artige Ensemble-Strategie: taeglicher Bias aus Logistic Regression ueber die
Signale aus algo/signals.py, filtert die bestehende Silver-Bullet-Intraday-Regel
(algo/rules.py::plan_trade) statt sie zu ersetzen (siehe
docs/superpowers/specs/2026-08-05-algo-rentec-ensemble-design.md Phase 2). Bias-Totzone
45-55% Wahrscheinlichkeit -> "neutral" (kein Trade). `intraday=False` (siehe
algo/stress_test.py) haelt stattdessen eine Position solange der Tages-Bias in dieselbe
Richtung zeigt (Open/Close-Fallback fuer Perioden ohne Intraday-Daten).

Bei ~150 Handelstagen und 8 Features ist Overfitting trotz L2-Regularisierung ein reales
Risiko -- jedes Ergebnis hier ist eine Groessenordnungs-Schaetzung, siehe algo/validate.py
fuer die Walk-Forward-Validierung mit Per-Fold-Refit (kein statischer Fit auf allen Daten).
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

from backtesting import Strategy
from sklearn.linear_model import LogisticRegression

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from analyze_ohlc import Bar  # noqa: E402
from rules import plan_trade  # noqa: E402
from signals import build_features  # noqa: E402

BIAS_LONG_THRESHOLD = 0.55
BIAS_SHORT_THRESHOLD = 0.45


def fit_model(mnq_rows: list[dict], es_rows: list[dict]) -> LogisticRegression:
    X, y, _ = build_features(mnq_rows, es_rows)
    model = LogisticRegression(class_weight="balanced", max_iter=1000)
    model.fit(X, y)
    return model


def bias_series(model: LogisticRegression, mnq_rows: list[dict], es_rows: list[dict],
                 min_history: int = 25) -> dict[date, str]:
    """Bias je Handelstag ('long'/'short'/'neutral'). `model` muss VOR diesem Aufruf
    bereits gefittet sein (siehe algo/validate.py::on_fold_train fuer den
    Walk-Forward-Fall: pro Fold ein frischer Fit auf dem In-Sample-Anteil)."""
    X, _, target_days = build_features(mnq_rows, es_rows, min_history)
    if not X:
        return {}
    probs = model.predict_proba(X)[:, 1]
    out = {}
    for day, p in zip(target_days, probs):
        if p > BIAS_LONG_THRESHOLD:
            out[day] = "long"
        elif p < BIAS_SHORT_THRESHOLD:
            out[day] = "short"
        else:
            out[day] = "neutral"
    return out


def _passes_bias_filter(setup_side: str, day_bias: str) -> bool:
    """True wenn eine Silver-Bullet-Setup-Richtung mit dem Tages-Bias uebereinstimmt."""
    return day_bias in ("long", "short") and (setup_side == "long") == (day_bias == "long")


class EnsembleStrategy(Strategy):
    bias: dict = {}            # date -> "long"/"short"/"neutral", vor bt.run() gesetzt
    stop_buffer_pct = 0.1
    intraday = True

    def init(self):
        self._taken: set[tuple] = set()

    def next(self):
        when = self.data.index[-1]
        day_bias = self.bias.get(when.date(), "neutral")

        if not self.intraday:
            if self.position:
                if (self.position.is_long and day_bias != "long") or \
                   (self.position.is_short and day_bias != "short"):
                    self.position.close()
                return
            if day_bias == "long":
                self.buy()
            elif day_bias == "short":
                self.sell()
            return

        if self.position or day_bias == "neutral":
            return
        hist = [Bar(t, o, h, l, c) for t, o, h, l, c in
                zip(self.data.index, self.data.Open, self.data.High,
                    self.data.Low, self.data.Close)]
        setup = plan_trade(hist, when, stop_buffer_pct=self.stop_buffer_pct)
        if setup is None or not _passes_bias_filter(setup.side, day_bias):
            return
        key = (setup.t.date(), setup.window)
        if key in self._taken:
            return
        self._taken.add(key)
        if setup.side == "long":
            self.buy(limit=setup.entry, sl=setup.stop, tp=setup.target)
        else:
            self.sell(limit=setup.entry, sl=setup.stop, tp=setup.target)


def _demo() -> None:
    assert _passes_bias_filter("long", "long") is True
    assert _passes_bias_filter("short", "short") is True
    assert _passes_bias_filter("long", "short") is False
    assert _passes_bias_filter("short", "long") is False
    assert _passes_bias_filter("long", "neutral") is False
    print("backtest_ensemble _passes_bias_filter demo ok")


if __name__ == "__main__":
    _demo()
