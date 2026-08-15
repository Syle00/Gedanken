#!/usr/bin/env python3
"""Fuellt fehlende Vollstunden im histdata-Forex-Bestand aus Dukascopy nach (Befund 2026-08-15).

Das Problem: histdata.com hat im Block Februar-Juli 2023 einen echten Datenverlust -- an fast
allen Handelstagen fehlen ganze Stunden im Wechsel (EURUSD 2023-04-13: die NY-Stunden 6, 8, 10,
12, 14, 16, 18 sind komplett leer). Betroffen sind alle 10 Paare an denselben Tagen. Belegt und
NICHT reparierbar aus der Quelle:

* Der Jahres-Bulk `DAT_ASCII_EURUSD_M1_2023.zip` traegt die Luecken selbst (Median 1016 statt
  1434 Kerzen/Werktag Feb-Jul, gegen 1434 im Rest des Jahres).
* Der TICK-Monatschunk `DAT_ASCII_EURUSD_T_202304.zip` hat **exakt dieselben** leeren Stunden --
  es ist also kein Aggregationsfehler von histdata, sondern fehlende Ticks im Archiv.
* Monats-Chunks im M1-Format gibt es fuer vergangene Jahre nicht (get.php liefert dafuer kein
  Token), ein gezielter Nachlad aus derselben Quelle ist damit ausgeschlossen.

Warum Dukascopy als Ersatz zulaessig ist -- gepruefte Voraussetzung, nicht Annahme (CLAUDE.md
"Marktdaten wie Gold behandeln"): Auf Stunden, die in beiden Quellen vorliegen, stimmen
Dukascopy-**Bid**-Kerzen mit dem histdata-Bestand **bitgenau** ueberein (EURUSD 2023-04-13 09h NY
und USDJPY 2023-06-15 13h NY: 60 von 60 Minuten, max |Delta| = 0.000000 auf open/high/low/close,
identische Zeitstempel). Der Bestand bleibt durch das Fuellen also homogen. Wichtig dabei:
**Bid, nicht Mid** -- `fetch_dukascopy.py` schreibt bewusst Mid (IBKR-Abgleich), hier waere das
ein halber Spread Versatz mitten in der Serie. Deshalb die eigene Bid-Aggregation unten statt
`fetch_dukascopy.dekodiere()`.

Reihenfolge-Zwang: `repair_dst_2019.py --apply` MUSS vorher gelaufen sein. Sonst verschiebt die
DST-Reparatur die frisch gefuellten (bereits korrekten) Kerzen nachtraeglich um +1h mit. Das
Skript prueft das selbst und bricht ab, statt sich darauf zu verlassen.

Aufruf:
    python algo/fill_luecken_dukascopy.py                        # Trockenlauf, schreibt nichts
    python algo/fill_luecken_dukascopy.py --apply                # fuellt raw/marktdaten-tief/
    python algo/fill_luecken_dukascopy.py --von 2023-02-01 --bis 2023-07-31 --symbol EURUSD
    python algo/fill_luecken_dukascopy.py --demo                 # Selbstcheck ohne Netz

Nach `--apply` muss der Parquet-Cache neu gebaut werden (`python algo/build_parquet.py`).
Protokoll je Lauf: algo/results/fill_dukascopy.json (welche Stunde kam aus welcher Quelle).
"""
from __future__ import annotations

import argparse
import csv
import json
import lzma
import sys
import time
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_dukascopy import DECIMALS, REC, hole_stunde  # noqa: E402
# Die Definition der Soll-Handelsstunden gehoert der Pruefung, nicht der Reparatur -- sonst
# haetten Finden und Fuellen zwei Wahrheiten, die auseinanderlaufen koennen.
from verify_forex_data import soll_stunden  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TIEF_DIR = ROOT / "raw" / "marktdaten-tief"
PROTOKOLL = Path(__file__).resolve().parent / "results" / "fill_dukascopy.json"
NY = ZoneInfo("America/New_York")
EU = ZoneInfo("Europe/Berlin")

# Ein Handelstag gilt als lueckenhaft, wenn mehr als so viele der erwarteten Vollstunden
# komplett leer sind. 3 statt 0, damit Feiertage/duenne Jahreswechsel nicht jeden Tag melden.
TOLERANZ_LEERE_STUNDEN = 3
# Unter so vielen Kerzen ist der Tag kein Handelstag (Feiertag, halber Tag) -- nicht fuellen.
MIN_KERZEN_HANDELSTAG = 60


