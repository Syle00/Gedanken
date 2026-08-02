---
tags: [concept, ict, trading-ict, mentorship-2025, ath, bias]
created: 2026-08-02
updated: 2026-08-02
sources: ["[[Trading All Time Market Highs (Source)]]", "[[Advanced ICT Liquidity Concepts (Source)]]"]
---

# Trading All Time Highs (ATH)

Wie mit einem Markt umzugehen ist, der neue Allzeithochs druckt. Die Quellen behandeln zwei
gegensätzliche Phasen, die zusammengehören: **erst mitlaufen** (Lektion 01), **dann erkennen, wann
Smart Money oben verkauft** (Lektion 05).

> Beide Logiken gelten laut Lektion 05 **nicht nur für ATH/ATL**, sondern genauso für alte Market
> Highs/Lows sowie Longterm- und Intermediate-Term-Highs/-Lows (LTH/LTL, ITH/ITL).

## Phase 1 — Continuation: ATH zieht weitere ATH nach sich

Grundannahme: Ist ein ATH geschaffen, ist es wahrscheinlich, dass Preis weiter presst und weitere
ATH bildet. Analysiert wird auf dem **Daily Timeframe**.

**Wir vermeiden es, Reversals zu antizipieren — wir bleiben einfach bullish.**

### Key Reference Points in Algorithmic Price Delivery

Die Checkliste der Quelle, in ihrer Reihenfolge:

1. Tradet Preis **unter dem Closing Price einer Down-Closed Candle**? Wenn ja, sind das
   [[Rejection Block|Rejection Blocks]], die Preis weiter nach oben anbieten.
2. Nach **[[BISI & SIBI (Buyside-Sellside Imbalance)|BISI-FVG]]** schauen, die ein Reentry für
   Institutionelle bilden und Preis promoten.
3. Alle **Premium Candle Wicks und ihr C.E** markieren — sie stellen die Discount-PD-Arrays dar.
4. Premium Candle Wicks **ausmalen** (in die Zukunft projizieren).
5. Prüfen, ob Preis **unter dem Close einer Up-Closed Candle** tradet. Bei ATH overshootet Preis
   oft die gesamte Candle, um eine **Bear Trap** zu bilden.
6. **Immediate Rebalance** ist oft sehr stark und bietet dem Preis Discount an.
7. Reversal nicht antizipieren — bullish bleiben.

Merksatz der Quelle: **Premium Candle Wick = bearishe Candle.**

![[MentorShip 2025 - 01 ATH Key Reference Points.png]]
*Die Key Reference Points im Daily Chart bei laufender ATH-Serie.*

## Phase 2 — Distribution: die 3 Stages of Accumulation (heavy Shorts)

Der Kipppunkt ist der **Candle Body Close über dem ATH** — nicht der Wick-Durchbruch:

> Equal Highs/Lows sollen **nicht nur mit einer Wick** durchbrochen werden, sondern mit einem
> **Candle Body Close**.

Nachdem über dem ATH geclosed wurde, nutzt Smart Money **jede PD Array oberhalb des Closing Price,
um heavy Short zu gehen** — genau das Verhalten großer Commercial Hedger.

**Das Muster besteht aus 3 Stages:** Dreimal wird über dem jeweiligen High mit einem höheren Preis
geclosed, und jedes Mal werden an Premium-PDs neue Shorts aufgebaut.

Woran man es erkennt: Man schaut auf die **Wicks**. Ja, es geht weiter höher — aber der **Closing
Price liegt ein gutes Stück tiefer**, teils sogar als bearishe Candle. Das heißt: **Distribution von
Longs und Akkumulation von Shorts.**

![[MentorShip 2025 - 05 Three Stages Heavy Shorts.png]]
*3 Stages: dreimal ein höherer Close über dem High, jedes Mal neue Shorts an Premium-PDs.*

![[MentorShip 2025 - 05 Three Closing Prices Above Highs 1.png]]
*Die 3 Closing Prices, die jeweils über dem zugehörigen High liegen.*

![[MentorShip 2025 - 05 Three Closing Prices Above Highs 2.png]]
*Derselbe Ablauf im Detail.*

> Zur Einordnung des Oktober-Drops merkt die Quelle an: der Tarif-News-Driver war für Smart Money
> nur die Ausrede, damit der Move nicht aufhört — der Aufbau war über die 3 Stages vorher sichtbar.

## Die Orderflow-Regel dahinter

Verallgemeinert und laut Quelle **in jeder Situation gültig**:

> Schafft Preis es **nicht**, über dem **C.E einer PD Array** (z.B. einer Premium Wick) zu closen,
> sind wir short — und spiegelbildlich umgekehrt. Der Orderflow sagt es einem direkt.

Das ist dieselbe C.E-Logik wie in [[ORG (Opening Range Gap) & 1st Presented FVG]], hier auf die
Bestimmung der Richtung nach den 3 Stages angewandt.

![[MentorShip 2025 - 05 No Close Above Premium Wick CE 1.png]]
*Preis schafft keinen Close über dem C.E der Premium Wick — Orderflow ist bearish.*

![[MentorShip 2025 - 05 No Close Above Premium Wick CE 2.png]]
*Fortsetzung nach den 3 Stages.*

## Verwandt

- [[ORG (Opening Range Gap) & 1st Presented FVG]] — warum ein ORG am ATH-Tag besonders relevant ist
- [[Rejection Block]], [[BISI & SIBI (Buyside-Sellside Imbalance)]], [[PD Array]]
- [[Central Bank Dealers Range (CBDR)]] (C.E), [[Institutional Order Flow (Body vs Wick)]]
- [[COT (Commitment of Traders) Data]] — die Commercial-Hedger-Seite des 3-Stages-Musters
- [[Market Reversal Types]], [[Smart Money Concepts (SMC)]]
