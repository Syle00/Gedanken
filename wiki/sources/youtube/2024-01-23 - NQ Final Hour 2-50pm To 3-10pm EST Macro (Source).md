---
tags: [source, youtube, ict, ict-executions, trade-example, macro, nq]
created: 2026-08-11
updated: 2026-08-11
sources: ["https://www.youtube.com/watch?v=rn32EntwGCs"]
---

# NQ Final Hour 2:50pm To 3:10pm EST Macro - January 23, 2024 (Source)

Quelle: https://www.youtube.com/watch?v=rn32EntwGCs
Kanal: ICT Gems (Executions-Reihe) | Veröffentlicht: 2024-01-23 | Länge: 5:01

> Kein Voiceover — reine Chart-Aufzeichnung, 15-Sek-Chart NQ (Mar 2024). Analyse basiert auf
> visueller Stichprobenauswertung extrahierter Frames (alle 4s, ~75 Frames, nur punktuell
> geprüft).

## Trade-Ablauf (visuell rekonstruiert, Stichprobe)

1. **Zeitfenster explizit benannt**: rotes Banner **"2:50pm To 3:10pm Macro"** — deckt sich mit
   der generischen `:50–:10`-Stundenregel in `algo/macro_db.py` für die 15:00-Stunde (kein
   Last-Hour-Sonderfall, da vor 15:00 ET).
2. **Cross-Session-Kontinuität**: Annotation *"Buyside Liquidity I mentioned during this
   morning's Livestream"* — ein am Morgen in einem separaten Live-Stream genanntes Level wird am
   Nachmittag im Executions-Clip wiederverwendet.

![[ict-exec-rn32EntwGCs-final-hour-macro.png]]
*"2:50pm To 3:10pm Macro"-Fenster, Referenz auf ein morgens im Livestream genanntes
Buyside-Liquidity-Level.*

## Kernaussagen (trading-relevant, gefiltert)

- Weitere Primärquellen-Bestätigung des generischen `:50–:10`-Stundenmacros, hier für die
  14:xx-Stunde — kein Code-Änderungsbedarf.
- Zeigt, dass **Levels über den Handelstag hinweg session-übergreifend im Blick behalten
  werden** (morgens genanntes Level wird nachmittags gehandelt) — relevant für die
  Layer-0-Anforderung, die volle Tagesrange statt nur kurzfristiger Fenster zu betrachten.

## Bewusst ausgefiltert

- Aufgrund der Videolänge nur stichprobenartig geprüft.

## Verwandt

- [[Market on Close (MOC) Macro Model]]
- [[ICT Macros & Leading Candles]]
