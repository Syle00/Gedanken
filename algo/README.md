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
Setup wird eine Bracket-Order (Limit + SL + TP) platziert. Die Historie wird per
`extend_hist(self._hist, self.data)` inkrementell fortgeschrieben statt je Kerze neu gebaut.
**Performance-Fix (2026-08-11):** der frühere Neubau der `Bar`-Liste je Kerze war O(n²)
(~270 s je 50-Tage-Lauf); jetzt O(n), ~40 s. Ergebnis-erhaltend bewiesen (24-Tage-Trade-Diff
Bit-für-Bit identisch, Regressionsguard `backtest_bt.demo` in `selfcheck.py`). War die
Voraussetzung fuer Permutationstests (PLAN.md Backlog 10).
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
**Ergaenzt (2026-08-11, Backlog 7+9a):** Der Report weist die Trades jetzt zusaetzlich auf
BAR-Basis aus (`confidence.bar_metrics`/`print_bar_metrics`) und stellt eine BCa-Untergrenze
daneben. Warum das kein Kosmetik-Zusatz ist: auf dem ersten vollen Lauf ist der Trade-basierte
Profit Factor knapp ueber 1, der bar-basierte aber darunter -- genau Masters' Punkt, dass
Trade-Kennzahlen systematisch zu optimistisch sind. Und die BCa-Untergrenze der mittleren
Bar-Rendite liegt unter null: die Regel ist statistisch nicht von "kein Edge" zu unterscheiden.
**Bekannte Grenzen:** Nutzt weiterhin `backtesting`s Equity-/Drawdown-Tracking in rohen
Preispunkten (Sharpe/Return% sind Naeherungen), nur `RealPnL_USD` ist der echte Dollar-Wert.
Limit-Orders verfallen ausserdem nie: ein Setup, dessen Entry-Preis erst Wochen spaeter beruehrt
wird, fuellt trotzdem noch -- obwohl `rules.py` strikt intraday und fensterbezogen plant. Das
erklaert die letzte verbleibende Margin-Stornierung eines Laufs und ist ein offener Punkt
(braucht Order-Verfall am Fenster-/Tagesende, aendert die Trade-Population).

## `risk_fixed.py` / `risk_garch.py` / `risk_kelly.py` / `risk_killswitch.py` -- austauschbare Risk-Module

Siehe docs/superpowers/specs/2026-08-12-quant-risk-management-design.md. Trennt "wie viel %
Risiko" (diese vier Module) von "wie viele Kontrakte kauft das bei diesem %" (unveraendert
`pnl.py::risk_size()`). Gemeinsames Interface: `risk_pct(base_pct=0.01, **ctx) -> float`.

- `risk_fixed.risk_pct()` -- liefert immer `base_pct` (Status quo, Default in
  `SilverBulletStrategy.risk_module`).
- `risk_garch.risk_pct(hist=...)` -- skaliert `base_pct` mit einer GARCH(1,1)-Vol-Prognose
  relativ zur langfristigen GARCH-Vol (`sqrt(omega/(1-alpha-beta))`), geclippt auf
  [0.5, 1.5] x `base_pct`. Fallback auf `base_pct` unter 100 Kerzen Historie.
- `risk_kelly.risk_pct(closed_trades=...)` -- Half-Kelly (`f* = p - (1-p)/b`) aus den letzten
  30 abgeschlossenen Trades, nach oben auf `1.5 x base_pct` gedeckelt (gleiche Obergrenze wie
  `risk_garch`, rohes Half-Kelly kann bis 50 % Kontorisiko pro Trade reichen). Fallback auf
  `base_pct` unter 20 Trades oder bei einseitigem Sample (nur Gewinner/nur Verlierer).
