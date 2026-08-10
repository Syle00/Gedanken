---
tags: [concept, ict, trading-ict, 2026]
created: 2026-08-01
updated: 2026-08-10
backtest: algo/backtest_macro.py
sources: ["[[From Vision To Execution (Source)]]", "[[2026-07-31 - Market Review NQ July 31, 2026 (Source)|Market Review NQ July 31, 2026 (Source)]]", "[[2026-08-07 - Case Study With NonFarm Payroll & NQ Futures (Source)|Case Study With NonFarm Payroll & NQ Futures (Source)]]", "[[ICT Gems - The Functions of a Macro (Source)]]", "[[ICT Gems - How Price Behaves At Specific Times (Source)]]", "[[ICT Gems - When To Anticipate Price Spooling (Source)]]", "[[ICT Gems - How to Trade the Final Hour Macro (Source)]]", "[[ICT Gems - Blending Silver Bullets and Macros (Source)]]", "[[ICT Gems - ICT Teaches how to Scalp Every 1 Hour Candle (Source)]]"]
---

# ICT Macros & Leading Candles

Zu bestimmten Uhrzeiten innerhalb der Handelssession ("Macros", Beispiel aus der Quelle:
**9:50–10:10**) achtet ICT gezielt auf **Leading Candlesticks** — Candles, die sich durch
ungewöhnliche Größe auszeichnen und sich genau zur "richtigen" Zeit gebildet haben. Diese gelten
als besonders aussagekräftig für die weitere Preisrichtung.

![[image 3.png]]
*Leading Candlesticks innerhalb der Macro-Zeit 9:50–10:10.*

## Was ein Macro *ist* — ICTs eigene Funktionsdefinition (2024)

Bis hierher beschreibt die Seite Macros über ihre **Uhrzeiten**. Aus
[[ICT Gems - The Functions of a Macro (Source)]] stammt die Definition über ihre **Funktion**:

> *"A macro is knowing where the market's likely draw to next with liquidity, and the time."*
> — und zur Wirkung: *"**They roll against who's in the money right now.** That's what their
> function is."*

Zwei Konsequenzen, die das Bild auf dieser Seite schärfen:

- **Ein Macro ist kein Volatilitätsfenster, sondern ein Umverteilungsfenster.** Es richtet sich
  gegen die Positionen, die *gerade* im Gewinn liegen. Das erklärt den eigenen Backtest-Befund
  weiter unten deutlich besser als "mehr Bewegung": Macros liefern nicht mehr Range, sondern mehr
  **Nettoweg** — sie räumen eine Seite ab.
- **Richtung ≠ Bias.** ICT trennt beides ausdrücklich: Gesucht wird nicht "bullish oder bearish",
  sondern *"where's the next draw on liquidity"*. Wer Tageszeit und Macro-Fenster beherrscht, kann
  laut ICT **ohne** Intraday-Bias allein auf interne Liquidität handeln.

> *"In a 20 minute span you know that there's going to be a setup — you could set your watch to
> it."*

## Warum es das 15:00-Macro gibt: der Bond-Close

Dieselbe Quelle nennt für das 14:50–15:10-Fenster eine **konkrete Ursache** statt nur einer
Uhrzeit: Um **15:00 NY schließt der Anleihemarkt**, und dieser Close wirkt auf die Aktienindizes.
Die Wirkung ist nicht einheitlich — ICT nennt drei mögliche Ausgänge: **Continuation**,
**Reversal** oder **Retracement mit anschließender Continuation**.

Damit gibt es auf dieser Seite jetzt zwei zeitlich fixierte, ursächlich erklärbare Punkte
außerhalb des reinen 20-Minuten-Rasters: **8:30** (News-Release, siehe unten) und **15:00**
(Bond-Close). Vgl. [[ICT Daily Range Session Timing]], wo der 15:00-Bond-Close bereits als
Einflussfaktor auf Währungen vermerkt ist — hier dieselbe Ursache für Indizes.

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

## "Spooling" — ICTs Definition (2024) ✅ Hypothese aufgelöst

> ✅ **Diese Frage war seit 2026-08-10 als offene Hypothese markiert und ist jetzt geklärt** — mit
> dem Ergebnis, dass die ursprüngliche Vermutung **den Begriff falsch herum** verstanden hatte.
> Quellen: [[ICT Gems - How Price Behaves At Specific Times (Source)]] und
> [[ICT Gems - When To Anticipate Price Spooling (Source)]].

