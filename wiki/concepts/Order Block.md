---
tags: [concept, ict, trading-ict, core]
created: 2026-08-01
updated: 2026-08-06
sources: ["[[Reeinforced Orderblock Theory Selecting & Avoiding (Source)]]", "[[Kurz Notizen (Source)]]", "[[ICT 2022 - Episode 13 Market Structure for Precision (Source)]]", "[[ICT 2022 - Episode 17 FX Anwendung (Source)]]", "[[ICT Mentorship Core Content - Month 04 - Orderblocks (Source)]]"]
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

## Rally-Away-Faustregel & HTF-Verfeinerung (2022er Video-Ergänzung)

Aus [[ICT Mentorship Core Content - Month 04 - Orderblocks (Source)]]:

- Nach der Validierung sollte Preis idealerweise **2–3× die eigene Range** wegrallieren, bevor das
  Retracement zurück zum OB erwartet wird — ein zu kleiner Wegzug (< 2×) macht den OB weniger
  verlässlich als Referenzpunkt.
- **Verfeinerung auf Nested Order Blocks**: entsteht während des Wegzugs eine **neue**, näher am
  aktuellen Preis liegende Down-/Up-Candle, die dieselbe Support-/Resistance-Prämisse bestätigt,
  wird diese zum bevorzugten (verfeinerten) Entry-Level — der ursprüngliche OB bleibt als
  Backup-Level gültig, wird aber nicht mehr priorisiert.
- **Monthly → Weekly → Daily-Kaskade**: derselbe OB wird auf jeder tieferen Timeframe neu gesucht
  und verfeinert (vgl. [[Risiko-Verfeinerung über Timeframes]] für dieselbe Technik im
  Reward-/Risiko-Kontext).
- **Multi-Candle-OB-Bestätigung**: zwei aufeinanderfolgende Down-Candles (bzw. Up-Candles bearish)
  zählen als **ein** zusammengesetzter Order Block, wenn beide zusammen von der validierenden
  Candle durchhandelt werden — bereits an anderer Stelle im Wiki dokumentiert (MentorShip 2022),
  hier durch ein zweites, unabhängiges Beispiel bestätigt.
- Entry/Exit-Rahmen: Order Block = [[External vs. Internal Range Liquidity|Internal Range
  Liquidity]] (Kauf-/Verkaufspunkt), altes High/Low = External Range Liquidity (Ziel).

## Verwandt

- [[PD Array]], [[Institutional Order Flow (Body vs Wick)]]
- [[Breaker Block]], [[Rejection Block]], [[Reclaimed Order Block]], [[Mitigation Block]], [[Propulsion Block]]
- [[Fair Value Gap (FVG)]], [[CISD (Change in State of Delivery)]]
- [[External vs. Internal Range Liquidity]]
- [[Kurz Notizen (Source)]]
