"""Selbstcheck fuer tools/agent_tick.py. Ausfuehren: python tools/test_agent_tick.py"""
import sys
import tempfile
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agent_tick import (
    Entry, append_run, cron_matches, expect_ok, faellige, last_due, last_run,
    parse_timeout, resolve_placeholders, run_entry, scan_entries, write_status,
)


def test_cron_matches():
    # "0 20 * * 0-4" = 20:00 an Sonntag(0) bis Donnerstag(4)
    assert cron_matches("0 20 * * 0-4", datetime(2026, 8, 24, 20, 0))    # Montag
    assert not cron_matches("0 20 * * 0-4", datetime(2026, 8, 24, 20, 1))
    assert not cron_matches("0 20 * * 0-4", datetime(2026, 8, 24, 19, 0))
    assert not cron_matches("0 20 * * 0-4", datetime(2026, 8, 28, 20, 0))  # Freitag
    assert cron_matches("0 20 * * 5", datetime(2026, 8, 28, 20, 0))        # Freitag
    assert cron_matches("*/10 * * * *", datetime(2026, 8, 24, 13, 30))
    assert not cron_matches("*/10 * * * *", datetime(2026, 8, 24, 13, 31))
    assert cron_matches("30 6 * * *", datetime(2026, 8, 24, 6, 30))
    assert cron_matches("0 23 * * 1-5", datetime(2026, 8, 28, 23, 0))      # Freitag
    assert not cron_matches("0 23 * * 1-5", datetime(2026, 8, 29, 23, 0))  # Samstag
    # Sonntag ist sowohl 0 als auch 7
    assert cron_matches("0 20 * * 0", datetime(2026, 8, 23, 20, 0))
    assert cron_matches("0 20 * * 7", datetime(2026, 8, 23, 20, 0))
    # Liste
    assert cron_matches("0 8,20 * * *", datetime(2026, 8, 24, 8, 0))
    assert cron_matches("0 8,20 * * *", datetime(2026, 8, 24, 20, 0))
    assert not cron_matches("0 8,20 * * *", datetime(2026, 8, 24, 12, 0))


def test_last_due():
    # Montag 21:15 -> letzte Faelligkeit von "0 20 * * 0-4" war Montag 20:00
    assert last_due("0 20 * * 0-4", datetime(2026, 8, 24, 21, 15)) == datetime(2026, 8, 24, 20, 0)
    # Montag 19:00 -> letzte war Sonntag 20:00
    assert last_due("0 20 * * 0-4", datetime(2026, 8, 24, 19, 0)) == datetime(2026, 8, 23, 20, 0)
    # exakt auf der Minute zaehlt als faellig
    assert last_due("0 20 * * 0-4", datetime(2026, 8, 24, 20, 0)) == datetime(2026, 8, 24, 20, 0)
    # ausserhalb des Rueckblickfensters -> None
    assert last_due("0 20 * * 5", datetime(2026, 8, 25, 12, 0), lookback_h=6) is None


def test_resolve_placeholders():
    # Montag 2026-08-24 -> naechster Handelstag ist Dienstag
    got = resolve_placeholders("raw/journal/Daily Bias {next_trading_day}.md", date(2026, 8, 24))
    assert got == "raw/journal/Daily Bias 2026-08-25.md", got
    assert resolve_placeholders("{today}", date(2026, 8, 24)) == "2026-08-24"
    assert resolve_placeholders("{yesterday}", date(2026, 8, 24)) == "2026-08-23"
    # Freitag 2026-08-28 -> naechster Montag ist 2026-08-31, KW 36
    got = resolve_placeholders("Weekly Bias KW{next_kw} {next_year}.md", date(2026, 8, 28))
    assert got == "Weekly Bias KW36 2026.md", got
    # unbekannte Klammern bleiben unangetastet
    assert resolve_placeholders("{unbekannt}", date(2026, 8, 24)) == "{unbekannt}"


def test_parse_timeout():
    assert parse_timeout("15m") == 900
    assert parse_timeout("60m") == 3600
    assert parse_timeout("2h") == 7200
    assert parse_timeout("90s") == 90
    assert parse_timeout(None) == 1800  # Default 30m


