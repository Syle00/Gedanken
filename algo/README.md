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

## `selfcheck.py` -- Gebuendelter Regressions-Check

**Was:** Buendelt alle `demo()`/`_demo()`-Selbstchecks (`pnl`, `rules`, `signals`,
`backtest_ensemble`) zu einem Kommando.
**Wie:** `python algo/selfcheck.py` -- Sekunden, kein neuer Backtest-Lauf.
**Warum:** Schneller taeglicher Regressions-Baustein, damit ein kuenftiger Code-Fix nicht
unbemerkt einen der hier gefixten Bugs reproduziert. Ausloese-Mechanik (Erinnerung/Loop) ist
Teil von Teilprojekt B.

## Exploratorische Skripte (`backtest_daily_patterns.py`, `backtest_fred_events.py`,
`backtest_ndog.py`, `backtest_nwog.py`, `backtest_ohlc.py`, `backtest_org_ce.py`,
`backtest_seasonal.py`, `backtest_tgif.py`, `backtest_fvg_specialness.py`,
`backtest_midnight_range_std.py`, `backtest_midnight_range_judas.py`)

**Was:** Reine statistische Zaehl-/Korrelationsskripte (Wochentag-Effekt, Turn-of-Month,
NDOG/NWOG-Bias, TGIF, FVG-Besonderheiten, Midnight-Range-STD/Judas-Swing, FRED-Events) --
nutzen NICHT die `backtesting`-Engine (bestaetigt per Grep, 2026-08-06), daher betrifft sie der
Punktwert-Layer aus `pnl.py` nicht.
**Audit 2026-08-06:** Alle 11 Skripte bestehen die Lookahead-Checkliste (keine Funde). Doppelzaehlung in `backtest_seasonal.py::turn_of_month()` erkannt (ueberlappende `rs[:-1]`- und `nrs[3:]`-Slices), ist statistisches Problem kein Lookahead-Verstoß -- separat zu behandeln.

## Security-Scan

2026-08-06: keine hartkodierten Secrets in `algo/*.py` gefunden. `algo/.secrets.yaml`
(FRED-API-Key) ist korrekt gitignored und wurde nie committet. Naechster Scan: woechentlich
oder sobald eine echte IBKR-Broker-Anbindung (Live-Keys) dazukommt -- taeglich waere aktuell
unnoetiger Aufwand ohne Live-Handel.
