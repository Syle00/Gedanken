# Backtest-Skript-Entduplizierung & Audit — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Die 11 exploratorischen `algo/backtest_*.py`-Skripte bekommen eine `run()`/`main()`-Trennung, ein gemeinsames `algo/backtest_common.py` ersetzt vierfach duplizierten Code, ein gefundener Statistik-Bug wird gefixt, und jedes Skript schreibt sein Ergebnis nach `algo/results/<name>.json`.

**Architecture:** Neues `algo/backtest_common.py` buendelt `find_1d_days()`, `load_rows()`, `pearson()`, `write_result()` (bisher: `pearson()` 4x dupliziert, `load_rows()`/`find_1d_days()` nur ueber Seiteneingaenge in Stat-Skripten importierbar). Jedes Zielskript bekommt `run() -> dict` (reine Berechnung) + duennes `main()` (druckt wie bisher, ruft `write_result()`). Datei-pro-These-Konvention bleibt erhalten, keine Zusammenlegung.

**Tech Stack:** Python-Stdlib + `scipy` (bereits ueber `scikit-learn` in `algo/requirements.txt` installiert) fuer `pearson()`.

## Global Constraints

- Spec: `docs/superpowers/specs/2026-08-07-algo-backtest-dedup-audit-design.md`.
- Scope: genau die 11 Dateien `backtest_daily_patterns.py`, `backtest_fred_events.py`, `backtest_fvg_specialness.py`, `backtest_midnight_range_judas.py`, `backtest_midnight_range_std.py`, `backtest_ndog.py`, `backtest_nwog.py`, `backtest_ohlc.py`, `backtest_org_ce.py`, `backtest_seasonal.py`, `backtest_tgif.py` plus `explore_patterns.py` (nur `pearson()`-Dedup, kein `run()`-Umbau). `backtest_bt.py`/`backtest_ensemble.py`/`backtest_walkforward.py` bleiben unangetastet.
- CLI-Verhalten und Konsolenausgabe jedes Skripts muessen nach dem Umbau **byte-identisch** bleiben (Ausnahme: `backtest_seasonal.py`, dort aendert der Bugfix in `turn_of_month()` die `rest`-Zahlen bewusst).
- `algo/results/*.json` ist **versioniert** (kein `.gitignore`-Eintrag), außer `backtest_seasonal.py` — das schreibt weiterhin nur `algo/seasonal_tendency.json`, kein zusaetzliches `algo/results/backtest_seasonal.json` (Redundanzvermeidung, siehe Spec).
- Jede Verifikation nutzt dasselbe Baseline-Diff-Muster wie der `backtest_walkforward.py`-Refactor vom 2026-08-05 (PLAN.md-Log): Skript vor und nach der Aenderung laufen lassen, Konsolenausgabe byte-vergleichen.
- Am Ende: `algo/PLAN.md`-Log-Eintrag mit allen gefundenen/behobenen Punkten (siehe Task 15).

---

### Task 1: `algo/backtest_common.py` (neu)

**Files:**
- Create: `algo/backtest_common.py`

**Interfaces:**
- Produces: `find_1d_days(symbol: str = "MNQ") -> list[tuple[date, Path]]`, `load_rows(symbol: str = "MNQ") -> list[dict]`, `pearson(xs: list[float], ys: list[float]) -> float | None`, `write_result(name: str, data: dict) -> None`, `RESULTS_DIR: Path`.

- [ ] **Step 1: Datei schreiben**

```python
#!/usr/bin/env python3
"""Gemeinsame Helfer fuer die algo/backtest_*.py-Explorationsskripte: Datenladen,
Korrelation, Ergebnis-Artefakt. Verhindert, dass Stat-Skripte sich gegenseitig nur wegen
einer Funktion importieren -- vorher: pearson() 4x identisch dupliziert
(backtest_ndog.py, backtest_nwog.py, backtest_daily_patterns.py, explore_patterns.py),
find_1d_days()/load_rows() nur ueber Seiteneingaenge zwischen Stat-Skripten importierbar
(siehe docs/superpowers/specs/2026-08-07-algo-backtest-dedup-audit-design.md).

Aufruf (Selbstcheck):
    python algo/backtest_common.py
"""
from __future__ import annotations

import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

from scipy.stats import pearsonr  # noqa: E402 -- scipy via scikit-learn, siehe requirements.txt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from analyze_ohlc import load  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "raw" / "marktdaten"
RESULTS_DIR = Path(__file__).resolve().parent / "results"


def find_1d_days(symbol: str = "MNQ") -> list[tuple[date, Path]]:
    """(Handelstag, Pfad zur 1d-Datei) fuer jeden Tagesordner mit `symbol`-1d-Daten.
    Verschoben aus backtest_daily_patterns.py (2026-08-07)."""
    out = []
    for day_dir in sorted(DATA_DIR.glob("*/*/*")):
        if not day_dir.is_dir():
            continue
        try:
            day = datetime.strptime(day_dir.name, "%d.%m.%Y").date()
        except ValueError:
            continue
        files = sorted(day_dir.glob(f"{symbol} * 1d.csv"))
        if files:
            out.append((day, files[0]))
    return sorted(out)


def load_rows(symbol: str = "MNQ") -> list[dict]:
    """Verschoben aus backtest_seasonal.py (2026-08-07), unveraendert. Ein dict pro
    Handelstag mit open/close/high/low/range/ret_pct/bullish."""
    rows = []
    for day, path in find_1d_days(symbol):
        bars = load(path)
        if not bars:
            continue
        b = bars[-1]
        if b.h <= b.l:
            continue
        rows.append({"day": day, "open": b.o, "close": b.c, "high": b.h, "low": b.l,
                      "range": b.h - b.l, "ret_pct": 100 * (b.c - b.o) / b.o,
                      "bullish": b.c > b.o})
    rows.sort(key=lambda r: r["day"])
    return rows


def pearson(xs: list[float], ys: list[float]) -> float | None:
    """Verschoben aus backtest_ndog.py/backtest_nwog.py/backtest_daily_patterns.py/
    explore_patterns.py (2026-08-07, war 4x identisch dupliziert). None bei n<3 oder
    Nullvarianz -- gleiches Verhalten wie die alte manuelle Implementierung."""
    if len(xs) < 3:
        return None
    r, _ = pearsonr(xs, ys)
    return r if r == r else None  # r!=r <=> NaN (Nullvarianz)


def write_result(name: str, data: dict) -> None:
    """Schreibt algo/results/<name>.json (Zeitstempel + data). `default=str` deckt
    date/datetime-Werte in den Ergebnis-dicts ab, ohne dass jedes Skript sie selbst
    serialisieren muss."""
    RESULTS_DIR.mkdir(exist_ok=True)
    payload = {"generated_at": datetime.now(timezone.utc).isoformat(), **data}
    (RESULTS_DIR / f"{name}.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, default=str), encoding="utf-8")


def demo() -> None:
    assert pearson([1, 2], [1, 2]) is None, "n<3 muss None liefern"
    r = pearson([1, 2, 3], [1, 2, 3])
    assert r is not None and abs(r - 1.0) < 1e-9, "perfekte Korrelation muss 1.0 sein"
    assert pearson([1, 1, 1], [1, 2, 3]) is None, "Nullvarianz muss None liefern (nicht NaN)"

    import tempfile
    global RESULTS_DIR
    orig = RESULTS_DIR
    with tempfile.TemporaryDirectory() as tmp:
        RESULTS_DIR = Path(tmp)
        write_result("demo_check", {"x": 1, "day": date(2026, 1, 1)})
        payload = json.loads((RESULTS_DIR / "demo_check.json").read_text(encoding="utf-8"))
        assert payload["x"] == 1 and payload["day"] == "2026-01-01" and "generated_at" in payload
    RESULTS_DIR = orig
    print("backtest_common.demo: OK")


if __name__ == "__main__":
    demo()
```

- [ ] **Step 2: Selbstcheck laufen lassen**

Run: `python algo/backtest_common.py`
Expected: `backtest_common.demo: OK`

- [ ] **Step 3: Commit**

```bash
git add algo/backtest_common.py
git commit -m "$(cat <<'EOF'
feat(algo): backtest_common.py -- geteilte Helfer fuer die Explorationsskripte

find_1d_days()/load_rows()/pearson() gebuendelt (vorher: pearson() 4x dupliziert),
neu write_result() fuer das Backtest-Ergebnis-Artefakt (algo/PLAN.md Backlog-Punkt 4).

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_015ynwbhsEzjykXFsjuKRhsK
EOF
)"
```

---

### Task 2: `algo/backtest_daily_patterns.py` entduplizieren + `run()`

**Files:**
- Modify: `algo/backtest_daily_patterns.py` (komplett, 105 Zeilen)

**Interfaces:**
- Consumes: `backtest_common.find_1d_days`, `backtest_common.pearson`, `backtest_common.write_result`.
- Produces: `run() -> dict` mit Keys `n_days, date_range, weekday, range_autocorr, range_autocorr_n, after_bull_pct, after_bull_n, after_bear_pct, after_bear_n, round_number_avg_dist, round_number_n`.

- [ ] **Step 1: Baseline sichern**

Run: `python algo/backtest_daily_patterns.py > algo/_baseline.txt 2>&1`

- [ ] **Step 2: Datei ersetzen**

Ersetze den kompletten Inhalt von `algo/backtest_daily_patterns.py` (ab `from __future__ import annotations` bis Dateiende) durch:

