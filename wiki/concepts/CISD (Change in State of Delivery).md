---
tags: [concept, ict, trading-ict, mentorship-2020, orderflow]
created: 2026-08-01
updated: 2026-08-02
sources: ["[[Elements To Successful Swing Trading (Source)]]", "[[CISD Mini Serie - Lecture 1 (Source)]]", "[[CISD Mini Serie - Lecture 2 (Source)]]"]
---

# CISD (Change in State of Delivery)

Der **State of Delivery** ist die Frage, wohin der Algorithmus gerade liefert — zur Buyside oder zur
Sellside. Das **CISD** ist der Moment, in dem diese Lieferrichtung **wechselt**.

Es ist Stufe 5 und damit die unterste, konkreteste Ebene der
[[Algorithmic Order Flow|Orderflow-Hierarchie]].

## Definition

> Der State of Delivery ist der **erste Run auf eine Liquidität, der die Richtung vergibt** — aus
> einer Konsolidierung heraus auf die erste Buyside (bzw. Sellside). Es ist also das CISD, das die
> **Richtung des Programms** vorgibt.

![[CISD Mini Serie - State Of Delivery Buyside.png]]
*EURUSD 4H: aus der Konsolidierung heraus „State Of Delivery Is On Buyside" — daraus ergibt sich das
Buy Program und der bullishe Short Term Bias.*

## Der Test des Bias

Nach Erreichen der Buyside **wechselt der State of Delivery zur Sellside**, um Sellside-Liquidität
zu ziehen. Genau hier entscheidet sich, ob der Bias stimmt:

- **Bias richtig** → es wird Liquidität gezogen **oder** eine Imbalance rebalanced, und der Markt
  arbeitet danach **weiter im Buy Program**.
- Bleibt das aus, war der Bias falsch.

![[CISD Mini Serie - State Of Delivery Sellside.png]]
*Derselbe Chart: „State Of Delivery Is On Sellside" (rot) — der Gegenzug, an dem sich der Bias
bewährt. Danach läuft das Buy Program weiter.*

Das ist der praktisch wichtigste Punkt der Seite: **ein Gegenzug widerlegt den Bias nicht** — er
gehört zum Programm dazu, solange er Liquidität holt oder eine Imbalance ausgleicht.

## Der Trigger: Close über dem Swing Point

Konkret geschaltet wird von Bullish zu Bearish (und umgekehrt), indem Preis **über dem Swing High
closed** — spiegelbildlich unter dem Swing Low. Siehe [[Graded Price Swings]], wo das CISD als
Schalter zwischen Buy- und Sell-Programm dient.

## Candle-Ebene

Jede **Down-Close-Candle** wird zum Support für nachfolgende bullishe Candles (spiegelbildlich bei
bearishem CISD). Das ist dieselbe Mechanik eine Ebene tiefer und zugleich das erste Kriterium, an
dem ein [[Buy & Sell Program]] erkannt wird.

Wird laut [[Elements To Successful Swing Trading (Source)]] im Verbund mit
[[SMT (Smart Money Divergence)|SMT]], [[COT (Commitment of Traders) Data|COT]],
[[Seasonal Tendency]] und [[Intermarket Relationships|Intermarket-Analyse]] genutzt, um eine
Trade-These zu verfestigen ("Hallmark"-Kriterien).

## Verwandt

- [[Algorithmic Order Flow]] — die Hierarchie, in der das CISD Stufe 5 ist
- [[Buy & Sell Program]] — was das CISD in Gang setzt
- [[Graded Price Swings]] — Modell, das das CISD als Programm-Schalter nutzt
- [[Modell 22]] — 2026er Weiterentwicklung mit IFVG-Trigger
- [[SMT (Smart Money Divergence)]], [[Order Block]], [[Institutional Order Flow (Body vs Wick)]]
- ✅ COT und Seasonal Tendency haben inzwischen eigene Seiten
  ([[COT (Commitment of Traders) Data]], [[Seasonal Tendency]]) — der frühere Lückenhinweis hier
  ist damit erledigt.
