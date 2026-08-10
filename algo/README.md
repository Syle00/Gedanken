# algo/ -- Backtesting fuer MNQ

Ziel des gesamten Ordners: ein Handelsalgorithmus, der eigenstaendig ueber Interactive Brokers
handelt (siehe `algo/PLAN.md`, Schicht 1). Dieses Dokument erklaert **jedes Modul, das an
Backtest-Zahlen beteiligt ist**: was es testet, wie, warum genau so, und welche Grenzen es hat --
Zielgruppe ist der Nutzer selbst, ohne dass er den Code lesen muss.

> Praezisions-Audit 2026-08-06: siehe
> `docs/superpowers/specs/2026-08-06-algo-backtest-precision-audit-design.md` fuer den vollen
> Hintergrund. Kernaenderung: `algo/pnl.py` bringt echten Dollar-P&L (Punktwert statt
> Notional-Prozent, netto nach Commission). Beim Umgang mit mehrdeutigen Trades sauber
> unterscheiden: der **Anteil** solcher Trades (`dubious_pct`) steht in jedem Report
> (`backtest_bt.py`, `validate.py`, `stress_test.py`) -- die **konservative Preiskorrektur**
> (`flag_dubious`, Exit auf den Stop) fliesst dagegen nur in die "Echte $-P&L"-Zeile von
> `backtest_bt.py` ein. WinRate/ProfitFactor/Return in `validate.py` und `stress_test.py`
> bleiben unkorrigiert, `dubious_pct` sagt dort nur, wie gross die Unsicherheit ist.

## `pnl.py` -- Praezisions-Layer

**Was:** Rechnet aus den rohen Preis-Trades der `backtesting`-Bibliothek den echten
Dollar-Gewinn/Verlust (`real_pnl`), markiert Trades mit unklarer Stop/Ziel-Reihenfolge
(`flag_dubious`, `dubious_pct`) und berechnet Risiko-basierte Kontraktgroessen (`risk_size`).
**Wie:** Punktwert-Tabelle nur fuer genutzte Symbole (MNQ=$2, NQ=$20, ES=$50). `real_pnl` zieht
die Commission ab, liefert also ein NETTO-Ergebnis. Mehrdeutige Trades (Entry- und Exit-Zeit in
derselben Kerze) werden konservativ als haetten sie den Stop getroffen bewertet, nicht dem
optimistischen Ergebnis der Lib vertraut. `risk_size` deckelt die Kontraktzahl optional per
`max_notional` (= Equity x Hebel) -- ohne diesen Deckel storniert die Lib Orders mit engem Stop
kommentarlos wegen fehlender Margin, was systematisch gegen genau diese Setups selektiert.
**Warum:** Die `backtesting`-Lib rechnet P&L wie eine Aktie (Preisdifferenz * Stueckzahl ohne
Punktwert) -- fuer MNQ ($2/Punkt) war dadurch sowohl die reale Positionsgroesse als auch der
reale Dollar-Gewinn falsch (siehe Bug-Funde unten).
**Bekannte Grenzen:** Punktwert-Tabelle deckt nur MNQ/NQ/ES ab; ein neues Symbol braucht einen
neuen Eintrag, bevor `real_pnl`/`risk_size` dafuer nutzbar sind (wirft sonst `ValueError`).
Ausserdem budgetiert `risk_size` gegen `Strategy.self.equity`, und das ist in den rohen
Preispunkt-Einheiten der Lib denominiert, nicht in echten Dollar -- die 1 %-Zahl stimmt exakt
fuer den ersten Trade und ist danach eine Naeherung (nach einem Drawdown eher zu gross). Details
im Docstring von `risk_size`.

## `rules.py` -- Silver-Bullet-Regel (Signal-Schicht)

**Was:** `plan_trade(bars, when)` liefert ein Setup (Entry/Stop/Ziel) oder `None`, basierend auf
dem Silver-Bullet-Modell aus `wiki/models/Silver Bullet Model.md`.
**Wie:** FVG im aktiven Zeitfenster (London/NY AM/NY PM) + unberuehrte Zielliquiditaet als
Confluenz-Pflicht. Nutzt nur `bars[t<=when]`, nie die volle Reihe (kein Lookahead).
**Warum:** Erste konkrete, deterministische Regel aus dem Wiki, testbar per Backtest statt nur
diskretionaer nachvollziehbar.
**Bekannte Grenzen:** Nur die Basisregel (Fenster+FVG+Ziel), zusaetzliche Wiki-Confluenz
(NWOG/NDOG, Midnight-Fibs) noch nicht eingebaut (siehe `algo/PLAN.md`).

