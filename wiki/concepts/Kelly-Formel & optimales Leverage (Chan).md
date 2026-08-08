---
tags: [concept, algo-methodology, risikomanagement, leverage, referenz]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[Algorithmic Trading - Winning Strategies and Their Rationale (Source)]]"]
---

# Kelly-Formel & optimales Leverage (Chan)

Wie viel Hebel ist richtig? Aus
[[Algorithmic Trading - Winning Strategies and Their Rationale (Source)]] (Ernest Chan, Kap. 8),
nach Edward Thorp (1997). Die **zentrale Risikomanagement-Seite** dieses Vaults für die Frage
der Positionsgröße.

Chans Ausgangspunkt ist eine Haltungsfrage: Anfänger betreiben Risikomanagement aus
**Verlustaversion** — Menschen brauchen im Schnitt die Aussicht auf $2 Gewinn, um $1 Risiko
auszugleichen (Kahneman), was erklärt, warum eine Sharpe Ratio von 2 emotional so attraktiv
wirkt. Diese Abneigung ist für sich genommen **nicht rational**:

> *„Our goal should be the maximization of long-term equity growth, and we avoid risk only
> insofar as it interferes with this goal."*

## Die Grundformeln

```
(8.1)  f = m / s²                      Kelly-Leverage, Einzelstrategie

       m = mittlere Überschussrendite (excess return, also abzüglich risikofreiem Zins)
       s² = Varianz der Überschussrenditen
       f  = Leverage (Marktwert des Portfolios / Eigenkapital)

(8.2)  F = C⁻¹ M                       Kelly-Allokation, mehrere Strategien

       F = Spaltenvektor der optimalen Leverages je Strategie
       C = Kovarianzmatrix der Strategie-Renditen
       M = Vektor der mittleren Überschussrenditen

(8.3)  g = Fᵀ C F / 2                  maximale Wachstumsrate — gilt NUR bei optimalem F

(8.5)  g(f) = ⟨ log(1 + f·R) ⟩         allgemeine Wachstumsrate, R = ungehebelte Rendite pro Bar
              └ Mittel über eine Zufallsstichprobe von R

       Gauss-Spezialfall:  g(f) = f·m − f²·s²/2
```

> **OCR-Hinweis zur Rohquelle:** Im konvertierten Text steht an dieser Stelle
> `g(f) = fm − f 2m2/2`. Das ist ein Erkennungsfehler — korrekt ist `f·m − f²·s²/2`.
> **Nachprüfbar:** `dg/df = m − f·s² = 0  ⟹  f = m/s²`, also exakt Gleichung 8.1. Mit `m²` im
> zweiten Term käme `f = 1/m` heraus, was der Kelly-Formel widerspräche.

Interpretation von `f`: bei $100.000 Eigenkapital und `f = 5` hält man ein Portfolio mit
**Marktwert $500.000**. `f` bezieht sich auf das **Brutto**-Leverage (Summe der Absolutbeträge
aller Long- und Short-Marktwerte / Eigenkapital), nicht auf das Netto-Leverage.

## Die unbequeme Konsequenz: konstantes Leverage

Egal welches Verfahren das optimale `f` bestimmt — **es muss konstant gehalten werden**. Das ist
Voraussetzung für die Maximierung der Wachstumsrate, mit oder ohne Drawdown-Nebenbedingung. Und
es fühlt sich falsch an:

**Rechenbeispiel 8.1 (wörtlich aus dem Buch):**

```
Start:      Equity $100K, f = 5   →  Portfolio-Marktwert $500K

Tag 1:      Verlust $10K
            Equity          $90K
            Portfolio jetzt $490K
            Soll:  5 × $90K = $450K
            ⟹  weitere $40K LIQUIDIEREN — in den Verlust hinein verkaufen

Tag 2:      Gewinn $20K
            Equity          $110K
            Portfolio jetzt $470K
            Soll:  5 × $110K = $550K
            ⟹  $80K NACHKAUFEN
```

„This selling into the loss may make some people uncomfortable, but it is a necessary part of
many risk management schemes."

**Systemisches Nebenprodukt:** Genau dieses Verkaufen-in-den-Verlust gilt als Ansteckungsmechanismus
in Finanzkrisen — als Ursache des Quant-Fonds-Einbruchs im August 2007 (Khandani & Lo). Viele
Fonds halten ähnliche Positionen; verliert einer und liquidiert, erzeugt das Verluste bei allen
anderen, die daraufhin ebenfalls liquidieren müssen. Chan nennt es eine Tragik der Allmende:
Selbstschutz des Einzelnen führt zur Katastrophe für alle.

