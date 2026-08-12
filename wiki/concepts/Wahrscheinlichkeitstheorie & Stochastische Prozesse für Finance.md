---
tags: [concept, quant-finance, wahrscheinlichkeitstheorie, stochastische-prozesse, mit-ocw]
created: 2026-08-12
updated: 2026-08-12
sources: ["[[2025-12-03 - MIT 15.S08 Lecture 4 - Linear Algebra cont, Probability Theory (Source)]]", "[[2025-12-03 - MIT 15.S08 Lecture 5 - Probability Theory cont, Stochastic Processes I (Source)]]", "[[2025-12-03 - MIT 15.S08 Lecture 6 - Stochastic Processes I cont, Regression Analysis (Source)]]", "[[2025-12-03 - MIT 15.S08 Lecture 14 - Stochastic Processes II (Source)]]"]
---

# Wahrscheinlichkeitstheorie & Stochastische Prozesse für Finance

Formelsammlung aus den MIT-15.S08-Vorlesungen 4, 5 und 6: Momente/Verteilungen, momenterzeugende
Funktionen, Martingale, Random Walks, Markov-Ketten, CAPM-Herleitung.

## Momente und Verteilungen

- Varianz: `Var(X) = E[X²] − (E[X])²`.
- Standardisierung: `Z = (X − μ)/σ` → `E[Z]=0`, `Var(Z)=1`.
- Skewness (Schiefe): `γ = E[Z³]` (Asymmetrie der Verteilung).
- Kurtosis (Wölbung): `κ = E[Z⁴]` — für die Normalverteilung ist `κ = 3` (Exzess-Kurtosis =
  `κ − 3`); höhere Kurtosis = fettere Tails als normal.
- Normalverteilungsdichte: `f(x) = 1/(σ√(2π)) · exp(−(x−μ)²/(2σ²))`.
- Lognormalverteilung: `Y = e^X` mit `X ~ N(μ, σ²)` → `Y` lognormal(μ, σ²) — Standardmodell für
  Preise (immer positiv), Log-Preise/Log-Returns als normal angenommen.
- Momenterzeugende Funktion (MGF): `M_X(t) = E[e^{tX}]`. Eindeutigkeit: identische MGFs ↔
  identische Verteilungen. Existiert nicht für alle Verteilungen (Gegenbeispiel: Cauchy-Verteilung
  hat weder endlichen Mittelwert noch Varianz) — Charakteristische Funktion `E[e^{itX}]` existiert
  dagegen immer.
- Kovarianz/Korrelation: `Cov(X,Y) = E[(X−μx)(Y−μy)]`, `Korr(X,Y) = Cov(X,Y)/(σx·σy)`.
  Nullkorrelation ⇏ Unabhängigkeit, sagt nur "keine lineare Abhängigkeit".
- Kovarianzmatrix eines Zufallsvektors `X`: `Σ = E[(X−μ)(X−μ)ᵀ]`. Varianz einer Linearkombination
  `Y = aᵀX`: `Var(Y) = aᵀΣa = Σᵢ Σⱼ aᵢaⱼΣᵢⱼ`.
  **Diversifikationsformel**: bei `n` unkorrelierten, gleich gewichteten (`a=1/n`), gleich-
  varianten Assets ist `Var(Y) = σ²/n` — Risiko sinkt mit `1/n`, nicht mit `1/√n` (das gilt für die
  Standardabweichung).
- Zentraler Grenzwertsatz: `Zₙ = (1/√n)·Σᵢ Xᵢ → N(0, σ²)` für i.i.d. `Xᵢ` mit `E[Xᵢ]=0`,
  `Var(Xᵢ)=σ²`, bewiesen über Konvergenz der MGFs.

## Martingale und Random Walks

- Martingal-Definition: `E[Mₙ | M₁,...,Mₙ₋₁] = Mₙ₋₁` (die beste Vorhersage der Zukunft ist der
  letzte beobachtete Wert).
- Einfacher Random Walk `Sₙ = Σᵢ Xᵢ` (i.i.d., `E[Xᵢ]=0`) ist ein Martingal;
  `S²ₙ − n·σ²` ist ebenfalls ein Martingal (Varianz-Kompensations-Martingal).
- **Gambler's-Ruin** (fairer Münzwurf, Schritte ±1): Wahrscheinlichkeit, zuerst `+A` statt `−B` zu
  erreichen: `P(+A zuerst) = B/(A+B)`. Erwartete Spieldauer bis zum Stopp: `E[τ] = A·B`.
- **Verzerrter Random Walk** (`p` = Wahrscheinlichkeit für `+1`, `q=1−p` für `−1`): über eine
  multiplikative Martingal-Konstruktion mit MGF `φ(λ) = p·e^λ + q·e^{−λ}` folgt
  `P(+A zuerst) = ((q/p)^B − 1) / ((q/p)^{A+B} − 1)`.
- Stopping-Time-Theorem: für eine Stoppzeit `τ` bleibt `E[M_τ] = E[M₀]`, sofern gewisse
  Regularitätsbedingungen gelten — der zentrale Hebel, mit dem obige Formeln hergeleitet werden.

## Markov-Prozesse

- Markov-Eigenschaft: `P(Xₜ | Xᵤ, u<s) = P(Xₜ | Xₛ)` für `u<s<t` — die Zukunft hängt nur vom
  letzten Zustand ab, nicht vom Pfad dorthin.
- Stationäre Übergangsmatrix `P` (zeitunabhängig): `n`-Schritt-Übergangswahrscheinlichkeiten sind
  `Pⁿ` (Matrixpotenz).
