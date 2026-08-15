#!/usr/bin/env python3
"""Backtest: legt die Midnight/London Opening Range (0:00-0:30 NY) per Standard-Deviation-
Projektion das Tages-High/-Low fest?

These aus wiki/concepts/Midnight Opening Range.md: der Fib ueber die 0:00-0:30-Range wird
mit negativen Standard Deviations (Vielfache der Range-Groesse) nach unten verlaengert, um
Tages-High/-Low zu antizipieren. Maximale Manipulation waehrend London (1:00-5:00 NY) soll
bei -1 STD liegen -- geht der Preis weiter, ist es kein Manipulation-Swing mehr, sondern der
eigentliche Move.

Gemessen wird k = wie viele Range-Vielfache der Tages-Low/-High ueber die Range-Grenze
hinausgeht (k=0: bleibt innerhalb der Range, k=1: genau -1/+1 STD, k=2: -2/+2 STD, ...) --
sowohl fuer die komplette London-Session als auch fuer den ganzen Tag.

Aufruf:
    python algo/backtest_midnight_range_std.py
"""
from __future__ import annotations

import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from analyze_ohlc import load, at, SESSION_TYP  # noqa: E402
from backtest_org_ce import find_days  # noqa: E402
from backtest_common import write_result  # noqa: E402

BUCKETS = [0.5, 1.0, 1.5, 2.0, 3.0, 5.0, float("inf")]


