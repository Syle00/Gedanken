---
tags: [source, algo-methodology, book]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[Successful Algorithmic Trading]]"]
---

# Successful Algorithmic Trading

Buch (PDF, 208 Seiten, LaTeX/QuantStart-Eigenverlag) von **Michael Halls-Moore**, Gründer von
QuantStart. Kein ICT/SMC-Material — algo-methodology-Domäne, wie
[[How I Develop Trading Strategies (Source)]]. Rohquelle:
`raw/Successful Algorithmic Trading.pdf`. Umfassendes Referenzwerk zum vollständigen
Algo-Trading-Stack in Python: von der Strategiefindung über Datenhaltung, Statistik/Modellierung,
Performance-/Risikomanagement bis zur Event-Driven-Backtest-Engine.

## Buchstruktur (6 Teile)

1. **Introducing Algorithmic Trading** — was Algo-Trading ist, Vor-/Nachteile, wissenschaftliche
   Methode als Arbeitsweise.
2. **Trading Systems** — Backtesting-Grundlagen und -Biases (siehe
   [[Backtesting-Biases (Optimisation, Look-Ahead, Survivorship, Cognitive)]]), Ausführungsinfra-
   struktur, Strategie-Sourcing/-Bewertung.
3. **Data Platform Development** — Software-Setup, Securities-Master-Datenbank-Design,
   Datenqualität/-bereinigung, Continuous-Futures-Contracts-Problematik.
4. **Modelling** — statistisches Lernen, Zeitreihenanalyse (siehe
   [[Mean-Reversion-Tests (ADF, Hurst-Exponent, Kointegration)]]), Forecasting-Klassifikatoren.
5. **Performance and Risk Management** — Kennzahlen (Sharpe, Drawdown), Risikoquellen, Money
   Management (siehe [[Kelly-Criterion & Value-at-Risk (Money Management)]]).
6. **Automated Trading** — Event-Driven-Backtest-Engine-Architektur (Event/DataHandler/Strategy/
   Portfolio/ExecutionHandler), konkrete Strategie-Implementierungen, Optimierung/Cross-Validation.

## Kernpunkte

- **Vier Backtesting-Biases als Katalog**: Optimisation Bias (Curve-Fitting), Look-Ahead Bias
  (mit drei konkreten Fehlerquellen: Technical Bugs/Off-by-one, Parameter-Berechnung auf dem
  Gesamtdatensatz, ungelaggte Maxima/Minima), Survivorship Bias, Cognitive Bias (Drawdown im
  Backtest ist psychologisch leichter zu ertragen als live — Warnung, dass eine Strategie in der
  Praxis während echter Drawdowns abgeschaltet wird, obwohl der Backtest genau das vorhersagte).
  Details: [[Backtesting-Biases (Optimisation, Look-Ahead, Survivorship, Cognitive)]].
- **Transaktionskosten-Dreiklang**: Commission, Slippage, Market Impact — explizit als häufigster
  Anfängerfehler benannt ("neglect or grossly underestimate the effects of transaction costs").
- **Exchange-Mikrostruktur-Fallstricke**: Market- vs. Limit-Order-Modellierung, OHLC-Preis-
  Konsolidierung bei Composite-Feeds (Yahoo Finance explizit als Negativbeispiel genannt — genau
  die Datenquelle, die auch `algo/fetch_yfinance.py` nutzt), Forex-ECN-Fragmentierung,
  Shorting-Constraints (SEC-Shortban 2008 als Beispiel).
- **Statistische Mean-Reversion-Tests** (ADF, Hurst-Exponent, Kointegration/Pairs-Trading) —
  Ornstein-Uhlenbeck-Prozess als mathematisches Fundament. Details:
  [[Mean-Reversion-Tests (ADF, Hurst-Exponent, Kointegration)]].
- **Kelly-Criterion & Value-at-Risk** als quantitative Money-Management-Werkzeuge, inklusive
  Warnung vor direkter Kelly-Nutzung (Ruin-Risiko wegen Nicht-Normalverteilung realer Returns →
  "Half-Kelly" als Praxis-Standard). Details:
  [[Kelly-Criterion & Value-at-Risk (Money Management)]].
- **Event-Driven-Backtest-Architektur** als Begründung, warum ein vektorisierter Backtest
  Lookahead-Bias strukturell begünstigt: die Event-Loop (Event → DataHandler → Strategy →
  Portfolio → ExecutionHandler → Backtest) zwingt jede Komponente, nur mit Daten zu arbeiten, die
  zum jeweiligen Zeitpunkt bereits eingetroffen sind. Dieses Projekt nutzt bewusst die
  PyPI-Bibliothek `backtesting` statt einer Eigenimplementierung (Reuse-first, siehe
  `algo/README.md`) — das Buchkapitel selbst ist daher eher Hintergrundverständnis als
  Bauanleitung für dieses Repo.
- **Sources-of-Risk-Katalog**: Strategy/Model Risk, Portfolio Risk (Faktor-Exposure, Korrelation
  zwischen Strategien, average-daily-volume-Limits), Counterparty Risk (Broker-Ausfall — Autor
  berichtet von einem selbst erlebten Brokerage-Bankrott), Operational Risk (Single Point of
  Failure, Record-Keeping/Steuern).

## Bezug zu diesem Projekt

Größtenteils Hintergrundwissen/Referenz statt akutem Umsetzungsauftrag — viele Buchinhalte
(Securities-Master-DB, Event-Driven-Engine von Grund auf, MySQL-Setup) sind für dieses Projekt
bereits anders gelöst (`raw/marktdaten/`-Dateistruktur statt DB, `backtesting`-Bibliothek statt
Eigenbau). Direkt anschlussfähig sind drei Themen, die im bisherigen Wiki-Stand fehlten: der
vollständige Backtesting-Bias-Katalog (Survivorship/Cognitive Bias waren bisher nicht explizit
dokumentiert, obwohl [[Algo-Trading: Arbeitsstandards]] bereits Lookahead/Optimierungs-Bias
implizit über Walk-Forward/MCPT abdeckt), die statistischen Mean-Reversion-Tests (bisher kein
Pairs-/Mean-Reversion-Ansatz im Vault, MNQ ist Single-Instrument) und Kelly/VaR als quantitative
Ergänzung zur bestehenden festen [[Risikomanagement (1% pro Trade)]]-Regel. Kein akuter
Backlog-Punkt in `algo/PLAN.md` — reines Wiki-Wissen für künftige Entscheidungen.
