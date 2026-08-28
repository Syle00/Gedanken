# Weekly Bias KW36 2026

*(Mo 31.08. – Fr 04.09.2026, erzeugt am 28.08.2026 durch `/bias-vorlage-weekly`, gelaufen als
Cloud-Agent in einem eigenen Checkout. Zwei Einschränkungen unten wirken sich auf die ganze
Datei aus: die Marktdaten für KW35 [24.–28.08.] fehlen komplett, und der COT-Abruf ist am
Proxy gescheitert — siehe Levels- bzw. COT-Abschnitt.)*

## News (Red/Orange Folder), ganze Woche

**Mo 31.08.** ❌ keine USD-Termine

**Di 01.09.** ❌ keine USD-Termine

**Mi 02.09.** ❌ keine USD-Termine

**Do 03.09.** ❌ keine USD-Termine

**Fr 04.09.** ❌ keine USD-Termine

**Quelle:** `tradingview` (ForexFactory nicht nutzbar: `URLError: <urlopen error Tunnel
connection failed: 403 Forbidden>`, TradingView-Kalender als Fallback verwendet).

**Einordnung:** Der Kalender liefert für alle fünf Tage null USD-Termine mit Red-/Orange-
Impact — das ist **kein** Abruf-Fehler im Sinne von `news.error` (die Tabelle steht, nur eben
leer), aber auch nicht der übliche Freitagabend-Regelfall ("ForexFactory kennt die Zielwoche
noch nicht"), denn hier hat sogar der TradingView-Fallback nichts gefunden.

⚠️ **Das ist auffällig, weil Fr 04.09. rechnerisch der erste Freitag im September ist — der
übliche NFP-Termin.** Ich trage NFP hier **nicht** ein, weil kein Datenfeld das bestätigt und
die Anweisung ausdrücklich verbietet, News zu erfinden. Aber: sollte der NFP-Termin bis
Montag noch nicht im Kalender auftauchen, das manuell auf forexfactory.com/tradingview
gegenprüfen, bevor Fr 04.09. als newsarmer Tag behandelt wird — die Wahrscheinlichkeit, dass
diese Woche tatsächlich NFP-frei ist, halte ich für gering.

## Levels

Gerechnet aus `raw/marktdaten/` (**NQ**, `gaps.symbol: NQ`, kein `gaps.hinweis` — kein
MNQ-Rückfall nötig). Angefordertes Fenster 24.07.–28.08., Preise auf dem 0,25-Tickraster.

⚠️ **Aktive Datenlücke, nicht auf Ansage zu schließen:** In diesem Checkout enthält
`raw/marktdaten/2026/08/` keine Ordner für **24.–28.08.2026** — die komplette auslaufende
Handelswoche (KW35) fehlt, weder als 1s noch als 1m, weder als Parquet noch registriert in
`1s-abdeckung.csv`. Das ist kein Fall von `registriert_ohne_datei` (die Tage sind nicht
einmal als geholt protokolliert), sondern schlicht: die Woche wurde in diesem Checkout noch
nicht nachgezogen. Letzter verfügbarer Handelstag ist **Fr 21.08.2026** (Close 17:00 NY:
**29374.00**). Folgen für diesen Abschnitt:

- Die Range der auslaufenden Woche (KW35) lässt sich **nicht** berechnen — auch nicht über
  den 1s-Fallback wie in der KW35-Datei, weil dafür schlicht keine Zeilen vorliegen.
- NDOG für Fr 21.08. fehlt (bräuchte den Open vom Mo 24.08.), ebenso NWOG für So 23.08.
  (bräuchte denselben Open). Beide sind unten deshalb nicht gelistet, nicht weil sie gefüllt
  wären, sondern weil sie nicht berechenbar sind.
- Die Level unten (offener Gap, ältere NWOGs/NDOGs) stammen alle aus dem Fenster bis 21.08.
  und sind davon unberührt.

**Datenlage im verfügbaren Fenster (24.07.–21.08., 21 Handelstage):** alle 21 liegen als
**1s** vor, `tage_nur_1m` ist leer, `registriert_ohne_datei` ist für dieses Fenster ebenfalls
leer — kein stiller Datenverlust innerhalb der vorhandenen Tage.

Wo TradingView-1m denselben Tag abdeckt (18 Tage), wurde 1s dagegen gegengerechnet:

| Tag | verglichene Minuten | ungleich | max. Abweichung |
| --- | --- | --- | --- |
| 28.07. | 566 | 1 | 0.25 |
| 29.07. | 1380 | 3 | 0.50 |
| 30.07. | 1380 | 7 | 2.00 |
| 31.07. | 1380 | 3 | 1.75 |
| 03.08. | 1380 | 2 | 0.25 |
| 04.08. | 1380 | 4 | 0.25 |
| 05.08. | 1380 | 3 | 0.25 |
| 06.08. | 1380 | 3 | 1.25 |
| 07.08. | 1380 | 4 | 0.75 |
| 10.08. | 1380 | 1 | 0.25 |
| 11.08. | 1380 | 3 | 0.75 |
| 12.08. | 1380 | 1 | 0.25 |
| 13.08. | 1380 | 3 | 0.25 |
| 14.08. | 1380 | 4 | 0.50 |
| 17.08. | 432 | 7 | 0.75 |
| 18.08. | 1380 | 5 | 0.75 |
| 19.08. | 1380 | 5 | 1.00 |
| 20.08. | 496 | 1 | 2.50 |

Größte Abweichung 2,50 Punkte (20.08., nur 496 verglichene Minuten an dem Tag), sonst durchweg
im niedrigen Punktebereich — beide Quellen bestätigen sich, die Level unten sind belastbar.

### Offene Gaps — die DOL-Kandidaten

| Level | Datum | Close (17:00) | Open (18:00) | Gap | C.E. | Status |
|---|---|---|---|---|---|---|
| **NWOG** | So 02.08. (Close Fr 31.07.) | 28287.00 | 28565.00 | **+278.00** | **28426.00** | **offen** |

Nach wie vor **ein einziger** offener Gap im gesamten Fenster — unverändert seit der
KW35-Datei, da dazwischen keine neuen Handelstage vorliegen. Alle 16 NDOGs und die drei
übrigen NWOGs im Fenster sind gefüllt. Bezogen auf den letzten bekannten Preis (Fr 21.08.
Close 29374.00) liegt das C.E. rund **948 Punkte darunter** — weit, aber der einzige
unerledigte Gap und damit der übergeordnete Downside-Magnet, bis neue Daten etwas anderes
zeigen.

**NWOG 02.08. — Qs / Os / Hs**

| | Level |
| --- | --- |
| High (Open So 18:00) | 28565.00 |
| O7 | 28530.25 |
| O6 / **Q3** | 28495.50 |
| O5 | 28460.75 |
| **C.E. (= H1 = Q2 = O4)** | **28426.00** |
| O3 | 28391.25 |
| O2 / **Q1** | 28356.50 |
| O1 | 28321.75 |
| Low (Close Fr 16:59) | 28287.00 |

### NWOG der letzten Wochen

| Level | Datum | Close (Fr 17:00) | Open (So 18:00) | Gap | C.E. | Status |
| --- | --- | --- | --- | --- | --- | --- |
| NWOG | So 16.08. | 30154.00 | 30170.00 | +16.00 | 30162.00 | gefüllt |
| NWOG | So 09.08. | 29839.50 | 29851.25 | +11.75 | 29845.50 | gefüllt |
| NWOG | So 02.08. | 28287.00 | 28565.00 | +278.00 | 28426.00 | **offen** |
| NWOG | So 26.07. | 28306.50 | 28500.00 | +193.50 | 28403.25 | gefüllt |

### NDOG im Fenster (bis Do 20.08. — Fr 21.08. fehlt, siehe oben)

| Level | Datum | Close (17:00) | Open (18:00) | Gap | C.E. | Status |
| --- | --- | --- | --- | --- | --- | --- |
| NDOG | Mo 17.08. | 30078.25 | 30077.00 | −1.25 | 30077.50 | gefüllt |
| NDOG | Di 18.08. | 29559.50 | 29566.50 | +7.00 | 29563.00 | gefüllt |
| NDOG | Mi 19.08. | 29561.00 | 29561.50 | +0.50 | 29561.25 | gefüllt |
| NDOG | Do 20.08. | 29317.25 | 29327.00 | +9.75 | 29322.00 | gefüllt |

Alle vier noch im einstelligen bis niedrig zweistelligen Bereich und am selben Tag gefüllt.

### Range der auslaufenden Woche (KW35)

**Nicht berechenbar** — siehe Datenlücke oben. Einziger bekannter Referenzpunkt ist der
Fr-21.08.-Handelstag (18:00 NY Do 20.08. → 16:59:59 NY Fr 21.08.), der noch vollständig
vorliegt:

| Tag | High | Low | Close |
| --- | --- | --- | --- |
| Fr 21.08. | 29539.00 | 29220.00 | **29374.00** |

Zum Vergleich die KW34-Quadranten (Vorwoche von KW35, aus der KW35-Datei übernommen, da
KW35 selbst nicht nachrechenbar ist):

| | Level |
| --- | --- |
| High (Mo 17.08.) | 30343.00 |
| O7 | 30200.50 |
| O6 / **Q3** | 30058.00 |
| O5 | 29915.50 |
| **C.E. (= H1 = Q2 = O4)** | **29773.00** |
| O3 | 29630.25 |
| O2 / **Q1** | 29487.75 |
| O1 | 29345.25 |
| Low (Do 20.08.) | 29202.75 |

Der Fr-21.08.-Close 29374.00 liegt zwischen O1 (29345.25) und Q1 (29487.75), also weiterhin
im Discount-Bereich der KW34-Range.

## COT (Commercials vs. Large Specs)

⚠️ **COT-Abruf fehlgeschlagen** (`ProxyError: HTTPSConnectionPool(host='cftc.gov', port=443):
Max retries exceeded with url: /files/dea/history/deacot2022.zip (Caused by
ProxyError('Unable to connect to proxy', OSError('Tunnel connection failed: 403 Forbidden')))`).
Der Fehler betrifft den gesamten Abruf, nicht nur ein Symbol — weder NQ noch ES liegen diese
Woche Zahlen vor. Keine Werte erfunden; letzter belastbarer Stand ist der in der
KW35-Datei dokumentierte Report vom 18.08.2026 (dort: NQ 3M/6M bearish, 12M/2Y bullish,
4Y bearish/neutral; ES über alle Horizonte bearish; in beiden Symbolen `gegenlaeufig: false`,
Commercials und Large Specs auf derselben Seite). Für KW36 keine belastbare Aussage möglich —
manuell auf cftc.gov prüfen, falls ein aktueller Report für die Einschätzung gebraucht wird.

## Wiki-Bezug

- [[Weekly Range Trading Model]] — Wochenprofil, welcher Tag High/Low setzt; für KW36 ohne
  KW35-Referenz (siehe Datenlücke) nicht mit der Vorwoche vergleichbar.
- [[IPDA Data Ranges]] — übergeordneter Datenbereich, in dem KW36 liegt.
- [[COT (Commitment of Traders) Data]] — EQ-Lesart der Lookback-Range; diese Woche ohne neue
  Zahlen, siehe COT-Abschnitt.
- [[Seasonal Tendency]] / [[Seasonal Tendency (Eigene Daten, laufend)]] — Wochentags-,
  Monats- und Week-of-Month-Muster, siehe Einschätzung.
- [[New Week Opening Gap (NWOG) Bias]] — zum offenen NWOG vom 02.08.
- [[New Day Opening Gap (NDOG)]] — zur NDOG-Tabelle.
- [[Using Monthly & Weekly Ranges (Source)]] — **Monatswechsel liegt mitten in KW36**: Mo
  31.08. ist der letzte Handelstag im August, Di–Do (01.–03.09.) sind die ersten drei
  Handelstage im September — vier der fünf Handelstage dieser Woche liegen im
  Turn-of-Month-Fenster.

## Einschaetzung (Claude)

**Datenbasis eingeschränkt.** News liefert (via TradingView-Fallback) formal null Termine,
aber mit der oben genannten NFP-Unsicherheit für Fr 04.09. COT ist komplett ausgefallen. Die
Level-Historie bis 21.08. steht sauber, aber ohne die auslaufende Woche (KW35) fehlt der
unmittelbare Bezugspunkt "wo steht der Markt gerade" — der letzte bekannte Preis ist der
Fr-21.08.-Close (29374.00), sieben Tage alt zum Zeitpunkt dieser Datei.

**Saisonalität** aus `algo/seasonal_tendency.json` (n=1882 Tage, 06.05.2019–14.08.2026, Symbol
MNQ):

- **Turn-of-Month betrifft diese Woche stark**: Mo 31.08. + Di/Mi/Do 01.–03.09. liegen im
  TOM-Fenster (4 von 5 Handelstagen). Der Effekt selbst ist aber schwach: TOM-Fenster 53,6 %
  bullish (n=349, avg +0,078 %) gegen 54,3 % im Rest (n=1533, avg +0,071 %) — praktisch kein
  Unterschied, wie schon in der KW35-Einschätzung festgehalten.
- **Week-of-Month**: Mo 31.08. fällt kalendarisch noch in "Woche 5" von August (46,1 %
  bullish, n=152, avg +0,099 %), Di–Fr (01.–04.09.) in "Woche 1" von September (56,5 %
  bullish, n=430, avg +0,089 %) — die stärkere der beiden Klassen trägt vier der fünf Tage.
- **September auf Monatsebene ist historisch schwach**: In 5 der letzten 7 Jahre negative
  Durchschnittsrendite (2020 −0,294 %, 2021 −0,202 %, 2022 −0,571 %, 2023 −0,21 %), nur 2019
  (+0,079 %), 2024 (+0,003 %, praktisch flach) und 2025 (+0,161 %) positiv. Das ist der
  deutlichste saisonale Fingerzeig dieser Woche — in die Gegenrichtung der schwachen
  Wochentags-/TOM-Effekte oben.
- **Montag ist der stärkste Einzelwochentag** (61,4 % bullish, avg +0,194 %), **Donnerstag der
  einzige mit negativer Durchschnittsrendite** (52,1 % bullish, avg −0,012 %) — beide Tage
  liegen in KW36.

**Wochenrichtung: keine klare Kante, leichter Bearish-Bias auf Monatsebene.** Die
kurzfristigen Effekte (TOM, Wochentag) sind zu schwach, um für sich zu tragen; die
Monats-Statistik für September ist der robustere Fingerzeig und zeigt in 5 von 7 Jahren nach
unten. Ohne aktuelle COT-Daten und ohne KW35-Referenzpunkt ist das aber eine schwache
Einschätzung — **Wahrscheinlichkeit für eine bearische Wochentendenz ~55 %**, nicht mehr.

**NFP-Einordnung (falls Fr 04.09. bestätigt NFP ist):** `algo/backtest_nfp_week.py` zeigt für
die 85 NFP-Freitage im Datensatz eine deutlich höhere Ø-Range (350,71 vs. 284,56 an anderen
Freitagen) bei gleichzeitig **niedrigerer** Whipsaw-Ratio (Ø 4,05 vs. 9,43) — NFP-Freitage
laufen historisch weiter, aber sauberer/direktionaler als normale Freitage. Das spräche dafür,
Fr 04.09. als potenziellen Range-Ausbruchstag einzuplanen, sollte NFP bestätigt sein — aber
das ist konditional auf eine News-Bestätigung, die diese Datei nicht liefert.

**NWOG-Einschränkung, unverändert gültig.** `algo/backtest_nwog.py` misst aktuell eine
Bias-intakt-Quote von **9,6 %** (36/375 Wochen, NWOG intraweek nicht wieder erreicht) — auch
mit dem Zusatzbefund "ab Dienstag hält der Bias in 28,5 % der Fälle". Das offene NWOG vom
02.08. (C.E. **28426.00**) ist damit ein **Level**, kein Richtungsfilter. Es bleibt der
einzige unerledigte Gap im gesamten Fenster und damit der übergeordnete Downside-Magnet,
unabhängig von der obigen Wochenrichtungs-Einschätzung.

**Zusammengefasst:** schwacher, monatsgetragener Bearish-Tilt (~55 %), überlagert von zwei
harten Datenlücken (KW35-Preisdaten, COT) und einer ungeklärten NFP-Frage für Freitag — das
ist eine Woche, in der die Level (offenes NWOG bei 28426.00, KW34-C.E. bei 29773.00) tragfähiger
sind als die Richtungseinschätzung.

## Mein Bias
