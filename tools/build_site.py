#!/usr/bin/env python3
"""Baut aus wiki/*.md eine statische, wikipedia-artige HTML-Website nach site/.

Aufruf:  python tools/build_site.py

Die Website ist fuer die lokale Nutzung per file:// gedacht. Bilder werden nicht
kopiert, sondern relativ nach raw/ referenziert -- das haelt site/ bei ~2 MB
statt 190 MB.
"""

from __future__ import annotations

import html
import json
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

try:
    import markdown
    import yaml
except ImportError:
    sys.exit("Fehlende Abhaengigkeiten. Bitte ausfuehren:\n"
             "  python -m pip install -r tools/requirements.txt")

ROOT = Path(__file__).resolve().parent.parent
WIKI = ROOT / "wiki"
SITE = ROOT / "site"
PAGES_DIR = SITE / "p"

IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}

# Reihenfolge und deutsche Anzeigenamen der Kategorien.
CATEGORIES = [
    ("concepts", "Konzepte"),
    ("models", "Modelle"),
    ("sources", "Quellen"),
    ("synthesis", "Synthese"),
    ("meta", "Meta"),
]
CATEGORY_LABEL = dict(CATEGORIES)

WIKILINK_RE = re.compile(r"(!?)\[\[([^\]\n]+)\]\]")
FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n?", re.DOTALL)
INDEX_ENTRY_RE = re.compile(
    r"^-\s*\[\[([^\]|]+?)(?:\|[^\]]*)?\]\]\s*[—-]\s*(.*?)\s*$", re.MULTILINE
)


# --------------------------------------------------------------------------- #
# Hilfsfunktionen
# --------------------------------------------------------------------------- #

UMLAUTS = str.maketrans({
    "ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss",
    "Ä": "ae", "Ö": "oe", "Ü": "ue",
    "é": "e", "è": "e", "ê": "e", "á": "a", "à": "a", "í": "i", "ó": "o", "ú": "u",
})


def slugify(text: str) -> str:
    """Titel -> URL-tauglicher Slug, mit Umlaut-Transliteration."""
    s = text.translate(UMLAUTS).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "seite"


