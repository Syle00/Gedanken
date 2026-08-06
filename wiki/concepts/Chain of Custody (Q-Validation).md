---
tags: [concept, ict, trading-ict, 2026]
created: 2026-08-01
updated: 2026-08-03
sources: ["[[ICT Chain Of Custody Of Price (Source)]]", "[[Chain Of Custody Of Price With Daily Inefficiencies (Source)]]", "[[2026-08-05 - ICT Price Action Chronicles - MOC Crushing The Buying & Selling Pressure Myth (Source)|ICT Price Action Chronicles - MOC Crushing The Buying & Selling Pressure Myth (Source)]]"]
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

## Oktanten (Os) und VII-Einschluss bei BISI/SIBI

Zweite Quelle ([[Chain Of Custody Of Price With Daily Inefficiencies (Source)]]) verfeinert das
Raster: neben den **Quadranten (Qs)** kommen **Oktanten (Os)** als feinere Fib-Unterteilung dazu.
Angewendet wird das Raster direkt auf ein [[BISI & SIBI (Buyside-Sellside Imbalance)|BISI/SIBI]]:

- Liegt am oberen *und* unteren Rand des BISI/SIBI je eine
  [[Volume Imbalance (VII)|VII]], zählen beide zur Range dazu — das **gesamte BISI inkl. VII** gilt
  dann als eine **Discount PD Array**.
- Bildet sich dabei ein FVG mit VII auf **beiden** Seiten, ist das ein
  [[Suspension Block]] — eine der stärksten PD Arrays überhaupt.
- **Partials**: an Quadranten/Oktanten, Liquidity-Leveln und NDOG werden, wo möglich, Teilgewinne
  genommen, um Risiko zu minimieren (vgl. [[Event Horizon]] als verwandter Partial-Marker).
- **No-Trade-Regel**: Verbringt Preis längere Zeit zwischen zwei Qs/Os und konsolidiert sichtlich,
  ist das **nicht High Probability** — unabhängig vom Zeitfenster wird kein Trade genommen.

## 16tel (halber Oktant) — 2026-Ergänzung (MOC-Video)

Das Raster geht noch eine Stufe feiner als Q/O: **Oktant halbiert = 16tel** (6,25 % der Range). Im
konkreten Beispiel am E-Mini S&P wurde ein 16tel-Level bei 7.761,75 projiziert, das Tagestief kam bei
7.761,25 — **2 Ticks Abweichung**. Details und Ablauf auf
[[Market on Close (MOC) Macro Model]].

## Verwandt

- [[Enigma FVG Projection]], [[Order Block]], [[Fair Value Gap (FVG)]]
- [[IFVG (Inverse Fair Value Gap)]]
- [[BISI & SIBI (Buyside-Sellside Imbalance)]], [[Suspension Block]], [[Event Horizon]]
- [[Market on Close (MOC) Macro Model]] — nutzt das 16tel-Level in der Praxis
- [[Kurz Notizen (Source)]], [[Chain Of Custody Of Price With Daily Inefficiencies (Source)]]
