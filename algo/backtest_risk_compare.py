#!/usr/bin/env python3
"""Vergleicht die drei Risk-Sizing-Module (fix/GARCH/Kelly) auf identischen Silver-Bullet-
Signalen -- gleiche Trades, nur die Positionsgroesse variiert. Der Drawdown-Kill-Switch (15%)
laeuft bei allen drei mit (unabhaengig vom Sizing-Modul, siehe backtest_bt.py). Siehe
docs/superpowers/specs/2026-08-12-quant-risk-management-design.md.

Aufruf:
    python algo/backtest_risk_compare.py MNQ
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pandas as pd
from backtesting import Backtest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from backtest_bt import SilverBulletStrategy, load_series  # noqa: E402
from pnl import POINT_VALUE, real_pnl, flag_dubious, dubious_pct  # noqa: E402
import risk_fixed  # noqa: E402
import risk_garch  # noqa: E402
import risk_kelly  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MODULES = {"fixed": risk_fixed, "garch": risk_garch, "kelly": risk_kelly}


def var_es(daily_pnl: pd.Series, confidence: float = 0.95) -> tuple[float, float]:
    """95%-Tages-VaR und Expected Shortfall (ES) aus einer taeglichen $-PnL-Reihe: VaR = das
    (1-confidence)-Quantil (als positiver Verlustbetrag), ES = Mittelwert aller Tage, die
    mindestens so schlecht wie das Quantil ausfielen (Tail-Mittelwert, subadditiv -- siehe
    wiki/concepts/Kelly-Criterion & Value-at-Risk (Money Management).md). Leere Reihe -> (0, 0)."""
    if len(daily_pnl) == 0:
        return 0.0, 0.0
    q = daily_pnl.quantile(1 - confidence, interpolation="lower")
    var = -float(q)
    tail = daily_pnl[daily_pnl <= q]
    es = -float(tail.mean()) if len(tail) else var
    return var, es


def run_one(df: pd.DataFrame, symbol: str, module) -> dict:
    """Fuehrt einen kompletten Backtest mit `module` als risk_module durch und liefert die
    Vergleichskennzahlen. Mutiert `SilverBulletStrategy`-Klassenattribute -- Aufrufe muessen
    sequenziell laufen (keine parallelen run_one()-Aufrufe auf derselben Klasse)."""
    SilverBulletStrategy.point_value = POINT_VALUE[symbol]
    SilverBulletStrategy.risk_module = module
    bt = Backtest(df, SilverBulletStrategy, cash=100_000, margin=0.05, commission=0.0002)
    stats = bt.run()
    trades = flag_dubious(stats._trades, df)
    trades = real_pnl(trades, symbol)
    if len(trades):
        daily = trades.groupby(trades["ExitTime"].dt.date)["RealPnL_USD"].sum()
    else:
        daily = pd.Series(dtype=float)
    var95, es95 = var_es(daily)
    return {
        "equity_final": float(stats["Equity Final [$]"]),
        "max_drawdown_pct": float(stats["Max. Drawdown [%]"]),
        "win_rate_pct": float(stats["Win Rate [%]"]) if len(trades) else 0.0,
        "profit_factor": float(stats["Profit Factor"]) if len(trades) and stats["Profit Factor"] == stats["Profit Factor"] else 0.0,
        "n_trades": int(len(trades)),
        "real_pnl_usd": float(trades["RealPnL_USD"].sum()) if len(trades) else 0.0,
        "dubious_pct": float(dubious_pct(trades)),
        "var95_usd": var95,
        "es95_usd": es95,
    }


def format_report(results: dict[str, dict], symbol: str) -> str:
    lines = [
        "---",
        "tags: [synthesis, algo-methodology, risikomanagement, backtest]",
        "created: 2026-08-12",
        f"updated: {date.today().isoformat()}",
        "sources: [\"[[Risikomanagement (1% pro Trade)]]\", \"[[Kelly-Criterion & Value-at-Risk (Money Management)]]\"]",
        "---",
        "",
        "# Risk-Management-Vergleich (laufend)",
        "",
        f"**Generiert** von `algo/backtest_risk_compare.py {symbol}` -- ueberschreibt sich bei "
        "jedem Lauf komplett, kein manuell gepflegter Inhalt (siehe CLAUDE.md \"(laufend)\"-Muster). "
        "Gleiche Silver-Bullet-Signale, nur die Positionsgroesse variiert zwischen den drei Modulen "
        "(siehe [[../algo/README.md|algo/README.md]]). Drawdown-Kill-Switch (15%) laeuft bei allen "
        "drei mit.",
        "",
        "| Modul | Equity Final $ | Max DD % | Win Rate % | Profit Factor | Trades | Echte $-P&L | Dubious % | VaR95 $ | ES95 $ |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for name, r in results.items():
        lines.append(
            f"| {name} | {r['equity_final']:.0f} | {r['max_drawdown_pct']:.1f} | "
            f"{r['win_rate_pct']:.1f} | {r['profit_factor']:.2f} | {r['n_trades']} | "
            f"{r['real_pnl_usd']:+.0f} | {r['dubious_pct']:.1f} | {r['var95_usd']:.0f} | "
            f"{r['es95_usd']:.0f} |"
        )
    return "\n".join(lines) + "\n"


def main(argv=None) -> None:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("symbol", nargs="?", default="MNQ")
    a = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")

    df = load_series(a.symbol)
    print(f"{a.symbol}: {len(df)} Kerzen, {df.index[0]} bis {df.index[-1]}")

    results = {name: run_one(df, a.symbol, mod) for name, mod in MODULES.items()}
    for name, r in results.items():
        print(f"{name}: {r}")

    report = format_report(results, a.symbol)
    out = ROOT / "wiki" / "synthesis" / "Risk-Management-Vergleich (laufend).md"
    out.write_text(report, encoding="utf-8")
    print(f"\ngeschrieben: {out.relative_to(ROOT)}")


def demo() -> None:
    # 5 Tage: -100, -50, 0, 30, 500 -- bei 95% Konfidenz liegt das 5%-Quantil beim schlechtesten
    # Wert (nur 5 Datenpunkte -> Quantil faellt exakt auf den Minimalwert), VaR = 100, ES = 100
    # (Tail = nur dieser eine Tag).
    s = pd.Series([-100.0, -50.0, 0.0, 30.0, 500.0])
    var95, es95 = var_es(s, confidence=0.95)
    assert abs(var95 - 100.0) < 1e-6
    assert abs(es95 - 100.0) < 1e-6

    # Leere Reihe -> (0, 0)
    assert var_es(pd.Series(dtype=float)) == (0.0, 0.0)

    # Zwei gleich schlechte Tage im Tail -> ES ist deren Mittelwert, nicht nur einer
    s2 = pd.Series([-200.0, -200.0, -10.0, 5.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0])
    var95b, es95b = var_es(s2, confidence=0.95)
    assert var95b > 0
    assert es95b >= var95b  # ES ist per Konstruktion mindestens so extrem wie VaR (Tail-Mittel)

    print("backtest_risk_compare demo: OK")


if __name__ == "__main__":
    if "--selfcheck" in sys.argv:
        demo()
    else:
        main()
