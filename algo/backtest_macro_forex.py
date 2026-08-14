#!/usr/bin/env python3
"""Macro-Fenster (:50-:10) auf dem Forex-Tiefbestand -- mit Offset-Kontrollgruppe.

Zwei Fragen, die `algo/macro_db.py` nicht beantworten kann:

1. **Ist `:50` ueberhaupt besonders?** macro_db vergleicht Macro-Fenster nur
   untereinander (09:50 gegen 10:50 gegen ...) und hat damit keine Kontrollgruppe. Hier
   laeuft je Stunde dasselbe Mass ueber SECHS 20-Minuten-Fenster (Offset :00 :10 :20
   :30 :40 :50). Ist die ICT-These wahr, muss sich Offset 50 von den fuenf anderen
   abheben. Tut er das nicht, ist der "Macro-Effekt" schlicht das, was jedes beliebige
   20-Minuten-Fenster tut.
2. **Ist der Effekt marktweit oder MNQ-Artefakt?** ICTs Begruendung ("ein Algorithmus
   steuert den Preis zu festen Uhrzeiten") impliziert einen interbank-weiten Mechanismus.
   Dann muesste er im FX-Spot mit 24 Jahren Historie genauso auftauchen wie im MNQ.

Skalenfreiheit ist hier der springende Punkt: `macro_db.NETTO_THR = 30.0` sind
MNQ-Indexpunkte und im EURUSD sinnlos. Alle Groessen werden deshalb auf die
**Median-Kerzenrange des jeweiligen Handelstags** (`medbar`) normiert. `K` (das Vielfache
von medbar, ab dem ein Netto als Expansion zaehlt) wird auf dem MNQ-Bestand kalibriert,
damit die Expansionsquote dort der bestehenden macro_db-Basisrate entspricht -- danach
gilt derselbe K fuer alle Symbole.

Warum `medbar` je Tag kein Lookahead-Problem ist: der Normierer ist fuer alle sechs
Offsets desselben Tages identisch und kann den Vergleich Offset-50-gegen-Rest daher
nicht verzerren. Es ist eine deskriptive Studie ueber die Uhr, kein Handelssignal --
als Merkmal in einer Regel waere er unzulaessig.

Aufruf:
    python algo/backtest_macro_forex.py --symbols EURUSD GBPUSD
    python algo/backtest_macro_forex.py --all          # alle 10 Paare, alle Jahre
    python algo/backtest_macro_forex.py --mnq          # nur MNQ (Kalibrierung/Vergleich)
    python algo/backtest_macro_forex.py --selfcheck
"""
from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from tools.analyze_ohlc import DATA_DIR, Bar, at, load  # noqa: E402

from macro_db import (DIR_THR, N_HOURS, SESSION_BY_HOUR, fmt_quote,  # noqa: E402
                      measure_window, quote, window_bars)

ROOT = Path(__file__).resolve().parent.parent
TIEF_DIR = ROOT / "raw" / "marktdaten-tief"
RESULT = Path(__file__).resolve().parent / "results" / "macro_forex.json"
AGG_CSV = Path(__file__).resolve().parent / "results" / "macro_forex_offsets.csv"
CACHE = Path(__file__).resolve().parent / "results" / "macro_forex_cache"

# Die sechs 20-Minuten-Fenster je Stunde. 50 ist das ICT-Macro, die anderen fuenf sind
# die Kontrollgruppe. Sie ueberlappen sich -- das ist gewollt: verglichen wird die
# Verteilung je Offset, nicht eine Zerlegung der Stunde.
OFFSETS = (0, 10, 20, 30, 40, 50)
MACRO_OFFSET = 50
WINDOW_MIN = 20
HORIZONTE = (20, 40, 60)

# Ueberlappungsfreie Kontrolle. `:40-:00` und `:00-:20` teilen je 10 Minuten mit dem
# Macro-Fenster `:50-:10` -- waere `:50` wirklich besonders, truegen diese beiden einen
# Teil des Effekts mit und wuerden den Kontrast verwaessern. `:10 :20 :30` beruehren
# `:50-:10` nicht.
CLEAN_CTRL = (10, 20, 30)

