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


def news(target_day: date, weekly: bool = False) -> dict:
    """Red-/Orange-Folder-Events fuer target_day (bzw. Mo-Fr ab target_day bei weekly=True).

    ForexFactory zuerst (Referenzquelle des Nutzers), TradingView als Fallback sobald der
    Zeitraum ausserhalb der FF-Woche liegt. Bricht nie hart ab: jeder Fehlschlag landet als
    Text in "error", "events" bleibt eine Liste -- der Command setzt dann seinen Platzhalter.
    "source" sagt immer, woher die Zahlen stammen."""
    bis = target_day + timedelta(days=4) if weekly else target_day
    ff = _ff_news(target_day, bis)
    if not ff.get("error"):
        return ff
    tv = _tv_news(target_day, bis)
    tv["hinweis"] = f"ForexFactory nicht nutzbar ({ff['error']}) -- TradingView-Kalender verwendet"
    return tv


# --------------------------------------------------------------------------- Zusammenbau

def compute(target_day: date, weekly: bool) -> dict:
    rows = load_rows("MNQ")
    if weekly:
        mon = next_monday(target_day)
        iso = mon.isocalendar()
        return {"target_week": {"monday": mon.isoformat(), "kw": iso[1], "year": iso[0]},
                "letzte_woche": week_range(rows, target_day),
                "news": news(mon, weekly=True)}
    return {"day": target_day.isoformat(),
            "weekday": target_day.strftime("%A"),
            "weekly_range": week_range(rows, target_day),
            "yesterday_range": yesterday_range(rows, target_day),
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
