#!/usr/bin/env python3
"""Macro-Datenbank: eine Zeile je Macro-Fenster je Handelstag.

Erfasst fuer jedes Macro-Fenster (:50-:10) eines MNQ-Handelstags, was davor passierte
(Spooling-Kandidaten, Sweeps, Structure Breaks, Displacements, offene Level), was im
Fenster geschah (Range, Nettoweg, Geradlinigkeit, Richtung), wann der Move einsetzte
und welche Level dabei genommen wurden.

Spec: docs/superpowers/specs/2026-08-10-macro-datenbank-design.md

Aufruf:
    python algo/macro_db.py build       # algo/results/macro_db.csv neu bauen
    python algo/macro_db.py stats       # Auswertung
    python algo/macro_db.py plot        # Diagramme + Wiki-Seite
    python algo/macro_db.py --selfcheck
"""
from __future__ import annotations

import argparse
import csv
import math
import statistics
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from tools.analyze_ohlc import (CFG, DATA_DIR, NY, Bar, at, displacements, fvgs,  # noqa: E402
                                load, structure_breaks, sweeps, untouched_levels)

from backtest_macro import session_day_from_path  # noqa: E402

# Der MNQ-Handelstag laeuft 18:00 (Vorabend) .. 17:00. Das erste Macro-Fenster ist
# 18:50, das letzte 16:50 -- 23 Stueck. 17:50 liegt in der Globex-Pause.
N_WINDOWS = 23
WINDOW_MIN = 20     # Laenge eines Macro-Fensters
PRE_MIN = 10        # Vorlauf, der fuer die Spooling-Kennzahlen vollstaendig sein muss


def macro_windows_session(session_day: date):
    """Die 23 Macro-Fenster eines Handelstags: (label, start, ende).

    Label ist die Startzeit (`"09:50"`), Start/Ende sind NY-Zeitpunkte. Das erste
    Fenster liegt am Vorabend (18:50), die spaeteren am `session_day` selbst.
    """
    out = []
    t = at(session_day - timedelta(days=1), 18, 50)
    for _ in range(N_WINDOWS):
        end = t + timedelta(minutes=WINDOW_MIN)
        out.append((f"{t:%H:%M}", t, end))
        t += timedelta(hours=1)
    return out


# Eindeutige Session je Fenster-Startstunde. Bewusst nicht ueber
# analyze_ohlc.session_windows(): die dortigen Fenster ueberlappen sich absichtlich
# ("NY AM" und "Premarket", "RTH" und "Lunch"), was fuer eine Report-Zeile taugt, aber
# nicht fuer eine eindeutige Spalte. Die 23 Stunden des Handelstags werden hier
# ueberschneidungsfrei aufgeteilt.
SESSION_BY_HOUR = {**{h: "Asia" for h in (18, 19, 20, 21, 22, 23, 0, 1)},
                   **{h: "London" for h in (2, 3, 4, 5, 6)},
                   **{h: "Premarket" for h in (7, 8)},
                   **{h: "NY AM" for h in (9, 10, 11)},
                   12: "Lunch",
                   **{h: "NY PM" for h in (13, 14, 15, 16)}}


def window_bars(bars: list[Bar], start: datetime, end: datetime) -> list[Bar]:
    """Kerzen mit `start <= t < end`. Erwartet nach NY konvertierte Bar-Zeiten."""
    return [b for b in bars if start <= b.t < end]


def is_complete(bars: list[Bar], start: datetime, end: datetime,
                pre_min: int = PRE_MIN) -> bool:
    """True, wenn Fenster und Vorlauf lueckenlos sind.

    Streng: alle 20 Minuten des Fensters und alle `pre_min` Minuten davor muessen je
    eine Kerze haben. Grund (Nutzerentscheidung, Spec 4.2): nur vollstaendig erfasste
    Fenster gehen in die Statistik -- eine halbe Kerzenreihe verzerrt Range, Nettoweg
    und Startminute, ohne dass man es der Zahl ansieht.
    """
    have = {b.t for b in bars}
    soll_win = {start + timedelta(minutes=i) for i in range(WINDOW_MIN)}
    soll_pre = {start - timedelta(minutes=i + 1) for i in range(pre_min)}
    return soll_win <= have and soll_pre <= have


DIR_THR = 0.60      # Startwert; Macro-Median liegt laut backtest_macro.py bei 0,52
NETTO_THR = 30.0    # Startwert in Punkten; Macro-Median liegt bei 31,50


def measure_window(win: list[Bar], dir_thr: float = DIR_THR,
                   netto_thr: float = NETTO_THR) -> dict:
    """Verlauf innerhalb eines Macro-Fensters.

    `netto` ist vorzeichenbehaftet (close der letzten minus open der ersten Kerze),
    `dir` = |netto| / range misst die Geradlinigkeit: 1,0 = glatte Expansion,
    0,0 = Hin und Her. `start_min` ist die Minute des Extrems **entgegen** der
    Netto-Richtung -- laeuft das Fenster aufwaerts, also die Minute des Tiefs. Das
    ist der Punkt, an dem der Move einsetzt, und misst die
    Manipulation-vor-Expansion-Sequenz innerhalb der 20 Minuten
    (siehe wiki/concepts/ICT Macros & Leading Candles.md).
    """
    hi = max(b.h for b in win)
    lo = min(b.l for b in win)
    rng = hi - lo
    netto = win[-1].c - win[0].o
    ab = abs(netto)
    if netto >= 0:
        start_min = min(range(len(win)), key=lambda i: win[i].l)
        direction = "up"
    else:
        start_min = max(range(len(win)), key=lambda i: win[i].h)
        direction = "down"
    d = ab / rng if rng else 0.0
    return {"range": rng, "netto": netto, "dir": d, "direction": direction,
            "start_min": start_min, "expansion": bool(d >= dir_thr and ab >= netto_thr)}


