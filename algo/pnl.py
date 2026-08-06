#!/usr/bin/env python3
"""Praezisions-Layer UEBER der `backtesting`-Bibliothek (siehe
docs/superpowers/specs/2026-08-06-algo-backtest-precision-audit-design.md Teil 1). Die Lib
rechnet Trade-P&L als (ExitPrice - EntryPrice) * Size in rohen Preispunkten -- fuer Futures mit
einem Punktwert ungleich $1 (MNQ = $2/Punkt) ist das weder die reale Positionsgroesse
(`risk_size`) noch der reale Dollar-Gewinn (`real_pnl`). Ersetzt die Lib nicht (Order-/Equity-
Verwaltung bleibt dort), ergaenzt sie nur um die zwei fehlenden Punktwert-Bezuege.

`stats._trades`-Spalten (siehe backtesting/_stats.py): Size, EntryBar, ExitBar, EntryPrice,
ExitPrice, SL, TP, PnL, Commission, ReturnPct, EntryTime, ExitTime, Duration, Tag.
"""
from __future__ import annotations

import pandas as pd

# Nur tatsaechlich im Projekt genutzte Symbole -- keine spekulative Vollstaendigkeit.
POINT_VALUE = {"MNQ": 2.0, "NQ": 20.0, "ES": 50.0}


def real_pnl(trades: pd.DataFrame, symbol: str) -> pd.DataFrame:
    """Kopie von `trades` mit zusaetzlicher Spalte 'RealPnL_USD' = (ExitPrice - EntryPrice) *
    Size * Punktwert[symbol]. `Size` traegt bei backtesting.py bereits das Vorzeichen (negativ
    bei Short), daher kein separates Side-Handling noetig."""
    if symbol not in POINT_VALUE:
        raise ValueError(f"Kein Punktwert fuer {symbol!r} hinterlegt (POINT_VALUE: {list(POINT_VALUE)})")
    out = trades.copy()
    out["RealPnL_USD"] = (out["ExitPrice"] - out["EntryPrice"]) * out["Size"] * POINT_VALUE[symbol]
    return out


def flag_dubious(trades: pd.DataFrame) -> pd.DataFrame:
    """Markiert Trades, deren entry- und Exit-Zeit in derselben Kerze liegen (Spalte
    'Dubious') -- bei diesen kann die `backtesting`-Lib die Fill-Reihenfolge von SL/TP nicht
    unterscheiden (siehe UserWarning "same bar its parent stop/limit order was turned into a
    trade"). Wertet sie konservativ: 'ExitPrice' wird auf den Stop-Preis ('SL') gesetzt, statt
    der von der Lib gewaehlten (moeglicherweise zu optimistischen) 'ExitPrice' zu vertrauen.
    Muss VOR real_pnl() aufgerufen werden, damit die $-Berechnung den korrigierten Exit sieht."""
    out = trades.copy()
    out["Dubious"] = out["EntryTime"] == out["ExitTime"]
    out.loc[out["Dubious"], "ExitPrice"] = out.loc[out["Dubious"], "SL"]
    return out


def dubious_pct(trades: pd.DataFrame) -> float:
    """Anteil der Trades mit Entry- und Exit-Zeit in derselben Kerze, in Prozent."""
    if len(trades) == 0:
        return 0.0
    return 100.0 * (trades["EntryTime"] == trades["ExitTime"]).sum() / len(trades)


def risk_size(equity: float, max_risk_pct: float, entry: float, stop: float,
              point_value: float) -> int:
    """Kontraktzahl, sodass ein Stop-Out genau `max_risk_pct` von `equity` in ECHTEN Dollar
    kostet: budget_usd = equity * max_risk_pct; realer Verlust pro Kontrakt bei Stop-Out =
    |entry-stop| (Punkte) * point_value ($/Punkt). Ohne point_value wuerde 1 Punkt wie $1
    behandelt -- bei MNQ ($2/Punkt) laege das reale Risiko dann beim Doppelten des
    beabsichtigten Budgets (Fund vom 2026-08-06-Audit, siehe frueheres
    algo/backtest_ensemble.py::_risk_size vor diesem Fix)."""
    budget_usd = equity * max_risk_pct
    stop_dist_pts = abs(entry - stop)
    if stop_dist_pts == 0:
        return 0
    risk_per_contract_usd = stop_dist_pts * point_value
    return max(0, int(budget_usd / risk_per_contract_usd))


def demo() -> None:
    trades = pd.DataFrame({
        "EntryTime": pd.to_datetime(["2026-01-01 10:00", "2026-01-01 10:05", "2026-01-01 10:10"]),
        "ExitTime":  pd.to_datetime(["2026-01-01 10:05", "2026-01-01 10:05", "2026-01-01 10:20"]),
        "EntryPrice": [100.0, 100.0, 100.0],
        "ExitPrice":  [105.0, 105.0, 95.0],
        "Size": [1, 1, -1],
        "SL": [95.0, 95.0, 105.0],
    })
    tagged = flag_dubious(trades)
    assert tagged["Dubious"].tolist() == [False, True, False]
    assert tagged.loc[1, "ExitPrice"] == 95.0  # mehrdeutiger Trade -> Exit auf Stop gesetzt

    priced = real_pnl(tagged, "MNQ")
    # Trade 0: (105-100)*1*$2 = $10. Trade 1 (mehrdeutig, Exit auf Stop=95): (95-100)*1*$2 = -$10.
    # Trade 2 (Short, Size=-1): (95-100)*-1*$2 = $10.
    assert priced["RealPnL_USD"].tolist() == [10.0, -10.0, 10.0]

    assert abs(dubious_pct(trades) - 100 / 3) < 1e-6  # 1 von 3 Trades ist mehrdeutig

    try:
        real_pnl(trades, "GC")
    except ValueError:
        pass
    else:
        raise AssertionError("real_pnl muss bei unbekanntem Symbol einen ValueError werfen")

    # 1% von 100_000 = $1000 Budget, Stop 10 Punkte entfernt, MNQ $2/Punkt -> Risiko/Kontrakt
    # $20 -> 50 Kontrakte (die alte, fehlerhafte Formel ohne point_value ergab hier 100 --
    # doppelt so viel reales Risiko wie beabsichtigt).
    assert risk_size(100_000, 0.01, 100, 90, 2.0) == 50
    assert risk_size(100_000, 0.01, 100, 0, 2.0) == 5
    assert risk_size(100_000, 0.01, 100, 100, 2.0) == 0  # Stop-Abstand 0 -> keine Kontrakte

    print("pnl demo ok")


if __name__ == "__main__":
    demo()
