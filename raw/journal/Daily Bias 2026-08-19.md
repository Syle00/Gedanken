# Daily Bias 2026-08-19

> Weekly Bias: [[Weekly Bias KW34 2026]]

## News (Red/Orange Folder)

**Mi 19.08.**

🔴 **14:00 NY** / 20:00 DE — FOMC Meeting Minutes

🟠 **14:30 NY** / 20:30 DE — President Trump Speaks

_Quelle: forexfactory (laufende FF-Woche), kein Abruf-Fehler._

## Laufende Session (Stand 19.08. 01:45:49 NY / 07:45 DE)

Aus einem Live-Abruf über `live_fenster()` — **rein im Speicher, nicht in `raw/marktdaten/`**.
Eine Tagesdatei darf für den laufenden Tag nicht entstehen, sonst friert der Teiltag ein (genau
der Fehler, der den 18.08. beschädigt hatte).

| | Wert | Zeit |
|---|---|---|
| Open (18.08. 18:00) | 29566.50 | 18.08. 18:00:00 |
| Session-High | 29609.50 | 21:22:29 |
| Session-Low | **29442.00** | 20:01:40 |
| Letzter Preis | **29470.00** | 01:45:49 |
| Range bisher | 167.50 Pkt | von 278.4 Pkt Mittwochs-Median |

**Was die Nacht gemacht hat, in drei Schritten:**

1. **19:00:19 NY** — das NDOG 2026-08-06 (29504.25–29514.25) wurde nach unten durchbrochen und
   damit vollständig durchgehandelt. Die unverbrauchte untere Hälfte, die gestern noch als Level
   dastand, ist verbraucht.
2. **20:01:40 NY** — Session-Tief 29442.00. Damit ist das **18.08.-Tagestief 29514.00 genommen**
   (Sell-Side-Liquidität abgeholt).
3. **21:22:29 NY** — Erholung auf 29609.50, also *zurück über* das 06.08-Gap, danach erneuter
   Abverkauf auf jetzt 29470.00. Das Gap wurde von unten angetestet und abgelehnt — es liegt
   jetzt **über** dem Preis und hat die Rolle gewechselt.

**ORG-C.E.:** noch nicht bestimmbar, RTH-Open 09:30 NY liegt ~7,7 h voraus.

## Levels

Symbol: NQ. Sortiert nach Abstand zum aktuellen Preis (29470.00).

| Level | Datum | Close (17:00) | Open (18:00) | Gap | C.E. | Lage zum Preis |
|---|---|---|---|---|---|---|
| NDOG | **2026-08-18** | 29559.50 | 29566.50 | +7.00 | 29563.00 | +93.00 — nach 84 s gefüllt |
| NDOG | 2026-08-06 | 29504.25 | 29514.25 | +10.00 | 29509.25 | **+34.25 — erster Widerstand** |
| NDOG | 2026-08-05 | 29600.25 | 29569.50 | -30.75 | 29585.00 | +99.50 |
| NDOG | 2026-08-11 | 29646.75 | 29657.75 | +11.00 | 29652.25 | +176.75 |
| NDOG | 2026-07-15 | 29707.50 | 29709.00 | +1.50 | 29708.25 | +237.50 |
| NDOG | **2026-07-21** | 29289.75 | 29310.75 | +21.00 | 29300.25 | **-169.75 — erster Draw nach unten** |
| NDOG | 2026-07-16 | 29179.00 | 29191.00 | +12.00 | 29185.00 | -279.00 |
| NWOG | **2026-08-02** | 28287.00 | 28565.00 | +278.00 | 28426.00 | -1044.00 — **einziges offenes Gap** |

