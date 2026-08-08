---
tags: [concept, algo-methodology, validation, permutation, referenz]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[How I Develop Trading Strategies (Source)]]", "[[Testing and Tuning Market Trading Systems (Source)]]"]
---

# Monte Carlo Permutation Test (MCPT)

Statistischer Test, ob das In-Sample- oder Walk-Forward-Ergebnis einer Handelsstrategie auf
echten Mustern in den Daten beruht oder überwiegend auf **Data-Mining-Bias** — dem Effekt, dass
eine Optimierung über mehrere Parameter-/Modellvarianten immer die zufällig beste findet, selbst
wenn die zugrunde liegende Strategie wertlos ist. Nullhypothese: die Strategie ist wertlos, ihr
gutes Ergebnis ist reines Optimierungsartefakt.

Zwei Quellen im Vault: [[How I Develop Trading Strategies (Source)]] (neurotrader-Transkript) und
seit 2026-08-08 die Primärquelle [[Testing and Tuning Market Trading Systems (Source)]]
(Masters, Kap. 7, Programme `MCPT_TRN.CPP`, `MCPT_BARS.CPP`, `CHOOSER.CPP`).

> Nicht zu verwechseln mit dem in `algo/validate.py` bereits als „Monte Carlo" bezeichneten
> Trade-Order-Resampling (mischt die Reihenfolge realer Trades, um Rendite-/Drawdown-Verteilungen
> zu schätzen). Der Test hier mischt die **Preis-Bars selbst**, bevor überhaupt optimiert wird.
> Zwei unterschiedliche Verfahren mit demselben umgangssprachlichen Namen; im `algo/`-Kontext
> bewusst als **Bar-Permutationstest** abgegrenzt (siehe
> `docs/superpowers/specs/2026-08-08-algo-permutation-test-design.md`).

## Das Grundprinzip

Wir führen die Aufgabe (Training oder Test) mit den Originaldaten in korrekter Reihenfolge aus,
dann `m`-mal mit permutierten Daten. Legitime Fähigkeit verschwindet durch die Permutation, weil
die vorhersagbaren Muster zerstört werden; Overfitting-Fähigkeit **nicht** — ein überangepasstes
System findet auch im Rauschen „Muster".

```
p-value = (k + 1) / (m + 1)

  m = Zahl der Permutationen
  k = Zahl der Permutationen, deren Performance die Originalperformance ERREICHT ODER UEBERTRIFFT
```

Die `+1` in Zähler und Nenner ist kein Schönheitsfehler: der Originallauf zählt als einer der
möglichen Ausgänge mit. Bei 9 Permutationen und dem Originallauf auf Platz 1 von 10 ist der
P-Wert 0,1 — nicht 0.

Streng korrektes Vorgehen: P-Wert-Schwelle **vorab** wählen (0,01 … 0,1), `m` so groß wählen, dass
`(m+1)·p` ganzzahlig ist, `k` daraus lösen, und danach entscheiden.

```
fuer irep = 0 … nreps-1:
    if irep > 0: shuffle
    performance berechnen
    if irep == 0:
        original_performance = performance
        count = 1
    else if performance >= original_performance:
        count += 1
p-value = count / nreps
```

## Was genau getestet wird — drei verschiedene Objekte

Masters' wichtigste Präzisierung gegenüber dem neurotrader-Material:

### 1. Fertig spezifiziertes System auf OOS-Daten

Gemessen wird die OOS-Performance. **Permutiert wird ausschließlich der OOS-Zeitraum.**

Die Lookback-Bars davor dürfen **nicht** mitpermutiert werden: sie fließen im Originallauf nicht
in die Performance ein. Wären sie ungewöhnlich (starker Trend, Volatilitätsspitze) und würden in
den OOS-Bereich gemischt, verfälschten sie das Ergebnis gegenüber dem Original.

Vorteil gegenüber t-Test und Bootstrap ([[Konfidenzgrenzen für Renditen (t-Test, Bootstrap, BCa)]]):
**keinerlei Verteilungsannahmen**, und robuster gegen Verteilungsprobleme als der Bootstrap.

### 2. Der Trainingsprozess — die wichtigste Anwendung

