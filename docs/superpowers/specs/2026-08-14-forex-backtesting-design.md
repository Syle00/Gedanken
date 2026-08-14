# Forex-Backtesting auf der 1m-Tiefenhistorie — Design-Spec

- **Datum:** 2026-08-14
- **Status:** entworfen, nicht umgesetzt
- **Auslöser:** Jannes: *"ich habe mehr daten das sind forex daten mit denen möchte ich auch
  backtesten mit allen modulen die vorhanden sind"*. Der histdata.com-Bulk-Import ist seit dem
  2026-08-14 abgeschlossen (10 Paare, 1m, 2003–2026), aber kein einziges Backtest-Modul kann
  den Bestand lesen.
- **Entscheidung des Nutzers zum Ziel:** *Validierung zuerst, Handelsfähigkeit später.* Forex
  dient in Phase 1 als 23-Jahres-Testfeld für die bestehenden ICT-Thesen. Ob der Algo Forex
  jemals handelt, ist ein separater, späterer Schritt (Phase 2) und nicht Teil dieser Spec.
- **Vorgänger:** `2026-08-12-marktdaten-schicht-design.md` (Bestandsaufnahme, 1m-Vorrang),
  `2026-08-08-algo-zielbild-design.md` §4.3 (Datenhaltung). Diese Spec ist die erste, die den
  Bestand über MNQ hinaus öffnet.

---

## 1. Bestandsaufnahme (gemessen am 2026-08-14, nicht geschätzt)

### 1.1 Was vorliegt

`raw/marktdaten-tief/<jjjj>/<mm>/<tt.mm.jjjj>/<SYM> <jjjj-mm-tt> 1m (bid).csv`

| Kennzahl | Wert |
|---|---|
| Tagesdateien | 73.100 |
| Symbole | EURUSD, GBPUSD, USDJPY, USDCHF, AUDUSD, USDCAD, NZDUSD, EURJPY, EURGBP, GBPJPY |
| Zeitraum | 2003–2026 (NZDUSD ab 2005 — für 2003/2004 existiert bei histdata.com keine Seite) |
| Auflösung | ausschließlich 1m |
| Preisart | **Bid** (nicht Mid) |
| Volumen roh | 3,81 GB, ~92 Mio Minutenkerzen |
| Kerzen/Tag | 1.427–1.437 (Vollhandelstag), 418 (Sonntag ab Marktöffnung) |
| Zeitstempel | Epoch-Sekunden UTC, Spalten `time,open,high,low,close` |

### 1.2 Tagesgrenze — der kritischste Einzelbefund

Die Forex-Tagesordner folgen dem **NY-Kalendertag**: 00:00–23:59 NY, sonntags ab 17:01
(Marktöffnung), freitags bis 16:59 (Marktschluss). Verifiziert an Mi 07.01., Do 08.01.,
So 11.01. und Mo 12.01.2026.

Der MNQ-Bestand folgt dagegen dem **Futures-Handelstag**: 18:00 des Vorabends bis 17:00, mit
Globex-Pause 17:00–18:00 (siehe `backtest_macro.py:56`, `macro_db.py:36`).

Das sind zwei unterschiedliche Konventionen für denselben Begriff „Tag". Ein Modul, das die
Futures-Grenze fest annimmt und auf Forex-Daten losgelassen wird, schneidet stillschweigend
den falschen Zeitraum — die Zahlen sehen dabei plausibel aus. Genau der Fehlertyp, den
`CLAUDE.md` unter „Zeit vor Preis" als am schädlichsten benennt.

**Konsequenz für das Design:** Die Tagesgrenze ist keine Konstante. Sie wird aus `SESSION_TYP`
(§3) abgeleitet — kein eigenes drittes dict — und vom Loader angewandt, nicht von den Modulen.

### 1.3 Bekannte Grenzen des Bestands (aus `algo/PLAN.md`, hier nicht neu erhoben)

