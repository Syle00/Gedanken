---
tags: [concept, algo-methodology, optimierung]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[Testing and Tuning Market Trading Systems (Source)]]"]
---

# Differential Evolution & Parameter-Sensitivität

Wie man die Parameter eines Handelssystems optimiert — und, wichtiger, wie man **danach**
erkennt, ob das Optimum stabil oder ein Zufallstreffer ist. Aus
[[Testing and Tuning Market Trading Systems (Source)]] (Kap. 3 und 4).

## Differential Evolution

Der Zielkonflikt jeder Optimierung: Hill-Climbing ist schnell, landet aber auf dem
nächstbesten Hügel; global suchende Verfahren finden den richtigen Hügel, sind aber langsam.
Differential Evolution ist der Kompromiss.

Anders als bei üblicher Fortpflanzung braucht ein Kind **vier** Eltern: `Parent1`
(deterministisch, der laufende Index) sowie `Parent2`, `Differential1`, `Differential2`
(zufällig, alle vier verschieden).

```
Mutation:  trial[j] = parent2[j] + konstante · (diff1[j] − diff2[j])
Crossover: pro Variable mit Wahrscheinlichkeit pcross den mutierten Wert nehmen,
           sonst den Wert von parent1
Selektion: Kind gegen parent1 antreten lassen, der Bessere kommt in die nächste Generation
```

Die entscheidende Eigenschaft: **die Störung skaliert sich selbst an die Problemgeometrie.**
Liegt das Optimum auf einem schmalen Grat, verteilt sich die Population entlang des Grats und
staucht sich quer dazu — die Differenzen zweier zufälliger Individuen sind dann automatisch groß
längs und klein quer zum Grat. Genau das, was man will.

Masters' Anpassungen gegenüber dem Lehrbuchverfahren:

- **Overinitialization.** Statt `popsize` Startindividuen erzeugt er etwa `2 × popsize` und
  ersetzt fortlaufend das jeweils schlechteste. Bessere Startpopulation, schnellere Konvergenz,
  höhere Chance, das globale Optimum überhaupt im Einzugsbereich zu haben. Der Grenznutzen
  erschöpft sich aber schnell.
- **Gelegentliches Hill-Climbing** (`pclimb`). Stochastische Verfahren kommen schnell in die Nähe
  des Optimums, treffen es aber nie exakt. Deshalb wird pro Generation **ein** Individuum (mit
  Vorzug für das beste) in **einer** Variablen exakt optimiert. Da immer nur ein einzelnes
  Individuum betroffen ist, bleiben die Einzugsbereiche der übrigen unangetastet, die Globalität
  geht also nicht verloren. `pclimb = 0` schaltet ab, ein winziger Wert tunt nur das Beste,
  ~0,2 tunt gelegentlich auch andere.
- **Mindest-Trade-Zahl.** Kandidaten unterhalb einer Mindestanzahl Trades werden verworfen.
  Scheitert das 500 Mal in Folge, senkt der Algorithmus die Anforderung um 10 % — deshalb muss
  man am Ende **nachprüfen, wie viele Trades das Siegersystem tatsächlich hat**.
- **Konvergenz** über `max_bad_gen`: so viele Generationen ohne Verbesserung des Besten. Großzügig
  ansetzen (50+), weil es nach längeren Durststrecken durchaus wieder anspringt.

Faustwerte: `pcross` klein (0,1–0,5), Populationsgröße mehrere hundert, wenn die Folgeanalysen
(unten) genutzt werden sollen.

> Hinweis zur Kombination: Für [[CSCV (Combinatorially Symmetric Cross Validation)]] ist
> Differential Evolution **unzulässig** — dort sind nur Grid Search oder unabhängige
> Zufallsparameter erlaubt. Und für die billige Bias-Schätzung
> ([[Training Bias & Selection Bias]]) darf nur die Initialpopulation verwendet werden, keine
> Kinder.

In Python entspricht das `scipy.optimize.differential_evolution`; Overinitialization und der
Hill-Climbing-Schritt fehlen dort, `polish=True` erfüllt einen ähnlichen Zweck am Ende.

## Parameter-Sensitivitätskurven

