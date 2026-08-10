---
tags: [concept, algo-methodology, validation, statistik, referenz]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[Testing and Tuning Market Trading Systems (Source)]]"]
---

# Konfidenzgrenzen für Renditen (t-Test, Bootstrap, BCa)

Untergrenze für die **wahre mittlere Rendite** — die Zahl, um die künftige Renditen streuen
werden. Aus [[Testing and Tuning Market Trading Systems (Source)]] (Kap. 6, Programme
`BOUND_MEAN.CPP`, `BOOT_CONF.CPP`, `BOOT_RATIO.CPP`).

Kernargument: ein guter Backtest-Mittelwert reicht nicht. Bei genug Bars findet jeder
Hypothesentest auch den winzigsten echten Edge — eine statistisch gesicherte Rendite von 0,5 %
p.a. will trotzdem niemand handeln. Die relevante Frage ist nicht „ist der Edge echt?", sondern
**„wie klein könnte er sein?"**.

## Formeln (Kapitel 6)

```
(6-1)  Mean     = (1/n) · Σᵢ xᵢ

(6-2)  StdDev   = sqrt( (1/(n−1)) · Σᵢ (xᵢ − Mean)² )

(6-3)  t        = √n · Mean / StdDev                     ← unter H₀: wahrer Mittelwert = 0

(6-4)  p-value  = 1 − CDF_t(n−1, t)

(6-5)  t        = √n · (ObsMean − TrueMean) / StdDev     ← allgemeine Form

(6-6)  P{ t ≤ t_p } = p          mit  t_p = InvCDF_t(n−1, p)

(6-7)  P{ √n·(ObsMean − TrueMean)/StdDev ≤ t_p } = p

(6-8)  P{ ObsMean − StdDev·t_p/√n ≤ TrueMean } = p

(6-9)  LowerBound = ObsMean − StdDev · t_p / √n
       UpperBound = ObsMean + StdDev · t_p / √n
```

## Weg 1: parametrisch (Student-t)

```python
import numpy as np
from scipy import stats

def t_bounds(returns, p=0.95):
    n      = len(returns)
    mean   = np.mean(returns)
    stddev = np.std(returns, ddof=1)                 # Gleichung 6-2
    t      = np.sqrt(n) * mean / stddev              # Gleichung 6-3
    pval   = 1.0 - stats.t.cdf(t, df=n - 1)          # Gleichung 6-4
    t_p    = stats.t.ppf(p, df=n - 1)                # Gleichung 6-6
    lower  = mean - stddev * t_p / np.sqrt(n)        # Gleichung 6-9
    return mean, t, pval, lower
```

**Praktische Abkürzung, die Masters betont:** algebraisch folgt aus (6-3) und (6-9), dass die
Nullhypothese *genau dann* auf dem Niveau `1−p` verworfen wird, wenn `LowerBound > 0`. Man braucht
also gar keinen getrennten Hypothesentest — es genügt, die Untergrenze zu berechnen und ihr
Vorzeichen anzusehen. (Bei stetiger Verteilung ist `LowerBound == 0` ein Nullereignis;
konservativ verlangt man echt positiv.)

**Zahlenbeispiel:** n = 100, Mean = 8, StdDev = 5, p = 0,95 → t_p ≈ 1,66 →
`8 − 5·1,66/√100 = 7,17`.

**Zwei Lesarten von 7,17:**

- *Gebräuchlich, etwas unsauber:* „mit 95 % Wahrscheinlichkeit liegt der wahre Mittelwert bei
  mindestens 7,17."
- *Streng korrekt:* 7,17 ist der kleinste Wert, den der wahre Mittelwert haben könnte, damit
  eine Stichprobe von mindestens der beobachteten Güte noch mit ≥ 95 % Wahrscheinlichkeit
  auftritt. (Der wahre Mittelwert ist eine feste Zahl, die Stichprobe ist die Zufallsgröße.)
  Masters: „Please don't stress over this concept too much."

**Warum H₀ „Mittelwert = 0" genügt**, obwohl die Nullhypothese formal „≤ 0" lauten muss: Bei
negativem wahrem Mittelwert wäre der t-Score nach (6-5) noch *größer* und der P-Wert noch
kleiner. Null ist also der konservativste Fall der Nullhypothese.

**Beidseitiges Intervall:** Fehlerwahrscheinlichkeit splitten. 90 %-Intervall = je 5 % oben und
unten, also `p = 0,95` für **beide** Grenzen.

