---
tags: [concept, algo-methodology, validation, walk-forward]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[Testing and Tuning Market Trading Systems (Source)]]"]
---

# Nested Walkforward

Walk-Forward **innerhalb** von Walk-Forward. Notwendig, sobald zwei Optimierungsstufen
übereinanderliegen — die zweite Stufe darf nur auf **OOS-Ergebnissen** der ersten aufsetzen.
Aus [[Testing and Tuning Market Trading Systems (Source)]] (Kap. 5).

## Wann es zwingend ist

Immer, wenn laufend zwischen konkurrierenden Systemen/Instrumenten/Kennzahlen ausgewählt wird:

- Mehrere Systeme für verschiedene Marktregime (Trendfolger, Mean Reversion, Channel Breakout)
  und man handelt jeweils das zuletzt beste.
- Ein System auf vielen Aktien, und man handelt die Titel, die zuletzt am besten liefen.
- Man weiß nicht, ob mittlere Rendite, Sharpe oder Profit Factor das richtige Auswahlkriterium
  ist, und lässt auch **das** mitlaufen.

Der Grund ist [[Training Bias & Selection Bias]]: In-Sample-Performance sagt nichts über die
Zukunft, also darf die Auswahlstufe niemals auf In-Sample-Zahlen der ersten Stufe schauen. Also
braucht die zweite Stufe eine eigene Quelle unverzerrter Zahlen — und die liefert nur ein
inneres Walk-Forward (Level-1). Die Entscheidungen von Level-2 müssen dann ihrerseits OOS
bewertet werden (Level-2-Walk-Forward).

## Ablauf (Miniaturbeispiel: Level-1-Lookback 10 Bars, Level-2-Lookback 3 Bars)

```
Bars  1-10  → Konkurrenten trainieren; Bar 11 testen  → 1. Level-1-OOS-Fall
Bars  2-11  → Konkurrenten trainieren; Bar 12 testen  → 2. Level-1-OOS-Fall
Bars  3-12  → Konkurrenten trainieren; Bar 13 testen  → 3. Level-1-OOS-Fall
        (jetzt genug Level-1-OOS-Fälle für Level-2)
Level-1-OOS-Bars 11-13 → Level-2 trainieren; Bar 14 testen → 1. VOLL-OOS-Fall
Bars  4-13  → Konkurrenten trainieren; Bar 14 testen  → neuer Level-1-OOS-Fall
Level-1-OOS-Bars 12-14 → Level-2 trainieren; Bar 15 testen → 2. VOLL-OOS-Fall
… bis die Historie erschöpft ist
```

Wichtige Indizes in der Implementierung: `IS_start` (Trainingsstart Level 1), `OOS1_start` /
`OOS1_end` (Fenster der Level-1-OOS-Returns, das Level-2 anschaut), `OOS2_start` = fix bei
`IS_n + OOS1_n`, `OOS2_end` (laufender Index der endgültigen OOS-Reihe). Die Aufwärmphase
(`OOS1_end − OOS1_start < OOS1_n`) produziert noch keine Level-2-Fälle.

## Beispiel CHOOSER: 65 S&P-100-Titel, 1986–2017

Masters' Demonstrationsprogramm kauft täglich denjenigen Titel, der zuletzt am besten lief —
und wählt gleichzeitig laufend das **Kriterium**, mit dem „am besten" gemessen wird
(Total Return / Sharpe / Profit Factor). Level-1-Lookback: 1.000 Bars; Level-2-Lookback: 100
Level-1-OOS-Bars; 7.725 Handelstage. Ergebnis (annualisiert, `25200 × mittlere Log-Rendite`,
P-Werte aus [[Monte Carlo Permutation Test (MCPT)]] mit 1.000 Permutationen):

| | Rendite p.a. | P-Wert | Anteil gewählt |
|---|---|---|---|
| Gleichgewichteter Korb (Buy & Hold) | 8,75 % | — | — |
| nur Total Return als Kriterium | 17,89 % | 0,076 | 67,8 % |
| nur Sharpe Ratio | 12,98 % | 0,138 | 21,1 % |
| nur Profit Factor | 12,28 % | 0,180 | 11,1 % |
| **Kriterienwahl mitlaufend (Level-2)** | **19,12 %** | **0,027** | — |

Die Pointe steckt in den P-Werten: die einzelnen Kriterien sind je für sich nur schwach
signifikant (0,076–0,180), das geschachtelte Verfahren aber deutlich (0,027). Die adaptive
Kriterienwahl ist also nicht nur nominell besser, sondern statistisch belastbarer.

## Permutation im geschachtelten Fall

Wichtig bei der Kombination mit dem MCPT: Die Historie zerfällt in **drei** Segmente, die
getrennt permutiert werden müssen, weil im unpermutierten Lauf jeweils andere Daten nie in einem
OOS-Block landen:

1. `[1 … IS_n)` — der erste „Trainings"-Block; taucht nie in einem OOS-Ergebnis auf.
2. `[IS_n … IS_n+OOS1_n)` — der erste Level-1-OOS-Block; taucht nie im Level-2-OOS auf.
3. `[IS_n+OOS1_n … Ende)` — der eigentlich interessierende Voll-OOS-Bereich.

Würde man alles in einen Topf permutieren, könnten ungewöhnliche Kursbewegungen (starker Trend,
Volatilitätsspitze) aus Segment 1 in den OOS-Bereich wandern und dort Ergebnisse erzeugen, die
im Originallauf gar nicht möglich waren.

## Bezug zu diesem Projekt

`algo/signals.py` / `algo/backtest_ensemble.py` kombinieren mehrere Regeln zu einem Ensemble.
Sobald daraus eine *Auswahl* wird („heute handelt die Regel, die zuletzt am besten lief"), gilt
dieses Kapitel und der aktuelle einschichtige Walk-Forward in `algo/validate.py` reicht nicht
mehr aus. Solange das Ensemble statisch gewichtet ist, ist es nicht betroffen.

Siehe auch [[Cross Validation vs. Walk-Forward (Masters)]] (dort die deutlich einfacher zu
implementierende Variante CV-in-Walk-Forward) und
[[CSCV (Combinatorially Symmetric Cross Validation)]].
