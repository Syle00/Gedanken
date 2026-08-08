---
tags: [concept, algo-methodology, validation, walk-forward]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[Testing and Tuning Market Trading Systems (Source)]]"]
---

# Cross Validation vs. Walk-Forward (Masters)

Warum Cross Validation bei Marktdaten **nicht** die datensparsamere Variante von Walk-Forward
ist, sondern ein anderes Verfahren mit eigenen Verzerrungen. Aus
[[Testing and Tuning Market Trading Systems (Source)]] (Kap. 5).

## Der Reiz und die Falle

Der Reiz von k-facher Cross Validation: Walk-Forward verwirft in jedem Fold sämtliche Daten
**nach** dem Testblock. CV nutzt sie mit. Gerade in den frühen Folds, wo Walk-Forward kaum
Historie hat, ist das ein echter Vorteil.

**Guard Buffer beidseitig.** Wie im Walk-Forward gilt bei Lookahead > 1:
`min(lookback, lookahead) − 1` Fälle streichen — hier aber **an beiden Rändern** des Testblocks,
also auch am Anfang des Trainingsteils, der hinter dem Testblock liegt. Siehe
[[Walk-Forward Guard Buffer & Varianz-Inflation]].

## Drei Einwände

### 1. CV kann pessimistisch verzerrt sein

Jeder CV-Trainingssatz ist kleiner als der volle Datensatz, mit dem man das Produktivmodell
trainieren würde. Kleinere Trainingsmenge → ungenauere Parameter → schlechtere OOS-Leistung.
CV **unterschätzt** deshalb tendenziell, was das final trainierte Modell leisten wird.

### 2. CV kann optimistisch verzerrt sein

Und zwar genau bei nichtstationären Daten, also praktisch immer im Markt. Die inneren Folds
trainieren auf Daten aus der **Zukunft** des Testblocks. Selbst wenn kein einzelner Fall geteilt
wird, bekommt der Trainingsalgorithmus Information über die künftige **Verteilung**.

Masters' Beispiel: die Volatilität steigt über die Historie stetig. Im Walk-Forward (und im
echten Leben) hat jeder Testblock höhere Volatilität als sein Trainingssatz. In den inneren
CV-Folds ist der Testblock von Trainingsdaten *eingeklammert* — das Modell hat die Bandbreite
schon gesehen. Ein subtiler Future Leak ohne geteilte Fälle.

### 3. CV bildet die Realität nicht ab

Und damit fällt auch der Datenvorteil weg: die meisten Entwickler wählen ihr
Walk-Forward-Trainingsfenster ohnehin genauso groß wie das des späteren Produktivmodells — eben
weil sie nicht über zu viele Marktregime hinweg trainieren wollen. Dann hat CV keinen
Datenvorteil mehr, wohl aber die Verzerrungen aus (2).

> Masters' Fazit wörtlich: *„I cannot recommend cross validation analysis in trading system
> development, except in the most unusual special situations."*

## XvW: wie groß ist der Unterschied praktisch?

Das Programm `XvW.CPP` lässt dasselbe System zweimal laufen (CV und Walk-Forward) und gibt beide
mittleren OOS-Renditen samt t-Score der Differenz aus. Beispielzeile aus dem Buch:

```
Grand XVAL = 0.02249 (t=253.371)   WALK = 0.00558 (t=81.355)
StdDev = 0.00011   t = 150.768   rtail = 0.00000
```

CV liefert hier die **vierfache** mittlere Rendite von Walk-Forward, hochsignifikant verschieden.
Bei Trend = 0 (reiner Random Walk) sind erwartungsgemäß alle t-Scores insignifikant. Kernaussage:
*in nahezu jeder praktischen Konstellation liefern CV und Walk-Forward deutlich, oft wild
verschiedene Ergebnisse* — die beiden sind nicht austauschbar.

## Die eine Ausnahme: CV innerhalb von Walk-Forward

CV ist dort vertretbar, wo die drei Einwände wenig wiegen: bei **Modellkomplexität** und
**Prädiktorenauswahl**. Beides sind Struktur-Entscheidungen, die vom Rausch-Charakter der Daten
abhängen und von möglichst vielen Daten profitieren; die Verzerrungen treffen alle
Komplexitätsstufen ungefähr gleich und heben sich im Vergleich weitgehend auf.

Umsetzung (Beispiel: 3 vs. 5 Hidden Neurons, 10 Datenabschnitte, 3-fache CV):

1. Modell mit 3 Neuronen konfigurieren.
2. Auf Abschnitten 2+3 trainieren, Abschnitt 1 vorhersagen.
3. Auf 1+3 trainieren, 2 vorhersagen.
4. Auf 1+2 trainieren, 3 vorhersagen.
5. Vorhersagen 1–3 poolen → OOS-Performance des 3-Neuronen-Modells.
6.–7. Dasselbe mit 5 Neuronen.
8. Gewinner nehmen, auf 1–3 trainieren.
9. Abschnitt 4 vorhersagen → **erster echter OOS-Fall**.
10. Fenster um einen Abschnitt weiterschieben, ab 1 wiederholen.
11. Am Ende Abschnitte 4–10 poolen → Gesamtergebnis.

Wichtig für die Implementierung: Schritte 1–8 gehören in **eine einzige Routine**. Von außen
bleibt es dann ein simpler, einschichtiger Walk-Forward, der gar nicht mitbekommt, dass innen
CV läuft. Das ist deutlich einfacher als das Index-Jonglieren bei
[[Nested Walkforward]], wo Walk-Forward in Walk-Forward geschachtelt wird.

Offene Frage aus Schritt 13 des Buches: das Produktivmodell mit den **letzten drei** Abschnitten
trainieren (konsistent zum Test, gut bei starker Nichtstationarität) oder mit **allen** Daten
(stabileres Modell)? Beides vertretbar.

## Bezug zu diesem Projekt

`algo/validate.py` nutzt Walk-Forward mit rollierenden Folds und **kein** k-faches CV — laut
diesem Kapitel die richtige Entscheidung, bisher aber nirgends begründet. Diese Seite liefert die
Begründung nach. Der CV-in-WF-Sonderfall wäre erst relevant, wenn `algo/` von reinen Regeln auf
ein prädiktives Modell mit wählbarer Komplexität umschwenkt — Stand heute nicht der Fall.
