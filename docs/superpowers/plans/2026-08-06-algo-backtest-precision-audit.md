# Backtest-Korrektheits-Audit & Praezisions-Layer fuer algo/ Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Jede an Backtest-Zahlen beteiligte Datei in `algo/` bekommt einen echten Dollar-P&L-Bezug (statt Notional-Prozent) und eine konservative Behandlung mehrdeutiger Stop/Ziel-Trades, damit die Zahlen reale Handelsentscheidungen mit echtem Geld tragen koennen.

**Architecture:** Eine neue, duenne Schicht `algo/pnl.py` sitzt UEBER der bestehenden `backtesting`-Bibliothek (die Order-/Equity-Verwaltung bleibt dort) und liefert Punktwert-basierte $-P&L, konservative Mehrdeutigkeits-Aufloesung und Risiko-basierte Positionsgroessen. Jede bestehende Datei, die Trades erzeugt oder Kennzahlen ausgibt, wird einzeln darauf umgestellt (siehe Datei-Reihenfolge im Spec). Dokumentation (`algo/README.md`) und ein gebuendelter Regressions-Check (`algo/selfcheck.py`) sind die abschliessenden Deliverables.

**Tech Stack:** Python 3.14, `pandas`, `backtesting` (PyPI-Lib), `scikit-learn` (bereits vorhanden, unveraendert). Keine neuen Abhaengigkeiten.

## Global Constraints

- Spec: `docs/superpowers/specs/2026-08-06-algo-backtest-precision-audit-design.md` (genehmigt 2026-08-06) -- jede Abweichung davon braucht eine Begruendung im Commit.
- `POINT_VALUE`-Tabelle bleibt auf tatsaechlich genutzte Symbole beschraenkt: `{"MNQ": 2.0, "NQ": 20.0, "ES": 50.0}` -- keine spekulative Vollstaendigkeit.
- Gefundene Bugs werden direkt repariert, keine separate Freigabe-Schleife pro Fund (Nutzer-Entscheidung, 2026-08-06).
- Test-Konvention dieses Projekts ist `demo()`/`_demo()` mit `assert`, kein pytest -- siehe `rules.py`, `signals.py`, `backtest_ensemble.py`. Neue Module folgen demselben Muster.
- Jede Aenderung an einer Datei mit bestehendem `demo()`/`_demo()` muss dieses nach der Aenderung weiterhin fehlerfrei durchlaufen lassen.
- `dubious_pct` (Anteil an Trades mit Entry- und Exit-Zeit in derselben Kerze) ist ab diesem Plan Pflichtzeile in jedem Backtest-/Validierungs-Report.

---

### Task 1: `algo/pnl.py` -- Praezisions-Layer (neu)

**Files:**
- Create: `algo/pnl.py`

**Interfaces:**
- Produces: `POINT_VALUE: dict[str, float]`, `real_pnl(trades: pd.DataFrame, symbol: str) -> pd.DataFrame` (fuegt Spalte `RealPnL_USD` hinzu), `flag_dubious(trades: pd.DataFrame) -> pd.DataFrame` (fuegt Spalte `Dubious` hinzu, ueberschreibt `ExitPrice` bei mehrdeutigen Trades mit `SL`), `dubious_pct(trades: pd.DataFrame) -> float`, `risk_size(equity: float, max_risk_pct: float, entry: float, stop: float, point_value: float) -> int`, `demo() -> None`. Alle spaeteren Tasks importieren aus diesem Modul.

- [ ] **Step 1: `algo/pnl.py` schreiben -- `real_pnl()` zunaechst OHNE den Punktwert-Faktor (bewusster Red-Step, spiegelt genau den Bug-Typ, um den es in diesem Audit geht)**

```python
#!/usr/bin/env python3
"""Praezisions-Layer UEBER der `backtesting`-Bibliothek (siehe
docs/superpowers/specs/2026-08-06-algo-backtest-precision-audit-design.md Teil 1). Die Lib
rechnet Trade-P&L als (ExitPrice - EntryPrice) * Size in rohen Preispunkten -- fuer Futures mit
einem Punktwert ungleich $1 (MNQ = $2/Punkt) ist das weder die reale Positionsgroesse
(`risk_size`) noch der reale Dollar-Gewinn (`real_pnl`). Ersetzt die Lib nicht (Order-/Equity-
Verwaltung bleibt dort), ergaenzt sie nur um die zwei fehlenden Punktwert-Bezuege.

`stats._trades`-Spalten (siehe backtesting/_stats.py): Size, EntryBar, ExitBar, EntryPrice,
ExitPrice, SL, TP, PnL, Commission, ReturnPct, EntryTime, ExitTime, Duration, Tag.
"""
from __future__ import annotations

import pandas as pd

# Nur tatsaechlich im Projekt genutzte Symbole -- keine spekulative Vollstaendigkeit.
POINT_VALUE = {"MNQ": 2.0, "NQ": 20.0, "ES": 50.0}


def real_pnl(trades: pd.DataFrame, symbol: str) -> pd.DataFrame:
    """Kopie von `trades` mit zusaetzlicher Spalte 'RealPnL_USD' = (ExitPrice - EntryPrice) *
    Size * Punktwert[symbol]. `Size` traegt bei backtesting.py bereits das Vorzeichen (negativ
    bei Short), daher kein separates Side-Handling noetig."""
    if symbol not in POINT_VALUE:
        raise ValueError(f"Kein Punktwert fuer {symbol!r} hinterlegt (POINT_VALUE: {list(POINT_VALUE)})")
    out = trades.copy()
    out["RealPnL_USD"] = (out["ExitPrice"] - out["EntryPrice"]) * out["Size"]  # Punktwert folgt in Step 3
    return out


def flag_dubious(trades: pd.DataFrame) -> pd.DataFrame:
    """Markiert Trades, deren Entry- und Exit-Zeit in derselben Kerze liegen (Spalte
    'Dubious') -- bei diesen kann die `backtesting`-Lib die Fill-Reihenfolge von SL/TP nicht
    unterscheiden (siehe UserWarning "same bar its parent stop/limit order was turned into a
    trade"). Wertet sie konservativ: 'ExitPrice' wird auf den Stop-Preis ('SL') gesetzt, statt
    der von der Lib gewaehlten (moeglicherweise zu optimistischen) 'ExitPrice' zu vertrauen.
    Muss VOR real_pnl() aufgerufen werden, damit die $-Berechnung den korrigierten Exit sieht."""
    out = trades.copy()
    out["Dubious"] = out["EntryTime"] == out["ExitTime"]
    out.loc[out["Dubious"], "ExitPrice"] = out.loc[out["Dubious"], "SL"]
    return out


def dubious_pct(trades: pd.DataFrame) -> float:
    """Anteil der Trades mit Entry- und Exit-Zeit in derselben Kerze, in Prozent."""
    if len(trades) == 0:
        return 0.0
    return 100.0 * (trades["EntryTime"] == trades["ExitTime"]).sum() / len(trades)


def risk_size(equity: float, max_risk_pct: float, entry: float, stop: float,
              point_value: float) -> int:
    """Kontraktzahl, sodass ein Stop-Out genau `max_risk_pct` von `equity` in ECHTEN Dollar
    kostet: budget_usd = equity * max_risk_pct; realer Verlust pro Kontrakt bei Stop-Out =
    |entry-stop| (Punkte) * point_value ($/Punkt). Ohne point_value wuerde 1 Punkt wie $1
    behandelt -- bei MNQ ($2/Punkt) laege das reale Risiko dann beim Doppelten des
    beabsichtigten Budgets (Fund vom 2026-08-06-Audit, siehe frueheres
    algo/backtest_ensemble.py::_risk_size vor diesem Fix)."""
    budget_usd = equity * max_risk_pct
    stop_dist_pts = abs(entry - stop)
    if stop_dist_pts == 0:
        return 0
    risk_per_contract_usd = stop_dist_pts * point_value
    return max(0, int(budget_usd / risk_per_contract_usd))


def demo() -> None:
    trades = pd.DataFrame({
        "EntryTime": pd.to_datetime(["2026-01-01 10:00", "2026-01-01 10:05", "2026-01-01 10:10"]),
        "ExitTime":  pd.to_datetime(["2026-01-01 10:05", "2026-01-01 10:05", "2026-01-01 10:20"]),
        "EntryPrice": [100.0, 100.0, 100.0],
        "ExitPrice":  [105.0, 105.0, 95.0],
        "Size": [1, 1, -1],
        "SL": [95.0, 95.0, 105.0],
    })
    tagged = flag_dubious(trades)
    assert tagged["Dubious"].tolist() == [False, True, False]
    assert tagged.loc[1, "ExitPrice"] == 95.0  # mehrdeutiger Trade -> Exit auf Stop gesetzt

    priced = real_pnl(tagged, "MNQ")
    # Trade 0: (105-100)*1*$2 = $10. Trade 1 (mehrdeutig, Exit auf Stop=95): (95-100)*1*$2 = -$10.
    # Trade 2 (Short, Size=-1): (95-100)*-1*$2 = $10.
    assert priced["RealPnL_USD"].tolist() == [10.0, -10.0, 10.0]

    assert abs(dubious_pct(trades) - 100 / 3) < 1e-6  # 1 von 3 Trades ist mehrdeutig

    try:
        real_pnl(trades, "GC")
    except ValueError:
        pass
    else:
        raise AssertionError("real_pnl muss bei unbekanntem Symbol einen ValueError werfen")

    # 1% von 100_000 = $1000 Budget, Stop 10 Punkte entfernt, MNQ $2/Punkt -> Risiko/Kontrakt
    # $20 -> 50 Kontrakte (die alte, fehlerhafte Formel ohne point_value ergab hier 100 --
    # doppelt so viel reales Risiko wie beabsichtigt).
    assert risk_size(100_000, 0.01, 100, 90, 2.0) == 50
    assert risk_size(100_000, 0.01, 100, 0, 2.0) == 5
    assert risk_size(100_000, 0.01, 100, 100, 2.0) == 0  # Stop-Abstand 0 -> keine Kontrakte

    print("pnl demo ok")


if __name__ == "__main__":
    demo()
```

