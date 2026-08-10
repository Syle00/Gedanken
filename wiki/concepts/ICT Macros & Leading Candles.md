---
tags: [concept, ict, trading-ict, 2026]
created: 2026-08-01
updated: 2026-08-10
backtest: algo/backtest_macro.py
sources: ["[[From Vision To Execution (Source)]]", "[[2026-07-31 - Market Review NQ July 31, 2026 (Source)|Market Review NQ July 31, 2026 (Source)]]", "[[2026-08-07 - Case Study With NonFarm Payroll & NQ Futures (Source)|Case Study With NonFarm Payroll & NQ Futures (Source)]]"]
---

# ICT Macros & Leading Candles

Zu bestimmten Uhrzeiten innerhalb der Handelssession ("Macros", Beispiel aus der Quelle:
**9:50–10:10**) achtet ICT gezielt auf **Leading Candlesticks** — Candles, die sich durch
ungewöhnliche Größe auszeichnen und sich genau zur "richtigen" Zeit gebildet haben. Diese gelten
als besonders aussagekräftig für die weitere Preisrichtung.

![[image 3.png]]
*Leading Candlesticks innerhalb der Macro-Zeit 9:50–10:10.*

## Zusatzregeln (aus derselben Quelle)

- **Overnight-Liquidity**: es wird **immer** davon ausgegangen, dass sie genommen wird, außer Preis
  zeigt eindeutig etwas anderes. Bilden sich Equal Highs/Lows über Nacht, ist das der erste
  [[AMD Cycle (Accumulation – Manipulation – Distribution)|DOL]] für die (NQ-)Session.
- **Schwaches FVG**: sehr klein **und** ohne genommene Liquidity dahinter = ein gewöhnliches Gap,
  keine belastbare PD Array.

  ![[image 4.png]]
  *Nicht starkes FVG: sehr klein und ohne genommene Liquidity — für ICT nur ein gewöhnliches Gap.*
- Ein FVG mit **Purge** (vorheriger Liquidity-Sweep) innerhalb der [[IPDA Data Ranges]] gilt als
  besonders starke PD Array.

## 8:30 als algorithmischer Fixzeitpunkt (2026-Ergänzung)

Unabhängig vom regulären 20-Minuten-Macro-Raster (xx:50–x0:10) ist **8:30 Uhr NY** ein feststehender
News-Release-Zeitpunkt (z.B. viele US-Konjunkturdaten) und dadurch verlässlich volatil — auch ohne
dass ein Macro-Fenster dort offiziell benannt ist. Quelle: [[2026-07-31 - Market Review NQ July 31, 2026 (Source)|Market Review NQ July 31, 2026 (Source)]].

## Macro-Zeit als Reversal-Check nach News-Expansion (2026-Ergänzung)

Aus [[2026-08-07 - Case Study With NonFarm Payroll & NQ Futures (Source)|Case Study With NonFarm
Payroll & NQ Futures (Source)]]: an einem NFP-Freitag rallyt Preis nach dem 8:30-Print bis in die
Macro-Zeit **8:50–9:10** hinein. Diese Macro-Zeit dient hier nicht als Entry-Trigger, sondern als
**Prüfpunkt für eine bereits laufende Position** — läuft eine Long-Position mit deutlicher
Stage-1-Expansion (siehe [[Two Stage News Delivery (FOMC & NFP)]]) genau in eine Macro-Zeit hinein,
ist das der Moment, Teilgewinne zu sichern, bevor ein Reversal einsetzt. Bestätigt zusätzlich per
Standard-Deviation-Projektion der Pre-News-Range (siehe [[Central Bank Dealers Range (CBDR)]]).

## Anzeichen einer aktiven Macro-Phase: "Spooling"/Energie-Aufbau (2026, offene Hypothese)

Nutzerbeobachtung (laufend, noch nicht gegen Daten geprüft): Am **Start eines Macro-Fensters**
(konkreter Anlass: **10:50**, Beginn des [[NY Lunch Macro Model|Lunch Macros]]) baut Preis
sichtbar **Kraft/Energie auf**, bevor der eigentliche Move einsetzt — im Chart als "Spooling"
beschrieben. Noch offen, wie sich das konkret operationalisieren lässt (Kandidaten: engere
Candle-Ranges mit steigendem Volumen direkt vor dem Fenster, mehrere kleine Same-Direction-Closes
in Folge, sinkende Wick-Anteile). Bis zur Präzisierung als **offene Hypothese** behandelt, nicht
als bestätigte Regel — bei mehr Beispielen/Daten hier ergänzen und in `algo/PLAN.md` backtesten.

