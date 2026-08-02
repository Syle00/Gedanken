---
tags: [synthesis, trading-ict, marktdaten, mnq]
created: 2026-08-02
updated: 2026-08-02
sources: ["[[OHLC-Datenanalyse (Workflow)]]"]
raw: "raw/marktdaten/MNQ 2026-07-31 1m.csv"
---

# MNQ 2026-07-31 — Datenbasierter Tagesrückblick

Freitag, ausgewertet aus `raw/marktdaten/MNQ 2026-07-31 {1m,5m,15m,1h,4h,1d}.csv` mit
`tools/analyze_ohlc.py`. Alle Zeiten New York. Erste Anwendung von
[[OHLC-Datenanalyse (Workflow)]] — kein Trade-Eintrag, sondern die Marktseite des Tages.

## Der Tag in einem Satz

Ein Freitag, an dem die gesamte Tagesrange in 41 Minuten entstand: Judas Swing auf ein
252 Kerzen altes High um 09:31, dann 646 Punkte nach unten bis 10:16 — danach passierte
nichts Wesentliches mehr.

## Eckdaten

| | |
|---|---|
| Tages-High | 28 725.75 um **09:35** |
| Tages-Low | 28 079.75 um **10:16** |
| Range | 646.00 Pkt · EQ 28 402.75 |
| Midnight Open | 28 459.00 |
| 8:30 Open | 28 494.75 |
| 9:30 Open | 28 576.25 |
| Close (16:59) | 28 284.00 |

5-Tage-Range als Erwartungsanker: 625.75–1 205.25 Pkt (Median 825.25) → die tatsächlichen
646 Pkt liegen **am unteren Rand des Erwartungsrahmens**, aber im Rahmen.

## Session-Verlauf

| Session | High | Low | Range |
|---|---|---|---|
| Asian Range (20–24) | 28 580.00 (21:15) | 28 389.75 (22:37) | 190.25 |
| London (1–5) | 28 612.25 (02:14) | 28 450.25 (02:48) | 162.00 |
| London Lunch (5–7) | 28 642.00 (05:10) | 28 519.25 (06:06) | 122.75 |
| Premarket (7–9:30) | 28 626.00 (07:08) | 28 432.00 (08:42) | 194.00 |
| **NY AM (7–10)** | **28 725.75 (09:35)** | **28 294.75 (09:54)** | **431.00** |
| London Close (10–12) | 28 392.00 (10:00) | 28 079.75 (10:16) | 312.25 |
| Lunch (12–13) | 28 391.00 (12:58) | 28 242.00 (12:07) | 149.00 |
| NY PM (13–16) | 28 524.50 (15:54) | 28 359.75 (13:00) | 164.75 |

**Beobachtung:** High *und* Low des Tages fielen in das Fenster 09:30–10:16 — also weder in
London noch in der PM-Session. Das widerspricht der Faustregel aus
[[ICT Daily Range Session Timing]], nach der sich das Tages-High/-Low bevorzugt in London
bildet (0–5 Uhr Manipulationsfenster). Hier lag London mit 162 Pkt Range praktisch flach; die
Manipulation kam erst mit dem 9:30-Open.

> ⚠️ Ein einzelner Tag widerlegt keine Statistik. Notiert als Datenpunkt, nicht als Korrektur
> der Wiki-Aussage. Der Freitag ist zudem der [[Market Maker Manipulation Templates|Seek-&-Destroy]]-Kandidat
> der Woche — das passt eher zum beobachteten Muster als das London-Profil.

## Die entscheidende Sequenz

