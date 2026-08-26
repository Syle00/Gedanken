# Daily Bias 2026-08-25

> Weekly Bias: [[Weekly Bias KW35 2026]]

## News (Red/Orange Folder)

⚠️ News-Abruf fehlgeschlagen (`URLError: <urlopen error Tunnel connection failed: 403 Forbidden>`), manuell auf forexfactory.com prüfen. (Sowohl ForexFactory- als auch der TradingView-Fallback scheiterten am selben Netzwerkfehler — in dieser Cloud-Session ist ausgehender Zugriff auf beide Domains offenbar blockiert.)

## Levels

**Datenlage (NQ):** 23 Tage 1s-Daten, keine nur-1m-Tage, keine registrierten Tage ohne Datei. 1s-vs-1m-Abgleich unkritisch (max. Abweichung 2,0 Pkt am 30.07., sonst ≤ 1,75 Pkt).

| Level | Datum | Close (17:00) | Open (18:00) | Gap | C.E. | Status |
|---|---|---|---|---|---|---|
| NWOG | 2026-08-02 | 28287.00 | 28565.00 | +278.00 | 28426.00 | **offen** |
| NDOG | 2026-08-20 | 29317.25 | 29327.00 | +9.75 | 29322.00 | gefüllt |
| NDOG | 2026-08-19 | 29561.00 | 29561.50 | +0.50 | 29561.25 | gefüllt |
| NDOG | 2026-08-18 | 29559.50 | 29566.50 | +7.00 | 29563.00 | gefüllt |
| NDOG | 2026-08-17 | 30078.25 | 30077.00 | −1.25 | 30077.50 | gefüllt |

- **Gestrige Daily Range (2026-08-21):** H 29539.00 / L 29220.00 / C 29374.00 — letzter vollständiger Handelstag zum Zeitpunkt dieses Laufs (20:16 CEST / 14:16 NY); Montag 24.08. war zur Laufzeit noch nicht abgeschlossen, deshalb fällt der Skript-Fallback auf Freitag zurück statt eine unvollständige Montags-Range zu zeigen.
- Weekly Range: _(kein Wert in den Daten — Zeile weggelassen)_

### Offenes Gap — NWOG 2026-08-02 (Qs/Os/Hs)

Einziges noch ungefülltes Gap; C.E. bei **28426.00**, rund 950 Pkt unter der letzten bekannten Range (29220–29539) — weiterhin ein übergeordneter Draw-on-Liquidity nach unten, kein realistisches Intraday-Ziel für Dienstag.

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

Dienstag ist saisonal der **schwächste Wochentag** in der eigenen Datenbasis: bullische Quote nur **50,5 %** (n=380, seit 2019) — praktisch Münzwurf und der niedrigste Wert aller Wochentage (Mo 61,4 %, Mi 55,3 %, Do 52,1 %, Fr 51,6 %) — bei mittlerem Tagesreturn **+0,056 %**, ebenfalls deutlich unter Montag. Die Range ist mit median 262,88 Pkt / avg 304,59 Pkt eher im unteren Mittelfeld (kleiner als Mo/Mi/Do, nur knapp über Fr). Kein starker statistischer Edge für Dienstag — Levels/PD-Arrays sollten hier stärker gewichtet werden als der Saisonalitäts-Bias.

Der News-Abruf ist wie bereits gestern fehlgeschlagen (derselbe Netzwerkfehler in dieser Cloud-Session, s.o.) — ob Red-Folder-Events anstehen, ist damit **nicht verifizierbar**. Ein FRED-Event-Backtest (`algo/backtest_fred_events.py`) entfällt deshalb; das sollte manuell nachgeholt werden, sobald der Kalender wieder erreichbar ist.

Das offene NWOG vom 02.08. (C.E. 28426.00) bleibt ein weit entfernter übergeordneter Downside-Draw, kein Tagesziel. Relevanter für die kurzfristige Struktur sind die NDOG-C.E. der Vorwoche (29322.00 / 29561.25 / 29563.00 / 30077.50) als nahe PD-Array-Bezugspunkte um die zuletzt bekannte Range (29220–29539).

ORG-C.E.-70%-These: **nicht anwendbar** (`org_ce` nicht gesetzt — IBKR-Gateway in dieser Cloud-Session nicht erreichbar, `ib_async` zudem nicht installiert, kein Live-Preis verfügbar).

Grundlage: `algo/seasonal_tendency.json` (Wochentag Di), [[Seasonal Tendency (Eigene Daten, laufend)]].

## Mein Bias

_(Nutzerbereich — bitte selbst ausfüllen)_
