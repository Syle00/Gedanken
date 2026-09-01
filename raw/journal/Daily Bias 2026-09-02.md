# Daily Bias 2026-09-02

> Weekly Bias: [[Weekly Bias KW36 2026]]

## News (Red/Orange Folder)

⚠️ News-Abruf fehlgeschlagen (URLError: <urlopen error Tunnel connection failed: 403 Forbidden>),
manuell auf forexfactory.com pruefen. Quelle laut Skript: `tradingview` (Fallback, da Zieltag
ausserhalb der laufenden ForexFactory-Woche liegt) — aber auch dieser Abruf ist am selben
Tunnel-403 gescheitert, nicht nur ForexFactory. Kein „news-armer Tag" bestaetigt, nur ein
Abrufproblem in dieser Cloud-Session.

## Levels

⚠️ **Datenlage:** `raw/marktdaten/` hat fuer NQ/ES **seit 2026-08-21 keine neuen 1s-Daten**
mehr (`1s-abdeckung.csv`, letzter Eintrag 2026-08-21 21:00 UTC) — 12 Tage Ruecklauf zum Zieltag.
Kein `registriert_ohne_datei` (keine stillen Datei-Luecken innerhalb des vorhandenen Bestands),
`abgleich_1s_vs_1m` unauffaellig (max. Abweichung 2,5 Pkt, ueberwiegend <1 Pkt — normale
Rundungsdifferenz). Die Luecke selbst ist aber real: Seit dem letzten Marktdaten-Ingest
(Commit `f35758b3ba`, 17.–20.08.) lief kein `daten-1s`-Nachlad mehr, vermutlich weil die
Daily-Bias-Vorlagen der letzten Tage aus dieser IBKR-losen Cloud-Session generiert wurden statt
vom Rechner mit laufendem IB-Gateway. Konsequenzen unten je Wert markiert.

**Gestrige Daily Range (2026-09-01) nicht verfuegbar.** `yesterday_range()` findet keine
Intraday-Daten (Luecke s.o.) und faellt auf die 1d-Reihe zurueck — deren letzter Eintrag ist
**2026-08-13**, 19 Tage alt. Das waere kein "gestern", sondern eine falsche Zuordnung — daher
hier bewusst **weggelassen** statt als Zeile mit falschem Datum ausgegeben.

**Weekly Range** nicht verfuegbar (`weekly_range: null`).

**ORG-C.E./aktueller Preis** nicht verfuegbar — `live_status.py` meldet `market_data: false`
(IBKR-Gateway von dieser Cloud-Session aus nicht erreichbar, Fehler
`ConnectionRefusedError(111, 127.0.0.1:4002)`).

Reihenfolge: offene Gaps zuerst, danach die zuletzt in den Daten vorhandenen NDOGs — **das ist
wegen der Luecke oben nicht die tatsaechlich letzte Handelswoche vor dem 02.09., sondern die
Woche 17.–20.08.**

| Level | Datum | Close (17:00) | Open (18:00) | Gap | C.E. | Status |
|---|---|---|---|---|---|---|
| NWOG | 2026-08-02 | 28287,00 | 28565,00 | +278,00 | 28426,00 | offen |
| NDOG | 2026-08-20 | 29317,25 | 29327,00 | +9,75 | 29322,00 | gefüllt |
| NDOG | 2026-08-19 | 29561,00 | 29561,50 | +0,50 | 29561,25 | gefüllt |
| NDOG | 2026-08-18 | 29559,50 | 29566,50 | +7,00 | 29563,00 | gefüllt |
| NDOG | 2026-08-17 | 30078,25 | 30077,00 | -1,25 | 30077,50 | gefüllt |

### NWOG 2026-08-02 — Qs/Os/Hs (offen, seit einem Monat ungefüllt)

| | Level |
|---|---|
| High (Open) | 28565,00 |
| O7 / O6 / O5 | 28530,25 / 28495,50 / 28460,75 |
| Q3 | 28495,50 |
| **C.E. (= H1 = Q2 = O4)** | **28426,00** |
| Q1 | 28356,50 |
| O3 / O2 / O1 | 28391,25 / 28356,50 / 28321,75 |
| Low (Close) | 28287,00 |

## Wiki-Bezug

- [[Weekly Range Trading Model]]
- [[ICT Daily Range Session Timing]]
- [[Midnight Opening Range]]
- [[ORG (Opening Range Gap) & 1st Presented FVG]]
- [[New Day Opening Gap (NDOG)]]
- [[New Week Opening Gap (NWOG) Bias]] — der einzige aktuell offene Gap ist ein NWOG, daher
  trotz Mittwoch relevant

## Einschaetzung (Claude)

Saisonalitaet laut `algo/seasonal_tendency.json` (Mittwoch, n=376, 2019–2026): 55,3 % bullische
Tage, durchschnittlicher Return +0,11 %, Median-Range 278,38 Pkt, Durchschnitts-Range 318,43 Pkt
— leicht bullisch verzerrt gegenüber dem Wochendurchschnitt, aber kein starkes Signal.

Keine Red-/Orange-Folder-News mit Impact bestaetigt (Abruf fehlgeschlagen, s.o.) — kein
`backtest_fred_events.py`-Lauf, da keine Events vorliegen, gegen die getestet werden könnte.

Die 70-%-ORG-C.E.-These (laufende Beobachtung, aktuell 35–43 % im eigenen Backtest, siehe
`wiki/synthesis/Muster-Validierung (laufend).md`) bleibt hier unberücksichtigt, weil `org_ce`
für den Zieltag mangels RTH-Open naturgemäß noch nicht feststeht.

**Aussage insgesamt schwach belastbar**: ohne aktuellen Preis, ohne gestrige Range und mit einer
12-Tage-Datenlücke stützt sich die Einschätzung praktisch nur auf die Saisonaltendenz und das
alte offene NWOG. Empfehlung: `daten-1s`-Nachlad auf dem Rechner mit IB-Gateway nachholen, bevor
morgen intraday gehandelt wird.

## Mein Bias

