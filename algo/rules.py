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
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_ohlc import (Bar, at, fvgs, hp_context, untouched_levels,  # noqa: E402
                          session_windows, slice_between, CFG, SIZE_REL_MEDIAN)
from backtest_hp_fvg import bias_proxy  # noqa: E402
from pnl import round_to_tick  # noqa: E402

# Kerzen VOR dem Silver-Bullet-Fenster, die fvgs() als Kontext bekommt (Volatilitaet
# fuer size_rel, Swings fuer die Stark-Einstufung). Begrenzt, weil plan_trade je Kerze
# laeuft -- die volle Historie waere O(n^2) ueber einen Backtest.
CONTEXT_BARS = 60

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


def sb_entry_signal(bars: list[Bar], when: datetime, stop_buffer_pct: float = 0.1,
                     symbol: str = "MNQ", require_strong: bool = False,
                     min_size_rel: float | None = None
                     ) -> tuple[str, str, float, float] | None:
    """Silver-Bullet-Entry (Fenster + 1st Presented FVG -> Seite/Entry/Stop), OHNE die
    Ziel-Liquiditaet zu pruefen -- extrahiert aus `plan_trade()`, damit Backtests, die eine
    ANDERE Ziel-Logik testen wollen (z.B. algo/backtest_sb_session_liq.py, PDH/PDL/PWH/PWL
    statt Swing-Level), nicht die Entry-Erkennung duplizieren muessen. Rueckgabe
    (window_name, side, entry, stop) oder None. Kein Lookahead: nur bars[t<=when]."""
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
    #
    # Umgesetzt ueber `t_start` statt ueber einen harten Schnitt bei win_start: mitgegeben
    # werden zusaetzlich CONTEXT_BARS Kerzen VOR dem Fenster, damit fvgs() die lokale
    # Volatilitaet (size_rel) und die Swings ueberhaupt schaetzen kann -- ein bei win_start
    # abgeschnittener Datensatz liefert fuer das erste FVG size_rel=None. Der Kontext ist
    # bewusst begrenzt: plan_trade laeuft je Kerze, die volle Historie waere O(n^2).
    first = next((k for k, b in enumerate(hist) if b.t >= win_start), None)
    if first is None:
        return None
    win_bars = hist[max(0, first - CONTEXT_BARS):]
    if len(win_bars) < 3:
        return None
    window_fvgs = [g for g in fvgs(win_bars, tick=symbol) if g["t_start"] >= win_start]
    if not window_fvgs:
        return None

    # Das Silver-Bullet-Setup baut auf dem *1st Presented* FVG auf -- also weiter das erste
    # im Fenster, nicht das erste passende. Taugt es nichts, gibt es kein Setup, statt auf
    # ein spaeteres auszuweichen.
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

    # Auf das Tick-Raster zwingen: C.E. ist ein Mittelwert (landet zur Haelfte auf dem
    # 0,125-Raster) und der Stop-Puffer ist ein Prozentwert -- beides ergibt Preise, die es
    # am Markt nicht gibt und die IBKR nicht annimmt. Richtung immer konservativ, damit die
    # Rundung nie zugunsten des Backtests ausfaellt: Entry schwerer zu fuellen, Stop weiter
    # weg (groesserer Verlust), Ziel weiter weg (schwerer erreichbar).
    entry = round_to_tick(entry, symbol, "down" if side == "long" else "up")
    stop = round_to_tick(stop, symbol, "down" if side == "long" else "up")
    return window_name, side, entry, stop


