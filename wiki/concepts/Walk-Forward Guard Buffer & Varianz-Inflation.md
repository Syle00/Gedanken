---
tags: [concept, algo-methodology, validation, walk-forward, referenz]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[Testing and Tuning Market Trading Systems (Source)]]"]
---

# Walk-Forward Guard Buffer & Varianz-Inflation

Zwei getrennte Fehler, die im Walk-Forward auftreten, sobald der **Lookahead des Ziels größer
als eine Bar** ist. Aus [[Testing and Tuning Market Trading Systems (Source)]] (Kap. 5,
Programme `OVERLAP.CPP`, `XvW.CPP`).

## Parameter des allgemeinen Walk-Forward

| Name | Bedeutung |
|---|---|
| `LOOKBACK` | Bars Historie **inkl.** aktueller Bar für die Indikatorberechnung |
| `LOOKAHEAD` | Bars in die Zukunft **ohne** aktuelle Bar für die Zielvariable |
| `NTRAIN` | Trainingsfälle je Fold, **vor** dem Abschneiden |
| `NTEST` | Testfälle je OOS-Block |
| `OMIT` | abgeschnittene jüngste Trainingsfälle (Guard Buffer) |
| `EXTRA` | zusätzlich zu `NTEST` übersprungene Fälle beim Fold-Vorrücken |

Abgeleitete Größen:

```
Gesamt-Rückblick vom aktuellen Bar   = LOOKBACK + NTRAIN − 2
tatsächliche Trainingsfälle          = NTRAIN − OMIT
Fold-Schrittweite                    = NTEST + EXTRA
```

Die beiden **Pflichteinstellungen** bei `LOOKAHEAD > 1`:

```
OMIT  = min(LOOKAHEAD, max_j LOOKBACK_j) − 1     ← gegen Future Leak (Fehler 1)
NTEST = 1 ,  EXTRA = LOOKAHEAD − 1               ← gegen Varianz-Inflation (Fehler 2)
```

`max_j LOOKBACK_j` = größter Lookback über **alle** Indikatoren.
Beispiel aus dem Buch: Lookbacks 30/40/50, Lookahead 80 → `min(50, 80) − 1 = 49`.
Ist `LOOKAHEAD = 1`, wird `OMIT = 0` und es geht nichts verloren.

## Der Algorithmus

```
1) OOS_START = gewünschter Teststart
   (ganzer Datensatz genutzt → OOS_START = NTRAIN)
2) System trainieren auf Fällen  OOS_START − NTRAIN  …  OOS_START − OMIT − 1
3) System testen auf Fällen      OOS_START          …  OOS_START + NTEST − 1
   Performance speichern.  (NTEST muss nicht fix sein — z.B. Kalenderjahre.)
4) Bleiben Daten übrig: OOS_START += NTEST + EXTRA , zurück zu 2)
```

Als Python-nahe Schleife (entspricht `OVERLAP.CPP`; `data` hat `ncols` Spalten, letzte Spalte =
Ziel, jede Zeile ein Bar):

```python
trn_start = 0          # Index des ersten Trainingsfalls
istart    = ntrain     # Index des ersten OOS-Falls
oos       = []

while True:
    test_start = trn_start + ntrain
    if test_start >= ncases:
        break

    # --- Training: NUR ntrain - omit Faelle, ab trn_start ---
    model = fit(data[trn_start : trn_start + ntrain - omit])

    # --- Test: nt Faelle ab istart (letzter Fold evtl. kuerzer) ---
    nt = min(ntest, ncases - istart)
    for k in range(test_start, test_start + nt):
        pred   = model.predict(data[k, :-1])
        target = data[k, -1]
        oos.append(target if pred > 0 else -target)

    istart    += nt + extra
    trn_start += nt + extra
```

Die beiden Fehler im Detail:

### Fehler 1 — Future Leak durch unauffällige IS/OOS-Überlappung

Indikatoren mit Lookback > 1 sind **seriell korreliert**: bei 50 Bars Lookback teilen zwei
benachbarte Fälle 49 Bars, der Indikatorwert ändert sich kaum. Dasselbe gilt für ein Ziel mit
Lookahead > 1 (bei Lookahead 10 haben Nachbarfälle 9 gemeinsame Zukunfts-Bars).

