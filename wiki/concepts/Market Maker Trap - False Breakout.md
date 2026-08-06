---
tags: [concept, ict, trading-ict, market-maker-trap, manipulation, liquidity]
created: 2026-08-06
updated: 2026-08-06
sources: ["[[ICT Mentorship Core Content - Month 02 - Market Maker Trap False Breakouts (Source)]]"]
---

# Market Maker Trap: False Breakout

Neophyten-/Breakout-Trader "bracketen" eine Konsolidierungs-Range mit Buy-Stops über dem alten
Hoch und Sell-Stops unter dem alten Tief, um egal in welche Richtung an einem Ausbruch beteiligt
zu sein. Market Maker nutzen genau diese beidseitig gestapelte Liquidität, treiben Preis aber
**nur auf eine Seite**, um dort gezielt Stops zu neutralisieren — nicht, weil ein echter
Trendausbruch beginnt.

## Grundmechanik (Beispiel: zugrunde liegend bullisher Markt)

1. Markt geht in eine Konsolidierung/Trading-Range.
2. Preis bricht **unter** die Range (false breakdown) — nimmt die Sell-Stops unterhalb ab.
3. Diese Sell-Stops sind für Smart Money die **Gegenpartei, um long zu gehen** (Sell-Stop-Ausführung
   = jemand verkauft an den Market Maker, der dadurch long wird).
4. Preis wird danach **oberhalb** der Range zu den dort liegenden Buy-Stops expandiert — dort
   liquidieren/hedgen die Longs (Buy-Stops = Gegenpartei für den Ausstieg der Long-Position).
5. Neue, höhere Konsolidierung entsteht — der gesamte Zyklus wiederholt sich auf höherem Niveau.

Bei einem zugrunde liegend **bearishen** Markt läuft alles spiegelverkehrt: false breakouts
**über** die Range neutralisieren Buy-Stops als Gegenpartei für neue Shorts, danach Expansion
**unter** die Range zu den Sell-Stops.

## Handlungsregel

> Jeder Bruch unter eine Konsolidierung in einem zugrunde liegend bullishen Markt ist als
> **False Breakout** zu behandeln — nicht als Beginn eines echten Abwärtstrends. Erwartung:
> Akkumulation von Long-Positionen, danach Repricing nach oben.

Spiegelbildlich für bearishe Märkte mit False Breakouts nach oben.

## Präzision der Measured-Move-Projektion

Aus dem Beispiel (Referenzpaar mit Preisen um 108–110): die Distanz vom False-Breakout-Tief zum
vorherigen Konsolidierungs-Hoch, projiziert auf das nächste Level, trifft wiederholt sehr präzise
das nächste Liquiditätsziel (z.B. Ausbruch unter 108,55 → Projektion trifft 109,40/109,45;
Ausbruch unter 108,85 → Projektion trifft 109,80/109,90 — dort deckt es sich zusätzlich mit einem
Daily Bearish Order Block).

## Verwandt

- [[Turtle Soup]] — dieselbe Grundmechanik auf **einem** Level; False Breakout beschreibt sie auf
  Ebene einer ganzen, beidseitig georderten Konsolidierungs-Range, die sich seriell wiederholt.
- [[Market Maker Trap - False Flag]] — Schwesterkonzept auf Flag-Pattern-Ebene.
- [[Open Float & Liquidity Pools]], [[Institutional Order Flow (Body vs Wick)]] — Liquidität liegt
  über den Bodies der Range-Extreme, nicht zwingend über den Wicks.
- [[Algorithmic Order Flow]]
