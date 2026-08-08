---
tags: [concept, algo-methodology, validation, referenz]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[Testing and Tuning Market Trading Systems (Source)]]"]
---

# CSCV (Combinatorially Symmetric Cross Validation)

Ein **Dominanz-Test**: Wie wahrscheinlich ist es, dass der in-sample beste Parametersatz
out-of-sample *schlechter* abschneidet als der Median seiner Konkurrenten? Aus
[[Testing and Tuning Market Trading Systems (Source)]] (Kap. 5, Programme `CSCV_CORE.CPP`,
`CSCV_MKT.CPP`), nach *„The Probability of Backtest Overfitting"* (Bailey et al., 2015).

Masters lehnt Cross Validation für Marktdaten sonst ab (siehe
[[Cross Validation vs. Walk-Forward (Masters)]]) — dies ist die eine Anwendung, die er nützlich
findet.

## Warum diese Bauform

Bei gewöhnlicher k-facher CV ist der Testsatz je Fold viel kleiner als der Trainingssatz. Will man
**pro Fold** eine eigene Kennzahl berechnen (etwa um die Fold-zu-Fold-Streuung zu sehen), bricht
das bei Verhältnismaßen zusammen: Sharpe braucht eine Standardabweichung im Nenner (kann winzig
oder null sein, bei einem einzigen Fall undefiniert), Profit Factor eine Verlustsumme, Drawdown
Ordnung.

CSCV löst das, indem es die Returns in eine **gerade** Zahl von Blöcken teilt und **jede mögliche
Kombination** aus der Hälfte der Blöcke als Trainingssatz und der anderen Hälfte als Testsatz
durchspielt. IS und OOS sind damit immer gleich groß (je ~50 %).

```
(5-1)  Ncombinations = Nblocks! / ( (Nblocks/2)! · (Nblocks/2)! )

       Nblocks = 10  →   252 Kombinationen
       Nblocks = 12  →   924 Kombinationen
       Nblocks = 14  →  3432 Kombinationen
```

## Voraussetzungen

- **Partitioniert werden die Bar-Returns, nicht die Preise.** Blöcke von Preisen neu zu
  kombinieren erzeugt Sprungstellen, die jede gleitende Berechnung zerstören. Man lässt jeden
  Kandidaten einmal über die *gesamte* Historie laufen und partitioniert die entstehende
  Renditereihe.
- **Kein „intelligentes" Training.** Jeder Kandidat muss **unabhängig** von den Ergebnissen der
  anderen entstehen. Genetische Optimierung und Hill-Climbing sind damit ausgeschlossen; erlaubt
  sind Grid Search oder viele Zufallsparametersätze. (Siehe
  [[Differential Evolution & Parameter-Sensitivität]] — dort explizit unzulässig.)
- **Ein-Bar-Lookahead**, sonst greift das Guard-Buffer-Problem
  ([[Walk-Forward Guard Buffer & Varianz-Inflation]]). Man könnte den Rekombinationsalgorithmus um
  schrumpfende Trainingssegmente erweitern, Masters hält das für den Aufwand nicht wert.
- Die Granularität muss für **alle** Kandidaten dieselbe sein — jede Spalte der Matrix muss bei
  allen Systemen denselben Zeitpunkt meinen. Bar-für-Bar ist der Normalfall; gröber (stündlich,
  freitags) ist zulässig, aber schlechter.

## Datenstruktur

Eine Matrix `returns[n_systems][n_cases]`: eine **Zeile je Kandidat** (Parametersatz), eine
**Spalte je Bar**. (Masters transponiert bewusst gegenüber dem Bailey-Paper — so liegen die
Returns eines Systems zusammenhängend im Speicher.)

Die Zeilenzahl wächst schnell: bei einem MA-Crossover mit `max_lookback` sind es
`max_lookback · (max_lookback−1) / 2` Kandidaten. Alle Zeilen müssen **am selben Bar beginnen**
(`max_lookback − 1`), auch wenn kürzere Lookbacks früher könnten — sonst ist es keine Matrix.

