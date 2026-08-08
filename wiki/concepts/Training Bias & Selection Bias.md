---
tags: [concept, algo-methodology, validation, bias, referenz]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[Testing and Tuning Market Trading Systems (Source)]]"]
---

# Training Bias & Selection Bias

Zwei **verschiedene** optimistische Verzerrungen, die nacheinander in jedem Entwicklungsprozess
auftreten. Aus [[Testing and Tuning Market Trading Systems (Source)]] (Kap. 4 und 5, Programme
`TRNBIAS.CPP`, `SelBias.cpp`, `STOC_BIAS.CPP`). Der Unterschied ist die zentrale Pointe: einen
Out-of-Sample-Zeitraum zurückzuhalten beseitigt nur die *erste*.

```
Training Bias  = IS-Performance − OOS-Performance   eines EINZELNEN Systems
Selection Bias = zusaetzliche Verzerrung, die durch das AUSWAEHLEN des besten
                 aus mehreren Systemen entsteht
```

## Training Bias

Zwei Ursachen:

1. **Overfitting** — das Modell lernt Rauschmuster, als wären sie echt. Rauschen wiederholt sich
   per Definition nicht, also verschwindet dieser Performanceanteil im Livebetrieb. Besonders
   schlimm bei übermächtigen Modellen.
2. **Unterrepräsentation** — die Trainingshistorie enthält nicht jedes Preismuster, das später
   auftreten wird. Subtiler, aber genauso schädlich. Konsequenz: **so viel Historie wie möglich
   verwenden.**

### Das TRNBIAS-Experiment

`TrnBias Which Ncases Trend Nreps` erzeugt `Ncases` Log-Preise aus Rauschen plus einem Trend, der
**alle 50 Bars die Richtung wechselt** (`Trend` von 0,01 = schwach bis 0,2 = stark; 0,0 = reiner
Random Walk). Ein vollständiges Grid aus MA-Lookbacks bis 200 Tage wird IS optimiert, dann wird
ein **zweiter, unabhängiger** Preissatz derselben Verteilung erzeugt und das Ergebnis darauf
getestet. Über `Nreps` (mehrere tausend) Wiederholungen gemittelt; `IS − OOS` ist der Training
Bias.

`Which` wählt das Optimierungskriterium: `0` = mittlere Tagesrendite, `1` = Profit Factor
(Summe Gewinne / Summe Verluste), `2` = roher Sharpe (Mittel / Standardabweichung).

**Vier Befunde, die Masters auch aus der Praxis bestätigt:**

| Befund | Konsequenz |
|---|---|
| Bei **großen** Datensätzen ist die Kriterienwahl fast egal — alle drei finden meist dieselben Lookbacks | bei viel Historie nicht überdenken |
| Bei **kleinen** Datensätzen hat das Kriterium **massiven** Einfluss | ← betrifft `algo/` direkt |
| Leichte Tendenz: die beste OOS-Rendite entsteht beim Optimieren auf **Profit Factor** | — |
| **Mittlere Rendite als Kriterium hatte fast immer den größten Training Bias**, Profit Factor fast immer den kleinsten | Profit Factor ist Masters' bevorzugtes Optimierungsziel |

Begründung für den letzten Punkt: mittlere Rendite berücksichtigt Risiko nur indirekt. Profit
Factor und Sharpe belohnen **konsistente** Ergebnisse und sind deshalb die besseren
Optimierungskriterien.

## Selection Bias

Masters' Lehrgeschichte (Kap. 5): Agnes lässt John und Phil unabhängig je ein System auf der
vollen Historie entwickeln und wählt nach **In-Sample**-Ergebnis Johns beeindruckenderes System →
Konto ruiniert, Agnes gefeuert. Mary übernimmt, erkennt das Problem sofort (John hatte ein
übermächtiges Modell benutzt, keiner der beiden hatte je OOS getestet) und formuliert die Regel:

> *„When selecting from among competing systems, always base the selection criterion on
> out-of-sample results, ignoring in-sample results."*

Mary hält daraufhin ein Jahr Daten zurück, lässt beide neu entwickeln und testet beide auf dem
zurückgehaltenen Jahr. Beide OOS-Zahlen sind zu diesem Zeitpunkt **unverzerrt**. Phils Ergebnis
ist etwas besser, sie wählt Phils System.

**Und genau in diesem Moment ist Phils OOS-Zahl nicht mehr unverzerrt.**

