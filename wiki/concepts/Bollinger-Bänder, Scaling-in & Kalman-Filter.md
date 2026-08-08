---
tags: [concept, algo-methodology, mean-reversion, referenz]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[Algorithmic Trading - Winning Strategies and Their Rationale (Source)]]"]
---

# Bollinger-Bänder, Scaling-in & Kalman-Filter

Die praktisch handelbaren Mean-Reversion-Techniken aus
[[Algorithmic Trading - Winning Strategies and Their Rationale (Source)]] (Chan, Kap. 3) — und
der überraschende Beweis, dass **Scaling-in im Backtest nie optimal ist**.

## Bollinger-Bänder als handelbare Version der linearen Strategie

Die parameterlose lineare Strategie aus
[[Halbwertszeit der Mean Reversion & Kointegration (Chan)]] ist nicht handelbar, weil der
Kapitalbedarf unbegrenzt ist. Die praktische Fassung:

```
Einstieg:  |Z-Score| > entryZscore
Ausstieg:  |Z-Score| < exitZscore                 mit exitZscore < entryZscore

exitZscore =  0            → Ausstieg bei Rueckkehr zum Mittelwert
exitZscore = −entryZscore  → Ausstieg erst am GEGENUEBERLIEGENDEN Band
                             (dort feuert bereits das Signal der Gegenrichtung)

Lookback fuer Mittelwert/Std: freier Parameter ODER = Halbwertszeit
```

Zu jedem Zeitpunkt hält man **null oder eine** Einheit (long oder short) — dadurch sind
Kapitalallokation und Risikosteuerung trivial.

**Faustregel:** kurzer Lookback und kleine `entryZscore`/`exitZscore` → kürzere Haltedauer, mehr
Round-Trips, allgemein höhere Gewinne.

Wirkung am Beispiel GLD-USO (identische Datenbasis, nur andere Entry-Logik):

| Strategie | APR | Sharpe |
|---|---|---|
| lineare Strategie (Z-Score-proportional) | 10,9 % | 0,59 |
| **Bollinger-Band** (`entryZscore = 1`, `exitZscore = 0`) | **17,8 %** | **0,96** |

```python
z = (yport - yport.rolling(lookback).mean()) / yport.rolling(lookback).std()
long_entry,  long_exit  = z < -entry_z, z >= -exit_z
short_entry, short_exit = z >  entry_z, z <=  exit_z

units_long  = pd.Series(np.nan, index=z.index); units_long.iloc[0] = 0
units_long[long_entry]  =  1;  units_long[long_exit]  = 0
units_short = pd.Series(np.nan, index=z.index); units_short.iloc[0] = 0
units_short[short_entry] = -1; units_short[short_exit] = 0
num_units = units_long.ffill() + units_short.ffill()      # Tage ohne Signal: Position halten
```

Das `ffill()` ist der Kern: An Tagen ohne Ein- oder Ausstiegssignal wird die Position des Vortags
fortgeschrieben.

## Scaling-in: der Beweis, dass es im Backtest nie optimal ist

Scaling-in (auch Averaging-in) heißt: je weiter der Preis vom Mittelwert abweicht, desto mehr
Kapital investieren. In Bollinger-Form: `entryZscore = 1, 2, 3, …, N` und
`exitZscore = 0, 1, 2, …, N−1`.

Die intuitiven Argumente dafür sind gut: Der potenzielle Gewinn steigt mit der Abweichung;
man **skaliert auch schrittweise hinaus** und realisiert dadurch schon kleine Rückläufe (wichtig,
wenn die Reihe nie ganz zum Mittelwert zurückkehrt); und bei großen Ordergrößen sinkt der
Market Impact.

**Schoenberg & Corwin (2010) haben trotzdem bewiesen, dass es nie optimal ist.** Chans
Rekonstruktion:

```
Preis faellt auf L1. Erwartete Rueckkehr zu F > L1.
Mit Wahrscheinlichkeit p faellt er vorher weiter auf L2 < L1.
Kaufkraft: genau 2 Kontrakte. Ausstieg immer erst bei F.

I.   All-in bei L1:    2(F − L1)
II.  All-in bei L2:    2p(F − L2)
III. Average-in:       p[(F − L1) + (F − L2)] + (1 − p)(F − L1)
                     = (F − L1) + p(F − L2)

Uebergangswahrscheinlichkeit:   p̂ = (F − L1) / (F − L2)

p < p̂  →  I ist besser als II  UND besser als III
p > p̂  →  II ist besser als I  UND besser als III
```

