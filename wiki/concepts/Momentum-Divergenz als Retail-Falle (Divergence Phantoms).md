---
tags: [concept, ict, trading-ict]
created: 2026-08-06
updated: 2026-08-06
sources: ["[[ICT Mentorship Core Content - Month 04 - Divergence Phantoms (Source)]]"]
---

# Momentum-Divergenz als Retail-Falle (Divergence Phantoms)

ICTs Grundhaltung zu Indikatoren: Sie sind **mathematisch aus der Vergangenheit abgeleitet** und
haben **keinerlei Bezug** zu tatsächlich im Markt liegenden Orders — Preis "weiß" nichts von einem
Stochastic oder RSI. Indikatoren werden trotzdem genutzt, aber nicht als Signalgeber, sondern um zu
lesen, **wie Retail-Trader gerade denken** — und dann bewusst das Gegenteil zu erwarten.

> ⚠️ Nicht zu verwechseln mit [[SMT (Smart Money Divergence)|SMT]]: SMT vergleicht **zwei
> korrelierte Märkte** gegeneinander (Cross-Asset), hier geht es um die Divergenz zwischen **Preis
> und einem Momentum-Indikator desselben Marktes** (Cross-Indicator).

## Typ 1 — klassische Divergenz (Retail-Lesart)

- **Bearish**: Preis macht ein Higher High, der Indikator (z.B. Stochastic) macht **kein** Higher
  High → Lehrbuch-Verkaufssignal.
- **Bullish**: Preis macht ein Lower Low, der Indikator macht **kein** Lower Low → Lehrbuch-Kaufsignal.
- Retail sieht darin Top-/Bottom-Picking-Signale und positioniert sich entsprechend gegen den
  bestehenden Trend.

## Typ 2 — Hidden/Trend-Following-Divergenz (die eigentlich relevante)

- **Bullish (Trendfortsetzung)**: Preis macht ein **Higher Low**, der Indikator macht dabei ein
  **tieferes Low** als beim vorherigen Zyklus.
- **Bearish (Trendfortsetzung)**: Preis macht ein **Lower High**, der Indikator macht ein
  **höheres High**.
- Korrekte Zuschreibung (von ICT explizit richtiggestellt): diese Form stammt von **Nick van Nice**,
  nicht von George Lane (dem oft fälschlich die gesamte Divergenz-Theorie zugeschrieben wird).

## Die Falle — wie Smart Money Typ-1-Divergenz gegen Retail nutzt

1. Preis macht ein Higher High an einem alten Hoch, Typ-1-Bearish-Divergenz erscheint im Indikator.
   Retail liest das als Top und geht short, mit Ziel: klassische Unterstützung/alte Tiefs.
2. Tatsächlich läuft Preis erst **in einen [[Order Block]] oder eine Konsolidierung knapp
   darunter**, nimmt dort die Sellside-Liquidity der zu früh eingestiegenen Shorts (bzw. baut neue
   Longs auf), OHNE die entscheidende alte Low-Zone zu verletzen.
3. Von dort läuft Preis **durch das ursprüngliche Hoch**, das Retail für "das Top" hielt — die
   Typ-1-Shorts werden ausgestoppt. Der eigentliche Kaufimpuls zeigt sich erst jetzt als
   **Typ-2-Divergenz** (Higher Low im Preis, tieferes Low im Indikator).
4. Spiegelbildlich für bearishe Fortsetzungen an einem vermeintlichen "Bottom".

## Praktische Regel für den erwarteten Rücklauf

Beim erwarteten Rücklauf in Richtung des Order Blocks/der Konsolidierung: Preis soll **bis maximal
zur Mitte des Bodys der letzten Gegen-Candle** vor dem Move laufen, aber **nicht darunter/darüber**
— das ist die Guard-Rail, an der die Idee invalidiert würde. Der Indikator darf dabei ruhig ein
neues Extrem erreichen (das gehört zur Typ-2-Signatur), der **Preis** darf es nicht.

## Verwandt

- [[SMT (Smart Money Divergence)]] — Cross-Asset-Pendant, nicht zu verwechseln
- [[Order Block]], [[Fair Value Gap (FVG)]], [[Open Float & Liquidity Pools]]
- [[ICT Mentorship Core Content - Month 04 - Divergence Phantoms (Source)]]
