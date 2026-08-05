#!/usr/bin/env python3
"""Live-Multi-Panel-Fenster fuer den Ensemble-Backtest -- eigene Simulationsschleife
(siehe docs/superpowers/specs/2026-08-05-algo-rentec-ensemble-design.md Phase 5), NICHT
die Quelle der offiziellen Kennzahlen (die kommen aus algo/validate_ensemble.py). Reines
Anschauungswerkzeug: reicht die Ergebnisse eines Backtest-Laufs Kerze fuer Kerze (oder Tag
fuer Tag bei --daily) an ein matplotlib-Fenster weiter.

Im `--stress`-Fall wird das Bias-Modell NUR auf Vorlauf-Daten strikt vor Fenster-Start
gefittet (analog algo/stress_test.py::run_window) -- sonst waere das Modell beim Replay
eines historischen Krisenfensters auch auf anderen Krisenfenstern und/oder der aktuellen
2026er-Periode trainiert, was fuer "was haette dieses Modell 2008 gezeigt" keinen Sinn
ergibt (Data-Leakage). Im normalen Live-Replay (ohne --stress) bleibt der Fit unrestricted
auf der vollen verfuegbaren Historie -- das entspricht, wie ein echtes Live-System
(algo/live_status.py) taeglich arbeitet.

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

    if a.stress and a.stress not in WINDOWS:
        print(f"Unbekanntes Stress-Fenster: {a.stress} (verfuegbar: {', '.join(WINDOWS)})")
        return 1

    mnq_symbol = "NQ" if a.stress else "MNQ"
    mnq_rows = load_rows(mnq_symbol)
    es_rows = load_rows("ES")
    if len(mnq_rows) < 30 or len(es_rows) < 10:
        print(f"Zu wenig Daten fuer ein Dashboard (MNQ/NQ n={len(mnq_rows)}, ES n={len(es_rows)}).")
        return 1

    if a.stress:
        # Fix (analog stress_test.py::run_window, Task-10-Bug): Modell-Fit strikt auf
        # Vorlauf-Daten VOR Fenster-Start beschraenken -- sonst faellt sofort raw/marktdaten
        # aus anderen Krisenfenstern (und der 2026er-Periode) mit ins Training, ein
        # Krisen-Replay waere dann kein "was haette das Modell damals gesagt" mehr.
        start, end = WINDOWS[a.stress]
        pre_crisis_mnq = [r for r in mnq_rows if r["day"] < start]
        pre_crisis_es = [r for r in es_rows if r["day"] < start]
        if len(pre_crisis_mnq) < 30 or len(pre_crisis_es) < 30:
            print(f"{a.stress}: zu wenig Vorlauf-Historie fuer Signale (NQ n={len(pre_crisis_mnq)}, "
                  f"ES n={len(pre_crisis_es)}) -- Dashboard kann nicht gebaut werden.")
            return 1
        model = fit_model(pre_crisis_mnq, pre_crisis_es)
        # Vorhersage/Anzeige ueber den vollen Bereich bis Fenster-Ende -- die Signale schauen
        # pro Tag nur rueckwaerts, das leakt nichts (siehe stress_test.py-Docstring).
        px_for_bias = [r for r in mnq_rows if r["day"] < end]
        es_for_bias = [r for r in es_rows if r["day"] < end]
        bias = bias_series(model, px_for_bias, es_for_bias)
        snapshot = signal_snapshot(px_for_bias, es_for_bias)

        df = load_daily_df("NQ", start, end)
        bars = [Bar(t, o, h, l, c) for t, o, h, l, c in
                zip(df.index, df.Open, df.High, df.Low, df.Close)]
        frames = simulate(bars, bias, intraday=False)
    else:
        model = fit_model(mnq_rows, es_rows)
        bias = bias_series(model, mnq_rows, es_rows)
        snapshot = signal_snapshot(mnq_rows, es_rows)

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
