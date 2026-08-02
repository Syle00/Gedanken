#!/usr/bin/env python3
"""Raeumt lose CSVs in raw/marktdaten/ in Tagesordner ein.

Aus

    raw/marktdaten/CME_MINI_MNQU2026, 1_f6229.csv
    raw/marktdaten/MNQ 2026-07-31 5m.csv

wird

    raw/marktdaten/31.07.2026/MNQ 2026-07-31 1m.csv
    raw/marktdaten/31.07.2026/MNQ 2026-07-31 5m.csv

Der Handelstag kommt aus der **letzten Kerze der Datei**, nicht aus dem Dateinamen —
so funktionieren auch rohe TradingView-Exporte, deren Namen kein Datum enthalten.
Kerzen ab 18:00 NY gehoeren bereits zur naechsten CME-Session und zaehlen deshalb
auf den Folgetag.

Der Timeframe wird aus dem Median-Abstand der Timestamps erkannt, das Symbol aus
dem Dateinamen (`CME_MINI_MNQU2026` -> `MNQ`, Kontraktcode wird abgestreift).

Aufruf:
    python tools/sort_marktdaten.py                 # einraeumen
    python tools/sort_marktdaten.py --dry-run       # nur zeigen, was passieren wuerde
    python tools/sort_marktdaten.py --symbol NQ     # Symbolerkennung ueberschreiben

Nur Standardbibliothek.
"""

from __future__ import annotations

import argparse
import csv
import filecmp
import re
import statistics
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

NY = ZoneInfo("America/New_York")
UTC = ZoneInfo("UTC")

DATA_DIR = Path(__file__).resolve().parent.parent / "raw" / "marktdaten"

# Median-Sekundenabstand -> Timeframe-Label
STEPS = {60: "1m", 300: "5m", 900: "15m", 3600: "1h", 14400: "4h", 86400: "1d"}

# Futures-Kontraktcode am Ende: MNQU2026, ESZ25, NQ1! ...
CONTRACT = re.compile(r"(?:[FGHJKMNQUVXZ]\d{2,4}|\d+!)$")


def read_times(path: Path) -> list[datetime]:
    out = []
    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        if not reader.fieldnames or "time" not in reader.fieldnames:
            return []
        for row in reader:
            raw = (row.get("time") or "").strip()
            if not raw:
                continue
            try:
                if raw.lstrip("-").isdigit():
                    out.append(datetime.fromtimestamp(int(raw), UTC).astimezone(NY))
                else:
                    ts = datetime.fromisoformat(raw.replace("Z", "+00:00"))
                    out.append(ts.astimezone(NY) if ts.tzinfo else ts.replace(tzinfo=NY))
            except ValueError:
                continue
    return sorted(out)


def trading_day(times: list[datetime]):
    """NY-Datum der Session. Ab 18:00 laeuft bereits die Session des Folgetags."""
    last = times[-1]
    return (last + timedelta(days=1)).date() if last.hour >= 18 else last.date()


def timeframe(times: list[datetime]) -> str | None:
    if len(times) < 3:
        return None
    steps = [(b - a).total_seconds() for a, b in zip(times, times[1:]) if b > a]
    if not steps:
        return None
    med = statistics.median(steps)
    best = min(STEPS, key=lambda s: abs(s - med))
    # 20% Toleranz — Session-Pausen verzerren den Median leicht
    return STEPS[best] if abs(best - med) <= 0.2 * best else None


def symbol_from_name(name: str) -> str | None:
    """'CME_MINI_MNQU2026, 1_f6229' -> 'MNQ';  'MNQ 2026-07-31 1m' -> 'MNQ'."""
    m = re.match(r"^([A-Za-z]{1,6}) \d{4}-\d{2}-\d{2} \w+$", name)
    if m:
        return m.group(1).upper()
    head = name.split(",")[0].strip()
    ticker = head.split("_")[-1] if "_" in head else head
    ticker = ticker.split()[0].upper()
    stripped = CONTRACT.sub("", ticker)
    return stripped or ticker or None


def plan(files: list[Path], forced_symbol: str | None):
    """Liefert (quelle, ziel, notiz) je Datei; ziel None bei Problem."""
    out = []
    for src in files:
        times = read_times(src)
        if not times:
            out.append((src, None, "keine lesbare time-Spalte"))
            continue
        tf = timeframe(times)
        if tf is None:
            out.append((src, None, "Timeframe nicht erkennbar"))
            continue
        sym = forced_symbol or symbol_from_name(src.stem)
        if not sym:
            out.append((src, None, "Symbol nicht erkennbar (--symbol nutzen)"))
            continue
        day = trading_day(times)
        dst = DATA_DIR / day.strftime("%d.%m.%Y") / f"{sym} {day.isoformat()} {tf}.csv"
        out.append((src, dst, f"{len(times)} Kerzen, letzte {times[-1]:%d.%m. %H:%M} NY"))
    return out


def loose_files() -> list[Path]:
    return sorted(p for p in DATA_DIR.glob("*.csv") if p.is_file())


def run(dry_run=False, forced_symbol=None, quiet=False) -> int:
    if not DATA_DIR.exists():
        return 0
    files = loose_files()
    if not files:
        if not quiet:
            print("raw/marktdaten/: nichts einzuraeumen.")
        return 0

    moved = skipped = 0
    for src, dst, note in plan(files, forced_symbol):
        if dst is None:
            print(f"  ! {src.name} — {note}")
            skipped += 1
            continue
        if dst.exists():
            if filecmp.cmp(src, dst, shallow=False):
                if dry_run:
                    print(f"  = {src.name} — identisch mit {dst.parent.name}/{dst.name}, "
                          f"Quelle waere zu loeschen")
                else:
                    src.unlink()
                    print(f"  = {src.name} — Duplikat von {dst.parent.name}/{dst.name}, entfernt")
                moved += 1
                continue
            stem, n = dst.stem, 2
            while dst.exists():
                dst = dst.with_name(f"{stem} ({n}).csv")
                n += 1
            note += " — Zielname belegt, abweichender Inhalt"
        rel = f"{dst.parent.name}/{dst.name}"
        if dry_run:
            print(f"  → {src.name}  ->  {rel}   ({note})")
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            src.replace(dst)
            print(f"  → {src.name}  ->  {rel}   ({note})")
        moved += 1

    if not quiet:
        verb = "waeren einzuraeumen" if dry_run else "eingeraeumt"
        print(f"{moved} Datei(en) {verb}"
              + (f", {skipped} uebersprungen" if skipped else "") + ".")
    return skipped


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="nur anzeigen, nichts verschieben")
    ap.add_argument("--symbol", help="Symbol erzwingen statt aus dem Dateinamen zu raten")
    ap.add_argument("--quiet", action="store_true", help="nur Meldungen zu einzelnen Dateien")
    a = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(1 if run(a.dry_run, a.symbol, a.quiet) else 0)


if __name__ == "__main__":
    main()
