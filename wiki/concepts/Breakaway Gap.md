---
tags: [concept, ict, trading-ict]
created: 2026-08-02
updated: 2026-08-06
sources: ["[[Kurz Notizen (Source)]]", "[[Advanced ICT Liquidity Concepts (Source)]]", "[[CISD Mini Serie - Lecture 2 (Source)]]", "[[ICT Mentorship Core Content - Month 04 - ICT Vacuum Block (Source)]]"]
---

# Breakaway Gap

Entsteht, wenn ein sehr großes Displacement genau an einem **Quadranten eines
[[Fair Value Gap (FVG)|FVG]]** oder einer **Wick** auftritt — im Lower Timeframe wird das
ursprüngliche FVG dadurch häufig zu einem Breakaway Gap.

![[Kurz Notizen - Breakaway Gap Example.png]]
*Großes Displacement an einem FVG-/Wick-Quadranten — im Lower Timeframe entsteht daraus oft ein Breakaway Gap.*

## Welches Gap zählt, wenn mehrere vorliegen?

- Liegen **zwei Displacements durch einen Quadranten** vor, gilt das **zuerst entstandene** Gap als
  das relevante — auch wenn das spätere (z.B. ein darüberliegendes BISI) formal dieselbe Bedingung
  erfüllt.
- Kontrollblick auf die Wick des zweiten Displacements: geht sie nur minimal übers **C.E** und
  **nicht mal bis 0,75**, ist das eindeutig heavy bearish (spiegelbildlich bullish).

![[MentorShip 2025 - 05 Two Displacements Daily Imbalance.png]]
*Zwei Displacements auf Quadranten der Daily Imbalance — das erste Gap ist das Breakaway Gap.*

![[MentorShip 2025 - 05 Bullish EU Mirrored IPDA 60 Days.png]]
*Gespiegelt bullish am EU: das zuerst entstandene Gap bleibt relevant, das darüberliegende BISI tritt zurück.*

## Entstehung am 50-%-Level

Ein zweiter, unabhängiger Entstehungsweg aus [[CISD Mini Serie - Lecture 2 (Source)]]: kommt Preis in
einem Buy Program am **50 % der antizipierten Range** an und liegt dort eine **Imbalance kurz unter
50 %**, wird diese **meistens zum Breakaway Gap**.

- Ist **keine Imbalance** vorhanden, wird stattdessen das **nächstliegende Short Term Low** genommen.
- **Oberhalb des 50-%-Levels** gilt dasselbe; spiegelbildlich im Sell Program.

Damit gibt es zwei Wege zum Breakaway Gap: über ein **Displacement am Quadranten** (oben) und über
die **Lage relativ zum 50-%-Level** einer gegradeten Range ([[Graded Price Swings]]). Beide laufen
auf dieselbe Quadranten-Logik hinaus.

## Vacuum Block = Breakaway Gap durch ein Volatilitäts-Event

ICT ausdrücklich: **"a vacuum block is nothing more than a breakaway gap."** Ein Vacuum Block
entsteht, wenn ein Volatilitäts-Event (NFP, FOMC, Session-Open, unvorhergesehene News) einen
Kurs-Gap auslöst, in dem **buchstäblich kein einziger Trade** zwischen dem Close der letzten Candle
und dem Open der nächsten stattfand — daher "Vakuum" der Liquidität. Quelle:
[[ICT Mentorship Core Content - Month 04 - ICT Vacuum Block (Source)]].

- **Wie eine synthetische Candle behandeln**: Open = Close der Candle davor, "Close" = Open der
  Candle danach, High/Low = die beiden Gap-Extreme. Auf diese synthetische Range dieselbe
  PD-Array-Logik anwenden wie auf jede andere Candle.
- **Teilfüllung möglich**: Liegt innerhalb des Gaps bereits ein gültiger [[Order Block]] (z.B. die
  höhere zweier Down-Candles direkt vor einem Gap-Up), kann Preis nur bis dorthin zurücklaufen und
  umkehren — der obere Teil des Gaps bleibt als eigenständiges [[Fair Value Gap (FVG)|FVG]] für
  später offen.
- **Tageszeit bestimmt die Füllwahrscheinlichkeit**: Früh in der Session (z.B. direkt nach der
  8:30-Uhr-News) bleibt genug Zeit für eine vollständige Füllung; entsteht der Gap spät in der
  NY-Session (ab ca. 10–11 Uhr), bleibt er häufiger nur teilweise offen und wird zum FVG für einen
  späteren Tag.
- **Volle Füllung = balancierte Preislieferung**: Ist der gesamte Gap geschlossen, gilt die
  Preislieferung auf beiden Seiten als abgeschlossen — danach besteht keine Erwartung mehr, dass
  Preis unter den Schlusspunkt der Füllung zurückfällt. Passiert das doch, gilt das Setup als
  verdächtig (Teilgewinne sichern statt an der ursprünglichen These festhalten).

## Inversion-Varianten

**Jede PD Array gibt es auch als Inversion-Variante** — also auch einen Inversion Breaker Block
(vgl. [[IFVG (Inverse Fair Value Gap)]], [[Breaker Block]]).

## Verwandt

- [[Fair Value Gap (FVG)]], [[Chain of Custody (Q-Validation)]]
- [[ORG (Opening Range Gap) & 1st Presented FVG]]
- [[IPDA Data Ranges]] — PDs bleiben bis zu 60 Tage rückwirkend nutzbar
- [[Kurz Notizen (Source)]], [[Advanced ICT Liquidity Concepts (Source)]]
