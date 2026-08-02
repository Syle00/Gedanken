---
tags: [concept, ict, trading-ict, core]
created: 2026-08-01
updated: 2026-08-02
sources: ["[[Reeinforced Orderblock Theory Selecting & Avoiding (Source)]]", "[[Kurz Notizen (Source)]]", "[[ICT 2022 - Episode 13 Market Structure for Precision (Source)]]", "[[ICT 2022 - Episode 17 FX Anwendung (Source)]]"]
---

# Order Block

Basiskonzept: die letzte gegensätzliche Candle vor einem starken Displacement — Grundtyp der
[[PD Array]]. Spezialisierte Varianten: [[Breaker Block]], [[Rejection Block]],
[[Reclaimed Order Block]], [[Mitigation Block]].

## Validierung (Selecting & Avoiding)

- OB muss auf ein **Support-/Resistance-Level** treffen (altes High/Low = Liquidity Sweep), um
  relevant zu sein.
- Ein Bullish OB gilt als **validiert**, wenn eine Up-Closing-Candle über dem OB closed.

![[Screenshot_2025-01-21_071042.png]]
*Bullish OB validiert durch eine Upclosing Candle, die über dem OB closed — Support Level als altes High/Low.*
- **Theoretischer Reentry** ist bereits mit der nächsten Candle möglich, sobald diese das High des
  OB+ berührt — kein langes Abwarten auf ein vollständiges Zurücktraden nötig. Ein zweiter,
  sicherer validierter Reentry-Punkt eignet sich für die größte Limit-Order.

![[Screenshot_2025-01-21_070018.png]]
*Zweiter, sicher validierter Reentry-Punkt — eignet sich für die größte Limit-Order.*
- **Qualitätsmerkmal**: bei den besten OBs geht Preis nicht über das **50%-Level** des OB hinaus.

![[Screenshot_2025-01-21_070728.png]]
*Bei den besten Order Blocks geht Price nicht über das 50%-Level hinaus.*
- Nach Validierung erwartet ICT einen Spike von **2–3× der Candle-Range**, bevor das eigentliche
  Retracement kommt — das gibt mehr Spielraum für einen optimalen Einstieg.

## Wann ein OB überhaupt entstanden ist (MentorShip 2022)

> **Ein OB ist immer erst bestätigt, wenn danach ein Displacement folgt.**

Das ist die schärfste Formulierung im Vault dazu — und sie erklärt zugleich, warum ein OB aus
**mehreren Candles** bestehen kann: im Beispiel bilden **zwei Up-Closing Candles zusammen einen OB**,
weil nach beiden zusammen das Displacement in Form eines SIBI folgt. Gilt spiegelbildlich bullish.

![[ICT 2022 - Ep17 03.png]]
*Zwei Up-Closing Candles bilden zusammen einen Order Block — bestätigt durch das nachfolgende SIBI.*

## High Probability OB: zwei Pflichtmerkmale

Ein High-Probability-OB hat **immer** beides:

1. eine **Imbalance**, und
2. ein **eindeutiges Buy-/Sellside-Liquidity-Target**.

Fehlt das Target, ist der OB nicht high probability — er zeigt dann nicht, wohin geliefert werden
soll.

![[ICT 2022 - Ep13 03.png]]
*1H-OB im 15M ausgemalt; im Lower Timeframe das Displacement mit eindeutigem Target auf der
High-Probability-Buyside.*

## C.E / Mean Threshold bei Multi-Candle-OBs (Kurz Notizen)

- Besteht ein OB aus mehreren Candles, das **C.E bzw. den Mean Threshold** des OB prüfen: liegt das
  **Open der (letzten) Candle** genau auf oder sogar unter dem C.E, gilt der OB als **High
  Probability** — unwahrscheinlich, dass Preis überhaupt bis zum C.E oder tiefer zurücktradet.

![[Kurz Notizen - OB Mean Threshold Example.png]]
*Multi-Candle-OB: liegt das Open der Candle auf oder unter dem C.E, ist der OB High Probability.*

- **OB + FVG kombiniert**: Um bei einem OB/[[CISD (Change in State of Delivery)|CISD]] das
  zugehörige FVG zu bestimmen, die unterste (bullish) bzw. oberste (bearish) Candle des OB als
  Referenz nehmen — daraus ergibt sich das korrekte FVG.

## HTF-Nutzung & Bias

- Sehr wichtig: Order Blocks über Monthly → Weekly → Daily für den Bias nutzen — was ist
  wahrscheinlicher?
- In einem laufenden bullishen Trend ist **jede Down-Closing-Candle** ein potenzieller OB+.
- Im Higher Timeframe kommen bearishe OBs kaum vor — wenn doch, meist nur zur Profitsicherung.

## Verwandt

- [[PD Array]], [[Institutional Order Flow (Body vs Wick)]]
- [[Breaker Block]], [[Rejection Block]], [[Reclaimed Order Block]], [[Mitigation Block]]
- [[Fair Value Gap (FVG)]], [[CISD (Change in State of Delivery)]]
- [[Kurz Notizen (Source)]]
