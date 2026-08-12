#!/usr/bin/env python3
"""Baseline-Risk-Modul: reine Auslagerung der bisherigen festen 1%-Regel (siehe
wiki/concepts/Risikomanagement (1% pro Trade).md) hinter das gemeinsame risk_pct()-Interface,
siehe docs/superpowers/specs/2026-08-12-quant-risk-management-design.md. Kein
Verhaltensunterschied zum bisherigen Stand -- Default-Modul in SilverBulletStrategy.
"""
from __future__ import annotations


def risk_pct(base_pct: float = 0.01, **ctx) -> float:
    """Ignoriert jeden Kontext (`hist`, `closed_trades`, ...) -- liefert immer `base_pct`."""
    return base_pct


def demo() -> None:
    assert risk_pct() == 0.01
    assert risk_pct(base_pct=0.02) == 0.02
    # Kontext-Kwargs (wie sie backtest_bt.py mitschickt) duerfen das Ergebnis nicht beeinflussen
    assert risk_pct(base_pct=0.01, hist=[1, 2, 3], closed_trades=["x"]) == 0.01
    print("risk_fixed demo: OK")


if __name__ == "__main__":
    demo()
