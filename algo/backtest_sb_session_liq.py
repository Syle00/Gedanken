#!/usr/bin/env python3
"""Testet Jannes' These (2026-08-14, siehe wiki/concepts/Open Float & Liquidity Pools.md):
Previous Day High/Low und Previous Week High/Low sind starke, high-probability DOL --
bezogen auf das Silver Bullet Model.

Haelt Entry/Stop (5m-FVG im SB-Fenster, `rules.sb_entry_signal`) UNVERAENDERT und ersetzt nur
die Ziel-Liquiditaet: statt der swing-basierten `untouched_levels()` (Baseline) werden PDH/PDL/
PWH/PWL als feste `target_candidates` an `plan_trade()` gegeben (2026-08-14 in rules.py
ergaenzt). Reuse-first: Entry-Erkennung kommt unveraendert aus rules.py, Simulation nach dem
Muster von backtest_hp_fvg.py/backtest_sb_bellwether.py (konservative Fill-Reihenfolge, dubious
bei Stop+Ziel in derselben Kerze).

PDH/PDL = High/Low des letzten Handelstags vor `day` (1d-Datei). PWH/PWL = High/Low ueber alle
Handelstage der zuletzt VOLLSTAENDIG abgeschlossenen Kalenderwoche (Montag-Sonntag vor der
aktuellen Woche) -- beides zum Handelsbeginn von `day` bereits bekannt, kein Lookahead. Ein
Level zaehlt nur als Kandidat, wenn es bis `when` noch UNBERUEHRT ist (5m-Historie des Tages
hat es noch nicht gerissen) -- sonst waere es keine offene Ziel-Liquiditaet mehr.

Aufruf:
    python algo/backtest_sb_session_liq.py
    python algo/backtest_sb_session_liq.py --selfcheck
"""
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "algo"))

from analyze_ohlc import Bar, at, load  # noqa: E402
from backtest_1p_fvg_woche import find_days  # noqa: E402
from backtest_common import write_result  # noqa: E402
from pnl import POINT_VALUE  # noqa: E402
from rules import (sb_entry_signal, plan_trade, WINDOWS, daily_hilo_from_bars,  # noqa: E402
                    prev_day_level, prev_week_level, level_untouched)

SYMBOL = "MNQ"
COMMISSION_RT = 1.24


def daily_hilo(days_5m: dict[date, Path]) -> dict[date, tuple[float, float]]:
    """{Handelstag: (High, Low)} aus den 5m-Dateien -- NICHT aus den 1d-Dateien, siehe
    rules.daily_hilo_from_bars() (2026-08-14 umgestellt, Fund: mehrere 1d-Dateien stehen
    nicht mehr im Einklang mit ihren eigenen Intraday-Dateien, siehe algo/PLAN.md)."""
    return daily_hilo_from_bars({d: load(p) for d, p in days_5m.items()})


def untouched_candidates(hist: list[Bar], pdh, pdl, pwh, pwl) -> list[dict]:
    """PDH/PWH als buyside-, PDL/PWL als sellside-Kandidat -- nur wenn `hist` (5m des
    laufenden Tages bis `when`) das Level noch nicht gerissen hat."""
    out = []
    for level, side in ((pdh, "buyside"), (pwh, "buyside")):
        if level is not None and level_untouched(hist, level, side):
            out.append({"side": side, "level": level})
    for level, side in ((pdl, "sellside"), (pwl, "sellside")):
        if level is not None and level_untouched(hist, level, side):
            out.append({"side": side, "level": level})
    return out


def simulate(bars_5m: list[Bar], after_t, side: str, entry: float, stop: float,
             target: float) -> dict | None:
    bull = side == "long"
    future = [b for b in bars_5m if b.t > after_t]
    gefuellt = False
    for b in future:
        if not gefuellt:
            if b.l <= entry <= b.h:
                gefuellt = True
            else:
                continue
        hit_stop = b.l <= stop if bull else b.h >= stop
        hit_ziel = b.h >= target if bull else b.l <= target
        if hit_stop and hit_ziel:
            return {"won": False, "dubious": True, "pts": -abs(entry - stop)}
        if hit_stop:
            return {"won": False, "dubious": False, "pts": -abs(entry - stop)}
        if hit_ziel:
            return {"won": True, "dubious": False, "pts": abs(target - entry)}
    return None