- [ ] **Step 2: Lauf bestaetigen, dass die Datei aktuell mit einem AssertionError fehlschlaegt**

Run: `python algo/pnl.py`
Expected: `AssertionError` bei der Zeile `assert priced["RealPnL_USD"].tolist() == [10.0, -10.0, 10.0]`
(tatsaechlicher Wert `[5.0, -5.0, 5.0]` -- ohne Punktwert-Faktor wird 1 Punkt wie $1 statt $2
behandelt, exakt der Bug-Typ, um den es in diesem Audit geht).

- [ ] **Step 3: Punktwert-Faktor ergaenzen**

In `algo/pnl.py`, die Zeile

```python
    out["RealPnL_USD"] = (out["ExitPrice"] - out["EntryPrice"]) * out["Size"]  # Punktwert folgt in Step 3
```

ersetzen durch:

```python
    out["RealPnL_USD"] = (out["ExitPrice"] - out["EntryPrice"]) * out["Size"] * POINT_VALUE[symbol]
```

- [ ] **Step 4: Lauf bestaetigen, dass jetzt alles durchlaeuft**

Run: `python algo/pnl.py`
Expected: `pnl demo ok` (Exit-Code 0, keine Exception)

- [ ] **Step 5: Commit**

```bash
git add algo/pnl.py
git commit -m "feat(algo): pnl.py -- echter Punktwert-P&L, konservative Mehrdeutigkeits-Aufloesung, Risiko-Sizing"
```

---

### Task 2: `algo/backtest_ensemble.py` -- Punktwert-Bug in `_risk_size` fixen

**Files:**
- Modify: `algo/backtest_ensemble.py`

**Interfaces:**
- Consumes: `pnl.risk_size(equity, max_risk_pct, entry, stop, point_value) -> int`, `pnl.POINT_VALUE: dict[str, float]` (aus Task 1).
- Produces: `EnsembleStrategy.point_value: float` (neues Klassenattribut, von Task 5 mitgenutzt sofern noetig).

**Bug (2026-08-06-Audit):** Die alte lokale `_risk_size()` teilte das Dollar-Budget nur durch
den Punkte-Abstand, ohne den Punktwert zu beruecksichtigen -- bei MNQ ($2/Punkt) war das reale
Risiko pro Trade dadurch **doppelt so hoch** wie die beabsichtigten 1 % Kontoguthaben.

- [ ] **Step 1: `_demo()` auf die neue Verdrahtung umstellen (schlaegt zunaechst fehl, da `risk_size` noch nicht importiert ist)**

In `algo/backtest_ensemble.py`, den bestehenden Block

```python
def _demo() -> None:
    assert _passes_bias_filter("long", "long") is True
    assert _passes_bias_filter("short", "short") is True
    assert _passes_bias_filter("long", "short") is False
    assert _passes_bias_filter("short", "long") is False
    assert _passes_bias_filter("long", "neutral") is False

    # 1% von 100_000 = 1000 Risiko-Budget, Stop 10 Punkte entfernt -> 100 Einheiten
    assert _risk_size(100_000, 0.01, 100, 90) == 100
    # 1% von 100_000 = 1000 Risiko-Budget, Stop 100 Punkte entfernt -> nur noch 10 Einheiten
    assert _risk_size(100_000, 0.01, 100, 0) == 10
    print("backtest_ensemble _passes_bias_filter/_risk_size demo ok")
```

ersetzen durch:

```python
def _demo() -> None:
    assert _passes_bias_filter("long", "long") is True
    assert _passes_bias_filter("short", "short") is True
    assert _passes_bias_filter("long", "short") is False
    assert _passes_bias_filter("short", "long") is False
    assert _passes_bias_filter("long", "neutral") is False

    # Kontraktgroessen-Logik selbst ist in pnl.py::demo() getestet -- hier nur die Verdrahtung:
    # EnsembleStrategy.point_value muss MNQ's echten Punktwert tragen, sonst reproduziert sich
    # der 2026-08-06-Audit-Fund (reales Risiko doppelt so hoch wie beabsichtigt).
    assert EnsembleStrategy.point_value == POINT_VALUE["MNQ"] == 2.0
    print("backtest_ensemble _passes_bias_filter/point_value-Verdrahtung demo ok")
```

- [ ] **Step 2: Lauf bestaetigen, dass es fehlschlaegt (Import fehlt noch)**

Run: `python algo/backtest_ensemble.py`
Expected: `NameError: name 'POINT_VALUE' is not defined`

- [ ] **Step 3: Import ergaenzen, lokale `_risk_size` entfernen, Klassenattribut + Aufrufstelle umstellen**

Import-Zeile ergaenzen (nach `from signals import build_features  # noqa: E402`):

```python
from pnl import risk_size, POINT_VALUE  # noqa: E402
```

Die gesamte Funktion

```python
def _risk_size(equity: float, max_pct: float, entry: float, stop: float) -> int:
    """Nutzerregel: nie mehr als `max_pct` des Kontoguthabens Risiko PRO TRADE -- siehe
    wiki/concepts/Risikomanagement (1% pro Trade).md. Groesse wird so gewaehlt, dass ein
    Stop-Out genau dieses Budget ausschoepft, nicht mehr."""
    budget = equity * max_pct
    stop_dist = abs(entry - stop)
    return max(0, int(budget / stop_dist))
```

komplett loeschen.

In der Klasse `EnsembleStrategy`, nach der Zeile `max_risk_pct = 0.01        # Nutzerregel: ...`
ergaenzen:

```python
    point_value = POINT_VALUE["MNQ"]  # $/Punkt, siehe pnl.POINT_VALUE
```

In `next()`, die Zeile

```python
        size = _risk_size(self.equity, self.max_risk_pct, setup.entry, setup.stop)
```

ersetzen durch:

```python
        size = risk_size(self.equity, self.max_risk_pct, setup.entry, setup.stop, self.point_value)
```

Im Modul-Docstring den Satz `Positionsgroesse so bemessen, dass ein Stop-Out max. 1%
Kontoguthaben PRO TRADE kostet (_risk_size) -- nicht kumulativ pro Tag ...` ersetzen durch:
`Positionsgroesse so bemessen, dass ein Stop-Out max. 1% Kontoguthaben PRO TRADE kostet
(pnl.risk_size) -- nicht kumulativ pro Tag ... Punktwert-Bug im 2026-08-06-Audit gefixt: die
alte lokale _risk_size vergass den Punktwert-Faktor, reales Risiko war dadurch doppelt so hoch
wie beabsichtigt.`

- [ ] **Step 4: Lauf bestaetigen, dass es jetzt durchlaeuft**

Run: `python algo/backtest_ensemble.py`
Expected: `backtest_ensemble _passes_bias_filter/point_value-Verdrahtung demo ok`

- [ ] **Step 5: Commit**

```bash
git add algo/backtest_ensemble.py
git commit -m "fix(algo): EnsembleStrategy nutzt pnl.risk_size -- Punktwert-Bug verdoppelte reales Risiko"
```

---

### Task 3: `algo/backtest_bt.py` -- SilverBulletStrategy ohne Risiko-Sizing fixen

**Files:**
- Modify: `algo/backtest_bt.py`

**Interfaces:**
- Consumes: `pnl.risk_size`, `pnl.POINT_VALUE`, `pnl.real_pnl`, `pnl.flag_dubious`, `pnl.dubious_pct` (aus Task 1).

**Bug (2026-08-06-Audit):** `SilverBulletStrategy.next()` ruft `self.buy()`/`self.sell()` bisher
**ohne** `size`-Argument auf -- die `backtesting`-Lib nutzt dann ihren Default (~99.99 % des
Kontoguthabens als Notional), nicht die im Wiki festgelegte 1-%-Risiko-Regel. Das ist derselbe
Fehlerfamilie wie Task 2, hier aber schwerer: Es wird KEINE Risikogrenze angewendet.

- [ ] **Step 1: Import ergaenzen**

In `algo/backtest_bt.py`, nach `from rules import plan_trade  # noqa: E402` ergaenzen:

```python
from pnl import risk_size, POINT_VALUE, real_pnl, flag_dubious, dubious_pct  # noqa: E402
```

- [ ] **Step 2: Klassenattribute ergaenzen**

In `class SilverBulletStrategy(Strategy):`, nach `stop_buffer_pct = 0.1` ergaenzen:

```python
    max_risk_pct = 0.01        # Nutzerregel, siehe wiki/concepts/Risikomanagement (1% pro Trade).md
    point_value = POINT_VALUE["MNQ"]
```

- [ ] **Step 3: `next()` auf Risiko-basierte Groesse umstellen**

Den Block

```python
        key = (setup.t.date(), setup.window)
        if key in self._taken:
            return
        self._taken.add(key)
        if setup.side == "long":
            self.buy(limit=setup.entry, sl=setup.stop, tp=setup.target)
        else:
            self.sell(limit=setup.entry, sl=setup.stop, tp=setup.target)
```

ersetzen durch:

```python
        key = (setup.t.date(), setup.window)
        if key in self._taken:
            return
        size = risk_size(self.equity, self.max_risk_pct, setup.entry, setup.stop, self.point_value)
        if size < 1:
            return  # 1%-Risiko-Budget reicht bei diesem Stop-Abstand fuer keinen Kontrakt
        self._taken.add(key)
        if setup.side == "long":
            self.buy(size=size, limit=setup.entry, sl=setup.stop, tp=setup.target)
        else:
            self.sell(size=size, limit=setup.entry, sl=setup.stop, tp=setup.target)
```

- [ ] **Step 4: `main()` um echten $-P&L-Report erweitern**

Den Block

```python
    bt = Backtest(df, SilverBulletStrategy, cash=100_000, margin=0.05, commission=0.0002)
    stats = bt.run()
    print(stats)
    print()
    print(stats._trades)
```

ersetzen durch:

```python
    bt = Backtest(df, SilverBulletStrategy, cash=100_000, margin=0.05, commission=0.0002)
    stats = bt.run()
    print(stats)
    print()
    print(stats._trades)

    trades = flag_dubious(stats._trades)
    trades = real_pnl(trades, "MNQ")
    print(f"\nEchte $-P&L (MNQ, ${POINT_VALUE['MNQ']:.0f}/Punkt): "
          f"{trades['RealPnL_USD'].sum():+.2f} USD  "
          f"(mehrdeutige Trades: {dubious_pct(trades):.1f}%, konservativ als Verlust gewertet)")
```

- [ ] **Step 5: Regressionscheck laufen lassen (bestehendes `rules.py::demo()` + Integrationslauf)**

Run: `python algo/rules.py`
Expected: `plan_trade demo ok: ...` (unveraendert -- `plan_trade` selbst wurde nicht angefasst)

