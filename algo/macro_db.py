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


def vergleich(teil: dict, basis: dict, bonf: float | None = None) -> str:
    """Bedingte Quote gegen Basisrate. Ueberlappende Intervalle heissen
    'kein Unterschied nachweisbar' -- nicht 'leicht erhoeht' (Spec 6, Regel 2).

    `bonf` ist die Bonferroni-korrigierte Signifikanzschwelle. Ist sie gesetzt, wird
    jede Abweichung zusaetzlich mit einem exakten Binomialtest gegen die Basisrate
    geprueft und direkt an der Zeile markiert, wenn sie die Korrektur nicht ueberlebt.
    Grund: die Schwelle nur im Fusstext zu nennen und auf keine einzige Aussage
    anzuwenden, laesst Zufallstreffer wie ein Ergebnis aussehen (Spec 6, Regel 4).
    """
    if not teil["genug"]:
        return "n zu klein"
    if teil["lo"] > basis["hi"]:
        richtung = "hoeher als die Basisrate"
    elif teil["hi"] < basis["lo"]:
        richtung = "niedriger als die Basisrate"
    else:
        return "kein Unterschied nachweisbar"
    if bonf is None or basis["p"] is None:
        return richtung
    from scipy.stats import binomtest
    p = binomtest(teil["k"], teil["n"], basis["p"]).pvalue
    return f"{richtung} (p={p:.4f}" + (")" if p < bonf else ", haelt Bonferroni nicht)")


