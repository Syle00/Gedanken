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
   Hauptursache fuer die niedrige Win Rate, noch nicht behoben. **Stop-Puffer-Test erledigt**
   (siehe Log 2026-08-05, `algo/backtest_walkforward.py`) — Vergroessern hilft, bleibt aber in
   jeder getesteten Groesse verlustreich. Naechster Schritt vor einer echten Bewertung:
   Confluenz-Filter (NWOG/NDOG, Midnight Opening Fibs, 1. presented FVG) ergaenzen.
3. **IBKR-Anbindung als eigener, duenner Adapter** (`algo/broker_ibkr.py`, noch nicht
   angelegt): Order-Ausfuehrung ueber die Interactive-Brokers-API (TWS/IB-Gateway, z.B. per
   `ib_insync` oder offiziellem `ibapi`) hinter einer schmalen Schnittstelle
   (`place_order`, `get_position`, `cancel`), damit die Regel-Schicht broker-unabhaengig
   bleibt. Erst nach Punkt 1+2, und zuerst gegen ein Paper-Trading-Konto, nie direkt live.
4. ~~**Backtest-Ergebnisse als Datenartefakt**~~ **erledigt 2026-08-07** -- `algo/results/<name>.json`
   pro Skript (Ausnahme `backtest_seasonal.py`, siehe `algo/seasonal_tendency.json`), siehe
   Log-Eintrag unten. Urspruenglicher Text: eine Zeile pro erkanntem Setup (Datum, Zeit, Muster,
   Richtung, Entry/Stop/Target, Ausgang) in einer CSV/JSON unter `algo/`. Das ist die Bruecke,
   ueber die "laufende Daten + Wiki verbessern den Algo" konkret wird -- sonst bleibt der Satz
   eine Absicht ohne Mechanismus.
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
7. ~~**Bar-Renditen statt nur Trade-Renditen.**~~ **erledigt 2026-08-11** — `algo/confidence.py`
   (`bar_metrics`/`print_bar_metrics`) in `backtest_bt.py` verdrahtet, siehe Log unten. *(Werkzeug
   stand: `algo/masters.py::bar_returns_from_trades()`; offen war nur noch das Verdrahten.)* Aus dem
   Masters-Ingest 2026-08-08
   ([[../wiki/concepts/Profit pro Bar vs. pro Trade|Profit pro Bar vs. pro Trade]]): alle
   `algo/`-Reports rechnen ueber die `backtesting`-Lib auf Trade-Basis. Profit Factor und
   Sharpe sind dort systematisch extremer als auf Bar-Basis — Masters' Beispiel: derselbe
   Sachverhalt ergibt Trade-basiert einen Profit Factor von unendlich und Bar-basiert 1,01.
   Konkret: `stats._trades` um eine Bar-fuer-Bar-Mark-to-Market-Serie ergaenzen (fuer Bars mit
   offener Position) und Kennzahlen zusaetzlich darauf rechnen. **Voraussetzung fuer die
   Punkte 8-10.**
8. ~~**Guard Buffer im Walk-Forward.**~~ **geprueft + gehaertet 2026-08-11.** Befund: kein Leck.
   `signals.py` ist zustandslos (reine Funktionen, `history = mnq_rows[:i+1]`, kalenderbasierte
   Signale strikt `< target_day`), und die Ensemble-Zielgroesse ist die Richtung des Folgetags
   (`build_features`: `y[i]` = Tag i+1), also Lookahead genau 1 -> `guard_buffer(L,1)=0`.
   SilverBulletStrategy entscheidet pro Kerze nur aus `bars[t<=when]` in einem harten 1h-Fenster,
   kein tagesuebergreifender Zustand. Die adjazenten Folds in `validate.py` lecken damit nicht.
   Trotzdem gehaertet: `walk_forward(..., omit=0)` streicht bei omit>0 die juengsten
   Trainingstage je Fold — Default 0 (byte-identisch), aber ein spaeter verlaengerter Zielhorizont
   H muss nur noch `omit=H-1` setzen, statt still anti-konservativ zu werden. Aus
   [[../wiki/concepts/Walk-Forward Guard Buffer & Varianz-Inflation|Walk-Forward Guard Buffer & Varianz-Inflation]].
   Masters' Zahl zur Groessenordnung: ohne Puffer erreicht ein wertloses System auf
   Random-Walk-Daten t = 74,64 statt 0.
9. ~~**Konfidenz-Untergrenze und ehrliche Drawdown-Grenze.**~~ **erledigt 2026-08-11.** (a) BCa-
   Untergrenze fuer mittlere Bar-Rendite und Profit Factor jetzt im `backtest_bt.py`-Report
   (`confidence.py`, PF ueber `exp(BCa auf log PF)`). (b) `validate.py::monte_carlo` weist die
   Drawdown-Zeile jetzt doppelt aus: die alte Perzentil-Zeile als "naiv" markiert, darunter die
   korrekte `double_bootstrap_drawdown()` (dd_conf 0,95/0,99) ueber `masters.drawdown_bound`.
   Siehe Log unten.
   [[../wiki/concepts/Konfidenzgrenzen für Renditen (t-Test, Bootstrap, BCa)|Konfidenzgrenzen für Renditen]]
   und [[../wiki/concepts/Grenzen für Einzelrenditen & Drawdown|Grenzen für Einzelrenditen & Drawdown]].
   Zwei getrennte Luecken: (a) Reports weisen nur Punktschaetzer aus — eine BCa-Untergrenze
   (`scipy.stats.bootstrap(method="BCa")`) zeigt, ob die Zahl ueberhaupt von null
   unterscheidbar ist; beim Profit Factor den **Logarithmus** bootstrappen, sonst versagt es.
   (b) Das Monte-Carlo-Trade-Resampling in `validate.py` ist exakt der von Masters als
   "incorrect" bezeichnete naive Drawdown-Bootstrap — er unterschaetzt bei kleiner Stichprobe
   Katastrophen-Drawdowns um bis zu Faktor 13,65. Vor jeder Kapitalentscheidung auf den
   Doppel-Bootstrap umstellen.
10. **Return-Partitionierung + Selection-Bias-P-Wert im geplanten `permutation_test.py`.**
    [[../wiki/concepts/Return-Partitionierung (Skill, Trend, Training Bias)|Return-Partitionierung]]:
    `TotalReturn = Skill + Trend + TrainingBias`, wobei `Trend = (NumLong − NumShort) ×
    TrendPerReturn` direkt berechenbar ist und `TrainingBias` als Mittelwert ueber die ohnehin
    laufenden Permutationen abfaellt. Beantwortet die bisher offene Frage, wie viel eines
    `algo/`-Backtestergebnisses schlicht daran liegt, dass MNQ im Datenzeitraum gestiegen ist.
    Dazu der `unbiased_pval` (Solo- vs. Bestenvergleich), weil im Vault laufend viele Thesen
    gegen dieselben Daten geprueft werden — siehe
    [[../wiki/concepts/Training Bias & Selection Bias|Training Bias & Selection Bias]].
    **Offen, aber jetzt entblockt (2026-08-11): bewusst NICHT mit 7-9 mitgeliefert.** Die
    Werkzeuge stehen (`masters.partition_return`, `permute_bars`, `stoc_bias`), aber
    `permutation_test.py` braucht je Permutation eine **volle Reoptimierung** der Strategie. Die
    dafuer noetige Performance-Voraussetzung ist **erledigt** (siehe Log 2026-08-11): `next()`
    baut die Historie jetzt inkrementell auf (`backtest_bt.extend_hist`, O(n²)->O(n)), ein voller
    50-Tage-Lauf faellt von ~270 s auf ~40 s. Damit sind hunderte Permutationslaeufe praktikabel.
    Naechster Schritt ist also der Bau von `permutation_test.py` selbst.