Run: `python algo/backtest_bt.py MNQ`
Expected: Laeuft durch (Exit-Code 0), Ausgabe enthaelt eine Zeile beginnend mit
`Echte $-P&L (MNQ, $2/Punkt): ...` und `mehrdeutige Trades: ...%`. Voraussetzung: `raw/marktdaten/`
enthaelt bereits MNQ-Tage (siehe `algo/PLAN.md` Log) -- bei 0 Kerzen stattdessen die Fehlermeldung
zu leeren Daten pruefen, kein Crash.

- [ ] **Step 6: Commit**

```bash
git add algo/backtest_bt.py
git commit -m "fix(algo): SilverBulletStrategy nutzt jetzt Risiko-basiertes Sizing statt ~100% Equity-Notional"
```

---

### Task 4: `algo/validate.py` -- `dubious_pct` in jeden Report

**Files:**
- Modify: `algo/validate.py`

**Interfaces:**
- Consumes: `pnl.dubious_pct(trades: pd.DataFrame) -> float` (aus Task 1).
- Produces: Erweiterte Textausgabe von `parameter_sensitivity()`, `walk_forward()`, `monte_carlo()` -- Spalte/Zeile `Dubious%`. Signatur der drei Funktionen bleibt unveraendert (nur Print-Output erweitert), daher keine Anpassung an `backtest_walkforward.py`/`validate_ensemble.py`/`stress_test.py` noetig.

- [ ] **Step 1: Import ergaenzen**

In `algo/validate.py`, nach `from backtesting import Backtest` ergaenzen:

```python
from pnl import dubious_pct
```

- [ ] **Step 2: `parameter_sensitivity()` um Dubious%-Spalte erweitern**

Den Block

```python
    print(f"1. Parameter-Sensitivitaet ({title})")
    print(f"   {col_label:>{col_width}}  {'Trades':>7}  {'WinRate%':>9}  {'ProfitFactor':>13}  {'Expectancy%':>12}")
    for value in candidates:
        stats = baseline if (baseline is not None and value == baseline_value) else \
            run(df, strategy_cls, bt_kwargs, param_name, value)
        pf = stats["Profit Factor"]
        pf_str = f"{pf:.3f}" if pf == pf else "n/a"
        value_str = value_fmt(value) if value_fmt else str(value)
        print(f"   {value_str:>{col_width}}  {stats['# Trades']:>7}  {stats['Win Rate [%]']:>9.1f}  "
              f"{pf_str:>13}  {stats['Expectancy [%]']:>12.3f}")
```

ersetzen durch:

```python
    print(f"1. Parameter-Sensitivitaet ({title})")
    print(f"   {col_label:>{col_width}}  {'Trades':>7}  {'WinRate%':>9}  {'ProfitFactor':>13}  "
          f"{'Expectancy%':>12}  {'Dubious%':>9}")
    for value in candidates:
        stats = baseline if (baseline is not None and value == baseline_value) else \
            run(df, strategy_cls, bt_kwargs, param_name, value)
        pf = stats["Profit Factor"]
        pf_str = f"{pf:.3f}" if pf == pf else "n/a"
        value_str = value_fmt(value) if value_fmt else str(value)
        print(f"   {value_str:>{col_width}}  {stats['# Trades']:>7}  {stats['Win Rate [%]']:>9.1f}  "
              f"{pf_str:>13}  {stats['Expectancy [%]']:>12.3f}  {dubious_pct(stats._trades):>9.1f}")
```

- [ ] **Step 3: `walk_forward()` um OOS-Dubious%-Spalte erweitern**

Den Block

```python
    print(f"2. Walk-Forward ({n_folds} rollierende Folds, ~{fold_len} Handelstage je Fold)")
    header = is_col_label if is_col_label is not None else ("IS " + (param_name or "Modell"))
    print(f"   {'Fold':>4}  {header:>{is_col_width}}  {'OOS Trades':>10}  "
          f"{'OOS WinRate%':>12}  {'OOS ProfitFactor':>16}  {'OOS Expectancy%':>15}")
```

ersetzen durch:

```python
    print(f"2. Walk-Forward ({n_folds} rollierende Folds, ~{fold_len} Handelstage je Fold)")
    header = is_col_label if is_col_label is not None else ("IS " + (param_name or "Modell"))
    print(f"   {'Fold':>4}  {header:>{is_col_width}}  {'OOS Trades':>10}  "
          f"{'OOS WinRate%':>12}  {'OOS ProfitFactor':>16}  {'OOS Expectancy%':>15}  {'OOS Dubious%':>13}")
```

und den Block

```python
        oos_pf_str = f"{oos_pf:.3f}" if oos_pf == oos_pf else "n/a"
        print(f"   {i + 1:>4}  {fold_label!s:>{is_col_width}}  {oos['# Trades']:>10}  "
              f"{oos['Win Rate [%]']:>12.1f}  {oos_pf_str:>16}  {oos['Expectancy [%]']:>15.3f}")
```

ersetzen durch:

```python
        oos_pf_str = f"{oos_pf:.3f}" if oos_pf == oos_pf else "n/a"
        print(f"   {i + 1:>4}  {fold_label!s:>{is_col_width}}  {oos['# Trades']:>10}  "
              f"{oos['Win Rate [%]']:>12.1f}  {oos_pf_str:>16}  {oos['Expectancy [%]']:>15.3f}  "
              f"{dubious_pct(oos._trades):>13.1f}")
```

- [ ] **Step 4: `monte_carlo()` um Dubious%-Zeile erweitern**

Den Block

```python
    print(f"3. Monte Carlo ({header_prefix}n={n} Trades, {n_sims} Resamples der Trade-Reihenfolge)")
    if n < 10:
```

ersetzen durch:

```python
    print(f"3. Monte Carlo ({header_prefix}n={n} Trades, {n_sims} Resamples der Trade-Reihenfolge)")
    print(f"   Baseline mehrdeutige Trades (Stop/Ziel in derselben Kerze, Fill-Reihenfolge "
          f"unbekannt): {dubious_pct(baseline._trades):.1f}%")
    if n < 10:
```

- [ ] **Step 5: Regressionslauf gegen SilverBulletStrategy und EnsembleStrategy**

Run: `python algo/backtest_walkforward.py MNQ`
Expected: Laeuft durch, Ausgabe enthaelt in Abschnitt 1 die Spalte `Dubious%`, in Abschnitt 2 die
Spalte `OOS Dubious%`, in Abschnitt 3 die Zeile `Baseline mehrdeutige Trades ...`.

Run: `python algo/validate_ensemble.py MNQ`
Expected: Gleiches Muster (nutzt dieselben `validate.py`-Funktionen ueber `walk_forward()`/`monte_carlo()`).

- [ ] **Step 6: Commit**

```bash
git add algo/validate.py
git commit -m "feat(algo): dubious_pct als Pflichtzeile in Parameter-Sensitivitaet/Walk-Forward/Monte-Carlo"
```

---

