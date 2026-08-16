#!/usr/bin/env python3
"""Levels + News fuer die Bias-Vorlage (raw/journal/Daily Bias */Weekly Bias *).

Reuse: load_rows() aus backtest_common.py (Open/High/Low/Close pro Handelstag) -- kein
eigenes CSV-Parsing.

News, zwei Quellen mit klarer Rangfolge:
  1. **ForexFactory-JSON-Feed** (nfs.faireconomy.media) -- die Referenzquelle des Nutzers.
     NICHT per Scraping von forexfactory.com/calendar: die HTML-Seite liefert hinter
     Cloudflare HTTP 403 fuer jeden Bot-Abruf (verifiziert 2026-08-15). Der Feed kennt aber
     nur die *laufende* Woche; ff_calendar_nextweek.json gibt es nicht mehr (HTTP 404).
  2. **TradingView-Wirtschaftskalender** als Fallback, sobald der Zeitraum ausserhalb der
     FF-Woche liegt -- beliebiger Datumsbereich, deshalb die einzige Quelle, die freitags
     abends die *kommende* Woche kennt (der Weekly-Lauf braucht genau das).
`news["source"]` sagt immer, welche der beiden geantwortet hat.

Gegenprobe 2026-08-15 auf KW33: beide Quellen nennen CPI am 12.08. 08:30 NY und PPI am
13.08. 08:30 NY -- **Zeitstempel deckungsgleich**. Unterschied nur in der Einstufung:
TradingView fuehrt zusaetzlich Retail Sales, Existing Home Sales und Michigan Sentiment als
Red, ForexFactory stuft die als Orange ein. Wer beide Seiten nebeneinander legt, sieht also
dieselben Zeiten, aber bei TradingView mehr rote Zeilen.

Zeitzonen: FF liefert ISO-Timestamps mit NY-Offset (-04:00 EDT / -05:00 EST), TradingView
UTC ("...Z"). Beide werden auf NY normalisiert, die DE-Zeit per zoneinfo daraus abgeleitet --
keine manuelle Stundenrechnung (siehe CLAUDE.md, "Zeit vor Preis").

Aufruf:
    python algo/bias_levels.py                      # Levels+News fuer heute
    python algo/bias_levels.py 2026-08-14           # fuer diesen Handelstag
    python algo/bias_levels.py --next               # fuer den naechsten Handelstag (Sa/So -> Mo)
    python algo/bias_levels.py --weekly --next      # kommende Woche (Range = auslaufende Woche)
    python algo/bias_levels.py --demo               # Selbstcheck, kein Datei-/Netzzugriff
"""
from __future__ import annotations

import json
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
from backtest_common import load_rows  # noqa: E402

FF_FEED = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
TV_FEED = "https://economic-calendar.tradingview.com/events"
CACHE = Path(tempfile.gettempdir()) / "ff_calendar_thisweek.json"
CACHE_TTL = 900  # s
BERLIN = ZoneInfo("Europe/Berlin")
NEWYORK = ZoneInfo("America/New_York")
IMPACT_FARBE = {"High": "Red", "Medium": "Orange"}  # Low/Holiday bewusst raus
TV_IMPACT = {1: "Red", 0: "Orange"}                 # -1 (Low) bewusst raus
# Nur USD (Nutzerentscheid 2026-08-16): gehandelt werden NQ/ES, CAD-CPI oder GBP-Jobs
# bewegen die US-Indizes nicht. TradingView filtert das serverseitig (countries=US),
# ForexFactory liefert alle Waehrungen -- dort wird beim Parsen gefiltert.
WAEHRUNG = "USD"
# **Micro und Mini werden streng getrennt** (Nutzervorgabe 2026-08-16). MNQ ist NICHT als
# Ersatz fuer NQ zugelassen, auch nicht als Rueckfall bei duenner Historie: die Kontrakte
# weichen minutenweise um bis zu 7,75 Punkte ab (gemessen ueber 1200 gemeinsame Minuten), und
# beim COT-Report lieferte dieselbe Verwechslung fuer ES ein komplett umgekehrtes Signal.
# Fehlen NQ-Daten, wird das gemeldet -- nicht durch das Micro-Pendant ersetzt.
GAP_SYMBOLE = ["NQ"]
GAP_MIN_TAGE = 6        # weniger Tage -> Datenlage melden, nicht ersetzen
GAP_RUECKBLICK = 35     # Tage: deckt die vergangene Woche + offene NWOG der letzten ~5 Wochen


# --------------------------------------------------------------------------- Levels

def week_range(rows: list[dict], target_day: date) -> dict | None:
    """High/Low aller Handelstage in der ISO-Woche von target_day, bis einschliesslich des
    letzten verfuegbaren Tages <= target_day. None wenn kein Tag der Woche vorliegt."""
    iso_week = target_day.isocalendar()[:2]
    week_rows = [r for r in rows
                 if r["day"] <= target_day and r["day"].isocalendar()[:2] == iso_week]
    if not week_rows:
        return None
    return {"high": max(r["high"] for r in week_rows),
            "low": min(r["low"] for r in week_rows),
            "days": len(week_rows)}


