---
tags: [synthesis, trading-ict, marktdaten, backtest]
created: 2026-08-07
updated: 2026-08-07
sources: ["[[OHLC-Datenanalyse (Workflow)]]"]
---

# Muster-Validierung (laufend)

**Generiert** von `algo/backtest_ohlc.py` aus allen Handelstagen in `raw/marktdaten/`. Prueft ICT-Behauptungen aus dem Wiki gegen die tatsaechlichen Daten, statt sie als gegeben zu uebernehmen. Wird bei jedem neuen Handelstag neu ausgefuehrt — siehe [[../algo/PLAN.md|Algo-Projekt]].

Datenbasis: 43 Handelstag(e) — 2026-06-08, 2026-06-09, 2026-06-10, 2026-06-11, 2026-06-12, 2026-06-15, 2026-06-16, 2026-06-17, 2026-06-18, 2026-06-22, 2026-06-23, 2026-06-24, 2026-06-25, 2026-06-26, 2026-06-29, 2026-06-30, 2026-07-01, 2026-07-02, 2026-07-06, 2026-07-07, 2026-07-08, 2026-07-09, 2026-07-10, 2026-07-13, 2026-07-14, 2026-07-15, 2026-07-16, 2026-07-17, 2026-07-20, 2026-07-21, 2026-07-22, 2026-07-23, 2026-07-24, 2026-07-27, 2026-07-28, 2026-07-29, 2026-07-30, 2026-07-31, 2026-08-03, 2026-08-04, 2026-08-05, 2026-08-06, 2026-08-07 (5m-Basis).

## Abdeckung (Nutzerwunsch: alle PD Arrays, das gesamte Wiki)

Diese Seite soll perspektivisch jede pruefbare Wiki-Behauptung gegen echte Daten testen. Stand jetzt automatisch pruefbar (Detektoren existieren in `tools/analyze_ohlc.py`):

- [[Fair Value Gap (FVG)]] (inkl. C.E-Fuellung), [[Volume Imbalance (VII)]], [[ORG (Opening Range Gap) & 1st Presented FVG]] (ueber FVG-Detektor), Liquidity Sweeps / [[Open Float & Liquidity Pools]], [[Market Structure Shift (MSS)]] / BOS-MSS / [[CISD (Change in State of Delivery)]] (als Struktur-Proxy), [[ICT Macros & Leading Candles]]-Expansion.

**Noch ohne eigenen Detektor** (Backlog in `algo/PLAN.md`, wird nach und nach ergaenzt statt in einem Schritt geraten): [[Order Block]] + Varianten ([[Breaker Block]], [[Rejection Block]], [[Mitigation Block]], [[Reclaimed Order Block]]), [[IFVG (Inverse Fair Value Gap)]], [[Balanced Price Range (BPR)]], [[Central Bank Dealers Range (CBDR)]], [[New Week Opening Gap (NWOG) Bias|NWOG/NDOG]], [[Optimal Trade Entry (OTE)]], [[Breakaway Gap]], [[Suspension Block]], [[Judas Swing]] als eigenes Zeitfenster (bislang nur ueber Sweeps sichtbar, nicht als benanntes Ereignis), [[Quarterly Shift]], [[SMT (Smart Money Divergence)]] (braucht ein zweites Symbol, bisher wird nur MNQ erfasst).

## Fair Value Gap / C.E-Fuellung

Testet die verbreitete ICT-Behauptung "das C.E eines FVG/ORG wird meist erreicht" (oft als ~70% zitiert) an den tatsaechlichen Daten. Zwei unterschiedliche Fragen, die in der Praxis oft vermischt werden:

| | Alle FVGs | Nur groessere FVGs (≥ Median-Kerzenrange des Tages) |
|---|---|---|
| Anzahl | 1826 | 186 |
| C.E erreicht (Preis beruehrt die 50%-Linie) | 88% | 74% |
| Komplett gefuellt (ganze Luecke geschlossen) | 85% | 68% |

„C.E erreicht" und „komplett gefuellt" sind unterschiedliche Ereignisse — die 70%-Zahl, die kursiert, bezieht sich vermutlich auf ersteres. Diese Seite zaehlt beide getrennt, um genau diese Vermischung sichtbar zu machen. Siehe [[Fair Value Gap (FVG)]], [[ORG (Opening Range Gap) & 1st Presented FVG]].

## Volume Imbalance (VII)

6892 VII (Close→Open-Luecke zwischen zwei Kerzen), 96% davon wieder komplett gefuellt. Siehe [[Volume Imbalance (VII)]].

## Liquidity Sweeps

437 Sweeps insgesamt, davon 60% mit sofortiger Rueckeroberung (`bars_back == 0`) — der Rest brauchte laenger, siehe `confirm`-Fenster in [[OHLC-Datenanalyse (Workflow)]].

## Market Structure Breaks (BOS/MSS → CISD)

