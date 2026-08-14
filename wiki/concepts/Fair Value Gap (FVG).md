---
tags: [concept, ict, trading-ict, core]
created: 2026-08-01
updated: 2026-08-14
sources: ["[[2026-08-10 - Navigating High Resistance Liquidity Run Conditions (Source)|Navigating High Resistance Liquidity Run Conditions (Source)]]", "[[Fair Valuation (Source)]]", "[[2026-08-04 - ICT Price Action Chronicles - Market On Close Macro (Source)|ICT Price Action Chronicles - Market On Close Macro (Source)]]", "[[2026-08-01 - Part 2 High Precision Secrets To Intraday Price Action (Source)|Part 2 High Precision Secrets To Intraday Price Action (Source)]]", "[[ICT Mentorship Core Content - Month 1 - Fair Valuation (Source)]]", "[[ICT Mentorship Core Content - Month 04 - ICT Fair Value Gaps FVG (Source)]]", "[[2026-08-06 - ICT Price Action Chronicles - The Science Of Anticipation In Price Action (Source)|ICT Price Action Chronicles - The Science Of Anticipation In Price Action (Source)]]", "[[2025-01-19 - ICT Private Mentorship - High Probability FVGs Masterclass (Source)|High Probability FVG's (Masterclass)]]", "[[2024-09-16 - ICT 2024 Mentorship - How To Trade ICT FVGs Correctly (Source)|How To Trade ICT FVGs Correctly]]"]
---

# Fair Value Gap (FVG)

Preiszone zwischen zwei Candles, in der **kein Trading stattgefunden hat** — entsteht bei starken
impulsiven Moves. Solange kein Handel in dieser Zone stattfand, besteht ein berechtigtes Interesse,
dass Preis dorthin zurückkehrt, um beide Richtungen (Bullish/Bearish) fair anzubieten.

## Einzeichnen: Open und Close, nicht die Wicks

> **Immer auf Open und Close achten.** Liegt zwischen dem Close einer Candle und dem Open der
> nächsten eine **[[Volume Imbalance (VII)|VII]]**, wird diese beim Einzeichnen des FVG
> **mitgenommen**. Nur wenn keine VII vorhanden ist, werden die **Wicks** als Begrenzung genutzt.

Wer das FVG allein über die Wick-Extrema aufzieht, bekommt also falsche Grenzen, sobald eine VII im
Spiel ist — mit Folgen für C.E, Quadranten und jeden darauf aufbauenden Entry. Details und
Zahlenbeispiel auf [[Volume Imbalance (VII)]].

### Präzisierung: Körperkante, nicht Close bzw. Open (2026-08-13)

„Close der einen, Open der nächsten Candle" ist eine Kurzform, die nur gilt, solange beide Candles
**in Richtung des Moves** schließen. Maßgeblich ist immer die **Körperkante**:

| Seite eines bullishen FVG | Grenze | Formel |
|---|---|---|
| unten | Körper-**Oberkante** Candle 1, falls Körper Candle 2 darüber beginnt | `max(o₁,c₁)`, sonst `high₁` |
| oben | Körper-**Unterkante** Candle 3, falls sie über dem Körper von Candle 2 endet | `min(o₃,c₃)`, sonst `low₃` |

Bei einem **bearishen** FVG gespiegelt. Ist Candle 1 oder 3 eine **Gegenkerze** (bearishe Candle 1
in einem bullishen FVG o.ä.), tauschen Open und Close die Rollen — die naive Close/Open-Formel
liefert dann eine Kante mitten im Kerzenkörper und erfindet eine VII, wo der Körper den Bereich
längst gehandelt hat. Belegt an 13 vom Nutzer im TradingView-Chart eingezeichneten MNQ-Boxen vom
13.08.2026 (Regressionstest: `tools/test_fvg_vii.py`).

## Stark (High Probability) vs. normal (2026-08-13)

> **Ein valides *starkes* FVG muss einen Swing High/Low brechen** — erst dadurch entsteht ein
> [[Market Structure Shift (MSS)|MSS]] bzw. BOS. Ein Displacement, das nur in freien Raum läuft,
> hinterlässt zwar eine Lücke, aber keine strukturelle Aussage.

