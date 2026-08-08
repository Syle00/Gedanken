---
tags: [concept, algo-methodology, validation]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[How I Develop Trading Strategies (Source)]]", "[[Testing and Tuning Market Trading Systems (Source)]]"]
---

# Vier-Stufen-Strategieentwicklung (Masters)

> **Nachtrag 2026-08-08:** Masters' eigenes Buch liegt inzwischen im Vault —
> [[Testing and Tuning Market Trading Systems (Source)]]. Es formuliert den Prozess nicht als
> nummerierte Vierstufen-Liste (das ist neurotraders Zuspitzung), enthält aber alle vier Stufen
> und ergänzt sie um Werkzeuge, die hier fehlten: die Vorprüfung der Indikatoren
> ([[Indikator-Stationarität & Entropie]]), die Nachprüfung der Parameterstabilität
> ([[Differential Evolution & Parameter-Sensitivität]]), die Konfidenzgrenzen
> ([[Konfidenzgrenzen für Renditen (t-Test, Bootstrap, BCa)]],
> [[Grenzen für Einzelrenditen & Drawdown]]) und vor allem die Unterscheidung
> [[Training Bias & Selection Bias]] — Stufe 3/4 beseitigen nur die erste der beiden.

Generischer Entwicklungs-/Validierungsprozess für jede regelbasierte oder ML-basierte
Handelsstrategie, aus [[How I Develop Trading Strategies (Source)]] (neurotrader, nach Timothy
Masters). Vier Stufen, jede baut auf der vorigen auf — keine ersetzt eine andere:

1. **In-Sample Excellence.** Strategie auf Entwicklungsdaten fitten/optimieren (Grid-Search,
   Modelltraining, Parameterwahl — beliebiges Optimierungsverfahren). Zwei Leitfragen: *Ist das
   Ergebnis exzellent?* und *Ist es offensichtlich overfittet?* (Alarmzeichen: verdächtig gute
   Kennzahlen wie 100%-Winrate deuten fast immer auf Future-Leak oder krasses Overfitting hin,
   nicht auf eine wirklich gute Strategie.) Objective-Funktionen (Profit Factor, Sharpe) werden
   auf Bar-Granularität berechnet (Positions-Vektor × geshiftete Returns), nicht auf
   Trade-Granularität — mehr Datenpunkte, stabilere Kennzahl.
2. **In-Sample Monte Carlo Permutation Test (MCPT).** Prüft, ob die In-Sample-Exzellenz aus
   Stufe 1 auf echten Mustern beruht oder auf Data-Mining-Bias (siehe
   [[Monte Carlo Permutation Test (MCPT)]]). Erst wenn diese Stufe besteht (P < 1%), lohnt es
   sich, überhaupt Validierungsdaten anzufassen.
3. **Walk-Forward-Test.** Rollierende Reoptimierung auf tatsächlich unbenutzten Daten (In-Sample-
   Fenster, Out-of-Sample-Test ohne Refit, Fenster wandert weiter). Sobald das Ziel mehr als eine
   Bar vorausschaut, braucht dieser Schritt zwingend einen Guard Buffer, sonst ist er trotz
   korrektem Aufbau optimistisch verzerrt — siehe
   [[Walk-Forward Guard Buffer & Varianz-Inflation]]. Ergebnisse liegen i.d.R.
   unter der In-Sample-Performance — kein Data-Mining-Bias mehr, nur noch potenzieller Selection
   Bias, falls bereits mehrere Strategien auf denselben Walk-Forward-Daten verglichen wurden.
4. **Walk-Forward Monte Carlo Permutation Test.** Wie Stufe 2, aber nur der Testzeitraum nach dem
   ersten Trainings-Fold wird permutiert — prüft, ob die Walk-Forward-Ergebnisse aus Stufe 3
   besser sind, als eine wertlose Strategie durch reinen Zufall in diesem Zeitraum erreicht hätte.

Der Autor handelt eine Strategie nur, wenn sowohl Stufe 2 als auch Stufe 4 sehr niedrige P-Werte
liefern — unabhängig davon, wie gut die Rohkennzahlen aus Stufe 1/3 aussehen. Explizit
gegen-intuitiv: eine Strategie mit mittelmäßiger, aber laut MCPT statistisch abgesicherter
Performance wird einer mit exzellenter, aber nicht abgesicherter Performance vorgezogen.

## Bezug zu diesem Projekt

Deckt sich strukturell mit [[Algo-Trading: Arbeitsstandards]]/`algo/PLAN.md`s bereits etablierter
Regel "Walk-Forward-Test, Monte-Carlo-Simulation und Parameter-Sensitivität sind Standardwerkzeuge
für jeden Regel-Backtest" (Log-Eintrag 2026-08-05) — bestätigt diese Praxis von außen, ergänzt sie
aber um die MCPT-Stufen (2 und 4), die `algo/validate.py` bisher nicht abdeckt. Siehe
[[Monte Carlo Permutation Test (MCPT)]] für den Kern-Mechanismus und den aktuellen
Implementierungsstand (`algo/permutation_test.py`, noch offen).