def strip_html(fragment: str) -> str:
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", fragment, flags=re.DOTALL | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def strip_markup(text: str) -> str:
    """Wikilinks/Markdown-Auszeichnung aus einer Zeile entfernen (fuer Summaries)."""
    text = re.sub(r"!?\[\[([^\]|]+)(?:\|([^\]]+))?\]\]", lambda m: m.group(2) or m.group(1), text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[*_`#>]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def write(path: Path, text: str) -> None:
    """Immer mit LF schreiben - sonst meldet Git bei jedem Build 150+ CRLF-Warnungen."""
    path.write_text(text, encoding="utf-8", newline="\n")


def as_text(value) -> str:
    if isinstance(value, (date,)):
        return value.isoformat()
    return "" if value is None else str(value)


# --------------------------------------------------------------------------- #
# Einlesen
# --------------------------------------------------------------------------- #

class Page:
    __slots__ = ("path", "title", "category", "slug", "meta", "body",
                 "html", "toc", "summary", "outgoing")

    def __init__(self, path: Path, title: str, category: str, meta: dict, body: str):
        self.path = path
        self.title = title
        self.category = category
        self.meta = meta
        self.body = body
        self.slug = ""
        self.html = ""
        self.toc = ""
        self.summary = ""
        self.outgoing: set[str] = set()


def collect_pages() -> list[Page]:
    pages: list[Page] = []
    for path in sorted(WIKI.rglob("*.md")):
        rel = path.relative_to(WIKI)
        if "graphify-out" in rel.parts:
            continue  # verirrter Semantic-Cache, kein Wiki-Inhalt
        category = rel.parts[0] if len(rel.parts) > 1 else "meta"
        if category not in CATEGORY_LABEL:
            category = "meta"

        raw = path.read_text(encoding="utf-8", errors="replace")
        meta: dict = {}
        m = FRONTMATTER_RE.match(raw)
        body = raw
        if m:
            try:
                parsed = yaml.safe_load(m.group(1))
                if isinstance(parsed, dict):
                    meta = parsed
            except yaml.YAMLError as exc:
                print(f"  ! Frontmatter unlesbar in {rel}: {exc}")
            body = raw[m.end():]

        pages.append(Page(path, path.stem, category, meta, body))
    return pages


def collect_assets() -> dict[str, str]:
    """Basename (lowercase) -> Pfad relativ zum Repo-Root, wie Obsidian es aufloest."""
    assets: dict[str, str] = {}
    for path in ROOT.rglob("*"):
        if path.suffix.lower() not in IMAGE_EXT or not path.is_file():
            continue
        if "site" in path.relative_to(ROOT).parts:
            continue
        assets.setdefault(path.name.lower(), path.relative_to(ROOT).as_posix())
    return assets


def parse_index() -> tuple[dict[str, str], set[str]]:
    """wiki/index.md auswerten.

    Liefert (Zusammenfassungen, alle gelisteten Titel). Nicht jeder Eintrag hat eine
    Zusammenfassung -- die Quellen-Sektion listet oft nur den Link. Fuer den
    Drift-Report zaehlt die vollstaendige Titelmenge, nicht nur die mit Text.
    """
    index_file = WIKI / "index.md"
    if not index_file.exists():
        return {}, set()

    text = index_file.read_text(encoding="utf-8")
    # Die Quellen-Sektion buendelt mehrere Links pro Zeile, darum alle Wikilinks
    # der Datei einsammeln statt nur den jeweils ersten einer Aufzaehlung.
    listed = {m.group(1).strip().lower()
              for m in re.finditer(r"(?<!!)\[\[([^\]|]+?)(?:\|[^\]]*)?\]\]", text)}

    summaries: dict[str, str] = {}
    for title, rest in INDEX_ENTRY_RE.findall(text):
        body = re.sub(r"\s*\(\d{4}-\d{2}-\d{2}\)\s*$", "", rest).strip()
        if body:
            summaries[title.strip().lower()] = strip_markup(body)
    return summaries, listed


def derive_summary(page: Page) -> str:
    """Fallback: erster echter Textabsatz der Seite."""
    for line in page.body.splitlines():
        line = line.strip()
        if not line or line.startswith(("#", "!", ">", "|", "---", "```")):
            continue
        text = strip_markup(line.lstrip("-* ").strip())
        if len(text) > 20:
            return text[:180] + ("…" if len(text) > 180 else "")
    return ""


# --------------------------------------------------------------------------- #
# Wikilink-Aufloesung
# --------------------------------------------------------------------------- #

class Resolver:
    def __init__(self, pages: list[Page], assets: dict[str, str]):
        self.by_title = {p.title.lower(): p for p in pages}
        self.assets = assets
        self.broken: dict[str, set[str]] = defaultdict(set)

    def lookup(self, target: str) -> Page | None:
        """Obsidian-nahe Aufloesung eines Linkziels auf eine Wiki-Seite."""
        name = target[:-3] if target.lower().endswith(".md") else target

        candidates = [name]
        # Titel duerfen kein "/" enthalten; Obsidian-Links schreiben es trotzdem
        # (z.B. [[DXY Correlation (Risk On/Off)]] -> Datei "... (Risk On_Off).md").
        if "/" in name:
            candidates.append(name.replace("/", "_"))
            candidates.append(name.rsplit("/", 1)[-1])          # [[../CLAUDE.md]]
        # Konvention aus CLAUDE.md: zur Rohquelle "X" gehoert die Wiki-Seite "X (Source)".
        candidates += [f"{c} (Source)" for c in list(candidates)]

        for cand in candidates:
            hit = self.by_title.get(cand.strip().lower())
            if hit:
                return hit
        return None

    def resolve(self, text: str, page: Page, depth: str = "../") -> str:
        """Ersetzt alle Wikilinks durch HTML. `depth` ist der Praefix zu site/."""

        def replace(match: re.Match) -> str:
            embed = match.group(1) == "!"
            inner = match.group(2).strip()
            target, _, alias = inner.partition("|")
            target = target.split("#", 1)[0].strip()   # Heading-Anker: im Bestand ungenutzt
            alias = alias.strip()
            basename = target.rstrip("/").split("/")[-1]
            label = alias or (basename[:-3] if basename.lower().endswith(".md") else basename)

            # 1) Bild-Embed
            if Path(basename).suffix.lower() in IMAGE_EXT:
                rel = self.assets.get(basename.lower())
                if rel:
                    src = f"{depth}../{rel}"
                    return (f'<img class="wiki-img" src="{html.escape(src)}" '
                            f'alt="{html.escape(Path(basename).stem)}" loading="lazy">')
                self.broken[basename].add(page.title)
                return f'<span class="broken">Bild fehlt: {html.escape(basename)}</span>'

            # 2) Seiten-Link
            hit = self.lookup(target)
            if hit:
                page.outgoing.add(hit.title)
                prefix = "!" if embed else ""
                return (f'{prefix}<a href="{depth}p/{hit.slug}.html">'
                        f'{html.escape(label)}</a>')

            # 3) Unaufloesbar -> bewusste Luecke, kein Fehler (siehe CLAUDE.md)
            self.broken[target].add(page.title)
            return (f'<span class="broken" title="Seite existiert noch nicht">'
                    f'{html.escape(label)}</span>')

        return WIKILINK_RE.sub(replace, text)


# --------------------------------------------------------------------------- #
# Markdown -> HTML
# --------------------------------------------------------------------------- #

IMG_LINE_RE = re.compile(r'^\s*(<img class="wiki-img"[^>]*>)\s*$')
CAPTION_LINE_RE = re.compile(r"^\s*\*([^*].*?)\*\s*$")
LIST_ITEM_RE = re.compile(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)")


def wrap_figures(text: str) -> str:
    """Bild (+ direkt folgende Kursivzeile) zu einem <figure>-Block zusammenfassen.

    Laeuft auf dem Markdown *vor* dem Rendern: als Block-HTML mit Leerzeilen davor
    und danach reicht Python-Markdown das <figure> unveraendert durch. Eine
    Nachbearbeitung des fertigen HTML waere fehleranfaellig, weil Bild, Unterschrift
    und nachfolgende Liste in den Quelldateien oft im selben Absatz stehen.
    """
    lines = text.split("\n")
    out: list[str] = []
    i = 0
    while i < len(lines):
        m = IMG_LINE_RE.match(lines[i])
        if not m:
            out.append(lines[i])
            i += 1
            continue

        caption = ""
        i += 1
        if i < len(lines):
            cap = CAPTION_LINE_RE.match(lines[i])
            if cap:
                caption = cap.group(1).strip()
                i += 1

        figcaption = f"<figcaption>{caption}</figcaption>" if caption else ""
        if out and out[-1].strip():
            out.append("")
        out.append(f"<figure>{m.group(1)}{figcaption}</figure>")
        out.append("")
    return "\n".join(out)


def normalize_lists(text: str) -> str:
    """Fehlende Leerzeile vor einem Listenbeginn ergaenzen.

    Obsidian rendert eine Liste auch direkt unter einem Textabsatz; Python-Markdown
    verlangt eine Leerzeile und wuerde die Punkte sonst als Fliesstext ausgeben.
    """
    out: list[str] = []
    in_list = False
    in_code = False
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            out.append(line)
            continue
        if in_code:
            out.append(line)
            continue

        if not stripped:
            in_list = False
        elif LIST_ITEM_RE.match(line):
            if not in_list and out and out[-1].strip():
                out.append("")
            in_list = True
        elif not line.startswith((" ", "\t")):
            in_list = False   # sonst: eingerueckte Fortsetzung, Liste bleibt offen
        out.append(line)
    return "\n".join(out)


# --------------------------------------------------------------------------- #
# HTML-Geruest
# --------------------------------------------------------------------------- #

def nav_html(pages: list[Page], current: Page | None, depth: str) -> str:
    by_cat: dict[str, list[Page]] = defaultdict(list)
    for p in pages:
        by_cat[p.category].append(p)

    out = ['<nav class="sidebar">']
    out.append(f'<a class="brand" href="{depth}index.html">Gedanken</a>')
    out.append('<div class="nav-block"><div class="nav-head">Kategorien</div><ul>')
    for key, label in CATEGORIES:
        items = by_cat.get(key, [])
        if not items:
            continue
        active = " class=\"active\"" if current and current.category == key else ""
        out.append(f'<li{active}><a href="{depth}index.html#{key}">{label}'
                   f'<span class="count">{len(items)}</span></a></li>')
    out.append("</ul></div>")

    if current:
        siblings = sorted(by_cat[current.category], key=lambda p: p.title.lower())
        out.append(f'<div class="nav-block"><div class="nav-head">'
                   f'{CATEGORY_LABEL[current.category]}</div><ul class="pagelist">')
        for p in siblings:
            cls = ' class="here"' if p is current else ""
            out.append(f'<li{cls}><a href="{depth}p/{p.slug}.html">'
                       f'{html.escape(p.title)}</a></li>')
        out.append("</ul></div>")
    out.append("</nav>")
    return "\n".join(out)


def shell(title: str, depth: str, nav: str, main: str, body_class: str = "") -> str:
    cls = f' class="{body_class}"' if body_class else ""
    return f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} — Gedanken</title>
<link rel="stylesheet" href="{depth}style.css">
</head>
<body{cls}>
<header class="topbar">
  <button class="menu-toggle" aria-label="Navigation">☰</button>
  <a class="topbrand" href="{depth}index.html">Gedanken</a>
  <div class="searchbox">
    <input id="q" type="search" placeholder="Wiki durchsuchen …" autocomplete="off"
           spellcheck="false">
    <div id="results" class="results" hidden></div>
  </div>
  <a class="random" href="#" id="random" title="Zufällige Seite">🎲</a>
</header>
<div class="layout">
{nav}
<main>
{main}
</main>
</div>
<script src="{depth}search-index.js"></script>
<script src="{depth}search.js"></script>
</body>
</html>
"""


def render_page(page: Page, pages: list[Page], backlinks: list[Page],
                resolver: Resolver) -> str:
    meta_bits = []
    tags = page.meta.get("tags") or []
    if isinstance(tags, str):
        tags = [tags]
    if tags:
        chips = " ".join(f'<span class="tag">{html.escape(as_text(t))}</span>' for t in tags)
        meta_bits.append(f'<div class="tags">{chips}</div>')

    dates = []
    if page.meta.get("created"):
        dates.append(f"erstellt {html.escape(as_text(page.meta['created']))}")
    if page.meta.get("updated"):
        dates.append(f"aktualisiert {html.escape(as_text(page.meta['updated']))}")
    if dates:
        meta_bits.append(f'<div class="dates">{" · ".join(dates)}</div>')

    sources = page.meta.get("sources") or []
    if isinstance(sources, str):
        sources = [sources]
    if sources:
        links = ", ".join(resolver.resolve(as_text(s), page) for s in sources)
        meta_bits.append(f'<div class="srcline"><span>Quellen:</span> {links}</div>')

    toc = ""
    if page.toc.count("<li>") >= 3:
        toc = f'<details class="toc" open><summary>Inhalt</summary>{page.toc}</details>'

    back = ""
    if backlinks:
        items = "".join(
            f'<li><a href="../p/{p.slug}.html">{html.escape(p.title)}</a>'
            f'<span class="cat">{CATEGORY_LABEL[p.category]}</span></li>'
            for p in sorted(backlinks, key=lambda p: p.title.lower()))
        back = (f'<section class="backlinks"><h2>Was zeigt hierher '
                f'<span class="count">{len(backlinks)}</span></h2>'
                f'<ul>{items}</ul></section>')

    rel_src = page.path.relative_to(ROOT).as_posix()
    main = f"""<article>
  <div class="crumb"><a href="../index.html">Gedanken</a> ›
    <a href="../index.html#{page.category}">{CATEGORY_LABEL[page.category]}</a></div>
  <h1>{html.escape(page.title)}</h1>
  <div class="pagemeta">{''.join(meta_bits)}</div>
  {toc}
  <div class="content">{page.html}</div>
  {back}
  <footer class="pagefoot">Quelldatei: <code>{html.escape(rel_src)}</code></footer>
</article>"""
    return shell(page.title, "../", nav_html(pages, page, "../"), main)


def render_home(pages: list[Page], summaries: dict[str, str], broken_count: int) -> str:
    by_cat: dict[str, list[Page]] = defaultdict(list)
    for p in pages:
        by_cat[p.category].append(p)

    parts = [f"""<article class="home">
  <h1>Gedanken</h1>
  <p class="lead">Persönliches Wissenssystem nach dem LLM-Wiki-Muster.
     {len(pages)} Seiten in {len([c for c, _ in CATEGORIES if by_cat.get(c)])} Kategorien.</p>"""]

    for key, label in CATEGORIES:
        items = sorted(by_cat.get(key, []), key=lambda p: p.title.lower())
        if not items:
            continue
        parts.append(f'<section id="{key}" class="catsection">'
                     f'<h2>{label} <span class="count">{len(items)}</span></h2><ul class="cards">')
        for p in items:
            summary = html.escape(p.summary) if p.summary else ""
            parts.append(f'<li><a href="p/{p.slug}.html">{html.escape(p.title)}</a>'
                         f'{f"<span>{summary}</span>" if summary else ""}</li>')
        parts.append("</ul></section>")

    if broken_count:
        parts.append(f'<p class="hint">{broken_count} Wikilinks zeigen auf noch nicht '
                     f'existierende Seiten — im Text grau markiert.</p>')
    parts.append("</article>")
    return shell("Startseite", "", nav_html(pages, None, ""), "\n".join(parts), "is-home")


# --------------------------------------------------------------------------- #
# Statische Assets
# --------------------------------------------------------------------------- #

STYLE = """
:root{
  --bg:#fff; --fg:#1f2328; --muted:#5b6570; --line:#d8dee4; --soft:#f6f8fa;
  --link:#0b5cad; --visited:#6b3fa0; --accent:#0b5cad; --broken:#98a1ab;
  --serif: "Iowan Old Style","Palatino Linotype",Palatino,Georgia,"Times New Roman",serif;
  --sans: -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
}
@media (prefers-color-scheme: dark){
  :root{ --bg:#15181c; --fg:#e3e6ea; --muted:#98a1ab; --line:#2c333b; --soft:#1c2026;
         --link:#79b8ff; --visited:#c3a6ff; --accent:#79b8ff; --broken:#69727c; }
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--fg);font-family:var(--sans);line-height:1.6}

/* --- Topbar ------------------------------------------------------------- */
.topbar{position:sticky;top:0;z-index:20;display:flex;align-items:center;gap:12px;
  padding:8px 16px;background:var(--bg);border-bottom:1px solid var(--line)}
.topbrand{font-weight:700;text-decoration:none;color:var(--fg);letter-spacing:.02em}
.menu-toggle{display:none;background:none;border:1px solid var(--line);border-radius:6px;
  color:var(--fg);font-size:16px;padding:4px 9px;cursor:pointer}
.searchbox{position:relative;flex:1;max-width:520px;margin-left:auto}
#q{width:100%;padding:7px 12px;border:1px solid var(--line);border-radius:999px;
  background:var(--soft);color:var(--fg);font-size:14px;font-family:inherit}
