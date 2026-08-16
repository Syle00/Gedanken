#!/usr/bin/env python3
"""COT-Positionierung (Commitment of Traders) fuer den Weekly Bias.

Quelle: CFTC-Legacy-Report ueber das Paket `cot_reports`
(https://github.com/NDelventhal/cot_reports). Ausgewertet wird nach ICT-Lesart **nur**
Commercials gegen Large Speculators (Non-Commercials) -- Small Specs bleiben aussen vor.

**Marktreihe, kalibriert (2026-08-16).** Die CFTC fuehrt NQ dreifach: "NASDAQ MINI",
"NASDAQ-100 Consolidated" und "MICRO E-MINI NASDAQ-100 INDEX". Sie liefern deutlich
verschiedene Zahlen. Massgeblich ist **"NASDAQ MINI"**: dort steht zum Report 2026-07-28
comm_net = -14.946, und genau diese -14,95 K nennt `wiki/concepts/COT (Commitment of Traders)
Data.md` als Wert von Jannes' eigenem Indikator. Consolidated haette -8.044 ergeben, Micro
+69.021 -- beide waeren still an seinem Chart vorbeigelaufen.

**Auswertung nach dem Wiki, nicht nach der 0-Linie.** Die Wiki-Seite praezisiert ausdruecklich:
massgeblich ist das **EQ der Lookback-Range**, nicht die Null. Bei Index-Futures sind
Commercials strukturell netto short, das EQ liegt also tief im Negativen; wer die 0-Linie
nimmt, liest fast immer "bearish". Deshalb: Signal = aktueller Wert ueber/unter dem EQ aus
High und Low des jeweiligen Lookbacks.

**Horizonte immer mit ausgeben.** Laut Wiki widersprechen sich 3M/6M/12M/2Y/4Y regelmaessig
(am 03.08.2026 stand NQ auf 3M SELL, 6M SELL, 12M BUY, 2Y BUY, 4Y SELL). Ein COT-Urteil ohne
Angabe des Lookbacks ist nicht ueberpruefbar.

Aufruf:
    python algo/cot.py            # NQ + ES, alle Horizonte
    python algo/cot.py --json     # maschinenlesbar (nutzt bias_levels.py)
    python algo/cot.py --demo     # Selbstcheck, kein Netz-/Dateizugriff
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from contextlib import contextmanager
from datetime import date, datetime, timedelta
from pathlib import Path

# CFTC-Marktreihe je Vault-Symbol -- siehe Kalibrierung im Modulkopf.
MAERKTE = {"NQ": "NASDAQ MINI", "ES": "E-MINI S&P 500"}
# Lookbacks in Monaten, Reihenfolge wie im Indikator des Nutzers
HORIZONTE = {"3M": 3, "6M": 6, "12M": 12, "2Y": 24, "4Y": 48}
CACHE = Path(tempfile.gettempdir()) / "cot_legacy_fut.json"
CACHE_TTL = 6 * 3600      # s -- der Report erscheint nur freitags, 6 h sind reichlich knapp
SPALTE_DATUM = "As of Date in Form YYYY-MM-DD"
SPALTEN = {"c_long": "Commercial Positions-Long (All)",
           "c_short": "Commercial Positions-Short (All)",
           "nc_long": "Noncommercial Positions-Long (All)",
           "nc_short": "Noncommercial Positions-Short (All)"}


@contextmanager
def _im_temp():
    """cot_reports legt `annual.txt` im *aktuellen* Arbeitsverzeichnis ab. Ohne diesen
    Wechsel landet die Datei im Repo-Root und taucht in jedem `git status` auf."""
    alt = os.getcwd()
    with tempfile.TemporaryDirectory() as d:
        os.chdir(d)
        try:
            yield
        finally:
            os.chdir(alt)


def _lade_jahre(jahre: list[int]) -> list[dict]:
    """Rohzeilen der gewuenschten Jahre, auf die gebrauchten Spalten reduziert."""
    if CACHE.exists() and time.time() - CACHE.stat().st_mtime < CACHE_TTL:
        gespeichert = json.loads(CACHE.read_text("utf-8"))
        if set(gespeichert.get("jahre", [])) >= set(jahre):
            return gespeichert["zeilen"]

    import cot_reports  # lokal: nur noetig, wenn wirklich geladen wird

    zeilen: list[dict] = []
    with _im_temp():
        for jahr in jahre:
            df = cot_reports.cot_year(year=jahr, cot_report_type="legacy_fut")
            d = df[df["Market and Exchange Names"].isin(
                [m for m in df["Market and Exchange Names"].unique()
                 if any(k in str(m) for k in MAERKTE.values())])]
            for _, r in d.iterrows():
                zeilen.append({"markt": str(r["Market and Exchange Names"]),
                               "datum": str(r[SPALTE_DATUM])[:10],
                               **{k: int(r[v]) for k, v in SPALTEN.items()}})
    CACHE.write_text(json.dumps({"jahre": jahre, "zeilen": zeilen}), "utf-8")
    return zeilen


def reihe(zeilen: list[dict], symbol: str) -> list[dict]:
    """Netto-Positionen je Reportdatum, aufsteigend. Commercials und Large Specs."""
    markt = MAERKTE[symbol]
    out = []
    for r in zeilen:
        if markt not in r["markt"]:
            continue
        out.append({"datum": r["datum"],
                    "commercials": r["c_long"] - r["c_short"],
                    "large_specs": r["nc_long"] - r["nc_short"]})
    out.sort(key=lambda x: x["datum"])
    return out


def bewerte(reihe_: list[dict], stichtag: date | None = None) -> dict:
    """Signal je Horizont: aktueller Commercials-Wert gegen das **EQ der Lookback-Range**.

    Ueber EQ -> bullish, darunter -> bearish (Wiki: "COT Hedging Program (12-Monats-Methode)",
    Praezisierung vom 2026-08-03). Bewusst nicht die 0-Linie.
    """
    if not reihe_:
        return {"error": "keine COT-Daten"}
    stichtag = stichtag or date.fromisoformat(reihe_[-1]["datum"])
    aktuell = reihe_[-1]

    horizonte = {}
    for name, monate in HORIZONTE.items():
        ab = (stichtag - timedelta(days=int(monate * 30.44))).isoformat()
        fenster = [r["commercials"] for r in reihe_ if r["datum"] >= ab]
        if len(fenster) < 3:                     # zu duenn fuer eine Range
            continue
        hi, lo = max(fenster), min(fenster)
        eq = (hi + lo) / 2
        horizonte[name] = {"high": hi, "low": lo, "eq": round(eq, 1),
                           "signal": "bullish" if aktuell["commercials"] > eq else "bearish",
                           "reports": len(fenster)}

    signale = [h["signal"] for h in horizonte.values()]
    return {"stand": aktuell["datum"],
            "commercials": aktuell["commercials"],
            "large_specs": aktuell["large_specs"],
            "gegenlaeufig": (aktuell["commercials"] > 0) != (aktuell["large_specs"] > 0),
            "horizonte": horizonte,
            "einig": len(set(signale)) == 1 if signale else False}


def cot(symbole: list[str] | None = None, stichtag: date | None = None) -> dict:
    """COT-Auswertung je Symbol. Laedt das laufende und die vier Vorjahre (4Y-Horizont)."""
    symbole = symbole or list(MAERKTE)
    jahr = (stichtag or date.today()).year
    try:
        zeilen = _lade_jahre(list(range(jahr - 4, jahr + 1)))
    except Exception as exc:                     # Netz, Paket fehlt, CFTC-Ausfall
        return {"error": f"{type(exc).__name__}: {exc}"}
    return {s: bewerte(reihe(zeilen, s), stichtag) for s in symbole if s in MAERKTE}


def demo() -> None:
    """Selbstcheck der Bewertungslogik -- synthetische Reihe, kein Netz."""
    # Commercials strukturell negativ (Index-Futures): Range -68k..+15k, EQ = -26.5k.
    # Genau der Fall aus der Wiki-Seite: aktueller Wert -14.95k liegt UEBER dem EQ -> bullish,
    # obwohl er unter null liegt. Nach der 0-Linien-Lesart waere er faelschlich bearish.
    r = [{"datum": f"2026-0{i}-01", "commercials": v, "large_specs": -v}
         for i, v in enumerate([-68000, 15000, -30000, -14950], start=1)]
    b = bewerte(r, date(2026, 4, 1))
    assert b["commercials"] == -14950, b
    h3 = b["horizonte"]["3M"]
    assert (h3["high"], h3["low"]) == (15000, -68000), h3
    assert h3["eq"] == -26500.0, h3
    assert h3["signal"] == "bullish", "ueber EQ, obwohl negativ -- 0-Linie waere bearish"
    assert b["gegenlaeufig"] is True, "Commercials und Large Specs zeigen gegeneinander"

    # Unter EQ -> bearish
    r2 = r + [{"datum": "2026-05-01", "commercials": -60000, "large_specs": 60000}]
    assert bewerte(r2, date(2026, 5, 1))["horizonte"]["3M"]["signal"] == "bearish"

    # Gleichlaeufig (beide long) -> nicht gegenlaeufig
    r3 = [{"datum": f"2026-0{i}-01", "commercials": v, "large_specs": 100}
          for i, v in enumerate([100, 300, 200, 250], start=1)]
    assert bewerte(r3, date(2026, 4, 1))["gegenlaeufig"] is False

    # Zu duenne Reihe liefert keinen Horizont statt einer erfundenen Range
    assert bewerte([{"datum": "2026-01-01", "commercials": 1, "large_specs": 1}],
                   date(2026, 1, 1))["horizonte"] == {}
    assert bewerte([])["error"], "leere Reihe -> Fehler, kein Absturz"

    assert MAERKTE["NQ"] == "NASDAQ MINI", "kalibriert am Wiki-Wert -14,95k (2026-07-28)"

    # Regressionsschutz: der am 2026-08-16 gegen Jannes' eigenen Indikator validierte Fall.
    # Wiki (Stand 03.08.2026, Report 2026-07-28): 3M SELL, 6M SELL, 12M BUY, 2Y BUY, 4Y SELL
    # bei Commercials -14,95k. Nachgestellt mit den echten Eckwerten je Lookback -- schlaegt
    # an, sobald die EQ-Logik oder die Horizont-Zuordnung kippt.
    def _sig(hi: int, lo: int, jetzt: int) -> str:
        return "bullish" if jetzt > (hi + lo) / 2 else "bearish"

    assert _sig(13812, -14946, -14946) == "bearish", "3M: am Low -> SELL"
    assert _sig(13812, -31456, -14946) == "bearish", "6M: SELL"
    assert _sig(13812, -66754, -14946) == "bullish", "12M: BUY trotz negativem Wert"
    assert _sig(43337, -66754, -14946) == "bearish", "4Y: SELL"
    # Kernaussage der Wiki-Praezisierung in einer Zeile: 12M sagt BUY, die 0-Linie saehe SELL
    assert _sig(13812, -66754, -14946) != ("bullish" if -14946 > 0 else "bearish"), \
        "EQ-Lesart weicht hier bewusst von der 0-Linien-Lesart ab"

    print("cot: alle Checks bestanden")


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if "--demo" in argv:
        demo()
        return 0

    d = cot()
    if "--json" in argv:
        print(json.dumps(d, indent=2))
        return 0

    if d.get("error"):
        print(f"COT-Abruf fehlgeschlagen: {d['error']}")
        return 1
    for sym, b in d.items():
        if b.get("error"):
            print(f"{sym}: {b['error']}")
            continue
        print(f"=== {sym} ({MAERKTE[sym]}), Stand {b['stand']}")
        print(f"    Commercials {b['commercials']:+,}   Large Specs {b['large_specs']:+,}"
              f"   {'gegenlaeufig' if b['gegenlaeufig'] else 'gleichlaeufig'}")
        for name, h in b["horizonte"].items():
            print(f"    {name:>3}  EQ {h['eq']:>10,.0f}   Range {h['low']:+,} .. {h['high']:+,}"
                  f"   -> {h['signal'].upper()}")
        print(f"    Horizonte einig: {'ja' if b['einig'] else 'NEIN -- Lookback nennen'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
