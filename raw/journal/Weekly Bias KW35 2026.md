# Weekly Bias KW35 2026

*(Mo 24.08. – Fr 28.08.2026, erzeugt am 21.08.2026 durch `/bias-vorlage-weekly`, Cloud-Session)*

## News (Red/Orange Folder), ganze Woche

⚠️ **News-Abruf komplett fehlgeschlagen** — nicht der übliche Freitagabend-Fall (ForexFactory
kennt die Zielwoche noch nicht, TradingView springt ein), sondern beide Quellen sind in dieser
Cloud-Session gar nicht erreichbar: Das Netzwerk-Proxy-Gateway dieser Session lehnt den
CONNECT-Tunnel zu `nfs.faireconomy.media` (ForexFactory-Feed), `economic-calendar.tradingview.com`
und `cftc.gov` mit HTTP 403 ab (Policy-Sperre des Sandbox-Proxys, kein Seitenfehler). `bias_levels.py`
meldet entsprechend `news.source: tradingview` mit `news.error` gesetzt
(`URLError: <urlopen error Tunnel connection failed: 403 Forbidden>`).

**Keine Termine erfunden.** Bitte KW35 (24.–28.08.) manuell auf forexfactory.com prüfen, bevor
die Woche gehandelt wird — insbesondere Mittwoch/Donnerstag, wo in den letzten Wochen die
Taktgeber lagen.

**Ein Datum lässt sich aber ohne Kalenderabruf einordnen:** NFP fällt regelmäßig auf den ersten
Freitag des Monats — im September also auf den 04.09., **nicht** in KW35. Das ist allgemeines
Kalenderwissen, keine aus dem (fehlgeschlagenen) Feed gezogene Aussage.

## Levels

Gerechnet aus `raw/marktdaten/` (**NQ**, kein MNQ-Rückfall nötig). Alle Preise auf dem
0,25-Tickraster.

**Datenlage (1s bevorzugt):** 23 der 24 Tage im Fenster (17.07.–19.08.) liegen als **1s** vor,
0 Tage nur als 1m. `1s-abdeckung.csv` protokolliert für dieses Fenster **keinen** Tag, zu dem die
Parquet-Datei fehlt — Register und Bestand decken sich, kein stiller Datenverlust.

Wo beide Quellen denselben Tag abdecken (14 Tage), wurde 1s gegen den TradingView-1m-Export
gegengerechnet — größte Abweichung 2,0 Ticks (30.07.), meist ≤ 1 Tick:

| Tag | verglichene Minuten | ungleich | max. Abweichung |
|---|---|---|---|
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

Beide Quellen bestätigen sich weitgehend gegenseitig — die Level unten sind damit belastbar.

### Offene Gaps — die DOL-Kandidaten

| Typ | Datum | Close (17:00) | Open (18:00) | Gap | C.E. | Spanne |
|---|---|---|---|---|---|---|
| **NWOG** | Fr 31.07. → So 02.08. | 28287.00 | 28565.00 | **+278.00** | **28426.00** | 278.00 |

Der einzige noch offene Gap im Fenster ist das NWOG vom 02.08. — alle NDOGs und die übrigen
NWOGs der letzten Wochen sind bereits gefüllt.

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

### NWOG der letzten Wochen

| Datum | Close (Fr 17:00) | Open (So 18:00) | Gap | C.E. | Status |
|---|---|---|---|---|---|
| So 16.08. | 30154.00 | 30170.00 | +16.00 | 30162.00 | gefüllt |
| So 09.08. | 29839.50 | 29851.25 | +11.75 | 29845.50 | gefüllt |
| So 26.07. | 28306.50 | 28500.00 | +193.50 | 28403.25 | gefüllt |
| So 19.07. | 28768.25 | 28747.75 | −20.50 | 28758.00 | gefüllt |

### NDOG der auslaufenden Woche (KW34)

| Datum | Close (17:00) | Open (18:00) | Gap | C.E. | Status |
|---|---|---|---|---|---|
| Mo 17.08. | 30078.25 | 30077.00 | −1.25 | 30077.50 | gefüllt |
| Di 18.08. | 29559.50 | 29566.50 | +7.00 | 29563.00 | gefüllt |

Nur zwei NDOG-Einträge für KW34 — die 1s-Daten decken im aktuellen Bestand nur bis
**19.08.** ab (siehe Datenlage oben), Mi–Fr der auslaufenden Woche fehlen dem Gap-Rechner
dafür noch die nötigen Randdaten. Kein fehlender Tag ist dabei als „geholt, aber Datei fehlt"
(`registriert_ohne_datei`) protokolliert — es ist schlicht noch nicht so weit nachgezogen.

### Range der auslaufenden Woche (KW34)

`letzte_woche` aus `bias_levels.py` ist **`null`** — die 1d-Reihe für NQ enthält die laufende
Woche noch nicht (dasselbe bekannte Problem wie im Code-Kommentar zu `intraday_range()`
dokumentiert: die 1d-Datei hinkt hinterher bzw. fehlt für aktuelle Tage teils ganz).