- **Juli/August 2026 nicht konsolidiert.** histdata.com liefert für die jüngsten 1–2 Monate
  widersprüchliche Duplikate (2–57 je Chunk, bei GBPJPY bis 119). Vor präzisionskritischer
  Nutzung erneut ziehen und diffen.
- **Bestandsende 11.08.2026**, letzter Tagesordner enthält nur 1 statt 10 Dateien — der Rand
  ist unvollständig und muss nachgezogen werden.
- **Bid statt Mid.** Der Dukascopy-Mid-Bestand fehlt (IP-Sperre, verifiziert 2026-08-14). Für
  Struktur-Statistik (FVG, Sweep, Displacement) ist Bid unkritisch, für Spread-abhängige
  Aussagen nicht — solche gibt es in Phase 1 nicht.
- **2000–2002** liegt nur als Legacy-XLSX für EURUSD vor, nicht im Bulk. Nicht Teil dieser Spec.

### 1.4 Der Altbestand ist teilweise Attrappe

Die yfinance-Forex-Dateien in `raw/marktdaten/` sind auf 1m-Ebene messbar unbrauchbar: Anteil
Kerzen mit `open=high=low=close` bei EURUSD 2026-08-10/11/12 jeweils **100,0 %** (1.380 bzw.
1.439 Kerzen ohne jede Range). Deckt sich mit dem PLAN-Eintrag vom 2026-08-12 (AUDUSD, GBPUSD,
NZDUSD je 100 %, EURUSD 93,9 %). Auf solchen Kerzen ist weder FVG noch Displacement noch Sweep
messbar.

---

## 2. Nicht-Ziele

Ausdrücklich **nicht** Teil dieser Spec, um Scope-Drift zu vermeiden:

- Kein `$`-P&L für Forex, kein Pip-Wert in `pnl.py`, kein Spread-Modell, keine Margin-Rechnung.
- Keine Forex-Regel in `algo/rules.py`. Die Regel-Schicht bleibt MNQ-only.
- Keine IBKR-Forex-Kontrakte.
- Keine Änderung an MNQ-Ergebnissen. Jede Zahl, die `selfcheck.py` heute liefert, muss danach
  identisch sein (§7).

---

## 3. Instrumenten-Metadaten: zwei Attribute, kein Framework

In `tools/analyze_ohlc.py` neben dem bestehenden `TICK_SIZE`:

```python
SESSION_TYP = {"MNQ": "futures_rth", ..., "EURUSD": "24x5", ...}
PIP_SIZE    = {"EURUSD": 0.0001, ..., "USDJPY": 0.01, "EURJPY": 0.01, "GBPJPY": 0.01}
```

Zwei dicts neben dem, das schon da ist. Keine Instrument-Klasse, keine Registry, kein
Vererbungsbaum — es gibt genau zwei Session-Typen und die Liste der Symbole ist bekannt.

**`SESSION_TYP` steuert drei Dinge:**

1. Die Tagesgrenze (§1.2): `futures_rth` → 18:00 Vorabend..17:00, `24x5` → 00:00..23:59 NY.
2. Den Guard für eröffnungsabhängige Detektoren (§4).
3. Ob `RTH`-Varianten überhaupt existieren.

**`PIP_SIZE` stellt Vergleichbarkeit her.** Ohne sie ist eine FVG-Größe von `0.00042` nicht
gegen „MNQ 12 Punkte" lesbar. Ergebnisse in Gruppe A/B werden in Pips ausgegeben, nicht in
Rohpreis.

---

## 4. Der Guard: was in Forex strukturell nicht existiert

### 4.1 Das Kriterium

Nutzerkorrektur vom 2026-08-14, zweistufig: *"in forex gibt es kein opening range gap ebenso
das c.e der opening range gap"* und *"1p fvg der woche ist auch nur für future wie opening
range gap auch erstes fvg nach 9.30 ndog gibt es nicht aber nwog gibt es"*.

