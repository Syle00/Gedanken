#!/usr/bin/env python3
"""Dashboard-Zentrale -- lokaler Server fuer tools/dashboard.html.

Design: docs/superpowers/specs/2026-08-25-dashboard-zentrale-design.md

Aufruf:
    python tools/dashboard_serve.py      # http://localhost:8787

Bindet ausschliesslich an 127.0.0.1. Keine Auth, kein Zugriff von aussen.
"""
from __future__ import annotations

import csv
import json
import os
import re
import subprocess
import sys
import threading
import time
from datetime import date, datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from zoneinfo import ZoneInfo

VAULT = Path(__file__).resolve().parent.parent
NY = ZoneInfo("America/New_York")
PORT = 8787
ABDECKUNG = VAULT / "raw" / "marktdaten" / "1s-abdeckung.csv"


def sicher(fn) -> dict:
    """Ruft ein Panel auf und verpackt es. Ein Fehler darf nie andere Panels mitreissen."""
    try:
        data, age_s = fn()
        return {"data": data, "error": None, "age_s": age_s}
    except Exception as exc:
        return {"data": None, "error": f"{type(exc).__name__}: {exc}", "age_s": None}


def _letzter_werktag(heute: date) -> date:
    """Letzter Mo-Fr strikt vor `heute`. Der laufende Tag zaehlt nicht: seine 1s-Daten
    sind noch unvollstaendig, ein Rueckstand waere dort kein echter Rueckstand."""
    d = heute - timedelta(days=1)
    while d.weekday() >= 5:
        d -= timedelta(days=1)
    return d


def _werktage(a: date, b: date) -> int:
    """Werktage (Mo-Fr) strikt nach `a` bis einschliesslich `b`; 0 wenn b <= a."""
    n, d = 0, a
    while d < b:
        d += timedelta(days=1)
        if d.weekday() < 5:
            n += 1
    return n


