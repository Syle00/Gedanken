---
tags: [concept, quant-finance, volatilitaet, garch, mit-ocw]
created: 2026-08-12
updated: 2026-08-12
sources: ["[[2025-12-03 - MIT 15.S08 Lecture 19 - Volatility Modeling (Source)]]"]
---

# Volatilitätsmodelle (GARCH & Co)

Formelsammlung aus MIT-15.S08-Lecture 19 (Peter Kempthorne): Volatilitätsschätzer aus historischen
Preisen, Extremwert-Schätzer (Garman-Klass-Familie) und Zeitreihenmodelle für Volatilität selbst
(ARCH/GARCH). Baut auf [[Zeitreihenanalyse für Finance]] auf.

## Historische Volatilitätsschätzer

- Annualisierung: `σ_annual = σ_periode · √N` (N=252 für tägliche, 52 für wöchentliche, 12 für
  monatliche Returns) — Standardskalierung, um Volatilitäten unterschiedlicher Frequenz
  vergleichbar zu machen.
- Rollierender Schätzer über die letzten `m` Perioden: `σ̂²_t = (1/m)·Σ_{j=0}^{m-1} σ̂²_{t-j}`.
- **Exponentiell gewichteter gleitender Durchschnitt (EWMA)**:
  `σ̂²_t = (1−β)·r²_t + β·σ̂²_{t-1}` — rekursiv, gewichtet jüngere Beobachtungen stärker.
  RiskMetrics (JP Morgan, 1990er) nutzt typischerweise `β ≈ 0,94–0,97` (langsames Vergessen).

## Garman-Klass-Familie (Extremwert-Schätzer)

Nutzt Open/High/Low/Close statt nur Close-to-Close — deutlich präzisere Schätzung bei gleicher
Beobachtungszahl (Effizienzfaktor relativ zum Close-to-Close-Schätzer):

| Schätzer | Nutzt | Effizienzfaktor |
|---|---|---|
| Close-to-Close | nur Schlusskurse | 1,0 (Referenz) |
| Parkinson (High-Low) | High/Low | 5,2 |
| Garman-Klass | O/H/L/C | 6,2–8,4 (Varianten) |
| Yang-Zhang | O/H/L/C, drift-unabhängig | aktuell empfohlener Standard |

Konsequenz: mit dem Yang-Zhang-Schätzer reicht z.B. eine Woche Daten für dieselbe Präzision wie
20 Tage Close-to-Close-Daten — relevant, wenn Volatilität über kurze, sich schnell ändernde
Fenster geschätzt werden soll.

## Geometrische Brownsche Bewegung — Drift-Korrektur

Für `dS_t = μ·S_t·dt + σ·S_t·dW_t` gilt für den Log-Return pro Periode:
`μ* = μ − σ²/2` (der "Volatility Drag" — die tatsächliche erwartete Log-Rendite liegt unter dem
naiven `μ`, weil die quadratische Variation der Brownschen Bewegung einen systematischen Abzug
erzeugt). Siehe auch [[Stochastische Analysis (Itô-Kalkül & SDEs)]].

## Sprung- und Fat-Tail-Erweiterungen

- **Poisson-Jump-Diffusion**: `dS_t/S_t = μ dt + σ dW_t + J dN_t`, `N_t` Poisson-Prozess mit Rate
  `λ`. Modelliert die Rendite als Mischung aus Normal-ohne-Sprung, Normal-mit-1-Sprung, etc. —
  erklärt fette Tails, ohne exotische Verteilungen anzunehmen.
- **Laplace-Verteilung**: entsteht, wenn Brownsche Bewegung zu zufälligen (exponentialverteilten)
  statt festen Zeitabständen beobachtet wird. Dichte `∝ exp(−|x−μ|/b)` statt `exp(−(x−μ)²/2σ²)` —
  passt empirisch deutlich besser zu täglichen S&P-500-Returns als die Normalverteilung
  (Q-Q-Plot-Vergleich in der Vorlesung eindeutig zugunsten Laplace).

## ARCH/GARCH

- **ARCH(p)** (Engle): `σ²_t = α_0 + Σ_{i=1}^{p} α_i·ε²_{t-i}` — Volatilität als autoregressiver
  Prozess der quadrierten Fehler. Bedingung `α_i ≥ 0` und `Σα_i < 1` (sonst explosiv/negative
  Varianz).
- **GARCH(1,1)** (Bollerslev): `σ²_t = ω + α·ε²_{t-1} + β·σ²_{t-1}` — in der Praxis fast immer die
  beste Ordnung unter den GARCH-Modellen (sparsames Modell mit nur 3 Parametern).
  Langfristvarianz: `σ*² = ω / (1 − α − β)`.
- Diagnosehinweis: die ACF der **quadrierten** Returns (nicht der Returns selbst) zeigt bei echten
  Finanzdaten (S&P 500, FX) signifikante Autokorrelation über viele Lags — das ist der empirische
  Beleg für Volatility Clustering und die Rechtfertigung für ARCH/GARCH statt konstanter
  Volatilität.
- Residuen unter GARCH sind oft besser mit einer **t-Verteilung** (statt Gauss) modelliert — in der
  Fallstudie der Vorlesung ca. 9 Freiheitsgrade für FX-Returns.

## Bezug zu diesem Projekt

- GARCH(1,1) ist die naheliegende Grundlage für eine **dynamische Stop-Distance/Positionsgrößen-
  Regel** in `algo/rules.py` — statt eines festen ATR-Multiplikators eine laufend aktualisierte
  `σ̂_t`-Schätzung, die auf Volatilitätsschocks schneller reagiert. Konkreter Vorschlag in
  [[Quant-Finance-Formeln für den MNQ-Algo (laufend)]].
- Der Yang-Zhang-Schätzer ist mit dem vorhandenen OHLC-Datenbestand in `raw/marktdaten/` ohne
  zusätzlichen Datenbedarf sofort berechenbar (nutzt exakt die Spalten, die bereits vorliegen).
- Volatility Clustering (ACF der quadrierten Returns) ist eine eigene, von der
  Autokorrelations-These in [[Zeitreihenanalyse für Finance]] unabhängige, aber verwandte
  falsifizierbare Aussage über MNQ.
