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
