---
tags: [concept, algo-methodology, validation, walk-forward, referenz]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[Testing and Tuning Market Trading Systems (Source)]]"]
---

# Nested Walkforward

Walk-Forward **innerhalb** von Walk-Forward. Notwendig, sobald zwei Optimierungsstufen
übereinanderliegen — die zweite Stufe darf nur auf **OOS-Ergebnissen** der ersten aufsetzen.
Aus [[Testing and Tuning Market Trading Systems (Source)]] (Kap. 5, Programm `CHOOSER.CPP`).

## Wann es zwingend ist

Immer, wenn laufend zwischen konkurrierenden Systemen, Instrumenten oder Kennzahlen ausgewählt
wird. Masters' drei Beispiele:

- Mehrere Systeme für verschiedene Marktregime (Trendfolger, Mean Reversion, Channel Breakout) —
  gehandelt wird das zuletzt beste.
- Ein System auf vielen Aktien, wobei verschiedene Branchen zu verschiedenen Zeiten am besten
  darauf reagieren — gehandelt werden die zuletzt besten Titel.
- Man weiß nicht, ob mittlere Rendite, Sharpe oder Profit Factor das richtige Auswahlkriterium
  ist, und lässt **auch das** mitlaufen.

Der Grund ist [[Training Bias & Selection Bias]]: In-Sample-Performance sagt nichts über die
Zukunft, also darf die Auswahlstufe niemals auf IS-Zahlen der ersten Stufe schauen. Die zweite
Stufe braucht eine eigene Quelle unverzerrter Zahlen — die liefert nur ein inneres Walk-Forward
(**Level-1**). Und die Entscheidungen von Level-2 müssen ihrerseits OOS bewertet werden
(**Level-2**-Walk-Forward).

Die naheliegende Abkürzung — alles in einen Topf werfen und gemeinsam optimieren — ist genau der
Fehler: *„the second stage must be based on OOS results from the first stage."*

## Ablauf am Miniaturbeispiel

Level-1-Lookback `IS_n = 10` Bars, Level-2-Lookback `OOS1_n = 3` Bars:

```
Bars  1-10  → Konkurrenten trainieren; Bar 11 testen  → 1. Level-1-OOS-Fall
Bars  2-11  → Konkurrenten trainieren; Bar 12 testen  → 2. Level-1-OOS-Fall
Bars  3-12  → Konkurrenten trainieren; Bar 13 testen  → 3. Level-1-OOS-Fall
        ── jetzt genug Level-1-OOS-Faelle fuer Level-2 ──
Level-1-OOS-Bars 11-13 → Level-2 trainieren; Bar 14 testen → 1. VOLL-OOS-Fall
Bars  4-13  → Konkurrenten trainieren; Bar 14 testen  → neuer Level-1-OOS-Fall
Level-1-OOS-Bars 12-14 → Level-2 trainieren; Bar 15 testen → 2. VOLL-OOS-Fall
… beide Fenster weiterschieben, bis die Historie erschoepft ist
```

## Die Indexvariablen

| Variable | Bedeutung |
|---|---|
| `n_cases` | Bars in der Preishistorie |
| `n_competitors` | Zahl der konkurrierenden Systeme |
| `IS_n` | Level-1-Lookback: Bars Historie je Handelsentscheidung |
| `OOS1_n` | Level-2-Lookback: Level-1-OOS-Returns, die der Selektor anschaut |
| `OOS1[c][j]` | Matrix `n_competitors × n_cases`; Rendite auf Bar `j` aus der Entscheidung von Bar `j−1`. **Die ersten `IS_n` Spalten sind undefiniert.** |
| `OOS2[j]` | Renditen des jeweils gewählten Systems — **das eigentliche Ziel** |
| `IS_start` | Startbar des Trainingsfensters, wandert mit |
| `OOS1_start` / `OOS1_end` | Fenster der Level-1-OOS-Returns; `OOS1_end` ist zugleich der Schreibindex |
| `OOS2_start` | **fix** bei `IS_n + OOS1_n` |
| `OOS2_end` | Schreibindex der Level-2-Returns |

## Der Algorithmus