### Task 5: `algo/stress_test.py` -- `dubious_pct` + dokumentierte Grenze fuer $-P&L

**Files:**
- Modify: `algo/stress_test.py`

**Interfaces:**
- Consumes: `pnl.dubious_pct` (aus Task 1).

**Bewusst NICHT gefixt (dokumentierte Grenze, kein stiller Fix):** Der Tages-Fallback-Modus von
`EnsembleStrategy` (`intraday=False`) sized ueber die Equity-Fraction-Logik der `backtesting`-Lib
(kein `size`-Argument bei `self.buy()`/`self.sell()` in diesem Zweig), nicht ueber echte
Kontrakte -- ein `pnl.real_pnl()`-Aufruf waere hier praezise falsch (irrefuehrende Genauigkeit).
Diese Grenze wird explizit dokumentiert statt uebernommen, siehe Fehlerbehandlung im Spec.

- [ ] **Step 1: Import ergaenzen**

In `algo/stress_test.py`, nach `from backtest_ensemble import EnsembleStrategy, fit_model, bias_series  # noqa: E402` ergaenzen:

```python
from pnl import dubious_pct  # noqa: E402
```

- [ ] **Step 2: Report-Zeile in `run_window()` erweitern**

Den Block

```python
    print(f"   Trades={stats['# Trades']}  Max-Drawdown={stats['Max. Drawdown [%]']:.1f}%  "
          f"Profit-Factor={pf_str}")
```

ersetzen durch:

```python
    print(f"   Trades={stats['# Trades']}  Max-Drawdown={stats['Max. Drawdown [%]']:.1f}%  "
          f"Profit-Factor={pf_str}  Dubious%={dubious_pct(stats._trades):.1f}")
    print("   Hinweis (2026-08-06-Audit): pnl.real_pnl() wird hier bewusst NICHT aufgerufen -- "
          "der Tages-Fallback-Modus sized ueber Equity-Fraction (~99.99%), nicht ueber echte "
          "Kontrakte, ein $-Betrag waere darum irrefuehrend genau. Offener Punkt fuer einen "
          "eigenen Spec, falls dieser Modus je fuer echten Handel genutzt wird.")
```

- [ ] **Step 3: Regressionslauf**

Run: `python algo/stress_test.py covid`
Expected: Laeuft durch, Ausgabe enthaelt `Dubious%=` und die Hinweis-Zeile.

- [ ] **Step 4: Commit**

```bash
git add algo/stress_test.py
git commit -m "feat(algo): stress_test dubious_pct + dokumentierte Grenze fuer Tages-Fallback-Sizing"
```

---

### Task 6: `algo/selfcheck.py` -- gebuendelter Regressions-Check (neu)

**Files:**
- Create: `algo/selfcheck.py`

**Interfaces:**
- Consumes: `pnl.demo`, `rules.demo`, `signals._demo`, `backtest_ensemble._demo` (aus Tasks 1-2 und bestehendem Code).
- Produces: CLI-Kommando mit Exit-Code 0 (alle Checks bestanden) oder 1 (mind. einer fehlgeschlagen) -- Grundlage fuer den taeglichen Regressions-Baustein aus Teilprojekt B.

- [ ] **Step 1: `algo/selfcheck.py` schreiben**

