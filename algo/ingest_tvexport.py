"""Nimmt einen TradingView-1m-Export, splittet ihn nach Handelstagen und fuehrt ihn
mit dem vorhandenen Bestand in raw/marktdaten/ zusammen.

Warum: TradingView exportiert alle *geladenen* Balken, nicht einen sauberen Handelstag.
Ein Export deckt darum meist mehrere (Teil-)Tage ab, und mehrere Exporte desselben Tages
ergaenzen sich. Gemessen am 2026-08-12: vier Teilexporte des 11.08. ergaben zusammen
exakt 1380 lueckenlose Kerzen, einzeln keiner mehr als 1171.

Konfliktregel: Bei gleichem Zeitstempel gewinnt der NEUE Export. Grund: TradingView
revidiert open/close nach (gemessen: 7,7 % der Kerzen zwischen zwei Exporten desselben
Tages, fast nur open/close, meist 1 Tick). Abweichungen werden gezaehlt und berichtet,
nicht verschluckt.

Aufruf:
    python algo/ingest_tvexport.py <exportdatei> <SYMBOL>
    python algo/ingest_tvexport.py --demo
"""
import csv
import datetime
import sys
import zoneinfo
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from analyze_ohlc import pruefe_kerzen  # noqa: E402

NY = zoneinfo.ZoneInfo("America/New_York")
RAW = Path(__file__).resolve().parent.parent / "raw" / "marktdaten"

# (Startstunde des Handelstags in NY, Soll-Kerzen). Soll None = Profil noch nicht gemessen.
PROFILE = {
    "futures": (18, 1380),  # 18:00 NY Vortag -> 17:00 NY, Pause 17-18 Uhr
    "forex": (17, 1440),  # 17:00 NY -> 17:00 NY, durchgehend
    "index": (17, None),  # DXY/EXY/BXY/JXY: duenn, mit Lucken - Soll erst messen
}
FUTURES = {"MNQ", "NQ", "ES", "YM", "RTY", "6E", "6B", "6J", "6S", "6C"}
INDIZES = {"DXY", "EXY", "BXY", "JXY"}


def profil(symbol):
    stamm = symbol.rstrip("!").rstrip("123456789").upper()
    if stamm in INDIZES:
        return PROFILE["index"]
    if stamm in FUTURES:
        return PROFILE["futures"]
    return PROFILE["forex"]


def handelstag(ts, startstunde):
    """Handelstag, zu dem ein Zeitstempel gehoert (Tag endet zur Startstunde)."""
    d = datetime.datetime.fromtimestamp(ts, NY)
    return (d + datetime.timedelta(hours=24 - startstunde)).date()


def lies(pfad):
    """CSV -> {ts: (o,h,l,c)}. Akzeptiert UNIX-Timestamps (TradingView-Format)."""
    with open(pfad, newline="") as fh:
        return {
            int(r["time"]): tuple(r[k] for k in ("open", "high", "low", "close"))
            for r in csv.DictReader(fh)
        }


def schreib(pfad, kerzen, symbol=None):
    # Gate wie in fetch_yfinance.write_day -- gilt auch fuer TradingView-Exporte und
    # fuer backfill_yfinance.py, das diese Funktion mitbenutzt.
    for hinweis in pruefe_kerzen(((ts, *kerzen[ts]) for ts in sorted(kerzen)),
                                 symbol, pfad.name):
        print(f"  ? {hinweis}")
    pfad.parent.mkdir(parents=True, exist_ok=True)
    with open(pfad, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["time", "open", "high", "low", "close"])
        for ts in sorted(kerzen):
            w.writerow([ts, *kerzen[ts]])


def zielpfad(symbol, tag):
    return RAW / f"{tag:%Y}" / f"{tag:%m}" / f"{tag:%d.%m.%Y}" / f"{symbol} {tag:%Y-%m-%d} 1m.csv"


