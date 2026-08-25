# Gedanken 2.0 — Wissenssystem + autonomer Handelsalgorithmus

> Diese Datei ist deine aktive Projektinstruktion. Seit 2026-08-08 ist sie die Weiterentwicklung
> der Vorgängerfassung `CLAUDE.2.0.md` (im Repo-Root, unverändert als Rollback-Punkt erhalten;
> die Fassung davor liegt als `CLAUDE.1.0.md` ebenso unverändert daneben) — sie hält fest, was
> gegenüber 2.0 an Arbeitsweise, Standards und Zielbild dazugekommen ist. Diese Fassung läuft
> aktuell in der Testphase; bei Bedarf lässt sich `CLAUDE.2.0.md` einfach zurück auf `CLAUDE.md`
> benennen.

## Sprache

Antworte in diesem Projekt immer auf Deutsch, unabhängig von der Sprache der
Nutzereingabe — gilt für Chat-Antworten und Berichte, nicht für Code selbst
(Bezeichner/Kommentare folgen den üblichen Code-Konventionen).

## Antwortlänge

Berichte Routineaufgaben knapp: Ergebnis, Zahl, eine Zeile Begründung. Details folgen auf
Nachfrage. Routine sind Datennachlad, Einsortieren, Ingest, Statusabfragen und Wiki-Pflege.

Berichte ausführlich, wo Kürze ein Korrektheitsrisiko wäre: Backtest-Ergebnisse,
Datenqualitätswarnungen und alles mit Zahlen-Auswirkung auf den Algo. Nenne dort Methode,
Datenbasis, Stichprobengröße und `dubious_pct` mit — auch ungefragt.

## Autonomie

Handle ohne Rückfrage bei Ingest und beim Einsortieren loser Dateien in `raw/`. Frag bei allem
Übrigen nach. Die harte Sperre für Live-Handel mit echtem Geld aus der IBKR-Roadmap bleibt in
jedem Fall bestehen und wird von dieser Regel nicht gelockert.

## Session-Start

Gib zu Beginn jeder Session ungefragt drei Zeilen aus, bevor du mit der eigentlichen Aufgabe
beginnst:

```
raw/:  <lose Dateien -> wohin einsortiert / "nichts offen">
Daten: <NQ/ES 1s-Abdeckung bis Datum | Lücken oder "keine">
Offen: <PLAN-Backlog in Stichworten | Stand Gedanken-Clone>
```

Quellen: `python tools/sort_marktdaten.py --quiet` und `tools/sort_bilder.py --quiet` für
Zeile 1, `raw/marktdaten/1s-abdeckung.csv` für Zeile 2, `algo/PLAN.md` für Zeile 3.

**Die Statuszeile berichtet, sie repariert nicht.** Findest du eine Datenlücke, melde sie —
geschlossen wird sie erst auf Ansage (siehe `## Autonomie`). Einzige Ausnahme ist das
Einsortieren loser Dateien, das ohnehin autonom läuft. Findest du nichts, schreibe „nichts
offen" statt die Zeile wegzulassen: eine fehlende Zeile ist nicht von einer vergessenen
Prüfung zu unterscheiden.

## Layer 0 — Übergeordnetes Ziel: autonomer IBKR-Handelsalgorithmus

Verfolge als Ziel von allem in diesem Repo einen Handelsalgorithmus für NQ und ES, der
selbstständig und allein über Interactive Brokers handelt. Behandle Wiki-System, Datenpflege
und Backtesting als **Unterbau für dieses eine Ziel**, nicht als eigenständige Ziele — bei
einem Zielkonflikt entscheide zugunsten des Algo-Ziels.

> Die vollständigen Algo-Standards (Arbeitsstandards, IBKR-Roadmap, Protokollartefakte,
> Domänenkontext) stehen in [`algo/CLAUDE.md`](algo/CLAUDE.md) und laden automatisch, sobald
> du eine Datei in `algo/` anfasst. Arbeitest du am Algo, lies sie zuerst.

