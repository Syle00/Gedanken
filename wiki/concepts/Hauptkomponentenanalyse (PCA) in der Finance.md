---
tags: [concept, quant-finance, pca, mit-ocw]
created: 2026-08-12
updated: 2026-08-12
sources: ["[[2025-12-03 - MIT 15.S08 Lecture 4 - Linear Algebra cont, Probability Theory (Source)]]", "[[2025-12-03 - MIT 15.S08 Lecture 5 - Probability Theory cont, Stochastic Processes I (Source)]]", "[[2025-12-03 - MIT 15.S08 Lecture 9 - Principal Component Analysis in Finance (Source)]]"]
---

# Hauptkomponentenanalyse (PCA) in der Finance

Formelsammlung und Praxisregeln aus den MIT-15.S08-Vorlesungen 4/5 (mathematische Herleitung,
Peter Kempthorne) und 9 (Praxisanwendung, Stefan Andreev/Two Sigma). Siehe auch
[[Lineare Algebra für Finance]] für die SVD-/Eigenwert-Grundlagen.

## Formale Definition

- Zufallsvektor `X` (m-dimensional), Mittelwert `α`, Kovarianzmatrix `Σ` (m×m, symmetrisch,
  positiv semidefinit: `aᵀΣa = Var(aᵀX) ≥ 0` für alle `a`).
- Eigenzerlegung `Σγᵢ = λᵢγᵢ`, Eigenvektoren `γᵢ` orthonormal, Eigenwerte absteigend sortiert
  `λ₁ ≥ λ₂ ≥ ... ≥ λₘ ≥ 0`.
- i-te Hauptkomponente: `pᵢ = γᵢᵀ(X − α)` — Projektion der demeanten Daten auf die i-te
  Eigenrichtung.
- Eigenschaften der PC-Variablen: `E[pᵢ]=0`, `Cov(p) = Λ` (Diagonalmatrix der Eigenwerte) — die
  PC-Variablen sind per Konstruktion unkorreliert.
- Äquivalente Definition über Optimierung: die erste PC ist der Einheitsvektor `w`, der
  `Var(wᵀX)` maximiert; die zweite PC maximiert dieselbe Varianz unter der Nebenbedingung, dass
  sie orthogonal zur ersten steht, usw.

## Empirische Berechnung

- Datenmatrix `X` (T Beobachtungen × m Variablen), demeant zu `X*`.
- Stichproben-Kovarianzmatrix: `Σ̂ = X*X*ᵀ / T`.
- Alternativ über SVD von `X*` (`X* = V·D·Uᵀ`): `Λ̂ = D²/T`, Eigenvektoren `= V`, PC-Koordinaten
  `= D·Uᵀ` — vermeidet die explizite Kovarianzmatrix-Berechnung, numerisch oft vorzuziehen.
- Varianzzerlegung: Gesamtvarianz `= Spur(Σ) = Σᵢ λᵢ`. **Erklärte Varianz** der i-ten Komponente
  `= λᵢ / Σⱼλⱼ`.

## Praxisregeln (aus der Zinskurven-Fallstudie)

- **Demeanen ist zwingend**: PCA rotiert immer um den Ursprung; nicht-demeante Daten (z.B. rohe,
  stets positive Preise) liefern keine sinnvolle Hauptrichtung.
- **Normalisieren nur bei unterschiedlichen Einheiten**: gleiche Einheiten (z.B. Renditen
  verschiedener Anleihen) → Kovarianzmatrix ohne Normalisierung verwenden (Ergebnis bleibt
  interpretierbar als "relative Volatilität"); unterschiedliche/nicht vergleichbare Größen →
  auf Einheitsvarianz normalisieren (Korrelationsmatrix statt Kovarianzmatrix).
- **Eigenwert-Separation prüfen**: Eigenwerte in log-Skala über die Zeit plotten. Robuste,
  bedeutungsvolle Komponenten zeigen eine stabile Größenordnungs-Trennung zueinander; kreuzen sich
  die Eigenwert-Zeitreihen, ist die Struktur instabil bzw. Rauschen dominiert.
- **Out-of-Sample-Test**: kalibrierte Ladungen auf neue (zukünftige) Daten projizieren und prüfen,
  ob die Projektionen näherungsweise unkorreliert bleiben — Stabilitäts-/Robustheitscheck für die
  Faktorstruktur.
- PCA ist **unsupervised** (keine Kausalität) — Unterschied zu Regression: PCA minimiert den
  senkrechten Abstand zur Hauptachse, Regression den Abstand in y-Richtung. Bei reiner
  Korrelationsstruktur (keine klare abhängige Variable) ist PCA das passendere Werkzeug.

## Zinskurven-Fallstudie (US-Treasuries)

- PC1 ("Level", typischerweise 85–90% erklärte Varianz): alle Laufzeiten bewegen sich gemeinsam.
- PC2 ("Slope/Steilheit", ~5–10%): kurzes vs. langes Ende der Kurve gegenläufig.
- PC3 ("Curvature/Krümmung", Rest): Bauch der Kurve gegenläufig zu beiden Enden.
- Handelbare PC-Portfolios: Gewichte = Eigenvektor-Ladungen je Laufzeit. PC2-/PC3-Portfolios sind
  näherungsweise orthogonal zu PC1 (>90% des Level-Risikos gehedgt), benötigen aber Leverage, um
  vergleichbare Volatilität wie ein reines PC1-Investment zu erzielen.

## Bezug zu diesem Projekt

- **Konkrete Signal-Idee für `algo/signals.py`**: PCA über die letzten N Tage OHLC-Returns mehrerer
  Timeframes (z.B. 1m/5m/15m/1h-Returns von MNQ) könnte ein Level-/Slope-/Curvature-Analogon für
  Intraday-Volatilitätsregime liefern — analog zur Zinskurven-PC1/PC2/PC3-Aufspaltung. Siehe
  ausführlicher [[Quant-Finance-Formeln für den MNQ-Algo (laufend)]].
- Eigenwert-Separation als Robustheitscheck ist direkt auf jede in `algo/validate.py` neu
  eingeführte Faktor-/Feature-Kombination übertragbar, bevor sie als Signal genutzt wird.
- ⚠️ Reines PCA-Backtesting ohne konkrete, ausführbare Handelsregel wäre laut CLAUDE.md ein
  Layer-0-Verstoß ("kein Backtesting als Selbstzweck") — jede PCA-Anwendung muss auf eine
  `algo/rules.py`-taugliche Regel hinarbeiten, nicht nur auf eine Analyse-Grafik.
