---
tags: [synthesis, algo-methodology, risikomanagement, backtest]
created: 2026-08-12
updated: 2026-08-12
sources: ["[[Risikomanagement (1% pro Trade)]]", "[[Kelly-Criterion & Value-at-Risk (Money Management)]]"]
---

# Risk-Management-Vergleich (laufend)

**Generiert** von `algo/backtest_risk_compare.py MNQ` -- ueberschreibt sich bei jedem Lauf komplett, kein manuell gepflegter Inhalt (siehe CLAUDE.md "(laufend)"-Muster). Gleiche Silver-Bullet-Signale, nur die Positionsgroesse variiert zwischen den drei Modulen (siehe [[../algo/README.md|algo/README.md]]). Drawdown-Kill-Switch (15%) laeuft bei allen drei mit.

| Modul | Equity Final $ | Max DD % | Win Rate % | Profit Factor | Trades | Echte $-P&L | Dubious % | VaR95 $ | ES95 $ |
|---|---|---|---|---|---|---|---|---|---|
| fixed | 81166 | -20.5 | 13.6 | 0.76 | 22 | -28190 | 0.0 | 11414 | 11414 |
| garch | 84269 | -17.4 | 13.6 | 0.76 | 22 | -21427 | 0.0 | 9486 | 9486 |
| kelly | 86235 | -15.5 | 14.3 | 0.88 | 21 | -18706 | 0.0 | 6978 | 6978 |