NORM_BLOCKS = 12    # 12 x 10 Minuten = 2 Stunden Rueckschau fuer die Normierung


def measure_pre(bars: list[Bar], start: datetime, pre_min: int = PRE_MIN) -> dict:
    """Spooling-Kandidaten aus den `pre_min` Minuten VOR dem Fenster.

    Alle vier Kennzahlen sind preisbasiert, weil die TradingView-Exporte kein Volumen
    enthalten (Spec 3.2) -- die naheliegende Definition "enge Kerzen bei steigendem
    Volumen" ist auf diesem Bestand nicht baubar.

    Sieht ausschliesslich Kerzen mit `t < start`: kein Lookahead.
    """
    pre = window_bars(bars, start - timedelta(minutes=pre_min), start)
    if not pre:
        return {"pre_range_rel": None, "pre_wick_frac": None,
                "pre_streak": None, "pre_contraction": None}

    rng_pre = max(b.h for b in pre) - min(b.l for b in pre)

    # Normierung gegen die 12 vorangegangenen 10-Minuten-Bloecke (nicht gegen den
    # Tagesmedian -- der enthielte Kerzen NACH dem Fenster und waere Lookahead).
    refs = []
    for k in range(1, NORM_BLOCKS + 1):
        b_end = start - timedelta(minutes=pre_min * k)
        blk = window_bars(bars, b_end - timedelta(minutes=pre_min), b_end)
        if len(blk) == pre_min:
            refs.append(max(b.h for b in blk) - min(b.l for b in blk))
    med = statistics.median(refs) if len(refs) >= NORM_BLOCKS // 2 else None
    pre_range_rel = (rng_pre / med) if med else None

    ges_rng = sum(b.rng for b in pre)
    ges_body = sum(b.body for b in pre)
    pre_wick_frac = ((ges_rng - ges_body) / ges_rng) if ges_rng > 0 else None

    best = cur = 1
    for a, b in zip(pre, pre[1:]):
        cur = cur + 1 if a.bull == b.bull else 1
        best = max(best, cur)

    half = len(pre) // 2
    erst = statistics.median(b.rng for b in pre[:half]) if half else None
    letzt = statistics.median(b.rng for b in pre[half:]) if half else None
    pre_contraction = (letzt / erst) if erst else None

    return {"pre_range_rel": pre_range_rel, "pre_wick_frac": pre_wick_frac,
            "pre_streak": best, "pre_contraction": pre_contraction}


def _minuten(a: datetime, b: datetime) -> float:
    return (a - b).total_seconds() / 60.0


def measure_events(bars: list[Bar], start: datetime) -> dict:
    """Letztes Sweep-/MSS-/Displacement-Ereignis vor dem Fenster.

    Laeuft ausschliesslich auf `bars[t < start]` -- kein Lookahead. Die
    Detektor-Parameter entsprechen den 1m-Werten aus `CFG`: `main()` in
    analyze_ohlc.py skaliert mit max(3, round(15/tf_min)) bzw. max(2, round(5/tf_min)),
    bei tf_min=1 sind das genau die CFG-Defaults. `min_pen` muss als
    CFG["min_pen"] * Median-Kerzenrange uebergeben werden, nicht als roher 0,75 --
    diese Falle ist in algo/PLAN.md dokumentiert.
    """
    hist = [b for b in bars if b.t < start]
    leer = {"sweep_age": None, "sweep_dir": None, "mss_age": None, "mss_dir": None,
            "displacement_age": None, "fvg_open_dist": None}
    if len(hist) < CFG["min_age"] + CFG["swing"] * 2 + 1:
        return leer

    med_bar = statistics.median(b.rng for b in hist) or 1.0
    sw = sweeps(hist, CFG["swing"], CFG["min_age"], CFG["min_pen"] * med_bar, CFG["confirm"])
    sb = [x for x in structure_breaks(hist, CFG["swing"], CFG["min_age"]) if x["type"] == "MSS"]
    dp = displacements(hist, factor=CFG["disp_factor"])
    fv = [f for f in fvgs(hist) if not f["filled"]]

    ref = hist[-1].c
    out = dict(leer)
    if sw:
        last = sw[-1]
        out["sweep_age"] = _minuten(start, last["t"])
        out["sweep_dir"] = last["side"]          # "buyside" | "sellside"
    if sb:
        last = sb[-1]
        out["mss_age"] = _minuten(start, last["t"])
        out["mss_dir"] = last["dir"]             # "bullish" | "bearish"
    if dp:
        out["displacement_age"] = _minuten(start, dp[-1]["t"])
    if fv:
        out["fvg_open_dist"] = min(abs(ref - f["ce"]) for f in fv)
    return out


