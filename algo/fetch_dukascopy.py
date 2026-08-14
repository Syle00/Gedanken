"""Laedt historische Devisen-Tickdaten von Dukascopy und aggregiert sie zu 1-Minuten-Kerzen.

Aufruf:
    python algo/fetch_dukascopy.py EURUSD --von 2026-08-01 --bis 2026-08-07
    python algo/fetch_dukascopy.py EURUSD GBPUSD USDJPY --von 2003-01-01 --bis 2026-08-07

Warum eigener Downloader statt Fremdbibliothek: Das Format ist simpel (LZMA + 20-Byte-Records),
alles Noetige steckt in der Standardbibliothek, und die Ausgabe muss ohnehin der Vault-Konvention
folgen (`time,open,high,low,close` mit echten UTC-Epoch-Sekunden). Eine Abhaengigkeit haette hier
mehr gekostet als sie spart.

Konventionen, bewusst gesetzt (siehe docs/superpowers/specs/2026-08-08-algo-zielbild-design.md):

* **OHLC aus dem Mittelkurs** (bid+ask)/2, nicht aus bid. Grund: IBKR liefert fuer Devisen
  standardmaessig Midpoint-Bars. Da IBKR laut Spec 4.5 die Validierungsstufe ist, muessen beide
  Quellen dieselbe Groesse messen, sonst ist der Abgleich wertlos. Der Spread wird als
  Zusatzspalte mitgeschrieben -- `csv.DictReader` in tools/analyze_ohlc.py liest nur benannte
  Spalten, zusaetzliche stoeren also nicht.
* **Echte UTC-Epoch-Sekunden**, geprueft gegen die bestehenden TradingView-Exporte.
* **Tagesordner nach NY-Kalenderdatum**, wie der uebrige Bestand. Die 17:00-NY-Grenze des
  Devisenhandelstags wird erst beim Ableiten von Tageskerzen angewendet, nicht schon beim
  Speichern -- eine Minutenkerze ist grenzenunabhaengig, und eine in die Ablage eingebackene
  Konvention waere spaeter nicht mehr korrigierbar.
* **Luecken werden protokolliert, nicht verschwiegen** (CLAUDE.md: Marktdaten wie Gold behandeln).

Ablage: raw/marktdaten-tief/<jjjj>/<mm>/<tt.mm.jjjj>/<SYMBOL> <jjjj-mm-tt> 1m.csv
Getrennt von raw/marktdaten/, weil das die zweite Datenstufe ist (Fremdquelle zur Erkundung).
⚠️ NICHT gitignored, trotz des Umfangs -- .gitignore versioniert raw/ bewusst vollstaendig
("Vault soll vollstaendig gesichert sein"). Der Kommentar hier stand lange falsch im Code, bis
der 10-Paare-Bulk-Import (2026-08-14, siehe PLAN.md) mit 73.100 Dateien / ~82 Mio. Zeilen in
einem Commit demonstrierte, dass es eben doch versioniert wird.
"""
from __future__ import annotations

import argparse
import csv
import json
import lzma
import struct
import sys
import time
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from analyze_ohlc import pruefe_kerzen  # noqa: E402

from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
OUT_ROOT = ROOT / "raw" / "marktdaten-tief"
NY = ZoneInfo("America/New_York")
URL = "https://datafeed.dukascopy.com/datafeed/{sym}/{y:04d}/{m:02d}/{d:02d}/{h:02d}h_ticks.bi5"

# Nachkommastellen je Symbol -> Umrechnungsfaktor der ganzzahligen Kurse im bi5-Format.
# JPY-Paare haben 3, alle uebrigen Majors 5.
DECIMALS = {
    "EURUSD": 5, "GBPUSD": 5, "AUDUSD": 5, "NZDUSD": 5,
    "USDCHF": 5, "USDCAD": 5, "USDSEK": 5, "EURGBP": 5,
    "USDJPY": 3, "EURJPY": 3, "GBPJPY": 3,
}
REC = struct.Struct(">3I2f")  # ms-Offset, ask, bid, ask-Volumen, bid-Volumen (Big-Endian)


