---
tags: [concept, algo-methodology, modelle, referenz]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[Testing and Tuning Market Trading Systems (Source)]]"]
---

# Regularisiertes lineares Modell (Ridge, Lasso, Elastic Net)

Masters' einzige Modellempfehlung im ganzen Buch — und der Satz, den er als wichtigsten überhaupt
bezeichnet. Aus [[Testing and Tuning Market Trading Systems (Source)]] (Kap. 3, Programme
`CDMODEL.CPP`, `CD_MA.CPP`), Verfahren nach Friedman/Hastie/Tibshirani, *„Regularization Paths for
Generalized Linear Models via Coordinate Descent"* (J. Stat. Software, Jan. 2010).

> *„If I could leave readers of this book with only one thought, it would be this: the strength of
> your indicators is vastly more important than the strength of the predictive model that uses
> them to signal trades."*

Die besten Systeme, die er über die Jahre gesehen hat, nutzten ein einfaches lineares Modell mit
hochwertigen Indikatoren. Marginale Indikatoren durch ein hochmodernes nichtlineares Modell zu
jagen, in der Hoffnung, es rette die Sache, funktioniert nicht — *garbage in, garbage out*. Sein
Vorgehen: **immer** mit einem linearen Modell anfangen, nur bei klarem Vorteil wechseln.

Fünf Gründe für lineare Modelle:

1. Overfitten deutlich seltener → geringerer Training Bias
   ([[Training Bias & Selection Bias]]).
2. Sind **interpretierbar** — man sieht, wie Indikatorwerte zu Entscheidungen werden.
3. Trainieren schnell. Entscheidend, weil [[Monte Carlo Permutation Test (MCPT)]] und
   [[Walk-Forward Guard Buffer & Varianz-Inflation]] hunderte bis tausende Neutrainings verlangen.
4. Lassen sich leicht **moderat nichtlinear** machen, ohne die anderen Eigenschaften zu verlieren.
5. Lassen sich mit überschaubarem Aufwand **regularisieren**.

## Notation und Modell

```
N      Anzahl Faelle
K      Anzahl Praediktoren
x_ij   Wert von Praediktor j im Fall i
y_i    Zielvariable im Fall i
β      K Koeffizienten (Spaltenvektor)
β₀     Konstante
α      steuert die ART der Regularisierung,   0 ≤ α ≤ 1
λ      steuert den GRAD der Regularisierung,  λ ≥ 0
```

**Alle Prädiktoren werden auf Mittelwert 0 und Varianz 1 standardisiert.** Dann ist `β₀` gleich
dem Mittelwert des Ziels; standardisiert man **auch das Ziel**, ist `β₀ = 0` und fällt komplett
weg. Die Rückrechnung auf Rohwerte ist einfache Algebra.

```
(3-1)  ŷ = β₀ + xᵀβ                    → nach Standardisierung:  ŷ = xᵀβ

(3-2)  RegErr = (1/N) · Σᵢ (yᵢ − xᵀβ)²  +  2λ · P_α(β)

(3-3)  P_α(β) = Σⱼ [ ((1−α)/2) · βⱼ²  +  α · |βⱼ| ]
```

Der Faktor 2 in (3-2) ließe sich in λ oder P absorbieren; er steht dort nur zur Übereinstimmung
mit Zwischenschritten der Originalherleitung. `λ = 0` ergibt die gewöhnliche
Kleinste-Quadrate-Lösung.

### Was α bewirkt

| α | Name | Verhalten bei stark korrelierten Prädiktoren |
|---|---|---|
| 0 | **Ridge Regression** | verteilt das Gewicht **gleichmäßig** auf alle. Bei `m` perfekt korrelierten Prädiktoren bekommt jeder `1/m` des Gewichts, das ein einzelner allein bekommen hätte. |
| 1 | **Lasso** | **wählt einen aus**, gibt ihm großes Gewicht und setzt die übrigen exakt auf null (entfernt sie aus dem Modell). |
| dazwischen | **Elastic Net** | steuerbare Sparsamkeit |

Für jedes feste λ steigt die Zahl der Nullkoeffizienten **monoton** mit α: bei `α = 0` sind alle
Variablen drin, danach fallen sie nach und nach heraus. Über α stellt man also den gewünschten
Grad an Sparsamkeit ein.

