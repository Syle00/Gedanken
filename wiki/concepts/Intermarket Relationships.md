---
tags: [concept, ict, trading-ict]
created: 2026-08-01
updated: 2026-08-06
sources: ["[[How To Use Intermarket Analysis (Source)]]", "[[Interest Rate Differentials (Source)]]", "[[Using 10 Year Notes In HTF Analysis (Source)]]", "[[ICTCross Currency Relationships und HTF Institutional Order Flow (Source)]]", "[[ICT Mentorship Core Content - Month 04 - Interest Rate Effects On Currency Trades (Source)]]"]
---

# Intermarket Relationships

Grobe Korrelationsregeln zwischen Asset-Klassen, genutzt um Bias über Märkte hinweg zu bestätigen
(ergänzt [[SMT (Smart Money Divergence)]] und [[Commodity Mega-Trades]] / [[Bond Mega-Trades]]).

![[image 75.png]]
*Übersicht "Key Intermarket Relationships": Zinsen, Bonds, Stocks, Commodities und Currencies im
Zusammenspiel.*

## Regeln

- **Zinsen ↑ → Bonds ↓** (Bonds mögen keine hohen Interest Rates).
- **Bonds ↑ ↔ Stocks ↑** — laufen gekoppelt zusammen; Bonds gelten als **Leading Indicator** für den
  Stock-Markt, allerdings mit **6–12 Monaten Zeitverzögerung**.
- **Bonds ↓ → Commodities ↑** (und umgekehrt); ebenso **Bond Yields ↑ → Commodities ↑**.
- **Currencies** werden von Commodities beeinflusst.
- **Commodities** gelten als Leading Indicator für Inflationsauswirkungen.
- Referenz-Indizes: **CRB Index** (stark auf Agriculture/Grain gewichtet, weniger Metalle/Energy),
  **Goldman Sachs Commodity Index** als Vergleichswert.

## Interest Rate Differentials (Carry Trade)

- Je größer der Zins-Unterschied zwischen zwei Währungspaaren, desto mehr Volatilität.
- Große Funds positionieren sich in **High-Yield-Currencies** gegen **Low-Yield-Currencies**
  ("buying strong pairs, selling weak pairs" — klassischer Carry-Trade-Gedanke).

![[image 97.png]]
*Große Funds setzen auf High-Yield- vs. Low-Yield-Currency: starke Paare kaufen, schwache
verkaufen.*

- Ein OI-Drop (Gewinnmitnahme, Orders verlassen den Markt) im Verbund mit einer erreichten
  Higher-Timeframe-PD-Array ist ein starkes Reversal-Signal — besonders mächtig in Kombination mit
  der Interest-Rate-Differenz im jeweiligen FX-Paar.

![[image 99.png]]
*Ein Drop im Open Interest zeigt Gewinnmitnahmen — kombiniert mit einer HTF-PD-Array dreht der
Markt.*

## Quarterly-Shift-Verifikation über Bonds/Yields/DXY

- Laufen **USDX und Bonds zusammen** (statt entgegengesetzt), deutet das auf **fehlende Trending
  Conditions** hin — der Markt steckt wahrscheinlich in einer Konsolidierung.
- "Money seeks Yields": Yields ↑ → Dollar ↑, Bonds ↓ (und umgekehrt).

![[image 82.png]]
*Steigende Yields lassen die Bonds fallen, während der Dollar steigt — "Money seeks Yields".*

- Bonds/Yields/DXY gemeinsam nutzen, um einen [[Quarterly Shift]] zu verifizieren, zu bestätigen
  oder frühzeitig zu erkennen.

![[image 86.png]]
*USDX läuft im Chart entgegengesetzt zu den Bonds — Divergenz als Warnsignal für fehlende
Trending Conditions.*

## Interest Rate Triad: Order-Block-Validierung über Bond-Divergenz (2022er Video-Ergänzung)

Aus [[ICT Mentorship Core Content - Month 04 - Interest Rate Effects On Currency Trades (Source)]]
— konkrete Technik, um einen Order Block/Liquidity Pool/FVG auf dem Dollar Index (oder einer
anderen Benchmark) zu **bestätigen**, bevor man ihn handelt:

- **Interest Rate Triad** = die drei US-Zins-Futures-Märkte **30-Year Treasury Bond**, **10-Year
  Note**, **5-Year Note** (kostenlos z.B. auf barchart.com einsehbar).
- **Smart-Money-Distribution** (bearish für die Benchmark): Benchmark macht ein **höheres Hoch**,
  aber **mindestens eine** der drei Zins-Märkte macht dabei ein **niedrigeres Hoch** (Failure
  Swing) — Divergenz signalisiert, dass die Rally nicht durch neue Käufe, sondern durch
  Distribution getrieben ist.
- **Smart-Money-Akkumulation** (bullish): Benchmark macht ein **niedrigeres Tief**, aber
  mindestens einer der drei Zins-Märkte macht ein **höheres Tief**.
- Es muss **nicht** bei allen drei Märkten gleichzeitig auftreten — **eine** Divergenz unter dreien
  reicht bereits als Bestätigungssignal.
- **Workflow**: trifft Preis auf der Benchmark (z.B. Dollar Index) einen vorab identifizierten
  Order Block/Liquidity Pool/FVG, wird die Interest Rate Triad geprüft — zeigt sie eine passende
  Divergenz, gilt der Level als von Smart Money bestätigt; zeigt sie **keine** Divergenz, wird das
  Setup **verworfen** statt gehandelt.
- Kausalkette: Zinsmärkte (fallend im Chart = Zinsen steigen) → treibt Dollar Index → treibt
  Fremdwährungen invers — bestätigt dieselbe "Money seeks Yields"-Logik wie oben, nur jetzt als
  **Timing-/Validierungswerkzeug** statt als reine Bias-Quelle.

## Cross Currency: Paarauswahl über News und EURGBP

Aus dem [[ICTCross Currency Relationships und HTF Institutional Order Flow (Source)|Market Maker Primer]]
— die FX-interne Anwendung derselben Logik. **Alles fängt mit dem Economic Calendar an**, nicht mit
dem Chart.

- **News-Asymmetrie als Filter**: Big News für den Euro, keine für GBP → der Euro wird bis zum
  Release zurückgehalten und konsolidiert, der **Cable ist freier und weniger manipuliert**. Also auf
  GBP konzentrieren.
- **EURGBP zeigt, wer führt.** Er kann nur aus **zwei** Gründen stark steigen/fallen: entweder EU ist
  bullish und Cable konsolidiert — oder Cable ist bullish und EU konsolidiert. Eine dritte
  Möglichkeit gibt es nicht.
- **Reihenfolge**: zuerst den **USDX** auf klare Divergenz prüfen, dann das Paar wählen, bei dem
  bessere Liquidität und Imbalances liegen.

## Verwandt

- [[SMT (Smart Money Divergence)]]
- [[Bond Mega-Trades]], [[Commodity Mega-Trades]]
- [[Open Float & Liquidity Pools]] — OI-Drop als gemeinsames Signal
- [[Quarterly Shift]]
- [[Order Block]] — Ziel der Interest-Rate-Triad-Validierung
