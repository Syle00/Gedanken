#!/usr/bin/env python3
"""Erste Version des Backtest-Harness aus algo/PLAN.md, Code-Idee 1.

Laeuft ueber ALLE Handelstage in raw/marktdaten/<jjjj>/<mm>/<dd.mm.jjjj>/, ruft je Tag
dieselben Detektoren aus tools/analyze_ohlc.py auf (keine Neuimplementierung) und
aggregiert die Statistik, gegen die sich ICT-Wiki-Behauptungen pruefen lassen — z.B.
"das C.E eines FVG/ORG wird zu ~70% erreicht".

Basis-Timeframe ist einheitlich 5m (Kompromiss: deckt volle Sessions ab, nicht zu
verrauscht). Jeder Tag wird auf sein eigenes Fenster (00:00-17:00 NY) beschraenkt, damit
die Lookback-Historie in einer CSV nicht in mehreren Tagesordnern doppelt gezaehlt wird.

Aufruf:
    python algo/backtest_ohlc.py MNQ
    python algo/backtest_ohlc.py MNQ -o "wiki/synthesis/Muster-Validierung (laufend).md"

Abhaengigkeiten: nur tools/analyze_ohlc.py (Stdlib). pandas wird hier bewusst NICHT
gebraucht -- die Aggregation ist eine Handvoll Zaehler, kein DataFrame-Problem.
"""

from __future__ import annotations

import sys
import statistics
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from analyze_ohlc import (  # noqa: E402
    load, at, slice_between, fvgs, sweeps, structure_breaks, macro_windows, viis,
    TF_MINUTES, CFG,
)

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "raw" / "marktdaten"
BASE_TF = "5m"

# tools/analyze_ohlc.py skaliert min_age/confirm beim CLI-Aufruf mit dem Timeframe
# (main(), Zeile "Rauschfilter in Kerzen skalieren..."); wer die Detektoren direkt
# importiert statt ueber die CLI, muss dieselbe Skalierung von Hand anwenden -- sonst
# laufen Tagesreport (skaliert) und Backtest (unskaliert) mit verschiedenen Schwellen
# und liefern nicht vergleichbare Zahlen.
_tf_min = TF_MINUTES[BASE_TF]
CFG.update(min_age=max(3, round(15 / _tf_min)), confirm=max(2, round(5 / _tf_min)))


def find_days() -> list[tuple[date, str, Path]]:
    """(Handelstag, Symbol, Pfad zur BASE_TF-Datei) fuer jeden Tagesordner."""
    out = []
    for day_dir in sorted(DATA_DIR.glob("*/*/*")):
        if not day_dir.is_dir():
            continue
        try:
            day = datetime.strptime(day_dir.name, "%d.%m.%Y").date()
        except ValueError:
            continue
        for f in sorted(day_dir.glob(f"* {day.isoformat()} {BASE_TF}.csv")):
            symbol = f.name.split(" ")[0]
            out.append((day, symbol, f))
    return out


def analyze_day(day: date, path: Path) -> dict:
    bars = load(path)
    day_bars = slice_between(bars, at(day, 0), at(day, 17))
    if not day_bars:
        return {}
    med_bar = statistics.median(b.rng for b in day_bars) or 1.0

    fg_all = [g for g in fvgs(bars) if at(day, 0) <= g["t"] < at(day, 17)]
    fg_big = [g for g in fg_all if g["size"] >= med_bar]

    vi = [v for v in viis(bars) if at(day, 0) <= v["t"] < at(day, 17)]

    sw = [s for s in sweeps(bars, CFG["swing"], CFG["min_age"], CFG["min_pen"] * med_bar,
                             CFG["confirm"]) if at(day, 0) <= s["t"] < at(day, 17)]
    sb = [x for x in structure_breaks(bars, CFG["swing"], CFG["min_age"])
          if at(day, 0) <= x["t"] < at(day, 17)]

    mrows = []
    for _, s, e in macro_windows(day):
        seg = slice_between(bars, s, e)
        if seg:
            mrows.append(max(b.h for b in seg) - min(b.l for b in seg))
    macro_med = statistics.median(mrows) if mrows else 0.0
    macro_expansions = sum(1 for r in mrows if macro_med and r > 1.5 * macro_med)

    return {
        "fvg_all": len(fg_all),
        "fvg_all_ce_hit": sum(1 for g in fg_all if g["ce_hit"]),
        "fvg_all_filled": sum(1 for g in fg_all if g["filled"]),
        "fvg_big": len(fg_big),
        "fvg_big_ce_hit": sum(1 for g in fg_big if g["ce_hit"]),
        "fvg_big_filled": sum(1 for g in fg_big if g["filled"]),
        "vii": len(vi),
        "vii_filled": sum(1 for v in vi if v["filled"]),
        "sweeps": len(sw),
        "sweeps_immediate": sum(1 for s in sw if s["bars_back"] == 0),
        "bos": sum(1 for x in sb if x["type"] == "BOS"),
        "mss": sum(1 for x in sb if x["type"] == "MSS"),
        "macro_windows": len(mrows),
        "macro_expansions": macro_expansions,
    }


