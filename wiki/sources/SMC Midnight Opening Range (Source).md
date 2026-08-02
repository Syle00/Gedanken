---
tags: [source, ict, trading-ict, lecture-2025, sessions, london, fvg]
created: 2026-08-02
updated: 2026-08-02
raw: "[[SMC Midnight Opening Range]]"
raw_path: "raw/trading-ict/ICT 2025 Lecture Series/SMC Midnight Opening Range.md"
curriculum: "[[ICT 2025 Lecture Series (Source)]]"
---

# SMC Midnight Opening Range (Source)

Die inhaltlich folgenreichste Seite der Reihe: sie definiert die **Midnight Opening Range** und
formuliert die **Auswahlregel für das 1. presented FVG** so deutlich wie keine andere Quelle im Vault.

## Kernpunkte

- Alles im **ETH-Chart**, **NY local time**. Midnight Opening Range = **0:00 bis 0:30**.
- High und Low mit **Fib** markieren (Wicks mitnehmen), zusätzlich das **0-Uhr-Opening** einzeichnen.
- Um Punkt 0 Uhr wird der **Algo zurückgesetzt**, der neue richtige Handelstag beginnt. Bereits
  **innerhalb der Range** wird das High/Low festgelegt, das in den meisten Fällen die **London
  Session** liefert.
- **Die Auswahlregel** — zweimal und ausdrücklich formuliert:

  > *„MERKE!! Nicht immer das erste FVG nehmen sondern schauen welches am größten ist!! Es heißt
  > also im Grunde nicht 1 presented FVG sondern 1. presented **Displacement** des Tages."*

  Im gezeigten Beispiel nimmt der Autor **das letzte FVG der Range** — es muss innerhalb der Range
  liegen, ausschlaggebend ist aber, dass es das **relevanteste und stärkste** ist.
- **Standard Deviations**: Fib über die Midnight Range legen, um das Daily High/Low zu antizipieren.
  Die STD-Level allein reichen nicht — sie müssen **mit Liq Pools und/oder FVG zusammenfallen**.
- Das STD-Verfahren funktioniert auch auf einem **einzelnen FVG** (−0,5 / −1). Gerade beim
  1. presented Displacement werden diese Level über die London Session hinweg respektiert.
- **3:30 ist der Sweetspot** der London Session — *„im Verbund mit SilverBullet ist crazy!!"*.
  Ein Beispiel zeigt einen Forex-Long zu dieser Zeit.

## Einordnung ins Wiki

Die Auswahlregel steht bislang im Wiki nur für die **PM-Session-ORG** („markantestes Displacement",
[[ORG (Opening Range Gap) & 1st Presented FVG]]) und implizit in der Sequenz-Regel der
[[Opening Range Theory - 1st Presented FVG Logic (Source)|Lektion 06]] („erstes *starkes*
Displacement, nicht jedes kleine Mini-FVG"). Diese Quelle **verallgemeinert sie** und benennt die
Umdeutung explizit: *1. presented Displacement* statt *1. presented FVG*.

## Extrahierte Seiten

- [[Midnight Opening Range]] (neu)
- [[ORG (Opening Range Gap) & 1st Presented FVG]] (aktualisiert)

## Bilder aus der Rohquelle

![[ICT 2025 - Midnight ORG 01.png]]
*Midnight Opening Range 0:00–0:30 mit Fib (0 / 0.25 / 0.5 / 1) und markiertem Midnight Open, NQ 1M.*

![[ICT 2025 - Midnight ORG 02.png]]
*Das gewählte FVG ist nicht das erste, sondern das stärkste der Range.*

![[ICT 2025 - Midnight ORG 03.png]]
*Standard Deviations auf das FVG angewandt (−0,5 / −1).*

![[ICT 2025 - Midnight ORG 04.png]]
![[ICT 2025 - Midnight ORG 05.png]]
*Weitere Beispiele zur STD-Projektion.*

![[ICT 2025 - Midnight ORG 06.png]]
*Forex-Long zum 3:30-Sweetspot in Kombination mit dem Silver Bullet.*

## Verwandt

- [[Midnight Opening Range]], [[ORG (Opening Range Gap) & 1st Presented FVG]]
- [[How To Disqualify 1st Presented FVGs (Source)]] — das Ausschlussverfahren als Gegenstück
- [[London Opening Range +1p FVG (Source)]] — dieselbe Range, Fokus auf STD-Manipulation
- [[Silver Bullet Model]], [[Fair Value Gap (FVG)]]
- [[ICT 2025 Lecture Series (Source)]]
