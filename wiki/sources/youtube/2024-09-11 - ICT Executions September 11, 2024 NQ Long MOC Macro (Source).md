---
tags: [source, youtube, ict, ict-executions, trade-example, macro, nq, moc]
created: 2026-08-11
updated: 2026-08-11
sources: ["https://www.youtube.com/watch?v=hI3JEJcRtSs"]
---

# ICT Executions September 11, 2024 NQ Long | MOC Macro (Source)

Quelle: https://www.youtube.com/watch?v=hI3JEJcRtSs
Kanal: ICT Gems (Executions-Reihe) | Veröffentlicht: 2024-09-11 | Länge: 1:00

> Kein Voiceover — reine Chart-Aufzeichnung, 1-Min-Chart NQ (Sep 2024). Analyse basiert auf
> visueller Auswertung extrahierter Frames (alle 3s, ffmpeg).

## Trade-Ablauf (visuell rekonstruiert)

1. **Zeitfenster im Chart selbst annotiert**: rotes Rechteck **"3:15pm – 3:45pm Macro"** — deckt
   sich mit dem in `algo/macro_db.py`/[[Market on Close (MOC) Macro Model]] hinterlegten
   Final-Hour-Fenster (15:15–15:45 ET), hier direkt aus einer Primärquelle bestätigt.
2. **Setup**: Sellside-Liquidity wird kurz vor dem Macro-Fenster geraidet ("Sellside Raided"),
   Text-Annotation "Retail Wants To Short..." markiert den erwarteten Retail-Fehler (Short in
   einen bullishen Kontext hinein).
3. **Entry**: Long-Einstieg **in einem Order Block** (Label "+OB") mit drei gestaffelten Adds:
   Buy 10 @ 19.152,25 / Buy 10 @ 19.152,75 / Buy 10 @ 19.159,50 → weiterer Add Buy 10 @ 19.173,50.
4. **Pyramiding statt reinem Partial-Exit**: Position wächst von 10 auf 40 Kontrakte während der
   Bewegung nach oben, sichtbarer Buchgewinn erreicht +60.050 USD auf den letzten 10 Kontrakten.

![[ict-exec-hI3JEJcRtSs-buildup.png]]
*Erster Teil des Aufbaus: 30 von später 40 Kontrakten, Order Block unten mit drei gestaffelten
Buy-Fills.*

![[ict-exec-hI3JEJcRtSs-macro-window.png]]
*Volle Sequenz mit explizit im Chart eingezeichnetem "3:15pm – 3:45pm Macro"-Fenster,
"Sellside Raided"-Annotation vor dem Anstieg.*

## Kernaussagen (trading-relevant, gefiltert)

- Primärquellen-Bestätigung des MOC-Fensters **15:15–15:45 ET** direkt aus einer
  Original-Chart-Annotation — stützt die bestehende Regel in
  [[Market on Close (MOC) Macro Model]] zusätzlich zur Transkript-Quelle
  `yt-VH7Dh1OONj4-transcript.md`.
- Neues Trade-Management-Muster: **Pyramiding (Adds in Trendrichtung)** statt Partial-Exit — im
  Gegensatz zu den Batch-1-Beispielen, wo Kontrakte reduziert wurden. Ergänzt
  [[Partial Profit-Taking & R-Multiple-Skalierung]] um die Gegenrichtung (Risiko/Größe erhöhen
  statt reduzieren, wenn die Prämisse bestätigt wird).

## Bewusst ausgefiltert

- Nichts — Video enthält keine Off-Topic-Inhalte (rein Chart, kein Voiceover).

## Verwandt

- [[Market on Close (MOC) Macro Model]]
- [[Order Block]]
- [[Partial Profit-Taking & R-Multiple-Skalierung]]
