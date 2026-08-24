#!/usr/bin/env python3
"""Sind die ICT-Macro-Fenster (XX:50-XX+1:10) auf FOREX die Expansions-Fenster?

Forex-Zwilling von `algo/backtest_macro.py` (Nutzerwunsch 2026-08-15: "nur die Forex-Daten
zum Backtesten der Macros"). Gleicher Aufbau, gleiche Kennzahlen, gleicher faire Vergleich:
jede Stunde zerfaellt in genau drei 20-Minuten-Bloecke

    :50-:10  (Macro)      :10-:30  (Kontrolle)     :30-:50  (Kontrolle)

Die Kontrollen liegen direkt daneben statt irgendwo im Tag -- ohne das gewaenne 09:50-10:10
schon deshalb, weil um diese Zeit ohnehin die meiste Bewegung liegt (Tageszeit-Confounder).

DREI UNTERSCHIEDE ZUR MNQ-FASSUNG
---------------------------------
1. **72 Bloecke statt 69.** Ein 24/5-Markt hat keine Globex-Pause, also auch kein Loch bei
   17:50: 24 Stunden x 3 Bloecke = 72, davon **24 Macros statt 23**. Der Tag ist der
   NY-Kalendertag (00:00-24:00), nicht der Futures-Handelstag ab 18:00 des Vorabends.
2. **Groessen in Pips.** `range`/`netto` in Rohpreis sind zwischen EURUSD (0,0001) und GBPJPY
   (0,01) nicht vergleichbar. Zusaetzlich `netto_rel` = Netto / Median-Kerzenrange des Tages,
   damit ueber Symbole UND ueber 23 Jahre gepoolt werden kann (2003 war eine EURUSD-Minute
   deutlich groesser als 2019, siehe die zwei Liquiditaetsregime in der Phase-2-Spec §1.1).
3. **Spooling-Flag**, das es auf der MNQ-Seite nicht gibt -- siehe unten.

SPOOLING: DIE DEFINITION KOMMT AUS DEM VAULT, NICHT AUS DER INTUITION
---------------------------------------------------------------------
`wiki/concepts/ICT Macros & Leading Candles.md`, Abschnitt "Spooling -- ICTs Definition (2024)":
die naheliegende Lesart (Kompression/Kraftaufbau VOR dem Move) ist dort ausdruecklich als
falsch herum aufgeloest. ICT meint die **Bewegung selbst**:

    "The market will spool -- it means it jumps and runs to one of two things."
    "All a macro is, is the beginning of a spooling event. ... It is not going to give you
     a direction."

Spooling ist der gerichtete Lauf zum Ziel (Short-Term Low = Sellside, Short-Term High =
Buyside, oder eine Ineffizienz), nicht die Ruhe davor. Die Konzeptseite benennt auch gleich
das Mass: *"die gemessene erhoehte Geradlinigkeit (`dir`) im Macro ist genau das Spooling"*.
Die vier `pre_*`-Spalten in `algo/macro_db.py` heissen deshalb seit dem 2026-08-10
**Vorlauf-Kandidaten**, nicht Spooling-Kandidaten.

Daraus folgen zwei Bedingungen, beide noetig:

    dir >= SPOOL_DIR          Geradlinigkeit -- der Weg wurde gerichtet zurueckgelegt
    netto_rel >= SPOOL_NETTO  ueberhaupt Weg -- ICT: "if the market simply doesn't budge",
                              dann ist das ausdruecklich KEIN Spooling, sondern das Signal,
                              die Charts zuzumachen.

Ohne die zweite Bedingung waere ein regungsloser Block mit 0,2 Pips Range und dir = 1,0 ein
"Spooling" -- die haeufigste stille Fehlmessung bei einem Geradlinigkeits-Mass.

Aufruf:
    python algo/forex/backtest_macro.py --selfcheck
    python algo/forex/backtest_macro.py --symbols EURUSD
    python algo/forex/backtest_macro.py --all --von 2012-01-01
"""
from __future__ import annotations

import argparse
import bisect
import calendar
import csv
import statistics
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

_HIER = Path(__file__).resolve().parent
_ALGO = _HIER.parent

# Siehe algo/forex/rules.py: eigener Ordner runter von sys.path, sonst verdeckt
# algo/forex/pnl.py das gleichnamige algo/pnl.py.
for _p in (str(_HIER), ""):
    while _p in sys.path:
        sys.path.remove(_p)
sys.path.insert(0, str(_ALGO))
sys.path.insert(0, str(_ALGO.parent / "tools"))

from scipy.stats import mannwhitneyu  # noqa: E402
from analyze_ohlc import Bar, NY, PIP_SIZE, SESSION_TYP, at, fvgs  # noqa: E402
from backtest_common import RESULTS_DIR, write_result  # noqa: E402

BLOCK_MIN = 20
MIN_BARS = 15          # von 20 Minuten -- weniger heisst Datenluecke, nicht ruhiger Markt