def luecken(ts_sortiert, schritt=60):
    """Fehlende Kerzen als (Zeitstempel davor, Anzahl). `schritt` = Sekunden pro Kerze --
    ohne ihn meldet jeder Nicht-1m-Timeframe jede Kerze als Luecke, und eine echte Luecke
    geht in diesem Rauschen unter."""
    return [
        (ts_sortiert[i], (ts_sortiert[i + 1] - ts_sortiert[i]) // schritt - 1)
        for i in range(len(ts_sortiert) - 1)
        if ts_sortiert[i + 1] - ts_sortiert[i] != schritt
    ]


def ingest(exportdatei, symbol, schreiben=True):
    """Splittet den Export nach Handelstagen und merged in den Bestand.

    Gibt eine Liste von Berichtszeilen zurueck (ein dict je Handelstag).
    """
    startstunde, soll = profil(symbol)
    neu = lies(exportdatei)

    nach_tag = {}
    for ts, ohlc in neu.items():
        nach_tag.setdefault(handelstag(ts, startstunde), {})[ts] = ohlc

    bericht = []
    for tag in sorted(nach_tag):
        pfad = zielpfad(symbol, tag)
        alt = lies(pfad) if pfad.exists() else {}
        # Konflikt: neuer Export gewinnt, Abweichung zaehlen.
        # Numerisch vergleichen, nicht als String: "29839.0" und "29839" sind derselbe Kurs,
        # unterschiedlich formatiert. Als String verglichen meldete das 51 % statt 6 % Revision.
        abweichungen = sum(
            1
            for ts in set(alt) & set(nach_tag[tag])
            if any(float(a) != float(b) for a, b in zip(alt[ts], nach_tag[tag][ts]))
        )
        gemerged = {**alt, **nach_tag[tag]}
        ts_sortiert = sorted(gemerged)
        zeile = {
            "tag": tag,
            "vorher": len(alt),
            "hinzu": len(set(gemerged) - set(alt)),
            "gesamt": len(gemerged),
            "soll": soll,
            "vollstaendig": soll is not None and len(gemerged) >= soll,
            "luecken": luecken(ts_sortiert),
            "revidiert": abweichungen,
            "pfad": pfad,
        }
        if schreiben:
            schreib(pfad, gemerged, symbol)
        bericht.append(zeile)
    return bericht


def demo():
    """Selbstcheck mit synthetischen Kerzen - keine Dateien, kein Netz."""
    import tempfile

    # Forex-Tag 2026-08-11 laeuft 10.08. 17:00 -> 11.08. 17:00 NY
    start = datetime.datetime(2026, 8, 10, 17, 0, tzinfo=NY)
    basis = int(start.timestamp())

    # Handelstag-Zuordnung: erste und letzte Minute gehoeren zum 11.08.
    assert handelstag(basis, 17) == datetime.date(2026, 8, 11), "Tagesbeginn falsch zugeordnet"
    assert handelstag(basis + 1439 * 60, 17) == datetime.date(2026, 8, 11), "Tagesende falsch"
    assert handelstag(basis + 1440 * 60, 17) == datetime.date(2026, 8, 12), "Folgetag falsch"

    # Futures-Tag beginnt 18:00 -> eine Stunde spaeter als Forex
    f = datetime.datetime(2026, 8, 10, 18, 0, tzinfo=NY)
    assert handelstag(int(f.timestamp()), 18) == datetime.date(2026, 8, 11), "Futures-Tag falsch"

    # Profilzuordnung
    assert profil("MNQ")[1] == 1380, "MNQ muss Futures-Profil haben"
    assert profil("6E1!")[1] == 1380, "6E1! ist ein Futures-Kontrakt"
    assert profil("EURUSD")[1] == 1440, "EURUSD muss Forex-Profil haben"
    assert profil("DXY")[1] is None, "DXY-Profil ist noch nicht gemessen"

    # Merge: zwei Teilexporte ergaenzen sich, Konflikt gewinnt der neue
    with tempfile.TemporaryDirectory() as tmp:
        a = Path(tmp) / "a.csv"
        b = Path(tmp) / "b.csv"
        schreib(a, {basis + i * 60: ("1", "2", "0", "1") for i in range(100)})
        schreib(b, {basis + i * 60: ("9", "9", "9", "9") for i in range(50, 150)})
        alt = lies(a)
        neu = lies(b)
        gemerged = {**alt, **neu}
        assert len(gemerged) == 150, f"Merge muss 150 Kerzen ergeben, ergab {len(gemerged)}"
        assert gemerged[basis + 60 * 60] == ("9", "9", "9", "9"), "neuer Export muss gewinnen"
        assert gemerged[basis] == ("1", "2", "0", "1"), "alte Kerze ohne Konflikt bleibt"

        # Unterschiedliche Schreibweise desselben Kurses ist KEINE Revision
        gleich = all(
            float(a) == float(b)
            for a, b in zip(("29839.0", "2", "0", "1"), ("29839", "2.00", "0", "1"))
        )
        assert gleich, "numerischer Vergleich muss Formatunterschiede ignorieren"

        # Luecke wird erkannt
        mit_luecke = {basis: ("1", "1", "1", "1"), basis + 300: ("1", "1", "1", "1")}
        lk = luecken(sorted(mit_luecke))
        assert lk == [(basis, 4)], f"Luecke von 4 Minuten erwartet, bekam {lk}"

        # Lueckenloser Lauf meldet nichts
        assert luecken(sorted({basis + i * 60: () for i in range(10)})) == [], "Fehlalarm"

        # Groebere Timeframes: nur mit passendem Schritt lueckenlos, sonst Dauerfehlalarm
        fuenfmin = sorted({basis + i * 300: () for i in range(10)})
        assert luecken(fuenfmin, 300) == [], "5m-Reihe darf mit schritt=300 nichts melden"
        assert len(luecken(fuenfmin)) == 9, "mit schritt=60 meldet jede 5m-Kerze -- genau der Fehlalarm"
        assert luecken([basis, basis + 900], 300) == [(basis, 2)], "2 fehlende 5m-Kerzen erwartet"

    print("ingest_tvexport: alle Selbstchecks bestanden")


if __name__ == "__main__":
    if "--demo" in sys.argv:
        demo()
    elif len(sys.argv) >= 3:
        for z in ingest(sys.argv[1], sys.argv[2]):
            st = "VOLLSTAENDIG" if z["vollstaendig"] else (
                f"fehlen {z['soll'] - z['gesamt']}" if z["soll"] else "Soll unbekannt"
            )
            rev = f", {z['revidiert']} revidiert" if z["revidiert"] else ""
            print(f"{z['tag']}  {z['vorher']:5d} +{z['hinzu']:4d} -> {z['gesamt']:5d}  {st}"
                  f"  Luecken: {len(z['luecken'])}{rev}")
    else:
        print(__doc__)