def collect() -> list[dict]:
    d5 = find_days(SYMBOL, "5m")
    days = sorted(d5)
    hilo = daily_hilo(d5)

    bars_5m: list[Bar] = []
    for d in days:
        bars_5m.extend(load(d5[d]))
    bars_5m.sort(key=lambda b: b.t)

    rows = []
    for day in days:
        pd = prev_day_level(hilo, day)
        pw = prev_week_level(hilo, day)
        pdh, pdl = pd if pd else (None, None)
        pwh, pwl = pw if pw else (None, None)
        if pdh is None and pwh is None:
            continue

        for name, h0, h1 in WINDOWS:
            win_bars = [b for b in bars_5m if at(day, h0) <= b.t < at(day, h1)]
            entry_sig, when = None, None
            for b in win_bars:
                sig = sb_entry_signal(bars_5m, b.t)
                if sig is not None:
                    entry_sig, when = sig, b.t
                    break
            if entry_sig is None:
                continue
            window_name, side, entry, stop = entry_sig

            for variant, cands_fn in (
                ("Swing-Level (Baseline)", lambda: None),
                ("PDH/PDL", lambda: untouched_candidates(
                    [b for b in bars_5m if at(day, 0) <= b.t <= when], pdh, pdl, None, None)),
                ("PWH/PWL", lambda: untouched_candidates(
                    [b for b in bars_5m if at(day, 0) <= b.t <= when], None, None, pwh, pwl)),
                ("PDH/PDL + PWH/PWL", lambda: untouched_candidates(
                    [b for b in bars_5m if at(day, 0) <= b.t <= when], pdh, pdl, pwh, pwl)),
            ):
                cands = cands_fn()
                s = plan_trade(bars_5m, when, target_candidates=cands) if cands is not None \
                    else plan_trade(bars_5m, when)
                if s is None:
                    rows.append({"day": day, "window": name, "variant": variant,
                                 "target": None, "trade": None})
                    continue
                trade = simulate(bars_5m, when, side, entry, stop, s.target)
                rows.append({"day": day, "window": name, "variant": variant,
                             "target": s.target, "trade": trade})
    return rows


def stats(rows: list[dict]) -> dict:
    kein_ziel = sum(1 for r in rows if r["target"] is None)
    done = [r for r in rows if r["trade"] and r["trade"]["won"] is not None]
    dub = [r for r in done if r["trade"]["dubious"]]
    pnl = sum(r["trade"]["pts"] * POINT_VALUE[SYMBOL] - COMMISSION_RT for r in done)
    return {
        "fenster": len(rows), "ohne_zielliquiditaet": kein_ziel, "trades": len(done),
        "win_pct": round(100 * sum(r["trade"]["won"] for r in done) / len(done), 1) if done else None,
        "dubious_pct": round(100 * len(dub) / len(done), 1) if done else None,
        "usd_pro_trade": round(pnl / len(done), 2) if done else None,
        "usd_gesamt": round(pnl, 2),
    }


def run() -> dict:
    rows = collect()
    tage = sorted({r["day"] for r in rows}) if rows else []
    out = {"symbol": SYMBOL, "tage": len(tage), "varianten": {}}
    for variant in ("Swing-Level (Baseline)", "PDH/PDL", "PWH/PWL", "PDH/PDL + PWH/PWL"):
        out["varianten"][variant] = stats([r for r in rows if r["variant"] == variant])
    return out


def report(res: dict) -> list[str]:
    L = [f"=== Silver Bullet: PDH/PDL/PWH/PWL als Ziel-Liquiditaet ({res['symbol']}) ===", "",
         f"Handelstage: {res['tage']}", "",
         f"  {'Variante':<24}{'Fenster':>9}{'ohne Ziel':>11}{'Trades':>8}{'Win%':>7}"
         f"{'dub%':>6}{'$/Trade':>10}{'$ ges':>9}"]
    for name, s in res["varianten"].items():
        if not s["trades"]:
            L.append(f"  {name:<24}{s['fenster']:>9}{s['ohne_zielliquiditaet']:>11}{'0':>8}")
            continue
        L.append(f"  {name:<24}{s['fenster']:>9}{s['ohne_zielliquiditaet']:>11}"
                  f"{s['trades']:>8}{s['win_pct']:>7}{s['dubious_pct']:>6}"
                  f"{s['usd_pro_trade']:>10}{s['usd_gesamt']:>9}")
    n = max((s["trades"] for s in res["varianten"].values()), default=0)
    if n < 20:
        L += ["", f"⚠️  n={n} Trades in der groessten Variante -- bei dieser Groesse ist "
              "keine der Varianten von Rauschen unterscheidbar. Ergebnis vorlaeufig."]
    return L


def selfcheck() -> None:
    # prev_day_level/prev_week_level selbst sind bereits in rules.demo() getestet (dort her
    # verschoben, 2026-08-14) -- hier nur der Smoke-Test fuer daily_hilo() aus 5m-Bars statt
    # aus den 1d-Dateien.
    day = date(2026, 1, 5)
    bar = lambda hh, mm, o, h, l, c: Bar(at(day, hh, mm), o, h, l, c)  # noqa: E731
    hist = [bar(9, 30, 100, 102, 99, 101), bar(9, 35, 101, 103, 100, 102)]
    # PDH=110 (unberuehrt, hist-Hoch nur 103) -> Kandidat; PDH=101 (schon durchbrochen) -> nicht
    cands = untouched_candidates(hist, pdh=110.0, pdl=95.0, pwh=None, pwl=None)
    assert {"side": "buyside", "level": 110.0} in cands
    assert {"side": "sellside", "level": 95.0} in cands
    cands2 = untouched_candidates(hist, pdh=101.5, pdl=None, pwh=None, pwl=None)
    assert cands2 == [], "PDH bereits gerissen (hist-Hoch 103 > 101.5) darf kein Kandidat sein"

    assert daily_hilo_from_bars({day: hist}) == {day: (103.0, 99.0)}

    print("selfcheck ok")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selfcheck", action="store_true")
    a = ap.parse_args(argv)
    if a.selfcheck:
        selfcheck()
        return 0
    res = run()
    print("\n".join(report(res)))
    write_result("sb_session_liq", res)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
