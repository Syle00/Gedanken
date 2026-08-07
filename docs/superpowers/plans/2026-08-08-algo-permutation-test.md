# Bar-Permutationstest (MCPT) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `algo/permutation_test.py`, a strategy-agnostic module implementing Timothy
Masters' Monte-Carlo bar-permutation test (in-sample + walk-forward variants) with a live,
`dashboard.py`-style animated histogram, wired into `algo/selfcheck.py`.

**Architecture:** Three public functions (`get_permutation`, `in_sample_test`,
`walk_forward_permutation_test`) plus two private helpers (`_optimize`,
`_walk_forward_returns`) that reuse `algo/validate.py::run()` for single-config backtests
instead of reimplementing the `backtesting.Backtest` call. A shared `_run_with_live_view()`
helper drives the `FuncAnimation`-based histogram for both public test functions, matching
`algo/dashboard.py`'s existing pattern (precompute-free, one animation frame = one permutation).

**Tech Stack:** Python, `pandas`, `numpy`, `backtesting` (existing dependency), `matplotlib`
(`matplotlib.animation.FuncAnimation`, already used by `dashboard.py`).

## Global Constraints

- No lookahead: `get_permutation()` only ever transforms a DataFrame already handed to it —
  never touches live/future data (spec: "Fehlerbehandlung").
