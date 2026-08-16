"""Sortiert lose TradingView-Exporte aus raw/ in das Tagesschema von raw/marktdaten/.

Hintergrund: Der Nutzer legt frische Chart-Exporte direkt in `raw/` ab (TradingView-Namen wie
"CME_MINI_NQU2026, 1_98a6b.csv"). `algo/bias_levels.py` und die Backtests lesen aber nur
`raw/marktdaten/<jahr>/<monat>/<TT.MM.JJJJ>/<SYM> <YYYY-MM-DD> <tf>.csv` -- solange die Exporte
lose herumliegen, werden sie schlicht nicht gefunden (2026-08-16: NQ-Levels wurden deshalb aus
MNQ gerechnet, obwohl die besseren NQ-Daten laengst da waren).

**Session-Grenze, nicht Mitternacht.** Eine Tagesdatei im Bestand laeuft von Vortag 18:00 NY
bis Handelstag 16:59 NY (1380 1m-Kerzen = 23 h). Wer nach Kalendertag schneidet, zerreisst die
Session und erzeugt genau den Fehler, der am 16.08.2026 die NDOG-Berechnung verfaelscht hat.

Aufruf:
    python tools/sortiere_marktdaten.py --dry-run   # zeigt nur, was passieren wuerde
    python tools/sortiere_marktdaten.py             # schreibt
    python tools/sortiere_marktdaten.py --demo      # Selbstcheck, kein Dateizugriff
"""

from __future__ import annotations

import csv
import re
import sys
from datetime import UTC, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "raw"
ZIEL = RAW / "marktdaten"
NY = ZoneInfo("America/New_York")
# Der Nutzer haelt zwei Clones ("VS Folder 1" und der Obsidian-Vault "Gedanken") und legt
# frische Exporte mal hier, mal dort ab. Beide Ablagen werden gelesen, geschrieben wird nur
# in den Bestand dieses Repos.
QUELLEN = [RAW, ROOT.parent / "Gedanken" / "raw"]

# TradingView-Exportname -> Vault-Symbol. Kontraktmonat/Continuous-Suffix faellt weg,
# die Tagesordner fuehren das Symbol ohne Laufzeit ("NQ 2026-08-14 1m.csv").
SYMBOL = {"NQU2026": "NQ", "NQZ2026": "NQ", "ESU2026": "ES", "ESZ2026": "ES",
          "MNQU2026": "MNQ", "MNQZ2026": "MNQ", "MESU2026": "MES",
          "YMU2026": "YM", "YMZ2026": "YM",
          "MNQ1!": "MNQ", "MES1!": "MES", "NQ1!": "NQ", "ES1!": "ES", "YM1!": "YM"}
# TradingView-Intervall -> Vault-Timeframe
TIMEFRAME = {"1S": "1s", "1": "1m", "5": "5m", "15": "15m", "60": "1h",
             "240": "4h", "1D": "1d"}
# Nach dem Intervall folgt entweder "_<hash>", " (2)" oder direkt ".csv" -- TradingView
# vergibt den Hash nur beim wiederholten Export desselben Charts.
DATEINAME = re.compile(
    r"^(?:CME_MINI_|CME_|CBOT_MINI_|CBOT_|COMEX_|NYMEX_)?"
    r"(?P<sym>[A-Z0-9!]+),\s*(?P<tf>1S|1D|\d+)(?:_|\.| \()")

SESSION_ENDE = time(17, 0)     # 17:00 NY -- danach Pause bis 18:00


def handelstag(t: datetime):
    """Handelstag einer NY-Zeit. Ab 18:00 gehoert die Kerze zum *naechsten* Werktag:
    die Session Sonntag 18:00 -> Montag 16:59 ist der Handelstag Montag."""
    if t.time() < SESSION_ENDE:
        return t.date()
    d = t.date() + timedelta(days=1)
    while d.weekday() >= 5:                 # Sa/So -> Montag
        d += timedelta(days=1)
    return d


def deute_namen(name: str) -> tuple[str, str] | None:
    """(Symbol, Timeframe) aus einem TradingView-Exportnamen, oder None."""
    m = DATEINAME.match(name)
    if not m:
        return None
    sym = SYMBOL.get(m["sym"])
    tf = TIMEFRAME.get(m["tf"])
    return (sym, tf) if sym and tf else None


def lies(pfad: Path) -> list[dict]:
    with pfad.open(newline="", encoding="utf-8-sig") as fh:
        return [r for r in csv.DictReader(fh) if r.get("time")]


def gruppiere(zeilen: list[dict]) -> dict:
    """Zeilen nach Handelstag buendeln (Reihenfolge bleibt erhalten)."""
    nach_tag: dict = {}
    for r in zeilen:
        t = datetime.fromtimestamp(int(r["time"]), UTC).astimezone(NY)
        nach_tag.setdefault(handelstag(t), []).append(r)
    return nach_tag