```python
def get_returns(prices, max_lookback):
    """prices = LOG-Preise. Zeile je (ilong, ishort), Spalte je Bar."""
    rows = []
    for ilong in range(2, max_lookback + 1):
        for ishort in range(1, ilong):
            row = []
            for i in range(max_lookback - 1, len(prices) - 1):
                s = np.mean(prices[i - ishort + 1 : i + 1])
                l = np.mean(prices[i - ilong  + 1 : i + 1])
                if   s > l: row.append(prices[i+1] - prices[i])    # long
                elif s < l: row.append(prices[i] - prices[i+1])    # short
                else:       row.append(0.0)                        # neutral
            rows.append(row)
    return np.array(rows)
```

(Im Original werden die gleitenden Summen inkrementell fortgeschrieben statt neu berechnet —
minimal ungenauer durch Fließkomma-Akkumulation, aber um Größenordnungen schneller.)

## Der Algorithmus

```
nless = 0
fuer jede der Ncombinations Trainings-/Test-Aufteilungen:
    fuer jedes System i:  is_crit[i]  = criter(Returns von i in den Trainingsbloecken)
    fuer jedes System i:  oos_crit[i] = criter(Returns von i in den Testbloecken)
    ibest = argmax(is_crit)
    rang  = #{ i : oos_crit[ibest] >= oos_crit[i] }        # inkl. sich selbst
    rel_rank = rang / (n_systems + 1)
    if rel_rank <= 0.5: nless += 1
return nless / Ncombinations
```

```python
from itertools import combinations

def cscv(returns, n_blocks, criter):
    n_systems, ncases = returns.shape
    n_blocks = (n_blocks // 2) * 2                      # muss gerade sein

    # Bloecke gleich oder fast gleich gross — kein Vielfaches noetig
    bounds, start = [], 0
    for i in range(n_blocks):
        length = (ncases - start) // (n_blocks - i)
        bounds.append((start, start + length))
        start += length

    nless = ncombo = 0
    for train_idx in combinations(range(n_blocks), n_blocks // 2):
        train_cols = np.concatenate([np.arange(*bounds[b]) for b in train_idx])
        test_cols  = np.concatenate([np.arange(*bounds[b]) for b in range(n_blocks)
                                     if b not in train_idx])
        is_crit  = np.array([criter(returns[s, train_cols]) for s in range(n_systems)])
        oos_crit = np.array([criter(returns[s, test_cols])  for s in range(n_systems)])

        ibest    = int(np.argmax(is_crit))
        rank     = int(np.sum(oos_crit[ibest] >= oos_crit))
        rel_rank = rank / (n_systems + 1)
        if rel_rank <= 0.5:
            nless += 1
        ncombo += 1
    return nless / ncombo
```

**Warum Rang statt Median:** rechnerisch äquivalent zu „liegt der OOS-Wert des IS-Besten über dem
Median der anderen?", aber schneller — man spart das Sortieren.

Masters' C-Version erzeugt die Kombinationen nicht über `itertools`, sondern durch einen
**Radix-artigen Vorrückschritt** über ein Flag-Array: das erste `(1,0)`-Paar von links wird zu
`(0,1)` gedreht und alle Einsen davor werden nach ganz links geschoben. Da ein einmal gedrehtes
`(0,1)` nie zurückkippen kann, ohne dass sich ein höheres Flag ändert, sind alle Kombinationen
garantiert eindeutig — Prüfung: die erzeugte Anzahl muss exakt (5-1) treffen, sonst gäbe es
Duplikate und der Algorithmus liefe endlos.

## Auslegung

Gelesen wird das Ergebnis wie ein P-Wert: **klein ist gut.** Es ist die geschätzte
Wahrscheinlichkeit, dass der IS-beste Kandidat OOS **unter** dem Median seiner Konkurrenten
landet. Wäre das Modell wertlos, läge sie bei ~0,5: es gäbe dann keinen Grund, warum
IS-Überlegenheit in OOS-Überlegenheit münden sollte.