## `signals.py` -- Tages-Bias-Signale

**Was:** Acht Einzel-Signalfunktionen (Wochentag, Turn-of-Month, Range-/Richtungs-Autokorrelation,
Stat-Arb-Spread MNQ/ES, VIX-Regime, DGS10-Aenderung, WALCL-Trend), kombiniert zu einer
Feature-Matrix `build_features()`.
**Wie:** Jede Funktion sieht nur Tage strikt vor `target_day`; Kalenderwissen ueber `target_day`
selbst (Wochentag) ist erlaubt, Kursdaten nicht.
**Warum:** Rohmaterial fuer das Ensemble-Bias-Modell in `backtest_ensemble.py`.
**Bekannte Grenzen:** `_in_tom_window()` naehert Turn-of-Month ueber Kalendertage an, nicht
echte Handelstage (kein Handelskalender im Projekt, siehe `ponytail`-Kommentar im Code).
**Audit 2026-08-06:** kein Lookahead gefunden, keine Aenderung noetig.

## `backtest_bt.py` -- Silver-Bullet-Trade-Simulation

**Was:** Verdrahtet `rules.py::plan_trade` als `backtesting.Strategy`, laeuft ueber alle
verfuegbaren MNQ-Tage.
**Wie:** Pro 5m-Kerze wird `plan_trade()` mit der Historie bis zu dieser Kerze aufgerufen; bei
Setup wird eine Bracket-Order (Limit + SL + TP) platziert.
**Warum:** Zeigt, ob die Silver-Bullet-Regel ohne Confluenz-Filter profitabel ist.
**Bug gefixt (2026-08-06-Audit):** Bestellungen hatten bisher KEINE explizite Groesse -- die
Lib nutzte ihren Default (~99,99 % Kontoguthaben als Notional), nicht die im Wiki festgelegte
1-%-Risiko-Regel. Jetzt: `pnl.risk_size()` bestimmt die Kontraktzahl, `main()` druckt zusaetzlich
den echten $-P&L (`pnl.real_pnl`) und den Anteil mehrdeutiger Trades.
**Bugs gefixt (Final Review 2026-08-06):** (a) ohne Margin-Deckel stornierte der Broker 60 von
99 Setups kommentarlos -- ausgerechnet die mit engem Stop, also ein systematischer Bias; jetzt
laeuft das Sizing ueber `pnl.risk_size(..., max_notional=equity*leverage)` wie im Ensemble.
(b) Symbol wird nicht mehr ignoriert: `backtest_bt.py ES` nutzt jetzt ES' $50/Punkt statt MNQs
$2/Punkt (vorher 25x zu grosse Positionen bei falscher Beschriftung).
**Bekannte Grenzen:** Nutzt weiterhin `backtesting`s Equity-/Drawdown-Tracking in rohen
Preispunkten (Sharpe/Return% sind Naeherungen), nur `RealPnL_USD` ist der echte Dollar-Wert.
Limit-Orders verfallen ausserdem nie: ein Setup, dessen Entry-Preis erst Wochen spaeter beruehrt
wird, fuellt trotzdem noch -- obwohl `rules.py` strikt intraday und fensterbezogen plant. Das
erklaert die letzte verbleibende Margin-Stornierung eines Laufs und ist ein offener Punkt
(braucht Order-Verfall am Fenster-/Tagesende, aendert die Trade-Population).

## `backtest_ensemble.py` -- RenTec-artiges Ensemble

**Was:** Taeglicher Bias aus Logistic Regression ueber `signals.py`, filtert die
Silver-Bullet-Intraday-Regel statt sie zu ersetzen; `intraday=False` haelt stattdessen eine
tagesbasierte Position (fuer Perioden ohne 5m-Daten, siehe `stress_test.py`).
**Wie:** Bias-Totzone 45-55 % Wahrscheinlichkeit -> "neutral" (kein Trade). Partial-Taking am
ersten Swing-Punkt in Traderichtung + Stop auf Breakeven danach.
**Warum:** Kombiniert mehrere schwache statistische Einzelbefunde statt sich auf eine
diskretionaere Regel zu verlassen (siehe `docs/superpowers/specs/2026-08-05-algo-rentec-ensemble-design.md`).
**Bug gefixt (2026-08-06-Audit):** `_risk_size()` vergass den Punktwert-Faktor -- reales Risiko
pro Trade war dadurch doppelt so hoch wie die beabsichtigten 1 % (bei MNQ, $2/Punkt). Jetzt:
`pnl.risk_size()` mit `EnsembleStrategy.point_value`.
**Bekannte Grenzen:** ~150 Handelstage, 8 Features -- Overfitting-Risiko trotz L2-Regularisierung
(siehe Docstring), nur Walk-Forward-Zahlen (nicht der In-Sample-Baseline) sind belastbar.

