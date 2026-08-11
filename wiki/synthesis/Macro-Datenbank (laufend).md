---
tags: [synthesis, algo, macro, laufend]
created: 2026-08-11
updated: 2026-08-11
sources: ["[[ICT Macros & Leading Candles]]"]
---

# Macro-Datenbank (laufend)

Erzeugt von `algo/macro_db.py plot`. Basis: **MNQ**, 483 vollständig
erfasste Macro-Fenster aus 23 Handelstagen (2026-07-08 … 2026-08-07).
Diese Seite wird bei jedem Lauf überschrieben — sie ist ein laufender Stand,
kein Schnappschuss.

**Basisrate Expansion:** 35.0% [30.9–39.3] (n=483, k=169)

## Hauptergebnis: Nullbefund bei den Vorlauf-Kandidaten

> **Begriffsklärung (2026-08-10).** Diese vier Kandidaten messen die **Ruhe vor** dem
> Fenster — die ursprüngliche Lesart von „Spooling". Die inzwischen belegte
> ICT-Definition meint mit Spooling das Gegenteil, nämlich den **gerichteten Lauf**
> selbst (siehe [[ICT Macros & Leading Candles]]). Sie heißen hier deshalb
> Vorlauf-Kandidaten; das Spooling im ICT-Sinn steckt in `dir` und `mfe_*`.

Keiner der vier Vorlauf-Kandidaten (`pre_range_rel`, `pre_wick_frac`, `pre_streak`, `pre_contraction`) korreliert mit der
**Geradlinigkeit** des Fensters, und keine der 7 Vorgeschichts-Bedingungen hebt sich
von der Basisrate ab (0 von 7 mit getrennten Wilson-Intervallen).
Die Vermutung, an der Vorgeschichte eines Macro-Fensters lasse sich ablesen, ob es
gleich sauber expandiert, trägt auf diesem Bestand nicht.

Rangkorrelation jedes Kandidaten gegen alle 4 Zielgrößen (Bonferroni-Schwelle über
56 Vergleiche: p < 0.0009):

| Kandidat | Zielgröße | rho | p | n | hält Bonferroni |
|---|---|---|---|---|---|
| `pre_range_rel` | `dir` | +0.008 | 0.8718 | 460 | nein |
| `pre_range_rel` | `expansion` | +0.021 | 0.6578 | 460 | nein |
| `pre_range_rel` | `range` | +0.258 | 1.98e-08 | 460 | **ja** |
| `pre_range_rel` | `mfe_60` | +0.198 | 2.538e-05 | 447 | **ja** |
| `pre_wick_frac` | `dir` | -0.012 | 0.7933 | 483 | nein |
| `pre_wick_frac` | `expansion` | -0.021 | 0.6389 | 483 | nein |
| `pre_wick_frac` | `range` | -0.072 | 0.1161 | 483 | nein |
| `pre_wick_frac` | `mfe_60` | -0.034 | 0.4583 | 469 | nein |
| `pre_streak` | `dir` | +0.006 | 0.897 | 483 | nein |
| `pre_streak` | `expansion` | +0.014 | 0.7585 | 483 | nein |
| `pre_streak` | `range` | +0.025 | 0.5865 | 483 | nein |
| `pre_streak` | `mfe_60` | +0.044 | 0.3363 | 469 | nein |
| `pre_contraction` | `dir` | -0.028 | 0.5417 | 483 | nein |
| `pre_contraction` | `expansion` | -0.031 | 0.4992 | 483 | nein |
| `pre_contraction` | `range` | +0.024 | 0.5916 | 483 | nein |
| `pre_contraction` | `mfe_60` | +0.027 | 0.5617 | 469 | nein |

### Gegenbefund: Volatilität hält an, sie staut sich nicht auf

- **`pre_range_rel` gegen `range`: rho = +0.258, p = 1.98e-08 (n=460)**
- **`pre_range_rel` gegen `mfe_60`: rho = +0.198, p = 2.538e-05 (n=447)**

Dieser Zusammenhang zeigt **in die Gegenrichtung der ursprünglichen Lesart**: Nicht
Ruhe vor dem Fenster geht großer Bewegung voraus, sondern **Aktivität**. Ein bereits
unruhiger Vorlauf (`pre_range_rel` hoch = die 10 Minuten davor waren weiter als
üblich) sagt eine **große Auslenkung** vorher — klassische Volatilitätspersistenz,
kein Macro-spezifischer Effekt. Gegen `dir` taucht er nicht auf, weil `dir` =
|netto|/range skalenfrei ist und einen reinen Größeneffekt strukturell nicht sehen
kann. Das Fenster wird groß, wenn es vorher schon laut war.

