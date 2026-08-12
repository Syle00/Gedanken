---
tags: [concept, quant-finance, stochastic-calculus, ito, sde, mit-ocw]
created: 2026-08-12
updated: 2026-08-12
sources: ["[[2025-12-03 - MIT 15.S08 Lecture 24 - Stochastic Calculus (Source)]]", "[[2025-12-03 - MIT 15.S08 Lecture 25 - Stochastic Calculus cont, Stochastic Differential Equations (Source)]]"]
---

# Stochastische Analysis (Itô-Kalkül & SDEs)

Formelsammlung aus MIT-15.S08-Lectures 24 und 25 (Peter Kempthorne): Itô-Integral, Itô-Formel,
stochastische Differentialgleichungen (SDEs). Mathematisches Fundament für
[[Black-Scholes & Risikoneutrale Bewertung]]; baut auf der Brownschen-Bewegungs-Formalisierung in
[[Wahrscheinlichkeitstheorie & Stochastische Prozesse für Finance]] auf.

## Itô-Integral — warum ein neuer Integralbegriff nötig ist

Ein gewöhnliches Riemann-Integral funktioniert nicht für Integranden bezüglich Brownscher Bewegung,
weil `B_t` nirgends differenzierbar ist und unendliche Variation hat. Das Itô-Integral
`∫₀ᵀ f(s,B_s) dB_s` wird stattdessen als Grenzwert von Treppenfunktions-Approximationen definiert,
wobei der Integrand an der **linken** Intervallgrenze ausgewertet wird (nicht-antizipierend/
"nonanticipatory") — diese Konvention ist der entscheidende Unterschied zu gewöhnlicher Integration
und erzwingt den zusätzlichen Korrekturterm in Itô's Formel.

Schlüsselresultat am einfachsten Beispiel: `∫₀ᵀ B_s dB_s = ½B_T² − ½T`, **nicht** `½B_T²` wie bei
gewöhnlicher Integration (`∫x dx = x²/2`). Der Korrekturterm `−½T` kommt aus der quadratischen
Variation der Brownschen Bewegung (`(dB_t)² = dt`, siehe unten).

## Itô's Formel (Itô's Lemma)

**Eindimensional** (`f` zweimal stetig differenzierbar):
`df(B_t) = f'(B_t)·dB_t + ½·f''(B_t)·dt`

**Zweidimensional** (`f(t,x)`, Standardform für Preisprozesse):
`df(t,B_t) = [∂f/∂t + ½·∂²f/∂x²]·dt + ∂f/∂x·dB_t`

Kernidee: die Taylor-Entwicklung zweiter Ordnung wird nicht wie in der gewöhnlichen Analysis nach
der ersten Ordnung abgebrochen, weil `(dB_t)²` von derselben Größenordnung wie `dt` ist (nicht
vernachlässigbar klein wie in deterministischer Rechnung). Merkregel: `(dt)²=0`, `dt·dB_t=0`,
`(dB_t)²=dt` — diese drei Regeln ersetzen die gewöhnliche Kettenregel im stochastischen Kalkül.

**Anwendung**: die Itô-Formel lässt sich "rückwärts" nutzen, um Itô-Integrale zu lösen — ist `F`
die Stammfunktion von `f`, dann gilt `∫₀ᵀ f(B_s)dB_s = F(B_T) − ½∫₀ᵀ f'(B_s)ds`.

## Geometrische Brownsche Bewegung — Log-Transformation

Für `dP_t = μ·P_t·dt + σ·P_t·dB_t` liefert Itô's Formel angewendet auf `log(P_t)`:

`d(log P_t) = (μ − σ²/2)·dt + σ·dB_t`

Der Log-Preis folgt also einer Brownschen Bewegung mit Drift `μ* = μ − σ²/2` — der bereits in
[[Volatilitätsmodelle (GARCH & Co))]] genannte "Volatility Drag". Konsequenz: `E[P_T] = P_t·e^{μ(T−t)}`
(kein Drag im Erwartungswert des Preises selbst), aber die annualisierte Log-Rendite hat
Erwartungswert `μ−σ²/2`, nicht `μ`. Bei hoher Volatilität relativ zum Drift (`μ < σ²/2`) geht der
Prozess mit Wahrscheinlichkeit 1 gegen 0, obwohl der Erwartungswert exponentiell wächst — ein
scheinbares Paradox, das erklärt, warum viele Einzelaktien langfristig gegen 0 tendieren, während
der Mittelwert über viele Aktien wächst.

## Black-Scholes-PDE über Itô-Kalkül (alternative Herleitung)

Dieselbe PDE wie in [[Black-Scholes & Risikoneutrale Bewertung]], hier direkt über Itô's Formel auf
den Derivatepreis `G_t=f(P_t,t)` angewendet und ein risikofreies Portfolio (`−G_t` plus
`∂G/∂P` Anteile Underlying) konstruiert, dessen Wertänderung gleich dem risikofreien Zins sein
muss. Ergebnis identisch: `∂f/∂t + ½σ²P²·∂²f/∂P² = rf − rP·∂f/∂P`.

## Existenz & Eindeutigkeit von SDE-Lösungen

Für `dX_t = μ(t,X_t)dt + σ(t,X_t)dB_t` garantiert die **Lipschitz-Bedingung**
(`|μ(t,x)−μ(t,y)| + |σ(t,x)−σ(t,y)| ≤ K|x−y|`) zusammen mit einer linearen Wachstumsbedingung
Existenz und (fast-sichere) Eindeutigkeit der Lösung — die formale Voraussetzung dafür, dass ein
SDE-Modell überhaupt wohldefiniert ist.

## Ornstein-Uhlenbeck-Prozess (Mean-Reversion-SDE)

`dX_t = −λ·(X_t − θ)·dt + σ·dB_t` (Drift proportional zur Abweichung vom Mittelwert `θ`, statt
konstant) — das SDE-Analogon zum AR(1)-Prozess aus [[Zeitreihenanalyse für Finance]] in stetiger
Zeit. In der Finance-Literatur als Vasicek-Zinsmodell bekannt. Löst sich über die
Koeffizientenvergleichs-Methode (Ansatz als Produktprozess); besitzt eine **stationäre
Grenzverteilung** mit konstantem Mittelwert und konstanter Varianz (ergodische Eigenschaft) — im
Gegensatz zur nicht-stationären Brownschen Bewegung mit konstantem Drift.

## Bezug zu diesem Projekt

- Geometrische Brownsche Bewegung ist die **Nullhypothese/Baseline** für "ist der Preis
  vorhersagbar": ein `algo/rules.py`-Setup muss sich statistisch gegen genau dieses driftlose
  (bzw. konstant-drift-behaftete) Martingal-Modell abheben. Rein konzeptuelle Grundlage, nicht
  direkt codierbar — siehe [[Quant-Finance-Formeln für den MNQ-Algo (laufend)]].
- Der Ornstein-Uhlenbeck-Prozess liefert die stetige-Zeit-Entsprechung zu
  [[Halbwertszeit der Mean Reversion & Kointegration (Chan)]] (`−log(2)/λ` als Lookback-Parameter)
  — beide Formeln beschreiben denselben Mean-Reversion-Mechanismus, einmal diskret (Chan/AR(1)),
  einmal stetig (Itô-SDE). Keine neue Handlungsanweisung, aber eine zusätzliche mathematische
  Absicherung der bestehenden Formel.
