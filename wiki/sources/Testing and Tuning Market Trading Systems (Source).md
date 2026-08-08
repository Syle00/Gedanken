---
tags: [source, algo-methodology, validation, buch, referenz]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[Testing and Tuning Market Trading Systems]]"]
---

# Testing and Tuning Market Trading Systems (Source)

**Timothy Masters, Apress 2018** (ISBN 978-1-4842-4172-1 / e-ISBN 978-1-4842-4173-8), 7 Kapitel,
C++-Beispielcode. Rohquelle: `raw/testing-and-tuning/Testing and Tuning Market Trading Systems.md`
(aus dem EPUB konvertiert, 9.434 Zeilen), Bilder unter `raw/testing-and-tuning/assets/` (78
Dateien, davon ein großer Teil TeX-Formelgrafiken und Ergebnis-Screenshots).

Kein ICT/SMC-Material — reine **Validierungsmethodik** für Handelssysteme, und zwar die
Primärquelle hinter dem, was im Vault bisher nur aus zweiter Hand über
[[How I Develop Trading Strategies (Source)]] (neurotrader) vorlag. Die Seiten
[[Vier-Stufen-Strategieentwicklung (Masters)]] und [[Monte Carlo Permutation Test (MCPT)]]
verweisen auf genau diesen Autor.

**Diese Seite ist der Einstiegsknoten**: Kapitelübersicht, vollständiges Formelverzeichnis,
Programmverzeichnis und Konstanten-/Default-Tabelle. Die inhaltliche Ausarbeitung steht auf den
verlinkten Konzeptseiten.

> Masters' eigene Positionierung: *„You will find little or nothing in the way of actual, proven
> trading systems here. Those are a dime a dozen and usually worth the price."* Alle
> Beispielsysteme (MA-Crossover, MA-Breakout, Mean Reversion) sind bewusst primitiv gehalten,
> damit der Fokus auf dem **Test** liegt, nicht auf dem System.

## Zielgruppe und Grundannahmen des Buches

Vorausgesetzt: Statistik-Grundkenntnisse (Mittelwert, Standardabweichung, Normalverteilung,
P-Werte) und irgendeine Programmiersprache. Nicht vorausgesetzt: fortgeschrittene Mathematik.
Nicht enthalten: Einführung ins Trading, fertige Systeme, „geheime" Indikatoren.

Vier durchgehende Konventionen, die man kennen muss, um die Beispiele zu lesen:

1. **Alles rechnet auf Log-Preisen.** Prozentänderungen sind nicht symmetrisch: +10 % und −10 %
   ergeben nicht null. Bei einem Hin und Her von 100→110→100 verbucht man +10 % und −9,1 %, also
   fast +1 % Scheingewinn — über viele Trades summiert das ein wertloses System in den Gewinn.
   Log-Differenzen lösen das exakt: `log(11)−log(10) = log(110)−log(100) = 0,09531`. Kleine
   Log-Änderungen mal 100 sind näherungsweise Prozent (100→101 ⇒ 0,995 statt 1,0).
2. **Tages-Bars in allen Beispielen**, aber nie erforderlich — alles gilt für Ticks bis Monate.
3. **Trades werden meist auf dem Bar-Close geöffnet/geschlossen.** Realistischer wäre: auf dem
   Close entscheiden, auf dem nächsten Open handeln. Bewusst vereinfacht, um den Blick auf den Test
   zu lenken; `MCPT_BARS` zeigt die konservative Variante.
4. **Handelskosten sind durchweg weggelassen**, ebenfalls zur Vereinfachung. Der Code zeigt, wo sie
   einzubauen wären.

Zwei Kapitel-1-Punkte, die im Vault sonst nirgends so klar stehen:

- **Future Leak wird chronisch unterschätzt.** Masters berichtet von erfahrenen Entwicklern, die
  ihm geduldig erklärten, ihr kleines Leck sei doch unerheblich. Sein Gegenbeleg: die Equity-Kurve
  eines nahezu zufälligen Win1/Lose1-Systems mit **1 % Edge** sieht bereits respektabel aus.
  Eine Kurve, die eigentlich flach sein müsste. *„Future leak is far deadlier than you imagine."*
