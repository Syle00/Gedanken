# yt-playlist-ingest Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a checkpoint-based, IP-ban-safe tool + skill that imports large, arbitrary-domain
YouTube playlists into `raw/<domain>/` and hands off to the standard wiki ingest workflow.

**Architecture:** New `tools/fetch_yt_playlist.py` imports `get_metadata()`/`get_transcript_text()`
from the existing `tools/fetch_yt_transcript.py` (unchanged) and adds playlist enumeration,
JSON-checkpoint tracking, dedup, serial pacing, and hard-stop-on-`IpBlocked` behavior. A new
`.claude/skills/yt-playlist-ingest/SKILL.md` orchestrates: run the fetch tool, then apply the
general CLAUDE.md ingest workflow to whatever transcripts landed, then one `push.ps1` per session.

**Tech Stack:** Python (stdlib `json`, `argparse`, `subprocess`, `time`, `pathlib`), `yt-dlp`,
`youtube_transcript_api` — all already installed and used by `fetch_yt_transcript.py`.

## Global Constraints

- Do not modify `tools/fetch_yt_transcript.py` — `yt-ict-ingest` depends on it; import from it only.
- Checkpoint files live at `raw/<domain>/.yt_playlist_state/<playlist_id>.json` and must be
  gitignored (transient operational state, per CLAUDE.md Versionskontrolle conventions).
- Serial fetches only, 45s pause between videos, 90s once 10+ videos fetched in the running
  session — no parallelism, no proxy/IP-rotation (out of scope per spec).
- On `youtube_transcript_api._errors.IpBlocked`: stop immediately, leave the in-flight video's
  checkpoint status as `pending` (not `failed`), exit with a non-zero code and a clear message.
- On "Subtitles are disabled": mark `skipped_no_captions`, keep going — no ffmpeg/Whisper fallback.
- Video IDs/playlist IDs starting with `-` must be passable via a `--` separator.
- Output transcript file format must match `fetch_yt_transcript.py`'s existing format exactly
  (same header/metadata lines), so downstream ingest tooling and manual review work unchanged.

---

### Task 1: Checkpoint read/write + dedup logic (pure functions, no network)

**Files:**
- Create: `tools/yt_playlist_checkpoint.py`
- Test: `tools/test_yt_playlist_checkpoint.py`

**Interfaces:**
- Produces:
  - `load_checkpoint(path: Path) -> dict` — returns `{"playlist_id": str, "playlist_title": str, "videos": [{"id": str, "title": str, "status": str}, ...]}`; returns a fresh empty-shell dict (`{"playlist_id": None, "playlist_title": None, "videos": []}`) if the file doesn't exist.
  - `save_checkpoint(path: Path, data: dict) -> None` — writes pretty JSON (`indent=2`), creates parent dirs.
  - `merge_playlist_entries(checkpoint: dict, playlist_id: str, playlist_title: str, entries: list[tuple[str, str]]) -> dict` — `entries` is `[(video_id, title), ...]` from a fresh playlist enumeration. Sets `playlist_id`/`playlist_title`. For each entry: if `video_id` already present in `checkpoint["videos"]`, leave its status untouched; if new, append with `status: "pending"`. Returns the updated checkpoint (mutates and returns the same dict).
  - `existing_transcript_ids(raw_dir: Path) -> set[str]` — scans `raw_dir` recursively for files matching `yt-*-transcript.md`, extracts the id between `yt-` and `-transcript.md`, returns as a set. Used for dedup against transcripts fetched outside this tool (e.g. via `yt-ict-ingest`).
  - `pending_video_ids(checkpoint: dict, already_on_disk: set[str]) -> list[tuple[str, str]]` — returns `[(id, title), ...]` for videos whose status is `"pending"` **and** whose id is not in `already_on_disk`. If an id is in `already_on_disk` but checkpoint status is `"pending"`, this function does NOT mutate the checkpoint (the caller marks it `done` after confirming, see Task 2) — it only filters the returned worklist.

- [ ] **Step 1: Write the failing tests**

```python
# tools/test_yt_playlist_checkpoint.py
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tools/test_yt_playlist_checkpoint.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'yt_playlist_checkpoint'`

- [ ] **Step 3: Write the implementation**

