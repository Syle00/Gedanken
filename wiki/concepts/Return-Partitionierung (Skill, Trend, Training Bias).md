---
tags: [concept, algo-methodology, validation, permutation]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[Testing and Tuning Market Trading Systems (Source)]]"]
---

# Return-Partitionierung (Skill, Trend, Training Bias)

Zerlegung des In-Sample-Gesamtergebnisses eines optimierten Handelssystems in drei Bestandteile —
mit Permutationen als Messinstrument. Aus
[[Testing and Tuning Market Trading Systems (Source)]] (Kap. 7).

```
TotalReturn = Skill + Trend + TrainingBias          (7-2)
```

- **Skill** — echtes Erkennen wiederholbarer Muster. Bleibt in der Zukunft erhalten.
- **Trend** — Gewinn allein daraus, dass das System in einem steigenden Markt überwiegend long
  ging. Bleibt erhalten, solange der Trend hält.
- **TrainingBias** — gelerntes Rauschen. Verschwindet sofort.

## Die Trend-Komponente ist explizit berechenbar

```
TrendPerReturn = MarketChange / n                   (MarketChange = log(Endpreis) − log(Startpreis))
Trend = (NumLong − NumShort) · TrendPerReturn       (7-1)
```

Begründung: In einem Markt mit Aufwärtsdrift hebt der Trend jede Long-Bar im Mittel um
`TrendPerReturn` an und drückt jede Short-Bar um denselben Betrag. Ein **Münzwurf-System** mit
derselben Long/Short-Verteilung würde also genau `Trend` verdienen, ganz ohne Intelligenz.

