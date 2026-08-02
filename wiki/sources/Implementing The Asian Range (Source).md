---
tags: [source, ict, trading-ict, market-maker-primer, sessions, bias]
created: 2026-08-02
updated: 2026-08-02
raw: "[[Implementing The Asian Range]]"
raw_path: "raw/trading-ict/Market Maker Primer/Implementing The Asian Range.md"
---

# Implementing The Asian Range (Source)

Die inhaltlich dichteste Lektion des [[Market Maker Primer Course (Source)|Market Maker Primer]].

## Kernpunkte

### Der Bias ist Vorbedingung, nicht Ergebnis

> *„Die gesamte Theorie geht nur auf, wenn wir einen Bias haben!"*

Selbst wenn das Asia Low gesweept wird und der Preis danach Richtung Buyside geht, ist das **keine
Trading-Option**, solange kein Bias vorliegt. Die Asia Range ist ein Rahmen zur Bestätigung, kein
Signalgeber.

### Definition und Aufbau

- Auf den Folien: **7:00 PM NY → 12:00 AM NY**, gemessen als **Highest High / Lowest Low**.
- Über und unter der Range bilden sich Orders — *„Orders & Sentiment Build Up"*. Sie bildet das
  Market Sentiment ab.
- **Ab 12 Uhr NY ist der Preis bereit sich zu bewegen** — Mitternacht ist zugleich der Start des
  Tages für den Algorithmus.

![[MMP - AsianRange 03.png]]
*Die Asian Range von 7:00 PM bis 12:00 AM New York — Highest High und Lowest Low fassen die Phase,
in der sich Orders und Sentiment aufbauen.*

### Konsolidierung = Trending Day

> **Consolidation Asia Range = Trending Tag.**

Eine enge, konsolidierende Asia Range ist ein starkes Argument für einen Trendtag — *„der Algo wird
abliefern"*. Der Preis steht still, bevor der Intraday Directional Impulse Swing kommt.

### Die Range bleibt nach dem Sweep relevant

Kehrt der Preis im späteren Tagesverlauf **in die Asia Range zurück**, kaufen die Big Boys dort
(spiegelbildlich für Sells). Ein Sweep entwertet die Range also nicht.

### Ablaufmuster nach Bias

- **Bullish**: Preis geht **unter** die Asia Range, dann darüber — und bleibt ab diesem Moment
  bullish.
- **Bearish**: Preis geht **erst über** die Asia Range, dann darunter — und bleibt darunter.

Begründung: In den meisten Fällen bildet **London** das High/Low des Tages, im schlimmsten Fall
**Asia** — deshalb ist der Stop Loss unter/über der Asia Range geschützt.

### Opening Price als Kaufzone

Der Bereich vom **12-Uhr-Midnight-Opening bis 11 Uhr** wird ausgemalt — bis 11 Uhr, weil der NY-AM-Trend
maximal bis dahin anhalten soll und danach mindestens ein kurzfristiges Retracement erwartet wird.
In einem bullishen Szenario will man den Preis **unter dem Opening** sehen, bevor man kauft
(spiegelbildlich für Sells).

## Extrahiert nach

- [[Asian Range]], [[Midnight Opening Range]], [[ICT Killzones]]

## Verwandt

- [[Asia Session (Source)]], [[Understanding The ICT Judas Swing (Source)]]
- [[AMD Cycle (Accumulation – Manipulation – Distribution)]]
