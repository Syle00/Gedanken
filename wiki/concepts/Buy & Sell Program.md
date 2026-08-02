---
tags: [concept, ict, trading-ict, mentorship-2020, orderflow, bias]
created: 2026-08-02
updated: 2026-08-02
sources: ["[[CISD Mini Serie - Lecture 1 (Source)]]"]
---

# Buy & Sell Program

Stufe 3 der [[Algorithmic Order Flow|Orderflow-Hierarchie]]: läuft der Algorithmus gerade ein
**Buy Program** oder ein **Sell Program**? Der Begriff taucht im Vault schon länger auf (etwa im
[[Weekly Range Trading Model]] als „Buy-Programm bei Durchbruch des Range-Highs"), hatte bislang
aber keine eigenen Erkennungskriterien.

## Die zwei Kriterien

Für ein **Buy Program** müssen **beide** erfüllt sein — zusätzlich zu den vorangehenden Stufen der
Hierarchie (Macro Interest Rate, [[Seasonal Tendency]]):

1. **Werden Up-Closing Candles von Down-Closed Candles unterstützt?** Und wenn eine Down-Closed
   Candle überschossen wird: repricet der Markt **gezielt in eine Imbalance**, um einen Entry
   anzubieten?
2. **Werden vorherige bearishe Order Blocks ignoriert** und der Markt bleibt aggressiv bullish —
   werden also zuvor gültige Candles einfach und aggressiv durchbrochen?

Spiegelbildlich für ein Sell Program.

Die Merkhilfe der Rohnotiz für die Blickrichtung:

> **Up-Closing Candle links aus der Vergangenheit — Down-Closed Candle im aktuellen Move nach oben.**

Kriterium 1 ist damit die konstruktive Seite (die Struktur trägt), Kriterium 2 die destruktive
(Gegenstruktur wird ignoriert). Erst zusammen ergeben sie das Programm.

![[CISD Mini Serie - EURUSD Daily Breaker Bullish Seasonal.png]]
*EURUSD Daily: Buyside-/Sellside-Liquidität, Breaker High und Low, dazu die als „Bullish Seasonal"
markierte Phase — das Umfeld, in dem das Buy Program läuft.*

## Bezug zum Order Block

Kriterium 1 ist der Grund, warum eine Down-Close-Candle in einem Buy Program als Support wirkt —
dieselbe Mechanik, die [[Order Block]] und [[CISD (Change in State of Delivery)]] beschreiben, hier
aber als **Programm-Erkennungsmerkmal** statt als Entry-Signal.

## Verwandt

- [[Algorithmic Order Flow]] — die Hierarchie, in der dieses Kriterium Stufe 3 ist
- [[CISD (Change in State of Delivery)]] — Stufe 5, gibt die Richtung des Programms vor
- [[Order Block]], [[Breaker Block]], [[Institutional Order Flow (Body vs Wick)]]
- [[Weekly Range Trading Model]] — nutzt „Buy-/Sell-Programm" auf Wochenebene
- [[Smart Money Concepts (SMC)]]
