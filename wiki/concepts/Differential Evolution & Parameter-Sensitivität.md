---
tags: [concept, algo-methodology, optimierung, referenz]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[Testing and Tuning Market Trading Systems (Source)]]"]
---

# Differential Evolution & Parameter-Sensitivität

Wie man die Parameter eines Handelssystems optimiert — und, wichtiger, wie man **danach** erkennt,
ob das Optimum stabil oder ein Zufallstreffer ist. Aus
[[Testing and Tuning Market Trading Systems (Source)]] (Kap. 3 und 4, Programme `DIFF_EV.CPP`,
`PARAMCOR.CPP`, `SENSITIV.CPP`, `DEV_MA.CPP`).

## Teil 1 — Differential Evolution

Der Zielkonflikt jeder Optimierung: Hill-Climbing ist schnell, landet aber auf dem nächstbesten
Hügel; global suchende Verfahren finden den richtigen Hügel, sind aber langsam. Differential
Evolution ist der Kompromiss.

### Der Kernmechanismus

Anders als bei üblicher Fortpflanzung braucht ein Kind **vier** Eltern: `Parent1` (deterministisch,
der laufende Index) sowie `Parent2`, `Differential1`, `Differential2` (zufällig gezogen, alle vier
paarweise verschieden).

```
Mutation:   mutiert[j] = parent2[j] + mutate_dev · (diff1[j] − diff2[j])
Crossover:  pro Variable j mit Wahrscheinlichkeit pcross den mutierten Wert nehmen,
            sonst parent1[j] kopieren
Selektion:  Kind gegen parent1 antreten lassen — der Bessere kommt in die naechste Generation
```

Die entscheidende Eigenschaft: **die Störung skaliert sich selbst an die Problemgeometrie.** Liegt
das Optimum auf einem schmalen Grat, verteilt sich die Population entlang des Grats und staucht
sich quer dazu. Die Differenz zweier zufälliger Individuen ist dann automatisch groß längs und
klein quer zum Grat — exakt die gewünschte Schrittweite in jeder Richtung.

### Aufrufsignatur und Praxiswerte

```
diff_ev(criter, nvars, nints, popsize, overinit, mintrades, max_evals,
        max_bad_gen, mutate_dev, pcross, pclimb, low_bounds, high_bounds,
        params, print_progress, stoc_bias)
```

| Parameter | Bedeutung | Wert im `DEV_MA`-Beispiel | Empfehlung im Text |
|---|---|---|---|
| `nvars` / `nints` | Anzahl Parameter / davon Ganzzahlen (**müssen zuerst stehen**) | 4 / 1 | — |
| `popsize` | Populationsgröße | 100 | mehrere hundert, wenn Teil 2/3 genutzt wird |
| `overinit` | Überinitialisierung | **10.000** | ≈ `popsize`; hier bewusst riesig für StocBias |
| `mintrades` | Mindestzahl Trades je Kandidat | 20 | — |
| `max_evals` | Notbremse bei der Initialpopulation | 10.000.000 | groß; **darf nie greifen** |
| `max_bad_gen` | Generationen ohne Verbesserung = Konvergenz | 300 | „50 or even more" |
| `mutate_dev` | Faktor der Differenz-Störung | 0,2 | meist < 1 |
| `pcross` | Crossover-Wahrscheinlichkeit | 0,2 | 0,1 … 0,5 |
| `pclimb` | Wahrscheinlichkeit eines Hill-Climbing-Schritts | 0,3 | 0 / winzig / ~0,2 (siehe unten) |

Der letzte Rückgabeplatz in `params` (Länge `nvars+1`) enthält den Kriteriumswert des Optimums.

### Der Ablauf

