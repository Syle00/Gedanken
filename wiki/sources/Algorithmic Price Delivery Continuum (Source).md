---
tags: [source, ict, trading-ict, lecture-2025, fvg, routine]
created: 2026-08-02
updated: 2026-08-02
raw: "[[Algorithmic Price Delivery Continuum]]"
raw_path: "raw/trading-ict/ICT 2025 Lecture Series/Algorithmic Price Delivery Continuum.md"
curriculum: "[[ICT 2025 Lecture Series (Source)]]"
---

# Algorithmic Price Delivery Continuum (Source)

Week 2 der [[ICT 2025 Lecture Series (Source)]]. Beschreibt ICTs Lesemethode und liefert nebenbei den
**Mechanismus**, der bislang nur als Merksatz in [[Kurz Notizen (Source)]] stand.

## Kernpunkte

- **Price Delivery Continuum Theory**: bei jedem Candle-Close (4H → 1H → 15M → 5M → 1M) alle
  Timeframes durchgehen. In den unteren Timeframes wird wenig Zeit verbracht — relevant ist nur der
  Close, dazu PD Arrays und Liquidität.
- Leitfragen: Premium oder Discount? Werden PDs respektiert? Geht es zur Sell- oder Buyside, oder
  sucht Preis eine PD?
- **SIBI → obere Hälfte relevant, BISI → untere Hälfte.**
- **Balanced Price Range definiert**: wird in der oberen Hälfte eines SIBI **länger** hoch und runter
  getradet und der Preis dabei gehalten, macht das diese Hälfte zur BPR. Spiegelbildlich beim BISI.
- Daraus die **Antizipation, ob ein FVG offen bleibt**: eine Hälfte, durch die nur eine einzige
  starke Candle gelaufen ist, ist imbalanced und wird gefüllt — die Hälfte mit viel verbrachter Zeit
  bleibt offen. Bei HTF-FVGs deshalb immer prüfen, was am 50-%-Level passiert ist.
- **FVG-Bildungszeiten**: 10:00–10:15 / 10:15–10:30 / 10:30–10:45 / 10:45–11:00.
- **Kein FVG in 15M/5M = High Resistance Liquidity Run** → nicht handeln.

## Extrahierte Seiten

- [[Algorithmic Price Delivery Continuum]] (neu)
- [[Balanced Price Range (BPR)]] (aktualisiert: Mechanismus und Herkunft der Regel ergänzt)

## Bilder aus der Rohquelle

![[ICT 2025 - APDC 01.png]]
*Titelchart der Lecture.*

![[ICT 2025 - APDC 02.png]]
*15M-SIBI — im 1M-Chart wirkt es kurzzeitig bullish, der Bias bleibt bearish.*

![[ICT 2025 - APDC 03.png]]
*15M-SIBI mit Balanced Price Range über dem C.E.*

![[ICT 2025 - APDC 04.png]]
*Die genannten FVG-Bildungsfenster zwischen 10:00 und 11:00.*

![[ICT 2025 - APDC 05.png]]
*Untere Hälfte imbalanced, obere Hälfte mit viel verbrachter Zeit — Fill unten erwartet, oben offen.*

![[ICT 2025 - APDC 06.png]]
*Kein FVG in 15M/5M → sicher im High Resistance Liquidity Run.*

## Verwandt

- [[Algorithmic Price Delivery Continuum]], [[Balanced Price Range (BPR)]]
- [[Balanced Price Chart Bsp (Source)]] — die zugehörige Chartstrecke
- [[Fair Value Gap (FVG)]], [[BISI & SIBI (Buyside-Sellside Imbalance)]], [[Low Resistance Liquidity Run]]
- [[ICT 2025 Lecture Series (Source)]]
