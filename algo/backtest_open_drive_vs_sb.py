#!/usr/bin/env python3
"""Jannes' These (2026-08-11, nach dem NY-SB-Tapereading): "gab es gute Bewegung aber
konnte erst ab 16 Uhr [= 10:00 NY] aktiv was machen" -- also: wenn der RTH-Open
(09:30-09:50 NY) schon stark expandiert, bleibt fuer die Silver-Bullet-Stunde
(10:00-11:00) nichts mehr uebrig.

Testbarer Kern, zwei getrennte Fragen:
  (1) Ist die SB-Stunde nach einem starken Open KLEINER (range)?
  (2) Ist sie RICHTUNGSLOSER (dir = |netto| / range)? Das ist die Frage, die seinem
      tatsaechlichen Leiden entspricht -- am 11.08. war die Range nicht klein, aber der
      Preis lief 80 Minuten hin und her.

Split: oberes Drittel der Open-Range gegen die unteren zwei Drittel, Mann-Whitney-U.
Kein Trade-Simulator, keine P&L -- das hier beantwortet eine Filterfrage, nicht die
Frage nach einer Strategie.

Aufruf:
    python algo/backtest_open_drive_vs_sb.py            # MNQ
    python algo/backtest_open_drive_vs_sb.py --selfcheck
"""
from __future__ import annotations

import argparse
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scipy.stats import mannwhitneyu  # noqa: E402 -- via scikit-learn, s. requirements.txt

from tools.analyze_ohlc import DATA_DIR, Bar, at, load  # noqa: E402

from backtest_common import write_result  # noqa: E402
from backtest_macro import session_day_from_path  # noqa: E402

OPEN_WIN = (9, 30, 9, 50)   # RTH-Open-Drive
SB_WIN = (10, 0, 11, 0)     # Silver Bullet AM
MIN_BARS_OPEN = 15          # von 20 -- weniger heisst Datenluecke, nicht ruhiger Markt
MIN_BARS_SB = 45            # von 60


def window(bars: list[Bar], day, h1, m1, h2, m2) -> list[Bar]:
    start, end = at(day, h1, m1), at(day, h2, m2)
    return [b for b in bars if start <= b.t < end]


def stats(win: list[Bar]) -> dict:
    hi, lo = max(b.h for b in win), min(b.l for b in win)
    rng = hi - lo
    net = abs(win[-1].c - win[0].o)
    return {"range": rng, "netto": net, "dir": net / rng if rng else 0.0}


def collect(symbol: str) -> list[dict]:
    rows = []
    for path in sorted(DATA_DIR.rglob(f"{symbol} *-*-* 1m.csv")):
        bars = load(path)
        if not bars:
            continue
        day = session_day_from_path(path)
        op = window(bars, day, *OPEN_WIN)
        sb = window(bars, day, *SB_WIN)
        if len(op) < MIN_BARS_OPEN or len(sb) < MIN_BARS_SB:
            continue
        o, s = stats(op), stats(sb)
        rows.append({"day": day, "open_range": o["range"], "open_dir": o["dir"],
                     "sb_range": s["range"], "sb_dir": s["dir"], "sb_netto": s["netto"]})
    return sorted(rows, key=lambda r: r["day"])


def med(xs):
    return round(statistics.median(xs), 2) if xs else None


def split_test(rows: list[dict], key: str) -> dict:
    """Oberes Drittel der Open-Range gegen den Rest, verglichen ueber `key`."""
    ranked = sorted(rows, key=lambda r: r["open_range"])
    cut = ranked[int(len(ranked) * 2 / 3)]["open_range"]
    hi = [r[key] for r in rows if r["open_range"] >= cut]
    lo = [r[key] for r in rows if r["open_range"] < cut]
    p = mannwhitneyu(hi, lo).pvalue if len(hi) >= 3 and len(lo) >= 3 else None
    return {"schwelle_open_range": round(cut, 2),
            "n_starker_open": len(hi), "n_rest": len(lo),
            "median_starker_open": med(hi), "median_rest": med(lo),
            "p": round(p, 4) if p is not None else None}


def report(symbol: str) -> dict:
    rows = collect(symbol)
    if len(rows) < 10:
        print(f"Zu wenige 1m-Tage mit vollstaendigem Open+SB-Fenster fuer {symbol}: {len(rows)}")
        return {"symbol": symbol, "n": len(rows)}

    out = {"symbol": symbol, "n_tage": len(rows),
           "zeitraum": [str(rows[0]["day"]), str(rows[-1]["day"])],
           "median_open_range": med([r["open_range"] for r in rows]),
           "median_sb_range": med([r["sb_range"] for r in rows]),
           "median_sb_dir": med([r["sb_dir"] for r in rows]),
           "sb_range_nach_starkem_open": split_test(rows, "sb_range"),
           "sb_dir_nach_starkem_open": split_test(rows, "sb_dir")}

    print(f"{symbol}: {out['n_tage']} Tage, {out['zeitraum'][0]} .. {out['zeitraum'][1]}")
    print(f"  Median Open-Range (09:30-09:50): {out['median_open_range']} Pkt")
    print(f"  Median SB-Range   (10:00-11:00): {out['median_sb_range']} Pkt")
    print(f"  Median SB-Direktionalitaet     : {out['median_sb_dir']}")
    for name, key in [("SB-Range", "sb_range_nach_starkem_open"),
                      ("SB-Direktionalitaet", "sb_dir_nach_starkem_open")]:
        t = out[key]
        print(f"\n  {name} -- starker Open (>= {t['schwelle_open_range']} Pkt) vs. Rest:")
        print(f"    starker Open (n={t['n_starker_open']}): {t['median_starker_open']}")
        print(f"    Rest         (n={t['n_rest']}): {t['median_rest']}")
        print(f"    Mann-Whitney p = {t['p']}")
    return out


def selfcheck() -> None:
    from datetime import date

    day = date(2026, 8, 11)
    # Kunst-Tag: Open 09:30-09:50 laeuft 100 Punkte glatt hoch, SB-Stunde pendelt in 20.
    bars = []
    for i in range(20):  # 09:30-09:50
        p = 100.0 + i * 5
        bars.append(Bar(at(day, 9, 30 + i), p, p + 5, p, p + 5, 0))
    for i in range(60):  # 10:00-11:00, Zickzack ohne Netto
        p = 200.0 + (10 if i % 2 else 0)
        bars.append(Bar(at(day, 10, 0) + (at(day, 10, 1) - at(day, 10, 0)) * i,
                        p, p + 10, p - 10, p, 0))
    op, sb = window(bars, day, *OPEN_WIN), window(bars, day, *SB_WIN)
    assert len(op) == 20 and len(sb) == 60, (len(op), len(sb))
    assert stats(op)["dir"] > 0.9, stats(op)          # glatter Drive
    assert stats(sb)["dir"] < 0.3, stats(sb)          # Chop
    # Split muss das obere Drittel wirklich abtrennen, nicht alles in eine Gruppe werfen
    fake = [{"open_range": float(i), "sb_range": float(i % 3)} for i in range(30)]
    t = split_test(fake, "sb_range")
    assert t["n_starker_open"] == 10 and t["n_rest"] == 20, t
    print("selfcheck ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", default="MNQ")
    ap.add_argument("--selfcheck", action="store_true")
    a = ap.parse_args()
    if a.selfcheck:
        selfcheck()
    else:
        write_result("backtest_open_drive_vs_sb", report(a.symbol))
