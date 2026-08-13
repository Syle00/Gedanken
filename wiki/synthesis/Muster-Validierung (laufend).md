---
tags: [synthesis, trading-ict, marktdaten, backtest]
created: 2026-08-07
updated: 2026-08-12
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

## 1st Presented FVG — Wochenrelevanz des Montags (offene Hypothese, Stand 2026-08-11)

**Behauptung (Jannes, aus ICT):** 1.p FVGs sind besonders; insbesondere das 1.p FVG der
**Montags**-NY-AM-Session bleibt die **gesamte Handelswoche** relevant und wird respektiert.
Zugehoerige Definitionspraezisierung auf [[ORG (Opening Range Gap) & 1st Presented FVG]]: die
komplette 3-Kerzen-Formation muss in der Session liegen (frueheste Position 9:30/9:31/9:32) —
ein frueher gebildetes FVG bleibt ein **normales** FVG, es ist nur kein 1.p FVG.

Geprueft von `algo/backtest_1p_fvg_woche.py` (MNQ, NY AM 9:30–11:00).

| Test | 5m (2026-06-08..08-11) | 1m (2026-07-08..08-11) |
|---|---|---|
| (A) Touch am **Folgetag**, Mo vs. Di/Mi/Do | 56 % (5/9) vs. 50 % (11/22), p=1,00 | 75 % (3/4) vs. 43 % (6/14), p=0,58 |
| (B) Montags-FVG **irgendwann Di–Fr** beruehrt | 78 % (7/9), C.E. ebenso | 100 % (4/4) |
| (C) 1.p FVG vs. **uebrige** FVGs derselben Session | 52 % vs. 62 %, p=0,40 | 50 % vs. 63 %, p=0,32 |

**Stand: unentschieden, weder bestaetigt noch widerlegt.** Kein Test wird signifikant, und mit
9 bzw. 4 Montagen ist die Datenbasis fuer eine Aussage in beide Richtungen zu duenn.

Zwei Beobachtungen, die beim Nachladen von Daten weiterzuverfolgen sind:

- **Fuer die These:** Montags-FVGs liegen im Median **weiter vom Tagesschluss entfernt**
  (5m: 214 vs. 176 Pkt; 1m: 284 vs. 183 Pkt) und werden trotzdem mindestens gleich oft
  angelaufen. Bei gleicher Distanz waere die Rate also hoeher — genau das, was "wird
  respektiert" bedeuten wuerde.
- **Gegen eine naive Lesart von (C):** das 1.p FVG wird *seltener* beruehrt als spaetere FVGs
  derselben Session — aber es liegt auch deutlich weiter weg (1m: 197 vs. 135 Pkt), weil der
  Preis im Lauf der Session davonlaeuft. Der Unterschied ist damit plausibel durch die Distanz
  erklaert und **kein** Beleg gegen die Besonderheit.
- Nebenbefund ohne Bezug zur These: das 1.p FVG des **Donnerstags** wird am Freitag auffallend
  selten angelaufen (5m: 1/7). Eigene Pruefung wert, sobald mehr Wochen vorliegen.

Wiederholen, sobald mehr als ~20 Montage in 1m vorliegen.

## STD-Projektionen und die Tages-/Session-Extrema (offene Hypothese, Stand 2026-08-11)

