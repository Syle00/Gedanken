---
tags: [concept, algo-methodology, machine-learning, risikomanagement, referenz]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[2022-07-05 - Two Sigma - Machine Learning Models of Financial Data (Source)|Two Sigma — Machine Learning Models of Financial Data (Source)]]"]
---

# Meta-Labeling (López de Prado)

Die **einzige ML-Bauform, die zur Architektur dieses Projekts passt** — weil sie nicht versucht,
die Handelsidee zu ersetzen, sondern sie zu filtern. Aus Marcos López de Prado,
*Advances in Financial Machine Learning* (2018).

## Die Konstruktion

Zwei Modelle mit getrennten Aufgaben:

```
Primärmodell   →  Welche Richtung?  (long / short)
                  Beliebiger Signalgeber: Regelwerk, Momentum, fundamentale Sicht.
                  In diesem Projekt: die ICT-Regeln aus wiki/models/.

Sekundärmodell →  Soll dieses Signal überhaupt gehandelt werden — und wie groß?
                  Zielgröße ist NICHT die Rendite, sondern die Frage:
                  "Lag das Primärmodell hier richtig?"  (binär)
```

Das Sekundärmodell lernt also **nicht** den Markt vorherzusagen, sondern **die Fehler des
Primärmodells** vorherzusagen. Es unterdrückt Fehlsignale und bemisst die Positionsgröße nach
Zuversicht — es wirkt als Risikoschicht über dem Regelwerk.

## Warum das die richtige Bauform ist

Die zentrale Schwierigkeit beim ML im Handel ist das Verhältnis von Signal zu Rauschen: Ein Modell,
das aus rohen Kursen die Richtung lernen soll, hat kaum Struktur, an der es sich festhalten kann
(siehe [[Reinforcement Learning für Handel — Grenzen (Starke)]]). Meta-Labeling dreht das um:

- Die **Richtung** kommt aus einem Regelwerk, das ein Mensch versteht und begründen kann.
- Das ML-Verfahren bekommt eine **einfachere, besser gestellte Frage** — eine binäre
  Klassifikation mit klarer Zielgröße.
- Die Erklärbarkeit bleibt erhalten: Man kann jederzeit sagen, **warum** ein Trade entstand.
  Das Sekundärmodell erklärt nur, warum einer **nicht** entstand.

Für dieses Projekt entscheidend: Es ist die einzige Variante, die mit dem Grundsatz vereinbar ist,
dass das ICT-Wiki die Regelquelle bleibt (`CLAUDE.md`, Layer 0).

## Voraussetzungen

- Ein **validiertes** Primärmodell. Meta-Labeling repariert kein Signal ohne Vorteil — es filtert
  nur ein vorhandenes. Reihenfolge: erst das Gate aus
  [[Vier-Stufen-Strategieentwicklung (Masters)]], dann Meta-Labeling.
- **Genug beschriftete Trades.** Jeder Trade des Primärmodells liefert genau einen Datenpunkt
  („war richtig" / „war falsch"). Bei wenigen Trades pro Woche dauert es entsprechend lange, bis
  eine brauchbare Stichprobe entsteht.
- **Purged Cross-Validation mit Embargo**, weil sich die Label über die Haltedauer überlappen —
  ohne das entsteht Datenleckage.

## Bekannte Schwächen

- Das Sekundärmodell kann selbst überanpassen, besonders bei stark adaptiven Eingangsmerkmalen.
- Es **erbt die Verzerrungen des Primärmodells**. Liefert das Regelwerk in einem bestimmten
  Marktregime systematisch schlechte Signale, fehlen dem Sekundärmodell dort die positiven
  Beispiele, um überhaupt etwas zu lernen.
- Es ist kein Ersatz für ein gutes Primärmodell, sondern ein Verstärker seiner Qualität — in beide
  Richtungen.

## Stand in diesem Projekt

**Nicht umgesetzt und derzeit nicht sinnvoll umsetzbar.** Es existiert noch kein validiertes
Primärmodell und keine Trade-Historie, aus der sich Label gewinnen ließen. Eingeordnet als
Ausbaustufe **nach** Regelregister und Validierungs-Gate, siehe
[[Machine Learning für den Algo — Bewertung (laufend)]].

Die Eingangsmerkmale für das spätere Sekundärmodell entstehen dabei ohnehin schon: Die
Beobachtungsschicht protokolliert Sweeps, FVGs, Strukturbrüche, Killzone-Zugehörigkeit und
Macro-Fenster — genau die strukturellen Größen, die ein Sekundärmodell bräuchte.

## Verwandt

- [[Machine Learning für den Algo — Bewertung (laufend)]]
- [[Universal Model & Instrument-Pooling]]
- [[Cross Validation vs. Walk-Forward (Masters)]] — markierter Widerspruch zu López de Prado
- [[Rule Significance Test (RST)]] — prüft die Entry-Regel isoliert, also das Primärmodell allein
- [[Risikomanagement (1% pro Trade)]] — Meta-Labeling würde hier als Größenmodulation ansetzen
