#!/usr/bin/env python3
"""Trade-Simulation fuer algo/rules.py::plan_trade ueber die PyPI-Bibliothek `backtesting`
(siehe Gespraech in algo/PLAN.md, Backlog-Punkt 2) -- keine eigene Equity-/Drawdown-Logik,
die Library liefert Positionsgroesse, Bracket-Orders (sl/tp) und Kennzahlen fertig.

Laedt dieselben 5m-Tagesdateien wie algo/backtest_ohlc.py (find_days()), haengt sie zu einer
durchgehenden Reihe zusammen und laesst pro Kerze plan_trade(hist_bis_hier, t) laufen -- exakt
derselbe Kein-Lookahead-Vertrag wie in rules.py, hier nur als Strategy.next() verdrahtet.

# `backtesting` preist alles wie eine Aktie (P&L = Preisdifferenz * Stueckzahl, margin/cash
# statt Punktwert). MNQ ist eigentlich $2/Punkt -- Sharpe/Return%/Equity Final der Lib bleiben
# darum Naeherungen. Die echte Zahl liefert algo/pnl.py aus stats._trades: die "Echte $-P&L"-
# Zeile unten ist netto (Punktwert-P&L minus Commission), nicht stats["Equity Final"].
# ponytail: self.equity ist beim Sizing weiterhin in Lib-Punkteinheiten -- siehe die
# dokumentierte Grenze in pnl.risk_size(), Fix braucht Startkapital-Tracking. Der
# Drawdown-Kill-Switch rechnet dagegen seit 2026-08-12 in echten Dollar (starting_cash +
# (lib_equity - starting_cash) * point_value), siehe SilverBulletStrategy.next().

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
from confidence import bar_metrics, print_bar_metrics  # noqa: E402
import risk_fixed  # noqa: E402
import risk_killswitch  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def extend_hist(hist: list, data) -> None:
    """Schreibt `hist` inkrementell auf die aktuell sichtbare Laenge von `data` fort: pro
    next()-Aufruf waechst das `backtesting`-Datenfenster um genau eine Bar, also nur die neu
    sichtbaren Bars anhaengen, statt die gesamte Historie je Kerze neu als Bar-Liste zu bauen.

    Das ist der Performance-Fix fuer den O(n²)-Neubau (bei 11.573 5m-Kerzen ~5 min -> Sekunden,
    siehe algo/PLAN.md Backlog 10). **Ergebnis-erhaltend by construction:** die entstehende
    Liste ist Bit-fuer-Bit dieselbe wie `[Bar(t,o,h,l,c) for t,o,h,l,c in zip(data.index,
    data.Open, data.High, data.Low, data.Close)]` -- gleiche Reihenfolge, gleiche Werte,
    gleiche Typen. Muss VOR der Positions-/Signalpruefung laufen, damit auch Bars waehrend
    einer offenen Position erfasst werden und keine Luecke entsteht."""
    idx, o, h, l, c = data.index, data.Open, data.High, data.Low, data.Close
    for j in range(len(hist), len(idx)):
        hist.append(Bar(idx[j], o[j], h[j], l[j], c[j]))


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
    # High-Probability-Filter aus rules.py -- als Klassenattribute, damit
    # Vorher/Nachher ohne Codeaenderung vergleichbar bleibt (2026-08-13).
    require_strong = False
    min_size_rel = None  # Defaults = Baseline; siehe rules.plan_trade-Docstring
    max_risk_pct = 0.01        # Nutzerregel, siehe wiki/concepts/Risikomanagement (1% pro Trade).md
    point_value = POINT_VALUE["MNQ"]  # main() ueberschreibt das passend zum CLI-Symbol
    leverage = 20               # muss zu Backtest(margin=...) in main() passen (0.05 -> 20x),
                                 # siehe EnsembleStrategy.leverage -- ohne diesen Deckel
                                 # stornierte der Broker Orders mit engem Stop stillschweigend
    risk_module = risk_fixed    # austauschbar: risk_fixed/risk_garch/risk_kelly, siehe
                                 # docs/superpowers/specs/2026-08-12-quant-risk-management-design.md
    max_drawdown_pct = risk_killswitch.DEFAULT_MAX_DRAWDOWN_PCT  # Kill-Switch-Schwelle, pro Strategie
    starting_cash = 100_000     # muss zu Backtest(cash=...) passen (main() hier und
                                 # backtest_risk_compare.py::run_one()) -- Basis der
                                 # Echt-Dollar-Umrechnung fuer den Kill-Switch

    def init(self):
        self._taken: set[tuple] = set()       # (Tag, Fenstername) -- ein Versuch pro Fenster/Tag
        self._hist: list[Bar] = []            # inkrementell fortgeschrieben, siehe extend_hist()
        self._equity_peak: float = 0.0        # laufendes Echt-Dollar-Hoch fuer den Kill-Switch

    def next(self):
        extend_hist(self._hist, self.data)  # muss VOR der Positionspruefung laufen (lueckenlos)
        # self.equity ist in Lib-Punkteinheiten ($1/Punkt) denominiert, nicht in echten Dollar --
        # derselbe Fehlertyp wie in der ⚠️-Grenze von pnl.py::risk_size() dokumentiert. Ohne diese
        # Skalierung wuerde die 15%-Schwelle nicht 15% echten Kontos bedeuten.
        real_equity = self.starting_cash + (self.equity - self.starting_cash) * self.point_value
        self._equity_peak = max(self._equity_peak, real_equity)
        if self.position:
            return
        if not risk_killswitch.allowed(self._equity_peak, real_equity, self.max_drawdown_pct):
            # Gate blockt nicht nur neue Orders: bereits platzierte, noch nicht gefuellte
            # Limit-Orders aus frueheren Bars verfallen hier nie von selbst (siehe
            # algo/README.md) und wuerden nach dem Trip noch fuellen.
            for o in self.orders:
                o.cancel()
            return  # Drawdown-Kill-Switch aktiv -- kein neuer Trade, bis neues Equity-Hoch
        when = self.data.index[-1]
        setup = plan_trade(self._hist, when, stop_buffer_pct=self.stop_buffer_pct,
                           require_strong=self.require_strong,
                           min_size_rel=self.min_size_rel)
        if setup is None:
            return
        key = (setup.t.date(), setup.window)
        if key in self._taken:
            return
        pct = self.risk_module.risk_pct(hist=self._hist, closed_trades=self.closed_trades,
                                         base_pct=self.max_risk_pct)
        size = risk_size(self.equity, pct, setup.entry, setup.stop, self.point_value,
                          max_notional=self.equity * self.leverage)
        if size < 1:
            return  # Risiko-Budget oder Margin-Obergrenze ergibt 0 Kontrakte
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

    sym = a.symbol or "MNQ"  # gleicher Default wie load_series()
    df = load_series(sym)
    print(f"{sym}: {len(df)} Kerzen, {df.index[0]} bis {df.index[-1]}")

    # Punktwert muss zum tatsaechlich geladenen Symbol passen -- fest verdrahtetes "MNQ" hiess
    # bei `backtest_bt.py ES` 25x zu grosse Positionen (Fund 3 des Final Review).
    SilverBulletStrategy.point_value = POINT_VALUE[sym]
    SilverBulletStrategy.starting_cash = 100_000  # muss zum cash= unten passen
    bt = Backtest(df, SilverBulletStrategy, cash=100_000, margin=0.05, commission=0.0002)
    stats = bt.run()
    print(stats)
    print()
    print(stats._trades)

    trades = flag_dubious(stats._trades, df)
    trades = real_pnl(trades, sym)
    print(f"\nEchte $-P&L netto ({sym}, ${POINT_VALUE[sym]:.0f}/Punkt, nach Commission): "
          f"{trades['RealPnL_USD'].sum():+.2f} USD  "
          f"(mehrdeutige Trades: {dubious_pct(trades):.1f}%, konservativ als Verlust gewertet)")

    # Backlog 7 + 9a (siehe algo/PLAN.md): dieselben Trades zusaetzlich auf BAR-Basis bewerten
    # und eine BCa-Untergrenze ausweisen, statt nur den Trade-basierten Punktschaetzer der Lib.
    print_bar_metrics(bar_metrics(stats._trades, df))

    if a.plot:
        out = ROOT / "algo" / "backtest_bt.html"
        bt.plot(filename=str(out), open_browser=False)
        print(f"\ngeschrieben: {out.relative_to(ROOT)}")


def demo() -> None:
    """Regressionsguard fuer extend_hist() (Performance-Fix, siehe algo/PLAN.md): das
    inkrementelle Anhaengen ueber ein wachsendes Fenster muss Bit-fuer-Bit dieselbe Bar-Liste
    liefern wie der fruehere Neubau je Kerze (zip ueber das volle Fenster). Damit ist der
    O(n²)->O(n)-Umbau dauerhaft gegen stille Ergebnisdrift abgesichert -- nicht nur durch den
    einmaligen Vorher/Nachher-Trade-Diff von 2026-08-11."""
    from types import SimpleNamespace
    import numpy as np
    n = 30
    idx = pd.date_range("2026-01-01", periods=n, freq="5min", tz="America/New_York")
    o = np.arange(n, dtype=float)
    hist: list[Bar] = []
    for k in range(1, n + 1):                       # Fenster waechst je next()-Aufruf um 1 Bar
        data = SimpleNamespace(index=idx[:k], Open=o[:k], High=o[:k] + 1,
                               Low=o[:k] - 1, Close=o[:k] + 0.5)
        extend_hist(hist, data)
        rebuild = [Bar(t, oo, hh, ll, cc) for t, oo, hh, ll, cc in
                   zip(data.index, data.Open, data.High, data.Low, data.Close)]
        assert hist == rebuild, f"extend_hist weicht bei k={k} vom Neubau ab"
    assert len(hist) == n
    print("backtest_bt.demo: OK (extend_hist ergebnis-erhaltend)")


if __name__ == "__main__":
    import sys as _sys
    if "--selfcheck" in _sys.argv:
        demo()
    else:
        main()
