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

**`plan_trade_hp_fvg(bars, when, prev_day_hi, prev_day_lo)`** -- zweite, eigenstaendige Regel
(High-Probability-FVG, siehe `wiki/concepts/Fair Value Gap (FVG).md` -> "Wo High-Probability-
FVGs entstehen"). Anders als `plan_trade()` **kein Fensterzwang** (der zugehoerige Backtest
`backtest_hp_fvg.py` lief ganztaegig). Entry/Stop/Ziel 1:1 aus `backtest_hp_fvg.py::simulate`.
Vortagesrange kommt als Parameter rein statt selbst geladen zu werden. Drei Masterclass-Kriterien
(`require_kz`/`require_zone`/`require_bias`) einzeln togglebar, alle per Default AUS -- gemessene
Kante bleibt duenn (36-38% Win bei 2R), Killzone allein nachweislich wirkungslos. IFVG und
Reclaimed FVG bewusst noch nicht eingebaut (siehe `algo/PLAN.md`-Backlog).

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

## `ingest_tvexport.py` -- Timeframes und die Stempel-Sperre

**Was:** Nimmt einen TradingView-Export, splittet ihn nach Handelstagen und merged ihn in
`raw/marktdaten/`. Konfliktregel: bei gleichem Zeitstempel gewinnt der **neue Export**
(TradingView revidiert open/close nach). `--tf` (Default `1m`) steuert Dateinamen, Soll und
Lueckenschritt; das Soll skaliert aus dem 1m-Profil (1380 -> 5m 276, 1h 23, 1d 1).

**Tagesbalken (`--tf 1d`) werden auf die Bestandskonvention normalisiert.** Der Bestand
stempelt jeden Tagesbalken auf **00:00 UTC des Handelstags** (2026-08-14 ueber alle 86024
1d-Dateien geprueft, null Abweichungen; UTC-verankert, also ohne DST-Sprung). TradingView
stempelt stattdessen auf den Sessionstart 18:00 NY. `tagesstempel()` rechnet das um, sonst
kollidieren die beiden Konventionen nicht, sondern stehen **nebeneinander**: ein erster Lauf
ohne Normalisierung schrieb in 5172 Tagesdateien einen zweiten Balken (MNQ 13.08.: Close
30201,5 neben 30223,5) und wurde komplett zurueckgerollt. Als Backstop bricht `ingest()`
zusaetzlich mit `ValueError` ab, sobald ein Handelstag nach dem Merge ueber dem Profil-Soll
laege -- und schreibt dann **gar nichts** (die Schreibschleife liegt hinter der Pruefung
aller Tage).

**`--nur-neue-tage` legt nur fehlende Handelstage an.** Gedacht fuer Quellen, die dieselbe
Serie in anderer Qualitaet liefern. Konkret gemessen am 2026-08-14: TradingView und der
yfinance-Bestand weichen im Median nur +1,25 (MNQ) bzw. +2,00 (YM) Punkte voneinander ab --
normale Settlement-gegen-Close-Differenz -- an einzelnen Tagen aber um bis zu 621 bzw. 1373
Punkte. Kein konstanter Offset, also kein Back-Adjustment, sondern einzelne echte Divergenzen
(Roll-Tage-Verdacht). Ein voller Merge haette 1763 von 1783 MNQ- und 3270 von 3389 YM-Tagen
revidiert; solche Tage gehoeren angesehen, nicht pauschal ueberschrieben.

**⚠️ Continuous gegen echten Kontrakt.** Die 1D-Exporte sind Continuous-Symbole
(`MNQ1!`/`MES1!`/`YM1!`), der 1m-Bestand kommt vom echten Kontrakt (`MNQU2026`). Das sind
verschiedene Preisreihen, nicht dieselbe in grober: MNQ 13.08. schliesst im Kontrakt auf
30216,25, der `MNQ1!`-Tagesbalken auf 30201,5 -- ein Wert, auf den **keine** Kontraktminute
schliesst. Nutzerentscheidung 2026-08-14: `raw/marktdaten/` fuehrt je Symbol die
**Continuous-Reihe** (der yfinance-Bestand ist ohnehin continuous). Wer 1d und 1m desselben
Symbols gegeneinander rechnet, vergleicht damit weiterhin zwei Serien -- beim Bau von
`data_gate.py`/`backtest_common.load_range()` beachten.

## `backfill_yfinance.py` -- ergaenzt Luecken in BESTEHENDEN Dateien

**Was:** Laedt denselben yfinance-Bereich wie `fetch_yfinance.py`, schreibt aber nur die
Zeitstempel in eine bestehende Datei, die dort noch **fehlen**. Legt bewusst keine neuen
Dateien an -- das bleibt `fetch_yfinance.py`, weil nur das den Tagesrand korrekt abschneidet.

**Warum:** `fetch_yfinance.write_day()` ueberschreibt grundsaetzlich nie (schuetzt
TradingView-Daten vor yfinance). Bricht ein Abruf mittendrin ab, friert der Stumpf damit
**fuer immer** ein -- der naechste Lauf meldet nur noch "existiert bereits, uebersprungen".
Gemessen am 2026-08-13: alle 10 Forex-Paare hatten fuer den 11.08. nur ~765 statt ~1440
Kerzen (Ende 06:45 NY) seit dem abgebrochenen Lauf vom 11.08.; MNQ 03.08. stand bei 300 statt
1369. Die Spec `docs/superpowers/specs/2026-08-12-marktdaten-schicht-design.md` benennt den
Fall ("Abgebrochener Download"), hatte aber kein Werkzeug dagegen.

**Wie:** Konfliktregel **umgekehrt** zu `ingest_tvexport.py` -- hier gewinnt der **Bestand**.
Vorhandene Kerzen werden nie revidiert, nur abweichende gezaehlt und im Bericht ausgewiesen.
Damit gilt "yfinance ueberschreibt nie" (Spec 3.2) weiter woertlich. Reuse statt Neubau:
`download_interval`/`trading_day`/`symbol_prefix` aus `fetch_yfinance.py`, `lies`/`schreib`/
`luecken` aus `ingest_tvexport.py`.

Die Lueckenmeldung braucht den Kerzenabstand des Timeframes (`luecken(ts, schritt)`,
gespeist aus `TF_SEKUNDEN`). Bis 2026-08-14 stand dort fest 60 s: auf `--tf 5m` meldete
darum *jede* Kerze eine Luecke ("Luecken danach: 275" bei 276 Kerzen) und eine echte Luecke
waere im Rauschen untergegangen.

```
python algo/backfill_yfinance.py 2026-08-10 2026-08-13 --symbol EURUSD=X [--dry-run]
python algo/backfill_yfinance.py --demo
```

**Bekannte Grenzen:** Dieselben yfinance-Fenster wie `fetch_yfinance.py` (1m ~30 Tage; aeltere
Chunks liefern eine Yahoo-Fehlermeldung statt leerer Daten -- laut und harmlos). Ergaenzt nur
1m-Aufloesung sinnvoll; die aus dem alten, kuerzeren 1m gerechneten 5m/15m/1h/1d-Dateien
desselben Tages bleiben stehen und sind danach **veraltet** (Spec-Entscheidung 5: nicht
loeschen, der Loader soll den aus 1m gerechneten Wert vorziehen -- `load_range()` ist noch
nicht gebaut, bis dahin ist das eine offene Inkonsistenz, siehe `PLAN.md`).

### ⚠️ AUDUSD und NZDUSD sind bei yfinance faktisch 2m-Daten, abgelegt als "1m"

