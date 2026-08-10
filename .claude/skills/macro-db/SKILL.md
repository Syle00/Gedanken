---
name: macro-db
description: Beantwortet statistische Fragen zu MNQ-Macro-Fenstern (:50-:10) aus algo/results/macro_db.csv — wie oft expandiert ein Fenster, wann setzt der Move ein, was war davor (Sweep, MSS, Displacement, Kompression), welche Liquidität wurde genommen. Nutze diesen Skill, wenn Jannes nach Wahrscheinlichkeiten, Häufigkeiten oder Timing rund um Macro-Zeiten fragt ("wie oft", "wann passiert X", "spoolt es vorher", "lohnt sich das 10:50-Macro"), auch wenn er die Wörter "Statistik" oder "Datenbank" nicht benutzt.
---

# Macro-Datenbank

Eine Zeile je Macro-Fenster je Handelstag in `algo/results/macro_db.csv`.
Gebaut von `algo/macro_db.py`. Spec: `docs/superpowers/specs/2026-08-10-macro-datenbank-design.md`.

## Ablauf

1. Ist die CSV älter als der jüngste Tagesordner in `raw/marktdaten/`, zuerst
   `python algo/macro_db.py build` laufen lassen.
2. `python algo/macro_db.py stats` für den Standardreport.
3. Für eine Frage, die der Standardreport nicht abdeckt: die CSV mit `read_csv()` laden
   und die Bedingung direkt auswerten — aber **immer** über `quote()` und `fmt_quote()`
   aus demselben Modul, nie mit einer selbst gerechneten Prozentzahl.

## Antwortdisziplin

Diese Regeln sind der eigentliche Zweck dieses Skills. Sie gelten ausnahmslos:

- **Nie eine Quote ohne n.** "62 %" allein ist keine Antwort.
- **Nie eine Punktschätzung ohne Intervall.** Immer das Wilson-Intervall mitgeben.
- **Immer die Basisrate danebenstellen.** Eine bedingte Quote ohne Vergleichswert ist
  bedeutungslos. Überlappen die Intervalle: **"kein Unterschied nachweisbar"** sagen,
  nicht "leicht erhöht" oder "tendenziell besser".
- **Unter n = 20 keine Prozentzahl.** Dann lautet die Antwort "n=7 — zu wenig für eine
  Aussage". Das ist eine vollständige, richtige Antwort, kein Ausweichen.
- **Mehrfachvergleiche offenlegen.** Wurden mehrere Bedingungen durchprobiert, sagen wie
  viele — und dass bei 5 % Niveau ein Teil davon zufällig auffällig ist.

## Vorbehalte, die ungefragt mitgehen

- Fenster desselben Handelstags sind **nicht unabhängig**; p-Werte sind optimistisch.
- **Auch oberhalb n = 20 bleibt die Stichprobe klein** (~20–22 Tage je Fenster) — das
  Wilson-Intervall ist der eigentliche Wahrheitsgehalt, nicht der Punktwert. Ein Fenster
  mit "45 % [27–65]" ist keine 45-%-Aussage, sondern "irgendwo zwischen einem Viertel und
  zwei Dritteln".
- Fenster **23:50** fehlt fast vollständig (Exportlücke 23:59–00:08), **16:50** ganz
  (ragt über den Sessionschluss 17:00).
- Level-Quelle ist bisher nur `untouched_levels` (Swing-Level des laufenden Handelstags).
  **NDOG/NWOG/ORG fehlen** (Kalendertag- statt Session-Logik) und **PDH/PDL ebenso**
  (bräuchte die Vortagsdatei) — siehe `algo/PLAN.md`.
- Die Spooling-Kandidaten sind rein preisbasiert; die Exporte enthalten kein Volumen.

## Spalten

`symbol, session_day, window, weekday, session` — Identität. `window` ist die Startzeit
(`"09:50"`), `session_day` das **Ende** des Handelstags (18:00 Vorabend bis 17:00), `session`
eine der sechs überschneidungsfreien Phasen (Asia, London, Premarket, NY AM, Lunch, NY PM).

`pre_range_rel, pre_wick_frac, pre_streak, pre_contraction` — Spooling-Kandidaten aus den
10 Minuten davor. Keiner davon ist als "das ist Spooling" bestätigt; welcher trägt, sagt
`stats`.

`sweep_age, sweep_dir, mss_age, mss_dir, displacement_age, fvg_open_dist, levels_open,
nearest_level_dist` — Vorgeschichte. Alter in Minuten vor dem Fensterstart.

`range, netto, dir, direction, start_min, expansion, levels_hit` — Verlauf im Fenster.
`netto` ist vorzeichenbehaftet, `dir` = |netto|/range (Geradlinigkeit), `start_min` die
Minute des Extrems entgegen der Netto-Richtung.

## Verwandt

- `wiki/synthesis/Macro-Datenbank (laufend).md` — die generierte Auswertungsseite
- `wiki/concepts/ICT Macros & Leading Candles.md` — das Konzept dahinter
- `algo/backtest_macro.py` — die ältere Frage "sind Macro-Blöcke anders als ihre Nachbarn"
