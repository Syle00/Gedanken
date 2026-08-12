---
tags: [concept, quant-finance, portfolio-management, money-management, mit-ocw]
created: 2026-08-12
updated: 2026-08-12
sources: ["[[2025-12-03 - MIT 15.S08 Lecture 13 - Portfolio Management (Source)]]", "[[2025-12-03 - MIT 15.S08 Lecture 5 - Probability Theory cont, Stochastic Processes I (Source)]]", "[[2025-12-03 - MIT 15.S08 Lecture 11 - Regression Analysis cont (Source)]]"]
---

# Portfolio-Management & Sizing (Gain-Loss-Ratio)

Formelsammlung aus MIT-15.S08-Vorlesung 13 (Jake Xia), mit CAPM-Bezug aus Vorlesung 5/11.
Ergänzt [[Kelly-Criterion & Value-at-Risk (Money Management)]] um eine zweite, im Vault noch
nicht dokumentierte Sizing-Kennzahl (Gain-Loss-Ratio) sowie ein Crowding-/Power-Law-Modell.

## Klassische Zwei-Asset-Portfoliotheorie (Markowitz)

- Portfolio-Return: `Rp = w₁R₁ + w₂R₂` (w₁+w₂=1).
- Portfolio-Volatilität: `σp² = w₁²σ₁² + w₂²σ₂² + 2w₁w₂ρσ₁σ₂` (ρ = Korrelation zwischen Asset 1
  und 2).
- Spezialfälle:
  - `ρ=+1`: `σp = w₁σ₁ + w₂σ₂` (lineare Grenze, kein Diversifikationsgewinn).
  - `ρ=−1`: zwei lineare Äste (perfekte Diversifikation theoretisch möglich, `σp=0` erreichbar).
  - `σ₁=0` (risikofreies Asset + riskantes Asset): `Rp` linear in `σp`, Steigung
    `(R₂−Rf)/σ₂` = **Sharpe-Ratio** — das ist die Capital-Allocation-Line.
- Effiziente Front (Efficient Frontier): die obere Grenze aller erreichbaren `(σp, Rp)`-Kombinationen
  bei variierenden Gewichten — jeder Punkt darauf ist eine potenziell optimale Portfoliowahl.
- **Alpha/Beta gegen eine Benchmark**: `Rp − Rf = α + β·(R_benchmark − Rf)`,
  `β = ρ(portfolio,benchmark) · σp/σ_benchmark`.

## Rebalancing als "einziger Free Lunch"

- Beispiel mit zwei perfekt negativ korrelierten Assets (Jahr 1: Asset A verdoppelt sich, Asset B
  halbiert sich; Jahr 2: umgekehrt): eine **rebalancierte** 50/50-Position erzielt in beiden Jahren
  +25%, kumuliert `1.25 × 1.25 − 1 = 56.25%`. Eine **nicht rebalancierte** Position endet nach zwei
  Jahren exakt bei 0% Gesamtrendite (das Startkapital ist unverändert).
- Voraussetzung: die Rebalancing-Entscheidung ist nur gerechtfertigt, wenn die Erwartungswert-
  Einschätzung für beide Assets über die Zeit unverändert bleibt (gleiche Wahrscheinlichkeits-
  verteilung) — sonst ist Rebalancing eine implizite Mean-Reversion-Wette, keine reine
  Diversifikationsmaßnahme.

## Kritik an Mean-Variance-Optimierung

- Volatilität ist kein universelles Risikomaß: eine Long-Optionsposition profitiert von höherer
  Volatilität, eine Short-Optionsposition wird durch sie geschädigt — Sizing rein über σ ignoriert
  die Payoff-Asymmetrie.
- Mean-Variance-Optimierung reagiert extrem sensitiv auf kleine Schätzfehler in den
  Kapitalmarktannahmen (erwartete Rendite, Volatilität, Korrelationsmatrix) — in der Praxis oft
  instabile Lösungen ohne künstliche Constraints.

## Gain-Loss-Ratio als Sizing-Alternative

- Für jedes Investment: erwarteter Gewinn `G` und erwarteter Verlust `L` (beide als positive
  Größen definiert, z.B. `G = P(Gewinnfall)·Auszahlung_Gewinn`,
  `L = P(Verlustfall)·Auszahlung_Verlust` im diskreten Fall, bzw. im stetigen Fall
  Integrale der Auszahlungsfunktion über die Gewinn-/Verlust-Bereiche der Wahrscheinlichkeits-
  dichte).
