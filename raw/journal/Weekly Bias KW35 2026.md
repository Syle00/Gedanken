# Weekly Bias KW35 2026

*(Mo 24.08. – Fr 28.08.2026, erzeugt am 23.08.2026 durch `/bias-vorlage-weekly`. Ersetzt die
Fassung vom 21.08., die in einer Cloud-Session ohne Netzzugang zu ForexFactory und CFTC
entstand — News und COT stehen unten jetzt vollständig.)*

## News (Red/Orange Folder), ganze Woche

**Mo 24.08.**

🟠 **14:00 NY** / 20:00 DE — Treasury Sec Bessent Speaks

**Di 25.08.**

🟠 **10:00 NY** / 16:00 DE — CB Consumer Confidence  (Forecast 90.3, Previous 90.8)

**Mi 26.08.**

🔴 **08:30 NY** / 14:30 DE — Core PCE Price Index m/m  (Forecast 0.2%, Previous 0.1%)

🔴 **08:30 NY** / 14:30 DE — Prelim GDP q/q  (Forecast 1.5%, Previous 1.5%)

🟠 **08:30 NY** / 14:30 DE — Prelim GDP Price Index q/q  (Forecast 6.2%, Previous 6.2%)

**Do 27.08.**

🟠 **08:30 NY** / 14:30 DE — Unemployment Claims  (Forecast 208K, Previous 206K)

**Fr 28.08.**

🔴 **10:00 NY** / 16:00 DE — Fed Chairman Warsh Speaks

🔴 **10:00 NY** / 16:00 DE — Prelim Benchmark Payrolls Revision  (Previous -911K)

🟠 **10:00 NY** / 16:00 DE — Revised UoM Consumer Sentiment  (Forecast 51.0, Previous 51.0)

🟠 **10:00 NY** / 16:00 DE — Revised UoM Inflation Expectations  (Previous 4.3%)

**Quelle:** `forexfactory` (Feed-Spanne 23.08.–29.08.2026), `news.error: null` — kein Fallback
auf TradingView nötig, kein Abruf-Fehler.

**Einordnung:** 10 USD-Termine, alle fünf Handelstage belegt, kein leerer Tag. Vier davon sind
Red Folder und sie ballen sich auf zwei Tage:

- **Mi 26.08., 08:30 NY / 14:30 DE — Core PCE Price Index m/m (🔴)** ist der Taktgeber der
  Woche. Es ist das Inflationsmaß, auf das die Fed selbst abstellt; Forecast 0,2 % gegen
  Previous 0,1 %, also eine erwartete Beschleunigung. Zeitgleich läuft **Prelim GDP q/q (🔴)**
  plus **Prelim GDP Price Index q/q (🟠)** — drei Zahlen in derselben Sekunde, entsprechend
  breit dürfte der 14:30-Impuls ausfallen.
- **Fr 28.08., 10:00 NY / 16:00 DE** bringt den zweiten Block: **Fed Chairman Warsh Speaks
  (🔴)** und **Prelim Benchmark Payrolls Revision (🔴)** — letztere mit Previous −911K, also
  eine potenziell große Revision der Beschäftigungsbasis. Dazu die beiden UoM-Revisionen (🟠).
- Mo und Do sind die ruhigen Tage: Mo nur Bessent (🟠, 14:00 NY), Do nur Unemployment Claims
  (🟠, 08:30 NY). Di bringt CB Consumer Confidence (🟠, 10:00 NY).

**Kein NFP diese Woche** — NFP fällt auf den ersten Freitag des Monats, also den 04.09. Die
Payrolls-*Revision* am Fr 28.08. ist ein anderer Termin und macht KW35 nicht zur NFP-Woche.

## Levels

Gerechnet aus `raw/marktdaten/` (**NQ**, kein MNQ-Rückfall nötig — `gaps.symbol: NQ`, kein
`gaps.hinweis`). Fenster 19.07.–23.08. Alle Preise auf dem 0,25-Tickraster.

**Datenlage:** alle **24 Handelstage im Fenster liegen als 1s vor**, `tage_nur_1m` ist leer —
es steckt kein einziges Level in dieser Datei, das nur aus 1m-Daten stammt.
`registriert_ohne_datei` ist **leer**: kein Tag, den `1s-abdeckung.csv` als geholt protokolliert
und zu dem die Parquet-Datei fehlt. Kein stiller Datenverlust.

