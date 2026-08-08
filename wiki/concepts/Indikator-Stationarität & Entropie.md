---
tags: [concept, algo-methodology, indikatoren, stationaritaet]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[Testing and Tuning Market Trading Systems (Source)]]"]
---

# Indikator-Stationarität & Entropie

Zwei Qualitätsprüfungen, die **vor** der Systementwicklung stattfinden: Wandert mein Indikator
langsam davon? Und trägt er überhaupt Information? Aus
[[Testing and Tuning Market Trading Systems (Source)]] (Kap. 2).

## Stationarität

*Stationarität* = die statistischen Eigenschaften einer Zeitreihe bleiben über die Zeit konstant.
Masters' pragmatische Haltung dazu:

- Märkte und daraus abgeleitete Indikatoren **sind** nichtstationär, immer. Die Frage ist nur, wie
  schlimm, und ob man es reparieren kann.
- **Klassische Stationaritätstests sind sinnlos** — sie sind praktisch immer hochsignifikant. Die
  Antwort kennt man vorher.
- Nichtstationarität kann unendlich viele Formen haben; welche davon einem System schadet, hängt
  vom System ab.

Die eigentliche Gefahr ist nicht das tägliche Zappeln, sondern das **langsame Wandern**: Ein
Indikator, der monate- oder jahrelang in einem Extrembereich hängt und dann in einen anderen
wandert, macht Modelle in genau diesen Phasen unbrauchbar oder legt sie still. Die daraus
folgende Falle im Backtest: hervorragende Performance über einen günstigen Teilabschnitt der
Historie, mittelmäßige überall sonst. **Deshalb immer die Equity-Kurve ansehen, nicht nur die
Gesamtkennzahl** — und Indikatoren plotten.

### STATN-Gap-Analyse

Statt eines Tests eine Messgröße: Für den Indikator das Quantil zu einer Fraktile bestimmen
(0,5 = Median). Dann durch die Historie laufen und zählen, **wie lange der Indikator am Stück auf
derselben Seite dieser Schwelle bleibt**. Die Laufzeiten werden in Bins gezählt
(1, 2, 4, 8, …, 512, >512 Bars). Viele lange Läufe = gefährliches Wandern.

Masters' Beispiel (OEX, Lookback 100, Median):

| Gap | roh | Version 1 | Version 3 |
|---|---|---|---|
| **Trend** 256 | 18 | 15 | 21 |
| **Trend** 512 | 3 | 1 | 1 |
| **Volatilität** 256 | 9 | 23 | 18 |
| **Volatilität** 512 | 2 | 5 | 9 |
| **Volatilität** >512 | **6** | 0 | 1 |

Der rohe Trendindikator bleibt dreimal über 256 Bars (mehr als zwei Jahre) auf derselben
Median-Seite; die Volatilität sechsmal über 512 Bars. „Volatility generally has extreme
nonstationarity."

### Drei Reparaturen, in aufsteigender Härte

1. **Oszillieren gegen den eigenen Lag** (Version 1): `Indikator(t) − Indikator(t − lookback)`.
   Wirkt am stärksten, verwirft aber die meiste Information über den *absoluten* Wert.
2. **Kurz minus lang** (Version >1): denselben Indikator mit kurzem und langem Lookback rechnen
   und subtrahieren. Kompromiss — über die Länge des zweiten Lookbacks lässt sich der
   Trade-off feinsteuern (langer Lookback = mehr Absolutinformation erhalten, weniger
   Stationaritätsgewinn).
3. **Rollendes Fenster normieren**: laufenden Mittelwert (bzw. Median bei Ausreißern) abziehen
   und durch die laufende Standardabweichung (bzw. Interquartilsabstand) teilen. Kurzes Fenster =
   nahezu erzwungene Stationarität bei fast vollständigem Verlust der Absolutinformation.

Masters' Erfahrung: der **relative** Wert trägt meistens *mehr* Vorhersagekraft als der absolute —
aber nicht immer, der Trade-off bleibt bewusst zu treffen.

## Entropie

Shannons Informationsmaß, angewandt auf Indikatoren: `H(X) = −Σ p(x)·log p(x)`.
Maximal ist `H` bei Gleichverteilung, dann gilt `H = log(K)`. Interessant ist deshalb die
**relative Entropie** `H(X)/log(K)` zwischen 0 und 1.

Berechnung: den **gesamten Wertebereich** in gleich **breite** Bins teilen (nicht gleich *volle*
— das gäbe immer 1), Anteile zählen, einsetzen, durch `log(nbins)` teilen. Bei mehreren tausend
Datenpunkten sind ~20 Bins sinnvoll. **Warnsignal:** Ändert sich die Entropie bei leicht
veränderter Bin-Zahl stark, stimmt etwas mit den Daten oder dem Indikator nicht — Histogramm
ansehen.

Masters' Schwelle: **relative Entropie ≥ 0,5**, unter 0,1 ist ernsthaft reparaturbedürftig.