```python
from __future__ import annotations

import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from backtest_common import find_1d_days, pearson, write_result  # noqa: E402
from analyze_ohlc import load  # noqa: E402

WEEKDAY_NAMES = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]


def run() -> dict:
    rows = []
    for day, path in find_1d_days():
        bars = load(path)
        if not bars:
            continue
        b = bars[-1]
        if b.h <= b.l:
            continue
        rows.append({"day": day, "weekday": day.weekday(), "open": b.o, "close": b.c,
                      "high": b.h, "low": b.l, "range": b.h - b.l, "bullish": b.c > b.o})
    rows.sort(key=lambda r: r["day"])
    assert all(rows[i]["day"] < rows[i + 1]["day"] for i in range(len(rows) - 1))

    by_wd: dict[int, list[dict]] = {}
    for r in rows:
        by_wd.setdefault(r["weekday"], []).append(r)
    weekday = {WEEKDAY_NAMES[wd]: {
        "n": len(rs), "median_range": round(statistics.median(r["range"] for r in rs), 2),
        "bullish_pct": round(100 * sum(r["bullish"] for r in rs) / len(rs), 1),
    } for wd, rs in sorted(by_wd.items())}

    ranges = [r["range"] for r in rows]
    range_autocorr = pearson(ranges[:-1], ranges[1:])

    pairs = list(zip(rows[:-1], rows[1:]))
    after_bull = [p[1]["bullish"] for p in pairs if p[0]["bullish"]]
    after_bear = [p[1]["bullish"] for p in pairs if not p[0]["bullish"]]

    dists = []
    for r in rows:
        for level in (r["high"], r["low"]):
            m = level % 50
            dists.append(min(m, 50 - m))

    return {
        "n_days": len(rows), "date_range": [rows[0]["day"], rows[-1]["day"]],
        "weekday": weekday, "range_autocorr": range_autocorr, "range_autocorr_n": len(ranges) - 1,
        "after_bull_pct": 100 * sum(after_bull) / len(after_bull), "after_bull_n": len(after_bull),
        "after_bear_pct": 100 * sum(after_bear) / len(after_bear), "after_bear_n": len(after_bear),
        "round_number_avg_dist": statistics.mean(dists), "round_number_n": len(dists),
    }


def main() -> None:
    result = run()
    print(f"{result['n_days']} Handelstage mit 1d-Daten ({result['date_range'][0]} bis "
          f"{result['date_range'][1]}).\n")

    print("-- 1. Wochentag-Effekt (volle Globex-Session) --")
    for name, s in result["weekday"].items():
        print(f"  {name}: n={s['n']:>3}  Median-Range={s['median_range']:>7.2f}  "
              f"Bullish%={s['bullish_pct']:>5.1f}")

    print("\n-- 2. Range-Autokorrelation (Tag[i] vs. Tag[i-1]) --")
    r_corr = result["range_autocorr"]
    print(f"  Pearson r = {r_corr:.3f}  (n={result['range_autocorr_n']})"
          if r_corr is not None else "  n/a")

    print("\n-- 3. Richtungs-Autokorrelation --")
    print(f"  Nach bullishem Tag: {result['after_bull_pct']:.1f}% bullish "
          f"am naechsten Tag (n={result['after_bull_n']})")
    print(f"  Nach bearishem Tag: {result['after_bear_pct']:.1f}% bullish "
          f"am naechsten Tag (n={result['after_bear_n']})")

    print("\n-- 4. Rundzahl-Magnetismus (Abstand High/Low zur naechsten 50er-Marke) --")
    print(f"  Durchschnittsabstand: {result['round_number_avg_dist']:.2f} Punkte "
          f"(Erwartung bei Gleichverteilung: 12,5 Punkte, n={result['round_number_n']})")

    write_result("backtest_daily_patterns", result)


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Nach-Lauf + Diff**

Run: `python algo/backtest_daily_patterns.py > algo/_after.txt 2>&1 && diff algo/_baseline.txt algo/_after.txt`
Expected: keine Ausgabe (identisch)

- [ ] **Step 4: JSON-Artefakt pruefen**

Run: `python -c "import json; json.load(open('algo/results/backtest_daily_patterns.json', encoding='utf-8'))" && echo OK`
Expected: `OK`

- [ ] **Step 5: Aufraeumen + Commit**

```bash
rm algo/_baseline.txt algo/_after.txt
git add algo/backtest_daily_patterns.py
git commit -m "$(cat <<'EOF'
refactor(algo): backtest_daily_patterns.py -- run()/main()-Trennung, common-Import

find_1d_days()/pearson() kommen jetzt aus backtest_common.py statt eigener Definition.
Konsolenausgabe unveraendert (Diff-verifiziert), neu: algo/results/backtest_daily_patterns.json.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_015ynwbhsEzjykXFsjuKRhsK
EOF
)"
```

---

### Task 3: `algo/backtest_seasonal.py` entduplizieren + `run()` + `turn_of_month()`-Bugfix

**Files:**
- Modify: `algo/backtest_seasonal.py` (komplett, 156 Zeilen)

**Interfaces:**
- Consumes: `backtest_common.find_1d_days`, `backtest_common.load_rows`.
- Produces: `run() -> dict` mit Keys `n_days, date_range, weekday, month, turn_of_month, week_of_month`. **Kein** `write_result()`-Aufruf (eigenes `seasonal_tendency.json` bleibt der Artefakt-Pfad).

**Bugfix:** `turn_of_month()` zaehlte Tage doppelt: `rest_of_month` akkumulierte pro Monat sowohl `rs[:-1]` (Tage des aktuellen Monats) als auch `nrs[3:]` (Tage des Folgemonats ab Tag 4) -- fuer Tage 4..n-1 jedes Monats geschah das zweimal (einmal als `rs[:-1]` der eigenen Iteration, einmal als `nrs[3:]` der Vor-Iteration). Der bestehende `tom_days`-Filter entfernte nur die Ueberschneidung zwischen `tom` und `rest`, nicht die Selbstdopplung innerhalb `rest`. Seit 2026-08-06 in `algo/PLAN.md` dokumentiert, nie behoben. Fix: `rest` wird direkt als Komplement von `tom_days` ueber `rows` berechnet, keine inkrementelle Akkumulation mehr.

- [ ] **Step 1: Baseline sichern**

Run: `python algo/backtest_seasonal.py > algo/_baseline.txt 2>&1`

- [ ] **Step 2: Datei ersetzen**

Ersetze den kompletten Inhalt von `algo/backtest_seasonal.py` (ab `from __future__ import annotations` bis Dateiende) durch:

```python
from __future__ import annotations

import json
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from backtest_common import load_rows  # noqa: E402

MONTH_NAMES = ["", "Jan", "Feb", "Mrz", "Apr", "Mai", "Jun", "Jul", "Aug",
               "Sep", "Okt", "Nov", "Dez"]
WEEKDAY_NAMES = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
OUT_PATH = Path(__file__).resolve().parent / "seasonal_tendency.json"


def trading_days_of_month(rows: list[dict], year: int, month: int) -> list[dict]:
    return [r for r in rows if r["day"].year == year and r["day"].month == month]


def group_stats(rs: list[dict]) -> dict:
    return {
        "n": len(rs),
        "bullish_pct": round(100 * sum(r["bullish"] for r in rs) / len(rs), 1),
        "avg_return_pct": round(statistics.mean(r["ret_pct"] for r in rs), 3),
        "median_range": round(statistics.median(r["range"] for r in rs), 2),
        "avg_range": round(statistics.mean(r["range"] for r in rs), 2),
    }


def weekday_table(rows: list[dict]) -> dict:
    by_wd: dict[int, list[dict]] = {}
    for r in rows:
        by_wd.setdefault(r["day"].weekday(), []).append(r)
    return {WEEKDAY_NAMES[wd]: group_stats(rs) for wd, rs in sorted(by_wd.items())}


def month_table(rows: list[dict]) -> dict:
    months = sorted({(r["day"].year, r["day"].month) for r in rows})
    out = {}
    for y, m in months:
        rs = trading_days_of_month(rows, y, m)
        out[f"{y}-{m:02d}"] = group_stats(rs)
    return out


def turn_of_month(rows: list[dict]) -> dict:
    months = sorted({(r["day"].year, r["day"].month) for r in rows})
    tom = []
    for i, (y, m) in enumerate(months):
        rs = trading_days_of_month(rows, y, m)
        if not rs:
            continue
        tom.append(rs[-1])
        if i + 1 < len(months):
            ny, nm = months[i + 1]
            nrs = trading_days_of_month(rows, ny, nm)
            tom.extend(nrs[:3])
    # Bugfix 2026-08-07 (siehe algo/PLAN.md-Log): rest = alles ausserhalb des TOM-Fensters,
    # direkt aus rows berechnet statt inkrementell akkumuliert -- die alte rest_of_month-
    # Akkumulation zaehlte Tage 4..n-1 jedes Monats doppelt (rs[:-1] der eigenen Iteration
    # UND nrs[3:] der Vor-Iteration ueberschnitten sich), der tom_days-Filter danach entfernte
    # nur die TOM/rest-Ueberschneidung, nicht die rest/rest-Selbstdopplung.
    tom_days = {r["day"] for r in tom}
    rest = [r for r in rows if r["day"] not in tom_days]
    return {"window": group_stats(tom), "rest": group_stats(rest)}


