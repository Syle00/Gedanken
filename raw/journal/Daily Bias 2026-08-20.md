# Daily Bias 2026-08-20

> Weekly Bias: [[Weekly Bias KW34 2026]]

## News (Red/Orange Folder)

⚠️ News-Abruf fehlgeschlagen (`URLError: <urlopen error Tunnel connection failed: 403 Forbidden>`),
manuell auf forexfactory.com prüfen. Sowohl der ForexFactory- als auch der TradingView-Fallback
sind an einem Proxy-Tunnel-403 gescheitert (Cloud-Checkout dieser Session) — kein newsarmer Tag,
sondern ein Abruffehler.

## Levels

| Level | Datum | Close (17:00) | Open (18:00) | Gap | C.E. | Status |
|---|---|---|---|---|---|---|
| NWOG | 2026-08-02 | 28287.00 | 28565.00 | +278.00 | 28426.00 | offen |
| NDOG | 2026-08-17 | 30078.25 | 30077.00 | -1.25 | 30077.50 | gefüllt |

Gestrige Daily Range (2026-08-18): High 30121.25 / Low 29514.00 / Close 29559.50.

Weekly Range: keine Daten (`weekly_range` ist `null`).

ORG-C.E.: nicht verfügbar — `live_status.py` meldet `market_data: false`
(IBKR-Gateway in dieser Cloud-Session nicht erreichbar, Markt zum Laufzeitpunkt geschlossen).

### Offenes Gap: NWOG 2026-08-02

| | Level |
|---|---|
| High (Open) | 28565.00 |
| O7 / O6 / O5 | 28530.25 / 28495.50 / 28460.75 |
| Q3 | 28495.50 |
| **C.E. (= H1 = Q2 = O4)** | 28426.00 |
| Q1 | 28356.50 |
| O3 / O2 / O1 | 28391.25 / 28356.50 / 28321.75 |
| Low (Close) | 28287.00 |

### Datenlage (Marktdaten)

Alle 23 Tage im Fenster 2026-07-16 bis 2026-08-18 stammen aus **1s-Daten** (`tage_nur_1m` leer,
`registriert_ohne_datei` leer — kein stiller Datenverlust). Der 1s/1m-Abgleich zeigt nur kleine
Abweichungen (max. bis 2,0 Punkte, meist deutlich darunter) — unauffällig, kein Quellen-Konflikt.
Symbol: NQ (kein MNQ-Fallback nötig).

## Wiki-Bezug

[[Weekly Range Trading Model]], [[ICT Daily Range Session Timing]],
[[ORG (Opening Range Gap) & 1st Presented FVG]], [[Midnight Opening Range]]

## Einschaetzung (Claude)

Donnerstag ist saisonal laut `algo/seasonal_tendency.json` (MNQ, n=378, 2019-2026) nahezu ein
Münzwurf: 52,1 % bullische Tage, aber ein leicht **negativer** durchschnittlicher Tagesreturn
(-0,012 %) — die Mehrheit knapp bullischer Tage wird von wenigen starken Abwärtstagen im
Mittel aufgewogen. Median-Range 281,4 Pkt., Ø-Range 328,4 Pkt. (die höchste Ø-Range aller
Wochentage) spricht für einen eher volatilen, aber richtungslosen Tag. Siehe
[[Seasonal Tendency (Eigene Daten, laufend)]].

Der News-Ausfall verhindert eine Aussage zu Red-Folder-Katalysatoren für morgen — das ist eine
echte Lücke, kein "newsarmer Tag", und sollte vor Sessionstart manuell auf forexfactory.com
nachgeprüft werden.

Zur ORG-C.E.-These keine Aussage möglich: `org_ce` ist für den Zieltag naturgemäß noch nicht
gebildet (liegt erst nach Sessionstart vor).

Das einzige offene Gap (NWOG 2026-08-02, C.E. 28426.00) liegt gut 1100 Punkte unter dem
aktuellen Bereich (gestrige Close 29559.50) — als Ziel weit entfernt, aber die nächstgelegene
ungefüllte höhere Zeitrahmen-Liquidität unterhalb des Marktes.

## Mein Bias

_(noch offen)_