- **Die Percent-Wins-Fallacy.** `(1-1) ExpectedReturn = Win·P(Win) − Loss·P(Loss)`. Auf einem
  echten Random Walk lässt sich jede Trefferquote herstellen: Ziel 1 Punkt, Stop 9 Punkte → man
  gewinnt in 9 von 10 Fällen, und der Erwartungswert bleibt exakt null. Gewinn-/Verlustgrößen und
  ihre Häufigkeiten sind untrennbar gekoppelt — wer mit einer Trefferquote wirbt, muss nach den
  Größen gefragt werden und umgekehrt. Deckt sich mit
  [[Erwartungswert & Reward-to-Risk-Modell]].

Und ein psychologischer, den Masters aus eigener Erfahrung schildert: ein Trader, dessen
Mantra „cut your losses and let your wins run" war, überschrieb dauerhaft die Signale eines
Systems, das nachweislich mit vielen kleinen Gewinnen und seltenen großen Verlusten optimal lief —
die parallel laufende Simulation verdiente deutlich mehr als seine Ausführung. *„Forget automated
trading if you don't have the guts to believe in it."*

## Kapitelübersicht mit Zielseiten

| Kap. | Inhalt | Wiki-Seite |
|---|---|---|
| 1 | Log-Preise, Future Leak, Percent-Wins-Fallacy, algorithmisch vs. modellbasiert | (hier) |
| 2 | Stationarität (STATN-Gap-Analyse), Indikator-Entropie, Tail-Cleaning | [[Indikator-Stationarität & Entropie]] |
| 3 | Regularisiertes lineares Modell (Coordinate Descent), Polynom-Nichtlinearität | [[Regularisiertes lineares Modell (Ridge, Lasso, Elastic Net)]] |
| 3 | Differential Evolution | [[Differential Evolution & Parameter-Sensitivität]] |
| 4 | StocBias (billige Bias-Schätzung) | [[Training Bias & Selection Bias]] |
| 4 | PARAMCOR (Hessian), Sensitivitätskurven | [[Differential Evolution & Parameter-Sensitivität]] |
| 5 | Training Bias, Selection Bias, „was heißt unbiased" | [[Training Bias & Selection Bias]] |
| 5 | Walk-Forward-Algorithmus, Guard Buffer, Varianz-Inflation, unbekannter Lookahead | [[Walk-Forward Guard Buffer & Varianz-Inflation]] |
| 5 | Cross Validation, XvW, CV-in-Walk-Forward | [[Cross Validation vs. Walk-Forward (Masters)]] |
| 5 | CSCV-Dominanztest | [[CSCV (Combinatorially Symmetric Cross Validation)]] |
| 5 | Nested Walkforward, CHOOSER | [[Nested Walkforward]] |
| 6 | Rendite-Granularität | [[Profit pro Bar vs. pro Trade]] |
| 6 | Hypothesentests, t-Grenzen, Bootstrap, BCa, Ratio-Warnung | [[Konfidenzgrenzen für Renditen (t-Test, Bootstrap, BCa)]] |
| 6 | Quantilgrenzen für Einzelrenditen, Drawdown-Doppel-Bootstrap | [[Grenzen für Einzelrenditen & Drawdown]] |
| 7 | MCPT: drei Testobjekte, Selection-Bias-Erweiterung, Permutationsalgorithmen | [[Monte Carlo Permutation Test (MCPT)]] |
| 7 | Return-Partitionierung Skill/Trend/TrainingBias | [[Return-Partitionierung (Skill, Trend, Training Bias)]] |

## Formelverzeichnis

Alle 40 nummerierten Gleichungen des Buches, mit Zielseite. (Im Rohtext liegen sie als
TeX-Grafiken vor; der Alt-Text enthält das LaTeX, daraus rekonstruiert.)