def week_of_month_table(rows: list[dict]) -> dict:
    by_week: dict[int, list[dict]] = {}
    for r in rows:
        wk = min((r["day"].day - 1) // 7 + 1, 5)
        by_week.setdefault(wk, []).append(r)
    return {str(wk): group_stats(rs) for wk, rs in sorted(by_week.items())}


def run() -> dict:
    rows = load_rows()
    return {
        "n_days": len(rows), "date_range": [rows[0]["day"], rows[-1]["day"]],
        "weekday": weekday_table(rows), "month": month_table(rows),
        "turn_of_month": turn_of_month(rows), "week_of_month": week_of_month_table(rows),
    }


def main() -> None:
    result = run()
    rng = result["date_range"]
    print(f"{result['n_days']} Handelstage ({rng[0]} bis {rng[1]}).\n")

    print("-- Wochentag --")
    for name, s in result["weekday"].items():
        print(f"  {name}: n={s['n']:>3}  Bullish%={s['bullish_pct']:>5.1f}  "
              f"Median-Range={s['median_range']:>7.2f}")

    print("\n-- Monat (Rohbefund, n=1 Jahr -- kein Mehrjahres-Seasonality-Test) --")
    for key, s in result["month"].items():
        y, m = key.split("-")
        print(f"  {MONTH_NAMES[int(m)]} {y}: n={s['n']:>2}  Bullish%={s['bullish_pct']:>5.1f}  "
              f"Tagesrendite(Avg)={s['avg_return_pct']:>+.2f}%")

    tom = result["turn_of_month"]
    print("\n-- Turn-of-Month (letzter Handelstag + erste 3 des Folgemonats) --")
    print(f"  Fenster (n={tom['window']['n']}): Tagesrendite(Avg) "
          f"{tom['window']['avg_return_pct']:+.3f}%, Bullish% {tom['window']['bullish_pct']}, "
          f"Range(Avg) {tom['window']['avg_range']}")
    print(f"  Rest    (n={tom['rest']['n']}): Tagesrendite(Avg) "
          f"{tom['rest']['avg_return_pct']:+.3f}%, Bullish% {tom['rest']['bullish_pct']}, "
          f"Range(Avg) {tom['rest']['avg_range']}")

    print("\n-- Woche-im-Monat (1=Tage 1-7, 2=8-14, 3=15-21, 4=22-28, 5=29-31) --")
    for wk, s in result["week_of_month"].items():
        print(f"  Woche {wk}: n={s['n']:>3}  Bullish%={s['bullish_pct']:>5.1f}  "
              f"Median-Range={s['median_range']:>7.2f}")

    db = {"generated_at": datetime.now(timezone.utc).isoformat(), **result}
    OUT_PATH.write_text(json.dumps(db, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"\nDatenbank geschrieben: {OUT_PATH.relative_to(OUT_PATH.parent.parent)}")


if __name__ == "__main__":
    main()
```

`backtest_nwog.py` importiert weiterhin `WEEKDAY_NAMES` aus diesem Modul (unveraendert, bleibt
hier definiert) -- `load_rows`/`find_1d_days` werden nur noch aus `backtest_common.py` bezogen.

- [ ] **Step 3: Nach-Lauf + Diff**

Run: `python algo/backtest_seasonal.py > algo/_after.txt 2>&1 && diff algo/_baseline.txt algo/_after.txt`
Expected: Diff zeigt **nur** die `Rest`-Zeile der Turn-of-Month-Sektion mit veraendertem `n`/Prozentwert (Bugfix), sonst identisch. Wenn mehr abweicht: Fehler, nicht committen.

- [ ] **Step 4: `wiki/synthesis/Seasonal Tendency (Eigene Daten, laufend).md` aktualisieren**

Die alten `rest`-Zahlen (vor dem Fix) in dieser Wiki-Seite mit den neuen aus `algo/_after.txt` ersetzen, plus ein `> ✅ Korrektur (2026-08-07): ...`-Hinweis analog der CLAUDE.md-Konvention fuer korrigierte eigene Backtest-Funde.

- [ ] **Step 5: Aufraeumen + Commit**

```bash
rm algo/_baseline.txt algo/_after.txt
git add algo/backtest_seasonal.py "wiki/synthesis/Seasonal Tendency (Eigene Daten, laufend).md"
git commit -m "$(cat <<'EOF'
fix(algo): turn_of_month() Doppelzaehlungs-Bug behoben, run()/main()-Trennung

rest wird jetzt direkt als Komplement von tom_days ueber rows berechnet statt
inkrementell akkumuliert -- die alte Logik zaehlte Tage 4..n-1 jedes Monats doppelt.
Seit 2026-08-06 dokumentiert (PLAN.md), jetzt tatsaechlich gefixt. Wiki-Seite mit
korrigierten Zahlen aktualisiert.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_015ynwbhsEzjykXFsjuKRhsK
EOF
)"
```

---

### Task 4: `algo/backtest_nwog.py` entduplizieren + `run()`

**Files:**
- Modify: `algo/backtest_nwog.py` (komplett, 107 Zeilen)

**Interfaces:**
- Consumes: `backtest_common.load_rows`, `backtest_common.pearson`, `backtest_common.write_result`, `backtest_seasonal.WEEKDAY_NAMES`.
- Produces: `group_weeks(rows) -> list[list[dict]]` (unveraendert, wird von `backtest_tgif.py`/`backtest_fred_events.py` importiert), `run() -> dict`.

- [ ] **Step 1: Baseline sichern**

Run: `python algo/backtest_nwog.py > algo/_baseline.txt 2>&1`

- [ ] **Step 2: Datei ersetzen**

```python
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from backtest_common import load_rows, pearson, write_result  # noqa: E402
from backtest_seasonal import WEEKDAY_NAMES  # noqa: E402


def group_weeks(rows: list[dict]) -> list[list[dict]]:
    weeks: list[list[dict]] = []
    for r in rows:
        if r["day"].weekday() == 0 or not weeks:
            weeks.append([r])
        else:
            weeks[-1].append(r)
    return weeks


def run() -> dict:
    rows = load_rows()
    weeks = group_weeks(rows)
    weeks = [w for w in weeks if w[0]["day"].weekday() == 0]

    nwogs = []
    for week in weeks:
        mon = week[0]
        idx = rows.index(mon)
        if idx == 0:
            continue
        prev_close = rows[idx - 1]["close"]
        gap = mon["open"] - prev_close
        week_high = max(r["high"] for r in week)
        week_low = min(r["low"] for r in week)
        week_range = week_high - week_low
        touched = any(r["low"] <= prev_close <= r["high"] for r in week)
        touched_after_monday = any(r["low"] <= prev_close <= r["high"] for r in week[1:])
        week_ret = week[-1]["close"] - mon["open"]
        high_day = next(r for r in week if r["high"] == week_high)["day"].weekday()
        low_day = next(r for r in week if r["low"] == week_low)["day"].weekday()
        nwogs.append({"week_start": mon["day"], "gap": gap, "range": week_range,
                      "touched": touched, "touched_after_monday": touched_after_monday,
                      "week_ret": week_ret, "high_day": high_day, "low_day": low_day})

    abs_gaps = [abs(n["gap"]) for n in nwogs]
    ranges = [n["range"] for n in nwogs]
    corr = pearson(abs_gaps, ranges)

    intact = sum(1 for n in nwogs if not n["touched"])
    intact_after_mon = sum(1 for n in nwogs if not n["touched_after_monday"])
    same_dir = sum(1 for n in nwogs if (n["gap"] > 0) == (n["week_ret"] > 0))
    high_days = Counter(n["high_day"] for n in nwogs)
    low_days = Counter(n["low_day"] for n in nwogs)

    return {
        "n_weeks": len(nwogs), "gap_range_corr": corr,
        "intact_pct": 100 * intact / len(nwogs), "intact_n": intact,
        "intact_after_monday_pct": 100 * intact_after_mon / len(nwogs),
        "intact_after_monday_n": intact_after_mon,
        "same_dir_pct": 100 * same_dir / len(nwogs), "same_dir_n": same_dir,
        "high_day_counts": {WEEKDAY_NAMES[wd]: high_days.get(wd, 0) for wd in range(5)},
        "low_day_counts": {WEEKDAY_NAMES[wd]: low_days.get(wd, 0) for wd in range(5)},
    }


def main() -> None:
    result = run()
    n = result["n_weeks"]
    print(f"{n} Wochen mit NWOG-Daten.\n")

    corr = result["gap_range_corr"]
    print(f"1. Korrelation |NWOG-Gap| vs. Wochenrange: r={corr:.3f} (n={n})")

    print(f"\n2. Bias-intakt-Quote (NWOG intraweek NICHT wieder erreicht, Mo-Fr): "
          f"{result['intact_n']}/{n} = {result['intact_pct']:.1f}%")
    print(f"   ... davon nur Montags eigene Kerze beruehrt, Di-Fr NICHT mehr: "
          f"{result['intact_after_monday_n']}/{n} = {result['intact_after_monday_pct']:.1f}% "
          f"(Bias haelt ab Dienstag)")

    print(f"\n3. Gap-Richtung = Wochenrichtung (Fortsetzung statt Fade): "
          f"{result['same_dir_n']}/{n} = {result['same_dir_pct']:.1f}%")

    print("\n4. Wochentag des Wochen-Highs / -Lows:")
    for wd in range(5):
        wd_name = WEEKDAY_NAMES[wd]
        h, low = result["high_day_counts"][wd_name], result["low_day_counts"][wd_name]
        print(f"   {wd_name}: High {h:>3} ({100 * h / n:.1f}%)   "
              f"Low {low:>3} ({100 * low / n:.1f}%)")

    write_result("backtest_nwog", result)


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Nach-Lauf + Diff**

Run: `python algo/backtest_nwog.py > algo/_after.txt 2>&1 && diff algo/_baseline.txt algo/_after.txt`
Expected: keine Ausgabe (identisch)

- [ ] **Step 4: JSON-Artefakt pruefen**

Run: `python -c "import json; json.load(open('algo/results/backtest_nwog.json', encoding='utf-8'))" && echo OK`
Expected: `OK`

- [ ] **Step 5: Aufraeumen + Commit**

```bash
rm algo/_baseline.txt algo/_after.txt
git add algo/backtest_nwog.py
git commit -m "$(cat <<'EOF'
refactor(algo): backtest_nwog.py -- run()/main()-Trennung, common-Import

load_rows()/pearson() kommen jetzt aus backtest_common.py. Konsolenausgabe
unveraendert (Diff-verifiziert), neu: algo/results/backtest_nwog.json.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_015ynwbhsEzjykXFsjuKRhsK
EOF
)"
```

---

### Task 5: `algo/backtest_tgif.py` entduplizieren + `run()`

**Files:**
- Modify: `algo/backtest_tgif.py` (komplett, 80 Zeilen)

**Interfaces:**
- Consumes: `backtest_common.load_rows`, `backtest_common.write_result`, `backtest_nwog.group_weeks`.
- Produces: `run() -> dict`.

- [ ] **Step 1: Baseline sichern**

Run: `python algo/backtest_tgif.py > algo/_baseline.txt 2>&1`

- [ ] **Step 2: Datei ersetzen**

```python
from __future__ import annotations

import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from backtest_common import load_rows, write_result  # noqa: E402
from backtest_nwog import group_weeks  # noqa: E402


def run() -> dict:
    rows = load_rows()
    weeks_raw = group_weeks(rows)
    weeks = [w for w in weeks_raw if w[0]["day"].weekday() == 0 and len(w) >= 3]

    results = []
    for w in weeks:
        week_open = w[0]["open"]
        pre_last_close = w[-2]["close"]
        last = w[-1]
        week_high = max(r["high"] for r in w)
        week_low = min(r["low"] for r in w)
        rng = week_high - week_low
        if rng <= 0:
            continue
        bullish = pre_last_close > week_open
        if bullish:
            retrace_pct = 100 * (week_high - last["close"]) / rng
        else:
            retrace_pct = 100 * (last["close"] - week_low) / rng
        results.append({"week_start": w[0]["day"], "bullish": bullish,
                         "retrace_pct": retrace_pct, "in_zone": 20 <= retrace_pct <= 30})

    hits = sum(1 for r in results if r["in_zone"])
    retraces = [r["retrace_pct"] for r in results]
    wide = sum(1 for r in retraces if 15 <= r <= 35)
    buckets = [10, 20, 30, 40, 50, 70, 100]
    bucket_counts = []
    prev = 0
    for b in buckets:
        c = sum(1 for r in retraces if prev <= r < b)
        bucket_counts.append([prev, b, c])
        prev = b

    return {
        "n_weeks": len(results), "hits": hits, "hit_pct": 100 * hits / len(results),
        "median_retrace_pct": statistics.median(retraces),
        "mean_retrace_pct": statistics.mean(retraces), "bucket_counts": bucket_counts,
        "bullish_weeks": sum(1 for r in results if r["bullish"]),
        "wide_hits": wide, "wide_pct": 100 * wide / len(retraces),
    }


def main() -> None:
    result = run()
    n = result["n_weeks"]
    print(f"{n} Wochen mit TGIF-Daten.\n")

    print(f"1. Freitag-Close im 20-30%-Retracement-Fenster: {result['hits']}/{n} = "
          f"{result['hit_pct']:.1f}%")

    print(f"\n2. Verteilung des tatsaechlichen Retracements (Median "
          f"{result['median_retrace_pct']:.1f}%, Mittelwert {result['mean_retrace_pct']:.1f}%):")
    for prev, b, c in result["bucket_counts"]:
        print(f"   {prev:>3}-{b:<3}%: {c:>3}  ({100 * c / n:.1f}%)")

    print(f"\n   Wochen bullish (Montag->vorletzter Tag): {result['bullish_weeks']}/{n}")

    print(f"\n3. Grosszuegigeres Fenster (15-35%, statt exakt 20-30%): "
          f"{result['wide_hits']}/{n} = {result['wide_pct']:.1f}%")

    write_result("backtest_tgif", result)


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Nach-Lauf + Diff**

Run: `python algo/backtest_tgif.py > algo/_after.txt 2>&1 && diff algo/_baseline.txt algo/_after.txt`
Expected: keine Ausgabe (identisch)

- [ ] **Step 4: Aufraeumen + Commit**

```bash
rm algo/_baseline.txt algo/_after.txt
git add algo/backtest_tgif.py
git commit -m "$(cat <<'EOF'
refactor(algo): backtest_tgif.py -- run()/main()-Trennung, common-Import

load_rows() kommt jetzt aus backtest_common.py. Konsolenausgabe unveraendert
(Diff-verifiziert), neu: algo/results/backtest_tgif.json.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_015ynwbhsEzjykXFsjuKRhsK
EOF
)"
```

---

### Task 6: `algo/backtest_ndog.py` entduplizieren + `run()`

**Files:**
- Modify: `algo/backtest_ndog.py` (komplett, 83 Zeilen)

**Interfaces:**
- Consumes: `backtest_common.load_rows`, `backtest_common.pearson`, `backtest_common.write_result`.
- Produces: `run() -> dict`.

- [ ] **Step 1: Baseline sichern**

Run: `python algo/backtest_ndog.py > algo/_baseline.txt 2>&1`

- [ ] **Step 2: Datei ersetzen**

```python
from __future__ import annotations

