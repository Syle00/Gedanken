---
tags: [concept, ict, trading-ict, trade-management]
created: 2026-08-06
updated: 2026-08-11
sources: ["[[ICT Mentorship Core Content - Month 02 - How Traders Make 10% Per Month (Source)]]", "[[2026-08-10 - Navigating High Resistance Liquidity Run Conditions (Source)|Navigating High Resistance Liquidity Run Conditions (Source)]]", "[[2024-10-03 - ICT Executions October 3, 2024 NQ Short (Source)]]", "[[2024-09-23 - ICT Executions September 23, 2024 NQ Long (Source)]]", "[[2024-09-13 - ICT Executions September 13, 2024 NQ Short Silver Bullet (Source)]]", "[[2024-09-11 - ICT Executions September 11, 2024 NQ Long MOC Macro (Source)]]", "[[2023-01-12 - ICT Executions January 12, 2023 ES Short Last Hour Setup (Source)]]", "[[2023-02-01 - ICT Executions February 1, 2023 ES Short (Source)]]"]
---

# Partial Profit-Taking & R-Multiple-Skalierung

Regel: **beim ersten Erreichen eines 3:1-Reward-to-Risk-Multiples einen Teil der Position
realisieren ("pay the trader")**, den Rest ohne Zeitdruck auf das nächste, höhere
HTF-Liquiditätsziel laufen lassen.

## Warum das kein Kompromiss ist

ICT stellt sich explizit gegen "All-or-nothing"-Exit-Philosophien: wer immer die volle Position
bis zum finalen Ziel hält, hat oft genug erlebt, wie ein großer offener Gewinn wieder komplett
zurückläuft oder sogar in einen Verlust dreht. Ein realisierter Teilgewinn ist **kein Zeichen von
Schwäche**, sondern reduziert das psychologische Risiko und lässt den Rest der Position "mit dem
Geld des Marktes" laufen.

> "The second portion of the trade will always make more than the first" — weil sie bereits
> risikoreduziert (oft auf Breakeven gesichert) weiterläuft, ohne dass man das Gesamtergebnis
> vorzeitig kappen muss.

## Konkretes Skalierungsbeispiel

Ausgangsposition: 2 % Kontorisiko.

1. **Erste Hälfte (1 % Risiko-Anteil) bei 3R schließen** → 3 % Kontogewinn realisiert.
2. **Zweite Hälfte (verbleibendes 1 % Risiko-Anteil) laufen lassen** Richtung nächster,
   höherer Liquiditätsstufe (im Beispiel: 15M-Buy-Stops, dann 1H-Buy-Stops) — kann auf **9R bis
   15R** anwachsen, weil dieselbe HTF-Prämisse (institutionelle Order-Flow-Richtung) weiterhin
   gilt.
3. Ergebnis in der Beispielrechnung: **>10 % Monatsrendite allein aus dem zweiten Positionsteil**,
   zusätzlich zu den 3 % aus dem ersten Teil — auch wenn nur die Hälfte der potenziellen Range
   (statt des vollen Zielbereichs) erreicht wird.

## Stop-Order auf Teilposition als Retracement-Partial (Live-Trade 2026-08-10)

Aus
[[2026-08-10 - Navigating High Resistance Liquidity Run Conditions (Source)|Navigating High Resistance Liquidity Run Conditions (Source)]]
— die Spiegelvariante zum Partial nach oben: Ein Partial lässt sich auch **gegen** die eigene
Richtung als Stop-Order platzieren, wenn die Fortsetzung fraglich wird.

- Umsetzung: 7 Kontrakte long, davon **2 mit eigenem Stop** knapp unter den zuletzt verteidigten
  Wick; die restlichen 5 behalten den weiteren Stop unter dem Swing Low.
- Bricht Preis den Wick, werden nur die 2 verkauft — *"it's kind of like taking a partial on a
  retracement"*. Ausdrücklich **nicht** die ideale Seite der Kurve (ideal wäre ein Limit über
  Markt bei bullisher Position), aber besser als die volle Position auf den Endstop laufen zu
  lassen.
- Drei Effekte: (1) realisierter Gewinn statt Buchgewinn, (2) mentale Entlastung — der Zwang,
  Recht zu behalten, fällt weg, (3) **Information**: löst der Teilstop aus und folgt danach ein
  Close unter dem Gap, ist der volle Rücklauf wahrscheinlich und der Reststop darf laufen.
- Vorher: erstes Partial von **5 aus 12** Kontrakten knapp unter dem Midnight Opening Price. Danach
  gilt der Trade als erledigt — *"it doesn't make a difference to me because it's done what I hoped
  it would do"*; der Rest ist ein "free look" auf höhere Preise.
- Grundhaltung dahinter: *"If you don't allow the trades that you're part of pay by any means
  necessary, you're not trading, you're gambling."* — Partials sind kein Verzicht, sondern das
  Zulassen, dass die Idee anders als geplant aufgehen darf.

## Kontraktbasierte Skalierung statt SL-Nachziehen (ICT-Executions-Beispiele, 2024)

Aus der chart-only [[2024-10-03 - ICT Executions October 3, 2024 NQ Short (Source)|ICT-Executions-Reihe]]
(keine Sprachspur, reine Order-Panel-Auswertung): In mehreren Beispielen wird Risiko **nicht**
über SL-Wanderung reduziert, sondern rein über gestaffelte Teilverkäufe der Kontraktzahl:

- **2024-10-03 (NQ Short, Lunch Macro)**: Entry 2 Kontrakte in einer FVG → Partial 1 (4 von
  ursprünglich mehr Kontrakten) bei ~46 Punkten, Partial 2 bei ~69 Punkten, Rest läuft bis zur
  **Weekly BSL Consequent Encroachment**. Stop bleibt sichtbar unverändert, nur die Positionsgröße
  schrumpft.
- **2024-09-23 (NQ Long, Macro)**: Entry an der 0,5-CE-Linie einer **+IFVG**
  ([[IFVG (Inverse Fair Value Gap)]]), 1/Rest-Split: 1 Kontrakt bei +580 USD gesichert, Rest läuft
  mit sichtbarem Buchgewinn +710 USD weiter.
- **2024-09-13 (NQ Short, Silver Bullet)**: mit 18 Kontrakten deutlich größere Positionsgröße als
  bei den Macro-Setups — offene Hypothese, dass Silver-Bullet-Entries hier mit höherer Konfidenz
  (mehr Kontrakten) gehandelt werden als reine Macro-Fenster-Entries; noch nicht über mehrere
  Videos verifiziert.

## Pyramiding als Gegenstück (ICT Executions, Batch 2)

Aus [[2024-09-11 - ICT Executions September 11, 2024 NQ Long MOC Macro (Source)]]: statt Kontrakte
zu reduzieren, wird hier **in eine bestätigte Trendrichtung hinein aufgestockt** — 3 Adds während
des MOC-Macro-Fensters (10 → 20 → 30 → 40 Kontrakte), Buchgewinn wächst auf +60.050 USD. Zeigt,
dass die R-Skalierungslogik in beide Richtungen gilt: reduzieren bei erreichtem Ziel, aufstocken
bei bestätigter Prämisse — nicht nur eine der beiden Varianten ist "die" ICT-Methode.

Zwei weitere Partial-Beispiele aus demselben Batch:
- [[2023-01-12 - ICT Executions January 12, 2023 ES Short Last Hour Setup (Source)]]: Partial
  explizit **innerhalb** der Ziel-FVG genommen ("1st Partial Profit In This FVG") — die FVG selbst
  ist der Skalierungspunkt, nicht ein davon unabhängiges Punkteziel.
- [[2023-02-01 - ICT Executions February 1, 2023 ES Short (Source)]]: Partial-Level liegt
  **unterhalb** einer New Week Opening Gap-Range ("Partial Opportunity Here"), nicht am
  NWOG-Rand selbst.

## Terminologie-Bestätigung aus Primärquellen (Batch 10-12)

[[2024-04-08 - April 08, 2024 NQ Market Maker Buy Model Example (Source)]] liefert den
Fachbegriff **"Risk Removed"** für die Stop-auf-Breakeven-Verschiebung nach dem ersten Teilziel.
[[2024-02-01 - NQ Futures Live Execution Pre-Opening Bell (Source)]] bestätigt live eingetippt den
Begriff **"Pyramided"** ("Pyramided 5 more at...") für das Kontrakt-Aufstockungsmuster —
[[2023-12-27 - NQ Live Execution Turtle Soup Short (Source)]] ergänzt **"Funded"** ("Trade is
'Funded' and locked in profit...") für dieselbe Risikofreistellungs-Idee, und
[[2023-12-06 - Why Do I Avoid NFP Weeks NQ 3 Trades 2 Losses (Source)]] zeigt, dass der
Breakeven-Stop explizit **"Risk & Costs"** (nicht nur Punkte-Risiko, sondern auch
Kommissionen/Spread) abdecken soll — alle vier Begriffe stammen direkt aus ICTs eigener
Chart-Beschriftung, nicht aus Ableitung.

## Runner statt vollständiger Glattstellung (Live-Beispiel)

[[2023-12-14 - Fading Retail Buyers For NQ (Source)]]: nach dem Hauptexit bleibt bewusst **ein
einzelner Kontrakt** offen ("I am leaving a single contract on in case it runs...") als
kostengünstiger "Lottery-Ticket"-Runner auf eine größere Fortsetzung — eine dritte Variante neben
"kompletter Exit" und "R-Multiple-Skalierung auf 2 Teile".

## Bezug zum Reward-to-Risk-Modell

Baut direkt auf [[Erwartungswert & Reward-to-Risk-Modell]] auf: das erste Partial bei 3:1 sichert
bereits die Mindestschwelle für Profitabilität ab (siehe dortige Break-even-Tabelle bei
niedriger Trefferquote); alles danach ist zusätzlicher Ertrag ohne zusätzliches Risiko.

## Verwandt

- [[Missed Entry Trade Management Playbook]] — konkreteres 2026er-Skalierungs-/Exit-Schema
  (CISD-Reentry, Event-Horizon-Exits); dieses Konzept liefert die grundsätzlichere
  R-Multiple-Logik dahinter.
- [[Silver Bullet Model]] — Trade-Management-Abschnitt dort nutzt ein festes Punktziel statt
  R-Multiples; beide Ansätze sind laut CLAUDE.md-Konvention nicht deckungsgleich, sondern
  ergänzend (fixe Mindestziel-Regel für dieses konkrete Modell vs. allgemeine R-Skalierung).
- [[Event Horizon]]
- [[Erwartungswert & Reward-to-Risk-Modell]]
- [[Risiko-Verfeinerung über Timeframes]]