def yesterday_range(rows: list[dict], target_day: date) -> dict | None:
    """H/L/C des letzten Handelstages vor target_day. None wenn keiner vorliegt."""
    prior = [r for r in rows if r["day"] < target_day]
    if not prior:
        return None
    r = prior[-1]
    return {"day": r["day"].isoformat(), "high": r["high"], "low": r["low"], "close": r["close"]}


def next_trading_day(today: date) -> date:
    """Naechster Werktag nach today (Sa/So -> Montag). Feiertage kennt die Funktion nicht."""
    d = today + timedelta(days=1)
    while d.weekday() >= 5:
        d += timedelta(days=1)
    return d


def next_monday(today: date) -> date:
    return today + timedelta(days=7 - today.weekday())


# --------------------------------------------------------------------------- News

def _fetch_feed(url: str = FF_FEED, timeout: int = 20) -> list[dict]:
    """Feed-Abruf mit 15-Minuten-Cache: mehrere Abrufe kurz nacheinander beantwortet
    faireconomy.media mit HTTP 429 (verifiziert 2026-08-15). Ein Cron-Lauf pro Tag trifft das
    nie, ein Testlauf-Doppel sehr wohl.
    ponytail: kein Locking -- zwei parallele Prozesse schreiben sich hoechstens denselben
    Inhalt gegenseitig ueber; relevant erst, wenn das Skript nebenlaeufig laufen soll."""
    if CACHE.exists() and time.time() - CACHE.stat().st_mtime < CACHE_TTL:
        return json.loads(CACHE.read_text("utf-8"))
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (gedanken-vault)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read().decode("utf-8")
    CACHE.write_text(body, "utf-8")
    return json.loads(body)


def _event(t: datetime, titel: str, land: str, impact: str, e: dict) -> dict:
    """Ein Event in Vault-Form. `t` muss zeitzonenbewusst und auf NY-Zeit sein."""
    return {"ny": t.strftime("%Y-%m-%d %H:%M"),
            "de": t.astimezone(BERLIN).strftime("%H:%M"),
            "weekday": t.strftime("%a"),
            "country": land,
            "title": titel,
            "impact": impact,
            "forecast": e.get("forecast") or "",
            "previous": e.get("previous") or ""}


def _gap_bars(symbol: str, von: date, bis: date) -> tuple[list, dict[date, str]]:
    """Bars fuer den Gap-Zeitraum, pro Tag in der besten verfuegbaren Aufloesung.

    1s (IBKR-Parquet) schlaegt 1m: der NDOG-Level ist der *letzte Print* vor 17:00 NY und der
    *erste* ab 18:00 NY -- auf 1m-Kerzen ist das der Close/Open einer 60s-Aggregation, auf 1s
    der tatsaechliche Tick. Fuer Levels, die spaeter als Entry/Ziel dienen, ist das der
    Unterschied zwischen "ungefaehr" und "auf dem Tickraster" (CLAUDE.md: Marktdaten wie Gold).
    Rueckgabe zusaetzlich: je Tag die tatsaechlich benutzte Quelle, damit der Bericht sie
    ausweisen kann statt 1s vorzutaeuschen.
    """
    import marktdaten
    from analyze_ohlc import load

    bars: list = []
    quelle: dict[date, str] = {}
    for day_dir in sorted(marktdaten.DATA_DIR.glob("*/*/*")):
        if not day_dir.is_dir():
            continue
        try:
            tag = datetime.strptime(day_dir.name, "%d.%m.%Y").date()
        except ValueError:
            continue
        if not (von <= tag <= bis):
            continue
        p1s = sorted(day_dir.glob(f"{symbol} * 1s.parquet"))
        if p1s:
            bars.extend(marktdaten._load_1s_parquet(p1s[0]))
            quelle[tag] = "1s"
            continue
        # Liegen mehrere 1m-Fassungen eines Tages vor ("... 1m.csv" und "... 1m (2).csv"),
        # gewinnt die **zeilenreichste**, nicht die alphabetisch erste: die "(2)"-Fassung ist
        # der nachgelieferte, vollstaendigere Export. Am 12.08.2026 fehlten der Bestandsdatei
        # 7 h Session (1011 statt 1380 Kerzen) -- damit verschwand ein ganzer NDOG.
        p1m = [f for f in day_dir.glob(f"{symbol} * 1m*.csv") if "RTH" not in f.name]
        if p1m:
            beste = max(p1m, key=lambda f: sum(1 for _ in f.open(encoding="utf-8-sig")))
            bars.extend(load(beste))
            quelle[tag] = "1m"
    bars.sort(key=lambda b: b.t)
    return bars, quelle


def tick(preis: float, groesse: float = 0.25) -> float:
    """Auf das Kontrakt-Tickraster runden. MNQ/NQ/ES handeln nur in 0,25-Schritten -- ein
    berechnetes Level, das dazwischen liegt, ist als Entry/Stop/Ziel nicht handelbar."""
    return round(round(preis / groesse) * groesse, 2)


