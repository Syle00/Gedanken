---
name: run-gedanken-wiki
description: Build the Gedanken wiki static site from wiki/*.md, serve it locally, and drive it in a real browser (navigate, search, click through pages, screenshot). Use when asked to build, run, preview, or screenshot the wiki site, or to confirm a wiki edit actually renders correctly.
---

This repo's "app" is `tools/build_site.py`: it turns `wiki/*.md` into a static,
wikipedia-style HTML site at `site/`. There is no server process and no
interactivity beyond client-side search — the site is meant to be opened as a
file. Drive it by serving `site/` over plain HTTP and controlling it with the
`claude-in-chrome` browser tools (`mcp__claude-in-chrome__*`) — see "Run (agent
path)" below. All paths below are relative to the repo root.

## Prerequisites

Python 3 (tested with 3.14) plus the two pure-Python deps in
`tools/requirements.txt`:

```bash
python -m pip install -r tools/requirements.txt   # markdown>=3.5, pyyaml>=6.0
```

If you'll also run `tools/sort_marktdaten.py` (invoked by `push.ps1`, step 0),
it needs the IANA tz database, which stock Windows Python does not ship:

```bash
python -m pip install tzdata
```

## Build

```bash
PYTHONIOENCODING=utf-8 python tools/build_site.py
```

Output: `219 Seiten gebaut → .../site/index.html`, plus a report of unresolved
wikilinks and any drift between `wiki/index.md` and the actual files (both are
informational, not errors — see `CLAUDE.md`'s page conventions).

`PYTHONIOENCODING=utf-8` is required on Windows — see Gotchas.

## Run (agent path)

Serve `site/` and drive it with `claude-in-chrome`. **`file://` does not
work with claude-in-chrome** (see Gotchas), so always serve over HTTP first.

```bash
cd site && python -m http.server 8843 --bind 127.0.0.1 &
timeout 15 bash -c 'until curl -sf http://127.0.0.1:8843/index.html >/dev/null; do sleep 0.5; done'
```

Then, in this session:

1. `mcp__claude-in-chrome__tabs_context_mcp` with `createIfEmpty: true` to get a tab.
2. `mcp__claude-in-chrome__navigate` to `http://127.0.0.1:8843/index.html`.
3. `mcp__claude-in-chrome__computer` with `action: screenshot` to see the home page.
4. To exercise search: `left_click` the search box (top-right, roughly
   `(1232, 26)` at a 1568-wide viewport), `type` a query (e.g. `"Order Block"`),
   `screenshot` — results render as a dropdown, top hit first.
5. `left_click` a result to open `p/<slug>.html`, `screenshot` to confirm the
   page (title, tags, sources, table of contents, resolved wikilinks,
   backlinks) rendered.
6. Batch steps 2–5 with `mcp__claude-in-chrome__browser_batch` where possible —
   one round trip instead of several.

Stop the server when done:

```bash
powershell -Command "Get-NetTCPConnection -LocalPort 8843 -State Listen | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }"
```

## Run (human path)

Open `site/index.html` directly in a browser — no server needed for normal
use, only for the agent-driven flow above (see Gotchas for why).

## Full publish (build + commit + push)

```powershell
.\push.ps1 -Message "..."
```

Runs, in order: `tools/sort_marktdaten.py` (tidies loose CSVs in
`raw/marktdaten/`, never fails the run), the build above (already sets
`PYTHONIOENCODING=utf-8` internally), `git add -A`, commit, push. If the build
fails, nothing is committed. `-NoPush` commits locally only.

## Related tools

Both are read-only in `--dry-run` and pure standard library (only
`sort_marktdaten.py` needs `tzdata`, per Prerequisites):

```bash
python tools/sort_marktdaten.py --dry-run   # preview CSV → daily-folder moves in raw/marktdaten/
python tools/journal_wiki.py --dry-run      # preview the generated journal/checklist wiki page
```

## Gotchas

- **`UnicodeEncodeError: 'charmap' codec can't encode character '\u2192'`**
  running `build_site.py` directly on Windows — its status prints use `→`,
  and the default console codepage (cp1252) can't encode it. Always set
  `PYTHONIOENCODING=utf-8` (already done for you inside `push.ps1`).
- **`claude-in-chrome` refuses `file://` URLs** — `navigate` to a
  `file:///C:/...` path errors with "Can't interact with browser-internal or
  unparseable URLs." There is no flag to allow it; serve over `http://`
  instead (see Run agent path). This is also why `build_site.py` ships
  `search-index.js` instead of `.js` — a `<script src>` tag loads fine over
  `file://`, a `fetch()` for JSON does not (CORS); serving over HTTP sidesteps
  both issues.
- **Windows `zoneinfo` has no tz database by default** — `sort_marktdaten.py`
  imports `zoneinfo.ZoneInfo` and throws deep inside
  `importlib.resources` if the `tzdata` package isn't installed (stock
  CPython on Windows doesn't bundle it, unlike Linux/macOS). Fix: `python -m
  pip install tzdata`.
- **The build is idempotent** — re-running `build_site.py` against an
  unchanged `wiki/` produces byte-identical output (verified via `git status`
  showing no diff under `site/`). If you see a `site/` diff after a build,
  it's a real content change, not build noise.