## Layer 1 — `raw/` (Inhalt unveränderlich, Ordnerstruktur von dir gepflegt)

In `raw/` liegen Rohquellen nach Themenbereich sortiert. Lies daraus, ändere Dateiinhalte hier
**nie**. Die Ordnerstruktur darfst du dagegen pflegen: siehe „Automatische Einsortierung" unten.

```
raw/
  trading-ict/
    Core Content/     ICT-Trading-Notizen (Notion-Export), unangetastet
    2026/              Weitere ICT-Notizen (2026er Jahrgang)
    assets/            Chart-/Screenshot-PNGs, per Obsidian-Wikilink referenziert
  journal/            Trading-Logbuch (Notion-Export): Daily Bias / Weekly Bias /
                        Trade Execution / Tape Reading, Juni 2025 – 2026
    Journal.md         Notion-Datenbanktabelle: alle Einträge mit Datum, Bias, Tags
    assets/            Screenshots; kollidierende Namen tragen das Präfix "journal-"
  marktdaten/          OHLC-Rohdaten für den Algo (siehe Layer 0), TradingView-Exporte +
                        yfinance-Nachlad + IBKR-1s-Anbindung (NQ/ES, `algo/fetch_ibkr.py`),
                        Jahr/Monat/Tag verschachtelt — **wie Gold behandeln**,
                        siehe algo/CLAUDE.md
  algo-pruefung/       Ergebnisse/Reports aus Algo-Prüfläufen, die lose in raw/ abgelegt wurden
                        (siehe „Automatische Einsortierung" unten) — reine Backtest-Artefakte
                        gehören sonst nach `algo/`, nicht hierher
  <neue-domäne>/       Weitere Themenbereiche entstehen hier bei Bedarf, z.B.
                        raw/gesundheit/, raw/buch-xyz/, raw/firma-abc/
```

> ⚠️ **Halte Bildnamen vault-weit eindeutig.** Obsidian *und* `tools/build_site.py` lösen
> `![[bild.png]]` allein über den Dateinamen auf — zwei gleichnamige Bilder in verschiedenen
> Ordnern führen dazu, dass stillschweigend das falsche angezeigt wird. Notion-Exporte liefern
> generische Namen (`image 1.png`, `image 2.png`, …) und kollidieren daher zwangsläufig. Lege
> beim Ingest eines neuen Exports Assets in den Domänenordner und versieh kollidierende Namen
> mit einem Domänen-Präfix.

Der Nutzer legt neue Rohquellen (Artikel, PDFs, Notizen, Screenshots) hier ab, thematisch in
einem eigenen Unterordner pro Domäne. Beginnt eine neue Domäne, lege den Ordner an, ohne extra
nachzufragen — folge dem gleichen Muster wie `trading-ict/`.

### Automatische Einsortierung

Der Nutzer legt neue Dateien gelegentlich direkt auf Root-Ebene von `raw/` ab (nicht in einem
Domänen-Unterordner), statt sie selbst einzusortieren. Erledige das für ihn:

- **Trigger**: Prüfe zu Beginn jeder neuen Session bzw. Aufgabe kurz, ob lose Dateien direkt in
  `raw/` liegen (nicht in einem `raw/<domäne>/`-Unterordner). Sortiere sie **zuerst ein**, bevor
  du mit der eigentlichen Aufgabe weitermachst — ohne nachzufragen.
