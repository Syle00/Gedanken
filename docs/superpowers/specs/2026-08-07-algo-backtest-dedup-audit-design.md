# Backtest-Skript-Entduplizierung & Audit fuer `algo/` — Design

Status: Design, genehmigt am 2026-08-07. Phase 1 von zwei — Phase 2 (TUI-Oberflaeche zur
interaktiven Auswahl/Vergleich der Backtests, "Bloomberg-Terminal"-Anspruch) ist ein eigener,
spaeterer Spec, der auf der hier gebauten `run()`-Schnittstelle aufsetzt.

## Ziel

Nutzerfrage: macht es bei ~20 Einzeldateien in `algo/` Sinn, das in eine interaktive Oberflaeche
zu ueberfuehren? Antwort nach Ruecksprache: nicht die Dateien zusammenlegen (die
"ein Skript pro These"-Konvention aus `CLAUDE.md` bleibt, sie erhaelt die Git-Historie pro
These), sondern zuerst die 11 "exploratorischen" `backtest_*.py`-Skripte (siehe
`algo/README.md`) auf Korrektheit pruefen und echte Code-Duplikation entfernen — als Fundament
fuer die spaetere Oberflaeche. Dem Nutzer geht es primaer um Richtigkeit, die Oberflaeche ist
nachrangig (Phase 2).

**Scope:** `backtest_daily_patterns.py`, `backtest_fred_events.py`, `backtest_fvg_specialness.py`,
`backtest_midnight_range_judas.py`, `backtest_midnight_range_std.py`, `backtest_ndog.py`,
`backtest_nwog.py`, `backtest_ohlc.py`, `backtest_org_ce.py`, `backtest_seasonal.py`,
`backtest_tgif.py`. `backtest_bt.py`/`backtest_ensemble.py`/`backtest_walkforward.py` bleiben
aussen vor — die haben den P&L-Praezisions-Audit vom 2026-08-06/07 bereits hinter sich
(`2026-08-06-algo-backtest-precision-audit-design.md`), andere Baustelle (Punktwert/Commission),
nicht Duplikation.

**Nicht Teil dieses Designs:** die TUI selbst (Phase 2), neue Strategien.

## Befund beim Durchlesen

Konkreter Duplikations-Fund (nicht nur vermutet): `pearson()` (Pearson-Korrelation) ist
**identisch in 4 Dateien dupliziert** (`backtest_ndog.py`, `backtest_nwog.py`,
`backtest_daily_patterns.py`, `explore_patterns.py`) — `scipy` ist ueber `scikit-learn`
(bereits in `algo/requirements.txt`) laengst installiert, kein Grund fuer eine Eigenimplementierung.

`load_rows()` (laedt 1d-Bars) lebt in `backtest_seasonal.py`, wird aber von mindestens 6 anderen
Skripten importiert, nur um diese eine Funktion zu bekommen — eine Stat-Datei fungiert dadurch
ungewollt als Bibliotheksmodul fuer andere Stat-Dateien.

Kein Skript gibt sein Ergebnis strukturiert zurueck — jedes `main()` laedt, rechnet und druckt
in einem Rutsch. Das macht die Skripte weder programmatisch aufrufbar (Voraussetzung fuer Phase 2)
noch existiert der in `algo/PLAN.md` seit 2026-08-03 offene Backlog-Punkt "Backtest-Ergebnisse
als Datenartefakt, nicht nur als Konsolenausgabe".

## Design

### 1. `algo/backtest_common.py` (neu)

```python
def pearson(xs: list[float], ys: list[float]) -> float | None:
    """Duenner Wrapper um scipy.stats.pearsonr, gleiche Signatur/None-Fall wie bisher
    (n<3 oder Nullvarianz -> None statt Exception)."""

def load_rows(symbol: str = "MNQ") -> list[dict]:
    """Verschoben aus backtest_seasonal.py (unveraendert), da 6+ Dateien es importieren."""

def write_result(name: str, data: dict) -> None:
    """Schreibt algo/results/<name>.json (Zeitstempel + data), legt algo/results/ bei Bedarf an."""
```

Die vier Duplikate von `pearson()` werden geloescht, `backtest_seasonal.py` importiert
`load_rows` kuenftig selbst aus `backtest_common.py` statt es zu definieren (Re-Export vermeiden,
alle Importe zeigen direkt auf `backtest_common`).

