"""Checkpoint read/write and dedup helpers for large-playlist YouTube ingest.

Pure functions, no network I/O -- keeps fetch_yt_playlist.py's orchestration
logic testable without hitting yt-dlp/YouTube.
"""
import json
import re
from pathlib import Path

TRANSCRIPT_ID_RE = re.compile(r"^yt-(.+)-transcript\.md$")


def load_checkpoint(path: Path) -> dict:
    if not path.exists():
        return {"playlist_id": None, "playlist_title": None, "videos": []}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"playlist_id": None, "playlist_title": None, "videos": []}


def save_checkpoint(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def merge_playlist_entries(checkpoint: dict, playlist_id: str, playlist_title: str,
                            entries: list[tuple[str, str]]) -> dict:
    checkpoint["playlist_id"] = playlist_id
    checkpoint["playlist_title"] = playlist_title
    known_ids = {v["id"] for v in checkpoint["videos"]}
    for video_id, title in entries:
        if video_id not in known_ids:
            checkpoint["videos"].append({"id": video_id, "title": title, "status": "pending"})
            known_ids.add(video_id)
    return checkpoint


def existing_transcript_ids(raw_dir: Path) -> set[str]:
    if not raw_dir.exists():
        return set()
    ids = set()
    for f in raw_dir.rglob("yt-*-transcript.md"):
        m = TRANSCRIPT_ID_RE.match(f.name)
        if m:
            ids.add(m.group(1))
    return ids


def pending_video_ids(checkpoint: dict, already_on_disk: set[str]) -> list[tuple[str, str]]:
    return [
        (v["id"], v["title"]) for v in checkpoint["videos"]
        if v["status"] == "pending" and v["id"] not in already_on_disk
    ]
