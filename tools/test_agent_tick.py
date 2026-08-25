"""Selbstcheck fuer tools/agent_tick.py. Ausfuehren: python tools/test_agent_tick.py"""
import sys
import tempfile
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agent_tick import (
    Entry, cron_matches, last_due, parse_timeout, resolve_placeholders, scan_entries,
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


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"ok   {t.__name__}")
    print(f"\n{len(tests)} Tests bestanden.")


if __name__ == "__main__":
    main()
