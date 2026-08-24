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
Zwei verschiedene Ambiguitaeten, beide werden als `dubious` gezaehlt und beide werden
zuungunsten des Backtests aufgeloest:

  (a) Stop UND Ziel liegen in der Spanne derselben Kerze -> Stop gewertet.
  (b) Der Stop liegt in der Spanne der ENTRY-Kerze -> Stop gewertet.

(b) ist auf 5m-Forex der mit Abstand haeufigere Fall und wurde in der ersten Fassung dieses
Moduls uebersehen: gemessen am 2026-08-15 auf EURUSD 5m (Januar 2019) traf das auf
**74,1 %** aller gefuellten Trades zu, waehrend `dubious_pct` 0,0 % meldete. Eine gemeldete
Null bei einer Pflichtkennzahl ist gefaehrlicher als ein hoher Wert -- sie sieht aus wie eine
saubere Messung. `dubious_pct` ist Pflichtkennzahl jedes Reports, wie auf der MNQ-Seite.

MINDEST-STOP-DISTANZ
--------------------
Auf der MNQ-Seite ist `stop_buffer_pct` (10 % der FVG-Groesse) unproblematisch, weil MNQ-FVGs
viele Punkte gross sind. Auf 5m-Forex ergibt dieselbe Regel Stops mit **1,2 Pips Median und
0,2 Pips Minimum** -- also unterhalb des Spreads. Ein Stop, der enger ist als die
Geld-Brief-Spanne, ist keine Handelsentscheidung, sondern ein Rundungsartefakt: er wird vom
Spread allein ausgeloest. `min_stop_pips` verwirft solche Setups und zaehlt sie; ohne diesen
Filter misst der Backtest die Mikrostruktur des Datenfeeds statt die Regel.

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
import risk_killswitch as killswitch  # noqa: E402  -- geteilt mit der MNQ-Seite, nicht kopiert

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
    verworfen_stop_zu_eng: int = 0   # Stop unter min_stop_pips -> Rundungsartefakt, kein Setup
    killswitch_blockiert: int = 0    # Drawdown-Kill-Switch stand, kein neuer Trade erlaubt
    flat_erzwungen: int = 0          # haette ohne Rollover-Regel weitergelaufen
    end_equity: float = 0.0

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
                    kurse: dict[str, float], equity: float,
                    dubious_aufloesung: str = "stop") -> Trade | None:
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
        entry_kerze = False
        if not im_markt:
            # Entry: Long kauft zum Ask (Bid muss E - s erreichen), Short verkauft zum Bid.
            gefuellt = (b.l <= setup.entry - s) if long else (b.h >= setup.entry)
            if not gefuellt:
                continue
            im_markt = True
            entry_kerze = True
            tr.t_entry = b.t
            # Stop/Ziel koennen in derselben Kerze schon liegen -- unten mitgeprueft.

        if long:
            stop_hit = b.l <= setup.stop
            ziel_hit = b.h >= setup.target
        else:
            stop_hit = b.h >= setup.stop - s        # Ask erreicht den Stop frueher
            ziel_hit = b.l <= setup.target - s      # Ask erreicht das Ziel spaeter

        # Zwei Ambiguitaeten, beide zuungunsten des Backtests aufgeloest (siehe Modul-Doku):
        # (a) Stop und Ziel in derselben Kerze, (b) Stop in der Entry-Kerze -- dort ist nicht
        # entscheidbar, ob der Ruecklauf den Entry vor oder nach dem Stop passiert hat.
        unbestimmt = stop_hit and (ziel_hit or entry_kerze)
        if unbestimmt:
            tr.dubious = True
            # `dubious_aufloesung="target"` ist NICHT die Handelsannahme, sondern das
            # Gegenstueck fuer die Einklammerung: bei 28,6 % unbestimmten Trades ist ein
            # einzelnes Ergebnis keine Zahl, sondern eine Grenze. Die Wahrheit liegt zwischen
            # beiden Laeufen. Fuer jede Handelsentscheidung gilt weiter "stop".
            if dubious_aufloesung == "target" and ziel_hit:
                tr.t_exit, tr.exit, tr.grund = b.t, setup.target, "target"
                break
        if stop_hit:
            tr.t_exit, tr.exit, tr.grund = b.t, setup.stop, "stop"
            break
        if ziel_hit:
            if entry_kerze:
                # Ziel in der Entry-Kerze ohne Stop-Beruehrung: die Reihenfolge ist hier
                # eindeutig (Entry liegt zwischen Kerzen-Extrem und Ziel), aber die Kerze
                # musste beide Preise durchlaufen -- als dubious markiert, nicht umgewertet.
                tr.dubious = True
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
         min_target_pips: float = 10.0, min_stop_pips: float = 3.0,
         killswitch_pct: float | None = killswitch.DEFAULT_MAX_DRAWDOWN_PCT,
         dubious_aufloesung: str = "stop") -> Ergebnis:
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
    peak = START_CASH

    for tag, tagesbars in sorted(_tage(bars).items()):
        kurse = kurse_je_tag.get(tag)

        # Erst ALLE Setups des Tages sammeln, dann chronologisch abwickeln. Die erste Fassung
        # lief Fenster fuer Fenster durch und buchte damit z.B. einen 19:00-Asia-Trade vor
        # einem 03:00-London-Trade auf die Equity -- die Reihenfolge der WINDOWS-Liste haette
        # so die Equity-Kurve (und ueber das Sizing die Trade-Groessen) mitbestimmt. Auf die
        # Richtung einzelner Trades wirkt das nicht, auf Drawdown und Endkapital sehr wohl.
        setups: list[tuple] = []
        for name in namen:
            for i, b in enumerate(tagesbars):
                if not any(n == name for n, _, _ in fx_rules.active_windows(tag, b.t)):
                    continue
                setup = fx_rules.plan_trade(tagesbars[:i + 1], b.t, name, symbol=symbol,
                                            min_target_pips=min_target_pips)
                if setup is not None:
                    setups.append((setup.t, setup, i + 1))
                    break
        setups.sort(key=lambda x: (x[0], x[1].window))

        for _, setup, start_idx in setups:
            if abs(setup.entry - setup.stop) / PIP_SIZE[symbol] < min_stop_pips:
                erg.verworfen_stop_zu_eng += 1
                continue
            if kurse is None:
                erg.verworfen_kein_kurs += 1
                continue
            # Kill-Switch wie auf der MNQ-Seite (algo/backtest_bt.py, 15 % Drawdown seit
            # Equity-Hoch). Gleiches Konzept, gleiches Modul -- algo/risk_killswitch.py wird
            # importiert, nicht kopiert.
            #
            # Abschaltbar (killswitch_pct=None), weil er sonst die Messung uebernimmt: laut
            # seiner eigenen Doku ist ein ausgeloester Kill-Switch "praktisch ein Dauerstopp",
            # da die Equity ohne offene Position kein neues Hoch bilden kann. Auf 5 Jahren
            # EURUSD blockierte er 1.065 von 1.109 Setups -- gemessen wurde dann der
            # Kill-Switch, nicht die Regel. Fuer die Frage "traegt die Regel?" ohne, fuer die
            # Frage "waere das System handelbar?" mit.
            if killswitch_pct is not None and not killswitch.allowed(peak, equity,
                                                                    killswitch_pct):
                erg.killswitch_blockiert += 1
                continue
            tr = simuliere_setup(setup, tagesbars[start_idx:], symbol, sp, kurse, equity,
                                 dubious_aufloesung)
            if tr is None:
                continue
            if tr.pnl_usd is None:
                erg.verworfen_kein_kurs += 1
                continue
            if tr.grund == "flat":
                erg.flat_erzwungen += 1
            erg.trades.append(tr)
            equity += tr.pnl_usd
            peak = max(peak, equity)

    erg.end_equity = equity
    return erg