```python
#!/usr/bin/env python3
"""Buendelt alle demo()-Selbstchecks aus dem Praezisions-Audit
(docs/superpowers/specs/2026-08-06-algo-backtest-precision-audit-design.md) zu einem
Kommando -- gedacht als schneller taeglicher Regressions-Check (Sekunden, kein neuer
Backtest-Lauf, buendelt nur bestehende kleine Checks). Die Ausloese-Mechanik (Erinnerung/Loop)
ist Teil von Teilprojekt B, nicht dieses Moduls.

Aufruf:
    python algo/selfcheck.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from pnl import demo as pnl_demo  # noqa: E402
from rules import demo as rules_demo  # noqa: E402
from signals import _demo as signals_demo  # noqa: E402
from backtest_ensemble import _demo as ensemble_demo  # noqa: E402

CHECKS = [
    ("pnl", pnl_demo),
    ("rules", rules_demo),
    ("signals", signals_demo),
    ("backtest_ensemble", ensemble_demo),
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

- [ ] **Step 2: Lauf bestaetigen**

Run: `python algo/selfcheck.py`
Expected: Vier `[OK]`-Zeilen, danach `Alle 4 Selbstchecks bestanden.`, Exit-Code 0.

- [ ] **Step 3: Absichtlichen Fehlschlag provozieren, um den Fail-Pfad zu pruefen**

Temporaer in `algo/pnl.py::demo()` eine falsche Assertion einfuegen (`assert 1 == 2`), dann:

Run: `python algo/selfcheck.py`
Expected: `[FAIL] pnl: ...`, danach `1/4 Selbstchecks fehlgeschlagen.`, Exit-Code 1.

Die temporaere Assertion danach wieder entfernen (Datei zurueck auf den Stand von Task 1).

- [ ] **Step 4: Commit**

```bash
git add algo/selfcheck.py
git commit -m "feat(algo): selfcheck.py buendelt alle demo()-Regressionschecks in einem Kommando"
```

---

### Task 7: Security-Scan (einmalig) + Dokumentation des Befunds

**Files:**
- Modify: keine Code-Datei (Befund fliesst in Task 9 `algo/README.md` ein)

Kein neuer Code -- dieser Task ist eine Verifikation mit dokumentiertem Ergebnis.

- [ ] **Step 1: Pruefen, dass Secrets nicht versioniert sind**

Run: `git check-ignore -v algo/.secrets.yaml`
Expected: Zeile `.gitignore:25:algo/.secrets.yaml	algo/.secrets.yaml` (Datei ist gitignored)

Run: `git log --all --oneline -- algo/.secrets.yaml`
Expected: leere Ausgabe (nie committet)

- [ ] **Step 2: Grep nach hartkodierten Secrets/Keys in `algo/*.py`**

Run: `grep -rniE "api[_-]?key|secret|token|password" algo/*.py`
Expected: Einzige Treffer sind Parameter-/Variablennamen in `algo/fetch_fred.py` (`api_key`
als Funktionsparameter, geladen aus der gitignored `algo/.secrets.yaml` via
`yaml.safe_load(...)["fred_api_key"]`) -- kein hartkodierter Wert.

- [ ] **Step 3: Befund notieren**

Ergebnis fuer Task 9 (`algo/README.md`) vormerken: "Security-Scan 2026-08-06: keine
hartkodierten Secrets in `algo/*.py`, `algo/.secrets.yaml` korrekt gitignored und nie
committet. Naechster Scan: woechentlich oder sobald eine echte IBKR-Anbindung (Broker-Keys)
dazukommt."

Kein Commit in diesem Task (keine Code-Aenderung).

---

### Task 8: Exploratorische `backtest_*.py`-Skripte -- Lookahead-Checkliste

**Files:**
- Read (Audit, keine Aenderung erwartet sofern Checkliste bestanden wird): `algo/backtest_daily_patterns.py`, `algo/backtest_fred_events.py`, `algo/backtest_ndog.py`, `algo/backtest_nwog.py`, `algo/backtest_ohlc.py`, `algo/backtest_org_ce.py`, `algo/backtest_seasonal.py`, `algo/backtest_tgif.py`, `algo/backtest_fvg_specialness.py`, `algo/backtest_midnight_range_std.py`, `algo/backtest_midnight_range_judas.py`
- Modify: nur die Datei(en), bei denen die Checkliste einen echten Verstoss findet

Diese Skripte rufen nachweislich nicht die `backtesting`-Engine auf (per
`grep -rn "Backtest(\|class.*Strategy" algo/*.py` bestaetigt, 2026-08-06) -- sie sind reine
statistische Zaehl-/Korrelationsskripte, keine Trade-Simulationen. Der Punktwert-Layer aus
Task 1-3 betrifft sie nicht; das verbleibende Risiko ist Lookahead-Bias in der Statistik.

- [ ] **Step 1: Jede Datei gegen diese drei Kriterien pruefen**

1. Jede Kennzahl fuer Tag `D` verwendet ausschliesslich Daten mit Tag `<= D` (bzw. `< D`, wenn
   die Funktion explizit den Folgetag vorhersagt) -- kein Zugriff auf `rows[i+1:]` oder spaetere
   Indizes wenn ueber Tag `i` berichtet wird.
2. Joins gegen externe Zeitreihen (FRED/VIX) verwenden `nearest_on_or_before()` (siehe
   `backtest_fred_events.py`) oder aequivalente Vergangenheits-Only-Logik, nie den naechstliegenden
   Wert unabhaengig von der Richtung.
3. Keine Off-by-One-Fehler beim Slicen (`history[:-1]` vs. `history[:]`, `range(n)` vs.
   `range(n-1)`) an Stellen, die eine Kennzahl mit dem Folgetag vergleichen.

Fuer jede Datei das Ergebnis (bestanden / Fund + Fix) in einer Liste festhalten -- diese Liste
wird woertlich in `algo/README.md` (Task 9) unter "Exploratorische Skripte" uebernommen.

- [ ] **Step 2: Gefundene Verstoesse direkt reparieren**

Falls Kriterium 1-3 an einer Stelle verletzt ist: Fix analog zum bestehenden Muster in
`signals.py` (`history[:i+1]`, `target_day = rows[i+1]["day"]`) anwenden, danach das Skript
einmal laufen lassen (`python algo/backtest_<name>.py`) und pruefen, dass es weiterhin ohne
Exception durchlaeuft.

- [ ] **Step 3: Commit (nur falls Fixes noetig waren)**

```bash
git add algo/backtest_<betroffene_datei>.py
git commit -m "fix(algo): Lookahead-Verstoss in backtest_<name>.py behoben (2026-08-06-Audit)"
```

Falls keine Datei einen Fund hatte: kein Commit in diesem Task, Ergebnis fliesst trotzdem in
Task 9 ein ("alle 11 Skripte bestehen die Lookahead-Checkliste, Stand 2026-08-06").

---

### Task 9: `algo/README.md` -- Modul-Dokumentation (neu)

**Files:**
- Create: `algo/README.md`

**Interfaces:**
- Consumes: Ergebnisse aus Task 1-8 (welche Bugs gefunden/gefixt wurden, Security-Scan-Befund, Lookahead-Checklisten-Ergebnis).

- [ ] **Step 1: `algo/README.md` schreiben**

```markdown
# algo/ -- Backtesting fuer MNQ

Ziel des gesamten Ordners: ein Handelsalgorithmus, der eigenstaendig ueber Interactive Brokers
handelt (siehe `algo/PLAN.md`, Schicht 1). Dieses Dokument erklaert **jedes Modul, das an
Backtest-Zahlen beteiligt ist**: was es testet, wie, warum genau so, und welche Grenzen es hat --
Zielgruppe ist der Nutzer selbst, ohne dass er den Code lesen muss.

> Praezisions-Audit 2026-08-06: siehe
> `docs/superpowers/specs/2026-08-06-algo-backtest-precision-audit-design.md` fuer den vollen
> Hintergrund. Kernaenderung: `algo/pnl.py` bringt echten Dollar-P&L (Punktwert statt
> Notional-Prozent) und konservative Behandlung mehrdeutiger Trades in jeden Report.

## `pnl.py` -- Praezisions-Layer

**Was:** Rechnet aus den rohen Preis-Trades der `backtesting`-Bibliothek den echten
Dollar-Gewinn/Verlust (`real_pnl`), markiert Trades mit unklarer Stop/Ziel-Reihenfolge
(`flag_dubious`, `dubious_pct`) und berechnet Risiko-basierte Kontraktgroessen (`risk_size`).
**Wie:** Punktwert-Tabelle nur fuer genutzte Symbole (MNQ=$2, NQ=$20, ES=$50). Mehrdeutige
Trades (Entry- und Exit-Zeit in derselben Kerze) werden konservativ als haetten sie den Stop
getroffen bewertet, nicht dem optimistischen Ergebnis der Lib vertraut.
**Warum:** Die `backtesting`-Lib rechnet P&L wie eine Aktie (Preisdifferenz * Stueckzahl ohne
Punktwert) -- fuer MNQ ($2/Punkt) war dadurch sowohl die reale Positionsgroesse als auch der
reale Dollar-Gewinn falsch (siehe Bug-Funde unten).
**Bekannte Grenzen:** Punktwert-Tabelle deckt nur MNQ/NQ/ES ab; ein neues Symbol braucht einen
neuen Eintrag, bevor `real_pnl`/`risk_size` dafuer nutzbar sind (wirft sonst `ValueError`).

## `rules.py` -- Silver-Bullet-Regel (Signal-Schicht)

**Was:** `plan_trade(bars, when)` liefert ein Setup (Entry/Stop/Ziel) oder `None`, basierend auf
dem Silver-Bullet-Modell aus `wiki/models/Silver Bullet Model.md`.
**Wie:** FVG im aktiven Zeitfenster (London/NY AM/NY PM) + unberuehrte Zielliquiditaet als
Confluenz-Pflicht. Nutzt nur `bars[t<=when]`, nie die volle Reihe (kein Lookahead).
**Warum:** Erste konkrete, deterministische Regel aus dem Wiki, testbar per Backtest statt nur
diskretionaer nachvollziehbar.
**Bekannte Grenzen:** Nur die Basisregel (Fenster+FVG+Ziel), zusaetzliche Wiki-Confluenz
(NWOG/NDOG, Midnight-Fibs) noch nicht eingebaut (siehe `algo/PLAN.md`).

## `signals.py` -- Tages-Bias-Signale

**Was:** Acht Einzel-Signalfunktionen (Wochentag, Turn-of-Month, Range-/Richtungs-Autokorrelation,
Stat-Arb-Spread MNQ/ES, VIX-Regime, DGS10-Aenderung, WALCL-Trend), kombiniert zu einer
Feature-Matrix `build_features()`.
**Wie:** Jede Funktion sieht nur Tage strikt vor `target_day`; Kalenderwissen ueber `target_day`
selbst (Wochentag) ist erlaubt, Kursdaten nicht.
**Warum:** Rohmaterial fuer das Ensemble-Bias-Modell in `backtest_ensemble.py`.
**Bekannte Grenzen:** `_in_tom_window()` naehert Turn-of-Month ueber Kalendertage an, nicht
echte Handelstage (kein Handelskalender im Projekt, siehe `ponytail`-Kommentar im Code).
**Audit 2026-08-06:** kein Lookahead gefunden, keine Aenderung noetig.

## `backtest_bt.py` -- Silver-Bullet-Trade-Simulation

**Was:** Verdrahtet `rules.py::plan_trade` als `backtesting.Strategy`, laeuft ueber alle
verfuegbaren MNQ-Tage.
**Wie:** Pro 5m-Kerze wird `plan_trade()` mit der Historie bis zu dieser Kerze aufgerufen; bei
Setup wird eine Bracket-Order (Limit + SL + TP) platziert.
**Warum:** Zeigt, ob die Silver-Bullet-Regel ohne Confluenz-Filter profitabel ist.
**Bug gefixt (2026-08-06-Audit):** Bestellungen hatten bisher KEINE explizite Groesse -- die
Lib nutzte ihren Default (~99,99 % Kontoguthaben als Notional), nicht die im Wiki festgelegte
1-%-Risiko-Regel. Jetzt: `pnl.risk_size()` bestimmt die Kontraktzahl, `main()` druckt zusaetzlich
den echten $-P&L (`pnl.real_pnl`) und den Anteil mehrdeutiger Trades.
**Bekannte Grenzen:** Nutzt weiterhin `backtesting`s Equity-/Drawdown-Tracking in rohen
Preispunkten (Sharpe/Return% sind Naeherungen), nur `RealPnL_USD` ist der echte Dollar-Wert.

## `backtest_ensemble.py` -- RenTec-artiges Ensemble

**Was:** Taeglicher Bias aus Logistic Regression ueber `signals.py`, filtert die
Silver-Bullet-Intraday-Regel statt sie zu ersetzen; `intraday=False` haelt stattdessen eine
tagesbasierte Position (fuer Perioden ohne 5m-Daten, siehe `stress_test.py`).
**Wie:** Bias-Totzone 45-55 % Wahrscheinlichkeit -> "neutral" (kein Trade). Partial-Taking am
ersten Swing-Punkt in Traderichtung + Stop auf Breakeven danach.
**Warum:** Kombiniert mehrere schwache statistische Einzelbefunde statt sich auf eine
diskretionaere Regel zu verlassen (siehe `docs/superpowers/specs/2026-08-05-algo-rentec-ensemble-design.md`).
**Bug gefixt (2026-08-06-Audit):** `_risk_size()` vergass den Punktwert-Faktor -- reales Risiko
pro Trade war dadurch doppelt so hoch wie die beabsichtigten 1 % (bei MNQ, $2/Punkt). Jetzt:
`pnl.risk_size()` mit `EnsembleStrategy.point_value`.
**Bekannte Grenzen:** ~150 Handelstage, 8 Features -- Overfitting-Risiko trotz L2-Regularisierung
(siehe Docstring), nur Walk-Forward-Zahlen (nicht der In-Sample-Baseline) sind belastbar.

## `validate.py` -- Monte Carlo / Walk-Forward / Parameter-Sensitivitaet

**Was:** Drei generalisierte Validierungsverfahren, unabhaengig von der konkreten Strategie
(genutzt von `backtest_walkforward.py` fuer Silver Bullet und `validate_ensemble.py` fuers
Ensemble).
**Wie:** Walk-Forward nutzt rollierende Folds (In-Sample-Parameterwahl bzw. `on_fold_train`-Hook
fuer Modell-Refit, Out-of-Sample-Test); Monte Carlo resampled die Trade-Reihenfolge 1000x fuer
Renditeverteilung/Drawdown-Perzentile.
**Warum:** Eine einzelne Backtest-Zahl ist ueberfitting-anfaellig; diese drei Verfahren zeigen,
wie stabil ein Ergebnis ueber Zeit/Parameter/Trade-Reihenfolge ist.
**Ergaenzt (2026-08-06-Audit):** `dubious_pct` ist jetzt Pflichtzeile in allen drei
Ausgaben -- zeigt, wie gross der Anteil an Trades mit unklarer Stop/Ziel-Reihenfolge ist.
**Bekannte Grenzen:** Kleine Stichprobe (siehe `algo/PLAN.md`) -- alle Zahlen sind
Groessenordnungen, keine belastbaren Ergebnisse, bis mehr Handelstage vorliegen.

## `stress_test.py` -- Historische Krisenfenster

**Was:** Testet `EnsembleStrategy(intraday=False)` gegen fuenf historische Krisenfenster (2008,
Covid, Flash Crash 2010, China 2015, Volmageddon 2018) auf NQ=F/ES=F-Tagesdaten (MNQ existiert
als Instrument erst seit 2019).
**Wie:** Bias-Modell wird strikt auf Vorlauf-Daten VOR Fenster-Start gefittet (kein
Data-Leakage aus der Krise selbst).
**Warum:** Verhaltens-Charakterisierung (Drawdown, Trade-Anzahl) in Extremsituationen, nicht als
Ersatz fuer die eigentliche Validierung.
**Ergaenzt (2026-08-06-Audit):** `dubious_pct` in der Report-Zeile.
**Bekannte, bewusst NICHT gefixte Grenze:** Der Tages-Fallback-Modus sized ueber Equity-Fraction
(~99,99 %), nicht ueber echte Kontrakte -- `pnl.real_pnl()` wird hier absichtlich NICHT
aufgerufen, ein $-Betrag waere irrefuehrend praezise. Offener Punkt fuer einen eigenen Spec,
falls dieser Modus je fuer echten Handel genutzt wird. Ausserdem: KEINE echte MNQ-P&L (NQ=F-Preis-
Proxy), `margin=0.05` (20x Hebel) OHNE Stop-Loss -- die Drawdown-Zahl ist Hebel-Mechanik, kein
Modellversagen.

## `dashboard.py` -- Live-Anschauungsfenster

**Was:** Matplotlib-Live-Fenster (oder GIF-Export), zeigt Preis/Entries/Equity/Drawdown/Signale
Kerze fuer Kerze oder Tag fuer Tag.
**Wie:** Eigene, einfachere Simulationsschleife (nicht die `backtesting`-Lib) -- Equity als
relativer Multiplikator (Start=1.0, prozentual), Sofort-Fill-Naeherung statt Limit-Order.
**Warum:** Reines Anschauungswerkzeug, damit der Backtest-Ablauf sichtbar statt nur Text ist.
**Wichtig:** **Nicht die Quelle der offiziellen Kennzahlen** (das ist `validate.py`/
`validate_ensemble.py`) -- Trades/WinRate hier sind wegen der Sofort-Fill-Naeherung nicht direkt
mit den offiziellen Zahlen vergleichbar. Titel im Fenster sagt das auch explizit ("keine
offizielle Kennzahl").
**Bekannte Grenzen:** Kein echter Dollar-Bezug (relative Prozent-Equity) -- fuer Optik/Anschauung
ausreichend, fuer Kapitalentscheidungen nicht gedacht. Bloomberg-Terminal-artige Optik ist
expliziter Zukunftswunsch (siehe `project_algo_precision_audit`-Memory), aktuell nicht geplant.

## `selfcheck.py` -- Gebuendelter Regressions-Check

**Was:** Buendelt alle `demo()`/`_demo()`-Selbstchecks (`pnl`, `rules`, `signals`,
`backtest_ensemble`) zu einem Kommando.
**Wie:** `python algo/selfcheck.py` -- Sekunden, kein neuer Backtest-Lauf.
**Warum:** Schneller taeglicher Regressions-Baustein, damit ein kuenftiger Code-Fix nicht
unbemerkt einen der hier gefixten Bugs reproduziert. Ausloese-Mechanik (Erinnerung/Loop) ist
Teil von Teilprojekt B.

## Exploratorische Skripte (`backtest_daily_patterns.py`, `backtest_fred_events.py`,
`backtest_ndog.py`, `backtest_nwog.py`, `backtest_ohlc.py`, `backtest_org_ce.py`,
`backtest_seasonal.py`, `backtest_tgif.py`, `backtest_fvg_specialness.py`,
`backtest_midnight_range_std.py`, `backtest_midnight_range_judas.py`)

**Was:** Reine statistische Zaehl-/Korrelationsskripte (Wochentag-Effekt, Turn-of-Month,
NDOG/NWOG-Bias, TGIF, FVG-Besonderheiten, Midnight-Range-STD/Judas-Swing, FRED-Events) --
nutzen NICHT die `backtesting`-Engine (bestaetigt per Grep, 2026-08-06), daher betrifft sie der
Punktwert-Layer aus `pnl.py` nicht.
**Audit 2026-08-06:** [Ergebnis aus Task 8 Step 1 hier eintragen -- entweder "alle 11 Skripte
bestehen die Lookahead-Checkliste" oder Liste der gefundenen+gefixten Verstoesse.]

## Security-Scan

2026-08-06: keine hartkodierten Secrets in `algo/*.py` gefunden. `algo/.secrets.yaml`
(FRED-API-Key) ist korrekt gitignored und wurde nie committet. Naechster Scan: woechentlich
oder sobald eine echte IBKR-Broker-Anbindung (Live-Keys) dazukommt -- taeglich waere aktuell
unnoetiger Aufwand ohne Live-Handel.
```

Die eckige Klammer `[Ergebnis aus Task 8 Step 1 hier eintragen ...]` MUSS vor dem Commit durch
das tatsaechliche Ergebnis aus Task 8 ersetzt werden -- das ist kein Platzhalter im
Implementierungsplan selbst (der hier beschriebene Text ist eine Anleitung fuer den
ausfuehrenden Engineer, keine Endfassung).

- [ ] **Step 2: Platzhalter durch das tatsaechliche Task-8-Ergebnis ersetzen**

Den Satz mit der eckigen Klammer durch den in Task 8 Step 1 dokumentierten Befund ersetzen,
z.B.: `Audit 2026-08-06: alle 11 Skripte bestehen die Lookahead-Checkliste (keine Funde).` oder
die entsprechende Fund-Liste.

- [ ] **Step 3: Commit**

```bash
git add algo/README.md
git commit -m "docs(algo): README.md -- Modul-Dokumentation aus dem Praezisions-Audit"
```

---

### Task 10: `algo/PLAN.md` -- Abschliessender Log-Eintrag

**Files:**
- Modify: `algo/PLAN.md`

**Interfaces:**
- Consumes: Ergebnisse aus allen vorherigen Tasks.

- [ ] **Step 1: Log-Eintrag anhaengen**

Am Ende der Log-Tabelle in `algo/PLAN.md` (nach der letzten bestehenden Zeile, gleiche
Tabellenkonvention `| Datum | Ereignis |`) folgende Zeile ergaenzen:

```markdown
| 2026-08-06 | **Praezisions-Audit abgeschlossen** (Spec: docs/superpowers/specs/2026-08-06-algo-backtest-precision-audit-design.md, Plan: docs/superpowers/plans/2026-08-06-algo-backtest-precision-audit.md). Neu: algo/pnl.py (echter $-P&L nach Punktwert MNQ=$2/NQ=$20/ES=$50, konservative Mehrdeutigkeits-Aufloesung, Risiko-Sizing), algo/selfcheck.py, algo/README.md. Zwei echte Bugs gefixt: (1) backtest_ensemble.py::_risk_size vergass den Punktwert-Faktor -- reales Risiko war doppelt so hoch wie die beabsichtigten 1%; (2) backtest_bt.py::SilverBulletStrategy hatte GAR keine Risiko-Begrenzung (Lib-Default ~100% Equity-Notional statt 1%-Regel). dubious_pct (Anteil Trades mit Stop/Ziel in derselben Kerze) ist jetzt Pflichtzeile in jedem Report (validate.py, stress_test.py, backtest_bt.py). Bewusst nicht gefixt: stress_test.py's Tages-Fallback-Sizing (dokumentierte Grenze, kein $-Betrag ausgewiesen). Security-Scan: keine Funde. Teilprojekt B (Wiki-Strategie-Findung, taegliche Erinnerung) folgt als eigener Spec. |
```

- [ ] **Step 2: Commit**

```bash
git add algo/PLAN.md
git commit -m "docs(algo): PLAN.md Log-Eintrag fuer den abgeschlossenen Praezisions-Audit"
```

---

## Self-Review-Notiz (fuer den ausfuehrenden Engineer)

- **Spec-Abdeckung:** Teil 1 (Praezisions-Layer) -> Task 1-5. Teil 2 (Datei-Reihenfolge) -> Tasks
  1-3, 5, 8 (Reihenfolge exakt aus dem Spec uebernommen; `signals.py` selbst brauchte laut Audit
  keine Aenderung, siehe README-Eintrag). Teil 3 (Deliverables) -> Task 6 (`selfcheck.py`),
  Task 7 (Security-Scan), Task 9 (`README.md`), Task 10 (`PLAN.md`-Log).
- **`dashboard.py`:** Laut Nutzer (2026-08-06) laeuft es bereits fehlerfrei -- kein Code-Fix-Task
  noetig, nur der README-Eintrag in Task 9 dokumentiert die bestehende Funktionsweise/Grenze.
- **Nicht Teil dieses Plans:** Teilprojekt B (Wiki-gestuetzte Strategie-Findung, taegliche
  Erinnerung, Bloomberg-Terminal-Optik) -- eigener, spaeterer Spec (siehe
  `project_algo_precision_audit`-Memory).
