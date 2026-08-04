---
tags: [synthesis, algo, backtest, generiert]
created: 2026-08-04
updated: 2026-08-04
sources: ["[[../../algo/explore_patterns.py]]", "[[../../algo/backtest_daily_patterns.py]]", "[[../../algo/backtest_seasonal.py]]"]
---

# Statistische Muster jenseits der ICT-Konzepte (laufend)

Reine Datenexploration ohne vorab formulierte ICT-These — Gegenstück zu den `backtest_*.py`-
Skripten, die eine konkrete Nutzeraussage prüfen. Ziel: Muster finden, die (noch) nicht als
benanntes Konzept im Wiki stehen. Zwei Stichproben: `algo/explore_patterns.py` (n≈34 Tage,
1m/5m-Auflösung, RTH 9:30–16:00) und `algo/backtest_daily_patterns.py` (n=147 Tage, 1d-Bars,
volle Globex-Session, 2026-01-02 bis 2026-08-04 — die 1d-Auflösung hat bei yfinance kein
30/60-Tage-Limit, deshalb die deutlich größere Stichprobe).

> **Laufende Seite**: wird bei wachsendem `raw/marktdaten/`-Bestand erneut gerechnet und hier
> aktualisiert (analog [[Muster-Validierung (laufend)]]). Ein Fund, der sich mit mehr Daten als
> Rauschen herausstellt, wird hier **gelöscht statt nur markiert** — anders als bei
> widersprüchlichen ICT-Primärquellen (dort bleibt beides stehen, siehe Seitenkonvention in
> [[../../CLAUDE.md]]), weil es hier keine zwei gleichwertigen Lehrmeinungen gibt, sondern eine
> einzige nachpruefbare Zahl.

> ⚠️ Die beiden Stichproben widersprechen sich teils (siehe unten) — ein Hinweis, dass die
> kleine Stichprobe (n≈34) für Wochentag-/Autokorrelations-Aussagen zu instabil ist. Wo beide
> vorliegen, zählt die n=147-Zahl mehr.

## 1. Montag: groß und bullish

Bei n=147 (volle Globex-Session) sticht **Montag klar heraus**: größte Median-Range aller
Wochentage (551,00 Pkt.) **und** deutlich bullish-verzerrt (**78,6 % bullish, n=28**) — alle
anderen Wochentage liegen bei 46–53 % (nahe Zufall).

| Tag | n | Median-Range | Bullish % |
|---|---|---|---|
| Mo | 28 | 551,00 | **78,6** |
| Di | 31 | 506,25 | 48,4 |
| Mi | 30 | 506,88 | 53,3 |
| Do | 30 | 491,88 | 50,0 |
| Fr | 28 | 467,00 | 46,4 |

Das ist **nicht** dasselbe wie die 70%-Wednesday-Regel aus [[One Shot One Kill Model]] (dort
geht es darum, *wann sich das Wochen-High/-Low bildet*, nicht um Montags eigene Richtung) und
auch nicht dieselbe Aussage wie „Wochenhoch/-tief bildet sich bevorzugt Montag" aus
[[Market Maker Manipulation Templates]]. Beide bestehenden Konzepte beschreiben *Timing*
innerhalb der Woche — dieser Fund beschreibt Montags eigene *Richtungs-Tendenz*, was bislang
nirgends im Wiki beziffert ist.

> Auf der kleinen Stichprobe (n≈34, nur die letzten ~7 Wochen) zeigte sich noch ein anderes
> Bild (Montag 50 % bullish, Mittwoch mit der größten Range) — bei n=8 pro Wochentag reiner
> Zufall möglich. Der Montags-Effekt gilt erst ab n=147 als belastbar, nicht schon vorher.
> **n=28 pro Wochentag ist immer noch klein** — 78,6 % ist ein echter, aber noch nicht
> bewiesener Befund. Naechster Check: haelt die Quote, sobald weitere Montage dazukommen?

