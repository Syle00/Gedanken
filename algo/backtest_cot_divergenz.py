#!/usr/bin/env python3
"""Backtest: Sagt eine COT-Divergenz zwischen NQ und ES etwas ueber die Folgewoche?

Anlass: Am Report 2026-08-11 standen NQ-Commercials netto **long** (alle Horizonte bullish),
ES-Commercials netto **short** (alle bearish) -- eine Divergenz auf Positionierungsebene,
analog zu SMT auf Preisebene. Die These wurde in `Weekly Bias KW34 2026.md` als
Beobachtungsauftrag notiert; hier wird sie geprueft statt geglaubt (CLAUDE.md: jede These wird
gebacktestet, auch wenn das Ergebnis der These widerspricht).

**These:** Zeigen NQ und ES im COT gegeneinander (nach der EQ-Lesart aus
`wiki/concepts/COT (Commitment of Traders) Data.md`), dann laeuft in der Folgewoche das Symbol
mit dem bullishen Signal besser als das mit dem bearishen -- messbar als Spread der
Wochen-Returns.

**Micro/Mini strikt getrennt** (Nutzervorgabe 2026-08-16): gerechnet wird ausschliesslich auf
NQ und ES, nie auf MNQ/MES. Der COT-Report fuehrt beide Familien getrennt, und ein
Micro-Datensatz als Mini-Ersatz hat am 2026-08-16 bereits ein Signal umgekehrt.

**Zeitachse, kein Lookahead:** Der Report traegt den Stand *Dienstag*, veroeffentlicht wird er
*Freitag* nach Boersenschluss. Gehandelt werden kann er also fruehestens ab dem darauffolgenden
Montag. Genau so wird gemessen: Signal aus Report der Woche W -> Return der Woche W+1
(Montag-Open bis Freitag-Close), nie der Woche, in der der Report erschien.

Aufruf:
    python algo/backtest_cot_divergenz.py            # Bericht
    python algo/backtest_cot_divergenz.py --demo     # Selbstcheck
"""

from __future__ import annotations

import statistics
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

HORIZONT = "12M"          # Leithorizont der Wiki-Methode ("COT Hedging Program, 12 Monate")


def wochen_returns(symbol: str) -> dict:
    """{ISO-Woche: Return in %} aus Montag-Open bis Freitag-Close der jeweiligen Woche."""
    from backtest_common import load_rows

    je_woche: dict = {}
    for r in load_rows(symbol):
        je_woche.setdefault(r["day"].isocalendar()[:2], []).append(r)
    out = {}
    for kw, tage in je_woche.items():
        tage.sort(key=lambda x: x["day"])
        if len(tage) < 3:                      # angebrochene Woche -> nicht vergleichbar
            continue
        o, c = tage[0]["open"], tage[-1]["close"]
        if o:
            out[kw] = 100 * (c - o) / o
    return out


def signale(symbol: str, zeilen: list) -> dict:
    """{Reportdatum: 'bullish'|'bearish'} nach der EQ-Lesart, Leithorizont HORIZONT."""
    import cot as c

    r = c.reihe(zeilen, symbol)
    out = {}
    for i in range(len(r)):
        b = c.bewerte(r[:i + 1], date.fromisoformat(r[i]["datum"]))
        h = b.get("horizonte", {}).get(HORIZONT)
        if h:
            out[r[i]["datum"]] = h["signal"]
    return out


def auswerten(nq_sig: dict, es_sig: dict, nq_ret: dict, es_ret: dict) -> dict:
    """Paart jedes Reportdatum mit der **Folgewoche** und trennt Divergenz von Gleichlauf."""
    divergenz, gleichlauf = [], []
    for datum, s_nq in sorted(nq_sig.items()):
        s_es = es_sig.get(datum)
        if not s_es:
            continue
        # Report-Stand ist Dienstag; handelbar ab Montag darauf -> Woche des Datums + 1 Woche
        folge = (datetime.fromisoformat(datum).date() + timedelta(days=7)).isocalendar()[:2]
        if folge not in nq_ret or folge not in es_ret:
            continue
        spread = nq_ret[folge] - es_ret[folge]
        if s_nq == s_es:
            gleichlauf.append(spread)
            continue
        # Divergenz: Vorzeichen so drehen, dass "These trifft zu" immer positiv ist --
        # das bullishe Symbol soll besser laufen als das bearishe.
        divergenz.append(spread if s_nq == "bullish" else -spread)

    def kennz(werte: list, name: str) -> dict:
        if not werte:
            return {"name": name, "n": 0}
        treffer = sum(1 for w in werte if w > 0)
        return {"name": name, "n": len(werte),
                "trefferquote_pct": round(100 * treffer / len(werte), 1),
                "avg_spread_pct": round(statistics.fmean(werte), 3),
                "median_spread_pct": round(statistics.median(werte), 3),
                "stdev": round(statistics.stdev(werte), 3) if len(werte) > 1 else None}

    return {"divergenz": kennz(divergenz, "Divergenz (These)"),
            "gleichlauf": kennz(gleichlauf, "Gleichlauf (Kontrollgruppe)"),
            "roh_divergenz": divergenz}


