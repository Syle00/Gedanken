"""Forex-Zwilling der MNQ-Algo-Schicht (Phase 2, siehe
docs/superpowers/specs/2026-08-15-forex-algo-phase2-design.md).

Bewusste Duplikation statt geteilter Basisklasse: die MNQ-Module (algo/pnl.py, algo/rules.py,
algo/backtest_bt.py, ...) werden nicht angefasst, damit ihre Zahlen unveraendert bleiben
(Nutzerentscheidung 2026-08-15). Geteilt und nur importiert werden die Schichten darunter --
tools/analyze_ohlc.py (Detektoren, Killzones, Tick-/Pip-Tabellen), algo/marktdaten.py (Loader),
algo/validate.py (Walk-Forward/Monte-Carlo), algo/risk_*.py, algo/confidence.py.

Der Preis dieser Entscheidung ist echte Drift: ein Bugfix in der FVG-Entry-Erkennung muss in
algo/rules.py UND algo/forex/rules.py gemacht werden. algo/forex/selfcheck.py enthaelt dafuer
einen Drift-Waechter, der meldet, wenn sich eine Seite bewegt hat und die andere nicht.
"""
