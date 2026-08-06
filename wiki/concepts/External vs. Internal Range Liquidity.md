---
tags: [concept, ict, trading-ict, liquidity, core]
created: 2026-08-06
updated: 2026-08-06
sources: ["[[ICT Mentorship Core Content - Month 04 - Reinforcing Liquidity Concepts & Price Delivery (Source)]]"]
---

# External vs. Internal Range Liquidity

Unterscheidet, **wo relativ zur aktuellen Trading-Range** eine Liquiditätsquelle liegt — bestimmt
damit, ob ein Level als Entry oder als Exit-Ziel taugt.

> Schließt eine bislang leere Rohdatei im Notion-Export
> (`Reeinforced Liquidity Pools - When to anticipate Raids`, siehe [[Month 04 (Source)]]).

## Definitionen

- **External Range Liquidity**: Buy-Side-Liquidity oberhalb des Range-Highs bzw. Sell-Side-Liquidity
  unterhalb des Range-Lows — also **außerhalb** der aktuell gehandelten Range.
- **Internal Range Liquidity**: [[Order Block]], [[Fair Value Gap (FVG)]] oder Liquidity Void
  **innerhalb** der aktuellen Range — füllt sich typischerweise, solange die Range aktiv bleibt
  ("Gap Risk").

## Faustregel für Entry/Exit

> Entries an Internal Range Liquidity (Order Block/FVG **innerhalb** der Range), Exits an External
> Range Liquidity (Buy-/Sell-Stops **außerhalb** der Range).

D.h. gekauft wird am Order Block innerhalb der Range, verkauft/eingedeckt wird an den Stops über
dem alten Range-High — nicht umgekehrt.

## Range-Neudefinition nach jedem Bruch

Jedes Mal, wenn External Range Liquidity gerissen wird (altes High/Low genommen), wird die Range
**neu definiert**: das gerissene Level plus der zuletzt gebildete Extrempunkt bilden die neue
Range, und External/Internal Range Liquidity werden entsprechend neu zugeordnet — ein iterativer
Prozess, der sich über mehrere Timeframes fortsetzt (Monthly → Weekly → Daily → 4H → 15M).

## Verzahnung mit Low/High Resistance Liquidity Run

Läuft die Range in Richtung des HTF-Bias (z.B. Monthly bullish, Preis läuft auf ein High), ist der
Bruch der External Range Liquidity ein **Low Resistance Liquidity Run** — siehe
[[Low Resistance Liquidity Run]]. Läuft sie gegen den HTF-Bias, ist er ein High Resistance Run.

## Mindest-Range-Größe (Praxisregel)

Der Abstand zwischen Order Block (Internal) und dem anvisierten alten High/Low (External) sollte
**mindestens 40 Pips** betragen (Faustwert des Quellvideos), sonst lohnt sich der Trade nicht — bei
höheren Zielen (z.B. 50+ Pips/Woche) entsprechend einen höheren Timeframe für die Range-Definition
wählen (30M/1H statt 15M).

## Verwandt

- [[Order Block]], [[Fair Value Gap (FVG)]]
- [[Low Resistance Liquidity Run]]
- [[Open Float & Liquidity Pools]]
- [[Dealing Range]]
