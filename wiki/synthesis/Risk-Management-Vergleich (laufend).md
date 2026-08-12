---
tags: [synthesis, algo-methodology, risikomanagement, backtest]
created: 2026-08-12
updated: 2026-08-12
sources: ["[[Risikomanagement (1% pro Trade)]]", "[[Kelly-Criterion & Value-at-Risk (Money Management)]]"]
---

# Risk-Management-Vergleich (laufend)

**Generiert** von `algo/backtest_risk_compare.py MNQ` -- ueberschreibt sich bei jedem Lauf komplett, kein manuell gepflegter Inhalt (siehe CLAUDE.md "(laufend)"-Muster). Gleiche Silver-Bullet-Signale, nur die Positionsgroesse variiert zwischen den drei Modulen (siehe `algo/README.md`). Drawdown-Kill-Switch (15% auf die in echte Dollar umgerechnete Equity-Kurve) laeuft bei allen drei mit.

| Modul | Equity Final $ | Max DD % | Win Rate % | Profit Factor | Expectancy % | Trades | Echte $-P&L | Dubious % | VaR95 $ | ES95 $ |
|---|---|---|---|---|---|---|---|---|---|---|
| fixed | 93142 | -8.7 | 0.0 | 0.00 | -0.111 | 6 | -11002 | 0.0 | 3787 | 3787 |
| garch | 93479 | -8.4 | 0.0 | 0.00 | -0.111 | 6 | -10385 | 0.0 | 3787 | 3787 |
| kelly | 93142 | -8.7 | 0.0 | 0.00 | -0.111 | 6 | -11002 | 0.0 | 3787 | 3787 |

> ⚠️ **Kleine Stichprobe** (siehe `algo/PLAN.md`): mit nur einer Handvoll Trades je Modul sind die Equity-/Drawdown-Unterschiede zwischen den Modulen noch nicht statistisch aussagekraeftig -- Groessenordnungs-Schaetzungen, keine belastbaren Ergebnisse.