Der Abschnitt, den Masters ausdrücklich als **Pflicht** bezeichnet („minimal due diligence"),
während er die Hessian-Analyse (unten) als nettes Beiwerk einstuft.

Verfahren: alle Parameter auf ihre Optimalwerte setzen, dann **einen** davon über seinen ganzen
Bereich variieren und die Performance plotten. Für jeden Parameter einzeln.

Was man sehen will: einen **breiten, glatten Gipfel** um den Optimalwert, mit sanftem Abfall nach
außen. Was ein Warnsignal ist:

- **Schmale Spitze** → instabil. Wenn sich die Marktbedingungen ändern, fällt der einst optimale
  Wert über die Klippe.
- **Mehrere getrennte Gipfel in der Nähe des Optimums** → die Performance stammt vermutlich daraus,
  dass zufällig ein paar gute Trades erwischt bzw. ein paar schlechte vermieden wurden. Kleine
  Parameterverschiebungen fangen sie mal ein, mal nicht. Glück, nicht Können.
- Zappeln **weit weg** vom Optimum ist unbedenklich.

## Hessian-Analyse (PARAMCOR)

Aus der Endpopulation der Differential Evolution lassen sich fast gratis Parameterbeziehungen
ablesen: eine quadratische Fläche per Kleinste-Quadrate (SVD) an die Punkte nahe dem Optimum
fitten, daraus die Hesse-Matrix bilden, invertieren.

- **Diagonale** → relative Variation je Parameter (auf 1,0 normiert): wie weit darf sich der
  Parameter bewegen, ohne dass die Performance nennenswert leidet. Groß = unempfindlich.
- **Nebendiagonalen** → Korrelationen: negative Korrelation heißt, dass sich eine Änderung des
  einen Parameters durch eine gegenläufige des anderen ausgleichen lässt.
- **Eigenvektoren** → Richtung maximaler und minimaler Empfindlichkeit im Parameterraum.

Wichtige Voraussetzung: die Parameter müssen **kommensurabel skaliert** sein, weil euklidische
Abstände zum Optimum verwendet werden.

**Der aufschlussreichste Fehlerfall:** Ist ein Diagonalelement null oder negativ, ist man in
diesem Parameter nicht in einem Minimum. Masters' Deutung ist nicht „der Algorithmus ist
schlecht", sondern: *„nonpositive diagonals are a red flag that the parameterization of the
trading system is unstable"* — die Performance springt dann wild statt glatt zu verlaufen, das
System fängt mehr oder minder zufällig große Gewinne und Verluste ein. Reaktion: nicht das
Verfahren wechseln, sondern **Sensitivitätskurven ansehen und das System überdenken.**

Beispiel DEV_MA auf OEX (4 Parameter: langer Lookback, kurzer Lookback in % des langen, Short-
und Long-Schwelle): Gesamt-Log-Return 2,671, geschätzter Trainings-Bias 0,3221, erwarteter Return
also 2,3489. Die Long-Schwelle dominiert die Empfindlichkeit vollständig; kurzer Lookback und
Short-Schwelle sind am unempfindlichsten und untereinander mit −0,679 korreliert (Änderungen des
einen lassen sich durch gegenläufige des anderen ausgleichen — vom Autor unerklärt). Die Richtung
minimaler Empfindlichkeit bestätigt genau diese Korrelation.

## Bezug zu diesem Projekt

`algo/backtest_walkforward.py` rechnet bereits eine Parameter-Sensitivitäts-Tabelle für den
Stop-Puffer — das ist genau dieses Verfahren, allerdings nur für **einen** Parameter und ohne
Bewertung der Kurvenform. Die Kriterien oben (breiter glatter Gipfel vs. schmale Spitze vs.
mehrere Gipfel) sind das, was in den Berichten bisher fehlt.

Für die Optimierung selbst nutzt `algo/` bisher Grid Search. Das ist bei wenigen Parametern
richtig und bleibt zudem die Voraussetzung für
[[CSCV (Combinatorially Symmetric Cross Validation)]] — Differential Evolution würde erst
interessant, wenn die Regelschicht so viele Parameter bekommt, dass ein Grid nicht mehr durchläuft.
