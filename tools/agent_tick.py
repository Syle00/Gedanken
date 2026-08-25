"""Taktgeber fuer die geplanten Vault-Laeufe.

Liest den Zeitplan aus dem YAML-Frontmatter der Commands und Skills, entscheidet
ohne LLM, was faellig ist, startet die Laeufe und protokolliert sie. Nur bei
rotem Befund wird ein Modell gestartet.

Design: docs/superpowers/specs/2026-08-25-main-agent-wachhund-design.md
"""
from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
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


REGISTER_SPALTEN = [
    "zeit_start", "command", "ausloeser", "dauer_s", "exit",
    "expect_ok", "status", "notiz",
]
# Ab dieser Verspaetung gilt ein Lauf als verpasst statt planmaessig.
NACHHOL_SCHWELLE = timedelta(hours=1)
# Aeltere Faelligkeiten werden nicht mehr nachgeholt (Ruling 1): liegt ueber
# dem groessten Abstand zweier Faelligkeiten im Plan (20:00 -> 06:30 = 10,5h)
# und unter 24h, damit ein noch nie gelaufener Eintrag nicht die Faelligkeit
# des Vortags nachholt.
NACHHOL_FENSTER = timedelta(hours=18)


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
    seinem letzten protokollierten Lauf liegt und nicht aelter als
    NACHHOL_FENSTER ist (Ruling 1 -- sonst holt ein noch nie gelaufener
    Eintrag rueckwirkend die Faelligkeit des Vortags nach). `extern` wird nie
    gestartet, aber erst gemeldet, wenn sein timeout_s als Kulanzfenster
    abgelaufen ist (Ruling 3).
    """
    dran = []
    for e in entries:
        faellig_um = last_due(e.schedule, now)
        if faellig_um is None:
            continue
        if now - faellig_um > NACHHOL_FENSTER:
            continue
        zuletzt = last_run(register, e.name)
        if zuletzt is not None and zuletzt >= faellig_um:
            continue
        if e.extern:
            if now - faellig_um >= timedelta(seconds=e.timeout_s):
                dran.append((e, "extern"))
        elif now - faellig_um > NACHHOL_SCHWELLE:
            dran.append((e, "nachhol"))
        else:
            dran.append((e, "plan"))
    return dran


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
        # Ruling 2: fuer 'changed:' zaehlt im Trockenlauf der heutige
        # Tagesbeginn als Startzeitpunkt, nicht der aktuelle Moment -- sonst
        # ist eine Datei, die heute frueh entstand, faelschlich rot. Der
        # echte Startzeitpunkt eines Laufs bleibt run_entry (Task 4)
        # vorbehalten.
        tagesbeginn = datetime.combine(now.date(), time.min)
        for e in entries:
            ok, notiz = expect_ok(e.expect, ROOT, tagesbeginn, now.date())
            aufgeloest = resolve_placeholders(str(e.expect), now.date()) if e.expect else "-"
            marke = next((a for x, a in dran if x.name == e.name), "-")
            print(f"  {e.name:24} {e.schedule:16} faellig={marke:8} "
                  f"expect={'ok' if ok else 'ROT'}  {aufgeloest}")
            if not ok and notiz:
                print(f"  {'':24} -> {notiz}")
        return 0

    register.parent.mkdir(parents=True, exist_ok=True)
    for e, ausloeser in dran:
        zeile = run_entry(e, ausloeser, ROOT, now)
        append_run(register, zeile)
        print(f"{zeile['status']:6} {e.name} ({ausloeser}) {zeile['notiz']}")
    write_status(ROOT, entries, now)
    return 0


if __name__ == "__main__":
    sys.exit(cli())
