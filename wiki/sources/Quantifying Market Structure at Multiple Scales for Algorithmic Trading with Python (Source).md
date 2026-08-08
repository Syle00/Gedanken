---
tags: [source, algo-methodology, market-structure]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[Quantifying Market Structure at Multiple Scales for Algorithmic Trading with Python]]"]
---

# Quantifying Market Structure at Multiple Scales for Algorithmic Trading with Python

YouTube-Transkript, Kanal neurotrader (neurotrader888), veröffentlicht 2025-01-30,
[github.com/neurotrader888/market-structure](https://github.com/neurotrader888/market-structure).
Kein ICT/SMC-Material — algo-methodology-Domäne, wie
[[How I Develop Trading Strategies (Source)]]. Quelle: Larry Williams, *Long-Term Secrets to
Short-Term Trading* (Kapitel Market Structure) — Autor betont ausdrücklich, dass seine
Implementierung vom Buch abweicht, die Kernidee aber dieselbe ist.

## Zusammenfassung

Algorithmus, der Markt-Wendepunkte (Swing-Hoch/-Tief) rekursiv in hierarchische Signifikanz-Level
gruppiert: Level 0 = alle per Directional-Change-Algorithmus gefundenen Wendepunkte, Level 1 = nur
die davon "wichtigeren" (ein Top umgeben von zwei niedrigeren Tops usw.), Level 2 = dieselbe
Regel nochmal auf Level 1 angewendet, beliebig oft wiederholbar. Ergebnis: eine objektive,
parameterarme Methode, um Marktstruktur auf mehreren Zeitskalen gleichzeitig zu quantifizieren,
ohne für jede Skala einen eigenen Indikator/Lookback zu definieren.

## Kernpunkte

### Directional Change (Level 0)

- Findet alternierende Extreme (immer Top→Bottom→Top…) rein aus OHLC-Daten, kein fester
  Lookback für "was ist ein Swing" nötig.
- **Bestätigungsschwelle ist ATR-basiert, nicht ein fester Prozentsatz**: bei einem laufenden
  Aufwärtszug wird der bisher höchste Preis als "pending top" mitgeführt; sobald ein neuer Low
  unter `pending_top − ATR` fällt, gilt der pending top als bestätigt (symmetrisch für Bottoms:
  `pending_bottom + ATR`). ATR macht die Schwelle automatisch volatilitätsadaptiv statt eines
  starren Punkte-/Prozent-Werts.
- Wichtige Eigenschaft: ein Extrem gilt erst rückblickend als bestätigt (braucht die
  Bestätigungs-Kerze danach) — Konfirmations-Index/-Zeitstempel wird separat vom eigentlichen
  Extrem-Index gespeichert (relevant für Lookahead-Vermeidung bei jeder Implementierung).
- Praxis-Hinweis des Autors zum ATR-Lookback: "I wouldn't optimize the look back or think about
  it too much, just use common sense" — bewusst kein Optimierungsziel.

### Hierarchische Levels (Level 1, 2, 3, …)

- Ein Level-N-Top wird zum Level-(N+1)-Top hochgestuft, wenn er niedriger ist als der
  vorangehende Level-N-Top UND höher als der zuletzt bestätigte Level-(N+1)-Extrem (symmetrisch
  für Bottoms). Rekursive Regel, beliebig oft anwendbar — je höher das Level, desto weniger
  Punkte bleiben übrig, aber desto strukturell bedeutsamer sind sie.
- **Alternierungs-Zwang bleibt auf jedem Level erhalten**: entstehen zwei aufeinanderfolgende
  hochgestufte Tops ohne dazwischenliegenden hochgestuften Bottom, wird zwischen ihnen der
  niedrigste Bottom nachträglich mit hochgestuft, damit Top/Bottom weiter strikt alternieren.
  Bei exakten Gleichständen (echter Doppel-Top) gilt der zeitlich frühere Treffer als der
  hochzustufende.
- **Höhere Levels haben strukturell mehr Verzögerung** (Konfirmations-Lag) — ein Level-2-Extrem
  wird erst deutlich nach dem eigentlichen Hoch/Tief eingezeichnet, weil es mehr nachfolgende
  Level-1-Bestätigung braucht. Explizit im Video demonstriert (weißes Level 0 vs. blaues Level 1
  vs. violettes Level 2, gleicher Chart-Ausschnitt).
- Kein Redraw/Repaint: einmal bestätigt, bleibt ein Extrem unverändert stehen (kein
  nachträgliches Verschieben).

## Bezug zu diesem Projekt

Direkt anschlussfähig an [[Market Structure Shift (MSS)]] und die bestehenden
Struktur-Break-Detektoren in `tools/analyze_ohlc.py` (aktuell fester Lookback pro Timeframe statt
ATR-adaptiver Schwelle) — dieser Algorithmus liefert eine mögliche, objektiv parametrisierte
Grundlage für "welcher Swing ist strukturell bedeutsam genug, um als MSS-Referenzpunkt zu
zählen", statt das implizit über den Timeframe-Wechsel zu lösen. Kein akuter Backlog-Punkt (noch
keine konkrete Regel/Backtest daraus abgeleitet), aber ein naheliegender Kandidat, sobald die
bestehenden Struktur-Detektoren überarbeitet werden — insbesondere die aktuelle
`min_age`/`confirm`-Skalierung je Timeframe (siehe `algo/PLAN.md`-Log 2026-08-03) könnte durch
diese ATR-adaptive, timeframe-unabhängige Hierarchie ersetzt oder ergänzt werden.