**Die ursprüngliche Lesart war**: Preis baue am Macro-Start "Kraft/Energie" auf (Kompression),
bevor der Move einsetzt. **ICT meint mit Spooling das Gegenteil — die Bewegung selbst:**

> *"The market will spool — it means it **jumps and runs** to one of two things."*

Spooling ist der **gerichtete Lauf zum Ziel**, nicht die Ruhe davor. Konkret läuft Preis im
Macro-Fenster zu genau einem von drei Dingen:

1. Zu einem **Short-Term Low** → Sellside-Liquidität / Sell-Stops.
2. Zu einem **Short-Term High** → Buyside-Liquidität / Buy-Stops.
3. In eine **Ineffizienz** (FVG) — um Smart Money einen Einstieg zu Fair Value anzubieten,
   **unmittelbar bevor** Preis dann zur Liquidität spoolt.

Punkt 3 ist die eigentliche Feinheit: Der Lauf ins FVG ist die *Vorbereitung*, der Lauf zur
Liquidität ist das Spooling.

### Was das für die eigenen Daten bedeutet

Die Auflösung passt zum eigenen Backtest weiter unten, und zwar besser als die alte Lesart: Wenn
Spooling der gerichtete Lauf ist, dann ist die gemessene **erhöhte Geradlinigkeit (`dir`) im
Macro genau das Spooling** — und nicht ein Nebenbefund. Die im Beispiel 2026-08-10 beobachtete
Kompression *zwischen* zwei Macros ist reale Preisaktion, aber sie ist **nicht** das, was ICT
Spooling nennt; sie ist schlicht Konsolidierung.

Praktische Konsequenz: Die in `algo/PLAN.md` notierte Suche nach einer volumenbasierten
Spooling-Definition ("enge Kerzen bei steigendem Volumen") zielte am Begriff vorbei — und wäre auf
diesem Datenbestand ohnehin unmöglich gewesen (kein Volumen in den Exporten, siehe Datenqualität
unten). Die messbare Größe ist stattdessen der bereits erhobene **Nettoweg/`dir`**.

## ⚠️ Der Move *beginnt* im Macro — er läuft nicht darin ab

Die für den eigenen Backtest folgenreichste Aussage des ganzen Batches, aus
[[ICT Gems - Blending Silver Bullets and Macros (Source)]]. ICT korrigiert dort ausdrücklich eine
verbreitete Fehllesart seiner eigenen Lehre:

> *"There's people out there trying to teach my stuff and they're saying the move happens between
> 9:50 and 10:10 — **you're already doing it wrong**. The move **begins** in those 20 minutes.
> It's not the entirety of the move."*

Ein Macro ist also ein **Startfenster**, kein Container. In einem schnellen Markt kann die
Bewegung innerhalb der 20 Minuten fertig sein; der Normalfall ist, dass sie dort **anfängt** und
darüber hinausläuft.

**Konsequenz für `algo/backtest_macro.py`**: Das Skript misst Range, Nettoweg und `dir` **innerhalb**
des 20-Minuten-Blocks. Nach ICTs Definition unterschätzt das den Effekt systematisch — ein Macro,
das um 10:05 einen Lauf startet, der bis 10:40 trägt, wird als schwacher Block gewertet. Die
passendere Kennzahl wäre die **Exkursion ab Macro-Start über die folgenden N Minuten**
(MFE/MAE-artig), nicht der Blockinhalt. Als Auftrag in `algo/PLAN.md` notiert.

Das erklärt außerdem den bisherigen "Befund gegen die These" weiter unten: Dass 09:50–10:10 nicht
das größte Fenster des Tages ist, ist nach dieser Lesart **kein Widerspruch** — der RTH-Open
liefert die Range, das Macro liefert den **Startschuss** für den gerichteten Anschlusslauf. Genau
das deckt sich mit der gemessenen höheren Geradlinigkeit.

## Jede Stunde hat ein Macro

> *"Every hour a macro is in operation, every single hour."* — 10 Minuten vor bis 10 Minuten nach
> der vollen Stunde, also das `:50–:10`-Fenster. *"Some macros are better than others, I'll leave
> that for the book."*

Das bestätigt unabhängig das Raster, auf dem `algo/backtest_macro.py` bereits aufsetzt (drei
20-Minuten-Blöcke pro Stunde, davon einer Macro). ICT nennt das Macro-Fenster einen
*"supercharger for efficiency and immediate responsiveness in your entries"*.

Noch kategorischer in [[ICT Gems - ICT Teaches how to Scalp Every 1 Hour Candle (Source)]] — und
damit als Abgrenzung gegen frei erfundene Zwischenfenster brauchbar:

> *"There is **no 19-minutes-after-the-hour macro**, there's **no 23-minutes-after-the-hour
> macro**. A macro only exists 10 minutes before the top of the hour [bis 10 danach]."*

**Definition eines Macros**, ebenfalls wörtlich (aus
[[ICT Gems - How to Trade the Final Hour Macro (Source)]]): *"a macro is a short little list of
instructions or directives for an algorithm to run, and they tend to repeat."*

**Auch in der London-Session**: [[ICT Gems - London Opening Range + Macros (Source)]] nennt
ausdrücklich **1:50–2:10** (das erste Macro beim Eintritt in die London Killzone) und
**3:50–4:10** — das Raster gilt also nicht nur in der NY-Session. Als "Sweetspot" der London
Killzone nennt ICT dort **2:00–4:00 NY**, womit beide Macros hineinfallen.

**Mindestziel**: Für NASDAQ-Scalps nennt ICT **10 Handles** als Untergrenze — *"if I can't at least
make 10 handles, I'm not willing to take the trade"*, und ausdrücklich ohne Anspruch auf das
tiefste Tief oder höchste Hoch. Für den [[Silver Bullet Model|Silver Bullet]] speziell nennt er
dagegen 5 Handles.

> ⚠️ **Ausnahme letzte Handelsstunde**: Dort gilt das `:50–:10`-Raster laut
> [[ICT Gems - When To Anticipate Price Spooling (Source)]] **nicht** — siehe
> [[Market on Close (MOC) Macro Model]]. Für `algo/backtest_macro.py` ist das relevant, weil das
> Skript aktuell durchgehend gleichmäßig rastert.

## Wonach ein Macro greift: Gap **oder** Order Block **oder** Short-Term Low

Im Macro-Fenster sucht der Algorithmus laut ICT genau eines von drei Elementen — und die Auswahl
ist erzwungen, nicht beliebig:

- Liegt eine **Ineffizienz** vor → sie ist das Ziel (Entry per
  [[Institutional Order Flow Entry Drill (IOFED)]]).
- Liegt **keine** vor (Kerzen überlappen lückenlos) → der **[[Order Block]]** übernimmt: die
  Down-Close-Kerze, die Preis im Retracement abstößt.
- Sonst das **Short-Term Low/High** als Liquiditätsziel.

> **Strukturregel**: *"You're not going to get a short-term low, an order block and a fair value
> gap [in the same place] — it's physically impossible. Two at best, but never all three. Usually
> one or the other, at least one of the three."*

Das ist praktisch nützlich als Ausschlussverfahren: Wer im Macro-Fenster kein FVG findet, sucht
nicht weiter nach einem — er wechselt zum Order Block.

## Immer relevante Daily-Level

Unabhängig vom Intraday-Bild nennt ICT diese Level als dauerhaft mitzuführen — sie liefern die
HTF-Prämisse, ohne die ein 1-Minuten-Setup laut ihm wertlos ist:

- **PDH/PDL**, dazu die Highs/Lows der **letzten drei Tage**
- **Wochen-High/-Low** der Vorwoche
- von dieser Range jeweils **oberer Quadrant, Mittelpunkt und unterer Quadrant**

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

`algo/backtest_macro.py` zerlegt jeden Handelstag in 69 lückenlose 20-Minuten-Blöcke — pro Stunde
genau drei: `:50–:10` (Macro), `:10–:30` und `:30–:50` (Kontrolle). Die Kontrollen liegen damit
unmittelbar neben dem Macro, was den Tageszeit-Confounder ausschaltet (sonst gewänne 09:50–10:10
allein deshalb, weil nach dem RTH-Open ohnehin die meiste Bewegung liegt).

Basis: MNQ, 23 Handelstage 1min (2026-07-08 … 2026-08-07), 1417 auswertbare Blöcke.

> ✅ **Zahlen erneuert am 2026-08-10 nach dem `blocks()`-Fix.** Die Funktion startete zuvor bei
> 00:10 des Kalendertags statt bei 18:00 des Vorabends und verlor dadurch 6 der 23 Macro-Fenster
> (Abend- und frühe Asia-Session). Der Befund wurde durch den Fix **bestätigt und leicht
> verstärkt**, nicht gekippt: Netto-Vorsprung 26 % statt 32 %, dafür alle p-Werte besser und der
> FVG-Größeneffekt deutlicher (siehe unten). Alte Zahlen: 1091 Blöcke, 351/740.
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
| Macro (`:50–:10`) | 450 | 63,38 | **30,88** | **0,51** |
| Kontrolle | 967 | 57,75 | 24,50 | 0,46 |

