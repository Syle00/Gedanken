---
tags: [model, ict, trading-ict, swing, weekly]
created: 2026-08-01
updated: 2026-08-16
sources: ["[[Using Monthly & Weekly Ranges (Source)]]", "[[NQ Futures Weekly Range Market Wizardry (Source)]]", "[[TGIF - Thank God its Friday (Source)]]", "[[2026-08-15 - The Week In The Life Cycle Of Price (Source)|The Week In The Life Cycle Of Price (Source)]]"]
---

# Weekly Range Trading Model

Short-Term-Modell: die **Weekly Range** wird getradet, PD-zu-PD von Monthly nach Weekly.

## Ablauf

- Faustregel: tradet Preis zu einer Premium-[[Fair Value Gap (FVG)|FVG]], ist es wahrscheinlich,
  dass er auch zu einer (Discount-)FVG tradet — analog für andere PD-Typen (Highs/Lows).
- Preis soll zu einer **Monthly PD** traden (z.B. Premium FVG), danach die erste **Discount PD im
  Weekly Chart** als Ziel suchen.
- Nicht alle PD-Typen sind gleichzeitig vorhanden — meist 2, max. 3 relevant.
- Execution im **1H-Chart** (15-Min funktioniert auch, 1H ist aber vorzuziehen). Top-down von
  Monthly bis 1H wie gewohnt.

![[image 137.png]]
*Top-Down-Ausführung von Monthly bis 1H-Chart.*
- Richtung zeigt sich meist bereits Montag/Dienstag, danach folgt das Retracement — dies ist aber
  nur eine Richtlinie, das Retracement kann auch schon Dienstag kommen.

![[image 142.png]]
*Die Richtung zeigt sich meist schon Montag/Dienstag, danach folgt das Retracement — nur eine
Richtlinie, kein starrer Ablauf.*
- Target immer die höchstmögliche verfügbare Timeframe-PD (Monthly > Weekly > Daily). Zusätzlich
  [[COT (Commitment of Traders) Data|COT]], [[Seasonal Tendency]] und [[Intermarket Relationships|Intermarktanalyse]]
  (z.B. Bonds) als Bonus-Bestätigung nutzen.
- Entry in der Killzone: London- oder NY-AM-Open.

## Montag–Mittwoch-Range als Signal

- Die Range von **Montag bis Mittwoch** ist entscheidend: wird sie durchbrochen, wird ein
  aggressiver Move erwartet.
- Bullisher Bias + Durchbruch des Range-Highs = Zeichen für ein "Buy Program".
- Bearisher Bias + Durchbruch des Range-Lows = Zeichen für ein "Sell Program".
- Wird das **Vorwochen-High** innerhalb Mo–Mi durchbrochen, ist das ein starkes Signal, dass Preis
  zur Higher-Timeframe-Premium-PD will.

![[image 147.png]]
*Montag-bis-Mittwoch-Range: Durchbruch signalisiert einen aggressiven Move (Buy- bzw.
Sell-Program).*

## Zwei-DOL-Methode & TGIF (2026-Ergänzung, NQ-Futures-Fallstudie)

- Die Weekly Range wird über **2 DOLs** bestimmt: ein **Premium-DOL** und ein **Discount-DOL**
  (jeweils Liquidity, [[New Week Opening Gap (NWOG) Bias|NWOG]]/NDOG oder jede andere Premium/
  Discount-Array).
- Bei bearishem Bias/Orderflow wird **zuerst** das Premium-DOL antizipiert — erst nach dessen
  Erreichen rückt das Discount-Pool/DOL in den Fokus (spiegelbildlich bei bullishem Bias).
- **TGIF** → ausführlich auf der eigenen Seite [[TGIF (Thank God its Friday)]]. Kurzfassung: nach
  Erreichen der Discount-Array und passendem Timing (Freitag) wird ein Retracement von
  **20–30 % der Weekly Range** erwartet. Kommt das Retracement nicht bereits am Freitag, wird es
  standardmäßig am **Montag oder Dienstag** der Folgewoche erwartet (Kurz Notizen).
