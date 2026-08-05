# RenTec-artige Ensemble-Strategie fuer MNQ — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eine zweite, statistisch-datengetriebene Handelsregel (Ensemble aus bestehenden
Backtest-Befunden + Stat-Arb, kombiniert per Logistic Regression zu einem Tages-Bias, der
die bestehende Silver-Bullet-Intraday-Regel filtert), plus generalisierte Validierung
(Walk-Forward/Monte-Carlo/Parameter-Sensitivitaet), Stress-Test gegen historische
Krisenperioden und ein Live-Python-Dashboard.

**Architecture:** Signal-Schicht (`algo/signals.py`, reine Funktionen, kein Lookahead) →
Ensemble-Strategie (`algo/backtest_ensemble.py`, `backtesting.Strategy`-Subklasse wie die
bestehende `SilverBulletStrategy`) → generalisierte Validierung (`algo/validate.py`, von
`backtest_walkforward.py` geloest) → Stress-Test (`algo/stress_test.py`, NQ=F/ES=F-Proxy) →
Live-Dashboard (`algo/dashboard.py`, eigene Simulationsschleife + `matplotlib.animation`).

**Tech Stack:** Python 3, pandas, `backtesting`-Lib (bestehend), neu: `scikit-learn`
(LogisticRegression). Kein neues Test-Framework — Projekt-Konvention ist `demo()`/
`assert`-Selbstcheck im `__main__`-Block (siehe `algo/rules.py`), kein pytest.

**Spec:** `docs/superpowers/specs/2026-08-05-algo-rentec-ensemble-design.md`

## Global Constraints

- Kein Lookahead: Signalfunktionen sehen nur Tage strikt vor `target_day`; Intraday-Code
  (`plan_trade`) nur `bars[t<=when]` — bestehender Vertrag aus `algo/rules.py`, gilt
  unveraendert weiter.
- Fehlende Signalwerte werden als `0.0` (neutral) imputiert, nie als verworfene Zeile.
- Bias-Totzone: `p_bullish > 0.55` → `long`, `< 0.45` → `short`, sonst `neutral` (kein Trade).
- Neue Abhaengigkeit `scikit-learn` nur in `algo/backtest_ensemble.py` importiert — `signals.py`
  bleibt frei davon (pandas/stdlib genuegt dort).
- Stress-Test-Ergebnisse sind Verhaltens-Kennzahlen auf einem Preis-Proxy (NQ=F/ES=F statt
  MNQ), keine echte MNQ-$-P&L — im Report-Text explizit vermerken.
- Test-Konvention: `assert`-basierter `demo()`/`__main__`-Selbstcheck pro Datei mit
  nicht-trivialer Logik (kein pytest, keine neue Test-Abhaengigkeit).
- Dateien folgen dem bestehenden flachen Schema in `algo/` (kein neues Subpackage).

---

## Task 1: Multi-Symbol-Datengrundlage

**Files:**
- Modify: `algo/fetch_yfinance.py`
- Modify: `algo/backtest_daily_patterns.py:27-39` (`find_1d_days`)
- Modify: `algo/backtest_seasonal.py:35-48` (`load_rows`)

**Interfaces:**
- Produces: `fetch_yfinance.fetch(start: str, end: str, symbol: str = "MNQ=F") -> list[Path]`,
  `fetch_yfinance.symbol_prefix(symbol: str) -> str`,
  `backtest_daily_patterns.find_1d_days(symbol: str = "MNQ") -> list[tuple[date, Path]]`,
  `backtest_seasonal.load_rows(symbol: str = "MNQ") -> list[dict]` (dict-Felder wie bisher:
  `day, open, close, high, low, range, ret_pct, bullish`)

Grund: `find_1d_days()` glob't bisher `"* 1d.csv"` ohne Symbol-Filter — sobald ein zweiter
Symbol-Datenstrom (ES=F) im selben Tagesordner liegt, waere die Auswahl zufaellig falsch.
Das muss vor jedem Stat-Arb-Code kommen, sonst laden spaetere Tasks im Zweifel die falsche
Datei.

- [ ] **Step 1: `fetch_yfinance.py` — Symbol generalisieren**

Ersetze die feste `SYMBOL`-Konstante und `write_day`/`download_interval`/`fetch`/`main` so,
dass der Symbol-Praefix im Dateinamen aus dem Ticker abgeleitet wird (`"MNQ=F"` → `"MNQ"`,
`"ES=F"` → `"ES"`, `"NQ=F"` → `"NQ"` — identisch zum bisherigen `"MNQ"`-Praefix, also
rueckwirkungsfrei fuer bestehende Aufrufe):

```python
SYMBOL = "MNQ=F"  # Default, ueberschreibbar per --symbol


def symbol_prefix(symbol: str) -> str:
    return symbol.split("=")[0]


def write_day(symbol: str, tf: str, day, rows: pd.DataFrame) -> Path | None:
    dest = (DATA_DIR / f"{day:%Y}" / f"{day:%m}" / f"{day:%d.%m.%Y}"
            / f"{symbol_prefix(symbol)} {day.isoformat()} {tf}.csv")
    if dest.exists():
        print(f"  = {dest.relative_to(DATA_DIR)} existiert bereits, uebersprungen")
        return None
    dest.parent.mkdir(parents=True, exist_ok=True)
    out = pd.DataFrame({
        "time": rows.index.as_unit("s").astype("int64"),
        "open": rows["Open"].to_numpy(),
        "high": rows["High"].to_numpy(),
        "low": rows["Low"].to_numpy(),
        "close": rows["Close"].to_numpy(),
    })
    out.to_csv(dest, index=False)
    return dest


def download_interval(symbol: str, tf: str, start: str, end: str) -> pd.DataFrame:
    if tf not in CHUNK_DAYS:
        return flatten(yf.download(symbol, start=start, end=end, interval=tf, progress=False))
    cur, end_d = date.fromisoformat(start), date.fromisoformat(end)
    chunks = []
    while cur < end_d:
        nxt = min(cur + timedelta(days=CHUNK_DAYS[tf]), end_d)
        df = flatten(yf.download(symbol, start=cur.isoformat(), end=nxt.isoformat(),
                                  interval=tf, progress=False))
        if not df.empty:
            chunks.append(df)
        cur = nxt
    return pd.concat(chunks) if chunks else pd.DataFrame()


def fetch(start: str, end: str, symbol: str = SYMBOL) -> list[Path]:
    written = []
    hourly = None
    end_day = date.fromisoformat(end)

    def emit(tf: str, day, rows) -> None:
        if day >= end_day:
            return
        f = write_day(symbol, tf, day, rows)
        if f:
            written.append(f)

    for tf in INTERVALS:
        df = download_interval(symbol, tf, start, end)
        if df.empty:
            print(f"  ! {tf}: keine Daten (yfinance-Limit fuer diesen Zeitraum?)")
            continue
        daily = tf == "1d"
        if tf == "1h":
            hourly = df
        for day, rows in df.groupby(df.index.map(lambda ts: trading_day(ts, daily))):
            emit(tf, day, rows)

        if tf in RTH_TFS:
            ny_time = df.index.tz_convert(NY).time
            rth = df[(ny_time >= RTH_START) & (ny_time <= RTH_END)]
            for day, rows in rth.groupby(rth.index.tz_convert(NY).date):
                emit(f"{tf} RTH", day, rows)

    if hourly is not None:
        h4 = (hourly.resample("4h").agg(
            {"Open": "first", "High": "max", "Low": "min", "Close": "last"}).dropna())
        for day, rows in h4.groupby(h4.index.map(trading_day)):
            emit("4h", day, rows)
    return written


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("start")
    ap.add_argument("end", help="exklusiv")
    ap.add_argument("--symbol", default=SYMBOL)
    a = ap.parse_args(argv)
    files = fetch(a.start, a.end, a.symbol)
    print(f"{len(files)} Datei(en) geschrieben.")
    return 0
```

Entferne die alte `SYMBOL`-Nutzung in `download_interval`/`fetch` (globale Konstante wird
nur noch als Default-Argument verwendet, nicht mehr direkt gelesen).

- [ ] **Step 2: `symbol_prefix` Selbstcheck**

Fuege am Dateiende hinzu:

```python
def _demo() -> None:
    assert symbol_prefix("MNQ=F") == "MNQ"
    assert symbol_prefix("ES=F") == "ES"
    assert symbol_prefix("NQ=F") == "NQ"
    print("fetch_yfinance symbol_prefix demo ok")


if __name__ == "__main__":
    _demo()
    sys.exit(main())
```

