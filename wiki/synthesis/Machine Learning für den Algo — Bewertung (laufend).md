---
tags: [synthesis, algo-methodology, machine-learning, bewertung, laufend]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[2022-07-05 - Two Sigma - Machine Learning Models of Financial Data (Source)|Two Sigma — Machine Learning Models of Financial Data (Source)]]", "[[2019-09-05 - Reinforcement Learning for Trading (Tom Starke) (Source)|Reinforcement Learning for Trading — Practical Examples and Lessons Learned (Source)]]", "[[Testing and Tuning Market Trading Systems (Source)]]"]
---

# Machine Learning für den Algo — Bewertung (laufend)

Antwort auf die Frage: **Macht es Sinn, Machine Learning in den Algorithmus zu integrieren?**
Bewertet gegen den Stand von 2026-08-08, wird bei neuen Quellen oder neuer Datenlage fortgeschrieben.

## Kurzantwort

**Nicht als Signalgeber. Ja an drei genau umrissenen Stellen — und eine davon ist sofort und ohne
jeden ML-Code nutzbar.**

| Einsatzort | Urteil | Wann |
|---|---|---|
| **Pooling über Instrumente** | **Ja, sofort** | Stufe 1, kostet nichts |
| **Merkmale statt Rohdaten** | **Ja, sofort** | bereits vorhanden |
| Meta-Labeling als Filter | Ja, aber später | nach Regelregister + Gate |
| RL als Signalgeber | **Nein** | absehbar nicht |
| RL für Orderausführung | Nein, nicht beschaffbar | Datenzugang fehlt |
| Deep Learning auf Kursdaten | **Nein** | Größenordnungen zu wenig Daten |

## Was dagegen spricht

### Die Größenordnung

Two Sigma trainiert das in [[2022-07-05 - Two Sigma - Machine Learning Models of Financial Data (Source)|Two Sigma — Machine Learning Models of Financial Data (Source)]]
gezeigte Modell auf **drei Jahren Event-für-Event-Orderbuchdaten von rund 1.000 Aktien** —
hunderte Milliarden Datenpunkte, verteilt über **25 GPUs**. Dieses Projekt verfügt über 394
Handelstage. Der Abstand ist nicht graduell, sondern um Größenordnungen.

Sirignano benennt die Folge selbst: Deep-Learning-Modelle haben hunderttausende bis Millionen
Parameter, und bei zu wenig Daten führt das zu Überanpassung. Er räumt zwar ein, dass ML auch bei
mittelgroßen Datensätzen möglich bleibt — aber nur mit besonders sorgfältiger Prüfung auf
Überanpassung.

### Das Rauschen

Starke, aus der Praxis: *„LSTMs and all these other fancy machine learning tools are really not
designed to deal with a lot of noise. Image recognition doesn't have a lot of noise."* Seine
Reinforcement Learner liefen auf echten Kursreihen in lokale Optima, waren zwischen Läufen nicht
reproduzierbar und erzeugten keine konsistenten Gewinne. Details:
[[Reinforcement Learning für Handel — Grenzen (Starke)]].

### Die Warnung, die für jedes Modell gilt

Sirignano rechnet vor, dass ein Modell mit **korrekter** Richtungsvorhersage trotzdem Geld
verlieren kann, weil zum Briefkurs gekauft und zum Geldkurs verkauft wird:

> *„Even if a model can predict future price moves with an accuracy greater than 50 %, a trading
> strategy based upon that model may not be profitable and could in fact lose money."*

Das deckt sich exakt mit Masters' „Percent Wins Fallacy" und mit
[[Implementation Shortfall]]. Höhere Vorhersagegenauigkeit ist damit **kein** eigenständiges Ziel.

## Was sofort nutzbar ist

### 1. Pooling über Instrumente — der eigentliche Gewinn

Der wertvollste Befund der ganzen Recherche, und er braucht **kein** Machine Learning:

> *„The universal model most strongly outperforms the stock-specific models on stocks with less
> data."* (Sirignano & Cont, Quantitative Finance 2019)

Ein gemeinsames Modell über viele Instrumente schlägt instrumentspezifische Anpassung — **am
deutlichsten dort, wo wenig Daten vorliegen**. Genau die Lage dieses Projekts.