```
IS_start   = 0
OOS1_start = OOS1_end = IS_n
OOS2_start = OOS2_end = IS_n + OOS1_n

Endlosschleife:
    # (1) alle Konkurrenten am aktuellen Fenster auswerten
    fuer jeden Konkurrenten c:
        OOS1[c][OOS1_end] = criterion_1(c, IS_n, IS_start, prices)
        # criterion_1 optimiert c auf bars[IS_start … IS_start+IS_n-1],
        # entscheidet fuer Bar OOS1_end und liefert DEREN Rendite

    # (2) Abbruch, wenn keine Bar mehr fuer OOS2 uebrig ist
    if OOS1_end >= n_cases - 1: break

    # (3) Fenster vorruecken, die immer vorruecken
    IS_start  += 1
    OOS1_end  += 1

    # (4) Aufwaermphase — noch nicht genug Level-1-OOS-Faelle
    if OOS1_end - OOS1_start < OOS1_n: continue

    # (5) besten Konkurrenten anhand seiner OOS1-Historie waehlen
    ibest = argmax_c  criterion_2( OOS1[c][OOS1_start … OOS1_end-1] )

    # (6) diesen Konkurrenten OOS testen — Bar OOS2_end ist NICHT in der Entscheidung enthalten
    position = trade_decision(ibest, IS_n, OOS2_end - IS_n, prices)
    OOS2[OOS2_end] = ( +diff  if position > 0 else
                       −diff  if position < 0 else 0.0 )
                     mit diff = prices[OOS2_end] − prices[OOS2_end-1]

    # (7) restliche Fenster vorruecken
    OOS1_start += 1
    OOS2_end   += 1
```

Am Ende gilt `OOS1_end == OOS2_end == n_cases`.

**Für einen Korb statt eines einzelnen Siegers:** in Schritt (5) `criterion_2` für alle
Konkurrenten berechnen, das Array sortieren und die besten k behalten.

**Fairer Vergleich in der Auswertung:** Die mittlere Performance jedes Konkurrenten wird
ausschließlich über `OOS2_start … OOS2_end` gemittelt, obwohl in `OOS1` mehr Daten stehen — sonst
verglichen man verschieden lange Zeiträume.

```
crit_perf[c] = mean( OOS1[c][OOS2_start … OOS2_end-1] )
final_perf   = mean( OOS2[OOS2_start … OOS2_end-1] )
```

Annualisierung bei Tages-Bars: `× 25200` (≈ 252 Handelstage × 100 %, weil Log-Renditen näherungsweise
Bruchteile sind).

## Praxisbeispiel CHOOSER: zwei Auswahlebenen

`CHOOSER.CPP` variiert das Schema leicht: Level 1 wählt aus vielen **Märkten**, Level 2 wählt das
**Kriterium**, mit dem gewählt wird. Aufruf:

```
CHOOSER Markets.txt IS_n OOS1_n MC_reps
CHOOSER Markets.txt 1000 100 100
```

Die drei konkurrierenden Kriterien, jeweils auf Log-Preisen:

```python
def total_return(p):   return p[-1] - p[0]

def sharpe_ratio(p):
    mean = (p[-1] - p[0]) / (len(p) - 1.0)
    var  = 1e-60 + np.sum((np.diff(p) - mean) ** 2)
    return mean / np.sqrt(var / (len(p) - 1))

def profit_factor(p):
    d = np.diff(p)
    return (d[d > 0].sum() + 1e-60) / (-d[d < 0].sum() + 1e-60)
```

Die Kernschleife:

```python
IS_start = 0
OOS1_start = OOS1_end = IS_n
OOS2_start = OOS2_end = IS_n + OOS1_n

while True:
    # (1) je Kriterium den besten Markt waehlen, dessen Naechst-Bar-Rendite notieren
    for icrit in range(n_criteria):
        ibest = max(range(n_markets),
                    key=lambda m: criterion(icrit, close[m][IS_start : IS_start + IS_n]))
        OOS1[icrit][OOS1_end] = close[ibest][OOS1_end] - close[ibest][OOS1_end - 1]

    if OOS1_end >= n_cases - 1:
        break
    IS_start += 1
    OOS1_end += 1
    if OOS1_end - OOS1_start < OOS1_n:
        continue

    # (2) zuverlaessigstes Kriterium = groesster Gesamt-OOS-Return im Rueckblickfenster
    ibestcrit = max(range(n_criteria),
                    key=lambda c: OOS1[c][OOS1_start:OOS1_end].sum())
    crit_count[ibestcrit] += 1

    # (3) mit diesem Kriterium den Markt fuer den naechsten Bar waehlen
    ibest = max(range(n_markets),
                key=lambda m: criterion(ibestcrit, close[m][OOS2_end - IS_n : OOS2_end]))
    OOS2[OOS2_end] = close[ibest][OOS2_end] - close[ibest][OOS2_end - 1]

    OOS1_start += 1
    OOS2_end   += 1
```

Als Kompetenzmaß der Kriterien in Schritt (2) genügt der **Gesamtreturn** — „a decent measure",
so Masters; hier eine weitere Kennzahl zu schachteln wäre Überbau.

