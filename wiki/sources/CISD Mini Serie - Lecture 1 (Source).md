---
tags: [source, ict, trading-ict, mentorship-2020, cisd, orderflow]
created: 2026-08-02
updated: 2026-08-02
raw: "[[CISD Mini Serie - Lecture 1]]"
raw_path: "raw/trading-ict/CISD Mini Serie/CISD Mini Serie - Lecture 1.md"
curriculum: "[[CISD Mini Serie (Source)]]"
---

# CISD Mini Serie - Lecture 1 (Source)

Die Grundlagen-Lecture: **Orderflow-Hierarchie**, **Buy-/Sell-Program-Erkennung** und der
**State of Delivery**.

## Kernpunkte

- **Fünfstufige Hierarchie**: (1) Macro Interest Rate → (2) Seasonal Tendency → (3) Buy/Sell
  Programs → (4) Short Term Bias → (5) State of Delivery.
- Im Forex-Bereich und in höheren Timeframes braucht es **mehr Bestätigung als den Orderflow
  allein**. Ausdrücklich betont: ICT nutzt dieselben Konzepte **bis in den 1M-Chart** — die
  Hierarchie ist **universal anwendbar**.
- **Seasonal Tendency praktisch gelesen**: wenn Preis es schwer hat, neue Lows zu bilden, heißt das
  nicht „durchgehend extrem bullish", sondern dass er es in diesem Zeitabschnitt **leichter hat,
  Highs als Lows zu bilden**. Zusammen mit tatsächlich bullisher Price Action ein gutes Anzeichen.
- **Buy Program erkennen — beide Kriterien müssen erfüllt sein** (zusätzlich zu den vorangehenden
  Stufen):
  1. Werden **Up-Closing Candles von Down-Closed Candles unterstützt**? Und wird bei einem Überschuss
     über eine Down-Closed Candle **gezielt in eine Imbalance repriced**, um einen Entry anzubieten?
  2. Werden **vorherige bearishe Order Blocks ignoriert** und der Markt bleibt aggressiv bullish?
  Merkhilfe: *„Up-Closing Candle links aus der Vergangenheit & Down-Closed Candle im aktuellen Move
  nach oben."*
- **State of Delivery**: der **erste Run auf eine Liquidität, der die Richtung vergibt** — aus einer
  Konsolidierung heraus auf die erste Buyside. Das CISD gibt damit die **Richtung des Programms** vor.
- **Der Test**: nach Erreichen der Buyside wechselt der State of Delivery zur Sellside, um
  Sellside-Liquidität zu ziehen. Stimmt der Bias, wird Liquidität gezogen **oder** eine Imbalance
  rebalanced — und das Buy Program läuft weiter.

## Extrahierte Seiten

- [[Algorithmic Order Flow]] (neu), [[Buy & Sell Program]] (neu)
- [[CISD (Change in State of Delivery)]] (erweitert)

## Bilder aus der Rohquelle

![[CISD Mini Serie - Algorithmic Order Flow Hierarchie.png]]
*Die Originalfolie mit den fünf Stufen, EURUSD Daily mit markierter Bullish-Seasonal-Phase.*

![[CISD Mini Serie - Seasonal Tendency Overlay.png]]
*Seasonal-Tendency-Overlay mehrerer Jahre — die Grundlage für Stufe 2.*

![[CISD Mini Serie - EURUSD Daily Breaker Bullish Seasonal.png]]
*EURUSD Daily: Buyside-/Sellside-Liquidität, Breaker High und Low, Bullish Seasonal ab Mai 2020.*

![[CISD Mini Serie - State Of Delivery Buyside.png]]
*„State Of Delivery Is On Buyside" — aus der Konsolidierung heraus, daraus Buy Program und bullisher
Short Term Bias.*

![[CISD Mini Serie - State Of Delivery Sellside.png]]
*„State Of Delivery Is On Sellside" — der Gegenzug, an dem sich der Bias bewährt.*

## Verwandt

- [[Algorithmic Order Flow]], [[Buy & Sell Program]], [[CISD (Change in State of Delivery)]]
- [[Seasonal Tendency]], [[Order Block]], [[Breaker Block]]
- [[CISD Mini Serie - Lecture 2 (Source)]], [[CISD Mini Serie (Source)]]