- `risk_killswitch.allowed(peak, current, max_drawdown_pct=0.15)` -- kein Sizing-Modul, sondern
  ein Gate VOR `risk_pct()`: stoppt neue Trades, sobald der Drawdown seit dem bisherigen
  Equity-Hoch die Schwelle **erreicht** (inklusiv). Reset automatisch bei neuem Hoch. `peak`
  fuehrt die Strategie inkrementell mit (`SilverBulletStrategy._equity_peak`, O(n) statt eines
  `max()` ueber die volle Kurve pro Bar), unabhaengig vom gewaehlten `risk_module`.
  **In ECHTEN Dollar**: `self.equity` der Lib ist in Punkteinheiten ($1/Punkt) denominiert, die
  Strategie rechnet vorher um (`starting_cash + (lib_equity - starting_cash) * point_value`) --
  sonst wuerden die 15 % nicht 15 % echten Kontos bedeuten (gleicher Fehlertyp wie die
  dokumentierte Grenze in `pnl.py::risk_size()`, gefixt 2026-08-12).
  **Dauerstopp ist gewollt:** solange keine Position offen ist, bewegt sich die Equity nicht, also
  kann kein neues Hoch entstehen -- ein ausgeloester Kill-Switch stoppt den Handel im Backtest
  damit praktisch dauerhaft. Bewusste, konservative Nutzerentscheidung fuer das Backtest-Stadium,
  kein Auto-Reset per Timer/Decay. Beim Trip werden zusaetzlich alle offenen, noch nicht gefuellten
  Limit-Orders storniert (`self.orders`) -- sie verfallen hier sonst nie (siehe oben) und wuerden
  nach dem Stop noch fuellen.

Umschalten: `SilverBulletStrategy.risk_module = risk_garch` vor `Backtest(...).run()`, siehe
`algo/backtest_risk_compare.py` fuer den automatisierten Vergleich aller drei Sizing-Module.

`algo/backtest_risk_compare.py MNQ` fuehrt alle drei Sizing-Module nacheinander gegen dieselben
Silver-Bullet-Signale aus und schreibt die Vergleichstabelle (Equity, Max-Drawdown, Win-Rate,
Profit Factor, Expectancy, `dubious_pct`, 95%-Tages-VaR/Expected-Shortfall) nach
`wiki/synthesis/Risk-Management-Vergleich (laufend).md` -- ueberschreibt die Datei bei jedem
Lauf komplett.

## `backtest_ensemble.py` -- RenTec-artiges Ensemble

**Was:** Taeglicher Bias aus Logistic Regression ueber `signals.py`, filtert die
Silver-Bullet-Intraday-Regel statt sie zu ersetzen; `intraday=False` haelt stattdessen eine
tagesbasierte Position (fuer Perioden ohne 5m-Daten, siehe `stress_test.py`).
**Wie:** Bias-Totzone 45-55 % Wahrscheinlichkeit -> "neutral" (kein Trade). Partial-Taking am
ersten Swing-Punkt in Traderichtung + Stop auf Breakeven danach. Nutzt denselben inkrementellen
`extend_hist`-Aufbau wie `backtest_bt.py` (Performance-Fix 2026-08-11, gegen einen rekonstruierten
Alt-Neubau ueber 32 Tage als trade-identisch verifiziert, x12,4 schneller).
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
**Ergaenzt (2026-08-11, Backlog 8+9b):** (a) Monte Carlo weist die Max-Drawdown-Zeile jetzt
doppelt aus -- die alte Perzentil-Zeile ist als "naiv" markiert (Masters' als "incorrect"
bezeichneter Bootstrap, unterschaetzt das Risiko systematisch), darunter die korrekte
Doppel-Bootstrap-Grenze aus `double_bootstrap_drawdown()` (delegiert an
`masters.drawdown_bound`), dd_conf 0,95 und 0,99. (b) `walk_forward()` hat einen
Guard-Buffer-Parameter `omit` (Default 0), der die juengsten Trainingstage je Fold streicht.
Default 0 ist fuer beide Strategien nachweislich korrekt (Lookahead 1 -> `guard_buffer` = 0,
siehe Docstring) und byte-identisch zur Vorversion; der Parameter existiert, damit ein spaeter
verlaengerter Zielhorizont nicht still anti-konservativ wird.
**Bekannte Grenzen:** Kleine Stichprobe (siehe `algo/PLAN.md`) -- alle Zahlen sind
Groessenordnungen, keine belastbaren Ergebnisse, bis mehr Handelstage vorliegen.

