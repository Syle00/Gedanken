---
tags: [synthesis, algo, backtest, generiert]
created: 2026-08-04
updated: 2026-08-04
sources: ["[[../../algo/explore_patterns.py]]", "[[../../algo/backtest_daily_patterns.py]]", "[[../../algo/backtest_ndog.py]]"]
---

# Statistische Muster jenseits der ICT-Konzepte (laufend)

Reine Datenexploration ohne vorab formulierte ICT-These — Gegenstück zu den `backtest_*.py`-
Skripten, die eine konkrete Nutzeraussage prüfen. Ziel: Muster finden, die (noch) nicht als
benanntes Konzept im Wiki stehen. Zwei Stichproben: `algo/explore_patterns.py` (n≈34 Tage,
1m/5m-Auflösung, RTH 9:30–16:00) und `algo/backtest_daily_patterns.py` (n=147 Tage, 1d-Bars,
volle Globex-Session, 2026-01-02 bis 2026-08-04 — die 1d-Auflösung hat bei yfinance kein
30/60-Tage-Limit, deshalb die deutlich größere Stichprobe).

> **Alle kalendarischen Muster** (Wochentag, Turn-of-Month, Woche-im-Monat, Monatszahlen)
> stehen jetzt auf der eigenen Datenbank-Seite
> [[Seasonal Tendency (Eigene Daten, laufend)]], inkl. Abgleich gegen externe Quellen. Diese
> Seite hier behält die nicht-kalendarischen Funde.

> **Laufende Seite**: wird bei wachsendem `raw/marktdaten/`-Bestand erneut gerechnet und hier
> aktualisiert (analog [[Muster-Validierung (laufend)]]). Ein Fund, der sich mit mehr Daten als
> Rauschen herausstellt, wird hier **gelöscht statt nur markiert** — anders als bei
> widersprüchlichen ICT-Primärquellen (dort bleibt beides stehen, siehe Seitenkonvention in
> [[../../CLAUDE.md]]), weil es hier keine zwei gleichwertigen Lehrmeinungen gibt, sondern eine
> einzige nachpruefbare Zahl.

> ⚠️ Bei der kleinen Stichprobe (n≈34) zeigten sich unten teils andere Vorzeichen als bei der
> großen (n=147, siehe Punkt 1 und Punkt 2 unten) — ein Hinweis, dass n≈34 für
> Autokorrelations-Aussagen zu instabil ist. Wo beide vorliegen, zählt die n=147-Zahl mehr.

## 1. Range-Autokorrelation: echtes Volatility Clustering

Pearson r = **0,305** (n=146) zwischen der Tagesrange und der Range des Vortags — ein
moderater, positiver Zusammenhang. Auf einen Tag mit großer Range folgt statistisch eher
wieder ein Tag mit großer Range (und umgekehrt), nicht das Gegenteil. Bei der kleinen
Stichprobe war das noch nicht sichtbar (r=-0,07, im Rauschen) — auch das erst ab n=147 klar.

**Praktische Lesart**: nach einem ungewöhnlich großen Tag eher mit einem weiteren
Expansions-Tag rechnen statt automatisch eine ruhigere Konsolidierung zu erwarten.

## 2. Richtungs-Autokorrelation: schwaches Momentum

- Nach bullishem Tag: 58,8 % bullish am nächsten Tag (n=80) — leichtes Momentum.
- Nach bearishem Tag: 51,5 % bullish am nächsten Tag (n=66) — praktisch Zufall.

Schwächer als der Range-Effekt, aber in dieselbe Richtung (Fortsetzung statt Umkehr), zumindest
nach bullishen Tagen. Bei n≈34 zeigte sich hier fälschlich das Gegenteil (33,3 % nach bullish —
Reversion) — noch ein Beleg, dass die kleine Stichprobe nicht tragfähig war.

## 3. Rundzahl-Magnetismus: kein Effekt

