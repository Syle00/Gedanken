---
tags: [model, ict, trading-ict, daytrade, sessions]
created: 2026-08-02
updated: 2026-08-05
sources: ["[[Kurz Notizen]]", "[[ICT Silver Bullet (Source)]]"]
---

# Silver Bullet Model

Reines **Time-based Model** — nur innerhalb der drei festen Zeitfenster tradebar. Der eigentliche
Silver-Bullet-Move beginnt **innerhalb des Macros vor** dem eigentlichen Silver-Bullet-Fenster,
nicht erst mit dessen Beginn.

## Die drei Fenster (NY Zeit)

| Fenster | Zeit | Session |
|---|---|---|
| London Silver Bullet | **3:00–4:00 Uhr** | London |
| NY AM Silver Bullet | **10:00–11:00 Uhr** | NY-Session |
| NY PM Silver Bullet | **14:00–15:00 Uhr** | NY PM |

Das Zeitfenster ist nur für den **Einstieg** relevant — der Trade muss nicht innerhalb des Windows
fertig sein und darf über die Stunde hinaus weiterlaufen. ICT nutzt bevorzugt den **5-Min-Chart**
für den Entry, kombiniert mit PD Arrays aus dem 15-Min- und 1H-Chart. Muss zusätzlich mit
**Confluenz** abgesichert werden: andere PD Arrays/Targets wie NWOG/NDOG, Midnight Opening Fibs
oder das 1. presented FVG. Siehe [[ICT Silver Bullet (Source)]].

## Ablauf

- Referenzbeispiel: das [[ICT Macros & Leading Candles|Macro]] **9:50–10:10** liefert Displacement +
  [[Fair Value Gap (FVG)|FVG]]. Danach wird dieses FVG als [[IFVG (Inverse Fair Value Gap)|IFVG]] in
  die **entgegengesetzte Richtung** genutzt — der sogenannte **"2022 Entry"** (typischerweise im
  5-Min-Chart).
- Der Move innerhalb dieses vorgelagerten Macros ist **selten der vollständige Move** — er startet
  lediglich. Laut ICT läuft der eigentliche Move über die **volle folgende Stunde**, wodurch
  theoretisch auch ein deutlich späterer Einstieg möglich ist, solange der Move über die Stunde
  weiterläuft.
- Der Move endet an einem logischen Level — Liquidity oder ein Quadrant eines FVG (siehe
  [[Chain of Custody (Q-Validation)]]).
- ICT würde laut Quelle auch dann noch shorten, wenn der Price-Run bereits fast vollendet wirkt (z.B.
  kurz vor halb 11) — solange ein klarer Liquidity Pool als Ziel erkennbar bleibt.

![[Kurz Notizen - Late Shorting Liquidity Pool Example.png]]
*ICT würde hier trotz fast vollendetem Price Run noch shorten, da kurz davor ein offensichtlicher Liquidity Pool liegt.*

## Trade Management (eigene Ausführungsregel, kein ICT-Quellenzitat)

Zusatzregel zur reinen Entry-Logik oben, so wie im Algo-Backtest (`algo/rules.py::plan_trade`,
`algo/backtest_ensemble.py::EnsembleStrategy`) umgesetzt:

- **Mindestziel:** Setup wird nur genommen, wenn zwischen Entry und Target mindestens
  **10 Handle/Punkte** Potenzial liegen. Ohne genug Abstand: kein Trade, unabhängig davon, ob
  sonst alle Kriterien (Fenster, FVG, Zielliquidität) erfüllt sind.
- **Partial:** am **ersten Swing-Hoch** (long) bzw. **ersten Swing-Tief** (short), das nach dem
  Entry entsteht, wird ein Teil der Position geschlossen (Backtest-Default 50%, siehe
  `EnsembleStrategy.partial_portion` — die genaue Aufteilung war nicht vorgegeben).
- **Breakeven:** sobald das Partial genommen wurde, wandert der Stop auf den Entry-Preis. Der
  Rest der Position läuft drawdown-frei bis Stop oder Target weiter.
- **Positionsgröße:** richtet sich nach dem Kontoguthaben, nicht nach fixer Kontraktzahl —
  siehe [[Risikomanagement (1% pro Trade)]] (`EnsembleStrategy._risk_size`).

Diese Regel ist reines Trade-Management, keine ICT-Quellenaussage — sie ergänzt, ersetzt aber
nicht die Entry-Kriterien aus dem Abschnitt oben.

## Bezug zu Nachbar-Fenstern

- Das **NY-AM-Fenster (10–11 Uhr)** überlappt mit dem Vorlauf zum [[NY Lunch Macro Model|NY Lunch
  Macro]] (Ausführung 10:50–11:10) — beide liegen im selben Vormittagsblock, sind aber getrennte
  Setups.
- Das **PM-Fenster (14–15 Uhr)** bestätigt [[NY PM Trend]] ("Beginnt typischerweise um 2 Uhr =
  Silver Bullet").
- ✅ Damit ist der bisher offene Punkt geklärt, dass die AM-/Lunch-Fenster noch nicht als eigene
  Zeiten belegt waren.

## Verwandt

- [[ICT Macros & Leading Candles]], [[Fair Value Gap (FVG)]], [[IFVG (Inverse Fair Value Gap)]]
- [[Modell 22]] — ebenfalls ein MSS+SIBI/IFVG-basierter Trigger
- [[NY PM Trend]], [[ICT Daily Range Session Timing]], [[ICT Killzones]]
- [[Kurz Notizen (Source)]], [[ICT Silver Bullet (Source)]]
- [[Meine Strategien (Übersicht)]], [[Risikomanagement (1% pro Trade)]]