#q:focus{outline:2px solid var(--accent);outline-offset:-1px;background:var(--bg)}
.results{position:absolute;top:calc(100% + 6px);left:0;right:0;max-height:60vh;overflow:auto;
  background:var(--bg);border:1px solid var(--line);border-radius:8px;
  box-shadow:0 8px 28px rgba(0,0,0,.16);padding:4px}
.results a{display:block;padding:7px 10px;border-radius:6px;text-decoration:none;color:var(--fg)}
.results a:hover,.results a.sel{background:var(--soft)}
.results .rt{font-weight:600}
.results .rc{font-size:12px;color:var(--muted);margin-left:6px}
.results .rx{display:block;font-size:12.5px;color:var(--muted);
  overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.results .empty{padding:10px;color:var(--muted);font-size:14px}
.random{text-decoration:none;font-size:18px;opacity:.75}
.random:hover{opacity:1}

/* --- Layout ------------------------------------------------------------- */
.layout{display:grid;grid-template-columns:250px minmax(0,1fr);gap:32px;
  max-width:1180px;margin:0 auto;padding:0 16px}
main{min-width:0;padding:22px 0 80px}

/* --- Sidebar ------------------------------------------------------------ */
.sidebar{position:sticky;top:53px;align-self:start;max-height:calc(100vh - 53px);
  overflow-y:auto;padding:22px 0 40px;font-size:14px}
.brand{display:none}
.nav-block{margin-bottom:22px}
.nav-head{font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);
  font-weight:700;padding-bottom:6px;border-bottom:1px solid var(--line);margin-bottom:6px}