| Nr. | Formel | Seite |
|---|---|---|
| 1-1 | `ExpectedReturn = Win·P(Win) − Loss·P(Loss)` | (hier) |
| 2-1 | `H(X) = −Σ p(x)·log p(x)` | [[Indikator-Stationarität & Entropie]] |
| 2-2 | `tanh(x) = (eᵗ−e⁻ᵗ)/(eᵗ+e⁻ᵗ)` | dito |
| 2-3 | `logistic(x) = 1/(1+e⁻ˣ)` | dito |
| 3-1 | `ŷ = β₀ + xᵀβ` | [[Regularisiertes lineares Modell (Ridge, Lasso, Elastic Net)]] |
| 3-2 | `RegErr = (1/N)Σ(yᵢ−xᵀβ)² + 2λ·P_α(β)` | dito |
| 3-3 | `P_α(β) = Σⱼ[((1−α)/2)βⱼ² + α|βⱼ|]` | dito |
| 3-4 | `rᵢ = yᵢ − ŷᵢ` | dito |
| 3-5 | `argumentⱼ = (1/N)Σ x_ij·rᵢ + βⱼ` | dito |
| 3-6 | `S(z,g)` Soft-Thresholding | dito |
| 3-7 | `β̂ⱼ = S(argumentⱼ, λα)/(1+λ(1−α))` | dito |
| 3-8 | `argumentⱼ` gewichtet | dito |
| 3-9 | `β̂ⱼ` gewichtet | dito |
| 3-10 | `argumentⱼ` über Kovarianz-Updates | dito |
| 3-11 … 3-15 | `Yinnerⱼ`, `Xinner_jk`, `Xssⱼ` (un-/gewichtet) | dito |
| 3-16 / 3-17 | λ-Schwelle, ab der alle β null bleiben | dito |
| 5-1 | `Ncombinations = Nblocks!/((Nblocks/2)!)²` | [[CSCV (Combinatorially Symmetric Cross Validation)]] |
| 6-1 | `Mean = (1/n)Σxᵢ` | [[Konfidenzgrenzen für Renditen (t-Test, Bootstrap, BCa)]] |
| 6-2 | `StdDev = sqrt((1/(n−1))Σ(xᵢ−Mean)²)` | dito |
| 6-3 | `t = √n·Mean/StdDev` | dito |
| 6-4 | `p = 1 − CDF_t(n−1, t)` | dito |
| 6-5 | `t = √n(ObsMean−TrueMean)/StdDev` | dito |
| 6-6 … 6-8 | Herleitung der Konfidenzaussage | dito |
| 6-9 | `LowerBound = ObsMean − StdDev·t_p/√n` | dito |
| 6-10 | `ẑ₀ = Φ⁻¹(#[θ̂*ᵇ<θ̂]/B)` — BCa-Bias | dito |
| 6-11 | `θ̄₍·₎ = (1/n)Σθ̂₍ᵢ₎` — Jackknife-Mittel | dito |
| 6-12 | `â` — BCa-Acceleration | dito |
| 6-13 | `α'` — verschobener Fraktilpunkt | dito |
| 7-1 | `Trend = (NumLong−NumShort)·TrendPerReturn` | [[Return-Partitionierung (Skill, Trend, Training Bias)]] |
| 7-2 | `TotalReturn = Skill + Trend + TrainingBias` | dito |
| 7-3 | `TrainingBias = PermutedTotalReturn − Trend` | dito |
| 7-4 | `UnbiasedReturn = TotalReturn − TrainingBias` | dito |
| 7-5 | `Skill = UnbiasedReturn − Trend` | dito |

Nicht nummeriert, aber gleich wichtig:

```
OMIT              = min(LOOKAHEAD, max LOOKBACK) − 1        Guard Buffer
Guard-Regel CV    = derselbe Wert, BEIDSEITIG
orderstat_tail    = 1 − I_q(m, n−m+1)                       Quantil-Konfidenz
Quantil-Index     = int(frac · (n+1)) − 1                   unverzerrter Schaetzer
dd_pct            = 100 · (1 − exp(−dd))                    Log-Drawdown → Prozent
Annualisierung    = 25200 · mittlere Log-Bar-Rendite        (252 Handelstage × 100)
```

## Programmverzeichnis