def datenabdeckung() -> tuple[dict, float]:
    """Bis wann reichen die 1s-Daten je Symbol, und wie viele Werktage fehlen."""
    letzte: dict[str, int] = {}
    with ABDECKUNG.open(encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            ts = int(r["bis"])
            if ts > letzte.get(r["symbol"], 0):
                letzte[r["symbol"]] = ts
    heute = datetime.now(NY).date()
    soll = _letzter_werktag(heute)
    out = {"soll": soll.isoformat(), "symbole": {}, "luecke_tage": 0}
    for sym, ts in sorted(letzte.items()):
        # ponytail: Handelstag = Kalendertag des letzten Bars in NY-Zeit. Genau genug fuer
        # eine Rueckstandsanzeige; die exakte Session-Zuordnung macht algo/, nicht dieses Panel.
        bis = datetime.fromtimestamp(ts, NY).date()
        fehlt = _werktage(bis, soll)
        out["symbole"][sym] = {"bis": bis.isoformat(), "fehlt_tage": fehlt}
        out["luecke_tage"] = max(out["luecke_tage"], fehlt)
    return out, time.time() - max(letzte.values(), default=time.time())


def jetzt() -> dict:
    t = datetime.now(NY)
    tage = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
    return {"iso": t.isoformat(timespec="seconds"),
            "ny": t.strftime("%H:%M"),
            "datum": t.strftime("%d.%m.%Y"),
            "weekday": tage[t.weekday()]}


BRIEFINGS = VAULT / "briefings"


def _ist_briefing(p: Path) -> bool:
    """Nur datierte Dateien sind Briefings. In briefings/ liegt laut CLAUDE.md auch
    status.md (Lernpfad-Statusseite) -- die darf hier nie als Briefing durchgehen."""
    n = p.name
    return (len(n) > 11 and n[:4].isdigit() and n[4] == "-"
            and n[7] == "-" and n[10] == "-")


def _parse_briefing(text: str) -> dict:
    """Fliesstext + Termine aus einer Cowork-Briefing-Datei.

    Bewusst tolerant: fehlt `## Termine`, bleibt die Liste leer und der Text kommt trotzdem
    durch. Ein strenger Parser wuerde hier nur dafuer sorgen, dass ein Formatwechsel in
    Cowork das ganze Panel abschaltet."""
    if text.startswith("---"):
        teile = text.split("---", 2)
        if len(teile) == 3:
            text = teile[2]
    termine, im_abschnitt = [], False
    for zeile in text.splitlines():
        if zeile.startswith("## "):
            im_abschnitt = zeile[3:].strip().lower() == "termine"
            continue
        if im_abschnitt and zeile.strip().startswith("- "):
            rest = zeile.strip()[2:]
            for trenner in ("—", "–", " - "):
                if trenner in rest:
                    zeit, titel = rest.split(trenner, 1)
                    termine.append({"zeit": zeit.strip(), "titel": titel.strip()})
                    break
    return {"text": text.strip(), "termine": termine}


def briefing() -> tuple[dict, float]:
    """Neuestes Briefing des heutigen Tages, sonst das letzte vorhandene."""
    heute = datetime.now(NY).date().isoformat()
    dateien = sorted(p for p in BRIEFINGS.glob("*.md")
                     if _ist_briefing(p)) if BRIEFINGS.is_dir() else []
    von_heute = [p for p in dateien if p.name.startswith(heute)]
    quelle = max(von_heute or dateien, key=lambda p: p.stat().st_mtime, default=None)
    if quelle is None:
        return {"fehlt": True, "datei": None, "termine": [],
                "hinweis": "Kein Briefing vorhanden — läuft Cowork und schreibt es "
                           "nach briefings/?"}, 0.0
    d = _parse_briefing(quelle.read_text(encoding="utf-8", errors="replace"))
    d["fehlt"] = not von_heute
    d["datei"] = quelle.name
    if d["fehlt"]:
        d["hinweis"] = (f"Kein Briefing für {heute} — letztes: {quelle.name}")
    return d, time.time() - quelle.stat().st_mtime


ERLAUBT = ("planung", "raw/journal", "wiki/lernpfad")

BIAS_ORDNER = VAULT / "raw" / "journal"
CACHE_S = 900
_markt_cache: dict = {"t": 0.0, "data": None, "wall": 0.0, "error": None}
_markt_lock = threading.Lock()
_markt_laden_laeuft = False


def _neueste_bias() -> dict | None:
    """Bias-Richtung aus der juengsten Daily-Bias-Datei (flach in raw/journal/,
    tools/sortiere_bias.py raeumt sie spaeter nach raw/journal/bias/daily/)."""
    dateien = sorted(BIAS_ORDNER.glob("Daily Bias *.md"))
    if not dateien:
        return None
    p = dateien[-1]
    kopf = p.read_text(encoding="utf-8", errors="replace")[:800]
    m = re.search(r"^Bias:\s*\n\s*-\s*(.+)$", kopf, re.MULTILINE)
    return {"datei": p.name,
            "bias": (m.group(1).strip() if m else "unbekannt"),
            "datum": p.stem.replace("Daily Bias ", "")}


def _markt_laden() -> None:
    """Synchroner Subprozess-Aufruf fuer bias_levels.py. Fuellt den Cache oder vermerkt
    den Fehler. Wird im Hintergrund-Thread aufgerufen."""
    global _markt_laden_laeuft
    try:
        p = subprocess.run([sys.executable, str(VAULT / "algo" / "bias_levels.py")],
                           capture_output=True, text=True, timeout=120,
                           encoding="utf-8", errors="replace", cwd=str(VAULT))
        if p.returncode != 0:
            raise RuntimeError((p.stderr or "").strip()[-300:] or f"exit {p.returncode}")
        _markt_cache.update(t=time.monotonic(), data=json.loads(p.stdout),
                            wall=time.time(), error=None)
    except Exception as exc:
        letzte = (datetime.fromtimestamp(_markt_cache["wall"], NY).strftime("%d.%m. %H:%M")
                  if _markt_cache["wall"] else "nie")
        _markt_cache.update(t=time.monotonic(), error=exc, wall=time.time())
    finally:
        _markt_laden_laeuft = False


def markt() -> tuple[dict, float]:
    """Levels + News aus algo/bias_levels.py, gecacht im Hintergrund.

    Cache-Status:
    - Frisch (jünger als CACHE_S): liefert Daten
    - Alt oder leer & nicht geladen: startet Hintergrund-Thread, wirft „werden geladen"
    - Alt oder leer & Laden läuft: wirft „werden geladen"
    - Fehler im Cache: wirft mit Kontext „letzter erfolgreicher Abruf"
    """
    global _markt_laden_laeuft

    # Ist der Cache frisch?
    if _markt_cache["data"] is not None and time.monotonic() - _markt_cache["t"] <= CACHE_S:
        d = dict(_markt_cache["data"])
        d["bias_datei"] = _neueste_bias()
        return d, time.time() - _markt_cache["wall"]

    # Cache alt oder leer -- prüfe, ob wir laden können
    with _markt_lock:
        # Doppelprüfung: vielleicht hat zwischen check und lock ein anderer Thread geladen
        if _markt_cache["data"] is not None and time.monotonic() - _markt_cache["t"] <= CACHE_S:
            d = dict(_markt_cache["data"])
            d["bias_datei"] = _neueste_bias()
            return d, time.time() - _markt_cache["wall"]

        if _markt_cache["error"] is not None:
            # Letzter Versuch hat Fehler geworfen -- wirf ihn jetzt
            exc = _markt_cache["error"]
            letzte = (datetime.fromtimestamp(_markt_cache["wall"], NY).strftime("%d.%m. %H:%M")
                      if _markt_cache["wall"] else "nie")
            raise RuntimeError(f"{type(exc).__name__}: {exc} "
                               f"(letzter erfolgreicher Abruf: {letzte})") from None

        # Kein Fehler im Cache, aber auch keine Daten -- muss geladen werden
        if not _markt_laden_laeuft:
            _markt_laden_laeuft = True
            thread = threading.Thread(target=_markt_laden, daemon=True)
            thread.start()

    # Lade läuft jetzt (oder lief), aber Cache ist leer -> wirft "werden geladen"
    raise RuntimeError("Levels werden geladen — der erste Abruf dauert etwa eine Minute")


def ziel_pfad(rel: str) -> Path:
    """Relativen Pfad gegen die Whitelist pruefen -- **nach** resolve(), sonst rutschen
    `..` und absolute Pfade durch. raw/marktdaten/ ist damit strukturell ausgeschlossen."""
    p = (VAULT / rel).resolve()
    if p.suffix != ".md":
        raise ValueError(f"nur .md erlaubt: {rel}")
    for ordner in ERLAUBT:
        basis = (VAULT / ordner).resolve()
        if basis in p.parents:
            return p
    raise ValueError(f"Pfad nicht erlaubt: {rel}")


def schreibe_atomar(p: Path, text: str) -> None:
    """Erst in eine Nachbardatei schreiben, dann umbenennen -- ein Abbruch darf keine
    halbe Journal-Datei hinterlassen."""
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    os.replace(tmp, p)


def state() -> dict:
    return {"now": jetzt(),
            "briefing": sicher(briefing),
            "daten": sicher(datenabdeckung),
            "markt": sicher(markt)}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_a):          # keine Zugriffszeile pro Poll ins Terminal
        pass

    def _sende(self, code: int, body: bytes, typ: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", typ)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _body(self) -> dict:
        laenge = int(self.headers.get("Content-Length") or 0)
        if laenge > 1_000_000:
            raise ValueError("Body zu groß")
        return json.loads(self.rfile.read(laenge).decode("utf-8"))

    def do_POST(self):
        try:
            daten = self._body()
            if self.path.startswith("/api/write"):
                ziel = ziel_pfad(str(daten["path"]))
                schreibe_atomar(ziel, str(daten["content"]))
                antwort = {"ok": True, "path": str(ziel.relative_to(VAULT))}
            else:
                return self._sende(404, b"not found", "text/plain; charset=utf-8")
        except Exception as exc:
            body = json.dumps({"ok": False, "error": f"{type(exc).__name__}: {exc}"},
                              ensure_ascii=False).encode("utf-8")
            return self._sende(400, body, "application/json; charset=utf-8")
        self._sende(200, json.dumps(antwort, ensure_ascii=False).encode("utf-8"),
                    "application/json; charset=utf-8")

    def do_GET(self):
        if self.path.startswith("/api/state"):
            body = json.dumps(state(), ensure_ascii=False, default=str).encode("utf-8")
            return self._sende(200, body, "application/json; charset=utf-8")
        if self.path in ("/", "/index.html"):
            seite = VAULT / "tools" / "dashboard.html"
            if not seite.exists():
                return self._sende(404, b"dashboard.html fehlt", "text/plain; charset=utf-8")
            return self._sende(200, seite.read_bytes(), "text/html; charset=utf-8")
        self._sende(404, b"not found", "text/plain; charset=utf-8")


def main() -> int:
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Dashboard laeuft auf http://localhost:{PORT}  (Strg+C beendet)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nbeendet")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
