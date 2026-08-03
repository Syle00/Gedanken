---
tags: [synthesis, trading-ict, marktdaten, mnq]
created: 2026-08-03
updated: 2026-08-03
sources: ["[[OHLC-Datenanalyse (Workflow)]]"]
raw: "raw/marktdaten/2026/08/03.08.2026/MNQ 2026-08-03 1m.csv"
---

# MNQ 2026-08-03 — Datenbasierter Tagesrückblick

Montag, ausgewertet aus `raw/marktdaten/2026/08/03.08.2026/MNQ 2026-08-03 {1m,5m,15m,1h,4h,1d}.csv` mit
`tools/analyze_ohlc.py`. Alle Zeiten New York. Zweite Anwendung von
[[OHLC-Datenanalyse (Workflow)]], erste Dateneingabe für [[../algo/PLAN.md|Algo-Trading-Projekt]].

> ⚠️ **Datenlücke:** Der 1m-Export deckt nur 11:19–16:18 NY ab (300-Kerzen-Limit von
> TradingView), nicht die volle Nacht/AM-Session. Für Opening Prices, Sessions und die
> AM-Sequenz unten wurde deshalb der **5m-Chart** als Basis verwendet (`--tf 5m`, deckt ab
> 31.07. 14:20 NY). Die Checkliste unten hat deshalb bei Punkt 8 keine belastbare Aussage für
> die AM-Session — dazu fehlt der 1m-Chart vor 11:19.
>
> ⚠️ Der Handelstag ist in diesen Daten **noch nicht beendet** — letzte Kerze 16:18 NY, nicht
> 17:00 (CME-Settlement). Zahlen unten sind Stand 16:18, kein finaler Tagesabschluss.

## Der Tag in einem Satz

Der RTH-Open (09:30) fiel exakt mit dem Tages-Low zusammen — ein Sweep der Sellside-Liquidität
von 08:05 direkt am Open, gefolgt von einer 166-Punkte-Displacement-Kerze (5,5x Median) um 09:35
und einer Rally bis 28 965,00 um 14:10.

## Eckdaten

| | |
|---|---|
| Tages-High | 28 965,00 um **14:10** |
| Tages-Low | 28 313,00 um **09:30** (= RTH-Open selbst) |
| Range (bis 16:18) | 652,00 Pkt · EQ 28 639,00 |
| Midnight Open | 28 670,00 |
| 8:30 Open | 28 450,00 |
| 9:30 Open (RTH) | 28 417,50 |
| 13:30 Open | 28 885,50 |
| Vortag (31.07.) | O 28 317,25 H 28 725,75 L 28 079,75 C 28 284,00 |

5-Tage-Range als Erwartungsanker: 625,75–1 205,25 Pkt (Median 825,25) → 652,00 Pkt liegen **im
Rahmen**, am unteren Ende.

**ORG (Opening Range Gap):** Vortagesschluss (1D-Close) 28 284,00 → RTH-Open 28 417,50 =
**+133,50 Pkt Gap up**. Siehe [[ORG (Opening Range Gap) & 1st Presented FVG]].

**Midnight-Open-Drift:** von 28 670,00 (00:00) auf 28 417,50 (RTH-Open) = −252,50 Pkt über
Nacht — der Markt lief die ganze Asia/London-Session abwärts, bevor der RTH-Open den Boden
markierte. Passt zur negativen-STD-Erwartung von [[Midnight Opening Range]] (Tages-Low unter
Midnight Open).

## Session-Verlauf (Basis 5m)

| Session | High | Low | Range |
|---|---|---|---|
| Asian Range | 28 698,25 (23:50) | 28 536,50 (20:25) | 161,75 |
| London Range | 28 667,50 (01:00) | 28 472,00 (04:30) | 195,50 |
| London Lunch | 28 601,50 (05:00) | 28 488,50 (06:25) | 113,00 |
| Premarket | 28 547,25 (07:00) | 28 382,75 (08:05) | 164,50 |
| **NY AM (7–10)** | **28 629,25 (09:55)** | **28 313,00 (09:30)** | **316,25** |
| London Close | 28 813,00 (11:50) | 28 525,00 (10:05) | 288,00 |
| Lunch | 28 847,50 (12:15) | 28 790,25 (12:00) | 57,25 |
| NY PM | 28 965,00 (14:10) | 28 812,75 (13:00) | 152,25 |

**Beobachtung:** wie am 31.07. bildete sich das Tages-Low nicht in London (195,50 Pkt Range,
eher ruhig), sondern exakt am RTH-Open. Zweiter Tag in Folge, an dem die NY-AM-Session (hier
316,25 Pkt) London klar schlägt — siehe [[ICT Daily Range Session Timing]] zur eigentlichen
Faustregel (London bevorzugt fürs Tages-High/-Low).

