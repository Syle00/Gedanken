---
tags: [concept, risikomanagement, position-sizing, eigene-regel]
created: 2026-08-05
updated: 2026-08-05
sources: []
---

# Risikomanagement (1% pro Trade)

Eigene, feste Regel (kein ICT-Quellenzitat) — gilt **strategieübergreifend** für jedes Setup in
[[Meine Strategien (Übersicht)]], nicht nur für [[Silver Bullet Model]].

> ⚠️ **Korrektur vom 2026-08-05**: diese Seite hieß zunächst "Risikomanagement (1% Tagesrisiko)"
> mit einem kumulativen Tagesbudget über mehrere Trades. Das war falsch verstanden — die Regel
> gilt **pro Trade**, nicht pro Tag. Vom Nutzer korrigiert.

## Die Regel

> Ich trade nie mehr als **1% meines Kontoguthabens** Risiko **pro Trade**.

Jeder Trade wird unabhängig von anderen Trades desselben Tages auf 1% Risiko bemessen — kein
gemeinsames Tagesbudget, keine Reduktion der Größe, weil am selben Tag schon ein anderer Trade
lief.

## Positionsgrößen-Formel

```
Budget         = Kontoguthaben (aktuelles Equity, nicht Startkapital) × 1%
Stop-Abstand   = |Entry − Stop|  (in Punkten/Handle)
Positionsgröße = floor(Budget / Stop-Abstand)
```

Reicht das Budget nicht für mindestens 1 Einheit (extrem enger Markt/hoher Preis), wird der
Trade nicht genommen.

## Implementierung im Backtest

- `algo/backtest_ensemble.py::_risk_size(equity, max_pct, entry, stop)` — reine Funktion,
  die die obige Formel berechnet (mit Selfcheck in `_demo()`).
- `EnsembleStrategy.max_risk_pct = 0.01` — Default, überschreibbar.
- Betrifft nur den Intraday-Zweig (`intraday=True`, [[Silver Bullet Model]]-Setups mit
  explizitem Stop). Der Tages-Bias-Fallback (`intraday=False`, siehe `algo/stress_test.py`)
  hat keinen expliziten Stop und bleibt bei der Standard-Backtesting.py-Größe.
- Zusätzlich gekappt durch `EnsembleStrategy.leverage` (20x, muss zum `Backtest(margin=0.05)`
  der Aufrufer passen): bei sehr engem Stop könnte die 1%-Regel rechnerisch mehr Kontrakte
  verlangen, als das Konto-Margin hergibt — ohne diese Kappung hätte der Broker die Order
  einfach storniert (kompletter Trade-Ausfall) statt sie kleiner zu füllen.

## Offener Punkt: Quelle der Regel

Der Nutzer verortet die Money-Management-/Drawdown-Regeln generell im ICT-Quellenmaterial
("Core Content"). Durchsucht (Volltext + [[Smart Money Concepts (SMC)|Graphify-Query]]):
`raw/trading-ict/` komplett (Core Content + alle Jahrgänge) nach %-Angaben, "risk",
"drawdown", "money management", "position size", "Konto", "Verlust" — **keine explizite
Prozent-Regel zur Positionsgröße gefunden**. Am nächsten dran:

- [[Missed Entry Trade Management Playbook]] — Skalierung/Reentry/Exit-Schema, aber ohne
  %-Bezug zum Kontoguthaben.
- `raw/2026/Chain Of Custody Of Price With Daily Inefficiencies.md`: *"wenn möglich nehmen wir
  an Key Leveln ... Partials ... um unser Risiko zu minimieren"* — deckt sich mit dem
  Partial-Teil in [[Silver Bullet Model]], aber ohne Zahl.

Möglich, dass die eigentliche Money-Management-Regel nur in einem der vielen Screenshots steht
(reiner Bildinhalt, nicht textuell erfasst) statt im Fließtext — die 1%-Regel bleibt bis zur
Nutzer-Bestätigung/-Korrektur als **eigene, unverknüpfte Regel** hier stehen.

## Verwandt

- [[Meine Strategien (Übersicht)]]
- [[Silver Bullet Model]] — erste Strategie, die diese Regel nutzt
- [[Missed Entry Trade Management Playbook]]