import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from backtest_common import load_rows, pearson, write_result  # noqa: E402


def run() -> dict:
    rows = load_rows()
    gaps = []
    for i in range(1, len(rows)):
        prev_close, today_open = rows[i - 1]["close"], rows[i]["open"]
        gap = today_open - prev_close
        filled = rows[i]["low"] <= prev_close <= rows[i]["high"]
        gaps.append({"day": rows[i]["day"], "gap": gap, "filled": filled,
                      "range": rows[i]["range"], "day_ret": rows[i]["close"] - rows[i]["open"]})

    abs_gaps = [abs(g["gap"]) for g in gaps]
    ranges = [g["range"] for g in gaps]
    corr = pearson(abs_gaps, ranges)

    filled = sum(1 for g in gaps if g["filled"])
    med_gap = statistics.median(abs_gaps)
    small = [g for g in gaps if abs(g["gap"]) <= med_gap]
    big = [g for g in gaps if abs(g["gap"]) > med_gap]
    same_dir = sum(1 for g in gaps if (g["gap"] > 0) == (g["day_ret"] > 0))

    return {
        "n_days": len(gaps), "gap_range_corr": corr, "fill_pct": 100 * filled / len(gaps),
        "fill_n": filled, "median_abs_gap": med_gap,
        "small_gap_fill_pct": 100 * sum(1 for g in small if g["filled"]) / len(small),
        "small_gap_n": len(small),
        "big_gap_fill_pct": 100 * sum(1 for g in big if g["filled"]) / len(big),
        "big_gap_n": len(big),
        "same_dir_pct": 100 * same_dir / len(gaps), "same_dir_n": same_dir,
    }


def main() -> None:
    result = run()
    n = result["n_days"]
    print(f"{n} Handelstage mit NDOG-Daten.\n")

    print(f"1. Korrelation |NDOG-Gap| vs. Tagesrange: r={result['gap_range_corr']:.3f} (n={n})")

    print(f"\n2. NDOG-Fill-Quote (selber Tag): {result['fill_n']}/{n} = {result['fill_pct']:.1f}%")
    print(f"   Kleine Gaps (<= Median {result['median_abs_gap']:.1f} Pkt.): "
          f"{result['small_gap_fill_pct']:.1f}% (n={result['small_gap_n']})")
    print(f"   Grosse Gaps (> Median {result['median_abs_gap']:.1f} Pkt.): "
          f"{result['big_gap_fill_pct']:.1f}% (n={result['big_gap_n']})")

    print(f"\n3. Gap-Richtung = Tagesrichtung (Fortsetzung statt Fade): "
          f"{result['same_dir_n']}/{n} = {result['same_dir_pct']:.1f}%")

    write_result("backtest_ndog", result)


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Nach-Lauf + Diff**

Run: `python algo/backtest_ndog.py > algo/_after.txt 2>&1 && diff algo/_baseline.txt algo/_after.txt`
Expected: keine Ausgabe (identisch)

- [ ] **Step 4: Aufraeumen + Commit**

```bash
rm algo/_baseline.txt algo/_after.txt
git add algo/backtest_ndog.py
git commit -m "$(cat <<'EOF'
refactor(algo): backtest_ndog.py -- run()/main()-Trennung, common-Import

load_rows()/pearson() kommen jetzt aus backtest_common.py. Konsolenausgabe
unveraendert (Diff-verifiziert), neu: algo/results/backtest_ndog.json.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_015ynwbhsEzjykXFsjuKRhsK
EOF
)"
```

---

### Task 7: `algo/backtest_fred_events.py` entduplizieren + `run()`

**Files:**
- Modify: `algo/backtest_fred_events.py` (komplett, 141 Zeilen)

**Interfaces:**
- Consumes: `backtest_common.load_rows`, `backtest_common.write_result`, `backtest_nwog.group_weeks`.
- Produces: `run() -> dict`.

- [ ] **Step 1: Baseline sichern**

Run: `python algo/backtest_fred_events.py > algo/_baseline.txt 2>&1`

- [ ] **Step 2: Datei ersetzen**

```python
from __future__ import annotations

import csv
import statistics
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from backtest_common import load_rows, write_result  # noqa: E402
from backtest_nwog import group_weeks  # noqa: E402

FRED_DIR = Path(__file__).resolve().parent.parent / "raw" / "marktdaten" / "fred"


def load_fred(series_id: str) -> dict[date, float]:
    out = {}
    with (FRED_DIR / f"{series_id}.csv").open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["value"]:
                out[date.fromisoformat(row["date"])] = float(row["value"])
    return out


def nearest_on_or_before(series: dict[date, float], d: date, lookback: int = 5) -> float | None:
    for i in range(lookback + 1):
        v = series.get(d - timedelta(days=i))
        if v is not None:
            return v
    return None


def run() -> dict:
    rows = load_rows()
    vix = load_fred("VIXCLS")
    dgs10 = load_fred("DGS10")
    walcl = load_fred("WALCL")

    with_vix = [(r, nearest_on_or_before(vix, r["day"])) for r in rows]
    with_vix = [(r, v) for r, v in with_vix if v is not None]
    with_vix.sort(key=lambda t: t[1])
    n = len(with_vix)
    tercile = n // 3
    low, mid, high = with_vix[:tercile], with_vix[tercile:-tercile], with_vix[-tercile:]
    regimes = {}
    for name, bucket in [("niedrig", low), ("mittel", mid), ("hoch", high)]:
        ranges = [r["range"] for r, _ in bucket]
        abs_rets = [abs(r["ret_pct"]) for r, _ in bucket]
        regimes[name] = {
            "n": len(bucket), "vix_range": [bucket[0][1], bucket[-1][1]],
            "median_range": statistics.median(ranges), "avg_abs_ret_pct": statistics.mean(abs_rets),
        }

    vix_delta, mnq_ret = [], []
    prev_vix = None
    for r in rows:
        v = nearest_on_or_before(vix, r["day"])
        if v is not None and prev_vix is not None:
            vix_delta.append(v - prev_vix)
            mnq_ret.append(r["ret_pct"])
        if v is not None:
            prev_vix = v
    corr_vix = statistics.correlation(vix_delta, mnq_ret) if len(vix_delta) >= 2 else None

    dgs_delta, mnq_ret2 = [], []
    prev_dgs = None
    for r in rows:
        v = nearest_on_or_before(dgs10, r["day"])
        if v is not None and prev_dgs is not None:
            dgs_delta.append(v - prev_dgs)
            mnq_ret2.append(r["ret_pct"])
        if v is not None:
            prev_dgs = v
    corr_dgs = statistics.correlation(dgs_delta, mnq_ret2) if len(dgs_delta) >= 2 else None

    weeks = [w for w in group_weeks(rows) if len(w) >= 2]
    grow, shrink = [], []
    prev_walcl = None
    for w in sorted(weeks, key=lambda w: w[0]["day"]):
        v = nearest_on_or_before(walcl, w[0]["day"], lookback=10)
        if v is None:
            continue
        week_ret = 100 * (w[-1]["close"] - w[0]["open"]) / w[0]["open"]
        if prev_walcl is not None:
            (grow if v > prev_walcl else shrink).append(week_ret)
        prev_walcl = v

    return {
        "n_days": len(rows), "vix_regimes": regimes,
        "vix_delta_corr": corr_vix, "vix_delta_n": len(vix_delta),
        "dgs10_delta_corr": corr_dgs, "dgs10_delta_n": len(dgs_delta),
        "walcl_grow_avg_week_ret": statistics.mean(grow) if grow else None, "walcl_grow_n": len(grow),
        "walcl_shrink_avg_week_ret": statistics.mean(shrink) if shrink else None,
        "walcl_shrink_n": len(shrink),
    }


def main() -> None:
    result = run()
    print(f"{result['n_days']} MNQ-Handelstage.\n")

    print("Hinweis: CPI-/FOMC-Reaktionstest bewusst NICHT gebaut -- FRED liefert kein "
          "Release-Datum fuer CPI und im Datenfenster gab es keine FOMC-Zielsatzaenderung "
          "(n=0). Details im Modul-Docstring. Stattdessen VIX/DGS10/WALCL-Zusammenhaenge:\n")

    print("1. VIX-Niveau-Regime (Terzile):")
    for name, s in result["vix_regimes"].items():
        vix_range = f"{s['vix_range'][0]:.1f}-{s['vix_range'][1]:.1f}"
        print(f"   VIX {name:>7} ({vix_range:>11}): n={s['n']:>2}  "
              f"Median-Range={s['median_range']:>7.1f}  Avg|Rendite|={s['avg_abs_ret_pct']:.2f}%")

    if result["vix_delta_corr"] is not None:
        print(f"\n2. VIX-Tagesaenderung vs. MNQ-Tagesrendite: n={result['vix_delta_n']}  "
              f"Korrelation={result['vix_delta_corr']:+.3f}")
    else:
        print("\n2. zu wenig Daten")

    if result["dgs10_delta_corr"] is not None:
        print(f"3. DGS10-Tagesaenderung vs. MNQ-Tagesrendite: n={result['dgs10_delta_n']}  "
              f"Korrelation={result['dgs10_delta_corr']:+.3f}")
    else:
        print("3. zu wenig Daten")

    print("\n4. WALCL-Trend vs. MNQ-Wochenrendite:")
    if result["walcl_grow_avg_week_ret"] is not None:
        print(f"   Bilanz waechst  (n={result['walcl_grow_n']:>2}): "
              f"Avg-Wochenrendite {result['walcl_grow_avg_week_ret']:+.2f}%")
    if result["walcl_shrink_avg_week_ret"] is not None:
        print(f"   Bilanz schrumpft(n={result['walcl_shrink_n']:>2}): "
              f"Avg-Wochenrendite {result['walcl_shrink_avg_week_ret']:+.2f}%")
    if result["walcl_grow_avg_week_ret"] is None or result["walcl_shrink_avg_week_ret"] is None:
        print("   zu wenig Wochen fuer beide Gruppen im aktuellen Fenster")

    write_result("backtest_fred_events", result)


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Nach-Lauf + Diff**

Run: `python algo/backtest_fred_events.py > algo/_after.txt 2>&1 && diff algo/_baseline.txt algo/_after.txt`
Expected: keine Ausgabe (identisch)

- [ ] **Step 4: Aufraeumen + Commit**

```bash
rm algo/_baseline.txt algo/_after.txt
git add algo/backtest_fred_events.py
git commit -m "$(cat <<'EOF'
refactor(algo): backtest_fred_events.py -- run()/main()-Trennung, common-Import

