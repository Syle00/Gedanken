---
tags: [concept, algo-methodology, validation, permutation, referenz]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[Testing and Tuning Market Trading Systems (Source)]]"]
---

# Return-Partitionierung (Skill, Trend, Training Bias)

Zerlegung des In-Sample-Gesamtergebnisses eines optimierten Handelssystems in drei Bestandteile —
mit Permutationen als Messinstrument. Aus
[[Testing and Tuning Market Trading Systems (Source)]] (Kap. 7, Programme `MCPT_TRN.CPP`,
`MCPT_BARS.CPP`).

Masters stuft das Verfahren selbst als weniger rigoros ein als die reinen Permutationstests
(„should usually be taken with a liberal grain of salt") — aber seine Herleitung erklärt, **wie**
scheinbar gute Performance zustande kommt, und liefert nebenbei eine zweite Schätzung künftiger
Leistung.

## Die Zerlegung

```
(7-2)  TotalReturn = Skill + Trend + TrainingBias
```

| Komponente | Bedeutung | Zukunft |
|---|---|---|
| **Skill** | echtes Erkennen wiederholbarer Muster | bleibt erhalten |
| **Trend** | Gewinn allein daraus, dass das System in einem steigenden Markt überwiegend long war | bleibt, solange der Trend hält |
| **TrainingBias** | gelerntes Rauschen | verschwindet sofort |

## Die Trend-Komponente ist explizit berechenbar

```
TrendPerReturn = MarketChange / n
                 MarketChange = log(Endpreis) − log(Startpreis)
                 n            = Anzahl einzelner Preisaenderungen (= Anzahl Preise − 1)

(7-1)  Trend = (NumLong − NumShort) · TrendPerReturn
```

Begründung: In einem Markt mit Aufwärtsdrift hebt der Trend jede Long-Bar im Mittel um
`TrendPerReturn` an und drückt jede Short-Bar um denselben Betrag. Ein **Münzwurf-System** mit
derselben Long/Short-Verteilung würde also im Mittel exakt `Trend` verdienen — ganz ohne
Intelligenz.

Da `TrendPerReturn` aus der Preishistorie und `NumLong`/`NumShort` aus dem trainierten System
bekannt sind, ist `Trend` **direkt berechenbar**, ohne jede Permutation.

### Die philosophische Frage dahinter

Masters lässt sie ausdrücklich offen und führt die Argumente vor:

- Trainiert man dasselbe System auf Markt A (starker Aufwärtstrend) und Markt B (seitwärts), wird
  A überwiegend Long-Trades produzieren und B ausgeglichene. Das ist kein Zufall, sondern die
  Optimierung, die dem Trend folgt.
- **Pro:** „go with the flow instead of fighting a current by rowing upstream." Die meisten
  Entwickler tun das, ohne darüber nachzudenken, und Masters neigt dieser Seite zu.
- **Contra:** Wer sagt, dass der Trend anhält — und was passiert mit einem stark unbalancierten
  System, wenn er dreht?
- **Verschärft:** In einem stark steigenden Markt verdient auch ein System Geld, das täglich eine
  Münze wirft. Man könnte „Intelligenz" also erst dort ansetzen, wo ein System diesen Münzwurf
  *schlägt*.
- Der Weise in der Ecke merkt an, dass das Contra-Argument bei einer Trendumkehr trägt, das
  Pro-Argument nicht. Woraufhin jemand einwirft, dass Langfristtrends nun einmal langfristig
  anhalten. „And the argument goes on."

**Wer den Trend herausrechnen will:** `TrendPerReturn` bei der **Performancemessung** von jeder
Bar-Rendite abziehen — aber niemals bei der Indikatorberechnung oder der Handelsentscheidung.
Masters erwähnt das als gängige Praxis, verfolgt es aber nicht weiter, weil er den Trend hier
anders verwendet.

## TrainingBias per Permutation messen

Permutiert man die Kursänderungen und trainiert neu (Permutationsalgorithmen auf
[[Monte Carlo Permutation Test (MCPT)]]):

- `TrendPerReturn` bleibt **identisch** — dieselben Änderungen in anderer Reihenfolge, Start- und
  Endpreis unverändert. Genau dafür ist die Permutation so konstruiert.
- `NumLong` / `NumShort` ändern sich, `Trend` ist also je Permutation neu zu berechnen.
- `Skill` ist **per Konstruktion null**, weil die Muster zerstört sind.

Was vom permutierten Gesamtreturn über den Trendanteil hinausgeht, muss also Training Bias sein:

```
(7-3)  TrainingBias   = PermutedTotalReturn − Trend
(7-4)  UnbiasedReturn = TotalReturn − mean(TrainingBias)
(7-5)  Skill          = UnbiasedReturn − Trend(original)
```

Ein einzelner Permutationslauf ist zu verrauscht; erst der Mittelwert über hunderte bis tausende
Permutationen liefert eine brauchbare Schätzung. Als Nebenprodukt fällt derselbe P-Wert
`(k+1)/(m+1)` an wie beim gewöhnlichen MCPT — man bekommt beides in **einer** Schleife.

**Zwei Zahlen mit unterschiedlicher Aussage:**

- `UnbiasedReturn` **enthält** den Trendanteil — die richtige Zahl, wenn man die Philosophie
  „Trendmitnahme ist legitim" vertritt.
- `Skill` ist die strengere Zahl: um wie viel schlägt das System einen Münzwurf mit derselben
  Long/Short-Bilanz?

## Die Kernschleife

```python
# Trend pro Rendite EINMAL vorab — ab dem ersten Bar, an dem eine Entscheidung moeglich ist
trend_per_return = (prices[-1] - prices[max_lookback-1]) / (len(prices) - max_lookback)
changes = prepare_permute(prices[max_lookback-1:])

count, mean_training_bias = 0, 0.0

for irep in range(nreps):
    if irep > 0:
        do_permute(prices[max_lookback-1:], changes)         # nur ab dem Basis-Bar!

    # VOLLE Reoptimierung — sonst misst man nicht den Bias des Trainingsprozesses
    opt_return, nshort, nlong = opt_params(prices, max_lookback)
    trend_component = (nlong - nshort) * trend_per_return     # (7-1)

    if irep == 0:
        original                 = opt_return
        original_trend_component = trend_component
        count                    = 1
    else:
        mean_training_bias += opt_return - trend_component    # (7-3)
        if opt_return >= original:
            count += 1

mean_training_bias /= (nreps - 1)
p_value          = count / nreps
unbiased_return  = original - mean_training_bias              # (7-4)
skill            = unbiased_return - original_trend_component # (7-5)
```

**Die drei Stellen, an denen man es falsch machen kann:**

1. Der Permutationsbereich beginnt beim **Basis-Bar** `max_lookback − 1` — dem ersten Bar, an dem
   eine gültige Handelsentscheidung möglich ist. So ist sichergestellt, dass **alle** möglichen
   Trade-Renditen der Permutation unterliegen und gleichzeitig **keine** Änderung von vor dem
   ersten möglichen Trade hineingemischt wird (was den Gesamttrend verändern würde).
2. In jeder Permutation wird **komplett neu optimiert**. Wer die Originalparameter beibehält, misst
   etwas anderes.
3. Der Mittelwert läuft über `nreps − 1`, weil der erste Durchlauf der unpermutierte ist.

## Variante mit konservativen Open-zu-Open-Renditen

`MCPT_BARS.CPP` zeigt dieselbe Rechnung auf OHLC-Bars und mit einer realistischeren Ausführung:
Der Return einer Entscheidung ist die log-Preisänderung vom **Open der Folgebar zum Open der
darauffolgenden** — statt Close-zu-Close, das im Livebetrieb kaum erreichbar ist.

Das System ist ein simples Mean-Reversion-Modell: gibt es einen langfristigen Aufwärtstrend über
einen Schwellenwert **und** gleichzeitig einen scharfen kurzfristigen Rückgang über einen zweiten
Schwellenwert, wird für die nächste Bar long gegangen. These: ein plötzlicher Einbruch in einem
Aufwärtsmarkt ist eine vorübergehende Abweichung.

```python
for irise in range(1, 51):                       # 50 × 50 Grid
    rise_thresh = irise * 0.005
    for idrop in range(1, 51):
        drop_thresh = idrop * 0.0005
        total_return, nl = 0.0, 0
        for i in range(lookback, ncases - 2):    # −2: die Rendite braucht zwei Bars voraus
            rise = close[i] - close[i - lookback]     # langfristiger Anstieg
            drop = close[i-1] - close[i]              # unmittelbarer Rueckgang
            if rise >= rise_thresh and drop >= drop_thresh:
                ret = open_[i+2] - open_[i+1]         # KONSERVATIV
                nl += 1
            else:
                ret = 0.0
            total_return += ret
```

Die Offsets verschieben sich entsprechend:

```
trend_per_return = (open[nprices-1] − open[lookback+1]) / (nprices − lookback − 2)
prepare_permute(nprices − lookback, open+lookback, high+lookback, low+lookback, close+lookback, …)
```

Der erste mögliche Trade öffnet bei `lookback+1` und schließt spätestens am Open der letzten Bar.
Genau dafür gibt es `preserve_OO` in der Bar-Permutation (siehe
[[Monte Carlo Permutation Test (MCPT)]]) — sonst wäre der so definierte Gesamttrend nicht über alle
Permutationen konstant.

## Zwei Referenzläufe — und ihre wichtigste Lehre

Dieselben zwei Programme auf OEX (S&P 100) und SPX (S&P 500), je 1.000 Permutationen:

| System | Markt | P-Wert |
|---|---|---|
| MA-Crossover (Trendfolge, `MCPT_TRN`) | SPX | **0,001** — Minimum bei 1.000 Permutationen |
| Mean Reversion (`MCPT_BARS`) | SPX | **≈ 1,0** |
| beide | OEX | jeweils deutlich anders |

SPX ist im getesteten Zeitraum ausgeprägt **anti**-mean-reverting und zugleich stark
trendfolgend — beide Extremwerte sind das jeweils Erreichbare. Masters' Kommentar: *„But wow.
I mean, wow."* (Mit der ehrlichen Einschränkung, dass die SPX-Historie 1962 beginnt, die
OEX-Historie erst 1982 — der frühe Zeitraum könnte eine Rolle spielen.)