def test_scan_entries():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        cmds = root / ".claude" / "commands"
        cmds.mkdir(parents=True)
        (cmds / "geplant.md").write_text(
            "---\ndescription: mit Plan\nschedule: \"0 20 * * 0-4\"\n"
            "expect: \"out/{today}.md\"\ntimeout: 15m\n---\nText\n",
            encoding="utf-8",
        )
        (cmds / "ungeplant.md").write_text(
            "---\ndescription: ohne Plan\n---\nText\n", encoding="utf-8"
        )
        (cmds / "extern.md").write_text(
            "---\ndescription: extern\nschedule: \"0 7 * * *\"\nextern: true\n"
            "expect: \"out/b-{today}.md\"\n---\nText\n",
            encoding="utf-8",
        )
        skill = root / ".claude" / "skills" / "meiner"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            "---\nname: meiner\nschedule: \"0 9 * * 1\"\n---\nText\n", encoding="utf-8"
        )

        entries = {e.name: e for e in scan_entries(root)}
        # ohne schedule wird ignoriert
        assert "ungeplant" not in entries
        assert set(entries) == {"geplant", "extern", "meiner"}, sorted(entries)
        assert entries["geplant"].timeout_s == 900
        assert entries["geplant"].extern is False
        assert entries["extern"].extern is True
        # Default-Timeout, wenn keiner angegeben ist
        assert entries["extern"].timeout_s == 1800
        assert entries["meiner"].schedule == "0 9 * * 1"


def test_expect_ok_existenz():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "out").mkdir()
        gestartet = datetime(2026, 8, 24, 20, 0)
        ok, notiz = expect_ok("out/{today}.md", root, gestartet, date(2026, 8, 24))
        assert ok is False, notiz
        assert "2026-08-24" in notiz, notiz  # aufgeloester Pfad steht in der Notiz

        (root / "out" / "2026-08-24.md").write_text("da", encoding="utf-8")
        ok, notiz = expect_ok("out/{today}.md", root, gestartet, date(2026, 8, 24))
        assert ok is True, notiz


def test_expect_ok_changed():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        ziel = root / "daten.csv"
        ziel.write_text("alt", encoding="utf-8")
        import os
        # mtime kuenstlich in die Vergangenheit setzen
        alt = datetime(2026, 8, 24, 10, 0).timestamp()
        os.utime(ziel, (alt, alt))

        gestartet = datetime(2026, 8, 24, 20, 0)
        ok, notiz = expect_ok("changed: daten.csv", root, gestartet, date(2026, 8, 24))
        assert ok is False, notiz
        assert "unveraendert" in notiz.lower() or "unverändert" in notiz.lower(), notiz

        neu = datetime(2026, 8, 24, 20, 5).timestamp()
        os.utime(ziel, (neu, neu))
        ok, notiz = expect_ok("changed: daten.csv", root, gestartet, date(2026, 8, 24))
        assert ok is True, notiz

        # fehlende Datei ist rot, kein Absturz
        ok, notiz = expect_ok("changed: gibtsnicht.csv", root, gestartet, date(2026, 8, 24))
        assert ok is False, notiz


def test_expect_ok_ohne_angabe():
    with tempfile.TemporaryDirectory() as td:
        ok, notiz = expect_ok(None, Path(td), datetime(2026, 8, 24, 20, 0), date(2026, 8, 24))
        assert ok is True, notiz


def test_register_lesen_schreiben():
    with tempfile.TemporaryDirectory() as td:
        reg = Path(td) / "agent-runs.csv"
        assert last_run(reg, "irgendwas") is None  # Datei existiert noch nicht

        append_run(reg, {
            "zeit_start": "2026-08-24T20:00", "command": "bias-vorlage-daily",
            "ausloeser": "plan", "dauer_s": "86", "exit": "0",
            "expect_ok": "1", "status": "gruen", "notiz": "",
        })
        append_run(reg, {
            "zeit_start": "2026-08-25T20:00", "command": "bias-vorlage-daily",
            "ausloeser": "plan", "dauer_s": "91", "exit": "0",
            "expect_ok": "1", "status": "gruen", "notiz": "",
        })
        append_run(reg, {
            "zeit_start": "2026-08-25T23:00", "command": "daten-1s",
            "ausloeser": "plan", "dauer_s": "912", "exit": "0",
            "expect_ok": "0", "status": "rot", "notiz": "expect verfehlt, Komma, Zeichen",
        })
        # juengster Lauf gewinnt
        assert last_run(reg, "bias-vorlage-daily") == datetime(2026, 8, 25, 20, 0)
        assert last_run(reg, "daten-1s") == datetime(2026, 8, 25, 23, 0)
        assert last_run(reg, "unbekannt") is None
        # Kopfzeile genau einmal
        assert reg.read_text(encoding="utf-8").count("zeit_start") == 1
        # Komma in der Notiz zerlegt die Zeile nicht
        assert last_run(reg, "daten-1s") is not None


