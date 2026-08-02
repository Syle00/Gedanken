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
    assets/            432 Chart-/Screenshot-PNGs, per Obsidian-Wikilink referenziert
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

## Operationen

### Ingest (neue Quelle verarbeiten)

1. Quelle lesen (aus `raw/`).
2. Mit dem Nutzer die Kernaussagen kurz besprechen (was ist neu, was wichtig, was widerspricht Bestehendem).
3. Seite unter `wiki/sources/<Quellname>.md` anlegen: Zusammenfassung, Kernpunkte, Zitate/Verweise auf `raw/`-Original.
4. Relevante `wiki/concepts/` und `wiki/models/` Seiten anlegen oder aktualisieren, Querverweise setzen.
5. `wiki/index.md` aktualisieren (neue Seiten eintragen).
6. Eintrag an `wiki/log.md` anhängen.

Standardmäßig eine Quelle nach der anderen, mit Rückfrage an den Nutzer, was betont werden soll.
Nur auf explizite Anweisung im Batch ohne Rückfragen verarbeiten.

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
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
