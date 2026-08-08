---
tags: [concept, algo-methodology, validation, risiko, drawdown, referenz]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[Testing and Tuning Market Trading Systems (Source)]]"]
---

# Grenzen für Einzelrenditen & Drawdown

Nicht der *Mittelwert* künftiger Renditen (dafür
[[Konfidenzgrenzen für Renditen (t-Test, Bootstrap, BCa)]]), sondern **die einzelnen künftigen
Werte selbst** — und speziell der schlimmste anzunehmende Drawdown. Aus
[[Testing and Tuning Market Trading Systems (Source)]] (Kap. 6, Programme `CONFTEST.CPP`,
`BND_RET.CPP`, `DRAWDOWN.CPP`, `CHOOSER_DD.CPP`).

Hauptzweck: **Überwachung im Livebetrieb.** Eine Untergrenze für die Monats-/Quartalsrendite,
unter die das System im Normalbetrieb nur mit Wahrscheinlichkeit `p` fällt. Fällt es öfter
darunter, degradiert es.

## Teil 1 — Grenzen für Einzelrenditen aus empirischen Quantilen

### Definition und Formel

*Quantil der Ordnung p* der Verteilung von X: der Wert x mit `P{X < x} ≤ p` und `P{X ≥ x} ≥ p`.
Bei diskreten Daten ist x nicht zwingend eindeutig; praktisch behandelt man die Renditen als
stetig.

```
n Renditen aufsteigend sortieren
m = n·p            → konservative (etwas zu tiefe) Grenze
m = (n+1)·p        → unverzerrte Grenze
m auf ganze Zahl abrunden

Untergrenze = m-kleinste Rendite
Obergrenze  = m-groesste Rendite
```

```python
def bound(returns, p, unbiased=True):
    s = np.sort(returns)
    n = len(s)
    m = int((n + 1) * p) if unbiased else int(n * p)
    m = max(m, 1)
    return s[m - 1]                      # Untergrenze; Obergrenze: s[n - m]
```

**Datenbedarf:** mindestens ~100 Renditen, besser mehrere hundert bis tausend. Bei Monatsrenditen
heißt das über zehn Jahre OOS. Der Kompromiss ist unangenehm: kürzere Renditeperioden liefern
mehr Datenpunkte, aber höhere Streuung und damit so tiefe Grenzen, dass sie nutzlos werden.
Masters: *„Just do your best."*

### Warum die Grenze selbst unsicher ist