def pct(n: int, d: int) -> str:
    return f"{100 * n / d:.0f}%" if d else "–"


def report(rows: list[tuple[date, str, dict]]) -> list[str]:
    n_days = len(rows)
    agg = {}
    for _, _, r in rows:
        for k, v in r.items():
            agg[k] = agg.get(k, 0) + v

    L = []
    L.append("---")
    L.append("tags: [synthesis, trading-ict, marktdaten, backtest]")
    L.append(f"created: {date.today().isoformat()}")
    L.append(f"updated: {date.today().isoformat()}")
    L.append('sources: ["[[OHLC-Datenanalyse (Workflow)]]"]')
    L.append("---")
    L.append("")
    L.append("# Muster-Validierung (laufend)")
    L.append("")
    L.append("**Generiert** von `algo/backtest_ohlc.py` aus allen Handelstagen in "
              "`raw/marktdaten/`. Prueft ICT-Behauptungen aus dem Wiki gegen die "
              "tatsaechlichen Daten, statt sie als gegeben zu uebernehmen. Wird bei jedem "
              "neuen Handelstag neu ausgefuehrt — siehe [[../algo/PLAN.md|Algo-Projekt]].")
    L.append("")
    if n_days < 20:
        L.append(f"> ⚠️ **Nur {n_days} Handelstag(e) in der Datenbasis.** Jede Prozentzahl "
                  f"unten ist bei dieser Stichprobengroesse **statistisch nicht belastbar** "
                  f"— sie zeigt den aktuellen Stand, keine bestaetigte Regel. Als Faustwert "
                  f"gilt: unter ~20-30 Tagen kann jede Zahl durch einen einzigen "
                  f"ungewoehnlichen Tag komplett kippen. Diese Seite wird bei jedem neuen "
                  f"Tag automatisch aktualisiert; erst beobachten, ob sich die Werte "
                  f"stabilisieren, bevor daraus eine Handelsregel wird.")
        L.append("")
    L.append(f"Datenbasis: {n_days} Handelstag(e) — " +
              ", ".join(d.isoformat() for d, _, _ in rows) + f" ({BASE_TF}-Basis).")
    L.append("")

    L.append("## Abdeckung (Nutzerwunsch: alle PD Arrays, das gesamte Wiki)")
    L.append("")
    L.append("Diese Seite soll perspektivisch jede pruefbare Wiki-Behauptung gegen echte "
              "Daten testen. Stand jetzt automatisch pruefbar (Detektoren existieren in "
              "`tools/analyze_ohlc.py`):")
    L.append("")
    L.append("- [[Fair Value Gap (FVG)]] (inkl. C.E-Fuellung), [[Volume Imbalance (VII)]], "
              "[[ORG (Opening Range Gap) & 1st Presented FVG]] (ueber FVG-Detektor), "
              "Liquidity Sweeps / [[Open Float & Liquidity Pools]], "
              "[[Market Structure Shift (MSS)]] / BOS-MSS / [[CISD (Change in State of Delivery)]] "
              "(als Struktur-Proxy), [[ICT Macros & Leading Candles]]-Expansion.")
    L.append("")
    L.append("**Noch ohne eigenen Detektor** (Backlog in `algo/PLAN.md`, wird nach und nach "
              "ergaenzt statt in einem Schritt geraten): [[Order Block]] + Varianten "
              "([[Breaker Block]], [[Rejection Block]], [[Mitigation Block]], "
              "[[Reclaimed Order Block]]), [[IFVG (Inverse Fair Value Gap)]], "
              "[[Balanced Price Range (BPR)]], [[Central Bank Dealers Range (CBDR)]], "
              "[[New Week Opening Gap (NWOG) Bias|NWOG/NDOG]], [[Optimal Trade Entry (OTE)]], "
              "[[Breakaway Gap]], [[Suspension Block]], [[Judas Swing]] als eigenes Zeitfenster "
              "(bislang nur ueber Sweeps sichtbar, nicht als benanntes Ereignis), "
              "[[Quarterly Shift]], [[SMT (Smart Money Divergence)]] (braucht ein zweites "
              "Symbol, bisher wird nur MNQ erfasst).")
    L.append("")

    L.append("## Fair Value Gap / C.E-Fuellung")
    L.append("")
    L.append("Testet die verbreitete ICT-Behauptung \"das C.E eines FVG/ORG wird meist "
              "erreicht\" (oft als ~70% zitiert) an den tatsaechlichen Daten. Zwei "
              "unterschiedliche Fragen, die in der Praxis oft vermischt werden:")
    L.append("")
    L.append("| | Alle FVGs | Nur groessere FVGs (≥ Median-Kerzenrange des Tages) |")
    L.append("|---|---|---|")
    L.append(f"| Anzahl | {agg.get('fvg_all', 0)} | {agg.get('fvg_big', 0)} |")
    L.append(f"| C.E erreicht (Preis beruehrt die 50%-Linie) | "
              f"{pct(agg.get('fvg_all_ce_hit', 0), agg.get('fvg_all', 0))} | "
              f"{pct(agg.get('fvg_big_ce_hit', 0), agg.get('fvg_big', 0))} |")
    L.append(f"| Komplett gefuellt (ganze Luecke geschlossen) | "
              f"{pct(agg.get('fvg_all_filled', 0), agg.get('fvg_all', 0))} | "
              f"{pct(agg.get('fvg_big_filled', 0), agg.get('fvg_big', 0))} |")
    L.append("")
    L.append("„C.E erreicht\" und „komplett gefuellt\" sind unterschiedliche Ereignisse — "
              "die 70%-Zahl, die kursiert, bezieht sich vermutlich auf ersteres. Diese "
              "Seite zaehlt beide getrennt, um genau diese Vermischung sichtbar zu machen. "
              "Siehe [[Fair Value Gap (FVG)]], [[ORG (Opening Range Gap) & 1st Presented FVG]].")
    L.append("")

    L.append("## Volume Imbalance (VII)")
    L.append("")
    L.append(f"{agg.get('vii', 0)} VII (Close→Open-Luecke zwischen zwei Kerzen), "
              f"{pct(agg.get('vii_filled', 0), agg.get('vii', 0))} davon wieder komplett "
              f"gefuellt. Siehe [[Volume Imbalance (VII)]].")
    L.append("")

    L.append("## Liquidity Sweeps")
    L.append("")
    L.append(f"{agg.get('sweeps', 0)} Sweeps insgesamt, davon "
              f"{pct(agg.get('sweeps_immediate', 0), agg.get('sweeps', 0))} mit sofortiger "
              f"Rueckeroberung (`bars_back == 0`) — der Rest brauchte laenger, siehe "
              f"`confirm`-Fenster in [[OHLC-Datenanalyse (Workflow)]].")
    L.append("")

    L.append("## Market Structure Breaks (BOS/MSS → CISD)")
    L.append("")
    bos, mss = agg.get("bos", 0), agg.get("mss", 0)
    total_sb = bos + mss
    L.append(f"{total_sb} Structure Breaks insgesamt: {bos} BOS (Fortsetzung), {mss} MSS "
              f"(Richtungswechsel) — {pct(mss, total_sb)} der Breaks waren ein "
              f"Richtungswechsel. Jeder Break ist ein potenzieller [[CISD (Change in State of Delivery)]]; "
              f"siehe dort fuer die Bedingung (Imbalance muss enthalten sein), die dieser "
              f"Zaehler noch nicht prueft.")
    L.append("")

    L.append("## Macro-Fenster-Expansion")
    L.append("")
    L.append(f"{agg.get('macro_expansions', 0)} von {agg.get('macro_windows', 0)} "
              f"Macro-Fenstern (XX:50–XX+1:10) waren Expansion (>1,5x Tages-Median) = "
              f"{pct(agg.get('macro_expansions', 0), agg.get('macro_windows', 0))}. Bei 24 "
              f"Fenstern/Tag waere ein Gleichverteilungs-Erwartungswert bei ~keinem "
              f"besonderen Fenster — dass es ueberhaupt planbare Haeufungen gibt (z.B. "
              f"[[NY Lunch Macro Model]]), ist erst ab mehr Tagen pruefbar.")
    L.append("")

    L.append("## Pro Tag")
    L.append("")
    L.append("| Tag | FVGs (groß) | C.E erreicht | Sweeps | BOS/MSS | Macro-Expansionen |")
    L.append("|---|---|---|---|---|---|")
    for d, sym, r in rows:
        if not r:
            continue
        L.append(f"| {d.isoformat()} | {r['fvg_big']} | "
                  f"{pct(r['fvg_big_ce_hit'], r['fvg_big'])} | {r['sweeps']} | "
                  f"{r['bos']}/{r['mss']} | {r['macro_expansions']}/{r['macro_windows']} |")
    L.append("")

    L.append("## Verwandt")
    L.append("")
    L.append("- [[OHLC-Datenanalyse (Workflow)]] — Detektoren, die diese Seite aggregiert")
    L.append("- [[Fair Value Gap (FVG)]], [[ORG (Opening Range Gap) & 1st Presented FVG]], "
              "[[CISD (Change in State of Delivery)]]")
    L.append("- `algo/PLAN.md` — Code-Idee 1 (Backtest-Harness), diese Seite ist die erste Version")
    return L


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("symbol", nargs="?", default=None, help="Nur dieses Symbol (default: alle)")
    ap.add_argument("-o", "--out", help="Ausgabedatei (default: stdout)")
    a = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")

    days = find_days()
    if a.symbol:
        days = [d for d in days if d[1] == a.symbol]
    rows = [(day, sym, analyze_day(day, path)) for day, sym, path in days]
    rows = [r for r in rows if r[2]]

    lines = report(rows)
    text = "\n".join(lines)
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
        print(f"geschrieben: {a.out} ({len(rows)} Handelstag(e))")
    else:
        print(text)


if __name__ == "__main__":
    main()
