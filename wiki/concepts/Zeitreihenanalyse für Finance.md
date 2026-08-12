---
tags: [concept, quant-finance, zeitreihenanalyse, mit-ocw]
created: 2026-08-12
updated: 2026-08-12
sources: ["[[2025-12-03 - MIT 15.S08 Lecture 12 - Time Series Analysis (Source)]]"]
---

# Zeitreihenanalyse für Finance

Formelsammlung aus MIT-15.S08-Lecture 12 (Peter Kempthorne): Stationarität, Autokorrelation, die
Wold-Zerlegung und ARMA-Modelle als Werkzeuge, um Preiszeitreihen auf eine analysierbare Skala zu
bringen. Ergänzt [[Regressionsanalyse für Finance]] um die zeitliche Dimension.

## Stationarität

- **Strikte Stationarität**: die Verteilung jeder endlichen Punktmenge `{X_t1,...,X_tm}` ist
  invariant gegenüber einer Zeitverschiebung `τ`.
- **Kovarianzstationarität** (schwächer, praxisrelevant): konstanter Mittelwert `E[X_t]=μ`,
  konstante Varianz, und die Kovarianz zwischen `X_t` und `X_{t+τ}` hängt nur von `τ` ab, nicht
  von `t`.
- Roh-Preisserien (z.B. S&P 500) sind nicht stationär (Trend). Log-Returns `r_t = log(P_t/P_{t-1})`
  sind i.d.R. näherungsweise kovarianzstationär — Standardtransformation vor jeder
  Zeitreihenmodellierung.
- Leptokurtosis: Log-Returns haben in der Praxis systematisch fettere Tails und eine höhere
  Zentrumsspitze als die Normalverteilungsanpassung vorhersagt — sichtbar bei S&P 500, Amazon,
  Crude-Oil-Futures und 10Y-Treasury-Yields gleichermaßen, unabhängig von der Frequenz.

## Autokorrelationsfunktion (ACF)

- `ρ(τ) = Cov(X_t, X_{t+τ}) / Var(X_t)` — Korrelation der Serie mit sich selbst.
- Geschätzt als `R̂_k` (Stichproben-Autokorrelation bei Lag k): approximativ normalverteilt mit
  Varianz `1/(T−k)`. Signifikanztest gegen `H₀: ρ_k=0`: Ablehnung falls
  `|R̂_k| > 1.96·√(1/(T−k))`.
- **Box-Pierce-Test** (Portmanteau-Test über mehrere Lags gleichzeitig):
  `BP = T·Σ_{j=1}^{K} R̂_j²` ist approximativ χ²-verteilt mit K Freiheitsgraden unter
  `H₀: ρ_1=...=ρ_K=0`.
- Praxisbefund aus der Vorlesung: monatliche S&P-500-Returns zeigen negative Autokorrelation bei
  Lag 1 (Mean-Reversion-Hinweis); Crude-Oil-Futures zeigen wöchentlich negative Autokorrelation bei
  Lag 2 und positive bei Lag 3 — ein potenziell ausnutzbares Muster laut Vorlesung; Amazon-Aktie
  zeigt auf keiner Frequenz signifikante Autokorrelation.
- Residuendiagnose: ein gutes Zeitreihenmodell hinterlässt Residuen, deren ACF überall innerhalb
  der Zufallsbänder liegt (White Noise: Mittel 0, konstante Varianz, unkorreliert).

## Wold-Zerlegungstheorem

Jeder kovarianzstationäre Prozess lässt sich zerlegen in `X_t = V_t + S_t`, wobei `V_t` linear
deterministisch ist (z.B. eine Summe von Sinus-/Kosinus-Termen, aus der Vergangenheit exakt
vorhersagbar) und `S_t = Σ ψ_i·η_{t-i}` ein Moving-Average-Prozess aus unkorreliertem White Noise
`η_t` ist. Praktische Konsequenz: sobald eine Serie auf kovarianzstationäre Skala gebracht ist
(Detrending + Log-Returns), lässt sich jede verbleibende Struktur als (potenziell unendlicher)
Moving-Average-Prozess auffassen — die theoretische Rechtfertigung für ARMA-Modelle.

## Lag-Operator und ARMA(p,q)

- Lag-Operator `L`: `L·X_t = X_{t-1}`. Polynome in `L` erlauben kompakte Notation für AR-/MA-Terme.
- **ARMA(p,q)**: `φ(L)(X_t − μ) = θ(L)η_t`, mit `φ(L) = 1 − φ_1L − ... − φ_pL^p` (AR-Teil) und
  `θ(L) = 1 + θ_1L + ... + θ_qL^q` (MA-Teil).
- **AR(1)-Stationaritätsbedingung**: `|φ| < 1` (äquivalent: die Nullstelle der charakteristischen
  Gleichung `1−φz=0` liegt außerhalb des Einheitskreises). Für `0<φ<1`: exponentielle
  Mean-Reversion. Für `−1<φ<0`: oszillierende Mean-Reversion. `φ=1`: Random Walk (nicht
  stationär). `|φ|>1`: explosiv.
- AR(1)-Momente: `Var(X_t) = σ²/(1−φ²)`, `j`-te Autokorrelation `= φ^j` — die
  Autokorrelationsfunktion eines AR(1)-Prozesses zerfällt geometrisch.
- **Yule-Walker-Gleichungen**: Methode-der-Momente-Schätzung der AR-Parameter über ein lineares
  Gleichungssystem aus den empirischen Autokovarianzen `γ_j = Σ_i φ_i·γ_{j-i}`.
- Differenzierung `ΔX_t = (1−L)X_t` entfernt einen linearen Trend; zweite Differenzierung entfernt
  einen quadratischen Trend — Standardvorgehen für nicht-stationäre Serien vor ARMA-Fit (→ ARIMA).

## Bezug zu diesem Projekt

- Die AR(1)-Mean-Reversion-Formel (`φ^j`-Zerfall der Autokorrelation) ist die direkte
  mathematische Fassung der ICT-These "Preis kehrt nach Extremen zum Mittel zurück" — testbar über
  die ACF von MNQ-Returns statt nur qualitativ zu behaupten. Siehe
  [[Quant-Finance-Formeln für den MNQ-Algo (laufend)]] für die konkrete Backtest-These.
- Box-Pierce/ACF-Signifikanztest ist ein direktes Werkzeug für `algo/signals.py`: statt eine
  Autokorrelation zu vermuten, lässt sich `|R̂_k| > 1.96·√(1/(T−k))` als harter Filter einbauen.
- Ergänzt [[Regressionsanalyse für Finance]]: OLS-Diagnostik geht von unkorrelierten Fehlern aus —
  bei Zeitreihen-Residuen ist die ACF-Prüfung aus diesem Abschnitt die passende Zusatzkontrolle.
