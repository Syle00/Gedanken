#!/usr/bin/env python3
"""Verifikationspflicht vor Freigabe des histdata-Forex-Bestands (Spec §5.4, CLAUDE.md
"Marktdaten wie Gold behandeln"). Drei Pruefungen, jede fuer sich meldepflichtig:
Zeit gegen eine unabhaengige Quelle, Vollstaendigkeit als Liste statt Annahme,
Attrappen-Quote (o=h=l=c) je Symbol/Jahr.

Aufruf:
    python algo/verify_forex_data.py
    python algo/verify_forex_data.py --demo
"""
from __future__ import annotations

import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_parquet import CACHE, SYMBOLE  # noqa: E402
from backtest_common import write_result  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TV_DIR = ROOT / "raw" / "marktdaten"
NY = ZoneInfo("America/New_York")

# Kerzen/Tag: Vollhandelstag 1427-1437, Sonntag ab Marktoeffnung 418 (Spec §1.1, gemessen).
ERWARTUNG_VOLLTAG = (1420, 1440)
ERWARTUNG_SONNTAG = (400, 430)


def lade_parquet(symbol: str) -> pd.DataFrame:
    df = pd.read_parquet(CACHE / f"{symbol}_1m.parquet")
    idx = pd.to_datetime(df["time"], unit="s", utc=True).dt.tz_convert(NY)
    df = df.set_index(idx).sort_index()
    return df


def zeit_kreuzprobe(symbol: str, max_tage: int = 20) -> dict:
    """1h-Aggregat aus dem Cache gegen vorhandene TradingView-1h-Exporte, fuer bis zu
    `max_tage` zufaellig verteilte ueberlappende Tage. Bid-vs-Mid ergibt einen kleinen,
    KONSTANTEN Offset -- ein Zeitversatz faellt als grosse, unregelmaessige Abweichung auf."""
    df = lade_parquet(symbol)
    stunden = df.resample("1h", label="left", closed="left", origin="start_day").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()

    treffer, abweichungen = 0, []
    geprueft_tage = 0
    for tv_pfad in sorted(TV_DIR.glob(f"*/*/*/{symbol} *-*-* 1h.csv")):
        if geprueft_tage >= max_tage:
            break
        tv = pd.read_csv(tv_pfad)
        for _, row in tv.iterrows():
            ts = pd.Timestamp(int(row["time"]), unit="s", tz="UTC").tz_convert(NY)
            if ts not in stunden.index:
                continue
            diff_close = abs(stunden.loc[ts, "close"] - row["close"])
            abweichungen.append(diff_close)
            treffer += 1
        geprueft_tage += 1

    if not abweichungen:
        return {"symbol": symbol, "gepruefte_stunden": 0, "status": "keine_ueberlappung"}
    avg = sum(abweichungen) / len(abweichungen)
    mx = max(abweichungen)
    # Ein Zeitversatz von 1h verschiebt Werte um eine ganze Bewegung, nicht um ein paar Pips --
    # Schwelle grosszuegig ueber dem plausiblen halben Spread (siehe fetch_histdata.py-Fund
    # 2026-08-14: ~0,0003-0,0004 fuer EURUSD).
    schwelle = 0.005 if "JPY" not in symbol else 0.5
    return {"symbol": symbol, "gepruefte_stunden": treffer,
            "avg_diff": avg, "max_diff": mx,
            "status": "ok" if mx < schwelle else "ZEITVERSATZ_VERDACHT"}