# Die Stunde 16 faellt raus: `16:50-17:10` ragt ueber den Sessionschluss 17:00 und ist
# damit NIE vollstaendig, waehrend `16:00-16:40` es sind. Bliebe sie drin, fehlte dem
# Macro-Pool eine ganze (und eher ruhige) Stunde, die die Kontrolle hat -- die gepoolte
# Macro-Quote waere allein dadurch zu hoch. Im Probelauf erklaerte genau das die
# Retention-Luecke 92,7 % gegen 96 %.
SKIP_HOURS = (16,)

FX_SYMBOLS = ("AUDUSD", "EURGBP", "EURJPY", "EURUSD", "GBPJPY",
              "GBPUSD", "NZDUSD", "USDCAD", "USDCHF", "USDJPY")


# --------------------------------------------------------------------------- Laden

def fx_path(symbol: str, d: date) -> Path:
    return TIEF_DIR / f"{d:%Y}" / f"{d:%m}" / f"{d:%d.%m.%Y}" / f"{symbol} {d:%Y-%m-%d} 1m (bid).csv"


def mnq_path(symbol: str, d: date) -> Path:
    return DATA_DIR / f"{d:%Y}" / f"{d:%m}" / f"{d:%d.%m.%Y}" / f"{symbol} {d:%Y-%m-%d} 1m.csv"


def session_bars(symbol: str, session_day: date, pathfn) -> list[Bar]:
    """Kerzen eines Handelstags 18:00 (Vorabend) .. 17:00, ueber Dateigrenzen hinweg.

    Noetig, weil die Forex-Dateien KALENDERTAGE (00:00-23:59 NY) sind, die
    Macro-Fenster eines Handelstags aber am Vorabend um 18:50 beginnen -- der liegt in
    der Datei des Vortags. Die MNQ-Dateien sind bereits Session-Dateien; das Verketten
    schadet dort nicht (Duplikate werden ueber den Zeitstempel entfernt).
    """
    bars: dict[datetime, Bar] = {}
    for d in (session_day - timedelta(days=1), session_day):
        p = pathfn(symbol, d)
        if p.exists():
            for b in load(p):
                bars[b.t] = b
    lo, hi = at(session_day - timedelta(days=1), 18), at(session_day, 17)
    return sorted((b for t, b in bars.items() if lo <= t < hi), key=lambda b: b.t)


def session_days(symbol: str, pathfn, root: Path, suffix: str) -> list[date]:
    """Alle Tage, fuer die eine Datei existiert."""
    out = []
    for p in root.rglob(f"{symbol} *-*-* {suffix}"):
        try:
            out.append(datetime.strptime(p.name.split(" ")[1], "%Y-%m-%d").date())
        except (IndexError, ValueError):
            continue
    return sorted(set(out))


# --------------------------------------------------------------------------- Messen

def mfe_norm(bars: list[Bar], start: datetime, medbar: float) -> dict:
    """Groesste Auslenkung ab Fenster-Open, in medbar-Einheiten, richtungsagnostisch.

    None je Horizont, wenn die Minuten nicht lueckenlos vorliegen -- eine halbe
    Kerzenreihe wuerde die Exkursion still nach unten verzerren.
    """
    out = {}
    for n in HORIZONTE:
        seg = window_bars(bars, start, start + timedelta(minutes=n))
        if len(seg) < n:
            out[f"mfe_{n}"] = None
            continue
        o = seg[0].o
        out[f"mfe_{n}"] = max(max(b.h for b in seg) - o, o - min(b.l for b in seg)) / medbar
    return out


