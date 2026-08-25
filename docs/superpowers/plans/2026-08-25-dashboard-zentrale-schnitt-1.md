# Dashboard „Zentrale" — Implementierungsplan Schnitt 1

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ein lokal laufendes Dashboard auf `http://localhost:8787`, das Cowork-Briefing samt Terminen, die Marktdaten des Handelstags und die 1s-Datenabdeckung anzeigt, Dateien im Vault schreiben und Claude-Läufe starten kann.

**Architecture:** Ein Python-Prozess (`tools/dashboard_serve.py`, stdlib `http.server`) sammelt alle Panel-Daten in einem einzigen `GET /api/state`-JSON und liefert daneben eine statische Seite aus. Das Frontend (`tools/dashboard.html`, Vanilla JS) pollt diesen Endpunkt alle 5 s und rendert komplett neu — es hält keinen eigenen Zustand. Schreiben (`POST /api/write`) und Läufe starten (`POST /api/run`) sind zwei kleine Endpunkte im selben Prozess.

**Tech Stack:** Python 3.14 (stdlib only: `http.server`, `json`, `subprocess`, `zoneinfo`, `pathlib`), HTML + CSS Grid + Vanilla JS, keine neue Dependency, kein Build-Schritt.

**Spec:** `docs/superpowers/specs/2026-08-25-dashboard-zentrale-design.md`

## Global Constraints

- **Keine neue Dependency.** Nur Python-stdlib. `tools/requirements.txt` bleibt unverändert (`markdown`, `pyyaml`).
- **Sprache:** Bezeichner, Kommentare und Docstrings auf Deutsch ohne Umlaute (`aendern`, `laeuft`) — so wie in `algo/bias_levels.py` und `tools/build_site.py`. UI-Texte auf Deutsch **mit** Umlauten.
- **Bind-Adresse:** ausschliesslich `127.0.0.1`, Port `8787` als Modulkonstante. Keine Konfigdatei.
- **Niemals nach `raw/marktdaten/` schreiben.** Die Whitelist ist `planung/`, `raw/journal/`, `wiki/lernpfad/` — sonst nichts.
- **Kein Panel darf ein anderes mitreissen.** Jede Datenquelle wird einzeln in `{data, error, age_s}` verpackt.
- **Keine Auto-Reparatur.** Findet das Dashboard eine Datenlücke, zeigt es sie an und lädt nichts nach (Autonomie-Regel aus `CLAUDE.md`).
- **Encoding:** jedes `read_text`/`write_text`/`subprocess.run` bekommt explizit `encoding="utf-8"`. Die Konsole ist cp1252, News-Daten enthalten Emoji.
- **Testlauf:** `python tools/test_dashboard.py` — reine `assert`s, kein pytest, kein Framework.
- **`.dashboard/` wird nicht versioniert** (`.gitignore`).

---

### Task 1: Server-Skelett, Zeit und Datenabdeckung

**Files:**
- Create: `tools/dashboard_serve.py`
- Create: `tools/test_dashboard.py`
- Modify: `.gitignore`

**Interfaces:**
- Consumes: `raw/marktdaten/1s-abdeckung.csv` (Spalten `symbol,von,bis,kontrakt,kerzen,geholt_am`, Unix-Timestamps UTC)
- Produces:
  - `VAULT: Path`, `NY: ZoneInfo`, `PORT: int`
  - `sicher(fn) -> dict` — ruft `fn()` auf, erwartet `(data, age_s)`, liefert `{"data","error","age_s"}`
  - `_letzter_werktag(heute: date) -> date`
  - `_werktage(a: date, b: date) -> int`
  - `datenabdeckung() -> tuple[dict, float]`
  - `jetzt() -> dict`
  - `state() -> dict` — der komplette `/api/state`-Blob
  - `Handler(BaseHTTPRequestHandler)` mit `do_GET`

- [ ] **Step 1: Write the failing test**

Create `tools/test_dashboard.py`:

```python
#!/usr/bin/env python3
"""Selbstcheck fuer tools/dashboard_serve.py -- reine asserts, kein Framework.

Aufruf: python tools/test_dashboard.py
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dashboard_serve as ds


def test_letzter_werktag():
    # Montag 24.08.2026 -> erwartet wird der Freitag davor, nicht das Wochenende
    assert ds._letzter_werktag(date(2026, 8, 24)) == date(2026, 8, 21)
    # Mittwoch -> Dienstag
    assert ds._letzter_werktag(date(2026, 8, 26)) == date(2026, 8, 25)
    # Sonntag -> Freitag
    assert ds._letzter_werktag(date(2026, 8, 23)) == date(2026, 8, 21)


def test_werktage():
    # Freitag -> Montag ist genau ein Werktag Rueckstand, nicht drei Kalendertage
    assert ds._werktage(date(2026, 8, 21), date(2026, 8, 24)) == 1
    assert ds._werktage(date(2026, 8, 24), date(2026, 8, 24)) == 0
    assert ds._werktage(date(2026, 8, 21), date(2026, 8, 26)) == 3


def test_sicher_faengt_fehler():
    def kaputt():
        raise RuntimeError("boom")

    r = ds.sicher(kaputt)
    assert r["data"] is None
    assert "boom" in r["error"]
    assert r["age_s"] is None

    r = ds.sicher(lambda: ({"x": 1}, 42.0))
    assert r == {"data": {"x": 1}, "error": None, "age_s": 42.0}


def test_state_hat_alle_panels():
    s = ds.state()
    for panel in ("now", "daten"):
        assert panel in s, panel
    assert set(s["daten"]) == {"data", "error", "age_s"}


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"ok  {name}")
    print("alle Tests bestanden")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python tools/test_dashboard.py`
