# tools/test_fetch_yt_playlist_integration.py
from pathlib import Path
import tempfile

import fetch_yt_playlist as fyp
from yt_playlist_checkpoint import load_checkpoint, save_checkpoint


class FakeIpBlocked(Exception):
    pass


def _fake_entries():
    return ("PLtest", "My Test Playlist", [("a", "Video A"), ("b", "Video B"), ("c", "Video C")])


def test_run_skips_already_done_and_fetches_rest():
    orig_list, orig_meta, orig_text, orig_sleep = (
        fyp.list_playlist_entries, fyp.get_metadata, fyp.get_transcript_text, fyp.time.sleep,
    )
    fyp.list_playlist_entries = lambda url: _fake_entries()
    fyp.get_metadata = lambda vid: {
        "title": f"Title {vid}", "channel": "C", "date": "2026-01-01", "duration": "1:00",
    }
    fyp.get_transcript_text = lambda vid: f"transcript {vid}"
    fyp.time.sleep = lambda s: None
    try:
        with tempfile.TemporaryDirectory() as d:
            out_dir = Path(d) / "raw" / "testdomain"
            checkpoint_path = out_dir / ".yt_playlist_state" / "PLtest.json"
            save_checkpoint(checkpoint_path, {
                "playlist_id": "PLtest", "playlist_title": "My Test Playlist",
                "videos": [{"id": "a", "title": "Video A", "status": "done"}],
            })

            exit_code = fyp.run("http://fake-url", out_dir)

            assert exit_code == 0
            assert not (out_dir / "yt-a-transcript.md").exists()  # already done, not re-fetched
            assert (out_dir / "yt-b-transcript.md").exists()
            assert (out_dir / "yt-c-transcript.md").exists()

            final = load_checkpoint(checkpoint_path)
            statuses = {v["id"]: v["status"] for v in final["videos"]}
            assert statuses == {"a": "done", "b": "done", "c": "done"}
    finally:
        fyp.list_playlist_entries, fyp.get_metadata, fyp.get_transcript_text, fyp.time.sleep = (
            orig_list, orig_meta, orig_text, orig_sleep,
        )


def test_run_stops_on_ip_block_and_resumes_on_second_call():
    orig_list, orig_meta, orig_text, orig_sleep = (
        fyp.list_playlist_entries, fyp.get_metadata, fyp.get_transcript_text, fyp.time.sleep,
    )
    fyp.list_playlist_entries = lambda url: _fake_entries()
    fyp.get_metadata = lambda vid: {
        "title": f"Title {vid}", "channel": "C", "date": "2026-01-01", "duration": "1:00",
    }
    fyp.time.sleep = lambda s: None
    try:
        with tempfile.TemporaryDirectory() as d:
            out_dir = Path(d) / "raw" / "testdomain"

            def transcript_blocks_on_b(vid):
                if vid == "b":
                    raise FakeIpBlocked("blocked")
                return f"transcript {vid}"
            fyp.get_transcript_text = transcript_blocks_on_b

            exit_code = fyp.run("http://fake-url", out_dir)
            assert exit_code == 1

            checkpoint_path = out_dir / ".yt_playlist_state" / "PLtest.json"
            mid = load_checkpoint(checkpoint_path)
            statuses = {v["id"]: v["status"] for v in mid["videos"]}
            assert statuses["a"] == "done"
            assert statuses["b"] == "pending"  # not marked failed -- eligible for resume
            assert statuses["c"] == "pending"  # never attempted

            fyp.get_transcript_text = lambda vid: f"transcript {vid}"
            exit_code_2 = fyp.run("http://fake-url", out_dir)
            assert exit_code_2 == 0

            final = load_checkpoint(checkpoint_path)
            statuses = {v["id"]: v["status"] for v in final["videos"]}
            assert statuses == {"a": "done", "b": "done", "c": "done"}
    finally:
        fyp.list_playlist_entries, fyp.get_metadata, fyp.get_transcript_text, fyp.time.sleep = (
            orig_list, orig_meta, orig_text, orig_sleep,
        )


if __name__ == "__main__":
    test_run_skips_already_done_and_fetches_rest()
    test_run_stops_on_ip_block_and_resumes_on_second_call()
    print("OK")