**Weekly Range KW34** (2 von 5 Handelstagen + laufende Nacht): High **30343.00** (17.08.) / Low
**29442.00** (heute Nacht). Gerechnet aus 1s-Daten — `week_range()` liefert `null`, weil die
1d-Reihe beim 13.08. endet (`algo/PLAN.md`: „1d-Dateien gegen Intraday-Aggregat gegenprüfen").

**Gestrige Daily Range (2026-08-18, vollständig):** High **30121.25** / Low **29514.00** /
Close **29559.50**. Range 607.25 Pkt = **2,3-fache** Dienstags-Median-Range (262.88 Pkt).
Gegenüber dem 17.08.-Close (30078.25) ein Abverkauf von **-518.75 Pkt (-1,72 %)**, Schluss
45.50 Pkt über dem Tief.

**Datenlage:** 24 Tage 1s (2026-07-15 – 2026-08-18), 0 Tage nur 1m, keine
`registriert_ohne_datei`-Einträge. Der 18.08. wurde am 19.08. neu geholt und ist jetzt mit
82.800 Kerzen vollständig; ebenso repariert: ES 26.06. (30-Minuten-Loch an der RTH-Eröffnung).
Offen: NQ 14.07. (30-Minuten-Loch 11:30–12:00 NY) — der Nachlauf wurde für diesen Live-Abruf
gestoppt und ist nachzuholen. 1s-vs-1m-Abgleich über 14 Tage unauffällig (max. 2.00 Pkt).

### NDOG 2026-08-18 — der Gap dieser Session

Close 18.08. 16:59:59 NY = 29559.50 · Open 18.08. 18:00:00 NY = 29566.50 · Spanne 7.00 Pkt

**Gefüllt um 18:01:24 NY — 84 Sekunden nach dem Open.** Als Level für heute erledigt.

| | Level |
|---|---|
| High (Open) | 29566.50 |
| O7 | 29565.50 |
| O6 / Q3 | 29564.75 |
| O5 | 29564.00 |
| **C.E. (= H1 = Q2 = O4)** | **29563.00** |
| O3 | 29562.00 |
| O2 / Q1 | 29561.25 |
| O1 | 29560.50 |
| Low (Close) | 29559.50 |

### NDOG 2026-08-06 — erster Widerstand über dem Preis (+34.25)

Close 29504.25 · Open 29514.25 · Spanne 10.00 Pkt. Gestern von oben gehalten, heute Nacht um
19:00:19 nach unten gebrochen und von unten wieder angetestet.

| | Level |
|---|---|
| High (Open) | 29514.25 |
| O7 | 29513.00 |
| O6 / Q3 | 29511.75 |
| O5 | 29510.50 |
| **C.E. (= H1 = Q2 = O4)** | **29509.25** |
| O3 | 29508.00 |
| O2 / Q1 | 29506.75 |
| O1 | 29505.50 |
| Low (Close) | 29504.25 |

### NDOG 2026-07-21 — erster Draw nach unten (-169.75)

Close 29289.75 · Open 29310.75 · Spanne 21.00 Pkt. 131.25 Pkt unter dem Session-Tief und damit
**innerhalb einer Median-Mittwochs-Range** erreichbar.

| | Level |
|---|---|
| High (Open) | 29310.75 |
| O7 | 29308.00 |
| O6 / Q3 | 29305.50 |
| O5 | 29303.00 |
| **C.E. (= H1 = Q2 = O4)** | **29300.25** |
| O3 | 29297.50 |
| O2 / Q1 | 29295.00 |
| O1 | 29292.50 |
| Low (Close) | 29289.75 |

### NWOG 2026-08-02 — einziges offenes Gap (-1044.00)

Close 31.07. 16:59:59 NY = 28287.00 · Open 02.08. 18:00:00 NY = 28565.00 · Spanne 278.00 Pkt

| | Level |
|---|---|
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
- [[Average Daily Range (5-Tage-ADR)]] — nach der 607-Pkt-Range von gestern

## Einschaetzung (Claude)

**Die Struktur ist bearish, und zwar über zwei Sessions hinweg konsistent.** Der 18.08. schloss
45 Pkt über seinem Tief, die Nacht hat dieses Tief dann genommen (29442.00 gegen 29514.00) und
das 06.08-NDOG dabei durchgehandelt. Der Rückläufer auf 29609.50 ging *über* das gebrochene Gap
und wurde verkauft — das ist die Sequenz, die man sehen will, wenn Verkäufer die Kontrolle
behalten: Level brechen, von unten antesten, ablehnen. Aktuell 29470.00, 28 Pkt über dem
Session-Tief.

**Die beiden Level, um die es heute geht:**

- **Nach unten: NDOG 2026-07-21, C.E. 29300.25** (-169.75 Pkt). Bei 278 Pkt Median-Range und
  bereits 167.50 Pkt verbrauchter Range ist das der nächste saubere Draw. Erst dahinter liegt
  das 07-16-NDOG bei 29185.00 (-279 Pkt), das eine Median-Range voll ausschöpfen würde.
- **Nach oben: NDOG 2026-08-06, 29504.25–29514.25** (+34.25 Pkt). Solange der Preis darunter
  bleibt, ist die Nacht-Struktur intakt. Ein Tagesschluss *über* 29514.25 würde sie brechen —
  das ist das kürzeste Invalidierungskriterium, das die Daten hergeben.

**Der 18.08.-NDOG spielt keine Rolle.** +7.00 Pkt, nach 84 Sekunden gefüllt. Ein Gap dieser
Größe ist kein PD Array, sondern Rauschen — er steht hier nur, weil du danach gefragt hast, nicht
weil er handelbar wäre.

**Taktgeber bleibt FOMC Meeting Minutes, 14:00 NY**, mit Trump-Auftritt 14:30 NY. Nach
[[Two Stage News Delivery (FOMC & NFP)]] ist die erste Reaktion typischerweise nicht die
Auflösung. Alles, was bis 14:00 passiert, ist damit vorläufig — die Nacht kann eine saubere
bearische Sequenz gelaufen sein und um 14:01 komplett neu verhandelt werden. Ein quantifizierter
Edge fehlt: `algo/backtest_fred_events.py` hat für FOMC keinen Reaktionstest (n=0, keine
Zielsatzänderung im Datenfenster).

**Saisonalität widerspricht** (`algo/seasonal_tendency.json`, MNQ, n=1882): Mittwoch **55,3 %
bullish** (n=376, avg +0,11 %). Das ist der schwächste Teil der Analyse — 55 gegen 45 ist kein
Signal, auf das sich ein Gegen-Trade stützen lässt, und es steht der konkreten Struktur der
letzten zwei Sessions entgegen. Ich gewichte die Struktur höher; vgl.
[[Seasonal Tendency (Eigene Daten, laufend)]].

**ORG-C.E.-These:** heute noch nicht prüfbar, RTH-Open steht aus. Die 70 %-Hypothese bleibt als
laufend beobachtet stehen (empirisch bislang 35–43 %).

**Was diese Einschätzung nicht leistet:** kein Kursziel, kein Entry, kein Stop. Die
Session-Zahlen sind ein Live-Stand von 01:45 NY und veralten bis zum RTH-Open — London öffnet
erst in gut einer Stunde, und die Nacht-Range von 167 Pkt ist bislang von einem dünnen
Asien-Buch gemacht.

## Mein Bias