Wo TradingView-1m denselben Tag abdeckt (14 Tage), wurde 1s dagegen gegengerechnet — bei je
1380 verglichenen Minuten ≤ 7 ungleiche Minuten, größte Abweichung **2,0 Punkte (30.07.)**,
sonst ≤ 1,75:

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

Beide Quellen bestätigen sich — die Level unten sind belastbar.

### Offene Gaps — die DOL-Kandidaten

| Level | Datum | Close (17:00) | Open (18:00) | Gap | C.E. | Status |
|---|---|---|---|---|---|---|
| **NWOG** | So 02.08. (Close Fr 31.07.) | 28287.00 | 28565.00 | **+278.00** | **28426.00** | **offen** |

Genau **ein** offener Gap im ganzen Fenster. Alle 18 NDOGs und die drei übrigen NWOGs sind
gefüllt.

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

### NDOG der auslaufenden Woche (KW34)

| Level | Datum | Close (17:00) | Open (18:00) | Gap | C.E. | Status |
| --- | --- | --- | --- | --- | --- | --- |
| NDOG | Mo 17.08. | 30078.25 | 30077.00 | −1.25 | 30077.50 | gefüllt |
| NDOG | Di 18.08. | 29559.50 | 29566.50 | +7.00 | 29563.00 | gefüllt |
| NDOG | Mi 19.08. | 29561.00 | 29561.50 | +0.50 | 29561.25 | gefüllt |
| NDOG | Do 20.08. | 29317.25 | 29327.00 | +9.75 | 29322.00 | gefüllt |

Vier NDOGs, alle im einstelligen bis niedrig zweistelligen Bereich und sämtlich noch am selben
Tag gefüllt — die auslaufende Woche hat keine offene Tageslücke hinterlassen.

### Range der auslaufenden Woche (KW34)

`letzte_woche` aus `bias_levels.py` ist **`null`** — die 1d-Reihe für NQ enthält die laufende
Woche noch nicht. Die Range ist deshalb direkt aus den **1s-Daten** nachgerechnet
(Handelstag = 18:00 NY Vortag → 16:59:59 NY), diesmal **vollständig Mo–Fr**:

| Tag | High | Low | Close |
| --- | --- | --- | --- |
| Mo 17.08. | 30343.00 | 30054.50 | 30078.25 |
| Di 18.08. | 30121.25 | 29514.00 | 29559.50 |
| Mi 19.08. | 29757.25 | 29375.75 | 29561.00 |
| Do 20.08. | 29689.75 | 29202.75 | 29317.25 |
| Fr 21.08. | 29539.00 | 29220.00 | **29374.00** |

**Wochen-High 30343.00 (Mo), Wochen-Low 29202.75 (Do), Wochen-Close 29374.00** — Spanne
1140.25 Punkte. Das High steht am Montag, das Low am Donnerstag: klassisches
Bearish-Wochenprofil nach [[Weekly Range Trading Model]], Freitag schließt im unteren Drittel.

**KW34-Range — Qs / Os / Hs**

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

Der Freitags-Close 29374.00 liegt zwischen O1 und O2, also tief im Discount der Vorwoche
(unteres Viertel).

## COT (Commercials vs. Large Specs)

Stand **18.08.2026** (CFTC-Report, Veröffentlichung Fr 21.08.), Abruf erfolgreich, kein
`cot.error`. Auswertung nach [[COT (Commitment of Traders) Data]]: **nur Commercials gegen
Large Speculators**, Small Specs bleiben außen vor. Signal = Position **gegen das EQ der
jeweiligen Lookback-Range**, nicht gegen die 0-Linie.

| Symbol | Stand | Commercials | Large Specs | 3M | 6M | 12M | 2Y | 4Y |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **NQ** | 18.08.2026 | −12.347 | −10.416 | bearish | bearish | **bullish** | **bullish** | bearish |
| **ES** | 18.08.2026 | −113.553 | −10.560 | bearish | bearish | bearish | bearish | bearish |

**NQ — Horizonte im Detail (`einig: false`):**

