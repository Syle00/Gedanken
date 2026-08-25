---
tags: [concept, futures, gold, kontrakt, daten]
created: 2026-08-25
updated: 2026-08-25
sources: []
---

# Kontraktspezifikation GC (COMEX-Gold)

Der Standard-Goldfuture an der COMEX (CME Group). Seit 2026-08-25 als drittes Symbol
neben NQ und ES in der 1s-Datenanbindung (`algo/fetch_ibkr.py`) unterstützt.

| Merkmal | GC | MGC (Micro) |
|---|---|---|
| Kontraktgröße | 100 Feinunzen | 10 Feinunzen |
| Tick | 0,10 USD/Unze | 0,10 USD/Unze |
| Tickwert | 10 USD | 1 USD |
| Börse | COMEX (**nicht** CME) | COMEX |

## Unterschiede zu NQ/ES, die im Code zählen

- **Börse**: `Future(exchange="COMEX")`. Mit `exchange="CME"` findet IBKR den Kontrakt nicht.
- **Kontraktzyklus**: gerade Monate — G (Feb), J (Apr), M (Jun), Q (Aug), V (Okt), Z (Dez).
  NQ/ES laufen dagegen im Quartalszyklus H/M/U/Z.
- **Roll-Termin**: Gold hat keinen Verfall am dritten Freitag. Der Kontrakt verliert das
  Volumen schon vor dem **First Notice Day** (letzter Geschäftstag des Vormonats), weil ab
  dann physische Andienung droht. Im Code genähert als *5 Kalendertage vor Monatsbeginn*
  des Liefermonats — z.B. läuft GCZ2026 bis 26.11.2026, danach ist GCG2027 Front-Monat.
- **Session**: identisch zu den CME-Indexfutures, 18:00 NY Vortag bis 17:00 NY
  (`SESSION_TYP = "futures_rth"`), damit greifen [[ORG]]/[[NDOG]]-Logik unverändert.

## Datenqualität

Erste Messung beim 183-Tage-Backfill (Start 2026-08-25): durchgehend 1800 Kerzen je
30-Minuten-Fenster, also keine handelslosen Sekunden in der asiatischen Session — GC ist
auf 1s-Ebene deutlich dichter als erwartet.

Siehe auch [[Kontraktspezifikation MNQ (Tick, Punktwert)]],
[[Futures-Datenaufbereitung & Backtesting-Fallstricke (Chan)]].