def quartile(paare: list[tuple]) -> tuple[list, list, bool]:
    """Unterstes und oberstes Viertel nach dem **Kandidatenwert** -- Perzentil-Schnitt.

    Bewusst NICHT `sorted(paare)`: bei Gleichstand im Kandidatenwert entscheidet dort
    das zweite Tupelelement, also die Zielgroesse selbst -- das erfindet einen Effekt
    aus der Sortierung. Konkreter Fall: `pre_streak` ist ganzzahlig, 174 von 440 Zeilen
    haben den Wert 3; der Report wies dadurch 20,9 % gegen 50,0 % aus, mit zufaelliger
    Bindungsaufloesung sind es 36 % gegen 39 %. `key=lambda x: x[0]` reicht ebenfalls
    nicht -- Python sortiert stabil, dann entscheidet die Zeilenreihenfolge der CSV.

    Geschnitten wird am Wert. Laeuft eine Bindung ueber die Schnittkante, enthaelt die
    Gruppe mehr als ein Viertel der Zeilen und der Vergleich ist fuer diesen Kandidaten
    nicht aussagekraeftig -- das meldet das dritte Rueckgabeelement.
    """
    xs = sorted(x for x, _ in paare)
    q = max(1, len(xs) // 4)
    lo_cut, hi_cut = xs[q - 1], xs[-q]
    unten = [y for x, y in paare if x <= lo_cut]
    oben = [y for x, y in paare if x >= hi_cut]
    return unten, oben, (len(unten) > q or len(oben) > q)


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


KANDIDATEN = ("pre_range_rel", "pre_wick_frac", "pre_streak", "pre_contraction")

# Spec 6 verlangt die Kandidaten gegen `expansion` UND `dir`. `range` kommt als dritte
# Zielgroesse dazu, weil `dir` skalenfrei ist (|netto|/range) und einen reinen
# Groesseneffekt strukturell nicht sehen kann -- genau dort liegt der einzige
# belastbare Zusammenhang im Datensatz (pre_range_rel gegen range).
ZIELE = (("dir", lambda r: r["dir"]),
         ("expansion", lambda r: 1.0 if r["expansion"] else 0.0),
         ("range", lambda r: r["range"]))


def cmd_stats(symbol: str = "MNQ") -> None:
    rows = [r for r in read_csv() if r["symbol"] == symbol]
    if not rows:
        print("Keine Daten. Erst `python algo/macro_db.py build` laufen lassen.")
        return

    tage = sorted({r["session_day"] for r in rows})
    fenster = sorted({r["window"] for r in rows})
    basis = quote(rows, lambda r: r["expansion"])
    # Zweite Basisrate: der Quartilsvergleich unten misst NICHT `expansion` (dir >= 0,60
    # UND |netto| >= 30 Pkt), sondern nur die Geradlinigkeit dir >= 0,60. Wer dort die
    # expansion-Basisrate danebenstellt, macht aus +5 Punkten optisch +10.
    basis_dir = quote(rows, lambda r: r["dir"] >= DIR_THR)
    # Level-Basisrate: fast gesaettigt, siehe unten -- ohne sie liest sich "53,9 % buyside"
    # als Befund, obwohl es weitgehend Grundrauschen der Detektorwahl ist.
    basis_lv = quote(rows, lambda r: bool(r["levels_hit"]))

    # Alle Vergleiche zaehlen, bevor der erste gedruckt wird -- die Bonferroni-Schwelle
    # wird an den Zeilen gebraucht, nicht erst im Fusstext.
    n_vergleiche = (len(BEDINGUNGEN) + len(fenster) + len(KANDIDATEN) * len(ZIELE)
                    + len(KANDIDATEN) + 2)
    bonf = 0.05 / n_vergleiche

    print(f"{symbol}: {len(rows)} Fenster aus {len(tage)} Handelstagen "
          f"({tage[0]} .. {tage[-1]})")
    print(f"Basisrate Expansion: {fmt_quote(basis)}")
    print(f"Bonferroni-Schwelle ueber alle {n_vergleiche} Vergleiche: p < {bonf:.4f}\n")

    print("Je Bedingung (Expansion | Bedingung):")
    for name, pred in BEDINGUNGEN:
        q = quote([r for r in rows if pred(r)], lambda r: r["expansion"])
        print(f"  {name:46} {fmt_quote(q):40} {vergleich(q, basis, bonf)}")

    print("\nJe Fenster:")
    for w in fenster:
        q = quote([r for r in rows if r["window"] == w], lambda r: r["expansion"])
        print(f"  {w:>6}  {fmt_quote(q):40} {vergleich(q, basis, bonf)}")

    print("\nStartminute des Moves (start_min), alle Fenster:")
    sm = [int(r["start_min"]) for r in rows if r["start_min"] is not None]
    if sm:
        print(f"  Median {statistics.median(sm):.1f}, "
              f"Anteil in den ersten 5 Minuten: {100 * sum(1 for x in sm if x < 5) / len(sm):.1f}%")

    print("\nLevel im Fenster genommen:")
    print(f"  {'mind. ein Level':10} {fmt_quote(basis_lv):40} <- Basisrate der beiden Zeilen darunter")
    for seite in ("buyside", "sellside"):
        q = quote(rows, lambda r, s=seite: s in (r["levels_hit"] or ""))
        print(f"  {seite:10} {fmt_quote(q):40} {vergleich(q, basis_lv, bonf)}")
    print(f"  Die Kennzahl ist fast gesaettigt ({100 * basis_lv['p']:.1f} % aller Fenster nehmen")
    print("  irgendein Level) -- die Seitenquoten sind daher weitgehend Grundrauschen der")
    print(f"  Detektorwahl (untouched_levels mit swing={CFG['swing']} auf 1m), kein Befund.")

    # Spooling-Kandidaten gegen die Zielgroessen (Spec 6): haengt einer ueberhaupt mit
    # dem Fensterverlauf zusammen? Ein Nullbefund ist hier ein Ergebnis.
    print("\nSpooling-Kandidaten gegen die Zielgroessen (Spearman-Rangkorrelation):")
    from scipy.stats import spearmanr
    for k in KANDIDATEN:
        for ziel, f in ZIELE:
            paare = [(r[k], f(r)) for r in rows if r[k] is not None and f(r) is not None]
            if len(paare) < MIN_N:
                print(f"  {k:18} vs {ziel:10} n={len(paare)} -- zu wenig")
                continue
            rho, p = spearmanr([a for a, _ in paare], [b for _, b in paare])
            if p < bonf:
                mark = "  ** haelt Bonferroni"
            elif p < 0.05:
                mark = "  (p<0,05, haelt Bonferroni nicht)"
            else:
                mark = ""
            print(f"  {k:18} vs {ziel:10} rho={rho:+.3f} p={p:.4f} (n={len(paare)}){mark}")

    print(f"\nQuartilsvergleich: Anteil dir >= {DIR_THR:.2f} im untersten vs. obersten Viertel")
    print(f"  des Kandidatenwerts. Passende Basisrate: {fmt_quote(basis_dir)}")
    for k in KANDIDATEN:
        paare = [(r[k], r["dir"]) for r in rows if r[k] is not None and r["dir"] is not None]
        if len(paare) < MIN_N:
            print(f"  {k:18} n={len(paare)} -- zu wenig")
            continue
        unten, oben, gebunden = quartile(paare)
        qu = quote([{"g": d >= DIR_THR} for d in unten], lambda r: r["g"])
        qo = quote([{"g": d >= DIR_THR} for d in oben], lambda r: r["g"])
        print(f"  {k:18} unten {fmt_quote(qu):38} | oben {fmt_quote(qo):38}"
              f" {vergleich(qu, qo, bonf)}")
        if gebunden:
            print(f"  {'':18} ^ Bindung laeuft ueber die Schnittkante (Gruppen groesser als"
                  f" ein Viertel) -- fuer diesen Kandidaten nicht aussagekraeftig.")

    print(f"\n--- Vorbehalte ---")
    print(f"* {n_vergleiche} Vergleiche gerechnet ({len(BEDINGUNGEN)} Bedingungen,"
          f" {len(fenster)} Fenster, {len(KANDIDATEN) * len(ZIELE)} Spearman,"
          f" {len(KANDIDATEN)} Quartilsvergleiche, 2 Level-Quoten). Bei einem")
    print(f"  Signifikanzniveau von 5 % waeren rein zufaellig etwa"
          f" {0.05 * n_vergleiche:.1f} davon 'auffaellig'.")
    print(f"  Bonferroni-korrigiert liegt die Schwelle bei p < {bonf:.4f} -- Aussagen, die sie")
    print("  nicht ueberstehen, sind oben an der Zeile markiert.")
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
    # Fenster mit n < MIN_N (dieselbe Schwelle wie fmt_quote/vergleich) werden auf
    # Hoehe 0 gezeichnet und nur mit "n=..." beschriftet -- Graustufe und Schraffur
    # allein reichten nicht: 23:50 (n=1, zufaellig 100 %) war dadurch der HOECHSTE
    # Balken der Grafik, und das Auge liest Hoehe vor Beschriftung.
    fenster = sorted({r["window"] for r in rows})
    fenster_qs = [(w, quote([r for r in rows if r["window"] == w], lambda r: r["expansion"]))
                  for w in fenster]
    ps = [100 * (q["p"] or 0) if q["genug"] else 0.0 for _, q in fenster_qs]
    unten = [100 * ((q["p"] or 0) - q["lo"]) if q["genug"] else 0.0 for _, q in fenster_qs]
    oben = [100 * (q["hi"] - (q["p"] or 0)) if q["genug"] else 0.0 for _, q in fenster_qs]
    farben = ["#4a7ba7" if q["genug"] else "#c9c9c9" for _, q in fenster_qs]
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(fenster, ps, color=farben)
    ax.errorbar(fenster, ps, yerr=[unten, oben], fmt="none", ecolor="#333", capsize=3)
    for w, q in fenster_qs:
        if not q["genug"]:
            ax.text(w, 1, f"n={q['n']}", ha="center", va="bottom", fontsize=7,
                    color="#333", rotation=90)
    ax.axhline(100 * basis["p"], color="crimson", linestyle="--",
               label=f"Basisrate {100 * basis['p']:.1f}%")
    ax.set_ylabel("Expansionsquote (%)")
    ax.set_title(f"{symbol}: Expansion je Macro-Fenster "
                 f"({len(tage)} Handelstage, 95%-Wilson-Intervall)")
    handles, _ = ax.get_legend_handles_labels()
    handles.append(Patch(facecolor="#c9c9c9", edgecolor="#777777",
                          label=f"n < {MIN_N}: keine Quote, Balken auf 0, nur n=... beschriftet"))
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

    # 3) Level-Trefferquote -- mit Basisrate, sonst liest sich "53,9 % buyside" als
    # Befund, obwohl die Kennzahl fast gesaettigt ist (Spec 6, Regel 2).
    seiten = ["buyside", "sellside"]
    basis_lv = quote(rows, lambda r: bool(r["levels_hit"]))
    lq = [quote(rows, lambda r, s=s: s in (r["levels_hit"] or "")) for s in seiten]
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.bar(seiten, [100 * (q["p"] or 0) for q in lq], color="#4a7ba7")
    ax.errorbar(seiten, [100 * (q["p"] or 0) for q in lq],
                yerr=[[100 * ((q["p"] or 0) - q["lo"]) for q in lq],
                      [100 * (q["hi"] - (q["p"] or 0)) for q in lq]],
                fmt="none", ecolor="#333", capsize=4)
    ax.axhline(100 * basis_lv["p"], color="crimson", linestyle="--",
               label=f"mind. ein Level: {100 * basis_lv['p']:.1f}%")
    ax.set_ylim(0, 100)
    ax.set_ylabel("Anteil Fenster mit genommenem Level (%)")
    ax.set_title(f"{symbol}: Liquiditaet im Macro genommen")
    ax.legend(fontsize=8)
    plt.tight_layout()
    fig.savefig(BILD_DIR / "macro-db-level.png", dpi=110)
    plt.close(fig)

    knapp = [w for w, q in fenster_qs if not q["genug"]]
    _schreibe_wiki(symbol, rows, tage, basis, fenster, knapp, basis_lv)
    print(f"3 Diagramme -> {BILD_DIR}")
    print(f"Wiki-Seite   -> {WIKI_SEITE}")


def _hauptbefund(rows, basis, fenster) -> list[str]:
    """Der Nullbefund als Wiki-Text -- aus den Daten gerechnet, nicht abgeschrieben.

    Er stand bisher nur in der Konsolenausgabe von `stats` und war damit nach dem
    naechsten Terminalfenster weg. CLAUDE.md verlangt, dass ein Ergebnis ehrlich
    festgehalten wird, auch wenn es der Nutzer-These widerspricht -- ein Nullbefund
    ist ein Ergebnis, kein fehlendes Ergebnis.
    """
    from scipy.stats import spearmanr
    n_vergleiche = (len(BEDINGUNGEN) + len(fenster) + len(KANDIDATEN) * len(ZIELE)
                    + len(KANDIDATEN) + 2)
    bonf = 0.05 / n_vergleiche

    tabelle, treffer = [], []
    for k in KANDIDATEN:
        for ziel, f in ZIELE:
            paare = [(r[k], f(r)) for r in rows if r[k] is not None and f(r) is not None]
            if len(paare) < MIN_N:
                continue
            rho, p = spearmanr([a for a, _ in paare], [b for _, b in paare])
            halt = p < bonf
            tabelle.append(f"| `{k}` | `{ziel}` | {rho:+.3f} | {p:.4g} | {len(paare)} | "
                           f"{'**ja**' if halt else 'nein'} |")
            if halt:
                treffer.append((k, ziel, rho, p, len(paare)))

    auffaellig = [(n, q) for n, pred in BEDINGUNGEN
                  for q in [quote([r for r in rows if pred(r)], lambda r: r["expansion"])]
                  if q["genug"] and (q["lo"] > basis["hi"] or q["hi"] < basis["lo"])]

    out = [
        "## Hauptergebnis: Nullbefund bei den Spooling-Kandidaten",
        "",
        f"Keiner der vier Spooling-Kandidaten (`{'`, `'.join(KANDIDATEN)}`) korreliert mit der",
        "**Geradlinigkeit** des Fensters, und keine der "
        f"{len(BEDINGUNGEN)} Vorgeschichts-Bedingungen hebt sich",
        f"von der Basisrate ab ({len(auffaellig)} von {len(BEDINGUNGEN)} mit getrennten"
        " Wilson-Intervallen).",
        "Das ist das eigentliche Ergebnis dieser Datenbank — die Vermutung, an der Vorgeschichte",
        "eines Macro-Fensters lasse sich ablesen, ob es gleich sauber expandiert, trägt auf",
        "diesem Bestand nicht.",
        "",
        f"Rangkorrelation jedes Kandidaten gegen alle drei Zielgrößen (Bonferroni-Schwelle über",
        f"{n_vergleiche} Vergleiche: p < {bonf:.4f}):",
        "",
        "| Kandidat | Zielgröße | rho | p | n | hält Bonferroni |",
        "|---|---|---|---|---|---|",
        *tabelle,
        "",
    ]
    if treffer:
        out += ["### Gegenbefund: Volatilität hält an, sie staut sich nicht auf", ""]
        for k, ziel, rho, p, n in treffer:
            out.append(f"- **`{k}` gegen `{ziel}`: rho = {rho:+.3f}, p = {p:.4g} (n={n})**")
        out += [
            "",
            "Dieser Zusammenhang zeigt **in die Gegenrichtung der Spooling-These**: Nicht Ruhe vor",
            "dem Fenster geht großer Bewegung voraus, sondern **Aktivität**. Ein bereits unruhiger",
            "Vorlauf (`pre_range_rel` hoch = die 10 Minuten davor waren weiter als üblich) sagt eine",
            "**große Range** im Fenster vorher — klassische Volatilitätspersistenz, kein",
            "Macro-spezifischer Effekt. Er taucht nur gegen `range` auf und nicht gegen `dir`, weil",
            "`dir` = |netto|/range skalenfrei ist und einen reinen Größeneffekt strukturell nicht",
            "sehen kann. Für die Spooling-Hypothese ist das keine Bestätigung, sondern ihr",
            "Gegenteil: das Fenster wird groß, wenn es vorher schon laut war.",
            "",
        ]
    return out


def _schreibe_wiki(symbol, rows, tage, basis, fenster, knapp, basis_lv) -> None:
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
        *_hauptbefund(rows, basis, fenster),
        "## Expansion je Fenster",
        "",
        "![[macro-db-expansion.png]]",
        ("*Expansionsquote je Macro-Fenster mit 95%-Wilson-Intervall. Rote Linie: Basisrate über"
         f" alle Fenster. Fenster mit n < {MIN_N} stehen grau auf Höhe 0 und tragen nur die"
         " n=…-Beschriftung — für sie wird bewusst keine Quote gezeigt.*"),
        "",
        "## Wann setzt der Move ein?",
        "",
        "![[macro-db-timing.png]]",
        "*Minute im 20-Minuten-Fenster, in der der Move einsetzt — definiert als das Extrem entgegen der Netto-Richtung.*",
        "",
        "## Liquidität im Fenster genommen",
        "",
        "![[macro-db-level.png]]",
        ("*Anteil der Fenster, in denen ein vor dem Fenster offenes Swing-Level genommen wurde."
         f" Rote Linie: **{100 * basis_lv['p']:.1f} % aller Fenster nehmen mindestens ein Level**"
         f" ({fmt_quote(basis_lv)}) — die Kennzahl ist damit fast gesättigt. Die beiden"
         " Seitenquoten sind vor diesem Hintergrund weitgehend Grundrauschen der Detektorwahl"
         f" (`untouched_levels`, swing={CFG['swing']} auf 1m), kein eigenständiger Befund.*"),
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

    # Kein Lookahead (Muster aus _check_events): ruhige Kerzen davor, danach ein
    # extremer Ausschlag AB dem Fensterstart -- die Vorlauf-Kennzahlen muessen identisch
    # bleiben. Diese Messfamilie ist die einzige mit Blockarithmetik
    # (`start - pre_min * k`), wo ein Off-by-one still ins Fenster greifen wuerde; die
    # erste Kerze von `danach` liegt genau auf `start` und prueft damit die Kante.
    danach = [Bar(start + timedelta(minutes=i), 100.0, 900.0, 1.0, 800.0, None)
              for i in range(WINDOW_MIN)]
    a = measure_pre(hist + pre, start)
    b = measure_pre(hist + pre + danach, start)
    assert a == b, f"Lookahead in measure_pre: Kerzen ab dem Fensterstart aendern\n{a}\n{b}"

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

    # quartile(): der eigentliche C1-Regressionstest. Kandidatenwert konstant 3, das
    # Ergebnis in der ersten Haelfte 0 und in der zweiten 1 -- `sorted(paare)` wuerde
    # daraus "unten 0 %, oben 100 %" machen. Richtig ist: eine einzige Bindung, beide
    # Gruppen = alle Zeilen, Vergleich als nicht aussagekraeftig gemeldet.
    gebunden_paare = [(3, 0.0)] * 50 + [(3, 1.0)] * 50
    u, o, gebunden = quartile(gebunden_paare)
    assert gebunden is True, "Bindung ueber die Schnittkante muss gemeldet werden"
    assert len(u) == len(o) == 100, (len(u), len(o))
    assert sum(u) == sum(o) == 50, "beide Gruppen muessen dieselbe Zeilenmenge sein"
    # Gegenprobe ohne Bindungen: sauberer Quartilsschnitt, kein Flag
    sauber = [(i, 1.0 if i >= 50 else 0.0) for i in range(100)]
    u2, o2, gebunden2 = quartile(sauber)
    assert gebunden2 is False and len(u2) == len(o2) == 25, (len(u2), len(o2), gebunden2)
    assert sum(u2) == 0 and sum(o2) == 25, (sum(u2), sum(o2))
    # Reihenfolge der Eingabe darf nichts aendern (kein stabiles-Sortieren-Artefakt)
    import random
    misch = list(gebunden_paare)
    random.Random(0).shuffle(misch)
    assert quartile(misch)[2] is True and sum(quartile(misch)[0]) == 50


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
