---
tags: [concept, quant-finance, regression, mit-ocw]
created: 2026-08-12
updated: 2026-08-12
sources: ["[[2025-12-03 - MIT 15.S08 Lecture 6 - Stochastic Processes I cont, Regression Analysis (Source)]]", "[[2025-12-03 - MIT 15.S08 Lecture 8 - Regression Analysis cont (Source)]]", "[[2025-12-03 - MIT 15.S08 Lecture 11 - Regression Analysis cont (Source)]]"]
---

# Regressionsanalyse für Finance

Formelsammlung aus den MIT-15.S08-Vorlesungen 6, 8 und 11 (Peter Kempthorne): multiple lineare
Regression über Lineare Algebra hergeleitet, Verteilungstheorie, Regularisierung (Ridge/Lasso/
PCR), plus die empirische CAPM-Anwendung.

## Kleinste-Quadrate-Schätzung (OLS)

- Modell: `y = Xβ + ε` (n Beobachtungen, p Regressoren).
- Kriterium: `Q(β) = ‖y − Xβ‖²` minimieren → Normalgleichungen `XᵀXβ̂ = Xᵀy` →
  `β̂ = (XᵀX)⁻¹Xᵀy` (falls `X` vollen Spaltenrang hat).
- Hat-Matrix `H = X(XᵀX)⁻¹Xᵀ` — Projektion auf den Spaltenraum von X (`H²=H`).
  Residuen `ε̂ = (I−H)y` stehen orthogonal auf X (Normalgleichungs-Konsequenz), daraus folgt der
  verallgemeinerte Satz des Pythagoras: `‖y‖² = ‖ŷ‖² + ‖ε̂‖²`.
- Unter Normalverteilungsannahme (Gauss-Markov + Normalität der Fehler):
  `β̂ ~ N(β, σ²(XᵀX)⁻¹)`, unabhängig davon `ε̂` multivariat normal mit Kovarianz
  `σ²(I−H)` (nicht vollrangig — Residuen sind linear abhängig).
- Unverzerrte Fehlervarianz-Schätzung: `σ̂² = RSS/(n−p)` (RSS = Residual Sum of Squares).

## Hypothesentests

- t-Statistik für einen Koeffizienten: `tⱼ = (β̂ⱼ − βⱼ) / (σ̂·√Cⱼⱼ)` mit `Cⱼⱼ` = j-tes
  Diagonalelement von `(XᵀX)⁻¹`; unter `H₀: βⱼ=0` t-verteilt mit `n−p` Freiheitsgraden.
- F-Test für den gemeinsamen Ausschluss mehrerer Koeffizienten: Vergleich der Residual-Sum-of-
  Squares von vollem Modell (`RSS₁`) und Submodell (`RSS₀`),
  `F = ((RSS₀−RSS₁)/(p−k)) / (RSS₁/(n−p))`. Für den Ausschluss genau eines Koeffizienten gilt
  `t² = F`.
- Standardisierte Regressoren (Z-Scores) ändern t-/p-Werte nicht, machen `β̂ⱼ` aber direkt als
  "Effekt pro Standardabweichung" interpretierbar.

## Maximum-Likelihood, robuste und Quantil-Schätzer

- MLE für normale Fehler: minimiert dieselbe `Q(β)` wie OLS für β, aber `σ̂²_MLE = RSS/n`
  (verzerrt, kleiner als der unverzerrte OLS-Schätzer `RSS/(n−p)`).
- Generalisierte M-Schätzer: `Q(β) = Σᵢ h(yᵢ, xᵢ, β)` — `h=Quadrat` liefert OLS, `h=|·|` liefert
  robuste (Median-artige) Schätzung, `h=−log(Dichte)` liefert MLE.
- Quantil-Regression (`τ`-Quantil): asymmetrisch gewichtete absolute Abweichung
  (`τ` für positive, `1−τ` für negative Residuen) — bei `τ=0.5` äquivalent zur Median-Regression.

## Regularisierung

- Ridge: `β̂_ridge = argmin ‖y−Xβ‖² + λ‖β‖²` → äquivalent zu Bayes'scher Regression mit
  Normal-Prior `β ~ N(0, ω·I)` auf den (standardisierten!) Koeffizienten. Schrumpfung stärker
  entlang Richtungen mit kleinem Singulärwert (wenig erklärte Varianz in den Prädiktoren).
- Lasso: `β̂_lasso = argmin ‖y−Xβ‖² + λ‖β‖₁` — L1-Penalty erzeugt exakte Nullen
  (Variablenselektion), Ridge (L2) nur Schrumpfung ohne exakte Nullen.
- Principal-Components-Regression (PCR): Regression auf die ersten `m` Hauptkomponenten der
  (zentrierten/standardisierten) Prädiktoren statt auf die Rohvariablen — orthogonale Regressoren,
  einfache separate Koeffizientenschätzung je Komponente.
- Generalisiertes GLS bei korrelierten/heteroskedastischen Fehlern (`Cov(ε)=σ²Σ`):
  Transformation `y* = Σ^{-1/2}y`, `X* = Σ^{-1/2}X` reduziert auf gewöhnliches OLS.

## CAPM-Regressionstest

- `R*ⱼₜ = αⱼ + βⱼ·R*_mt + εⱼₜ` (Excess-Returns von Asset j und Markt m).
- Test `H₀: αⱼ=0` (t-Test) als empirischer CAPM-/Markteffizienz-Test.
- Empirisches Ergebnis über ~380–400 S&P-500-Titel: große Mehrheit hat statistisch nicht-
  signifikante Alphas, wenige Ausreißer mit deutlich positiven Alphas.
- Regime-Wechsel-Test: CAPM-Parameter über Sub-Perioden per F-Test auf Änderung vergleichen — bei
  langen Historien zeigen sich signifikante β-/α-Sprünge, ein Argument für Rolling-Window-
  Kalibrierung statt eines statischen Fits über den gesamten Datensatz.

## Bezug zu diesem Projekt

- Ridge/Lasso/PCR sind direkt auf `algo/signals.py` übertragbar, falls dort künftig mehrere
  korrelierte Features (z.B. mehrere Timeframes derselben Kompressions-/Displacement-Metrik)
  gemeinsam in ein Modell einfließen sollen — siehe
  [[Quant-Finance-Formeln für den MNQ-Algo (laufend)]] für die konkrete Einsatzidee.
- Der CAPM-Regressionstest (α vs. 0) ist ein Muster für einen Backtest-Signifikanztest: statt
  „Strategie X hat positiven Return" wäre „Strategie-Alpha ist signifikant von 0 verschieden nach
  Kontrolle für Markt-Beta" die strengere, in `algo/validate.py` nachbaubare Formulierung.
- Markov-/Regressions-Diagnostik (Cook's Distance, studentisierte Residuen, Q-Q-Plots) ist ein
  direktes Muster für `algo/validate.py`, um einzelne Extremtage nicht das gesamte Backtest-Ergebnis
  dominieren zu lassen.
