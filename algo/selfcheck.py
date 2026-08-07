#!/usr/bin/env python3
"""Buendelt alle demo()-Selbstchecks aus dem Praezisions-Audit
(docs/superpowers/specs/2026-08-06-algo-backtest-precision-audit-design.md) zu einem
Kommando -- gedacht als schneller taeglicher Regressions-Check (Sekunden, kein neuer
Backtest-Lauf, buendelt nur bestehende kleine Checks). Die Ausloese-Mechanik (Erinnerung/Loop)
ist Teil von Teilprojekt B, nicht dieses Moduls.

Aufruf:
    python algo/selfcheck.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from pnl import demo as pnl_demo  # noqa: E402
from rules import demo as rules_demo  # noqa: E402
from signals import _demo as signals_demo  # noqa: E402
from backtest_ensemble import _demo as ensemble_demo  # noqa: E402

CHECKS = [
    ("pnl", pnl_demo),
    ("rules", rules_demo),
    ("signals", signals_demo),
    ("backtest_ensemble", ensemble_demo),
]


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    failed = []
    for name, check in CHECKS:
        try:
            check()
        except Exception as exc:  # noqa: BLE001
            failed.append((name, exc))
            print(f"[FAIL] {name}: {exc}")
        else:
            print(f"[OK]   {name}")
    if failed:
        print(f"\n{len(failed)}/{len(CHECKS)} Selbstchecks fehlgeschlagen.")
        return 1
    print(f"\nAlle {len(CHECKS)} Selbstchecks bestanden.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
