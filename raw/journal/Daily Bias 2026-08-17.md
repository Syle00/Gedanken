# Daily Bias 2026-08-17

*(Montag, überarbeitet am 16.08.2026 durch `/bias-vorlage-daily`)*

> Weekly Bias: [[Weekly Bias KW34 2026]]

## News (Red/Orange Folder)

Quelle: **ForexFactory** (`news.source: forexfactory`). **Nur USD** — gehandelt werden NQ/ES.

**Mo 17.08.** ❌ keine USD-Termine

**Kein Abrufproblem, sondern die Nachrichtenlage** — der Feed antwortet fehlerfrei, es gibt für
Montag schlicht keinen USD-Termin mit Red- oder Orange-Impact. Der erste Taktgeber der Woche ist
Mittwoch 14:00 NY (FOMC Minutes), siehe [[Weekly Bias KW34 2026]].

Für einen newsarmen Tag liegt die Median-Tagesrange bei **266,9 Punkten** (n=42, gemessen über
753 NQ-Handelstage) gegenüber 330,8 an Tagen mit drei oder mehr Terminen — also rund **24 %
weniger Bewegung** zu erwarten.

## Levels

Gerechnet aus `raw/marktdaten/` (**NQ**, 14 Handelstage im Fenster, 1s bevorzugt).
Kein Micro-Rückfall — die Level stammen aus dem tatsächlich gehandelten Symbol.
Alle Preise auf dem 0,25-Tickraster.

**Datenlage:** 2 der 14 Tage liegen als 1s vor (13.08., 14.08.), die übrigen 12 als 1m.
`1s-abdeckung.csv` meldet für dieses Fenster keinen Tag ohne Datei — Register und Bestand
decken sich. Wo beide Quellen denselben Tag abdecken, stimmen sie zu über 99,7 % überein.

### Vortagesrange (Fr 14.08.)

| | Wert |
|---|---|
| High (PDH) | **30283.00** (09:05 NY) |
| Low (PDL) | **30028.50** |
| Close | **30154.00** (16:59 NY) |
| Range | 254.50 Punkte |

> ⚠️ **Aus den Intraday-Daten**, nicht aus der 1d-Reihe. Die enthält den 14.08. gar nicht und
> würde den 13.08. liefern (High 30272.75) — falscher Tag und 10,25 Punkte zu wenig.
> `yesterday_range()` wurde am 16.08. auf die Intraday-Quelle umgestellt.

### Offene Gaps — DOL-Kandidaten

| Typ | Datum | Close (17:00) | Open (18:00) | Gap | C.E. | Spanne |
|---|---|---|---|---|---|---|
| **NWOG** | Fr 31.07. → So 02.08. | 28287.00 | 28565.00 | +278.00 | **28426.00** | 278.00 |
| **NDOG** | Mi 29.07. | 27259.25 | 27202.00 | −57.25 | **27230.50** | 57.25 |

Beide liegen weit **unter** dem Freitagsschluss (30154.00) — Sell-Side-Ziele, für einen
einzelnen Handelstag außer Reichweite. Sie bleiben übergeordnete Draw-Kandidaten.

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

### NDOG der Vorwoche (alle gefüllt)

| Datum | Close (17:00) | Open (18:00) | Gap | C.E. |
|---|---|---|---|---|
| Mo 10.08. | 29764.25 | 29764.50 | +0.25 | 29764.50 |
| Di 11.08. | 29646.75 | 29657.75 | +11.00 | 29652.25 |
| Mi 12.08. | 29805.75 | 29825.00 | +19.25 | 29815.50 |
| Do 13.08. | 30214.25 | 30210.75 | −3.50 | 30212.50 |

Die Vorwoche hat jeden Tages-Gap wieder eingesammelt — kein offener NDOG aus KW33.

### Wochenrange KW33 (Referenz)

High **30283.00** (Fr 14.08. 09:05) / Low **29533.50** (Di 11.08. 14:29), Spanne 749.50.
Das Wochen-High ist zugleich der PDH — beide Level fallen auf denselben Punkt.

*ORG-C.E. und NDOG für heute: `live_status.py` meldet `market_data: false` (Sonntag, Globex
öffnet erst 18:00 NY). Wird beim ersten Lauf nach Wochenstart nachgetragen.*

## Wiki-Bezug

