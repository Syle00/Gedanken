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
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scipy.stats import mannwhitneyu  # noqa: E402 -- via scikit-learn, s. requirements.txt

from tools.analyze_ohlc import DATA_DIR, Bar, at, fvgs, load  # noqa: E402

from backtest_common import write_result  # noqa: E402

MIN_BARS = 15  # von 20 Minuten -- weniger heisst Datenluecke, nicht ruhiger Markt
# Mindestgroesse eines FVG -- RELATIV zur lokalen Kerzenrange, nicht in Punkten. Eine
# absolute Schwelle waere hier ein Messfehler: eine 1m-Kerze ist um 9:35 fast dreimal so
# gross wie um 4:00 (gemessen ueber 27 Tage, siehe wiki/synthesis/FVG-Stärke,
# Session-Volatilität & Confluence (laufend).md). Mit "2 Punkte" haette derselbe Filter in
# den NY-Bloecken fast alles durchgelassen und in Asia/London aussortiert -- und genau
# solche Bloecke werden hier gegeneinander getestet. Median ueber alle FVG: 0,45.
MIN_FVG_REL = 0.45


def blocks(session_day):
    """Alle 69 20-Minuten-Bloecke eines Handelstags: (label, start, ende, ist_macro).

    Der MNQ-Handelstag laeuft von 18:00 des Vorabends bis 17:00 des `session_day`
    (dazwischen die Globex-Pause 17:00-18:00). Er ist damit 23 Stunden lang, also
    69 Bloecke zu 20 Minuten, davon 23 Macro-Fenster (:50-:10).

    Startpunkt ist 18:10 des Vorabends, damit die drei Bloecke jeder Stunde luecken-
    und ueberlappungsfrei aneinanderliegen und :50-:10 als ganzer Block auftaucht.
    Frueher startete diese Funktion bei 00:10 des Kalendertags und verlor dadurch die
    Bloecke 18:00-24:00 -- 6 der 23 Macro-Fenster (siehe
    docs/superpowers/specs/2026-08-10-macro-datenbank-design.md, 9.2).
    """
    out = []
    t = at(session_day - timedelta(days=1), 18, 10)
    for _ in range(69):
        end = t + timedelta(minutes=20)
        out.append((f"{t:%H:%M}-{end:%H:%M}", t, end, t.minute == 50))
        t = end
    return out


def session_day_from_path(path) -> date:
    """Handelstag aus dem Dateinamen: 'MNQ 2026-07-09 1m.csv' -> date(2026, 7, 9).

    Bewusst aus dem Namen statt aus den Bars: die Datei enthaelt Kerzen von zwei
    Kalendertagen (18:00 Vorabend .. 17:00), eine Heuristik ueber die Bars waere
    bei Fragmenttagen mehrdeutig.
    """
    return datetime.strptime(path.name.split(" ")[1], "%Y-%m-%d").date()


def measure(bars: list[Bar], start, end, tages_fvgs=None) -> dict | None:
    win = [b for b in bars if start <= b.t < end]
    if len(win) < MIN_BARS:
        return None
    hi, lo = max(b.h for b in win), min(b.l for b in win)
    rng = hi - lo
    net = abs(win[-1].c - win[0].o)
    # Jannes' These (2026-08-10): das SB-FVG soll optimalerweise IM Macro entstehen.
    # Testbarer Kern davon: haeufen sich 1m-FVGs ueberhaupt in den Macro-Fenstern?
    #
    # Die FVGs kommen aus dem GANZEN Tag und werden hier nur zugeschnitten -- nicht aus
    # dem 20-Minuten-Fenster. Sonst haetten die ersten Kerzen jedes Blocks zu wenig
    # Vorlauf fuer size_rel (None) und die halbe Messung fiele weg.
    if tages_fvgs is None:
        tages_fvgs = fvgs(bars)
    fvg = [f for f in tages_fvgs
           if start <= f["t_start"] and f["t_end"] < end
           and f["size_rel"] is not None and f["size_rel"] >= MIN_FVG_REL]
    return {"range": rng, "netto": net, "dir": net / rng if rng else 0.0,
            "fvgs": len(fvg), "fvg_pts": sum(f["size"] for f in fvg)}


def collect(symbol: str) -> dict[str, list[dict]]:
    """label -> Liste der Tagesmessungen (inkl. Tagesrang nach range)."""
    per_label: dict[str, list[dict]] = {}
    for path in sorted(DATA_DIR.rglob(f"{symbol} *-*-* 1m.csv")):
        bars = load(path)
        if not bars:
            continue
        day = session_day_from_path(path)
        tages_fvgs = fvgs(bars)     # einmal pro Tag statt 69x je Block
        today = []
        for label, start, end, is_macro in blocks(day):
            m = measure(bars, start, end, tages_fvgs)
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
    print(f"  FVGs (>= {MIN_FVG_REL:.2f} x Kerzenrange) je Block:  Macro {sum(m['fvgs'] for m in macro)/len(macro):.2f}"
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
    day = date(2026, 8, 10)          # session_day = Ende der Session
    bs = blocks(day)
    labels = [b[0] for b in bs]
    # Handelstag 18:00 Vorabend .. 17:00: 23 Stunden, drei Bloecke je Stunde = 69
    assert len(bs) == 69, f"69 Bloecke erwartet, {len(bs)} bekommen"
    assert labels[0] == "18:10-18:30", labels[:3]
    # 18:10 + 69*20min = 17:10 des session_day. Der letzte Block reicht damit 10 Minuten
    # ueber den 17:00-Close hinaus und wird von MIN_BARS immer verworfen -- das ist der
    # unvermeidbare Randeffekt eines :10/:30/:50-Rasters auf einer 18:00-Session, kein Bug.
    assert labels[-1] == "16:50-17:10", labels[-3:]
    assert sum(1 for b in bs if b[3]) == 23, "23 Macro-Fenster pro Handelstag"
    # das 17:50-Fenster liegt in der Globex-Pause und darf nicht vorkommen
    assert not any(b[0].startswith("17:50") for b in bs), "17:50 liegt in der Handelspause"
    # Bloecke muessen luecken- und ueberlappungsfrei sein
    assert all(a[2] == b[1] for a, b in zip(bs, bs[1:])), "Bloecke haben Luecken"
    # der erste Block beginnt am Vorabend, der letzte am session_day
    assert bs[0][1].date() == date(2026, 8, 9), bs[0][1]
    assert bs[-1][1].date() == day, bs[-1][1]

    start, end = at(day, 9, 50), at(day, 10, 10)
    bars = [Bar(start + timedelta(minutes=i), 100.0 + i, 100.0 + i + 2, 100.0 + i - 1,
                100.0 + i + 1, None) for i in range(20)]
    m = measure(bars, start, end)
    assert m is not None and abs(m["range"] - 22.0) < 1e-9, m   # 121 - 99
    assert abs(m["netto"] - 20.0) < 1e-9, m                     # 120 - 100
    assert measure(bars[:10], start, end) is None, "zu wenige Kerzen muss None geben"

    assert session_day_from_path(Path("MNQ 2026-07-09 1m.csv")) == date(2026, 7, 9)
    print("backtest_macro.selfcheck: OK")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--symbol", default="MNQ")
    p.add_argument("--min-fvg", type=float, default=MIN_FVG_REL,
                   help="Mindestgroesse eines FVG als Vielfaches der lokalen "
                        "Kerzenrange (Default 0.45 = Median)")
    p.add_argument("--selfcheck", action="store_true")
    a = p.parse_args()
    MIN_FVG_REL = a.min_fvg
    selfcheck() if a.selfcheck else report(a.symbol)
