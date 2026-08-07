---
tags: [synthesis, algo, backtest, generiert, seasonal]
created: 2026-08-04
updated: 2026-08-07
sources: ["[[../../algo/backtest_seasonal.py]]", "[[../../algo/seasonal_tendency.json]]"]
---

# Seasonal Tendency (Eigene Daten, laufend)

Gegenstück zur ICT-Quellenseite [[Seasonal Tendency]] (dort: allgemeine ICT-Lehrmeinung ohne
konkrete Zahlen) — hier steht dieselbe Frage rein aus den eigenen MNQ-Daten beantwortet, als
laufend wachsende Datenbank statt einmaliger Behauptung.

> **Datenbank**: `algo/seasonal_tendency.json`, erzeugt von `algo/backtest_seasonal.py`.
> Maschinenlesbar strukturiert (Wochentag/Monat/Turn-of-Month/Woche-im-Monat je mit n,
> Bullish %, Ø-Tagesrendite, Median-/Ø-Range) — gedacht dafür, in einem Jahr Jahr-1 gegen
> Jahr-2 zu vergleichen, statt bei jeder neuen Frage von vorn zu rechnen. Skript einfach
> erneut laufen lassen, sobald `raw/marktdaten/` waechst; überschreibt die JSON und diese
> Seite wird danach von Hand nachgezogen (kein Auto-Write in den Wiki-Text, damit Einordnung/
> Prosa nicht verloren geht).
>
> **Lösch-statt-Markier-Regel**: stellt sich eine Zahl hier mit mehr Daten als Rauschen
> heraus, wird sie entfernt statt mit ⚠️ stehen gelassen — anders als bei widersprüchlichen
> ICT-Primärquellen. Siehe [[Statistische Muster jenseits der ICT-Konzepte (laufend)]] für die
> Begründung.

Stand: 147 Handelstage, 2026-01-02 bis 2026-08-04 (volle Globex-Session, 1d-Bars — 1d hat bei
yfinance kein Lookback-Limit, daher die deutlich groessere Stichprobe als die anderen
Backtests in diesem Vault).

## Wochentag

| Tag | n | Bullish % | Ø-Tagesrendite | Median-Range |
|---|---|---|---|---|
| Mo | 28 | **78,6** | **+0,71 %** | 551,00 |
| Di | 31 | 48,4 | −0,03 % | 506,25 |
| Mi | 30 | 53,3 | +0,14 % | 506,88 |
| Do | 30 | 50,0 | −0,06 % | 491,88 |
| Fr | 28 | 46,4 | +0,04 % | 467,00 |