Aus den **Intraday-1s-Daten** lässt sich die Woche aber immerhin bis Mittwoch nachrechnen
(Do 20.08. und Fr 21.08. fehlen den Daten noch):

| Tag | High | Low | Close |
|---|---|---|---|
| Mo 17.08. | 30343.00 | 30054.50 | 30078.25 |
| Di 18.08. | 30121.25 | 29514.00 | 29559.50 |
| Mi 19.08. | 29757.25 | 29375.75 | 29561.00 |

⚠️ **Unvollständig** — High/Low von Do 20.08. und Fr 21.08. fehlen, die echte Wochenrange kann
also noch tiefer/höher liegen. Bislang (Mo–Mi): High **30343.00** (Mo), Low **29375.75** (Mi).

## COT (Commercials vs. Large Specs)

⚠️ **COT-Abruf fehlgeschlagen** — derselbe Proxy-Grund wie beim News-Abruf: das Sandbox-Gateway
lehnt den CONNECT-Tunnel zu `cftc.gov` mit HTTP 403 ab
(`ProxyError: HTTPSConnectionPool(host='cftc.gov', port=443): Max retries exceeded with url:
/files/dea/history/deacot2022.zip (... Tunnel connection failed: 403 Forbidden)`).

Keine Zahlen erfunden. Letzter bekannter Stand ist der Report aus KW34 (siehe
`raw/journal/Weekly Bias KW34 2026.md`): NQ-Commercials netto long über alle Horizonte, ES
netto short über alle Horizonte, beide gegenläufig zueinander — dieser Stand ist aber
**mindestens eine Woche alt** und sollte vor dem Handeln der KW35 manuell nachgezogen werden
(`cot.gov` oder `algo/cot.py` auf einem Rechner mit freiem Netzzugang).

## Wiki-Bezug

- [[Weekly Range Trading Model]] — Wochenstruktur, welcher Tag High/Low setzt
- [[IPDA Data Ranges]] — übergeordneter Datenbereich, in dem KW35 liegt
- [[COT (Commitment of Traders) Data]] — EQ-Lesart der Lookback-Range; diese Woche ohne
  frischen Report (siehe COT-Abschnitt)
- [[Seasonal Tendency]] — Wochentags- und Week-of-Month-Muster, siehe Einschätzung unten
- [[New Day Opening Gap (NDOG)]] — für die NDOG-Tabelle oben

## Einschätzung (Claude)

**Datenbasis diese Woche schwächer als sonst.** News und COT konnten in dieser Cloud-Session
gar nicht abgerufen werden (Proxy-Sperre, siehe oben), nicht nur „ForexFactory kennt die Woche
noch nicht". Diese Einschätzung stützt sich deshalb nur auf Level-Struktur und Saisonalität —
beide sind aus echten Marktdaten gerechnet, aber ohne News- und COT-Bestätigung ist die
Aussage schwächer abgesichert als in den Vorwochen.

**Saisonalität, ehrlich eingeordnet.** Aus `algo/seasonal_tendency.json` (n=1882 Tage,
17.05.2019–14.08.2026):

- KW35 ist die **vierte Woche des Monats** (Wochen mit Start Mo 22.–28. des Monats):
  **57,0 % bullish** (n=428, avg +0,079 %) — nach Woche 1 (56,5 %) die zweitstärkste
  Wochenklasse.
- **Montag ist mit 61,4 % bullish** (n=376, avg +0,194 %) der stärkste Einzelwochentag im
  gesamten Datensatz.
- **Kein Turn-of-Month-Effekt** — das TOM-Fenster liegt um den Monatswechsel (Ende
  August/Anfang September), KW35 (24.–28.08.) liegt noch davor.

Woche-4-Bias und Montag-Bias zeigen beide leicht bullish — beides sind aber moderate,
statistische Kanten (n groß, aber Effektgröße unter 0,2 %), kein Handelssignal für sich allein.

**NWOG-Einschränkung, unverändert gültig.** `algo/backtest_nwog.py` misst laut Projektstandard
eine Bias-intakt-Quote von nur **7 %** — das offene NWOG vom 02.08. (C.E. 28426.00) taugt als
**Level** (DOL-Kandidat, ca. 1650 Punkte unter dem letzten bekannten Print von 29561.00),
nicht als Richtungsfilter.

**NFP-Woche: nein.** Der erste Freitag im September (NFP-Termin) ist der 04.09. — KW35 ist
also keine NFP-Woche, `algo/backtest_nfp_week.py` ist damit nicht einschlägig.

**Kein Wochenziel ableitbar.** Ohne News- und COT-Bestätigung, mit nur einer moderaten
saisonalen Kante und einem weit entfernten offenen Gap lässt sich aus den verfügbaren Daten
kein belastbares KW35-Ziel benennen. Vor dem Handeln der Woche unbedingt News (ForexFactory)
und COT (aktueller CFTC-Report, Stand Di 18.08., Veröffentlichung Fr 21.08.) manuell
nachziehen.

## Mein Bias
