---
tags: [concept, ict, trading-ict, orderflow, fvg, 2026]
created: 2026-08-16
updated: 2026-08-16
sources: ["[[2026-08-15 - The Week In The Life Cycle Of Price (Source)|The Week In The Life Cycle Of Price (Source)]]"]
---

# Gladhanding

ICTs Begriff für das **Paaren von Orders**, das ein Ausführen/Drucken auf einem bestimmten
Preislevel überhaupt erst ermöglicht:

> *„Gladhanding is where there's pairing of orders and it allows to book or print at a specific
> price level."*

Handelsrelevant ist vor allem der **Negativfall**: Wenn Preis eine PD Array anläuft und dort
**nicht** gladhandet — die C.E. also gar nicht erst erreicht —, ist das ein eigenständiges
Order-Flow-Signal.

## Die Regel

Bei einem bullishen [[BISI & SIBI (Buyside-Sellside Imbalance)|BISI]]:

- **Normalfall (bullish, stark)**: Der Rücklauf beginnt in der **oberen Hälfte** des Gaps und läuft
  von dort wieder hoch. Smart Money kauft in dieser oberen Hälfte — *„that's confirming bullish
  order flow."*
- **Stärkster Fall**: Preis **berührt die C.E. nicht einmal** und legt auch keine Bodies darunter
  ab. ICT wörtlich: *„If it can't even touch consequent encroachment, it really is bullish."*
  Es bleibt kein *unfinished business* darunter zurück.
- **Spiegelbildlich bearish** bei einem SIBI.

Zugrunde liegt die Regel, dass ein **bullisher Markt Ineffizienzen offen lassen darf** — ein
nicht gefülltes Gap ist dort kein Mangel, sondern Stärkezeichen. (ICT beansprucht die Erstlehre
dieses Punktes ausdrücklich für sich.)

## Anwendung als Bestätigungs-Check

Im Fallbeispiel der Woche 11.–15.08.2026 lieferte das zweimal einen Bias-Check, jeweils **ohne**
Level 2, DOM, Footprint oder Volume Profile — allein aus Open/High/Low/Close:

1. **Daily-Ebene**: Beim Rücksetzer in das Daily-BISI berührte das Low die C.E. nicht → bullish.
2. **Dienstag**: Das Tageslow erreichte das BISI-High (= Gap-Obergrenze) nicht → zweite
   Bestätigung, dass der bullishe Order Flow intakt ist.

Beide zusammen begründeten ICTs öffentlich vorab gepostete Erwartung höherer Preise.

## Abgrenzung

- Gladhanding beschreibt den **Ausführungs-/Pairing-Vorgang**, nicht das Level selbst — das Level
  ist die C.E. der jeweiligen [[PD Array]].
- Verwandt, aber nicht identisch mit der Pairing-Logik in [[Open Float & Liquidity Pools]] (dort:
  genommene Sellside-Liquidity wird mit Kaufpositionen gepaart). Gladhanding ist der allgemeinere
  Mechanismus, der auch ohne Liquidity-Sweep an einer Gap-Grenze stattfindet.
- Die Body-vs-Wick-Bewertung des Ergebnisses steht in
  [[Institutional Order Flow (Body vs Wick)]].

> ⚠️ **Noch nicht gebacktestet.** Die Aussage „C.E. nicht berührt → Fortsetzung wahrscheinlicher"
> ist als deterministische Regel formulierbar (Detektor `tools/analyze_ohlc.py::fvgs` liefert die
> Gap-Grenzen, C.E. = Mittelpunkt) und damit gegen `raw/marktdaten/` prüfbar. Steht noch aus,
> siehe `algo/PLAN.md`.

## Verwandt

- [[BISI & SIBI (Buyside-Sellside Imbalance)]], [[Fair Value Gap (FVG)]]
- [[Institutional Order Flow (Body vs Wick)]] — Bodies als Volumen-Träger
- [[Equilibrium Vs. Discount]] — die obere/untere Hälfte als Premium/Discount des Gaps
- [[Algorithmic Order Flow]], [[PD Array]]
- [[2026-08-15 - The Week In The Life Cycle Of Price (Source)|The Week In The Life Cycle Of Price (Source)]]
