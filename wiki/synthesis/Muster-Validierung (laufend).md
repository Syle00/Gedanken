---
tags: [synthesis, trading-ict, marktdaten, backtest]
created: 2026-08-04
updated: 2026-08-04
sources: ["[[OHLC-Datenanalyse (Workflow)]]"]
---

# Muster-Validierung (laufend)

**Generiert** von `algo/backtest_ohlc.py` aus allen Handelstagen in `raw/marktdaten/`. Prueft ICT-Behauptungen aus dem Wiki gegen die tatsaechlichen Daten, statt sie als gegeben zu uebernehmen. Wird bei jedem neuen Handelstag neu ausgefuehrt — siehe [[../algo/PLAN.md|Algo-Projekt]].

> ⚠️ **Nur 3 Handelstag(e) in der Datenbasis.** Jede Prozentzahl unten ist bei dieser Stichprobengroesse **statistisch nicht belastbar** — sie zeigt den aktuellen Stand, keine bestaetigte Regel. Als Faustwert gilt: unter ~20-30 Tagen kann jede Zahl durch einen einzigen ungewoehnlichen Tag komplett kippen. Diese Seite wird bei jedem neuen Tag automatisch aktualisiert; erst beobachten, ob sich die Werte stabilisieren, bevor daraus eine Handelsregel wird.

Datenbasis: 3 Handelstag(e) — 2026-07-31, 2026-08-03, 2026-08-04 (5m-Basis).

## Abdeckung (Nutzerwunsch: alle PD Arrays, das gesamte Wiki)

Diese Seite soll perspektivisch jede pruefbare Wiki-Behauptung gegen echte Daten testen. Stand jetzt automatisch pruefbar (Detektoren existieren in `tools/analyze_ohlc.py`):

- [[Fair Value Gap (FVG)]] (inkl. C.E-Fuellung), [[Volume Imbalance (VII)]], [[ORG (Opening Range Gap) & 1st Presented FVG]] (ueber FVG-Detektor), Liquidity Sweeps / [[Open Float & Liquidity Pools]], [[Market Structure Shift (MSS)]] / BOS-CHoCH / [[CISD (Change in State of Delivery)]] (als Struktur-Proxy), [[ICT Macros & Leading Candles]]-Expansion.

**Noch ohne eigenen Detektor** (Backlog in `algo/PLAN.md`, wird nach und nach ergaenzt statt in einem Schritt geraten): [[Order Block]] + Varianten ([[Breaker Block]], [[Rejection Block]], [[Mitigation Block]], [[Reclaimed Order Block]]), [[IFVG (Inverse Fair Value Gap)]], [[Balanced Price Range (BPR)]], [[Central Bank Dealers Range (CBDR)]], [[New Week Opening Gap (NWOG) Bias|NWOG/NDOG]], [[Optimal Trade Entry (OTE)]], [[Breakaway Gap]], [[Suspension Block]], [[Judas Swing]] als eigenes Zeitfenster (bislang nur ueber Sweeps sichtbar, nicht als benanntes Ereignis), [[Quarterly Shift]], [[SMT (Smart Money Divergence)]] (braucht ein zweites Symbol, bisher wird nur MNQ erfasst).

## Fair Value Gap / C.E-Fuellung

Testet die verbreitete ICT-Behauptung "das C.E eines FVG/ORG wird meist erreicht" (oft als ~70% zitiert) an den tatsaechlichen Daten. Zwei unterschiedliche Fragen, die in der Praxis oft vermischt werden:

| | Alle FVGs | Nur groessere FVGs (≥ Median-Kerzenrange des Tages) |
|---|---|---|
| Anzahl | 84 | 9 |
| C.E erreicht (Preis beruehrt die 50%-Linie) | 88% | 78% |
| Komplett gefuellt (ganze Luecke geschlossen) | 87% | 67% |

„C.E erreicht" und „komplett gefuellt" sind unterschiedliche Ereignisse — die 70%-Zahl, die kursiert, bezieht sich vermutlich auf ersteres. Diese Seite zaehlt beide getrennt, um genau diese Vermischung sichtbar zu machen. Siehe [[Fair Value Gap (FVG)]], [[ORG (Opening Range Gap) & 1st Presented FVG]].

## Volume Imbalance (VII)

346 VII (Close→Open-Luecke zwischen zwei Kerzen), 95% davon wieder komplett gefuellt. Siehe [[Volume Imbalance (VII)]].

## Liquidity Sweeps

25 Sweeps insgesamt, davon 56% mit sofortiger Rueckeroberung (`bars_back == 0`) — der Rest brauchte laenger, siehe `confirm`-Fenster in [[OHLC-Datenanalyse (Workflow)]].

## Market Structure Breaks (BOS/CHoCH → CISD)

39 Structure Breaks insgesamt: 24 BOS (Fortsetzung), 15 CHoCH (Richtungswechsel) — 38% der Breaks waren ein Richtungswechsel. Jeder Break ist ein potenzieller [[CISD (Change in State of Delivery)]]; siehe dort fuer die Bedingung (Imbalance muss enthalten sein), die dieser Zaehler noch nicht prueft.

## Macro-Fenster-Expansion

5 von 38 Macro-Fenstern (XX:50–XX+1:10) waren Expansion (>1,5x Tages-Median) = 13%. Bei 24 Fenstern/Tag waere ein Gleichverteilungs-Erwartungswert bei ~keinem besonderen Fenster — dass es ueberhaupt planbare Haeufungen gibt (z.B. [[NY Lunch Macro Model]]), ist erst ab mehr Tagen pruefbar.

## Pro Tag

| Tag | FVGs (groß) | C.E erreicht | Sweeps | BOS/CHoCH | Macro-Expansionen |
|---|---|---|---|---|---|
| 2026-07-31 | 6 | 67% | 9 | 12/7 | 4/18 |
| 2026-08-03 | 3 | 100% | 15 | 11/7 | 1/17 |
| 2026-08-04 | 0 | – | 1 | 1/1 | 0/3 |

## Verwandt

- [[OHLC-Datenanalyse (Workflow)]] — Detektoren, die diese Seite aggregiert
- [[Fair Value Gap (FVG)]], [[ORG (Opening Range Gap) & 1st Presented FVG]], [[CISD (Change in State of Delivery)]]
- `algo/PLAN.md` — Code-Idee 1 (Backtest-Harness), diese Seite ist die erste Version