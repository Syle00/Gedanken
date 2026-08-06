---
tags: [source, ict, trading-ict]
created: 2026-08-01
updated: 2026-08-06
raw: "[[Institutional Order Flow]]"
raw_path: "raw/trading-ict/Core Content/Institutional Order Flow.md"
curriculum: "[[Month 03 (Source)]]"
video: "https://www.youtube.com/watch?v=PQkcFbr61FI"
video_transcript: "raw/trading-ict/2016/yt-PQkcFbr61FI-transcript.md"
---

# Institutional Order Flow (Source)

Quelle zu [[Institutional Order Flow (Body vs Wick)]]: Volumen steckt in Candle Bodys, nicht Wicks.

## Extrahierte Seiten

- [[Institutional Order Flow (Body vs Wick)]]

## Bilder aus der Rohquelle

![[image 18.png]]
*Institutional Order Flow sucht das Maximum der Liquidität — die Haupt-Liq liegt bereits in den
Candle-Bodys (dort steckt das Volumen), daher läuft der Run nicht zwingend über die Wicks; Wicks
dürfen einen OB nicht komplett überschießen, sonst muss auf CISD/Shift geachtet werden.*

![[image 19.png]]
*Nach genommener Sellside liegt die nächste Liquidität logischerweise auf der Buyside — hier
bilden starke Order Blocks die Grenze.*

![[image 20.png]]
*Fokus liegt auf den Candle-Bodys, nicht den Wicks — in den Bodys steckt das institutionelle
Volumen.*

![[5FD03C65-470D-42BE-925B-86A325863CFA.png]]
*Sellside wird inklusive der Wicks genommen, aber die Bodys respektieren den bullishen OB — der
Blick wandert zur Buyside, zusätzlich wird die Discount-PD (bullisher OB) respektiert.*

![[DCD7BD7A-9F2B-43B0-B61E-B72363979EDE.png]]
*Back-and-forth-Prinzip: hin und her, sobald Liquidität und eine PD Array (oder die
gegensätzliche Liquidität) genommen wurden.*

![[B5AE9E5B-D647-4111-B879-9424023E8B18.png]]
*Weiteres Chart-Beispiel zum Back-and-forth zwischen Liquidität und PD Array.*

![[6015F9B4-3C62-4641-BB9B-45F2B4F9D3CA.png]]
*Drittes Chart-Beispiel zum Back-and-forth-Prinzip.*

## Ergänzung aus dem Begleitvideo (YouTube)

Das [Begleitvideo](https://www.youtube.com/watch?v=PQkcFbr61FI) (30 Min., vollständig transkribiert:
`raw/trading-ict/2016/yt-PQkcFbr61FI-transcript.md`) führt die Body-vs-Wick-Regel an einem
durchgehenden EURUSD-Beispiel von Monthly über Weekly bis Daily vor und ergänzt zwei Punkte, die in
der knappen Notion-Notiz fehlten:

- **Hedge-Book-Mechanik**: Eine Bank hält gleichzeitig Long- und Short-Positionen ("hedged") und
  bewegt Preis, um das eine Buch zu füllen, ohne das andere sofort zu räumen — ein scharfer
  Umkehr-Wick nach einem Order-Block-Retest ist oft das **Glattstellen der Gegenpositionen**
  (Unwinding), nicht ein neues Signal. Sichtbar z.B. daran, dass ein Wick knapp unter die Open-Mitte
  einer Kerze zurückläuft, um dort aufgebaute Shorts zu mitigieren, bevor die Rally weitergeht.
- Genau dieses Wick-zu-Body-Retracement-Muster (Preis kehrt vom Hoch nur bis zur Kerzenmitte/zum
  Body zurück, um Gegenpositionen zu mitigieren, statt den ganzen Block zu retracen) ist im Video
  wortwörtlich als **Mitigation Block** benannt — deckt sich mit [[Mitigation Block]], dort aber ohne
  die Hedge-Book-Begründung dokumentiert.

## Verwandt

- [[Institutional Order Flow (Body vs Wick)]]
- [[Mitigation Block]], [[Order Block]]
