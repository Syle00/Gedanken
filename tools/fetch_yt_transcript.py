"""Fetch a YouTube video's auto-caption transcript + metadata and save it as a
raw/ source file, in the format established by the first two manual ingests
(raw/trading-ict/2026/yt-<id>-transcript.md).

Usage:
    python tools/fetch_yt_transcript.py <video_id> [--out-dir raw/trading-ict/2026]

Deps: yt-dlp, youtube_transcript_api (both already installed in this venv).
No ffmpeg/whisper needed -- this only pulls YouTube's own auto-captions.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

from youtube_transcript_api import YouTubeTranscriptApi


def get_metadata(video_id: str) -> dict:
    url = f"https://www.youtube.com/watch?v={video_id}"
    out = subprocess.run(
        [sys.executable, "-m", "yt_dlp", "--skip-download", "--print",
         "%(title)s\n%(channel)s\n%(upload_date)s\n%(duration_string)s", url],
        capture_output=True, check=True,
        encoding="utf-8", errors="replace",  # yt-dlp gibt UTF-8, nicht die Windows-ANSI-Locale
    ).stdout.strip().split("\n")
    title, channel, upload_date, duration = out[0], out[1], out[2], out[3]
    date_fmt = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"
    return {"title": title, "channel": channel, "date": date_fmt, "duration": duration}


def get_transcript_text(video_id: str) -> str:
    api = YouTubeTranscriptApi()
    snippets = api.fetch(video_id)
    return " ".join(s.text.replace("\n", " ") for s in snippets)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video_id")
    ap.add_argument("--out-dir", default="raw/trading-ict/2026")
    args = ap.parse_args()

    meta = get_metadata(args.video_id)
    text = get_transcript_text(args.video_id)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"yt-{args.video_id}-transcript.md"
    out_path.write_text(
        f"# {meta['title']}\n\n"
        f"Quelle: https://www.youtube.com/watch?v={args.video_id}\n"
        f"Kanal: {meta['channel']} | Veroeffentlicht: {meta['date']} | Laenge: {meta['duration']}\n\n"
        f"## Transkript (auto-generiert)\n\n"
        f"{text}\n",
        encoding="utf-8",
    )
    print(f"OK {out_path} ({len(text)} chars)")


if __name__ == "__main__":
    main()