def unterteilung(a: float, b: float) -> dict:
    """Hs / Qs / Os einer Range plus C.E. -- Reihenfolge immer von unten nach oben.

    Hs = Halves (50%), Qs = Quarters (25/50/75%), Os = Octants (12,5%-Schritte).
    C.E. (Consequent Encroachment) ist die Mitte und damit identisch mit H1/Q2/O4 --
    bewusst zusaetzlich ausgewiesen, weil im Vault durchgaengig mit diesem Namen gearbeitet
    wird. Alle Werte aufs 0,25-Raster.
    """
    lo, hi = (a, b) if a <= b else (b, a)
    spanne = hi - lo
    def bei(anteil: float) -> float:
        return tick(lo + spanne * anteil)
    return {"low": tick(lo), "high": tick(hi), "spanne": round(spanne, 2),
            "ce": bei(0.5),
            "hs": {"H1": bei(0.5)},
            "qs": {f"Q{i}": bei(i / 4) for i in (1, 2, 3)},
            "os": {f"O{i}": bei(i / 8) for i in (1, 2, 3, 4, 5, 6, 7)}}


def _gaps_aus_bars(bars: list, quelle: dict | None = None) -> tuple[list, list]:
    """(ndog, nwog) aus einer Bar-Folge -- reine Rechnung, kein Dateizugriff, damit testbar.

    Ein Gap ist der Sprung ueber eine **echte Handelspause**, nicht ueber jede Luecke:
      * taeglich  17:00 -> 18:00 NY  (~1 h)          -> NDOG
      * Wochenende Fr 17:00 -> So 18:00 (~49 h)      -> NWOG
    Alles dazwischen (2 h .. 40 h) ist eine Luecke im Datenbestand -- ein fehlender Tag darf
    nicht als 300-Punkte-Gap in der Bias-Datei landen.
    """
    quelle = quelle or {}
    ndog, nwog = [], []
    for vorher, nachher in zip(bars, bars[1:]):
        pause = nachher.t - vorher.t
        if pause < timedelta(minutes=30):       # normale Bar-Folge, keine Session-Pause
            continue
        ist_wochenende = pause > timedelta(hours=24)
        if not ist_wochenende and pause > timedelta(hours=2):
            continue                            # zu lang fuer eine Tagespause -> Datenluecke
        if ist_wochenende and not (timedelta(hours=40) < pause < timedelta(hours=56)):
            continue                            # zu lang/kurz fuer ein Wochenende
        gap = nachher.o - vorher.c
        if gap == 0:                            # luecklos, kein PD Array
            continue
        tag = nachher.t.date()                  # Tag, an dem die neue Session eroeffnet
        # Gefuellt, sobald der Preis den alten Close spaeter wieder erreicht
        fill = next((x.t for x in bars if x.t > nachher.t and x.l <= vorher.c <= x.h), None)
        e = {"tag": tag.isoformat(),
             "weekday": tag.strftime("%a"),
             # close = Close der letzten gehandelten Kerze vor der Pause,
             # open  = Open der ersten Kerze nach der Pause (Nutzervorgabe 2026-08-16)
             "close": tick(vorher.c),
             "close_t": vorher.t.strftime("%Y-%m-%d %H:%M:%S"),
             "open": tick(nachher.o),
             "open_t": nachher.t.strftime("%Y-%m-%d %H:%M:%S"),
             "gap": round(gap, 2),
             "filled": fill is not None,
             "quelle": quelle.get(vorher.t.date(), "?"),
             **{k: v for k, v in unterteilung(vorher.c, nachher.o).items()
                if k in ("ce", "hs", "qs", "os", "spanne")}}
        (nwog if ist_wochenende else ndog).append(e)
    return ndog, nwog


def _register_tage(symbol: str) -> set:
    """Handelstage, fuer die `raw/marktdaten/1s-abdeckung.csv` einen 1s-Abruf protokolliert.

    Das Register ist das Fetch-Protokoll von `fetch_ibkr.py` -- es sagt, was **geholt wurde**,
    nicht was **auf der Platte liegt**. Beides auseinanderzuhalten ist der Sinn dieser
    Funktion: ein registrierter Tag ohne Parquet-Datei ist ein stiller Datenverlust.
    """
    import csv as _csv

    reg = Path(__file__).resolve().parent.parent / "raw" / "marktdaten" / "1s-abdeckung.csv"
    tage: set = set()
    if not reg.exists():
        return tage
    with reg.open(newline="", encoding="utf-8-sig") as fh:
        for r in _csv.DictReader(fh):
            if r.get("symbol") != symbol or not (r.get("von") or "").strip().isdigit():
                continue          # kaputte/fremde Zeile -- ueberspringen statt abbrechen
            t = datetime.fromtimestamp(int(r["von"]), tz=ZoneInfo("UTC")).astimezone(NEWYORK)
            # Ein Abruffenster ab 18:00 gehoert zur Session des naechsten Handelstages
            tage.add(t.date() + timedelta(days=1) if t.hour >= 18 else t.date())
    return tage


