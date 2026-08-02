# Gedanken — LLM Wiki

Dies ist ein persönliches Wissenssystem nach dem "LLM Wiki"-Muster: eine unveränderliche
Rohquellen-Schicht (`raw/`) und eine von dir (dem LLM-Agenten) gepflegte, verlinkte
Wiki-Schicht (`wiki/`). Der Mensch kuratiert Quellen und stellt Fragen; du liest, verdichtest,
verlinkst und hältst das Wiki konsistent. Ziel ist ein kompoundierendes Wissenssystem, nicht
RAG-Retrieval bei jeder Frage.

## Layer 1 — `raw/` (unveränderlich)

Rohquellen, nach Themenbereich sortiert. Du liest daraus, du änderst hier **nie** etwas.

```
raw/
  trading-ict/
    Core Content/     ICT-Trading-Notizen (Notion-Export), unangetastet
    2026/              Weitere ICT-Notizen (2026er Jahrgang)
    assets/            453 Chart-/Screenshot-PNGs, per Obsidian-Wikilink referenziert
  <neue-domäne>/       Weitere Themenbereiche entstehen hier bei Bedarf, z.B.
                        raw/gesundheit/, raw/buch-xyz/, raw/firma-abc/
```

Neue Rohquellen (Artikel, PDFs, Notizen, Screenshots) legt der Nutzer hier ab, thematisch
in einem eigenen Unterordner pro Domäne. Wenn eine neue Domäne beginnt, lege den Ordner an,
aber frag nicht extra nach — folge dem gleichen Muster wie `trading-ict/`.

## Layer 2 — `wiki/` (von dir gepflegt)

```
wiki/
  index.md            Katalog aller Wiki-Seiten, nach Kategorie, mit 1-Zeilen-Zusammenfassung
  log.md               Chronologisches, append-only Änderungsprotokoll
  concepts/            Konzept-Seiten (z.B. "Order Block", "Liquidity Pool", "IPDA")
  models/               Setup-/Modell-Seiten (konkrete Trade-Modelle, z.B. "One Shot One Kill")
  sources/               Eine Seite pro ingesteter Rohquelle: Zusammenfassung + Kernpunkte + Link zur raw/-Datei
  synthesis/              Übergreifende Thesen, Vergleiche, offene Fragen, die mehrere Quellen verbinden
```

Für neue Domänen (nicht-Trading) entstehen bei Bedarf eigene Top-Level-Unterordner in `wiki/`
mit passenden Kategorien (z.B. `wiki/gesundheit/`, mit eigenen Konzept-/Entitäts-Seiten) —
das obige Schema ist das Trading-spezifische Beispiel, kein starres Gesetz.

### Seitenkonventionen

- Dateiname = Seitentitel, z.B. `wiki/concepts/Order Block.md`.
- `wiki/sources/`-Seiten dürfen **nicht** denselben Dateinamen wie ihre `raw/`-Quelle tragen
  (sonst sind Obsidian-Wikilinks zwischen Original und Zusammenfassung mehrdeutig). Konvention:
  Suffix `(Source)` anhängen, z.B. `raw/trading-ict/Core Content/Essentials To ICT Daytrading.md`
  → `wiki/sources/Essentials To ICT Daytrading (Source).md`.
- Jede Seite bekommt YAML-Frontmatter:
  ```yaml
  ---
  tags: [concept, ict, liquidity]
  created: 2026-08-01
  updated: 2026-08-01
  sources: ["[[Essentials To ICT Daytrading]]"]
  ---
  ```
- Verlinke mit Obsidian-Wikilinks: `[[Seitenname]]`. Verlinke großzügig — auch auf Seiten,
  die noch nicht existieren (das markiert eine Lücke, kein Fehler).
- Bei Widersprüchen zwischen Quellen: nicht stillschweigend überschreiben, sondern im Text
  markieren, z.B. `> ⚠️ Widerspruch zu [[Andere Quelle]]: dort wird X behauptet, hier Y.`
- Bilder aus `raw/trading-ict/assets/` können direkt per `![[bilddatei.png]]` eingebunden
  werden (Obsidian löst Wikilinks vault-weit nach Dateinamen auf, Ordnerpfad ist egal).

## Layer 3 — `site/` (generiert, nie von Hand bearbeiten)

Eine statische, wikipedia-artige HTML-Ansicht des `wiki/`-Layers, erzeugt von
`tools/build_site.py`. Gedacht für die lokale Nutzung: `site/index.html` im Browser öffnen.

```
site/
  index.html          Startseite: alle Seiten nach Kategorie, mit Kurzbeschreibung
  p/<slug>.html       Eine Seite pro Wiki-Seite
  style.css           Light/Dark, Serifen-Lesespalte, Sidebar
  search.js           Clientseitige Volltextsuche (Tastenkürzel: / oder Strg+K)
  search-index.js     Suchindex (bewusst .js statt .json — file:// blockiert fetch auf JSON)
```

Was der Generator aus dem Wiki macht:

- **Wikilinks** werden wie in Obsidian vault-weit über den Dateinamen aufgelöst, inklusive
  Alias (`[[Seite|Kurzform]]`). Zeigt ein Link auf eine Rohquelle `X`, greift automatisch die
  Wiki-Seite `X (Source)`.
