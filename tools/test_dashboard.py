#!/usr/bin/env python3
"""Selbstcheck fuer tools/dashboard_serve.py -- reine asserts, kein Framework.

Aufruf: python tools/test_dashboard.py
"""
from __future__ import annotations

import sys
import time
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


def test_ziel_pfad_whitelist():
    # erlaubt
    assert ds.ziel_pfad("planung/2026-08-25.md").name == "2026-08-25.md"
    assert ds.ziel_pfad("raw/journal/Daily Bias 2026-08-25.md").parent.name == "journal"
    assert ds.ziel_pfad("wiki/lernpfad/Lernpfad — Woche 01.md").parent.name == "lernpfad"

    # abgelehnt: Traversal, absolute Pfade, Marktdaten, falsche Endung
    for boese in ("planung/../raw/marktdaten/kaputt.md",
                  "raw/marktdaten/NQ.md",
                  "C:/Windows/Temp/x.md",
                  "/etc/passwd",
                  "wiki/index.md",
                  "planung/notiz.txt"):
        try:
            ds.ziel_pfad(boese)
        except ValueError:
            continue
        raise AssertionError(f"haette abgelehnt werden muessen: {boese}")


def test_atomarer_write():
    import os
    ziel = ds.VAULT / "planung" / "_test_atomar.md"
    try:
        ds.schreibe_atomar(ziel, "alt")
        assert ziel.read_text(encoding="utf-8") == "alt"

        # simulierter Abbruch mitten im Schreiben: die alte Datei bleibt unangetastet
        echt = os.replace
        os.replace = lambda *a, **k: (_ for _ in ()).throw(OSError("abgebrochen"))
        try:
            ds.schreibe_atomar(ziel, "neu-halb")
        except OSError:
            pass
        finally:
            os.replace = echt
        assert ziel.read_text(encoding="utf-8") == "alt", "Teildatei ueberschrieben"
    finally:
        ziel.unlink(missing_ok=True)
        for rest in ziel.parent.glob("_test_atomar.md.tmp"):
            rest.unlink()


def test_parse_briefing():
    text = ("---\ntyp: morgen-briefing\n---\n\n"
            "Erster Absatz.\n\n"
            "## Termine\n\n"
            "- 09:00 — Uni Mathe\n"
            "- 14:30 — Call Quant\n\n"
            "## Sonstiges\n\n"
            "- kein Termin, sondern eine Notiz\n")
    r = ds._parse_briefing(text)
    assert r["termine"] == [{"zeit": "09:00", "titel": "Uni Mathe"},
                            {"zeit": "14:30", "titel": "Call Quant"}], r["termine"]
    assert r["text"].startswith("Erster Absatz."), "Frontmatter nicht abgeschnitten"
    assert "kein Termin" not in str(r["termine"]), "Liste aus fremdem Abschnitt uebernommen"


def test_parse_briefing_ohne_termine():
    # tolerant: fehlt der Abschnitt, bleibt die Liste leer und der Text kommt trotzdem durch
    r = ds._parse_briefing("Nur Fliesstext.\n")
    assert r["termine"] == []
    assert r["text"] == "Nur Fliesstext."


def test_briefing_fehlend_meldet_statt_zu_werfen():
    # Kernfall aus der Spec: Cowork lief nicht -> error, keine Exception, kein alter Wert
    echt = ds.BRIEFINGS
    ds.BRIEFINGS = ds.VAULT / "_gibt_es_nicht"
    try:
        r = ds.sicher(ds.briefing)
    finally:
        ds.BRIEFINGS = echt
    assert r["error"] is None, "fehlendes Briefing ist kein Serverfehler"
    assert r["data"]["fehlt"] is True
    assert r["data"]["hinweis"], "kein Hinweistext fuer den Nutzer"


