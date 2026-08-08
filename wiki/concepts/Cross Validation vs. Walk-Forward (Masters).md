---
tags: [concept, algo-methodology, validation, walk-forward, referenz]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[Testing and Tuning Market Trading Systems (Source)]]"]
---

# Cross Validation vs. Walk-Forward (Masters)

Warum Cross Validation bei Marktdaten **nicht** die datensparsamere Variante von Walk-Forward ist,
sondern ein anderes Verfahren mit eigenen Verzerrungen. Aus
[[Testing and Tuning Market Trading Systems (Source)]] (Kap. 5, Programm `XvW.CPP`).

## Der Reiz und die Falle

Der Reiz: Walk-Forward verwirft in jedem Fold sämtliche Daten **nach** dem Testblock. CV nutzt sie
mit. Gerade in den frühen Folds, wo Walk-Forward kaum Historie hat, ist das ein echter Vorteil.

**Guard Buffer beidseitig.** Wie im Walk-Forward gilt bei Lookahead > 1:
`min(lookback, lookahead) − 1` Fälle streichen — hier aber **an beiden Rändern** des Testblocks,
also auch am Anfang des Trainingsteils, der *hinter* dem Testblock liegt. Herleitung identisch,
siehe [[Walk-Forward Guard Buffer & Varianz-Inflation]].

```
|<──── Training ────>|<─ omit ─>|<── OOS-Test ──>|<─ omit ─>|<──── Training ────>|
                      Guard                        Guard
```

## Drei Einwände

### 1. CV kann pessimistisch verzerrt sein

Jeder CV-Trainingssatz ist kleiner als der volle Datensatz, mit dem man das Produktivmodell
trainieren würde. Kleinere Trainingsmenge → ungenauere Parameter → schlechtere OOS-Leistung. CV
**unterschätzt** deshalb tendenziell, was das final trainierte Modell leisten wird.

(Das ist der weit verbreitete Irrglaube, den Masters explizit anspricht: „There is widespread
belief that cross validation produces an unbiased estimate of population performance." Auf den
ersten Blick plausibel — man testet immer auf getrennten Daten. Der Haken ist die *Größe* der
Trainingsmenge, nicht ihre Trennung.)

### 2. CV kann optimistisch verzerrt sein

Und zwar bei nichtstationären Daten — also praktisch immer im Markt. Die inneren Folds trainieren
auf Daten aus der **Zukunft** des Testblocks. Selbst wenn kein einzelner Fall geteilt wird, bekommt
der Trainingsalgorithmus Information über die künftige **Verteilung**.

Masters' Beispiel: die Volatilität steigt über die Historie stetig. Im Walk-Forward — und im
echten Leben — hat jeder Testblock höhere Volatilität als sein Trainingssatz, was problematisch
sein kann. In den inneren CV-Folds ist der Testblock von Trainingsdaten **eingeklammert**; das
Modell hat die Bandbreite also schon gesehen. Ein subtiler Future Leak ohne geteilte Fälle.

### 3. CV bildet die Realität nicht ab

Und damit fällt auch der Datenvorteil weg: die meisten Entwickler wählen ihr
Walk-Forward-Trainingsfenster ohnehin **genauso groß** wie das des späteren Produktivmodells —
eben weil sie nicht über zu viele Marktregime hinweg trainieren wollen. Dann hat CV keinen
Datenvorteil mehr, wohl aber die Verzerrungen aus (2).

Masters räumt dabei ein, dass Walk-Forward wegen der mageren frühen Folds **noch stärker**
pessimistisch verzerrt sein kann als CV — der Punkt ist nicht, dass Walk-Forward unverzerrt wäre,
sondern dass es die Realität abbildet.

> Fazit wörtlich: *„I cannot recommend cross validation analysis in trading system development,
> except in the most unusual special situations."*

## Der allgemeine CV-Algorithmus mit Guard Buffern

Die Umsetzung ist deutlich fummeliger als beim Walk-Forward, weil der Trainingssatz **zerfällt**:
ein Stück links vom Testblock, ein Stück rechts davon. Damit Training und Test trotzdem an
generische Routinen übergeben werden können, wird alles in **zusammenhängende Blöcke** kopiert.

```
istart = 0 ;  ncases_save = ncases

fuer jeden Fold:
    n_in_fold = (ncases − n_done) / (nfolds − ifold)     # gleich grosse Folds
    istop     = istart + n_in_fold

    WENN omit > 0:                       # mit Guard Buffer → zwei Arrays (SRC → DEST)
        SRC[istart : istop]  →  ans ENDE von DEST                   # der OOS-Block
        erster Fold:   SRC[istop+omit : ncases]  → Anfang von DEST
                       ncases −= n_in_fold + omit
        letzter Fold:  SRC[0 : istart−omit]      → Anfang von DEST
                       ncases −= n_in_fold + omit
        sonst:         SRC[0 : istart−omit]      → Anfang von DEST
                       SRC[istop+omit : ncases]  → direkt dahinter
                       ncases −= n_in_fold + 2·omit
    SONST:                               # omit == 0 → in place tauschen, ein Array reicht
        wenn nicht letzter Fold: Bloecke [istart:istop] mit den Endfaellen tauschen
        ncases −= n_in_fold

    TRAINIEREN auf den ersten ncases Faellen
    ncases = ncases_save                 # sofort zuruecksetzen
    TESTEN auf den letzten (istop − istart) Faellen

    wenn omit == 0 und nicht letzter Fold: Tausch rueckgaengig machen
    istart = istop ;  n_done += n_in_fold
```

Zwei Implementierungsdetails, die man sonst schmerzhaft lernt:

- **Innere Folds können auf einer Seite leer laufen.** Wählt der Nutzer sehr viele Folds (winzige
  Testblöcke), kann nach Abzug des Guard Buffers auf einer Seite **kein einziger** Trainingsfall
  übrig bleiben. Beide Kopierschritte brauchen deshalb eine Bedingung (`istart > omit` bzw.
  `ncases_save > istop + omit`).
- **`ncases` wird temporär reduziert** und muss unmittelbar nach dem Training zurückgesetzt
  werden, weil der Testteil wieder den vollen Datensatz adressiert.

Wer will, kann stattdessen die Grenzen direkt in Trainings- und Testcode einbauen — dann braucht
es aber hochgradig maßgeschneiderten Code, generische Bibliotheksroutinen scheiden aus.

## XvW: wie groß ist der Unterschied praktisch?

```
XvW nprices trend lookback lookahead ntrain ntest nfolds omit nreps seed
```

Lässt dasselbe System zweimal laufen (CV und Walk-Forward) und gibt beide mittleren OOS-Renditen
samt t-Score der Differenz aus. Anders als `OVERLAP` kann `XvW` auch Preisreihen mit einem
alle 50 Bars wechselnden **Trend** erzeugen — also mit echter, dosierbarer Vorhersagbarkeit.

Beispielzeile aus dem Buch:

```
Grand XVAL = 0.02249 (t=253.371)   WALK = 0.00558 (t=81.355)
StdDev = 0.00011   t = 150.768   rtail = 0.00000
```

CV liefert hier die **vierfache** mittlere Rendite von Walk-Forward, und die Differenz ist
hochsignifikant. Bei `trend = 0` (reiner Random Walk) sind erwartungsgemäß alle t-Scores
insignifikant.

Der t-Score der Differenz hängt stark von Lookback und Lookahead ab und in geringerem Maß von der
Foldzahl. Kernaussage:

> *„In nearly all practical situations, walkforward and cross validation analysis produce
> significantly different results, often wildly different."*

Die beiden Verfahren sind also **nicht austauschbar** — man kann nicht CV rechnen und das Ergebnis
als Näherung für Walk-Forward lesen.

## Die eine Ausnahme: CV innerhalb von Walk-Forward

CV ist dort vertretbar, wo die drei Einwände wenig wiegen: bei **Modellkomplexität** und
**Prädiktorenauswahl**. Beides sind Struktur-Entscheidungen, die vom Rausch-Charakter der Daten
abhängen und von möglichst vielen Daten profitieren. Und die Verzerrungen treffen alle
Komplexitätsstufen ungefähr gleich, heben sich im **Vergleich** also weitgehend auf — man will hier
ohnehin nur den *relativen* Overfitting-Unterschied zwischen den Varianten messen.

(Beides betrifft naturgemäß modellgetriebene Systeme. Für regelbasierte Systeme nennt Masters die
Konstellation „rare".)

Umsetzung am Beispiel „3 vs. 5 Hidden Neurons", 10 Datenabschnitte, 3-fache CV:

```
 1) Modell mit 3 Neuronen konfigurieren
 2) auf Abschnitten 2+3 trainieren, Abschnitt 1 vorhersagen
 3) auf 1+3 trainieren, 2 vorhersagen
 4) auf 1+2 trainieren, 3 vorhersagen
 5) Vorhersagen 1–3 poolen → OOS-Performance des 3-Neuronen-Modells
 6) Modell mit 5 Neuronen konfigurieren
 7) Schritte 2–5 wiederholen
 8) Gewinner nehmen, auf 1–3 trainieren
 9) Abschnitt 4 vorhersagen                        ← erster ECHTER OOS-Fall
10) Fenster um einen Abschnitt weiterschieben, ab 1 wiederholen
11) am Ende Abschnitte 4–10 poolen → Gesamtergebnis
12) zufrieden? Dann CV auf dem GESAMTEN Datensatz fuer beide Varianten rechnen
13) Gewinner final trainieren
```

**Der entscheidende Implementierungstrick:** Schritte 1–8 gehören in **eine einzige Routine**. Von
außen bleibt es dann ein simpler, einschichtiger Walk-Forward, der gar nicht mitbekommt, dass innen
CV läuft — *„blissfully unaware that there is cross validation going on inside the training
routine."* Das ist erheblich einfacher als das Index-Jonglieren bei [[Nested Walkforward]], wo
Walk-Forward in Walk-Forward geschachtelt wird und die Indizes explizit verwaltet werden müssen.

**Offene Frage aus Schritt 13:** das Produktivmodell mit den **letzten drei** Abschnitten
trainieren (konsistent zum Test, gut bei starker Nichtstationarität) oder mit **allen** Daten
(stabileres Modell)? Masters lässt beides gelten — „either choice is defensible".

## Bezug zu diesem Projekt

`algo/validate.py` nutzt Walk-Forward mit rollierenden Folds und **kein** k-faches CV — laut diesem
Kapitel die richtige Entscheidung, bisher aber nirgends begründet. Diese Seite liefert die
Begründung nach.

Der CV-in-WF-Sonderfall wäre erst relevant, wenn `algo/` von reinen Regeln auf ein prädiktives
Modell mit wählbarer Komplexität umschwenkt — Stand heute nicht der Fall. Er ist allerdings genau
das Werkzeug, mit dem in
[[Regularisiertes lineares Modell (Ridge, Lasso, Elastic Net)]] der Hyperparameter λ gewählt wird.

Die eine Anwendung von CV, die Masters trotz seiner Ablehnung nützlich findet, steht separat:
[[CSCV (Combinatorially Symmetric Cross Validation)]].
