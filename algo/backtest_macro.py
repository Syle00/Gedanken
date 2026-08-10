#!/usr/bin/env python3
"""Sind die ICT-Macro-Fenster (XX:50-XX+1:10) wirklich die Expansions-Fenster?

Anlass: Jannes markiert am 2026-08-10 im MNQ das Macro 09:50-10:10 im Chart
(siehe wiki/concepts/ICT Macros & Leading Candles.md). Die These dahinter ist
falsifizierbar: wenn zu diesen Uhrzeiten ein Algorithmus den Preis ausdehnt,
muessen diese 20-Minuten-Bloecke messbar groessere Ranges und mehr Netto-Weg
liefern als die anderen 20-Minuten-Bloecke derselben Stunde.

Aufbau: jede Stunde zerfaellt in genau drei 20-Minuten-Bloecke
    :50-:10  (Macro)      :10-:30  (Kontrolle)     :30-:50  (Kontrolle)
Damit ist der Vergleich zeitlich fair -- die Kontrollen liegen direkt daneben,
nicht irgendwo im Tag. Ohne das wuerde 09:50-10:10 nur gewinnen, weil kurz nach
dem RTH-Open ohnehin die meiste Bewegung liegt (Tageszeit-Confounder).

Gemessen je Block (nur wenn >=15 der 20 Minuten Daten haben, sonst verworfen):
    range   = high - low in Punkten
    netto   = |close - open| in Punkten
    dir     = netto / range  (1.0 = glatte Expansion, 0.0 = Hin und Her)
    rang    = Platz des Blocks nach range unter allen Bloecken des Tages (1 = groesster)

Aufruf:
    python algo/backtest_macro.py                 # MNQ, alle 1m-Tage in raw/marktdaten
    python algo/backtest_macro.py --symbol ES
    python algo/backtest_macro.py --selfcheck
"""

from __future__ import annotations

import argparse
import statistics
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scipy.stats import mannwhitneyu  # noqa: E402 -- via scikit-learn, s. requirements.txt

from tools.analyze_ohlc import DATA_DIR, NY, Bar, at, fvgs, load  # noqa: E402

from backtest_common import write_result  # noqa: E402

MIN_BARS = 15  # von 20 Minuten -- weniger heisst Datenluecke, nicht ruhiger Markt
MIN_FVG_PTS = 2.0  # kleiner ist auf MNQ-1m Rauschen, kein handelbares PD Array


def blocks(day):
    """Alle 72 20-Minuten-Bloecke eines Tages: (label, start, ende, ist_macro).

    Startpunkt ist 00:10 NY, damit die drei Bloecke jeder Stunde luecken- und
    ueberlappungsfrei aneinanderliegen und :50-:10 als ganzer Block auftaucht.
    """
    out = []
    t = at(day, 0, 10)
    for _ in range(72):
        end = t + timedelta(minutes=20)
        out.append((f"{t:%H:%M}-{end:%H:%M}", t, end, t.minute == 50))
        t = end
    return out


def measure(bars: list[Bar], start, end) -> dict | None:
    win = [b for b in bars if start <= b.t < end]
    if len(win) < MIN_BARS:
        return None
    hi, lo = max(b.h for b in win), min(b.l for b in win)
    rng = hi - lo
    net = abs(win[-1].c - win[0].o)
    # Jannes' These (2026-08-10): das SB-FVG soll optimalerweise IM Macro entstehen.
    # Testbarer Kern davon: haeufen sich 1m-FVGs ueberhaupt in den Macro-Fenstern?
    fvg = [f for f in fvgs(win) if f["size"] >= MIN_FVG_PTS]
    return {"range": rng, "netto": net, "dir": net / rng if rng else 0.0,
            "fvgs": len(fvg), "fvg_pts": sum(f["size"] for f in fvg)}


