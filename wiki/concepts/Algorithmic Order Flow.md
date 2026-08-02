---
tags: [concept, ict, trading-ict, mentorship-2020, bias, hierarchie]
created: 2026-08-02
updated: 2026-08-02
sources: ["[[CISD Mini Serie - Lecture 1 (Source)]]"]
---

# Algorithmic Order Flow

ICTs **Bestätigungs-Hierarchie** für den Orderflow — fünf Stufen, von der makroökonomischen Lage
bis zur einzelnen Candle. Der Punkt der Seite ist die **Reihenfolge**: die unteren Stufen sind nur
belastbar, wenn die oberen mitspielen.

| # | Stufe | Was sie beantwortet |
|---|---|---|
| 1 | **Macro Interest Rate** | Die makroökonomische Grundrichtung |
| 2 | **[[Seasonal Tendency]]** | Hat Preis es in diesem Zeitabschnitt leichter, Highs oder Lows zu bilden? |
| 3 | **[[Buy & Sell Program]]** | Läuft gerade ein Buy- oder ein Sell-Programm? |
| 4 | **Short Term Bias** | Die kurzfristige Richtung innerhalb des Programms |
| 5 | **State of Delivery** → [[CISD (Change in State of Delivery)]] | Wohin liefert der Algorithmus als nächstes? |

![[CISD Mini Serie - Algorithmic Order Flow Hierarchie.png]]
*Die Originalfolie „Algorithmic Order Flow — Changes In The State Of Delivery" mit den fünf Stufen,
am Beispiel EURUSD Daily mit Bullish Seasonal.*

## Warum eine Hierarchie

Im Forex-Bereich und gerade in höheren Timeframes braucht es **mehr Bestätigung als den Orderflow
allein**. Die Stufen liefern diese Bestätigung von oben nach unten.

> **Nicht nur HTF.** Die Quelle betont ausdrücklich, dass ICT dieselben Konzepte **bis in den
> 1-Minuten-Chart** anwendet — die Hierarchie ist **universal anwendbar**, nicht an eine bestimmte
> Zeitebene gebunden.

Das ist der Unterschied zu einer bloßen Checkliste: es geht nicht darum, möglichst viele Häkchen zu
sammeln, sondern darum, dass die untere Stufe nur zählt, wenn die darüberliegende sie trägt.

## Verwandt

- [[CISD (Change in State of Delivery)]] — Stufe 5, der eigentliche Trigger
- [[Buy & Sell Program]] — Stufe 3, mit den zwei Erkennungskriterien
- [[Seasonal Tendency]] — Stufe 2
- [[Institutional Order Flow (Body vs Wick)]], [[Intermarket Relationships]]
- [[COT (Commitment of Traders) Data]] — dieselbe Rolle als übergeordneter Bestätigungsfilter
- [[Smart Money Concepts (SMC)]]
