"""Baut aus einer 1m-Datei in raw/marktdaten/ die hoeheren Timeframes (5m/15m/1h/4h/1d).

Bucket-Konvention geprueft gegen echte TradingView-Exporte (03.08./11.08.2026):
- 5m/15m/1h/4h: Timestamp = Oeffnungszeit, Fenster [t, t+tf) in UTC-Sekunden, clock-aligned
  ab Unix-Epoche (pandas resample Default-Origin "epoch" trifft das exakt).
- 1d: EINE Kerze pro Datei (= ganze Session, 18:00 NY Vortag -> 17:00 NY), nicht
  kalendertagsweise -- pandas' Default-Origin fuer "1D" ("start_day") erzeugt sonst 2
  krumme Teil-Buckets. Label = 00:00 UTC des Handelstags aus dem Dateinamen (= 20:00 NY
  Vortag; beobachtet an 1786406400 = 2026-08-11 00:00 UTC fuer die Session "11.08.2026").

Aufruf:
    python tools/resample_1m.py <1m-Datei>
    python tools/resample_1m.py --demo
"""
import datetime
import re
import sys
from pathlib import Path

import pandas as pd

RULES = {"5m": "5min", "15m": "15min", "1h": "1h", "4h": "4h"}


def resample(pfad_1m: Path):
    df = pd.read_csv(pfad_1m)
    df["time"] = pd.to_datetime(df["time"], unit="s").dt.as_unit("s")
    df = df.set_index("time").sort_index()
    out = {}
    for tf, rule in RULES.items():
        agg = df.resample(rule, label="left", closed="left").agg(
            {"open": "first", "high": "max", "low": "min", "close": "last"}
        ).dropna()
        agg.index = agg.index.astype("int64")  # bereits Sekunden dank as_unit("s") oben
        out[tf] = agg

    m = re.search(r"(\d{4}-\d{2}-\d{2})", pfad_1m.stem)
    tag = datetime.date.fromisoformat(m.group(1))
    label = int(datetime.datetime(tag.year, tag.month, tag.day, tzinfo=datetime.timezone.utc).timestamp())
    out["1d"] = pd.DataFrame(
        {"open": [df["open"].iloc[0]], "high": [df["high"].max()],
         "low": [df["low"].min()], "close": [df["close"].iloc[-1]]},
        index=pd.Index([label], name="time"),
    )
    return out


def schreib(agg: pd.DataFrame, pfad: Path):
    pfad.parent.mkdir(parents=True, exist_ok=True)
    agg.reset_index().rename(columns={"time": "time"}).to_csv(pfad, index=False)


def demo():
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "MNQ 2026-08-11 1m.csv"
        rows = [(1786435200 + i * 60, 100 + i, 101 + i, 99 + i, 100.5 + i) for i in range(10)]
        pd.DataFrame(rows, columns=["time", "open", "high", "low", "close"]).to_csv(p, index=False)
        out = resample(p)
        first5 = out["5m"].iloc[0]
        assert first5["open"] == 100, "open muss erste 1m-Kerze sein"
        assert first5["close"] == 104.5, "close muss letzte 1m-Kerze im Fenster sein"
        assert first5["high"] == 105, "high muss max ueber 5 Kerzen sein"
        assert first5["low"] == 99, "low muss min ueber 5 Kerzen sein"
        assert len(out["5m"]) == 2, "10 1m-Kerzen muessen 2 5m-Kerzen ergeben"
        assert len(out["1d"]) == 1, "1d muss genau eine Kerze pro Datei ergeben"
        d1 = out["1d"].iloc[0]
        assert d1["open"] == 100 and d1["close"] == 109.5, "1d muss ganze Datei aggregieren"
        assert int(out["1d"].index[0]) == 1786406400, "1d-Label muss 00:00 UTC des Handelstags sein"
    print("resample_1m: alle Selbstchecks bestanden")


if __name__ == "__main__":
    if "--demo" in sys.argv:
        demo()
    elif len(sys.argv) >= 2:
        quelle = Path(sys.argv[1])
        stamm = quelle.stem.rsplit(" ", 1)[0]  # "MNQ 2026-08-11 1m" -> "MNQ 2026-08-11"
        for tf, agg in resample(quelle).items():
            ziel = quelle.with_name(f"{stamm} {tf}.csv")
            schreib(agg, ziel)
            print(f"{ziel.name}: {len(agg)} Kerzen")
    else:
        print(__doc__)
