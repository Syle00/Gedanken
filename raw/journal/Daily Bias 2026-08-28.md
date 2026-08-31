# Daily Bias 2026-08-28

> Weekly Bias: [[Weekly Bias KW35 2026]]
> Freitag, KW 35

## News (Red/Orange Folder)

⚠️ News-Abruf fehlgeschlagen (`URLError: <urlopen error Tunnel connection failed: 403 Forbidden>`),
manuell auf forexfactory.com prüfen. Sowohl ForexFactory (`nfs.faireconomy.media`) als auch der
TradingView-Fallback (`economic-calendar.tradingview.com`) wurden vom Netzwerk-Proxy dieser
Cloud-Session mit HTTP 403 abgewiesen (Egress-Policy-Ablehnung, kein transienter Fehler — siehe
`/root/.ccr/README.md`, Abschnitt „403 / 407 from the proxy"). Beide Hosts sind für diese Session
nicht freigegeben.

Bereits verifizierte Fr-28.08.-Termine stehen in [[Weekly Bias KW35 2026]] (Quelle
`forexfactory`, `news.error: null`, abgerufen 23.08.2026 aus einer Session mit Netzzugang) —
zur Sicherheit trotzdem gegen forexfactory.com gegenprüfen, falls sich der Kalender seither
geändert hat:

🔴 **10:00 NY** / 16:00 DE — Fed Chairman Warsh Speaks

🔴 **10:00 NY** / 16:00 DE — Prelim Benchmark Payrolls Revision (Previous −911K)

🟠 **10:00 NY** / 16:00 DE — Revised UoM Consumer Sentiment (Forecast 51.0, Previous 51.0)

🟠 **10:00 NY** / 16:00 DE — Revised UoM Inflation Expectations (Previous 4.3%)

## Levels

**Datenlage:** 21 Handelstage mit 1s-Daten (2026-07-24 – 2026-08-21), kein Tag nur auf 1m,
keine in `1s-abdeckung.csv` registrierten Tage ohne Datei. Abgleich 1s gegen TradingView-1m:
max. Abweichung 2,50 Punkte (2026-08-20), sonst ≤ 2,00 — unauffällig. Symbol: NQ.

⚠️ **Lücke, aktiv:** Die 1s-Daten enden am 21.08. (Fr, KW34). Für die **gesamte laufende Woche
KW35 (Mo 24.08. – Do 27.08.)** liegen noch keine Marktdaten vor — weder in `raw/marktdaten/`
noch als frischer Git-Commit (letzter marktdatenrelevanter Commit: 23.08.). Deshalb sind Weekly
Range, ein aktueller Live-Preis und ein heutiges ORG-C.E. **nicht berechenbar**; die Tabelle
unten zeigt ausschließlich Level aus der Zeit bis 21.08. `live_status.py` bestätigt das separat
(`market_data: false`, IBKR-Gateway nicht erreichbar, `ib_async` fehlt in dieser Cloud-Session).

| Level | Datum | Close (17:00) | Open (18:00) | Gap | C.E. | Status |
|---|---|---|---|---|---|---|
| NWOG | 2026-08-02 | 28287,00 | 28565,00 | +278,00 | 28426,00 | **offen** |
| NDOG | 2026-08-20 | 29317,25 | 29327,00 | +9,75 | 29322,00 | gefüllt |
| NDOG | 2026-08-19 | 29561,00 | 29561,50 | +0,50 | 29561,25 | gefüllt |
| NDOG | 2026-08-18 | 29559,50 | 29566,50 | +7,00 | 29563,00 | gefüllt |
| NDOG | 2026-08-17 | 30078,25 | 30077,00 | −1,25 | 30077,50 | gefüllt |
| NWOG | 2026-08-16 | 30154,00 | 30170,00 | +16,00 | 30162,00 | gefüllt |
| NDOG | 2026-08-13 | 30214,25 | 30210,75 | −3,50 | 30212,50 | gefüllt |
| NDOG | 2026-08-12 | 29805,75 | 29825,00 | +19,25 | 29815,50 | gefüllt |
| NDOG | 2026-08-11 | 29646,75 | 29657,75 | +11,00 | 29652,25 | gefüllt |
| NDOG | 2026-08-10 | 29764,25 | 29764,50 | +0,25 | 29764,50 | gefüllt |

**Letzter verfügbarer Daily-Bar** (2026-08-13, Quelle 1d — nicht „gestern", siehe Lücke oben):
H 30272,75 / L 29780,50 / C 30188,50

_Weekly Range: keine Daten — Zeile ausgelassen (siehe Lücke oben)._

### Offenes Gap — NWOG 2026-08-02 (Qs/Os/Hs)

Spanne 278,00 Punkte, Close 28287,00 (2026-07-31 16:59:59) → Open 28565,00 (2026-08-02 18:00:00).

| | Level |
|---|---|
| High (Open) | 28565,00 |
| O7 | 28530,25 |
| O6 / Q3 | 28495,50 |
| O5 | 28460,75 |
| **C.E. (= H1 = Q2 = O4)** | **28426,00** |
| O3 | 28391,25 |
| O2 / Q1 | 28356,50 |
| O1 | 28321,75 |
| Low (Close) | 28287,00 |

## Wiki-Bezug

- [[Weekly Range Trading Model]] — übergeordneter Rahmen für den Wochenabschluss
- [[TGIF (Thank God its Friday)]] — Freitags-Setup par excellence: Retracement in die
  20–30-%-Zone der Weekly Range, PM Silver Bullet (14–15 Uhr NY); heute nicht quantifizierbar,
  da die Weekly Range wegen der Datenlücke fehlt (siehe Levels)
  — die Voraussetzung „Reaching into a Higher Timeframe PD Array" muss trotzdem zuerst geprüft
  werden, bevor das Setup gilt
- [[ICT Daily Range Session Timing]]
- [[Midnight Opening Range]]
- [[ORG (Opening Range Gap) & 1st Presented FVG]]
- [[New Day Opening Gap (NDOG)]]
- [[New Week Opening Gap (NWOG) Bias]] — für das offene 278-Punkte-Gap vom 2026-08-02
- [[Average Daily Range (5-Tage-ADR)]]

## Einschaetzung (Claude)

**Wochentag-Statistik (MNQ, n=372 Freitage, 2019-05-06 – 2026-08-14, Quelle
`algo/seasonal_tendency.json`):** bullish 51,6 %, Ø-Return +0,013 %, Median-Range 245,12 Punkte,
Ø-Range 299,67 Punkte. Freitag ist damit sowohl richtungslos (praktisch Münzwurf) als auch der
Wochentag mit der **kleinsten** Median-Range aller fünf Tage — ein Kontrast zu Donnerstag
(größte Median-Range, siehe gestriger Bericht). Aus der reinen Saisonalität kommt heute also
kein Edge, weder Richtung noch Bewegungsgröße.

**News:** Zwei Red-Folder-Termine fallen **zeitgleich auf 10:00 NY / 16:00 DE** — Fed Chairman
Warsh Speaks und die Prelim Benchmark Payrolls Revision (Previous −911K, also potenziell eine
große Korrektur der Beschäftigungsbasis), dazu zwei Orange-Folder-UoM-Revisionen zur selben
Zeit. Das bündelt den News-getriebenen Teil des Tages fast vollständig in ein einziges Fenster;
vorher (AM Session bis 10:00 NY) ist strukturell freier handelbar, danach ist mit einem breiten
Impuls zu rechnen. Diese Termine kommen aus [[Weekly Bias KW35 2026]] (verifiziert, forexfactory,
23.08.), nicht aus dem heutigen — blockierten — Abrufversuch; vor dem Handel gegen
forexfactory.com gegenprüfen.

**TGIF-Setup:** Freitag ist laut [[TGIF (Thank God its Friday)]] der Tag, an dem Preis
typischerweise in die 20–30-%-Zone der Weekly Range zurückläuft (Arbeitsziel ~25 %,
Backtest-Median eigener Daten 22,1 %, siehe [[Statistische Muster jenseits der ICT-Konzepte
(laufend)]]). Ohne Weekly-Range-Daten für KW35 (siehe Lücke oben) lässt sich das Ziel heute
nicht beziffern — sobald frische Daten vorliegen, zuerst Wochen-High/-Low nachtragen, dann die
Zielzone rechnen.

**Weekly Bias (unverändert, aus [[Weekly Bias KW35 2026]]):** Der Nutzer ist für KW35 explizit
bearish — begründet mit einem schnellen, starken Aufbau bearisher COT-Positionierung
(Commercials in NQ und ES beide netto short) und einem MMSM-Modell (Market Maker Sell Model).
Zielzone: eine VII zwischen 31.07. und 01.08., darin das offene NWOG vom 02.08. (C.E. 28426,00)
als DOL. Das Claude-Einschätzung der Weekly-Bias-Datei selbst sah dagegen nur eine schwache,
niedrig-konfidente Tendenz (~55 % bullish für die erste Wochenhälfte, aus Saisonalität) bei
klar bearishem COT-Hintergrund — die beiden Bilder widersprechen sich in der Richtung, nicht
in den zugrundeliegenden Daten. Ohne Preisdaten für Mo–Do dieser Woche lässt sich von hier aus
nicht sagen, welches Bild bisher trägt.

**Offenes NWOG 2026-08-02 (28287,00–28565,00, C.E. 28426,00):** weiterhin das einzige offene
Gap im Fenster und laut Nutzer-Bias das Wochenziel. Abstand zum zuletzt bekannten Preis lässt
sich wegen der Datenlücke nicht seriös beziffern (der letzte Daily-Bar ist zwei Wochen alt) —
vor dem Handel den tatsächlichen aktuellen Preis prüfen.

**ORG-C.E.:** Für diesen Lauf liegen keine Live-Marktdaten vor, also kein ORG-Level. Die
ORG-C.E.-70%-These bleibt als *laufend beobachtete* Hypothese offen — eigene Messungen liegen
bislang bei 35–43 % und damit deutlich unter der Lehrmeinung; laut Nutzerentscheid nicht als
widerlegt abgehakt, sondern weiter erhoben.

**Fazit:** Datenqualität für diesen Bericht deutlich eingeschränkt — kein Preis, keine Weekly
Range, News nur aus einer vier Tage alten Quelle nachgetragen. Der einzige belastbare Fahrplan
ist der Kalender: AM-Session bis 10:00 NY strukturell frei handelbar, danach zwei Red-Folder-
Events gebündelt. Der Nutzer-Bias bleibt bearish Richtung NWOG-C.E. 28426,00; vor jeder
Positionierung zuerst frische Daten (1s-Nachlad, `live_status.py`) ziehen und damit sowohl
Weekly Range als auch aktuellen Preis gegen die hier gelisteten, veralteten Level prüfen.

## Mein Bias

<!-- Jannes -->