# Mindestgroesse eines FVG, RELATIV zur lokalen Kerzenrange. Identisch zur MNQ-Fassung und aus
# demselben Grund: eine absolute Schwelle waere hier ein Messfehler, weil genau Bloecke
# unterschiedlicher Tageszeit gegeneinander getestet werden.
MIN_FVG_REL = 0.45

# Spooling-Schwellen (siehe Modulkopf).
SPOOL_DIR = 0.5        # mehr als die Haelfte der Blockrange als Nettoweg
SPOOL_NETTO = 1.0      # mindestens eine Median-Kerzenrange des Tages an Weg

FOREX_SYMBOLE = tuple(s for s, t in SESSION_TYP.items() if t == "24x5")
BLOCK_CSV = RESULTS_DIR / "forex_macro_blocks.csv"

# Jahre je Ladeschritt. Kompromiss aus zwei gegenlaeufigen Kosten: kleinere Chunks halten den
# Speicher niedrig, aber `marktdaten.bars()` liest je Aufruf die GANZE Parquet-Datei und
# filtert erst danach -- jahrweise waeren das 23 Vollreads je Symbol.
CHUNK_JAHRE = 5

CSV_FELDER = ["symbol", "day", "label", "macro", "range_pips", "netto_pips", "dir",
              "netto_rel", "fvgs", "rank", "n_blocks", "spooling"]


def _nter_sonntag(jahr: int, monat: int, n: int) -> date:
    """n-ter Sonntag des Monats (n=-1 -> letzter).

    Der letzte Sonntag wird vom LETZTEN Tag des Monats zurueckgerechnet, nicht vom 28. Eine
    frueher hier stehende Fassung startete bei Tag 28 und verlor damit die Tage 29-31: fuer
    Maerz 2019 lieferte sie den 24. statt des 31., also ein um eine Woche zu breites
    DST-Fenster. Aufgefallen ist das nur, weil der Selbstcheck gegen die tatsaechlichen
    Umstellungstermine prueft und nicht gegen die eigene Rechenlogik."""
    if n > 0:
        d = date(jahr, monat, 1)
        d += timedelta(days=(6 - d.weekday()) % 7)      # erster Sonntag
        return d + timedelta(weeks=n - 1)
    letzter = date(jahr, monat, calendar.monthrange(jahr, monat)[1])
    return letzter - timedelta(days=(letzter.weekday() + 1) % 7)


def dst_verdaechtig(tag: date) -> bool:
    """Liegt `tag` in einem Fenster, in dem US- und EU-Sommerzeit auseinanderlaufen?

    Hintergrund: der histdata-Endpoint stempelt seine Zeitstempel **ab 2019** an den EU-,
    nicht an den US-Umstellungsterminen -- in den Wochen dazwischen liegt der Bestand eine
    Stunde zu frueh (Befund 2026-08-15, siehe wiki/synthesis/Forex-Algo — ICT-Konzepte auf
    23 Jahren (laufend).md und algo/repair_dst_2019.py). Betroffen sind 2,40 % aller Kerzen.

    US: 2. Sonntag Maerz bis 1. Sonntag November. EU: letzter Sonntag Maerz bis letzter
    Sonntag Oktober. Auseinander laufen sie also im Fruehjahr zwischen US-Start und EU-Start
    und im Herbst zwischen EU-Ende und US-Ende.

    Vor 2019 folgte der Endpoint der US-Regel und war korrekt -- deshalb der Jahresschnitt.
    Ein zeitbasierter Backtest kann diese Tage bis zur Reparatur ausschliessen, statt auf
    `raw/` zuzugreifen (Layer 1 ist unveraenderlich, die Reparatur ist ein eigener,
    freizugebender Schritt).
    """
    if tag.year < 2019:
        return False
    j = tag.year
    return (_nter_sonntag(j, 3, 2) <= tag < _nter_sonntag(j, 3, -1)
            or _nter_sonntag(j, 10, -1) <= tag < _nter_sonntag(j, 11, 1))


def blocks(tag: date) -> list[tuple[str, datetime, datetime, bool]]:
    """Die 72 lueckenlosen 20-Minuten-Bloecke eines Forex-Kalendertags.

    Startpunkt 00:10, damit :50-:10 als GANZER Block auftaucht statt an der Tagesgrenze
    zerschnitten zu werden -- dieselbe Ueberlegung wie in algo/backtest_macro.py, dort mit
    18:10 als Start. Der letzte Block (23:50-00:10) reicht in den Folgetag; die 10 Minuten
    00:00-00:10 eines Tages werden also vom Vortag abgedeckt, nicht doppelt gezaehlt.
    """
    out = []
    t = at(tag, 0, 10)
    for _ in range(72):
        ende = t + timedelta(minutes=BLOCK_MIN)
        out.append((f"{t:%H:%M}-{ende:%H:%M}", t, ende, t.minute == 50))
        t = ende
    return out


