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
from analyze_ohlc import Bar, swings, CFG  # noqa: E402
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
    min_target_points = 10.0   # Mindest-Handle-Ziel Entry->Target, siehe rules.py::plan_trade
    partial_portion = 0.5      # Anteil, der am ersten Swing-Punkt in Traderichtung geschlossen
                                # wird (Nutzerregel; Split selbst nicht vorgegeben -> 50/50
                                # als ponytail: Default, bei Bedarf anpassbar)
    intraday = True

    def init(self):
        self._taken: set[tuple] = set()
        self._active: dict | None = None  # Entry-Info der offenen Position (Partial/BE-Tracking)

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

        hist = [Bar(t, o, h, l, c) for t, o, h, l, c in
                zip(self.data.index, self.data.Open, self.data.High,
                    self.data.Low, self.data.Close)]

        if self.position:
            self._manage_partial(hist)
            return
        if day_bias == "neutral":
            return

        setup = plan_trade(hist, when, stop_buffer_pct=self.stop_buffer_pct,
                            min_target_points=self.min_target_points)
        if setup is None or not _passes_bias_filter(setup.side, day_bias):
            return
        key = (setup.t.date(), setup.window)
        if key in self._taken:
            return
        self._taken.add(key)
        self._active = {"side": setup.side, "entry": setup.entry, "entry_t": setup.t,
                         "partial_done": False}
        if setup.side == "long":
            self.buy(limit=setup.entry, sl=setup.stop, tp=setup.target)
        else:
            self.sell(limit=setup.entry, sl=setup.stop, tp=setup.target)

    def _manage_partial(self, hist: list[Bar]) -> None:
        """Nutzerregel: Partial am ersten Swing-Hoch (long) bzw. Swing-Tief (short) NACH dem
        Entry, danach Stop auf Breakeven -- verhindert, dass ein ausgelaufener Gewinn wieder
        zum Drawdown wird (siehe wiki/models/Silver Bullet Model.md, "Trade Management")."""
        if self._active is None or self._active["partial_done"] or not self.trades:
            return
        side, entry_t = self._active["side"], self._active["entry_t"]
        kind = "high" if side == "long" else "low"
        candidates = [price for idx, k, price in swings(hist, CFG["swing"])
                      if k == kind and hist[idx].t > entry_t]
        if not candidates:
            return
        level = candidates[0]  # erster (frueheste) Swing-Punkt nach Entry in Traderichtung
        bar = hist[-1]
        reached = bar.h >= level if side == "long" else bar.l <= level
        if not reached:
            return
        self.trades[0].close(portion=self.partial_portion)
        self.trades[0].sl = self._active["entry"]
        self._active["partial_done"] = True


def _demo() -> None:
    assert _passes_bias_filter("long", "long") is True
    assert _passes_bias_filter("short", "short") is True
    assert _passes_bias_filter("long", "short") is False
    assert _passes_bias_filter("short", "long") is False
    assert _passes_bias_filter("long", "neutral") is False
    print("backtest_ensemble _passes_bias_filter demo ok")


if __name__ == "__main__":
    _demo()