```python
# tools/yt_playlist_checkpoint.py
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
    return json.loads(path.read_text(encoding="utf-8"))


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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tools/test_yt_playlist_checkpoint.py -v`
Expected: PASS (5 tests)

- [ ] **Step 5: Commit**

```bash
git add tools/yt_playlist_checkpoint.py tools/test_yt_playlist_checkpoint.py
git commit -m "$(cat <<'EOF'
add checkpoint/dedup helpers for playlist ingest

Pure, network-free functions so the playlist orchestrator (next task) can be
tested without hitting yt-dlp/YouTube.
EOF
)"
```

---

### Task 2: Playlist orchestrator script (`fetch_yt_playlist.py`)

**Files:**
- Create: `tools/fetch_yt_playlist.py`
- Test: `tools/test_fetch_yt_playlist.py`

**Interfaces:**
- Consumes (from Task 1, `tools/yt_playlist_checkpoint.py`):
  `load_checkpoint`, `save_checkpoint`, `merge_playlist_entries`, `existing_transcript_ids`, `pending_video_ids`
- Consumes (from existing `tools/fetch_yt_transcript.py`, unmodified):
  `get_metadata(video_id: str) -> dict` (keys: `title`, `channel`, `date`, `duration`),
  `get_transcript_text(video_id: str) -> str`
- Produces:
  - `derive_domain(playlist_title: str) -> str` — lowercases, strips non-alphanumeric to `-`,
    collapses repeats, trims to a short slug (e.g. `"Clean Code Playlist"` → `"clean-code"`; strip
    trailing generic words `playlist`/`series`/`videos` before slugging).
  - `list_playlist_entries(playlist_url: str) -> tuple[str, str, list[tuple[str, str]]]` — runs
    `yt-dlp --flat-playlist --print "%(playlist_id)s | %(playlist_title)s | %(id)s | %(title)s"`
    once, parses stdout, returns `(playlist_id, playlist_title, [(video_id, title), ...])`.
  - `fetch_one(video_id: str, out_dir: Path) -> str` — returns one of
    `"done" | "skipped_no_captions"`; raises the underlying `IpBlocked` exception unhandled (caller
    decides the stop behavior). Writes `out_dir/yt-<id>-transcript.md` in the same format as
    `fetch_yt_transcript.py`'s `main()` (title header, `Quelle:`/`Kanal:` line, transcript body).
  - `run(playlist_url: str, out_dir: Path | None) -> int` — the CLI entry point's logic, returns a
    process exit code (0 = finished or nothing pending, 1 = stopped early on `IpBlocked`). Handles
    domain derivation when `out_dir` is `None`, checkpoint load/merge/save, dedup, the serial
    fetch loop with pacing, and prints the end-of-run summary line.
  - CLI: `python tools/fetch_yt_playlist.py <playlist-url> [--out-dir raw/<domain>]`, argparse with
    `--` separator support inherited automatically from argparse for the positional URL (URLs don't
    start with `-`, but playlist IDs might be logged standalone — no special handling needed here
    since the tool takes a full URL, not a bare ID).

**Note on testability:** `fetch_one` calls network functions (`get_metadata`, `get_transcript_text`)
directly by name at module level, so tests monkeypatch `tools.fetch_yt_playlist.get_metadata` /
`tools.fetch_yt_playlist.get_transcript_text` rather than mocking subprocess/HTTP.

- [ ] **Step 1: Write the failing tests**

