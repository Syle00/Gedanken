---
tags: [concept, algo-methodology, market-structure]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[Quantifying Market Structure at Multiple Scales for Algorithmic Trading with Python (Source)]]"]
---

# Directional Change & Hierarchische Marktstruktur

Algorithmische Methode, um Swing-Hochs/-Tiefs objektiv und ATR-adaptiv zu finden (Directional
Change) und sie anschließend rekursiv in Signifikanz-Levels zu gruppieren (hierarchische
Marktstruktur) — ohne für jede Zeitskala einen eigenen festen Lookback-Parameter zu brauchen. Aus
[[Quantifying Market Structure at Multiple Scales for Algorithmic Trading with Python (Source)]]
(neurotrader, nach Larry Williams' *Long-Term Secrets to Short-Term Trading*).

## Directional Change (Basis-Level, "Level 0")

Findet alternierende Extreme direkt aus OHLC-Daten:

1. In einer laufenden Aufwärtsbewegung wird der bisher höchste gesehene Preis als "pending top"
   mitgeführt und bei jedem neuen Höchstwert aktualisiert.
2. Der pending top gilt als **bestätigt**, sobald der Preis unter eine ATR-basierte Schwelle
   fällt: `pending_top − ATR(lookback)`. Symmetrisch für pending bottoms:
   `pending_bottom + ATR(lookback)`.
3. Nach Bestätigung eines Tops beginnt symmetrisch die Suche nach dem nächsten Bottom, usw. —
   Extreme alternieren zwangsläufig Top/Bottom/Top/Bottom.

Wichtig: ein Extrem ist erst **rückblickend** bekannt (braucht die Bestätigungs-Kerze danach) —
Index/Zeitstempel des Extrems selbst und Index/Zeitstempel seiner Bestätigung werden getrennt
gespeichert. Die ATR-Schwelle macht die Empfindlichkeit automatisch volatilitätsadaptiv, ohne
Timeframe-spezifische Kalibrierung. Empfehlung des Autors: Lookback grob nach gesundem
Menschenverstand wählen (z.B. 24h bei 1-Minuten-Daten), nicht optimieren.

## Hierarchische Levels (rekursiv)

Level-0-Extreme werden zu Level-1 hochgestuft, wenn ein Top niedriger ist als sein Vorgänger-Top
UND höher als das zuletzt bestätigte höhere Extrem (symmetrisch für Bottoms) — dieselbe Regel
lässt sich beliebig oft auf die jeweils nächste Ebene anwenden (Level 1 → Level 2 → …).

- **Alternierung bleibt auf jedem Level erzwungen**: entstehen zwei hochgestufte Tops in Folge
  ohne dazwischenliegenden hochgestuften Bottom, wird der niedrigste Bottom zwischen ihnen
  nachträglich mit hochgestuft.
- **Höhere Levels = strukturell bedeutsamer, aber mit mehr Bestätigungs-Verzögerung.** Ein
  Level-2-Extrem braucht sichtbar mehr nachfolgende Kerzen, bis es feststeht, als ein
  Level-0-Extrem.
- Kein Repaint: einmal bestätigt, bleibt ein Extrem fix, wird nie nachträglich verschoben.

## Bezug zu diesem Projekt

Direkt anschlussfähig an [[Market Structure Shift (MSS)]] und die bestehenden
Struktur-Break-/Swing-Detektoren in `tools/analyze_ohlc.py`, die aktuell mit fester
`min_age`/`confirm`-Skalierung je Timeframe arbeiten statt einer ATR-adaptiven Schwelle (siehe
`algo/PLAN.md`-Log 2026-08-03). Diese Methode liefert eine mögliche, objektiv parametrisierte
Alternative/Ergänzung dafür — insbesondere um "welcher Swing zählt als MSS-Referenzpunkt" nicht
implizit über den gewählten Timeframe, sondern explizit über eine hierarchische
Signifikanz-Stufe zu entscheiden. Kein akuter Backlog-Punkt, aber ein Kandidat für die nächste
Überarbeitung der Struktur-Detektoren.
