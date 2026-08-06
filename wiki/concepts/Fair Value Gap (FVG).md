---
tags: [concept, ict, trading-ict, core]
created: 2026-08-01
updated: 2026-08-06
sources: ["[[Fair Valuation (Source)]]", "[[ICT Price Action Chronicles - Market On Close Macro (Source)]]", "[[Part 2 High Precision Secrets To Intraday Price Action (Source)]]", "[[ICT Mentorship Core Content - Month 1 - Fair Valuation (Source)]]", "[[ICT Mentorship Core Content - Month 04 - ICT Fair Value Gaps FVG (Source)]]"]
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

## Fair Value — zwei Perspektiven

- **Retail**: Fair Value = der Preis, zu dem verkauft (Premium) bzw. gekauft (Discount) wird —
  siehe [[Equilibrium Vs. Discount]].
- **Market Maker**: Fair Value wird über die FVG selbst hergestellt, nicht nur über Premium/Discount.

## Checkliste: sind wir im fairen Preisbereich?

1. Große Dealing Range: sind wir im korrekten Premium/Discount?
2. Aktuelle (mittlere) Dealing Range: gleiche Prüfung.
3. Kleinste Dealing Range: gleiche Prüfung.

Erst wenn alle drei Ebenen übereinstimmen, gilt der Preis als "im fairen Bereich" für einen Entry.

## Ergänzungen aus Kurz Notizen

- **Doppelte Sicherheit**: Auf **2 FVG** warten statt auf eines, dabei müssen trotzdem mindestens
  **10 Handle** im Setup stecken — sonst ist der Move zu klein, um das Risiko zu rechtfertigen.
- **5-Candle-Regel**: Verbringt Preis innerhalb eines FVG mehr als **5 Candles** ober-/unterhalb des
  C.E, sinkt die Wahrscheinlichkeit stark, dass die Idee noch aufgeht — zu viel Zeit gebraucht.
  Optimal sind **1–3 Candles** mit einem starken, explosiven Move Richtung Ziel-DOL. Bei einem SIBI
  muss Preis dabei unter dem C.E bleiben, bei einem BISI darüber.
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
[[Part 2 High Precision Secrets To Intraday Price Action (Source)]].

## Verwandt

- [[Volume Imbalance (VII)]] — bestimmt die Grenzen des FVG
- [[Equilibrium Vs. Discount]]
- [[PD Array]]
- [[Turtle Soup]] — nutzt FVG als Retracement-Ziel nach einem Sweep
- [[Balanced Price Range (BPR)]], [[Breakaway Gap]], [[Chain of Custody (Q-Validation)]]
- [[Kurz Notizen (Source)]]