Run: `python algo/fetch_yfinance.py` (ohne Argumente) — Expected: `demo ok`-Zeile, danach
`argparse`-Nutzungsfehler (fehlende `start`/`end`) — das ist ok, bestaetigt nur dass `_demo()`
vor dem CLI-Parsing laeuft.

- [ ] **Step 3: `find_1d_days` und `load_rows` um Symbol-Parameter erweitern**

`algo/backtest_daily_patterns.py`:

```python
def find_1d_days(symbol: str = "MNQ") -> list[tuple]:
    out = []
    for day_dir in sorted(DATA_DIR.glob("*/*/*")):
        if not day_dir.is_dir():
            continue
        try:
            day = datetime.strptime(day_dir.name, "%d.%m.%Y").date()
        except ValueError:
            continue
        files = list(day_dir.glob(f"{symbol} * 1d.csv"))
        if files:
            out.append((day, files[0]))
    return sorted(out)
```

`algo/backtest_seasonal.py`:

```python
def load_rows(symbol: str = "MNQ") -> list[dict]:
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
```

- [ ] **Step 4: Regressionscheck — bestehendes Verhalten unveraendert**

Run: `python algo/backtest_seasonal.py > /tmp/seasonal_before_and_after.txt` — vor und nach
Step 3 ausfuehren (Default `symbol="MNQ"` muss identische Ausgabe liefern wie vorher).
Expected: identischer Report-Text (Wochentag/Monat/TOM/Woche-Tabellen unveraendert).

- [ ] **Step 5: ES=F-Daten fuer den Hauptbacktest-Zeitraum laden**

Run: `python algo/fetch_yfinance.py 2026-06-07 2026-08-06 --symbol ES=F`

(Ein Tag vor dem in `backtest_walkforward.py` dokumentierten Zeitraum 2026-06-08 bis
2026-08-05 starten, aus demselben Grund wie im `fetch_yfinance.py`-Docstring beschrieben:
Globex-Handelstag beginnt 18:00 NY des Vortages.) Erwartet: mehrere `MNQ ...`→jetzt
`ES ...`-Dateien unter `raw/marktdaten/2026/...`, plus einige `! <tf>: keine Daten`-Zeilen
fuer 1m/5m (yfinance-Limit, erwartet).

- [ ] **Step 6: Commit**

```bash
git add algo/fetch_yfinance.py algo/backtest_daily_patterns.py algo/backtest_seasonal.py raw/marktdaten
git commit -m "algo: fetch_yfinance/find_1d_days/load_rows Symbol-Parameter fuer Multi-Symbol-Daten (ES=F)"
```

---

## Task 2: signals.py — Kalender-Signale

**Files:**
- Create: `algo/signals.py`

**Interfaces:**
- Consumes: `backtest_seasonal.load_rows(symbol) -> list[dict]` (Task 1),
  `backtest_seasonal.turn_of_month(rows) -> dict` (bestehend)
- Produces: `signal_weekday(history, target_day) -> float | None`,
  `signal_turn_of_month(history, target_day) -> float | None`,
  `SIGNAL_NAMES: list[str]` (wird in Task 3-5 erweitert)

- [ ] **Step 1: Datei anlegen mit den zwei Kalender-Signalen**

```python
#!/usr/bin/env python3
"""Signal-Schicht fuer die RenTec-artige Ensemble-Strategie (algo/backtest_ensemble.py) --
reine Funktionen, extrahiert aus den bestehenden Einzel-Backtests (siehe
docs/superpowers/specs/2026-08-05-algo-rentec-ensemble-design.md Phase 1), keine
Neuimplementierung der zugrundeliegenden Statistik. Jede Signalfunktion sieht nur Tage
strikt VOR `target_day` (Historie) -- Kalenderwissen ueber `target_day` selbst (Wochentag,
Kalendertag) ist erlaubt, das ist kein Lookahead (der Kalender ist im Voraus bekannt),
Kursdaten von `target_day` sind es nicht.

Rueckgabe je Signal: float in [-1, +1] (bearish...bullish) oder None, wenn nicht
berechenbar (zu wenig Historie). None wird von build_features() als 0.0 imputiert, nie
als verworfene Zeile.
"""
from __future__ import annotations

import calendar
import statistics
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from backtest_seasonal import load_rows, turn_of_month  # noqa: E402

SIGNAL_NAMES = ["weekday", "turn_of_month", "range_autocorr", "direction_autocorr",
                "stat_arb_spread", "vix_regime", "dgs10_change", "walcl_trend"]


def signal_weekday(history: list[dict], target_day: date) -> float | None:
    """Bias aus dem historischen Wochentag-Effekt (Montag n=147, +0,71% Avg-Rendite,
    siehe backtest_seasonal.py::weekday_table). target_day.weekday() ist Kalenderwissen;
    die Bullish%-Statistik dazu kommt ausschliesslich aus `history`."""
    same_wd = [r for r in history if r["day"].weekday() == target_day.weekday()]
    if len(same_wd) < 10:
        return None
    bullish_pct = sum(r["bullish"] for r in same_wd) / len(same_wd)
    return max(-1.0, min(1.0, 2 * (bullish_pct - 0.5)))


def _in_tom_window(d: date) -> bool:
    # ponytail: Kalendertage statt echter Handelstage (kein Handelskalender im Projekt) --
    # letzte 2 Kalendertage des Monats oder erste 3 des Folgemonats als Naeherung an
    # backtest_seasonal.py::turn_of_month()s Handelstag-genaue TOM-Definition.
    last_day = calendar.monthrange(d.year, d.month)[1]
    return d.day >= last_day - 1 or d.day <= 3


def signal_turn_of_month(history: list[dict], target_day: date) -> float | None:
    """Turn-of-Month-Bias (bestaetigter Fund: TOM +0,341%/64,3% bullish vs. Rest
    +0,070%/52,5%, siehe backtest_seasonal.py::turn_of_month). Ausserhalb des TOM-Fensters
    0.0 (kein belegtes Gegen-Signal fuer den Rest-Monat)."""
    if len(history) < 20:
        return None
    if not _in_tom_window(target_day):
        return 0.0
    tom = turn_of_month(history)
    if tom["window"]["n"] < 5:
        return None
    return max(-1.0, min(1.0, 2 * (tom["window"]["bullish_pct"] / 100 - 0.5)))


def _demo() -> None:
    hist = []
    for i in range(60):
        d = date(2026, 1, 1) + timedelta(days=i)
        if d.weekday() >= 5:
            continue
        bullish = d.weekday() == 0  # nur Montage bullish -> eindeutiges Testsignal
        hist.append({"day": d, "open": 100.0, "close": 101.0 if bullish else 99.0,
                      "high": 101.5, "low": 98.5, "range": 3.0,
                      "ret_pct": 1.0 if bullish else -1.0, "bullish": bullish})
    monday = next(d for d in (date(2026, 3, 2) + timedelta(days=i) for i in range(7))
                  if d.weekday() == 0)
    friday = next(d for d in (date(2026, 3, 2) + timedelta(days=i) for i in range(7))
                  if d.weekday() == 4)
    assert signal_weekday(hist, monday) == 1.0
    assert signal_weekday(hist, friday) == -1.0
    assert signal_weekday(hist[:5], monday) is None  # zu wenig Historie
    print("signals calendar demo ok")


if __name__ == "__main__":
    _demo()
```

- [ ] **Step 2: Run**

Run: `python algo/signals.py` — Expected: `signals calendar demo ok`, kein Traceback.

- [ ] **Step 3: Commit**

```bash
git add algo/signals.py
git commit -m "algo: signals.py mit Wochentag-/Turn-of-Month-Signal (Phase 1)"
```

---

## Task 3: signals.py — Autokorrelations-Signale

**Files:**
- Modify: `algo/signals.py`

**Interfaces:**
- Produces: `signal_range_autocorr(history) -> float | None`,
  `signal_direction_autocorr(history) -> float | None`

- [ ] **Step 1: Zwei Funktionen ergaenzen (vor `_demo`)**