def hole_stunde(sym: str, tag: date, stunde: int, versuche: int = 5) -> bytes | None:
    """Rohe bi5-Bytes einer Stunde. None = kein Datenfile (Wochenende/Feiertag/Luecke).

    Achtung, klassische Falle: Dukascopy zaehlt Monate ab 0. Ein Off-by-one hier verschiebt
    saemtliche Daten um einen Monat, ohne dass irgendetwas auffaellig aussieht.

    429 (Too Many Requests) bekommt eine deutlich laengere Pause als andere Fehler -- ein
    Bulk-Lauf ueber 10 Paare x 23 Jahre hat den Server vorher in die Rate-Limitierung getrieben
    (kurze 2**versuch-Backoffs reichen dagegen nicht).
    """
    url = URL.format(sym=sym, y=tag.year, m=tag.month - 1, d=tag.day, h=stunde)
    for versuch in range(versuche):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if e.code == 429:
                if versuch == versuche - 1:
                    raise
                time.sleep(15 * (versuch + 1))
                continue
            if versuch == versuche - 1:
                raise
        except (urllib.error.URLError, TimeoutError):
            if versuch == versuche - 1:
                raise
        time.sleep(2 ** versuch)
    return None


def dekodiere(roh: bytes, sym: str, tag: date, stunde: int) -> list[tuple[float, float, float]]:
    """bi5 -> [(epoch_sekunden, mid, spread), ...]"""
    if not roh:
        return []
    try:
        daten = lzma.LZMADecompressor(format=lzma.FORMAT_ALONE).decompress(roh)
    except lzma.LZMAError:
        daten = lzma.LZMADecompressor(format=lzma.FORMAT_AUTO).decompress(roh)

    faktor = 10 ** DECIMALS[sym]
    basis = datetime(tag.year, tag.month, tag.day, stunde, tzinfo=timezone.utc).timestamp()
    ticks = []
    for (ms, ask_i, bid_i, _av, _bv) in REC.iter_unpack(daten[: len(daten) - len(daten) % REC.size]):
        ask, bid = ask_i / faktor, bid_i / faktor
        if bid <= 0 or ask <= 0:
            continue
        ticks.append((basis + ms / 1000.0, (bid + ask) / 2.0, ask - bid))
    return ticks


def zu_minutenkerzen(ticks: list[tuple[float, float, float]]) -> dict[int, dict]:
    kerzen: dict[int, dict] = {}
    for ts, mid, spread in ticks:
        minute = int(ts // 60) * 60
        k = kerzen.get(minute)
        if k is None:
            kerzen[minute] = {"open": mid, "high": mid, "low": mid, "close": mid,
                              "spread_sum": spread, "n": 1}
        else:
            if mid > k["high"]:
                k["high"] = mid
            if mid < k["low"]:
                k["low"] = mid
            k["close"] = mid
            k["spread_sum"] += spread
            k["n"] += 1
    return kerzen


def schreibe_tag(sym: str, ny_tag: date, kerzen: dict[int, dict]) -> Path:
    ordner = OUT_ROOT / f"{ny_tag.year:04d}" / f"{ny_tag.month:02d}" / ny_tag.strftime("%d.%m.%Y")
    ordner.mkdir(parents=True, exist_ok=True)
    ziel = ordner / f"{sym} {ny_tag.isoformat()} 1m.csv"
    for hinweis in pruefe_kerzen(
            ((m, kerzen[m]["open"], kerzen[m]["high"], kerzen[m]["low"], kerzen[m]["close"])
             for m in sorted(kerzen)), sym, ziel.name):
        print(f"  ? {hinweis}")
    with ziel.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["time", "open", "high", "low", "close", "spread"])
        for minute in sorted(kerzen):
            k = kerzen[minute]
            w.writerow([minute,
                        f"{k['open']:.6f}", f"{k['high']:.6f}",
                        f"{k['low']:.6f}", f"{k['close']:.6f}",
                        f"{k['spread_sum'] / k['n']:.6f}"])
    return ziel


