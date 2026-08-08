---
tags: [source, algo-methodology, validation, buch]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[Testing and Tuning Market Trading Systems]]"]
---

# Testing and Tuning Market Trading Systems (Source)

**Timothy Masters, Apress 2018** (ISBN 978-1-4842-4172-1), 7 Kapitel, C++-Beispielcode.
Rohquelle: `raw/testing-and-tuning/Testing and Tuning Market Trading Systems.md` (aus dem
EPUB konvertiert, Bilder unter `raw/testing-and-tuning/assets/`).

Kein ICT/SMC-Material — reine **Validierungsmethodik** für Handelssysteme, und zwar die
Primärquelle hinter dem, was im Vault bisher nur zweiter Hand über
[[How I Develop Trading Strategies (Source)]] (neurotrader) vorlag. Die dortigen
Seiten [[Vier-Stufen-Strategieentwicklung (Masters)]] und
[[Monte Carlo Permutation Test (MCPT)]] verweisen auf genau diesen Autor.

> Masters' eigene Positionierung: „You will find little or nothing in the way of actual, proven
> trading systems here." Alle Beispielsysteme (MA-Crossover, MA-Breakout, Mean Reversion) sind
> bewusst primitiv gehalten, damit der Fokus auf dem **Test** liegt, nicht auf dem System.

## Was das Buch für dieses Projekt beiträgt

Das Buch beantwortet genau die Frage, an der `algo/` gerade hängt: *Wann darf ich einer
Backtest-Zahl glauben?* Es liefert dafür sieben getrennte Werkzeuge, die im Vault bisher
teilweise oder gar nicht abgedeckt waren:

| Thema | Wiki-Seite | Status in `algo/` |
|---|---|---|
| Trainings- vs. Selektions-Bias | [[Training Bias & Selection Bias]] | Selection Bias nirgends behandelt |
| Guard Buffer / Future Leak im Walk-Forward | [[Walk-Forward Guard Buffer & Varianz-Inflation]] | nicht implementiert |
| Cross Validation vs. Walk-Forward | [[Cross Validation vs. Walk-Forward (Masters)]] | CV wird nicht genutzt (laut Buch richtig) |
| Zwei-Ebenen-Validierung | [[Nested Walkforward]] | `signals.py`-Ensemble wäre ein Kandidat |
| Dominanz-Test über viele Parametersätze | [[CSCV (Combinatorially Symmetric Cross Validation)]] | nicht implementiert |
| Konfidenzgrenzen für die mittlere Rendite | [[Konfidenzgrenzen für Renditen (t-Test, Bootstrap, BCa)]] | `validate.py` liefert nur Punktschätzer |
| Grenzen für Einzelrenditen und Drawdown | [[Grenzen für Einzelrenditen & Drawdown]] | Drawdown wird nur beobachtet, nicht begrenzt |
| Zerlegung des Backtest-Ergebnisses | [[Return-Partitionierung (Skill, Trend, Training Bias)]] | nicht implementiert |

Ergänzend auf der Modellseite: [[Indikator-Stationarität & Entropie]],
[[Regularisiertes lineares Modell (Ridge, Lasso, Elastic Net)]],
[[Differential Evolution & Parameter-Sensitivität]],
[[Profit pro Bar vs. pro Trade]].

## Kapitelübersicht

1. **Introduction** — Log-Preise statt Prozent (`log(11)−log(10) = log(110)−log(100)`, damit
   +10 %/−10 % sich exakt aufheben statt +1 % Scheingewinn zu erzeugen); algorithmische vs.
   modellbasierte Systeme; „Future Leak Is More Dangerous Than You May Think"; die
   **Percent-Wins-Fallacy** (`E = Win·P(Win) − Loss·P(Loss)`; ein 1:9-Ziel/Stop gewinnt 9 von 10
   Mal und hat trotzdem Erwartungswert null) — deckt sich mit
   [[Erwartungswert & Reward-to-Risk-Modell]].
