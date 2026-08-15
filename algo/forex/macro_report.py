#!/usr/bin/env python3
"""Auswertung von `algo/results/macro_forex_offsets.csv` -- die Macro-Frage "wie bei MNQ",
aber mit der Kontrollgruppe, die der MNQ-Seite fehlt.

Warum diese Auswertung getrennt von `backtest_macro_forex.py` steht: das Skript dort ist der
teure Messlauf (10 Paare x 24 Jahre x 22 Stunden x 6 Offsets). Die Aggregat-CSV, die es
schreibt, laesst sich in Sekunden immer wieder anders schneiden -- nach Symbol, nach Stunde,
nach Liquiditaetsregime. Messen und Auswerten zu trennen spart bei jeder neuen Frage einen
Mehrstundenlauf.

Die entscheidende Groesse ist NICHT die Expansionsquote des :50-Fensters, sondern ihr
**Abstand zu den fuenf Kontroll-Offsets derselben Stunde**. `macro_db.py` kann das auf der
MNQ-Seite nicht liefern, weil es Macro-Fenster nur untereinander vergleicht: eine Quote von
85 % um 09:50 ist wertlos, solange nicht feststeht, was 09:00/09:10/09:20/09:30/09:40 machen.

Aufruf:
    python algo/forex/macro_report.py                    # alle Symbole, gepoolt + je Symbol
    python algo/forex/macro_report.py --stunden          # Aufschluesselung je Stunde
    python algo/forex/macro_report.py --symbol EURUSD
"""
from __future__ import annotations

import argparse
import csv
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path

_ALGO = Path(__file__).resolve().parent.parent
CSV_PFAD = _ALGO / "results" / "macro_forex_offsets.csv"

MACRO_OFFSET = 50
KONTROLLE = (0, 10, 20, 30, 40)


def lade(pfad: Path = CSV_PFAD) -> list[dict]:
    if not pfad.exists():
        raise SystemExit(f"{pfad} fehlt -- zuerst `python algo/backtest_macro_forex.py --all`")
    with pfad.open(encoding="utf-8") as fh:
        return [z for z in csv.DictReader(fh)]


def wilson(treffer: float, n: int, z: float = 1.96) -> tuple[float, float]:
    """95-%-Wilson-Intervall fuer eine Quote. Bewusst Wilson statt Normal-Approximation:
    bei kleinen n oder Quoten nahe 0/1 liefert die Normalnaeherung Intervalle, die aus [0,1]
    herauslaufen -- dieselbe Wahl wie auf der MNQ-Seite (siehe wiki/assets/macro-db-*)."""
    if n <= 0:
        return (0.0, 0.0)
    p = treffer / n
    nenner = 1 + z * z / n
    mitte = (p + z * z / (2 * n)) / nenner
    rand = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / nenner
    return (max(0.0, mitte - rand), min(1.0, mitte + rand))


def je_symbol(zeilen: list[dict]) -> dict[str, dict]:
    """Gepoolt ueber alle Stunden: Expansionsquote :50 gegen den Mittelwert der Kontrollen."""
    macro: dict[str, list[float]] = defaultdict(list)
    macro_n: dict[str, int] = defaultdict(int)
    macro_treffer: dict[str, float] = defaultdict(float)
    kontrolle: dict[str, list[float]] = defaultdict(list)
    kontrolle_n: dict[str, int] = defaultdict(int)
    kontrolle_treffer: dict[str, float] = defaultdict(float)

    for z in zeilen:
        sym, off, n = z["symbol"], int(z["offset"]), int(z["n"])
        rate = float(z["expansion_rate"])
        if off == MACRO_OFFSET:
            macro[sym].append(rate)
            macro_n[sym] += n
            macro_treffer[sym] += rate * n
        elif off in KONTROLLE:
            kontrolle[sym].append(rate)
            kontrolle_n[sym] += n
            kontrolle_treffer[sym] += rate * n

    out = {}
    for sym in sorted(macro):
        m = macro_treffer[sym] / max(macro_n[sym], 1)
        k = kontrolle_treffer[sym] / max(kontrolle_n[sym], 1)
        lo, hi = wilson(macro_treffer[sym], macro_n[sym])
        klo, khi = wilson(kontrolle_treffer[sym], kontrolle_n[sym])
        out[sym] = {
            "macro_rate": m, "macro_n": macro_n[sym], "macro_ci": (lo, hi),
            "kontroll_rate": k, "kontroll_n": kontrolle_n[sym], "kontroll_ci": (klo, khi),
            "delta_pp": 100 * (m - k),
            # Ueberlappen die Intervalle, ist der Unterschied nicht von Rauschen zu trennen.
            "trennbar": lo > khi or klo > hi,
        }
    return out


def je_stunde(zeilen: list[dict], symbol: str | None = None) -> dict[int, dict]:
    macro_t: dict[int, float] = defaultdict(float)
    macro_n: dict[int, int] = defaultdict(int)
    kon_t: dict[int, float] = defaultdict(float)
    kon_n: dict[int, int] = defaultdict(int)
    for z in zeilen:
        if symbol and z["symbol"] != symbol:
            continue
        h, off, n = int(z["hour"]), int(z["offset"]), int(z["n"])
        rate = float(z["expansion_rate"])
        if off == MACRO_OFFSET:
            macro_t[h] += rate * n
            macro_n[h] += n
        elif off in KONTROLLE:
            kon_t[h] += rate * n
            kon_n[h] += n
    out = {}
    for h in sorted(macro_n):
        m = macro_t[h] / max(macro_n[h], 1)
        k = kon_t[h] / max(kon_n[h], 1)
        lo, hi = wilson(macro_t[h], macro_n[h])
        klo, khi = wilson(kon_t[h], kon_n[h])
        out[h] = {"macro_rate": m, "kontroll_rate": k, "delta_pp": 100 * (m - k),
                  "n": macro_n[h], "trennbar": lo > khi or klo > hi}
    return out