| Lookback | Low | EQ | High | Commercials | Signal |
| --- | --- | --- | --- | --- | --- |
| 3M (13 Reports) | −14.946 | **+1.264,5** | +17.475 | −12.347 | bearish |
| 6M (26) | −27.334 | **−4.929,5** | +17.475 | −12.347 | bearish |
| 12M (52) | −66.754 | **−24.639,5** | +17.475 | −12.347 | bullish |
| 2Y (104) | −66.754 | **−24.639,5** | +17.475 | −12.347 | bullish |
| 4Y (209) | −66.754 | **−11.708,5** | +43.337 | −12.347 | bearish |

⚠️ **Die NQ-Horizonte widersprechen sich (`einig: false`) — es gibt hier kein pauschales
COT-Urteil.** Kurzfristig (3M/6M) sitzen die Commercials unter dem EQ ihrer Range → bearish;
über 12M/2Y liegen sie deutlich *über* dem EQ → bullish. Der 4Y-Wert ist praktisch neutral:
−12.347 gegen ein EQ von −11.708,5 sind 638 Kontrakte Abstand in einer Range von 110.091 —
das ist Rauschen, kein Signal. Wer eine Richtung aus dem NQ-COT ableiten will, muss den
Lookback ausdrücklich benennen. Für eine einzelne Handelswoche ist der **3M-Lookback** der
sachnähere: dort stehen die Commercials unter EQ, also **leicht bearish**.

**ES — Horizonte im Detail (`einig: true`):**

| Lookback | Low | EQ | High | Commercials | Signal |
| --- | --- | --- | --- | --- | --- |
| 3M (13) | −142.440 | **−16.183,0** | +110.074 | −113.553 | bearish |
| 6M (26) | −142.440 | **−16.183,0** | +110.074 | −113.553 | bearish |
| 12M (52) | −142.440 | **−4.210,5** | +134.019 | −113.553 | bearish |
| 2Y (104) | −233.202 | **−49.591,5** | +134.019 | −113.553 | bearish |
| 4Y (209) | −233.202 | **+101.178,0** | +435.558 | −113.553 | bearish |

**ES ist über alle fünf Horizonte einig bearish** und dabei nicht knapp: −113.553 liegt im
3M/6M-Fenster nahe am unteren Extrem (Low −142.440), also im deutlichen Short-Bereich der
eigenen Range. Das ist das klarere der beiden Bilder.

**`gegenlaeufig: false` in beiden Symbolen.** Commercials und Large Specs stehen jeweils auf
**derselben Seite** — beide netto short (NQ −12.347 / −10.416, ES −113.553 / −10.560). Die
Konstellation, auf die ICT eigentlich abstellt (Commercials gegen Large Specs), liegt diese
Woche also **nicht** vor. Damit fehlt dem COT-Bild sein schärfstes Element; es taugt hier als
Hintergrundfärbung, nicht als Trigger.

## Wiki-Bezug

- [[Weekly Range Trading Model]] — Wochenprofil, welcher Tag High/Low setzt. KW34 hat das High
  am Montag und das Low am Donnerstag gesetzt; für KW35 ist die Frage, ob sich das wiederholt.
- [[IPDA Data Ranges]] — übergeordneter Datenbereich, in dem KW35 liegt.
- [[COT (Commitment of Traders) Data]] — EQ-Lesart der Lookback-Range, siehe COT-Abschnitt.
- [[Seasonal Tendency]] — Wochentags- und Week-of-Month-Muster, siehe Einschätzung.
- [[New Week Opening Gap (NWOG) Bias]] — zum offenen NWOG vom 02.08.
- [[New Day Opening Gap (NDOG)]] — zur NDOG-Tabelle.
- [[Using Monthly & Weekly Ranges (Source)]] — KW35 ist die letzte volle Augustwoche, der
  Monatswechsel fällt auf Mo 31.08./Di 01.09.

## Einschaetzung (Claude)

**Datenbasis diese Woche vollständig.** News (ForexFactory, 10 Termine), COT (CFTC, Stand
18.08.) und Level (NQ 1s, 24/24 Tage) liegen alle vor — anders als in der Vorfassung dieser
Datei, in der News und COT netzwerkbedingt fehlten.

**Saisonalität** aus `algo/seasonal_tendency.json` (n=1882 Tage, 06.05.2019–14.08.2026, Symbol
**MNQ** — für die *Richtungs*-Statistik derselbe Index wie NQ, Punktangaben sind 1:1
übertragbar, nur die Kontraktgröße unterscheidet sich):