.sidebar ul{list-style:none;margin:0;padding:0}
.sidebar li{margin:1px 0}
.sidebar a{display:flex;justify-content:space-between;gap:8px;padding:4px 8px;
  border-radius:5px;text-decoration:none;color:var(--link)}
.sidebar a:hover{background:var(--soft)}
.sidebar li.active>a,.sidebar li.here>a{background:var(--soft);color:var(--fg);font-weight:600}
.sidebar .count{color:var(--muted);font-size:12px;font-variant-numeric:tabular-nums}
.pagelist a{display:block}

/* --- Artikel ------------------------------------------------------------ */
article{max-width:760px}
.crumb{font-size:13px;color:var(--muted);margin-bottom:6px}
.crumb a{color:var(--muted)}
h1{font-family:var(--serif);font-weight:400;font-size:2.1rem;line-height:1.25;
  margin:0 0 10px;padding-bottom:10px;border-bottom:1px solid var(--line)}
.content{font-family:var(--serif);font-size:1.02rem}
.content h2{font-family:var(--serif);font-weight:400;font-size:1.5rem;margin:1.8em 0 .5em;
  padding-bottom:6px;border-bottom:1px solid var(--line)}
.content h3{font-size:1.18rem;margin:1.5em 0 .4em}
.content h4{font-size:1.02rem;margin:1.3em 0 .3em}
a{color:var(--link)}
a:visited{color:var(--visited)}
.content li{margin:.28em 0}
.content ul,.content ol{padding-left:1.4em}
.content blockquote{margin:1em 0;padding:.6em 1em;border-left:3px solid var(--accent);
  background:var(--soft);border-radius:0 6px 6px 0}
