# Forex-Algo Phase 2 — Regel-Schicht, $-P&L und Validierung — Design-Spec

- **Datum:** 2026-08-15
- **Status:** entworfen, nicht umgesetzt
- **Auslöser:** Jannes: *"ich will die algos nun for forex haben die aktuellen sollen nicht
  überschrieben werden"*, präzisiert als Ziel: *"ich möchte die genau gleichen konzepte nutzen
  außer bekannte sachen die nur für future sind"*.
- **Vorgänger:** `2026-08-14-forex-backtesting-design.md` (Phase 1: Datenschicht, Guard,
  Gruppen A/B). Diese Spec ist deren **Phase 2** — genau der Teil, den §2 der Vorgänger-Spec
  ausdrücklich als Nicht-Ziel ausgeklammert hatte (kein `$`-P&L für Forex, keine Forex-Regel
  in `rules.py`).
- **Entscheidungen des Nutzers zu dieser Spec** (2026-08-15, in dieser Reihenfolge getroffen):
  1. Zielbild: **voller `$`-P&L, ohne Broker** (kein IBKR, keine Live-Ausführung).
  2. Schutz des Bestands: **getrennte Forex-Module** — die MNQ-Dateien werden buchstäblich
     nicht angefasst, Duplikation wird bewusst in Kauf genommen.
  3. Regel-Logik: **sofort Forex-angepasst** statt 1:1-Port.
  4. Fenstersatz: **alle vier Killzones messen**, die Daten sollen entscheiden.
  5. Kostenmodell: **konstanter Spread + Break-even-Spread als Pflichtkennzahl**.
  6. Zuschnitt: **Unterpaket `algo/forex/`** (Variante B von drei vorgelegten).
  7. Konzeptumfang: **dieselben Konzepte wie MNQ, abzüglich der bekannten Futures-Only-Sachen**.

---

## 1. Bestandsaufnahme — was Phase 1 bereits liefert

Gemessen am 2026-08-15, nicht geschätzt.

| Baustein | Zustand | Ort |
|---|---|---|
| Einheitlicher Bar-Loader | fertig | `algo/marktdaten.py::bars(symbol, tf, von, bis)` |
| Tagesgrenze Futures vs. 24x5 | fertig | `SESSION_TYP` in `tools/analyze_ohlc.py` |
| DST-Anker beim Resampling | fertig, mit Regressionswächter | `marktdaten._forex_bars`, `WANDUHR_TF` |
| Pip-Normierung | fertig | `PIP_SIZE` in `tools/analyze_ohlc.py` |
| Tick-Raster Forex | fertig | `TICK_SIZE`: 0,00001 Majors / 0,001 JPY |
| 9:30-Guard | fertig | `org_gap()`/`ndog_gap()` → `None` bei `24x5` |
| Forex-Zweig im Datenladen | fertig | `backtest_common.load_rows()` |
| Gruppe A/B teilweise | läuft | `backtest_seasonal.py --symbol`, `backtest_macro_forex.py` |

**Offen und Gegenstand dieser Spec:** die gesamte Gruppe D der Vorgänger-Spec — Regel-Schicht,
Trade-Simulation, $-P&L, Risiko-Sizing, Ensemble, Stress-Test.

**Praktischer Blocker auf dem aktuellen Rechner:** `raw/marktdaten-tief/` enthält alle 73.105
Tages-CSVs, aber `algo/cache/` existierte nicht — der Parquet-Cache ist gitignored und wurde auf
diesem Gerät nie gebaut. *(Erledigt am 2026-08-15: `pyarrow` nachinstalliert, Cache über alle 10
Paare gebaut, siehe §1.1.)*

### 1.1 Messung am gebauten Cache (2026-08-15) — zwei Befunde, die das Design ändern

| Symbol | Kerzen | von | bis | flat % gesamt | fehlende Wochentage |
|---|---:|---|---|---:|---:|
| EURUSD | 8.499.827 | 2000-05-30 | 2026-08-07 | 4,43 | **540** |
| GBPUSD | 8.298.336 | 2003-01-01 | 2026-08-07 | 4,10 | 15 |
| USDJPY | 8.292.046 | 2003-01-01 | 2026-08-07 | 4,59 | 13 |
| USDCHF | 8.283.008 | 2003-01-01 | 2026-08-07 | 5,19 | 22 |
| AUDUSD | 8.111.229 | 2003-01-01 | 2026-08-07 | 5,88 | 15 |
| USDCAD | 7.788.898 | 2003-01-01 | 2026-08-07 | 6,74 | 13 |
| NZDUSD | 7.201.155 | 2005-08-12 | 2026-08-07 | 5,86 | 11 |
| EURJPY | 8.565.125 | 2003-01-01 | 2026-08-07 | 1,86 | 13 |
| EURGBP | 8.043.177 | 2003-01-01 | 2026-08-07 | 5,47 | 13 |
| GBPJPY | 8.593.799 | 2003-01-01 | 2026-08-07 | 1,39 | 20 |

Keine Duplikate, alle Reihen monoton sortiert. `verify_forex_data.py` meldet alle zehn Symbole
als `AUFFAELLIG` — die Jahresaufschlüsselung erklärt beide Auffälligkeiten:

**Befund 1 — die Attrappen-Quote ist ein Liquiditäts-Zeitartefakt, kein Bestandsfehler.** Sie
fällt über die Jahre monoton, und die Kerzenzahl je Jahr steigt gegenläufig:

