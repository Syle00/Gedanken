#!/usr/bin/env python3
"""Erkennt und rankt die aktuell offene Liquiditaet ueber 1m/5m/15m/Daily -- automatisiert
das manuelle Vorgehen aus der Chat-Session 2026-08-14 ("gebe mir die Liq Level..."), reuse-first
auf rules.py-Bausteinen (`session_extrema`, `ipda_windows`, `rel_pair`, `level_untouched`,
`daily_hilo_from_bars`, `prev_day_level`, `prev_week_level`) und den bestehenden Detektoren aus
tools/analyze_ohlc.py (`untouched_levels`, `swings`).

Ranking bleibt bewusst QUALITATIV (Hoch/Mittel/Niedrig + Begruendung), kein numerischer Score --
Nutzerentscheidung 2026-08-14 (Brainstorming-Session), weil Gewichte sonst geschaetzt statt
gemessen waeren. Die Klassifizierung ist damit ein Startpunkt, kein fertiges Modell: neue
Kriterien kommen als weitere Merkmale in `_classify()` dazu, ohne die Erkennung selbst
anzufassen ("wird noch erweitert", Nutzerformulierung).

Intraday-Timeframes (1m/5m/15m) nutzen historische `raw/marktdaten/`-Dateien + frische
Live-Daten ueber `live_status.fetch_today()` (kein doppelter Fetch-Code). Der Daily/IPDA-Layer
wird bewusst aus 5m-Tagesdateien aggregiert, NICHT aus den 1d-Dateien -- siehe
`rules.daily_hilo_from_bars()`-Docstring: mehrere 1d-Dateien liefen der eigenen Intraday-Historie
davon (Fund 2026-08-14, algo/PLAN.md).

Aufruf:
    python algo/liquidity_report.py MNQ
    python algo/liquidity_report.py MNQ --selfcheck
"""
from __future__ import annotations

import argparse
import sys
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "algo"))

from analyze_ohlc import Bar, at, load, untouched_levels  # noqa: E402
from backtest_1p_fvg_woche import find_days  # noqa: E402
from rules import (session_extrema, ipda_windows, rel_pair, level_untouched,  # noqa: E402
                    daily_hilo_from_bars, prev_day_level, prev_week_level)
from live_status import fetch_today, DISPLAY_SYMBOL as LIVE_SYMBOL  # noqa: E402
from fetch_yfinance import trading_day  # noqa: E402

import pandas as pd

NY = ZoneInfo("America/New_York")
INTRADAY_TFS = ["1m", "5m", "15m"]
SWING_N = 2
LOOKBACK_DAYS = {"1m": 5, "5m": 20, "15m": 40}  # je kuerzer der TF, desto weniger Historie
                                                  # sinnvoll (Rauschen/Datenmenge) -- Startwerte,
                                                  # per "wird noch erweitert" anpassbar.
NEAR_PCT = 0.003  # Toleranz fuer "nahezu gleich" bei REH/REL-Paarbildung, grob kalibriert an
                  # den Beispielen der Chat-Session (0.2-0.3% Kursabstand) -- kein gemessener Wert.
MAX_DISTANCE_PCT = 0.05  # Swing-/REH-REL-Level weiter als 5% vom Preis entfernt sind fuer den
                          # Report irrelevant (bei starkem Trend bleiben sonst Dutzende alter,
                          # nie wieder besuchter Level "unberuehrt" und fluten die Ausgabe).
                          # PDH/PDL/PWH/PWL/Session-Extrema sind davon ausgenommen -- feste,
                          # kleine Menge, immer relevant unabhaengig von der Distanz.
MAX_ROWS = 20  # Obergrenze fuer die gedruckte Tabelle (nach Label/Distanz sortiert)


def historical_daybars(symbol: str, upto: date, n: int = 90) -> list[Bar]:
    """Ein Bar je Handelstag (O erste Kerze, H/L Session-Extrem, C letzte Kerze) aus 5m-Dateien
    aggregiert, nur Handelstage VOR `upto` (der laufende Tag ist unvollstaendig)."""
    d5 = find_days(symbol, "5m")
    days = sorted(d for d in d5 if d < upto)[-n:]
    out = []
    for d in days:
        bars = load(d5[d])
        if not bars:
            continue
        out.append(Bar(t=bars[-1].t, o=bars[0].o, h=max(b.h for b in bars),
                        l=min(b.l for b in bars), c=bars[-1].c))
    return out