def test_status_md_ist_kein_briefing():
    # briefings/status.md ist die Lernpfad-Statusseite (CLAUDE.md), kein Briefing
    assert ds._ist_briefing(ds.VAULT / "briefings" / "status.md") is False
    assert ds._ist_briefing(ds.VAULT / "briefings" / "2026-08-25-morgen.md") is True


def test_briefing_altes_wird_als_alt_erkannt():
    # Spec-Kernfall: ein Briefing von gestern darf nicht aussehen wie das von heute.
    import os
    from datetime import datetime, timedelta
    echt = ds.BRIEFINGS
    ds.BRIEFINGS = ds.VAULT / "_test_briefings"
    ds.BRIEFINGS.mkdir(exist_ok=True)
    gestern = (datetime.now(ds.NY).date() - timedelta(days=1)).isoformat()
    p = ds.BRIEFINGS / f"{gestern}-morgen.md"
    p.write_text("Altes Briefing.\n", encoding="utf-8")
    alt = time.time() - 30 * 3600
    os.utime(p, (alt, alt))
    try:
        r = ds.sicher(ds.briefing)
        assert r["error"] is None
        assert r["data"]["fehlt"] is True, "Briefing von gestern als heutiges ausgegeben"
        assert gestern in r["data"]["hinweis"], r["data"]["hinweis"]
        assert r["age_s"] > 24 * 3600, r["age_s"]
    finally:
        ds.BRIEFINGS = echt
        p.unlink(missing_ok=True)
        (ds.VAULT / "_test_briefings").rmdir()


def test_neueste_bias():
    r = ds._neueste_bias()
    # Im Vault liegen Bias-Dateien; ist der Ordner leer, ist None korrekt.
    assert r is None or {"datei", "bias", "datum"} <= set(r), r


def test_markt_laden_synchron():
    aufrufe = []

    def fake_run(*a, **k):
        aufrufe.append(1)
        class P:
            returncode = 0
            stdout = '{"day": "2026-08-25", "weekday": "Tuesday", "news": {"events": []}}'
            stderr = ""
        return P()

    echt_run, echt_cache = ds.subprocess.run, dict(ds._markt_cache)
    ds.subprocess.run = fake_run
    ds._markt_cache.update(data=None, wall=0.0, versuch=0.0, error_str=None)
    try:
        ds._markt_laden()
        assert len(aufrufe) == 1, f"bias_levels.py {len(aufrufe)}x aufgerufen statt 1x"
        assert ds._markt_cache["data"]["day"] == "2026-08-25"
        assert ds._markt_cache["error_str"] is None
    finally:
        ds.subprocess.run = echt_run
        ds._markt_cache.update(echt_cache)


def test_markt_laden_fehler_vermerken():
    def fake_run(*a, **k):
        raise ds.subprocess.TimeoutExpired(cmd="bias_levels.py", timeout=120)

    echt_run, echt_cache = ds.subprocess.run, dict(ds._markt_cache)
    ds.subprocess.run = fake_run
    ds._markt_cache.update(data=None, wall=0.0, versuch=0.0, error_str=None)
    try:
        ds._markt_laden()
        assert ds._markt_cache["data"] is None
        assert ds._markt_cache["error_str"] is not None
        assert "TimeoutExpired" in ds._markt_cache["error_str"]
    finally:
        ds.subprocess.run = echt_run
        ds._markt_cache.update(echt_cache)


def test_markt_leer_wirft_werden_geladen():
    """Wenn Cache leer ist und Laden unterwegs ist, wirft markt() sofort Fehler."""
    echt_cache = dict(ds._markt_cache)
    ds._markt_cache.update(data=None, wall=0.0, versuch=0.0, error_str=None)
    ds._markt_laden_laeuft = True
    try:
        r = ds.sicher(ds.markt)
        assert r["data"] is None
        assert "werden geladen" in r["error"], r["error"]
        assert "eine Minute" in r["error"], "Zeitangabe fehlt"
    finally:
        ds._markt_cache.update(echt_cache)
        ds._markt_laden_laeuft = False