| Jahr | EURUSD flat % | USDCAD flat % | USDCAD Kerzen |
|---|---:|---:|---:|
| 2003 | 11,76 | 23,65 | 248.005 |
| 2008 | 6,36 | 17,12 | 276.953 |
| 2012 | 0,45 | 1,36 | 367.869 |
| 2019 | 0,88 | 0,76 | 372.245 |
| 2026 | 1,01 | 1,06 | 223.411 (Teiljahr) |

2003 hatte eine USDCAD-Minute schlicht oft keinen einzigen Kursdruck. Das ist echte Marktruhe,
nicht der yfinance-Attrappen-Fall (dort 100 %, siehe Vorgänger-Spec §1.4).

**Konsequenz für das Design — zwei Liquiditätsregime, nicht ein Datensatz.** Ein Backtest über
2003–2011 misst einen strukturell anderen Markt als einer über 2012–2026: Detektoren, die auf
Kerzengeometrie beruhen (FVG, Displacement, Sweep), sehen bei 10–24 % druckfreien Minuten etwas
anderes als bei unter 1 %. Daraus folgt verbindlich:

1. **Jeder Forex-Report gibt die Flat-Quote des ausgewerteten Fensters an** — als Pflichtangabe
   neben `dubious_pct` und Break-even-Spread.
2. **Ergebnisse werden zusätzlich nach Regime getrennt ausgewiesen** (bis 2011 / ab 2012). Ein
   Gesamtergebnis über 23 Jahre ohne diese Aufteilung ist keine Kennzahl dieser Spec.
3. Die Regime-Grenze 2012 ist aus der Tabelle abgelesen, nicht gesetzt: der Sprung liegt bei
   allen geprüften Paaren zwischen 2011 und 2012.

**Befund 2 — EURUSDs „Reichweite bis 2000" ist irreführend.** Die 540 fehlenden Wochentage sind
**2001 und 2002 vollständig**; die Reihe springt von 2000 direkt auf 2003. Das Jahr 2000 selbst
hat nur 182 Tage und **30 % flache Kerzen**. Verbindlich: **EURUSD-Auswertungen starten bei
2003-01-01**, wie alle anderen Paare. Der Legacy-XLSX-Bestand aus 2000 wird nicht verwendet — ein
naives `von=min(t)` würde sonst still ein unbrauchbares Jahr und ein Zweijahresloch einschließen.

**Befund 3 — Bestandsende 2026-08-07**, nicht 11.08. wie in der Vorgänger-Spec §1.3 angenommen.
Für die 23-Jahres-Statistik unkritisch, für alles Aktuelle relevant. Die restlichen fehlenden
Wochentage (11–22 je Symbol, außer EURUSD) sind Feiertage ohne Notierung — unauffällig.

---

## 2. Konzept-Inventur — das Kriterium des Nutzers, angewandt

Die Vorgabe lautet: **dieselben Konzepte, abzüglich der bekannten Futures-Only-Sachen.** Das
Ausschlusskriterium ist keine Modul-Liste, sondern ein einziger Satz aus der Vorgänger-Spec
§4.1: *setzt das Konzept die 9:30-Eröffnung als Ereignis voraus?* Ein 24/5-Markt hat weder
Schluss noch Eröffnung.

### 2.1 Übernommen, identisch zur MNQ-Seite

| Konzept | Heutiger Ort | Warum es trägt |
|---|---|---|
| Silver Bullet (1st presented FVG **im Fenster**) | `algo/rules.py::sb_entry_signal` | fensterrelativ, nicht 9:30-relativ |
| FVG-Detektion inkl. Stärke (`strong` = Swing-Break per Close), `size_rel` | `analyze_ohlc.fvgs` | reine Kerzengeometrie |
| Swings, MSS, `structure_breaks` | `analyze_ohlc` | reine Kerzengeometrie |
| HP-FVG (Vortagesrange-Hälfte + Killzone + Bias) | `algo/rules.py::plan_trade_hp_fvg` | braucht keine Eröffnungsauktion (Vorgänger §6, Gruppe B) |
| Liquidität: `untouched_levels`, PDH/PDL/PWH/PWL, Session-Extrema | `algo/rules.py` | Liquiditätspools existieren in jedem Markt |
| IPDA-Fenster (20/40/60 Tage) | `algo/rules.py::ipda_windows` | reine Kalenderdefinition |
| Killzones, Midnight Opening Range (0:00–0:30), Macros (:50–:10) | `analyze_ohlc.KILLZONES`, `algo/macro_db.py` | reine Zeitdefinition |
| **NWOG** (Fr 17:00 → So 17:01 NY) | `analyze_ohlc.nwog_gap` | Wochenendgap ist im Forex-Bestand belegt (Vorgänger §4.3) |
| Trade Management, 1 %-Risiko, Kill-Switch | `algo/rules.py`, `algo/risk_*.py` | symbol-unabhängig |
| Ensemble-Bias über ein zweites, korreliertes Instrument | `algo/backtest_ensemble.py` | Idee trägt, Instrumentenpaar wechselt (§6) |

### 2.2 Ausgeschlossen — die bekannten Futures-Only-Sachen

ORG (Opening Range Gap) · ORG C.E. · ORG-Standardabweichungs-Extrema · 1st Presented FVG **des
Tages** · 1p FVG **der Woche** · 1p-Mindestgröße · erstes FVG nach 9:30 · Open Drive
(09:30–09:50) · **NDOG** · alle RTH-Varianten.

