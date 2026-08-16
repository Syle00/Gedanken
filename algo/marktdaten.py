#!/usr/bin/env python3
"""Ein Einstieg fuer alle Backtest-Module: `bars(symbol, tf, von, bis)` liefert die bestehende
`Bar`-Liste, egal ob das Symbol aus raw/marktdaten/ (Futures, CSV je Timeframe) oder aus dem
histdata-Parquet-Cache (Forex, resampled aus 1m) stammt. Kein Detektor merkt den Unterschied.

Aufruf:
    python algo/marktdaten.py --demo
"""
from __future__ import annotations

import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from analyze_ohlc import Bar, DATA_DIR, NY, SESSION_TYP, load  # noqa: E402
from build_parquet import CACHE  # noqa: E402

PANDAS_FREQ = {"1m": "1min", "5m": "5min", "15m": "15min", "1h": "1h", "4h": "4h", "1d": "1D"}
OHLC = {"open": "first", "high": "max", "low": "min", "close": "last"}
# Timeframes, deren Buckets an der NY-Wanduhr haengen muessen statt am tz-awaren Index:
# pandas verankert `origin="start_day"` genau EINMAL (im DST-Zustand der ersten Kerze) und
# re-verankert nicht je DST-Wechsel. Fuer Mehrstunden-Buckets, die keinen DST-verschobenen
# Tag glatt teilen, landeten die Grenzen dadurch im halben Bestand 3h daneben
# (Review-Fund 2026-08-15: Jan 2025 lieferte 03/07/11/15/19/23 statt 00/04/08/12/16/20).
# 1m/5m/15m/1h/1d sind nachweislich nicht betroffen und behalten den tz-awaren Pfad --
# der liefert am Fall-Back-Tag korrekt 25 Stunden statt zweier zusammengefalteter.
WANDUHR_TF = {"4h"}


def trading_day(ts: pd.Timestamp, daily: bool = False):
    """Globex-Handelstag: 18:00 NY des Vortages bis 17:00 NY. Uebernommen aus
    fetch_yfinance.py (dort 2026-08-16 entfallen) -- quellenunabhaengig, gilt fuer
    IBKR-Daten genauso."""
    if daily:
        return ts.date()
    ts = ts.tz_convert(NY)
    return ts.date() + timedelta(days=1) if ts.hour >= 18 else ts.date()


def flatten(df: pd.DataFrame) -> pd.DataFrame:
    """MultiIndex-Spalten auf die erste Ebene reduzieren."""
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df


def resample_bars(bars_in: list[Bar], tf: str) -> list[Bar]:
    """Bar-Liste auf einen groeberen Timeframe verdichten. Anker an NY-Mitternacht ueber
    origin='start_day' -- der Index ist NY-lokalisiert, ohne den Anker laegen die Buckets an
    UTC-Mitternacht. Fuer WANDUHR_TF (4h) wird tz-naiv resampled und danach re-lokalisiert."""
    if not bars_in:
        return []
    df = pd.DataFrame(
        {"open": [b.o for b in bars_in], "high": [b.h for b in bars_in],
         "low": [b.l for b in bars_in], "close": [b.c for b in bars_in]},
        index=pd.DatetimeIndex([b.t for b in bars_in]),
    )
    if tf in WANDUHR_TF:
        res = df.tz_localize(None).resample(
            PANDAS_FREQ[tf], label="left", closed="left").agg(OHLC).dropna()
        res.index = res.index.tz_localize(NY, ambiguous=True, nonexistent="shift_forward")
        df = res
    else:
        df = df.resample(PANDAS_FREQ[tf], label="left", closed="left",
                         origin="start_day").agg(OHLC).dropna()
    idx_py = df.index.to_pydatetime()
    opens, highs, lows, closes = (df[c].to_numpy() for c in ("open", "high", "low", "close"))
    return [Bar(t, float(o), float(h), float(l), float(c))
            for t, o, h, l, c in zip(idx_py, opens, highs, lows, closes)]