### 2. Pro Skript: `run()`/`main()`-Trennung

Jedes der 11 Skripte bekommt statt einem monolithischen `main()`:

```python
def run(symbol: str = "MNQ") -> dict:
    """Reine Berechnung, keine Konsolenausgabe. Gibt das Ergebnis-Dict zurueck
    (dieselben Werte, die main() bisher gedruckt hat)."""

def main() -> None:
    result = run()
    ...  # bestehende print()-Ausgabe, unveraendert im Wortlaut
    write_result("<script_name>", result)
```

CLI-Aufruf (`python algo/backtest_tgif.py`) bleibt identisch in Verhalten und Ausgabe — einziger
sichtbarer Unterschied ist die zusaetzliche `algo/results/<name>.json`-Datei. Symbol-Parameter
nur wo ein Skript bereits nicht MNQ-hartkodiert ist (die meisten laufen aktuell fix auf MNQ via
`load_rows()`-Default, kein Scope-Wechsel hier).

### 3. Korrektheits-Audit pro Skript

Ueber den bestehenden Lookahead-Check vom 2026-08-06 hinaus (der bleibt bestaetigt), pro Datei
pruefen:

- Doppelzaehlung/Ueberlappung bei Tages-/Wochen-Gruppierung (Vorlage: der bekannte
  `turn_of_month()`-Bug in `backtest_seasonal.py`, ueberlappende `rs[:-1]`/`nrs[3:]`-Slices,
  seit 2026-08-06 dokumentiert, nie gefixt — wird in diesem Pass direkt repariert).
- Off-by-one bei Fenstergrenzen (z.B. `<=` vs. `<` an Session-/Wochenrand).
- Division-durch-Null-Guards vorhanden, wo Stichproben leer sein koennen.
- Stichprobengroesse (`n=`) wird in jeder Ausgabe ehrlich mitgefuehrt, keine stillschweigend
  gefilterten Teilmengen.

Gefundene Bugs werden direkt repariert (keine separate Freigabe-Schleife pro Fund, siehe
CLAUDE.md-Standard), Ergebnis am Ende gesammelt berichtet.

### 4. `algo/results/*.json`

Neu, **versioniert** (kein `.gitignore`-Eintrag) — analog `algo/seasonal_tendency.json`, da es
genau der seit 2026-08-03 offene PLAN.md-Backlog-Punkt 4 ist ("Backtest-Ergebnisse als
Datenartefakt"). Eine Datei pro Skript, ueberschrieben bei jedem Lauf (kein Verlauf, das leistet
weiterhin `PLAN.md`s Log).

### 5. Test

`algo/selfcheck.py` bekommt einen neuen Check (`dedup` oder in bestehenden Check integriert):
ruft `run()` fuer alle 11 Skripte auf, prueft `isinstance(result, dict)` und dass
`algo/results/<name>.json` danach existiert und gueltiges JSON ist. Kein Zahlen-Assert (die
inhaltlichen Ergebnisse aendern sich mit wachsenden Daten) — reiner Schnittstellen-Regressionscheck,
damit ein spaeterer Phase-2-TUI-Aufruf von `run()` nicht auf einer kaputten Schnittstelle aufbaut.

## Deliverables

- `algo/backtest_common.py` (neu), 4x `pearson()`-Duplikat geloescht, `load_rows()` verschoben.
- 11 Skripte: `run()`/`main()`-Trennung + gefundene Bugs direkt gefixt.
- `algo/results/` (neu, versioniert).
- `algo/selfcheck.py`: neuer Schnittstellen-Check.
- `algo/README.md`: betroffene Abschnitte aktualisiert (neue `run()`-Signatur, `backtest_common.py`
  ergaenzt, `algo/results/` erwaehnt).
- `algo/PLAN.md`-Log-Eintrag: gefundene/gefixte Bugs, Backlog-Punkt 4 als erledigt markiert.

## Fehlerbehandlung

Wo ein Bugfix ein bisher berichtetes Ergebnis inhaltlich aendert (z.B. `turn_of_month()`s
`rest.n`-Korrektur), wird die betroffene `wiki/synthesis/*.md`-Seite direkt mit aktualisiert
(laufende Seite, kein Schnappschuss) und im PLAN.md-Log explizit als Korrektur vermerkt — analog
zur bewussten Ausnahme "eigene Backtest-Funde werden korrigiert, nicht nur markiert" aus
`CLAUDE.md`.
