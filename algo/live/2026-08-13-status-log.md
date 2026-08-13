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

## Nachtrag: Daily-Bias-Kontext (aus journal/entries/2026-08-13 MNQ Daily Bias.md)

Fehlte im ersten Durchlauf, live_status.py liest nur Marktdaten, keinen Journal-Bias.

- **Bias heute**: bullish bis Buyside — Fortsetzung des seit `2026-08-10 MNQ Weekly Bias`
  laufenden Wochen-Bias. Interimsziel **29.931,75**, übergeordnetes Wochenziel **30.094,00**.
  Preis aktuell (29893.75) liegt noch unter beiden Zielen, klarer Aufwärts-Bias.
- **PPI-News heute 8:30 NY** — mehr Volatilität erwartet, relevant für spätere Fenster.
- **NDOG/NWOG-Gültigkeitsdauer** (neu, `wiki/concepts/New Day Opening Gap (NDOG).md`): NDOG bleibt
  mind. **5 Handelstage**, NWOG mind. **5 Handelswochen** aktiv — darüber hinaus laut Nutzer
  weiter als DOL nutzbar, bislang unbacktestete Nutzeraussage. Der heutige `live_status.py`-Output
  zeigt nur das *aktuelle* NDOG (Fill um 00:10 NY); ältere, noch unerreichte NDOG-/NWOG-Level der
  letzten 5 Tage/Wochen sind darin nicht enthalten — dafür müsste `live_status.py` erweitert
  werden (offener Punkt, siehe unten).
- **Zeitbasierte Algorithmen**: Nutzer vermutet laut ICT weitere algorithmische Zeitfenster über
  die bekannten Macros hinaus — noch keine konkrete neue Uhrzeit benannt, offene Suche.

**Offener Punkt für `algo/live_status.py`**: aktuell wird nur das NDOG/NWOG der letzten 1-2 Tage
getrackt. Um die 5-Tage/5-Wochen-These operativ nutzbar zu machen, müsste der Live-Status auch
ältere, noch ungefüllte NDOG-/NWOG-Level als eigene `untouched_levels`-Kategorie führen.

## [2026-08-13 02:35 NY] Update: NDOG-/NWOG-Historie ergänzt

Der offene Punkt oben ist erledigt: `algo/live_status.py` liefert jetzt zwei neue Felder
`ndog_history`/`nwog_history` — die letzten 5 Handelstage (NDOG) bzw. 5 Handelswochen (NWOG)
vor heute, gefiltert auf Level, die seither noch **nicht** wieder erreicht wurden (DOL-These aus
dem Daily-Bias-Journal 13.08.). Reuse: `ndog_gap()`/`nwog_gap()` aus `tools/analyze_ohlc.py`
unverändert, neue Funktion `open_gap_history()` prüft nur zusätzlich per Daily-Bars, ob das Level
zwischen Gap-Tag und heute je berührt wurde (nicht nur am Gap-Tag selbst wie bisher).

Aktueller Live-Lauf zeigt zwei noch offene NDOG-Level und ein offenes NWOG-Level:

| Typ  | Tag        | Level      | Gap-Größe |
|------|------------|------------|-----------|
| NDOG | 2026-08-07 | 29.488,25  | 26,75     |
| NDOG | 2026-08-12 | 29.626,00  | 37,00     |
| NWOG | 2026-08-03 | 28.404,25  | 163,25    |

Alle drei liegen deutlich unter dem aktuellen Preis (29.902,50) — passt zum bullishen Bias, diese
Level sind aktuell keine naheliegenden Ziele, bleiben aber als Sellside-DOL im Blick, falls der
Preis vor dem Buyside-Ziel noch mal zurückfällt. `--dry-run` liefert diese Felder bewusst leer
(kein Multi-Day-Fetch dort), `--selftest` deckt `open_gap_history()` mit synthetischen Tageskerzen
ab. Alle 4 Selftests und alle 16 `algo/selfcheck.py`-Checks laufen grün.
