# Live-Status-Log 2026-08-13

## [2026-08-13 02:23 NY] Status

**Stand:** Preis 29893.75 (Stand 02:10 NY) — wir befinden uns in der frühen Asia-Session, kein
aktives Makro- oder Silver-Bullet-Fenster gerade. NDOG heute: Vortages-Close 29878.5 (Di 23:55 NY)
vs. heutiger Open 29885.5 → Gap nur 7.0 Punkte (klein), bereits um 00:10 NY gefüllt — passt zur
empirischen NDOG-Fill-Quote von 86% (siehe `algo/backtest_ndog.py`), bei so kleinen Gaps ohnehin
erwartbar. Kein NWOG (Donnerstag, kein Wochenstart). ORG-C.E. noch `null`, da die NY-Session-Open
(9:30 NY) noch nicht erreicht ist.

**Abgleich:** `new_events` ist leer — seit dem letzten Lauf (bzw. da noch kein Log für heute
existierte: seit Sessionbeginn) ist nichts Neues aufgelaufen. Kein Setup aktiv, kein Fenster offen.

**Ausblick:** Nächstes relevantes Zeitfenster ist die London-Killzone bzw. später NY-Open
(9:30 NY) — dort wird `org_ce` erstmals gefüllt. Unberührte Liquidität liegt aktuell überwiegend
sellside darunter (29780.5 – 29854.0, mehrere Pools aus der Asia-Range) sowie ein buyside-Pool bei
29924.25 (01:30 NY) knapp über dem aktuellen Preis — dieser buyside-Pool ist der nächstliegende
und am ehesten kandidiert für einen Sweep vor der London-Session.