def measure_day(symbol: str, session_day: date, bars: list[Bar], k: float) -> list[dict]:
    """Eine Zeile je (Stunde, Offset) fuer einen Handelstag.

    Ein Fenster geht nur ein, wenn alle 20 Minuten vorliegen. Grund: `netto` ist
    `letzte.close - erste.open`; bei Luecken misst es eine kuerzere Spanne und die
    Geradlinigkeit `dir` waere nicht mehr vergleichbar. Die Retention je Offset wird
    mitgezaehlt und im Report ausgewiesen -- unterschiedliche Ausfallquoten zwischen
    den Offsets waeren selbst eine Verzerrung.
    """
    if len(bars) < 60:
        return []
    medbar = statistics.median(b.rng for b in bars)
    if medbar <= 0:
        return []

    by_t = {b.t: b for b in bars}
    rows = []
    stunde = at(session_day - timedelta(days=1), 18)
    for _ in range(N_HOURS):
        if stunde.hour in SKIP_HOURS:
            stunde += timedelta(hours=1)
            continue
        for off in OFFSETS:
            start = stunde + timedelta(minutes=off)
            end = start + timedelta(minutes=WINDOW_MIN)
            win = [by_t[start + timedelta(minutes=i)] for i in range(WINDOW_MIN)
                   if start + timedelta(minutes=i) in by_t]
            if len(win) < WINDOW_MIN:
                rows.append({"symbol": symbol, "session_day": str(session_day),
                             "hour": stunde.hour, "offset": off, "ok": False})
                continue
            m = measure_window(win, DIR_THR, k * medbar)
            rows.append({"symbol": symbol, "session_day": str(session_day),
                         "hour": stunde.hour, "offset": off, "ok": True,
                         "session": SESSION_BY_HOUR[stunde.hour],
                         "dir": m["dir"], "range": m["range"] / medbar,
                         "netto": abs(m["netto"]) / medbar,
                         "expansion": m["expansion"], "start_min": m["start_min"],
                         **mfe_norm(bars, start, medbar)})
        stunde += timedelta(hours=1)
    return rows


# --------------------------------------------------------------------------- Lauf

def run(symbol: str, pathfn, root: Path, suffix: str, k: float,
        limit: int | None = None) -> list[dict]:
    tage = session_days(symbol, pathfn, root, suffix)
    if limit:
        tage = tage[-limit:]
    rows = []
    for d in tage:
        rows.extend(measure_day(symbol, d, session_bars(symbol, d, pathfn), k))
    return rows


def kalibriere_k(rows_mnq_raw: list[tuple[float, float]], netto_thr: float = 30.0) -> float:
    """K so, dass `netto_thr` Punkte im Median dem K-fachen der Median-Kerzenrange
    entsprechen. `rows_mnq_raw` sind (medbar,)-Paare je Handelstag."""
    meds = [m for m, _ in rows_mnq_raw if m > 0]
    return netto_thr / statistics.median(meds) if meds else 6.0


# --------------------------------------------------------------------------- Report

def _stat(rows: list[dict], feld: str):
    vals = [r[feld] for r in rows if r.get(feld) is not None]
    return statistics.median(vals) if vals else None


