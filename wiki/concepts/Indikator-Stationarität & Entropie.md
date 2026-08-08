---
tags: [concept, algo-methodology, indikatoren, stationaritaet, referenz]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[Testing and Tuning Market Trading Systems (Source)]]"]
---

# Indikator-Stationarität & Entropie

Zwei Qualitätsprüfungen, die **vor** der Systementwicklung stattfinden: Wandert mein Indikator
langsam davon? Und trägt er überhaupt Information? Aus
[[Testing and Tuning Market Trading Systems (Source)]] (Kap. 2, Programme `STATN.CPP`,
`ENTROPY.CPP`).

## Teil 1 — Stationarität

*Stationarität* = die statistischen Eigenschaften einer Zeitreihe bleiben über die Zeit konstant.
Masters' pragmatische Haltung:

- Märkte und daraus abgeleitete Indikatoren **sind** nichtstationär, immer. Die Frage ist nur, wie
  schlimm, und ob man es reparieren kann.
- **Klassische Stationaritätstests sind sinnlos** — sie fallen praktisch immer hochsignifikant
  aus. Die Antwort kennt man vorher.
- Nichtstationarität hat unendlich viele Formen; welche einem System schadet, hängt vom System ab.
- Die beste Prüfung eines **fertigen** Systems ist der progressive Walk-Forward
  ([[Walk-Forward Guard Buffer & Varianz-Inflation]], Abschnitt Robustheitstest). Dieses Kapitel
  behandelt bewusst die Phase **davor**.

Die eigentliche Gefahr ist nicht das tägliche Zappeln, sondern das **langsame Wandern**: Ein
Indikator, der monate- oder jahrelang in einem Extrembereich hängt und dann in einen anderen
wandert, macht Modelle in genau diesen Phasen unbrauchbar oder legt sie still. (Nur in einem
Sonderfall ist das erwünscht: wer mehrere komplementäre Systeme betreibt, freut sich, wenn sie
sich abwechseln. Masters nennt das ausdrücklich die Ausnahme, nicht die Regel.)

Die daraus folgende Backtest-Falle: hervorragende Performance über einen **günstigen Teilabschnitt**
der Historie, mittelmäßige überall sonst. Daher: **immer die Equity-Kurve ansehen**, nicht nur die
Gesamtkennzahl — und besonders misstrauisch werden, wenn die gute Phase lange zurückliegt und die
jüngste Performance nachlässt. Und: Indikatoren plotten. *„You may be amazed at what you see."*

Der zugrunde liegende Wunsch: *dass die Marktbedingungen sich während der Entwicklungs- und
Testperiode oft genug ändern, damit alle möglichen Bedingungen vertreten sind.*

### STATN: Gap-Analyse

Statt eines Tests eine Messgröße. Aufruf: `STATN Lookback Fractile Version Filename`.

Vorgehen: Trend (Steigung der Kleinste-Quadrate-Geraden) und Volatilität (Average True Range) über
die Historie berechnen, das Quantil zur angegebenen Fraktile bestimmen (0,5 = Median), dann
zählen, **wie lange der Indikator am Stück auf derselben Seite dieser Schwelle bleibt**. Die
Lauflängen werden in 11 Bins gezählt: 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, > 512.

```python
def gap_analyze(x, thresh, gap_sizes=(1,2,4,8,16,32,64,128,256,512)):
    """zaehlt Lauflaengen auf derselben Seite von thresh"""
    counts = [0] * (len(gap_sizes) + 1)
    count  = 1
    above  = x[0] >= thresh
    for i in range(1, len(x) + 1):
        new_above = (not above) if i == len(x) else (x[i] >= thresh)  # Array-Ende = Wechsel
        if new_above == above:
            count += 1
        else:
            j = next((j for j, g in enumerate(gap_sizes) if count <= g), len(gap_sizes))
            counts[j] += 1
            count = 1
            above = new_above
    return counts
```

Der `Version`-Parameter steuert die Transformation und damit den benötigten Gesamt-Lookback:

```
version == 0 : full_lookback = lookback
               trend[i] = slope(lookback, close+k)
version == 1 : full_lookback = 2 · lookback
               trend[i] = slope(lookback, close+k) − slope(lookback, close+k−lookback)
version  > 1 : full_lookback = version · lookback
               trend[i] = slope(lookback, close+k) − slope(full_lookback, close+k)

mit  k = full_lookback − 1 + i      und   nind = nprices − full_lookback + 1
```

Quantil-Index: `k = int(fractile · (nind+1)) − 1`, auf ≥ 0 begrenzt.

### Messergebnis (OEX, Lookback 100, Fraktile 0,5)

