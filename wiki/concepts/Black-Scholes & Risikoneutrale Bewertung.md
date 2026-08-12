---
tags: [concept, quant-finance, derivate, black-scholes, mit-ocw]
created: 2026-08-12
updated: 2026-08-12
sources: ["[[2025-12-03 - MIT 15.S08 Lecture 21 - Black-Scholes Formula, Risk Neutral Valuation (Source)]]", "[[2025-12-03 - MIT 15.S08 Lecture 25 - Stochastic Calculus cont, Stochastic Differential Equations (Source)]]"]
---

# Black-Scholes & Risikoneutrale Bewertung

Formelsammlung aus MIT-15.S08-Lecture 21 (Vasily Strela) und Teilen von Lecture 25 (Peter
Kempthorne): Replikationsargument, risikoneutrales Maß, Herleitung der Black-Scholes-PDE. Nutzt
[[Stochastische Analysis (Itô-Kalkül & SDEs)]] als mathematisches Fundament.

## Grundidee: Replikation statt Wahrscheinlichkeitsschätzung

Kernaussage der Vorlesung (illustriert am Pferdewett-Beispiel): ein Buchmacher, der Quoten nach dem
Marktverhalten statt nach eigenen Wahrscheinlichkeitsschätzungen setzt, kann sich **risikofrei**
absichern. Übertragen auf Derivate: der Preis eines Derivats hängt **nicht** von der realen
Wahrscheinlichkeit künftiger Kursbewegungen ab, sondern einzig davon, ob sich sein Payoff aus
handelbaren Instrumenten replizieren lässt. Das ist der zentrale konzeptionelle Bruch, den
Black-Scholes-Merton 1973 einführten.

## Diskretes Ein-Schritt-Modell

- Forward: `F_0 = 0` (kostenlos zu Beginn), Payoff `S_T − K`. Replikation durch Kauf des Underlyings
  auf Kredit liefert bei Zinssatz 0: `K = S_0` (Strike = aktueller Preis).
- **Risikoneutrale Wahrscheinlichkeit** `P_n`: die (fiktive) Wahrscheinlichkeit, unter der der
  aktuelle Preis exakt dem diskontierten Erwartungswert des künftigen Preises entspricht,
  `S_0 = P_n·S_1 + (1−P_n)·S_2`. Sie muss **nicht** mit der realen Wahrscheinlichkeit
  übereinstimmen.
- Call-Option-Replikationsportfolio: `a` Anteile Aktie + `B_0` Cash, gelöst aus zwei Gleichungen
  (Payoff-Gleichheit in beiden Endzuständen). Preis `C_0 = a·S_0 + B_0` — identisch mit dem
  Erwartungswert des Payoffs unter `P_n`.

## Black-Scholes-Differentialgleichung (Herleitung über Delta-Hedging)

Für `dP_t = μ·P_t·dt + σ·P_t·dW_t` und eine Derivatepreisfunktion `G_t = f(P_t, t)`: ein Portfolio
aus **kurzem** Derivat plus `∂G/∂P` Anteilen des Underlyings eliminiert den Brownschen-Bewegungs-
Term (Delta-Hedge). Da das resultierende Portfolio risikofrei ist, muss es mit dem risikofreien
Zinssatz `r` wachsen. Gleichsetzen liefert die **Black-Scholes-PDE**:

`∂f/∂t + ½·σ²·P²·∂²f/∂P² = r·f − r·P·∂f/∂P`

Zentrale Eigenschaften:

- Die Gleichung hängt **nicht vom realen Drift `μ`** ab — nur von der Volatilität `σ` und dem
  risikofreien Zins `r`. Das ist der mathematische Kern der risikoneutralen Bewertung.
- `a = ∂f/∂P` ist gleichzeitig die Hedge-Ratio (Delta) — Replikationsstrategie und
  Hedging-Strategie sind dieselbe Größe.
- Randbedingungen variieren je Kontrakt: Call bei Verfall `max(P_T−K, 0)`, Put `max(K−P_T, 0)`,
  bei `P→0` bzw. `P→∞` je nach Optionstyp.
- Die PDE ist eine Form der Wärmeleitungsgleichung (Diffusionsgleichung) — durch Variablenwechsel
  (Zeitumkehr, Skalierung) direkt darauf zurückführbar, siehe
  [[Stochastische Analysis (Itô-Kalkül & SDEs)]].

## Risikoneutrales Maß im Lognormal-Fall

Unter dem risikoneutralen Maß gilt `μ = r` (der reale Drift wird durch den risikofreien Zins
ersetzt). Der Preis eines Derivats ist dann der diskontierte Erwartungswert seines Payoffs unter
dieser Verteilung — äquivalent zur PDE-Lösung, aber oft einfacher zu berechnen (Integration statt
PDE-Lösung).

## Put-Call-Parität als modellfreies Ergebnis

`Call − Put = S_t − K·e^{−r(T−t)}` — gilt **unabhängig von der Kursdynamik** (nicht nur unter
Lognormal-Annahme), weil ein Long-Call/Short-Put-Portfolio bei Verfall exakt einem Forward-Kontrakt
entspricht. Abweichungen von dieser Gleichung sind eine reine Arbitrage-Gelegenheit — in der
Vorlesung anhand realer Apple/IBM-Optionsdaten bestätigt (Daten liegen exakt auf der Geraden).
Zusätzlich: die implizite Volatilität ist über Strikes hinweg **nicht konstant** (Volatility Smile)
— ein empirischer Beleg, dass reine Lognormal-Dynamik die Realität nicht vollständig erfasst.

## Bezug zu diesem Projekt

- **MNQ ist ein Future, kein Optionskontrakt** — Black-Scholes-PDE und risikoneutrale Bewertung
  sind für die aktuelle `algo/`-Strategie (Layer 0, kein Optionshandel) nicht direkt anwendbar.
  Siehe [[Quant-Finance-Formeln für den MNQ-Algo (laufend)]] für die explizite Einordnung als
  "aktuell nicht direkt anwendbar, Notiz für falls Optionsstrategien auf NQ-Futures dazukommen".
- Konzeptionell übertragbar ist die **Replikations-/No-Arbitrage-Denkweise**: bevor ein
  Backtest-Ergebnis als "Edge" gilt, sollte geprüft werden, ob es nicht durch ein einfacheres,
  risikofreies Konstrukt (z.B. Trendfolge plus Finanzierungskosten) reproduzierbar wäre.