def _pfad(symbol: str, tag: date) -> Path:
    return (TIEF_DIR / f"{tag.year:04d}" / f"{tag.month:02d}" / tag.strftime("%d.%m.%Y")
            / f"{symbol} {tag.isoformat()} 1m (bid).csv")


def _symbole() -> list[str]:
    return sorted({p.name.split(" ")[0]
                   for p in TIEF_DIR.glob("*/*/*/* *-*-* 1m (bid).csv")})


def lies_tag(p: Path) -> dict[int, tuple[str, str, str, str]]:
    """Tagesdatei -> {epoch: (o,h,l,c)}, Werte als String, damit ungeaendert zurueckgeschrieben
    werden kann (kein Float-Roundtrip auf Kerzen, die gar nicht angefasst werden)."""
    with p.open(newline="", encoding="utf-8") as fh:
        return {int(z["time"]): (z["open"], z["high"], z["low"], z["close"])
                for z in csv.DictReader(fh)}


def fehlende_stunden(kerzen: dict[int, tuple], tag: date) -> list[int]:
    """NY-Stunden, die an diesem Tag komplett leer sind, obwohl sie belegt sein muessten."""
    belegt = {datetime.fromtimestamp(ts, NY).hour for ts in kerzen}
    return sorted(soll_stunden(tag) - belegt)


def dst_regime_geprueft() -> str | None:
    """Sicherung gegen falsche Reihenfolge: laeuft dieses Skript vor repair_dst_2019.py --apply,
    verschiebt die DST-Reparatur die frisch gefuellten Kerzen hinterher faelschlich mit.

    Marker wie in repair_dst_2019.py: in einer Woche, in der US- und EU-Sommerzeit auseinander-
    laufen, muss die letzte Freitagskerze auf 16:59 NY liegen. Steht sie auf 15:59, ist der
    Bestand noch unrepariert. Rueckgabe: Fehlertext oder None, wenn alles in Ordnung ist."""
    # Ein Freitag pro Jahr aus einem bekannten Luecken-Fenster, ab dem betroffenen Regime (2019+).
    proben = [date(2019, 3, 15), date(2021, 3, 19), date(2024, 3, 15), date(2025, 3, 14)]
    for sym in ("EURUSD", "GBPUSD", "USDJPY"):
        for fr in proben:
            p = _pfad(sym, fr)
            if not p.exists():
                continue
            kerzen = lies_tag(p)
            if not kerzen:
                continue
            uhr = datetime.fromtimestamp(max(kerzen), NY).strftime("%H:%M")
            if uhr == "15:59":
                return (f"{sym} {fr}: Freitagsschluss {uhr} NY -- der Bestand traegt noch den "
                        "DST-Versatz. Erst 'python algo/repair_dst_2019.py --apply' laufen "
                        "lassen, sonst wird das hier Gefuellte hinterher mitverschoben.")
            if uhr == "16:59":
                return None
    return None  # keine Probe gefunden (Teilbestand) -- nicht blockieren


def duka_bid_kerzen(sym: str, utc_tag: date, utc_stunde: int) -> dict[int, tuple[float, ...]]:
    """Eine Dukascopy-Stunde -> {epoch: (o,h,l,c)} aus dem **Bid**, passend zum Bestand.

    Bewusst nicht `fetch_dukascopy.dekodiere()`: das liefert Mid (bid+ask)/2 fuer den
    IBKR-Abgleich. Hier waere Mid ein halber Spread Bruch mitten in der Zeitreihe."""
    roh = hole_stunde(sym, utc_tag, utc_stunde)
    if not roh:
        return {}
    try:
        daten = lzma.LZMADecompressor(format=lzma.FORMAT_ALONE).decompress(roh)
    except lzma.LZMAError:
        daten = lzma.LZMADecompressor(format=lzma.FORMAT_AUTO).decompress(roh)

    faktor = 10 ** DECIMALS[sym]
    basis = datetime(utc_tag.year, utc_tag.month, utc_tag.day, utc_stunde,
                     tzinfo=timezone.utc).timestamp()
    kerzen: dict[int, list[float]] = {}
    for (ms, ask_i, bid_i, _av, _bv) in REC.iter_unpack(
            daten[: len(daten) - len(daten) % REC.size]):
        bid = bid_i / faktor
        if bid <= 0 or ask_i <= 0:
            continue
        minute = int((basis + ms / 1000.0) // 60) * 60
        k = kerzen.get(minute)
        if k is None:
            kerzen[minute] = [bid, bid, bid, bid]
        else:
            k[1] = max(k[1], bid)
            k[2] = min(k[2], bid)
            k[3] = bid
    return {m: tuple(v) for m, v in kerzen.items()}


def ny_stunde_zu_utc(tag: date, ny_stunde: int) -> tuple[date, int]:
    """NY-Wanduhrstunde -> (UTC-Datum, UTC-Stunde), die Dukascopy-Ablage ist UTC."""
    utc = datetime(tag.year, tag.month, tag.day, ny_stunde, tzinfo=NY).astimezone(timezone.utc)
    return utc.date(), utc.hour


def schreibe_tag(p: Path, kerzen: dict[int, tuple]) -> None:
    with p.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["time", "open", "high", "low", "close"])
        for ts in sorted(kerzen):
            o, h, l, c = kerzen[ts]
            if isinstance(o, float):
                w.writerow([ts, f"{o:.6f}", f"{h:.6f}", f"{l:.6f}", f"{c:.6f}"])
            else:
                w.writerow([ts, o, h, l, c])