.content blockquote p{margin:.3em 0}
.content code{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:.87em;
  background:var(--soft);padding:.12em .38em;border-radius:4px}
.content pre{background:var(--soft);padding:12px;border-radius:8px;overflow-x:auto}
.content pre code{background:none;padding:0}
.content hr{border:0;border-top:1px solid var(--line);margin:2em 0}
.content table{border-collapse:collapse;width:100%;font-family:var(--sans);font-size:.92rem;
  display:block;overflow-x:auto}
.content th,.content td{border:1px solid var(--line);padding:6px 10px;text-align:left}
.content th{background:var(--soft)}

figure{margin:1.4em 0;text-align:center}
.wiki-img{max-width:100%;height:auto;border:1px solid var(--line);border-radius:6px;
  background:var(--soft)}
figcaption{font-family:var(--sans);font-size:.83rem;color:var(--muted);margin-top:6px;
  text-align:center}

.broken{color:var(--broken);border-bottom:1px dashed var(--broken);cursor:help}

/* --- Seiten-Metadaten --------------------------------------------------- */
.pagemeta{margin-bottom:18px;font-size:13px}
.tags{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:6px}
.tag{background:var(--soft);border:1px solid var(--line);border-radius:999px;
  padding:1px 9px;color:var(--muted);font-size:12px}