```python
def signal_range_autocorr(history: list[dict]) -> float | None:
    """Volatilitaets-Kontext-Feature, KEIN Richtungssignal: wie weit liegt die Range des
    letzten Tages ueber/unter dem Median der letzten 20 Tage -- nutzt die bestaetigte
    Range-Autokorrelation (r=0,305, n=146, siehe backtest_daily_patterns.py Punkt 2)."""
    if len(history) < 21:
        return None
    recent = [r["range"] for r in history[-21:-1]]
    med = statistics.median(recent)
    if med == 0:
        return 0.0
    ratio = history[-1]["range"] / med - 1
    return max(-1.0, min(1.0, ratio))


def signal_direction_autocorr(history: list[dict]) -> float | None:
    """Momentum-Signal aus der bedingten Wahrscheinlichkeit "bullish nach bullish"/"nach
    bearish" (58,8%/51,5%, n=80/66, siehe backtest_daily_patterns.py Punkt 3) -- nutzt die
    historische Bedingte-Wahrscheinlichkeit aus `history`, nicht eine feste Zahl, damit
    sich das Signal mit mehr Daten anpasst."""
    if len(history) < 15:
        return None
    last_bullish = history[-1]["bullish"]
    pairs = list(zip(history[:-1], history[1:]))
    same = [p[1]["bullish"] for p in pairs if p[0]["bullish"] == last_bullish]
    if len(same) < 10:
        return None
    pct = sum(same) / len(same)
    return max(-1.0, min(1.0, 2 * (pct - 0.5)))
```

- [ ] **Step 2: `_demo()` erweitern**

Fuege vor `print("signals calendar demo ok")` ein (Funktionsname bleibt `_demo`, Test wird
erweitert statt dupliziert):

```python
    trending_up = [{"day": date(2026, 4, 1) + timedelta(days=i), "open": 100 + i,
                     "close": 101 + i, "high": 102 + i, "low": 99 + i, "range": 3.0,
                     "ret_pct": 1.0, "bullish": True} for i in range(20)]
    assert signal_direction_autocorr(trending_up) == 1.0  # immer bullish nach bullish
    assert signal_range_autocorr(trending_up) is not None
    assert signal_range_autocorr(trending_up[:10]) is None  # zu wenig Historie
```

Und passe die Abschluss-Meldung an: `print("signals calendar+autocorr demo ok")`.

- [ ] **Step 3: Run**

Run: `python algo/signals.py` — Expected: `signals calendar+autocorr demo ok`.

- [ ] **Step 4: Commit**

```bash
git add algo/signals.py
git commit -m "algo: signals.py Range-/Richtungs-Autokorrelation ergaenzt"
```

---

## Task 4: signals.py — Stat-Arb-Signal

**Files:**
- Modify: `algo/signals.py`

**Interfaces:**
- Produces: `signal_stat_arb(mnq_history, es_history, target_day, window=20) -> float | None`

- [ ] **Step 1: Funktion ergaenzen**

```python
def signal_stat_arb(mnq_history: list[dict], es_history: list[dict], target_day: date,
                     window: int = 20) -> float | None:
    """Mean-Reversion-Signal: Z-Score des MNQ/ES=F-Tagesrendite-Spreads ueber die letzten
    `window` gemeinsamen Handelstage vor target_day. Lief MNQ zuletzt deutlich staerker als
    ES (positiver Spread), erwartet das Signal eine Rueckkehr zum Mittel (negatives
    Vorzeichen), und umgekehrt -- klassisches Stat-Arb-Paar-Signal (siehe Spec Phase 1)."""
    mnq_by_day = {r["day"]: r["ret_pct"] for r in mnq_history if r["day"] < target_day}
    es_by_day = {r["day"]: r["ret_pct"] for r in es_history if r["day"] < target_day}
    common_days = sorted(set(mnq_by_day) & set(es_by_day))[-window:]
    if len(common_days) < 10:
        return None
    spreads = [mnq_by_day[d] - es_by_day[d] for d in common_days]
    mean_spread = statistics.mean(spreads)
    stdev_spread = statistics.stdev(spreads) if len(spreads) > 1 else 0.0
    if stdev_spread == 0:
        return 0.0
    z = (spreads[-1] - mean_spread) / stdev_spread
    return max(-1.0, min(1.0, -z / 3))
```

- [ ] **Step 2: `_demo()` erweitern**

```python
    mnq_spread = [{"day": date(2026, 5, 1) + timedelta(days=i), "ret_pct": 2.0}
                  for i in range(19)] + [{"day": date(2026, 5, 20), "ret_pct": 10.0}]
    es_spread = [{"day": date(2026, 5, 1) + timedelta(days=i), "ret_pct": 2.0}
                 for i in range(20)]
    z_signal = signal_stat_arb(mnq_spread, es_spread, date(2026, 5, 21))
    assert z_signal is not None and z_signal < -0.5  # MNQ lief stark ab -> Mean-Reversion bearish
    assert signal_stat_arb(mnq_spread[:5], es_spread[:5], date(2026, 5, 21)) is None
```

Abschluss-Meldung: `print("signals calendar+autocorr+statarb demo ok")`.

- [ ] **Step 3: Run**

Run: `python algo/signals.py` — Expected: `signals calendar+autocorr+statarb demo ok`.

- [ ] **Step 4: Commit**

```bash
git add algo/signals.py
git commit -m "algo: signals.py Stat-Arb-Signal (MNQ/ES=F Spread-Z-Score) ergaenzt"
```

---

## Task 5: signals.py — Makro-Signale + `build_features` + `signal_snapshot`

**Files:**
- Modify: `algo/signals.py`

**Interfaces:**
- Consumes: `backtest_fred_events.load_fred(series_id) -> dict[date, float]`,
  `backtest_fred_events.nearest_on_or_before(series, d, lookback=5) -> float | None`
  (bestehend, unveraendert)
- Produces: `signal_vix_regime(history, target_day, vix) -> float | None`,
  `signal_dgs10_change(history, target_day, dgs10) -> float | None`,
  `signal_walcl_trend(history, target_day, walcl) -> float | None`,
  `build_features(mnq_rows, es_rows, min_history=25) -> tuple[list[list[float]], list[int], list[date]]`,
  `signal_snapshot(mnq_rows, es_rows) -> dict[date, dict[str, float]]`

- [ ] **Step 1: Import ergaenzen**

Am Kopf von `algo/signals.py`, nach dem bestehenden Import-Block:

```python
from backtest_fred_events import load_fred, nearest_on_or_before  # noqa: E402
```

- [ ] **Step 2: Makro-Signale ergaenzen**

```python
def signal_vix_regime(history: list[dict], target_day: date, vix: dict) -> float | None:
    """VIX-Tagesaenderung als schwaches Richtungssignal (negative Korrelation VIX-Spike vs.
    MNQ-Rendite, siehe backtest_fred_events.py Punkt 2 -- Rohkorrelation, kein bestaetigter
    Fund, das Modell gewichtet es selbst)."""
    v_today = nearest_on_or_before(vix, target_day - timedelta(days=1))
    v_prev = nearest_on_or_before(vix, target_day - timedelta(days=2))
    if v_today is None or v_prev is None:
        return None
    delta = v_today - v_prev
    return max(-1.0, min(1.0, -delta / 5))


def signal_dgs10_change(history: list[dict], target_day: date, dgs10: dict) -> float | None:
    """10J-Renditeaenderung (siehe backtest_fred_events.py Punkt 3, Rohkorrelation)."""
    d_today = nearest_on_or_before(dgs10, target_day - timedelta(days=1))
    d_prev = nearest_on_or_before(dgs10, target_day - timedelta(days=2), lookback=10)
    if d_today is None or d_prev is None:
        return None
    delta = d_today - d_prev
    return max(-1.0, min(1.0, -delta * 5))


def signal_walcl_trend(history: list[dict], target_day: date, walcl: dict) -> float | None:
    """Fed-Bilanz waechst/schrumpft (woechentliche Reihe, siehe backtest_fred_events.py
    Punkt 4 -- wachsende Bilanz historisch mit hoeherer Wochenrendite assoziiert)."""
    v_now = nearest_on_or_before(walcl, target_day - timedelta(days=1), lookback=10)
    v_prev = nearest_on_or_before(walcl, target_day - timedelta(days=8), lookback=10)
    if v_now is None or v_prev is None:
        return None
    return 1.0 if v_now > v_prev else -1.0
```

- [ ] **Step 3: `build_features` und `signal_snapshot` ergaenzen**

