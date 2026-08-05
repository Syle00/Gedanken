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
from backtest_fred_events import load_fred, nearest_on_or_before  # noqa: E402

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


def _demo() -> None:
    hist = []
    for i in range(70):
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
    trending_up = [{"day": date(2026, 4, 1) + timedelta(days=i), "open": 100 + i,
                     "close": 101 + i, "high": 102 + i, "low": 99 + i, "range": 3.0,
                     "ret_pct": 1.0, "bullish": True} for i in range(21)]
    assert signal_direction_autocorr(trending_up) == 1.0  # immer bullish nach bullish
    assert signal_range_autocorr(trending_up) is not None
    assert signal_range_autocorr(trending_up[:10]) is None  # zu wenig Historie
    mnq_spread = [{"day": date(2026, 5, 1) + timedelta(days=i), "ret_pct": 2.0}
                  for i in range(19)] + [{"day": date(2026, 5, 20), "ret_pct": 10.0}]
    es_spread = [{"day": date(2026, 5, 1) + timedelta(days=i), "ret_pct": 2.0}
                 for i in range(20)]
    z_signal = signal_stat_arb(mnq_spread, es_spread, date(2026, 5, 21))
    assert z_signal is not None and z_signal < -0.5  # MNQ lief stark ab -> Mean-Reversion bearish
    assert signal_stat_arb(mnq_spread[:5], es_spread[:5], date(2026, 5, 21)) is None
    print("signals calendar+autocorr+statarb demo ok")

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


if __name__ == "__main__":
    _demo()
