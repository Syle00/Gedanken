import json
from pathlib import Path
import tempfile

from yt_playlist_checkpoint import (
    load_checkpoint, save_checkpoint, merge_playlist_entries,
    existing_transcript_ids, pending_video_ids,
)


def test_load_checkpoint_missing_file_returns_empty_shell():
    with tempfile.TemporaryDirectory() as d:
        cp = load_checkpoint(Path(d) / "nope.json")
        assert cp == {"playlist_id": None, "playlist_title": None, "videos": []}


def test_save_then_load_roundtrip():
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "sub" / "cp.json"
        data = {"playlist_id": "PL1", "playlist_title": "T", "videos": [{"id": "a", "title": "A", "status": "done"}]}
        save_checkpoint(path, data)
        assert path.exists()
        assert load_checkpoint(path) == data


def test_merge_playlist_entries_adds_new_as_pending_and_keeps_existing_status():
    checkpoint = {"playlist_id": None, "playlist_title": None,
                  "videos": [{"id": "a", "title": "A", "status": "done"}]}
    merged = merge_playlist_entries(
        checkpoint, "PL1", "My Playlist",
        [("a", "A"), ("b", "B")],
    )
    assert merged["playlist_id"] == "PL1"
    assert merged["playlist_title"] == "My Playlist"
    by_id = {v["id"]: v for v in merged["videos"]}
    assert by_id["a"]["status"] == "done"  # untouched
    assert by_id["b"]["status"] == "pending"  # newly added


def test_existing_transcript_ids_scans_recursively():
    with tempfile.TemporaryDirectory() as d:
        raw = Path(d)
        (raw / "sub").mkdir()
        (raw / "yt-abc123-transcript.md").write_text("x")
        (raw / "sub" / "yt-def456-transcript.md").write_text("x")
        (raw / "not-a-transcript.md").write_text("x")
        assert existing_transcript_ids(raw) == {"abc123", "def456"}


def test_pending_video_ids_filters_status_and_disk():
    checkpoint = {"playlist_id": "PL1", "playlist_title": "T", "videos": [
        {"id": "a", "title": "A", "status": "done"},
        {"id": "b", "title": "B", "status": "pending"},
        {"id": "c", "title": "C", "status": "pending"},
        {"id": "d", "title": "D", "status": "skipped_no_captions"},
    ]}
    result = pending_video_ids(checkpoint, already_on_disk={"c"})
    assert result == [("b", "B")]


if __name__ == "__main__":
    test_load_checkpoint_missing_file_returns_empty_shell()
    test_save_then_load_roundtrip()
    test_merge_playlist_entries_adds_new_as_pending_and_keeps_existing_status()
    test_existing_transcript_ids_scans_recursively()
    test_pending_video_ids_filters_status_and_disk()
    print("OK")
