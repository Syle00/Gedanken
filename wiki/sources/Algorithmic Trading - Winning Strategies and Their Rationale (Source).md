---
tags: [source, algo-methodology, risikomanagement, buch, referenz]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[Winning strategies and ther rationale]]"]
---

# Algorithmic Trading - Winning Strategies and Their Rationale (Source)

**Ernest P. Chan, Wiley Trading Series 2013**, 8 Kapitel, MATLAB-Beispielcode.
Rohquelle: `raw/literatur/Winning strategies and ther rationale.md` (6.741 Zeilen, aus
`raw/literatur/Winning strategies and ther rationale.pdf` extrahiert).

Nachfolgeband zu Chans *Quantitative Trading* (2009). Während das erste Buch die Grundtechniken
behandelte, geht es hier ausschließlich um **Strategien und ihre Begründung** — plus ein
Risikomanagement-Kapitel, das der inhaltliche Schwerpunkt dieses Ingests ist.

> Chans Leitgedanke: *„Instead of recipes, what I hope to convey is the deeper reasons, the basic
> principles, why certain strategies should work and why others shouldn't."* Deshalb bevorzugt er
> durchweg **einfache, lineare** Strategien — nicht weil sie besser performen, sondern weil sie
> zeigen, dass der Gewinn aus einer **Marktineffizienz** stammt und nicht aus der Raffinesse der
> Regel.

## Kapitelübersicht mit Zielseiten

| Kap. | Inhalt | Wiki-Seite |
|---|---|---|
| 1 | Backtesting-Fallstricke, Futures-Datenaufbereitung, Hypothesentests, Plattformwahl | [[Futures-Datenaufbereitung & Backtesting-Fallstricke (Chan)]] |
| 2 | ADF, Hurst, Variance Ratio, **Halbwertszeit**, CADF, Johansen | [[Halbwertszeit der Mean Reversion & Kointegration (Chan)]] |
| 3 | Preis-/Log-/Ratio-Spreads, Bollinger, Scaling-in, **Kalman-Filter** | [[Bollinger-Bänder, Scaling-in & Kalman-Filter]] |
| 4 | Mean Reversion bei Aktien und ETFs, Buy-on-Gap, Index-Arbitrage | (in den obigen Seiten mitbehandelt) |
| 5 | Währungen und Futures, **Roll Return**, Kalenderspreads, VX/ES | [[Roll Return, Contango & Backwardation]] |
| 6 | Interday-Momentum, Zeitreihen-Tests, Roll-Return-Signal | [[Momentum-Ursachen & Opening-Gap-Strategie]] |
| 7 | Intraday-Momentum, **Opening Gap**, PEAD, gehebelte ETFs, HFT-Taktiken | dito |
| 8 | **Risikomanagement** | [[Kelly-Formel & optimales Leverage (Chan)]], [[CPPI (Constant Proportion Portfolio Insurance)]], [[Stop Loss bei Mean Reversion vs. Momentum]], [[Leading Risk Indicators]] |

## Formelverzeichnis

| Nr. | Formel | Seite |
|---|---|---|
| 1.1 | `z(i) = (f(i) − mean(f))/std(f)` — Z-Score eines Faktors | (hier) |
| 1.2 | `R = mean(R) + std(R)·Σ sign(i)·z(i)/n` — Faktormodell mit **Gleichgewichtung** | (hier) |
| 1.3 | `rank_s = Σ sign(i)·rank_s(i)` — Rangaggregation ohne Renditeschätzung | (hier) |
| 2.1 | ADF-Regression `Δy(t) = λy(t−1) + μ + βt + …` | [[Halbwertszeit der Mean Reversion & Kointegration (Chan)]] |
| 2.2–2.4 | Varianz-Diffusion, Hurst-Exponent `⟨…⟩ ∼ τ^(2H)` | dito |
| 2.5–2.6 | Ornstein-Uhlenbeck, **Halbwertszeit = −log(2)/λ** | dito |
| 2.7 | Johansen-Vektorform `ΔY(t) = ΛY(t−1) + …` | dito |
| 3.1–3.4 | Preis-Spread, Log-Preis-Spread, Kapital- vs. Stückgewichte | [[Bollinger-Bänder, Scaling-in & Kalman-Filter]] |
| 3.5–3.13 | Kalman-Filter: Mess-, Übergangs-, Prognose- und Update-Gleichungen | dito |
| 3.14–3.20 | Kalman als Market-Making-Modell, `Ve` als Funktion der Ordergröße | dito |
| 4.1 | `wᵢ = −(rᵢ − ⟨r⟩)/Σ|rₖ − ⟨r⟩|` — Cross-sectional Long-Short-Gewichte | (hier) |
| 5.11 | `ES×50 = −0,3906·VX×1000 + $77.150` | [[Roll Return, Contango & Backwardation]] |
| **8.1** | **`f = m/s²`** — Kelly-Leverage | [[Kelly-Formel & optimales Leverage (Chan)]] |
| **8.2** | **`F = C⁻¹M`** — Kelly-Allokation über Strategien | dito |
| 8.3 | `g = FᵀCF/2` — maximale Wachstumsrate | dito |
| 8.5 | `g(f) = ⟨log(1 + f·R)⟩` — allgemeine Wachstumsrate | dito |