> **Die Lehre für dieses Projekt:** Zwei ähnlich zusammengesetzte US-Indizes können auf denselben
> Test **gegensätzlich** reagieren. Backtest-Ergebnisse aus `raw/marktdaten/` für MNQ lassen sich
> **nicht** auf ES übertragen, auch wenn beide US-Indexfutures sind. Das ist im Vault bislang
> nirgends festgehalten — und `algo/backtest_*.py` filtert seit dem 2026-08-07-Fix bewusst nach
> Symbol.

## Bezug zu diesem Projekt

Direkt umsetzbar, sobald `algo/permutation_test.py` existiert (offener Backlog-Punkt 10 in
`algo/PLAN.md`). Die Partitionierung kostet neben dem ohnehin geplanten MCPT nur:

- eine Zeile für `trend_per_return`,
- das Mitzählen von Long- und Short-Bars je Lauf,
- drei Subtraktionen am Ende.

Sie beantwortet eine Frage, die bei allen bisherigen `algo/`-Backtests offen bleibt: **wie viel
eines Ergebnisses liegt schlicht daran, dass MNQ im Datenzeitraum gestiegen ist?** Bei einer
Datenbasis, die im Juli/August 2026 beginnt, ist das keine akademische Frage.

Verwandt und ebenfalls fast gratis in derselben Schleife: der `unbiased_pval` gegen Selection Bias
(siehe [[Monte Carlo Permutation Test (MCPT)]] und [[Training Bias & Selection Bias]]).

Die billigere, ungenauere Alternative zur reinen Bias-Schätzung ohne Permutationen ist StocBias —
ebenfalls auf [[Training Bias & Selection Bias]].

## Implementierung

`algo/masters.py`: `partition_return(original_return, nlong, nshort, trend_per_return, permuted)` liefert ein `Partition`-Objekt mit `trend`, `training_bias`, `unbiased_return`, `skill` und `p_value` in einem Durchgang.

Selbstcheck: `python algo/masters.py` (auch in `algo/selfcheck.py`).
