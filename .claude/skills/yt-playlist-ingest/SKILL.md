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
  check the printed domain in the report; if it's wrong, move both the transcript files (`yt-*-transcript.md`)
  and the checkpoint file (`raw/<wrong-domain>/.yt_playlist_state/<playlist_id>.json`) to `raw/<correct-domain>/`
  before re-running with `--out-dir raw/<correct-domain>`; otherwise the tool will re-fetch everything from
  scratch and burn the fetch budget.
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
