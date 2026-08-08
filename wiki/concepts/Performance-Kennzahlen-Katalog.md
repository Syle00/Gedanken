---
tags: [concept, algo-methodology, kennzahlen, risikomanagement, referenz]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[AI in Finance and Quantitative Analysis (Source)]]", "[[Algorithmic Trading - Winning Strategies and Their Rationale (Source)]]", "[[Testing and Tuning Market Trading Systems (Source)]]"]
---

# Performance-Kennzahlen-Katalog

Was eine Backtest-Auswertung ausweisen sollte, mit den Formeln. Zusammengeführt aus dem
`ffn.calc_stats()`-Katalog in [[AI in Finance and Quantitative Analysis (Source)]], den
`backtesting.py`-Kennzahlen und den methodischen Vorbehalten aus
[[Algorithmic Trading - Winning Strategies and Their Rationale (Source)]] (Chan) und
[[Testing and Tuning Market Trading Systems (Source)]] (Masters).

> **Vorbedingung, die alles andere entwertet, wenn man sie ignoriert:** Alle Verhältniskennzahlen
> hier sind auf **Bar-Basis** zu rechnen, nicht auf Trade-Basis — sonst sind sie systematisch zu
> extrem. Masters' Beispiel: derselbe Sachverhalt ergibt trade-basiert einen Profit Factor von
> *unendlich* und bar-basiert 1,01. Siehe [[Profit pro Bar vs. pro Trade]].

## Renditekennzahlen

```
Log-Rendite pro Bar    r(t) = log(P(t)) − log(P(t−1))
                       ← durchgaengig verwenden: +10 %/−10 % heben sich exakt auf,
                         Prozentrenditen erzeugen dabei ~1 % Scheingewinn

Total Return           Π(1 + rᵢ) − 1

CAGR                   (Endwert/Startwert)^(1/Jahre) − 1
                       = Compound Annual Growth Rate

Annualisierung von Log-Bar-Renditen bei Tages-Bars:
                       Jahresrendite ≈ 25200 × mittlere Log-Bar-Rendite
                       (252 Handelstage × 100 %)
```

## Risikoadjustierte Kennzahlen

```
Sharpe Ratio           SR = (mean(r) − rf) / std(r)          annualisiert: × √252 bei Tages-Bars
                       ← bestraft Aufwaerts- und Abwaertsvolatilitaet GLEICH

Sortino Ratio          So = (mean(r) − rf) / std(r | r < 0)
                       ← nur die Abwaertsabweichung im Nenner.
                         Immer ≥ Sharpe; die Luecke misst die Schiefe der Verteilung.

Calmar Ratio           CR = CAGR / |Max Drawdown|
                       ← setzt die Rendite ins Verhaeltnis zum SCHLIMMSTEN erlebten Verlust
                         statt zur Volatilitaet — die fuer einen gehebelten Trader
                         relevantere Groesse

Profit Factor          PF = Σ(Gewinne) / |Σ(Verluste)|
                       ← Masters' bevorzugtes Optimierungskriterium: hatte in seinen
                         Tests fast immer den KLEINSTEN Trainings-Bias.
                         Beim Bootstrappen IMMER den Logarithmus nehmen.

Expectancy             E = WinRate × AvgWin − LossRate × AvgLoss
                       ← identisch mit ICTs Erwartungswertformel, siehe unten

SQN                    SQN = √n × mean(Trade-R) / std(Trade-R)     (Van Tharp)
                       ← System Quality Number; strukturell derselbe Ausdruck wie
                         Masters' t-Score √n·Mean/StdDev
```

**Der Zusammenhang, den man kennen sollte:** `SQN` und die t-Statistik aus
[[Konfidenzgrenzen für Renditen (t-Test, Bootstrap, BCa)]] sind dieselbe Größe. Und Chans
kritische Werte für `√n × tägliche Sharpe Ratio` gelten damit auch hier:

```
p-Wert       0,10    0,05    0,01    0,001
krit. Wert  1,282   1,645   2,326   3,091
```

Eine annualisierte Sharpe Ratio von 1,0 über 4 Jahre entspricht also
`√4 × 1,0 = 2,0` — knapp unter dem 1-%-Niveau.

## Drawdown-Kennzahlen

```
Max Drawdown (MDD)     max über t von  (Hochwasserstand(t) − Equity(t)) / Hochwasserstand(t)

Log-Variante           dd = max( cummax(Σr) − Σr )          absolut, auf Log-Renditen
                       dd_pct = 100 × (1 − exp(−dd))         Umrechnung in Prozent
                       ← Masters rechnet absolut: vermeidet die Willkuer eines Startkapitals
                         und funktioniert auch bei negativem Eigenkapital (gehebelte Futures)

Avg Drawdown           Mittel über alle Drawdown-Episoden
Max Drawdown Duration  laengste Zeit vom Hoch bis zum Wiedererreichen des Hochs
Avg Drawdown Days      mittlere Dauer einer Drawdown-Episode
```