Der gemeinsame Nenner ist **nicht** „ORG" — es ist **die 9:30-Eröffnung als Ereignis**. ORG,
1.p FVG (täglich wie wöchentlich), erstes FVG nach 9:30 und der Open Drive setzen alle voraus,
dass der Markt vorher geschlossen war. Ein 24/5-Markt hat weder Schluss noch Eröffnung, also
kein Gap, keine Eröffnungsauktion und kein „erstes" FVG danach.

Das ist ein Kriterium, kein Modul-für-Modul-Urteil, und daher als **ein** Attribut
implementierbar statt als sechs Einzelguards.

### 4.2 Warum ein Guard und nicht bloß „das Modul nicht starten"

`org_gap()` misst den Abstand zwischen der ~16:14-Kerze des Vortags und der 9:30-Kerze
(`tools/analyze_ohlc.py:364`). Auf Forex-Daten existieren **beide Kerzen** — sie laufen nur
durchgehend ineinander. Die Funktion würde also keinen Fehler werfen, sondern eine plausibel
aussehende Zahl liefern, die nichts weiter misst als die normale Übernacht-Bewegung.

Still falsch ist schlimmer als sichtbar leer. Der Guard sitzt deshalb in `analyze_ohlc.py` an
der geteilten Basis (Präzedenzfall: PLAN-Eintrag zur Tick-Rundung, „eine Funktion an der
geteilten Basis statt sechs Einzelguards") und greift auch für Module, die es noch nicht gibt.

### 4.3 Betroffene Funktionen

| Funktion | Bei `24x5` | Begründung |
|---|---|---|
| `org_gap()` | `None` | kein Close/Open, also kein Gap |
| `ndog_gap()` | `None` | keine tägliche Handelspause |
| `nwog_gap()` | **bleibt aktiv** | Wochenendgap Fr 17:00 → So 17:01 NY ist real und im Bestand belegt (§1.1) |

---

## 5. Datenschicht

### 5.1 `algo/marktdaten.py` (neu) — ein Einstieg für alle Backtests

```python
bars(symbol, tf, von=None, bis=None) -> list[Bar]
```

- **Forex** → liest `algo/cache/<SYM>_1m.parquet`, resampled auf `tf`.
- **Futures** → unverändert der bestehende CSV-Pfad (`find_days()` + `analyze_ohlc.load()`).

Rückgabetyp ist die bestehende `Bar`-Liste aus `tools/analyze_ohlc.py`. Damit laufen **alle**
vorhandenen Detektoren (`fvgs()`, `swings()`, `untouched_levels()`, `hp_context()`) unverändert
auf Forex. Kein Detektor wird angefasst.

### 5.2 `algo/build_parquet.py` (neu) — einmalige Aufbereitung

73.100 CSVs → 10 Parquet-Dateien, idempotent, `algo/cache/` gitignored, jederzeit aus `raw/`
neu baubar. Erwartete Größe ~400–600 MB gegen 3,81 GB roh.

**Neue Dependency `pyarrow`** (fehlt aktuell; pandas 3.0 braucht sie für Parquet). Bewusste
Entscheidung: CSV-Parsen von 92 Mio Zeilen kostet Minuten pro Lauf, Parquet Sekunden. Die
Alternative ohne neue Dependency wäre pandas-Pickle — unkomprimiert ~3,7 GB und
versionsabhängig. Für einen reinen, neu baubaren Cache wäre auch das vertretbar; der Tausch
lohnt hier nicht.

### 5.3 Resampling — Anker an NY-Mitternacht

`pandas.resample()` verankert per Default an UTC-Mitternacht. Bei `4h` liegen die Kerzen dann
um Stunden verschoben zu jedem ICT-Zeitfenster, während die OHLC-Werte für sich korrekt
aussehen. Der Loader verankert explizit an **NY-Mitternacht**, `label="left"`,
`closed="left"`. Datetime64-Auflösung explizit über `.as_unit("s")` (Projektstandard, siehe
`algo/fetch_yfinance.py`).

### 5.4 Verifikationspflicht vor Freigabe der Daten

Nach `CLAUDE.md` („Marktdaten wie Gold behandeln") gelten die Daten erst als nutzbar, wenn:

1. **Zeit gegen unabhängige Quelle geprüft:** resampeltes 1h aus histdata gegen die
   vorhandenen yfinance-1h-Forex-CSVs derselben Tage. Bid vs. Mid ergibt einen kleinen,
   konstanten Preisoffset — ein *Zeitversatz* fällt dagegen sofort auf. Nur die 1h-Dateien
   taugen als Referenz; die 1m-Dateien sind Attrappen (§1.4).
2. **Vollständigkeit gelistet, nicht angenommen:** Kerzen je Tag gegen Erwartungswert, fehlende
   Tage je Symbol/Jahr explizit ausgegeben. Lücken werden aufgelistet, nicht stillschweigend
   hingenommen.
3. **Attrappen-Quote gemessen:** Anteil `o=h=l=c` je Symbol/Jahr. Der histdata-Bestand sollte
   im Promillebereich liegen; alles darüber wird gemeldet, bevor irgendein Backtest startet.

Schlägt einer der drei Punkte fehl, wird gemeldet statt weitergebaut.

---

## 6. Modul-Matrix

Vom Nutzer am 2026-08-14 bestätigt.

| Gruppe | Module | Bedingung |
|---|---|---|
| **A — nur 1d nötig** | `seasonal`, `daily_patterns`, `tgif`, `nfp_week`, `ohlc` | läuft, sobald §5 steht |
| **B — läuft auf Forex** | `macro`, `macro_db`, `midnight_range_std`, `midnight_range_judas`, `fvg_strength`, `hp_fvg`, `nwog` | reine Zeit-/Strukturdefinition, zusätzlich Pip-Normierung (§3) und korrekte Tagesgrenze (§1.2) |
| **C — futures-only** | `org_ce`, `org_std_extrema`, `1p_mindestgroesse`, `1p_fvg_woche`, `fvg_specialness`, `open_drive_vs_sb`, `ndog`, alle `RTH`-Varianten | Guard nach §4, werden für Forex gar nicht erst gestartet |
| **D — Phase 2** | `backtest_bt`, `ensemble`, `validate`, `stress_test`, `risk_*`, `sb_session_liq` | brauchen `rules.py` + $-P&L, außerhalb dieser Spec |

**Einordnungsgründe, die nicht offensichtlich sind:**

- `1p_mindestgroesse` → C, weil seine These wörtlich lautet „Das 1.p FVG der NY-AM-Session
  **nach dem Opening Range Gap**" (`backtest_1p_mindestgroesse.py:2`).
- `open_drive_vs_sb` → C, weil es die Expansion 09:30–09:50 misst (`OPEN_WIN`, Zeile 36).
- `sb_session_liq` → D statt C: fällt nicht am Session-Typ, sondern daran, dass es Entry/Stop
  über `rules.py` simuliert.
- `hp_fvg` → B: Vortagesrange-Hälfte, Killzone und Bias brauchen keine Eröffnungsauktion.

**Namensbereinigung im Zuge der Arbeit:** `backtest_midnight_range_judas.py` verwendet die
Konstante `ORG` für *Opening Range* (Kerzen-Range der Fenster 0:00–0:30, 7:00–7:30, 13:30–14:00),
nicht für den *Opening Range Gap*. Das Modul läuft auf Forex, aber die Doppelbelegung hat die
Fehl-Einordnung in der ersten Design-Fassung mitverursacht. Umbenennung auf `OR`.

---

## 7. Regressionssicherung

`algo/selfcheck.py` (bündelt `pnl`, `rules`, `signals`, `backtest_ensemble`) muss nach der
Loader-Umstellung grün bleiben **und dieselben MNQ-Zahlen liefern wie vorher**. Verschiebt die
Umstellung ein MNQ-Ergebnis, ist das ein Bug, kein Fortschritt — die Futures bekommen einen
neuen Weg zu denselben Daten, nicht neue Daten.

Vorgehen: Kennzahlen vor der Umstellung festhalten, danach diffen.

Zusätzlich je neuem Modul ein `assert`-basierter Selbstcheck im `__main__` (Projektstandard),
mindestens: Resample-Anker (eine 4h-Kerze beginnt zur erwarteten NY-Stunde), Guard
(`org_gap()` auf einem Forex-Symbol liefert `None`), Tagesgrenze (Forex-Tag beginnt 00:00 NY,
MNQ-Tag 18:00 Vorabend).

---

## 8. Löschung der Attrappen-Dateien

Vom Nutzer entschieden (Option „alte Forex-Dateien löschen"). Weil das die Layer-1-Regel
„`raw/` ist unveränderlich" bricht, gilt ein eigenes Verfahren:

1. **Messen, nicht raten:** Skript listet jede Forex-Datei in `raw/marktdaten/` mit ihrem
   Flat-Anteil (`o=h=l=c`) und ihrer Kerzenzahl.
2. **Löschvorschlag nur über 90 % Flat-Anteil.** Nach heutigem Stand betrifft das die
   1m/5m/15m-Dateien.
3. **1d/1h/4h bleiben ausdrücklich erhalten** — sie sind nicht als Attrappen belegt, die
   1d-Reihe reicht bis 2000 zurück und deckt damit 2000–2002, was der histdata-Bestand *nicht*
   hat. Die 1h-Dateien werden zusätzlich als Verifikationsreferenz gebraucht (§5.4).
4. **Liste wird vorgelegt, gelöscht wird erst nach ausdrücklicher Freigabe.** Kein Löschen im
   selben Arbeitsschritt wie das Messen.

---

## 9. Reihenfolge

1. `build_parquet.py` bauen, laufen lassen.
2. Verifikation nach §5.4 (Zeit, Vollständigkeit, Attrappen-Quote). Bei Fehlschlag: melden,
   nicht weiterbauen.
3. `marktdaten.py` + `SESSION_TYP`/`PIP_SIZE` + Guard (§3, §4), mit Selbstchecks.
4. Löschliste messen → vorlegen → nach Freigabe ausführen (§8).
5. `backtest_common` auf den neuen Loader umstellen. `selfcheck.py`-Diff gegen den vorher
   festgehaltenen Stand (§7).
6. Gruppe A laufen lassen (10 Paare × 23 Jahre, nur 1d).
7. Gruppe B laufen lassen, Ergebnisse nach `wiki/synthesis/`.
8. `algo/PLAN.md`, `wiki/log.md`, `algo/README.md` und die Konzeptseite zur
   Eröffnungsauktions-Unterscheidung nachziehen.

---

## 10. Was diese Spec bringt — und was nicht

**Bringt:** Zwölf Module (Gruppe A + B) laufen statt auf einer zweistelligen MNQ-Tagesmenge auf
10 Paaren × 23 Jahren. Am meisten gewinnen die Macro-Fenster-Statistik und die
FVG-Stärke-Auswertung, wo die MNQ-Stichprobe bisher zu klein für belastbare Aussagen ist.

**Bringt nicht:** Die ORG-C.E.-70 %-These (aktuell 35–43 % auf MNQ, vom Nutzer ausdrücklich als
„weiter beobachten" markiert) lässt sich über Forex **nicht** breiter absichern — sie fällt
unter den Guard aus §4. Gleiches gilt für alle 1.p-FVG-Thesen. Diese bleiben auf der
MNQ-Stichprobe und wachsen weiter nur im Tagesrhythmus.

Ein Ergebnis aus Gruppe B ist zudem nicht automatisch auf MNQ übertragbar: bestätigt sich ein
Zeitfenster-Muster auf Forex, ist das ein Hinweis auf marktübergreifendes algorithmisches
Verhalten — bestätigt es sich nicht, kann es trotzdem ein echtes Index-Futures-Spezifikum sein.
Beide Richtungen werden als Befund notiert, keine als Widerlegung der jeweils anderen Serie.
