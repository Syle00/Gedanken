---
tags: [concept, ict, trading-ict, core]
created: 2026-08-01
updated: 2026-08-10
sources: ["[[Low Resistance Liquidity Runs Part 1 (Source)]]", "[[Low Resistance Liquidity Runs Part 2 (Source)]]", "[[Post US Holiday Monday Followup (Source)]]", "[[2026-07-31 - ICT Algorithmic Time & Price Grids (Source)|ICT Algorithmic Time & Price Grids (Source)]]", "[[ICT Mentorship Core Content - Month 1 - Liquidity Runs (Source)]]", "[[2026-08-10 - Navigating High Resistance Liquidity Run Conditions (Source)|Navigating High Resistance Liquidity Run Conditions (Source)]]"]
---

# Low Resistance Liquidity Run

Zielbild jeder Range-Analyse: ein Preislauf mit möglichst wenig Widerstand von einer [[PD Array]] zur
nächsten. Zentrales Suchziel in [[Classic Swing Trading Approach]].

## Verschachtelte EQ-Messung

- Consolidierende Range zuerst grob per PD-Matrix einordnen (High to Low, EQ bestimmen).
- Innerhalb der Premium-Hälfte erneut EQ messen → "Premium innerhalb des Premium" (analog für
  Discount) — die Range wird rekursiv in Quadranten aufgeteilt, bis hinunter zu 4H/1H.
- Alle PD Arrays von Monthly bis Daily innerhalb der Range identifizieren, um die Consolidierung zu
  deuten und Targets/Profit-Targets abzuleiten.

![[image 190.png]]
*Rekursive EQ-Messung: Premium innerhalb des Premium (analog Discount innerhalb des Discount).*

## Kernregeln

- Eine bereits genutzte PD Array ist **nicht mehr gültig** — Preis läuft zur nächsten.
- Die Range muss korrekt aufgeteilt sein, sonst droht Liquidation der eigenen Position.
- Befindet sich Preis genau am EQ der Gesamtrange und ist der Open Float nicht klar erkennbar: lieber
  abwarten, statt zu raten — die Wahrscheinlichkeit, ausgestoppt zu werden, ist in dieser Lage hoch.

## Umsetzung für 50-75 Pip Runs (Part 2)

- Praktische Anwendung im **4H-Chart** in Kombination mit Monthly/Weekly/Daily PD Arrays — für
  [[One Shot One Kill Model|One-Shot-One-Kill]]-Setups gut geeignet, um 50–75 Pips zu erreichen.

![[image 199.png]]
*One-Shot-One-Kill im 4H-Chart: 50–75-Pip-Run bei High-Probability-Setup aus klarem Discount mit starkem bullishem Bias.*
- Auf High-Probability-Trades beschränken: klarer Discount-Bereich + starker bullisher Bias
  (spiegelbildlich für Shorts).
- Weekly Range wird immer antizipiert; verpasste M/W/D-PDs erlauben einen Reentry — bevorzugt an der
  jeweils höheren PD.
- **30–50 % Wahrscheinlichkeit**, dass sich das Wochen-High/Low unter Trending Conditions bereits am
  **Mittwoch** bildet.

## Setup-Erkennung: leere Zone zwischen zwei Daily PD Arrays (2026-Ergänzung)

Liegen zwei Daily-[[Suspension Block|Suspension Blocks]] (oder andere Daily-PD-Arrays) **ohne
Überlappung** übereinander und eröffnet die Session **innerhalb der leeren Zone dazwischen**, ist ein
schneller, "sauberer" Lauf zum entfernteren Block wahrscheinlich — große Candles, hohe Geschwindigkeit,
kaum Gegenreaktion. Davon zu unterscheiden ist das **effiziente Buy-/Sell-Program** (siehe
[[Buy & Sell Program]]): eng getaktete, kleine Candles ohne Pullback, die genauso schwer zu shorten/
longen sind, aber optisch das Gegenteil zeigen (langsam statt schnell). Quelle:
[[2026-07-31 - ICT Algorithmic Time & Price Grids (Source)|ICT Algorithmic Time & Price Grids (Source)]].

## Gegenstück: High Resistance Liquidity Run

