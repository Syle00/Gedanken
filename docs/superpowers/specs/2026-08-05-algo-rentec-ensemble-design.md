# RenTec-artige Ensemble-Strategie fuer MNQ — Design

Status: Design, genehmigt am 2026-08-05. Umsetzung folgt in 5 Phasen (siehe unten),
jede Phase ist ein eigener Implementierungsschritt.

## Ziel

`algo/rules.py::plan_trade` (Silver Bullet, ICT-Regel) ist bisher die einzige Handelsregel
im Projekt und zeigt auf allen bisherigen Backtests (`backtest_bt.py`, `backtest_walkforward.py`)
robust negative Erwartung (Profit Factor < 1 bei jedem getesteten Stop-Puffer, jedem
Walk-Forward-Fold). Ziel dieses Designs: eine zweite, RenTec/Simons-artige Strategie-Schicht,
die viele schwache statistische Einzelbefunde (bereits im Projekt gebacktestet: Montags-Effekt,
Turn-of-Month, Range-Autokorrelation, Stat-Arb-Korrelation zu ES=F, Makro-Regime aus FRED) zu
einem taeglichen Bias kombiniert, statt sich auf eine einzelne diskretionaere ICT-Regel zu
verlassen. Die bestehende Silver-Bullet-Regel wird dabei nicht ersetzt, sondern als
Intraday-Timing-Mechanismus wiederverwendet und durch den neuen Tages-Bias gefiltert.

Zusaetzlich: die bestehenden Validierungswerkzeuge (Walk-Forward, Monte-Carlo,
Parameter-Sensitivitaet aus `algo/backtest_walkforward.py`) werden von der einen Strategie
geloest und wiederverwendbar gemacht; ein Stress-Test gegen historische Krisenperioden
(2008, Covid, Flash-Crashes) kommt dazu; ein Live-Dashboard macht den Backtest-Ablauf
in einem Python-Fenster sichtbar statt nur als Text-Report.

## Phase 1 — Signal-Schicht (`algo/signals.py`)

Reine Funktionen `signal_x(history) -> float | None`, grob skaliert auf `[-1, +1]`
(bearish...bullish), `None` wenn nicht berechenbar. Kein Lookahead: nur Daten bis
zum Vortag. Extrahiert bestehende Logik, keine Neuimplementierung:

| Signal | Beleg im Projekt | Quelle |
|---|---|---|
| Wochentag-Bias | Montag n=147, +0,71% Ø-Rendite | `backtest_seasonal.py` |
| Turn-of-Month | TOM-Fenster +0,341%/64,3% bullish vs. Rest +0,070%/52,5% | `backtest_seasonal.py` |
| Range-Autokorrelation | r=0,305 (n=146), Volatility Clustering | `backtest_daily_patterns.py` |
| Richtungs-Autokorrelation | 58,8% bullish nach bullishem Tag (n=80) | `backtest_daily_patterns.py` |
| Stat-Arb-Spread MNQ/ES=F | neu: Z-Score der relativen Tagesrendite | neu, braucht ES=F-Daten |
| VIX-Regime | Terzil-Level + Tagesaenderung | `backtest_fred_events.py` |
| DGS10-Aenderung | Korrelation zu Tagesrendite | `backtest_fred_events.py` |
| WALCL-Trend | Fed-Bilanz wachsend/schrumpfend -> Wochenrendite | `backtest_fred_events.py` |

`build_features(days) -> (X, y)`: eine Zeile pro Handelstag, Spalten = obige 8 Signale,
Label `y` = Richtung des **naechsten** Tages. Fehlende Signalwerte werden als `0` (neutral)
imputiert, nicht als Zeile verworfen (bei ~150 Tagen Historie ist jede Zeile relevant).

Intraday-Timing-Signale (Silver-Bullet-FVG aus `rules.py::plan_trade`) bleiben unveraendert
und sind nicht Teil der Regression — sie werden erst in Phase 2 als Entry-Mechanik genutzt.

**Test:** `demo()`-Selbstcheck pro Signalfunktion mit synthetischen Tagesreihen (bekannte
Eingabe -> erwarteter Wert), wie bei `rules.py::demo()`.

## Phase 2 — Ensemble-Strategie (`algo/backtest_ensemble.py`)

**Modell:** `sklearn.linear_model.LogisticRegression(class_weight="balanced")`,
L2-Regularisierung als Schutz gegen Overfitting bei ~150 Datenpunkten und 8 Features —
Docstring vermerkt das explizit als Groessenordnungs-Schaetzung, keine belastbare Aussage
(gleicher Vorbehalt wie bei allen bisherigen kleinen Stichproben im Projekt).

**Ablauf pro Handelstag `d`:**
1. `X = build_features(history_bis_d-1)` -> `model.predict_proba(X)` -> `p_bullish`.
2. Bias: `long` wenn `p_bullish > 0.55`, `short` wenn `< 0.45`, sonst `neutral`
   (Totzone gegen Rauschen um 50%, kein Trade bei `neutral`).
