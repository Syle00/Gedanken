---
tags: [concept, ict, trading-ict, 2026, core, pd-array]
created: 2026-08-05
updated: 2026-08-05
sources: ["[[ICT Algorithmic Time & Price Grids (Source)]]"]
---

# Algorithmic Time & Price Grid

ICTs eigene Bezeichnung für das Zusammenspiel aus [[PD Array|PD Arrays]] (Preis-Achse) und
[[ICT Macros & Leading Candles|Macro-Startzeiten]] (Zeit-Achse) — vergleichbar mit einem
Einmaleins-Raster: horizontale Linien sind Preis-Level (Octant/Quadrant einer Range), vertikale
Linien sind Zeitpunkte (Beginn eines Macro-Fensters, volle/halbe Stunde). Ein PD Array, das genau am
Kreuzungspunkt aus beidem entsteht, gilt als höchste Bestätigungsstufe — deckt sich mit der
bestehenden [[PD Array#3 Komponenten einer starken PD (Kurz Notizen)|3-Komponenten-Regel starker PD Arrays]]
(Time of Day + Formation + gegradetes Level), benennt sie hier aber explizit als wiederholbares
Raster statt als lose Checkliste.

## Fraktale Wiederholung

Innerhalb eines laufenden Trends bildet sich an **jedem** erreichten Octant-/Quadrant-Level ein
neues PD Array (Order Block, FVG, IFVG), das den Trend bestätigt — nicht nur an einem
ausgezeichneten Level. Praxisregel zur Prüfung:

- Wick-Consequent-Encroachment (Midpoint) jedes Wicks graden — bei bullischem Bias dürfen Bodies den
  Midpoint **nicht** unterschreiten (Wicks dürfen kurz durchtauchen).
- Ein [[IFVG (Inverse Fair Value Gap)|IFVG]] kann, sobald Preis erneut darüber/darunter schließt,
  zu seiner **First Utilization zurückkehren** (ursprüngliche FVG-Polarität) — die Zuordnung ist
  damit nicht endgültig, sondern hängt vom zuletzt bestätigten Close ab.
- Jede neue PD Array muss an ein Octant/Quadrant-Level **angankert** sein, sonst gilt sie laut ICT
  nicht als valide — reine Formähnlichkeit reicht nicht.

## Praxisbeispiel (NQ, 2026-07-31)

Tagesbias vorab öffentlich genannt (X-Post vor Handelsbeginn): Preis eröffnet in der **leeren Zone
zwischen zwei nicht überlappenden Daily-[[Suspension Block|Suspension Blocks]]** und läuft von dort
schnell in Richtung des oberen Blocks — siehe [[Low Resistance Liquidity Run]] für die
Setup-Bedingung. Im weiteren Verlauf bestätigte sich der Bias wiederholt exakt an
Octant-/Quadrant-Kreuzungen mit Macro-Startzeiten (u.a. 9:50–10:10-, 10:50-11:10-Fenster).

## Verwandt

- [[PD Array]], [[ICT Macros & Leading Candles]]
- [[Chain of Custody (Q-Validation)]] — liefert die Octant/Quadrant/16tel-Feinheit dieses Rasters
- [[Low Resistance Liquidity Run]], [[Buy & Sell Program]]
- [[IFVG (Inverse Fair Value Gap)]], [[Suspension Block]]
- [[ICT Algorithmic Time & Price Grids (Source)]]
