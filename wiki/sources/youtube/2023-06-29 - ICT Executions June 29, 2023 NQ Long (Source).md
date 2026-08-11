---
tags: [source, youtube, ict, ict-executions, trade-example, macro, breaker, org, nq]
created: 2026-08-11
updated: 2026-08-11
sources: ["https://www.youtube.com/watch?v=UjiUidVS4xI"]
---

# ICT Executions June 29, 2023 NQ Long (Source)

Quelle: https://www.youtube.com/watch?v=UjiUidVS4xI
Kanal: ICT Gems (Executions-Reihe) | Veröffentlicht: 2023-06-29 | Länge: 2:15

> Kein Voiceover — reine Chart-Aufzeichnung, 1-Min-Chart NQ. Analyse basiert auf visueller
> Auswertung extrahierter Frames (alle 3s, ffmpeg).

## Trade-Ablauf (visuell rekonstruiert)

1. **Ziel**: *"Opening Range Gap Portion Remaining Undelivered"* — ORG-Rest, der noch nicht
   gefüllt/geliefert wurde, als übergeordnetes Ziel.
2. **Prognose-Annotation**: *"Smooth Highs Will Be Made 'Jagged'..."* und *"Typically it creates
   a sudden spike higher on a single or small number of candlesticks"* — beschreibt das erwartete
   Lieferverhalten (abrupter Spike statt allmählichem Anstieg).
3. **Entry-Zeitfenster explizit benannt**: **"10:50 to 11:10 Macro"** — Entry in einer
   **+Breaker**-Zone innerhalb dieses Fensters, nach vorangegangenem Sellside-Sweep.

![[ict-exec-UjiUidVS4xI-1050-macro.png]]
*"10:50 to 11:10 Macro"-Fenster explizit im Chart benannt, Entry im +Breaker nach
Sellside-Sweep, ORG-Restlieferung als Ziel.*

## Kernaussagen (trading-relevant, gefiltert)

- Bestätigt ein **zusätzliches stündliches Macro-Fenster (10:50–11:10 ET)** direkt aus einer
  Primärquelle — deckt sich mit der generischen `:50–:10`-Regel in `algo/macro_db.py`
  (`N_HOURS`-Schleife), die dieses Fenster bereits algorithmisch für jede Handelsstunde erzeugt;
  kein Code-Änderungsbedarf, aber zusätzliche Primärquellen-Bestätigung.
- Konkrete Beschreibung des **"Jagged Spike"-Liefermusters**: ICT beschreibt explizit, dass
  Ziel-Level oft durch einen einzelnen abrupten Kerzenspike statt einer allmählichen Bewegung
  erreicht werden — relevant für Backtest-Annahmen zu Fill-Wahrscheinlichkeit/-Geschwindigkeit.

## Bewusst ausgefiltert

- Nichts weiter — Video enthält keine Off-Topic-Inhalte (rein Chart, kein Voiceover).

## Verwandt

- [[ORG (Opening Range Gap) & 1st Presented FVG]]
- [[Breaker Block]]
- [[2023-07-07 - ICT Executions July 7, 2023 NQ Long (Source)]]