3. `plan_trade()` laeuft wie bisher (Silver-Bullet-Fenster, FVG-Trigger) — der Trade wird
   nur genommen, wenn `setup.side` mit dem Tages-Bias uebereinstimmt. Das ist der konkrete
   Test: filtert der Tages-Bias die bekannt schwache Silver-Bullet-Regel zu positiver
   Erwartung heraus, oder nicht?

**Modell-Fit im Walk-Forward:** kein statischer Fit auf allen Daten (Lookahead-Bias).
Das Modell wird pro Fold neu gefittet: In-Sample-Fold -> Fit -> Out-of-Sample-Fold ->
Predict, kein Refit — dasselbe Muster wie die bestehende `stop_buffer_pct`-Grid-Search,
nur dass hier Modellgewichte statt eines Skalarparameters optimiert werden (siehe Phase 3).

`EnsembleStrategy` bekommt einen `intraday: bool`-Schalter (Default `True`): bei `False`
(fuer Stress-Test-Perioden ohne Intraday-Daten, siehe Phase 4) entfaellt Schritt 3,
stattdessen Entry am Tages-Open in Bias-Richtung, Exit am Tages-Close.

**Test:** synthetischer Fall wie `rules.py::demo()` — Bias stimmt mit Silver-Bullet-Richtung
ueberein -> Trade; stimmt nicht ueberein -> kein Trade.

## Phase 3 — Validierung generalisieren (`algo/validate.py`)

Die drei bestehenden Funktionen aus `backtest_walkforward.py` verlieren ihre Kopplung an
`SilverBulletStrategy`/`stop_buffer_pct`:

```python
def parameter_sensitivity(df, strategy_cls, param_name, candidates, bt_kwargs): ...
def walk_forward(df, strategy_cls, param_name, candidates, bt_kwargs, n_folds=6,
                  on_fold_train=None): ...
def monte_carlo(baseline_stats, n_sims=1000, seed=42): ...
```

`on_fold_train(train_df) -> dict` ist ein optionaler Hook, der vor jedem Fold aufgerufen
wird. Fuer `EnsembleStrategy` fittet er dort das Modell und liefert es als
Strategie-Klassenattribut zurueck (Model-Fit statt Grid-Search-Parameter). Fuer
`SilverBulletStrategy` bleibt der Hook leer — Verhalten unveraendert.

`algo/backtest_walkforward.py` wird zum duennen Wrapper: importiert `validate.py`, ruft es
mit `SilverBulletStrategy` + `stop_buffer_pct`-Grid auf. Ein neues, ebenso duennes
`algo/validate_ensemble.py` ruft dasselbe `validate.py` mit `EnsembleStrategy` +
Model-Fit-Hook auf.

**Test:** Regressionscheck — Aufruf mit `SilverBulletStrategy` + `stop_buffer_pct`-Grid
muss dieselben Zahlen liefern wie der bisherige `backtest_walkforward.py` (stellt sicher,
dass die Generalisierung das bestehende Verhalten nicht veraendert).

## Phase 4 — Stress-Test (`algo/stress_test.py`)

**Daten:** `algo/fetch_yfinance.py` wird generalisiert (`SYMBOL`-Konstante wird
`--symbol`-CLI-Argument, Dateiname-Praefix folgt dem Symbol statt hart "MNQ") und fuer
`NQ=F` (Preis-Proxy, Historie bis ~1999/2000 bei yfinance) sowie `ES=F` (Stat-Arb-Partner,
siehe Phase 1) auf folgenden Fenstern ausgefuehrt (Tagesaufloesung, `1d` hat kein
yfinance-Lookback-Limit):

| Fenster | Zeitraum | Krisentyp |
|---|---|---|
| 2008-Crash | 2008-09-01 – 2009-03-31 | Kredit-/Bankenkrise |
| Covid-Crash | 2020-02-15 – 2020-04-15 | Pandemie-Schock |
| Flash-Crash 2010 | 2010-05-01 – 2010-05-13 | Mikrostruktur-Flash-Crash |
| China-Deval/Black-Monday | 2015-08-18 – 2015-08-26 | Externer Schock |
| Volmageddon | 2018-02-02 – 2018-02-09 | Vol-Produkt-Blowup |

**Einschraenkung:** Intraday-Daten (5m/1m) reichen bei yfinance nicht so weit zurueck —
fuer alle fuenf Fenster existieren nur Tages-Bars. Die Intraday-Timing-Signale
(Silver-Bullet-FVG-Entry) koennen fuer diese Perioden nicht laufen. Deshalb laeuft
`stress_test.py` durchgehend mit `EnsembleStrategy(intraday=False)` (siehe Phase 2) — ein
reiner Tages-Bias-Test, sauber gekennzeichnet statt stillschweigend ungenau.

