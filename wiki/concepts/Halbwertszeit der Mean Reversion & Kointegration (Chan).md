---
tags: [concept, algo-methodology, mean-reversion, statistik, referenz]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[Algorithmic Trading - Winning Strategies and Their Rationale (Source)]]"]
---

# Halbwertszeit der Mean Reversion & Kointegration (Chan)

Aus [[Algorithmic Trading - Winning Strategies and Their Rationale (Source)]] (Chan, Kap. 2).
Ergänzt [[Mean-Reversion-Tests (ADF, Hurst-Exponent, Kointegration)]] (Halls-Moore) um die beiden
praktisch wichtigsten Größen: die **Halbwertszeit** und den **Johansen-Test**.

## Zwei äquivalente Sichtweisen, zwei verschiedene Tests

| Sichtweise | Aussage | Test |
|---|---|---|
| **Mean Reversion** | die Preisänderung der nächsten Periode ist proportional zur Differenz zwischen Mittelwert und aktuellem Preis | **ADF** |
| **Stationarität** | die Varianz der Log-Preise wächst **langsamer** als bei einem geometrischen Random Walk (sublinear in der Zeit) | **Hurst / Variance Ratio** |

> „Stationarität" ist ein Missgriff: Sie bedeutet **nicht**, dass die Preise in einer festen Range
> laufen (das wäre Hurst-Exponent 0), sondern nur, dass die Varianz **langsamer als normal
> diffundiert**.

## Die Formeln

```
(2.1)  Δy(t) = λ·y(t−1) + μ + β·t + α₁Δy(t−1) + … + α_k Δy(t−k) + ε
       ADF-Teststatistik  =  λ / SE(λ)          muss NEGATIV und unter dem kritischen Wert liegen

(2.2)  Var(τ) = ⟨ |z(t+τ) − z(t)|² ⟩            z = log(y)
(2.3)  Random Walk:      ⟨…⟩ ∼ τ
(2.4)  allgemein:        ⟨…⟩ ∼ τ^(2H)           H = Hurst-Exponent

       H = 0,5  Random Walk
       H < 0,5  mean-revertierend   (je naeher 0, desto staerker)
       H > 0,5  trendend            (je naeher 1, desto staerker)

       Variance-Ratio-Test:   Var(z(t) − z(t−τ)) / (τ · Var(z(t) − z(t−1)))  = 1 ?

(2.5)  dy(t) = (λ·y(t−1) + μ)·dt + dε           Ornstein-Uhlenbeck
(2.6)  E(y(t)) = y₀·exp(λt) − (μ/λ)·(1 − exp(λt))

       ⟹  HALBWERTSZEIT  =  −log(2) / λ
```

**Zwei Konventionen, die man kennen muss:**

- Die kritischen ADF-Werte hängen von Stichprobengröße und davon ab, ob man einen Mittelwert
  `−μ/λ` und/oder eine Drift `−βt/λ` zulässt. **Praxisregel: Mittelwert ja, Drift nein** (`β = 0`)
  — die konstante Preisdrift ist gegenüber den Tagesschwankungen meist vernachlässigbar.
- Der Lag `k`: mit `k = 0` anfangen, aber oft lässt sich die Nullhypothese **erst mit `k = 1`**
  verwerfen — was bedeutet, dass die Preisänderungen selbst serielle Korrelation aufweisen.

## Die Halbwertszeit ist die praktisch wichtigste Zahl

Die statistischen Tests verlangen 90 % Sicherheit. **Für profitables Handeln braucht man das
oft gar nicht.** Chans Ausweg: `λ` nicht auf Signifikanz prüfen, sondern in eine **Zeitgröße**
übersetzen.

```python
import numpy as np, statsmodels.api as sm

def half_life(y):
    """Halbwertszeit der Mean Reversion aus Gleichung 2.6."""
    y = np.asarray(y, dtype=float)
    ylag  = y[:-1]
    dy    = y[1:] - ylag
    beta  = sm.OLS(dy, sm.add_constant(ylag)).fit().params[1]   # = lambda
    return -np.log(2) / beta
```

Drei Dinge, die sie einem sagt:

1. **`λ > 0`** → die Reihe ist überhaupt nicht mean-revertierend. Gar nicht erst eine
   Mean-Reversion-Strategie darauf schreiben.
2. **`λ ≈ 0`** → sehr lange Halbwertszeit, also wenige Round-Trips pro Zeitraum, also
   unprofitabel — unabhängig davon, ob die Reihe „eigentlich" stationär ist.
3. **`λ` setzt die natürliche Zeitskala aller Strategieparameter.** Bei einer Halbwertszeit von
   20 Tagen ist ein 5-Tage-Lookback für gleitenden Durchschnitt oder Standardabweichung unsinnig.
   **Lookback = (kleines Vielfaches der) Halbwertszeit** ist oft nahezu optimal — und erspart die
   Brute-Force-Optimierung eines freien Parameters, also eine Quelle von Data-Snooping-Bias.