Durchschnittlicher Abstand von Tages-High/-Low zur nächsten 50-Punkte-Marke: **12,25 Punkte**
(n=294) gegen 12,5 Punkte, die bei Gleichverteilung zu erwarten wären. Praktisch identisch —
**keine Evidenz**, dass Tagesextreme in diesem Datensatz runde Zahlen bevorzugen. Konsistentes
Nullresultat über beide Stichproben.

## 4. NDOG (New Day Opening Gap): Fill-Quote und Fortsetzung

Erster Detektor für NDOG/NWOG (bislang Backlog-Posten, siehe `algo/PLAN.md`): `ndog_gap()` in
`tools/analyze_ohlc.py`, Gap zwischen Vortages-Close und Tages-Open (Mitternacht-Grenze, anders
als das 16:14-verankerte [[ORG (Opening Range Gap) & 1st Presented FVG|ORG]]). Getestet mit
`algo/backtest_ndog.py` (n=146, 1d-Bars):

- **Korrelation |Gap| vs. Tagesrange**: r=0,264 — ein größeres NDOG geht tendenziell mit einem
  größeren Handelstag einher (schwächer als die 0,305 bei Punkt 1, gleiche Richtung).
- **Fill-Quote (selber Tag)**: 86,3 % insgesamt — **98,6 %** bei unterdurchschnittlichen Gaps,
  aber nur **74,0 %** bei überdurchschnittlich großen. Bestätigt quantitativ, was fürs ORG
  bereits qualitativ dokumentiert ist („Gap-Größe entscheidet über den Fill", siehe
  [[ORG (Opening Range Gap) & 1st Presented FVG]]) — hier zum ersten Mal beziffert, und für
  einen anderen Gap-Typ (NDOG statt ORG).
- **Gap-Richtung vs. Tagesrichtung**: nur 43,2 % Fortsetzung — der Tag läuft **öfter gegen**
  die Gap-Richtung als mit ihr. Leichte Fade-Tendenz, kein Momentum-Effekt.

Live-Tracking ergänzt: `algo/live_status.py` liefert jetzt ein `ndog`-Feld (Vortages-Close,
heutiger Open, Gap, Fill-Status) im JSON, `/algo-live-status` berichtet es mit — Nutzer-Vorgabe
vom 2026-08-04 ("NDOG/NWOG sind relevant, Opening-/Closing-Preise immer mitführen") damit
erstmals technisch umgesetzt statt nur vorgemerkt.

## Einordnung

Punkt 1 ist der robusteste Fund hier (großes n, deutlicher Effekt) und Kandidat für eine
eigene Konzept-Seite, falls er sich mit wachsendem Datenstand hält. Punkt 2 ist schwächer und
sollte mit mehr Daten erneut geprüft werden. Punkt 3 ist ein stabiles Negativ-Ergebnis. Punkt 4
bestätigt eine bestehende ICT-Regel quantitativ für einen neuen Gap-Typ. Für die kalendarischen
Funde (Montag-Effekt, Turn-of-Month, Woche-im-Monat, Monatszahlen) siehe
[[Seasonal Tendency (Eigene Daten, laufend)]]. Alle Skripte laufen bei wachsendem
`raw/marktdaten/`-Bestand automatisch mit größerer Stichprobe erneut — siehe `algo/PLAN.md`-Log
für den Rohbefund.

## Verwandt

- [[Seasonal Tendency (Eigene Daten, laufend)]] — Schwesterseite für alle kalendarischen
  Muster (Wochentag, Turn-of-Month, Woche-im-Monat, Monat)
- [[ORG (Opening Range Gap) & 1st Presented FVG]] — der andere, 16:14-verankerte Gap-Typ
- [[New Week Opening Gap (NWOG) Bias]] — NWOG (Wochen-Ebene), NDOG-Pendant fürs Wochenende
- [[Muster-Validierung (laufend)]] — Schwesterseite fuer die ICT-PD-Array-Backtests
- `algo/PLAN.md` — vollstaendiger Log-Eintrag mit Methodik