```python
# tools/test_fetch_yt_playlist.py
from pathlib import Path
import tempfile
import pytest

import fetch_yt_playlist as fyp


def test_derive_domain_slugifies_and_strips_generic_words():
    assert fyp.derive_domain("Clean Code Playlist") == "clean-code"
    assert fyp.derive_domain("ICT 2026 Mentorship Series") == "ict-2026-mentorship"
    assert fyp.derive_domain("  Weird!!  Chars??  ") == "weird-chars"


def test_fetch_one_writes_transcript_file(monkeypatch):
    monkeypatch.setattr(fyp, "get_metadata", lambda vid: {
        "title": "Test Video", "channel": "Test Channel", "date": "2026-01-02", "duration": "10:00",
    })
    monkeypatch.setattr(fyp, "get_transcript_text", lambda vid: "hello world transcript")

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


def test_fetch_one_marks_skipped_when_subtitles_disabled(monkeypatch):
    def raise_disabled(vid):
        raise Exception("Subtitles are disabled for this video")
    monkeypatch.setattr(fyp, "get_metadata", lambda vid: {
        "title": "T", "channel": "C", "date": "2026-01-01", "duration": "1:00",
    })
    monkeypatch.setattr(fyp, "get_transcript_text", raise_disabled)

    with tempfile.TemporaryDirectory() as d:
        status = fyp.fetch_one("vid456", Path(d))
        assert status == "skipped_no_captions"
        assert not (Path(d) / "yt-vid456-transcript.md").exists()


def test_fetch_one_reraises_ip_blocked(monkeypatch):
    class FakeIpBlocked(Exception):
        pass
    monkeypatch.setattr(fyp, "get_metadata", lambda vid: {
        "title": "T", "channel": "C", "date": "2026-01-01", "duration": "1:00",
    })
    def raise_blocked(vid):
        raise FakeIpBlocked("blocked")
    monkeypatch.setattr(fyp, "get_transcript_text", raise_blocked)

    with tempfile.TemporaryDirectory() as d:
        with pytest.raises(FakeIpBlocked):
            fyp.fetch_one("vid789", Path(d))
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tools/test_fetch_yt_playlist.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'fetch_yt_playlist'`

- [ ] **Step 3: Write the implementation**

```python
# tools/fetch_yt_playlist.py
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

PAUSE_SECONDS = 45
LONG_PAUSE_SECONDS = 90
LONG_PAUSE_THRESHOLD = 10

GENERIC_WORDS = {"playlist", "series", "videos", "video"}


def derive_domain(playlist_title: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", playlist_title.lower())
    words = [w for w in words if w not in GENERIC_WORDS]
    return "-".join(words) if words else "misc"


def list_playlist_entries(playlist_url: str) -> tuple[str, str, list[tuple[str, str]]]:
    out = subprocess.run(
        [sys.executable, "-m", "yt_dlp", "--flat-playlist", "--print",
         "%(playlist_id)s | %(playlist_title)s | %(id)s | %(title)s", playlist_url],
        capture_output=True, text=True, check=True,
    ).stdout.strip().splitlines()
    playlist_id, playlist_title = None, None
    entries = []
    for line in out:
        pid, ptitle, vid, vtitle = line.split(" | ", 3)
        playlist_id, playlist_title = pid, ptitle
        entries.append((vid, vtitle))
    return playlist_id, playlist_title, entries


def fetch_one(video_id: str, out_dir: Path) -> str:
    meta = get_metadata(video_id)
    try:
        text = get_transcript_text(video_id)
    except Exception as e:
        if "Subtitles are disabled" in str(e):
            return "skipped_no_captions"
        raise

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

    if not todo:
        print(f"Nichts zu tun: {done_count}/{total} bereits geholt.")
        return 0

    fetched_this_session = 0
    by_id = {v["id"]: v for v in checkpoint["videos"]}
    for i, (video_id, title) in enumerate(todo):
        try:
            status = fetch_one(video_id, raw_dir)
        except Exception as e:
            if type(e).__name__ == "IpBlocked":
                save_checkpoint(checkpoint_path, checkpoint)
                remaining = len(todo) - i
                print(f"GESTOPPT (IP-Block) bei '{title}' ({video_id}). "
                      f"{done_count}/{total} geholt, {remaining} verbleibend inkl. diesem Video. "
                      f"Erneuter Aufruf setzt hier fort.")
                return 1
            raise
        by_id[video_id]["status"] = status
        if status == "done":
            done_count += 1
        save_checkpoint(checkpoint_path, checkpoint)
        fetched_this_session += 1

        if i < len(todo) - 1:
            pause = LONG_PAUSE_SECONDS if fetched_this_session >= LONG_PAUSE_THRESHOLD else PAUSE_SECONDS
            time.sleep(pause)

    print(f"Fertig: {done_count}/{total} geholt.")
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tools/test_fetch_yt_playlist.py -v`
Expected: PASS (4 tests)

- [ ] **Step 5: Commit**

