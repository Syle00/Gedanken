---
tags: [source, algo-methodology, validation]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[How I Develop Trading Strategies  Permutation Tests and Trading Strategy Development with Python]]"]
---

# How I Develop Trading Strategies | Permutation Tests and Trading Strategy Development with Python

YouTube-Transkript, Kanal neurotrader (neurotrader888), veröffentlicht 2026-08-03,
[github.com/neurotrader888/mcpt](https://github.com/neurotrader888/mcpt). Kein ICT/SMC-Material —
gehört zur `algo/`-Domäne (Validierungsmethodik), nicht zu `trading-ict`. Rohquelle:
`raw/How I Develop Trading Strategies  Permutation Tests and Trading Strategy Development with
Python.md` (inhaltsgleiches Duplikat ohne Metadaten unter `raw/md.md`, das als erster
Ingest-Anlass bereits `docs/superpowers/specs/2026-08-08-algo-permutation-test-design.md` erzeugt
hat — diese Seite holt den dort als offen vermerkten Wiki-Ingest-Schritt nach).

## Zusammenfassung

Vier-Schritte-Prozess zur Entwicklung und Validierung einer Handelsstrategie, generisch für
jede regelbasierte oder ML-basierte Strategie: **In-Sample Excellence → In-Sample Monte Carlo
Permutation Test (MCPT) → Walk-Forward-Test → Walk-Forward MCPT**. Details in
[[Vier-Stufen-Strategieentwicklung (Masters)]]. Kernmethode ist der **Bar-Permutationstest**
([[Monte Carlo Permutation Test (MCPT)]]): OHLC-Bars werden statistik-erhaltend gemischt (Mean/
Std/Skew/Kurtosis der Returns bleiben nahezu identisch, echte Muster verschwinden), die Strategie
auf den permutierten Daten neu optimiert, und der Anteil der Permutationen, die mindestens so gut
abschneiden wie auf echten Daten, ergibt einen P-Wert für die Data-Mining-Bias-Hypothese.

## Kernpunkte

- **Objective-Funktion auf Bar- statt Trade-Granularität**: Positions-Vektor (long/flat/short je
  Bar) × geshiftete Close-zu-Close-Returns → Strategie-Return je Bar. Liefert deutlich mehr
  Datenpunkte für Profit-Factor/Sharpe als eine Trade-Liste, macht die Kennzahl stabiler. Quelle
  im Video: Timothy Masters' Buch *Testing and Tuning Market Trading Systems*.
- **Zwei Fragen im Entwicklungsstadium** (In-Sample): "Ist das exzellent?" und "Ist das
  offensichtlich overfittet?" (z.B. 100%-Winrate → fast immer Future-Leak oder Overfit statt
  echter Qualität).
- **Bar-Permutationsalgorithmus** (Beispielcode: `raw/`-Transkript, Timestamp 6:07–8:52): Log-
  Preise relativ zum eigenen Open ausdrücken (Intrabar-Offsets + Gap zum Vor-Close), Indizes für
  Intrabar-Offsets und Gaps **getrennt** mischen, daraus neue Bars sequenziell rekonstruieren.
  Erster und letzter Preis bleiben exakt gleich (Gesamttrend erhalten), der Pfad dazwischen ist
  komplett anders.
- **In-Sample MCPT**: Strategie einmal auf echten Daten optimieren (Beispiel: Donchian-Channel-
  Breakout, Bitcoin stündlich 2016–2019, bester Lookback 19, Profit Factor 1,08), dann N-mal auf
  Permutationen neu optimieren. P-Wert = Anteil Permutationen ≥ echtem Wert. Beispielergebnis:
  1.000 Permutationen, P = 0,3% → Pass. Gegenbeispiel Decision Tree (absichtlich overfit, sehr
  niedriges `min_samples_leaf`) besteht den Test nicht — Permutationen schneiden genauso gut ab
  wie echte Daten.
- **Warum nicht einfach Out-of-Sample testen?** Sobald Out-of-Sample-Daten einmal benutzt wurden,
  sind sie kontaminiert (Selection Bias: testet man mehrere Strategien auf denselben Validierungs-
  Daten und wählt die beste, überfittet man effektiv die Validierungsdaten, obwohl sie nie fürs
  Fitting genutzt wurden). Der In-Sample-MCPT verwirft schlechte Ideen, bevor Out-of-Sample-/
  Validierungsdaten überhaupt angefasst werden.
- **Walk-Forward-Test**: rollierende Reoptimierung (Beispiel: 4 Jahre Trainingsfenster, alle 30
  Tage reoptimiert) auf tatsächlich unbenutzten Daten. Walk-Forward-Ergebnisse sind i.d.R.
  schlechter als In-Sample (kein Data-Mining-Bias mehr, nur noch potenzieller Selection Bias).
- **Walk-Forward-MCPT**: wie In-Sample-MCPT, aber nur der Testzeitraum NACH dem ersten
  Trainings-Fold wird permutiert (`start_index = train_window`), das Trainingsfenster bleibt echt.
  Rechenintensiv (voller Walk-Forward pro Permutation) → im Beispiel nur 200 statt 1.000
  Permutationen.
- **P-Wert-Schwellen des Autors**: In-Sample < 1%. Walk-Forward < 5% bei nur einem Jahr Testdaten,
  < 1% ab zwei oder mehr Jahren. Ausdrücklicher Hinweis: der P-Wert ist ein Maß, kein Ziel — "if a
  measure becomes a target, it is no longer a good measure" (Goodhart's Law, nicht explizit
  benannt, aber inhaltlich beschrieben).
- **Bekannte Grenzen des Verfahrens** (vom Autor selbst benannt): Preis ist kein reiner Random
  Walk — reale Preise haben Volatility Clustering und Long Memory, beide zerstört die Permutation.
  Strategien, die stark auf diesen Eigenschaften beruhen, können den Test optimistisch verzerrt
  bestehen. Kein Totalausfall des Verfahrens dadurch: besteht eine Strategie den Test selbst mit
  dieser Verzerrung nicht, ist sie mit hoher Sicherheit overfit.
- **Multi-Market-Permutation** wird nur angerissen (korrelierte Märkte gemeinsam mischen, z.B.
  BTC/ETH), im Video nicht weiter vertieft.
- Quelle des gesamten Verfahrens: Timothy Masters, *Permutation and Randomization Tests for
  Trading System Development* (Buch, Autor hat PhD in Statistik).

## Bezug zu diesem Projekt

Direkt Layer-0-relevant ([[Algo-Trading: Arbeitsstandards]], Roadmap-Punkt 3 "Validierung"):
`algo/validate.py` deckt bereits Walk-Forward, Parameter-Sensitivität und Trade-Order-Resampling
("Monte Carlo" im bisherigen Sprachgebrauch der Codebase) ab — der hier beschriebene
**Bar-Permutationstest ist ein viertes, unabhängiges Verfahren**, noch nicht implementiert.
Design steht bereits fest: `docs/superpowers/specs/2026-08-08-algo-permutation-test-design.md`
(geplantes Modul `algo/permutation_test.py`, Umsetzung als Backlog-Punkt in `algo/PLAN.md`
offen). Terminologie-Hinweis aus dem Spec: um Verwechslung mit `validate.py`s bestehendem
"Monte Carlo" (Trade-Resampling) zu vermeiden, heißt das neue Verfahren konsequent
**Bar-Permutationstest / MCPT**, nie nur "Monte Carlo".
