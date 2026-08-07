---
tags: [concept, algo-methodology, validation]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[How I Develop Trading Strategies (Source)]]"]
---

# Monte Carlo Permutation Test (MCPT)

Statistischer Test, ob das In-Sample- oder Walk-Forward-Ergebnis einer Handelsstrategie auf
echten Mustern in den Daten beruht oder überwiegend auf **Data-Mining-Bias** — dem Effekt, dass
eine Optimierung über mehrere Parameter-/Modellvarianten immer die zufällig beste findet, selbst
wenn die zugrunde liegende Strategie wertlos ist. Nullhypothese: die Strategie ist wertlos, ihr
gutes Ergebnis ist reines Optimierungsartefakt. Aus [[How I Develop Trading Strategies (Source)]]
(neurotrader, nach Timothy Masters' *Permutation and Randomization Tests for Trading System
Development*).

> Nicht zu verwechseln mit dem in `algo/validate.py` bereits als "Monte Carlo" bezeichneten
> Trade-Order-Resampling (Verfahren, das die Reihenfolge realer Trades mischt, um Rendite-/
> Drawdown-Verteilungen zu schätzen) — dieser Test hier mischt stattdessen die **Preis-Bars
> selbst**, bevor überhaupt optimiert wird. Zwei unterschiedliche Verfahren mit demselben
> umgangssprachlichen Namen im Ursprungsmaterial; im Code/`algo/`-Kontext dieses Vaults bewusst
> als **Bar-Permutationstest** bzw. MCPT von `validate.py`s Monte Carlo abgegrenzt (siehe
> `docs/superpowers/specs/2026-08-08-algo-permutation-test-design.md`).

## Der Bar-Permutationsalgorithmus

Ziel: eine synthetische Preisreihe erzeugen, die dieselben statistischen Eigenschaften hat wie
die echte (Mean/Std/Skew/Kurtosis der Returns nahezu identisch, erster und letzter Preis exakt
gleich — Gesamttrend bleibt erhalten), aber keine der zeitlichen Muster, auf die eine Strategie
trainiert werden könnte.

1. Preise pro Bar relativ zum eigenen Open ausdrücken (log-Skala): High/Low/Close als
   prozentualer Offset vom Open dieser Bar, plus die Gap-Größe (Open relativ zum Close der
   Vor-Bar).
2. Die Bar-Indizes werden **zweimal getrennt** zufällig gemischt — einmal für die Intrabar-Werte
   (High/Low/Close-Offsets), einmal für die Gaps. Getrennt, weil Gaps bei manchen Märkten (Krypto:
   kaum vorhanden, da 24/7-Handel) ein anderes statistisches Verhalten haben als bei anderen
   (Aktien/Futures mit Handelspause: Gap kann groß sein).
3. Aus den gemischten relativen Werten werden die Bars sequenziell neu zusammengesetzt: jeder
   Open = Close der vorigen (permutierten) Bar + gemischter Gap, dann High/Low/Close relativ zu
   diesem neuen Open.
4. Zurück auf die normale Preisskala exponenzieren.

Ein `start_index`-Parameter erlaubt, nur einen Teil der Reihe zu permutieren (alles davor bleibt
unverändert) — das macht den Algorithmus für den Walk-Forward-MCPT wiederverwendbar (siehe
unten).

## Zwei Varianten

### In-Sample MCPT

1. Strategie einmal auf den echten In-Sample-Daten optimieren → realer Objective-Wert (z.B.
   Profit Factor).
2. N Permutationen der gesamten Datenreihe erzeugen (`start_index=0`), Strategie auf jeder neu
   optimieren → Verteilung von Objective-Werten, die eine wertlose Strategie durch reines
   Data-Mining hätte erzielen können.
3. P-Wert = Anteil der Permutationen mit Objective-Wert ≥ realem Wert.
4. Schwelle im Quellmaterial: P < 1%, mindestens 1.000 Permutationen (100 nur bei zu teurer
   Optimierung als absolutes Minimum).

### Walk-Forward MCPT

Wie oben, aber nur der Testzeitraum nach dem ersten Trainings-Fold wird permutiert
(`start_index = train_window`), das Trainingsfenster bleibt echt — pro Permutation läuft der
volle Walk-Forward (teuer, deshalb im Quellmaterial nur 200 statt 1.000 Permutationen). Schwelle:
P < 5% bei nur einem Jahr Testdaten, P < 1% ab zwei oder mehr Jahren.

## Warum nicht einfach "auf 2020 testen"?

Sobald Out-of-Sample-/Validierungsdaten einmal zum Vergleich mehrerer Strategie-Ideen benutzt
wurden, sind sie nicht mehr wirklich "out of sample" — wählt man die beste von mehreren auf
denselben Validierungsdaten getesteten Varianten, überfittet man effektiv die Validierungsdaten
(**Selection Bias**), obwohl keine einzelne Variante direkt darauf trainiert wurde. Der MCPT
verwirft schwache Ideen, bevor überhaupt Validierungsdaten "verbraucht" werden.

## Bekannte Grenzen

- Reale Preise sind kein reiner Random Walk — sie haben Volatility Clustering und Long Memory,
  beide Eigenschaften werden durch die Permutation zerstört. Eine Strategie, die stark auf einer
  dieser Eigenschaften beruht, kann den Test dadurch optimistisch verzerrt bestehen.
- Trotzdem kein wertloser Test: besteht eine Strategie den MCPT selbst mit dieser Verzerrung
  nicht, ist Overfitting hochwahrscheinlich.
- P-Wert ist ein Maß, kein Optimierungsziel — bei genug Herumprobieren lässt sich fast jede
  Strategie durch den Test bringen ("if a measure becomes a target, it is no longer a good
  measure").
- Multi-Market-Fall (korrelierte Märkte gemeinsam permutieren) im Quellmaterial nur angerissen,
  hier nicht vertieft.

## Bezug zu diesem Projekt

Viertes, unabhängiges Verfahren neben Walk-Forward/Parameter-Sensitivität/Trade-Order-Resampling
in `algo/validate.py`. Design für `algo/permutation_test.py` liegt vor
(`docs/superpowers/specs/2026-08-08-algo-permutation-test-design.md`), Implementierung selbst ist
noch offener Backlog-Punkt in `algo/PLAN.md`. Siehe auch
[[Vier-Stufen-Strategieentwicklung (Masters)]] für den übergeordneten Entwicklungsprozess, in den
dieser Test eingebettet ist.