def report(rows: list[dict], titel: str) -> dict:
    """Offset 50 gegen die fuenf Kontroll-Offsets, gesamt und je Stunde."""
    ok = [r for r in rows if r["ok"]]
    macro = [r for r in ok if r["offset"] == MACRO_OFFSET]
    ctrl = [r for r in ok if r["offset"] != MACRO_OFFSET]

    print(f"\n=== {titel} ===")
    tage = {r["session_day"] for r in rows}
    print(f"{len(rows)} Fenster gerastert, {len(ok)} vollstaendig ({100*len(ok)/max(1,len(rows)):.1f}%), "
          f"{len(tage)} Handelstage")

    print("\nRetention je Offset (Ausfallquoten muessen vergleichbar sein):")
    for off in OFFSETS:
        alle = [r for r in rows if r["offset"] == off]
        gut = sum(1 for r in alle if r["ok"])
        print(f"  :{off:02d}  {100*gut/max(1,len(alle)):5.1f}%  (n={len(alle)})")

    clean = [r for r in ok if r["offset"] in CLEAN_CTRL]
    qm = quote(macro, lambda r: r["expansion"])
    qc = quote(ctrl, lambda r: r["expansion"])
    qcl = quote(clean, lambda r: r["expansion"])
    print(f"\nExpansionsquote:")
    print(f"  Macro  :50               {fmt_quote(qm)}")
    print(f"  Kontrolle alle uebrigen  {fmt_quote(qc)}")
    print(f"  Kontrolle ohne Ueberlapp {fmt_quote(qcl)}   <- schaerferes Mass")
    getrennt = qm["lo"] > qcl["hi"] or qm["hi"] < qcl["lo"]
    print(f"  -> {'UNTERSCHIED (Wilson-Intervalle getrennt)' if getrennt else 'kein Unterschied nachweisbar (Intervalle ueberlappen)'}")

    # Stundenweise stratifiziert: die Stunden haben sehr verschiedene Basisraten (Asia
    # ruhig, London laut). Ein gepoolter Vergleich misst zum Teil die Stundenmischung
    # mit. Der stratifizierte Wert ist das n-gewichtete Mittel der Deltas JE Stunde --
    # dort kann die Mischung nichts mehr beitragen.
    deltas, gew = [], []
    for h in sorted({r["hour"] for r in ok}):
        m = quote([r for r in macro if r["hour"] == h], lambda r: r["expansion"])
        c = quote([r for r in clean if r["hour"] == h], lambda r: r["expansion"])
        if m["genug"] and c["genug"]:
            deltas.append(m["p"] - c["p"])
            gew.append(m["n"])
    strat = sum(d * g for d, g in zip(deltas, gew)) / sum(gew) if gew else None
    if strat is not None:
        pos = sum(1 for d in deltas if d > 0)
        print(f"  stratifiziert ueber {len(deltas)} Stunden: Delta {100*strat:+.2f} pp "
              f"({pos}/{len(deltas)} Stunden mit positivem Delta)")

    print(f"\nMediane (in Median-Kerzenrange-Einheiten):")
    print(f"  {'Offset':8} {'dir':>7} {'range':>8} {'netto':>8} {'mfe_20':>8} {'mfe_60':>8}")
    je_offset = {}
    for off in OFFSETS:
        sel = [r for r in ok if r["offset"] == off]
        je_offset[off] = {f: _stat(sel, f) for f in ("dir", "range", "netto", "mfe_20", "mfe_60")}
        mark = "  <- Macro" if off == MACRO_OFFSET else ""
        v = je_offset[off]
        print(f"  :{off:02d}      " + " ".join(
            f"{v[f]:8.3f}" if v[f] is not None else f"{'-':>8}"
            for f in ("dir", "range", "netto", "mfe_20", "mfe_60")) + mark)

    print(f"\nExpansionsquote je Stunde, Macro :50 gegen ueberlappungsfreie Kontrolle:")
    je_stunde = {}
    for h in sorted({r["hour"] for r in ok}):
        m = quote([r for r in macro if r["hour"] == h], lambda r: r["expansion"])
        c = quote([r for r in clean if r["hour"] == h], lambda r: r["expansion"])
        if not m["genug"] or not c["genug"]:
            continue
        delta = 100 * (m["p"] - c["p"])
        sig = m["lo"] > c["hi"] or m["hi"] < c["lo"]
        je_stunde[h] = {"macro_p": m["p"], "ctrl_p": c["p"], "n": m["n"], "sig": sig}
        print(f"  {h:02d}:50  {SESSION_BY_HOUR[h]:10} Macro {100*m['p']:5.1f}%  "
              f"Kontrolle {100*c['p']:5.1f}%  Delta {delta:+5.1f} pp  n={m['n']:5d}"
              f"{'  ** getrennt' if sig else ''}")

    return {"titel": titel, "n_fenster": len(rows), "n_ok": len(ok), "n_tage": len(tage),
            "macro": {kk: qm[kk] for kk in ("n", "k", "p", "lo", "hi")},
            "kontrolle": {kk: qc[kk] for kk in ("n", "k", "p", "lo", "hi")},
            "kontrolle_clean": {kk: qcl[kk] for kk in ("n", "k", "p", "lo", "hi")},
            "stratifiziert_pp": (100 * strat if strat is not None else None),
            "getrennt": getrennt, "je_offset": je_offset, "je_stunde": je_stunde}


