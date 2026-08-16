# Weekly Bias KW34 2026

*(Mo 17.08. – Fr 21.08.2026, überarbeitet am 16.08.2026 durch `/bias-vorlage-weekly`)*

## News (Red/Orange Folder), ganze Woche

Quelle: **ForexFactory** (`news.source: forexfactory`, Feed-Span 16.–21.08. — deckt die
Zielwoche vollständig ab). **Nur USD** — gehandelt werden NQ/ES.

**Mo 17.08.** ❌ keine USD-Termine

**Di 18.08.** ❌ keine USD-Termine

**Mi 19.08.**

🔴 **14:00 NY** / 20:00 DE — FOMC Meeting Minutes

**Do 20.08.**

🟠 **08:30 NY** / 14:30 DE — Philly Fed Manufacturing Index  (Forecast 24.3, Previous 41.4)

🟠 **08:30 NY** / 14:30 DE — Unemployment Claims  (Forecast 210K, Previous 209K)

**Fr 21.08.** ❌ keine USD-Termine

**Drei USD-Termine in der ganzen Woche, verteilt auf zwei Tage.** Montag, Dienstag und Freitag
sind leer — das ist kein Abrufproblem, sondern die Nachrichtenlage. Der einzige echte Taktgeber
ist **Mittwoch 14:00 NY**.

Das ist ein **Nachmittagstermin** — anders als CPI/PPI, die vor dem Open liegen und die
Tagesrange von Beginn an prägen. Für Mittwoch gilt [[Two Stage News Delivery (FOMC & NFP)]]:
erste Reaktion direkt auf 14:00, die eigentliche Auflösung eher danach, nicht in einer
Bewegung.

## Levels

Gerechnet aus `raw/marktdaten/` (**NQ**, 14 Handelstage im Fenster). Kein MNQ-Rückfall nötig —
die Level stammen aus dem tatsächlich gehandelten Symbol. Alle Preise auf dem 0,25-Tickraster.

**Datenlage (1s bevorzugt):** Nur **2 der 14 Tage** liegen als 1s vor (13.08., 14.08.), die
übrigen **12 Tage nur als 1m**. `1s-abdeckung.csv` protokolliert für dieses Fenster keinen Tag,
zu dem die Parquet-Datei fehlt — Register und Bestand decken sich.
Wo beide Quellen denselben Tag abdecken, wurde gegengerechnet:

| Tag | verglichene Minuten | ungleich | max. Abweichung |
|---|---|---|---|
| 13.08. | 1380 | 3 | 0.25 |
| 14.08. | 1380 | 4 | 0.50 |

IBKR-1s und der TradingView-1m-Export bestätigen sich also gegenseitig (>99,7 % identisch).
Die Level oben sind damit belastbar — **die 1s-Historie für Juli/August fehlt aber weitgehend**,
der NWOG vom 02.08. stammt aus 1m-Daten.

### Offene Gaps — die DOL-Kandidaten

| Typ | Datum | Close (17:00) | Open (18:00) | Gap | C.E. | Spanne |
|---|---|---|---|---|---|---|
| **NWOG** | Fr 31.07. → So 02.08. | 28287.00 | 28565.00 | **+278.00** | **28426.00** | 278.00 |
| **NDOG** | Mi 29.07. | 27259.25 | 27202.00 | −57.25 | **27230.50** | 57.25 |

Beide liegen **deutlich unter** dem Freitagsschluss (30154.00) — es sind Sell-Side-Ziele,
keine Kaufzonen. Der NWOG ist mit 278 Punkten Spanne das mit Abstand größere Array.

**NWOG 02.08. — Qs / Os / Hs**

| | Level |
|---|---|
| High (Open So 18:00) | 28565.00 |
| O7 | 28530.25 |
| O6 / **Q3** | 28495.50 |
| O5 | 28460.75 |
| **C.E. (= H1 = Q2 = O4)** | **28426.00** |
| O3 | 28391.25 |
| O2 / **Q1** | 28356.50 |
| O1 | 28321.75 |
| Low (Close Fr 16:59) | 28287.00 |

**NDOG 29.07. — Qs / Os / Hs**

| | Level |
|---|---|
| High (Close 16:59) | 27259.25 |
| O7 | 27252.00 |
| O6 / **Q3** | 27245.00 |
| O5 | 27237.75 |
| **C.E. (= H1 = Q2 = O4)** | **27230.50** |
| O3 | 27223.50 |
| O2 / **Q1** | 27216.25 |
| O1 | 27209.25 |
| Low (Open 18:00) | 27202.00 |