**Gemessen am 2026-08-13, ueber alle vorliegenden Tage.** `AUDUSD=X` und `NZDUSD=X` liefern
ueber `interval="1m"` durchgaengig nur **jede zweite Minute**: 719 statt 1440 Kerzen pro Tag,
Abstandsverteilung 717×120 s und 1×240 s -- kein einziger 60-s-Abstand. Gegenprobe am selben
Tag: `EURUSD=X` 1439 Kerzen, 1437×60 s. Der Effekt ist also paar-spezifisch, kein
Pipeline-Fehler, und ein erneuter Abruf aendert nichts (per `backfill_yfinance.py` geprueft:
382 → 719, nicht → 1440).

**Auswirkung:** Jede Auswertung, die diese beiden Paare als 1m behandelt, laeuft auf halber
Aufloesung -- Opening Ranges, FVG-Erkennung und Sweep-Detektion sehen die Haelfte der Kerzen
nicht. Die acht uebrigen Paare sind nicht betroffen. Bis das im Torwaechter (Spec 3.1) haengt:
AUDUSD/NZDUSD nicht fuer minutengenaue Auswertungen verwenden, oder bewusst als 2m behandeln.

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
<tt.mm.jjjj>/<SYMBOL> <jjjj-mm-tt> 1m.csv` -- zweite Datenstufe. ⚠️ **Nicht gitignored**, trotz
mehrfach anderslautender Kommentare in diesem Repo: `.gitignore` versioniert `raw/` bewusst
vollstaendig ("Vault soll vollstaendig gesichert sein"), siehe root-`.gitignore`-Kommentar.
Der 10-Paare-Bulk-Import per histdata.com (2026-08-14) hat das mit 73.100 Dateien / ~82 Mio.
Zeilen in einem Commit demonstriert -- entsprechend gross ist jetzt die Repo-Historie. Nur M1
wird geladen, keine rohen Tick-Dateien (Groessenersparnis); alle groeberen Timeframes
(5m/15m/1h/4h/1d) werden bei Bedarf lokal aus M1 resampled.

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
Bestaende kombiniert werden. Automatisierter Bulk-Download inzwischen vorhanden, siehe
`fetch_histdata.py` unten (2026-08-14, nachdem `fetch_dukascopy.py` per IP gesperrt wurde).

## `fetch_histdata.py` -- automatisierter histdata.com-Downloader (Live-ASCII-Endpoint)

**Was:** Laedt M1-Forex-Bars automatisiert vom `get.php`-Live-Endpoint von histdata.com (Token aus
der Referer-Seite gescraped, per `re`+`urllib`, keine `requests`/`bs4`-Abhaengigkeit). Ersatz fuer
`fetch_dukascopy.py`, seit dieses per IP gesperrt wurde (2026-08-14, siehe PLAN.md). Aufruf:
`python algo/fetch_histdata.py EURUSD --von 2020-01-01 --bis 2020-12-31`. Chunking: ein
Jahres-Request fuer vergangene Jahre, monatsweise fuers laufende Jahr (Serverseitige Vorgabe).
Gleiches Bid-Suffix-Konzept wie `ingest_histdata_xlsx.py` (` 1m (bid).csv`).

**⚠️ Zeitkonvertierung weicht von `ingest_histdata_xlsx.py` ab, per Messung entschieden, nicht
geraten:** Die histdata.com-FAQ ("feste EST ohne DST") stimmt fuer die Legacy-XLSX-Exporte oben,
aber **nicht** fuer diesen Live-Endpoint -- an zwei Sommertagen (2025-07-01, 2026-07-01, je einmal
Jahres- und Monats-Chunk) war eine feste +5h-Verschiebung gegen den TradingView-1h-Export
durchgaengig 1h daneben (teils `mid < bid`, physikalisch unmoeglich), waehrend Winter (2026-01-05)
exakt passte -- klassisches DST-Muster. `fetch_histdata.py` konvertiert deshalb per `zoneinfo`
(`America/New_York`, mit DST) statt per fixer Verschiebung. Nach dem Fix: alle drei Testtage bei
94-100% `mid >= bid`-Konsistenz, Restabweichung ~0,3-0,4 Pip (plausibler halber Spread).

**⚠️ Nachtrag 2026-08-15 -- die obige Regel gilt nur bis 2018.** Die Verifikation oben testete
zwei Sommertage und einen Wintertag. An solchen Tagen sind US- und EU-Sommerzeit gleichzeitig
aktiv bzw. gleichzeitig aus; die US- und die EU-Umstellungsregel sind dort **nicht
unterscheidbar**. Sie unterscheiden sich nur in den ~4 Wochen pro Jahr zwischen den beiden
Umstellungsterminen. Messung genau dort, quellenunabhaengig ueber die Wochengrenzen des
24x5-Marktes (Freitagsschluss 17:00 NY, Sonntagsoeffnung 17:00 NY), alle 10 Paare:

| Woche | 2007-2018 | 2019-2026 |
|---|---|---|
| Luecken-Woche (US != EU) | letzte Freitagskerze 16:59 NY ✓ | **15:59 NY** (1h zu frueh) |
| gewoehnliche Woche | 16:59 NY ✓ | 16:59 NY ✓ |

Der Endpoint hat also **2019 die Umstellungstermine** von der US- auf die EU-Regel gewechselt,
der Offset (-5/-4) blieb -- typisch fuer eine europaeische Broker-Serveruhr (EET/EEST minus 7h).
`label_zu_epoch()` bildet das als zwei Regime ab: vor `EU_REGEL_AB` (2019-01-01) echte
`America/New_York`-Zeit, danach "Europe/Berlin minus 6h". Der Umschalttermin ist nur auf
2018-11-05..2019-03-09 eingrenzbar -- in diesem Intervall liegt keine Luecken-Woche, die Wahl
darin wirkt sich also auf kein Datum aus. Sechs Selbstcheck-Faelle inkl. Negativkontrolle.
**Bereits geladener Bestand ist davon betroffen** (140 Handelstage je Paar, 2,40 % der Kerzen) --
Reparatur siehe `repair_dst_2019.py` unten.

## `repair_dst_2019.py` -- Umstempeln des DST-Versatzes im vorhandenen Bestand

**Was:** Verschiebt die Zeitstempel der betroffenen Tagesdateien in `raw/marktdaten-tief/` um
+1h und sortiert sie nach NY-Tag neu ein. `--apply` schreibt, ohne Flag Trockenlauf;
`--stichprobe` listet die Monats-Chunks fuer eine Gegenprobe per frischem Download.

**Wie:** Die Luecken-Fenster werden aus `zoneinfo` berechnet (nicht als Datumsliste gepflegt),
ab `EU_REGEL_AB`. Alle betroffenen Dateien werden gelesen, +3600 s gerechnet und nach NY-Tag neu
gebuendelt -- noetig, weil die letzte Stunde eines Tages durch die Verschiebung in die Datei des
Folgetags wandert. Vor dem Schreiben laeuft `pruefe_kerzen()` wie im Downloader.

**Warum umstempeln statt neu laden:** Der Fehler ist eine reine Beschriftung -- jede Kerze
existiert, nur ihr Zeitstempel ist 3600 s zu klein, die OHLC-Werte sind unberuehrt. Das
Umstempeln ist verlustfrei und exakt aequivalent zu einem Neu-Download, holt aber nicht den
oben dokumentierten Live-Feed-Drift des juengsten Datenrands in den Bestand.

**Tragende Annahme, im Code geprueft statt vorausgesetzt:** alle Sommerzeit-Umstellungen fallen
auf einen Sonntag, der Forex-Markt oeffnet aber erst Sonntag 17:00 NY -- beide Fenstergrenzen
liegen damit im Wochenende, es kann keine Kerze ueber den Fensterrand hinauswandern. Das Skript
zaehlt Grenzueberschreitungen mit und warnt; Trockenlauf ueber alle 10 Paare: **0 Faelle**,
1 962 205 Kerzen erfasst.

**Bekannte Grenzen:** (1) Nach `--apply` ist `python algo/build_parquet.py` zwingend, sonst
traegt `algo/cache/` weiter die alte Zeitachse. (2) Das Skript ist **nicht idempotent** -- ein
zweiter Lauf verschiebt noch einmal um +1h. Vor einem Wiederholungslauf den Bestand pruefen
(Freitagsschluss muss auf 16:59 NY liegen). (3) Es repariert nur `raw/marktdaten-tief/`, nicht
`raw/marktdaten/` (Futures, andere Quelle, nicht betroffen).

**Bulk-Import 2026-08-14 abgeschlossen:** alle 10 Paare (EURUSD + GBPUSD/USDJPY/USDCHF/AUDUSD/
USDCAD/NZDUSD/EURJPY/EURGBP/GBPJPY), 2003-2026, 73.100 Tagesdateien, 0 echte Fehler. Kein 429
oder IP-Sperr-Hinweis unter diesem Lastprofil (1s Pause zwischen Chunks) -- histdata.com verhaelt
sich anders als Dukascopy. `parse_zip()` deduped exakte Zeitstempel-Duplikate automatisch
(histdata.com liefert vereinzelt einen Block doppelt) und zaehlt separat Faelle mit
ABWEICHENDEN Werten am selben Zeitstempel.

**⚠️ Bekannte Grenze -- juengster Datenrand ist nicht stabil:** die letzten 1-2 Monate jedes
Paares (aktuell Juli/August 2026) zeigen wiederholt Zeitstempel mit widerspruechlichen Werten
zwischen zwei Downloads derselben Datei im Abstand von Minuten -- der Live-Feed konsolidiert sich
dort offenbar noch nach. Betrifft alle 10 Paare in unterschiedlicher Staerke (2 bis 119 Faelle je
Chunk beobachtet). Vor praezisionskritischer Nutzung den juengsten Rand erneut ziehen und gegen
den aktuellen Stand diffen; aeltere Jahre (2003 bis ca. 2 Monate vor "heute") sind stabil.

## `fill_luecken_dukascopy.py` -- Nachfuellen fehlender Vollstunden aus Dukascopy

**Was:** Sucht Handelstage, an denen mehr als drei erwartete NY-Vollstunden **komplett leer**
sind, holt genau diese Stunden von Dukascopy und mischt sie in die vorhandene Tagesdatei.
Trockenlauf ist Standard, `--apply` schreibt. Protokoll je Lauf nach
`algo/results/fill_dukascopy.json` (welcher Tag, welche Stunden, wie viele Kerzen).

**Warum:** histdata.com hat im Block **Februar bis Juli 2023** einen echten Datenverlust -- an
fast allen Handelstagen fehlen ganze Stunden im Wechsel, bei allen 10 Paaren an denselben Tagen
(EURUSD 2023-04-13: die NY-Stunden 6, 8, 10, 12, 14, 16, 18 sind leer). Maerz bis Juni sind zu
100 % betroffen, Juli zu 95 %, Februar zu 35 %; jedes andere Jahr liegt bei ≤4 %. Das ist kein
Importfehler: der **Tick**-Monatschunk derselben Quelle traegt exakt dieselben leeren Stunden,
und M1-Monatschunks gibt es fuer vergangene Jahre nicht -- aus histdata ist der Block nicht
heilbar. Fuer fensterbasierte Auswertungen ist das gravierender als ein Zeitversatz: fehlt die
NY-Stunde 10 ganz, ist jede Aussage ueber die NY-Killzone dieses Tages leer.

**Wie -- geprueft, nicht angenommen:** Auf Stunden, die in beiden Quellen vorliegen, stimmen
Dukascopy-**Bid**-Kerzen mit dem histdata-Bestand **bitgenau** ueberein (EURUSD 2023-04-13 09h NY
und USDJPY 2023-06-15 13h NY: 60 von 60 Minuten, max |Delta| = 0.000000 auf OHLC, identische
Zeitstempel). Deshalb bleibt der Bestand durch das Fuellen homogen. Bewusst **Bid**, nicht die
Mid-Aggregation aus `fetch_dukascopy.py` (die dient dem IBKR-Abgleich) -- Mid waere hier ein
halber Spread Bruch mitten in der Zeitreihe. Bestehende Kerzen werden nie ueberschrieben, nur
tatsaechlich leere Minuten gefuellt; Kollisionen werden gezaehlt und gemeldet.

**Bekannte Grenzen:**
- **Reihenfolge ist zwingend:** `repair_dst_2019.py --apply` muss vorher gelaufen sein, sonst
  verschiebt die DST-Reparatur die frisch gefuellten (bereits korrekten) Kerzen hinterher um
  +1h mit. Das Skript prueft das selbst am Freitagsschluss-Marker und bricht ab.
- Dukascopy rate-limitet (429). `--pause` steuert den Abstand; der Bulk ueber Feb-Jul 2023 x 10
  Paare laeuft mehrere Stunden.
- Der Vermerk "Dukascopy ist per IP gesperrt" aus der `fetch_dukascopy.py`-Zeit stimmt nicht
  mehr -- 503 und Timeouts sind Rate-Limitierung, nach Wiederholung liefert der Endpoint.
- Nach `--apply` zwingend `python algo/build_parquet.py`.

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

## FVG-/VII-Grenzen (`analyze_ohlc.fvgs`, `analyze_ohlc.viis`)

**Was:** Die Aussenkanten eines FVG kommen aus der **VII** (Koerperluecke zwischen zwei
Nachbarkerzen), falls eine vorliegt, sonst aus dem Wick. Siehe
`wiki/concepts/Fair Value Gap (FVG).md`.

**Wo:** Beide Funktionen bestimmen die Koerperkante ueber `max(o,c)` / `min(o,c)`, nie ueber ein
festes Feld. Bullish: `lo = max(o₁,c₁)` falls `min(o₂,c₂)` darueber liegt, sonst `high₁`;
`hi = min(o₃,c₃)` falls es ueber `max(o₂,c₂)` liegt, sonst `low₃`. Bearish gespiegelt.

**Warum (Bugfix 2026-08-13):** Vorher standen dort `a.c` / `m.o` / `m.c` / `c.o` fest verdrahtet
-- korrekt nur, solange jede der drei Kerzen in Richtung des Moves schliesst. Bei einer
**Gegenkerze** tauschen Open und Close die Rollen: die Grenze landete mitten im Kerzenkoerper und
das VII-Kriterium meldete eine Luecke, die der Koerper selbst schon gehandelt hatte. Gemessene
Auswirkung am 13.08.2026: 1m-FVG 12:26 um 4,5 Punkte zu hoch (30.184,50 statt 30.180,00), 5m-FVG
12:05 um 22 Punkte zu gross und als "unberuehrt" statt "gefuellt 12:15" gemeldet.

**Regressionstest:** `python tools/test_fvg_vii.py` -- enthaelt zwei Faelle aus Jannes' eigenen
TradingView-Boxen (13.08.2026 00:01-00:03 und 12:24-12:26), die genau die Gegenkerzen-Faelle
abdecken.

## FVG-Einstufung stark/normal (`analyze_ohlc._grade`)

**Was:** Jedes FVG traegt zusaetzlich `strong` (bool), `broke` (`close`/`wick`/`None`), `swing`
(gebrochenes Level) und `ms` (`MSS`/`BOS`). Nutzerregel vom 13.08.2026: nur ein FVG, dessen
Displacement einen Swing High/Low **schliesst**, ist eine High-Probability-Bedingung.

**Wo:** Laeuft automatisch am Ende von `fvgs()` -- kein separater Aufruf, damit kein Aufrufer die
Einordnung vergessen kann. Reuse: `swings()` fuer die Level, `structure_breaks()` fuer MSS/BOS.

**Zwei Fallstricke, die drin sind:**
1. **Kein Lookahead** -- nur Swings, die `n` Kerzen vor Kerze 1 des FVG bestaetigt waren.
2. **Nur intakte Swings** -- ein bereits per Close genommenes Level faellt raus, sonst gilt in
   einem Trend jedes Folge-FVG als "stark" gegen dasselbe, laengst gebrochene Level.

**Zeitstempel:** `t` ist die **mittlere** (Displacement-)Kerze, dazu `t_start`/`t_end` fuer die
Drei-Kerzen-Spanne. Vorher wurde in Auswertungen teils auf die dritte Kerze umgerechnet -- das
verschiebt jede Box im Chart um eine Kerze und laesst am Fensterrand FVGs verschwinden.

## `backtest_fvg_strength.py` -- was macht ein FVG wirklich stark?

**Was:** Prueft die vier Nutzerthesen vom 13.08.2026 (Groesse haengt an Session/Vola;
Swing-Break; gross + MSS = High Probability; Confluence mit Higher-TF-Qs bzw. NDOG/NWOG) ueber
alle MNQ-1m-Tage. Ergebnisseite: `wiki/synthesis/FVG-Stärke, Session-Volatilität & Confluence
(laufend).md`, Rohwerte `algo/results/fvg_strength.json`.

**Wie:** Limit-Entry am C.E., Stop an der fernen Kante, Ziel 2R, 1 Kontrakt, P&L in echten
Dollar ueber `pnl.POINT_VALUE` **abzueglich `COMMISSION_RT` (1,24 $ Round Turn)**. Der Posten
entscheidet mit: Gruppe "normal" faellt dadurch von 1,26 auf 0,02 $ je Trade. Slippage ist
bewusst mit 0 modelliert (Limit-Entry) -- Stop-Slippage fehlt und macht die Zahlen weiter
optimistisch. `size_rel = FVG-Groesse / Median-Range der 30 Kerzen davor` ist der
sessionunabhaengige Groessenmassstab -- absolute Punkte sind wertlos, weil eine 1m-Kerze um
9:35 fast dreimal so gross ist wie um 4:00.

**Bekannte Grenze (wichtig):** `dubious_pct` -- Stop und Ziel in derselben 1m-Kerze -- liegt bei
kleinen FVG bei 56 %, bei grossen bei 27 %. Die konservative Wertung als Verlust ist korrekt,
macht aber den Vergleich klein/gross unfair: rechnet man die strittigen Faelle raus, dreht die
Rangfolge. Nur Gruppen mit **aehnlicher dubious-Quote** duerfen gegeneinander gelesen werden.
Sauber aufloesen laesst sich das erst mit Ausfuehrungsdaten feiner als 1m (IBKR, Roadmap 4).

## OHLC-Nulltoleranz-Gate (`analyze_ohlc.pruefe_kerzen`, `pruefe_gegen_referenz`)

**Was.** Ein Pflicht-Check vor **jedem** Schreibvorgang nach `raw/marktdaten/`. Alle sechs
Schreibpfade laufen hindurch: `fetch_yfinance.write_day`, `ingest_tvexport.schreib` (das auch
`backfill_yfinance.py` mitbenutzt), `resample_1m.schreib`, `ingest_histdata_xlsx.schreibe_tage`,
`fetch_dukascopy.schreibe_tag`.

**Wie.** Zwei Schaerfegrade:

| Grad | Prueft | Reaktion |
|---|---|---|
| hart (`OHLCDefekt`) | High < Low, **Open** ausserhalb High/Low, NaN, doppelte oder fallende Zeitstempel, leerer Datensatz, Haeufung degenerierter Bars **bei Tagesaufloesung** | Exception, **Datei entsteht gar nicht erst** |
| weich (Rueckgabeliste) | **Close** ausserhalb High/Low, Haeufung degenerierter Bars **intraday**, Preis nicht auf dem Tick-Raster | wird gedruckt, blockiert nicht |

Die Trennung hart/weich ist **gemessen, nicht geraten** (Gegenpruefung 2026-08-13 gegen alle
101 583 Bestandsdateien — die erste Fassung des Gates haette 2 055 davon abgelehnt und damit jeden
kuenftigen Forex-Import blockiert):

- **Close ausserhalb High/Low ist real**, nicht defekt: 1 749 von 84 044 Daily-Bars im Bestand
  (2,1 %), ueber alle Symbole ausser MNQ. Der Close kommt als Settlement bzw. aus einem anderen
  Session-Fenster als High/Low. **Open** ausserhalb ist dagegen ein echter Defekt — der Open ist der
  erste gehandelte Preis der Kerze; betroffen sind 281 Bars (0,33 %), MNQ mit **0**.
- **Degenerierte Bars sind intraday real**: AUDUSD 5m hat 36 % davon, weil Yahoo dort faktisch nur
  jede zweite Minute einen Tick liefert. Ueber 23 Handelsstunden (1d) ist derselbe Bar dagegen
  praktisch unmoeglich — deshalb greift die Haeufungsregel hart nur bei Tagesaufloesung, erkannt am
  Median-Kerzenabstand (`DAILY_SEKUNDEN`), nicht am Dateinamen.

Die Haeufungs-Schwelle ist bewusst kein Einzelkerzen-Verbot: eine einzelne Kerze mit
`open==high & low==close` ist auf 1m legitim (monotone Bewegung ohne Gegenbewegung). Erst die
Haeufung ueber einen Datensatz ist ein Feed-Defekt. Gemessener Realfall: 71 von 290 Daily-Bars.

**Warum.** Anlass ist der Tiefhistorie-Lauf vom 31.07./03.08.2026, der 71 degenerierte Daily-Bars
ins Depot schrieb, die erst am 13.08. auffielen (siehe `PLAN.md`). Auf solchen Bars ist jede
Wick-/Quadranten-Analyse rechnerisch 0 Punkte breit — der Fehler ist still und faellt in keiner
Auswertung als Fehler auf, sondern nur als unplausibles Ergebnis.

**Bekannte Grenze — und warum es die zweite Funktion gibt.** `pruefe_kerzen` findet **keinen**
Datums- oder Zeitzonen-Offset: verschobene Bars sind in sich stimmig, nur falsch einsortiert.
Genau das lag im Realfall zusaetzlich vor (+1 Tag). Dagegen hilft nur die Gegenpruefung gegen eine
unabhaengige Quelle — `pruefe_gegen_referenz(eigen, referenz)`, beides `{ts: (o,h,l,c)}`.

⚠️ Diese vergleicht **nur Open/High/Low, nie den Close**. Der Close weicht zwischen Feeds
systematisch ab (Settlement vs. letzter Trade). Ein Vergleich inklusive Close meldete am
13.08.2026 faelschlich "0 Treffer" und fuehrte zu der falschen Schlussfolgerung, die Daten seien
voellig andere Preise — tatsaechlich waren O/H/L identisch und nur um einen Tag verschoben.

**Regressionstest.** `analyze_ohlc.demo_pruefe_kerzen()`, eingehaengt in `selfcheck.py`
(`ohlc_gate`). Prueft beide Richtungen: dass echte Defekte gefangen werden **und** dass gesunde
Daten sowie einzelne legitime degenerierte Kerzen keinen Fehlalarm ausloesen.

## FVG-Wissen in den bestehenden Modulen (Stand 2026-08-13)

Das neue FVG-Wissen sitzt an **einer** Stelle -- `analyze_ohlc.fvgs()` liefert `strong`,
`broke`, `swing`, `ms`, `size_rel`, `t_start`/`t_end` automatisch mit. Alle Aufrufer bekommen
das ohne eigene Rechnung; niemand kann die Einordnung vergessen.

- **`rules.py::plan_trade`** -- neue Parameter `require_strong` / `min_size_rel`.
  **Default AUS**, weil sie das Silver-Bullet-Setup messbar verschlechtern (16 Trades/+2.194 $
  gegen 10-13 Trades/-6.281 bis -9.790 $). Begruendung und Zahlen im Docstring. Nebenbei
  sauberer geworden: der Fensterschnitt laeuft jetzt ueber `t_start >= win_start` statt ueber
  einen harten Slice, dazu `CONTEXT_BARS = 60` Vorlaufkerzen -- ohne die liefert `size_rel`
  fuer das erste FVG im Fenster `None`. Der Umbau ist ergebniserhaltend (Baseline exakt
  reproduziert).
- **`backtest_macro.py`** -- `MIN_FVG_PTS = 2.0` (absolut) ersetzt durch `MIN_FVG_REL = 0.45`
  (Vielfaches der lokalen Kerzenrange). Die absolute Schwelle war hier ein *Messfehler*: sie
  liess in den NY-Bloecken fast alles durch und sortierte in Asia/London aus -- also genau
  entlang der Achse, die der Test vergleicht. FVGs werden jetzt einmal pro Tag berechnet statt
  69x je Block. Befund bleibt: FVGs haeufen sich in den Macro-Fenstern (p=0,0087).
- **`analyze_ohlc.day_report`** -- FVG-Tabelle sortiert **High Probability zuerst** (stark vor
  gross), neue Spalten "x Kerze" (`size_rel`) und "Stark" (inkl. MSS/BOS). "Gross" misst sich
  an der lokalen Kerzenrange statt am Tagesmedian.
- **`live_status.py`** -- gibt die neuen Felder ohne Codeaenderung im JSON weiter.
- **`backtest_fvg_strength.py`** -- nutzt `size_rel` aus dem Detektor statt einer eigenen
  Kopie der Volatilitaetsrechnung.

## Liquiditaets-Wissen in `rules.py` + `liquidity_report.py` (2026-08-14)

Aus einer Chat-Session ("Liquiditaeten definieren/erkennen") kodiert, `rules.py` bekam vier
reine Funktionen (jeweils mit `demo()`-Asserts):

- **`session_extrema(bars, day)`** -- echtes Session-High/Low (Asia/London/NY, ueber
  `analyze_ohlc.session_windows`) + Midnight Open. **Nicht** dasselbe wie `swings()`/
  `untouched_levels()`: ein Session-Extrem ist nicht zwingend ein fraktaler Swing-Punkt
  (braucht `n` Nachbarn auf beiden Seiten) und kann dort durchrutschen -- genau das ist am
  2026-08-14 passiert (Asia-Low fehlerhaft als 30128 statt 30124,25 gemeldet).
- **`ipda_windows(daily_bars, last_price)`** -- High/Low je 20/40/60-Tage-Fenster (siehe
  wiki/concepts/IPDA Data Ranges.md) + `active` (vereinfachte Erweiterungsregel: 20 Tage
  bleibt aktiv, bis `last_price` das 20-Tage-Low/-High reisst, dann 40, dann 60 -- deckt nicht
  die volle ICT-Nuance "nur erweitern, wenn kein neues Lower Low im 40-Tage-Abschnitt" ab,
  bewusst vereinfacht).
- **`rel_pair(left, right, side)`** -- Nutzerregel: bei zwei nahen REH/REL-Extremen zaehlt nur
  das LINKE (zeitlich frueher) als noch unberuehrt, und nur wenn es weiter aussen liegt als
  das rechte (REH: links hoeher, REL: links tiefer) -- sonst hat das rechte es bereits
  genommen.
- **`daily_hilo_from_bars`/`prev_day_level`/`prev_week_level`** -- PDH/PDL/PWH/PWL aus
  INTRADAY-Bars (z.B. 5m) statt aus den 1d-Dateien aggregiert. ⚠️ Bewusste Entscheidung, kein
  Stilbruch: mehrere 1d-Dateien liefen ihrer eigenen Intraday-Historie davon (13.08. nach
  einer TradingView-Korrektur, die nur die Intraday-Dateien traf; 19.06. mit Werten des
  naechsten Handelstags dupliziert -- siehe PLAN.md-Log 2026-08-14). Aus `backtest_
  sb_session_liq.py` hierher verschoben (dort vorher lokal definiert, jetzt importiert) --
  mit der korrigierten Quelle sank das gemessene PWH/PWL-Ergebnis von +34,35 $/Trade
  (Artefakt, siehe unten) auf -1,27 $/Trade.

**`liquidity_report.py`** (neu) -- CLI wie `live_status.py`, `python algo/liquidity_report.py
MNQ`: zieht frische 1m/5m/15m-Daten (`live_status.fetch_today`, kein doppelter Fetch-Code),
kombiniert sie mit lokaler Historie aus `raw/marktdaten/`, erkennt unberuehrte Level je
Timeframe (`untouched_levels` + `rel_pair`-Aufloesung) und ordnet sie qualitativ (Hoch/
Mittel/Niedrig + Begruendung -- bewusst kein numerischer Score, Nutzerentscheidung). Deckelt
auf ±5 % Preisdistanz und die Top 20 Zeilen, sonst fluten alte, seit einem Trend nie wieder
besuchte Level die Liste. ⚠️ **Bekannte Grenze (v1, wird erweitert)**: derselbe Pool taucht oft
auf 1m/5m/15m als separate Zeile auf statt zusammengefasst -- noch keine Cross-Timeframe-
Deduplizierung.

**PDH/PDL/PWH/PWL-Backtest neu gelaufen** (`backtest_sb_session_liq.py`, korrigierte Quelle):
Baseline 110 Trades/17,3 % Win/+4,62 $/Trade; PDH/PDL 71/2,8 %/-14,23 $ (weiter klar negativ);
PWH/PWL 69/1,4 %/-1,27 $ (vorher +34,35 $ -- der alte Wert war ein Artefakt aus der stale
1d-Datei plus dem bekannten Fehlen eines Haltedauer-Caps, siehe PLAN.md-Backlog).

## `build_parquet.py` -- Parquet-Cache fuer Forex

**Was:** Baut aus `raw/marktdaten-tief/` (histdata.com-M1-Bid-Bars, siehe `fetch_histdata.py`/
`ingest_histdata_xlsx.py`) einen Parquet-Cache je Forex-Paar -- die Grundlage, auf der
`marktdaten.py::bars()` fuer Forex aufsetzt (siehe unten). Ausgangslage waren 73.100
Einzel-Tagesdateien (CSV) ueber 10 Paare; das direkte Einlesen davon fuer jeden Backtest-Lauf
waere sowohl langsam als auch der falsche Layer fuer Resampling auf groebere Timeframes.
**Wie:** Ein Lauf pro Symbol, liest alle Tagesdateien des Paares, dedupliziert exakte wie
widerspruechliche Zeitstempel-Duplikate (siehe `fetch_histdata.py`-Befund zum juengsten
Datenrand) und schreibt einen zusammenhaengenden Parquet-Frame. **Fix waehrend des Baus:**
Dedup sortierte urspruenglich mit dem pandas-Default (Quicksort) -- bei mehreren Zeilen mit
identischem Zeitstempel (die im Bestand real vorkommen, siehe oben) ist die Reihenfolge dabei
nicht deterministisch, welche Zeile am Ende gewinnt. Umgestellt auf einen stabilen Mergesort
(`kind="mergesort"`), damit derselbe Lauf immer denselben Cache erzeugt.
**Warum:** Ein einziger Parquet-Frame pro Symbol ist um Groessenordnungen schneller zu laden als
tausende CSV-Dateien und ist die Voraussetzung fuer die numpy-vektorisierte Bar-Konstruktion in
`marktdaten.py` (siehe dort).
**Ergebnis:** Gesamt-Cache-Groesse ueber alle 10 Paare ~894 MB.
**Bekannte Grenzen:** Cache ist ein abgeleitetes Artefakt, keine Quelle der Wahrheit -- bei
Aenderungen an `raw/marktdaten-tief/` (z.B. Nachzug des juengsten, noch instabilen Datenrands,
siehe `fetch_histdata.py`) muss er neu gebaut werden, es gibt noch keinen automatischen
Staleness-Check gegen den CSV-Bestand.

## `verify_forex_data.py` -- Drei-Ebenen-Gegenpruefung des Parquet-Caches

**Was:** Verbindliche Nulltoleranz-Pruefung (siehe CLAUDE.md, "Marktdaten wie Gold behandeln")
fuer den in `build_parquet.py` gebauten Forex-Cache, in drei getrennten Checks.
**Wie:**
- **Zeit-Kreuzprobe:** vergleicht den Cache gegen unabhaengige TradingView-1h-Exporte je Symbol.
  Die Stichprobe wird mit fester Schrittweite ueber den gesamten verfuegbaren Export-Zeitraum
  gezogen (Korrektur 2026-08-15: vorher die chronologisch ersten N Dateien, das deckte nur die
  Sommerzeit ab und liess einen DST-Ankerfehler in `marktdaten.py` unentdeckt -- jetzt sind
  EDT- *und* EST-Tage in jeder Stichprobe).
  **Ergebnis:** OK fuer alle 10 Symbole (~420-470 geprueften Stunden je Symbol, Tage von
  2024-08 bis 2026-07). Die Abweichungen liegen im erwarteten Bid-vs-Mid-Bereich, nicht bei
  null: EURUSD avg 0,00039 (≈3,9 Pips) / max 0,0023 (≈23 Pips), GBPUSD avg ≈1,7 / max ≈30 Pips,
  GBPJPY avg 0,0165 (≈1,6 Pips) / max 0,476 (≈48 Pips). Alle deutlich unter der
  Zeitversatz-Schwelle (0,005 bzw. 0,5 fuer JPY-Paare) -- ein echter 1h-Versatz wuerde eine
  ganze Kursbewegung ergeben, nicht ein paar Pips. Das bestaetigt die DST-bewusste
  Zeitkonvertierung aus `fetch_histdata.py` auch im vollen Bestand, nicht nur an den
  urspruenglich stichprobenartig geprueften Einzeltagen.
  (Eine frueher hier dokumentierte "maximale Abweichung <0,1 Pip" war um rund Faktor 100
  falsch -- die tatsaechlichen Werte standen schon damals in `algo/results/forex_verify_report.json`.)
- **Vollstaendigkeit:** prueft je Handelstag gegen die erwartete Kerzenzahl. **Bug im ersten
  Entwurf gefunden und gefixt:** der Check kannte keine Sonderregel fuer Freitags-17:00-NY-Schluss
  (Forex handelt bis 17:00 NY, nicht 24h) -- dadurch zaehlte *jeder* Freitag in 23 Jahren
  faelschlich als anomaler/luekenhafter Tag. Nach dem Fix fiel EURUSDs Flag-Zahl von 4016 auf
  3243; die verbleibenden Flags sind eine Mischung aus echten feiertagsverkuerzten Tagen und der
  duennen 2000-2011-Periode (siehe Attrappen-Quote unten).
  **Bekannte Luecke EURUSD (2000-2002):** EURUSD hat **540 fehlende Wochentage**, alle anderen
  neun Paare nur 11-22. Die Luecke liegt fast vollstaendig im Legacy-XLSX-Zeitraum 2000-2002
  (z.B. Jan-Mrz 2001 komplett ohne Daten); der Bestand springt von Dez 2000 direkt auf Jan 2003.
  Das fliesst **ungefiltert** in `algo/seasonal_tendency_EURUSD.json` ein, dessen `date_range`
  deshalb mit `2000-05-31` beginnt, obwohl der zusammenhaengende, saubere Bestand erst 2003
  anfaengt. Wer EURUSD-Statistiken ueber die volle Historie zieht, mischt damit eine echt
  lueckenhafte Fruehphase in den 2003+-Bulk -- fuer Vergleiche zwischen Jahren/Monaten
  entweder auf >=2003 einschraenken oder die kleineren `n` der Fruehjahre explizit mitlesen.
- **Stunden-Luecken** (neu 2026-08-15): zaehlt je Handelstag die erwarteten NY-Vollstunden, die
  **komplett leer** sind (`soll_stunden()`: Mo-Do 0-23, Fr 0-16, So 17-23), meldet ab vier
  leeren Stunden und verdichtet zusaetzlich nach Monat. **Warum als eigene Kennzahl:** der
  Feb-Jul-2023-Block (histdata-Quellenschaden, siehe `fill_luecken_dukascopy.py`) hat die
  Kerzenzahl-Pruefung oben zwar getroffen, aber nur als "kurzer Tag" -- dass zwoelf Stunden
  mitten in London- und NY-Session fehlen, war aus keiner Kennzahl ablesbar, und die 20er-Liste
  der auffaelligen Tage verbarg einen 5-Monats-Block. Fuer fensterbasierte Auswertungen ist
  genau das der toedliche Fall: fehlt die NY-Stunde 10 ganz, ist jede Aussage ueber die
  NY-Killzone dieses Tages leer. Regressionsfall im Selbstcheck (Symbol `LOCH`, nur gerade
  Stunden belegt, plus Negativkontrolle Feiertag).
- **Attrappen-Quote** (`open==high==low==close`): aggregiert ueber alle Jahre 1,4-6,7 % je Symbol
  (Spec-Erwartung war <1 %), aber **nicht gleichverteilt ueber die Zeit** -- Beispiel EURUSD je
  Jahr: 2000: 30,0 %, 2003: 11,8 %, 2005: 11,3 %, 2007: 14,7 %, 2008: 6,4 %, 2010: 5,7 %, 2012:
  0,45 %, 2015: 1,18 %, 2019: 0,88 %, 2022: 1,22 %, 2025: 0,97 %. Fruehe Jahre sind duenn
  gehandelt, ab ca. 2012 liegt die Quote durchgehend unter 1,5 %.

  Nachvollziehbar per direkter Abfrage gegen den Cache (nicht Teil von `verify_forex_data.py`,
  das nur Aggregate persistiert):

  ```python
  import pandas as pd
  df = pd.read_parquet('algo/cache/EURUSD_1m.parquet')
  idx = pd.to_datetime(df['time'], unit='s', utc=True).dt.tz_convert('America/New_York')
  df = df.set_index(idx)
  df['jahr'] = df.index.year
  flach = (df['open']==df['high']) & (df['low']==df['close']) & (df['open']==df['low'])
  by_year = flach.groupby(df['jahr']).mean()
  ```
**Warum:** Eine einzelne Aggregatzahl ("6,7 % Attrappen") haette die Entscheidung "ganze
2000-2011-Periode verwerfen" nahegelegt -- die Jahresaufschluesselung zeigt, dass das ein
Frueh-Historie-Phaenomen ist, kein durchgehender Datenfehler.
**Nutzerentscheidung (explizit):** alle Jahre 2000-2026 bleiben im Datensatz, **keine**
Filterung/Ausschluss der duennen 2000-2011-Periode. Stattdessen als bekannte Grenze dokumentiert:
praezisionskritische Arbeit auf 2000-2011-Daten muss die duennere Liquiditaet/hoehere
Attrappen-Dichte dieser Periode beruecksichtigen.
**Bekannte Grenzen:** Die Zeit-Kreuzprobe deckt nur Stunden ab, in denen TradingView-1h-Exporte
vorliegen -- keine Minute-fuer-Minute-Verifikation des gesamten 23-Jahre-Bestands. Die
Attrappen-Quote misst nur `open==high==low==close`, keine sonstigen Feed-Artefakte.

## `marktdaten.py` -- Symbol-agnostischer Bar-Loader (Forex + Futures)

**Was:** `bars(symbol, tf, von, bis)` ist der neue, einheitliche Einstiegspunkt fuer
Kursdaten-Ladung -- ersetzt den direkten CSV-Zugriff in Backtest-Skripten fuer Forex-Symbole,
bleibt fuer Futures unveraendert.
**Wie:** Dispatcht nach Symbol: Forex-Paare laufen ueber den Parquet-Cache aus `build_parquet.py`
(aus 1m resampled auf den angeforderten Timeframe, Session-Tage NY-Mitternacht-verankert statt
Kalendertag-verankert); Futures-Symbole laufen unveraendert ueber den bestehenden
`raw/marktdaten/`-CSV-Pfad.
**Performance-Fix:** die erste Fassung baute die `Bar`-Liste per `df.iterrows()` -- fuer einen
vollen 23-Jahre/8,5-Mio-Zeilen-Symbol-Load dauerte das 600+ Sekunden (Timeout, kein nutzbares
Ergebnis). Umgebaut auf numpy-Array-Vektorisierung (Spalten einmal als numpy-Arrays extrahieren,
`Bar`-Objekte per Listcomprehension ueber Indizes statt per Pandas-Zeilen-Iteration bauen) --
jetzt ~12,5 s fuer dieselbe volle 1m-Historie.
**Warum:** `backtest_common.py::load_rows()` und die Gruppe-A/B-Module brauchen einen Loader, der
Forex und Futures gleich behandelt, ohne dass jedes Skript selbst zwischen CSV- und
Parquet-Pfad unterscheiden muss.
**Bekannte Grenzen:** Nur Gruppe-A/B-Module (`backtest_seasonal.py`,
`backtest_midnight_range_std.py`) sind bislang tatsaechlich umgestellt (siehe `algo/PLAN.md`-
Backlog fuer die restlichen acht). Gruppe-C-Module (ORG/NDOG-abhaengig) bleiben MNQ-only, siehe
`SESSION_TYP`-Guard in `tools/analyze_ohlc.py`.

## `measure_forex_attrappen.py` -- Attrappen-Loeschvorschlag fuer `raw/marktdaten/`

**Was:** Misst die **alten** yfinance-Forex-Dateien in `raw/marktdaten/` (nicht den neuen
histdata-Cache in `raw/marktdaten-tief/`) auf ihre Attrappen-Quote (`open==high==low==close`),
je Datei -- reiner Messschritt, keine Loeschung.
**Wie:** Prueft laut Spec §8.3 bewusst nur 1m/5m/15m-Dateien (1h/4h/1d werden bewusst
ausgenommen/erhalten -- gröbere Timeframes sind seltener degenerierte Kerzen und werden
weiterhin fuer andere Zwecke gebraucht). 340 Dateien geprueft, **72 ueberschreiten die
90-%-Attrappen-Schwelle** und stehen auf der Loeschkandidaten-Liste.
**Warum:** Der alte yfinance-Forex-Bestand wird durch den neuen, deutlich laengeren und
gruendlicher verifizierten histdata-Cache (`build_parquet.py`) ersetzt -- Dateien mit einer derart
hohen Attrappen-Quote liefern praktisch kein echtes OHLC-Signal mehr und sind Kandidaten zum
Aufraeumen.
**Nichts geloescht:** die 72 Dateien bleiben vorerst liegen (Spec §8.4) -- Loeschung braucht eine
separate, ausdrueckliche Freigabe des Nutzers, ist explizit nicht Teil der automatisierten
Ausfuehrung dieses Plans.
**Bekannte Grenzen:** Die 90-%-Schwelle ist ein fester Cutoff, keine statistische Herleitung --
Dateien knapp darunter koennen ebenfalls stark degeneriert sein, wurden hier aber nicht als
Loeschkandidat gefuehrt.

## `bias_levels.py` -- Levels + News fuer die Bias-Vorlage

**Was.** Liefert als ein JSON alles, was `/bias-vorlage-daily` und `/bias-vorlage-weekly` zum
Vorbefuellen von `raw/journal/Daily Bias *.md` / `Weekly Bias KW*.md` brauchen: Wochen-Range,
Vortages-Range (H/L/C), das Zieldatum (naechster Handelstag bzw. kommender Montag) und die
Red-/Orange-Folder-News.

**Wie.** Ranges ueber `backtest_common.load_rows("MNQ")` -- kein eigenes CSV-Parsing.

News aus **zwei Quellen mit fester Rangfolge** (beide stdlib `urllib`, kein neues Paket):

1. **ForexFactory-JSON-Feed** `nfs.faireconomy.media/ff_calendar_thisweek.json` -- die
   Referenzquelle des Nutzers, wird immer zuerst gefragt.
2. **TradingView-Wirtschaftskalender** `economic-calendar.tradingview.com/events` als
   Fallback, sobald der angefragte Zeitraum ausserhalb der FF-Woche liegt. Nimmt beliebige
   `from`/`to`-Datumsbereiche und ist damit die einzige Quelle, die **freitags abends schon
   die kommende Woche** kennt -- genau das braucht der Weekly-Lauf.

`news["source"]` sagt in jeder Ausgabe, welche der beiden geantwortet hat; beim Fallback
steht zusaetzlich `news["hinweis"]` mit dem Grund. Die Commands geben beides in der
erzeugten Datei aus, damit nie unklar bleibt, woher eine Uhrzeit stammt.

**Warum kein Scraping.** `forexfactory.com/calendar` antwortet Bots mit **HTTP 403**
(Cloudflare, verifiziert 2026-08-15) -- der urspruengliche Plan
`docs/superpowers/plans/2026-08-13-bias-vorlage.md` sah dort WebFetch vor und haette nie
funktioniert. Der JSON-Feed ist der von ForexFactory selbst bereitgestellte Weg.

**Zeitpruefung (Zeit vor Preis).** FF liefert ISO-Timestamps mit NY-Offset (-04:00 EDT /
-05:00 EST), TradingView UTC (`...Z`); beide werden auf NY normalisiert, die DE-Zeit per
`zoneinfo` daraus abgeleitet -- keine manuelle Stundenrechnung. Zwei unabhaengige
Gegenproben am 2026-08-15:
- gegen die **Nutzernotiz**: `raw/journal/Daily Bias 2026-08-13.md` sagt "PPI News um 14.30
  DE Zeit also 8.30 Ny", der Feed sagt exakt dasselbe.
- **FF gegen TradingView** auf KW33: CPI 12.08. 08:30 NY und PPI 13.08. 08:30 NY bei beiden,
  Zeitstempel deckungsgleich.

**Bekannte Grenzen.**
- **Die beiden Quellen stufen Impact unterschiedlich ein.** TradingView fuehrt zusaetzlich
  Retail Sales, Existing Home Sales und Michigan Sentiment als Red, ForexFactory stuft sie
  als Orange ein. Wer die Bias-Datei neben seine ForexFactory-Seite legt, sieht bei einem
  TradingView-Lauf also mehr rote Zeilen -- die Uhrzeiten stimmen, die Farbe kann abweichen.
- ForexFactory kennt nur die *laufende* Woche; `ff_calendar_nextweek.json` gibt es nicht mehr
  (HTTP 404, geprueft 2026-08-15). Deshalb ueberhaupt der TradingView-Fallback.
- FF antwortet auf mehrere Abrufe kurz nacheinander mit **HTTP 429**. Dagegen ein
  15-Minuten-Dateicache im Systemtemp (`tempfile.gettempdir()/ff_calendar_thisweek.json`),
  bewusst nicht im Repo.
- TradingView wird nur mit `countries=US` gefragt (MNQ-Fokus) -- EUR/GBP/JPY-Termine tauchen
  im Fallback also nicht auf, im FF-Pfad dagegen schon.
- `next_trading_day()` kennt nur Sa/So, **keine Feiertage** -- an einem US-Feiertag zeigt die
  erzeugte Datei auf einen Tag ohne Handel.
- Jeder Abrufsfehler wird abgefangen und landet als Text in `news["error"]`; `news["events"]`
  bleibt immer eine Liste. Ein Fehlschlag darf den Bias-Lauf nie abbrechen.

**Selbstcheck.** `python algo/bias_levels.py --demo` (Ranges, Wochentagslogik, NY/DE-Umrechnung
in Sommer- und Winterzeit, Gleichheit von TradingViews UTC- und FFs NY-Timestamps,
Netzfehler-Pfad beider Quellen, Fallback-Umschaltung). Kein Netz-/Dateizugriff, laeuft in
`selfcheck.py` mit.

## `algo/forex/` -- Forex-Zwilling der Regel-, P&L- und Simulationsschicht (Phase 2, 2026-08-15)

**Was.** Eigenes Unterpaket mit `pnl.py`, `rules.py`, `backtest.py`, `selfcheck.py`. Setzt die
MNQ-Konzepte auf den 23-Jahres-Forex-Bestand um -- Nutzervorgabe: *"die genau gleichen Konzepte
nutzen, ausser bekannte Sachen die nur fuer Future sind"*. Spec:
`docs/superpowers/specs/2026-08-15-forex-algo-phase2-design.md`.

**Warum getrennt statt parametrisiert.** Nutzerentscheidung 2026-08-15: die MNQ-Module duerfen
sich nicht bewegen. `algo/pnl.py`, `algo/rules.py`, `algo/backtest_bt.py`, `algo/signals.py`,
`algo/backtest_ensemble.py`, `algo/stress_test.py`, `algo/masters.py`, `algo/live_status.py`
und `algo/selfcheck.py` sind unangetastet; nachgewiesen ueber den Diff gegen
`algo/results/mnq_baseline_2026-08-15.txt` (26/26 Selbstchecks, bitgleich).

**Geteilt, nicht kopiert:** `tools/analyze_ohlc.py` (Detektoren, KILLZONES, TICK_SIZE,
PIP_SIZE, SESSION_TYP, 9:30-Guard), `algo/marktdaten.py`, `algo/risk_killswitch.py`,
`algo/backtest_hp_fvg.py::bias_proxy`. Von `algo/validate.py` sind nur `monte_carlo()` und
`double_bootstrap_drawdown()` nutzbar -- `run()`/`walk_forward()` haengen an
`backtesting.Backtest` und damit an einer Strategy-Klasse, die es hier bewusst nicht gibt.

**Welche Konzepte laufen.** Silver Bullet (1st presented FVG *im Fenster*), FVG-Detektion inkl.
Staerke, Swings/MSS, HP-FVG, Liquiditaets-Level, IPDA-Fenster, Killzones, Midnight OR, Macros,
NWOG, 1 %-Risiko, Kill-Switch. **Ausgeschlossen** (setzen die 9:30-Eroeffnung als Ereignis
voraus): ORG, ORG C.E., ORG-Std-Extrema, 1p FVG Tag/Woche, 1p-Mindestgroesse, erstes FVG nach
9:30, Open Drive, NDOG, alle RTH-Varianten.

**Fenstersatz.** Die drei SB-Fenster (London 3-4, NY AM 10-11, NY PM 14-15) plus die vier
Killzones, jedes getrennt ausgewiesen. `KZ NY 7-9` und `KZ NY-Forex 7-10` stehen bewusst
NEBENeinander: `analyze_ohlc.KILLZONES` sagt 7-9, `wiki/concepts/ICT Daily Range Session
Timing.md` sagt fuer Forex 7-10 -- der Widerspruch wird gemessen statt aufgeloest.
`active_windows()` liefert deshalb ALLE zutreffenden Fenster, nicht den ersten Treffer.

**`forex/pnl.py` -- die drei Fallgruppen des Pip-Werts.** Der Pip-Wert haengt ausschliesslich
an der Quote-Waehrung, nie an der Basis; daraus folgt eine Regel statt einer
Paar-Fallunterscheidung: `pip_wert_quote = PIP_SIZE * 100.000`; Quote == USD -> fertig ($10);
sonst ueber `<QUOTE>USD` mal Kurs bzw. `USD<QUOTE>` durch Kurs. Der USD/XXX-Fall ist dabei kein
Sonderfall, sondern faellt mit sich selbst als Referenz in dieselbe Zeile. Fehlt der
Referenzkurs, gibt es `None` -- der Trade wird verworfen und gezaehlt, nie genaehert.
`round_to_lot()` rundet auf 0,01 Lot ab, nie auf, und normalisiert vorher gegen das
Float-Artefakt `5.0 / 0.01 = 499,99999999999994` (ein nacktes `floor` lieferte 4,99).

**Zwei P&L-Konventionen, bewusst getrennt benannt.** `brutto_usd()` rechnet ohne jede
Kostenannahme -- fuer Fuellpreise, die bereits auf der richtigen Marktseite liegen.
`real_pnl_usd()` geht von rohen Bid-Preisen aus und zieht den Spread einmal explizit ab. Wer
sie verwechselt, zaehlt den Spread doppelt oder gar nicht; deshalb stehen sie getrennt statt
implizit vermischt.

**`forex/backtest.py` -- eigener Bar-Walk statt `backtesting`-Lib.** Die Lib preist wie eine
Aktie; fuer Forex kaemen drei weitere Brueche dazu (zeitabhaengiger Pip-Wert, Ask/Bid-Trennung,
Lot-Granularitaet), die sich nur ueber Preis-Hacks nachbauen liessen, welche dann die
P&L-Rechnung der Lib verfaelschen. Fill-Konvention: jede Seite wird dort gefuellt, wo ein
Broker fuellen wuerde (Long kauft zum Ask, Short verkauft zum Bid) -- dadurch faellt der Spread
automatisch genau einmal an, und die Short-Stop-Asymmetrie ergibt sich von selbst statt als
Zuschlag. Positionen werden vor dem 17:00-Rollover glattgestellt, statt ein Swap-Modell zu
raten.

**Drei Pflichtangaben in jedem Report:** `dubious_pct`, Break-even-Spread (`--breakeven`,
numerisch per Bisektion, rechnet den Backtest ~12x) und die Flat-Quote des Fensters.

**Bekannte Grenzen.**
- **Spread ist gesetzt, nicht gemessen** (`SPREAD_PIPS`, Bid-only-Bestand). Deshalb ist der
  Break-even-Spread die belastbare Kennzahl, nicht der $-P&L.
- **1h und groeber sind fuer die SB-Fenster unbrauchbar:** ein Fenster ist eine Stunde, auf
  1h-Kerzen passt dort keine 3-Kerzen-Formation hinein (gemessen: 0 Trades).
- **`min_stop_pips` (Default 3,0) ist ein Forex-Zusatz ohne MNQ-Entsprechung.** Ohne ihn liegt
  die mediane Stop-Distanz bei 1,2 Pips, also unter dem Spread.
- Kein Ensemble, kein Stress-Test, kein Walk-Forward -- Schritte 7-9 der Spec, noch offen.

**Selbstcheck.** `python algo/forex/selfcheck.py` buendelt die drei Modul-Demos und den
**Drift-Waechter**: er hasht die normalisierten Rumpfe von `sb_entry_signal`, `plan_trade` und
`plan_trade_hp_fvg` in `algo/rules.py` und meldet, wenn das MNQ-Original sich bewegt hat. Er
verhindert die Drift nicht -- er macht sie sichtbar, was bei bewusst duplizierter Logik der
einzige ehrliche Umgang ist. Nach einer bewussten Uebernahme:
`python algo/forex/selfcheck.py --hashes` und die Wache aktualisieren.
