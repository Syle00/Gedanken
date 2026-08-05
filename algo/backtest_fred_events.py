#!/usr/bin/env python3
"""Backtest: MNQ-Reaktion auf makro FRED-Daten (siehe algo/fetch_fred.py).

Urspruenglich als "Reaktion an CPI-/FOMC-Tagen" gedacht, aber das laesst sich mit FRED
NICHT sauber bauen und wurde deshalb NICHT gebaut (siehe unten) -- lieber ehrlich melden
als ein Ergebnis auf falschen Daten ausgeben:

- CPIAUCSL: das `date`-Feld von FRED ist der Referenzmonat (die Periode, auf die sich der
  Wert bezieht), nicht das tatsaechliche Veroeffentlichungsdatum (~2-3 Wochen spaeter).
  Ohne echten Release-Kalender waere jeder "Reaktionstag" falsch datiert.
- DFF (Effective Fed Funds Rate) schwankt taeglich in Basispunkten OHNE FOMC-Bezug (reiner
  Marktzins, keine Zielsatz-Aenderung) -- gegen Aenderungstage zu testen waere Rauschen als
  Ereignis verkauft.
- DFEDTARU (oberes Zielband) aendert sich NUR bei echten FOMC-Entscheidungen -- das ist
  sauber, aber im MNQ-Datenfenster (siehe find_1d_days(), 02.01.-04.08.2026) gab es laut
  FRED keine einzige Aenderung (Rate blieb bei 3.75-4.00%), also n=0 Events zum Testen.
  Ein FOMC-Termin-Kalender (auch "Hold"-Meetings sind Events) muesste aus einer verifizierten
  Quelle kommen, nicht aus Trainingsdaten geraten werden -- siehe Bericht.

Stattdessen: was FRED direkt und taeglich/woechentlich liefert, ohne Kalender-Rateraten.
1. VIX-Niveau-Regime: MNQ-Range/Betrag-Rendite an Tagen mit hohem vs. niedrigem VIX-Level
   (Terzile) -- Sanity-Check, ob die Daten ueberhaupt Sinn ergeben (hoher VIX -> groessere Range?).
2. VIX-Tagesaenderung vs. MNQ-Tagesrendite: Korrelation (Erwartung: negativ, VIX-Spike = Down-Tag).
3. DGS10-Tagesaenderung (10J-Rendite) vs. MNQ-Tagesrendite: Korrelation.
4. WALCL (Fed-Bilanzsumme, woechentlich) wachsend vs. schrumpfend -> MNQ-Wochenrendite.

Aufruf:
    python algo/backtest_fred_events.py
"""
from __future__ import annotations

import csv
import statistics
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from backtest_seasonal import load_rows  # noqa: E402
from backtest_nwog import group_weeks  # noqa: E402

FRED_DIR = Path(__file__).resolve().parent.parent / "raw" / "marktdaten" / "fred"


def load_fred(series_id: str) -> dict[date, float]:
    out = {}
    with (FRED_DIR / f"{series_id}.csv").open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["value"]:
                out[date.fromisoformat(row["date"])] = float(row["value"])
    return out


def nearest_on_or_before(series: dict[date, float], d: date, lookback: int = 5) -> float | None:
    for i in range(lookback + 1):
        v = series.get(d - timedelta(days=i))
        if v is not None:
            return v
    return None