Montag sticht klar heraus — höchste Bullish-Quote, höchste Ø-Rendite (+0,71 %, mehr als das
Fünffache jedes anderen Wochentags) und größte Range. Gegenprobe pro Monat (siehe
[[Statistische Muster jenseits der ICT-Konzepte (laufend)]]#1) zeigt: haelt in 5/7 Monaten,
Ausnahme Mai (dort war Montag schwaecher). **Nicht** dieselbe Aussage wie die 70%-Wednesday-
Regel ([[One Shot One Kill Model]]) oder "Wochenextrem bevorzugt Montag"
([[Market Maker Manipulation Templates]]) — beide beschreiben *Timing* des Wochenextrems,
nicht Montags eigene Richtung.

**Gegenprobe gegen Turn-of-Month-Überschneidung** (naheliegender Einwand: ist der Montags-
Effekt nur ein Nebenprodukt von Turn-of-Month, weil beide bullish sind?): nur 7 von 28 Montagen
liegen überhaupt im TOM-Fenster. Die übrigen 21 „reinen" Montage (kein TOM-Overlap) liegen bei
**76,2 % bullish, Ø-Rendite +0,70 %** — praktisch identisch zu den TOM-Montagen (85,7 %,
+0,73 %). Der Montags-Effekt ist also **kein** TOM-Artefakt, sondern hält unabhängig davon.

## Turn-of-Month

Extern sehr gut belegtes Phänomen (Kunkel/Compton/Beyer 2003, McConnell/Xu 2008 — siehe Links
unten). Fenster = letzter Handelstag des Monats + erste 3 Handelstage des Folgemonats.

> ✅ Korrektur (2026-08-07): Die `Rest des Monats`-Zeile war durch einen Doppelzaehlungs-Bug in
> `turn_of_month()` (`algo/backtest_seasonal.py`) verzerrt — die alte Akkumulation zaehlte Tage
> 4..Monatsende jedes Monats zweifach (`rs[:-1]` der eigenen Iteration UND `nrs[3:]` der
> Vor-Iteration ueberschnitten sich). Erkennbar allein an der Summe: Fenster (n=28) + Rest
> (n=221) = 249, mehr als die damals 147 Handelstage insgesamt. Fix: `rest` wird jetzt direkt
> als Komplement von `tom_days` ueber alle `rows` berechnet. Zahlen unten aktualisiert (Stand
> 150 Handelstage, 2026-01-02 bis 2026-08-07) — Fenster+Rest = 150 stimmt jetzt exakt.

| | n | Bullish % | Ø-Tagesrendite | Ø-Range |
|---|---|---|---|---|
| TOM-Fenster | 29 | **62,1** | **+0,419 %** | 580,64 |
| Rest des Monats | 121 | 52,9 | +0,071 % | 562,39 |

Bislang der robusteste Fund auf dieser Seite: extern **und** in den eigenen Daten bestätigt.
Nicht größer in der Range, aber deutlich einseitiger bullish.

## Woche-im-Monat

| Woche (Tage) | n | Bullish % | Median-Range |
|---|---|---|---|
| 1 (1.–7.) | 34 | 61,8 | 528,00 |
| 2 (8.–14.) | 35 | 62,9 | 473,50 |
| 3 (15.–21.) | 32 | 50,0 | 479,38 |
| 4 (22.–28.) | 34 | **44,1** | 503,38 |
| 5 (29.–31., dünn) | 12 | 58,3 | 655,38 |

Woche 1+2 überschneiden mit dem Turn-of-Month-Fenster oben (kein unabhängiger Fund). Woche 4
fällt unerwartet ab (44,1 % bullish) — noch unbestätigt, nicht durch TOM erklärt, Kandidat für
den nächsten Check.

## Monat (Rohbefund — kein Mehrjahres-Test)

Nur 1 Jahr Historie, Kalendermonate wiederholen sich noch nicht — das hier ist **kein**
belastbarer Jahres-Seasonality-Test, sondern der erste Datenpunkt für einen, der sich über
mehrere Jahre aufbaut.

| Monat 2026 | n | Bullish % | Ø-Tagesrendite |
|---|---|---|---|
| Jan | 20 | 60,0 | +0,05 % |
| Feb | 19 | 42,1 | −0,06 % |
| Mär | 22 | 36,4 | −0,00 % |
| Apr | 21 | **85,7** | **+0,80 %** |
| Mai | 20 | 70,0 | +0,49 % |
| Jun | 21 | 52,4 | −0,06 % |
| Jul | 22 | 36,4 | −0,40 % |
| Aug | 2 | 100,0 (n=2, kaum aussagekräftig) | +0,84 % |

Abgleich gegen externe 20-Jahres-Nasdaq-100-Seasonality (Equity Clock/Barchart: beste Monate
historisch Jan/Mär/Apr/Mai/Jul/Aug/Okt/Nov): **April und Mai passen** (beide historisch stark,
beide 2026 stark bullish — Mai bestätigt auch "Sell in May gilt für Tech kaum", Forbes).
**März und Juli widersprechen klar** (beide historisch "beste Monate", 2026 aber die
schwächsten mit 36,4 % bullish). Ein Jahr beweist nichts — diese Zeile wird jedes Jahr um
eine Spalte länger, bis ein echter Mehrjahresvergleich möglich ist.

## Externe Quellen (Web-Recherche 2026-08-04)

- [E-Mini Nasdaq 100 Futures (NQ) Seasonal Chart – Equity Clock](https://equityclock.com/charts/e-mini-nasdaq-100-futures-nq-seasonal-chart/)
- [Nasdaq 100 E-Mini Futures Seasonal Returns – Barchart](https://www.barchart.com/futures/quotes/NQ*0/seasonality-chart)
- [Turn of the Month Effect – ETF Trends](https://www.etftrends.com/etf-strategist-channel/turn-month-effect/)
- [Turn of the Month in Equity Indexes – Quantpedia](https://quantpedia.com/strategies/turn-of-the-month-in-equity-indexes)
- [Selling Stocks In May? S&P-Yes, Nasdaq-No! – Forbes](https://www.forbes.com/sites/kennethwinans/2026/05/05/selling-stocks-in-may-sp-yes-nasdaq-no/)
- [Sell in May and Go Away? Testing the adage with 50 years of data – Deephaven](https://deephaven.io/blog/2026/05/08/sell-in-may/)

## Verwandt

- [[Seasonal Tendency]] — die ICT-Quellenseite, die hier gegengeprüft wird
- [[Statistische Muster jenseits der ICT-Konzepte (laufend)]] — Schwesterseite für
  nicht-kalendarische Muster (Range-/Richtungs-Autokorrelation, Rundzahl-Magnetismus)
- [[One Shot One Kill Model]], [[Market Maker Manipulation Templates]], [[TGIF (Thank God its Friday)]]
  — bestehende ICT-Wochentags-/Wochenzeit-Konzepte
- [[Muster-Validierung (laufend)]] — Schwesterseite für die ICT-PD-Array-Backtests
- `algo/PLAN.md` — vollständiger Log-Eintrag mit Methodik