def falte(rows: list[dict]) -> dict:
    """Rohzeilen -> kompakte Zaehler je (Symbol, Stunde, Offset).

    Der Grund ist hart: 10 Paare x 24 Jahre x 22 Stunden x 6 Offsets sind ~10 Mio
    Zeilen. Die alle im Speicher zu halten hat den ersten Hauptlauf zerlegt (OOM-Kill,
    keine Ausgabe). Je Symbol wird daher sofort gefaltet und die Rohliste freigegeben.
    Medianwerte werden hier endguelltig festgehalten -- sie lassen sich aus Zaehlern
    spaeter nicht mehr rekonstruieren.
    """
    agg = defaultdict(list)
    ges = defaultdict(int)
    for r in rows:
        ges[(r["hour"], r["offset"])] += 1
        if r["ok"]:
            agg[(r["hour"], r["offset"])].append(r)
    out = {}
    for (h, off), sel in agg.items():
        out[f"{h}|{off}"] = {
            "hour": h, "offset": off, "n": len(sel), "n_gesamt": ges[(h, off)],
            "k": sum(1 for r in sel if r["expansion"]),
            **{f"med_{f}": _stat(sel, f)
               for f in ("dir", "range", "netto", "mfe_20", "mfe_60")}}
    return out


def schreibe_agg(je_symbol: dict) -> None:
    """Kompakte Aggregat-CSV je (Symbol, Stunde, Offset). Rohzeilen werden bewusst
    nicht geschrieben -- siehe `falte`."""
    AGG_CSV.parent.mkdir(exist_ok=True)
    with AGG_CSV.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["symbol", "hour", "offset", "n", "expansion_rate",
                    "med_dir", "med_range", "med_netto", "med_mfe_20", "med_mfe_60"])
        for sym in sorted(je_symbol):
            for key in sorted(je_symbol[sym], key=lambda s: (int(s.split("|")[0]),
                                                             int(s.split("|")[1]))):
                z = je_symbol[sym][key]
                w.writerow([sym, z["hour"], z["offset"], z["n"],
                            f"{z['k'] / z['n']:.4f}" if z["n"] else "",
                            *(f"{z[f]:.4f}" if z.get(f) is not None else ""
                              for f in ("med_dir", "med_range", "med_netto",
                                        "med_mfe_20", "med_mfe_60"))])
    print(f"\nAggregat -> {AGG_CSV}")


def report_gepoolt(je_symbol: dict, titel: str) -> dict:
    """Gepoolter Bericht allein aus den Zaehlern -- ohne Rohzeilen.

    Deckt Expansionsquote und den stratifizierten Vergleich ab. Mediane werden hier
    NICHT gepoolt (aus Zaehlern nicht rekonstruierbar); sie stehen je Symbol im
    Einzelbericht und in der Aggregat-CSV.
    """
    n_m = k_m = n_c = k_c = 0
    je_h = defaultdict(lambda: [0, 0, 0, 0])       # hour -> [n_m, k_m, n_c, k_c]
    for sym in je_symbol:
        for z in je_symbol[sym].values():
            if z["offset"] == MACRO_OFFSET:
                n_m += z["n"]; k_m += z["k"]
                je_h[z["hour"]][0] += z["n"]; je_h[z["hour"]][1] += z["k"]
            elif z["offset"] in CLEAN_CTRL:
                n_c += z["n"]; k_c += z["k"]
                je_h[z["hour"]][2] += z["n"]; je_h[z["hour"]][3] += z["k"]

    from macro_db import wilson
    lo_m, hi_m = wilson(k_m, n_m)
    lo_c, hi_c = wilson(k_c, n_c)
    p_m, p_c = (k_m / n_m if n_m else 0), (k_c / n_c if n_c else 0)

    print(f"\n=== {titel} ===")
    print(f"  Macro  :50               {100*p_m:.2f}% [{100*lo_m:.2f}-{100*hi_m:.2f}] (n={n_m})")
    print(f"  Kontrolle ohne Ueberlapp {100*p_c:.2f}% [{100*lo_c:.2f}-{100*hi_c:.2f}] (n={n_c})")
    getrennt = lo_m > hi_c or hi_m < lo_c
    print(f"  Delta {100*(p_m-p_c):+.2f} pp -> "
          f"{'UNTERSCHIED (Wilson-Intervalle getrennt)' if getrennt else 'kein Unterschied nachweisbar'}")

    deltas, gew, pos = [], [], 0
    print(f"\n  Je Stunde (Macro vs. Kontrolle ohne Ueberlapp):")
    for h in sorted(je_h):
        nm, km, nc, kc = je_h[h]
        if nm < 20 or nc < 20:
            continue
        pm, pc = km / nm, kc / nc
        lm, hm_ = wilson(km, nm)
        lc, hc = wilson(kc, nc)
        sig = lm > hc or hm_ < lc
        deltas.append(pm - pc); gew.append(nm); pos += (pm > pc)
        print(f"    {h:02d}:50  {SESSION_BY_HOUR[h]:10} Macro {100*pm:5.2f}%  "
              f"Kontrolle {100*pc:5.2f}%  Delta {100*(pm-pc):+5.2f} pp  n={nm:6d}"
              f"{'  ** getrennt' if sig else ''}")
    strat = sum(d * g for d, g in zip(deltas, gew)) / sum(gew) if gew else None
    if strat is not None:
        print(f"\n  stratifiziert ueber {len(deltas)} Stunden: Delta {100*strat:+.2f} pp "
              f"({pos}/{len(deltas)} Stunden positiv)")
    return {"titel": titel, "macro": {"n": n_m, "k": k_m, "p": p_m, "lo": lo_m, "hi": hi_m},
            "kontrolle_clean": {"n": n_c, "k": k_c, "p": p_c, "lo": lo_c, "hi": hi_c},
            "getrennt": getrennt,
            "stratifiziert_pp": (100 * strat if strat is not None else None),
            "stunden_positiv": pos, "stunden_gesamt": len(deltas)}


