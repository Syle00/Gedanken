---
tags: [source, ict, trading-ict, mentorship-2025, liquidity, ath, ipda]
created: 2026-08-02
updated: 2026-08-02
raw: "[[05 Advanced ICT Liquidity Concepts]]"
raw_path: "raw/trading-ict/MentorShip 2025/05 Advanced ICT Liquidity Concepts.md"
---

# Advanced ICT Liquidity Concepts (Source)

Lektion 05 der **MentorShip 2025**, zwei Themenblöcke: **Breakaway Gaps** (inkl. der Frage, wie weit
PD Arrays rückwirkend gültig bleiben) und **Opening Range Gaps am ATH** — letzteres mündet in das
3-Stages-Distributionsmuster.

## Kernpunkte

### Breakaway Gap

- **Großes Displacement an einem Quadranten eines FVG oder einer Wick → im Lower Timeframe wird das
  FVG oft zu einem Breakaway Gap.** (Wortgleich mit [[Kurz Notizen (Source)]] — Bestätigung, kein
  neuer Inhalt.)
- Fallbeispiel: zwei große Displacements auf Quadranten der Daily Imbalance. Das **erste** Gap gilt
  als Breakaway Gap. Selbst beim zweiten geht die Wick nur minimal übers C.E und **nicht mal bis
  0,75** — eindeutig heavy bearish.
- Spiegelbildlich bullish am EU: auch hier Displacement durch einen Quadranten. Liegen zwei Gaps
  vor, ist **das zuerst entstandene** relevant — das darüberliegende BISI ist zwar ebenfalls ein
  Displacement durch einen Quadranten, tritt aber zurück.
- **Jede PD Array gibt es auch als Inversion-Variante** — also auch einen Inversion Breaker Block.

### Wie weit rückwirkend sind PD Arrays gültig?

> **Wir nehmen die [[IPDA Data Ranges]] 20/40/60 Days — PDs sind bis zu 60 Tage rückwirkend
> nutzbar.**

Gilt für Imbalances, Wicks, Gaps usw. Das beantwortet eine Frage, die die bisherigen IPDA-Seiten
offenließen: das 20/40/60-Fenster begrenzt nicht nur die High-/Low-Suche, sondern die
Verwendbarkeit der PD Arrays insgesamt.

### Opening Range Gap am ATH

- **Equal Highs/Lows sollen nicht nur mit einer Wick durchbrochen werden, sondern mit einem Candle
  Body Close.**
- Die **ORGs der letzten 3 Tage plus des laufenden Handelstags** sind relevant — insgesamt also
  **4 ORGs mit Quadranten**.
- Warum das ORG an genau diesem Tag so relevant war: (1) sehr großes Gap, (2) an diesem Tag wurde
  ein ATH durchbrochen, (3) es gab einen **Candle Body Close über dem ATH**.
- Diese Logik gilt **nicht nur bei ATH**, sondern auch bei alten Market Highs/Lows sowie LTH/LTL und
  ITH/ITL.

### 3 Stages of Accumulation (heavy Shorts)

Ausführlich auf [[Trading All Time Highs (ATH)]]. Kurz: nach dem Body Close über dem ATH nutzt Smart
Money jede PD Array oberhalb des Closing Price für heavy Shorts — dreimal ein höherer Close über dem
jeweiligen High, jedes Mal neue Shorts an Premium-PDs. Erkennbar an den Wicks: höher ja, aber der
Close liegt deutlich tiefer → Distribution von Longs, Akkumulation von Shorts.

Die verallgemeinerte Orderflow-Regel daraus: **kein Close über dem C.E einer PD Array → short**
(und spiegelbildlich).

## Extrahierte Seiten

- [[Trading All Time Highs (ATH)]] (neu, gemeinsam mit
  [[Trading All Time Market Highs (Source)]])
- [[IPDA Data Ranges]] (aktualisiert: 60-Tage-Gültigkeit der PD Arrays)
- [[Breakaway Gap]] (aktualisiert: Auswahlregel bei mehreren Gaps, Inversion-Varianten)
- [[ORG (Opening Range Gap) & 1st Presented FVG]] (aktualisiert: 4-ORG-Regel, Candle Body Close)

## Bilder aus der Rohquelle

![[MentorShip 2025 - 05 Breakaway Gap Quadrant Displacement.png]]
*Großes Displacement an einem Quadranten — im Lower Timeframe entsteht daraus ein Breakaway Gap.*

![[MentorShip 2025 - 05 Two Displacements Daily Imbalance.png]]
*Zwei Displacements auf Quadranten der Daily Imbalance; das zweite erreicht nicht mal 0,75 —
heavy bearish.*

![[MentorShip 2025 - 05 Bullish EU Mirrored IPDA 60 Days.png]]
*Gespiegelt bullish am EU: das zuerst entstandene Gap bleibt das relevante.*

![[MentorShip 2025 - 05 ORG with ATH Equal Highs.png]]
*ORG am ATH-Tag: Equal Highs mit Candle Body Close durchbrochen, ORGs der letzten 3 Tage markiert.*

![[MentorShip 2025 - 05 Three Stages Heavy Shorts.png]]
*3 Stages der Short-Akkumulation an Premium-PDs.*

![[MentorShip 2025 - 05 Three Closing Prices Above Highs 1.png]]
*Die 3 Closing Prices über den jeweiligen Highs.*

![[MentorShip 2025 - 05 Three Closing Prices Above Highs 2.png]]
*Derselbe Ablauf im Detail.*

![[MentorShip 2025 - 05 No Close Above Premium Wick CE 1.png]]
*Kein Close über dem C.E der Premium Wick — Orderflow sagt short.*

![[MentorShip 2025 - 05 No Close Above Premium Wick CE 2.png]]
*Fortsetzung.*

## Verwandt

- [[Trading All Time Highs (ATH)]], [[Breakaway Gap]], [[IPDA Data Ranges]]
- [[ORG (Opening Range Gap) & 1st Presented FVG]], [[PD Array]]
- [[Trading All Time Market Highs (Source)]] — Lektion 01, die Continuation-Seite desselben Themas
- [[Smart Money Concepts (SMC)]]
- [[MentorShip 2025]] — Überknotenpunkt der Reihe
