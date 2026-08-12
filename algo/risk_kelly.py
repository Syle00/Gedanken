#!/usr/bin/env python3
"""Half-Kelly-Sizing aus rollierenden Trade-Ergebnissen (diskrete Trading-Kelly-Formel,
p - (1-p)/b, nicht die Portfolio-Rendite-Variante aus
wiki/concepts/Kelly-Criterion & Value-at-Risk (Money Management).md). Siehe
docs/superpowers/specs/2026-08-12-quant-risk-management-design.md Abschnitt 2. Nutzt
`closed_trades` aus backtesting.Strategy (nur abgeschlossene Trades vor dem aktuellen
Zeitpunkt -- kein Lookahead)."""
from __future__ import annotations

WINDOW = 30       # rollierendes Fenster ueber die letzten N abgeschlossenen Trades
MIN_TRADES = 20   # Fallback auf base_pct, solange weniger Trades vorliegen


def _kelly_fraction(pl_pcts: list[float]) -> float | None:
    """Reine Funktion auf einer Liste von Trade-Returns (pl_pct, in %): p = Trefferquote,
    b = avg_win/avg_loss (R-Multiple-Verhaeltnis), f* = p - (1-p)/b. None, wenn das Sample
    nicht gemischt ist (nur Gewinner oder nur Verlierer -- Formel dann nicht anwendbar)."""
    wins = [p for p in pl_pcts if p > 0]
    losses = [-p for p in pl_pcts if p < 0]
    if not wins or not losses:
        return None
    p = len(wins) / len(pl_pcts)
    b = (sum(wins) / len(wins)) / (sum(losses) / len(losses))
    return p - (1 - p) / b


def risk_pct(closed_trades=None, base_pct: float = 0.01, **ctx) -> float:
    """Half-Kelly ueber die letzten WINDOW abgeschlossenen Trades. Fallback auf base_pct,
    solange weniger als MIN_TRADES vorliegen oder das Sample nicht gemischt ist."""
    if closed_trades is None or len(closed_trades) < MIN_TRADES:
        return base_pct
    recent = list(closed_trades)[-WINDOW:]
    pl_pcts = [t.pl_pct for t in recent]
    f_star = _kelly_fraction(pl_pcts)
    if f_star is None:
        return base_pct
    return max(0.0, f_star / 2)


def demo() -> None:
    # --- _kelly_fraction(): Lehrbuchbeispiel, p=0.5, b=2 (Gewinne doppelt so gross wie
    # Verluste) -> f* = 0.5 - 0.5/2 = 0.25
    pl_pcts = [2.0, -1.0, 2.0, -1.0]
    assert abs(_kelly_fraction(pl_pcts) - 0.25) < 1e-9

    # Nur Gewinner oder nur Verlierer -> Formel nicht anwendbar
    assert _kelly_fraction([1.0, 2.0, 3.0]) is None
    assert _kelly_fraction([-1.0, -2.0]) is None

    # --- risk_pct(): Fallback unter MIN_TRADES ---
    from types import SimpleNamespace
    few = [SimpleNamespace(pl_pct=2.0 if i % 2 == 0 else -1.0) for i in range(MIN_TRADES - 1)]
    assert risk_pct(closed_trades=few, base_pct=0.01) == 0.01
    assert risk_pct(closed_trades=None, base_pct=0.01) == 0.01

    # --- risk_pct(): genug Trades, gemischtes p=0.5/b=2-Sample -> Half-Kelly = 0.125 ---
    enough = [SimpleNamespace(pl_pct=2.0 if i % 2 == 0 else -1.0) for i in range(MIN_TRADES)]
    pct = risk_pct(closed_trades=enough, base_pct=0.01)
    assert abs(pct - 0.125) < 1e-9

    # --- risk_pct(): nur Verlierer im rollierenden Fenster -> Fallback auf base_pct ---
    all_losses = [SimpleNamespace(pl_pct=-1.0) for _ in range(MIN_TRADES)]
    assert risk_pct(closed_trades=all_losses, base_pct=0.01) == 0.01

    print("risk_kelly demo: OK")


if __name__ == "__main__":
    demo()
