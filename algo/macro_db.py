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
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from tools.analyze_ohlc import CFG, DATA_DIR, NY, Bar, at, load  # noqa: E402

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


CSV_PATH = Path(__file__).resolve().parent / "results" / "macro_db.csv"

FIELDS = ["symbol", "session_day", "window", "weekday", "session",
          "range", "netto", "dir", "direction", "start_min", "expansion"]


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
    else:
        p.error("stats/plot folgen in spaeteren Tasks")