Warum das praktisch zählt: niedrige Entropie korreliert stark mit schlechter Modelltrainierbarkeit.
Zwei typische Ursachen:

- **Ausreißer.** Ein einzelner Extremwert zieht die Entscheidungsgrenze eines Klassifikators zu
  sich hin und verdirbt die Trennung der übrigen Fälle — auch bei nichtlinearen Modellen.
- **Klumpung.** Eine exogene Bedingung verschiebt die Hälfte der Fälle um einen festen Offset
  (Werte um 1,0 vs. um 100,0). Das Modell fokussiert dann auf die Clusterzugehörigkeit statt auf
  die eigentliche Information.

Wichtige Einschränkung: Entropie misst **Informationsmenge**, nicht Relevanz. Ein Indikator kann
hochentrop sein und trotzdem nichts über die gesuchte Zielgröße sagen. Umgekehrt gilt aber: wenig
Entropie ⇒ wahrscheinlich wenig Wert. Entropie ist eine **obere Schranke**.

### Entropie verbessern

Grundregel: jede Umformung muss **monoton** sein (ordnungserhaltend). Sonst geht die Eigenschaft
verloren, dass eine trennende Schwelle vor der Transformation auch danach existiert. **Truncation
(Kappen auf einen Grenzwert) verletzt genau das und ist deshalb schlecht.**

- Division durch etwas, das klein werden kann → grundsätzlich riskant.
- Nur rechtes Ende schwer: Wurzel/Kubikwurzel, bei schweren Fällen Log.
- Beide Enden schwer: Kubikwurzel.
- Extrem schwere Enden: `tanh` oder Logistik (vorher passend skalieren; bei Logistik danach 0,5
  abziehen).
- Passende theoretische Verteilung vorhanden: deren CDF anwenden (Normal-CDF bei
  glockenähnlichen Oszillatoren, F-CDF bei Varianzverhältnissen).
- Brute Force bei Klumpung: Stichprobe sortieren, jeder Wert wird durch die Anzahl der
  kleiner-gleichen Elemente ersetzt (Binärsuche), durch `n` teilen, 0,5 abziehen → Bereich
  −0,5…0,5, relative Entropie fast 1.
- Wenn Extremwerte *bedeutsam* sind, aber nicht zu extrem sein sollen: erst gleichverteilt
  transformieren, dann die **inverse Normal-CDF** anwenden — moderate Enden bleiben erhalten.

### Monotones Tail-Cleaning

Für den häufigen Fall „Verteilung ist okay, nur gelegentliche Ausreißer stören":

1. Daten sortieren, `cover = 1 − 2·tail_frac` (typisch `tail_frac` 0,01–0,1).
2. Über alle zusammenhängenden Fenster dieser Abdeckung laufen und das mit der **kleinsten
   Spannweite** suchen → `minval`, `maxval`. Alles außerhalb ist per Definition „Tail".
3. Nur die Tails umformen, monoton und mit begrenztem Überstand:
   `limit = (maxval − minval)·(1 − cover)`, `scale = −1/(maxval − minval)`
   - links: `x = minval − limit·(1 − exp(scale·(minval − x)))`
   - rechts: `x = maxval + limit·(1 − exp(scale·(x − maxval)))`

Der Innenbereich bleibt **unverändert**, die Ordnung bleibt erhalten.

Wirkung im `ENTROPY`-Programm auf S&P 500 (20 Bins):

| Indikator | Lookback 20 | Lookback 7 |
|---|---|---|
| Trend | 0,580 | 0,483 |
| Volatilität | 0,639 | 0,559 |
| Expansion (absichtlich schlecht: Range-Verhältnis) | 0,461 | **0,000** |
| RawJump | 0,484 | 0,395 |
| **CleanedJump** (RawJump + 5 %-Tail-Cleaning) | **0,958** | **0,952** |

Zwei Lehren: ein instabiles **Verhältnis** als Indikator kann bei kurzem Lookback komplett
kollabieren (0,000) — und reines Tail-Cleaning der äußeren 5 % hebt denselben Indikator von
„schlecht" auf „exzellent", ohne sonst irgendetwas zu ändern.

## Bezug zu diesem Projekt

`tools/analyze_ohlc.py` erzeugt Detektorausgaben (FVG-Größe, Displacement-Stärke,
Sweep-Penetration, Macro-Expansion), die faktisch Indikatoren sind — geprüft wurde bisher weder
Stationarität noch Entropie. Besonders relevant, weil mehrere davon **Verhältnisse** oder
Größenmaße mit gelegentlichen Extremwerten sind (News-Tage), also genau die Kategorie, für die
Tail-Cleaning gedacht ist. Als Vorstufe zu [[Directional Change & Hierarchische Marktstruktur]]
(ATR-adaptive, also selbst schon stationaritätsbewusste Skalierung) einzuordnen.