| Zeit | Ereignis | Beleg aus den Daten |
|---|---|---|
| 09:10 | CHoCH bullish @ 28 491.00 | Close 28 527.00 |
| 09:25 | Sweep buyside @ 28 560.00 (87 Kerzen alt), +54.00 Pkt | Rückeroberung nach 1 Kerze |
| 09:30 | RTH Open 28 576.25 | |
| **09:31** | **Sweep buyside @ 28 627.75 — Level stand seit 05:19 (252 Kerzen), +98.00 Pkt** | sofortige Rückeroberung |
| 09:31–09:35 | Displacement bullish, 3 Kerzen über 3x Median-Range | 49.00 / 42.00 / 46.00 Pkt |
| 09:35 | Tages-High 28 725.75 | |
| 09:38 | Displacement bearish 79.50 Pkt (3.7x), größte Kerze des Tages | hinterlässt bearish FVG 28 611.00–28 645.75 |
| 09:40–09:48 | fünf Sellside-Sweeps in Folge, darunter Levels von **23:12** (634 Kerzen) und **19:38** (849 Kerzen) | 121 / 127 / 112 / 77 / 56 Pkt Durchstich |
| 09:50–10:10 | Macro mit **293.25 Pkt Range** = 4.6x Tagesmedian | |
| 10:16 | Tages-Low 28 079.75 | |

Das ist ein lehrbuchmäßiger [[Judas Swing]]: ein über Nacht stehengebliebenes High wird zum
RTH-Open um fast 100 Punkte überschossen, sofort zurückerobert, und die Gegenbewegung räumt in
acht Minuten die Sellside-Liquidität von Asia und Vorabend ab.

Der bearish FVG von 09:38 (28 611.00–28 645.75) blieb **bis Handelsschluss ungefüllt**.

## Macro-Expansion

Median-Range eines Macro-Fensters an diesem Tag: 63.75 Pkt. Drei Fenster gelten als Expansion:

| Fenster | Range | Faktor |
|---|---|---|
| **09:50–10:10** | 293.25 | 4.6x |
| 11:50–12:10 | 120.50 | 1.9x |
| 15:50–16:10 | 184.00 | 2.9x |

Das 10:50–11:10-Macro — das Ausführungsfenster des [[NY Lunch Macro Model]] — lag mit 92.00 Pkt
**unter** der Expansionsschwelle. Wer an diesem Tag auf das Lunch-Setup gewartet hat, hat auf
das falsche Fenster gewartet; die Bewegung war um 10:16 gelaufen.

## Was der Tag über die Checkliste sagt

Prüfung mit `--at 09:50` (dem Macro, in dem die Expansion lief):

| Punkt | Daten |
|---|---|
| Liq Sweep | **ja** — drei Sellside-Sweeps zwischen 09:46 und 09:48 |
| Displacement | **ja** — 09:31 bis 09:33, bis 3.9x Median |
| Anhaltende Consolidation | **ja** — 08:50–09:29, zwei Blöcke à 20 Kerzen |
| Richtige Zeitfenster | **ja** — Macro 09:50–10:10, Session NY AM |
| MS Break | **ja** — 09:10 CHoCH bullish, 09:34 BOS bullish |
| Entry | — deine Entscheidung |
| Macro Expansion | **ja** — 4.6x |
| Target Liquidität ≥2 H/L 1m | **nein** — zum Zeitpunkt 09:50 war 1 Buyside-Level offen, kein Sellside-Level |

**6 von 7 prüfbaren Punkten.** Der eine fehlende ist aufschlussreich: um 09:50 war die
Sellside-Liquidität bereits abgeräumt — es gab kein sauberes 1m-Ziel mehr unter dem Preis. Der
Move lief trotzdem noch 281 Punkte tiefer. Das ist genau die Situation, in der die Checkliste
konservativ ist und der Markt nicht.

## Offen am Handelsende

Unangetastete Liquidität (1m, Stand 16:59):

- **Sellside:** 28 115.50 (11:34) · 28 163.50 (11:43) · 28 165.25 (11:47) · 28 242.00 (12:07) · 28 256.00 (12:16)
- **Buyside:** 28 524.50 (15:54) · 28 406.00 (16:13) · darüber der ungefüllte FVG 28 611.00–28 645.75

Der Tag schloss bei 28 284.00 — zwischen beiden Clustern, näher an der Sellside.

## Verwandt

- [[OHLC-Datenanalyse (Workflow)]] — wie diese Zahlen entstehen
- [[Judas Swing]], [[Fair Value Gap (FVG)]], [[ICT Daily Range Session Timing]]
- [[Market Maker Manipulation Templates]] — Seek & Destroy Friday
- [[NY Lunch Macro Model]]
