---
tags: [concept, ict, trading-ict, risikomanagement, timeframes]
created: 2026-08-06
updated: 2026-08-06
sources: ["[[ICT Mentorship Core Content - Month 02 - Framing Low Risk Trade Setups (Source)]]", "[[ICT Mentorship Core Content - Month 02 - How Traders Make 10% Per Month (Source)]]"]
---

# Risiko-Verfeinerung über Timeframes

Technik, um den Stop-Loss eines HTF-Setups zu verkleinern, **ohne das Ziel oder die
institutionelle Prämisse zu ändern**: dieselbe HTF-[[PD Array]] (z.B. ein daily Bullish
[[Order Block]]) wird auf sukzessiv tieferen Timeframes erneut lokalisiert — dort entsteht
jeweils ein frischerer, näher am Preis liegender Order Block auf demselben institutionellen
Level, der einen deutlich engeren Stop erlaubt.

## Ablauf (Beispiel AUDUSD, 0.7512-Level)

| Timeframe | Order Block / Entry | Stop-Abstand |
|---|---|---|
| Daily | HTF-Referenzlevel 0.7512 (Bullish OB) | — (nur Kontext) |
| 1H | Entry 0.7542 | 20 Pips |
| 15M | Entry 0.7520 | 17 Pips |
| 5M | Entry ~0.7515 | < 10 Pips (konkret 8 Pips) |

Auf jeder Stufe bleibt das **Ziel identisch** (die auf dem Daily/1H identifizierten Buy-Stops
über den alten Highs) — nur der Entry rückt näher an das HTF-Level heran, wodurch derselbe
Preis-Move ein deutlich höheres R-Multiple ergibt (im Beispiel: 3R auf dem 5M-Timeframe für
denselben Move, der auf dem 1H nur 1R gewesen wäre).

## Voraussetzung

Funktioniert nur, wenn die tiefere Timeframe **denselben Grund** liefert, warum Preis dort
reagieren sollte — d.h. es muss tatsächlich ein neuer, gültiger Order Block auf dem Weg zum
HTF-Level sein, kein beliebig enger Stop ohne strukturelle Begründung. ICT warnt explizit vor
"Ultra short stop-loss" ohne Verständnis, warum Preis genau dort reagieren soll.

## Verwandt

- [[Three Timeframe Framing]] — verwandt, aber andere Fragestellung: dort geht es um die
  **Rollenverteilung** (Kontext/Framing/Timing) je Timeframe-Tripel, hier um das gezielte
  **Verkleinern des Stops** durch Wechsel auf tiefere Timeframes bei gleichbleibendem Ziel.
- [[Order Block]], [[PD Array]]
- [[Erwartungswert & Reward-to-Risk-Modell]] — engerer Stop bei gleichem Ziel treibt das R-Multiple
- [[Partial Profit-Taking & R-Multiple-Skalierung]]