def datenlage(symbol: str, von: date, bis: date) -> dict:
    """Welche Aufloesung deckt den Zeitraum tatsaechlich ab -- und deckt sie sich mit 1m?

    Drei Fragen, die vor jeder Level-Rechnung beantwortet sein muessen:
      1. Welche Tage liegen als 1s vor (die gewuenschte Quelle), welche nur als 1m?
      2. Verspricht `1s-abdeckung.csv` Tage, zu denen keine Datei existiert?
      3. Wo beides vorliegt: weichen 1s und der TradingView-1m-Export voneinander ab?
    Frage 3 ist der vom Nutzer gewuenschte Abgleich -- eine Abweichung heisst, dass eine der
    beiden Quellen nicht stimmt, und dann darf kein Level daraus gebaut werden.
    """
    import marktdaten
    from analyze_ohlc import load

    hat_1s, hat_1m, abweichung = set(), set(), []
    for day_dir in sorted(marktdaten.DATA_DIR.glob("*/*/*")):
        if not day_dir.is_dir():
            continue
        try:
            tag = datetime.strptime(day_dir.name, "%d.%m.%Y").date()
        except ValueError:
            continue
        if not (von <= tag <= bis):
            continue
        p1s = sorted(day_dir.glob(f"{symbol} * 1s.parquet"))
        p1m = [f for f in day_dir.glob(f"{symbol} * 1m*.csv") if "RTH" not in f.name]
        if p1s:
            hat_1s.add(tag)
        if p1m:
            hat_1m.add(tag)
        if p1s and p1m:
            # Beide da -> gegenpruefen. 1s auf Minutenschluss verdichten und mit dem
            # 1m-Close vergleichen; verglichen wird nur, wo beide dieselbe Minute kennen.
            s = {b.t.replace(second=0): b.c for b in marktdaten._load_1s_parquet(p1s[0])}
            beste = max(p1m, key=lambda f: sum(1 for _ in f.open(encoding="utf-8-sig")))
            diffs = [abs(b.c - s[b.t]) for b in load(beste) if b.t in s]
            if diffs:
                abweichung.append({"tag": tag.isoformat(), "minuten": len(diffs),
                                   "max": round(max(diffs), 2),
                                   "ungleich": sum(1 for d in diffs if d > 0)})

    registriert = {t for t in _register_tage(symbol) if von <= t <= bis}
    return {"symbol": symbol,
            "tage_1s": sorted(t.isoformat() for t in hat_1s),
            "tage_nur_1m": sorted(t.isoformat() for t in hat_1m - hat_1s),
            "registriert_ohne_datei": sorted(t.isoformat() for t in registriert - hat_1s),
            "abgleich_1s_vs_1m": abweichung}


def gaps_auto(heute: date | None = None) -> dict:
    """`gaps()` fuer das Leitsymbol. **Kein Symbol-Rueckfall** -- Micro ersetzt nie Mini.

    Reicht die Historie nicht, wird `hinweis` gesetzt und die duenne Datenlage gemeldet.
    Frueher fiel diese Funktion auf MNQ zurueck; das ist seit der Micro/Mini-Trennung
    (2026-08-16) untersagt, weil ein Micro-Preis als "NQ-Level" still falsch ist.
    """
    for sym in GAP_SYMBOLE:
        g = gaps(sym, heute)
        tage = len(g.get("quellen", {}))
        if tage < GAP_MIN_TAGE:
            g["hinweis"] = (f"nur {tage} Handelstage {sym}-Historie im Fenster -- Level sind "
                            f"entsprechend duenn belegt. Kein Rueckfall auf das Micro-Pendant "
                            f"(Micro und Mini werden streng getrennt).")
        return g
    return {"symbol": GAP_SYMBOLE[0], "error": "kein Symbol konfiguriert",
            "ndog": [], "nwog": [], "offen": []}


def gaps(symbol: str = "NQ", heute: date | None = None) -> dict:
    """NDOG/NWOG aus `raw/marktdaten/` -- offline, unabhaengig vom Live-Feed.

    Bewusst nicht aus `live_status.py`: das braucht einen offenen Markt und liefert am
    Wochenende `market_data: false`. Genau dann werden die Bias-Dateien aber geschrieben.
    Die Gaps der zurueckliegenden Tage stehen in den Rohdaten und sind am Sonntag genauso
    bestimmbar wie am Mittwoch.

    `offen` = Vortages-Close wurde am Gap-Tag nicht mehr erreicht -> weiter handelbares
    PD Array und DOL-Kandidat.
    """
    heute = heute or date.today()
    von = heute - timedelta(days=GAP_RUECKBLICK)
    bars, quelle = _gap_bars(symbol, von, heute)
    if not bars:
        return {"symbol": symbol, "error": f"keine {symbol}-Daten in {von}..{heute}",
                "ndog": [], "nwog": [], "offen": []}

    # Bewusst NICHT analyze_ohlc.ndog_gap(): der nimmt erste/letzte Kerze des *Kalendertags*.
    # Das passt auf session-geschnittene Tagesdateien, aber nicht auf 1s/1m-Daten, die
    # durchgehend von 00:00:00 bis 23:59:59 laufen -- dort misst er den Sprung ueber
    # Mitternacht (typisch 0.00-0.25 Punkte) statt den echten Gap ueber die Handelspause.
    # Geprueft am 13.08.2026: 17h enthaelt 0 Bars, 16h und 18h je 3600 -- die Pause steht
    # sauber in den Daten. Deshalb datengetrieben: Gap = Sprung ueber jede Handelspause.
    ndog, nwog = _gaps_aus_bars(bars, quelle)

    offen = [e for e in ndog + nwog if not e["filled"]]
    offen.sort(key=lambda e: e["tag"], reverse=True)
    return {"symbol": symbol, "von": von.isoformat(), "bis": heute.isoformat(),
            "ndog": ndog, "nwog": nwog, "offen": offen,
            "quellen": {t.isoformat(): q for t, q in sorted(quelle.items())},
            "datenlage": datenlage(symbol, von, heute)}


