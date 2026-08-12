---
tags: [synthesis, quant-finance, algo-methodology, laufend]
created: 2026-08-12
updated: 2026-08-12
sources: ["[[Lineare Algebra für Finance]]", "[[Wahrscheinlichkeitstheorie & Stochastische Prozesse für Finance]]", "[[Regressionsanalyse für Finance]]", "[[Hauptkomponentenanalyse (PCA) in der Finance]]", "[[Bond-Mathematik & Zinskurven]]", "[[Portfolio-Management & Sizing (Gain-Loss-Ratio)]]", "[[Kelly-Criterion & Value-at-Risk (Money Management)]]", "[[Zeitreihenanalyse für Finance]]", "[[Volatilitätsmodelle (GARCH & Co)]]", "[[Black-Scholes & Risikoneutrale Bewertung]]", "[[Machine Learning für Finance (Grundlagen)]]", "[[Stochastische Analysis (Itô-Kalkül & SDEs)]]"]
---

# Quant-Finance-Formeln für den MNQ-Algo (laufend)

Übergreifende Bewertung: welche Formel/Methode aus der 13-teiligen MIT-15.S08-Ingestion
(Konzeptseiten oben) sich konkret für `algo/` (Layer 0, siehe CLAUDE.md) einsetzen lässt — nicht
als allgemeine "das ist nützlich"-Aussage, sondern mit Modul, Funktion und Datenbedarf. Vorschläge,
die reines Backtesting-Spielzeug ohne Weg zu einer ausführbaren Regel wären, sind explizit als
Layer-0-Verstoß markiert. Diese Seite wird bei jeder neuen quant-finance-Erkenntnis erweitert
(Muster "(laufend)").

## PCA für Regime-Erkennung

**Was sie macht**: zerlegt einen multivariaten Datensatz in unkorrelierte Richtungen absteigender
Varianz. In der Zinskurven-Fallstudie ([[Hauptkomponentenanalyse (PCA) in der Finance]]) liefert
sie ein sauberes Level/Slope/Curvature-Zerlegungsschema für stark korrelierte Zeitreihen.

**Konkreter Vorschlag**: PCA über die letzten N Tage der OHLC-Returns von MNQ auf mehreren
Timeframes gleichzeitig (z.B. 1m-, 5m-, 15m-, 1h-Returns als Spalten derselben Datenmatrix)
könnte, analog zum Zinskurven-Level/Slope/Curvature-Muster, ein Feature für `algo/signals.py`
liefern: PC1 (~"generelle Volatilitäts-/Trendrichtung über alle Timeframes") als Regime-Indikator,
PC2/PC3 als Divergenz-Signal zwischen kurz- und langfristigem Preisverhalten (Timeframe-
Disagreement als potenzieller Kompressions-/Displacement-Vorbote). Praxisregel aus der Vorlesung
übernehmen: Eigenwert-Separation in log-Skala prüfen, bevor eine Komponente als Signal genutzt
wird — sonst reines Rauschen.

⚠️ Nur sinnvoll, wenn direkt auf eine `algo/rules.py`-taugliche Schwellenwert-Regel hinarbeitend
(z.B. "PC1-Ladung > X → Trade-Filter aktiv"), nicht als Analyse-Dashboard-Feature ohne
Entscheidungsbezug.

## Lineare Regression (OLS) für Signifikanztests statt reiner Backtest-Zahlen

**Was sie macht**: liefert nicht nur einen Punktschätzer, sondern über die t-/F-Statistik direkt
ein Signifikanzmaß, ob ein Effekt von 0 verschieden ist — siehe
[[Regressionsanalyse für Finance]] und den CAPM-Alpha-Test (`H₀: α=0`).

**Konkreter Vorschlag**: statt "Strategie X hatte über N Backtest-Tage einen positiven Return" in
`algo/validate.py` einen Regressionstest analog zum CAPM-Alpha-Test einbauen — Strategie-Return
gegen ein Markt-/Buy&Hold-Benchmark regressieren und testen, ob der Alpha-Achsenabschnitt
signifikant von 0 verschieden ist. Das ist strenger als der reine Mittelwertvergleich, den
`algo/backtest_ensemble.py` aktuell nutzt, weil es implizit für allgemeine Marktrichtung
kontrolliert.

