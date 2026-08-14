#!/usr/bin/env python3
"""Ergaenzt fehlende Kerzen in BESTEHENDEN raw/marktdaten/-Dateien aus yfinance.

Warum es das zusaetzlich zu `fetch_yfinance.py` gibt: dessen `write_day()` ueberschreibt
grundsaetzlich nie (bewusst, schuetzt TradingView-Daten vor yfinance). Bricht ein Abruf ab,
friert der Stumpf damit fuer immer ein -- `fetch_yfinance.py` meldet beim naechsten Lauf nur
"existiert bereits, uebersprungen". Gemessen am 2026-08-13: alle 10 Forex-Paare hatten fuer
den 11.08. nur ~765 statt 1440 Kerzen, Ende 06:45 NY, seit dem abgebrochenen Lauf vom 11.08.
Die Spec `docs/superpowers/specs/2026-08-12-marktdaten-schicht-design.md` benennt genau
diesen Fall ("Abgebrochener Download"), hatte aber kein Werkzeug dagegen.

Konfliktregel umgekehrt zu `ingest_tvexport.py`: hier gewinnt der BESTAND. Nur Zeitstempel,
die noch gar nicht in der Datei stehen, kommen dazu. Damit gilt "yfinance ueberschreibt nie"
(Spec 3.2) weiter woertlich -- es wird nichts revidiert, nur ergaenzt. Vorhandene Kerzen mit
abweichenden Werten werden gezaehlt und berichtet, nicht angefasst.

Aufruf:
    python algo/backfill_yfinance.py 2026-08-10 2026-08-13 --symbol EURUSD=X
    python algo/backfill_yfinance.py --demo
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fetch_yfinance import DATA_DIR, download_interval, symbol_prefix, trading_day
from ingest_tvexport import TF_SEKUNDEN, lies, luecken, schreib


def zielpfad(symbol: str, tf: str, tag) -> Path:
    return (DATA_DIR / f"{tag:%Y}" / f"{tag:%m}" / f"{tag:%d.%m.%Y}"
            / f"{symbol_prefix(symbol)} {tag.isoformat()} {tf}.csv")


def als_kerzen(rows) -> dict:
    """yfinance-DataFrame -> {ts: (o,h,l,c)} im Dateiformat."""
    ts = rows.index.as_unit("s").astype("int64")
    return {
        int(t): (str(o), str(h), str(l), str(c))
        for t, o, h, l, c in zip(ts, rows["Open"], rows["High"], rows["Low"], rows["Close"])
    }


def backfill(start: str, end: str, symbol: str, tf: str = "1m", schreiben: bool = True) -> list[dict]:
    """Ergaenzt fehlende Kerzen je Handelstag. Legt KEINE neuen Dateien an --
    dafuer ist fetch_yfinance.py zustaendig, das den Tagesrand korrekt abschneidet."""
    df = download_interval(symbol, tf, start, end)
    if df.empty:
        return []

    bericht = []
    for tag, rows in df.groupby(df.index.map(lambda t: trading_day(t, tf == "1d"))):
        pfad = zielpfad(symbol, tf, tag)
        if not pfad.exists():
            continue  # neuer Tag -> fetch_yfinance.py, nicht hier
        alt = lies(pfad)
        neu = als_kerzen(rows)
        fehlend = {ts: k for ts, k in neu.items() if ts not in alt}
        # Bestand gewinnt: nur ergaenzen, nie revidieren.
        abweichend = sum(
            1 for ts in set(alt) & set(neu)
            if any(round(float(a), 6) != round(float(b), 6) for a, b in zip(alt[ts], neu[ts]))
        )
        gemerged = {**neu, **alt}
        bericht.append({
            "tag": tag, "pfad": pfad, "vorher": len(alt), "hinzu": len(fehlend),
            "gesamt": len(gemerged), "abweichend_ignoriert": abweichend,
            "luecken": luecken(sorted(gemerged), TF_SEKUNDEN[tf]),
        })
        if schreiben and fehlend:
            schreib(pfad, gemerged, symbol_prefix(symbol))
    return bericht


def demo() -> None:
    """Selbstcheck ohne Netz und ohne raw/-Zugriff."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "X 2026-08-11 1m.csv"
        basis = 1786435200
        bestand = {basis + i * 60: ("1", "2", "0", "1") for i in range(3)}
        schreib(p, bestand)

        neu = {basis + i * 60: ("9", "9", "9", "9") for i in range(5)}
        alt = lies(p)
        fehlend = {ts: k for ts, k in neu.items() if ts not in alt}
        gemerged = {**neu, **alt}

        assert len(fehlend) == 2, f"nur die 2 neuen Zeitstempel duerfen fehlen, waren {len(fehlend)}"
        assert len(gemerged) == 5, "Merge muss 5 Kerzen ergeben"
        assert gemerged[basis] == ("1", "2", "0", "1"), "Bestand muss gewinnen, nicht yfinance"
        assert gemerged[basis + 3 * 60] == ("9", "9", "9", "9"), "fehlende Kerze muss ergaenzt werden"

        # Lueckenmeldung nach dem Merge
        assert luecken(sorted(gemerged)) == [], "lueckenloser Merge darf nichts melden"
        loechrig = {basis: (), basis + 300: ()}
        assert luecken(sorted(loechrig)) == [(basis, 4)], "Luecke muss weiter erkannt werden"

    print("backfill_yfinance: alle Selbstchecks bestanden")


def main(argv=None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("start")
    ap.add_argument("end", help="exklusiv")
    ap.add_argument("--symbol", required=True)
    ap.add_argument("--tf", default="1m")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)

    zeilen = backfill(a.start, a.end, a.symbol, a.tf, schreiben=not a.dry_run)
    for z in zeilen:
        rev = f", {z['abweichend_ignoriert']} abweichend (Bestand behalten)" if z["abweichend_ignoriert"] else ""
        print(f"{z['tag']}  {z['vorher']:5d} +{z['hinzu']:4d} -> {z['gesamt']:5d}"
              f"  Luecken danach: {len(z['luecken'])}{rev}")
    print(f"{sum(z['hinzu'] > 0 for z in zeilen)} Datei(en) ergaenzt.")
    return 0


if __name__ == "__main__":
    if "--demo" in sys.argv:
        demo()
    elif len(sys.argv) > 1:
        sys.exit(main())
    else:
        print(__doc__)