def measure(win: list[Bar], pip: float, med_bar: float | None,
            tages_fvgs: list[dict] | None, start: datetime, ende: datetime) -> dict | None:
    """Kennzahlen eines Blocks, oder None bei Datenluecke.

    `win` sind die Kerzen des Blocks (bereits geschnitten), `med_bar` die Median-Kerzenrange
    des Tages in Rohpreis. Die FVGs kommen aus dem GANZEN Tag und werden hier nur
    zugeschnitten -- wie in der MNQ-Fassung, sonst haetten die ersten Kerzen jedes Blocks zu
    wenig Vorlauf fuer `size_rel` und die halbe Messung fiele weg.
    """
    if len(win) < MIN_BARS:
        return None
    hi, lo = max(b.h for b in win), min(b.l for b in win)
    rng = hi - lo
    net = abs(win[-1].c - win[0].o)
    d = net / rng if rng else 0.0
    netto_rel = (net / med_bar) if med_bar else None

    n_fvg = 0
    if tages_fvgs is not None:
        n_fvg = sum(1 for f in tages_fvgs
                    if start <= f["t_start"] and f["t_end"] < ende
                    and f["size_rel"] is not None and f["size_rel"] >= MIN_FVG_REL)

    return {"range_pips": rng / pip, "netto_pips": net / pip, "dir": d,
            "netto_rel": netto_rel, "fvgs": n_fvg,
            "spooling": ist_spooling(d, netto_rel)}


def ist_spooling(d: float, netto_rel: float | None) -> bool:
    """Spooling nach der Vault-Definition: der gerichtete Lauf selbst (siehe Modulkopf).

    Beide Bedingungen noetig. `netto_rel is None` (kein Median verfuegbar) gilt als NICHT
    spooling -- ein unbekannter Massstab darf kein Ja erzeugen.
    """
    if netto_rel is None:
        return False
    return d >= SPOOL_DIR and netto_rel >= SPOOL_NETTO


def _schneide(bars: list[Bar], zeiten: list[datetime],
              start: datetime, ende: datetime) -> list[Bar]:
    """Blockkerzen per Bisektion statt Listen-Comprehension.

    Der Unterschied ist nicht kosmetisch: bei 10 Paaren x 23 Jahren sind das ~430.000 Bloecke
    gegen ~8,5 Mio. Kerzen je Symbol. Ein `[b for b in bars if start <= b.t < ende]` je Block
    waere O(n) pro Block und liefe Tage.
    """
    i = bisect.bisect_left(zeiten, start)
    j = bisect.bisect_left(zeiten, ende)
    return bars[i:j]


def _collect_spanne(symbol: str, von: date, bis: date, mit_fvgs: bool) -> list[dict]:
    """Blockzeilen fuer die Tage [von..bis]. Laedt einen Tag Vorlauf ueber `bis` hinaus,
    weil der letzte Block eines Tages (23:50-00:10) in den Folgetag reicht -- ohne diesen
    Vorlauf faellt an jeder Chunk-Grenze ein Macro-Fenster still unter MIN_BARS."""
    import marktdaten as md
    bars = md.bars(symbol, "1m", von, bis + timedelta(days=1))
    if not bars:
        return []
    zeiten = [b.t for b in bars]
    pip = PIP_SIZE[symbol]

    nach_tag: dict[date, list[Bar]] = defaultdict(list)
    for b in bars:
        nach_tag[b.t.date()].append(b)

    zeilen: list[dict] = []
    for tag in sorted(nach_tag):
        if tag < von or tag > bis:
            continue                       # Vorlauftag liefert nur den Rand, keine Zeilen
        tagesbars = nach_tag[tag]
        if len(tagesbars) < 2:
            continue
        med_bar = statistics.median(b.rng for b in tagesbars) or None
        tages_fvgs = fvgs(tagesbars, tick=symbol) if mit_fvgs else None

        heute = []
        for label, start, ende, ist_macro in blocks(tag):
            win = _schneide(bars, zeiten, start, ende)
            m = measure(win, pip, med_bar, tages_fvgs, start, ende)
            if m:
                heute.append({"symbol": symbol, "day": tag, "label": label,
                              "macro": ist_macro, **m})
        # Tagesrang nach Range -- 1 = groesster Block des Tages.
        for rang, m in enumerate(sorted(heute, key=lambda x: -x["range_pips"]), start=1):
            m["rank"] = rang
            m["n_blocks"] = len(heute)
        zeilen.extend(heute)
    return zeilen


def collect(symbol: str, von: date | None = None, bis: date | None = None,
            mit_fvgs: bool = True) -> list[dict]:
    """Eine Zeile je auswertbarem Block, jahrweise geladen.

    Warum in Jahres-Chunks statt am Stueck: 23 Jahre 1m sind ~8,5 Mio. Bar-Objekte je Symbol.
    Zusammen mit den ~1,7 Mio. Ergebniszeilen desselben Symbols laeuft ein Volllauf sonst in
    den Arbeitsspeicher. Chunken haelt den Spitzenbedarf bei einem Jahr, und der Ein-Tages-
    Vorlauf in `_collect_spanne` sorgt dafuer, dass an den Chunk-Grenzen kein Block verloren
    geht -- das Ergebnis ist identisch zum Lauf am Stueck.
    """
    import marktdaten as md
    if von is None or bis is None:
        alle_tage = {b.t.date() for b in md.bars(symbol, "1d")}
        if not alle_tage:
            return []
        von = von or min(alle_tage)
        bis = bis or max(alle_tage)

    zeilen: list[dict] = []
    for start_jahr in range(von.year, bis.year + 1, CHUNK_JAHRE):
        j_von = max(von, date(start_jahr, 1, 1))
        j_bis = min(bis, date(start_jahr + CHUNK_JAHRE - 1, 12, 31))
        zeilen.extend(_collect_spanne(symbol, j_von, j_bis, mit_fvgs))
    return zeilen