Chop-artige Seek-&-Destroy-Bedingungen statt eines glatten Runs — typisch **nach großen
US-Feiertags-Wochenenden** (z.B. 4. Juli auf Sa/So: Montag meist schwierige, schlechte Price
Action → am Montag lieber nicht traden, erst Dienstag wieder einsteigen) und **vor
Zinsentscheiden/FOMC-Meetings**.

### Mechanik (2022er Video-Ergänzung)

Aus [[ICT Mentorship Core Content - Month 1 - Liquidity Runs (Source)]] — die konkrete
Preis-Struktur-Erklärung, warum manche Highs/Lows "verteidigt" sind:

- **High Resistance**: liegen zwischen dem aktuellen Preis und dem anvisierten alten High/Low
  bereits **viele weitere Zwischenhochs/-tiefs**, muss Preis erst durch all diese Widerstände, bevor
  das eigentliche Ziel überhaupt erreichbar wird — solche Levels sind gut verteidigt und werden
  meist nur durch einen echten Katalysator gebrochen (NFP, FOMC, unerwartete Zinsentscheidung,
  Black-Swan-Ereignis), nicht durch normale Preisbewegung.
- **Low Resistance**: läuft Preis dagegen **einseitig glatt** (wenig Retracement) von einem
  gebrochenen Level weg, bleibt jeder neu gebildete Short-Term-Swing bis zum nächsten Extrem
  "unbelastet" von Zwischenständen — solche Runs sind die bevorzugten Trade-Bedingungen, weil jeder
  Rücklauf zum letzten Swing praktisch widerstandsfrei zum nächsten alten High/Low durchläuft.
- Je **mehr Preisaktion** (Candles, Konsolidierung) um ein Level herum stattgefunden hat, desto
  stärker ist es institutionell verteidigt — Faustregel für die Einschätzung ohne zusätzliche Tools.

### Navigieren statt Aussitzen (Live-Trade 2026-08-10)

Die bestehende Regel "kein FVG in 15M/5M → nicht handeln" (siehe
[[Algorithmic Price Delivery Continuum]], [[Balanced Price Range (BPR)]]) ist ein **Entry-Filter**.
[[2026-08-10 - Navigating High Resistance Liquidity Run Conditions (Source)|Navigating High Resistance Liquidity Run Conditions (Source)]]
ergänzt den Fall, dass man bereits in einem Lauf sitzt, der in eine widerstandsreiche Zone
hineinläuft — ICT handelt dort bewusst weiter, aber mit verändertem Management:

- **HRLR vorab erkennen**: mehrere ungetestete bzw. bereits invertierte Gaps übereinander zwischen
  Preis und Ziel, dazwischen der Midnight Opening Price, plus schwere News-Woche (im Beispiel
  CPI/PPI Mi+Do). Ansage vorab: *"see how I told you it can get a little messy in here?"* — die
  Unruhe wird antizipiert, nicht als Überraschung behandelt.
- **Ziele auf die nahen Pools staffeln**, nicht auf das Endziel setzen: erstes Partial knapp unter
  dem Midnight Opening Price ([[Midnight Opening Range]]), zweites am nächsten minoren
  Buyside-Pool. Danach gilt der Trade als bezahlt, unabhängig vom Ausgang des Rests.
- **Nicht "das Magazin leeren"**, solange das eigentliche Ziel (hier: relativ gleiche
  Overnight-Swing-Highs) noch weit entfernt ist — sonst fehlt Size für den Teil des Laufs, der die
  Widerstände tatsächlich durchbricht.
- Der Midnight Opening Price wirkt beim Anlaufen von unten selbst als **massiver Widerstand**
  ("offering a whole lot of initial resistance"), nicht nur als Magnet — genau das macht die Zone
  darüber zum HRLR-Abschnitt.
- Gegen sich laufende Bewegung: Teil-Stops statt Alles-oder-Nichts, siehe
  [[Partial Profit-Taking & R-Multiple-Skalierung]].

## Verwandt

- [[PD Array]], [[Equilibrium Vs. Discount]]
- [[Open Float & Liquidity Pools]]
- [[One Shot One Kill Model]]
- [[External vs. Internal Range Liquidity]] — dieselbe Unterscheidung, aus Range-Perspektive statt Preis-Struktur-Perspektive
