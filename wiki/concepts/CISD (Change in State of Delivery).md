---
tags: [concept, ict, trading-ict, mentorship-2020, orderflow]
created: 2026-08-01
updated: 2026-08-10
sources: ["[[Elements To Successful Swing Trading (Source)]]", "[[CISD Mini Serie - Lecture 1 (Source)]]", "[[CISD Mini Serie - Lecture 2 (Source)]]", "[[ICT 2022 - Episode 13 Market Structure for Precision (Source)]]", "[[ICT 2022 - Episode 18 Higher Timeframe 15m 1H is Key (Source)]]", "[[ICT Gems - How Price Behaves At Specific Times (Source)]]"]
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

## Wann ein CISD valide ist

Aus [[ICT 2022 - Episode 18 Higher Timeframe 15m 1H is Key (Source)]]:

> **Ein CISD ist valide, wenn eine Imbalance darin liegt.**

Ohne Imbalance zählt der Shift nicht. Das ist die schärfste Validierungsregel im Vault dazu und
ergänzt die strukturelle Sicht in [[Market Structure Shift (MSS)]].

![[ICT 2022 - Ep18 04.png]]
*Valider CISD — die Imbalance darin ist das entscheidende Merkmal.*

Der Blick auf die Candles davor ([[ICT 2022 - Episode 13 Market Structure for Precision (Source)|Episode 13]]):
Solange in einem Downside Run die **Down-Closed Candles nicht überschossen** werden — der Preis also
bei keiner Candle unter deren Closing Price schließt — ist der Trend intakt. Erst wenn Preis
schließlich **über die Down-Closed Candle** geht, liegt ein bullisher CISD vor.

## Candle-Ebene

Jede **Down-Close-Candle** wird zum Support für nachfolgende bullishe Candles (spiegelbildlich bei
bearishem CISD). Das ist dieselbe Mechanik eine Ebene tiefer und zugleich das erste Kriterium, an
dem ein [[Buy & Sell Program]] erkannt wird.

Wird laut [[Elements To Successful Swing Trading (Source)]] im Verbund mit
[[SMT (Smart Money Divergence)|SMT]], [[COT (Commitment of Traders) Data|COT]],
[[Seasonal Tendency]] und [[Intermarket Relationships|Intermarket-Analyse]] genutzt, um eine
Trade-These zu verfestigen ("Hallmark"-Kriterien).

## Welcher Opening Price genau? Die Rückwärts-Zählregel (2024)

Aus [[ICT Gems - How Price Behaves At Specific Times (Source)]] — die operative Antwort auf die
Frage, welchen Preis der Algorithmus bei mehreren aufeinanderfolgenden Kerzen ansteuert:

1. Bei einer Serie **aufeinanderfolgender Down-Close-Kerzen** (bullisher Fall) gilt die Serie als
   **ein** [[Order Block]].
2. Der relevante Preis ist der **Opening Price der obersten/ersten** dieser Kerzen — er ist die
   CISD. *"The algorithm sees these three candles and goes right to that opening price."*
3. **Rückwärts zählen**: Gibt es links davon noch eine Down-Close-Kerze? Und links davon? Sobald
   keine mehr folgt, ist die zuletzt gefundene die maßgebliche.
4. **Validiert** ist der Order Block, sobald Preis diesen Opening Price durchbricht.

### Den Preis nach rechts verlängern

Die Linie danach **nach rechts ausziehen** und beobachten, wie Preis mit ihr umgeht. Die Lesart
folgt der Body-vs-Wick-Regel ([[Institutional Order Flow (Body vs Wick)]]):

> *"The wicks are always allowed to do the damage, but look what the bodies are doing — the bodies
> tell you the narrative."*

Die relevante Zone ist der Bereich zwischen diesem **Open** und dem **Close der tiefsten
Down-Close-Kerze**. Bleiben die Bodies bei jedem Rücklauf in der **oberen Hälfte** dieser Zone und
durchstechen das Body-Low nicht, ist der Order Block intakt — auch wenn Wicks darunter greifen.

## Verwandt

- [[Algorithmic Order Flow]] — die Hierarchie, in der das CISD Stufe 5 ist
- [[Buy & Sell Program]] — was das CISD in Gang setzt
- [[Graded Price Swings]] — Modell, das das CISD als Programm-Schalter nutzt
- [[Modell 22]] — 2026er Weiterentwicklung mit IFVG-Trigger
- [[SMT (Smart Money Divergence)]], [[Order Block]], [[Institutional Order Flow (Body vs Wick)]]
- ✅ COT und Seasonal Tendency haben inzwischen eigene Seiten
  ([[COT (Commitment of Traders) Data]], [[Seasonal Tendency]]) — der frühere Lückenhinweis hier
  ist damit erledigt.
