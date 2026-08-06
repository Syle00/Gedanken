---
tags: [source, ict, trading-ict]
created: 2026-08-01
updated: 2026-08-06
raw: "[[Quarterly Shifts & IPDA Data Ranges]]"
raw_path: "raw/trading-ict/Core Content/Quarterly Shifts & IPDA Data Ranges.md"
curriculum: "[[Month 05 (Source)]]"
video: "https://www.youtube.com/watch?v=n7SPAK_tpN8"
video_transcript: "raw/trading-ict/2017/yt-n7SPAK_tpN8-transcript.md"
---

# Quarterly Shifts & IPDA Data Ranges (Source)

Kernquelle zu [[Quarterly Shift]]: Underlying/Benchmark-Terminologie, Marker-Methodik,
3-4-Monats-Rhythmus.

## Extrahierte Seiten

- [[Quarterly Shift]] (aktualisiert)

## Bilder aus der Rohquelle

![[image 47.png]]
*Marker-Setzung nach Trading-Monaten: bei Shift im November zurück zum 1. Oktober als erster
Marker.*

![[image 48.png]]
*Weiteres Beispiel zur Marker-Methodik.*

![[image 49.png]]
*USDX Daily über ein Jahr: alle 4 Monate ein markanter Shift.*

![[image 50.png]]
*1 Trading-Tag pro Monat als Lookback-Bezugspunkt für 60/40/20-Tage-Fenster.*

![[image 51.png]]
*Weiteres Beispiel zum Lookback-Fenster.*

![[image 52.png]]
*Lookback zeigt anhaltend bullishen Kontext mit Shift — Liquidität liegt unter der Sellside.*

![[image 53.png]]
*Gleiche Methode vorwärts angewendet (Forward-Projektion).*

## Ergänzung aus dem Begleitvideo (YouTube)

Video: [ICT Mentorship Core Content - Month 05 - Quarterly Shifts & IPDA Data Ranges](https://www.youtube.com/watch?v=n7SPAK_tpN8)
(2017er Mentorship-Lektion 1.1, Transkript: `raw/trading-ict/2017/yt-n7SPAK_tpN8-transcript.md`).
Das Video liefert deutlich mehr Kontext als die Notion-Notiz und ergänzt zwei genuin neue Punkte:

- **Marker-Regel präzisiert**: Der Marker wird nicht auf den aktuellen Monat gesetzt, sondern auf
  den ersten Handelstag des **zuletzt vollständig abgeschlossenen Kalendermonats**. Beispiel aus dem
  Video: wer die Analyse im November macht, setzt den Marker auf den 1. Oktober.
- **Cast Forward (neu)**: Nach dem Lookback (60/40/20 Handelstage zurück) wird symmetrisch nach
  vorne projiziert — 20/40/60 Handelstage rechts vom Marker als Zeitfenster, in dem der nächste
  Quarterly Shift erwartet wird. Faustregel: lag der letzte Shift bereits 40 Tage zurück, wird nur
  noch 20 Tage weiter nach vorn projiziert (Summe bleibt bei ~60 Handelstagen). Details siehe
  [[Quarterly Shift]].
- **Buy/Sell-Program-Erkennung via Underlying/Benchmark-Divergenz**: eine eigenständige,
  SMT-artige Methode, um auf dem Daily-Chart zu erkennen, ob der Algorithmus gerade akkumuliert
  (Buy Program) oder distribuiert (Sell Program) — vier gespiegelte Bedingungspaare, die verglichen,
  ob Underlying und Benchmark beide ein neues Extrem (Higher High/Lower Low) bilden oder ob eines
  der beiden es verweigert (Turtle-Soup-Kontext). Ausführlich neu dokumentiert unter
  [[Buy & Sell Program]].

Konkretes Beispiel aus dem Video (USDX als Benchmark, EURUSD als Underlying, Dez 2015–2017):
Nach einem bearishen Quarterly Shift am 1.12.2015 lag das nächste bedeutende Hoch im EURUSD exakt
auf der 60-Tage-Cast-Forward-Marke — als Beleg dafür, dass die 20/40/60-Fenster nicht nur rückwärts,
sondern auch vorwärts zur Zeitprognose taugen.
