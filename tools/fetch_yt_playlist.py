"""Import a whole YouTube playlist's transcripts, resumably and IP-ban-safely.

Wraps fetch_yt_transcript.py's per-video fetch (imported, not modified) with:
playlist enumeration, a JSON checkpoint for resume-after-interruption, dedup
against already-fetched transcripts, serial pacing, and a hard stop on
youtube_transcript_api's IpBlocked error.

Usage:
    python tools/fetch_yt_playlist.py <playlist-url> [--out-dir raw/<domain>]

Re-running with the same playlist URL resumes from the checkpoint -- already
"done"/"skipped_no_captions" videos are not re-fetched.
"""
import argparse
import re
import subprocess
import sys
import time
from pathlib import Path

from fetch_yt_transcript import get_metadata, get_transcript_text
from yt_playlist_checkpoint import (
    load_checkpoint, save_checkpoint, merge_playlist_entries,
    existing_transcript_ids, pending_video_ids,
)

PAUSE_SECONDS = 20
LONG_PAUSE_SECONDS = 20
LONG_PAUSE_THRESHOLD = 10

GENERIC_WORDS = {"playlist", "series", "videos", "video"}


def derive_domain(playlist_title: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", playlist_title.lower())
    words = [w for w in words if w not in GENERIC_WORDS]
    return "-".join(words) if words else "misc"


def _parse_playlist_entries(stdout: str) -> tuple[str, str, list[tuple[str, str]]]:
    playlist_id, playlist_title = None, None
    entries = []
    for line in stdout.strip().splitlines():
        pid, ptitle, vid, vtitle = line.split("\t", 3)
        playlist_id, playlist_title = pid, ptitle
        entries.append((vid, vtitle))
    return playlist_id, playlist_title, entries


def list_playlist_entries(playlist_url: str) -> tuple[str, str, list[tuple[str, str]]]:
    out = subprocess.run(
        [sys.executable, "-m", "yt_dlp", "--flat-playlist", "--print",
         "%(playlist_id)s\t%(playlist_title)s\t%(id)s\t%(title)s", playlist_url],
        capture_output=True, text=True, check=True,
    ).stdout
    return _parse_playlist_entries(out)


def fetch_one(video_id: str, out_dir: Path) -> str:
    try:
        meta = get_metadata(video_id)
        text = get_transcript_text(video_id)
    except Exception as e:
        if "IpBlocked" in type(e).__name__:
            raise
        if "Subtitles are disabled" in str(e):
            return "skipped_no_captions"
        return "failed"

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"yt-{video_id}-transcript.md"
    out_path.write_text(
        f"# {meta['title']}\n\n"
        f"Quelle: https://www.youtube.com/watch?v={video_id}\n"
        f"Kanal: {meta['channel']} | Veroeffentlicht: {meta['date']} | Laenge: {meta['duration']}\n\n"
        f"## Transkript (auto-generiert)\n\n"
        f"{text}\n",
        encoding="utf-8",
    )
    return "done"


def run(playlist_url: str, out_dir: Path | None) -> int:
    playlist_id, playlist_title, entries = list_playlist_entries(playlist_url)
    if not playlist_id or not entries:
        print("Playlist leer oder nicht erreichbar.")
        return 1
    domain = derive_domain(playlist_title) if out_dir is None else out_dir.name
    raw_dir = out_dir if out_dir is not None else Path("raw") / domain
    if out_dir is None:
        print(f"Abgeleitete Domaene: {domain} ({raw_dir})")

    checkpoint_path = raw_dir / ".yt_playlist_state" / f"{playlist_id}.json"
    checkpoint = load_checkpoint(checkpoint_path)
    checkpoint = merge_playlist_entries(checkpoint, playlist_id, playlist_title, entries)

    on_disk = existing_transcript_ids(raw_dir)
    for v in checkpoint["videos"]:
        if v["status"] == "pending" and v["id"] in on_disk:
            v["status"] = "done"
    save_checkpoint(checkpoint_path, checkpoint)

    todo = pending_video_ids(checkpoint, already_on_disk=set())
    total = len(checkpoint["videos"])
    done_count = sum(1 for v in checkpoint["videos"] if v["status"] == "done")
    skipped_count = sum(1 for v in checkpoint["videos"] if v["status"] == "skipped_no_captions")
    failed_count = sum(1 for v in checkpoint["videos"] if v["status"] == "failed")

    if not todo:
        print(f"Nichts zu tun: {done_count}/{total} bereits geholt.")
        return 0

    fetched_this_session = 0
    by_id = {v["id"]: v for v in checkpoint["videos"]}
    for i, (video_id, title) in enumerate(todo):
        try:
            status = fetch_one(video_id, raw_dir)
        except Exception as e:
            if "IpBlocked" in type(e).__name__:
                save_checkpoint(checkpoint_path, checkpoint)
                remaining = len(todo) - i
                print(f"GESTOPPT (IP-Block) bei '{title}' ({video_id}). "
                      f"{done_count}/{total} geholt, {skipped_count} ohne Untertitel uebersprungen, "
                      f"{failed_count} fehlgeschlagen, {remaining} verbleibend inkl. diesem Video. "
                      f"Erneuter Aufruf setzt hier fort.")
                return 1
            raise
        by_id[video_id]["status"] = status
        if status == "done":
            done_count += 1
        elif status == "skipped_no_captions":
            skipped_count += 1
        elif status == "failed":
            failed_count += 1
        save_checkpoint(checkpoint_path, checkpoint)
        fetched_this_session += 1

        if i < len(todo) - 1:
            pause = LONG_PAUSE_SECONDS if fetched_this_session >= LONG_PAUSE_THRESHOLD else PAUSE_SECONDS
            time.sleep(pause)

    print(f"Fertig: {done_count}/{total} geholt, {skipped_count} ohne Untertitel uebersprungen, "
          f"{failed_count} fehlgeschlagen.")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("playlist_url")
    ap.add_argument("--out-dir", default=None)
    args = ap.parse_args()
    out_dir = Path(args.out_dir) if args.out_dir else None
    sys.exit(run(args.playlist_url, out_dir))


if __name__ == "__main__":
    main()