```python
def _row_features(mnq_rows: list[dict], es_rows: list[dict], i: int,
                   vix: dict, dgs10: dict, walcl: dict) -> list[float]:
    history = mnq_rows[:i + 1]
    target_day = mnq_rows[i + 1]["day"]
    values = {
        "weekday": signal_weekday(history, target_day),
        "turn_of_month": signal_turn_of_month(history, target_day),
        "range_autocorr": signal_range_autocorr(history),
        "direction_autocorr": signal_direction_autocorr(history),
        "stat_arb_spread": signal_stat_arb(history, es_rows, target_day),
        "vix_regime": signal_vix_regime(history, target_day, vix),
        "dgs10_change": signal_dgs10_change(history, target_day, dgs10),
        "walcl_trend": signal_walcl_trend(history, target_day, walcl),
    }
    return [0.0 if values[name] is None else values[name] for name in SIGNAL_NAMES]


def build_features(mnq_rows: list[dict], es_rows: list[dict],
                    min_history: int = 25) -> tuple[list[list[float]], list[int], list[date]]:
    """Eine Zeile pro Tag i (min_history <= i < len(mnq_rows)-1): X[i] aus Signalen bis
    Tag i, y[i] = Richtung von Tag i+1 (1=bullish, 0=bearish), target_days[i] = Tag i+1.
    Fehlende Signalwerte werden als 0.0 imputiert, keine Zeile wird deswegen verworfen."""
    vix, dgs10, walcl = load_fred("VIXCLS"), load_fred("DGS10"), load_fred("WALCL")
    X, y, target_days = [], [], []
    for i in range(min_history, len(mnq_rows) - 1):
        X.append(_row_features(mnq_rows, es_rows, i, vix, dgs10, walcl))
        y.append(1 if mnq_rows[i + 1]["bullish"] else 0)
        target_days.append(mnq_rows[i + 1]["day"])
    return X, y, target_days


def signal_snapshot(mnq_rows: list[dict], es_rows: list[dict],
                     min_history: int = 25) -> dict[date, dict[str, float]]:
    """Wie build_features(), aber als {Tag: {Signalname: Wert}} fuer Anzeige (z.B.
    algo/dashboard.py Text-Panel) statt als Matrix fuers Modell."""
    vix, dgs10, walcl = load_fred("VIXCLS"), load_fred("DGS10"), load_fred("WALCL")
    out = {}
    for i in range(min_history, len(mnq_rows) - 1):
        target_day = mnq_rows[i + 1]["day"]
        out[target_day] = dict(zip(SIGNAL_NAMES, _row_features(mnq_rows, es_rows, i, vix, dgs10, walcl)))
    return out
```

- [ ] **Step 4: `_demo()` um einen Integrationscheck mit echten Daten erweitern**

```python
    real_mnq = load_rows("MNQ")
    real_es = load_rows("ES")
    if len(real_mnq) > 30 and len(real_es) > 10:
        X, y, days = build_features(real_mnq, real_es)
        assert len(X) == len(y) == len(days)
        assert all(len(row) == len(SIGNAL_NAMES) for row in X)
        assert all(v in (0, 1) for v in y)
        snap = signal_snapshot(real_mnq, real_es)
        assert set(snap) == set(days)
        print(f"build_features Integrationscheck ok: n={len(X)} Zeilen")
    else:
        print("build_features Integrationscheck uebersprungen (zu wenig echte Daten -- "
              "erwartet vor Task 1 Step 5)")
```

Abschluss-Meldung bleibt `print("signals calendar+autocorr+statarb demo ok")` als letzte Zeile
der synthetischen Checks; der Integrationscheck druckt zusaetzlich seine eigene Zeile.

- [ ] **Step 5: Run**

Run: `python algo/signals.py` — Expected: alle `assert`s passieren, Ausgabe endet mit
`build_features Integrationscheck ok: n=<N> Zeilen` (N > 0, da Task 1 Step 5 bereits
ES=F-Daten geladen hat).

- [ ] **Step 6: Commit**

```bash
git add algo/signals.py
git commit -m "algo: signals.py Makro-Signale (VIX/DGS10/WALCL) + build_features + signal_snapshot"
```

---

## Task 6: `algo/backtest_ensemble.py` — EnsembleStrategy

**Files:**
- Modify: `algo/requirements.txt`
- Create: `algo/backtest_ensemble.py`

**Interfaces:**
- Consumes: `signals.build_features`, `signals.SIGNAL_NAMES` (Task 5), `rules.plan_trade`,
  `analyze_ohlc.Bar` (bestehend), `backtest_seasonal.load_rows` (Task 1)
- Produces: `EnsembleStrategy(Strategy)` (Klassenattribute `bias: dict`,
  `stop_buffer_pct: float = 0.1`, `intraday: bool = True`),
  `fit_model(mnq_rows, es_rows) -> LogisticRegression`,
  `bias_series(model, mnq_rows, es_rows, min_history=25) -> dict[date, str]`,
  `_passes_bias_filter(setup_side: str, day_bias: str) -> bool`

- [ ] **Step 1: `scikit-learn` zu `algo/requirements.txt` hinzufuegen**

```
scikit-learn>=1.4
```

- [ ] **Step 2: `algo/backtest_ensemble.py` schreiben**

```python
#!/usr/bin/env python3
"""RenTec-artige Ensemble-Strategie: taeglicher Bias aus Logistic Regression ueber die
Signale aus algo/signals.py, filtert die bestehende Silver-Bullet-Intraday-Regel
(algo/rules.py::plan_trade) statt sie zu ersetzen (siehe
docs/superpowers/specs/2026-08-05-algo-rentec-ensemble-design.md Phase 2). Bias-Totzone
45-55% Wahrscheinlichkeit -> "neutral" (kein Trade). `intraday=False` (siehe
algo/stress_test.py) haelt stattdessen eine Position solange der Tages-Bias in dieselbe
Richtung zeigt (Open/Close-Fallback fuer Perioden ohne Intraday-Daten).

Bei ~150 Handelstagen und 8 Features ist Overfitting trotz L2-Regularisierung ein reales
Risiko -- jedes Ergebnis hier ist eine Groessenordnungs-Schaetzung, siehe algo/validate.py
fuer die Walk-Forward-Validierung mit Per-Fold-Refit (kein statischer Fit auf allen Daten).
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

from backtesting import Strategy
from sklearn.linear_model import LogisticRegression

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from analyze_ohlc import Bar  # noqa: E402
from rules import plan_trade  # noqa: E402
from signals import build_features  # noqa: E402

BIAS_LONG_THRESHOLD = 0.55
BIAS_SHORT_THRESHOLD = 0.45


def fit_model(mnq_rows: list[dict], es_rows: list[dict]) -> LogisticRegression:
    X, y, _ = build_features(mnq_rows, es_rows)
    model = LogisticRegression(class_weight="balanced", max_iter=1000)
    model.fit(X, y)
    return model


def bias_series(model: LogisticRegression, mnq_rows: list[dict], es_rows: list[dict],
                 min_history: int = 25) -> dict[date, str]:
    """Bias je Handelstag ('long'/'short'/'neutral'). `model` muss VOR diesem Aufruf
    bereits gefittet sein (siehe algo/validate.py::on_fold_train fuer den
    Walk-Forward-Fall: pro Fold ein frischer Fit auf dem In-Sample-Anteil)."""
    X, _, target_days = build_features(mnq_rows, es_rows, min_history)
    if not X:
        return {}
    probs = model.predict_proba(X)[:, 1]
    out = {}
    for day, p in zip(target_days, probs):
        if p > BIAS_LONG_THRESHOLD:
            out[day] = "long"
        elif p < BIAS_SHORT_THRESHOLD:
            out[day] = "short"
        else:
            out[day] = "neutral"
    return out


def _passes_bias_filter(setup_side: str, day_bias: str) -> bool:
    """True wenn eine Silver-Bullet-Setup-Richtung mit dem Tages-Bias uebereinstimmt."""
    return day_bias in ("long", "short") and (setup_side == "long") == (day_bias == "long")


class EnsembleStrategy(Strategy):
    bias: dict = {}            # date -> "long"/"short"/"neutral", vor bt.run() gesetzt
    stop_buffer_pct = 0.1
    intraday = True

    def init(self):
        self._taken: set[tuple] = set()

    def next(self):
        when = self.data.index[-1]
        day_bias = self.bias.get(when.date(), "neutral")

        if not self.intraday:
            if self.position:
                if (self.position.is_long and day_bias != "long") or \
                   (self.position.is_short and day_bias != "short"):
                    self.position.close()
                return
            if day_bias == "long":
                self.buy()
            elif day_bias == "short":
                self.sell()
            return

        if self.position or day_bias == "neutral":
            return
        hist = [Bar(t, o, h, l, c) for t, o, h, l, c in
                zip(self.data.index, self.data.Open, self.data.High,
                    self.data.Low, self.data.Close)]
        setup = plan_trade(hist, when, stop_buffer_pct=self.stop_buffer_pct)
        if setup is None or not _passes_bias_filter(setup.side, day_bias):
            return
        key = (setup.t.date(), setup.window)
        if key in self._taken:
            return
        self._taken.add(key)
        if setup.side == "long":
            self.buy(limit=setup.entry, sl=setup.stop, tp=setup.target)
        else:
            self.sell(limit=setup.entry, sl=setup.stop, tp=setup.target)


def _demo() -> None:
    assert _passes_bias_filter("long", "long") is True
    assert _passes_bias_filter("short", "short") is True
    assert _passes_bias_filter("long", "short") is False
    assert _passes_bias_filter("short", "long") is False
    assert _passes_bias_filter("long", "neutral") is False
    print("backtest_ensemble _passes_bias_filter demo ok")


if __name__ == "__main__":
    _demo()
```