Zwei bekannte Restverzerrungen (weshalb Masters von *reasonably* unbiased spricht):

- jeder Trainingssatz ist nur halb so groß wie die Gesamtdaten → **pessimistisch**;
- bei nichtstationären Preisen leckt wie bei jeder CV etwas Zukunftsinformation ein →
  **optimistisch**.

## Was der Test tatsächlich misst — und was nicht

Das Ergebnis ist **vollständig relativ zum Konkurrentenfeld**. Es misst *Dominanz*: wie stark
schlägt der IS-beste Kandidat seine Konkurrenten in der realen Welt (approximiert durch OOS)?

Zwei Manipulationsrichtungen, beide unbeabsichtigt leicht:

- **Feld verwässern.** Viele offensichtlich unsinnige Parametersätze schneiden überall schlecht
  ab — schon ein mittelmäßiges System liegt dann OOS über dem Median und bekommt einen unverdient
  guten Wert.
- **Feld verengen.** Nur gute, ähnliche Kandidaten: keiner dominiert die anderen, der Wert wird
  schlecht, obwohl das System gut sein kann.

**Regel: der Parameterraum muss gründlich, aber realistisch abgedeckt sein.** Und: der Test sagt
**nichts** über Rendite oder Risiko — nur darüber, ob Training überhaupt Mehrwert schafft.

## Referenzlauf auf SPX (MA-Crossover)

Masters wählt SPX wegen der langen Historie und der Marktbreite.

| Blöcke | Max. Lookback | Wahrscheinlichkeit |
|---|---|---|
| 10 | 50 | 0,008 |
| 10 | 100 | 0,016 |
| 10 | 150 | 0,036 |
| 12 | 50 | 0,004 |
| 12 | 100 | 0,009 |
| 12 | 150 | 0,027 |

Seine Interpretation: das sagt nichts über das Risiko-Ertrags-Verhältnis und ist keine Empfehlung,
dieses System zu handeln — aber es zeigt, dass ein optimiert trainiertes Modell seine suboptimalen
Konkurrenten OOS deutlich schlägt. **Das Training schafft echten Wert.** Wäre das Modell fehlerhaft,
lägen die Werte nahe 0,5.

Der Trend über den Lookback (0,008 → 0,036) ist selbst aussagekräftig: mehr Kandidaten heißt mehr
Gelegenheit für Zufallstreffer, die Dominanz wird schwerer nachzuweisen.

Zwei Nebenbefunde aus demselben Abschnitt, die Masters ausdrücklich als *nicht* verallgemeinerbar
markiert: MA-Crossover-Systeme funktionierten über lange Zeiträume gut und **brachen in den
letzten Jahrzehnten deutlich ein**; einzelne Aktien streuen dabei enorm — manche reagieren
hervorragend, andere gar nicht.

## Bezug zu diesem Projekt

Direkt anwendbar auf jeden Grid-Search-Backtest in `algo/` — etwa die Stop-Puffer-Sensitivität in
`backtest_walkforward.py`. Dort werden ohnehin viele Parametersätze über dieselbe Historie
gerechnet, also genau die Return-Matrix erzeugt, die CSCV braucht; es fehlt nur die
Zusammenführung als Matrix statt als Einzelläufe.

**Vorbedingung** ist allerdings die Umstellung auf **Bar-Returns** statt Trade-Returns
([[Profit pro Bar vs. pro Trade]]) — mit Trade-Renditen hat jedes System eine andere Spaltenzahl
und die Matrix existiert gar nicht.

Der Test beantwortet eine Frage, die im Vault bisher offen ist: Bringt die Parameteroptimierung
in `rules.py`/`signals.py` überhaupt etwas, oder wäre ein zufälliger Parametersatz genauso gut?

## Implementierung

`algo/masters.py`: `cscv(returns_matrix, n_blocks, criter)`. Die Matrix (Kandidaten × Bars) entsteht aus `bar_returns_from_trades()` je Parametersatz.

Selbstcheck: `python algo/masters.py` (auch in `algo/selfcheck.py`).
