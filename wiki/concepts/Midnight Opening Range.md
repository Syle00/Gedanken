---
tags: [concept, ict, trading-ict, lecture-2025, sessions, london]
created: 2026-08-02
updated: 2026-08-10
sources: ["[[SMC Midnight Opening Range (Source)]]", "[[London Opening Range +1p FVG (Source)]]", "[[Making Money With SMC Concepts (Source)]]", "[[2026-08-10 - Navigating High Resistance Liquidity Run Conditions (Source)|Navigating High Resistance Liquidity Run Conditions (Source)]]"]
---

# Midnight Opening Range

Die Range von **0:00 bis 0:30 Uhr NY-Zeit** (im ETH-Chart). Um Punkt 0 Uhr wird der Algorithmus
zurückgesetzt und der neue, "richtige" Handelstag beginnt — bereits **innerhalb dieser halben
Stunde** wird das High/Low festgelegt, das in den meisten Fällen die **London Session** liefert.

> ⚠️ **Nicht verwechseln.** Die Quelle stellt ausdrücklich klar: das
> [[ORG (Opening Range Gap) & 1st Presented FVG|Opening Range Gap]] (16:14-Close → 9:30-Open) ist
> **weder** das New Day Opening Gap **noch** die Midnight Opening Range. Drei verschiedene Dinge.

## Aufbau

Drei markante Punkte:

1. **Midnight Opening Price** (0 Uhr)
2. **Range High**
3. **Range Low**

High und Low werden mit einem **Fib** markiert (die Wicks mitnehmen), das 0-Uhr-Opening zusätzlich
einzeichnen.

![[ICT 2025 - Midnight ORG 01.png]]
*Midnight Opening Range 0:00–0:30 mit Fib (0 / 0.25 / 0.5 / 1) und markiertem Midnight Open.*

Innerhalb der Range wird nach **PD Arrays aus der Matrix** gesucht — FVG, Order Block, Breaker Block,
Inefficiencies (siehe [[PD Array]]).

## Standard-Deviation-Projektion

Der Fib über die Range wird mit **negativen Standard Deviations** verlängert, um Tages-High/-Low zu
antizipieren:

- Genannt werden **−0,5 bis −5** (in einem Beispiel liegt das Tages-Low in London sogar bei **−6 STD**).
- Entscheidend: die STD-Level allein reichen nicht — sie müssen **mit Liquidity Pools und/oder FVGs
  zusammenfallen**. Erst dann wird es präzise.

### Manipulations-Grenze: −1 STD

- **−0,5 und −1 STD sind die Manipulations-Targets.** Die **maximale Manipulation geht bis −1 STD** —
  weiter lässt der Algorithmus sie nicht laufen.
- Geht Preis **darüber hinaus**, ist es **keine Manipulation mehr, sondern der eigentliche Move**.
- Es kommt außerdem oft vor, dass es **gar keine Manipulation** über die Opening Range gibt — dafür
  braucht es dann einen klaren Bias mit guten PD Arrays.
- Diese Grenze gilt **nur für London**. Nach der London Session kann Preis über die STD-Targets
  hinausgehen, etwa an einem NY-AM-Reversal- oder Consolidation-Tag.

![[ICT 2025 - London ORG 02.png]]
*Fib mit negativen Standard Deviations über die Opening Range: −0,5 und −1 als Manipulations-Targets.*

Dasselbe Verfahren lässt sich auch auf ein **einzelnes FVG** anwenden (−0,5 / −1) — gerade beim
1. presented Displacement werden diese Level über die London Session hinweg respektiert.

## Gilt den ganzen Tag

> Die Midnight Range ist **den ganzen Tag aktiv**, inklusive ihrer STD-Level. Bevor irgendetwas
> anderes gemacht wird, geht man auf die Midnight Range zurück — sie wird den ganzen Tag respektiert.

## Midnight Opening Price: Magnet und Widerstand zugleich (Live-Trade 2026-08-10)

Aus
[[2026-08-10 - Navigating High Resistance Liquidity Run Conditions (Source)|Navigating High Resistance Liquidity Run Conditions (Source)]]
— der reine **Opening Price** (Punkt 1 oben) als eigenständiges Handelsziel, unabhängig von der
0:00–0:30-Range:

- *"The midnight opening price is something I teach. It's like a magnet. It's a very strong draw on
  liquidity."* Er trägt einen **Session-Bias**, nicht zwingend den Daily Bias — das reicht als
  Prämisse für einen Intraday-Trade aus.
- Praktische Nutzung als **erstes Partial-Ziel**: Im Beispiel wurden 5 von 12 Kontrakten knapp
  **unter** dem MOP (29.878,25) realisiert, statt auf einen Durchbruch zu setzen.
- Von unten angelaufen wirkt er zugleich als **massiver Widerstand** ("offering a whole lot of
  initial resistance") — der Bereich darüber wird dadurch zum
  [[Low Resistance Liquidity Run|High Resistance Liquidity Run]]-Abschnitt. Beides gilt
  gleichzeitig: starker Draw hin zum Level, zäher Handel darüber.

## 3:30 als Sweetspot

Um **3:30 Uhr** kommt ein **erneuter Run**, der oft ein Retracement ist — laut Quelle der Sweetspot
der London Session, besonders **in Kombination mit dem [[Silver Bullet Model|Silver Bullet]]**.

Der London-Ablauf im Überblick:

| Zeit | Was |
|---|---|
| 0:00–0:30 | Opening Range mit First Displacement (nicht zwingend das erste FVG) |
| 3:00 | Silver Bullet, "Heart of London" |
| 3:30 | Retracement / erneuter Run — Sweetspot |
| 5:00 | London Session ist fertig |

![[ICT 2025 - London ORG 08.png]]
*Der London-Ablauf: Opening Range → Silver Bullet 3 Uhr → 3:30 Retracement → 5 Uhr Ende.*

## Zur Namensfrage „London Opening Range"

Diese Quelle nennt dieselbe Range **0:00–0:30** einmal „Midnight Opening Range" und einmal
„London Opening Range" — offenbar deshalb, weil in ihr das High/Low der London Session festgelegt
wird.

> ⚠️ Damit stehen sich zwei Zeitfenster gegenüber, die beide „London Opening Range" heißen:
> **0:00–0:30** (hier und in [[Kurz Notizen (Source)]]) gegen **1:30–2:00**
> (in [[Opening Range Theory - 1st Presented FVG Logic (Source)]], dort durch Chartmarker gestützt).
> Da nun **zwei unabhängige Quellen** die 0:00–0:30 nennen und diese Quelle auch **erklärt**, warum
> sie „London" heißt, spricht viel dafür, dass es **zwei verschiedene Ranges** sind und nicht ein
> Fehler — nicht dieselbe Sache mit widersprüchlicher Uhrzeit. Endgültig geklärt ist es nicht.

## Verwandt

- [[ORG (Opening Range Gap) & 1st Presented FVG]] — das andere Opening-Range-Konzept (9:30) und das 1. presented Displacement
- [[Silver Bullet Model]], [[ICT Daily Range Session Timing]]
- [[PD Array]], [[Fair Value Gap (FVG)]]
- [[New Week Opening Gap (NWOG) Bias]]
- [[Smart Money Concepts (SMC)]]