```
# --- Phase 1: Initialpopulation (popsize + overinit Kandidaten) ---
for ind in 0 … popsize+overinit-1:
    zufaelligen Parametervektor erzeugen
        Ganzzahl j:  low[j] + int( unifrand() · (high[j] − low[j] + 1) )
        Real     j:  low[j] + unifrand() · (high[j] − low[j])
    value = criter(vektor, mintrades)
    if value <= 0:                       # wertlos oder zu wenige Trades
        ind -= 1                         # Kandidat verwerfen und neu ziehen
        if ++failures >= 500:            # 500 Fehlschlaege IN FOLGE
            failures  = 0
            mintrades = max(1, mintrades · 9 // 10)     # Anforderung senken
        if n_evals > max_evals: NOTAUSSTIEG
        continue
    failures = 0
    if ind >= popsize:                   # Ueberinitialisierungsphase
        schlechtestes Individuum der Population suchen
        if value > schlechtestes: ersetzen

# --- Phase 2: Generationen ---
for generation = 1, 2, …:
    improved = false
    for ind in 0 … popsize-1:
        parent1 = old_gen[ind]
        parent2, diff1, diff2 = drei verschiedene Zufallsindizes ≠ ind
        # Mutation + Crossover in EINER Schleife, rotierend ab zufaelligem Startindex j:
        for i = nvars-1 … 0:
            if (i == 0 and noch nichts mutiert) or unifrand() < pcross:
                kind[j] = parent2[j] + mutate_dev · (diff1[j] − diff2[j])
            else:
                kind[j] = parent1[j]
            j = (j + 1) % nvars
        ensure_legal(kind)
        value = criter(kind, mintrades)
        new_gen[ind] = kind if value > parent1.value else parent1
        optional: Hill-Climbing-Schritt (siehe unten)
    if not improved:
        if ++bad_generations > max_bad_gen: FERTIG
    else:
        bad_generations = 0
    old_gen, new_gen = new_gen, old_gen
return bestes Individuum
```