- **Zuordnung**: Lies die Datei kurz an (Titel/Metadaten/erste Zeilen, bei Bildern Dateiname und
  ggf. visuelle Prüfung) und verschiebe sie in die inhaltlich passende bestehende Domäne, in
  deren dort übliche Unterstruktur. Passt keine bestehende Domäne, lege `raw/<neue-domäne>/` nach
  dem etablierten Muster an. Konkrete Fälle aus deinem Trading-/Algo-Workflow:
  - **OHLC-CSVs** (neue Marktdaten-Exporte) → `marktdaten/`, Jahr/Monat/Tag-Ordner. Symbol/
    Timeframe/Datum aus Dateinamen ableiten, wie beim bestehenden TradingView-Export-Muster;
    ist der Dateiname uneindeutig, zusätzlich erste/letzte Zeile der CSV auf das Datum prüfen.
  - **TradingView-Chart-Screenshots** (Setup-/Bias-Aufnahmen) → `journal/assets/`, analog zu
    bestehenden Journal-Screenshots; Datumsbezug im Dateinamen übernehmen, falls erkennbar.
  - **Algo-Prüfergebnisse/Backtest-Reports**, die als Datei in `raw/` abgelegt werden →
    `algo-pruefung/`. Gehört ein Artefakt eigentlich zur laufenden Backtest-Pipeline (kein
    Rohquellen-Charakter), weise stattdessen aktiv darauf hin, dass es besser nach `algo/` gehört,
    statt es unter `raw/` einzusortieren.
- **Namenskollisionen**: Behandle sie wie beim Ingest (siehe Bildnamen-Hinweis oben) — Domänen-
  Präfix statt Überschreiben.
- **Unklare Fälle**: Bist du dir bei der Zuordnung nicht sicher, lass die Datei liegen und melde
  das **aktiv** im Bericht, statt zu raten.
- **Bericht**: Liste nach dem Einsortieren kurz auf, was wohin verschoben wurde und was liegen
  geblieben ist.
- **Kein automatischer Ingest**: Einsortieren verschiebt die Datei nur an den richtigen Ort in
  `raw/`. Ob sie zusätzlich ins Wiki eingearbeitet wird, bleibt ein separater Schritt nach den
  bestehenden Ingest-Regeln unten.

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

Lege für neue Domänen (nicht-Trading) bei Bedarf eigene Top-Level-Unterordner in `wiki/` mit
passenden Kategorien an (z.B. `wiki/gesundheit/`, mit eigenen Konzept-/Entitäts-Seiten) — das
obige Schema ist das Trading-spezifische Beispiel, kein starres Gesetz.

### Seitenkonventionen

- Nutze den Dateinamen als Seitentitel, z.B. `wiki/concepts/Order Block.md`.
- Vergib `wiki/sources/`-Seiten **nicht** denselben Dateinamen wie ihrer `raw/`-Quelle (sonst
  sind Obsidian-Wikilinks zwischen Original und Zusammenfassung mehrdeutig). Hänge stattdessen
  den Suffix `(Source)` an, z.B. `raw/trading-ict/Core Content/Essentials To ICT Daytrading.md`
  → `wiki/sources/Essentials To ICT Daytrading (Source).md`.
- Gib jeder Seite YAML-Frontmatter mit:
  ```yaml
  ---
  tags: [concept, ict, liquidity]
  created: 2026-08-01
  updated: 2026-08-01
  sources: ["[[Essentials To ICT Daytrading]]"]
  ---
  ```
- Verlinke mit Obsidian-Wikilinks: `[[Seitenname]]`. Verlinke großzügig — auch auf Seiten, die
  noch nicht existieren (das markiert eine Lücke, keinen Fehler).
- Markiere Widersprüche zwischen **Primärquellen** im Text, statt sie still zu überschreiben,
  z.B. `> ⚠️ Widerspruch zu [[Andere Quelle]]: dort wird X behauptet, hier Y.` Wende das nur bei
  zwei gleichwertigen Lehrmeinungen an (z.B. zwei ICT-Vorlesungen). Wende es **nicht** auf eigene
  Backtest-Funde an — siehe [`algo/CLAUDE.md`](algo/CLAUDE.md), dort gilt eine bewusste Ausnahme
  (Löschen statt Markieren).
- Binde Bilder aus `raw/trading-ict/assets/` direkt per `![[bilddatei.png]]` ein (Obsidian löst
  Wikilinks vault-weit nach Dateinamen auf, der Ordnerpfad ist egal).

## Layer 3 — `site/` (generiert, nie von Hand bearbeiten)

