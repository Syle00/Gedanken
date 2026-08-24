#!/usr/bin/env python3
"""Forex-Zwilling von algo/rules.py (Spec §6.1). DIESELBE Regel-Logik -- Nutzervorgabe
2026-08-15: "ich moechte die genau gleichen konzepte nutzen ausser bekannte sachen die nur fuer
future sind".

Silver Bullet, so wie er im Wiki steht (wiki/models/Silver Bullet Model.md), unveraendert:
  1. `when` muss in einem Fenster liegen (siehe WINDOWS unten).
  2. Erstes FVG, das INNERHALB des Fensters entstanden und bis `when` bestaetigt ist -> Setup.
  3. Richtung = FVG-Seite (bullish -> long, bearish -> short).
  4. Entry = FVG-C.E. (50 %), Stop = FVG-Gegenkante + Puffer.
  5. Target = naechstes unberuehrtes Liquiditaets-Level in Traderichtung -- ohne Ziel kein Setup.
  6. Mindestabstand Entry->Target, sonst kein Setup.

Drei Unterschiede zu algo/rules.py, alle in der Spec begruendet:
  1. WINDOWS traegt zusaetzlich die vier Killzones (Spec §2.4) und je Fenster eine Herkunft
     ("sb" / "killzone"), damit der Report sie getrennt ausweisen kann.
  2. Tick-Rundung ueber algo/forex/pnl.py statt algo/pnl.py -- algo/pnl.py bleibt unangetastet.
  3. Mindestabstand in PIPS statt Punkten. "10 Punkte" ist auf EURUSD sinnlos; PIP_SIZE stellt
     die Vergleichbarkeit her (Spec §3 der Vorgaenger-Spec).

Ausgeschlossen (Spec §2.2), und zwar durch Nicht-Aufruf statt durch Guard: org_gap(),
ndog_gap(), 1st-Presented-FVG-des-Tages, erstes FVG nach 9:30, Open Drive. Der Guard in
tools/analyze_ohlc.py greift ohnehin -- ein Aufruf, der garantiert None liefert, gehoert nicht
in den Code. NWOG bleibt ausdruecklich zulaessig (Wochenendgap existiert im Forex).

Kein Lookahead: alle Detektoren laufen nur auf bars mit t <= when.

Aufruf (Selbstcheck):
    python algo/forex/rules.py
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

_HIER = Path(__file__).resolve().parent
_ALGO = _HIER.parent

# Der eigene Ordner MUSS von sys.path runter, bevor irgendetwas aus algo/ importiert wird:
# beim direkten Aufruf (`python algo/forex/rules.py`) setzt Python ihn automatisch auf
# sys.path[0], und dann verdeckt algo/forex/pnl.py das gleichnamige algo/pnl.py. Folge waere
# ein ImportError tief in algo/backtest_hp_fvg.py ("cannot import name POINT_VALUE from pnl") --
# schlimmer noch, bei aehnlicher API haette es still das falsche Modul benutzt. Die
# Geschwister werden deshalb ueber das Paket (`forex.pnl`) angesprochen, nicht flach.
for _p in (str(_HIER), ""):
    while _p in sys.path:
        sys.path.remove(_p)
sys.path.insert(0, str(_ALGO))
sys.path.insert(0, str(_ALGO.parent / "tools"))

from analyze_ohlc import (Bar, at, fvgs, hp_context, untouched_levels,  # noqa: E402
                          CFG, PIP_SIZE, SESSION_TYP)
from backtest_hp_fvg import bias_proxy  # noqa: E402

from forex import pnl as fx_pnl  # noqa: E402  -- algo/forex/pnl.py, NICHT algo/pnl.py

# Identisch zu algo/rules.py: Kerzen VOR dem Fenster, die fvgs() als Kontext bekommt
# (Volatilitaet fuer size_rel, Swings fuer die Stark-Einstufung).
CONTEXT_BARS = 60

# (Name, Start-Stunde, End-Stunde, Herkunft) in NY-Zeit.
#
# Die drei Silver-Bullet-Fenster stehen unveraendert wie in algo/rules.py::WINDOWS -- gleiches
# Konzept, gleiche Zeiten (wiki/models/Silver Bullet Model.md).
#
# Dazu die vier Killzones aus analyze_ohlc.KILLZONES (Nutzerentscheidung 2026-08-15: "alle vier
# Killzones messen", die Daten sollen die Fensterwahl entscheiden). Asia laeuft ueber
# Mitternacht und wird wie dort als zwei Fenster gefuehrt.
#
# "NY-Forex 7-10" steht NEBEN "NY 7-9", nicht statt dessen: analyze_ohlc.KILLZONES fuehrt die
# NY-Killzone als 07:00-09:00, wiki/concepts/ICT Daily Range Session Timing.md sagt fuer Forex
# ausdruecklich 07:00-10:00. Der Widerspruch wird gemessen statt still aufgeloest
# (Spec §2.4, CLAUDE.md "Widersprueche markieren").
# Grenzen sind (Stunde, Minute) und damit minutengenau: die Asia-Nacht-Killzone endet laut
# analyze_ohlc.KILLZONES um 0:30, nicht zur vollen Stunde. Eine Sonderfall-Tabelle daneben
# waere fehleranfaellig -- die erste Fassung dieses Moduls hatte damit prompt ein Fenster bis
# 1:30 statt 0:30 gebaut.
WINDOWS = [
    ("London Silver Bullet", (3, 0), (4, 0), "sb"),
    ("NY AM Silver Bullet", (10, 0), (11, 0), "sb"),
    ("NY PM Silver Bullet", (14, 0), (15, 0), "sb"),
    ("KZ Asia (abends)", (19, 0), (24, 0), "killzone"),
    ("KZ Asia (nachts)", (0, 0), (0, 30), "killzone"),
    ("KZ London", (2, 0), (5, 0), "killzone"),
    ("KZ NY", (7, 0), (9, 0), "killzone"),
    ("KZ NY-Forex", (7, 0), (10, 0), "killzone"),
    ("KZ London Close", (10, 0), (12, 0), "killzone"),
]


@dataclass
class TradeSetup:
    t: datetime
    window: str
    herkunft: str          # "sb" | "killzone" -- fuer die getrennte Auswertung im Report
    side: str              # "long" | "short"
    entry: float
    stop: float
    target: float


def _fenster_grenzen(day: date, von: tuple[int, int],
                     bis: tuple[int, int]) -> tuple[datetime, datetime]:
    """Fensterspanne als [start, ende). 24:00 ist die Tagesgrenze und wird als 0:00 des
    Folgetags aufgeloest -- `at()` kennt keine Stunde 24, und ein Ersatz durch 23:59 wuerde
    die letzte Minute des Abend-Asia-Fensters stillschweigend verschlucken."""
    start = at(day, von[0], von[1])
    if bis[0] >= 24:
        ende = at(day + timedelta(days=1), 0, 0)
    else:
        ende = at(day, bis[0], bis[1])
    return start, ende


def active_windows(day: date, when: datetime) -> list[tuple[str, str, datetime]]:
    """ALLE Fenster, in die `when` faellt -- anders als algo/rules.py::_active_window, das beim
    ersten Treffer abbricht.

    Grund: die Fenster ueberlappen hier bewusst (NY AM Silver Bullet 10-11 liegt in KZ London
    Close 10-12 und in KZ NY-Forex 7-10). Ein "erster Treffer gewinnt" wuerde das Ergebnis von
    der Reihenfolge der Liste abhaengig machen und genau die Trennung verhindern, wegen der die
    Killzones ueberhaupt aufgenommen wurden. Der Aufrufer entscheidet, welches Fenster er
    auswertet."""
    out = []
    for name, von, bis, herkunft in WINDOWS:
        start, ende = _fenster_grenzen(day, von, bis)
        if start <= when < ende:
            out.append((name, herkunft, start))
    return out


def sb_entry_signal(bars: list[Bar], when: datetime, fenster: str,
                    stop_buffer_pct: float = 0.1, symbol: str = "EURUSD",
                    require_strong: bool = False, min_size_rel: float | None = None
                    ) -> tuple[str, str, float, float] | None:
    """Silver-Bullet-Entry fuer EIN benanntes Fenster (Fenster/1st Presented FVG ->
    Seite/Entry/Stop), ohne Ziel-Pruefung. Rueckgabe (fenster, side, entry, stop) oder None.

    Unterschied zur MNQ-Fassung nur in der Signatur: dort waehlt die Funktion das Fenster
    selbst (erster Treffer), hier bekommt sie es vorgegeben, weil sich die Fenster ueberlappen.
    Die Logik darunter ist Zeile fuer Zeile dieselbe.

    Kein Lookahead: nur bars[t<=when].
    """
    treffer = [(n, h, s) for n, h, s in active_windows(when.date(), when) if n == fenster]
    if not treffer:
        return None
    _, _, win_start = treffer[0]

    hist = [b for b in bars if b.t <= when]
    if len(hist) < 3:
        return None

    # Die 3-Kerzen-Formation muss KOMPLETT im Fenster liegen -- ein FVG, dessen mittlere Kerze
    # exakt auf win_start faellt, beginnt eine Kerze davor, also ausserhalb der Session. Darum
    # ueber `t_start` filtern statt ueber g["t"] (= mittlere Kerze). Uebernommen aus
    # algo/rules.py inkl. der Nutzerklaerung vom 2026-08-11: ein randueberlappendes FVG ist
    # NICHT ungueltig -- es ist nur kein *1st Presented* FVG, und darauf baut dieses Setup auf.
    #
    # CONTEXT_BARS Kerzen VOR dem Fenster kommen mit, damit fvgs() die lokale Volatilitaet
    # (size_rel) und die Swings ueberhaupt schaetzen kann.
    first = next((k for k, b in enumerate(hist) if b.t >= win_start), None)
    if first is None:
        return None
    win_bars = hist[max(0, first - CONTEXT_BARS):]
    if len(win_bars) < 3:
        return None
    window_fvgs = [g for g in fvgs(win_bars, tick=symbol) if g["t_start"] >= win_start]
    if not window_fvgs:
        return None

    # Weiter das ERSTE FVG im Fenster, nicht das erste passende. Taugt es nichts, gibt es kein
    # Setup, statt auf ein spaeteres auszuweichen.
    fvg = window_fvgs[0]
    if require_strong and not fvg["strong"]:
        return None
    # size_rel None = unbekannt (zu wenig Vorlauf), das darf kein Ausschluss sein.
    if min_size_rel is not None and fvg["size_rel"] is not None \
            and fvg["size_rel"] < min_size_rel:
        return None

    side = "long" if fvg["side"] == "bullish" else "short"
    entry = fvg["ce"]
    buffer = stop_buffer_pct * fvg["size"]
    stop = fvg["lo"] - buffer if side == "long" else fvg["hi"] + buffer

    # Auf das Tick-Raster zwingen, Richtung immer konservativ (Entry schwerer zu fuellen, Stop
    # weiter weg). Identisch zu algo/rules.py, nur ueber algo/forex/pnl.py.
    entry = fx_pnl.round_to_tick(entry, symbol, "down" if side == "long" else "up")
    stop = fx_pnl.round_to_tick(stop, symbol, "down" if side == "long" else "up")
    return fenster, side, entry, stop


def plan_trade(bars: list[Bar], when: datetime, fenster: str,
               stop_buffer_pct: float = 0.1, min_target_pips: float = 10.0,
               symbol: str = "EURUSD", require_strong: bool = False,
               min_size_rel: float | None = None,
               levels_bars: list[Bar] | None = None,
               target_candidates: list[dict] | None = None) -> TradeSetup | None:
    """Silver-Bullet-Setup zum Zeitpunkt `when` im Fenster `fenster`, oder None.

    `min_target_pips` statt `min_target_points`: der MNQ-Default von 10 Punkten ist auf EURUSD
    bedeutungslos (10 Preiseinheiten waeren 100.000 Pips). 10 Pips ist die direkte Entsprechung.

    `require_strong` / `min_size_rel` stehen wie auf der MNQ-Seite per Default AUS -- dort
    verschlechterten sie das Setup in der Messung vom 13.08.2026 deutlich (16 Trades/+2.194 USD
    ohne Filter gegen 10 Trades/-9.790 USD mit `require_strong`). Ob das auf Forex ebenso ist,
    ist eine der Fragen, die dieser Bestand erstmals beantworten kann.

    `levels_bars` / `target_candidates` wie in algo/rules.py: andere Bar-Reihe bzw. feste
    Session-Level (PDH/PDL/PWH/PWL) fuer die Ziel-Liquiditaet.
    """
    signal = sb_entry_signal(bars, when, fenster, stop_buffer_pct, symbol,
                             require_strong, min_size_rel)
    if signal is None:
        return None
    fenster_name, side, entry, stop = signal
    herkunft = next(h for n, _, _, h in WINDOWS if n == fenster_name)  # noqa: E501
    hist = [b for b in bars if b.t <= when]

    if target_candidates is not None:
        levels = target_candidates
    else:
        lvl_hist = hist if levels_bars is None else [b for b in levels_bars if b.t <= when]
        levels = untouched_levels(lvl_hist, CFG["swing"])
    if side == "long":
        kandidaten = [lv["level"] for lv in levels
                      if lv["side"] == "buyside" and lv["level"] > entry]
        target = min(kandidaten) if kandidaten else None
    else:
        kandidaten = [lv["level"] for lv in levels
                      if lv["side"] == "sellside" and lv["level"] < entry]
        target = max(kandidaten) if kandidaten else None
    if target is None:
        return None  # keine Zielliquiditaet -> Quelle fordert Confluenz, kein Setup ohne Ziel
    if abs(target - entry) / PIP_SIZE[symbol] < min_target_pips:
        return None  # zu wenig Potenzial

    return TradeSetup(t=when, window=fenster_name, herkunft=herkunft, side=side,
                      entry=entry, stop=stop, target=target)


def plan_trade_hp_fvg(bars: list[Bar], when: datetime, prev_day_hi: float, prev_day_lo: float,
                      symbol: str = "EURUSD", stop_feld: str = "stop_c2",
                      ziel_pips: float = 20.0, rr: float | None = None,
                      require_kz: bool = False, require_zone: bool = False,
                      require_bias: bool = False) -> TradeSetup | None:
    """High-Probability-FVG-Setup, Zeile fuer Zeile wie algo/rules.py::plan_trade_hp_fvg.
    Kein Fensterzwang (der MNQ-Backtest lief ganztaegig, also auch dieser).

    Einziger Unterschied: `ziel_pips` statt `ziel_pkt` -- dieselbe Groesse in der
    forex-lesbaren Einheit.

    Laeuft auf Forex, weil Vortagesrange-Haelfte, Killzone und Bias-Proxy keine
    Eroeffnungsauktion brauchen (Vorgaenger-Spec §6, Gruppe B).
    """
    hist = [b for b in bars if b.t <= when]
    if len(hist) < 3:
        return None

    window_fvgs = fvgs(hist, tick=symbol)
    if not window_fvgs:
        return None
    fvg = window_fvgs[-1]

    bias = bias_proxy(hist, when.date(), prev_day_hi, prev_day_lo)
    ctx = hp_context(fvg, prev_day_hi, prev_day_lo, bias)
    if require_kz and not ctx["kz_ok"]:
        return None
    if require_zone and not ctx["zone_ok"]:
        return None
    if require_bias and not bool(ctx["bias_ok"]):
        return None

    side = "long" if fvg["side"] == "bullish" else "short"
    entry, stop = fvg["entry"], fvg[stop_feld]
    risk = abs(entry - stop)
    if risk <= 0:
        return None
    spanne = rr * risk if rr else ziel_pips * PIP_SIZE[symbol]
    target = entry + spanne if side == "long" else entry - spanne

    return TradeSetup(t=when, window=ctx["killzone"] or "HP-FVG", herkunft="hp-fvg",
                      side=side, entry=entry, stop=stop, target=target)


def demo() -> None:
    """Selbstcheck nach Spec §6.5: Fenster, Ueberlappung, Symbol-Typ, kein Lookahead."""
    from zoneinfo import ZoneInfo
    NY = ZoneInfo("America/New_York")
    tag = date(2026, 1, 5)   # Montag

    # --- Fenster ----------------------------------------------------------------------
    # 10:30 liegt in NY AM Silver Bullet UND in KZ London Close -- beide muessen kommen.
    namen = {n for n, _, _ in active_windows(tag, datetime(2026, 1, 5, 10, 30, tzinfo=NY))}
    assert "NY AM Silver Bullet" in namen, namen
    assert "KZ London Close" in namen, namen
    assert "KZ NY-Forex" not in namen, "NY-Forex endet um 10:00"

    # 8:00 liegt in KZ NY (7-9) und KZ NY-Forex (7-10) -- die Diskrepanz aus Spec §2.4.
    namen = {n for n, _, _ in active_windows(tag, datetime(2026, 1, 5, 8, 0, tzinfo=NY))}
    assert namen == {"KZ NY", "KZ NY-Forex"}, namen
    # 9:30 nur noch in NY-Forex -- genau daran wird sich zeigen, welche Definition traegt.
    namen = {n for n, _, _ in active_windows(tag, datetime(2026, 1, 5, 9, 30, tzinfo=NY))}
    assert namen == {"KZ NY-Forex"}, namen

    # Asia-Nacht endet um 0:30, nicht 1:00.
    assert any(n == "KZ Asia (nachts)"
               for n, _, _ in active_windows(tag, datetime(2026, 1, 5, 0, 15, tzinfo=NY)))
    assert not any(n == "KZ Asia (nachts)"
                   for n, _, _ in active_windows(tag, datetime(2026, 1, 5, 0, 45, tzinfo=NY)))

    # Ausserhalb jedes Fensters (13:00 = Lunch, ausdruecklich keine Handelszeit).
    assert active_windows(tag, datetime(2026, 1, 5, 13, 0, tzinfo=NY)) == []

    # --- Alle 10 Paare sind als 24x5 gefuehrt und haben eine PIP_SIZE ------------------
    for sym in ("EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD",
                "USDCAD", "NZDUSD", "EURJPY", "EURGBP", "GBPJPY"):
        assert SESSION_TYP.get(sym) == "24x5", sym
        assert sym in PIP_SIZE, sym

    # --- Setup auf konstruierten Kerzen -----------------------------------------------
    # Bullisches FVG im NY-AM-Fenster: Kerze 2 laeuft hoch, Luecke zwischen c1.high und c3.low.
    def b(hh, mm, o, h, lo, c):
        return Bar(datetime(2026, 1, 5, hh, mm, tzinfo=NY), o, h, lo, c)

    bars = [b(9, 55 + i, 1.1000, 1.1005, 1.0995, 1.1000) for i in range(5)]
    bars += [
        b(10, 1, 1.1000, 1.1010, 1.0998, 1.1008),      # c1: high 1,1010
        b(10, 2, 1.1010, 1.1060, 1.1008, 1.1055),      # c2: Displacement
        b(10, 3, 1.1050, 1.1065, 1.1020, 1.1060),      # c3: low 1,1020 > c1.high -> FVG
    ]
    bars += [b(10, 4 + i, 1.1060, 1.1080, 1.1055, 1.1075) for i in range(6)]

    when = datetime(2026, 1, 5, 10, 10, tzinfo=NY)
    sig = sb_entry_signal(bars, when, "NY AM Silver Bullet", symbol="EURUSD")
    assert sig is not None, "bullisches FVG im Fenster muss ein Signal liefern"
    _, side, entry, stop = sig
    assert side == "long", side
    assert stop < entry, (entry, stop)
    # Auf dem Tick-Raster (EURUSD: 0,00001)
    assert abs(entry * 100_000 - round(entry * 100_000)) < 1e-6, entry
    assert abs(stop * 100_000 - round(stop * 100_000)) < 1e-6, stop

    # Im falschen Fenster gibt es dasselbe Signal NICHT.
    assert sb_entry_signal(bars, when, "KZ London", symbol="EURUSD") is None

    # --- Kein Lookahead ----------------------------------------------------------------
    # Dieselbe Anfrage gegen die um Zukunftskerzen erweiterte Reihe muss identisch antworten.
    zukunft = bars + [b(11, i, 1.2000, 1.2100, 1.1900, 1.2050) for i in range(30)]
    assert sb_entry_signal(zukunft, when, "NY AM Silver Bullet", symbol="EURUSD") == sig, \
        "Signal darf sich durch spaetere Kerzen nicht aendern (Lookahead!)"

    # --- Mindestziel in Pips, nicht in Punkten -----------------------------------------
    # Ohne erreichbare Ziel-Liquiditaet gibt es kein Setup.
    assert plan_trade(bars, when, "NY AM Silver Bullet", symbol="EURUSD",
                      min_target_pips=10_000) is None, \
        "unerfuellbares Mindestziel muss das Setup verwerfen"

    print("forex.rules demo: OK")


if __name__ == "__main__":
    demo()
