---
tags: [concept, ict, trading-ict, risikomanagement, trade-management]
created: 2026-08-06
updated: 2026-08-06
sources: ["[[ICT Mentorship Core Content - Month 02 - How To Mitigate Losing Trades Effectively (Source)]]"]
---

# Verlust-Mitigation durch reduzierte Re-Entry-Size

Regel für den Umgang mit einem Stop-out auf einer HTF-Prämisse, die weiterhin gültig ist: **nicht
mit gleicher oder größerer Size erneut einsteigen, sondern mit der Hälfte der zuvor verlorenen
Size.**

## Ablauf

1. Trade wird gestoppt (z.B. voller 2-%-Verlust), die zugrunde liegende HTF-Prämisse (z.B. daily
   Bullish [[Order Block]]) ist aber weiterhin intakt — der Stop-out bedeutet nicht automatisch,
   dass die Idee falsch war, oft war nur der Stop zu eng platziert (siehe auch die
   Stop-out-Reentry-Ausnahme in [[PD Array]]).
2. Bildet sich ein **neuer Order Block** auf demselben Level (die vorherige Kerze wird durch eine
   neue down-/up-Kerze samt Preis-Durchhandeln bestätigt), erfolgt der Re-Entry dort — aber mit
   **halber Risiko-Size** des ursprünglichen Verlusts (2 % Verlust → 1 % Re-Entry-Risiko).
3. Sobald der Re-Entry **R2 erreicht** (mit der halbierten Size), ist der **ursprüngliche volle
   Verlust bereits vollständig ausgeglichen** — ohne dass mehr riskiert wurde als beim ersten
   Versuch verloren ging.
4. Ab R2: Stop auf Breakeven-plus nachziehen, sodass der wiederhergestellte Ausgangs-Equity-Stand
   nicht mehr unterschritten werden kann. Bei Erreichen von R2 spätestens **spät in der
   Handelswoche (Donnerstag/Freitag) die Position glattstellen** — nicht mit einem
   Netto-Wochenverlust ins Wochenende gehen, wenn der Markt die Gelegenheit zum Ausgleich bietet.
5. Erst in einer späteren Entwicklungsstufe (mehr Erfahrung): nach R2 nicht mehr zwingend
   schließen, sondern nur den Stop sichern und der Position weiteren Raum geben.

## Kernprinzip: Equity-Preservation vor Recovery-Drang

> "Equity preservation is the number one rule in this game."

Nach einem Verlust die Size zu **erhöhen**, um ihn schneller zurückzuholen, wird explizit als
Fehler benannt — ein einzelner Verlust kann der Beginn einer längeren Verlustserie sein, das weiß
man im Moment des Stop-outs nicht. Die Reduktion der Size (statt Erhöhung) ist der Hebel, der den
Verlust ohne zusätzliches Risiko wieder ausgleicht.

## Numerisches Beispiel aus der Quelle

- Erster Versuch: 2 % Risiko, Stop bei zu engem Mean-Threshold-Level, volle 2 % verloren.
- Re-Entry: 1 % Risiko am neuen Order Block.
- R1 (1 % Gewinn) → hälftig ausgeglichen. R2 (2 % Gewinn) → voll ausgeglichen, neue Equity-High
  erreicht, alles in **derselben ursprünglichen Trade-Idee**.

## Verwandt

- [[Order Block]], [[PD Array]]
- [[Risikomanagement (1% pro Trade)]]
- [[Erwartungswert & Reward-to-Risk-Modell]]