- [ ] **Step 3: Abhaengigkeit installieren + Selbstcheck**

Run: `pip install -r algo/requirements.txt` (installiert `scikit-learn` neu)
Run: `python algo/backtest_ensemble.py` — Expected: `backtest_ensemble _passes_bias_filter demo ok`

- [ ] **Step 4: Smoke-Test gegen echte Daten**

Run:
```bash
python -c "
from algo.backtest_seasonal import load_rows
from algo.backtest_ensemble import fit_model, bias_series
mnq, es = load_rows('MNQ'), load_rows('ES')
model = fit_model(mnq, es)
bias = bias_series(model, mnq, es)
print(f'n={len(bias)} Tage, Bias-Verteilung:',
      {k: sum(1 for v in bias.values() if v == k) for k in ('long', 'short', 'neutral')})
"
```
Expected: laeuft ohne Exception, druckt eine Bias-Verteilung mit `long`/`short`/`neutral`-Zaehlern.

- [ ] **Step 5: Commit**

```bash
git add algo/requirements.txt algo/backtest_ensemble.py
git commit -m "algo: EnsembleStrategy (Logistic-Regression-Bias filtert Silver-Bullet-Timing)"
```

---

## Task 7: `algo/validate.py` + `backtest_walkforward.py`-Refactor (mit Regressionscheck)

**Files:**
- Create: `algo/validate.py`
- Modify: `algo/backtest_walkforward.py` (kompletter Neuschreib als duenner Wrapper)

**Interfaces:**
- Produces: `validate.run(df, strategy_cls, bt_kwargs, param_name=None, param_value=None, on_fold_train=None, train_df=None)`,
  `validate.parameter_sensitivity(df, strategy_cls, param_name, candidates, bt_kwargs, baseline=None, baseline_value=None)`,
  `validate.walk_forward(df, strategy_cls, param_name, candidates, bt_kwargs, n_folds=6, on_fold_train=None) -> list[float]`,
  `validate.monte_carlo(baseline, n_sims=1000, seed=42)`

- [ ] **Step 1: Baseline-Ausgabe vor dem Refactor sichern**

Run: `python algo/backtest_walkforward.py MNQ > "$CLAUDE_JOB_DIR/tmp/walkforward_before.txt" 2>&1`

- [ ] **Step 2: `algo/validate.py` schreiben**

```python
#!/usr/bin/env python3
"""Generalisierte Walk-Forward/Monte-Carlo/Parameter-Sensitivitaet -- geloest von
SilverBulletStrategy (frueher hart in backtest_walkforward.py), damit dieselben drei
Verfahren auch fuer EnsembleStrategy (algo/validate_ensemble.py) laufen. Verhalten fuer
den SilverBulletStrategy-Fall bleibt unveraendert (siehe Regressionscheck in Task 7 des
Implementierungsplans docs/superpowers/plans/2026-08-05-algo-rentec-ensemble.md).

`on_fold_train(train_df) -> dict` ist ein optionaler Hook: statt eines Parameter-Grids wird
er vor jedem Walk-Forward-Fold aufgerufen und liefert Attribut-Name/Wert-Paare, die auf die
Strategie-Klasse gesetzt werden (z.B. ein frisch gefittetes Modell) -- ersetzt die
In-Sample-Grid-Search fuer Strategien, deren "Parameter" kein Skalar ist.
"""
from __future__ import annotations

import random

import pandas as pd
from backtesting import Backtest


def run(df: pd.DataFrame, strategy_cls, bt_kwargs: dict, param_name: str | None = None,
        param_value=None, on_fold_train=None, train_df: pd.DataFrame | None = None):
    if on_fold_train is not None and train_df is not None:
        for name, value in on_fold_train(train_df).items():
            setattr(strategy_cls, name, value)
    elif param_name is not None:
        setattr(strategy_cls, param_name, param_value)
    return Backtest(df, strategy_cls, **bt_kwargs).run()


def parameter_sensitivity(df, strategy_cls, param_name: str, candidates: list,
                           bt_kwargs: dict, baseline=None, baseline_value=None) -> None:
    print(f"1. Parameter-Sensitivitaet ({param_name})")
    print(f"   {'value':>8}  {'Trades':>7}  {'WinRate%':>9}  {'ProfitFactor':>13}  {'Expectancy%':>12}")
    for value in candidates:
        stats = baseline if (baseline is not None and value == baseline_value) else \
            run(df, strategy_cls, bt_kwargs, param_name, value)
        pf = stats["Profit Factor"]
        pf_str = f"{pf:.3f}" if pf == pf else "n/a"
        print(f"   {value!s:>8}  {stats['# Trades']:>7}  {stats['Win Rate [%]']:>9.1f}  "
              f"{pf_str:>13}  {stats['Expectancy [%]']:>12.3f}")


def slice_days(df: pd.DataFrame, days: list) -> pd.DataFrame:
    day_set = set(days)
    return df[[d in day_set for d in df.index.date]]


def walk_forward(df, strategy_cls, param_name: str | None, candidates: list | None,
                  bt_kwargs: dict, n_folds: int = 6, on_fold_train=None) -> list[float]:
    all_days = sorted(set(df.index.date))
    fold_len = len(all_days) // n_folds
    if fold_len < 2:
        print(f"2. Walk-Forward uebersprungen: nur {len(all_days)} Handelstage, "
              f"zu wenig fuer {n_folds} Folds.")
        return []
    folds = [all_days[i * fold_len:(i + 1) * fold_len] for i in range(n_folds)]
    folds[-1] = folds[-1] + all_days[n_folds * fold_len:]

    print(f"2. Walk-Forward ({n_folds} rollierende Folds, ~{fold_len} Handelstage je Fold)")
    header = param_name or "Modell"
    print(f"   {'Fold':>4}  {'IS ' + header:>16}  {'OOS Trades':>10}  "
          f"{'OOS WinRate%':>12}  {'OOS ProfitFactor':>16}  {'OOS Expectancy%':>15}")
    oos_returns = []
    for i in range(n_folds - 1):
        train, test = slice_days(df, folds[i]), slice_days(df, folds[i + 1])
        if train.empty or test.empty:
            continue
        if on_fold_train is not None:
            fold_label = "Modell"
            oos = run(test, strategy_cls, bt_kwargs, on_fold_train=on_fold_train, train_df=train)
        else:
            best_value, best_pf = candidates[0], -1.0
            for value in candidates:
                s = run(train, strategy_cls, bt_kwargs, param_name, value)
                pf = s["Profit Factor"]
                if pf == pf and pf > best_pf:
                    best_pf, best_value = pf, value
            fold_label = best_value
            oos = run(test, strategy_cls, bt_kwargs, param_name, best_value)
        oos_pf = oos["Profit Factor"]
        oos_pf_str = f"{oos_pf:.3f}" if oos_pf == oos_pf else "n/a"
        print(f"   {i + 1:>4}  {fold_label!s:>16}  {oos['# Trades']:>10}  "
              f"{oos['Win Rate [%]']:>12.1f}  {oos_pf_str:>16}  {oos['Expectancy [%]']:>15.3f}")
        if oos["# Trades"] > 0:
            oos_returns.extend(oos._trades["ReturnPct"].tolist())
    if oos_returns:
        compounded = 1.0
        for r in oos_returns:
            compounded *= (1 + r)
        print(f"   Alle Out-of-Sample-Folds zusammen: n={len(oos_returns)} Trades, "
              f"kumulierte Rendite {100 * (compounded - 1):+.2f}%")
    else:
        print("   Keine Out-of-Sample-Trades in irgendeinem Fold.")
    return oos_returns


def monte_carlo(baseline, n_sims: int = 1000, seed: int = 42) -> None:
    returns = baseline._trades["ReturnPct"].tolist()
    n = len(returns)
    print(f"3. Monte Carlo (n={n} Trades, {n_sims} Resamples der Trade-Reihenfolge)")
    if n < 10:
        print(f"   Zu wenig Trades (n={n}) fuer eine aussagekraeftige Verteilung.")
        return
    rng = random.Random(seed)
    finals, max_dds = [], []
    for _ in range(n_sims):
        sample = rng.choices(returns, k=n)
        equity = peak = 1.0
        max_dd = 0.0
        for r in sample:
            equity *= (1 + r)
            peak = max(peak, equity)
            max_dd = max(max_dd, (peak - equity) / peak)
        finals.append(equity - 1)
        max_dds.append(max_dd)
    finals.sort()
    max_dds.sort()

    def pctl(lst, p):
        return lst[int(p / 100 * (len(lst) - 1))]

    print(f"   Kumulierte Rendite:   5.%={100*pctl(finals,5):+.1f}%  "
          f"50.%={100*pctl(finals,50):+.1f}%  95.%={100*pctl(finals,95):+.1f}%")
    print(f"   Max. Drawdown:        5.%={100*pctl(max_dds,5):.1f}%  "
          f"50.%={100*pctl(max_dds,50):.1f}%  95.%={100*pctl(max_dds,95):.1f}%")
```

