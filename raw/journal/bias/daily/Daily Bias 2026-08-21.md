# Daily Bias 2026-08-21

> Weekly Bias: [[Weekly Bias KW34 2026]]

## News (Red/Orange Folder)

Quelle: **TradingView** (ForexFactory nicht erreichbar: `URLError 403 Forbidden` → TradingView-Kalender-Fallback; Uhrzeiten beider Quellen deckungsgleich geprüft)

**Fr 21.08.** ❌ keine USD-Termine

→ Newsarmer Tag: kein Red-/Orange-Folder-Event mit USD-Impact.

## Levels

**Datenlage (NQ):** 23 Tage 1s-Daten, keine nur-1m-Tage, keine registrierten Tage ohne Datei. 1s-vs-1m-Abgleich unkritisch (max. Abweichung 2,0 Pkt am 30.07., sonst ≤ 1,75 Pkt).

| Level | Datum | Close (17:00) | Open (18:00) | Gap | C.E. | Status |
|---|---|---|---|---|---|---|
| NWOG | 2026-08-02 | 28287.00 | 28565.00 | +278.00 | 28426.00 | **offen** |
| NDOG | 2026-08-18 | 29559.50 | 29566.50 | +7.00 | 29563.00 | gefüllt |
| NDOG | 2026-08-17 | 30078.25 | 30077.00 | −1.25 | 30077.50 | gefüllt |

- **Gestrige Daily Range (2026-08-19):** H 29757.25 / L 29375.75 / C 29561.00
- Weekly Range: _(kein Wert in den Daten — Zeile weggelassen)_
- ORG-C.E.: _(entfällt — Markt geschlossen, keine Live-Daten)_

### Offenes Gap — NWOG 2026-08-02 (Qs/Os/Hs)

Einziges noch ungefülltes Gap; C.E. bei **28426.00**, rund 1135 Pkt unter dem gestrigen Close — Draw-on-Liquidity nach unten, kein Intraday-Ziel für Freitag.

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
- [[New Day Opening Gap (NDOG)]]
- [[New Week Opening Gap (NWOG) Bias]] — wegen des offenen NWOG vom 02.08.

## Einschätzung (Claude)

Freitag ist saisonal der neutralste Wochentag: bullische Quote **51,6 %** (n=372, seit 2019), mittlerer Tagesreturn faktisch null (+0,013 %), und mit **median 245 Pkt** die **kleinste Range der Woche** (vgl. Do 281, Mi 278). Statistisch also eher ein Konsolidierungs-/Rangetag ohne klare Richtungserwartung.

Dazu ein **newsarmer Tag** ohne USD-Red/Orange-Termine → kein externer Katalysator, der die typische Freitags-Kompression aufbricht. Der gestrige Close (29561) liegt etwa mittig in der gestrigen Range — kein starkes Ungleichgewicht, das eine Fortsetzung erzwingt.

Das offene NWOG (C.E. 28426) ist als übergeordneter Draw nach unten notiert, aber mit ~1135 Pkt Abstand kein realistisches Tagesziel; relevanter für die intraday-Struktur sind die frischen NDOG-C.E. der laufenden Woche (29563 / 30077.50) als nahe Bezugspunkte.

ORG-C.E.-70%-These: **nicht anwendbar** (org_ce nicht gesetzt, Markt geschlossen). Keine Red-Folder-Events → kein FRED-Event-Backtest nötig.

Grundlage: `algo/seasonal_tendency.json` (Wochentag Fr), [[Seasonal Tendency (Eigene Daten, laufend)]].

## Mein Bias

_(Nutzerbereich — bitte selbst ausfüllen)_