### NWOG der letzten Wochen

| Datum | Close (Fr 17:00) | Open (So 18:00) | Gap | C.E. | Status |
|---|---|---|---|---|---|
| So 02.08. | 28287.00 | 28565.00 | +278.00 | 28426.00 | **offen** |
| So 09.08. | 29839.50 | 29851.25 | +11.75 | 29845.50 | gefüllt |

### NDOG der auslaufenden Woche (KW33)

| Datum | Close (17:00) | Open (18:00) | Gap | C.E. | Status |
|---|---|---|---|---|---|
| Mo 10.08. | 29764.25 | 29764.50 | +0.25 | 29764.50 | gefüllt |
| Di 11.08. | 29646.75 | 29657.75 | +11.00 | 29652.25 | gefüllt |
| Mi 12.08. | 29805.75 | 29825.00 | +19.25 | 29815.50 | gefüllt |
| Do 13.08. | 30214.25 | 30210.75 | −3.50 | 30212.50 | gefüllt |

Alle vier gefüllt — die Woche hat jeden Tages-Gap wieder eingesammelt.

### Range der auslaufenden Woche (KW33)

| | Wert |
|---|---|
| High | **30283.00** (Fr 14.08. 09:05 NY) |
| Low | **29533.50** (Di 11.08. 14:29 NY) |
| Spanne | 749.50 Punkte |
| Letzter Print | 30154.00 (Fr 14.08. 16:59 NY) |
| Handelstage | 5 |

> ⚠️ **Aus den Intraday-Daten gerechnet, nicht aus der 1d-Datei.** `bias_levels.py` meldet aus
> der 1d-Reihe ein Wochen-High von 30273.25 — **9,75 Punkte zu niedrig**. Derselbe
> Zu-früh-Snapshot-Fehler wie beim 14.08. (1d: 30232.5/30124.25 gegen 1m: 30287.25/30025.0,
> 154 Punkte Differenz). Die 1d-Reihe ist für Wochen-Extrema im Bestand weiterhin unzuverlässig.

Der Schlusskurs liegt bei **30154.00**, also im oberen Drittel der KW33-Range. Das Wochen-High
(30283.00) liegt nur ~129 Punkte darüber und ist der nächstliegende Liquiditätspunkt nach oben.

## COT (Commercials vs. Large Specs)

Stand **11.08.2026** (CFTC-Legacy-Report, Reihen „NASDAQ MINI" bzw. „E-MINI S&P 500").
Ausgewertet nach [[COT (Commitment of Traders) Data]]: nur **Commercials gegen Large
Speculators**, Signal gegen das **EQ der Lookback-Range** — nicht gegen die 0-Linie.

| Symbol | Commercials | Large Specs | Lage |
|---|---|---|---|
| **NQ** | **+17.475** (long) | **−39.302** (short) | gegenläufig |
| **ES** | **−142.440** (short) | **+11.280** (long) | gegenläufig |

**NQ und ES stehen gegeneinander.** In beiden Märkten sind Commercials und Large Specs
gegenläufig positioniert — aber mit umgekehrten Vorzeichen: Bei NQ sind die Commercials netto
**long** (für Index-Futures die Ausnahme, sie sind dort strukturell short), bei ES netto
**short** und das nahe am 12-Monats-Tief.

Das ist eine Divergenz zwischen den beiden Indizes, wie sie [[SMT (Smart Money Divergence)|SMT]]
auf Preisebene beschreibt — hier auf Positionierungsebene. Sie ist der auffälligste Befund
dieser Woche und spricht gegen ein einheitliches Index-Bias.

**NQ — alle Horizonte bullish (einig)**

| Horizont | Range (Low … High) | EQ | Signal |
|---|---|---|---|
| 3M | −14.946 … +17.475 | +1.264 | 🟢 bullish |
| 6M | −31.456 … +17.475 | −6.990 | 🟢 bullish |
| **12M** | −66.754 … +17.475 | −24.640 | 🟢 **bullish** |
| 2Y | −66.754 … +17.475 | −24.640 | 🟢 bullish |
| 4Y | −66.754 … +43.337 | −11.708 | 🟢 bullish |

**ES — alle Horizonte bearish (einig)**

