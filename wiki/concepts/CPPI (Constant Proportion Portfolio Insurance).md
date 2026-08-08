---
tags: [concept, algo-methodology, risikomanagement, drawdown, referenz]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[Algorithmic Trading - Winning Strategies and Their Rationale (Source)]]"]
---

# CPPI (Constant Proportion Portfolio Insurance)

Das einzige Verfahren, das **beide** widerstreitenden Ziele erfüllt: maximale Wachstumsrate *und*
harte Drawdown-Obergrenze. Aus
[[Algorithmic Trading - Winning Strategies and Their Rationale (Source)]] (Chan, Kap. 8).

## Die Konstruktion

```
Gegeben:  f  = optimales Kelly-Leverage der Strategie
          D  = maximal erlaubter Drawdown (z.B. 0,5 fuer 50 %)

1.  Konto in zwei Teile spalten:
       Trading-Subkonto :  D   × Gesamt-Equity
       Cash-Konto       : (1−D) × Gesamt-Equity   (liegt einfach da)

2.  Auf das SUBKONTO das volle Leverage f anwenden.
       Portfolio-Marktwert = f × Subkonto-Equity

3.  Neues Allzeithoch der GESAMT-Equity erreicht?
       → Subkonto auf D × Gesamt-Equity zuruecksetzen, Rest ins Cash-Konto.

4.  Verluste?
       → KEIN Transfer zwischen Cash und Subkonto.

5.  Subkonto aufgebraucht?
       → Strategie abschalten. Der maximal erlaubte Drawdown −D ist erreicht.
```

Weil das Cash-Konto nie angetastet wird, kann der Gesamtverlust **konstruktionsbedingt** `−D`
nicht überschreiten.

Nebeneffekt, den Chan ausdrücklich hervorhebt: Das ist zugleich ein **geordneter, prinzipiengeleiteter
Weg, eine verlierende Strategie stillzulegen** — im Gegensatz zur üblichen Variante, bei der der
Ausstieg vom emotionalen Zusammenbruch des Portfoliomanagers getrieben wird.

## Warum das nicht dasselbe ist wie Leverage `f·D`

Der naheliegende Einwand: Warum nicht einfach das ganze Konto mit `L = f·D` hebeln? Drei Gründe:

1. Es gibt **keine Garantie**, dass der Drawdown `−D` dann nicht überschritten wird.
2. Selbst mit zusätzlichem Stop Loss bei `−D` ist die zusammengesetzte Rendite nicht dieselbe —
   außer die Renditen jeder Periode wären positiv (also Drawdown exakt null).
3. **Der eigentliche Mechanismus:** Sobald ein Drawdown auftritt, reduziert CPPI die Ordergröße
   **deutlich schneller** als die Alternative. Dadurch wird es „almost impossible", dass das
   Konto den Maximalverlust überhaupt erreicht — trotz Kelly-Leverage auf dem Subkonto.

## Der Wachstumspreis ist praktisch null

Chan kennt keinen mathematischen Beweis, zeigt es aber empirisch an 100.000 simulierten Tagen mit
`D = 0,5`:

| Verfahren | Wachstumsrate/Tag | max. Drawdown |
|---|---|---|
| CPPI | **0,002484** | **< 0,5** (per Konstruktion) |
| Leverage `f·D` ohne Stop | 0,002525 | **0,9** |

Also: praktisch **identische Wachstumsrate**, aber 0,5 statt 0,9 Drawdown. Das ist der ganze
Punkt der Methode.

## Implementierung

Chans MATLAB-Fassung (Box 8.6):

```matlab
g_cppi=0; drawdown=0; D=0.5;
for t=1:length(ret_sim)
    g_cppi = g_cppi + log(1 + ret_sim(t)*D*optimalF*(1+drawdown));
    drawdown = min(0, (1+drawdown)*(1+ret_sim(t)) - 1);
end
g_cppi = g_cppi/length(ret_sim);
```

Python-Portierung mit erläuterten Größen:

```python
def cppi_growth(returns, optimal_f, D=0.5):
    """Wachstumsrate unter CPPI.
       drawdown ist <= 0 und misst den Abstand zum bisherigen Hochwasserstand.
       Effektives Leverage = D · f · (1 + drawdown)  — es SINKT automatisch mit
       wachsendem Drawdown und ist am Hochwasserstand (drawdown = 0) maximal D·f."""
    g, drawdown = 0.0, 0.0
    for r in returns:
        g += np.log1p(r * D * optimal_f * (1.0 + drawdown))
        drawdown = min(0.0, (1.0 + drawdown) * (1.0 + r) - 1.0)
    return g / len(returns)
```

Der Kern steckt im Faktor `(1 + drawdown)`: er ist 1 am Allzeithoch und geht gegen 0, wenn sich
der Drawdown `−D` nähert. Das effektive Leverage schrumpft also **automatisch und stetig**, ohne
dass man eine Regel dafür formulieren müsste.

## Zwei harte Einschränkungen

1. **Nur für Ein-Strategie-Konten.** Bei einem Multi-Strategie-Konto können profitable
   Strategien die unprofitablen quersubventionieren, sodass der Drawdown nie groß genug wird, um
   das Abschalten auszulösen. Dann bleibt die kaputte Strategie unbemerkt am Leben.
2. **Kein Schutz über Nacht.** CPPI teilt dieses Problem mit dem Stop Loss: Ein großer Drawdown
   im Overnight-Gap oder bei ausgesetztem Handel lässt sich damit nicht verhindern. Das einzige
   Gegenmittel ist der Kauf von Out-of-the-Money-Optionen vor einem erwarteten Marktschluss — was
   teuer ist und sich nur bei planbaren Handelspausen lohnt.

## Bezug zu diesem Projekt

Der Vault hat bisher **keinen** Drawdown-Deckel — weder als Regel noch im Code. `algo/`s
Risikosteuerung besteht aus der 1-%-pro-Trade-Regel
([[Risikomanagement (1% pro Trade)]]) und dem Margin-Deckel in `pnl.py::risk_size()`. Beides
begrenzt das Risiko **pro Position**, nichts begrenzt den **kumulierten** Verlust.

CPPI wäre dafür das passende Werkzeug und ist bemerkenswert billig zu implementieren: ein
laufender Hochwasserstand plus ein Faktor auf die Positionsgröße. Besonders relevant für
Roadmap-Stufe 5/6 (Paper Trading → echtes Kapital) in [[Algo-Trading: Arbeitsstandards]] — dort
ist ein harter, mechanischer Verlustdeckel wertvoller als jede nachträgliche Analyse.

Voraussetzung ist ein belastbares `f`, siehe [[Kelly-Formel & optimales Leverage (Chan)]].
Für die Frage, wie groß der Drawdown realistisch werden kann, siehe
[[Grenzen für Einzelrenditen & Drawdown]] (Masters) — dort auch die Warnung, dass das im Projekt
verwendete Verfahren ihn systematisch unterschätzt.

Alternative und Abgrenzung: [[Stop Loss bei Mean Reversion vs. Momentum]] — Chan bevorzugt CPPI,
weil ein Strategie-Stop-Loss nur **einmal im Leben** einer Strategie feuern kann und damit ein
unbrauchbar grobes Instrument ist.