| Gap | Trend v0 | Trend v1 | Trend v3 | Vola v0 | Vola v1 | Vola v3 |
|---|---|---|---|---|---|---|
| 1 | 3 | 1 | 0 | 13 | 41 | 19 |
| 2 | 3 | 1 | 0 | 6 | 13 | 6 |
| 4 | 2 | 2 | 2 | 2 | 9 | 13 |
| 8 | 5 | 2 | 1 | 2 | 8 | 6 |
| 16 | 4 | 3 | 4 | 4 | 9 | 4 |
| 32 | 14 | 2 | 12 | 2 | 10 | 10 |
| 64 | 22 | 14 | 25 | 3 | 12 | 8 |
| 128 | 29 | 54 | 33 | 5 | 25 | 10 |
| 256 | 18 | 15 | 21 | 9 | 23 | 18 |
| 512 | 3 | 1 | 1 | 2 | 5 | 9 |
| > 512 | 0 | 0 | 0 | **6** | 0 | 1 |

Lesarten:

- Der **rohe Trend** bleibt dreimal über 256 Bars (mehr als zwei Jahre) auf derselben
  Median-Seite; beide Transformationen drücken das auf einmal.
- Die **rohe Volatilität** bleibt **sechsmal über 512 Bars** hängen — die Transformationen
  beseitigen das fast vollständig, verschlechtern dafür aber die nächstniedrigere Stufe.
  *„Volatility generally has extreme nonstationarity."*

### Drei Reparaturen, in aufsteigender Härte

**1. Oszillieren gegen den eigenen Lag** (Version 1)

```
neu(t) = Indikator(t) − Indikator(t − lookback)
```

Wirkt am stärksten, verwirft aber die meiste Information über den *absoluten* Wert.

**2. Kurzer minus langer Lookback** (Version > 1)

```
neu(t) = Indikator(t, lookback) − Indikator(t, version · lookback)
```

Kompromiss — über die Länge des zweiten Lookbacks fein steuerbar: längerer zweiter Lookback =
mehr Absolutinformation erhalten, weniger Stationaritätsgewinn.

**3. Rollendes Fenster normieren** (extreme, kontrollierbare Induktion)

```
Zentrierung:  neu(t) = x(t) − mean(x[t−w … t])       bzw. − median(...) bei Ausreissern
Skalierung:   neu(t) = neu(t) / std(x[t−w … t])      bzw. / IQR(...)   bei Ausreissern
```

Kurzes Fenster `w` = nahezu erzwungene Stationarität bei fast vollständigem Verlust der
Absolutinformation; langes Fenster = umgekehrt.

Masters' Erfahrung: der **relative** Wert trägt meistens *mehr* Vorhersagekraft als der absolute —
aber nicht immer; der Trade-off ist bewusst zu treffen.

## Teil 2 — Entropie

Shannons Informationsmaß auf Indikatoren angewandt:

```
(2-1)  H(X) = − Σ_{x ∈ χ} p(x) · log p(x)          mit 0·log 0 := 0

       H ist maximal bei Gleichverteilung, dann gilt H = log K
       relative Entropie  =  H(X) / log K           ∈ [0, 1]
```

Analogie, mit der Masters das herleitet: 1.024 Lose, eines davon meins. Vor der Nachricht habe ich
`log₂ 1024 = 10` Bit Unsicherheit. Nachricht „gewonnen" (p = 1/1024) hat den Wert
`−log(1/1024) = 6,93 nats`; Nachricht „nicht gewonnen" nur `−log(1023/1024) = 0,00098 nats`.
Erwartungswert = `1/1024 · 6,93 + 1023/1024 · 0,00098 = 0,0077 nats` — **das ist die Entropie**.
(Mit natürlichem Logarithmus heißt die Einheit *nat* statt *bit*.)

### Berechnung

Den **gesamten Wertebereich** in gleich **breite** Bins teilen — nicht in gleich **volle**, das
ergäbe immer 1.

```python
def entropy(x, nbins=20):
    minval, maxval = float(np.min(x)), float(np.max(x))
    factor = (nbins - 1e-10) / (maxval - minval + 1e-60)
    idx    = ((x - minval) * factor).astype(int)
    counts = np.bincount(idx, minlength=nbins)
    p      = counts[counts > 0] / len(x)
    return float(-(p * np.log(p)).sum() / np.log(nbins))
```

Die beiden Konstanten sind kein Zierrat: `−1e-10` im Zähler verhindert, dass der Maximalwert in
einen nicht existierenden Bin hinter dem letzten fällt; `+1e-60` im Nenner verhindert Division
durch null, falls alle Werte gleich sind.

**Bin-Zahl:** bei mehreren tausend Datenpunkten ~20. Nicht kritisch — **aber**: ändert sich die
Entropie bei leicht veränderter Bin-Zahl stark, stimmt etwas mit den Daten oder dem Indikator
nicht. *„Plot a histogram!"*

**Masters' Schwellen:**

