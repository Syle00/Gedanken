---
tags: [concept, ict, trading-ict, mentorship-2020, orderflow, bias]
created: 2026-08-02
updated: 2026-08-06
sources: ["[[CISD Mini Serie - Lecture 1 (Source)]]", "[[2026-07-31 - ICT Algorithmic Time & Price Grids (Source)|ICT Algorithmic Time & Price Grids (Source)]]", "[[Quarterly Shifts & IPDA Data Ranges (Source)]]"]
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

## Visuelle Signatur (2026-Ergänzung)

Ein laufendes Buy Program zeigt sich optisch als **eng getaktete Folge kleiner, gleichförmiger
Candles ohne nennenswerten Pullback** — im Gegensatz zum [[Low Resistance Liquidity Run]], der über
große, schnelle Candles läuft. Beide Signaturen sind gleichermaßen schwer gegen den Trend zu
handeln, sehen aber unterschiedlich aus (langsam-stetig vs. schnell-explosiv). Quelle:
[[2026-07-31 - ICT Algorithmic Time & Price Grids (Source)|ICT Algorithmic Time & Price Grids (Source)]].

## SMT-basierte Erkennung via Underlying/Benchmark (2017 Mentorship)

Eine ältere, eigenständige Methode aus dem Begleitvideo zu
[[Quarterly Shifts & IPDA Data Ranges (Source)]] (2017er Mentorship), um auf dem **Daily-Chart**
zu erkennen, ob der Algorithmus gerade akkumuliert oder distribuiert — komplementär zu den
Candle-Kriterien oben, funktional verwandt mit [[SMT (Smart Money Divergence)]]. **Underlying** =
das gehandelte Asset, **Benchmark** = ein korreliertes Vergleichsasset (z.B. USDX für
Forex-Paare).

Grundprinzip: verglichen wird, ob Underlying und Benchmark bei einem neuen Extrem (Higher
High/Lower Low) **gemeinsam mitziehen** oder ob eines der beiden es **verweigert** — die
Verweigerung ist das Signal. Ein Buy Program (Akkumulation) zeigt sich z.B. daran, dass der
Benchmark ein neues Lower Low macht, während das Underlying sich weigert (Higher Low statt Lower
Low) — relative Stärke im Underlying. Bei invers korrelierten Benchmarks (z.B. USDX zu EURUSD)
kippt die Lesart entsprechend um.

Konkretes Beispiel aus dem Video: GBPUSD macht ein Lower Low (sammelt Sellside-Liquidity unter
einem alten Tief ein), während USDX zeitgleich ein Lower High macht (keine neue Dollar-Stärke) →
Erwartung eines Turtle-Soup-Long im GBPUSD. Spiegelbildlich für ein Sell Program: macht das
Underlying ein neues Higher High, während der Benchmark sich weigert, ein entsprechendes Extrem zu
bilden, deutet das auf einen bevorstehenden Turtle-Soup-Sell hin (Liquidity Grab statt echter
Fortsetzung). Es gibt insgesamt vier gespiegelte Bedingungspaare pro Richtung (positiv wie invers
korrelierte Benchmarks) — das Kernmuster ist immer dieselbe Divergenz-Logik: **eine Seite bestätigt
das neue Extrem, die andere verweigert es**.

Diese Methode ist ausdrücklich an [[Quarterly Shift]] gekoppelt: die 60/40/20-Handelstage-Fenster
(siehe [[IPDA Data Ranges]]) dienen dabei sowohl als Lookback für die institutionelle Orderflow-
Richtung als auch als Cast-Forward-Fenster für den Zeitpunkt des nächsten Shifts.

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
- [[SMT (Smart Money Divergence)]] — verwandte Divergenz-Logik zwischen korrelierten Assets
- [[Quarterly Shift]], [[IPDA Data Ranges]]