**Nicht nummeriert, aber zentral:**

```
f_ruin          = 1 / |schlechteste Einzelrendite|      harte Leverage-Obergrenze
Half-Kelly      = f/2                                   uebliche Praxis
CPPI-Leverage   = D · f · (1 + drawdown)                sinkt automatisch mit dem Drawdown
Gap-Entry       = Vortages-High × (1 + 0,1 · std90)     Opening-Gap-Momentum
krit. Werte     √n × taegliche Sharpe:  1,282 / 1,645 / 2,326 / 3,091
                fuer p = 0,10 / 0,05 / 0,01 / 0,001
```

## Der Risikoteil in einem Bild

```
Ziel: Maximierung des LANGFRISTIGEN Kapitalwachstums —
      Risiko wird nur insoweit gemieden, wie es diesem Ziel im Weg steht.

  1. Wie viel Hebel?           →  Kelly f = m/s², in der Praxis Half-Kelly
                                  oder numerisch auf simulierten/historischen Renditen
  2. Und wenn ein maximaler
     Drawdown vorgegeben ist?  →  NICHT linear herunterskalieren.
                                  Besser: CPPI (Wachstum + harte Grenze zugleich)
  3. Einzelne Position?        →  Stop Loss — logisch bei Momentum,
                                  bei Mean Reversion nur GROESSER als der
                                  Backtest-Drawdown ansetzen
  4. Ganze Perioden meiden?    →  Leading Risk Indicators — aber JEDE Strategie
                                  einzeln testen, das Vorzeichen kann kippen
```

## Die wichtigsten Einzelbefunde

- **Kelly-Leverage ist eine Obergrenze, kein Sollwert.** Überschätztes `f` führt zum Ruin,
  unterschätztes nur zu weniger Wachstum — daher Half-Kelly. Russell 1000/2000 haben Kelly ≈ 1,8,
  während dreifach gehebelte ETFs darauf mit Leverage 3 arbeiten.
- **Konstantes Leverage zwingt zum Verkaufen in den Verlust.** Rechenbeispiel und die
  systemische Folge (Quant-Krise August 2007) auf der Kelly-Seite.
- **Drawdown-Halbierung erforderte Leverage-Teilung durch 7**, nicht durch 2.
- **CPPI liefert praktisch dieselbe Wachstumsrate** (0,002484 vs. 0,002525 pro Tag) bei
  Drawdown 0,5 statt 0,9.
- **Stop Loss bei Mean Reversion:** Die Aussage „schadet immer" ist selbst ein
  Survivorship-Bias-Artefakt. Lösung: Stop **größer** als der maximale Intraday-Drawdown des
  Backtests — kostenlos im Backtest, schützt aber gegen Regimewechsel.
- **Derselbe Risikoindikator, gegensätzliche Konsequenz:** VIX > 35 verdoppelt die Rendite der
  einen Strategie (8,7 % → 17,2 %) und zerstört die der anderen (13 % → 2,6 %).
- **Scaling-in ist in-sample beweisbar nie optimal** (Schoenberg & Corwin) — kann out-of-sample
  aber gewinnen, weil der Beweis konstante Volatilität voraussetzt.
