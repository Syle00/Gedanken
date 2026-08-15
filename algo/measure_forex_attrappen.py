#!/usr/bin/env python3
"""Misst den Attrappen-Anteil (o=h=l=c) je Forex-Datei in raw/marktdaten/ -- Grundlage fuer
den Loeschvorschlag aus Spec §8. LOESCHT NICHTS. Legt nur eine Liste vor; die eigentliche
Loeschung braucht ausdrueckliche Nutzerfreigabe (siehe algo/PLAN.md).

Aufruf:
    python algo/measure_forex_attrappen.py
    python algo/measure_forex_attrappen.py --demo
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from analyze_ohlc import SESSION_TYP  # noqa: E402
from backtest_common import DATA_DIR, write_result  # noqa: E402

FOREX_SYMBOLE = [s for s, t in SESSION_TYP.items() if t == "24x5"]
LOESCH_SCHWELLE = 0.90  # Spec §8.2: Vorschlag nur ueber 90% Flat-Anteil


def flat_anteil(pfad: Path) -> tuple[int, int]:
    """(flache Kerzen, Kerzen gesamt) einer CSV-Datei."""
    flach = gesamt = 0
    with pfad.open(newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            gesamt += 1
            if row["open"] == row["high"] == row["low"] == row["close"]:
                flach += 1
    return flach, gesamt


def messen(symbol: str, tf: str) -> list[dict]:
    out = []
    for pfad in sorted(DATA_DIR.glob(f"*/*/*/{symbol} *-*-* {tf}.csv")):
        if "RTH" in pfad.name:
            continue
        flach, gesamt = flat_anteil(pfad)
        if gesamt == 0:
            continue
        out.append({"pfad": str(pfad.relative_to(DATA_DIR.parent.parent)),
                    "symbol": symbol, "tf": tf, "kerzen": gesamt,
                    "flat_anteil": round(flach / gesamt, 4)})
    return out


def _demo() -> None:
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        ordner = Path(tmp) / "raw" / "marktdaten" / "2026" / "01" / "05.01.2026"
        ordner.mkdir(parents=True)
        pfad = ordner / "TEST 2026-01-05 1m.csv"
        pfad.write_text("time,open,high,low,close\n1,1,1,1,1\n2,1,2,1,2\n3,1,1,1,1\n",
                        encoding="utf-8")
        global DATA_DIR
        orig = DATA_DIR
        DATA_DIR = Path(tmp) / "raw" / "marktdaten"
        try:
            r = messen("TEST", "1m")
            assert len(r) == 1 and r[0]["flat_anteil"] == round(2 / 3, 4), r
        finally:
            DATA_DIR = orig
    print("measure_forex_attrappen: Selbstcheck ok")


def main() -> int:
    if "--demo" in sys.argv:
        _demo()
        return 0

    alle = []
    for sym in sorted(FOREX_SYMBOLE):
        for tf in ("1m", "5m", "15m"):  # 1d/1h/4h bleiben laut Spec §8.3 ausdruecklich erhalten
            alle.extend(messen(sym, tf))

    vorschlag = [r for r in alle if r["flat_anteil"] >= LOESCH_SCHWELLE]
    print(f"{len(alle)} Dateien geprueft, {len(vorschlag)} ueber {LOESCH_SCHWELLE:.0%} flach "
          f"(Loeschkandidaten, NICHT geloescht):")
    for r in vorschlag[:30]:
        print(f"  {r['flat_anteil']:.1%}  {r['pfad']}")
    if len(vorschlag) > 30:
        print(f"  ... und {len(vorschlag) - 30} weitere, siehe Report")

    write_result("forex_attrappen_report", {"alle": alle, "loeschvorschlag": vorschlag})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