Grundlage ist die zweistufige Nutzerkorrektur vom 2026-08-14: *"in forex gibt es kein opening
range gap ebenso das c.e der opening range gap"* und *"1p fvg der woche ist auch nur für future
wie opening range gap auch erstes fvg nach 9.30 ndog gibt es nicht aber nwog gibt es"*.

**Kein zweiter Guard.** Der bestehende Guard in `tools/analyze_ohlc.py` greift bereits. Die
Forex-Module rufen die betroffenen Funktionen zusätzlich gar nicht erst auf — ein Aufruf, der
garantiert `None` liefert, gehört nicht in den Code.

### 2.3 Modul-Inventur — dieselbe Frage, auf die vorhandenen Skripte angewandt

Nutzerpräzisierung 2026-08-15: *„nutzen wir die bekannten Module macros, sb tgif etc.
future only konzepte wie opening range gap und c.e davon entfallen"*. Das Kriterium aus §2.1/§2.2
wird deshalb hier modul-für-modul durchdekliniert, damit beim Bauen nichts interpretiert werden
muss.

**Läuft auf Forex — dieselben Module, nur ein anderes Symbol:**

| Modul | Was es misst | Anmerkung |
|---|---|---|
| `backtest_macro.py`, `macro_db.py` | Macro-Fenster (:50–:10) | `backtest_macro_forex.py` existiert bereits (Phase 1) |
| `backtest_tgif.py` | TGIF-Freitagsmuster | reine Wochentagslogik |
| `backtest_seasonal.py` | Saisonalität | läuft bereits über `--symbol` |
| `backtest_daily_patterns.py`, `backtest_ohlc.py`, `backtest_nfp_week.py` | Tagesstatistik, NFP-Woche | nur 1d nötig |
| `backtest_midnight_range_std.py`, `backtest_midnight_range_judas.py` | Midnight OR, Judas Swing | `_std` hat den Forex-Zweig schon |
| `backtest_fvg_strength.py`, `backtest_hp_fvg.py` | FVG-Stärke, HP-FVG | reine Struktur |
| `backtest_nwog.py` | Wochenendgap | NWOG existiert im Forex (§2.1) |
| `backtest_sb_bellwether.py` | Timeframe-Wahl für die Ziel-Liquidität beim SB | variiert nur `levels_bars`, Entry/Stop unverändert |
| `backtest_1m_gaps.py` | Häufigkeit von 1m-Vakuum | reine Kerzenstatistik; auf 23 Jahren erstmals aussagekräftig |
| `backtest_risk_compare.py` | fix/GARCH/Kelly auf identischen SB-Signalen | über den Forex-Zwilling der Simulation |
| `backtest_walkforward.py` | Walk-Forward-Wrapper | dünner Wrapper um `validate.py`, symbol-agnostisch |
| `liquidity_report.py` | offene Liquidität über 1m/5m/15m/1d | nutzt nur `rules.py`-Bausteine, die alle tragen |
| `mor_levels.py` | Midnight Opening Range, Quarters, SD-Projektionen | siehe Korrektur unten |
| `explore_patterns.py` | Mustersuche ohne Vorab-These | rein statistisch |

**Entfällt — futures-only:**

| Modul | Warum |
|---|---|
| `backtest_org_ce.py` | ORG C.E. — kein Gap, kein C.E. davon |
| `backtest_org_std_extrema.py` | ORG-Standardabweichungs-Extrema |
| `backtest_ndog.py` | NDOG — keine tägliche Handelspause |
| `backtest_1p_fvg_woche.py` | 1p FVG der Woche |
| `backtest_1p_mindestgroesse.py` | These lautet wörtlich „das 1.p FVG der NY-AM-Session **nach dem Opening Range Gap**" |
| `backtest_open_drive_vs_sb.py` | misst die Expansion 09:30–09:50 |
| alle `RTH`-Varianten | RTH existiert in einem 24/5-Markt nicht |

**Zwei Korrekturen an der Vorgänger-Spec (§6, Gruppe C), beim Durchdeklinieren gefunden:**

1. **`backtest_fvg_specialness.py` ist nicht pauschal futures-only.** Das Modul prüft *drei*
   Thesen: (1) das 1. FVG nach 9:30 NY, (2) das 1. FVG nach 0:00 NY, (3) das 1. FVG jeder neuen
   Stunde im 1m-Chart. Nur **These 1** fällt unter den Ausschluss. These 2 (Mitternacht) und
   These 3 (Stundenwechsel) sind reine Zeitdefinitionen ohne Eröffnungsbezug und laufen auf
   Forex. Die Vorgänger-Spec ordnete das Modul als Ganzes der Gruppe C zu — zu grob. Für Forex
   wird These 1 übersprungen, 2 und 3 laufen.
2. **`mor_levels.py` trägt trotz „first presentation".** Der Begriff bezeichnet dort das erste
   FVG **innerhalb der 0:00–0:30-Range**, nicht das erste nach 9:30. Mitternachtsbezug, kein
   Eröffnungsbezug — läuft auf Forex.

**Nicht Teil dieser Spec:** `backtest_fred_events.py`. Das Modul dokumentiert ausdrücklich, dass
sich die ursprüngliche These mit FRED-Daten *nicht* sauber bauen ließ und deshalb bewusst nicht
gebaut wurde. Es auf Forex zu übertragen hieße, einen nicht vorhandenen Baustein zu portieren.
Bleibt, wo es ist.

### 2.4 Fenstersatz