- Terminology: always "Bar-Permutationstest" / "MCPT" in code, comments, and docs — never bare
  "Monte Carlo" (that name is taken by `validate.py`'s trade-order resampling).
- `validate.py` is not modified. All reuse happens via import (`from validate import run as
  bt_run`), no changes to its existing functions or output.
- `live=True` is the default for both public test functions; `selfcheck.py`'s demo calls always
  pass `live=False` explicitly — a self-check must never pop a window or block on `plt.show()`.
- Single-market scope only (no multi-market permutation) — matches the approved spec.
- Every new function gets covered by the module's own `demo()`, wired into
  `algo/selfcheck.py::CHECKS`, following the existing `pnl.py`/`rules.py`/`signals.py` pattern
  (assert-based, no pytest — this codebase has no `test_*.py` files).

---

## File Structure

- **Create:** `algo/permutation_test.py` — the entire feature (bar permutation, in-sample test,
  walk-forward permutation test, live view, `demo()`).
- **Modify:** `algo/selfcheck.py` — add `permutation_test` to the `CHECKS` list.
- **Modify:** `algo/README.md` — new module section.
- **Modify:** `algo/PLAN.md` — log entry.

No other files change. This is a single self-contained module — one task-chain, no
decomposition into separate plans needed.

---

### Task 1: Bar permutation core (`get_permutation`)

**Files:**
- Create: `algo/permutation_test.py`
- Modify: `algo/selfcheck.py` (import + CHECKS entry — done at the end in Task 6, not here)

**Interfaces:**
- Produces: `get_permutation(df: pd.DataFrame, start_index: int = 0, seed: int | None = None) -> pd.DataFrame`
  — input/output both have columns `Open, High, Low, Close` and a `DatetimeIndex`, same shape
  and index as `df`. Rows before `start_index` are byte-identical to `df`. Used by every later
  task.

- [ ] **Step 1: Write the module docstring, imports, and `get_permutation()`**

```python
#!/usr/bin/env python3
"""Bar-Permutationstest (MCPT) nach Timothy Masters -- siehe
docs/superpowers/specs/2026-08-08-algo-permutation-test-design.md und raw/md.md (Quelle).

Strategie-agnostisch wie validate.py, aber ein eigenstaendiges viertes Validierungsverfahren
(nicht "Monte Carlo" -- der Name ist in validate.py fuers Trade-Reihenfolge-Resampling
vergeben). get_permutation() mischt Preis-Bars statistik-erhaltend (gleicher Mittelwert/
Standardabweichung/Skew/Kurtosis der Close-zu-Close-Returns wie im Original), in_sample_test()
und walk_forward_permutation_test() optimieren eine Strategie wiederholt auf solchen
Permutationen, um zu schaetzen, wie viel des In-Sample-Erfolgs auf Data-Mining-Bias beruht statt
auf echte Muster.

Aufruf (Selbstcheck):
    python algo/permutation_test.py
"""
from __future__ import annotations

import random

import numpy as np
import pandas as pd

from validate import run as bt_run


def get_permutation(df: pd.DataFrame, start_index: int = 0, seed: int | None = None) -> pd.DataFrame:
    """Mischt Bars ab `start_index` statistik-erhaltend (Masters' Algorithmus): Log-Preise
    relativ zum eigenen Open ausdruecken (High/Low/Close-Offset + Gap zum Vor-Close), beide
    Gruppen unabhaengig voneinander permutieren, daraus neue OHLC-Bars sequenziell
    rekonstruieren. Alles vor `start_index` bleibt unveraendert.

    Da dieselbe Multimenge an relativen Werten nur umsortiert wird, bleiben Summe (-> letzter
    Close) und Verteilungskennzahlen (Mittelwert/Std/Skew/Kurtosis der Returns) erhalten --
    nur der Pfad dazwischen ist neu."""
    n = len(df)
    log_o = np.log(df["Open"].to_numpy())
    log_h = np.log(df["High"].to_numpy())
    log_l = np.log(df["Low"].to_numpy())
    log_c = np.log(df["Close"].to_numpy())

    rel_h = log_h - log_o
    rel_l = log_l - log_o
    rel_c = log_c - log_o
    gap = np.empty(n)
    gap[0] = 0.0
    gap[1:] = log_o[1:] - log_c[:-1]

    rng = random.Random(seed)
    idx_intrabar = list(range(start_index, n))
    idx_gaps = list(range(start_index, n))
    rng.shuffle(idx_intrabar)
    rng.shuffle(idx_gaps)

    out_o = log_o.copy()
    out_h = log_h.copy()
    out_l = log_l.copy()
    out_c = log_c.copy()

    prev_close = log_c[start_index - 1] if start_index > 0 else log_o[0]
    for pos, (gi, ii) in enumerate(zip(idx_gaps, idx_intrabar)):
        i = start_index + pos
        o = prev_close if i == 0 else prev_close + gap[gi]
        out_o[i] = o
        out_h[i] = o + rel_h[ii]
        out_l[i] = o + rel_l[ii]
        out_c[i] = o + rel_c[ii]
        prev_close = out_c[i]

    return pd.DataFrame({
        "Open": np.exp(out_o), "High": np.exp(out_h),
        "Low": np.exp(out_l), "Close": np.exp(out_c),
    }, index=df.index)
```

- [ ] **Step 2: Write `demo()` for `get_permutation()` and a `__main__` block**

```python
def demo() -> None:
    """Selbstcheck: Permutation erhaelt Shape/Spalten/Index, laesst Daten vor start_index
    unveraendert, und bewahrt den letzten Close (Summeninvariante einer reinen Umsortierung)."""
    rng = np.random.default_rng(0)
    n = 200
    idx = pd.date_range("2026-01-01 09:30", periods=n, freq="5min")
    price = 100 + np.cumsum(rng.normal(0, 0.5, n))
    close = price + rng.normal(0, 0.1, n)
    open_ = np.roll(close, 1)
    open_[0] = price[0]
    high = np.maximum(price, np.maximum(open_, close)) + rng.uniform(0, 0.3, n)
    low = np.minimum(price, np.minimum(open_, close)) - rng.uniform(0, 0.3, n)
    df = pd.DataFrame({"Open": open_, "High": high, "Low": low, "Close": close}, index=idx)

    perm = get_permutation(df, seed=1)
    assert perm.shape == df.shape
    assert list(perm.columns) == list(df.columns)
    assert perm.index.equals(df.index)
    assert abs(perm["Open"].iloc[0] - df["Open"].iloc[0]) < 1e-9
    assert abs(perm["Close"].iloc[-1] - df["Close"].iloc[-1]) < 1e-6

    start = 100
    perm2 = get_permutation(df, start_index=start, seed=2)
    pd.testing.assert_frame_equal(perm2.iloc[:start], df.iloc[:start])
    assert not perm2.iloc[start:].equals(df.iloc[start:])

    print("get_permutation demo ok")


if __name__ == "__main__":
    demo()
```

- [ ] **Step 3: Run to verify it fails before the code above existed**

This step documents intent for TDD ordering: write Step 2's `demo()` body first (referencing
`get_permutation`), run it, confirm `NameError: name 'get_permutation' is not defined`, THEN add
Step 1's implementation above `demo()`. In practice, write both steps in the file in the order
shown (Step 1 then Step 2) and run once — either order proves the same thing once both are
present. Run:

```bash
python "algo/permutation_test.py"
```

Expected before Step 1 exists: `NameError`. After adding Step 1: proceeds to Step 4's expected
output.

- [ ] **Step 4: Run to verify it passes**

Run: `python "algo/permutation_test.py"`
Expected: `get_permutation demo ok` printed, exit code 0.

- [ ] **Step 5: Commit**

```bash
git add algo/permutation_test.py
git commit -m "feat(algo): permutation_test.py -- Bar-Permutationsalgorithmus (MCPT-Basis)"
```

---

### Task 2: `_optimize()` helper + `in_sample_test()` (batch mode)

**Files:**
- Modify: `algo/permutation_test.py`

**Interfaces:**
- Consumes: `get_permutation` (Task 1), `bt_run` (= `validate.run`, already imported).
- Produces:
  - `_optimize(df, strategy_cls, bt_kwargs, param_name, candidates, on_fold_train) -> tuple[object | None, dict]`
    — `(chosen_param_value_or_None, stats)`. `stats` is a `backtesting.Backtest.run()` result
    (dict-like, supports `stats["Profit Factor"]`, `stats["# Trades"]`, `stats._trades`).
  - `in_sample_test(df, strategy_cls, bt_kwargs, param_name=None, candidates=None,
    on_fold_train=None, objective="Profit Factor", n_perms=1000, seed=42, live=True,
    plot_path=None) -> float` — returns the P-value (`nan` if fewer than 1 valid permutation).
    Used later by `walk_forward_permutation_test`'s demo only indirectly (no direct
    dependency), but the signature is the template Task 4 mirrors.

- [ ] **Step 1: Add `_optimize()` above `demo()`**

```python
def _optimize(df: pd.DataFrame, strategy_cls, bt_kwargs: dict, param_name: str | None,
              candidates: list | None, on_fold_train) -> tuple:
    """Ein Grid-Search-Schritt (gleiche Auswahllogik wie validate.walk_forward()'s Inline-Loop,
    hier als wiederverwendbare Funktion): bei on_fold_train wird kein Skalar-Parameter gewaehlt
    (das Modell fittet sich selbst), sonst wird der Kandidat mit dem besten In-Sample-Profit-
    Factor zurueckgegeben."""
    if on_fold_train is not None:
        return None, bt_run(df, strategy_cls, bt_kwargs, on_fold_train=on_fold_train, train_df=df)
    best_value, best_stats, best_pf = candidates[0], None, -1.0
    for value in candidates:
        stats = bt_run(df, strategy_cls, bt_kwargs, param_name, value)
        pf = stats["Profit Factor"]
        if pf == pf and pf > best_pf:
            best_pf, best_value, best_stats = pf, value, stats
    return best_value, best_stats
```

- [ ] **Step 2: Add `in_sample_test()` (batch/`live=False` path only for now)**

```python
def in_sample_test(df: pd.DataFrame, strategy_cls, bt_kwargs: dict, param_name: str | None = None,
                    candidates: list | None = None, on_fold_train=None,
                    objective: str = "Profit Factor", n_perms: int = 1000, seed: int = 42,
                    live: bool = True, plot_path: str | None = None) -> float:
    _, real_stats = _optimize(df, strategy_cls, bt_kwargs, param_name, candidates, on_fold_train)
    real_value = real_stats[objective]
    values: list[float] = []

    def step(i: int) -> None:
        perm = get_permutation(df, seed=seed + i)
        _, stats = _optimize(perm, strategy_cls, bt_kwargs, param_name, candidates, on_fold_train)
        v = stats[objective]
        if v == v:  # NaN-Check ohne math-Import
            values.append(v)

    for i in range(n_perms):  # live-Zweig kommt in Task 3
        step(i)

    p_value = (sum(v >= real_value for v in values) / len(values)) if values else float("nan")
    note = "" if len(values) >= 10 else f"  (WARNUNG: nur {len(values)} gueltige Permutationen)"
    print(f"In-Sample-Permutationstest: real {objective}={real_value:.3f}, "
          f"P-Wert={100*p_value:.1f}% (n={len(values)}/{n_perms} Permutationen){note}")
    return p_value
```

- [ ] **Step 3: Extend `demo()` with an in-sample-test check**