Die eigene OOS-Sammlung ist mit Sicherheit optimistisch **oder** pessimistisch verzerrt (siehe
den „Unbiased"-Abschnitt in [[Training Bias & Selection Bias]]). Also ist auch die berechnete
Grenze zu hoch oder zu tief:

| Fehler | Folge | zu prüfen mit |
|---|---|---|
| Grenze **zu hoch** | wird öfter verletzt als die gewünschten `p` → man vermutet Degradation, wo keine ist | „pessimistisches" `q > p` |
| Grenze **zu tief** | wird seltener verletzt → **echte Degradation wird nicht erkannt** | „optimistisches" `q < p` |

Der zweite Fehler ist für die Live-Überwachung der gefährlichere.

Beide Wahrscheinlichkeiten liefert die **unvollständige Beta-Verteilung**. Wahrscheinlichkeit,
dass der m-kleinste von n Werten **über** dem q-Quantil der Verteilung liegt:

```
orderstat_tail(n, q, m) = 1 − I_q(m, n − m + 1)
```

`I_q(a,b)` = regularisierte unvollständige Beta-Funktion (`scipy.special.betainc(a, b, q)`).

```python
from scipy.special import betainc
from scipy.stats  import beta as beta_dist

def orderstat_tail(n, q, m):
    """P{ m-kleinster von n Werten > q-Quantil }"""
    return 1.0 - betainc(m, n - m + 1, q)

def quantile_conf(n, m, conf):
    """Umkehrung: welches q gehoert zu dieser Wahrscheinlichkeit?"""
    return beta_dist.ppf(1.0 - conf, m, n - m + 1)

# pessimistisches q (Grenze zu hoch):
p_pes = orderstat_tail(n, q_pes, m)
# optimistisches q (Grenze zu tief):
p_opt = 1.0 - orderstat_tail(n, q_opt, m)
```

Die `1.0 −`-Drehung beim optimistischen Fall ist der häufigste Stolperstein: `orderstat_tail`
liefert die Wahrscheinlichkeit, dass die Grenze **über** dem q-Quantil liegt; gefragt ist aber
„liegt **darunter**".

### Zahlenbeispiel (CONFTEST, n = 200, p = 0,1 → m = 20)

Die 20.-kleinste OOS-Rendite ist die Untergrenze, die 20.-größte die Obergrenze.

| Vorgabe | Ergebnis |
|---|---|
| optimistisches `q = 0,07` | Wahrscheinlichkeit **0,0692** (⇒ 93,1 % Konfidenz, dass die Grenze über dem 0,07-Quantil liegt) |
| pessimistisches `q = 0,12` | Wahrscheinlichkeit **0,1638** (⇒ 83,6 % Konfidenz, dass sie unter dem 0,12-Quantil liegt) |
| umgekehrt: `p_of_q = 0,05` | optimistisches `q = 0,0673`, pessimistisches `q = 0,1363` |

Letzte Zeile gelesen: es gibt je 5 % Chance, dass die wahre Fehlerrate meiner „10 %-Grenze"
tatsächlich unter 6,73 % bzw. über 13,63 % liegt.

Ein weiteres Buchbeispiel: n = 200, p = 0,1, gewünschte Sicherheit 0,999 → pessimistisches
q = 0,18. Also 99,9 % Sicherheit, dass die vermeintliche 10 %-Grenze höchstens 18 % Fehlerrate
hat. *„That's not very good, but on the other hand, demanding such high certainty is asking a
lot."*

CONFTEST verifiziert diese Theoriewerte per Simulation über Millionen Ziehungen aus einer
Gleichverteilung (deren Quantilfunktion die Identität ist, was die Prüfung trivial macht) — die
gemessenen Raten stimmen auf drei Nachkommastellen (0,0691 vs. 0,0692 theoretisch). Der leichte
Bias in den „fail above/below"-Zählern (sollte 0,5 sein) stammt aus dem Abrunden bei `m` und
verschwindet bei großem n; er wirkt zudem in die konservative Richtung.

### Obergrenzen sind hier ausdrücklich nützlich

Anders als beim Mittelwert. Ein System degradiert nämlich nicht nur, indem es zu schlechte Trades
produziert, sondern auch, indem die **guten ausbleiben**. Deshalb:

- Für die Obergrenze eine **große** „Fehlerrate" ansetzen, z.B. `p = 0,4` — man *erwartet*, dass
  40 % der künftigen Renditen darüber liegen. Sinkt dieser Anteil deutlich, wird man misstrauisch.
- Alle Beziehungen kehren sich um: bei der Obergrenze ist das *pessimistische* q **kleiner** als
  die Fehlerrate, das *optimistische* größer. Rechnerisch: `upper_bound_index = n − 1 − lower_bound_index`,
  `upper_q = 1 − lower_q`.

### Referenzlauf BND_RET (OEX, Quartalsrenditen)

Parameter: `max_lookback = 100`, `n_train = 1000`, `n_test = 63` (≈ ein Quartal Handelstage),
`lower_fail_rate = 0,1`, `upper_fail_rate = 0,4`, `p_of_q = 0,05`; optimistisches/pessimistisches
q automatisch als `0,9 ×` bzw. `1,1 ×` der Fehlerrate.

| Ergebnis | Wert |
|---|---|
| annualisierte mittlere Rendite | 1,021 % („a mighty poor trading system") |
| 10 % der künftigen Quartale schlechter als | **−38,942 %** annualisiert |
| 40 % der künftigen Quartale besser als | **+9,043 %** annualisiert |
| Anzahl Renditen | 124 — „dangerously few" |

Lesart für die Überwachung: zwei Quartale unter −38,9 % ⇒ hochgradig verdächtig; bleibt der
Anteil der Quartale über +9,0 % dauerhaft deutlich unter 40 % ⇒ ebenfalls verdächtig.

## Teil 2 — Drawdown

### Definition im Buch (absolut, nicht prozentual)

```python
def drawdown(trades):
    """trades = Log-Renditen in zeitlicher Reihenfolge"""
    cumulative = max_price = trades[0]
    dd = 0.0
    for r in trades[1:]:
        cumulative += r
        if cumulative > max_price:
            max_price = cumulative
        else:
            dd = max(dd, max_price - cumulative)
    return dd
```

Bewusst **absolut** statt „Prozent vom Maximalkapital": das vermeidet die Willkür eines
Startkapitals, macht die Wirkung über das Zeitintervall gleichförmig und funktioniert auch bei
negativem Eigenkapital (gehebelte Futures). Da die Renditen Logarithmen sind, ist das Ergebnis
monoton zum Prozent-Drawdown; die Umrechnung ist eine Zeile:

```python
dd_pct = 100.0 * (1.0 - math.exp(-dd))
```

Herleitung: `dd` ist der Log des Verhältnisses Peak-Equity zu Tal-Equity. Start 1, Peak 3, Tal 2
→ `dd = log 3 − log 2` → `100·(1 − exp(log 2 − log 3)) = 100·(1 − 2/3) = 33,3 %`.

### Der naive Bootstrap ist gefährlich falsch

Die intuitive und **falsche** Argumentationskette:

1. Die Returns sind OOS und damit unverzerrt.
2. *Also* repräsentieren sie die Zukunft fair. ← **hier bricht es**
3. Drawdown hängt von der Reihenfolge ab.
4. Die Zukunft unterscheidet sich nur durch Zusammensetzung und Reihenfolge.
5. Also: mit Zurücklegen aus den OOS-Returns ziehen, Drawdown je Stichprobe, 5 %-Quantil =
   95 %-Grenze.

Schritt 2 ist der Fehler: die OOS-Stichprobe **ist** verzerrt, man weiß nur nicht in welche
Richtung. Der naive Bootstrap erfasst die Faktoren 2 und 3, ignoriert aber **Faktor 1** (die
Stichprobe ist selbst eine Zufallsziehung). Und die Verzerrung wirkt beim Drawdown
**asymmetrisch** — optimistische Stichproben schaden mehr, als pessimistische nützen. Deshalb
ist der Fehler nicht neutral, sondern systematisch **anti-konservativ**.

### Der korrekte Doppel-Bootstrap

```
fuer 'outer' Wiederholungen:
    aeussere Bootstrap-Stichprobe aus den OOS-Returns ziehen  (Groesse = n_changes, ganze OOS-Menge)
    fuer 'inner' Wiederholungen:
        innere Stichprobe daraus ziehen  (Groesse = n_trades, Laenge der Drawdown-Periode)
        DD_inner[inner] = drawdown(innere Stichprobe)
    DD_inner sortieren
    DD_outer[outer] = DD_inner[ DD_conf · inner ]
DD_outer sortieren
Bound = DD_outer[ Bound_conf · outer ]
```

```python
def find_quantile(sorted_data, frac):
    k = int(frac * (len(sorted_data) + 1)) - 1
    return sorted_data[max(k, 0)]

def drawdown_quantiles(b_changes, n_trades, nboot, rng):
    """vier Quantile in einem Durchlauf — das Sortieren ist der teure Teil"""
    work = np.empty(nboot)
    for i in range(nboot):
        work[i] = drawdown(rng.choice(b_changes, size=n_trades, replace=True))
    work.sort()
    return (find_quantile(work, 0.999),   # katastrophal
            find_quantile(work, 0.99),    # schwer
            find_quantile(work, 0.95),    # ziemlich schlecht
            find_quantile(work, 0.90))    # gelegentlich zu erwarten

def dd_bound(oos_returns, n_trades, bootstrap_reps, quantile_reps, bound_conf, rng):
    n   = len(oos_returns)
    q10 = np.empty(bootstrap_reps)
    for b in range(bootstrap_reps):
        outer = rng.choice(oos_returns, size=n, replace=True)          # Faktor 1
        _, _, _, q10[b] = drawdown_quantiles(outer, n_trades, quantile_reps, rng)
    q10.sort()
    return find_quantile(q10, bound_conf)
```

**Die zwei Konfidenzen auseinanderhalten:**

| Größe | Bedeutung | typischer Wert |
|---|---|---|
| `DD_conf` | Wahrscheinlichkeit, dass ein künftiger Drawdown die Grenze **nicht** überschreitet | 0,9 / 0,95 / 0,99 / 0,999 |
| `Bound_conf` | Konfidenz, dass die **berechnete** Grenze mindestens so groß ist wie die wahre, unbekannte `DD_conf`-Grenze | 0,7 (Routine) bis 0,9+ (Extremfälle) |

Also: *„Mit 70 % Sicherheit liegt die Grenze, die zu 90 % nicht überschritten wird, bei höchstens
69 %."* Eine Grenze für eine Grenze. Im Buch wird `Bound_conf` für die beiden extremsten
`DD_conf`-Werte automatisch auf `1 − (1 − Bound_conf)/2` angehoben — bei den ernsten Drawdowns
will man sicherer sein.

**Auslegungsregeln:** Die Grenze gilt für **einen im Voraus festgelegten Zeitraum** (typisch das
kommende Jahr, `n_trades = 252`) und nur für Equity-Veränderungen *innerhalb* dieses Zeitraums —
nicht für „jemals" und nicht für die Fortsetzung eines laufenden Drawdowns. Vorheriges
Eigenkapital wird ignoriert.

**Kosten:** Größenordnung 10⁸ Iterationen — Sekunden bis eine Minute für ein fertiges System,
aber unbrauchbar *innerhalb* einer Optimierungsschleife. Genau dafür ist die Tabelle unten da:
sie sagt, wann der billige naive Weg vertretbar ist.

Formal ist übrigens nur die **äußere** Schleife ein echter Bootstrap (Perzentil-Methode für ein
Konfidenzintervall). Die innere schätzt lediglich die Statistik — das gewünschte Quantil — aus der
empirischen Verteilung der äußeren Stichprobe.

### Wie schlimm der Fehler ist (DRAWDOWN-Experimente)

Parameter: `WinProb = 0,6`, `BootstrapReps = 5.000`, `QuantileReps = 10.000`, `TestReps = 2.000`.
Jede Zelle: **Faktor, um den die tatsächliche Verletzungsrate die angenommene übersteigt.**
1,0 wäre perfekt; > 1,0 ist gefährlich, < 1,0 nur konservativ.

| p | OOS | DD-Periode | naiv | korrekt (0,5) | korrekt (0,6) | korrekt (0,8) |
|---|---|---|---|---|---|---|
| 0,001 | 63 | 63 | **13,65** | 4,49 | 3,42 | 1,64 |
| 0,01 | 63 | 63 | 4,29 | 1,74 | 1,37 | 0,71 |
| 0,05 | 63 | 63 | 2,16 | 2,15 | 1,65 | 0,85 |
| 0,10 | 63 | 63 | 1,66 | 1,66 | 1,31 | 0,72 |
| 0,001 | 252 | 252 | 5,84 | 1,81 | 1,35 | 0,59 |
| 0,01 | 252 | 252 | 2,55 | 1,02 | 0,80 | 0,41 |
| 0,05 | 252 | 252 | 1,62 | 1,62 | 1,26 | 0,64 |
| 0,10 | 252 | 252 | 1,36 | 1,37 | 1,10 | 0,61 |
| 0,001 | 2520 | 252 | 1,54 | 0,79 | 0,68 | 0,45 |
| 0,01 | 2520 | 252 | 1,16 | 0,76 | 0,68 | 0,51 |
| 0,05 | 2520 | 252 | 1,06 | 1,06 | 0,95 | 0,72 |
| 0,10 | 2520 | 252 | 1,04 | 1,03 | 0,94 | 0,75 |

(Die drei Konfigurationen entsprechen: ein Quartal OOS → nächstes Quartal; ein Jahr → nächstes
Jahr; zehn Jahre → nächstes Jahr.)

Ablesbar:

- Der naive Bootstrap **unterschätzt in jeder einzelnen Zeile** — nie konservativ.
- Seine Qualität hängt massiv an **Stichprobengröße** und **Fehlerrate**: mit 63 OOS-Returns und
  p = 0,001 liegt er um **Faktor 13,65** daneben; mit 2.520 Returns und p = 0,1 nur noch um 1,04.
- Die einzige Konstellation, in der er vertretbar ist (und dann innerhalb einer Optimierung sehr
  nützlich, weil er Größenordnungen schneller ist): **große OOS-Stichprobe und moderates p**.
- Der korrekte Algorithmus mit `Bound_conf = 0,8` ist außer im Extremfall (63 / 0,001) durchweg
  konservativ, ohne zu übertreiben — schlechtester Wert 0,41. *„This trade-off is a no-brainer
  for me."*
- Selbst der korrekte Weg schafft die Kombination „kleine Stichprobe + Katastrophenwahrscheinlichkeit"
  nicht (1,64 bei 0,8) — das ist schlicht eine zu schwere Frage für 63 Datenpunkte.

### Anwendungsbeispiel CHOOSER_DD

Auf dieselben 65 S&P-100-Titel wie bei [[Nested Walkforward]] angewandt, `n_trades = 252`
(kommendes Jahr). Ausgabe ist eine Matrix: Zeilen = `DD_conf` (0,001 / 0,01 / 0,05 / 0,1),
Spalten = `Bound_conf` (0,5 / 0,6 / 0,7 / 0,8 / 0,9 / 0,95). Masters' Kommentar zum Ergebnis:
*„we pay surprisingly low penalty for greatly increased confidence in our bound"* — die Spalten
laufen nicht dramatisch auseinander, hohe Sicherheit ist also billig zu haben.

## Bezug zu diesem Projekt

`algo/validate.py` liefert Monte-Carlo-Drawdown-Verteilungen aus dem Mischen realer Trades —
**das ist exakt der naive Bootstrap aus Schritt 5.** Bei der aktuellen Datenbasis (wenige Dutzend
Trades, `raw/marktdaten/` wächst erst seit August 2026) fällt das in die **schlechteste Zeile**
der Tabelle. Die dort berichteten Drawdown-Zahlen sind also zu optimistisch, möglicherweise um
eine Größenordnung. Vor jeder Kapitalfreigabe relevant, siehe Roadmap-Stufe 5/6 in
[[Algo-Trading: Arbeitsstandards]].

Zweiter offener Punkt: Für die Live-Überwachung existiert im Projekt noch keine Grenze. Sobald
genug OOS-Wochen vorliegen, wäre die Quantilgrenze aus Teil 1 auf **Wochen- oder Monatsrenditen**
das passende Werkzeug — zusammen mit `orderstat_tail`, um zu wissen, wie sehr man ihr trauen darf.

## Implementierung

`algo/masters.py`: `return_bound(returns, p, upper=…)` für Einzelrenditen, `orderstat_tail(n, q, m)` / `quantile_conf(n, m, conf)` für das Vertrauen in diese Grenze. Drawdown: `drawdown()`, `dd_to_pct()`, `drawdown_bound()` (korrekter Doppel-Bootstrap) und `drawdown_bound_naive()` — letzteres bewusst mitgeliefert, um den Unterschied messen zu können.

Selbstcheck: `python algo/masters.py` (auch in `algo/selfcheck.py`).
