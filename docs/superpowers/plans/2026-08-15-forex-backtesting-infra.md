# Forex-Backtesting-Infrastruktur Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Den histdata.com-Bulk-Bestand (`raw/marktdaten-tief/`, 73.100 Dateien, 10 Forex-Paare,
2003–2026, 1m) für die bestehenden ICT-Backtest-Module nutzbar machen — mit einem Guard, der
Module, die eine Handels-Eröffnung voraussetzen (ORG, NDOG, 1.p-FVG), auf Forex korrekt
deaktiviert, weil ein 24/5-Markt weder Schluss noch Eröffnung kennt.

**Architecture:** Ein neuer Parquet-Cache (`algo/build_parquet.py`) verdichtet die 73.100 CSVs
auf 10 Dateien. Ein gemeinsamer Loader (`algo/marktdaten.py::bars()`) liefert daraus (oder für
Futures unverändert aus `raw/marktdaten/`) `Bar`-Listen im bestehenden Format — kein Detektor
wird angefasst. Zwei neue Dicts (`SESSION_TYP`, `PIP_SIZE`) in `tools/analyze_ohlc.py` steuern
Tagesgrenze und den Eröffnungs-Guard an der geteilten Basis (`org_gap()`/`ndog_gap()`), nicht
pro Modul.

**Tech Stack:** Python-Stdlib (`tools/analyze_ohlc.py` bleibt frei von Abhängigkeiten), pandas
(bereits vorhanden), neu: `pyarrow` (Parquet-Backend).

**Spec:** `docs/superpowers/specs/2026-08-14-forex-backtesting-design.md`

## Global Constraints

- `algo/selfcheck.py` muss nach jeder Umstellung grün bleiben und **dieselben MNQ-Zahlen**
  liefern wie vorher (Spec §7) — jede Abweichung ist ein Bug, kein Fortschritt.
- Kein Detektor in `tools/analyze_ohlc.py` (`fvgs()`, `swings()`, `sweeps()`, `untouched_levels()`,
  `hp_context()`, ...) wird verändert — nur `org_gap()`/`ndog_gap()` bekommen den Guard.
- Kein `$`-P&L, kein Pip-Wert in `pnl.py`, keine Forex-Regel in `algo/rules.py` (Spec §2 —
  Nicht-Ziele).
- Neue Caches (`algo/cache/`) sind gitignored und jederzeit aus `raw/` neu baubar — `raw/`
  selbst bleibt unveränderlich (Layer-1-Regel) und ist bewusst NICHT gitignored (siehe
  `.gitignore`-Root-Kommentar "Vault soll vollständig gesichert sein").
- Jede neue Datenpipeline wird gegen eine unabhängige Quelle zeitlich verifiziert, bevor sie als
  nutzbar gilt (CLAUDE.md "Zeit vor Preis", Spec §5.4) — Löschungen an `raw/marktdaten/` erst
  nach ausdrücklicher Freigabe (Spec §8), nie im selben Schritt wie das Messen.

---

## Task 1: Parquet-Cache aus dem histdata-Bestand

**Files:**
- Create: `algo/build_parquet.py`
- Modify: `algo/requirements.txt` (Zeile anhängen: `pyarrow>=15.0`)
- Modify: `.gitignore` (neue Zeile `algo/cache/` unter einem neuen Abschnitt)

**Interfaces:**
- Produces: `build(symbol: str, tief_dir: Path = TIEF_DIR, cache_dir: Path = CACHE) -> Path`
  — liest alle `<SYM> * 1m (bid).csv` unter `tief_dir`, schreibt
  `cache_dir/<SYM>_1m.parquet` (Spalten `time` int64 Epoch-UTC-Sekunden, `open/high/low/close`
  float64, sortiert nach `time`, keine Duplikate). Wird von Task 5 (`marktdaten.py`) gelesen.

- [ ] **Step 1: Dependency ergänzen**

In `algo/requirements.txt` ans Ende anhängen:
```
pyarrow>=15.0        # Parquet-Backend fuer den histdata-Forex-Cache (algo/build_parquet.py)
```
Ausführen: `pip install pyarrow>=15.0` und verifizieren mit `python -c "import pyarrow; print(pyarrow.__version__)"`.

- [ ] **Step 2: `.gitignore` ergänzen**

Am Ende von `.gitignore` einen neuen Abschnitt anhängen:
```
# --- Algo Forex-Cache ---
# Parquet-Verdichtung von raw/marktdaten-tief/ (73.100 CSVs -> 10 Dateien), jederzeit aus
# raw/ neu baubar (algo/build_parquet.py) -- anders als raw/ selbst gehoert das nicht in
# die Historie (gleiche Begruendung wie graphify-out/ oben).
algo/cache/
```

- [ ] **Step 3: Modul-Grundgerüst mit Selbstcheck schreiben**