Add a minimal `backtesting.Strategy` and synthetic multi-day series to `demo()` (this fixture is
reused by Task 4's demo extension too, so define it once):

```python
def _demo_strategy_and_df():
    from backtesting import Strategy
    from backtesting.lib import crossover

    class SmaCross(Strategy):
        n = 3

        def init(self):
            close = pd.Series(self.data.Close)
            self.sma = self.I(lambda: close.rolling(self.n).mean())

        def next(self):
            if crossover(self.data.Close, self.sma):
                self.buy()
            elif crossover(self.sma, self.data.Close):
                self.sell()

    rng = np.random.default_rng(7)
    n_days, bars_per_day = 12, 20
    idx = pd.date_range("2026-01-01 09:30", periods=n_days * bars_per_day, freq="5min")
    price = 100 + np.cumsum(rng.normal(0, 0.5, len(idx)))
    close = price + rng.normal(0, 0.1, len(idx))
    open_ = np.roll(close, 1)
    open_[0] = price[0]
    high = np.maximum(price, np.maximum(open_, close)) + rng.uniform(0, 0.3, len(idx))
    low = np.minimum(price, np.minimum(open_, close)) - rng.uniform(0, 0.3, len(idx))
    df = pd.DataFrame({"Open": open_, "High": high, "Low": low, "Close": close}, index=idx)
    bt_kwargs = dict(cash=100_000, margin=0.05, commission=0.0002)
    return SmaCross, df, bt_kwargs
```

Insert this call at the top of `demo()`, and append after the existing `get_permutation` checks:

```python
    SmaCross, sdf, bt_kwargs = _demo_strategy_and_df()
    p = in_sample_test(sdf, SmaCross, bt_kwargs, param_name="n", candidates=[2, 3, 5],
                        n_perms=5, seed=1, live=False)
    assert p != p or 0.0 <= p <= 1.0
    print("in_sample_test demo ok")
```

- [ ] **Step 4: Run to verify it fails, then passes**

```bash
python "algo/permutation_test.py"
```
Before Step 1/2 exist: `NameError`. After: prints `get_permutation demo ok`, `in_sample_test
demo ok`, exit code 0.

- [ ] **Step 5: Commit**

```bash
git add algo/permutation_test.py
git commit -m "feat(algo): permutation_test.py -- in_sample_test() Batch-Modus"
```

---

### Task 3: Live-animierte Histogramm-Ansicht

**Files:**
- Modify: `algo/permutation_test.py`

**Interfaces:**
- Consumes: `step(i)` closures as defined inside `in_sample_test`/`walk_forward_permutation_test`.
- Produces: `_run_with_live_view(step_fn, n_perms, live, title, real_value_getter, plot_path,
  values) -> None`. `real_value_getter` is a zero-arg callable (not a plain float) so the
  walk-forward variant in Task 4 — whose "real" value is only known after its own real run,
  identical call shape — can share this helper unchanged.

- [ ] **Step 1: Add `_run_with_live_view()` above `in_sample_test()`**

```python
def _run_with_live_view(step_fn, n_perms: int, live: bool, title: str, real_value: float,
                         plot_path: str | None, values: list) -> None:
    """Ein FuncAnimation-Frame = eine Permutation: step_fn(i) berechnet Permutation i UND
    haengt ihren Objective-Wert an `values` an (Seiteneffekt, siehe step()-Closures in
    in_sample_test/walk_forward_permutation_test) -- kein Vorab-Rechnen wie in dashboard.py,
    weil hier die Berechnung selbst der Fortschritt ist, den man live sehen will."""
    if live:
        import matplotlib.pyplot as plt
        from matplotlib.animation import FuncAnimation

        fig, ax = plt.subplots()

        def draw(i):
            step_fn(i)
            ax.clear()
            if values:
                ax.hist(values, bins=30, color="tab:blue")
                ax.axvline(real_value, color="tab:red", linewidth=2)
            ax.set_title(f"{title} -- {i + 1}/{n_perms}")

        anim = FuncAnimation(fig, draw, frames=n_perms, interval=1, repeat=False)
        plt.tight_layout()
        plt.show()
    else:
        for i in range(n_perms):
            step_fn(i)

    if plot_path:
        import matplotlib.pyplot as plt

        fig2, ax2 = plt.subplots()
        if values:
            ax2.hist(values, bins=30, color="tab:blue")
            ax2.axvline(real_value, color="tab:red", linewidth=2)
        ax2.set_title(title)
        fig2.savefig(plot_path)
        plt.close(fig2)
```

- [ ] **Step 2: Wire `in_sample_test()`'s loop through the new helper**

Replace the `for i in range(n_perms): step(i)` line from Task 2 Step 2 with:

```python
    _run_with_live_view(step, n_perms, live, f"In-Sample-Permutationstest ({objective})",
                         real_value, plot_path, values)
```

- [ ] **Step 3: Extend `demo()` with a `plot_path` check (still `live=False`, self-checks never open a window)**

```python
    import tempfile
    from pathlib import Path as _Path

    with tempfile.TemporaryDirectory() as tmp:
        png = str(_Path(tmp) / "is_test.png")
        p2 = in_sample_test(sdf, SmaCross, bt_kwargs, param_name="n", candidates=[2, 3, 5],
                             n_perms=5, seed=1, live=False, plot_path=png)
        assert _Path(png).exists()
    assert p2 != p2 or 0.0 <= p2 <= 1.0
    print("in_sample_test plot_path demo ok")
```

- [ ] **Step 4: Run to verify it fails, then passes**

```bash
python "algo/permutation_test.py"
```
Before Step 1/2: `NameError` (or old behavior without plot_path support, so the new assert on
`_Path(png).exists()` fails). After: all demo lines print `ok`, exit code 0.

- [ ] **Step 5: Commit**

```bash
git add algo/permutation_test.py
git commit -m "feat(algo): permutation_test.py -- Live-Histogramm-Animation + PNG-Export"
```

---

### Task 4: `_walk_forward_returns()` + `walk_forward_permutation_test()`

**Files:**
- Modify: `algo/permutation_test.py`

**Interfaces:**
- Consumes: `get_permutation` (Task 1), `_optimize` (Task 2), `bt_run` (import),
  `_run_with_live_view` (Task 3).
- Produces: `walk_forward_permutation_test(df, strategy_cls, bt_kwargs, train_window_days,
  param_name=None, candidates=None, on_fold_train=None, n_perms=200, seed=42, live=True,
  plot_path=None) -> float` — P-value, or `nan` (with a printed skip message) if `df` has fewer
  than `2 * train_window_days` trading days.

- [ ] **Step 1: Add `_profit_factor()` and `_walk_forward_returns()`**

```python
def _profit_factor(returns: list) -> float:
    gains = sum(r for r in returns if r > 0)
    losses = -sum(r for r in returns if r < 0)
    return gains / losses if losses > 0 else float("nan")


def _walk_forward_returns(df: pd.DataFrame, strategy_cls, bt_kwargs: dict,
                           train_window_days: int, param_name, candidates, on_fold_train):
    """Rollierende Folds der Groesse train_window_days (Trainings-Fold i -> Test-Fold i+1),
    gleiche Fold-Bildung wie validate.walk_forward(), aber ohne dessen Text-Ausgabe -- die
    laeuft hier bis zu n_perms-mal pro Aufruf und wuerde die Konsole fluten. Gibt None zurueck,
    wenn weniger als 2 Folds moeglich sind (Signal fuer den Skip-Pfad im Aufrufer)."""
    all_days = sorted(set(df.index.date))
    n_folds = len(all_days) // train_window_days
    if n_folds < 2:
        return None
    folds = [all_days[i * train_window_days:(i + 1) * train_window_days] for i in range(n_folds)]
    folds[-1] = folds[-1] + all_days[n_folds * train_window_days:]

    returns: list = []
    for i in range(n_folds - 1):
        train_set, test_set = set(folds[i]), set(folds[i + 1])
        train = df[[d in train_set for d in df.index.date]]
        test = df[[d in test_set for d in df.index.date]]
        if train.empty or test.empty:
            continue
        if on_fold_train is not None:
            oos = bt_run(test, strategy_cls, bt_kwargs, on_fold_train=on_fold_train, train_df=train)
        else:
            value, _ = _optimize(train, strategy_cls, bt_kwargs, param_name, candidates, None)
            oos = bt_run(test, strategy_cls, bt_kwargs, param_name, value)
        if oos["# Trades"] > 0:
            returns.extend(oos._trades["ReturnPct"].tolist())
    return returns
```

- [ ] **Step 2: Add `walk_forward_permutation_test()`**

```python
def walk_forward_permutation_test(df: pd.DataFrame, strategy_cls, bt_kwargs: dict,
                                   train_window_days: int, param_name: str | None = None,
                                   candidates: list | None = None, on_fold_train=None,
                                   n_perms: int = 200, seed: int = 42, live: bool = True,
                                   plot_path: str | None = None) -> float:
    real_returns = _walk_forward_returns(df, strategy_cls, bt_kwargs, train_window_days,
                                          param_name, candidates, on_fold_train)
    if real_returns is None:
        n_days = len(sorted(set(df.index.date)))
        print(f"Walk-Forward-Permutationstest uebersprungen: nur {n_days} Handelstage, "
              f"train_window_days={train_window_days} ergibt < 2 Folds.")
        return float("nan")
    real_pf = _profit_factor(real_returns)
    values: list = []

    def step(i: int) -> None:
        perm = get_permutation(df, start_index=train_window_days, seed=seed + i)
        returns = _walk_forward_returns(perm, strategy_cls, bt_kwargs, train_window_days,
                                         param_name, candidates, on_fold_train)
        if returns:
            pf = _profit_factor(returns)
            if pf == pf:
                values.append(pf)

    title = "Walk-Forward-Permutationstest (Profit Factor)"
    _run_with_live_view(step, n_perms, live, title, real_pf, plot_path, values)

    p_value = (sum(v >= real_pf for v in values) / len(values)) if values else float("nan")
    note = "" if len(values) >= 10 else f"  (WARNUNG: nur {len(values)} gueltige Permutationen)"
    print(f"{title}: real Profit Factor={real_pf:.3f}, P-Wert={100*p_value:.1f}% "
          f"(n={len(values)}/{n_perms} Permutationen){note}")
    return p_value
```

- [ ] **Step 3: Extend `demo()` with walk-forward checks (pass path + skip path)**

```python
    p3 = walk_forward_permutation_test(sdf, SmaCross, bt_kwargs, train_window_days=3,
                                        param_name="n", candidates=[2, 3, 5], n_perms=3,
                                        seed=1, live=False)
    assert p3 != p3 or 0.0 <= p3 <= 1.0

    p4 = walk_forward_permutation_test(sdf.iloc[:20], SmaCross, bt_kwargs,
                                        train_window_days=30, param_name="n",
                                        candidates=[2, 3], n_perms=2, live=False)
    assert p4 != p4  # zu wenig Handelstage -> Skip -> nan
    print("walk_forward_permutation_test demo ok")
```

- [ ] **Step 4: Run to verify it fails, then passes**

```bash
python "algo/permutation_test.py"
```
Before Step 1/2: `NameError`. After: all `demo ok` lines print, exit code 0.

- [ ] **Step 5: Commit**

```bash
git add algo/permutation_test.py
git commit -m "feat(algo): permutation_test.py -- walk_forward_permutation_test()"
```

---

### Task 5: `selfcheck.py`-Integration

**Files:**
- Modify: `algo/selfcheck.py:20-24` (imports), `algo/selfcheck.py:77-84` (`CHECKS` list)

**Interfaces:**
- Consumes: `algo.permutation_test.demo` (Task 1-4).
- Produces: `python algo/selfcheck.py` exercises `permutation_test` alongside the existing six
  checks; no new public interface.

- [ ] **Step 1: Add the import**

In `algo/selfcheck.py`, after line 24 (`from backtest_common import demo as
backtest_common_demo`):

```python
from permutation_test import demo as permutation_test_demo  # noqa: E402
```

- [ ] **Step 2: Add to `CHECKS`**

In `algo/selfcheck.py`, change:

```python
CHECKS = [
    ("pnl", pnl_demo),
    ("rules", rules_demo),
    ("signals", signals_demo),
    ("backtest_ensemble", ensemble_demo),
    ("backtest_common", backtest_common_demo),
    ("dedup", _results_demo),
]
```

to:

```python
CHECKS = [
    ("pnl", pnl_demo),
    ("rules", rules_demo),
    ("signals", signals_demo),
    ("backtest_ensemble", ensemble_demo),
    ("backtest_common", backtest_common_demo),
    ("dedup", _results_demo),
    ("permutation_test", permutation_test_demo),
]
```

- [ ] **Step 3: Run the full self-check**

```bash
python algo/selfcheck.py
```
Expected: `[OK]   permutation_test` among the printed lines, `Alle 7 Selbstchecks bestanden.`,
exit code 0. If it fails, fix `permutation_test.py` (not `selfcheck.py`) before continuing.

- [ ] **Step 4: Commit**

```bash
git add algo/selfcheck.py
git commit -m "test(algo): selfcheck.py -- permutation_test.py eingebunden"
```

---

### Task 6: Doku (`README.md` + `PLAN.md`)

**Files:**
- Modify: `algo/README.md` (insert new section after the `validate.py` section, i.e. after the
  line `**Bekannte Grenzen:** Kleine Stichprobe (siehe algo/PLAN.md) -- alle Zahlen sind
  Groessenordnungen, keine belastbaren Ergebnisse, bis mehr Handelstage vorliegen.` and before
  `## \`stress_test.py\` -- Historische Krisenfenster`)
- Modify: `algo/PLAN.md` (append log entry)

**Interfaces:** None — documentation only, no code.

- [ ] **Step 1: Insert README section**

```markdown
## `permutation_test.py` -- Bar-Permutationstest (MCPT nach Timothy Masters)

**Was:** Ein viertes, unabhaengiges Validierungsverfahren neben Walk-Forward/Parameter-
Sensitivitaet/Trade-Order-Resampling (`validate.py`): Preis-Bars werden statistik-erhaltend
gemischt (`get_permutation()`), die Strategie wird auf den Permutationen neu optimiert
(`in_sample_test()`, `walk_forward_permutation_test()`), und der Anteil der Permutationen mit
gleich gutem oder besserem Ergebnis liefert einen P-Wert -- eine Schaetzung, wie viel des
In-Sample-Erfolgs auf Data-Mining-Bias statt auf echte Muster zurueckgeht.
**Wie:** `get_permutation()` mischt Log-relative Intrabar-Werte und Gaps unabhaengig
voneinander (Summeninvariante -> letzter Close bleibt gleich). `in_sample_test()` mischt die
gesamten Daten, `walk_forward_permutation_test()` nur den Zeitraum nach dem ersten
Trainings-Fold (`start_index=train_window_days`). Beide zeigen standardmaessig
(`live=True`) ein animiertes Histogramm waehrend des Laufs (gleiches `FuncAnimation`-Pattern
wie `dashboard.py`), `plot_path` speichert den Endstand zusaetzlich als PNG nach
`algo/results/`.
**Warum:** Quelle `raw/md.md` (YouTube-Transkript zu Timothy Masters' Buch "Permutation and
Randomization Tests for Trading System Development") -- siehe
`docs/superpowers/specs/2026-08-08-algo-permutation-test-design.md`.
**Bekannte Grenzen:** Reine Infrastruktur, noch an keine konkrete Strategie angebunden (bewusst
-- siehe Spec). Permutation zerstoert Volatility-Clustering/Long-Memory echter Preise; ein
Test-Pass ist kein Ersatz fuer Walk-Forward/Stress-Test. Kleine Stichprobe in
`raw/marktdaten/` macht P-Werte aktuell zu Groessenordnungen, nicht zu belastbaren Zahlen.
```

- [ ] **Step 2: Append PLAN.md log entry**

Find the log table/section at the bottom of `algo/PLAN.md` (append after the most recent
entry, matching the existing entry format used there) with:

```markdown
- **2026-08-08**: Bar-Permutationstest (MCPT) hinzugefuegt (`algo/permutation_test.py`),
  Quelle `raw/md.md` (Timothy Masters' Methode). Viertes Validierungsverfahren neben
  `validate.py`s Walk-Forward/Parameter-Sensitivitaet/Trade-Resampling -- noch an keine
  konkrete Strategie angebunden. Spec:
  `docs/superpowers/specs/2026-08-08-algo-permutation-test-design.md`.
```

- [ ] **Step 3: Commit**

```bash
git add algo/README.md algo/PLAN.md
git commit -m "docs(algo): README/PLAN.md -- permutation_test.py dokumentiert"
```

---

## Post-Plan (not part of this implementation, tracked separately)

- Wiki-Ingest der Quelle `raw/md.md` nach `wiki/sources/` (folgt dem normalen Ingest-Workflow
  aus `CLAUDE.md`, kein Code) — separater Schritt, nicht Teil dieses Plans.
- Anbindung an eine konkrete Strategie (Ensemble oder Silver Bullet) — separater Spec/Plan,
  sobald genug Handelstage vorliegen (siehe Spec "Bekannte Grenzen").
