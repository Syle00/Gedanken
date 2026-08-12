from pathlib import Path
import tempfile

import fetch_yt_playlist as fyp


def test_derive_domain_slugifies_and_strips_generic_words():
    assert fyp.derive_domain("Clean Code Playlist") == "clean-code"
    assert fyp.derive_domain("ICT 2026 Mentorship Series") == "ict-2026-mentorship"
    assert fyp.derive_domain("  Weird!!  Chars??  ") == "weird-chars"


def test_fetch_one_writes_transcript_file():
    orig_meta, orig_text = fyp.get_metadata, fyp.get_transcript_text
    fyp.get_metadata = lambda vid: {
        "title": "Test Video", "channel": "Test Channel", "date": "2026-01-02", "duration": "10:00",
    }
    fyp.get_transcript_text = lambda vid: "hello world transcript"
    try:
        with tempfile.TemporaryDirectory() as d:
            out_dir = Path(d)
            status = fyp.fetch_one("vid123", out_dir)
            assert status == "done"
            out_file = out_dir / "yt-vid123-transcript.md"
            assert out_file.exists()
            content = out_file.read_text(encoding="utf-8")
            assert "Test Video" in content
            assert "hello world transcript" in content
            assert "Quelle: https://www.youtube.com/watch?v=vid123" in content
    finally:
        fyp.get_metadata, fyp.get_transcript_text = orig_meta, orig_text


def test_fetch_one_marks_skipped_when_subtitles_disabled():
    orig_meta, orig_text = fyp.get_metadata, fyp.get_transcript_text
    fyp.get_metadata = lambda vid: {
        "title": "T", "channel": "C", "date": "2026-01-01", "duration": "1:00",
    }
    def raise_disabled(vid):
        raise Exception("Subtitles are disabled for this video")
    fyp.get_transcript_text = raise_disabled
    try:
        with tempfile.TemporaryDirectory() as d:
            status = fyp.fetch_one("vid456", Path(d))
            assert status == "skipped_no_captions"
            assert not (Path(d) / "yt-vid456-transcript.md").exists()
    finally:
        fyp.get_metadata, fyp.get_transcript_text = orig_meta, orig_text


def test_fetch_one_reraises_ip_blocked():
    class FakeIpBlocked(Exception):
        pass
    orig_meta, orig_text = fyp.get_metadata, fyp.get_transcript_text
    fyp.get_metadata = lambda vid: {
        "title": "T", "channel": "C", "date": "2026-01-01", "duration": "1:00",
    }
    def raise_blocked(vid):
        raise FakeIpBlocked("blocked")
    fyp.get_transcript_text = raise_blocked
    try:
        with tempfile.TemporaryDirectory() as d:
            try:
                fyp.fetch_one("vid789", Path(d))
                raise AssertionError("expected FakeIpBlocked to propagate")
            except FakeIpBlocked:
                pass
    finally:
        fyp.get_metadata, fyp.get_transcript_text = orig_meta, orig_text


def test_fetch_one_returns_failed_on_unexpected_error():
    orig_meta, orig_text = fyp.get_metadata, fyp.get_transcript_text

    def raise_unexpected(vid):
        raise RuntimeError("yt-dlp exited with code 1")
    fyp.get_metadata = raise_unexpected
    fyp.get_transcript_text = orig_text
    try:
        with tempfile.TemporaryDirectory() as d:
            status = fyp.fetch_one("vid999", Path(d))
            assert status == "failed"
            assert not (Path(d) / "yt-vid999-transcript.md").exists()
    finally:
        fyp.get_metadata, fyp.get_transcript_text = orig_meta, orig_text


def test_parse_playlist_entries_handles_tab_delimiter():
    stdout = (
        "PL1\tICT | Mentorship 2026\tvid1\tVideo One\n"
        "PL1\tICT | Mentorship 2026\tvid2\tVideo | With Pipe\n"
    )
    playlist_id, playlist_title, entries = fyp._parse_playlist_entries(stdout)
    assert playlist_id == "PL1"
    assert playlist_title == "ICT | Mentorship 2026"
    assert entries == [("vid1", "Video One"), ("vid2", "Video | With Pipe")]


if __name__ == "__main__":
    test_derive_domain_slugifies_and_strips_generic_words()
    test_fetch_one_writes_transcript_file()
    test_fetch_one_marks_skipped_when_subtitles_disabled()
    test_fetch_one_reraises_ip_blocked()
    test_fetch_one_returns_failed_on_unexpected_error()
    test_parse_playlist_entries_handles_tab_delimiter()
    print("OK")