## Kovarianzmatrix/Diversifikationsformel für Multi-Symbol-Erweiterung

**Was sie macht**: `Var(gleichgewichtetes Portfolio aus n unkorrelierten Assets) = σ²/n` (siehe
[[Wahrscheinlichkeitstheorie & Stochastische Prozesse für Finance]]) — Risiko sinkt linear mit der
Anzahl unkorrelierter Positionen, nicht mit der Wurzel.

**Konkreter Vorschlag**: sobald `algo/` mehr als ein Symbol gleichzeitig handelt (Roadmap-Punkt 1,
zweite Datenquelle/mehrere Kontrakte), liefert diese Formel die quantitative Begründung für
Positionsgrößen-Diversifikation über mehrere, möglichst unkorrelierte MNQ-Setups (z.B.
verschiedene Killzones/Macro-Fenster als separate "Assets" im Sinne dieser Formel) statt einer
einzelnen konzentrierten Tagesposition.

## Markov-Ketten für Bar-Zustandsfolgen

**Was sie macht**: modelliert Übergangswahrscheinlichkeiten zwischen diskreten Zuständen
(z.B. Up-/Down-Tage) unter der Annahme, dass nur der letzte Zustand zählt.

**Konkreter Vorschlag**: eine Markov-Kette über MNQ-5m-Bar-Zustände (Up/Down, ggf. erweitert um
"Displacement"/"Kompression") als zusätzlicher Detektor in `tools/analyze_ohlc.py` — die
Vorlesung zeigt am Beispiel Apple, dass zwei Aufwärtstage die Wahrscheinlichkeit eines dritten
erhöhen können. Das ist eine **falsifizierbare These im Sinne von CLAUDE.md** ("jede neue These
wird automatisch geloggt und gebacktestet") und wurde als solche in `algo/PLAN.md` eingetragen
(siehe Log-Eintrag zu diesem Ingest).

## Gain-Loss-Ratio als Sizing-Kennzahl neben Profit Factor

**Was sie macht**: `(G−L)/(G+L)` (siehe [[Portfolio-Management & Sizing (Gain-Loss-Ratio)]]) —
mathematisch identisch mit dem Kelly-Sizing-Anteil bei binären Wetten, bestraft aber hohe
Rohvolatilität nicht per se wie die Sharpe-Ratio.

**Konkreter Vorschlag**: als zusätzliche Kennzahl neben `dubious_pct` und Profit Factor in jedem
`algo/backtest_ensemble.py`/`algo/validate.py`-Report ausgeben — direkter interpretierbar für
eine Positionsgrößen-Entscheidung als die reine Sharpe-Ratio, weil sie bereits auf `[-1,+1]`
normiert und Kelly-artig sizing-fähig ist.

## Bond-Duration/Convexity — nicht direkt relevant für MNQ

**Was sie macht**: Preissensitivität eines Anleihe-Investments gegenüber Zinsänderungen (1. und
2. Ableitung des Preises nach dem Yield).

**Bewertung**: MNQ ist ein Aktienindex-Future, kein Zinsprodukt — Duration/Convexity im engeren
Sinn sind nicht direkt auf `algo/pnl.py` übertragbar. Relevanter Nebeneffekt: das
"Funding=Discounting"-Prinzip aus [[Bond-Mathematik & Zinskurven]] wäre ein sauberer Rahmen, um
Übernachtfinanzierungskosten für gehaltene MNQ-Positionen realistischer in `algo/pnl.py`
abzubilden — aktuell laut `algo/README.md` nicht modelliert. ⚠️ Nur sinnvoll, wenn `algo/` je
Overnight-Positionen hält (aktuell primär Intraday-fokussiert laut `algo/PLAN.md`).

## Counterparty-Risk-Optimierung (SIMM/Netzwerk-Margin) — nicht relevant

**Bewertung**: die in Lecture 10 behandelte Initial-Margin-Netzwerkoptimierung setzt ein
Multi-Bank-Netzwerk mit bilateralen Trades voraus — für einen einzelnen autonomen IBKR-Retail-
Algo ohne Interbanken-Gegenparteien-Netzwerk nicht anwendbar. Die einzige übertragbare Erkenntnis
ist die VaR/ES-Methodik, bereits in [[Kelly-Criterion & Value-at-Risk (Money Management)]]
dokumentiert.

## Stochastische Prozesse / Brownsche Bewegung

**Was sie macht**: Random-Walk-Grenzwertprozess mit normalverteilten Inkrementen, Martingal-
Eigenschaft (`E[zukünftig] = letzter Wert`).

**Bewertung**: primär eine **Nullhypothese/Baseline**, kein direktes Signal — ein profitables
`algo/rules.py`-Setup muss sich gegen genau dieses Martingal-Nullmodell abheben (kein
vorhersagbarer Drift ohne Regel). Nützlich als formaler Rahmen für `algo/selfcheck.py`: ein
Zufallssignal-Backtest sollte im Erwartungswert ein Martingal-artiges (driftloses) Ergebnis
liefern; weicht die tatsächliche Regel systematisch davon ab, ist das der eigentliche Beleg für
einen Edge — ⚠️ nur sinnvoll als Kontrollexperiment neben einer echten Regel, nicht als
eigenständiges Analyseziel.

## GARCH-Volatilitätsschätzung für dynamisches Sizing (neu, Batch 2)

**Was sie macht**: [[Volatilitätsmodelle (GARCH & Co)]] liefert mit GARCH(1,1)
(`σ²_t = ω + α·ε²_{t-1} + β·σ²_{t-1}`) eine laufend aktualisierte Volatilitätsschätzung, die auf
Volatilitätsschocks (Displacement, News) schneller reagiert als ein fester ATR-Lookback. Der
Yang-Zhang-Schätzer (Effizienzfaktor ~8 gegenüber Close-to-Close) ist mit dem vorhandenen
OHLC-Bestand in `raw/marktdaten/` ohne zusätzlichen Datenbedarf sofort berechenbar.

**Konkreter Vorschlag**: `algo/rules.py`/`algo/pnl.py` um eine GARCH(1,1)-basierte
Stop-Distance-/Positionsgrößen-Regel erweitern — statt eines festen ATR-Multiplikators eine
laufende `σ̂_t`-Schätzung, die Stop-Weite und Kontraktzahl dynamisch skaliert. Dies ist **konkret
umsetzbar**, nicht nur konzeptionell: Datenbedarf ist vollständig gedeckt.

⚠️ Noch nicht implementiert — Kandidat für `algo/backtest_garch_sizing.py` (noch nicht angelegt).

## Autokorrelations-These für MNQ-Returns (neu, Batch 2, falsifizierbare These)

**Was sie macht**: [[Zeitreihenanalyse für Finance]] liefert mit dem Box-Pierce-Test
(`BP = T·Σ R̂_j²`, χ²-verteilt) ein direktes Signifikanzwerkzeug für Autokorrelation. Die Vorlesung
zeigt empirisch unterschiedliche Autokorrelationsmuster über Anlageklassen (S&P 500 negativ bei
Lag 1 monatlich, Crude-Oil-Futures negativ/positiv bei Lag 2/3 wöchentlich, Amazon durchgehend
keine signifikante Autokorrelation) — es ist also **nicht** selbstverständlich, dass ein Future
wie MNQ Autokorrelation zeigt.

**Konkreter Vorschlag**: die Box-Pierce-/ACF-Signifikanzprüfung auf MNQ-Returns (mehrere
Timeframes: 1m/5m/15m/1h/1d) in `tools/analyze_ohlc.py` oder einem neuen
`algo/backtest_autocorrelation.py` anwenden. Das ist eine eigenständige, von der bereits
eingetragenen Markov-Ketten-These unterschiedliche, aber verwandte Prüfung — die Markov-These
testet Zustandsfolgen (Up/Down-Serien), diese hier testet die lineare Korrelationsstruktur direkt
über die ACF. Gemäß [[Algo-Trading: Arbeitsstandards]] als falsifizierbare These in `algo/PLAN.md`
eingetragen (siehe Log-Eintrag zu diesem Ingest).

## Black-Scholes/Risikoneutrale Bewertung — nicht direkt anwendbar

**Was sie macht**: [[Black-Scholes & Risikoneutrale Bewertung]] liefert die Bewertungsformel für
Optionen über Replikationsportfolios; hängt nur von Volatilität und risikofreiem Zins ab, nicht vom
realen Drift.

**Bewertung**: **MNQ ist ein Future, kein Optionsprodukt** — Black-Scholes-PDE und risikoneutrale
Bewertung sind für die aktuelle `algo/`-Strategie nicht direkt anwendbar. ⚠️ Notiz für später:
falls `algo/` künftig Optionsstrategien auf NQ-Futures (z.B. Absicherung über Puts, oder
Volatilitäts-Overlay über Optionen) dazunimmt, ist dieser Formelapparat direkt einsatzbereit.
Aktuell kein Handlungsbedarf.

## Stochastic Calculus/Itô — konzeptuelle Grundlage, nicht direkt codierbar

**Was sie macht**: [[Stochastische Analysis (Itô-Kalkül & SDEs)]] zeigt, dass geometrische
Brownsche Bewegung (die formale Fassung von "Random Walk auf Log-Preis-Skala") eine driftkorrigierte
Rendite `μ−σ²/2` hat und mit Wahrscheinlichkeit 1 gegen 0 gehen kann, obwohl der Erwartungswert
wächst.

**Bewertung**: primär eine **konzeptuelle Nullhypothese**, kein direkt codierbares Signal — wie
bereits im ersten Batch für Brownsche Bewegung allgemein festgehalten (siehe Abschnitt oben zu
"Stochastische Prozesse / Brownsche Bewegung"). Der Ornstein-Uhlenbeck-Prozess ist die
stetige-Zeit-Entsprechung zur bereits produktiv genutzten
[[Halbwertszeit der Mean Reversion & Kointegration (Chan)]]-Formel — keine neue Handlungsanweisung,
aber zusätzliche mathematische Absicherung.

## Machine-Learning-Grundlagen — Bestätigung bestehender Methodik

**Was sie macht**: [[Machine Learning für Finance (Grundlagen)]] beschreibt den
Train/Validation/Test-Split (60/20/20) und die Overfitting-Erkennungsregel (Komplexität erhöhen,
bis Validation-Performance schlechter wird).

**Bewertung**: **keine neue Methodik** — methodisch identisch mit dem bereits in `algo/validate.py`
umgesetzten Walk-Forward-/Out-of-Sample-Prinzip, siehe
[[Vier-Stufen-Strategieentwicklung (Masters)]] und
[[Cross Validation vs. Walk-Forward (Masters)]]. Dient als unabhängige Bestätigung der
bestehenden Projektdisziplin, nicht als Implementierungsauftrag. Reinforcement Learning für
Hedging ist mangels Optionsportfolio in `algo/` nicht anwendbar (siehe
[[Reinforcement Learning für Handel — Grenzen (Starke)]] für die bereits dokumentierte Skepsis
gegenüber RL als Signalgeber).

## Offene Punkte

- Markov-Ketten-These (Bar-Zustandsfolgen) noch nicht gegen `raw/marktdaten/` gebacktestet —
  siehe `algo/PLAN.md`-Log-Eintrag zu diesem Ingest, folgt in einer künftigen Session
  (`algo/backtest_markov_bars.py`, noch nicht angelegt).
- PCA-Multi-Timeframe-Feature ebenfalls noch nicht implementiert — Datenbedarf (mehrere
  Timeframes derselben Zeitspanne) ist mit dem aktuellen `raw/marktdaten/`-Bestand grundsätzlich
  gedeckt, aber ungeprüft.
- GARCH(1,1)-basierte Stop-Distance-These (Batch 2) noch nicht implementiert/gebacktestet —
  `algo/backtest_garch_sizing.py`, noch nicht angelegt.
- Autokorrelations-/Box-Pierce-These auf MNQ-Returns (Batch 2) noch nicht gebacktestet —
  `algo/backtest_autocorrelation.py`, noch nicht angelegt. Siehe `algo/PLAN.md`-Log-Eintrag zu
  diesem Ingest.