## `confidence.py` -- Bar-Renditen- und Konfidenz-Report (Bruecke zu masters.py)

**Was:** Verdrahtet die masters.py-Werkzeuge (Kap. 6) in die Backtest-Reports: `bar_metrics()`
rechnet `stats._trades` per `masters.bar_returns_from_trades` in Bar-Renditen um und liefert
Profit Factor/Sharpe auf BAR- und TRADE-Basis plus einseitige 95%-Untergrenzen (t-Test und BCa)
fuer die mittlere Bar-Rendite und den Profit Factor.
**Wie:** BCa nur bei >=8 Bars und beiden Vorzeichenklassen (sonst entartet die
Bootstrap-Verteilung); der Profit Factor wird als `exp(BCa auf log PF)` gebildet, weil das rohe
PF-Verteilungsende zu schwer fuer einen Bootstrap ist (siehe `masters.log_profit_factor`).
**Warum:** Trade-basierte Kennzahlen sind laut Masters systematisch extremer als bar-basierte,
und ein Punktschaetzer sagt nichts darueber, ob die Zahl von null unterscheidbar ist -- beide
Luecken schliesst dieser Block (Backlog 7 + 9a).
**Bekannte Grenzen:** Getrennt gehalten von masters.py, damit der Werkzeugkasten
backtesting-Lib-unabhaengig bleibt; kennt daher fest die Spaltennamen der `backtesting`-Lib.

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

## 1m-Thesenskripte (`backtest_1m_gaps.py`, `backtest_macro.py`, `backtest_open_drive_vs_sb.py`)

**Was:** Zwei eigenstaendige Skripte auf 1m-Basis, jeweils aus einer konkreten
Nutzerbeobachtung entstanden. Sie folgen nicht dem `run()`/`main()`-Muster der
exploratorischen Skripte oben, sondern bringen einen eigenen `--selfcheck` mit (deshalb auch
nicht in `selfcheck.py` eingehaengt).

- `backtest_1m_gaps.py` -- wie selten ist ein Preisvakuum zwischen zwei benachbarten
  1m-Kerzen? Zaehlt nur echte Nachbarminuten (`t2-t1 == 60s`), damit Session-Pausen nicht als
  Gap durchgehen. Anlass: das 19-Punkte-Vakuum am 2026-08-10 um 12:32 NY.
- `backtest_macro.py` -- sind die ICT-Macro-Fenster `:50-:10` messbar anders als der Rest?
  Zerlegt jeden Tag in 69 lueckenlose 20min-Bloecke; pro Stunde steht das Macro gegen die
  beiden direkt benachbarten Kontrollbloecke `:10-:30` und `:30-:50`. **Dieser Vergleich ist
  der Kern des Skripts**: ohne die Nachbarschaft gewaenne 09:50-10:10 allein durch die Naehe
  zum RTH-Open (Tageszeit-Confounder). Kennzahlen je Block: Range, |Netto|, dir = Netto/Range
  und der Tagesrang nach Range. Signifikanz per Mann-Whitney (einseitig, Macro > Kontrolle).

- `backtest_open_drive_vs_sb.py` -- laesst ein starker RTH-Open-Drive (09:30-09:50) die
  Silver-Bullet-Stunde (10:00-11:00) leerlaufen? Anlass: Jannes' Satz nach dem Tapereading vom
  2026-08-11, der Move sei vor seinem Fenster gelaufen. Misst je Tag Range und
  Direktionalitaet (dir = |Netto|/Range) beider Fenster und stellt das obere Drittel der
  Open-Range dem Rest gegenueber (Mann-Whitney). **Range und Direktionalitaet werden bewusst
  getrennt gefragt** -- eine grosse, aber richtungslose Stunde ist genau der Fall, den er
  erlebt hat, und faellt bei reiner Range-Betrachtung nicht auf. Stand 2026-08-11: kein Signal
  (p = 0,45 bzw. 0,97 bei n=22), These damit unentschieden, nicht widerlegt.