**Gegenprobe pro Monat** (haelt der Montags-Vorsprung, oder kommt er nur aus einem starken
Trendmonat?): Montag schlaegt die uebrigen Wochentage in 5 von 7 Monaten mit brauchbarem n
(Jan 100 % vs. 53 %, Feb 67 % vs. 38 %, Mär 80 % vs. 24 %, Jun 100 % vs. 38 %, Jul 50 % vs.
33 %) — aber **nicht im Mai** (33 % vs. 76 %, dort war Montag sogar schwaecher) und im April
kein klarer Vorsprung (100 % vs. 82 %, beide Seiten in einem generell sehr bullishen Monat).
Der Effekt ist also kein Artefakt eines einzelnen Ausreißer-Monats, haelt aber auch nicht
ausnahmslos — Mai widerspricht offen. Wird bei jedem neuen Monat aktualisiert.

## 2. Range-Autokorrelation: echtes Volatility Clustering

Pearson r = **0,305** (n=146) zwischen der Tagesrange und der Range des Vortags — ein
moderater, positiver Zusammenhang. Auf einen Tag mit großer Range folgt statistisch eher
wieder ein Tag mit großer Range (und umgekehrt), nicht das Gegenteil. Bei der kleinen
Stichprobe war das noch nicht sichtbar (r=-0,07, im Rauschen) — auch das erst ab n=147 klar.

**Praktische Lesart**: nach einem ungewöhnlich großen Tag eher mit einem weiteren
Expansions-Tag rechnen statt automatisch eine ruhigere Konsolidierung zu erwarten.

## 3. Richtungs-Autokorrelation: schwaches Momentum

- Nach bullishem Tag: 58,8 % bullish am nächsten Tag (n=80) — leichtes Momentum.
- Nach bearishem Tag: 51,5 % bullish am nächsten Tag (n=66) — praktisch Zufall.

Schwächer als der Range-Effekt, aber in dieselbe Richtung (Fortsetzung statt Umkehr), zumindest
nach bullishen Tagen. Bei n≈34 zeigte sich hier fälschlich das Gegenteil (33,3 % nach bullish —
Reversion) — noch ein Beleg, dass die kleine Stichprobe nicht tragfähig war.

## 4. Rundzahl-Magnetismus: kein Effekt

Durchschnittlicher Abstand von Tages-High/-Low zur nächsten 50-Punkte-Marke: **12,25 Punkte**
(n=294) gegen 12,5 Punkte, die bei Gleichverteilung zu erwarten wären. Praktisch identisch —
**keine Evidenz**, dass Tagesextreme in diesem Datensatz runde Zahlen bevorzugen. Konsistentes
Nullresultat über beide Stichproben.

## 5. Turn-of-Month-Effekt: bestätigt sich in den eigenen Daten

Extern gut belegtes Phänomen (siehe Quellen unten): Renditen konzentrieren sich auf die
letzten Handelstage eines Monats plus die ersten paar Tage des Folgemonats. Getestet mit
`algo/backtest_seasonal.py` (letzter Handelstag + erste 3 des Folgemonats vs. Rest):

| | n | Ø-Tagesrendite | Bullish % | Ø-Range |
|---|---|---|---|---|
| TOM-Fenster | 28 | **+0,341 %** | **64,3** | 544,5 |
| Rest des Monats | 221 | +0,070 % | 52,5 | 578,0 |

Die TOM-Tage sind **nicht größer** in der Range (sogar leicht kleiner), aber deutlich
einseitiger bullish — passt zur externen Literatur (Kunkel/Compton/Beyer 2003, McConnell/Xu
2008: 4-Tage-Fenster in 19+ Ländern, ~15–20 Basispunkte Zusatzrendite pro Tag im TOM-Fenster
gegen ~0 sonst). Von den bisher getesteten Mustern das einzige mit externer Bestätigung UND
Bestätigung in den eigenen Daten.

## 6. Woche-im-Monat

| Woche (Tage) | n | Bullish % | Median-Range |
|---|---|---|---|
| 1 (1.–7.) | 34 | 61,8 | 528,00 |
| 2 (8.–14.) | 35 | 62,9 | 473,50 |
| 3 (15.–21.) | 32 | 50,0 | 479,38 |
| 4 (22.–28.) | 34 | **44,1** | 503,38 |
| 5 (29.–31., dünn) | 12 | 58,3 | 655,38 |

Woche 1+2 überschneiden sich teilweise mit dem Turn-of-Month-Fenster (Punkt 5) — kein
unabhängiger Fund. Woche 4 (44,1 % bullish, spürbar unter den anderen) ist dagegen **nicht**
durch TOM erklärt und noch unbeobachtet — möglicher Vorbote-Effekt vor dem TOM-Fenster, aber
bei n=34 noch nicht belastbar. Offener Punkt fürs nächste Update.