Gemessen wird die finale **In-Sample**-Performance nach vollständiger Reoptimierung, und zwar in
**jeder** Permutation neu.

Zwei Arten, wie ein System scheitern kann:

- **zu schwach** — findet keine Muster. Fällt ohnehin früh auf, dafür braucht man keinen teuren
  Test.
- **zu stark (Overfitting)** — genau hier hilft der Test. Ein überangepasstes System erzeugt auch
  auf permutierten Daten hervorragende IS-Ergebnisse, der Originallauf sticht also **nicht**
  heraus. Masters' Beispiel für so ein System: optimierbare Lookbacks für mehrere gleitende
  Durchschnitte *und* für die Volatilität *und* optimierbare Schwellen für deren Änderungen —
  „astonishing performance in the training period and yet completely random trades out-of-sample."

> *„Unless you get a small (0.05 or less) p-value, you should be suspicious of your system
> specification and optimization process."* — Masters nennt das eines der wertvollsten Werkzeuge
> in seinem Werkzeugkasten.

### 3. Die „Model Factory"

Nicht ein System, sondern **Systemidee + Optimierungsverfahren + OOS-Prüfung** als Ganzes.
Gemessen wird die gepoolte Walk-Forward-OOS-Performance. Fällt der P-Wert klein aus, darf man
darauf vertrauen, dass die Fabrik mit aktuellen Daten ein brauchbares System produziert.

Zwei Entscheidungen dabei:

- **Der erste Trainings-Fold muss von der Permutation ausgenommen werden**, weil er im
  Originallauf nie in einem OOS-Block auftaucht. Ob man ihn *für sich* permutiert, ist laut
  Masters egal; er tut es, um mehr Varianz in die Trade-Entscheidungen zu bringen (sonst kann ein
  aufwärts gerichteter Markt im ersten Fold systematisch Long-Übergewicht erzeugen und die
  permutierte Performance aufblähen).
- **Alles nach dem ersten Fold in einem Rutsch permutieren** (Masters' Praxis — er sucht
  universelle Muster) **oder je Fold getrennt** (bewahrt lokale Marktcharakteristik, passend wenn
  man sich adaptiv an wechselnde Bedingungen anpassen will). Rigorose Forschung dazu existiert
  laut Autor nicht.

### Sonderfall prädiktive Modelle

Bei Prädiktor-/Zielvariablen-Datensätzen ist die Reihenfolge egal — es zählt nur die **Paarung**.
Permutiert wird durch Umsortieren der Ziele. Zwei Regeln:

1. **Indikatoren dürfen nicht gegeneinander permutiert werden**, nur gegen das Ziel. Sonst
   entstehen unsinnige Kombinationen — Masters' Beispiel: S&P-100-Trend stark aufwärts bei
   gleichzeitig S&P-500-Trend stark abwärts. Grundtenet des Permutationstests: **jede Permutation
   muss unter H₀ real gleich wahrscheinlich sein.**
2. **Serielle Korrelation darf nicht in Prädiktoren *und* Ziel gleichzeitig vorliegen.** In einem
   von beiden ist unschädlich (man permutiert dann gedanklich das jeweils andere). In beiden
   zerstört die Permutation eine reale Eigenschaft und erzeugt unmögliche Paarungen.
   - Prädiktoren sind fast immer seriell korreliert (20-Bar-Trend teilt 19 Bars mit dem Nachbarn).
   - Beim Ziel vermeidbar: **Änderung** der Volatilität statt Volatilität selbst. Aber Achtung:
     überlappende Zeitfenster (täglich die Änderung über die kommenden fünf Tage) bringen die
     Korrelation zurück.
   - Diese Einschränkung ist nicht MCPT-spezifisch — sie gilt für nahezu alle Standardtests:
     Abhängigkeit reduziert die effektiven Freiheitsgrade und macht Tests anti-konservativ.

## Erweiterung für Selection Bias: Solo- vs. unbiased P-Wert

Bei mehreren Konkurrenten (verschiedene Entwickler, oder derselbe Ansatz mit vielen
Parametersätzen) reicht der P-Wert des Siegers nicht — man hat ihn ja *ausgewählt*, siehe
[[Training Bias & Selection Bias]]. Testet man genug wertlose Systeme, hat garantiert eines Glück.

