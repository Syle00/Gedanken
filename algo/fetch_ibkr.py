#!/usr/bin/env python3
"""Laedt sekundengenaue OHLC-Daten fuer NQ und ES ueber die IBKR-TWS/Gateway-API und legt sie
im bestehenden raw/marktdaten/-Baum als Tages-Parquet ab (Schema wie das TradingView-CSV,
plus volume/contract). Siehe docs/superpowers/specs/2026-08-15-ibkr-1s-datenanbindung-design.md.

Drei Betriebsarten:
    python algo/fetch_ibkr.py --verify [--symbol NQ]      # ein 30-Min-Fenster, schreibt nichts
    python algo/fetch_ibkr.py --backfill                  # gesamte verfuegbare 1s-Historie
    python algo/fetch_ibkr.py --backfill 2026-02-17 2026-08-14
    python algo/fetch_ibkr.py                             # Nachlad: letzter Registereintrag bis gestern

`--backfill` ohne Datumsangabe holt alles, was IBKR fuer 1s-Bars vorhaelt (~6 Monate), und
kann beliebig oft neu gestartet werden: bereits vorhandene Tagesdateien werden ohne einen
einzigen Request uebersprungen, der Lauf macht also von selbst dort weiter, wo er aufhoerte.

Verbindet sich ausschliesslich readonly gegen Port 4002 (Paper-Gateway) -- dieser Datenpfad
hat konstruktionsbedingt keinen Weg zu echtem Kapital (Spec Design SS9).
"""
from __future__ import annotations

import argparse
import csv
import io
import os
import socket
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
# IBKR haelt 1s-Bars rund 6 Monate vor (Design SS2/E1). Bewusst 183 statt "6 Monate"
# gerechnet: faellt der Startzeitpunkt einen Tag zu weit zurueck, meldet IBKR fuer die
# betroffenen Tage sauber "no data" und der Lauf geht weiter -- ein zu spaeter Start
# wuerde dagegen stillschweigend Historie liegenlassen.
HISTORIE_TAGE = 183
GATEWAY_HOST, GATEWAY_PORT = "127.0.0.1", 4002
# Zwei-Rechner-Betrieb: IBC liegt je nach Rechner woanders (C:\IBC bzw. %USERPROFILE%\IBC).
# Darum nicht hart verdrahten, sondern die bekannten Orte durchprobieren -- IBC_GATEWAY_BAT
# sticht immer, damit ein dritter Ort ohne Code-Aenderung funktioniert.
GATEWAY_BAT_KANDIDATEN = [Path(r"C:\IBC") / "StartGateway.bat",
                          Path.home() / "IBC" / "StartGateway.bat"]
GATEWAY_BAT = Path(os.environ["IBC_GATEWAY_BAT"]) if os.environ.get("IBC_GATEWAY_BAT") else \
    next((p for p in GATEWAY_BAT_KANDIDATEN if p.exists()), GATEWAY_BAT_KANDIDATEN[0])


FORTSCHRITT_LOG_DIR = Path(__file__).resolve().parent / "live"


def _balken(i: int, n: int, breite: int = 10) -> str:
    """Textfortschrittsbalken, z.B. '[####------]' bei 18 von 46."""
    voll = round(breite * i / n) if n else 0
    return f"[{'#' * voll}{'-' * (breite - voll)}]"


class _Tee:
    """Schreibt in mehrere Streams gleichzeitig (hier: echtes stdout + Fortschrittslog).

    Nach jedem write() geflusht, weil das Fortschrittsfenster ein zweiter Prozess ist, der
    die Datei mitliest -- gepufferte Ausgabe kaeme dort erst blockweise oder gar nicht an.
    """

    def __init__(self, *ziele):
        self._ziele = ziele

    def write(self, text: str) -> int:
        for ziel in self._ziele:
            ziel.write(text)
            ziel.flush()
        return len(text)

    def flush(self) -> None:
        for ziel in self._ziele:
            ziel.flush()


def _fenster_laeuft_schon(pid_datei: Path) -> bool:
    """True, wenn das Fortschrittsfenster aus einem frueheren Lauf noch offen ist.

    Ueber `tasklist` statt psutil (Stdlib reicht) und ueber eine PID-Datei statt einer
    Kommandozeilen-Suche (`tasklist` zeigt keine Argumente). Ein recyceltes PID kann
    hoechstens dazu fuehren, dass kein neues Fenster aufgeht -- Anzeige ist Beiwerk.
    """
    import subprocess
    try:
        pid = int(pid_datei.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return False
    try:
        # Bewusst Bytes statt text=True: `tasklist` schreibt in der OEM-Codepage (cp850),
        # dekodiert wuerde aber mit der ANSI-Locale (cp1252) -- das deutsche "ausgefuehrt"
        # enthaelt 0x81, in cp1252 undefiniert. Der UnicodeDecodeError faellt in subprocess'
        # Reader-Thread an, wird dort verschluckt, und .stdout ist danach still None.
        out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH"],
                             capture_output=True, timeout=10).stdout or b""
    except (OSError, subprocess.SubprocessError):
        return False
    return b"powershell" in out.lower()


