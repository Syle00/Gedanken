#!/usr/bin/env python3
"""Sammel-Selbstcheck fuer algo/forex/ -- das Gegenstueck zu algo/selfcheck.py, das dieselbe
Rolle fuer die MNQ-Seite hat (Spec §6.5).

Buendelt die Modul-Selbstchecks und ergaenzt den DRIFT-WAECHTER: weil die Nutzerentscheidung
vom 2026-08-15 bewusst getrennte Module statt einer geteilten Basis vorsieht, existiert die
Silver-Bullet-Logik doppelt. Ein Bugfix in algo/rules.py, der hier nicht nachgezogen wird,
waere sonst unsichtbar. Der Waechter kann das nicht verhindern -- er macht es sichtbar.

Aufruf:
    python algo/forex/selfcheck.py
"""
from __future__ import annotations

import hashlib
import re
import sys
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

MODULE = ["forex.pnl", "forex.rules", "forex.backtest", "forex.macro_report",
          "forex.backtest_macro"]

# Funktionen, die aus algo/rules.py uebernommen wurden, mit dem Stand ihres MNQ-Originals zum
# Zeitpunkt der Uebernahme. Weicht das Original spaeter ab, meldet der Waechter das -- dann ist
# zu entscheiden, ob der Fix auch hier gilt.
#
# Der Hash deckt den normalisierten Funktionsrumpf ab (Kommentare/Docstrings/Leerzeilen raus,
# Whitespace vereinheitlicht): eine reine Kommentaraenderung soll keinen Fehlalarm ausloesen,
# eine Logikaenderung dagegen immer. Beim Nachziehen den neuen Hash hier eintragen und im
# Commit begruenden, warum die Forex-Seite mitgeht oder bewusst nicht.
DRIFT_WACHE = {
    "sb_entry_signal": "72ab0c9a29b78b01",
    "plan_trade": "6b81b535b549046f",
    "plan_trade_hp_fvg": "9bbb1fcf5c281289",
}


def _rumpf_hash(quelle: str, funktion: str) -> str | None:
    """Normalisierter Hash des Funktionsrumpfs aus einer Python-Datei.

    Bewusst textbasiert statt ueber ast/inspect: der Waechter soll auch dann noch
    funktionieren, wenn algo/rules.py sich gerade nicht importieren laesst (kaputte
    Abhaengigkeit, halber Refactor) -- genau in solchen Momenten ist Drift wahrscheinlich.
    """
    zeilen = quelle.splitlines()
    start = next((i for i, z in enumerate(zeilen)
                  if re.match(rf"^def {re.escape(funktion)}\b", z)), None)
    if start is None:
        return None
    ende = len(zeilen)
    for i in range(start + 1, len(zeilen)):
        if zeilen[i] and not zeilen[i][0].isspace() and not zeilen[i].startswith(")"):
            ende = i
            break
    rumpf = zeilen[start:ende]

    # Docstrings und Kommentare raus.
    ohne: list[str] = []
    in_doc = False
    for z in rumpf:
        s = z.strip()
        if in_doc:
            if s.endswith('"""') or s.endswith("'''"):
                in_doc = False
            continue
        if s.startswith('"""') or s.startswith("'''"):
            if not (len(s) > 3 and (s.endswith('"""') or s.endswith("'''"))):
                in_doc = True
            continue
        s = re.sub(r"#.*$", "", s).strip()
        if s:
            ohne.append(re.sub(r"\s+", " ", s))
    return hashlib.sha256("\n".join(ohne).encode("utf-8")).hexdigest()[:16]


def pruefe_drift(schreibe_hashes: bool = False) -> list[str]:
    """Meldungen zurueckgeben statt zu werfen: Drift ist ein Hinweis, kein Testfehler --
    ein bewusst nur auf einer Seite gemachter Fix ist legitim, muss aber auffallen."""
    quelle = (_ALGO / "rules.py").read_text(encoding="utf-8")
    meldungen = []
    for fn, erwartet in DRIFT_WACHE.items():
        ist = _rumpf_hash(quelle, fn)
        if ist is None:
            meldungen.append(f"  ! {fn}: in algo/rules.py nicht mehr gefunden (umbenannt?)")
        elif schreibe_hashes:
            meldungen.append(f'    "{fn}": "{ist}",')
        elif ist != erwartet:
            meldungen.append(
                f"  ! {fn}: algo/rules.py hat sich geaendert ({erwartet} -> {ist}). "
                f"Pruefen, ob algo/forex/rules.py mitgezogen werden muss.")
    return meldungen


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if "--hashes" in argv:
        # Hilfsmodus zum Neusetzen der Wache nach einer bewussten Uebernahme.
        print("DRIFT_WACHE = {")
        for z in pruefe_drift(schreibe_hashes=True):
            print(z)
        print("}")
        return 0

    fehler = 0
    for name in MODULE:
        modul = __import__(name, fromlist=["demo"])
        try:
            modul.demo()
            print(f"[OK]   {name}")
        except AssertionError as e:
            print(f"[FEHL] {name}: {e}")
            fehler += 1

    print()
    meldungen = pruefe_drift()
    if meldungen:
        print("Drift-Waechter gegen algo/rules.py:")
        for z in meldungen:
            print(z)
        print("  (Hinweis, kein Fehler -- siehe Modul-Doku. Nach dem Nachziehen "
              "`python algo/forex/selfcheck.py --hashes` und die Wache aktualisieren.)")
    else:
        print("Drift-Waechter: algo/rules.py unveraendert gegenueber dem Uebernahmestand.")

    print()
    if fehler:
        print(f"{fehler} Selbstcheck(s) fehlgeschlagen.")
        return 1
    print(f"Alle {len(MODULE)} Forex-Selbstchecks bestanden.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