def main() -> None:
    rows = load_rows()
    print(f"{len(rows)} MNQ-Handelstage ({rows[0]['day']} bis {rows[-1]['day']}).\n")

    print("Hinweis: CPI-/FOMC-Reaktionstest bewusst NICHT gebaut -- FRED liefert kein "
          "Release-Datum fuer CPI und im Datenfenster gab es keine FOMC-Zielsatzaenderung "
          "(n=0). Details im Modul-Docstring. Stattdessen VIX/DGS10/WALCL-Zusammenhaenge:\n")

    vix = load_fred("VIXCLS")
    dgs10 = load_fred("DGS10")
    walcl = load_fred("WALCL")

    # 1. VIX-Niveau-Regime
    with_vix = [(r, nearest_on_or_before(vix, r["day"])) for r in rows]
    with_vix = [(r, v) for r, v in with_vix if v is not None]
    with_vix.sort(key=lambda t: t[1])
    n = len(with_vix)
    tercile = n // 3
    low, mid, high = with_vix[:tercile], with_vix[tercile:-tercile], with_vix[-tercile:]
    print(f"1. VIX-Niveau-Regime (n={n}, Terzile):")
    for name, bucket in [("niedrig", low), ("mittel", mid), ("hoch", high)]:
        ranges = [r["range"] for r, _ in bucket]
        abs_rets = [abs(r["ret_pct"]) for r, _ in bucket]
        vix_range = f"{bucket[0][1]:.1f}-{bucket[-1][1]:.1f}"
        print(f"   VIX {name:>7} ({vix_range:>11}): n={len(bucket):>2}  "
              f"Median-Range={statistics.median(ranges):>7.1f}  "
              f"Avg|Rendite|={statistics.mean(abs_rets):.2f}%")

    # 2. VIX-Aenderung vs. MNQ-Rendite
    vix_delta, mnq_ret = [], []
    prev_vix = None
    for r in rows:
        v = nearest_on_or_before(vix, r["day"])
        if v is not None and prev_vix is not None:
            vix_delta.append(v - prev_vix)
            mnq_ret.append(r["ret_pct"])
        if v is not None:
            prev_vix = v
    corr_vix = statistics.correlation(vix_delta, mnq_ret) if len(vix_delta) >= 2 else None
    print(f"\n2. VIX-Tagesaenderung vs. MNQ-Tagesrendite: n={len(vix_delta)}  "
          f"Korrelation={corr_vix:+.3f}" if corr_vix is not None else "\n2. zu wenig Daten")

    # 3. DGS10-Aenderung vs. MNQ-Rendite
    dgs_delta, mnq_ret2 = [], []
    prev_dgs = None
    for r in rows:
        v = nearest_on_or_before(dgs10, r["day"])
        if v is not None and prev_dgs is not None:
            dgs_delta.append(v - prev_dgs)
            mnq_ret2.append(r["ret_pct"])
        if v is not None:
            prev_dgs = v
    corr_dgs = statistics.correlation(dgs_delta, mnq_ret2) if len(dgs_delta) >= 2 else None
    print(f"3. DGS10-Tagesaenderung vs. MNQ-Tagesrendite: n={len(dgs_delta)}  "
          f"Korrelation={corr_dgs:+.3f}" if corr_dgs is not None else "3. zu wenig Daten")

    # 4. WALCL (woechentlich) wachsend/schrumpfend vs. MNQ-Wochenrendite
    weeks = [w for w in group_weeks(rows) if len(w) >= 2]
    grow, shrink = [], []
    prev_walcl = None
    for w in sorted(weeks, key=lambda w: w[0]["day"]):
        v = nearest_on_or_before(walcl, w[0]["day"], lookback=10)
        if v is None:
            continue
        week_ret = 100 * (w[-1]["close"] - w[0]["open"]) / w[0]["open"]
        if prev_walcl is not None:
            (grow if v > prev_walcl else shrink).append(week_ret)
        prev_walcl = v
    print(f"\n4. WALCL-Trend vs. MNQ-Wochenrendite:")
    if grow:
        print(f"   Bilanz waechst  (n={len(grow):>2}): Avg-Wochenrendite {statistics.mean(grow):+.2f}%")
    if shrink:
        print(f"   Bilanz schrumpft(n={len(shrink):>2}): Avg-Wochenrendite {statistics.mean(shrink):+.2f}%")
    if not grow or not shrink:
        print("   zu wenig Wochen fuer beide Gruppen im aktuellen Fenster")


if __name__ == "__main__":
    main()