def _ff_news(von: date, bis: date) -> dict:
    """ForexFactory-Feed -- die Referenzquelle des Nutzers, aber nur laufende Woche."""
    try:
        raw = _fetch_feed()
    except Exception as exc:  # Netz, Timeout, kaputtes JSON -- alles gleich behandelt
        return {"source": "forexfactory", "events": [], "error": f"{type(exc).__name__}: {exc}"}

    parsed = [(datetime.fromisoformat(e["date"]), e) for e in raw]
    days = {t.date() for t, _ in parsed}
    out = {"source": "forexfactory",
           "feed_span": [min(days).isoformat(), max(days).isoformat()] if days else None,
           "events": sorted((_event(t, e["title"], e["country"], IMPACT_FARBE[e["impact"]], e)
                             for t, e in parsed
                             if e["impact"] in IMPACT_FARBE and von <= t.date() <= bis
                             and e["country"] == WAEHRUNG),
                            key=lambda x: x["ny"])}
    if not days:
        out["error"] = "Feed leer"
    elif not (min(days) <= von and bis <= max(days)):
        # Events der falschen Woche waeren schlimmer als keine -- sie landen sonst ungeprueft
        # in der Bias-Datei. Deshalb leeren und den Aufrufer auf TradingView umleiten.
        out["events"] = []
        out["error"] = (f"Feed deckt nur {min(days)}..{max(days)} ab, {von}..{bis} liegt "
                        f"(teilweise) ausserhalb -- ForexFactory hat nur die laufende Woche")
    return out