def plan_trade(bars: list[Bar], when: datetime, stop_buffer_pct: float = 0.1,
                min_target_points: float = 10.0, symbol: str = "MNQ",
                require_strong: bool = False,
                min_size_rel: float | None = None,
                levels_bars: list[Bar] | None = None,
                target_candidates: list[dict] | None = None) -> TradeSetup | None:
    """Silver-Bullet-Setup zum Zeitpunkt `when`, oder None. Nur bars[t<=when] werden benutzt.

    `stop_buffer_pct` (Anteil der FVG-Groesse als SL-Puffer) ist optimierbar/testbar --
    siehe algo/backtest_walkforward.py (Parameter-Sensitivitaet, PLAN.md "Stop-Puffer
    vergroessern/testen"). `min_target_points`: Setup wird nur genommen, wenn Entry->Target
    mindestens so viele Punkte Potenzial hat (Nutzerregel, siehe wiki/models/Silver Bullet
    Model.md).

    `levels_bars`: optionale ANDERE Bar-Reihe (z.B. 15m/1m statt der 5m-Entry-Bars) fuer die
    Ziel-Liquiditaet (untouched_levels) -- Nutzer-These 2026-08-14 ("15m als Bellwether-Chart,
    1m fuer grosse Pools"), siehe algo/backtest_sb_bellwether.py. None (Default) = wie bisher
    dieselben Bars wie fuer den Entry (bit-identisches Verhalten zur alten Signatur).

    `target_candidates`: optionale FESTE Ziel-Level statt der swing-basierten
    untouched_levels() -- Format wie deren Rueckgabe (`[{"side": "buyside"|"sellside",
    "level": float}, ...]`). Fuer Session-Liquiditaet (PDH/PDL/PWH/PWL, Nutzer-These
    2026-08-14 "previous day/week High/Low sind starke DOL"), siehe
    algo/backtest_sb_session_liq.py. Ist ignoriert, wenn `levels_bars` gesetzt ist (beide
    ersetzen dieselbe Stelle; `target_candidates` gewinnt, wenn beide kommen). Der Aufrufer
    ist dafuer verantwortlich, nur noch UNBERUEHRTE Level hineinzugeben (kein impliziter
    Touch-Check hier, weil feste Session-Level anders geprueft werden als Swing-Level).

    `require_strong` / `min_size_rel` setzen die High-Probability-Bedingung um (Nutzerregel
    2026-08-13): nur ein FVG, dessen Displacement einen bestaetigten, noch intakten Swing
    per Close bricht (-> MSS/BOS) UND das relativ zur lokalen Kerzenrange nicht unter dem
    Median liegt. `min_size_rel` ist bewusst *relativ*: eine 1m-Kerze ist um 9:35 fast
    dreimal so gross wie um 4:00, eine absolute Punktschwelle waere sessionabhaengig
    falsch.

    ⚠️ **Beide stehen bewusst per Default AUS.** Gemessen am 13.08.2026 ueber
    `backtest_bt.py` verschlechtern sie dieses Setup deutlich, statt es zu verbessern:

        require_strong=False, min_size_rel=None   16 Trades   +2.194 USD   (Baseline)
        require_strong=True,  min_size_rel=None   10 Trades   -9.790 USD
        require_strong=True,  min_size_rel=0,45   11 Trades   -9.031 USD
        require_strong=False, min_size_rel=0,45   13 Trades   -6.281 USD

    Vermutete Ursache: das *1st Presented* FVG entsteht per Konstruktion frueh im Fenster,
    oft noch BEVOR Struktur genommen wird. Der Swing-Break-Filter waehlt damit systematisch
    spaetere, schon ausgedehnte Setups (Haltedauer steigt von 64 auf ~200 Bars). Bei n=10-16
    ist keine der Varianten von Rauschen unterscheidbar -- die Filter bleiben deshalb
    verfuegbar und getestet, aber nicht aktiv, bis mehr Daten vorliegen. Siehe
    wiki/synthesis/FVG-Stärke, Session-Volatilität & Confluence (laufend).md."""
    signal = sb_entry_signal(bars, when, stop_buffer_pct, symbol, require_strong, min_size_rel)
    if signal is None:
        return None
    window_name, side, entry, stop = signal
    hist = [b for b in bars if b.t <= when]

    if target_candidates is not None:
        levels = target_candidates
    else:
        lvl_hist = hist if levels_bars is None else [b for b in levels_bars if b.t <= when]
        levels = untouched_levels(lvl_hist, CFG["swing"])
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


