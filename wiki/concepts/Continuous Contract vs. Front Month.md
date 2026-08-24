---
tags: [concept, ict, trading-ict, futures, daten, 2026]
created: 2026-08-16
updated: 2026-08-16
sources: ["[[2026-08-15 - The Week In The Life Cycle Of Price (Source)|The Week In The Life Cycle Of Price (Source)]]"]
---

# Continuous Contract vs. Front Month

ICTs feste **Reihenfolge** jeder Analyse: erst der **Continuous Contract** (fortlaufende,
über Rollover hinweg verkettete Reihe), danach der **Front Month** (der aktuell gehandelte
Liefermonat, z.B. NQ September 2026). Nicht umgekehrt und nicht nur eines von beidem.

## Warum zuerst der Continuous Contract

Er liefert das **Referenzfeld**: Key Highs, Key Lows, Ineffizienzen und [[PD Array|PD Arrays]],
die im Front Month **gar nicht existieren**, weil der Rollover-Effekt sie dort abgeschnitten hat.
ICTs Kernargument gegen den reinen Front-Month-Chart:

> Ein Kontrakt, der später ausläuft (März 2027, Dezember), hat **heute keinen Einfluss** auf die
> fortlaufende Reihe — und der Front Month begann erst zu einem Zeitpunkt zu handeln, an dem sein
> Beitrag zur Historie fehlt. Die alten Preisdaten sind nur über den Continuous Contract
> erreichbar: *„it allows me to look at things where the average person wouldn't."*

Konkreter Ablauf im Video:

1. **Monthly** (Continuous) — ICT arbeitet standardmäßig ab Monthly, hier abgekürzt, indem die
   Monats-Highs/-Lows direkt im Weekly eingezeichnet wurden.
2. **Weekly** (Continuous) — Vormonats-High/-Low und Vorwochen-High/-Low definieren die Range.
3. **Front Month** (NQ September) — dieselben vier Level erneut einzeichnen und prüfen:
   **stimmen sie überein?** Nur bei Übereinstimmung gilt das Level als handelbar.
4. Erst danach Daily → 15-Min → 1-Min.

## Übertragung auf CFDs

Für Händler ohne Zugang zu US-Futures gilt dieselbe Mechanik: Continuous Contract als
Referenzfeld, dann die tatsächlichen Tages-/Wochen-Highs und -Lows des CFD-Instruments
(US 100 für NASDAQ, US 500 für S&P) als korrelierendes Gegenstück suchen und daran abgleichen.

## Konsequenz für dieses Repo

Betrifft direkt die Datenhaltung in `raw/marktdaten/`: Dort wird bewusst die **Continuous-Reihe**
(`MNQ1!`/`NQ1!`) geführt statt der Einzelkontrakte — was ICTs Analysereihenfolge auf der
Referenz-Ebene abdeckt, den Schritt-3-Abgleich gegen den Front Month aber **nicht** ersetzt.
1d- und 1m-Daten sind dabei zwei verschiedene Serien, siehe `algo/PLAN.md`.

> ⚠️ **Offener Punkt für den Algo.** Ein Backtest auf reiner Continuous-Reihe bildet Schritt 3
> (Front-Month-Bestätigung) nicht ab. Rollover-Sprünge in der verketteten Reihe sind zudem ein
> bekannter Backtest-Fallstrick — siehe
> [[Futures-Datenaufbereitung & Backtesting-Fallstricke (Chan)]], dort auch die Panama-/
> Ratio-Adjustment-Verfahren. Ob die Level-Diskrepanz zwischen Continuous und Front Month
> materiell ist, ist gegen `raw/marktdaten/` noch nicht gemessen.

## Verwandt

- [[Futures-Datenaufbereitung & Backtesting-Fallstricke (Chan)]] — die quantitative Gegenseite
  (Rollover-Adjustment, Backtest-Verzerrung)
- [[Roll Return, Contango & Backwardation]], [[Premium vs. Carrying Charge Market]]
- [[Open Float & Liquidity Pools]] — die Level, die auf dem Continuous Contract gesucht werden
- [[Drei-Ebenen-Marktperspektive]], [[Three Timeframe Framing]] — Top-Down-Reihenfolge allgemein
- [[Kontraktspezifikation MNQ (Tick, Punktwert)]]