> **Praxiswarnung:** Bei exakt `α = 1` wird das Training **numerisch instabil**, sobald zwei
> Prädiktoren perfekt oder nahezu perfekt korreliert sind — das Lasso „verliert den Verstand" bei
> dem Versuch zu entscheiden, welcher der bessere ist. Bei Lasso-Wunsch deshalb α knapp unter 1
> setzen. Das Modell ist praktisch identisch, aber stabil.

Für die typische „Spaghetti-an-die-Wand"-Situation im Trading (viele Kandidaten-Indikatoren)
empfiehlt Masters einen Wert **zwischen** 0 und 1.

### Drei Punkte gegenüber gewöhnlicher Regression

1. Das Ergebnis ist **absichtlich** keine Kleinste-Quadrate-Lösung mehr — der In-Sample-Fehler ist
   größer. Genau das ist der Zweck: das Modell soll schlechter darin werden, Rauschen zu lernen.
   *„That's exactly what we are doing to make it less able to erroneously learn random noise."*
2. Gewöhnliche Regression reagiert auf stark korrelierte Prädiktoren katastrophal: riesige
   positive Koeffizienten, kompensiert durch riesige negative, in einem instabilen Gleichgewicht.
   Die Regularisierung nicht.
3. Die Variablenauswahl ist der **Vorwärts-Schrittweisen-Selektion** überlegen. Dort ist eine
   einmal aufgenommene Variable für immer drin — und ein Paar A+B, das nur *gemeinsam* stark ist,
   wird nie gefunden, wenn ein mittelmäßiges C zuerst gewählt wird. Das regularisierte Modell
   lässt Variablen kommen und gehen, während sich der Rest verändert.

## Die Update-Formeln

```
(3-4)  rᵢ = yᵢ − ŷᵢ                                       Residuum

(3-5)  argumentⱼ = (1/N) · Σᵢ x_ij · rᵢ  +  βⱼ

(3-6)  S(z, g) =  z − g   falls z > 0  und  g < z         Soft-Thresholding
                  z + g   falls z < 0  und  g < −z
                  0       sonst

(3-7)  β̂ⱼ = S(argumentⱼ, λα) / (1 + λ(1−α))
```

Mit **Fallgewichten** `wᵢ` (Summe 1) — im Trading selten gebraucht, aber vorhanden:

```
(3-8)  argumentⱼ = Σᵢ wᵢ · x_ij · ( rᵢ + βⱼ · x_ij )

(3-9)  β̂ⱼ = S(argumentⱼ, λα) / ( Σᵢ wᵢ · x_ij²  +  λ(1−α) )
```

(Übung des Autors: mit `wᵢ = 1/N` reduziert sich (3-8) auf (3-5) und (3-9) auf (3-7) — man braucht
dafür, dass `Σᵢ x_ij² = N` gilt, weil die Prädiktoren auf Varianz 1 standardisiert sind.)

### Schnellvariante über Kovarianz-Updates

Wenn `N ≫ K` — im Trading der Normalfall — lohnt die Umformung, die pro Iteration nur noch über
`K` statt über `N` Terme summiert:

```
(3-10)  argumentⱼ = Yinnerⱼ − Σₖ Xinner_jk · βₖ  +  Xssⱼ · βⱼ

ungewichtet:
(3-11)  Yinnerⱼ    = (1/N) · Σᵢ x_ij · yᵢ
(3-12)  Xinner_jk  = (1/N) · Σᵢ x_ij · x_ik              (= 1 auf der Diagonale, da standardisiert)
        Xssⱼ       = 1

gewichtet:
(3-13)  Xssⱼ       = Σᵢ wᵢ · x_ij²
(3-14)  Yinnerⱼ    = Σᵢ wᵢ · x_ij · yᵢ
(3-15)  Xinner_jk  = Σᵢ wᵢ · x_ij · x_ik
```

(3-13) bis (3-15) hängen nur von den Trainingsdaten ab und werden **einmal** vor dem Training
berechnet. `Xinner` ist symmetrisch; Masters speichert trotzdem die volle Matrix — „wasteful of
very cheap memory, but the simpler addressing saves very expensive time".

## Das Trainingsverfahren