- **Kalman-Filter liefert Hedge Ratio, Mittelwert und Standardabweichung in einem Verfahren** und
  ohne willkürlichen Lookback: EWA-EWC APR 26,2 %, Sharpe 2,4.
- **Momentum bei Futures kommt aus der Persistenz der Roll-Rendite** — das saubere Signal
  (Roll-Rendite statt Gesamtrendite) verdoppelte die Sharpe Ratio und halbierte den Drawdown.
- **Drei verschiedene Nullhypothesen, drei verschiedene Signifikanzen** für dieselbe Strategie:
  99 %, 88 % und praktisch 100 %.
- **Die Halbwertszeit setzt alle Lookbacks**, ohne dass man sie optimieren muss — und sagt
  vorab, ob Mean-Reversion-Handel überhaupt lohnt.

## Warum manche Strategien gar nicht erst getestet werden

Chans Ausschlusskriterien (Details auf
[[Futures-Datenaufbereitung & Backtesting-Fallstricke (Chan)]]): hohe Rendite bei niedriger
Sharpe Ratio und langer Drawdown-Dauer; Long-only ohne Vergleich gegen Buy-and-Hold; jede
Aktienstrategie ohne survivorship-bias-freie Daten; neuronale Netze mit dutzenden Knoten;
HFT-Backtests ohne Orderbuch und ohne Berücksichtigung der Reaktion anderer Teilnehmer.

## Chans Schlussgedanken

Zwei Urteilsfragen, die auch bei vollautomatischem Handel bleiben — und für die er seine eigene
Erfahrung angibt:

1. **Vor einem absehbaren Großereignis das Leverage senken?** Nein. Hat das Modell frühere
   Stressphasen im Backtest überstanden, gibt es keinen Grund. *„It is much better to start off
   with a more conservative leverage during good times than to have to lower it in bad ones."*
   Die „unknown unknowns" schaden, nicht die bekannten.
2. **Kelly über alle Strategien gemeinsam oder je Strategie einzeln?** Mathematisch ist gemeinsam
   optimal — aber nur unter der Annahme unveränderlicher Erwartungswerte und Volatilitäten. Chans
   Praxis: **je Strategie einzeln**, damit schwächelnde Strategien schnell absterben.

Und die Einordnung des Ganzen: Nicht-Stationarität der Finanzzeitreihen ist der Grund, warum
subjektives Urteil überhaupt nötig bleibt — Wissenschaft kann nur mit stationären Statistiken
umgehen. Weicht der Livebetrieb vom Backtest ab, liegt das oft **nicht** an einem
Backtesting-Fehler, sondern an einem echten Regimewechsel durch Regulierung oder Makroänderung.
Die Rolle des Managers ist dann, auf Basis fundamentalen Marktverständnisses zu beurteilen, ob
das Modell noch gilt.

## Bewusst nicht ins Wiki übernommen

- **Der MATLAB-Code als solcher** (jplv7/spatial-econometrics, Econometrics Toolbox,
  `pearsrnd`, `fminbnd`, `genhurst`, `vratiotest`, `johansen`, `cadf`, `ols`). Die Algorithmen
  stehen als Prosa und Python-nahes Pseudocode auf den Konzeptseiten; für Python gibt es
  `statsmodels` (ADF, Johansen, OLS), `scipy` und `filterpy`/`pykalman`.
- **Die Aktien-/ETF-Strategien im Detail** (Buy-on-Gap auf SPX-Aktien, SPY-Index-Arbitrage,
  Khandani-Lo-Long-Short, PEAD-Scraper für earnings.com). Dieses Projekt handelt ein einzelnes
  Futures-Instrument; die *Mechanismen* sind auf den Konzeptseiten erfasst, die
  Aktien-Implementierungen nicht.
- **Plattformvergleich** (Deltix, Progress Apama, MetaTrader, NinjaTrader, TradeStation,
  Marketcetera, FXone …) — Stand 2013 und für dieses Projekt gegenstandslos, das in Python mit
  `backtesting` arbeitet.
- **HFT-Ausführungstaktiken** (ratio trade, ticking/quote matching, flipping,
  momentum ignition) sind auf [[Momentum-Ursachen & Opening-Gap-Strategie]] nur zusammengefasst —
  sie setzen Kolokation und Direktfeeds voraus.
