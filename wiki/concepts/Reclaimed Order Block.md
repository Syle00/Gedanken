---
tags: [concept, ict, trading-ict]
created: 2026-08-01
updated: 2026-08-02
sources: ["[[Reclaimed ICT Orderblock (Source)]]"]
---

# Reclaimed Order Block

[[Order Block]]-Variante speziell im **MMXM-Modell** (Market Maker Buy/Sell Model, siehe
[[New Week Opening Gap (NWOG) Bias]]): wird genutzt, nachdem die Buy- oder Sell-Curve abgeschlossen
ist, v.a. wenn keine FVG, [[Breaker Block]] oder andere PD Arrays verfügbar sind.

ICT nennt das Konzept in der Monthly Mentorship (Dezember 2016) "Reinforcing Orderblock Theory":
im Uptrend wird ein alter Sell-Block auf der Buy Side der Curve zu einem reclaimed Long, im
Downtrend spiegelbildlich ein alter Buy-Block auf der Sell Side zu einem reclaimed Short.

![[ICT Mentorship Dez2016 - Reclaimed Block Market Maker Buy Model.png]]
*Bullish Reclaimed Block: Setup in Major-/Intermediate-Uptrends — ein Block, der zuvor Price
gekauft hat, bestätigt nach kurzem Bounce ein minor Displacement; in der Buy Side der Curve wird
er als "alter" Block zu einem reclaimed Long.*

![[ICT Mentorship Dez2016 - Reclaimed Block Market Maker Sell Model.png]]
*Bearish Reclaimed Block: spiegelbildlich in Major-/Intermediate-Downtrends — ein Block, der
zuvor Price verkauft hat, wird in der Sell Side der Curve zu einem reclaimed Short.*

## Mechanik

- In der Sellcurve eines MMBM-Modells hedgen große Player an jedem **Minor Higher High** — diese
  Blöcke können später als Bullish [[CISD (Change in State of Delivery)|CISD]] in der Buycurve
  "reclaimed" werden.
- Bedingung: auf einen OB **muss** ein **Displacement** folgen, um ihn überhaupt als OB zu
  identifizieren — und danach **muss** zusätzlich ein **Minor Retracement** folgen (nicht
  durchgehendes Displacement in eine Richtung).
- Wichtiger Fallstrick: Ein **Reclaimed Bullish OB ist selbst eine bearishe Candle** (oder mehrere)
  innerhalb eines bearishen Moves, die ein minor-bullishes Displacement zeigt — keine bullishe
  Candle! Spiegelbildlich für Reclaimed Bearish OB.
- Bestätigungsmuster: nach jedem starken Displacement folgt ein Minor Displacement zur Gegenseite —
  das bestätigt Hedging-Aktivität und den Aufbau der Zielposition (z.B. Long). Solange das
  eintrifft, ist das MMXM-Modell intakt.

## Chart-Beispiele (AUDUSD H4, ICT Monthly Mentorship Dez. 2016)

![[ICT Mentorship Dez2016 - Reclaimed Block Chart Example (Uptrend).png]]
*Uptrend-Beispiel: nach dem Retracement bestätigt der reclaimed Block als Long-Fortsetzung.*

![[ICT Mentorship Dez2016 - Reclaimed Block Chart Example (Downtrend).png]]
*Downtrend-Beispiel: reclaimed Block als Short-Fortsetzung nach kurzem Gegenbounce.*

## Verwandt

- [[Order Block]], [[CISD (Change in State of Delivery)]]
- [[New Week Opening Gap (NWOG) Bias]] (MMBM/MMSM)