### Erstes Beispiel (2026-08-10, MNQ 1min) — nach Datenprüfung korrigiert

Vom Nutzer per Chart-Screenshot geliefert (TradingView, MNQU2026, 1min, Montag 2026-08-10,
09:30–12:30 NY). Die ursprüngliche Lesart aus dem Chart war, Preis verbringe die **gesamte**
10:50–11:10-Macro-Zeit komprimiert in der Zone um 29.790–29.810 und expandiere erst danach. Die
Gegenprüfung an den 1m-Daten widerlegt das: 10:50–11:10 war der **stärkste gerichtete Block des
ganzen Tages** — Open 29.870,25 → Close 29.783,00, also **−87,25 Punkte netto bei 106,50 Punkten
Range (dir 0,82)**. Die Kompression lag **nach** dem Macro, nämlich 11:10–11:50 (netto −5,00 bei
64,00 Range, dir 0,08; danach +18,50 bei 77,25, dir 0,24), und die Auflösung nach oben Richtung
NWOG 33 (29.841,00 / 29.851,50) fiel wiederum in das **nächste** Macro 11:50–12:10 (+30,25, dir
0,46).

Das ändert die Deutung: nicht "Spooling *im* Macro, Expansion danach", sondern **Expansion im
Macro, Spooling zwischen zwei Macros**. Das Auge hatte die Fensterlage um ~20 Minuten verschoben
— derselbe Fehlertyp wie beim 1m-Vakuum am selben Tag ([[Statistische Muster jenseits der ICT-Konzepte (laufend)]],
Punkt 7). Die Spooling-Hypothese als solche ist damit nicht erledigt, aber sie beschreibt die
**Zwischenphase**, nicht den Macro-Start.

### Zweites Beispiel: Macro 09:50–10:10 (2026-08-10, MNQ 1min/5min)

![[MNQ 2026-08-10 - 09-50 Macro.png]]
*MNQU2026 1min (links) / 5min (rechts), 2026-08-10: das Macro 09:50–10:10 gelb markiert, darunter
die NDOG-Level 29.819,50 / 29.781,25 und NWOG 33 bei 29.841,00 / 29.851,50.*

Ablauf laut 1m-Daten: das Fenster öffnet bei 29.817,75 (direkt am NDOG-05.08-Level 29.819,50),
läuft zuerst **gegen** die spätere Richtung bis 29.754,25 herunter und schließt bei 29.874,50 —
**+56,75 Punkte netto bei 122,00 Range (dir 0,47)**, Hoch am Fensterende. Klassische
Manipulation-vor-Expansion-Sequenz innerhalb der 20 Minuten
([[AMD Cycle (Accumulation – Manipulation – Distribution)]]).

Der Kontrast zu den Nachbarblöcken desselben Tages ist deutlicher als die Range vermuten lässt:

| Block | Range | Netto | dir |
|---|---|---|---|
| 09:30–09:50 (RTH-Open) | 122,25 | +12,25 | 0,10 |
| **09:50–10:10 (Macro)** | **122,00** | **+56,75** | **0,47** |
| 10:10–10:30 | 98,75 | −17,00 | 0,17 |
| 10:30–10:50 | 54,25 | +12,00 | 0,22 |
| **10:50–11:10 (Macro)** | **106,50** | **−87,25** | **0,82** |

Der Open-Block 09:30–09:50 hatte praktisch dieselbe Range, aber nur ein Fünftel des Nettowegs —
viel Bewegung, kein Fortschritt. **Nicht die Range unterscheidet Macro von Nicht-Macro, sondern
wie gerade sie durchlaufen wird.** Alle fünf Macros des Tages lagen bei dir ≥ 0,27, vier von fünf
bei ≥ 0,46; die Kontrollblöcke der gleichen Stunden bei 0,06 / 0,10 / 0,17 / 0,08 / 0,24.