Die drei Silver-Bullet-Fenster bleiben unverändert (gleiches Konzept): London SB 03:00–04:00,
NY AM 10:00–11:00, NY PM 14:00–15:00. **Zusätzlich** werden die vier Killzones aus
`analyze_ohlc.KILLZONES` als eigene Fenster gemessen: Asia (19:00–00:30), London (02:00–05:00),
NY (07:00–09:00), London Close (10:00–12:00).

> ⚠️ **Offene Diskrepanz in den eigenen Quellen, nicht stillschweigend aufgelöst.**
> `analyze_ohlc.KILLZONES` führt die NY-Killzone als **07:00–09:00**. Die Wiki-Seite
> [[ICT Daily Range Session Timing]] sagt dagegen ausdrücklich *„7–10 Uhr NY ist die
> NY-Killzone **für Forex**"* — also 07:00–10:00, mit Verlängerung auf 11:00/11:30 bei einem
> High-Impact-News-Driver um 10 Uhr. Das ist genau der Fall, in dem laut `CLAUDE.md` markiert
> statt überschrieben wird. **Umsetzung:** Beide Varianten werden als getrennte Fenster
> gemessen (`NY 07-09` und `NY-Forex 07-10`), die Messung entscheidet. Die News-Verlängerung
> auf 11:00/11:30 bleibt außen vor — sie bräuchte einen News-Kalender über 23 Jahre, den es im
> Bestand nicht gibt (`fetch_fred.py` deckt nur einen Teil ab). Das ist als Backlog-Punkt in
> `algo/PLAN.md` zu vermerken, nicht als stille Auslassung.

Jedes Fenster wird im Report **separat** ausgewiesen. Kein Fenster wird mit einem anderen
verrechnet, und ein Gesamtergebnis über alle Fenster ist keine Kennzahl dieser Spec — es würde
ein gutes Fenster hinter sieben mittelmäßigen verstecken.

Begründung für die Erweiterung über die drei SB-Fenster hinaus: Bei 23 Jahren × 10 Paaren ist
die Stichprobe erstmals groß genug, dass die Daten die Fensterwahl entscheiden können, statt
einer Vorannahme zu folgen. Das entspricht dem Projektstandard „falsifizierbare Behauptung statt
Meinungsstück" (`CLAUDE.md`, Algo-Trading: Arbeitsstandards).

---

## 3. Nicht-Ziele

- **Kein Broker, keine Ausführung.** Kein IBKR-Forex-Kontrakt, kein `live_status.py` auf Paaren,
  keine Order-Schnittstelle. Das ist Phase 3 und braucht erst belastbare Zahlen aus dieser Phase.
- **Keine Änderung an MNQ-Ergebnissen.** Jede Zahl, die `algo/selfcheck.py` heute liefert, muss
  danach identisch sein (§7).
- **Kein Refactoring der MNQ-Module.** Ausdrücklich auch dann nicht, wenn es die technisch
  sauberere Lösung wäre — siehe §4.3.
- **Kein Swap-/Rollover-Modell.** Stattdessen Glattstellung vor dem Rollover (§5.4).
- **Kein Tick-Daten-Bestand, kein gemessener Spread.** Die Beschaffung von Bid/Ask-Daten
  (Dukascopy, IBKR) ist ein eigenes Vorhaben; diese Spec kommt mit Bid-Daten aus und macht die
  Unsicherheit über den Break-even-Spread sichtbar statt sie zu kaschieren.

---

## 4. Struktur und Schnitt

### 4.1 Neu: das Paket `algo/forex/`

```
algo/forex/
  __init__.py      Paket-Marker, keine Logik
  pnl.py           Pip-Wert, Lot-Sizing, $-P&L, Spread-Kosten, Break-even-Spread
  rules.py         Fenstersatz (§2.4), sb_entry_signal(), plan_trade(), plan_trade_hp_fvg()
  backtest.py      Strategy-Klasse + Runner (Daten über marktdaten.bars)
  ensemble.py      Forex-Analogon zum MNQ/ES-Feature-Paar
  stress.py        Forex-Krisenfenster
  selfcheck.py     bündelt die Selbstchecks aller Forex-Module + Drift-Wächter
```

Ergebnis-Artefakte gehen nach `algo/results/forex_<modul>_<SYM>.json`. Kein bestehendes
MNQ-Artefakt wird berührt. `algo/cache/` bleibt gitignored.

### 4.2 Geteilt — importiert, nicht kopiert

Importieren ist kein Überschreiben. Diese Module bleiben unverändert und werden von
`algo/forex/` benutzt:

| Modul | Was daraus gebraucht wird |
|---|---|
| `tools/analyze_ohlc.py` | `Bar`, `fvgs()`, `swings()`, `hp_context()`, `untouched_levels()`, `KILLZONES`, `TICK_SIZE`, `to_tick()`, `SESSION_TYP`, `PIP_SIZE`, Guard |
| `algo/marktdaten.py` | `bars(symbol, tf, von, bis)` — Tagesgrenze und DST-Anker bereits korrekt |
| `algo/backtest_common.py` | `load_rows()`, `pearson()`, `write_result()` |
| `algo/validate.py` | `run()`, `parameter_sensitivity()`, `walk_forward()`, `monte_carlo()`, `double_bootstrap_drawdown()` — vollständig symbol-agnostisch |
| `algo/risk_fixed.py`, `risk_kelly.py`, `risk_garch.py` | einheitliches `risk_pct(...)`-Interface |
| `algo/risk_killswitch.py` | `allowed(peak, current)` |
| `algo/confidence.py` | `bar_metrics(trades, df)` |