```
relative Entropie ≥ 0,5     brauchbar (sein persoenlicher Mindestanspruch)
                  < 0,5     verdaechtig
                  < 0,1     ernsthaft reparaturbeduerftig
```

### Warum das praktisch zählt

Niedrige Entropie korreliert stark mit schlechter Modelltrainierbarkeit, weil hohe Entropie
ungefähr gleichmäßige Verteilung über den Wertebereich bedeutet — und die meisten Trainingsverfahren
arbeiten damit am besten. Zwei typische Ursachen:

- **Ausreißer.** Ein einzelner Extremwert zieht die Entscheidungsgrenze eines Klassifikators zu
  sich hin und verdirbt die Trennung der übrigen Fälle. Betrifft auch nichtlineare Modelle mit
  gekrümmter Grenze.
- **Klumpung.** Eine exogene, mit der Vorhersage nichts zu tun habende Bedingung verschiebt die
  Hälfte der Fälle um einen festen Offset (Werte um 1,0 vs. um 100,0), obwohl der Indikator
  *innerhalb* jeder Gruppe exzellent funktioniert. Das Modell fokussiert dann auf die
  Clusterzugehörigkeit. „The result would not be pretty."

**Zwei Einschränkungen:**

1. Entropie misst **Informationsmenge**, nicht Relevanz. Ein Indikator kann hochentrop sein und
   trotzdem nichts über die gesuchte Zielgröße sagen (er sagt vielleicht perfekt die Volatilität
   voraus, während man die Richtung sucht). Umgekehrt gilt aber: wenig Entropie ⇒ wahrscheinlich
   wenig Wert. **Entropie ist eine obere Schranke.**
2. Es *kann* vorkommen, dass eine entropie-erhöhende Umformung die Performance verschlechtert.
   Masters nennt das eine ungewöhnliche Ausnahme — „in the vast majority of situations, increasing
   the entropy of an indicator significantly improves its performance".

### Entropie verbessern

**Grundregel: jede Umformung muss monoton (ordnungserhaltend) sein.** Sonst geht die Eigenschaft
verloren, dass eine trennende Schwelle vor der Transformation auch danach existiert.
**Truncation (Kappen auf einen Grenzwert) verletzt genau das und ist deshalb schlecht** — obwohl
sie das Ausreißerproblem scheinbar löst.

| Situation | Empfehlung |
|---|---|
| Division durch etwas, das klein werden kann | grundsätzlich riskant — Indikator neu denken |
| nur rechtes Ende schwer, moderat | Wurzel oder Kubikwurzel |
| nur rechtes Ende schwer, extrem | Logarithmus |
| beide Enden schwer | Kubikwurzel |
| beide Enden extrem schwer | `tanh(x)` oder `logistic(x)`, vorher passend skalieren |
| passende theoretische Verteilung bekannt | deren CDF (Normal-CDF bei glockenähnlichen Oszillatoren; F-CDF bei Varianzverhältnissen) |
| Klumpung, mehrere Cluster, evtl. plus schwere Enden | Rang-Transformation (unten) |
| Extremwerte sind *bedeutsam*, aber stören das Training | erst gleichverteilt, dann inverse Normal-CDF |

```
(2-2)  tanh(x)     = (eᵗ − e⁻ᵗ) / (eᵗ + e⁻ᵗ)
(2-3)  logistic(x) = 1 / (1 + e⁻ˣ)          ← danach 0,5 abziehen, zentriert bei null
```

**Rang-Transformation (Brute Force, sehr wirksam):** Stichprobe sortiert vorhalten; ein Wert wird
per Binärsuche eingeordnet und durch die Anzahl der kleiner-gleichen Elemente ersetzt. Dann durch
`n` teilen und 0,5 abziehen → Bereich −0,5 … 0,5, relative Entropie nahe 1. Funktioniert am besten
bei großer, repräsentativer Stichprobe mit wenigen Bindungen.

**Extremwerte erhalten, aber zähmen:** erst irgendeine Transformation auf nahezu Gleichverteilung,
dann **inverse Normal-CDF** anwenden. Ergebnis: Glockenform — die Masse liegt innen, es gibt noch
Ausläufer, aber keine trainingsschädlichen.

### Monotones Tail-Cleaning

Für den häufigen Fall „Verteilung ist okay, nur gelegentliche Ausreißer stören". Auch geeignet für
die **Zielvariable**, wenn man deren Werte möglichst wenig verzerren will.

```
cover = 1 − 2 · tail_frac                     tail_frac typisch 0,01 … 0,1
Daten sortieren; ueber alle zusammenhaengenden Fenster mit  int(cover·(n+1))  Faellen laufen
und dasjenige mit der KLEINSTEN Spannweite suchen → minval, maxval

limit = (maxval − minval) · (1 − cover)
scale = −1 / (maxval − minval)

x < minval :  x' = minval − limit · (1 − exp( scale · (minval − x) ))
x > maxval :  x' = maxval + limit · (1 − exp( scale · (x − maxval) ))
sonst      :  x' = x                                   ← Innenbereich bleibt UNVERAENDERT
```

