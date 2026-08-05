---
name: yt-ict-ingest
description: Import new YouTube videos from The Inner Circle Trader channel into the Gedanken wiki (raw transcript + filtered wiki pages). Use when asked to import/ingest new ICT videos, e.g. "importiere alle videos der letzten woche", "importiere neue ICT-Videos", "gibt es neue Videos vom Kanal".
---

Recurring ingest pipeline for `https://www.youtube.com/@InnerCircleTrader`. Follows the general
Ingest rules in `CLAUDE.md` (batch, no clarifying questions, report at the end, self-run
`push.ps1`) — this skill adds the video-specific mechanics.

## 1. Find candidate videos

List the channel newest-first (the bare channel URL is **not** sorted newest-first — the
`sort=dd` query param is required):

```bash
python -m yt_dlp --flat-playlist --playlist-end 15 --print "%(id)s | %(title)s" \
  "https://www.youtube.com/@InnerCircleTrader/videos?view=0&sort=dd"
```

For each id in the requested window, get the real upload date (flat-playlist entries don't carry
one):

```bash
python -m yt_dlp --print "%(id)s | %(upload_date)s | %(duration_string)s | %(title)s" \
  --skip-download "https://www.youtube.com/watch?v=<id>"
```

Walk down the list until `upload_date` falls outside the requested window (e.g. "last week" =
today minus 7 days). Cross-check candidates against `raw/trading-ict/2026/yt-*-transcript.md`
(filename = `yt-<id>-transcript.md`) and `wiki/log.md` — skip ids already ingested.

## 2. Fetch transcript + metadata

```bash
python tools/fetch_yt_transcript.py <video_id>
```

Pulls title/channel/upload date via `yt-dlp` and the transcript via YouTube's own auto-captions
(`youtube_transcript_api` — no ffmpeg/Whisper needed). Writes
`raw/trading-ict/2026/yt-<id>-transcript.md` in the same format as the existing files there
(title header, `Quelle:`/`Kanal:` line, `## Transkript (auto-generiert)`).

**If it fails with "Subtitles are disabled for this video"**: no auto-captions exist (common for
videos marked `[Silent]`, i.e. screen recordings without narration). Do not fabricate a
transcript. Note the video as skipped in the batch report/log with the reason. A Whisper fallback
would need `ffmpeg` on PATH — check with `where ffmpeg` / `ffmpeg -version` first; if missing,
report that instead of attempting it silently.

## 3. Filter to trading-relevant content ("meine Regeln")

ICT's videos mix genuinely new trading rules with a large amount of non-trading content. Read the
full raw transcript, then keep only concrete, generalizable trading rules, setups, numeric
examples, and named concepts — drop:

- Personal/family anecdotes, health updates, life updates
- Meta-commentary defending against critics/plagiarism accusations, "smooth brains" rants
- General motivational rhetoric about prediction-vs-reaction, discipline, mindset (unless it states
  a genuinely new, concrete rule — most of this is repeated across videos and already in the wiki)
- Self-promotion, charity/prop-firm partner shoutouts, X/Twitter references

## 4. Write wiki pages (same conventions as any ingest, see `CLAUDE.md`)

- `wiki/sources/<Title> (Source).md`: frontmatter, `Quelle:`/`Kanal:`/date/length line, a
  blockquote noting the raw transcript path and any coverage gap (auto-captions can cut off before
  the video ends — check the raw file's word count against the stated video length), a
  `## Kernaussagen (trading-relevant, gefiltert)` section (bullets, link out to concept/model pages
  rather than re-explaining), a `## Bewusst ausgefiltert` section (one line naming what was
  dropped), a `## Verwandt` section.
- Update or create `wiki/concepts/` / `wiki/models/` pages for any new rule, term, or numeric
  example — search the existing wiki first (`wiki/index.md`, related concept pages) so an addition
  extends an existing page instead of duplicating it. Bump `updated:` and add the new source to
  `sources:` in frontmatter whenever a page's body changes.
- Multiple videos often cover the **same trading day** from different angles (e.g. a live review +
  a deeper Saturday breakdown of the same Friday) — cross-link them explicitly and avoid
  re-documenting a rule that's already captured from the companion video; note only what's new.

## 5. Batch wrap-up

- One `wiki/index.md` update (Sources + Concepts/Models sections) covering the whole batch.
- One `wiki/log.md` entry, type `ingest`, listing: channel scan window, which candidates were
  in-window vs. already-ingested vs. skipped (with reason), pages created/extended.
- One `.\push.ps1 -Message "ingest | <summary>"` call at the end of the batch, not per video.

## Gotchas

- `--flat-playlist` entries have no `upload_date` — always resolve real dates with a second,
  non-flat `yt-dlp` call per candidate before deciding the date window.
- `yt-dlp` and `youtube_transcript_api` are Python packages here, not standalone CLIs — invoke via
  `python -m yt_dlp ...`, not a bare `yt-dlp` command.
- Auto-caption transcripts have no timestamps and can end early (YouTube stops auto-captioning
  after a while on long videos) — always state the actual coverage (e.g. "~39 of 52 minutes") in
  the source page instead of implying full coverage.