> **Die eine harte Bedingung.** Der t-Test ist erstaunlich robust gegen moderate Schiefe und
> mäßig schwere Verteilungsenden und sehr robust gegen *leichte* Enden. Aber **ein einziger
> wilder Ausreißer macht ihn wertlos**: liegen die Renditen zwischen −5 und +5 und eine bei 50,
> ist die Zahl Müll. Deshalb gilt ausnahmslos: **vor jedem t-Test ein Histogramm der Renditen
> ansehen.** Ausreißer im Rahmen einer Glockenkurve sind unbedenklich, man muss nicht pingelig
> sein — aber echte Ausreißer disqualifizieren das Verfahren.

## Zwischenspiel: was ein P-Wert nicht sagt

Drei Umgangsweisen mit dem Ergebnis — eine korrekt, eine grau, eine falsch:

1. **Korrekt:** Fehlerniveau **vorab** festlegen (0,01 / 0,05 / 0,1) und danach entscheiden.
   Bei einem wertlosen System wird man dann mit genau dieser Wahrscheinlichkeit fälschlich
   „Können" attestieren. Äquivalent: vorab den Schwellenwert der Teststatistik berechnen.
2. **Grau, aber verbreitet (auch bei Masters):** P-Wert einfach berichten. Mehr Information, aber
   Missbrauchsgefahr — **P-Werte sind keine Vergleichsmaße**. p = 0,001 fühlt sich besser an als
   p = 0,049, doch das 0,049-System könnte auf längerer Historie ebenfalls 0,001 erreichen.
   P-Werte hängen an der Datenmenge.
3. **Falsch:** „p = 0,01, also ist die Wahrscheinlichkeit, dass ich mich irre, 1 %" bzw. „also ist
   das System zu 99 % gut."