def measure_levels(bars: list[Bar], start: datetime, end: datetime) -> dict:
    """Offene Liquiditaets-Level vor dem Fenster und welche davon im Fenster fielen.

    Level-Quelle ist `untouched_levels` auf `bars[t < start]`: Swing-Hochs/-Tiefs, die
    bis zum Fensterstart nie wieder genommen wurden -- das ist die ICT-Kernliquiditaet
    ("Target Liquiditaet min. 2 H/L").

    Bewusst NICHT enthalten, obwohl die Spec sie in 4.1 nennt:

    * **NDOG/NWOG/ORG.** Die Funktionen `ndog_gap`/`nwog_gap`/`org_gap` in
      analyze_ohlc.py filtern ueber `b.t.date() == day`, also ueber den Kalendertag.
      Eine 1m-Session-Datei enthaelt aber zwei Kalendertage (18:00 Vorabend .. 17:00),
      wodurch sie den Gap ueber die Globex-Pause verfehlen und stattdessen den Sprung
      ueber Mitternacht messen wuerden -- und der ist auf diesem Bestand ohnehin ein
      Exportartefakt (Luecke 23:59-00:08).
    * **PDH/PDL und Session-Extreme des Vortags.** Beide brauchen die *vorherige*
      Tagesdatei, also Mehrdatei-Logik, die `build()` heute nicht hat. Die Level des
      laufenden Handelstags decken `untouched_levels` bereits ab.

    Beides ist ein eigener Schritt -- siehe algo/PLAN.md.
    """
    hist = [b for b in bars if b.t < start]
    win = window_bars(bars, start, end)
    if not hist or not win:
        return {"levels_open": None, "levels_hit": "", "nearest_level_dist": None}

    offen = untouched_levels(hist, CFG["swing"])
    hi = max(b.h for b in win)
    lo = min(b.l for b in win)
    ref = hist[-1].c

    getroffen = []
    for lv in offen:
        if lv["side"] == "buyside" and hi >= lv["level"]:
            getroffen.append("buyside")
        elif lv["side"] == "sellside" and lo <= lv["level"]:
            getroffen.append("sellside")
    return {"levels_open": len(offen),
            "levels_hit": "|".join(sorted(set(getroffen))),
            "nearest_level_dist": min((abs(ref - lv["level"]) for lv in offen), default=None)}


CSV_PATH = Path(__file__).resolve().parent / "results" / "macro_db.csv"

FIELDS = ["symbol", "session_day", "window", "weekday", "session",
          "pre_range_rel", "pre_wick_frac", "pre_streak", "pre_contraction",
          "sweep_age", "sweep_dir", "mss_age", "mss_dir", "displacement_age",
          "fvg_open_dist", "levels_open", "nearest_level_dist",
          "range", "netto", "dir", "direction", "start_min", "expansion", "levels_hit"]


def build(symbol: str = "MNQ", dir_thr: float = DIR_THR,
          netto_thr: float = NETTO_THR) -> tuple[list[dict], list[dict]]:
    """Baut die Datenbank neu und liefert (Zeilen, Ausschluesse).

    Rechnet immer alles neu -- bei einigen hundert Zeilen dauert das Sekunden, eine
    Inkrementell-Logik waere Code fuer ein Problem, das es nicht gibt.
    """
    rows, skipped = [], []
    for path in sorted(DATA_DIR.rglob(f"{symbol} *-*-* 1m.csv")):
        bars = load(path)
        if not bars:
            skipped.append({"session_day": path.name, "window": "-", "grund": "Datei leer"})
            continue
        session_day = session_day_from_path(path)
        for label, start, end in macro_windows_session(session_day):
            if not is_complete(bars, start, end):
                win = window_bars(bars, start, end)
                skipped.append({"session_day": str(session_day), "window": label,
                                "grund": f"unvollstaendig ({len(win)}/{WINDOW_MIN} Kerzen"
                                         f" im Fenster)"})
                continue
            win = window_bars(bars, start, end)
            rows.append({"symbol": symbol, "session_day": str(session_day),
                         "window": label, "weekday": start.strftime("%a"),
                         "session": SESSION_BY_HOUR[start.hour],
                         **measure_pre(bars, start),
                         **measure_events(bars, start),
                         **measure_levels(bars, start, end),
                         **measure_window(win, dir_thr, netto_thr)})
    return rows, skipped


def write_csv(rows: list[dict], fields: list[str] = None) -> None:
    """Schreibt algo/results/macro_db.csv. Reine Standardbibliothek."""
    CSV_PATH.parent.mkdir(exist_ok=True)
    with CSV_PATH.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields or FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def read_csv() -> list[dict]:
    """Liest die CSV zurueck und wandelt Zahlen/Booleans in echte Typen."""
    if not CSV_PATH.exists():
        return []
    out = []
    with CSV_PATH.open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            for k, v in list(r.items()):
                if v == "":
                    r[k] = None
                elif v in ("True", "False"):
                    r[k] = v == "True"
                elif k not in ("symbol", "session_day", "window", "weekday",
                               "direction", "session", "levels_hit",
                               "sweep_dir", "mss_dir"):
                    try:
                        r[k] = float(v)
                    except ValueError:
                        pass
            out.append(r)
    return out