## Warum Kelly eine Obergrenze ist, kein Sollwert

Chans Praxiserfahrung, dreifach begründet:

1. **Schätzfehler sind asymmetrisch tödlich.** Überschätzt man `m` oder unterschätzt man `s²`,
   ergibt sich ein **zu hohes** `f` — und bei genug Überhöhung endet das im Ruin (Equity → 0).
   Unterschätzt man `f`, verliert man nur Wachstumsrate. Deshalb die verbreitete Praxis:
   **Half-Kelly**, also `f/2`.
2. **Der Wert ist oft praktisch unerreichbar.** Das aus einem Backtest ermittelte Kelly-Leverage
   übersteigt regelmäßig das, was der Broker überhaupt zulässt.
3. **Die Gauss-Annahme trägt nicht.** Bei fetten Verteilungsenden hätte Kelly-Leverage im
   Backtest zum Ruin geführt — maximaler Drawdown von −1.

Zwei aufschlussreiche Anwendungen als **Obergrenze**:

- Russell 1000 und 2000 haben ein Kelly-Leverage von etwa **1,8**. Die dreifach gehebelten ETFs
  BGU und TNA auf genau diese Indizes haben per Konstruktion Leverage 3 — der Nettoinventarwert
  kann also gegen null gehen. Buy-and-Hold ist bei ihnen mathematisch unvernünftig, was der
  Emittent selbst einräumt.
- Bei einem Broker-Maximum `Fmax`, das deutlich unter `Σ|Fᵢ|` liegt, ist die übliche
  Empfehlung — alle `Fᵢ` mit `Fmax / Σ|Fᵢ|` skalieren — **nicht optimal**.

### Rechenbeispiel 8.2: Wenn das Broker-Limit bindet

```
Strategie 1:  m = 30 %,  s = 26 %   →  Kelly f₁ = 4,4
Strategie 2:  m = 60 %,  s = 35 %   →  Kelly f₂ = 4,9
Korrelation 0, Gauss, risikofreier Zins 0
Gesamt-Brutto-Leverage 9,3   →   g = FᵀCF/2 = 2,1

Broker erlaubt aber nur  Fmax = 2.

Naive Skalierung:   F1 = 0,95 ; F2 = 1,05   →   g = 0,82
Optimal:            F1 = 0,00 ; F2 = 2,00   →   g = 0,96      ← +17 %
```

**Regel:** Liegt `Fmax` weit unter dem Kelly-Gesamtleverage und unterscheiden sich die
Wachstumsraten der Strategien deutlich, ist es oft optimal, **die gesamte Kaufkraft auf die
Strategie mit der höchsten mittleren Überschussrendite zu legen** — statt zu diversifizieren.

## Drei Wege zum optimalen Leverage

### Weg 1 — Kelly analytisch (Gauss)

`f = m/s²`. Einfachste und eleganteste Lösung, aber die restriktivste Annahme.

### Weg 2 — Monte-Carlo auf simulierten Renditen

Wenn die Renditen fette Enden haben, wird `g(f)` numerisch maximiert. Chan nutzt das
**Pearson-System**: es nimmt Mittelwert, Standardabweichung, **Schiefe und Kurtosis** der
empirischen Renditen und modelliert daraus eine von sieben analytischen Verteilungen (umfasst
Gauss, Beta, Gamma, Student-t …).

```matlab
moments = {mean(ret), std(ret), skewness(ret), kurtosis(ret)};
[ret_sim, type] = pearsrnd(moments{:}, 100000, 1);
g = inline('sum(log(1+f*R))/length(R)', 'f', 'R');
optimalF = fminbnd(@(f) -g(f, ret_sim), 0, 24);
```

Python-Äquivalent (das Pearson-System steckt in `scipy.stats.pearson3` bzw. lässt sich über
`scipy.stats.johnsonsu`/Momentenanpassung nachbilden; einfacher ist Bootstrap-Resampling der
echten Renditen):

```python
def growth_rate(f, R):
    """g(f) = <log(1 + f·R)>  — Gleichung 8.5"""
    return np.mean(np.log1p(f * R))

from scipy.optimize import minimize_scalar
res = minimize_scalar(lambda f: -growth_rate(f, ret_sim), bounds=(0, 24), method="bounded")
optimal_f = res.x
```

**Ergebnis im Buchbeispiel:** Kelly analytisch 18,4 — Monte-Carlo 19. Verblüffend nah beieinander.

**Der Ruin-Punkt ist exakt berechenbar:**