def plan_trade_hp_fvg(bars: list[Bar], when: datetime, prev_day_hi: float, prev_day_lo: float,
                       symbol: str = "MNQ", stop_feld: str = "stop_c2",
                       ziel_pkt: float = 20.0, rr: float | None = None,
                       require_kz: bool = False, require_zone: bool = False,
                       require_bias: bool = False) -> TradeSetup | None:
    """High-Probability-FVG-Setup (ICT Private Mentorship "High Probability FVG's" +
    2024 Mentorship "How To Trade ICT FVGs Correctly", siehe wiki/concepts/Fair Value Gap
    (FVG).md). Anders als plan_trade() KEIN Fensterzwang -- der Backtest
    (algo/backtest_hp_fvg.py) lief ganztaegig, also handelt auch diese Regel ganztaegig.
    Nur bars[t<=when] werden benutzt.

    `prev_day_hi`/`prev_day_lo` (High/Low des VORHERGEHENDEN Handelstags) kommen als Parameter
    rein, statt hier selbst Tagesdateien zu laden -- der Aufrufer (Backtest/Live-Loop) kennt
    den Vortag ohnehin. Bewusst tagesskaliert, nicht auf beliebige Timeframes verallgemeinert:
    ICTs Quelle meint woertlich den vorherigen Handelstag, eine Verallgemeinerung waere eine
    neue, ungetestete These (siehe algo/PLAN.md Backlog "Regeln fraktal ueber TF/Markt").

    `require_kz`/`require_zone`/`require_bias` schalten die drei Masterclass-Kriterien
    (Killzone/Vortageshaelfte/Bias-Proxy) einzeln zu, alle per Default AUS: gemessen an
    7.375 FVGs bleibt die Kante duenn (36-38% Win bei 2R), Killzone allein ist nachweislich
    wirkungslos, und `fast` ("Kerze 4 laeuft sofort zurueck") ist bewusst NICHT als Filter
    aufgenommen, weil er die Kante in der Messung verschlechtert statt verbessert. Siehe
    wiki/concepts/Fair Value Gap (FVG).md -> "Wo High-Probability-FVGs entstehen" fuer die
    Zahlen. Der Bias-Proxy ist zudem nur eine Naeherung (Midnight Open vs. Vortages-
    Equilibrium), nicht ICTs handgesetzter Draw on Liquidity."""
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
    spanne = rr * risk if rr else ziel_pkt
    target = entry + spanne if side == "long" else entry - spanne

    return TradeSetup(t=when, window=ctx["killzone"] or "HP-FVG", side=side,
                       entry=entry, stop=stop, target=target)


# --------------------------------------------------------------------------- Liquiditaets-Wissen
#
# Vier Bausteine fuer algo/liquidity_report.py (2026-08-14, Nutzer-Session "Liquiditaeten
# definieren/erkennen"): reine Funktionen, kein Fensterzwang, kein Symbol-Bezug -- der
# Aufrufer laedt/kombiniert die Bars, hier steckt nur das Regelwissen. Absichtlich fraktal
# ueber Timeframes (1m/5m/15m/Daily nutzen dieselben Funktionen), siehe PLAN.md-Backlog
# "Regeln fraktal ueber Timeframe/Markt generalisieren".

def session_extrema(bars: list[Bar], day: date) -> dict:
    """Echte Session-High/Low (Asia/London/NY, siehe analyze_ohlc.session_windows) plus
    Midnight Open -- NICHT die fraktalen Swings aus swings()/untouched_levels(). Fund
    2026-08-14: ein Session-Extrem ist nicht zwingend ein gueltiger Swing-Punkt (braucht
    n Nachbarn auf beiden Seiten), das echte Tief/Hoch der Session kann dabei durchrutschen
    -- siehe wiki/log.md, "Ranking-Antwort hatte Swing-Punkt statt Session-Extrem gemeldet"."""
    out: dict[str, dict] = {}
    for name, start, end in session_windows(day):
        seg = slice_between(bars, start, end)
        if not seg:
            continue
        hi_bar = max(seg, key=lambda b: b.h)
        lo_bar = min(seg, key=lambda b: b.l)
        out[name] = {"hi": hi_bar.h, "hi_t": hi_bar.t, "lo": lo_bar.l, "lo_t": lo_bar.t}
    mo = next((b.o for b in bars if b.t >= at(day, 0, 0)), None)
    out["Midnight Open"] = mo
    return out


