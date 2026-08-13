---
tags: [concept, ict, trading-ict, core]
created: 2026-08-01
updated: 2026-08-10
sources: ["[[2026-08-10 - Navigating High Resistance Liquidity Run Conditions (Source)|Navigating High Resistance Liquidity Run Conditions (Source)]]", "[[Fair Valuation (Source)]]", "[[2026-08-04 - ICT Price Action Chronicles - Market On Close Macro (Source)|ICT Price Action Chronicles - Market On Close Macro (Source)]]", "[[2026-08-01 - Part 2 High Precision Secrets To Intraday Price Action (Source)|Part 2 High Precision Secrets To Intraday Price Action (Source)]]", "[[ICT Mentorship Core Content - Month 1 - Fair Valuation (Source)]]", "[[ICT Mentorship Core Content - Month 04 - ICT Fair Value Gaps FVG (Source)]]", "[[2026-08-06 - ICT Price Action Chronicles - The Science Of Anticipation In Price Action (Source)|ICT Price Action Chronicles - The Science Of Anticipation In Price Action (Source)]]"]
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

## Fair Value — zwei Perspektiven

- **Retail**: Fair Value = der Preis, zu dem verkauft (Premium) bzw. gekauft (Discount) wird —
  siehe [[Equilibrium Vs. Discount]].
- **Market Maker**: Fair Value wird über die FVG selbst hergestellt, nicht nur über Premium/Discount.

## Checkliste: sind wir im fairen Preisbereich?

1. Große Dealing Range: sind wir im korrekten Premium/Discount?
2. Aktuelle (mittlere) Dealing Range: gleiche Prüfung.
3. Kleinste Dealing Range: gleiche Prüfung.

Erst wenn alle drei Ebenen übereinstimmen, gilt der Preis als "im fairen Bereich" für einen Entry.

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
- [[Kurz Notizen (Source)]]
