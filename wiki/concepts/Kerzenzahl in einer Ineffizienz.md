---
tags: [concept, ict, trading-ict, fvg, orderflow, 2026]
created: 2026-08-16
updated: 2026-08-16
sources: ["[[2026-07-13 - How To Probe Low Probability RTH Opening Ranges (Source)|How To Probe Low Probability RTH Opening Ranges (Source)]]"]
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