706 Structure Breaks insgesamt: 400 BOS (Fortsetzung), 306 MSS (Richtungswechsel) — 43% der Breaks waren ein Richtungswechsel. Jeder Break ist ein potenzieller [[CISD (Change in State of Delivery)]]; siehe dort fuer die Bedingung (Imbalance muss enthalten sein), die dieser Zaehler noch nicht prueft.

## Macro-Fenster-Expansion

180 von 766 Macro-Fenstern (XX:50–XX+1:10) waren Expansion (>1,5x Tages-Median) = 23%. Bei 24 Fenstern/Tag waere ein Gleichverteilungs-Erwartungswert bei ~keinem besonderen Fenster — dass es ueberhaupt planbare Haeufungen gibt (z.B. [[NY Lunch Macro Model]]), ist erst ab mehr Tagen pruefbar.

## Pro Tag

| Tag | FVGs (groß) | C.E erreicht | Sweeps | BOS/MSS | Macro-Expansionen |
|---|---|---|---|---|---|
| 2026-06-08 | 2 | 50% | 8 | 12/4 | 5/18 |
| 2026-06-09 | 14 | 57% | 8 | 13/8 | 7/18 |
| 2026-06-10 | 3 | 100% | 12 | 12/6 | 5/18 |
| 2026-06-11 | 5 | 80% | 12 | 7/8 | 5/18 |
| 2026-06-12 | 2 | 100% | 14 | 6/12 | 5/18 |
| 2026-06-15 | 2 | 50% | 5 | 11/8 | 3/18 |
| 2026-06-16 | 5 | 60% | 11 | 10/10 | 4/18 |
| 2026-06-17 | 3 | 67% | 14 | 4/11 | 5/18 |
| 2026-06-18 | 2 | 50% | 10 | 12/8 | 2/18 |
| 2026-06-22 | 3 | 67% | 14 | 7/9 | 4/18 |
| 2026-06-23 | 3 | 67% | 10 | 10/5 | 5/18 |
| 2026-06-24 | 8 | 50% | 9 | 7/8 | 5/18 |
| 2026-06-25 | 9 | 78% | 13 | 10/8 | 6/18 |
| 2026-06-26 | 1 | 100% | 14 | 8/11 | 2/18 |
| 2026-06-29 | 5 | 60% | 11 | 11/5 | 5/18 |
| 2026-06-30 | 5 | 60% | 11 | 11/5 | 5/18 |
| 2026-07-01 | 4 | 100% | 9 | 11/6 | 5/18 |
| 2026-07-02 | 4 | 50% | 7 | 9/9 | 7/18 |
| 2026-07-06 | 3 | 67% | 10 | 10/6 | 5/18 |
| 2026-07-07 | 3 | 100% | 13 | 6/9 | 5/18 |
| 2026-07-08 | 2 | 100% | 7 | 10/8 | 4/18 |
| 2026-07-09 | 5 | 100% | 12 | 13/3 | 3/18 |
| 2026-07-10 | 6 | 100% | 13 | 12/4 | 4/18 |
| 2026-07-13 | 1 | 100% | 15 | 7/9 | 3/18 |
| 2026-07-14 | 4 | 100% | 10 | 5/9 | 3/18 |
| 2026-07-15 | 8 | 75% | 16 | 8/12 | 3/18 |
| 2026-07-16 | 3 | 67% | 8 | 12/2 | 3/18 |
| 2026-07-17 | 6 | 50% | 12 | 8/10 | 4/18 |
| 2026-07-20 | 5 | 100% | 7 | 9/5 | 5/18 |
| 2026-07-21 | 2 | 100% | 7 | 10/5 | 4/18 |
| 2026-07-22 | 1 | 100% | 12 | 13/5 | 4/18 |
| 2026-07-23 | 5 | 40% | 6 | 10/6 | 4/18 |
| 2026-07-24 | 3 | 100% | 11 | 10/8 | 4/18 |
| 2026-07-27 | 9 | 67% | 7 | 10/5 | 6/18 |
| 2026-07-28 | 3 | 100% | 10 | 10/9 | 2/18 |
| 2026-07-29 | 8 | 88% | 14 | 8/7 | 7/18 |
| 2026-07-30 | 4 | 50% | 9 | 8/7 | 3/18 |
| 2026-07-31 | 6 | 67% | 9 | 12/7 | 4/18 |
| 2026-08-03 | 3 | 100% | 15 | 11/7 | 1/17 |
| 2026-08-04 | 4 | 50% | 4 | 10/7 | 3/18 |
| 2026-08-05 | 2 | 50% | 7 | 9/5 | 6/18 |
| 2026-08-06 | 4 | 100% | 10 | 4/5 | 3/18 |
| 2026-08-07 | 6 | 83% | 1 | 4/5 | 2/11 |

## Verwandt

- [[OHLC-Datenanalyse (Workflow)]] — Detektoren, die diese Seite aggregiert
- [[Fair Value Gap (FVG)]], [[ORG (Opening Range Gap) & 1st Presented FVG]], [[CISD (Change in State of Delivery)]]
- `algo/PLAN.md` — Code-Idee 1 (Backtest-Harness), diese Seite ist die erste Version