**Befund, der den Zuschnitt trägt:** `validate.py` nimmt `(df, strategy_cls, bt_kwargs)` und
kennt kein Symbol. Die gesamte Validierungsstufe der Roadmap ist damit ohne jede Duplikation
nutzbar.

### 4.3 Unangetastet und nicht ersetzt

`algo/pnl.py`, `algo/rules.py`, `algo/signals.py`, `algo/backtest_bt.py`,
`algo/backtest_ensemble.py`, `algo/stress_test.py`, `algo/selfcheck.py`, `algo/masters.py`,
`algo/live_status.py`. MNQ-only, behalten ihre Zahlen.

**Offengelegte Konsequenz der Nutzerentscheidung:** Es wird **keine** gemeinsame Basis aus
`algo/rules.py` extrahiert. Das wäre die sauberere Entkopplung, würde aber `rules.py` anfassen.
Der Preis ist reale Duplikation: ein Bugfix in der FVG-Entry-Erkennung muss künftig in
`algo/rules.py` **und** `algo/forex/rules.py` gemacht werden.

**Gegenmaßnahme (kein Ersatz, nur Sichtbarmachung):** `algo/forex/selfcheck.py` enthält einen
Drift-Wächter, der die dupliziert übernommenen Funktionsrümpfe gegen ihre MNQ-Vorlage
vergleicht und meldet, wenn eine Seite sich bewegt hat und die andere nicht. Damit wird die
Drift ein sichtbares Ereignis statt eines schleichenden Auseinanderlaufens.

### 4.4 Zwilling oder `--symbol`? Die Trennlinie

Die Modul-Inventur (§2.3) listet vierzehn Module, die auf Forex laufen. Ein Zwilling für jedes
davon wäre absurd — die meisten sind reine Auswertungsskripte ohne eigene Handelslogik. Es gibt
deshalb zwei Klassen, und die Grenze verläuft entlang der Frage, ob ein Modul **Handelslogik
enthält** oder nur **Daten auswertet**:

**Klasse 1 — echter Zwilling in `algo/forex/`:** Module mit Regel-, P&L- oder Sizing-Logik.
Das sind genau die sieben aus §4.1. Hier ist Duplikation die Nutzerentscheidung.

**Klasse 2 — additiver `--symbol`-Parameter am bestehenden Modul:** die reinen Auswertungs-
skripte aus §2.3. Ein Flag mit Default `MNQ` **ändert das MNQ-Verhalten nicht** — es fügt einen
Codepfad hinzu, der ohne das Flag nie betreten wird. Der Regressionsnachweis (§7.2) belegt das
mechanisch.

**Präzedenzfall, nicht Neuerfindung:** Genau dieses Muster wurde in Phase 1 bereits angewandt
und vom Nutzer freigegeben — `backtest_seasonal.py`, `backtest_macro.py`, `macro_db.py` und
`mor_levels.py` haben ihr `--symbol` dort bekommen, `backtest_midnight_range_std.py` sogar einen
vollen Forex-Zweig. Für `backtest_tgif.py`, `backtest_daily_patterns.py`, `backtest_ohlc.py` und
`backtest_nfp_week.py` steht es noch aus und wird hier nachgezogen.

**Abgrenzung zur Nutzervorgabe:** „Die aktuellen sollen nicht überschrieben werden" wird gelesen
als *meine MNQ-Zahlen und mein MNQ-Verhalten müssen unverändert überleben* — nicht als
*kein Zeichen darf sich in irgendeiner Datei ändern*. Bei einem additiven Default-Flag ist die
erste Bedingung mechanisch prüfbar erfüllt, während die zweite Lesart vierzehn sinnlose Kopien
erzwingen würde. Die Kernmodule aus §4.3 bleiben davon unberührt: **die** werden nicht angefasst,
weder additiv noch sonstwie.

> Falls der Nutzer das anders sieht, ist das die eine Stelle dieser Spec, an der eine Korrektur
> spürbar mehr Arbeit bedeutet — dann bräuchte Klasse 2 ebenfalls Zwillinge.

---

## 5. `algo/forex/pnl.py` — der $-P&L

Der heikelste Teil dieser Spec, weil hier still falsche Zahlen entstehen können, die plausibel
aussehen.

### 5.1 Pip-Wert, zeitpunktgenau statt genähert

Standardlot = 100.000 Einheiten Basiswährung, Micro-Lot = 1.000. Pip-Wert in Quote-Währung =
`PIP_SIZE × Einheiten`. Die Umrechnung nach USD zerfällt in drei Fälle:

| Fall | Paare | Pip-Wert USD je Standardlot |
|---|---|---|
| **XXX/USD** | EURUSD, GBPUSD, AUDUSD, NZDUSD | konstant **$10**, keine Umrechnung |
| **USD/XXX** | USDJPY, USDCHF, USDCAD | `(PIP_SIZE × 100.000) ÷ Kurs_t` — Kurs steht im eigenen Datensatz |
| **Cross** | EURGBP, EURJPY, GBPJPY | über `GBPUSD_t` bzw. `USDJPY_t`, beide im Cache vorhanden |

Alle Referenzkurse liegen im Bestand, die Umrechnung ist also **exakt zum Trade-Zeitpunkt**
möglich und wird auch so gebaut — kein Periodendurchschnitt, kein Endkurs.

