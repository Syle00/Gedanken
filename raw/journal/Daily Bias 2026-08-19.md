# Daily Bias 2026-08-19

> Weekly Bias: [[Weekly Bias KW34 2026]]

## News (Red/Orange Folder)

<<<<<<< Updated upstream
⚠️ News-Abruf fehlgeschlagen (`URLError: <urlopen error Tunnel connection failed: 403 Forbidden>`),
manuell auf forexfactory.com pruefen. Sowohl ForexFactory als auch der TradingView-Fallback
lieferten denselben 403-Fehler — vermutlich blockiert die Netzwerk-Policy dieser Cloud-Sandbox
ausgehende Verbindungen zu beiden Domains. Keine Termine erfunden; ob Mi 19.08.
Red-/Orange-Folder-Events hat, ist damit unbekannt und muss manuell geprüft werden.

## Levels

| Level | Datum | Close (17:00) | Open (18:00) | Gap | C.E. | Status |
|---|---|---|---|---|---|---|
| NWOG | 2026-08-02 | 28287.00 | 28565.00 | 278.00 | 28426.00 | offen |
| NDOG | 2026-07-29 | 27259.25 | 27202.00 | -57.25 | 27230.50 | offen |
| NDOG | 2026-08-10 | 29764.25 | 29764.50 | 0.25 | 29764.50 | gefüllt |
| NDOG | 2026-08-11 | 29646.75 | 29657.75 | 11.00 | 29652.25 | gefüllt |
| NDOG | 2026-08-12 | 29805.75 | 29825.00 | 19.25 | 29815.50 | gefüllt |
| NDOG | 2026-08-13 | 30214.25 | 30210.75 | -3.50 | 30212.50 | gefüllt |

Gestrige Daily Range (2026-08-14, letzter verfügbarer Handelstag — seit dem letzten Lauf ist
kein neuerer Tag in `raw/marktdaten/` hinzugekommen): High 30283.00 / Low 30028.50 / Close
30154.00.

Weekly Range: keine Daten für die laufende ISO-Woche 34 vorhanden — Zeile entfällt statt eine
Zahl zu erfinden.

ORG-C.E.: `algo/live_status.py` meldete `market_data: false` (kein 5m-Feed/IBKR-Gateway
erreichbar) — Zeile entfällt ohne Platzhalter.

**Datenlage:** 2 Tage 1s (13., 14.08.), 12 Tage nur 1m im betrachteten Zeitraum
(2026-07-15 – 2026-08-19). Keine `registriert_ohne_datei`-Lücken. 1s-vs-1m-Abgleich für beide
1s-Tage unauffällig (13.08.: max 0.25 Pkt Abweichung auf 3 von 1380 Minuten; 14.08.: max 0.5 Pkt
auf 4 von 1380 Minuten) — beide Quellen stimmen praktisch überein, kein Level-Ausschluss nötig.

### NWOG 2026-08-02 (offen)

| | Level |
|---|---|
| High (Open, 08-02 18:00) | 28565.00 |
| O7 | 28530.25 |
| O6 / Q3 | 28495.50 |
| O5 | 28460.75 |
| **C.E. (= H1 = Q2 = O4)** | 28426.00 |
| O3 | 28391.25 |
| O2 / Q1 | 28356.50 |
| O1 | 28321.75 |
| Low (Close, 07-31 17:00) | 28287.00 |

### NDOG 2026-07-29 (offen)

| | Level |
|---|---|
| High (Close, 07-29 17:00) | 27259.25 |
| O7 | 27252.00 |
| O6 / Q3 | 27245.00 |
| O5 | 27237.75 |
| **C.E. (= H1 = Q2 = O4)** | 27230.50 |
| O3 | 27223.50 |
| O2 / Q1 | 27216.25 |
| O1 | 27209.25 |
| Low (Open, 07-29 18:00) | 27202.00 |
=======
**Mi 19.08.**

🔴 **14:00 NY** / 20:00 DE — FOMC Meeting Minutes

Quelle: **ForexFactory** (`news.source: forexfactory`).

## Levels

Gerechnet aus `raw/marktdaten/` (**NQ**, 1s bevorzugt). Alle Preise auf dem 0,25-Tickraster.

> ⚠️ **Datenlücke:** `raw/marktdaten/2026/08/` enthält aktuell keine Tage nach dem 14.08.
> Heute ist Di 18.08. — der Handelstag läuft noch, dass er fehlt ist normal, keine Lücke. Der
> echte Fehlbestand ist **Mo 17.08.** (abgeschlossener Handelstag, keine Datei vorhanden).
> `yesterday_range` unten ist deshalb der letzte verfügbare Handelstag (Fr 14.08.), nicht der
> eigentliche Vortag. Wird hier nicht selbst nachgeladen (Autonomie-Regel: Lücken werden
> gemeldet, nicht repariert) — bitte Nachlad für 17.08. anstoßen, bevor mit aktuellen Levels
> gehandelt wird.

| Level | Datum | Close (17:00) | Open (18:00) | Gap | C.E. | Status |
|---|---|---|---|---|---|---|
| NWOG | So 02.08. | 28287.00 | 28565.00 | +278.00 | 28426.00 | offen |
| NDOG | Mi 29.07. | 27259.25 | 27202.00 | −57.25 | 27230.50 | offen |
| NDOG | Mo 10.08. | 29764.25 | 29764.50 | +0.25 | 29764.50 | gefüllt |
| NDOG | Di 11.08. | 29646.75 | 29657.75 | +11.00 | 29652.25 | gefüllt |
| NDOG | Mi 12.08. | 29805.75 | 29825.00 | +19.25 | 29815.50 | gefüllt |
| NDOG | Do 13.08. | 30214.25 | 30210.75 | −3.50 | 30212.50 | gefüllt |