### ⚠️ yfinance liefert die ersten Minuten nach Mitternacht NY nicht

**Betrifft jede Midnight-Opening-Range-Auswertung.** Fuer `MNQ=F` fehlen in Yahoos Daten
systematisch die Kerzen **00:00-00:08 NY** — an 19 von 24 MNQ-1m-Tagen, immer exakt dieselben
neun Minuten, **inklusive der 0:00-Kerze und damit des Midnight Opening Price**. Die 5m-Datei
hat dieselbe Luecke (die 00:00-00:05-Kerze fehlt), es gibt also keinen Ausweg ueber eine
groebere Aufloesung.

Am 2026-08-11 gegen den rohen `yf.download()`-Abruf verifiziert: **die Luecke steckt in der
Quelle, nicht in `fetch_yfinance.py`.** Aufgefallen ist sie nur, weil Jannes den Midnight Open
aus TradingView nannte (29 832,25) und der aus unseren Daten gerechnete Wert 7 Punkte daneben
lag (29 839,25 — das war der Open der 00:09-Kerze).

Auswirkung: eine aus 21 von 30 Minuten gerechnete Opening Range faellt **zu klein** aus, und
weil alle STD-Level Vielfache dieser Range sind, ist jede abgeleitete k-Kennzahl **aufgeblaeht**.
Zahlen, die vor dem 2026-08-11 aus diesen Skripten berichtet wurden, sind entsprechend
unbrauchbar (konkret: die frueher gemeldeten „52,3 % der Tage reissen −1 STD in London" bei
n=44 — auf sauberen Daten bleiben n=10 uebrig).

Der Riegel sitzt in `window_gaps()` (in `backtest_midnight_range_std.py`): `session_range()`
nimmt `expect_complete=True` und verwirft loechrige Fenster, `mor_levels.py` bricht mit einer
erklaerenden Meldung ab statt zu rechnen. Beide Backtests weisen die Zahl der verworfenen Tage
aus. `window_gaps()` leitet den erwarteten Kerzenabstand ueber `bar_minutes()` aus den Daten ab
— ohne das haelt es die 6 Kerzen eines 5m-Fensters faelschlich fuer 24 fehlende Minuten
(`find_days()` faellt auf 5m zurueck, wenn keine 1m-Datei existiert). Ein komplett leeres
Fenster gilt bewusst **nicht** als Luecke: ein Tag ohne Intraday-Daten ist keine loechrige
Messung, sondern gar keine.

**Ausweg:** 1m-Export aus TradingView fuer die betroffenen Tage nach `raw/marktdaten/` legen.
Mittelfristig loest der IBKR-Adapter (PLAN.md Schritt 4) das Problem an der Wurzel.

**Bekannte Grenzen:** Alle drei haengen an den 1m-Dateien in `raw/marktdaten/` -- die reichen
nur ~30 Tage zurueck (yfinance-Grenze), aktuell 22 MNQ-Tage bis einschliesslich 2026-08-10.
Der laufende Handelstag fehlt immer, weil `fetch_yfinance.py` ihn bewusst nicht schreibt
(`end` exklusiv, sonst bliebe ein Tagesstumpf liegen). Bloecke desselben Tages sind nicht unabhaengig, der
p-Wert in `backtest_macro.py` ist dadurch optimistisch. `MIN_BARS = 15` verwirft Bloecke mit
Datenluecken, statt sie als ruhigen Markt zu zaehlen; `backtest_open_drive_vs_sb.py` macht
dasselbe mit `MIN_BARS_OPEN = 15` / `MIN_BARS_SB = 45` und wirft damit Fragmenttage raus. Bei
n=21 sind beide Nicht-Befunde dort schwach -- der Test gehoert mit wachsendem Bestand wiederholt.

## `fetch_dukascopy.py` -- Forex-Tickdaten-Downloader (M1-Aggregation)