**Fehlender Referenzkurs:** Fehlt zum Zeitpunkt `t` die Kerze im Referenzpaar (Datenlücke), wird
der Trade **verworfen und gezählt**, nicht mit einer Näherung bewertet. Die Anzahl verworfener
Trades ist Pflichtangabe im Report. Das ist die „Marktdaten wie Gold"-Nulltoleranz-Regel,
angewandt auf abgeleitete Größen.

### 5.2 Spread — inklusive der Short-Asymmetrie

Der Bestand ist **Bid**. Daraus folgt:

- **Long:** Kauf zum Ask (`Bid + Spread`), Verkauf zum Bid.
- **Short:** Verkauf zum Bid, Rückkauf zum Ask (`Bid + Spread`).

Die vollen Spread-Kosten fallen also genau **einmal je Round-Trip** an, nicht zweimal halb.

**Der Punkt, den man leicht übersieht — die Stop-Auslösung:** Ein Long-Stop wird beim Bid
ausgelöst; die Bid-Kerze zeigt das korrekt. Ein **Short-Stop wird beim Ask ausgelöst**, also
`Spread` früher, als die Bid-Kerze aussehen lässt. Ohne diese Modellierung fallen Short-Ergebnisse
systematisch zu gut aus. `algo/forex/backtest.py` prüft Short-Stop **und** Short-Target deshalb
gegen `Bid + Spread`.

### 5.3 Default-Spreads

Konservativ am oberen Rand retail-typischer ECN-Spreads angesetzt. **Gesetzt, nicht gemessen** —
im Report ausdrücklich als solche gekennzeichnet.

| Paar | Pips | Paar | Pips |
|---|---|---|---|
| EURUSD | 0,6 | USDCAD | 1,2 |
| USDJPY | 0,7 | EURGBP | 1,1 |
| GBPUSD | 0,9 | EURJPY | 1,3 |
| AUDUSD | 0,8 | GBPJPY | 2,2 |
| USDCHF | 1,0 | NZDUSD | 1,4 |

### 5.4 Break-even-Spread — Pflichtkennzahl

In **jedem** Forex-Report, analog zu `dubious_pct` auf der MNQ-Seite: ab welchem Spread kippt
das Ergebnis ins Minus. Zusammen mit `dubious_pct` und der Flat-Quote des ausgewerteten Fensters
(§1.1) sind das die **drei Pflichtangaben** jedes Forex-Reports.

**Numerisch bestimmt, nicht analytisch.** Der naheliegende Ansatz „Brutto-Pips ÷ Trade-Anzahl"
ist falsch, weil der Spread über die Short-Stop-Asymmetrie (§5.2) mitbestimmt, *welche* Trades
überhaupt ausgestoppt werden — die Trade-Menge ist selbst spread-abhängig. Der Backtest läuft
deshalb über eine Spread-Achse, und die Nullstelle des Netto-P&L wird gesucht.

Damit steht keine geratene Zahl als Wahrheit im Report. Die entscheidende Aussage ist nicht
„die Regel macht $X", sondern „die Regel verträgt bis Y Pips Spread".

### 5.5 Swap/Rollover — vermieden statt geraten

Kein Swap-Modell. Stattdessen wird jede Position **vor dem nächsten Rollover glattgestellt**:
spätestens um 16:59 NY des Rollover-Zyklus, in dem sie eröffnet wurde. Präzise formuliert, weil
die Asia-Killzone das nicht-triviale Beispiel ist — ein Trade, der Montag 19:00 eröffnet, liegt
*nach* dem Montags-Rollover; sein Zwangsschluss ist Dienstag 16:59, unmittelbar vor dem
Dienstags-Rollover. Er kreuzt also keinen. Ein Trade aus der London-Killzone am Dienstag 03:00
wird ebenfalls Dienstag 16:59 geschlossen.

Trades, die ohne diese Regel über einen Rollover gelaufen wären, werden gezählt und im Report
ausgewiesen — damit sichtbar bleibt, wieviel die Regel kostet und ob ein Swap-Modell später
überhaupt lohnt.

### 5.6 Kommission

$7 je Standardlot Round-Turn als Default (ECN-typisch), als Parameter auf 0 setzbar für ein
reines Spread-Broker-Modell. Geht in den Netto-P&L **und** in die Break-even-Rechnung ein.
Begründung für „nicht 0 als Default": Auf der MNQ-Seite fiel die Kommission im Audit vom
2026-08-06 zunächst komplett unter den Tisch und machte die Zahlen um eine Größenordnung zu
optimistisch (siehe `algo/pnl.py::real_pnl`). Derselbe Fehler wird hier nicht wiederholt.

### 5.7 Sizing

```python
lot_size(equity, risk_pct, entry, stop, symbol, t) -> float   # Lots, auf 0,01 abgerundet
```

- Risiko-Budget USD = `equity × risk_pct`.
- Verlust je Lot bei Stop-Out = Stop-Distanz in Pips × Pip-Wert-USD(symbol, t).
- **Abgerundet** auf 0,01 Lot, nie aufgerundet — dieselbe Logik wie die gerichtete Tick-Rundung
  in `pnl.round_to_tick`: die Rundung darf nie zugunsten des Backtests ausfallen.
- Hebel-Deckel analog `pnl.risk_size`'s `max_notional`.
- **Startkapital 100.000 USD, `max_risk_pct` = 0,01** — identisch zur MNQ-Seite
  (`backtest_bt.py:81,89`), damit die beiden Serien überhaupt vergleichbar sind.