Mann-Whitney einseitig (Macro > Kontrolle): Range p = 0,0004, Netto p = 0,0001, dir p = 0,0026.

**Befund**: Die Macro-Fenster sind real, aber der Effekt liegt woanders als erwartet. Die Range
ist nur **+10 %** größer — der Nettoweg dagegen **+26 %** und die Geradlinigkeit systematisch
höher. Macros produzieren also nicht mehr Volatilität, sondern **gerichtetere** Volatilität. Das
passt zu ICTs Formulierung ("Leading Candles"), widerspricht aber der landläufigen Lesart "im
Macro ist am meisten los".

**Gegen die These**: 09:50–10:10 ist **nicht** das größte Fenster des Tages. Über 22 Tage liegt
sein Median-Rang bei 3 von 67 Blöcken — geschlagen von 09:30–09:50 (Median-Rang 2, Median-Range
199,12 gegen 152,38). Der RTH-Open ist der Expansionsblock, das Macro der Anschlussblock. Wer
09:50 auf "jetzt kommt der große Move" wartet, hat den größeren Move meist schon verpasst; was
das Macro liefert, ist die **saubere** Bewegung.

Vorbehalt: 23 Tage sind wenig, und Blöcke desselben Tages sind nicht unabhängig — der p-Wert ist
dadurch optimistisch. Mit wachsendem Datenbestand nachziehen.

### Entstehen FVGs bevorzugt im Macro? Ja — aber erst die großen (2026-08-10)

Anlass: Nutzeraussage am 2026-08-10 zum SB FVG (SIBI) um 14:12 — *"genau das will ich
optimalerweise im Macro sehen"*. Testbarer Kern davon: häufen sich 1m-[[Fair Value Gap (FVG)|FVGs]]
in den Macro-Fenstern? `algo/backtest_macro.py --min-fvg <n>` zählt sie je Block:

| Mindestgröße | Macro | Kontrolle | Vorsprung | Blöcke **ohne** FVG (Macro / Kontrolle) |
|---|---|---|---|---|
| ≥ 2 Pkt | 2,81 | 2,59 | +8 % | 5 % / 7 % |
| ≥ 5 Pkt | 1,70 | 1,52 | +12 % | 18 % / 25 % |
| **≥ 10 Pkt** | **0,81** | **0,61** | **+33 %** | **46 % / 60 %** |
| ≥ 15 Pkt | 0,37 | 0,28 | +32 % | 72 % / 80 % |

**Je größer das FVG, desto stärker sitzt es im Macro.** Und daraus folgt die praktisch wichtigere
Hälfte: *"ein FVG im Macro"* ist als Filter wertlos — **95 % aller Macro-Fenster enthalten
mindestens ein FVG ≥ 2 Punkte**, im Schnitt fast drei pro 20 Minuten. Wer darauf wartet, wartet
auf etwas, das praktisch immer passiert. Erst ab ~10 Punkten wird das FVG selten genug, um zu
selektieren: dann hat es nur noch gut jedes zweite Macro (54 %) gegen 40 % der Kontrollblöcke.

Das passt zum Hauptbefund oben: der Macro-Vorteil steckt in der **Größe und Geradlinigkeit** der
Bewegung, nicht in der bloßen Existenz einer Ineffizienz.

### Beleg-Beispiel: das SB FVG vom 2026-08-10, 14:12 (verifiziert)

Aus 1m-Daten bestätigt (yfinance MNQ=F, Nachzug um 14:34 NY): 14:11 Low **29.767,25**, 14:13 High
**29.759,50** → SIBI von **29.759,50 bis 29.767,25**, Größe **7,75 Punkte**, C.E. **29.763,38**.
Preis fiel anschließend bis 29.742,25 und lief bis 14:34 auf 29.764,75 zurück, also **über die
C.E. hinein**; um 14:42 stand er bei 29.768,00 und damit an der Gap-Oberkante — das FVG war
vollständig durchgehandelt.

Bemerkenswert für die Tabelle darüber: mit 7,75 Punkten liegt genau dieses SB FVG **unterhalb der
10-Punkte-Schwelle**, ab der sich FVGs überhaupt erst im Macro häufen. Es gehört zur häufigen
Sorte, nicht zur selektiven. Und es entstand 14:12, also zwei Minuten **nach** dem Macro
13:50–14:10 (im [[Silver Bullet Model|SB-Fenster]] 14:00–15:00 dagegen liegt es).

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