```
f_ruin = 1 / |schlechteste Einzelrendite|

Buchbeispiel: schlechteste Bar-Rendite −0,0331  ⟹  f_ruin = 1/0,0331 = 30,2
              bei f = 31 ist die Wachstumsrate −1, also Totalverlust.
```

Das ist eine **harte, modellfreie Obergrenze**, die man immer kennen sollte.

### Weg 3 — Optimierung auf den historischen Renditen

Dieselbe Optimierung, aber auf `ret` statt `ret_sim`. Ergebnis im Buch: **18,4** — identisch mit
Kelly. Nachteil: klassischer Data-Snooping-Bias, weil es nur *eine* Realisierung gibt. Monte
Carlo liefert dagegen viele.

## Die Drawdown-Nebenbedingung

Wenn nicht nur Wachstum zählt, sondern ein maximaler Drawdown `−D` einzuhalten ist, gilt eine
Warnung:

> **Die Umrechnung ist NICHT linear.** Man kann nicht einfach das unbeschränkte optimale `f` mit
> dem Verhältnis der Drawdowns skalieren.

Zahlen aus dem Buch (simulierte Renditen `ret_sim`):

| Leverage | max. Drawdown |
|---|---|
| `f = 19,2` (unbeschränkt optimal) | **−0,999** |
| `f = 9,6` (halbiert) | **−0,963** |
| `f ≈ 2,7` (durch 7 geteilt) | ≈ **−0,5** |

Um den Drawdown zu **halbieren**, musste das Leverage durch **7** geteilt werden. Auf den
*historischen* Renditen genügte dagegen ein Faktor 1,5 (auf `f = 13`) für einen Drawdown unter
−0,49.

**Welche Datenbasis?**

| | Vorteil | Nachteil |
|---|---|---|
| **Simulierte** Renditen | viel höhere statistische Signifikanz; entspricht der VaR-Methodik großer Banken | der simulierte Extrem-Drawdown kann so selten sein, dass er „einmal in einer Million Jahre" auftritt — der Lieblingsausrede gescheiterter Fondsmanager |
| **Historische** Renditen | erfassen die **seriellen Korrelationen**, die in der Simulation zwangsläufig verloren gehen und die den realen Drawdown oft dämpfen; decken eine realistische Strategie-Lebensdauer ab | viel zu wenig Daten für einen Worst Case |

Chans Kompromiss: **ein Leverage zwischen den beiden Ergebnissen wählen.**

Und die entscheidende Einschränkung: Ein so bestimmtes Leverage verhindert nur, dass der
*simulierte* Drawdown die Grenze überschreitet — **nicht der zukünftige**. Dafür braucht es
[[CPPI (Constant Proportion Portfolio Insurance)]] oder einen Stop Loss.

## Bezug zu diesem Projekt

Der Vault arbeitet mit einer **festen 1-%-Regel** ([[Risikomanagement (1% pro Trade)]]) — das ist
eine Risiko-pro-Trade-Regel, während Kelly eine Aussage über das **Gesamt-Leverage des Kontos**
macht. Beide schließen sich nicht aus, adressieren aber verschiedene Fragen.

Konkret anwendbar auf `algo/`:

- `algo/pnl.py::risk_size()` bestimmt die Kontraktzahl aus dem 1-%-Risiko und einem
  `max_notional`-Margin-Deckel. **Der Kelly-Wert wäre die zweite, unabhängige Obergrenze** — und
  laut dem Log vom 2026-08-07 handelt die Silver-Bullet-Strategie „praktisch durchgehend am
  Margin-Limit" bei 20× Hebel. Ein Kelly-Check würde zeigen, ob dieses Leverage überhaupt
  vertretbar ist.
- `f_ruin = 1/|schlechteste Bar-Rendite|` ist mit den vorhandenen Daten in einer Zeile
  auszurechnen und liefert eine harte Obergrenze, die bisher nirgends im Projekt existiert.
- Die Drawdown-Nebenbedingung ist die Brücke zu
  [[Grenzen für Einzelrenditen & Drawdown]] (Masters) — dort steht, wie man den erwarteten
  Drawdown ehrlich schätzt, hier, wie man das Leverage daran anpasst.

Ergänzend: [[Kelly-Criterion & Value-at-Risk (Money Management)]] (Halls-Moore) behandelt
dieselbe Formel knapper und ergänzt VaR; diese Seite ist die ausführliche Fassung mit den
Praxiseinschränkungen.

Weiterführend: [[CPPI (Constant Proportion Portfolio Insurance)]],
[[Stop Loss bei Mean Reversion vs. Momentum]], [[Leading Risk Indicators]].
