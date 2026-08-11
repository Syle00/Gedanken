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
- Die letzte Handelsstunde hat **drei eigene Fenster** statt des generischen 20-Min-Rasters:
  **15:15** (30 Min, Final Hour Macro, unstrittig) sowie **beide** MOC-Lesarten nebeneinander
  — **15:45** (15 Min, Gems-Quelle) und **15:50** (10 Min, 2:1-Mehrheit der Chronicles-Quellen).
  Beleg: `raw/trading-ict/2026/yt-VH7Dh1OONj4-transcript.md` ("there's four of four macros in
  that last hour"). Ein vierter Teil (Algo feuert 16:01, Run bis 16:15) gilt nur zur
  Earnings-Season und ist aus OHLC allein nicht erkennbar, siehe
  `wiki/models/Market on Close (MOC) Macro Model.md`.
- Level-Quelle ist bisher nur `untouched_levels` (Swing-Level des laufenden Handelstags).
  **NDOG/NWOG/ORG fehlen** (Kalendertag- statt Session-Logik) und **PDH/PDL ebenso**
  (bräuchte die Vortagsdatei) — siehe `algo/PLAN.md`.
- Die Vorlauf-Kandidaten sind rein preisbasiert; die Exporte enthalten kein Volumen.
- **In der letzten Handelsstunde gilt das `:50–:10`-Raster laut ICT nicht** — dort nennt er
  15:15–15:45 (Final Hour Macro) und 15:45/15:50–16:00 (Market on Close). Die Zeile `15:50`
  misst 15:50–16:10 und läuft über den RTH-Schluss 16:00 hinaus; sie ist als Macro-Zeile nur
  eingeschränkt vergleichbar. Siehe [[Market on Close (MOC) Macro Model]].

## Begriffsfalle: „Spooling"

Die vier `pre_*`-Spalten messen die **Ruhe vor** dem Fenster. Das war die ursprüngliche
Lesart von „Spooling" — sie ist widerlegt. ICT meint mit Spooling den **gerichteten Lauf
selbst** (*„the market will spool — it jumps and runs"*), also das, was `dir` und `mfe_*`
messen. Nenne die vier Kandidaten deshalb **Vorlauf-Kandidaten**, nicht Spooling-Kandidaten,
und behaupte nicht, ein Nullbefund bei ihnen widerlege Spooling — er widerlegt die alte
Lesart des Begriffs.

## Spalten

`symbol, session_day, window, weekday, session` — Identität. `window` ist die Startzeit
(`"09:50"`), `session_day` das **Ende** des Handelstags (18:00 Vorabend bis 17:00), `session`
eine der sechs überschneidungsfreien Phasen (Asia, London, Premarket, NY AM, Lunch, NY PM).

`pre_range_rel, pre_wick_frac, pre_streak, pre_contraction` — Vorlauf-Kandidaten aus den
10 Minuten davor. Gemessen: keiner hängt mit der Geradlinigkeit zusammen; `pre_range_rel`
hängt mit der **Größe** der Bewegung zusammen (Volatilitätspersistenz). Details sagt `stats`.

`sweep_age, sweep_dir, mss_age, mss_dir, displacement_age, fvg_open_dist, levels_open,
nearest_level_dist` — Vorgeschichte. Alter in Minuten vor dem Fensterstart.

`range, netto, dir, direction, start_min, expansion, levels_hit` — Verlauf im Fenster.
`netto` ist vorzeichenbehaftet, `dir` = |netto|/range (Geradlinigkeit), `start_min` die
Minute des Extrems entgegen der Netto-Richtung.

`exc_up_N, exc_dn_N, mfe_N, reach10_N` für N ∈ {20, 40, 60} — **Zielgrößen**: die größte
Auslenkung ab Fenster-Open über die folgenden N Minuten. `mfe_N` ist die größere der beiden
Seiten (richtungsagnostisch, weil ein Macro laut ICT keine Richtung liefert), `reach10_N`
prüft ICTs Mindestziel von 10 Handles. Existieren, weil ICT sagt, der Move **beginne** im
Macro und laufe darüber hinaus — der reine Blockinhalt kann das nicht sehen.

> Diese vier Spalten sehen bewusst Kerzen **nach** dem Fensterstart. Das ist kein
> Lookahead-Verstoß (sie sind das Ergebnis, nicht das Merkmal), aber sie taugen deshalb
> auch **nicht** als Vorhersagemerkmal in einer Regel. Verwechsle sie nicht mit `pre_*`.

`reach10_N` ist auf diesem Bestand **immer wahr** — die Schwelle selektiert nichts.

## Verwandt

- `wiki/synthesis/Macro-Datenbank (laufend).md` — die generierte Auswertungsseite
- `wiki/concepts/ICT Macros & Leading Candles.md` — das Konzept dahinter
- `algo/backtest_macro.py` — die ältere Frage "sind Macro-Blöcke anders als ihre Nachbarn"
