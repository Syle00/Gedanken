---
tags: [synthesis, algo, backtest, generiert]
created: 2026-08-04
updated: 2026-08-04
sources: ["[[../../algo/explore_patterns.py]]", "[[../../algo/backtest_daily_patterns.py]]"]
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

## Einordnung

Punkt 1 und 2 sind die robustesten Funde (großes n, deutlicher Effekt) und Kandidaten für
eigene Konzept-Seiten, falls sich das Muster mit wachsendem Datenstand hält. Punkt 3 ist
schwächer und sollte mit mehr Daten erneut geprüft werden. Punkt 4 ist ein stabiles
Negativ-Ergebnis. Alle vier Skripte laufen bei wachsendem `raw/marktdaten/`-Bestand automatisch
mit größerer Stichprobe erneut — siehe `algo/PLAN.md`-Log für den Rohbefund.

## Verwandt

- [[One Shot One Kill Model]], [[Market Maker Manipulation Templates]] — bestehende
  Wochentags-Konzepte, die etwas anderes behaupten als Punkt 1
- [[TGIF (Thank God its Friday)]] — einziges anderes wochentagsspezifisches Konzept im Wiki
- [[Muster-Validierung (laufend)]] — Schwesterseite fuer die ICT-PD-Array-Backtests
- `algo/PLAN.md` — vollstaendiger Log-Eintrag mit Methodik