- [ ] **Step 3: `algo/backtest_walkforward.py` zum duennen Wrapper umschreiben**

Kompletter Dateiinhalt:

```python
#!/usr/bin/env python3
"""Duenner Wrapper um algo/validate.py fuer SilverBulletStrategy -- Verhalten/Ausgabe
identisch zur Vorgaenger-Version (Regressionscheck: siehe
docs/superpowers/plans/2026-08-05-algo-rentec-ensemble.md Task 7). Die generalisierten
Walk-Forward/Monte-Carlo/Parameter-Sensitivitaet-Funktionen leben jetzt in validate.py und
werden auch von algo/validate_ensemble.py genutzt.

Aufruf:
    python algo/backtest_walkforward.py MNQ
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from backtest_bt import load_series, SilverBulletStrategy  # noqa: E402
from validate import run, parameter_sensitivity, walk_forward, monte_carlo  # noqa: E402

STOP_BUFFER_CANDIDATES = [0.05, 0.1, 0.2, 0.3, 0.5]
BT_KWARGS = dict(cash=100_000, margin=0.05, commission=0.0002)


def main(argv=None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    symbol = args[0] if args else None
    sys.stdout.reconfigure(encoding="utf-8")

    df = load_series(symbol)
    all_days = sorted(set(df.index.date))
    print(f"{len(df)} Kerzen, {len(all_days)} Handelstage ({all_days[0]} bis {all_days[-1]})")
    print("Kleine Stichprobe -- alle Zahlen unten sind Groessenordnungen, keine belastbaren "
          "Ergebnisse (siehe Docstring).\n")

    baseline = run(df, SilverBulletStrategy, BT_KWARGS, "stop_buffer_pct", 0.1)
    parameter_sensitivity(df, SilverBulletStrategy, "stop_buffer_pct", STOP_BUFFER_CANDIDATES,
                           BT_KWARGS, baseline=baseline, baseline_value=0.1)
    print()
    walk_forward(df, SilverBulletStrategy, "stop_buffer_pct", STOP_BUFFER_CANDIDATES, BT_KWARGS)
    print()
    monte_carlo(baseline)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Regressionscheck ausfuehren**

Run: `python algo/backtest_walkforward.py MNQ > "$CLAUDE_JOB_DIR/tmp/walkforward_after.txt" 2>&1`
Run: `diff "$CLAUDE_JOB_DIR/tmp/walkforward_before.txt" "$CLAUDE_JOB_DIR/tmp/walkforward_after.txt"`

Expected: keine Differenz (Monte Carlo nutzt `seed=42`, Grid-Search ist deterministisch —
Output muss bei gleichen Daten byte-identisch sein). Bei Abweichung: Ursache im Refactor
suchen, nicht im Diff-Tool.

- [ ] **Step 5: Commit**

```bash
git add algo/validate.py algo/backtest_walkforward.py
git commit -m "algo: validate.py generalisiert (on_fold_train-Hook), backtest_walkforward.py zu duennem Wrapper"
```

---

## Task 8: `algo/validate_ensemble.py`

**Files:**
- Create: `algo/validate_ensemble.py`

**Interfaces:**
- Consumes: `validate.run/walk_forward/monte_carlo` (Task 7),
  `backtest_ensemble.EnsembleStrategy/fit_model/bias_series` (Task 6),
  `backtest_seasonal.load_rows` (Task 1), `backtest_bt.load_series` (bestehend)

- [ ] **Step 1: Datei schreiben**

```python
#!/usr/bin/env python3
"""Duenner Wrapper um algo/validate.py fuer EnsembleStrategy -- nutzt den on_fold_train-
Hook um vor jedem Walk-Forward-Fold ein neues LogisticRegression-Modell NUR auf den
In-Sample-Tagen zu fitten (kein statischer Fit auf allen Daten, siehe
docs/superpowers/specs/2026-08-05-algo-rentec-ensemble-design.md Phase 2/3).

Aufruf:
    python algo/validate_ensemble.py MNQ
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from backtest_bt import load_series  # noqa: E402
from backtest_ensemble import EnsembleStrategy, fit_model, bias_series  # noqa: E402
from backtest_seasonal import load_rows  # noqa: E402
from validate import run, walk_forward, monte_carlo  # noqa: E402

BT_KWARGS = dict(cash=100_000, margin=0.05, commission=0.0002)


def _make_fold_hook(es_rows: list[dict], mnq_rows: list[dict]):
    def on_fold_train(train_df: pd.DataFrame) -> dict:
        train_days = set(train_df.index.date)
        fold_mnq = [r for r in mnq_rows if r["day"] in train_days]
        fold_es = [r for r in es_rows if r["day"] < max(train_days, default=r["day"])]
        model = fit_model(fold_mnq, fold_es)
        return {"bias": bias_series(model, fold_mnq, fold_es)}
    return on_fold_train


def main(argv=None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    symbol = args[0] if args else None
    sys.stdout.reconfigure(encoding="utf-8")

    df = load_series(symbol)
    all_days = sorted(set(df.index.date))
    print(f"{len(df)} Kerzen, {len(all_days)} Handelstage ({all_days[0]} bis {all_days[-1]})")
    print("Kleine Stichprobe (~150 Tage, 8 Features) -- Overfitting-Risiko trotz "
          "Regularisierung, siehe backtest_ensemble.py Docstring.\n")

    mnq_rows, es_rows = load_rows("MNQ"), load_rows("ES")
    model = fit_model(mnq_rows, es_rows)
    EnsembleStrategy.bias = bias_series(model, mnq_rows, es_rows)
    EnsembleStrategy.intraday = True
    baseline = run(df, EnsembleStrategy, BT_KWARGS)
    print(baseline)
    print()
    walk_forward(df, EnsembleStrategy, None, None, BT_KWARGS,
                 on_fold_train=_make_fold_hook(es_rows, mnq_rows))
    print()
    monte_carlo(baseline)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Run gegen echte Daten**

Run: `python algo/validate_ensemble.py MNQ`
Expected: laeuft ohne Exception durch, druckt Baseline-`stats`, Walk-Forward-Tabelle,
Monte-Carlo-Perzentile — Zahlen selbst sind bei ~150 Tagen Groessenordnungs-Schaetzungen
(siehe Docstring), kein bestimmtes Ergebnis erwartet.

- [ ] **Step 3: Commit**

```bash
git add algo/validate_ensemble.py
git commit -m "algo: validate_ensemble.py (Walk-Forward mit Per-Fold-Modell-Fit)"
```

---

## Task 9: Krisenfenster-Daten fetchen

**Files:**
- Keine Code-Aenderung — nutzt `algo/fetch_yfinance.py --symbol` aus Task 1.

- [ ] **Step 1: NQ=F und ES=F fuer alle fuenf Krisenfenster laden**

```bash
python algo/fetch_yfinance.py 2008-09-01 2009-04-01 --symbol NQ=F
python algo/fetch_yfinance.py 2008-09-01 2009-04-01 --symbol ES=F
python algo/fetch_yfinance.py 2020-02-15 2020-04-16 --symbol NQ=F
python algo/fetch_yfinance.py 2020-02-15 2020-04-16 --symbol ES=F
python algo/fetch_yfinance.py 2010-05-01 2010-05-14 --symbol NQ=F
python algo/fetch_yfinance.py 2010-05-01 2010-05-14 --symbol ES=F
python algo/fetch_yfinance.py 2015-08-17 2015-08-27 --symbol NQ=F
python algo/fetch_yfinance.py 2015-08-17 2015-08-27 --symbol ES=F
python algo/fetch_yfinance.py 2018-02-01 2018-02-10 --symbol NQ=F
python algo/fetch_yfinance.py 2018-02-01 2018-02-10 --symbol ES=F
```

Expected: fuer jeden Aufruf mehrere `1d`-Dateien geschrieben (`NQ .../NQ <Datum> 1d.csv`
bzw. `ES ...`), `! 1m/5m/15m/1h: keine Daten`-Zeilen sind fuer alle Fenster erwartet (kein
Bug — yfinance-Limit fuer Intraday-Historie, siehe `fetch_yfinance.py`-Docstring).

- [ ] **Step 2: Stichprobe pruefen**

Run: `python -c "from algo.backtest_daily_patterns import find_1d_days; print(len(find_1d_days('NQ')), len(find_1d_days('ES')))"`
Expected: beide Zahlen deutlich > 0 (mind. die ~35 Handelstage der fuenf Fenster zusammen).

- [ ] **Step 3: Commit**

```bash
git add raw/marktdaten
git commit -m "algo: NQ=F/ES=F-Tagesdaten fuer 5 Krisenfenster (2008/Covid/2010/2015/2018)"
```

---

## Task 10: `algo/stress_test.py`

**Files:**
- Create: `algo/stress_test.py`

**Interfaces:**
- Consumes: `backtest_seasonal.load_rows` (Task 1), `backtest_ensemble.EnsembleStrategy/fit_model/bias_series` (Task 6)
- Produces: `WINDOWS: dict[str, tuple[date, date]]`, `load_daily_df(symbol, start, end) -> pd.DataFrame`, `run_window(name, start, end) -> None`

- [ ] **Step 1: Datei schreiben**

```python
#!/usr/bin/env python3
"""Stress-Test: EnsembleStrategy(intraday=False) gegen historische Krisenfenster, auf
NQ=F/ES=F-Tagesdaten (MNQ existiert als Instrument erst seit 2019). Verhaltens-Kennzahlen
(Drawdown, Trades) auf einem Preis-Proxy, KEINE echte MNQ-$-P&L (siehe
docs/superpowers/specs/2026-08-05-algo-rentec-ensemble-design.md Phase 4). Intraday-Daten
existieren fuer keines der fuenf Fenster (yfinance-Limit) -- deshalb laeuft
EnsembleStrategy hier durchgehend im Tages-Open/Close-Fallback-Modus.