- **Woche 4 im Monat** (Tage 22.–28., trifft auf KW35 mit 24.–28.08. exakt zu): **57,0 %
  bullish**, n=428, avg +0,079 % — die stärkste der fünf Wochenklassen.
- **Montag ist mit 61,4 % bullish** (n=376, avg +0,194 %) der stärkste Einzelwochentag des
  Datensatzes. Mittwoch folgt mit 55,3 %; **Donnerstag ist der einzige Tag mit negativer
  Durchschnittsrendite** (52,1 % bullish, avg −0,012 %).
- **Kein Turn-of-Month-Effekt in KW35.** Das TOM-Fenster ist im Code als „letzter Handelstag
  des Monats + erste 3 des Folgemonats" definiert; der letzte Augusttag ist Mo **31.08.**,
  liegt also in KW36. Ohnehin ist der Effekt vernachlässigbar (Fenster 53,6 % vs. Rest
  54,3 % bullish).

**Wochenrichtung: leicht bullish, mit niedriger Konfidenz.** Die Saisonalität zeigt in beiden
relevanten Dimensionen (Woche 4, Montag) nach oben, aber die Effektgrößen liegen unter 0,2 %
Tagesrendite — statistische Kanten, kein Handelssignal für sich. Dagegen steht ein COT-Bild,
das im ES über alle Horizonte bearish liest und im NQ kurzfristig (3M/6M) ebenfalls, und eine
auslaufende Woche, die nahe ihrem Tief geschlossen hat (Close 29374.00 im unteren Viertel der
KW34-Range). **Netto: kein klarer Wochenbias.** Wenn ich mich festlegen muss: frühe
Wochenstärke (Montag-Statistik, Woche-4-Statistik) in ein Umfeld, das ab Mittwoch von Core PCE
bestimmt wird — also eher ein Kauf der ersten Tage gegen die KW34-Discount-Level als eine
durchgehende Wochenrichtung. **Wahrscheinlichkeit ~55 %, also kaum über Münzwurf.**

**Die entscheidende Struktur ist nicht die Richtung, sondern der Kalender.** Mi 14:30 DE
(Core PCE + Prelim GDP gleichzeitig) und Fr 16:00 DE (Warsh + Payrolls-Revision) sind die
beiden Punkte, an denen die Woche ihre Range macht. Mo/Di sind newsarm — dort ist das
Wochenprofil formbar, ab Mittwoch bestimmt die Zahl.

**NWOG-Einschränkung, unverändert gültig.** `algo/backtest_nwog.py` misst eine
Bias-intakt-Quote von nur **7 %**. Das offene NWOG vom 02.08. (C.E. **28426.00**) ist damit
ein **Level** — ein DOL-Kandidat —, **kein Richtungsfilter**. Es liegt rund **948 Punkte
unter** dem Freitags-Close von 29374.00; als Wochenziel für KW35 ist das weit, aber es ist der
einzige unerledigte Gap im Fenster und bleibt damit der übergeordnete Downside-Magnet.

**Näher liegende Level für die Woche:** die KW34-Quadranten oben. C.E. der Vorwoche steht bei
**29773.00** — solange NQ darunter handelt, bleibt die Vorwoche im Discount und ein Retest der
29487.75 (Q1) bzw. des Wochen-Lows 29202.75 ist der wahrscheinlichere Weg als ein Ausbruch
über 30058.00 (Q3).

**Keine NFP-Woche** — `algo/backtest_nfp_week.py` ist nicht einschlägig, NFP ist der 04.09.

## Mein Bias

Viele News wird also eine volatile Woche vergangeen WOche waren wir antizipiert Baerish was auch COT Daten nachweisen. Durch den schnellen und enorm starken Aufbau von Baerishen Positionen bin ich auch diese Woche weiterhin Baerish.
Weekly Chart haben wir das C.E des Daily BISI berührt und drüber geclosed ebenso das Weekly BISI nicht das C.E getroffen aber kurz davor. Montag erwarte ich Bullishes Retracement höchstens bis zum SIBI C.E vom 18.08. VII zwischen 31.07 und 01.08 ist ein gutes Target für diese Woche. Innerhalb der VII ist ein NWOG das nehme ich als DOL. Ich bin BAerish und erwarte ein MMSM Model den COT drückt Price enorm runter. Im ES sieht es genauso aus.