# --------------------------------------------------------------------------- Selfcheck

def selfcheck() -> None:
    """Konstruierte Kerzen: das :50-Fenster expandiert, die Kontrolle nicht."""
    d = date(2024, 3, 5)
    bars, t = [], at(d - timedelta(days=1), 18)
    px = 100.0
    while t < at(d, 17):
        # Grundrauschen: 1 Punkt Range, kein Netto.
        o = px
        bars.append(Bar(t, o, o + 0.5, o - 0.5, o))
        t += timedelta(minutes=1)
    # In die 09:50-09:59 Kerzen einen glatten Lauf legen.
    idx = {b.t: i for i, b in enumerate(bars)}
    start = at(d, 9, 50)
    for i in range(20):
        j = idx[start + timedelta(minutes=i)]
        o = 100.0 + i * 2.0
        bars[j] = Bar(start + timedelta(minutes=i), o, o + 2.0, o, o + 2.0)

    rows = measure_day("TEST", d, bars, k=3.0)
    macro = [r for r in rows if r["hour"] == 9 and r["offset"] == 50][0]
    assert macro["ok"], "Macro-Fenster muss vollstaendig sein"
    assert macro["expansion"], f"konstruierter Lauf muss Expansion sein: {macro}"
    assert macro["dir"] > 0.9, f"glatter Lauf muss dir ~1 haben, ist {macro['dir']}"

    # Nur Fenster pruefen, die den konstruierten Lauf (09:50-10:10) gar nicht beruehren.
    # Die Offsets :00..:40 derselben und der Folgestunde ueberlappen ihn absichtlich und
    # duerfen expandieren -- genau diese Ueberlappung ist ja die Kontrollgruppe.
    unberuehrt = [r for r in rows if r["ok"]
                  and not (at(d, r["hour"], r["offset"]) < at(d, 10, 10)
                           and at(d, r["hour"], r["offset"]) + timedelta(minutes=20) > at(d, 9, 50))]
    assert unberuehrt, "Testaufbau: es muss unberuehrte Fenster geben"
    assert not any(r["expansion"] for r in unberuehrt), "Grundrauschen darf nicht expandieren"

    # Luecke -> Fenster faellt raus, nicht still verkuerzt gemessen
    ohne = [b for b in bars if b.t != at(d, 11, 55)]
    r11 = [r for r in measure_day("TEST", d, ohne, k=3.0)
           if r["hour"] == 11 and r["offset"] == 50][0]
    assert not r11["ok"], "Fenster mit fehlender Minute muss ausgeschlossen werden"

    # session_bars darf ueber die Dateigrenze hinweg sammeln (hier nur Sortierung/Slice)
    assert bars[0].t == at(d - timedelta(days=1), 18)
    print("backtest_macro_forex selfcheck: OK")


