---
tags: [concept, ict, trading-ict, fvg, orderflow, 2026]
created: 2026-08-16
updated: 2026-08-16
sources: ["[[2026-07-13 - How To Probe Low Probability RTH Opening Ranges (Source)|How To Probe Low Probability RTH Opening Ranges (Source)]]", "[[2026-05-13 - Turning Loss Into Gain - Market Alchemy (Source)|Turning Loss Into Gain - Market Alchemy (Source)]]"]
---

# Kerzenzahl in einer Ineffizienz

**Wie viele Kerzen** Preis innerhalb eines [[Fair Value Gap (FVG)|FVG]] verbringt, ist selbst ein
Signal — je mehr, desto schwächer die Fortsetzung in Gap-Richtung. ICTs einzige Anwendung von
Kerzen-Zählerei überhaupt:

> *„The only time I'm counting candles is when inside inefficiencies."*

## Die Skala

| Kerzen im Gap | Lesart |
|---|---|
| **1** | Ideal — Markt hat es eilig |
| **2** | Noch in Ordnung (*„one, two at most"*) |
| **3** | *„The probability starts to shift lower"* |
| **4–5** | Letzte Chance — *„it's got to do it now or it's failing"* |
| **> 5** | Gescheitert; Ziel liegt jetzt in der Gegenrichtung |

> *„A market that's in a hurry to get somewhere **doesn't want to go in the gap**."*

## Was die ideale eine Kerze tut

Drei Merkmale, die ICT für den Ein-Kerzen-Fall nennt:

1. Sie lässt **keinen Body** im Gap zurück.
2. Sie schließt das Gap **nicht vollständig**.
3. Sie handelt **nicht einmal bis zur C.E.** (Mittelpunkt).

Das ist dieselbe Aussage wie [[Gladhanding]] — dort aus der Gegenrichtung formuliert (die *nicht
erreichte* C.E. als Stärkezeichen). Beide Regeln beschreiben denselben Sachverhalt: **Ein starker
Markt hält sich nicht in seinen eigenen Ineffizienzen auf.** Vgl. auch „Offener Rest =
Stärke-Signal" auf [[Fair Value Gap (FVG)]].

## Abgrenzung gegen Support/Resistance

Am Fallbeispiel ausdrücklich gegen die Retail-Lesart gestellt: Wo klassische Chartlehre an
derselben Stelle *„Support broken, turned resistance"* liest, liest ICT die **Verweildauer in der
Ineffizienz**:

> *„Why, if it's bearish, why is it spending so much time in that?"*

Nach fünf Kerzen im Gap kippte im Beispiel die Erwartung — Preis lief anschließend zurück nach
oben und wischte die nachgezogenen Short-Stops aus.

## Verweildauer *zwischen* zwei PD Arrays = manuelle Intervention (2026-05-13)

Aus [[2026-05-13 - Turning Loss Into Gain - Market Alchemy (Source)|Turning Loss Into Gain — Market Alchemy (Source)]] —
dieselbe Lesart, aber auf den Raum **zwischen** zwei Arrays statt in ein Gap hinein angewandt:

> *„Way too many candles in here. **That's how you know they're holding it.** It's between two PD
> arrays. This doesn't make any sense at all. So that's how you can identify it."*

Zweite, unabhängige Signatur derselben Diagnose: **beidseitige Dochte**. Sieht die Zone aus wie ein
Stachelschwein (*„like a porcupine, where it has these little needles and thorns on both sides"*),
ist es Eingriff; wären es glatte Kerzen mit erkennbarer Richtung, wäre es normaler
Higher-Timeframe-Orderflow, der eine PD Array abarbeitet.

Praktische Folge im Fallbeispiel: ICT wertete die Zone als *„shenanigans"* und **blieb bei seiner
These**, statt die Verweildauer als Widerlegung zu lesen — die Kerzenzahl sagte hier „Manipulation",
nicht „falsch positioniert".

## Verwandt, aber getrennt: der Geschwindigkeits-Maßstab für ein zweites Bein

Ebenfalls aus derselben Quelle, und ausdrücklich **keine** Anwendung dieser Seite: Nach einem
ersten Lauf zu einem Pool (dort sieben Kerzen) erwartet ICT den zweiten Lauf **schneller** —
*„I want less than seven candlesticks to get to that buy side."* Begründung ist nicht die
Ineffizienz, sondern die Ausführung: Tempo verhindert, dass die Gegenseite ihre Orders zurückzieht.

> ⚠️ **ICT verwahrt sich dort ausdrücklich gegen mechanisches Zählen**: *„Don't start turning this
> into a science… ‚See, ICT counts candles and it's a specific number' — **I don't do those
> things.**"* Das ist ein **Vergleich zweier Beine**, keine feste Zahl.
>
> Zusammen mit dem Zitat oben („the only time I'm counting candles is when inside inefficiencies")
> ergibt das ein konsistentes Bild: Kerzenzahl ist bei ICT durchgehend eine **qualitative Aussage
> über Verweildauer und Tempo**, nie ein Auslöser. Die Skala oben ist entsprechend als Erwartung zu
> lesen, nicht als Signalgeber — was für einen Backtest heißt, dass die Trennschärfe zwischen 2 und
> 3 Kerzen die eigentlich zu prüfende Behauptung ist.

## Praktische Konsequenz

- Die Regel ist ein **Abbruchkriterium**, kein Entry-Trigger: Sie sagt, wann eine bestehende
  Erwartung fallenzulassen ist.
- Sie liefert eine harte Frist an einem sonst zähen Tag — siehe
  [[Low Probability Day Probing]], wo ICT sie genau dafür einsetzt.
- Der Timeframe ist der, auf dem das FVG eingezeichnet wurde (im Beispiel 1-Min).

> ⚠️ **Noch nicht gebacktestet — guter Kandidat.** Die Regel ist vollständig deterministisch: FVG
> aus `tools/analyze_ohlc.py::fvgs`, danach die Kerzen zählen, deren Range das Gap schneidet, und
> die Fortsetzungsrate in Gap-Richtung nach Kerzenzahl gruppieren. Erwartung laut ICT: monoton
> fallende Fortsetzungsrate mit Bruch zwischen 2 und 3. Vermerkt in `algo/PLAN.md`.

## Verwandt

- [[Fair Value Gap (FVG)]], [[Gladhanding]] — dieselbe Aussage aus der Gegenrichtung
- [[Liquidity Void]], [[Balanced Price Range (BPR)]]
- [[Institutional Order Flow (Body vs Wick)]] — Bodies als das, was im Gap zählt
- [[Low Probability Day Probing]]
