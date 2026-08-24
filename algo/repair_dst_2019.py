#!/usr/bin/env python3
"""Repariert den 1-Stunden-Zeitversatz im histdata-Forex-Bestand (Befund 2026-08-15).

Hintergrund und Beleg: siehe Modul-Docstring von `algo/fetch_histdata.py`. Kurz: der
`get.php`-Endpoint schaltet seine Zeitstempel **ab 2019** an den EU-, nicht an den
US-Umstellungsterminen um. In den rund vier Wochen pro Jahr, in denen beide Regeln
auseinanderlaufen, liegt der Bestand dadurch eine Stunde zu frueh. `fetch_histdata.py` ist
korrigiert -- dieses Skript zieht die bereits heruntergeladenen Dateien nach, ohne erneut
23 Jahre zu laden.

Warum Umstempeln und nicht neu laden: der Fehler ist eine reine Beschriftung. Jede Kerze
existiert, nur ihr Zeitstempel ist um 3600 s zu klein; die OHLC-Werte sind unberuehrt. Ein
erneuter Download brauchte 240 Monats-Chunks und wuerde ausserdem den bereits dokumentierten
Live-Feed-Drift von histdata.com (siehe algo/PLAN.md, 2026-08-14) in den Bestand holen.
Das Umstempeln ist verlustfrei und exakt aequivalent -- die Gegenprobe steht trotzdem offen:
`--stichprobe` schreibt eine Liste der Monats-Chunks, mit denen sich das Ergebnis gegen einen
frischen Download pruefen laesst.

Warum die Fenster sauber abgeschlossen sind: alle Sommerzeit-Umstellungen fallen auf einen
Sonntag, der Forex-Markt oeffnet aber erst Sonntag 17:00 NY und schliesst Freitag 17:00 NY.
Beide Fenstergrenzen liegen damit im Wochenende -- es wandert keine Kerze ueber den Fensterrand
hinaus, wenn alles um +1h verschoben wird. Innerhalb des Fensters wandert die letzte Stunde
eines NY-Tages in die Datei des Folgetags; genau dafuer wird neu einsortiert statt Datei fuer
Datei gerechnet.

Aufruf:
    python algo/repair_dst_2019.py                 # Trockenlauf, schreibt nichts
    python algo/repair_dst_2019.py --apply         # schreibt raw/marktdaten-tief/ um
    python algo/repair_dst_2019.py --stichprobe    # Chunk-Liste fuer die Download-Gegenprobe

Nach `--apply` muss der Parquet-Cache neu gebaut werden (`python algo/build_parquet.py`),
sonst bleibt die alte, falsche Zeitachse in `algo/cache/` liegen.
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from analyze_ohlc import pruefe_kerzen  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TIEF_DIR = ROOT / "raw" / "marktdaten-tief"
NY = ZoneInfo("America/New_York")
EU = ZoneInfo("Europe/Berlin")

# Ab hier folgt der Endpoint der EU-Regel (identisch zu fetch_histdata.EU_REGEL_AB gehalten --
# bewusst dupliziert statt importiert, damit dieses Reparaturskript auch dann noch beschreibt,
# was es getan hat, wenn der Downloader spaeter umgebaut wird).
EU_REGEL_AB = date(2019, 1, 1)
VERSATZ_S = 3600  # Bestand ist 1h zu frueh gestempelt


def _offset(zone: ZoneInfo, tag: date) -> float:
    return zone.utcoffset(datetime(tag.year, tag.month, tag.day, 12)).total_seconds() / 3600


def luecken_fenster(von: date, bis: date) -> list[tuple[date, date]]:
    """Zeitraeume, in denen US- und EU-Sommerzeit auseinanderlaufen (nur ab EU_REGEL_AB)."""
    fenster: list[tuple[date, date]] = []
    start: date | None = None
    tag = von
    while tag <= bis:
        luecke = (_offset(NY, tag) == -4) != (_offset(EU, tag) == 2)
        if luecke and start is None:
            start = tag
        elif not luecke and start is not None:
            fenster.append((start, tag - timedelta(days=1)))
            start = None
        tag += timedelta(days=1)
    if start is not None:
        fenster.append((start, bis))
    return [(a, b) for a, b in fenster if b >= EU_REGEL_AB]


def betroffene_tage(fenster: list[tuple[date, date]]) -> set[date]:
    tage: set[date] = set()
    for a, b in fenster:
        for i in range((b - a).days + 1):
            tage.add(a + timedelta(days=i))
    return tage


def _pfad(symbol: str, tag: date) -> Path:
    return (TIEF_DIR / f"{tag.year:04d}" / f"{tag.month:02d}" / tag.strftime("%d.%m.%Y")
            / f"{symbol} {tag.isoformat()} 1m (bid).csv")


def _symbole() -> list[str]:
    namen = {p.name.split(" ")[0] for p in TIEF_DIR.glob("*/*/*/* *-*-* 1m (bid).csv")}
    return sorted(namen)


def wochenschluss_marker(symbol: str, fenster: list[tuple[date, date]]) -> list[tuple[date, str]]:
    """Letzte Freitagskerze je Fenster, als NY-Wanduhr -- der Marker, der den Fehler belegt.

    Der 24x5-Markt schliesst Freitag 17:00 NY, die letzte 1m-Kerze liegt also auf 16:59. Steht
    dort 15:59, ist der Bestand noch unrepariert; steht 16:59, war er es schon."""
    treffer = []
    for a, b in fenster:
        freitage = [a + timedelta(days=i) for i in range((b - a).days + 1)
                    if (a + timedelta(days=i)).weekday() == 4]
        for fr in reversed(freitage):
            p = _pfad(symbol, fr)
            if not p.exists():
                continue
            with p.open(newline="", encoding="utf-8") as fh:
                letzte = None
                for zeile in csv.DictReader(fh):
                    letzte = zeile
            if letzte:
                ts = datetime.fromtimestamp(int(letzte["time"]), NY)
                treffer.append((fr, ts.strftime("%H:%M")))
            break
    return treffer


def sperre_pruefen(symbol: str, fenster: list[tuple[date, date]]) -> list[str]:
    """Bricht ab, wenn der Bestand nicht (mehr) das erwartete Fehlerbild zeigt.

    Das Skript ist **nicht idempotent** -- ein zweiter Lauf wuerde noch einmal um +1h schieben und
    den Bestand aktiv kaputtmachen. Statt das nur zu dokumentieren, wird es hier geprueft: die
    letzte Freitagskerze eines Luecken-Fensters muss auf 15:59 NY liegen (= unrepariert). Liegt
    sie auf 16:59, ist das Fenster bereits in Ordnung und darf nicht angefasst werden."""
    fehler = []
    for tag, uhr in wochenschluss_marker(symbol, fenster):
        if uhr == "15:59":
            continue
        if uhr < "15:59":
            # Datenluecke am Tagesende, nicht Zeitversatz: der Tag endet frueher, weil Kerzen
            # fehlen (belegt fuer den Block Feb-Jul 2023, siehe algo/PLAN.md 2026-08-15). Das ist
            # ein eigenes Problem und darf die Zeitkorrektur nicht blockieren -- ein zu frueher
            # Schluss kann nie von einer bereits erfolgten +1h-Verschiebung stammen.
            continue
        fehler.append(f"{symbol} {tag}: Freitagsschluss {uhr} NY statt 15:59 -- "
                      "sieht nach bereits erfolgter Reparatur aus, Abbruch statt zweitem +1h")
    return fehler


def repariere(symbol: str, tage: set[date], apply: bool) -> dict:
    """Liest alle betroffenen Tagesdateien, verschiebt +1h, sortiert nach NY-Tag neu ein."""
    quellen = sorted(t for t in tage if _pfad(symbol, t).exists())
    neu: dict[date, list[tuple[int, str, str, str, str]]] = defaultdict(list)
    gelesen = 0
    for tag in quellen:
        with _pfad(symbol, tag).open(newline="", encoding="utf-8") as fh:
            for zeile in csv.DictReader(fh):
                ts = int(zeile["time"]) + VERSATZ_S
                ny_tag = datetime.fromtimestamp(ts, NY).date()
                neu[ny_tag].append((ts, zeile["open"], zeile["high"],
                                    zeile["low"], zeile["close"]))
                gelesen += 1

    bericht = {"symbol": symbol, "quelldateien": len(quellen), "kerzen": gelesen,
               "zieldateien": len(neu), "gewandert": 0, "hinweise": []}

    # Kerzen, die durch die Verschiebung in einen Tag ausserhalb der Quellmenge rutschen, waeren
    # ein Zeichen dafuer, dass die Fenstergrenzen doch nicht im Wochenende liegen -- das ist die
    # tragende Annahme dieses Skripts und wird deshalb geprueft statt vorausgesetzt.
    fremd = {t: len(v) for t, v in neu.items() if t not in tage}
    if fremd:
        bericht["gewandert"] = sum(fremd.values())
        bericht["hinweise"].append(
            f"WARNUNG: {sum(fremd.values())} Kerzen fallen aus dem Fenster: "
            + ", ".join(f"{t} ({n})" for t, n in sorted(fremd.items())))

    for ny_tag, zeilen in sorted(neu.items()):
        zeilen.sort()
        for hinweis in pruefe_kerzen(
                ((ts, float(o), float(h), float(l), float(c)) for ts, o, h, l, c in zeilen),
                symbol, f"{symbol} {ny_tag.isoformat()} 1m (bid).csv"):
            bericht["hinweise"].append(f"{ny_tag}: {hinweis}")
        if not apply:
            continue
        ziel = _pfad(symbol, ny_tag)
        ziel.parent.mkdir(parents=True, exist_ok=True)
        with ziel.open("w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["time", "open", "high", "low", "close"])
            w.writerows(zeilen)
    return bericht


def stichprobe(fenster: list[tuple[date, date]]) -> list[str]:
    """Monats-Chunks, mit denen sich das Umstempeln gegen einen frischen Download pruefen laesst."""
    monate = sorted({(a.year, a.month) for a, _ in fenster} | {(b.year, b.month) for _, b in fenster})
    return [f"{j}-{m:02d}" for j, m in monate]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="schreibt raw/marktdaten-tief/ um")
    ap.add_argument("--stichprobe", action="store_true", help="nur Chunk-Liste ausgeben")
    ap.add_argument("--symbol", nargs="*", default=None)
    a = ap.parse_args(argv)

    fenster = luecken_fenster(date(2003, 1, 1), date.today())
    if a.stichprobe:
        print("Monats-Chunks fuer die Download-Gegenprobe:")
        for m in stichprobe(fenster):
            print(f"  {m}")
        return 0

    tage = betroffene_tage(fenster)
    handelstage = {t for t in tage if t.weekday() < 5}
    print(f"{len(fenster)} Fenster ab {EU_REGEL_AB}, {len(handelstage)} Handelstage je Paar")
    for von, bis in fenster:
        print(f"  {von} .. {bis}")
    print()

    symbole = a.symbol or _symbole()

    # Idempotenz-Sperre vor jedem Schreibzugriff: ein zweiter Lauf wuerde den Bestand um eine
    # weitere Stunde verschieben. Bewusst als harter Abbruch ueber ALLE Paare, bevor auch nur
    # eine Datei geschrieben wird -- ein halb reparierter Bestand waere schlimmer als gar keiner.
    print("Sperre: Freitagsschluss je Luecken-Fenster muss auf 15:59 NY liegen ...")
    einwaende = [z for sym in symbole for z in sperre_pruefen(sym, fenster)]
    if einwaende:
        print(f"  ABBRUCH -- {len(einwaende)} Fenster zeigen nicht das erwartete Fehlerbild:")
        for z in einwaende[:20]:
            print(f"    {z}")
        if len(einwaende) > 20:
            print(f"    ... und {len(einwaende) - 20} weitere")
        return 1
    print(f"  ok -- alle Fenster in allen {len(symbole)} Paaren sind unrepariert\n")

    if not a.apply:
        print("TROCKENLAUF -- es wird nichts geschrieben (--apply zum Ausfuehren)\n")
    ges = 0
    for sym in symbole:
        b = repariere(sym, tage, a.apply)
        ges += b["kerzen"]
        print(f"  {b['symbol']:8} {b['quelldateien']:4} Quelldateien -> {b['zieldateien']:4} "
              f"Zieldateien, {b['kerzen']:>8,} Kerzen +1h")
        for h in b["hinweise"]:
            print(f"           ? {h}")
    print(f"\nSumme: {ges:,} Kerzen ueber {len(symbole)} Paare")
    if a.apply:
        print("\nJetzt zwingend: python algo/build_parquet.py  (Cache traegt sonst weiter die "
              "alte Zeitachse)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