Damit zerfällt jede FVG-Liste in zwei Klassen:

| Klasse | Kriterium | Bedeutung |
|---|---|---|
| **stark** | Displacement- oder Bestätigungskerze **schließt** durch einen bestätigten, noch intakten Swing | High-Probability-Bedingung, Handelskandidat |
| *wick* | Swing nur mit dem Docht genommen, kein Close darüber/darunter | eher Sweep/Judas als Break — Vorsicht |
| *normal* | kein Swing im Weg | Lücke ohne strukturelle Aussage, nur als Draw relevant |

Zwei Bedingungen, damit der Break zählt:

1. **Der Swing muss zum Zeitpunkt von Kerze 1 bereits bestätigt sein** (Fraktal braucht Nachlauf) —
   sonst ist die Einordnung Lookahead.
2. **Der Swing muss noch intakt sein.** Ein bereits genommenes Level ist keine Liquidität mehr;
   sonst gilt in einem Trend jedes Folge-FVG als „stark" gegen dasselbe, längst gebrochene Level.

Implementiert in `tools/analyze_ohlc.py::fvgs()` — jedes FVG trägt die Felder `strong`, `broke`
(`close`/`wick`/`None`), `swing` und `ms` (`MSS`/`BOS`, falls `structure_breaks()` auf derselben
Kerze ein Event meldet).

### Größe: nur relativ zur Session-Volatilität

> **Ein großes FVG mit MSS/BOS ist High Probability** — aber „groß" ist keine absolute Punktzahl.
> Kurz nach dem 9:30-Open ist die Volatilität hoch und die Kerzen sind ein Vielfaches der
> London-Kerzen; Richtung NY PM fällt sie wieder Richtung London-Niveau.

Gemessen an 27 MNQ-Handelstagen (siehe
[[FVG-Stärke, Session-Volatilität & Confluence (laufend)]]): der 9:30-Open trägt die **2,8-fache**
FVG-Größe von London (13,50 vs. 4,75 Punkte). Das Verhältnis **FVG-Größe ÷ lokale Kerzenrange**
ist dagegen in jeder Session ≈ **0,45** — ein FVG ist immer rund die halbe Kerzenrange groß.
Deshalb gehört jeder Größen-Schwellwert auf `size / Median-Kerzenrange der letzten 30 Kerzen`,
nie auf feste Punkte.

### Confluence

Zusätzlich wahrscheinlichkeitserhöhend, wenn das FVG mit einer **Higher-Timeframe-PD-Array**
überlappt — konkret mit deren Qs/C.E. — oder mit [[New Day Opening Gap (NDOG)|NDOG]] /
[[New Week Opening Gap (NWOG) Bias|NWOG]]. Backtest-Stand: die HTF-Qs-Überlappung hält als
kleiner, konsistenter Zusatzeffekt (bester $/Trade-Wert der Auswertung), für die NDOG-Confluence
gibt es bislang **keinen Beleg**. Details und der wichtige Messvorbehalt auf der Syntheseseite.

## Zeitstempel: die mittlere Kerze

Ein FVG trägt die Zeit seiner **Displacement-Kerze** (der mittleren), nicht der dritten. Genau
dort sitzt die Box im Chart; die dritte Kerze bestätigt sie nur. `fvgs()` liefert zusätzlich
`t_start`/`t_end` für die volle Drei-Kerzen-Spanne.

## Fair Value — zwei Perspektiven

- **Retail**: Fair Value = der Preis, zu dem verkauft (Premium) bzw. gekauft (Discount) wird —
  siehe [[Equilibrium Vs. Discount]].
- **Market Maker**: Fair Value wird über die FVG selbst hergestellt, nicht nur über Premium/Discount.

## Checkliste: sind wir im fairen Preisbereich?

1. Große Dealing Range: sind wir im korrekten Premium/Discount?
2. Aktuelle (mittlere) Dealing Range: gleiche Prüfung.
3. Kleinste Dealing Range: gleiche Prüfung.

