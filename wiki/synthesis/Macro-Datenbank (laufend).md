---
tags: [synthesis, algo, macro, laufend]
created: 2026-08-10
updated: 2026-08-10
sources: ["[[ICT Macros & Leading Candles]]"]
---

# Macro-Datenbank (laufend)

Erzeugt von `algo/macro_db.py plot`. Basis: **MNQ**, 440 vollständig
erfasste Macro-Fenster aus 23 Handelstagen (2026-07-08 … 2026-08-07).
Diese Seite wird bei jedem Lauf überschrieben — sie ist ein laufender Stand,
kein Schnappschuss.

**Basisrate Expansion:** 35.2% [30.9–39.8] (n=440, k=155)

## Hauptergebnis: Nullbefund bei den Spooling-Kandidaten

Keiner der vier Spooling-Kandidaten (`pre_range_rel`, `pre_wick_frac`, `pre_streak`, `pre_contraction`) korreliert mit der
**Geradlinigkeit** des Fensters, und keine der 7 Vorgeschichts-Bedingungen hebt sich
von der Basisrate ab (0 von 7 mit getrennten Wilson-Intervallen).
Das ist das eigentliche Ergebnis dieser Datenbank — die Vermutung, an der Vorgeschichte
eines Macro-Fensters lasse sich ablesen, ob es gleich sauber expandiert, trägt auf
diesem Bestand nicht.

Rangkorrelation jedes Kandidaten gegen alle drei Zielgrößen (Bonferroni-Schwelle über
47 Vergleiche: p < 0.0011):

| Kandidat | Zielgröße | rho | p | n | hält Bonferroni |
|---|---|---|---|---|---|
| `pre_range_rel` | `dir` | -0.004 | 0.9329 | 417 | nein |
| `pre_range_rel` | `expansion` | +0.027 | 0.5836 | 417 | nein |
| `pre_range_rel` | `range` | +0.258 | 9.458e-08 | 417 | **ja** |
| `pre_wick_frac` | `dir` | -0.015 | 0.7541 | 440 | nein |
| `pre_wick_frac` | `expansion` | -0.024 | 0.6089 | 440 | nein |
| `pre_wick_frac` | `range` | -0.042 | 0.3801 | 440 | nein |
| `pre_streak` | `dir` | -0.004 | 0.9383 | 440 | nein |
| `pre_streak` | `expansion` | +0.004 | 0.9257 | 440 | nein |
| `pre_streak` | `range` | +0.018 | 0.7018 | 440 | nein |
| `pre_contraction` | `dir` | -0.020 | 0.6787 | 440 | nein |
| `pre_contraction` | `expansion` | -0.024 | 0.6108 | 440 | nein |
| `pre_contraction` | `range` | +0.043 | 0.3683 | 440 | nein |

### Gegenbefund: Volatilität hält an, sie staut sich nicht auf

- **`pre_range_rel` gegen `range`: rho = +0.258, p = 9.458e-08 (n=417)**

Dieser Zusammenhang zeigt **in die Gegenrichtung der Spooling-These**: Nicht Ruhe vor
dem Fenster geht großer Bewegung voraus, sondern **Aktivität**. Ein bereits unruhiger
Vorlauf (`pre_range_rel` hoch = die 10 Minuten davor waren weiter als üblich) sagt eine
**große Range** im Fenster vorher — klassische Volatilitätspersistenz, kein
Macro-spezifischer Effekt. Er taucht nur gegen `range` auf und nicht gegen `dir`, weil
`dir` = |netto|/range skalenfrei ist und einen reinen Größeneffekt strukturell nicht
sehen kann. Für die Spooling-Hypothese ist das keine Bestätigung, sondern ihr
Gegenteil: das Fenster wird groß, wenn es vorher schon laut war.

## Expansion je Fenster

![[macro-db-expansion.png]]
*Expansionsquote je Macro-Fenster mit 95%-Wilson-Intervall. Rote Linie: Basisrate über alle Fenster. Fenster mit n < 20 stehen grau auf Höhe 0 und tragen nur die n=…-Beschriftung — für sie wird bewusst keine Quote gezeigt.*

## Wann setzt der Move ein?

![[macro-db-timing.png]]
*Minute im 20-Minuten-Fenster, in der der Move einsetzt — definiert als das Extrem entgegen der Netto-Richtung.*

## Liquidität im Fenster genommen

![[macro-db-level.png]]
*Anteil der Fenster, in denen ein vor dem Fenster offenes Swing-Level genommen wurde. Rote Linie: **87.5 % aller Fenster nehmen mindestens ein Level** (87.5% [84.1–90.3] (n=440, k=385)) — die Kennzahl ist damit fast gesättigt. Die beiden Seitenquoten sind vor diesem Hintergrund weitgehend Grundrauschen der Detektorwahl (`untouched_levels`, swing=2 auf 1m), kein eigenständiger Befund.*

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