## Ist das Macro ein Startfenster? Gemessen: nein

ICT korrigiert ausdrücklich die Lesart, der Move finde *innerhalb* der 20 Minuten
statt: *„The move **begins** in those 20 minutes. It's not the entirety of the
move."* Ein Macro wäre demnach ein **Startfenster**, kein Container.

Testbar gemacht: die größte Auslenkung ab Fenster-Open (`mfe`, richtungsagnostisch,
weil ein Macro laut ICT keine Richtung liefert) über wachsende Horizonte. Ein
Startfenster müsste die Auslenkung **schneller** wachsen lassen als die Wurzel der
Zeit — das ist der Maßstab eines reinen Random Walk.

| Horizont | Median MFE (Pkt) | n | gemessenes Wachstum | Random Walk erwartet |
|---|---|---|---|---|
| +20 Min | 49.00 | 483 | — | — |
| +40 Min | 67.50 | 477 | ×1.38 | ×1.41 |
| +60 Min | 83.00 | 469 | ×1.69 | ×1.73 |

**Befund**: Das gemessene Wachstum entspricht der Wurzel-der-Zeit-Erwartung praktisch
exakt. Die Auslenkung wächst nach dem Macro also genau so weiter, wie sie es bei
reiner Diffusion täte — **kein messbarer Startfenster-Effekt** auf diesem Bestand.
Das widerlegt ICTs Aussage nicht (sie betrifft die *Richtung* eines Setups, nicht die
mittlere Auslenkung über alle Fenster), aber es zeigt: aus dem bloßen Zeitpunkt allein
lässt sich kein Bewegungsvorteil ableiten.

**Nebenbefund**: ICTs Mindestziel von 10 Handles für NASDAQ-Scalps wird in praktisch
**jedem** Fenster erreicht — der Median-MFE liegt ein Vielfaches darüber. Die Schwelle
taugt damit nicht als Filter für die Fensterauswahl, sondern höchstens als Untergrenze
für die Stop- und Zielwahl.

## Expansion je Fenster

![[macro-db-expansion.png]]
*Expansionsquote je Macro-Fenster mit 95%-Wilson-Intervall. Rote Linie: Basisrate über alle Fenster. Fenster mit n < 20 stehen grau auf Höhe 0 und tragen nur die n=…-Beschriftung — für sie wird bewusst keine Quote gezeigt.*

## Wann setzt der Move ein?

![[macro-db-timing.png]]
*Minute im 20-Minuten-Fenster, in der der Move einsetzt — definiert als das Extrem entgegen der Netto-Richtung.*

## Liquidität im Fenster genommen

![[macro-db-level.png]]
*Anteil der Fenster, in denen ein vor dem Fenster offenes Swing-Level genommen wurde. Rote Linie: **88.2 % aller Fenster nehmen mindestens ein Level** (88.2% [85.0–90.8] (n=483, k=426)) — die Kennzahl ist damit fast gesättigt. Die beiden Seitenquoten sind vor diesem Hintergrund weitgehend Grundrauschen der Detektorwahl (`untouched_levels`, swing=2 auf 1m), kein eigenständiger Befund.*

## Vorbehalte

- Die Stichprobe ist klein: rund 20 Tage je Fenster. Aussagen auf
  **Fenster-Ebene** sind noch nicht belastbar, Aussagen auf **Bedingungs-Ebene**
  über alle Fenster hinweg früher.
- Fenster desselben Handelstags sind nicht unabhängig — p-Werte sind optimistisch.
- 6 Fenster liegen mit n < 20 unter der Mindeststichprobe aus `fmt_quote()`/`vergleich()` und stehen in Diagramm 1 grau auf Höhe 0, nur mit n=…-Beschriftung statt eines Prozentbalkens: 18:50, 19:50, 20:50, 21:50, 22:50, 23:50. Am deutlichsten **23:50** mit nur n=1 (Exportlücke 23:59–00:08) — dessen 100%-Rohwert ist ein Stichproben-Artefakt, keine belastbare Quote (Wilson-Intervall entsprechend breit: 20,7–100 %) und war als vollwertiger, höchster Balken die irreführendste Stelle der Grafik. **16:50** fehlt sogar ganz (ragt über den Sessionschluss 17:00 hinaus) und taucht im Diagramm nicht auf. Die Asia-Session ist damit systematisch knapper besetzt als der Rest, nicht nur ein Einzelfall.
- NDOG/NWOG/ORG sind noch keine Level-Quelle (Kalendertag- statt Session-Logik,
  siehe `algo/PLAN.md`).

## Verwandt

- [[ICT Macros & Leading Candles]]
- [[Muster-Validierung (laufend)]]
