#!/usr/bin/env python3
"""Buendelt alle demo()-Selbstchecks aus dem Praezisions-Audit
(docs/superpowers/specs/2026-08-06-algo-backtest-precision-audit-design.md) und den
Schnittstellen-Check der 11 entduplizierten Explorationsskripte
(docs/superpowers/specs/2026-08-07-algo-backtest-dedup-audit-design.md) zu einem
Kommando -- gedacht als schneller Regressions-Check, kein neuer inhaltlicher Backtest.

Aufruf:
    python algo/selfcheck.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from pnl import demo as pnl_demo  # noqa: E402
from risk_fixed import demo as risk_fixed_demo  # noqa: E402
from risk_garch import demo as risk_garch_demo  # noqa: E402
from risk_kelly import demo as risk_kelly_demo  # noqa: E402
from risk_killswitch import demo as risk_killswitch_demo  # noqa: E402
from masters import demo as masters_demo  # noqa: E402
from confidence import demo as confidence_demo  # noqa: E402
from rules import demo as rules_demo  # noqa: E402
from signals import _demo as signals_demo  # noqa: E402
from backtest_ensemble import _demo as ensemble_demo  # noqa: E402
from backtest_bt import demo as backtest_bt_demo  # noqa: E402
from backtest_risk_compare import demo as backtest_risk_compare_demo  # noqa: E402
from validate import demo as validate_demo  # noqa: E402
from backtest_common import demo as backtest_common_demo  # noqa: E402
from macro_db import selfcheck as macro_db_selfcheck  # noqa: E402
from backtest_fvg_strength import selfcheck as fvg_strength_selfcheck  # noqa: E402
from backtest_hp_fvg import selfcheck as hp_fvg_selfcheck  # noqa: E402
from backtest_1p_mindestgroesse import selfcheck as mindestgroesse_selfcheck  # noqa: E402
from analyze_ohlc import demo_pruefe_kerzen, demo_session_guard  # noqa: E402


def _results_demo() -> None:
    """run() liefert ein dict, write_result() schreibt gueltiges JSON -- fuer jedes der 11
    im Dedup-Audit (2026-08-07) umgebauten Skripte. Kein Zahlen-Assert, nur Interface.

    Schreibt in ein Tempdir (gleiches Muster wie backtest_common.py::demo()), NIE nach
    algo/results/: main() jedes Skripts persistiert dort bewusst eine kompakte
    Zusammenfassung, nicht den vollen run()-Dict hier -- ein direkter write_result()-Aufruf
    gegen das echte RESULTS_DIR wuerde die committeten JSONs mit einem anderen Schema
    ueberschreiben."""
    import tempfile
    import backtest_daily_patterns
    import backtest_nwog
    import backtest_tgif
    import backtest_ndog
    import backtest_fred_events
    import backtest_org_ce
    import backtest_fvg_specialness
    import backtest_midnight_range_std
    import backtest_midnight_range_judas
    import backtest_ohlc
    import backtest_seasonal
    import backtest_common

    checks = [
        ("backtest_daily_patterns", backtest_daily_patterns.run),
        ("backtest_nwog", backtest_nwog.run),
        ("backtest_tgif", backtest_tgif.run),
        ("backtest_ndog", backtest_ndog.run),
        ("backtest_fred_events", backtest_fred_events.run),
        ("backtest_org_ce", backtest_org_ce.run),
        ("backtest_fvg_specialness", backtest_fvg_specialness.run),
        ("backtest_midnight_range_std", backtest_midnight_range_std.run),
        ("backtest_midnight_range_judas", backtest_midnight_range_judas.run),
        ("backtest_ohlc", lambda: backtest_ohlc.run("MNQ")),
    ]
    orig_results_dir = backtest_common.RESULTS_DIR
    with tempfile.TemporaryDirectory() as tmp:
        backtest_common.RESULTS_DIR = Path(tmp)
        for name, call in checks:
            result = call()
            assert isinstance(result, dict), f"{name}.run() liefert kein dict"
            backtest_common.write_result(name, result)
            path = backtest_common.RESULTS_DIR / f"{name}.json"
            assert path.exists(), f"{name}: {path} wurde nicht geschrieben"
            json.loads(path.read_text(encoding="utf-8"))  # wirft bei ungueltigem JSON
    backtest_common.RESULTS_DIR = orig_results_dir

    assert isinstance(backtest_seasonal.run(), dict), "backtest_seasonal.run() liefert kein dict"


CHECKS = [
    ("pnl", pnl_demo),
    ("risk_fixed", risk_fixed_demo),
    ("risk_garch", risk_garch_demo),
    ("risk_kelly", risk_kelly_demo),
    ("risk_killswitch", risk_killswitch_demo),
    ("masters", masters_demo),
    ("confidence", confidence_demo),
    ("rules", rules_demo),
    ("signals", signals_demo),
    ("backtest_ensemble", ensemble_demo),
    ("backtest_bt", backtest_bt_demo),
    ("backtest_risk_compare", backtest_risk_compare_demo),
    ("validate", validate_demo),
    ("backtest_common", backtest_common_demo),
    ("macro_db", macro_db_selfcheck),
    ("backtest_fvg_strength", fvg_strength_selfcheck),
    ("backtest_hp_fvg", hp_fvg_selfcheck),
    ("backtest_1p_mindestgroesse", mindestgroesse_selfcheck),
    ("ohlc_gate", demo_pruefe_kerzen),
    ("session_guard", demo_session_guard),
    ("dedup", _results_demo),
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
