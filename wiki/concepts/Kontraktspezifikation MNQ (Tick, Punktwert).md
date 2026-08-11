---
tags: [concept, algo, marktdaten, mnq]
created: 2026-08-11
updated: 2026-08-11
sources: []
---

# Kontraktspezifikation MNQ (Tick, Punktwert)

Die harten Kontraktdaten, gegen die jede Preisberechnung im Projekt geprüft werden muss.
Hinterlegt nach zweifacher Nutzerkorrektur am 2026-08-11.

## Tick-Größe: 0,25 Punkte

> **Der Future bewegt sich ausschließlich in 0,25-Punkt-Schritten.** Preise dazwischen —
> 29 833,34 oder 29 299,225 — existieren am Markt nicht. Sie sind weder handelbar noch als
> Order platzierbar; IBKR weist sie ab oder rundet still.

| Symbol | Tick | Punktwert | Tickwert |
|---|---|---|---|
| **MNQ** | 0,25 | $2,00 | $0,50 |
| NQ | 0,25 | $20,00 | $5,00 |
| ES | 0,25 | $50,00 | $12,50 |
| MES | 0,25 | $5,00 | $1,25 |

Forex zum Vergleich (andere Größenordnung, nicht pauschal 0,25 annehmen): die meisten Paare
0,00001, JPY-Paare 0,001.

## Wo im Code das lebt

`tools/analyze_ohlc.py::TICK_SIZE` ist die **einzige Quelle der Wahrheit**; `algo/pnl.py`
importiert von dort und reicht sie als `round_to_tick()` an die `algo/`-Module weiter. Der
Punktwert liegt daneben in `algo/pnl.py::POINT_VALUE`.

## Welche Werte betroffen sind

Nicht die Kursdaten selbst — die kommen tick-konform aus der Börse. Betroffen ist alles
**Abgeleitete**:

- **C.E. / Mean Threshold** — ein Mittelwert `(lo + hi) / 2` landet zur Hälfte genau zwischen
  zwei Ticks. Betraf 50 % aller [[Fair Value Gap (FVG)|FVG]]-C.E.
- **Quadranten / Oktanten / 16tel** ([[Chain of Custody (Q-Validation)|Qs/Os/Hs]]) — teilt die
  Range nicht glatt durch 16, liegt kein einziges Zwischenlevel auf dem Raster.
- **Stops aus prozentualen Puffern** — erzeugen beliebige Nachkommastellen.

## Rundungsrichtung bei Order-Preisen

Analyse-Level werden auf den nächsten Tick gerundet. **Order-Preise dagegen gerichtet**, damit
die Rundung nie zugunsten des Backtests ausfällt:

| Preis | Long | Short |
|---|---|---|
| Entry (Limit) | abrunden | aufrunden |
| Stop | abrunden | aufrunden |
| Ziel | aufrunden | abrunden |

Also immer so, dass der Entry schwerer zu füllen und Stop wie Ziel weiter entfernt sind.

## Verwandt

- [[Chain of Custody (Q-Validation)]] — das Qs/Os/Hs-Raster, dessen Level gerundet werden müssen
- [[ORG (Opening Range Gap) & 1st Presented FVG]]
- [[Fair Value Gap (FVG)]]