## `validate.py` -- Monte Carlo / Walk-Forward / Parameter-Sensitivitaet

**Was:** Drei generalisierte Validierungsverfahren, unabhaengig von der konkreten Strategie
(genutzt von `backtest_walkforward.py` fuer Silver Bullet und `validate_ensemble.py` fuers
Ensemble).
**Wie:** Walk-Forward nutzt rollierende Folds (In-Sample-Parameterwahl bzw. `on_fold_train`-Hook
fuer Modell-Refit, Out-of-Sample-Test); Monte Carlo resampled die Trade-Reihenfolge 1000x fuer
Renditeverteilung/Drawdown-Perzentile.
**Warum:** Eine einzelne Backtest-Zahl ist ueberfitting-anfaellig; diese drei Verfahren zeigen,
wie stabil ein Ergebnis ueber Zeit/Parameter/Trade-Reihenfolge ist.
**Ergaenzt (2026-08-06-Audit):** `dubious_pct` ist jetzt Pflichtzeile in allen drei
Ausgaben -- zeigt, wie gross der Anteil an Trades mit unklarer Stop/Ziel-Reihenfolge ist.
**Bekannte Grenzen:** Kleine Stichprobe (siehe `algo/PLAN.md`) -- alle Zahlen sind
Groessenordnungen, keine belastbaren Ergebnisse, bis mehr Handelstage vorliegen.

## `stress_test.py` -- Historische Krisenfenster

**Was:** Testet `EnsembleStrategy(intraday=False)` gegen fuenf historische Krisenfenster (2008,
Covid, Flash Crash 2010, China 2015, Volmageddon 2018) auf NQ=F/ES=F-Tagesdaten (MNQ existiert
als Instrument erst seit 2019).
**Wie:** Bias-Modell wird strikt auf Vorlauf-Daten VOR Fenster-Start gefittet (kein
Data-Leakage aus der Krise selbst).
**Warum:** Verhaltens-Charakterisierung (Drawdown, Trade-Anzahl) in Extremsituationen, nicht als
Ersatz fuer die eigentliche Validierung.
**Ergaenzt (2026-08-06-Audit):** `dubious_pct` in der Report-Zeile.
**Bekannte, bewusst NICHT gefixte Grenze:** Der Tages-Fallback-Modus sized ueber Equity-Fraction
(~99,99 %), nicht ueber echte Kontrakte -- `pnl.real_pnl()` wird hier absichtlich NICHT
aufgerufen, ein $-Betrag waere irrefuehrend praezise. Offener Punkt fuer einen eigenen Spec,
falls dieser Modus je fuer echten Handel genutzt wird. Ausserdem: KEINE echte MNQ-P&L (NQ=F-Preis-
Proxy), `margin=0.05` (20x Hebel) OHNE Stop-Loss -- die Drawdown-Zahl ist Hebel-Mechanik, kein
Modellversagen.

## `dashboard.py` -- Live-Anschauungsfenster