## 7. Monatszahlen 2026 gegen externe Nasdaq-Seasonality-Quellen

Mit nur 7 vollen Monaten (ein einziges Jahr) ist das **kein echter Mehrjahres-
Seasonality-Test** — Kalendermonate wiederholen sich hier nicht. Trotzdem als Rohbefund
gegen die extern behauptete 20-Jahres-Nasdaq-100-Saisonalität gehalten (Equity Clock/Barchart:
beste Monate historisch Jan, Mär, Apr, Mai, Jul, Aug, Okt, Nov; „Sell in May" gilt für
Tech/Nasdaq laut mehreren Quellen deutlich schwächer als für den S&P 500):

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

**Deckt sich**: April und Mai — beide historisch "beste Monate" laut Quellen, beide 2026
deutlich bullish. Mai speziell bestätigt auch die "Sell in May gilt für Tech kaum"-Beobachtung
aus der Literatur (Forbes: „S&P-Yes, Nasdaq-No").
**Widerspricht klar**: März und Juli — beide historisch "beste Monate", in 2026 aber die mit
Abstand schwächsten (36,4 % bullish, negative Ø-Rendite). Kein Beleg, dass die 20-Jahres-
Saisonalität sich in diesem einen Jahr wiederholt hat.

**Quellen** (Web-Recherche 2026-08-04):
- [E-Mini Nasdaq 100 Futures (NQ) Seasonal Chart – Equity Clock](https://equityclock.com/charts/e-mini-nasdaq-100-futures-nq-seasonal-chart/)
- [Nasdaq 100 E-Mini Futures Seasonal Returns – Barchart](https://www.barchart.com/futures/quotes/NQ*0/seasonality-chart)
- [Turn of the Month Effect – ETF Trends](https://www.etftrends.com/etf-strategist-channel/turn-month-effect/)
- [Turn of the Month in Equity Indexes – Quantpedia](https://quantpedia.com/strategies/turn-of-the-month-in-equity-indexes)
- [Selling Stocks In May? S&P-Yes, Nasdaq-No! – Forbes](https://www.forbes.com/sites/kennethwinans/2026/05/05/selling-stocks-in-may-sp-yes-nasdaq-no/)
- [Sell in May and Go Away? Testing the adage with 50 years of data – Deephaven](https://deephaven.io/blog/2026/05/08/sell-in-may/)

## Einordnung

**Am robustesten**: Punkt 5 (Turn-of-Month) — großes n, klarer Effekt, UND extern durch
unabhängige Forschung über 19+ Länder bestätigt. Punkt 1 (Montag) und 2 (Range-Autokorrelation)
sind ebenfalls solide (großes n, deutlicher Effekt), aber ohne externe Bestätigung gefunden —
Kandidaten für eigene Konzept-Seiten, falls sie sich halten. Punkt 3 ist schwächer und sollte
mit mehr Daten erneut geprüft werden. Punkt 4 ist ein stabiles Negativ-Ergebnis. Punkt 6
(Woche 4) ist ein neuer, noch unbestätigter Kandidat. Punkt 7 zeigt: die *externe* Monats-
Seasonality-Erwartung trifft in diesem einen Jahr nur teilweise zu (Apr/Mai ja, Mär/Jul klar
nein) — ohne Mehrjahresdaten kein belastbarer Test. Alle fünf Skripte laufen bei wachsendem
`raw/marktdaten/`-Bestand automatisch mit größerer Stichprobe erneut — siehe `algo/PLAN.md`-Log
für den Rohbefund.

## Verwandt

- [[One Shot One Kill Model]], [[Market Maker Manipulation Templates]] — bestehende
  Wochentags-Konzepte, die etwas anderes behaupten als Punkt 1
- [[TGIF (Thank God its Friday)]] — einziges anderes wochentagsspezifisches Konzept im Wiki
- [[Seasonal Tendency]] — bestehende Wiki-Seite zu saisonalen Tendenzen (allgemein, ohne
  Monatsdetails); Punkt 7 hier ist die erste konkrete Zahlenprüfung dagegen
- [[Muster-Validierung (laufend)]] — Schwesterseite fuer die ICT-PD-Array-Backtests
- `algo/PLAN.md` — vollstaendiger Log-Eintrag mit Methodik
