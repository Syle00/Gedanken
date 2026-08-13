---
tags: [synthesis, trading-ict, marktdaten, mnq, mor, fvg]
created: 2026-08-13
updated: 2026-08-13
sources: ["[[OHLC-Datenanalyse (Workflow)]]", "[[Midnight Opening Range]]", "[[Fair Value Gap (FVG)]]"]
raw: "raw/marktdaten/2026/08/13.08.2026/MNQ 2026-08-13 1m.csv"
---

# MNQ 2026-08-13 — MOR & FVG

Donnerstag, ausgewertet aus `raw/marktdaten/2026/08/13.08.2026/MNQ 2026-08-13 1m.csv` mit
`tools/analyze_ohlc.py` (`algo/mor_levels.py` für die MOR-Level, `fvgs()` für die FVGs). Alle
Zeiten New York. Anlass war eine Fehlersuche: die Opening-Range-Preise „stimmten nicht" — das
Ergebnis steht unten unter *Datenbefund*.

> ⚠️ **Teiltag:** Der 1m-Export reicht nur bis **07:44 NY** (Session noch offen). MOR (0:00–0:30)
> und die London-Session (1:00–5:00) sind vollständig; NY AM/PM fehlen noch.

## Datenbefund (Fehlersuche 2026-08-13)

Die Rohdaten sind **korrekt**: die Kerze aus dem Chart (00:01 NY, O 29.877,25 / H 29.878,00 /
L 29.876,50 / C 29.877,00) liegt ziffernidentisch in der Datei, die Zeitzone stimmt
(Epoch → UTC → New York, EDT −04:00) und die Minuten 00:00–00:29 sind vollständig (30/30). Kein
Zeitzonen- und kein Export-Lückenfehler.

Ursache der „falschen Preise" war eine **Fenster-Verwechslung im Code**: `session_windows()` in
`tools/analyze_ohlc.py` kannte **kein MOR-Fenster** und nannte 1:00–5:00 „London Range". Wer im
allgemeinen Tagesreport nach der „London/Opening Range" schaute, bekam die **1–5-Uhr-Range**
(High 29.924,25 / Low 29.827,50) statt der 0:00–0:30-MOR. **Fix:** MOR (0:00–0:30) als eigenes
Fenster ergänzt, 1:00–5:00 klar als „London Session" benannt.

## Midnight Opening Range (0:00–0:30 NY)

Siehe [[Midnight Opening Range]]. Werte aus `algo/mor_levels.py 2026-08-13`.

| Größe | Wert |
|---|---|
| Midnight Open | **29.878,25** |
| Range High | **29.892,25** |
| Range Low | **29.854,00** |
| Range | **38,25 Pkt** |
| C.E. (Q 0,50) | 29.873,12 |
| Q 0,25 / Q 0,75 | 29.863,56 / 29.882,69 |
| +1 STD / −1 STD | 29.930,50 / 29.815,75 |
| +2 STD / −2 STD | 29.968,75 / 29.777,50 |

**Setzten die STD-Level das Tagesextrem?** (offene Jannes-These, 2026-08-11)

- **Tages-High 29.924,25 um 01:31** → k = **0,84 STD**, nur **6,25 Pkt (0,16× Range)** unter dem +1-STD-Level.
- **Tages-Low 29.821,25 um 05:15** → k = **0,86 STD**, nur **5,50 Pkt (0,14× Range)** über dem −1-STD-Level.

Beide Extreme landeten also **knapp innerhalb ±1 STD** — an diesem Tag stützt das die STD-Projektions-These
(Extrem nahe ±1 STD). Ein Einzeltag, kein Beleg; die Statistik über viele Tage macht
`algo/backtest_midnight_range_std.py`.

## First Presentation FVG (erstes FVG in der MOR)

Siehe [[ORG (Opening Range Gap) & 1st Presented FVG]]. Das erste FVG *innerhalb* 0:00–0:30 wird
laut Wiki den Tag mitgeführt:

- **bullish**, 29.877,00 – 29.879,00, **C.E. 29.878,00**, Größe **2,00 Pkt**, entstanden **00:02**, gefüllt **00:13**.

Einordnung: Mit 2,00 Pkt liegt es **unter der 10-Punkte-Schwelle**, ab der sich FVGs laut
[[Fair Value Gap (FVG)]]-Auswertung überhaupt als „besonders" abheben — es gehört zur häufigen,
nicht zur selektiven Sorte und wurde nach 11 Minuten gefüllt.

## FVG-Statistik des Tages (0:00–07:44 NY)

`fvgs()` über die Session bis Datenende: **91 FVGs**, davon nur **6 ≥ 10 Pkt** — die große
Mehrheit ist klein (bestätigt „ein FVG allein selektiert nichts"; erst die Größe filtert). Die
großen FVGs clustern in der **London-Expansion 04:02–04:08**:

| Zeit | Seite | Bereich | C.E. | Größe | Fill |
|---|---|---|---|---|---|
| 03:02 | bearish | 29.875,50–29.887,00 | 29.881,25 | 11,50 | gefüllt 07:00 (hielt ~4 h) |
| 04:02 | bearish | 29.851,75–29.866,75 | 29.859,25 | 15,00 | gefüllt 04:51 |
| 04:03 | bearish | 29.836,75–29.852,00 | 29.844,38 | 15,25 | gefüllt 04:06 |
| 04:06 | bullish | 29.838,00–29.859,50 | 29.848,75 | 21,50 | gefüllt 04:08 |
| 04:08 | bearish | 29.835,00–29.853,25 | 29.844,12 | 18,25 | gefüllt 04:24 |
| 05:14 | bearish | 29.832,25–29.844,00 | 29.838,12 | 11,75 | gefüllt 05:23 |

Noch **offen** bei Datenende: das bearische FVG von **01:32** (29.910,00–29.918,50, C.E. 29.914,25,
8,50 Pkt) — es markiert die Zone knapp über dem Tages-High.

## Verwandt

- [[Midnight Opening Range]], [[Fair Value Gap (FVG)]], [[ORG (Opening Range Gap) & 1st Presented FVG]]
- [[../algo/PLAN.md|Algo-Trading-Projekt]] — Fix `session_windows` (MOR-Fenster), siehe Log
- Tool: `algo/mor_levels.py` (Tages-Readout), `algo/backtest_midnight_range_std.py` (STD-Statistik)