## Die entscheidende Sequenz

| Zeit | Ereignis | Beleg aus den Daten |
|---|---|---|
| 08:05 | Premarket-Low 28 382,75 | Level, das später gesweept wird |
| 09:00–09:25 | BOS bearish @ 28 439,00 | Close 28 417,00 |
| 09:25 | Sweep sellside @ 28 439,00 (5 Kerzen alt), +126,00 Pkt | Rückeroberung nach 2 Kerzen |
| **09:30** | **Sweep sellside @ 28 382,75 — Level stand seit 08:05 (17 Kerzen), +69,75 Pkt** | RTH-Open, zugleich Tages-Low |
| 09:35 | Displacement bullish, 166,25 Pkt (5,5x Median), größte Kerze des Tages | Sweep buyside @ 28 496,50 im selben Zug |
| 09:55 | CHoCH bullish @ 28 540,25 | Close 28 629,25 |
| 09:55 | Displacement bullish 115,50 Pkt (3,3x) | |
| 10:20 | BOS bullish @ 28 630,00 | Close 28 661,50 |
| 14:10 | Tages-High 28 965,00 | |

Muster: Sellside-Liquidität am RTH-Open genommen, sofortige Rückeroberung, dann Displacement
und Struktur-Shift zur Gegenseite — dieselbe Grundform wie der [[Judas Swing]] am 31.07., nur
diesmal am RTH-Open (09:30) statt im Judas-Fenster (00:00–05:00). Kein reiner Judas Swing im
Definitionssinn (der ist auf 0:00–5:00 begrenzt), aber strukturell verwandt: Sweep → sofortige
Displacement-Umkehr.

## Macro-Expansion

Median-Range eines Macro-Fensters an diesem Tag: 59,75 Pkt. Einziges Expansions-Fenster:

| Fenster | Range | Faktor |
|---|---|---|
| **09:50–10:10** | 175,00 | 2,9x |

Das 10:50–11:10-Macro — Ausführungsfenster des [[NY Lunch Macro Model]] bzw. der AM
[[Silver Bullet Model|Silver-Bullet-Session]] — lag mit 73,50 Pkt **unter** der
Expansionsschwelle (89,6 Pkt). Wie schon am 31.07. lief die eigentliche Bewegung bereits vorher
(damals 09:50–10:10, heute ebenfalls 09:50–10:10). Zwei von zwei Tagen mit demselben Muster —
bei n=2 noch kein Beweis, aber ein Kandidat für die erste Musterhypothese im
[[../algo/PLAN.md|Algo-Projekt]].

## Was der Tag über die Checkliste sagt

Prüfung mit `--at 09:30` (RTH-Open/Tages-Low) und `--at 09:50` (das Macro mit der Expansion):

| Punkt | 09:30 | 09:50 |
|---|---|---|
| Liq Sweep | **ja** | **ja** |
| Displacement | **ja** | **ja** |
| Anhaltende Consolidation | **ja** (08:30–09:25) | nein |
| Richtige Zeitfenster | nein (außerhalb Macro) | **ja** (Macro 09:50–10:10) |
| MS Break | **ja** (09:25 BOS bearish) | **ja** |
| Entry | — | — |
| Macro Expansion | nein | **ja** (2,9x) |
| Target Liquidität ≥2 H/L 1m | *keine Daten* (1m-Chart beginnt erst 11:19) | *keine Daten* |

09:30: 4/7 · 09:50: 5/7 (Punkt 8 jeweils nicht auswertbar, siehe Datenlücke oben — nicht als
„nein" zu werten).

## Offen am Handelsende (Stand 16:18)

- **Sellside:** 28 313,00 (09:30, Tages-Low, unangetastet) · 28 723,25 (11:25) · 28 810,00
  (12:40) · 28 812,75 (13:00)
- **Buyside:** 28 965,00 (14:10, Tages-High, unangetastet) · 28 943,75 (15:00) · 28 935,75
  (15:50)

Beide Tagesextreme stehen zum Datenende noch unangetastet — der Tag ist, wie oben vermerkt,
nicht abgeschlossen.

## Verwandt

- [[OHLC-Datenanalyse (Workflow)]] — wie diese Zahlen entstehen
- [[MNQ 2026-07-31 — Datenbasierter Tagesrückblick]] — erster Datenpunkt, gleiche Methode
- [[Judas Swing]], [[Fair Value Gap (FVG)]], [[ICT Daily Range Session Timing]]
- [[NY Lunch Macro Model]], [[Silver Bullet Model]], [[Midnight Opening Range]]
- [[ORG (Opening Range Gap) & 1st Presented FVG]]
- `algo/PLAN.md` — Planungsdokument für den eigenen Handelsalgorithmus, der diese Tage als
  Datengrundlage nutzt
