#!/usr/bin/env python3
"""Levels + News fuer die Bias-Vorlage (raw/journal/Daily Bias */Weekly Bias *).

Reuse: load_rows() aus backtest_common.py (Open/High/Low/Close pro Handelstag) -- kein
eigenes CSV-Parsing. News kommen aus dem offiziellen ForexFactory-JSON-Feed
(nfs.faireconomy.media), NICHT per Scraping von forexfactory.com/calendar -- die HTML-Seite
liefert hinter Cloudflare HTTP 403 fuer jeden Bot-Abruf (verifiziert 2026-08-15).

Zeitzonen: Der Feed liefert ISO-Timestamps mit NY-Offset (-04:00 EDT / -05:00 EST). Die
NY-Zeit wird daher unveraendert uebernommen, DE-Zeit per zoneinfo daraus abgeleitet --
keine manuelle Stundenrechnung (siehe CLAUDE.md, "Zeit vor Preis").

Bekannte Grenze: Es gibt nur den Feed der *laufenden* Woche (ff_calendar_thisweek.json);
`ff_calendar_nextweek.json` existiert nicht mehr (HTTP 404, geprueft 2026-08-15). Liegt der
Zieltag ausserhalb der Feed-Woche, steht das explizit in news["error"] -- deshalb laeuft der
Weekly-Cron sonntags, nicht freitags.

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
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
from backtest_common import load_rows  # noqa: E402

FF_FEED = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
CACHE = Path(tempfile.gettempdir()) / "ff_calendar_thisweek.json"
CACHE_TTL = 900  # s
BERLIN = ZoneInfo("Europe/Berlin")
IMPACT_FARBE = {"High": "Red", "Medium": "Orange"}  # Low/Holiday bewusst raus


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


def _event(t: datetime, e: dict) -> dict:
    return {"ny": t.strftime("%Y-%m-%d %H:%M"),
            "de": t.astimezone(BERLIN).strftime("%H:%M"),
            "weekday": t.strftime("%a"),
            "country": e["country"],
            "title": e["title"],
            "impact": IMPACT_FARBE[e["impact"]],
            "forecast": e.get("forecast", ""),
            "previous": e.get("previous", "")}


def news(target_day: date, weekly: bool = False) -> dict:
    """Red-/Orange-Folder-Events. weekly=True -> ganze Feed-Woche statt nur target_day.

    Bricht nie hart ab: jeder Fehlschlag landet als Text in "error", "events" bleibt eine
    Liste. Der aufrufende Command setzt dann seinen Warn-Platzhalter."""
    try:
        raw = _fetch_feed()
    except Exception as exc:  # Netz, Timeout, kaputtes JSON -- alles gleich behandelt
        return {"events": [], "error": f"{type(exc).__name__}: {exc}"}

    parsed = [(datetime.fromisoformat(e["date"]), e) for e in raw]
    days = {t.date() for t, _ in parsed}
    out = {"events": sorted((_event(t, e) for t, e in parsed
                             if e["impact"] in IMPACT_FARBE
                             and (weekly or t.date() == target_day)),
                            key=lambda x: x["ny"]),
           "feed_span": [min(days).isoformat(), max(days).isoformat()] if days else None}
    if days and not (min(days) <= target_day <= max(days)):
        # Events der falschen Woche liefern waere schlimmer als keine -- sie landen sonst
        # ungeprueft in der Bias-Datei. Deshalb hier leeren, nicht nur warnen.
        out["events"] = []
        out["error"] = (f"Feed deckt nur {min(days)}..{max(days)} ab, {target_day} liegt "
                        f"ausserhalb -- ForexFactory veroeffentlicht nur die laufende Woche")
    return out


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

    # Zeit vor Preis: NY-Zeit aus dem Feed unveraendert, DE-Zeit korrekt +6h im Sommer
    ev = _event(datetime.fromisoformat("2026-08-12T08:30:00-04:00"),
                {"country": "USD", "title": "CPI m/m", "impact": "High"})
    assert (ev["ny"], ev["de"], ev["impact"]) == ("2026-08-12 08:30", "14:30", "Red"), ev
    ev_w = _event(datetime.fromisoformat("2026-01-14T08:30:00-05:00"),
                  {"country": "USD", "title": "CPI m/m", "impact": "Medium"})
    assert (ev_w["ny"], ev_w["de"], ev_w["impact"]) == ("2026-01-14 08:30", "14:30", "Orange"), ev_w

    # Fehlschlagender Abruf darf nie durchschlagen (CLAUDE.md-Constraint)
    orig, globals()["_fetch_feed"] = _fetch_feed, _boom
    try:
        r = news(date(2026, 8, 12))
    finally:
        globals()["_fetch_feed"] = orig
    assert r["events"] == [] and "URLError" in r["error"], r

    # Zieltag ausserhalb der Feed-Woche -> leere Liste + Fehler, NICHT die falsche Woche
    feed = [{"date": "2026-08-12T08:30:00-04:00", "country": "USD", "title": "CPI m/m",
             "impact": "High", "forecast": "", "previous": ""}]
    orig, globals()["_fetch_feed"] = _fetch_feed, lambda *a, **k: feed
    try:
        assert news(date(2026, 8, 12))["events"], "Tag in der Feed-Woche -> Events"
        weit = news(date(2026, 8, 19), weekly=True)
    finally:
        globals()["_fetch_feed"] = orig
    assert weit["events"] == [] and "ausserhalb" in weit["error"], weit
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
