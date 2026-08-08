---
tags: [concept, algo-methodology, modelle]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[Testing and Tuning Market Trading Systems (Source)]]"]
---

# Regularisiertes lineares Modell (Ridge, Lasso, Elastic Net)

Masters' einzige Modellempfehlung im ganzen Buch — und der Satz, den er als wichtigsten überhaupt
bezeichnet. Aus [[Testing and Tuning Market Trading Systems (Source)]] (Kap. 3).

> *„If I could leave readers of this book with only one thought, it would be this: the strength
> of your indicators is vastly more important than the strength of the predictive model that
> uses them to signal trades."*

Die besten Systeme, die er über die Jahre gesehen hat, nutzten ein einfaches lineares Modell mit
hochwertigen Indikatoren. Marginale Indikatoren durch ein hochmodernes nichtlineares Modell zu
jagen, in der Hoffnung, es rette die Sache, funktioniert nicht — *garbage in, garbage out*. Sein
Vorgehen: **immer** mit einem linearen Modell anfangen, nur bei klarem Vorteil auf ein
nichtlineares wechseln.

Vorteile eines linearen Modells: overfittet deutlich seltener; ist interpretierbar (man sieht,
wie Indikatorwerte zu Entscheidungen werden); trainiert schnell — was entscheidend ist, weil
[[Monte Carlo Permutation Test (MCPT)]] und
[[Walk-Forward Guard Buffer & Varianz-Inflation]] hunderte bis tausende Neutrainings verlangen.

## Das Modell

Alle Prädiktoren (und das Ziel) auf Mittelwert 0 und Varianz 1 standardisieren, dann ist
`β₀ = 0` und es bleibt `ŷ = xᵀβ`. Minimiert wird nicht der reine Fehler, sondern:

```
RegErr = (1/N)·Σ(yᵢ − xᵀβ)² + 2λ·P_α(β)
P_α(β) = Σ [ (1−α)/2 · βⱼ² + α·|βⱼ| ]
```

- `λ` steuert die **Stärke** der Bestrafung (λ=0 → gewöhnliche Kleinste-Quadrate-Regression).
- `α` steuert die **Art** der Bestrafung:
  - `α = 0` → **Ridge Regression**: verteilt bei korrelierten Prädiktoren das Gewicht
    gleichmäßig auf alle. Bei `m` perfekt korrelierten Prädiktoren bekommt jeder `1/m` des
    Gewichts, das ein einzelner allein bekommen hätte.
  - `α = 1` → **Lasso**: wählt aus einer korrelierten Gruppe den nützlichsten aus, gibt ihm
    großes Gewicht und setzt die übrigen exakt auf null (entfernt sie aus dem Modell).
  - dazwischen → **Elastic Net**. Je größer `α`, desto mehr Nullkoeffizienten.

**Praxiswarnung:** Bei exakt `α = 1` wird das Training numerisch instabil, sobald zwei
Prädiktoren perfekt korreliert sind (das Lasso kann sich nicht entscheiden). Deshalb bei
Lasso-Wunsch `α` knapp unter 1 setzen.

Drei Punkte, die gegenüber gewöhnlicher Regression zu verstehen sind:

1. Das Ergebnis ist **absichtlich** keine Kleinste-Quadrate-Lösung mehr — der In-Sample-Fehler ist
   größer. Genau das ist der Zweck: das Modell soll schlechter darin werden, Rauschen zu lernen.
2. Gewöhnliche Regression reagiert auf stark korrelierte Prädiktoren katastrophal (riesige
   positive Koeffizienten, kompensiert durch riesige negative). Die Regularisierung nicht.
3. Die Variablenauswahl ist der klassischen Vorwärts-Schrittweisen-Selektion überlegen: dort ist
   eine einmal aufgenommene Variable für immer drin, und ein Paar A+B, das nur *gemeinsam* stark
   ist, wird nie gefunden, wenn ein mittelmäßiges C zuerst gewählt wird. Das regularisierte Modell
   lässt Variablen kommen und gehen, während sich der Rest verändert.

## Training: Coordinate Descent auf einem Lambda-Pfad

Das Kriterium hat unter realistischen Bedingungen genau ein Minimum, also genügt reihum je ein
Gewicht zu aktualisieren:

```
rᵢ        = yᵢ − ŷᵢ                                        (Residuum)
argumentⱼ = (1/N)·Σ xᵢⱼ·rᵢ + βⱼ
S(z,g)    = z−g falls z>0 und g<z;  z+g falls z<0 und g<−z;  sonst 0
β̂ⱼ        = S(argumentⱼ, λα) / (1 + λ(1−α))
```