**Active-Set-Strategie:** Einmal auf null gefallene Gewichte bleiben meist null. Also nur die
Nicht-Null-Gewichte („active set") iterieren, mit gelegentlichen vollständigen Kontrollläufen.

```
do_active_only = false
fuer iter = 0 … maxits-1:
    active_set_changed = false
    fuer jede Variable j:
        if do_active_only and β[j] == 0: ueberspringen
        neues β[j] nach (3-7) bzw. (3-9) berechnen
        wechselte β[j] von/nach exakt 0: active_set_changed = true
    converged = Konvergenztest
    if do_active_only:
        if converged: do_active_only = false        # naechste Runde alle pruefen
    else:
        if converged and not active_set_changed: FERTIG
        do_active_only = true
```

`maxits` ist reine Hänger-Versicherung (mehrere tausend) und sollte nie greifen. Der Aufwand
lohnt nur bei vielen Nullgewichten — schadet aber auch sonst nicht.

**Zwei Konvergenztests:**

```
fast_test = 1 :  max_j |Δβ_j| < eps                       schnell, braucht keine Residuen
fast_test = 0 :  |prior_crit − crit| < eps
                 crit = MSE + penalty                     mit penalty nach (3-3), mal 2λ
```

Der langsame Test braucht die Residuen — die bei aktiven Kovarianz-Updates gar nicht mitgeführt
werden und dann eigens berechnet werden müssen. `eps` typisch `1e-5`.

Nebenbei ausgegeben (spielt im Algorithmus keine Rolle): der erklärte Varianzanteil
`explained = (YmeanSquare − MSE) / YmeanSquare`.

**Warm Start:** Training kann von den aktuellen β-Werten aus fortgesetzt werden statt bei null.
Bei der naiven Update-Methode müssen die Residuen dann neu berechnet werden.

### Lambda-Pfad statt Einzelwert

Es gibt ein kleinstes λ, bei dem **alle** Gewichte null bleiben. Aus (3-6) und (3-7) folgt für den
Startzustand (alle β = 0, also `r = y`):

```
(3-16)  |(1/N) · Σᵢ x_ij · yᵢ| < λα               → βⱼ bleibt null   (ungewichtet)
(3-17)  |Σᵢ wᵢ · x_ij · yᵢ|    < λα                                  (gewichtet)

λ_thresh = max_j |…| / α          ← ueber alle Praediktoren maximieren
```

```
max_lambda    = 0.999 · λ_thresh
min_lambda    = 0.001 · max_lambda
lambda_factor = exp( log(min_lambda / max_lambda) / (n_lambda − 1) )

λ = max_lambda
fuer ilambda = 0 … n_lambda-1:
    core_train(α, λ, …, warm_start = (ilambda > 0))
    β-Vektor fuer dieses λ speichern
    λ *= lambda_factor
```

Drei Gewinne auf einmal:

- **Stabilität** — man startet mit einem trivialen Modell (fast alle Gewichte null) und lockert
  schrittweise.
- **Geschwindigkeit** — dank Warm Start beginnt jedes Training nahe der Lösung. Der Pfad kann
  dadurch **schneller** sein als ein einzelner Lauf bei kleinem λ. Deshalb kostet `n_lambda = 50`
  kaum mehr als `n_lambda = 5`.
- **Diagnose** — die Tabelle „λ / Anzahl aktiver Prädiktoren / erklärte Varianz" erlaubt die
  manuelle Auswahl.

### λ per Cross Validation wählen

```
für jeden Fold:
    n_OOS = (n − n_done) / (nfolds − ifold)        # gleich grosse Folds ohne Rest-Problem
    n_IS  = n − n_OOS
    i_OOS = (i_IS + n_IS) mod n                    # zyklisch, wickelt am Datenende um
    lambda_train(...) auf dem IS-Teil
    fuer jedes λ:  quadratischen OOS-Fehler kumulieren
                   (OOS-Faelle mit den TRAININGS-Mittelwerten/-Skalen normieren!)
lambda_OOS[λ] = (YsumSquares − Fehlersumme[λ]) / YsumSquares
return λ mit maximalem lambda_OOS
```

Wichtig: der λ-Schwellenwert wird **einmal auf dem Gesamtdatensatz** bestimmt, damit alle Folds
denselben λ-Pfad durchlaufen und vergleichbar sind. Empfehlung: `n_lambda = 50`, `nfolds` ≥ 5,
besser 10 oder mehr.

Cross Validation ist hier vertretbar, weil es um **Modellkomplexität** geht — siehe
[[Cross Validation vs. Walk-Forward (Masters)]], Abschnitt „die eine Ausnahme".

## Referenzlauf CD_MA auf OEX

```
CD_MA Lookback_inc N_long N_short Alpha Filename
CD_MA 2 30 10 <alpha> OEX.TXT
```

300 Indikatoren aus MA-Oszillatoren (30 lange Lookbacks in 2er-Schritten × 10 kurze), Ziel:
log-Preisänderung zum nächsten Tag, ein Jahr als Testsatz zurückgehalten. Der kurze Lookback ist
`i · langer / (N_short+1)`, abgeschnitten — bei kleinen langen Lookbacks entstehen dadurch
**exakt duplizierte** Indikatoren. Das ist Absicht: es macht gewöhnliche Regression unmöglich und
zeigt, wie die drei Varianten damit umgehen.

| Lauf | In-Sample | Out-of-Sample | Modellgröße |
|---|---|---|---|
| `λ = 0` (keine Regularisierung) | **1,63 % erklärte Varianz** (Maximum) | **schlechteste** | fast alle 300 Indikatoren |
| `α = 0,1` (fast Ridge) | niedriger | **beste** | duplizierte Indikatoren erhalten **gleiche** Gewichte |
| `α = 0,9` (fast Lasso) | niedriger | bricht ein | minimiert die Indikatorzahl, wirft nützliche mit weg |

Das ist die Kernaussage in Zahlen: **maximale In-Sample-Güte und beste OOS-Performance schließen
sich aus.**

Inhaltlicher Nebenbefund: **alle** Koeffizienten der regularisierten Modelle sind **negativ** —
das gefundene System ist ein Mean-Reversion-System, kein Trendfolger.

## Nichtlinearität ohne nichtlineares Modell

Ein Indikator mit nichtlinearem Bezug zum Ziel ist meist **kein** Problem: man transformiert ihn
und die Beziehung wird weitgehend linear. Das sollte man immer zuerst versuchen. Tödlich für ein
lineares Modell ist die **nichtlineare Wechselwirkung zwischen** Indikatoren.

Dafür genügt oft eine Polynomerweiterung niedrigen Grades:

```
Grad 2, Praediktoren A,B,C  →  A, B, C, A², B², C², AB, AC, BC
Grad 3 zusaetzlich          →  A³, B³, C³, A²B, A²C, B²C, AB², AC², BC², ABC
```

Zwei Pflichtmaßnahmen (mathematisch nicht nötig, aber gegen Fließkomma-Ungenauigkeit und für
Trainingsstabilität):

1. **Auf den natürlichen Bereich −1 … 1 skalieren:** `2·(X − Min)/(Max − Min) − 1`. Dann liegen
   auch alle Potenzen und Produkte in diesem Bereich.
2. **Ab Grad 3:** statt `X³` besser `0,5·(5X³ − 3X)` verwenden. Gleicher Bereich, gleiche
   Nichtlinearität, aber deutlich geringere Korrelation mit `X` — das erleichtert vielen
   Trainingsverfahren die Arbeit. „You have nothing to lose and potentially much to gain."

Über Grad 3 hinaus ist nahezu immer sinnlos — dann lieber gleich ein nichtlineares Modell. Wer
partout will: **Legendre-Polynome** für die höheren Terme.

## Bezug zu diesem Projekt

`algo/` ist bisher rein regelbasiert (`rules.py`, `signals.py`), es gibt kein prädiktives Modell.
Diese Seite ist damit **Vorratswissen** für den Fall, dass aus den Detektoren in
`tools/analyze_ohlc.py` einmal ein Prädiktorensatz gebaut wird.

Die relevante Vorarbeit dafür steht auf [[Indikator-Stationarität & Entropie]] — Masters'
Reihenfolge ist eindeutig: **erst Indikatorqualität, dann Modell.** Der Eröffnungssatz dieses
Kapitels ist die stärkste Formulierung dieses Prinzips im ganzen Buch.

In Python entspricht das Modell `sklearn.linear_model.ElasticNet` bzw. `ElasticNetCV`
(`l1_ratio` = Masters' α, `alpha` = Masters' λ — **die Namen sind vertauscht**, hier liegt die
häufigste Verwechslungsquelle). Ein Eigenbau nach Buchvorlage wäre unnötig; die Formeln oben
dienen dem Verständnis der Stellschrauben, nicht der Reimplementierung.

## Implementierung

Bewusst **nicht** portiert — `sklearn.linear_model.ElasticNetCV` deckt das ab. Namensfalle beachten: sklearns `alpha` ist Masters' λ, sklearns `l1_ratio` sein α.

Selbstcheck: `python algo/masters.py` (auch in `algo/selfcheck.py`).
