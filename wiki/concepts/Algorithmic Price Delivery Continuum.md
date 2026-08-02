---
tags: [concept, ict, trading-ict, lecture-2025, routine, fvg]
created: 2026-08-02
updated: 2026-08-02
sources: ["[[Algorithmic Price Delivery Continuum (Source)]]", "[[Balanced Price Chart Bsp (Source)]]"]
---

# Algorithmic Price Delivery Continuum

ICTs eigener Name für seine **Lesemethode**: bei jedem Candle-Close alle Timeframes von oben nach
unten durchgehen, um ein Gefühl für den laufenden Orderflow zu bekommen. Kein Setup, sondern die
Routine, aus der ein Setup überhaupt erst sichtbar wird.

## Der Durchlauf

- Bei jedem **4H-Close**: alle Timeframes durchgehen. Idealerweise dasselbe bei jedem **1H-Close** —
  zu jeder neuen Handelsstunde geht es zurück in den 1H-Chart, dort wird auch generell am meisten
  Zeit verbracht.
- Bei jedem **15M-Close** dasselbe, danach runter auf **5M**, und so weiter bis in den **1M-Chart**.
- In den unteren Timeframes muss **nicht viel Zeit** verbracht werden — relevant ist allein der
  **Candle-Close**, dazu die PD Arrays und wo die Liquidität liegt.

Die vier Fragen bei jedem Durchlauf:

1. Sind wir gerade **Premium oder Discount**?
2. Werden **PD Arrays respektiert** oder nicht?
3. Geht es auf die **Sellside oder Buyside** zu — oder sucht Preis eine PD?
4. Wo liegt die Liquidität?

Der Nutzen zeigt sich im Gegenlauf: bei bearishem Bias kann der 1M-Chart kurzzeitig bullish
aussehen — *„das einzige was wir machen müssen ist abwarten"*.

![[ICT 2025 - APDC 02.png]]
*15M-SIBI: im 1M-Chart wirkt es kurzzeitig bullish, der übergeordnete Bias bleibt aber bearish.*

## Welche Hälfte eines FVG zählt

- Bei einem **SIBI** ist die **obere Hälfte** relevant.
- Bei einem **BISI** die **untere Hälfte**.

Siehe [[BISI & SIBI (Buyside-Sellside Imbalance)]], [[Fair Value Gap (FVG)]].

## Wann ein FVG offen bleibt

Diese Lecture liefert den **Mechanismus** hinter der [[Balanced Price Range (BPR)]]-Regel:

> Wird in der oberen Hälfte eines SIBI **länger** hoch und runter getradet und der Preis dabei
> gehalten, macht das diese Hälfte zur **Balanced Price Range** — sie ist damit abgearbeitet.
> Spiegelbildlich für ein BISI.

Daraus folgt die Antizipation, ob ein FVG offen bleibt:

- Ist eine Hälfte **imbalanced** (nur eine einzige Candle ist stark durchgelaufen), während in der
  anderen Hälfte **viel Zeit** verbracht wurde → es wird erwartet, dass Preis die imbalanced Hälfte
  füllt und die andere **offen bleibt**.
- Bei einem Higher-Timeframe-FVG ist deshalb entscheidend, **was am 50-%-Level (C.E) passiert ist**:
  liegt dort eine Balanced Price Range oder nicht? Ohne BPR ist eher mit einem Fill oder sogar einem
  Durchschießen zu rechnen.

![[ICT 2025 - APDC 03.png]]
*15M-SIBI mit Balanced Price Range über dem C.E — die obere Hälfte ist abgearbeitet.*

![[ICT 2025 - APDC 05.png]]
*Untere Hälfte imbalanced (eine einzige starke Candle), obere Hälfte mit viel verbrachter Zeit —
erwartet wird ein Fill der unteren 50 %, während die oberen offen bleiben.*

## FVG-Bildungszeiten

FVGs bilden sich nach bestimmten Zeiten — genannt werden die Viertelstunden-Fenster:

**10:00–10:15 / 10:15–10:30 / 10:30–10:45 / 10:45–11:00**

In jedem Timeframe ab 15M bildet sich über den Tag verteilt ein FVG. Vgl.
[[ICT Macros & Leading Candles]].

## Kein FVG = Hände still

Bildet sich im **15M- oder 5M-Timeframe kein FVG**, befindet man sich sicher in einem
**High Resistance Liquidity Run** — dann Abstand halten und nicht handeln.

![[ICT 2025 - APDC 06.png]]
*Kein FVG in 15M/5M → High Resistance Liquidity Run.*

Gegenstück: [[Low Resistance Liquidity Run]].

## Verwandt

- [[Balanced Price Range (BPR)]] — die Regel, deren Mechanismus hier erklärt wird
- [[Fair Value Gap (FVG)]], [[BISI & SIBI (Buyside-Sellside Imbalance)]]
- [[Low Resistance Liquidity Run]], [[ICT Macros & Leading Candles]]
- [[ICT Day Trade Routine]] — die tägliche Analyse-Routine, in die dieser Durchlauf gehört
- [[Smart Money Concepts (SMC)]]
