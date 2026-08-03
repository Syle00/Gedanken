#!/usr/bin/env python3
"""Analysiert TradingView-OHLC-Exporte nach ICT-Kriterien.

Liest die CSVs aus raw/marktdaten/ und rechnet aus, was auf einem Screenshot nur
geschaetzt werden kann: Session-Level, Liquidity Sweeps, Displacement, FVGs,
Market-Structure-Breaks, Macro-Fenster.

Konvention fuer Dateinamen:  raw/marktdaten/<SYMBOL> <YYYY-MM-DD> <TF>.csv
Das Datum ist der Handelstag, um den es geht (letzte Kerze), TF eines von
1m 5m 15m 1h 4h 1d.

Aufruf:
    python tools/analyze_ohlc.py MNQ 2026-07-31              # Tagesreport
    python tools/analyze_ohlc.py MNQ 2026-07-31 --at 10:52   # Setup-Checkliste
    python tools/analyze_ohlc.py MNQ 2026-07-31 --tf 5m
    python tools/analyze_ohlc.py MNQ 2026-07-31 -o bericht.md

Nur Standardbibliothek. Zeiten immer New York.
"""

from __future__ import annotations

import argparse
import csv
import statistics
import sys
from dataclasses import dataclass
from datetime import datetime, time as dtime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

NY = ZoneInfo("America/New_York")
UTC = ZoneInfo("UTC")

DATA_DIR = Path(__file__).resolve().parent.parent / "raw" / "marktdaten"

TF_MINUTES = {"1m": 1, "5m": 5, "15m": 15, "1h": 60, "4h": 240, "1d": 1440}

# Rauschfilter — per CLI justierbar. min_age/min_swing in Kerzen des Basis-TF,
# min_pen in Vielfachen der Median-Kerzenrange.
CFG = {"swing": 2, "min_age": 15, "min_pen": 0.75, "disp_factor": 2.0, "confirm": 5}


# --------------------------------------------------------------------------- Daten

@dataclass
class Bar:
    t: datetime          # Open-Zeit der Kerze, NY
    o: float
    h: float
    l: float
    c: float
    v: float | None = None

    @property
    def rng(self) -> float:
        return self.h - self.l

    @property
    def body(self) -> float:
        return abs(self.c - self.o)

    @property
    def bull(self) -> bool:
        return self.c >= self.o

    def hm(self) -> str:
        return self.t.strftime("%H:%M")