```
fuer irep = 0 … nreps-1:
    if irep > 0: shuffle
    fuer jeden Konkurrenten k:
        perf = Performance von k
        if irep == 0:
            original[k]        = perf
            solo_count[k]      = 1
            unbiased_count[k]  = 1
        else if perf >= original[k]:
            solo_count[k] += 1
    if irep > 0:
        best = max( Performance ALLER Konkurrenten in DIESER Permutation )
        fuer jeden Konkurrenten k:
            if best >= original[k]:
                unbiased_count[k] += 1

solo_pval[k]     = solo_count[k]     / nreps
unbiased_pval[k] = unbiased_count[k] / nreps
```

Der `solo_pval` ist identisch mit dem, was der Basisalgorithmus für dieses System einzeln liefern
würde. Der `unbiased_pval` beantwortet: *Wenn alle Konkurrenten wertlos wären — wie wahrscheinlich
wäre es, dass der **Beste** von ihnen so gut abschneidet wie das betrachtete System?*

- Für den **tatsächlichen Sieger** ist das ein exakter Vergleich bester-gegen-besten und damit der
  korrekte P-Wert.
- Für **alle anderen** ist er konservativ, also eine Obergrenze. Deshalb: **jeder Konkurrent mit
  kleinem `unbiased_pval` verdient ernsthafte Betrachtung**, nicht nur der Sieger.

## Die Permutationsalgorithmen

### Basis: Vektor korrekt mischen (Fisher-Yates)

```
i = n
while i > 1:
    j = int(unifrand() · i)      # j MUSS strikt kleiner als i sein
    i -= 1
    tausche indices[i] und indices[j]
```

Voraussetzung: `unifrand()` liefert `0.0 ≤ x < 1.0` und **nie exakt 1.0**. Lässt sich das nicht
garantieren, muss der Index abgefangen werden. Bei diesem Verfahren ist jede Permutation gleich
wahrscheinlich; `j == i` (kein Tausch) ist ein zulässiger Ausgang.

### Einfache Preisreihe

Preise darf man **nicht** direkt tauschen — man stelle sich eine Aktie vor, die bei 20 startet und
bei 800 endet. Also: in Änderungen zerlegen, Änderungen mischen, Reihe neu aufbauen. Und weil
Differenzen bei hohen Kursen größer sind als bei niedrigen, arbeitet man mit **Verhältnissen** —
äquivalent: mit Differenzen der **Log-Preise**.

```python
def prepare_permute(log_prices):
    return np.diff(log_prices)          # nc-1 Aenderungen

def do_permute(log_prices, changes, rng):
    """log_prices[0] bleibt unveraendert; Rest wird neu aufgebaut."""
    rng.shuffle(changes)                # Fisher-Yates
    out = np.empty_like(log_prices)
    out[0] = log_prices[0]
    out[1:] = log_prices[0] + np.cumsum(changes)
    return out
```

**Der Trend bleibt exakt erhalten**, weil derselbe Startpreis und dieselbe Menge an Änderungen
verwendet wird — nur das Auf und Ab dazwischen ändert sich. Das ist Voraussetzung dafür, dass
Long-/Short-Ungleichgewichte in [[Return-Partitionierung (Skill, Trend, Training Bias)]]
korrekt behandelt werden.

### Preis-Bars (OHLC) — vier Bedingungen

Deutlich heikler. Vier Eigenschaften müssen erhalten bleiben:

1. Open und Close dürfen **nie** außerhalb von High/Low liegen.
2. Die Verteilung von High und Low **relativ zu Open/Close** und ihre Spannweite muss erhalten
   bleiben.
3. Die Verteilung der **Open-zu-Close**-Änderungen muss erhalten bleiben.
4. Die Verteilung der **Inter-Bar-Gaps** (Close → nächstes Open) muss erhalten bleiben.

Die ersten drei sind leicht: alles relativ zum Open der Bar ausdrücken und die Tripel
(High, Low, Close) **zusammenhalten**. Punkt 4 ist die Falle.