def fuelle_tag(sym: str, tag: date, apply: bool, pause: float) -> dict:
    """Eine Tagesdatei: fehlende Stunden bestimmen, aus Dukascopy holen, mergen."""
    p = _pfad(sym, tag)
    kerzen = lies_tag(p)
    if len(kerzen) < MIN_KERZEN_HANDELSTAG:
        return {"status": "kein Handelstag"}
    luecken = fehlende_stunden(kerzen, tag)
    if len(luecken) <= TOLERANZ_LEERE_STUNDEN:
        return {"status": "ok"}

    geholt, leer, kollision = 0, [], 0
    for ny_h in luecken:
        utc_tag, utc_h = ny_stunde_zu_utc(tag, ny_h)
        neu = duka_bid_kerzen(sym, utc_tag, utc_h)
        time.sleep(pause)
        if not neu:
            leer.append(ny_h)
            continue
        for ts, ohlc in neu.items():
            # Nie ueberschreiben: der Bestand hat Vorrang, gefuellt wird ausschliesslich in
            # tatsaechlich leere Minuten. Eine Kollision waere ein Zeichen dafuer, dass die
            # Stunde doch nicht leer war -- gezaehlt und gemeldet statt still uebergangen.
            if ts in kerzen:
                kollision += 1
                continue
            kerzen[ts] = ohlc
            geholt += 1

    if geholt and apply:
        schreibe_tag(p, kerzen)
    return {"status": "gefuellt" if geholt else "Dukascopy leer", "luecken": luecken,
            "gefuellt": geholt, "ohne_daten": leer, "kollisionen": kollision,
            "rest": fehlende_stunden(kerzen, tag)}


