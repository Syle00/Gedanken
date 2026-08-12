# Quant-Riskmanagement — austauschbare Risk-Module (Design)

> Status: entworfen 2026-08-12, noch nicht implementiert. Ersetzt keine bestehende Datei,
> ergänzt `algo/pnl.py::risk_size()` um eine vorgeschaltete, austauschbare Schicht.

## Ziel

Die aktuelle Positionsgrößen-Regel ([[Risikomanagement (1% pro Trade)]]: feste 1% Risiko pro
Trade) ist die einzige existierende Regel im Vault. Ziel dieses Designs ist kein Ersatz dieser
Regel, sondern ein **Framework, das mehrere quantitative Risk-Ansätze gegeneinander testbar
macht** — dieselben Trade-Signale laufen durch verschiedene Sizing-Logiken, Ergebnisse werden
nebeneinander verglichen (Equity, Drawdown, Expectancy, VaR/ES). Das deckt sich mit
[[Algo-Trading: Arbeitsstandards]] ("jede neue These wird automatisch geloggt und
gebacktestet") und ist bewusst getrennt von der Frage, wo ein Stop platziert wird (das bleibt
Modell-Domäne, siehe `rules.py::plan_trade`) — Risk-Management entscheidet nur, WIE VIEL Kapital
bei einem gegebenen Entry/Stop riskiert wird, nicht WO der Stop liegt.

Der Nutzer plant weitere Strategien über das Silver Bullet Model hinaus — das Risk-Interface ist
deshalb **strategie-unabhängig**: es nimmt nur ein generisches `TradeSetup` (Entry, Stop,
Richtung, Zeitpunkt) entgegen, keine Strategie-Interna. Silver Bullet ist nur die erste
Testsignal-Quelle für den Vergleichs-Backtest, keine Festlegung für künftige Strategien.

## Architektur

Trennung von zwei bisher vermischten Fragen:

- **"Wie viel % Risiko?"** — unterscheidet die Module, neue Schicht
- **"Wie viele Kontrakte kauft das bei diesem %?"** — bleibt exakt die bestehende, geprüfte
  `pnl.py::risk_size(equity, max_risk_pct, entry, stop, point_value, max_notional)` — unangetastet

Jedes Sizing-Modul ist eine Funktion mit gleicher Signatur, die eine `max_risk_pct` liefert und
per `**ctx` nur zieht, was es braucht:

```python
def risk_pct(base_pct: float = 0.01, **ctx) -> float: ...
```

`SilverBulletStrategy` (`algo/backtest_bt.py`) bekommt ein neues Klassenattribut `risk_module`
(Default: `risk_fixed`, verhält sich dann exakt wie heute). `next()` ruft
`self.risk_module.risk_pct(hist=self._hist, closed_trades=self.closed_trades,
base_pct=self.max_risk_pct)` statt der festen Konstante auf. `self._hist` ist bereits lückenlos
und ohne Lookahead geführt (`extend_hist()` läuft vor jeder Positionsprüfung) — Voraussetzung für
GARCH, das nur auf Daten bis `when` fitten darf.

Zusätzlich ein Kill-Switch-Gate, das **vor** `risk_pct()` geprüft wird und unabhängig vom
gewählten Sizing-Modul greift.

## Die vier Bausteine

### 1. `algo/risk_fixed.py` — Baseline

```python
def risk_pct(base_pct: float = 0.01, **ctx) -> float:
    return base_pct
```

Reine Auslagerung der heutigen Konstante, kein Verhaltensunterschied zum Status quo.

### 2. `algo/risk_garch.py` — GARCH(1,1)-Vol-Skalierung

Skaliert nur das Risikobudget (die %), **nicht** die Stop-Distanz — Stop bleibt strukturell aus
`rules.py::plan_trade` (FVG-Gegenkante + Puffer). Kein neues Package: GARCH(1,1) hat 3 Parameter
(ω, α, β), MLE-Fit über `scipy.optimize.minimize` (bereits Dependency, siehe `masters.py`) auf
Log-Returns aus `hist`.

```
σ²_t      = ω + α·r²_{t-1} + β·σ²_{t-1}           # Vol-Prognose für die nächste Bar
vol_ratio = σ_prognose / σ_langfrist_median        # >1 = aktuell volatiler als üblich
risk_pct  = clip(base_pct / vol_ratio, 0.5·base_pct, 1.5·base_pct)
```

Clipping verhindert, dass ein Fit-Ausreißer die Größe sprengt (nie unter halbem, nie über 1,5×
Budget). Fallback auf `base_pct`, solange `len(hist) < 100` (zu wenig Historie für stabilen Fit).

### 3. `algo/risk_kelly.py` — Half-Kelly aus rollierenden Trade-Ergebnissen

