---
tags: [concept, algo-methodology, validation, walk-forward]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[Testing and Tuning Market Trading Systems (Source)]]"]
---

# Walk-Forward Guard Buffer & Varianz-Inflation

Zwei getrennte Fehler, die im Walk-Forward auftreten, sobald der **Lookahead des Ziels größer
als eine Bar** ist — und die selbst erfahrene Entwickler laut Masters routinemäßig übersehen.
Aus [[Testing and Tuning Market Trading Systems (Source)]] (Kap. 5).

## Der allgemeine Walk-Forward-Algorithmus

Größen, die der Nutzer festlegt:

- `LOOKBACK` — Bars Historie (inkl. aktueller Bar) für die Indikatorberechnung
- `LOOKAHEAD` — Bars in die Zukunft (ohne aktuelle Bar) für das Zielvariable
- `NTRAIN` — Trainingsfälle je Fold (vor dem Abschneiden)
- `NTEST` — Testfälle je OOS-Block
- `OMIT` — abgeschnittene jüngste Trainingsfälle (Guard Buffer)
- `EXTRA` — zusätzlich zu `NTEST` übersprungene Fälle beim Fold-Vorrücken

Ablauf: `OOS_START` setzen → System auf `OOS_START−NTRAIN` bis `OOS_START−OMIT−1` trainieren →
auf `OOS_START` bis `OOS_START+NTEST−1` testen und Performance speichern → `OOS_START` um
`NTEST+EXTRA` vorrücken → wiederholen.

## Fehler 1: Future Leak durch unauffällige IS/OOS-Überlappung

Indikatoren mit Lookback > 1 sind **seriell korreliert**: bei 50 Bars Lookback teilen zwei
benachbarte Fälle 49 Bars. Genauso beim Ziel mit Lookahead > 1. Sind **beide** korreliert,
ähneln die letzten Trainingsfälle den ersten Testfällen — Information über den Testblock leckt
ins Training.

**Formel:** `OMIT = min(LOOKAHEAD, max(LOOKBACK aller Indikatoren)) − 1` Fälle am Ende des
Trainingsblocks streichen.

Beispiel aus dem Buch: Indikatoren mit Lookbacks 30/40/50, Ziel-Lookahead 80 →
`min(50, 80) − 1 = 49` Fälle streichen.

Beruhigend für die meisten modellbasierten Fälle: ist der Lookahead **genau 1**, ist `OMIT = 0`
und es geht nichts verloren.

## Fehler 2: Varianz-Inflation durch serielle Korrelation der OOS-Trades

Auch mit korrektem Guard Buffer sind die OOS-Renditen bei Lookahead > 1 untereinander korreliert
(überlappende Zukunftsfenster). Das erzeugt **keinen Bias**, aber es bläht die Fehlervarianz auf
und macht praktisch **alle** Standard-Signifikanztests anti-konservativ: P-Werte werden zu klein,
Konfidenzintervalle zu eng.

**Lösung:** `NTEST = 1` und `EXTRA = LOOKAHEAD − 1` — jede OOS-Bar wird einzeln getestet, dann
wird um den vollen Lookahead weitergesprungen, sodass die OOS-Fälle keine Kursinformation teilen.
Nebeneffekt: entspricht dem, was ein realer Trader ohnehin täte (nicht während der Haltedauer
weiter aufstocken).

## Die fünf Experimente (Random-Walk-Daten, 50.000 Preise, Lookback 100, Lookahead 10)

Weil die Preise ein reiner Random Walk sind, **muss** der korrekte Median-t-Score 0 sein und der
Anteil der Läufe mit p ≤ 0,1 muss 0,1 betragen. Alles darüber ist reiner Bias.

| # | ntest | omit | extra | Median t | Anteil p ≤ 0,1 |
|---|---|---|---|---|---|
| 1 | 50 | 0 | 0 | **5,35** | 0,920 |
| 2 | 1 | 0 | 0 | **74,64** | 1,000 |
| 3 | 1 | 9 | 0 | −0,023 | 0,314 |
| 4 | 1 | **8** | 0 | **1,88** | 0,588 |
| 5 | 1 | 9 | 9 | −0,012 | **0,101** |

Lesarten:

- **Experiment 2 ist der Schocker**: das *sauberste* Setup (nach jeder Bar neu trainieren) ist
  ohne Guard Buffer das *schlechteste*, weil die getestete Bar maximal viele Preise mit dem
  Training teilt. Bei großem Testblock (Exp. 1) verdünnt sich der Leak nach hinten.
- **Experiment 4**: ein einziger fehlender Puffer-Bar (8 statt 9) reicht für t=1,88. Es gibt kein
  „fast genug gepuffert".
- **Experiment 3 vs. 5**: Bias ist mit `omit` allein beseitigt (t≈0), aber der Test hält seinen
  Signifikanzlevel erst mit `extra` ein (0,314 → 0,101).

