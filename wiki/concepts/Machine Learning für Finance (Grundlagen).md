---
tags: [concept, quant-finance, machine-learning, mit-ocw]
created: 2026-08-12
updated: 2026-08-12
sources: ["[[2025-12-03 - MIT 15.S08 Lecture 23 - Introduction to Machine Learning (Source)]]"]
---

# Machine Learning für Finance (Grundlagen)

Formel- und Methodensammlung aus MIT-15.S08-Lecture 23 (Gastvorlesung John Hull, Rotman School):
Grundunterscheidung Statistik vs. ML, neuronale Netze, Backpropagation, Reinforcement Learning.

## Statistik vs. Machine Learning — methodischer Unterschied

Statistik: erst Hypothese aufstellen, dann Daten sammeln und die Hypothese testen. Machine
Learning: erst Daten sammeln, dann Muster/Modelle daraus ableiten, ohne vorherige Hypothese.
Terminologiewechsel: "unabhängige/abhängige Variable" (Statistik) ↔ "Features/Targets" (ML).

## Train/Validation/Test-Split

Standardaufteilung **60 % Training / 20 % Validation / 20 % Test**:

- Training Set: Modellparameter schätzen.
- Validation Set: Modellkomplexität wählen (Regel: Komplexität erhöhen, bis die Performance auf
  dem Validation Set schlechter wird — das ist der Overfitting-Punkt).
- Test Set: **wird nicht** zur Modellauswahl verwendet, dient ausschließlich als finale
  Out-of-Sample-Schätzung der tatsächlichen Modellgüte.
- Faustregel-Beispiel aus der Vorlesung (Polynomgrad-Wahl für ein Salär-Prognosemodell): ein Grad-5-
  Polynom passt die Trainingsdaten exzellent, versagt aber am Validation Set (Overfitting); ein
  lineares Modell ist zu einfach (Underfitting); ein quadratisches Modell war im Beispiel optimal.

## Neuronale Netze (ANN)

- Struktur: Input-Layer (bekannte Variablen) → mehrere Hidden Layers → Output-Layer (Zielgröße).
  Der Übergang zwischen Layern erfolgt nicht in einem Schritt (anders als lineare Regression),
  sondern in mehreren Stufen — das macht das Modell flexibler.
- Jeder Knoten: gewichtete Linearkombination der Vorgänger-Knoten, danach eine
  **Aktivierungsfunktion** (Identität, Sigmoid, Tanh, ReLU, …). Wird durchgehend die Identität
  verwendet, degeneriert das gesamte Netz zu einem linearen Modell.
- Parameter = alle Kantengewichte. Optimierung per **Gradientenverfahren**: Gewichte iterativ in
  Richtung des negativen Gradienten der Zielfunktion verschieben, Lernrate bestimmt Schrittweite
  (zu klein → langsame Konvergenz, zu groß → Oszillation um das Minimum).
- **Backpropagation**: nutzt die Kettenregel, um die partiellen Ableitungen der Zielfunktion nach
  allen Gewichten effizient zu berechnen (Funktion-von-Funktion-von-Funktion-Struktur des Netzes).
- Praxisbeispiel aus der Vorlesung: ein 3-Hidden-Layer-Netz (20 Neuronen/Layer, Sigmoid,
  Identität in der letzten Schicht) approximiert den Black-Scholes-Preis aus verrauschten
  Trainingsdaten sehr genau — Trainingsabbruch nach 2.575 Epochen (Validation-Set-Performance wird
  danach schlechter). Praxisnutzen: Neuronale Netze als **schnelle Surrogat-Modelle** für
  Monte-Carlo-Preismodelle exotischer Derivate (Sekundenbruchteile statt Minuten pro Preis).

## Reinforcement Learning

- Rahmen: Zustände (States), Aktionen (Actions), Belohnungen (Rewards) über eine Sequenz von
  Entscheidungen (nicht nur eine einzelne Entscheidung wie bei supervised learning).
- **Exploration vs. Exploitation**: Wahrscheinlichkeit `ε`, zufällig zu handeln (Exploration), vs.
  `1−ε`, die bisher beste bekannte Aktion zu wählen (Exploitation). `ε` startet bei 1 und fällt mit
  einem Decay-Faktor (Beispiel Nim-Spiel: `0,9995` pro Trial).
- Q-Learning-Update: `Q(s,a) ← Q(s,a) + α·(Gain − Q(s,a))`, Gain entweder als finaler Reward
  (Monte-Carlo-Methode) oder als Wert des Folgezustands (Temporal-Difference-Learning — konvergiert
  in der Vorlesung schneller als reines Monte-Carlo).
- Anwendung auf Derivate-Hedging: RL sucht eine Hedge-Strategie über mehrere Perioden statt der
  myopischen Greeks-Optimierung (Delta/Gamma/Vega). Ergebnis der Vorlesung: bei Vanilla-Optionen
  vergleichbare Performance wie Greeks-Hedging, aber signifikant geringere Transaktionskosten; bei
  Barriere-Optionen sogar überlegene Ergebnisse auch ohne Transaktionskosten. Zielfunktion frei
  wählbar (z.B. VaR95 oder CVaR95 statt reiner Varianzminimierung).

## Bezug zu diesem Projekt

- Der Train/Validation/Test-Split und die Overfitting-Erkennungsregel ("Komplexität erhöhen, bis
  die Validation-Performance schlechter wird") sind **methodisch identisch** mit dem
  Walk-Forward-/Out-of-Sample-Prinzip, das `algo/validate.py` bereits umsetzt (siehe
  [[Vier-Stufen-Strategieentwicklung (Masters)]], [[Cross Validation vs. Walk-Forward (Masters)]]).
  Diese Lecture liefert keine neue Methodik, sondern eine unabhängige Bestätigung der bereits
  gültigen Projektstandards — kein neuer Code nötig, siehe
  [[Quant-Finance-Formeln für den MNQ-Algo (laufend)]].
- Reinforcement Learning für Hedging ist für `algo/` aktuell nicht direkt anwendbar (kein
  Optionsportfolio, keine Delta-Hedging-Notwendigkeit), aber konzeptionell interessant für eine
  spätere Exit-/Trade-Management-Erweiterung (mehrstufige Entscheidung: halten, Partial, Stop
  nachziehen — analog zur Hedging-Entscheidungssequenz).
- Neuronale Netze als Signalgeber: laut [[Reinforcement Learning für Handel — Grenzen (Starke)]]
  bereits als grundsätzlich riskant für dieses Projekt eingeordnet (Rauschen statt Struktur) — die
  hier gezeigten ANN-Erfolge betreffen Preismodell-Approximation (bekannte, glatte Zielfunktion),
  nicht Signal-Vorhersage in verrauschten Marktdaten. Kein Widerspruch, sondern unterschiedliche
  Anwendungsklasse.