- **Fallbeispiel aus [[Alltime Highs und TGIF (Source)]]**: bei einer sehr bullishen Woche
  Retracement von **20 %**; Target waren die Quadranten der Premium Wick bzw. die
  **Premarket-Sellside-Liquidität**, der Entry lag am **Reclaimed FVG**. Relevant war die
  **Daily [[Volume Imbalance (VII)|VII]]** — nach deren Erreichen folgte eine explosive Reaktion.
  > ✅ **Geklärt (2026-08-02)**: Die dort notierte „20% der **Daily** Range" war als offene Frage
  > markiert. [[TGIF - Thank God its Friday (Source)]] verwendet dieselbe lose „Daily"-Sprechweise
  > in der Einleitung, definiert das Setup operativ aber über einen Fib auf die **Weekly Range** und
  > beschriftet die Charts mit „20% / 30% Weekly Range". Maßgeblich ist die **Weekly Range**.
- Wo genau relativ zum **C.E** (Consequent Encroachment, siehe [[Central Bank Dealers Range (CBDR)]])
  einer Wick/PD Array geclosed wird, ist entscheidend — der tatsächliche Orderflow wiegt dabei immer
  schwerer als der einzelne Schlusskurs einer Candle.

![[image 34.png]]
*Zwei-DOL-Methode am NQ-Beispiel: bei bearishem Bias zuerst das Premium-DOL antizipieren, danach den Discount-Pool/DOL.*
- **Overnight Liquidity** wird bevorzugt im Fenster **7–9 Uhr** (Premarket) attackiert.
- ✅ **Geklärt (2026-08-16)**: Der hier ohne Definition auftauchende Begriff „Suspensionblock" ist
  inzwischen als eigene Seite [[Suspension Block]] belegt (FVG mit
  [[Volume Imbalance (VII)|VII]] auf **beiden** Seiten). Nicht verwandt mit [[Order Block]], wie
  ursprünglich vermutet.
  [[2026-08-15 - The Week In The Life Cycle Of Price (Source)|The Week In The Life Cycle Of Price (Source)]]
  zeigt zusätzlich die praktische Verwendung: dessen C.E. als Entry-Anker.

## Wochenend-Routine (2026-08-15)

Wie ICT die Level-Liste für die Folgewoche erstellt — Freitag nach Close oder Samstag früh, auf
Papier:

1. **Continuous Contract zuerst**, dann Front-Month-Abgleich — siehe
   [[Continuous Contract vs. Front Month]].
2. **Alle Session-Ranges plus deren Mittelpunkte** notieren (Asia, London, NY AM, NY Lunch), dazu
   Vortag, Last-3-Days, Vorwoche, Vormonat — vollständiger Katalog in
   [[Open Float & Liquidity Pools]].
3. **Abgelaufene Woche einem Profil zuordnen** ([[Market Maker Manipulation Templates]]) und das
   erwartete Profil der Folgewoche über den **Wirtschaftskalender** legen.
4. **Bias über Nähe**: Liegt der Wochenopen näher am Vorwochen-/Vormonats-High als am
   entsprechenden Low, ist das High der Weg des geringsten Widerstands — zusammen mit dem
   übergeordneten Order Flow ergibt das den Wochenbias.

Der 15-Min-Chart genügt für Schritt 2–4 („Bellwether"); höhere Timeframes bringen laut ICT nichts
dazu.

## Verwandt

- [[TGIF (Thank God its Friday)]]
- [[One Shot One Kill Model]]
- [[Market Maker Manipulation Templates]]
- [[PD Array]], [[Fair Value Gap (FVG)]]
- [[Event Horizon]]
- [[Continuous Contract vs. Front Month]] — Schritt 1 der Wochenend-Routine
- [[Suspension Block]], [[Open Float & Liquidity Pools]]
