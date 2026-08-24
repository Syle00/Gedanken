---
tags: [lernpfad, meta, meilensteine]
created: 2026-08-24
updated: 2026-08-24
---

# Lernpfad — Meilensteine

Die neun Prüfpunkte über zwölf Monate. Ein Meilenstein gilt **erst als erreicht, wenn der
Nachweis existiert** — nicht, wenn sich der Stoff vertraut anfühlt. Gefühlte Sicherheit ist
kein Nachweis.

Übersicht: [[Lernpfad Quant — Übersicht]]

## Checkliste

- [ ] **Woche 6 · So 04.10.2026 — Phase 0 abgeschlossen**
      CS50P Woche 0–4 durch, tägliche Kartenwiederholung läuft, Schulmathe aufgefrischt.
      *Selbsttest:* Funktion mit Parametern, Rückgabewert und `try/except` aus dem Kopf.
      `A = P·(1+r)ⁿ` nach jeder Variable auflösen, ohne zu googeln. In einem Satz erklären,
      warum log-Renditen addierbar sind und einfache Renditen nicht.

- [ ] **Woche 12 · So 15.11.2026 — Phase 1 abgeschlossen**
      CS50P komplett inklusive Abschlussprojekt. Git, virtuelle Umgebungen und pytest im Griff.
      *Selbsttest:* `groupby` und `resample` ohne Nachschlagen.

- [ ] **Woche 13 · So 22.11.2026 — MEILENSTEIN 1 · Backtest v0**
      GitHub-Repository mit sauberen Commits: lädt OHLCV-Daten, wendet eine banal einfache Regel
      an (z. B. Bruch des Vortageshochs), zeichnet eine Equity-Kurve.
      Bewusst simpel — es geht um die Pipeline, nicht um Profitabilität.

- [ ] **Woche 20 · So 10.01.2027 — Phase 2 abgeschlossen**
      *Selbsttest:* Erklären, warum Matrixmultiplikation nicht kommutativ ist. 3×3-Determinante
      ohne Formelsammlung. Gradient Descent in unter 20 Zeilen NumPy. Kovarianzmatrix mehrerer
      Assets berechnen und die Eigenvektoren deuten.

- [ ] **Woche 25 · So 14.02.2027 — MEILENSTEIN 2 · Feature-Bibliothek**
      Getestetes Python-Modul, das die ICT-Konzepte erkennt: Swing Points, Break of Structure,
      Fair Value Gaps, Order Blocks, Liquidity Sweeps — jeweils mit pytest-Tests gegen
      Beispiel-Charts. Verweis auf die Konzeptseiten im Wiki, z. B. [[Fair Value Gap (FVG)]].

- [ ] **Woche 30 · So 21.03.2027 — Phase 3 abgeschlossen**
      Statistik und Zeitreihen durch, Kennzahlen selbst berechnet.
      *Selbsttest:* Erklären, warum ein Sharpe Ratio von 2,0 nichts wert ist, wenn 500 Varianten
      getestet wurden.

- [ ] **Woche 41 · So 06.06.2027 — MEILENSTEIN 3 · ML-Modell v1**
      Klassifikationsmodell, das ICT-Setups nach Erfolgswahrscheinlichkeit sortiert, verglichen
      gegen ein dummes Basismodell.
      *Selbsttest:* Data Leakage in fremdem Notebook-Code finden, ohne Hinweis.

- [ ] **Woche 48 · So 25.07.2027 — Walk-Forward und realistische Kosten**
      Purged Cross-Validation mit Embargo implementiert, Spread und Slippage realistisch im
      Backtest abgebildet.

- [ ] **Woche 53 · So 29.08.2027 — MEILENSTEIN 4 · Paper-Trading**
      Modell läuft live auf einem Demokonto, mit Logging und wöchentlichem Report.
      *Der eigentliche Test:* begründen können, warum es live funktionieren sollte — ohne dabei
      auf die Backtest-Kurve zu zeigen.

## Harte Sperre

> [!warning] Kein Live-Handel mit echtem Geld
> Meilenstein 4 endet bei **Paper-Trading**. Die Sperre für Live-Handel mit echtem Geld aus der
> IBKR-Roadmap in [[../../algo/CLAUDE.md|algo/CLAUDE.md]] bleibt davon unberührt und wird durch
> diesen Lernpfad nicht gelockert.
