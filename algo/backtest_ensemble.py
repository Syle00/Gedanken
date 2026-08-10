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

Trade Management + Position Sizing (Nutzerregeln, siehe wiki/models/Silver Bullet Model.md
und wiki/concepts/Risikomanagement (1% pro Trade).md): Mindestziel 10 Punkte (rules.py),
Partial am ersten Swing-Punkt in Traderichtung + Stop auf Breakeven danach (_manage_partial),
Positionsgroesse so bemessen, dass ein Stop-Out max. 1% Kontoguthaben PRO TRADE kostet
(pnl.risk_size) -- nicht kumulativ pro Tag (Korrektur vom urspruenglich falsch verstandenen
Tagesbudget). Punktwert-Bug im 2026-08-06-Audit gefixt: die alte lokale _risk_size vergass
den Punktwert-Faktor, reales Risiko war dadurch doppelt so hoch wie beabsichtigt.
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
from pnl import risk_size, POINT_VALUE  # noqa: E402
from backtest_bt import extend_hist  # noqa: E402  -- inkrementeller hist-Aufbau (Performance-Fix)

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
    max_risk_pct = 0.01        # Nutzerregel: nie mehr als 1% Kontoguthaben Risiko PRO TRADE
    point_value = POINT_VALUE["MNQ"]  # $/Punkt, siehe pnl.POINT_VALUE
    leverage = 20               # muss zu Backtest(margin=...) passen (0.05 -> 20x); Strategy
                                 # hat keinen direkten Zugriff auf den margin-Wert des Brokers.
                                 # Geht als max_notional=equity*leverage in pnl.risk_size (dort
                                 # liegt der Deckel inkl. 0.95-Puffer, gemeinsam mit
                                 # SilverBulletStrategy)
    intraday = True

    def init(self):
        self._taken: set[tuple] = set()
        self._active: dict | None = None  # Entry-Info der offenen Position (Partial/BE-Tracking)
        self._hist: list[Bar] = []         # inkrementell fortgeschrieben, siehe extend_hist()

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

        extend_hist(self._hist, self.data)  # ersetzt den O(n²)-Neubau je Kerze (siehe backtest_bt)

        if self.position:
            self._manage_partial(self._hist)
            return
        if day_bias == "neutral":
            return

        setup = plan_trade(self._hist, when, stop_buffer_pct=self.stop_buffer_pct,
                            min_target_points=self.min_target_points)
        if setup is None or not _passes_bias_filter(setup.side, day_bias):
            return
        key = (setup.t.date(), setup.window)
        if key in self._taken:
            return

        size = risk_size(self.equity, self.max_risk_pct, setup.entry, setup.stop, self.point_value,
                          max_notional=self.equity * self.leverage)
        if size < 1:
            return  # 1%-Risiko-Budget oder Margin-Obergrenze ergibt 0 Kontrakte

        self._taken.add(key)
        self._active = {"side": setup.side, "entry": setup.entry, "entry_t": setup.t,
                         "partial_done": False}
        if setup.side == "long":
            self.buy(size=size, limit=setup.entry, sl=setup.stop, tp=setup.target)
        else:
            self.sell(size=size, limit=setup.entry, sl=setup.stop, tp=setup.target)

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

    # Kontraktgroessen-Logik selbst ist in pnl.py::demo() getestet -- hier nur die Verdrahtung:
    # EnsembleStrategy.point_value muss MNQ's echten Punktwert tragen, sonst reproduziert sich
    # der 2026-08-06-Audit-Fund (reales Risiko doppelt so hoch wie beabsichtigt).
    assert EnsembleStrategy.point_value == POINT_VALUE["MNQ"] == 2.0

    # Margin-Deckel liegt seit dem Final-Review-Fix in pnl.risk_size (max_notional), nicht mehr
    # lokal hier -- diese Zeile spiegelt den Aufruf in next() nach und haelt fest, dass leverage
    # zu Backtest(margin=0.05) passt: enger Stop -> Risiko-Groesse waere 5000, Margin erlaubt
    # 100k*20*0.95/25000 = 76 Kontrakte.
    lev = EnsembleStrategy.leverage
    assert lev == 20
    assert risk_size(100_000, 0.01, 25_000, 24_999.9, POINT_VALUE["MNQ"],
                     max_notional=100_000 * lev) == 76
    print("backtest_ensemble _passes_bias_filter/point_value/Margin-Deckel demo ok")


if __name__ == "__main__":
    _demo()