load_rows() kommt jetzt aus backtest_common.py. Konsolenausgabe unveraendert
(Diff-verifiziert), neu: algo/results/backtest_fred_events.json.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_015ynwbhsEzjykXFsjuKRhsK
EOF
)"
```

---

### Task 8: `algo/backtest_org_ce.py` — `run()`

**Files:**
- Modify: `algo/backtest_org_ce.py` (komplett, 88 Zeilen)

**Interfaces:**
- Consumes: `backtest_common.write_result`.
- Produces: `find_days() -> list[tuple]` (unveraendert, wird von `backtest_fvg_specialness.py`, `backtest_midnight_range_std.py`, `backtest_midnight_range_judas.py`, `explore_patterns.py` importiert), `run() -> dict`.

Kein Bug gefunden (Struktur bereits sauber, inkl. Regressionscheck gegen den bekannten 2026-07-23-Wert).

- [ ] **Step 1: Baseline sichern**

Run: `python algo/backtest_org_ce.py > algo/_baseline.txt 2>&1`

- [ ] **Step 2: Datei ersetzen**

```python
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from analyze_ohlc import load, org_gap  # noqa: E402
from backtest_common import write_result  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "raw" / "marktdaten"


def find_days() -> list[tuple]:
    """(Tag, Datei) -- 1m bevorzugt, sonst 5m als naechstbeste Aufloesung."""
    out = []
    for day_dir in sorted(DATA_DIR.glob("*/*/*")):
        if not day_dir.is_dir():
            continue
        try:
            day = datetime.strptime(day_dir.name, "%d.%m.%Y").date()
        except ValueError:
            continue
        for tf in ("1m", "5m"):
            files = [f for f in day_dir.glob(f"* {tf}.csv") if "RTH" not in f.name]
            if files:
                out.append((day, files[0]))
                break
    return sorted(out)


def run() -> dict:
    days = find_days()
    results = []
    for i in range(1, len(days)):
        day, path = days[i]
        _, prev_path = days[i - 1]
        combined = sorted(load(prev_path) + load(path), key=lambda b: b.t)
        r = org_gap(combined, day)
        if r is not None:
            results.append((day, r))

    known = next((r for d, r in results if d.isoformat() == "2026-07-23"), None)
    if known is not None:
        assert abs(known["ce"] - 28984.00) < 0.01, known

    hit = [r for _, r in results if r["filled_30m"]]
    by_min_gap = {}
    for min_gap in (5, 15, 30):
        sub = [r for _, r in results if r["gap"] >= min_gap]
        if sub:
            h = sum(1 for r in sub if r["filled_30m"])
            by_min_gap[min_gap] = {"hit_n": h, "n": len(sub), "hit_pct": 100 * h / len(sub)}

    return {"n_days": len(results),
            "hit_n": len(hit), "hit_pct": 100 * len(hit) / len(results) if results else 0.0,
            "days": results, "by_min_gap": by_min_gap}


def main() -> None:
    result = run()
    results = result["days"]
    if not results:
        print("keine Tage mit vollstaendigen ORG-Daten gefunden")
        return

    print(f"{result['n_days']} Tage mit ORG-Daten, C.E. gefuellt in 9:30-10:00: "
          f"{result['hit_n']}/{result['n_days']} = {result['hit_pct']:.1f}%\n")

    print(f"{'Tag':<12}{'PrevClose':>11}{'Open':>11}{'Gap':>9}{'C.E.':>11}{'Fill':>7}{'Zeit':>8}")
    for day, r in results:
        print(f"{day.isoformat():<12}{r['prev_close']:>11.2f}{r['today_open']:>11.2f}"
              f"{r['gap']:>9.2f}{r['ce']:>11.2f}{'JA' if r['filled_30m'] else 'nein':>7}"
              f"{r['filled_t'].strftime('%H:%M') if r['filled_t'] else '':>8}")

    for min_gap, s in result["by_min_gap"].items():
        print(f"\nNur Gap >= {min_gap} Pkt.: {s['hit_n']}/{s['n']} = {s['hit_pct']:.1f}%")

    write_result("backtest_org_ce", {"n_days": result["n_days"], "hit_n": result["hit_n"],
                                      "hit_pct": result["hit_pct"], "by_min_gap": result["by_min_gap"]})


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Nach-Lauf + Diff**

Run: `python algo/backtest_org_ce.py > algo/_after.txt 2>&1 && diff algo/_baseline.txt algo/_after.txt`
Expected: keine Ausgabe (identisch)

- [ ] **Step 4: Aufraeumen + Commit**

```bash
rm algo/_baseline.txt algo/_after.txt
git add algo/backtest_org_ce.py
git commit -m "$(cat <<'EOF'
refactor(algo): backtest_org_ce.py -- run()/main()-Trennung

Kein Bug gefunden. Konsolenausgabe unveraendert (Diff-verifiziert), neu:
algo/results/backtest_org_ce.json.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_015ynwbhsEzjykXFsjuKRhsK
EOF
)"
```

---

### Task 9: `algo/backtest_fvg_specialness.py` — `run()`

**Files:**
- Modify: `algo/backtest_fvg_specialness.py` (komplett, 95 Zeilen)

**Interfaces:**
- Consumes: `backtest_org_ce.find_days`, `backtest_common.write_result`.
- Produces: `run() -> dict`.

Kein Bug gefunden.

- [ ] **Step 1: Baseline sichern**

Run: `python algo/backtest_fvg_specialness.py > algo/_baseline.txt 2>&1`

- [ ] **Step 2: Datei ersetzen**

```python
from __future__ import annotations

import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from analyze_ohlc import load, fvgs, at  # noqa: E402
from backtest_org_ce import find_days  # noqa: E402
from backtest_common import write_result  # noqa: E402


def classify(day, gaps):
    first_930 = min((g for g in gaps if g["t"] >= at(day, 9, 30)), key=lambda g: g["t"], default=None)
    first_midnight = min((g for g in gaps if g["t"] >= at(day, 0, 0)), key=lambda g: g["t"], default=None)
    by_hour: dict[tuple, dict] = {}
    for g in gaps:
        key = (g["t"].date(), g["t"].hour)
        if key not in by_hour or g["t"] < by_hour[key]["t"]:
            by_hour[key] = g
    return first_930, first_midnight, {id(g) for g in by_hour.values()}


def stats(gaps: list[dict]) -> dict:
    n = len(gaps)
    if n == 0:
        return {"n": 0, "filled": 0.0, "ce_hit": 0.0, "avg_size": 0.0}
    return {
        "n": n,
        "filled": 100 * sum(1 for g in gaps if g["filled"]) / n,
        "ce_hit": 100 * sum(1 for g in gaps if g["ce_hit"]) / n,
        "avg_size": sum(g["size"] for g in gaps) / n,
    }


def run() -> dict:
    groups: dict[str, list[dict]] = {"first_930": [], "first_midnight": [],
                                      "first_of_hour": [], "rest": []}
    days_used = 0
    for day, path in find_days():
        bars = load(path)
        gaps = fvgs(bars)
        gaps = [g for g in gaps if g["t"].date() in {day, day - timedelta(days=1)}]
        if not gaps:
            continue
        days_used += 1
        first_930, first_midnight, hour_ids = classify(day, gaps)
        for g in gaps:
            tagged = False
            if first_930 is not None and g is first_930:
                groups["first_930"].append(g)
                tagged = True
            if first_midnight is not None and g is first_midnight:
                groups["first_midnight"].append(g)
                tagged = True
            if id(g) in hour_ids:
                groups["first_of_hour"].append(g)
                tagged = True
            if not tagged:
                groups["rest"].append(g)

    assert len(groups["first_930"]) <= days_used, groups["first_930"]
    assert len(groups["first_midnight"]) <= days_used, groups["first_midnight"]

    return {"days_used": days_used, "group_stats": {name: stats(gaps) for name, gaps in groups.items()}}


def main() -> None:
    result = run()
    print(f"{result['days_used']} Handelstage mit FVG-Daten.\n")
    print(f"{'Gruppe':<16}{'n':>6}{'Fill%':>8}{'CE-Hit%':>10}{'AvgSize':>10}")
    for name, s in result["group_stats"].items():
        print(f"{name:<16}{s['n']:>6}{s['filled']:>8.1f}{s['ce_hit']:>10.1f}{s['avg_size']:>10.2f}")

    write_result("backtest_fvg_specialness", result)


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Nach-Lauf + Diff**

Run: `python algo/backtest_fvg_specialness.py > algo/_after.txt 2>&1 && diff algo/_baseline.txt algo/_after.txt`
Expected: keine Ausgabe (identisch)

- [ ] **Step 4: Aufraeumen + Commit**

```bash
rm algo/_baseline.txt algo/_after.txt
git add algo/backtest_fvg_specialness.py
git commit -m "$(cat <<'EOF'
refactor(algo): backtest_fvg_specialness.py -- run()/main()-Trennung

Kein Bug gefunden. Konsolenausgabe unveraendert (Diff-verifiziert), neu:
algo/results/backtest_fvg_specialness.json.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_015ynwbhsEzjykXFsjuKRhsK
EOF
)"
```

---

### Task 10: `algo/backtest_midnight_range_std.py` — `run()`

**Files:**
- Modify: `algo/backtest_midnight_range_std.py` (komplett, 115 Zeilen)

**Interfaces:**
- Consumes: `backtest_org_ce.find_days`, `backtest_common.write_result`.
- Produces: `session_range(...)`, `midnight_range(...)` (unveraendert, werden von `backtest_midnight_range_judas.py` importiert), `run() -> dict`.

Kein Bug gefunden (der theoretische `ZeroDivisionError` bei komplett leerem `london_low` ist bei der aktuellen, immer gefuellten Datenbasis nicht erreichbar -- keine Aenderung, um das bestehende Verhalten 1:1 zu erhalten).

- [ ] **Step 1: Baseline sichern**

Run: `python algo/backtest_midnight_range_std.py > algo/_baseline.txt 2>&1`

- [ ] **Step 2: Datei ersetzen**

```python
from __future__ import annotations

import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from analyze_ohlc import load, at  # noqa: E402
from backtest_org_ce import find_days  # noqa: E402
from backtest_common import write_result  # noqa: E402

BUCKETS = [0.5, 1.0, 1.5, 2.0, 3.0, 5.0, float("inf")]


def session_range(bars, day, start_hm: tuple[int, int], end_hm: tuple[int, int]):
    """Kerzen-High/Low ueber ein Zeitfenster (z.B. eine Opening Range). None, wenn keine
    Kerzen im Fenster liegen oder das Fenster keine echte Range hat (rng <= 0)."""
    win = [b for b in bars if at(day, *start_hm) <= b.t < at(day, *end_hm)]
    if not win:
        return None
    rh, rl = max(b.h for b in win), min(b.l for b in win)
    rng = rh - rl
    return (rh, rl, rng) if rng > 0 else None


