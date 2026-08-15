#!/usr/bin/env python3
"""Laedt sekundengenaue OHLC-Daten fuer NQ und ES ueber die IBKR-TWS/Gateway-API und legt sie
im bestehenden raw/marktdaten/-Baum als Tages-Parquet ab (Schema wie das TradingView-CSV,
plus volume/contract). Siehe docs/superpowers/specs/2026-08-15-ibkr-1s-datenanbindung-design.md.

Drei Betriebsarten:
    python algo/fetch_ibkr.py --verify [--symbol NQ]      # ein 30-Min-Fenster, schreibt nichts
    python algo/fetch_ibkr.py --backfill 2026-02-17 2026-08-14
    python algo/fetch_ibkr.py                             # Nachlad: letzter Registereintrag bis gestern

Verbindet sich ausschliesslich readonly gegen Port 4002 (Paper-Gateway) -- dieser Datenpfad
hat konstruktionsbedingt keinen Weg zu echtem Kapital (Spec Design SS9).
"""
from __future__ import annotations

import argparse
import csv
import os
import socket
import subprocess
import sys
import time
from collections import deque
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from analyze_ohlc import pruefe_kerzen, OHLCDefekt  # noqa: E402

NY = ZoneInfo("America/New_York")
UTC = ZoneInfo("UTC")
DATA_DIR = Path(__file__).resolve().parent.parent / "raw" / "marktdaten"
REGISTER = DATA_DIR / "1s-abdeckung.csv"
REGISTER_HEADER = ["symbol", "von", "bis", "kontrakt", "kerzen", "geholt_am"]
SYMBOLS = ["NQ", "ES"]
WINDOW_SECONDS = 1800
GATEWAY_HOST, GATEWAY_PORT = "127.0.0.1", 4002
# Ueberschreibbar per Umgebungsvariable, falls IBC mal an einem anderen Ort installiert wird.
GATEWAY_BAT = Path(os.environ.get("IBC_GATEWAY_BAT", r"C:\Users\janne\IBC\StartGateway.bat"))


def _gateway_erreichbar(timeout: float = 1.0) -> bool:
    try:
        with socket.create_connection((GATEWAY_HOST, GATEWAY_PORT), timeout=timeout):
            return True
    except OSError:
        return False


def _gateway_sicherstellen(wartezeit: int = 180) -> None:
    """Startet IB Gateway automatisch ueber StartGateway.bat, falls Port 4002 noch nicht
    erreichbar ist -- damit `python fetch_ibkr.py` nicht voraussetzt, dass Gateway schon
    manuell laeuft. Wartet bis zu `wartezeit` Sekunden auf den IBC-Login (Cold-Start dauert
    ein paar Sekunden bis Minuten). Laeuft Gateway schon, passiert nichts."""
    if _gateway_erreichbar():
        return
    if not GATEWAY_BAT.exists():
        print(f"! Gateway nicht erreichbar und {GATEWAY_BAT} existiert nicht -- "
              f"bitte manuell starten oder IBC_GATEWAY_BAT setzen", flush=True)
        return
    print(f"Gateway auf Port {GATEWAY_PORT} nicht erreichbar, starte {GATEWAY_BAT} ...", flush=True)
    # cwd explizit auf den IBC-Ordner setzen (leerzeichenfrei) -- ohne das erbt der
    # Kindprozess das CWD von Python, hier der Repo-Pfad mit Leerzeichen ("...\Ablage 1\...").
    # StartGateway.bat/StartIBC.bat parsen intern u.a. die Java-Version ueber ein `for /f`
    # mit Backtick-Befehlssubstitution -- das bricht bei einem Leerzeichen im CWD mit
    # "'set' kann syntaktisch an dieser Stelle nicht verarbeitet werden" ab, noch bevor
    # Gateway selbst startet (Realfall 2026-08-15: Fenster oeffnet sich, aber IBKR kommt nie).
    subprocess.Popen([str(GATEWAY_BAT)], cwd=str(GATEWAY_BAT.parent),
                      creationflags=subprocess.CREATE_NEW_CONSOLE)
    start = time.monotonic()
    while time.monotonic() - start < wartezeit:
        if _gateway_erreichbar():
            print(f"Gateway erreichbar nach {time.monotonic() - start:.0f}s.", flush=True)
            return
        time.sleep(5)
    print(f"! Gateway nach {wartezeit}s immer noch nicht erreichbar -- "
          f"Verbindungsversuch trotzdem, wird vermutlich fehlschlagen", flush=True)