def demo() -> None:
    # Folgewoche, nicht Report-Woche: Report vom Di 2026-08-11 (KW33) -> Return KW34
    nq_sig = {"2026-08-11": "bullish"}
    es_sig = {"2026-08-11": "bearish"}
    nq_ret = {(2026, 33): 5.0, (2026, 34): 2.0}
    es_ret = {(2026, 33): -5.0, (2026, 34): 1.0}
    r = auswerten(nq_sig, es_sig, nq_ret, es_ret)
    assert r["divergenz"]["n"] == 1, r
    assert r["divergenz"]["avg_spread_pct"] == 1.0, "KW34-Spread 2.0-1.0, nicht KW33"

    # Vorzeichendrehung: ist ES das bullishe Symbol, zaehlt ES-minus-NQ als Treffer
    r2 = auswerten({"2026-08-11": "bearish"}, {"2026-08-11": "bullish"},
                   {(2026, 34): 1.0}, {(2026, 34): 3.0})
    assert r2["divergenz"]["avg_spread_pct"] == 2.0, r2
    assert r2["divergenz"]["trefferquote_pct"] == 100.0, r2

    # Gleichlauf landet in der Kontrollgruppe, nicht in der These
    r3 = auswerten({"2026-08-11": "bullish"}, {"2026-08-11": "bullish"},
                   {(2026, 34): 1.0}, {(2026, 34): 3.0})
    assert r3["divergenz"]["n"] == 0 and r3["gleichlauf"]["n"] == 1, r3

    # Fehlende Folgewoche wird uebersprungen statt geraten
    assert auswerten({"2026-08-11": "bullish"}, {"2026-08-11": "bearish"},
                     {(2026, 33): 1.0}, {(2026, 33): 1.0})["divergenz"]["n"] == 0

    # Ein Spread von exakt 0 gilt nicht als Treffer (> 0, nicht >= 0)
    r4 = auswerten({"2026-08-11": "bullish"}, {"2026-08-11": "bearish"},
                   {(2026, 34): 1.0}, {(2026, 34): 1.0})
    assert r4["divergenz"]["trefferquote_pct"] == 0.0, r4
    print("backtest_cot_divergenz: alle Checks bestanden")


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if "--demo" in argv:
        demo()
        return 0

    import cot as c

    jahr = date.today().year
    zeilen = c._lade_jahre(list(range(jahr - 4, jahr + 1)))
    nq_sig, es_sig = signale("NQ", zeilen), signale("ES", zeilen)
    nq_ret, es_ret = wochen_returns("NQ"), wochen_returns("ES")

    r = auswerten(nq_sig, es_sig, nq_ret, es_ret)
    print(f"COT-Divergenz NQ vs ES, Leithorizont {HORIZONT}")
    print(f"Reports gepaart: {len(set(nq_sig) & set(es_sig))} | "
          f"Wochen-Returns: NQ {len(nq_ret)}, ES {len(es_ret)}")
    print("Signal aus Report der Woche W -> Return der Woche W+1 (kein Lookahead)\n")
    for k in ("divergenz", "gleichlauf"):
        g = r[k]
        if not g["n"]:
            print(f"  {g['name']}: keine Faelle")
            continue
        print(f"  {g['name']}: n={g['n']}, Trefferquote {g['trefferquote_pct']} %, "
              f"Ø-Spread {g['avg_spread_pct']} %, Median {g['median_spread_pct']} %, "
              f"stdev {g['stdev']}")
    d = r["divergenz"]
    if d["n"]:
        print(f"\nEinordnung: bei reinem Zufall waeren ~50 % erwartbar. Gemessen "
              f"{d['trefferquote_pct']} % bei n={d['n']}.")
        if d["n"] < 30:
            print("  ACHTUNG: n < 30 -- fuer eine belastbare Aussage zu wenige Faelle.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