Warum: jede OOS-Zahl besteht aus *echtem Können* und *Glück*. Betrachtet man Systeme **einzeln**,
mitteln sich Glück und Pech über das gedachte Universum vieler Entwickler heraus — die Zahl ist
unverzerrt. Wählt man aber das **bessere von zweien**, wählt man systematisch das **glücklichere**
mit. Sind beide gleich gut (unmessbar), gewinnt garantiert das glücklichere. Nur wenn die wahren
Fähigkeiten weit auseinanderliegen, sticht Können das Glück. Und Glück wiederholt sich nicht.

**Konsequenz: es braucht zwei getrennte Auslass-Zeiträume.**

```
Entwicklung        ──────────────────┐
                                     │
1. OOS-Block  ("first OOS")          │  → Auswahl des besten Systems
                                     │
2. OOS-Block  ("second OOS")         │  → unverzerrte Schaetzung des GEWAEHLTEN Systems
```

Mary gibt John und Phil also Daten bis vor **zwei** Jahren, wählt anhand des vorletzten Jahres und
schätzt die Performance auf dem letzten Jahr. Diese Schätzung ist frei von Training Bias **und**
von Selection Bias.

### Das SelBias-Experiment

`SelBias Which Ncases Trend Nreps` — gleicher Aufbau wie TRNBIAS, aber das zweiseitige System wird
in **zwei konkurrierende** Systeme aufgespalten: eines nur long, eines nur short. Beide werden
getrennt IS optimiert, beide auf einem zweiten Datensatz (first OOS) bewertet, der Gewinner auf
einem **dritten** Datensatz (second OOS) getestet.

```
Selection Bias = Performance des Gewinners im 1. OOS − Performance desselben Systems im 2. OOS
```

Ausgegeben werden je Konkurrent IS und OOS (⇒ zwei Training Biases), der Grand-OOS-Wert, **ein**
Selection Bias und dessen t-Score. Masters bittet ausdrücklich darum, diesen Abschnitt auch dann
zu lesen, wenn man das Programm nie benutzt — die Erklärung des Versuchsaufbaus ist selbst das
Lehrmittel für ein Konzept, das vielen Entwicklern fremd bleibt.

> Für dieses Projekt direkt relevant: Der Vault vergleicht laufend viele Thesen und
> Parametervarianten gegen dieselben `raw/marktdaten/` (siehe [[Muster-Validierung (laufend)]],
> [[Statistische Muster jenseits der ICT-Konzepte (laufend)]]). Jede Zahl dort ist von Selection
> Bias betroffen, sobald aus den geprüften Thesen die beste ausgewählt wird. Das ist **kein**
> Argument gegen die Exploration — sondern eines dafür, dass die Gewinner-These vor dem Livegang
> einen eigenen, bis dahin unberührten Zeitraum braucht.

## Interlude: Was „unbiased" wirklich heißt

Masters' Warnung, die für alle Folgeseiten gilt und die er selbst mehrfach zurückreferenziert:

*Unbiased* bedeutet **nicht**, dass die gemessene Zahl ungefähr der Zukunft entspricht. Man stelle
sich unendlich viele Johns in unendlich vielen verrauschten Marktuniversen vor, jeder entwickelt
sein System auf seiner eigenen Historie. *Unbiased* heißt nur: **im Mittel über dieses Universum**
wird die künftige Performance weder über- noch unterschätzt.

Die konkrete eigene Stichprobe ist mit an Sicherheit grenzender Wahrscheinlichkeit zu optimistisch
**oder** zu pessimistisch — man weiß nur nicht, welches von beiden. *„This is the best we can do."*

Diese Einsicht ist die Wurzel von zwei späteren Verfahren:

- [[Grenzen für Einzelrenditen & Drawdown]] — der naive Drawdown-Bootstrap ignoriert genau diese
  Variationsquelle und unterschätzt Katastrophen deshalb um bis zu Faktor 13,65.
- [[Konfidenzgrenzen für Renditen (t-Test, Bootstrap, BCa)]] — quantifiziert die Streuung, statt
  sie zu ignorieren.

## Billige Trainings-Bias-Schätzung (StocBias)

Wer ohnehin mit einem stochastischen Optimierer arbeitet
([[Differential Evolution & Parameter-Sensitivität]]), bekommt eine grobe Bias-Schätzung fast
umsonst — aus der **Initialpopulation**.