```python
#!/usr/bin/env python3
"""Verdichtet raw/marktdaten-tief/ (73.100 CSVs, histdata.com-Bulk-Import, siehe PLAN.md
2026-08-14) zu 10 Parquet-Dateien -- eine je Symbol. Grund: 92 Mio. Zeilen als CSV zu
parsen kostet Minuten pro Backtest-Lauf, Parquet Sekunden.

Idempotent und jederzeit aus raw/ neu baubar -- algo/cache/ ist gitignored (siehe
.gitignore-Kommentar), kein Datenverlust bei Loeschung.

Aufruf:
    python algo/build_parquet.py                 # alle 10 Symbole
    python algo/build_parquet.py EURUSD GBPUSD    # nur diese
    python algo/build_parquet.py --demo           # Selbstcheck ohne Netz/Dateien
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
TIEF_DIR = ROOT / "raw" / "marktdaten-tief"
CACHE = Path(__file__).resolve().parent / "cache"

SYMBOLE = ("EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD",
           "USDCAD", "NZDUSD", "EURJPY", "EURGBP", "GBPJPY")


def build(symbol: str, tief_dir: Path = TIEF_DIR, cache_dir: Path = CACHE) -> Path:
    dateien = sorted(tief_dir.glob(f"*/*/*/{symbol} *-*-* 1m (bid).csv"))
    if not dateien:
        raise FileNotFoundError(f"Keine histdata-Dateien fuer {symbol} unter {tief_dir}")

    frames = [pd.read_csv(p, usecols=["time", "open", "high", "low", "close"])
              for p in dateien]
    df = pd.concat(frames, ignore_index=True)
    df = df.sort_values("time").drop_duplicates(subset="time", keep="first")
    df["time"] = df["time"].astype("int64")
    for spalte in ("open", "high", "low", "close"):
        df[spalte] = df[spalte].astype("float64")

    cache_dir.mkdir(parents=True, exist_ok=True)
    ziel = cache_dir / f"{symbol}_1m.parquet"
    df.to_parquet(ziel, index=False)
    return ziel


def _demo() -> None:
    """Selbstcheck ohne echte histdata-Dateien -- baut zwei winzige CSVs in ein Tempdir."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        tief = Path(tmp) / "marktdaten-tief" / "2026" / "01" / "01.01.2026"
        tief.mkdir(parents=True)
        (tief / "TEST 2026-01-01 1m (bid).csv").write_text(
            "time,open,high,low,close\n"
            "1735689600,1.1,1.1,1.1,1.1\n"
            "1735689660,1.2,1.2,1.2,1.2\n"
            "1735689600,1.1,1.1,1.1,1.1\n",  # Duplikat -- muss verworfen werden
            encoding="utf-8",
        )
        cache = Path(tmp) / "cache"
        ziel = build("TEST", tief_dir=Path(tmp) / "marktdaten-tief", cache_dir=cache)
        df = pd.read_parquet(ziel)
        assert len(df) == 2, f"Duplikat nicht entfernt: {len(df)} Zeilen"
        assert list(df["time"]) == [1735689600, 1735689660], "nicht sortiert"
        assert df["open"].dtype == "float64" and df["time"].dtype == "int64"
    print("build_parquet: Selbstcheck ok")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("symbole", nargs="*", help="z.B. EURUSD GBPUSD (Default: alle 10)")
    ap.add_argument("--demo", action="store_true")
    a = ap.parse_args()

    if a.demo:
        _demo()
        return 0

    for sym in (a.symbole or SYMBOLE):
        ziel = build(sym)
        groesse_mb = ziel.stat().st_size / 1_000_000
        print(f"[{sym}] {ziel.name}: {groesse_mb:.1f} MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Selbstcheck laufen lassen**

Ausführen: `python algo/build_parquet.py --demo`
Erwartet: `build_parquet: Selbstcheck ok`

- [ ] **Step 5: Echten Cache bauen**

Ausführen: `python algo/build_parquet.py`
Erwartet: 10 Zeilen `[SYM] SYM_1m.parquet: NN.N MB`, keine Exception. Größenordnung laut Spec
§5.2 ca. 400–600 MB gesamt gegen 3,81 GB roh — deutlich außerhalb dieser Spanne (z.B. > 1 GB
oder < 100 MB) ist ein Hinweis auf einen Bug, nicht nur eine Abweichung, und wird gemeldet statt
weitergebaut.

- [ ] **Step 6: Commit**

```bash
git add algo/build_parquet.py algo/requirements.txt .gitignore
git commit -m "feat: Parquet-Cache fuer den histdata-Forex-Bestand"
```

---

## Task 2: Verifikation vor Freigabe der Daten (Spec §5.4)

**Files:**
- Create: `algo/verify_forex_data.py`
- Test: eingebauter `--demo`-Selbstcheck (Projektstandard, kein separates `tests/`-Verzeichnis
  im Repo)

**Interfaces:**
- Consumes: `algo.build_parquet.CACHE`-Pfade aus Task 1 (müssen existieren, sonst
  `FileNotFoundError` mit klarer Meldung).
- Produces: `algo/results/forex_verify_report.json` mit drei Blöcken (`zeit`, `vollstaendigkeit`,
  `attrappen`). Nichts davon wird von späteren Tasks importiert — reiner Freigabe-Report, der
  vor Task 5 einmal grün sein muss.

- [ ] **Step 1: Zeit-Kreuzprobe schreiben**

Vergleicht 1h-Aggregate aus dem Parquet-Cache gegen die vorhandenen `raw/marktdaten/*/1h.csv`
TradingView-Exporte (nicht die 1m-Attrappen, siehe Spec §1.4) für überlappende Tage.

```python
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
```

- [ ] **Step 2: Selbstcheck laufen lassen**

Ausführen: `python algo/verify_forex_data.py --demo`
Erwartet: `verify_forex_data: Selbstcheck ok`

- [ ] **Step 3: Echte Verifikation laufen lassen und Ergebnis lesen**

Ausführen: `python algo/verify_forex_data.py`
Erwartet: für jedes der 10 Symbole eine Zeile `[SYM] OK` oder `[SYM] PRUEFEN` mit Detailzeilen.
**Schlägt einer der drei Punkte fehl (Status `PRUEFEN` oder `ZEITVERSATZ_VERDACHT`), wird das
dem Nutzer gemeldet und Task 3 erst nach Rückmeldung fortgesetzt — nicht stillschweigend
weitergebaut** (Spec §5.4, harte Vorgabe).

- [ ] **Step 4: Commit**

```bash
git add algo/verify_forex_data.py
git commit -m "feat: Zeit-/Vollstaendigkeits-/Attrappen-Verifikation fuer den Forex-Cache"
```

---

## Task 3: `SESSION_TYP`/`PIP_SIZE` + Eröffnungs-Guard in `tools/analyze_ohlc.py`

**Files:**
- Modify: `tools/analyze_ohlc.py:59-65` (neue Dicts neben `TICK_SIZE`), `:364-397` (`org_gap`),
  `:400-418` (`ndog_gap`)
- Modify: `algo/live_status.py:203-204` (zwei Aufrufstellen, einzige Nicht-MNQ-taugliche
  Aufrufer außerhalb von Group-C-Modulen — `backtest_org_ce.py` und `backtest_fvg_strength.py`
  bleiben unverändert: sie sind laut Spec-Modul-Matrix Group C/futures-only und rufen `org_gap()`
  bereits jetzt nur mit hartkodiertem `MNQ` auf, ein Guard griffe dort nie — sie anzufassen wäre
  YAGNI)
- Test: neue `demo_session_guard()` in `tools/analyze_ohlc.py`, eingehängt in
  `algo/selfcheck.py`

**Interfaces:**
- Produces: `SESSION_TYP: dict[str, str]`, `PIP_SIZE: dict[str, float]` (Modulkonstanten),
  `org_gap(bars, day, tol_min=10, tick=None, symbol=None) -> dict | None`,
  `ndog_gap(bars, day, symbol=None) -> dict | None` — beide geben `None` zurück, wenn
  `SESSION_TYP.get(symbol) == "24x5"`, sonst unverändertes Verhalten. `nwog_gap()` bleibt
  unverändert (kein Guard, Spec §4.3).

- [ ] **Step 1: Dicts ergänzen**

In `tools/analyze_ohlc.py` direkt nach dem bestehenden `TICK_SIZE`-Dict (Zeile 65) einfügen:

```python
# Zwei Attribute statt einer Instrument-Klasse -- es gibt genau zwei Session-Typen (siehe
# docs/superpowers/specs/2026-08-14-forex-backtesting-design.md §3). "futures_rth": Handelstag
# 18:00 Vorabend..17:00 NY mit echtem Schluss/Eroeffnung. "24x5": Forex, 00:00..23:59 NY,
# durchgehend Mo 00:00 bis Fr 23:59 (mit Wochenend-Gap Fr 17:00 -> So 17:01) -- kein Schluss,
# also kein ORG/NDOG, siehe Guard in org_gap()/ndog_gap() unten.
SESSION_TYP = {
    "MNQ": "futures_rth", "NQ": "futures_rth", "ES": "futures_rth", "MES": "futures_rth",
    "YM": "futures_rth", "MYM": "futures_rth",
    "EURUSD": "24x5", "GBPUSD": "24x5", "AUDUSD": "24x5", "NZDUSD": "24x5",
    "USDCAD": "24x5", "USDCHF": "24x5", "EURGBP": "24x5",
    "USDJPY": "24x5", "EURJPY": "24x5", "GBPJPY": "24x5",
}

# Pip-Groesse fuer Forex-Vergleichbarkeit (0.0001 Majors, 0.01 JPY-Paare) -- ohne das ist eine
# FVG-Groesse von 0.00042 nicht gegen "MNQ 12 Punkte" lesbar.
PIP_SIZE = {
    "EURUSD": 0.0001, "GBPUSD": 0.0001, "AUDUSD": 0.0001, "NZDUSD": 0.0001,
    "USDCAD": 0.0001, "USDCHF": 0.0001, "EURGBP": 0.0001,
    "USDJPY": 0.01, "EURJPY": 0.01, "GBPJPY": 0.01,
}
```

- [ ] **Step 2: Guard-Test schreiben (vor der Implementierung, muss zuerst fehlschlagen)**

Direkt vor `if __name__ == "__main__":` (Ende der Datei) einfügen:

```python
def demo_session_guard() -> None:
    """org_gap()/ndog_gap() muessen fuer 24x5-Symbole None liefern, unabhaengig von den
    Kerzendaten -- und fuer futures_rth/unbekannte Symbole unveraendert rechnen."""
    tag = datetime(2026, 1, 5).date()
    bars = [
        Bar(at(tag - timedelta(days=1), 16, 14), 100, 100, 100, 100),
        Bar(at(tag, 9, 30), 105, 105, 105, 105),
    ]
    assert org_gap(bars, tag, symbol="EURUSD") is None, "24x5 muss org_gap None liefern"
    assert ndog_gap(bars, tag, symbol="EURUSD") is None, "24x5 muss ndog_gap None liefern"
    assert org_gap(bars, tag) is not None, "ohne symbol muss sich nichts aendern (Rueckwaertskompat.)"
    assert org_gap(bars, tag, symbol="MNQ") is not None, "futures_rth darf nicht geguardet werden"
    print("analyze_ohlc.demo_session_guard: OK")
```

- [ ] **Step 3: Test laufen lassen, muss fehlschlagen**

Ausführen: `python -c "from tools.analyze_ohlc import demo_session_guard; demo_session_guard()"`
Erwartet: `TypeError: org_gap() got an unexpected keyword argument 'symbol'`

- [ ] **Step 4: Guard in `org_gap()` und `ndog_gap()` einbauen**

In `org_gap()` (Zeile 364) die Signatur und den Funktionskopf ändern:

```python
def org_gap(bars: list[Bar], day, tol_min: int = 10, tick: float | str | None = None,
           symbol: str | None = None) -> dict | None:
    """... (bestehender Docstring unveraendert bis zum letzten Absatz, dann anhaengen:)

    `symbol`: gesetzt und SESSION_TYP[symbol] == "24x5" -> None. Ein 24/5-Markt hat weder
    Schluss noch Eroeffnung, ORG existiert dort strukturell nicht (Nutzerkorrektur 2026-08-14,
    siehe docs/superpowers/specs/2026-08-14-forex-backtesting-design.md §4).
    """
    if symbol is not None and SESSION_TYP.get(symbol) == "24x5":
        return None
    open_bar = next((b for b in bars if b.t == at(day, 9, 30)), None)
    # ... Rest der Funktion unveraendert
```

In `ndog_gap()` (Zeile 400) analog:

```python
def ndog_gap(bars: list[Bar], day, symbol: str | None = None) -> dict | None:
    """... (bestehender Docstring, letzter Absatz ergaenzt:)

    `symbol`: gesetzt und SESSION_TYP[symbol] == "24x5" -> None. Kein taeglicher Handelsschluss,
    also keine Handelspause, also kein NDOG (siehe org_gap()).
    """
    if symbol is not None and SESSION_TYP.get(symbol) == "24x5":
        return None
    day_bars = sorted((b for b in bars if b.t.date() == day), key=lambda b: b.t)
    # ... Rest der Funktion unveraendert
```

`nwog_gap()` bleibt **unverändert** — sie ruft `ndog_gap(bars, day)` ohne `symbol` auf und bleibt
damit für Forex aktiv (Spec §4.3: NWOG ist real, Fr 17:00 → So 17:01 NY).

- [ ] **Step 5: Test laufen lassen, muss jetzt passen**

Ausführen: `python -c "from tools.analyze_ohlc import demo_session_guard; demo_session_guard()"`
Erwartet: `analyze_ohlc.demo_session_guard: OK`

- [ ] **Step 6: In `selfcheck.py` einhängen**

In `algo/selfcheck.py` bei den bestehenden Imports (Zeile ~26, neben `demo_pruefe_kerzen`):

```python
from analyze_ohlc import demo_pruefe_kerzen, demo_session_guard  # noqa: E402
```

In der `CHECKS`-Liste (nach dem `ohlc_gate`-Eintrag) ergänzen:

```python
    ("session_guard", demo_session_guard),
```

- [ ] **Step 7: `live_status.py` auf die neue Signatur umstellen**

In `algo/live_status.py:203-204`:

```python
    org = org_gap(wide_bars, day, tick=SYMBOL_TICK, symbol=DISPLAY_SYMBOL)
    ndog = ndog_gap(wide_bars, day, symbol=DISPLAY_SYMBOL)
```

(`DISPLAY_SYMBOL = "MNQ"` aktuell einziger Wert — `SESSION_TYP["MNQ"] == "futures_rth"`, Verhalten
bleibt identisch. Die Änderung ist Vorbereitung für den Tag, an dem `live_status.py` auch für
Forex laufen soll, nicht Teil dieser Spec (Phase 2).)

- [ ] **Step 8: Volles `selfcheck.py` laufen lassen**

Ausführen: `python algo/selfcheck.py`
Erwartet: `Alle 21 Selbstchecks bestanden.` (bisher 20, plus `session_guard`), keine anderen
Zahlen verändert.

- [ ] **Step 9: Commit**

```bash
git add tools/analyze_ohlc.py algo/selfcheck.py algo/live_status.py
git commit -m "feat: SESSION_TYP/PIP_SIZE + Eroeffnungs-Guard fuer org_gap/ndog_gap"
```

---

## Task 4: `algo/marktdaten.py` — ein Loader für Futures und Forex

**Files:**
- Create: `algo/marktdaten.py`

**Interfaces:**
- Consumes: `tools.analyze_ohlc.{Bar, load, DATA_DIR, SESSION_TYP, NY}`,
  `algo.build_parquet.CACHE`
- Produces: `bars(symbol: str, tf: str, von: date | None = None, bis: date | None = None) -> list[Bar]`
  — für `SESSION_TYP[symbol] == "24x5"` aus dem Parquet-Cache resampled, sonst unverändert aus
  `raw/marktdaten/` (identisches Verhalten zu `backtest_common.find_days()` für Futures). Wird
  von Task 6 (`backtest_common.py`) und Task 7/8 (Modul-Läufe) konsumiert.

- [ ] **Step 1: Test schreiben (muss zuerst fehlschlagen, Modul existiert noch nicht)**

Am Ende von `algo/marktdaten.py` (wird in Step 2 angelegt) folgt der `_demo()`-Selbstcheck —
hier zunächst der Testfall, den er beweisen muss:

```python
def _demo() -> None:
    """Selbstcheck: winziger Parquet-Cache in ein Tempdir, prueft Resample-Anker (NY-
    Mitternacht) und von/bis-Filter. Futures-Pfad wird NICHT hier getestet (der laeuft
    unveraendert ueber tools.analyze_ohlc.load(), bereits durch selfcheck.py abgedeckt)."""
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
    print("marktdaten: Selbstcheck ok")
```

- [ ] **Step 2: Vollständiges Modul schreiben**

```python
#!/usr/bin/env python3
"""Ein Einstieg fuer alle Backtest-Module: `bars(symbol, tf, von, bis)` liefert die bestehende
`Bar`-Liste, egal ob das Symbol aus raw/marktdaten/ (Futures, CSV je Timeframe) oder aus dem
histdata-Parquet-Cache (Forex, resampled aus 1m) stammt. Kein Detektor merkt den Unterschied.

Aufruf:
    python algo/marktdaten.py --demo
"""
from __future__ import annotations

import sys
from datetime import date, datetime
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from analyze_ohlc import Bar, DATA_DIR, NY, SESSION_TYP, load  # noqa: E402
from build_parquet import CACHE  # noqa: E402

PANDAS_FREQ = {"1m": "1min", "5m": "5min", "15m": "15min", "1h": "1h", "4h": "4h", "1d": "1D"}


def bars(symbol: str, tf: str, von: date | None = None, bis: date | None = None) -> list[Bar]:
    if SESSION_TYP.get(symbol) == "24x5":
        return _forex_bars(symbol, tf, von, bis)
    return _futures_bars(symbol, tf, von, bis)


def _futures_bars(symbol: str, tf: str, von: date | None, bis: date | None) -> list[Bar]:
    """Unveraendertes Verhalten gegenueber backtest_common.find_days()/load() -- ein Bar
    je Tagesordner-Datei, im Bestand bereits im Ziel-Timeframe vorliegend."""
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
        dateien = sorted(f for f in day_dir.glob(f"{symbol} * {tf}.csv") if "RTH" not in f.name)
        if dateien:
            out.extend(load(dateien[0]))
    out.sort(key=lambda b: b.t)
    return out


def _forex_bars(symbol: str, tf: str, von: date | None, bis: date | None) -> list[Bar]:
    """Liest den 1m-Parquet-Cache, resampled bei Bedarf. Anker an NY-Mitternacht: der Index
    ist bereits NY-lokalisiert, `origin="start_day"` verankert Resample-Buckets deshalb an
    NY-00:00, nicht UTC-Mitternacht (Spec §5.3)."""
    df = pd.read_parquet(CACHE / f"{symbol}_1m.parquet")
    idx = pd.to_datetime(df["time"], unit="s", utc=True).dt.tz_convert(NY)
    df = df.set_index(idx).drop(columns="time").sort_index()

    if tf != "1m":
        df = df.resample(PANDAS_FREQ[tf], label="left", closed="left",
                         origin="start_day").agg(
            {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()

    if von:
        df = df[df.index.date >= von]
    if bis:
        df = df[df.index.date <= bis]

    return [Bar(t.to_pydatetime(), r.open, r.high, r.low, r.close) for t, r in df.iterrows()]


# _demo() aus Step 1 hier einfuegen


def main() -> int:
    if "--demo" in sys.argv:
        _demo()
        return 0
    print(__doc__)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 3: Selbstcheck laufen lassen**

Ausführen: `python algo/marktdaten.py --demo`
Erwartet: `marktdaten: Selbstcheck ok`

- [ ] **Step 4: Gegen den echten Cache aus Task 1 probelaufen**

```bash
python -c "
from algo.marktdaten import bars
b = bars('EURUSD', '1d', von=__import__('datetime').date(2026,1,1), bis=__import__('datetime').date(2026,1,10))
print(len(b), b[0].t, b[-1].t)
"
```
Erwartet: eine Handvoll Tagesbalken, `t` jeweils auf `00:00` NY (nicht `19:00`/`20:00` Vortag
wie beim yfinance-1d-Bestand — das ist die im Spec §1.2 gemessene Forex-eigene Konvention).

- [ ] **Step 5: Commit**

```bash
git add algo/marktdaten.py
git commit -m "feat: gemeinsamer Bar-Loader fuer Futures und Forex (marktdaten.py)"
```

---

## Task 5: Attrappen-Messung in `raw/marktdaten/` (nur Messen, kein Löschen)

**Files:**
- Create: `algo/measure_forex_attrappen.py`

**Interfaces:**
- Produces: `messen(symbol: str, tf: str) -> list[dict]` (ein Eintrag je Datei mit
  `flat_anteil`), `algo/results/forex_attrappen_report.json`. Kein anderer Task konsumiert
  diese Datei — sie ist ausschließlich die Löschvorschlags-Grundlage für Spec §8, die der
  Nutzer selbst freigibt.

- [ ] **Step 1: Modul mit Selbstcheck schreiben**

```python
#!/usr/bin/env python3
"""Misst den Attrappen-Anteil (o=h=l=c) je Forex-Datei in raw/marktdaten/ -- Grundlage fuer
den Loeschvorschlag aus Spec §8. LOESCHT NICHTS. Legt nur eine Liste vor; die eigentliche
Loeschung braucht ausdrueckliche Nutzerfreigabe (siehe algo/PLAN.md).

Aufruf:
    python algo/measure_forex_attrappen.py
    python algo/measure_forex_attrappen.py --demo
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from analyze_ohlc import SESSION_TYP  # noqa: E402
from backtest_common import DATA_DIR, write_result  # noqa: E402

FOREX_SYMBOLE = [s for s, t in SESSION_TYP.items() if t == "24x5"]
LOESCH_SCHWELLE = 0.90  # Spec §8.2: Vorschlag nur ueber 90% Flat-Anteil


def flat_anteil(pfad: Path) -> tuple[int, int]:
    """(flache Kerzen, Kerzen gesamt) einer CSV-Datei."""
    flach = gesamt = 0
    with pfad.open(newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            gesamt += 1
            if row["open"] == row["high"] == row["low"] == row["close"]:
                flach += 1
    return flach, gesamt


def messen(symbol: str, tf: str) -> list[dict]:
    out = []
    for pfad in sorted(DATA_DIR.glob(f"*/*/*/{symbol} *-*-* {tf}.csv")):
        if "RTH" in pfad.name:
            continue
        flach, gesamt = flat_anteil(pfad)
        if gesamt == 0:
            continue
        out.append({"pfad": str(pfad.relative_to(DATA_DIR.parent.parent)),
                    "symbol": symbol, "tf": tf, "kerzen": gesamt,
                    "flat_anteil": round(flach / gesamt, 4)})
    return out


def _demo() -> None:
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        ordner = Path(tmp) / "raw" / "marktdaten" / "2026" / "01" / "05.01.2026"
        ordner.mkdir(parents=True)
        pfad = ordner / "TEST 2026-01-05 1m.csv"
        pfad.write_text("time,open,high,low,close\n1,1,1,1,1\n2,1,2,1,2\n3,1,1,1,1\n",
                        encoding="utf-8")
        global DATA_DIR
        orig = DATA_DIR
        DATA_DIR = Path(tmp) / "raw" / "marktdaten"
        try:
            r = messen("TEST", "1m")
            assert len(r) == 1 and r[0]["flat_anteil"] == round(2 / 3, 4), r
        finally:
            DATA_DIR = orig
    print("measure_forex_attrappen: Selbstcheck ok")


def main() -> int:
    if "--demo" in sys.argv:
        _demo()
        return 0

    alle = []
    for sym in sorted(FOREX_SYMBOLE):
        for tf in ("1m", "5m", "15m"):  # 1d/1h/4h bleiben laut Spec §8.3 ausdruecklich erhalten
            alle.extend(messen(sym, tf))

    vorschlag = [r for r in alle if r["flat_anteil"] >= LOESCH_SCHWELLE]
    print(f"{len(alle)} Dateien geprueft, {len(vorschlag)} ueber {LOESCH_SCHWELLE:.0%} flach "
          f"(Loeschkandidaten, NICHT geloescht):")
    for r in vorschlag[:30]:
        print(f"  {r['flat_anteil']:.1%}  {r['pfad']}")
    if len(vorschlag) > 30:
        print(f"  ... und {len(vorschlag) - 30} weitere, siehe Report")

    write_result("forex_attrappen_report", {"alle": alle, "loeschvorschlag": vorschlag})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Selbstcheck laufen lassen**

Ausführen: `python algo/measure_forex_attrappen.py --demo`
Erwartet: `measure_forex_attrappen: Selbstcheck ok`

- [ ] **Step 3: Echte Messung laufen lassen**

Ausführen: `python algo/measure_forex_attrappen.py`
Erwartet: eine Liste von Dateipfaden mit Flat-Anteil ≥90 % (laut Spec §1.4 betrifft das nach
heutigem Stand die 1m/5m/15m-Dateien). **Diese Liste wird dem Nutzer vorgelegt — keine Datei
wird in diesem Task gelöscht** (Spec §8.4).

- [ ] **Step 4: Commit**

```bash
git add algo/measure_forex_attrappen.py
git commit -m "feat: Attrappen-Messung fuer raw/marktdaten/ (Loeschvorschlag, ohne Loeschung)"
```

---

## Task 6: `backtest_common.py` auf den neuen Loader umstellen

**Files:**
- Modify: `algo/backtest_common.py:51-66` (`load_rows()`)
- Test: `algo/backtest_common.py::demo()` erweitert

**Interfaces:**
- Consumes: `algo.marktdaten.bars()` aus Task 4.
- Produces: `load_rows(symbol: str = "MNQ") -> list[dict]` — identisches Rückgabeformat wie
  bisher, jetzt auch für Forex-Symbole nutzbar. `find_days()`/`find_1d_days()` bleiben
  **unverändert** (reiner Futures-Pfad, siehe Spec §7 — kein MNQ-Ergebnis darf sich
  verschieben, und diese beiden Funktionen werden von Group-C-Modulen weiterverwendet, die nie
  Forex sehen).

- [ ] **Step 1: MNQ-Baseline vor der Änderung festhalten**

Ausführen und Ausgabe notieren (Spec §7: "Kennzahlen vor der Umstellung festhalten, danach
diffen"):
```bash
python algo/selfcheck.py > /tmp/selfcheck_vor_task6.txt
python -c "from algo.backtest_common import load_rows; r = load_rows(); print(len(r), r[0], r[-1])" > /tmp/load_rows_vor_task6.txt
```

- [ ] **Step 2: Test für den Forex-Zweig schreiben**

In `algo/backtest_common.py::demo()` (Zeile 89) ergänzen, vor dem `tempfile`-Block:

```python
    # Forex-Zweig: load_rows() muss fuer ein 24x5-Symbol ueber marktdaten.bars() gehen,
    # nicht ueber find_1d_days() (das kennt raw/marktdaten-tief/ nicht).
    import marktdaten as md
    orig_bars = md.bars
    def fake_bars(symbol, tf, von=None, bis=None):
        assert tf == "1d", f"load_rows muss 1d anfragen, nicht {tf}"
        from analyze_ohlc import Bar
        from datetime import datetime
        from zoneinfo import ZoneInfo
        ny = ZoneInfo("America/New_York")
        return [Bar(datetime(2026, 1, 5, tzinfo=ny), 1.1, 1.12, 1.09, 1.11)]
    md.bars = fake_bars
    try:
        rows = load_rows("EURUSD")
        assert len(rows) == 1 and rows[0]["bullish"] is True, rows
    finally:
        md.bars = orig_bars
```

- [ ] **Step 3: Test laufen lassen, muss fehlschlagen**

Ausführen: `python algo/backtest_common.py`
Erwartet: `AssertionError` oder leere `rows` (aktuell ruft `load_rows()` unabhängig vom Symbol
`find_1d_days()` auf `raw/marktdaten/` auf, findet dort kein `EURUSD`-1d mit dieser Konvention
bzw. ignoriert den Forex-Pfad komplett).

- [ ] **Step 4: `load_rows()` erweitern**

```python
def load_rows(symbol: str = "MNQ") -> list[dict]:
    """Verschoben aus backtest_seasonal.py (2026-08-07). Fuer 24x5-Symbole (Forex) ueber
    algo.marktdaten.bars() (histdata-Cache), fuer alles andere unveraendert ueber
    find_1d_days() (raw/marktdaten/) -- siehe docs/superpowers/specs/
    2026-08-14-forex-backtesting-design.md §5.1."""
    from analyze_ohlc import SESSION_TYP  # lokal, um den Futures-Pfad ohne neue
                                          # Modulabhaengigkeit unveraendert zu lassen
    if SESSION_TYP.get(symbol) == "24x5":
        import marktdaten
        rows = []
        for b in marktdaten.bars(symbol, "1d"):
            if b.h <= b.l:
                continue
            rows.append({"day": b.t.date(), "open": b.o, "close": b.c, "high": b.h, "low": b.l,
                        "range": b.h - b.l, "ret_pct": 100 * (b.c - b.o) / b.o,
                        "bullish": b.c > b.o})
        rows.sort(key=lambda r: r["day"])
        return rows

    rows = []
    for day, path in find_1d_days(symbol):
        bars = load(path)
        if not bars:
            continue
        b = bars[-1]
        if b.h <= b.l:
            continue
        rows.append({"day": day, "open": b.o, "close": b.c, "high": b.h, "low": b.l,
                      "range": b.h - b.l, "ret_pct": 100 * (b.c - b.o) / b.o,
                      "bullish": b.c > b.o})
    rows.sort(key=lambda r: r["day"])
    return rows
```

- [ ] **Step 5: Test laufen lassen, muss jetzt passen**

Ausführen: `python algo/backtest_common.py`
Erwartet: `backtest_common.demo: OK`

- [ ] **Step 6: MNQ-Baseline diffen**

```bash
python algo/selfcheck.py > /tmp/selfcheck_nach_task6.txt
diff /tmp/selfcheck_vor_task6.txt /tmp/selfcheck_nach_task6.txt
python -c "from algo.backtest_common import load_rows; r = load_rows(); print(len(r), r[0], r[-1])" > /tmp/load_rows_nach_task6.txt
diff /tmp/load_rows_vor_task6.txt /tmp/load_rows_nach_task6.txt
```
Erwartet: **beide `diff`-Aufrufe liefern keine Ausgabe** (identisch). Jede Abweichung ist ein
Bug (Spec §7) und muss vor dem nächsten Task behoben werden.

- [ ] **Step 7: Commit**

```bash
git add algo/backtest_common.py
git commit -m "feat: load_rows() unterstuetzt Forex-Symbole ueber marktdaten.bars()"
```

---

## Task 7: Gruppe A auf Forex — `backtest_seasonal.py` als Nachweis

**Files:**
- Modify: `algo/backtest_seasonal.py` (`run()`/`main()` bekommen einen `symbol`-Parameter,
  `main()` zusätzlich einen symbolabhängigen Ausgabepfad; CLI nimmt `symbol` optional als
  Positionsargument)
- Test: bestehender Selbstcheck-Mechanismus (`selfcheck.py::_results_demo` — nutzt
  `backtest_seasonal.run()` direkt, unbetroffen) bleibt für MNQ unverändert; neuer manueller
  Lauf für alle 10 Forex-Paare als Nachweis, kein zusätzlicher `assert`-Test nötig (reiner
  Parameter-Durchreich, per Diff in Step 3 abgesichert)

**Interfaces:**
- Consumes: `backtest_common.load_rows(symbol)` aus Task 6.
- Produces: `algo/seasonal_tendency_<SYM>.json` je Forex-Paar (gleiches Schema wie das
  bestehende `algo/seasonal_tendency.json`, das für MNQ unter genau diesem Namen bestehen
  bleibt — siehe Step 1, wichtig: `run()` schreibt **nicht** über `backtest_common.write_result`,
  sondern direkt nach `OUT_PATH`, siehe `algo/backtest_seasonal.py:31,133-135`).

- [ ] **Step 1: MNQ-Baseline vor der Änderung festhalten**

```bash
python -c "from algo.backtest_seasonal import run; import json; print(json.dumps(run(), default=str, sort_keys=True))" > /tmp/seasonal_mnq_vor.json
```

- [ ] **Step 2: `run()`/`main()` parametrisieren, ohne den bestehenden MNQ-Dateinamen zu kapern**

`algo/backtest_seasonal.py:94` (`run()`) und `:103` (`main()`) ändern. **Wichtig:** `OUT_PATH`
ist aktuell eine feste Modulkonstante (`algo/seasonal_tendency.json`, Zeile 31) — die ist laut
`CLAUDE.md` ("Protokoll- und Datenartefakte") das kanonische MNQ-Artefakt für
Jahr-über-Jahr-Vergleiche. Ein Forex-Lauf darf diese Datei nicht überschreiben, deshalb bekommt
`main()` einen eigenen Ausgabepfad je Symbol statt der bisherigen Konstante:

```python
def run(symbol: str = "MNQ") -> dict:
    rows = load_rows(symbol)
    return {
        "symbol": symbol, "n_days": len(rows), "date_range": [rows[0]["day"], rows[-1]["day"]],
        "weekday": weekday_table(rows), "month": month_table(rows),
        "turn_of_month": turn_of_month(rows), "week_of_month": week_of_month_table(rows),
    }


def out_path(symbol: str) -> Path:
    """MNQ behaelt den bestehenden Namen (Protokollartefakt, siehe CLAUDE.md) -- jedes
    andere Symbol bekommt einen eigenen, damit ein Forex-Lauf die MNQ-Datenbank nicht
    ueberschreibt."""
    if symbol == "MNQ":
        return OUT_PATH
    return OUT_PATH.parent / f"seasonal_tendency_{symbol}.json"


def main(symbol: str = "MNQ") -> None:
    result = run(symbol)
    # ... alle bisherigen print()-Zeilen unveraendert (result["date_range"] etc. bleiben
    #     gleich benannt, nur "symbol" ist zusaetzlich im dict) ...
    db = {"generated_at": datetime.now(timezone.utc).isoformat(), **result}
    ziel = out_path(symbol)
    ziel.write_text(json.dumps(db, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"\nDatenbank geschrieben: {ziel.relative_to(ziel.parent.parent)}")
```

Am Dateiende:
```python
if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "MNQ")
```
(Braucht `import sys` — bereits vorhanden, Zeile 21.)

- [ ] **Step 3: MNQ-Baseline diffen**

```bash
python -c "from algo.backtest_seasonal import run; import json; print(json.dumps(run(), default=str, sort_keys=True))" > /tmp/seasonal_mnq_nach.json
diff /tmp/seasonal_mnq_vor.json /tmp/seasonal_mnq_nach.json
```
Erwartet: **die einzige Abweichung ist das neu hinzugekommene Feld `"symbol": "MNQ"`** — alle
Zahlen (`n_days`, `weekday`, `month`, `turn_of_month`, `week_of_month`) müssen identisch sein.
Jede andere Abweichung ist ein Bug (Spec §7) und wird vor Step 4 behoben.

- [ ] **Step 4: Für alle 10 Forex-Paare laufen lassen**

```bash
python -c "
from algo.backtest_seasonal import main
for sym in ('EURUSD','GBPUSD','USDJPY','USDCHF','AUDUSD','USDCAD','NZDUSD','EURJPY','EURGBP','GBPJPY'):
    main(sym)
"
```
Erwartet: für jedes Symbol eine Ausgabe endend mit `Datenbank geschrieben:
algo/seasonal_tendency_<SYM>.json`, ohne Exception. `n_days` im Bereich mehrerer tausend (23
Jahre Historie statt der bisherigen ~150 MNQ-Tage) — anders als beim aktuellen MNQ-Datenstand
wird der Monatsvergleich (`month_table`) hier zu einem **echten** Mehrjahres-Seasonality-Test
(siehe Docstring-Hinweis in `algo/backtest_seasonal.py:8-12`, der für MNQ noch explizit
einschränkt "kein echter Mehrjahres-Seasonality-Test").

- [ ] **Step 5: Commit**

```bash
git add algo/backtest_seasonal.py
git commit -m "feat: backtest_seasonal.py laeuft ueber --symbol auch auf Forex"
```

---

## Task 8: Gruppe B auf Forex — `backtest_midnight_range_std.py` als Nachweis

**Files:**
- Modify: `algo/backtest_midnight_range_std.py` (Datenzugriff von `backtest_org_ce.find_days()`
  auf `marktdaten.bars()` umgestellt, `run()` bekommt `symbol`-Parameter)

**Interfaces:**
- Consumes: `algo.marktdaten.bars(symbol, "1m", von, bis)` aus Task 4.
- Produces: `algo/results/midnight_range_std_<SYM>.json` je Paar.

- [ ] **Step 1: Aktuellen Datenzugriff lokalisieren und Baseline festhalten**

```bash
python -c "from algo.backtest_midnight_range_std import run; import json; print(json.dumps(run(), default=str, sort_keys=True))" > /tmp/mrs_mnq_vor.json
```

- [ ] **Step 2: Datenquelle umstellen**

In `algo/backtest_midnight_range_std.py` den Import
```python
from backtest_org_ce import find_days  # noqa: E402
```
ersetzen durch
```python
from backtest_org_ce import find_days  # noqa: E402
from analyze_ohlc import SESSION_TYP  # noqa: E402
```
(bleibt zusätzlich bestehen — `find_days()` wird weiter für den Futures-Zweig gebraucht,
`find_days(symbol)` akzeptiert bereits einen Symbolparameter, siehe `backtest_org_ce.py:32`).

`run()` (Zeile 130) auf einen Symbolparameter und eine Verzweigung umstellen. Der Futures-Pfad
bleibt dabei Zeile für Zeile identisch (nur die Quelle von `(day, bars)`-Paaren ändert sich von
"pro Tag `load(path)` aufrufen" zu "vorher schon fertig gruppiert"), damit Step 3 exakt
dieselben Zahlen liefert:

```python
def run(symbol: str = "MNQ") -> dict:
    if SESSION_TYP.get(symbol) == "24x5":
        import marktdaten
        alle_bars = marktdaten.bars(symbol, "1m")
        nach_tag: dict = {}
        for b in alle_bars:
            nach_tag.setdefault(b.t.date(), []).append(b)
        tage = sorted(nach_tag.items())
    else:
        tage = [(day, load(path)) for day, path in find_days(symbol)]

    london_high, london_low, day_high, day_low = [], [], [], []
    days_used = 0
    days_incomplete = []
    for day, bars in tage:
        if window_gaps(bars, day, (0, 0), (0, 30)):
            days_incomplete.append(str(day))
        mr = midnight_range(bars, day)
        if mr is None:
            continue
        rh, rl, rng = mr
        lh, ll = k_extension(bars, day, at(day, 1, 0), at(day, 5, 0), rh, rl, rng)
        dh, dl = k_extension(bars, day, at(day, 0, 30), at(day, 17, 0), rh, rl, rng)
        if lh is None or dh is None:
            continue
        days_used += 1
        london_high.append(lh)
        london_low.append(ll)
        day_high.append(dh)
        day_low.append(dl)

    exceed_1std = (sum(1 for k in london_low if k > 1.0) / len(london_low)) if london_low else None

    return {"days_used": days_used, "london_high": london_high, "london_low": london_low,
            "day_high": day_high, "day_low": day_low,
            "days_incomplete": days_incomplete,
            "exceed_1std_pct": 100 * exceed_1std if exceed_1std is not None else None}
```

(Ersetzt den bisherigen Funktionskörper vollständig — die einzige inhaltliche Änderung
gegenüber dem Original ist die neue `if SESSION_TYP.get(symbol) == "24x5":`-Verzweigung am
Anfang; alles ab `london_high, london_low, ... = [], [], [], []` ist zeichengleich zum
bisherigen Code, nur dass die Schleife über `tage` statt über `find_days()` läuft.)

`main()` (Zeile 160) unverändert lassen — sie ruft weiterhin `run()` ohne Argument auf (Default
`"MNQ"`), CLI-Erweiterung um `--symbol` ist für diesen Nachweis-Task nicht nötig (der Forex-Lauf
erfolgt in Step 5 direkt über `run(symbol)`).

- [ ] **Step 3: MNQ-Baseline diffen**

```bash
python -c "from algo.backtest_midnight_range_std import run; import json; print(json.dumps(run(), default=str, sort_keys=True))" > /tmp/mrs_mnq_nach.json
diff /tmp/mrs_mnq_vor.json /tmp/mrs_mnq_nach.json
```
Erwartet: keine Ausgabe (identisch).

- [ ] **Step 4: `selfcheck.py`-Aufrufstelle anpassen**

`algo/selfcheck.py` ruft `backtest_midnight_range_std.run` bereits ohne Argument auf (Default
`"MNQ"` bleibt bestehen) — keine Änderung in `selfcheck.py` nötig, nur bestätigen:
```bash
python algo/selfcheck.py
```
Erwartet: weiterhin `Alle 21 Selbstchecks bestanden.`

- [ ] **Step 5: Für alle 10 Forex-Paare laufen lassen**

```bash
python -c "
from algo.backtest_midnight_range_std import run
for sym in ('EURUSD','GBPUSD','USDJPY','USDCHF','AUDUSD','USDCAD','NZDUSD','EURJPY','EURGBP','GBPJPY'):
    r = run(sym)
    print(sym, 'ok')
"
```
Erwartet: kein Fehler für alle 10 Paare — inklusive korrekter 00:00-23:59-NY-Tagesgrenze
(anders als bei MNQ, wo der Handelstag 18:00 beginnt; da `marktdaten.bars()` die Tagesgrenze
bereits pro Symbol richtig auflöst, braucht dieses Modul dafür keine eigene Fallunterscheidung).

- [ ] **Step 6: Commit**

```bash
git add algo/backtest_midnight_range_std.py
git commit -m "feat: backtest_midnight_range_std.py laeuft ueber marktdaten.bars() auch auf Forex"
```

---

## Task 9: Dokumentation nachziehen

**Files:**
- Modify: `algo/PLAN.md` (Log-Eintrag + Backlog-Punkt)
- Modify: `algo/README.md` (neue Abschnitte für `build_parquet.py`, `verify_forex_data.py`,
  `marktdaten.py`, `measure_forex_attrappen.py`)
- Modify: `wiki/log.md`
- Create: `wiki/concepts/Eröffnungsauktion vs. 24x5-Markt.md`

- [ ] **Step 1: `algo/PLAN.md` Log-Eintrag anhängen**

Neue Zeile in der Log-Tabelle (Datum des Implementierungstags), die zusammenfasst: Parquet-Cache
gebaut (Größe in MB), Verifikationsergebnis (Zeit/Vollständigkeit/Attrappen je Symbol),
Guard-Implementierung, `backtest_seasonal.py`/`backtest_midnight_range_std.py` als Gruppe-A/B-
Nachweis mit realen Kennzahlen aus den Läufen in Task 7/8, Attrappen-Löschvorschlag-Anzahl (aus
Task 5, noch nicht umgesetzt), und **explizit als Backlog vermerkt**: die übrigen Gruppe-A-Module
(`daily_patterns`, `tgif`, `nfp_week`, `ohlc`) und Gruppe-B-Module (`hp_fvg`,
`midnight_range_judas`, `fvg_strength`, `nwog`) folgen demselben in Task 6-8 bewiesenen Muster
(`symbol`-Parameter + `marktdaten.bars()`), sind aber nicht Teil dieses Plans — je eigener,
kleiner Umbau nach diesem Vorbild.

- [ ] **Step 2: `algo/README.md` ergänzen**

Je ein Abschnitt (Was/Wie/Warum/bekannte Grenzen, bestehendes Format) für die vier neuen Module
aus Task 1, 2, 4, 5 — mit den realen Zahlen aus den jeweiligen Testläufen (Cache-Größe,
Verifikationsstatus je Symbol, Anzahl Löschkandidaten).

- [ ] **Step 3: `wiki/log.md` Eintrag**

Typ `setup`, ein bis zwei Sätze: Forex-Backtesting-Infrastruktur nach Spec vom 14.08. umgesetzt,
Verweis auf `algo/PLAN.md` für Details.

- [ ] **Step 4: Neue Konzeptseite**

```markdown
---
tags: [concept, ict, forex, futures]
created: 2026-08-15
updated: 2026-08-15
sources: []
---

# Eröffnungsauktion vs. 24x5-Markt

Futures (MNQ, ES, ...) haben einen täglichen Handelsschluss und eine Wiedereröffnung (bei MNQ:
17:00 NY Schluss, 18:00 NY Globex-Reopen). Genau dieser Schluss-/Eröffnungswechsel erzeugt die
Konzepte, die auf ihm aufbauen:

- [[Opening Range Gap (ORG) & 1st Presented FVG]] — Gap zwischen Vortagesschluss (~16:14) und
  9:30-Eröffnung.
- [[New Day Opening Gap (NDOG)]] — Gap zwischen letztem Kerzen-Close und erster Kerze des Tages.
- Das "erste FVG nach 9:30" und der Open Drive setzen ebenfalls eine Eröffnungsauktion voraus.

Forex-Paare (EURUSD, GBPUSD, ...) handeln 24x5 durchgehend (So 17:01 NY bis Fr 17:00 NY) — es
gibt keinen täglichen Schluss, also strukturell **kein** ORG, **kein** NDOG und **kein** "erstes
FVG nach 9:30" im ICT-Sinn. Was in Forex weiterhin existiert: das **[[New Week Opening Gap (NWOG)
Bias|NWOG]]** — der reale Wochenend-Gap zwischen Freitagsschluss und Sonntagsöffnung.

**Implementierung:** `tools/analyze_ohlc.py::SESSION_TYP` markiert jedes Symbol als
`futures_rth` oder `24x5`; `org_gap()`/`ndog_gap()` liefern für `24x5`-Symbole `None`, statt
eine plausibel aussehende, aber bedeutungslose Zahl zu berechnen (siehe
`docs/superpowers/specs/2026-08-14-forex-backtesting-design.md` §4).

Nutzerkorrektur, die diese Unterscheidung ausgelöst hat (2026-08-14): *"in forex gibt es kein
opening range gap ... ndog gibt es nicht aber nwog gibt es."*
```

In `wiki/index.md` unter `## Concepts` eintragen, in `wiki/concepts/ORG (Opening Range Gap) &
1st Presented FVG.md` und `wiki/concepts/New Day Opening Gap (NDOG).md` einen Rückverweis
ergänzen (`> Siehe auch [[Eröffnungsauktion vs. 24x5-Markt]] für die Forex-Abgrenzung.`).

- [ ] **Step 5: Commit**

```bash
git add algo/PLAN.md algo/README.md wiki/log.md wiki/index.md \
       "wiki/concepts/Eröffnungsauktion vs. 24x5-Markt.md" \
       "wiki/concepts/ORG (Opening Range Gap) & 1st Presented FVG.md" \
       "wiki/concepts/New Day Opening Gap (NDOG).md"
git commit -m "docs: Forex-Backtesting-Infrastruktur dokumentiert"
```

**Hinweis:** `.\push.ps1` wird laut CLAUDE.md nur manuell vom Nutzer ausgelöst — dieser Task
endet beim lokalen Commit, kein automatischer Push.

---

## Was dieser Plan bewusst NICHT umsetzt

Direkt aus Spec §2 und §6/§10 übernommen, damit kein Executor versehentlich darüber hinausbaut:

- Keine der Gruppe-C-Module (`org_ce`, `1p_mindestgroesse`, `1p_fvg_woche`, `ndog`, ...) werden
  für Forex freigeschaltet — sie bleiben MNQ-only, der Guard aus Task 3 sorgt genau dafür, falls
  sie versehentlich mit einem Forex-Symbol aufgerufen würden.
- Kein `$`-P&L, kein Pip-Wert in `pnl.py`, keine Forex-Regel in `rules.py`, keine
  IBKR-Forex-Anbindung (Phase 2, außerhalb dieser Spec).
- Löschung der Attrappen-Dateien aus `raw/marktdaten/` (Task 5 liefert nur die Liste) — braucht
  ausdrückliche Freigabe des Nutzers, kein Teil der automatisierten Ausführung dieses Plans.
- Die übrigen 8 Gruppe-A/B-Module folgen dem in Task 6-8 bewiesenen Muster als eigener,
  kleiner Folge-Task — nicht in diesem Plan enthalten, um ihn reviewbar zu halten.
- `PIP_SIZE` (Task 3) wird angelegt, aber von keinem der beiden Nachweis-Module (Task 7/8)
  konsumiert — `backtest_seasonal.py` und `backtest_midnight_range_std.py` arbeiten beide mit
  selbstnormierten Größen (Prozent-Rendite bzw. STD-Vielfache der eigenen Opening Range) und
  brauchen keine Pip-Umrechnung. `PIP_SIZE` wird erst relevant, sobald ein Modul absolute
  Preis-/FVG-Größen MNQ-Punkten gegenüberstellt (z.B. `fvg_strength`, `hp_fvg` — Teil der oben
  genannten Folge-Tasks).