def ipda_windows(daily_bars: list[Bar], last_price: float | None = None) -> dict:
    """High/Low je IPDA-Lookback-Fenster (20/40/60 Tage, siehe wiki/concepts/IPDA Data
    Ranges.md) aus `daily_bars` (ein Bar je Handelstag, aufsteigend, letzter = aktuellster
    VOLLSTAENDIGER Handelstag). `complete` markiert, ob genug Historie fuer das Fenster
    vorliegt (bei begrenzter 5m-Verfuegbarkeit z.B. keine vollen 60 Tage).

    `active`: vereinfachte IPDA-Erweiterungsregel -- 20 Tage bleibt aktiv, solange
    `last_price` das 20-Tage-Low/-High noch nicht gerissen hat, sonst 40, sonst 60. Deckt
    nicht die volle ICT-Nuance ("nur erweitern, wenn im 40-Tage-Abschnitt KEIN neues Lower
    Low entstand") ab -- bewusst vereinfacht (YAGNI), bis eine feinere Version gebraucht wird."""
    out: dict = {}
    active = None
    for n in (20, 40, 60):
        win = daily_bars[-n:]
        complete = len(daily_bars) >= n
        hi = max(b.h for b in win) if win else None
        lo = min(b.l for b in win) if win else None
        out[n] = {"hi": hi, "lo": lo, "complete": complete}
        if active is None and win and (last_price is None or lo is None
                                        or last_price > lo):
            active = n
    out["active"] = active or 60
    return out


def rel_pair(left: dict, right: dict, side: str) -> dict | None:
    """Nutzerregel 2026-08-14 (siehe wiki/concepts/Open Float & Liquidity Pools.md, REH/REL):
    bei zwei nahen, aber nicht exakt gleichen Extremen (`left` zeitlich vor `right`, beide
    `{"level": float, ...}`) zaehlt nur das LINKE als noch unberuehrt -- und nur, wenn es
    weiter aussen liegt als das rechte (REH: links hoeher: REL: links tiefer). Liegt es
    naeher am Preis als rechts, hat rechts es bereits genommen -> kein gueltiges Paar mehr,
    `None`. Gibt bei Gueltigkeit `left` unveraendert zurueck (nicht kopiert/gemerged)."""
    if side == "buyside":
        return left if left["level"] > right["level"] else None
    return left if left["level"] < right["level"] else None


def level_untouched(hist: list[Bar], level: float, side: str) -> bool:
    """Ist `level` bis zum Ende von `hist` noch nicht gerissen? buyside: kein Hoch >= level,
    sellside: kein Tief <= level. Fuer PDH/PDL/PWH/PWL & Session-Level, die selbst keine
    Swing-Punkte sind (also nicht ueber untouched_levels() pruefbar)."""
    if side == "buyside":
        return all(b.h < level for b in hist)
    return all(b.l > level for b in hist)


def daily_hilo_from_bars(days_bars: dict[date, list[Bar]]) -> dict[date, tuple[float, float]]:
    """{Handelstag: (High, Low)} aus INTRADAY-Bars je Tag (z.B. 5m) statt aus den 1d-Dateien.

    ⚠️ Bewusst NICHT aus den 1d-Dateien: Fund 2026-08-14 (siehe algo/PLAN.md) -- mehrere
    1d-Dateien stehen nicht mehr im Einklang mit ihren eigenen Intraday-Dateien (u.a. 13.08.
    nach einer TradingView-Korrektur, die nur die Intraday-Dateien aktualisierte; 19.06. mit
    Werten des naechsten Handelstags dupliziert). Intraday-Aggregation umgeht das Problem
    strukturell, statt jede 1d-Datei einzeln gegenzupruefen."""
    return {d: (max(b.h for b in bars), min(b.l for b in bars))
            for d, bars in days_bars.items() if bars}


def prev_day_level(hilo: dict[date, tuple[float, float]], day: date) -> tuple[float, float] | None:
    """(PDH, PDL) -- High/Low des letzten Handelstags VOR `day` in `hilo`."""
    frueher = [d for d in hilo if d < day]
    return hilo[max(frueher)] if frueher else None