| Horizont | Range (Low … High) | EQ | Signal |
|---|---|---|---|
| 3M | −142.440 … +110.074 | −16.183 | 🔴 bearish |
| 6M | −142.440 … +110.074 | −16.183 | 🔴 bearish |
| **12M** | −142.440 … +134.019 | −4.210 | 🔴 **bearish** |
| 2Y | −233.202 … +134.019 | −49.592 | 🔴 bearish |
| 4Y | −233.202 … +435.558 | +101.178 | 🔴 bearish |

> Der aktuelle ES-Wert **−142.440 ist zugleich das Tief der 3M-, 6M- und 12M-Range** — die
> Commercials sind so kurz positioniert wie seit zwölf Monaten nicht. Alle fünf Horizonte
> zeigen deshalb in dieselbe Richtung; ein Lookback-Streit stellt sich hier nicht.

**Wende gegenüber Anfang August (NQ).** Am Report vom 28.07. standen die NQ-Commercials noch bei
−14.946 (3M/6M/4Y bearish, nur 12M/2Y bullish). In zwei Wochen sind sie um **+32.421** auf
+17.475 gedreht und haben damit jeden Horizont ins Bullische gekippt. ES lief im selben Zeitraum
in die Gegenrichtung (−95.929 → −142.440, also **−46.511**). Die beiden Indizes haben sich in
zwei Wochen auseinanderbewegt — ein COT-Urteil aus der Vorwoche trägt hier nicht mehr.

## Wiki-Bezug

- [[Weekly Range Trading Model]] — Wochenstruktur, welcher Tag High/Low setzt
- [[IPDA Data Ranges]] — übergeordneter Datenbereich, in dem KW34 liegt
- [[COT (Commitment of Traders) Data]] — EQ-Lesart der 12-Monats-Range, siehe COT-Abschnitt
- [[Seasonal Tendency]] — im Verbund mit COT zur Bias-Bestätigung
- [[New Day Opening Gap (NDOG)]] — für die beiden offenen Gaps oben
- [[Two Stage News Delivery (FOMC & NFP)]] — einschlägig für Mittwoch 14:00
- [[Using Monthly & Weekly Ranges (Source)]] — KW34 liegt in der Monatsmitte

## Einschätzung (Claude)

**Struktur der Woche.** Der einzige echte Taktgeber ist Mittwoch 14:00 NY. Montag, Dienstag und
Freitag sind newsseitig leer — die Woche nimmt ihre Richtung eher aus der Struktur als aus
Daten. Der Schwerpunkt liegt damit in der Wochenmitte.

**Statistik, ehrlich eingeordnet.** Aus `algo/seasonal_tendency.json` (n=1882 Tage):

- **Montag ist mit 61,4 % bullish** (n=376, avg +0,194 %, Median-Range 263,88) der klar
  stärkste Wochentag und die einzige Wochentagsabweichung, die deutlich aus dem Rauschen läuft
  (Di 50,5 %, Mi 55,3 %, Do 52,1 %).
- **Die dritte Woche des Monats ist dagegen die schwächste**: 50,3 % bullish, avg −0,01 %
  (n=433) — praktisch ein Münzwurf. KW34 ist eine solche dritte Woche.

Diese beiden Kennzahlen zeigen in verschiedene Richtungen. Aus ihnen lässt sich kein
Wochenbias ableiten, nur eine leichte Erwartung eines festeren Wochenstarts.

**NWOG-Einschränkung, unverändert gültig.** `algo/backtest_nwog.py` misst eine
**Bias-intakt-Quote von nur 7 %** — die meisten Wochen durchbrechen ihr NWOG wieder. Das NWOG
taugt als **Level** (DOL-Kandidat), nicht als Richtungsfilter. Diese Einschränkung gilt auch
für den offenen 02.08.-NWOG unten.

**Ausgangslage.** KW33 schloss bei 30154.00 im oberen Drittel ihrer Range. Nach oben liegt das
Wochen-High bei 30283.00 (~129 Punkte). Nach unten sind die beiden offenen Gaps mit C.E.
28426.00 und 27230.50 die einzigen unerledigten PD Arrays — aber rund 1700 bzw. 2900 Punkte
entfernt. Als Wochenziel sind sie damit unrealistisch; sie bleiben übergeordnete Draw-Kandidaten,
nicht KW34-Ziele.

**Kein Turn-of-Month.** KW34 liegt in der Monatsmitte, die Turn-of-Month-Kennzahlen greifen nicht.

