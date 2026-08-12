#!/usr/bin/env python3
"""Drawdown-Kill-Switch pro Strategie: haelt kompletten Handel an, wenn der Drawdown seit dem
bisherigen Equity-Hoch eine Schwelle erreicht. Reset automatisch bei neuem Equity-Hoch (kein
manueller Reset noetig, der Aufrufer fuehrt `peak` inkrementell mit).

Wichtig zum Verhalten im Backtest: solange keine Position offen ist, bewegt sich die Equity
nicht, also kann auch kein neues Hoch entstehen -- ein ausgeloester Kill-Switch ist damit
praktisch ein Dauerstopp, bis wieder eine Position offen ist und die Equity sich bewegt. Das ist
im Backtest-Stadium **beabsichtigtes, konservatives Verhalten** (Nutzerentscheidung, siehe
docs/superpowers/specs/2026-08-12-quant-risk-management-design.md), kein Bug: kein Auto-Reset per
Timer/Decay.

Siehe docs/superpowers/specs/2026-08-12-quant-risk-management-design.md Abschnitt 2."""
from __future__ import annotations

DEFAULT_MAX_DRAWDOWN_PCT = 0.15


def allowed(peak: float, current: float,
            max_drawdown_pct: float = DEFAULT_MAX_DRAWDOWN_PCT) -> bool:
    """False = kein neuer Trade erlaubt. `peak` = bisheriges Equity-Hoch (vom Aufrufer
    inkrementell mitgefuehrt, siehe SilverBulletStrategy._equity_peak -- vermeidet ein
    max() ueber die volle Kurve pro Bar, O(n) statt O(n²)), `current` = aktuelle Equity.
    Beide in ECHTEN Dollar, nicht in Lib-Punkteinheiten (siehe pnl.py::risk_size()-Docstring).
    peak <= 0 -> immer erlaubt (noch keine Historie)."""
    if peak <= 0:
        return True
    dd = (peak - current) / peak
    return dd < max_drawdown_pct


def demo() -> None:
    assert allowed(0.0, 0.0) is True           # keine Historie
    assert allowed(100_000, 100_000) is True
    # Knapp UNTER der Schwelle (14.999% Drawdown) -> noch erlaubt
    assert allowed(100_000, 85_001, 0.15) is True
    # Genau auf der Schwelle (15% Drawdown) -> SOFORT gestoppt (Schwelle erreicht = stop)
    assert allowed(100_000, 85_000, 0.15) is False
    # Ueber der Schwelle -> gestoppt
    assert allowed(100_000, 84_999, 0.15) is False
    # Reset bei neuem Hoch: peak folgt dem neuen Hoch (110k), ein erneuter Ruecksetzer auf 95k
    # bleibt unter der Schwelle: (110k-95k)/110k = 13.636...% < 15%
    assert allowed(110_000, 95_000, 0.15) is True
    print("risk_killswitch demo: OK")


if __name__ == "__main__":
    demo()
