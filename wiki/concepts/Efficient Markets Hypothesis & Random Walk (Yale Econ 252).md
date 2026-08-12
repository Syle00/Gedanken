---
tags: [concept, quant-finance, risikomanagement, markteffizienz, yale-econ252]
created: 2026-08-12
updated: 2026-08-12
sources: ["[[2012-04-05 - Yale Econ 252 Lecture 07 - Efficient Markets (Source)]]"]
---

# Efficient Markets Hypothesis & Random Walk (Yale Econ 252)

Shillers Vorlesung zur Efficient Markets Hypothesis (EMH) — von ihm explizit als "Halbwahrheit"
eingeordnet, nicht als Dogma. Direkt relevant für die Grundfrage dieses Vaults: kann ein
regelbasierter Algo systematisch Edge erzielen?

## Kernthese: Halbwahrheit statt Dogma

- EMH-Kern: Marktpreise integrieren augenblicklich alle öffentlich verfügbaren Informationen; wer
  schneller handelt als der Markt, kann kurzfristig profitieren (Informationsvorsprung von
  Sekunden bis Minuten), aber **bereits bekannte** Information (z. B. gestrige Zeitungsmeldung)
  bringt keinen Edge mehr.
- Historischer Verlauf der akademischen Überzeugung: Höhepunkt der EMH-Dogmatik in den 1970ern
  (Fama 1969/1970, CRSP-Datenbank 1960 ermöglichte erstmals systematische Tests). Seither
  schrittweise Relativierung — selbst das Standardlehrbuch Brealey/Myers strich zwischen 1984 und
  2008 die Aussage "Wertpapierpreise spiegeln den wahren zugrunde liegenden Wert wider" komplett.
- Gegenbeispiel im selben Kurs: David Swensen (Yale-CIO) erzielte über 25 Jahre konsistent
  Überrendite — laut Shiller nicht durch Sharpe-Ratio-Tricks, sondern durch Fokussierung auf
  **ineffiziente** Marktsegmente (Private Equity, Venture Capital), wo Informationsasymmetrien
  real und ausnutzbar sind (siehe [[Markowitz-Portfoliotheorie & Diversifikation (Yale Econ 252)]]).

## Random Walk vs. AR(1) — der entscheidende Unterschied für Trading

- **Random Walk**: `x_t = x_{t-1} + ε_t` (ε unvorhersagbares Rauschen). Beste Prognose für die
  Zukunft ist der aktuelle Wert; keine Mean-Reversion, keine Trendfolge-Edge.
- **AR(1) / mean-reverting Prozess**: `x_t = μ + ρ(x_{t-1} − μ) + ε_t` mit `0 < ρ < 1`. Erzeugt
  eine **echte Handelsmöglichkeit**: kaufen unter dem Trend, verkaufen darüber, weil der Prozess
  systematisch zum Mittelwert zurückkehrt.
- **Simulationsbeweis im Kurs**: zufallsgenerierte Random-Walk-Linien mit Trend sehen dem echten
  S&P-500-Kursverlauf (1871–heute) verblüffend ähnlich, inklusive scheinbarer "Kopf-Schulter"-
  Muster — ein starkes Argument dafür, dass viele klassische Chart-Muster reine
  Zufallsartefakte sind ("Fooled by Randomness", Nassim Taleb).
- **Praktisch entscheidende Erkenntnis**: die reale Welt liegt vermutlich zwischen beiden
  Extremen — ein AR(1) mit `ρ` sehr nahe 1 (z. B. 0,98–0,99) ist von einem reinen Random Walk kaum
  zu unterscheiden, bietet aber theoretisch eine sehr langsame Mean-Reversion-Edge, die erst über
  Jahre bis Jahrzehnte ausgenutzt werden könnte — für Intraday-/Daytrading-Horizonte praktisch
  irrelevant.

## Sharpe-Ratio-Manipulation als Warnung vor Track-Record-Gläubigkeit

- Formaler Beweis (Goetzmann/Ibbotson/Spiegel/Welch): die statistisch optimale Strategie, um eine
  Sharpe Ratio künstlich hochzutreiben, besteht darin, die obere Tail der Renditeverteilung zu
  verkaufen (OTM-Calls schreiben) und die untere zu verdoppeln (OTM-Puts schreiben) — over-
  ausführlich in [[Markowitz-Portfoliotheorie & Diversifikation (Yale Econ 252)]] dokumentiert.
  Direkter Bezug zu diesem Vault: ein Backtest mit ungewöhnlich glatter Equity-Kurve und hohem
  Sharpe/Profit-Factor sollte aktiv auf versteckte Tail-Risk-Struktur geprüft werden.

## Bezug zu diesem Projekt

- **Zentrale methodische Konsequenz für den MNQ-Algo**: jede getestete Regel muss explizit gegen
  die Random-Walk-Nullhypothese geprüft werden (genau das leistet der bereits im Vault
  dokumentierte [[Monte Carlo Permutation Test (MCPT)]] — Random-Walk-Simulationen wie in dieser
  Vorlesung sind methodisch dasselbe Prinzip: erzeuge Zufallsdaten mit denselben statistischen
  Eigenschaften und prüfe, ob die Strategie darauf zufällig genauso gut abschneidet).
- Die AR(1)-vs-Random-Walk-Unterscheidung liefert eine konkrete, testbare Frage für
  `algo/analyze_ohlc.py`: lässt sich für MNQ-Intraday-Returns ein `ρ` deutlich unter 1 (z. B. über
  ADF-Test, siehe [[Mean-Reversion-Tests (ADF, Hurst-Exponent, Kointegration)]]) nachweisen, oder
  ist die beobachtete Autokorrelation (r=0,305 laut
  [[Statistische Muster jenseits der ICT-Konzepte (laufend)]]) im Rahmen dessen, was ein Random
  Walk mit Trend zufällig erzeugen würde?
