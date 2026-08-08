---
tags: [concept, algo-methodology, validation, bias]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[Testing and Tuning Market Trading Systems (Source)]]"]
---

# Training Bias & Selection Bias

Zwei **verschiedene** optimistische Verzerrungen, die in jedem Entwicklungsprozess nacheinander
auftreten. Aus [[Testing and Tuning Market Trading Systems (Source)]] (Masters, Kap. 4 und 5).
Der Unterschied ist die zentrale Pointe: einen Out-of-Sample-Zeitraum zurückzuhalten beseitigt
nur die *erste*.

## Training Bias

*Training Bias* = In-Sample-Performance minus Out-of-Sample-Performance eines **einzelnen**
Systems. Zwei Ursachen:

1. **Overfitting** — das Modell lernt Rauschmuster als wären sie echt. Rauschen wiederholt sich
   per Definition nicht, also verschwindet dieser Performance-Anteil im Livebetrieb.
2. **Unterrepräsentation** — die Trainingshistorie enthält nicht jedes Preismuster, das später
   auftreten wird. Daraus folgt: so viel Historie wie möglich verwenden.

Masters' empirische Nebenbefunde aus dem TRNBIAS-Experiment (MA-Crossover auf synthetischen
Preisen mit alternierendem Trend, tausende Wiederholungen):

- Bei **großen** Datensätzen ist die Wahl des Optimierungskriteriums fast egal — mittlere
  Rendite, Profit Factor und Sharpe finden meist dieselben Lookbacks.
- Bei **kleinen** Datensätzen hat das Kriterium massiven Einfluss.
- Die **mittlere Rendite als Optimierungskriterium hatte fast immer den größten Trainings-Bias**,
  weil sie Risiko nur indirekt berücksichtigt. **Profit Factor hatte fast immer den kleinsten** —
  Masters' bevorzugtes Optimierungsziel. Relevant für `algo/`: `backtest_bt.py` und
  `backtest_ensemble.py` optimieren bisher nicht explizit gegen Profit Factor.

## Selection Bias

Die Geschichte, mit der Masters das erklärt (Kap. 5): Agnes lässt John und Phil je ein System
entwickeln und wählt nach **In-Sample**-Ergebnis → Konto ruiniert. Mary macht es besser und hält
ein Jahr Daten zurück; beide Systeme werden darauf getestet, Phils OOS-Ergebnis ist besser, sie
wählt Phils System.

**Und genau in dem Moment ist Phils OOS-Zahl nicht mehr unverzerrt.** Vor der Auswahl war sie es;
die Auswahlhandlung selbst erzeugt die Verzerrung. Grund: jede OOS-Zahl besteht aus *echtem
Können* plus *Glück*. Solange man Systeme einzeln betrachtet, mitteln sich Glück und Pech heraus.
Sobald man das bessere von zweien wählt, wählt man systematisch das **glücklichere** mit — und
Glück wiederholt sich nicht.

**Konsequenz: es braucht zwei getrennte Auslass-Zeiträume.** Ersten OOS-Block für die Auswahl,
zweiten OOS-Block für die unverzerrte Schätzung des ausgewählten Systems.

> Für dieses Projekt direkt relevant: Der Vault vergleicht laufend viele Thesen und
> Parametervarianten gegen dieselben `raw/marktdaten/` (siehe
> [[Muster-Validierung (laufend)]], [[Statistische Muster jenseits der ICT-Konzepte (laufend)]]).
> Jede Zahl dort ist von Selection Bias betroffen, sobald aus den geprüften Thesen die beste
> ausgewählt wird. Das ist kein Argument gegen die Exploration, sondern eines dafür, dass die
> Gewinner-These vor dem Livegang einen **eigenen, bis dahin unberührten Zeitraum** braucht.

## Interlude: Was „unbiased" wirklich heißt

Masters' Warnung, die für alle Folgeseiten gilt: *unbiased* bedeutet **nicht**, dass die
gemessene Zahl ungefähr der Zukunft entspricht. Es bedeutet nur, dass sie über ein gedachtes
Universum vieler paralleler Entwickler hinweg im Mittel weder über- noch unterschätzt. Die
konkrete eigene Stichprobe ist mit an Sicherheit grenzender Wahrscheinlichkeit zu optimistisch
**oder** zu pessimistisch — man weiß nur nicht, welches von beiden.

Diese Einsicht ist die Wurzel von zwei späteren Verfahren:
[[Grenzen für Einzelrenditen & Drawdown]] (der naive Drawdown-Bootstrap ignoriert genau das)
und [[Konfidenzgrenzen für Renditen (t-Test, Bootstrap, BCa)]].

## Billige Trainings-Bias-Schätzung (StocBias)

Wer ohnehin mit einem stochastischen Optimierer arbeitet
([[Differential Evolution & Parameter-Sensitivität]]), bekommt eine grobe Bias-Schätzung fast
umsonst — aus der **Initialpopulation**, nicht aus dem gerichteten Suchteil:

1. Nur zufällig erzeugte (oder per Grid gezogene) Parametersätze verwenden. Mutations-/
   Crossover-Kinder sind unzulässig, weil sie gerichtet sind.
2. Für jeden Parametersatz die Bar-für-Bar-Returns aufzeichnen und die Gesamtsumme bilden.
3. Für **jede** Bar `i` separat: „IS-Return" = Gesamtsumme minus Return von Bar `i`, „OOS-Return"
   = Return von Bar `i`. Über alle Parametersätze das Maximum des IS-Returns je Bar mitführen
   und den zugehörigen OOS-Return merken.
4. `Bias = mean(IS_best) − mean(OOS)`.

Grenzen laut Autor: braucht mehrere tausend Zufallskandidaten, sonst wertlos. Und: liegt der so
ermittelte `IS_return` deutlich unter dem Optimum des echten Optimierers, waren es zu wenige
Kandidaten und die Bias-Schätzung ist unbrauchbar.

Ein deutlich genaueres Verfahren für dieselbe Größe steht auf
[[Return-Partitionierung (Skill, Trend, Training Bias)]].

## Abgrenzung zu bestehenden Vault-Seiten

- [[Backtesting-Biases (Optimisation, Look-Ahead, Survivorship, Cognitive)]] (Halls-Moore)
  nennt „Optimisation Bias" — das ist Masters' Training Bias. **Selection Bias fehlt dort
  vollständig**, ebenso die Konsequenz der zwei Auslass-Zeiträume.
- [[Monte Carlo Permutation Test (MCPT)]] misst denselben Effekt aus einer anderen Richtung:
  statt IS/OOS zu vergleichen, wird geprüft, ob das IS-Ergebnis über dem liegt, was auf
  permutierten Daten erreichbar wäre. Masters' MCPT hat eine **Selection-Bias-Erweiterung**
  (Solo-P-Wert vs. unbiased P-Wert), siehe dort.