- Sizing-/Qualitäts-Score: `Score = (G−L) / (G+L)`, äquivalent zu `1 − 2L/(G+L)`.
- Diese Formel ist **mathematisch identisch mit dem Kelly-Sizing-Anteil bei binären Wetten**
  (siehe [[Kelly-Criterion & Value-at-Risk (Money Management)]]) — Wertebereich `[−1, +1]`, direkt
  als Positionsgrößen-Anteil interpretierbar, im Gegensatz zur Sharpe-Ratio, die keine direkte
  Sizing-Aussage liefert.
- Praktischer Vorteil gegenüber Sharpe: hohe Volatilität allein verschlechtert den Score nicht
  automatisch — nur ein ungünstiges Verhältnis von erwartetem Gewinn zu erwartetem Verlust tut das.
  Der Nenner `(G+L)` normalisiert über verschiedene Investments mit unterschiedlicher Vola
  vergleichbar.

## Crowding-Feedback-Modell und Power-Law-Verteilungen

- Feedback-Schleife: Beobachtung `O` als gewichtete Summe der Akteurs-Aktionen `Sᵢ` mit
  Einflussgewicht `Aᵢ` (`dO = Σᵢ Aᵢ·dSᵢ`); Akteurs-Reaktion `dSᵢ` hängt von einem
  Reaktivitätsparameter ab, der bei steigender Beobachtungs-Volatilität zunimmt.
- Ordnungsparameter (Synchronisationsgrad) = `|Σᵢ Sᵢ| / Σᵢ|Sᵢ|` — nahe 1 bei vollständig
  synchronisierten Akteuren, nahe 0 bei unkorreliertem Verhalten. Steigt mit der Anzahl reaktiver
  Akteure, sinkt mit stärkerem Rauschterm.
- Analogie: Resonanzeffekt der London Millennium Bridge (synchronisierter Fußgängergleichschritt
  verstärkt die Schwingung) als physikalisches Bild für Markt-Bubbles/Crashes.
- Power-Law/Pareto-Verteilung `P(x) ∝ x^{−a}` statt Normalverteilung bei Vermögen, VC-Fonds-
  Renditen, Stadtgrößen — laut Vorlesung eine Konsequenz genau dieses positiven
  Rückkopplungsmechanismus (Akteure mit mehr Einfluss `Aᵢ` gewinnen bei richtigen Wetten
  überproportional mehr Einfluss dazu), nicht eines rein zufälligen Prozesses.

## Bezug zu diesem Projekt

- **Konkreter Vorschlag für `algo/backtest_ensemble.py`/`algo/validate.py`**: die Gain-Loss-Ratio
  `(G−L)/(G+L)` als zusätzliche Kennzahl neben `dubious_pct` und Profit Factor berichten — sie
  bestraft hohe Rohvolatilität nicht per se, sondern nur ein schlechtes Gewinn/Verlust-Verhältnis,
  und ist direkter auf eine Positionsgrößen-Empfehlung übertragbar als die reine Sharpe-Ratio.
- Das Rebalancing-Argument ist eine **prüfbare These** für ein Multi-Symbol-Portfolio (MNQ + ggf.
  weitere Kontrakte), sobald `algo/` mehr als ein Symbol gleichzeitig handelt — aktuell (Stand
  dieses Ingests) nur ein Layer-0-Ziel (MNQ), daher primär als Zukunftsnotiz relevant.
- Crowding-/Power-Law-Modell: ⚠️ nur sinnvoll, wenn es zu einer konkreten, testbaren Regel führt
  (z.B. "hohe realized Volatility → erhöhte Wahrscheinlichkeit von Trendfortsetzung wegen
  Akteurs-Synchronisation" als Hypothese für `algo/backtest_<these>.py`) — als reine Analyse-
  Theorie ohne Regelbezug wäre es Layer-0-Verstoß.
- Siehe auch [[Erwartungswert & Reward-to-Risk-Modell]] (ICT-Pendant zur RR/Sizing-Logik) und
  [[Kelly-Criterion & Value-at-Risk (Money Management)]] (mathematische Verwandtschaft der
  Gain-Loss-Ratio zum Kelly-Kriterium).
