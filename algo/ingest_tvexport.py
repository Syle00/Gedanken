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

Timeframe: `--tf` steuert Dateiname und Soll-/Lueckenrechnung (Default 1m). **Auf 1d aktuell
nicht nutzbar** -- der Merge laeuft ueber den rohen Zeitstempel, und dort stempeln die Quellen
verschieden (yfinance 00:00 UTC, TradingView Sessionstart 18:00 NY). `ingest()` bricht in dem
Fall ab, statt zwei Balken fuer denselben Handelstag abzulegen; welcher Stempel im Bestand
gilt, ist offen (siehe algo/PLAN.md, 2026-08-14).

Aufruf:
    python algo/ingest_tvexport.py <exportdatei> <SYMBOL> [--tf 1m]
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
FUTURES = {"MNQ", "NQ", "ES", "MES", "YM", "RTY", "6E", "6B", "6J", "6S", "6C"}
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


def tagesstempel(tag):
    """Kanonischer Stempel eines Tagesbalkens: 00:00 UTC des Handelstags.

    Das ist die Konvention, die der Bestand ohnehin schon durchgaengig hat (2026-08-14 ueber
    alle 7965 vorhandenen 1d-Dateien geprueft, null Abweichungen) -- sie kommt von yfinance.
    UTC-verankert, also ohne Sommerzeit-Sprung; in NY liegt derselbe Moment je nach Jahreszeit
    auf 19:00 oder 20:00 des Vortags. TradingView stempelt stattdessen auf den Sessionstart
    18:00 NY, deshalb muss beim 1d-Ingest genau hier normalisiert werden.
    """
    return int(datetime.datetime.combine(tag, datetime.time(0, 0), datetime.timezone.utc).timestamp())


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


TF_SEKUNDEN = {"1m": 60, "5m": 300, "15m": 900, "1h": 3600, "4h": 14400, "1d": 86400}


def zielpfad(symbol, tag, tf="1m"):
    return RAW / f"{tag:%Y}" / f"{tag:%m}" / f"{tag:%d.%m.%Y}" / f"{symbol} {tag:%Y-%m-%d} {tf}.csv"


