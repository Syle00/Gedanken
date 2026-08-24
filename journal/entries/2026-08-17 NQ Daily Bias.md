---
tags:
  - Daily-Bias
Bias:
  - Bullish
Date: 2026-08-17
NQ/ES: NQ
id: 2026-08-17-01
typ: daily-bias
modus: live
kw: 2026-W34
wochentag: Montag
liquidity_ziel: "Tagesziel PDH 30.283,00; Wochenziel Buyside-Pool 30.599,75 (30.06.); baerische Wochenziele NWOG-Open 30.170,00 und Asia-Sellside"
pd_arrays: [New Week Opening Gap (NWOG) Bias, BISI & SIBI (Buyside-Sellside Imbalance), Asian Range, Judas Swing, Open Float & Liquidity Pools, Equilibrium Vs. Discount, External vs. Internal Range Liquidity]
fehler: [P07]
---

# 2026-08-17 NQ Daily Bias

## Bias

**Bullish** für den Tag

## Timeline (NY)

- **02:18** — Preis 30.280,00 (08:18 DE), kurz unter der ersten Buyside 30.320,00. NWOG-Open bei 30.170,00 liegt darunter und ist unfilled - innerhalb der 1m-Kerze kurz baerish gehandelt.
- **—** — Asia hat konsolidiert und kaum Bewegung gezeigt - passt ins erwartete Muster fuer einen newsarmen Montag.
- **—** — NY-AM-Buyside vom Freitag genommen, Preis steht ueber dem C.E. des Daily BISI.
- **—** — Asia gibt eine Sellside her. Das 5m-Low liegt 0,25 Punkte unter den linken relativ gleichen Lows - fuer ihn weiter High Probability, die Sellside bleibt aktiv.
- **—** — Plan: NWOG-Open und Asia-Sellside als Wochenziele - oder heute als Judas Swing nach unten, um danach weiter bullish zu gehen.
- **—** — Daily Premium Wick vom 02.06. (Qs/Hs) wird selbst im 1m-Chart respektiert; dessen High ist zugleich der Buyside-Pool.
- **—** — Erwartung fuer NY: London liefert oft den Judas des Tages.

## Gefühlslage


> Bis jetzt passt alles zum Bias bin aber gesoant was in NY passiert, da London oft die Judas des Tages ist.

## Gegenprüfung (Claude, gegen `raw/marktdaten/`)

**NY-AM-Buyside vom Freitag — 30.280,50.** Aus den NQ-1s-Daten des 14.08.: High der NY-AM-Session
(09:30–11:00 NY) liegt bei **30.280,50**, gesetzt um **09:48:40**. Das ist ein *anderes* Level als
der PDH: der **PDH 30.283,00** entstand schon um **09:05:59**, also vor dem RTH-Open. Zwischen
seinem genannten Preis (30.280,00) und dem PDH liegen damit nur **2,50 Punkte** — die NY-AM-Buyside
ist der Nahzielpunkt, der PDH das eigentliche Tagesziel dahinter.

**„1. Buyside bei 30.320,00" — exakt bestätigt.** Das ist das **Tages-High vom 02.07.2026**
(NQ 1d: 30.320,00, auf den Tick). Zusätzlicher Kontext: das **Tages-Low vom 02.06.** liegt bei
30.317,75 — beide Level bilden ein 2,25-Punkte-Cluster, das den Bereich als Zone statt als
Einzellinie ausweist.

**Sellside 29.780,50** (aus [[Weekly Bias KW34 2026]]) = Tages-Low vom 13.08., aus dem
1m-Intraday-Aggregat bestätigt.

### Daily-Kerze 02.06.2026 (NQ)

`O 30.544,75 · H 30.763,25 · L 30.317,75 · C 30.712,75` — Up-Close.
High und Low sind unabhängig bestätigt (MNQ-1h-Aggregat derselben Session: H 30.763,50,
L 30.317,75 — 0,25 Punkte Micro/Mini-Spread beim High, Low identisch).