def window_gaps(bars, day, start_hm, end_hm) -> list[int]:
    """Fehlende Minuten in einem **teilweise** befuellten 1m-Fenster, als Offsets ab `start_hm`.

    Existiert, weil yfinance fuer MNQ=F systematisch die ersten ~9 Minuten nach Mitternacht
    NY nicht liefert (verifiziert am 2026-08-11 gegen den yfinance-Rohabruf: die Luecke
    steckt in der Quelle, nicht in fetch_yfinance.py). An 19 von 24 MNQ-1m-Tagen fehlten
    genau 00:00-00:08 -- inklusive der 0:00-Kerze, also des Midnight Opening Price.

    Ein **komplett leeres** Fenster gibt bewusst `[]` zurueck, nicht "alle Minuten fehlen":
    ein Tag ohne Intraday-Daten ist keine loechrige Messung, sondern gar keine, und die
    Aufrufer verwerfen ihn ohnehin ueber `session_range() is None`. Ohne diese Unterscheidung
    zaehlte jeder 1d-only-Tag als Datenluecke und blies die Warnung auf (aufgefallen
    2026-08-11: `judas` meldete 23 "Luecken" im sauberen 7:00-7:30-Fenster).
    """
    start, end = at(day, *start_hm), at(day, *end_hm)
    have = {int((b.t - start).total_seconds() // 60) for b in bars if start <= b.t < end}
    if not have:
        return []
    step = bar_minutes(bars)
    return sorted(set(range(0, int((end - start).total_seconds() // 60), step)) - have)


def bar_minutes(bars) -> int:
    """Haeufigster Abstand zwischen aufeinanderfolgenden Kerzen, in Minuten.

    `find_days()` liefert 1m bevorzugt, faellt aber auf **5m** zurueck, wenn fuer den Tag
    keine 1m-Datei existiert. Eine fest in Minuten gerechnete Vollstaendigkeitspruefung haelt
    die 6 Kerzen eines 5m-Fensters dann faelschlich fuer 24 fehlende Minuten und verwirft den
    Tag (aufgefallen 2026-08-11: 20 gesunde 7:00-7:30-Fenster wurden so weggeworfen).
    Der Modalwert ist robuster als min/mean -- eine einzelne Sessionpause verschiebt ihn nicht.
    """
    deltas = [int((b.t - a.t).total_seconds() // 60) for a, b in zip(bars, bars[1:])]
    deltas = [d for d in deltas if d > 0]
    return statistics.mode(deltas) if deltas else 1


def session_range(bars, day, start_hm: tuple[int, int], end_hm: tuple[int, int],
                   expect_complete: bool = False):
    """Kerzen-High/Low ueber ein Zeitfenster (z.B. eine Opening Range). None, wenn keine
    Kerzen im Fenster liegen oder das Fenster keine echte Range hat (rng <= 0).

    `expect_complete=True` verlangt zusaetzlich, dass **jede** Minute des Fensters vorliegt,
    und gibt sonst None zurueck. Fuer Opening Ranges ist das Pflicht: fehlen ausgerechnet die
    ersten Minuten, fehlt der Opening Price, und High/Low stammen aus einem verkuerzten
    Fenster -- die Range faellt dann typischerweise zu klein aus und blaeht jede daraus
    abgeleitete STD-Kennzahl auf. Der Aufrufer sieht die Verwerfung nicht; wer zaehlt, wie
    viele Tage wegfallen, muss `window_gaps()` selbst aufrufen und die Zahl ausweisen.
    """
    win = [b for b in bars if at(day, *start_hm) <= b.t < at(day, *end_hm)]
    if not win:
        return None
    if expect_complete and window_gaps(bars, day, start_hm, end_hm):
        return None
    rh, rl = max(b.h for b in win), min(b.l for b in win)
    rng = rh - rl
    return (rh, rl, rng) if rng > 0 else None


def midnight_range(bars, day):
    """Midnight/London Opening Range 0:00-0:30 NY. Verlangt ein vollstaendiges Fenster --
    siehe `window_gaps()` fuer den Grund."""
    return session_range(bars, day, (0, 0), (0, 30), expect_complete=True)


def k_extension(bars, day, start, end, rh, rl, rng):
    seg = [b for b in bars if start <= b.t < end]
    if not seg:
        return None, None
    day_high = max(b.h for b in seg)
    day_low = min(b.l for b in seg)
    k_high = max(0.0, (day_high - rh) / rng)
    k_low = max(0.0, (rl - day_low) / rng)
    return k_high, k_low


def bucket(k: float) -> str:
    for b in BUCKETS:
        if k <= b:
            return f"<= {b} STD" if b != float("inf") else "> 5 STD"
    return "> 5 STD"


def report(name: str, ks: list[float]) -> None:
    if not ks:
        print(f"{name}: keine Tage")
        return
    print(f"\n{name} (n={len(ks)}): Median {statistics.median(ks):.2f} STD, "
          f"Mittelwert {statistics.mean(ks):.2f} STD, Max {max(ks):.2f} STD")
    counts: dict[str, int] = {}
    for k in ks:
        counts[bucket(k)] = counts.get(bucket(k), 0) + 1
    for b in BUCKETS:
        label = f"<= {b} STD" if b != float("inf") else "> 5 STD"
        c = counts.get(label, 0)
        print(f"  {label:<12}{c:>4}  ({100 * c / len(ks):.1f}%)")


def run(symbol: str = "MNQ") -> dict:
    if SESSION_TYP.get(symbol) == "24x5":
        import marktdaten
        alle_bars = marktdaten.bars(symbol, "1m")
        nach_tag: dict = {}
        for b in alle_bars:
            nach_tag.setdefault(b.t.date(), []).append(b)
        tage = sorted(nach_tag.items())
    else:
        tage = [(day, load(path)) for day, path in find_days(symbol)]

    london_high, london_low, day_high, day_low = [], [], [], []
    days_used = 0
    days_incomplete = []
    for day, bars in tage:
        if window_gaps(bars, day, (0, 0), (0, 30)):
            days_incomplete.append(str(day))
        mr = midnight_range(bars, day)
        if mr is None:
            continue
        rh, rl, rng = mr
        lh, ll = k_extension(bars, day, at(day, 1, 0), at(day, 5, 0), rh, rl, rng)
        dh, dl = k_extension(bars, day, at(day, 0, 30), at(day, 17, 0), rh, rl, rng)
        if lh is None or dh is None:
            continue
        days_used += 1
        london_high.append(lh)
        london_low.append(ll)
        day_high.append(dh)
        day_low.append(dl)

    exceed_1std = (sum(1 for k in london_low if k > 1.0) / len(london_low)) if london_low else None

    return {"days_used": days_used, "london_high": london_high, "london_low": london_low,
            "day_high": day_high, "day_low": day_low,
            "days_incomplete": days_incomplete,
            "exceed_1std_pct": 100 * exceed_1std if exceed_1std is not None else None}


def main() -> None:
    result = run()
    print(f"{result['days_used']} Handelstage mit vollstaendiger Midnight-Range.")
    if result["days_incomplete"]:
        n = len(result["days_incomplete"])
        print(f"WARNUNG: {n} Tage wegen Luecken im 0:00-0:30-Fenster verworfen "
              f"(yfinance liefert die ersten Minuten nach Mitternacht oft nicht). "
              f"Betroffen: {', '.join(result['days_incomplete'][:5])}"
              f"{' ...' if n > 5 else ''}")
        if result["days_used"] < n:
            print("         Es bleiben weniger gueltige als verworfene Tage — die Zahlen "
                  "unten sind eine Stichprobe, keine Basisrate.")
    print("\n-- Waehrend London (1:00-5:00 NY) -- These: 'max. Manipulation bis -1 STD' --")
    report("London-Low unter Range-Tief", result["london_low"])
    report("London-High ueber Range-Hoch", result["london_high"])
    print("\n-- Ganzer Tag (0:30-17:00 NY) --")
    report("Tages-Low unter Range-Tief", result["day_low"])
    report("Tages-High ueber Range-Hoch", result["day_high"])

    if result["exceed_1std_pct"] is not None:
        print(f"\nLondon-Low geht bei {result['exceed_1std_pct']:.1f}% der Tage ueber -1 STD "
              f"hinaus (These behauptet: das soll waehrend London selten/nie passieren).")

    write_result("backtest_midnight_range_std", {
        "days_used": result["days_used"], "exceed_1std_pct": result["exceed_1std_pct"],
        "london_low_median": statistics.median(result["london_low"]) if result["london_low"] else None,
        "london_high_median": statistics.median(result["london_high"]) if result["london_high"] else None,
        "day_low_median": statistics.median(result["day_low"]) if result["day_low"] else None,
        "day_high_median": statistics.median(result["day_high"]) if result["day_high"] else None,
    })


if __name__ == "__main__":
    main()
