---
tags: [concept, algo-methodology, statistics]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[Successful Algorithmic Trading (Source)]]"]
---

# Mean-Reversion-Tests (ADF, Hurst-Exponent, Kointegration)

Statistisches Werkzeug-Set, um zu prüfen, ob eine Preisreihe (oder eine Kombination mehrerer
Preisreihen) **mean-reverting** statt eines reinen Random Walk (Geometric Brownian Motion, GBM)
ist — Grundvoraussetzung für jede Mean-Reversion-Strategie. Aus
[[Successful Algorithmic Trading (Source)]] (Michael Halls-Moore). Mathematisches Fundament: eine
mean-reverting Zeitreihe lässt sich als **Ornstein-Uhlenbeck-Prozess** beschreiben — die Änderung
im nächsten Zeitschritt ist proportional zum Abstand vom historischen Mittelwert
(`dx_t = θ(µ − x_t)dt + σdW_t`).

## Augmented Dickey-Fuller (ADF) Test

Testet auf einen **Unit Root** in einem autoregressiven Modell: `Δy_t = α + βt + γy_{t−1} + …`.
Nullhypothese: `γ = 0` (Zeitserie ist Random Walk, nicht mean-reverting). Wird `γ = 0` verworfen
(Teststatistik `DFτ` negativer als der kritische Wert bei 1/5/10%), ist die nächste
Preisbewegung proportional zum aktuellen Preis — Hinweis auf Mean Reversion statt Zufallslauf.
Praxis: `p = 1` (Lag-Order) reicht meist aus, um die Nullhypothese sinnvoll zu testen (führt
selbst aber einen zusätzlichen Parameter ein). Python: `statsmodels.tsa.stattools.adfuller()`.
Buchbeispiel: Amazon-Aktie 2000–2015 verwirft die Nullhypothese NICHT (Teststatistik über allen
kritischen Werten) — Amazon verhält sich in diesem Zeitraum wie GBM, nicht mean-reverting.

## Hurst-Exponent

Alternative/ergänzende Methode über die **Diffusionsrate der Log-Preis-Varianz**:
`⟨|log(t+τ) − log(t)|²⟩ ~ τ^(2H)`. Bei GBM gilt `H = 0,5`. Interpretation:

- `H < 0,5` — Zeitserie ist mean-reverting (näher an 0 = stärker mean-reverting)
- `H = 0,5` — Zeitserie verhält sich wie GBM (Random Walk)
- `H > 0,5` — Zeitserie ist trending (näher an 1 = stärker trending)

Python-Implementierung ist eine simple lineare Regression (`polyfit`) auf log-log-skalierten
Lag-Varianzen. Buchbeispiel bestätigt die Definition an synthetischen Serien (GBM: H≈0,502,
Mean-Reverting: H≈0,0002, Trending: H≈0,958) und zeigt an Amazon (H≈0,454, nahe 0,5) dieselbe
Schlussfolgerung wie der ADF-Test: kein starkes Mean-Reversion-Signal.

## Kointegration (Pairs Trading)

Einzelne Aktien/Instrumente verhalten sich selten mean-reverting (die meisten ähneln GBM) — aber
ein **Portfolio aus zwei oder mehr korrelierten Instrumenten** kann stationär sein, selbst wenn
keines der Einzelinstrumente es ist. Klassischer "Pairs Trade": lineares Modell
`y(t) = βx(t) + ε(t)` zwischen zwei Instrumenten (Buchbeispiel: zwei Energie-Aktien AREX/WLL,
die auf ähnliche Marktfaktoren reagieren). Die Residuen `ε(t) = y(t) − βx(t)` bilden eine neue
Zeitreihe, die per ADF-Test oder Hurst-Exponent auf Stationarität geprüft wird (**Cointegrated
Augmented Dickey-Fuller Test**, CADF) — ist sie stationär, gilt das Paar als kointegriert und
handelbar (long das relativ unterbewertete, short das relativ überbewertete Instrument, bei
Rückkehr zum Mittel schließen).

## Bezug zu diesem Projekt

Bisher kein Mean-Reversion-/Pairs-Ansatz im Vault — MNQ läuft als Single-Instrument-Strategie
(Silver Bullet, Ensemble). Direkt anwendbar wäre der ADF-Test/Hurst-Exponent als **Vorab-Check**
für jede neue MNQ-basierte These, die implizit Mean-Reversion voraussetzt (z.B. Midnight-Opening-
Range-Manipulation-Rückkehr, ORG-C.E.-Füllung) — bisher werden solche Thesen nur über
Trefferquoten gebacktestet (`algo/backtest_midnight_range_*.py`), nicht vorab statistisch auf
Mean-Reversion-Charakter geprüft. Kointegration würde einen zweiten korrelierten Future
voraussetzen (Kandidat: NQ oder ES, beide bereits in `algo/pnl.py`s Punktwert-Tabelle) — aktuell
kein Backlog-Punkt, da das Projekt bewusst auf ein Einzelinstrument (MNQ) fokussiert ist (siehe
[[Algo-Trading: Arbeitsstandards]], Layer 0).