def test_faellige():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        reg = root / "agent-runs.csv"
        e = Entry("bias", "0 20 * * 0-4", None, 900, False, root / "bias.md")
        ex = Entry("brief", "0 7 * * *", "out/x.md", 3600, True, root / "brief.md")

        # Montag 20:05, noch nie gelaufen -> faellig als "plan"
        got = faellige([e], datetime(2026, 8, 24, 20, 5), reg)
        assert [(x.name, a) for x, a in got] == [("bias", "plan")], got

        # nach dem Lauf nicht mehr faellig
        append_run(reg, {
            "zeit_start": "2026-08-24T20:05", "command": "bias", "ausloeser": "plan",
            "dauer_s": "10", "exit": "0", "expect_ok": "1", "status": "gruen", "notiz": "",
        })
        assert faellige([e], datetime(2026, 8, 24, 20, 15), reg) == []

        # Dienstag 20:05: neue Faelligkeit nach dem letzten Lauf -> wieder dran
        got = faellige([e], datetime(2026, 8, 25, 20, 5), reg)
        assert [(x.name, a) for x, a in got] == [("bias", "plan")], got

        # deutlich verspaetet (Rechner war aus) -> "nachhol"
        got = faellige([e], datetime(2026, 8, 25, 23, 30), reg)
        assert [(x.name, a) for x, a in got] == [("bias", "nachhol")], got

        # extern wird nie gestartet, aber als "extern" gemeldet
        got = faellige([ex], datetime(2026, 8, 25, 8, 0), reg)
        assert [(x.name, a) for x, a in got] == [("brief", "extern")], got

        # vor der ersten Faelligkeit des Tages: nichts zu tun
        assert faellige([ex], datetime(2026, 8, 25, 6, 0), reg) == []


def test_faellige_nachhol_fenster():
    # Ruling 1: eine Faelligkeit aelter als NACHHOL_FENSTER (18h) wird nicht
    # mehr nachgeholt; eine juengere schon.
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        reg = root / "agent-runs.csv"
        e = Entry("bias", "0 20 * * 0-4", None, 900, False, root / "bias.md")

        # Montag 20:00 faellig, Dienstag 15:00 = 19h spaeter -> zu alt, kein Nachholen
        assert faellige([e], datetime(2026, 8, 25, 15, 0), reg) == []

        # Montag 20:00 faellig, Dienstag 13:00 = 17h spaeter -> noch im Fenster
        got = faellige([e], datetime(2026, 8, 25, 13, 0), reg)
        assert [(x.name, a) for x, a in got] == [("bias", "nachhol")], got


def test_faellige_extern_kulanz():
    # Ruling 3: extern-Eintraege bekommen ihr timeout_s als Kulanzfenster --
    # erst danach gilt der Lauf als ausgeblieben und wird gemeldet.
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        reg = root / "agent-runs.csv"
        ex = Entry("brief", "0 7 * * *", "out/x.md", 3600, True, root / "brief.md")

        # 07:30, 30 Min nach Faelligkeit, Kulanz (60 Min) noch nicht um
        assert faellige([ex], datetime(2026, 8, 25, 7, 30), reg) == []

        # 08:00, 60 Min nach Faelligkeit, Kulanz um -> gemeldet
        got = faellige([ex], datetime(2026, 8, 25, 8, 0), reg)
        assert [(x.name, a) for x, a in got] == [("brief", "extern")], got


def test_dry_run_changed_nutzt_tagesbeginn():
    # Ruling 2: der Dry-Run-Zweig von cli() soll fuer 'changed:' den heutigen
    # Tagesbeginn als Startzeitpunkt uebergeben, nicht den aktuellen Moment --
    # sonst ist eine Datei, die heute frueh entstand, im Trockenlauf
    # faelschlich rot. Klemmt cli() tatsaechlich ein (kein direkter
    # expect_ok-Aufruf), sonst haette ein Rueckbau auf `now` keinen Effekt.
    import agent_tick
    import io
    import os
    from contextlib import redirect_stdout

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        cmds = root / ".claude" / "commands"
        cmds.mkdir(parents=True)
        (cmds / "geplant.md").write_text(
            "---\ndescription: mit Plan\nschedule: \"0 20 * * 0-4\"\n"
            "expect: \"changed: daten.csv\"\n---\nText\n",
            encoding="utf-8",
        )
        ziel = root / "daten.csv"
        ziel.write_text("neu", encoding="utf-8")
        heute_frueh = datetime.combine(date.today(), datetime.min.time()).replace(minute=30)
        os.utime(ziel, (heute_frueh.timestamp(), heute_frueh.timestamp()))

        alt_root = agent_tick.ROOT
        agent_tick.ROOT = root
        try:
            buf = io.StringIO()
            with redirect_stdout(buf):
                agent_tick.cli(["--dry-run"])
        finally:
            agent_tick.ROOT = alt_root

        ausgabe = buf.getvalue()
        assert "ROT" not in ausgabe, ausgabe
        assert "expect=ok" in ausgabe, ausgabe