```bash
git add tools/fetch_yt_playlist.py tools/test_fetch_yt_playlist.py
git commit -m "$(cat <<'EOF'
add fetch_yt_playlist.py orchestrator

Enumerates a playlist, resumes via checkpoint, dedups against existing
raw/ transcripts, paces requests, and hard-stops on IpBlocked without
corrupting checkpoint state. Imports fetch_yt_transcript.py unmodified.
EOF
)"
```

---

### Task 3: Gitignore the checkpoint state directory

**Files:**
- Modify: `.gitignore`

**Interfaces:** None (config-only task).

- [ ] **Step 1: Add the gitignore entry**

Add this block near the existing "Algo Backtest-Rohlaeufe" / transient-state section of
`.gitignore` (see the existing `algo/live/*/state.json` entry for precedent):

```gitignore

# --- YouTube-Playlist-Ingest ---
# Laufzeit-Checkpoint fuer resumable Playlist-Fetches (fetch_yt_playlist.py) --
# reine Betriebsbuchhaltung, kein Content.
**/.yt_playlist_state/
```

- [ ] **Step 2: Verify it takes effect**

Run: `python -c "from pathlib import Path; p = Path('raw/_gitignore_test/.yt_playlist_state'); p.mkdir(parents=True, exist_ok=True); (p / 'x.json').write_text('{}')"`
Then: `git status --porcelain raw/_gitignore_test/`
Expected: no output (file is ignored)

Cleanup: `python -c "import shutil; shutil.rmtree('raw/_gitignore_test')"`

- [ ] **Step 3: Commit**

```bash
git add .gitignore
git commit -m "gitignore yt_playlist_state checkpoint directories"
```

---

### Task 4: Playlist-level integration test (checkpoint resume across two runs)

**Files:**
- Test: `tools/test_fetch_yt_playlist_integration.py`

**Interfaces:**
- Consumes: `fetch_yt_playlist.run`, `fetch_yt_playlist.list_playlist_entries` (monkeypatched),
  `fetch_yt_playlist.get_metadata`/`get_transcript_text` (monkeypatched), `time.sleep`
  (monkeypatched to avoid real waits in tests).

This is the end-to-end check the spec calls for: a fake 3-entry playlist, one already `done`,
confirms only the remaining 2 are fetched, and confirms a second `run()` call after an `IpBlocked`
interruption resumes correctly.

- [ ] **Step 1: Write the failing test**

```python
# tools/test_fetch_yt_playlist_integration.py
from pathlib import Path
import tempfile
import pytest

import fetch_yt_playlist as fyp
from yt_playlist_checkpoint import load_checkpoint, save_checkpoint


class FakeIpBlocked(Exception):
    pass


def _fake_entries():
    return ("PLtest", "My Test Playlist", [("a", "Video A"), ("b", "Video B"), ("c", "Video C")])


def test_run_skips_already_done_and_fetches_rest(monkeypatch, tmp_path):
    monkeypatch.setattr(fyp, "list_playlist_entries", lambda url: _fake_entries())
    monkeypatch.setattr(fyp, "get_metadata", lambda vid: {
        "title": f"Title {vid}", "channel": "C", "date": "2026-01-01", "duration": "1:00",
    })
    monkeypatch.setattr(fyp, "get_transcript_text", lambda vid: f"transcript {vid}")
    monkeypatch.setattr(fyp.time, "sleep", lambda s: None)

    out_dir = tmp_path / "raw" / "testdomain"
    checkpoint_path = out_dir / ".yt_playlist_state" / "PLtest.json"
    save_checkpoint(checkpoint_path, {
        "playlist_id": "PLtest", "playlist_title": "My Test Playlist",
        "videos": [{"id": "a", "title": "Video A", "status": "done"}],
    })

    exit_code = fyp.run("http://fake-url", out_dir)

    assert exit_code == 0
    assert not (out_dir / "yt-a-transcript.md").exists()  # was already done, no re-fetch attempted
    assert (out_dir / "yt-b-transcript.md").exists()
    assert (out_dir / "yt-c-transcript.md").exists()

    final = load_checkpoint(checkpoint_path)
    statuses = {v["id"]: v["status"] for v in final["videos"]}
    assert statuses == {"a": "done", "b": "done", "c": "done"}


def test_run_stops_on_ip_block_and_resumes_on_second_call(monkeypatch, tmp_path):
    monkeypatch.setattr(fyp, "list_playlist_entries", lambda url: _fake_entries())
    monkeypatch.setattr(fyp, "get_metadata", lambda vid: {
        "title": f"Title {vid}", "channel": "C", "date": "2026-01-01", "duration": "1:00",
    })
    monkeypatch.setattr(fyp.time, "sleep", lambda s: None)

    out_dir = tmp_path / "raw" / "testdomain"

    # First call: video "b" raises IpBlocked.
    def transcript_blocks_on_b(vid):
        if vid == "b":
            raise FakeIpBlocked("blocked")
        return f"transcript {vid}"
    monkeypatch.setattr(fyp, "get_transcript_text", transcript_blocks_on_b)

    exit_code = fyp.run("http://fake-url", out_dir)
    assert exit_code == 1

    checkpoint_path = out_dir / ".yt_playlist_state" / "PLtest.json"
    mid = load_checkpoint(checkpoint_path)
    statuses = {v["id"]: v["status"] for v in mid["videos"]}
    assert statuses["a"] == "done"
    assert statuses["b"] == "pending"  # not marked failed -- eligible for resume
    assert statuses["c"] == "pending"  # never attempted

    # Second call: no more blocking, should finish the rest.
    monkeypatch.setattr(fyp, "get_transcript_text", lambda vid: f"transcript {vid}")
    exit_code_2 = fyp.run("http://fake-url", out_dir)
    assert exit_code_2 == 0

    final = load_checkpoint(checkpoint_path)
    statuses = {v["id"]: v["status"] for v in final["videos"]}
    assert statuses == {"a": "done", "b": "done", "c": "done"}
```

