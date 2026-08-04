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
import sys
from pathlib import Path

LIVE_DIR = Path(__file__).resolve().parent / "live"


def event_key(d: dict, field: str) -> list:
    """Identitaet eines Ereignisses ueber Laeufe hinweg: Kerzenzeit + Seite/Richtung."""
    t = d["t"]
    return [t.isoformat() if hasattr(t, "isoformat") else t, d[field]]


def load_state(path: Path) -> dict:
    if not path.exists():
        return {"fvgs": [], "sweeps": [], "structure_breaks": [], "setup": None}
    return json.loads(path.read_text(encoding="utf-8"))


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
    from datetime import datetime

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


def main(argv=None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if "--selftest" in args:
        selftest()
        return 0
    print("noch nicht implementiert", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
