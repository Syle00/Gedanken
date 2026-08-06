---
tags:
  - Daily-Bias
Bias:
  - Bullish
Date: 2026-08-06
NQ/ES: MNQ
id: 2026-08-06-01
typ: daily-bias
modus: live
kw: 2026-W32
wochentag: Donnerstag
modell: "kein Trade (No-Trading-Tag laut eigener Regel)"
liquidity_ziel: "Buyside 30.094,00 (User nannte '26 Juli' — tatsächlich Doppel-Hoch 02.07+05.07, siehe Korrektur); näher: Daily-BISI-Oberkante ~29.775,50"
pd_arrays: [New Week Opening Gap (NWOG) Bias, New Day Opening Gap (NDOG), IFVG (Inverse Fair Value Gap), BISI & SIBI (Buyside-Sellside Imbalance), Market Structure Shift (MSS), Judas Swing, Silver Bullet Model]
fehler: []
---

# 2026-08-06 MNQ Daily Bias

## Bias

**Bullish**, aber **No-Trading-Tag** nach eigener Regel: heute Unemployment/Jobless-Claims-News
(orange Folder), morgen NFP — dazwischen bewusst nicht gehandelt.

**Sein Plan (Original in `raw/journal/Daily Bias 2026-08-06.md`):** Vorgestern (04.08) enorme
bullishe Daily Range ohne nennenswerte Sellside-Reaktion, gestern (05.08) dadurch fragilere,
schwerer zu antizipierende Price Action — typisch nach einem sehr großen Range-Tag. Ablauf gestern:
false Run zur Sellside im London Silver Bullet, danach in NY AM erst Buyside genommen (bis knapp
über das NWOG KW29), dann MSB Richtung Sellside; Lunch Konsolidierung; NY PM zog sich lange hin,
Move erst ~15:25 kurz vor Market Close mit starker Expansion. Für heute: Daily IFVG vom 16.07 hat
gestern über dem C.E. geclosed → dadurch neues Daily BISI am 04.08 gebildet, dessen C.E. respektiert
werden soll — solange das hält, bleibt die bullishe Marketstructure bestätigt. DOL: Buyside-High
"26 Juli" bei 30.094,00. Montag bleibt Wochentief. Aktuell auf dem BISI-Hoch, 1H zeigt bereits
bullishe Reaktion. NDOG-Open 29.576,00, Konsolidierung darum. Bevorzugt: keine tiefe Sellside-Reaktion
zur Dienstag-NY-AM-Liquidität — falls doch, dann von dort starke MSS-Reaktion zur Upside mit Close
über dem BISI-C.E. Asia-Low darf von London genommen werden, danach Upside-Expansion.

---

## Nachgerechnet

Datenbasis: `raw/marktdaten/2026/08/06.08.2026/` (frisch per yfinance gezogen, 05.08. 18:00 –
06.08. 02:05 NY, 97×5m-Kerzen) plus 1m-Aggregation über eigene Handelstag-Grenze (18:00 NY) für
die Tages-OHLC-Reihe Juli/August, weil die pro-Tag benannten 1d/4h/1h-Dateien bekanntermaßen
Fremd-Historie enthalten (siehe `wiki/log.md`, 2026-08-04) und nicht direkt vergleichbar sind.

**Bestätigt ✅**

- **NDOG-Open 29.576,00 stimmt exakt.** Erste 5m-Kerze der heutigen Session (05.08. 18:00 NY)
  öffnet bei genau 29.576,00.
- **Unemployment heute, NFP morgen — bestätigt.** ForexFactory/TradingEconomics für Do. 06.08.:
  Initial/Continuing Jobless Claims um 08:30 NY (üblich orange/mittel). Für Fr. 07.08.: Non-Farm
  Payrolls, Unemployment Rate, Average Hourly Earnings um 08:30 NY (red). Passt zur eigenen
  No-Trading-Regel.
- **Montag bleibt Wochentief.** Wochentief KW32 liegt bei **28.723,25** (Mo. 03.08., eigene
  1m-Aggregation). Bisheriges Tief seither (Di–Do) liegt klar darüber (niedrigstes: 28.831,50 am
  04.08.) — Montag hält.