Aufruf:
    python algo/stress_test.py                # alle 5 Fenster
    python algo/stress_test.py covid 2008      # nur bestimmte Fenster
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pandas as pd
from backtesting import Backtest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from backtest_seasonal import load_rows  # noqa: E402
from backtest_ensemble import EnsembleStrategy, fit_model, bias_series  # noqa: E402

BT_KWARGS = dict(cash=100_000, margin=0.05, commission=0.0002)

WINDOWS = {
    "2008": (date(2008, 9, 1), date(2009, 4, 1)),
    "covid": (date(2020, 2, 15), date(2020, 4, 16)),
    "flash2010": (date(2010, 5, 1), date(2010, 5, 14)),
    "china2015": (date(2015, 8, 17), date(2015, 8, 27)),
    "volmageddon2018": (date(2018, 2, 1), date(2018, 2, 10)),
}


def load_daily_df(symbol: str, start: date, end: date) -> pd.DataFrame:
    rows = [r for r in load_rows(symbol) if start <= r["day"] < end]
    return pd.DataFrame({
        "Open": [r["open"] for r in rows], "High": [r["high"] for r in rows],
        "Low": [r["low"] for r in rows], "Close": [r["close"] for r in rows],
    }, index=pd.DatetimeIndex([r["day"] for r in rows], name="t"))


def run_window(name: str, start: date, end: date) -> None:
    df = load_daily_df("NQ", start, end)
    if df.empty:
        print(f"{name}: keine NQ=F-Daten geladen (siehe Task 9) -- uebersprungen.")
        return
    px_rows = [r for r in load_rows("NQ") if r["day"] < end]
    es_rows = [r for r in load_rows("ES") if r["day"] < end]
    if len(px_rows) < 30 or len(es_rows) < 30:
        print(f"{name}: zu wenig Vorlauf-Historie fuer Signale (NQ n={len(px_rows)}, "
              f"ES n={len(es_rows)}) -- uebersprungen.")
        return
    model = fit_model(px_rows, es_rows)
    EnsembleStrategy.bias = bias_series(model, px_rows, es_rows)
    EnsembleStrategy.intraday = False
    stats = Backtest(df, EnsembleStrategy, **BT_KWARGS).run()
    pf = stats["Profit Factor"]
    pf_str = f"{pf:.3f}" if pf == pf else "n/a"
    print(f"-- {name} ({start} bis {end}, n={len(df)} Tage, NQ=F-Proxy, keine echte "
          f"MNQ-P&L) --")
    print(f"   Trades={stats['# Trades']}  Max-Drawdown={stats['Max. Drawdown [%]']:.1f}%  "
          f"Profit-Factor={pf_str}")