def combined_bars(symbol: str, tf: str, today: date, live_bars: list[Bar]) -> list[Bar]:
    """Historische `tf`-Bars (raw/marktdaten, LOOKBACK_DAYS[tf] Handelstage vor `today`) plus
    frische `today`-Bars aus `live_bars` (ersetzt eine evtl. veraltete lokale Datei fuer heute)."""
    days_map = find_days(symbol, tf)
    days = sorted(d for d in days_map if d < today)[-LOOKBACK_DAYS[tf]:]
    bars: list[Bar] = []
    for d in days:
        bars.extend(load(days_map[d]))
    bars.extend(live_bars)
    bars.sort(key=lambda b: b.t)
    return bars


def resolve_rel_clusters(levels: list[dict], side: str) -> list[dict]:
    """Levels derselben Seite, nach Zeit sortiert. Bildet Paare benachbarter, innerhalb
    NEAR_PCT liegender Level und loest sie ueber rel_pair() auf (siehe wiki/concepts/Open
    Float & Liquidity Pools.md, REH/REL); unpaarige Level bleiben unveraendert. Rein
    heuristisch -- die Toleranz ist ein Schaetzwert, kein gemessener."""
    levels = sorted(levels, key=lambda x: x["t"])
    out, skip = [], set()
    for i, lv in enumerate(levels):
        if i in skip:
            continue
        paired = False
        for j in range(i + 1, len(levels)):
            other = levels[j]
            if lv["level"] == 0:
                continue
            if abs(other["level"] - lv["level"]) / abs(lv["level"]) <= NEAR_PCT:
                resolved = rel_pair(lv, other, side)
                if resolved is not None:
                    out.append({**resolved, "rel_pair": True})
                skip.add(j)
                paired = True
                break
        if not paired:
            out.append({**lv, "rel_pair": False})
    return out


def timeframe_pools(bars: list[Bar], tf: str) -> list[dict]:
    """Unberuehrte Swing-Level je Timeframe (untouched_levels), REH/REL-aufgeloest, mit
    Metadaten fuer die Klassifizierung."""
    ut = untouched_levels(bars, SWING_N)
    out = []
    for side in ("buyside", "sellside"):
        side_levels = [u for u in ut if u["side"] == side]
        for lv in resolve_rel_clusters(side_levels, side):
            out.append({"level": lv["level"], "side": side, "t": lv["t"], "tf": tf,
                        "kind": "REH/REL" if lv["rel_pair"] else "Swing", "rel_pair": lv["rel_pair"]})
    return out


def _classify(pool: dict, last_price: float, confluence: int) -> tuple[str, str]:
    """Qualitative Einstufung (Hoch/Mittel/Niedrig) + Begruendung -- Nutzerentscheidung
    2026-08-14: kein numerischer Score nach aussen, nur nachvollziehbare Merkmale. Intern ein
    einfacher Zaehler, um die Label-Grenzen konsistent zu ziehen; nicht Teil der Ausgabe."""
    dist_pct = abs(pool["level"] - last_price) / last_price
    gruende, score = [], 0
    if dist_pct < 0.01:
        score += 2; gruende.append("sehr nah am aktuellen Preis")
    elif dist_pct < 0.03:
        score += 1; gruende.append("nah am aktuellen Preis")
    else:
        gruende.append("weit vom aktuellen Preis entfernt")
    if confluence > 0:
        score += 2
        gruende.append(f"Konfluenz mit {confluence} weiterem Level auf anderem Timeframe")
    if pool.get("rel_pair"):
        score += 1; gruende.append("REH/REL-bestaetigt (noch unberuehrt)")
    if pool.get("session_level"):
        score += 1; gruende.append(pool["session_level"])
    if pool.get("ipda_active"):
        score += 1; gruende.append("im aktiven IPDA-Fenster")
    label = "Hoch" if score >= 4 else "Mittel" if score >= 2 else "Niedrig"
    return label, ", ".join(gruende)


