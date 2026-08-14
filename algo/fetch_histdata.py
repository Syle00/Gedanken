"""Laedt historische 1-Minuten-FX-Kerzen von histdata.com (Ersatz fuer fetch_dukascopy.py,
das per IP gesperrt ist -- siehe algo/PLAN.md).

Aufruf:
    python algo/fetch_histdata.py EURUSD --von 2020-01-01 --bis 2020-12-31
    python algo/fetch_histdata.py EURUSD GBPUSD --von 2003-01-01 --bis 2026-08-01

Warum eigener Downloader statt des `histdata`-Pip-Pakets: Das Paket macht nur zwei HTTP-Schritte
(Token aus einer versteckten Formular-`tk`-Eingabe scrapen, dann POST) -- das ist mit stdlib
(urllib + re) in wenigen Zeilen nachgebaut, ohne die Abhaengigkeiten `requests`+`bs4` zu ziehen.

Wichtige Eigenheit, per Abgleich gegen TradingView-1h-Exporte in raw/marktdaten/ verifiziert
(Layer 0 Nulltoleranz-Pflicht, CLAUDE.md "Zeit vor Preis"): Die eigene histdata.com-FAQ behauptet
fuer alle Downloads eine feste Eastern Time OHNE Sommerzeit-Umstellung (ganzjaehrig UTC-5) -- das
stimmt nachweislich fuer die manuell abgelegten Legacy-XLSX-Exporte (siehe
`ingest_histdata_xlsx.py`, dort an den Jahr-2000-Daten verifiziert), **aber nicht fuer diesen
Live-ASCII-Endpoint** (`get.php`), egal ob Jahres- oder Monats-Chunk: An zwei unabhaengigen
Sommertagen (2025-07-01, 2026-07-01) lag eine feste +5h-Verschiebung durchgaengig 1h daneben,
ein Winter-Test (2026-01-05) passte dagegen exakt -- klassisches DST-Muster. Dieser Endpoint
liefert also echte America/New_York-Ortszeit inkl. Sommerzeit, nicht die fixe EST der Legacy-
Daten. Deshalb hier zoneinfo-basierte Konvertierung, nicht die feste Verschiebung aus
`ingest_histdata_xlsx.py`.

histdata.com liefert **Bid**-Preise, nicht Mid (siehe eigene FAQ: "the bar prices ... are based
on the tick Bid price.") -- anders als fetch_dukascopy.py, das bewusst Mid nutzt (IBKR liefert FX
als Midpoint-Bars). Deshalb wie im bereits bestehenden `ingest_histdata_xlsx.py` (manueller
XLSX-Import, gleiche EST-Verschiebung, gleiche Ablage) der eigene Dateisuffix ` 1m (bid).csv`
-- damit Bid- und Mid-Bestand nie versehentlich vermischt werden.

Ablage: raw/marktdaten-tief/<jjjj>/<mm>/<tt.mm.jjjj>/<SYMBOL> <jjjj-mm-tt> 1m (bid).csv
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from analyze_ohlc import pruefe_kerzen  # noqa: E402

from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
OUT_ROOT = ROOT / "raw" / "marktdaten-tief"
NY = ZoneInfo("America/New_York")

REFERER_PREFIX = "https://www.histdata.com/download-free-forex-historical-data/?/ascii/1-minute-bar-quotes/"
POST_URL = "https://www.histdata.com/get.php"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
TOKEN_RE = re.compile(
    r'id=["\']tk["\'][^>]*value=["\']([^"\']+)["\']'
    r'|value=["\']([^"\']+)["\'][^>]*id=["\']tk["\']'
)


def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def hole_monat(pair: str, jahr: int, monat: int | None) -> bytes:
    """Ein Jahres- (monat=None) oder Monats-Zip von histdata.com.

    histdata erlaubt fuer vergangene Jahre nur den Jahres-Bulk (monat=None); fuers laufende Jahr
    muss man monatsweise anfragen -- siehe api.py des `histdata`-Pip-Pakets, dessen Zwei-Schritt-
    Ablauf (Token holen, dann POST) hier nachgebaut ist.
    """
    referer = REFERER_PREFIX + f"{pair.lower()}/{jahr}"
    if monat is not None:
        referer += f"/{monat}"
    html = _get(referer).decode("utf-8", errors="replace")
    m = TOKEN_RE.search(html)
    if not m:
        raise RuntimeError(f"Kein Token gefunden fuer {pair} {jahr}/{monat} -- Seite geaendert "
                           f"oder Paar/Jahr ungueltig ({referer})")
    token = m.group(1) or m.group(2)

    datemonth = f"{jahr}{monat:02d}" if monat is not None else str(jahr)
    daten = urllib.parse.urlencode({
        "tk": token, "date": str(jahr), "datemonth": datemonth,
        "platform": "ASCII", "timeframe": "M1", "fxpair": pair.upper(),
    }).encode("ascii")
    req = urllib.request.Request(POST_URL, data=daten, headers={
        "User-Agent": UA, "Referer": referer,
        "Content-Type": "application/x-www-form-urlencoded",
    })
    with urllib.request.urlopen(req, timeout=60) as r:
        inhalt = r.read()
    if not inhalt.startswith(b"PK"):
        raise RuntimeError(f"Keine Zip-Antwort fuer {pair} {jahr}/{monat} "
                           f"(evtl. keine Daten fuer diesen Zeitraum): {inhalt[:200]!r}")
    return inhalt


def parse_zip(zip_bytes: bytes) -> list[tuple[float, float, float, float, float]]:
    """Zip -> [(epoch_utc, open, high, low, close), ...], histdata liefert schon fertige 1m-Bars.

    histdata.com selbst liefert vereinzelt einen kompletten Stundenblock doppelt (verifiziert an
    EURUSD 2019-10-27 19:00-19:59 lokal, wortwoertlich zweimal im Rohdatensatz) -- echter Fehler
    der Quelle, keiner der Konvertierung. Dedup statt Absturz, aber unterschiedliche Werte am
    gleichen Zeitstempel waeren ein staerkeres Datenproblem und werden separat gezaehlt/gemeldet."""
    zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    [name] = [n for n in zf.namelist() if n.lower().endswith(".csv")]
    gesehen: dict[float, tuple[float, float, float, float]] = {}
    duplikate = konflikte = 0
    with zf.open(name) as fh:
        for zeile in io.TextIOWrapper(fh, encoding="ascii"):
            zeile = zeile.strip()
            if not zeile:
                continue
            ts_str, o, h, l, c, *_rest = zeile.split(";")
            lokal = datetime.strptime(ts_str, "%Y%m%d %H%M%S").replace(tzinfo=NY)
            epoch = lokal.timestamp()
            werte = (float(o), float(h), float(l), float(c))
            vorherige = gesehen.get(epoch)
            if vorherige is not None:
                duplikate += 1
                if vorherige != werte:
                    konflikte += 1
                continue
            gesehen[epoch] = werte
    if duplikate:
        hinweis = f"{duplikate} doppelte Zeitstempel im histdata-Rohdatensatz uebersprungen"
        if konflikte:
            hinweis += f", davon {konflikte} mit ABWEICHENDEN Werten (nicht nur Duplikat!)"
        print(f"  ? {hinweis}")
    return [(ts, *werte) for ts, werte in gesehen.items()]


def schreibe_tag(sym: str, ny_tag: date, bars: list[tuple[float, float, float, float, float]]) -> Path:
    ordner = OUT_ROOT / f"{ny_tag.year:04d}" / f"{ny_tag.month:02d}" / ny_tag.strftime("%d.%m.%Y")
    ordner.mkdir(parents=True, exist_ok=True)
    ziel = ordner / f"{sym} {ny_tag.isoformat()} 1m (bid).csv"
    zeilen = sorted(bars)  # (epoch, o, h, l, c), epoch ist bereits die Minutengrenze
    for hinweis in pruefe_kerzen(
            ((int(ts), o, h, l, c) for ts, o, h, l, c in zeilen), sym, ziel.name):
        print(f"  ? {hinweis}")
    with ziel.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["time", "open", "high", "low", "close"])
        for ts, o, h, l, c in zeilen:
            w.writerow([int(ts), f"{o:.6f}", f"{h:.6f}", f"{l:.6f}", f"{c:.6f}"])
    return ziel


def monatsketten(von: date, bis: date) -> list[tuple[int, int | None]]:
    """Welche (jahr, monat)-Chunks muessen bei histdata angefragt werden, um [von, bis]
    abzudecken -- ein Chunk pro Jahr, ausser dem laufenden Jahr (dort nur einzelne Monate)."""
    heute_jahr = date.today().year
    chunks: list[tuple[int, int | None]] = []
    for jahr in range(von.year, bis.year + 1):
        if jahr < heute_jahr:
            chunks.append((jahr, None))
        else:
            start_m = von.month if jahr == von.year else 1
            end_m = bis.month if jahr == bis.year else 12
            for monat in range(start_m, end_m + 1):
                chunks.append((jahr, monat))
    return chunks


def lade_symbol(sym: str, von: date, bis: date, pause: float = 1.0) -> dict:
    bericht = {"symbol": sym, "tage_geschrieben": 0, "kerzen": 0, "fehler": []}
    tage: dict[date, list] = {}
    for jahr, monat in monatsketten(von, bis):
        try:
            zip_bytes = hole_monat(sym, jahr, monat)
            for epoch, o, h, l, c in parse_zip(zip_bytes):
                ny_tag = datetime.fromtimestamp(epoch, NY).date()
                if von <= ny_tag <= bis:
                    tage.setdefault(ny_tag, []).append((epoch, o, h, l, c))
        except Exception as e:
            bericht["fehler"].append(f"{jahr}/{monat}: {e}")
        time.sleep(pause)

    for ny_tag in sorted(tage):
        schreibe_tag(sym, ny_tag, tage[ny_tag])
        bericht["tage_geschrieben"] += 1
        bericht["kerzen"] += len(tage[ny_tag])
    return bericht


def _demo() -> None:
    """Selbstcheck ohne Netz: Token-Regex, EST->UTC-Verschiebung, Zeilenformat, Chunk-Planung."""
    html_a = '<input type="hidden" id="tk" value="abc123">'
    html_b = '<input type="hidden" value="xyz789" id="tk">'
    assert TOKEN_RE.search(html_a).group(1) == "abc123"
    m = TOKEN_RE.search(html_b)
    assert (m.group(1) or m.group(2)) == "xyz789"

    # Winter (kein DST): 09:30 NY-Ortszeit = EST = UTC-5 -> 14:30 UTC
    lokal_winter = datetime.strptime("20200102 093000", "%Y%m%d %H%M%S").replace(tzinfo=NY)
    utc_winter = datetime.fromtimestamp(lokal_winter.timestamp(), timezone.utc)
    assert utc_winter.hour == 14 and utc_winter.minute == 30, utc_winter

    # Sommer (DST aktiv): 09:30 NY-Ortszeit = EDT = UTC-4 -> 13:30 UTC (nicht 14:30 wie bei
    # fester EST -- das war genau der per Abgleich gefundene Bug, siehe Modul-Docstring)
    lokal_sommer = datetime.strptime("20250701 093000", "%Y%m%d %H%M%S").replace(tzinfo=NY)
    utc_sommer = datetime.fromtimestamp(lokal_sommer.timestamp(), timezone.utc)
    assert utc_sommer.hour == 13 and utc_sommer.minute == 30, utc_sommer

    zeile = "20200102 093000;1.11000;1.11050;1.10990;1.11020;0"
    ts_str, o, h, l, c, vol = zeile.split(";")
    assert float(o) == 1.11000 and float(c) == 1.11020

    ch = monatsketten(date(2019, 6, 15), date(2020, 3, 10))
    heute_jahr = date.today().year
    if heute_jahr > 2020:
        assert ch == [(2019, None), (2020, None)], ch

    # Dedup: histdata.com liefert manchmal einen Block doppelt (siehe parse_zip-Docstring) --
    # exaktes Duplikat wird stillschweigend uebersprungen, ein WIDERSPRECHENDES Duplikat (gleicher
    # Zeitstempel, andere Werte) muss trotzdem als Konflikt gezaehlt werden statt eine der beiden
    # Versionen unbemerkt zu verwerfen.
    fake_csv = (
        "20200102 093000;1.1;1.1;1.1;1.1;0\n"
        "20200102 093100;1.2;1.2;1.2;1.2;0\n"
        "20200102 093000;1.1;1.1;1.1;1.1;0\n"   # exaktes Duplikat -> uebersprungen
        "20200102 093100;1.9;1.9;1.9;1.9;0\n"   # Konflikt: gleicher ts, andere Werte
    )
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("DAT_ASCII_TEST_M1_2020.csv", fake_csv)
    bars = parse_zip(buf.getvalue())
    assert len(bars) == 2, bars  # nicht 4 -- Duplikate raus

    print("fetch_histdata: Selbstcheck ok")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("symbole", nargs="*", help="z.B. EURUSD GBPUSD")
    ap.add_argument("--von", help="JJJJ-MM-TT")
    ap.add_argument("--bis", help="JJJJ-MM-TT")
    ap.add_argument("--bericht", help="Pfad fuer einen JSON-Bericht")
    ap.add_argument("--pause", type=float, default=1.0,
                     help="Sekunden Pause zwischen Chunk-Downloads (Default 1.0)")
    ap.add_argument("--demo", action="store_true", help="Nur Selbstcheck, kein Netzzugriff")
    a = ap.parse_args()

    if a.demo or not a.symbole:
        _demo()
        return 0
    if not (a.von and a.bis):
        sys.exit("--von und --bis werden gebraucht")

    von, bis = date.fromisoformat(a.von), date.fromisoformat(a.bis)
    berichte = []
    for sym in a.symbole:
        print(f"[{sym}] {von} .. {bis}", flush=True)
        b = lade_symbol(sym, von, bis, pause=a.pause)
        berichte.append(b)
        print(f"  {b['tage_geschrieben']} Tage, {b['kerzen']} Minutenkerzen, "
              f"{len(b['fehler'])} Fehler", flush=True)

    if a.bericht:
        Path(a.bericht).write_text(json.dumps(berichte, indent=2, default=str), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