Erst wenn alle drei Ebenen übereinstimmen, gilt der Preis als "im fairen Bereich" für einen Entry.

## Wo High-Probability-FVGs entstehen (Masterclass, 2026-08-14)

Aus [[2025-01-19 - ICT Private Mentorship - High Probability FVGs Masterclass (Source)|High Probability FVG's (Masterclass)]] —
drei Bedingungen, die zusammen erfüllt sein müssen:

1. **Der Draw on Liquidity steht vorher fest.** *„You have to know what it's reaching for."* ICTs
   eigene Negativdefinition: *„if it's not one-sided… it's not high probability"* — die Bedingung
   eines [[Low Resistance Liquidity Run]]. Fehlt sie, ist Nichtstun die Antwort.
2. **Lage in der richtigen Hälfte der Vortagesrange.** Vortages-High/-Low mit Fib messen,
   Equilibrium markieren: **bearish** muss das FVG zwischen Equilibrium und Vortages-Low liegen,
   **bullish** zwischen Equilibrium und Vortages-High. Begründung: *„IPDA will not want to go back
   above the previous day's midpoint."* Ob das FVG im Vortag oder im neuen Tag entstand, ist egal —
   entscheidend ist die **Preiszone**.
3. **Entstehung in einer [[ICT Killzones|Killzone]].**

Ergänzend: **Daily Highs/Lows der letzten 3 Tage** vorher markieren; der **Stop** gehört an den
Swing High/Low **vor** der Entstehung des FVG, nicht an die Gap-Kante; er bleibt dort **bis zum
ersten Partial** und wird danach nur reduziert, nicht auf Breakeven gerissen.

> ⚠️ Eigene Messung: von den drei Kriterien hält vor allem die **Vortageshälfte**; die Killzone
> allein ist in MNQ nicht messbar. ICTs *„98 % strike rate"* ist nicht reproduzierbar (gemessen
> 36–38 % bei 2R). Zahlen und Vorbehalte:
> [[High-Probability-FVG - ICTs Kriterien gegen eigene Daten (laufend)]].

## Entry, Stop und Quadranten (2024er Mentorship, 2026-08-14)

Aus [[2024-09-16 - ICT 2024 Mentorship - How To Trade ICT FVGs Correctly (Source)|How To Trade ICT FVGs Correctly]].
Die drei Kerzen haben feste Rollen: **1** = linke Kante, **2** = Displacement-/Trigger-Kerze (sie
*ist* das FVG), **3** = rechte Kante.

| | bullish (BISI) | bearish (SIBI) |
|---|---|---|
| **Entry** | Low Kerze 3 **+ 1 Tick** | High Kerze 3 **− 1 Tick** |
| **Stop aggressiv** | unter Low Kerze 2 | über High Kerze 2 |
| **Stop konservativ** | unter Low Kerze 1 | über High Kerze 1 |
| **Nachlegen** | oberer Quadrant → C.E. → unterer Quadrant | unterer Quadrant → C.E. → oberer Quadrant |

> *„We are not supply and demand… **we don't deal with zones**. There are specific price levels."*
> Deshalb: **jede Ineffizienz rastern** („you have to always grade your inefficiencies") — Kante,
> Quadranten, C.E. Der Entry sitzt bewusst *einen Tick vor* der Kante, damit der Fill zustande
> kommt, bevor Preis ins Gap läuft.

**Stop-Verfeinerung**: hat Kerze 1 selbst einen Wick, der ein eigenes Gap bildet („two layers of
gaps"), genügt ein Tick jenseits des **C.E. dieses Wicks**. Nach dem Bruch des Hochs weiter zum
**unteren Quadranten** des FVG trailen.

### Die ferne Hälfte soll offen bleiben

> **Bullish**: *„the best perfect scenario is the market only drops into the upper half of the gap,
> it leaves that **lower half untouched** — that's indicating it's extremely bullish."* Bearish
> gespiegelt. Dosierung: die nahe Hälfte höchstens **ein- bis zweimal** besuchen.

Das ist dieselbe Aussage wie die Viertel-Regel unten, nur gröber — und sie gilt laut derselben
Quelle **genauso für Wicks und Order Blocks** (bullish: kein Candle-Close unter dem Mean Threshold;
ein Stich durch ist tolerierbar).

> ⚠️ Als **Auswahl**kriterium taugt es nicht: liegt der Stop hinter Kerze 2, heißt „ferne Hälfte
> offen" fast zwangsläufig „Stop nie erreicht" — die gemessenen 99 % Trefferquote beschreiben den
> Gewinner, statt ihn vorherzusagen. Der Wert liegt im **Trade-Management**. Auch das Tempo-Signal
> („Kerze 4 läuft sofort ins Gap") schneidet gemessen *schlechter* ab als der Durchschnitt. Siehe
> [[High-Probability-FVG - ICTs Kriterien gegen eigene Daten (laufend)]].

**Mindest-Bewegungsraum**: *„it's got to have at least this much movement potential… **20 handles**"*
zwischen Entry und erstem Ziel, damit 15 Handles Gewinn realistisch sind. Ausdrücklich **gegen**
10-Handle-Ziele: *„10 handles is static price action, you can get stopped out and be right."*

Implementiert in `tools/analyze_ohlc.py::fvgs()` als Felder `entry`, `stop_c2`, `stop_c1`, `q25`,
`q75`, `near_touches`, `far_touches`, `far_half_open`, `fast`.

## Die vier Level eines FVG — wie tief darf der Rücklauf gehen?

Aus [[ICT Gems - How to Trade the Final Hour Macro (Source)]]. Jedes FVG wird in **vier gleiche
Teile** zerlegt; ICT nennt sie von unten nach oben: **Low → unteres Viertel (25 %) → C.E. (50 %) →
oberes Viertel (75 %) → High**.

Für einen **bullishen** Kontext ergibt sich daraus eine klare Rangfolge (spiegelbildlich bearish):

| Wie tief läuft Preis zurück? | Lesart |
|---|---|
| hält im **oberen Viertel (75 %)** | **stärkstes Signal** — der Wunschfall |
| berührt die **C.E.** und stützt dort | zulässig, aber schwächer — *"you're allowing that to happen"* |
| handelt **unter die C.E.** | Prämisse bröckelt |

> ICT ausdrücklich: *"if you're bullish you really don't want to see it trade down to consequent
> encroachment"* — die C.E. ist als hochsensibler Punkt zu respektieren, nicht als Ziel zu
> erwarten.

**Ein bereits berührtes FVG ist nicht mehr gleichwertig.** Kehrt Preis ein zweites Mal in dasselbe
Gap zurück, wertet ICT das **nicht** als zusätzliche Stärke — gesucht wird dann eine frische,
noch unberührte Array. Deckt sich mit der Grundregel "eine bereits genutzte PD Array ist nicht mehr
gültig" aus [[Low Resistance Liquidity Run]].

Hält das obere Viertel, ist das genau die Konstellation für einen
[[Institutional Order Flow Entry Drill (IOFED)]] — Teil-Entry oben, ohne auf die volle Füllung zu
warten.

## Ineffizienz ist fraktal — die Farbrollen-Analogie

Aus [[ICT Gems - The Functions of a Macro (Source)]]: Ein großes Down-Close-Displacement ist als
Ganzes eine Sellside-Imbalance/Buyside-Ineffizienz ([[BISI & SIBI (Buyside-Sellside Imbalance)|SIBI]])
— aber **innerhalb** dieser Bewegung liegen weitere, im höheren Timeframe unsichtbare Ineffizienzen.

> ICTs Bild: Wie eine Farbrolle an der Wand. Zu Beginn trägt sie dick auf; je weiter man rollt,
> desto mehr kleine Stellen bleiben, an denen keine Farbe ankam — und über die man erneut rollen
> muss.

Praktisch heißt das: In eine große Ineffizienz **hineinzoomen** (15-Min → 5-Min → 1-Min, bei Bedarf
bis zum **15-** oder **5-Sekunden-Chart**) und dort die *tatsächlichen* kleinen FVGs und
[[Volume Imbalance (VII)|Volume Imbalances]] als Ziel nehmen, statt die grobe Zone als Ganzes zu
handeln. Wie weit ein Rücklauf in die große Zone reicht, entscheidet sich an diesen kleinen
Elementen.

**Bid/Ask-Tick**: Um eine Volume Imbalance oder ein Level tatsächlich zu handeln, muss Preis
**mindestens einen Tick darüber hinaus** — sonst kommt der Print wegen der Spanne zwischen Bid und
Ask nicht zustande. Genau dieser eine Tick ist auch der Fill-Mechanismus des IOFED.

## Ergänzungen aus Kurz Notizen

- **Doppelte Sicherheit**: Auf **2 FVG** warten statt auf eines, dabei müssen trotzdem mindestens
  **10 Handle** im Setup stecken — sonst ist der Move zu klein, um das Risiko zu rechtfertigen.
- **5-Candle-Regel**: Verbringt Preis innerhalb eines FVG mehr als **5 Candles** ober-/unterhalb des
  C.E, sinkt die Wahrscheinlichkeit stark, dass die Idee noch aufgeht — zu viel Zeit gebraucht.
  Optimal sind **1–3 Candles** mit einem starken, explosiven Move Richtung Ziel-DOL. Bei einem SIBI
  muss Preis dabei unter dem C.E bleiben, bei einem BISI darüber.
- **Teilweise offen gelassenes FVG = Continuation-Signatur** (Live-Trade 2026-08-10): Läuft Preis
  bullish weiter und füllt ein neu entstandenes BISI **nicht komplett**, ist der offen gebliebene
  Rest laut ICT *"one of the strongest signatures that the market's still likely to go higher"*.
  Vollständige Füllung ist früh im Lauf nicht per se schlecht, macht den Nachweis der Fortsetzung
  aber schwerer. Wird das Gap gar nicht erst angetastet, wirkt es als Breakaway-/Measuring-Gap
  ([[Breakaway Gap]]) relativ zum Ursprung des Laufs. Spiegelbildlich bei SIBI im bearishen Lauf.
  Quelle: [[2026-08-10 - Navigating High Resistance Liquidity Run Conditions (Source)|Navigating High Resistance Liquidity Run Conditions (Source)]].
- **Pflicht-Check eine Timeframe tiefer**: Sobald sich ein FVG bildet, MUSS mindestens eine
  Timeframe tiefer geprüft werden, was Preis innerhalb des FVG gemacht hat — siehe
  [[Balanced Price Range (BPR)]]. Bildet sich auf 15-/5-Min kein FVG, gilt das als **High
  Resistance**: abwarten, bis wieder ein FVG entsteht.
- **FVG auf dem EQ** der Dealing Range ist ebenfalls relevant und kann **reclaimed** werden (siehe
  [[Equilibrium Vs. Discount]]).
- **1-Min-FVG an Quadranten eines Daily-FVG** (siehe [[Chain of Custody (Q-Validation)]]) sind oft
  besonders stark und einseitig ("onesided").
- **Wick schlägt FVG**: Im Daily Chart gilt — liegt oberhalb/unterhalb eines FVG bereits die nächste
  Wick, ist die Wick das relevantere nächste Level, nicht das FVG.
- **Präzisierung (2026, MOC-Grundlagen-Lecture)**: Teilt sich ein Wick den Preisbereich direkt mit
  einem FVG (Wick links vom FVG, beide überlappen), hat der **gesamte Wick** Vorrang — nicht nur der
  FVG-Anteil. Details und Beispiel: [[Market on Close (MOC) Macro Model]].
- **2-Gap-Regel**: Treten zwei Gaps unmittelbar hintereinander auf, wird für den Stop Loss das
  **erste** der beiden Gaps genutzt.
- Bildet sich ein sehr großes Displacement genau an einem Quadranten eines FVG oder einer Wick, wird
  das FVG im Lower Timeframe oft zu einem [[Breakaway Gap]].

![[Kurz Notizen - Breakaway Gap Example.png]]
*Großes Displacement an einem FVG-/Wick-Quadranten — im Lower Timeframe entsteht daraus oft ein Breakaway Gap.*

## Akkumulation/Distribution am FVG (2022er Video-Ergänzung)

Aus [[ICT Mentorship Core Content - Month 1 - Fair Valuation (Source)]] — Market-Maker-Perspektive
auf denselben Preisbereich, unabhängig von der Retail-Premium/Discount-Sicht:

- Eine Liquidity-Void-/FVG-Zone entsteht, wenn Preis **nur in eine Richtung** durchhandelt (keine
  Gegenbewegung innerhalb der Range) — das ist gleichzeitig die Zone, in der Market Maker
  Positionen **aufgebaut** haben (Accumulation, bei Long-Bias am unteren Ende) und später **wieder
  abbauen** (Distribution, am oberen Ende, sobald Preis dorthin zurückkehrt).
- Dieselbe FVG kann also aus zwei Blickwinkeln relevant sein: Discount-Ende = Fair Value für
  Market-Maker-Käufe, Premium-Ende (weiterer, später entstandener FVG näher an alten Highs) = Fair
  Value für deren Verkäufe/Gewinnmitnahme.
- Praktische Konsequenz: mehrere überlappende Prüfungen sollten in dieselbe Richtung zeigen —
  Position in der Gesamtrange (unteres Drittel), Position relativ zum EQ (unter 50 %) **und** Nähe
  zu einem [[Order Block]]/[[PD Array]] — erst wenn alle drei übereinstimmen, gilt der Bereich als
  hochwahrscheinliche Akkumulationszone.

## FVG × Liquidity Void × Turtle Soup — dasselbe Level, drei Blickwinkel

Aus [[ICT Mentorship Core Content - Month 04 - ICT Fair Value Gaps FVG (Source)]]: ein FVG auf
höherem Timeframe zeigt sich auf tieferem Timeframe oft als [[Liquidity Void]] (mehrere Candles
statt einer einzelnen Lücke), und ein Fehlausbruch unter/über ein altes Tief/Hoch genau an diesem
Level kombiniert es mit [[Turtle Soup]] zu einer einzigen, mehrfach bestätigten Zone. Je mehr dieser
Blickwinkel am selben Preis zusammenfallen, desto höher die Wahrscheinlichkeit.

## Immediate Rebalance (2026-Ergänzung)

Wird der Low/High einer Candle **von der unmittelbar nächsten Candle** erneut angelaufen (nicht
irgendwann später), gilt das als "Immediate Rebalance" — ein eigenständig benannter Spezialfall, der
nur in diesem engen Zeitfenster (die direkt folgende Candle) zählt. Quelle:
[[2026-08-01 - Part 2 High Precision Secrets To Intraday Price Action (Source)|Part 2 High Precision Secrets To Intraday Price Action (Source)]].

## Offener Rest = Stärke-Signal (2026-Ergänzung)

Aus [[2026-08-06 - ICT Price Action Chronicles - The Science Of Anticipation In Price Action (Source)|ICT Price Action Chronicles - The Science Of Anticipation In Price Action (Source)]]: bleibt
beim Reversal-Versuch ein kleiner Teil eines Gaps **ungeschlossen**, obwohl Preis eigentlich tiefer
(bzw. höher, invertiert) erwartet würde, gilt das als **Unwilligkeit, dorthin zu gehen** — ein
Stärke-Zeichen für die Gegenrichtung. Besonders am oberen Bereich eines Buyside-Imbalance/
Sellside-Inefficiency-Gaps genutzt, als eigenständiges drittes PD Array neben Daily-IFVG und
Wick-C.E.

## Verwandt

- [[Volume Imbalance (VII)]] — bestimmt die Grenzen des FVG
- [[Equilibrium Vs. Discount]]
- [[PD Array]]
- [[Turtle Soup]] — nutzt FVG als Retracement-Ziel nach einem Sweep
- [[Balanced Price Range (BPR)]], [[Breakaway Gap]], [[Chain of Custody (Q-Validation)]]
- [[High-Probability-FVG - ICTs Kriterien gegen eigene Daten (laufend)]] — die Kriterien gegen MNQ-Daten gemessen
- [[Kurz Notizen (Source)]]