**Was:** Laedt historische Tickdaten von Dukascopy (`datafeed.dukascopy.com`, bi5-Format:
LZMA-komprimiert, 20-Byte-Records) und aggregiert sie zu 1-Minuten-Kerzen. Reine
Standardbibliothek (kein `pip install`), OHLC aus dem Mittelkurs (bid+ask)/2 -- IBKR liefert
Devisen standardmaessig als Midpoint-Bars, beide Quellen muessen dieselbe Groesse messen. Spread
wird als Zusatzspalte mitgeschrieben. Aufruf: `python algo/fetch_dukascopy.py EURUSD GBPUSD --von
2003-01-01 --bis 2026-08-11 --pause 1.0 --bericht results/x.json`.

**Drosselung (`--pause`, Default 0,5s):** Proaktive Pause zwischen JEDER Stundenabfrage, nicht
nur nach Fehlern -- Dukascopy blockt bei zu hoher Anfragerate mit HTTP 429. `hole_stunde()`
behandelt 429 zusaetzlich mit eigenem 15s×Versuch-Backoff statt des generischen 2^Versuch.
**Wichtig:** eine IP-seitige 429-Sperre kann laenger anhalten als jede sinnvolle Pause ausgleicht
-- wenn selbst ein isolierter Einzel-Request ohne jede Bulk-Last weiterhin 429/Timeout liefert
(siehe Vorfall 2026-08-11, `algo/PLAN.md`), hilft nur Abwarten, kein weiteres Erhoehen von
`--pause`. In diesem Fall nicht weiter testen (verlaengert die Sperre eher) und den Nutzer
informieren statt automatisch neu zu starten.

**Warum:** Nutzerentscheidung 2026-08-11, das Projekt bewusst auf Forex-Paare zu erweitern
(bisher nur MNQ). Ablage getrennt von `raw/marktdaten/` unter `raw/marktdaten-tief/<jjjj>/<mm>/
<tt.mm.jjjj>/<SYMBOL> <jjjj-mm-tt> 1m.csv` (gitignored) -- zweite Datenstufe, Umfang gehoert
nicht ins Git-Repo. Nur M1 wird geladen, keine rohen Tick-Dateien (Groessenersparnis); alle
groeberen Timeframes (5m/15m/1h/4h/1d) werden bei Bedarf lokal aus M1 resampled.

**Bulk-Lauf 2026-08-11 -- zweimal gescheitert, aktuell pausiert:** `algo/dukascopy_bulk.sh` soll
sequenziell EURUSD, USDJPY, GBPUSD, USDCHF, AUDUSD, USDCAD, NZDUSD, EURJPY, EURGBP, GBPJPY je
2003-01-01 bis 2026-08-11 laden. 1. Versuch (ungedrosselt) noch waehrend EURUSD/Tag 1 per
`taskkill` beendet (Nutzerwunsch, keine unvollstaendigen Dateien). 2. Versuch mit `--pause 1.0`
lief ~1h ohne eine einzige neue Datei, dann Diagnose: selbst ein isolierter Einzel-Request ohne
Bulk-Last lieferte weiterhin HTTP 429/Timeout -- **IP-seitige Sperre bei Dukascopy**, kein
Tempoproblem mehr. Auf Nutzerwunsch gestoppt, bewusst nicht weiter gegen die Sperre getestet
(Details siehe `algo/PLAN.md`, Eintrag "Dukascopy-Bulk-Lauf (2.) an IP-Sperre gescheitert").
Skript und Log (`algo/dukascopy_bulk.sh`, `algo/dukascopy_bulk.log`) bleiben liegen; naechster
Versuch braucht eine laengere Wartezeit plus hoehere `--pause` (3-6s). Am selben Tag kam
zusaetzlich ein manueller histdata.com-Import dazu, siehe `ingest_histdata_xlsx.py` unten.