def midnight_range(bars, day):
    """Rueckwaertskompatibler Spezialfall: Midnight/London Opening Range 0:00-0:30 NY."""
    return session_range(bars, day, (0, 0), (0, 30))


def k_extension(bars, day, start, end, rh, rl, rng):
    seg = [b for b in bars if start <= b.t < end]
    if not seg:
        return None, None
    day_high = max(b.h for b in seg)
    day_low = min(b.l for b in seg)
    k_high = max(0.0, (day_high - rh) / rng)
    k_low = max(0.0, (rl - day_low) / rng)
    return k_high, k_low


def bucket(k: float) -> str:
    for b in BUCKETS:
        if k <= b:
            return f"<= {b} STD" if b != float("inf") else "> 5 STD"
    return "> 5 STD"


def report(name: str, ks: list[float]) -> None:
    if not ks:
        print(f"{name}: keine Tage")
        return
    print(f"\n{name} (n={len(ks)}): Median {statistics.median(ks):.2f} STD, "
          f"Mittelwert {statistics.mean(ks):.2f} STD, Max {max(ks):.2f} STD")
    counts: dict[str, int] = {}
    for k in ks:
        counts[bucket(k)] = counts.get(bucket(k), 0) + 1
    for b in BUCKETS:
        label = f"<= {b} STD" if b != float("inf") else "> 5 STD"
        c = counts.get(label, 0)
        print(f"  {label:<12}{c:>4}  ({100 * c / len(ks):.1f}%)")


def run() -> dict:
    london_high, london_low, day_high, day_low = [], [], [], []
    days_used = 0
    for day, path in find_days():
        bars = load(path)
        mr = midnight_range(bars, day)
        if mr is None:
            continue
        rh, rl, rng = mr
        lh, ll = k_extension(bars, day, at(day, 1, 0), at(day, 5, 0), rh, rl, rng)
        dh, dl = k_extension(bars, day, at(day, 0, 30), at(day, 17, 0), rh, rl, rng)
        if lh is None or dh is None:
            continue
        days_used += 1
        london_high.append(lh)
        london_low.append(ll)
        day_high.append(dh)
        day_low.append(dl)

    exceed_1std = sum(1 for k in london_low if k > 1.0) / len(london_low)

    return {"days_used": days_used, "london_high": london_high, "london_low": london_low,
            "day_high": day_high, "day_low": day_low, "exceed_1std_pct": 100 * exceed_1std}


def main() -> None:
    result = run()
    print(f"{result['days_used']} Handelstage mit Midnight-Range-Daten.")
    print("\n-- Waehrend London (1:00-5:00 NY) -- These: 'max. Manipulation bis -1 STD' --")
    report("London-Low unter Range-Tief", result["london_low"])
    report("London-High ueber Range-Hoch", result["london_high"])
    print("\n-- Ganzer Tag (0:30-17:00 NY) --")
    report("Tages-Low unter Range-Tief", result["day_low"])
    report("Tages-High ueber Range-Hoch", result["day_high"])

    print(f"\nLondon-Low geht bei {result['exceed_1std_pct']:.1f}% der Tage ueber -1 STD "
          f"hinaus (These behauptet: das soll waehrend London selten/nie passieren).")

    write_result("backtest_midnight_range_std", {
        "days_used": result["days_used"], "exceed_1std_pct": result["exceed_1std_pct"],
        "london_low_median": statistics.median(result["london_low"]) if result["london_low"] else None,
        "london_high_median": statistics.median(result["london_high"]) if result["london_high"] else None,
        "day_low_median": statistics.median(result["day_low"]) if result["day_low"] else None,
        "day_high_median": statistics.median(result["day_high"]) if result["day_high"] else None,
    })


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Nach-Lauf + Diff**

Run: `python algo/backtest_midnight_range_std.py > algo/_after.txt 2>&1 && diff algo/_baseline.txt algo/_after.txt`
Expected: keine Ausgabe (identisch)

- [ ] **Step 4: Aufraeumen + Commit**

```bash
rm algo/_baseline.txt algo/_after.txt
git add algo/backtest_midnight_range_std.py
git commit -m "$(cat <<'EOF'
refactor(algo): backtest_midnight_range_std.py -- run()/main()-Trennung

Kein Bug gefunden. Konsolenausgabe unveraendert (Diff-verifiziert), neu:
algo/results/backtest_midnight_range_std.json.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_015ynwbhsEzjykXFsjuKRhsK
EOF
)"
```

---

### Task 11: `algo/backtest_midnight_range_judas.py` — `run()`

**Files:**
- Modify: `algo/backtest_midnight_range_judas.py` (komplett, 158 Zeilen)

**Interfaces:**
- Consumes: `backtest_org_ce.find_days`, `backtest_midnight_range_std.session_range`, `backtest_common.write_result`.
- Produces: `run() -> dict` mit Key `sessions` (Liste von 4 Session-Ergebnis-dicts).

`run_backtest()` wird in `compute_session()` (reine Berechnung) und `print_session()` (Ausgabe) aufgespalten, da diese Funktion bisher Berechnung und Print vermischte -- fuer den `run()`-Vertrag muss die Berechnung ohne Print laufen koennen. Kein inhaltlicher Bug gefunden.

- [ ] **Step 1: Baseline sichern**

Run: `python algo/backtest_midnight_range_judas.py > algo/_baseline.txt 2>&1`

- [ ] **Step 2: Datei ersetzen**

```python
from __future__ import annotations

import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from analyze_ohlc import load, at, fvgs  # noqa: E402
from backtest_org_ce import find_days  # noqa: E402
from backtest_midnight_range_std import session_range  # noqa: E402
from backtest_common import write_result  # noqa: E402

SESSIONS = [
    ("Midnight/London ORG", (0, 0), (0, 30), (0, 30), (5, 0)),
    ("NY Pre-Session ORG", (7, 0), (7, 30), (7, 30), (9, 30)),
    ("NY PM ORG", (13, 30), (14, 0), (14, 0), (16, 0)),
]


def classify_side(bars, day, rh, rl, rng, side: str, start, end) -> dict:
    """side='low' (Sellside-Manipulation unter Rl) oder 'high' (Buyside-Manipulation ueber Rh).
    `start`/`end` ist das Testfenster, in dem Durchbruch + Rueckeroberung geprueft werden."""
    seg = [b for b in bars if start <= b.t < end]
    level = rl if side == "low" else rh
    penetrating = [b for b in seg if (b.l < level if side == "low" else b.h > level)]
    if not penetrating:
        return {"status": "no_extension", "k": 0.0}

    extreme_bar = min(penetrating, key=lambda b: b.l) if side == "low" \
        else max(penetrating, key=lambda b: b.h)
    depth = (level - extreme_bar.l) if side == "low" else (extreme_bar.h - level)
    k = depth / rng

    after = [b for b in seg if b.t > extreme_bar.t]
    reclaimed = any((b.c >= level) if side == "low" else (b.c <= level) for b in after)
    return {"status": "manipulation" if reclaimed else "trend", "k": k, "t": extreme_bar.t}


def fvg_range(bars, day, start_hm, end_hm):
    """Groesstes FVG (nicht zwingend das erste, siehe wiki/concepts/ORG.../1st Presented FVG)
    mit Startzeit im Fenster -- dessen eigene Lo/Hi als STD-Basiseinheit statt der Kerzen-Range."""
    start, end = at(day, *start_hm), at(day, *end_hm)
    cand = [g for g in fvgs(bars) if start <= g["t"] < end]
    if not cand:
        return None
    biggest = max(cand, key=lambda g: g["size"])
    return biggest["hi"], biggest["lo"], biggest["size"]


def report(name: str, results: list[dict], range_label: str, window_label: str) -> None:
    n = len(results)
    if n == 0:
        print(f"{name}: keine Tage")
        return
    counts = {"no_extension": 0, "manipulation": 0, "trend": 0}
    for r in results:
        counts[r["status"]] += 1
    assert sum(counts.values()) == n, counts
    print(f"\n{name} (n={n}):")
    for status, label in [
        ("no_extension", f"High/Low bereits in {range_label} gesetzt (keine Extension)"),
        ("manipulation", f"Manipulation (Durchbruch + Rueckeroberung in {window_label})"),
        ("trend", "Trend/echter Move (Durchbruch haelt bis Fensterende)"),
    ]:
        c = counts[status]
        print(f"  {label:<62}{c:>4}  ({100 * c / n:.1f}%)")

    manip_ks = [r["k"] for r in results if r["status"] == "manipulation"]
    if manip_ks:
        print(f"  -> Manipulationstiefe (nur 'manipulation'-Tage, n={len(manip_ks)}): "
              f"Median {statistics.median(manip_ks):.2f} STD, "
              f"Mittelwert {statistics.mean(manip_ks):.2f} STD")
        buckets = [0.5, 1.0, 1.5, 2.0, 3.0, float("inf")]
        for b in buckets:
            lo = 0 if b == buckets[0] else buckets[buckets.index(b) - 1]
            c = (sum(1 for k in manip_ks if lo < k <= b) if b != buckets[0]
                 else sum(1 for k in manip_ks if k <= b))
            label = f"<= {b} STD" if b != float("inf") else "> 3 STD"
            print(f"     {label:<12}{c:>4}  ({100 * c / len(manip_ks):.1f}%)")


def compute_session(label: str, range_hm: tuple, range_end_hm: tuple,
                     test_start_hm: tuple, test_end_hm: tuple, use_fvg: bool = False) -> dict:
    low_results, high_results = [], []
    either_count = both_count = days_used = 0
    for day, path in find_days():
        bars = load(path)
        rr = (fvg_range(bars, day, range_hm, range_end_hm) if use_fvg
              else session_range(bars, day, range_hm, range_end_hm))
        if rr is None:
            continue
        rh, rl, rng = rr
        test_start, test_end = at(day, *test_start_hm), at(day, *test_end_hm)
        lo = classify_side(bars, day, rh, rl, rng, "low", test_start, test_end)
        hi = classify_side(bars, day, rh, rl, rng, "high", test_start, test_end)
        low_results.append(lo)
        high_results.append(hi)
        lo_ne, hi_ne = lo["status"] == "no_extension", hi["status"] == "no_extension"
        either_count += lo_ne or hi_ne
        both_count += lo_ne and hi_ne
        days_used += 1

    range_label = f"{range_hm[0]:02d}:{range_hm[1]:02d}-{range_end_hm[0]:02d}:{range_end_hm[1]:02d}"
    window_label = f"{test_start_hm[0]:02d}:{test_start_hm[1]:02d}-{test_end_hm[0]:02d}:{test_end_hm[1]:02d}"
    return {"label": label, "range_label": range_label, "window_label": window_label,
            "use_fvg": use_fvg, "days_used": days_used, "low_results": low_results,
            "high_results": high_results, "either_count": either_count, "both_count": both_count}


def print_session(data: dict) -> None:
    print(f"\n{'=' * 70}\n{data['label']} (Range {data['range_label']}"
          f"{' , groesstes FVG darin' if data['use_fvg'] else ''}, "
          f"Testfenster {data['window_label']}) -- {data['days_used']} Tage")
    report("Sellside (unter Range-Low)", data["low_results"], data["range_label"], data["window_label"])
    report("Buyside (ueber Range-High)", data["high_results"], data["range_label"], data["window_label"])

    if data["days_used"] == 0:
        return
    days_used = data["days_used"]
    set_in_range = sum(1 for r in data["low_results"] + data["high_results"]
                        if r["status"] == "no_extension")
    print(f"\nInsgesamt {set_in_range}/{2 * days_used} Seiten "
          f"({100 * set_in_range / (2 * days_used):.1f}%) im Testfenster ueberhaupt nicht "
          f"durchbrochen -- fuer diese haelt die These 'High/Low in {data['range_label']} gesetzt' "
          f"woertlich.")
    print(f"Pro Tag (High ODER Low): an {data['either_count']}/{days_used} Tagen "
          f"({100 * data['either_count'] / days_used:.1f}%) wurde mindestens eine Seite nicht "
          f"durchbrochen -- an {data['both_count']}/{days_used} Tagen beide.")


def run() -> dict:
    sessions = [compute_session(label, r_start, r_end, t_start, t_end)
                for label, r_start, r_end, t_start, t_end in SESSIONS]
    sessions.append(compute_session(
        "Midnight/London ORG -- groesstes FVG statt Kerzen-Range",
        (0, 0), (0, 30), (0, 30), (5, 0), use_fvg=True))
    return {"sessions": sessions}


def main() -> None:
    result = run()
    for data in result["sessions"]:
        print_session(data)

    summary = [{"label": s["label"], "days_used": s["days_used"],
                "either_pct": 100 * s["either_count"] / s["days_used"] if s["days_used"] else None,
                "both_pct": 100 * s["both_count"] / s["days_used"] if s["days_used"] else None}
               for s in result["sessions"]]
    write_result("backtest_midnight_range_judas", {"sessions": summary})


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Nach-Lauf + Diff**

Run: `python algo/backtest_midnight_range_judas.py > algo/_after.txt 2>&1 && diff algo/_baseline.txt algo/_after.txt`
Expected: keine Ausgabe (identisch)

- [ ] **Step 4: Aufraeumen + Commit**

```bash
rm algo/_baseline.txt algo/_after.txt
git add algo/backtest_midnight_range_judas.py
git commit -m "$(cat <<'EOF'
refactor(algo): backtest_midnight_range_judas.py -- compute/print-Trennung fuer run()

