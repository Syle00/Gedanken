---
tags: [concept, algo-methodology, validation, kennzahlen]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[Testing and Tuning Market Trading Systems (Source)]]"]
---

# Profit pro Bar vs. pro Trade

Auf welcher Granularität Performancekennzahlen berechnet werden, entscheidet über ihre
Aussagekraft — und die branchenübliche Wahl (pro abgeschlossenem Trade) ist laut Masters die
schlechteste. Aus [[Testing and Tuning Market Trading Systems (Source)]] (Kap. 6).

## Vier mögliche Renditearten

1. **Nur Bars mit offener Position.** Masters' Favorit: feine Granularität, und
   inhaltlich sinnvoll („was bekomme ich dafür, dass ich das Risiko einer offenen Position
   trage?").
2. **Alle Bars, auch Nullrenditen ohne Position.** Maximale Information — enthält zusätzlich,
   *wie oft* man überhaupt im Markt ist. Nötig, wenn man selten-aber-treffsichere gegen
   oft-aber-ungenaue Systeme abwägen will.
3. **Blockweise gepoolt** (z.B. je 10 Bars, oder wochen-/monatsweise). Verliert Information und
   Datenpunkte, verdünnt aber wilde Einzel-Bars und reduziert Zufall. Genau die Form, die man für
   die Überwachung im Livebetrieb braucht — siehe
   [[Grenzen für Einzelrenditen & Drawdown]].
4. **Pro abgeschlossenem Trade (Round Turn).** Branchenstandard, weil intuitiv.

## Warum Trade-Renditen für die Statistik untauglich sind

**Datenverlust.** Dauert ein Trade im Schnitt 50 Bars, schrumpft die Stichprobe um Faktor 50.
Der Unterschied zwischen 10 und 500 Datenpunkten ist statistisch gewaltig.

**Informationsverlust.** Ein Long, der ruhig und stetig ins Ziel läuft, und einer, der zuerst
weit ins Minus taucht und erst am Ende dreht, ergeben dieselbe Trade-Rendite — bei völlig
verschiedenem Risiko.

**Und das trifft die Kennzahlen direkt.** Masters' Zahlenbeispiel für den Profit Factor:
Zwei Trades, jeder intern mit 101 Punkten Gewinnbewegung und 100 Punkten Verlustbewegung,
netto also je **+1 Punkt**.

- Auf Trade-Basis: keine Verlusttrades → `(1+1)/0` = **unendlich**.
- Auf Bar-Basis: `(101+101)/(100+100)` = **1,01** — praktisch wertlos.

Beim Sharpe Ratio gilt dasselbe: zwei Systeme können bei identischem Trade-Sharpe völlig
verschiedene Bar-Sharpes haben, je nachdem wie viel Volatilität *innerhalb* der Trades steckt.

**Systematischer Effekt:** Trade-basierte Kennzahlen sind praktisch immer **extremer** als
bar-basierte — teils wegen der kleineren Stichprobe, teils weil die marktübliche Schwankung
innerhalb eines Trades herausgemittelt wird. Extremer heißt hier: verführerischer.

> Masters' pragmatischer Rat: Für Präsentationen ruhig die Trade-Zahlen groß und fett
> ausweisen — das macht jeder, man muss vergleichbar bleiben. Für die eigene Forschung sind sie
> zu ignorieren.

## Voraussetzung: Ein-Bar-Konversion

Damit ein regelbasiertes System mit unbestimmter Haltedauer überhaupt Bar-Renditen liefert, wird
es in eine Kette von Ein-Bar-Trades umgeschrieben (Algorithmus auf
[[Walk-Forward Guard Buffer & Varianz-Inflation]]). Schreibt man den Backtest selbst, genügt es,
pro Bar die Mark-to-Market-Rendite der offenen Position zu notieren.

Nebeneffekte: kein Guard Buffer mehr nötig, genauere Drawdown-Berechnung (entspricht täglichem
Mark-to-Market) und die zwingende Voraussetzung für
[[CSCV (Combinatorially Symmetric Cross Validation)]].

## Beim Training zusätzlich zu entscheiden

Ein Detail aus dem `PER_WHAT`-Programm: Ob Bars **ohne** offene Position in das
Optimierungskriterium eingehen (`all_bars`), macht für den Profit Factor keinen Unterschied, wohl
aber für mittlere Rendite und Sharpe — dort wird die Kennzahl dadurch empfindlich dafür, wie oft
das System überhaupt handelt. Abgeschlossene Trades werden im **Training** nie verwendet;
Masters nennt das „a terrible approach because of massive information loss".

## Bezug zu diesem Projekt

`algo/backtest_bt.py` und `algo/backtest_ensemble.py` rechnen über die `backtesting`-Bibliothek
auf **Trade-Basis** — Profit Factor und Drawdown in
[[Ensemble-Strategie — Backtest-Ergebnis & Commission-Verzerrung (laufend)]] sind also genau die
Sorte Zahl, vor der dieses Kapitel warnt. Bei den aktuellen Stichprobengrößen (Dutzende Trades)
wiegt das doppelt.

Konsequenz für künftige Reports: Bar-Renditen der offenen Positionen als zusätzliche
Ausgabespalte mitführen und Profit Factor/Sharpe **zusätzlich** darauf berechnen. Ohne das sind
weder [[Konfidenzgrenzen für Renditen (t-Test, Bootstrap, BCa)]] noch
[[Grenzen für Einzelrenditen & Drawdown]] sinnvoll anwendbar — beide setzen viele, möglichst
unabhängige Datenpunkte voraus.

Passt zu einer bereits im Vault stehenden Aussage: [[Vier-Stufen-Strategieentwicklung (Masters)]]
verlangt Objective-Funktionen auf Bar-Granularität (Positions-Vektor × geshiftete Returns) —
dies ist die ausführliche Begründung dafür.