Beispielwerte aus dem Buch:

| Reihe | Halbwertszeit | Bewertung |
|---|---|---|
| USD.CAD | **115 Tage** | grenzwertig, je nach Horizont zu lang |
| EWA-EWC-IGE (Johansen-Eigenvektor) | **23 Tage** | deutlich besser geeignet |
| CL 12-Monats-Kalenderspread | **36 Tage** | brauchbar |

Bemerkenswert: USD.CAD **bestand die Stationaritätstests nicht** (ADF −1,84 gegen kritische
−2,594; Variance Ratio p = 0,367; H = 0,49) — und war mit einer simplen linearen
Mean-Reversion-Strategie trotzdem profitabel. Genau dafür ist die Halbwertszeit da.

## Warum diese Vortests überhaupt, statt gleich zu backtesten?

Chans Begründung ist methodisch wichtig:

- Die Tests nutzen **jede einzelne Bar**, ein Backtest dagegen nur die (viel selteneren)
  Round-Trip-Trades. Die statistische Signifikanz ist deshalb **höher**.
- Ein Backtest-Ergebnis hängt an den Spezifika *einer* Strategie mit *einem* Parametersatz. Die
  Tests hängen nur an der Preisreihe.

> Besteht eine Reihe die Stationaritätstests oder hat wenigstens eine kurze Halbwertszeit, kann
> man sicher sein, **irgendeine** profitable Strategie darauf zu finden — vielleicht nur nicht
> die, die man gerade gebacktestet hat.

## Kointegration: künstlich stationäre Portfolios bauen

Die wenigsten handelbaren Preisreihen sind von sich aus stationär. Man kann aber mehrere nicht
stationäre Reihen so **kombinieren**, dass der Marktwert des Portfolios stationär ist — das ist
Kointegration.

### CADF (Engle-Granger, nur für Paare)

Hedge Ratio per linearer Regression bestimmen, Portfolio bilden, darauf den ADF-Test laufen
lassen.

**Der Haken: Der Test ist reihenfolgeabhängig.** Vertauscht man abhängige und unabhängige
Variable, bekommt man eine **andere** Hedge Ratio — und die ist **nicht** der Kehrwert der
ersten. Häufig führt nur **eine** der beiden zu einem stationären Portfolio. Man muss also beide
Richtungen probieren und die mit der negativsten t-Statistik nehmen.

Beispiel EWA/EWC: CADF −3,643 gegen kritische −3,359 (95 %) → kointegriert.

### Johansen (beliebig viele Reihen)

Verallgemeinerung von (2.1) auf Vektoren:

```
(2.7)  ΔY(t) = Λ·Y(t−1) + M + A₁ΔY(t−1) + … + A_k ΔY(t−k) + ε

       r = Rang von Λ = Anzahl unabhaengiger kointegrierender Beziehungen
       Λ = 0  ⟹  keine Kointegration
```

Der Test liefert zwei Statistiken (**Trace** und **Eigen**) mit kritischen Werten für die
Hypothesen `r = 0`, `r ≤ 1`, … `r ≤ n−1`.

**Drei entscheidende Vorteile gegenüber CADF:**

1. **Reihenfolgeunabhängig** — ein Lauf liefert alle unabhängigen kointegrierenden Beziehungen.
2. Funktioniert für **beliebig viele** Reihen (Chans Implementierung: max. 12 Symbole).
3. **Die Eigenvektoren sind direkt die Hedge Ratios** — als nützliches Nebenprodukt.

**Die Auswahlregel, die man kennen muss:** Die Eigenvektoren sind nach absteigenden Eigenwerten
sortiert. Der **erste** ist die „stärkste" kointegrierende Beziehung — also die mit der
**kürzesten Halbwertszeit**. Den nimmt man.

Warum es bei zwei Reihen **zwei** kointegrierende Beziehungen geben kann: genau wegen der
Reihenfolgeabhängigkeit von CADF — die beiden nicht-reziproken Hedge Ratios spannen zwei
unabhängige stationäre Portfolios auf.

Beispielausgabe (EWA, EWC, IGE): drei kointegrierende Beziehungen mit 95 %; Eigenwerte 0,0112 /
0,0087 / 0,0030; erster Eigenvektor `[−1,0460, 0,7600, 0,2233]` → Halbwertszeit 23 Tage.

## Die parameterlose lineare Strategie

Chans Referenzstrategie, bewusst so gebaut, dass sie **keinen** Parameter zum Optimieren hat:

```
Anzahl Einheiten des Unit-Portfolios  =  − Z-Score seines Marktwerts
Lookback fuer Mittelwert/Std          =  Halbwertszeit
```

```python
lookback  = round(half_life(yport))
z         = (yport - yport.rolling(lookback).mean()) / yport.rolling(lookback).std()
num_units = -z                                  # negativ proportional
positions = num_units[:, None] * hedge_ratios * prices
pnl       = (positions.shift(1) * prices.pct_change()).sum(axis=1)
```

