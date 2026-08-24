#!/usr/bin/env python3
"""Backtest: Bringen newsarme Tage weniger Bewegung? Und sind Mi/Do wirklich die besten Tage?

Anlass: Jannes' Weekly Bias KW34 (2026-08-16) enthaelt zwei pruefbare Aussagen --
  1. "Aufgrund der wenigen News erwarte ich, dass wir keine grosse Priceaction erhalten."
  2. "Am Mittwoch und Donnerstag gehe ich davon aus, dass wir dort die beste Priceaction
     erhalten."
Beide sind falsifizierbare Behauptungen ueber ein Regelwerk, also werden sie geprueft statt
besprochen (CLAUDE.md: jede These wird gebacktestet).

**Datenquelle Termine:** TradingView-Wirtschaftskalender ueber `bias_levels._tv_news()` --
ForexFactory liefert nur die laufende Woche, TradingView beliebige Zeitraeume. Gefiltert auf
USD und Red/Orange, genau wie in der Bias-Vorlage.

**Datenquelle Preis:** NQ-Tagesdaten (nicht MNQ -- Micro/Mini werden strikt getrennt).
Bekannte Grenze: einzelne 1d-Tage im Bestand sind zu frueh gezogene Snapshots (belegt fuer
den 14.08.2026, 154 Punkte zu klein). Fuer einen *Verteilungsvergleich* ueber hunderte Tage
faellt das kaum ins Gewicht, fuer einen Einzeltag schon -- deshalb Median statt Mittelwert.

Aufruf:
    python algo/backtest_news_dichte.py            # Bericht
    python algo/backtest_news_dichte.py --demo     # Selbstcheck, kein Netz
"""

from __future__ import annotations

import statistics
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

JAHRE_ZURUECK = 3
WOCHENTAG = ["Mo", "Di", "Mi", "Do", "Fr"]


def termine_je_tag(von: date, bis: date) -> dict:
    """{ISO-Datum: {"red": n, "orange": n}} aus dem TradingView-Kalender, quartalsweise geholt."""
    import bias_levels as b

    out: dict = {}
    start = von
    while start <= bis:
        ende = min(start + timedelta(days=90), bis)
        r = b._tv_news(start, ende)
        for e in r.get("events", []):
            tag = out.setdefault(e["ny"][:10], {"red": 0, "orange": 0})
            tag["red" if e["impact"] == "Red" else "orange"] += 1
        start = ende + timedelta(days=1)
    return out


def einordnen(rows: list, termine: dict) -> dict:
    """Tagesranges nach News-Dichte und Wochentag gruppieren."""
    nach_dichte: dict = {"0 (newsarm)": [], "1-2": [], "3+": []}
    nach_tag: dict = {w: [] for w in WOCHENTAG}
    nach_red: dict = {"kein Red": [], "mind. 1 Red": []}

    for r in rows:
        if r["day"].weekday() >= 5:
            continue
        spanne = r["high"] - r["low"]
        if spanne <= 0:
            continue
        t = termine.get(r["day"].isoformat(), {"red": 0, "orange": 0})
        n = t["red"] + t["orange"]
        schluessel = "0 (newsarm)" if n == 0 else ("1-2" if n <= 2 else "3+")
        nach_dichte[schluessel].append(spanne)
        nach_tag[WOCHENTAG[r["day"].weekday()]].append(spanne)
        nach_red["mind. 1 Red" if t["red"] else "kein Red"].append(spanne)

    def kennz(werte: list) -> dict:
        if not werte:
            return {"n": 0}
        return {"n": len(werte), "median": round(statistics.median(werte), 1),
                "avg": round(statistics.fmean(werte), 1)}

    return {"dichte": {k: kennz(v) for k, v in nach_dichte.items()},
            "wochentag": {k: kennz(v) for k, v in nach_tag.items()},
            "red": {k: kennz(v) for k, v in nach_red.items()}}


def demo() -> None:
    class R(dict):
        pass

    def tag(d: date, hi: float, lo: float) -> dict:
        return {"day": d, "high": hi, "low": lo}

    # Mo newsarm (Range 100), Di mit 3 Terminen (Range 300), Sa wird ignoriert
    rows = [tag(date(2026, 8, 17), 100, 0), tag(date(2026, 8, 18), 300, 0),
            tag(date(2026, 8, 22), 999, 0)]
    termine = {"2026-08-18": {"red": 1, "orange": 2}}
    r = einordnen(rows, termine)
    assert r["dichte"]["0 (newsarm)"] == {"n": 1, "median": 100.0, "avg": 100.0}, r["dichte"]
    assert r["dichte"]["3+"] == {"n": 1, "median": 300.0, "avg": 300.0}, r["dichte"]
    assert r["dichte"]["1-2"]["n"] == 0, "keine Fehlzuordnung"
    assert r["wochentag"]["Mo"]["n"] == 1 and r["wochentag"]["Di"]["n"] == 1
    assert sum(v["n"] for v in r["wochentag"].values()) == 2, "Samstag muss rausfallen"
    assert r["red"]["mind. 1 Red"]["median"] == 300.0, r["red"]
    assert r["red"]["kein Red"]["median"] == 100.0, r["red"]
    # Tag ohne Spanne wird verworfen statt als 0 zu zaehlen
    assert einordnen([tag(date(2026, 8, 17), 5, 5)], {})["dichte"]["0 (newsarm)"]["n"] == 0
    print("backtest_news_dichte: alle Checks bestanden")


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    if "--demo" in argv:
        demo()
        return 0

    from backtest_common import load_rows

    bis = date.today()
    von = bis - timedelta(days=365 * JAHRE_ZURUECK)
    print(f"Hole USD-Termine {von} .. {bis} (TradingView, quartalsweise) ...")
    termine = termine_je_tag(von, bis)
    rows = [r for r in load_rows("NQ") if von <= r["day"] <= bis]
    r = einordnen(rows, termine)

    print(f"\nNQ-Handelstage im Fenster: {sum(v['n'] for v in r['wochentag'].values())}, "
          f"Tage mit Terminen: {len(termine)}\n")

    print("1. Tagesrange nach Anzahl USD-Termine (Red+Orange)")
    for k, v in r["dichte"].items():
        if v["n"]:
            print(f"   {k:>12}: n={v['n']:>4}  Median-Range {v['median']:>7}  Ø {v['avg']:>7}")
    print("\n2. Tagesrange mit/ohne Red-Folder-Termin")
    for k, v in r["red"].items():
        if v["n"]:
            print(f"   {k:>12}: n={v['n']:>4}  Median-Range {v['median']:>7}  Ø {v['avg']:>7}")
    print("\n3. Tagesrange nach Wochentag")
    for k in WOCHENTAG:
        v = r["wochentag"][k]
        if v["n"]:
            print(f"   {k:>12}: n={v['n']:>4}  Median-Range {v['median']:>7}  Ø {v['avg']:>7}")

    d = r["dichte"]
    if d["0 (newsarm)"]["n"] and d["3+"]["n"]:
        diff = d["3+"]["median"] - d["0 (newsarm)"]["median"]
        pct = 100 * diff / d["0 (newsarm)"]["median"]
        print(f"\nThese 1 (newsarm = wenig Bewegung): newsreiche Tage haben eine um "
              f"{diff:+.1f} Punkte ({pct:+.1f} %) groessere Median-Range.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