def load(path: Path) -> list[Bar]:
    bars: list[Bar] = []
    with path.open(newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            raw_t = row["time"].strip()
            if raw_t.lstrip("-").isdigit():
                ts = datetime.fromtimestamp(int(raw_t), UTC).astimezone(NY)
            else:
                ts = datetime.fromisoformat(raw_t.replace("Z", "+00:00"))
                ts = ts.astimezone(NY) if ts.tzinfo else ts.replace(tzinfo=NY)
            vol = row.get("Volume") or row.get("volume")
            bars.append(Bar(
                ts, float(row["open"]), float(row["high"]),
                float(row["low"]), float(row["close"]),
                float(vol) if vol not in (None, "", "NaN") else None,
            ))
    bars.sort(key=lambda b: b.t)
    return bars


def find_files(symbol: str, day: str) -> dict[str, Path]:
    """Sucht im Tagesordner (jjjj/mm/dd.mm.jjjj), im alten flachen Tagesordner
    (dd.mm.jjjj, vor der Jahr/Monat-Verschachtelung) und, als letzter Rueckfall,
    flach in raw/marktdaten/."""
    iso = datetime.strptime(day, "%Y-%m-%d").date()
    roots = [DATA_DIR / iso.strftime("%Y") / iso.strftime("%m") / iso.strftime("%d.%m.%Y"),
             DATA_DIR / iso.strftime("%d.%m.%Y"), DATA_DIR]
    out = {}
    for tf in TF_MINUTES:
        for root in roots:
            p = root / f"{symbol} {day} {tf}.csv"
            if p.exists():
                out[tf] = p
                break
    return out


def slice_between(bars: list[Bar], start: datetime, end: datetime) -> list[Bar]:
    return [b for b in bars if start <= b.t < end]


# --------------------------------------------------------------------------- Sessions

def at(day, hh, mm=0) -> datetime:
    return datetime.combine(day, dtime(hh, mm), tzinfo=NY)


def session_windows(day):
    """(Name, Start, Ende) in NY-Zeit. Quelle: wiki/concepts/ICT Daily Range Session Timing.md"""
    prev = day - timedelta(days=1)
    return [
        ("Asian Range",     at(prev, 20), at(day, 0)),
        ("London Range",    at(day, 1),   at(day, 5)),
        ("London Lunch",    at(day, 5),   at(day, 7)),
        ("NY AM",           at(day, 7),   at(day, 10)),
        ("Premarket",       at(day, 7),   at(day, 9, 30)),
        ("London Close",    at(day, 10),  at(day, 12)),
        ("Lunch",           at(day, 12),  at(day, 13)),
        ("NY PM",           at(day, 13),  at(day, 16)),
        ("RTH (9:30-16)",   at(day, 9, 30), at(day, 16)),
        ("IPDA True Range", at(day, 0),   at(day, 15)),
    ]


def macro_windows(day):
    """Jannes' durchgehendes Stundenraster: XX:50 - XX+1:10, 24 Fenster."""
    out = []
    for h in range(24):
        start = at(day, h, 50) - timedelta(hours=1) if h == 0 else at(day, h - 1, 50)
        out.append((f"{start.strftime('%H:%M')}-{(start + timedelta(minutes=20)).strftime('%H:%M')}",
                    start, start + timedelta(minutes=20)))
    return out


def open_price(bars: list[Bar], when: datetime) -> float | None:
    """Open der Kerze, die genau bei `when` startet (bzw. der ersten danach)."""
    for b in bars:
        if b.t == when:
            return b.o
        if b.t > when:
            return b.o
    return None


# --------------------------------------------------------------------------- Detektoren

def swings(bars: list[Bar], n: int = 2):
    """Fraktale Swing Points. Liefert (index, 'high'|'low', preis)."""
    out = []
    for i in range(n, len(bars) - n):
        window = bars[i - n:i + n + 1]
        if bars[i].h == max(b.h for b in window) and \
                all(bars[i].h > b.h for b in window if b is not bars[i]):
            out.append((i, "high", bars[i].h))
        if bars[i].l == min(b.l for b in window) and \
                all(bars[i].l < b.l for b in window if b is not bars[i]):
            out.append((i, "low", bars[i].l))
    return out


def _swings_by_confirmation(bars: list[Bar], n: int):
    """Swings, indiziert nach dem Bar, ab dem sie in Echtzeit bekannt waeren."""
    out: dict[int, list] = {}
    for idx, kind, price in swings(bars, n):
        out.setdefault(idx + n, []).append((kind, price, idx))
    return out


def sweeps(bars: list[Bar], n: int = 2, min_age: int = 15,
           min_pen: float | None = None, confirm: int = 5):
    """Liquidity Sweep: Docht nimmt einen *stehengebliebenen* Swing, Preis kommt zurueck.

    Ein Level, das drei Kerzen alt ist, ist keine Liquiditaet — deshalb `min_age`
    (Mindestalter in Kerzen) und `min_pen` (Mindestdurchstich, default 0,75x
    Median-Kerzenrange).

    `confirm` ist das Fenster, in dem der Preis zurueckerobern muss. Ein Sweep, der
    erst nach drei Kerzen zurueckkommt, bleibt ein Sweep — nur wenn der Preis
    laenger als `confirm` Kerzen jenseits des Levels schliesst, war es ein echter
    Break und kein Stop Hunt. Genau daran scheitert die naive Ein-Kerzen-Regel:
    sie uebersieht den Judas Swing.
    """
    if min_pen is None:
        min_pen = 0.75 * (statistics.median(b.rng for b in bars) or 1.0)
    conf = _swings_by_confirmation(bars, n)
    live: list[tuple[str, float, int]] = []   # noch nicht genommene Swings
    out = []
    for j, b in enumerate(bars):
        live.extend(conf.get(j, []))
        keep = []
        for kind, level, idx in live:
            taken = (b.h > level) if kind == "high" else (b.l < level)
            if not taken:
                keep.append((kind, level, idx))
                continue
            age = j - idx
            if age < min_age:
                continue
            # maximale Auslenkung und Rueckeroberung im Bestaetigungsfenster
            window = bars[j:j + confirm + 1]
            pen = max((w.h - level) if kind == "high" else (level - w.l) for w in window)
            back_at = None
            for k, w in enumerate(window):
                if (w.c < level) if kind == "high" else (w.c > level):
                    back_at = j + k
                    break
            if back_at is not None and pen >= min_pen:
                out.append({"t": b.t, "side": "buyside" if kind == "high" else "sellside",
                            "level": level, "pen": pen, "swing_t": bars[idx].t,
                            "age": age, "reclaim_t": bars[back_at].t,
                            "bars_back": back_at - j})
        live = keep
    # pro Kerze und Seite nur den groessten Durchstich
    dedup: dict = {}
    for s in out:
        key = (s["t"], s["side"])
        if key not in dedup or s["pen"] > dedup[key]["pen"]:
            dedup[key] = s
    return sorted(dedup.values(), key=lambda d: d["t"])


def structure_breaks(bars: list[Bar], n: int = 2, min_age: int = 10):
    """Sequenzieller Structure-Tracker statt Paarweise-Vergleich.

    Gebrochen wird immer nur der *zuletzt bestaetigte, noch intakte* Swing —
    dadurch entsteht pro echtem Richtungswechsel ein Event und nicht dreissig.
    BOS = Fortsetzung, CHoCH = erster Break gegen die laufende Richtung.
    """
    conf = _swings_by_confirmation(bars, n)
    last_high = last_low = None       # (index, preis)
    trend = None
    out = []
    for j, b in enumerate(bars):
        for kind, price, idx in conf.get(j, []):
            if kind == "high":
                if last_high is None or price > last_high[1] or idx > last_high[0]:
                    last_high = (idx, price)
            else:
                if last_low is None or price < last_low[1] or idx > last_low[0]:
                    last_low = (idx, price)
        if last_high and b.c > last_high[1] and j - last_high[0] >= min_age:
            typ = "CHoCH" if trend == "bearish" else "BOS"
            out.append({"t": b.t, "dir": "bullish", "type": typ,
                        "level": last_high[1], "close": b.c,
                        "swing_t": bars[last_high[0]].t})
            trend, last_high, last_low = "bullish", None, None
        elif last_low and b.c < last_low[1] and j - last_low[0] >= min_age:
            typ = "CHoCH" if trend == "bullish" else "BOS"
            out.append({"t": b.t, "dir": "bearish", "type": typ,
                        "level": last_low[1], "close": b.c,
                        "swing_t": bars[last_low[0]].t})
            trend, last_high, last_low = "bearish", None, None
    return out


def displacements(bars: list[Bar], lookback: int = 20, factor: float = 2.0,
                  body_ratio: float = 0.5):
    """Kerzen mit ueberdurchschnittlicher Range und klarem Koerper."""
    out = []
    for i in range(lookback, len(bars)):
        ref = statistics.median(b.rng for b in bars[i - lookback:i]) or 0.0
        if ref <= 0:
            continue
        b = bars[i]
        if b.rng >= factor * ref and b.rng > 0 and b.body / b.rng >= body_ratio:
            out.append({"t": b.t, "dir": "bullish" if b.bull else "bearish",
                        "rng": b.rng, "body": b.body, "x": b.rng / ref,
                        "o": b.o, "c": b.c})
    return out


def fvgs(bars: list[Bar], min_size: float = 0.0):
    """3-Kerzen-FVG. Fuellstand wird ueber alle Folgekerzen geprueft."""
    out = []
    for i in range(1, len(bars) - 1):
        a, c = bars[i - 1], bars[i + 1]
        if c.l > a.h and c.l - a.h > min_size:
            lo, hi, side = a.h, c.l, "bullish"
        elif c.h < a.l and a.l - c.h > min_size:
            lo, hi, side = c.h, a.l, "bearish"
        else:
            continue
        ce = (lo + hi) / 2
        rest = bars[i + 2:]
        touched = ce_hit = filled = False
        fill_t = None
        for b in rest:
            if b.l <= hi and b.h >= lo:
                touched = True
                if b.l <= ce <= b.h:
                    ce_hit = True
                if (side == "bullish" and b.l <= lo) or (side == "bearish" and b.h >= hi):
                    filled = True
                    fill_t = b.t
                    break
        out.append({"t": bars[i].t, "side": side, "lo": lo, "hi": hi, "ce": ce,
                    "size": hi - lo, "touched": touched, "ce_hit": ce_hit,
                    "filled": filled, "fill_t": fill_t})
    return out


def untouched_levels(bars: list[Bar], n: int = 2):
    """Swing H/L, die bis zum Ende der Daten nie wieder genommen wurden.

    Das sind die Kandidaten fuer 'Target Liquiditaet min. 2 H/L 1m'.
    """
    sw = swings(bars, n)
    out = []
    for idx, kind, level in sw:
        rest = bars[idx + n + 1:]
        if kind == "high" and all(b.h <= level for b in rest):
            out.append({"t": bars[idx].t, "side": "buyside", "level": level})
        if kind == "low" and all(b.l >= level for b in rest):
            out.append({"t": bars[idx].t, "side": "sellside", "level": level})
    return out


def consolidations(bars: list[Bar], min_bars: int = 10, factor: float = 1.5):
    """Zusammenhaengende Abschnitte, deren Gesamtrange klein bleibt.

    Schwelle = factor * Median-Range einer einzelnen Kerze * sqrt(min_bars).
    """
    if len(bars) < min_bars:
        return []
    med = statistics.median(b.rng for b in bars) or 1.0
    thresh = factor * med * (min_bars ** 0.5)
    out = []
    i = 0
    while i <= len(bars) - min_bars:
        j = i + min_bars
        while j <= len(bars):
            seg = bars[i:j]
            if max(b.h for b in seg) - min(b.l for b in seg) > thresh:
                break
            j += 1
        length = j - 1 - i
        if length >= min_bars:
            seg = bars[i:i + length]
            out.append({"start": seg[0].t, "end": seg[-1].t, "bars": length,
                        "hi": max(b.h for b in seg), "lo": min(b.l for b in seg)})
            i += length
        else:
            i += 1
    return out


# --------------------------------------------------------------------------- Report

def fmt(p: float) -> str:
    return f"{p:,.2f}".replace(",", " ")


def hilo(bars: list[Bar]):
    if not bars:
        return None
    hb = max(bars, key=lambda b: b.h)
    lb = min(bars, key=lambda b: b.l)
    return {"hi": hb.h, "hi_t": hb.t, "lo": lb.l, "lo_t": lb.t,
            "o": bars[0].o, "c": bars[-1].c}


def day_report(symbol, day, data: dict[str, list[Bar]], tf: str) -> list[str]:
    bars = data[tf]
    L = []
    L.append(f"# {symbol} — {day.isoformat()} ({day.strftime('%A')})")
    L.append("")
    L.append(f"Basis: `{tf}`, {len(bars)} Kerzen, "
             f"{bars[0].t.strftime('%d.%m. %H:%M')} – {bars[-1].t.strftime('%d.%m. %H:%M')} NY. "
             f"Alle Zeiten New York.")
    L.append("")

    # -- Anker
    L.append("## Opening Prices")
    L.append("")
    L.append("| Anker | Preis |")
    L.append("|---|---|")
    for label, when in [("Midnight Open (00:00)", at(day, 0)),
                        ("8:30 Open (NY AM)", at(day, 8, 30)),
                        ("9:30 Open (RTH)", at(day, 9, 30)),
                        ("13:30 Open (PM)", at(day, 13, 30))]:
        p = open_price(bars, when)
        if p is not None:
            L.append(f"| {label} | {fmt(p)} |")
    L.append("")

    # -- Sessions
    L.append("## Session-Level")
    L.append("")
    L.append("| Session | Open | High (Zeit) | Low (Zeit) | Range | Equilibrium |")
    L.append("|---|---|---|---|---|---|")
    for name, s, e in session_windows(day):
        seg = slice_between(bars, s, e)
        d = hilo(seg)
        if not d:
            continue
        L.append(f"| {name} | {fmt(d['o'])} | {fmt(d['hi'])} ({d['hi_t'].strftime('%H:%M')}) "
                 f"| {fmt(d['lo'])} ({d['lo_t'].strftime('%H:%M')}) "
                 f"| {fmt(d['hi'] - d['lo'])} | {fmt((d['hi'] + d['lo']) / 2)} |")
    L.append("")

    day_bars = slice_between(bars, at(day, 0), at(day, 17))
    d = hilo(day_bars)
    if d:
        L.append(f"**Tages-High** {fmt(d['hi'])} um {d['hi_t'].strftime('%H:%M')} · "
                 f"**Tages-Low** {fmt(d['lo'])} um {d['lo_t'].strftime('%H:%M')} · "
                 f"Range {fmt(d['hi'] - d['lo'])} Pkt · EQ {fmt((d['hi'] + d['lo']) / 2)}")
        L.append("")

    # -- HTF-Kontext
    if "1d" in data:
        # Tageskerzen oeffnen um 18:00 NY (CME-Session-Start) -- eine Kerze mit
        # Open-Zeitstempel "Vortag 18:00" gehoert zum Handelstag danach, nicht davor.
        dailies = [b for b in data["1d"]
                   if (b.t.date() if b.t.hour < 18 else (b.t + timedelta(days=1)).date()) < day]
        if len(dailies) >= 5:
            last5 = dailies[-5:]
            rngs = [b.rng for b in last5]
            L.append("## HTF-Kontext")
            L.append("")
            L.append(f"- 5-Tage-Range als Erwartungsanker: "
                     f"{fmt(min(rngs))}–{fmt(max(rngs))} Pkt, Median {fmt(statistics.median(rngs))}")
            if d:
                actual = d["hi"] - d["lo"]
                verdict = ("im Rahmen" if min(rngs) <= actual <= max(rngs)
                           else "kleiner als erwartet" if actual < min(rngs) else "groesser als erwartet")
                L.append(f"- Tatsaechliche Tagesrange: {fmt(actual)} Pkt — **{verdict}**")
            prev = dailies[-1]
            L.append(f"- Vortag: O {fmt(prev.o)} H {fmt(prev.h)} L {fmt(prev.l)} C {fmt(prev.c)}")
            L.append("")

    # -- Sweeps
    med_bar = statistics.median(b.rng for b in bars) or 1.0
    sw = [s for s in sweeps(bars, CFG["swing"], CFG["min_age"], CFG["min_pen"] * med_bar,
                 CFG["confirm"])
          if at(day, 0) <= s["t"] < at(day, 17)]
    L.append(f"## Liquidity Sweeps ({len(sw)})")
    L.append("")
    if sw:
        L.append("| Zeit | Seite | Genommenes Level | Level stand seit | Alter | Penetration | zurueck |")
        L.append("|---|---|---|---|---|---|---|")
        for s in sw:
            back = "sofort" if s["bars_back"] == 0 else f"nach {s['bars_back']}"
            L.append(f"| {s['t'].strftime('%H:%M')} | {s['side']} | {fmt(s['level'])} "
                     f"| {s['swing_t'].strftime('%H:%M')} | {s['age']} Kerzen "
                     f"| {s['pen']:.2f} Pkt | {back} |")
    else:
        L.append("_keine_")
    L.append("")

    # -- Structure
    sb = [x for x in structure_breaks(bars, CFG["swing"], CFG["min_age"])
          if at(day, 0) <= x["t"] < at(day, 17)]
    L.append(f"## Market Structure Breaks ({len(sb)})")
    L.append("")
    if sb:
        L.append("| Zeit | Typ | Richtung | gebrochenes Level | Close |")
        L.append("|---|---|---|---|---|")
        for x in sb:
            L.append(f"| {x['t'].strftime('%H:%M')} | {x['type']} | {x['dir']} "
                     f"| {fmt(x['level'])} | {fmt(x['close'])} |")
    else:
        L.append("_keine_")
    L.append("")

    # -- Displacement
    dp = [x for x in displacements(bars, factor=CFG["disp_factor"])
          if at(day, 0) <= x["t"] < at(day, 17)]
    dp.sort(key=lambda x: -x["rng"])
    L.append(f"## Displacement ({len(dp)} Kerzen ueber 2x Median-Range)")
    L.append("")
    if dp:
        L.append("| Zeit | Richtung | Range | Koerper | x Median |")
        L.append("|---|---|---|---|---|")
        for x in dp[:15]:
            L.append(f"| {x['t'].strftime('%H:%M')} | {x['dir']} | {x['rng']:.2f} "
                     f"| {x['body']:.2f} | {x['x']:.1f}x |")
        if len(dp) > 15:
            L.append("")
            L.append(f"_({len(dp) - 15} weitere)_")
    else:
        L.append("_keine_")
    L.append("")

    # -- FVG
    fg = [g for g in fvgs(bars) if at(day, 0) <= g["t"] < at(day, 17)]
    med_rng = med_bar
    big = [g for g in fg if g["size"] >= med_rng]
    L.append(f"## Fair Value Gaps ({len(fg)} gesamt, {len(big)} groesser als Median-Kerzenrange)")
    L.append("")
    if big:
        L.append("| Zeit | Seite | Bereich | CE | Groesse | Status |")
        L.append("|---|---|---|---|---|---|")
        for g in sorted(big, key=lambda x: -x["size"])[:20]:
            status = ("gefuellt " + g["fill_t"].strftime("%H:%M")) if g["filled"] else \
                     ("CE erreicht" if g["ce_hit"] else "angetippt" if g["touched"] else "**offen**")
            L.append(f"| {g['t'].strftime('%H:%M')} | {g['side']} "
                     f"| {fmt(g['lo'])}–{fmt(g['hi'])} | {fmt(g['ce'])} "
                     f"| {g['size']:.2f} | {status} |")
    else:
        L.append("_keine nennenswerten_")
    L.append("")

    # -- Macros
    L.append("## Macro-Fenster (XX:50–XX+1:10)")
    L.append("")
    mrows = []
    all_rngs = []
    for label, s, e in macro_windows(day):
        seg = slice_between(bars, s, e)
        if not seg:
            continue
        h = hilo(seg)
        r = h["hi"] - h["lo"]
        all_rngs.append(r)
        mrows.append((label, s, r, h))
    if mrows:
        med = statistics.median(all_rngs)
        L.append(f"Median-Range eines Macro-Fensters an diesem Tag: **{fmt(med)} Pkt**. "
                 f"Expansion = Range > 1,5x Median.")
        L.append("")
        L.append("| Fenster | Range | High | Low | Expansion |")
        L.append("|---|---|---|---|---|")
        for label, s, r, h in mrows:
            flag = "**ja**" if r > 1.5 * med else ""
            L.append(f"| {label} | {fmt(r)} | {fmt(h['hi'])} | {fmt(h['lo'])} | {flag} |")
    L.append("")

    # -- Consolidation
    co = [c for c in consolidations(day_bars)]
    L.append(f"## Consolidation-Phasen ({len(co)})")
    L.append("")
    if co:
        L.append(f"Kriterium: Abschnitt bleibt unter {fmt(max(c['hi'] - c['lo'] for c in co))} Pkt "
                 f"Gesamtrange. Die Range-Spalte liegt deshalb immer nah an dieser Schwelle — "
                 f"aussagekraeftig ist die **Dauer**.")
        L.append("")
        L.append("| Von | Bis | Kerzen | Range |")
        L.append("|---|---|---|---|")
        for c in sorted(co, key=lambda x: -x["bars"])[:10]:
            L.append(f"| {c['start'].strftime('%H:%M')} | {c['end'].strftime('%H:%M')} "
                     f"| {c['bars']} | {fmt(c['hi'] - c['lo'])} |")
    else:
        L.append("_keine_")
    L.append("")

    # -- offene Liquiditaet
    ut = untouched_levels(bars)
    ut = [u for u in ut if u["t"] >= at(day, 0)]
    L.append("## Unangetastete Liquiditaet am Ende der Daten")
    L.append("")
    if ut:
        L.append("| Zeit | Seite | Level |")
        L.append("|---|---|---|")
        for u in ut[-12:]:
            L.append(f"| {u['t'].strftime('%H:%M')} | {u['side']} | {fmt(u['level'])} |")
    else:
        L.append("_keine_")
    L.append("")

    open_fvgs = [g for g in fg if not g["filled"] and g["size"] >= med_rng]
    if open_fvgs:
        L.append(f"Dazu {len(open_fvgs)} ungefuellte FVGs — siehe Tabelle oben.")
        L.append("")

    return L


def checklist_report(symbol, day, data, tf, at_time: dtime, before=60, after=60) -> list[str]:
    """Prueft die objektiv pruefbaren Punkte seiner 8er-Checkliste um einen Zeitpunkt."""
    bars = data[tf]
    center = datetime.combine(day, at_time, tzinfo=NY)
    lo_t = center - timedelta(minutes=before)
    hi_t = center + timedelta(minutes=after)
    pre = slice_between(bars, lo_t, center + timedelta(minutes=1))
    post = slice_between(bars, center, hi_t)

    L = []
    L.append(f"# Setup-Check {symbol} {day.isoformat()} um {at_time.strftime('%H:%M')} NY")
    L.append("")
    L.append(f"Fenster: {lo_t.strftime('%H:%M')}–{hi_t.strftime('%H:%M')} auf `{tf}`. "
             f"Geprueft werden die Punkte, die aus Preisdaten belegbar sind — "
             f"*Entry* bleibt deine Entscheidung.")
    L.append("")

    results = []

    # 1 Liq Sweep
    med_bar = statistics.median(b.rng for b in bars) or 1.0
    sw = [s for s in sweeps(bars, CFG["swing"], CFG["min_age"], CFG["min_pen"] * med_bar,
                 CFG["confirm"])
          if lo_t <= s["t"] <= center]
    results.append(("Liq Sweep", bool(sw),
                    "; ".join(f"{s['t'].strftime('%H:%M')} {s['side']} @ {fmt(s['level'])} "
                              f"(+{s['pen']:.2f})" for s in sw[-3:]) or "kein Sweep im Vorfeld"))

    # 2 Displacement
    dp = [x for x in displacements(bars, factor=CFG["disp_factor"]) if lo_t <= x["t"] <= hi_t]
    results.append(("Displacement", bool(dp),
                    "; ".join(f"{x['t'].strftime('%H:%M')} {x['dir']} {x['rng']:.2f} Pkt "
                              f"({x['x']:.1f}x)" for x in dp[:3]) or "keine Kerze ueber 2x Median-Range"))

    # 3 Anhaltende Consolidation
    co = [c for c in consolidations(pre) if c["bars"] >= 10]
    results.append(("Anhaltende Consolidation", bool(co),
                    "; ".join(f"{c['start'].strftime('%H:%M')}–{c['end'].strftime('%H:%M')} "
                              f"({c['bars']} Kerzen, {fmt(c['hi'] - c['lo'])} Pkt)" for c in co[:2])
                    or "keine erkennbare Consolidation davor"))

    # 4 Richtige Zeitfenster
    in_macro = [lbl for lbl, s, e in macro_windows(day) if s <= center < e]
    in_sess = [n for n, s, e in session_windows(day)
               if s <= center < e and n not in ("IPDA True Range", "RTH (9:30-16)")]
    ok_time = bool(in_macro) and "Lunch" not in in_sess
    detail = f"Macro: {in_macro[0] if in_macro else 'ausserhalb'} · Session: {', '.join(in_sess) or '—'}"
    if "Lunch" in in_sess:
        detail += " — **Lunch ist No-Trading-Time**"
    results.append(("Richtige Zeitfenster", ok_time, detail))

    # 5 MS Break
    sb = [x for x in structure_breaks(bars, CFG["swing"], CFG["min_age"]) if lo_t <= x["t"] <= center]
    results.append(("MS Break", bool(sb),
                    "; ".join(f"{x['t'].strftime('%H:%M')} {x['type']} {x['dir']} "
                              f"@ {fmt(x['level'])}" for x in sb[-3:]) or "kein Break im Vorfeld"))

    # 6 Entry — nicht ableitbar
    results.append(("Entry", None, "nur von dir zu setzen"))

    # 7 Macro Expansion
    exp = "—"
    ok_exp = False
    if in_macro:
        lbl, s, e = next(m for m in macro_windows(day) if m[0] == in_macro[0])
        seg = slice_between(bars, s, e)
        allr = [hilo(slice_between(bars, a, b)) for _, a, b in macro_windows(day)]
        allr = [x["hi"] - x["lo"] for x in allr if x]
        if seg and allr:
            h = hilo(seg)
            r = h["hi"] - h["lo"]
            med = statistics.median(allr)
            ok_exp = r > 1.5 * med
            exp = f"Range {fmt(r)} Pkt vs. Tagesmedian {fmt(med)} Pkt ({r / med:.1f}x)"
    results.append(("Macro Expansion", ok_exp, exp))

    # 8 Target Liquiditaet — nur mit dem Wissensstand zum Setup-Zeitpunkt,
    # sonst zaehlt man Levels, die erst im Nachhinein unangetastet blieben.
    m1 = data.get("1m", bars)
    past = [b for b in m1 if b.t <= center]
    ut = untouched_levels(past)
    price = past[-1].c if past else 0.0
    above = [u for u in ut if u["side"] == "buyside" and u["level"] > price]
    below = [u for u in ut if u["side"] == "sellside" and u["level"] < price]
    ok_target = len(above) >= 2 or len(below) >= 2
    results.append(("Target Liquiditaet min. 2 H/L 1m", ok_target,
                    f"offen ueber Preis ({fmt(price)}): {len(above)} Highs · "
                    f"offen darunter: {len(below)} Lows — Stand {at_time.strftime('%H:%M')}"
                    + (f" · naechste: {fmt(above[-1]['level'])} / {fmt(below[-1]['level'])}"
                       if above and below else "")))

    L.append("| # | Punkt | Daten sagen | Beleg |")
    L.append("|---|---|---|---|")
    for i, (name, ok, why) in enumerate(results, 1):
        mark = "—" if ok is None else ("**ja**" if ok else "nein")
        L.append(f"| {i} | {name} | {mark} | {why} |")
    L.append("")
    hit = sum(1 for _, ok, _ in results if ok)
    L.append(f"**{hit}/7 objektiv pruefbare Punkte erfuellt** (Entry ausgenommen). "
             f"Deine Schwelle liegt bei 6/8.")
    L.append("")

    d = hilo(post)
    if d:
        L.append("## Was danach passierte")
        L.append("")
        L.append(f"In den {after} Minuten nach {at_time.strftime('%H:%M')}: "
                 f"High {fmt(d['hi'])} um {d['hi_t'].strftime('%H:%M')}, "
                 f"Low {fmt(d['lo'])} um {d['lo_t'].strftime('%H:%M')}. "
                 f"Von {fmt(post[0].o)} aus: "
                 f"+{d['hi'] - post[0].o:.2f} / {d['lo'] - post[0].o:.2f} Pkt.")
        L.append("")
    return L


# --------------------------------------------------------------------------- CLI

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("symbol", help="z.B. MNQ")
    ap.add_argument("day", help="YYYY-MM-DD (Handelstag)")
    ap.add_argument("--tf", default="1m", choices=list(TF_MINUTES),
                    help="Basis-Timeframe der Analyse (default 1m)")
    ap.add_argument("--at", metavar="HH:MM",
                    help="Setup-Zeitpunkt: prueft die Checkliste statt Tagesreport")
    ap.add_argument("--before", type=int, default=60, help="Minuten Rueckschau bei --at")
    ap.add_argument("--after", type=int, default=60, help="Minuten Vorschau bei --at")
    ap.add_argument("--min-age", type=int, default=None,
                    help="Mindestalter eines Levels in Kerzen, damit ein Durchstich als Sweep "
                         "zaehlt (default: skaliert mit dem Timeframe)")
    ap.add_argument("--min-pen", type=float, default=CFG["min_pen"],
                    help="Mindest-Durchstich als Vielfaches der Median-Kerzenrange")
    ap.add_argument("--confirm", type=int, default=None,
                    help="Kerzen, in denen der Preis nach einem Durchstich zurueckerobern muss")
    ap.add_argument("--swing", type=int, default=CFG["swing"],
                    help="Fraktal-Breite fuer Swing Points (Kerzen je Seite)")
    ap.add_argument("--disp-factor", type=float, default=CFG["disp_factor"],
                    help="Displacement ab dem Wievielfachen der Median-Range")
    ap.add_argument("-o", "--out", help="Ausgabedatei (default: stdout)")
    a = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")

    # Rauschfilter in Kerzen skalieren mit dem Timeframe: 15 Kerzen sind auf 1m
    # eine Viertelstunde, auf 15m fast vier Stunden.
    tf_min = TF_MINUTES[a.tf]
    CFG.update(
        swing=a.swing, min_pen=a.min_pen, disp_factor=a.disp_factor,
        min_age=a.min_age if a.min_age is not None else max(3, round(15 / tf_min)),
        confirm=a.confirm if a.confirm is not None else max(2, round(5 / tf_min)),
    )
    day = datetime.strptime(a.day, "%Y-%m-%d").date()
    # Lose Exporte zuerst einraeumen, damit sie ueberhaupt gefunden werden.
    try:
        from sort_marktdaten import run as sort_run
        sort_run(quiet=True)
    except ImportError:
        pass
    files = find_files(a.symbol, a.day)
    if not files:
        sys.exit(f"Keine Dateien fuer '{a.symbol} {a.day} <tf>.csv' in {DATA_DIR}")
    if a.tf not in files:
        sys.exit(f"Timeframe {a.tf} fehlt. Vorhanden: {', '.join(files)}")

    data = {tf: load(p) for tf, p in files.items()}

    if a.at:
        t = datetime.strptime(a.at, "%H:%M").time()
        lines = checklist_report(a.symbol, day, data, a.tf, t, a.before, a.after)
    else:
        lines = day_report(a.symbol, day, data, a.tf)

    text = "\n".join(lines)
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
        print(f"geschrieben: {a.out}")
    else:
        sys.stdout.reconfigure(encoding="utf-8")
        print(text)


if __name__ == "__main__":
    main()