.dates{color:var(--muted)}
.srcline{margin-top:4px;color:var(--muted)}
.srcline span{font-weight:600}

.toc{background:var(--soft);border:1px solid var(--line);border-radius:8px;
  padding:8px 14px;margin:0 0 22px;font-size:14px;max-width:440px}
.toc summary{cursor:pointer;font-weight:600}
.toc ul{margin:.4em 0;padding-left:1.1em}
.toc>div>ul{padding-left:.2em}
.toc li{margin:.15em 0}

.backlinks{margin-top:46px;padding-top:18px;border-top:1px solid var(--line)}
.backlinks h2{font-family:var(--serif);font-weight:400;font-size:1.3rem;margin:0 0 8px}
.backlinks ul{list-style:none;margin:0;padding:0;
  display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:2px 16px}
.backlinks li{display:flex;justify-content:space-between;gap:10px;padding:3px 0;font-size:14px}
.backlinks .cat{color:var(--muted);font-size:12px;white-space:nowrap}
.backlinks .count{color:var(--muted);font-size:.8em}

.pagefoot{margin-top:34px;font-size:12px;color:var(--muted)}
.pagefoot code{font-family:ui-monospace,Consolas,monospace}

/* --- Startseite --------------------------------------------------------- */
.home{max-width:920px}
.lead{color:var(--muted);margin-top:0}
.catsection{margin-top:34px;scroll-margin-top:70px}
.catsection h2{font-family:var(--serif);font-weight:400;font-size:1.6rem;
  margin:0 0 12px;padding-bottom:8px;border-bottom:1px solid var(--line)}
.catsection .count{color:var(--muted);font-size:.7em}
.cards{list-style:none;margin:0;padding:0;
  display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:10px 22px}
.cards li{padding:7px 0;border-bottom:1px dotted var(--line)}
.cards a{font-weight:600;text-decoration:none}
.cards a:hover{text-decoration:underline}
.cards span{display:block;color:var(--muted);font-size:13px;line-height:1.45;margin-top:2px}
.hint{margin-top:34px;color:var(--muted);font-size:13px}