def _fortschrittsfenster_oeffnen():
    """Spiegelt stdout in ein Tageslog und oeffnet ein zweites Konsolenfenster, das dieses
    Log live mitliest (`Get-Content -Wait`) -- damit ein langer Backfill sichtbar mitlaeuft,
    ohne dass die aufrufende Konsole blockiert ist. Gibt das offene Log-Handle zurueck.

    Bewusst ein zweiter Prozess statt eines eigenen GUI-Fensters: keine zusaetzliche
    Abhaengigkeit, kein zweiter Thread im Datenpfad, und das Fenster ueberlebt das Ende des
    Laufs (`-NoExit`), sodass das Ergebnis lesbar bleibt. Alle Laeufe eines Tages schreiben
    in dieselbe Logdatei, ein noch offenes Fenster zeigt den neuen Lauf also von selbst --
    darum wird es wiederverwendet statt gestapelt (sonst steht nach fuenf Laeufen ein
    Fensterwald offen). Schlaegt das Oeffnen fehl, laeuft der Download normal weiter -- eine
    fehlende Anzeige darf keinen Datenlauf abbrechen.
    """
    FORTSCHRITT_LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_pfad = FORTSCHRITT_LOG_DIR / f"fetch_ibkr-{date.today():%Y-%m-%d}.log"
    log = log_pfad.open("a", encoding="utf-8")
    log.write(f"\n=== Lauf gestartet {datetime.now():%Y-%m-%d %H:%M:%S} "
              f"({' '.join(sys.argv[1:]) or 'Nachlad'}) ===\n")
    log.flush()
    sys.stdout = _Tee(sys.stdout, log)
    pid_datei = FORTSCHRITT_LOG_DIR / ".fetch_ibkr-fenster.pid"
    if _fenster_laeuft_schon(pid_datei):
        print("Fortschrittsfenster aus einem frueheren Lauf ist noch offen, "
              "es zeigt diesen Lauf mit.", flush=True)
        return log
    try:
        import subprocess
        proc = subprocess.Popen(
            ["powershell", "-NoExit", "-Command",
             f"$host.UI.RawUI.WindowTitle='IBKR-Download'; "
             f"Get-Content -Wait -Tail 40 -Encoding UTF8 -LiteralPath '{log_pfad}'"],
            creationflags=subprocess.CREATE_NEW_CONSOLE)
        pid_datei.write_text(str(proc.pid), encoding="utf-8")
    except Exception as exc:  # Anzeige ist Beiwerk, der Download zaehlt
        print(f"! Fortschrittsfenster liess sich nicht oeffnen ({exc}) -- "
              f"Ausgabe steht in {log_pfad}", flush=True)
    return log


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
    # os.startfile() statt subprocess.Popen: StartGateway.bat/StartIBC.bat brechen ueber
    # subprocess.Popen() reproduzierbar mit "'set' kann syntaktisch an dieser Stelle nicht
    # verarbeitet werden" ab (batch-interne `for /f`-Befehlssubstitution bei der
    # Java-Versionserkennung) -- auch mit explizit gesetztem cwd, siehe algo/PLAN.md
    # 2026-08-15. os.startfile() ist Pythons Aequivalent zum Explorer-Doppelklick (nutzt
    # denselben ShellExecute-Mechanismus), der manuell nachweislich zuverlaessig funktioniert.
    os.startfile(str(GATEWAY_BAT), cwd=str(GATEWAY_BAT.parent))
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

    **`min_gap` ist die eigentliche Bremse und muss `window / max_requests` sein (10s).**
    Die deque-Pruefung allein greift erst beim 61. Request -- ein voller Handelstag hat aber
    nur 46 Fenster und lief damit komplett an der Grenze vorbei. Gemessen: 41 Requests in
    60s = **41 Req/Min gegen erlaubte 6**. Genau bei Request 42 begann IBKR am 2026-08-16
    reproduzierbar mit Error 162 "pacing violation" abzuweisen, und weil jeder der drei
    Wiederholversuche selbst ein Request ist, riss danach der ganze Rest des Tages ab
    (5 Fenster x 3 Versuche, alle abgelehnt).

    Die frueheren Anlaeufe (0.5s, dann 1.5s nach dem Review-Fund 2026-08-15) kurierten das
    Symptom: sie streckten den Burst von 20s auf 60s, blieben aber beide um ein Vielfaches
    ueber der Rate und verschoben den Abbruch nur weiter nach hinten -- daher der Eindruck,
    Violations kaemen "meist in der zweiten Haelfte eines Laufs". Mit 10s liegt der
    Durchsatz bei den 6 Req/Min, die Design SS3.3 als Grenze und SS3.4 als Rechengrundlage
    nennt (46 Fenster ~= 8 Min je Symbol und Tag, 6-Monats-Backfill ~34h) -- die
    Laufzeittabelle des Designs war also immer schon auf 10s gerechnet, nur der Code nicht.

    ponytail: der Zustand lebt im Prozess. Zwei gleichzeitige fetch_ibkr-Prozesse teilen
    sich IBKRs serverseitiges Kontingent, ohne voneinander zu wissen -- der zweite startet
    mit leerer deque in ein bereits erschoepftes Budget. Sichtbar geworden, als zwei Laeufe
    direkt hintereinander starteten: der zweite scheiterte an Fenster 1. Wenn das oefter
    stoert, den letzten Request-Zeitpunkt in einer Datei neben dem Register ablegen."""

    def __init__(self, clock=time.monotonic, sleep=time.sleep,
                 max_requests: int = 60, window: float = 600.0, min_gap: float | None = None):
        self._clock = clock
        self._sleep = sleep
        self._max = max_requests
        self._window = window
        # Aus der Grenze abgeleitet statt frei gewaehlt: eine handgesetzte Zahl war genau
        # der Fehler, aus dem die Violations kamen.
        self._min_gap = window / max_requests if min_gap is None else min_gap
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
    """(symbol, von, bis) aller bereits erfolgreich geholten Fenster, als UNIX-Sekunden.

    Defekte Zeilen werden uebersprungen statt zu crashen: das Register ist ein
    Buchhaltungs-Index, kein Datenbestand -- ein nicht lesbares Fenster gilt als
    "noch nicht geholt" und wird beim naechsten Lauf einfach neu gezogen.
    """
    if not path.exists():
        return set()
    fenster, defekt = set(), 0
    with path.open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            try:
                fenster.add((r["symbol"], int(r["von"]), int(r["bis"])))
            except (TypeError, ValueError):
                defekt += 1
    if defekt:
        print(f"  ! {path.name} -- {defekt} defekte Zeile(n) uebersprungen, "
              f"betroffene Fenster werden neu geholt")
    return fenster


def register_append(rows: list[dict], path: Path = REGISTER) -> None:
    """Haengt Zeilen an -- schreibt den Header nur, wenn die Datei neu angelegt wird.

    Der komplette Block geht als *ein* write()-Aufruf raus. csv.writer schreibt sonst
    pro Feld einzeln in den gepufferten Stream; laufen zwei fetch_ibkr-Prozesse
    gleichzeitig (Backfill + Nachlad), koennen sich diese Teilschreibvorgaenge
    verschraenken und einen Datensatz mitten im Feld zerreissen -- genau so entstand
    am 2026-08-16 die kaputte Zeile in 1s-abdeckung.csv.
    """
    neu = not path.exists()
    path.parent.mkdir(parents=True, exist_ok=True)
    puffer = io.StringIO()
    w = csv.DictWriter(puffer, fieldnames=REGISTER_HEADER, lineterminator="\n")
    if neu:
        w.writeheader()
    w.writerows(rows)
    with path.open("a", newline="", encoding="utf-8") as fh:
        fh.write(puffer.getvalue())
        fh.flush()


def _tagesdatei(symbol: str, day: date) -> Path:
    """Zielpfad der Tagesdatei. Eigene Funktion, weil dieser Pfad seit dem Resume-Umbau an
    zwei Stellen gebraucht wird: beim Schreiben und beim Ueberspringen bereits fertiger Tage."""
    return (DATA_DIR / f"{day:%Y}" / f"{day:%m}" / f"{day:%d.%m.%Y}"
            / f"{symbol} {day.isoformat()} 1s.parquet")


def write_day_1s(symbol: str, day: date, rows: pd.DataFrame, contract: str) -> Path | None:
    """Schreibt eine Tagesdatei als Parquet, niemals ueberschreibend (wie
    fetch_yfinance.write_day()). Fuehrt vorher das Nulltoleranz-Gate aus -- wirft es
    OHLCDefekt, entsteht keine Datei (Aufrufer faengt das ab, siehe fetch_symbol_day)."""
    dest = _tagesdatei(symbol, day)
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


def _echter_fehler(code: int, text: str) -> bool:
    """Trennt echte Stoerungen von IBKR-Meldungen, die ein leeres Fenster *erklaeren*.

    Notwendig, weil `reqHistoricalData` bei jedem Fehlschlag ganz normal eine leere Liste
    zurueckgibt -- ob "kein Handel" oder "Request abgewiesen" steht ausschliesslich in
    `errorEvent`. Zwei Faelle sind kein Fehlschlag:

    - **Codes 2100-2199**: IBKRs System-/Verbindungsmeldungen ("Market data farm connection
      is OK", 2104/2106/2158). Die kommen im Normalbetrieb staendig und haben mit dem
      Request nichts zu tun.
    - **162 mit "no data" im Text**: IBKRs Antwort fuer ein Fenster ohne jeden Handel --
      Feiertag oder Early Close (z.B. Presidents' Day 2026-02-16, CME schliesst 13:00 NY,
      die letzten 8 Tagesfenster sind leer). Ausgerechnet dieselbe Nummer 162 traegt aber
      auch die Pacing-Violation, deshalb ueber den *Text* unterscheiden statt ueber den Code:
      eine Pacing-Violation als "Markt zu" zu verbuchen wuerde eine Datenluecke als
      geschlossen ausweisen.
    """
    if 2100 <= code < 2200:
        return False
    if code == 162 and "no data" in text.lower():
        return False
    return True


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

        fehler = [(c, t) for c, t in fehler if _echter_fehler(c, t)]
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
                      register_path: Path = REGISTER, sleep=time.sleep) -> tuple[Path | None, str]:
    """Ein Handelstag, ein Symbol: alle Fenster holen, zusammensetzen, Gate, schreiben,
    Register anhaengen. Gibt `(pfad, status)` zurueck -- `pfad` ist None, sobald keine Datei
    entstand.

    **Der Status wird mitgegeben, statt ihn den Aufrufer raten zu lassen.** Frueher war die
    Rueckgabe nur `Path | None` und beide Schleifen in main() machten daraus
    "uebersprungen (schon vorhanden/keine Daten)" -- diese Meldung erschien am 2026-08-16
    auch fuer einen Tag, der gerade an 5 Pacing-Violations gescheitert war. Ein Fehlschlag,
    der wie "ist schon da, alles gut" aussieht, ist in einem 30-Stunden-Lauf genau die
    Sorte Meldung, die man nicht nachtraeglich richtigstellen kann.

    **Resume-Autoritaet ist die Tagesdatei, nicht das Register.** Existiert sie, wird der Tag
    ohne einen einzigen Request uebersprungen -- damit macht jeder Neustart von selbst dort
    weiter, wo der letzte Lauf aufhoerte, und ein Wiederholungslauf ueber einen fertigen
    Zeitraum kostet nichts. Frueher wurden pro Tag trotzdem alle 46 Fenster angefragt und das
    Ergebnis dann von write_day_1s() verworfen.

    **Alles-oder-nichts je Tag.** Schlaegt auch nur ein Fenster fehl, entsteht weder Datei
    noch Registerzeile; der ganze Tag wird beim naechsten Lauf neu geholt. Grund ist ein
    realer Datenverlust: frueher schrieb diese Funktion den Tag aus den Fenstern, die
    ankamen, und weil write_day_1s() nie ueberschreibt, war das Loch danach dauerhaft
    eingefroren -- `ES 2026-02-19` endete so bei 11:29 NY statt 17:00 (35 von 46 Fenstern),
    sah aber wie ein fertiger Handelstag aus. Verschaerfend kam der frueher hier stehende
    Register-Filter dazu: er uebersprang genau die Fenster, deren Daten nur im Speicher des
    abgebrochenen Laufs existierten, sodass ein zweiter Lauf das Loch nicht mehr fuellen
    konnte, sondern zementierte. Der Preis der neuen Regel sind bis zu 46 wiederholte
    Requests (~70 s) nach einem Abbruch mitten im Tag -- gegen einen 34-Stunden-Backfill
    vernachlaessigbar, gegen eine unsichtbare Datenluecke ohnehin.

    Ein Fenster ohne Handel (Feiertag, Early Close) ist *kein* Fehlschlag, siehe
    _echter_fehler() -- sonst kaeme ein verkuerzter Handelstag wie Presidents' Day nie
    zustande."""
    dest_pfad = _tagesdatei(symbol, day)
    if dest_pfad.exists():
        return None, "schon vorhanden (0 Requests)"
    contract = front_month(day, symbol)
    alle_fenster = day_windows(day)
    frames, neue_register_zeilen, fehlgeschlagen = [], [], 0
    for i, (start_utc, end_utc) in enumerate(alle_fenster, start=1):
        df = fetch_window(ib, contract, symbol, end_utc, pacing, sleep=sleep)
        if df is None:
            fehlgeschlagen += 1
            print(f"    {_balken(i, len(alle_fenster))} {i}/{len(alle_fenster)} {symbol} {day} "
                  f"{end_utc:%H:%M} UTC: fehlgeschlagen", flush=True)
            continue
        print(f"    {_balken(i, len(alle_fenster))} {i}/{len(alle_fenster)} {symbol} {day} "
              f"{end_utc:%H:%M} UTC: {len(df)} Kerzen geholt", flush=True)
        if not df.empty:
            frames.append(df)
        neue_register_zeilen.append({
            "symbol": symbol, "von": int(start_utc.timestamp()), "bis": int(end_utc.timestamp()),
            "kontrakt": contract, "kerzen": len(df), "geholt_am": int(time.time())})
    if fehlgeschlagen:
        return None, (f"FEHLGESCHLAGEN ({fehlgeschlagen}/{len(alle_fenster)} Fenster) -- keine "
                      f"Datei, keine Registerzeilen, wird beim naechsten Lauf erneut geholt")
    if not frames:
        return None, "alle Fenster leer (kein Handelstag?)"
    rows = pd.concat(frames).sort_values("time").drop_duplicates("time", keep="first")
    try:
        dest = write_day_1s(symbol, day, rows, contract)
    except OHLCDefekt as exc:
        return None, f"FEHLGESCHLAGEN (Gate: {exc}) -- keine Datei, keine Registerzeilen"
    if dest is None:                      # zwischen Eingangspruefung und Schreiben entstanden
        return None, "schon vorhanden (0 Requests)"
    register_append(neue_register_zeilen, register_path)
    return dest, f"geschrieben ({len(rows)} Kerzen, {len(neue_register_zeilen)} Fenster)"


def live_fenster(symbol: str, day: date, seit: datetime, ib=None,
                  pacing: PacingLimiter | None = None) -> list[dict]:
    """Laufender Handelstag, **rein im Speicher**: holt die 30-Minuten-Fenster von `day`, die
    Kerzen nach `seit` enthalten koennen, und gibt die Kerzenzeilen zurueck
    (time/open/high/low/close/volume, aufsteigend, ohne Duplikate).

    **Schreibt bewusst weder Tagesdatei noch Registerzeile.** Eine mitten am Tag geschriebene
    Tagesdatei waere dauerhaft eingefroren: write_day_1s() ueberschreibt nie, und
    fetch_symbol_day() ueberspringt jeden Tag, dessen Datei existiert -- selbst ein spaeterer
    expliziter --backfill wuerde den Teiltag also nicht mehr heilen. Der Teiltag entstuende
    dabei lautlos: Fenster, die in der Zukunft enden, beantwortet IBKR mit Error 162
    ("no data"), und _echter_fehler() stuft genau das absichtlich als "Markt zu" statt als
    Fehlschlag ein -- es gaebe kein FEHLGESCHLAGEN, sondern eine sauber aussehende Datei.
    Eine Registerzeile wiederum wuerde _letzter_registrierter_tag() auf heute setzen, worauf
    der taegliche Nachlad ("bis gestern") den Tag nie mehr holt. Wird gar nichts geschrieben,
    ist diese ganze Fehlerklasse per Konstruktion ausgeschlossen.

    `seit` grenzt den Abruf auf das Neue ein: ein Live-Loop kostet damit 1-2 Requests je
    Zyklus statt 46 (Pacing: 1 Request/10s, siehe PacingLimiter).

    Faellt hart aus statt eine Luecke zu liefern: ein nicht erreichbares Gateway laesst
    `ib.connect` durch, ein nach drei Versuchen fehlgeschlagenes Fenster wirft. Ein Loch
    mitten im Live-Strom waere schlimmer als gar keine Zahl.

    `ib`/`pacing` sind injizierbar (echte Verbindung im Betrieb, Stub im Selbstcheck)."""
    jetzt = datetime.now(UTC)
    seit_utc = seit.astimezone(UTC)
    fenster = [(s, e) for s, e in day_windows(day) if e > seit_utc and s <= jetzt]
    if not fenster:
        return []
    eigene_verbindung = ib is None
    if eigene_verbindung:
        _gateway_sicherstellen()
        from ib_async import IB  # lokal: der Selbstcheck laeuft ohne ib_async
        ib = IB()
        ib.connect(GATEWAY_HOST, GATEWAY_PORT, clientId=8, readonly=True)
    pacing = pacing or PacingLimiter()
    contract = front_month(day, symbol)
    zeilen: dict[int, dict] = {}
    try:
        for _start_utc, end_utc in fenster:
            df = fetch_window(ib, contract, symbol, end_utc, pacing)
            if df is None:
                raise RuntimeError(f"{symbol}: Livefenster bis {end_utc} nach 3 Versuchen "
                                   f"fehlgeschlagen -- lieber kein Stand als ein Loch")
            for zeile in df.to_dict("records"):
                zeilen[zeile["time"]] = zeile
    finally:
        if eigene_verbindung:
            ib.disconnect()
    grenze = int(seit_utc.timestamp())
    return [zeilen[t] for t in sorted(zeilen) if t > grenze]


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


def _backfill_zeitraum(argumente: list[str], heute: date | None = None) -> tuple[date, date]:
    """Zeitraum fuer --backfill. Leere Liste = gesamte verfuegbare Historie (HISTORIE_TAGE
    zurueck bis zum letzten Handelstag), sonst die beiden angegebenen ISO-Daten.

    Der Endtag ist bewusst der letzte *Handelstag*, nicht schlicht gestern: an einem Sonntag
    wuerde `gestern` sonst auf Samstag fallen, `_ist_handelstag()` filtert ihn wieder heraus,
    und der Lauf endete beim Freitag -- was er auch soll, aber die gemeldete Zeitraumgrenze
    haette gelogen."""
    heute = heute or date.today()
    if not argumente:
        bis = _letzter_handelstag_bis(heute - timedelta(days=1))
        return bis - timedelta(days=HISTORIE_TAGE), bis
    if len(argumente) != 2:
        raise ValueError(f"--backfill braucht entweder kein Argument (gesamte Historie) "
                         f"oder genau zwei (VON BIS), bekommen: {len(argumente)}")
    von, bis = date.fromisoformat(argumente[0]), date.fromisoformat(argumente[1])
    if von > bis:
        raise ValueError(f"--backfill: VON ({von}) liegt nach BIS ({bis})")
    return von, bis


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--backfill", nargs="*", metavar=("VON", "BIS"),
                    help="ohne Angabe: gesamte verfuegbare 1s-Historie "
                         f"(letzte {HISTORIE_TAGE} Tage bis gestern); sonst VON BIS")
    ap.add_argument("--symbol", help="Komma-Liste, z.B. NQ oder NQ,ES (Default: beide)")
    ap.add_argument("--kein-fenster", dest="kein_fenster", action="store_true",
                    help="kein zweites Fortschrittsfenster oeffnen (fuer unbeaufsichtigte "
                         "Laeufe wie den taeglichen Task)")
    a = ap.parse_args(argv)
    symbols = [s.strip().upper() for s in a.symbol.split(",")] if a.symbol else SYMBOLS
    unbekannt = [s for s in symbols if s not in SYMBOLS]
    if unbekannt:
        ap.error(f"unbekannte Symbole: {', '.join(unbekannt)} -- bekannt: {', '.join(SYMBOLS)}")
    # Bewusst vor Fortschrittsfenster und Gateway-Start: ein Tippfehler im Datum soll nicht
    # erst nach dem (bis zu dreiminuetigen) Gateway-Cold-Start auffliegen.
    zeitraum = None
    if a.backfill is not None:
        try:
            zeitraum = _backfill_zeitraum(a.backfill)
        except ValueError as exc:
            ap.error(str(exc))

    if not a.kein_fenster:
        _fortschrittsfenster_oeffnen()

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
        elif zeitraum is not None:
            von, bis = zeitraum
            handelstage = [von + timedelta(days=i) for i in range((bis - von).days + 1)
                           if _ist_handelstag(von + timedelta(days=i))]
            gesamt = len(handelstage) * len(symbols)
            print(f"Backfill {von} bis {bis}: {len(handelstage)} Handelstage x "
                  f"{len(symbols)} Symbol(e) = {gesamt} Tagesdateien. Bereits vorhandene "
                  f"werden ohne Request uebersprungen.", flush=True)
            erledigt = 0
            offen: list[str] = []
            for tag in handelstage:
                for symbol in symbols:
                    erledigt += 1
                    _, status = fetch_symbol_day(ib, symbol, tag, pacing)
                    if status.startswith("FEHLGESCHLAGEN"):
                        offen.append(f"{symbol} {tag}")
                    print(f"{_balken(erledigt, gesamt)} {erledigt}/{gesamt} "
                          f"{symbol} {tag}: {status}", flush=True)
            # Schlussbilanz: bei 264 Tagesdateien ist die Zeile-fuer-Zeile-Ausgabe nicht mehr
            # ueberschaubar, und offene Tage duerfen nicht im Scrollback verschwinden.
            if offen:
                print(f"\n! {len(offen)} von {gesamt} Tagesdateien offen geblieben: "
                      f"{', '.join(offen)}\n  Denselben Aufruf einfach wiederholen -- fertige "
                      f"Tage kosten 0 Requests, nur diese werden neu geholt.", flush=True)
            else:
                print(f"\nAlle {gesamt} Tagesdateien vollstaendig.", flush=True)
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
                if tag > gestern:
                    print(f"{symbol}: bereits aktuell bis {letzter} (letzter Handelstag: {gestern}), "
                          f"nichts zu holen", flush=True)
                while tag <= gestern:
                    if _ist_handelstag(tag):
                        _, status = fetch_symbol_day(ib, symbol, tag, pacing)
                        print(f"{symbol} {tag}: {status}", flush=True)
                    tag += timedelta(days=1)
    finally:
        ib.disconnect()
        # Schlusszeile, damit im Fortschrittsfenster (das per -NoExit offen bleibt) sichtbar
        # ist, dass der Lauf durch ist und nicht bloss haengt.
        print(f"=== Lauf beendet {datetime.now():%H:%M:%S} ===", flush=True)
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

    # Fortschrittsanzeige: Balken-Randfaelle und die stdout-Spiegelung ins Fortschrittslog.
    assert _balken(0, 46) == "[----------]"
    assert _balken(46, 46) == "[##########]"
    assert _balken(23, 46) == "[#####-----]"
    assert _balken(0, 0) == "[----------]", "n=0 darf nicht durch Null teilen"
    puffer_a, puffer_b = io.StringIO(), io.StringIO()
    _Tee(puffer_a, puffer_b).write("hallo\n")
    assert puffer_a.getvalue() == puffer_b.getvalue() == "hallo\n", \
        "Tee muss identisch in alle Ziele schreiben"

    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        pid_datei = Path(tmp) / "fenster.pid"
        assert not _fenster_laeuft_schon(pid_datei), "ohne PID-Datei darf kein Fenster gelten"
        pid_datei.write_text("kaputt", encoding="utf-8")
        assert not _fenster_laeuft_schon(pid_datei), "unlesbare PID darf nicht crashen"
        pid_datei.write_text(str(os.getpid()), encoding="utf-8")
        assert not _fenster_laeuft_schon(pid_datei), \
            "die eigene python.exe ist kein Fortschrittsfenster (Namensprüfung muss greifen)"
        # Laengst beendete PID: hier meldet `tasklist` "keine Aufgaben ... ausgefuehrt" in der
        # OEM-Codepage -- der Fall, an dem die fruehere text=True-Dekodierung still None ergab.
        pid_datei.write_text("999998", encoding="utf-8")
        assert not _fenster_laeuft_schon(pid_datei), \
            "eine nicht mehr laufende PID darf False ergeben, nicht crashen"

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

    # Der eigentliche Test: die Grenze ist eine *Rate*, kein Deckel beim 61. Request.
    # Ein voller Handelstag (46 Fenster) liegt unter 60 Requests -- frueher fiel er damit
    # komplett durch die Pruefung und lief mit 41 Req/Min statt der erlaubten 6 (siehe
    # PacingLimiter-Docstring). Genau diese Rate deckt der Check jetzt ab, fuer mehrere
    # Laufgroessen unterhalb des Deckels.
    for n in (10, 41, 46, 60):
        clock_state["t"] = 0.0
        lim = PacingLimiter(clock=fake_clock, sleep=fake_sleep)
        for _ in range(n):
            lim.wait()
        erlaubt_ab = (n - 1) * 600.0 / 60
        assert clock_state["t"] >= erlaubt_ab, (
            f"{n} Requests dauerten {clock_state['t']:.1f}s, muessen >= {erlaubt_ab:.1f}s "
            f"dauern (60 Requests je 600s = 1 alle 10s, auch unterhalb des 60er-Deckels)")

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

    # Backfill-Zeitraum: ohne Argumente die gesamte Historie, mit zweien genau die Angabe,
    # alles andere ein Fehler. Feste "heute"-Vorgabe, damit der Check nicht am Kalender haengt.
    heute_di = date(2026, 8, 12)  # ein Mittwoch
    von, bis = _backfill_zeitraum([], heute=heute_di)
    assert bis == date(2026, 8, 11), f"Endtag muss der letzte Handelstag sein, war {bis}"
    assert (bis - von).days == HISTORIE_TAGE
    heute_mo = date(2026, 8, 10)  # Montag -> gestern waere Sonntag
    _, bis_mo = _backfill_zeitraum([], heute=heute_mo)
    assert bis_mo == date(2026, 8, 7), \
        f"an einem Montag muss der Endtag auf Freitag zurueckfallen, war {bis_mo}"
    assert _backfill_zeitraum(["2026-02-17", "2026-08-14"]) == (date(2026, 2, 17), date(2026, 8, 14))
    for kaputt in ([" 2026-02-17"], ["2026-02-17", "2026-08-14", "NQ"]):
        try:
            _backfill_zeitraum(kaputt)
            raise AssertionError(f"{kaputt} haette abgelehnt werden muessen")
        except ValueError:
            pass
    try:
        _backfill_zeitraum(["2026-08-14", "2026-02-17"])
        raise AssertionError("VON nach BIS haette abgelehnt werden muessen")
    except ValueError:
        pass

    # Fehlerklassifikation: nur echte Stoerungen duerfen ein leeres Fenster zum Fehlschlag
    # machen. Verbindungsmeldungen und "keine Daten" (Feiertag/Early Close) nicht -- sonst
    # kaeme ein verkuerzter Handelstag nie zustande bzw. jedes Fenster liefe dreimal.
    assert not _echter_fehler(2104, "Market data farm connection is OK:usfarm")
    assert not _echter_fehler(2158, "Sec-def data farm connection is OK")
    assert not _echter_fehler(
        162, "Historical Market Data Service error message:HMDS query returned no data: "
             "NQH2026@CME Trades")
    assert _echter_fehler(162, "Historical Market Data Service error message:pacing violation"), \
        "die Pacing-Violation traegt dieselbe Nummer 162 -- sie darf NICHT als 'kein Handel' gelten"
    assert _echter_fehler(200, "No security definition has been found for the request")
    assert _echter_fehler(-1, "connection reset")

    # Fetch-Orchestrierung ohne Netz: Stub-IB liefert kanonische Bars.
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
        """`leer_ab`: ab diesem Request-Zaehler liefert der Stub nichts mehr -- mit
        `fehler=True` als echte Stoerung (Pacing), sonst als sauberes 'keine Daten'."""

        def __init__(self, leer_ab: int | None = None, fehler: bool = True):
            self.calls = 0
            self.errorEvent = _StubEvent()
            self._leer_ab, self._fehler = leer_ab, fehler

        def reqHistoricalData(self, contract, endDateTime, **kw):
            self.calls += 1
            if self._leer_ab is not None and self.calls > self._leer_ab:
                if self._fehler:
                    raise RuntimeError("simulierte Pacing-Violation")
                return []
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
                dest, status = fetch_symbol_day(stub, "NQ", tag, pacing, register_path=reg_path)
                assert dest is not None and dest.exists(), "erster Lauf muss eine Datei schreiben"
                assert status.startswith("geschrieben"), status
                erster_call_count = stub.calls
                assert erster_call_count == 46, erster_call_count

                kerzen_komplett = len(pd.read_parquet(dest))

                # Resume: eine vorhandene Tagesdatei kostet KEINEN Request. Frueher wurden
                # trotzdem alle 46 Fenster angefragt und das Ergebnis von write_day_1s()
                # verworfen -- bei einem 6-Monats-Backfill ueber einen halb gefuellten
                # Bestand sind das Stunden Laufzeit fuer nichts.
                stub2 = _StubIB()
                dest2, status2 = fetch_symbol_day(stub2, "NQ", tag, pacing, register_path=reg_path)
                assert dest2 is None and status2.startswith("schon vorhanden"), status2
                assert stub2.calls == 0, \
                    f"vorhandene Tagesdatei muss 0 Requests kosten, waren {stub2.calls}"

                # Regression zu ES 2026-02-19 (Datenverlust): schlaegt auch nur ein Fenster
                # fehl, darf WEDER eine Datei NOCH eine Registerzeile entstehen. Frueher
                # wurde der Tag aus den angekommenen Fenstern geschrieben, sah wie ein
                # fertiger Handelstag aus und war wegen der Nie-Ueberschreiben-Regel
                # dauerhaft eingefroren.
                dest.unlink()
                reg_path.unlink()
                stub3 = _StubIB(leer_ab=35, fehler=True)
                dest3, status3 = fetch_symbol_day(stub3, "NQ", tag, pacing,
                                                  register_path=reg_path, sleep=lambda s: None)
                assert dest3 is None, "fehlgeschlagener Tag darf keinen Pfad liefern"
                # Genau der Fund vom 2026-08-16: der Status darf einen Fehlschlag NICHT als
                # "schon vorhanden/keine Daten" ausgeben.
                assert status3.startswith("FEHLGESCHLAGEN"), status3
                assert "vorhanden" not in status3,                     f"ein Fehlschlag darf nicht wie 'schon da' klingen: {status3}"
                assert not dest.exists(), \
                    "ein Tag mit fehlgeschlagenen Fenstern darf KEINE Tagesdatei hinterlassen"
                assert not reg_path.exists(), \
                    "fehlgeschlagene Fenster duerfen KEINE Registerzeilen hinterlassen"

                # Gegenprobe Early Close: liefert IBKR fuer die letzten Fenster sauber
                # 'keine Daten' statt eines Fehlers, ist der Tag vollstaendig und muss
                # geschrieben werden -- nur eben kuerzer (Realfall Presidents' Day
                # 2026-02-16, CME schliesst 13:00 NY).
                stub4 = _StubIB(leer_ab=38, fehler=False)
                dest4, status4 = fetch_symbol_day(stub4, "NQ", tag, pacing,
                                                  register_path=reg_path)
                assert dest4 is not None and dest4.exists(), \
                    "ein verkuerzter Handelstag muss trotzdem geschrieben werden"
                assert status4.startswith("geschrieben"), status4
                kerzen_kurz = len(pd.read_parquet(dest4))
                assert kerzen_kurz == kerzen_komplett * 38 // 46, \
                    f"Early-Close-Tag muss genau 38/46 der Kerzen haben, waren {kerzen_kurz}"
                assert len(register_load(reg_path)) == 46, \
                    "auch die leeren Fenster gehoeren ins Register (sonst 'kein Trade' == 'nicht geholt')"
            finally:
                DATA_DIR = orig_data_dir
        finally:
            _future_contract = _orig_future_contract

    # Live-Fenster (laufender Handelstag): nur die Fenster nach `seit`, und weder Tagesdatei
    # noch Registerzeile -- genau das haelt die Einfrier-Fehlerklasse aus fetch_symbol_day()
    # vom laufenden Tag fern (siehe live_fenster-Docstring).
    with tempfile.TemporaryDirectory() as tmp:
        orig_data_dir = DATA_DIR
        DATA_DIR = Path(tmp)
        _orig_future_contract = _future_contract
        _future_contract = lambda contract, symbol: contract
        try:
            tag = date(2026, 6, 15)
            fenster = day_windows(tag)
            seit = fenster[-3][1]  # Ende des drittletzten Fensters -> 2 Fenster sind offen
            stub = _StubIB()
            zeilen = live_fenster("NQ", tag, seit, ib=stub,
                                  pacing=PacingLimiter(clock=lambda: 0.0, sleep=lambda s: None))
            assert stub.calls == 2, \
                f"nur die 2 Fenster nach `seit` duerfen geholt werden, waren {stub.calls}"
            assert zeilen, "die offenen Fenster muessen Kerzen liefern"
            grenze = int(seit.timestamp())
            assert all(z["time"] > grenze for z in zeilen), "keine Kerze darf vor `seit` liegen"
            assert [z["time"] for z in zeilen] == sorted({z["time"] for z in zeilen}), \
                "Rueckgabe muss aufsteigend und duplikatfrei sein"
            assert list(DATA_DIR.iterdir()) == [], \
                "live_fenster darf weder Tagesdatei noch Registerzeile hinterlassen"
            # Nichts mehr offen -> kein einziger Request.
            stub_leer = _StubIB()
            assert live_fenster("NQ", tag, fenster[-1][1], ib=stub_leer) == []
            assert stub_leer.calls == 0, "ohne offenes Fenster darf kein Request entstehen"
        finally:
            _future_contract = _orig_future_contract
            DATA_DIR = orig_data_dir

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
    sys.exit(main())
