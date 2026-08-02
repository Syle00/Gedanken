---
tags: [concept, ict, trading-ict, 2026, flagship]
created: 2026-08-01
updated: 2026-08-01
sources: ["[[ICT 2026 Smart Money Concepts Lecture - January 02, 2026 (Source)]]", "[[From Vision To Execution (Source)]]", "[[How Do I Engage Markets When I Don't Have An Initial Bias (Source)]]", "[[ICT 2022 - Episode 03 Market ST + Modell 22 (Source)]]", "[[ICT 2022 - Episode 06 Institutional Orderflow (Source)]]", "[[ICT 2022 - Episode 18 Higher Timeframe 15m 1H is Key (Source)]]"]
---

# Modell 22

2026er-Weiterentwicklung des Turtle-Soup-/CISD-Setups mit präzisem IFVG-Trigger.

> **Das Modell ist deutlich älter als gedacht.** Es taucht bereits in der
> [[ICT MentorShip 2022 (Source)|MentorShip 2022]] unter genau diesem Namen auf — dort als
> **Liq Sweep + Displacement + FVG**. Die 2026er Fassung unten ist also keine Neuerfindung, sondern
> eine Präzisierung eines seit mindestens 2022 laufenden Modells.

## Trigger

- Ein **High** bildet sich, danach ein **Higher High** (selbst wenn nur mit 3 Candles), das entweder
  in eine Higher-Timeframe-PD hineinläuft oder eine High-Probability-Liquidity nimmt — **inklusive
  eines **[[Market Structure Shift (MSS)]] + SIBI**.
- Formel: **High + Higher High mit Failure-MSS + SIBI = [[Turtle Soup]]**.
- Das erste FVG, das sich bildet, nachdem 2 Highs genommen wurden, wird in die Zukunft projiziert
  (ausgemalt) und als Ziel-PD genutzt.

## Auswahlregel: linkes IFVG bevorzugen

Bildet sich ein Swing High mit einem FVG (BISI) auf der **linken** Seite und einem FVG (SIBI) auf
der rechten Seite, wird **immer das linke [[IFVG (Inverse Fair Value Gap)|IFVG]]** genutzt — es ist
Teil der Buyside-Curve und deutlich stärker/relevanter als die PD Arrays der Sellside-Curve.

## Nach Liquidity-Erreichen

Nach Erreichen der Liquidity/Higher-PD wird auf die Bestätigung durch Marketstructure gewartet:
**2 Higher Highs/Lows + Shift mit FVG**, optimalerweise mit einem IFVG.

## Die 2022er Ausführung

Aus der [[ICT MentorShip 2022 (Source)|MentorShip 2022]] — der praktische Ablauf, den die 2026er
Fassung voraussetzt:

### Timeframe-Abstieg bis zum FVG

- Der Ablauf beginnt im **15M**: dort wird der **Liquidity Sweep** eines signifikanten Swing
  High/Low abgewartet. Erst danach geht es abwärts.
- Vom **5M** aus wird weiter heruntergegangen, bis ein FVG da ist — ausdrücklich über die
  **unüblichen Timeframes 4M, 3M, 2M** bis notfalls 1M.
- **Kein FVG = kein Trade.** *„Liq sweep auf 5min aber kein FVG → kein Trade, deshalb gehen wir einen
  Timeframe weiter runter."*
- Der **1M-Chart ist der unprofitabelste** — er wird genutzt, aber ungern.
- Liegen **mehrere FVGs** vor, wird bei Shorts das **höchste** genommen — auch wenn Preis womöglich
  gar nicht mehr so weit hochkommt.

![[ICT 2022 - Ep06 04.png]]
*Liq Sweep im 5M ohne FVG — Abstieg über 4M auf 3M, wo das SIBI liegt.*

### Was das Displacement leisten muss

> Ein **Displacement muss unter das gesamte Manipulation Leg** gehen — also meist unter das Swing
> Low, spiegelbildlich über das Swing High.

### Wann der CISD valide ist

> **Ein CISD ist valide, wenn eine Imbalance darin liegt.** Ohne Imbalance zählt der Shift nicht.

### Die wichtigste Warnung

> *„Nur weil wir unser Model haben — also 22 mit Liq Sweep, Displacement, FVG — heißt es nicht, dass
> es richtig ist."*

Entscheidend bleibt der **übergeordnete Timeframe-Trend**: war der Markt den ganzen Tag über London
und NY AM bullish und ergibt sich in der NY PM ein Modell-22-Long, kann es gut sein, dass gerade die
**Daily Wick** gebildet wird und der Markt bearish ist. Das Modell ist ein Trigger, kein Bias.

## Verwandt

- [[Market Structure Shift (MSS)]] — der Struktur-Baustein, jetzt eigenständig definiert
- [[Turtle Soup]], [[CISD (Change in State of Delivery)]]
- [[BISI & SIBI (Buyside-Sellside Imbalance)]], [[IFVG (Inverse Fair Value Gap)]]
- [[Dealing Range]] — der Premium/Discount-Rahmen, in dem das Setup zu prüfen ist
- [[No-Bias Engagement Routine]] — nutzt Modell-22-Entry als letzten Schritt
- [[ICT MentorShip 2022 (Source)]]
