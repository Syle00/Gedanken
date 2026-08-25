#!/usr/bin/env python3
"""Selbstcheck fuer tools/dashboard_serve.py -- reine asserts, kein Framework.

Aufruf: python tools/test_dashboard.py
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dashboard_serve as ds


def test_letzter_werktag():
    # Montag 24.08.2026 -> erwartet wird der Freitag davor, nicht das Wochenende
    assert ds._letzter_werktag(date(2026, 8, 24)) == date(2026, 8, 21)
    # Mittwoch -> Dienstag
    assert ds._letzter_werktag(date(2026, 8, 26)) == date(2026, 8, 25)
    # Sonntag -> Freitag
    assert ds._letzter_werktag(date(2026, 8, 23)) == date(2026, 8, 21)


def test_werktage():
    # Freitag -> Montag ist genau ein Werktag Rueckstand, nicht drei Kalendertage
    assert ds._werktage(date(2026, 8, 21), date(2026, 8, 24)) == 1
    assert ds._werktage(date(2026, 8, 24), date(2026, 8, 24)) == 0
    assert ds._werktage(date(2026, 8, 21), date(2026, 8, 26)) == 3


def test_sicher_faengt_fehler():
    def kaputt():
        raise RuntimeError("boom")

    r = ds.sicher(kaputt)
    assert r["data"] is None
    assert "boom" in r["error"]
    assert r["age_s"] is None

    r = ds.sicher(lambda: ({"x": 1}, 42.0))
    assert r == {"data": {"x": 1}, "error": None, "age_s": 42.0}


def test_state_hat_alle_panels():
    s = ds.state()
    for panel in ("now", "daten"):
        assert panel in s, panel
    assert set(s["daten"]) == {"data", "error", "age_s"}


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"ok  {name}")
    print("alle Tests bestanden")