**Behauptung (Jannes):** Mit den STD-Projektionen wird ein High/Low fixiert — entweder das
Session- oder das Daily-High/Low. Bezug: [[ORG (Opening Range Gap) & 1st Presented FVG]]
(Partial-Leiter −0,2/−0,5/−1,0 STD sowie die Opening-Range-STDs, die laut Quelle "die Ziele
des Tages" liefern).

Geprueft von `algo/backtest_org_std_extrema.py` gegen **beide** Basen (ORG-Gap und Opening
Range 9:30–10:00; bei letzterer nur Extrema ab 10:00, sonst zirkular).

| Basis | Extremum | 5m (42 Tage) | 1m (23 Tage) |
|---|---|---|---|
| ORG-Gap | Daily High / Low | 5 % / 12 % | 9 % / 13 % |
| ORG-Gap | AM High / Low | 10 % / 17 % | 17 % / 17 % |
| Opening Range | Daily High / Low (ab 10:00) | 14 % / 19 % | 13 % / **26 %** |
| Opening Range | AM High / Low (ab 10:00) | 21 % / 19 % | 22 % / 26 % |

**Zufallserwartung: 20 %** — die STD-Level stehen im Abstand 0,5 STD, ein ±5-%-Fenster deckt
damit bereits ein Fuenftel der Preisachse ab. Gemessen an dieser Baseline liegt **keine**
Kennzahl signifikant darueber (bestes p=0,305). Der Median-Abstand zum naechsten Level liegt
mit 0,10–0,20 STD ueberwiegend **ueber** dem Zufallswert 0,125 STD.

**Stand: nicht gestuetzt, aber nicht widerlegt** — 42 bzw. 23 Tage sind zu wenig. Sensitivitaet
gegen die Toleranzwahl geprueft (0,03/0,05/0,10), Bild unveraendert. Wiederholen bei
groesserem 1m-Bestand.

Datenpunkt 2026-08-11: Tagestief 29 533,50 lag zwischen −2,0 STD (29 554,75, erreicht) und
−2,5 STD (29 507,25, offen) — also nicht auf einem Level.

### Nachtrag 2026-08-11: beide STD-Basen bleiben offen

Zur Begriffsklaerung: das **ORG** ist der Closing Price des Vortags um **16:14** zum **9:30**-Opening Price; "NY AM" benennt nur, welches ORG gemeint ist (gegen PM 13:30–14:00, London, Midnight). Davon zu unterscheiden ist die **Opening Range** 9:30–10:00. Beide tragen im Wiki STD-Projektionen, beide bleiben in Pruefung.

Als eigenstaendiger Datenpunkt vom 11.08. bemerkenswert ist die **Opening-Range**-Projektion:

| | |
|---|---|
| OR 9:30–10:00 | High 29 842,75 (09:30) / Low 29 636,00 (09:47), Range 206,75 Pkt |
| −0,5 STD | 29 532,62 |
| Tagestief ab 10:00 | 29 533,50 |
| **Abweichung** | **0,88 Pkt (3,5 Ticks)** |

Aus dem **ORG-Gap** projiziert lag dasselbe Tief zwischen −2,0 und −2,5 STD, also auf keinem
Level. Das ist kein Argument gegen eine der beiden Basen — es zeigt nur, dass sie sich am
selben Tag unterschiedlich verhalten und getrennt gefuehrt werden muessen. Passt zum
Backtest, wo `or_:post_daily_low` (26 %, 1m) der beste aller acht Werte war.

### Nachtrag 2026-08-12: Daily-Bias-Notiz — ORG-C.E.-70%-These live angewendet (vor RTH-Open)

Jannes' Tagesnotiz (`raw/daily bias 12.08.md`) wendet die offene ORG-C.E.-70%-These (siehe
Abschnitt „Fair Value Gap / C.E-Fuellung" oben, aktuell 35–43 % statt der behaupteten 70 %)
live an: CPI-News um 8:30 NY (14:30 CEST) als Volatilitaetstreiber, Buyside noch nicht
genommen (Ziel), Premium Wick vom 05.08. knapp unterhalb der Buyside noch offen, Discount
Wick vom 06.08. unberuehrt (bullish bestaetigend). Vortagsschluss (16:14 NY) 29 640,25,
`algo/live_status.py`-Check (frisch gezogen, 12 Min. Lag, im tolerierten Bereich) bestaetigt
Jannes' Beobachtung: 29 800,00 um 05:00 NY (11:00 CEST) — der eigentliche ORG-Wert steht aber
erst mit dem 9:30-NY-Open fest (`org_ce` in `live_status.py` liefert vor RTH-Open `null`).

Jannes' Erwartung: bei einem **sehr grossen** ORG-Gap greift die 70%-Regel *nicht* (C.E. wird
**nicht** innerhalb 30 Min. gefuellt) — das waere eine Praezisierung der bestehenden
Hypothese, keine neue: falls grosse Gaps seltener fuellen, erklaert das teilweise, warum die
Gesamtquote (35–43 %) unter dem behaupteten 70 % liegt. **Backlog-Idee:** `org_gap()`-Ergebnisse
nach Gap-Groesse (z. B. Quartile) segmentieren, um "grosser Gap → seltener C.E.-Fill"
statistisch zu pruefen, statt die Quote nur pauschal auszuweisen — in `algo/PLAN.md` vermerkt.

Weekly DOL (Jannes' Ziel fuer die Woche, nicht zwingend heute): Buyside **30 094,00**. Status
offen, wird nach RTH-Open per `algo/live_status.py`/`algo/backtest_org_ce.py` nachgeprueft.

Vorbehalt: Tag lief beim Erfassen noch (Daten bis 14:39 NY).

## 1st Presented Displacement — Respekt über die Daily Range (laufend)

**These** (2026-08-13, siehe [[Midnight Opening Range]]: „wird nach rechts ausgezogen und über den
gesamten Tag mitgeführt"): Das 1st presented Displacement (größtes FVG im 0:00–0:30-MOR-Fenster)
wird über den restlichen Tag als Referenz respektiert — Preis läuft an dessen C.E. zurück und
reagiert dort. Backtest: `algo/backtest_1p_daily_respect.py`, n=25 Tage (Juli–Aug 2026, MNQ 1m,
kein Lookahead: 1.p nur aus 0:00–0:30, Tracking erst danach bis 16:00 NY).

| Kennzahl | Ergebnis |
|---|---|
| Zone später berührt | **25/25 (100 %)** |
| C.E. später berührt | **25/25 (100 %)** |
| FVG hält (kein Bruch der fernen Grenze in 15 Min) | **1/25 (4 %)** |
| Median-Reaktion am C.E. vor dem Bruch | **10,0 Pkt** |
| Reaktion ≥ 10 Pkt vor dem Bruch | **13/25 (52 %)** |

**Befund (ehrlich):** Als **Draw/Referenz bestätigt** — der 1.p wird ausnahmslos wieder angelaufen
(100 % Zone + C.E.), das stützt „Magnet / über den Tag mitgeführt". Als **haltendes Level
widerlegt** — das kleine FVG (Median ~7–9 Pkt) wird an 96 % der Tage durchgehandelt. Reaktion nur
mäßig (Median 10 Pkt, ≥10 Pkt auf 52 % — Münzwurf).

> ⚠️ **Kein Kontroll-Baseline.** 100 % Berührung ist wenig aussagekräftig, weil das FVG nahe am
> Eröffnungspreis liegt und Preis diese Zone ohnehin wieder besucht — ein **beliebiges** Level nahe
> dem Open würde vermutlich ähnlich oft berührt. Um zu zeigen, dass der 1.p *spezifisch* respektiert
> wird, fehlt der Vergleich gegen (a) zufällige Level nahe Open und (b) Nicht-1.p-FVGs. Offen, plus
> n=25 klein. Bis dahin: **Referenz ja, handelbares Hold nein.**
