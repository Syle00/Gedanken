---
tags: [concept, ict, trading-ict, core]
created: 2026-08-01
updated: 2026-08-06
sources: ["[[Open Float (Source)]]", "[[Quarterly Shifts & IPDA Data Ranges (Source)]]"]
---

# Quarterly Shift

Alle **3–4 Monate** findet ein markanter Liquidity-Shift/Trendwechsel statt (Beispiel USDX-Daily:
etwa alle 4 Monate) — genutzt als HTF-Ankerpunkt für [[Classic Swing Trading Approach|Swing]]- und
[[One Shot One Kill Model|OSOK]]-Setups, eng verknüpft mit den [[IPDA Data Ranges]] und immer im
Rahmen einer Makroanalyse.

## Terminologie & Marker-Methodik

- **Underlying** = das aktuell gehandelte Asset. **Benchmark** = Vergleichsasset für SMT
  (z.B. USDX, NQ, ES).
- Marker werden nach Trading-Monaten gesetzt: liegt ein Shift z.B. im November, geht man einen
  vollen Trading-Monat zurück auf den 1. Oktober als ersten Marker und arbeitet von dort chronologisch
  vorwärts.
- **Präzise Marker-Regel** (Begleitvideo zu [[Quarterly Shifts & IPDA Data Ranges (Source)]]): der
  Marker sitzt auf dem ersten Handelstag des **zuletzt vollständig abgeschlossenen Kalendermonats** —
  nicht auf dem laufenden Monat. Analyse im November → Marker auf den 1. Oktober.

![[image 49.png]]
*USDX Daily über ein Jahr ausgemalt: alle ca. 4 Monate ein markanter Shift.*

- Für den Lookback (siehe [[IPDA Data Ranges]], 20/40/60 Tage) wird 1 Trading-Tag pro Monat als
  Bezugspunkt genutzt.

![[image 52.png]]
*Lookback-Beispiel: anhaltend bullisher Kontext trotz Shift — Liquidität liegt weiterhin unter der
Sellside.*

## Cast Forward (Vorwärts-Projektion)

Nach dem Lookback (60/40/20 Handelstage zurück vom Marker, siehe [[IPDA Data Ranges]]) wird
symmetrisch nach vorne projiziert:

- 20/40/60 Handelstage **rechts** vom Marker markieren das Zeitfenster, in dem der nächste
  Quarterly Shift erwartet wird — die Summe aus bereits verstrichener Zeit seit dem letzten Shift
  und der Projektion bleibt bei ~60 Handelstagen. Lag der letzte Shift schon 40 Tage zurück, wird
  nur noch 20 Tage weiter projiziert.
- Praxisbeleg (USDX/EURUSD, Marker 1.12.2015): das nächste bedeutende Hoch im EURUSD fiel exakt auf
  die 60-Tage-Cast-Forward-Marke — die Fenster taugen also nicht nur rückwärts (Liquiditätssuche),
  sondern auch vorwärts zur Zeitprognose des nächsten Shifts.

## Shift-Timing erkennen

- Ein großer bullischer Impuls-Swing, der zusätzlich ein altes High sweept, bedeutet: ein alter
  Meilenstein wurde erreicht → danach wird ein Retracement erwartet (Gewinnmitnahme). Spiegelbildlich
  für Shorts.
- Gewissheit über einen Shift entsteht, wenn über den gesamten vorherigen Zeitraum **kein**
  signifikanter Run/Sweep auf die Gegenseite (z.B. Sellside) stattgefunden hat — erst wenn das alte
  High/Low genommen wird, beginnt sich der Shift zu bestätigen.

![[image 60.png]]
*Vor dem eigentlichen Shift gab es keinen signifikanten Run auf die Sellside — das änderte sich
erst, nachdem das alte High genommen wurde.*

- Ein Short-Term-High-Sweep erzeugt nicht zwangsläufig ein neues (höheres) High — bleibt das aus,
  ist das selbst ein Hinweis auf einen bevorstehenden Shift (verwandt: [[Turtle Soup]]).

![[image 62.png]]
*Nach dem Sweep eines Shortterm-Highs wird nicht einmal ein neues High geschaffen — Hinweis auf
einen bevorstehenden Shift.*

## Verwandt

- [[Open Float & Liquidity Pools]]
- [[IPDA Data Ranges]]
- [[One Shot One Kill Model]]
- [[Buy & Sell Program]] — Underlying/Benchmark-Divergenz als eigenständige Methode, ein laufendes
  Akkumulations-/Distributionsprogramm um einen Quarterly Shift herum zu erkennen