def _tv_news(von: date, bis: date) -> dict:
    """TradingView-Wirtschaftskalender -- beliebiger Zeitraum, also auch die *kommende*
    Woche. Deshalb ueberhaupt noetig: der Weekly-Lauf ist freitags abends, da kennt
    ForexFactory die Zielwoche noch nicht."""
    q = urllib.parse.urlencode({"from": f"{von}T00:00:00.000Z",
                                "to": f"{bis + timedelta(days=1)}T00:00:00.000Z",
                                "countries": "US"})
    req = urllib.request.Request(f"{TV_FEED}?{q}",
                                 headers={"Origin": "https://www.tradingview.com",
                                          "User-Agent": "Mozilla/5.0 (gedanken-vault)"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            raw = json.loads(r.read().decode("utf-8"))["result"]
    except Exception as exc:
        return {"source": "tradingview", "events": [], "error": f"{type(exc).__name__}: {exc}"}

    evs = []
    for e in raw:
        farbe = TV_IMPACT.get(e.get("importance"))
        if not farbe:
            continue
        t = datetime.fromisoformat(e["date"].replace("Z", "+00:00")).astimezone(NEWYORK)
        if von <= t.date() <= bis:
            evs.append(_event(t, e["title"], e.get("currency") or e["country"], farbe, e))
    return {"source": "tradingview", "events": sorted(evs, key=lambda x: x["ny"])}


WOCHENTAG_DE = {"Mon": "Mo", "Tue": "Di", "Wed": "Mi", "Thu": "Do", "Fri": "Fr",
                "Sat": "Sa", "Sun": "So"}


def news_block(events: list[dict], von: date | None = None, bis: date | None = None) -> str:
    """Termine als Fliesszeilen, nach Tagen gruppiert -- je Termin **eine** Zeile, danach
    eine Leerzeile (Nutzervorgabe 2026-08-16).

    Kein Spaltenlayout mehr: Emoji sind nicht monospace-breit, in einer ausgerichteten Tabelle
    verrutscht damit jede Zeile mit Farbsymbol. Als Fliesstext ist das egal, und Leerzeilen
    rendern in Obsidian als Absatz -- genau die gewuenschte Luft zwischen den Terminen.

    Impact als Farbsymbol (🔴 Red / 🟠 Orange), Uhrzeiten immer mit "NY" und "DE" beschriftet,
    damit keine Verwechslung moeglich ist. Leere Handelstage werden mitgefuehrt -- dass Montag
    *keine* Termine hat, ist eine Aussage fuer die Wochenplanung, kein Nichts.
    """
    zeilen: list[str] = []

    je_tag: dict = {}
    for e in events:
        je_tag.setdefault(e["ny"][:10], []).append(e)

    tage = sorted(je_tag)
    if von and bis:                       # alle Handelstage des Zeitraums, auch die leeren
        d, alle = von, []
        while d <= bis:
            if d.weekday() < 5:
                alle.append(d.isoformat())
            d += timedelta(days=1)
        tage = sorted(set(alle) | set(je_tag))

    for tag in tage:
        t = date.fromisoformat(tag)
        label = f"{WOCHENTAG_DE.get(t.strftime('%a'), t.strftime('%a'))} {t:%d.%m.}"
        drin = sorted(je_tag.get(tag, []), key=lambda e: e["ny"])
        if not drin:
            # Rotes Kreuz: ein leerer Handelstag soll auf einen Blick als leer erkennbar sein,
            # nicht als uebersehene Zeile.
            zeilen += [f"**{label}** ❌ keine USD-Termine", ""]
            continue
        zeilen += [f"**{label}**", ""]
        for e in drin:
            symbol = "🔴" if e["impact"] == "Red" else "🟠"
            werte = []
            if e["forecast"]:
                werte.append(f"Forecast {e['forecast']}")
            if e["previous"]:
                werte.append(f"Previous {e['previous']}")
            schwanz = f"  ({', '.join(werte)})" if werte else ""
            zeilen += [f"{symbol} **{e['ny'][11:]} NY** / {e['de']} DE — "
                       f"{e['title']}{schwanz}", ""]
    return "\n".join(zeilen).strip()


def news(target_day: date, weekly: bool = False) -> dict:
    """Red-/Orange-Folder-Events fuer target_day (bzw. Mo-Fr ab target_day bei weekly=True).

    ForexFactory zuerst (Referenzquelle des Nutzers), TradingView als Fallback sobald der
    Zeitraum ausserhalb der FF-Woche liegt. Bricht nie hart ab: jeder Fehlschlag landet als
    Text in "error", "events" bleibt eine Liste -- der Command setzt dann seinen Platzhalter.
    "source" sagt immer, woher die Zahlen stammen."""
    bis = target_day + timedelta(days=4) if weekly else target_day
    ff = _ff_news(target_day, bis)
    if not ff.get("error"):
        ff["block"] = news_block(ff["events"], target_day, bis)
        return ff
    tv = _tv_news(target_day, bis)
    tv["hinweis"] = f"ForexFactory nicht nutzbar ({ff['error']}) -- TradingView-Kalender verwendet"
    tv["block"] = news_block(tv.get("events", []), target_day, bis)
    return tv


# --------------------------------------------------------------------------- Zusammenbau

def compute(target_day: date, weekly: bool) -> dict:
    # NQ, nicht MNQ: gehandelt wird der Mini, und NQ hat mit 6540 Tagesdateien ohnehin die
    # laengere 1d-Historie. Micro/Mini werden strikt getrennt (Nutzervorgabe 2026-08-16).
    rows = load_rows("NQ")
    if weekly:
        mon = next_monday(target_day)
        iso = mon.isocalendar()
        # COT nur im Weekly: der CFTC-Report erscheint woechentlich (Stand Dienstag,
        # Veroeffentlichung Freitag) -- fuer eine Tagesvorlage gibt es nichts Neues.
        from cot import cot as _cot
        return {"target_week": {"monday": mon.isoformat(), "kw": iso[1], "year": iso[0]},
                "letzte_woche": week_range(rows, target_day),
                "gaps": gaps_auto(heute=target_day),
                "cot": _cot(["NQ", "ES"], stichtag=target_day),
                "news": news(mon, weekly=True)}
    return {"day": target_day.isoformat(),
            "weekday": target_day.strftime("%A"),
            "weekly_range": week_range(rows, target_day),
            "yesterday_range": yesterday_range(rows, target_day),
            "gaps": gaps_auto(heute=target_day),
            "news": news(target_day)}


def demo() -> None:
    rows = [
        {"day": date(2026, 8, 10), "open": 100.0, "close": 105.0, "high": 106.0, "low": 99.0},
        {"day": date(2026, 8, 11), "open": 105.0, "close": 103.0, "high": 107.0, "low": 102.0},
        {"day": date(2026, 8, 12), "open": 103.0, "close": 110.0, "high": 111.0, "low": 103.0},
    ]
    assert week_range(rows, date(2026, 8, 12)) == {"high": 111.0, "low": 99.0, "days": 3}
    assert yesterday_range(rows, date(2026, 8, 12)) == {
        "day": "2026-08-11", "high": 107.0, "low": 102.0, "close": 103.0}
    assert week_range(rows, date(2026, 8, 3)) is None, "andere ISO-Woche -> None"
    assert yesterday_range(rows, date(2026, 8, 10)) is None, "kein Vortag -> None"

    assert next_trading_day(date(2026, 8, 14)) == date(2026, 8, 17), "Fr -> Mo"
    assert next_trading_day(date(2026, 8, 17)) == date(2026, 8, 18), "Mo -> Di"
    assert next_monday(date(2026, 8, 14)) == date(2026, 8, 17)
    assert next_monday(date(2026, 8, 16)) == date(2026, 8, 17), "So -> Montag darauf"

    # Register-Fenster ab 18:00 NY gehoert zur Session des naechsten Handelstages -- sonst
    # meldet die Datenlage-Pruefung reihenweise "registriert, aber keine Datei" fuer Tage,
    # deren Parquet unter dem Folgetag liegt.
    def _reg_tag(t: datetime) -> date:
        return t.date() + timedelta(days=1) if t.hour >= 18 else t.date()

    assert _reg_tag(datetime(2026, 8, 12, 18, 30, tzinfo=NEWYORK)) == date(2026, 8, 13)
    assert _reg_tag(datetime(2026, 8, 13, 9, 30, tzinfo=NEWYORK)) == date(2026, 8, 13)
    assert _reg_tag(datetime(2026, 8, 13, 16, 59, tzinfo=NEWYORK)) == date(2026, 8, 13)
    # Das echte Register muss lesbar sein und darf an kaputten Zeilen nicht abbrechen
    # (am 2026-08-16 hat ein paralleler fetch_ibkr-Lauf eine Zeile zerrissen).
    assert isinstance(_register_tage("NQ"), set), "Register lesbar, kaputte Zeilen toleriert"

    # Tickraster + Hs/Qs/Os. Futures handeln nur in 0,25-Schritten (CLAUDE.md/Nutzervorgabe).
    assert tick(28443.375) == 28443.5 and tick(28443.1) == 28443.0, tick(28443.375)
    u = unterteilung(28284.0, 28602.75)          # NWOG 02.08.2026, Spanne 318.75
    assert (u["low"], u["high"], u["spanne"]) == (28284.0, 28602.75, 318.75), u
    assert u["ce"] == u["hs"]["H1"] == u["qs"]["Q2"] == u["os"]["O4"], "C.E. == H1 == Q2 == O4"
    assert u["ce"] == 28443.5, u["ce"]            # 28284 + 159.375 -> aufs Raster
    # 28284 + 318.75*0.25 = 28363.6875 -> 28363.75; *0.75 = 28523.0625 -> 28523.0
    assert u["qs"]["Q1"] == 28363.75 and u["qs"]["Q3"] == 28523.0, u["qs"]
    assert list(u["os"]) == [f"O{i}" for i in range(1, 8)], u["os"]
    assert all(u["os"][f"O{i}"] <= u["os"][f"O{i+1}"] for i in range(1, 7)), "Os aufsteigend"
    # Richtung egal: ein bearisher Gap (open < close) liefert dieselbe Unterteilung
    assert unterteilung(28602.75, 28284.0) == u, "Reihenfolge der Argumente darf nichts aendern"
    assert all(abs(v * 4 - round(v * 4)) < 1e-9 for v in u["qs"].values()), "Qs auf 0,25-Raster"

    # Gap-Erkennung ueber Handelspausen. Synthetische Bars, kein Dateizugriff.
    # Regressionsschutz gegen den Fehler vom 16.08.2026: analyze_ohlc.ndog_gap() nahm
    # erste/letzte Kerze des Kalendertags und mass damit auf 1s-Daten den Sprung ueber
    # Mitternacht (-0.25) statt den echten Session-Gap ueber die 17:00-18:00-Pause (+19.25).
    class _B:
        def __init__(s, t, o, h, l, c): s.t, s.o, s.h, s.l, s.c = t, o, h, l, c

    ny = NEWYORK
    def _bar(tag, hh, mm, preis, hoch=None, tief=None):
        return _B(datetime(2026, 8, tag, hh, mm, tzinfo=ny), preis,
                  hoch if hoch is not None else preis, tief if tief is not None else preis, preis)

    # Mi: 16:59 -> 18:00 = NDOG +20, ungefuellt (Preis kehrt nie auf 100 zurueck).
    # Durchgehende Bars ueber Mitternacht -- dort darf KEIN Gap entstehen (der eigentliche Bug).
    reihe = [_bar(12, 16, 58, 100.0), _bar(12, 16, 59, 100.0),
             _bar(12, 18, 0, 120.0), _bar(12, 23, 59, 121.0), _bar(13, 0, 0, 121.0)]
    nd, nw = _gaps_aus_bars(reihe)
    assert [(e["tag"], e["gap"], e["filled"]) for e in nd] == [("2026-08-12", 20.0, False)], nd
    assert nw == [], nw

    # Fill-Erkennung: Do 16:59 (130) -> 18:00 (125), spaeter Ruecklauf auf 130 -> gefuellt
    reihe2 = [_bar(13, 16, 59, 130.0), _bar(13, 18, 0, 125.0),
              _bar(13, 18, 1, 129.0, hoch=131.0, tief=124.0)]
    nd2, _ = _gaps_aus_bars(reihe2)
    assert [(e["gap"], e["filled"], e["ce"]) for e in nd2] == [(-5.0, True, 127.5)], nd2

    # Wochenende Fr 17:00 -> So 18:00 (49 h) ist ein NWOG, kein NDOG
    wochenende = [_B(datetime(2026, 8, 14, 16, 59, tzinfo=ny), 200.0, 200.0, 200.0, 200.0),
                  _B(datetime(2026, 8, 16, 18, 0, tzinfo=ny), 210.0, 210.0, 210.0, 210.0)]
    nd3, nw3 = _gaps_aus_bars(wochenende)
    assert nd3 == [] and [(e["tag"], e["gap"]) for e in nw3] == [("2026-08-16", 10.0)], (nd3, nw3)

    # Fehlender Tag im Bestand (23 h Luecke) darf NIE als Gap zaehlen -- sonst stuende eine
    # erfundene Grossbewegung als PD Array in der Bias-Datei.
    luecke = [_bar(12, 18, 1, 121.0), _bar(13, 16, 59, 130.0)]
    assert _gaps_aus_bars(luecke) == ([], []), _gaps_aus_bars(luecke)

    # Zeit vor Preis: NY-Zeit unveraendert, DE-Zeit korrekt +6h im Sommer / +6h im Winter
    ev = _event(datetime.fromisoformat("2026-08-12T08:30:00-04:00"), "CPI m/m", "USD", "Red", {})
    assert (ev["ny"], ev["de"]) == ("2026-08-12 08:30", "14:30"), ev
    ev_w = _event(datetime.fromisoformat("2026-01-14T08:30:00-05:00"), "CPI", "USD", "Orange", {})
    assert (ev_w["ny"], ev_w["de"]) == ("2026-01-14 08:30", "14:30"), ev_w
    # TradingViews UTC-Timestamps muessen auf dieselbe NY-Zeit fallen wie ForexFactorys
    utc = datetime.fromisoformat("2026-08-12T12:30:00+00:00").astimezone(NEWYORK)
    assert _event(utc, "CPI", "USD", "Red", {})["ny"] == ev["ny"], "UTC->NY == FF-NY"

    # Fehlschlagender Abruf darf nie durchschlagen (CLAUDE.md-Constraint). Beide Quellen tot
    # -> leere Liste + Fehler, kein Absturz.
    orig_ff, orig_tv = _fetch_feed, _tv_news
    globals()["_fetch_feed"] = _boom
    globals()["_tv_news"] = lambda *a, **k: {"source": "tradingview", "events": [],
                                             "error": "URLError: kein Netz"}
    try:
        r = news(date(2026, 8, 12))
        assert r["events"] == [] and "URLError" in r["error"], r
        assert "ForexFactory nicht nutzbar" in r["hinweis"], r

        # Zeitraum ausserhalb der FF-Woche -> NICHT die falsche Woche, sondern TradingView
        feed = [{"date": "2026-08-12T08:30:00-04:00", "country": "USD", "title": "CPI m/m",
                 "impact": "High", "forecast": "", "previous": ""}]
        globals()["_fetch_feed"] = lambda *a, **k: feed
        assert news(date(2026, 8, 12))["source"] == "forexfactory", "Tag in der FF-Woche"

        # Nur USD: FF liefert alle Waehrungen, CAD/GBP/EUR duerfen nicht durchrutschen.
        # Ohne diesen Filter standen am 17.08. drei CAD-CPI-Termine in der NQ-Bias-Datei.
        gemischt = feed + [
            {"date": "2026-08-12T08:30:00-04:00", "country": "CAD", "title": "CPI m/m",
             "impact": "High", "forecast": "", "previous": ""},
            {"date": "2026-08-12T02:00:00-04:00", "country": "GBP", "title": "Claimant Count",
             "impact": "High", "forecast": "", "previous": ""},
        ]
        globals()["_fetch_feed"] = lambda *a, **k: gemischt
        nur_usd = news(date(2026, 8, 12))
        assert [e["country"] for e in nur_usd["events"]] == ["USD"], nur_usd
        # Leeres Ergebnis ohne Fehler ist ein newsarmer Tag, KEIN Abruf-Fehler --
        # die Commands unterscheiden das, sonst steht faelschlich eine Warnung in der Datei.
        globals()["_fetch_feed"] = lambda *a, **k: [gemischt[1]]  # nur CAD im Feed
        leer = news(date(2026, 8, 12))
        assert leer["events"] == [] and leer.get("error") is None, leer
        globals()["_tv_news"] = lambda von, bis: {"source": "tradingview", "events": [
            _event(datetime.fromisoformat("2026-08-19T14:00:00-04:00"), "FOMC Minutes",
                   "USD", "Red", {})]}
        weit = news(date(2026, 8, 17), weekly=True)
        assert weit["source"] == "tradingview" and len(weit["events"]) == 1, weit
        assert "ausserhalb" in weit["hinweis"], weit
    finally:
        globals()["_fetch_feed"], globals()["_tv_news"] = orig_ff, orig_tv
    print("demo ok")


def _boom(*a, **k):
    raise urllib.error.URLError("kein Netz")


def main(argv: list[str] | None = None) -> int:
    # Der News-Block enthaelt ein Emoji. Ohne das hier bricht die Ausgabe auf einer
    # cp1252-Konsole mit UnicodeEncodeError ab -- und damit der headless-Lauf, der ueber
    # tools/bias-cron.cmd in algo/live/bias-cron.log schreibt.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    import argparse
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("day", nargs="?", help="YYYY-MM-DD, Default: heute")
    ap.add_argument("--next", action="store_true", dest="nxt",
                    help="naechster Handelstag statt heute (Daily-Modus)")
    ap.add_argument("--weekly", action="store_true",
                    help="kommende Woche: Zielwoche + Range der auslaufenden Woche")
    ap.add_argument("--demo", action="store_true", help="Selbstcheck, kein Datei-/Netzzugriff")
    a = ap.parse_args(argv)

    if a.demo:
        demo()
        return 0

    target = date.fromisoformat(a.day) if a.day else date.today()
    if a.nxt and not a.weekly:
        target = next_trading_day(target)
    print(json.dumps(compute(target, a.weekly), default=str, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