Sie ist **nicht praktisch handelbar** (unbegrenzter Kapitalbedarf, infinitesimales Rebalancing),
aber als **Diagnosewerkzeug** wertvoll: Sie zeigt ohne jeden Data-Snooping-Bias, ob sich aus einer
Reihe überhaupt Gewinn ziehen lässt, und erzeugt wegen des ständigen Ein- und Aussteigens mehr
statistische Signifikanz als jede selektivere Regel.

Ergebnis auf EWA-EWC-IGE: **APR 12,6 %, Sharpe 1,4**.

**Warum überhaupt gleitender Mittelwert bei einer „stationären" Reihe?** Weil der Mittelwert sich
durch Wirtschafts- oder Managementänderungen langsam verschiebt — und weil selbst eine stationäre
Reihe mit `0 < H < 0,5` laut (2.4) eine **mit der Zeit wachsende Varianz** hat, nur langsamer als
ein Random Walk.

## Preis-Spread, Log-Preis-Spread oder Verhältnis?

```
(3.1)  y = h₁y₁ + h₂y₂ + … + h_n y_n         → h = ANZAHL SHARES, feste Stueckzahl
(3.2)  y = y₁ − h·y₂                          Spezialfall Paar
(3.3)  log(q) = h₁log(y₁) + … + h_n log(y_n)  → h = KAPITALGEWICHTE, fester Geldbetrag
```

Die Herleitung für (3.3): `Δlog(x) ≈ Δx/x`, also ist die rechte Seite von (3.4) die **Rendite**
eines Portfolios mit konstanten Kapitalgewichten. Konsequenz: Log-Preise implizieren
**tägliches Rebalancing** (samt Transaktionskosten), Preise implizieren feste Stückzahlen.

| Verwenden | Wann |
|---|---|
| **Preis**-Spread | feste Stückzahl über die Trade-Dauer gewünscht — der einfachere Fall |
| **Log-Preis**-Spread | feste Kapitalgewichte gewünscht; erfordert ständiges Rebalancing |
| **Verhältnis** `y₁/y₂` | nur korrekt, wenn `h₁ = −h₂`. Aber: bei **nicht wirklich kointegrierenden** Paaren oft besser, weil skaleninvariant. Beispiel: A=$10/B=$5 → später A=$100/B=$50; der Spread wandert von $5 auf $50 (nicht stationär), das Verhältnis bleibt 2. Auch für Devisenpaare der natürliche Weg (EUR.GBP **ist** EUR.USD/GBP.USD). |

Gegenprobe an GLD/USO (nicht kointegriert), lineare Strategie, Lookback 20:

| Signal | APR | Sharpe |
|---|---|---|
| Preis-Spread mit **dynamischer** Hedge Ratio | **10,9 %** | **0,59** |
| Log-Preis-Spread | 9,0 % | 0,50 (plus Rebalancing-Kosten) |
| Verhältnis | **negativ** | — |

Hier gewinnt also der Preis-Spread mit adaptiver Hedge Ratio deutlich — trotz der theoretischen
Attraktivität des Verhältnisses.

## Bezug zu diesem Projekt

`algo/` handelt MNQ als **Einzelinstrument**; Kointegration und Hedge Ratios sind damit vorerst
nicht anwendbar. **Die Halbwertszeit dagegen sofort.**

Konkret: Die Halbwertszeit ist ein **parameterfreier Weg, Lookbacks zu bestimmen**, statt sie zu
optimieren. Im Projekt gibt es mehrere frei gewählte Lookbacks — die `min_age`/`confirm`-Fenster
in `tools/analyze_ohlc.py`, die Fensterlängen in `signals.py`. Jeder davon ist derzeit gesetzt
oder per Grid optimiert; die Halbwertszeit der jeweiligen Reihe wäre die datengetriebene
Alternative und würde eine Data-Snooping-Quelle beseitigen.

Zweitens ist sie ein **Vorfilter**: Bevor man eine ICT-These als Mean-Reversion-Regel kodiert
(Rückkehr in ein FVG, Rückkehr zur Midnight-Range-Mitte), sagt `λ > 0` oder eine sehr lange
Halbwertszeit direkt, dass es sich nicht lohnt.

Der Johansen-Test wird relevant, sobald ein **zweites Symbol** dazukommt — was bereits Thema ist:
[[SMT (Smart Money Divergence)]] verlangt einen Cross-Asset-Vergleich, und `pnl.py` führt bereits
Punktwerte für NQ und ES.

Ergänzt: [[Mean-Reversion-Tests (ADF, Hurst-Exponent, Kointegration)]] (Halls-Moore, knapper,
ohne Halbwertszeit und Johansen).
Weiterführend: [[Bollinger-Bänder, Scaling-in & Kalman-Filter]] für die praktisch handelbaren
Varianten.
