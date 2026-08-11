#!/usr/bin/env python3
"""Backtest: sind NFP-Freitage (Non-Farm Payroll) volatiler/"choppier" als normale Handelstage?
Primaerquelle der These: wiki/sources/youtube/2023-12-06 - Why Do I Avoid NFP Weeks NQ 3 Trades
2 Losses (Source).md -- ICT vermeidet NFP-Wochen wegen erhoehter Verlustrate (2 von 3 Trades im
gezeigten Beispiel verloren), siehe algo/PLAN.md-Log 2026-08-11.

Kein Trade-P&L verfuegbar fuer diese spezifischen Tage (das Video zeigt reale Trades, aber
keine reproduzierbare Regel) -- stattdessen zwei Proxy-Metriken fuer "schwerer zu halten":
1. Range: NFP-Freitag-Range vs. normale Freitage vs. alle Handelstage.
2. Whipsaw-Ratio: Range / |Netto-Bewegung (Close-Open)| -- hoher Wert = viel Gegenbewegung
   pro Punkt Nettofortschritt, was Stop-Outs bei Directional-Trades wahrscheinlicher macht.

NFP-Termin-Naeherung: erster Freitag des Monats (US-Standardtermin). Bekannte Ausnahme: bei
Regierungs-Shutdowns/Feiertagsverschiebungen kann der Termin abweichen (in dieser Datenreihe
nicht geprueft, da keine Termin-Referenzliste vorliegt) -- explizit als Naeherung markiert,
kein exakter Kalenderabgleich mit BLS-Terminen.

Aufruf:
    python algo/backtest_nfp_week.py
"""
from __future__ import annotations

import statistics
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from backtest_common import load_rows, write_result  # noqa: E402


def first_friday(year: int, month: int) -> date:
    d = date(year, month, 1)
    offset = (4 - d.weekday()) % 7  # Friday = weekday 4
    return date(year, month, 1 + offset)


def whipsaw_ratio(r: dict) -> float | None:
    net = abs(r["close"] - r["open"])
    if net <= 0:
        return None
    return r["range"] / net


def stats(rs: list[dict]) -> dict:
    ranges = [r["range"] for r in rs]
    whips = [w for r in rs if (w := whipsaw_ratio(r)) is not None]
    return {
        "n": len(rs),
        "avg_range": round(statistics.mean(ranges), 2) if ranges else None,
        "median_range": round(statistics.median(ranges), 2) if ranges else None,
        "avg_whipsaw_ratio": round(statistics.mean(whips), 2) if whips else None,
        "median_whipsaw_ratio": round(statistics.median(whips), 2) if whips else None,
    }


def run() -> dict:
    rows = load_rows()
    months = sorted({(r["day"].year, r["day"].month) for r in rows})
    nfp_fridays = {first_friday(y, m) for y, m in months}

    nfp_rows = [r for r in rows if r["day"] in nfp_fridays]
    other_fridays = [r for r in rows if r["day"].weekday() == 4 and r["day"] not in nfp_fridays]
    all_days = rows

    return {
        "n_nfp_fridays_in_data": len(nfp_rows),
        "nfp_fridays": stats(nfp_rows),
        "other_fridays": stats(other_fridays),
        "all_days": stats(all_days),
    }


def main() -> None:
    result = run()
    print(f"{result['n_nfp_fridays_in_data']} NFP-Freitage in den Daten gefunden "
          f"(Naeherung: erster Freitag des Monats).\n")

    for label, key in [("NFP-Freitage", "nfp_fridays"), ("Andere Freitage", "other_fridays"),
                        ("Alle Handelstage", "all_days")]:
        s = result[key]
        if s["n"] == 0:
            print(f"{label}: keine Daten")
            continue
        print(f"{label} (n={s['n']}): Ø-Range {s['avg_range']}, Median-Range {s['median_range']}, "
              f"Ø-Whipsaw-Ratio {s['avg_whipsaw_ratio']}, Median-Whipsaw-Ratio "
              f"{s['median_whipsaw_ratio']}")

    write_result("backtest_nfp_week", result)


def demo() -> None:
    assert first_friday(2024, 12) == date(2024, 12, 6)
    assert first_friday(2024, 11) == date(2024, 11, 1)
    r = {"range": 10.0, "open": 100.0, "close": 105.0}
    assert whipsaw_ratio(r) == 2.0


if __name__ == "__main__":
    demo()
    main()
