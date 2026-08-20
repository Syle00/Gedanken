# Daily Bias 2026-08-19

> Weekly Bias: [[Weekly Bias KW34 2026]]

## News (Red/Orange Folder)

**Mi 19.08.**

🔴 **14:00 NY** / 20:00 DE — FOMC Meeting Minutes

🟠 **14:30 NY** / 20:30 DE — President Trump Speaks

_Quelle: forexfactory (laufende FF-Woche), kein Abruf-Fehler._

## Levels

Symbol: NQ. Offene Gaps zuerst, danach die NDOGs der vergangenen Handelswoche.

| Level | Datum | Close (17:00) | Open (18:00) | Gap | C.E. | Status |
| --- | --- | --- | --- | --- | --- | --- |
| NWOG | 2026-08-02 | 28287.00 | 28565.00 | +278.00 | 28426.00 | **offen** |
| NWOG | 2026-08-16 | 30154.00 | 30170.00 | +16.00 | 30162.00 | gefüllt |
| NDOG | 2026-08-17 | 30078.25 | 30077.00 | -1.25 | 30077.50 | gefüllt |
| NDOG | 2026-08-13 | 30214.25 | 30210.75 | -3.50 | 30212.50 | gefüllt |
| NDOG | 2026-08-12 | 29805.75 | 29825.00 | +19.25 | 29815.50 | gefüllt |
| NDOG | 2026-08-11 | 29646.75 | 29657.75 | +11.00 | 29652.25 | gefüllt |
| NDOG | 2026-08-10 | 29764.25 | 29764.50 | +0.25 | 29764.50 | gefüllt |

**Weekly Range:** entfällt — für ISO-KW34 liegt keine abgeschlossene Range vor (die Woche
läuft, und der 18.08. ist in den Daten unvollständig, siehe Datenlage).

**Gestrige Daily Range (2026-08-18):** ⚠️ **unvollständig** — die 1s-Daten enden am 18.08. um
**09:05:39 NY**, die gesamte RTH-Session (09:30–16:00) und der 17:00-Close fehlen. Die Werte
High 30121.25 / Low 29680.50 / „Close" 29707.00 beschreiben nur das Fenster 17.08. 18:00 NY bis
18.08. 09:05 NY. **Nicht als Tages-H/L/C verwenden.** Letzter belastbarer Tagesschluss ist der
17.08. mit 30078.25.

**ORG-C.E.:** entfällt (`live_status.py` meldet `market_data: false`).

**Datenlage:** 24 Tage 1s (2026-07-15 – 2026-08-18), 0 Tage nur 1m, keine
`registriert_ohne_datei`-Einträge. 1s-vs-1m-Abgleich über 14 Tage unauffällig (max. 2.00 Pkt am
30.07. auf 7 von 1380 Minuten, sonst ≤ 1.75 Pkt) — beide Quellen tragfähig, kein
Level-Ausschluss. Einschränkung: der 18.08. ist nur bis 09:05 NY abgedeckt, obwohl im Register
als Tag geführt; deshalb fehlt auch der NDOG 2026-08-18.

### NWOG 2026-08-02 — offen (einziges offenes Gap)

Close 31.07. 16:59:59 NY = 28287.00 · Open 02.08. 18:00:00 NY = 28565.00 · Spanne 278.00 Pkt

| | Level |
| --- | --- |
| High (Open) | 28565.00 |
| O7 | 28530.25 |
| O6 / Q3 | 28495.50 |
| O5 | 28460.75 |
| **C.E. (= H1 = Q2 = O4)** | **28426.00** |
| O3 | 28391.25 |
| O2 / Q1 | 28356.50 |
| O1 | 28321.75 |
| Low (Close) | 28287.00 |

## Wiki-Bezug

- [[Weekly Range Trading Model]]
- [[ICT Daily Range Session Timing]]
- [[Midnight Opening Range]]
- [[ORG (Opening Range Gap) & 1st Presented FVG]]
- [[New Day Opening Gap (NDOG)]]
- [[New Week Opening Gap (NWOG) Bias]]
- [[Two Stage News Delivery (FOMC & NFP)]] — einschlägig für den 14:00-Termin
- [[FOMC (Federal Open Market Committee)]]

## Einschaetzung (Claude)

**Taktgeber ist FOMC Meeting Minutes, 14:00 NY**, direkt gefolgt von einem Trump-Auftritt um
14:30 NY. Nach [[Two Stage News Delivery (FOMC & NFP)]] ist die erste Reaktion auf die
Veröffentlichung typischerweise nicht die Auflösung — die kommt in einer zweiten Stufe danach.
Die beiden Termine liegen 30 Minuten auseinander und fallen damit beide in dieselbe
Nachmittagsphase; das erhöht das Risiko einer Fehlinterpretation der ersten Bewegung zusätzlich.
Ein quantifizierter Edge fehlt: `algo/backtest_fred_events.py` hat für FOMC-Releases bewusst
keinen Reaktionstest (im Datenfenster keine Zielsatzänderung, n=0) und deckt nur
VIX/DGS10/WALCL-Zusammenhänge ab — für heute also nur das Strukturmodell, keine eigene Statistik.