# Verfallsmonate NQ/ES: H (Maerz), M (Juni), U (September), Z (Dezember).
QUARTER_MONTHS = [(3, "H"), (6, "M"), (9, "U"), (12, "Z")]
_MONTH_NUM = {code: month for month, code in QUARTER_MONTHS}


def _future_contract(contract: str, symbol: str):
    """Baut ein ib_async-Future-Objekt aus dem Kontrakt-Code (z.B. 'NQU2026', 'NQ') --
    reqHistoricalData braucht ein Contract-Objekt, keinen blossen String. includeExpired=True
    ist Pflicht fuer den Backfill ueber bereits verfallene Kontrakte (Design SS3.2)."""
    from ib_async import Future
    code = contract[len(symbol)]
    year = contract[len(symbol) + 1:]
    month = _MONTH_NUM[code]
    return Future(symbol=symbol, lastTradeDateOrContractMonth=f"{year}{month:02d}",
                  exchange="CME", includeExpired=True)


def _third_friday(year: int, month: int) -> date:
    d = date(year, month, 1)
    first_friday = d + timedelta(days=(4 - d.weekday()) % 7)
    return first_friday + timedelta(weeks=2)


def front_month(d: date, symbol: str) -> str:
    """Front-Monat-Kontrakt (z.B. 'NQU2026') fuer Datum `d`: der erste Quartalskontrakt,
    dessen Roll-Termin (Verfall - 8 Tage) nach `d` liegt. Deterministisch, netzfrei."""
    for year in (d.year, d.year + 1):
        for month, code in QUARTER_MONTHS:
            verfall = _third_friday(year, month)
            roll = verfall - timedelta(days=8)
            if roll > d:
                return f"{symbol}{code}{year}"
    raise ValueError(f"kein Front-Monat fuer {d} gefunden")


class PacingLimiter:
    """IBKR-Pacing: max. `max_requests` je `window` Sekunden, mindestens `min_gap`
    Sekunden zwischen zwei Requests. `clock`/`sleep` sind injizierbar, damit Tests ohne
    echtes Warten laufen.

    `min_gap`-Default 1.5s statt der urspruenglich angenommenen 0.5s (Review-Fund
    2026-08-15): 0.5s haette rechnerisch die "6 Requests je 2s fuer denselben
    Kontrakt"-Regel (Design SS3.3) mit Reserve einhalten sollen, in der Praxis kamen beim
    echten Backfill-Testlauf trotzdem wiederholt Pacing-Violations (Error 162), meist in
    der zweiten Haelfte eines 46-Fenster-Laufs. 1.5s gibt deutlich mehr Puffer, auf Kosten
    von mehr Laufzeit (46 Fenster ~= 69s statt ~23s pro Symbol -- fuer einen 34h-Backfill
    vernachlaessigbar gegen die Kosten eines abgebrochenen Laufs)."""

    def __init__(self, clock=time.monotonic, sleep=time.sleep,
                 max_requests: int = 60, window: float = 600.0, min_gap: float = 1.5):
        self._clock = clock
        self._sleep = sleep
        self._max = max_requests
        self._window = window
        self._min_gap = min_gap
        self._times: deque[float] = deque(maxlen=max_requests)

    def wait(self) -> None:
        now = self._clock()
        if self._times and now - self._times[-1] < self._min_gap:
            self._sleep(self._min_gap - (now - self._times[-1]))
        if len(self._times) == self._max:
            wait_for = self._window - (self._clock() - self._times[0])
            if wait_for > 0:
                self._sleep(wait_for)
        self._times.append(self._clock())


def day_windows(day: date) -> list[tuple[datetime, datetime]]:
    """46 Fenster a 30 Minuten: 18:00 NY des Vortages bis 17:00 NY `day`, als UTC-Paare.
    Anker werden EINMAL nach UTC konvertiert, danach laeuft die gesamte Fenster-Arithmetik
    in UTC (timedelta-Addition auf einer NY-tz-awaren Datetime wuerde am DST-Fold sonst ein
    90-Minuten-Fenster statt zweier 30-Minuten-Fenster erzeugen, weil fold=0 den mehrdeutigen
    Stunden-Block auch nach dem Wechsel noch auf EDT aufloest)."""
    start_ny = datetime.combine(day - timedelta(days=1), datetime.min.time(), tzinfo=NY).replace(hour=18)
    end_ny = datetime.combine(day, datetime.min.time(), tzinfo=NY).replace(hour=17)
    start_utc, end_utc = start_ny.astimezone(UTC), end_ny.astimezone(UTC)
    out = []
    cur = start_utc
    while cur < end_utc:
        nxt = cur + timedelta(seconds=WINDOW_SECONDS)
        out.append((cur, nxt))
        cur = nxt
    return out