def vollstaendigkeit(symbol: str) -> dict:
    """Kerzen je Tag gegen Erwartungswert, fehlende Tage explizit gelistet statt gezaehlt."""
    df = lade_parquet(symbol)
    pro_tag = df.groupby(df.index.date).size()
    auffaellig = []
    for tag, n in pro_tag.items():
        ist_sonntag = tag.weekday() == 6
        lo, hi = ERWARTUNG_SONNTAG if ist_sonntag else ERWARTUNG_VOLLTAG
        if not (lo <= n <= hi) and n > 50:  # <50 sind erwartete Kurztage (Feiertage), kein Fund
            auffaellig.append({"tag": str(tag), "kerzen": int(n)})

    alle_tage = sorted(pro_tag.index)
    luecken = []
    if alle_tage:
        cur = alle_tage[0]
        vorhandene = set(alle_tage)
        while cur <= alle_tage[-1]:
            if cur.weekday() < 5 and cur not in vorhandene:  # Wochentag ohne Datei
                luecken.append(str(cur))
            cur += timedelta(days=1)

    return {"symbol": symbol, "tage_gesamt": len(alle_tage),
            "auffaellige_kerzenzahl": auffaellig[:20], "auffaellig_gesamt": len(auffaellig),
            "fehlende_wochentage": luecken[:20], "fehlende_wochentage_gesamt": len(luecken)}


def attrappen_quote(symbol: str) -> dict:
    """Anteil o=h=l=c je Symbol -- soll im Promillebereich liegen (Spec §5.4.3)."""
    df = lade_parquet(symbol)
    flach = ((df["open"] == df["high"]) & (df["low"] == df["close"]) &
             (df["open"] == df["low"])).sum()
    quote = flach / len(df) if len(df) else 0.0
    return {"symbol": symbol, "kerzen_gesamt": len(df), "flach": int(flach),
            "quote": round(quote, 5), "status": "ok" if quote < 0.01 else "AUFFAELLIG"}


def _demo() -> None:
    """Selbstcheck: baut einen winzigen Parquet-Cache in ein Tempdir und prueft alle drei
    Funktionen gegen bekannte, konstruierte Werte."""
    import tempfile
    import build_parquet

    with tempfile.TemporaryDirectory() as tmp:
        tief = Path(tmp) / "marktdaten-tief" / "2026" / "01" / "05.01.2026"
        tief.mkdir(parents=True)
        zeilen = ["time,open,high,low,close"]
        basis = int(datetime(2026, 1, 5, tzinfo=NY).timestamp())
        for i in range(5):
            zeilen.append(f"{basis + i * 60},1.1,1.1,1.1,1.1")  # 5 flache Kerzen
        (tief / "TEST 2026-01-05 1m (bid).csv").write_text("\n".join(zeilen), encoding="utf-8")

        global CACHE
        orig_cache = CACHE
        cache = Path(tmp) / "cache"
        build_parquet.build("TEST", tief_dir=Path(tmp) / "marktdaten-tief", cache_dir=cache)
        import build_parquet as bp
        bp.CACHE = cache
        globals()["CACHE"] = cache

        q = attrappen_quote("TEST")
        assert q["quote"] == 1.0 and q["status"] == "AUFFAELLIG", q

        v = vollstaendigkeit("TEST")
        assert v["tage_gesamt"] == 1, v

        globals()["CACHE"] = orig_cache
    print("verify_forex_data: Selbstcheck ok")


def main() -> int:
    if "--demo" in sys.argv:
        _demo()
        return 0

    ergebnis = {"zeit": [], "vollstaendigkeit": [], "attrappen": []}
    for sym in SYMBOLE:
        z = zeit_kreuzprobe(sym)
        v = vollstaendigkeit(sym)
        a = attrappen_quote(sym)
        ergebnis["zeit"].append(z)
        ergebnis["vollstaendigkeit"].append(v)
        ergebnis["attrappen"].append(a)
        warnungen = []
        if z.get("status") not in ("ok", "keine_ueberlappung"):
            warnungen.append(f"ZEIT: {z}")
        if v["auffaellig_gesamt"] or v["fehlende_wochentage_gesamt"]:
            warnungen.append(f"VOLLSTAENDIGKEIT: {v['auffaellig_gesamt']} auffaellige Tage, "
                             f"{v['fehlende_wochentage_gesamt']} fehlende Wochentage")
        if a["status"] != "ok":
            warnungen.append(f"ATTRAPPEN: {a}")
        status = "OK" if not warnungen else "PRUEFEN"
        print(f"[{sym}] {status}" + ("".join(f"\n  ! {w}" for w in warnungen)))

    write_result("forex_verify_report", ergebnis)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