Bearbeite `site/` nie von Hand — es ist eine statische, wikipedia-artige HTML-Ansicht des
`wiki/`-Layers, erzeugt von `tools/build_site.py`. Öffne `site/index.html` im Browser für die
lokale Nutzung.

```
site/
  index.html          Startseite: alle Seiten nach Kategorie, mit Kurzbeschreibung
  p/<slug>.html       Eine Seite pro Wiki-Seite
  style.css           Light/Dark, Serifen-Lesespalte, Sidebar
  search.js           Clientseitige Volltextsuche (Tastenkürzel: / oder Strg+K)
  search-index.js     Suchindex (bewusst .js statt .json — file:// blockiert fetch auf JSON)
```

Der Generator verarbeitet das Wiki so:

- **Wikilinks** löst er wie Obsidian vault-weit über den Dateinamen auf, inklusive Alias
  (`[[Seite|Kurzform]]`). Zeigt ein Link auf eine Rohquelle `X`, greift automatisch die
  Wiki-Seite `X (Source)`.
- **Bilder** kopiert er nicht, sondern referenziert sie relativ nach `raw/` — das hält `site/`
  bei ~2 MB statt 190 MB. Eine `![[bild.png]]`-Zeile plus direkt folgende `*Kursivzeile*` wird
  zu `<figure>` mit Bildunterschrift.