def test_markt_fehler_beim_refresh_verbietet_alte_daten_als_frisch():
    """Nach erfolgreicher Ladung, dann abgelaufenem Cache, dann fehlgeschlagenem Refresh
    muss der Fehler gemeldet werden — nicht die alten Daten als frisch ausgegeben."""
    aufrufe = []

    def fake_run_erfolg(*a, **k):
        aufrufe.append("erfolg")
        class P:
            returncode = 0
            stdout = '{"day": "2026-08-24", "news": {"events": []}}'
            stderr = ""
        return P()

    def fake_run_fehler(*a, **k):
        aufrufe.append("fehler")
        raise ds.subprocess.TimeoutExpired(cmd="bias_levels.py", timeout=120)

    echt_run, echt_cache = ds.subprocess.run, dict(ds._markt_cache)
    ds.subprocess.run = fake_run_erfolg
    ds._markt_cache.update(data=None, wall=0.0, versuch=0.0, error_str=None)
    try:
        # Erste Ladung: erfolg
        ds._markt_laden()
        assert ds._markt_cache["data"]["day"] == "2026-08-24"
        assert ds._markt_cache["error_str"] is None
        # Alter Cache: versuch + wall sehr alt
        ds._markt_cache["versuch"] = time.monotonic() - 1000
        ds._markt_cache["wall"] = time.time() - 1000
        # Zweiter Versuch: fehler
        ds.subprocess.run = fake_run_fehler
        ds._markt_laden()
        # Nach Fehlschlag: Error im Cache, aber alte Daten noch vorhanden
        assert ds._markt_cache["error_str"] is not None
        # markt() muss jetzt den Fehler werfen, nicht die alten Daten als frisch liefern
        r = ds.sicher(ds.markt)
        assert r["data"] is None, "alte Daten sollten nicht zuruckgegeben werden"
        assert "TimeoutExpired" in r["error"], r["error"]
        assert len(aufrufe) == 2, f"{aufrufe}x aufgerufen, erwartet 2"
    finally:
        ds.subprocess.run = echt_run
        ds._markt_cache.update(echt_cache)


def test_markt_fehler_danach_retry_nach_cache_abgelaufen():
    """Nach Fehlschlag ohne Daten und abgelaufenem Versuch-Cache:
    markt() startet neuen Ladeversuch UND wirft den alten Fehler (kein Retry-Status-Text)."""
    aufrufe = []

    def fake_run(*a, **k):
        aufrufe.append(1)
        raise ds.subprocess.TimeoutExpired(cmd="bias_levels.py", timeout=120)

    echt_run, echt_cache = ds.subprocess.run, dict(ds._markt_cache)
    ds.subprocess.run = fake_run
    ds._markt_cache.update(data=None, wall=0.0, versuch=0.0, error_str=None)
    try:
        # Erster Fehlschlag
        ds._markt_laden()
        assert len(aufrufe) == 1
        assert ds._markt_cache["error_str"] is not None
        # Versuch-Cache abgelaufen -> triggert neuen Ladeversuch
        ds._markt_cache["versuch"] = time.monotonic() - 1000
        # markt() soll einen neuen Thread starten
        start_anfrage = []
        echt_thread = ds.threading.Thread
        def fake_thread(target=None, daemon=None):
            start_anfrage.append(target)
            class FakeThread:
                def start(self):
                    pass
            return FakeThread()
        ds.threading.Thread = fake_thread
        try:
            r = ds.sicher(ds.markt)
            # Sollte neuen Thread starten
            assert len(start_anfrage) == 1, "Kein neuer Thread fuer Retry"
            # UND den alten Fehler werfen (Spec: error check kommt vor "werden geladen")
            assert "TimeoutExpired" in r["error"]
        finally:
            ds.threading.Thread = echt_thread
    finally:
        ds.subprocess.run = echt_run
        ds._markt_cache.update(echt_cache)


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"ok  {name}")
    print("alle Tests bestanden")