```python
def clean_tails(raw, tail_frac=0.05):
    x     = np.asarray(raw, dtype=float).copy()
    n     = len(x)
    cover = 1.0 - 2.0 * tail_frac
    w     = np.sort(x)

    istop = min(int(cover * (n + 1)) - 1, n - 1)
    best, bs, be = np.inf, 0, istop
    for a in range(0, n - istop):                 # jedes moegliche Fenster testen
        rng = w[a + istop] - w[a]
        if rng < best:
            best, bs, be = rng, a, a + istop

    minval, maxval = w[bs], w[be]
    if maxval <= minval:                          # seltener Pathologiefall
        maxval *= 1 + 1e-10
        minval *= 1 - 1e-10

    limit = (maxval - minval) * (1.0 - cover)
    scale = -1.0 / (maxval - minval)
    lo = x < minval
    hi = x > maxval
    x[lo] = minval - limit * (1.0 - np.exp(scale * (minval - x[lo])))
    x[hi] = maxval + limit * (1.0 - np.exp(scale * (x[hi] - maxval)))
    return x
```

Die Konstruktion erfüllt drei Eigenschaften, die Masters explizit nachzuprüfen bittet: `limit`
begrenzt den Überstand der transformierten Randwerte; die Werte **bei** `minval`/`maxval` und alles
dazwischen bleiben unverändert; die Abbildung ist monoton. (`limit` als
`(maxval−minval)·(1−cover)` ist Masters' eigene Heuristik — „feel free to disagree".)
`scale` normiert auf die Datenskala, das Verfahren ist damit einheitenunabhängig.

Die Suche nach dem Fenster **kleinster Spannweite** ist der Clou: sie definiert „Tail" datengetrieben
als das, was außerhalb des dichtesten Bereichs liegt — statt über feste Perzentile.

### Messergebnis (ENTROPY auf S&P 500, 20 Bins)

Aufruf: `ENTROPY Lookback Nbins Version Filename`.

| Indikator | Lookback 20 | Lookback 7 |
|---|---|---|
| *Trend* (log-Preisänderung/Bar, Kleinste-Quadrate) | 0,580 | 0,483 |
| *Volatility* (ATR, Standarddefinition) | 0,639 | 0,559 |
| *Expansion* (absichtlich schlecht: Range-Verhältnis) | 0,461 | **0,000** |
| *RawJump* (Close vs. exponentiell geglätteter Close) | 0,484 | 0,395 |
| ***CleanedJump*** (RawJump + 5 %-Tail-Cleaning) | **0,958** | **0,952** |

Drei Lehren:

1. Trend und Volatilität sind gerade noch akzeptabel und bräuchten etwas Nachbearbeitung —
   „something gentle would likely do".
2. Ein instabiles **Verhältnis** als Indikator (`Expansion` = jüngere Preis-Range geteilt durch
   ältere) **kollabiert bei kurzem Lookback vollständig auf 0,000**. Das ist Masters' Musterbeispiel
   dafür, wie man einen Indikator *nicht* baut — und dafür, dass die Entropie diesen Defekt
   sichtbar macht.
3. Reines Tail-Cleaning der äußeren 5 % hebt denselben Indikator von „schlecht" (0,484) auf
   „exzellent" (0,958), **ohne sonst irgendetwas zu ändern**.

## Bezug zu diesem Projekt

`tools/analyze_ohlc.py` erzeugt Detektorausgaben (FVG-Größe, Displacement-Stärke,
Sweep-Penetration, Macro-Expansion), die faktisch Indikatoren sind — geprüft wurde bisher weder
Stationarität noch Entropie. Besonders relevant, weil mehrere davon **Verhältnisse** oder
Größenmaße mit gelegentlichen Extremwerten sind (News-Tage) — also genau die beiden Kategorien,
die im `Expansion`- bzw. `RawJump`-Beispiel oben durchfallen.

Konkret machbar ohne neue Abhängigkeiten: `entropy()` und `gap_analyze()` sind je ein Dutzend
Zeilen Standardbibliothek/numpy und ließen sich als Prüfschritt an `backtest_ohlc.py` anhängen.

Einzuordnen als Vorstufe zu [[Directional Change & Hierarchische Marktstruktur]] (ATR-adaptive,
also selbst schon stationaritätsbewusste Skalierung) und als Vorarbeit für
[[Regularisiertes lineares Modell (Ridge, Lasso, Elastic Net)]] — Masters' Reihenfolge ist
eindeutig: **erst Indikatorqualität, dann Modell.**