**Letzter verfügbarer Handelstag (Fr 14.08.):** High 30283.00 / Low 30028.50 / Close 30154.00
(Quelle: intraday).

Kein ORG-C.E. — `live_status.py` meldet `market_data: false` (Marktzugriff beim Lauf nicht
verfügbar).

**NWOG 02.08. — Qs / Os / Hs**

| | Level |
|---|---|
| High (Open So 18:00) | 28565.00 |
| O7 | 28530.25 |
| O6 / Q3 | 28495.50 |
| O5 | 28460.75 |
| **C.E. (= H1 = Q2 = O4)** | **28426.00** |
| O3 | 28391.25 |
| O2 / Q1 | 28356.50 |
| O1 | 28321.75 |
| Low (Close Fr 16:59) | 28287.00 |

**NDOG 29.07. — Qs / Os / Hs**

| | Level |
|---|---|
| High (Close 16:59) | 27259.25 |
| O7 | 27252.00 |
| O6 / Q3 | 27245.00 |
| O5 | 27237.75 |
| **C.E. (= H1 = Q2 = O4)** | **27230.50** |
| O3 | 27223.50 |
| O2 / Q1 | 27216.25 |
| O1 | 27209.25 |
| Low (Open 18:00) | 27202.00 |
>>>>>>> Stashed changes

## Wiki-Bezug

- [[Weekly Range Trading Model]]
- [[ICT Daily Range Session Timing]]
- [[Midnight Opening Range]]
- [[ORG (Opening Range Gap) & 1st Presented FVG]]
<<<<<<< Updated upstream

## Einschaetzung (Claude)

Mittwoch zeigt in `algo/seasonal_tendency.json` (n=376, 2019–2026) eine leichte bullische
Tendenz: 55.3% bullische Tage, avg_return_pct 0.11%, avg_range ~318.4 Punkte (Median 278.4) —
schwächer als ein starker Edge, aber deutlicher als der Münzwurf vom Dienstag (50.5%).

Die beiden offenen Gaps (NWOG-C.E. 28426.00, NDOG-C.E. 27230.50) liegen ca. 1700–2900 Punkte
unterhalb der letzten bekannten Preisregion (~30154, Close 14.08.) — als PD-Arrays weiterhin
gültige, aber kurzfristig eher unwahrscheinlich erreichbare Downside-DOL-Kandidaten, kein
primäres Ziel für die Mi-Range.

Die ORG-C.E.-70%-These (empirisch bislang 35-43% im eigenen Backtest, siehe `algo/PLAN.md`)
bleibt laut Nutzerentscheid eine aktiv weiter beobachtete Hypothese — nicht widerlegt, aber auch
nicht bestätigt. Für 2026-08-19 lässt sie sich vorab naturgemäß nicht auswerten, da das ORG erst
mit der US-Session-Eröffnung entsteht.

Da der News-Abruf fehlgeschlagen ist (siehe oben), bleibt unklar, ob am Mittwoch ein
Red-Folder-Event ansteht — das ist ein zusätzliches, unbeziffertes Risiko gegenüber einem
normalen newsarmen Tag und sollte vor dem Handelstag manuell nachgeprüft werden.

## Mein Bias
=======
- [[New Day Opening Gap (NDOG)]]
- [[New Week Opening Gap (NWOG) Bias]]
- [[Two Stage News Delivery (FOMC & NFP)]] — einschlägig für den 14:00-Termin

## Einschätzung (Claude)

**Taktgeber des Tages ist FOMC Meeting Minutes, 14:00 NY.** Nach [[Two Stage News Delivery
(FOMC & NFP)]] ist mit einer ersten Reaktion direkt auf die Veröffentlichung zu rechnen, die
eigentliche Auflösung eher danach — nicht in einer einzelnen Bewegung. Ein quantifizierter
Edge für Minutes-Releases fehlt: `algo/backtest_fred_events.py` hat bewusst keinen FOMC-
Reaktionstest gebaut (im Datenfenster keine FOMC-Zielsatzänderung, n=0) und deckt stattdessen
nur VIX/DGS10/WALCL-Zusammenhänge ab — für den heutigen Termin also keine eigene Statistik,
nur das Strukturmodell.

**Saisonalität.** Aus `algo/seasonal_tendency.json` (n=1882 Tage) ist Mittwoch mit **55,3 %
bullish** (n=376, avg +0,11 %) leicht überdurchschnittlich, aber kein starkes Signal.

**Level-Lage.** Die beiden offenen Gaps (NWOG-C.E. 28426.00, NDOG-C.E. 27230.50) liegen weit
unter dem zuletzt bekannten Preisbereich (~30150) — sie bleiben Sell-Side-Draw-Kandidaten für
den übergeordneten Zeitrahmen, keine realistischen Tagesziele für Mittwoch.

Kein ORG-C.E. verfügbar (`market_data: false`), daher keine Aussage zur 70%-These heute möglich.

**Was diese Einschätzung nicht leistet:** kein Kursziel, keine Richtungsprognose — die
Datenlücke (Mo 17.08. fehlt) und der fehlende ORG-C.E. schränken die Aussagekraft zusätzlich
ein.

## Mein Bias

>>>>>>> Stashed changes
