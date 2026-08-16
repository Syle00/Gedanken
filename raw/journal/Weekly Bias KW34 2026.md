# Weekly Bias KW34 2026

*(Mo 17.08. – Fr 21.08.2026, erzeugt am 15.08.2026 durch `/bias-vorlage-weekly`)*

## News (Red/Orange Folder), ganze Woche

Quelle: **TradingView-Wirtschaftskalender** (`news.source: tradingview`) — ForexFactory
veröffentlicht nur die laufende Woche und kennt KW34 am Freitag/Samstag noch nicht.
TradingView stuft mehr Events als Red ein als ForexFactory; die Uhrzeiten beider Quellen sind
gegengeprüft und deckungsgleich. Nur US-Termine.

| Tag | NY | DE | Event | Impact | Forecast | Previous |
|---|---|---|---|---|---|---|
| Mo 17.08. | 08:30 | 14:30 | NY Empire State Manufacturing Index | Orange | 10.2 | 15.6 |
| Mo 17.08. | 10:00 | 16:00 | NAHB Housing Market Index | Orange | 33 | 34 |
| Mo 17.08. | 16:00 | 22:00 | Net Long-term TIC Flows | Orange | – | 232.7 |
| Di 18.08. | 08:15 | 14:15 | ADP Employment Change Weekly | Orange | – | 8.25 |
| Di 18.08. | 08:30 | 14:30 | **Housing Starts** | **Red** | 1.35 | 1.427 |
| Di 18.08. | 08:30 | 14:30 | **Building Permits Prel** | **Red** | 1.37 | 1.374 |
| Di 18.08. | 08:30 | 14:30 | Housing Starts MoM | Orange | – | 19 |
| Di 18.08. | 08:30 | 14:30 | Building Permits MoM Prel | Orange | – | -2.6 |
| Di 18.08. | 08:30 | 14:30 | Import Prices MoM | Orange | 0.1 | 0.3 |
| Di 18.08. | 08:30 | 14:30 | Export Prices MoM | Orange | -0.2 | -0.6 |
| Di 18.08. | 09:15 | 15:15 | Industrial Production MoM | Orange | 0.3 | 0.1 |
| Di 18.08. | 10:00 | 16:00 | Pending Home Sales MoM | Orange | 0.5 | -5.4 |
| Di 18.08. | 10:00 | 16:00 | Pending Home Sales YoY | Orange | – | -0.3 |
| Di 18.08. | 16:30 | 22:30 | API Crude Oil Stock Change | Orange | – | 9.072 |
| Mi 19.08. | 07:00 | 13:00 | MBA 30-Year Mortgage Rate | Orange | – | 6.77 |
| Mi 19.08. | 10:30 | 16:30 | EIA Crude Oil Stocks Change | Orange | – | 17.422 |
| Mi 19.08. | 10:30 | 16:30 | EIA Gasoline Stocks Change | Orange | – | -0.968 |
| **Mi 19.08.** | **14:00** | **20:00** | **FOMC Minutes** | **Red** | – | – |
| Do 20.08. | 08:30 | 14:30 | Initial Jobless Claims | Orange | 210 | 209 |
| Do 20.08. | 08:30 | 14:30 | Philadelphia Fed Manufacturing Index | Orange | 25.3 | 41.4 |
| Fr 21.08. | 09:45 | 15:45 | S&P Global Services PMI Flash | Orange | 53.9 | 54.6 |
| Fr 21.08. | 09:45 | 15:45 | S&P Global Manufacturing PMI Flash | Orange | 53.7 | 53.9 |
| Fr 21.08. | 09:45 | 15:45 | S&P Global Composite PMI Flash | Orange | – | 54.5 |

**Der Wochentermin ist FOMC Minutes am Mittwoch 14:00 NY / 20:00 DE.** Das ist ein
Nachmittagstermin — anders als CPI/PPI, die vor dem Open liegen und die Range des ganzen Tages
prägen. Zweitwichtigster Block: Dienstag 08:30 NY (Housing Starts + Building Permits gebündelt).
Montag und Donnerstag sind newsseitig ruhig.

## Levels