Expected: FAIL mit `ModuleNotFoundError: No module named 'dashboard_serve'`

- [ ] **Step 3: Write minimal implementation**

Create `tools/dashboard_serve.py`:

```python
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


def state() -> dict:
    return {"now": jetzt(),
            "daten": sicher(datenabdeckung)}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_a):          # keine Zugriffszeile pro Poll ins Terminal
        pass

    def _sende(self, code: int, body: bytes, typ: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", typ)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python tools/test_dashboard.py`
Expected: PASS — vier `ok test_...`-Zeilen, dann `alle Tests bestanden`

- [ ] **Step 5: Server von Hand starten**

Run: `python tools/dashboard_serve.py`
Dann in einem zweiten Terminal: `curl http://localhost:8787/api/state`
Expected: JSON mit `now` und `daten`; `daten.data.symbole` enthält `NQ` und `ES` mit `bis`-Datum. Server mit Strg+C beenden.

- [ ] **Step 6: `.dashboard/` ignorieren**

Hänge an `.gitignore` an:

```
# Dashboard: transiente Run-Logs (analog algo/live/*/)
.dashboard/
```

- [ ] **Step 7: Commit**

```bash
git add tools/dashboard_serve.py tools/test_dashboard.py .gitignore
git commit -m "setup | Dashboard-Server: Skelett, Zeit, Datenabdeckung"
```

---

### Task 2: Schreiben mit Pfad-Whitelist

**Files:**
- Modify: `tools/dashboard_serve.py`
- Modify: `tools/test_dashboard.py`

**Interfaces:**
- Consumes: `VAULT` aus Task 1
- Produces:
  - `ERLAUBT: tuple[str, ...]`
  - `ziel_pfad(rel: str) -> Path` — wirft `ValueError` bei allem ausserhalb der Whitelist
  - `schreibe_atomar(p: Path, text: str) -> None`
  - `POST /api/write` mit Body `{"path": "planung/2026-08-25.md", "content": "..."}`

- [ ] **Step 1: Write the failing test**

Hänge in `tools/test_dashboard.py` vor dem `if __name__`-Block an:

```python
def test_ziel_pfad_whitelist():
    # erlaubt
    assert ds.ziel_pfad("planung/2026-08-25.md").name == "2026-08-25.md"
    assert ds.ziel_pfad("raw/journal/Daily Bias 2026-08-25.md").parent.name == "journal"
    assert ds.ziel_pfad("wiki/lernpfad/Lernpfad — Woche 01.md").parent.name == "lernpfad"

    # abgelehnt: Traversal, absolute Pfade, Marktdaten, falsche Endung
    for boese in ("planung/../raw/marktdaten/kaputt.md",
                  "raw/marktdaten/NQ.md",
                  "C:/Windows/Temp/x.md",
                  "/etc/passwd",
                  "wiki/index.md",
                  "planung/notiz.txt"):
        try:
            ds.ziel_pfad(boese)
        except ValueError:
            continue
        raise AssertionError(f"haette abgelehnt werden muessen: {boese}")


def test_atomarer_write():
    import os
    ziel = ds.VAULT / "planung" / "_test_atomar.md"
    try:
        ds.schreibe_atomar(ziel, "alt")
        assert ziel.read_text(encoding="utf-8") == "alt"

        # simulierter Abbruch mitten im Schreiben: die alte Datei bleibt unangetastet
        echt = os.replace
        os.replace = lambda *a, **k: (_ for _ in ()).throw(OSError("abgebrochen"))
        try:
            ds.schreibe_atomar(ziel, "neu-halb")
        except OSError:
            pass
        finally:
            os.replace = echt
        assert ziel.read_text(encoding="utf-8") == "alt", "Teildatei ueberschrieben"
    finally:
        ziel.unlink(missing_ok=True)
        for rest in ziel.parent.glob("_test_atomar.md.tmp"):
            rest.unlink()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python tools/test_dashboard.py`
Expected: FAIL mit `AttributeError: module 'dashboard_serve' has no attribute 'ziel_pfad'`

- [ ] **Step 3: Write minimal implementation**

In `tools/dashboard_serve.py`: `import os` zu den Imports ergänzen, dann vor `class Handler` einfügen:

```python
ERLAUBT = ("planung", "raw/journal", "wiki/lernpfad")


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
```

Und in `class Handler` ergänzen:

```python
    def _body(self) -> dict:
        laenge = int(self.headers.get("Content-Length") or 0)
        if laenge > 1_000_000:
            raise ValueError("Body zu gross")
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python tools/test_dashboard.py`
Expected: PASS — jetzt sechs `ok test_...`-Zeilen

- [ ] **Step 5: Endpunkt von Hand prüfen**

Server starten (`python tools/dashboard_serve.py`), dann:

```bash
curl -X POST http://localhost:8787/api/write -H "Content-Type: application/json" \
  -d "{\"path\":\"planung/_probe.md\",\"content\":\"hallo\"}"
curl -X POST http://localhost:8787/api/write -H "Content-Type: application/json" \
  -d "{\"path\":\"raw/marktdaten/boese.md\",\"content\":\"nein\"}"
```

Expected: erster Aufruf `{"ok": true, ...}` und `planung/_probe.md` existiert; zweiter Aufruf HTTP 400 mit `Pfad nicht erlaubt`. Danach `planung/_probe.md` löschen.

- [ ] **Step 6: Commit**

```bash
git add tools/dashboard_serve.py tools/test_dashboard.py
git commit -m "setup | Dashboard: /api/write mit Pfad-Whitelist und atomarem Schreiben"
```

---

### Task 3: Briefing-Panel

**Files:**
- Modify: `tools/dashboard_serve.py`
- Modify: `tools/test_dashboard.py`

**Interfaces:**
- Consumes: `VAULT`, `NY`, `sicher` aus Task 1
- Produces:
  - `BRIEFINGS: Path` (= `VAULT / "briefings"`)
  - `_ist_briefing(p: Path) -> bool` — nur datierte Dateien; `briefings/status.md` ist
    laut `CLAUDE.md` die Lernpfad-Statusseite und kein Briefing
  - `_parse_briefing(text: str) -> dict` — liefert `{"text": str, "termine": [{"zeit","titel"}]}`
  - `briefing() -> tuple[dict, float]` — Panel-Daten inklusive `age_s` aus der Mtime
  - `state()` enthält zusätzlich den Schlüssel `briefing`

