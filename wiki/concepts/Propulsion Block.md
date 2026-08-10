---
tags: [concept, ict, trading-ict]
created: 2026-08-06
updated: 2026-08-10
sources: ["[[ICT Mentorship Core Content - Month 04 - ICT Propulsion Block (Source)]]", "[[ICT Gems - Non-Farm Payroll Profile + Macros (Source)]]"]
---

# Propulsion Block

[[Order Block]]-Variante: eine zweite, **höher liegende** (bullish) bzw. **tiefer liegende**
(bearish) Down-/Up-Close-Candle, die selbst wieder in den bereits validierten ursprünglichen Order
Block zurücktradet, bevor sie selbst als Order Block genutzt wird.

## Definition

- Ausgangspunkt ist ein bereits **validierter** Order Block (Displacement hat stattgefunden).
- Bildet sich danach eine **neue** Candle gleicher Polarität (down-close im bullishen Fall), die
  bis in den Bereich des ursprünglichen Order Blocks zurückläuft, wird diese neue Candle selbst
  zum **Propulsion Block**.
- Kennzeichen: der **Mean Threshold** (50-%-Punkt des Candle-Bodys) des Propulsion Blocks wird so
  gut wie **nie** verletzt — deutlich strikter als beim gewöhnlichen Order Block, der laut
  [[Order Block]] "idealerweise" nicht unter 50 % zurückläuft. Beim Propulsion Block ist das fast
  eine harte Regel.

## Entry & Risiko

- Entry: sobald Preis in den Propulsion Block zurückläuft (Open/High der Candle je nach Richtung).
- **Sehr enger Stop möglich**, da ein Bruch des Mean Threshold als klares Warnsignal gilt — wird er
  gebrochen, ist die Idee wahrscheinlich ungültig, sofortiger Ausstieg statt Aussitzen.
- Charakteristik: **sofortige, heftige Reaktion** direkt nach dem Touch — kein längeres Verweilen
  im Block. Macht den Propulsion Block besonders für sehr kurzfristige/Scalping-Entries geeignet.

## Die Halbe-Body-Grenze (2023-Ergänzung)

Aus [[ICT Gems - Non-Farm Payroll Profile + Macros (Source)]] — die Invalidierungsregel, die auf
dieser Seite bislang fehlte:

> **Preis darf nicht unter die Hälfte des Bodys der Propulsion-Kerze fallen.** *"You don't ever
> want to see price go down below half of this candle's body."*

Hält diese Grenze — auch knapp —, bleibt die Erwartung höherer Preise für den Folgetag bestehen.
Im Beispiel kam Preis sehr nah heran, ohne sie zu brechen, und genau das wertete ICT als Freigabe
für den bullishen Ansatz am nächsten Tag.

**Welche Preispunkte den Block aufspannen**: das **High** der letzten Down-Close-Kerze und deren
**Opening Price** — ausdrücklich **nicht** der Mean Threshold des Bodys und **nicht** der Mean
Threshold von High bis Low. Der Algorithmus behandelt die Spanne High↔Open wie ein Gap.

**Praktisch nutzbar wird der Block über seine C.E.**: Die Mitte zwischen Propulsion-Block-High
(Wick) und Opening Price ist der sensible Punkt — im Beispiel drehte der Markt exakt dort, und
dieselbe Stelle deckte sich mit der C.E. eines Hourly FVG. Vgl.
[[Institutional Order Flow (Body vs Wick)]].

> Merkhilfe von ICT für jede Wick: *"whenever I look at a tail or a wick, my eye goes immediately
> to the midpoint — that's consequent encroachment."*

## Verwandt

- [[Order Block]] — Basiskonzept
- [[Breaker Block]], [[Rejection Block]], [[Reclaimed Order Block]], [[Mitigation Block]] — weitere
  Order-Block-Varianten aus derselben Lecture-Reihe ([[Month 04 (Source)]])
