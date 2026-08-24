# Algo-Kontext — NQ/ES-Handelsalgorithmus

> Diese Datei lädt automatisch, sobald eine Datei in `algo/` gelesen oder bearbeitet wird.
> Sie enthält die Algo-spezifischen Standards, die bis 2026-08-16 in der Haupt-`CLAUDE.md`
> standen. Für Wiki-, `raw/`- und `site/`-Regeln gilt weiterhin `../CLAUDE.md`.

## Layer 0 — Übergeordnetes Ziel: autonomer IBKR-Handelsalgorithmus

**Verfolge als Ziel von allem in diesem Repo** — Wiki, `raw/marktdaten/`, `tools/analyze_ohlc.py`,
`algo/` — einen Handelsalgorithmus für NQ und ES, der **selbstständig und allein über Interactive
Brokers** (TWS/IB-Gateway-API) handelt. NQ/ES statt MNQ seit 2026-08-15: sekundengenaue
IBKR-Daten liegen für beide vor (`algo/fetch_ibkr.py`), beide sind deutlich liquider, und die
Punktwerte (NQ $20, ES $50) sind in `algo/pnl.py` bereits hinterlegt — siehe
`docs/superpowers/specs/2026-08-15-ibkr-1s-datenanbindung-design.md`. Baue keinen Signal-Geber
für einen Menschen und betreibe kein Backtesting als Selbstzweck — das Ziel ist eine laufende,
autonome, profitable Ausführung mit echtem Geld. Behandle alles andere in diesem Dokument
(Wiki-System, Datenpflege, Backtesting) als
**Unterbau für dieses eine Ziel**, nicht als eigenständiges Ziel. Gewichte diese Priorität über
allen anderen Layern unten — bei einem Zielkonflikt (z.B. "schöneres Wiki" vs. "korrekterer
Backtest") entscheide zugunsten des Backtest-Ziels, siehe [[Algo-Trading: Arbeitsstandards]] unten.

Leite den Algorithmus über **echte, wachsende Datenbasis statt vorschneller Regeln** ab: baue aus
den täglich wachsenden OHLC-Daten in `raw/marktdaten/` einen regelbasierten, statistisch
validierten Handelsalgorithmus, der sich per IBKR-API selbstständig ausführt. Prüfe für den
aktuellen Umsetzungsstand, die Backlog-Punkte und das laufende Log `algo/PLAN.md` — dieses
Dokument dupliziert das nicht, sondern hält den *Rahmen* fest, in dem sich `algo/PLAN.md` bewegt.

Behandle das gesamte Wiki-System (Layer 1–3 unten) als Quelle für testbare Handelsregeln, weil
die ICT/SMC-Konzepte im Vault dafür da sind: Eine Wiki-Seite wie [[Silver Bullet Model]] gilt erst
dann als fertig verarbeitet, wenn du sie — sobald genug Daten vorliegen — als
`algo/rules.py`-Regel kodiert und gegen `raw/marktdaten/` gebacktestet hast. Behandle "Wissen
sammeln" und "Algo bauen" im Alltag als zwei verschränkte Tätigkeiten, nicht als getrennte
Projekte.

## Algo-Trading: Arbeitsstandards

Wende diese Regeln für `algo/`, `tools/analyze_ohlc.py` und `raw/marktdaten/` **verbindlich**
an, nicht optional — sie entstanden aus wiederholten Nutzerkorrekturen und gelten ab sofort ohne
erneute Nachfrage. Prüfe für den lebenden Implementierungsstand `algo/PLAN.md` (Backlog + Log)
und `algo/README.md` (Modul-für-Modul-Doku); dieser Abschnitt hält die *Regeln* fest, nicht den
*Stand*.

**Zeit vor Preis.** Der Nutzer geht davon aus, dass ein oder mehrere Algorithmen den Preis zu
bestimmten Uhrzeiten steuern (ICT-These "Time before Price"). Eine leicht falsche Zeitzuordnung
macht jede Musteranalyse wertlos, selbst wenn die OHLC-Werte an sich stimmen —
 Verifiziere bei jeder Datenpipeline
(Download, Resampling, Zeitzonen-Konvertierung) Timestamps aktiv gegen eine unabhängige Quelle
(z.B. bestehende TradingView-Exporte gegenprüfen), bevor du Daten als fertig meldest. Setze die
Datetime64-Auflösung immer explizit über `.as_unit("s")`, nie über manuelle Division — ein
stiller Pandas-Versionswechsel in der Auflösung (ns/us/s) ist genau der Fehlertyp, der hier am
meisten schadet (siehe `algo/fetch_yfinance.py`).

**Marktdaten wie Gold behandeln (Nulltoleranz).** Prüfe bei jedem Download, Import oder jeder
Bearbeitung von `raw/marktdaten/`: (1) Ist die Zeit gegen eine unabhängige Quelle geprüft? (2)
Sind die Daten vollständig — keine fehlenden Tage/Kerzen/Timeframes stillschweigend hinnehmen, Lücken
explizit auflisten? Melde dich bei jedem Zweifel (Daten wirken fehlerhaft, lückenhaft,
inkonsistent) **aktiv und ungefragt**, auch wenn der Rest der Aufgabe erledigt ist. Warne lieber
einmal zu oft, als einen fehlerhaften Datenpunkt durchrutschen zu lassen.

**Frische Live-Daten bei Zukunftsfragen.** Führe bei einer Frage des Nutzers zum aktuellen oder
zukünftigen Marktstand **immer zuerst `python algo/live_status.py` neu aus** — verlass dich nie
auf zuvor gelesene `raw/marktdaten/`-CSVs oder einen älteren Live-Lauf im selben Gespräch, auch
nicht bei Wiederholung der Frage. Bekannte Grenze: yfinance kann bei MNQ=F/ES=F mehrere Stunden
hinter der echten NY-Zeit zurückliegen — liegt `price.t` >15-20 Min hinter der aktuellen NY-Zeit
(bei 5m-TF), melde das aktiv, statt die Daten stillschweigend als aktuell auszugeben.

**Bekannte Grenze: yfinance kann auch auf Tick-Ebene vom Preis abweichen (nicht nur zeitlich).**
Am 12.08.2026 wich der `MNQ=F`-Feed am 9:30-Open um 0,5 Punkte von der Chart-/Broker-Quelle des
Nutzers ab (Root-Cause-Analyse: kein Pipeline-Bug, Zeitstempel korrekt — der Yahoo-Feed selbst
liefert diesen Preis, siehe `algo/PLAN.md`, Eintrag 2026-08-13). Prüfe bei präzisionskritischen
Berechnungen (ORG-C.E., Qs/Os/Hs, FVG-Grenzen, alles, was auf den exakten Tick ankommt) an Tagen,
die **nur** per `fetch_yfinance.py` ins Depot kamen (kein manueller TradingView-Export im selben
Ordner, erkennbar am Fehlen von `(2)`/`(3)`-Dateisuffixen), aktiv gegen die Chart-Quelle des
Nutzers gegen, statt die CSV blind als exakt zu behandeln.

**Ziel ist die volle Daily Range, nicht nur Bias.** Gehe über reine Richtungsvorhersage
(bullish/bearish) hinaus: Benenne konkrete OHLC-Zielzonen für die Tagesrange, gestützt auf PD
Arrays (Order Blocks, FVGs, NDOG/NWOG, Liquidity Pools), Session-Ranges (Asia/London/NY
Killzones) und wiederkehrende Zeitfenster-Muster. Suche explizit nach Mustern, die auf
algorithmisches Verhalten hindeuten, und benenne sie, statt nur Levels aufzulisten. Behandle
NDOG/NWOG dabei als besonders relevante PD Arrays — hinterlege bei jeder Analyse (insbesondere
`/algo-live-status`) die konkreten Opening-/Closing-Preise, nicht nur die Gap-Größe.

**Jede neue These wird automatisch geloggt und gebacktestet, ohne zu fragen.** Nennt der Nutzer
eine neue Trading-These oder Beobachtung (Frage oder Aussage), gehe unaufgefordert so vor: (1) Trage sie
in `algo/PLAN.md`s Log-Tabelle ein, (2) baue oder erweitere, wenn irgend möglich, ein
Backtest-Script dafür und lass es gegen alle verfügbaren Daten in `raw/marktdaten/` laufen
(Reuse-first: baue auf `tools/analyze_ohlc.py`-Detektoren und dem `find_days()`-Muster auf,
erfinde nicht jedes Mal neu; nutze einen eigenen Dateinamen `algo/backtest_<these>.py` pro
These), (3) berichte das Ergebnis ehrlich, auch wenn es der Nutzer-These widerspricht — beschönige
Zahlen nicht, um Zustimmung zu simulieren. Grund: Jede ICT-These ist im Rahmen dieses Projekts
kein Meinungsstück, sondern eine falsifizierbare Behauptung über ein Regelwerk, die geprüft
werden muss statt nur besprochen zu werden.

**Proaktiv gegenprüfen, offene Hypothesen halten, Falsifiziertes löschen.** Prüfe ständig gegen
und mach Vorschläge, statt nur auf explizite Backtest-Aufträge zu reagieren — taucht eine
Zahl/These im Gespräch auf, prüfe sie aktiv, statt zu warten. Halte unsichere Nutzeraussagen
("ich weiß nicht genau, ob...") als offene Hypothese in der passenden `wiki/synthesis/`-Seite
(Muster "(laufend)" im Namen) fest und aktualisiere sie bei neuen Daten. **Bewusste Ausnahme von
der generellen Widerspruchsregel** (siehe Seitenkonventionen oben): Behandle eigene
Backtest-Ergebnisse nicht als zwei gleichwertige Meinungen, sondern als nachprüfbare Zahl —
stellt sich ein früherer Fund mit mehr Daten als Rauschen heraus, **entferne** ihn, statt ihn als
„⚠️ widerlegt" stehenzulassen. Ausdrücklich anders: Lass eine vom Nutzer explizit als "weiter
beobachten" markierte These (z.B. die ORG-C.E.-70%-These, aktuell 35-43% im eigenen Backtest)
trotz widersprechender Zahlen aktiv bestehen und kommentiere sie in jedem neuen Bericht, statt
sie als erledigt/widerlegt abzuhaken — der Nutzer entscheidet hier explizit gegen das
Standard-Löschverfahren.

**Korrektheit vor Features, weil reales Geld geplant ist.** **Behebe** Backtest-Code, der
Zahlen liefert, die nicht dem realen Kontrakt-P&L entsprechen (Notional-Prozent statt echtem
Punktwert, geratene statt konservativ aufgelöste Stop/Ziel-Reihenfolge in derselben Kerze,
Lookahead-Bias, Data-Leakage), **mit höchster Priorität** — vor neuen Strategien, vor Optik-/Dashboard-
Verbesserungen. Prüfe bei jedem neuen Backtest-Script oder jeder Erweiterung zuerst: (1) echter
Punktwert/Kontraktgröße statt Notional-Prozent, (2) konservative statt geratene Fill-Reihenfolge
bei Stop/Ziel in derselben Kerze (`dubious_pct` als Pflichtkennzahl in jedem Report), (3) kein
Lookahead in Signalen/Modellen (nur `bars[t<=when]`). Repariere gefundene Bugs **direkt**, ohne
vorherige Freigabeschleife pro Einzelfund — ein Bericht am Ende reicht. Behandle Optik-Wünsche
(z.B. "Bloomberg-Terminal-Look" für `dashboard.py`) explizit als nachrangig und setze sie nur
auf separate Anfrage um. Lass `algo/selfcheck.py` (bündelt die Regressions-Selbstchecks `pnl`,
`rules`, `signals`, `backtest_ensemble`) vor größeren Refactors laufen.

**Marktdaten-Lücken nachträglich schließbar.** Fehlt in einem ingesteten Export ein Zeitabschnitt
(z.B. ein ganzer Monat in `raw/trading-ict/Core Content/`), prüfe vor dem Nachfragen beim Nutzer,
ob der YouTube-Kanal `@InnerCircleTrader` dieselben Inhalte als Video-Reihe hat (Suchmuster
`"ICT Mentorship Core Content - Month <NN>"`) — das `yt-ict-ingest`-Skill deckt den technischen
Ablauf ab.

## Algo-Trading: Roadmap zur IBKR-Anbindung

Folge dieser Reihenfolge, in der sich das Projekt Richtung Layer-0-Ziel bewegt — jede Stufe baut
auf der vorherigen auf, überspringe keine:

1. **Datensammlung (laufend, nie abgeschlossen).** Lass `raw/marktdaten/` täglich wachsen
   (TradingView-Export + `algo/fetch_yfinance.py`-Nachlad), begrenzt durch yfinance-Limits
   (1m ~30 Tage, 5m/15m ~60 Tage, 1d unbegrenzt zurück). Für NQ/ES steht seit 2026-08-15
   sekundengenaue IBKR-Historie zur Verfügung (`algo/fetch_ibkr.py`, `/daten-1s`) — IBKR ist
   damit die primäre Intraday-Quelle für diese beiden Symbole, nicht mehr nur ein
   perspektivischer Kandidat; historische Daten und Live-Order-Ausführung laufen über denselben
   Broker, das vermeidet Datenquellen-Drift zwischen Backtest und Live-Betrieb.
2. **Regel-Schicht (laufend).** Übersetze Wiki-Konzepte (`wiki/models/`) in deterministische
   Python-Regeln (`algo/rules.py::plan_trade` als erstes Beispiel: Silver Bullet Model). Folge
   bei jeder neuen Regel [[Algo-Trading: Arbeitsstandards]] — kein Lookahead, Reuse bestehender
   Detektoren aus `tools/analyze_ohlc.py`.
3. **Validierung (Standardwerkzeug für jede Regel, nicht optional).** Verlass dich nicht auf
   einen Einzelbacktest (`backtest_bt.py`) — lass Parameter-Sensitivität, Walk-Forward
   (rollierende Folds, Out-of-Sample ohne Refit) und Monte-Carlo-Resampling (`validate.py`) für
   jede Regel laufen, bevor eine Zahl als belastbar gilt. Führe Stress-Tests gegen historische
   Krisenfenster (`stress_test.py`) für die Verhaltenscharakterisierung unter Extrembedingungen
   durch. Bringe eine Regel erst dann zum nächsten Schritt, wenn sie hier über mehrere Verfahren
   hinweg konsistent (nicht zwingend profitabel, aber *verstanden*) abschneidet.
4. **IBKR-Adapter, dünn und broker-unabhängig gehalten.** Baue `algo/broker_ibkr.py` (noch nicht
   angelegt) für die Order-Ausführung über TWS/IB-Gateway-API (`ib_insync` oder offizielles
   `ibapi`) hinter einer schmalen Schnittstelle (`place_order`, `get_position`, `cancel`) — halte
   die Regel-Schicht broker-unabhängig, damit sie weiter isoliert testbar bleibt. Beginne das
   erst nach Punkt 2+3, nicht parallel dazu.
5. **Paper-Trading zuerst, ausnahmslos.** Lass den Adapter zuerst gegen ein
   IBKR-Paper-Trading-Konto laufen. Wechsle nie zu echtem Kapital ohne expliziten, gesonderten
   Freigabeschritt durch den Nutzer — das ist keine Formalie, sondern eine harte Sperre in diesem
   Projekt: Aktiviere Live-Handel mit echtem Geld nie stillschweigend aus einer anderen Aufgabe
   heraus.
6. **Live-Betrieb, nach expliziter Freigabe.** Betreibe erst danach die laufende Ausführung, mit
   kontinuierlichem Monitoring (`algo/dashboard.py`-Nachfolger oder eigenes Live-Reporting) und
   demselben Korrektheits-Standard wie im Backtest (echter $-P&L, keine Notional-Näherung).

**Security-Gate.** Stelle den Secret-Scan, sobald echte IBKR-Keys ins Spiel kommen (spätestens
Punkt 4), von "einmalig/gelegentlich" auf ein festes Intervall um (mind. wöchentlich, vor jedem
Live-Übergang zwingend) — aktuell (Stand 2026-08-07) ohne Live-Keys unnötiger Aufwand, das kippt
aber mit dem ersten Broker-Zugangsdaten-File.

## Protokoll- und Datenartefakte

Halte diese Artefakte gepflegt, damit "laufende Daten verbessern den Algo" ein Mechanismus
bleibt, keine Absicht:

- `algo/PLAN.md` — Backlog + chronologisches Log (Datum, Ereignis) für alles, was in `algo/`
  passiert: neue Thesen, Backtest-Ergebnisse, Bugfixes mit Zahlen-Auswirkung. Führe es als
  primäres Protokoll für die Algo-Arbeit, feingranularer als `wiki/log.md`.
- `wiki/synthesis/*.md` mit `(laufend)` im Namen — aggregierte Auswertungsseiten, die sich mit
  wachsendem Datenbestand aktualisieren (z.B. `Muster-Validierung (laufend).md`,
  `Statistische Muster jenseits der ICT-Konzepte (laufend).md`). Überschreibe/erweitere sie bei
  jedem neuen Backtest-Lauf, lass sie nicht als Schnappschuss stehen.
- `algo/seasonal_tendency.json` — versionierte Kennzahlen-Datenbank (Wochentag/Monat/
  Turn-of-Month/Woche-im-Monat), gedacht für Jahr-über-Jahr-Vergleiche statt Neuberechnung bei
  jeder Frage.
- `algo/README.md` — ein Abschnitt pro Modul (Was/Wie/Warum/bekannte Grenzen). Pflege ihn bei
  jeder inhaltlichen Code-Änderung, damit der Nutzer ohne Code-Lesen nachschlagen kann.
- `algo/live/<datum>/` + `algo/live/<datum>-status-log.md` — transiente Live-Ziehung
  (gitignored) plus versioniertes Text-Protokoll der `/algo-live-status`-Läufe.

## Domänenkontext: algo (NQ/ES-Backtesting)

`algo/` enthält den gesamten Backtesting-/Validierungs-Stack für Layer 0 (siehe `algo/README.md`
für die Modul-für-Modul-Doku, `algo/PLAN.md` für Stand/Backlog/Log). Kernkomponenten: `pnl.py`
(Punktwert-Präzisionsschicht), `rules.py`/`signals.py` (Regel-/Signal-Schicht),
`backtest_bt.py`/`backtest_ensemble.py` (Trade-Simulation), `validate.py`/`stress_test.py`
(Validierung), `live_status.py` (Live-Loop), `selfcheck.py` (Regressionscheck). Aktuelle
Symbol-Punktwerte: MNQ=$2, NQ=$20, ES=$50 — trage für ein neues Symbol zuerst einen neuen Eintrag
in `pnl.py` ein, bevor du `real_pnl`/`risk_size` dafür nutzt.