def prev_week_level(hilo: dict[date, tuple[float, float]], day: date) -> tuple[float, float] | None:
    """(PWH, PWL) -- High/Low ueber die zuletzt VOLLSTAENDIG abgeschlossene Kalenderwoche
    (Montag-Sonntag vor der Woche von `day`), unabhaengig davon, welche Handelstage darin
    tatsaechlich in `hilo` vorliegen (Feiertage etc.)."""
    this_monday = day - timedelta(days=day.weekday())
    prev_monday = this_monday - timedelta(days=7)
    prev_sunday = this_monday - timedelta(days=1)
    week_days = [d for d in hilo if prev_monday <= d <= prev_sunday]
    if not week_days:
        return None
    return (max(hilo[d][0] for d in week_days), min(hilo[d][1] for d in week_days))


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

    # Geometrie (Entry/Stop/Target) wird ohne die High-Probability-Filter geprueft -- die
    # haben eine eigene Sektion weiter unten.
    roh = dict(require_strong=False, min_size_rel=None)

    setup = plan_trade(bars, at(day, 10, 10), **roh)
    assert setup is not None
    assert setup.window == "NY AM Silver Bullet"
    assert setup.side == "long"
    assert setup.entry == (98 + 99) / 2
    assert setup.stop < 98
    assert setup.target == 110

    assert plan_trade(bars, at(day, 9, 0), **roh) is None  # ausserhalb jedes Fensters
    assert plan_trade(bars, at(day, 14, 30), **roh) is None  # PM-Fenster, kein FVG darin

    # levels_bars=None (Default) muss bit-identisch zum alten Verhalten sein (dieselben Bars).
    s_same = plan_trade(bars, at(day, 10, 10), levels_bars=bars, **roh)
    assert s_same is not None and (s_same.entry, s_same.stop, s_same.target) == \
        (setup.entry, setup.stop, setup.target)
    # levels_bars auf eine Reihe OHNE den Spike bei 9:30 -> keine Ziel-Liquiditaet -> kein Setup,
    # obwohl der Entry (aus `bars`) unveraendert ein gueltiges FVG haette.
    flach = [bar(9, 20, 95, 96, 94, 95.5), bar(9, 25, 95.5, 96, 95, 95.5)] + bars[2:]
    flach[2] = bar(9, 30, 95.5, 96, 95, 96)  # Spike entfernt -> keine unberuehrte Buyside
    assert plan_trade(bars, at(day, 10, 10), levels_bars=flach, **roh) is None, \
        "levels_bars muss die Ziel-Liquiditaet ersetzen, nicht nur ergaenzen"

    # target_candidates ersetzt untouched_levels() komplett -- ein festes Session-Level
    # (z.B. PDH) statt Swing-Erkennung.
    s_cand = plan_trade(bars, at(day, 10, 10), target_candidates=[
        {"side": "buyside", "level": 130.0}, {"side": "sellside", "level": 50.0}], **roh)
    assert s_cand is not None and s_cand.target == 130.0
    assert plan_trade(bars, at(day, 10, 10), target_candidates=[
        {"side": "sellside", "level": 50.0}], **roh) is None, \
        "kein passendes buyside-Kandidat -> kein Setup, auch wenn die Swing-Levels welche haetten"

    # High-Probability-Filter (2026-08-13, per Default AUS -- Begruendung im Docstring):
    # dasselbe FVG bricht keinen Swing, mit require_strong darf daraus kein Setup werden.
    assert plan_trade(bars, at(day, 10, 10), require_strong=True) is None, \
        "schwaches FVG (kein Swing-Break) darf require_strong nicht passieren"

    # Dieselben Bars, aber mit einem Swing High bei 9:45 (h=99), das die Displacement-Kerze
    # 10:05 per Close (100) nimmt -> starkes FVG, Setup kommt zustande. Entry/Stop/Target
    # bleiben unveraendert, der Filter aendert nur das Ob.
    stark = list(bars)
    stark[5] = bar(9, 45, 96.5, 99, 96, 97)
    s_stark = plan_trade(stark, at(day, 10, 10), require_strong=True)
    assert s_stark is not None, "FVG mit Swing-Break muss den Filter passieren"
    assert (s_stark.entry, s_stark.target) == (setup.entry, setup.target)

    # Groessenfilter mit unbekannter Groesse: in diesem Mini-Datensatz liegen vor dem FVG
    # nur 9 Kerzen, size_rel ist also None. None heisst "unbekannt", nicht "zu klein" --
    # selbst eine absurd hohe Schwelle darf das Setup dann NICHT wegfiltern.
    assert plan_trade(stark, at(day, 10, 10), require_strong=True,
                      min_size_rel=99) is not None, \
        "size_rel=None darf nicht als 'zu klein' behandelt werden"

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
    s2 = plan_trade(rand, at(day, 10, 20), **roh)
    assert s2 is not None
    assert s2.entry == (103 + 104) / 2, (
        f"randueberlappendes FVG genommen (C.E {s2.entry}) statt des innenliegenden 103.5")

    # Tick-Raster: MNQ handelt in 0,25-Schritten. Der Stop entsteht aus einem Prozent-Puffer
    # und landet ungerundet auf krummen Werten (hier 97.9) -- solche Orders nimmt IBKR nicht
    # an, und ein Backtest wuerde Fills an nie existierenden Preisen simulieren.
    for s in (setup, s2):
        for feld, wert in (("entry", s.entry), ("stop", s.stop), ("target", s.target)):
            assert abs(round(wert / 0.25) * 0.25 - wert) < 1e-9, \
                f"{feld} {wert} liegt nicht auf dem 0,25-Tick-Raster"
    assert setup.stop == 97.75, f"Stop muss konservativ abgerundet sein (97.75), war {setup.stop}"

    # --- plan_trade_hp_fvg: kein Fensterzwang, drei HP-Kriterien einzeln togglebar ---
    hp_bars = [
        bar(0, 0, 105, 106, 104, 105.5),    # Midnight Open 105, Vortag-EQ 100 -> Bias bullish
        bar(6, 55, 100, 101, 99, 100.5),    # a: h=101
        bar(7, 0, 100.5, 108, 100, 107),    # m: Displacement, Zeit 7:00 -> NY-Killzone
        bar(7, 5, 107, 109, 102, 108),      # c: l=102 > a.h=101 -> bullish FVG
    ]
    hp_setup = plan_trade_hp_fvg(hp_bars, at(day, 7, 10), 110.0, 90.0)
    assert hp_setup is not None and hp_setup.side == "long"

    # dieselbe Geometrie, nur zeitlich ausserhalb jeder Killzone verschoben (11:45-12:05)
    hp_bars_no_kz = [
        bar(11, 45, 105, 106, 104, 105.5),
        bar(11, 55, 100, 101, 99, 100.5),
        bar(12, 0, 100.5, 108, 100, 107),
        bar(12, 5, 107, 109, 102, 108),
    ]
    assert plan_trade_hp_fvg(hp_bars_no_kz, at(day, 12, 10), 110.0, 90.0,
                              require_kz=True) is None, \
        "FVG ausserhalb jeder Killzone darf require_kz nicht passieren"
    assert plan_trade_hp_fvg(hp_bars_no_kz, at(day, 12, 10), 110.0, 90.0) is not None, \
        "ohne Filter muss das Setup trotzdem zustande kommen -- kein Fensterzwang wie bei plan_trade"

    # Vortagesrange so verschoben, dass der C.E. in der FALSCHEN Haelfte liegt (EQ 250 statt 100)
    assert plan_trade_hp_fvg(hp_bars, at(day, 7, 10), 300.0, 200.0,
                              require_zone=True) is None, \
        "FVG in der falschen Vortageshaelfte darf require_zone nicht passieren"

    # Midnight Open unter der Equilibrium -> Bias-Proxy bearish, FVG aber bullish
    hp_bars_wrong_bias = list(hp_bars)
    hp_bars_wrong_bias[0] = bar(0, 0, 95, 96, 94, 95.5)
    assert plan_trade_hp_fvg(hp_bars_wrong_bias, at(day, 7, 10), 110.0, 90.0,
                              require_bias=True) is None, \
        "Bias-Proxy gegen die FVG-Seite darf require_bias nicht passieren"

    # rr-Modus: Ziel als Vielfaches des Stopabstands statt fester Punkte
    hp_rr = plan_trade_hp_fvg(hp_bars, at(day, 7, 10), 110.0, 90.0, rr=2.0)
    risk = abs(hp_rr.entry - hp_rr.stop)
    assert abs(abs(hp_rr.target - hp_rr.entry) - 2 * risk) < 1e-9

    print("plan_trade demo ok:", setup)
    print("plan_trade_hp_fvg demo ok:", hp_setup)

    # --- session_extrema: echtes Session-Tief statt fraktalem Swing ---
    # London (02:00-05:00): das Tief 96.0 bei 02:30 hat KEINEN gueltigen Swing-Nachbarn
    # (nur eine Kerze tief), waere also fuer swings()/untouched_levels() unsichtbar.
    se_bars = [
        bar(2, 0, 100, 101, 99, 100),
        bar(2, 15, 100, 100.5, 98, 99),
        bar(2, 30, 99, 99.5, 96.0, 97),   # Session-Tief
        bar(2, 45, 97, 98, 96.5, 97.5),
    ]
    se = session_extrema(se_bars, day)
    assert se["London Range"]["lo"] == 96.0, se["London Range"]
    assert se["London Range"]["hi"] == 101.0

    # --- ipda_windows: 20/40/60-Tage-Fenster + aktives Fenster ---
    daily = [bar(0, 0, 100 + i, 105 + i, 95 + i, 100 + i) for i in range(50)]
    ipda = ipda_windows(daily)
    assert ipda[20]["lo"] == 95 + 30 and ipda[20]["complete"] is True
    assert ipda[60]["complete"] is False, "nur 50 Tage vorhanden -> 60-Tage-Fenster unvollstaendig"
    # last_price noch UEBER dem 20-Tage-Low -> 20 bleibt aktiv
    assert ipda_windows(daily, last_price=200.0)["active"] == 20
    # last_price UNTER dem 20-Tage-Low -> erweitert auf 40
    assert ipda_windows(daily, last_price=daily[-20].l - 1)["active"] == 40

    # --- rel_pair: links hoeher/tiefer als rechts = noch gueltig ---
    links_hoch, rechts_hoch = {"level": 110.0}, {"level": 105.0}
    assert rel_pair(links_hoch, rechts_hoch, "buyside") == links_hoch, \
        "links hoeher als rechts -> links noch unberuehrt"
    assert rel_pair(rechts_hoch, links_hoch, "buyside") is None, \
        "links (105) niedriger als rechts (110) -> bereits genommen, kein Paar"
    links_tief, rechts_tief = {"level": 90.0}, {"level": 95.0}
    assert rel_pair(links_tief, rechts_tief, "sellside") == links_tief

    # --- level_untouched ---
    hist_lvl = [bar(9, 30, 100, 102, 99, 101)]
    assert level_untouched(hist_lvl, 110.0, "buyside") is True
    assert level_untouched(hist_lvl, 101.5, "buyside") is False, "Hoch 102 > 101.5 -> gerissen"
    assert level_untouched(hist_lvl, 90.0, "sellside") is True
    assert level_untouched(hist_lvl, 99.5, "sellside") is False, "Tief 99 < 99.5 -> gerissen"

    # --- daily_hilo_from_bars + prev_day_level/prev_week_level ---
    d1, d2, d3 = date(2026, 1, 5), date(2026, 1, 6), date(2026, 1, 12)  # Mo, Di, naechster Mo
    hilo = daily_hilo_from_bars({
        d1: [bar(0, 0, 100, 105, 95, 100)],
        d2: [bar(0, 0, 100, 108, 96, 100)],
    })
    assert hilo[d1] == (105.0, 95.0) and hilo[d2] == (108.0, 96.0)
    assert prev_day_level(hilo, d2) == (105.0, 95.0)
    assert prev_day_level(hilo, d1) is None, "kein Vortag vorhanden -> None"
    assert prev_week_level(hilo, d3) == (108.0, 95.0), "PWH aus d2, PWL aus d1"
    assert prev_week_level(hilo, d1) is None, "keine Vorwoche vorhanden -> None"

    print("liquidity-helpers demo ok")


if __name__ == "__main__":
    demo()