**Warum ein eigener Zwilling und nicht `pnl.risk_size` mit anderem `point_value`:**
`pnl.risk_size()` ist parametrisch bereits symbol-agnostisch, liefert aber ein `int`
(Kontraktzahl). Forex braucht 0,01-Lot-Granularität, also einen gerundeten `float`. Das ist ein
Rückgabetyp-Unterschied, kein Parameterwert.

---

## 6. Regel-Schicht und Simulation

### 6.1 `algo/forex/rules.py`

Portierung von `sb_entry_signal()`, `plan_trade()` und `plan_trade_hp_fvg()` mit **derselben
Logik**, drei Änderungen:

1. `WINDOWS` wird zu einer Liste mit Herkunftskennzeichnung (SB-Fenster vs. Killzone, §2.4), der
   Fenstername steht im `TradeSetup`, damit der Report je Fenster trennen kann.
2. Tick-Rundung über `analyze_ohlc.to_tick()` statt über `pnl.round_to_tick()` — gleiche
   Funktion, anderer Einstieg, damit `algo/pnl.py` unberührt bleibt.
3. Keine Aufrufe von `org_gap`/`ndog_gap`/1p-Logik (§2.2).

Unverändert übernommen: kein Lookahead (`bars[t <= when]`), `CONTEXT_BARS = 60` Kerzen Vorlauf
für `size_rel`, die Regel „die 3-Kerzen-Formation muss komplett im Fenster liegen" und der
Hinweis dazu, dass ein randüberlappendes FVG nicht ungültig, sondern nur kein *1st Presented*
FVG ist (Nutzerklärung 2026-08-11).

### 6.2 `algo/forex/backtest.py`

Strategy-Klasse auf derselben `backtesting`-Bibliothek, Daten über `marktdaten.bars(symbol, tf)`.
Übernimmt die drei Korrektheits-Pflichten aus `CLAUDE.md`:

1. **Echter Geldwert statt Notional-Prozent** — hier über den Pip-Wert aus §5.1.
2. **Konservative Fill-Reihenfolge** bei Stop *und* Ziel in derselben Kerze, mit `dubious_pct`
   als Pflichtkennzahl in jedem Report.
3. **Kein Lookahead** in Signalen und Modellen.

Forex-spezifisch zusätzlich: Short-Stop-Asymmetrie (§5.2) und 16:59-Glattstellung (§5.5).

### 6.3 `algo/forex/ensemble.py`

Das MNQ-Modell nutzt **MNQ/ES** als Feature-Paar — zwei korrelierte Indizes, wobei das zweite
Instrument den Bias bestätigt oder ihm widerspricht. Das Forex-Analogon ist der **USD-Korb**:
EURUSD/GBPUSD als Hauptpaare, USDJPY als Gegenrichtung. Dieselbe `LogisticRegression`, dieselbe
Feature-Bauweise, derselbe Bias-Filter.

Konzeptueller Anker im Vault: `wiki/concepts/SMT (Smart Money Divergence).md`, Abschnitt
*„Forex: immer gegen den DXY"*.

### 6.4 `algo/forex/stress.py`

Dieselbe Verhaltenscharakterisierung wie `stress_test.py`, andere Fenster — Aktienindex-Krisen
sind für Forex die falschen Ereignisse:

| Fenster | Zeitraum | Warum |
|---|---|---|
| GFC | 2008-09 – 2009-03 | breiter Risk-Off, USD-Funding-Stress |
| EUR-Krise | 2011-08 – 2012-07 | EUR-spezifisch, betrifft EURUSD/EURGBP/EURJPY |
| **CHF-Schock** | 2015-01-15 | SNB-Mindestkurs-Aufgabe, härtester Einzeltest überhaupt |
| Brexit | 2016-06-24 | GBP-Gap über Nacht |
| Covid | 2020-03 | Liquiditätskollaps über alle Paare |
| GBP-Mini-Budget | 2022-09 – 2022-10 | GBPUSD-Absturz Richtung Parität |

Der 23-Jahres-Bestand deckt alle sechs ab. Das ist der eigentliche Gewinn gegenüber MNQ, dessen
Historie nicht so weit zurückreicht (`stress_test.py` behilft sich dort mit einem NQ/ES-Proxy).

### 6.5 `algo/forex/selfcheck.py`

Bündelt die `assert`-Selbstchecks aller Forex-Module (Projektstandard: jedes Modul hat einen im
`__main__`) plus den Drift-Wächter aus §4.3. Mindestumfang:

- Pip-Wert je Fallgruppe aus §5.1 (XXX/USD konstant $10; USD/XXX gegen Kurs; Cross gegen
  Referenzpaar), plus der Verwerfungsfall bei fehlendem Referenzkurs.
- Lot-Abrundung: ein Ergebnis von 0,0349 Lot muss 0,03 werden, nie 0,04.
- Fenster: ein Zeitpunkt in genau einer Killzone liefert genau ein aktives Fenster.
- Kein Lookahead: `plan_trade` mit abgeschnittener Historie liefert dasselbe wie mit voller.
- Short-Stop-Asymmetrie: ein Short, dessen Stop nur durch den Spread getroffen wird, muss als
  Stop-Out zählen.
- 16:59-Glattstellung: ein Setup, das später schließen würde, wird zwangsgeschlossen und gezählt.

---

## 7. Validierung und Regressionssicherung

### 7.1 Validierung

Läuft vollständig über das importierte `algo/validate.py`, ohne eine Zeile darin zu ändern:
Parameter-Sensitivität, Walk-Forward (rollierende Folds, Out-of-Sample ohne Refit),
Monte-Carlo-Resampling, Bootstrap-Drawdown. Bei 23 Jahren × 10 Paaren ist Walk-Forward hier zum
ersten Mal in diesem Projekt mit belastbarer Fold-Zahl möglich — auf der MNQ-Stichprobe war die
Fold-Zahl bisher der begrenzende Faktor.

