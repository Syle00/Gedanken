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
    """Kopie von `trades` mit zusaetzlicher Spalte 'RealPnL_USD' = NETTO-Ergebnis in Dollar,
    also (ExitPrice - EntryPrice) * Size * Punktwert[symbol] MINUS der von der Lib gebuchten
    'Commission'. `Size` traegt bei backtesting.py bereits das Vorzeichen (negativ bei Short),
    daher kein separates Side-Handling noetig.

    Die Kommission wird abgezogen, weil sie sonst komplett unter den Tisch fiel: im
    MNQ-Lauf vom 2026-08-06 lagen ~$13.3k Kommission gegen ~$1.1k Brutto-Punktwert-P&L --
    die als "echt" beworbene Zahl war dadurch um eine Groessenordnung zu optimistisch
    (Fund 2 des Final Review)."""
    if symbol not in POINT_VALUE:
        raise ValueError(f"Kein Punktwert fuer {symbol!r} hinterlegt (POINT_VALUE: {list(POINT_VALUE)})")
    out = trades.copy()
    out["RealPnL_USD"] = ((out["ExitPrice"] - out["EntryPrice"]) * out["Size"] * POINT_VALUE[symbol]
                          - out["Commission"])
    return out


def flag_dubious(trades: pd.DataFrame, bars: pd.DataFrame) -> pd.DataFrame:
    """Markiert Trades, deren Entry- und Exit-Zeit in derselben Kerze liegen UND deren SL/TP
    beide in der High/Low-Spanne der Entry-Kerze liegen (Spalte 'Dubious') -- nur dann kann die
    `backtesting`-Lib die Fill-Reihenfolge tatsaechlich nicht unterscheiden (siehe UserWarning
    "same bar its parent stop/limit order was turned into a trade"). Wertet sie konservativ:
    'ExitPrice' wird auf den Stop-Preis ('SL') gesetzt, statt der von der Lib gewaehlten
    (moeglicherweise zu optimistischen) 'ExitPrice' zu vertrauen. `bars` = dieselbe OHLC-Reihe,
    die an `Backtest()` ging (Spalten 'High'/'Low', Position = 'EntryBar'). Muss VOR real_pnl()
    aufgerufen werden, damit die $-Berechnung den korrigierten Exit sieht.

    Bar-Range-Check statt Pauschal-Korrektur (Code-Review-Fund 2026-08-07, siehe
    docs/superpowers/specs/2026-08-06-algo-backtest-precision-audit-design.md:45 -- die
    urspruengliche Design-Signatur hatte `bars` bereits vorgesehen, die erste Implementierung
    liess den Parameter faelschlich weg): liegt nur das TP im Bar-Range, das SL aber nie, ist
    die Reihenfolge laut Lib-Quelle selbst eindeutig ("stop and TP go in the same price
    direction", backtesting.py::_process_orders) -- ein echter Gewinn-Trade wurde von der
    Pauschal-Version faelschlich zum Verlust am Stop-Preis umgewertet. Trades ohne Stop oder
    ohne Ziel (SL/TP = NaN) bleiben unangetastet, sonst wuerde ExitPrice zu NaN und der Trade
    faende in real_pnl() gar nicht mehr statt, statt korrekt bewertet zu werden. Nur
    'ExitPrice' (und damit 'RealPnL_USD') spiegelt die Korrektur -- die Lib-Spalten
    'PnL'/'ReturnPct' bleiben auf dem unkorrigierten Stand und duerfen nach diesem Aufruf nicht
    mehr als Wahrheit gelten."""
    out = trades.copy()
    same_bar = out["EntryTime"] == out["ExitTime"]
    entry_high = bars["High"].to_numpy()[out["EntryBar"].to_numpy()]
    entry_low = bars["Low"].to_numpy()[out["EntryBar"].to_numpy()]
    both_touchable = (
        out["SL"].notna() & out["TP"].notna()
        & (entry_low <= out["SL"]) & (out["SL"] <= entry_high)
        & (entry_low <= out["TP"]) & (out["TP"] <= entry_high)
    )
    out["Dubious"] = same_bar & both_touchable
    out.loc[out["Dubious"], "ExitPrice"] = out.loc[out["Dubious"], "SL"]
    return out


