---
tags: [concept, algo-methodology, machine-learning, reinforcement-learning, referenz]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[2019-09-05 - Reinforcement Learning for Trading (Tom Starke) (Source)|Reinforcement Learning for Trading — Practical Examples and Lessons Learned (Source)]]", "[[2022-07-05 - Two Sigma - Machine Learning Models of Financial Data (Source)|Two Sigma — Machine Learning Models of Financial Data (Source)]]"]
---

# Reinforcement Learning für Handel — Grenzen (Starke)

Warum Reinforcement Learning als **Signalgeber** im Handel bislang nicht trägt — und wo es
trotzdem funktioniert. Aus dem Praktikerbericht von Dr. Tom Starke
([[2019-09-05 - Reinforcement Learning for Trading (Tom Starke) (Source)|Reinforcement Learning for Trading — Practical Examples and Lessons Learned (Source)]]),
ergänzt um das institutionelle Gegenbeispiel von Two Sigma.

## Die Anziehungskraft

RL verspricht, was jeden Systemhändler reizt: Man gibt dem Verfahren **keine Strategie** vor. Es
probiert, lernt aus der Rückmeldung und entwickelt sein eigenes Regelwerk. Starke formuliert es
als das, was jeder hofft: *„I don't even have to do the research anymore, the machine does it all
for me."*

## Warum es an echten Kursdaten scheitert

| Problem | Ausprägung |
|---|---|
| **Rauschen** | *„LSTMs and all these other fancy machine learning tools are really not designed to deal with a lot of noise. Image recognition doesn't have a lot of noise."* Bilderkennung hat klare Merkmale, Kursreihen nicht |
| **Lokale Optima** | Das System bleibt in Zwischenlösungen hängen, läuft eine Weile gut, hört dann auf |
| **Nicht reproduzierbar** | Ergebnisse schwanken zwischen Läufen so stark, dass sie kaum wiederholbar sind |
| **Stichprobenhunger** | RL braucht sehr viele Beispiele — bei einem Konto mit wenigen Trades pro Woche unerreichbar |
| **Entartende Belohnung** | Reine P&L als Belohnung führt auf steigenden Märkten schlicht zu Kaufen-und-Halten |
| **Regeln ändern sich** | Der Markt ist kein Spiel mit festen Regeln |

## Der konstruktive Befund

Auf einer **geglätteten** Reihe (5-Perioden-Durchschnitt) erkennt derselbe Lerner die Struktur und
liefert brauchbare Ergebnisse. Starkes Schluss: der Kursreihe erst eine **geometrische Bedeutung**
geben, dann das Verfahren darauf ansetzen — nicht auf rohes Rauschen.

> ⚠️ **Einwand, den Starke selbst nicht macht.** Ein gleitender Durchschnitt ist
> konstruktionsbedingt autokorreliert und damit zwangsläufig leichter vorhersagbar. Gehandelt wird
> aber zum **echten** Kurs, nicht zum geglätteten. Ein Ergebnis auf der geglätteten Reihe ist
> deshalb nur belastbar, wenn die Abrechnung zu den tatsächlichen Kursen erfolgt — sonst ist es
> eine Selbsttäuschung derselben Familie wie Lookahead-Bias. Der **Grundgedanke** bleibt richtig:
> Struktur extrahieren statt Rohdaten füttern.

Für dieses Projekt ist genau dieser Grundgedanke bereits umgesetzt: Die Detektoren aus
`tools/analyze_ohlc.py` (FVG, Sweep, Strukturbruch, Displacement, Macro-Fenster) **sind** die
Strukturextraktion. Ein Lernverfahren müsste hier auf diesen Merkmalen aufsetzen, nie auf rohem
OHLC.

## Wo RL nachweislich funktioniert: Ausführung, nicht Richtung

Das institutionelle Gegenbeispiel von Two Sigma nutzt RL **nicht** zur Richtungsvorhersage, sondern
zur Frage, **wann** eine bereits beschlossene Order abgesetzt wird. Ergebnis über rund 100 Aktien:
durchgehend positive Kostenersparnis gegenüber der sofortigen Marktorder, gemessen in Basispunkten.

Der Unterschied ist grundsätzlich: Bei der Ausführung ist die Zielgröße sauber definiert
(erzielter Preis gegen Referenzpreis), die Rückmeldung dicht und der Zeithorizont Sekunden statt
Tage. Genau die Bedingungen, unter denen RL funktioniert.

**Für dieses Projekt trotzdem nicht umsetzbar:** Das Verfahren braucht Orderbuchdaten Ereignis für
Ereignis. Die stehen einem Privatkonto bei IBKR nicht zur Verfügung.

## Nebenbefunde, die unabhängig wertvoll sind

- **Zeitmerkmale wirken.** Tageszeit, Wochentag und Jahreszeit als Eingangsgrößen verbessern das
  Ergebnis laut Starke spürbar — unabhängige Bestätigung für [[ICT Killzones]] und „Time before
  Price".
- **Erst Kunstdaten, dann Markt.** Sinuskurven, Trends, dann mit Rauschen, dann autokorrelierte
  Reihen, erst danach echte Kurse. Auf einer Reihe, die überwiegend einem Zufallspfad gleicht,
  lässt sich sonst gar nicht feststellen, ob das Verfahren funktioniert. Diese Methodik ist auf
  **jeden** Detektor in `algo/` übertragbar, nicht nur auf ML.
- **Einfacher schlägt komplexer.** *„Simple neural nets are just as good as anything."* Für
  überwachtes Lernen nennt er Support Vector Machines als das bei ihm über Jahre
  zuverlässigste Verfahren.

## Verwandt

- [[Machine Learning für den Algo — Bewertung (laufend)]]
- [[Meta-Labeling (López de Prado)]] — umgeht das Kernproblem, indem die Richtung aus dem Regelwerk kommt
- [[Universal Model & Instrument-Pooling]]
- [[Monte Carlo Permutation Test (MCPT)]] — Kunstdaten-Prüfung in strenger Form