def build_report(symbol: str, today: date, live: dict[str, list[Bar]]) -> list[dict]:
    live_by_tf = {tf: live[tf] for tf in INTRADAY_TFS}
    last_price = None
    for tf in ("1m", "5m", "15m"):
        if live_by_tf[tf]:
            last_price = live_by_tf[tf][-1].c
            break
    if last_price is None:
        return []

    pools: list[dict] = []
    for tf in INTRADAY_TFS:
        bars = combined_bars(symbol, tf, today, live_by_tf[tf])
        pools.extend(p for p in timeframe_pools(bars, tf)
                     if abs(p["level"] - last_price) / last_price <= MAX_DISTANCE_PCT)
        if tf == "5m":  # Session-Extrema + Midnight Open einmal auf 5m-Basis
            se = session_extrema(bars, today)
            mo = se.pop("Midnight Open", None)
            for name, ext in se.items():
                pools.append({"level": ext["hi"], "side": "buyside", "t": ext["hi_t"], "tf": tf,
                              "kind": "Session-Hoch", "session_level": f"Session-Hoch ({name})"})
                pools.append({"level": ext["lo"], "side": "sellside", "t": ext["lo_t"], "tf": tf,
                              "kind": "Session-Tief", "session_level": f"Session-Tief ({name})"})
            if mo is not None:
                pools.append({"level": mo, "side": None, "t": None, "tf": "Referenz",
                              "kind": "Midnight Open", "session_level": "Midnight Open (Referenz, kein Pool)"})

    daybars = historical_daybars(symbol, today)
    if daybars:
        hilo = daily_hilo_from_bars({b.t.date(): [b] for b in daybars})
        pd_ = prev_day_level(hilo, today)
        pw_ = prev_week_level(hilo, today)
        if pd_:
            pools.append({"level": pd_[0], "side": "buyside", "t": None, "tf": "Daily",
                          "kind": "PDH", "session_level": "Previous Day High"})
            pools.append({"level": pd_[1], "side": "sellside", "t": None, "tf": "Daily",
                          "kind": "PDL", "session_level": "Previous Day Low"})
        if pw_:
            pools.append({"level": pw_[0], "side": "buyside", "t": None, "tf": "Daily",
                          "kind": "PWH", "session_level": "Previous Week High"})
            pools.append({"level": pw_[1], "side": "sellside", "t": None, "tf": "Daily",
                          "kind": "PWL", "session_level": "Previous Week Low"})

        ipda = ipda_windows(daybars, last_price)
        active_n = ipda["active"]
        active_hi, active_lo = ipda[active_n]["hi"], ipda[active_n]["lo"]
        for pool in pools:
            if pool["tf"] == "Daily" and pool["side"] == "buyside" and pool["level"] == active_hi:
                pool["ipda_active"] = True
            if pool["tf"] == "Daily" and pool["side"] == "sellside" and pool["level"] == active_lo:
                pool["ipda_active"] = True

    # nur noch offene (unberuehrte) Level: 5m-Referenzhistorie seit Handelsbeginn heute
    check_hist = live_by_tf.get("5m") or live_by_tf.get("1m") or []
    pools = [p for p in pools if p["side"] is None
             or level_untouched(check_hist, p["level"], p["side"])] if check_hist else pools

    for pool in pools:
        confluence = sum(1 for other in pools if other is not pool and other["side"] == pool["side"]
                         and pool["level"] and abs(other["level"] - pool["level"]) / pool["level"] <= NEAR_PCT)
        label, reason = _classify(pool, last_price, confluence) if pool["level"] else ("-", "Referenz")
        pool["label"], pool["reason"] = label, reason
        pool["distance"] = abs(pool["level"] - last_price) if pool["level"] else None

    order = {"Hoch": 0, "Mittel": 1, "Niedrig": 2, "-": 3}
    pools.sort(key=lambda p: (order[p["label"]], p["distance"] if p["distance"] is not None else 1e18))
    return pools