def demo() -> None:
    """Selbstcheck ohne Datei: Wilson-Intervall und die Aggregation gegen Handrechnung."""
    lo, hi = wilson(50, 100)
    assert 0.40 < lo < 0.41 and 0.59 < hi < 0.60, (lo, hi)
    lo, hi = wilson(0, 10)
    assert lo == 0.0 and 0 < hi < 1, (lo, hi)          # kein Ausbrechen aus [0,1]
    lo, hi = wilson(10, 10)
    assert 0 < lo < 1 and hi == 1.0, (lo, hi)
    assert wilson(0, 0) == (0.0, 0.0)

    zeilen = [
        {"symbol": "X", "hour": "9", "offset": "50", "n": "100", "expansion_rate": "0.60"},
        {"symbol": "X", "hour": "9", "offset": "0", "n": "100", "expansion_rate": "0.40"},
        {"symbol": "X", "hour": "9", "offset": "10", "n": "100", "expansion_rate": "0.40"},
    ]
    s = je_symbol(zeilen)["X"]
    assert abs(s["macro_rate"] - 0.60) < 1e-9, s
    assert abs(s["kontroll_rate"] - 0.40) < 1e-9, s
    assert abs(s["delta_pp"] - 20.0) < 1e-9, s
    assert s["macro_n"] == 100 and s["kontroll_n"] == 200, s
    assert s["trennbar"], "60 % gegen 40 % bei n=100/200 muss trennbar sein"

    # Gewichtung nach n, nicht Mittelwert der Quoten: eine Stunde mit 1 Fenster darf eine
    # mit 1000 nicht gleich stark ziehen.
    zeilen2 = [
        {"symbol": "Y", "hour": "1", "offset": "50", "n": "1000", "expansion_rate": "0.10"},
        {"symbol": "Y", "hour": "2", "offset": "50", "n": "1", "expansion_rate": "1.00"},
        {"symbol": "Y", "hour": "1", "offset": "0", "n": "1000", "expansion_rate": "0.10"},
    ]
    s2 = je_symbol(zeilen2)["Y"]
    assert abs(s2["macro_rate"] - 101 / 1001) < 1e-9, s2["macro_rate"]

    h = je_stunde(zeilen)
    assert abs(h[9]["delta_pp"] - 20.0) < 1e-9, h
    print("forex.macro_report demo: OK")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stunden", action="store_true", help="Aufschluesselung je Stunde")
    ap.add_argument("--symbol", default=None)
    ap.add_argument("--demo", action="store_true")
    a = ap.parse_args(argv)

    if a.demo:
        demo()
        return 0

    zeilen = lade()
    symbole = sorted({z["symbol"] for z in zeilen})
    print(f"Quelle: {CSV_PFAD.name}   Symbole: {len(symbole)}   Zeilen: {len(zeilen):,}")
    print()

    if a.stunden:
        print(f"Je Stunde{' (' + a.symbol + ')' if a.symbol else ' (alle Symbole gepoolt)'} — "
              f"Expansionsquote :50 gegen Kontroll-Offsets :00–:40")
        print("{:>5} {:>10} {:>10} {:>9} {:>10} {:>10}".format(
            "Std", "Macro %", "Kontr %", "Delta pp", "n", "trennbar"))
        for h, d in je_stunde(zeilen, a.symbol).items():
            print("{:>5} {:>10.2f} {:>10.2f} {:>+9.2f} {:>10,} {:>10}".format(
                f"{h:02d}:50", 100 * d["macro_rate"], 100 * d["kontroll_rate"],
                d["delta_pp"], d["n"], "ja" if d["trennbar"] else "nein"))
        return 0

    print("Je Symbol — Expansionsquote des :50-Fensters gegen die fuenf Kontroll-Offsets")
    print("{:<9} {:>10} {:>10} {:>9} {:>12} {:>10}".format(
        "Symbol", "Macro %", "Kontr %", "Delta pp", "n (Macro)", "trennbar"))
    ergebnisse = je_symbol(zeilen)
    for sym, d in ergebnisse.items():
        print("{:<9} {:>10.2f} {:>10.2f} {:>+9.2f} {:>12,} {:>10}".format(
            sym, 100 * d["macro_rate"], 100 * d["kontroll_rate"], d["delta_pp"],
            d["macro_n"], "ja" if d["trennbar"] else "nein"))

    if ergebnisse:
        deltas = [d["delta_pp"] for d in ergebnisse.values()]
        positiv = sum(1 for x in deltas if x > 0)
        print()
        print(f"Median-Delta ueber {len(deltas)} Symbole: {statistics.median(deltas):+.2f} pp   "
              f"positiv: {positiv}/{len(deltas)}   "
              f"trennbar: {sum(1 for d in ergebnisse.values() if d['trennbar'])}/{len(deltas)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
