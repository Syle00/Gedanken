---
tags: [concept, quant-finance, risikomanagement, statistik, yale-econ252]
created: 2026-08-12
updated: 2026-08-12
sources: ["[[2012-04-05 - Yale Econ 252 Lecture 02 - Risk and Financial Crises (Source)]]"]
---

# Value at Risk, CoVaR & Unabhängigkeitsannahme (Yale Econ 252)

Shillers Einführungsvorlesung zu Risiko/Wahrscheinlichkeit, aufgehängt an der Finanzkrise 2007ff.
**Risikomanagement-Kernseite**: die zwei Modellannahmen, deren Bruch laut Shiller die Krise
erklärt — Unabhängigkeit und Normalverteilung (dünne Tails). Direkte Brücke zu
[[Versicherung als Risikomanagement-Institution (Yale Econ 252)]] (dieselbe Schwachstelle bei
Versicherungspools) und zu [[Grenzen für Einzelrenditen & Drawdown]].

## Value at Risk (VaR) — Entstehung und Grundproblem

- VaR entstand nach dem Crash 1987: Unternehmen begannen, Kennzahlen wie "5 % Wahrscheinlichkeit,
  in einem Jahr $10 Mio. zu verlieren" zu berechnen, um Investoren zu beruhigen.
- **Grundproblem**: VaR-Berechnungen setzten implizit (relative) Unabhängigkeit der Risikofaktoren
  voraus. Die Finanzkrise zeigte, dass diese Annahme in Stresssituationen systematisch bricht —
  VaR-Schätzungen waren weltweit "zu optimistisch" relativ zum tatsächlichen Verlust.
- **CoVaR** (Brunnermeier/Princeton) als Weiterentwicklung: statt Varianz isoliert zu betrachten,
  wird explizit modelliert, dass Portfolios **in Krisenepisoden stärker mitkovariieren** als im
  Normalfall — die Kovarianz selbst ist zustandsabhängig, nicht konstant.

## Das Gesetz der großen Zahlen und sein Versagen

- Formal: bei `n` unabhängigen, identisch verteilten Schocks geht die Varianz des Mittelwerts wie
  `1/n` gegen 0 (Standardabweichung `1/√n`). Trägt das gesamte Fundament von Diversifikation UND
  Versicherung.
- **Kritischer Punkt**: "Diversifikation durch Zeit" (viele Jahre) und "Diversifikation über
  Wertpapiere" (viele Aktien) beruhen beide auf Unabhängigkeit. In der Krise 2007–2009 brach diese
  Annahme in beiden Dimensionen — Korrelationen zwischen Anlageklassen und über Zeit stiegen
  gleichzeitig stark an.

## Fat Tails statt Normalverteilung

- Klassische Finanztheorie unterstellt normalverteilte Schocks (Gauß'sche Glockenkurve, dünne
  Tails, effektiv Null-Wahrscheinlichkeit für Extremereignisse jenseits ~4 Standardabweichungen).
- **Empirischer Gegenbeweis**: Crash vom 19.10.1987 (S&P −20,47 % an einem Tag) hätte unter
  Normalverteilungsannahme eine Wahrscheinlichkeit von `10⁻⁷¹` — praktisch unmöglich, ist aber
  passiert. Ebenso der Doppel-Crash 28./29.10.1929 (−12 % zwei Tage in Folge, gefolgt vom größten
  je gemessenen Eintagesgewinn +12,53 % am 30.10.1929).
- Konzept **fat-tailed distributions** (Lévy, weitergeführt von seinem Schüler Mandelbrot):
  Verteilungen wie die Cauchy-Verteilung sehen im Zentrum wie eine Normalverteilung aus, haben aber
  deutlich höhere Extremwahrscheinlichkeiten in den Tails — mit begrenzter Stichprobe (~100
  Beobachtungen) nicht von der Normalverteilung unterscheidbar; der Unterschied zeigt sich erst in
  seltenen, aber wiederkehrenden Sprüngen.

## Idiosynkratisches vs. Markt-Risiko (Beta-Zerlegung, Praxisbeispiel Apple)

- Aktienrendite = Marktrendite (β × Marktbewegung) + idiosynkratische Rendite. Nur der
  Beta-Anteil ist systematisch, der Rest diversifizierbar.
- Praxisbeispiel Apple (2000–2010): Beta ≈ 1,45 (überproportionale Marktreaktion), aber
  idiosynkratisches Risiko dominiert die Einzelbewegungen (z. B. −5 % nach Gerüchten über Steve
  Jobs' Gesundheit im selben Monat wie der Lehman-Kollaps, obwohl der breite Markt −16 % verlor —
  ein Beispiel dafür, dass idiosynkratisches Rauschen den systematischen Effekt zeitweise
  überdecken kann).

## Bezug zu diesem Projekt

- Die Fat-Tail-Warnung ist eine direkte Ergänzung zu `algo/validate.py`/`algo/stress_test.py`:
  Normalverteilungsannahmen bei der Drawdown-Schätzung (z. B. naiver Bootstrap) unterschätzen
  systematisch Tail-Risiken — bereits als Faktor-13,65-Unterschätzung in
  [[Grenzen für Einzelrenditen & Drawdown]] dokumentiert; diese Vorlesung liefert die
  ökonomische Intuition dazu (Unabhängigkeitsbruch in Krisen).
- CoVaR-Logik ist relevant, falls `algo/` je mehrere gleichzeitig laufende Setups/Symbole hält:
  Korrelationen zwischen Strategien sind nicht konstant, sondern steigen in Stressphasen — eine
  Warnung gegen naive Diversifikationsannahmen bei Multi-Strategie-Ensembles, vgl.
  [[Ensemble-Strategie — Backtest-Ergebnis & Commission-Verzerrung (laufend)]].
