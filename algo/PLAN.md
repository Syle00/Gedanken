# Algo-Trading-Projekt — Planungsdokument

## Schicht 1 — Übergeordnetes Ziel

**Das ist das Ziel von allem hier** — Wiki, `raw/marktdaten/`, `tools/analyze_ohlc.py`, dieser
Ordner: ein Handelsalgorithmus, der **selbststaendig und allein ueber Interactive Brokers**
(TWS/IB-Gateway-API) handelt. Kein Signal-Geber fuer einen Menschen, kein Backtest-Spielzeug —
am Ende steht eine laufende, autonome Ausfuehrung. Alles andere in diesem Dokument (Fundament,
offene Punkte, Backtesting) ist **Unterbau fuer dieses eine Ziel**, keine eigenstaendigen Ziele.

Status: **Planungsphase, kein Code.** Der Weg dahin fuehrt ueber echte, wachsende Datenbasis
statt ueber vorschnelle Regeln: aus den taeglich wachsenden OHLC-Daten in `raw/marktdaten/`
einen regelbasierten Handelsalgorithmus fuer MNQ ableiten, der sich per IBKR-API selbststaendig
ausfuehrt.

## Datengrundlage

- `raw/marktdaten/<jjjj>/<mm>/<dd.mm.jjjj>/` — ein Ordner pro Handelstag, TradingView-Exporte in
  1m/5m/15m/1h/4h/1d. Jahr/Monat verschachteln sich von selbst beim Wechsel, damit der Ordner
  bei taeglichen Exporten nicht flach mit hunderten Tagesordnern volllaeuft. Konvention:
  [[OHLC-Datenanalyse (Workflow)]].
- Ab jetzt taeglich neu: TradingView-Export flach nach `raw/marktdaten/` legen,
  `tools/sort_marktdaten.py` raeumt automatisch ein (laeuft auch vor jedem `push.ps1` und
  vor jedem `analyze_ohlc.py`-Aufruf).
- Bisher eingesammelte Tage: siehe Log unten.

## Bereits vorhandenes Fundament

`tools/analyze_ohlc.py` rechnet pro Tag bereits:

- Opening Prices (Midnight/8:30/9:30/13:30), Session-Level (Asia/London/NY AM/PM/...)
- Liquidity Sweeps (mit Levelalter + Penetration + Bestaetigungsfenster)
- Market Structure Breaks (BOS/MSS, sequenziell)
- Displacement-Kerzen, Fair Value Gaps (Groesse, CE, Fuellstatus)
- Macro-Fenster-Expansion (Jannes' XX:50–XX+1:10-Raster)
- Consolidation-Phasen, unangetastete Liquiditaet am Datenende
- Setup-Checkliste gegen einen Zeitpunkt (`--at HH:MM`), 7 von 8 Punkten objektiv pruefbar

Das ist die Rohmasse fuer den Algorithmus — noch keine Handelslogik, nur Erkennung.

## Was fuer einen Algorithmus noch fehlt

1. **Backtesting-Harness. Erste Version existiert:** `algo/backtest_ohlc.py`. Laeuft ueber
   alle Handelstage in `raw/marktdaten/`, importiert dieselben Detektoren aus
   `tools/analyze_ohlc.py` (`fvgs`, `viis`, `sweeps`, `structure_breaks`, `macro_windows` —
   keine Neuimplementierung) und schreibt die Aggregation nach
   `wiki/synthesis/Muster-Validierung (laufend).md`. Bleibt bewusst Standardbibliothek wie
   `analyze_ohlc.py` selbst — die Aggregation ist eine Handvoll Zaehler, kein
   DataFrame-Problem. **Wichtige Falle, auf die man achten muss:** `analyze_ohlc.py` skaliert
   `min_age`/`confirm` beim CLI-Aufruf mit dem Timeframe (in `main()`); wer die Detektoren
   direkt importiert, muss dieselbe Skalierung von Hand anwenden, sonst laufen Tagesreport
   und Backtest mit verschiedenen Schwellen und liefern nicht vergleichbare Zahlen (genau
   dieser Fehler ist beim ersten Entwurf passiert und wurde noch am selben Tag gefixt).
   **Werkzeugentscheidung pandas/matplotlib** bleibt fuer den Explorations-/Visualisierungs-
   Layer (`algo/viz_prototype.py` + `.html`, Zeitzonen/Fenster-Slicing sind dort eine Zeile
   statt einer Schleife) — beide Wege liefern dieselben Zahlen (Macro-Range 175,00 Pkt
   deckungsgleich). Abhaengigkeiten fuer den pandas-Pfad: `algo/requirements.txt`.
   **Naechster Ausbauschritt (Nutzerwunsch "alle PD Arrays, das gesamte Wiki"):** siehe
   Abdeckungs-Tabelle in der generierten Seite selbst — Order-Block-Varianten, IFVG, BPR,
   CBDR, NWOG/NDOG, OTE, Breakaway Gap, Suspension Block, Judas-Swing-Zeitfenster und
   SMT (zweites Symbol noetig) haben noch keinen Detektor.
2. **Harte Entry-/Exit-/Stop-/Target-Regeln.** Die 8er-Checkliste ist eine manuelle
   Pruefliste fuer einen Menschen ("Entry bleibt deine Entscheidung"). Ein Algorithmus
   braucht stattdessen eine deterministische Regel, die aus denselben Daten einen
   Trigger + Stop + Ziel ableitet.
3. **Stichprobengroesse.** Aktuell liegen 2 Handelstage vor (31.07., 03.08.2026). Fuer
   belastbare Aussagen zu Killzone-Trefferquote, Macro-Expansion-Rate oder
   Silver-Bullet-Fenstern braucht es Wochen bis Monate. Vor Regel-Festlegung: weiter
   sammeln, nicht auf 2 Tage ueberfitten.
4. **Risk-/Money-Management.** Positionsgroesse, Stop-Distanz relativ zur gesweepten
   Liquiditaet, Max-Trades/Tag — bisher nirgends im Vault spezifiziert.
5. **Pattern-Prioritaet.** Kandidaten aus dem Wiki, sobald genug Tage vorliegen:
   [[Silver Bullet Model]], [[NY Lunch Macro Model]], [[Judas Swing]] / AM-Reversal,
   [[Midnight Opening Range]] STD-Projektion, [[ORG (Opening Range Gap) & 1st Presented FVG]].

## Code-Ideen (Backlog — notiert, noch nicht umgesetzt)

Ideen werden hier gesammelt, sobald sie auftauchen, statt verloren zu gehen oder verfrueht
implementiert zu werden. Kein Punkt hier ist beauftragt — erst wenn genug Tage vorliegen
(siehe oben), wird priorisiert und gebaut.

1. ~~`tools/backtest_ohlc.py`~~ **erledigt, siehe oben** — liegt unter `algo/backtest_ohlc.py`
   statt `tools/`, sonst wie geplant: laeuft ueber alle Tagesordner, aggregiert die
   bestehenden Detektoren, schreibt nach `wiki/synthesis/Muster-Validierung (laufend).md`.
   Nutzer wollte es sofort mit den vorhandenen 2 Tagen starten statt auf 20-30 Tage zu
   warten — die Seite selbst warnt jetzt explizit vor der kleinen Stichprobe, statt zu warten.
2. **Regel-Schicht statt Checkliste — erste Regel steht:** `algo/rules.py`, `plan_trade(bars,
   when) -> TradeSetup | None`. Setzt das [[Silver Bullet Model]] um (drei Zeitfenster,
   FVG im Fenster als Trigger, Entry = FVG-C.E., Stop = FVG-Gegenkante + Puffer, Ziel = naechstes
   Level aus `untouched_levels()`). Laeuft nur auf `bars[t<=when]` (kein Lookahead). Smoke-Test
   gegen alle 26 Juli-Tage: erzeugt an einem Tag ein Setup, an den anderen korrekt `None`
   (meist weil keine unberuehrte Zielliquiditaet vorliegt) — noch nicht gegen viele Tage
   validiert, siehe Stichprobengroesse unten. Noch offen: nur die Basisregel aus dem Wiki
   (Fenster + FVG + Ziel), die dort genannte zusaetzliche Confluenz (NWOG/NDOG, Midnight
   Opening Fibs, 1. presented FVG) fliesst noch nicht ein; der "2022 Entry" (FVG als IFVG in
   Gegenrichtung, siehe [[Silver Bullet Model]]) ist eine Variante, keine Pflicht, und bewusst
   nicht die erste Version. **Trade-Simulation steht:** `algo/backtest_bt.py` verdrahtet `plan_trade()` in eine
   `backtesting.Strategy` (PyPI-Bibliothek `backtesting`, kein Eigenbau fuer Equity/Drawdown/
   Bracket-Orders). Erster Lauf ueber alle 26 Juli-Tage (5m, MNQ): 53 Trades, Win Rate 15%,
   Profit Factor 0,32, Expectancy -0,046%/Trade — die Basisregel ohne Confluenz verliert auf
   dieser (kleinen) Stichprobe. Zwei Einschraenkungen vor jeder Interpretation: (1) `backtesting`
   preist wie eine Aktie (Notional * Commission-Rate, keine MNQ-Punktwerte) — die $-Kennzahlen
   (Equity, Commissions, Sharpe) sind daher keine echte MNQ-P&L, nur die Prozent-/Trade-Kennzahlen
   (Win Rate, Profit Factor, Expectancy) sind aussagekraeftig; fuer echte $-P&L braeuchte es eine
   eigene Auswertung von `stats._trades` mit Punktwert $2/Punkt statt `stats.Equity Final`.
   (2) Der Stop-Puffer (10% der FVG-Groesse) ist oft kleiner als das Rauschen einer einzelnen
   5m-Kerze — `backtesting` markiert dutzende Trades explizit als "dubious", weil SL/TP in
   derselben Kerze wie der Entry ausgeloest wird (Intra-Kerze-Reihenfolge unbekannt). Vermutlich
   Hauptursache fuer die niedrige Win Rate, noch nicht behoben. Naechste Schritte vor einer
   echten Bewertung: Stop-Puffer vergroessern/testen, Confluenz-Filter (NWOG/NDOG, Midnight
   Opening Fibs, 1. presented FVG) ergaenzen, mehr Tage sammeln.
3. **IBKR-Anbindung als eigener, duenner Adapter** (`algo/broker_ibkr.py`, noch nicht
   angelegt): Order-Ausfuehrung ueber die Interactive-Brokers-API (TWS/IB-Gateway, z.B. per
   `ib_insync` oder offiziellem `ibapi`) hinter einer schmalen Schnittstelle
   (`place_order`, `get_position`, `cancel`), damit die Regel-Schicht broker-unabhaengig
   bleibt. Erst nach Punkt 1+2, und zuerst gegen ein Paper-Trading-Konto, nie direkt live.
4. **Backtest-Ergebnisse als Datenartefakt**, nicht nur als Konsolenausgabe: eine Zeile pro
   erkanntem Setup (Datum, Zeit, Muster, Richtung, Entry/Stop/Target, Ausgang) in einer
   CSV/JSON unter `algo/`. Das ist die Bruecke, ueber die "laufende Daten + Wiki verbessern
   den Algo" konkret wird — sonst bleibt der Satz eine Absicht ohne Mechanismus.
5. Detektor-Schwellen (`CFG` in `analyze_ohlc.py`: `min_age`, `min_pen`, `disp_factor`,
   `confirm`) bleiben die **eine** Quelle fuer Parameter, die Tagesreport und spaeterer
   Backtest teilen — nicht doppelt pflegen.
6. **Live-Status-Loop — umgesetzt:** `algo/live_status.py` + `.claude/commands/algo-live-status.md`
   + `/loop 10m /algo-live-status` (Design: `docs/superpowers/specs/2026-08-04-algo-live-status-loop-design.md`,
   Plan: `docs/superpowers/plans/2026-08-04-algo-live-status-loop.md`). Zieht den laufenden
   Handelstag alle 10 Minuten per yfinance nach `algo/live/<datum>/` (transient, ueberschreibend,
   `raw/marktdaten/` bleibt unangetastet), laesst dieselben Detektoren wie `backtest_ohlc.py`
   auf den 5m-Daten laufen plus `plan_trade()`, und meldet nur *neue* Ereignisse seit dem
   letzten Zyklus. Session-gebunden (`/loop`), kein Cloud-Schedule (Mindest-Takt dort 1h,
   keine lokale Dateizugriff) — Start/Stop manuell per Zuruf.

## Naechster Schritt

**Korrektur (2026-08-03):** Der urspruengliche Plan war, mit dem Backtest zu warten, bis
genug Tage vorliegen. Nutzerwunsch war ausdruecklich das Gegenteil — sofort mit den
vorhandenen Daten anfangen und bei jedem neuen Tag weiterlaufen lassen, damit sich die
Aussagekraft von selbst aufbaut, statt eine willkuerliche Wartegrenze abzuwarten. Umgesetzt:
`algo/backtest_ohlc.py` existiert und wird ab jetzt bei jedem neuen Handelstag erneut
ausgefuehrt (siehe [[../wiki/models/OHLC-Datenanalyse (Workflow)|OHLC-Datenanalyse (Workflow)]]).
Jeder neue Tag bekommt weiterhin zusaetzlich seinen eigenen
`wiki/synthesis/MNQ <Datum> — Datenbasierter Tagesrueckblick.md`; die Muster-Validierungs-Seite
aggregiert alle Tage zusammen. Naechster Ausbauschritt ist mehr Detektoren (siehe Punkt 1
oben), nicht mehr Warten.

## Log

| Datum | Ereignis |
|---|---|
| 2026-08-03 | Projekt angelegt. Datengrundlage: 31.07.2026, 03.08.2026 (03.08. Handelstag noch nicht beendet, Daten bis 16:18 NY). Bug in `tools/analyze_ohlc.py` gefixt: HTF-Kontext ("Vortag") behandelte die noch laufende Tageskerze faelschlich als Historie. |
| 2026-08-03 | Nutzer praezisiert das Ziel: **Schicht 1 = autonomer IBKR-Handelsalgorithmus**, alles andere hier ist Unterbau. `raw/marktdaten/` auf Jahr/Monat-Verschachtelung umgestellt (`tools/sort_marktdaten.py`, `tools/analyze_ohlc.py` mitgezogen); bestehende Tage nach `2026/07/31.07.2026` bzw. `2026/08/03.08.2026` migriert. Erste Code-Ideen als Backlog notiert (Backtest-Harness, Regel-Schicht, IBKR-Adapter, Backtest-Ergebnis-Artefakt). |
| 2026-08-03 | Frage beantwortet: pandas eignet sich fuer den Backtest-/Aggregations-Layer (kein eigenes Backtesting-Framework, aber die richtige Grundlage fuer Punkt 1 oben). pandas + matplotlib installiert. Beleg gebaut: `algo/viz_prototype.py` laedt den 03.08.-5m-Chart per pandas, `algo/viz_prototype.html` zeigt ihn interaktiv (Preislinie, Sweep/Displacement/Macro-Expansion annotiert, Hover-Tooltip) — Macro-Range 175,00 Pkt deckt sich exakt mit `tools/analyze_ohlc.py`. `algo/requirements.txt` neu (pandas, matplotlib; `tools/analyze_ohlc.py` bleibt Stdlib-only). |
| 2026-08-03 | Nutzerwunsch: alle Daten (CISD, ORG, "alle PD Arrays", "das gesamte Wiki") sollen jetzt schon und laufend gegen echte Daten geprueft werden, konkrete Frage: "wird das C.E eines ORG zu 70% gefuellt?". Ergebnis: dieser 70%-Wert steht in keiner ingesteten Quelle im Vault (gezielt gesucht, nur False-Positives zur "70%-Wednesday-Regel" gefunden) — vermutlich allgemeines ICT-Wissen von aussen, nicht aus dem hier vorliegenden Material. `algo/backtest_ohlc.py` gebaut: aggregiert `fvgs`/`viis`/`sweeps`/`structure_breaks`/`macro_windows` ueber alle Tagesordner, schreibt `wiki/synthesis/Muster-Validierung (laufend).md`. **Bug im ersten Entwurf gefunden und gefixt**: CFG-Skalierung (`min_age`/`confirm` je Timeframe) wird nur in `analyze_ohlc.py`s CLI (`main()`) angewendet, nicht wenn man die Detektoren direkt importiert — dadurch waren Struktur-Break-Zahlen vor dem Fix ca. 5x zu niedrig. Neuer Detektor `viis()` in `tools/analyze_ohlc.py` (Volume Imbalance, 2-Kerzen-Luecke Close→Open) ergaenzt, als erster Schritt Richtung "alle PD Arrays" — vollstaendige Liste der noch fehlenden PD Arrays (Order-Block-Varianten, IFVG, BPR, CBDR, NWOG/NDOG, OTE, Breakaway Gap, Suspension Block, Judas-Zeitfenster, SMT) in der generierten Seite und hier im Backlog festgehalten, nicht in einem Schritt geraten. Ergebnis bei n=2 Tagen (**nicht belastbar**, nur Statusbericht): C.E erreicht bei grossen FVGs 78%, komplett gefuellt 67% — in der Naehe der kursierenden 70%, aber bei 2 Tagen reiner Zufall moeglich. |
| 2026-08-04 | `yfinance` installiert (`algo/requirements.txt`), `algo/fetch_yfinance.py` gebaut: laedt MNQ=F (5m/15m/1h/1d + aus 1h resampled 4h) und legt die Daten im selben Format wie die TradingView-Exporte ab. Kompletten Juli 2026 nachgeladen (26 Handelstage, vorhandene 31.07.-Exporte nicht angetastet — Datei existiert bereits -> ueberspringen statt ueberschreiben). Nutzer betont: **Zeit hat Prioritaet vor Preis** ("Time before Price", ICT-These eines algorithmisch gesteuerten Preisverlaufs zu bestimmten Uhrzeiten) — Timestamp-Korrektheit deshalb explizit gegen die vorhandene 31.07.-TradingView-Datei gegengeprueft (identische Epochs). Dabei zwei Fehler im ersten Entwurf gefunden und gefixt, bevor Daten uebernommen wurden: (1) erster Lauf ueberschrieb die 5 bestehenden 31.07.-Dateien, aus Git wiederhergestellt und Skript geschuetzt; (2) Pandas 3.0 liefert Datetime64 nicht mehr einheitlich in Nanosekunden, dadurch stand ueberall `time=1` — Konvertierung auf `.as_unit("s")` umgestellt. Zusaetzlich RTH-Varianten (09:30-16:00 NY, Fenster aus dem bestehenden manuellen `15m RTH`-Referenzfile uebernommen) fuer 5m/15m/1h ergaenzt — yfinance hat keinen eigenen RTH-Feed, das ist derselbe Datenstrom nur gefiltert. 1m bewusst ausgelassen: yfinance liefert Minutendaten nur fuer die letzten ~7 Tage. Bekannte Luecken: 03.07. (verkuerzte Feiertagssession) ohne 1d-Kerze, die vier Sonntage im Juli nur mit einem duennen Ausreisser-Bar. |
| 2026-08-04 | Nutzerwunsch: 1m per yfinance nachladen, wo moeglich. `algo/fetch_yfinance.py`: `1m` zu `INTERVALS`/`RTH_TFS` ergaenzt, `download_interval()` fragt 1m in 7-Tage-Haeppchen an (yfinance-Limit pro Request). Backfill fuer 01.07.-04.08. gelaufen: 1m + `1m RTH` fuer 08.07.-31.07. geschrieben (30-Tage-Fenster ab heute), 01.07.-07.07. bleiben leer (Yahoo-Fehler "must be within the last 30 days", erwartet), 31.07./03.08./04.08. unangetastet (TradingView-Originale, `raw/` bleibt unveraenderlich). |
| 2026-08-04 | Nutzerwunsch: `plan_trade()` bauen, als Regel das [[Silver Bullet Model]] nutzen. `algo/rules.py` gebaut (Backlog-Punkt 2): drei Zeitfenster (London 3-4, NY AM 10-11, NY PM 14-15 Uhr NY) aus dem Wiki, erstes im Fenster bestaetigtes FVG als Trigger, Entry=C.E., Stop=Gegenkante+10%-Puffer, Ziel=naechstes `untouched_levels()`-Level in Traderichtung (kein Ziel -> kein Setup). Nutzt nur bestehende Detektoren (`fvgs`, `untouched_levels`), keine Neuimplementierung. Bewusst kein Lookahead: alle Detektoren laufen nur auf `bars[t<=when]`. Selbstcheck mit synthetischen Bars (`python algo/rules.py`) plus Smoke-Test gegen alle 26 Juli-Tage: ein Setup am 01.07., an den uebrigen Tagen korrekt `None` (meist fehlende Zielliquiditaet). Noch nicht drin: die vom Wiki geforderte Zusatz-Confluenz (NWOG/NDOG, Midnight Opening Fibs, 1. presented FVG) und der "2022 Entry" (IFVG-Variante) — bewusst als Basisversion gestartet, siehe Backlog-Punkt 2. `plan_trade()` liefert nur Setups, noch keine Trade-Simulation (P&L/Equity) — dafuer wurde die PyPI-Bibliothek `backtesting` als naechster Baustein besprochen. |
| 2026-08-04 | Live-Status-Loop gebaut: `algo/live_status.py` (Fetch heutiger Handelstag per yfinance nach `algo/live/<datum>/`, Detektoren wie `backtest_ohlc.py` auf 5m + `plan_trade()`, Diff gegen `state.json` fuer neue Ereignisse seit letztem Zyklus) + `.claude/commands/algo-live-status.md` + `/loop 10m /algo-live-status`. Session-gebunden statt Cloud-Schedule (Mindest-Takt dort 1h, kein lokaler Dateizugriff). `algo/live/*/` neu in `.gitignore` (transient, ueberschreibend); die Text-Statusberichte `algo/live/<datum>-status-log.md` bleiben versioniert. |