- **Daily IFVG vom 16.07 — C.E.-Respekt bestätigt, mit Zahl nachgeliefert.** 3-Kerzen-Daily-FVG aus
  15.07./16.07./17.07. (Handelstag-Kerzen): bearish, Range **29.220,00–29.396,75**, C.E. ≈
  **29.308,38**. Gestern (05.08.) schloss bei **29.904,00** — deutlich über dem C.E. Bestätigt.
- **Daily BISI am 04.08 — Lage plausibel, "auf dem Hoch" ungenau.** 3-Kerzen-Daily-FVG aus
  03.08./04.08./05.08.: bullish, Range **28.965,00–29.775,50**, C.E. ≈ **29.370,25**. Heutiger
  bisheriger Bereich (29.454,25–29.678,75) liegt **innerhalb** der oberen Hälfte dieser Zone, aber
  rund 100 Punkte **unter** der tatsächlichen Oberkante (29.775,50) — "auf dem Hoch" ist optimistisch
  formuliert, "im oberen Drittel der Zone" träfe es genauer. Kein Widerspruch zur bullishen Lesart.

**Korrekturen ⚠️**

1. **"High vom 26 Juli 30.094,00" — Datum falsch, Level real.** 30.094,00 ist exakt der Doppel-Top-
   High vom **02.07. und 05.07.** (beide Tage treffen den Wert auf den Tick). Der tatsächliche
   Handelstag-High vom 26.07. liegt bei **28.763,75** — das ist zufällig derselbe Level wie der
   "Montags-High 27.07" aus dem Buyside-Cluster im 03.08.-Eintrag (`journal/entries/2026-08-03 MNQ
   Daily Bias.md`), Verwechslungsgefahr zwischen den beiden Daten naheliegend. Als fernes DOL bleibt
   30.094,00 grundsätzlich gültig (deutlich über dem aktuellen Preis, kein Widerspruch zur Bullish-
   These), nur die Datumsangabe war falsch.
2. **Dienstag-NY-AM-Sellside — nicht unabhängig verifiziert.** Der genaue Level dieser Liquidität
   wurde hier nicht nachgerechnet (kein konkreter Preis im Text genannt); offen für den nächsten
   Durchgang.

---

## Timeline (NY)

- **05.08. 18:00** — NDOG öffnet bei 29.576,00, Beginn der heutigen Konsolidierung um das Gap.
- Stand der Marktdaten bricht um **02:05 NY** ab (Asia/frühe London-Übergabe) — London- und
  NY-Sessions dieses Handelstags sind zum Zeitpunkt dieses Eintrags noch nicht gelaufen.

## Was gut lief

- No-Trading-Regel um bekannte Doppel-News (Jobless Claims heute, NFP morgen) konsequent angewandt,
  statt trotz Kalender zu handeln.
- Sequenz "IFVG-C.E. respektiert → neues BISI gebildet" korrekt aus der eigenen Wiki-Logik
  hergeleitet (IFVG/BISI-Kette), nicht nur behauptet.
- Präferenz-Szenario (kein tiefer Sellside-Sweep) UND Alternativ-Szenario (Sweep + MSS-Reaktion
  zurück über den BISI-C.E.) beide im Voraus benannt, statt nur ein Szenario zu planen.

## Datenlücken

*Nicht bewertbar, weil die Information fehlt oder der Tag noch läuft.*

- Tag ist zum Zeitpunkt dieses Eintrags erst bis 02:05 NY (Asia-Ende) mit Daten hinterlegt —
  London/NY AM/Lunch/NY PM und damit `bias_korrekt` erst im Nachtrag bewertbar (analog zum
  08.03.-Muster, ausgewertet am Folgetag).
- Exakter Level der "Dienstag NY AM Sellside" fehlt im Text — nicht nachrechenbar.
- Kein Screenshot zu diesem Eintrag (reine Text-Notiz, kein Chart-Export vorhanden).

## Verwandt

[[New Week Opening Gap (NWOG) Bias]], [[New Day Opening Gap (NDOG)]], [[IFVG (Inverse Fair Value Gap)]], [[BISI & SIBI (Buyside-Sellside Imbalance)]], [[Market Structure Shift (MSS)]], [[Judas Swing]], [[Silver Bullet Model]]