def register_load(path: Path = REGISTER) -> set[tuple[str, int, int]]:
    """(symbol, von, bis) aller bereits erfolgreich geholten Fenster, als UNIX-Sekunden."""
    if not path.exists():
        return set()
    with path.open(newline="", encoding="utf-8") as fh:
        return {(r["symbol"], int(r["von"]), int(r["bis"])) for r in csv.DictReader(fh)}


def register_append(rows: list[dict], path: Path = REGISTER) -> None:
    """Haengt Zeilen an -- schreibt den Header nur, wenn die Datei neu angelegt wird."""
    neu = not path.exists()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=REGISTER_HEADER)
        if neu:
            w.writeheader()
        w.writerows(rows)


def write_day_1s(symbol: str, day: date, rows: pd.DataFrame, contract: str) -> Path | None:
    """Schreibt eine Tagesdatei als Parquet, niemals ueberschreibend (wie
    fetch_yfinance.write_day()). Fuehrt vorher das Nulltoleranz-Gate aus -- wirft es
    OHLCDefekt, entsteht keine Datei (Aufrufer faengt das ab, siehe fetch_symbol_day)."""
    dest = (DATA_DIR / f"{day:%Y}" / f"{day:%m}" / f"{day:%d.%m.%Y}"
            / f"{symbol} {day.isoformat()} 1s.parquet")
    if dest.exists():
        return None
    for hinweis in pruefe_kerzen(
            rows[["time", "open", "high", "low", "close"]].itertuples(index=False, name=None),
            symbol, str(dest.name)):
        print(f"  ? {hinweis}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    out = rows.copy()
    out["contract"] = contract
    out.to_parquet(dest, index=False)
    return dest


def fetch_window(ib, contract: str, symbol: str, end_utc: datetime, pacing: PacingLimiter,
                  sleep=time.sleep) -> pd.DataFrame | None:
    """Ein 30-Minuten-Fenster ueber `ib.reqHistoricalData`. `ib` ist injizierbar (echter
    ib_async.IB im CLI-Pfad, Stub in Tests). formatDate=2 liefert UNIX-Sekunden UTC direkt --
    keine Zeitzonen-Umrechnung noetig (schaedlichster Fehlertyp dieses Projekts, siehe
    CLAUDE.md 'Zeit vor Preis').

    Bis zu 3 Versuche mit mind. 15s Abstand (Spec SS4: Pacing-Violations/transiente Fehler
    duerfen einen 34h-Backfill nicht abbrechen). IBKR meldet einen Fehlschlag (z.B. Error 162
    "pacing violation") NICHT als Python-Exception, sondern nur ueber `ib.errorEvent` --
    `reqHistoricalData` liefert dabei ganz normal eine leere Liste zurueck, ununterscheidbar
    von einem Fenster ohne Trades. Realfall 2026-08-15: 3 ES-Fenster wurden nach einer
    Pacing-Violation stillschweigend als "0 Kerzen, kein Trade" ins Register geschrieben und
    waeren nie wieder nachgeholt worden -- eine 90-Minuten-Luecke, die als erledigt galt.
    Deshalb: `errorEvent` waehrend des Requests mitschneiden; kommt ein Fehler UND die
    Antwort ist leer, gilt der Versuch als fehlgeschlagen, nicht als "kein Trade". Gibt nach
    3 gescheiterten Versuchen `None` zurueck (nicht einen leeren DataFrame) -- der Aufrufer
    (fetch_symbol_day) darf ein `None`-Fenster NICHT ins Register schreiben, sonst gilt die
    Luecke faelschlich als prueft-und-leer statt als offen."""
    future = _future_contract(contract, symbol)
    for versuch in range(1, 4):
        pacing.wait()
        fehler: list[tuple[int, str]] = []

        def _on_error(reqId, errorCode, errorString, errContract, fehler=fehler):
            fehler.append((errorCode, errorString))

        ib.errorEvent += _on_error
        try:
            bars = ib.reqHistoricalData(
                future, endDateTime=end_utc, durationStr=f"{WINDOW_SECONDS} S",
                barSizeSetting="1 secs", whatToShow="TRADES", useRTH=False, formatDate=2)
        except Exception as exc:
            fehler.append((-1, str(exc)))
            bars = []
        finally:
            ib.errorEvent -= _on_error

        if bars or not fehler:
            break
        print(f"  ! {symbol} Fenster bis {end_utc}: Versuch {versuch}/3 fehlgeschlagen ({fehler})")
        if versuch == 3:
            print(f"  ! {symbol} Fenster bis {end_utc}: nach 3 Versuchen aufgegeben -- "
                  f"NICHT registriert, wird beim naechsten Lauf erneut versucht")
            return None
        sleep(15.0)
    rows = [{"time": int(b.date.timestamp()) if hasattr(b.date, "timestamp") else int(b.date),
             "open": b.open, "high": b.high, "low": b.low, "close": b.close,
             "volume": b.volume} for b in bars]
    df = pd.DataFrame(rows, columns=["time", "open", "high", "low", "close", "volume"])
    return df.sort_values("time").drop_duplicates("time", keep="first").reset_index(drop=True)


def fetch_symbol_day(ib, symbol: str, day: date, pacing: PacingLimiter,
                      register_path: Path = REGISTER) -> Path | None:
    """Ein Handelstag, ein Symbol: bereits abgedeckte Fenster ueberspringen, Rest holen,
    zusammensetzen, Gate, schreiben, Register anhaengen. Gibt den geschriebenen Pfad zurueck
    (None, wenn die Datei schon existierte oder gar kein Fenster geholt werden konnte)."""
    contract = front_month(day, symbol)
    vorhanden = {(v, b) for s, v, b in register_load(register_path) if s == symbol}
    alle_fenster = day_windows(day)
    frames, neue_register_zeilen = [], []
    for i, (start_utc, end_utc) in enumerate(alle_fenster, start=1):
        key = (int(start_utc.timestamp()), int(end_utc.timestamp()))
        if key in vorhanden:
            print(f"    Fenster {i}/{len(alle_fenster)} {symbol} {day} "
                  f"{end_utc:%H:%M} UTC: schon vorhanden, uebersprungen", flush=True)
            continue
        df = fetch_window(ib, contract, symbol, end_utc, pacing)
        if df is None:
            # Fehlgeschlagen (z.B. Pacing-Violation nach 3 Versuchen) -- KEINE Registerzeile,
            # sonst gilt das Fenster faelschlich als "geprueft, kein Trade" statt "offen"
            # (Realfall 2026-08-15, siehe fetch_window()-Docstring).
            print(f"    Fenster {i}/{len(alle_fenster)} {symbol} {day} "
                  f"{end_utc:%H:%M} UTC: fehlgeschlagen, wird spaeter erneut versucht", flush=True)
            continue
        print(f"    Fenster {i}/{len(alle_fenster)} {symbol} {day} "
              f"{end_utc:%H:%M} UTC: {len(df)} Kerzen geholt", flush=True)
        if not df.empty:
            frames.append(df)
        neue_register_zeilen.append({
            "symbol": symbol, "von": key[0], "bis": key[1], "kontrakt": contract,
            "kerzen": len(df), "geholt_am": int(time.time())})
    if not frames:
        if neue_register_zeilen:
            register_append(neue_register_zeilen, register_path)
        return None
    rows = pd.concat(frames).sort_values("time").drop_duplicates("time", keep="first")
    try:
        dest = write_day_1s(symbol, day, rows, contract)
    except OHLCDefekt as exc:
        print(f"  ! {symbol} {day}: {exc} -- keine Datei, keine Registerzeilen")
        return None
    if dest is not None:
        register_append(neue_register_zeilen, register_path)
    return dest


def _ist_handelstag(d: date) -> bool:
    """CME-Futures handeln nie an einem vollstaendig auf Sa/So liegenden Kalendertag (die
    Session laeuft 18:00 NY Vortag bis 17:00 NY) -- Sa/So-Kalendertage ueberspringen spart
    garantiert leere Requests (siehe Review-Fund 4)."""
    return d.weekday() < 5


def _letzter_handelstag_bis(d: date) -> date:
    """`d`, oder der naechste Kalendertag davor, der kein Wochenende ist."""
    while not _ist_handelstag(d):
        d -= timedelta(days=1)
    return d


def _letzter_registrierter_tag(symbol: str, register_path: Path = REGISTER) -> date | None:
    """Juengster Handelstag, der laut Register fuer `symbol` mindestens ein Fenster hat (auch
    leere Fenster zaehlen, siehe Review-Fund 3), oder None ohne jeden Eintrag. Ein Fenster-
    `bis`-Zeitstempel vor 18:00 NY gehoert zum Handelstag seines eigenen Kalendertags, ab
    18:00 (Beginn des naechsten Handelstag-Fensters) zum Folgetag -- siehe day_windows()."""
    tage = set()
    for s, _von, bis in register_load(register_path):
        if s != symbol:
            continue
        dt_ny = datetime.fromtimestamp(bis, tz=UTC).astimezone(NY)
        tage.add(dt_ny.date() + timedelta(days=1) if dt_ny.hour >= 18 else dt_ny.date())
    return max(tage) if tage else None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--backfill", nargs=2, metavar=("VON", "BIS"))
    ap.add_argument("--symbol", help="Komma-Liste, z.B. NQ oder NQ,ES (Default: beide)")
    a = ap.parse_args(argv)
    symbols = [s.strip().upper() for s in a.symbol.split(",")] if a.symbol else SYMBOLS
    unbekannt = [s for s in symbols if s not in SYMBOLS]
    if unbekannt:
        ap.error(f"unbekannte Symbole: {', '.join(unbekannt)} -- bekannt: {', '.join(SYMBOLS)}")

    _gateway_sicherstellen()

    from ib_async import IB  # lokal importiert: Selbstcheck/Tests brauchen kein ib_async-Netz
    ib = IB()
    ib.connect(GATEWAY_HOST, GATEWAY_PORT, clientId=7, readonly=True)
    pacing = PacingLimiter()
    try:
        if a.verify:
            # Wochenend-Kalendertage rausrechnen -- sonst liest ein Verify an einem So/Mo
            # "0 Kerzen" wie ein echter R1-Befund (IBKR liefert keine 1s-Bars), obwohl es
            # nur ein geschlossener Handelstag war (Review-Fund 7).
            day = _letzter_handelstag_bis(date.today() - timedelta(days=1))
            for symbol in symbols:
                contract = front_month(day, symbol)
                _, end_utc = day_windows(day)[-1]
                df = fetch_window(ib, contract, symbol, end_utc, pacing)
                print(f"{symbol}: Verify-Fenster {len(df)} Kerzen geholt "
                      f"(Kontrakt {contract}, Tag {day}), nichts geschrieben")
        elif a.backfill:
            von, bis = date.fromisoformat(a.backfill[0]), date.fromisoformat(a.backfill[1])
            handelstage = [von + timedelta(days=i) for i in range((bis - von).days + 1)
                           if _ist_handelstag(von + timedelta(days=i))]
            gesamt = len(handelstage) * len(symbols)
            erledigt = 0
            for tag in handelstage:
                for symbol in symbols:
                    erledigt += 1
                    dest = fetch_symbol_day(ib, symbol, tag, pacing)
                    status = f"geschrieben ({dest.name})" if dest else "uebersprungen (schon vorhanden/keine Daten)"
                    print(f"[{erledigt}/{gesamt}] {symbol} {tag}: {status}", flush=True)
        else:
            # Nachlad: pro Symbol vom Tag nach dem juengsten Registereintrag bis gestern
            # auffuellen (resumable, stateless). Ohne jeden Registereintrag (kalter Start)
            # bewusst nur "gestern" holen statt unbegrenzt zurueck zu backfillen -- ein
            # kompletter Nachlad ab leerem Register ist Aufgabe von --backfill, nicht des
            # taeglichen Cronjobs (Review-Fund 1).
            gestern = _letzter_handelstag_bis(date.today() - timedelta(days=1))
            for symbol in symbols:
                letzter = _letzter_registrierter_tag(symbol)
                tag = letzter + timedelta(days=1) if letzter else gestern
                while tag <= gestern:
                    if _ist_handelstag(tag):
                        dest = fetch_symbol_day(ib, symbol, tag, pacing)
                        status = f"geschrieben ({dest.name})" if dest else "uebersprungen (schon vorhanden/keine Daten)"
                        print(f"{symbol} {tag}: {status}", flush=True)
                    tag += timedelta(days=1)
    finally:
        ib.disconnect()
    return 0


def _demo() -> None:
    global DATA_DIR
    # Front-Monat: Tag vor und nach einem bekannten Roll (Verfall - 8 Tage) muss
    # unterschiedliche Kontrakte liefern, und der Roll-Termin selbst zaehlt schon zum
    # naechsten Kontrakt (roll > d ist strikt).
    verfall_maerz_2026 = _third_friday(2026, 3)
    roll = verfall_maerz_2026 - timedelta(days=8)
    assert front_month(roll - timedelta(days=1), "NQ") == "NQH2026", \
        "Tag vor dem Roll muss noch der alte Front-Monat sein"
    assert front_month(roll, "NQ") == "NQM2026", \
        "der Roll-Tag selbst zaehlt schon zum naechsten Quartalskontrakt"
    assert front_month(roll + timedelta(days=1), "ES") == "ESM2026"
    # Jahreswechsel: kurz vor dem Dezember-Roll noch Z, danach H des Folgejahres.
    verfall_dez_2026 = _third_friday(2026, 12)
    roll_dez = verfall_dez_2026 - timedelta(days=8)
    assert front_month(roll_dez - timedelta(days=1), "NQ") == "NQZ2026"
    assert front_month(roll_dez, "NQ") == "NQH2027"

    # Pacing-Limiter: 61 Requests duerfen mit einer simulierten Uhr nicht in unter 600s
    # durchgehen -- der 61. Request muss auf das Verlassen des 60er-Fensters warten.
    clock_state = {"t": 0.0}

    def fake_clock():
        return clock_state["t"]

    def fake_sleep(seconds):
        clock_state["t"] += seconds

    limiter = PacingLimiter(clock=fake_clock, sleep=fake_sleep)
    start = clock_state["t"]
    for _ in range(61):
        limiter.wait()
    assert clock_state["t"] - start >= 600.0, \
        f"61 Requests dauerten nur {clock_state['t'] - start}s, muessen >= 600s sein"

    # Fenster-Zerlegung: genau 46 Fenster, erstes beginnt 18:00 NY des Vortages,
    # letztes endet 17:00 NY -- inklusive eines Tages ueber einen DST-Wechsel.
    normal_tag = date(2026, 6, 15)
    windows = day_windows(normal_tag)
    assert len(windows) == 46, len(windows)
    assert windows[0][0] == datetime(2026, 6, 14, 18, 0, tzinfo=NY).astimezone(UTC)
    assert windows[-1][1] == datetime(2026, 6, 15, 17, 0, tzinfo=NY).astimezone(UTC)
    assert all((b - a).total_seconds() == WINDOW_SECONDS for a, b in windows), \
        "alle Fenster muessen exakt 1800 Sekunden lang sein"

    dst_tag = date(2026, 11, 1)  # "fall back" 2026 faellt auf den 1. November
    dst_windows = day_windows(dst_tag)
    # Am DST-Fold (Nov 1) spannt 18:00 NY Vortag bis 17:00 NY Heute 24h UTC (nicht 23h),
    # weil die rueckwaertsgesprungene Stunde doppelt zaehlt -- also 48 Fenster, nicht 46.
    # Wichtig: ALLE sind exakt 1800 Sekunden (keine 90-Minuten-Fenster durch fold=0-Fehler).
    assert len(dst_windows) == 48, \
        f"DST-Tag mit 24h UTC muss 48 Fenster liefern, waren {len(dst_windows)}"
    assert all((b - a).total_seconds() == WINDOW_SECONDS for a, b in dst_windows), \
        "jedes Fenster muss exakt 1800 Sekunden lang sein, auch am DST-Fold"

    # Register-Resume: nach simuliertem Abbruch werden nur die fehlenden Fenster erkannt.
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        reg_path = Path(tmp) / "1s-abdeckung.csv"
        alle_fenster = {(int(a.timestamp()), int(b.timestamp())) for a, b in windows[:10]}
        geholt = set(list(alle_fenster)[:6])
        register_append(
            [{"symbol": "NQ", "von": v, "bis": b, "kontrakt": "NQU2026",
              "kerzen": 1800, "geholt_am": 1786838400} for v, b in geholt],
            path=reg_path)
        vorhanden = register_load(reg_path)
        assert vorhanden == {("NQ", v, b) for v, b in geholt}
        fehlend = alle_fenster - {(v, b) for _, v, b in vorhanden}
        assert len(fehlend) == 4, "nur die 4 nicht geholten Fenster duerfen fehlend sein"

    # Fetch-Orchestrierung ohne Netz: Stub-IB liefert kanonische Bars, register_load()
    # muss bereits geholte Fenster ueberspringen (kein zweiter reqHistoricalData-Aufruf).
    class _FakeBar:
        def __init__(self, ts, o, h, l, c, v):
            self.date, self.open, self.high, self.low, self.close, self.volume = ts, o, h, l, c, v

    class _StubEvent:
        """Minimaler Ersatz fuer ib_async's errorEvent -- unterstuetzt nur +=/-=, ruft nie
        auf. Reicht, damit fetch_window() denselben Handler-An-/Abmelde-Code laufen lassen
        kann wie gegen ein echtes IB()."""

        def __iadd__(self, handler):
            return self

        def __isub__(self, handler):
            return self

    class _StubIB:
        def __init__(self):
            self.calls = 0
            self.errorEvent = _StubEvent()

        def reqHistoricalData(self, contract, endDateTime, **kw):
            self.calls += 1
            start = int(endDateTime.timestamp()) - WINDOW_SECONDS
            return [_FakeBar(start + i, 100.0 + i, 100.5 + i, 99.5 + i, 100.0 + i, 5)
                    for i in range(0, WINDOW_SECONDS, 900)]

    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        global _future_contract
        _orig_future_contract = _future_contract
        _future_contract = lambda contract, symbol: contract  # Stub-IB ignoriert den Contract-Typ
        try:
            orig_data_dir = DATA_DIR
            DATA_DIR = Path(tmp)
            try:
                stub = _StubIB()
                pacing = PacingLimiter(clock=lambda: 0.0, sleep=lambda s: None)
                tag = date(2026, 6, 15)
                reg_path = DATA_DIR / "1s-abdeckung.csv"
                dest = fetch_symbol_day(stub, "NQ", tag, pacing, register_path=reg_path)
                assert dest is not None and dest.exists(), "erster Lauf muss eine Datei schreiben"
                erster_call_count = stub.calls
                assert erster_call_count == 46, erster_call_count

                # Zweiter Lauf: Datei existiert schon -> write_day_1s() liefert None, aber
                # fetch_symbol_day holt die Fenster trotzdem erneut an (Register schuetzt nur
                # vor Doppel-Requests INNERHALB eines Laufs, nicht vor einem Re-Lauf auf eine
                # bereits fertige Datei). Stattdessen: Register simuliert einen Abbruch nach
                # 6 Fenstern, zweiter Lauf darf nur die restlichen 40 anfragen.
                dest.unlink()
                reg_path.unlink()
                teil_fenster = day_windows(tag)[:6]
                register_append(
                    [{"symbol": "NQ", "von": int(a.timestamp()), "bis": int(b.timestamp()),
                      "kontrakt": "NQU2026", "kerzen": 1800, "geholt_am": 0}
                     for a, b in teil_fenster],
                    path=reg_path)
                stub2 = _StubIB()
                fetch_symbol_day(stub2, "NQ", tag, pacing, register_path=reg_path)
                assert stub2.calls == 40, \
                    f"Resume nach Abbruch bei 6/46 Fenstern muss 40 Requests machen, waren {stub2.calls}"
            finally:
                DATA_DIR = orig_data_dir
        finally:
            _future_contract = _orig_future_contract

    # Parquet-Roundtrip: Schreiben und Zurücklesen erhaelt Typen und Zeitstempel.
    with tempfile.TemporaryDirectory() as tmp:
        orig_data_dir = DATA_DIR
        DATA_DIR = Path(tmp)
        try:
            df = pd.DataFrame({"time": [1786752000, 1786752001], "open": [100.0, 100.25],
                               "high": [100.5, 100.5], "low": [99.75, 100.0],
                               "close": [100.25, 100.25], "volume": [3, 5]})
            dest = write_day_1s("NQ", date(2026, 6, 15), df, "NQU2026")
            zurueck = pd.read_parquet(dest)
            assert zurueck["time"].tolist() == [1786752000, 1786752001]
            assert zurueck["contract"].tolist() == ["NQU2026", "NQU2026"]
            assert write_day_1s("NQ", date(2026, 6, 15), df, "NQU2026") is None, \
                "bestehende Datei darf nie ueberschrieben werden"
        finally:
            DATA_DIR = orig_data_dir

    print("fetch_ibkr front_month/PacingLimiter demo ok")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        _demo()
    else:
        sys.exit(main())