def bars(symbol: str, tf: str, von: date | None = None, bis: date | None = None) -> list[Bar]:
    if SESSION_TYP.get(symbol) == "24x5":
        return _forex_bars(symbol, tf, von, bis)
    return _futures_bars(symbol, tf, von, bis)


def _futures_bars(symbol: str, tf: str, von: date | None, bis: date | None) -> list[Bar]:
    """Unveraendertes Verhalten gegenueber backtest_common.find_days()/load() fuer CSV-TFs --
    ein Bar je Tagesordner-Datei. Fuer tf == '1s' wird stattdessen die Tages-Parquet-Datei
    aus algo/fetch_ibkr.py gelesen (siehe _load_1s_parquet)."""
    out: list[Bar] = []
    for day_dir in sorted(DATA_DIR.glob("*/*/*")):
        if not day_dir.is_dir():
            continue
        try:
            day = datetime.strptime(day_dir.name, "%d.%m.%Y").date()
        except ValueError:
            continue
        if von and day < von:
            continue
        if bis and day > bis:
            continue
        if tf == "1s":
            dateien = sorted(day_dir.glob(f"{symbol} * 1s.parquet"))
            if dateien:
                out.extend(_load_1s_parquet(dateien[0]))
            continue
        dateien = sorted(f for f in day_dir.glob(f"{symbol} * {tf}.csv") if "RTH" not in f.name)
        if dateien:
            out.extend(load(dateien[0]))
    out.sort(key=lambda b: b.t)
    return out


def _load_1s_parquet(path: Path) -> list[Bar]:
    """IBKR-1s-Tagesdatei -> Bar-Liste. `time` ist UNIX-Sekunden UTC (formatDate=2 in
    fetch_ibkr.py), deshalb direkte tz_convert(NY) ohne Zwischenschritt."""
    df = pd.read_parquet(path)
    idx_series = pd.to_datetime(df["time"], unit="s", utc=True).dt.tz_convert(NY)
    idx_py = pd.DatetimeIndex(idx_series).to_pydatetime()
    return [Bar(t, float(o), float(h), float(l), float(c), float(v))
            for t, o, h, l, c, v in zip(idx_py, df["open"], df["high"], df["low"],
                                        df["close"], df["volume"])]


def _forex_bars(symbol: str, tf: str, von: date | None, bis: date | None) -> list[Bar]:
    """Liest den 1m-Parquet-Cache, resampled bei Bedarf. Anker an NY-Mitternacht: der Index
    ist bereits NY-lokalisiert, `origin="start_day"` verankert Resample-Buckets deshalb an
    NY-00:00, nicht UTC-Mitternacht (Spec §5.3). Fuer `WANDUHR_TF` wird stattdessen auf der
    tz-naiven NY-Wanduhr resampled und danach re-lokalisiert -- siehe Kommentar dort."""
    df = pd.read_parquet(CACHE / f"{symbol}_1m.parquet")
    idx = pd.to_datetime(df["time"], unit="s", utc=True).dt.tz_convert(NY)
    df = df.set_index(idx).drop(columns="time").sort_index()

    idx_py = df.index.to_pydatetime()
    opens, highs, lows, closes = (df[c].to_numpy() for c in ("open", "high", "low", "close"))
    out = [Bar(t, o, h, l, c) for t, o, h, l, c in zip(idx_py, opens, highs, lows, closes)]
    if tf != "1m":
        out = resample_bars(out, tf)

    if von:
        out = [b for b in out if b.t.date() >= von]
    if bis:
        out = [b for b in out if b.t.date() <= bis]

    return out