## Sonderfall: algorithmische Systeme mit unbekanntem Lookahead

Bei regelbasierten Systemen („öffne bei X, halte bis Y feuert") ist der Lookahead **unbestimmt** —
die Position kann 3 oder 1.000 Bars offen bleiben. Dann bestimmt nicht der Lookahead, sondern
der **Lookback** die Puffergröße. Masters nennt fünf Umgangsweisen für die Trainings-/Test-Grenze:

1. **Position über die Trainingsgrenze hinaus offen lassen** → *katastrophal*. Ein am letzten
   Trainingsbar geöffneter Supertrade zieht die Optimierung an sich, und der erste Testbar öffnet
   fast denselben Trade mit denselben Zukunftsbars. Massiver Future Leak.
2. **Position am Trainingsende zwangsschließen (mark-to-market)** → sauber, verzerrt aber die
   späten Trades gegenüber den frühen.
3. **Zeitlimit in die Exit-Regel einbauen** (z.B. „max. 20 Bars offen") und um dieses Limit
   puffern → Masters' Favorit: alle Trades folgen derselben Regel, kein Blick in die Zukunft.
   Zusatzargument aus seiner Praxis: Systeme verlieren mit wachsendem Abstand zum Entry rapide
   an Treffsicherheit, ein Zeitlimit reduziert also ohnehin den Zufallsanteil.
4. **Trades frei weiterlaufen lassen, aber `LOOKBACK−1` Bars vor Trainingsende keine neuen mehr
   öffnen** → unverzerrt, schaut aber während des Trainings über die Grenze hinaus. Besser als 3,
   wenn die Haltedauer prinzipbedingt länger als der Lookback sein muss.
5. **Auf Ein-Bar-Systeme umbauen** (siehe unten).

**Falle: unbegrenzter Lookback.** Methode 4 ist nur zulässig, wenn der Lookback wirklich
beschränkt ist. Unbeschränkt wird er z.B. bei exponentieller Glättung/rekursiven Filtern (hängen
an der gesamten Historie) — oder, viel subtiler, wenn **Handelsentscheidungen von früheren
Handelsentscheidungen abhängen** („nur öffnen, wenn keine Position offen ist", „nach 4 Verlusten
einen Monat pausieren"). Dann reicht der Lookback rekursiv bis zum Anfang der Daten zurück.

> Relevant für `algo/rules.py`: das Silver-Bullet-Modell hat ein hartes Ein-Stunden-Fenster und
> damit implizit ein Zeitlimit (Methode 3). `algo/signals.py`s Ensemble hingegen entscheidet
> teils zustandsabhängig — dort wäre zu prüfen, ob ein unbeschränkter Lookback im Sinne dieser
> Falle vorliegt.

## Konversion auf Ein-Bar-Renditen

Der eleganteste Ausweg: das unbestimmte System in eine Kette von Ein-Bar-Trades umschreiben.
Pro Bar-Close:

```
Wenn keine Position offen:
    Wenn OpenPosition wahr: Position für die nächste Bar öffnen
Sonst:
    Position schließen und die Bar-Rendite dieses Trades protokollieren
    Wenn ClosePosition falsch: dieselbe Position sofort wieder öffnen
```

(Schreibt man den Backtest selbst, genügt es, die Mark-to-Market-Rendite jeder Bar zu notieren —
die Öffnen/Schließen-Gymnastik braucht nur, wer an eine Fremdplattform gebunden ist.)

Vorteile: **kein Guard Buffer mehr nötig**, unabhängig vom Lookback; feinste Granularität für
Profit Factor und Drawdown (siehe [[Profit pro Bar vs. pro Trade]]); zwingende Voraussetzung für
[[CSCV (Combinatorially Symmetric Cross Validation)]]. Zusätzlich wird der Übergang vom letzten
Trainings- in den Testblock trivial: man merkt sich nur die Position am letzten Trainingsbar und
kann damit nahtlos vom Backtest in den Livebetrieb blenden.

## Robustheitstest gegen Nichtstationarität

Aus demselben Kapitel, als Nebenprodukt: mehrere Walk-Forwards mit **unterschiedlich langer
Testperiode** laufen lassen (täglich neu trainieren, dann alle 2 Tage, alle 5 …) und die
OOS-Performance gegen die Testperiodenlänge plotten. Der Punkt, an dem die Kurve abknickt, sagt,
wie oft das System nachtrainiert werden muss. Empfindlicher wird der Test, wenn man nur die
**letzte** Bar jedes Test-Folds bewertet.

Siehe auch [[Indikator-Stationarität & Entropie]] (Prüfung *vor* der Entwicklung) und
[[Cross Validation vs. Walk-Forward (Masters)]].