def main(argv=None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    sys.stdout.reconfigure(encoding="utf-8")
    names = args or list(WINDOWS)
    for name in names:
        if name not in WINDOWS:
            print(f"Unbekanntes Fenster: {name} (verfuegbar: {', '.join(WINDOWS)})")
            continue
        run_window(name, *WINDOWS[name])
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Smoke-Test gegen ein kleines Fenster**

Run: `python algo/stress_test.py flash2010`
Expected: laeuft ohne Exception durch — entweder ein Ergebnis-Block, oder eine
"zu wenig Vorlauf-Historie"-Meldung (der Flash-Crash 2010 hat nur ~65 NQ-Handelstage
Vorlauf via `load_rows("NQ")` vor `2010-05-01`, das kann je nach Task-9-Fetch-Umfang knapp
werden — beides ist ein gueltiges, erwartetes Ergebnis, kein Bug).

- [ ] **Step 3: Alle fuenf Fenster**

Run: `python algo/stress_test.py`
Expected: fuer jedes der 5 Fenster entweder ein Ergebnis-Block oder eine
"uebersprungen"-Meldung, kein Traceback.

- [ ] **Step 4: Commit**

```bash
git add algo/stress_test.py
git commit -m "algo: stress_test.py (EnsembleStrategy gegen 5 historische Krisenfenster)"
```

---

## Task 11: `algo/dashboard.py` — Live-Multi-Panel-Fenster

**Files:**
- Create: `algo/dashboard.py`

**Interfaces:**
- Consumes: `rules.plan_trade`, `analyze_ohlc.Bar` (bestehend), `backtest_bt.load_series`
  (bestehend), `backtest_seasonal.load_rows` (Task 1),
  `backtest_ensemble.fit_model/bias_series/_passes_bias_filter` (Task 6),
  `signals.signal_snapshot/SIGNAL_NAMES` (Task 5), `stress_test.WINDOWS/load_daily_df`
  (Task 10)

- [ ] **Step 1: Datei schreiben**

```python
#!/usr/bin/env python3
"""Live-Multi-Panel-Fenster fuer den Ensemble-Backtest -- eigene Simulationsschleife
(siehe docs/superpowers/specs/2026-08-05-algo-rentec-ensemble-design.md Phase 5), NICHT
die Quelle der offiziellen Kennzahlen (die kommen aus algo/validate_ensemble.py). Reines
Anschauungswerkzeug: reicht die Ergebnisse eines Backtest-Laufs Kerze fuer Kerze (oder Tag
fuer Tag bei --daily) an ein matplotlib-Fenster weiter.

Aufruf:
    python algo/dashboard.py MNQ                        # letzte 5 Handelstage, 5m-Kerzen
    python algo/dashboard.py MNQ --days 10
    python algo/dashboard.py MNQ --daily                 # 1 Frame/Tag
    python algo/dashboard.py MNQ --daily --stress covid  # Stress-Fenster aus stress_test.py
"""
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from analyze_ohlc import Bar  # noqa: E402
from rules import plan_trade  # noqa: E402
from backtest_bt import load_series  # noqa: E402
from backtest_seasonal import load_rows  # noqa: E402
from backtest_ensemble import fit_model, bias_series, _passes_bias_filter  # noqa: E402
from signals import signal_snapshot, SIGNAL_NAMES  # noqa: E402
from stress_test import WINDOWS, load_daily_df  # noqa: E402


def _snapshot(times, closes, equity, drawdown, markers, trades, wins) -> dict:
    return {"times": list(times), "closes": list(closes), "equity": list(equity),
            "drawdown": list(drawdown), "markers": list(markers), "trades": trades,
            "wins": wins}


def simulate(bars: list[Bar], bias: dict, intraday: bool) -> list[dict]:
    """Ein Frame pro Bar. Bei `intraday=False` (Stress-Fenster, Tages-Bars) haelt die
    Simulation eine Position solange der Bias uebereinstimmt (analog
    EnsembleStrategy.next()); bei `intraday=True` nutzt sie plan_trade() + Bias-Filter."""
    times, closes, equity, drawdown, markers = [], [], [1.0], [0.0], []
    trades = wins = 0
    position = None  # (side, entry, stop, target) fuer intraday, oder "long"/"short" fuer daily
    peak = 1.0
    taken = set()
    frames = []

    for i, bar in enumerate(bars):
        hist = bars[:i + 1]
        times.append(bar.t)
        closes.append(bar.c)
        day_bias = bias.get(bar.t.date(), "neutral")

        if intraday:
            if position is not None:
                side, entry, stop, target = position
                hit_stop = bar.l <= stop if side == "long" else bar.h >= stop
                hit_target = bar.h >= target if side == "long" else bar.l <= target
                if hit_stop or hit_target:
                    exit_price = stop if hit_stop else target
                    ret = ((exit_price - entry) / entry if side == "long"
                           else (entry - exit_price) / entry)
                    equity.append(equity[-1] * (1 + ret))
                    trades += 1
                    wins += 1 if ret > 0 else 0
                    markers.append((bar.t, exit_price, "exit"))
                    position = None
                else:
                    equity.append(equity[-1])
            else:
                equity.append(equity[-1])
                if day_bias in ("long", "short"):
                    setup = plan_trade(hist, bar.t)
                    key = (setup.t.date(), setup.window) if setup else None
                    if (setup is not None and key not in taken
                            and _passes_bias_filter(setup.side, day_bias)):
                        taken.add(key)
                        position = (setup.side, setup.entry, setup.stop, setup.target)
                        markers.append((bar.t, setup.entry, setup.side))
        else:
            if position is not None and position != day_bias:
                ret = ((bar.c - bar.o) / bar.o if position == "long"
                       else (bar.o - bar.c) / bar.o)
                equity.append(equity[-1] * (1 + ret))
                trades += 1
                wins += 1 if ret > 0 else 0
                markers.append((bar.t, bar.c, "exit"))
                position = None
            elif position is not None:
                ret = (bar.c - bar.o) / bar.o if position == "long" else (bar.o - bar.c) / bar.o
                equity.append(equity[-1] * (1 + ret))
            else:
                equity.append(equity[-1])
            if position is None and day_bias in ("long", "short"):
                position = day_bias
                markers.append((bar.t, bar.o, day_bias))

        peak = max(peak, equity[-1])
        drawdown.append((peak - equity[-1]) / peak)
        frames.append(_snapshot(times, closes, equity, drawdown, markers, trades, wins))
    return frames


def render(frames: list[dict], bias: dict, snapshot: dict) -> None:
    fig, (ax_price, ax_equity, ax_dd, ax_text) = plt.subplots(
        4, 1, figsize=(11, 9), gridspec_kw={"height_ratios": [3, 2, 1, 1.5]})
    fig.suptitle("Ensemble-Backtest -- Live-Replay (Anschauung, keine offizielle Kennzahl)")

    def draw(i):
        for ax in (ax_price, ax_equity, ax_dd, ax_text):
            ax.clear()
        f = frames[i]
        ax_price.plot(f["times"], f["closes"], color="tab:blue", linewidth=1)
        for t, price, kind in f["markers"]:
            color, marker = {"long": ("green", "^"), "short": ("red", "v")}.get(kind, ("black", "x"))
            ax_price.scatter([t], [price], marker=marker, color=color, s=60, zorder=3)
        ax_price.set_title("Preis + Entries/Exits")

        ax_equity.plot(f["equity"], color="tab:green")
        ax_equity.set_title("Equity-Kurve (relativ, Start=1.0)")

        ax_dd.plot(f["drawdown"], color="tab:red")
        ax_dd.set_title("Drawdown")

        day = f["times"][-1].date() if f["times"] else None
        day_bias = bias.get(day, "neutral") if day else "neutral"
        sig = snapshot.get(day, {})
        sig_lines = [f"  {name}: {'+' if sig.get(name, 0) > 0.05 else '-' if sig.get(name, 0) < -0.05 else 'o'}"
                     for name in SIGNAL_NAMES]
        win_rate = 100 * f["wins"] / f["trades"] if f["trades"] else 0.0
        lines = [f"Tages-Bias: {day_bias}", f"Trades: {f['trades']}  WinRate: {win_rate:.1f}%",
                 "Signale:"] + sig_lines
        ax_text.axis("off")
        ax_text.text(0.0, 1.0, "\n".join(lines), fontsize=9, va="top", family="monospace")

    anim = FuncAnimation(fig, draw, frames=len(frames), interval=30, repeat=False)
    plt.tight_layout()
    plt.show()
    return anim


def main(argv=None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("symbol", nargs="?", default=None)
    ap.add_argument("--days", type=int, default=5)
    ap.add_argument("--daily", action="store_true")
    ap.add_argument("--stress", default=None, help="Fenstername aus stress_test.WINDOWS")
    a = ap.parse_args(args)
    sys.stdout.reconfigure(encoding="utf-8")

    mnq_symbol = "NQ" if a.stress else "MNQ"
    mnq_rows = load_rows(mnq_symbol)
    es_rows = load_rows("ES")
    if len(mnq_rows) < 30 or len(es_rows) < 10:
        print(f"Zu wenig Daten fuer ein Dashboard (MNQ/NQ n={len(mnq_rows)}, ES n={len(es_rows)}).")
        return 1
    model = fit_model(mnq_rows, es_rows)
    bias = bias_series(model, mnq_rows, es_rows)
    snapshot = signal_snapshot(mnq_rows, es_rows)

    if a.stress:
        if a.stress not in WINDOWS:
            print(f"Unbekanntes Stress-Fenster: {a.stress} (verfuegbar: {', '.join(WINDOWS)})")
            return 1
        start, end = WINDOWS[a.stress]
        df = load_daily_df("NQ", start, end)
        bars = [Bar(t, o, h, l, c) for t, o, h, l, c in
                zip(df.index, df.Open, df.High, df.Low, df.Close)]
        frames = simulate(bars, bias, intraday=False)
    else:
        df = load_series(a.symbol)
        all_days = sorted(set(df.index.date))[-a.days:]
        df = df[[d in set(all_days) for d in df.index.date]]
        bars = [Bar(t, o, h, l, c) for t, o, h, l, c in
                zip(df.index, df.Open, df.High, df.Low, df.Close)]
        frames = simulate(bars, bias, intraday=not a.daily)

    if not frames:
        print("Keine Bars im gewaehlten Zeitraum -- nichts zu zeigen.")
        return 1
    render(frames, bias, snapshot)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Manueller Rauchtest (visuell, kein `assert`-Test — Dashboard visualisiert nur
  bereits getestete Logik aus Task 6/7, siehe Global Constraints)**

Run: `python algo/dashboard.py MNQ --days 3`
Erwartet: ein matplotlib-Fenster oeffnet sich, 4 Panels wie oben beschrieben, Animation
laeuft durch die Kerzen der letzten 3 Handelstage ohne Exception. Fenster manuell schliessen.

Run: `python algo/dashboard.py MNQ --daily --stress covid`
Erwartet: Fenster oeffnet sich mit Tages-Cadence-Replay des Covid-Crash-Fensters (NQ=F-Proxy).

- [ ] **Step 3: Commit**

```bash
git add algo/dashboard.py
git commit -m "algo: dashboard.py (Live-Multi-Panel-Replay, matplotlib.animation)"
```

---

## Self-Review-Notizen (bereits eingearbeitet)

- **Spec-Abdeckung:** Phase 1 -> Task 1-5, Phase 2 -> Task 6, Phase 3 -> Task 7-8,
  Phase 4 -> Task 9-10, Phase 5 -> Task 11. Alle Spec-Abschnitte haben eine Aufgabe.
- **Luecke gefunden und geschlossen:** die Spec ordnete die `fetch_yfinance.py`-
  Generalisierung Phase 4 zu, aber Phase 1 (Stat-Arb-Signal) braucht ES=F-Daten schon fuer
  den Haupt-Backtest-Zeitraum, nicht erst fuer die Krisenfenster — deshalb liegt die
  Generalisierung + `find_1d_days`/`load_rows`-Symbol-Parameter in Task 1 (vor allen
  Signal-Tasks), Task 9 nutzt dieselbe generalisierte Funktion nur fuer die Krisenfenster.
- **Typkonsistenz geprueft:** `bias: dict[date, str]` durchgehend gleiche Form in
  `backtest_ensemble.py`, `validate_ensemble.py`, `stress_test.py`, `dashboard.py`.
  `SIGNAL_NAMES`-Reihenfolge identisch in `signals.py::_row_features` und
  `dashboard.py::render`. `_passes_bias_filter` einmal definiert (backtest_ensemble.py),
  von `dashboard.py` importiert statt dupliziert.