def dubious_pct(trades: pd.DataFrame) -> float:
    """Anteil der Trades mit Entry- und Exit-Zeit in derselben Kerze, in Prozent."""
    if len(trades) == 0:
        return 0.0
    return 100.0 * (trades["EntryTime"] == trades["ExitTime"]).sum() / len(trades)


def risk_size(equity: float, max_risk_pct: float, entry: float, stop: float,
              point_value: float, max_notional: float | None = None) -> int:
    """Kontraktzahl, sodass ein Stop-Out genau `max_risk_pct` von `equity` in ECHTEN Dollar
    kostet: budget_usd = equity * max_risk_pct; realer Verlust pro Kontrakt bei Stop-Out =
    |entry-stop| (Punkte) * point_value ($/Punkt). Ohne point_value wuerde 1 Punkt wie $1
    behandelt -- bei MNQ ($2/Punkt) laege das reale Risiko dann beim Doppelten des
    beabsichtigten Budgets (Fund vom 2026-08-06-Audit, siehe frueheres
    algo/backtest_ensemble.py::_risk_size vor diesem Fix).

    `max_notional` (optional, = equity * Hebel) deckelt das Ergebnis zusaetzlich auf
    int(max_notional * 0.95 / entry) Kontrakte. Ohne diesen Deckel fordert ein enger Stop mehr
    Kontrakte an, als die Margin hergibt, und die `backtesting`-Lib STORNIERT die Order
    stillschweigend ("Broker canceled the order due to insufficient margin") statt sie kleiner
    zu fuellen -- ein systematischer Bias gegen genau die Setups mit engem Stop (Fund 1 des
    Final Review: 60 von 99 Setups fielen so weg). Der 0.95-Puffer faengt ab, dass die Order
    ggf. erst Bars spaeter zum Limit-Preis fuellt und die Margin dann knapper ist.

    ⚠️ Grenze: `equity` kommt an beiden Aufrufstellen aus `backtesting.Strategy.self.equity` und
    ist in den ROHEN Preispunkt-Einheiten der Lib denominiert (intern $1/Punkt), nicht in echten
    Dollar. Beim Startkapital stimmen beide ueberein, danach driften sie mit jedem Trade
    auseinander (echtes Konto bewegt sich um ×point_value). Nach einem realen Drawdown budgetiert
    diese Funktion daher 1% eines zu hoch angesetzten Eigenkapitals -- das reale Risiko pro Trade
    kriecht ueber die 1% hinaus. Die 1%-Zahl ist exakt fuer den ersten Trade und eine
    Groessenordnung fuer alle folgenden; ein echter Fix braucht Startkapital-Tracking in der
    Strategy (offen, Fund 5 des Final Review)."""
    budget_usd = equity * max_risk_pct
    stop_dist_pts = abs(entry - stop)
    if stop_dist_pts == 0:
        return 0
    risk_per_contract_usd = stop_dist_pts * point_value
    size = int(budget_usd / risk_per_contract_usd)
    if max_notional is not None:
        size = min(size, int(max_notional * 0.95 / entry))
    return max(0, size)