> ⚠️ **Der Close ist nicht bestätigt.** NQ-1d meldet 30.712,75, das MNQ-1h-Aggregat 30.743,00 —
> 30 Punkte Differenz. Weil der Body-Top den Premium Wick **startet**, verschiebt das die ganze
> Quadranten-Tabelle unten. Die Fassung hier folgt der NQ-1d-Datei; deine eingezeichneten Werte
> im Chart gehen vor.

Alle Level aus `python tools/qoh_levels.py`, auf das 0,25-Tickraster gerundet
([[Chain of Custody (Q-Validation)]]).

**Premium Wick** (Body-Top 30.712,75 → High 30.763,25) — 50,50 Punkte

| Stufe | Fib | Level | Preis |
| --- | --- | --- | --- |
| Qs | 0,0000 | Low (Body-Top) | 30.712,75 |
| Hs | 0,0625 | | 30.716,00 |
| Os | 0,1250 | | 30.719,00 |
| Hs | 0,1875 | | 30.722,25 |
| **Qs** | 0,2500 | **Q1** | **30.725,50** |
| Hs | 0,3125 | | 30.728,50 |
| Os | 0,3750 | | 30.731,75 |
| Hs | 0,4375 | | 30.734,75 |
| **Qs** | 0,5000 | **C.E / Mean Threshold** | **30.738,00** |
| Hs | 0,5625 | | 30.741,25 |
| Os | 0,6250 | | 30.744,25 |
| Hs | 0,6875 | | 30.747,50 |
| **Qs** | 0,7500 | **Q3** | **30.750,75** |
| Hs | 0,8125 | | 30.753,75 |
| Os | 0,8750 | | 30.757,00 |
| Hs | 0,9375 | | 30.760,00 |
| Qs | 1,0000 | High (= Buyside Pool) | **30.763,25** |

**Discount Wick** (Low 30.317,75 → Body-Bottom 30.544,75) — 227,00 Punkte

| Stufe | Fib | Level | Preis |
| --- | --- | --- | --- |
| Qs | 0,0000 | Low | **30.317,75** |
| Hs | 0,0625 | | 30.332,00 |
| Os | 0,1250 | | 30.346,25 |
| Hs | 0,1875 | | 30.360,25 |
| **Qs** | 0,2500 | **Q1** | **30.374,50** |
| Hs | 0,3125 | | 30.388,75 |
| Os | 0,3750 | | 30.403,00 |
| Hs | 0,4375 | | 30.417,00 |
| **Qs** | 0,5000 | **C.E / Mean Threshold** | **30.431,25** |
| Hs | 0,5625 | | 30.445,50 |
| Os | 0,6250 | | 30.459,75 |
| Hs | 0,6875 | | 30.473,75 |
| **Qs** | 0,7500 | **Q3** | **30.488,00** |
| Hs | 0,8125 | | 30.502,25 |
| Os | 0,8750 | | 30.516,50 |
| Hs | 0,9375 | | 30.530,50 |
| Qs | 1,0000 | High (Body-Bottom) | 30.544,75 |

**Gesamtrange der Kerze** (30.317,75 → 30.763,25) — 445,50 Punkte

| Stufe | Fib | Level | Preis |
| --- | --- | --- | --- |
| Qs | 0,0000 | Low | 30.317,75 |
| Hs | 0,0625 | | 30.345,50 |
| Os | 0,1250 | | 30.373,50 |
| Hs | 0,1875 | | 30.401,25 |
| **Qs** | 0,2500 | **Q1** | **30.429,25** |
| Hs | 0,3125 | | 30.457,00 |
| Os | 0,3750 | | 30.484,75 |
| Hs | 0,4375 | | 30.512,75 |
| **Qs** | 0,5000 | **C.E / Mean Threshold** | **30.540,50** |
| Hs | 0,5625 | | 30.568,25 |
| Os | 0,6250 | | **30.596,25** |
| Hs | 0,6875 | | 30.624,00 |
| **Qs** | 0,7500 | **Q3** | **30.652,00** |
| Hs | 0,8125 | | 30.679,75 |
| Os | 0,8750 | | 30.707,50 |
| Hs | 0,9375 | | 30.735,50 |
| Qs | 1,0000 | High | 30.763,25 |