def _demo() -> None:
    """Selbstcheck: winziger Parquet-Cache in ein Tempdir, prueft Resample-Anker (NY-
    Mitternacht) und von/bis-Filter, sowie den 1s-Futures-Pfad (IBKR-Anbindung)."""
    import tempfile
    import build_parquet as bp

    with tempfile.TemporaryDirectory() as tmp:
        tief = Path(tmp) / "marktdaten-tief" / "2026" / "01" / "05.01.2026"
        tief.mkdir(parents=True)
        basis = int(datetime(2026, 1, 5, 0, 0, tzinfo=NY).timestamp())
        zeilen = ["time,open,high,low,close"]
        for i in range(240):  # 0:00-3:59 NY, in 1m-Schritten
            zeilen.append(f"{basis + i * 60},1.1,1.1001,1.0999,1.1")
        (tief / "TEST 2026-01-05 1m (bid).csv").write_text("\n".join(zeilen), encoding="utf-8")

        cache = Path(tmp) / "cache"
        bp.build("TEST", tief_dir=Path(tmp) / "marktdaten-tief", cache_dir=cache)

        global CACHE
        orig = CACHE
        CACHE = cache
        SESSION_TYP["TEST"] = "24x5"
        try:
            b1m = bars("TEST", "1m")
            assert len(b1m) == 240, len(b1m)
            assert b1m[0].t == datetime(2026, 1, 5, 0, 0, tzinfo=NY), b1m[0].t

            b4h = bars("TEST", "4h")
            # Anker an NY-Mitternacht: die erste 4h-Kerze muss um 0:00 beginnen, nicht
            # verschoben durch UTC-Anker (waere hier 19:00 des Vortags, siehe Spec §5.3).
            assert b4h[0].t == datetime(2026, 1, 5, 0, 0, tzinfo=NY), b4h[0].t
            assert len(b4h) == 1, len(b4h)  # 4 Stunden Daten -> genau eine 4h-Kerze

            gefiltert = bars("TEST", "1m", von=date(2026, 1, 6))
            assert gefiltert == [], "von-Filter muss ausserhalb liegende Tage ausschliessen"
        finally:
            CACHE = orig
            del SESSION_TYP["TEST"]

    # 1s-Parquet-Zweig (IBKR-Anbindung, algo/fetch_ibkr.py): eigenes Tempdir als DATA_DIR,
    # weil _futures_bars() (anders als der Forex-Pfad oben) direkt gegen das importierte
    # DATA_DIR aus analyze_ohlc glob't.
    import analyze_ohlc as ao
    with tempfile.TemporaryDirectory() as tmp:
        orig_dd = ao.DATA_DIR
        global DATA_DIR
        try:
            ao.DATA_DIR = DATA_DIR = Path(tmp)
            tag_dir = DATA_DIR / "2026" / "06" / "15.06.2026"
            tag_dir.mkdir(parents=True)
            df = pd.DataFrame({
                "time": [1781544600, 1781544601, 1781544602],
                "open": [100.0, 100.25, 100.5], "high": [100.5, 100.5, 100.75],
                "low": [99.75, 100.0, 100.25], "close": [100.25, 100.5, 100.5],
                "volume": [3, 5, 2], "contract": ["NQU2026"] * 3,
            })
            df.to_parquet(tag_dir / "NQ 2026-06-15 1s.parquet", index=False)
            b1s = bars("NQ", "1s")
            assert len(b1s) == 3, len(b1s)
            assert b1s[0].t == datetime(2026, 6, 15, 13, 30, tzinfo=NY), b1s[0].t
            assert b1s[0].v == 3.0, b1s[0].v
        finally:
            ao.DATA_DIR = DATA_DIR = orig_dd

    # --- trading_day: Globex-Grenze 18:00 NY -------------------------------
    ts_abend = pd.Timestamp("2026-08-13 18:30", tz=NY)
    ts_morgen = pd.Timestamp("2026-08-13 09:30", tz=NY)
    assert trading_day(ts_abend) == date(2026, 8, 14), "18:30 NY gehoert zum Folgetag"
    assert trading_day(ts_morgen) == date(2026, 8, 13), "09:30 NY gehoert zum selben Tag"
    assert trading_day(ts_abend, daily=True) == date(2026, 8, 13), "daily=True nimmt das Kalenderdatum"

    # --- flatten: MultiIndex-Spalten plaetten ------------------------------
    multi = pd.DataFrame([[1.0]], columns=pd.MultiIndex.from_tuples([("close", "NQ")]))
    assert list(flatten(multi).columns) == ["close"], "flatten muss die zweite Ebene entfernen"

    # --- resample_bars: 1m -> 5m, OHLC-Aggregation korrekt -----------------
    basis = [Bar(datetime(2026, 8, 13, 9, 30 + i, tzinfo=NY), 100.0 + i, 101.0 + i,
                 99.0 + i, 100.5 + i) for i in range(5)]
    fuenf = resample_bars(basis, "5m")
    assert len(fuenf) == 1, f"5 1m-Kerzen ergeben 1 5m-Kerze, nicht {len(fuenf)}"
    assert fuenf[0].o == 100.0, "open = erste Kerze"
    assert fuenf[0].h == 105.0, "high = Maximum"
    assert fuenf[0].l == 99.0, "low = Minimum"
    assert fuenf[0].c == 104.5, "close = letzte Kerze"

    _demo_dst()
    print("marktdaten: Selbstcheck ok")


