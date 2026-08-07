# Bar-Permutationstest (MCPT nach Timothy Masters) — Design

> Quelle: `raw/md.md` (Transkript, YouTube-Video zu Timothy Masters' Buch "Permutation and
> Randomization Tests for Trading System Development"). Wird zusaetzlich als
> `wiki/sources/`-Seite ingestet (separater, nicht-Code-Schritt, folgt den Ingest-Konventionen
> aus `CLAUDE.md`).

## Ziel

Ein strategie-agnostisches Validierungsmodul `algo/permutation_test.py`, das die im Video
beschriebene Monte-Carlo-Permutationsmethode implementiert: Preis-Bars werden statistik-erhaltend
gemischt, die Strategie wird auf den permutierten Daten neu optimiert, und die Verteilung der so
erzielten Objective-Werte (Profit Factor) zeigt, wie viel des In-Sample-Ergebnisses auf
Data-Mining-Bias statt auf echte Muster zurueckgeht. Ergaenzt die bestehenden drei Verfahren in
`algo/validate.py` (Walk-Forward, Parameter-Sensitivitaet, Trade-Order-Resampling) um ein
viertes, unabhaengiges Verfahren — keine dieser vier Methoden ersetzt eine der anderen.

**Abgrenzung zu `validate.py`:** `validate.py` nennt Trade-Reihenfolge-Resampling bereits
"Monte Carlo". Um Verwechslung zu vermeiden, heisst das neue Modul im Code und in der Doku
konsequent **"Bar-Permutationstest"** bzw. **MCPT**, nie nur "Monte Carlo".

**Scope dieser Iteration:** Nur die Infrastruktur (Bar-Permutation + In-Sample-Test +
Walk-Forward-Permutationstest + Live-Visualisierung). Keine konkrete Strategie wird in diesem
Schritt angebunden — das ist ein separater, spaeterer Schritt (z.B. Ensemble- oder Silver-Bullet-
Strategie), sobald genug Handelstage fuer sinnvolle Re-Optimierung vorliegen.

## Architektur

Datei `algo/permutation_test.py`, drei Kernfunktionen. Parameter-Konvention bewusst identisch zu
`algo/validate.py` (`strategy_cls`, `bt_kwargs`, `param_name`/`candidates` ODER `on_fold_train`-
Hook) — wer `validate.walk_forward()` kennt, kennt auch dieses Interface.

### 1. `get_permutation(df, start_index=0, seed=None) -> pd.DataFrame`

Implementiert den Bar-Permutationsalgorithmus aus dem Transkript:

1. Log-Preise berechnen, pro Bar relativ zum eigenen Open ausdruecken (High/Low/Close als
   Prozent-Offset vom Open), plus die Gap-Groesse (Open relativ zum Close des Vorbars).
2. Ab `start_index` (Default 0 = alles) werden die Indizes zweimal separat permutiert — einmal
   fuer die Intrabar-Werte (High/Low/Close-Offsets), einmal fuer die Gaps — mit einem
   `random.Random(seed)`-Objekt fuer Reproduzierbarkeit.
3. Aus den gemischten relativen Werten werden neue OHLC-Bars sequenziell rekonstruiert (jeder
   Open = Vor-Close + gemischter Gap, dann High/Low/Close relativ zu diesem Open), zurueck auf
   die normale Preisskala exponenziert.
4. Alles vor `start_index` bleibt unveraendert — das macht `start_index` fuer den
   Walk-Forward-Test nutzbar (nur der Test-Zeitraum wird permutiert, die Trainingsdaten bleiben
   echt).

Reiner NumPy/Pandas-Code, kein Lookahead moeglich (die Funktion arbeitet auf einem fertigen
DataFrame, nicht auf einem Live-Strom). Single-Market-Scope fuer diese Iteration (der
Multi-Market-Fall wird im Transkript selbst nur angerissen und explizit fuer spaeter
zurueckgestellt — hier ebenso).

### 2. `in_sample_test(df, strategy_cls, bt_kwargs, param_name=None, candidates=None, on_fold_train=None, objective="Profit Factor", n_perms=1000, seed=42, live=True, plot_path=None) -> float`

- Optimiert einmal auf den echten Daten (gleiche Optimierungslogik wie
  `validate.walk_forward()`: Grid-Search ueber `candidates` falls `param_name` gesetzt, sonst
  `on_fold_train`-Hook fuer Modell-Strategien).
- Loopt `n_perms`-mal: `get_permutation(df, seed=seed+i)` erzeugen, Strategie darauf neu
  optimieren, Objective-Wert (Default Profit Factor) sammeln.
- P-Wert = Anteil Permutationen mit Objective-Wert >= echtem Wert.
- Gibt den P-Wert zurueck und druckt eine Textzeile (Real-Wert, P-Wert, n_perms) analog zum
  bestehenden `validate.monte_carlo()`-Ausgabestil.

### 3. `walk_forward_permutation_test(df, strategy_cls, bt_kwargs, train_window_days, ..., n_perms=200, live=True, plot_path=None) -> float`

Wie oben, aber:

- `get_permutation(df, start_index=train_window_days)` — nur der Test-Zeitraum nach dem ersten
  Trainings-Fold wird permutiert, das Training bleibt auf echten Daten.
- Pro Permutation laeuft der volle Walk-Forward (teuer, daher Default `n_perms=200` statt 1000,
  wie im Transkript begruendet: "walk forward permutation test can take forever to run").
- Wenn zu wenig Handelstage fuer den gewuenschten `train_window_days`-Wert vorliegen: Test wird
  uebersprungen mit Hinweistext (Skip-Meldung), analog zu `validate.walk_forward()`s
  bestehendem Verhalten bei zu kurzem `df` — kein Crash.

## Live-Visualisierung

Beide Testfunktionen bekommen `live=True` (Default) und `plot_path=None` (optional).

- **Waehrend des Laufs:** Ein matplotlib-Fenster oeffnet sich und baut das Histogramm der
  Permutations-Objective-Werte laufend auf (Balken wachsen mit jeder abgeschlossenen
  Permutation), plus eine vertikale Linie beim echten Wert — visuell wie im Transkript
  beschrieben ("plot a histogram... add a line showing where in the distribution the real
  profit factor fell"). Implementiert mit demselben `matplotlib.animation.FuncAnimation`-Pattern
  und Stil wie `algo/dashboard.py`, nicht neu erfunden.
- **Am Ende:** Falls `plot_path` gesetzt, wird der Endstand zusaetzlich per `savefig` als PNG
  abgelegt (Konvention: `algo/results/permutation_<name>.png`, ueberschrieben bei jedem neuen
  Lauf — reiht sich neben die bestehenden `algo/results/backtest_*.json`-Dateien ein).
- `live=False` erlaubt einen reinen Text-/Batch-Modus (z.B. fuer `selfcheck.py`, siehe unten) —
  kein Fenster, kein PNG, nur der zurueckgegebene P-Wert.

## Fehlerbehandlung

- Zu wenig Handelstage fuer den Walk-Forward-Test: Skip mit Hinweistext (siehe oben), kein
  Crash — konsistent mit `validate.walk_forward()`.
- `n < 10` Permutationen mit gueltigem Objective-Wert (z.B. weil eine Strategie auf permutierten
  Daten oft keine Trades erzeugt): Warnhinweis im Textoutput, P-Wert wird trotzdem berechnet,
  aber als "wenig belastbar" markiert (analog zu `dubious_pct`-Handhabung in `validate.py`).
- Kein Lookahead-Risiko durch Design: Permutation arbeitet auf einem fertigen DataFrame, jede
  Re-Optimierung sieht nur die Daten, die ihr explizit uebergeben werden (Trainingsfenster bei
  Walk-Forward bleibt unveraendert echt).

## Tests

`algo/selfcheck.py` bekommt einen neuen Check `permutation_test`: ruft `in_sample_test()` und
`walk_forward_permutation_test()` mit `live=False`, winzigem `n_perms` (z.B. 5) und einer
Mini-Dummy-Strategie/synthetischem DataFrame auf — prueft nur, dass die Schnittstelle funktioniert
und ein P-Wert zwischen 0 und 1 zurueckkommt, kein echter Backtest-Regressionscheck.

## Dokumentation

- `algo/README.md`: neue Sektion `## permutation_test.py -- Bar-Permutationstest (MCPT)` nach
  bestehendem Muster (Was/Wie/Warum/Bekannte Grenzen).
- `algo/PLAN.md`: Log-Eintrag mit Datum, Quelle (`raw/md.md`), kurzer Zusammenfassung.
- `wiki/sources/`: separate Ingest-Seite fuer das Transkript (folgt normalem Ingest-Workflow aus
  `CLAUDE.md`, ausserhalb dieses Specs).

## Bekannte Grenzen (von Anfang an dokumentiert, nicht erst im Audit)

- Die Permutation zerstoert Volatility-Clustering und Long-Memory-Eigenschaften echter Preise
  (explizit im Transkript benannt) — Strategien, die stark auf diesen Eigenschaften beruhen,
  koennen den Test optimistisch verzerrt bestehen. Das macht den Test nicht wertlos (siehe
  Transkript-Begruendung), aber es ist kein Ersatz fuer Walk-Forward/Stress-Test.
- Kleine Stichprobe: solange `raw/marktdaten/` nur wenige hundert Handelstage umfasst, sind
  P-Werte Groessenordnungen, keine belastbaren Zahlen (gleiche Einschraenkung wie in
  `validate.py` dokumentiert).
- Multi-Market-Permutation (korrelierte Maerkte gemeinsam mischen) ist nicht Teil dieser
  Iteration.