2. **Pre-optimization Issues** — Stationarität (STATN-Gap-Analyse), Indikator-Entropie.
3. **Optimization Issues** — regularisiertes lineares Modell per Coordinate Descent,
   polynomiale Nichtlinearität, Differential Evolution.
4. **Post-optimization Issues** — billige Trainings-Bias-Schätzung (StocBias), Hessian-basierte
   Parameter-Korrelationen (PARAMCOR), Sensitivitätskurven.
5. **Estimating Future Performance I** — IS/OOS, Selection Bias, Walk-Forward-Algorithmus samt
   Guard Buffer, Cross Validation, CSCV, Nested Walkforward.
6. **Estimating Future Performance II** — Rendite-Granularität, t-Test-/Bootstrap-Grenzen,
   BCa, Grenzen für Einzelrenditen, Drawdown-Grenzen.
7. **Permutation Tests** — MCPT (fertiges System / Trainingsprozess / „Model Factory"),
   Selection-Bias-Erweiterung, Return-Partitionierung, korrekte Permutation von Preisbars und
   mehreren Märkten.

## Wichtigste Einzelbefunde (mit Zahlen)

- **Future Leak durch IS/OOS-Überlappung** ist quantifizierbar katastrophal: auf reinem Random
  Walk erreicht ein wertloses System einen Median-t-Score von **74,64**, wenn Lookahead 10 ist
  und kein Guard Buffer gesetzt wird — mit korrektem Guard Buffer fällt er auf −0,012.
  → [[Walk-Forward Guard Buffer & Varianz-Inflation]]
- **Ein Bar zu wenig gepuffert reicht schon**: `omit=8` statt der nötigen 9 liefert immer noch
  t=1,88 statt 0.
- **Der naive Drawdown-Bootstrap unterschätzt Katastrophen-Drawdowns um Faktor 13,65**
  (bei 63 OOS-Returns, p=0,001). → [[Grenzen für Einzelrenditen & Drawdown]]
- **Profit Factor auf Trade-Basis statt Bar-Basis kann ∞ statt 1,01 ergeben** — Masters'
  Zahlenbeispiel: zwei Trades mit je +101/−100 Punkten intern, netto je +1.
  → [[Profit pro Bar vs. pro Trade]]
- **Cross Validation ist für Marktdaten nicht empfohlen** („I cannot recommend cross validation
  analysis in trading system development, except in the most unusual special situations") —
  wegen Nichtstationaritäts-Leck und mangelnder Realitätsnähe.
- **Profit Factor hat in Masters' Tests den kleinsten Trainings-Bias** der drei geprüften
  Optimierungskriterien (mittlere Rendite, Profit Factor, Sharpe) und ist sein bevorzugtes
  Optimierungsziel.
- **Nested Walkforward auf 65 S&P-100-Werten**: Buy-and-Hold 8,75 % p.a., bestes Einzelkriterium
  (Total Return) 17,89 % (p=0,076), Kriterienauswahl on-the-fly 19,12 % (**p=0,027**).

## Bewusst nicht ingestet

- Der vollständige C++-Code (CDMODEL, DIFF_EV, SVDCMP, BOOT_CONF, CSCV_CORE, …) — dieses Projekt
  arbeitet in Python mit `numpy`/`scipy`/`backtesting`; die Algorithmen sind auf den Konzeptseiten
  in Prosa/Pseudocode festgehalten, die Zeile-für-Zeile-Implementierung nicht.
- Die Herleitungen zu Coordinate Descent (Friedman/Hastie/Tibshirani) und zur BCa-Theorie
  (Efron/Tibshirani) — im Buch selbst schon nur referenziert.
- TeX-Formelbilder sind als `assets/*_TeX_Equ*.png` in der Rohquelle erhalten, aber nicht
  einzeln ins Wiki übernommen; die für das Projekt relevanten Formeln stehen als Text auf den
  Konzeptseiten.
