---
tags: [synthesis, algo, backtest, ensemble, generiert]
created: 2026-08-05
updated: 2026-08-05
sources: ["[[../../algo/backtest_ensemble.py]]", "[[../../algo/PLAN.md]]"]
---

# Ensemble-Strategie — Backtest-Ergebnis & Commission-Verzerrung (laufend)

Antwort auf die Nutzerfrage "hast du Ideen wie ich profitabel werde?" — Ergebnis eines vollen
In-Sample-Laufs von `EnsembleStrategy` (48 Handelstage MNQ, alle Regeln aus
[[Silver Bullet Model]] + [[Risikomanagement (1% pro Trade)]] Stand 2026-08-05).

## Kennzahlen

| Kennzahl | Wert |
|---|---|
| Return | -0,89% |
| Profit Factor | 1,48 |
| Win Rate | 32,4% |
| Sharpe Ratio | 0,13 |
| Kelly Criterion | -0,01 (negativ) |
| SQN | -0,07 |
| Commissions | $19.757 |
| Max Drawdown | -15,7% |
| # Trades | 34 |

## Hauptbefund: Commission-Modell verzerrt das Ergebnis massiv

Profit Factor >1 bei gleichzeitig negativem Return ist der Schlüssel: Netto-Verlust
(-885,67 $) + Commissions (19.757 $) = **brutto ca. +18.870 $ (+18,9%)**.

`BT_KWARGS = dict(commission=0.0002)` (in `backtest_walkforward.py`, `validate_ensemble.py`,
`stress_test.py`, `backtest_bt.py`) berechnet Kommission als **Prozent vom Notional-Wert** —
das Modell für Aktien/Forex. Echte Futures-Broker berechnen einen **Fixbetrag pro Kontrakt**
(MNQ real ca. 0,50–1,50 $ Roundtrip/Kontrakt), unabhängig vom Preis. Bei den hier üblichen
Positionsgrößen (12–70 Kontrakte, siehe [[Risikomanagement (1% pro Trade)]]) multipliziert das
Prozent-Modell die echten Kosten um ein Vielfaches — verschärft durch das neue Partial-Taking
(jeder Trade jetzt 3 statt 2 Commission-Events: Entry, Partial-Exit, Final-Exit).

**Höchster Hebel für Profitabilität**: Commission-Modell auf Fixbetrag/Kontrakt umstellen,
kompletten Stack neu laufen lassen.

## Vorsicht vor der +18,9%-Zahl

n=34 Trades auf 48 Tagen ist eine sehr kleine Stichprobe, und dieser Lauf war reiner
**In-Sample** (`bt.run()`, kein Walk-Forward mit Per-Fold-Refit). SQN -0,07 und negatives
Kelly-Criterion zeigen: selbst mit dem Profit-Factor-Edge ist die Trade-zu-Trade-Qualität
(noch) schwach/instabil. Nicht als bestätigte Profitabilität werten, bevor Walk-Forward +
realistische Kosten das bestätigen.

## Bereits nachweislich widerlegte Ansätze (nicht wiederholen)

- Silver Bullet ohne Bias-Filter: Profit Factor <1 bei jedem `stop_buffer_pct`, Walk-Forward OOS
  durchgehend negativ, Monte-Carlo-95.-Perzentil nie profitabel (siehe `algo/PLAN.md`-Log 2026-08-05).
- [[TGIF (Thank God its Friday)]] 20–30%-Retracement: nur 3,7% exakte Trefferquote.
- [[New Week Opening Gap (NWOG) Bias]] "Bias intakt": nur 7,1%.
- Rundzahl-Magnetismus: kein Effekt (siehe [[Statistische Muster jenseits der ICT-Konzepte (laufend)]]).

## Bereits als Signal in der Bias-Regression enthalten (nicht doppelt hinzufügen)

- Montags-Effekt (78,6% bullish, +0,71% Ø-Rendite) aus [[Seasonal Tendency (Eigene Daten, laufend)]]
- Range-Autokorrelation (r=0,305) aus [[Statistische Muster jenseits der ICT-Konzepte (laufend)]]

Beide fließen schon über `algo/signals.py` in `fit_model()` ein.

## Nächste Schritte (Priorität)

1. Commission-Modell auf Fixbetrag/Kontrakt umstellen, gesamten Stack neu validieren.
2. Walk-Forward (nicht nur Einzellauf) für die aktuelle Regelmenge (min-10pt-Filter,
   Partial+Breakeven, 1%-Sizing) — bisher nur die Vorstufe walk-forward-validiert.
3. `algo/stress_test.py`-Ergebnisse (5 Krisenfenster) tatsächlich auswerten — Skript existiert
   seit heute, Ergebnis nie gelesen/dokumentiert.
4. `partial_portion` und `min_target_points` parameter-sensitivitätstesten (wie `stop_buffer_pct`
   bereits getestet wurde) — beide neue, ungetestete Freiheitsgrade bei kleinem Sample.

## Verwandt

- [[Silver Bullet Model]], [[Risikomanagement (1% pro Trade)]], [[Meine Strategien (Übersicht)]]
- [[Statistische Muster jenseits der ICT-Konzepte (laufend)]], [[Seasonal Tendency (Eigene Daten, laufend)]]
- [[Makro-FRED-Zusammenhaenge (Eigene Daten, laufend)]]
