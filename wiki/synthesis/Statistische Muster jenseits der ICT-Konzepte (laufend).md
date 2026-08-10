---
tags: [synthesis, algo, backtest, generiert]
created: 2026-08-04
updated: 2026-08-10
sources: ["[[../../algo/explore_patterns.py]]", "[[../../algo/backtest_daily_patterns.py]]", "[[../../algo/backtest_ndog.py]]", "[[../../algo/backtest_nwog.py]]", "[[../../algo/backtest_tgif.py]]", "[[../../algo/backtest_1m_gaps.py]]"]
---

# Statistische Muster jenseits der ICT-Konzepte (laufend)

Reine Datenexploration ohne vorab formulierte ICT-These — Gegenstück zu den `backtest_*.py`-
Skripten, die eine konkrete Nutzeraussage prüfen. Ziel: Muster finden, die (noch) nicht als
benanntes Konzept im Wiki stehen. Zwei Stichproben: `algo/explore_patterns.py` (n=43 Tage,
1m/5m-Auflösung, RTH 9:30–16:00) und `algo/backtest_daily_patterns.py` (n=147 Tage, 1d-Bars,
volle Globex-Session, 2026-01-02 bis 2026-08-04 — die 1d-Auflösung hat bei yfinance kein
30/60-Tage-Limit, deshalb die deutlich größere Stichprobe).

> ✅ Korrektur (2026-08-08): Die `explore_patterns.py`-Zahlen unten (n≈34, r=-0,07, 33,3 %)
> waren durch einen Bug in der gemeinsam genutzten `find_days()` (`algo/backtest_org_ce.py`)
> verzerrt — ohne Symbol-Filter griff sie faktisch deterministisch zugunsten von ES statt MNQ
> (alphabetisch vor MNQ, kein `sorted()` auf die Kandidatenliste), 40 von 45 betroffenen Tagen
> lieferten die ES- statt der MNQ-Datei. `explore_patterns.py` lief also grossteils auf dem
> falschen Instrument. Fix (Task 8, 2026-08-07): `find_days(symbol="MNQ")` filtert jetzt
> korrekt. Zahlen unten auf einen frischen Lauf mit echten MNQ-Daten aktualisiert (n=43 statt
> ≈34 — die Differenz ist ueberwiegend seit 2026-08-04 gewachsener `raw/marktdaten/`-Bestand,
> nicht der Bug selbst). Details: `algo/PLAN.md`-Log vom 2026-08-07. Die `backtest_daily_patterns.py`-Zahlen
> (n=147, Punkt 1–3 grosse Stichprobe) nutzen `find_1d_days()` aus `backtest_common.py`, einen
> anderen, vom Bug nicht betroffenen Pfad — die bleiben unveraendert.

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

> ⚠️ Bei der kleinen Stichprobe (n=43) bleiben Punkt 1 und Punkt 2 deutlich schwächer als bei
> der großen (n=147, siehe unten) — ein Hinweis, dass n=43 für Autokorrelations-Aussagen zu
> instabil ist. Wo beide vorliegen, zählt die n=147-Zahl mehr.

## 1. Range-Autokorrelation: echtes Volatility Clustering

Pearson r = **0,305** (n=146) zwischen der Tagesrange und der Range des Vortags — ein
moderater, positiver Zusammenhang. Auf einen Tag mit großer Range folgt statistisch eher
wieder ein Tag mit großer Range (und umgekehrt), nicht das Gegenteil. Bei der kleinen
Stichprobe zeigt sich derselbe Trend, aber viel schwächer (r=0,038, n=42) — deutlich klarer
erst ab n=147.

**Praktische Lesart**: nach einem ungewöhnlich großen Tag eher mit einem weiteren
Expansions-Tag rechnen statt automatisch eine ruhigere Konsolidierung zu erwarten.

## 2. Richtungs-Autokorrelation: schwaches Momentum

- Nach bullishem Tag: 58,8 % bullish am nächsten Tag (n=80) — leichtes Momentum.
- Nach bearishem Tag: 51,5 % bullish am nächsten Tag (n=66) — praktisch Zufall.