# --------------------------------------------------------------------------- CLI

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbols", nargs="*", default=None)
    ap.add_argument("--all", action="store_true", help="alle 10 FX-Paare")
    ap.add_argument("--mnq", action="store_true", help="nur MNQ")
    ap.add_argument("--limit", type=int, default=None, help="nur die letzten N Tage je Symbol")
    ap.add_argument("--force", action="store_true", help="Zwischenstand ignorieren, neu rechnen")
    ap.add_argument("--selfcheck", action="store_true")
    a = ap.parse_args()

    if a.selfcheck:
        selfcheck()
        return

    # --- K auf MNQ kalibrieren (30 Punkte = wieviel Median-Kerzenrange?)
    mnq_tage = session_days("MNQ", mnq_path, DATA_DIR, "1m.csv")
    meds = []
    for d in mnq_tage:
        b = session_bars("MNQ", d, mnq_path)
        if len(b) >= 60:
            meds.append((statistics.median(x.rng for x in b), 0.0))
    k = kalibriere_k(meds)
    print(f"Kalibrierung auf MNQ: {len(meds)} Handelstage, Median-Kerzenrange "
          f"{statistics.median(m for m, _ in meds):.2f} Pkt -> "
          f"macro_db-Schwelle 30 Pkt entspricht K = {k:.2f} x medbar")

    # Je Symbol: rechnen, berichten, sofort auf Zaehler falten, Rohzeilen freigeben.
    # Der Zwischenstand liegt nach jedem Symbol auf Platte -- ein Abbruch (der erste
    # Hauptlauf starb am Speicher) kostet dann hoechstens das laufende Symbol.
    CACHE.mkdir(parents=True, exist_ok=True)
    zus, je_symbol = [], {}

    aufgaben = []
    if a.mnq or not (a.all or a.symbols):
        aufgaben.append(("MNQ", mnq_path, DATA_DIR, "1m.csv"))
    for s in (FX_SYMBOLS if a.all else (a.symbols or [])):
        aufgaben.append((s, fx_path, TIEF_DIR, "1m (bid).csv"))

    for sym, pathfn, root, suffix in aufgaben:
        cache = CACHE / f"{sym}.json"
        if cache.exists() and not a.force:
            d = json.loads(cache.read_text(encoding="utf-8"))
            je_symbol[sym] = d["zaehler"]
            zus.append(d["bericht"])
            print(f"\n{sym}: aus Zwischenstand uebernommen ({cache.name})")
            continue
        rows = run(sym, pathfn, root, suffix, k, a.limit)
        if not rows:
            print(f"\n{sym}: keine Daten gefunden")
            continue
        titel = f"{sym} (Futures)" if sym == "MNQ" else f"{sym} (FX Spot)"
        b = report(rows, titel)
        z = falte(rows)
        rows = None                      # Speicher sofort freigeben
        je_symbol[sym], _ = z, zus.append(b)
        cache.write_text(json.dumps({"bericht": b, "zaehler": z}, indent=2, default=str),
                         encoding="utf-8")

    fx_teil = {s: z for s, z in je_symbol.items() if s in FX_SYMBOLS}
    if len(fx_teil) > 1:
        zus.append(report_gepoolt(fx_teil, "ALLE FX-PAARE GEPOOLT"))

    if je_symbol:
        schreibe_agg(je_symbol)
        RESULT.parent.mkdir(exist_ok=True)
        RESULT.write_text(json.dumps({"k": k, "berichte": zus}, indent=2, default=str),
                          encoding="utf-8")
        print(f"Zusammenfassung -> {RESULT}")


if __name__ == "__main__":
    main()
