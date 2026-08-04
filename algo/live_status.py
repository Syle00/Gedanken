#!/usr/bin/env python3
"""Live-Status-Zyklus fuer MNQ: zieht den heutigen Handelstag per yfinance, laesst die
bestehenden Detektoren aus tools/analyze_ohlc.py + algo/rules.py darueber laufen und
gibt eine JSON-Zusammenfassung der *neuen* Ereignisse seit dem letzten Lauf aus.
Siehe docs/superpowers/specs/2026-08-04-algo-live-status-loop-design.md.

Aufruf:
    python algo/live_status.py                       # live: heutiger Handelstag
    python algo/live_status.py --dry-run 2026-07-31   # Pipeline gegen einen fertigen Tag testen
    python algo/live_status.py --selftest             # reine Funktions-Selbstchecks
"""

from __future__ import annotations

import json
import statistics
import sys
from dataclasses import asdict
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from analyze_ohlc import (  # noqa: E402
    Bar, load, fvgs, sweeps, structure_breaks, macro_windows, TF_MINUTES, CFG,
)
from rules import plan_trade, _active_window  # noqa: E402

BASE_TF = "5m"
_tf_min = TF_MINUTES[BASE_TF]
CFG.update(min_age=max(3, round(15 / _tf_min)), confirm=max(2, round(5 / _tf_min)))

LIVE_DIR = Path(__file__).resolve().parent / "live"


def event_key(d: dict, field: str) -> list:
    """Identitaet eines Ereignisses ueber Laeufe hinweg: Kerzenzeit + Seite/Richtung."""
    t = d["t"]
    return [t.isoformat() if hasattr(t, "isoformat") else t, d[field]]


def load_state(path: Path) -> dict:
    if not path.exists():
        return {"fvgs": [], "sweeps": [], "structure_breaks": [], "setup": None}
    return json.loads(path.read_text(encoding="utf-8"))


def run_detectors(bars: list[Bar], day: date, now: datetime) -> dict:
    """Reine Funktion: bestehende Detektoren auf `bars` (Basis-TF 5m, siehe BASE_TF) +
    plan_trade(). Feldnamen matchen die Kategorien aus diff_events() (Task 1)."""
    if not bars:
        return {"price": None, "active_macro_window": None,
                "active_silver_bullet_window": None, "setup": None,
                "fvgs": [], "sweeps": [], "structure_breaks": []}

    med_bar = statistics.median(b.rng for b in bars) or 1.0
    fg = fvgs(bars)
    sw = sweeps(bars, CFG["swing"], CFG["min_age"], CFG["min_pen"] * med_bar, CFG["confirm"])
    sb = structure_breaks(bars, CFG["swing"], CFG["min_age"])
    setup = plan_trade(bars, now)

    active_macro = None
    for name, start, end in macro_windows(day):
        if start <= now < end:
            active_macro = {"name": name, "start": start.isoformat(), "end": end.isoformat()}
            break
    win = _active_window(day, now)

    last = bars[-1]
    return {
        "price": {"last": last.c, "t": last.t.isoformat()},
        "active_macro_window": active_macro,
        "active_silver_bullet_window": win[0] if win else None,
        "setup": asdict(setup) if setup else None,
        "fvgs": fg, "sweeps": sw, "structure_breaks": sb,
    }


def diff_events(current: dict, prev_state: dict) -> tuple[list[dict], dict]:
    """Vergleicht aktuelle Detektor-Ergebnisse mit dem letzten gespeicherten Snapshot.
    Liefert (neue Ereignisse seit dem letzten Lauf, neuer Snapshot fuer state.json)."""
    new_events: list[dict] = []
    new_state: dict = {}
    categories = [("fvgs", "side"), ("sweeps", "side"), ("structure_breaks", "dir")]
    for field, side_field in categories:
        prev_keys = {tuple(k) for k in prev_state.get(field, [])}
        keys = []
        for d in current[field]:
            k = tuple(event_key(d, side_field))
            keys.append(list(k))
            if k not in prev_keys:
                new_events.append({"kind": field[:-1], **d})
        new_state[field] = keys

    prev_setup, cur_setup = prev_state.get("setup"), current["setup"]
    if cur_setup and cur_setup != prev_setup:
        new_events.append({"kind": "setup_entered", **cur_setup})
    elif prev_setup and not cur_setup:
        new_events.append({"kind": "setup_exited", **prev_setup})
    new_state["setup"] = cur_setup

    return new_events, new_state


def selftest() -> None:
    t1 = datetime(2026, 8, 4, 10, 5)
    fvg = {"t": t1, "side": "bullish", "lo": 100.0, "hi": 101.0, "ce": 100.5}

    current = {"fvgs": [fvg], "sweeps": [], "structure_breaks": [], "setup": None}
    empty_state = {"fvgs": [], "sweeps": [], "structure_breaks": [], "setup": None}
    events, state = diff_events(current, empty_state)
    assert len(events) == 1 and events[0]["kind"] == "fvg", events

    events2, _ = diff_events(current, state)
    assert events2 == [], events2

    setup = {"t": t1, "window": "NY AM Silver Bullet", "side": "long",
             "entry": 100.5, "stop": 99.0, "target": 105.0}
    with_setup = {"fvgs": [], "sweeps": [], "structure_breaks": [], "setup": setup}
    events3, state3 = diff_events(with_setup, empty_state)
    assert any(e["kind"] == "setup_entered" for e in events3), events3

    without_setup = {"fvgs": [], "sweeps": [], "structure_breaks": [], "setup": None}
    events4, _ = diff_events(without_setup, state3)
    assert any(e["kind"] == "setup_exited" for e in events4), events4

    print("selftest (Task 1: diff_events) ok")

    # Task 2: run_detectors gegen echte, bereits abgeschlossene Daten (31.07.2026).
    day_path = (Path(__file__).resolve().parent.parent / "raw" / "marktdaten"
                / "2026" / "07" / "31.07.2026" / "MNQ 2026-07-31 5m.csv")
    real_bars = load(day_path)
    det = run_detectors(real_bars, date(2026, 7, 31), real_bars[-1].t)
    assert det["price"]["last"] == real_bars[-1].c
    assert isinstance(det["fvgs"], list) and isinstance(det["sweeps"], list)
    empty_det = run_detectors([], date(2026, 7, 31), real_bars[-1].t)
    assert empty_det["price"] is None and empty_det["fvgs"] == []
    print("selftest (Task 2: run_detectors) ok")


def main(argv=None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if "--selftest" in args:
        selftest()
        return 0
    print("noch nicht implementiert", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
