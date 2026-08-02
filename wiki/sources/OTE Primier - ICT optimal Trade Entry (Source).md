---
tags: [source, ict, trading-ict, market-maker-primer, ote, entry, unvollstaendig]
created: 2026-08-02
updated: 2026-08-02
raw: "[[OTE Primier - ICT optimal Trade Entry]]"
raw_path: "raw/trading-ict/Market Maker Primer/OTE Primier - ICT optimal Trade Entry.md"
---

# OTE Primier - ICT optimal Trade Entry (Source)

> ⚠️ **Unvollständig.** Die Mitschrift endet mit *„Weiter bei min 30"*.

Die einzige Quelle im Vault, die die **konkreten Fib-Level des OTE** samt Beschriftung zeigt.

## Kernpunkte

- **Higher Timeframe nutzen.** Beim OTE geht es darum, **das Retracement zu kaufen** (bullish wie
  bearish).
- **Retracement bis maximal 0,79** — laut ICT ist auch das noch in Ordnung.
- **Stop Loss genau unter/über dem initialen Low/High** — dort ist er protected.
- **Erster Profit am ersten High/Low**, optimalerweise **etwas davor** — es kann immer sein, dass der
  Preis es nicht ganz bis zum High/Low zurückschafft.

### Die Fib-Einstellungen

Aus den Screenshots der MT4-Fibo-Konfiguration:

| Level | Beschriftung |
| --- | --- |
| **0** | First Profit – Scaling |
| **0.618** | %$ – 62 Percent |
| **0.705** | **OTE** (aus der Übersichtsfolie) |
| **0.79** | %$ – 79 Percent |
| **1** | 100.0 |
| **−0.27** | Target 1 |
| **−0.62** | Target 2 |
| **−1** | Symmetrical Swing |

![[MMP - OTE 01.png]]
*Die OTE-Übersichtsfolie: Retracement-Zone 62 / 70,5 / 79 Prozent, darüber First Profit (Scaling),
Target 1, Target 2 und der Symmetrical Swing — in beide Richtungen gespiegelt.*

Die Level werden dafür einmalig im MT4-Fibo-Werkzeug hinterlegt:

![[MMP - OTE 02.png]]
*Fibo-Einstellungen, Teil 1: Level 0 = „First Profit – Scaling", 0.618 = „62 Percent", 1 = 100.0.*

![[MMP - OTE 03.png]]
*Teil 2: 0.79 = „79 Percent", −0.62 = „Target 2", −0.27 = „Target 1".*

![[MMP - OTE 04.png]]
*Teil 3: −0.27 = „Target 1", −1 = „Symmetrical Swing".*

![[MMP - OTE 05.png]]
*Das fertige Raster auf einen Swing gelegt — Retracement in die OTE-Zone, Ziele darüber hinaus.*

![[MMP - OTE 06.png]]
*Dasselbe Raster in der Gegenrichtung.*

## Extrahiert nach

- [[Optimal Trade Entry (OTE)]] (neu)

## Verwandt

- [[ICT Killzones]] — alle vier Killzones werden über OTE-Setups gehandelt
- [[Equilibrium Vs. Discount]], [[PD Array]]
