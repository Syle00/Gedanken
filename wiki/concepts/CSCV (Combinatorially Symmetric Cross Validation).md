---
tags: [concept, algo-methodology, validation]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[Testing and Tuning Market Trading Systems (Source)]]"]
---

# CSCV (Combinatorially Symmetric Cross Validation)

Ein **Dominanz-Test**: Wie wahrscheinlich ist es, dass der in-sample beste Parametersatz
out-of-sample *schlechter* abschneidet als der Median seiner Konkurrenten? Aus
[[Testing and Tuning Market Trading Systems (Source)]] (Kap. 5), nach *„The Probability of
Backtest Overfitting"* (Bailey et al., 2015).

Masters lehnt Cross Validation für Marktdaten sonst ab (siehe
[[Cross Validation vs. Walk-Forward (Masters)]]) — dies ist die eine Anwendung, die er nützlich
findet.

## Warum diese Bauform

Bei gewöhnlicher k-facher CV ist der Testsatz je Fold viel kleiner als der Trainingssatz. Will
man **pro Fold** eine eigene Kennzahl berechnen, bricht das bei Verhältnismaßen zusammen:
Sharpe braucht eine Standardabweichung im Nenner, Profit Factor eine Verlustsumme, Drawdown
Ordnung — alles instabil bis undefiniert bei winzigen Testsätzen.

CSCV löst das, indem es die Returns in eine **gerade** Zahl von Blöcken teilt und dann **jede
mögliche Kombination** aus der Hälfte der Blöcke als Trainingssatz und der anderen Hälfte als
Testsatz durchspielt. Damit sind IS und OOS immer gleich groß (je ~50 %).
Anzahl Kombinationen: `Nblocks! / ((Nblocks/2)!)²`.

## Voraussetzungen

- **Partitioniert werden die Bar-Returns, nicht die Preise.** Blöcke von Preisen neu zu
  kombinieren erzeugt Sprungstellen, die jede gleitende Berechnung zerstören. Man lässt jeden
  Kandidaten einmal über die *gesamte* Historie laufen und partitioniert die entstehende
  Renditereihe.
- **Kein „intelligentes" Training.** Genetische Optimierung oder Hill Climbing sind unzulässig,
  weil sie Ergebnisse früherer Versuche nutzen. Erlaubt sind nur Grid Search oder viele
  Zufallsparametersätze.
- **Ein-Bar-Lookahead**, sonst greift wieder das Guard-Buffer-Problem
  ([[Walk-Forward Guard Buffer & Varianz-Inflation]]).

## Datenstruktur und Algorithmus

Eine Matrix `returns[n_systems][n_cases]`: eine Zeile je Kandidat (Parametersatz), eine Spalte
je Bar.

```
nless = 0
für jede der n_combinations Trainings-/Test-Aufteilungen:
    Zeile mit maximalem Kriterium im Trainingsteil finden  → ibest
    Rang des OOS-Kriteriums dieser Zeile unter allen n_systems OOS-Kriterien bestimmen
    fractile = rang / (n_systems + 1)
    wenn fractile <= 0.5: nless += 1
Rückgabe: nless / n_combinations
```

Gelesen wird das Ergebnis wie ein P-Wert: **klein ist gut.** Es ist die geschätzte
Wahrscheinlichkeit, dass der IS-beste Kandidat OOS unter dem Median seiner Konkurrenten landet.
Wäre das Modell wertlos, läge sie bei ~0,5.

## Was der Test tatsächlich misst — und was nicht

Das Ergebnis ist **vollständig relativ zum Konkurrentenfeld**. Zwei Manipulationsrichtungen:

- Füllt man das Feld mit offensichtlich unsinnigen Parametersätzen auf, schneiden die überall
  schlecht ab — schon ein mittelmäßiges System liegt dann OOS über dem Median und bekommt einen
  unverdient guten Wert.
- Beschränkt man das Feld auf lauter gute, ähnliche Kandidaten, dominiert keiner die anderen und
  der Wert wird schlecht, obwohl das System gut sein kann.

Der Parameterraum muss also **gründlich, aber realistisch** abgedeckt sein. Und: der Test sagt
nichts über Rendite oder Risiko — nur darüber, ob Training überhaupt Mehrwert schafft.

Zwei bekannte Restverzerrungen: jeder Trainingssatz ist nur halb so groß wie die Gesamtdaten
(pessimistisch), und Nichtstationarität leckt wie bei jeder CV etwas Zukunftsinformation ein
(optimistisch).

## Masters' SPX-Beispiel (MA-Crossover)

| Blöcke | Max. Lookback | Wahrscheinlichkeit |
|---|---|---|
| 10 | 50 | 0,008 |
| 10 | 100 | 0,016 |
| 10 | 150 | 0,036 |
| 12 | 50 | 0,004 |
| 12 | 100 | 0,009 |
| 12 | 150 | 0,027 |

Interpretation des Autors: das sagt nichts über das Risiko-Ertrags-Verhältnis und nicht, dass
man dieses System handeln sollte — aber es zeigt, dass ein optimiert trainiertes Modell seine
suboptimalen Konkurrenten OOS deutlich schlägt, das Training also echten Wert schafft.

Randnotiz aus demselben Abschnitt: MA-Crossover-Systeme funktionierten in Masters' Tests über
lange Zeiträume gut und **brachen in den letzten Jahrzehnten deutlich ein**; einzelne Aktien
streuen dabei enorm.

## Bezug zu diesem Projekt

Direkt anwendbar auf jeden Grid-Search-Backtest in `algo/` (z.B. die Stop-Puffer-Sensitivität in
`backtest_walkforward.py`): dort werden ohnehin viele Parametersätze über dieselbe Historie
gerechnet — genau die Return-Matrix, die CSCV braucht. Voraussetzung wäre die Umstellung auf
Bar-Returns statt Trade-Returns ([[Profit pro Bar vs. pro Trade]]). Bisher nicht implementiert.