**Was:** Matplotlib-Live-Fenster (oder GIF-Export), zeigt Preis/Entries/Equity/Drawdown/Signale
Kerze fuer Kerze oder Tag fuer Tag.
**Wie:** Eigene, einfachere Simulationsschleife (nicht die `backtesting`-Lib) -- Equity als
relativer Multiplikator (Start=1.0, prozentual), Sofort-Fill-Naeherung statt Limit-Order.
**Warum:** Reines Anschauungswerkzeug, damit der Backtest-Ablauf sichtbar statt nur Text ist.
**Wichtig:** **Nicht die Quelle der offiziellen Kennzahlen** (das ist `validate.py`/
`validate_ensemble.py`) -- Trades/WinRate hier sind wegen der Sofort-Fill-Naeherung nicht direkt
mit den offiziellen Zahlen vergleichbar. Titel im Fenster sagt das auch explizit ("keine
offizielle Kennzahl").
**Bekannte Grenzen:** Kein echter Dollar-Bezug (relative Prozent-Equity) -- fuer Optik/Anschauung
ausreichend, fuer Kapitalentscheidungen nicht gedacht. Bloomberg-Terminal-artige Optik ist
expliziter Zukunftswunsch (siehe `project_algo_precision_audit`-Memory), aktuell nicht geplant.

## `masters.py` -- Validierungs-Werkzeugkasten (Masters-Buch)

**Was:** Python-Portierung der Verfahren aus Timothy Masters, *Testing and Tuning Market Trading
Systems* (Apress 2018). Reine Bibliothek -- kein Backtest, kein CLI, keine Marktdaten. Herleitungen,
Formelnummern und Referenzzahlen stehen im Wiki unter
`wiki/sources/Testing and Tuning Market Trading Systems (Source).md`.

**Wie:** Portiert wird die algorithmische Substanz; alles, wofuer es fertige Numerik gibt (t-/
Beta-Verteilung, BCa-Bootstrap, Sortieren, SVD), geht an `scipy`/`numpy`. Masters' Hilfsdateien
STATS.CPP/SVDCMP.CPP/QSORTD.CPP werden also nicht nachgebaut.

| Funktion | Zweck |
|---|---|
| `guard_buffer(lookback, lookahead)` | `min(LOOKAHEAD, LOOKBACK) - 1` -- so viele juengste Trainingsfaelle streichen |
| `walkforward(n, ntrain, ntest, omit, extra)` | Fold-Generator mit Guard Buffer und Varianz-Inflations-Schutz |
| `entropy` / `clean_tails` / `gap_analyze` | Indikator-Vorpruefung: Informationsgehalt und langsames Wandern |
| `drawdown` / `dd_to_pct` / `drawdown_quantiles` | Drawdown auf Log-Renditen, absolut statt prozentual |
| `drawdown_bound` / `drawdown_bound_naive` | korrekter Doppel-Bootstrap vs. das billige, zu optimistische Verfahren |
| `lower_bound_t` / `lower_bound_bca` | Untergrenze fuer die **wahre** mittlere Rendite |
| `return_bound` / `orderstat_tail` / `quantile_conf` | Quantilgrenzen fuer **einzelne** kuenftige Renditen + wie sehr man ihnen trauen darf |
| `profit_factor` / `log_profit_factor` / `sharpe_ratio` | Kennzahlen auf Bar-Basis; PF beim Bootstrap immer logarithmiert |
| `permute_prices` / `permute_bars` / `permute_multi` | Bar-Permutation fuer den MCPT, inkl. der Inter-Bar-Gap-Falle |
| `cscv` | Dominanz-Test ueber viele Parametersaetze |
| `stoc_bias` | billige Trainings-Bias-Schaetzung aus Zufallskandidaten |
| `partition_return` | `TotalReturn = Skill + Trend + TrainingBias` |
| `bar_returns_from_trades` | **Bruecke**: `stats._trades` der `backtesting`-Lib -> Bar-Renditen |

**Warum genau so:** Die Lib `backtesting` liefert nur **Trade**-Renditen. Darauf berechnete
Kennzahlen sind systematisch extremer als bar-basierte -- Masters' Beispiel: zwei Trades mit je
+101/-100 Punkten intern (netto je +1) ergeben trade-basiert einen Profit Factor von *unendlich*
und bar-basiert 1,01. `bar_returns_from_trades()` ist deshalb die Eintrittstuer: erst damit sind
`lower_bound_*`, `return_bound` und `cscv` ueberhaupt sinnvoll anwendbar.

**Bekannte Grenzen:**

- **Nicht portiert** (mit Absicht): CoordinateDescent/Elastic Net -> `sklearn.linear_model.ElasticNetCV`
  (Namensfalle: sklearns `alpha` ist Masters' Lambda, `l1_ratio` sein Alpha); Differential Evolution
  -> `scipy.optimize.differential_evolution`; PARAMCOR (Hessian-Analyse) -- haengt an einer
  DE-Endpopulation, die es hier nicht gibt.
- `drawdown_bound()` kostet `outer * inner` Drawdown-Berechnungen. Die Defaults (500 x 1000) sind
  auf interaktive Nutzung ausgelegt; Masters rechnet 5000 x 10000. Fuer belastbare Zahlen hochsetzen.
- `stoc_bias()` braucht **mehrere tausend** Zufallskandidaten, sonst ist die Schaetzung wertlos --
  und ausschliesslich zufaellig/per Grid gezogene, keine aus gerichteter Suche.
- `cscv()` verlangt unabhaengig erzeugte Kandidaten (Grid oder Zufall). Mit Hill-Climbing oder
  genetischer Optimierung erzeugte Parametersaetze sind unzulaessig.
- `bar_returns_from_trades()` bewertet Mark-to-Market **Close-zu-Close**. Intrabar-Bewegungen
  (Stop-Durchschlaege innerhalb einer Kerze) bildet es nicht ab -- dafuer bleibt `pnl.py::flag_dubious`
  zustaendig.

**Verifikation:** `python algo/masters.py` (auch Teil von `selfcheck.py`). Die Checks pruefen
Eigenschaften, nicht nur Durchlauf -- u.a. dass permutierte Bars strukturell gueltig bleiben (alle
vier Bedingungen), dass die Multi-Markt-Permutation die Korrelation erhaelt, dass CSCV einen echten
Edge (0,00) von reinem Rauschen (0,86) trennt, dass der Doppel-Bootstrap konservativer ist als der
naive, und dass die Identitaet aus Gleichung 7-2 exakt aufgeht.

## `selfcheck.py` -- Gebuendelter Regressions-Check

**Was:** Buendelt alle `demo()`/`_demo()`-Selbstchecks (`pnl`, `rules`, `signals`,
`backtest_ensemble`) zu einem Kommando.
**Wie:** `python algo/selfcheck.py` -- Sekunden, kein neuer Backtest-Lauf.
**Warum:** Schneller taeglicher Regressions-Baustein, damit ein kuenftiger Code-Fix nicht
unbemerkt einen der hier gefixten Bugs reproduziert. Ausloese-Mechanik (Erinnerung/Loop) ist
Teil von Teilprojekt B.

## `backtest_common.py` -- Geteilte Helfer fuer die Explorationsskripte

**Was:** `find_1d_days()`, `load_rows()`, `pearson()`, `write_result()`. Verhindert, dass
Stat-Skripte sich gegenseitig nur wegen einer Funktion importieren (vorher: `pearson()` 4x
dupliziert, `load_rows()`/`find_1d_days()` nur ueber Seiteneingaenge importierbar).
**Audit 2026-08-07:** Entduplizierung + Korrektheits-Audit, siehe
`docs/superpowers/specs/2026-08-07-algo-backtest-dedup-audit-design.md`. Ein Bug gefunden und
behoben: `backtest_seasonal.py::turn_of_month()` zaehlte Tage an Monatsuebergaengen doppelt
(seit 2026-08-06 dokumentiert, jetzt gefixt).

## Exploratorische Skripte (`backtest_daily_patterns.py`, `backtest_fred_events.py`,
`backtest_ndog.py`, `backtest_nwog.py`, `backtest_ohlc.py`, `backtest_org_ce.py`,
`backtest_seasonal.py`, `backtest_tgif.py`, `backtest_fvg_specialness.py`,
`backtest_midnight_range_std.py`, `backtest_midnight_range_judas.py`)

**Was:** Reine statistische Zaehl-/Korrelationsskripte (Wochentag-Effekt, Turn-of-Month,
NDOG/NWOG-Bias, TGIF, FVG-Besonderheiten, Midnight-Range-STD/Judas-Swing, FRED-Events) --
nutzen NICHT die `backtesting`-Engine (bestaetigt per Grep, 2026-08-06), daher betrifft sie der
Punktwert-Layer aus `pnl.py` nicht. Jedes Skript trennt seit 2026-08-07 `run() -> dict` (reine
Berechnung, importierbar) von `main()` (Konsolenausgabe + `write_result()`) -- CLI-Verhalten
unveraendert. Ergebnis landet in `algo/results/<skriptname>.json` (Ausnahme:
`backtest_seasonal.py`, das schreibt weiterhin nur `algo/seasonal_tendency.json`).
**Audit 2026-08-06:** Alle 11 Skripte bestehen die Lookahead-Checkliste (keine Funde).
**Audit 2026-08-07:** Doppelzaehlungs-Bug in `backtest_seasonal.py::turn_of_month()` behoben
(siehe oben). Waehrend Task 8 ein zweiter echter Bug gefunden und gefixt: `find_days()` in
`backtest_org_ce.py` filterte nicht nach Symbol und griff faktisch deterministisch zugunsten
von ES statt MNQ (40/45 betroffene Tage), betraf/behob implizit auch die vier
Downstream-Konsumenten `backtest_fvg_specialness.py`/`backtest_midnight_range_std.py`/
`backtest_midnight_range_judas.py`/`explore_patterns.py` -- Details im `algo/PLAN.md`-Log
vom 2026-08-07. Sonst keine weiteren Bugs gefunden. `pearson()`-Duplikat (4x) und
`load_rows()`/`find_1d_days()`-Seiteneingaenge in `backtest_common.py` konsolidiert.

## 1m-Thesenskripte (`backtest_1m_gaps.py`, `backtest_macro.py`)

**Was:** Zwei eigenstaendige Skripte auf 1m-Basis, jeweils aus einer konkreten
Nutzerbeobachtung entstanden. Sie folgen nicht dem `run()`/`main()`-Muster der
exploratorischen Skripte oben, sondern bringen einen eigenen `--selfcheck` mit (deshalb auch
nicht in `selfcheck.py` eingehaengt).

- `backtest_1m_gaps.py` -- wie selten ist ein Preisvakuum zwischen zwei benachbarten
  1m-Kerzen? Zaehlt nur echte Nachbarminuten (`t2-t1 == 60s`), damit Session-Pausen nicht als
  Gap durchgehen. Anlass: das 19-Punkte-Vakuum am 2026-08-10 um 12:32 NY.
- `backtest_macro.py` -- sind die ICT-Macro-Fenster `:50-:10` messbar anders als der Rest?
  Zerlegt jeden Tag in 72 lueckenlose 20min-Bloecke; pro Stunde steht das Macro gegen die
  beiden direkt benachbarten Kontrollbloecke `:10-:30` und `:30-:50`. **Dieser Vergleich ist
  der Kern des Skripts**: ohne die Nachbarschaft gewaenne 09:50-10:10 allein durch die Naehe
  zum RTH-Open (Tageszeit-Confounder). Kennzahlen je Block: Range, |Netto|, dir = Netto/Range
  und der Tagesrang nach Range. Signifikanz per Mann-Whitney (einseitig, Macro > Kontrolle).

**Bekannte Grenzen:** Beide haengen an den 1m-Dateien in `raw/marktdaten/` -- die reichen nur
~30 Tage zurueck (yfinance-Grenze), aktuell 23 MNQ-Tage. Bloecke desselben Tages sind nicht
unabhaengig, der p-Wert in `backtest_macro.py` ist dadurch optimistisch. `MIN_BARS = 15`
verwirft Bloecke mit Datenluecken, statt sie als ruhigen Markt zu zaehlen.

## `macro_db.py`

**Was:** Eine Zeile je Macro-Fenster (`:50–:10`) je Handelstag in `algo/results/macro_db.csv` --
Vorgeschichte (Spooling-Kandidaten, Sweep-/MSS-/Displacement-Alter, offene Level), Verlauf
(Range, Nettoweg, Geradlinigkeit, Richtung), Startminute des Moves, genommene Level.

**Wie:** `build` rechnet immer alles neu und schreibt nur **vollstaendig erfasste** Fenster
(20/20 Kerzen im Fenster, 10/10 im Vorlauf); ausgeschlossene Fenster werden aufgelistet, nicht
verschwiegen. `stats` rechnet Quoten mit Wilson-Intervall gegen die Basisrate. `plot` erzeugt
drei Diagramme und `wiki/synthesis/Macro-Datenbank (laufend).md`.

**Warum:** `backtest_macro.py` beantwortet eine Frage und aggregiert sofort. Diese
Zwischenschicht macht beliebige Folgefragen rechenbar, ohne die Rohdaten erneut zu durchlaufen.

**Bekannte Grenzen:** Kleine Stichprobe -- auf Fenster-Ebene rund 21 Tage, damit sind
Einzelfenster-Aussagen nicht belastbar. Fenster desselben Tages sind nicht unabhaengig.
Fenster 23:50 fehlt fast ganz (Exportluecke), 16:50 ganz (Sessionschluss). NDOG/NWOG/ORG sind
noch keine Level-Quelle. Spooling-Kandidaten sind rein preisbasiert (kein Volumen in den Exporten).

## Security-Scan

2026-08-06: keine hartkodierten Secrets in `algo/*.py` gefunden. `algo/.secrets.yaml`
(FRED-API-Key) ist korrekt gitignored und wurde nie committet. Naechster Scan: woechentlich
oder sobald eine echte IBKR-Broker-Anbindung (Live-Keys) dazukommt -- taeglich waere aktuell
unnoetiger Aufwand ohne Live-Handel.