Bemerkenswert: das **O bei 0,625 der Gesamtrange (30.596,25)** liegt 3,50 Punkte unter deinem
Wochenziel **30.599,75** (High vom 30.06.), und der **C.E. der Gesamtrange (30.540,50)** fällt
fast auf den Open der Kerze (30.544,75).

## Fehleranalyse

**Belegt:**

- **P07** — Kein Chartbild - Screenshot-Ordner 17-08-2026 existiert nicht. Die Level-Aussagen (NWOG-Open 30.170,00, Asia-Sellside, 5m-Low 0,25 unter den REL) sind spaeter nicht am Chart nachvollziehbar.

## Was gut lief

- Exakte Preise statt Naeherungswerten genannt - genau die Luecke, die am 13.08. noch als Datenluecke notiert wurde ('beim naechsten Mal exakte Preise statt Naeherungswerte mitloggen').
- Die '1. Buyside bei 30.320,00' ist gegen die Daten exakt belegbar: Tages-High vom 02.07.2026 (NQ 1d, 30.320,00 auf den Tick).
- Notiz vor London/NY geschrieben - der Bias ist damit nachpruefbar und nicht nachtraeglich rationalisiert.
- Sauber getrennt zwischen Tagesrichtung (bullish, PDH als Ziel) und Wochenrichtung (baerish, NWOG/Asia-Sellside als Draw) statt beides zu vermischen.

## Datenlücken

*Nicht bewertbar, weil die Information fehlt — beim nächsten Mal mitloggen.*

- P09: Bias noch nicht nachgehalten — nach Sessionende eintragen, ob er aufging. Ohne das bleibt die Trefferquote des Bias unbekannt.
- Kein Marktdatenstand fuer die laufende Session 17.08.: IB Gateway (Port 4002) nicht erreichbar, der yfinance-Pfad wurde am 16.08. aus dem Repo entfernt. NWOG-Open 30.170,00, der Preis 30.280,00, die Asia-Range/Sellside und 'NY-AM-Buyside genommen' sind damit heute nicht gegenpruefbar - nachziehen, sobald das Gateway laeuft.
- Grenzfall NY-AM-Buyside: das NY-AM-High vom Fr 14.08. liegt laut 1s-Daten bei 30.280,50 (09:48:40 NY). Sein genannter Preis 30.280,00 liegt 0,50 Punkte darunter - ob der Sweep wirklich schon durch ist, entscheidet sich in zwei Ticks und ist ohne heutige Daten offen.
- Der Daily-Close vom 02.06. ist quellenabhaengig: NQ-1d meldet 30.712,75, das MNQ-1h-Aggregat derselben Session 30.743,00 (30 Punkte Differenz). H/L sind unabhaengig bestaetigt (30.763,25 / 30.317,75), aber der Body-Top - und damit der Startpunkt der Premium-Wick-Quadranten - haengt an dieser Zahl.
- 1s-Historie hat eine Luecke vom 05.05. bis 12.08.2026 (Backfill laeuft); Juni-Intraday fuer NQ fehlt komplett, deshalb ist die 02.06.-Kerze nur ueber MNQ-1h plausibilisierbar.
- bias_korrekt noch offen - nach Sessionende gegen den Daily-Candle-Close nachtragen.

## Verwandt

Quelle des Freitexts: `raw/journal/Daily Bias 2026-08-17.md` · Wochenkontext:
[[Weekly Bias KW34 2026]] · Vortags-Eintrag: [[2026-08-13 MNQ Daily Bias]]

[[New Week Opening Gap (NWOG) Bias]], [[BISI & SIBI (Buyside-Sellside Imbalance)]], [[Asian Range]], [[Judas Swing]], [[Open Float & Liquidity Pools]], [[Equilibrium Vs. Discount]], [[External vs. Internal Range Liquidity]], [[Chain of Custody (Q-Validation)]]