Masters' Hunde-Analogie zu (3): 99 % aller Hunde haben vier Beine. Jemand meldet ein zweibeiniges
Tier → wahrscheinlich kein Hund. Unter allen Anrufen, bei denen es *wirklich* ein Hund ist, irrt
man sich nur in 1 % der Fälle — **das ist die korrekte Aussage.** Ruft aber ausschließlich ein
Tierheim an, das nur Hunde hält, liegt man **jedes Mal** falsch, obwohl der P-Wert stimmt. Der
P-Wert ist bedingt („falls H₀ gilt") und sagt nichts über die Grundgesamtheit der geprüften
Systeme.

Und in der Gegenrichtung: ein *nicht* kleiner P-Wert erlaubt **nie** den Schluss, das System sei
wertlos. Vielleicht wurde nur zu wenig getestet, oder das Testverfahren war unpassend. *„We must
never assert the truth of the null hypothesis."*

## Weg 2: Bootstrap

Grundidee (Efron): die eigene OOS-Stichprobe so behandeln, als wäre sie die Grundgesamtheit, und
daraus mit Zurücklegen `B` Stichproben **gleicher Größe** ziehen (gleiche Größe ist wichtig — viele
Kennzahlen hängen an `n`). Die Streuung der so berechneten Kennzahlen schätzt die Streuung, der
die Originalstichprobe selbst unterlag.

### Pivot-Methode

Annahme: die Verzerrung Stichprobe→Bootstrap-Stichprobe entspricht der Verzerrung
Grundgesamtheit→Stichprobe. Grenzen ergeben sich aus den Perzentilgrenzen:

```
PivotLower = 2·Param − PctileUpper
PivotUpper = 2·Param − PctileLower
```

In Masters' Tests durchweg **die schlechteste** der drei Methoden.

### Perzentil-Methode

```python
def boot_conf_pctile(x, stat, nboot=10000, alpha=0.025, rng=None):
    rng   = rng or np.random.default_rng()
    n     = len(x)
    vals  = np.empty(nboot)
    for b in range(nboot):
        vals[b] = stat(rng.choice(x, size=n, replace=True))
    vals.sort()
    k = int(alpha * (nboot + 1)) - 1                 # unverzerrter Quantilschaetzer
    k = max(k, 0)
    return vals[k], vals[nboot - 1 - k]              # (lower, upper)
```

Kurios und von Masters als Übung empfohlen: Pivot- und Perzentil-Intervalle sind **spiegelbildlich**
zueinander — liegt bei der einen Methode die Untergrenze weiter vom Stichprobenwert entfernt,
ist es bei der anderen die Obergrenze. Dass beide trotzdem meist gut funktionieren, nennt er
„a miracle".

### BCa („bias corrected and accelerated") — Masters' Empfehlung

Vier Schritte:

```
Schritt 1 — Bias-Korrektur (6-10)
  ẑ₀ = Φ⁻¹( #[ θ̂*ᵇ < θ̂ ] / B )
       θ̂     = Kennzahl der Originalstichprobe
       θ̂*ᵇ   = Kennzahl der b-ten Bootstrap-Stichprobe
       #[·]  = Anzahl der Bootstrap-Werte unter dem Originalwert

Schritt 2 — Acceleration per Jackknife (6-11, 6-12)
  θ̂₍ᵢ₎  = Kennzahl mit weggelassenem Fall i   (n Durchlaeufe ueber n−1 Faelle)
  θ̄₍·₎  = (1/n) · Σᵢ θ̂₍ᵢ₎
  â     =        Σᵢ (θ̄₍·₎ − θ̂₍ᵢ₎)³
          ─────────────────────────────────
          6 · [ Σᵢ (θ̄₍·₎ − θ̂₍ᵢ₎)² ]^(3/2)

Schritt 3 — Fraktilpunkte verschieben (6-13)
  α' = Φ( ẑ₀ +      ẑ₀ + Φ⁻¹(α)          )
              ──────────────────────────
              1 − â · ( ẑ₀ + Φ⁻¹(α) )
  getrennt fuer die untere und die obere Grenze anwenden

Schritt 4 — Perzentile an den verschobenen Punkten ziehen
  untere Grenze (α' < 0.5):  k = trunc( α'   · (B+1) )        → Element k      (1-basiert)
  obere  Grenze (α' > 0.5):  k = trunc( (1−α') · (B+1) )      → Element B+1−k
```

Sind `ẑ₀` und `â` beide null, ist `α' = α` und BCa fällt auf die Perzentil-Methode zurück.

```python
def boot_conf_bca(x, stat, nboot=10000, alpha=0.025, rng=None):
    rng   = rng or np.random.default_rng()
    n     = len(x)
    theta = stat(x)

    vals = np.empty(nboot)
    for b in range(nboot):
        vals[b] = stat(rng.choice(x, size=n, replace=True))

    z0 = stats.norm.ppf(np.mean(vals < theta))                  # (6-10)

    jack = np.array([stat(np.delete(x, i)) for i in range(n)])  # (6-11)
    d    = jack.mean() - jack
    a    = (d ** 3).sum() / (6.0 * ((d ** 2).sum() ** 1.5) + 1e-60)   # (6-12)

    vals.sort()
    def shifted(al):                                            # (6-13)
        z = stats.norm.ppf(al)
        return stats.norm.cdf(z0 + (z0 + z) / (1.0 - a * (z0 + z)))

    alo, ahi = shifted(alpha), shifted(1.0 - alpha)
    klo = max(int(alo         * (nboot + 1)) - 1, 0)
    khi = max(int((1.0 - ahi) * (nboot + 1)) - 1, 0)
    return vals[klo], vals[nboot - 1 - khi]
```

In der Praxis: `scipy.stats.bootstrap(..., method="BCa")` implementiert genau das — Eigenbau
unnötig. `nboot = 10.000` nennt Masters als vernünftiges Minimum für ernsthafte Tests.

Eine Obergrenze für die mittlere Rendite interessiert selten, kostet aber praktisch nichts extra —
alle Routinen im Buch liefern beide.

## Warnung: Verhältniskennzahlen bootstrappen schlecht

Sharpe Ratio und Profit Factor haben einen Nenner, der klein werden kann — dann explodiert die
Kennzahl. `BOOT_RATIO` testet das mit wertlosen Systemen (Gewinnwahrscheinlichkeit 0,5, wahrer
Profit Factor also `prob/(1−prob) = 1`) und zählt, wie oft die berechneten Grenzen verletzt
werden. Ideal wäre: Verletzungsrate = Soll-Fehlerrate.

Befunde:

- Probleme konzentrieren sich auf die **strengste** Spalte (2,5 % Sollfehlerrate).
- **Pivot ist mit Abstand am schlechtesten.** Bei 50 Trades und 2,5 %: die Profit-Factor-
  Untergrenze wird **nie** verletzt (sie liegt also absurd tief und ist wertlos), während die
  Obergrenze **fast viermal so oft** verletzt wird wie erlaubt.
- **Profit Factor verhält sich schlechter als Sharpe.**
- Bei nur 50 Renditen liegt schon der *mittlere* Profit Factor über 1, weil gelegentlich winzige
  Nenner Extremwerte erzeugen, die den Mittelwert hochziehen.

**Lösung: den Logarithmus des Profit Factors bootstrappen.** Das zähmt das rechte
Verteilungsende. Ergebnis laut Buch: die Untergrenze — die einzige, die interessiert — wird
deutlich zuverlässiger; nur die BCa-**Ober**grenze bei 2,5 % verschlechtert sich leicht, was
praktisch egal ist. Bei 5 % und 10 % verbessern sich beide Grenzen deutlich.

**Verallgemeinerte Regel:** Bootstrappt man eine Verteilung mit schwerem Ende, vorher so
transformieren, dass das Ende gezähmt wird.

## Referenzlauf: BOUND_MEAN auf SPX

Aufruf: `BOUND_MEAN max_lookback n_train n_test n_boot filename`
Werte: `max_lookback = 100`, `n_train = 1000`, `n_test = 100`, 23.557 Tagespreise,
MA-Breakout-System, Bar-Renditen mit `25200` annualisiert.

Drei Renditearten parallel ausgewertet (siehe [[Profit pro Bar vs. pro Trade]]):
*open-posn* (Bars mit offener Position), *complete* (abgeschlossene Trades), *grouped* (alle Bars
in 10er-Blöcken gemittelt — deutlich kleiner, weil die Nullrenditen ohne Position mitzählen).

| Kennzahl (open-posn) | Wert |
|---|---|
| annualisierte mittlere Rendite | **9,91 %** |
| t-Test-P-Wert | **0,1000** |
| 90 %-Untergrenze (t-basiert) | **−0,0022** |
| Bootstrap-Untergrenzen (Perzentil / BCa) | ebenfalls ≈ 0 |
| Pivot-Untergrenze | Ausreißer nach unten, wie üblich |

> **Das ist die Kernbotschaft der Seite:** eine zweistellige Backtest-Rendite kann eine
> Untergrenze unter null haben. „Back to the drawing board."

Der P-Wert von exakt 0,1000 bei einer Untergrenze von ≈ 0 illustriert nebenbei die oben genannte
Äquivalenz — bei 90 % Konfidenz ist die Grenze genau dann null, wenn p = 0,1.

## Bezug zu diesem Projekt

`algo/`-Reports (`validate.py`, `backtest_bt.py`, `stress_test.py`,
[[Ensemble-Strategie — Backtest-Ergebnis & Commission-Verzerrung (laufend)]]) weisen bisher nur
**Punktschätzer** aus. Eine BCa-Untergrenze wäre eine Zeile `scipy.stats.bootstrap(...)` und würde
beantworten, ob die Zahl überhaupt von null unterscheidbar ist. Beim Profit Factor zwingend auf
dem **Logarithmus** rechnen.

Voraussetzung für alle Verfahren hier: möglichst viele, möglichst **unabhängige** Datenpunkte —
also Bar-Renditen offener Positionen ([[Profit pro Bar vs. pro Trade]]) und keine serielle
Korrelation ([[Walk-Forward Guard Buffer & Varianz-Inflation]]).

Grenzen um **einzelne** künftige Renditen statt um deren Mittelwert:
[[Grenzen für Einzelrenditen & Drawdown]].

## Implementierung

`algo/masters.py`: `lower_bound_t(returns, p)` liefert `(mean, t, p_value, lower)` — die Nullhypothese ist genau dann verworfen, wenn `lower > 0`. `lower_bound_bca(...)` delegiert an `scipy.stats.bootstrap(method="BCa")`. Bei Verhältniskennzahlen `statistic=log_profit_factor` übergeben, nie `profit_factor`.

**Seit 2026-08-11 im Report** (Backlog 9a, siehe `algo/PLAN.md`): `algo/confidence.py` weist im `backtest_bt.py`-Report die 95%-Untergrenze der mittleren Bar-Rendite (t-Test und BCa nebeneinander) sowie die Profit-Factor-Untergrenze (`exp(BCa auf log PF)`) aus. Erster realer Lauf (36 Tage, MNQ): mittlere Bar-Rendite -0,0050 %, BCa-Untergrenze **-0,0137 % ≤ 0 → nicht von null unterscheidbar**, PF-Untergrenze 0,689. Damit ist die Silver-Bullet-Basisregel ohne Confluenz statistisch nicht von „kein Edge" zu trennen — die Untergrenze macht sichtbar, was der Punktschätzer allein verschweigt.

Selbstcheck: `python algo/masters.py` und `python algo/confidence.py` (beide in `algo/selfcheck.py`).
