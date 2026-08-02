---
tags: [concept, ict, trading-ict, 2026]
created: 2026-08-01
updated: 2026-08-02
sources: ["[[ICT Chain Of Custody Of Price (Source)]]"]
---

# Chain of Custody (Q-Validation)

Baut auf [[Enigma FVG Projection]] auf (Unrealised/Implied Dealing Range). Ein FVG rund um ein
Key Level (z.B. eine Daily Wick mit klarem DOL) wird genutzt: Fib vom High/Low der 2. FVG-Candle bis
zum DOL gezogen, um die **gesamte Dealing Range** zu antizipieren.

## Validierung über "Qs"

- Die entlang der antizipierten Range ausgemalten **Q-Level** (Quadranten/Fib-Zwischenmarken)
  validieren eine PD Array: geht ein FVG **durch ein Q** (überlappend), gilt das als Bestätigung,
  dass die PD Array **stark ist und hält** — gilt genauso für andere PD-Typen wie [[Order Block]]s
  (macht einen OB ab diesem Moment "validiert").
- **Größere Qs sind relevanter** als kleinere. Besonders relevant: das **0,5-Mean-Threshold** der
  antizipierten Dealing Range — erfolgt dort ein Displacement, soll dieses Gap als **Measuring Gap**
  fungieren und **nicht gefüllt** werden (kein Retracement dorthin erwartet).
- Auf den Qs können sich weitere Imbalances bilden — Voraussetzung ist eine korrekt eingezeichnete
  antizipierte Dealing Range.
- Funktioniert auch im Higher Timeframe (z.B. FVG genau auf dem 0,5-Mean-Threshold im 1H-Chart als
  IFVG).

![[image 41.png]]
*Konvergenz mehrerer RTH-C.E-Level: deutet auf eine große Daily Range hin.*

## High-Probability-FVG über Q-Lage (Kurz Notizen)

High-Probability-FVGs bilden sich bevorzugt an Quadranten (Q) von Wicks, FVGs, ORGs, NDOGs, NWOGs
etc. Damit es wirklich High Probability ist, MUSS das Q **innerhalb** des FVG selbst liegen — und
beide Candles, die das FVG bilden, müssen das Q ebenfalls überschreiten (bullish: über das Q,
bearish: unter das Q).

![[Kurz Notizen - High Probability FVG Quadrant Example 1.png]]
![[Kurz Notizen - High Probability FVG Quadrant Example 2.png]]
![[Kurz Notizen - High Probability FVG Quadrant Example 3.png]]
![[Kurz Notizen - High Probability FVG Quadrant Example 4.png]]
![[Kurz Notizen - High Probability FVG Quadrant Example 5.png]]
*Beispielserie: High-Probability-FVG, dessen Q innerhalb des FVG liegt und von beiden FVG-Candles überschritten wird.*

## Verwandt

- [[Enigma FVG Projection]], [[Order Block]], [[Fair Value Gap (FVG)]]
- [[IFVG (Inverse Fair Value Gap)]]
- [[Kurz Notizen (Source)]]