- **Backlinks** („Was zeigt hierher") erzeugt er automatisch pro Seite.
- **Unauflösbare Links** lassen den Build nicht abbrechen — er markiert sie grau und listet sie
  am Ende auf; sie sind laut Seitenkonvention gewollte Lücken.

Lösche `site/` jederzeit und erzeuge es neu — der Build ist reproduzierbar. Installiere die
Abhängigkeiten mit `python -m pip install -r tools/requirements.txt` (nur `markdown` + `pyyaml`).

## Versionskontrolle

Das gesamte Vault liegt in einem privaten Git-Repo (`raw/` inkl. aller PNGs, `wiki/`, `site/`,
`algo/`). Versioniere abgeleitete Artefakte (`graphify-out/`), den Notion-Export-ZIP,
maschinenlokale Configs, transiente Live-Daten (`algo/live/*/`) und Secrets
(`algo/.secrets.yaml`) **nicht** — siehe `.gitignore`.

`.\push.ps1 [-Message "..."] [-NoPush]` ist der einzige Weg, Änderungen zu veröffentlichen: Build →
`git add -A` → Commit → Push. Schlägt der Build fehl, entsteht kein Commit. Gibt es nichts zu
committen, endet das Skript ohne Leer-Commit. Beachte: `push.ps1` deckt nur das Wiki/Site-Artefakt ab —
Code-Änderungen in `algo/`/`tools/` werden mitcommittet, aber nicht separat validiert (kein CI).
Führe vor sicherheitsrelevanten Änderungen (IBKR-Keys, Order-Ausführung) den eigenen
Review-Schritt aus, siehe unten.

## Kontinuierliches Wachstum (autonom, nicht nur beim Ingest)

Erweitere das Wiki **laufend, in jeder Session** — nicht nur bei explizitem "ingest" oder
"importiere". Übernimm jede neue Erkenntnis, Regel oder Verbindung, die über den aktuellen
Chatverlauf hinaus Wert hat, **sofort** ins Wiki, sobald sie während irgendeiner Aufgabe
(Backtest, Debugging, Rückfrage, Korrektur des Nutzers, Recherche) entsteht — nicht erst auf
Nachfrage. Wende das auf neue Fakten genauso an wie auf Korrekturen bestehender Seiten. Wende
für `algo/`-spezifische Erkenntnisse (neue Trading-These, Backtest-Ergebnis, Bugfix mit
Zahlen-Auswirkung) zusätzlich das strengere Protokoll unter [`algo/CLAUDE.md`](algo/CLAUDE.md)
an — dort ist Loggen nicht optional, sondern Standardverfahren.

- **Strukturiere rein logisch**: Platziere neue Erkenntnisse an der Stelle, die die bestehende
  Kategorie-Struktur (`concepts/`, `models/`, `sources/`, `synthesis/`, plus Domänen-eigene
  Unterordner) vorsieht — kein loses Sammelbecken, keine Datei "Sonstiges" oder "Notizen". Passt
  keine bestehende Seite, lege eine neue in der passenden Kategorie an und verlinke sie in
  `wiki/index.md`, nach denselben Seitenkonventionen wie beim Ingest (Frontmatter, Wikilinks,
  Widerspruchsmarkierung, Verlinkung mit verwandten Seiten).
- Hänge jeder Erweiterung einen `wiki/log.md`-Eintrag an (passender Typ, z.B. `synthesis`,
  `query`, oder ein neuer treffender Typ), damit nachvollziehbar bleibt, wann und warum eine
  Seite entstand oder sich änderte.
- Lass Push (`.\push.ps1`) weiterhin nur **manuell** auslösen — das übernimmt der Nutzer selbst (siehe
  Versionskontrolle); einzige Ausnahme ist Ingest-Schritt 7, den du dort selbst ausführst. Sei
  autonom beim *Schreiben* ins Wiki, nicht beim Veröffentlichen.

## Lernpfad — Statusseite `briefings/status.md`

`briefings/status.md` ist die nach außen gerichtete Fortschrittsseite des Quant-Lernpfads: Sie
soll jemandem, der den Kontext nicht kennt, in einer Minute sagen, wo das Projekt steht und was
als Nächstes ansteht. Sie trägt kein Datum im Namen, hält immer nur den aktuellen Stand und wird
vollständig überschrieben.

**Schreibe sie ungefragt neu, sobald sich der Fortschritt ändert** — also immer dann, wenn du in
derselben Session eine dieser Dateien angelegt oder geändert hast:

- `wiki/lernpfad/tagebuch/Lernpfad JJJJ-MM-TT Xx.md` (Status, Minuten, Karten, die drei Felder)
- `wiki/lernpfad/Lernpfad — Meilensteine.md` (ein `- [ ]` wird zu `- [x]`)
- `wiki/lernpfad/Lernpfad — Woche NN.md` (Wochenplanung angelegt oder verschoben)
- `wiki/lernpfad/Lernpfad Quant — Übersicht.md` (Phase oder Plan geändert)

Erwähne die Aktualisierung im Bericht mit einer Zeile, frag nicht vorher nach. Ändert sich nichts
am Lernpfad, fass die Datei nicht an. Zusätzlich schreibt der Task `abend-briefing` sie jeden
Abend um 21:00 neu — das ist das Netz, nicht der Normalfall.

Aufbau (Frontmatter `titel`, `stand: JJJJ-MM-TT`, `typ: projektstatus`):

1. **Worum es geht** — zwei, drei Sätze zum Ziel des Lernpfads.
2. **Phase & Meilensteine** — laufende Phase, nächster offener Meilenstein mit Fälligkeit und
   verbleibenden Wochen, darunter die abgehakten.
3. **Pensum & Streak** — erledigte Blöcke der letzten 7 Tage (`teilweise` zählt halb), geleistete
   gegen geplante Minuten, ein Satz Einordnung.
4. **Diese Woche** — Blöcke und Themen der laufenden Woche, Erledigtes markiert.
5. **Aus dem Lerntagebuch** — die letzten drei Lerntage mit „Gelernt", „Hängengeblieben",
   „Hier weiter".
6. **Als Nächstes** — was in den kommenden Tagen ansteht.

Schreib für Außenstehende: keine Vault-Pfade, keine Kalender-IDs, keine internen Kürzel, jeder
Fachbegriff beim ersten Auftreten kurz erklärt. Fehlt ein Feld, schreib „keine Notiz" hin, statt
etwas zu erfinden. Keine Bewertungen, keine Motivationssprache.

Veröffentlicht wird wie immer nur manuell über `.\push.ps1` — schreiben ja, pushen nein.

## Operationen

### Ingest (neue Quelle verarbeiten)

1. Lies die Quelle (aus `raw/`) — **inklusive aller eingebetteten Bilder und PDFs**: Sieh dir
   jedes PNG/JPG tatsächlich an (das Read-Tool rendert Bilder visuell, nicht nur als Dateiname),
   und lies jede PDF-Seite. Übernimm Text, Diagramme, Zahlen und Chart-Markierungen aus Bildern
   wörtlich bzw. sinngemäß ins Wiki, wenn sie inhaltlich relevant sind — bei vielen
   Notion-Exporten steckt der Content überwiegend in den Screenshots, nicht im Fließtext. Ist ein
   Bild nicht lesbar (zu unscharf, abgeschnitten, reines Rauschen, Wasserzeichen-verdeckt): sag
   das **explizit** ("ich kann das nicht sehen"), statt zu raten oder das Bild stillschweigend
   zu überspringen.
2. Arbeite die Kernaussagen heraus (was ist neu, was wichtig, was widerspricht Bestehendem) —
   bespreche das **nicht vorab, sondern berichte es am Ende**.
3. Lege eine Seite unter `wiki/sources/<Quellname>.md` an: Zusammenfassung, Kernpunkte,
   Zitate/Verweise auf `raw/`-Original.
4. Lege relevante `wiki/concepts/`- und `wiki/models/`-Seiten an oder aktualisiere sie, setze
   Querverweise.
5. Aktualisiere `wiki/index.md` (neue Seiten eintragen).
6. Hänge einen Eintrag an `wiki/log.md` an.
7. **Führe `.\push.ps1 -Message "<typ> | <worum ging es>"` am Ende der Session selbst aus** —
   das baut die HTML-Website neu, erstellt einen Checkpoint-Commit und pusht ins private
   Repo. Ein Aufruf pro Session genügt, nicht einer pro Ingest. Ohne diesen Schritt ist der
   Ingest nicht abgeschlossen; frag **nicht erst nach**. `push.ps1` verweigert seit
   2026-08-16 den Dienst ohne `-Message` — die Git-Historie ist die Chronik des Projekts,
   siehe `## log.md`-Format.

**Arbeite ohne Rückfragen, im Batch.** Behandle eine Aufforderung wie „injeziere den neuen
Kontent" oder „importiere" als vollständige Freigabe für alles, was an neuem Material vorliegt —
nicht nur für eine Quelle. Frag nicht nach, welche Quelle zuerst drankommt oder was betont werden
soll; arbeite einfach durch und berichte am Ende. Bei einem Batch genügt ein einziger
`push.ps1`-Aufruf am Ende.

Triff Entscheidungen, die sonst eine Rückfrage wären, selbst — nach den Konventionen dieses
Vaults — und lege sie **im Bericht sowie in `wiki/log.md` offen**, insbesondere:

- **Widerspruch zu einer Bestandsseite**: Markiere ihn, statt still zu überschreiben (siehe
  Seitenkonventionen). Bestätigt eine neue Quelle eine bislang offene Frage, stelle den Marker
  von `⚠️` auf `✅` um und schreibe die Begründung dazu, statt ihn zu löschen.
- **Große Exporte**: Gib kollidierenden Bildnamen ein Domänen-Präfix. Sind es zu viele Bilder für
  durchgehend sprechende Namen, nummeriere sie seiten- und positionsbezogen
  (`<Domäne> - <Seitenkürzel> <NN>.png`) und lege die Beschreibung in die Bildunterschrift der
  Wiki-Seite. Vermerke die Abweichung im Log.
- **Leere oder reine Container-Seiten** im Export: Lege sie nicht als Rohdateien an, sondern
  falte sie in die Index-Datei der Reihe und kennzeichne sie als leer.

### Query (Frage beantworten)

1. Lies `wiki/index.md`, um relevante Seiten zu finden.
2. Lies relevante `wiki/`-Seiten (und bei Bedarf `raw/`-Originale). Betrifft die Frage den
   aktuellen/zukünftigen Marktstand: Beantworte sie **nicht** aus `raw/marktdaten/` oder einem
   älteren Live-Lauf, siehe [`algo/CLAUDE.md`](algo/CLAUDE.md) → Frische Daten.
3. Synthetisiere die Antwort, mit Verweisen auf Quellseiten.
4. Hat die Antwort eigenständigen Wert (Vergleich, Analyse, neue Verbindung): Biete dem Nutzer
   an, sie als neue Seite unter `wiki/synthesis/` abzulegen, damit sie ins Wiki einfließt, statt
   im Chatverlauf zu verschwinden.

### Lint (Wiki-Gesundheitscheck)

Suche auf Anfrage Widersprüche zwischen Seiten, markiere veraltete Aussagen, finde verwaiste
Seiten (keine eingehenden Links), identifiziere erwähnte aber fehlende Konzept-Seiten, ergänze
fehlende Querverweise. Schlage Ergebnisse als Liste vor, lösche nicht automatisch.

Starte dafür `python tools/build_site.py`: der Build meldet ohne zusätzlichen Aufwand
unauflösbare Wikilinks, verwaiste Seiten und die Drift zwischen `wiki/index.md` und dem
tatsächlichen Dateibestand.

## `index.md`-Format

Gruppiere nach Kategorie (`## Concepts`, `## Models`, `## Sources`, `## Synthesis`), pro Zeile:
`- [[Seitenname]] — Ein-Zeilen-Zusammenfassung (Datum)`

## `log.md`-Format

Seit 2026-08-16 trägt die **Git-Historie** den chronologischen Verlauf (`git log`), nicht mehr
`wiki/log.md` — `push.ps1` erzwingt dafür eine aussagekräftige Commit-Message im Format
`<typ> | <worum ging es>`, z.B. `ingest | Essentials To ICT Daytrading`. Mögliche Typen:
`ingest`, `query`, `lint`, `synthesis`, `setup`, `fix` (auch für autonome Wiki-Erweiterungen
außerhalb eines formalen Ingest, siehe "Kontinuierliches Wachstum" oben). Alte, chronologische
Einträge bis 2026-08-16 im alten `## [Datum] typ | Titel`-Format stehen weiterhin in
`wiki/log-archiv-bis-2026-08.md` (append-only, nicht mehr fortgeführt).

`wiki/log.md` selbst ist seit 2026-08-16 **kein chronologisches Protokoll mehr**, sondern eine
kurze, nicht datierte Liste dessen, was keine Commit-Message ausdrückt: offene Fragen, bewusste
Abweichungen von den Konventionen, Widerspruchsmarker, die auf keiner Wiki-Seite unterkommen.
Setze einen neuen Widerspruchsmarker **zuerst auf die betroffene Wiki-Seite selbst**
(Seitenkonvention oben); trage in `wiki/log.md` nur ein, was sich keiner einzelnen Seite
zuordnen lässt (Beispiel: eine vault-weite Content-Lücke wie eine fehlende Konzeptseite).

## Domänenkontext: trading-ict

`raw/trading-ict/` enthält ICT-(Inner-Circle-Trader-)Konzepte zu Market Structure, Liquidity,
Order Blocks, IPDA-Datenbereichen und konkreten Trade-Modellen — vermutlich aus einem
Mentorship-/Kursexport (Notion). Diese Notizen sind bereits recht dicht: Extrahiere beim Ingest
pro Datei mehrere verwandte Konzept-Seiten, statt 1:1 eine Quelle auf eine Seite abzubilden.
Terminologie-Fix: Nenne den kurzfristigen Retracement-Break im gesamten Vault **MSS (Market
Structure Shift)**, nicht CHoCH — CHoCH war eine ältere, mittlerweile korrigierte Bezeichnung.

## Algo-Trading

Siehe [`algo/CLAUDE.md`](algo/CLAUDE.md) — Arbeitsstandards, IBKR-Roadmap, Protokollartefakte
und Domänenkontext liegen dort und laden automatisch bei Zugriff auf `algo/`.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- For broad navigation use `wiki/index.md` (the curated catalog) rather than raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