**Output:** Report analog zu den bestehenden Backtests (Drawdown-Tiefe, Erholungsdauer,
Trades waehrend/nach dem Crash) — explizit als **Verhaltens-Kennzahlen auf einem
Preis-Proxy**, keine echte MNQ-$-P&L (gleicher Vorbehalt wie bei `backtest_bt.py` zur
`backtesting`-Lib-Preisung, MNQ existiert als Instrument erst seit 2019).

**Test:** Smoke-Test gegen ein kleines Fenster (laeuft durch, ohne Crash).

## Phase 5 — Live-Dashboard (`algo/dashboard.py`)

**Architektur-Entscheidung:** die `backtesting`-Lib hat keinen Per-Bar-Callback-Hook fuer
Live-Rendering. Das Dashboard laeuft deshalb eine eigene, einfache Simulationsschleife
(dieselben Funktionen — `plan_trade`, Signale, Modell — aber ohne die `backtesting`-Bibliothek),
rein zum Zusehen. Die offiziellen Kennzahlen (Profit Factor, Sharpe, Walk-Forward-Ergebnisse)
kommen weiterhin aus `validate.py`/`backtest_ensemble.py` — das Dashboard ist Anschauung,
nicht die Quelle der Wahrheit fuer Zahlen. Steht so im Docstring.

**Fenster:** `matplotlib.animation.FuncAnimation`, 4 Panels:
1. Preis-Chart mit Entry/Exit-Markern (long=gruenes Dreieck, short=rotes Dreieck, Exit=X)
2. Equity-Kurve (laeuft synchron mit)
3. Drawdown-Kurve
4. Text-Panel: aktueller Tages-Bias, Stand der 8 Einzelsignale (+/−/neutral),
   laufende Win-Rate/Profit-Factor

**Umfang/Cadence:** ein Frame pro Kerze (5m) im Default-Modus, begrenzt auf `--days N`
(Default 5 Handelstage) — bei ~11.000 5m-Kerzen ueber 47 Tage (siehe bestehende Notiz zur
`bt.run()`-Laufzeit in `backtest_walkforward.py`) waere ein Kerzen-Replay ueber die volle
Historie unbrauchbar lang. Ein `--daily`-Schalter wechselt auf 1 Frame/Tag fuer laengere
Zeitraeume und ist fuer die Stress-Fenster aus Phase 4 ohnehin noetig (dort keine
Intraday-Daten vorhanden).

Aufruf: `python algo/dashboard.py MNQ` (Default: letzte 5 Handelstage, volles Kerzen-Replay)
oder `python algo/dashboard.py MNQ --daily --stress 2008` (Tages-Cadence, Stress-Fenster).

**Test:** kein eigener Test — visualisiert nur bereits getestete Logik aus
`backtest_ensemble.py`.

## Dateiuebersicht

| Datei | Status |
|---|---|
| `algo/signals.py` | neu |
| `algo/fetch_yfinance.py` | erweitert (`--symbol`-Argument) |
| `algo/backtest_ensemble.py` | neu |
| `algo/validate.py` | neu |
| `algo/backtest_walkforward.py` | umgebaut zu duennem Wrapper um `validate.py` |
| `algo/validate_ensemble.py` | neu, duenner Wrapper um `validate.py` |
| `algo/stress_test.py` | neu |
| `algo/dashboard.py` | neu |
| `algo/requirements.txt` | erweitert (`scikit-learn`) |

## Fehlerbehandlung (projektweit fuer diese Phasen)

- Fehlende Signal-Daten (z.B. ES=F an einem Tag nicht geladen): Signal liefert `None` ->
  in der Feature-Matrix als `0` imputiert, keine Exception, keine verworfene Zeile.
- Zu wenig Tage in einem Walk-Forward-Fold: gleiches Verhalten wie heute — Fold wird
  uebersprungen, Meldung auf stdout, kein Abbruch.
- Stress-Fenster ohne Intraday-Daten: sauberer Fallback `EnsembleStrategy(intraday=False)`,
  kein stiller Genauigkeitsverlust.
- sklearn-Konvergenzwarnungen bei kleinen Folds: werden durchgereicht/geloggt, nicht
  unterdrueckt — ehrlich melden statt schoenrechnen, passt zum bisherigen Projektstil.

## Offene Punkte / bewusste Einschraenkungen

- Bei ~150 Handelstagen und 8 Features ist Overfitting ein reales Risiko trotz
  Regularisierung — jedes Ergebnis aus Phase 2/3 ist eine Groessenordnungs-Schaetzung,
  kein Beweis. Wird in jedem betroffenen Docstring/Report vermerkt, wie bei allen
  bisherigen kleinen Stichproben im Projekt.
- Stress-Test-Ergebnisse sind Verhaltens-Kennzahlen auf einem Preis-Proxy (NQ=F statt
  MNQ), keine echte historische MNQ-P&L — MNQ existiert als Instrument erst seit 2019.