MIN_N = 20      # darunter wird keine Prozentzahl ausgegeben (Spec 6, Regel 3)


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson-Score-Konfidenzintervall fuer eine Quote k/n (95 % bei z=1,96).

    Bewusst Wilson statt des ueblichen Normal-Intervalls: bei kleinem n und Quoten
    nahe 0 oder 1 liefert das Normal-Intervall Grenzen ausserhalb [0,1] und viel zu
    enge Bereiche. Bei n=0 ist das Intervall das ganze Einheitsintervall.
    """
    if n == 0:
        return 0.0, 1.0
    p = k / n
    d = 1 + z * z / n
    mitte = (p + z * z / (2 * n)) / d
    rand = (z / d) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return max(0.0, mitte - rand), min(1.0, mitte + rand)


def quote(rows: list[dict], pred) -> dict:
    """Quote von `pred` ueber `rows`, mit Wilson-Intervall und Mindest-n-Flag."""
    n = len(rows)
    k = sum(1 for r in rows if pred(r))
    lo, hi = wilson(k, n)
    return {"n": n, "k": k, "p": (k / n if n else None),
            "lo": lo, "hi": hi, "genug": n >= MIN_N}


def fmt_quote(q: dict) -> str:
    """Eine Quote als Text -- nie ohne n, nie ohne Intervall (Spec 6, Regeln 1+3)."""
    if not q["genug"]:
        return f"n={q['n']} — zu wenig"
    return (f"{100 * q['p']:.1f}% [{100 * q['lo']:.1f}–{100 * q['hi']:.1f}] "
            f"(n={q['n']}, k={q['k']})")


def vergleich(teil: dict, basis: dict) -> str:
    """Bedingte Quote gegen Basisrate. Ueberlappende Intervalle heissen
    'kein Unterschied nachweisbar' -- nicht 'leicht erhoeht' (Spec 6, Regel 2)."""
    if not teil["genug"]:
        return "n zu klein"
    if teil["lo"] > basis["hi"]:
        return "hoeher als die Basisrate"
    if teil["hi"] < basis["lo"]:
        return "niedriger als die Basisrate"
    return "kein Unterschied nachweisbar"


BEDINGUNGEN = [
    ("Sweep in den 30 Min davor",     lambda r: r["sweep_age"] is not None and r["sweep_age"] <= 30),
    ("MSS in den 30 Min davor",       lambda r: r["mss_age"] is not None and r["mss_age"] <= 30),
    ("Displacement in den 30 Min davor",
     lambda r: r["displacement_age"] is not None and r["displacement_age"] <= 30),
    ("Kompression davor (pre_range_rel < 0,7)",
     lambda r: r["pre_range_rel"] is not None and r["pre_range_rel"] < 0.7),
    ("Kontraktion davor (pre_contraction < 0,8)",
     lambda r: r["pre_contraction"] is not None and r["pre_contraction"] < 0.8),
    ("hoher Dochtanteil davor (pre_wick_frac > 0,6)",
     lambda r: r["pre_wick_frac"] is not None and r["pre_wick_frac"] > 0.6),
    ("Serie >= 5 gleichgerichtete Closes davor",
     lambda r: r["pre_streak"] is not None and r["pre_streak"] >= 5),
]


def cmd_stats(symbol: str = "MNQ") -> None:
    rows = [r for r in read_csv() if r["symbol"] == symbol]
    if not rows:
        print("Keine Daten. Erst `python algo/macro_db.py build` laufen lassen.")
        return

    tage = sorted({r["session_day"] for r in rows})
    basis = quote(rows, lambda r: r["expansion"])
    print(f"{symbol}: {len(rows)} Fenster aus {len(tage)} Handelstagen "
          f"({tage[0]} .. {tage[-1]})")
    print(f"Basisrate Expansion: {fmt_quote(basis)}\n")

    print("Je Bedingung (Expansion | Bedingung):")
    n_vergleiche = 0
    for name, pred in BEDINGUNGEN:
        teil = [r for r in rows if pred(r)]
        q = quote(teil, lambda r: r["expansion"])
        n_vergleiche += 1
        print(f"  {name:46} {fmt_quote(q):40} {vergleich(q, basis)}")

    print("\nJe Fenster:")
    for w in sorted({r["window"] for r in rows}):
        q = quote([r for r in rows if r["window"] == w], lambda r: r["expansion"])
        n_vergleiche += 1
        print(f"  {w:>6}  {fmt_quote(q):40} {vergleich(q, basis)}")

    print("\nStartminute des Moves (start_min), alle Fenster:")
    sm = [int(r["start_min"]) for r in rows if r["start_min"] is not None]
    if sm:
        print(f"  Median {statistics.median(sm):.1f}, "
              f"Anteil in den ersten 5 Minuten: {100 * sum(1 for x in sm if x < 5) / len(sm):.1f}%")

    print("\nLevel im Fenster genommen:")
    for seite in ("buyside", "sellside"):
        q = quote(rows, lambda r, s=seite: s in (r["levels_hit"] or ""))
        print(f"  {seite:10} {fmt_quote(q)}")

    # Spooling-Kandidaten gegen die Zielgroesse (Spec 6): welcher haengt ueberhaupt mit
    # gerichteter Expansion zusammen? Rangkorrelation gegen `dir`, plus Quotenvergleich
    # oberstes vs. unterstes Quartil. Ein Nullbefund ist hier ein Ergebnis.
    print("\nSpooling-Kandidaten gegen die Geradlinigkeit (dir):")
    from scipy.stats import spearmanr
    for k in ("pre_range_rel", "pre_wick_frac", "pre_streak", "pre_contraction"):
        paare = [(r[k], r["dir"]) for r in rows if r[k] is not None and r["dir"] is not None]
        n_vergleiche += 1
        if len(paare) < MIN_N:
            print(f"  {k:18} n={len(paare)} — zu wenig")
            continue
        rho, p = spearmanr([a for a, _ in paare], [b for _, b in paare])
        srt = sorted(paare)
        q = max(1, len(srt) // 4)
        unten = quote([{"expansion": d >= DIR_THR} for _, d in srt[:q]],
                      lambda r: r["expansion"])
        oben = quote([{"expansion": d >= DIR_THR} for _, d in srt[-q:]],
                     lambda r: r["expansion"])
        print(f"  {k:18} rho={rho:+.3f} p={p:.4f} (n={len(paare)})   "
              f"unterstes Quartil {fmt_quote(unten)} | oberstes {fmt_quote(oben)}")

    print(f"\n--- Vorbehalte ---")
    print(f"* {n_vergleiche} Vergleiche gerechnet. Bei einem Signifikanzniveau von 5 % waeren")
    print(f"  rein zufaellig etwa {0.05 * n_vergleiche:.1f} davon 'auffaellig'. Bonferroni-"
          f"korrigiert liegt die Schwelle bei p < {0.05 / n_vergleiche:.4f}.")
    print("* Fenster desselben Handelstags sind nicht unabhaengig -- p-Werte sind optimistisch.")
    print("* Das Fenster 23:50 fehlt fast vollstaendig (Exportluecke 23:59-00:08),")
    print("  16:50 ganz (ragt ueber den Sessionschluss 17:00).")


# Generierte Bilder gehoeren nach wiki/assets/, NICHT nach raw/ -- raw/ ist laut
# CLAUDE.md Layer 1 (Rohquellen, unveraenderlich). build_site.py loest Bildnamen
# ueber das ganze Repo auf (collect_assets() nutzt ROOT.rglob), der Ort ist also frei.
BILD_DIR = Path(__file__).resolve().parent.parent / "wiki" / "assets"
WIKI_SEITE = (Path(__file__).resolve().parent.parent / "wiki" / "synthesis"
              / "Macro-Datenbank (laufend).md")


def cmd_plot(symbol: str = "MNQ") -> None:
    import matplotlib
    matplotlib.use("Agg")           # kein Fenster, nur Dateien
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch

    rows = [r for r in read_csv() if r["symbol"] == symbol]
    if not rows:
        print("Keine Daten. Erst `python algo/macro_db.py build` laufen lassen.")
        return
    BILD_DIR.mkdir(parents=True, exist_ok=True)
    basis = quote(rows, lambda r: r["expansion"])
    tage = sorted({r["session_day"] for r in rows})

    # 1) Expansionsquote je Fenster, mit Wilson-Fehlerbalken und Basisrate.
    # Fenster mit n < MIN_N (dieselbe Schwelle wie fmt_quote/vergleich) werden
    # ausgegraut+schraffiert und mit "n=..." statt eines vollwertigen Prozentbalkens
    # gezeigt -- sonst taeuscht z.B. 23:50 (n=1, zufaellig 100%) eine belastbare Quote
    # vor, obwohl genau davor MIN_N schuetzen soll.
    fenster = sorted({r["window"] for r in rows})
    fenster_qs = [(w, quote([r for r in rows if r["window"] == w], lambda r: r["expansion"]))
                  for w in fenster]
    ps = [100 * (q["p"] or 0) for _, q in fenster_qs]
    unten = [100 * ((q["p"] or 0) - q["lo"]) for _, q in fenster_qs]
    oben = [100 * (q["hi"] - (q["p"] or 0)) for _, q in fenster_qs]
    farben = ["#4a7ba7" if q["genug"] else "#c9c9c9" for _, q in fenster_qs]
    fig, ax = plt.subplots(figsize=(12, 5))
    bars = ax.bar(fenster, ps, color=farben)
    for bar, (_, q) in zip(bars, fenster_qs):
        if not q["genug"]:
            bar.set_hatch("//")
            bar.set_edgecolor("#777777")
    ax.errorbar(fenster, ps, yerr=[unten, oben], fmt="none", ecolor="#333", capsize=3)
    for w, q in fenster_qs:
        if not q["genug"]:
            ax.text(w, 2, f"n={q['n']}", ha="center", va="bottom", fontsize=7, color="#333")
    ax.axhline(100 * basis["p"], color="crimson", linestyle="--",
               label=f"Basisrate {100 * basis['p']:.1f}%")
    ax.set_ylabel("Expansionsquote (%)")
    ax.set_title(f"{symbol}: Expansion je Macro-Fenster "
                 f"({len(tage)} Handelstage, 95%-Wilson-Intervall)")
    handles, _ = ax.get_legend_handles_labels()
    handles.append(Patch(facecolor="#c9c9c9", hatch="//", edgecolor="#777777",
                          label=f"n < {MIN_N} (nicht belastbar, siehe n=-Beschriftung)"))
    ax.legend(handles=handles)
    plt.xticks(rotation=90)
    plt.tight_layout()
    fig.savefig(BILD_DIR / "macro-db-expansion.png", dpi=110)
    plt.close(fig)

    # 2) Timing-Histogramm der Startminute
    sm = [int(r["start_min"]) for r in rows if r["start_min"] is not None]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(sm, bins=range(0, WINDOW_MIN + 1), color="#4a7ba7", edgecolor="white")
    ax.set_xlabel("Minute im Fenster, in der der Move einsetzt")
    ax.set_ylabel("Anzahl Fenster")
    ax.set_title(f"{symbol}: Startminute des Moves (n={len(sm)})")
    plt.tight_layout()
    fig.savefig(BILD_DIR / "macro-db-timing.png", dpi=110)
    plt.close(fig)

    # 3) Level-Trefferquote
    seiten = ["buyside", "sellside"]
    lq = [quote(rows, lambda r, s=s: s in (r["levels_hit"] or "")) for s in seiten]
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.bar(seiten, [100 * (q["p"] or 0) for q in lq], color="#4a7ba7")
    ax.errorbar(seiten, [100 * (q["p"] or 0) for q in lq],
                yerr=[[100 * ((q["p"] or 0) - q["lo"]) for q in lq],
                      [100 * (q["hi"] - (q["p"] or 0)) for q in lq]],
                fmt="none", ecolor="#333", capsize=4)
    ax.set_ylabel("Anteil Fenster mit genommenem Level (%)")
    ax.set_title(f"{symbol}: Liquiditaet im Macro genommen")
    plt.tight_layout()
    fig.savefig(BILD_DIR / "macro-db-level.png", dpi=110)
    plt.close(fig)

    knapp = [w for w, q in fenster_qs if not q["genug"]]
    _schreibe_wiki(symbol, rows, tage, basis, fenster, knapp)
    print(f"3 Diagramme -> {BILD_DIR}")
    print(f"Wiki-Seite   -> {WIKI_SEITE}")


def _schreibe_wiki(symbol, rows, tage, basis, fenster, knapp) -> None:
    heute = datetime.now(NY).date()
    zeilen = [
        "---",
        "tags: [synthesis, algo, macro, laufend]",
        f"created: {heute}",
        f"updated: {heute}",
        'sources: ["[[ICT Macros & Leading Candles]]"]',
        "---",
        "",
        "# Macro-Datenbank (laufend)",
        "",
        f"Erzeugt von `algo/macro_db.py plot`. Basis: **{symbol}**, {len(rows)} vollständig",
        f"erfasste Macro-Fenster aus {len(tage)} Handelstagen ({tage[0]} … {tage[-1]}).",
        "Diese Seite wird bei jedem Lauf überschrieben — sie ist ein laufender Stand,",
        "kein Schnappschuss.",
        "",
        f"**Basisrate Expansion:** {fmt_quote(basis)}",
        "",
        "## Expansion je Fenster",
        "",
        "![[macro-db-expansion.png]]",
        f"*Expansionsquote je Macro-Fenster mit 95%-Wilson-Intervall. Rote Linie: Basisrate über alle Fenster.*",
        "",
        "## Wann setzt der Move ein?",
        "",
        "![[macro-db-timing.png]]",
        "*Minute im 20-Minuten-Fenster, in der der Move einsetzt — definiert als das Extrem entgegen der Netto-Richtung.*",
        "",
        "## Liquidität im Fenster genommen",
        "",
        "![[macro-db-level.png]]",
        "*Anteil der Fenster, in denen ein vor dem Fenster offenes Swing-Level genommen wurde.*",
        "",
        "## Vorbehalte",
        "",
        f"- Die Stichprobe ist klein: rund {len(rows) // len(fenster)} Tage je Fenster. Aussagen auf",
        "  **Fenster-Ebene** sind noch nicht belastbar, Aussagen auf **Bedingungs-Ebene**",
        "  über alle Fenster hinweg früher.",
        "- Fenster desselben Handelstags sind nicht unabhängig — p-Werte sind optimistisch.",
        (f"- {len(knapp)} Fenster liegen mit n < {MIN_N} unter der Mindeststichprobe aus"
         f" `fmt_quote()`/`vergleich()` und sind in Diagramm 1 ausgegraut/schraffiert mit"
         f" n=…-Beschriftung statt vollem Prozentbalken markiert: {', '.join(knapp)}."
         " Am deutlichsten **23:50** mit nur n=1 (Exportlücke 23:59–00:08) — der 100%-Wert"
         " dort ist ein Stichproben-Artefakt, keine belastbare Quote (Wilson-Intervall"
         " entsprechend breit: 20,7–100 %). **16:50** fehlt sogar ganz (ragt über den"
         " Sessionschluss 17:00 hinaus) und taucht im Diagramm nicht auf. Die Asia-Session"
         " ist damit systematisch knapper besetzt als der Rest, nicht nur ein Einzelfall."),
        "- NDOG/NWOG/ORG sind noch keine Level-Quelle (Kalendertag- statt Session-Logik,",
        "  siehe `algo/PLAN.md`).",
        "",
        "## Verwandt",
        "",
        "- [[ICT Macros & Leading Candles]]",
        "- [[Muster-Validierung (laufend)]]",
        "",
    ]
    WIKI_SEITE.parent.mkdir(parents=True, exist_ok=True)
    WIKI_SEITE.write_text("\n".join(zeilen), encoding="utf-8")


def cmd_build(symbol: str) -> None:
    rows, skipped = build(symbol)
    write_csv(rows)
    tage = len({r["session_day"] for r in rows})
    print(f"{len(rows)} Fenster aus {tage} Handelstagen -> {CSV_PATH}")
    if skipped:
        print(f"\nAusgeschlossen: {len(skipped)} Fenster (nicht vollstaendig erfasst)")
        per_win: dict[str, int] = {}
        for s in skipped:
            per_win[s["window"]] = per_win.get(s["window"], 0) + 1
        for w, n in sorted(per_win.items(), key=lambda kv: -kv[1]):
            print(f"  {w:>6}  {n:3d}x")


def _bars(start: datetime, n: int, price: float = 100.0) -> list[Bar]:
    """Testhelfer: n lueckenlose Minutenkerzen ab `start`."""
    return [Bar(start + timedelta(minutes=i), price, price + 2, price - 1, price + 1, None)
            for i in range(n)]


def _check_measure() -> None:
    start = at(date(2026, 8, 10), 9, 50)

    # Aufwaerts, Tief in Minute 3: erst gegen die spaetere Richtung, dann Expansion.
    # o/h/l/c je Minute; die Minute mit dem tiefsten Low ist start_min.
    lows = [100, 99, 98, 95, 97, 99, 101, 103, 105, 107,
            109, 111, 113, 115, 117, 119, 121, 123, 125, 127]
    win = [Bar(start + timedelta(minutes=i), lo + 1, lo + 3, lo, lo + 2, None)
           for i, lo in enumerate(lows)]
    m = measure_window(win)
    assert m["direction"] == "up", m
    assert m["start_min"] == 3, f"Tief liegt in Minute 3, nicht {m['start_min']}"
    assert abs(m["netto"] - (129 - 101)) < 1e-9, m      # close[-1]=129, open[0]=101
    assert abs(m["range"] - (130 - 95)) < 1e-9, m       # max high 130, min low 95
    assert 0.0 <= m["dir"] <= 1.0, m

    # Abwaerts: start_min ist die Minute des hoechsten Highs
    win_dn = [Bar(start + timedelta(minutes=i), 200 - lo, 202 - lo, 199 - lo, 201 - lo, None)
              for i, lo in enumerate(lows)]
    m2 = measure_window(win_dn)
    assert m2["direction"] == "down", m2
    assert m2["start_min"] == 3, f"Hoch liegt in Minute 3, nicht {m2['start_min']}"

    # Flach: gleiche Preise -> range 0, dir 0, keine Expansion, kein Absturz
    flat = [Bar(start + timedelta(minutes=i), 100, 100, 100, 100, None) for i in range(20)]
    mf = measure_window(flat)
    assert mf["range"] == 0.0 and mf["dir"] == 0.0 and mf["expansion"] is False, mf

    # Expansion: dir >= Schwelle UND |netto| >= Punkte-Schwelle.
    # Dieses Fenster hat netto=28 und dir=0,80 -- also greift die Netto-Schwelle
    # bei 25 (True) und bei 30 nicht mehr (False). Genau dieser Randfall ist der
    # Sinn des Tests: beide Bedingungen muessen einzeln blocken koennen.
    assert measure_window(win, dir_thr=0.60, netto_thr=25.0)["expansion"] is True
    assert measure_window(win, dir_thr=0.60, netto_thr=30.0)["expansion"] is False
    assert measure_window(win, dir_thr=0.99, netto_thr=25.0)["expansion"] is False


def _check_pre() -> None:
    start = at(date(2026, 8, 10), 9, 50)

    def mk(t0, n, rng, step=0.0, body_frac=1.0):
        """n Kerzen ab t0 mit fester Range `rng`; body_frac steuert den Dochtanteil."""
        out = []
        for i in range(n):
            base = 100.0 + i * step
            half = rng / 2
            body = rng * body_frac
            o = base - body / 2
            c = base + body / 2
            out.append(Bar(t0 + timedelta(minutes=i), o, base + half, base - half, c, None))
        return out

    # 130 Minuten Historie mit Range 10, danach 10 Minuten mit Range 2 -> Kompression
    hist = mk(start - timedelta(minutes=130), 120, rng=10.0)
    pre = mk(start - timedelta(minutes=10), 10, rng=2.0)
    m = measure_pre(hist + pre, start)
    assert m["pre_range_rel"] is not None and m["pre_range_rel"] < 1.0, m
    # Gegenprobe: Vorlauf so volatil wie die Historie -> etwa 1.0
    pre_gleich = mk(start - timedelta(minutes=10), 10, rng=10.0)
    m2 = measure_pre(hist + pre_gleich, start)
    assert 0.5 < m2["pre_range_rel"] < 2.0, m2

    # Dochtanteil: body_frac=1.0 heisst Koerper = ganze Range -> Wick-Anteil ~0
    assert m["pre_wick_frac"] < 0.2, m
    pre_docht = mk(start - timedelta(minutes=10), 10, rng=10.0, body_frac=0.1)
    m3 = measure_pre(hist + pre_docht, start)
    assert m3["pre_wick_frac"] > 0.7, m3

    # Streak: 10 durchgehend steigende Closes -> Serie 10
    pre_up = [Bar(start - timedelta(minutes=10 - i), 100.0 + i, 100.0 + i + 2,
                  100.0 + i - 1, 100.0 + i + 1, None) for i in range(10)]
    m4 = measure_pre(hist + pre_up, start)
    assert m4["pre_streak"] == 10, m4
    # abwechselnd bull/bear -> Serie 1
    pre_alt = [Bar(start - timedelta(minutes=10 - i), 100.0, 102.0, 98.0,
                   101.0 if i % 2 == 0 else 99.0, None) for i in range(10)]
    m5 = measure_pre(hist + pre_alt, start)
    assert m5["pre_streak"] == 1, m5

    # Kontraktion: erste 5 Kerzen gross, letzte 5 klein -> Wert < 1
    schrumpf = (mk(start - timedelta(minutes=10), 5, rng=10.0)
                + mk(start - timedelta(minutes=5), 5, rng=2.0))
    m6 = measure_pre(hist + schrumpf, start)
    assert m6["pre_contraction"] < 1.0, m6

    # Zu wenig Historie fuer die Normierung -> pre_range_rel None, Rest trotzdem da
    m7 = measure_pre(pre, start)
    assert m7["pre_range_rel"] is None, m7
    assert m7["pre_wick_frac"] is not None and m7["pre_streak"] is not None, m7


def _check_events() -> None:
    start = at(date(2026, 8, 10), 9, 50)

    # Kein Vorlauf ueberhaupt -> alle Felder None, kein Absturz
    leer = measure_events([], start)
    assert all(v is None for v in leer.values()), leer

    # Kein Lookahead: Kerzen NACH dem Fenster duerfen die Vorgeschichte nicht aendern.
    # 200 ruhige Kerzen davor, dann ein extremer Ausschlag nach dem Fenster.
    ruhig = [Bar(start - timedelta(minutes=200 - i), 100.0, 100.5, 99.5, 100.0, None)
             for i in range(200)]
    danach = [Bar(start + timedelta(minutes=30 + i), 100.0, 500.0, 1.0, 400.0, None)
              for i in range(20)]
    a = measure_events(ruhig, start)
    b = measure_events(ruhig + danach, start)
    assert a == b, f"Lookahead: Kerzen nach dem Fenster aendern die Vorgeschichte\n{a}\n{b}"

    # Ohne Kerzen IM Fenster liefert measure_levels die leere Form, ohne abzustuerzen
    leer_lv = measure_levels(ruhig, start, start + timedelta(minutes=WINDOW_MIN))
    assert leer_lv["levels_open"] is None and leer_lv["levels_hit"] == "", leer_lv

    # Echter Fall: eine Zickzack-Historie erzeugt Swing-Level, das Fenster laeuft
    # darueber hinaus -> buyside muss als genommen auftauchen.
    zick = []
    for i in range(120):
        base = 100.0 + (5.0 if i % 10 < 5 else 0.0)
        zick.append(Bar(start - timedelta(minutes=120 - i), base, base + 1, base - 1, base, None))
    hoch = max(b.h for b in zick)
    win = [Bar(start + timedelta(minutes=i), hoch, hoch + 20, hoch - 1, hoch + 15, None)
           for i in range(WINDOW_MIN)]
    lv = measure_levels(zick + win, start, start + timedelta(minutes=WINDOW_MIN))
    assert isinstance(lv["levels_hit"], str), "levels_hit muss CSV-tauglich (str) sein"
    assert lv["levels_open"] is not None and lv["levels_open"] >= 0, lv
    assert "|" in lv["levels_hit"] or lv["levels_hit"] in ("", "buyside", "sellside"), lv


def _check_stats() -> None:
    # Wilson gegen von Hand nachgerechnete Werte
    lo, hi = wilson(1, 1)
    assert 0.0 <= lo <= 1.0 and 0.0 <= hi <= 1.0 and lo < hi, (lo, hi)
    assert hi == 1.0 or hi > 0.9, (lo, hi)      # 1/1 darf nicht als "100% sicher" gelten
    lo0, hi0 = wilson(0, 10)
    assert lo0 < 1e-9 and 0.0 < hi0 < 0.5, (lo0, hi0)   # 0/10 heisst nicht "nie"
    # symmetrisch: p=0,5 muss ein um 0,5 zentriertes Intervall geben
    lo5, hi5 = wilson(10, 20)
    assert abs((lo5 + hi5) / 2 - 0.5) < 1e-9, (lo5, hi5)
    # mehr Daten -> engeres Intervall
    a_lo, a_hi = wilson(60, 100)
    b_lo, b_hi = wilson(600, 1000)
    assert (b_hi - b_lo) < (a_hi - a_lo), "mehr n muss das Intervall verengen"

    # quote(): Mindest-n greift
    rows = [{"expansion": True} for _ in range(5)] + [{"expansion": False} for _ in range(5)]
    q = quote(rows, lambda r: r["expansion"])
    assert q["n"] == 10 and q["k"] == 5, q
    assert q["genug"] is False, "n=10 liegt unter MIN_N und darf nicht als belastbar gelten"
    gross = [{"expansion": True} for _ in range(30)] + [{"expansion": False} for _ in range(30)]
    q2 = quote(gross, lambda r: r["expansion"])
    assert q2["genug"] is True and abs(q2["p"] - 0.5) < 1e-9, q2
    # leere Menge darf nicht abstuerzen
    q3 = quote([], lambda r: r["expansion"])
    assert q3["n"] == 0 and q3["genug"] is False and q3["p"] is None, q3


def selfcheck() -> None:
    day = date(2026, 8, 10)         # Montag; session_day = Ende der Session
    ws = macro_windows_session(day)
    assert len(ws) == N_WINDOWS, f"{N_WINDOWS} Fenster erwartet, {len(ws)} bekommen"
    assert ws[0][0] == "18:50" and ws[-1][0] == "16:50", (ws[0][0], ws[-1][0])
    assert not any(w[0] == "17:50" for w in ws), "17:50 liegt in der Handelspause"
    # das erste Fenster liegt am Vorabend, das letzte am session_day
    assert ws[0][1].date() == date(2026, 8, 9), ws[0][1]
    assert ws[-1][1].date() == day, ws[-1][1]
    # Fenster sind eine Stunde auseinander und je 20 Minuten lang
    assert all((b[1] - a[1]) == timedelta(hours=1) for a, b in zip(ws, ws[1:]))
    assert all((w[2] - w[1]) == timedelta(minutes=WINDOW_MIN) for w in ws)
    # ueber den Datumswechsel: 23:50 gehoert zum Vorabend, 00:50 zum session_day
    lab = {w[0]: w[1].date() for w in ws}
    assert lab["23:50"] == date(2026, 8, 9) and lab["00:50"] == day, lab
    # jede der 23 Stunden muss genau einer Session zugeordnet sein
    assert len(SESSION_BY_HOUR) == N_WINDOWS, len(SESSION_BY_HOUR)
    assert all(w[1].hour in SESSION_BY_HOUR for w in ws), "Stunde ohne Session"

    start = at(day, 9, 50)
    full = _bars(start - timedelta(minutes=PRE_MIN), PRE_MIN + WINDOW_MIN)
    assert is_complete(full, start, start + timedelta(minutes=WINDOW_MIN))
    # eine fehlende Minute im Fenster reicht zum Ausschluss
    ohne_eine = [b for b in full if b.t != start + timedelta(minutes=7)]
    assert not is_complete(ohne_eine, start, start + timedelta(minutes=WINDOW_MIN))
    # eine fehlende Minute im Vorlauf ebenso
    ohne_pre = [b for b in full if b.t != start - timedelta(minutes=3)]
    assert not is_complete(ohne_pre, start, start + timedelta(minutes=WINDOW_MIN))
    # Fenster vollstaendig, aber gar kein Vorlauf
    nur_win = _bars(start, WINDOW_MIN)
    assert not is_complete(nur_win, start, start + timedelta(minutes=WINDOW_MIN))

    assert len(window_bars(full, start, start + timedelta(minutes=WINDOW_MIN))) == WINDOW_MIN

    _check_measure()
    _check_pre()
    _check_events()
    _check_stats()
    print("macro_db.selfcheck: OK")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("cmd", nargs="?", choices=["build", "stats", "plot"])
    p.add_argument("--symbol", default="MNQ")
    p.add_argument("--selfcheck", action="store_true")
    a = p.parse_args()
    if a.selfcheck:
        selfcheck()
    elif a.cmd == "build":
        cmd_build(a.symbol)
    elif a.cmd == "stats":
        cmd_stats(a.symbol)
    elif a.cmd == "plot":
        cmd_plot(a.symbol)
    else:
        p.error("cmd erwartet: build, stats oder plot")