def zielpfad(sym: str, tf: str, tag) -> Path:
    return (ZIEL / f"{tag:%Y}" / f"{tag:%m}" / f"{tag:%d.%m.%Y}"
            / f"{sym} {tag:%Y-%m-%d} {tf}.csv")


def sortiere(trocken: bool = False) -> dict:
    geschrieben, vorhanden, uebersprungen, teilweise = [], [], [], []

    # Erst alle Quellen sammeln: mehrere Exporte decken denselben Tag oft unterschiedlich weit
    # ab (ein 3-Tage- und ein 18-Tage-Export ueberlappen). Pro (Symbol, TF, Tag) gewinnt die
    # **vollstaendigste** Fassung -- sonst haengt es an der Dateinamen-Sortierung, ob ein
    # angeschnittener Tag den vollen verdraengt.
    beste: dict = {}
    dateien = sorted({p.resolve() for q in QUELLEN if q.is_dir() for p in q.glob("*.csv")})
    for quelle in dateien:
        deutung = deute_namen(quelle.name)
        if not deutung:
            uebersprungen.append(f"{quelle.name} (Name nicht deutbar)")
            continue
        sym, tf = deutung
        try:
            zeilen = lies(quelle)
        except Exception as exc:
            uebersprungen.append(f"{quelle.name} ({type(exc).__name__})")
            continue
        if not zeilen:
            uebersprungen.append(f"{quelle.name} (leer)")
            continue
        felder = list(zeilen[0])
        for tag, rows in gruppiere(zeilen).items():
            key = (sym, tf, tag)
            if key not in beste or len(rows) > len(beste[key][1]):
                beste[key] = (quelle, rows, felder)

    for (sym, tf, tag), (quelle, rows, felder) in sorted(
            beste.items(), key=lambda kv: (kv[0][2], kv[0][0], kv[0][1])):
        ziel = zielpfad(sym, tf, tag)
        if ziel.exists():
            # Bestandsdatei nie ueberschreiben (CLAUDE.md: raw/ ist inhaltlich unveraenderlich).
            # Ist der Export aber deutlich vollstaendiger, wird er als "(2)"-Fassung daneben
            # gelegt -- das etablierte Muster fuer einen zweiten Export desselben Tages.
            # Anlass: NQ 2026-08-12 lag mit 1011 Kerzen ab 00:09 im Bestand, der Export hatte
            # 1380 ab 18:00; die fehlenden 7 h verschluckten den NDOG vom 11.08.
            try:
                vorhandene_zeilen = sum(1 for _ in ziel.open(encoding="utf-8-sig")) - 1
            except Exception:
                vorhandene_zeilen = -1
            if len(rows) > vorhandene_zeilen > 0:
                zweit = ziel.with_name(f"{ziel.stem} (2){ziel.suffix}")
                if zweit.exists():
                    vorhanden.append(f"{zweit.name} (schon da)")
                    continue
                if not trocken:
                    with zweit.open("w", newline="", encoding="utf-8") as fh:
                        w = csv.DictWriter(fh, fieldnames=felder)
                        w.writeheader()
                        w.writerows(rows)
                geschrieben.append(f"{quelle.name} -> {zweit.relative_to(ROOT)} "
                                   f"({len(rows)} statt {vorhandene_zeilen} Zeilen)")
                continue
            vorhanden.append(f"{ziel.name} ({len(rows)} Zeilen, nicht ueberschrieben)")
            continue
        # Fuer 1s liegt im Bestand die IBKR-Parquet-Datei (voller Handelstag, 82800 Bars).
        # Ein TradingView-1s-Export deckt nur wenige Minuten ab -- als CSV daneben gelegt
        # waere er eine zweite, schlechtere Quelle fuer denselben Tag. Nicht einsortieren.
        parquet = ziel.with_suffix(".parquet")
        if parquet.exists():
            vorhanden.append(f"{parquet.name} ({len(rows)} Zeilen im Export vs. "
                             f"vorhandenes IBKR-Parquet -- CSV nicht danebengelegt)")
            continue
        # Ein Handelstag, dessen Session im Export nur angeschnitten ist, wird als
        # solcher gemeldet -- sonst landet eine 3-Stunden-Datei als "voller Tag" im
        # Bestand und taeuscht Vollstaendigkeit vor.
        soll = {"1m": 1380, "1s": 82800, "5m": 276, "15m": 92}.get(tf)
        if soll and len(rows) < soll:
            teilweise.append(f"{ziel.name}: {len(rows)}/{soll} Kerzen")
        if not trocken:
            ziel.parent.mkdir(parents=True, exist_ok=True)
            with ziel.open("w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, fieldnames=felder)
                w.writeheader()
                w.writerows(rows)
        geschrieben.append(f"{quelle.name} -> {ziel.relative_to(ROOT)} ({len(rows)})")

    return {"geschrieben": geschrieben, "vorhanden": vorhanden,
            "uebersprungen": uebersprungen, "teilweise": teilweise}


def demo() -> None:
    from datetime import date

    # Namensdeutung
    assert deute_namen("CME_MINI_NQU2026, 1_98a6b.csv") == ("NQ", "1m")
    assert deute_namen("CME_MINI_ESU2026, 1S_26d87.csv") == ("ES", "1s")
    assert deute_namen("CME_MINI_MNQ1!, 15_6fcfd.csv") == ("MNQ", "15m")
    assert deute_namen("preview.csv") is None, "fremde Datei wird nicht geraten"
    assert deute_namen("CME_MINI_XYZ9999, 1_a.csv") is None, "unbekanntes Symbol"
    # TradingView haengt den Hash nur beim Wiederholungsexport an
    assert deute_namen("CME_MINI_MNQU2026, 1.csv") == ("MNQ", "1m"), "ohne Hash"
    assert deute_namen("CBOT_MINI_YMU2026, 1 (1).csv") == ("YM", "1m"), "Kopie-Suffix"
    assert deute_namen("CBOT_MINI_YM1!, 1D_983a2.csv") == ("YM", "1d"), "CBOT + 1D"
    assert deute_namen("CME_MINI_MES1!, 1D_fe8f3.csv") == ("MES", "1d"), "1D vor \\d+"

    # Session-Grenze: 18:00 gehoert zum naechsten Handelstag, 16:59 zum laufenden
    assert handelstag(datetime(2026, 8, 13, 16, 59, tzinfo=NY)) == date(2026, 8, 13)
    assert handelstag(datetime(2026, 8, 13, 18, 0, tzinfo=NY)) == date(2026, 8, 14)
    assert handelstag(datetime(2026, 8, 13, 23, 59, tzinfo=NY)) == date(2026, 8, 14)
    assert handelstag(datetime(2026, 8, 14, 9, 30, tzinfo=NY)) == date(2026, 8, 14)
    # Freitag 18:00 -> Montag (Wochenende wird uebersprungen), Sonntag 18:00 -> Montag
    assert handelstag(datetime(2026, 8, 14, 18, 0, tzinfo=NY)) == date(2026, 8, 17), "Fr->Mo"
    assert handelstag(datetime(2026, 8, 16, 18, 0, tzinfo=NY)) == date(2026, 8, 17), "So->Mo"

    # Gruppierung schneidet an der Session-, nicht an der Kalendergrenze
    def _z(tag, hh, mm):
        return {"time": str(int(datetime(2026, 8, tag, hh, mm, tzinfo=NY).timestamp())),
                "open": "1", "high": "1", "low": "1", "close": "1"}
    g = gruppiere([_z(13, 16, 59), _z(13, 18, 0), _z(13, 23, 59), _z(14, 0, 0), _z(14, 16, 59)])
    assert sorted(g) == [date(2026, 8, 13), date(2026, 8, 14)], sorted(g)
    assert len(g[date(2026, 8, 13)]) == 1 and len(g[date(2026, 8, 14)]) == 4, \
        "Mitternacht darf NICHT trennen, 17:00-18:00 schon"

    assert zielpfad("NQ", "1m", date(2026, 8, 14)).relative_to(ROOT).as_posix() == \
        "raw/marktdaten/2026/08/14.08.2026/NQ 2026-08-14 1m.csv"

    print("sortiere_marktdaten: alle Checks bestanden")


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if "--demo" in argv:
        demo()
        return 0

    trocken = "--dry-run" in argv
    r = sortiere(trocken=trocken)
    kopf = "[dry-run] " if trocken else ""

    if r["geschrieben"]:
        print(f"{kopf}Einsortiert ({len(r['geschrieben'])}):")
        for z in r["geschrieben"]:
            print(f"  {z}")
    else:
        print("Nichts einzusortieren.")
    if r["teilweise"]:
        print(f"\n!! Unvollstaendige Handelstage ({len(r['teilweise'])}) -- Session nur "
              f"angeschnitten, nicht als vollen Tag behandeln:")
        for z in r["teilweise"]:
            print(f"  {z}")
    if r["vorhanden"]:
        print(f"\nSchon vorhanden, nicht ueberschrieben ({len(r['vorhanden'])}):")
        for z in r["vorhanden"]:
            print(f"  {z}")
    if r["uebersprungen"]:
        print(f"\nUebersprungen ({len(r['uebersprungen'])}):")
        for z in r["uebersprungen"]:
            print(f"  {z}")
    print("\nOriginale in raw/ bleiben liegen.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