- [ ] **Step 2: Run tests to verify they fail (or pass if Task 2's implementation already covers it)**

Run: `python -m pytest tools/test_fetch_yt_playlist_integration.py -v`
Expected: PASS if Task 2 was implemented per spec above. If it fails, the failure output tells you
which part of `run()`'s resume/IpBlocked handling is off — fix `fetch_yt_playlist.py` (not the
test) since the test encodes the spec's required behavior.

- [ ] **Step 3: Run the full test suite for this feature together**

Run: `python -m pytest tools/test_yt_playlist_checkpoint.py tools/test_fetch_yt_playlist.py tools/test_fetch_yt_playlist_integration.py -v`
Expected: PASS (all tests across the three files)

- [ ] **Step 4: Commit**

```bash
git add tools/test_fetch_yt_playlist_integration.py
git commit -m "add integration test for playlist resume-after-IpBlocked"
```

---

### Task 5: `yt-playlist-ingest` skill

**Files:**
- Create: `.claude/skills/yt-playlist-ingest/SKILL.md`

**Interfaces:** None (documentation/orchestration skill, no code interface — it drives
`tools/fetch_yt_playlist.py` via CLI and then the manual CLAUDE.md ingest workflow).

- [ ] **Step 1: Write the skill file**

```markdown
---
name: yt-playlist-ingest
description: Import a large YouTube playlist (any domain, not just trading) into raw/<domain>/ and the wiki, resumably and IP-ban-safely. Use when asked to import/ingest a whole playlist, e.g. "importiere diese Playlist", "importier alle Videos aus <Playlist-URL>", "setz den Playlist-Import fort".
---

Generic, resumable playlist ingest — unlike `yt-ict-ingest` (single-channel, trading-filtered),
this skill takes any playlist URL and any domain, and applies the **general ingest workflow from
`CLAUDE.md`** with no domain-specific content filter. Follows the same batch/no-clarifying-questions
rule from CLAUDE.md's Ingest section — this file adds the playlist-specific mechanics.

## 1. Fetch transcripts (resumable, IP-ban-safe)

```bash
python tools/fetch_yt_playlist.py "<playlist-url>" [--out-dir raw/<domain>]
```

- Without `--out-dir`, the tool derives a domain slug from the playlist title and prints it —
  check the printed domain in the report; if it's wrong, re-run with an explicit `--out-dir`
  (already-fetched transcripts are not re-fetched, the checkpoint just gets reassigned by pointing
  `--out-dir` at the new location manually if needed).
- The tool paces itself (45s/90s between videos) and stops immediately on an IP block, printing
  how many videos were fetched and how many remain. **Do not retry immediately** — an IP block is
  session-wide, not per-video; re-running right away will not help. Report the stop to the user;
  they decide when to re-run (per project convention, this skill does not auto-schedule a retry).
- Re-running the exact same command later **resumes** automatically — it reads the checkpoint at
  `raw/<domain>/.yt_playlist_state/<playlist_id>.json` and only fetches videos still `pending`.
- Videos with disabled captions are marked `skipped_no_captions` and skipped, not retried — note
  them in the batch report, do not fabricate a transcript.

## 2. Wiki ingest for newly fetched transcripts

For every transcript that reached `status: done` in this session (check the checkpoint JSON, or
diff which `raw/<domain>/yt-*-transcript.md` files are new), apply the **general Ingest workflow**
from `CLAUDE.md` — no ICT-style relevance filter:

1. Read each raw transcript.
2. Create `wiki/sources/youtube/<upload-date> - <Titel> (Source).md` per CLAUDE.md's page
   conventions (frontmatter, `Quelle:`/`Kanal:`/date/length line, summary + key points, link to
   the raw file).
3. Create/update `wiki/concepts/` or domain-appropriate pages for any new concept, term, or
   numeric claim — search the existing wiki first so additions extend rather than duplicate.
4. Update `wiki/index.md`.

## 3. Batch wrap-up

- One `wiki/log.md` entry (type `ingest`) per session-batch: playlist title, domain, how many
  fetched/skipped/stopped-early this session.
- One `.\push.ps1 -Message "ingest | <playlist title>"` call at the end of **this session's**
  batch — not per video, and not held back until the entire playlist finishes if that spans
  multiple sessions (a multi-day playlist import means multiple pushes, one per session).

## Gotchas

- Playlist/video IDs starting with `-` need a `--` separator when passed as bare CLI args
  elsewhere in this pipeline (not an issue for this tool's `playlist_url` argument, since URLs
  don't start with `-`, but relevant if you manually re-run `fetch_yt_transcript.py` on a single
  stuck video).
- `--flat-playlist` entries carry no reliable per-video upload date at enumeration time — the
  per-video `get_metadata()` call inside `fetch_one()` resolves the real date, so this is already
  handled; don't try to date-sort from the enumeration step.
- Never run this in parallel with itself or with `yt-ict-ingest` in another session/subagent —
  the historical `IpBlocked` trigger has always been concurrent access, not raw volume.
- The checkpoint directory (`.yt_playlist_state/`) is gitignored — it's local operational state,
  not wiki content. Don't hand-edit it; let the tool manage it.
```

