---
tags: [source, algo-methodology, machine-learning]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[AI_in_Finance_and_Quantitative_Analysis]]"]
---

# AI in Finance and Quantitative Analysis (Source)

**Min-Yuh Day (National Taipei University), Vorlesungsfolien 1111AIFQA10**, 13.12.2022.
Rohquelle: `raw/literatur/AI_in_Finance_and_Quantitative_Analysis.md` (10.175 Zeilen).

> **Einordnung vorweg — diese Quelle ist deutlich dünner, als ihre Zeilenzahl vermuten lässt.**
> Rund **7.600 der 10.175 Zeilen** sind ein eingebetteter **Literatur-Survey** (Ozbayoglu,
> Gudelek & Sezer, *„Deep learning for financial applications: A survey"*, Applied Soft Computing
> 2020), abgedruckt als Tabellen der Form *Datensatz / Zeitraum / Feature Set / Methode /
> Performance-Kriterium / Referenz*. Das ist eine **Bibliografie von ~200 Papern**, keine
> Methodik: keine Formeln, keine Herleitungen, keine nachvollziehbaren Ergebnisse.
>
> Der eigentlich verwertbare Teil sind die letzten ~1.500 Zeilen: eine praktische
> Colab-Demonstration mit `ffn` und `backtesting.py`.

## Was die Folien angekündigt haben — und was tatsächlich drinsteht

Das Outline (Zeile 105 ff.) nennt vier Themen und verweist als Quelle auf Yves Hilpisch,
*Artificial Intelligence in Finance: A Python-Based Guide* (O'Reilly 2020):

| Angekündigt | Tatsächlich im Foliensatz |
|---|---|
| Algorithmic Trading | nur die `backtesting.py`-SMA-Crossover-Demo |
| **Risk Management** | **fehlt** — der Begriff taucht ausschließlich als *Kategorielabel* im Survey auf („Risk Management / Fraud Detection"), nicht als Methode |
| Trading Bot | fehlt |
| Event-Based Backtesting | fehlt (nur vektorisiertes `backtesting.py`) |

Für den Risikomanagement-Schwerpunkt dieses Ingests trägt die Quelle also **nichts** bei. Die
belastbaren Risikoseiten des Vaults kommen aus
[[Algorithmic Trading - Winning Strategies and Their Rationale (Source)]] (Chan) und
[[Testing and Tuning Market Trading Systems (Source)]] (Masters).

## Was verwertbar war

**1. Der `ffn`-Kennzahlenkatalog** → [[Performance-Kennzahlen-Katalog]]

`ffn.calc_stats().display()` liefert einen weit umfangreicheren Kennzahlensatz als das, was
`algo/` heute ausweist — inklusive Calmar Ratio, Sortino, durchschnittliche Drawdown-**Dauer** und
rollierender Gewinnquoten. Das ist die konkret übernehmbare Substanz dieser Quelle.

**2. Ein lehrreiches Benchmark-Versagen.** Die Demo backtestet einen 5/20-SMA-Crossover auf
BTC-USD (2016-01-01 bis 2021-12-31, $100.000 Startkapital, 0,2 % Kommission):

```
Return [%]                4137,45
Buy & Hold Return [%]    10879,29      ← Buy-and-Hold ist ZWEIEINHALBFACH besser
Sharpe Ratio                 0,60
Max. Drawdown [%]          −63,52
# Trades                      116
Win Rate [%]                35,34
Profit Factor                2,29
```

Die Folien präsentieren das ohne Kommentar als Ergebnis. Tatsächlich ist es ein Musterbeispiel für
Chans Ausschlusskriterium: **immer gegen den richtigen Benchmark messen.** Eine Long-only-Strategie
mit 4.137 % Rendite, die Buy-and-Hold um mehr als den Faktor 2 unterliegt, hat keinen Mehrwert —
die passende Kennzahl wäre die Information Ratio, nicht die Sharpe Ratio. Siehe
[[Futures-Datenaufbereitung & Backtesting-Fallstricke (Chan)]], Abschnitt „Wann man einen Backtest
gar nicht erst anfängt".

Zum Vergleich derselbe Zeitraum als reines Buy-and-Hold über `ffn`: Total Return 10.879 %,
Daily Sharpe 1,18, CAGR 118,79 %, Max Drawdown −83,40 %, Calmar 1,42.

**3. Parameter-Heatmap über zwei Dimensionen.** `bt.optimize()` mit `return_heatmap=True`:

```python
stats, heatmap = bt.optimize(
    n1=range(5, 65, 5), n2=range(10, 205, 5),
    constraint=lambda p: p.n1 < p.n2,
    maximize='Avg. Trade [%]', max_tries=600, random_state=0,
    return_heatmap=True)
plot_heatmaps(heatmap, agg='mean')
hm = heatmap.groupby(['n1', 'n2']).mean().unstack()
```

Das ist die **zweidimensionale** Fassung der Parameter-Sensitivitätskurven aus
[[Differential Evolution & Parameter-Sensitivität]] — und damit ein direkt nutzbares Muster für
`algo/backtest_walkforward.py`, das die Sensitivität bisher nur eindimensional (Stop-Puffer)
darstellt. Was die Folien **nicht** erwähnen: dass diese Optimierung Data-Snooping-Bias erzeugt
und die Fläche auf Glattheit zu beurteilen ist statt nur auf ihr Maximum.

**4. Die Survey-Taxonomie** als grobe Orientierung, welche Anwendungsfelder in der
DL-Finance-Literatur überhaupt besetzt sind: Kursprognose, algorithmisches Handeln,
Portfoliomanagement, Risiko-/Betrugserkennung, Sentiment-Analyse aus News und Social Media,
Kreditwürdigkeit, Fundamentalprognose. Die Folien selbst halten fest, dass **Kursprognose und
algorithmisches Handeln die beiden meistbearbeiteten Felder** sind.

## Bewusst nicht ins Wiki übernommen

- **Der gesamte Survey-Tabellenteil** (~7.600 Zeilen, ~200 Paper). Es sind Verweise auf fremde
  Arbeiten mit je einer Zeile Beschreibung — ohne Formeln, ohne Reproduzierbarkeit, ohne Bezug zu
  einem einzelnen Futures-Instrument. Wer daraus etwas will, braucht die Originalpaper.
- Die Colab-spezifischen Teile (`google.colab.files.download`, `!pip install`, `%pylab inline`)
  und die Plotly-Visualisierungen — projektfremd, `algo/` nutzt matplotlib.
- Der Syllabus der Lehrveranstaltung.
- **`pandas_datareader.data.DataReader(..., 'yahoo', ...)`** funktioniert seit Yahoos
  API-Umstellung nicht mehr; dieses Projekt nutzt korrekt `yfinance`
  (`algo/fetch_yfinance.py`).
