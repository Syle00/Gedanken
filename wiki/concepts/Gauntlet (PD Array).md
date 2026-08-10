---
tags: [concept, ict, trading-ict, ict-gems, pd-array, entry, 2025]
created: 2026-08-10
updated: 2026-08-10
sources: ["[[ICT Gems - Turtle Soup Entries Using ICT Gauntlet (Source)]]"]
---

# Gauntlet (PD Array)

Eigenständige, von ICT benannte PD Array — im Vault bislang unbekannt. Der Gauntlet ist **ein ganz
bestimmtes FVG innerhalb des Preis-Beins eines [[Breaker Block|Breakers]]**, das als Entry für ein
[[Turtle Soup]]-Setup dient.

> Namensherkunft: *"laying down the gauntlet"* — man geht long in der Überzeugung, dass das
> gerade genommene Low **ausreichend Liquidität** abgeholt hat.

## Identifikation (bullisher Fall)

1. Ein Liquidity Pool wird genommen und es bildet sich ein **Breaker**: Low → High → Lauf, der
   dieses Low ausnimmt und in einen **größeren** Liquiditätspool hineinläuft.
2. Man betrachtet **nur das Bein des Breakers, das zur Liquidität läuft** — nicht den ganzen
   Breaker.
3. Innerhalb dieses Beins **vom Low aus rückwärts** gehen: Das **allererste SIBI**
   ([[BISI & SIBI (Buyside-Sellside Imbalance)|Sellside Imbalance / Buyside Inefficiency]]), auf
   das man trifft, **ist der Gauntlet**.
4. Die **[[Volume Imbalance (VII)|Volume Imbalance]] muss beim Einzeichnen mitgenommen werden** —
   ICT nennt das ausdrücklich als Bedingung, sonst stimmen die Grenzen nicht.

Spiegelbildlich beim bearishen Breaker: Dort ist es das erste BISI im Bein, das zur Liquidität
läuft.

> **Merkmal in einem Satz**: das **tiefste, erste** SIBI innerhalb des Liquiditäts-Beins eines
> bullishen Breakers.

## Entry

- Preis handelt **über** den Gauntlet und kommt anschließend **zurück hinein** → Entry.
- Jeder weitere Rücklauf, bei dem die **Bodies oberhalb bleiben**, ist eine Gelegenheit zum
  **Nachlegen** — oder zum Ersteinstieg, falls man den ersten verpasst hat.
- Der eigentliche Zielbereich ist das darüberliegende Breaker-Level, das sich als klassischer
  Breaker-Entry nutzen lässt.

## Verhältnis zu Silver Bullet und IOFED

ICT trennt im selben Beispiel sauber zwischen drei Dingen, die optisch nah beieinander liegen:

- Der **Gauntlet** ist das erste SIBI im Breaker-Bein.
- Das **SIBI, das zu einem [[IFVG (Inverse Fair Value Gap)|IFVG]] wird**, ist der
  [[Silver Bullet Model|Silver Bullet]] — *"forget the gauntlet for now, this is your silver
  bullet"*.
- Der Einstieg an dessen Oberkante ist der
  [[Institutional Order Flow Entry Drill (IOFED)|IOFED]].

Alle drei können im selben Preisabschnitt auftreten und sich gegenseitig bestätigen.

## Konfluenz-Stack aus dem Beispiel

ICT zählt für den gezeigten Trade auf, was gleichzeitig zusammenfiel — brauchbar als Checkliste:

- **Macro-Zeit 9:50–10:10** ([[ICT Macros & Leading Candles]])
- Rücklauf in ein **Daily Bullish FVG**
- **Market Structure Shift** ([[Market Structure Shift (MSS)]])
- **Silver Bullet** (SIBI → IFVG) plus **IOFED** als Einstieg
- der **Gauntlet**
- **Turtle Soup Low-to-Low**
- die **C.E. einer Wick** als zusätzliches Level

## Wick-Projektion als Zusatzwerkzeug

Aus derselben Quelle: Eine markante **Daily-Premium-Wick** wird in fünf Level zerlegt — **High,
oberer Quadrant, C.E., unterer Quadrant, Low** (= der Close der Kerze) — und diese Level werden
**nach rechts projiziert**. Sie wirken danach wie jede andere PD-Referenz.

## Ausführung auf dem 15-Sekunden-Chart

ICT ausdrücklich: *"every time I talk about executions, I'm looking at a 15-second chart, folks.
Just because you don't see it doesn't mean I'm not looking at it."* Auf dieser Ebene wird der
Einstieg in ein reclaimed Bullish FVG bei Relative Equal Lows gesucht; der **Stop** liegt unter dem
Low, etwa am **unteren Quadranten** der maßgeblichen Wick. Vgl.
[[Algorithmic Price Delivery Continuum]].

## Verwandt

- [[Breaker Block]], [[Turtle Soup]], [[BISI & SIBI (Buyside-Sellside Imbalance)]]
- [[Institutional Order Flow Entry Drill (IOFED)]], [[Silver Bullet Model]]
- [[Volume Imbalance (VII)]], [[IFVG (Inverse Fair Value Gap)]]
- [[PD Array]], [[ICT Macros & Leading Candles]]
- [[ICT Gems - Turtle Soup Entries Using ICT Gauntlet (Source)]]