Sind **beide** korreliert, ähneln die letzten Trainingsfälle den ersten Testfällen — Information
über den Testblock steckt damit schon im Training. Ist nur *eines* von beiden korreliert, ist
alles in Ordnung: dann teilen die Fälle keine prägende Information.

Herleitung der Formel (Masters lässt sie als Übung): Testblock beginnt bei Bar 100. Teilt der
Trainingsfall bei Bar 99 sowohl über einen Indikator als auch über das Ziel Preise mit Bar 100?
Bar 98? Man streicht so lange, bis entweder die Indikator-Preismenge oder die Ziel-Preismenge
disjunkt ist — das tritt nach `min(Lookback, Lookahead) − 1` Fällen ein.

### Fehler 2 — Varianz-Inflation

Auch mit korrektem Guard Buffer sind die OOS-Renditen bei `LOOKAHEAD > 1` untereinander
korreliert (überlappende Zukunftsfenster). Folgen:

- **Kein Bias**, aber aufgeblähte Fehlervarianz: die unverzerrte Schätzung streut stärker um den
  wahren Wert. Bei großem Lookahead so stark, dass die Zahl praktisch wertlos wird.
- Praktisch **alle** Standard-Signifikanztests setzen Unabhängigkeit voraus und werden
  anti-konservativ: P-Werte zu klein, Konfidenzintervalle zu eng — der schlimmste Fehlertyp.
- Mechanismus: bei unabhängigen Renditen heben sich positive und negative Zufallsfehler auf. Bei
  serieller Korrelation kommen sie in Klumpen und heben sich schlechter auf.

Lösung `NTEST = 1`, `EXTRA = LOOKAHEAD − 1`: jede OOS-Bar wird einzeln getestet, dann wird um den
vollen Lookahead gesprungen, sodass die OOS-Fälle keine Kursinformation teilen. Beispiel
Lookahead 5, OOS-Fold bei Bar 100: Training endet bei Bar 95 (4 Fälle gestrichen), nächster
OOS-Fold bei Bar 105. Nebeneffekt: entspricht dem, was ein realer Trader ohnehin tut — er baut
während der Haltedauer nicht weiter auf.

## Die fünf Experimente

`OVERLAP.EXE` erzeugt einen **reinen Random Walk** (unvorhersagbar) und misst über
`nreps = 10.001` Wiederholungen den Median-t-Score der gepoolten OOS-Renditen sowie den Anteil
der Läufe mit p ≤ 0,1. Korrekt wäre t ≈ 0 und Anteil ≈ 0,1; alles darüber ist reiner Bias.

Feste Parameter: `nprices = 50.000`, `lookback = 100`, `lookahead = 10`, `ntrain = 50`.

| # | ntest | omit | extra | Median t | Anteil p ≤ 0,1 | Deutung |
|---|---|---|---|---|---|---|
| 1 | 50 | 0 | 0 | **5,35** | 0,920 | großer Testblock, kein Puffer |
| 2 | 1 | 0 | 0 | **74,64** | 1,000 | „sauberstes" Setup, kein Puffer |
| 3 | 1 | 9 | 0 | −0,023 | 0,314 | Bias weg, Varianz-Inflation bleibt |
| 4 | 1 | **8** | 0 | **1,88** | 0,588 | ein Bar zu wenig gepuffert |
| 5 | 1 | 9 | 9 | −0,012 | **0,101** | beides korrekt behandelt |

Drei Lehren:

1. **Experiment 2 ist kontraintuitiv.** Das scheinbar sauberste Vorgehen (nach jeder Bar neu
   trainieren, nur die nächste Bar testen) ist ohne Puffer das *schlechteste*, weil die getestete
   Bar die maximal mögliche Zahl an Preisen mit dem Training teilt. Bei großem Testblock (Exp. 1)
   verdünnt sich der Leak nach hinten, weil spätere Testfälle weniger Überlappung haben.
2. **Experiment 4: es gibt kein „fast genug".** Ein einziger fehlender Puffer-Bar (8 statt 9)
   lässt t = 1,88 übrig.
3. **Experiment 3 vs. 5:** `omit` allein beseitigt den Bias (t ≈ 0), aber erst `extra` stellt das
   Signifikanzniveau her (0,314 → 0,101).

## Sonderfall: algorithmische Systeme mit unbekanntem Lookahead