| Programm | Aufruf / Zweck | Wiki-Seite |
|---|---|---|
| `STATN` | `STATN Lookback Fractile Version Filename` — Gap-Analyse für Trend/Volatilität | [[Indikator-Stationarität & Entropie]] |
| `ENTROPY` | `ENTROPY Lookback Nbins Version Filename` — relative Entropie mehrerer Indikatoren | dito |
| `CDMODEL` | Coordinate-Descent-Klasse (Elastic Net) | [[Regularisiertes lineares Modell (Ridge, Lasso, Elastic Net)]] |
| `CD_MA` | `CD_MA Lookback_inc N_long N_short Alpha Filename` | dito |
| `DIFF_EV` | Differential Evolution (Bibliotheksroutine) | [[Differential Evolution & Parameter-Sensitivität]] |
| `STOC_BIAS` | billige Trainings-Bias-Schätzung | [[Training Bias & Selection Bias]] |
| `PARAMCOR` | Hessian-basierte Parameterbeziehungen | [[Differential Evolution & Parameter-Sensitivität]] |
| `SENSITIV` | Sensitivitätskurven als Text-Histogramme | dito |
| `DEV_MA` | Komplettbeispiel: DE + StocBias + PARAMCOR + Sensitivität | dito |
| `TRNBIAS` | `TrnBias Which Ncases Trend Nreps` — Training Bias demonstrieren | [[Training Bias & Selection Bias]] |
| `SelBias` | `SelBias Which Ncases Trend Nreps` — Selection Bias demonstrieren | dito |
| `OVERLAP` | `OVERLAP nprices lookback lookahead ntrain ntest omit extra nreps` | [[Walk-Forward Guard Buffer & Varianz-Inflation]] |
| `XvW` | `XvW nprices trend lookback lookahead ntrain ntest nfolds omit nreps seed` | [[Cross Validation vs. Walk-Forward (Masters)]] |
| `CSCV_CORE` / `CSCV_MKT` | Dominanztest + Aufbau der Return-Matrix | [[CSCV (Combinatorially Symmetric Cross Validation)]] |
| `CHOOSER` | `CHOOSER Markets.txt IS_n OOS1_n MC_reps` — Nested Walkforward | [[Nested Walkforward]] |
| `PER_WHAT` | `PER_WHAT which_crit all_bars ret_type max_lookback n_train n_test file` | [[Profit pro Bar vs. pro Trade]] |
| `BOUND_MEAN` | `BOUND_MEAN max_lookback n_train n_test n_boot file` | [[Konfidenzgrenzen für Renditen (t-Test, Bootstrap, BCa)]] |
| `BOOT_CONF` | Perzentil- und BCa-Bootstrap (Bibliothek) | dito |
| `BOOT_RATIO` | `BOOT_RATIO nsamples nboot ntries prob` — Ratio-Bootstrap-Versagen | dito |
| `CONFTEST` | `CONFTEST nsamples fail_rate low_q high_q p_of_q` | [[Grenzen für Einzelrenditen & Drawdown]] |
| `BND_RET` | Quantilgrenzen an echten Marktdaten | dito |
| `DRAWDOWN` | `DRAWDOWN Nchanges Ntrades WinProb BoundConf BootReps QuantReps TestReps` | dito |
| `CHOOSER_DD` | Drawdown-Grenzen für das CHOOSER-System | dito |
| `MCPT_TRN` | `MCPT_TRN MaxLookback Nreps FileName` — P-Wert + Partitionierung | [[Return-Partitionierung (Skill, Trend, Training Bias)]] |
| `MCPT_BARS` | dasselbe auf OHLC-Bars mit Open-zu-Open-Renditen | dito |

Hilfsroutinen ohne eigene Seite: `STATS.CPP` (`normal_cdf`, `inverse_normal_cdf`, `t_CDF`,
`inverse_t_CDF`, `F_CDF`, `orderstat_tail`, `quantile_conf`), `QSORTD.CPP` (`qsortd`, `qsortdsi`),
`SVDCMP.CPP` (Singulärwertzerlegung), `EVER_RS.CPP` (`evec_rs`, Eigenwerte symmetrischer Matrizen),
`GLOB_MAX.CPP` / `BRENTMAX.CPP` (eindimensionale Maximierung).