> **Es gibt keine Situation, in der Average-in die profitabelste Methode ist.** Man kann immer ein
> einzelnes Ein-/Ausstiegsniveau finden, das im Backtest eine höhere Durchschnittsrendite liefert
> („all-in").

**Warum man es trotzdem tut** — Chans Auflösung: Der Beweis setzt voraus, dass `p` über die Zeit
**konstant** ist. Real ist die Volatilität nicht konstant, also `p` auch nicht. Unter dieser
Bedingung liefert Scaling-in wahrscheinlich eine bessere realisierte Sharpe Ratio, wenn nicht
sogar mehr Gewinn.

> **Die brauchbare Formulierung:** Scaling-in ist **in-sample nie optimal** — kann aber
> **out-of-sample** die All-in-Methode schlagen.

## Kalman-Filter als dynamische Regression

Das Problem: Hedge Ratio, Mittelwert und Standardabweichung ändern sich über die Zeit. Ein
gleitendes Fenster hat einen unschönen Nebeneffekt — das Wegfallen der ältesten und das Hinzukommen
der neuesten Bar erzeugt **abrupte, künstliche Sprünge**. Eine exponentielle Gewichtung (EMA)
mildert das, aber es ist unklar, warum ausgerechnet ein exponentieller Abfall optimal sein sollte.

Der Kalman-Filter umgeht die willkürliche Gewichtswahl. Vier Größen sind zu definieren — *„this is
actually the only creative part of the application"*, der Rest ist mechanisch:

| Größe | Bei der dynamischen Hedge Ratio |
|---|---|
| beobachtbare Variable | Preisreihe `y` |
| verborgene Variable | `β` = **2×1**-Vektor aus Achsenabschnitt (Mittelwert) **und** Steigung (Hedge Ratio) |
| Zustandsübergangsmodell | Identitätsmatrix |
| Beobachtungsmodell | Preisreihe `x`, mit einer Spalte Einsen erweitert |

```
(3.5)  y(t) = x(t)·β(t) + ε(t)                Messgleichung,   Var(ε) = Ve
(3.6)  β(t) = β(t−1) + ω(t−1)                 Zustandsuebergang, Cov(ω) = Vω

(3.7)  β̂(t|t−1) = β̂(t−1|t−1)                  Zustandsprognose
(3.8)  R(t|t−1)  = R(t−1|t−1) + Vω             Kovarianzprognose
(3.9)  ŷ(t)      = x(t)·β̂(t|t−1)               Messprognose
(3.10) Q(t)      = x(t)'·R(t|t−1)·x(t) + Ve    Varianz der Messprognose

       e(t) = y(t) − x(t)·β̂(t|t−1)             Prognosefehler,  Q(t) = Var(e(t))

(3.11) β̂(t|t)  = β̂(t|t−1) + K(t)·e(t)          Zustands-Update
(3.12) R(t|t)   = R(t|t−1) − K(t)·x(t)·R(t|t−1) Kovarianz-Update
(3.13) K(t)     = R(t|t−1)·x(t) / Q(t)          Kalman-Gain

Start:  β̂(1|0) = 0,  R(0|0) = 0
```

**Parametrisierung** (nach Montana et al., statt der aufwendigen Autocovariance-Least-Squares-
Schätzung):

```
Vω = δ/(1−δ) · I           δ ∈ (0, 1)

δ → 0 :  β(t) = β(t−1)  ⟹  entspricht gewoehnlicher OLS mit festem Offset und Steigung
δ → 1 :  β schwankt wild mit jeder neuen Beobachtung

Chans Werte (mit Hindsight gewaehlt):  δ = 0,0001 ,  Ve = 0,001
```

**Der Mehrfachnutzen — drei Größen aus einem Verfahren:**

1. eine **dynamische Hedge Ratio** (Steigungskomponente von β),
2. der **Mittelwert des Spreads** (Achsenabschnittskomponente) — ersetzt den gleitenden Durchschnitt,
3. die **Standardabweichung des Prognosefehlers** `√Q(t)` — ersetzt die gleitende
   Standardabweichung im Bollinger-Band.

Handelsregeln werden damit besonders schlank, weil `e(t)` bereits die Abweichung vom prognostizierten
Mittelwert **ist**:

```
long_entry  = e < −√Q      long_exit  = e > −√Q
short_entry = e >  √Q      short_exit = e <  √Q
```

Ergebnis auf EWA-EWC: **APR 26,2 %, Sharpe 2,4** — mit Abstand das beste
Mean-Reversion-Ergebnis des Buches.

```python
def kalman_hedge(x, y, delta=1e-4, Ve=1e-3):
    """x, y = Preisreihen. Liefert beta (2×T), e (Prognosefehler), Q (dessen Varianz)."""
    X = np.column_stack([x, np.ones_like(x)])
    Vw = delta / (1 - delta) * np.eye(2)
    P  = np.zeros((2, 2)); beta = np.zeros((2, len(y)))
    e  = np.full(len(y), np.nan); Q = np.full(len(y), np.nan)
    R  = np.zeros((2, 2))
    for t in range(len(y)):
        if t > 0:
            beta[:, t] = beta[:, t-1]        # (3.7)
            R = P + Vw                       # (3.8)
        yhat = X[t] @ beta[:, t]             # (3.9)
        Q[t] = X[t] @ R @ X[t] + Ve          # (3.10)
        e[t] = y[t] - yhat
        K = R @ X[t] / Q[t]                  # (3.13)
        beta[:, t] = beta[:, t] + K * e[t]   # (3.11)
        P = R - np.outer(K, X[t] @ R)        # (3.12)
    return beta, e, Q
```

## Kalman-Filter als Market-Making-Modell

Zweite Anwendung — hier interessiert **nur eine** Reihe, keine Hedge Ratio. Verborgene Variable
ist der **faire Mittelpreis** `m(t)`:

```
(3.14) y(t) = m(t) + ε(t)
(3.15) m(t) = m(t−1) + ω(t−1)
(3.16) m(t|t) = m(t|t−1) + K(t)·( y(t) − m(t|t−1) )
(3.17) Q(t)   = Var(m(t)) + Ve
(3.18) K(t)   = R(t|t−1) / ( R(t|t−1) + Ve )
(3.19) R(t|t) = (1 − K(t))·R(t|t−1)
```

Der Kniff, mit dem Market Maker daraus etwas Praktisches machen (nach Sinclair, 2010): Die
Messunsicherheit `Ve` wird von der **Ordergröße** abhängig gemacht — eine große Transaktion trägt
mehr Information über den fairen Preis als eine kleine.

```
(3.20)  Ve = R(t|t−1) · ( T/Tmax − 1 )

        T    = Transaktionsgroesse
        Tmax = Benchmark-Groesse (z.B. ein Bruchteil des Vortagesvolumens)

        T = Tmax  ⟹  Ve = 0  ⟹  Kalman-Gain = 1
                  ⟹  der neue Mittelpreis IST exakt der beobachtete Preis
```

Chans Einordnung: Das ist eine Verallgemeinerung des **VWAP**. Beim VWAP gewichtet man nur nach
Volumen; hier zusätzlich nach **Aktualität**. Also gewissermaßen ein volumen- **und**
zeitgewichteter Durchschnittspreis.

## Bezug zu diesem Projekt

**Bollinger-Bänder** sind im Vault bereits präsent — als ICT-Werkzeug in
[[Midnight Opening Range]] (STD-Projektionen) und in
[[Central Bank Dealers Range (CBDR)]]. Chans Fassung liefert die generische Entry/Exit-Mechanik
samt der Regel, `exitZscore < entryZscore` zu wählen, und die Begründung, den Lookback aus der
Halbwertszeit statt aus einer Optimierung zu ziehen.

**Der Scaling-in-Befund betrifft eine bestehende Projektregel unmittelbar.**
[[Verlust-Mitigation durch reduzierte Re-Entry-Size]] und die Pyramiding-Beobachtung in
[[2026-08-01 - Part 2 High Precision Secrets To Intraday Price Action (Source)|Part 2 High Precision Secrets]]
(Single-Contract-Probe plus Nachlegen im Drawdown) sind Scaling-in-Verfahren. Chans Beweis sagt:
Im Backtest wird sich **immer** ein einzelnes Einstiegsniveau finden lassen, das besser abschneidet —
das ist **kein** Argument gegen die Praxis, aber es heißt, dass ein Backtest diese Technik
systematisch schlechtreden wird. Wer sie testet, muss das wissen, sonst verwirft er sie aus dem
falschen Grund.

**Der Kalman-Filter** ist der interessanteste offene Faden: Er liefert gleitenden Mittelwert und
gleitende Standardabweichung **ohne** willkürlichen Lookback. Damit wäre er ein direkter Ersatz
für mehrere fest gewählte Fensterlängen in `tools/analyze_ohlc.py` und `algo/signals.py` — und
`filterpy` bzw. `pykalman` machen eine Eigenimplementierung überflüssig. Die Market-Making-Variante
(3.14–3.20) wird erst mit Tick-und-Volumen-Daten relevant, also frühestens mit der
IBKR-Anbindung (Roadmap-Stufe 4).