Zwei Beschleuniger:

- **Active Set.** Einmal auf null gefallene Gewichte bleiben meist null. Also: ein voller Durchlauf,
  danach nur noch die Nicht-Null-Gewichte, bis Konvergenz; dann ein voller Kontrolldurchlauf.
  Ändert sich dabei nichts mehr, ist man fertig.
- **Covariance Updates.** Bei `N ≫ K` (Normalfall im Trading) lässt sich `argumentⱼ` über
  vorberechnete Kreuzprodukte `Xinner`/`Yinner` bilden — die Iteration summiert dann über `K`
  statt über `N` Terme.

**Lambda-Pfad statt Einzelwert.** Es gibt ein kleinstes `λ`, bei dem alle Gewichte null bleiben
(`max_j |Σ xᵢⱼyᵢ| / N / α`). Von dort startet man knapp darunter und senkt `λ` geometrisch bis auf
1/1000 des Startwerts, jedes Mal mit **Warm Start** (Fortsetzung von den bisherigen Gewichten).
Das ist nicht nur stabiler, sondern oft **schneller** als ein einzelner Lauf bei kleinem `λ` — und
liefert nebenbei die Tabelle „λ / Anzahl aktiver Prädiktoren / erklärte Varianz" zur manuellen
Auswahl.

`λ` selbst wird per Cross Validation optimiert (pro Fold den Pfad durchlaufen, OOS-erklärte
Varianz je `λ` über alle Folds aufsummieren, bestes nehmen). Hier ist CV vertretbar, weil es um
Modellkomplexität geht — siehe [[Cross Validation vs. Walk-Forward (Masters)]].

## Beispiel CD_MA auf OEX

300 Indikatoren aus Moving-Average-Oszillatoren (30 lange × 10 kurze Lookbacks), Ziel: log-Änderung
zum nächsten Tag, ein Jahr als Testsatz zurückgehalten.

- `λ=0` (keine Regularisierung): maximale In-Sample-Güte (1,63 % der Zielvarianz erklärt),
  praktisch alle Indikatoren im Modell — und **die schlechteste OOS-Leistung** der drei Läufe.
- `α=0,1` (fast Ridge): In-Sample-Güte fällt, **OOS-Leistung am besten**. Duplizierte Indikatoren
  bekommen erwartungsgemäß gleiche Gewichte.
- `α=0,9` (fast Lasso): minimiert die Zahl der Indikatoren, wirft dabei nützliche mit weg,
  OOS-Leistung bricht ein.

Und ein inhaltlicher Nebenbefund: **alle** Koeffizienten der regularisierten Modelle sind negativ —
das gefundene System ist ein Mean-Reversion-System, kein Trendfolger.

## Nichtlinearität ohne nichtlineares Modell

Ein Indikator mit nichtlinearem Bezug zum Ziel ist meist kein Problem — man transformiert ihn.
Tödlich für ein lineares Modell ist die **nichtlineare Wechselwirkung zwischen** Indikatoren.
Dafür genügt oft eine Polynomerweiterung niedrigen Grades:

- Grad 2 bei A, B, C → `A, B, C, A², B², C², AB, AC, BC`. Grad 3 explodiert bereits.
- **Zwingend vorher** auf den natürlichen Bereich −1…1 skalieren: `2(X−Min)/(Max−Min) − 1`.
  Sonst leiden Genauigkeit und Trainingsstabilität.
- Bei Grad 3 statt `X³` besser `0,5·(5X³ − 3X)` verwenden — gleicher Bereich, gleiche
  Nichtlinearität, aber deutlich geringere Korrelation mit `X`.
- Über Grad 3 hinaus: lieber gleich ein nichtlineares Modell (oder Legendre-Polynome).

## Bezug zu diesem Projekt

`algo/` ist bisher rein regelbasiert (`rules.py`, `signals.py`), es gibt kein prädiktives Modell.
Diese Seite ist damit **Vorratswissen** für den Fall, dass aus den Detektoren in
`tools/analyze_ohlc.py` einmal ein Prädiktorensatz gebaut wird. Die relevante Vorarbeit dafür
steht auf [[Indikator-Stationarität & Entropie]] — Masters' Reihenfolge ist eindeutig: erst
Indikatorqualität, dann Modell.

In Python entspricht das Modell `sklearn.linear_model.ElasticNet` bzw. `ElasticNetCV`; ein
Eigenbau nach Buchvorlage wäre unnötig.