### Backlog: drei quantifizierte Regeln aus Core Content Month 09 (2026-08-10)

Aus dem Ingest der Month-09-Videoreihe stammen drei Thesen, die konkret genug fuer einen eigenen
Backtest gegen `raw/marktdaten/` sind. Noch nicht umgesetzt — hier als Auftrag notiert.

1. **London-Close-Retracement (`algo/backtest_london_close.py`)** — Bedingung: NY und London
   liefen in dieselbe Richtung **und** die 5-Tage-ADR wurde erreicht/ueberschritten. Erwartung:
   Retracement von 20–30 % der Tagesrange. ⚠️ ICT nennt in Month 09 **zwei abweichende
   Parametersaetze** — Reversal-Lektion: Fenster 10:00–12:00 NY, ~20 %, ADR-Ueberschuss
   1,25–1,33×; Bread-&-Butter-Lektionen: Fenster 10:30–13:00 NY, 20–30 %, kein fester Faktor.
   **Beide Varianten getrennt testen**, nicht eine willkuerlich waehlen. Siehe
   [[../wiki/concepts/Average Daily Range (5-Tage-ADR)|Average Daily Range (5-Tage-ADR)]].
2. **33-Pip-Protraction** — auf einem "klassischen 100-Pip-Tag" laeuft die Protraction unter den
   Midnight-NY-Opening-Price bis zu ~33 Pips, also rund **ein Drittel der erwarteten Tagesrange**.
   Auf MNQ als Verhaeltnis (nicht als Pip-Wert) zu pruefen: Wie tief unter dem Midnight-Open liegt
   das Tagestief an Up-Close-Tagen, relativ zur ADR? Siehe
   [[../wiki/models/ICT Day Trade Routine|ICT Day Trade Routine]].
3. **Filling The Numbers (vier Level)** — IPDA handelt pro Tag zu vier Leveln, gemessen ueber
   CBDR-STDs, Asia-Range-STDs, Pivots **oder** den Flout (Range 15:00–00:00 NY, halbiert). Gut
   testbar, weil CBDR- und Asia-Range-Detektoren bereits existieren; der Flout waere neu. Frage an
   die Daten: Wird die Vier-Level-Faustregel getroffen, und **welche** Messlatte trifft auf MNQ am
   haeufigsten? Siehe
   [[../wiki/concepts/Filling The Numbers (4 Level pro Tag)|Filling The Numbers (4 Level pro Tag)]].

### Backlog: Macro-Messmethodik korrigieren (2026-08-10, aus ICT-Gems-Ingest)

**Hoch priorisiert, weil es eine bereits publizierte Zahl betrifft.** ICT sagt woertlich, das
Macro-Fenster sei ein **Startfenster**, kein Container: *"the move **begins** in those 20 minutes,
it's not the entirety of the move"* (siehe
[[../wiki/sources/youtube/ICT Gems - Blending Silver Bullets and Macros (Source)|Blending Silver Bullets and Macros (Source)]]).

`algo/backtest_macro.py` misst aber Range, Netto und `dir` **innerhalb** des 20-Minuten-Blocks.
Ein Macro, das um 10:05 einen Lauf startet, der bis 10:40 traegt, wird dadurch als schwacher Block
gewertet — die Methode unterschaetzt den Effekt systematisch.

1. **Neue Kennzahl**: Exkursion **ab Macro-Start ueber die folgenden N Minuten** (MFE/MAE-artig,
   N z.B. 20/40/60) statt Blockinhalt. Kontrollbloecke identisch behandeln, sonst entsteht ein
   neuer Confounder.
2. **Letzte Handelsstunde ausnehmen**: Dort gilt das `:50-:10`-Raster laut zwei Quellen **nicht**
   (15:15-15:45 Final Hour Macro, 15:45-16:00 MOC, in der Earnings-Saison zusaetzlich 16:01 und
   16:15). Das Skript rastert aktuell durchgehend gleichmaessig und misst diese Stunde damit falsch.
3. **Spooling-Suche einstellen wie bisher geplant**: Die Suche nach einer volumenbasierten
   Spooling-Definition ("enge Kerzen bei steigendem Volumen") zielte am Begriff vorbei — ICT
   bezeichnet mit Spooling den **gerichteten Lauf zur Liquiditaet**, nicht die Kompression davor.
   Die passende Messgroesse ist der bereits erhobene Nettoweg/`dir`, nicht Volumen (das im Bestand
   ohnehin fehlt).
4. **Mindestziel als Filter pruefen**: ICT nennt **10 Handles** als Untergrenze fuer NASDAQ-Scalps
   und **5 Handles** speziell fuer den Silver Bullet. Auf MNQ direkt als Punktschwelle testbar.

### Backlog: Vier-FVG-pro-Stunde-These (2026-08-10, aus ICT-Gems-Ingest)

ICT behauptet, in **jedem** Viertelstunden-Fenster bilde sich ein FVG auf 15M oder 5M — also
**vier pro Stunde** ("high frequency trading algorithmically"). Wichtig: Das FVG muss sich nur
**bilden**, es muss nicht angehandelt werden. Bleiben sie aus, ist das laut ICT die Definition von
**High Resistance Liquidity Run** und damit sein "number one premise" fuer Nicht-Handeln.

Direkt gegen `raw/marktdaten/` pruefbar und auf `algo/backtest_macro.py`s FVG-Zaehlung aufsetzbar
(die zaehlt bereits FVGs je 20-Minuten-Block mit `--min-fvg`):

1. **Grundfrage**: Wie oft enthaelt ein Viertelstunden-Fenster (:00-:15, :15-:30, :30-:45, :45-:00)
   mindestens ein 1m-FVG? Getrennt nach Mindestgroesse, analog zur bestehenden Tabelle.
2. **Verknuepfung mit dem HRLR-Kriterium**: Sind Stunden **ohne** FVG in mehreren aufeinander-
   folgenden Vierteln messbar anders (kleinere Range, niedrigeres `dir`) als Stunden mit? Das waere
   ein datenseitiger Test des "sit still"-Kriteriums.
3. Vorsicht bei der Interpretation: Die bestehende Messung zeigt bereits, dass **95 % aller
   Macro-Fenster mindestens ein FVG >= 2 Punkte** enthalten — die These koennte also trivial wahr
   und als Filter wertlos sein. Genau das ist zu quantifizieren, statt sie zu bestaetigen.
   Siehe [[../wiki/concepts/Algorithmic Price Delivery Continuum|Algorithmic Price Delivery Continuum]].

### Backlog: zwei Fenster-Widersprueche aus ICT-Quellen (2026-08-10)

Beide Male widerspricht ICT sich selbst zwischen zwei Quellen; **beide Varianten testen**, keine
willkuerlich waehlen:

- **MOC-Fensterlaenge**: 15:50-16:00 (2026er Chronicles) vs. **15:45-16:00** (2024er Gems,
  ausdruecklich *"it's not 10 minutes, it's 15 minutes"*). Siehe
  [[../wiki/models/Market on Close (MOC) Macro Model|Market on Close (MOC) Macro Model]].
