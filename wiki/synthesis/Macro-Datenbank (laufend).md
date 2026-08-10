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

## Expansion je Fenster

![[macro-db-expansion.png]]
*Expansionsquote je Macro-Fenster mit 95%-Wilson-Intervall. Rote Linie: Basisrate über alle Fenster.*

## Wann setzt der Move ein?

![[macro-db-timing.png]]
*Minute im 20-Minuten-Fenster, in der der Move einsetzt — definiert als das Extrem entgegen der Netto-Richtung.*

## Liquidität im Fenster genommen

![[macro-db-level.png]]
*Anteil der Fenster, in denen ein vor dem Fenster offenes Swing-Level genommen wurde.*

## Vorbehalte

- Die Stichprobe ist klein: rund 20 Tage je Fenster. Aussagen auf
  **Fenster-Ebene** sind noch nicht belastbar, Aussagen auf **Bedingungs-Ebene**
  über alle Fenster hinweg früher.
- Fenster desselben Handelstags sind nicht unabhängig — p-Werte sind optimistisch.
- Das Fenster **23:50** fehlt fast vollständig (Exportlücke 23:59–00:08), **16:50**
  ganz (ragt über den Sessionschluss 17:00 hinaus).
- NDOG/NWOG/ORG sind noch keine Level-Quelle (Kalendertag- statt Session-Logik,
  siehe `algo/PLAN.md`).

## Verwandt

- [[ICT Macros & Leading Candles]]
- [[Muster-Validierung (laufend)]]