## Backtest: sind die Macro-Fenster messbar anders? (2026-08-10)

`algo/backtest_macro.py` zerlegt jeden Handelstag in 72 lückenlose 20-Minuten-Blöcke — pro Stunde
genau drei: `:50–:10` (Macro), `:10–:30` und `:30–:50` (Kontrolle). Die Kontrollen liegen damit
unmittelbar neben dem Macro, was den Tageszeit-Confounder ausschaltet (sonst gewänne 09:50–10:10
allein deshalb, weil nach dem RTH-Open ohnehin die meiste Bewegung liegt).

Basis: MNQ, 23 Handelstage 1min (2026-07-08 … 2026-08-07), 1091 auswertbare Blöcke.

> ⚠️ **Alle Zahlen dieses Abschnitts decken nur einen verkürzten Handelstag ab (2026-08-10).**
> `blocks()` in `algo/backtest_macro.py` startet bei **00:10 des Kalendertags**. Der MNQ-Handelstag
> beginnt aber um **18:00 des Vorabends** (die 1m-Exporte enthalten ihn korrekt: `MNQ 2026-07-09
> 1m.csv` reicht von 2026-07-08 18:00 bis 2026-07-09 17:00). Dadurch fallen die Blöcke von 18:00
> bis 24:00 heraus — **6 der 23 Macro-Fenster**, also die gesamte Abend- und frühe Asia-Session.
> Betroffen: die Blockzahlen (351 / 740 / 1091), die drei p-Werte und die Median-Rang-Aussage
> ("3 von 49 Blöcken" — bei vollem Handelstag sind es 69 Blöcke, nicht 72, da 17:50 in der
> Globex-Pause liegt). Die *Richtung* des Befunds (Macros liefern gerichtetere, nicht größere
> Bewegung) ist davon unberührt, die *Zahlen* sind nach dem Fix neu zu erzeugen.
> Details: `docs/superpowers/specs/2026-08-10-macro-datenbank-design.md` §9.2.

**Datenqualität, am 2026-08-10 gemessen** (gilt für alle Auswertungen auf diesem Bestand):

- **Kein Volumen.** Die TradingView-1m-Exporte enthalten nur `time,open,high,low,close`. Jede
  volumenbasierte Kennzahl ist auf diesem Bestand unmöglich — das trifft insbesondere die
  naheliegende Spooling-Definition "enge Kerzen bei steigendem Volumen" (siehe Abschnitt oben).
- **Systematische Exportlücke am Datumswechsel.** An 15 von 19 vollen Tagen fehlen die Minuten
  **23:59–00:08**. Immer dieselben zehn Minuten. MNQ handelt dort durchgehend (Asia-Session läuft),
  zehn tickfreie Minuten sind praktisch ausgeschlossen — das ist ein TradingView-Exportartefakt,
  kein Marktverhalten. Es macht genau das Macro-Fenster **23:50–00:10** unbrauchbar (nur 1 von 23
  Tagen vollständig). Schließbar über `algo/fetch_yfinance.py` (MNQ=F, 1m, ~30 Tage rückwärts).
- **Vier Fragmenttage** im Bestand: 2026-07-08, 08-03 (nur 11:19–16:18), 08-05, 08-07.
- **16:50–17:10** ist grundsätzlich unvollständig — das Fenster ragt über den Sessionschluss 17:00
  hinaus und existiert nur zur Hälfte.

| | n | median Range | median Netto | median dir |
|---|---|---|---|---|
| Macro (`:50–:10`) | 351 | 63,50 | **31,50** | **0,52** |
| Kontrolle | 740 | 58,25 | 23,88 | 0,46 |

Mann-Whitney einseitig (Macro > Kontrolle): Range p = 0,0028, Netto p < 0,0001, dir p = 0,0003.

**Befund**: Die Macro-Fenster sind real, aber der Effekt liegt woanders als erwartet. Die Range
ist nur **+9 %** größer — der Nettoweg dagegen **+32 %** und die Geradlinigkeit systematisch
höher. Macros produzieren also nicht mehr Volatilität, sondern **gerichtetere** Volatilität. Das
passt zu ICTs Formulierung ("Leading Candles"), widerspricht aber der landläufigen Lesart "im
Macro ist am meisten los".

