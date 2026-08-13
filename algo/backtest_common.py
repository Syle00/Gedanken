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


def find_days(symbol: str = "MNQ", tf: str = "1d") -> list[tuple[date, Path]]:
    """(Handelstag, Pfad) fuer jeden Tagesordner mit `symbol`-Daten im Timeframe `tf`."""
    out = []
    for day_dir in sorted(DATA_DIR.glob("*/*/*")):
        if not day_dir.is_dir():
            continue
        try:
            day = datetime.strptime(day_dir.name, "%d.%m.%Y").date()
        except ValueError:
            continue
        files = sorted(day_dir.glob(f"{symbol} * {tf}.csv"))
        if files:
            out.append((day, files[0]))
    return sorted(out)


def find_1d_days(symbol: str = "MNQ") -> list[tuple[date, Path]]:
    """(Handelstag, Pfad zur 1d-Datei). Verschoben aus backtest_daily_patterns.py
    (2026-08-07), seit 2026-08-13 duenner Wrapper um find_days()."""
    return find_days(symbol, "1d")


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