Diskrete Trading-Kelly-Formel (Win/Loss-Trades, nicht die Portfolio-Rendite-Variante aus
[[Kelly-Criterion & Value-at-Risk (Money Management)]]):

```
p         = Trefferquote der letzten `window` (Default 30) abgeschlossenen Trades
b         = avg_win / avg_loss   (R-Multiple-Verhältnis)
f*        = p − (1−p)/b
risk_pct  = max(0, f*/2)          # Half-Kelly, nie negativ
```

Fallback auf `base_pct`, solange `< min_trades` (Default 20) abgeschlossene Trades vorliegen —
verhindert wilde Größen aus einer Schätzung auf 2-3 Trades. Nutzt `closed_trades` aus der
`backtesting`-Lib-Strategie (nur bereits abgeschlossene Trades vor dem aktuellen Zeitpunkt, kein
Lookahead).

### 4. `algo/risk_killswitch.py` — Drawdown-Kill-Switch pro Strategie

Kein `risk_pct`, sondern ein Gate, das vor jedem neuen Trade geprüft wird:

```python
def allowed(equity_curve: list[float], max_drawdown_pct: float = 0.15) -> bool:
    peak = max(equity_curve)
    dd = (peak - equity_curve[-1]) / peak
    return dd < max_drawdown_pct
```

Bei `False`: kein neuer Trade, unabhängig vom Sizing-Modul. Reset automatisch bei neuem
Equity-Hoch (kein manueller Reset nötig, `peak` ergibt sich immer aus der bisherigen Kurve).
Schwelle 15% als Default. Läuft **pro Strategie** (eigener Drawdown-Zähler ab eigenem
Equity-Hoch) — wichtig, weil weitere Strategien geplant sind und eine schlecht laufende
Strategie nicht automatisch alle anderen mitstoppen soll.

## VaR/ES — reine Report-Kennzahl

Bestimmt keine Positionsgröße, wird nach jedem Backtest-Lauf aus den Trade-Returns berechnet:
95%-Tages-VaR **und** Expected Shortfall (ES ist laut
[[Kelly-Criterion & Value-at-Risk (Money Management)]] methodisch überlegen — subadditiv,
erfasst Tail-Risiko jenseits der VaR-Schwelle, VaR allein nicht). Zusätzliche
Vergleichsdimension neben Equity/Drawdown/Expectancy, kein eigenes Sizing-Modul.

## Vergleichs-Harness

`algo/backtest_risk_compare.py` — läuft `SilverBulletStrategy` (Signal fix, alle 3
`risk_module`-Varianten, Kill-Switch läuft bei allen dreien mit, da unabhängig vom Sizing-Modul)
dreimal über denselben Datenbestand. Report pro Modul: Equity-Endstand, Max-Drawdown, Win-Rate,
Profit Factor, Expectancy, `dubious_pct` (Pflichtkennzahl gemäß
[[Algo-Trading: Arbeitsstandards]]), 95%-Tages-VaR, Expected Shortfall. Ausgabe als Tabelle
(Konsole + `wiki/synthesis/Risk-Management-Vergleich (laufend).md`, passend zum bestehenden
"(laufend)"-Muster für wachsende Datenbestände).

## Out of Scope (bewusst nicht Teil dieses Designs)

- Portfolio-Ebene (Exposure-Caps, Korrelations-Monitoring zwischen mehreren gleichzeitig offenen
  Strategien/Symbolen) — erst relevant, sobald mehr als eine Strategie gleichzeitig live läuft.
- Vol-adaptive Stop-Puffer (`stop_buffer_pct` in `SilverBulletStrategy`) — aktuell fest, wäre ein
  eigenständiger, späterer Backlog-Punkt, nicht Teil dieses Redesigns.
- Live-Anbindung (`algo/live_status.py`) — dieses Design ist Backtest-/Validierungs-Scope, gemäß
  Roadmap-Reihenfolge in `CLAUDE.md` (Validierung vor IBKR-Adapter).

## Dateien

Neu: `algo/risk_fixed.py`, `algo/risk_garch.py`, `algo/risk_kelly.py`,
`algo/risk_killswitch.py`, `algo/backtest_risk_compare.py`.
Geändert: `algo/backtest_bt.py` (`risk_module`-Klassenattribut + Kill-Switch-Gate in `next()`).

## Testing

Jedes Modul bekommt einen `__main__`/`_demo()`-Selfcheck (Konvention aus `pnl.py`) mit
Grenzfällen: `risk_garch` bei `len(hist) < 100` → `base_pct`; `risk_kelly` bei
`< min_trades` → `base_pct`, negatives `f*` → `0`; `risk_killswitch` bei erreichter Schwelle →
`False`, bei neuem Hoch → Reset auf `True`. `algo/selfcheck.py` bindet die neuen Selfchecks ein.