**Datenvoraussetzung:** alle Märkte müssen zu **jedem** Bar einen Preis haben. Fehlt ein Datum bei
einem Markt, muss dieser Bar bei allen entfernt werden. Der Kompressionsalgorithmus dafür steht
auf [[Monte Carlo Permutation Test (MCPT)]] (er wird für die Permutation ohnehin gebraucht).

## Ergebnis: 65 S&P-100-Titel, 1986–2017

7.725 Handelstage, `IS_n = 1000`, `OOS1_n = 100`, 1.000 Monte-Carlo-Permutationen.
Alle Renditen `× 25200` annualisiert.

| | Rendite p.a. | P-Wert | Anteil gewählt |
|---|---|---|---|
| Gleichgewichteter Korb (Buy & Hold) | 8,7473 % | — | — |
| nur Total Return als Kriterium | 17,8898 % | 0,076 | 67,8 % |
| nur Sharpe Ratio | 12,9834 % | 0,138 | 21,1 % |
| nur Profit Factor | 12,2799 % | 0,180 | 11,1 % |
| **Kriterienwahl mitlaufend (Level-2)** | **19,1151 %** | **0,027** | — |

Die Pointe steckt in den P-Werten: die einzelnen Kriterien sind je für sich nur schwach
signifikant (0,076–0,180), das geschachtelte Verfahren aber deutlich (**0,027**). Die adaptive
Kriterienwahl ist also nicht nur nominell besser, sondern statistisch belastbarer.

Nebenbefund: Total Return wird in zwei Dritteln der Fälle als zuverlässigstes Kriterium gewählt —
aber eben nicht immer, und genau die restlichen 32 % machen den Unterschied zwischen 17,89 % und
19,12 %.

## Permutation im geschachtelten Fall

Bei der Kombination mit dem MCPT zerfällt die Historie in **drei** Segmente, die **getrennt**
permutiert werden müssen — weil im unpermutierten Lauf jeweils andere Daten nie in einem
OOS-Block landen:

```
prepare_permute( IS_n,             n_markets, offset=1,             close, work )
prepare_permute( IS_n + OOS1_n,    n_markets, offset=IS_n,          close, work )
prepare_permute( n_cases,          n_markets, offset=IS_n + OOS1_n, close, work )
```

| Segment | warum getrennt |
|---|---|
| `[0 … IS_n)` | erster „Trainings"-Block; taucht nie in einem OOS-Ergebnis auf |
| `[IS_n … IS_n+OOS1_n)` | erster Level-1-OOS-Block; taucht nie im Level-2-OOS auf |
| `[IS_n+OOS1_n … Ende)` | der eigentlich interessierende Voll-OOS-Bereich |

Würde man alles in einen Topf permutieren, könnten ungewöhnliche Kursbewegungen (starker Trend,
Volatilitätsspitze) aus Segment 1 in den OOS-Bereich wandern und dort Ergebnisse erzeugen, die im
Originallauf gar nicht möglich waren. Das Permutieren des ersten Segments selbst hält Masters für
folgenlos („I am not aware of any pros or cons") und tut es aus pädagogischen Gründen mit.

**Segmentgrenzen dürfen sich nicht überlappen**, einschließlich des jeweiligen „Basis"-Falls bei
`offset−1` — Details auf [[Monte Carlo Permutation Test (MCPT)]].

## Bezug zu diesem Projekt

`algo/signals.py` / `algo/backtest_ensemble.py` kombinieren mehrere Regeln zu einem Ensemble.
Solange die Gewichtung **statisch** ist, greift dieses Kapitel nicht. Sobald daraus eine *Auswahl*
wird — „heute handelt die Regel, die zuletzt am besten lief" —, reicht der einschichtige
Walk-Forward in `algo/validate.py` nicht mehr aus, und alle dort berichteten Zahlen wären
selection-biased.

Die CHOOSER-Struktur ist überdies direkt auf eine Frage übertragbar, die im Vault offen ist:
*welches Kriterium soll `algo/` überhaupt optimieren?* Statt sich einmalig für Profit Factor oder
Sharpe zu entscheiden, ließe sich diese Wahl mitlaufen lassen — mit dem Nachweis, dass sie
Mehrwert bringt.

Siehe auch [[Cross Validation vs. Walk-Forward (Masters)]] (dort die deutlich einfacher zu
implementierende Variante CV-in-Walk-Forward) und
[[CSCV (Combinatorially Symmetric Cross Validation)]].

## Implementierung

Nicht als eigene Funktion portiert (die Indexlogik hängt am konkreten System). Der Permutationsteil ist abgedeckt: `algo/masters.py::permute_multi(data, rng, offset)` dreimal mit den drei Segmentgrenzen aufrufen.

Selbstcheck: `python algo/masters.py` (auch in `algo/selfcheck.py`).