def report(pools: list[dict], symbol: str, last_price: float, max_rows: int = MAX_ROWS) -> list[str]:
    L = [f"=== Liquiditaet {symbol}, Preis {last_price:g} ===", "",
         f"  {'Label':<8}{'Level':>12}{'Seite':>10}{'TF':>6}{'Typ':>14}  Begruendung"]
    for p in pools[:max_rows]:
        seite = p["side"] or "-"
        L.append(f"  {p['label']:<8}{p['level']:>12g}{seite:>10}{p['tf']:>6}{p['kind']:>14}  {p['reason']}")
    if len(pools) > max_rows:
        L.append(f"\n  ... {len(pools) - max_rows} weitere Level unterhalb der Top {max_rows} "
                  "(nach Label/Distanz sortiert), nicht angezeigt.")
    return L


def selfcheck() -> None:
    day = date(2026, 1, 6)  # Dienstag

    def bar(hh, mm, o, h, l, c):
        return Bar(at(day, hh, mm), o, h, l, c)

    # resolve_rel_clusters: REH-Paar (links hoeher, < NEAR_PCT auseinander -> gueltig) +
    # Einzel-Level (95.0 liegt zu weit weg fuer eine Paarbildung)
    levels = [{"level": 110.0, "t": bar(9, 0, 0, 0, 0, 0).t, "side": "buyside"},
              {"level": 109.8, "t": bar(9, 5, 0, 0, 0, 0).t, "side": "buyside"},
              {"level": 95.0, "t": bar(9, 10, 0, 0, 0, 0).t, "side": "buyside"}]
    res = resolve_rel_clusters(levels, "buyside")
    reh = [r for r in res if r.get("rel_pair")]
    assert len(reh) == 1 and reh[0]["level"] == 110.0, res
    assert any(not r["rel_pair"] and r["level"] == 95.0 for r in res)

    # timeframe_pools: unberuehrter Spike liefert einen buyside-Pool
    bars = [bar(9, 15, 95, 96, 94, 95.5), bar(9, 20, 95.5, 96, 95, 95.5),
            bar(9, 25, 95.5, 110, 95, 96), bar(9, 30, 96, 97, 95.5, 96.5),
            bar(9, 35, 96.5, 97, 96, 96.5), bar(9, 40, 96.5, 97.5, 96, 97)]
    pools = timeframe_pools(bars, "5m")
    assert any(p["level"] == 110.0 and p["side"] == "buyside" for p in pools), pools

    # _classify: nah + Konfluenz -> Hoch; weit + keine Konfluenz -> Niedrig
    nah = {"level": 100.3, "side": "buyside"}
    label, reason = _classify(nah, last_price=100.0, confluence=1)
    assert label == "Hoch", (label, reason)
    weit = {"level": 150.0, "side": "buyside"}
    label2, _ = _classify(weit, last_price=100.0, confluence=0)
    assert label2 == "Niedrig", label2

    print("selfcheck ok")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("symbol", nargs="?", default="MNQ")
    ap.add_argument("--selfcheck", action="store_true")
    a = ap.parse_args(argv)
    if a.selfcheck:
        selfcheck()
        return 0

    if a.symbol != LIVE_SYMBOL:
        # combined_bars() mischt historische <symbol>-Dateien mit den Live-Kerzen aus
        # live_status.fetch_today(). Die kommen seit 2026-08-16 von NQ -- ein anderes Symbol
        # hier wuerde Micro und Mini in einer Kerzenreihe vermengen (im Vault verboten).
        print(f"Live-Daten kommen von {LIVE_SYMBOL}, angefragt ist {a.symbol} -- Micro und "
              f"Mini nicht vermengen. Aufruf mit {LIVE_SYMBOL} wiederholen.")
        return 1
    now = datetime.now(NY)
    today = trading_day(pd.Timestamp(now))
    live = fetch_today(today)
    if not live["5m"]:
        print("Keine Live-Daten (Markt geschlossen oder IBKR-Gateway nicht erreichbar).")
        return 1

    live5 = live["5m"] or live["1m"]
    if not live5:
        print("Kein aktueller Preis ermittelbar.")
        return 1
    last_price = live5[-1].c

    pools = build_report(a.symbol, today, live)
    print("\n".join(report(pools, a.symbol, last_price)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