- [ ] **Step 2: Verify the skill file is discoverable**

Run: `python -c "import yaml, pathlib; d = yaml.safe_load(pathlib.Path('.claude/skills/yt-playlist-ingest/SKILL.md').read_text(encoding='utf-8').split('---')[1]); print(d['name'], '|', d['description'][:60])"`
Expected: prints `yt-playlist-ingest | Import a large YouTube playlist (any domain, not ju`
(confirms frontmatter parses cleanly)

- [ ] **Step 3: Commit**

```bash
git add ".claude/skills/yt-playlist-ingest/SKILL.md"
git commit -m "add yt-playlist-ingest skill"
```

---

## Self-Review Notes

- **Spec coverage:** checkpoint file location/schema (Task 1/2), domain auto-derivation (Task 2),
  dedup against existing files (Task 1/2), serial pacing 45s/90s (Task 2), `IpBlocked` hard-stop
  leaving checkpoint consistent (Task 2/4), `skipped_no_captions` no-fallback behavior (Task 2),
  resume-by-rerun (Task 2/4), gitignore (Task 3), self-test with fake 3-entry playlist incl. resume
  (Task 4), skill orchestration + CLAUDE.md handoff + one push per session (Task 5) — all covered.
- **Not modifying `fetch_yt_transcript.py`:** confirmed — Task 2 only imports from it.
- **Type consistency:** `run()` returns `int` exit code throughout (Task 2 and Task 4 agree);
  checkpoint dict shape (`playlist_id`, `playlist_title`, `videos: [{id, title, status}]`) is
  identical across Task 1, 2, and 4.
