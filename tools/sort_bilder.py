#!/usr/bin/env python3
"""Raeumt lose Bilddateien direkt unter raw/ nach raw/bilder/ ein.

Nur Bilder, die lose im raw/-Wurzelverzeichnis liegen (z.B. frische Screenshots),
wandern nach raw/bilder/. Bereits einsortierte Assets (raw/trading-ict/assets/,
raw/journal/assets/) bleiben unangetastet.

Aufruf:
    python tools/sort_bilder.py                 # einraeumen
    python tools/sort_bilder.py --dry-run       # nur zeigen, was passieren wuerde

Nur Standardbibliothek.
"""

from __future__ import annotations

import argparse
import filecmp
import sys
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parent.parent / "raw"
DEST_DIR = RAW_DIR / "bilder"

IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".tif", ".tiff"}


def loose_images() -> list[Path]:
    return sorted(p for p in RAW_DIR.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXT)


def run(dry_run=False, quiet=False) -> int:
    files = loose_images()
    if not files:
        if not quiet:
            print("raw/: keine losen Bilder einzuraeumen.")
        return 0

    moved = 0
    for src in files:
        dst = DEST_DIR / src.name
        if dst.exists():
            if filecmp.cmp(src, dst, shallow=False):
                if dry_run:
                    print(f"  = {src.name} — identisch mit bilder/{dst.name}, Quelle waere zu loeschen")
                else:
                    src.unlink()
                    print(f"  = {src.name} — Duplikat von bilder/{dst.name}, entfernt")
                moved += 1
                continue
            stem, suf, n = dst.stem, dst.suffix, 2
            while dst.exists():
                dst = DEST_DIR / f"{stem} ({n}){suf}"
                n += 1
            note = " — Zielname belegt, abweichender Inhalt"
        else:
            note = ""
        if dry_run:
            print(f"  → {src.name}  ->  bilder/{dst.name}{note}")
        else:
            DEST_DIR.mkdir(parents=True, exist_ok=True)
            src.replace(dst)
            print(f"  → {src.name}  ->  bilder/{dst.name}{note}")
        moved += 1

    if not quiet:
        verb = "waeren einzuraeumen" if dry_run else "eingeraeumt"
        print(f"{moved} Bild(er) {verb}.")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="nur anzeigen, nichts verschieben")
    ap.add_argument("--quiet", action="store_true", help="nur Meldungen zu einzelnen Dateien")
    a = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(run(a.dry_run, a.quiet))


if __name__ == "__main__":
    main()
