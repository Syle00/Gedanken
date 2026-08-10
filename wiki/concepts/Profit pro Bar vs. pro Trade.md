---
tags: [concept, algo-methodology, validation, kennzahlen, referenz]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[Testing and Tuning Market Trading Systems (Source)]]"]
---

# Profit pro Bar vs. pro Trade

Auf welcher Granularität Performancekennzahlen berechnet werden, entscheidet über ihre
Aussagekraft — und die branchenübliche Wahl (pro abgeschlossenem Trade) ist laut Masters die
schlechteste. Aus [[Testing and Tuning Market Trading Systems (Source)]] (Kap. 6, Programm
`PER_WHAT.CPP`).

## Vier mögliche Renditearten

| # | Renditeart | Eigenschaften |
|---|---|---|
| 1 | **nur Bars mit offener Position** | Masters' Favorit. Feine Granularität, inhaltlich sinnvoll: „was bekomme ich dafür, dass ich das Risiko einer offenen Position trage?" Basis der meisten Verfahren im Buch. |
| 2 | **alle Bars**, auch Nullrenditen ohne Position | Maximale Information — enthält zusätzlich, *wie oft* man im Markt ist. Nötig, um selten-aber-treffsicher gegen oft-aber-ungenau abzuwägen. |
| 3 | **blockweise gepoolt** (10 Bars, wöchentlich, monatlich) | Verliert Information und Datenpunkte, verdünnt aber wilde Einzel-Bars und reduziert Zufall. Die Form für die Live-Überwachung — siehe [[Grenzen für Einzelrenditen & Drawdown]]. |
| 4 | **pro abgeschlossenem Trade** (Round Turn) | Branchenstandard, weil intuitiv. Für Statistik untauglich. |

Zu Nr. 3: aus einer Handvoll einzelner Bar-Renditen lässt sich nichts ablesen; aus einer Handvoll
Zehner-Blöcke schon etwas.

Masters' Seitenhieb zu Nr. 4: die Verbreitung liegt auch daran, dass diese Darstellung Gewinne
**und** Verluste übertreibt — „if a developer has a winning system, exaggeration is welcome, while
if the developer has a losing system, we'll never see it."

## Warum Trade-Renditen für die Statistik untauglich sind

**Datenverlust.** Dauert ein Trade im Schnitt 50 Bars, schrumpft die Stichprobe um Faktor 50. Der
Unterschied zwischen 10 und 500 Datenpunkten ist statistisch gewaltig.

**Informationsverlust.** Ein Long, der ruhig und stetig ins Ziel läuft, und einer, der zuerst weit
ins Minus taucht und erst am Ende dreht, ergeben **dieselbe** Trade-Rendite — bei völlig
verschiedenem Risiko. Die Information über das, was *während* des Trades passiert, ist weg.

**Und das trifft die Kennzahlen direkt.** Masters' Zahlenbeispiel für den Profit Factor:

```
Zwei Trades, jeder intern:  Gewinnbewegung 101 Punkte, Verlustbewegung 100 Punkte
                            → netto je +1 Punkt, KEIN Verlusttrade

Trade-Basis:  PF = (1 + 1) / 0                = ∞          ← "perfektes System"
Bar-Basis:    PF = (101 + 101) / (100 + 100)  = 1,01       ← praktisch wertlos
```

Beim **Sharpe Ratio** derselbe Mechanismus: zwei Systeme mit identischem Trade-Sharpe können
völlig verschiedene Bar-Sharpes haben, je nachdem wie viel Volatilität *innerhalb* der Trades
steckt — und der Bar-Wert ist der zutreffendere.

**Systematische Richtung:** Trade-basierte Kennzahlen sind praktisch **immer extremer** als
bar-basierte. Zwei Ursachen: die kleinere Stichprobe destabilisiert, und die natürliche
Marktschwankung innerhalb eines Trades wird herausgemittelt. Extremer heißt hier: verführerischer.

> Masters' pragmatischer Rat: Für Präsentationen ruhig die Trade-Zahlen groß und fett ausweisen —
> das macht jeder, man muss vergleichbar bleiben. *„But for your own internal research, ignore
> those numbers. Look at the fine-granularity returns that make up the complete trades. That's
> what counts."*

## Voraussetzung: Ein-Bar-Konversion

Damit ein regelbasiertes System mit unbestimmter Haltedauer überhaupt Bar-Renditen liefert, wird
es in eine Kette von Ein-Bar-Trades umgeschrieben (vollständiger Algorithmus und Begründung auf
[[Walk-Forward Guard Buffer & Varianz-Inflation]]). Schreibt man den Backtest selbst, genügt:

```python
if price[i] > thresh * ma[i]:      # Entry-Regel
    position = 1
elif price[i] < ma[i]:             # Exit-Regel
    position = 0
# sonst: Position unveraendert weiterfuehren
ret = price[i+1] - price[i] if position else 0.0
```

Nebeneffekte: kein Guard Buffer mehr nötig, genauere Drawdown-Berechnung (entspricht täglichem
Mark-to-Market) und die zwingende Voraussetzung für
[[CSCV (Combinatorially Symmetric Cross Validation)]].

## Die drei Renditearten in einem Durchlauf erzeugen

`PER_WHAT.CPP`'s `comp_return()` — `ret_type` 0 = alle Bars, 1 = nur offene Position,
2 = abgeschlossene Trades:

```python
def comp_return(ret_type, prices, istart, ntest, lookback, thresh, last_pos):
    """Erste Entscheidung faellt auf dem LETZTEN Trainingsbar (istart-1);
       deren Rendite ist der erste OOS-Wert."""
    out            = []
    position       = last_pos          # Position am Ende des Trainings — wichtig!
    prior_position = 0                 # fuer 'complete': immer flat starten (kein Future Leak)
    trial_thresh   = 1.0 + thresh
    open_price     = None

    for i in range(istart - 1, istart - 1 + ntest):
        ma = prices[i - lookback + 1 : i + 1].mean()

        if prices[i] > trial_thresh * ma:      # Entry
            position = 1
        elif prices[i] < ma:                   # Exit
            position = 0
        # sonst: Position beibehalten

        ret = prices[i+1] - prices[i] if position else 0.0

        if ret_type == 0:                                   # alle Bars
            out.append(ret)
        elif ret_type == 1:                                 # nur offene Position
            if position:
                out.append(ret)
        else:                                               # abgeschlossene Trades
            if position and not prior_position:
                open_price = prices[i]                      # Trade geoeffnet
            elif prior_position and not position:
                out.append(prices[i] - open_price)          # Trade geschlossen
            elif position and i == istart - 2 + ntest:      # am Datenende zwangsschliessen
                out.append(prices[i+1] - open_price)

        prior_position = position
    return out
```

Drei Feinheiten, die im Original ausdrücklich kommentiert sind:

- **`last_pos`** kommt aus dem Training. Feuert am ersten Testbar weder Entry- noch Exit-Regel,
  läuft die Position aus dem Training weiter — realistisch, denn im Livebetrieb kennt man seine
  Position. Ohne diesen Wert würde jeder Fold künstlich flat starten.
- **`prior_position = 0`** bei `ret_type == 2`: der Eröffnungspreis muss **innerhalb** des
  Testblocks liegen, sonst leckt Trainingsinformation in die Trade-Rendite.
- Bei Systemen, die direkt von long auf short drehen oder mehrere Positionen halten, muss dieser
  Block erweitert werden — die übliche Konvention ist „alter Trade zu, neuer Trade auf, selber
  Bar", aber es gibt andere Buchhaltungen.

**Blockweises Poolen** (Renditeart 3) geschieht nachgelagert aus `ret_type == 0`:

```python
crunch = 10
grouped = [np.mean(r[i:i+crunch]) for i in range(0, len(r), crunch)]
```

## Beim Training zusätzlich zu entscheiden

Der `all_bars`-Schalter in `opt_params()`: Ob Bars **ohne** offene Position ins
Optimierungskriterium eingehen.

```
all_bars = 0 :  nur Bars mit offener Position zaehlen
all_bars = 1 :  alle Bars zaehlen (auch Nullrenditen)
```

- **Profit Factor:** kein Unterschied — Nullrenditen erhöhen weder Gewinn- noch Verlustsumme.
- **Mittlere Rendite und Sharpe:** deutlicher Unterschied. Mit `all_bars = 1` wird die Kennzahl
  empfindlich dafür, **wie oft** das System handelt: ein selten handelndes System wird bestraft.

**Abgeschlossene Trades werden im Training nie verwendet** — Masters nennt das „a terrible
approach because of massive information loss".

## Bezug zu diesem Projekt

`algo/backtest_bt.py` und `algo/backtest_ensemble.py` rechnen über die `backtesting`-Bibliothek auf
**Trade-Basis**. Profit Factor, Win Rate und Drawdown in
[[Ensemble-Strategie — Backtest-Ergebnis & Commission-Verzerrung (laufend)]] sind also genau die
Sorte Zahl, vor der dieses Kapitel warnt. Bei den aktuellen Stichprobengrößen (Dutzende Trades)
wiegt das doppelt.

**Konkreter Umbau:** `stats._trades` liefert Entry-/Exit-Bar je Trade — daraus lässt sich eine
Bar-für-Bar-Mark-to-Market-Serie rekonstruieren, ohne die Strategie anzufassen. Profit Factor und
Sharpe **zusätzlich** darauf berechnen und beide Zahlen ausweisen.

Ohne diesen Schritt sind drei weitere Verfahren nicht sinnvoll anwendbar, weil sie alle viele und
möglichst unabhängige Datenpunkte brauchen:
[[Konfidenzgrenzen für Renditen (t-Test, Bootstrap, BCa)]],
[[Grenzen für Einzelrenditen & Drawdown]] und
[[CSCV (Combinatorially Symmetric Cross Validation)]] (dort ist die Bar-Matrix sogar strukturelle
Voraussetzung).

Passt zu einer bereits im Vault stehenden Aussage: [[Vier-Stufen-Strategieentwicklung (Masters)]]
verlangt Objective-Funktionen auf Bar-Granularität (Positions-Vektor × geshiftete Returns) — dies
ist die ausführliche Begründung dafür.

## Implementierung

`algo/masters.py`: `bar_returns_from_trades(trades, bars, only_open=True)` rechnet `stats._trades` der `backtesting`-Lib in Bar-Renditen um — die Eintrittstür für alle übrigen Verfahren. Dazu `profit_factor()`, `log_profit_factor()`, `sharpe_ratio()` auf Bar-Basis.

**Seit 2026-08-11 in den Report verdrahtet** (Backlog 7, siehe `algo/PLAN.md`): `algo/confidence.py::bar_metrics`/`print_bar_metrics` nutzt diese Funktionen und stellt im `backtest_bt.py`-Report Profit Factor und Sharpe **auf Bar- neben Trade-Basis** gegenüber. Erster realer Lauf (36 von 50 Tagen, MNQ): Profit Factor Trade 0,549 vs. Bar 0,872 — die Abweichung ist also nicht bloß Masters' Lehrbeispiel, sondern messbar im eigenen Backtest.

Selbstcheck: `python algo/masters.py` und `python algo/confidence.py` (beide in `algo/selfcheck.py`).