run_backtest() in compute_session() (reine Berechnung) und print_session() (Ausgabe)
aufgespalten. Kein inhaltlicher Bug gefunden. Konsolenausgabe unveraendert
(Diff-verifiziert), neu: algo/results/backtest_midnight_range_judas.json.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_015ynwbhsEzjykXFsjuKRhsK
EOF
)"
```

---

### Task 12: `algo/backtest_ohlc.py` — `run()`

**Files:**
- Modify: `algo/backtest_ohlc.py`, nur `main()` (Zeilen 252-276) plus neuer `run()` davor

**Interfaces:**
- Consumes: `backtest_common.write_result`.
- Produces: `run(symbol: str = "MNQ") -> dict` mit Keys `symbol, n_days, rows, agg` (einziges Skript mit Symbol-Parameter, da `find_days(symbol)` bereits eine CLI-Flexibilitaet hat, die erhalten bleibt).

- [ ] **Step 1: Baseline sichern**

Run: `python algo/backtest_ohlc.py MNQ > algo/_baseline.txt 2>&1`

- [ ] **Step 2: Import ergaenzen**

In `algo/backtest_ohlc.py`, nach der bestehenden `sys.path.insert(...)`/Import-Zeile (Zeilen 28-32) ergaenzen:

```python
sys.path.insert(0, str(Path(__file__).resolve().parent))
from backtest_common import write_result  # noqa: E402
```

- [ ] **Step 3: `run()` einfuegen und `main()` ersetzen**

Ersetze `def main(argv=None):` bis zum Dateiende (Zeilen 252-276) durch:

```python
def run(symbol: str = "MNQ") -> dict:
    days = find_days(symbol)
    rows = [(day, sym, analyze_day(day, path)) for day, sym, path in days]
    rows = [r for r in rows if r[2]]
    agg = {}
    for _, _, r in rows:
        for k, v in r.items():
            agg[k] = agg.get(k, 0) + v
    return {"symbol": symbol, "n_days": len(rows), "rows": rows, "agg": agg}


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("symbol", nargs="?", default="MNQ", help="Symbol (default: MNQ)")
    ap.add_argument("-o", "--out", help="Ausgabedatei (default: stdout)")
    a = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")

    result = run(a.symbol)
    lines = report(result["rows"])
    text = "\n".join(lines)
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
        print(f"geschrieben: {a.out} ({result['n_days']} Handelstag(e))")
    else:
        print(text)

    write_result("backtest_ohlc", {"symbol": result["symbol"], "n_days": result["n_days"],
                                    "agg": result["agg"]})


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Nach-Lauf + Diff (stdout)**

Run: `python algo/backtest_ohlc.py MNQ > algo/_after.txt 2>&1 && diff algo/_baseline.txt algo/_after.txt`
Expected: keine Ausgabe (identisch)

- [ ] **Step 5: `-o`-Flag pruefen (bestehendes Wiki-Schreibverhalten)**

Run: `python algo/backtest_ohlc.py MNQ -o "wiki/synthesis/Muster-Validierung (laufend).md"`
Expected: `geschrieben: wiki/synthesis/Muster-Validierung (laufend).md (N Handelstag(e))`, Datei aktualisiert (Diff via `git diff "wiki/synthesis/Muster-Validierung (laufend).md"` sollte nur das `updated:`-Datum aendern, falls sich seit dem letzten Lauf keine Zahlen verschoben haben)

- [ ] **Step 6: Aufraeumen + Commit**

```bash
rm algo/_baseline.txt algo/_after.txt
git add algo/backtest_ohlc.py "wiki/synthesis/Muster-Validierung (laufend).md"
git commit -m "$(cat <<'EOF'
refactor(algo): backtest_ohlc.py -- run()/main()-Trennung

run(symbol="MNQ") kapselt die Datenaggregation, main() bleibt fuer CLI (-o-Flag)
zustaendig. Konsolen-/Dateiausgabe unveraendert (Diff-verifiziert), neu:
algo/results/backtest_ohlc.json (Symbol/n_days/agg, kompakt statt Rohdaten).

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_015ynwbhsEzjykXFsjuKRhsK
EOF
)"
```

---

### Task 13: `algo/explore_patterns.py` — nur `pearson()`-Dedup

**Files:**
- Modify: `algo/explore_patterns.py`, Zeilen 27-57

**Interfaces:**
- Consumes: `backtest_common.pearson`.

Ausserhalb des `run()`/Audit-Scopes (siehe Spec) -- nur die duplizierte `pearson()`-Definition wird entfernt.

- [ ] **Step 1: Baseline sichern**

Run: `python algo/explore_patterns.py > algo/_baseline.txt 2>&1`

- [ ] **Step 2: Import ergaenzen, `pearson()`-Definition entfernen**

Ersetze Zeilen 27-57 (`sys.path.insert(0, str(Path(__file__).resolve().parent))` bis zum Ende der `pearson()`-Funktion) durch:

```python
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from analyze_ohlc import load, at  # noqa: E402
from backtest_common import pearson  # noqa: E402
from backtest_org_ce import find_days  # noqa: E402

WEEKDAY_NAMES = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]


def day_stats(bars, day) -> dict | None:
    rth = [b for b in bars if at(day, 9, 30) <= b.t < at(day, 16, 0)]
    if not rth:
        return None
    hi_bar = max(rth, key=lambda b: b.h)
    lo_bar = min(rth, key=lambda b: b.l)
    return {
        "day": day, "weekday": day.weekday(), "open": rth[0].o, "close": rth[-1].c,
        "range": hi_bar.h - lo_bar.l, "bullish": rth[-1].c > rth[0].o,
        "high": hi_bar.h, "low": lo_bar.l,
        "high_hour": hi_bar.t.hour, "low_hour": lo_bar.t.hour,
    }
```

(`main()` ab der bisherigen Zeile 60 bleibt unveraendert -- nur die `pearson()`-Definition entfaellt.)

- [ ] **Step 3: Nach-Lauf + Diff**

Run: `python algo/explore_patterns.py > algo/_after.txt 2>&1 && diff algo/_baseline.txt algo/_after.txt`
Expected: keine Ausgabe (identisch)

- [ ] **Step 4: Aufraeumen + Commit**

```bash
rm algo/_baseline.txt algo/_after.txt
git add algo/explore_patterns.py
git commit -m "$(cat <<'EOF'
refactor(algo): explore_patterns.py -- pearson() aus backtest_common.py statt Duplikat

Letztes der 4 identischen pearson()-Duplikate entfernt. Konsolenausgabe
unveraendert (Diff-verifiziert).

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_015ynwbhsEzjykXFsjuKRhsK
EOF
)"
```

---

### Task 14: `algo/selfcheck.py` — Schnittstellen-Check fuer alle 11 Skripte

**Files:**
- Modify: `algo/selfcheck.py` (komplett, 52 Zeilen)

**Interfaces:**
- Consumes: `run()` aus allen 11 auditierten Skripten (Tasks 2-12), `backtest_common.RESULTS_DIR`, `backtest_common.write_result`.

Kein Zahlen-Assert (Werte wachsen mit den Daten) -- reiner Schnittstellen-Regressionscheck: `run()` liefert ein dict, `write_result()` schreibt gueltiges JSON.

- [ ] **Step 1: Datei ersetzen**