Schwächer als der Range-Effekt, aber in dieselbe Richtung (Fortsetzung statt Umkehr), zumindest
nach bullishen Tagen. Bei der kleinen Stichprobe (n=43) zeigt sich ein schwächeres,
uneindeutiges Signal (47,1 % nach bullish, n=17; 40,0 % nach bearish, n=25) — bei diesem n
im Rauschen, kein klarer Widerspruch mehr zur großen Stichprobe.

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

## 5. NWOG (New Week Opening Gap): Bias-intakt-Quote überraschend niedrig

Spezialfall von NDOG (Punkt 4), nur montags: Gap zwischen Freitag-Close und Montag-Open.
`nwog_gap()` in `tools/analyze_ohlc.py` ist ein dünner Wrapper um `ndog_gap()` (gleiche Logik,
nur auf Montage beschränkt). Getestet mit `algo/backtest_nwog.py` (n=28 Wochen), direkt gegen
die Regel aus [[New Week Opening Gap (NWOG) Bias]] ("bleibt der Kurs die ganze Woche auf einer
Seite des NWOG, gilt der Bias als intakt"):

- **Bias-intakt-Quote nur 7,1 %** (2/28 Wochen) — das NWOG wird in fast allen Wochen
  irgendwann wieder erreicht. Selbst wenn man Montags eigene Kerze (die den Freitag-Close fast
  immer trivial mitstreift) ausklammert und erst ab Dienstag zählt, bleibt es bei nur 10,7 %.
  Die "saubere" NWOG-Bias-Situation, auf die sich die Regel bezieht, ist in diesem Datensatz
  die Ausnahme, nicht der Normalfall.
- **Korrelation |Gap| vs. Wochenrange**: r=0,124 — deutlich schwächer als der Tages-Analog
  (0,264 bei NDOG), praktisch kein Zusammenhang.
- **Gap-Richtung vs. Wochenrichtung**: exakt 50,0 % — reiner Zufall, anders als NDOG (43,2 %,
  leichte Fade-Tendenz). Auf Wochenebene liefert die Gap-Richtung keine Information.
- **Wochentag von Wochen-High/-Low** (Test der beiden Timing-Behauptungen aus
  [[New Week Opening Gap (NWOG) Bias]]): Wochen-**Low** bildet sich am häufigsten Montag
  (32,1 %, höchster Einzelwert) — **teilweise bestätigt**. Wochen-**High** dagegen am seltensten
  Montag (14,3 %, hinter Di/Mi mit je 28,6 %) — **nicht bestätigt**. Die "Donnerstag ist
  Reversal-Kandidat"-Behauptung widerspricht der Datenlage klar: Donnerstag ist der
  *unwahrscheinlichste* Tag für sowohl Wochen-High (7,1 %) als auch Wochen-Low (0,0 %).

`algo/live_status.py` liefert montags zusätzlich ein `nwog`-Feld (sonst `null`).

## 6. TGIF: Median trifft die Zielzone, Einzelwochen kaum

[[TGIF (Thank God its Friday)]] erwartet einen Freitag-Close, der 20–30 % in die laufende
Weekly Range zurückretraced. Operationalisierung mangels exakter Formel in der Quelle:
Wochenrichtung über Montag-Open vs. Close des vorletzten Handelstags, Retracement dann als
Abstand des Freitag-Close vom Wochen-Extrem (High bei bullisher, Low bei bearisher Richtung)
in % der Wochenrange. `algo/backtest_tgif.py`, n=27 Wochen:

- **Exakte Trefferquote (20–30 %-Fenster): nur 3,7 %** (1/27) — auch mit großzügigerer
  Toleranz (15–35 %) bleibt es bei 3,7 %.
- **Median 22,1 %** — trifft die Zielzone fast exakt.
- **Aber**: die Verteilung ist **bimodal**, kein Cluster um 20–30 %. 37 % der Wochen retracen
  kaum (0–10 %, Freitag schließt nahe am Wochenextrem), 48 % dagegen deutlich mehr als erwartet
  (50–100 %, teils bis zum gegenüberliegenden Ende der Range). Der Median trifft die 20–30 %
  also eher zufällig durch den Split zwischen "kaum" und "viel" als durch echtes Clustering.

**Fazit**: die 20–30 %-Zahl ist als Median richtig, aber als Erwartung für eine einzelne Woche
irreführend — TGIF liefert eher "kaum" oder "viel" Retracement, selten genau die Zielzone.

## 7. Intraday-Vakuen zwischen zwei 1m-Kerzen: extrem selten, praktisch immer randständig

Anlass war eine Beobachtung von Jannes am 2026-08-10: ein „unnatürlich großer offener Bereich"
im MNQ-1m-Chart um die Mittagszeit, den er für einen TradingView-Anzeigefehler hielt. Ein
*Vakuum* ist hier der Preisbereich, den weder Kerze `i` noch Kerze `i+1` berührt hat — nicht zu
verwechseln mit einem [[Fair Value Gap]], der über **drei** Kerzen definiert ist. Gezählt wird
nur zwischen echt benachbarten Minuten (`t2 - t1 == 60 s`), damit Session-Pausen und
Tagesgrenzen nicht als Vakuum durchgehen. `algo/backtest_1m_gaps.py`:

- **MNQ, n=23 Tage / 28.839 Minutenpaare: nur 16 Vakuen überhaupt (0,055 % aller Minuten)**,
  Median 0,25 Pkt. Genau **eines ≥ 10 Punkte** (20,75 Pkt am 2026-08-04, 16:15 NY — nach
  RTH-Close).
- **ES, n=18 Tage / 24.096 Minutenpaare: 139 Vakuen (0,577 %)**, ebenfalls nur eines ≥ 10 Punkte
  (20,50 Pkt am 2026-07-28, 01:19 NY — Asia-Session).
- Beide Vergleichsfälle liegen in **dünnen Randzeiten**, nicht in einer liquiden Phase. Beide
  wurden innerhalb einer Minute wieder berührt.
- Der ES zeigt rund zehnmal so viele Mikro-Vakuen wie der MNQ, bei praktisch gleicher Zahl
  großer — ein Tick-Size-Effekt (ES 0,25 Pkt auf ~7.400, MNQ 0,25 auf ~29.800), kein
  Verhaltensunterschied.

**Fazit**: Ein Vakuum ≥ 10 Punkten tritt im MNQ etwa **alle 23 Handelstage** auf. Jannes'
Einschätzung „so noch nie gesehen" ist damit quantitativ bestätigt — die Seltenheit ist real,
die Kerze selbst aber nicht falsch. Ein solches Vakuum ist also kein Anlass, die Daten
anzuzweifeln, sondern ein Marker für einen echten Liquiditätsabriss. Praktische Prüfregel, um
beides zu unterscheiden: Ein **Anzeigefehler** zeigt fehlende Bars (Lücken im Minutenraster) und
normales Volumen; ein **echtes Vakuum** hat ein lückenloses Minutenraster und eine
Volumenspitze in der Bar, die den Sprung erzeugt.

## Einordnung

Punkt 1 ist der robusteste Fund hier (großes n, deutlicher Effekt) und Kandidat für eine
eigene Konzept-Seite, falls er sich mit wachsendem Datenstand hält. Punkt 2 ist schwächer und
sollte mit mehr Daten erneut geprüft werden. Punkt 3 ist ein stabiles Negativ-Ergebnis. Punkt 4
bestätigt eine bestehende ICT-Regel quantitativ für einen neuen Gap-Typ. Punkt 5 relativiert
eine bestehende ICT-Regel deutlich (Bias-intakt-Quote nur 7 %) und widerlegt die
Donnerstag-Reversal-Behauptung klar. Punkt 6 zeigt einen Median-Treffer bei gleichzeitig
niedriger Einzeltreffer-Quote — Vorsicht vor Medianen, die eine bimodale Verteilung verdecken.
Bei n=27/28 Wochen ist das noch keine große Stichprobe. Punkt 7 ist weniger ein Handelsmuster
als ein **Datenqualitäts-Werkzeug**: er gibt die Häufigkeitsbasis, an der sich eine
Chart-Auffälligkeit als „echt, aber selten" statt als Feedfehler einordnen lässt. Für die
kalendarischen Funde
(Montag-Effekt, Turn-of-Month, Woche-im-Monat, Monatszahlen) siehe
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