> **Die Gap-Falle.** Permutiert man naiv die Open-zu-Open-Änderungen, trifft regelmäßig ein großer
> permutierter Open-Sprung auf eine Bar mit großem Open-zu-Close-Verfall. Beispiel: Bar öffnet bei
> 100, schließt bei 98 (realistisch). Das nächste Open *sollte* nahe 98 liegen, das permutierte
> Open ist aber 102 (für sich genommen ebenfalls realistisch). Ergebnis: ein Sprung von 98 auf 102
> **zwischen** zwei Bars — real nahezu unmöglich. *„The problems induced by this are not just
> theoretical; they will utterly destroy permutation testing of many trading systems."*

Lösung: Intra-Bar- und Inter-Bar-Änderungen **getrennt** mischen.

```python
def prepare_permute_bars(o, h, l, c):
    """alles LOG-Preise. Bar 0 ist die unveraenderte 'Basis'-Bar."""
    rel_open  = o[1:] - c[:-1]     # Gap: Close der Vorbar → Open
    rel_high  = h[1:] - o[1:]      # Intrabar, relativ zum Open
    rel_low   = l[1:] - o[1:]
    rel_close = c[1:] - o[1:]
    return rel_open, rel_high, rel_low, rel_close

def do_permute_bars(o, h, l, c, rel, rng, preserve_OO=False):
    rel_open, rel_high, rel_low, rel_close = rel
    off = 1 if preserve_OO else 0
    n   = len(rel_open)

    rng.shuffle(rel_open[off:])                      # (A) Gaps getrennt mischen
    idx = rng.permutation(n - off)                   # (B) Intrabar-Tripel GEMEINSAM mischen
    rel_high[:n-off]  = rel_high[:n-off][idx]
    rel_low[:n-off]   = rel_low[:n-off][idx]
    rel_close[:n-off] = rel_close[:n-off][idx]

    for i in range(1, len(o)):                       # (C) sequenziell neu aufbauen
        o[i] = c[i-1] + rel_open[i-1]
        h[i] = o[i]   + rel_high[i-1]
        l[i] = o[i]   + rel_low[i-1]
        c[i] = o[i]   + rel_close[i-1]
    return o, h, l, c
```

**`preserve_OO`**: Wer Trades konservativ auf dem **Open der Folgebar** ausführt und zusätzlich die
Return-Partitionierung nutzt, muss den Gesamttrend über alle Permutationen exakt konstant halten.
Dafür bleiben die **erste Close-zu-Open-Änderung** und die **letzte Open-zu-Close-Änderung** von
der Permutation ausgenommen. Wirkung: das Open der zweiten Bar (erster möglicher Entry) und das
Open der letzten Bar (letzter möglicher Exit) sind über alle Permutationen identisch. Masters
nennt das „probably excessively cautious, but it's easy to do".

Wichtig: die **erste Bar** und der **Close der letzten Bar** bleiben in jedem Fall unverändert.

### Mehrere Märkte gleichzeitig

Referenziert ein System mehrere Märkte, müssen **alle identisch permutiert** werden, sonst
entstehen Konstellationen (hochkorrelierte Märkte laufen gegeneinander), die es real nicht gäbe —
und die Grundannahme „jede Permutation ist unter H₀ gleich wahrscheinlich" bricht.

```python
def do_permute_multi(data, changes, offset, rng):
    """data: nmkt × nc Matrix von Log-Preisen. offset > 0."""
    nmkt, nc = data.shape
    perm = rng.permutation(nc - offset)                  # EINE Permutation fuer alle Maerkte
    for m in range(nmkt):
        changes[m, offset:] = changes[m, offset:][perm]
        for i in range(offset, nc):
            data[m, i] = data[m, i-1] + changes[m, i]
    return data
```

Regeln für den `offset`:

- `offset` ist der Index des **ersten Falls, der sich ändert**; er muss positiv sein, weil der Fall
  bei `offset−1` als „Basis" unverändert bleibt.
- Der Fall bei `nc−1` bleibt ebenfalls unverändert. Die gemischte Reihe **beginnt und endet damit
  auf den Originalpreisen**, nur das Innere ändert sich.
- Werden mehrere Abschnitte getrennt permutiert, dürfen sie sich **nicht überlappen** — inklusive
  des jeweiligen Basis-Falls. Beispiel: `offset=1, nc=5` verändert die Fälle 1–3; der nächste
  Aufruf muss bei `offset ≥ 5` beginnen, Fall 4 gehört zu keinem von beiden.