- **Bilder** werden nicht kopiert, sondern relativ nach `raw/` referenziert — das hält `site/`
  bei ~2 MB statt 190 MB. Eine `![[bild.png]]`-Zeile plus direkt folgende `*Kursivzeile*` wird
  zu `<figure>` mit Bildunterschrift.
- **Backlinks** („Was zeigt hierher") entstehen automatisch pro Seite.
- **Unauflösbare Links** brechen den Build nicht ab, sondern werden grau markiert und am Ende
  aufgelistet — sie sind laut Seitenkonvention gewollte Lücken.

Der Build ist reproduzierbar: `site/` darf jederzeit gelöscht und neu erzeugt werden.
Abhängigkeiten: `python -m pip install -r tools/requirements.txt` (nur `markdown` + `pyyaml`).

## Versionskontrolle

Das gesamte Vault liegt in einem privaten Git-Repo (`raw/` inkl. aller PNGs, `wiki/`, `site/`).
Nicht versioniert werden abgeleitete Artefakte (`graphify-out/`), der Notion-Export-ZIP und
maschinenlokale Configs — siehe `.gitignore`.

`.\publish.ps1 [-Message "..."] [-NoPush]` ist der einzige Weg, Änderungen zu veröffentlichen:
Build → `git add -A` → Commit → Push. Schlägt der Build fehl, entsteht kein Commit. Gibt es
nichts zu committen, endet das Skript ohne Leer-Commit.

## Operationen

### Ingest (neue Quelle verarbeiten)

1. Quelle lesen (aus `raw/`).
2. Mit dem Nutzer die Kernaussagen kurz besprechen (was ist neu, was wichtig, was widerspricht Bestehendem).
3. Seite unter `wiki/sources/<Quellname>.md` anlegen: Zusammenfassung, Kernpunkte, Zitate/Verweise auf `raw/`-Original.
4. Relevante `wiki/concepts/` und `wiki/models/` Seiten anlegen oder aktualisieren, Querverweise setzen.
5. `wiki/index.md` aktualisieren (neue Seiten eintragen).
6. Eintrag an `wiki/log.md` anhängen.
7. **`.\publish.ps1 -Message "ingest | <Quellname>"` ausführen** — baut die HTML-Website neu,
   erstellt einen lokalen Checkpoint-Commit und pusht ins private GitHub-Repo. Ohne diesen
   Schritt ist der Ingest nicht abgeschlossen.

Standardmäßig eine Quelle nach der anderen, mit Rückfrage an den Nutzer, was betont werden soll.
Nur auf explizite Anweisung im Batch ohne Rückfragen verarbeiten. Bei einem Batch genügt ein
einziger `publish.ps1`-Aufruf am Ende.

### Query (Frage beantworten)

1. `wiki/index.md` lesen, um relevante Seiten zu finden.
2. Relevante `wiki/`-Seiten (und bei Bedarf `raw/`-Originale) lesen.
3. Antwort synthetisieren, mit Verweisen auf Quellseiten.
4. Wenn die Antwort eigenständigen Wert hat (Vergleich, Analyse, neue Verbindung): dem Nutzer
   anbieten, sie als neue Seite unter `wiki/synthesis/` abzulegen, damit sie ins Wiki einfließt
   statt im Chatverlauf zu verschwinden.

### Lint (Wiki-Gesundheitscheck)

Auf Anfrage: Widersprüche zwischen Seiten suchen, veraltete Aussagen markieren, verwaiste
Seiten (keine eingehenden Links) finden, erwähnte aber fehlende Konzept-Seiten identifizieren,
fehlende Querverweise ergänzen. Ergebnisse als Liste vorschlagen, nicht automatisch löschen.

Als Startpunkt dafür `python tools/build_site.py` laufen lassen: der Build meldet ohne
zusätzlichen Aufwand unauflösbare Wikilinks, verwaiste Seiten und die Drift zwischen
`wiki/index.md` und dem tatsächlichen Dateibestand.

## `index.md`-Format

Gruppiert nach Kategorie (`## Concepts`, `## Models`, `## Sources`, `## Synthesis`), pro Zeile:
`- [[Seitenname]] — Ein-Zeilen-Zusammenfassung (Datum)`

## `log.md`-Format

Append-only, neueste Einträge unten. Jeder Eintrag beginnt mit einem festen Präfix, damit er
mit einfachen Tools grep-bar bleibt:

```
## [2026-08-01] ingest | Essentials To ICT Daytrading
- Seiten erstellt: wiki/sources/Essentials To ICT Daytrading.md, wiki/concepts/IPDA.md
- Seiten aktualisiert: wiki/index.md
```

Mögliche Typen: `ingest`, `query`, `lint`, `synthesis`.

## Domänenkontext: trading-ict

`raw/trading-ict/` enthält ICT-(Inner-Circle-Trader-)Konzepte zu Market Structure, Liquidity,
Order Blocks, IPDA-Datenbereichen und konkreten Trade-Modellen — vermutlich aus einem
Mentorship-/Kursexport (Notion). Diese Notizen sind bereits recht dicht; beim Ingest lohnt es
sich, pro Datei mehrere verwandte Konzept-Seiten zu extrahieren statt 1:1 eine Quelle = eine Seite.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- For broad navigation use `wiki/index.md` (the curated catalog) rather than raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
