#!/usr/bin/env python3
"""Praezisions-Layer fuer Forex-$-P&L -- das Gegenstueck zu algo/pnl.py, das dort fuer Futures
den Punktwert liefert (MNQ = $2/Punkt). Bei Forex ist der Gegenwert einer Kursbewegung nicht
konstant: er haengt an der Quote-Waehrung und damit am Wechselkurs ZUM TRADE-ZEITPUNKT.

Warum ein eigenes Modul und nicht algo/pnl.py mit anderem Parameter (Spec §4.3/§5.7):
  - `pnl.risk_size()` liefert ein `int` (Kontraktzahl). Forex handelt in Lots mit 0,01-Schritten,
    also einem gerundeten `float` -- ein Rueckgabetyp-Unterschied, kein Parameterwert.
  - `pnl.POINT_VALUE` ist eine Konstante je Symbol. Der Pip-Wert ist hier eine FUNKTION von
    Symbol und Zeitpunkt.
  - algo/pnl.py wird laut Nutzerentscheidung nicht angefasst.

Kern der Umrechnung (Spec §5.1): der Pip-Wert entsteht in der QUOTE-Waehrung und wird von dort
nach USD gebracht. Alle dafuer noetigen Referenzkurse liegen im eigenen Bestand.

Aufruf (Selbstcheck):
    python algo/forex/pnl.py
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "tools"))
from analyze_ohlc import PIP_SIZE, TICK_SIZE, to_tick  # noqa: E402

# Standardlot = 100.000 Einheiten der Basiswaehrung. Micro-Lot (0,01) = 1.000 Einheiten und
# damit die kleinste handelbare Groesse -- daraus folgt LOT_STEP.
LOT_UNITS = 100_000
LOT_STEP = 0.01

# Konservativ am oberen Rand retail-typischer ECN-Spreads (Spec §5.3). GESETZT, NICHT GEMESSEN:
# der histdata-Bestand ist reines Bid, ein echter Spread steht nicht darin. Deshalb ist nicht
# der $-P&L die entscheidende Kennzahl, sondern der Break-even-Spread (siehe unten).
SPREAD_PIPS = {
    "EURUSD": 0.6, "USDJPY": 0.7, "GBPUSD": 0.9, "AUDUSD": 0.8, "USDCHF": 1.0,
    "USDCAD": 1.2, "EURGBP": 1.1, "EURJPY": 1.3, "GBPJPY": 2.2, "NZDUSD": 1.4,
}

# $ je Standardlot und Round-Turn (ECN-typisch). Auf 0 setzbar fuer ein reines Spread-Broker-
# Modell. Default bewusst nicht 0: auf der MNQ-Seite fiel die Kommission im Audit vom
# 2026-08-06 komplett unter den Tisch und machte die Zahlen um eine Groessenordnung zu
# optimistisch (siehe algo/pnl.py::real_pnl).
COMMISSION_PER_LOT_RT = 7.0


def quote_ccy(symbol: str) -> str:
    return symbol[3:6]


def base_ccy(symbol: str) -> str:
    return symbol[0:3]


def pip_value_usd(symbol: str, kurse: dict[str, float]) -> float | None:
    """$-Wert eines Pips je STANDARDLOT, zum Zeitpunkt der uebergebenen `kurse`.

    `kurse` ist ein Schnappschuss {Symbol: Kurs} -- mindestens die Referenz, die dieses Paar
    braucht. Rueckgabe None, wenn die noetige Referenz fehlt; der Aufrufer verwirft den Trade
    dann und zaehlt ihn, statt zu naehern (Spec §5.1, "Marktdaten wie Gold"-Nulltoleranz auf
    abgeleitete Groessen).

    Eine Regel deckt alle drei Faelle ab, weil der Pip-Wert AUSSCHLIESSLICH an der
    Quote-Waehrung haengt, nie an der Basis:

        pip_wert_quote = PIP_SIZE * LOT_UNITS
        Quote == USD          -> fertig                    (EURUSD: 0,0001*100k = $10)
        es gibt <QUOTE>USD    -> * Kurs                    (EURGBP ueber GBPUSD)
        es gibt USD<QUOTE>    -> / Kurs                    (USDJPY/EURJPY/GBPJPY ueber USDJPY)

    Der USD/XXX-Fall (USDJPY, USDCHF, USDCAD) ist dabei kein Sonderfall, sondern faellt in die
    dritte Zeile mit sich selbst als Referenz -- deshalb steht hier eine Regel und keine
    Fallunterscheidung nach Paar-Typ.
    """
    if symbol not in PIP_SIZE:
        raise ValueError(f"Keine PIP_SIZE fuer {symbol!r} hinterlegt "
                         f"(tools/analyze_ohlc.py::PIP_SIZE)")
    pv_quote = PIP_SIZE[symbol] * LOT_UNITS
    quote = quote_ccy(symbol)
    if quote == "USD":
        return pv_quote

    direkt = f"{quote}USD"      # z.B. GBPUSD fuer EURGBP
    invers = f"USD{quote}"      # z.B. USDJPY fuer EURJPY -- und fuer USDJPY selbst
    if direkt in kurse and kurse[direkt] > 0:
        return pv_quote * kurse[direkt]
    if invers in kurse and kurse[invers] > 0:
        return pv_quote / kurse[invers]
    return None


def pips(symbol: str, von: float, bis: float) -> float:
    """Preisdifferenz in Pips (vorzeichenbehaftet)."""
    return (bis - von) / PIP_SIZE[symbol]


def spread_preis(symbol: str, spread_pips: float | None = None) -> float:
    """Spread in Preiseinheiten statt Pips -- fuer die Ask-Rekonstruktion aus Bid-Daten."""
    sp = SPREAD_PIPS[symbol] if spread_pips is None else spread_pips
    return sp * PIP_SIZE[symbol]


def ask(bid: float, symbol: str, spread_pips: float | None = None) -> float:
    """Ask aus dem Bid-Bestand. Gebraucht fuer die Short-Stop-Asymmetrie (Spec §5.2): ein
    Short-Stop loest beim Ask aus, also `Spread` frueher, als die Bid-Kerze aussehen laesst.
    Ohne diese Rekonstruktion fallen Short-Ergebnisse systematisch zu gut aus."""
    return bid + spread_preis(symbol, spread_pips)


def round_to_lot(lots: float) -> float:
    """Auf LOT_STEP ABGERUNDET, nie auf. Gleiche Haltung wie die gerichtete Tick-Rundung in
    algo/pnl.py::round_to_tick: die Rundung darf nie zugunsten des Backtests ausfallen --
    eine aufgerundete Position wuerde mehr Risiko tragen als das Budget hergibt.

    Das `round(..., 9)` vor dem `floor` ist kein Kosmetik-Schritt: LOT_STEP=0,01 ist binaer
    nicht exakt darstellbar, `5.0 / 0.01` ergibt 499,99999999999994, und ein nacktes `floor`
    macht daraus 4,99 Lots statt 5,00 -- ein stiller Sizing-Fehler von 0,2 %, der sich ueber
    einen Backtest aufsummiert. Neun Nachkommastellen liegen weit ueber jeder realen
    Lot-Granularitaet und weit unter dem Float-Rauschen."""
    if lots <= 0:
        return 0.0
    schritte = math.floor(round(lots / LOT_STEP, 9))
    return round(schritte * LOT_STEP, 2)


def round_to_tick(price: float, symbol: str, mode: str = "nearest") -> float:
    """Duenner Wrapper um analyze_ohlc.to_tick(), damit die Forex-Module nur dieses Modul
    kennen muessen -- bewusst NICHT ueber algo/pnl.py::round_to_tick, weil algo/pnl.py
    unangetastet bleiben soll. TICK_SIZE fuehrt die Forex-Paare bereits (0,00001 Majors,
    0,001 JPY-Paare)."""
    if symbol not in TICK_SIZE:
        raise ValueError(f"Keine TICK_SIZE fuer {symbol!r} hinterlegt")
    return to_tick(price, symbol, mode)


def lot_size(equity: float, max_risk_pct: float, entry: float, stop: float,
             symbol: str, kurse: dict[str, float],
             max_notional: float | None = None) -> float:
    """Lots, sodass ein Stop-Out genau `max_risk_pct` von `equity` in ECHTEN Dollar kostet.

    Analog zu algo/pnl.py::risk_size, aber mit Lot-Granularitaet statt Kontraktzahl und mit
    zeitpunktabhaengigem Pip-Wert statt konstantem Punktwert. Rueckgabe 0.0, wenn der Pip-Wert
    mangels Referenzkurs nicht bestimmbar ist -- der Aufrufer erkennt daran den zu
    verwerfenden Trade.

    `max_notional` (optional, = equity * Hebel) deckelt zusaetzlich: LOT_UNITS Einheiten der
    Basiswaehrung je Lot, bewertet in USD.
    """
    pv = pip_value_usd(symbol, kurse)
    if pv is None or pv <= 0:
        return 0.0
    dist = abs(entry - stop) / PIP_SIZE[symbol]
    if dist <= 0:
        return 0.0
    lots = (equity * max_risk_pct) / (dist * pv)

    if max_notional is not None:
        # Notional je Lot in USD: LOT_UNITS Basiswaehrung. Fuer XXXUSD ist der Kurs selbst der
        # USD-Wert der Basis; fuer USDXXX ist die Basis bereits USD.
        if base_ccy(symbol) == "USD":
            notional_je_lot = LOT_UNITS
        else:
            basis_usd = kurse.get(f"{base_ccy(symbol)}USD")
            if basis_usd is None:
                # Basis-in-USD nicht direkt bekannt: ueber den eigenen Kurs und den Pip-Wert
                # laesst sich das nicht sauber ableiten -> Deckel konservativ ueber den
                # Rohkurs, das ist die vorsichtigere Annahme.
                basis_usd = entry
            notional_je_lot = LOT_UNITS * basis_usd
        deckel = (max_notional * 0.95) / notional_je_lot
        lots = min(lots, deckel)

    return round_to_lot(lots)


def brutto_usd(symbol: str, side: str, entry: float, exit_: float, lots: float,
               kurse: dict[str, float]) -> float | None:
    """BRUTTO-$-Ergebnis aus zwei Fuellpreisen, ohne jede Kostenannahme. None, wenn der
    Pip-Wert nicht bestimmbar ist.

    Diese Funktion trifft KEINE Aussage darueber, auf welcher Marktseite die beiden Preise
    liegen -- das ist Sache des Aufrufers. algo/forex/backtest.py arbeitet mit echten
    Fuellpreisen (Kauf zum Ask, Verkauf zum Bid), da steckt der Spread bereits drin und darf
    nicht erneut abgezogen werden. `real_pnl_usd()` unten ist die andere Konvention.
    """
    pv = pip_value_usd(symbol, kurse)
    if pv is None:
        return None
    bewegung = pips(symbol, entry, exit_) if side == "long" else pips(symbol, exit_, entry)
    return bewegung * pv * lots


def real_pnl_usd(symbol: str, side: str, entry: float, exit_: float, lots: float,
                 kurse: dict[str, float], spread_pips: float | None = None,
                 commission_per_lot_rt: float = COMMISSION_PER_LOT_RT) -> float | None:
    """NETTO-$-Ergebnis eines Round-Trips aus ROHEN BID-Preisen. None, wenn der Pip-Wert nicht
    bestimmbar ist.

    Konvention hier: `entry` und `exit_` sind Bid-Preise, so wie sie im Bestand stehen, und die
    Spread-Kosten werden genau EINMAL explizit abgezogen. Fuer Ueberschlagsrechnungen auf
    Rohdaten.

    ⚠️ NICHT fuer Fuellpreise aus algo/forex/backtest.py verwenden -- dort liegen Kauf- und
    Verkaufspreis bereits auf den richtigen Marktseiten (Ask bzw. Bid), der Spread ist also
    schon bezahlt. Dafuer `brutto_usd()` nehmen und nur die Kommission abziehen. Zwei
    Konventionen nebeneinander sind eine Fehlerquelle; sie stehen hier bewusst getrennt und
    benannt, statt implizit in einer Funktion vermischt zu werden.
    """
    b = brutto_usd(symbol, side, entry, exit_, lots, kurse)
    if b is None:
        return None
    pv = pip_value_usd(symbol, kurse)
    assert pv is not None  # brutto_usd waere sonst None gewesen
    sp = SPREAD_PIPS[symbol] if spread_pips is None else spread_pips
    return b - sp * pv * lots - commission_per_lot_rt * lots


def break_even_spread(lauf, symbol: str, obergrenze: float = 20.0,
                      toleranz: float = 0.01) -> float | None:
    """Der Spread in Pips, bei dem das Netto-Ergebnis auf 0 kippt -- Pflichtkennzahl jedes
    Forex-Reports (Spec §5.4).

    NUMERISCH bestimmt, nicht analytisch. Der naheliegende Ansatz "Brutto-Pips / Trade-Anzahl"
    ist falsch, weil der Spread ueber die Short-Stop-Asymmetrie mitbestimmt, WELCHE Trades
    ueberhaupt ausgestoppt werden -- die Trade-Menge ist selbst spread-abhaengig. Deshalb
    bekommt diese Funktion den kompletten Backtest als Callable und sucht die Nullstelle per
    Bisektion.

    `lauf(spread_pips) -> float` liefert den Netto-$-P&L bei diesem Spread.
    Rueckgabe None, wenn schon bei Spread 0 kein Gewinn steht (dann gibt es keinen
    Break-even) oder wenn die Reihe bis `obergrenze` positiv bleibt.
    """
    unten, oben = 0.0, obergrenze
    if lauf(unten) <= 0:
        return None            # schon ohne Kosten im Minus
    if lauf(oben) > 0:
        return None            # traegt mehr als obergrenze Pips -- Angabe waere irrefuehrend
    while oben - unten > toleranz:
        mitte = (unten + oben) / 2
        if lauf(mitte) > 0:
            unten = mitte
        else:
            oben = mitte
    return round((unten + oben) / 2, 2)


def demo() -> None:
    """Selbstcheck nach Spec §6.5. Reine Rechenpruefungen, keine Dateien noetig."""
    # --- Pip-Wert, drei Faelle aus Spec §5.1 -------------------------------------------
    # Fall 1: Quote ist USD -> konstant $10 je Standardlot, unabhaengig vom Kurs.
    assert abs(pip_value_usd("EURUSD", {}) - 10.0) < 1e-9
    assert abs(pip_value_usd("GBPUSD", {"GBPUSD": 1.27}) - 10.0) < 1e-9
    assert abs(pip_value_usd("AUDUSD", {}) - 10.0) < 1e-9

    # Fall 2: Basis ist USD -> Referenz ist das Paar selbst.
    # USDJPY bei 150: 0,01 * 100.000 = 1.000 JPY / 150 = $6,667
    pv = pip_value_usd("USDJPY", {"USDJPY": 150.0})
    assert pv is not None and abs(pv - 1000 / 150) < 1e-9, pv
    # USDCAD bei 1,36: 10 CAD / 1,36 = $7,353
    pv = pip_value_usd("USDCAD", {"USDCAD": 1.36})
    assert pv is not None and abs(pv - 10 / 1.36) < 1e-9, pv

    # Fall 3: Cross -> Referenz ist ein DRITTES Paar.
    # EURGBP: 10 GBP * GBPUSD(1,27) = $12,70
    pv = pip_value_usd("EURGBP", {"GBPUSD": 1.27})
    assert pv is not None and abs(pv - 12.7) < 1e-9, pv
    # EURJPY/GBPJPY: 1.000 JPY / USDJPY(150) = $6,667 -- identisch, weil nur die Quote zaehlt
    a = pip_value_usd("EURJPY", {"USDJPY": 150.0})
    b = pip_value_usd("GBPJPY", {"USDJPY": 150.0})
    assert a is not None and b is not None and abs(a - b) < 1e-9, (a, b)
    assert abs(a - 1000 / 150) < 1e-9, a

    # Fehlende Referenz -> None (Trade wird verworfen, nicht genaehert).
    assert pip_value_usd("EURJPY", {}) is None
    assert pip_value_usd("EURGBP", {"USDJPY": 150.0}) is None

    # --- Lot-Rundung: immer ab, nie auf ------------------------------------------------
    assert abs(round_to_lot(0.0349) - 0.03) < 1e-9, round_to_lot(0.0349)
    assert abs(round_to_lot(0.0399) - 0.03) < 1e-9, round_to_lot(0.0399)
    assert round_to_lot(0.009) == 0.0, "unter einem Micro-Lot ist keine Position handelbar"
    assert round_to_lot(-1) == 0.0
    # Regressionswaechter fuer das Float-Artefakt: 5,0 / 0,01 ist binaer 499,99999999999994,
    # ein nacktes floor() lieferte hier 4,99 statt 5,00.
    assert abs(round_to_lot(5.0) - 5.0) < 1e-9, round_to_lot(5.0)
    assert abs(round_to_lot(0.07) - 0.07) < 1e-9, round_to_lot(0.07)
    assert abs(round_to_lot(1.23) - 1.23) < 1e-9, round_to_lot(1.23)

    # --- Sizing: 1 % von 100k bei 20 Pips Stop auf EURUSD ------------------------------
    # Budget $1.000, Verlust je Lot = 20 Pips * $10 = $200 -> 5,0 Lots
    lots = lot_size(100_000, 0.01, 1.1000, 1.0980, "EURUSD", {})
    assert abs(lots - 5.0) < 1e-9, lots
    # Fehlende Referenz -> 0.0 statt Naeherung
    assert lot_size(100_000, 0.01, 160.00, 159.80, "EURJPY", {}) == 0.0
    # Stop == Entry -> keine Position (Division durch 0 vermieden)
    assert lot_size(100_000, 0.01, 1.1, 1.1, "EURUSD", {}) == 0.0

    # --- Ask-Rekonstruktion -------------------------------------------------------------
    # EURUSD mit 0,6 Pips: Ask liegt 0,00006 ueber dem Bid
    assert abs(ask(1.10000, "EURUSD") - 1.10006) < 1e-12, ask(1.10000, "EURUSD")
    # JPY-Paar: 1,3 Pips = 0,013 (PIP_SIZE 0,01)
    assert abs(ask(160.000, "EURJPY") - 160.013) < 1e-9, ask(160.000, "EURJPY")

    # --- $-P&L: Kosten fallen genau einmal an ------------------------------------------
    # Long EURUSD 1,1000 -> 1,1020 = +20 Pips, 1 Lot: brutto $200
    # minus Spread 0,6 Pips ($6) minus Kommission ($7) = $187
    p = real_pnl_usd("EURUSD", "long", 1.1000, 1.1020, 1.0, {})
    assert p is not None and abs(p - 187.0) < 1e-9, p
    # Short spiegelbildlich: 1,1020 -> 1,1000 ist ebenfalls +20 Pips
    p = real_pnl_usd("EURUSD", "short", 1.1020, 1.1000, 1.0, {})
    assert p is not None and abs(p - 187.0) < 1e-9, p
    # Ohne Kosten waeren es glatt $200 -- belegt, dass nichts doppelt gezaehlt wird
    p = real_pnl_usd("EURUSD", "long", 1.1000, 1.1020, 1.0, {},
                     spread_pips=0.0, commission_per_lot_rt=0.0)
    assert p is not None and abs(p - 200.0) < 1e-9, p
    # Fehlende Referenz -> None
    assert real_pnl_usd("EURJPY", "long", 160.0, 160.2, 1.0, {}) is None

    # --- Break-even-Spread --------------------------------------------------------------
    # Kunstlauf: 10 Trades, brutto 30 Pips Gewinn, Kosten linear -> Nullstelle bei 3 Pips.
    def kunstlauf(sp: float) -> float:
        return (30.0 - 10.0 * sp) * 10.0
    be = break_even_spread(kunstlauf, "EURUSD")
    assert be is not None and abs(be - 3.0) < 0.02, be
    # Schon bei Spread 0 im Minus -> kein Break-even
    assert break_even_spread(lambda sp: -1.0, "EURUSD") is None
    # Traegt mehr als die Obergrenze -> keine irrefuehrende Angabe
    assert break_even_spread(lambda sp: 1.0, "EURUSD") is None

    print("forex.pnl demo: OK")


if __name__ == "__main__":
    demo()
