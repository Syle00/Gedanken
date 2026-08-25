# Main-Agent ("Wachhund") Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ein Taktgeber, der alle geplanten Vault-Läufe startet, auf Korrektheit/Aktivität/Laufzeit prüft und Fehlschläge über einen LLM-Agenten selbstständig repariert.

**Architecture:** Ein Windows-Aufgabenplaner-Eintrag ruft alle 10 min `tools/agent_tick.py`. Das Skript liest den Zeitplan aus dem YAML-Frontmatter der Commands/Skills (`schedule`, `expect`, `timeout`, `extern`), entscheidet ohne LLM, was fällig ist, startet `claude -p "/<command>"`, misst Laufzeit und prüft `expect`. Ist alles grün, endet der Tick bei null Tokens. Nur bei rotem Befund wird `claude -p "/wachhund <json>"` gerufen, der diagnostiziert, repariert und berichtet.

**Tech Stack:** Python 3.14, nur Standardbibliothek + `pyyaml` (bereits in `tools/requirements.txt`). **Keine neuen Abhängigkeiten** — insbesondere kein `croniter` und kein `pytest` (beide nicht installiert). Cron-Auswertung: eigener Matcher für die tatsächlich benutzte Teilmenge. Tests: `assert`-Skript nach Repo-Konvention `tools/test_*.py`.

**Spec:** `docs/superpowers/specs/2026-08-25-main-agent-wachhund-design.md`

## Global Constraints

- **Sprache:** Alle Nutzerausgaben, Commit-Messages und Command-Texte auf **Deutsch**. Bezeichner im Code englisch/deutsch gemischt wie im Repo üblich (`scan_entries`, `ausloeser`).
- **Keine neuen Abhängigkeiten.** `tools/requirements.txt` bleibt unverändert (`markdown`, `pyyaml`).
- **Kein `pytest`.** Tests sind `assert`-basierte Skripte, ausführbar mit `python tools/test_agent_tick.py`.
- **`raw/` ist unveränderlich.** Kein Task in diesem Plan schreibt jemals nach `raw/`. Der Tick liest dort nur (`raw/marktdaten/1s-abdeckung.csv`, `raw/journal/Daily Bias *.md`).
- **Determinismus:** Jede Funktion, deren Ergebnis von der Uhr abhängt, nimmt `now: datetime` bzw. `today: date` als **Parameter** — nie `datetime.now()` im Funktionsrumpf außer in `main()`. Ohne das ist der Selbsttest nicht schreibbar.
- **Zeitzone:** Alles in lokaler Rechnerzeit (naive `datetime`). Der Windows-Task, die Cowork-Briefings und `push.ps1` laufen alle in Ortszeit; eine zweite Zeitbasis wäre eine Fehlerquelle ohne Nutzen.
- **Registerpfad:** `algo/live/agent-runs.csv`. **Ist bereits gitignored** (`algo/live/*/` laut `CLAUDE.md` — vor Task 4 prüfen, ob die Regel auch Dateien direkt in `algo/live/` erfasst; falls nicht, Muster ergänzen, damit das Register nicht bei jedem Tick einen Commit auslöst).
- **Commit-Format:** `<typ> | <worum ging es>`, Typen `setup`, `fix`, `ingest`, `query`, `lint`, `synthesis` (erzwungen von `push.ps1`).
- **Stop-Hook beachten:** Das Projekt hat einen Stop-Hook, der bei jeder Änderung `push.ps1` ausführt. Commits in diesem Plan werden also gepusht. Das ist erwünscht — aber es heißt, ein kaputter Zwischenstand ist sofort auf GitHub. Jeder Task endet grün.

---

### Task 1: Vertrag lesen — Scanner, Cron-Matcher, Platzhalter

Reine Funktionen ohne Seiteneffekte. Nach diesem Task kann das Skript den Zeitplan lesen und beantworten "war X um Zeitpunkt Y fällig?", aber noch nichts starten.

**Files:**
- Create: `tools/agent_tick.py`
- Test: `tools/test_agent_tick.py`

**Interfaces:**
- Consumes: `next_trading_day(date) -> date` und `next_monday(date) -> date` aus `algo/bias_levels.py` (Zeilen 144 und 152, bereits vorhanden)
- Produces:
  - `@dataclass Entry(name: str, schedule: str, expect: str | None, timeout_s: int, extern: bool, quelle: Path)`
  - `scan_entries(root: Path) -> list[Entry]`
  - `cron_matches(expr: str, when: datetime) -> bool`
  - `last_due(expr: str, now: datetime, lookback_h: int = 36) -> datetime | None`
  - `resolve_placeholders(text: str, today: date) -> str`
  - `parse_timeout(text: str | None) -> int`

- [ ] **Step 1: Den Test schreiben**

Erstelle `tools/test_agent_tick.py`:

```python
"""Selbstcheck fuer tools/agent_tick.py. Ausfuehren: python tools/test_agent_tick.py"""
import sys
import tempfile
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agent_tick import (
    Entry, cron_matches, last_due, parse_timeout, resolve_placeholders, scan_entries,
)


def test_cron_matches():
    # "0 20 * * 0-4" = 20:00 an Sonntag(0) bis Donnerstag(4)
    assert cron_matches("0 20 * * 0-4", datetime(2026, 8, 24, 20, 0))    # Montag
    assert not cron_matches("0 20 * * 0-4", datetime(2026, 8, 24, 20, 1))
    assert not cron_matches("0 20 * * 0-4", datetime(2026, 8, 24, 19, 0))
    assert not cron_matches("0 20 * * 0-4", datetime(2026, 8, 28, 20, 0))  # Freitag
    assert cron_matches("0 20 * * 5", datetime(2026, 8, 28, 20, 0))        # Freitag
    assert cron_matches("*/10 * * * *", datetime(2026, 8, 24, 13, 30))
    assert not cron_matches("*/10 * * * *", datetime(2026, 8, 24, 13, 31))
    assert cron_matches("30 6 * * *", datetime(2026, 8, 24, 6, 30))
    assert cron_matches("0 23 * * 1-5", datetime(2026, 8, 28, 23, 0))      # Freitag
    assert not cron_matches("0 23 * * 1-5", datetime(2026, 8, 29, 23, 0))  # Samstag
    # Sonntag ist sowohl 0 als auch 7
    assert cron_matches("0 20 * * 0", datetime(2026, 8, 23, 20, 0))
    assert cron_matches("0 20 * * 7", datetime(2026, 8, 23, 20, 0))
    # Liste
    assert cron_matches("0 8,20 * * *", datetime(2026, 8, 24, 8, 0))
    assert cron_matches("0 8,20 * * *", datetime(2026, 8, 24, 20, 0))
    assert not cron_matches("0 8,20 * * *", datetime(2026, 8, 24, 12, 0))


def test_last_due():
    # Montag 21:15 -> letzte Faelligkeit von "0 20 * * 0-4" war Montag 20:00
    assert last_due("0 20 * * 0-4", datetime(2026, 8, 24, 21, 15)) == datetime(2026, 8, 24, 20, 0)
    # Montag 19:00 -> letzte war Sonntag 20:00
    assert last_due("0 20 * * 0-4", datetime(2026, 8, 24, 19, 0)) == datetime(2026, 8, 23, 20, 0)
    # exakt auf der Minute zaehlt als faellig
    assert last_due("0 20 * * 0-4", datetime(2026, 8, 24, 20, 0)) == datetime(2026, 8, 24, 20, 0)
    # ausserhalb des Rueckblickfensters -> None
    assert last_due("0 20 * * 5", datetime(2026, 8, 25, 12, 0), lookback_h=6) is None


def test_resolve_placeholders():
    # Montag 2026-08-24 -> naechster Handelstag ist Dienstag
    got = resolve_placeholders("raw/journal/Daily Bias {next_trading_day}.md", date(2026, 8, 24))
    assert got == "raw/journal/Daily Bias 2026-08-25.md", got
    assert resolve_placeholders("{today}", date(2026, 8, 24)) == "2026-08-24"
    assert resolve_placeholders("{yesterday}", date(2026, 8, 24)) == "2026-08-23"
    # Freitag 2026-08-28 -> naechster Montag ist 2026-08-31, KW 36
    got = resolve_placeholders("Weekly Bias KW{next_kw} {next_year}.md", date(2026, 8, 28))
    assert got == "Weekly Bias KW36 2026.md", got
    # unbekannte Klammern bleiben unangetastet
    assert resolve_placeholders("{unbekannt}", date(2026, 8, 24)) == "{unbekannt}"


def test_parse_timeout():
    assert parse_timeout("15m") == 900
    assert parse_timeout("60m") == 3600
    assert parse_timeout("2h") == 7200
    assert parse_timeout("90s") == 90
    assert parse_timeout(None) == 1800  # Default 30m


def test_scan_entries():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        cmds = root / ".claude" / "commands"
        cmds.mkdir(parents=True)
        (cmds / "geplant.md").write_text(
            "---\ndescription: mit Plan\nschedule: \"0 20 * * 0-4\"\n"
            "expect: \"out/{today}.md\"\ntimeout: 15m\n---\nText\n",
            encoding="utf-8",
        )
        (cmds / "ungeplant.md").write_text(
            "---\ndescription: ohne Plan\n---\nText\n", encoding="utf-8"
        )
        (cmds / "extern.md").write_text(
            "---\ndescription: extern\nschedule: \"0 7 * * *\"\nextern: true\n"
            "expect: \"out/b-{today}.md\"\n---\nText\n",
            encoding="utf-8",
        )
        skill = root / ".claude" / "skills" / "meiner"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            "---\nname: meiner\nschedule: \"0 9 * * 1\"\n---\nText\n", encoding="utf-8"
        )

        entries = {e.name: e for e in scan_entries(root)}
        # ohne schedule wird ignoriert
        assert "ungeplant" not in entries
        assert set(entries) == {"geplant", "extern", "meiner"}, sorted(entries)
        assert entries["geplant"].timeout_s == 900
        assert entries["geplant"].extern is False
        assert entries["extern"].extern is True
        # Default-Timeout, wenn keiner angegeben ist
        assert entries["extern"].timeout_s == 1800
        assert entries["meiner"].schedule == "0 9 * * 1"


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"ok   {t.__name__}")
    print(f"\n{len(tests)} Tests bestanden.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Test laufen lassen, Fehlschlag bestätigen**

Run: `python tools/test_agent_tick.py`
Expected: FAIL mit `ModuleNotFoundError: No module named 'agent_tick'`

- [ ] **Step 3: Die Implementierung schreiben**

Erstelle `tools/agent_tick.py`:

```python
"""Taktgeber fuer die geplanten Vault-Laeufe.

Liest den Zeitplan aus dem YAML-Frontmatter der Commands und Skills, entscheidet
ohne LLM, was faellig ist, startet die Laeufe und protokolliert sie. Nur bei
rotem Befund wird ein Modell gestartet.

Design: docs/superpowers/specs/2026-08-25-main-agent-wachhund-design.md
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "algo"))
from bias_levels import next_monday, next_trading_day  # noqa: E402

DEFAULT_TIMEOUT_S = 30 * 60


@dataclass
class Entry:
    """Ein geplanter Lauf, gelesen aus dem Frontmatter einer Command-/Skill-Datei."""

    name: str
    schedule: str
    expect: str | None
    timeout_s: int
    extern: bool
    quelle: Path


def parse_timeout(text: str | None) -> int:
    """'15m' -> 900. Ohne Angabe der Default von 30 Minuten."""
    if not text:
        return DEFAULT_TIMEOUT_S
    text = str(text).strip().lower()
    faktor = {"s": 1, "m": 60, "h": 3600}
    if text[-1] in faktor:
        return int(float(text[:-1]) * faktor[text[-1]])
    return int(float(text))  # nackte Zahl = Sekunden


def _feld_passt(feld: str, wert: int, sonntag_auch_7: bool = False) -> bool:
    """Wertet ein einzelnes Cron-Feld aus: *, N, a-b, a,b, */n."""
    for teil in feld.split(","):
        teil = teil.strip()
        schritt = 1
        if "/" in teil:
            teil, s = teil.split("/", 1)
            schritt = int(s)
        if teil == "*":
            if wert % schritt == 0:
                return True
            continue
        if "-" in teil:
            a, b = (int(x) for x in teil.split("-", 1))
            if a <= wert <= b and (wert - a) % schritt == 0:
                return True
            # Sonntag darf als 0 oder 7 geschrieben werden
            if sonntag_auch_7 and wert == 0 and a <= 7 <= b:
                return True
            continue
        n = int(teil)
        if n == wert or (sonntag_auch_7 and wert == 0 and n == 7):
            return True
    return False


def cron_matches(expr: str, when: datetime) -> bool:
    """True, wenn `when` (minutengenau) auf den Cron-Ausdruck passt.

    Unterstuetzt die tatsaechlich benutzte Teilmenge: Minute, Stunde,
    Monatstag, Monat, Wochentag -- je *, N, a-b, a,b, */n. Wochentag 0 und 7
    sind beide Sonntag, wie bei Vixie-Cron.
    """
    felder = expr.split()
    if len(felder) != 5:
        raise ValueError(f"Cron-Ausdruck braucht 5 Felder, hat {len(felder)}: {expr!r}")
    minute, stunde, mtag, monat, wtag = felder
    # Python: Montag=0..Sonntag=6. Cron: Sonntag=0..Samstag=6.
    cron_wtag = (when.weekday() + 1) % 7
    return (
        _feld_passt(minute, when.minute)
        and _feld_passt(stunde, when.hour)
        and _feld_passt(mtag, when.day)
        and _feld_passt(monat, when.month)
        and _feld_passt(wtag, cron_wtag, sonntag_auch_7=True)
    )


def last_due(expr: str, now: datetime, lookback_h: int = 36) -> datetime | None:
    """Letzter Zeitpunkt <= now, zu dem der Ausdruck faellig war.

    Minutenweise rueckwaerts. Bei 36 h sind das 2160 Schritte -- schnell genug,
    und es erspart eine Cron-Bibliothek.
    """
    kandidat = now.replace(second=0, microsecond=0)
    for _ in range(lookback_h * 60 + 1):
        if cron_matches(expr, kandidat):
            return kandidat
        kandidat -= timedelta(minutes=1)
    return None


def resolve_placeholders(text: str, today: date) -> str:
    """Ersetzt {today}, {yesterday}, {next_trading_day}, {next_kw}, {next_year}.

    next_trading_day/next_monday kommen aus algo/bias_levels.py -- dieselbe
    Logik, mit der die Bias-Commands ihre Dateien benennen. Unbekannte
    Klammerausdruecke bleiben stehen.
    """
    mo = next_monday(today)
    werte = {
        "today": today.isoformat(),
        "yesterday": (today - timedelta(days=1)).isoformat(),
        "next_trading_day": next_trading_day(today).isoformat(),
        "next_kw": f"{mo.isocalendar().week:02d}",
        "next_year": str(mo.isocalendar().year),
    }
    for schluessel, wert in werte.items():
        text = text.replace("{" + schluessel + "}", wert)
    return text


def _frontmatter(pfad: Path) -> dict:
    """YAML-Kopf einer Markdown-Datei. Leeres dict, wenn keiner da ist."""
    try:
        inhalt = pfad.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return {}
    if not inhalt.startswith("---"):
        return {}
    teile = inhalt.split("---", 2)
    if len(teile) < 3:
        return {}
    try:
        kopf = yaml.safe_load(teile[1])
    except yaml.YAMLError:
        return {}
    return kopf if isinstance(kopf, dict) else {}


def scan_entries(root: Path) -> list[Entry]:
    """Alle Commands und Skills mit `schedule:` im Kopf. Der Scan IST die Registry."""
    quellen = sorted((root / ".claude" / "commands").glob("*.md"))
    quellen += sorted((root / ".claude" / "skills").glob("*/SKILL.md"))
    entries = []
    for pfad in quellen:
        kopf = _frontmatter(pfad)
        if not kopf.get("schedule"):
            continue
        name = pfad.parent.name if pfad.name == "SKILL.md" else pfad.stem
        entries.append(
            Entry(
                name=name,
                schedule=str(kopf["schedule"]),
                expect=kopf.get("expect"),
                timeout_s=parse_timeout(kopf.get("timeout")),
                extern=bool(kopf.get("extern", False)),
                quelle=pfad,
            )
        )
    return entries
```

- [ ] **Step 4: Test laufen lassen, grün bestätigen**

Run: `python tools/test_agent_tick.py`
Expected: PASS, `5 Tests bestanden.`

Schlägt `test_resolve_placeholders` fehl, prüfe zuerst die Annahme über `next_trading_day` in `algo/bias_levels.py:144` — passe **den Test** an das tatsächliche Verhalten an, nicht die Bibliotheksfunktion. Sie ist die Quelle der Wahrheit, weil die Bias-Commands ihre Dateien damit benennen.

- [ ] **Step 5: Commit**

```bash
git add tools/agent_tick.py tools/test_agent_tick.py
git commit -m "setup | agent_tick: Frontmatter-Scanner, Cron-Matcher, Platzhalter"
```

---

### Task 2: Register, Fälligkeit, `expect` und `--dry-run`

Nach diesem Task ist Rollout-Stufe 1 fertig: `python tools/agent_tick.py --dry-run` zeigt die echte Lage, startet aber nichts.

**Files:**
- Modify: `tools/agent_tick.py`
- Test: `tools/test_agent_tick.py`

**Interfaces:**
- Consumes: `Entry`, `last_due`, `resolve_placeholders` aus Task 1
- Produces:
  - `expect_ok(expect: str | None, root: Path, started: datetime, today: date) -> tuple[bool, str]`
  - `last_run(register: Path, name: str) -> datetime | None`
  - `append_run(register: Path, row: dict) -> None`
  - `faellige(entries: list[Entry], now: datetime, register: Path) -> list[tuple[Entry, str]]` — `str` ist der `ausloeser` (`plan`, `nachhol`, `extern`)
  - Konstante `REGISTER_SPALTEN: list[str]`

- [ ] **Step 1: Die Tests schreiben**

Ergänze in `tools/test_agent_tick.py` — **oberhalb** von `def main():` einfügen und den Import-Block oben um die neuen Namen erweitern:

```python
def test_expect_ok_existenz():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "out").mkdir()
        gestartet = datetime(2026, 8, 24, 20, 0)
        ok, notiz = expect_ok("out/{today}.md", root, gestartet, date(2026, 8, 24))
        assert ok is False, notiz
        assert "2026-08-24" in notiz, notiz  # aufgeloester Pfad steht in der Notiz

        (root / "out" / "2026-08-24.md").write_text("da", encoding="utf-8")
        ok, notiz = expect_ok("out/{today}.md", root, gestartet, date(2026, 8, 24))
        assert ok is True, notiz


def test_expect_ok_changed():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        ziel = root / "daten.csv"
        ziel.write_text("alt", encoding="utf-8")
        import os
        # mtime kuenstlich in die Vergangenheit setzen
        alt = datetime(2026, 8, 24, 10, 0).timestamp()
        os.utime(ziel, (alt, alt))

        gestartet = datetime(2026, 8, 24, 20, 0)
        ok, notiz = expect_ok("changed: daten.csv", root, gestartet, date(2026, 8, 24))
        assert ok is False, notiz
        assert "unveraendert" in notiz.lower() or "unverändert" in notiz.lower(), notiz

        neu = datetime(2026, 8, 24, 20, 5).timestamp()
        os.utime(ziel, (neu, neu))
        ok, notiz = expect_ok("changed: daten.csv", root, gestartet, date(2026, 8, 24))
        assert ok is True, notiz

        # fehlende Datei ist rot, kein Absturz
        ok, notiz = expect_ok("changed: gibtsnicht.csv", root, gestartet, date(2026, 8, 24))
        assert ok is False, notiz


def test_expect_ok_ohne_angabe():
    with tempfile.TemporaryDirectory() as td:
        ok, notiz = expect_ok(None, Path(td), datetime(2026, 8, 24, 20, 0), date(2026, 8, 24))
        assert ok is True, notiz


def test_register_lesen_schreiben():
    with tempfile.TemporaryDirectory() as td:
        reg = Path(td) / "agent-runs.csv"
        assert last_run(reg, "irgendwas") is None  # Datei existiert noch nicht

        append_run(reg, {
            "zeit_start": "2026-08-24T20:00", "command": "bias-vorlage-daily",
            "ausloeser": "plan", "dauer_s": "86", "exit": "0",
            "expect_ok": "1", "status": "gruen", "notiz": "",
        })
        append_run(reg, {
            "zeit_start": "2026-08-25T20:00", "command": "bias-vorlage-daily",
            "ausloeser": "plan", "dauer_s": "91", "exit": "0",
            "expect_ok": "1", "status": "gruen", "notiz": "",
        })
        append_run(reg, {
            "zeit_start": "2026-08-25T23:00", "command": "daten-1s",
            "ausloeser": "plan", "dauer_s": "912", "exit": "0",
            "expect_ok": "0", "status": "rot", "notiz": "expect verfehlt, Komma, Zeichen",
        })
        # juengster Lauf gewinnt
        assert last_run(reg, "bias-vorlage-daily") == datetime(2026, 8, 25, 20, 0)
        assert last_run(reg, "daten-1s") == datetime(2026, 8, 25, 23, 0)
        assert last_run(reg, "unbekannt") is None
        # Kopfzeile genau einmal
        assert reg.read_text(encoding="utf-8").count("zeit_start") == 1
        # Komma in der Notiz zerlegt die Zeile nicht
        assert last_run(reg, "daten-1s") is not None


def test_faellige():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        reg = root / "agent-runs.csv"
        e = Entry("bias", "0 20 * * 0-4", None, 900, False, root / "bias.md")
        ex = Entry("brief", "0 7 * * *", "out/x.md", 3600, True, root / "brief.md")

        # Montag 20:05, noch nie gelaufen -> faellig als "plan"
        got = faellige([e], datetime(2026, 8, 24, 20, 5), reg)
        assert [(x.name, a) for x, a in got] == [("bias", "plan")], got

        # nach dem Lauf nicht mehr faellig
        append_run(reg, {
            "zeit_start": "2026-08-24T20:05", "command": "bias", "ausloeser": "plan",
            "dauer_s": "10", "exit": "0", "expect_ok": "1", "status": "gruen", "notiz": "",
        })
        assert faellige([e], datetime(2026, 8, 24, 20, 15), reg) == []

        # Dienstag 20:05: neue Faelligkeit nach dem letzten Lauf -> wieder dran
        got = faellige([e], datetime(2026, 8, 25, 20, 5), reg)
        assert [(x.name, a) for x, a in got] == [("bias", "plan")], got

        # deutlich verspaetet (Rechner war aus) -> "nachhol"
        got = faellige([e], datetime(2026, 8, 25, 23, 30), reg)
        assert [(x.name, a) for x, a in got] == [("bias", "nachhol")], got

        # extern wird nie gestartet, aber als "extern" gemeldet
        got = faellige([ex], datetime(2026, 8, 25, 8, 0), reg)
        assert [(x.name, a) for x, a in got] == [("brief", "extern")], got

        # vor der ersten Faelligkeit des Tages: nichts zu tun
        assert faellige([ex], datetime(2026, 8, 25, 6, 0), reg) == []
```

Erweitere den Import-Block am Dateianfang:

```python
from agent_tick import (
    Entry, append_run, cron_matches, expect_ok, faellige, last_due, last_run,
    parse_timeout, resolve_placeholders, scan_entries,
)
```

- [ ] **Step 2: Tests laufen lassen, Fehlschlag bestätigen**

Run: `python tools/test_agent_tick.py`
Expected: FAIL mit `ImportError: cannot import name 'expect_ok' from 'agent_tick'`

- [ ] **Step 3: Die Implementierung schreiben**

Ergänze in `tools/agent_tick.py` (unterhalb von `scan_entries`):

```python
import argparse
import csv

REGISTER_SPALTEN = [
    "zeit_start", "command", "ausloeser", "dauer_s", "exit",
    "expect_ok", "status", "notiz",
]
# Ab dieser Verspaetung gilt ein Lauf als verpasst statt planmaessig.
NACHHOL_SCHWELLE = timedelta(hours=1)


def expect_ok(
    expect: str | None, root: Path, started: datetime, today: date
) -> tuple[bool, str]:
    """Prueft das Erfolgskriterium. Rueckgabe: (erfuellt, Notiz fuers Register).

    Zwei Formen -- 'pfad/datei.md' (existiert danach) und
    'changed: pfad/datei.csv' (ist seit Laufbeginn juenger geworden).
    Ohne Angabe zaehlen nur Exit-Code und Laufzeit.
    """
    if not expect:
        return True, ""
    text = resolve_placeholders(str(expect).strip(), today)
    if text.startswith("changed:"):
        ziel = root / text.split(":", 1)[1].strip()
        if not ziel.exists():
            return False, f"expect verfehlt: {ziel.name} fehlt"
        if datetime.fromtimestamp(ziel.stat().st_mtime) < started:
            return False, f"expect verfehlt: {ziel.name} unveraendert"
        return True, ""
    ziel = root / text
    if not ziel.exists():
        return False, f"expect verfehlt: {text} fehlt"
    return True, ""


def last_run(register: Path, name: str) -> datetime | None:
    """Startzeit des juengsten protokollierten Laufs dieses Eintrags."""
    if not register.exists():
        return None
    juengster = None
    with register.open(encoding="utf-8", newline="") as f:
        for zeile in csv.DictReader(f):
            if zeile.get("command") != name:
                continue
            try:
                wann = datetime.fromisoformat(zeile["zeit_start"])
            except (ValueError, KeyError, TypeError):
                continue
            if juengster is None or wann > juengster:
                juengster = wann
    return juengster


def append_run(register: Path, row: dict) -> None:
    """Haengt eine Zeile ans Register. Legt Datei samt Kopfzeile bei Bedarf an."""
    register.parent.mkdir(parents=True, exist_ok=True)
    neu = not register.exists()
    with register.open("a", encoding="utf-8", newline="") as f:
        schreiber = csv.DictWriter(f, fieldnames=REGISTER_SPALTEN)
        if neu:
            schreiber.writeheader()
        schreiber.writerow({s: row.get(s, "") for s in REGISTER_SPALTEN})


def faellige(
    entries: list[Entry], now: datetime, register: Path
) -> list[tuple[Entry, str]]:
    """Was ist jetzt dran? Liefert (Eintrag, ausloeser)-Paare.

    Faellig ist ein Eintrag, wenn seine letzte planmaessige Faelligkeit nach
    seinem letzten protokollierten Lauf liegt. `extern` wird nie gestartet,
    aber zur Pruefung gemeldet.
    """
    dran = []
    for e in entries:
        faellig_um = last_due(e.schedule, now)
        if faellig_um is None:
            continue
        zuletzt = last_run(register, e.name)
        if zuletzt is not None and zuletzt >= faellig_um:
            continue
        if e.extern:
            dran.append((e, "extern"))
        elif now - faellig_um > NACHHOL_SCHWELLE:
            dran.append((e, "nachhol"))
        else:
            dran.append((e, "plan"))
    return dran
```

Und ans Dateiende:

```python
def cli(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Taktgeber fuer die geplanten Vault-Laeufe.")
    p.add_argument("--dry-run", action="store_true",
                   help="nur zeigen, was faellig waere -- nichts starten")
    p.add_argument("--selftest", action="store_true", help="Selbstcheck ausfuehren")
    args = p.parse_args(argv)

    if args.selftest:
        import subprocess
        return subprocess.call([sys.executable, str(Path(__file__).parent / "test_agent_tick.py")])

    now = datetime.now().replace(second=0, microsecond=0)
    register = ROOT / "algo" / "live" / "agent-runs.csv"
    entries = scan_entries(ROOT)
    dran = faellige(entries, now, register)

    if args.dry_run:
        print(f"Stand {now:%Y-%m-%d %H:%M} -- {len(entries)} geplante Eintraege\n")
        for e in entries:
            ok, notiz = expect_ok(e.expect, ROOT, now, now.date())
            aufgeloest = resolve_placeholders(str(e.expect), now.date()) if e.expect else "-"
            marke = next((a for x, a in dran if x.name == e.name), "-")
            print(f"  {e.name:24} {e.schedule:16} faellig={marke:8} "
                  f"expect={'ok' if ok else 'ROT'}  {aufgeloest}")
            if not ok and notiz:
                print(f"  {'':24} -> {notiz}")
        return 0

    print("Ausfuehrung folgt in Task 4.")
    return 0


if __name__ == "__main__":
    sys.exit(cli())
```

- [ ] **Step 4: Tests laufen lassen, grün bestätigen**

Run: `python tools/test_agent_tick.py`
Expected: PASS, `10 Tests bestanden.`

- [ ] **Step 5: Trockenlauf gegen das echte Repo**

Run: `python tools/agent_tick.py --dry-run`
Expected: `Stand … -- 0 geplante Eintraege` — noch hat kein Command einen `schedule:`-Kopf. Kein Absturz, keine Ausgabe von Einträgen. Genau das ist der Beweis, dass der Vertrag additiv ist.

- [ ] **Step 6: Commit**

```bash
git add tools/agent_tick.py tools/test_agent_tick.py
git commit -m "setup | agent_tick: Register, Faelligkeit, expect-Pruefung, --dry-run"
```

---

### Task 3: Frontmatter-Köpfe setzen und Briefing-Einträge anlegen

Nach diesem Task zeigt `--dry-run` die echte Lage der vier geplanten Einträge plus der beiden Cowork-Briefings.

**Files:**
- Modify: `.claude/commands/bias-vorlage-daily.md` (Frontmatter, Zeilen 1–4)
- Modify: `.claude/commands/bias-vorlage-weekly.md` (Frontmatter)
- Modify: `.claude/commands/daten-1s.md` (Frontmatter)
- Modify: `.claude/commands/update.md` (Frontmatter)
- Create: `.claude/commands/briefing-morgens.md`
- Create: `.claude/commands/briefing-abends.md`
- Modify: `.gitignore` (nur falls nötig, siehe Step 1)

- [ ] **Step 1: Register vom Auto-Push ausnehmen**

Run: `git check-ignore -v algo/live/agent-runs.csv; echo "exit=$?"`

Meldet das `exit=1` (also *nicht* ignoriert), ergänze in `.gitignore`:

```
# Lauf-Register des Taktgebers -- transient, wie algo/live/*/
algo/live/agent-runs.csv
algo/live/agent-status.md
```

Ohne das löst jeder einzelne Tick über den Stop-Hook einen Commit und Push aus.

- [ ] **Step 2: Köpfe der vier geplanten Commands ergänzen**

Jeweils **nur** die neuen Zeilen in den bestehenden Frontmatter-Block einfügen, `description` unverändert lassen.

`.claude/commands/bias-vorlage-daily.md`:
```yaml
schedule: "0 20 * * 0-4"
expect: "raw/journal/Daily Bias {next_trading_day}.md"
timeout: 15m
```

`.claude/commands/bias-vorlage-weekly.md`:
```yaml
schedule: "0 20 * * 5"
expect: "raw/journal/Weekly Bias KW{next_kw} {next_year}.md"
timeout: 15m
```

`.claude/commands/daten-1s.md`:
```yaml
schedule: "0 23 * * 1-5"
expect: "changed: raw/marktdaten/1s-abdeckung.csv"
timeout: 90m
```

`.claude/commands/update.md`:
```yaml
schedule: "30 6 * * *"
timeout: 10m
```

`/update` bekommt bewusst kein `expect` — ein Pull ohne neue Commits ist erfolgreich und ändert nichts. Der Exit-Code trägt hier.

`/daten-1s` bekommt 90 min statt der 15 min der Bias-Commands: der Lauf startet bei Bedarf das IB-Gateway kalt und holt einen ganzen Handelstag in 1s-Auflösung.

- [ ] **Step 3: Die beiden Briefing-Einträge anlegen**

`.claude/commands/briefing-morgens.md`:
```markdown
---
description: Cowork-Morgenbriefing -- geplant in Claude Desktop, laeuft lokal in diesem Ordner
schedule: "0 7 * * *"
expect: "algo/live/briefing-{today}-morgens.md"
timeout: 60m
extern: true
---

Dieser Eintrag wird vom Taktgeber **nur beobachtet, nie gestartet** (`extern: true`).

Geplant ist er in Claude Desktop unter "Chat und Cowork" -> "Geplant" -> "Daily briefing",
Ordner `C:\Users\janne\OneDrive\Desktop\Ablage 1\VS Folder 1`. Coworks Planer ist von
aussen nicht ansteuerbar; `tools/agent_tick.py` prueft daher nur, ob das Briefing seine
Datei geschrieben hat, und meldet einen Ausfall.

Damit das funktioniert, muss die Cowork-Anweisung diese beiden Saetze enthalten:

1. "Schreibe das fertige Briefing zusaetzlich nach
   `algo/live/briefing-<YYYY-MM-DD>-morgens.md`."
2. "Lies zu Beginn `algo/live/agent-status.md` und uebernimm offene Punkte daraus in
   einen Abschnitt 'Vault & Algo'."

Das `timeout: 60m` ist hier ein Kulanzfenster: erst eine Stunde nach der geplanten Zeit
gilt das Briefing als ausgeblieben.
```

`.claude/commands/briefing-abends.md`:
```markdown
---
description: Cowork-Abendbriefing -- geplant in Claude Desktop, laeuft lokal in diesem Ordner
schedule: "0 20 * * *"
expect: "algo/live/briefing-{today}-abends.md"
timeout: 60m
extern: true
---

Dieser Eintrag wird vom Taktgeber **nur beobachtet, nie gestartet** (`extern: true`).

Geplant ist er in Claude Desktop unter "Chat und Cowork" -> "Geplant" -> "Abend briefing",
Ordner `C:\Users\janne\OneDrive\Desktop\Ablage 1\VS Folder 1`. Coworks Planer ist von
aussen nicht ansteuerbar; `tools/agent_tick.py` prueft daher nur, ob das Briefing seine
Datei geschrieben hat, und meldet einen Ausfall.

Damit das funktioniert, muss die Cowork-Anweisung diese beiden Saetze enthalten:

1. "Schreibe das fertige Briefing zusaetzlich nach
   `algo/live/briefing-<YYYY-MM-DD>-abends.md`."
2. "Lies zu Beginn `algo/live/agent-status.md` und uebernimm offene Punkte daraus in
   einen Abschnitt 'Vault & Algo'."

Das `timeout: 60m` ist hier ein Kulanzfenster: erst eine Stunde nach der geplanten Zeit
gilt das Briefing als ausgeblieben.
```

Achtung bei der Zeitkollision: `briefing-abends` und `bias-vorlage-daily` stehen beide auf
20:00. Das ist unkritisch — der Bias-Command wird gestartet, das Briefing nur geprueft,
und dessen 60-Minuten-Kulanzfenster laeuft ohnehin laenger.

- [ ] **Step 4: Trockenlauf prüfen**

Run: `python tools/agent_tick.py --dry-run`
Expected: Sechs Einträge (`bias-vorlage-daily`, `bias-vorlage-weekly`, `daten-1s`, `update`, `briefing-morgens`, `briefing-abends`). `algo-live-status` und `tagesbericht` tauchen **nicht** auf. Die aufgelösten `expect`-Pfade müssen sinnvoll aussehen — insbesondere muss `raw/journal/Daily Bias <morgen>.md` den Namen tragen, den `/bias-vorlage-daily` tatsächlich erzeugt. Vergleiche gegen `ls raw/journal/`.

Stimmt ein Pfad nicht, korrigiere den `expect`-Eintrag, nicht das Skript.

- [ ] **Step 5: Commit**

```bash
git add .claude/commands/ .gitignore
git commit -m "setup | schedule/expect-Koepfe fuer die geplanten Laeufe, Cowork-Briefings als externe Eintraege"
```

---

### Task 4: Ausführung — starten, messen, protokollieren, Status schreiben

Rollout-Stufe 2. Läufe werden gestartet und protokolliert; rote Befunde landen nur im Register, es wird noch kein Wachhund gerufen.

**Files:**
- Modify: `tools/agent_tick.py`
- Test: `tools/test_agent_tick.py`

**Interfaces:**
- Consumes: alles aus Task 1 und 2
- Produces:
  - `run_entry(entry: Entry, ausloeser: str, root: Path, now: datetime, starter=None) -> dict` — Rückgabe ist eine fertige Registerzeile. `starter` ist eine Einschleusstelle für den Test: eine Funktion `(list[str], int) -> tuple[int, str]`, die `(exit_code, ausgabe)` liefert. Ohne Angabe wird `subprocess` benutzt.
  - `write_status(root: Path, entries: list[Entry], now: datetime) -> str`

- [ ] **Step 1: Die Tests schreiben**

Ergänze in `tools/test_agent_tick.py` (oberhalb `def main():`, Import-Block erweitern):

```python
def test_run_entry_gruen():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "out").mkdir()
        e = Entry("demo", "0 20 * * *", "out/{today}.md", 900, False, root / "demo.md")

        def starter(cmd, timeout_s):
            (root / "out" / "2026-08-24.md").write_text("erzeugt", encoding="utf-8")
            return 0, "fertig"

        zeile = run_entry(e, "plan", root, datetime(2026, 8, 24, 20, 0), starter=starter)
        assert zeile["status"] == "gruen", zeile
        assert zeile["exit"] == "0"
        assert zeile["expect_ok"] == "1"
        assert zeile["command"] == "demo"
        assert zeile["ausloeser"] == "plan"


def test_run_entry_expect_verfehlt():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        e = Entry("demo", "0 20 * * *", "out/{today}.md", 900, False, root / "demo.md")
        # Lauf meldet Erfolg, erzeugt aber nichts -- genau der Fall, den expect faengt
        zeile = run_entry(e, "plan", root, datetime(2026, 8, 24, 20, 0),
                          starter=lambda cmd, t: (0, "angeblich fertig"))
        assert zeile["status"] == "rot", zeile
        assert zeile["exit"] == "0"
        assert zeile["expect_ok"] == "0"
        assert "expect verfehlt" in zeile["notiz"], zeile


def test_run_entry_wiederholt_bei_fehler():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        e = Entry("demo", "0 20 * * *", None, 900, False, root / "demo.md")
        versuche = []

        def starter(cmd, timeout_s):
            versuche.append(cmd)
            return (1, "peng") if len(versuche) < 3 else (0, "endlich")

        zeile = run_entry(e, "plan", root, datetime(2026, 8, 24, 20, 0), starter=starter)
        assert len(versuche) == 3, versuche          # Erstversuch + 2 Wiederholungen
        assert zeile["status"] == "gruen", zeile


def test_run_entry_gibt_nach_zwei_wiederholungen_auf():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        e = Entry("demo", "0 20 * * *", None, 900, False, root / "demo.md")
        versuche = []

        def starter(cmd, timeout_s):
            versuche.append(cmd)
            return 1, "peng"

        zeile = run_entry(e, "plan", root, datetime(2026, 8, 24, 20, 0), starter=starter)
        assert len(versuche) == 3, versuche
        assert zeile["status"] == "rot", zeile
        assert zeile["exit"] == "1"


def test_run_entry_timeout():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        e = Entry("demo", "0 20 * * *", None, 900, False, root / "demo.md")
        # 124 ist der Code, den _subprocess_starter bei TimeoutExpired liefert
        zeile = run_entry(e, "plan", root, datetime(2026, 8, 24, 20, 0),
                          starter=lambda cmd, t: (124, ""))
        assert zeile["status"] == "rot", zeile
        assert zeile["exit"] == "124"
        assert "Timeout" in zeile["notiz"], zeile
        assert "900" in zeile["notiz"], zeile


def test_run_entry_extern_startet_nichts():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        e = Entry("brief", "0 7 * * *", "out/b.md", 3600, True, root / "brief.md")
        versuche = []

        def starter(cmd, timeout_s):
            versuche.append(cmd)
            return 0, ""

        zeile = run_entry(e, "extern", root, datetime(2026, 8, 24, 8, 0), starter=starter)
        assert versuche == [], "externer Eintrag darf nie gestartet werden"
        assert zeile["status"] == "rot", zeile
        assert zeile["dauer_s"] == ""
        assert "ausgeblieben" in zeile["notiz"], zeile


def test_write_status():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "algo" / "live").mkdir(parents=True)
        e = Entry("demo", "0 20 * * *", "out/fehlt.md", 900, False, root / "demo.md")
        text = write_status(root, [e], datetime(2026, 8, 24, 21, 0))
        ziel = root / "algo" / "live" / "agent-status.md"
        assert ziel.exists()
        assert "demo" in text
        assert "2026-08-24" in text
```

- [ ] **Step 2: Tests laufen lassen, Fehlschlag bestätigen**

Run: `python tools/test_agent_tick.py`
Expected: FAIL mit `ImportError: cannot import name 'run_entry' from 'agent_tick'`

- [ ] **Step 3: Die Implementierung schreiben**

Ergänze in `tools/agent_tick.py`:

```python
import subprocess

WIEDERHOLUNGEN = 2  # zusaetzlich zum Erstversuch


def _subprocess_starter(cmd: list[str], timeout_s: int) -> tuple[int, str]:
    """Startet einen Lauf wirklich. Rueckgabe (exit_code, letzte Ausgabezeilen)."""
    try:
        p = subprocess.run(
            cmd, cwd=ROOT, timeout=timeout_s, capture_output=True,
            text=True, encoding="utf-8", errors="replace",
        )
        ausgabe = (p.stdout or "") + (p.stderr or "")
        return p.returncode, ausgabe[-4000:]
    except subprocess.TimeoutExpired:
        return 124, f"Timeout nach {timeout_s}s -- Prozess beendet"


def run_entry(
    entry: Entry, ausloeser: str, root: Path, now: datetime, starter=None
) -> dict:
    """Fuehrt einen faelligen Eintrag aus und liefert die fertige Registerzeile.

    `extern` wird nie gestartet -- dort wird nur geprueft, ob das erwartete
    Ergebnis eingetroffen ist. Bei Exit != 0 wird bis zu WIEDERHOLUNGEN mal
    neu versucht; `expect` entscheidet danach ueber gruen/rot.
    """
    starter = starter or _subprocess_starter
    basis = {
        "zeit_start": now.isoformat(timespec="minutes"),
        "command": entry.name,
        "ausloeser": ausloeser,
    }

    if entry.extern:
        ok, notiz = expect_ok(entry.expect, root, now, now.date())
        return {**basis, "dauer_s": "", "exit": "", "expect_ok": "1" if ok else "0",
                "status": "gruen" if ok else "rot",
                "notiz": "" if ok else "ausgeblieben (extern geplant, nicht eingetroffen)"}

    cmd = ["claude", "-p", f"/{entry.name}"]
    begonnen = datetime.now()
    code, ausgabe = -1, ""
    for versuch in range(WIEDERHOLUNGEN + 1):
        code, ausgabe = starter(cmd, entry.timeout_s)
        if code == 0:
            break
    dauer = int((datetime.now() - begonnen).total_seconds())

    ok, notiz = expect_ok(entry.expect, root, begonnen, now.date())
    if code == 124:  # muss VOR dem allgemeinen Fehlerzweig stehen
        notiz = f"Timeout nach {entry.timeout_s}s -- Prozess beendet"
    elif code != 0:
        notiz = f"exit {code} nach {WIEDERHOLUNGEN + 1} Versuchen: {ausgabe.strip()[-300:]}"
    return {**basis, "dauer_s": str(dauer), "exit": str(code),
            "expect_ok": "1" if ok else "0",
            "status": "gruen" if (code == 0 and ok) else "rot", "notiz": notiz}


def write_status(root: Path, entries: list[Entry], now: datetime) -> str:
    """Schreibt algo/live/agent-status.md -- bei JEDEM Tick, auch bei gruener Nacht.

    Sonst liest das Cowork-Morgenbriefing nach einer stoerungsfreien Nacht einen
    Stand von vorgestern. Der Wachhund haengt seinen Diagnoseteil spaeter an.
    """
    register = root / "algo" / "live" / "agent-runs.csv"
    zeilen = [f"# Agent-Status — Stand {now:%Y-%m-%d %H:%M}", ""]
    zeilen.append("| Eintrag | letzter Lauf | expect | Status |")
    zeilen.append("|---|---|---|---|")
    for e in entries:
        zuletzt = last_run(register, e.name)
        wann = f"{zuletzt:%Y-%m-%d %H:%M}" if zuletzt else "nie"
        ok, notiz = expect_ok(e.expect, root, now, now.date())
        marke = "ok" if ok else "ROT"
        zeilen.append(f"| `{e.name}` | {wann} | {marke} | {notiz or 'in Ordnung'} |")
    text = "\n".join(zeilen) + "\n"
    ziel = root / "algo" / "live" / "agent-status.md"
    ziel.parent.mkdir(parents=True, exist_ok=True)
    ziel.write_text(text, encoding="utf-8")
    return text
```

Ersetze in `cli()` die Zeile `print("Ausfuehrung folgt in Task 4.")` durch:

```python
    register.parent.mkdir(parents=True, exist_ok=True)
    for e, ausloeser in dran:
        zeile = run_entry(e, ausloeser, ROOT, now)
        append_run(register, zeile)
        print(f"{zeile['status']:6} {e.name} ({ausloeser}) {zeile['notiz']}")
    write_status(ROOT, entries, now)
    return 0
```

- [ ] **Step 4: Tests laufen lassen, grün bestätigen**

Run: `python tools/test_agent_tick.py`
Expected: PASS, `17 Tests bestanden.`

- [ ] **Step 5: Einen echten Lauf erzwingen und beobachten**

Run: `python tools/agent_tick.py`
Expected: Startet, was gerade fällig ist. Ist nichts fällig, erscheint nur die Status-Ausgabe. Prüfe danach:

```bash
cat algo/live/agent-runs.csv
cat algo/live/agent-status.md
```

Das Register muss die Kopfzeile plus etwaige Laufzeilen enthalten, `agent-status.md` eine Tabelle mit allen sechs Einträgen.

- [ ] **Step 6: Windows-Aufgabenplaner einrichten**

Ausführen in einer **PowerShell mit Administratorrechten**:

```powershell
$py = (Get-Command python).Source
schtasks /create /tn "Gedanken Agent-Tick" /tr "`"$py`" `"C:\Users\janne\OneDrive\Desktop\Ablage 1\VS Folder 1\tools\agent_tick.py`"" /sc minute /mo 10 /f
schtasks /query /tn "Gedanken Agent-Tick" /fo LIST
```

Expected: `Status: Bereit`, `Nächste Ausführungszeit` innerhalb der nächsten 10 Minuten.

Zum Abschalten während der Beobachtungsphase: `schtasks /change /tn "Gedanken Agent-Tick" /disable`.

- [ ] **Step 7: Commit**

```bash
git add tools/agent_tick.py tools/test_agent_tick.py
git commit -m "setup | agent_tick: Laeufe starten, Laufzeit messen, Register und Status schreiben"
```

---

### Task 5: `/wachhund` — Diagnose, Backfill, Report (noch ohne Autofix)

Rollout-Stufe 3. Bei rotem Befund wird ein Modell gerufen, das diagnostiziert und Datenlücken schließt — aber noch keinen Code ändert.

**Files:**
- Create: `.claude/commands/wachhund.md`
- Modify: `tools/agent_tick.py` (Eskalation in `cli()`)

**Interfaces:**
- Consumes: `run_entry`, `append_run`, `write_status` aus Task 4
- Produces: `eskaliere(befunde: list[dict], root: Path, starter=None) -> int` — ruft `claude -p "/wachhund <json>"` mit den roten Registerzeilen

- [ ] **Step 1: Den Command schreiben**

Erstelle `.claude/commands/wachhund.md`:

```markdown
---
description: Diagnostiziert und repariert fehlgeschlagene geplante Laeufe -- wird von tools/agent_tick.py gerufen, nicht von Hand
---

Du wirst von `tools/agent_tick.py` gerufen, weil mindestens ein geplanter Lauf rot ist.
In `$ARGUMENTS` steht ein JSON-Array der roten Registerzeilen, je mit `command`,
`ausloeser`, `dauer_s`, `exit`, `expect_ok` und `notiz`.

Design: `docs/superpowers/specs/2026-08-25-main-agent-wachhund-design.md`

Arbeite jeden Befund einzeln ab:

1. **Verstehen.** Lies `algo/live/agent-runs.csv` (die letzten Zeilen dieses Commands --
   ist das ein Einzelfall oder das dritte Mal diese Woche?) und das Frontmatter des
   betroffenen Commands unter `.claude/commands/`, um zu sehen, was `expect` eigentlich
   erwartet hat.

2. **Einordnen.** Genau eine der vier Ursachen:
   - **Datenluecke**: `raw/marktdaten/1s-abdeckung.csv` hat Tage ohne Eintrag. Handle:
     `/daten-1s backfill <von> <bis>` fuer genau die fehlenden Tage. Das ist die einzige
     Reparatur, die du in dieser Ausbaustufe selbst ausfuehrst.
   - **Externer Lauf ausgeblieben** (Cowork-Briefing): Du kannst Coworks Planer nicht
     starten. Nur berichten -- mit dem Hinweis, in Claude Desktop nachzusehen, ob der
     Eintrag noch aktiv ist und ob doppelte Eintraege denselben Zweck belegen.
   - **Merge-Konflikt** (typisch bei `/update`): **Nicht aufloesen.** `/update` schreibt
     ausdruecklich vor, die betroffenen Dateien zu nennen und auf Anweisung zu warten.
     Nur berichten.
   - **Crash oder Timeout im Code**: Traceback aus der Notiz lesen, Ursache benennen,
     Datei und Zeile nennen. **In dieser Ausbaustufe nur diagnostizieren, nichts aendern.**

3. **Berichten.** Haenge an `algo/live/agent-status.md` einen Abschnitt an -- die Datei
   existiert bereits, der Taktgeber hat sie zu Beginn geschrieben. Ueberschreibe sie nicht:

       ## Wachhund <HH:MM>

       ### <command> — <Ursache in drei Worten>
       **Was passiert ist:** ein bis zwei Saetze.
       **Was ich getan habe:** oder: nichts, und warum.
       **Was du tun musst:** konkret, oder "nichts".

   Auf Deutsch, knapp. Dieser Abschnitt wird morgens vom Cowork-Briefing vorgelesen --
   schreib ihn so, dass er beim Zuhoeren verstaendlich ist.

**Grenzen, die in jeder Ausbaustufe gelten:**

- Schreibe **nie** nach `raw/`. Der Inhalt ist laut `CLAUDE.md` unveraenderlich; die
  Marktdaten sind "wie Gold" zu behandeln. Ein Backfill ueber `/daten-1s` ist erlaubt --
  der legt neue Tagesdateien an und ueberschreibt keine bestehenden.
- Fasse **nie** `algo/.secrets.yaml` oder `journal/.secrets.yaml` an.
- Fasse **nie** den IBKR-Order-Pfad an. Die harte Sperre fuer Live-Handel gilt unveraendert.
- Loese **nie** Merge-Konflikte auf.
- Rufe **nie** `push.ps1` selbst auf -- der Stop-Hook erledigt das.
```

- [ ] **Step 2: Den Eskalationstest schreiben**

Ergänze in `tools/test_agent_tick.py`:

```python
def test_eskaliere_nur_bei_rot():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        gerufen = []

        def starter(cmd, timeout_s):
            gerufen.append(cmd)
            return 0, ""

        # nur gruene Zeilen -> kein Modellstart
        assert eskaliere([{"command": "a", "status": "gruen", "notiz": ""}], root,
                         starter=starter) == 0
        assert gerufen == [], "gruener Tick darf kein Modell starten"

        # eine rote Zeile -> genau ein Aufruf, Befund als JSON im Argument
        eskaliere([{"command": "daten-1s", "status": "rot", "notiz": "expect verfehlt"}],
                  root, starter=starter)
        assert len(gerufen) == 1, gerufen
        assert gerufen[0][0] == "claude"
        assert "/wachhund" in gerufen[0][-1]
        assert "daten-1s" in gerufen[0][-1]
```

Import-Block um `eskaliere` erweitern.

- [ ] **Step 3: Test laufen lassen, Fehlschlag bestätigen**

Run: `python tools/test_agent_tick.py`
Expected: FAIL mit `ImportError: cannot import name 'eskaliere'`

- [ ] **Step 4: Die Eskalation implementieren**

Ergänze in `tools/agent_tick.py`:

```python
import json

WACHHUND_TIMEOUT_S = 30 * 60


def eskaliere(befunde: list[dict], root: Path, starter=None) -> int:
    """Ruft /wachhund, wenn mindestens ein Befund rot ist. Sonst null Tokens."""
    rot = [b for b in befunde if b.get("status") == "rot"]
    if not rot:
        return 0
    starter = starter or _subprocess_starter
    argument = json.dumps(rot, ensure_ascii=False)
    code, _ = starter(["claude", "-p", f"/wachhund {argument}"], WACHHUND_TIMEOUT_S)
    return code
```

Ergänze in `cli()` **nach** `write_status(...)`, vor `return 0`:

```python
    if [z for z in zeilen_dieses_ticks if z["status"] == "rot"]:
        eskaliere(zeilen_dieses_ticks, ROOT)
```

Dafür in der Schleife die Zeilen sammeln: `zeilen_dieses_ticks = []` vor der Schleife, `zeilen_dieses_ticks.append(zeile)` darin.

**Wichtig zur Reihenfolge:** `write_status` läuft **vor** der Eskalation. Der Wachhund hängt seinen Abschnitt an eine Datei an, die schon existiert — schriebe er zuerst, überschriebe ihn der Taktgeber.

- [ ] **Step 5: Tests laufen lassen, grün bestätigen**

Run: `python tools/test_agent_tick.py`
Expected: PASS, `18 Tests bestanden.`

- [ ] **Step 6: Die Eskalation einmal echt auslösen**

Erzeuge einen künstlich roten Befund, um den Wachhund einmal wirklich laufen zu sehen — ohne auf eine echte Panne zu warten:

```bash
python -c "import sys; sys.path.insert(0,'tools'); from pathlib import Path; import agent_tick as a; a.eskaliere([{'command':'daten-1s','status':'rot','ausloeser':'plan','exit':'0','expect_ok':'0','notiz':'TESTLAUF: kuenstlich roter Befund, keine echte Panne'}], a.ROOT)"
```

Expected: Der Wachhund läuft, liest das Register, stellt fest, dass `1s-abdeckung.csv` in Ordnung ist, und hängt einen Abschnitt an `algo/live/agent-status.md` an, der das sagt. Prüfe mit `cat algo/live/agent-status.md`, dass der Taktgeber-Teil **erhalten** geblieben ist.

- [ ] **Step 7: Commit**

```bash
git add .claude/commands/wachhund.md tools/agent_tick.py tools/test_agent_tick.py
git commit -m "setup | Wachhund: Diagnose, Backfill bei Datenluecken, Report an agent-status.md"
```

---

### Task 6: Autofix mit den vier Sicherungen

Rollout-Stufe 4. Der Wachhund darf jetzt Code reparieren — auf einem Branch, mit Verifikationspflicht, Sperrliste und Versuchsgrenze.

**Files:**
- Modify: `.claude/commands/wachhund.md` (Punkt 2 der Einordnung, neuer Abschnitt)
- Modify: `tools/agent_tick.py` (Versuchszähler)
- Test: `tools/test_agent_tick.py`

**Interfaces:**
- Consumes: `last_run`, `REGISTER_SPALTEN` aus Task 2
- Produces: `autofix_erlaubt(register: Path, name: str, now: datetime) -> bool` — falsch, wenn für diesen Command in den letzten 24 h schon ein Autofix protokolliert wurde

- [ ] **Step 1: Den Test für die Versuchsgrenze schreiben**

Ergänze in `tools/test_agent_tick.py`:

```python
def test_autofix_nur_einmal_pro_nacht():
    with tempfile.TemporaryDirectory() as td:
        reg = Path(td) / "agent-runs.csv"
        jetzt = datetime(2026, 8, 25, 23, 30)
        assert autofix_erlaubt(reg, "daten-1s", jetzt) is True  # noch nie

        append_run(reg, {
            "zeit_start": "2026-08-25T20:00", "command": "daten-1s", "ausloeser": "plan",
            "dauer_s": "10", "exit": "1", "expect_ok": "0", "status": "rot",
            "notiz": "autofix versucht: Branch agent/autofix-2026-08-25",
        })
        assert autofix_erlaubt(reg, "daten-1s", jetzt) is False       # heute schon
        assert autofix_erlaubt(reg, "update", jetzt) is True          # anderer Command
        # 26 h spaeter wieder frei
        assert autofix_erlaubt(reg, "daten-1s", datetime(2026, 8, 26, 22, 0)) is True
```

- [ ] **Step 2: Test laufen lassen, Fehlschlag bestätigen**

Run: `python tools/test_agent_tick.py`
Expected: FAIL mit `ImportError: cannot import name 'autofix_erlaubt'`

- [ ] **Step 3: Die Versuchsgrenze implementieren**

Ergänze in `tools/agent_tick.py`:

```python
AUTOFIX_MARKE = "autofix versucht"


def autofix_erlaubt(register: Path, name: str, now: datetime) -> bool:
    """Ein Autofix-Versuch pro Command und 24 h. Verhindert den Reparaturkreisel."""
    if not register.exists():
        return True
    grenze = now - timedelta(hours=24)
    with register.open(encoding="utf-8", newline="") as f:
        for zeile in csv.DictReader(f):
            if zeile.get("command") != name:
                continue
            if AUTOFIX_MARKE not in (zeile.get("notiz") or ""):
                continue
            try:
                if datetime.fromisoformat(zeile["zeit_start"]) > grenze:
                    return False
            except (ValueError, KeyError, TypeError):
                continue
    return True
```

Erweitere `eskaliere()`, damit der Wachhund weiß, ob er reparieren darf — im JSON je Befund ein Feld ergänzen:

```python
    register = root / "algo" / "live" / "agent-runs.csv"
    for b in rot:
        b["autofix_erlaubt"] = autofix_erlaubt(register, b.get("command", ""), datetime.now())
```

Einfügen direkt nach `rot = [...]`, vor `argument = json.dumps(...)`.

- [ ] **Step 4: Tests laufen lassen, grün bestätigen**

Run: `python tools/test_agent_tick.py`
Expected: PASS, `19 Tests bestanden.`

- [ ] **Step 5: Den Wachhund-Command um den Autofix erweitern**

In `.claude/commands/wachhund.md` den vierten Spiegelstrich unter Punkt 2 ersetzen:

```markdown
   - **Crash oder Timeout im Code**: Traceback lesen, Ursache in `tools/` oder `algo/`
     finden. Steht im Befund `"autofix_erlaubt": true`, repariere ihn nach dem Verfahren
     unten. Steht dort `false`, wurde es fuer diesen Command in den letzten 24 Stunden
     schon einmal versucht -- dann nur diagnostizieren und berichten.
```

Und vor "Grenzen, die in jeder Ausbaustufe gelten" einfügen:

```markdown
## Autofix-Verfahren

Nur bei `"autofix_erlaubt": true`, und nur fuer Crashes in `tools/` oder `algo/`.

1. **Branch anlegen**, nie auf `main` arbeiten:
   `git checkout -b agent/autofix-<YYYY-MM-DD>` (existiert er schon, `git checkout` genuegt).
2. **Reparieren.** Kleinste Aenderung, die die Ursache behebt -- nicht das Symptom.
   Beruehrt der Fix eine Datei der Sperrliste unten: abbrechen, nur berichten.
3. **Verifizieren.** Starte den fehlgeschlagenen Command erneut
   (`claude -p "/<command>"`) und pruefe sein `expect` ein zweites Mal.
4. **Nur bei gruen behalten.** Ist der Lauf jetzt gruen: committen mit
   `fix | autofix <command>: <ursache>`. Ist er weiterhin rot: **Aenderung verwerfen**
   (`git checkout -- <dateien>`), zurueck auf `main` (`git checkout main`), und nur
   Traceback samt Diagnose berichten. Eine Reparatur, die nur plausibel aussieht, darf
   die Nacht nicht ueberleben.
5. **Nicht mergen.** Der Branch bleibt stehen und wartet auf Jannes. Schreib im Report
   ausdruecklich, welcher Branch auf Freigabe wartet und was er enthaelt.
6. **Notiz ins Register.** Haenge dem betroffenen Befund eine Zeile in
   `algo/live/agent-runs.csv` an, deren `notiz` mit `autofix versucht:` beginnt --
   daran erkennt der Taktgeber, dass es fuer heute genug ist. Ohne diese Zeile
   greift die Versuchsgrenze nicht.

**Zusaetzlich gesperrt fuer den Autofix** (ueber die Grenzen unten hinaus):
`CLAUDE.md`, `algo/CLAUDE.md`, `push.ps1`, `.gitignore`, `.claude/settings.json`.
Die Regeln repariert der Wachhund nicht selbst.
```

- [ ] **Step 6: Den Autofix trocken durchspielen**

Lege einen absichtlichen Fehler in ein harmloses Hilfsskript, lass den Wachhund darauf los und prüfe **die Sicherungen**, nicht die Reparatur:

```bash
git checkout -b test/autofix-probe
python -c "open('tools/probe_kaputt.py','w').write('import sys\nsys.exit(1)\n')"
git add tools/probe_kaputt.py && git commit -m "setup | Probe fuer Autofix-Test"
```

Expected nach dem Wachhund-Lauf, in dieser Reihenfolge geprüft:
1. `git branch --show-current` — er steht auf `agent/autofix-<datum>`, **nicht** auf `main`.
2. `git log main..HEAD --stat` — keine Datei aus `raw/`, keine `*.secrets.yaml`, kein `CLAUDE.md`.
3. `git log --oneline -1` auf `main` — unverändert.
4. `algo/live/agent-status.md` nennt den wartenden Branch.

Danach aufräumen: `git checkout main && git branch -D test/autofix-probe agent/autofix-<datum>` und `tools/probe_kaputt.py` löschen.

- [ ] **Step 7: Commit**

```bash
git add .claude/commands/wachhund.md tools/agent_tick.py tools/test_agent_tick.py
git commit -m "setup | Wachhund-Autofix: Branch statt main, Verifikationspflicht, Sperrliste, ein Versuch pro Nacht"
```

---

## Was dieser Plan bewusst nicht enthält

- **Die Cowork-Anpassungen.** Zwei Sätze in die Anweisung beider Briefings und das Aufräumen der doppelten Einträge muss Jannes in Claude Desktop selbst erledigen — von außen ist Coworks Planer nicht erreichbar. Bis das geschehen ist, meldet `briefing-morgens`/`briefing-abends` jeden Tag „ausgeblieben"; das ist korrekt, nur noch nicht nützlich. Steht in `.claude/commands/briefing-morgens.md` als Anleitung.
- **Erfassung manueller Läufe.** Bräuchte einen Session-Hook. `expect` deckt den Zweck ab.
- **`/tagesbericht` als geplanter Lauf.** Er gibt nur im Chat aus; ihn planbar zu machen hieße, ihn erst eine Datei schreiben zu lassen — eigene Änderung.