Bei regelbasierten Systemen („öffne bei X, halte bis Y feuert") ist der Lookahead **unbestimmt** —
die Position kann 3 oder 1.000 Bars offen bleiben. Dann bestimmt nicht der Lookahead, sondern der
**Lookback** die Puffergröße, und der ist meist unangenehm groß. Fünf Umgangsweisen für die
Trainings-/Test-Grenze:

| # | Methode | Bewertung |
|---|---|---|
| 1 | Position über die Trainingsgrenze hinaus offen lassen | **katastrophal** |
| 2 | am Trainingsende zwangsschließen (mark-to-market) | sauber, verzerrt späte Trades |
| 3 | Zeitlimit in die Exit-Regel + Puffer in dieser Größe | **Masters' Favorit** |
| 4 | frei laufen lassen, aber `LOOKBACK−1` vor Ende keine neuen Trades | unverzerrt, schaut aber voraus |
| 5 | auf Ein-Bar-System umbauen | bester Weg, wenn machbar |

**Warum Methode 1 katastrophal ist:** öffnet sich auf Bar 1000 (letzter Trainingsbar) ein extrem
profitabler Trade, zieht die Optimierung die Lookbacks zu genau diesem Trade hin. Bar 1001
(erster Testbar) teilt fast die gesamte Vorgeschichte, öffnet also fast sicher denselben Trade —
**und teilt dieselben profitablen Zukunfts-Bars**. Preise werden hier in *beide* Richtungen
geteilt.

**Warum Masters Methode 3 bevorzugt:** (a) alle Trades folgen derselben Regel, egal ob früh oder
spät im Trainingszeitraum (Methode 2 verletzt das); (b) kein Blick in die Zukunft (Methode 4
tut das, wenn auch harmlos); (c) inhaltliches Argument aus seiner Praxis — *Systeme verlieren mit
wachsendem Abstand zum Entry rasch an Treffsicherheit*; ein Zeitlimit reduziert also ohnehin den
Zufallsanteil. Beispielregel: „halte bis der kurze MA unter den langen kreuzt **oder** 20 Bars
vergangen sind", dann 20 Bars vor Trainingsende keine neuen Trades mehr eröffnen.

**Wann Methode 4 doch besser ist:** wenn das Handelskonzept lange Haltedauern erzwingt. Methode 3
kostet das Zeitlimit an Trading-Gelegenheiten, Methode 4 den Lookback — ist die nötige Haltedauer
länger als der Lookback, verliert Methode 4 weniger.

Rechenbeispiel Methode 4: Trainingsende Bar 1000, max. Lookback 150 → letzter mögliche
Entry-Bar ist `1000 − (150 − 1) = 851`. Der Test ab Bar 1001 schaut auf Bars 852…1001, die
Entscheidungsgrundlagen sind damit **vollständig disjunkt**.

### Falle: unbeschränkter Lookback

Methode 4 ist nur zulässig, wenn der Lookback wirklich beschränkt ist. Unbeschränkt wird er:

- **offensichtlich** bei exponentieller Glättung oder rekursiven Filtern — deren Wert hängt an der
  gesamten Historie zurück bis zum ersten Preis. Die Beiträge früher Preise sind winzig, aber
  Masters warnt ausdrücklich davor, das als unerheblich abzutun.
- **subtil**, wenn Handelsentscheidungen von **früheren Handelsentscheidungen** abhängen:
  „nur öffnen, wenn keine Position offen ist"; „nach 4 Verlusten in Folge einen Monat pausieren".
  Dann hängt die Entscheidung am vorigen Trade, der am vorvorigen, ad infinitum.

> Masters dazu: *„Sceptics may scoff at this concept. I do not, as I was badly burned by this very
> issue early in my career."*

Für `algo/`: `rules.py::plan_trade` hat ein hartes Ein-Stunden-Fenster und damit implizit ein
Zeitlimit (Methode 3). `signals.py` / `backtest_ensemble.py` entscheiden teils zustandsabhängig —
dort ist zu prüfen, ob dieser Fall vorliegt.

## Konversion auf Ein-Bar-Renditen (Methode 5)

Ein System mit unbestimmter Haltedauer wird in eine Kette von Ein-Bar-Trades umgeschrieben.
Auszuführen **bei jedem Bar-Close**:

```
Wenn keine Position offen:
    Wenn OpenPosition wahr:  Position eroeffnen, gilt bis zum naechsten Bar
Sonst:
    Position schliessen und die Bar-Rendite dieses Trades protokollieren
    Wenn ClosePosition falsch: dieselbe Position sofort wieder eroeffnen
```

Diese Umständlichkeit braucht nur, wer an eine Fremdplattform gebunden ist, die explizites
Öffnen/Schließen zum Protokollieren verlangt. Wer den Backtest selbst schreibt, notiert schlicht
pro Bar die Mark-to-Market-Rendite der offenen Position. Kompakt (entspricht `PER_WHAT.CPP`):

```python
if price[i] > thresh * ma[i]:      # Entry-Regel
    position = 1
elif price[i] < ma[i]:             # Exit-Regel
    position = 0
# sonst: Position unveraendert weiterfuehren
ret = price[i+1] - price[i] if position else 0.0
```

Vorteile:

- **Kein Guard Buffer mehr nötig**, unabhängig vom Lookback → jeder Fold wird effektiv größer.
- Feinste Granularität für Profit Factor und Drawdown — siehe [[Profit pro Bar vs. pro Trade]].
- Zwingende Voraussetzung für [[CSCV (Combinatorially Symmetric Cross Validation)]].
- **Nahtloser Übergang Backtest → Live.** Man merkt sich nur die Position am letzten
  Trainingsbar. Beispiel: 120 Bars, Training 1–100, Test 101–120. Die letzte Trainings-
  Entscheidung fällt auf Bar 99 (Bar 100 liefert deren Rendite); gespeichert wird die Position von
  Bar 99→100. Der Test entscheidet dann auf Bar 100 und wertet mit Bar 101. Am Ende: auf Bar 119
  entscheiden, Position merken, mit dem retrainierten Modell auf Bar 120 entscheiden — **das ist
  die erste reale Live-Order für Bar 121.**

## Robustheitstest gegen Nichtstationarität

Nebenprodukt desselben Kapitels: mehrere Walk-Forwards mit **unterschiedlich langer Testperiode**
laufen lassen (täglich neu trainieren, dann alle 2 Tage, alle 5 …) und die OOS-Performance gegen
die Testperiodenlänge plotten.

Typisches Bild: Maximum bei kürzester Testperiode (häufigstes Nachtrainieren), dann zunächst
langsamer, später steiler Abfall. Der Knick sagt, **wie oft das System nachtrainiert werden muss**.
Empfindlicher wird der Test, wenn man je Fold nur die **letzte** Bar bewertet — das eliminiert den
Einfluss der besseren frühen Bars, auf Kosten von etwas mehr Streuung.

Vorgelagerte Prüfung derselben Frage: [[Indikator-Stationarität & Entropie]].
Vergleich mit dem Alternativverfahren: [[Cross Validation vs. Walk-Forward (Masters)]].

## Implementierung

`algo/masters.py`: `guard_buffer(lookback, lookahead)` liefert `OMIT`, `walkforward(n, ntrain, ntest, omit, extra)` ist der Fold-Generator. Gegen Varianz-Inflation `ntest=1, extra=LOOKAHEAD-1` setzen.

**Am eigenen Code geprüft (2026-08-11, Backlog 8, siehe `algo/PLAN.md`): kein Leck.** `algo/validate.py::walk_forward` nutzt adjazente Folds ohne Puffer — das ist hier korrekt, nicht bloß toleriert: die Zielgröße des Ensembles ist die Richtung des Folgetags (`signals.py::build_features`, `y[i]` = Tag i+1), also Lookahead genau 1, und `guard_buffer(L, 1) = 0`. `signals.py` ist zustandslos (reine Rückwärts-Funktionen, `history = mnq_rows[:i+1]`), `SilverBulletStrategy` entscheidet pro Kerze nur aus `bars[t<=when]` in einem harten 1h-Fenster — kein tagesübergreifender Zustand, der den Lookback formal unbeschränkt machen würde. Trotzdem gehärtet: `walk_forward(..., omit=0)` streicht bei `omit>0` die jüngsten Trainingstage je Fold; ein später auf H Tage verlängerter Zielhorizont setzt nur noch `omit=H-1`, statt still anti-konservativ zu werden.

Selbstcheck: `python algo/masters.py` (auch in `algo/selfcheck.py`).