**Datenvoraussetzung:** jeder Markt braucht zu jedem Datum einen Preis. Fehlt eines, muss der Bar
bei allen Märkten entfernt werden:

```
alle Markt-Indizes auf 0, grand_index = 0
Schleife:
    max_date = groesstes Datum ueber die aktuellen Indizes aller Maerkte
    jeden Markt vorruecken, bis sein Datum >= max_date ist
    stimmen ALLE Daten ueberein:
        Datensatz an Position grand_index kopieren, alle Indizes und grand_index erhoehen
    laeuft auch nur ein Markt aus: fertig
n_cases = grand_index
```

In der Praxis verliert man bei breit gehandelten Märkten kaum Tage — an Feiertagen ruht alles,
sonst handelt alles.

## Bekannte Grenzen

- Reale Preise sind kein reiner Random Walk — sie haben **Volatility Clustering** und
  **Long Memory**. Beide Eigenschaften werden durch die Permutation zerstört. Eine Strategie, die
  stark auf einer davon beruht, kann den Test dadurch optimistisch verzerrt bestehen.
- Trotzdem kein wertloser Test: besteht eine Strategie den MCPT selbst mit dieser Verzerrung
  **nicht**, ist Overfitting hochwahrscheinlich.
- Der P-Wert ist ein Maß, kein Optimierungsziel — bei genug Herumprobieren lässt sich fast jede
  Strategie durch den Test bringen. („If a measure becomes a target, it is no longer a good
  measure.")
- Alle Einschränkungen zur Auslegung von P-Werten aus
  [[Konfidenzgrenzen für Renditen (t-Test, Bootstrap, BCa)]] gelten unverändert: ein großer P-Wert
  beweist **nicht**, dass die Strategie wertlos ist.

## Schwellen und Umfang

| Variante | Permutationen | Schwelle |
|---|---|---|
| In-Sample MCPT | 1.000 (100 nur als absolutes Minimum) | P < 1 % |
| Walk-Forward MCPT | 200 (teurer, voller Walk-Forward je Permutation) | P < 5 % bei 1 Jahr Testdaten, P < 1 % ab 2 Jahren |
| Trainingsprozess (Masters) | ≥ 100 | P ≤ 0,05 |

## Warum nicht einfach „auf 2020 testen"?

Sobald OOS-/Validierungsdaten einmal zum **Vergleich** mehrerer Strategie-Ideen benutzt wurden,
sind sie nicht mehr wirklich out of sample — wählt man die beste von mehreren auf denselben Daten
getesteten Varianten, überfittet man effektiv die Validierungsdaten (**Selection Bias**), obwohl
keine einzelne Variante direkt darauf trainiert wurde. Der MCPT verwirft schwache Ideen, **bevor**
Validierungsdaten „verbraucht" werden.

## Bezug zu diesem Projekt

Viertes, unabhängiges Verfahren neben Walk-Forward, Parameter-Sensitivität und
Trade-Order-Resampling in `algo/validate.py`. Design für `algo/permutation_test.py` liegt vor
(`docs/superpowers/specs/2026-08-08-algo-permutation-test-design.md`), die Implementierung ist
offener Backlog-Punkt in `algo/PLAN.md`.

Zwei Auswertungen fallen dort fast gratis mit ab und sollten von Anfang an mitgebaut werden:
[[Return-Partitionierung (Skill, Trend, Training Bias)]] (nur Long-/Short-Bars mitzählen) und der
`unbiased_pval` oben (nur das Maximum je Permutation mitführen).

Übergeordneter Prozess: [[Vier-Stufen-Strategieentwicklung (Masters)]].

## Implementierung

`algo/masters.py`: `permute_prices()`, `permute_bars(preserve_oo=…)` und `permute_multi()`. Der `offset`-Parameter deckt die abschnittsweise Permutation ab, die [[Nested Walkforward]] verlangt. `algo/permutation_test.py` (die eigentliche Testschleife) ist weiterhin offener Backlog-Punkt.

Selbstcheck: `python algo/masters.py` (auch in `algo/selfcheck.py`).
