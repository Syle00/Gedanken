---
tags: [model, workflow, tooling, trading-ict]
created: 2026-08-02
updated: 2026-08-02
sources: ["[[Trading Journal & DOL Checklist]]", "[[ICT Daily Range Session Timing]]"]
---

# OHLC-Datenanalyse (Workflow)

Screenshot und CSV ersetzen sich nicht — sie beantworten verschiedene Fragen. Diese Seite hält
fest, wie beides zusammenspielt und was `tools/analyze_ohlc.py` daraus rechnet.

## Arbeitsteilung

| | Screenshot (PNG) | OHLC-CSV |
|---|---|---|
| Zeigt | **was du gesehen und markiert hast** | **was tatsächlich passiert ist** |
| Stark bei | Struktur, deine Einzeichnungen, dein Blickwinkel | exakte Preise, Zeiten, Distanzen |
| Schwach bei | exakte Preise (aus Pixeln geraten), Kerzen zählen | dem, was du wahrgenommen hast |
| Rolle im Journal | Beleg der Entscheidung | Korrektiv der Wahrnehmung |

Der Punkt ist das Korrektiv: ein als „Liquidity Sweep" markiertes Ereignis, das in den Daten nur
2 Ticks Durchstich hatte und darüber schloss, war kein Sweep. Das ist aus einem Bild nicht
belegbar, aus der CSV schon. Siehe [[Trading Journal & DOL Checklist]].

## Dateikonvention

```
raw/marktdaten/<SYMBOL> <YYYY-MM-DD> <TF>.csv
```

- `<YYYY-MM-DD>` = der **Handelstag**, um den es geht (Datum der letzten Kerze). Alle Timeframes
  eines Tages tragen dasselbe Datum, auch wenn der 1D-Export 289 Kerzen Historie enthält.
- `<TF>` ∈ `1m 5m 15m 1h 4h 1d`
- Spalten: `time,open,high,low,close[,volume]`. `time` als Unix-Timestamp (TradingView-Default)
  oder ISO-8601. **Zeitzone wird immer nach New York gerechnet**, weil das gesamte Vokabular
  (Killzones, Macros, Midnight Open) daran hängt.
- TradingView: `Chart → Export chart data`. Der Export enthält je nach Plan keine Volumenspalte —
  das Skript kommt ohne aus.

## Aufruf

```bash
python tools/analyze_ohlc.py MNQ 2026-07-31              # Tagesreport
python tools/analyze_ohlc.py MNQ 2026-07-31 --at 09:50   # Setup gegen die 8er-Checkliste
python tools/analyze_ohlc.py MNQ 2026-07-31 --tf 15m     # anderer Basis-Timeframe
```

Nur Standardbibliothek, keine Installation nötig.

## Was gerechnet wird

- **Opening Prices** — Midnight Open, 8:30, 9:30, 13:30 (siehe [[ICT Daily Range Session Timing]])
- **Session-Level** — Asia / London / London Lunch / NY AM / Premarket / London Close / Lunch /
  NY PM / RTH / IPDA True Range, je mit High, Low, Uhrzeit, Range und Equilibrium
- **HTF-Kontext** — 5-Tage-Range als Erwartungsanker gegen die tatsächliche Tagesrange
- **Liquidity Sweeps** — mit Alter des genommenen Levels und Durchstich in Punkten
- **Market Structure Breaks** — BOS/CHoCH, sequenziell getrackt
- **Displacement** — Kerzen über dem Vielfachen der Median-Range, mit Körperanteil
- **Fair Value Gaps** — Bereich, CE, Größe, Füllstand ([[Fair Value Gap (FVG)]])
- **Macro-Fenster** — Jannes' Stundenraster XX:50–XX+1:10, mit Expansion-Markierung
- **Consolidation-Phasen** und **unangetastete Liquidität**

## Zwei Detektor-Entscheidungen, die das Ergebnis prägen

**1. Ein Level braucht Alter.** Ein Swing High, das drei Kerzen alt ist, ist keine Liquidität —
dort liegen keine Stops. Ohne Mindestalter (`--min-age`, default skaliert mit dem Timeframe)
meldet der 1m-Chart eines einzigen Tages über 100 „Sweeps" und die Auswertung ist wertlos.

**2. Der Rückgang darf dauern.** Die naive Regel „Docht nimmt das Level, dieselbe Kerze schließt
zurück" übersieht genau den Fall, auf den es ankommt: der [[Judas Swing]] nimmt Buyside, hält
sich ein paar Kerzen darüber und kippt dann. Deshalb ein Bestätigungsfenster (`--confirm`).
Am 31.07.2026 lag der entscheidende Sweep um 09:31 — mit der Ein-Kerzen-Regel war er unsichtbar.

> Beides sind Konventionen, keine Wahrheiten. Wer die Schwellen verschiebt, bekommt andere
> Ereignisse. Die Defaults stehen im Skript und sind per CLI überschreibbar.

## Grenze der Checklisten-Prüfung

`--at` prüft **7 von 8** Punkten. „Entry" ist keine Eigenschaft des Marktes, sondern deine
Entscheidung — das Skript setzt den Haken nicht.

Punkt 8 („Target Liquidität min. 2 H/L 1m") wird ausdrücklich **nur mit dem Wissensstand zum
Setup-Zeitpunkt** gerechnet. Levels, die im Nachhinein unangetastet blieben, sind kein Ziel, das
zum Entry sichtbar war.

## Verwandt

- [[Trading Journal & DOL Checklist]] — die Checkliste, gegen die geprüft wird
- [[ICT Daily Range Session Timing]] — Herkunft der Session-Fenster
- [[ICT Macros & Leading Candles]] — das Stundenraster der Macros
- [[MNQ 2026-07-31 — Datenbasierter Tagesrückblick]] — erste Anwendung
