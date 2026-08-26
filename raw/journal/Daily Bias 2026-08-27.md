# Daily Bias 2026-08-27

> Weekly Bias: [[Weekly Bias KW35 2026]]
> Donnerstag, KW 35

## News (Red/Orange Folder)

Quelle: `forexfactory` (Feed-Woche 2026-08-23 – 2026-08-29)

**Do 27.08.**

🟠 **08:30 NY** / 14:30 DE — Unemployment Claims  (Forecast 208K, Previous 206K)

## Levels

**Datenlage:** 21 Handelstage mit 1s-Daten (2026-07-24 – 2026-08-21), kein Tag nur auf 1m,
keine in `1s-abdeckung.csv` registrierten Tage ohne Datei. Abgleich 1s gegen TradingView-1m:
max. Abweichung 2,50 Punkte (2026-08-20), sonst ≤ 2,00 — unauffällig.
Symbol: NQ.

| Level | Datum | Close (17:00) | Open (18:00) | Gap | C.E. | Status |
|---|---|---|---|---|---|---|
| NWOG | 2026-08-02 | 28287,00 | 28565,00 | +278,00 | 28426,00 | **offen** |
| NDOG | 2026-08-20 | 29317,25 | 29327,00 | +9,75 | 29322,00 | gefüllt |
| NDOG | 2026-08-19 | 29561,00 | 29561,50 | +0,50 | 29561,25 | gefüllt |
| NDOG | 2026-08-18 | 29559,50 | 29566,50 | +7,00 | 29563,00 | gefüllt |
| NDOG | 2026-08-17 | 30078,25 | 30077,00 | −1,25 | 30077,50 | gefüllt |
| NWOG | 2026-08-16 | 30154,00 | 30170,00 | +16,00 | 30162,00 | gefüllt |
| NDOG | 2026-08-13 | 30214,25 | 30210,75 | −3,50 | 30212,50 | gefüllt |
| NDOG | 2026-08-12 | 29805,75 | 29825,00 | +19,25 | 29815,50 | gefüllt |
| NDOG | 2026-08-11 | 29646,75 | 29657,75 | +11,00 | 29652,25 | gefüllt |
| NDOG | 2026-08-10 | 29764,25 | 29764,50 | +0,25 | 29764,50 | gefüllt |

**Gestrige Daily Range** (letzter verfügbarer Daily-Bar, 2026-08-13, Quelle 1d):
H 30272,75 / L 29780,50 / C 30188,50

_Weekly Range: keine Daten — Zeile ausgelassen._

### Offenes Gap — NWOG 2026-08-02 (Qs/Os/Hs)

Spanne 278,00 Punkte, Close 28287,00 (2026-07-31 16:59:59) → Open 28565,00 (2026-08-02 18:00:00).

| | Level |
|---|---|
| High (Open) | 28565,00 |
| O7 | 28530,25 |
| O6 / Q3 | 28495,50 |
| O5 | 28460,75 |
| **C.E. (= H1 = Q2 = O4)** | **28426,00** |
| O3 | 28391,25 |
| O2 / Q1 | 28356,50 |
| O1 | 28321,75 |
| Low (Close) | 28287,00 |

## Wiki-Bezug

- [[Weekly Range Trading Model]] — Donnerstag ist im Wochenprofil typischerweise der Tag, an dem die Weekly Range bereits steht oder final ausgereizt wird
- [[ICT Daily Range Session Timing]]
- [[Midnight Opening Range]]
- [[ORG (Opening Range Gap) & 1st Presented FVG]]
- [[New Day Opening Gap (NDOG)]]
- [[New Week Opening Gap (NWOG) Bias]] — für das noch offene 278-Punkte-Gap vom 2026-08-02
- [[Average Daily Range (5-Tage-ADR)]]
- [[ICT Macros & Leading Candles]]

## Einschaetzung (Claude)

**Wochentag-Statistik (MNQ, n=378 Donnerstage, 2019-05-06 – 2026-08-14, Quelle
`algo/seasonal_tendency.json`):** bullish 52,1 %, Ø-Return −0,012 %, Median-Range 281,38 Punkte,
Ø-Range 328,42 Punkte. Donnerstag ist damit der **richtungsloseste** Wochentag der Serie — die
Bullish-Quote liegt praktisch auf Münzwurf, der mittlere Return sogar minimal negativ. Zugleich
ist es der Tag mit der **größten Median-Range** aller fünf Wochentage. Lies das als: Bewegung
ja, Richtungsedge aus der Saisonalität nein. Ein Donnerstags-Bias sollte deshalb aus
Struktur/PD Arrays kommen, nicht aus dem Wochentag. Siehe
[[Seasonal Tendency (Eigene Daten, laufend)]].

**News:** Nur ein Orange-Folder-Event (Unemployment Claims, 08:30 NY). Kein Red Folder — kein
Anlass für den `backtest_fred_events.py`-Pfad. Claims sind der Standard-Donnerstagstermin und
liefern in der Regel nur einen kurzen Spike um 08:30 NY, keine Tagesstruktur. Praktische
Konsequenz: die AM-Session ist normal handelbar, die 09:30–11:00-Struktur wird nicht durch ein
Großevent überlagert.

**Offenes NWOG 2026-08-02 (28287,00–28565,00, C.E. 28426,00):** Das einzige noch ungefüllte Gap
im Betrachtungsfenster und damit formal ein Draw-on-Liquidity-Kandidat — aber es liegt rund
1.500 Punkte unter dem zuletzt gehandelten Bereich (Daily Close 2026-08-13: 30188,50). Für einen
einzelnen Handelstag ist das **kein Intraday-Ziel**, sondern ein Wochen-/Monatsziel. Führe es
als Level mit, plane aber nicht darauf.

**ORG-C.E.:** Für diesen Lauf liegen keine Live-Marktdaten vor, also kein ORG-Level. Die
ORG-C.E.-70%-These bleibt als *laufend beobachtete* Hypothese offen — eigene Messungen liegen
bislang bei 35–43 % und damit deutlich unter der Lehrmeinung; laut Nutzerentscheid nicht als
widerlegt abgehakt, sondern weiter erhoben.

**Fazit:** Neutrale Ausgangslage. Erwartungswert der Range hoch (Median 281 Punkte), Richtung
offen. Warte auf Midnight-Open-Bezug und die erste saubere Liquiditätsnahme in der AM-Session,
statt vorab eine Richtung festzulegen.

## Mein Bias

<!-- Jannes -->
