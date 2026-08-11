---
tags: [source, youtube, ict, ict-executions, trade-example, nfp, news, risk-management, nq]
created: 2026-08-11
updated: 2026-08-11
sources: ["https://www.youtube.com/watch?v=hMvyE0qhads"]
---

# Why Do I Avoid NFP Weeks? NQ 3 Trades \ 2 Losses \ December 06, 2023 (Source)

Quelle: https://www.youtube.com/watch?v=hMvyE0qhads
Kanal: ICT Gems (Executions-Reihe) | Veröffentlicht: 2023-12-06 | Länge: 18:51

> Kein Voiceover — reine Chart-Aufzeichnung, mit 18:51 eines der längsten Videos im Batch,
> NFP-Woche (Non-Farm Payroll). Analyse basiert auf visueller Stichprobenauswertung extrahierter
> Frames (alle 4s, ~283 Frames, nur punktuell geprüft).

## Trade-Ablauf (visuell rekonstruiert, Stichprobe)

1. **Selbstkritischer Titel**: "Why Do I Avoid NFP Weeks? NQ 3 Trades / 2 Losses" — seltenes
   Beispiel, das explizit **2 von 3 Verlust-Trades** in einer NFP-Woche dokumentiert statt nur
   Gewinner zu zeigen.
2. **PD Arrays kombiniert**: +Breaker, IFVG und Opening Range Gap in derselben Zone.
3. **Risikoterminologie**: *"1st Partial Profit Booked Above Breaker"* und *"Risk & Costs are
   covered with the Stop Loss moved..."* — der verschobene Stop deckt explizit nicht nur das
   Punkte-Risiko, sondern auch Kosten (Kommissionen/Spread).

![[ict-exec-hMvyE0qhads-risk-costs-covered.png]]
*"1st Partial Profit Booked Above Breaker" und "Risk & Costs are covered with the Stop Loss
moved..." — Kostenbewusstsein bei der SL-Verschiebung.*

## Kernaussagen (trading-relevant, gefiltert)

- **Wichtigster Fund im gesamten Batch**: explizite Bestätigung, dass NFP-Wochen laut ICT selbst
  ein erhöhtes Verlustrisiko bergen (2/3 Trades verloren) — direkte Primärquelle für die
  "NFP meiden"-These, die bereits in `algo/PLAN.md` als zu prüfende These vermerkt sein sollte.
- **"Risk & Costs" statt nur "Risk"** beim SL-Move: bestätigt, dass ICT selbst
  Kommissionen/Spread in die Breakeven-Berechnung einbezieht — deckt sich mit der
  `dubious_pct`/Commission-Sensitivität aus dem Backtest-Stack
  (siehe [[Ensemble-Strategie — Backtest-Ergebnis & Commission-Verzerrung (laufend)]]).

## Bewusst ausgefiltert

- Aufgrund der Videolänge nur stichprobenartig geprüft — die konkreten 3 Trades/2 Verluste sind
  nicht einzeln nachvollzogen, nur das Gesamtnarrativ.

## Bereits gebacktestet

`algo/backtest_nfp_week.py` (2026-08-11): NFP-Freitage zeigen 56% höhere Range als andere
Freitage, aber niedrigere statt höhere Whipsaw-Ratio — bestätigt "volatiler", nicht eindeutig
"choppier". n=6 zu klein für ein belastbares Ergebnis. Details:
[[Statistische Muster jenseits der ICT-Konzepte (laufend)]] Abschnitt 8.

## Verwandt

- [[Risikomanagement (1% pro Trade)]]
- [[Ensemble-Strategie — Backtest-Ergebnis & Commission-Verzerrung (laufend)]]
- [[Statistische Muster jenseits der ICT-Konzepte (laufend)]]
