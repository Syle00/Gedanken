---
tags: [concept, algo-methodology, machine-learning, validation, referenz]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[2022-07-05 - Two Sigma - Machine Learning Models of Financial Data (Source)|Two Sigma — Machine Learning Models of Financial Data (Source)]]"]
---

# Universal Model & Instrument-Pooling

**Der praktisch wertvollste Befund aus der ML-Literatur für dieses Projekt — und er lässt sich
ohne eine einzige Zeile Machine-Learning-Code nutzen.**

Aus [[2022-07-05 - Two Sigma - Machine Learning Models of Financial Data (Source)|Two Sigma — Machine Learning Models of Financial Data (Source)]] (Justin Sirignano, Two Sigma
Securities / Oxford). Begutachtete Fassung: Sirignano & Cont, *Universal features of price formation
in financial markets*, Quantitative Finance 19(9), 2019, [arXiv:1803.06917](https://arxiv.org/abs/1803.06917).

## Der Befund

Ein **einziges** Modell, trainiert auf den **zusammengelegten** Daten hunderter Instrumente,
schlägt durchgängig die Modelle, die für jedes Instrument einzeln angepasst wurden.

| Prüfung | Ergebnis |
|---|---|
| Universelles Modell vs. instrumentspezifische Modelle, ~500 Aktien, 3 Monate out-of-sample | Universelles Modell gewinnt durchgängig |
| Übertragung auf **nie trainierte** Instrumente (Training ~500 Titel, Test ~500 andere) | Genauigkeit weiterhin deutlich über 50 % |
| Stabilität über ein Jahr nach Ende des Trainingszeitraums | gehalten |

Und der Satz, der dieses Projekt direkt betrifft:

> *„The universal model most strongly outperforms the stock-specific models on stocks with **less
> data**."*

## Warum das funktioniert

Zwei Gründe, beide von Sirignano im Q&A genannt:

1. **Weniger Überanpassung.** Ein instrumentspezifisches Modell hat wenig Daten und passt sich dem
   Rauschen an. Das gepoolte Modell hat ein Vielfaches davon.
2. **Transferlernen zwischen Regimen.** Sein Beispiel: Instrument A hatte in der verfügbaren
   Historie nie eine Hochvolatilitätsphase, Instrument B schon. Kippt A später in dieses Regime,
   kennt das gepoolte Modell die Situation bereits — das Einzelmodell steht ratlos da.

Voraussetzung ist, dass die zugrunde liegende Mechanik über die Instrumente hinweg **tatsächlich
gemeinsam** ist. Für die Preisbildung aus Angebot und Nachfrage im Orderbuch weisen Sirignano &
Cont genau das nach.

## Übertragung auf dieses Projekt

**Das Prinzip ist von Machine Learning unabhängig.** Es gilt für jede Regel mit Parametern.

Konkret: Wenn eine ICT-Regel einen Schwellwert hat (Mindestgröße eines FVG, Alter eines
Liquiditätslevels, Fenstergröße eines Macros), dann gibt es zwei Wege, ihn zu bestimmen:

- **Je Instrument einzeln anpassen** — mehr Freiheitsgrade, bessere In-Sample-Zahlen, und laut
  diesem Befund schlechtere Ergebnisse außerhalb der Stichprobe.
- **Einen gemeinsamen Parametersatz über alle Instrumente** validieren — weniger Freiheitsgrade,
  schlechtere In-Sample-Zahlen, robuster außerhalb.

Der Befund spricht klar für den zweiten Weg, **und am deutlichsten dort, wo wenig Daten vorliegen**
— also genau in der Lage dieses Projekts (`algo/PLAN.md`: Stichprobe „noch nicht belastbar").

Praktischer Nebeneffekt: Mit EURUSD, GBPUSD, USDJPY, MNQ und MES gepoolt steht einer Regel das
Mehrfache an Beobachtungen zur Verfügung, ohne einen einzigen Tag länger zu warten.

**Einschränkung, die zu prüfen ist:** Devisen und Index-Futures teilen die Session-Struktur und die
Dollar-Abhängigkeit, aber nicht alles. NDOG existiert im Devisenmarkt praktisch nicht (kein
Tagesgap). Das Pooling ist deshalb **je Konzept** zu rechtfertigen, nicht pauschal — und die
Gegenprobe ist einfach: Schlägt der gepoolte Parametersatz die instrumentspezifischen
out-of-sample, war das Pooling gerechtfertigt.

## Verwandt

- [[Machine Learning für den Algo — Bewertung (laufend)]]
- [[Training Bias & Selection Bias]] — instrumentspezifische Anpassung ist eine Form der Auswahl
- [[Nested Walkforward]] — nötig, sobald zwischen Parametersätzen ausgewählt wird
- [[Vier-Stufen-Strategieentwicklung (Masters)]] — das Gate, durch das beide Varianten müssen