**Bekannte Grenzen:** Sequenziell, ein HTTP-Request pro Stunde -- kein Concurrency-Limit noetig,
aber entsprechend langsam bei grossen Zeitraeumen. Fruehe Jahre liefern fuer manche Paare
erwartungsgemaess durchgehend leere Stunden (Paar noch nicht gehandelt) -- das ist keine Luecke,
sondern korrekt, muss aber beim Luecken-Report nach Abschluss beruecksichtigt werden. Nach
Abschluss steht die Vollstaendigkeits-/Luecken-Pruefung laut Arbeitsstandards ("Marktdaten wie
Gold behandeln") noch aus.

## `ingest_histdata_xlsx.py` -- Import manueller histdata.com-XLSX-Exporte

**Was:** Importiert `HISTDATA_COM_XLSX_<SYMBOL>_M1<JAHR>.zip`-Archive (histdata.com, Generic-XLSX,
fertige M1-Bars statt Ticks) nach `raw/marktdaten-tief/`. Aufruf: `python
algo/ingest_histdata_xlsx.py raw/HISTDATA_COM_XLSX_EURUSD_M12000.zip`. Zeitkonvertierung: histdata
liefert laut eigener FAQ eine **feste EST-Zeitzone (UTC-5) ohne DST** -- einfache
+5h-Verschiebung, keine Fallunterscheidung noetig. Tagesordner richten sich trotzdem nach dem
echten NY-Kalendertag (`ZoneInfo`, mit DST), gleiche Begruendung wie bei `fetch_dukascopy.py`.
Sekundenaufloesung ueber `.as_unit("s")`, nie manuelle Division (CLAUDE.md-Vorgabe).

**Warum eigenes Dateisuffix ` 1m (bid).csv`:** histdata.com liefert laut FAQ **Bid-Preise, nicht
Mid** ("bar prices ... are based on the tick Bid price") -- eine andere Konvention als
`fetch_dukascopy.py` (dort bewusst Mid, weil IBKR Devisen als Midpoint-Bars liefert). Damit Bid-
und Mid-Bestand nie versehentlich in denselben Backtest gemischt werden, tragen histdata-Importe
das Suffix ` (bid)` statt ` 1m.csv`.

**Erster Import 2026-08-11 (EURUSD, Jahr 2000):** 182 Handelstage, 143.042 Minutenkerzen,
2000-05-30 bis 2000-12-29 (Jan-Mai 2000 fehlt, vermutlich histdata.com-seitige Grenze fuers erste
verfuegbare Jahr). Gegen zwei unabhaengige Fakten geprueft, bevor der Import als vertrauenswuerdig
galt: (1) Wochenend-Luecken-Muster (Freitagsschluss ~16:20-16:47 unabhaengig von Sommer-/
Winterzeit) passt zu einer festen statt lokal-NY-Zeitzone. (2) Minimum der Datei **0,8229 am
2000-10-26** trifft das dokumentierte EUR/USD-Allzeittief (0,8225-0,8230, 26.10.2000) fast exakt.
OHLC-Konsistenz und Monotonie sauber, keine Duplikate.

**Bekannte Grenzen:** Bid-Bestand ist bis auf Weiteres von Backtests ausgeschlossen (Preisbasis
weicht von der Mid-Konvention ab, siehe oben) -- bewusste Entscheidung noch offen, ob/wie beide
Bestaende kombiniert werden. Weitere Jahre/Paare kommen vermutlich manuell dazu (Nutzer laedt
selbst von histdata.com herunter, kein automatisierter Downloader -- deren Anti-Scraping-Token
macht das unattraktiv gegenueber Dukascopy).

## `macro_db.py`

**Was:** Eine Zeile je Macro-Fenster (`:50–:10`) je Handelstag in `algo/results/macro_db.csv` --
Vorgeschichte (Vorlauf-Kandidaten, Sweep-/MSS-/Displacement-Alter, offene Level), Verlauf
(Range, Nettoweg, Geradlinigkeit, Richtung), Startminute des Moves, genommene Level, und die
**Exkursion ab Fenster-Open ueber 20/40/60 Minuten** (`mfe_*`) -- letztere, weil ICT sagt, der
Move *beginne* im Macro und laufe darueber hinaus; der reine Blockinhalt kann das nicht sehen.

**Wie:** `build` rechnet immer alles neu und schreibt nur **vollstaendig erfasste** Fenster
(20/20 Kerzen im Fenster, 10/10 im Vorlauf); ausgeschlossene Fenster werden aufgelistet, nicht
verschwiegen. `stats` rechnet Quoten mit Wilson-Intervall gegen die Basisrate. `plot` erzeugt
drei Diagramme und `wiki/synthesis/Macro-Datenbank (laufend).md`. **Ohne Subcommand** (z.B. per
Run-Knopf der IDE) laeuft `stats`, und die CSV wird vorher neu gebaut, wenn sie fehlt, aelter
als die Rohdaten ist oder nicht mehr zum aktuellen Spaltensatz passt.

**Warum:** `backtest_macro.py` beantwortet eine Frage und aggregiert sofort. Diese
Zwischenschicht macht beliebige Folgefragen rechenbar, ohne die Rohdaten erneut zu durchlaufen.

**Bekannte Grenzen:** Kleine Stichprobe -- auf Fenster-Ebene rund 21 Tage, damit sind
Einzelfenster-Aussagen nicht belastbar. Fenster desselben Tages sind nicht unabhaengig.
Fenster 23:50 fehlt fast ganz (Exportluecke), 16:50 ganz (Sessionschluss). NDOG/NWOG/ORG sind
noch keine Level-Quelle. Vorlauf-Kandidaten sind rein preisbasiert (kein Volumen in den Exporten).
In der **letzten Handelsstunde** gilt das `:50-:10`-Raster laut ICT nicht (dort 15:15-15:45 und
15:45/15:50-16:00) -- die Zeile `15:50` laeuft ueber den RTH-Schluss hinaus und ist nur
eingeschraenkt vergleichbar. Die `exc_*`/`mfe_*`/`reach10_*`-Spalten sind **Zielgroessen** und
sehen bewusst Kerzen nach dem Fensterstart -- kein Lookahead-Verstoss, aber auch nicht als
Vorhersagemerkmal verwendbar.

## Security-Scan

2026-08-06: keine hartkodierten Secrets in `algo/*.py` gefunden. `algo/.secrets.yaml`
(FRED-API-Key) ist korrekt gitignored und wurde nie committet. Naechster Scan: woechentlich
oder sobald eine echte IBKR-Broker-Anbindung (Live-Keys) dazukommt -- taeglich waere aktuell
unnoetiger Aufwand ohne Live-Handel.

## `backtest_1p_fvg_woche.py` -- Wochenrelevanz des 1st Presented FVG

**Was:** Prueft die ICT-Behauptung, dass das 1.p FVG der Montags-NY-AM-Session die ganze Woche
relevant bleibt, und ob das erste FVG einer Session ueberhaupt besonders ist.

**Wie:** Drei getrennte Tests, alle auf der 1.p-Definition "komplette 3-Kerzen-Formation
innerhalb 9:30-11:00" (`am_fvgs()`/`first_presented_fvg()`):

- **(A)** Touch am unmittelbaren Folgetag, Montag gegen Di/Mi/Do. Der Vergleich muss auf einen
  Tag normiert sein, sonst haette das Montags-FVG vier Resttage Zeit und das Donnerstags-FVG
  einen -- der scheinbare Vorsprung waere reine Exposure.
- **(B)** Deskriptiv: wird das Montags-FVG irgendwann Di-Fr beruehrt, an welchem Tag zuerst.
  Das ist die woertliche Behauptung, aber ohne Kontrollgruppe und darum allein nicht belastbar.
- **(C)** 1.p FVG gegen die uebrigen FVGs derselben Session (gleicher Tag, gleiche Exposure).

**Warum die Distanz mitlaeuft:** ein FVG dicht am Preis wird fast zwangslaeufig beruehrt. Ohne
den Median-Abstand Schlusskurs->Zone waere (C) systematisch unfair zuungunsten des 1.p FVG, das
als frueheste Zone am weitesten weg liegt. Fisher exact statt Mann-Whitney, weil die Kennzahl
binaer ist (beruehrt ja/nein).

**Bekannte Grenzen:** Datenbasis klein (5m: 9 Montage, 1m: 4) -- kein Test wird signifikant, das
Ergebnis ist unentschieden, nicht negativ. FVGs desselben Tages sind nicht unabhaengig
(Clustering), der p-Wert in (C) ist dadurch zu optimistisch. Tagesdateien ueberlappen sich
(Globex 18:00-17:00), darum werden Bars ueber `b.t.date() == d` eindeutig einem Kalendertag
zugeordnet. Eigener `--selfcheck` (nicht in `selfcheck.py` eingehaengt, wie die anderen
Thesenskripte).

## `backtest_org_std_extrema.py` -- Setzen STD-Projektionen die Extrema?

**Was:** Prueft, ob Session- oder Daily-High/Low auf den STD-Projektionen der ORG bzw. der
Opening Range liegen.

**Wie:** Zwei Basen, weil das Wiki beide kennt -- `org` (Gap 16:14->9:30) und `or_`
(Opening Range 9:30-10:00). Level in 0,5er-Schritten bis 3,0 STD beidseitig vom jeweiligen
Rand. Pro Tag wird der Abstand des Extremums zum naechsten Level gemessen, relativ zur
Gap-/Range-Groesse.

**Warum die Nullerwartung der Kern ist:** die Level stehen im Abstand 0,5 STD. Ein
Trefferfenster von +-`tol` deckt damit `2*tol/0,5` der Preisachse ab -- bei tol=0,05 sind das
20 %. Eine Trefferquote von "20 %" waere also **exakt Zufall**, nicht Bestaetigung. Der
Binomialtest laeuft einseitig gegen genau diesen Wert. Zusaetzlich wird der Median-Abstand
ausgegeben: bei Gleichverteilung liegt er bei 0,125 STD.

**Zirkularitaet vermieden:** fuer die `or_`-Basis zaehlen nur Extrema ab 10:00. Sonst waere
das High/Low der Opening Range selbst der Treffer.

**Bekannte Grenzen:** 42 Tage (5m) bzw. 23 (1m) -- kein Test signifikant, Ergebnis ist
"nicht gestuetzt", nicht "widerlegt". Der ORG-Anker ist bei groberen TFs ungenau (5m liefert
die 16:10-Kerze statt 16:14), darum ist 1m die belastbarere Variante. Eigener `--selfcheck`.

## Tick-Raster (`analyze_ohlc.TICK_SIZE`, `pnl.round_to_tick`)

**Was:** Der Kontrakt bewegt sich nur in festen Schritten (MNQ/NQ/ES 0,25 Punkte). Jeder
*abgeleitete* Preis muss darauf liegen, sonst ist er nicht handelbar.

**Wo:** `tools/analyze_ohlc.py::TICK_SIZE` + `to_tick()` sind die einzige Quelle der Wahrheit
(stdlib-only, unterste Schicht). `algo/pnl.py` importiert von dort und bietet
`round_to_tick(price, symbol, mode)` fuer die `algo/`-Module. Zwei getrennte Tabellen waeren
frueher oder spaeter auseinandergelaufen.

**Betroffen sind nur abgeleitete Werte** -- Kursdaten selbst kommen tick-konform von der
Boerse. Krumm werden: C.E. (`(lo+hi)/2` trifft zur Haelfte zwischen zwei Ticks), Quadranten/
Oktanten/16tel einer Range, Stops aus prozentualen Puffern.

**Rundungsrichtung:** `nearest` fuer Analyse-Level. Order-Preise gerichtet, nie zugunsten des
Backtests -- Entry schwerer zu fuellen (long ab, short auf), Stop und Ziel weiter weg.

**Bekannte Grenze:** `fvgs()`/`org_gap()` runden nur, wenn `tick` uebergeben wird. Ohne den
Parameter bleibt der rohe Mittelwert stehen -- Absicht, damit das Modul symbolagnostisch
bleibt (Forex hat 0,00001), aber es heisst: neue Aufrufer muessen `tick` mitgeben.