```python
#!/usr/bin/env python3
"""Buendelt alle demo()-Selbstchecks aus dem Praezisions-Audit
(docs/superpowers/specs/2026-08-06-algo-backtest-precision-audit-design.md) und den
Schnittstellen-Check der 11 entduplizierten Explorationsskripte
(docs/superpowers/specs/2026-08-07-algo-backtest-dedup-audit-design.md) zu einem
Kommando -- gedacht als schneller Regressions-Check, kein neuer inhaltlicher Backtest.

Aufruf:
    python algo/selfcheck.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from pnl import demo as pnl_demo  # noqa: E402
from rules import demo as rules_demo  # noqa: E402
from signals import _demo as signals_demo  # noqa: E402
from backtest_ensemble import _demo as ensemble_demo  # noqa: E402
from backtest_common import demo as backtest_common_demo  # noqa: E402


def _results_demo() -> None:
    """run() liefert ein dict, write_result() schreibt gueltiges JSON -- fuer jedes der 11
    im Dedup-Audit (2026-08-07) umgebauten Skripte. Kein Zahlen-Assert, nur Interface."""
    import backtest_daily_patterns
    import backtest_nwog
    import backtest_tgif
    import backtest_ndog
    import backtest_fred_events
    import backtest_org_ce
    import backtest_fvg_specialness
    import backtest_midnight_range_std
    import backtest_midnight_range_judas
    import backtest_ohlc
    import backtest_seasonal
    from backtest_common import RESULTS_DIR, write_result

    checks = [
        ("backtest_daily_patterns", backtest_daily_patterns.run),
        ("backtest_nwog", backtest_nwog.run),
        ("backtest_tgif", backtest_tgif.run),
        ("backtest_ndog", backtest_ndog.run),
        ("backtest_fred_events", backtest_fred_events.run),
        ("backtest_org_ce", backtest_org_ce.run),
        ("backtest_fvg_specialness", backtest_fvg_specialness.run),
        ("backtest_midnight_range_std", backtest_midnight_range_std.run),
        ("backtest_midnight_range_judas", backtest_midnight_range_judas.run),
        ("backtest_ohlc", lambda: backtest_ohlc.run("MNQ")),
    ]
    for name, call in checks:
        result = call()
        assert isinstance(result, dict), f"{name}.run() liefert kein dict"
        write_result(name, result)
        path = RESULTS_DIR / f"{name}.json"
        assert path.exists(), f"{name}: {path} wurde nicht geschrieben"
        json.loads(path.read_text(encoding="utf-8"))  # wirft bei ungueltigem JSON

    assert isinstance(backtest_seasonal.run(), dict), "backtest_seasonal.run() liefert kein dict"


CHECKS = [
    ("pnl", pnl_demo),
    ("rules", rules_demo),
    ("signals", signals_demo),
    ("backtest_ensemble", ensemble_demo),
    ("backtest_common", backtest_common_demo),
    ("dedup", _results_demo),
]


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    failed = []
    for name, check in CHECKS:
        try:
            check()
        except Exception as exc:  # noqa: BLE001
            failed.append((name, exc))
            print(f"[FAIL] {name}: {exc}")
        else:
            print(f"[OK]   {name}")
    if failed:
        print(f"\n{len(failed)}/{len(CHECKS)} Selbstchecks fehlgeschlagen.")
        return 1
    print(f"\nAlle {len(CHECKS)} Selbstchecks bestanden.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Laufen lassen**

Run: `python algo/selfcheck.py`
Expected: `Alle 6 Selbstchecks bestanden.`, Exit-Code 0

- [ ] **Step 3: Commit**

```bash
git add algo/selfcheck.py
git commit -m "$(cat <<'EOF'
test(algo): selfcheck.py -- Schnittstellen-Check fuer alle 11 entduplizierten Skripte

Neuer 'dedup'-Check ruft run() fuer alle 11 im Dedup-Audit umgebauten Skripte auf
und prueft dict-Rueckgabe + gueltiges algo/results/<name>.json. Kein Zahlen-Assert.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_015ynwbhsEzjykXFsjuKRhsK
EOF
)"
```

---

### Task 15: Doku — `algo/README.md`, `algo/PLAN.md`

**Files:**
- Modify: `algo/README.md` (Abschnitt "Exploratorische Skripte", Zeilen 156-165)
- Modify: `algo/PLAN.md` (neuer Log-Eintrag am Ende, nach Zeile 177; Backlog-Punkt 4 als erledigt markieren, Zeilen 118-121)

- [ ] **Step 1: `algo/README.md` aktualisieren**

Ersetze den Abschnitt "Exploratorische Skripte" (Zeilen 156-165) durch:

```markdown
## `backtest_common.py` -- Geteilte Helfer fuer die Explorationsskripte

**Was:** `find_1d_days()`, `load_rows()`, `pearson()`, `write_result()`. Verhindert, dass
Stat-Skripte sich gegenseitig nur wegen einer Funktion importieren (vorher: `pearson()` 4x
dupliziert, `load_rows()`/`find_1d_days()` nur ueber Seiteneingaenge importierbar).
**Audit 2026-08-07:** Entduplizierung + Korrektheits-Audit, siehe
`docs/superpowers/specs/2026-08-07-algo-backtest-dedup-audit-design.md`. Ein Bug gefunden und
behoben: `backtest_seasonal.py::turn_of_month()` zaehlte Tage an Monatsuebergaengen doppelt
(seit 2026-08-06 dokumentiert, jetzt gefixt).

## Exploratorische Skripte (`backtest_daily_patterns.py`, `backtest_fred_events.py`,
`backtest_ndog.py`, `backtest_nwog.py`, `backtest_ohlc.py`, `backtest_org_ce.py`,
`backtest_seasonal.py`, `backtest_tgif.py`, `backtest_fvg_specialness.py`,
`backtest_midnight_range_std.py`, `backtest_midnight_range_judas.py`)

**Was:** Reine statistische Zaehl-/Korrelationsskripte (Wochentag-Effekt, Turn-of-Month,
NDOG/NWOG-Bias, TGIF, FVG-Besonderheiten, Midnight-Range-STD/Judas-Swing, FRED-Events) --
nutzen NICHT die `backtesting`-Engine (bestaetigt per Grep, 2026-08-06), daher betrifft sie der
Punktwert-Layer aus `pnl.py` nicht. Jedes Skript trennt seit 2026-08-07 `run() -> dict` (reine
Berechnung, importierbar) von `main()` (Konsolenausgabe + `write_result()`) -- CLI-Verhalten
unveraendert. Ergebnis landet in `algo/results/<skriptname>.json` (Ausnahme:
`backtest_seasonal.py`, das schreibt weiterhin nur `algo/seasonal_tendency.json`).
**Audit 2026-08-06:** Alle 11 Skripte bestehen die Lookahead-Checkliste (keine Funde).
**Audit 2026-08-07:** Doppelzaehlungs-Bug in `backtest_seasonal.py::turn_of_month()` behoben
(siehe oben), sonst keine weiteren Bugs gefunden. `pearson()`-Duplikat (4x) und
`load_rows()`/`find_1d_days()`-Seiteneingaenge in `backtest_common.py` konsolidiert.
```

- [ ] **Step 2: `algo/PLAN.md` — Backlog-Punkt 4 als erledigt markieren**

Ersetze in Punkt 4 des Abschnitts "Code-Ideen (Backlog)" (beginnt "**Backtest-Ergebnisse als Datenartefakt**...") den einleitenden Satz durch:

```markdown
4. ~~**Backtest-Ergebnisse als Datenartefakt**~~ **erledigt 2026-08-07** -- `algo/results/<name>.json`
   pro Skript (Ausnahme `backtest_seasonal.py`, siehe `algo/seasonal_tendency.json`), siehe
   Log-Eintrag unten. Urspruenglicher Text: eine Zeile pro erkanntem Setup (Datum, Zeit, Muster,
   Richtung, Entry/Stop/Target, Ausgang) in einer CSV/JSON unter `algo/`. Das ist die Bruecke,
   ueber die "laufende Daten + Wiki verbessern den Algo" konkret wird -- sonst bleibt der Satz
   eine Absicht ohne Mechanismus.
```

- [ ] **Step 3: `algo/PLAN.md` — Log-Eintrag anhaengen**

Nach der letzten Log-Zeile (2026-08-07-Eintrag zum Code-Review des Praezisions-Audits) eine neue Zeile anhaengen:

```markdown
| 2026-08-07 | **Backtest-Skript-Entduplizierung & Audit (Phase 1 des TUI-Vorhabens, siehe Spec/Plan-Doku unten).** Nutzerwunsch: pruefen, ob die ~20 Einzeldateien in `algo/` Sinn ergeben oder in eine interaktive Oberflaeche gehoeren -- Entscheidung: Dateien bleiben getrennt (Git-Historie pro These), stattdessen Korrektheits-Audit + Entduplizierung als Fundament fuer eine spaetere TUI (Phase 2, eigener Spec). Neu: `algo/backtest_common.py` buendelt `find_1d_days()`/`load_rows()`/`pearson()` (vorher: `pearson()` 4x dupliziert in `backtest_ndog.py`/`backtest_nwog.py`/`backtest_daily_patterns.py`/`explore_patterns.py`) + `write_result()`. Alle 11 exploratorischen Skripte bekamen eine `run()`/`main()`-Trennung (Konsolenausgabe Diff-verifiziert unveraendert), jedes schreibt sein Ergebnis nach `algo/results/<name>.json` -- damit ist der seit 2026-08-03 offene PLAN.md-Backlog-Punkt 4 ("Backtest-Ergebnisse als Datenartefakt") erledigt. **Ein echter Bug gefunden und gefixt**: `backtest_seasonal.py::turn_of_month()` zaehlte Tage an Monatsuebergaengen doppelt (ueberlappende `rs[:-1]`/`nrs[3:]`-Slices akkumulierten `rest` inkrementell statt es als Komplement von `tom_days` zu berechnen) -- seit dem Praezisions-Audit-Nachtrag am 2026-08-06 dokumentiert, aber nie tatsaechlich behoben (ein bereits vorhandener `tom_days`-Filter taeuschte einen Fix vor, entfernte aber nur die TOM/rest-Ueberschneidung, nicht die rest/rest-Selbstdopplung). `wiki/synthesis/Seasonal Tendency (Eigene Daten, laufend).md` mit den korrigierten Zahlen aktualisiert. Sonst keine weiteren Bugs in den 11 Skripten gefunden (Audit-Kriterien: Doppelzaehlung, Off-by-one, Division-durch-Null, ehrliche Stichprobengroesse -- ueber den bestehenden 2026-08-06-Lookahead-Check hinaus). `algo/selfcheck.py` bekam einen neuen `dedup`-Check (ruft `run()` fuer alle 11 Skripte auf, prueft dict-Rueckgabe + gueltiges JSON, kein Zahlen-Assert). Phase 2 (interaktive TUI-Oberflaeche darauf aufbauend, "Bloomberg-Terminal"-Anspruch des Nutzers) ist ein eigener, spaeterer Spec. |
```

- [ ] **Step 4: Commit**

```bash
git add algo/README.md algo/PLAN.md
git commit -m "$(cat <<'EOF'
docs(algo): README/PLAN.md -- Dedup-Audit dokumentiert, Backlog-Punkt 4 erledigt

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_015ynwbhsEzjykXFsjuKRhsK
EOF
)"
```

---

## Self-Review (durchgefuehrt)

- **Spec-Abdeckung:** `backtest_common.py` (Task 1), alle 11 Skripte (Tasks 2-12), `explore_patterns.py`-Pearson-Dedup (Task 13, im Spec explizit erwaehnt), `selfcheck.py`-Check (Task 14), README/PLAN.md (Task 15) -- jeder Spec-Abschnitt hat eine Task.
- **Platzhalter-Scan:** keine TBD/TODO, jeder Codeblock ist vollstaendig lauffaehiger Code, kein "wie in Task N".
- **Typ-Konsistenz:** `run()`-Signaturen konsistent (`-> dict`, nur `backtest_ohlc.run(symbol: str = "MNQ")` mit Parameter, alle anderen ohne), `write_result(name: str, data: dict)` durchgehend gleich aufgerufen, `RESULTS_DIR` nur in `backtest_common.py`/`selfcheck.py` referenziert.
