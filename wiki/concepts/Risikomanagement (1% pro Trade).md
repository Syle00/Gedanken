---
tags: [concept, risikomanagement, position-sizing, eigene-regel]
created: 2026-08-05
updated: 2026-08-06
sources: ["[[ICT Mentorship Core Content - Month 02 - No Fear Of Losing (Source)]]", "[[ICT Mentorship Core Content - Month 02 - Growing Small Accounts (Source)]]"]
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

## ✅ Quelle gefunden (2026-08-06): ICT Mentorship Core Content Month 02 (YouTube-Nachtrag)

Der zuvor offene Punkt (keine Prozent-Regel im damals durchsuchten Core-Content-Text gefunden)
ist jetzt geklärt: **Month 02** fehlte komplett im Notion-Export (siehe
[[Core Content 2016 (Source)]]) und wurde erst nachträglich über YouTube-Videos ingested — dort
steht die Regel explizit:

- [[ICT Mentorship Core Content - Month 02 - Growing Small Accounts (Source)]]: max. 2 %
  Risiko/Trade (ideal für neue Trader).
- [[ICT Mentorship Core Content - Month 02 - No Fear Of Losing (Source)]]: **1 % Risiko/Trade**
  bei 50 % Trefferquote + 5:1 RR als "optimales Trading-Ziel" — deckt sich exakt mit der hier
  bereits implementierten Regel.

Vollständige Herleitung inkl. Erwartungswert-Tabellen: [[Erwartungswert & Reward-to-Risk-Modell]].
Ergänzend dazu die Rest der Passung: [[Missed Entry Trade Management Playbook]] (Skalierung/
Reentry/Exit-Schema) und `raw/2026/Chain Of Custody Of Price With Daily Inefficiencies.md`
(Partial-Taking-Hinweis) waren die zuvor bereits gefundenen, nur teilweise passenden Belege.

## Verwandt

- [[Meine Strategien (Übersicht)]]
- [[Silver Bullet Model]] — erste Strategie, die diese Regel nutzt
- [[Missed Entry Trade Management Playbook]]
- [[Erwartungswert & Reward-to-Risk-Modell]]
- [[Verlust-Mitigation durch reduzierte Re-Entry-Size]]