def bericht(erg: Ergebnis, flat_quote: float | None = None,
            be_spread: float | None = None) -> str:
    """Report mit den drei Pflichtangaben aus Spec §5.4: dubious_pct, Break-even-Spread und
    Flat-Quote des ausgewerteten Fensters."""
    zeilen = [f"=== {erg.symbol} ===",
              f"Trades: {len(erg.trades)}   Netto: {erg.netto_usd():+,.2f} USD   "
              f"Endkapital: {erg.end_equity:,.2f} USD (Start {START_CASH:,.0f})"]
    if erg.trades:
        gewinner = [t for t in erg.trades if (t.pnl_usd or 0) > 0]
        zeilen.append(f"Trefferquote: {100*len(gewinner)/len(erg.trades):.1f} %")
    zeilen.append(f"dubious_pct: {erg.dubious_pct():.1f} %   "
                  f"(Stop und Ziel in derselben Kerze -> Stop gewertet)")
    zeilen.append(f"Break-even-Spread: "
                  f"{'-' if be_spread is None else f'{be_spread:.2f} Pips'}")
    zeilen.append(f"Flat-Quote Fenster: "
                  f"{'-' if flat_quote is None else f'{flat_quote:.2f} %'}")
    zeilen.append(f"verworfen (Stop enger als min_stop_pips): {erg.verworfen_stop_zu_eng}")
    zeilen.append(f"verworfen (kein Referenzkurs): {erg.verworfen_kein_kurs}")
    zeilen.append(f"vom Kill-Switch blockiert: {erg.killswitch_blockiert}")
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

    # --- Konservative Fill-Reihenfolge (a): Stop UND Ziel in derselben Kerze -----------
    folge_d = [b(10, 1, 1.10010, 1.10020, 1.09985, 1.10000),
               b(10, 2, 1.10000, 1.10350, 1.09850, 1.10200)]
    tr = simuliere_setup(setup_l, folge_d, sym, s_pips, kurse, START_CASH)
    assert tr is not None and tr.grund == "stop" and tr.dubious, (tr.grund, tr.dubious)

    # --- Konservative Fill-Reihenfolge (b): Stop in der ENTRY-Kerze --------------------
    # Regressionswaechter fuer den Fund vom 2026-08-15: auf 5m-EURUSD betraf das 74,1 % aller
    # Trades, waehrend dubious_pct 0,0 % meldete. Eine Kerze, die den Entry fuellt UND den
    # Stop reisst -- die Reihenfolge darin ist aus OHLC nicht rekonstruierbar.
    folge_eb = [b(10, 1, 1.10050, 1.10060, 1.09880, 1.09900)]
    tr = simuliere_setup(setup_l, folge_eb, sym, s_pips, kurse, START_CASH)
    assert tr is not None and tr.grund == "stop", tr.grund
    assert tr.dubious, "Stop in der Entry-Kerze MUSS als dubious gelten"
    assert tr.t_exit == tr.t_entry, (tr.t_entry, tr.t_exit)

    # --- Einklammerung: optimistische Aufloesung dreht NUR unbestimmte Faelle -----------
    tr_opt = simuliere_setup(setup_l, folge_d, sym, s_pips, kurse, START_CASH,
                             dubious_aufloesung="target")
    assert tr_opt is not None and tr_opt.grund == "target" and tr_opt.dubious, tr_opt.grund
    # Ein eindeutiger Stop-Out (Ziel nie beruehrt) bleibt auch optimistisch ein Stop-Out.
    folge_klar = [b(10, 1, 1.10010, 1.10020, 1.09985, 1.10000),
                  b(10, 2, 1.10000, 1.10010, 1.09880, 1.09890)]
    tr_klar = simuliere_setup(setup_l, folge_klar, sym, s_pips, kurse, START_CASH,
                              dubious_aufloesung="target")
    assert tr_klar is not None and tr_klar.grund == "stop", tr_klar.grund

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

    # --- Mindest-Stop-Distanz -----------------------------------------------------------
    # Ein Setup mit 1,2 Pips Stop (der gemessene Median auf 5m-EURUSD) liegt unter dem
    # Default von 3 Pips und darf gar nicht erst gehandelt werden -- der Spread allein
    # wuerde ihn ausloesen.
    tag = date(2026, 1, 5)
    eng = [b(10, 0, 1.10000, 1.10050, 1.09950, 1.10000),
           b(10, 1, 1.10000, 1.10200, 1.09990, 1.10180),
           b(10, 2, 1.10150, 1.10250, 1.10100, 1.10200)]
    eng += [b(10, 3 + i, 1.10200, 1.10260, 1.10150, 1.10210) for i in range(8)]

    class _FakeSetup:
        pass

    # Direkt ueber lauf() pruefen, weil der Filter dort sitzt: ein kuenstliches Setup mit
    # 1,2 Pips Stop muss in verworfen_stop_zu_eng landen und darf keinen Trade erzeugen.
    orig_plan = fx_rules.plan_trade

    def fake_plan(bars_, when, name, **kw):
        if name != "NY AM Silver Bullet" or when.minute != 0:
            return None
        return fx_rules.TradeSetup(t=when, window=name, herkunft="sb", side="long",
                                   entry=1.10000, stop=1.09988, target=1.10300)
    fx_rules.plan_trade = fake_plan
    try:
        e = lauf(sym, eng, {tag: {}}, spread_pips=s_pips)
        assert e.verworfen_stop_zu_eng == 1, e.verworfen_stop_zu_eng
        assert e.trades == [], e.trades
        # Mit abgesenkter Schwelle entsteht derselbe Trade sehr wohl -- belegt, dass der
        # Filter greift und nicht etwas anderes den Trade verhindert hat.
        e2 = lauf(sym, eng, {tag: {}}, spread_pips=s_pips, min_stop_pips=1.0)
        assert e2.verworfen_stop_zu_eng == 0, e2.verworfen_stop_zu_eng
    finally:
        fx_rules.plan_trade = orig_plan

    # --- Chronologische Abwicklung ------------------------------------------------------
    # Regressionswaechter: Setups muessen nach Zeit abgewickelt werden, nicht in der
    # Reihenfolge der WINDOWS-Liste. Zwei Fenster, das spaetere steht in WINDOWS weiter oben
    # -- die Trades muessen trotzdem chronologisch in erg.trades landen.
    def fake_zwei(bars_, when, name, **kw):
        stunde = {"London Silver Bullet": 3, "NY PM Silver Bullet": 14}.get(name)
        if stunde is None or when.hour != stunde or when.minute != 0:
            return None
        return fx_rules.TradeSetup(t=when, window=name, herkunft="sb", side="long",
                                   entry=1.10000, stop=1.09900, target=1.10300)

    zwei = []
    for hh in (3, 14):
        zwei.append(b(hh, 0, 1.10050, 1.10060, 1.10040, 1.10050))
        zwei.append(b(hh, 5, 1.10010, 1.10020, 1.09985, 1.10000))
        zwei.append(b(hh, 10, 1.10000, 1.10310, 1.10000, 1.10300))
    zwei.sort(key=lambda x: x.t)

    fx_rules.plan_trade = fake_zwei
    try:
        e3 = lauf(sym, zwei, {tag: {}}, spread_pips=s_pips,
                  fenster=["NY PM Silver Bullet", "London Silver Bullet"])
        assert len(e3.trades) == 2, len(e3.trades)
        assert e3.trades[0].t_entry < e3.trades[1].t_entry, \
            "Trades muessen chronologisch gebucht werden, nicht in WINDOWS-Reihenfolge"
        assert e3.trades[0].window == "London Silver Bullet", e3.trades[0].window
    finally:
        fx_rules.plan_trade = orig_plan

    print("forex.backtest demo: OK")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--symbol", default=None, help="z.B. EURUSD (ohne: nur Selbstcheck)")
    ap.add_argument("--tf", default="5m")
    ap.add_argument("--von", default=None, help="JJJJ-MM-TT")
    ap.add_argument("--bis", default=None, help="JJJJ-MM-TT")
    ap.add_argument("--fenster", nargs="*", default=None)
    ap.add_argument("--min-stop-pips", type=float, default=3.0)
    ap.add_argument("--dubious-optimistisch", action="store_true",
                    help="Unbestimmte Fills zugunsten des Ziels aufloesen statt des Stops. "
                         "NICHT die Handelsannahme -- nur die Gegengrenze zur Einklammerung.")
    ap.add_argument("--no-killswitch", action="store_true",
                    help="Drawdown-Kill-Switch aus. Fuer die Frage 'traegt die Regel?' -- "
                         "mit Kill-Switch misst ein Mehrjahres-Lauf ueberwiegend ihn selbst.")
    ap.add_argument("--breakeven", action="store_true",
                    help="Break-even-Spread numerisch suchen (rechnet den Backtest ~12x, "
                         "auf Mehrjahres-Fenstern entsprechend teuer)")
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

    ks = None if a.no_killswitch else killswitch.DEFAULT_MAX_DRAWDOWN_PCT
    aufl = "target" if a.dubious_optimistisch else "stop"
    erg = lauf(a.symbol, bars, kurse_je_tag, fenster=a.fenster,
               min_stop_pips=a.min_stop_pips, killswitch_pct=ks, dubious_aufloesung=aufl)

    flach = sum(1 for b in bars if b.o == b.h == b.l == b.c)
    be = None
    if a.breakeven:
        be = fx_pnl.break_even_spread(
            lambda sp: lauf(a.symbol, bars, kurse_je_tag, spread_pips=sp,
                            fenster=a.fenster, min_stop_pips=a.min_stop_pips,
                            killswitch_pct=ks).netto_usd(),
            a.symbol)
    print(f"Zeitraum: {bars[0].t.date()} .. {bars[-1].t.date()}   "
          f"Kerzen: {len(bars):,}   TF: {a.tf}   min_stop_pips: {a.min_stop_pips}   "
          f"Kill-Switch: {'aus' if ks is None else f'{ks:.0%}'}   "
          f"dubious->{aufl}")
    print(bericht(erg, flat_quote=100.0 * flach / len(bars), be_spread=be))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
