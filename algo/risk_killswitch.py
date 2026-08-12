#!/usr/bin/env python3
"""Drawdown-Kill-Switch pro Strategie: haelt kompletten Handel an, wenn der Drawdown seit dem
bisherigen Equity-Hoch eine Schwelle ueberschreitet. Reset automatisch bei neuem Equity-Hoch
(kein manueller Reset noetig, `peak` ergibt sich immer aus der bisherigen Kurve). Siehe
docs/superpowers/specs/2026-08-12-quant-risk-management-design.md Abschnitt 2."""
from __future__ import annotations

DEFAULT_MAX_DRAWDOWN_PCT = 0.15


def allowed(equity_curve: list[float], max_drawdown_pct: float = DEFAULT_MAX_DRAWDOWN_PCT) -> bool:
    """False = kein neuer Trade erlaubt. `equity_curve` ist die bisherige Equity-Historie
    (aeltestes zuerst, letzter Wert = aktuell); leer -> immer erlaubt (noch keine Historie)."""
    if not equity_curve:
        return True
    peak = max(equity_curve)
    if peak <= 0:
        return True
    dd = (peak - equity_curve[-1]) / peak
    return dd < max_drawdown_pct


def demo() -> None:
    assert allowed([]) is True
    assert allowed([100_000]) is True
    # Knapp UNTER der Schwelle (14.999% Drawdown) -> noch erlaubt
    assert allowed([100_000, 85_001], 0.15) is True
    # Genau auf der Schwelle (15% Drawdown) -> SOFORT gestoppt (Schwelle erreicht = stop)
    assert allowed([100_000, 85_000], 0.15) is False
    # Ueber der Schwelle -> gestoppt
    assert allowed([100_000, 84_999], 0.15) is False
    # Reset bei neuem Hoch: Drawdown, dann neues Hoch -> peak folgt dem neuen Hoch,
    # ein erneuter kleiner Ruecksetzer bleibt unter der Schwelle
    curve = [100_000, 80_000, 110_000, 95_000]  # DD ab 110k: (110k-95k)/110k = 13.636...% < 15%
    assert allowed(curve, 0.15) is True
    print("risk_killswitch demo: OK")


if __name__ == "__main__":
    demo()