## Konstanten und Defaults aus den Beispielen

| Größe | Wert | Kontext |
|---|---|---|
| Bootstrap-Replikationen | ≥ 10.000 | „minimum for serious testing" |
| MCPT-Permutationen | 1.000 (Buch), 200 bei Walk-Forward | Rechenzeit |
| MCPT-Schwelle | p ≤ 0,05, besser 0,01 | Trainingsprozess |
| relative Entropie | ≥ 0,5 gut, < 0,1 kritisch | Indikatorprüfung |
| Entropie-Bins | ~20 bei mehreren tausend Fällen | — |
| Tail-Cleaning | 1–10 % je Ende | typisch 5 % |
| CV-Folds | ≥ 5, besser 10+ | λ-Optimierung |
| λ-Pfad | 50 Werte, `min = 0,001·max` | Warm Start macht es billig |
| Konvergenz `eps` | 1e-5 | Coordinate Descent |
| DE `popsize` | 100 (Beispiel), mehrere hundert empfohlen | — |
| DE `overinit` | ≈ popsize, im StocBias-Beispiel 10.000 | StocBias braucht Tausende |
| DE `mutate_dev` / `pcross` / `pclimb` | 0,2 / 0,2 / 0,3 | `DEV_MA` |
| DE `max_bad_gen` | 300 (Beispiel), „50 or more" | Konvergenz |
| PARAMCOR `nc_kept` | `1,5 × ncoefs` | Heuristik des Autors |
| Sensitivität | `npoints = 30`, `nres = 80` | `DEV_MA` |
| CSCV-Blöcke | 10–12, **gerade** | Beispiele |
| Drawdown `DD_conf` | 0,9 / 0,95 / 0,99 / 0,999 | fest im Programm |
| Drawdown `Bound_conf` | 0,7 Routine, 0,9+ bei Extremen | Empfehlung |
| Annualisierung | × 25200 | Tages-Bars, Log-Renditen |

## Die wichtigsten Einzelbefunde mit Zahlen

- **Future Leak durch IS/OOS-Überlappung** ist quantifizierbar katastrophal: auf reinem Random Walk
  erreicht ein wertloses System einen Median-t-Score von **74,64**, wenn Lookahead 10 ist und kein
  Guard Buffer gesetzt wird — mit korrektem Guard Buffer fällt er auf **−0,012**.
  → [[Walk-Forward Guard Buffer & Varianz-Inflation]]
- **Ein Bar zu wenig gepuffert reicht schon**: `omit=8` statt der nötigen 9 liefert immer noch
  t = 1,88.
- **Der naive Drawdown-Bootstrap unterschätzt Katastrophen-Drawdowns um Faktor 13,65** (63
  OOS-Returns, p = 0,001) — und in **jeder** getesteten Konstellation zu wenig, nie zu viel.
  → [[Grenzen für Einzelrenditen & Drawdown]]
- **Profit Factor auf Trade- statt Bar-Basis kann ∞ statt 1,01 ergeben.**
  → [[Profit pro Bar vs. pro Trade]]
- **Eine 9,91-%-Backtest-Rendite kann eine 90-%-Untergrenze von −0,0022 haben** (SPX,
  MA-Breakout). → [[Konfidenzgrenzen für Renditen (t-Test, Bootstrap, BCa)]]
- **Cross Validation liefert im Beispiel die vierfache Rendite von Walk-Forward** — beide sind
  nicht austauschbar. → [[Cross Validation vs. Walk-Forward (Masters)]]
- **Profit Factor hat den kleinsten Training Bias** der drei geprüften Optimierungskriterien und
  ist Masters' bevorzugtes Ziel; mittlere Rendite hat den größten.
- **Nested Walkforward auf 65 S&P-100-Werten**: Buy-and-Hold 8,75 % p.a., bestes Einzelkriterium
  17,89 % (p = 0,076), adaptive Kriterienwahl 19,12 % (**p = 0,027**). → [[Nested Walkforward]]