/* --- Mobil -------------------------------------------------------------- */
@media (max-width:860px){
  .layout{grid-template-columns:1fr;gap:0}
  .menu-toggle{display:block}
  .sidebar{display:none;position:static;max-height:none}
  body.nav-open .sidebar{display:block}
  h1{font-size:1.7rem}
}
"""

SEARCH_JS = """
(function () {
  var idx = window.SEARCH_INDEX || [];
  for (var n = 0; n < idx.length; n++) idx[n].x = idx[n].raw.toLowerCase();
  var q = document.getElementById('q');
  var box = document.getElementById('results');
  var base = (document.querySelector('link[rel=stylesheet]').getAttribute('href') || '')
               .replace('style.css', '');
  var sel = -1, current = [];

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  function score(page, terms) {
    var t = page.t.toLowerCase(), g = (page.g || '').toLowerCase(), x = page.x;
    var total = 0;
    for (var i = 0; i < terms.length; i++) {
      var term = terms[i], s = 0;
      if (t === term) s = 1000;
      else if (t.indexOf(term) === 0) s = 400;
      else if (t.indexOf(term) > -1) s = 200;
      if (g.indexOf(term) > -1) s += 60;
      var at = x.indexOf(term);
      if (at > -1) s += 30;
      if (s === 0) return 0;          // jeder Begriff muss vorkommen
      total += s;
    }
    return total;
  }

  function excerpt(page, term) {
    var at = page.x.indexOf(term);
    if (at < 0) return page.s || '';
    var from = Math.max(0, at - 40);
    return (from > 0 ? '…' : '') + page.raw.substr(from, 120) + '…';
  }

  function render(list, terms) {
    if (!list.length) {
      box.innerHTML = '<div class="empty">Keine Treffer</div>';
      box.hidden = false;
      return;
    }
    box.innerHTML = list.map(function (p, i) {
      return '<a href="' + base + p.u + '" data-i="' + i + '">' +
             '<span class="rt">' + esc(p.t) + '</span>' +
             '<span class="rc">' + esc(p.c) + '</span>' +
             '<span class="rx">' + esc(excerpt(p, terms[0])) + '</span></a>';
    }).join('');
    box.hidden = false;
  }

  function run() {
    var value = q.value.trim().toLowerCase();
    sel = -1;
    if (value.length < 2) { box.hidden = true; return; }
    var terms = value.split(/\\s+/);
    var scored = [];
    for (var i = 0; i < idx.length; i++) {
      var s = score(idx[i], terms);
      if (s > 0) scored.push([s, idx[i]]);
    }
    scored.sort(function (a, b) { return b[0] - a[0]; });
    current = scored.slice(0, 25).map(function (p) { return p[1]; });
    render(current, terms);
  }

  function move(delta) {
    var links = box.querySelectorAll('a');
    if (!links.length) return;
    if (sel > -1) links[sel].classList.remove('sel');
    sel = (sel + delta + links.length) % links.length;
    links[sel].classList.add('sel');
    links[sel].scrollIntoView({ block: 'nearest' });
  }

  if (q) {
    q.addEventListener('input', run);
    q.addEventListener('focus', run);
    q.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown') { e.preventDefault(); move(1); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); move(-1); }
      else if (e.key === 'Enter') {
        var links = box.querySelectorAll('a');
        if (links.length) { e.preventDefault(); (links[sel > -1 ? sel : 0]).click(); }
      } else if (e.key === 'Escape') { box.hidden = true; q.blur(); }
    });
  }

  document.addEventListener('click', function (e) {
    if (box && !box.contains(e.target) && e.target !== q) box.hidden = true;
  });

  document.addEventListener('keydown', function (e) {
    if ((e.key === '/' || (e.key === 'k' && (e.ctrlKey || e.metaKey))) &&
        document.activeElement !== q) {
      e.preventDefault(); q.focus(); q.select();
    }
  });

  var toggle = document.querySelector('.menu-toggle');
  if (toggle) toggle.addEventListener('click', function () {
    document.body.classList.toggle('nav-open');
  });

  var rnd = document.getElementById('random');
  if (rnd) rnd.addEventListener('click', function (e) {
    e.preventDefault();
    if (idx.length) location.href = base + idx[Math.floor(Math.random() * idx.length)].u;
  });
})();
"""


# --------------------------------------------------------------------------- #
# Build
# --------------------------------------------------------------------------- #

def main() -> int:
    if not WIKI.is_dir():
        sys.exit(f"wiki/ nicht gefunden unter {WIKI}")

    print(f"Gedanken → Website")
    pages = collect_pages()
    if not pages:
        sys.exit("Keine Wiki-Seiten gefunden.")
    assets = collect_assets()
    summaries, listed = parse_index()
    print(f"  {len(pages)} Seiten, {len(assets)} Bilder, "
          f"{len(summaries)} Zusammenfassungen aus index.md")

    # Slugs (mit Kollisionsschutz)
    used: dict[str, int] = {}
    for page in sorted(pages, key=lambda p: p.title.lower()):
        base = slugify(page.title)
        if base in used:
            used[base] += 1
            page.slug = f"{base}-{used[base]}"
        else:
            used[base] = 1
            page.slug = base

    resolver = Resolver(pages, assets)
    md = markdown.Markdown(extensions=["extra", "sane_lists", "toc"],
                           extension_configs={"toc": {"toc_depth": "2-3"}})

    for page in pages:
        resolved = normalize_lists(wrap_figures(resolver.resolve(page.body, page)))
        md.reset()
        page.html = md.convert(resolved)
        page.toc = md.toc
        page.summary = summaries.get(page.title.lower()) or derive_summary(page)

    # Backlinks aus den gesammelten Kanten
    incoming: dict[str, list[Page]] = defaultdict(list)
    for page in pages:
        for target in page.outgoing:
            if target != page.title:
                incoming[target].append(page)

    # Schreiben
    PAGES_DIR.mkdir(parents=True, exist_ok=True)
    for stale in PAGES_DIR.glob("*.html"):
        stale.unlink()

    search_index = []
    for page in pages:
        out = render_page(page, pages, incoming.get(page.title, []), resolver)
        write(PAGES_DIR / f"{page.slug}.html", out)

        text = strip_html(page.html)
        tags = page.meta.get("tags") or []
        if isinstance(tags, str):
            tags = [tags]
        search_index.append({
            "t": page.title,
            "u": f"p/{page.slug}.html",
            "c": CATEGORY_LABEL[page.category],
            "g": " ".join(as_text(t) for t in tags),
            "s": page.summary[:140],
            # Nur der Originaltext wird ausgeliefert; die Kleinschreib-Variante
            # baut search.js einmalig beim Laden (halbiert die Indexgroesse).
            "raw": text[:4000],
        })

    broken_total = sum(len(v) for v in resolver.broken.values())
    write(SITE / "index.html", render_home(pages, summaries, len(resolver.broken)))
    write(SITE / "style.css", STYLE.strip() + "\n")
    write(SITE / "search.js", SEARCH_JS.strip() + "\n")
    # Als .js statt .json: fetch() auf lokale JSON-Dateien blockiert Chrome
    # unter file:// per CORS, ein <script src> laedt dagegen problemlos.
    write(SITE / "search-index.js",
          "window.SEARCH_INDEX=" + json.dumps(search_index, ensure_ascii=False) + ";\n")

    # ---- Report ----------------------------------------------------------- #
    by_cat: dict[str, int] = defaultdict(int)
    for p in pages:
        by_cat[p.category] += 1
    print("  " + ", ".join(f"{CATEGORY_LABEL[c]}: {by_cat[c]}"
                           for c, _ in CATEGORIES if by_cat.get(c)))

    if resolver.broken:
        print(f"\n  {len(resolver.broken)} unaufgeloeste Linkziele "
              f"({broken_total} Vorkommen) — im Text grau markiert:")
        for name in sorted(resolver.broken)[:15]:
            src = sorted(resolver.broken[name])
            more = f" (+{len(src) - 3})" if len(src) > 3 else ""
            print(f"    · {name}  ←  {', '.join(src[:3])}{more}")
        if len(resolver.broken) > 15:
            print(f"    … und {len(resolver.broken) - 15} weitere")

    titles = {p.title.lower() for p in pages}
    missing = sorted(t for t in listed if t not in titles)
    unlisted = sorted(p.title for p in pages
                      if p.title.lower() not in listed and p.category != "meta")
    if missing or unlisted:
        print("\n  Drift zwischen wiki/index.md und Dateibestand:")
        if unlisted:
            print(f"    nicht im Index gelistet ({len(unlisted)}): {', '.join(unlisted[:8])}"
                  + (" …" if len(unlisted) > 8 else ""))
        if missing:
            print(f"    im Index, aber keine Datei ({len(missing)}): {', '.join(missing[:8])}"
                  + (" …" if len(missing) > 8 else ""))

    orphans = [p.title for p in pages
               if not incoming.get(p.title) and p.category not in ("meta",)]
    if orphans:
        print(f"\n  {len(orphans)} verwaiste Seiten (keine eingehenden Links): "
              f"{', '.join(sorted(orphans)[:8])}" + (" …" if len(orphans) > 8 else ""))

    print(f"\n  ✓ {len(pages)} Seiten gebaut → {SITE / 'index.html'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