def lade_symbol(sym: str, von: date, bis: date, ueberspringe_vorhandene: bool = True,
                pause: float = 0.5) -> dict:
    """Laedt einen Zeitraum. Gruppiert nach NY-Kalendertag, weil eine UTC-Stunde in den
    NY-Vortag fallen kann.

    `pause` bremst proaktiv zwischen JEDER Stundenabfrage (nicht nur nach Fehlern) -- der
    vorherige Bulk-Lauf ueber 10 Paare x 23 Jahre hat Dukascopy ohne Drosselung angefragt und
    wurde mit HTTP 429 blockiert.
    """
    if sym not in DECIMALS:
        sys.exit(f"Unbekanntes Symbol {sym}. Bekannt: {', '.join(sorted(DECIMALS))}")

    bericht = {"symbol": sym, "tage_geschrieben": 0, "kerzen": 0,
               "leere_stunden": 0, "tage_ohne_daten": [], "fehler": []}
    puffer: dict[date, list[tuple[float, float, float]]] = {}
    tag = von
    while tag <= bis:
        for stunde in range(24):
            try:
                roh = hole_stunde(sym, tag, stunde)
            except Exception as e:  # Netzfehler nach allen Versuchen
                bericht["fehler"].append(f"{tag} {stunde:02d}h: {e}")
                time.sleep(pause)
                continue
            time.sleep(pause)
            if not roh:
                bericht["leere_stunden"] += 1
                continue
            for ts, mid, spread in dekodiere(roh, sym, tag, stunde):
                ny_tag = datetime.fromtimestamp(ts, NY).date()
                puffer.setdefault(ny_tag, []).append((ts, mid, spread))

        # Alle NY-Tage schreiben, die sicher abgeschlossen sind (vor dem aktuellen UTC-Tag)
        for ny_tag in sorted([d for d in puffer if d < tag]):
            ticks = puffer.pop(ny_tag)
            kerzen = zu_minutenkerzen(ticks)
            if kerzen:
                schreibe_tag(sym, ny_tag, kerzen)
                bericht["tage_geschrieben"] += 1
                bericht["kerzen"] += len(kerzen)
        tag += timedelta(days=1)

    for ny_tag in sorted(puffer):
        kerzen = zu_minutenkerzen(puffer[ny_tag])
        if kerzen:
            schreibe_tag(sym, ny_tag, kerzen)
            bericht["tage_geschrieben"] += 1
            bericht["kerzen"] += len(kerzen)
    return bericht


def _demo() -> None:
    """Selbstcheck ohne Netz -- prueft Dekodierung und Aggregation gegen erfundene Ticks."""
    m0 = 1_700_000_040          # echte Minutengrenze: durch 60 teilbar
    assert m0 % 60 == 0
    ticks = [
        (m0 + 0.0,  1.1000, 0.00002),   # Minute 0, Open
        (m0 + 30.0, 1.1010, 0.00004),   # Minute 0, High
        (m0 + 59.9, 1.0990, 0.00003),   # Minute 0, Low + Close
        (m0 + 60.0, 1.2000, 0.00001),   # Minute 1 -- darf die erste Kerze nicht beruehren
    ]
    k = zu_minutenkerzen(ticks)
    assert len(k) == 2, k
    erste = k[m0]
    assert erste["open"] == 1.1000 and erste["close"] == 1.0990, erste
    assert erste["high"] == 1.1010 and erste["low"] == 1.0990, erste
    assert abs(erste["spread_sum"] / erste["n"] - 0.00003) < 1e-9
    assert k[m0 + 60]["open"] == 1.2000

    # Monat MUSS 0-basiert in die URL -- der haeufigste Fehler bei dieser Schnittstelle
    u = URL.format(sym="EURUSD", y=2026, m=8 - 1, d=5, h=13)
    assert "/2026/07/05/13h_ticks.bi5" in u, u

    # 20-Byte-Records, Big-Endian
    assert REC.size == 20
    print("fetch_dukascopy: Selbstcheck ok")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("symbole", nargs="*", help="z.B. EURUSD GBPUSD USDJPY")
    ap.add_argument("--von", help="JJJJ-MM-TT")
    ap.add_argument("--bis", help="JJJJ-MM-TT")
    ap.add_argument("--bericht", help="Pfad fuer einen JSON-Bericht")
    ap.add_argument("--pause", type=float, default=0.5,
                     help="Sekunden Pause zwischen Stundenabfragen (Default 0.5, gegen HTTP 429)")
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
              f"{b['leere_stunden']} leere Stunden, {len(b['fehler'])} Fehler", flush=True)

    if a.bericht:
        Path(a.bericht).write_text(json.dumps(berichte, indent=2, default=str), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