def med(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else None


def _quote(ms: list[dict], feld: str) -> float:
    return 100.0 * sum(1 for m in ms if m[feld]) / len(ms) if ms else 0.0


def report(zeilen: list[dict], titel: str) -> dict:
    macro = [m for m in zeilen if m["macro"]]
    ctrl = [m for m in zeilen if not m["macro"]]
    if not macro or not ctrl:
        print(f"{titel}: zu wenig Daten ({len(macro)} Macro / {len(ctrl)} Kontrolle)")
        return {}

    tage = sorted({m["day"] for m in zeilen})
    print(f"\n=== {titel} ===")
    print(f"{len(tage)} Handelstage ({tage[0]} .. {tage[-1]}), "
          f"{len(zeilen):,} auswertbare 20min-Bloecke")
    print(f"  {'':<12} {'n':>7} {'medRange':>10} {'medNetto':>10} {'dir':>6} "
          f"{'nettoRel':>9} {'Spooling':>9}")
    for name, ms in (("Macro :50-:10", macro), ("Kontrolle", ctrl)):
        print(f"  {name:<12} {len(ms):>7,} {med([m['range_pips'] for m in ms]):>10.2f} "
              f"{med([m['netto_pips'] for m in ms]):>10.2f} {med([m['dir'] for m in ms]):>6.2f} "
              f"{med([m['netto_rel'] for m in ms]) or 0:>9.2f} {_quote(ms, 'spooling'):>8.1f}%")

    spool_delta = _quote(macro, "spooling") - _quote(ctrl, "spooling")
    print(f"  Spooling-Delta Macro - Kontrolle: {spool_delta:+.2f} pp")

    # Welche der beiden Bedingungen bindet ueberhaupt? Ohne diese Zeile ist die
    # Spooling-Quote nicht interpretierbar: liegt der Median-netto_rel weit ueber
    # SPOOL_NETTO, ist das Flag faktisch nur `dir >= SPOOL_DIR` und die zweite Bedingung
    # reine Dekoration. Gemessen am 2026-08-15 auf EURUSD 2019 war genau das der Fall
    # (Median netto_rel 2,4 gegen Schwelle 1,0) -- ohne den Ausweis haette die Zahl wie ein
    # Zwei-Kriterien-Mass ausgesehen, das sie nicht ist.
    for name, ms in (("Macro", macro), ("Kontr", ctrl)):
        ohne_dir = 100.0 * sum(1 for m in ms if m["dir"] < SPOOL_DIR) / len(ms)
        ohne_netto = 100.0 * sum(1 for m in ms
                                 if m["netto_rel"] is None
                                 or m["netto_rel"] < SPOOL_NETTO) / len(ms)
        beide = 100.0 * sum(1 for m in ms
                            if m["dir"] < SPOOL_DIR
                            and (m["netto_rel"] is None
                                 or m["netto_rel"] < SPOOL_NETTO)) / len(ms)
        print(f"    {name}: an dir gescheitert {ohne_dir:5.1f} %   "
              f"an netto_rel gescheitert {ohne_netto:5.1f} %   an beidem {beide:5.1f} %")

    # Mann-Whitney statt t-Test: Blockgroessen sind rechtsschief, nicht normalverteilt.
    # Vorbehalt wie in der MNQ-Fassung: Bloecke desselben Tages sind nicht unabhaengig,
    # das p ist deshalb optimistisch.
    pvals = {}
    for k in ("range_pips", "netto_pips", "dir", "netto_rel", "fvgs"):
        a = [m[k] for m in macro if m[k] is not None]
        b = [m[k] for m in ctrl if m[k] is not None]
        if a and b:
            pvals[k] = mannwhitneyu(a, b, alternative="greater").pvalue
    print("  Mann-Whitney (Macro > Kontrolle), einseitig:  "
          + "  ".join(f"{k} p={v:.4f}" for k, v in pvals.items()))

    return {"titel": titel, "n_tage": len(tage), "von": str(tage[0]), "bis": str(tage[-1]),
            "n_macro": len(macro), "n_ctrl": len(ctrl),
            "med_range_macro": med([m["range_pips"] for m in macro]),
            "med_range_ctrl": med([m["range_pips"] for m in ctrl]),
            "med_netto_macro": med([m["netto_pips"] for m in macro]),
            "med_netto_ctrl": med([m["netto_pips"] for m in ctrl]),
            "med_dir_macro": med([m["dir"] for m in macro]),
            "med_dir_ctrl": med([m["dir"] for m in ctrl]),
            "spooling_macro_pct": _quote(macro, "spooling"),
            "spooling_ctrl_pct": _quote(ctrl, "spooling"),
            "spooling_delta_pp": spool_delta, "p": pvals}


def je_block(zeilen: list[dict], min_tage: int = 5) -> None:
    """Tabelle je Blocklabel, sortiert nach median range -- wie in der MNQ-Fassung."""
    nach_label: dict[str, list[dict]] = defaultdict(list)
    for m in zeilen:
        nach_label[m["label"]].append(m)
    print(f"\nJe Block (nur Bloecke mit >= {min_tage} Tagen), sortiert nach median range:")
    print(f"  {'Block':<12} {'M':<2} {'n':>7} {'medRange':>10} {'medNetto':>10} "
          f"{'dir':>6} {'Spool%':>8} {'medRang':>8}")
    stats = {label: ms for label, ms in nach_label.items() if len(ms) >= min_tage}
    for label, ms in sorted(stats.items(),
                            key=lambda kv: -(med([m["range_pips"] for m in kv[1]]) or 0)):
        print(f"  {label:<12} {'M' if ms[0]['macro'] else ' ':<2} {len(ms):>7,} "
              f"{med([m['range_pips'] for m in ms]):>10.2f} "
              f"{med([m['netto_pips'] for m in ms]):>10.2f} "
              f"{med([m['dir'] for m in ms]):>6.2f} {_quote(ms, 'spooling'):>7.1f}% "
              f"{med([m['rank'] for m in ms]):>8.1f}")


def schreibe_csv(zeilen: list[dict], fh, kopf: bool) -> None:
    """Rohzeilen anhaengen. Der Messlauf ueber 10 Paare x 23 Jahre ist teuer, das Nachschneiden
    von Schwellen (SPOOL_DIR, SPOOL_NETTO, Regime-Trennung, einzelne Stunden) kostet danach
    Sekunden -- dieselbe Trennung wie bei algo/forex/macro_report.py.

    Geschrieben wird symbolweise statt am Ende, damit die Zeilen aller zehn Paare nie
    gleichzeitig im Speicher liegen muessen (~4,3 Mio. dicts waeren mehrere GB)."""
    w = csv.DictWriter(fh, fieldnames=CSV_FELDER, extrasaction="ignore")
    if kopf:
        w.writeheader()
    for z in zeilen:
        w.writerow(z)


def pool_aus_csv(pfad: Path = BLOCK_CSV, ohne_dst: bool = False) -> dict:
    """Gepoolter Bericht ueber alle Symbole, aus der CSV gestreamt.

    Warum nicht einfach die Zeilen im Speicher behalten: 4,3 Mio. dicts sind mehrere GB. Hier
    landen nur die fuenf Zahlen je Block in `array('d')`-Puffern (8 Byte je Wert statt ~32 fuer
    ein Python-Float in einer Liste), getrennt nach Macro und Kontrolle."""
    from array import array
    puffer = {gruppe: {f: array("d") for f in
                       ("range_pips", "netto_pips", "dir", "netto_rel", "fvgs")}
              for gruppe in ("macro", "ctrl")}
    n_spool = {"macro": 0, "ctrl": 0}
    n_ges = {"macro": 0, "ctrl": 0}
    n_ohne_dir = {"macro": 0, "ctrl": 0}
    n_ohne_netto = {"macro": 0, "ctrl": 0}
    tage: set[str] = set()

    n_dst_raus = 0
    with pfad.open(encoding="utf-8") as fh:
        for z in csv.DictReader(fh):
            if ohne_dst and dst_verdaechtig(date.fromisoformat(z["day"])):
                n_dst_raus += 1
                continue
            g = "macro" if z["macro"] == "True" else "ctrl"
            n_ges[g] += 1
            tage.add(z["day"])
            if z["spooling"] == "True":
                n_spool[g] += 1
            d = float(z["dir"])
            nr = float(z["netto_rel"]) if z["netto_rel"] not in ("", "None") else None
            if d < SPOOL_DIR:
                n_ohne_dir[g] += 1
            if nr is None or nr < SPOOL_NETTO:
                n_ohne_netto[g] += 1
            for f in ("range_pips", "netto_pips", "dir", "fvgs"):
                puffer[g][f].append(float(z[f]))
            if nr is not None:
                puffer[g]["netto_rel"].append(nr)

    if not n_ges["macro"] or not n_ges["ctrl"]:
        return {}

    titel = ("ALLE FX-PAARE GEPOOLT, OHNE DST-VERDAECHTIGE TAGE" if ohne_dst
             else "ALLE FX-PAARE GEPOOLT")
    print(f"\n=== {titel} ===")
    print(f"{len(tage):,} Handelstage, {sum(n_ges.values()):,} auswertbare 20min-Bloecke"
          + (f"   ({n_dst_raus:,} Bloecke wegen DST-Versatz ausgeschlossen)"
             if ohne_dst else ""))
    print(f"  {'':<12} {'n':>9} {'medRange':>10} {'medNetto':>10} {'dir':>6} "
          f"{'nettoRel':>9} {'Spooling':>9}")
    for name, g in (("Macro :50-:10", "macro"), ("Kontrolle", "ctrl")):
        p = puffer[g]
        print(f"  {name:<12} {n_ges[g]:>9,} {statistics.median(p['range_pips']):>10.2f} "
              f"{statistics.median(p['netto_pips']):>10.2f} "
              f"{statistics.median(p['dir']):>6.2f} "
              f"{statistics.median(p['netto_rel']):>9.2f} "
              f"{100 * n_spool[g] / n_ges[g]:>8.1f}%")
    delta = 100 * n_spool["macro"] / n_ges["macro"] - 100 * n_spool["ctrl"] / n_ges["ctrl"]
    print(f"  Spooling-Delta Macro - Kontrolle: {delta:+.2f} pp")
    for name, g in (("Macro", "macro"), ("Kontr", "ctrl")):
        print(f"    {name}: an dir gescheitert {100*n_ohne_dir[g]/n_ges[g]:5.1f} %   "
              f"an netto_rel gescheitert {100*n_ohne_netto[g]/n_ges[g]:5.1f} %")

    pvals = {}
    for f in ("range_pips", "netto_pips", "dir", "netto_rel", "fvgs"):
        a, b = puffer["macro"][f], puffer["ctrl"][f]
        if len(a) and len(b):
            pvals[f] = mannwhitneyu(a, b, alternative="greater").pvalue
    print("  Mann-Whitney (Macro > Kontrolle), einseitig:  "
          + "  ".join(f"{k} p={v:.4f}" for k, v in pvals.items()))

    return {"titel": titel, "n_tage": len(tage), "n_dst_raus": n_dst_raus,
            "n_macro": n_ges["macro"], "n_ctrl": n_ges["ctrl"],
            "med_range_macro": statistics.median(puffer["macro"]["range_pips"]),
            "med_range_ctrl": statistics.median(puffer["ctrl"]["range_pips"]),
            "med_netto_macro": statistics.median(puffer["macro"]["netto_pips"]),
            "med_netto_ctrl": statistics.median(puffer["ctrl"]["netto_pips"]),
            "med_dir_macro": statistics.median(puffer["macro"]["dir"]),
            "med_dir_ctrl": statistics.median(puffer["ctrl"]["dir"]),
            "spooling_macro_pct": 100 * n_spool["macro"] / n_ges["macro"],
            "spooling_ctrl_pct": 100 * n_spool["ctrl"] / n_ges["ctrl"],
            "spooling_delta_pp": delta, "p": pvals}


def selfcheck() -> None:
    # --- Blockraster ------------------------------------------------------------------
    tag = date(2026, 1, 5)
    bs = blocks(tag)
    labels = [b[0] for b in bs]
    assert len(bs) == 72, f"72 Bloecke erwartet, {len(bs)} bekommen"
    assert sum(1 for b in bs if b[3]) == 24, "24 Macro-Fenster -- ein 24/5-Markt hat keine " \
                                             "Globex-Pause, anders als MNQ mit 23"
    assert labels[0] == "00:10-00:30", labels[:3]
    assert labels[-1] == "23:50-00:10", labels[-3:]
    # Lueckenlos und ueberlappungsfrei
    assert all(a[2] == b[1] for a, b in zip(bs, bs[1:])), "Bloecke haben Luecken"
    # Der letzte Block reicht in den Folgetag -- die 10 Minuten 00:00-00:10 gehoeren dem
    # Vortag und werden nicht doppelt gezaehlt.
    assert bs[-1][2].date() == tag + timedelta(days=1), bs[-1]
    # Anders als MNQ gibt es hier ein 17:50-Fenster (dort liegt es in der Handelspause).
    assert any(l.startswith("17:50") for l in labels), "17:50 muss auf 24x5 existieren"
    # Genau 24 Stunden abgedeckt
    assert bs[-1][2] - bs[0][1] == timedelta(hours=24), bs[-1][2] - bs[0][1]

    # --- measure() gegen Handrechnung --------------------------------------------------
    start, ende = at(tag, 9, 50), at(tag, 10, 10)
    pip = PIP_SIZE["EURUSD"]          # 0,0001
    win = [Bar(start + timedelta(minutes=i),
               1.1000 + i * 0.0001, 1.1000 + i * 0.0001 + 0.0002,
               1.1000 + i * 0.0001 - 0.0001, 1.1000 + i * 0.0001 + 0.0001)
           for i in range(20)]
    m = measure(win, pip, 0.0003, None, start, ende)
    assert m is not None
    # High = 1,1019+0,0002 = 1,1021 ; Low = 1,1000-0,0001 = 1,0999 -> 22 Pips
    assert abs(m["range_pips"] - 22.0) < 1e-6, m["range_pips"]
    # Netto = |1,1020 - 1,1000| = 20 Pips
    assert abs(m["netto_pips"] - 20.0) < 1e-6, m["netto_pips"]
    assert abs(m["dir"] - 20 / 22) < 1e-9, m["dir"]
    # Datenluecke -> None
    assert measure(win[:10], pip, 0.0003, None, start, ende) is None

    # --- Spooling: die drei Faelle aus dem Modulkopf ------------------------------------
    # 1. Glatter gerichteter Lauf -> ja
    assert ist_spooling(0.90, 5.0) is True
    # 2. Hin und Her bei gleicher Weglaenge -> nein (dir zu niedrig)
    assert ist_spooling(0.20, 5.0) is False
    # 3. Regungslos, aber formal perfekt gerichtet -> nein.
    #    Das ist die stille Fehlmessung, gegen die SPOOL_NETTO existiert: ICTs
    #    "if the market simply doesn't budge" ist ausdruecklich KEIN Spooling.
    assert ist_spooling(1.00, 0.1) is False
    # Genau auf der Schwelle zaehlt als ja (>=, nicht >)
    assert ist_spooling(SPOOL_DIR, SPOOL_NETTO) is True
    # Unbekannter Massstab darf kein Ja erzeugen
    assert ist_spooling(1.00, None) is False

    # measure() muss das Flag durchreichen: derselbe Block einmal mit winzigem, einmal mit
    # grossem Tagesmedian -- nur die Skala entscheidet.
    m_gross = measure(win, pip, 0.0001, None, start, ende)   # netto_rel = 20
    m_klein = measure(win, pip, 0.0100, None, start, ende)   # netto_rel = 0,2
    assert m_gross["spooling"] is True, m_gross
    assert m_klein["spooling"] is False, m_klein

    # --- Bindungs-Diagnose im Report ---------------------------------------------------
    # Regressionswaechter fuer den Fund vom 2026-08-15: auf echten Daten liegt der
    # Median-netto_rel bei ~2,4 gegen eine Schwelle von 1,0 -- die zweite Bedingung bindet
    # dann praktisch nie und das Flag ist faktisch nur `dir >= SPOOL_DIR`. Der Report muss
    # das ausweisen, sonst sieht die Quote nach einem Zwei-Kriterien-Mass aus.
    import io
    import contextlib
    kunst = [{"macro": True, "day": tag, "label": "09:50-10:10", "range_pips": 10.0,
              "netto_pips": 9.0, "dir": 0.9, "netto_rel": 5.0, "fvgs": 0, "rank": 1,
              "n_blocks": 72, "spooling": True},
             {"macro": False, "day": tag, "label": "10:10-10:30", "range_pips": 10.0,
              "netto_pips": 1.0, "dir": 0.1, "netto_rel": 5.0, "fvgs": 0, "rank": 2,
              "n_blocks": 72, "spooling": False}]
    puffer = io.StringIO()
    with contextlib.redirect_stdout(puffer):
        report(kunst, "SELBSTCHECK")
    text = puffer.getvalue()
    assert "an dir gescheitert" in text, text
    assert "Macro: an dir gescheitert   0.0 %" in text, text
    assert "Kontr: an dir gescheitert 100.0 %" in text, text
    # Beide netto_rel liegen ueber der Schwelle -> die zweite Bedingung bindet nirgends.
    assert "an netto_rel gescheitert   0.0 %" in text, text

    # --- Bisektions-Schnitt liefert dasselbe wie die naive Filterung --------------------
    alle = [Bar(at(tag, 0, 0) + timedelta(minutes=i), 1.1, 1.1, 1.1, 1.1) for i in range(500)]
    zeiten = [b.t for b in alle]
    for s, e in ((at(tag, 0, 10), at(tag, 0, 30)), (at(tag, 5, 50), at(tag, 6, 10)),
                 (at(tag, 8, 0), at(tag, 8, 20))):
        naiv = [b for b in alle if s <= b.t < e]
        assert _schneide(alle, zeiten, s, e) == naiv, (s, e)

    # --- Alle Forex-Symbole haben eine PIP_SIZE ----------------------------------------
    assert len(FOREX_SYMBOLE) == 10, FOREX_SYMBOLE
    for s in FOREX_SYMBOLE:
        assert s in PIP_SIZE, s

    # --- DST-Fenster gegen bekannte Umstellungstermine ---------------------------------
    # Sonntagsberechnung zuerst, sonst pruefe ich das Fenster gegen dieselbe moegliche
    # Fehlannahme, aus der es entstanden ist.
    assert _nter_sonntag(2019, 3, 2) == date(2019, 3, 10), _nter_sonntag(2019, 3, 2)
    assert _nter_sonntag(2019, 3, -1) == date(2019, 3, 31), _nter_sonntag(2019, 3, -1)
    assert _nter_sonntag(2019, 10, -1) == date(2019, 10, 27), _nter_sonntag(2019, 10, -1)
    assert _nter_sonntag(2019, 11, 1) == date(2019, 11, 3), _nter_sonntag(2019, 11, 1)
    # Maerz 2021 begann selbst an einem Montag -- Randfall fuer "erster Sonntag".
    assert _nter_sonntag(2021, 3, 2) == date(2021, 3, 14), _nter_sonntag(2021, 3, 2)
    # Oktober 2020 endete an einem Samstag -- Randfall fuer "letzter Sonntag".
    assert _nter_sonntag(2020, 10, -1) == date(2020, 10, 25), _nter_sonntag(2020, 10, -1)

    # Fruehjahrsfenster 2019: US ab 10.03. auf Sommerzeit, EU erst ab 31.03.
    assert dst_verdaechtig(date(2019, 3, 10)) is True
    assert dst_verdaechtig(date(2019, 3, 20)) is True
    assert dst_verdaechtig(date(2019, 3, 30)) is True
    assert dst_verdaechtig(date(2019, 3, 31)) is False, "ab EU-Umstellung wieder synchron"
    assert dst_verdaechtig(date(2019, 3, 9)) is False, "vor US-Umstellung synchron"
    # Herbstfenster 2019: EU ab 27.10. zurueck, US erst ab 03.11.
    assert dst_verdaechtig(date(2019, 10, 27)) is True
    assert dst_verdaechtig(date(2019, 11, 2)) is True
    assert dst_verdaechtig(date(2019, 11, 3)) is False
    assert dst_verdaechtig(date(2019, 10, 26)) is False
    # Gewoehnliche Tage
    assert dst_verdaechtig(date(2019, 7, 1)) is False
    assert dst_verdaechtig(date(2019, 1, 15)) is False
    # Vor 2019 folgte der Endpoint der US-Regel und war korrekt -- derselbe Kalendertag,
    # aber ein Jahr frueher, muss sauber sein.
    assert dst_verdaechtig(date(2018, 3, 20)) is False, "vor 2019 kein Versatz"
    assert dst_verdaechtig(date(2018, 10, 30)) is False, "vor 2019 kein Versatz"

    # Umfang plausibel: ~4 Wochen je Jahr ab 2019 (die Wiki-Seite nennt 140 Handelstage
    # je Paar ueber alle Jahre -- hier nur die Groessenordnung, nicht die Handelstage).
    n_2019 = sum(1 for i in range(365)
                 if dst_verdaechtig(date(2019, 1, 1) + timedelta(days=i)))
    assert 25 <= n_2019 <= 32, n_2019

    print("forex.backtest_macro selfcheck: OK")


def demo() -> None:
    """Alias fuer algo/forex/selfcheck.py, das `demo()` erwartet."""
    selfcheck()


def main(argv=None) -> int:
    global MIN_FVG_REL, SPOOL_DIR, SPOOL_NETTO
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--symbols", nargs="*", default=None)
    ap.add_argument("--all", action="store_true", help=f"alle {len(FOREX_SYMBOLE)} FX-Paare")
    ap.add_argument("--von", default=None, help="JJJJ-MM-TT")
    ap.add_argument("--bis", default=None, help="JJJJ-MM-TT")
    ap.add_argument("--ohne-fvgs", action="store_true",
                    help="FVG-Zaehlung ueberspringen (deutlich schneller)")
    ap.add_argument("--min-fvg", type=float, default=None)
    ap.add_argument("--spool-dir", type=float, default=None)
    ap.add_argument("--spool-netto", type=float, default=None)
    ap.add_argument("--je-block", action="store_true", help="Tabelle je Blocklabel")
    ap.add_argument("--selfcheck", action="store_true")
    a = ap.parse_args(argv)

    if a.selfcheck:
        selfcheck()
        return 0

    if a.min_fvg is not None:
        MIN_FVG_REL = a.min_fvg
    if a.spool_dir is not None:
        SPOOL_DIR = a.spool_dir
    if a.spool_netto is not None:
        SPOOL_NETTO = a.spool_netto

    symbole = list(FOREX_SYMBOLE) if a.all else (a.symbols or ["EURUSD"])
    von = date.fromisoformat(a.von) if a.von else None
    bis = date.fromisoformat(a.bis) if a.bis else None

    print(f"Symbole: {', '.join(symbole)}   Zeitraum: {von or 'Anfang'} .. {bis or 'Ende'}   "
          f"Spooling: dir >= {SPOOL_DIR}, netto_rel >= {SPOOL_NETTO}")

    berichte = []
    n_zeilen = 0
    BLOCK_CSV.parent.mkdir(exist_ok=True)
    with BLOCK_CSV.open("w", newline="", encoding="utf-8") as fh:
        for i, sym in enumerate(symbole):
            zeilen = collect(sym, von, bis, mit_fvgs=not a.ohne_fvgs)
            if not zeilen:
                print(f"{sym}: keine Daten.")
                continue
            b = report(zeilen, f"{sym} (FX Spot)")
            if b:
                berichte.append(b)
            if a.je_block:
                je_block(zeilen)
            schreibe_csv(zeilen, fh, kopf=(n_zeilen == 0))
            n_zeilen += len(zeilen)
            fh.flush()
            del zeilen          # bevor das naechste Symbol geladen wird

    if not n_zeilen:
        return 1
    print(f"\nRohzeilen -> {BLOCK_CSV}  ({n_zeilen:,} Bloecke)")

    if len(berichte) > 1:
        b = pool_aus_csv()
        if b:
            berichte.append(b)

    write_result("forex_macro", {"spool_dir": SPOOL_DIR, "spool_netto": SPOOL_NETTO,
                                 "min_fvg_rel": MIN_FVG_REL, "berichte": berichte})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
