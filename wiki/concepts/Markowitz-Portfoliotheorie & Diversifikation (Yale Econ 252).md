---
tags: [concept, quant-finance, risikomanagement, portfolio-theorie, yale-econ252]
created: 2026-08-12
updated: 2026-08-12
sources: ["[[2012-04-05 - Yale Econ 252 Lecture 04 - Portfolio Diversification and Supporting Financial Institutions (Source)]]", "[[2012-04-05 - Yale Econ 252 Lecture 06 - Guest Speaker David Swensen (Source)]]", "[[2012-04-05 - Yale Econ 252 Lecture 20 - Professional Money Managers and their Influence (Source)]]"]
---

# Markowitz-Portfoliotheorie & Diversifikation (Yale Econ 252)

Shillers Herleitung der Markowitz'schen Portfoliotheorie (1952) aus Yale Econ 252, ergänzt um
David Swensens praktische Anwendung im Yale-Endowment. **Risikomanagement-Kernseite** dieses
Ingests. Ergänzt die bereits vorhandenen quant-finance-Seiten
[[Portfolio-Management & Sizing (Gain-Loss-Ratio)]] und die CAPM-Herleitung aus
[[Wahrscheinlichkeitstheorie & Stochastische Prozesse für Finance]] um die historische/intuitive
Herleitung: warum es **kein** "bestes Investment" gibt, sondern nur einen Risiko-Rendite-Trade-off.

## Kernidee: Es gibt kein "bestes Investment"