def collect(symbol: str) -> dict[str, list[dict]]:
    """label -> Liste der Tagesmessungen (inkl. Tagesrang nach range)."""
    per_label: dict[str, list[dict]] = {}
    for path in sorted(DATA_DIR.rglob(f"{symbol} *-*-* 1m.csv")):
        bars = load(path)
        if not bars:
            continue
        day = bars[len(bars) // 2].t.astimezone(NY).date()
        today = []
        for label, start, end, is_macro in blocks(day):
            m = measure(bars, start, end)
            if m:
                today.append({"label": label, "macro": is_macro, "day": day, **m})
        for rank, m in enumerate(sorted(today, key=lambda x: -x["range"]), start=1):
            m["rank"] = rank
            m["n_blocks"] = len(today)
        for m in today:
            per_label.setdefault(m["label"], []).append(m)
    return per_label


def med(xs):
    return statistics.median(xs) if xs else None


def report(symbol: str) -> dict:
    per_label = collect(symbol)
    if not per_label:
        print(f"Keine 1m-Daten fuer {symbol} gefunden.")
        return {}

    rows = [m for ms in per_label.values() for m in ms]
    days = sorted({m["day"] for m in rows})
    macro = [m for m in rows if m["macro"]]
    ctrl = [m for m in rows if not m["macro"]]

    print(f"{symbol}: {len(days)} Handelstage ({days[0]} .. {days[-1]}), "
          f"{len(rows)} auswertbare 20min-Bloecke")
    print(f"  Macro (:50-:10) n={len(macro):4d}  median range {med([m['range'] for m in macro]):7.2f} "
          f"netto {med([m['netto'] for m in macro]):6.2f}  dir {med([m['dir'] for m in macro]):.2f}")
    print(f"  Kontrolle       n={len(ctrl):4d}  median range {med([m['range'] for m in ctrl]):7.2f} "
          f"netto {med([m['netto'] for m in ctrl]):6.2f}  dir {med([m['dir'] for m in ctrl]):.2f}")
    # Mann-Whitney statt t-Test: Block-Ranges sind rechtsschief, nicht normalverteilt.
    # Vorbehalt: Bloecke desselben Tages sind nicht unabhaengig -> p ist optimistisch.
    pvals = {k: mannwhitneyu([m[k] for m in macro], [m[k] for m in ctrl],
                             alternative="greater").pvalue
             for k in ("range", "netto", "dir", "fvgs")}
    print("  Mann-Whitney (Macro > Kontrolle), einseitig:  "
          + "  ".join(f"{k} p={v:.4f}" for k, v in pvals.items()))
    print(f"  FVGs (>= {MIN_FVG_PTS:.0f} Pkt) je Block:  Macro {sum(m['fvgs'] for m in macro)/len(macro):.2f}"
          f"   Kontrolle {sum(m['fvgs'] for m in ctrl)/len(ctrl):.2f}"
          f"   | Bloecke ganz ohne FVG: Macro {100*sum(1 for m in macro if not m['fvgs'])/len(macro):.0f} %"
          f"  Kontrolle {100*sum(1 for m in ctrl if not m['fvgs'])/len(ctrl):.0f} %")

    print("\nJe Block, sortiert nach median range (nur Bloecke mit >=5 Tagen):")
    print(f"  {'Block':<12} {'M':<2} {'n':>3} {'medRange':>9} {'medNetto':>9} {'dir':>5} {'medRang':>8}")
    stats = {}
    for label, ms in per_label.items():
        if len(ms) < 5:
            continue
        stats[label] = {
            "macro": ms[0]["macro"], "n": len(ms),
            "med_range": med([m["range"] for m in ms]),
            "med_netto": med([m["netto"] for m in ms]),
            "med_dir": med([m["dir"] for m in ms]),
            "med_rank": med([m["rank"] for m in ms]),
            "fvgs_je_block": sum(m["fvgs"] for m in ms) / len(ms),
        }
    for label, s in sorted(stats.items(), key=lambda kv: -kv[1]["med_range"]):
        print(f"  {label:<12} {'M' if s['macro'] else ' ':<2} {s['n']:>3} {s['med_range']:>9.2f} "
              f"{s['med_netto']:>9.2f} {s['med_dir']:>5.2f} {s['med_rank']:>8.1f}")

    # Der Fall aus dem Chart: 09:50-10:10 gegen seine direkten Nachbarn.
    print("\nMacro 09:50-10:10 gegen die Nachbarbloecke derselben zwei Stunden:")
    for label in ["09:10-09:30", "09:30-09:50", "09:50-10:10", "10:10-10:30", "10:30-10:50"]:
        s = stats.get(label)
        if s:
            print(f"  {label} {'(Macro)' if s['macro'] else '       '} n={s['n']:>3} "
                  f"medRange {s['med_range']:7.2f}  medNetto {s['med_netto']:6.2f}  "
                  f"dir {s['med_dir']:.2f}  medRang {s['med_rank']:.1f}/{med([m['n_blocks'] for m in rows]):.0f}")

    out = {"symbol": symbol, "days": [str(d) for d in days], "blocks": stats, "p": pvals,
           "macro_vs_ctrl": {
               "macro": {"n": len(macro), "med_range": med([m["range"] for m in macro]),
                         "med_netto": med([m["netto"] for m in macro]),
                         "med_dir": med([m["dir"] for m in macro])},
               "kontrolle": {"n": len(ctrl), "med_range": med([m["range"] for m in ctrl]),
                             "med_netto": med([m["netto"] for m in ctrl]),
                             "med_dir": med([m["dir"] for m in ctrl])}}}
    write_result("macro", out)
    return out


def selfcheck() -> None:
    day = date(2026, 8, 10)
    labels = [b[0] for b in blocks(day)]
    assert len(labels) == 72, labels[:5]
    assert labels[0] == "00:10-00:30" and labels[-1] == "23:50-00:10"
    assert sum(1 for b in blocks(day) if b[3]) == 24, "24 Macro-Fenster pro Tag"
    # Bloecke muessen luecken- und ueberlappungsfrei sein
    bs = blocks(day)
    assert all(a[2] == b[1] for a, b in zip(bs, bs[1:])), "Bloecke haben Luecken"

    start, end = at(day, 9, 50), at(day, 10, 10)
    bars = [Bar(start + timedelta(minutes=i), 100.0 + i, 100.0 + i + 2, 100.0 + i - 1,
                100.0 + i + 1, None) for i in range(20)]
    m = measure(bars, start, end)
    assert m is not None and abs(m["range"] - 22.0) < 1e-9, m   # 121 - 99
    assert abs(m["netto"] - 20.0) < 1e-9, m                     # 120 - 100
    assert measure(bars[:10], start, end) is None, "zu wenige Kerzen muss None geben"
    print("backtest_macro.selfcheck: OK")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--symbol", default="MNQ")
    p.add_argument("--min-fvg", type=float, default=MIN_FVG_PTS,
                   help="Mindestgroesse eines FVG in Punkten (Default 2.0)")
    p.add_argument("--selfcheck", action="store_true")
    a = p.parse_args()
    MIN_FVG_PTS = a.min_fvg
    selfcheck() if a.selfcheck else report(a.symbol)
