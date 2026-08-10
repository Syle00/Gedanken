---
tags: [concept, ict, trading-ict, lecture-2025, routine, fvg]
created: 2026-08-02
updated: 2026-08-10
sources: ["[[Algorithmic Price Delivery Continuum (Source)]]", "[[Balanced Price Chart Bsp (Source)]]", "[[ICT Gems - Balanced Price Ranges Inside Fair Value Gaps (Source)]]"]
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

### Präzisierung 2025: vier FVGs pro Stunde als Erwartung

[[ICT Gems - Balanced Price Ranges Inside Fair Value Gaps (Source)]] formuliert das als
durchgehende Regel statt als Beispielliste:

> In **jedem** Viertelstunden-Fenster bildet sich ein FVG — auf dem 15M- oder 5M-Chart. Damit
> entstehen **vier potenzielle FVGs pro Stunde**. ICT nennt das ausdrücklich
> *"high frequency trading algorithmically"* und leitet daraus ab: *"I can trade every single
> 60-minute candlestick, because I have four opportunities."*

**Wichtige Einschränkung**: Das FVG muss sich in diesem Viertelstunden-Fenster nur **bilden** — es
muss **nicht** angehandelt werden. *"It need not trade into the fair value gap in that 15-minute
interval; it just means that you have to see them forming, because that's the algorithm posting
little areas where it's going to refer back to later on."*

**Richtungsfilter dazu**: Zieht Preis zur **Buyside**, sucht man bullishe FVGs — **oder** bearishe
FVGs, die **scheitern** und zu [[IFVG (Inverse Fair Value Gap)|IFVGs]] werden. Spiegelbildlich zur
Sellside.

> Diese Vier-pro-Stunde-These ist konkret genug für einen eigenen Backtest auf MNQ und wurde als
> Backlog-Punkt in `algo/PLAN.md` eingetragen.

## Kein FVG = Hände still

Bildet sich im **15M- oder 5M-Timeframe kein FVG**, befindet man sich sicher in einem
**High Resistance Liquidity Run** — dann Abstand halten und nicht handeln.

![[ICT 2025 - APDC 06.png]]
*Kein FVG in 15M/5M → High Resistance Liquidity Run.*

Gegenstück: [[Low Resistance Liquidity Run]].

### Das Warteverfahren, ausformuliert (2025)

Die 2025er Fassung macht daraus eine explizite Schleife statt einer Haltung — und benennt den
Extremfall:

1. Bildet sich im laufenden Viertelstunden-Fenster kein FVG → **15 Minuten warten**.
2. Immer noch keines → **weitere 15 Minuten warten**.
3. So weiter **bis zum Sessionende**.
4. *"If the entire session was high resistance, you did nothing and you took no trade — come back
   the following afternoon or next trading day."*

ICT stellt das ausdrücklich als **erste Prüfung überhaupt** voran: *"that's the reason why I teach
that number one premise is: are we in low resistance or high resistance liquidity run conditions?"*

## Der Zyklus in Reinform: "nicht Top-Down, sondern Cycling"

Die deutlichste Beschreibung der Methode, die dieser Seite den Namen gibt:

- Bei **jedem** Stundenschluss zurück auf den 60-Min-Chart — Ineffizienzen? Werden welche
  respektiert? Zielt es auf Buyside oder Sellside?
- Bei **jedem** 15-Min-Schluss dasselbe auf dem 15-Min-Chart.
- Bei **jedem** 5-Min-Schluss dasselbe auf dem 5-Min-Chart.
- Dazwischen zurück auf den **1-Min-Chart** für die Ausführung (bei Executions laut ICT sogar den
  **15-Sekunden-Chart**).

> *"I'm not living on those time frames — I'm just referring to it real quick and then going right
> back. **It's not top-down analysis, it's cycling through continuously.**"*

Der Zweck ist nicht Vollständigkeit, sondern laufende Rückkopplung: Man sucht die Stellen, an denen
Preis eine PD Array respektiert — **oder scheitert**, denn auch das Scheitern ist Information.

**Universalitätsanspruch**: ICT betont, dieselbe Logik auf NASDAQ, ES, Commodities und Bonds
anzuwenden — *"everything that's traded uses this logic"*; das Beispiel läuft nur zufällig auf
GBP/USD.

## Verwandt

- [[Balanced Price Range (BPR)]] — die Regel, deren Mechanismus hier erklärt wird
- [[Fair Value Gap (FVG)]], [[BISI & SIBI (Buyside-Sellside Imbalance)]]
- [[Low Resistance Liquidity Run]], [[ICT Macros & Leading Candles]]
- [[ICT Day Trade Routine]] — die tägliche Analyse-Routine, in die dieser Durchlauf gehört
- [[Smart Money Concepts (SMC)]]