Die philosophische Frage dahinter, die Masters ausdrücklich offen lässt: Ist es Intelligenz, den
Langfristtrend mitzunehmen — oder ist Intelligenz nur das, was einen Münzwurf schlägt? Die meisten
Entwickler lassen den Trend unbewusst mitlaufen („go with the flow"). Das Gegenargument ist ein
Trendwechsel. Wer den Trend herausrechnen will, zieht `TrendPerReturn` bei der
**Performancemessung** von jeder Bar-Rendite ab (aber nie bei der Indikatorberechnung).

## TrainingBias per Permutation messen

Permutiert man die Kursänderungen und trainiert neu:

- `TrendPerReturn` bleibt identisch (dieselben Änderungen, nur andere Reihenfolge — Start- und
  Endpreis bleiben gleich, siehe [[Monte Carlo Permutation Test (MCPT)]]).
- `NumLong`/`NumShort` ändern sich, also ist `Trend` je Permutation neu zu berechnen.
- `Skill` ist **per Konstruktion null**, weil die Muster zerstört sind.

Also:

```
TrainingBias      = PermutedTotalReturn − Trend                (7-3)
UnbiasedReturn    = TotalReturn − mean(TrainingBias)           (7-4)
Skill             = UnbiasedReturn − Trend(original)           (7-5)
```

Ein einzelner Permutationslauf ist zu verrauscht; erst der Mittelwert über hunderte bis tausende
Permutationen liefert eine brauchbare `TrainingBias`-Schätzung. Als Nebenprodukt fällt derselbe
P-Wert `(k+1)/(m+1)` an wie beim gewöhnlichen MCPT — man bekommt beides in einer Schleife.

Kernschleife (aus `MCPT_TRN.CPP`, gekürzt):

```
trend_per_return = (prices[n-1] - prices[max_lookback-1]) / (n - max_lookback)
prepare_permute(...)
für irep = 0 … nreps-1:
    wenn irep > 0: do_permute(...)
    opt_return = opt_params(...)                      # volle Reoptimierung!
    trend_component = (nlong - nshort) * trend_per_return
    wenn irep == 0:  original = opt_return; original_trend = trend_component; count = 1
    sonst:           mean_training_bias += opt_return - trend_component
                     wenn opt_return >= original: count += 1
mean_training_bias /= (nreps - 1)
unbiased_return = original - mean_training_bias
skill = unbiased_return - original_trend
```

Entscheidend: In **jeder** Permutation wird komplett neu optimiert. Sonst misst man nicht den
Bias des Trainingsprozesses.

## Verwandt: MCPT für drei verschiedene Objekte

Masters unterscheidet sauber, *was* eigentlich getestet wird — die Unterscheidung ist auf
[[Monte Carlo Permutation Test (MCPT)]] bisher nicht ausgeführt:

1. **Fertig spezifiziertes System** auf OOS-Daten. Permutiert wird **nur** der OOS-Zeitraum. Die
   Lookback-Bars davor dürfen nicht mitpermutiert werden — sie gehen im Originallauf nicht in die
   Performance ein, könnten aber (falls ungewöhnlich, z.B. starker Trend) in den OOS-Bereich
   hineingemischt werden.
2. **Der Trainingsprozess.** Getestet wird die finale In-Sample-Performance. Hier ist der Test am
   wertvollsten: ein *überangepasstes* System findet auch auf permutierten Daten „Muster" und
   sticht deshalb nicht heraus. Ein zu schwaches System fällt ohnehin früher auf. Masters:
   *„Unless you get a small (0.05 or less) p-value, you should be suspicious."*
3. **Die „Model Factory"** — Systemidee + Optimierungsverfahren, bewertet über den gepoolten
   Walk-Forward-OOS. Hier muss der **erste Trainings-Fold von der Permutation ausgenommen**
   werden (er taucht im Originallauf nie in einem OOS-Block auf). Masters permutiert ihn separat
   für sich, hält das aber für nebensächlich. Ebenso offen: alles nach dem ersten Fold in einem
   Rutsch permutieren (seine Praxis, sucht universelle Muster) oder je Fold getrennt (bewahrt
   lokale Marktcharakteristik).

## MCPT mit Selection Bias: Solo-P-Wert vs. unbiased P-Wert

Bei mehreren Konkurrenten (verschiedene Entwickler, oder derselbe Ansatz mit vielen
Parametersätzen) reicht der P-Wert des Siegers nicht — man hat ihn ja *ausgewählt*, siehe
[[Training Bias & Selection Bias]]. Erweiterter Algorithmus:

```
für irep = 0 … nreps-1:
    wenn irep > 0: shuffle
    für jeden Konkurrenten: Performance berechnen
        wenn irep == 0: original[k] = perf; solo_count[k] = 1; unbiased_count[k] = 1
        sonst und perf >= original[k]: solo_count[k] += 1
    wenn irep > 0:
        best = max(Performance aller Konkurrenten in dieser Permutation)
        für jeden Konkurrenten k: wenn best >= original[k]: unbiased_count[k] += 1
solo_pval[k]     = solo_count[k] / nreps
unbiased_pval[k] = unbiased_count[k] / nreps
```

Der `unbiased_pval` fragt: *Wenn alle Konkurrenten wertlos wären — wie wahrscheinlich wäre es,
dass der **Beste** von ihnen so gut abschneidet wie beobachtet?* Für den tatsächlichen Sieger ist
das der exakte P-Wert; für alle anderen ist er konservativ (eine Obergrenze). Deshalb gilt:
**jeder Konkurrent mit kleinem `unbiased_pval` verdient ernsthafte Betrachtung.**

## Zwei Beispielläufe, die zeigen, wie stark Markt und System interagieren

`MCPT_TRN` (MA-Crossover) und `MCPT_BARS` (Mean Reversion, konservativ auf Open-zu-Open
gerechnet) auf OEX bzw. SPX liefern laut Buch drastisch verschiedene Ergebnisse. Bei SPX hat das
Mean-Reversion-System einen P-Wert von **fast 1,0** (der Markt ist dort ausgeprägt
*anti*-mean-reverting), während dasselbe SPX beim Trendfolger **0,001** erreicht — das Minimum
bei 1.000 Permutationen. Masters' Kommentar dazu: „But wow. I mean, wow."

Direkte Lehre für dieses Projekt: **derselbe Test auf zwei ähnlich zusammengesetzten Indizes kann
gegensätzlich ausfallen.** Backtest-Ergebnisse aus `raw/marktdaten/` für MNQ lassen sich nicht auf
ES übertragen, auch wenn beide US-Indexfutures sind.

## Bezug zu diesem Projekt

Direkt umsetzbar, sobald `algo/permutation_test.py` existiert (offener Backlog-Punkt in
`algo/PLAN.md`): Die Partitionierung kostet neben dem ohnehin geplanten MCPT nur das Mitzählen
von Long-/Short-Bars. Sie beantwortet genau die Frage, die bei den bisherigen `algo/`-Backtests
offen bleibt — wie viel eines Ergebnisses schlicht daran liegt, dass MNQ im Datenzeitraum
gestiegen ist.
