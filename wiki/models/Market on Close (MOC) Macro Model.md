---
tags: [model, ict, trading-ict, 2026, macro, sessions, moc]
created: 2026-08-05
updated: 2026-08-05
sources: ["[[ICT Price Action Chronicles - MOC Crushing The Buying & Selling Pressure Myth (Source)]]"]
---

# Market on Close (MOC) Macro Model

Setup für die **letzten 10 Minuten des RTH-Handelstags (15:50–16:00 Uhr NY)** — analog zum
[[NY Lunch Macro Model]], nur am Tagesende statt zur Mittagszeit. Laut Quelle **nicht
NASDAQ-exklusiv**: das Beispiel läuft am E-Mini S&P (ES), dieselbe Logik gilt index-übergreifend.

## Grundidee

Ab **15:00 Uhr** (Beginn der letzten RTH-Stunde) wird beobachtet, wie sich Preis relativ zur
**Dealing Range des Tages** verhält (PM-Opening-Range-Low ab 13:30 Uhr bis Tageshoch). Ziel ist,
**in einem 10-Minuten-Fenster** eine chirurgisch präzise Entscheidung zu treffen — kein
"Hold for hundreds of handles", sondern ein kleiner, gezielter Move.

> Bei einem Tag, der bereits **lange in eine Richtung gelaufen ist** ("long in the tooth"), wird vor
> dem Close eher **Konsolidierung oder ein Retracement** erwartet als eine weitere Fortsetzung.

## Ablauf

1. **Dealing Range bestimmen**: PM-Opening-Range-Low (13:30 Uhr) bis Tageshoch — das ist der große
   Rahmen. Innerhalb davon eine **kleinere Dealing Range** suchen, die dicht ans Equilibrium
   herangehandelt hat (Discount, ohne den Midpoint zu brechen) und ein Buyside-Balance-Sellside-
   Inefficiency respektiert (siehe [[Equilibrium Vs. Discount]]).
2. **Fib-Grid anlegen**: Low → High dieser kleineren Range, inkl. **negativem -0,5-Level** (Setting
   wie bei [[Midnight Opening Range]] gewohnt). Daraus ergibt sich ein Levelpaar (Q/O-Raster, siehe
   unten).
3. **Erwartung ab ~15:50**: Preis läuft **erst** in Richtung Buyside (nimmt die Relative-Equal-Highs
   der kleineren Range), **dann erst** wird die eigentliche MOC-Richtung gehandelt — der erste Move
   ist noch **nicht** die Execution, sondern baut nur das Levelpaar auf (analog zur
   [[NY Lunch Macro Model|10-Uhr-Linie]] beim Lunch Macro: "erst entsteht das Target, dann wird
   gehandelt").
4. **Entry-Zone**: Alles zwischen dem gesweepten High und dem Midpoint der kleineren Range gilt als
   valide Short- (bzw. Long-)Zone — **aber erst nach Order-Flow-Bestätigung** (Schritt 5).
5. **Order-Flow-Bestätigung** (candlestick-only, siehe
   [[Institutional Order Flow (Body vs Wick)#MOC-Order-Flow-Bestätigung (Candlestick-only)|Detailregel]]):
   Candle rallyt in ein (Inversion-)FVG, berührt dessen C.E. nicht, closed unterhalb des eigenen Lows
   (das eine Volume Imbalance trägt) → bestätigt den bearishen Bias (spiegelbildlich bullish).
6. **Fortsetzung**: nach Bestätigung aggressiver Bruch durch minor Sellside-Pools (Relative Equal
   Lows), bis das projizierte Fib-Level erreicht wird.

## Fib-Feinraster: Quadrant → Oktant → 16tel

Ergänzt das bestehende Q/O-Raster ([[Chain of Custody (Q-Validation)]]):

| Ebene | Anteil der Range | Bezeichnung |
|---|---|---|
| Percentile | 100 % / Hälften | — |
| Quadrant (Q) | 25 % | bereits im Wiki |
| Oktant (O) | 12,5 % (halber Quadrant) | bereits im Wiki |
| **16tel** | **6,25 % (halber Oktant)** | **neu** |

## Zahlenbeispiel (ES, 2026-08-04)

- Short-Entry am projizierten Midpoint: **7.786,00**
- Projiziertes 16tel-Level (Ziel/Reversal): **7.761,75**
- Tatsächliches Tagestief: **7.761,25** — Abweichung **2 Ticks**

Diente ICT als Präzisionsnachweis: die Level wurden **vor** dem Move berechnet, nicht im Nachhinein
angepasst.

## Risikohinweis aus der Quelle

Fills sind bei öffentlich geteilten Levels **nicht garantiert** — bei genug Followern, die dieselbe
enge Zone anlaufen, bekommt nicht jeder eine Füllung zum selben Preis (Marktmechanik, keine
Verschwörung). Siehe [[Signal-Following & Crowd Liquidity Risk]].

## Verwandt

- [[NY PM Trend]] — die übergeordnete PM-Session, in die das MOC-Fenster fällt
- [[NY Lunch Macro Model]] — strukturell identisches Prinzip zur Mittagszeit
- [[ICT Daily Range Session Timing]], [[ICT Macros & Leading Candles]]
- [[Dealing Range]], [[Equilibrium Vs. Discount]], [[Chain of Custody (Q-Validation)]]
- [[Institutional Order Flow (Body vs Wick)]], [[IFVG (Inverse Fair Value Gap)]]
- [[Signal-Following & Crowd Liquidity Risk]]
- [[ICT Price Action Chronicles - MOC Crushing The Buying & Selling Pressure Myth (Source)]]