**Gegen die These**: 09:50–10:10 ist **nicht** das größte Fenster des Tages. Über 22 Tage liegt
sein Median-Rang bei 3 von 49 Blöcken — geschlagen von 09:30–09:50 (Median-Rang 2, Median-Range
199,12 gegen 152,38). Der RTH-Open ist der Expansionsblock, das Macro der Anschlussblock. Wer
09:50 auf "jetzt kommt der große Move" wartet, hat den größeren Move meist schon verpasst; was
das Macro liefert, ist die **saubere** Bewegung.

Vorbehalt: 23 Tage sind wenig, und Blöcke desselben Tages sind nicht unabhängig — der p-Wert ist
dadurch optimistisch. Mit wachsendem Datenbestand nachziehen.

### Entstehen FVGs bevorzugt im Macro? Ja — aber erst die großen (2026-08-10)

Anlass: Nutzeraussage am 2026-08-10 zum SB FVG (SIBI) um 14:12 — *"genau das will ich
optimalerweise im Macro sehen"*. Testbarer Kern davon: häufen sich 1m-[[Fair Value Gap (FVG)|FVGs]]
in den Macro-Fenstern? `algo/backtest_macro.py --min-fvg <n>` zählt sie je Block:

| Mindestgröße | Macro | Kontrolle | Vorsprung | Blöcke **ohne** FVG (Macro / Kontrolle) | p |
|---|---|---|---|---|---|
| ≥ 2 Pkt | 2,82 | 2,59 | +9 % | 4 % / 7 % | 0,0034 |
| ≥ 5 Pkt | 1,71 | 1,51 | +13 % | 17 % / 26 % | 0,0035 |
| **≥ 10 Pkt** | **0,79** | **0,62** | **+27 %** | **47 % / 60 %** | **0,0001** |
| ≥ 15 Pkt | 0,36 | 0,30 | +20 % | 74 % / 79 % | 0,0225 |

**Je größer das FVG, desto stärker sitzt es im Macro.** Und daraus folgt die praktisch wichtigere
Hälfte: *"ein FVG im Macro"* ist als Filter wertlos — **96 % aller Macro-Fenster enthalten
mindestens ein FVG ≥ 2 Punkte**, im Schnitt fast drei pro 20 Minuten. Wer darauf wartet, wartet
auf etwas, das praktisch immer passiert. Erst ab ~10 Punkten wird das FVG selten genug, um zu
selektieren: dann hat es nur noch gut jedes zweite Macro (53 %) gegen 40 % der Kontrollblöcke.

Das passt zum Hauptbefund oben: der Macro-Vorteil steckt in der **Größe und Geradlinigkeit** der
Bewegung, nicht in der bloßen Existenz einer Ineffizienz.

## Chart-Konvention (Nutzer)

In Jannes' TradingView-Charts markiert ein **lila/violettes FVG-Rechteck immer ein
Silver-Bullet-FVG** ([[Silver Bullet Model]]) — nie ein beliebiges FVG. Andere Farben sind nicht
festgelegt; lila **Linien** sind dagegen NWOG-Level, blau gestrichelt NDOG, grün Liquidity-Level.

![[MNQ 2026-08-10 - 10-50 Macro Spooling.png]]
*MNQU2026 1min, 2026-08-10: Spooling in der 10:50–11:10-Macro-Zeit (gelb markiert) knapp über der
NDOG-Zone, danach Expansion Richtung NWOG 33.*

## Verwandt

- [[AMD Cycle (Accumulation – Manipulation – Distribution)]]
- [[NY Lunch Macro Model]] — konkretes Setup rund um das 10:50-Macro
- [[Fair Value Gap (FVG)]], [[IPDA Data Ranges]]
- [[Modell 22]] — Displacement nach [[Turtle Soup]] muss laut Quelle konsequent in die Zukunft
  ausgemalt werden, relevant für spätere Price-Runs (reclaimed FVG oder IFVG).
- [[Two Stage News Delivery (FOMC & NFP)]], [[Central Bank Dealers Range (CBDR)]]
- [[2026-08-07 - Case Study With NonFarm Payroll & NQ Futures (Source)|Case Study With NonFarm Payroll & NQ Futures (Source)]]