def demo() -> None:
    trades = pd.DataFrame({
        "EntryTime": pd.to_datetime(["2026-01-01 10:00", "2026-01-01 10:05", "2026-01-01 10:10"]),
        "ExitTime":  pd.to_datetime(["2026-01-01 10:05", "2026-01-01 10:05", "2026-01-01 10:20"]),
        "EntryPrice": [100.0, 100.0, 100.0],
        "ExitPrice":  [105.0, 105.0, 95.0],
        "Size": [1, 1, -1],
        "SL": [95.0, 95.0, 105.0],
        "TP": [110.0, 110.0, 85.0],
        "EntryBar": [0, 1, 2],
        "Commission": [1.0, 1.0, 2.0],
    })
    # Kerze 1 (Trade 1's Entry-Kerze): High/Low umschliessen SOWOHL SL=95 ALS AUCH TP=110 ->
    # echte Ambiguitaet, Lib kann Reihenfolge nicht bestimmen.
    bars = pd.DataFrame({"High": [101.0, 115.0, 106.0], "Low": [99.0, 90.0, 94.0]})
    tagged = flag_dubious(trades, bars)
    assert tagged["Dubious"].tolist() == [False, True, False]
    assert tagged.loc[1, "ExitPrice"] == 95.0  # mehrdeutiger Trade -> Exit auf Stop gesetzt

    priced = real_pnl(tagged, "MNQ")
    # Netto = Punktwert-P&L minus Commission.
    # Trade 0: (105-100)*1*$2 - $1 = $9. Trade 1 (mehrdeutig, Exit auf Stop=95): -$10 - $1 = -$11.
    # Trade 2 (Short, Size=-1): (95-100)*-1*$2 - $2 = $8.
    assert priced["RealPnL_USD"].tolist() == [9.0, -11.0, 8.0]

    # Same-Bar-Trade OHNE Stop: ExitPrice bleibt stehen, statt zu NaN zu werden (der Trade
    # zaehlte sonst in der $-Summe gar nicht mehr mit).
    no_sl = trades.copy()
    no_sl.loc[1, "SL"] = float("nan")
    assert flag_dubious(no_sl, bars).loc[1, "ExitPrice"] == 105.0

    # Same-Bar-Trade, aber NICHT ambig: TP=108 liegt in der Entry-Kerze (Low=95/High=110),
    # SL=90 nie (< Low=95) -- laut Lib-Quelle "not ambiguous", TP war eindeutig zuerst dran.
    # Vorherige Pauschal-Version haette diesen Gewinn-Trade faelschlich zum Verlust gemacht.
    not_ambig = pd.DataFrame({
        "EntryTime": pd.to_datetime(["2026-01-01 10:15"]),
        "ExitTime":  pd.to_datetime(["2026-01-01 10:15"]),
        "EntryPrice": [100.0], "ExitPrice": [108.0], "Size": [1],
        "SL": [90.0], "TP": [108.0], "EntryBar": [0], "Commission": [1.0],
    })
    not_ambig_bars = pd.DataFrame({"High": [110.0], "Low": [95.0]})
    result = flag_dubious(not_ambig, not_ambig_bars)
    assert result.loc[0, "Dubious"] == False
    assert result.loc[0, "ExitPrice"] == 108.0  # unangetastet, kein falscher Verlust

    assert abs(dubious_pct(trades) - 100 / 3) < 1e-6  # 1 von 3 Trades ist same-bar (Rohmetrik)

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

    # Margin-Deckel (Fund 1 des Final Review): ein sehr enger Stop (0.1 Punkte) laesst das
    # 1%-Budget 5000 Kontrakte tragen -- das Notional (5000 * 100 = $500k) sprengt die Margin,
    # die Lib storniert die Order dann kommentarlos. Mit max_notional wird stattdessen gedeckelt.
    assert risk_size(100_000, 0.01, 100, 99.9, 2.0) == 5000
    assert risk_size(100_000, 0.01, 100, 99.9, 2.0, max_notional=100_000) == 950  # 100k*0.95/100
    # Deckel greift nur nach oben: passt die Risiko-Groesse ins Notional, bleibt sie unveraendert.
    assert risk_size(100_000, 0.01, 100, 90, 2.0, max_notional=100_000 * 20) == 50
    assert risk_size(100_000, 0.01, 100, 99.9, 2.0, max_notional=0) == 0

    print("pnl demo ok")


if __name__ == "__main__":
    demo()
