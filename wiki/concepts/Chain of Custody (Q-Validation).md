---
tags: [concept, ict, trading-ict, 2026]
created: 2026-08-01
updated: 2026-08-10
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
- **Größere Qs sind relevanter** als kleinere. Besonders relevant: das **0,5-C.E.** der
  antizipierten Dealing Range (aus Wick/FVG projiziert → C.E., nicht Mean Threshold) — erfolgt dort
  ein Displacement, soll dieses Gap als **Measuring Gap**
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

## 16tel / Hexadezimant (Hs) — 2026-Ergänzung (MOC-Video)

Das Raster geht noch eine Stufe feiner als Q/O: **Oktant halbiert = 16tel** (6,25 % der Range),
Kurzform **Hs** (Hexadezimant), analog zu Qs (Quadranten) und Os (Oktanten). Im konkreten Beispiel
am E-Mini S&P wurde ein 16tel-Level bei 7.761,75 projiziert, das Tagestief kam bei 7.761,25 —
**2 Ticks Abweichung**. Details und Ablauf auf [[Market on Close (MOC) Macro Model]].

## Terminologie: Qs / Os / Hs

Ein einheitliches Fib-Raster in drei Verfeinerungsstufen, anwendbar auf jede Range (Wick, ORG,
NDOG/NWOG, FVG, OB, BISI/SIBI):

| Kürzel | Name | Unterteilung | Level-Abstand |
|---|---|---|---|
| **Qs** | Quadranten | Range / 4 | 25 % |
| **Os** | Oktanten | Range / 8 | 12,5 % |
| **Hs** | Hexadezimanten | Range / 16 | 6,25 % |

**0,5-Level je nach PD-Array-Typ benannt** (nicht synonym): Es ist immer das 50-%-Level der Range,
heißt aber unterschiedlich —

- **Wick** und **[[Fair Value Gap (FVG)|FVG]]** → **C.E. (Consequent Encroachment)**.
- **[[Order Block]] und alle seine Varianten** — [[Breaker Block]], [[Rejection Block]],
  [[Mitigation Block]], [[Propulsion Block]], [[Reclaimed Order Block]] — sowie
  **[[CISD (Change in State of Delivery)|CISD]]** → **Mean Threshold**.

Also: C.E. ≠ Mean Threshold, es sind zwei Namen für dasselbe Fib-Level bei verschiedenen
Array-Typen. Merksatz: **jeder Order-Block-Abkömmling nutzt „Mean Threshold"**, alles vom Typ
Wick/Gap nutzt „C.E.".

> **Standardverfahren ab jetzt**: Fragt der Nutzer nach den Qs, Os oder Hs einer Range (z.B. einer
> Premium Wick oder des ORG), immer eine vollständige tabellarische Übersicht aller Level dieser
> Stufe berechnen und ausgeben (High/Low der Range, dann jedes Q/O/H-Level mit Preis), nicht nur
> das angefragte Einzellevel.
>
> **Erweiterung (2026-08-10)**: Auch **ohne explizite Nachfrage** — sobald der Nutzer in einem
> Daily/Weekly Bias von **Wicks oder FVGs** spricht, automatisch die Qs/Os/Hs-Tabelle für die
> relevante Range dazu erstellen und prüfen, **welche Level Preis bereits respektiert hat**
> (Reaktion/Close/Wick-Reject an dem Level) — mit besonderem Fokus auf das **C.E.** (das 0,5-Level;
> bei Wick/FVG so genannt, bei OB/CISD hieße es Mean Threshold), da ein gehaltenes C.E. laut obiger
> Regel die PD Array als stark validiert.

## Verwandt

- [[Enigma FVG Projection]], [[Order Block]], [[Fair Value Gap (FVG)]]
- [[IFVG (Inverse Fair Value Gap)]]
- [[BISI & SIBI (Buyside-Sellside Imbalance)]], [[Suspension Block]], [[Event Horizon]]
- [[Market on Close (MOC) Macro Model]] — nutzt das 16tel-Level in der Praxis
- [[Kontraktspezifikation MNQ (Tick, Punktwert)]] — Qs/Os/Hs teilen eine Range selten glatt;
  die Level müssen auf das 0,25-Tick-Raster gerundet werden, sonst sind es keine handelbaren Preise
- [[Kurz Notizen (Source)]], [[Chain Of Custody Of Price With Daily Inefficiencies (Source)]]
