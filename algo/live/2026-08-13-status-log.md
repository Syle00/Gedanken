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

## [2026-08-13 14:02 NY] Live-Status (first_run — Startaufnahme des ganzen Handelstages)

**Stand.** Preis **30.214,75**. ⚠️ Datenstand der Kerze ist **13:45 NY**, der Lauf 14:02 NY —
**17 Minuten Verzug**, die bekannte yfinance-Grenze bei MNQ=F. Alles unten ist auf 13:45 bezogen.
Aktives Makro-Fenster **13:50–14:10**, dazu **NY PM Silver Bullet** aktiv. `setup: null` — die
Regel hat für das Fenster keinen Trigger erzeugt.

- **ORG (Opening Range Gap):** Vortages-Close 29.830,75 (12.08. 16:15), Open 29.910,25,
  **Gap +79,50 nach oben**, C.E. **29.870,50**. **Innerhalb der ersten 30 Minuten gefüllt** —
  sogar in der 09:30-Kerze selbst (deren Tief 29.862,75 lief unter das C.E.). Ein Treffer für
  die ICT-These „C.E. zu 70 % gefüllt"; der eigene Backtest steht weiter bei 35–43 %, die These
  bleibt auf Wunsch in Beobachtung.
- **NDOG heute:** Vortages-Close 29.878,50 (23:55), Open 29.885,50, **Gap 7,00** — klein, um
  **00:10 gefüllt**. Passt zur empirischen Fill-Quote von 86 % (kleine Gaps füllen zuverlässiger).
- **NWOG:** `null` (Donnerstag).
- **Noch offene ältere Level (DOL-These):** NDOG 07.08. **29.488,25** (Gap 26,75), NDOG 12.08.
  **29.626,00** (Gap 37,00), NWOG 03.08. **28.404,25** (Gap 163,25). Alle drei liegen 590 bis
  1.810 Punkte **unter** dem Preis — heute keine realistischen Ziele, bleiben als Sellside-DOL
  im Blick.

**Abgleich.** `first_run: true`, die 74 Events sind die Startaufnahme des ganzen Tages, nicht das,
was gerade eben passierte. Der Tag deckt sich auffallend sauber mit dem Sweep-/Reclaim-Schema:

- **09:30 Sellside-Sweep 29.899,75 mit 37 Punkten Penetration, Reclaim in derselben Kerze**
  (`bars_back: 0`) — Tagestief 29.862,75. Direkt danach bullish **BOS 09:30** (Level 29.921,00,
  Close 29.945,75). Vorlauf gab es schon um 09:00 mit einem bullishen **MSS** (Level 29.894,00,
  Close 29.908,75), also vor dem RTH-Open.
- Von dort **+404 Punkte** bis zum Hoch **30.267,00** um 10:35. Der Move riss drei große bullishe
  FVGs auf, die bis heute unberührt sind (siehe Ausblick).
- **Das Weekly-Bias-Ziel aus dem Journal vom 10.08. — Buyside 30.094,00 — ist heute genommen und
  klar überschritten.** Ebenso das Interimsziel 29.931,75 aus dem Daily Bias von heute früh.
- Danach Verteilung: bearish **MSS 11:25** (30.194,00), Rücklauf bis 30.104,00, dann bullish
  **MSS 12:25** (30.173,25) und **BOS 13:00** (30.199,75) nach einem Buyside-Sweep um 12:50.
- Gegenüber dem letzten Eintrag (02:35 NY, Preis 29.902,50) sind das **+312 Punkte**.

**Ausblick.**

- **Direkt über dem Preis:** unberührte Buyside **30.250,25** (13:20) und **30.267,00** (10:35,
  Tageshoch) — nur 35 bzw. 52 Punkte entfernt. Das ist das naheliegende DOL für das laufende
  Makro-Fenster und die PM-Killzone.
- **Erste Auffanglinie darunter:** die bullishe FVG **30.193,50–30.216,50** (13:00) — angetastet,
  C.E. 30.205,00 noch **nicht** erreicht. Darunter 30.165,25–30.184,00 (12:25) und die noch völlig
  unberührte 30.143,75–30.165,50 (12:20).
- **Unberührte Sellside:** 30.176,25 / 30.133,25 / 30.104,00.
- **Die markanteste offene Imbalance des Tages** ist die bullishe FVG **30.053,75–30.119,00**
  (09:45, 65,25 Punkte, C.E. 30.086,50 nie erreicht). Wird der PM-Rücksetzer größer, ist das der
  stärkste Magnet — und sie deckt sich mit der unberührten Sellside 30.104,00.
- Darunter liegen als Reste des Vertikal-Moves noch 29.947,00–29.995,50 (09:35, 48,5 Pkt) und
  29.920,00–29.940,00 (09:30) — beide **komplett unberührt**, `touched: false`.
- Einschränkung: `raw/marktdaten` hat für heute nur bis 13:39 NY, der Live-Feed bis 13:45. Alles
  ab 13:45 ist in dieser Aufnahme nicht enthalten.