def test_run_entry_gruen():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "out").mkdir()
        e = Entry("demo", "0 20 * * *", "out/{today}.md", 900, False, root / "demo.md")

        def starter(cmd, timeout_s):
            (root / "out" / "2026-08-24.md").write_text("erzeugt", encoding="utf-8")
            return 0, "fertig"

        zeile = run_entry(e, "plan", root, datetime(2026, 8, 24, 20, 0), starter=starter)
        assert zeile["status"] == "gruen", zeile
        assert zeile["exit"] == "0"
        assert zeile["expect_ok"] == "1"
        assert zeile["command"] == "demo"
        assert zeile["ausloeser"] == "plan"


def test_run_entry_expect_verfehlt():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        e = Entry("demo", "0 20 * * *", "out/{today}.md", 900, False, root / "demo.md")
        # Lauf meldet Erfolg, erzeugt aber nichts -- genau der Fall, den expect faengt
        zeile = run_entry(e, "plan", root, datetime(2026, 8, 24, 20, 0),
                          starter=lambda cmd, t: (0, "angeblich fertig"))
        assert zeile["status"] == "rot", zeile
        assert zeile["exit"] == "0"
        assert zeile["expect_ok"] == "0"
        assert "expect verfehlt" in zeile["notiz"], zeile


def test_run_entry_wiederholt_bei_fehler():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        e = Entry("demo", "0 20 * * *", None, 900, False, root / "demo.md")
        versuche = []

        def starter(cmd, timeout_s):
            versuche.append(cmd)
            return (1, "peng") if len(versuche) < 3 else (0, "endlich")

        zeile = run_entry(e, "plan", root, datetime(2026, 8, 24, 20, 0), starter=starter)
        assert len(versuche) == 3, versuche          # Erstversuch + 2 Wiederholungen
        assert zeile["status"] == "gruen", zeile


def test_run_entry_gibt_nach_zwei_wiederholungen_auf():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        e = Entry("demo", "0 20 * * *", None, 900, False, root / "demo.md")
        versuche = []

        def starter(cmd, timeout_s):
            versuche.append(cmd)
            return 1, "peng"

        zeile = run_entry(e, "plan", root, datetime(2026, 8, 24, 20, 0), starter=starter)
        assert len(versuche) == 3, versuche
        assert zeile["status"] == "rot", zeile
        assert zeile["exit"] == "1"


def test_run_entry_timeout():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        e = Entry("demo", "0 20 * * *", None, 900, False, root / "demo.md")
        # 124 ist der Code, den _subprocess_starter bei TimeoutExpired liefert
        zeile = run_entry(e, "plan", root, datetime(2026, 8, 24, 20, 0),
                          starter=lambda cmd, t: (124, ""))
        assert zeile["status"] == "rot", zeile
        assert zeile["exit"] == "124"
        assert "Timeout" in zeile["notiz"], zeile
        assert "900" in zeile["notiz"], zeile


def test_run_entry_extern_startet_nichts():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        e = Entry("brief", "0 7 * * *", "out/b.md", 3600, True, root / "brief.md")
        versuche = []

        def starter(cmd, timeout_s):
            versuche.append(cmd)
            return 0, ""

        zeile = run_entry(e, "extern", root, datetime(2026, 8, 24, 8, 0), starter=starter)
        assert versuche == [], "externer Eintrag darf nie gestartet werden"
        assert zeile["status"] == "rot", zeile
        assert zeile["dauer_s"] == ""
        assert "ausgeblieben" in zeile["notiz"], zeile


def test_write_status():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "algo" / "live").mkdir(parents=True)
        e = Entry("demo", "0 20 * * *", "out/fehlt.md", 900, False, root / "demo.md")
        text = write_status(root, [e], datetime(2026, 8, 24, 21, 0))
        ziel = root / "algo" / "live" / "agent-status.md"
        assert ziel.exists()
        assert "demo" in text
        assert "2026-08-24" in text


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"ok   {t.__name__}")
    print(f"\n{len(tests)} Tests bestanden.")


if __name__ == "__main__":
    main()
