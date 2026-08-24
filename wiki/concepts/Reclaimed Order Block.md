---
tags: [concept, ict, trading-ict]
created: 2026-08-01
updated: 2026-08-23
sources: ["[[Reclaimed ICT Orderblock (Source)]]", "[[ICT Mentorship Core Content - Month 04 - Reclaimed ICT Orderblock (Source)]]"]
---

# Reclaimed Order Block

[[Order Block]]-Variante speziell im **[[MMXM (Market Maker Buy & Sell Model)|MMXM]]**
(Market Maker Buy/Sell Model): wird genutzt, nachdem die Buy- oder Sell-Curve abgeschlossen ist, v.a. wenn keine FVG, [[Breaker Block]] oder andere PD Arrays verfügbar sind.

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

## Curve-Matching-Logik (2022er Video-Ergänzung)

Aus [[ICT Mentorship Core Content - Month 04 - Reclaimed ICT Orderblock (Source)]] — dieselbe
Mechanik nochmals hergeleitet, mit dem konkreten Bild eines Market-Maker-Buy-Modells:

- Die **Sell-Seite der Kurve** (Preis fällt zum HTF-Support) enthält bereits mehrere kleine
  Zwischenerholungen — jede davon ist ein normaler Bullish Order Block, entstanden durch frühes,
  gestaffeltes Hedging (Smart Money kann Positionen wegen ihrer Größe nicht in einer Transaktion
  aufbauen).
- Sobald die **Buy-Seite der Kurve** beginnt (Preis dreht am HTF-Support nach oben), wird für **jede
  neue Kaufgelegenheit** der jeweils passende Down-Candle-Level von der Sell-Seite als Reclaimed
  Block herangezogen — die Blöcke "matchen" sich 1:1 zwischen beiden Kurvenhälften.
- Spiegelbildlich für ein Market-Maker-Sell-Modell mit Up-Candles auf der Buy-Seite, die auf der
  Sell-Seite als Reclaimed Shorts genutzt werden.
- Praktische Konsequenz: wer die Sell-Seite der Kurve im Nachhinein durchgeht und **jeden**
  Down-Candle mit kurzer Gegenreaktion markiert, hat damit bereits die komplette Liste künftiger
  Reclaimed-Long-Level für die Buy-Seite vorbereitet.

## Verwandt

- [[Order Block]], [[CISD (Change in State of Delivery)]]
- [[New Week Opening Gap (NWOG) Bias]] (MMBM/MMSM)
- [[Propulsion Block]] — verwandte, aber unterschiedliche zweite Rücklauf-Bewegung in denselben Order Block
