---
tags: [concept, quant-finance, risikomanagement, behavioral-finance, yale-econ252]
created: 2026-08-12
updated: 2026-08-12
sources: ["[[2012-04-05 - Yale Econ 252 Lecture 11 - Behavioral Finance and the Role of Psychology (Source)]]"]
---

# Behavioral Finance (Prospect Theory & Kognitive Verzerrungen, Yale Econ 252)

Shillers Überblicksvorlesung zu Behavioral Finance. Ergänzt die bestehenden ICT-Wiki-Seiten zu
Retail-Fallen (z. B. [[Market Maker Trap - False Breakout]],
[[Momentum-Divergenz als Retail-Falle (Divergence Phantoms)]]) um eine akademisch fundierte
Taxonomie der zugrunde liegenden psychologischen Mechanismen.

## Prospect Theory (Kahneman & Tversky)

- **Wertfunktion**: konkav für Gewinne (abnehmender Grenznutzen), konvex für Verluste, mit einem
  **Knick am Referenzpunkt** (meist das aktuelle Vermögen, aber manipulierbar durch "Framing").
  Konsequenz: kleine Verluste werden überproportional schmerzhaft empfunden, kleine Gewinne
  unterproportional erfreulich — Menschen sind "gespookt" von kleinen Verlusten, obwohl diese
  gemessen am Lebenszeitvermögen irrelevant sind.
- **Gewichtungsfunktion für Wahrscheinlichkeiten**: sehr niedrige Wahrscheinlichkeiten werden auf 0
  abgerundet (ignoriert) oder massiv überschätzt, sehr hohe auf 1 aufgerundet — Menschen denken in
  effektiv drei Kategorien ("kann nicht passieren", "vielleicht", "wird passieren") statt in einem
  Kontinuum. Praxisbeispiel: Flugversicherungs-Automaten direkt vor dem Abflug nutzten gezielt
  Momente höchster subjektiver Risikowahrnehmung aus.

## Weitere dokumentierte Verzerrungen mit Finanzbezug

- **Overconfidence**: im Live-Experiment (90-%-Konfidenzintervalle für Weltbevölkerung,
  Erdmasse, Sprachanzahl) trafen die Teilnehmer die Zielquote von 90 % nur bei der vertrautesten
  Frage (Weltbevölkerung ≈ 80 %), bei unvertrauten Fragen brach die Trefferquote auf ~10 % ein —
  Menschen unterschätzen systematisch die Unsicherheit ihres eigenen Wissens.
- **Cognitive Dissonance**: Anleger mit schlecht laufenden Fonds blenden die schlechte Performance
  aktiv aus (Goetzmann-Studie); Finanzberater hinterfragen riskante Kundenportfolios selten (nur
  40 % rieten von übermäßiger Eigenaktien-Konzentration im Arbeitgeber ab — Mullainathan-Studie),
  weil sie Kunden nicht mit unangenehmen Wahrheiten verlieren wollen.
- **Anchoring**: irrelevante Zahlen (Glücksrad-Ergebnis) beeinflussen nachweislich spätere
  quantitative Schätzungen, obwohl die Testpersonen den Zusammenhang explizit abstreiten.
- **Representativeness Heuristic**: seltene Chartmuster (z. B. Kopf-Schulter) werden überproportional
  häufig "erkannt", weil sie im Gedächtnis salient sind — reale Basisrate meist deutlich niedriger
  als subjektiv wahrgenommen.
- **Herd Behavior / Collective Consciousness** (Durkheim): kollektive Meinungsbildung erzeugt
  Marktbewegungen, die individuell rational erscheinen, aggregiert aber Blasen/Crashes verursachen.

## Antisocial Personality Disorder (APD) als Marktfaktor

- DSM-IV-Schätzung: ~3 % der Männer, ~1 % der Frauen erfüllen APD-Kriterien (Mangel an Reue,
  häufiges Lügen, oberflächlicher Charme). Relevanz für Finanzmärkte: diese Personen sind gezielt
  in der Lage, Verzerrungen wie Prospect Theory oder Anchoring bei anderen auszunutzen — Shillers
  Gegenthese ist aber, dass Reputationsmechanismen (Adam Smiths "praise-worthiness"-Konzept) und
  Regulierung diese Ausbeutung in der Praxis begrenzen, siehe
  [[Finanzregulierung — Fünf Ebenen & Too-Big-To-Fail (Yale Econ 252)]].

## Bezug zu diesem Projekt

- Direkte Bestätigung der ICT-These, dass Retail-Verhalten strukturell ausnutzbar ist (z. B.
  [[Market Maker Trap - False Flag]], [[Trendline Phantoms (3 Drives Pattern)]]): die
  Representativeness Heuristic liefert die kognitionswissenschaftliche Erklärung dafür, warum
  Chartmuster wie Kopf-Schulter oder Trendlinien-Brüche überzeugend *aussehen*, obwohl ihre
  statistische Trefferquote (laut Shillers Random-Walk-Simulationen, siehe
  [[Efficient Markets Hypothesis & Random Walk (Yale Econ 252)]]) nicht signifikant über Zufall
  liegen muss.
- Die Overconfidence-Befunde sind eine Warnung für die eigene Backtest-Interpretation: die
  Tendenz, das erste plausible Muster für ausreichend zu halten, statt die Bandbreite möglicher
  Erklärungen (und damit die Konfidenzintervall-Breite) zu berücksichtigen — Ergänzung zu
  [[Konfidenzgrenzen für Renditen (t-Test, Bootstrap, BCa)]].