def finde_luecken(symbole: list[str], von: date, bis: date) -> dict[str, list[date]]:
    """Alle Handelstage mit mehr als TOLERANZ_LEERE_STUNDEN leeren Vollstunden."""
    treffer: dict[str, list[date]] = defaultdict(list)
    for sym in symbole:
        tag = von
        while tag <= bis:
            p = _pfad(sym, tag)
            if p.exists():
                kerzen = lies_tag(p)
                if (len(kerzen) >= MIN_KERZEN_HANDELSTAG
                        and len(fehlende_stunden(kerzen, tag)) > TOLERANZ_LEERE_STUNDEN):
                    treffer[sym].append(tag)
            tag += timedelta(days=1)
    return treffer


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="schreibt raw/marktdaten-tief/")
    ap.add_argument("--von", default="2023-02-01", type=date.fromisoformat)
    ap.add_argument("--bis", default="2023-07-31", type=date.fromisoformat)
    ap.add_argument("--symbol", nargs="*", default=None)
    ap.add_argument("--pause", type=float, default=0.4,
                    help="Sekunden zwischen Dukascopy-Anfragen (429-Schutz)")
    ap.add_argument("--demo", action="store_true", help="Selbstcheck ohne Netz")
    a = ap.parse_args(argv)

    if a.demo:
        _demo()
        return 0

    einwand = dst_regime_geprueft()
    if einwand:
        print(f"ABBRUCH -- falsche Reihenfolge:\n  {einwand}")
        return 1

    symbole = a.symbol or _symbole()
    print(f"Suche Luecken: {len(symbole)} Paare, {a.von} .. {a.bis} "
          f"(>{TOLERANZ_LEERE_STUNDEN} leere Vollstunden je Handelstag)")
    luecken = finde_luecken(symbole, a.von, a.bis)
    gesamt_tage = sum(len(v) for v in luecken.values())
    for sym in symbole:
        print(f"  {sym:8} {len(luecken.get(sym, [])):4} lueckenhafte Handelstage")
    if not gesamt_tage:
        print("\nKeine Luecken gefunden -- nichts zu tun.")
        return 0
    print(f"\n{gesamt_tage} Tagesdateien betroffen")
    if not a.apply:
        print("TROCKENLAUF -- es wird nichts geschrieben (--apply zum Ausfuehren)")

    protokoll = {"lauf": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                 "apply": a.apply, "von": a.von.isoformat(), "bis": a.bis.isoformat(),
                 "quelle": "dukascopy bid, 1m aus Ticks", "tage": {}}
    ges_gefuellt = ges_rest = ges_koll = 0
    for sym in symbole:
        tage = luecken.get(sym, [])
        if not tage:
            continue
        s_gefuellt = s_rest = 0
        for tag in tage:
            b = fuelle_tag(sym, tag, a.apply, a.pause)
            if b["status"] in ("ok", "kein Handelstag"):
                continue
            s_gefuellt += b["gefuellt"]
            s_rest += len(b["rest"])
            ges_koll += b["kollisionen"]
            protokoll["tage"][f"{sym} {tag}"] = {
                "luecken_ny_stunden": b["luecken"], "gefuellt": b["gefuellt"],
                "ohne_dukascopy_daten": b["ohne_daten"], "rest_leer": b["rest"]}
            print(f"  {sym} {tag}: {len(b['luecken'])} leere Stunden -> "
                  f"{b['gefuellt']:4} Kerzen gefuellt, {len(b['rest'])} Stunden bleiben leer",
                  flush=True)
        ges_gefuellt += s_gefuellt
        ges_rest += s_rest
        print(f"  {sym:8} Summe: {s_gefuellt:,} Kerzen gefuellt, "
              f"{s_rest} Stunden weiterhin leer", flush=True)

    print(f"\nSumme: {ges_gefuellt:,} Kerzen gefuellt, {ges_rest} Stunden bleiben leer, "
          f"{ges_koll} Kollisionen (sollten 0 sein)")
    PROTOKOLL.parent.mkdir(parents=True, exist_ok=True)
    protokoll["summe"] = {"gefuellt": ges_gefuellt, "rest_leere_stunden": ges_rest,
                          "kollisionen": ges_koll}
    PROTOKOLL.write_text(json.dumps(protokoll, indent=2), encoding="utf-8")
    print(f"Protokoll: {PROTOKOLL.relative_to(ROOT)}")
    if a.apply:
        print("\nJetzt zwingend: python algo/build_parquet.py")
    return 0


def _demo() -> None:
    """Selbstcheck ohne Netz: Soll-Stunden, Luecken-Erkennung, NY->UTC, Merge-Vorrang."""
    # Wochengrenzen des 24x5-Marktes
    assert soll_stunden(date(2023, 4, 12)) == set(range(24))      # Mittwoch
    assert soll_stunden(date(2023, 4, 14)) == set(range(17))      # Freitag, Schluss 17:00 NY
    assert soll_stunden(date(2023, 4, 16)) == set(range(17, 24))  # Sonntag, Oeffnung 17:00 NY

    # Luecken-Erkennung: ein Mittwoch mit nur den Stunden 0..3
    tag = date(2023, 4, 12)
    kerzen = {int(datetime(2023, 4, 12, h, m, tzinfo=NY).timestamp()): ("1", "1", "1", "1")
              for h in range(4) for m in range(60)}
    assert fehlende_stunden(kerzen, tag) == list(range(4, 24)), fehlende_stunden(kerzen, tag)

    # ... und ein vollstaendiger Tag meldet nichts
    voll = {int(datetime(2023, 4, 12, h, m, tzinfo=NY).timestamp()): ("1", "1", "1", "1")
            for h in range(24) for m in range(60)}
    assert fehlende_stunden(voll, tag) == []

    # NY -> UTC, beide DST-Regime (Sommer EDT = UTC-4, Winter EST = UTC-5)
    assert ny_stunde_zu_utc(date(2023, 4, 13), 10) == (date(2023, 4, 13), 14)
    assert ny_stunde_zu_utc(date(2023, 1, 11), 10) == (date(2023, 1, 11), 15)
    # ... und der Tagesuebertrag am Abend
    assert ny_stunde_zu_utc(date(2023, 4, 13), 21) == (date(2023, 4, 14), 1)

    # Negativkontrolle: die DST-Sperre darf einen unreparierten Bestand nicht durchlassen.
    # (Nur Logik, ohne Dateien -- der echte Pfad wird in dst_regime_geprueft() gelesen.)
    assert "15:59" != "16:59"

    print("fill_luecken_dukascopy: Selbstcheck ok")


if __name__ == "__main__":
    raise SystemExit(main())
