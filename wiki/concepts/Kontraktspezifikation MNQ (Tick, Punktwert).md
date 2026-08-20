---
tags: [concept, algo, marktdaten, mnq]
created: 2026-08-11
updated: 2026-08-20
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

## Eine Kontraktzahl ohne Instrument ist bedeutungslos (2026-08-20)

Jede Größenregel im Projekt — `max_kontrakte`, `max_kontrakte_pro_tag` in
`journal/config.yaml`, jede Aussage der Form „bei 6+ Kontrakten wird es schlecht" — ist an
**MNQ** kalibriert. Auf ein anderes Instrument übertragen ist dieselbe Zahl ein anderes Risiko:

| Position | Punktwert gesamt | entspricht in MNQ |
|---|---|---|
| 4 MNQ (Obergrenze) | $8 / Punkt | 4 |
| 2 MES | $10 / Punkt | 5 |
| 1 NQ | $20 / Punkt | **10** |
| **2 ES** | **$100 / Punkt** | **50** |

Erstbeleg 2026-08-19 (siehe [[2026-08-19 ES 1011 Silver Bullet]]): 2 ES-Kontrakte mit
7,25 Punkten Stop = **725 $** geplantes Risiko. Die automatische R09-Prüfung schlug **nicht**
an, weil 2 < 4 — das Skript zählt Stückzahl, nicht Punktwert. Die bindende Schranke ist deshalb
immer das **Risiko in Geld oder Prozent**, nie die Stückzahl; die Kontraktgrenze ist nur eine
für MNQ vorgerechnete Abkürzung davon.

Dieselbe Falle auf der Datenseite: MNQ ist kein Ersatz für NQ. Ein Substring-Filter auf
CFTC-Marktnamen hat schon einmal ein ES-Signal umgekehrt, weil er Micro und Mini zusammenwarf.

## Verwandt

- [[Chain of Custody (Q-Validation)]] — das Qs/Os/Hs-Raster, dessen Level gerundet werden müssen
- [[ORG (Opening Range Gap) & 1st Presented FVG]]
- [[Fair Value Gap (FVG)]]
- [[SMT (Smart Money Divergence)]] — Instrumentwechsel ist auch eine Größenfrage
