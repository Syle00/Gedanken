# Daily Bias 2026-08-27

> Weekly Bias: [[Weekly Bias KW35 2026]]

## News (Red/Orange Folder)

⚠️ News-Abruf fehlgeschlagen (`URLError: <urlopen error Tunnel connection failed: 403 Forbidden>`), manuell auf forexfactory.com prüfen. (Sowohl ForexFactory- als auch der TradingView-Fallback scheiterten am selben Netzwerkfehler — in dieser Cloud-Session ist ausgehender Zugriff auf beide Domains offenbar blockiert.)

## Levels

**Datenlage (NQ):** 21 Tage 1s-Daten, keine nur-1m-Tage, keine registrierten Tage ohne Datei. 1s-vs-1m-Abgleich unkritisch (max. Abweichung 2,0 Pkt am 30.07., sonst ≤ 1,75 Pkt).

⚠️ **Die 1s-Anbindung hängt seit dem 21.08. fest** — die letzte vorhandene NQ-1s-Datei ist `2026-08-21`, identisch mit dem Stand der Läufe vom 24.08. und 25.08. Für 22.–26.08. fehlt IBKR-1s-Nachlad komplett (Lücke, kein Backfill in dieser Cloud-Session möglich — kein Gateway-Zugriff). Dadurch greift der Skript-Fallback für die gestrige Range auf die (laut `algo/bias_levels.py`-Docstring ohnehin brüchige) 1d-Reihe zurück und liefert den 13.08. statt des 26.08. — siehe Warnung unten.

| Level | Datum | Close (17:00) | Open (18:00) | Gap | C.E. | Status |
|---|---|---|---|---|---|---|
| NWOG | 2026-08-02 | 28287.00 | 28565.00 | +278.00 | 28426.00 | **offen** |
| NDOG | 2026-08-20 | 29317.25 | 29327.00 | +9.75 | 29322.00 | gefüllt |
| NDOG | 2026-08-19 | 29561.00 | 29561.50 | +0.50 | 29561.25 | gefüllt |
| NDOG | 2026-08-18 | 29559.50 | 29566.50 | +7.00 | 29563.00 | gefüllt |
| NDOG | 2026-08-17 | 30078.25 | 30077.00 | −1.25 | 30077.50 | gefüllt |

- ⚠️ **Gestrige Daily Range:** Kein verlässlicher Wert. Skript-Fallback lieferte 2026-08-13 (H 30272.75 / L 29780.50 / C 30188.50, Quelle `1d`) statt des 26.08. — 13 Tage alt, wegen der 1s-Lücke oben nicht als "gestern" verwertbar. Zeile bewusst nicht als aktuelle Range ausgewiesen.
- Weekly Range: _(kein Wert in den Daten — Zeile weggelassen)_
- ORG-C.E.: entfällt (`market_data: false` — IBKR-Gateway in dieser Cloud-Session nicht erreichbar)

### Offenes Gap — NWOG 2026-08-02 (Qs/Os/Hs)

Einziges noch ungefülltes Gap; C.E. bei **28426.00** — weiterhin ein übergeordneter Draw-on-Liquidity nach unten. Ohne verlässliche aktuelle Range (s.o.) keine belastbare Aussage zur Entfernung von der laufenden Kursstruktur möglich.

| | Level |
|---|---|
| High (Open) | 28565.00 |
| O7 / O6 / O5 | 28530.25 / 28495.50 / 28460.75 |
| Q3 | 28495.50 |
| **C.E. (= H1 = Q2 = O4)** | **28426.00** |
| Q1 | 28356.50 |
| O3 / O2 / O1 | 28391.25 / 28356.50 / 28321.75 |
| Low (Close) | 28287.00 |

## Wiki-Bezug

- [[Weekly Range Trading Model]]
- [[ICT Daily Range Session Timing]]
- [[Midnight Opening Range]]
- [[ORG (Opening Range Gap) & 1st Presented FVG]]
- [[New Day Opening Gap (NDOG)]] — die vier gefüllten NDOGs der Vorwoche (17.–20.08.) bleiben als nahe PD-Array-Bezugspunkte relevant.
- [[New Week Opening Gap (NWOG) Bias]] — das offene NWOG vom 02.08. ist weiterhin der einzige unerfüllte Gap im Fenster und bleibt als übergeordneter Downside-Draw notiert.

## Einschätzung (Claude)

Donnerstag liegt saisonal im Mittelfeld: bullische Quote **52,1 %** (n=378, seit 2019) — knapp über Dienstag (50,5 %) und Freitag (51,6 %), deutlich unter Montag (61,4 %) und Mittwoch (55,3 %) — bei mittlerem Tagesreturn **−0,012 %** (einziger negativer Wochentags-Durchschnitt). Die Range ist mit median 281,38 Pkt / avg 328,42 Pkt dagegen die **größte aller Wochentage**. Kein klarer Richtungs-Edge, aber historisch die volatilsten Sessions der Woche — Levels/PD-Arrays entsprechend eng führen.

Der News-Abruf ist fehlgeschlagen (Netzwerkfehler in dieser Cloud-Session, s.o.) — ob Red-Folder-Events anstehen, ist damit **nicht verifizierbar**. Ein FRED-Event-Backtest (`algo/backtest_fred_events.py`) entfällt deshalb; das sollte manuell nachgeholt werden, sobald der Kalender wieder erreichbar ist.

Das offene NWOG vom 02.08. (C.E. 28426.00) bleibt der einzige übergeordnete Downside-Draw. Eine Einordnung relativ zur aktuellen Kursstruktur ist wegen der fehlenden aktuellen Daily Range (s.o., 1s-Lücke seit 22.08.) nicht seriös möglich — die NDOG-C.E. der Vorwoche (29322.00 / 29561.25 / 29563.00 / 30077.50) sind die letzten verlässlichen nahen PD-Array-Bezugspunkte.

ORG-C.E.-70%-These: **nicht anwendbar** (`org_ce` nicht gesetzt — IBKR-Gateway in dieser Cloud-Session nicht erreichbar, kein Live-Preis verfügbar).

Grundlage: `algo/seasonal_tendency.json` (Wochentag Do), [[Seasonal Tendency (Eigene Daten, laufend)]].

## Mein Bias

_(Nutzerbereich — bitte selbst ausfüllen)_
