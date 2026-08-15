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
from collections import Counter
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
ERWARTUNG_FREITAG = (1005, 1030)  # Fr schliesst 17:00 NY = 17h*60min = 1020 Kerzen, gemessener Median 1017


def lade_parquet(symbol: str) -> pd.DataFrame:
    df = pd.read_parquet(CACHE / f"{symbol}_1m.parquet")
    idx = pd.to_datetime(df["time"], unit="s", utc=True).dt.tz_convert(NY)
    df = df.set_index(idx).sort_index()
    return df


def zeit_kreuzprobe(symbol: str, max_tage: int = 20) -> dict:
    """1h-Aggregat aus dem Cache gegen vorhandene TradingView-1h-Exporte, fuer bis zu
    `max_tage` ueberlappende Tage, per Schrittweite ueber den GESAMTEN verfuegbaren
    Datumsbereich verteilt (nicht die ersten N -- die deckten nur eine DST-Saison ab und
    liessen den 4h-Ankerfehler in marktdaten.py unentdeckt, Review-Fund 2026-08-15).
    Bid-vs-Mid ergibt einen kleinen, KONSTANTEN Offset -- ein Zeitversatz faellt als
    grosse, unregelmaessige Abweichung auf."""
    df = lade_parquet(symbol)
    stunden = df.resample("1h", label="left", closed="left", origin="start_day").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()

    treffer, abweichungen = 0, []
    alle = sorted(TV_DIR.glob(f"*/*/*/{symbol} *-*-* 1h.csv"))
    schritt = max(1, len(alle) // max_tage)
    kandidaten = alle[::schritt][:max_tage]
    tage = []
    for tv_pfad in kandidaten:
        tv = pd.read_csv(tv_pfad)
        for _, row in tv.iterrows():
            ts = pd.Timestamp(int(row["time"]), unit="s", tz="UTC").tz_convert(NY)
            if ts not in stunden.index:
                continue
            diff_close = abs(stunden.loc[ts, "close"] - row["close"])
            abweichungen.append(diff_close)
            treffer += 1
            tage.append(str(ts.date()))

    if not abweichungen:
        return {"symbol": symbol, "gepruefte_stunden": 0, "status": "keine_ueberlappung"}
    tage_sortiert = sorted(set(tage))
    avg = sum(abweichungen) / len(abweichungen)
    mx = max(abweichungen)
    # Ein Zeitversatz von 1h verschiebt Werte um eine ganze Bewegung, nicht um ein paar Pips --
    # Schwelle grosszuegig ueber dem plausiblen halben Spread (siehe fetch_histdata.py-Fund
    # 2026-08-14: ~0,0003-0,0004 fuer EURUSD).
    schwelle = 0.005 if "JPY" not in symbol else 0.5
    return {"symbol": symbol, "gepruefte_stunden": treffer,
            "gepruefte_tage": tage_sortiert, "avg_diff": avg, "max_diff": mx,
            "status": "ok" if mx < schwelle else "ZEITVERSATZ_VERDACHT"}


def soll_stunden(tag: date) -> set[int]:
    """Welche NY-Stunden ein Handelstag haben muss.

    Der 24x5-Markt oeffnet Sonntag 17:00 NY und schliesst Freitag 17:00 NY -- ein Freitag hat
    also nur die Stunden 0..16, ein Sonntag nur 17..23, Mo-Do alle 24. Liegt hier, weil die
    Pruefung die Definition besitzt und `fill_luecken_dukascopy.py` sie von hier bezieht."""
    if tag.weekday() == 4:
        return set(range(17))
    if tag.weekday() == 6:
        return set(range(17, 24))
    return set(range(24))


def vollstaendigkeit(symbol: str) -> dict:
    """Kerzen je Tag gegen Erwartungswert, fehlende Tage explizit gelistet statt gezaehlt.

    Zusaetzlich **leere Vollstunden** je Tag (Befund 2026-08-15): im Block Feb-Jul 2023 fehlen
    bei allen 10 Paaren ganze Stunden im Wechsel. Die reine Kerzenzahl macht daraus einen
    unauffaellig wirkenden "zu kurzen Tag" -- fuer fensterbasierte Auswertungen ist aber genau
    das Gegenteil wahr: fehlt die NY-Stunde 10 komplett, ist jede Aussage ueber die
    NY-Killzone dieses Tages leer, ohne dass eine Kennzahl anschlaegt. Deshalb wird die
    Stunden-Luecke eigenstaendig gezaehlt und nicht in der Kerzenzahl versteckt."""
    df = lade_parquet(symbol)
    pro_tag = df.groupby(df.index.date).size()
    belegte_stunden = df.groupby([df.index.date, df.index.hour]).size()
    stunden_je_tag = {tag: set() for tag in pro_tag.index}
    for (tag, stunde) in belegte_stunden.index:
        stunden_je_tag[tag].add(stunde)

    auffaellig = []
    stunden_luecken = []
    for tag, n in pro_tag.items():
        if tag.weekday() == 6:
            lo, hi = ERWARTUNG_SONNTAG
        elif tag.weekday() == 4:
            lo, hi = ERWARTUNG_FREITAG
        else:
            lo, hi = ERWARTUNG_VOLLTAG
        leer = sorted(soll_stunden(tag) - stunden_je_tag[tag])
        # >3 statt >0: einzelne Randstunden an Feiertagen/Jahreswechseln sind normal duenn,
        # ein Loch-Muster wie 2023 reisst durchgaengig sechs bis zwoelf Stunden auf.
        if leer and len(leer) > 3 and n > 50:
            stunden_luecken.append({"tag": str(tag), "kerzen": int(n),
                                    "leere_ny_stunden": leer})
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
            "fehlende_wochentage": luecken[:20], "fehlende_wochentage_gesamt": len(luecken),
            "stunden_luecken": stunden_luecken[:20],
            "stunden_luecken_gesamt": len(stunden_luecken),
            # Monatsweise Verdichtung: eine 20er-Liste verbirgt einen 5-Monats-Block, die
            # Monatszaehlung nicht. Genau daran ist der 2023er Befund lange vorbeigelaufen.
            "stunden_luecken_je_monat": dict(sorted(Counter(
                e["tag"][:7] for e in stunden_luecken).items()))}


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

        # Eigenes Symbol als Regressionsfall fuer den 2023er Befund: ein Mittwoch, an dem nur
        # jede zweite NY-Stunde belegt ist. Genau dieses Muster hat die reine Kerzenzahl-
        # Pruefung durchgelassen -- der Tag sieht wie ein "kurzer Tag" aus, ist aber ein Tag
        # mit zwoelf Loechern mitten in London- und NY-Session. Bewusst ein eigenes Symbol:
        # als zweiter TEST-Tag wuerde er die Attrappen-Quote oben verduennen und deren
        # Aussagekraft zerstoeren.
        loch = Path(tmp) / "marktdaten-tief" / "2026" / "01" / "07.01.2026"
        loch.mkdir(parents=True)
        z2 = ["time,open,high,low,close"]
        b2 = int(datetime(2026, 1, 7, tzinfo=NY).timestamp())
        for stunde in range(0, 24, 2):          # nur die geraden Stunden
            for minute in range(60):
                z2.append(f"{b2 + stunde * 3600 + minute * 60},1.1,1.2,1.0,1.15")
        (loch / "LOCH 2026-01-07 1m (bid).csv").write_text("\n".join(z2), encoding="utf-8")

        global CACHE
        orig_cache = CACHE
        orig_bp_cache = build_parquet.CACHE
        cache = Path(tmp) / "cache"
        build_parquet.build("TEST", tief_dir=Path(tmp) / "marktdaten-tief", cache_dir=cache)
        build_parquet.build("LOCH", tief_dir=Path(tmp) / "marktdaten-tief", cache_dir=cache)
        build_parquet.CACHE = cache
        globals()["CACHE"] = cache
        try:
            q = attrappen_quote("TEST")
            assert q["quote"] == 1.0 and q["status"] == "AUFFAELLIG", q

            v = vollstaendigkeit("TEST")
            assert v["tage_gesamt"] == 1, v

            # Negativkontrolle: unter 50 Kerzen ist ein Feiertag, kein Loch. Ohne diesen Fall
            # wuerde ein zu scharfer Schwellwert nicht auffallen.
            assert v["stunden_luecken_gesamt"] == 0, v["stunden_luecken"]

            # Der Loch-Tag muss anschlagen, mit den konkreten leeren Stunden.
            vl = vollstaendigkeit("LOCH")
            assert vl["stunden_luecken_gesamt"] == 1, vl
            assert vl["stunden_luecken"][0]["leere_ny_stunden"] == list(range(1, 24, 2)), vl
            assert vl["stunden_luecken_je_monat"] == {"2026-01": 1}, vl

            # Soll-Stunden an den Wochengrenzen des 24x5-Marktes
            assert soll_stunden(date(2026, 1, 7)) == set(range(24))       # Mittwoch
            assert soll_stunden(date(2026, 1, 9)) == set(range(17))       # Freitag
            assert soll_stunden(date(2026, 1, 11)) == set(range(17, 24))  # Sonntag
        finally:
            # Beide zuruecksetzen: build_parquet.CACHE blieb vorher auf dem geloeschten
            # Tempdir stehen und haette jeden spaeteren Import im selben Prozess vergiftet
            # (Review-Fund 2026-08-15, faellt beim Einhaengen in selfcheck.py auf).
            globals()["CACHE"] = orig_cache
            build_parquet.CACHE = orig_bp_cache
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
        if v["stunden_luecken_gesamt"]:
            monate = ", ".join(f"{m} ({n})" for m, n in v["stunden_luecken_je_monat"].items())
            warnungen.append(f"STUNDEN-LUECKEN: {v['stunden_luecken_gesamt']} Handelstage mit "
                             f">3 komplett leeren NY-Stunden -- {monate}")
        if a["status"] != "ok":
            warnungen.append(f"ATTRAPPEN: {a}")
        status = "OK" if not warnungen else "PRUEFEN"
        print(f"[{sym}] {status}" + ("".join(f"\n  ! {w}" for w in warnungen)))

    write_result("forex_verify_report", ergebnis)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
