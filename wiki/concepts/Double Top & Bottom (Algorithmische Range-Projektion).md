---
tags: [concept, ict, trading-ict]
created: 2026-08-06
updated: 2026-08-06
sources: ["[[ICT Mentorship Core Content - Month 04 - Double Bottom Double Top (Source)]]"]
---

# Double Top & Bottom (Algorithmische Range-Projektion)

Retail liest ein Double Top/Bottom als klassische Unterstützung/Widerstand und erwartet eine
Ablehnung dort. ICTs Gegenposition: **niemals einem Double Top/Bottom vertrauen** — beide Extreme
sammeln über die Zeit Stop-Liquidität (Buy Stops über einem Double Top, Sell Stops unter einem
Double Bottom), und Preis läuft mit hoher Wahrscheinlichkeit durch beide Level, um genau diese
Liquidität zu holen.

## Measured-Move-Projektion

Statt das Double Top/Bottom als Endpunkt zu behandeln, wird die **Range dazwischen** vermessen und
über den Level hinaus projiziert:

- **Double Top**: Distanz vom höheren der beiden Hochs bis zum Tief zwischen den beiden Peaks
  messen, dieselbe Distanz **über** das Double Top projizieren → algorithmisches Kursziel.
- **Double Bottom**: spiegelbildlich — Distanz vom tieferen der beiden Tiefs bis zum Hoch
  zwischen den beiden Tälern, dieselbe Distanz **unter** das Double Bottom projiziert.
- Im Quellmaterial trifft die Projektion beide Male auf **1 Pip genau** — als Beleg dafür, dass der
  Algorithmus diese Referenzpunkte "kennt", auch wenn seit der Konsolidierung viel Zeit vergangen
  ist.

## Zusammenspiel mit anderen PD Arrays

Das Double Top/Bottom liefert den **Auslöser** (Stop-Run durch das alte Extrem), das eigentliche
Ziel liegt oft an einer weiter entfernten Konfluenz aus [[Fair Value Gap (FVG)|FVG]],
[[Liquidity Void]] oder [[Order Block]] — die Reihenfolge im Quellbeispiel: Preis läuft zuerst in
einen [[Order Block]]/eine FVG **innerhalb** der Range, zeigt dort eine Reaktion, danach erst der
Run durch das Double Top/Bottom in Richtung der projizierten Zielzone.

## Extreme vs. Mitte der Range

Hohe Wahrscheinlichkeit liegt an den **Extremen** einer Trading-Range (dort, wo die Stops beider
Seiten liegen), niedrige Wahrscheinlichkeit in der **Mitte**. Für Stop-Größen gilt auf höheren
Timeframes (z.B. Stundenchart) nicht mehr die übliche 10-20-Pip-Sweep-Regel aus dem
15-Minuten-Chart (siehe [[Open Float & Liquidity Pools]]) — dort bestimmt stattdessen die
Measured-Move-Projektion selbst die relevante Distanz.

## Verwandt

- [[Fair Value Gap (FVG)]], [[Liquidity Void]], [[Order Block]]
- [[Open Float & Liquidity Pools]] — Stop-Liquidität an alten Hochs/Tiefs
- [[Turtle Soup]] — verwandtes Fehlausbruch-Konzept am Einzel-Extrem statt am Doppel-Extrem
- [[ICT Mentorship Core Content - Month 04 - Double Bottom Double Top (Source)]]