def _demo_dst() -> None:
    """Regressionswaechter fuer den DST-Ankerfehler (Review-Fund 2026-08-15): 4h-Buckets
    muessen VOR und NACH einem DST-Wechsel auf denselben Wanduhr-Stunden landen. Der alte
    tz-aware `origin="start_day"`-Pfad verankerte einmalig im DST-Zustand der ersten Kerze
    und lieferte hier ab dem 2. November 03/07/11/... statt 00/04/08/...

    Fenster: 31.10.2025 (EDT) bis 03.11.2025 (EST), Umstellung "fall back" am 02.11.2025."""
    import tempfile
    import build_parquet as bp

    start = int(datetime(2025, 10, 31, 0, 0, tzinfo=NY).timestamp())
    ende = int(datetime(2025, 11, 4, 0, 0, tzinfo=NY).timestamp())  # 4 Tage, davon einer 25h

    with tempfile.TemporaryDirectory() as tmp:
        tief = Path(tmp) / "marktdaten-tief" / "2025" / "10" / "31.10.2025"
        tief.mkdir(parents=True)
        zeilen = ["time,open,high,low,close"]
        for ts in range(start, ende, 60):
            zeilen.append(f"{ts},1.1,1.1001,1.0999,1.1")
        (tief / "TESTDST 2025-10-31 1m (bid).csv").write_text("\n".join(zeilen), encoding="utf-8")

        cache = Path(tmp) / "cache"
        bp.build("TESTDST", tief_dir=Path(tmp) / "marktdaten-tief", cache_dir=cache)

        global CACHE
        orig = CACHE
        CACHE = cache
        SESSION_TYP["TESTDST"] = "24x5"
        try:
            b4h = bars("TESTDST", "4h")
            nach_tag: dict[date, list[int]] = {}
            for b in b4h:
                nach_tag.setdefault(b.t.date(), []).append(b.t.hour)
            erwartet = [0, 4, 8, 12, 16, 20]
            for tag in (date(2025, 10, 31), date(2025, 11, 1),
                        date(2025, 11, 2), date(2025, 11, 3)):
                assert nach_tag.get(tag) == erwartet, (
                    f"4h-Buckets am {tag} liegen auf {nach_tag.get(tag)} statt {erwartet} "
                    "-- DST-Anker verrutscht")
            # Kein Datenverlust ueber den Wechsel: 4 Tage a 6 Buckets, keiner leer.
            assert len(b4h) == 24, len(b4h)
        finally:
            CACHE = orig
            del SESSION_TYP["TESTDST"]


def main() -> int:
    if "--demo" in sys.argv:
        _demo()
        return 0
    print(__doc__)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
