#!/usr/bin/env python3
"""Trade-Simulation fuer die Forex-Regeln (Spec §6.2) -- der Zwilling zu algo/backtest_bt.py.

WARUM EIN EIGENER SIMULATOR STATT DER `backtesting`-BIBLIOTHEK
--------------------------------------------------------------
Die MNQ-Seite laeuft auf `backtesting` plus der Praezisionsschicht algo/pnl.py, weil die Lib
alles wie eine Aktie preist (P&L = Preisdifferenz * Stueckzahl). Fuer Forex kaemen zu diesem
einen Bruch drei weitere dazu, die sich in der Lib nicht ohne Preis-Hacks ausdruecken lassen:

  1. Der Pip-Wert ist keine Konstante, sondern haengt am Wechselkurs zum Trade-Zeitpunkt.
  2. Kauf und Verkauf liegen auf verschiedenen Marktseiten (Ask/Bid) -- ein Short-Stop loest
     frueher aus, als die Bid-Kerze zeigt.
  3. Positionsgroessen sind Lots in 0,01-Schritten, keine ganzzahligen Kontrakte.

Punkt 2 liesse sich nur ueber verschobene Stop-Preise nachbauen, was dann wiederum die
P&L-Rechnung der Lib verfaelscht. Ein expliziter Bar-Walk ist hier das ehrlichere Werkzeug:
er macht die Fill-Annahmen sichtbar, statt sie in einer fremden Order-Engine zu verstecken.
CLAUDE.md ordnet Korrektheit ueber Wiederverwendung ("Korrektheit vor Features, weil reales
Geld geplant ist").

Konsequenz: von algo/validate.py sind `monte_carlo()` und `double_bootstrap_drawdown()`
weiter direkt nutzbar (sie arbeiten auf reinen Zahlenreihen); `run()`/`walk_forward()` sind an
`Backtest(...)` gebunden und werden hier durch `walk_forward()` unten ersetzt.

FILL-KONVENTION (Spec §5.2)
---------------------------
Der Bestand ist Bid. Ask = Bid + Spread. Jede Seite wird dort gefuellt, wo ein Broker fuellen
wuerde -- dadurch faellt der Spread automatisch genau einmal an, und die Short-Asymmetrie
ergibt sich von selbst statt als Zuschlag:

  Long   Entry  Limit-Kauf bei E   -> fuellt, wenn Ask <= E, also Bid <= E - s.  Fill: E
         Stop   Verkauf bei S      -> ausgeloest, wenn Bid <= S.                 Fill: S
         Ziel   Verkauf bei T      -> ausgeloest, wenn Bid >= T.                 Fill: T
  Short  Entry  Limit-Verkauf bei E-> fuellt, wenn Bid >= E.                     Fill: E
         Stop   Kauf bei S         -> ausgeloest, wenn Ask >= S, also Bid >= S-s. Fill: S
         Ziel   Kauf bei T         -> ausgeloest, wenn Ask <= T, also Bid <= T-s. Fill: T

Der Short-Stop trifft damit `s` Pips frueher und das Short-Ziel `s` Pips spaeter als eine
naive Bid-Betrachtung -- beides zuungunsten des Backtests, also konservativ.

KONSERVATIVE FILL-REIHENFOLGE
-----------------------------
Liegen Stop UND Ziel in der Spanne derselben Kerze, ist aus OHLC nicht entscheidbar, was
zuerst kam. Dann wird der STOP gewertet und der Trade als `dubious` gezaehlt. `dubious_pct`
ist Pflichtkennzahl jedes Reports, wie auf der MNQ-Seite.

Aufruf:
    python algo/forex/backtest.py                      # Selbstcheck
    python algo/forex/backtest.py --symbol EURUSD --von 2012-01-01 --bis 2012-12-31
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, time as dtime, timedelta
from pathlib import Path

_HIER = Path(__file__).resolve().parent
_ALGO = _HIER.parent

# Siehe die ausfuehrliche Begruendung in algo/forex/rules.py: der eigene Ordner muss von
# sys.path runter, sonst verdeckt algo/forex/pnl.py das gleichnamige algo/pnl.py.
for _p in (str(_HIER), ""):
    while _p in sys.path:
        sys.path.remove(_p)
sys.path.insert(0, str(_ALGO))
sys.path.insert(0, str(_ALGO.parent / "tools"))

from analyze_ohlc import Bar, NY, PIP_SIZE  # noqa: E402

from forex import pnl as fx_pnl  # noqa: E402
from forex import rules as fx_rules  # noqa: E402

# Startkapital und Risiko identisch zur MNQ-Seite (algo/backtest_bt.py:81,89), damit die
# beiden Serien ueberhaupt vergleichbar sind.
START_CASH = 100_000.0
MAX_RISK_PCT = 0.01

# Rollover 17:00 NY. Jede Position wird davor glattgestellt, statt ein Swap-Modell zu raten
# (Spec §5.5). 16:59 ist die letzte Minute, in der noch gehandelt wird.
ROLLOVER = dtime(17, 0)
FLAT_AB = dtime(16, 59)


@dataclass
class Trade:
    symbol: str
    tag: date
    window: str
    herkunft: str
    side: str
    t_entry: datetime
    entry: float
    stop: float
    target: float
    t_exit: datetime | None = None
    exit: float | None = None
    grund: str = ""            # "stop" | "target" | "flat" | "offen"
    lots: float = 0.0
    pnl_usd: float | None = None
    dubious: bool = False


@dataclass
class Ergebnis:
    symbol: str
    trades: list[Trade] = field(default_factory=list)
    verworfen_kein_kurs: int = 0     # Pip-Wert nicht bestimmbar -> Trade nicht bewertbar
    flat_erzwungen: int = 0          # haette ohne Rollover-Regel weitergelaufen

    def netto_usd(self) -> float:
        return sum(t.pnl_usd for t in self.trades if t.pnl_usd is not None)

    def dubious_pct(self) -> float:
        bewertet = [t for t in self.trades if t.pnl_usd is not None]
        if not bewertet:
            return 0.0
        return 100.0 * sum(1 for t in bewertet if t.dubious) / len(bewertet)


def _tage(bars: list[Bar]) -> dict[date, list[Bar]]:
    """Bars nach NY-Kalendertag. Fuer 24x5 ist der Kalendertag die Tagesgrenze
    (Vorgaenger-Spec §1.2) -- nicht der Futures-Handelstag ab 18:00 des Vorabends."""
    out: dict[date, list[Bar]] = {}
    for b in bars:
        out.setdefault(b.t.date(), []).append(b)
    return out


def _flat_zeit(tag: date) -> datetime:
    return datetime.combine(tag, FLAT_AB, tzinfo=NY)


def simuliere_setup(setup, bars_ab: list[Bar], symbol: str, spread_pips: float,
                    kurse: dict[str, float], equity: float) -> Trade | None:
    """Ein Setup ab seiner Entstehung vorwaerts abwickeln. `bars_ab` sind die Kerzen NACH dem
    Setup-Zeitpunkt (streng spaeter -- kein Fill in der Kerze, die das Signal erzeugt hat).

    Rueckgabe None, wenn der Entry bis zum Rollover nie gefuellt wurde.
    """
    s = spread_pips * PIP_SIZE[symbol]
    long = setup.side == "long"
    flat_um = _flat_zeit(setup.t.date())

    lots = fx_pnl.lot_size(equity, MAX_RISK_PCT, setup.entry, setup.stop, symbol, kurse)
    if lots <= 0:
        return None

    tr = Trade(symbol=symbol, tag=setup.t.date(), window=setup.window,
               herkunft=setup.herkunft, side=setup.side, t_entry=setup.t,
               entry=setup.entry, stop=setup.stop, target=setup.target, lots=lots)

    im_markt = False
    for b in bars_ab:
        if b.t >= flat_um:
            break
        if not im_markt:
            # Entry: Long kauft zum Ask (Bid muss E - s erreichen), Short verkauft zum Bid.
            gefuellt = (b.l <= setup.entry - s) if long else (b.h >= setup.entry)
            if not gefuellt:
                continue
            im_markt = True
            tr.t_entry = b.t
            # Stop/Ziel koennen in derselben Kerze schon liegen -- unten mitgeprueft.

        if long:
            stop_hit = b.l <= setup.stop
            ziel_hit = b.h >= setup.target
        else:
            stop_hit = b.h >= setup.stop - s        # Ask erreicht den Stop frueher
            ziel_hit = b.l <= setup.target - s      # Ask erreicht das Ziel spaeter

        if stop_hit and ziel_hit:
            # Aus OHLC nicht entscheidbar, was zuerst kam -> Stop werten, Trade markieren.
            tr.dubious = True
            tr.t_exit, tr.exit, tr.grund = b.t, setup.stop, "stop"
            break
        if stop_hit:
            tr.t_exit, tr.exit, tr.grund = b.t, setup.stop, "stop"
            break
        if ziel_hit:
            tr.t_exit, tr.exit, tr.grund = b.t, setup.target, "target"
            break

    if not im_markt:
        return None
    if tr.exit is None:
        # Rollover erreicht: zum letzten verfuegbaren Bid glattstellen (Long) bzw. Ask (Short).
        letzte = [b for b in bars_ab if b.t < flat_um]
        if not letzte:
            return None
        schluss = letzte[-1].c
        tr.t_exit = letzte[-1].t
        tr.exit = schluss if long else schluss + s
        tr.grund = "flat"

    brutto = fx_pnl.brutto_usd(symbol, tr.side, tr.entry, tr.exit, tr.lots, kurse)
    if brutto is None:
        return tr          # unbewertbar -- der Aufrufer zaehlt ihn als verworfen
    tr.pnl_usd = brutto - fx_pnl.COMMISSION_PER_LOT_RT * tr.lots
    return tr


def lauf(symbol: str, bars: list[Bar], kurse_je_tag: dict[date, dict[str, float]],
         spread_pips: float | None = None, fenster: list[str] | None = None,
         min_target_pips: float = 10.0) -> Ergebnis:
    """Backtest ueber die uebergebenen Bars. Ein Setup je Fenster und Tag (das *1st Presented*
    FVG ist per Definition eindeutig), danach vorwaerts abgewickelt.

    `kurse_je_tag` liefert je Handelstag den Referenzkurs-Schnappschuss fuer die
    Pip-Wert-Umrechnung. Fehlt einer, wird der Trade verworfen und gezaehlt (Spec §5.1),
    statt mit einer Naeherung bewertet zu werden.
    """
    sp = fx_pnl.SPREAD_PIPS[symbol] if spread_pips is None else spread_pips
    namen = fenster or [n for n, _, _, _ in fx_rules.WINDOWS]
    erg = Ergebnis(symbol=symbol)
    equity = START_CASH

    for tag, tagesbars in sorted(_tage(bars).items()):
        kurse = kurse_je_tag.get(tag)
        for name in namen:
            setup = None
            for i, b in enumerate(tagesbars):
                if not any(n == name for n, _, _ in fx_rules.active_windows(tag, b.t)):
                    continue
                setup = fx_rules.plan_trade(tagesbars[:i + 1], b.t, name, symbol=symbol,
                                            min_target_pips=min_target_pips)
                if setup is not None:
                    start_idx = i + 1
                    break
            if setup is None:
                continue
            if kurse is None:
                erg.verworfen_kein_kurs += 1
                continue
            tr = simuliere_setup(setup, tagesbars[start_idx:], symbol, sp, kurse, equity)
            if tr is None:
                continue
            if tr.pnl_usd is None:
                erg.verworfen_kein_kurs += 1
                continue
            if tr.grund == "flat":
                erg.flat_erzwungen += 1
            erg.trades.append(tr)
            equity += tr.pnl_usd

    return erg


def bericht(erg: Ergebnis, flat_quote: float | None = None,
            be_spread: float | None = None) -> str:
    """Report mit den drei Pflichtangaben aus Spec §5.4: dubious_pct, Break-even-Spread und
    Flat-Quote des ausgewerteten Fensters."""
    zeilen = [f"=== {erg.symbol} ===",
              f"Trades: {len(erg.trades)}   Netto: {erg.netto_usd():+,.2f} USD"]
    if erg.trades:
        gewinner = [t for t in erg.trades if (t.pnl_usd or 0) > 0]
        zeilen.append(f"Trefferquote: {100*len(gewinner)/len(erg.trades):.1f} %")
    zeilen.append(f"dubious_pct: {erg.dubious_pct():.1f} %   "
                  f"(Stop und Ziel in derselben Kerze -> Stop gewertet)")
    zeilen.append(f"Break-even-Spread: "
                  f"{'-' if be_spread is None else f'{be_spread:.2f} Pips'}")
    zeilen.append(f"Flat-Quote Fenster: "
                  f"{'-' if flat_quote is None else f'{flat_quote:.2f} %'}")
    zeilen.append(f"verworfen (kein Referenzkurs): {erg.verworfen_kein_kurs}")
    zeilen.append(f"vor Rollover zwangsgeschlossen: {erg.flat_erzwungen}")

    nach_fenster: dict[str, list[Trade]] = {}
    for t in erg.trades:
        nach_fenster.setdefault(t.window, []).append(t)
    if nach_fenster:
        zeilen.append("")
        zeilen.append("{:<26} {:>7} {:>14} {:>9}".format("Fenster", "Trades", "Netto USD", "Treffer%"))
        for name, ts in sorted(nach_fenster.items(), key=lambda kv: -len(kv[1])):
            netto = sum(t.pnl_usd for t in ts if t.pnl_usd is not None)
            gew = sum(1 for t in ts if (t.pnl_usd or 0) > 0)
            zeilen.append("{:<26} {:>7} {:>14,.2f} {:>9.1f}".format(
                name, len(ts), netto, 100 * gew / len(ts)))
    return "\n".join(zeilen)


def demo() -> None:
    """Selbstcheck nach Spec §6.5. Konstruierte Kerzen, keine Dateien noetig."""
    def b(hh, mm, o, h, lo, c, tag=date(2026, 1, 5)):
        return Bar(datetime.combine(tag, dtime(hh, mm), tzinfo=NY), o, h, lo, c)

    sym = "EURUSD"
    s_pips = 1.0
    s = s_pips * PIP_SIZE[sym]
    kurse = {}          # EURUSD braucht keine Referenz (Quote ist USD)

    # --- Short-Stop-Asymmetrie ---------------------------------------------------------
    # Short mit Stop bei 1,10500. Die Kerze erreicht als Bid nur 1,10495 -- ohne
    # Ask-Betrachtung waere das KEIN Stop-Out. Mit 1 Pip Spread liegt der Ask bei 1,10505,
    # der Stop ist also getroffen.
    setup = fx_rules.TradeSetup(t=b(10, 0, 1.1, 1.1, 1.1, 1.1).t, window="NY AM Silver Bullet",
                                herkunft="sb", side="short", entry=1.10400,
                                stop=1.10500, target=1.10100)
    folge = [b(10, 1, 1.10400, 1.10420, 1.10380, 1.10400),   # Entry fuellt (Bid >= 1,10400)
             b(10, 2, 1.10400, 1.10495, 1.10390, 1.10490)]   # Bid-High 1,10495 < Stop
    tr = simuliere_setup(setup, folge, sym, s_pips, kurse, START_CASH)
    assert tr is not None and tr.grund == "stop", tr
    assert abs(tr.exit - 1.10500) < 1e-9, tr.exit

    # Ohne Spread waere derselbe Trade NICHT ausgestoppt -- belegt, dass die Asymmetrie wirkt
    # und nicht nur mitlaeuft.
    tr0 = simuliere_setup(setup, folge, sym, 0.0, kurse, START_CASH)
    assert tr0 is not None and tr0.grund != "stop", tr0

    # --- Long-Stop bleibt symmetrisch (Bid-Seite) -------------------------------------
    setup_l = fx_rules.TradeSetup(t=b(10, 0, 1.1, 1.1, 1.1, 1.1).t,
                                  window="NY AM Silver Bullet", herkunft="sb", side="long",
                                  entry=1.10000, stop=1.09900, target=1.10300)
    folge_l = [b(10, 1, 1.10010, 1.10020, 1.09985, 1.10000),   # Bid <= E - s -> Fill
               b(10, 2, 1.10000, 1.10010, 1.09905, 1.09910)]   # Bid-Low ueber dem Stop
    tr = simuliere_setup(setup_l, folge_l, sym, s_pips, kurse, START_CASH)
    assert tr is not None and tr.grund == "flat", tr.grund

    # --- Konservative Fill-Reihenfolge -------------------------------------------------
    # Stop UND Ziel in derselben Kerze -> Stop wird gewertet, Trade als dubious markiert.
    folge_d = [b(10, 1, 1.10010, 1.10020, 1.09985, 1.10000),
               b(10, 2, 1.10000, 1.10350, 1.09850, 1.10200)]
    tr = simuliere_setup(setup_l, folge_d, sym, s_pips, kurse, START_CASH)
    assert tr is not None and tr.grund == "stop" and tr.dubious, (tr.grund, tr.dubious)

    # --- Rollover-Glattstellung ---------------------------------------------------------
    # Eine Kerze um 17:30 darf nicht mehr gehandelt werden.
    folge_r = [b(16, 50, 1.10010, 1.10020, 1.09985, 1.10000),
               b(17, 30, 1.10000, 1.10400, 1.09800, 1.10300)]
    tr = simuliere_setup(setup_l, folge_r, sym, s_pips, kurse, START_CASH)
    assert tr is not None and tr.grund == "flat", tr.grund
    assert tr.t_exit.time() < ROLLOVER, tr.t_exit

    # --- Fehlender Referenzkurs -> unbewertbar, nicht genaehert ------------------------
    setup_j = fx_rules.TradeSetup(t=b(10, 0, 160, 160, 160, 160).t, window="KZ NY",
                                  herkunft="killzone", side="long", entry=160.000,
                                  stop=159.800, target=160.500)
    folge_j = [b(10, 1, 160.00, 160.02, 159.98, 160.00),
               b(10, 2, 160.00, 160.60, 159.99, 160.55)]
    tr = simuliere_setup(setup_j, folge_j, "EURJPY", 1.3, {}, START_CASH)
    assert tr is None, "ohne USDJPY-Referenz darf kein bewerteter Trade entstehen"

    # --- P&L-Vorzeichen und Kostenrichtung ---------------------------------------------
    # Long 1,10000 -> Ziel 1,10300 = +30 Pips. Bei 1 % Risiko auf 10 Pips Stop: 10 Lots.
    folge_g = [b(10, 1, 1.10010, 1.10020, 1.09985, 1.10000),
               b(10, 2, 1.10000, 1.10310, 1.10000, 1.10300)]
    tr = simuliere_setup(setup_l, folge_g, sym, s_pips, kurse, START_CASH)
    assert tr is not None and tr.grund == "target", tr.grund
    assert abs(tr.lots - 10.0) < 1e-9, tr.lots
    # brutto 30 Pips * $10 * 10 Lots = $3.000, minus Kommission 10 * $7 = $70
    assert tr.pnl_usd is not None and abs(tr.pnl_usd - (3000 - 70)) < 1e-6, tr.pnl_usd
    # Der Spread steckt bereits in den Fuellpreisen und wird NICHT zusaetzlich abgezogen --
    # Regressionswaechter gegen die Doppelzaehlung, vor der pnl.real_pnl_usd warnt.

    print("forex.backtest demo: OK")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--symbol", default=None, help="z.B. EURUSD (ohne: nur Selbstcheck)")
    ap.add_argument("--tf", default="5m")
    ap.add_argument("--von", default=None, help="JJJJ-MM-TT")
    ap.add_argument("--bis", default=None, help="JJJJ-MM-TT")
    ap.add_argument("--fenster", nargs="*", default=None)
    a = ap.parse_args(argv)

    if a.symbol is None:
        demo()
        return 0

    import marktdaten as md
    von = date.fromisoformat(a.von) if a.von else None
    bis = date.fromisoformat(a.bis) if a.bis else None
    bars = md.bars(a.symbol, a.tf, von, bis)
    if not bars:
        print(f"Keine Bars fuer {a.symbol} {a.tf} in diesem Zeitraum.")
        return 1

    # Referenzkurse je Tag: der Tagesschluss der benoetigten Paare. Fuer XXXUSD leer, weil der
    # Pip-Wert dort konstant ist -- so wird nur geladen, was wirklich gebraucht wird.
    kurse_je_tag: dict[date, dict[str, float]] = {}
    quote = fx_pnl.quote_ccy(a.symbol)
    if quote != "USD":
        ref = f"{quote}USD" if f"{quote}USD" in PIP_SIZE else f"USD{quote}"
        for rb in md.bars(ref, "1d", von, bis):
            kurse_je_tag[rb.t.date()] = {ref: rb.c}
    else:
        for tag in {b.t.date() for b in bars}:
            kurse_je_tag[tag] = {}

    erg = lauf(a.symbol, bars, kurse_je_tag, fenster=a.fenster)

    flach = sum(1 for b in bars if b.o == b.h == b.l == b.c)
    be = fx_pnl.break_even_spread(
        lambda sp: lauf(a.symbol, bars, kurse_je_tag, spread_pips=sp,
                        fenster=a.fenster).netto_usd(), a.symbol)
    print(bericht(erg, flat_quote=100.0 * flach / len(bars), be_spread=be))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