Eine Regel gilt erst dann als verstanden, wenn sie über mehrere Verfahren hinweg **konsistent**
abschneidet (nicht zwingend profitabel) — Roadmap-Stufe 3 aus `CLAUDE.md`.

### 7.2 Regressionsnachweis: MNQ ist unangetastet

Die Kernbedingung des Nutzers wird **nachgewiesen, nicht behauptet**:

1. **Vor** der ersten Zeile Code: `python algo/selfcheck.py` laufen lassen, MNQ-Kennzahlen
   einfrieren (Datei unter `algo/results/`, versioniert).
2. **Nach** Fertigstellung: erneut laufen lassen, diffen. Jede Abweichung ist ein Bug, kein
   Fortschritt.
3. `git status` / `git diff --stat` muss zeigen, dass keine der in §4.3 gelisteten Dateien
   geändert wurde. Das ist mechanisch prüfbar und geht in den Abschlussbericht.

---

## 8. Reihenfolge

1. **Vorarbeit:** `python algo/build_parquet.py` für alle 10 Paare. Der Cache existiert auf
   diesem Rechner nicht (§1). Zwingend vor dem ersten Backtest, dauert. *(erledigt 2026-08-15:
   `pyarrow` nachinstalliert, Bau angestoßen)*
2. MNQ-Baseline einfrieren (§7.2, Schritt 1). *(erledigt 2026-08-15: alle 26 Selbstchecks grün,
   Ausgabe unter `algo/results/mnq_baseline_2026-08-15.txt`)*
3. `algo/forex/pnl.py` + Selbstcheck.
4. `algo/forex/rules.py` + Selbstcheck.
5. `algo/forex/backtest.py` + Selbstcheck, erster Lauf auf EURUSD.
6. Break-even-Spread-Achse (§5.4), Ergebnis gegen die Default-Spreads aus §5.3 halten.
7. `algo/forex/ensemble.py`, `algo/forex/stress.py`.
8. Klasse-2-Module aus §4.4 nachziehen (`--symbol` für `backtest_tgif.py`,
   `backtest_daily_patterns.py`, `backtest_ohlc.py`, `backtest_nfp_week.py`), dann die
   Auswertungsskripte aus §2.3 über die 10 Paare laufen lassen. Bei
   `backtest_fvg_specialness.py` These 1 überspringen (§2.3, Korrektur 1).
9. Validierung über `validate.py` für alle 10 Paare.
10. MNQ-Regressionsdiff + `git status`-Nachweis (§7.2).
11. `algo/PLAN.md`, `algo/README.md`, `wiki/synthesis/`, `wiki/log.md` nachziehen.

Schlägt Schritt 2 oder 10 fehl, wird gemeldet statt weitergebaut.

**Zuschnitt für die Umsetzung:** Die Schritte 1–6 bilden den ersten Implementierungsplan — an
ihrem Ende steht eine erste belastbare $-Zahl mit Break-even-Spread auf EURUSD, also der Punkt,
an dem sich beurteilen lässt, ob der Rest überhaupt lohnt. Die Schritte 7–11 (Ensemble,
Stress-Test, Klasse-2-Nachzug, Vollauswertung über 10 Paare, Dokumentation) bekommen einen
eigenen Plan, sobald Schritt 6 Zahlen geliefert hat. Grund: Ensemble und Stress-Test bauen auf
Kennzahlen auf, die Schritt 6 erst erzeugt — sie jetzt schon durchzuplanen hieße, ihre Parameter
zu raten.

---

## 9. Was diese Spec bringt — und was nicht

**Bringt:** Die Regel-Schicht wird erstmals gegen 23 Jahre × 10 Instrumente geprüft statt gegen
eine zweistellige MNQ-Tagesmenge. Walk-Forward und Stress-Test bekommen erstmals eine
Stichprobe, die die Verfahren tragen. Und die Frage, ob die Silver-Bullet-Fenster ein echtes
Zeitmuster oder eine MNQ-Eigenheit sind, wird beantwortbar.

**Bringt nicht:** Die ORG-C.E.-70 %-These (aktuell 35–43 % auf MNQ, vom Nutzer ausdrücklich als
*„weiter beobachten"* markiert) lässt sich über Forex **nicht** breiter absichern — sie fällt
unter §2.2. Gleiches gilt für alle 1p-FVG-Thesen. Diese bleiben auf der MNQ-Stichprobe und
wachsen weiter nur im Tagesrhythmus; sie werden wie bisher in jedem Bericht mitkommentiert.

**Übertragbarkeit ist keine Einbahnstraße.** Bestätigt sich ein Muster auf Forex, ist das ein
Hinweis auf marktübergreifendes algorithmisches Verhalten. Bestätigt es sich nicht, kann es
trotzdem ein echtes Index-Futures-Spezifikum sein. Beide Richtungen werden als Befund notiert,
keine als Widerlegung der jeweils anderen Serie.

**Der Spread bleibt die größte Unsicherheit.** Solange kein Bid/Ask-Bestand vorliegt, ist jede
$-Zahl dieser Spec so gut wie die Annahme in §5.3. Deshalb ist der Break-even-Spread die
Pflichtkennzahl und nicht der P&L — er ist die einzige Zahl, die von dieser Annahme unabhängig
ist.
