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
