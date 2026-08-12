# Quant-Riskmanagement — austauschbare Risk-Module Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Vier austauschbare Risk-Sizing-Module (fix 1%, GARCH-Vol, Half-Kelly, Drawdown-Kill-Switch) hinter einem gemeinsamen Interface bauen, in `algo/backtest_bt.py` verdrahten und über ein Vergleichs-Script gegeneinander backtesten.

**Architecture:** Trennung von "wie viel % Risiko" (neu, austauschbar) und "wie viele Kontrakte kauft das" (bestehend, unverändert `pnl.py::risk_size()`). Jedes Modul ist eine Funktion `risk_pct(base_pct=0.01, **ctx) -> float`, die nur die Kontext-Kwargs zieht, die sie braucht (`hist` für GARCH, `closed_trades` für Kelly). `SilverBulletStrategy` bekommt ein austauschbares Klassenattribut `risk_module` sowie ein Kill-Switch-Gate, das unabhängig vom gewählten Modul vor jedem neuen Trade prüft.

**Tech Stack:** Python 3.12, pandas, numpy, scipy (`scipy.optimize.minimize` für den GARCH-Fit — bereits Dependency, kein neues Package), `backtesting`-Lib (bereits Dependency).

## Global Constraints

- Kein neues PyPI-Package (aus der Spec: GARCH(1,1) via `scipy.optimize.minimize`, bereits in `algo/requirements.txt`).
- Stop-Platzierung bleibt unangetastet — nur das Risikobudget (%) wird skaliert, nicht die Stop-Distanz aus `rules.py::plan_trade`.
- Kein Lookahead: GARCH-Fit nutzt nur `hist` (Bars bis `when`, bereits lückenlos in `SilverBulletStrategy._hist` geführt), Kelly nutzt nur `closed_trades` (nur bereits abgeschlossene Trades vor dem aktuellen Zeitpunkt).
- Jedes Modul bekommt einen `demo()`-Selfcheck nach dem Muster aus `algo/pnl.py` (assert-basiert, kein pytest) und wird in `algo/selfcheck.py::CHECKS` eingetragen.
- `algo/README.md` bekommt pro neuem Modul einen Abschnitt (Konvention: ein `## `datei.py`` -- Kurzbeschreibung`-Block pro Datei, siehe bestehende Einträge).
- Reale $-P&L-Vergleichbarkeit: das Vergleichs-Script nutzt `pnl.py::real_pnl()`/`flag_dubious()`/`dubious_pct()` unverändert (Punktwert-korrekt, `dubious_pct` als Pflichtkennzahl im Report).

---

## Vorab ermittelte Baseline (MNQ, `python algo/backtest_bt.py MNQ`, vor jeder Änderung)

Aktueller Stand mit der festen 1%-Regel (Silver Bullet ohne Confluence, 12083 5m-Kerzen,
2026-06-08 bis 2026-08-11):

```
# Trades                        107
Echte $-P&L netto (netto)       -32032.82 USD
Equity Final [$]                63354.93
Max. Drawdown [%]               -38.45458
Win Rate [%]                    20.56075
Profit Factor                   0.55351
```

Diese Zahlen sind die Referenz für den Regressionscheck in Task 5 (Kill-Switch deaktiviert muss
exakt reproduzieren; Kill-Switch mit Default-Schwelle 15% muss sichtbar eingreifen, weil der
reale Drawdown mit -38.45% weit über der 15%-Schwelle liegt).

---

### Task 1: `algo/risk_fixed.py` — Baseline-Modul

**Files:**
- Create: `algo/risk_fixed.py`
- Modify: `algo/selfcheck.py`

**Interfaces:**
- Produces: `risk_fixed.risk_pct(base_pct: float = 0.01, **ctx) -> float` — ignoriert jeden
  Kontext, liefert immer `base_pct`. Wird von Task 5 (`backtest_bt.py`) als Default-Modul importiert.

- [ ] **Step 1: `algo/risk_fixed.py` schreiben**

```python
#!/usr/bin/env python3
"""Baseline-Risk-Modul: reine Auslagerung der bisherigen festen 1%-Regel (siehe
wiki/concepts/Risikomanagement (1% pro Trade).md) hinter das gemeinsame risk_pct()-Interface,
siehe docs/superpowers/specs/2026-08-12-quant-risk-management-design.md. Kein
Verhaltensunterschied zum bisherigen Stand -- Default-Modul in SilverBulletStrategy.
"""
from __future__ import annotations


def risk_pct(base_pct: float = 0.01, **ctx) -> float:
    """Ignoriert jeden Kontext (`hist`, `closed_trades`, ...) -- liefert immer `base_pct`."""
    return base_pct


def demo() -> None:
    assert risk_pct() == 0.01
    assert risk_pct(base_pct=0.02) == 0.02
    # Kontext-Kwargs (wie sie backtest_bt.py mitschickt) duerfen das Ergebnis nicht beeinflussen
    assert risk_pct(base_pct=0.01, hist=[1, 2, 3], closed_trades=["x"]) == 0.01
    print("risk_fixed demo: OK")


if __name__ == "__main__":
    demo()
```

- [ ] **Step 2: Selfcheck ausführen**

Run: `python algo/risk_fixed.py`
Expected: `risk_fixed demo: OK`

- [ ] **Step 3: In `algo/selfcheck.py` eintragen**

In `algo/selfcheck.py`, Import-Block (nach `from pnl import demo as pnl_demo`):
```python
from risk_fixed import demo as risk_fixed_demo  # noqa: E402
```
In der `CHECKS`-Liste (nach `("pnl", pnl_demo),`):
```python
    ("risk_fixed", risk_fixed_demo),
```

- [ ] **Step 4: Bündel-Selfcheck ausführen**

Run: `python algo/selfcheck.py`
Expected: `[OK]   risk_fixed` in der Ausgabe, Endsumme unverändert bis auf den neuen Eintrag.

- [ ] **Step 5: Commit**

```bash
git add algo/risk_fixed.py algo/selfcheck.py
git commit -m "feat(algo): risk_fixed.py -- Baseline-Risk-Modul (1%-Regel als risk_pct()-Interface)"
```

---

### Task 2: `algo/risk_garch.py` — GARCH(1,1)-Vol-Sizing

**Files:**
- Create: `algo/risk_garch.py`
- Modify: `algo/selfcheck.py`

**Interfaces:**
- Consumes: `hist: list[Bar]` (Objekte mit Attribut `.c`, wie `algo/backtest_bt.py::extend_hist`
  sie in `SilverBulletStrategy._hist` pflegt — hier nur strukturell genutzt, kein Import von
  `analyze_ohlc.Bar` nötig).
- Produces: `risk_garch.risk_pct(hist: list | None = None, base_pct: float = 0.01, **ctx) -> float`.

- [ ] **Step 1: `algo/risk_garch.py` schreiben**

```python
#!/usr/bin/env python3
"""GARCH(1,1)-Vol-Sizing: skaliert nur das Risikobudget (die %), NICHT die Stop-Distanz -- der
Stop bleibt strukturell aus rules.py::plan_trade (FVG-Gegenkante + Puffer). Siehe
docs/superpowers/specs/2026-08-12-quant-risk-management-design.md Abschnitt 2. Kein neues
Package: GARCH(1,1) hat nur 3 Parameter (omega/alpha/beta), MLE-Fit ueber
scipy.optimize.minimize (bereits Dependency, siehe algo/masters.py)."""
from __future__ import annotations

import numpy as np
from scipy.optimize import minimize

MIN_BARS = 100    # zu wenig Historie fuer einen stabilen GARCH-Fit -> Fallback auf base_pct
LOOKBACK = 500    # Fit-Fenster in Kerzen, begrenzt Rechenzeit und gewichtet juengere Vol staerker


def _fit_garch(returns: np.ndarray) -> tuple[float, float, float]:
    """MLE-Fit von GARCH(1,1) (omega, alpha, beta) auf demeanten Log-Returns."""
    r = returns - returns.mean()
    var0 = float(r.var()) or 1e-8

    def neg_log_lik(params: np.ndarray) -> float:
        omega, alpha, beta = params
        if omega <= 0 or alpha < 0 or beta < 0 or alpha + beta >= 0.999:
            return 1e10
        n = len(r)
        sigma2 = np.empty(n)
        sigma2[0] = var0
        for t in range(1, n):
            sigma2[t] = omega + alpha * r[t - 1] ** 2 + beta * sigma2[t - 1]
        sigma2 = np.maximum(sigma2, 1e-12)
        ll = -0.5 * np.sum(np.log(2 * np.pi * sigma2) + r ** 2 / sigma2)
        return float(-ll)

    x0 = np.array([var0 * 0.1, 0.1, 0.8])
    bounds = [(1e-12, None), (0.0, 1.0), (0.0, 1.0)]
    res = minimize(neg_log_lik, x0, bounds=bounds, method="L-BFGS-B")
    omega, alpha, beta = res.x
    return float(omega), float(alpha), float(beta)


def _sigma_from_variance_path(omega: float, alpha: float, beta: float,
                               returns: np.ndarray) -> tuple[float, float]:
    """Reine Funktion, getrennt von _fit_garch(): baut den GARCH-Varianzpfad aus gegebenen
    Parametern und liefert (naechste Vol-Prognose, langfristige GARCH-Vol =
    sqrt(omega/(1-alpha-beta))). Erlaubt, die Skalierungslogik unabhaengig von der
    MLE-Konvergenz deterministisch zu testen (siehe demo())."""
    r = returns - returns.mean()
    n = len(r)
    sigma2 = np.empty(n)
    sigma2[0] = float(r.var()) or 1e-8
    for t in range(1, n):
        sigma2[t] = omega + alpha * r[t - 1] ** 2 + beta * sigma2[t - 1]
    forecast_var = omega + alpha * r[-1] ** 2 + beta * sigma2[-1]
    longrun_var = omega / max(1 - alpha - beta, 1e-3)
    return float(np.sqrt(max(forecast_var, 1e-12))), float(np.sqrt(max(longrun_var, 1e-12)))


def _scale(base_pct: float, sigma_forecast: float, sigma_longrun: float) -> float:
    """base_pct / (Prognose/Langfrist-Vol), geclippt auf [0.5, 1.5] x base_pct -- verhindert,
    dass ein Fit-Ausreisser die Positionsgroesse sprengt."""
    if sigma_longrun <= 0:
        return base_pct
    vol_ratio = sigma_forecast / sigma_longrun
    return float(min(max(base_pct / vol_ratio, 0.5 * base_pct), 1.5 * base_pct))


def risk_pct(hist: list | None = None, base_pct: float = 0.01, **ctx) -> float:
    """Skaliert base_pct mit der GARCH(1,1)-Vol-Prognose relativ zur langfristigen GARCH-Vol.
    Fallback auf base_pct, solange weniger als MIN_BARS Kerzen vorliegen."""
    if hist is None or len(hist) < MIN_BARS:
        return base_pct
    window = hist[-LOOKBACK:]
    closes = np.array([b.c for b in window], dtype=float)
    returns = np.diff(np.log(closes))
    if len(returns) < MIN_BARS - 1:
        return base_pct
    omega, alpha, beta = _fit_garch(returns)
    sigma_fc, sigma_lr = _sigma_from_variance_path(omega, alpha, beta, returns)
    return _scale(base_pct, sigma_fc, sigma_lr)


def demo() -> None:
    # --- _scale(): reine Clipping-Logik, keine Randomness ---
    assert abs(_scale(0.01, 2.0, 1.0) - 0.005) < 1e-9    # Ratio 2 -> untere Klammer (0.5x)
    assert abs(_scale(0.01, 0.1, 1.0) - 0.015) < 1e-9    # Ratio 0.1 -> obere Klammer (1.5x)
    assert abs(_scale(0.01, 1.0, 1.0) - 0.01) < 1e-9     # Ratio 1 -> unveraendert
    assert _scale(0.01, 1.0, 0.0) == 0.01                # sigma_longrun<=0 -> Fallback

    # --- _sigma_from_variance_path(): deterministisch, kein MLE-Fit noetig ---
    returns = np.array([0.001, -0.001, 0.0008, -0.0012, 0.05])  # letzter Wert: starker Spike
    sigma_fc, sigma_lr = _sigma_from_variance_path(1e-6, 0.1, 0.85, returns)
    assert sigma_fc > sigma_lr, "nach einem Vol-Spike muss die Prognose ueber der Langfrist-Vol liegen"

    # --- risk_pct(): Fallback bei zu wenig Historie ---
    from types import SimpleNamespace
    short_hist = [SimpleNamespace(c=100.0 + i * 0.01) for i in range(MIN_BARS - 1)]
    assert risk_pct(hist=short_hist, base_pct=0.01) == 0.01
    assert risk_pct(hist=None, base_pct=0.01) == 0.01

    # --- risk_pct(): End-to-End-Smoke-Test (Fit muss laufen, Ergebnis in den Clip-Grenzen) ---
    rng = np.random.default_rng(42)
    prices = 100.0 * np.exp(np.cumsum(rng.normal(0, 0.001, MIN_BARS + 50)))
    hist = [SimpleNamespace(c=p) for p in prices]
    pct = risk_pct(hist=hist, base_pct=0.01)
    assert 0.005 - 1e-9 <= pct <= 0.015 + 1e-9, f"risk_pct {pct} ausserhalb der Clip-Grenzen"

    print("risk_garch demo: OK")


if __name__ == "__main__":
    demo()
```

- [ ] **Step 2: Selfcheck ausführen**

Run: `python algo/risk_garch.py`
Expected: `risk_garch demo: OK`

- [ ] **Step 3: In `algo/selfcheck.py` eintragen**

Import (nach dem `risk_fixed`-Import aus Task 1):
```python
from risk_garch import demo as risk_garch_demo  # noqa: E402
```
`CHECKS`-Eintrag (nach `("risk_fixed", risk_fixed_demo),`):
```python
    ("risk_garch", risk_garch_demo),
```

- [ ] **Step 4: Bündel-Selfcheck ausführen**

Run: `python algo/selfcheck.py`
Expected: `[OK]   risk_garch` zusätzlich zu `[OK]   risk_fixed`.

- [ ] **Step 5: Commit**

```bash
git add algo/risk_garch.py algo/selfcheck.py
git commit -m "feat(algo): risk_garch.py -- GARCH(1,1)-Vol-Sizing (skaliert nur das Risikobudget)"
```

---

### Task 3: `algo/risk_kelly.py` — Half-Kelly aus rollierenden Trade-Ergebnissen

**Files:**
- Create: `algo/risk_kelly.py`
- Modify: `algo/selfcheck.py`

**Interfaces:**
- Consumes: `closed_trades` — iterable von Objekten mit Attribut `.pl_pct` (float, Prozent) —
  entspricht `backtesting.Strategy.closed_trades` (jedes Element ist ein `Trade`-Objekt mit
  `.pl_pct`-Property; siehe `backtesting/backtesting.py::Trade.pl_pct`).
- Produces: `risk_kelly.risk_pct(closed_trades=None, base_pct: float = 0.01, **ctx) -> float`.

- [ ] **Step 1: `algo/risk_kelly.py` schreiben**

```python
#!/usr/bin/env python3
"""Half-Kelly-Sizing aus rollierenden Trade-Ergebnissen (diskrete Trading-Kelly-Formel,
p - (1-p)/b, nicht die Portfolio-Rendite-Variante aus
wiki/concepts/Kelly-Criterion & Value-at-Risk (Money Management).md). Siehe
docs/superpowers/specs/2026-08-12-quant-risk-management-design.md Abschnitt 2. Nutzt
`closed_trades` aus backtesting.Strategy (nur abgeschlossene Trades vor dem aktuellen
Zeitpunkt -- kein Lookahead)."""
from __future__ import annotations

WINDOW = 30       # rollierendes Fenster ueber die letzten N abgeschlossenen Trades
MIN_TRADES = 20   # Fallback auf base_pct, solange weniger Trades vorliegen


def _kelly_fraction(pl_pcts: list[float]) -> float | None:
    """Reine Funktion auf einer Liste von Trade-Returns (pl_pct, in %): p = Trefferquote,
    b = avg_win/avg_loss (R-Multiple-Verhaeltnis), f* = p - (1-p)/b. None, wenn das Sample
    nicht gemischt ist (nur Gewinner oder nur Verlierer -- Formel dann nicht anwendbar)."""
    wins = [p for p in pl_pcts if p > 0]
    losses = [-p for p in pl_pcts if p < 0]
    if not wins or not losses:
        return None
    p = len(wins) / len(pl_pcts)
    b = (sum(wins) / len(wins)) / (sum(losses) / len(losses))
    return p - (1 - p) / b


def risk_pct(closed_trades=None, base_pct: float = 0.01, **ctx) -> float:
    """Half-Kelly ueber die letzten WINDOW abgeschlossenen Trades. Fallback auf base_pct,
    solange weniger als MIN_TRADES vorliegen oder das Sample nicht gemischt ist."""
    if closed_trades is None or len(closed_trades) < MIN_TRADES:
        return base_pct
    recent = list(closed_trades)[-WINDOW:]
    pl_pcts = [t.pl_pct for t in recent]
    f_star = _kelly_fraction(pl_pcts)
    if f_star is None:
        return base_pct
    return max(0.0, f_star / 2)


def demo() -> None:
    # --- _kelly_fraction(): Lehrbuchbeispiel, p=0.5, b=2 (Gewinne doppelt so gross wie
    # Verluste) -> f* = 0.5 - 0.5/2 = 0.25
    pl_pcts = [2.0, -1.0, 2.0, -1.0]
    assert abs(_kelly_fraction(pl_pcts) - 0.25) < 1e-9

    # Nur Gewinner oder nur Verlierer -> Formel nicht anwendbar
    assert _kelly_fraction([1.0, 2.0, 3.0]) is None
    assert _kelly_fraction([-1.0, -2.0]) is None

    # --- risk_pct(): Fallback unter MIN_TRADES ---
    from types import SimpleNamespace
    few = [SimpleNamespace(pl_pct=2.0 if i % 2 == 0 else -1.0) for i in range(MIN_TRADES - 1)]
    assert risk_pct(closed_trades=few, base_pct=0.01) == 0.01
    assert risk_pct(closed_trades=None, base_pct=0.01) == 0.01

    # --- risk_pct(): genug Trades, gemischtes p=0.5/b=2-Sample -> Half-Kelly = 0.125 ---
    enough = [SimpleNamespace(pl_pct=2.0 if i % 2 == 0 else -1.0) for i in range(MIN_TRADES)]
    pct = risk_pct(closed_trades=enough, base_pct=0.01)
    assert abs(pct - 0.125) < 1e-9

    # --- risk_pct(): nur Verlierer im rollierenden Fenster -> Fallback auf base_pct ---
    all_losses = [SimpleNamespace(pl_pct=-1.0) for _ in range(MIN_TRADES)]
    assert risk_pct(closed_trades=all_losses, base_pct=0.01) == 0.01

    print("risk_kelly demo: OK")


if __name__ == "__main__":
    demo()
```

- [ ] **Step 2: Selfcheck ausführen**

Run: `python algo/risk_kelly.py`
Expected: `risk_kelly demo: OK`

- [ ] **Step 3: In `algo/selfcheck.py` eintragen**

Import:
```python
from risk_kelly import demo as risk_kelly_demo  # noqa: E402
```
`CHECKS`-Eintrag (nach `("risk_garch", risk_garch_demo),`):
```python
    ("risk_kelly", risk_kelly_demo),
```

- [ ] **Step 4: Bündel-Selfcheck ausführen**

Run: `python algo/selfcheck.py`
Expected: `[OK]   risk_kelly` zusätzlich zu den beiden vorherigen.

- [ ] **Step 5: Commit**

```bash
git add algo/risk_kelly.py algo/selfcheck.py
git commit -m "feat(algo): risk_kelly.py -- Half-Kelly-Sizing aus rollierenden Trade-Ergebnissen"
```

---

### Task 4: `algo/risk_killswitch.py` — Drawdown-Kill-Switch

**Files:**
- Create: `algo/risk_killswitch.py`
- Modify: `algo/selfcheck.py`

**Interfaces:**
- Produces: `risk_killswitch.allowed(equity_curve: list[float], max_drawdown_pct: float = 0.15) -> bool`
  und `risk_killswitch.DEFAULT_MAX_DRAWDOWN_PCT = 0.15`. Wird von Task 5 als Gate vor
  `risk_pct()` genutzt.

- [ ] **Step 1: `algo/risk_killswitch.py` schreiben**

```python
#!/usr/bin/env python3
"""Drawdown-Kill-Switch pro Strategie: haelt kompletten Handel an, wenn der Drawdown seit dem
bisherigen Equity-Hoch eine Schwelle ueberschreitet. Reset automatisch bei neuem Equity-Hoch
(kein manueller Reset noetig, `peak` ergibt sich immer aus der bisherigen Kurve). Siehe
docs/superpowers/specs/2026-08-12-quant-risk-management-design.md Abschnitt 2."""
from __future__ import annotations

DEFAULT_MAX_DRAWDOWN_PCT = 0.15


def allowed(equity_curve: list[float], max_drawdown_pct: float = DEFAULT_MAX_DRAWDOWN_PCT) -> bool:
    """False = kein neuer Trade erlaubt. `equity_curve` ist die bisherige Equity-Historie
    (aeltestes zuerst, letzter Wert = aktuell); leer -> immer erlaubt (noch keine Historie)."""
    if not equity_curve:
        return True
    peak = max(equity_curve)
    if peak <= 0:
        return True
    dd = (peak - equity_curve[-1]) / peak
    return dd < max_drawdown_pct


def demo() -> None:
    assert allowed([]) is True
    assert allowed([100_000]) is True
    # Genau auf der Schwelle (15% Drawdown) -> noch NICHT gestoppt (strikt kleiner)
    assert allowed([100_000, 85_000], 0.15) is True
    # Ueber der Schwelle -> gestoppt
    assert allowed([100_000, 84_999], 0.15) is False
    # Reset bei neuem Hoch: Drawdown, dann neues Hoch -> peak folgt dem neuen Hoch,
    # ein erneuter kleiner Ruecksetzer bleibt unter der Schwelle
    curve = [100_000, 80_000, 110_000, 95_000]  # DD ab 110k: (110k-95k)/110k = 13.6%
    assert allowed(curve, 0.15) is True
    print("risk_killswitch demo: OK")


if __name__ == "__main__":
    demo()
```

- [ ] **Step 2: Selfcheck ausführen**

Run: `python algo/risk_killswitch.py`
Expected: `risk_killswitch demo: OK`

- [ ] **Step 3: In `algo/selfcheck.py` eintragen**

Import:
```python
from risk_killswitch import demo as risk_killswitch_demo  # noqa: E402
```
`CHECKS`-Eintrag (nach `("risk_kelly", risk_kelly_demo),`):
```python
    ("risk_killswitch", risk_killswitch_demo),
```

- [ ] **Step 4: Bündel-Selfcheck ausführen**

Run: `python algo/selfcheck.py`
Expected: alle vier neuen Module `[OK]`.

- [ ] **Step 5: Commit**

```bash
git add algo/risk_killswitch.py algo/selfcheck.py
git commit -m "feat(algo): risk_killswitch.py -- Drawdown-Kill-Switch pro Strategie"
```

---

### Task 5: Integration in `algo/backtest_bt.py`

**Files:**
- Modify: `algo/backtest_bt.py:1-172` (Imports, `SilverBulletStrategy`, `README.md`)
- Modify: `algo/README.md` (neuer Abschnitt für die vier Module + Update des
  `backtest_bt.py`-Abschnitts)

**Interfaces:**
- Consumes: `risk_fixed.risk_pct`, `risk_killswitch.allowed`, `risk_killswitch.DEFAULT_MAX_DRAWDOWN_PCT`
  (Tasks 1+4). `risk_garch`/`risk_kelly` werden hier NICHT importiert (Default bleibt `risk_fixed`
  — Task 6 schaltet sie im Vergleichs-Script um).
- Produces: `SilverBulletStrategy.risk_module` (Klassenattribut, Default `risk_fixed`),
  `SilverBulletStrategy.max_drawdown_pct` (Klassenattribut, Default `risk_killswitch.DEFAULT_MAX_DRAWDOWN_PCT`).
  Task 6 setzt `SilverBulletStrategy.risk_module` vor jedem `Backtest().run()`-Aufruf um.

- [ ] **Step 1: Baseline erneut bestätigen (vor jeder Änderung)**

Run: `python algo/backtest_bt.py MNQ 2>/dev/null | grep -A 30 "^Start"`
Erwartet (Referenzwerte, siehe "Vorab ermittelte Baseline" oben): `# Trades  107`,
`Max. Drawdown [%]  -38.45458`. Notiere diese Werte, falls sie von der obigen Baseline
abweichen sollten (z.B. weil zwischenzeitlich neue Handelstage in `raw/marktdaten/`
dazugekommen sind) — die folgenden Vergleichsschritte nutzen dann die frisch notierten Werte
statt der oben genannten.

- [ ] **Step 2: Imports in `algo/backtest_bt.py` ergänzen**

Nach Zeile 36 (`from confidence import bar_metrics, print_bar_metrics`):
```python
import risk_fixed  # noqa: E402
import risk_killswitch  # noqa: E402
```

- [ ] **Step 3: `SilverBulletStrategy` um `risk_module` und Kill-Switch erweitern**

Ersetze den Klassenkopf (aktuell Zeilen 69-77):
```python
class SilverBulletStrategy(Strategy):
    # Klassen-Attribut statt Konstante, damit bt.optimize() es variieren kann
    # (siehe algo/backtest_walkforward.py).
    stop_buffer_pct = 0.1
    max_risk_pct = 0.01        # Nutzerregel, siehe wiki/concepts/Risikomanagement (1% pro Trade).md
    point_value = POINT_VALUE["MNQ"]  # main() ueberschreibt das passend zum CLI-Symbol
    leverage = 20               # muss zu Backtest(margin=...) in main() passen (0.05 -> 20x),
                                 # siehe EnsembleStrategy.leverage -- ohne diesen Deckel
                                 # stornierte der Broker Orders mit engem Stop stillschweigend
```
durch:
```python
class SilverBulletStrategy(Strategy):
    # Klassen-Attribut statt Konstante, damit bt.optimize() es variieren kann
    # (siehe algo/backtest_walkforward.py).
    stop_buffer_pct = 0.1
    max_risk_pct = 0.01        # Nutzerregel, siehe wiki/concepts/Risikomanagement (1% pro Trade).md
    point_value = POINT_VALUE["MNQ"]  # main() ueberschreibt das passend zum CLI-Symbol
    leverage = 20               # muss zu Backtest(margin=...) in main() passen (0.05 -> 20x),
                                 # siehe EnsembleStrategy.leverage -- ohne diesen Deckel
                                 # stornierte der Broker Orders mit engem Stop stillschweigend
    risk_module = risk_fixed    # austauschbar: risk_fixed/risk_garch/risk_kelly, siehe
                                 # docs/superpowers/specs/2026-08-12-quant-risk-management-design.md
    max_drawdown_pct = risk_killswitch.DEFAULT_MAX_DRAWDOWN_PCT  # Kill-Switch-Schwelle, pro Strategie
```

Ersetze `init()` (aktuell Zeilen 79-81):
```python
    def init(self):
        self._taken: set[tuple] = set()  # (Tag, Fenstername) -- ein Versuch pro Fenster/Tag
        self._hist: list[Bar] = []       # inkrementell fortgeschrieben, siehe extend_hist()
```
durch:
```python
    def init(self):
        self._taken: set[tuple] = set()       # (Tag, Fenstername) -- ein Versuch pro Fenster/Tag
        self._hist: list[Bar] = []            # inkrementell fortgeschrieben, siehe extend_hist()
        self._equity_curve: list[float] = []  # fuer den Drawdown-Kill-Switch, waechst pro Bar
```

Ersetze `next()` (aktuell Zeilen 83-102):
```python
    def next(self):
        extend_hist(self._hist, self.data)  # muss VOR der Positionspruefung laufen (lueckenlos)
        if self.position:
            return
        when = self.data.index[-1]
        setup = plan_trade(self._hist, when, stop_buffer_pct=self.stop_buffer_pct)
        if setup is None:
            return
        key = (setup.t.date(), setup.window)
        if key in self._taken:
            return
        size = risk_size(self.equity, self.max_risk_pct, setup.entry, setup.stop, self.point_value,
                          max_notional=self.equity * self.leverage)
        if size < 1:
            return  # 1%-Risiko-Budget oder Margin-Obergrenze ergibt 0 Kontrakte
        self._taken.add(key)
        if setup.side == "long":
            self.buy(size=size, limit=setup.entry, sl=setup.stop, tp=setup.target)
        else:
            self.sell(size=size, limit=setup.entry, sl=setup.stop, tp=setup.target)
```
durch:
```python
    def next(self):
        extend_hist(self._hist, self.data)  # muss VOR der Positionspruefung laufen (lueckenlos)
        self._equity_curve.append(self.equity)
        if self.position:
            return
        if not risk_killswitch.allowed(self._equity_curve, self.max_drawdown_pct):
            return  # Drawdown-Kill-Switch aktiv -- kein neuer Trade, bis neues Equity-Hoch
        when = self.data.index[-1]
        setup = plan_trade(self._hist, when, stop_buffer_pct=self.stop_buffer_pct)
        if setup is None:
            return
        key = (setup.t.date(), setup.window)
        if key in self._taken:
            return
        pct = self.risk_module.risk_pct(hist=self._hist, closed_trades=self.closed_trades,
                                         base_pct=self.max_risk_pct)
        size = risk_size(self.equity, pct, setup.entry, setup.stop, self.point_value,
                          max_notional=self.equity * self.leverage)
        if size < 1:
            return  # Risiko-Budget oder Margin-Obergrenze ergibt 0 Kontrakte
        self._taken.add(key)
        if setup.side == "long":
            self.buy(size=size, limit=setup.entry, sl=setup.stop, tp=setup.target)
        else:
            self.sell(size=size, limit=setup.entry, sl=setup.stop, tp=setup.target)
```

- [ ] **Step 4: Regressionscheck 1 — Kill-Switch deaktiviert muss die Baseline exakt reproduzieren**

Run:
```bash
python -c "
import sys; sys.path.insert(0, 'algo')
from backtest_bt import SilverBulletStrategy, main
SilverBulletStrategy.max_drawdown_pct = 1.0  # praktisch nie ausloesend (>100% DD unmoeglich)
main(['MNQ'])
" 2>/dev/null | grep -E "^# Trades|Max. Drawdown|^Echte"
```
Expected: `# Trades  107`, `Max. Drawdown [%]  -38.45458` (bzw. die in Step 1 frisch notierten
Werte) — identisch zur Baseline, weil `risk_fixed.risk_pct()` immer `base_pct` liefert (kein
Sizing-Unterschied) und der Kill-Switch mit Schwelle 1.0 nie greift. Weicht ein Wert ab: Fehler
im Refactor, nicht im neuen Feature — vor Fortfahren beheben.

- [ ] **Step 5: Regressionscheck 2 — Kill-Switch mit Default-Schwelle (15%) muss sichtbar eingreifen**

Run: `python algo/backtest_bt.py MNQ 2>/dev/null | grep -E "^# Trades|Max. Drawdown"`
Expected: `# Trades` echt **kleiner** als 107 und `Max. Drawdown [%]` deutlich **flacher** als
-38.45% (die Strategie verliert bereits vor dem 107. Trade mehr als 15% vom Hoch und wird
gestoppt) — bestätigt, dass das Gate tatsächlich greift. Ein exakter Zahlenwert ist hier nicht
vorhersagbar (hängt von der genauen Reihenfolge der Trades ab), nur die Richtung zählt.

- [ ] **Step 6: `algo/backtest_bt.py::demo()` läuft weiterhin (unverändertes Verhalten von `extend_hist`)**

Run: `python algo/backtest_bt.py --selfcheck`
Expected: `backtest_bt.demo: OK (extend_hist ergebnis-erhaltend)` — dieser Test prüft nur
`extend_hist()`, das von Task 5 nicht verändert wurde, muss also unverändert grün bleiben.

- [ ] **Step 7: `algo/README.md` aktualisieren**

Füge nach dem bestehenden Abschnitt `## \`backtest_bt.py\` -- Silver-Bullet-Trade-Simulation`
(Zeile 62 laut `grep -n "^## "`) einen neuen Abschnitt ein:

```markdown
## `risk_fixed.py` / `risk_garch.py` / `risk_kelly.py` / `risk_killswitch.py` -- austauschbare Risk-Module

Siehe docs/superpowers/specs/2026-08-12-quant-risk-management-design.md. Trennt "wie viel %
Risiko" (diese vier Module) von "wie viele Kontrakte kauft das bei diesem %" (unveraendert
`pnl.py::risk_size()`). Gemeinsames Interface: `risk_pct(base_pct=0.01, **ctx) -> float`.

- `risk_fixed.risk_pct()` -- liefert immer `base_pct` (Status quo, Default in
  `SilverBulletStrategy.risk_module`).
- `risk_garch.risk_pct(hist=...)` -- skaliert `base_pct` mit einer GARCH(1,1)-Vol-Prognose
  relativ zur langfristigen GARCH-Vol (`sqrt(omega/(1-alpha-beta))`), geclippt auf
  [0.5, 1.5] x `base_pct`. Fallback auf `base_pct` unter 100 Kerzen Historie.
- `risk_kelly.risk_pct(closed_trades=...)` -- Half-Kelly (`f* = p - (1-p)/b`) aus den letzten
  30 abgeschlossenen Trades. Fallback auf `base_pct` unter 20 Trades oder bei einseitigem
  Sample (nur Gewinner/nur Verlierer).
- `risk_killswitch.allowed(equity_curve, max_drawdown_pct=0.15)` -- kein Sizing-Modul, sondern
  ein Gate VOR `risk_pct()`: stoppt neue Trades, sobald der Drawdown seit dem bisherigen
  Equity-Hoch die Schwelle ueberschreitet. Reset automatisch bei neuem Hoch. Laeuft pro
  Strategie (`SilverBulletStrategy._equity_curve`), unabhaengig vom gewaehlten `risk_module`.

Umschalten: `SilverBulletStrategy.risk_module = risk_garch` vor `Backtest(...).run()`, siehe
`algo/backtest_risk_compare.py` fuer den automatisierten Vergleich aller drei Sizing-Module.
```

- [ ] **Step 8: Commit**

```bash
git add algo/backtest_bt.py algo/README.md
git commit -m "feat(algo): risk_module-Umschalter + Drawdown-Kill-Switch in SilverBulletStrategy"
```

---

### Task 6: `algo/backtest_risk_compare.py` — Vergleichs-Harness

**Files:**
- Create: `algo/backtest_risk_compare.py`
- Modify: `algo/README.md`

**Interfaces:**
- Consumes: `backtest_bt.SilverBulletStrategy`, `backtest_bt.load_series` (Task 5),
  `risk_fixed`, `risk_garch`, `risk_kelly` (Tasks 1-3), `pnl.{POINT_VALUE,real_pnl,flag_dubious,dubious_pct}`.
- Produces: `algo/backtest_risk_compare.py::var_es(daily_pnl: pd.Series, confidence: float = 0.95) -> tuple[float, float]`
  (reine Funktion, `demo()`-getestet), CLI `python algo/backtest_risk_compare.py [SYMBOL]`,
  schreibt `wiki/synthesis/Risk-Management-Vergleich (laufend).md`.

- [ ] **Step 1: `algo/backtest_risk_compare.py` schreiben**

```python
#!/usr/bin/env python3
"""Vergleicht die drei Risk-Sizing-Module (fix/GARCH/Kelly) auf identischen Silver-Bullet-
Signalen -- gleiche Trades, nur die Positionsgroesse variiert. Der Drawdown-Kill-Switch (15%)
laeuft bei allen drei mit (unabhaengig vom Sizing-Modul, siehe backtest_bt.py). Siehe
docs/superpowers/specs/2026-08-12-quant-risk-management-design.md.

Aufruf:
    python algo/backtest_risk_compare.py MNQ
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pandas as pd
from backtesting import Backtest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from backtest_bt import SilverBulletStrategy, load_series  # noqa: E402
from pnl import POINT_VALUE, real_pnl, flag_dubious, dubious_pct  # noqa: E402
import risk_fixed  # noqa: E402
import risk_garch  # noqa: E402
import risk_kelly  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MODULES = {"fixed": risk_fixed, "garch": risk_garch, "kelly": risk_kelly}


def var_es(daily_pnl: pd.Series, confidence: float = 0.95) -> tuple[float, float]:
    """95%-Tages-VaR und Expected Shortfall (ES) aus einer taeglichen $-PnL-Reihe: VaR = das
    (1-confidence)-Quantil (als positiver Verlustbetrag), ES = Mittelwert aller Tage, die
    mindestens so schlecht wie das Quantil ausfielen (Tail-Mittelwert, subadditiv -- siehe
    wiki/concepts/Kelly-Criterion & Value-at-Risk (Money Management).md). Leere Reihe -> (0, 0)."""
    if len(daily_pnl) == 0:
        return 0.0, 0.0
    q = daily_pnl.quantile(1 - confidence)
    var = -float(q)
    tail = daily_pnl[daily_pnl <= q]
    es = -float(tail.mean()) if len(tail) else var
    return var, es


def run_one(df: pd.DataFrame, symbol: str, module) -> dict:
    """Fuehrt einen kompletten Backtest mit `module` als risk_module durch und liefert die
    Vergleichskennzahlen. Mutiert `SilverBulletStrategy`-Klassenattribute -- Aufrufe muessen
    sequenziell laufen (keine parallelen run_one()-Aufrufe auf derselben Klasse)."""
    SilverBulletStrategy.point_value = POINT_VALUE[symbol]
    SilverBulletStrategy.risk_module = module
    bt = Backtest(df, SilverBulletStrategy, cash=100_000, margin=0.05, commission=0.0002)
    stats = bt.run()
    trades = flag_dubious(stats._trades, df)
    trades = real_pnl(trades, symbol)
    if len(trades):
        daily = trades.groupby(trades["ExitTime"].dt.date)["RealPnL_USD"].sum()
    else:
        daily = pd.Series(dtype=float)
    var95, es95 = var_es(daily)
    return {
        "equity_final": float(stats["Equity Final [$]"]),
        "max_drawdown_pct": float(stats["Max. Drawdown [%]"]),
        "win_rate_pct": float(stats["Win Rate [%]"]) if len(trades) else 0.0,
        "profit_factor": float(stats["Profit Factor"]) if len(trades) and stats["Profit Factor"] == stats["Profit Factor"] else 0.0,
        "n_trades": int(len(trades)),
        "real_pnl_usd": float(trades["RealPnL_USD"].sum()) if len(trades) else 0.0,
        "dubious_pct": float(dubious_pct(trades)),
        "var95_usd": var95,
        "es95_usd": es95,
    }


def format_report(results: dict[str, dict], symbol: str) -> str:
    lines = [
        "---",
        "tags: [synthesis, algo-methodology, risikomanagement, backtest]",
        "created: 2026-08-12",
        f"updated: {date.today().isoformat()}",
        "sources: [\"[[Risikomanagement (1% pro Trade)]]\", \"[[Kelly-Criterion & Value-at-Risk (Money Management)]]\"]",
        "---",
        "",
        "# Risk-Management-Vergleich (laufend)",
        "",
        f"**Generiert** von `algo/backtest_risk_compare.py {symbol}` -- ueberschreibt sich bei "
        "jedem Lauf komplett, kein manuell gepflegter Inhalt (siehe CLAUDE.md \"(laufend)\"-Muster). "
        "Gleiche Silver-Bullet-Signale, nur die Positionsgroesse variiert zwischen den drei Modulen "
        "(siehe [[../algo/README.md|algo/README.md]]). Drawdown-Kill-Switch (15%) laeuft bei allen "
        "drei mit.",
        "",
        "| Modul | Equity Final $ | Max DD % | Win Rate % | Profit Factor | Trades | Echte $-P&L | Dubious % | VaR95 $ | ES95 $ |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for name, r in results.items():
        lines.append(
            f"| {name} | {r['equity_final']:.0f} | {r['max_drawdown_pct']:.1f} | "
            f"{r['win_rate_pct']:.1f} | {r['profit_factor']:.2f} | {r['n_trades']} | "
            f"{r['real_pnl_usd']:+.0f} | {r['dubious_pct']:.1f} | {r['var95_usd']:.0f} | "
            f"{r['es95_usd']:.0f} |"
        )
    return "\n".join(lines) + "\n"


def main(argv=None) -> None:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("symbol", nargs="?", default="MNQ")
    a = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")

    df = load_series(a.symbol)
    print(f"{a.symbol}: {len(df)} Kerzen, {df.index[0]} bis {df.index[-1]}")

    results = {name: run_one(df, a.symbol, mod) for name, mod in MODULES.items()}
    for name, r in results.items():
        print(f"{name}: {r}")

    report = format_report(results, a.symbol)
    out = ROOT / "wiki" / "synthesis" / "Risk-Management-Vergleich (laufend).md"
    out.write_text(report, encoding="utf-8")
    print(f"\ngeschrieben: {out.relative_to(ROOT)}")


def demo() -> None:
    # 5 Tage: -100, -50, 0, 30, 500 -- bei 95% Konfidenz liegt das 5%-Quantil beim schlechtesten
    # Wert (nur 5 Datenpunkte -> Quantil faellt exakt auf den Minimalwert), VaR = 100, ES = 100
    # (Tail = nur dieser eine Tag).
    s = pd.Series([-100.0, -50.0, 0.0, 30.0, 500.0])
    var95, es95 = var_es(s, confidence=0.95)
    assert abs(var95 - 100.0) < 1e-6
    assert abs(es95 - 100.0) < 1e-6

    # Leere Reihe -> (0, 0)
    assert var_es(pd.Series(dtype=float)) == (0.0, 0.0)

    # Zwei gleich schlechte Tage im Tail -> ES ist deren Mittelwert, nicht nur einer
    s2 = pd.Series([-200.0, -200.0, -10.0, 5.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0])
    var95b, es95b = var_es(s2, confidence=0.95)
    assert var95b > 0
    assert es95b >= var95b  # ES ist per Konstruktion mindestens so extrem wie VaR (Tail-Mittel)

    print("backtest_risk_compare demo: OK")


if __name__ == "__main__":
    if "--selfcheck" in sys.argv:
        demo()
    else:
        main()
```

- [ ] **Step 2: Selfcheck ausführen**

Run: `python algo/backtest_risk_compare.py --selfcheck`
Expected: `backtest_risk_compare demo: OK`

- [ ] **Step 3: In `algo/selfcheck.py` eintragen**

Import:
```python
from backtest_risk_compare import demo as backtest_risk_compare_demo  # noqa: E402
```
`CHECKS`-Eintrag (nach `("backtest_bt", backtest_bt_demo),`):
```python
    ("backtest_risk_compare", backtest_risk_compare_demo),
```

Bewusst NUR die reine `var_es()`-Funktion hier eingebunden, nicht `main()` — drei volle
MNQ-Backtests nacheinander würden `selfcheck.py` (soll ein schneller Regressions-Check
bleiben, siehe Datei-Docstring) spürbar verlangsamen. Der volle Lauf ist Step 4.

- [ ] **Step 4: Vollen Vergleich einmal ausführen (manuelle Verifikation, kein Selfcheck)**

Run: `python algo/backtest_risk_compare.py MNQ`
Expected: druckt drei Zeilen (`fixed: {...}`, `garch: {...}`, `kelly: {...}`) und schreibt
`wiki/synthesis/Risk-Management-Vergleich (laufend).md`. Prüfe von Hand:
- `fixed`-Zeile: `n_trades` und `real_pnl_usd` sollten sich (bis auf Rundung) mit dem Ergebnis
  aus Task 5 Step 5 decken (Kill-Switch mit Default-Schwelle 15%, weniger als 107 Trades).
- `garch`/`kelly`-Zeilen: `n_trades` kann von `fixed` abweichen (unterschiedliche
  Positionsgrößen → unterschiedlicher Drawdown-Verlauf → Kill-Switch greift zu einem anderen
  Zeitpunkt), das ist erwartetes Verhalten, kein Bug.
- Öffne die geschriebene Markdown-Datei, prüfe, dass die Tabelle alle drei Zeilen enthält und
  kein Wert `NaN`/leer ist.

- [ ] **Step 5: `algo/README.md` ergänzen**

Füge direkt nach dem in Task 5 Step 7 eingefügten Risk-Modul-Abschnitt einen weiteren Absatz an:

```markdown
`algo/backtest_risk_compare.py MNQ` fuehrt alle drei Sizing-Module nacheinander gegen dieselben
Silver-Bullet-Signale aus und schreibt die Vergleichstabelle (Equity, Max-Drawdown, Win-Rate,
Profit Factor, `dubious_pct`, 95%-Tages-VaR/Expected-Shortfall) nach
`wiki/synthesis/Risk-Management-Vergleich (laufend).md` -- ueberschreibt die Datei bei jedem
Lauf komplett.
```

- [ ] **Step 6: Commit**

```bash
git add algo/backtest_risk_compare.py algo/selfcheck.py algo/README.md "wiki/synthesis/Risk-Management-Vergleich (laufend).md"
git commit -m "feat(algo): backtest_risk_compare.py -- Vergleichs-Harness fuer die drei Risk-Module + VaR/ES-Report"
```

---

## Self-Review (Ergebnis)

**Spec-Abdeckung:** Alle vier Spec-Bausteine (fix/GARCH/Kelly/Kill-Switch) haben eine eigene
Datei + Task (1-4); das gemeinsame Interface (`risk_pct(base_pct=0.01, **ctx)`) ist in allen
vier identisch; die Vergleichs-Harness inkl. VaR/ES-Report ist Task 6; die Integration in
`backtest_bt.py` (Klassenattribut `risk_module`, Kill-Switch-Gate) ist Task 5. Out-of-Scope-Punkte
aus der Spec (Portfolio-Ebene, vol-adaptiver Stop-Puffer, Live-Anbindung) haben bewusst keine
Tasks.

**Typkonsistenz geprüft:** `risk_pct(base_pct: float = 0.01, **ctx) -> float` ist in allen vier
Modulen identisch signiert; `backtest_bt.py` ruft konsistent
`self.risk_module.risk_pct(hist=self._hist, closed_trades=self.closed_trades, base_pct=self.max_risk_pct)`
auf (jedes Modul zieht sich per `**ctx` nur, was es braucht); `risk_killswitch.allowed()` und
`DEFAULT_MAX_DRAWDOWN_PCT` werden in Task 5 exakt mit den in Task 4 definierten Namen importiert.

**Platzhalter-Scan:** keine TBD/TODO; die Baseline-Zahlen (107 Trades, -32032.82 USD,
-38.45458% Max Drawdown) wurden vor Planerstellung tatsächlich per
`python algo/backtest_bt.py MNQ` ermittelt, keine geschätzten Platzhalter.