- **Lunch-Macro-Start**: Execution im Macro 10:50-11:10 (Lecture 2025) vs. **11:30** als Beginn mit
  Fenster bis 13:30 (Gems 2024). Die 11:30-Fassung ist mechanisch formuliert und damit direkt
  codierbar: erstes Low rueckwaerts von 11:30, das nach 10:00 entstanden ist. Siehe
  [[../wiki/models/NY Lunch Macro Model|NY Lunch Macro Model]].

### Backlog: ORG-Gap nach Groesse segmentieren (2026-08-12, aus Daily-Bias-Notiz)

Jannes' These (aus `raw/daily bias 12.08.md`): bei einem **sehr grossen** ORG-Gap greift die
70%-C.E.-Regel nicht (kein Fill innerhalb 30 Min). `algo/backtest_org_ce.py` erweitern, um die
Fuellrate nach Gap-Groesse (Quartile) statt nur aggregiert auszuweisen — prueft, ob grosse Gaps
die 35–43%-Gesamtquote nach unten ziehen. Siehe [[../wiki/synthesis/Muster-Validierung (laufend)|Muster-Validierung (laufend)]], Nachtrag 2026-08-12.

### Backlog: zwei quant-finance-Thesen aus MIT-15.S08-Batch-2-Ingest (2026-08-12)

Aus dem Ingest der 9 restlichen MIT-15.S08-Transkripte (Lectures 12/14/18-21/23-25, siehe
`wiki/log.md`) stammen zwei konkret codierbare, noch nicht implementierte Thesen:

- **Autokorrelations-These (Box-Pierce)**: prueft, ob MNQ-Returns auf einem oder mehreren
  Timeframes (1m/5m/15m/1h/1d) signifikante Autokorrelation zeigen (`BP = T·Σ R̂_j²`,
  χ²-verteilt). Siehe [[../wiki/concepts/Zeitreihenanalyse für Finance|Zeitreihenanalyse für
  Finance]]. Noch kein Code — Kandidat `algo/backtest_autocorrelation.py`.
- **GARCH(1,1)-Sizing-These**: dynamische Stop-Distance/Positionsgroesse ueber eine laufend
  aktualisierte GARCH-Volatilitaetsschaetzung statt festem ATR-Multiplikator; Datenbedarf
  (OHLC) ist mit `raw/marktdaten/` bereits gedeckt. Siehe
  [[../wiki/concepts/Volatilitätsmodelle (GARCH & Co)|Volatilitätsmodelle (GARCH & Co)]]. Noch
  kein Code — Kandidat `algo/backtest_garch_sizing.py`.