- Anwendungsbeispiele aus den Vorlesungen: Credit-Rating-Migrationsmatrizen (AAA→AAA nur 43%
  Verbleibwahrscheinlichkeit über ein Jahr), Aktienkurs-Zustandsfolgen (Up/Down-Tagessequenzen).

## CAPM-Herleitung über Nutzenmaximierung

- Ein-Perioden-Modell: Agent maximiert `E[U(W̃)]` mit `W̃` = Endvermögen als Funktion der
  Positionsgröße im riskanten Asset. Über Stein's Lemma (für gemeinsam normalverteilte
  Zufallsvariablen `Y`: `Cov(g(Y),Y) = E[g'(Y)]·Var(Y)`) lässt sich die Optimalitätsbedingung
  explizit lösen.
- Für konstante absolute Risikoaversion (`U(w) = −e^{−Aw}`): Preis eines Assets =
  diskontierter Erwartungswert **minus** Risikoabschlag proportional zu `A` und `Var`.
- Marktgleichgewicht führt zur **Sicherheitsmarktlinie**:
  `E[Rᵢ] = Rf + βᵢ·(E[R_m] − Rf)`, mit `βᵢ = Cov(Rᵢ, R_m) / Var(R_m)`.
  `βᵢ` ist exakt der Regressionskoeffizient von `Rᵢ − Rf` auf `R_m − Rf` — Brücke zu
  [[Regressionsanalyse für Finance]].

## Brownsche Bewegung — formale Definition (Lecture 14)

- Definierende Eigenschaften: `B_0=0`, Inkremente `B_{t+Δt}−B_t ~ N(0, σ²Δt)`, disjunkte Inkremente
  sind unabhängig, Pfade sind stetig. Markov-Eigenschaft: die bedingte Verteilung von `B_{t+Δt}`
  gegeben der gesamten Vergangenheit hängt nur von `B_t` ab.
- Konstruktion als Grenzwert: der normierte Random Walk (Partialsummen von i.i.d. Schritten mit
  Mittel 0, Varianz 1, skaliert mit `1/√n`) konvergiert für `n→∞` gegen Brownsche Bewegung —
  **unabhängig von der Verteilung der einzelnen Schritte** (Bernoulli- und Gauss-Schritte liefern
  denselben Grenzprozess). Das rechtfertigt Brownsche Bewegung als Modell für Preisprozesse, deren
  Mikrostruktur-Schritte nicht notwendig normalverteilt sind.
- **Reflection Principle**: der um ein Niveau `x` gespiegelte Pfad hat dieselbe Wahrscheinlichkeit
  wie der Originalpfad. Daraus folgt `P(max_{s≤t} B_s > x) = 2·P(B_t > x)` — das Maximum einer
  Brownschen Bewegung lässt sich über die Endwertverteilung berechnen, ohne den gesamten Pfad zu
  betrachten.
- **First-Passage-/Hitting-Time-Dichte**: durch Differenzieren der obigen Formel nach `t` ergibt
  sich die Dichte der Zeit, zu der ein Niveau `x` erstmals erreicht wird — je höher das Zielniveau,
  desto breiter gestreut die Trefferzeit.
- Erweiterungen: **Absorbed Brownian Motion** (Prozess bleibt bei 0 "kleben", sobald 0 erreicht ist
  — Modell für den Bankrott-Fall bei Aktienkursen), **Brownian Bridge** (an beiden Enden fixierter
  Pfad, `X_t = B_t − t·B_1`, taucht bei normierten empirischen Verteilungsfunktionen auf).
- **Probability Integral Transform**: für jede stetige Zufallsvariable `Y` mit CDF `F_Y` ist
  `F_Y(Y)` gleichverteilt auf `[0,1]` — Grundlage für Modell-Diagnostik (Test, ob eine angenommene
  Verteilung zu den Daten passt).
- **Laplace-Verbindung**: wird Brownsche Bewegung zu zufälligen (exponentialverteilten) statt
  festen Zeitabständen beobachtet, sind die Inkremente Laplace- statt normalverteilt — passt
  empirisch besser zu täglichen S&P-500-Renditen, siehe [[Volatilitätsmodelle (GARCH & Co)]].
- **Adaptierte Prozesse**: eine Handelsstrategie `Y_t`, die von einem Preisprozess `X_t` abhängt,
  muss "adaptiert" sein — `Y_t` darf nur von Information bis Zeitpunkt `t` abhängen (formale
  Fassung von "kein Lookahead"). Direkte Brücke zur Martingal-Theorie: adaptierte Transformationen
  eines Martingals bleiben unter bestimmten Bedingungen Martingale.

## Bezug zu diesem Projekt

- Martingal-/Random-Walk-Theorie ist die formale Grundlage für "kein Lookahead, keine
  vorhersagbare Drift" — direkt relevant für die Selbstchecks in `algo/selfcheck.py`. Der Begriff
  "adaptierter Prozess" (Lecture 14) ist die mathematisch präzise Fassung derselben Regel, die in
  [[Algo-Trading: Arbeitsstandards]] als "nur `bars[t<=when]`" formuliert ist.
- Markov-Ketten für Bar-Zustandsfolgen (Up/Up/Down etc.) sind eine unmittelbare, noch nicht
  gebaute Backtest-These für `algo/signals.py`, siehe [[Quant-Finance-Formeln für den MNQ-Algo (laufend)]].
- CAPM-β-Formel und Diversifikationsformel `σ²/n` sind die theoretische Basis für
  [[Portfolio-Management & Sizing (Gain-Loss-Ratio)]].