Format der Quelldatei (schreibt Cowork, siehe Spec-Abschnitt „Externe Voraussetzung"):

```markdown
---
typ: morgen-briefing
datum: 2026-08-25
---

Fliesstext des Briefings, beliebig viele Absaetze.

## Termine

- 09:00 — Uni Mathe
- 14:30 — Call Quant
```

- [ ] **Step 1: Write the failing test**

Hänge in `tools/test_dashboard.py` an:

```python
def test_parse_briefing():
    text = ("---\ntyp: morgen-briefing\n---\n\n"
            "Erster Absatz.\n\n"
            "## Termine\n\n"
            "- 09:00 — Uni Mathe\n"
            "- 14:30 — Call Quant\n\n"
            "## Sonstiges\n\n"
            "- kein Termin, sondern eine Notiz\n")
    r = ds._parse_briefing(text)
    assert r["termine"] == [{"zeit": "09:00", "titel": "Uni Mathe"},
                            {"zeit": "14:30", "titel": "Call Quant"}], r["termine"]
    assert r["text"].startswith("Erster Absatz."), "Frontmatter nicht abgeschnitten"
    assert "kein Termin" not in str(r["termine"]), "Liste aus fremdem Abschnitt uebernommen"


def test_parse_briefing_ohne_termine():
    # tolerant: fehlt der Abschnitt, bleibt die Liste leer und der Text kommt trotzdem durch
    r = ds._parse_briefing("Nur Fliesstext.\n")
    assert r["termine"] == []
    assert r["text"] == "Nur Fliesstext."


def test_briefing_fehlend_meldet_statt_zu_werfen():
    # Kernfall aus der Spec: Cowork lief nicht -> error, keine Exception, kein alter Wert
    echt = ds.BRIEFINGS
    ds.BRIEFINGS = ds.VAULT / "_gibt_es_nicht"
    try:
        r = ds.sicher(ds.briefing)
    finally:
        ds.BRIEFINGS = echt
    assert r["error"] is None, "fehlendes Briefing ist kein Serverfehler"
    assert r["data"]["fehlt"] is True
    assert r["data"]["hinweis"], "kein Hinweistext fuer den Nutzer"


def test_status_md_ist_kein_briefing():
    # briefings/status.md ist die Lernpfad-Statusseite (CLAUDE.md), kein Briefing
    assert ds._ist_briefing(ds.VAULT / "briefings" / "status.md") is False
    assert ds._ist_briefing(ds.VAULT / "briefings" / "2026-08-25-morgen.md") is True


def test_briefing_altes_wird_als_alt_erkannt():
    # Spec-Kernfall: ein Briefing von gestern darf nicht aussehen wie das von heute.
    import os
    from datetime import datetime, timedelta
    echt = ds.BRIEFINGS
    ds.BRIEFINGS = ds.VAULT / "_test_briefings"
    ds.BRIEFINGS.mkdir(exist_ok=True)
    gestern = (datetime.now(ds.NY).date() - timedelta(days=1)).isoformat()
    p = ds.BRIEFINGS / f"{gestern}-morgen.md"
    p.write_text("Altes Briefing.\n", encoding="utf-8")
    alt = time.time() - 30 * 3600
    os.utime(p, (alt, alt))
    try:
        r = ds.sicher(ds.briefing)
        assert r["error"] is None
        assert r["data"]["fehlt"] is True, "Briefing von gestern als heutiges ausgegeben"
        assert gestern in r["data"]["hinweis"], r["data"]["hinweis"]
        assert r["age_s"] > 24 * 3600, r["age_s"]
    finally:
        ds.BRIEFINGS = echt
        p.unlink(missing_ok=True)
        (ds.VAULT / "_test_briefings").rmdir()
```

Ergänze dafür oben in `tools/test_dashboard.py` den Import `import time`.

- [ ] **Step 2: Run test to verify it fails**

Run: `python tools/test_dashboard.py`
Expected: FAIL mit `AttributeError: module 'dashboard_serve' has no attribute '_parse_briefing'`

- [ ] **Step 3: Write minimal implementation**

In `tools/dashboard_serve.py` vor `def state()` einfügen:

```python
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
                "hinweis": "Kein Briefing vorhanden — laeuft Cowork und schreibt es "
                           "nach briefings/?"}, 0.0
    d = _parse_briefing(quelle.read_text(encoding="utf-8", errors="replace"))
    d["fehlt"] = not von_heute
    d["datei"] = quelle.name
    if d["fehlt"]:
        d["hinweis"] = (f"Kein Briefing fuer {heute} — letztes: {quelle.name}")
    return d, time.time() - quelle.stat().st_mtime
```

In `state()` die Zeile ergänzen:

```python
def state() -> dict:
    return {"now": jetzt(),
            "briefing": sicher(briefing),
            "daten": sicher(datenabdeckung)}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python tools/test_dashboard.py`
Expected: PASS — elf `ok test_...`-Zeilen

- [ ] **Step 5: Mit einer echten Datei gegenprüfen**

```bash
mkdir -p briefings
printf -- "---\ntyp: morgen-briefing\n---\n\nProbe.\n\n## Termine\n\n- 09:00 — Uni Mathe\n" > "briefings/$(date +%Y-%m-%d)-morgen.md"
python -c "import sys; sys.path.insert(0,'tools'); import dashboard_serve as d, json; print(json.dumps(d.sicher(d.briefing), ensure_ascii=False, indent=2))"
```

Expected: `fehlt: false`, ein Termin, `age_s` nahe 0. Probedatei danach löschen.

- [ ] **Step 6: Commit**

```bash
git add tools/dashboard_serve.py tools/test_dashboard.py
git commit -m "setup | Dashboard: Briefing-Panel mit tolerantem Termin-Parser"
```

---

### Task 4: Markt-Panel

**Files:**
- Modify: `tools/dashboard_serve.py`
- Modify: `tools/test_dashboard.py`

**Interfaces:**
- Consumes: `VAULT`, `NY`, `sicher` aus Task 1; `algo/bias_levels.py` als Subprozess (gibt JSON auf stdout mit den Schlüsseln `day`, `weekday`, `weekly_range`, `yesterday_range`, `gaps`, `news`)
- Produces:
  - `CACHE_S = 900`, `_markt_cache: dict`
  - `_neueste_bias() -> dict | None` — `{"datei": str, "bias": str, "datum": str}` aus `raw/journal/Daily Bias *.md`
  - `markt() -> tuple[dict, float]`
  - `state()` enthält zusätzlich den Schlüssel `markt`

`bias_levels.py` braucht Netz und mehrere Sekunden. Deshalb: Cache mit Mindestalter 900 s, Subprozess-Timeout 20 s, und im Fehlerfall nennt die Meldung den letzten erfolgreichen Abruf (Spec-Anforderung).

- [ ] **Step 1: Write the failing test**

Hänge in `tools/test_dashboard.py` an:

```python
def test_neueste_bias():
    r = ds._neueste_bias()
    # Im Vault liegen Bias-Dateien; ist der Ordner leer, ist None korrekt.
    assert r is None or {"datei", "bias", "datum"} <= set(r), r


def test_markt_cache_verhindert_zweiten_aufruf():
    aufrufe = []

    def fake_run(*a, **k):
        aufrufe.append(1)
        class P:
            returncode = 0
            stdout = '{"day": "2026-08-25", "weekday": "Tuesday", "news": {"events": []}}'
            stderr = ""
        return P()

    echt_run, echt_cache = ds.subprocess.run, dict(ds._markt_cache)
    ds.subprocess.run = fake_run
    ds._markt_cache.update(t=0.0, data=None, wall=0.0)
    try:
        d1, _ = ds.markt()
        d2, _ = ds.markt()
    finally:
        ds.subprocess.run = echt_run
        ds._markt_cache.update(echt_cache)
    assert len(aufrufe) == 1, f"bias_levels.py {len(aufrufe)}x aufgerufen statt 1x"
    assert d1["day"] == d2["day"] == "2026-08-25"


def test_markt_fehler_nennt_letzten_erfolg():
    def fake_run(*a, **k):
        raise ds.subprocess.TimeoutExpired(cmd="bias_levels.py", timeout=20)

    echt_run, echt_cache = ds.subprocess.run, dict(ds._markt_cache)
    ds.subprocess.run = fake_run
    ds._markt_cache.update(t=0.0, data=None, wall=0.0)
    try:
        r = ds.sicher(ds.markt)
    finally:
        ds.subprocess.run = echt_run
        ds._markt_cache.update(echt_cache)
    assert r["data"] is None
    assert "letzter erfolgreicher Abruf" in r["error"], r["error"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python tools/test_dashboard.py`
Expected: FAIL mit `AttributeError: module 'dashboard_serve' has no attribute '_neueste_bias'`

- [ ] **Step 3: Write minimal implementation**

In `tools/dashboard_serve.py`: `import re`, `import subprocess` und `import sys` zu den Imports ergänzen, dann vor `def state()` einfügen:

```python
BIAS_ORDNER = VAULT / "raw" / "journal"
CACHE_S = 900
_markt_cache: dict = {"t": 0.0, "data": None, "wall": 0.0}


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


def markt() -> tuple[dict, float]:
    """Levels + News aus algo/bias_levels.py, gecacht.

    Der Aufruf zieht News ueber HTTP und braucht Sekunden -- bei jedem 5s-Poll waere das
    ein Dauerfeuer auf ForexFactory. Deshalb Mindestalter CACHE_S; `age_s` sagt immer,
    wie alt der Wert wirklich ist."""
    if _markt_cache["data"] is None or time.monotonic() - _markt_cache["t"] > CACHE_S:
        try:
            p = subprocess.run([sys.executable, str(VAULT / "algo" / "bias_levels.py")],
                               capture_output=True, text=True, timeout=20,
                               encoding="utf-8", errors="replace", cwd=str(VAULT))
            if p.returncode != 0:
                raise RuntimeError((p.stderr or "").strip()[-300:] or f"exit {p.returncode}")
            _markt_cache.update(t=time.monotonic(), data=json.loads(p.stdout),
                                wall=time.time())
        except Exception as exc:
            letzte = (datetime.fromtimestamp(_markt_cache["wall"], NY).strftime("%d.%m. %H:%M")
                      if _markt_cache["wall"] else "nie")
            raise RuntimeError(f"{type(exc).__name__}: {exc} "
                               f"(letzter erfolgreicher Abruf: {letzte})") from None
    d = dict(_markt_cache["data"])
    d["bias_datei"] = _neueste_bias()
    return d, time.time() - _markt_cache["wall"]
```

In `state()` ergänzen:

```python
            "markt": sicher(markt),
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python tools/test_dashboard.py`
Expected: PASS — vierzehn `ok test_...`-Zeilen

- [ ] **Step 5: Echten Abruf gegenprüfen**

```bash
python -c "import sys; sys.path.insert(0,'tools'); import dashboard_serve as d, json; r=d.sicher(d.markt); print(json.dumps(r, ensure_ascii=False, default=str)[:900])"
```

Expected: `error: null`, `data.day` ist der heutige Handelstag, `data.news.events` ist eine Liste, `data.bias_datei.bias` ist gesetzt. Dauert beim ersten Aufruf einige Sekunden (Netz).

- [ ] **Step 6: Commit**

```bash
git add tools/dashboard_serve.py tools/test_dashboard.py
git commit -m "setup | Dashboard: Markt-Panel (bias_levels.py mit Cache und Timeout)"
```

---

### Task 5: Läufe starten (`POST /api/run`)

**Files:**
- Modify: `tools/dashboard_serve.py`
- Modify: `tools/test_dashboard.py`

**Interfaces:**
- Consumes: `VAULT`, `NY`, `sicher` aus Task 1; `do_POST` aus Task 2
- Produces:
  - `RUNS: Path` (= `VAULT / ".dashboard" / "runs"`), `CLAUDE: str`
  - `starte_run(prompt: str) -> str` — liefert die Run-ID
  - `runs() -> tuple[list[dict], float]` — je Run `{"id","status","exit","log"}`, `status` ∈ `laeuft | ok | fehlgeschlagen | beendet`
  - `state()` enthält zusätzlich den Schlüssel `runs`
  - `POST /api/run` mit Body `{"prompt": "..."}` → `{"ok": true, "id": "..."}`

- [ ] **Step 1: Write the failing test**

Hänge in `tools/test_dashboard.py` an:

```python
def test_runs_liest_logs():
    ds.RUNS.mkdir(parents=True, exist_ok=True)
    probe = ds.RUNS / "_test-run.log"
    probe.write_text("Zeile 1\nZeile 2\nZeile 3\nZeile 4\n", encoding="utf-8")
    try:
        liste, _ = ds.runs()
        treffer = [r for r in liste if r["id"] == "_test-run"]
        assert treffer, "Log nicht gefunden"
        r = treffer[0]
        # ohne laufenden Prozess: beendet, und nur die letzten drei Zeilen
        assert r["status"] == "beendet", r["status"]
        assert r["log"] == ["Zeile 2", "Zeile 3", "Zeile 4"], r["log"]
    finally:
        probe.unlink(missing_ok=True)


def test_starte_run_lehnt_leeren_prompt_ab():
    for leer in ("", "   ", None):
        try:
            ds.starte_run(leer)
        except ValueError:
            continue
        raise AssertionError(f"leerer Prompt akzeptiert: {leer!r}")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python tools/test_dashboard.py`
Expected: FAIL mit `AttributeError: module 'dashboard_serve' has no attribute 'RUNS'`

- [ ] **Step 3: Write minimal implementation**

In `tools/dashboard_serve.py`: `import shutil` ergänzen, dann vor `def state()` einfügen:

```python
RUNS = VAULT / ".dashboard" / "runs"
# Auf Windows ist `claude` eine .cmd -- Popen ohne shell findet sie nur ueber den vollen Pfad.
CLAUDE = shutil.which("claude") or "claude"
_PROZESSE: dict[str, subprocess.Popen] = {}


def starte_run(prompt: str) -> str:
    """Startet `claude -p <prompt>` im Vault, Ausgabe nach .dashboard/runs/<id>.log."""
    if not (prompt or "").strip():
        raise ValueError("leerer Prompt")
    RUNS.mkdir(parents=True, exist_ok=True)
    rid = datetime.now(NY).strftime("%Y%m%d-%H%M%S")
    fh = (RUNS / f"{rid}.log").open("w", encoding="utf-8", errors="replace")
    _PROZESSE[rid] = subprocess.Popen([CLAUDE, "-p", prompt], cwd=str(VAULT),
                                      stdout=fh, stderr=subprocess.STDOUT)
    return rid


def runs() -> tuple[list[dict], float]:
    """Die fuenf juengsten Laeufe mit den letzten drei Logzeilen.

    Kein automatischer Neustart bei Fehlschlag -- ein Lauf, der stirbt, bleibt sichtbar
    gestorben."""
    if not RUNS.is_dir():
        return [], 0.0
    out = []
    for log in sorted(RUNS.glob("*.log"), key=lambda p: p.stat().st_mtime,
                      reverse=True)[:5]:
        proc = _PROZESSE.get(log.stem)
        code = proc.poll() if proc else None
        status = ("laeuft" if proc is not None and code is None else
                  "ok" if code == 0 else
                  "fehlgeschlagen" if code is not None else "beendet")
        zeilen = log.read_text(encoding="utf-8", errors="replace").splitlines()[-3:]
        out.append({"id": log.stem, "status": status, "exit": code, "log": zeilen})
    return out, 0.0
```

In `state()` ergänzen:

```python
            "runs": sicher(runs),
```

Und in `do_POST` den `/api/write`-Zweig um einen zweiten ergänzen:

```python
            elif self.path.startswith("/api/run"):
                antwort = {"ok": True, "id": starte_run(str(daten.get("prompt") or ""))}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python tools/test_dashboard.py`
Expected: PASS — sechzehn `ok test_...`-Zeilen

- [ ] **Step 5: Echten Lauf starten**

Server starten, dann:

```bash
curl -X POST http://localhost:8787/api/run -H "Content-Type: application/json" \
  -d "{\"prompt\":\"Antworte nur mit dem Wort Testlauf.\"}"
curl http://localhost:8787/api/state
```

Expected: erst `{"ok": true, "id": "..."}`; im `state` steht der Run zunächst als `laeuft`, nach ein paar Sekunden als `ok` mit `Testlauf` in `log`. Danach `.dashboard/runs/` leeren.

- [ ] **Step 6: Commit**

```bash
git add tools/dashboard_serve.py tools/test_dashboard.py
git commit -m "setup | Dashboard: /api/run startet claude -p, Logs im State"
```

---

### Task 6: Frontend

**Files:**
- Create: `tools/dashboard.html`

**Interfaces:**
- Consumes: `GET /api/state` (Schlüssel `now`, `briefing`, `markt`, `daten`, `runs`), `POST /api/run`
- Produces: die Seite selbst; keine weiteren Konsumenten

- [ ] **Step 1: Seite schreiben**

Create `tools/dashboard.html`:

```html
<!doctype html>
<meta charset="utf-8">
<title>Zentrale</title>
<style>
  :root {
    --bg: #fbfaf8; --karte: #fff; --rahmen: #e3ded6; --text: #1c1a17;
    --leise: #6b6560; --ok: #2f7a3f; --warn: #a8760a; --fehler: #b3261e;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #16171a; --karte: #1d1f23; --rahmen: #2d3036; --text: #e6e3de;
      --leise: #948e87; --ok: #6bbd7c; --warn: #d9a441; --fehler: #e4756b;
    }
  }
  * { box-sizing: border-box; }
  body { margin: 0; padding: 1rem; background: var(--bg); color: var(--text);
         font: 15px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif; }
  header { display: flex; justify-content: space-between; align-items: baseline;
           gap: 1rem; margin-bottom: 1rem; flex-wrap: wrap; }
  header h1 { font-size: 1.05rem; font-weight: 600; margin: 0; }
  #grid { display: grid; gap: 1rem;
          grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); align-items: start; }
  section { background: var(--karte); border: 1px solid var(--rahmen);
            border-radius: 10px; padding: .9rem 1rem; }
  section h2 { font-size: .72rem; letter-spacing: .09em; text-transform: uppercase;
               color: var(--leise); margin: 0 0 .7rem; }
  .alter { float: right; font-weight: 400; letter-spacing: 0; text-transform: none; }
  .fehler { color: var(--fehler); }
  .ok { color: var(--ok); }
  .warn { color: var(--warn); }
  .leise { color: var(--leise); }
  table { width: 100%; border-collapse: collapse; }
  td { padding: .12rem 0; vertical-align: baseline; }
  td.wert { text-align: right; font-variant-numeric: tabular-nums; }
  td.zeit { width: 4.2rem; font-variant-numeric: tabular-nums; color: var(--leise); }
  pre { white-space: pre-wrap; font: inherit; margin: 0 0 .6rem; }
  .log { font: 12px/1.4 ui-monospace, Consolas, monospace; color: var(--leise);
         background: var(--bg); border-radius: 6px; padding: .4rem .6rem; margin-top: .3rem; }
  button { font: inherit; padding: .3rem .7rem; border-radius: 6px;
           border: 1px solid var(--rahmen); background: var(--bg); color: var(--text);
           cursor: pointer; }
  button:hover { border-color: var(--leise); }
</style>

<header>
  <h1 id="kopf">…</h1>
  <div id="daten" class="leise"></div>
</header>
<div id="grid">
  <section id="p-heute"><h2>Heute</h2><div class="inhalt"></div></section>
  <section id="p-markt"><h2>Markt</h2><div class="inhalt"></div></section>
  <section id="p-runs"><h2>Läufe</h2><div class="inhalt"></div></section>
</div>

<script>
const esc = s => String(s ?? "").replace(/[&<>]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));
const alter = s => s == null ? "" : s < 90 ? "gerade eben"
  : s < 5400 ? Math.round(s / 60) + " min alt" : Math.round(s / 3600) + " h alt";

function kachel(id, panel, render) {
  const sec = document.getElementById(id);
  const kopf = sec.querySelector("h2");
  kopf.querySelector(".alter")?.remove();
  const badge = document.createElement("span");
  badge.className = "alter leise";
  badge.textContent = panel?.error ? "" : alter(panel?.age_s);
  kopf.append(badge);
  sec.querySelector(".inhalt").innerHTML =
    panel?.error ? `<p class="fehler">${esc(panel.error)}</p>` : render(panel.data);
}

function heute(d) {
  const termine = d.termine.length
    ? `<table>${d.termine.map(t =>
        `<tr><td class="zeit">${esc(t.zeit)}</td><td>${esc(t.titel)}</td></tr>`).join("")}</table>`
    : `<p class="leise">Keine Termine hinterlegt.</p>`;
  const kopf = d.fehlt
    ? `<p class="warn">${esc(d.hinweis)}</p>
       <p><button onclick="lauf('Erstelle das heutige Morgen-Briefing.')">nachholen</button></p>`
    : `<p class="leise">${esc(d.datei)}</p><pre>${esc(d.text)}</pre>`;
  return kopf + `<h2>Termine</h2>` + termine;
}

function markt(d) {
  const z = [];
  const r = (label, v) => v && z.push(
    `<tr><td>${esc(label)}</td><td class="wert">${esc(v)}</td></tr>`);
  if (d.yesterday_range) {
    r("PDH", d.yesterday_range.high); r("PDL", d.yesterday_range.low);
    r("PD Close", d.yesterday_range.close);
  }
  if (d.weekly_range) { r("Wochen-High", d.weekly_range.high); r("Wochen-Low", d.weekly_range.low); }
  for (const g of (d.gaps?.offen ?? []).slice(0, 4)) r(`Gap ${esc(g.tag)} open`, g.open);
  const levels = z.length ? `<table>${z.join("")}</table>`
                          : `<p class="leise">Keine Levels verfügbar.</p>`;
  const news = d.news?.error
    ? `<p class="warn">News: ${esc(d.news.error)}</p>`
    : (d.news?.events ?? []).length
      ? `<table>${d.news.events.map(e =>
          `<tr><td class="zeit">${esc(e.ny.slice(-5))}</td><td>${esc(e.impact)} ${esc(e.title)}</td></tr>`
        ).join("")}</table>`
      : `<p class="leise">Keine USD-Termine mit Red-/Orange-Impact.</p>`;
  const bias = d.bias_datei
    ? `<p>Bias ${esc(d.bias_datei.datum)}: <strong>${esc(d.bias_datei.bias)}</strong></p>`
    : `<p class="leise">Keine Bias-Datei gefunden.</p>`;
  return levels + `<h2>News (USD, NY)</h2>` + news + bias;
}

function laeufe(liste) {
  if (!liste.length) return `<p class="leise">Kein Lauf gestartet.</p>`;
  const farbe = {laeuft: "", ok: "ok", fehlgeschlagen: "fehler", beendet: "leise"};
  return liste.map(r => `
    <div><span class="${farbe[r.status]}">${esc(r.status)}</span>
         <span class="leise">${esc(r.id)}</span>
         ${r.log.length ? `<div class="log">${r.log.map(esc).join("<br>")}</div>` : ""}</div>`
  ).join("");
}

async function lauf(prompt) {
  const p = window.prompt("Prompt für claude -p:", prompt ?? "");
  if (!p) return;
  await fetch("/api/run", {method: "POST", headers: {"Content-Type": "application/json"},
                           body: JSON.stringify({prompt: p})});
  tick();
}

async function tick() {
  let s;
  try {
    s = await (await fetch("/api/state")).json();
  } catch (e) {
    document.getElementById("kopf").textContent = "Server nicht erreichbar";
    return;
  }
  document.getElementById("kopf").textContent =
    `${s.now.weekday}, ${s.now.datum} · NY ${s.now.ny}`;
  const d = s.daten;
  document.getElementById("daten").innerHTML = d.error
    ? `<span class="fehler">${esc(d.error)}</span>`
    : Object.entries(d.data.symbole).map(([sym, v]) =>
        `<span class="${v.fehlt_tage ? "fehler" : "ok"}">${esc(sym)} 1s bis ${esc(v.bis)}${
          v.fehlt_tage ? ` · ${v.fehlt_tage} Tage Lücke` : ""}</span>`).join(" · ");
  kachel("p-heute", s.briefing, heute);
  kachel("p-markt", s.markt, markt);
  kachel("p-runs", s.runs, laeufe);
}

tick();
setInterval(tick, 5000);
</script>
```

- [ ] **Step 2: Im Browser prüfen**

Run: `python tools/dashboard_serve.py`, dann `http://localhost:8787` öffnen.
Expected: Kopfzeile mit Wochentag/Datum/NY-Zeit und der 1s-Abdeckung je Symbol; drei Kacheln nebeneinander; Markt-Kachel zeigt PDH/PDL und die News-Liste; Briefing-Kachel zeigt den Hinweis „Kein Briefing vorhanden" mit Nachholen-Button (solange Cowork noch nichts schreibt); Läufe-Kachel „Kein Lauf gestartet". Fensterbreite verkleinern: Kacheln fließen untereinander.

- [ ] **Step 3: Fehlerfall sichtbar prüfen**

Netzwerk trennen (oder WLAN aus), Server neu starten, Seite laden.
Expected: Markt-Kachel zeigt den Fehlertext inklusive „letzter erfolgreicher Abruf: nie" in Rot — die anderen Kacheln rendern normal weiter.

- [ ] **Step 4: Commit**

```bash
git add tools/dashboard.html
git commit -m "setup | Dashboard-Frontend: Grid, Panels Heute/Markt/Laeufe"
```

---

### Task 7: Start-Skript und Doku

**Files:**
- Create: `dashboard.cmd`
- Modify: `CLAUDE.md`

**Interfaces:**
- Consumes: `tools/dashboard_serve.py`
- Produces: nichts, was Code liest — nur Startkomfort und Auffindbarkeit

- [ ] **Step 1: Start-Skript schreiben**

Create `dashboard.cmd` (analog zum vorhandenen `tools/bias-cron.cmd`):

```bat
@echo off
rem Startet die Dashboard-Zentrale und oeffnet sie im Browser.
cd /d "%~dp0"
start "" http://localhost:8787
python tools\dashboard_serve.py
```

- [ ] **Step 2: Von Hand prüfen**

Run: `.\dashboard.cmd`
Expected: Browser öffnet `http://localhost:8787`, das Dashboard lädt. Fenster mit Strg+C schließen.

- [ ] **Step 3: In CLAUDE.md eintragen**

Ergänze in `CLAUDE.md` nach dem Abschnitt `## Layer 3 — site/` einen neuen Abschnitt:

```markdown
## Dashboard-Zentrale

`.\dashboard.cmd` startet die lokale Arbeitszentrale auf `http://localhost:8787`
(`tools/dashboard_serve.py` + `tools/dashboard.html`, Design:
`docs/superpowers/specs/2026-08-25-dashboard-zentrale-design.md`). Sie zeigt das
Cowork-Briefing samt Terminen, die Levels/News des Handelstags und die 1s-Datenabdeckung,
und startet auf Knopfdruck `claude -p`-Laeufe.

Sie liest und schreibt ausschliesslich Dateien im Vault. Schreiben ist auf `planung/`,
`raw/journal/` und `wiki/lernpfad/` begrenzt — nach `raw/marktdaten/` schreibt sie nie.
Datenluecken meldet sie nur, sie schliesst sie nicht.

Voraussetzung fuer das Briefing-Panel: die Cowork-Aufgaben „Daily briefing" und
„Abend briefing" schreiben ihr Ergebnis zusaetzlich nach
`briefings/<JJJJ-MM-TT>-{morgen,abend}.md`, Termine als Liste unter `## Termine`.

Selbstcheck: `python tools/test_dashboard.py`.
```

- [ ] **Step 4: Gesamten Testlauf**

Run: `python tools/test_dashboard.py`
Expected: PASS — alle sechzehn Tests, `alle Tests bestanden`

- [ ] **Step 5: Commit**

```bash
git add dashboard.cmd CLAUDE.md
git commit -m "setup | Dashboard: Startskript und Eintrag in CLAUDE.md"
```

---

## Nach Abschluss

Schnitt 1 ist fertig, wenn `.\dashboard.cmd` eine Seite zeigt, die Briefing, Levels/News und Datenabdeckung korrekt darstellt — und bei fehlender oder veralteter Quelle sichtbar sagt, dass sie fehlt.

**Was Jannes danach selbst tun muss:** die beiden Cowork-Anweisungen um den Satz aus der Spec erweitern („zusätzlich nach `briefings/<datum>-morgen.md` schreiben"). Vorher bleibt das Briefing-Panel beim Hinweistext.

**Nicht in diesem Plan:** Agents-Panel (Cron-Status, Skill-Katalog, Transcripts) und Planungs-Panel (Todos, Journal-Notizen, Lernpfad) — Schnitt 2 und 3 bekommen eigene Pläne. Die Endpunkte, die sie brauchen, stehen nach Task 5 bereits.
