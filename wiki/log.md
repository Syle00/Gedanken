# Log

Chronologisches, append-only Protokoll. Neueste Einträge unten. Format siehe [[../CLAUDE.md]].

## [2026-08-01] setup | LLM-Wiki-Struktur initialisiert
- Bestehenden Vault-Inhalt (Core Content/, 2026/, 432 PNGs) nach raw/trading-ict/ verschoben
- CLAUDE.md, wiki/index.md, wiki/log.md angelegt

## [2026-08-01] ingest | Essentials To ICT Daytrading
- Quelle: raw/trading-ict/Core Content/Essentials To ICT Daytrading.md
- Seiten erstellt: wiki/sources/Essentials To ICT Daytrading (Source).md, wiki/concepts/ICT Daily Range Session Timing.md, wiki/concepts/New Week Opening Gap (NWOG) Bias.md
- Seiten aktualisiert: wiki/index.md
- Offene Anschlussfrage notiert: PD Array / Discount PD Array noch ohne eigene Konzept-Seite

## [2026-08-01] ingest | Batch: raw/trading-ict/ komplett (71 Core-Content-Dateien + 11 2026er-Dateien + FOMC)
- Auf explizite Anweisung ("injeziere den raw Ordner ins wiki") ohne Rückfragen pro Datei verarbeitet.
- Quellen: alle Dateien in raw/trading-ict/Core Content/ (71, inkl. der bereits ingesteten Essentials To ICT Daytrading), alle Dateien in raw/trading-ict/2026/ (11), sowie raw/Federal Open Market Committee.md.
- Übersprungen: raw/Where teams and agents work together.md (fehlgeschlagener Notion-Clip, kein Inhalt); raw/trading-ict/Core Content/Reeinforced Liquidity Pools -      When to anticipate Raids.md ist leer (0 Byte).
- Seiten erstellt: 36 neue wiki/concepts/-Seiten (u.a. PD Array, IPDA Data Ranges, Equilibrium Vs. Discount, Fair Value Gap (FVG), Order Block + Breaker/Rejection/Reclaimed/Mitigation-Varianten, AMD Cycle, SMT, Judas Swing, Turtle Soup, CISD, Quarterly Shift, COT Data, Seasonal Tendency, Market Reversal Types, Intermarket Relationships, Institutional Order Flow, Institutional Sponsorship, Open Float & Liquidity Pools, Low Resistance Liquidity Run, Central Bank Dealers Range (CBDR), Trendline Phantoms, Premium vs. Carrying Charge Market, sowie 2026er-Konzepte: BISI & SIBI, IFVG, Modell 22, Enigma FVG Projection, Chain of Custody, ICT Macros & Leading Candles, ORG & 1st Presented FVG, Event Horizon, FOMC).
- 20 neue wiki/models/-Seiten (u.a. One Shot One Kill Model, Market Maker Manipulation Templates, Classic Swing Trading Approach, Bread & Butter Setups, Weekly Range Trading Model, London Session Profiles, ICT Day Trade Routine, Bond/Commodity/Stock Mega-Trades, sowie 2026er-Modelle: No-Bias Engagement Routine, Missed Entry Trade Management Playbook, Trading Complex Opening Ranges, The Sentiment Effect, Trading Journal & DOL Checklist).
- 82 neue wiki/sources/-Seiten (eine pro Rohquelle, Month-1–11-Dateien als reine Curriculum-Sprunglisten markiert).
- Seiten aktualisiert: wiki/index.md (vollständig neu strukturiert mit allen Kategorien).
- Offene Punkte für nächsten Durchgang: unklare 2026er-Begriffe (VII, Suspensionblock, REH/REL, MSS) noch nicht vollständig definiert; Basics & Opening Range Concept nur Bild-Embeds ohne Text — siehe wiki/index.md "Offene Punkte" für Details.

## [2026-08-02] setup | Root-Aufräumung nach Obsidian-Vault-Integration
- Vault-Root (C:\Users\Jannes\Desktop\Gedanken) ist bereits der Obsidian-Vault (`.obsidian/` liegt dort) — keine Verschiebung nach `.obsidian/` nötig, das ist nur Obsidians Config-Ordner.
- 4 lose Screenshots im Root (image.png, image 1-3.png; ICT Monthly Mentorship Dezember 2016, "Reinforcing Orderblock Theory / Reclaimed Block", bisher nirgends im raw/-Bestand — kein "Month 12" in Core Content 2016.md) nach raw/trading-ict/assets/ verschoben und umbenannt (Namenskollision mit gleichnamigen, aber inhaltlich anderen Dateien im Zielordner vermieden): "ICT Mentorship Dez2016 - Reclaimed Block Market Maker Buy Model.png", "... Chart Example (Uptrend).png", "... Market Maker Sell Model.png", "... Chart Example (Downtrend).png".
- 2 leere Stub-Dateien im Root gelöscht (0 Byte, kein Inhalt): image 19.png.md, Reeinforced Liquidity Pools - When to anticipate Raids.md (Duplikat-Stub der bereits bekannten leeren Datei raw/trading-ict/Core Content/Reeinforced Liquidity Pools -      When to anticipate Raids.md, siehe Batch-Ingest-Eintrag oben).
- Zip 737cb9f5-...-ExportBlock-....zip (9.7MB, vermutlich Notion-Export) auf Nutzerwunsch unangetastet gelassen — noch nicht ausgepackt/gesichtet.
- Offener Punkt: Die 4 neuen Reclaimed-Block-Bilder sind reines raw-Material, noch nicht ins Wiki ingestet. Passende Konzept-Seite wäre vermutlich [[Reclaimed Block]] (bereits als Order-Block-Variante erwähnt, aber ohne eigene Vertiefung zu "Reinforcing"-Theorie) oder eine neue wiki/sources/-Seite für "ICT Monthly Mentorship Dezember 2016".

## [2026-08-02] lint | Curriculum-Zuordnung Monat 4 (Breaker Block)
- Nutzerhinweis: `Reeinforced Orderblock Theory    BreakerBlock` gehört ins Core Content, Monat 4.
- Seiten aktualisiert: wiki/sources/Reeinforced Orderblock Theory BreakerBlock (Source).md (Curriculum-Zeile → [[Month 04 (Source)]]), wiki/sources/Month 04 (Source).md (veralteter Stand "Breaker/Rejection/Reclaimed noch offen" korrigiert; jetzt vollständige Liste aller 6 Monat-4-Quellen mit ihren Konzept-Seiten).
- Offener Punkt: Die anderen 5 Monat-4-Quellen tragen noch keine eigene Curriculum-Rückverlinkung (nur die Sammelliste in Month 04).