Zwei Details, die leicht übersehen werden: der **zufällige Startindex** `j` in der Crossover-Schleife
sorgt dafür, dass die erzwungene Mindestmutation („mindestens eine Variable muss mutiert sein")
nicht immer dieselbe Variable trifft. Und `ensure_legal` ist Pflicht, weil die Mutation Parameter
regelmäßig aus ihren Grenzen schiebt.

### Masters' Erweiterungen gegenüber dem Lehrbuchverfahren

**Overinitialization.** Statt `popsize` Startindividuen erzeugt er `popsize + overinit` und ersetzt
fortlaufend das jeweils schlechteste. Bessere Startpopulation, schnellere Konvergenz, höhere
Chance, das globale Optimum im Einzugsbereich zu haben. Der Grenznutzen erschöpft sich aber
schnell: sobald das schlechteste Populationsmitglied besser ist als die meisten Neuziehungen, ist
weiteres Überinitialisieren Verschwendung. `overinit = 0` liefert das klassische Verfahren.

**Automatische Absenkung von `mintrades`.** Nach 500 Fehlschlägen **in Folge** wird die Anforderung
um 10 % gesenkt. Deshalb gilt: **am Ende nachprüfen, wie viele Trades das Siegersystem tatsächlich
hat.** Es braucht sehr viel Fehlschlag, um das auszulösen — wenn es auslöst, stimmt etwas nicht.

**Schwellenwert 0 für „wertlos".** Der Reject-Test lautet hart `value <= 0`. Wer ein Kriterium mit
anderem neutralen Punkt optimieren will (Profit Factor: 1), muss es transformieren — Masters'
Vorschlag: **den Logarithmus des Profit Factors maximieren.**

**Gelegentliches Hill-Climbing** (`pclimb`). Stochastische Verfahren kommen schnell in die Nähe des
Optimums, treffen es aber nie exakt, weil sie keine lokale Information nutzen. Deshalb wird pro
Generation **ein** Individuum in **einer** Variablen exakt optimiert:

```
if pclimb > 0 and ( (ind == ibest and n_tweaked < nvars) or unifrand() < pclimb ):
    if ind == ibest:                       # einmal pro Generation das Beste
        n_tweaked += 1
        k = generation % nvars             # rotiert durch alle Variablen
    else:
        k = zufaellige Variable
```

`n_tweaked` wird bei jeder Verbesserung des Grand Best zurückgesetzt; die Bedingung
`n_tweaked < nvars` verhindert, dass ein unverändert bleibendes Bestes endlos nachpoliert wird.
Die Rotation über `generation % nvars` vermeidet Doppelarbeit, weil dasselbe Individuum oft über
mehrere Generationen das beste bleibt.

Da immer nur **ein einzelnes** Individuum betroffen ist, bleiben die Einzugsbereiche der übrigen
unangetastet — die Globalität geht also nicht verloren.

| `pclimb` | Wirkung |
|---|---|
| 0 | klassisches Verfahren, kein Hill-Climbing |
| 1e-5 | nur das jeweils Beste wird gelegentlich nachgezogen — stark verbesserte Endkonvergenz |
| ~0,2 | zusätzlich gelegentlich zufällige andere Individuen |
| größer | selten lohnend; teuer, und die Globalität kann leiden |

**Hill-Climbing bei Ganzzahlen** — einfache Nachbarschaftssuche, kein globaler Scan:

```
ibase = aktueller Wert
aufwaerts laufen, solange sich das Kriterium verbessert; bei Verschlechterung abbrechen
war das erfolglos: von ibase abwaerts laufen, gleiche Logik
kein Erfolg → auf ibase zuruecksetzen
```

(Flache Zwischenbereiche mit späterer Verbesserung werden bewusst nicht durchsucht — zugunsten
der Geschwindigkeit.)

**Hill-Climbing bei Realparametern** — zweistufig:

```
1) grobe globale Suche in der NAEHE des aktuellen Werts:
      lower = base − 0.1 · (high − low)
      upper = base + 0.1 · (high − low)
      an den Raendern auf ein 0.2-Fenster innerhalb der Grenzen verschieben
      glob_max(lower, upper, 7 Punkte)  →  Tripel (x1,x2,x3) mit Maximum in der Mitte
2) Verfeinerung mit Brents Verfahren:
      brentmax(maxits=5, tol=1e-8, eps=1e-4)
3) ensure_legal(), Kriterium neu berechnen
   verbessert?  uebernehmen : auf den alten Wert zuruecksetzen
```

**`ensure_legal`** — rundet Ganzzahlparameter (Mutation erzeugt Kommawerte!), erzwingt die Grenzen
und liefert eine Strafe zurück, die bei der Realparameter-Optimierung vom Kriterium abgezogen wird:

```
Ganzzahl:  params[i] ≥ 0 →  int(params[i] + 0.5)
           params[i] < 0 → −int(0.5 − params[i])       # korrektes Runden in beide Richtungen
zu gross:  penalty += 1e10 · (params[i] − high[i]) ;  params[i] = high[i]
zu klein:  penalty += 1e10 · (low[i]  − params[i]) ;  params[i] = low[i]
```

Der Faktor `1e10` macht die Strafe so steil, dass `brentmax` sofort wieder ins zulässige Gebiet
zurückgetrieben wird.

**Nuisance-Parameter über Statics.** Damit `diff_ev` generisch bleibt, kapselt ein Wrapper die
systemspezifischen Dinge (Preisreihe, Lookback-Maximum) in statischen Variablen und mappt den
generischen `params`-Vektor auf die benannten Systemparameter. Sauberer Trennungspunkt zwischen
Optimierer und Handelssystem.

> **Verträglichkeit mit anderen Verfahren:** Für
> [[CSCV (Combinatorially Symmetric Cross Validation)]] ist Differential Evolution **unzulässig** —
> dort sind nur Grid Search oder unabhängige Zufallsparameter erlaubt. Und für die billige
> Bias-Schätzung ([[Training Bias & Selection Bias]]) darf **nur die Initialpopulation** verwendet
> werden, keine Kinder — deshalb im Beispiel `overinit = 10.000`.

In Python entspricht das Verfahren `scipy.optimize.differential_evolution`; Overinitialization und
der rotierende Hill-Climbing-Schritt fehlen dort, `polish=True` (Nelder-Mead/L-BFGS am Ende)
erfüllt einen ähnlichen Zweck.

## Teil 2 — Parameter-Sensitivitätskurven

Der Abschnitt, den Masters ausdrücklich als **Pflicht** bezeichnet („minimal due diligence"),
während er Teil 3 als nettes Beiwerk einstuft.

Verfahren: alle Parameter auf ihre Optimalwerte setzen, dann **einen** davon über seinen ganzen
Bereich in `npoints` Schritten variieren und die Performance plotten. Für jeden Parameter einzeln.

```
sensitivity(criter, nvars, nints, npoints, nres, mintrades, best, low_bounds, high_bounds)
   npoints = 30   Auswertungspunkte je Parameter   (DEV_MA-Beispiel)
   nres    = 80   Balkenbreite des Text-Histogramms

je Parameter ivar:
    params = Kopie von best
    label_frac = (high − low) / (npoints − 1)                    # real
               = (high − low + 0.99999999) / (npoints − 1)       # ganzzahlig
    fuer jeden Punkt:  params[ivar] setzen, vals[p] = criter(params, mintrades)
    hist_frac = (nres + 0.9999999) / max(vals)
    Balkenlaenge = int(vals[p] · hist_frac)
```

**Was man sehen will:** einen **breiten, glatten Gipfel** um den Optimalwert mit sanftem Abfall
nach außen. Das bedeutet: das System reagiert gutmütig auf Störungen, ist immun gegen Glücks-
schwankungen und bleibt vermutlich eine Weile stabil.

**Warnsignale:**

| Bild | Deutung |
|---|---|
| **schmale Spitze** | instabil — ändern sich die Marktbedingungen, fällt der einst optimale Wert über die Klippe |
| **mehrere getrennte Gipfel nahe dem Optimum** | die Performance stammt daraus, dass zufällig ein paar gute Trades erwischt bzw. schlechte vermieden wurden; kleine Verschiebungen fangen sie mal ein, mal nicht → **Glück, nicht Können** |
| Zappeln **weit weg** vom Optimum | unbedenklich |

## Teil 3 — Hessian-Analyse (PARAMCOR)

Aus der **Endpopulation** der Differential Evolution (nicht der Initialpopulation — hier will man
alle Punkte nahe am Optimum) lassen sich fast gratis Parameterbeziehungen ablesen.

```
ncoefs  = nparams                        # lineare Terme
        + nparams·(nparams+1)/2          # quadratische Terme
        + 1                              # Konstante
nc_kept = int(1.5 · ncoefs)              # so viele Individuen nahe am Optimum behalten
```

```
1) bestes Individuum finden
2) euklidischen Abstand jedes Individuums zum Besten berechnen, aufsteigend sortieren,
   die nc_kept naechstgelegenen behalten
3) quadratische Flaeche per Singulaerwertzerlegung anpassen (Designmatrix zentriert auf das Beste,
   backsub-Toleranz 1e-10) — dabei das VORZEICHEN der Performance drehen
   (Maximierung → Minimierung, wie bei negativer Log-Likelihood)
4) Hesse-Matrix aus den quadratischen Koeffizienten:
       Diagonale     = 2 · Koeffizient      (zweite Ableitung)
       Nebendiagonal = Koeffizient          (symmetrisch kopieren)
5) Diagonalelemente < 1e-10 → ganze Zeile und Spalte auf null (Parameter ausschliessen)
6) Nebendiagonalen begrenzen: |h[j,k]| ≤ 0.99999 · sqrt(h[j,j] · h[k,k])
7) Eigenwerte/-vektoren, verallgemeinerte Inverse ueber Eigenwerte > 1e-8
8) ausgeben:
      Variation  = sqrt(diag(H⁻¹)), auf Maximum 1,0 normiert
      Korrelation = H⁻¹[i,k] / (sqrt(H⁻¹[i,i]) · sqrt(H⁻¹[k,k])), auf [−1,1] geklemmt
      Eigenvektor zum groessten Eigenwert = Richtung MAXIMALER Empfindlichkeit
      Eigenvektor zum kleinsten positiven  = Richtung MINIMALER Empfindlichkeit
```

**Interpretation:**

- **Diagonale (Variation):** wie weit darf sich der Parameter bewegen, ohne dass die Performance
  nennenswert leidet. Groß = unempfindlich.
- **Nebendiagonalen (Korrelation):** negative Korrelation heißt, dass sich eine Änderung des einen
  Parameters durch eine gegenläufige des anderen ausgleichen lässt.
- **Eigenvektoren:** Richtungen im Parameterraum, in denen die Performance am stärksten bzw. am
  wenigsten reagiert. Das Vorzeichen ist bedeutungslos — es ist eine Richtung.

**Zwei harte Voraussetzungen:**

1. Die Parameter müssen **kommensurabel skaliert** sein, weil euklidische Abstände verwendet
   werden. Im `DEV_MA`-Beispiel wird deshalb der kurze Lookback als *Prozent* des langen und die
   Schwellen als *10.000-faches* des tatsächlichen Werts geführt — sonst wären die Skalen so
   verschieden, dass PARAMCOR wertlos würde.
2. Das Verfahren setzt voraus, dass man wirklich in einem Optimum sitzt.

**Der aufschlussreichste Fehlerfall:** Ist ein Diagonalelement null oder negativ, sitzt man in
diesem Parameter **nicht** in einem Minimum. Masters' Deutung ist ausdrücklich *nicht* „der
Algorithmus taugt nichts":

> *„Nonpositive diagonals are a red flag that the parameterization of the trading system is
> unstable."*

Die Performance springt dann wild statt glatt — das System fängt mehr oder minder zufällig große
Gewinne und Verluste ein. Mögliche Ursachen: echtes lokales, aber nicht globales Optimum; oder
die Kleinste-Quadrate-Fläche erstreckt sich über einen zu großen Bereich und beschreibt kein
lokales Verhalten mehr. **Reaktion: nicht das Verfahren wechseln, sondern Sensitivitätskurven
ansehen und das System überdenken.**

Daraus folgt Masters' allgemeineres Kriterium: „lokal" soll so weit wie möglich über die
unmittelbare Umgebung hinausreichen. Verhält sich die Kurve direkt am Optimum anders als ein
Stück daneben, ist das System gefährlich.

## Referenzlauf DEV_MA auf OEX

System: thresholded MA-Crossover mit vier Parametern — langer Lookback (ganzzahlig), kurzer
Lookback in **Prozent** des langen, Short-Schwelle × 10.000, Long-Schwelle × 10.000. Long, wenn
`kurzer_MA / langer_MA − 1 > long_thresh`; short, wenn `< −short_thresh`; sonst neutral. Handel auf
Log-Preisen, Rendite = `x[i+1] − x[i]`. Wichtig: **alle Lookbacks starten am selben Bar**
(`max_lookback − 1`), damit die Läufe vergleichbar bleiben.

| Größe | Wert |
|---|---|
| Gesamt-Log-Return (optimiert) | 2,6710 |
| geschätzter Trainings-Bias (StocBias) | 0,3221 |
| erwarteter Return | **2,3489** |

PARAMCOR-Befunde:

- Die **Long-Schwelle dominiert die Empfindlichkeit vollständig** — winzige Änderungen haben
  extreme Wirkung. Die Richtung maximaler Empfindlichkeit besteht fast nur aus ihr.
- Kurzer Lookback und Short-Schwelle sind am unempfindlichsten, der lange Lookback nur wenig
  empfindlicher.
- **Korrelation −0,679** zwischen kurzem Lookback und Short-Schwelle: Änderungen des einen lassen
  sich durch gegenläufige des anderen ausgleichen. Masters: „I have no explanation for this
  unexpected phenomenon."
- Die Richtung **minimaler** Empfindlichkeit bestätigt genau diese Korrelation — kurzer Lookback
  hoch und Short-Schwelle fast gleich stark runter ist die Bewegung, die am wenigsten bewirkt.
- Die Sensitivitätskurven bestätigen die Zahlen: Parameter 3 (Short-Schwelle) am flachsten,
  Parameter 4 (Long-Schwelle) am steilsten.

## Bezug zu diesem Projekt

`algo/backtest_walkforward.py` rechnet bereits eine Sensitivitätstabelle für den Stop-Puffer — das
ist genau Teil 2, aber nur für **einen** Parameter und ohne Bewertung der Kurvenform. Die
Kriterien oben (breiter glatter Gipfel vs. schmale Spitze vs. mehrere Gipfel) sind das, was in den
Berichten bisher fehlt.

Für die Optimierung selbst nutzt `algo/` Grid Search. Das ist bei wenigen Parametern richtig und
bleibt Voraussetzung für [[CSCV (Combinatorially Symmetric Cross Validation)]]. Differential
Evolution würde erst interessant, wenn die Regelschicht so viele Parameter bekommt, dass ein Grid
nicht mehr durchläuft — und dann wäre der PARAMCOR-Teil ein billiges Nebenprodukt.

**Sofort übertragbar, unabhängig vom Optimierer:** die Kommensurabilitäts-Regel. Wer Stop-Puffer
in Prozent, Zeitfenster in Minuten und Zielabstände in Punkten mischt, bekommt aus jeder
abstandsbasierten Analyse Unsinn heraus.