- [[Weekly Range Trading Model]] — Montag als Wochenstart, wo High/Low typischerweise liegt
- [[ICT Daily Range Session Timing]] — Session-Struktur eines Handelstags
- [[New Day Opening Gap (NDOG)]] — für die offenen Gaps oben
- [[Midnight Opening Range]] — Bezugspunkt für den NY-Handelstag
- [[ORG (Opening Range Gap) & 1st Presented FVG]] — sobald der Sonntag-Open steht

## Einschaetzung (Claude)

**Newsarmer Wochenstart.** Kein USD-Termin, der erste echte Taktgeber ist Mittwoch 14:00 NY.
Empirisch bedeutet das rund 24 % weniger Tagesrange als an newsreichen Tagen (266,9 gegen
330,8 Punkte Median). Die Woche dürfte ihre Bewegung erst ab Mittwoch liefern — Mi (330,5) und
Do (342,0) sind die beiden bewegungsstärksten Wochentage im Bestand.

**Montag ist der statistisch stärkste Wochentag.** `algo/seasonal_tendency.json`: **61,4 %
bullish** (n=376, avg +0,194 %, Median-Range 263,88). Das ist die einzige Wochentagsabweichung,
die deutlich aus dem Rauschen läuft. Zusammen mit dem newsarmen Umfeld spricht das für einen
freundlichen, aber ruhigen Start.

**Nächstliegender Bezugspunkt nach oben ist der PDH 30283.00** — nur 129 Punkte über dem
Freitagsschluss und damit innerhalb der Median-Range eines newsarmen Tages. Nach unten liegt der
PDL bei 30028.50 (125,5 Punkte), also nahezu symmetrisch.

**COT stützt NQ, nicht ES.** Der Report vom 11.08. zeigt NQ-Commercials netto long über alle
fünf Horizonte, ES-Commercials netto short am 12-Monats-Tief. Details in
[[Weekly Bias KW34 2026]]. Für den Wochenstart heißt das: ein bullishes NQ-Signal, aber kein
einheitliches Index-Bias.

**Was fehlt:** Der Sonntag-Open (18:00 NY) steht noch aus, damit auch NDOG und ORG-C.E. für
heute. Die ORG-C.E.-70%-These bleibt als *laufend beobachtete* Hypothese notiert (empirisch
bislang 35–43 % im eigenen Backtest, laut Nutzerentscheid nicht als widerlegt abgehakt) —
sobald die Opening Range steht, ist sie hier prüfbar.

## Mein Bias

### Targets und relevante PD Arrays (Mo 17.08.)

- **Target: PDH 30.283,00** — möglich.
- **Relevantes PD Array: SIBI vom 23.06.**
- **Höchster Buyside Pool, der für Montag und Dienstag gerade erkennbar ist: 30.599,75 (30.06.)**

Übernommen aus [[Weekly Bias KW34 2026]] — Montag ist bereits Teil dieser Woche, die
Wochenstruktur (Retracement ins BISI, Sellside 29.780,50 als DOL) gilt unverändert.

---

*Gegenprüfung (Claude, 16.08.2026):*

- **PDH 30.283,00 bestätigt** — High vom Fr 14.08., 09:05 NY, aus den NQ-Intraday-Daten.
  Der Freitag schloss bei 30.154,00, das Ziel liegt also **129 Punkte** über dem letzten Print.
  Tagesrange Freitag: H 30.283,00 / L 30.028,50 / C 30.154,00.
- **30.599,75 (30.06.) exakt bestätigt** als Tages-High. Liegt **445 Punkte** über dem
  Freitagsschluss — als Montagsziel weit, als Wochenziel erreichbar.
- **SIBI 23.06.:** Tagesrange H 30.701,25 / L 29.577,25 / C 29.666,00 — für die genaue
  Gap-Lage fehlen mir Intraday-Daten aus dem Juni, das kann ich nicht nachrechnen.
- Einordnung zur Erwartung „wenig Bewegung": Die Median-Tagesrange an newsarmen Tagen liegt bei
  **266,9 Punkten** (n=42). Vom Freitagsschluss aus reicht das rechnerisch für den PDH
  (129 Punkte), **nicht** für 30.599,75 (445 Punkte). Zusammen mit dem statistisch starken
  Montag stützt das „PDH als Tagesziel, Buyside-Pool als Wochenziel".