⚠️ **Live-Daten nicht verfügbar** — `algo/live_status.py` meldet am Samstag `market_data: false`
(„keine 5m-Daten, Markt geschlossen"). NWOG (Freitag-Close vs. Montag-Open) lässt sich erst
Sonntagabend nach dem Globex-Open bestimmen. Die NWOG-Zeile bleibt bis dahin offen:

| Level | Open | Close |
|---|---|---|
| NWOG (KW34) | _(offen bis So 18:00 NY)_ | 30154.75 _(letzter 1m-Print Fr 16:59 NY)_ |

**Range der auslaufenden Woche (KW33):**

| | Wert |
|---|---|
| High | 30287.25 |
| Low | 29533.5 |
| Spanne | 753.75 Punkte |
| Handelstage | 5 (10.–14.08.) |

> ⚠️ **Korrigierter Wert, nicht der aus `raw/marktdaten/`.** Die 1d-Datei für den 14.08.
> (`MNQ 2026-08-14 1d.csv`) ist ein zu früh gezogener Snapshot: sie meldet High 30232.5 /
> Low 30124.25 = 108,25 Punkte Tagesrange, während die 1m-Daten desselben Tages 30287.25 /
> 30025.0 = 262,25 Punkte zeigen — **154 Punkte unterschlagen**. Die Tabelle oben nutzt die
> 1m-Werte. Ohne die Korrektur stünde hier ein Wochen-High von 30273.25, also 14 Punkte zu
> niedrig. Betroffen ist nur dieser eine Tag (alle anderen 1d-Dateien im Bestand geprüft).
> Siehe Bericht unten — die 1d-Datei sollte nachgezogen werden.

**Vortageswerte (Fr 14.08., aus den 1m-Daten):** Open 30213.0 / High 30287.25 / Low 30025.0 /
letzter Print 30154.75 (16:59 NY — die Settlement-Minute 17:00 fehlt im Export).

## Wiki-Bezug

- [[Weekly Range Trading Model]] — Wochenstruktur, welcher Tag das Wochen-High/-Low setzt
- [[IPDA Data Ranges]] — übergeordneter Datenbereich, in dem KW34 liegt
- [[New Day Opening Gap (NDOG)]] — für das NWOG am Sonntagabend
- [[Two Stage News Delivery (FOMC & NFP)]] — direkt einschlägig für Mittwoch: FOMC-Termine
  liefern laut dieser Seite typischerweise in zwei Stufen, nicht in einer Bewegung

## Einschätzung (Claude)

**Struktur der Woche.** Der einzige echte Taktgeber ist Mittwoch 14:00 NY (FOMC Minutes).
Damit fällt der Wochen-Schwerpunkt in die zweite Wochenhälfte — Montag und Dienstag sind
newsarm genug, dass die Woche ihre Richtung eher aus der Struktur als aus Daten nimmt.
Für Mittwoch ist [[Two Stage News Delivery (FOMC & NFP)]] die relevante Erwartung: erste
Reaktion direkt auf 14:00, die eigentliche Auflösung eher danach — keine einzelne Bewegung.

**Montag (Wochenstart), statistisch.** `algo/seasonal_tendency.json`: Montag ist mit
**61,4 % bullish** (n=376) der klar stärkste Wochentag im MNQ-Bestand, avg. Return +0,194 %,
Median-Range 263,88 Punkte. Das ist die stärkste Wochentagsabweichung in der ganzen Tabelle
(Di 50,5 %, Mi 55,3 %, Do 52,1 %, Fr 51,6 %) und die einzige, die deutlich aus dem Rauschen
läuft.

**NWOG-Einschränkung.** Sobald das NWOG Sonntagabend steht, gilt der empirische Befund aus
`algo/backtest_nwog.py`: die **Bias-intakt-Quote liegt bei nur 7 %** — die meisten Wochen
durchbrechen ihr NWOG irgendwann wieder, auch nach Montag. Eine NWOG-basierte
Wochenrichtungsaussage ist damit schwach; das NWOG taugt besser als Level (DOL-Kandidat) denn
als Richtungsfilter.

**Ausgangslage.** KW33 schloss bei 30154.75 und damit im unteren Drittel ihrer eigenen Range
(29533.5–30287.25). Das Wochen-High vom Freitag (30287.25) liegt nur ~130 Punkte über dem
Schlusskurs und ist damit der nächstliegende Liquiditätspunkt nach oben.

**Kein Turn-of-Month.** KW34 liegt in der Monatsmitte, die Turn-of-Month-Kennzahlen aus
`seasonal_tendency.json` greifen hier nicht.

## Mein Bias