Übertragen auf gewöhnliche Regelvalidierung heißt das: **einen gemeinsamen Parametersatz über alle
Instrumente validieren statt je Instrument anzupassen.** Weniger Freiheitsgrade, schlechtere
In-Sample-Zahlen, robustere Ergebnisse außerhalb der Stichprobe. Ausführlich:
[[Universal Model & Instrument-Pooling]].

### 2. Merkmale statt Rohdaten — bereits erfüllt

Starkes konstruktiver Befund: Auf rohen Kursreihen scheiterte sein Lerner, auf einer geglätteten
Reihe funktionierte er. Sein Schluss — der Reihe erst eine **geometrische Bedeutung** geben.

Dieses Projekt tut das bereits: `tools/analyze_ohlc.py` extrahiert FVGs, Sweeps, Strukturbrüche,
Displacement und Macro-Fenster. Das **sind** die strukturellen Merkmale. Ein Lernverfahren würde
hier auf diesen aufsetzen, nie auf rohem OHLC — und die Beobachtungsschicht protokolliert sie
ohnehin schon.

Unabhängiger Nebenbefund von Starke, der ICT stützt: Tageszeit, Wochentag und Jahreszeit als
Eingangsmerkmale verbessern das Ergebnis spürbar.

## Was später sinnvoll wird

**Meta-Labeling** ([[Meta-Labeling (López de Prado)]]) ist die einzige ML-Bauform, die zur
Architektur dieses Projekts passt: Das ICT-Regelwerk bestimmt die **Richtung**, ein zweites Modell
entscheidet nur, **ob** dieses Signal gehandelt wird und **wie groß**. Zielgröße ist nicht die
Rendite, sondern „lag die Regel hier richtig".

Vorteile in dieser Reihenfolge: Die Frage an das Lernverfahren wird einfacher (binär statt
Regression auf Rauschen), die Erklärbarkeit bleibt erhalten, und das Wiki bleibt Regelquelle.

**Voraussetzungen, die noch fehlen:** ein validiertes Primärmodell, genügend beschriftete Trades
(jeder Trade ergibt genau einen Datenpunkt), und Purged Cross-Validation mit Embargo gegen
Datenleckage durch überlappende Label. Einzuordnen **nach** Regelregister und Validierungs-Gate.

## Was nicht geht

- **RL als Signalgeber.** Siehe oben — Rauschen, lokale Optima, Stichprobenhunger.
- **RL für die Orderausführung.** Bei Two Sigma nachweislich erfolgreich (positive Kostenersparnis
  über rund 100 Aktien), braucht aber Orderbuchdaten Ereignis für Ereignis. Für ein Privatkonto bei
  IBKR nicht beschaffbar. Der Zweck — bessere Einstiegszeitpunkte innerhalb einer beschlossenen
  Zone — bleibt bestehen und wird stattdessen regelbasiert gelöst.
- **Deep Learning direkt auf Kursdaten.** Siehe Größenordnung.

## Bedingungen für eine Neubewertung

Diese Seite wird fortgeschrieben, wenn eine der folgenden Bedingungen eintritt:

1. Mehr als etwa 1.000 abgeschlossene, protokollierte Trades des Primärmodells liegen vor →
   Meta-Labeling wird prüfbar.
2. Eine Datenquelle für Orderbuchdaten auf Ereignisebene wird verfügbar → RL für Ausführung wird
   prüfbar.
3. Eine neue Quelle widerlegt einen der obigen Punkte.

## Offene Frage

Ob das Pooling zwischen **Devisen und Index-Futures** gerechtfertigt ist, oder ob die Unterschiede
(kein Tagesgap im Devisenmarkt, andere Sessionstruktur) getrennte Gruppen erzwingen, ist ungeprüft.
Die Gegenprobe ist einfach und gehört in den ersten Bericht: Schlägt der gepoolte Parametersatz die
instrumentspezifischen außerhalb der Stichprobe, war das Pooling gerechtfertigt.

## Verwandt

- [[Universal Model & Instrument-Pooling]], [[Meta-Labeling (López de Prado)]],
  [[Reinforcement Learning für Handel — Grenzen (Starke)]]
- [[Vier-Stufen-Strategieentwicklung (Masters)]] — das Gate, durch das auch ML-Regeln müssten
- [[Training Bias & Selection Bias]], [[Monte Carlo Permutation Test (MCPT)]]
- [[Statistische Muster jenseits der ICT-Konzepte (laufend)]] — die Explorationsschicht, in der ML
  eines Tages ein Werkzeug unter mehreren wäre