**Saisonalität** (`algo/seasonal_tendency.json`, MNQ, n=1882 Tage 2019-05-06 – 2026-08-14):
Mittwoch **55,3 % bullish** (n=376, avg +0,11 %), Median-Range **278,4 Pkt**. Leicht
überdurchschnittlich, aber kein tragfähiges Richtungssignal — vgl.
[[Seasonal Tendency (Eigene Daten, laufend)]].

**Level-Lage.** Der letzte belastbare Bezug ist der 17.08.-Close bei 30078.25; am 18.08. war der
Markt bis 09:05 NY bereits auf 29707.00 abverkauft (Tief 29680.50). Das einzige offene Gap,
NWOG 2026-08-02 mit C.E. 28426.00, liegt damit rund **1280 Punkte unter** dem zuletzt bekannten
Kurs. Es bleibt ein Sell-Side-Draw-Kandidat für den übergeordneten Zeitrahmen, ist aber
**kein realistisches Tagesziel** für Mittwoch (Median-Tagesrange 278 Pkt). Die relevanten
Intraday-Referenzen sind stattdessen der NDOG des laufenden Tages und die Midnight Opening
Range — beide erst nach Sessionbeginn bestimmbar.

**ORG-C.E.-These:** heute nicht prüfbar, da kein `org_ce` vorliegt. Die 70%-Hypothese bleibt
als laufend beobachtet stehen (empirisch bislang 35–43 %, nicht als widerlegt abgehakt).

**Was diese Einschätzung nicht leistet:** kein Kursziel, keine Richtungsprognose. Zusätzlich
eingeschränkt durch die fehlende 18.08.-RTH-Session — Vortages-High/Low und -Close, sonst die
Basis jeder Daily-Range-Projektion, sind für gestern nicht belastbar.

## Mein Bias

FOMC und Trump Rede sind High Impact weswegen wir kein NY PM traden werden.
Gestern haben wir einen stark Baerishen Tag gehabt was für meinen Weekly richtig wäre aber der Move runter schon früh kam anstatt mitte ende der Woche bereits am Dienstag.
Wir haben am Montag Buyside genommen und das SIBI vom 23.06 wunderbar respektiert immer unter dem C.E geclosed das wir mit den Wicks drüber gehen ist ok da die Wicks den Damage verursachen. (Ich muss rausfinden wiesp gerade die PD repektiert wurde) Liegt ja immer noch in der IPDA 40 Day Range bzw. genau drauf. Die Premium Wick 02.07 wurde ebenfalls genutzt.
Das Daily BISI vom 13.08 ist zum IFVG geworden bzw (wirklich IFVG?) das C.E oder Low wurde zuvor nicht genutzt also die Frage ob es wirklich ein IFVG ist.
Wir sind dabei ein Daily SIBI zu bilden wo oben eine VII bereits inkludiert ist wichtig ist wie wir heute closen werden da wir um die 30 Punkte tiefer geöffnet haben als gestern geclosed also wenn wir Baerish schließen erhalten wir ein Suspenblock Baerish

Wir haben ein 1h MMSM Model erhalten wwobei die originale consolidation von Mittwoch NY AM opening bis zur NY AM open Donnerstag open angehalten hat. Diese wurde dan als Target genommen.

Heute haben wir FOMC News znd die Trump rede und gehe davon aus das wir auf die News warten weshalb wir ewas komplziertere Price Action erhalten.
Nächstes Target wäre das Daily BISI wo wir bereits an dessen High traden c.E und Qs und das Weekly BISI c.E . Daily Low vom 06.08  bei 29,241,25 Sellside Liq.
Ich gehe also davon aus das wir BAerish sind zwecks News kann es sein das wir recht lange auf den Move warten aber dadurch sollte sich dan das Daily Suspensionblock bilden.

RTH das offene ORG Mittwoch 12.08 wurde gefilled aber wir haben ein großes ORG von gestern was nahezu komplett offen geblieben ist was zu erwarten war da es fast 400 Handle groß ist.
Das gefällt mir tatsächlich für weiterführende Baerishe Priceaction nicht da es wirklich sehr groß ist und als Zukünftiges Target gillt. Wenn mein Bias also falsch ist wird es daran liegen. Darum wäre es eigentlich optimal wenn wir in London und pre market session nach oben manipulieren wenn wir bereits am Morgen also London und Pre MArket nach unten gehen erwarte ich das wir nach oben gehen in NY AM.