- **Derselbe Test kann auf zwei ähnlichen Indizes gegensätzlich ausfallen**: Mean Reversion auf SPX
  p ≈ 1,0, Trendfolge auf SPX p = 0,001.
  → [[Return-Partitionierung (Skill, Trend, Training Bias)]]
- **Ein instabiles Verhältnis als Indikator kollabiert auf relative Entropie 0,000**; reines
  Tail-Cleaning der äußeren 5 % hebt einen anderen von 0,484 auf 0,958.
  → [[Indikator-Stationarität & Entropie]]
- **Keine Regularisierung = beste In-Sample-Güte und zugleich schlechteste OOS-Leistung.**
  → [[Regularisiertes lineares Modell (Ridge, Lasso, Elastic Net)]]

## Was das Buch für dieses Projekt beiträgt

| Thema | Wiki-Seite | Status in `algo/` |
|---|---|---|
| Trainings- vs. Selektions-Bias | [[Training Bias & Selection Bias]] | Selection Bias nirgends behandelt |
| Guard Buffer / Future Leak im Walk-Forward | [[Walk-Forward Guard Buffer & Varianz-Inflation]] | nicht implementiert |
| Cross Validation vs. Walk-Forward | [[Cross Validation vs. Walk-Forward (Masters)]] | CV wird nicht genutzt (laut Buch richtig) |
| Zwei-Ebenen-Validierung | [[Nested Walkforward]] | relevant, sobald das Ensemble *auswählt* |
| Dominanz-Test über viele Parametersätze | [[CSCV (Combinatorially Symmetric Cross Validation)]] | nicht implementiert |
| Konfidenzgrenzen für die mittlere Rendite | [[Konfidenzgrenzen für Renditen (t-Test, Bootstrap, BCa)]] | Reports liefern nur Punktschätzer |
| Grenzen für Einzelrenditen und Drawdown | [[Grenzen für Einzelrenditen & Drawdown]] | `validate.py` nutzt den „incorrect method" |
| Rendite-Granularität | [[Profit pro Bar vs. pro Trade]] | alles auf Trade-Basis |
| Zerlegung des Backtest-Ergebnisses | [[Return-Partitionierung (Skill, Trend, Training Bias)]] | nicht implementiert |
| Indikator-Vorprüfung | [[Indikator-Stationarität & Entropie]] | Detektoren nie geprüft |
| Modellwahl (falls je nötig) | [[Regularisiertes lineares Modell (Ridge, Lasso, Elastic Net)]] | kein Modell vorhanden |
| Optimierer + Sensitivität | [[Differential Evolution & Parameter-Sensitivität]] | Grid Search, Sensitivität nur 1D |

Daraus abgeleitete Backlog-Punkte 7–10 in `algo/PLAN.md`.

## Bewusst nicht ins Wiki übernommen

- **Der vollständige C++-Quellcode.** Die Algorithmen stehen als Prosa und Python-nahes Pseudocode
  auf den Konzeptseiten, inklusive aller Konstanten und Sonderfälle; die Zeile-für-Zeile-Umsetzung
  in C++ nicht. Dieses Projekt arbeitet in Python mit `numpy`/`scipy`/`backtesting`.
- **Die Herleitungen** zu Coordinate Descent (Friedman/Hastie/Tibshirani 2010) und zur BCa-Theorie
  (Efron/Tibshirani, *An Introduction to the Bootstrap*) — im Buch selbst nur referenziert. Ebenso
  Masters' Querverweise auf seine eigenen Bücher *Data Mining Algorithms in C++* und *Assessing and
  Improving Prediction and Classification*.
- **Speicher-/Performance-Details** der C-Implementierung (Zeigerarithmetik, `memcpy`-Muster,
  symmetrische Matrizen doppelt speichern) — außer wo sie eine algorithmische Aussage tragen.
- **TeX-Formelbilder** bleiben in `raw/testing-and-tuning/assets/`; die inhaltlich relevanten
  Formeln sind oben und auf den Konzeptseiten als Text erfasst.
