---
tags: [concept, quant-finance, lineare-algebra, mit-ocw]
created: 2026-08-12
updated: 2026-08-12
sources: ["[[2025-12-03 - MIT 15.S08 Lecture 2 - Linear Algebra (Source)]]", "[[2025-12-03 - MIT 15.S08 Lecture 4 - Linear Algebra cont, Probability Theory (Source)]]"]
---

# Lineare Algebra für Finance

Formelsammlung aus den MIT-15.S08-Vorlesungen 2 und 4 (Peter Kempthorne): lineare Algebra, so weit
wie sie in der Finance direkt gebraucht wird — Portfolio-Vektoren, Markov-Ketten,
Ein-Perioden-Marktmodelle, Eigenwertzerlegung, Singulärwertzerlegung (SVD).

## Portfolio als Vektor-Algebra

- Preisvektor `p` (m Assets), Positionsvektor `q` (Stückzahlen je Asset). Portfoliowert:
  `V(t) = q(t) · p(t)` (Skalarprodukt).
- PnL zwischen zwei Zeitpunkten: `ΔV = q(t) · (p(t+1) − p(t))` — die Positionen `q(t)` müssen aus
  Information bis `t` (nicht später) stammen, sonst Lookahead-Bias.
- Rebalancing-Constraint (keine Ein-/Auszahlung): `Σⱼ Δqⱼ(t)·pⱼ(t) = 0`.
- Long-Short-Portfolio `d = q − w`; **Zero-Cost-Portfolio**: `d · p = 0` bei mindestens einer
  Komponente `dⱼ ≠ 0`. Ein **Arbitrage-Portfolio** ist ein Zero-Cost-Portfolio mit garantiert
  nicht-negativem und manchmal positivem Payoff — existiert per Definition nicht in
  arbitragefreien Märkten.
- Norm/Skalarprodukt-Geometrie: `v·w = ‖v‖‖w‖cos θ` — Grundlage für Orthogonalität, später
  zentral in Regression (orthogonale Residuen) und PCA (orthogonale Hauptachsen).

## Markov-Matrizen

- Stochastische Matrix `A`: Spalten summieren zu 1, `Aᵢⱼ = P(Zustand i zum Zeitpunkt t+1 | Zustand j zum Zeitpunkt t)`.
- Zustandsverteilung entwickelt sich über `π(t+1) = A·π(t)`, also `π(t) = Aᵗ·π(0)`.
- Stationäre Verteilung `π*` erfüllt `A·π* = π*` — `π*` ist der Eigenvektor von `A` zum Eigenwert 1.
  Existiert nur, wenn die Kette azyklisch ist (keine reinen Zyklen zwischen Zuständen).

## Ein-Perioden-Marktmodell (zwei Zustände)

- Bond `B`: `B_T = B_0·(1 + r_f·T)` (risikofrei). Aktie `S`: `S_T ∈ {S_T^u, S_T^d}` (unsicher).
- Portfolio `π = (π_B, π_S)`, Startwert `V_0 = π_B·B_0 + π_S·S_0`.
- **Replizierendes Portfolio** für einen Contingent Claim `C` (z.B. Call-Option mit Payoff
  `max(S_T − K, 0)`): löse `π_B·B_T + π_S·S_T^u = C_T^u` und analog für den Down-Zustand nach
  `π_B, π_S` auf → `C_0 = π_B·B_0 + π_S·S_0`. Grundprinzip der Optionsbewertung
  (Black-Scholes-Vorstufe).
- **Arbitragefreiheit ↔ Pricing-Measure**: existiert eine Wahrscheinlichkeitsverteilung `Q*` über
  die Zustände mit `Preis_j(0) = Diskontfaktor · E_Q*[Preis_j(T)]` und allen `qⱼ* > 0`, dann ist
  der Markt arbitragefrei; ist `Q*` eindeutig, ist der Markt zusätzlich **vollständig** (jeder
  Claim replizierbar).

## Eigenwerte, Eigenvektoren, Diagonalisierung

- `A·v = λ·v`. Eigenwerte als Nullstellen von `det(A − λI) = 0`.
- Bei linear unabhängigen Eigenvektoren: `A = S·Λ·S⁻¹` (S = Matrix der Eigenvektoren als Spalten,
  Λ = Diagonalmatrix der Eigenwerte). Potenzen: `Aᵏ = S·Λᵏ·S⁻¹` — Basis für Zustandsraum-Modelle
  und Kalman-Filter (State-Transition über mehrere Perioden ohne wiederholte Matrixmultiplikation).
- Symmetrische reelle Matrizen (z.B. jede Kovarianzmatrix) haben ausschließlich reelle Eigenwerte,
  und Eigenvektoren zu unterschiedlichen Eigenwerten stehen orthogonal aufeinander — Grundlage der
  PCA, siehe [[Hauptkomponentenanalyse (PCA) in der Finance]].
- **Perron-Frobenius-Theorem**: eine quadratische Matrix mit ausschließlich streng positiven
  Einträgen hat einen reellen, betragsgrößten Eigenwert mit ausschließlich positivem Eigenvektor —
  relevant für Konvergenzbeweise bei Markov-Ketten und Preismodellen mit positiven Zuständen.

## Singulärwertzerlegung (SVD)

- Jede Matrix `A` (m×n) lässt sich zerlegen als `A = U·D·Vᵀ` mit `U`, `V` orthogonal (`UᵀU=I`,
  `VᵀV=I`) und `D` diagonal (Singulärwerte `σ₁ ≥ σ₂ ≥ ... ≥ 0`).
  Reduzierte Form: `A = Σᵢ σᵢ·uᵢ·vᵢᵀ` — Summe von `r` Rang-1-Matrizen (r = Rang von A).
- `AᵀA = V·D²·Vᵀ` liefert Eigenwerte `= σᵢ²` und Eigenvektoren `= vᵢ` — SVD und
  Kovarianzmatrix-Eigenzerlegung sind zwei äquivalente Rechenwege zur PCA.
- Praktischer Nutzen: Rang-`k`-Approximation (nur die `k` größten Singulärwerte behalten) als
  Dimensionsreduktion, wenn die Varianz eines Datensatzes auf wenige Richtungen konzentriert ist.

## Bezug zu diesem Projekt

- Die Portfolio-Vektor-Notation (`q·p`, PnL als `q(t)·Δp`) ist im Kern bereits, was
  `algo/pnl.py`/`algo/backtest_ensemble.py` implizit tun — eine explizite Vektorisierung über
  mehrere gleichzeitig gehaltene Kontrakte (MNQ + andere Symbole) wäre eine direkte Anwendung,
  siehe [[Quant-Finance-Formeln für den MNQ-Algo (laufend)]].
- Eigenwertzerlegung/SVD sind die mathematische Basis für [[Hauptkomponentenanalyse (PCA) in der Finance]]
  und [[Bollinger-Bänder, Scaling-in & Kalman-Filter]] (Kalman-Filter-Zustandsraummodelle).
- Markov-Ketten für Up/Down-Zustandsfolgen sind direkt auf MNQ-Bar-Sequenzen übertragbar (siehe
  Lecture-6-Beispiel mit Apple-Aktie in
  [[2025-12-03 - MIT 15.S08 Lecture 6 - Stochastic Processes I cont, Regression Analysis (Source)]]).