**Zulässigkeitsregel:** Nur zufällig erzeugte oder per deterministischem Grid gezogene
Parametersätze dürfen einfließen. **Keine** Mutations-/Crossover-Kinder — die stammen aus einer
gerichteten Suche und würden das Verfahren zerstören.

**Die Idee:** Man denke sich **eine** Bar im Voraus als OOS-Bar. Für jeden Kandidaten bildet man
den Gesamtreturn über **alle anderen** Bars (das ist der IS-Teil) und merkt sich den Kandidaten
mit dem höchsten IS-Wert; dessen Return auf der ausgelassenen Bar ist der ehrliche OOS-Wert. Da
die OOS-Bar an der IS-Auswahl nicht beteiligt war, ist die Differenz eine unverfälschte
Bias-Schätzung.

Eine einzelne Bar wäre zu verrauscht — also macht man es für **jede** Bar gleichzeitig. Und weil
`IS_i = Gesamtsumme − return_i` gilt, kostet das kaum mehr als eine Summe pro Kandidat.

```python
class StocBias:
    def __init__(self, nreturns):
        self.n       = nreturns
        self.IS_best = None      # bester IS-Return je ausgelassener Bar
        self.OOS     = None      # zugehoeriger Return DIESER Bar

    def process(self, returns):
        """Pro Kandidat einmal aufrufen, mit dessen Bar-fuer-Bar-Returns."""
        total = returns.sum()
        IS    = total - returns                      # IS-Return je ausgelassener Bar
        if self.IS_best is None:
            self.IS_best, self.OOS = IS.copy(), returns.copy()
        else:
            better = IS > self.IS_best
            self.IS_best[better] = IS[better]
            self.OOS[better]     = returns[better]

    def compute(self):
        IS_return  = self.IS_best.sum() / (self.n - 1)   # kommensurabel machen:
        OOS_return = self.OOS.sum()                      # jedes IS_best ist Summe ueber n-1 Bars
        return IS_return, OOS_return, IS_return - OOS_return
```

Die Division durch `n−1` ist der einzige nicht offensichtliche Schritt: jedes `IS_best[i]` ist die
Summe über `n−1` Bars, die OOS-Werte sind Einzelrenditen. Erst nach der Division sind beide
Größen vergleichbar.

**Zwei Grenzen, die man kennen muss:**

1. Braucht **mehrere tausend** Zufallskandidaten, sonst ist die Schätzung wertlos. Genau deshalb
   steht im `DEV_MA`-Beispiel `overinit = 10.000` bei `popsize = 100`.
2. **Selbsttest:** Liegt der so ermittelte `IS_return` deutlich unter dem Optimum, das der echte
   Optimierer gefunden hat, waren es zu wenige Kandidaten — dann ist die Bias-Schätzung
   unbrauchbar. Nahe beieinander liegende Werte sind das Gütesiegel.

**Verwendung:** Bias vom optimierten Gesamtreturn abziehen. Ist das Ergebnis nicht mehr
überzeugend, sollte man das System überdenken, bevor man weiter investiert. Im `DEV_MA`-Referenzlauf:
`2,6710 − 0,3221 = 2,3489`.

Ein deutlich genaueres Verfahren für dieselbe Größe (und zusätzlich mit Trennung des
Trendanteils): [[Return-Partitionierung (Skill, Trend, Training Bias)]].

## Abgrenzung zu bestehenden Vault-Seiten

- [[Backtesting-Biases (Optimisation, Look-Ahead, Survivorship, Cognitive)]] (Halls-Moore) nennt
  „Optimisation Bias" — das ist Masters' Training Bias. **Selection Bias fehlt dort vollständig**,
  ebenso die Konsequenz der zwei Auslass-Zeiträume.
- [[Monte Carlo Permutation Test (MCPT)]] misst denselben Effekt aus anderer Richtung: statt IS
  und OOS zu vergleichen, wird geprüft, ob das IS-Ergebnis über dem liegt, was auf permutierten
  Daten erreichbar wäre. Dort auch die **Selection-Bias-Erweiterung** (Solo-P-Wert vs. unbiased
  P-Wert) — das direkte Gegenstück zum zweiten Auslass-Zeitraum, wenn man sich diesen nicht
  leisten kann.
- [[Nested Walkforward]] ist die Antwort auf denselben Befund für den Fall, dass die Auswahl nicht
  einmalig, sondern **laufend** stattfindet.
