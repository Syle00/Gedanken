---
tags: [concept, ict, trading-ict, core]
created: 2026-08-01
updated: 2026-08-05
sources: ["[[Low Resistance Liquidity Runs Part 1 (Source)]]", "[[Low Resistance Liquidity Runs Part 2 (Source)]]", "[[Post US Holiday Monday Followup (Source)]]", "[[ICT Algorithmic Time & Price Grids (Source)]]"]
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
[[ICT Algorithmic Time & Price Grids (Source)]].

## Gegenstück: High Resistance Liquidity Run

Chop-artige Seek-&-Destroy-Bedingungen statt eines glatten Runs — typisch **nach großen
US-Feiertags-Wochenenden** (z.B. 4. Juli auf Sa/So: Montag meist schwierige, schlechte Price
Action → am Montag lieber nicht traden, erst Dienstag wieder einsteigen) und **vor
Zinsentscheiden/FOMC-Meetings**.

## Verwandt

- [[PD Array]], [[Equilibrium Vs. Discount]]
- [[Open Float & Liquidity Pools]]
- [[One Shot One Kill Model]]