**COT ist der auffälligste Befund — aber kein einheitlicher.** Die Positionierung zeigt in den
beiden Indizes gegeneinander: NQ-Commercials netto **long** über alle fünf Horizonte (nach einer
Drehung um +32.421 in zwei Wochen), ES-Commercials netto **short** über alle fünf Horizonte und
dabei am 12-Monats-Tief (−46.511 im selben Zeitraum). Nach der Lesart aus
[[COT (Commitment of Traders) Data]] steht damit ein bullishes NQ-Signal gegen ein bearishes
ES-Signal.

Diese Divergenz ist auf Positionierungsebene das, was [[SMT (Smart Money Divergence)|SMT]] auf
Preisebene beschreibt — **als Handelssignal für die Folgewoche taugt sie aber nicht.**

> **Gebacktestet und widerlegt** (`algo/backtest_cot_divergenz.py`, 16.08.2026). Über 101
> Divergenzfälle seit 2022: Läuft in der Folgewoche das Symbol mit dem bullishen COT-Signal
> besser als das mit dem bearishen? **Trefferquote 46,5 %** — schlechter als der Münzwurf.
> Ø-Spread −0,068 %, Median −0,104 %. Die Kontrollgruppe (beide Symbole gleiches Signal,
> n=132) liegt mit 48,5 % praktisch gleichauf. Es gibt also keinen messbaren Unterschied
> zwischen Divergenz und Gleichlauf.
>
> Gemessen wurde ohne Lookahead: Signal aus dem Report der Woche W (Stand Dienstag,
> veröffentlicht Freitag) gegen den Return der Woche W+1 (Montag-Open bis Freitag-Close).

Die Divergenz bleibt damit eine **Beschreibung der Lage**, kein Vorsprung. Sie erklärt, warum
kein einheitliches Index-Bias sinnvoll ist — mehr nicht.

Einschränkungen, die dazugehören: COT ist ein **Wochenbild mit Verzögerung** (Stand Dienstag,
veröffentlicht Freitag) und taugt zur Bias-Bestätigung, nicht zum Timing. Die Kombination, auf
die ICT abstellt — COT plus [[Seasonal Tendency]] plus SMT — ist hier nur teilweise gegeben,
weil die Saisonalität (dritte Monatswoche, 50,3 %) neutral steht.

**Was diese Einschätzung nicht leistet:** Sie nennt kein Wochenziel und kein einheitliches
Index-Bias. Die Newslage ist dünn, die Saisonalität neutral, die offenen Gaps liegen zu weit
unten — und COT zeigt in NQ und ES gegeneinander. Was bleibt: die Level oben als Bezugspunkte
und die NQ/ES-Divergenz als Beobachtungsauftrag.

## Mein Bias

Weekly Chart haben wir einen Suspensionblock Bisi gebildet 2 vii und Buyside genommen wir haben auch über dem Swing High geclosed.
28,500,00 Low High bei 29,851,25.
3 Buysie Liq Pools abgesehen vom PWH und PDH 30,599,75 29. Juni
30,975,50 15 juni und das ATH = All time high bei 31,100,00

Ein Retracement ins BISI ist denkbar weil wir bereits gute Buyside genommen haben und einen Internal Liq Sweep in Form des Bisi realistisch ist.

Daily Chart bin ich gespanntt ob alte FVG genutzt werden als IFVG oder reclaimed FVG vom 23. Juli z.b Im Daily Chart sehe ich abgesehen von Buyside Pools nicht viel weiter. Ein Daily bisi mit einer vii 13.08 auch hier wäre ein Retracement denkbar.

4h Chart großes sibi vom 22 juni 22 uhr interessiert michschauen ob die noch relevant ist. Viel Sellside das sind keine rel die nebeneinander liegen sondern alles swing lows aber es passt zum interene Liq sweep

Im 1H Chart sind sind es bessere Sellside Pools 12.08 18:00 uhr bei 29,780,50 unterhalb des Daily Bisi das gefällt mir als DOL gut.
Sollte der Longterm Bias weiterhin Bullish sein sehe ich ungern einen close unterhalb. Allgemein wenn wir weiter Bullish sind muss Price mir das zeigen aber da wir Montag keine News haben und keine NFP am Freitag ist wird die Priceaction wohl etwas schwierig.
S&P Chart sieht ähnlich aus. Ich werde schauen was der Montag bringt