Beide sind reine Backlog-Eintraege gemaess [[Algo-Trading: Arbeitsstandards]] ("jede neue These
wird automatisch geloggt") — Backtest folgt in einer kuenftigen Session, nicht Teil dieses
Ingest-Auftrags.

### Backlog: Risikomanagement-Prinzipien aus Yale-Econ-252-Ingest (2026-08-12)

Aus dem Ingest der 23-teiligen Yale-"Financial Markets"-Playlist (Robert Shiller, siehe
`wiki/log.md` und die neuen `wiki/concepts/*Yale Econ 252*`-Seiten) stammen sechs Punkte mit
direktem Bezug zu Korrektheit/Risiko im eigenen Stack — priorisiert nach Aufwand/Nutzen:

1. **Korrelationsbruch in Stressphasen (hoechste Prioritaet, geringer Aufwand).** These: Setups,
   die im Normalbetrieb unkorreliert wirken, laufen in volatilen Phasen synchron (AIG-Fallstudie,
   siehe [[../wiki/concepts/Versicherung als Risikomanagement-Institution (Yale Econ 252)|Versicherung
   als Risikomanagement-Institution]]). Betrifft direkt `algo/backtest_ensemble.py`, das mehrere
   Regeln kombiniert, ohne die Korrelation ihrer Trade-Returns bedingt auf Vola-Regime zu pruefen.
   Kandidat: `algo/backtest_ensemble.py` um eine Kennzahl "Korrelation der Strategie-Returns,
   getrennt nach oberem/unterem ATR-Quartil" erweitern — warnt, falls die Diversifikations-Annahme
   des Ensembles nur im ruhigen Regime gilt.
2. **Fat-Tail-Realitaetscheck (hohe Prioritaet, geringer Aufwand).** 1987 (-20,47 % an einem Tag)
   und der Doppelcrash 1929 als historische Belege gegen Normalverteilungs-Annahmen (siehe
   [[../wiki/concepts/Value at Risk, CoVaR & Unabhängigkeitsannahme (Yale Econ 252)|Value at Risk,
   CoVaR & Unabhängigkeitsannahme]]). Ergaenzt die bestehende Doppel-Bootstrap-Drawdown-Schaetzung
   in `validate.py`/`stress_test.py` um einen expliziten Hinweis, dass Bootstrap aus der eigenen
   Historie Tail-Ereignisse jenseits des beobachteten Fensters strukturell unterschaetzt — kein
   Code-Fix, sondern eine Reporting-Ergaenzung ("worst observed" vs. "plausibles Tail-Risiko").
3. **Sharpe-Ratio-Manipulierbarkeit durch Tail-Verkauf (mittlere Prioritaet).** Formal belegt
   (Fallbeispiel Integral Investment Management): eine unauffaellig glatte Equity-Kurve mit hoher
   Sharpe-Ratio kann aus verkauften Tail-Optionen/kurz gehaltenen Crash-Risiken stammen, nicht aus
   echtem Edge. Bezug zur bestehenden `dubious_pct`-Pflichtkennzahl (siehe
   [[Algo-Trading: Arbeitsstandards]]) — ergaenzt sie um eine Warnung, wenn Sharpe hoch UND
   Drawdown-Verteilung stark linksschief ist (Skewness-Check in `selfcheck.py`).
4. **Gambler's-Ruin-Bestaetigung (kein neuer Code).** Yale-Formel `[(1−p)/p]^S` fuer
   Market-Maker-Ruin ist mathematisch identisch zur bereits im Vault genutzten Kelly-Ruin-Grenze —
   reine Bestaetigung, kein Handlungsbedarf.
5. **Random-Walk-vs.-AR(1) (kein neuer Code).** Liefert die oekonomische Begruendung fuer den
   bereits eingesetzten Monte-Carlo-Permutationstest — reine Bestaetigung.
6. **Futures-Fair-Value-Formel fuer Rollover (niedrige Prioritaet).** Contango/Backwardation-Logik
   (siehe [[../wiki/concepts/Forward- & Futures-Märkte (Contango, Backwardation, Yale Econ 252)|Forward-
   & Futures-Märkte]]) erklaert strukturell den MNQ/NQ-Rollover-Sprung in den Rohdaten — relevant,
   sobald Kontraktwechsel in `raw/marktdaten/` explizit behandelt werden (aktuell kein bekanntes
   Problem, daher niedrige Prioritaet).

Alle sechs sind Backlog-Eintraege gemaess [[Algo-Trading: Arbeitsstandards]] — Umsetzung folgt in
einer kuenftigen Session, nicht Teil dieses Ingest-Auftrags. Punkt 1 und 2 zuerst, da sie
bestehende Validierungsluecken direkt schliessen (Korrektheit vor Features).

### Backlog: IFVG + Reclaimed FVG in rules.py (2026-08-14, Nutzeranstoss)

`plan_trade_hp_fvg()` deckt bislang nur das klassische FVG ab. Zwei Varianten fehlen noch,
weil sie nicht als klassisches FVG gehandelt werden, sondern erst nach einem Durchbruch
erneut genutzt werden:

- **IFVG (Inverse FVG)**: hat bereits eine klar spezifizierte Regel im Wiki
  ([[../wiki/concepts/IFVG (Inverse Fair Value Gap)|IFVG (Inverse Fair Value Gap)]]) — Validierung
  (High/Low ODER C.E. vorher respektiert), Polaritaetswechsel nach vollem Durchhandeln,
  doppelte Qualifizierung vorm Entry (1. Close durchs Gap, 2. erneuter Close nach Ruecklauf).
- **Reclaimed FVG**: hat **keine** eigene Wiki-Konzeptseite, nur verstreute Rohnotizen
  (`Kurz Notizen`, `03 Trading Premarket and Regular Session Liquidity`, `04 Alltime Highs und
  TGIF`, `From Vision To Execution`), die den Begriff faktisch mit IFVG verzahnen ("reclaimed
  SIBI... gefolgt von Break nach unten + IFVG") statt ihn als eigenstaendigen Mechanismus zu
  spezifizieren.

Nutzerentscheidung 2026-08-14: **beide vorerst zurueckgestellt** ("machen wir wann später").
Naechster Schritt bei Wiedervorlage: zuerst `wiki/concepts/Reclaimed FVG.md` anlegen (oder
Reclaimed FVG explizit als Sweep-Narrativ um ein IFVG dokumentieren, keine zweite Detektor-Logik),
dann `ifvgs()`-Detektor in `tools/analyze_ohlc.py` (stateful: FVG -> voller Durchhandel mit
Vorbedingung -> 2. Qualifizierung) und darauf aufbauend eine dritte `rules.py`-Regel.

### Backlog: Regeln fraktal ueber Timeframe und Markt generalisieren (2026-08-14, Nutzerprinzip)

Nutzerprinzip: alle gehandelten Regeln sollen fraktal auf jeder Timeframe (1 Monat bis 1 Sekunde)
und in jedem Markt (Futures, FX, Aktien, Crypto) gelten. Status quo bereits gut: `fvgs()`,
`hp_context()` etc. arbeiten nur mit `Bar`-Listen ohne TF-Annahme, Groessenschwellen sind relativ
zur lokalen Kerzenrange (nicht absolut), `symbol` ist durchgaengig Parameter (`pnl.POINT_VALUE`,
`round_to_tick`) — neue Symbole sind Zusatzeintraege, keine Strukturaenderung. **Eine bewusste
Ausnahme**: `plan_trade_hp_fvg()`s `prev_day_hi`/`prev_day_lo` ist tagesskaliert, weil die
Masterclass-Quelle woertlich den vorherigen **Handelstag** meint — eine Verallgemeinerung auf
"vorherige Periode auf beliebiger Timeframe" waere eine neue, ungetestete These und keine
Umsetzung der bestehenden Messung. Falls das Prinzip spaeter zur Pflicht wird: als eigene These
loggen und gegen mehrere Timeframes/Symbole backtesten, statt es stillschweigend in bestehende
Regeln einzubauen.

### Backlog: Haltedauer-Cap fuer SB-Backtests (2026-08-14, aus PWH/PWL-Artefakt)

Kein bisheriger Silver-Bullet-Backtest (`backtest_bt.py`, `backtest_sb_bellwether.py`,
`backtest_sb_session_liq.py`) deckelt, wie lange eine simulierte Position offen bleiben darf --
`simulate()` laeuft bis Stop/Ziel, und sei es Wochen spaeter. Fuer Swing-Level (meist nah) faellt
das kaum auf, bei weit entfernten Zielen (PWH/PWL) verzerrt es das Ergebnis massiv: ein Trade vom
11.06. "gewann" erst am 15.06. (439 5m-Kerzen / ~4 Handelstage spaeter) und macht einen Grossteil
des gemessenen PWH/PWL-Gewinns aus, obwohl das Silver-Bullet-Modell laut Wiki maximal "die volle
folgende Stunde" erwartet. Fix: `simulate()` um ein Zeit-Limit ergaenzen (z.B. Sessionende
17:00 NY desselben Tages, oder N Stunden nach Entry) und die betroffenen Backtests damit erneut
laufen lassen, bevor eine der beiden Thesen (Bellwether-Timeframe, Session-Liquiditaet) als
entschieden gilt.

### Backlog: 1d-Dateien gegen Intraday-Aggregat gegenpruefen (2026-08-14, aus Liquiditaets-Check gefunden)

**Aktiver Datenbefund, Nulltoleranz-Regel greift.** Beim manuellen Liquiditaets-Check (15m-Chart)
korrigierte Jannes das gemeldete PDH (13.08.) von 30267,0 auf 30273,25 -- Gegenprobe bestaetigt
seine Zahl: die 5m/15m-Intraday-Datei fuer 13.08. hat tatsaechlich H 30273,25, waehrend die
`MNQ 2026-08-13 1d.csv`-Datei noch H 30267,0 / C 30223,5 fuehrte (O/L stimmten). Root Cause:
die TradingView-Korrektur vom 14.08. ("16 Kerzen revidiert", siehe Log-Eintrag oben) hat die
5m/15m/1m-Dateien aktualisiert, aber **die 1d-Datei nicht neu aus den korrigierten Intraday-Bars
aggregiert** -- sie blieb auf dem Stand des vorherigen (fehlerhaften) yfinance-Nachzugs stehen.
**13.08. direkt repariert** (H 30267,0→30273,25, C 30223,5→30216,25, gegen die 275 5m-Kerzen der
korrekten Session 12.08. 18:00–13.08. 16:55 verifiziert). ⚠️ **Systemcheck ueber den gesamten
Bestand (1883 1d-Dateien) findet 6 weitere Tage mit derselben Art Abweichung** (>0,3 Pkt gegen
das 5m-Aggregat derselben Session): 08.06., 15.06., 16.06., 17.06., 18.06., 01.07., 03.08. --
teils uber 300 Punkte Differenz. **Nicht blind automatisch ueberschrieben** (anders als beim
13.08.-Fix, wo eine externe Bestaetigung vorlag) -- diese sechs brauchen erst denselben
Gegencheck (5m-Aggregat plausibel? gegen TradingView/Chart verifizieren, nicht nur gegen sich
selbst), bevor sie geschrieben werden. **Impact:** `backtest_sb_session_liq.py` (PDH/PDL/PWH/PWL-
These, 2026-08-14 gemessen) liest PDH/PDL aus genau diesen 1d-Dateien -- die 03.08.-Abweichung
liegt in der 47-Tage-Stichprobe dieses Backtests, das Ergebnis (2,7% Win/-14,57 USD PDH/PDL) ist
davon mitbetroffen, wenn auch nur an einem von 47 Tagen. **Naechster Schritt:** die sechs Tage
einzeln gegenpruefen und reparieren, danach `backtest_sb_session_liq.py` erneut laufen lassen.

⚠️ **Nachtrag, Daily-IPDA-Check (2026-08-14):** weiterer betroffener Tag gefunden, der beim
ersten Scan durch den `len(bars5) < 200`-Filter rutschte (unvollstaendiger Handelstag): die
1d-Datei fuer **19.06.2026** (Freitag) enthaelt H 30967,75 / L 30336,75 -- exakt die Werte von
**22.06.2026** (Montag danach), nicht die eigenen (5m-Aggregat 19.06.: H 30771,0 / L 30505,5).
Sieht nach einer Duplizierung beim Wochenend-Rollover aus (Freitag-Datei blieb auf dem naechsten
Handelstag stehen). Fuer den Daily-IPDA-Report umgangen, indem 20/40-Tage-High/Low direkt aus
den 5m-Tagesdateien aggregiert wurden statt aus den 1d-Dateien -- robuster, aber nur 49
Handelstage 5m-Abdeckung (ab 08.06.), das volle 60-Tage-IPDA-Fenster bleibt damit unvollstaendig
belegt. Zaehlt als achter Fund fuer die anstehende 1d-Bereinigung.

### Erledigt: Liquiditaets-Wissen in rules.py + neues liquidity_report.py (2026-08-14)

Brainstorming-Session (bounded) umgesetzt: `rules.py` bekam vier neue reine Funktionen
(`session_extrema`, `ipda_windows`, `rel_pair`, `daily_hilo_from_bars`/`prev_day_level`/
`prev_week_level`, `level_untouched`) mit `demo()`-Asserts, siehe `algo/README.md` fuer die
Doku. Dabei `backtest_sb_session_liq.py::daily_hilo()` von den 1d-Dateien auf 5m-Aggregation
umgestellt (importiert jetzt aus `rules.py`) -- behebt strukturell den am selben Tag gefundenen
1d-Datenfehler fuer diesen Backtest. Neu erlaufen: PWH/PWL-Ergebnis kippte von +34,35 $/Trade
(Artefakt) auf -1,27 $/Trade, PDH/PDL bleibt klar negativ (-14,23 $/Trade). Neue Datei
`algo/liquidity_report.py` (CLI wie `live_status.py`) erkennt und rankt aktuelle Liquiditaet
ueber 1m/5m/15m/Daily qualitativ (Hoch/Mittel/Niedrig) -- Details, Limits (Cross-TF-Dedup fehlt
noch) und Konstanten (`NEAR_PCT`, `MAX_DISTANCE_PCT`) in `algo/README.md`. `selfcheck.py`
weiterhin 20/20 (Erweiterung ist additiv, kein bestehender Test veraendert).

### Erledigt: Forex-Backtesting-Infrastruktur (2026-08-15)

Spec `docs/superpowers/specs/2026-08-14-forex-backtesting-design.md` umgesetzt: Parquet-Cache
(`build_parquet.py`, ~894 MB, 10 Paare), dreistufige Verifikation (`verify_forex_data.py`:
Zeit-Kreuzprobe OK, Vollstaendigkeits-Check-Bug gefixt, Attrappen-Quote als bekannte Grenze statt
Filterung dokumentiert), `SESSION_TYP`/`PIP_SIZE`-Guard in `tools/analyze_ohlc.py`, neuer
`marktdaten.bars()`-Loader (inkl. Performance-Fix iterrows->numpy), Attrappen-Loeschvorschlag
fuer `raw/marktdaten/` (72/340 Dateien, nicht umgesetzt), zwei Module (`backtest_seasonal.py`,
`backtest_midnight_range_std.py`) auf allen 10 Paaren als Beweis fuers `symbol`-Parameter +
`marktdaten.bars()`-Muster. Volle Zahlen: siehe Log-Eintraege 2026-08-15 oben, Modul-Doku in
`algo/README.md`.

### Backlog: uebrige Gruppe-A/B-Module fuer Forex parametrisieren (2026-08-15, Folge-Task)

Die restlichen acht exploratorischen Module folgen demselben in den zwei Nachweis-Modulen oben
bewiesenen Muster (`symbol`-Parameter ergaenzen, `backtest_common.load_rows()`/
`marktdaten.bars()` statt direktem CSV-Zugriff nutzen), sind aber bewusst nicht Teil des
Forex-Backtesting-Plans, um ihn reviewbar zu halten -- je ein eigener, kleiner Folge-Umbau:

- Gruppe A: `backtest_daily_patterns.py`, `backtest_tgif.py`, `backtest_fred_events.py`
  (NFP-Week-These), `backtest_ohlc.py`.
- Gruppe B: `backtest_hp_fvg.py`, `backtest_midnight_range_judas.py`,
  `backtest_fvg_strength.py` (braucht dafuer `PIP_SIZE` aus Task 3, bisher von keinem der beiden
  Nachweis-Module konsumiert), `backtest_nwog.py`.

Gruppe C (`backtest_org_ce.py`, `backtest_1p_...`, `backtest_ndog.py`, ...) bleibt MNQ-only, der
Guard aus Task 3 sorgt dafuer, falls sie versehentlich mit einem Forex-Symbol aufgerufen wuerden.

### Erledigt: IBKR 1s-Datenanbindung fuer NQ/ES implementiert (2026-08-15)

Design `docs/superpowers/specs/2026-08-15-ibkr-1s-datenanbindung-design.md` umgesetzt:
`algo/fetch_ibkr.py` (Front-Monat-Aufloesung, Pacing-Limiter, Fenster-Zerlegung,
Abdeckungs-Register, Parquet-Schreiben), Nulltoleranz-Gate ueberspringt den
Degeneriert-Check bei <=5s Median-Abstand (`tools/analyze_ohlc.py`), 1s-Parquet-Zweig in
`algo/marktdaten.py::_futures_bars()`, Slash-Command `/daten-1s`, alle Selbstchecks in
`algo/selfcheck.py` eingebunden.

**Update 2026-08-15, abends -- Inbetriebnahme + Verifikation (Nutzer-Rechner):**
IB Gateway + IBC eingerichtet (Stolpersteine: `StartGateway.bat`-Pfade zeigten auf
Default-Installationsorte statt der echten `%USERPROFILE%\IBC`-Struktur; `JAVA_PATH` musste
explizit auf die versionsgebundene JRE unter `C:\Jts\ibgateway\1050\jre\bin` zeigen, sonst
"Can't find suitable Java installation"; `TWS_SETTINGS_PATH` musste auf einen existierenden,
festen Ordner zeigen, sonst kam bei jedem Neustart ein "Settings corrupted"-Dialog).
Ausserdem ein echter Code-Bug gefunden und gefixt: der `if __name__ == "__main__":`-Block in
`algo/fetch_ibkr.py` rief bei vorhandenen CLI-Argumenten nur `print(__doc__)` auf, nie
`main()` -- aus Task 1 uebrig geblieben, bei der `main()`-Erweiterung in Task 3 nicht
nachgezogen, durch keinen Selbstcheck abgedeckt (kein Test ruft das Skript mit `sys.argv`
auf). Fix: `sys.exit(main())` statt `print(__doc__)`.

**`--verify` erfolgreich:** NQ und ES liefern je 1800 Kerzen (volle 30 Min, 1s-Aufloesung,
keine Luecke) fuer den aktuellen Front-Monat-Kontrakt (NQU2026/ESU2026). Grundvoraussetzung
war ein fehlendes IBKR-Marktdaten-Abo (`CME Real-Time (NP,L1)`, 1,55 USD/Monat, im Client
Portal unter Market Data Subscriptions nachtraeglich aktiviert) -- ohne das kamen selbst
AAPL-Testabrufe (Aktie, komplett losgeloest von CME-Futures) mit Timeout und 0 Kerzen zurueck,
was den Fehler eindeutig als Abo-Luecke statt Verbindungs-/Zeitzonen-/1s-spezifisches Problem
identifizierte.

**R1 (verfallene Kontrakte) geklaert -- positiv:** `includeExpired=True` liefert 1s-Bars auch
fuer einen laengst verfallenen Kontrakt (NQU2025, Verfall September 2025): 1800/1800 Kerzen
fuer ein Testfenster aus Juli 2025, keine Luecke. Der 6-Monats-Backfill ueber mehrere
Kontrakt-Rolls hinweg (NQU2025->NQZ2025->NQH2026->NQM2026->NQU2026 fuer den geplanten
Zeitraum) ist damit nicht durch R1 blockiert.

**Prüfpunkte 3/4 durchgeführt (14.08.2026 als Testtag, gegen eingespielte TradingView-
1m-Referenz):** Zeitstempel stimmen **zu 100 %** überein (1380/1380 NQ-, 1320/1320
ES-Minuten deckungsgleich mit der Referenz) -- kein Zeitzonen-/Offset-Fehler. Preise
weichen in ~19-30 % der Minuten leicht ab (meist 1 Tick bei Open, High/Low fast immer
exakt gleich).

**Ursache gefunden, kein Bug in `fetch_ibkr.py` -- widerspricht aber Design-Annahme E4:**
IBKR liefert fuer 1s-TRADES-Bars tatsaechlich fuer *jede* Sekunde des Fensters eine Kerze,
nicht nur fuer Sekunden mit echtem Trade. Handelslose Sekunden kommen als `volume=0`-Kerze
mit fortgeschriebenem letzten Preis (`open==high==low==close`), nicht als Luecke -- E4 nahm
das Gegenteil an ("bleiben schlicht leer"). Gemessen: 45,8 % aller NQ- und 58,6 % aller
ES-1s-Kerzen am 14.08.2026 sind solche Phantomkerzen. Ein `open="first"`-Aggregat (z.B.
Resampling 1s->1m) kann dadurch eine Phantomkerze statt des ersten echten Trades als Open
erwischen -- erklaert praktisch alle beobachteten Open-Abweichungen zur TradingView-Referenz;
High/Low bleiben unberuehrt, weil `max`/`min` von Phantomkerzen nicht verfaelscht werden.
**Nutzerentscheidung:** `raw/marktdaten/` wird NICHT bereinigt, Rohdaten bleiben 1:1 wie
geliefert (Nulltoleranz). Dokumentiert in `algo/README.md` (`fetch_ibkr.py`-Abschnitt) --
jeder kuenftige 1s-Verbraucher muss selbst nach `volume > 0` filtern, wenn er echte Trades
statt Preisfortschreibung braucht.

**Zusaetzlicher Bugfix waehrend der Verifikation:** `fetch_window()` erkannte eine echte
IBKR-Pacing-Violation (Error 162) nicht -- `reqHistoricalData` liefert dabei ganz normal eine
leere Liste zurueck statt einer Exception, ununterscheidbar von einem Fenster ohne Trades.
3 ES-Fenster wurden dadurch beim ersten Testlauf faelschlich als "0 Kerzen, geprueft" ins
Register geschrieben (90-Minuten-Luecke, waere nie automatisch nachgeholt worden). Fix:
`fetch_window()` haengt sich waehrend des Requests an `ib.errorEvent`, behandelt eine leere
Antwort MIT Fehlermeldung als gescheiterten Versuch, gibt nach 3 Versuchen `None` (nicht
einen leeren DataFrame) zurueck -- `fetch_symbol_day()` schreibt fuer `None` keine
Registerzeile, das Fenster bleibt offen fuer den naechsten Lauf. Commit `1344954a9`.
Ausserdem ein zweiter, unabhaengiger Bug gefunden und gefixt: der `if __name__ ==
"__main__":`-Block rief bei CLI-Argumenten nur `print(__doc__)` auf, nie `main()` -- aus
Task 1 uebrig, bei der `main()`-Erweiterung in Task 3 nicht nachgezogen, durch keinen
Selbstcheck abgedeckt.

**Update 2026-08-15, spaeter Abend -- Gateway-Autostart (`_gateway_sicherstellen()`) reparaiert,
Root Cause war ausserhalb von `fetch_ibkr.py`:** Nutzer meldete, dass `StartGateway.bat` per
Doppelklick zuverlaessig startet, per `python fetch_ibkr.py` (also ueber `os.startfile()`) aber
nicht -- Verdacht Sandbox, war es nicht. Root Cause per systematischem Debugging in IBC's
eigenem `scripts/StartIBC.bat` (nicht im Repo, lokale IBC-Installation unter `C:\Users\janne\IBC`)
gefunden, zwei gestapelte Bugs in derselben Zeile (Java-Versions-Erkennung fuer den
`moduleAccess`-Flag):
1. `for /f "... usebackq" %%A in (`java.exe ... 2^>^&1 ^| findstr ...`) do set ...` -- ein
   gepipeter Unterbefehl in Backticks bricht beim nicht-interaktiven Start (`os.startfile`/
   ShellExecute-Kette statt Explorer-Doppelklick) mit einem cmd.exe-Parserfehler ("'set' kann
   syntaktisch an dieser Stelle nicht verarbeitet werden") den kompletten Batch-Lauf ab, noch
   bevor Gateway ueberhaupt startet -- reproduziert: kein `java`-Prozess entsteht, IBC-Log
   bricht exakt an dieser Zeile ab.
2. Nach Umbau auf eine pipe-freie Variante (Zwischendatei statt Backtick-Pipe) zweiter,
   unabhaengiger Fund: `pushd "%JAVA_PATH%"` + nacktes `java.exe` (IBC's eigener Workaround-
   Kommentar dazu: "using %JAVA_PATH%\\java.exe ... causes an error") schlaegt fehl, weil auf
   diesem Rechner `NoDefaultCurrentDirectoryInExePath=1` (Machine-Env-Var) gesetzt ist -- Windows
   sucht dann nicht mehr im Arbeitsverzeichnis nach unqualifizierten .exe-Namen, `dir /b
   java.exe` findet die Datei, aber `java.exe -version` scheitert mit "Befehl nicht gefunden".
   Fix: vollqualifizierter Pfad `"%JAVA_PATH%\java.exe"` statt `pushd`+nacktem Namen (der
   urspruengliche IBC-Kommentar bezog sich vermutlich auf den *gepipeten* Backtick-Fehler aus
   Punkt 1, nicht auf den vollen Pfad an sich).

Lokal in `C:\Users\janne\IBC\scripts\StartIBC.bat` gepatcht (Backup als `StartIBC.bat.bak-
2026-08-15` daneben abgelegt) -- Datei liegt ausserhalb des Repos, ueberlebt also kein IBC-
Update; bei einem IBC-Upgrade muss dieser Fix erneut angewendet werden. Verifiziert:
`python algo/fetch_ibkr.py --verify --symbol NQ` startet Gateway jetzt automatisch und meldet
"Gateway erreichbar nach 12s." (vorher: 3 Min. Timeout, nie erreichbar). `fetch_ibkr.py` selbst
brauchte keine Code-Aenderung -- der Bug lag komplett in der vom Nutzer verwalteten
IBC-Installation.

**Zweiter, unabhaengiger Bug beim ersten echten Nachlad-Lauf gefunden und gefixt:**
`python algo/fetch_ibkr.py` (ohne Argumente) lief in `_demo()` (interner Selbsttest) statt in
den laut Docstring dokumentierten Nachlad-Modus -- `__main__`-Block hatte `if len(sys.argv) ==
1: _demo() else: sys.exit(main())`, obwohl `algo/selfcheck.py` `_demo()` bereits direkt
importiert (`from fetch_ibkr import _demo as fetch_ibkr_demo`); der `sys.argv`-Zweig war
ueberfluessig und brach den dokumentierten No-Args-Aufruf. Fix: `__main__` ruft jetzt
immer `sys.exit(main())`. Nach dem Fix erster echter Nachlad-Lauf durchgefuehrt: Register
(`raw/marktdaten/1s-abdeckung.csv`) war bereits luecklos bis 2026-08-14 (letzter Handelstag)
aus vorherigen Testlaeufen, Lauf endete sauber mit Exit 0 ohne neue Fenster.

**Ausserdem, gleicher Abend -- Standard-`python` hatte `ib_async` nicht installiert:**
`python`/`py` (ohne Versionsflag) zeigen auf diesem Rechner auf Python 3.12, in dem alle
anderen `algo/`-Pakete installiert waren, `ib_async` aber fehlte (nur eine separate 3.14-
Installation hatte es). Der dokumentierte Aufruf `python algo/fetch_ibkr.py` brach dadurch
sofort mit `ModuleNotFoundError` ab, noch bevor irgendein Download versucht wurde. Fix:
`pip install -r algo/requirements.txt` in die 3.12-Umgebung nachgeholt. Alle 27 Selbstchecks
(`algo/selfcheck.py`) bestehen weiterhin.

**Dritter Fund, gleicher Abend -- Nachlad-Modus stumm, wenn nichts zu holen ist:** Nutzer
meldete "es findet kein Download statt" bei einem Lauf ohne jede Konsolenausgabe. Root Cause:
die Nachlad-`while`-Schleife in `main()` druckt nur pro tatsaechlich verarbeitetem Tag --
ist das Register schon aktuell (kein Tag zwischen letztem Registereintrag und gestern), laeuft
die Schleife nie und es gibt keinerlei Ausgabe, obwohl das korrektes Verhalten ist (kein neuer
Handelstag seit dem letzten Lauf). Fix: `main()` druckt jetzt vor der Schleife pro Symbol
explizit "bereits aktuell bis <Tag> (letzter Handelstag: <Tag>), nichts zu holen", wenn nichts
offen ist -- Konsole bleibt nie mehr stumm.

**Beobachtung fuer den echten Backfill:** Trotz `PacingLimiter` (60 Requests/10 Min,
min. 0,5s Abstand) traten bei mehreren Testlaeufen wiederholt Pacing-Violations auf, meist
in der zweiten Haelfte eines 46-Fenster-Laufs fuer ein Symbol -- IBKRs tatsaechliche
Grenze scheint enger als die dokumentierten 60/10Min zu greifen (moeglicherweise die
"6 Requests je 2s fuer denselben Kontrakt"-Regel aus Design SS3.3, die `PacingLimiter`
nicht separat abbildet). Der eingebaute Retry faengt das ab (Fenster bleibt offen statt
falsch registriert, siehe Fix oben), aber fuer den echten 34h-Backfill lohnt sich ein
grosszuegigerer `min_gap` (z.B. 2-3s statt 0,5s) VOR dem Start, statt sich auf Retries zu
verlassen -- noch nicht umgesetzt.

**Noch offen:** Handelslose-Sekunden-Quote (SS6.5, Pflichtkennzahl) noch nicht separat
berechnet -- ergibt sich jetzt direkt aus dem Volumen-0-Anteil oben (45,8 %/58,6 % am
14.08.2026), sollte aber noch als expliziter Report-Wert in `--verify`/`/daten-1s`
auftauchen. Danach `min_gap` in `PacingLimiter` erhoehen, dann Backfill (~34h).
`raw/algo-pruefung/IBKR 1s-Datenanbindung -- Uebergabestand 2026-08-15.md` erst nach
abgeschlossener Verifikation loeschen (Design SS1).

### Backlog: sechs unbewertete Kandidaten aus dem 2026-08-16-Ingest (noch nicht implementiert)

Diese sechs Punkte standen bisher nur in der jetzt entfallenden Log-Tabelle, nie in einem eigenen
Backlog-Abschnitt -- ohne diese Migration waeren sie beim Kuerzen aus dem laufenden Bestand
gefallen (Volltext samt Quellenzitaten in `PLAN-archiv-bis-2026-08.md`, Eintraege 2026-08-16):

- **Gladhanding-Regel**: Erreicht ein Ruecksetzer die C.E. eines bullishen BISI *nicht*, soll das
  ein staerkeres Fortsetzungssignal sein als ein normaler Fill. `wiki/concepts/Gladhanding.md`.
- **TGIF-40-%-Trennkriterium**: Retracement jenseits 40 % der Weekly Range waere laut ICT kein
  TGIF mehr. Ergaenzung fuer das bereits vorhandene `algo/backtest_tgif.py` (liefert bereits
  3,7-%/22,1-%-Zahlen).
- **Kerzenzahl in einer Ineffizienz**: Fortsetzungsrate soll mit der Anzahl Kerzen sinken, die
  sich in einem FVG aufhalten (1-2 stark, >5 gescheitert). Ueberschneidet sich inhaltlich mit
  Gladhanding, ein gemeinsames `algo/backtest_gap_verweildauer.py` vorgesehen.
  `wiki/concepts/Kerzenzahl in einer Ineffizienz.md`.
- **Feiertags-/HRLR-Effekt**: zwei pruefbare Teilthesen -- kleinere Ranges nach US-Feiertagen
  (trivial) und geringere PD-Array-Praezision (interessanter, bisher ungeprueft).
  `wiki/concepts/Low Resistance Liquidity Run.md`. **Methodikfalle:** der Feiertag selbst kann auf
  ein Wochenende fallen (Beispiel 4. Juli 2026 = Samstag, betroffener Handelstag war der Montag
  danach) -- ein Filter auf "Boersenfeiertag" trifft dann gar keinen Handelstag. Filtern muss auf
  den **ersten regulaeren Handelstag nach einem Feiertagswochenende**, je nach Jahr Montag oder
  Dienstag (NYSE/CME-Feiertagsliste).
- **Continuous Contract vs. Front Month**: `raw/marktdaten/` fuehrt nur die Continuous-Reihe;
  ICTs Regel verlangt einen Front-Month-Gegencheck, der im Backtest komplett fehlt. Materialitaet
  nicht gemessen. `wiki/concepts/Continuous Contract vs. Front Month.md`.
- **ORG-C.E.-70-%-These, zweite Primaerquelle**: zwei unabhaengige ICT-Videos nennen 70 %, ohne
  Symbol/Definition zu praezisieren. Zwei offene Erklaerungen fuer die Luecke zum eigenen
  Backtest-Wert (35-43 %): Symbol (NQ vs. MNQ) und Definition (Beruehrung vs. Close) -- beides in
  `algo/backtest_org.py` pruefbar. Die These bleibt auf Nutzerwunsch aktiv in Beobachtung, siehe
  [[Algo-Trading: Arbeitsstandards]].

### Backlog: laufender Handelstag fuer `live_status.py` (2026-08-16, blockiert Live-Betrieb)

`live_status.py` liest seit 2026-08-16 NQ-1s aus `raw/marktdaten/` statt MNQ aus yfinance.
Fuer **abgeschlossene** Handelstage ist das vollstaendig (`--dry-run 2026-08-14` liefert einen
kompletten Bericht inkl. ORG-C.E. und NDOG/NWOG-Historie). Fuer den **laufenden** Tag fehlt
der Abrufweg, und `fetch_ibkr.py` kann ihn in seiner heutigen Form nicht liefern:

- `write_day_1s()` ueberschreibt nie, `fetch_symbol_day()` ueberspringt jeden Tag, dessen
  Datei existiert. Ein mitten am Tag geholter Stand waere damit dauerhaft als vollstaendiger
  Handelstag eingefroren -- derselbe Datenverlust wie `ES 2026-02-19` (endete bei 11:29 NY
  statt 17:00, sah aber fertig aus), nur diesmal automatisch in jedem Loop-Durchlauf.
- Die Registerzeilen des Teiltags wuerden `_letzter_registrierter_tag()` auf heute setzen; der
  taegliche Nachlad ("bis gestern") wuerde diesen Tag danach nie mehr holen -- stille Luecke.
- 46 Fenster je Zyklus sind fuer einen 10-Minuten-Loop ohnehin zu viel (Pacing).

`_download_1s()` verweigert den laufenden Tag deshalb bewusst mit einer klaren Meldung, statt
einen eingefrorenen Stand als "live" auszugeben (CLAUDE.md, "Frische Live-Daten"). Noetig ist
ein eigener Modus in `fetch_ibkr.py`: transientes Ziel (`algo/live/`, gitignored), keine
Registerzeilen, inkrementell nur das letzte Fenster statt aller 46.

### Backlog: Kontraktroll in `fetch_ibkr.py` sitzt zu frueh (2026-08-16, beim 1s-Umbau gefunden)

`fetch_ibkr.py` wechselt am **12.03.2026** von H2026 (Maerz) auf M2026 (Juni) -- zu einem
Zeitpunkt, an dem das Volumen noch im Maerz-Kontrakt lag. Die betroffenen Tage liegen als
`raw/marktdaten/`-Parquets vor und sehen aeusserlich vollstaendig aus (82.800 Kerzen, keine
Zeitluecke), enthalten aber einen praktisch untraded Kontrakt:

| Tag | Kontrakt | Sekunden mit Trade | Tagesvolumen |
|---|---|---|---|
| NQ 11.03. | NQH2026 | 49.515 | 467.980 |
| NQ 12.03. | NQM2026 | 4.055 | **9.042** |
| NQ 13.03. | NQM2026 | 11.077 | 26.553 |
| NQ 16.03. | NQM2026 | 43.927 | 280.694 |
| ES 11.03. | ESH2026 | 55.716 | 1.508.796 |
| ES 12.03. | ESM2026 | 24.391 | **95.786** |
| ES 13.03. | ESM2026 | 33.663 | 202.143 |

Am 12.03. ist das Volumen rund **50-fach** (NQ) bzw. **16-fach** (ES) niedriger als am Vortag.
Die Preise sind echt, aber die 1s-Mikrostruktur dieser Tage ist eine andere: FVGs entstehen
dort, weil kaum jemand handelt, nicht weil der Preis effizient wegspringt. Fuer jede Auswertung
auf Tick-/Sekundenebene sind die Tage damit nicht vergleichbar mit dem Rest.

Zwei Dinge fangen den Effekt heute ab, keines loest ihn:
- `backtest_macro.py` verwirft dank `MIN_MINUTEN` die zu duennen Bloecke automatisch und weist
  die betroffenen Tage im Bericht namentlich aus (NQ 12.03. faellt dadurch von 68 auf 22
  auswertbare Bloecke).
- Die uebrigen Bloecke bleiben aber drin und mitteln mit.

**Zu tun:** Front-Month in `fetch_ibkr.py` ueber das **Volumen** waehlen statt ueber den
Kalender -- gerollt wird, wenn der Folgekontrakt den aktuellen im Tagesvolumen ueberholt
(Standardregel im Futures-Handel), nicht an einem festen Datum. Danach die betroffenen Tage
(12./13.03.2026, beide Symbole) im richtigen Kontrakt neu holen. Solange das offen ist, gilt
`raw/marktdaten/1s-abdeckung.csv` als vollstaendig, obwohl zwei Tage die falsche Serie
enthalten.

### Backlog: drei Thesen aus der Daily-Bias-Notiz 17.08. (2026-08-17, Nutzeraussage)

Aus Jannes' eigener Bias-Notiz vom Montagmorgen (`raw/journal/Daily Bias 2026-08-17.md`, unterer
Freitextteil; Journal-Eintrag `journal/entries/2026-08-17 NQ Daily Bias.md`). Alle drei sind
falsifizierbar und noch nicht implementiert:

1. **London-Judas-These** -- *"London ist oft die Judas des Tages"*. Messbar ohne neuen Detektor:
   Wie oft liegt das Tagesextrem **gegen** die spaetere Tagesrichtung innerhalb der
   London-Killzone (02:00-05:00 NY), und wie weit traegt der Gegenlauf danach? Aufsetzen auf
   `backtest_midnight_range_judas.py` (existiert, misst den Judas gegen die Midnight Opening
   Range) statt ein zweites Skript zu bauen -- fehlt dort nur die Session-Segmentierung
   London vs. NY AM. Datenlage gut: 1s fuer NQ/ES ab 12.02.2026 (mit Luecke 05.05.-12.08.).
2. **REL-Toleranz-These** -- ein 5m-Low, das **0,25 Punkte** unter den linken relativ gleichen
   Lows liegt, entwertet den Sellside-Pool **nicht**; der Pool bleibt fuer ihn High Probability.
   Das ist direkt eine Aussage ueber `CFG.min_pen` in `tools/analyze_ohlc.py`: ab welcher
   Penetration gilt ein Liquiditaetspool als abgeraeumt statt nur angetippt? Test: Reaktionsrate
   (Rueckkehr in die Range / Fortsetzung) als Funktion der Penetrationstiefe, in Tickstufen
   0,25/0,50/1,00/2,00+. Ergebnis kalibriert eine Konstante, die heute geraten ist -- hoher
   Nutzen bei kleinem Aufwand. Kandidat `algo/backtest_sweep_toleranz.py`.
3. **Daily-Wick-Quadranten-These** -- die Qs/Hs/C.E. eines alten **Daily Premium Wicks** (sein
   Beispiel: 02.06.2026) werden noch Wochen spaeter *"selbst im 1m Chart genutzt und
   respektiert"*. Test: Reaktionsrate an C.E./Q1/Q3 historischer Daily-Wicks gegen eine
   Kontrollmenge zufaelliger Preise derselben Distanzverteilung -- ohne Kontrollgruppe ist die
   These trivial wahr (jedes Level wird irgendwann beruehrt). Kandidat
   `algo/backtest_daily_wick_quadranten.py`. **Blockiert** durch den Datenbefund unten.

**Datenbefund dabei gefunden (gehoert zum 1d-Backlog vom 2026-08-14):** Die NQ-1d-Kerze vom
**02.06.2026** meldet `C 30.712,75`, das MNQ-1h-Aggregat derselben Session dagegen `30.743,00` --
**30 Punkte Differenz**. `O/H/L` sind sauber (H 30.763,25 / L 30.317,75, gegen MNQ-1h auf 0,25
bestaetigt). Das ist ein **neunter** Tag mit 1d-Abweichung und faellt beim bisherigen Scan durch,
weil dieser gegen 5m-Aggregate ab 08.06. lief -- fuer Juni-Anfang existiert **kein** NQ-Intraday
im Bestand. Direkte Folge: Punkt 3 oben ist nicht messbar, solange der Body-Top der Kerze -- und
damit der Startpunkt jedes Premium-Wick-Quadranten -- quellenabhaengig ist. Vor dem Backtest muss
die 1d-Bereinigung fuer Mai/Juni stehen oder die Wick-Basis auf Intraday-Aggregate umgestellt
werden (wie es `rules.py::daily_hilo_from_bars` fuer H/L bereits tut, fuer den Close aber nicht).

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

> Die chronologische Log-Tabelle steht seit 2026-08-16 in `PLAN-archiv-bis-2026-08.md` und
> wird nicht fortgefuehrt -- neue Ereignisse stehen in der Commit-Message. Hier bleiben Backlog
> und aktueller Zustand.