> **Die Drawdown-DAUER ist eine eigenständige Kennzahl** und wird regelmäßig vergessen. Chan
> lehnt eine Strategie mit 30 % APR und Sharpe 0,3 allein wegen einer **Drawdown-Dauer von zwei
> Jahren** ab: „Very few traders have the stomach for a strategy that remains under water for two
> years." Die Tiefe sagt, wie viel man verliert; die Dauer sagt, wie lange man es aushalten muss.

## Zeitraum- und Konsistenzkennzahlen

Aus `ffn.calc_stats()` — der Teil, den `algo/` heute gar nicht ausweist:

```
Daily / Monthly / Yearly Sharpe        dieselbe Kennzahl auf verschiedenen Aggregationsstufen
Daily / Monthly / Yearly Skew, Kurt    Schiefe und Woelbung der Renditeverteilung
Best / Worst Day, Month, Year          Extremwerte
Avg Up Month / Avg Down Month          Asymmetrie der Monatsergebnisse
Win Year % / Win 12m %                 Anteil profitabler Jahre bzw. rollierender 12-Monats-Fenster
MTD / 3m / 6m / YTD / 1Y / 3Y / 5Y     rollierende Zeitraumrenditen
```

**Warum Skew und Kurtosis dazugehören:** Sie sind die Eingangsgrößen für die
Monte-Carlo-Leverage-Optimierung über das Pearson-System
([[Kelly-Formel & optimales Leverage (Chan)]]) und sie entscheiden darüber, ob ein t-Test auf die
Renditen überhaupt zulässig ist ([[Konfidenzgrenzen für Renditen (t-Test, Bootstrap, BCa)]] — ein
einziger wilder Ausreißer macht ihn wertlos).

**Warum die Aggregationsstufen auseinanderfallen können:** Im BTC-Beispiel der Quelle liegt der
Daily Sharpe bei 1,18, der Monthly bei 1,38 und der Yearly bei 0,54. Solche Unterschiede sind ein
Hinweis auf serielle Korrelation der Renditen — dieselbe Eigenschaft, die laut
[[Walk-Forward Guard Buffer & Varianz-Inflation]] Signifikanztests anti-konservativ macht.

## Was zusätzlich in einen Report gehört

Über die Standardkennzahlen hinaus, aus den anderen Quellen dieses Vaults:

| Kennzahl | Warum | Quelle |
|---|---|---|
| **Buy-and-Hold-Vergleich** | Pflicht bei jeder Long-only-Strategie; die Kennzahl ist dann die Information Ratio, nicht Sharpe | Chan |
| **`dubious_pct`** | Anteil Trades mit Stop und Ziel in derselben Kerze — Maß der Ausführungsunsicherheit | Projektregel, `algo/pnl.py` |
| **Untergrenze der mittleren Rendite** (BCa) | sagt, ob die Zahl überhaupt von null unterscheidbar ist | Masters |
| **Drawdown-Grenze** (Doppel-Bootstrap) | der naive Bootstrap unterschätzt Katastrophen um bis zu Faktor 13,65 | Masters |
| **Kelly-`f` und `f_ruin`** | ist das gefahrene Leverage überhaupt vertretbar? | Chan |
| **P-Wert aus Permutationstest** | trennt echte Muster von Data-Mining-Bias | Masters |
| **Trade-Anzahl** | alles oben ist bei zweistelligen Trade-Zahlen nicht belastbar | alle drei |

## Bezug zu diesem Projekt

`algo/backtest_bt.py` nutzt bereits `backtesting.py` und bekommt damit einen Teil dieser
Kennzahlen frei geliefert (Return, Sharpe, Sortino, Calmar, MDD, Drawdown-Dauer, Win Rate, Profit
Factor, Expectancy, SQN). Im Report ausgewiesen wird davon bisher nur ein Ausschnitt — siehe
[[Ensemble-Strategie — Backtest-Ergebnis & Commission-Verzerrung (laufend)]].

**Drei konkrete Lücken:**

1. **Calmar und Drawdown-Dauer fehlen.** Beide sind für einen gehebelten Futures-Trader
   aussagekräftiger als die Sharpe Ratio, und `backtesting.py` liefert sie bereits — sie werden
   nur nicht ausgegeben.
2. **Der Buy-and-Hold-Vergleich fehlt.** `stats['Buy & Hold Return [%]']` existiert im
   `backtesting`-Output. Bei einer Strategie, die MNQ in einem steigenden Zeitraum handelt, ist
   das die entscheidende Kontrollzahl — vgl. auch
   [[Return-Partitionierung (Skill, Trend, Training Bias)]], die denselben Effekt
   permutationsbasiert isoliert.
3. **Skew und Kurtosis fehlen** — und ohne sie lässt sich weder die Zulässigkeit des t-Tests
   beurteilen noch die Monte-Carlo-Leverage-Optimierung durchführen.

Alle drei sind reine Ausgabeerweiterungen ohne neue Berechnung.

Verwandt im Vault: [[Erwartungswert & Reward-to-Risk-Modell]] (dieselbe Expectancy-Formel aus dem
ICT-Material) und [[Risikomanagement (1% pro Trade)]].
