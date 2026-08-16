"""Raeumt abgelaufene Bias-Dateien aus raw/journal/ in raw/journal/bias/{daily,weekly}/.

Workflow-Hintergrund (Nutzerentscheid 2026-08-16): Frisch erzeugte Bias-Dateien liegen
bewusst flach in `raw/journal/`, solange sie aktuell sind -- dort traegt der Nutzer seinen
eigenen Bias ein. Erst wenn der Tag bzw. die Woche vorbei ist, wandern sie ins Archiv.
Dieses Skript macht genau diesen einen Schritt, deterministisch und ohne LLM.

Regeln:
  "Daily Bias YYYY-MM-DD.md"  -> bias/daily/   sobald  datum  <  heute
  "Weekly Bias KWNN JJJJ.md"  -> bias/weekly/  sobald  (jahr, kw) < aktuelle ISO-Woche

Alles andere bleibt liegen und wird gemeldet -- Altbestand mit uneindeutigem Namen
("Daily Bias 10.08.md", "Daily Bias Journal 5.md") wird nicht geraten.
Inhalte werden nie veraendert, bestehende Zieldateien nie ueberschrieben.
"""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JOURNAL = ROOT / "raw" / "journal"

RE_DAILY = re.compile(r"^Daily Bias (\d{4})-(\d{2})-(\d{2})$")
RE_WEEKLY = re.compile(r"^Weekly Bias KW(\d{1,2}) (\d{4})$")


def ziel_fuer(stem: str, heute: date) -> str | None:
    """Unterordner, in den `stem` gehoert -- oder None, wenn er (noch) flach bleibt."""
    m = RE_DAILY.match(stem)
    if m:
        tag = date(int(m[1]), int(m[2]), int(m[3]))
        return "bias/daily" if tag < heute else None

    m = RE_WEEKLY.match(stem)
    if m:
        kw, jahr = int(m[1]), int(m[2])
        jetzt_jahr, jetzt_kw, _ = heute.isocalendar()
        return "bias/weekly" if (jahr, kw) < (jetzt_jahr, jetzt_kw) else None

    return None


def sortiere(journal: Path, heute: date, trocken: bool = False) -> dict:
    verschoben, aktuell, unklar, kollision = [], [], [], []

    for pfad in sorted(journal.glob("*.md")):
        if pfad.stem == "Journal":
            continue

        unter = ziel_fuer(pfad.stem, heute)
        if unter is None:
            # Aktuell (Datum liegt in der Zukunft) oder Name nicht auswertbar?
            if RE_DAILY.match(pfad.stem) or RE_WEEKLY.match(pfad.stem):
                aktuell.append(pfad.name)
            elif pfad.stem.startswith(("Daily Bias", "Weekly Bias")):
                unklar.append(pfad.name)
            continue

        ziel = journal / unter / pfad.name
        if ziel.exists():
            kollision.append(pfad.name)
            continue
        if not trocken:
            ziel.parent.mkdir(parents=True, exist_ok=True)
            pfad.rename(ziel)
        verschoben.append(f"{pfad.name} -> {unter}/")

    return {"verschoben": verschoben, "aktuell": aktuell,
            "unklar": unklar, "kollision": kollision}


def demo() -> None:
    """Selbstcheck gegen einen Wegwerf-Baum -- beruehrt raw/journal/ nicht."""
    import tempfile

    heute = date(2026, 8, 16)  # Sonntag, ISO-KW 33

    # Datumslogik
    assert ziel_fuer("Daily Bias 2026-08-15", heute) == "bias/daily", "gestern -> Archiv"
    assert ziel_fuer("Daily Bias 2026-08-16", heute) is None, "heute bleibt flach"
    assert ziel_fuer("Daily Bias 2026-08-17", heute) is None, "morgen bleibt flach"
    # KW-Logik: heute liegt in KW33, also ist KW34 die kommende Woche
    assert ziel_fuer("Weekly Bias KW32 2026", heute) == "bias/weekly", "Vorwoche -> Archiv"
    assert ziel_fuer("Weekly Bias KW33 2026", heute) is None, "laufende Woche bleibt"
    assert ziel_fuer("Weekly Bias KW34 2026", heute) is None, "kommende Woche bleibt"
    assert ziel_fuer("Weekly Bias KW52 2025", heute) == "bias/weekly", "Jahreswechsel"
    # Uneindeutiger Altbestand wird nie geraten
    assert ziel_fuer("Daily Bias 10.08", heute) is None, "kein Jahr -> nicht raten"
    assert ziel_fuer("Daily Bias Journal 5", heute) is None, "Notion-Altbestand"
    assert ziel_fuer("Weekly Bias KW 33", heute) is None, "Leerzeichen-Variante"
    assert ziel_fuer("Tape Reading 17", heute) is None, "fremde Reihe"

    with tempfile.TemporaryDirectory() as tmp:
        j = Path(tmp)
        for name in ["Daily Bias 2026-08-15.md", "Daily Bias 2026-08-17.md",
                     "Weekly Bias KW32 2026.md", "Daily Bias Journal 5.md",
                     "Tape Reading 17.md", "Journal.md"]:
            (j / name).write_text("x", encoding="utf-8")

        r = sortiere(j, heute)
        assert r["verschoben"] == ["Daily Bias 2026-08-15.md -> bias/daily/",
                                   "Weekly Bias KW32 2026.md -> bias/weekly/"], r
        assert r["aktuell"] == ["Daily Bias 2026-08-17.md"], r
        assert r["unklar"] == ["Daily Bias Journal 5.md"], r
        assert (j / "bias/daily/Daily Bias 2026-08-15.md").exists(), "verschoben"
        assert (j / "Daily Bias 2026-08-17.md").exists(), "aktuelle bleibt liegen"
        assert (j / "Tape Reading 17.md").exists(), "fremde Reihe unangetastet"
        assert (j / "Journal.md").exists(), "Journal.md unangetastet"

        # Kollision: Zieldatei existiert schon -> nicht ueberschreiben
        (j / "Daily Bias 2026-08-14.md").write_text("neu", encoding="utf-8")
        (j / "bias/daily/Daily Bias 2026-08-14.md").write_text("alt", encoding="utf-8")
        r2 = sortiere(j, heute)
        assert r2["kollision"] == ["Daily Bias 2026-08-14.md"], r2
        assert (j / "bias/daily/Daily Bias 2026-08-14.md").read_text(encoding="utf-8") == "alt"

    print("sortiere_bias: alle Checks bestanden")


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if "--demo" in argv:
        demo()
        return 0

    trocken = "--dry-run" in argv
    r = sortiere(JOURNAL, date.today(), trocken=trocken)

    if r["verschoben"]:
        print(("[dry-run] " if trocken else "") + f"Einsortiert ({len(r['verschoben'])}):")
        for z in r["verschoben"]:
            print(f"  {z}")
    else:
        print("Nichts einzusortieren.")

    if r["aktuell"]:
        print(f"Bleibt flach (noch aktuell): {', '.join(r['aktuell'])}")
    if r["kollision"]:
        print(f"!! Zieldatei existiert schon, NICHT verschoben: {', '.join(r['kollision'])}")
    if r["unklar"]:
        print(f"!! Name nicht auswertbar, liegen gelassen: {', '.join(r['unklar'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