- Vor Markowitz (1952) glaubten Investoren, es gebe eine beste Einzelanlage ("diese Aktie hat die
  höchste Rendite, also alles rein"). Markowitz' Einsicht: mit reiner Verschuldung/Leerverkauf
  (Leverage) lässt sich aus **jeder** Einzelanlage plus risikolosem Zins **jede beliebige**
  erwartete Rendite konstruieren (Preis: proportional steigendes Risiko). Die "beste Anlage"-Frage
  ist daher falsch gestellt — es gibt nur einen Trade-off zwischen erwarteter Rendite und
  Standardabweichung.
- **Effiziente Portfoliofront (Efficient Frontier)**: Für ≥2 riskante Anlagen mit Kovarianz ist die
  Menge der Minimum-Varianz-Portfolios pro Renditeziel eine Hyperbel. Nur der **obere** Ast
  (oberhalb des Minimum-Varianz-Punkts) ist rational wählbar — jeder Punkt darunter wird von einem
  Punkt mit gleichem Risiko, aber höherer Rendite dominiert.
- **Mehr Anlageklassen verschieben die Front nach links** (weniger Risiko bei gleicher Rendite) —
  "the more the merrier". Konkretes Beispiel aus der Vorlesung: Aktien+Anleihen+Öl schlägt
  Aktien+Anleihen, weil Öl kaum mit dem Aktienmarkt korreliert ist.
- **Tangentialportfolio + risikoloser Zins**: Sobald ein risikoloses Asset existiert, ist die
  relevante effiziente Front nur noch die Gerade vom risikolosen Zins tangential an die
  Hyperbel — das **Tangentialportfolio**. Jeder Investor sollte nur eine Mischung aus
  risikolosem Asset und diesem einen Tangentialportfolio halten ("Mutual Fund Theorem") — nie ein
  suboptimales Portfolio darunter.
- **Marktportfolio = Tangentialportfolio**: Da alle rationalen Investoren dasselbe
  Tangentialportfolio wollen, muss dessen Zusammensetzung der Gesamtheit aller im Markt
  vorhandenen Assets entsprechen (Angebot = Nachfrage) — das ist die Brücke zum CAPM.

## CAPM — die intuitive Version

- **Risiko ist Kovarianz, nicht Varianz.** Kernumdenken: Ein Anleger, der viele kleine,
  unabhängige (idiosynkratische) Risiken hält, sieht diese im Portfolio wegdiversifiziert — sie
  kosten ihn nichts. Nur der Teil des Risikos, der mit dem Gesamtmarkt mitläuft (Beta,
  Regressionskoeffizient gegen den Markt), lässt sich nicht wegdiversifizieren und wird deshalb
  bepreist.
- Formel: `E(Ri) = Rf + βi·(E(Rm) − Rf)`.
- **Sharpe Ratio** = `(Portfolio-Rendite − Rf) / σ_Portfolio` — Korrektur der Rendite um Leverage.
  Entlang der Tangentiallinie konstant. Zentrale Warnung aus der Vorlesung: **Sharpe Ratio kann
  manipuliert werden**, indem man die Tail-Verteilung verkauft (Short OTM-Calls, Verkauf der
  Gewinn-Tails; Verdoppelung der Verlust-Tails über OTM-Puts) — ein Hedgefonds erzielt so viele
  Jahre eine künstlich hohe Sharpe Ratio, bis ein Tail-Event alles auslöscht (Fallbeispiel: Integral
  Investment Management, Art Institute of Chicago verlor $43 Mio.).

## Swensen-Anwendung: das "Yale-Modell"

- Drei Renditequellen für einen Portfoliomanager: **Asset Allocation** (welche Anlageklassen, in
  welchem Verhältnis — dominant, weil Security Selection und Market Timing im Aggregat
  Nullsummen- bzw. Negativsummenspiele sind, sobald Handelskosten/Gebühren abgezogen werden),
  **Market Timing** und **Security Selection**.
- **Effizienzgrad je Anlageklasse bestimmt, wo aktives Management sich lohnt**: Spread
  Top-Quartil–Bottom-Quartil über 10 Jahre: Anleihen 0,5 %, Large Caps 2 %, Auslandsaktien 4 %,
  Absolute-Return-Hedgefonds 7,1 %, Immobilien 9,3 %, Leveraged Buyouts 13,7 %, Venture Capital
  43,2 %. Konsequenz: Zeit/Ressourcen auf ineffiziente Märkte (VC, Immobilien) konzentrieren, nicht
  auf Anleihen/Large Caps versuchen zu schlagen.
- **Rebalancing als der einzige "Free Lunch"**: Dollar-gewichtete Renditen liegen bei
  Investoren-Fonds systematisch unter zeitgewichteten Renditen, weil Anleger prozyklisch
  ein-/aussteigen (Top-10-Internetfonds-Beispiel: +1,5 %/Jahr zeitgewichtet, aber −72 % der
  eingesetzten Dollar, weil das meiste Geld genau am Hoch einströmte).
- **Survivorship Bias bei Fondsbewertung**: von 30.361 US-Fonds in einer bias-freien Datenbank
  waren 11.232 (37 %) "gestorben" (meist wegen Underperformance, teils durch Fusion mit
  besseren Fonds verschleiert) — Track-Records ohne diese Korrektur sind systematisch zu positiv.

## Bezug zu diesem Projekt

- Die Effizienzgrad-Logik (Spread Top-/Bottom-Quartil je Anlageklasse) ist ein direktes Argument
  **gegen** den Versuch, hocheffiziente, viel beobachtete Zeitfenster zu schlagen, und **für**
  ICTs Fokus auf enge, weniger beobachtete Nischen-Zeitfenster (Macros) — konzeptionelle Parallele
  zu [[Algorithmic Order Flow]] und der Makro-Zeitfenster-These, nicht direkt in Zahlen übertragbar.
- Sharpe-Ratio-Manipulation via Tail-Selling ist eine **Warnung für die Interpretation eigener
  Backtest-Kennzahlen**: ein hoher Sharpe/Profit-Factor über wenige Monate kann eine verdeckte
  Tail-Risk-Position widerspiegeln (Analogon: Martingale-artiges Nachkaufen im MNQ-Backtest würde
  denselben Effekt erzeugen) — Ergänzung zu [[Grenzen für Einzelrenditen & Drawdown]].
- Survivorship-Bias-Warnung ist direkt auf Strategie-Backtests übertragbar: eine Regel, die nur
  gegen die "überlebenden" Tage/Muster in `raw/marktdaten/` getestet wird (keine ausgeschiedenen
  Kontrakte, keine strukturellen Marktbrüche), überschätzt systematisch die Robustheit — vgl.
  [[Backtesting-Biases (Optimisation, Look-Ahead, Survivorship, Cognitive)]].
