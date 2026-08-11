#!/usr/bin/env python3
"""These (Jannes/ICT, 2026-08-11): Das 1st Presented FVG der **Montags**-NY-AM-Session
ist fuer die **gesamte Handelswoche** relevant -- es wird spaeter in der Woche respektiert
und angelaufen. Andere Wochentage haben zwar auch ein 1.p FVG, aber ohne diesen
Wochen-Status.

Definition 1.p FVG (siehe wiki/concepts/ORG (Opening Range Gap) & 1st Presented FVG.md):
das erste FVG, dessen **komplette 3-Kerzen-Formation** in der NY AM Session liegt. Fuer
den 9:30-Open ist die frueheste Formation 9:30/9:31/9:32. Ein FVG, dessen mittlere Kerze
auf 9:30 faellt, beginnt um 9:29 und ist damit ein normales FVG, aber kein 1.p FVG.

Testaufbau -- zwei getrennte Fragen:

  (A) Fairer Wochentagsvergleich bei GLEICHER Exposure: wird das 1.p FVG am unmittelbar
      folgenden Handelstag beruehrt? Montag vs. Di/Mi/Do. Nur so ist der Vergleich sauber
      -- das Montags-FVG hat sonst 4 Resttage Zeit, das Donnerstags-FVG nur einen.

  (B) Deskriptiv fuer Montag: wird das FVG irgendwann Di-Fr beruehrt, und an welchem Tag
      zuerst? Das ist die woertliche ICT-Behauptung, aber ohne Kontrollgruppe.

Kontrollgroesse: Abstand vom Schlusskurs des Bildungstags zur Zone. Ein FVG dicht am
Preis wird fast zwangslaeufig beruehrt -- liegen Montags-FVGs naeher, erklaert das eine
hoehere Rate ohne jede "Besonderheit".

Aufruf:
    python algo/backtest_1p_fvg_woche.py             # 5m (mehr Historie)
    python algo/backtest_1p_fvg_woche.py --tf 1m
    python algo/backtest_1p_fvg_woche.py --selfcheck
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

from scipy.stats import fisher_exact

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "algo"))
from analyze_ohlc import Bar, at, fvgs, load  # noqa: E402
from backtest_common import write_result  # noqa: E402

# NY AM Session: RTH-Open bis 11:00. Start 9:30, weil das 1.p FVG laut Wiki ab 9:31 zaehlt.
AM_START = (9, 30)
AM_END = (11, 0)
WD = ["Mo", "Di", "Mi", "Do", "Fr"]


def find_days(symbol: str, tf: str) -> dict[date, Path]:
    """{Handelstag: Pfad} fuer alle Tagesordner mit <symbol>-<tf>-Datei."""
    out = {}
    for f in sorted(ROOT.glob(f"raw/marktdaten/*/*/*/{symbol} * {tf}.csv")):
        try:
            d = date(*map(int, f.stem.split()[1].split("-")))
        except (ValueError, IndexError):
            continue
        out[d] = f
    return out


def am_fvgs(bars: list[Bar], day: date) -> list[dict]:
    """Alle FVGs der NY AM Session, deren komplette Formation im Fenster liegt."""
    win = [b for b in bars if at(day, *AM_START) <= b.t < at(day, *AM_END)]
    return fvgs(win) if len(win) >= 3 else []


def first_presented_fvg(bars: list[Bar], day: date) -> dict | None:
    """1.p FVG der NY AM Session: erstes FVG mit kompletter Formation im Fenster."""
    found = am_fvgs(bars, day)
    return found[0] if found else None


def touched(bars: list[Bar], lo: float, hi: float, ce: float) -> tuple[bool, bool]:
    """(Zone beruehrt, C.E. erreicht) durch irgendeine Kerze."""
    t = c = False
    for b in bars:
        if b.l <= hi and b.h >= lo:
            t = True
            if b.l <= ce <= b.h:
                c = True
                break
    return t, c


def run(symbol: str, tf: str) -> dict:
    days = find_days(symbol, tf)
    bars_of = {d: load(p) for d, p in days.items()}
    # Bars eindeutig einem Kalendertag zuordnen -- die Tagesdateien ueberlappen sich
    # (Globex 18:00 Vortag - 17:00), sonst wuerde derselbe Bar doppelt zaehlen.
    day_bars = {d: [b for b in bs if b.t.date() == d] for d, bs in bars_of.items()}

    recs = []
    for d in sorted(days):
        if d.weekday() > 4:
            continue
        f = first_presented_fvg(bars_of[d], d)
        if f is None:
            continue
        close = day_bars[d][-1].c if day_bars[d] else None
        # Abstand Schlusskurs -> Zone (0, wenn der Kurs in der Zone schliesst)
        dist = 0.0 if close is None or f["lo"] <= close <= f["hi"] else (
            min(abs(close - f["lo"]), abs(close - f["hi"])))

        # Restliche Handelstage derselben Kalenderwoche
        rest = [x for x in sorted(days)
                if d < x <= d + timedelta(days=4 - d.weekday())
                and x.isocalendar()[:2] == d.isocalendar()[:2] and day_bars.get(x)]
        nxt = rest[0] if rest else None

        t_next, ce_next = touched(day_bars[nxt], f["lo"], f["hi"], f["ce"]) if nxt else (None, None)

        erst = None
        t_week = ce_week = False
        for x in rest:
            t, c = touched(day_bars[x], f["lo"], f["hi"], f["ce"])
            if t and erst is None:
                erst = x
            t_week = t_week or t
            ce_week = ce_week or c

        recs.append({
            "day": d, "wd": WD[d.weekday()], "t": f["t"], "side": f["side"],
            "lo": f["lo"], "hi": f["hi"], "ce": f["ce"], "size": f["size"],
            "close": close, "dist": dist, "n_rest": len(rest),
            "next_day": nxt, "touch_next": t_next, "ce_next": ce_next,
            "touch_week": t_week if rest else None,
            "ce_week": ce_week if rest else None,
            "first_touch": erst, "first_touch_wd": WD[erst.weekday()] if erst else None,
        })

    # --- (A) fairer Vergleich: Beruehrung am unmittelbaren Folgetag ---
    mit_next = [r for r in recs if r["touch_next"] is not None]
    mo = [r for r in mit_next if r["wd"] == "Mo"]
    rest_wd = [r for r in mit_next if r["wd"] in ("Di", "Mi", "Do")]

    def rate(rs, key):
        return (sum(bool(r[key]) for r in rs), len(rs),
                100 * sum(bool(r[key]) for r in rs) / len(rs) if rs else None)

    mo_t, mo_n, mo_p = rate(mo, "touch_next")
    re_t, re_n, re_p = rate(rest_wd, "touch_next")
    p_touch = None
    if mo_n and re_n:
        p_touch = fisher_exact([[mo_t, mo_n - mo_t], [re_t, re_n - re_t]])[1]

    mo_c, _, mo_cp = rate(mo, "ce_next")
    re_c, _, re_cp = rate(rest_wd, "ce_next")
    p_ce = None
    if mo_n and re_n:
        p_ce = fisher_exact([[mo_c, mo_n - mo_c], [re_c, re_n - re_c]])[1]

    med = lambda rs: (sorted(r["dist"] for r in rs)[len(rs) // 2] if rs else None)

    # --- (B) deskriptiv: Montags-FVG ueber die Restwoche ---
    mo_alle = [r for r in recs if r["wd"] == "Mo" and r["touch_week"] is not None]
    tw = sum(bool(r["touch_week"]) for r in mo_alle)
    cw = sum(bool(r["ce_week"]) for r in mo_alle)
    verteilung = Counter(r["first_touch_wd"] for r in mo_alle if r["first_touch_wd"])

    per_wd = defaultdict(list)
    for r in mit_next:
        per_wd[r["wd"]].append(bool(r["touch_next"]))

    # --- (C) ist das ERSTE FVG besonders? 1.p gegen die uebrigen FVGs derselben Session,
    # gleicher Tag und gleiche Exposure (Folgetag). Achtung: FVGs eines Tages sind nicht
    # unabhaengig voneinander (Clustering) -- der p-Wert ist dadurch zu optimistisch.
    erste, uebrige = [], []
    for d in sorted(days):
        if d.weekday() > 4:
            continue
        alle = am_fvgs(bars_of[d], d)
        if not alle:
            continue
        rest = [x for x in sorted(days)
                if d < x <= d + timedelta(days=4 - d.weekday())
                and x.isocalendar()[:2] == d.isocalendar()[:2] and day_bars.get(x)]
        if not rest:
            continue
        nb = day_bars[rest[0]]
        cl = day_bars[d][-1].c if day_bars[d] else None
        for i, g in enumerate(alle):
            t, c = touched(nb, g["lo"], g["hi"], g["ce"])
            # Abstand Tagesschluss -> Zone: das 1.p FVG ist das frueheste und liegt
            # dadurch tendenziell weiter weg als spaetere -- ohne diese Groesse waere
            # der Vergleich unfair zuungunsten des 1.p FVG.
            dd = None if cl is None else (
                0.0 if g["lo"] <= cl <= g["hi"] else min(abs(cl - g["lo"]), abs(cl - g["hi"])))
            (erste if i == 0 else uebrige).append(
                {"touch": t, "ce": c, "size": g["size"], "dist": dd})

    def q(rs, key):
        return (sum(bool(x[key]) for x in rs), len(rs),
                100 * sum(bool(x[key]) for x in rs) / len(rs) if rs else None)

    e_t, e_n, e_p = q(erste, "touch")
    u_t, u_n, u_p = q(uebrige, "touch")
    p_erst = fisher_exact([[e_t, e_n - e_t], [u_t, u_n - u_t]])[1] if e_n and u_n else None
    msize = lambda rs: (sorted(x["size"] for x in rs)[len(rs) // 2] if rs else None)
    mdist = lambda rs: (sorted(x["dist"] for x in rs if x["dist"] is not None)[
        len([x for x in rs if x["dist"] is not None]) // 2] if any(x["dist"] is not None for x in rs) else None)

    return {
        "symbol": symbol, "tf": tf, "n_fvgs": len(recs),
        "zeitraum": [str(min(r["day"] for r in recs)), str(max(r["day"] for r in recs))] if recs else None,
        "A_folgetag": {
            "montag": {"touch": mo_t, "n": mo_n, "pct": mo_p, "ce": mo_c, "ce_pct": mo_cp,
                        "median_dist": med(mo)},
            "di_mi_do": {"touch": re_t, "n": re_n, "pct": re_p, "ce": re_c, "ce_pct": re_cp,
                          "median_dist": med(rest_wd)},
            "p_touch_fisher": p_touch, "p_ce_fisher": p_ce,
            "je_wochentag": {k: [sum(v), len(v)] for k, v in sorted(per_wd.items(),
                              key=lambda kv: WD.index(kv[0]))},
        },
        "B_montag_restwoche": {
            "n": len(mo_alle), "touch_week": tw, "ce_week": cw,
            "erster_touch_tag": dict(verteilung),
        },
        "C_erstes_vs_uebrige": {
            "erstes": {"touch": e_t, "n": e_n, "pct": e_p, "median_size": msize(erste),
                        "median_dist": mdist(erste)},
            "uebrige": {"touch": u_t, "n": u_n, "pct": u_p, "median_size": msize(uebrige),
                         "median_dist": mdist(uebrige)},
            "p_fisher": p_erst,
        },
        "records": recs,
    }


def report(res: dict) -> list[str]:
    A, B = res["A_folgetag"], res["B_montag_restwoche"]
    L = [f"# 1.p FVG der NY AM Session -- Wochenrelevanz ({res['symbol']}, {res['tf']})", ""]
    L.append(f"Zeitraum {res['zeitraum'][0]} .. {res['zeitraum'][1]}, {res['n_fvgs']} 1.p FVGs.")
    L.append("")
    L.append("## (A) Beruehrung am unmittelbaren Folgetag -- gleiche Exposure")
    m, r = A["montag"], A["di_mi_do"]
    L.append(f"- Montag:    {m['touch']}/{m['n']} beruehrt"
             + (f" ({m['pct']:.0f} %)" if m["pct"] is not None else "")
             + f", C.E. {m['ce']}/{m['n']}"
             + (f" ({m['ce_pct']:.0f} %)" if m["ce_pct"] is not None else "")
             + (f", Median-Abstand {m['median_dist']:.1f} Pkt" if m["median_dist"] is not None else ""))
    L.append(f"- Di/Mi/Do:  {r['touch']}/{r['n']} beruehrt"
             + (f" ({r['pct']:.0f} %)" if r["pct"] is not None else "")
             + f", C.E. {r['ce']}/{r['n']}"
             + (f" ({r['ce_pct']:.0f} %)" if r["ce_pct"] is not None else "")
             + (f", Median-Abstand {r['median_dist']:.1f} Pkt" if r["median_dist"] is not None else ""))
    if A["p_touch_fisher"] is not None:
        L.append(f"- Fisher exact: p={A['p_touch_fisher']:.3f} (Touch), "
                 f"p={A['p_ce_fisher']:.3f} (C.E.)")
    L.append(f"- je Wochentag (Touch/n): "
             + ", ".join(f"{k} {v[0]}/{v[1]}" for k, v in A["je_wochentag"].items()))
    L.append("")
    L.append("## (B) Montags-FVG ueber die Restwoche (deskriptiv, keine Kontrollgruppe)")
    if B["n"]:
        L.append(f"- irgendwann Di-Fr beruehrt: {B['touch_week']}/{B['n']} "
                 f"({100 * B['touch_week'] / B['n']:.0f} %), C.E. {B['ce_week']}/{B['n']} "
                 f"({100 * B['ce_week'] / B['n']:.0f} %)")
        L.append(f"- erster Touch-Tag: {B['erster_touch_tag'] or '-'}")
    else:
        L.append("- keine Montage mit Restwoche im Datenbestand")
    C = res["C_erstes_vs_uebrige"]
    L.append("")
    L.append("## (C) Ist das ERSTE FVG besonders? 1.p gegen die uebrigen der Session")
    for k, lab in (("erstes", "1.p FVG "), ("uebrige", "uebrige ")):
        x = C[k]
        L.append(f"- {lab}: {x['touch']}/{x['n']} am Folgetag beruehrt"
                 + (f" ({x['pct']:.0f} %)" if x["pct"] is not None else "")
                 + (f", Median-Groesse {x['median_size']:.2f} Pkt" if x["median_size"] is not None else "")
                 + (f", Median-Abstand {x['median_dist']:.1f} Pkt" if x["median_dist"] is not None else ""))
    if C["p_fisher"] is not None:
        L.append(f"- Fisher exact: p={C['p_fisher']:.3f} "
                 "(FVGs eines Tages sind nicht unabhaengig -> p zu optimistisch)")
    return L


def selfcheck() -> None:
    """Kunstdaten: 1.p FVG muss die randueberlappende Formation ueberspringen, und
    Touch/C.E. muessen sauber erkannt werden."""
    d = date(2026, 8, 3)
    mk = lambda hh, mm, o, h, l, c: Bar(at(d, hh, mm), o, h, l, c, 0)
    bars = [
        mk(9, 29, 100, 101, 99, 100),
        mk(9, 30, 102, 108, 102, 107),   # Mitte einer Formation, die 9:29 beginnt
        mk(9, 31, 110, 112, 109, 111),   # -> c.l=109 > a.h=101, aber randueberlappend
        mk(9, 32, 113, 118, 113, 117),
        mk(9, 33, 121, 123, 120, 122),   # Formation 9:31/9:32/9:33 liegt komplett innen
    ]
    f = first_presented_fvg(bars, d)
    # frueheste moegliche Formation ist 9:30/9:31/9:32 -> FVG traegt die Zeit der
    # mittleren Kerze (9:31); die Formation um 9:29/9:30/9:31 faellt raus.
    assert f is not None and f["t"] == at(d, 9, 31), f"erwartet 9:31, war {f and f['t']}"
    assert (f["lo"], f["hi"]) == (107, 113), f"Zone falsch: {f['lo']}-{f['hi']}"

    zone = (107.0, 113.0, 110.0)
    assert touched([mk(10, 0, 130, 131, 129, 130)], *zone) == (False, False), "kein Touch erwartet"
    assert touched([mk(10, 0, 130, 131, 112, 130)], *zone) == (True, False), "Touch ohne C.E."
    assert touched([mk(10, 0, 130, 131, 109, 130)], *zone) == (True, True), "C.E. erwartet"

    # zu wenig Bars im Fenster -> kein FVG statt Absturz
    assert first_presented_fvg(bars[:2], d) is None
    print("backtest_1p_fvg_woche selfcheck ok")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--symbol", default="MNQ")
    ap.add_argument("--tf", default="5m", choices=["1m", "5m", "15m"])
    ap.add_argument("--selfcheck", action="store_true")
    a = ap.parse_args(argv)
    if a.selfcheck:
        selfcheck()
        return 0
    res = run(a.symbol, a.tf)
    if not res["n_fvgs"]:
        print("keine 1.p FVGs gefunden -- Datenbestand pruefen")
        return 1
    print("\n".join(report(res)))
    write_result(f"backtest_1p_fvg_woche_{a.tf}", res)
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
