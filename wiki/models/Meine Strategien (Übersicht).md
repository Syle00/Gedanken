---
tags: [model, strategie, übersicht, eigene-regel]
created: 2026-08-05
updated: 2026-08-05
sources: []
---

# Meine Strategien (Übersicht)

Diese Seite ist der **Einstiegspunkt für alle live-getradeten Strategien** — abzugrenzen von der
allgemeinen ICT-Konzeptbibliothek unter `wiki/concepts/` und `wiki/models/`. Eine "Strategie"
hier bedeutet: vollständig geregelt (Entry, Stop, Target, Trade-Management, Position-Sizing) und
im Algo-Backtest (`algo/`) hinterlegt — nicht nur eine ICT-Idee, die getestet wurde.

**Zweck:** jede Strategie bekommt eine eigene Wiki-Seite, damit sie beim Backtesten als
verbindliche Regelquelle nachschlagbar ist statt aus dem Chatverlauf rekonstruiert zu werden.
Neue Strategie → eigene Seite unter `wiki/models/`, hier verlinkt, plus Eintrag in
`algo/rules.py` bzw. eine eigene `algo/backtest_*.py`.

## Strategieübergreifende Regeln

Gilt für **jede** Strategie unten, unabhängig vom Setup:

- [[Risikomanagement (1% pro Trade)]] — Positionsgröße richtet sich nach Kontoguthaben, nie
  mehr als 1% Risiko pro Trade (unabhängig von anderen Trades desselben Tages).

## Strategien

| Strategie | Entry | Trade Management | Algo-Umsetzung |
|---|---|---|---|
| [[Silver Bullet Model]] | FVG-C.E. in einem der drei Zeitfenster, Ziel = nächste unberührte Liquidität, min. 10 Punkte Potenzial | Partial am ersten Swing-Punkt in Traderichtung, danach Stop auf Breakeven | `algo/rules.py::plan_trade`, `algo/backtest_ensemble.py::EnsembleStrategy` |

## Noch keine eigenen Strategien (nur Backtest-Explorationen)

Diese Setups sind im Algo gegen historische Daten getestet, aber **nicht** vollständig als
eigene Strategie geregelt (kein festes Entry/SL/TP/Management-Set) — Kandidaten für eine eigene
Seite hier, sobald konkrete Regeln dazu vorliegen:

- TGIF-Retracement (`algo/backtest_tgif.py`) — siehe [[TGIF (Thank God its Friday)]]
- NDOG/NWOG-Fill (`algo/backtest_ndog.py`, `algo/backtest_nwog.py`)
- ORG-C.E.-70%-These (`algo/backtest_org_ce.py`) — siehe [[ORG (Opening Range Gap) & 1st Presented FVG]], Backtest liegt bei 35–43% statt 70%, wird trotzdem weiterverfolgt
- Midnight-Range-Judas/STD (`algo/backtest_midnight_range_judas.py`, `algo/backtest_midnight_range_std.py`)
- Saisonale/Wochentags-Muster (`algo/backtest_seasonal.py`, `algo/backtest_daily_patterns.py`)

## Verwandt

- [[Silver Bullet Model]], [[Risikomanagement (1% pro Trade)]]
- [[Smart Money Concepts (SMC)]] — Wurzelseite der allgemeinen ICT-Konzeptbibliothek
