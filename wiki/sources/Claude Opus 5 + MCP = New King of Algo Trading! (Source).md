---
tags: [source, algo-methodology, agentic-workflow]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[Claude Opus 5 + MCP = New King of Algo Trading!]]"]
---

# Claude Opus 5 + MCP = New King of Algo Trading!

YouTube-Transkript, Kanal "Algo-trading with Saleh", veröffentlicht 2026-07-25. Kein
ICT/SMC-Material — algo-methodology-Domäne, wie
[[How I Develop Trading Strategies (Source)]]. Demonstriert Claude Opus 5 (per Claude Code +
Jesse-MCP-Server) beim eigenständigen Entwickeln, Backtesten und Validieren einer
ETH/USDT-Trendfolge-Strategie (`ETHSTPullback30m`: Supertrend + EMA-Trendfilter auf 30m,
4h-Anchor-Timeframe).

## Zusammenfassung

Der im Video gezeigte Prompt-Workflow ist eine konkrete Vorlage für "KI entwickelt + validiert
eine Handelsstrategie eigenständig", inklusive expliziter Validierungsreihenfolge: erst
Signifikanztest der reinen Entry-Regel (Rule Significance Test, RST), erst danach der Rest der
Strategie (Sizing/Stop/Ziel), erst danach Optimierung, erst danach Monte-Carlo-Overfit-Check,
erst danach Mehrperioden-Validierung. Kein Schritt wird übersprungen oder vorgezogen.

## Kernpunkte

- **Prompt-Vorgabe erzwingt Validierungsreihenfolge**: "validate the result using a statistical
  significance test before writing the full strategy to ensure the entry rules are not pure
  noise. Only proceed if the strategy's metrics demonstrate genuine statistical significance."
  Erst danach Optimierung, erst danach Monte-Carlo-Simulation gegen Overfitting.
- **Rule Significance Test (RST)** — siehe [[Rule Significance Test (RST)]] — wird VOR
  Position-Sizing/Stop/Ziel ausgeführt: "if the entry rules of the strategy don't have an actual
  edge, then everything else that we do is pointless." Testet also nur das reine Entry-Signal auf
  Zufall/Rauschen, isoliert vom Rest der Strategie.
- **Monte-Carlo-Heuristik gegen Overfitting**: originaler Backtest-Sharpe-Ratio sollte nahe am
  **Median** der simulierten Verteilung liegen, nicht am oberen Rand. Konkretes Beispiel im
  Video: Original-Sharpe 1,62, Median der Simulationen 1,93 (Original UNTER dem Median) → gilt
  als starkes Zeichen gegen Overfitting. Läge das Original stattdessen am oberen Ende der
  Verteilung (z.B. bei den besten 5%), wäre das ein Zeichen für reines Glück im Backtest statt
  echter Robustheit.
- **Mehrperioden-Validierung**: Strategie wird nicht nur auf dem Zielzeitraum (seit Jahresanfang),
  sondern zusätzlich auf 2,5 und 5,5 Jahren Historie gebacktestet. Kennzahlen bleiben über alle
  drei Zeiträume in ähnlicher Größenordnung (Sharpe 1,68 / 1,35 / 1,34) — als zusätzliches
  Robustheitsindiz gewertet, unabhängig vom RST/Monte-Carlo.
- **Portfolio unkorrelierter Strategien statt Einzelstrategie**: explizit begründet mit
  Drawdown-Perioden von bis zu 205 Tagen ("max underwater period") und psychologischer
  Tragbarkeit (Winrate nur 27–31%, aber hohes Win/Loss-Verhältnis ~3,8–3,95) — eine zweite,
  unkorrelierte Strategie soll in Verlustphasen der ersten gegensteuern und Sharpe/Max-Drawdown
  des Gesamtportfolios verbessern.
- **Agentic-Workflow-Beobachtung**: das Modell schrieb mehrere Versionen (v1–v5) der Strategie,
  bis die Kriterien (Sharpe ≥ 1,5) erfüllt waren, ohne Zwischen-Rückfrage ("Continue until you
  find strategies that fully meet the criteria requested. Do not prompt me in the meanwhile.") —
  vollautonome Iteration bis zum Erfüllen einer vorab quantifizierten Erfolgsschwelle.
- **Nicht 1:1 auf dieses Projekt übertragbar**: Jesse ist ein Krypto-Backtesting-Framework
  (ETH/USDT, andere Marktstruktur/Handelszeiten als MNQ-Futures), RST ist ein Jesse-internes
  Feature, keine öffentlich dokumentierte generische Formel im Transkript selbst. Übertragbar ist
  die **Methodik/Reihenfolge**, nicht der konkrete Jesse-Code.

## Bezug zu diesem Projekt

Bestätigt von außen dieselbe Grundhaltung wie
[[Algo-Trading: Arbeitsstandards]]/[[Vier-Stufen-Strategieentwicklung (Masters)]]: Validierung
vor Vertrauen in eine Kennzahl, Monte-Carlo-Vergleich original-vs-Verteilung als Overfitting-
Warnsignal (deckt sich mit `algo/validate.py::monte_carlo()`). **Neu gegenüber dem bisherigen
Wiki-Stand**: der Zwischenschritt "teste zuerst NUR die Entry-Regel auf Signifikanz, bevor
Sizing/Stop/Ziel überhaupt entworfen werden" (siehe [[Rule Significance Test (RST)]]) — in
`algo/rules.py`/`algo/backtest_bt.py` bisher nicht als eigener Schritt vorhanden, dort wird direkt
die vollständige `TradeSetup`-Regel gebacktestet. Kandidat für einen künftigen Zwischenschritt vor
neuen Regeln, kein akuter Backlog-Punkt.
