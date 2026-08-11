#!/usr/bin/env python3
"""Regel-Schicht aus algo/PLAN.md, Code-Idee 2: plan_trade(bars, when) -> TradeSetup | None.

Erste konkrete Regel: Silver Bullet Model (siehe wiki/models/Silver Bullet Model.md,
wiki/sources/ICT Silver Bullet (Source).md). Baut nur auf bestehenden Detektoren aus
tools/analyze_ohlc.py auf (fvgs, untouched_levels) -- keine Neuimplementierung.

Regel, so wie sie im Wiki steht:
  1. `when` muss in einem der drei Fenster liegen (London 3-4, NY AM 10-11, NY PM 14-15 Uhr NY).
  2. Erstes FVG, das innerhalb des Fensters entstanden und bis `when` bestaetigt ist -> Setup.
  3. Richtung = FVG-Seite (bullish FVG -> long, bearish FVG -> short).
  4. Entry = FVG-C.E. (50%-Linie), Stop = FVG-Gegenkante + kleiner Puffer.
  5. Target = naechstes noch unberuehrtes Liquiditaets-Level (untouched_levels) in Traderichtung
     -- ohne Zielliquiditaet kein Setup (die Quelle verlangt Confluenz mit einem Ziel).
  6. Mindestabstand Entry->Target: `min_target_points` (Default 10) -- Setup ohne genug
     Potenzial wird nicht genommen (siehe wiki/models/Silver Bullet Model.md, "Trade
     Management"). Partial-Taking an Swing-Punkten + Stop-auf-Breakeven danach passiert
     als Trade-Management NACH Entry, nicht hier -- siehe algo/backtest_ensemble.py.

Kein Lookahead: alle Detektoren laufen nur auf bars mit t <= when, nie auf der vollen Reihe --
sonst waere der Backtest gegen die eigene Zukunft geloest.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from analyze_ohlc import Bar, at, fvgs, untouched_levels, CFG  # noqa: E402

# (Name, Start-Stunde, End-Stunde) in NY-Zeit, siehe wiki/models/Silver Bullet Model.md
WINDOWS = [
    ("London Silver Bullet", 3, 4),
    ("NY AM Silver Bullet", 10, 11),
    ("NY PM Silver Bullet", 14, 15),
]


@dataclass
class TradeSetup:
    t: datetime
    window: str
    side: str  # "long" | "short"
    entry: float
    stop: float
    target: float


def _active_window(day: date, when: datetime) -> tuple[str, datetime] | None:
    for name, h0, h1 in WINDOWS:
        start = at(day, h0)
        if start <= when < at(day, h1):
            return name, start
    return None


def plan_trade(bars: list[Bar], when: datetime, stop_buffer_pct: float = 0.1,
                min_target_points: float = 10.0) -> TradeSetup | None:
    """Silver-Bullet-Setup zum Zeitpunkt `when`, oder None. Nur bars[t<=when] werden benutzt.

    `stop_buffer_pct` (Anteil der FVG-Groesse als SL-Puffer) ist optimierbar/testbar --
    siehe algo/backtest_walkforward.py (Parameter-Sensitivitaet, PLAN.md "Stop-Puffer
    vergroessern/testen"). `min_target_points`: Setup wird nur genommen, wenn Entry->Target
    mindestens so viele Punkte Potenzial hat (Nutzerregel, siehe wiki/models/Silver Bullet
    Model.md)."""
    win = _active_window(when.date(), when)
    if win is None:
        return None
    window_name, win_start = win

    hist = [b for b in bars if b.t <= when]
    if len(hist) < 3:
        return None

    # Die 3-Kerzen-Formation muss KOMPLETT im Fenster liegen: ein FVG, dessen mittlere
    # Kerze exakt auf win_start faellt, beginnt eine Kerze davor -- also ausserhalb der
    # Session. Darum das Fenster vor der Detektion schneiden statt danach auf g["t"]
    # (= mittlere Kerze) zu filtern. Siehe wiki/concepts/ORG (Opening Range Gap) &
    # 1st Presented FVG.md ("fuer die 9:30-Session zaehlt das 1.p FVG ab 9:31").
    #
    # Wichtig (Jannes, 2026-08-11): ein randueberlappendes FVG ist NICHT ungueltig -- es
    # bleibt ein normales FVG/PD Array. Es ist nur kein *1st Presented* FVG, und genau
    # darauf baut das Silver-Bullet-Setup hier auf.
    win_bars = [b for b in hist if b.t >= win_start]
    if len(win_bars) < 3:
        return None
    window_fvgs = fvgs(win_bars)
    if not window_fvgs:
        return None
    fvg = window_fvgs[0]  # erstes FVG im Fenster

    side = "long" if fvg["side"] == "bullish" else "short"
    entry = fvg["ce"]
    buffer = stop_buffer_pct * fvg["size"]
    stop = fvg["lo"] - buffer if side == "long" else fvg["hi"] + buffer

    levels = untouched_levels(hist, CFG["swing"])
    if side == "long":
        candidates = [lv["level"] for lv in levels if lv["side"] == "buyside" and lv["level"] > entry]
        target = min(candidates) if candidates else None
    else:
        candidates = [lv["level"] for lv in levels if lv["side"] == "sellside" and lv["level"] < entry]
        target = max(candidates) if candidates else None
    if target is None:
        return None  # keine Zielliquiditaet -> Quelle fordert Confluenz, kein Setup ohne Ziel
    if abs(target - entry) < min_target_points:
        return None  # zu wenig Potenzial fuers Mindest-Handle-Ziel

    return TradeSetup(t=when, window=window_name, side=side, entry=entry, stop=stop, target=target)


def demo() -> None:
    """Selbstcheck mit synthetischen Bars: FVG + Ziel-Liquiditaet -> long-Setup; ausserhalb
    des Fensters bzw. ohne FVG im Fenster -> kein Setup."""
    day = date(2026, 8, 3)

    def bar(hh, mm, o, h, l, c):
        return Bar(at(day, hh, mm), o, h, l, c)

    # Ueberlappende Ranges vor 10:00, damit dort kein FVG entsteht (nur der Spike bei 9:30
    # liefert die spaeter unberuehrte Buyside-Liquiditaet). Erst 10:00-10:10 (a/b/c) bildet
    # die beabsichtigte FVG im NY-AM-Fenster.
    bars = [
        bar(9, 20, 95, 96, 94, 95.5),
        bar(9, 25, 95.5, 96, 95, 95.5),
        bar(9, 30, 95.5, 110, 95, 96),   # Spike -> spaeter unberuehrte Buyside-Liquiditaet
        bar(9, 35, 96, 97, 95.5, 96.5),
        bar(9, 40, 96.5, 97, 96, 96.5),
        bar(9, 45, 96.5, 97.5, 96, 97),
        bar(9, 50, 97, 97.5, 96.5, 97),
        bar(9, 55, 97, 97.5, 96.5, 97.2),
        bar(10, 0, 97.2, 98, 97, 97.8),      # a: h=98
        bar(10, 5, 97.8, 101, 97.4, 100),    # b: Displacement-Kerze
        bar(10, 10, 100, 102, 99, 101),      # c: l=99 > a.h=98 -> bullish FVG bei 10:05
    ]

    setup = plan_trade(bars, at(day, 10, 10))
    assert setup is not None
    assert setup.window == "NY AM Silver Bullet"
    assert setup.side == "long"
    assert setup.entry == (98 + 99) / 2
    assert setup.stop < 98
    assert setup.target == 110

    assert plan_trade(bars, at(day, 9, 0)) is None  # ausserhalb jedes Fensters
    assert plan_trade(bars, at(day, 14, 30)) is None  # PM-Fenster, aber kein FVG darin

    # Grenzfall Session-Rand: ein FVG, dessen MITTLERE Kerze exakt auf den Fensterstart
    # (10:00) faellt, beginnt eine Kerze davor (9:55) und liegt damit nicht komplett im
    # Fenster -- es zaehlt nicht als erstes FVG der Session. Genommen werden muss das
    # spaetere, vollstaendig innenliegende FVG (10:10/10:15/10:20, C.E 103.5).
    rand = [
        bar(9, 20, 95, 96, 94, 95.5),
        bar(9, 25, 95.5, 96, 95, 95.5),
        bar(9, 30, 95.5, 130, 95, 96),        # Spike -> unberuehrte Buyside 130
        bar(9, 35, 96, 97, 95.5, 96.5),
        bar(9, 40, 96.5, 97, 96, 96.5),
        bar(9, 45, 96.5, 97.5, 96, 97),
        bar(9, 50, 97, 97.5, 96.5, 97),
        bar(9, 55, 97, 98, 96.5, 97.5),       # a1: h=98  (VOR dem Fenster)
        bar(10, 0, 97.5, 101, 97.4, 100),     # b1: mittlere Kerze == win_start
        bar(10, 5, 100, 102, 99, 101),        # c1: l=99 > 98 -> FVG, aber randueberlappend
        bar(10, 10, 101, 103, 100.5, 102),    # a2: h=103
        bar(10, 15, 102, 106, 101.5, 105),    # b2
        bar(10, 20, 105, 108, 104, 107),      # c2: l=104 > 103 -> erstes gueltiges FVG
    ]
    s2 = plan_trade(rand, at(day, 10, 20))
    assert s2 is not None
    assert s2.entry == (103 + 104) / 2, (
        f"randueberlappendes FVG genommen (C.E {s2.entry}) statt des innenliegenden 103.5")

    print("plan_trade demo ok:", setup)


if __name__ == "__main__":
    demo()
