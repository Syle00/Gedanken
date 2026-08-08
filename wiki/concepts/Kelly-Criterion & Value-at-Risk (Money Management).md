---
tags: [concept, algo-methodology, risikomanagement]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[Successful Algorithmic Trading (Source)]]"]
---

# Kelly-Criterion & Value-at-Risk (Money Management)

Zwei quantitative Werkzeuge aus [[Successful Algorithmic Trading (Source)]] (Michael Halls-Moore)
für Positionsgrößen-/Hebel-Entscheidungen — Kelly für optimales Kapitalwachstum, VaR für
Verlustabschätzung. Beide ergänzen, ersetzen aber nicht, die bereits im Vault etablierte feste
[[Risikomanagement (1% pro Trade)]]-Regel (siehe Bezug unten).

## Kelly-Criterion

Bestimmt den **optimalen Hebel/Kapitalanteil** je Strategie, um die langfristige geometrische
Wachstumsrate zu maximieren: `f_i = µ_i / σ_i²` (µ = mittlere Excess-Return, σ = Standard-
abweichung der Excess-Returns einer Strategie `i`). Erwartete Wachstumsrate:
`g = r + S²/2` (r = risikofreier Zins, S = annualisierte Sharpe Ratio).

**Annahmen, die die Formel voraussetzt** (und die real selten exakt gelten): normalverteilte
Returns mit über die Zeit konstantem Mittelwert/Standardabweichung, Excess-Returns (netto aller
Finanzierungskosten), vollständige Reinvestition ohne Entnahmen, statistisch unabhängige
Strategien (keine Korrelation zwischen mehreren Strategien in einem Portfolio).

**Praxis-Warnungen aus der Quelle**:

- Kelly verlangt eigentlich kontinuierliches Rebalancing — in der Praxis wird täglich
  approximiert, mit einer rollierenden Lookback-Periode von 3-6 Monaten für Mean/Std.
  Kontraintuitives Verhalten: Kelly-Rebalancing kauft nach Gewinnen zu (erhöht den Hebel) und
  verkauft nach Verlusten (reduziert ihn) — mathematisch korrekt für Wachstumsmaximierung, aber
  emotional schwer auszuhalten.
- **Direkte Kelly-Nutzung kann zum Totalverlust führen**, weil reale Strategie-Returns nicht
  normalverteilt sind (die Grundannahme der Formel). Praxisstandard ist deshalb "**Half-Kelly**"
  (Kelly-Wert halbieren) — Kelly gilt als Obergrenze des sinnvollen Hebels, nicht als direkte
  Handlungsvorgabe.
- Kelly ist ein Framework für **Multi-Strategie-Portfolios** (Kapitalallokation zwischen mehreren
  unkorrelierten Strategien), nicht primär für Einzeltrade-Sizing.

## Value-at-Risk (VaR)

Schätzt, mit welcher Wahrscheinlichkeit (Konfidenzniveau, z.B. 95%/99%) ein Portfolio über einen
gegebenen Zeitraum nicht mehr als einen bestimmten Betrag verliert:
`P(Verlust ≤ −VaR) = 1 − Konfidenzniveau`. Berechnungsmethoden: Varianz-Kovarianz-Methode
(Normalverteilungsannahme, im Buch vertieft), Monte-Carlo-Methode, historisches Bootstrapping.

**Vorteile**: einfach zu berechnen, auf Einzelinstrument/Strategie/Gesamtportfolio anwendbar,
zeitraum-flexibel, leicht auch gegenüber Nicht-Technikern zu kommunizieren.

**Nachteile**: sagt nichts über die Verlusthöhe JENSEITS des VaR-Werts aus (kein Tail-Risk),
berücksichtigt keine Extremereignisse, ist rückwärtsgewandt (historische Volatilität/Korrelation
≠ zukünftige). Sollte nie isoliert, sondern immer zusammen mit Diversifikation und Hebel-Disziplin
verwendet werden.

## Bezug zu diesem Projekt

Dieses Projekt nutzt aktuell eine **feste, statistik-unabhängige Regel**
([[Risikomanagement (1% pro Trade)]]: nie mehr als 1% Kontoguthaben Risiko pro Trade) statt
Kelly/VaR — bewusst einfacher, aber nicht formal wachstumsoptimiert. `algo/pnl.py::risk_size()`
implementiert bereits eine `max_notional`-Margin-Deckelung (siehe `algo/PLAN.md`-Log
2026-08-07), was strukturell in dieselbe Richtung wie eine Kelly-Obergrenze geht, aber ohne die
statistische Herleitung über Mean/Varianz der Strategie-Returns. Kein akuter Backlog-Punkt: Kelly
würde eine belastbare Schätzung von Mittelwert/Standardabweichung der Strategie-Returns
voraussetzen, die laut `algo/validate.py`-Ergebnissen bei der aktuellen Datenmenge (siehe
"Kleine Stichprobe"-Einschränkung, `algo/README.md`) noch nicht robust genug ist. VaR wäre
unabhängig davon als zusätzliche Kennzahl in `algo/dashboard.py`/`algo/live_status.py` denkbar,
aktuell aber nicht beauftragt.
