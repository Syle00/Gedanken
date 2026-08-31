# Daily Bias 2026-09-01

> Weekly Bias: _(noch kein Weekly Bias fuer diese Woche)_

## News (Red/Orange Folder)

⚠️ News-Abruf fehlgeschlagen (`URLError: <urlopen error Tunnel connection failed: 403 Forbidden>`), manuell auf forexfactory.com prüfen. (Sowohl ForexFactory- als auch der TradingView-Fallback scheiterten am selben Netzwerkfehler — in dieser Cloud-Session ist ausgehender Zugriff auf beide Domains offenbar blockiert.)

## Levels

**Datenlage (NQ):** 19 Tage 1s-Daten (28.07.–21.08.2026), keine nur-1m-Tage, keine registrierten Tage ohne Datei. 1s-vs-1m-Abgleich unkritisch (max. Abweichung 2,0 Pkt am 30.07., sonst ≤ 1,75 Pkt).

⚠️ **Datenlücke (aktiv, über das übliche Maß hinaus):** Die 1s-Anbindung in `raw/marktdaten/` endet am 21.08.2026, 21:00 UTC — für die Handelstage 24.–31.08. (Mo–Mo, sieben Tage inkl. heute) liegen **weder 1s- noch 1d-Daten** vor. Das ist keine normale Wochenend-Lücke, sondern ein mehrtägiger Ausfall der laufenden IBKR-Anbindung. Entsprechend sind die NDOG-Zeilen unten die letzten *verfügbaren* (Woche 17.–20.08.), nicht die der zuletzt abgeschlossenen Handelswoche, und die "gestrige Daily Range" ist ein 1d-Fallback vom 13.08. — nicht der tatsächliche Vortag (Montag, 31.08.). Bitte den IBKR-1s-Nachlad manuell prüfen (`algo/fetch_ibkr.py` bzw. `/daten-1s`), sobald jemand am Rechner mit Gateway-Zugriff ist.

| Level | Datum | Close (17:00) | Open (18:00) | Gap | C.E. | Status |
|---|---|---|---|---|---|---|
| NWOG | 2026-08-02 | 28287.00 | 28565.00 | +278.00 | 28426.00 | **offen** |
| NDOG | 2026-08-20 | 29317.25 | 29327.00 | +9.75 | 29322.00 | gefüllt |
| NDOG | 2026-08-19 | 29561.00 | 29561.50 | +0.50 | 29561.25 | gefüllt |
| NDOG | 2026-08-18 | 29559.50 | 29566.50 | +7.00 | 29563.00 | gefüllt |
| NDOG | 2026-08-17 | 30078.25 | 30077.00 | −1.25 | 30077.50 | gefüllt |

- **Gestrige Daily Range (Fallback 2026-08-13, Quelle 1d):** H 30272.75 / L 29780.50 / C 30188.50 — **nicht** der tatsächliche Vortag; letzter Handelstag, für den in der 1d-Reihe überhaupt Daten vorliegen (siehe Datenlücke oben).
- Weekly Range: _(kein Wert in den Daten — Zeile weggelassen)_

### Offenes Gap — NWOG 2026-08-02 (Qs/Os/Hs)

Einziges noch ungefülltes Gap; C.E. bei **28426.00**, rund 1750 Pkt unter der letzten bekannten Range (29780–30273) — weiterhin ein übergeordneter Draw-on-Liquidity nach unten, kein realistisches Intraday-Ziel für Dienstag.

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
- [[New Day Opening Gap (NDOG)]] — die vier gefüllten NDOGs der letzten *verfügbaren* Woche (17.–20.08.) bleiben mangels neuerer Daten die nächsten PD-Array-Bezugspunkte.
- [[New Week Opening Gap (NWOG) Bias]] — das offene NWOG vom 02.08. ist weiterhin der einzige unerfüllte Gap im Fenster und bleibt als übergeordneter Downside-Draw notiert.

## Einschätzung (Claude)

Dienstag ist saisonal der **schwächste Wochentag** in der eigenen Datenbasis: bullische Quote nur **50,5 %** (n=380, seit 2019) — praktisch Münzwurf und der niedrigste Wert aller Wochentage (Mo 61,4 %, Mi 55,3 %, Do 52,1 %, Fr 51,6 %) — bei mittlerem Tagesreturn **+0,056 %**. Die Range ist mit median 262,88 Pkt / avg 304,59 Pkt eher im unteren Mittelfeld. Kein starker statistischer Edge für Dienstag — Levels/PD-Arrays sollten stärker gewichtet werden als der Saisonalitäts-Bias. Grundlage: `algo/seasonal_tendency.json` (Wochentag Di), [[Seasonal Tendency (Eigene Daten, laufend)]].

Der News-Abruf ist fehlgeschlagen (Netzwerkfehler in dieser Cloud-Session, s.o.) — ob Red-Folder-Events anstehen, ist damit **nicht verifizierbar**. Ein FRED-Event-Backtest (`algo/backtest_fred_events.py`) entfällt deshalb.

Das offene NWOG vom 02.08. (C.E. 28426.00) bleibt ein weit entfernter übergeordneter Downside-Draw, kein Tagesziel. Näher an der zuletzt bekannten Range liegen die NDOG-C.E. der Woche 17.–20.08. (29322.00 / 29561.25 / 29563.00 / 30077.50) — mit der Einschränkung, dass seit dem 21.08. keine neuen Daten hinzugekommen sind und sich die tatsächliche aktuelle Range seither verschoben haben kann, ohne dass das hier sichtbar wäre.

ORG-C.E.-70%-These: **nicht anwendbar** (`org_ce` nicht gesetzt — IBKR-Gateway in dieser Cloud-Session nicht erreichbar, kein Live-Preis verfügbar; `market_data: false`).

**Wichtigster Punkt dieses Laufs ist nicht der Bias, sondern die Datenlücke** (s.o., Abschnitt Levels): Ohne frischen 1s-Nachlad beruhen alle Level hier auf einem zehn Tage alten Datenstand.

## Mein Bias

_(Nutzerbereich — bitte selbst ausfüllen)_
