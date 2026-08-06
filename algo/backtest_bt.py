#!/usr/bin/env python3
"""Trade-Simulation fuer algo/rules.py::plan_trade ueber die PyPI-Bibliothek `backtesting`
(siehe Gespraech in algo/PLAN.md, Backlog-Punkt 2) -- keine eigene Equity-/Drawdown-Logik,
die Library liefert Positionsgroesse, Bracket-Orders (sl/tp) und Kennzahlen fertig.

Laedt dieselben 5m-Tagesdateien wie algo/backtest_ohlc.py (find_days()), haengt sie zu einer
durchgehenden Reihe zusammen und laesst pro Kerze plan_trade(hist_bis_hier, t) laufen -- exakt
derselbe Kein-Lookahead-Vertrag wie in rules.py, hier nur als Strategy.next() verdrahtet.

# ponytail: `backtesting` preist alles wie eine Aktie (P&L = Preisdifferenz * Stueckzahl,
# margin/cash statt Punktwert). MNQ ist eigentlich $2/Punkt -- Sharpe/Return% sind darum eine
# Naeherung, keine echte $-P&L. Fuer echte Punktwert-Ergebnisse: eigene Kennzahl aus
# stats._trades (EntryPrice/ExitPrice-Differenz je Trade) statt stats.Equity Final.

Aufruf:
    python algo/backtest_bt.py MNQ
    python algo/backtest_bt.py MNQ --plot
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from backtesting import Backtest, Strategy

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from backtest_ohlc import find_days  # noqa: E402
from analyze_ohlc import Bar, load  # noqa: E402
from rules import plan_trade  # noqa: E402
from pnl import risk_size, POINT_VALUE, real_pnl, flag_dubious, dubious_pct  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def load_series(symbol: str | None) -> pd.DataFrame:
    days = find_days(symbol or "MNQ")
    bars: list[Bar] = []
    for _, _, path in days:
        bars.extend(load(path))
    bars.sort(key=lambda b: b.t)
    return pd.DataFrame({
        "Open": [b.o for b in bars], "High": [b.h for b in bars],
        "Low": [b.l for b in bars], "Close": [b.c for b in bars],
    }, index=pd.DatetimeIndex([b.t for b in bars], name="t"))


class SilverBulletStrategy(Strategy):
    # Klassen-Attribut statt Konstante, damit bt.optimize() es variieren kann
    # (siehe algo/backtest_walkforward.py).
    stop_buffer_pct = 0.1
    max_risk_pct = 0.01        # Nutzerregel, siehe wiki/concepts/Risikomanagement (1% pro Trade).md
    point_value = POINT_VALUE["MNQ"]

    def init(self):
        self._taken: set[tuple] = set()  # (Tag, Fenstername) -- ein Versuch pro Fenster/Tag

    def next(self):
        if self.position:
            return
        when = self.data.index[-1]
        hist = [Bar(t, o, h, l, c) for t, o, h, l, c in
                zip(self.data.index, self.data.Open, self.data.High,
                    self.data.Low, self.data.Close)]
        setup = plan_trade(hist, when, stop_buffer_pct=self.stop_buffer_pct)
        if setup is None:
            return
        key = (setup.t.date(), setup.window)
        if key in self._taken:
            return
        size = risk_size(self.equity, self.max_risk_pct, setup.entry, setup.stop, self.point_value)
        if size < 1:
            return  # 1%-Risiko-Budget reicht bei diesem Stop-Abstand fuer keinen Kontrakt
        self._taken.add(key)
        if setup.side == "long":
            self.buy(size=size, limit=setup.entry, sl=setup.stop, tp=setup.target)
        else:
            self.sell(size=size, limit=setup.entry, sl=setup.stop, tp=setup.target)


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("symbol", nargs="?", default=None)
    ap.add_argument("--plot", action="store_true", help="algo/backtest_bt.html schreiben")
    a = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")

    df = load_series(a.symbol)
    print(f"{len(df)} Kerzen, {df.index[0]} bis {df.index[-1]}")

    bt = Backtest(df, SilverBulletStrategy, cash=100_000, margin=0.05, commission=0.0002)
    stats = bt.run()
    print(stats)
    print()
    print(stats._trades)

    trades = flag_dubious(stats._trades)
    trades = real_pnl(trades, "MNQ")
    print(f"\nEchte $-P&L (MNQ, ${POINT_VALUE['MNQ']:.0f}/Punkt): "
          f"{trades['RealPnL_USD'].sum():+.2f} USD  "
          f"(mehrdeutige Trades: {dubious_pct(trades):.1f}%, konservativ als Verlust gewertet)")

    if a.plot:
        out = ROOT / "algo" / "backtest_bt.html"
        bt.plot(filename=str(out), open_browser=False)
        print(f"\ngeschrieben: {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