def luecken(ts_sortiert, schritt=60):
    """Fehlende Kerzen als (Zeitstempel davor, Anzahl). `schritt` = Sekunden pro Kerze --
    ohne ihn meldet jeder Nicht-1m-Timeframe jede Kerze als Luecke, und eine echte Luecke
    geht in diesem Rauschen unter."""
    return [
        (ts_sortiert[i], (ts_sortiert[i + 1] - ts_sortiert[i]) // schritt - 1)
        for i in range(len(ts_sortiert) - 1)
        if ts_sortiert[i + 1] - ts_sortiert[i] != schritt
    ]


def ingest(exportdatei, symbol, schreiben=True, tf="1m", nur_neu=False):
    """Splittet den Export nach Handelstagen und merged in den Bestand.

    Gibt eine Liste von Berichtszeilen zurueck (ein dict je Handelstag).

    `tf` steuert nur Dateiname und Soll-/Lueckenrechnung -- die Handelstag-Zuordnung
    bleibt dieselbe, weil TradingView auch Tagesbalken auf den Sessionstart stempelt
    (Balken "12.08. 18:00" ist der Handelstag 13.08.).

    `nur_neu=True` ueberspringt jeden Handelstag, fuer den schon eine Datei existiert --
    ergaenzt also nur fehlende Tage, statt bestehende Balken zu revidieren. Gedacht fuer
    Quellen, die dieselbe Serie in anderer Qualitaet liefern: beim 1D-Import am 2026-08-14
    wichen TradingView und der yfinance-Bestand im Median nur +1,25 Punkte ab, an einzelnen
    Tagen aber um bis zu 600 (MNQ) bzw. 1370 (YM) -- solche Tage gehoeren angesehen, nicht
    pauschal ueberschrieben.
    """
    startstunde, soll = profil(symbol)
    if soll is not None:
        soll = max(1, soll * 60 // TF_SEKUNDEN[tf])  # 1m 1380 -> 5m 276, 1h 23, 1d 1
    neu = lies(exportdatei)

    nach_tag = {}
    for ts, ohlc in neu.items():
        tag = handelstag(ts, startstunde)
        # Auf 1d entscheidet der Handelstag, nicht die Uhrzeit: ein Tagesbalken ist pro Tag
        # eindeutig, und die Quellen stempeln ihn verschieden (siehe tagesstempel()). Ohne
        # diese Normalisierung mergen die beiden Konventionen nicht, sondern stehen
        # nebeneinander -- genau der Schaden vom 2026-08-14.
        nach_tag.setdefault(tag, {})[tagesstempel(tag) if tf == "1d" else ts] = ohlc

    bericht = []
    zu_schreiben = []
    for tag in sorted(nach_tag):
        pfad = zielpfad(symbol, tag, tf)
        if nur_neu and pfad.exists():
            continue
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
        # Der Merge laeuft ueber den rohen Zeitstempel -- das setzt voraus, dass Bestand und
        # Export dieselbe Stempelkonvention haben. Auf 1m stimmt das; auf 1d nicht: yfinance
        # stempelt den Tagesbalken auf 00:00 UTC, TradingView auf den Sessionstart 18:00 NY.
        # Ohne diese Sperre standen am 2026-08-14 in 5172 Tagesdateien zwei Balken fuer
        # denselben Handelstag (gemessen MNQ 13.08.: 18:00 und 20:00 NY, Close 22 Punkte
        # auseinander). Nicht automatisch aufloesen -- welcher Stempel gilt, ist eine
        # Entscheidung ueber den ganzen Bestand, kein Detail dieses einen Imports.
        if soll is not None and len(gemerged) > soll:
            zusatz = sorted(set(gemerged) - set(nach_tag[tag]))
            raise ValueError(
                f"{pfad.name}: {len(gemerged)} Kerzen bei Soll {soll} fuer {tf}. Bestand und "
                f"Export stempeln verschieden (Bestand u.a. {zusatz[:3]}, Export u.a. "
                f"{sorted(nach_tag[tag])[:3]}). Import abgebrochen, nichts geschrieben."
            )
        zeile = {
            "tag": tag,
            "vorher": len(alt),
            "hinzu": len(set(gemerged) - set(alt)),
            "gesamt": len(gemerged),
            "soll": soll,
            "vollstaendig": soll is not None and len(gemerged) >= soll,
            "luecken": luecken(ts_sortiert, TF_SEKUNDEN[tf]),
            "revidiert": abweichungen,
            "pfad": pfad,
        }
        bericht.append(zeile)
        zu_schreiben.append((pfad, gemerged))

    # Erst schreiben, wenn JEDER Tag die Pruefung bestanden hat -- sonst haette der Abbruch
    # oben die bereits verarbeiteten Tage schon veraendert zurueckgelassen.
    if schreiben:
        for pfad, gemerged in zu_schreiben:
            schreib(pfad, gemerged, symbol)
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

        # Timeframe landet im Dateinamen, sonst ueberschreibt ein 1d-Import die 1m-Datei
        tag = datetime.date(2026, 8, 13)
        assert zielpfad("MNQ", tag).name == "MNQ 2026-08-13 1m.csv", "Default bleibt 1m"
        assert zielpfad("MNQ", tag, "1d").name == "MNQ 2026-08-13 1d.csv", "tf muss in den Namen"

        # Soll skaliert mit dem Timeframe -- 1380 1m-Kerzen sind 276 5m-, 23 1h-, 1 Tagesbalken
        soll = profil("MNQ")[1]
        skaliert = {tf: max(1, soll * 60 // s) for tf, s in TF_SEKUNDEN.items()}
        assert (skaliert["1m"], skaliert["5m"], skaliert["1h"], skaliert["1d"]) == (1380, 276, 23, 1), skaliert

        # TradingView stempelt auch Tagesbalken auf den Sessionstart 18:00 NY des VORTAGS
        d = datetime.datetime(2026, 8, 12, 18, 0, tzinfo=NY)
        assert handelstag(int(d.timestamp()), 18) == datetime.date(2026, 8, 13), \
            "Tagesbalken '12.08. 18:00' gehoert zum Handelstag 13.08."

        # MES ist ein Futures-Kontrakt -- ohne Eintrag bekaeme er still das Forex-Profil (17:00)
        assert profil("MES1!") == PROFILE["futures"], "MES muss das Futures-Profil bekommen"

        # Der Schaden vom 2026-08-14: Bestand stempelt den Tagesbalken auf 00:00 UTC
        # (= 19:00/20:00 NY je nach Sommerzeit), TradingView auf den Sessionstart 18:00 NY.
        alt_raw = globals()["RAW"]
        try:
            globals()["RAW"] = Path(tmp) / "vault"
            tag13 = datetime.date(2026, 8, 13)
            bestand = zielpfad("MNQ", tag13, "1d")
            bestand.parent.mkdir(parents=True, exist_ok=True)
            yf_ts = tagesstempel(tag13)
            tv_ts = int(datetime.datetime(2026, 8, 12, 18, 0, tzinfo=NY).timestamp())
            assert yf_ts != tv_ts, "die beiden Konventionen muessen sich unterscheiden"
            assert yf_ts == int(datetime.datetime(2026, 8, 12, 20, 0, tzinfo=NY).timestamp()),                 "00:00 UTC ist im August 20:00 NY des Vortags"
            schreib(bestand, {yf_ts: ("1", "9", "0", "1")})

            # Sessionstart-Stempel im Export -> auf die Bestandskonvention normalisiert,
            # ergibt EINE Zeile mit Revision statt zweier Balken nebeneinander
            export = Path(tmp) / "tv1d.csv"
            schreib(export, {tv_ts: ("1", "9", "0", "9")})
            z = ingest(export, "MNQ", tf="1d")
            nachher = lies(bestand)
            assert list(nachher) == [yf_ts], f"genau ein Balken erwartet, waren {list(nachher)}"
            assert nachher[yf_ts][3] == "9", "neuer Export gewinnt"
            assert z[0]["revidiert"] == 1, "die Revision gehoert in den Bericht"

            # --nur-neue-tage laesst bestehende Tage komplett in Ruhe
            schreib(export, {tv_ts: ("7", "7", "7", "7")})
            z = ingest(export, "MNQ", tf="1d", nur_neu=True)
            assert z == [], "bestehender Tag darf gar nicht erst im Bericht auftauchen"
            assert lies(bestand)[yf_ts][3] == "9", "nur_neu darf den Bestand nicht anfassen"

            # ... legt aber fehlende Tage an, ebenfalls auf der Bestandskonvention
            tag14 = datetime.date(2026, 8, 14)
            schreib(export, {int(datetime.datetime(2026, 8, 13, 18, 0, tzinfo=NY).timestamp()):
                             ("1", "9", "0", "5")})
            z = ingest(export, "MNQ", tf="1d", nur_neu=True)
            neu_pfad = zielpfad("MNQ", tag14, "1d")
            assert z and z[0]["tag"] == tag14 and neu_pfad.exists(), "fehlender Tag muss entstehen"
            assert list(lies(neu_pfad)) == [tagesstempel(tag14)], "auch neu auf Bestandskonvention"

            # Die Sperre bleibt als Backstop scharf: mehr Kerzen als das Profil-Soll
            zuviel = Path(tmp) / "zuviel.csv"
            basis1m = int(datetime.datetime(2026, 8, 12, 18, 0, tzinfo=NY).timestamp())
            schreib(zuviel, {basis1m + i * 60: ("1", "9", "0", "1") for i in range(1381)})
            try:
                ingest(zuviel, "MNQ", tf="1m")
                raise AssertionError("mehr als 1380 1m-Kerzen an einem Tag muessen abbrechen")
            except ValueError as e:
                assert "stempeln verschieden" in str(e), f"falsche Fehlermeldung: {e}"
        finally:
            globals()["RAW"] = alt_raw

    print("ingest_tvexport: alle Selbstchecks bestanden")


if __name__ == "__main__":
    if "--demo" in sys.argv:
        demo()
    elif len(sys.argv) >= 3:
        import argparse

        ap = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
        ap.add_argument("exportdatei")
        ap.add_argument("symbol")
        ap.add_argument("--tf", default="1m", choices=sorted(TF_SEKUNDEN))
        ap.add_argument("--nur-neue-tage", action="store_true", dest="nur_neu",
                        help="nur fehlende Handelstage anlegen, bestehende nicht revidieren")
        a = ap.parse_args()
        for z in ingest(a.exportdatei, a.symbol, tf=a.tf, nur_neu=a.nur_neu):
            st = "VOLLSTAENDIG" if z["vollstaendig"] else (
                f"fehlen {z['soll'] - z['gesamt']}" if z["soll"] else "Soll unbekannt"
            )
            rev = f", {z['revidiert']} revidiert" if z["revidiert"] else ""
            print(f"{z['tag']}  {z['vorher']:5d} +{z['hinzu']:4d} -> {z['gesamt']:5d}  {st}"
                  f"  Luecken: {len(z['luecken'])}{rev}")
    else:
        print(__doc__)
