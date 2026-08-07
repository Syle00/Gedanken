# Gedanken 2.0 — Wissenssystem + autonomer Handelsalgorithmus

> Diese Datei ist deine aktive Projektinstruktion. Seit 2026-08-07 ist sie die Weiterentwicklung
> der Vorgängerfassung `CLAUDE.1.0.md` (im Repo-Root, unverändert als Rollback-Punkt erhalten) —
> wende zusätzlich zu 1.0 auch die hier neu hinzugekommene Arbeitsweise, Standards und Zielbild
> an. Vieles davon lag vorher nur in Cross-Session-Memory, nicht im Repo selbst. Diese Fassung
> läuft aktuell in der Testphase; bei Bedarf benenne einfach `CLAUDE.1.0.md` zurück zu
> `CLAUDE.md`.

## Sprache

Antworte in diesem Projekt immer auf Deutsch, unabhängig von der Sprache der
Nutzereingabe — gilt für Chat-Antworten und Berichte, nicht für Code selbst
(Bezeichner/Kommentare folgen den üblichen Code-Konventionen).

## Layer 0 — Übergeordnetes Ziel: autonomer IBKR-Handelsalgorithmus

**Verfolge als Ziel von allem in diesem Repo** — Wiki, `raw/marktdaten/`, `tools/analyze_ohlc.py`,
`algo/` — einen Handelsalgorithmus für MNQ, der **selbstständig und allein über Interactive
Brokers** (TWS/IB-Gateway-API) handelt. Baue keinen Signal-Geber für einen Menschen und betreibe
kein Backtesting als Selbstzweck — das Ziel ist eine laufende, autonome, profitable Ausführung mit
echtem Geld. Behandle alles andere in diesem Dokument (Wiki-System, Datenpflege, Backtesting) als
**Unterbau für dieses eine Ziel**, nicht als eigenständiges Ziel. Gewichte diese Priorität über
allen anderen Layern unten — bei einem Zielkonflikt (z.B. "schöneres Wiki" vs. "korrekterer
Backtest") entscheide zugunsten des Backtest-Ziels, siehe [[Algo-Trading: Arbeitsstandards]] unten.

Leite den Algorithmus über **echte, wachsende Datenbasis statt vorschneller Regeln** ab: baue aus
den täglich wachsenden OHLC-Daten in `raw/marktdaten/` einen regelbasierten, statistisch
validierten Handelsalgorithmus, der sich per IBKR-API selbstständig ausführt. Prüfe für den
aktuellen Umsetzungsstand, die Backlog-Punkte und das laufende Log `algo/PLAN.md` — dieses
Dokument dupliziert das nicht, sondern hält den *Rahmen* fest, in dem sich `algo/PLAN.md` bewegt.

Behandle das gesamte Wiki-System (Layer 1–3 unten) als Quelle für testbare Handelsregeln, weil
die ICT/SMC-Konzepte im Vault dafür da sind: Gilt eine Wiki-Seite wie [[Silver Bullet Model]] erst
dann als fertig verarbeitet, wenn du sie — sobald genug Daten vorliegen — als
`algo/rules.py`-Regel kodiert und gegen `raw/marktdaten/` gebacktestet hast. Behandle "Wissen
sammeln" und "Algo bauen" im Alltag als zwei verschränkte Tätigkeiten, nicht als getrennte
Projekte.

## Layer 1 — `raw/` (unveränderlich)

Sortiere Rohquellen nach Themenbereich. Lies daraus, ändere hier **nie** etwas.

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
                        yfinance-Nachlad, Jahr/Monat/Tag verschachtelt — **wie Gold behandeln**,
                        siehe [[Algo-Trading: Arbeitsstandards]]
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
  Backtest-Funde an — siehe [[Algo-Trading: Arbeitsstandards]], dort gilt eine bewusste Ausnahme
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
- **Backlinks** ("Was zeigt hierher") erzeugt er automatisch pro Seite.
- **Unauflösbare Links** lassen den Build nicht abbrechen — er markiert sie grau und listet sie
  am Ende auf; sie sind laut Seitenkonvention gewollte Lücken.

Lösche `site/` jederzeit und erzeuge es neu — der Build ist reproduzierbar. Installiere die
Abhängigkeiten mit `python -m pip install -r tools/requirements.txt` (nur `markdown` + `pyyaml`).

## Versionskontrolle

Das gesamte Vault liegt in einem privaten Git-Repo (`raw/` inkl. aller PNGs, `wiki/`, `site/`,
`algo/`). Versioniere abgeleitete Artefakte (`graphify-out/`), den Notion-Export-ZIP,
maschinenlokale Configs, transiente Live-Daten (`algo/live/*/`) und Secrets
(`algo/.secrets.yaml`) **nicht** — siehe `.gitignore`.

Veröffentliche Änderungen ausschließlich über `.\push.ps1 [-Message "..."] [-NoPush]`: Build →
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
Zahlen-Auswirkung) zusätzlich das strengere Protokoll unter [[Algo-Trading: Arbeitsstandards]]
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
  Versionskontrolle). Sei autonom beim *Schreiben* ins Wiki, nicht beim Veröffentlichen.

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
7. **Führe `.\push.ps1 -Message "ingest | <Quellname>"` selbst aus** — das baut die HTML-Website
   neu, erstellt einen lokalen Checkpoint-Commit und pusht ins private GitHub-Repo. Ohne diesen
   Schritt ist der Ingest nicht abgeschlossen. Das gehört zum Ingest dazu — frag **nicht erst
   nach**; bei einem Batch genügt ein Aufruf am Schluss.

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
   älteren Live-Lauf, siehe [[Algo-Trading: Arbeitsstandards]] → Frische Daten.
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

Mögliche Typen: `ingest`, `query`, `lint`, `synthesis`, `setup` (auch für autonome
Wiki-Erweiterungen außerhalb eines formalen Ingest, siehe "Kontinuierliches Wachstum" oben).

## Domänenkontext: trading-ict

`raw/trading-ict/` enthält ICT-(Inner-Circle-Trader-)Konzepte zu Market Structure, Liquidity,
Order Blocks, IPDA-Datenbereichen und konkreten Trade-Modellen — vermutlich aus einem
Mentorship-/Kursexport (Notion). Diese Notizen sind bereits recht dicht; beim Ingest lohnt es
sich, pro Datei mehrere verwandte Konzept-Seiten zu extrahieren statt 1:1 eine Quelle = eine Seite.
Terminologie-Fix: der kurzfristige Retracement-Break heißt im gesamten Vault **MSS (Market
Structure Shift)**, nicht CHoCH — CHoCH war eine ältere, mittlerweile korrigierte Bezeichnung.

## Algo-Trading: Arbeitsstandards

Diese Regeln sind für `algo/`, `tools/analyze_ohlc.py` und `raw/marktdaten/` **verbindlich**,
nicht optional — sie entstanden aus wiederholten Nutzerkorrekturen und gelten ab sofort ohne
erneute Nachfrage. Der lebende Implementierungsstand steht in `algo/PLAN.md` (Backlog + Log)
und `algo/README.md` (Modul-für-Modul-Doku); dieser Abschnitt hält die *Regeln* fest, nicht den
*Stand*.

**Zeit vor Preis.** Der Nutzer geht davon aus, dass ein oder mehrere Algorithmen den Preis zu
bestimmten Uhrzeiten steuern (ICT-These "Time before Price"). Eine leicht falsche Zeitzuordnung
macht jede Musteranalyse wertlos, selbst wenn die OHLC-Werte an sich stimmen — Preis-Ungenauigkeiten
sind zweitrangig, Zeit-Fehler nicht. Bei jeder Datenpipeline (Download, Resampling,
Zeitzonen-Konvertierung) Timestamps aktiv gegen eine unabhängige Quelle verifizieren (z.B.
bestehende TradingView-Exporte gegenprüfen), bevor Daten als fertig gemeldet werden.
Datetime64-Auflösung immer explizit über `.as_unit("s")` setzen, nie über manuelle Division —
ein stiller Pandas-Versionswechsel in der Auflösung (ns/us/s) ist genau der Fehlertyp, der hier
am meisten schadet (siehe `algo/fetch_yfinance.py`).

**Marktdaten wie Gold behandeln (Nulltoleranz).** Bei jedem Download, Import oder jeder
Bearbeitung von `raw/marktdaten/`: (1) Zeit gegen unabhängige Quelle geprüft? (2) Vollständig —
keine fehlenden Tage/Kerzen/Timeframes stillschweigend hingenommen, Lücken explizit aufgelistet?
Bei jedem Zweifel (Daten wirken fehlerhaft, lückenhaft, inkonsistent) **aktiv und ungefragt
Bescheid geben**, auch wenn der Rest der Aufgabe erledigt ist. Lieber einmal zu oft warnen als
einen fehlerhaften Datenpunkt durchrutschen lassen.

**Frische Live-Daten bei Zukunftsfragen.** Fragt der Nutzer nach dem aktuellen oder zukünftigen
Marktstand, **immer zuerst `python algo/live_status.py` neu ausführen** — nie auf zuvor
gelesene `raw/marktdaten/`-CSVs oder einen älteren Live-Lauf im selben Gespräch verlassen, auch
bei Wiederholung der Frage. Bekannte Grenze: yfinance kann bei MNQ=F/ES=F mehrere Stunden hinter
der echten NY-Zeit zurückliegen — liegt `price.t` >15-20 Min hinter der aktuellen NY-Zeit (bei
5m-TF), das aktiv melden statt die Daten stillschweigend als aktuell auszugeben.

**Ziel ist die volle Daily Range, nicht nur Bias.** Über reine Richtungsvorhersage (bullish/
bearish) hinaus: konkrete OHLC-Zielzonen für die Tagesrange benennen, gestützt auf PD Arrays
(Order Blocks, FVGs, NDOG/NWOG, Liquidity Pools), Session-Ranges (Asia/London/NY Killzones) und
wiederkehrende Zeitfenster-Muster. Explizit nach Mustern suchen, die auf algorithmisches
Verhalten hindeuten, und diese benennen statt nur Levels aufzulisten. NDOG/NWOG gelten dabei als
besonders relevante PD Arrays — bei jeder Analyse (insbesondere `/algo-live-status`) die
konkreten Opening-/Closing-Preise mit hinterlegen, nicht nur die Gap-Größe.

**Jede neue These wird automatisch geloggt und gebacktestet, ohne zu fragen.** Nennt der Nutzer
eine neue Trading-These oder Beobachtung (Frage oder Aussage), passiert unaufgefordert: (1)
Eintrag in `algo/PLAN.md`s Log-Tabelle, (2) wenn irgend möglich ein Backtest-Script dafür bauen
oder erweitern und gegen alle verfügbaren Daten in `raw/marktdaten/` laufen lassen (Reuse-first:
auf `tools/analyze_ohlc.py`-Detektoren und dem `find_days()`-Muster aufbauen, nicht jedes Mal
neu erfinden; ein eigener Dateiname `algo/backtest_<these>.py` pro These), (3) Ergebnis ehrlich
berichten, auch wenn es der Nutzer-These widerspricht — Zahlen werden nicht geschönt, um
Zustimmung zu simulieren. Grund: jede ICT-These ist im Rahmen dieses Projekts kein
Meinungsstück, sondern eine falsifizierbare Behauptung über ein Regelwerk, die geprüft werden
muss statt nur besprochen zu werden.

**Proaktiv gegenprüfen, offene Hypothesen halten, Falsifiziertes löschen.** Ständig
gegenprüfen und Vorschläge machen, nicht nur auf explizite Backtest-Aufträge reagieren — taucht
eine Zahl/These im Gespräch auf, aktiv prüfen statt zu warten. Unsichere Nutzeraussagen ("ich
weiß nicht genau, ob...") als offene Hypothese in der passenden `wiki/synthesis/`-Seite (Muster
"(laufend)" im Namen) festhalten und bei neuen Daten aktualisieren. **Bewusste Ausnahme von der
generellen Widerspruchsregel** (siehe Seitenkonventionen oben): eigene Backtest-Ergebnisse sind
keine zwei gleichwertigen Meinungen, sondern eine nachprüfbare Zahl — stellt sich ein früherer
Fund mit mehr Daten als Rauschen heraus, wird er **entfernt**, nicht als „⚠️ widerlegt"
stehengelassen. Ausdrücklich anders: eine vom Nutzer explizit als "weiter beobachten" markierte
These (z.B. die ORG-C.E.-70%-These, aktuell 35-43% im eigenen Backtest) bleibt trotz
widersprechender Zahlen aktiv bestehen und wird in jedem neuen Bericht kommentiert, statt als
erledigt/widerlegt abgehakt zu werden — der Nutzer entscheidet hier explizit gegen das
Standard-Löschverfahren.

**Korrektheit vor Features, weil reales Geld geplant ist.** Backtest-Code, der Zahlen liefert,
die nicht dem realen Kontrakt-P&L entsprechen (Notional-Prozent statt echtem Punktwert, geratene
statt konservativ aufgelöste Stop/Ziel-Reihenfolge in derselben Kerze, Lookahead-Bias,
Data-Leakage), hat **höchste Priorität** — vor neuen Strategien, vor Optik-/Dashboard-
Verbesserungen. Bei jedem neuen Backtest-Script oder jeder Erweiterung zuerst prüfen: (1) echter
Punktwert/Kontraktgröße statt Notional-Prozent, (2) konservative statt geratene Fill-Reihenfolge
bei Stop/Ziel in derselben Kerze (`dubious_pct` als Pflichtkennzahl in jedem Report), (3) kein
Lookahead in Signalen/Modellen (nur `bars[t<=when]`). Gefundene Bugs werden **direkt repariert**,
ohne vorherige Freigabeschleife pro Einzelfund — ein Bericht am Ende reicht. Optik-Wünsche (z.B.
"Bloomberg-Terminal-Look" für `dashboard.py`) sind explizit nachrangig und werden nur auf
separate Anfrage umgesetzt. `algo/selfcheck.py` bündelt die Regressions-Selbstchecks (`pnl`,
`rules`, `signals`, `backtest_ensemble`) — vor größeren Refactors laufen lassen.

**Marktdaten-Lücken nachträglich schließbar.** Fehlt in einem ingesteten Export ein Zeitabschnitt
(z.B. ein ganzer Monat in `raw/trading-ict/Core Content/`), vor dem Nachfragen beim Nutzer
prüfen, ob der YouTube-Kanal `@InnerCircleTrader` dieselben Inhalte als Video-Reihe hat
(Suchmuster `"ICT Mentorship Core Content - Month <NN>"`) — das `yt-ict-ingest`-Skill deckt den
technischen Ablauf ab.

## Algo-Trading: Roadmap zur IBKR-Anbindung

Reihenfolge, in der das Projekt sich Richtung Layer-0-Ziel bewegt — jede Stufe baut auf der
vorherigen auf, keine wird übersprungen:

1. **Datensammlung (laufend, nie abgeschlossen).** `raw/marktdaten/` wächst täglich
   (TradingView-Export + `algo/fetch_yfinance.py`-Nachlad), begrenzt durch yfinance-Limits
   (1m ~30 Tage, 5m/15m ~60 Tage, 1d unbegrenzt zurück). Mehr Historie in Intraday-Auflösung
   braucht perspektivisch eine zweite Datenquelle (Kandidat: IBKR selbst, sobald die
   API-Anbindung aus Punkt 4 steht — historische Daten und Live-Order-Ausführung über denselben
   Broker zu beziehen vermeidet Datenquellen-Drift zwischen Backtest und Live-Betrieb).
2. **Regel-Schicht (laufend).** Wiki-Konzepte (`wiki/models/`) werden zu deterministischen
   Python-Regeln (`algo/rules.py::plan_trade` als erstes Beispiel: Silver Bullet Model). Jede
   neue Regel folgt [[Algo-Trading: Arbeitsstandards]] — kein Lookahead, Reuse bestehender
   Detektoren aus `tools/analyze_ohlc.py`.
3. **Validierung (Standardwerkzeug für jede Regel, nicht optional).** Einzelbacktest
   (`backtest_bt.py`) reicht nicht — Parameter-Sensitivität, Walk-Forward (rollierende Folds,
   Out-of-Sample ohne Refit) und Monte-Carlo-Resampling (`validate.py`) laufen für jede Regel,
   bevor eine Zahl als belastbar gilt. Stress-Test gegen historische Krisenfenster
   (`stress_test.py`) für Verhaltenscharakterisierung unter Extrembedingungen. Erst wenn eine
   Regel hier über mehrere Verfahren hinweg konsistent (nicht zwingend profitabel, aber
   *verstanden*) abschneidet, ist sie reif für den nächsten Schritt.
4. **IBKR-Adapter, dünn und broker-unabhängig gehalten.** `algo/broker_ibkr.py` (noch nicht
   angelegt): Order-Ausführung über TWS/IB-Gateway-API (`ib_insync` oder offizielles `ibapi`)
   hinter einer schmalen Schnittstelle (`place_order`, `get_position`, `cancel`) — die
   Regel-Schicht bleibt broker-unabhängig, damit sie weiter isoliert testbar bleibt. Wird erst
   nach Punkt 2+3 begonnen, nicht parallel.
5. **Paper-Trading zuerst, ausnahmslos.** Der Adapter läuft zuerst gegen ein IBKR-Paper-Trading-
   Konto. Kein Übergang zu echtem Kapital ohne expliziten, gesonderten Freigabeschritt durch den
   Nutzer — das ist keine Formalie, sondern eine harte Sperre in diesem Projekt: Live-Handel mit
   echtem Geld wird nie stillschweigend aus einer anderen Aufgabe heraus aktiviert.
6. **Live-Betrieb, nach expliziter Freigabe.** Erst danach: laufende Ausführung, mit
   kontinuierlichem Monitoring (`algo/dashboard.py`-Nachfolger oder eigenes Live-Reporting) und
   demselben Korrektheits-Standard wie im Backtest (echter $-P&L, keine Notional-Näherung).

**Security-Gate.** Sobald echte IBKR-Keys ins Spiel kommen (spätestens Punkt 4), Secret-Scan von
"einmalig/gelegentlich" auf ein festes Intervall umstellen (mind. wöchentlich, vor jedem
Live-Übergang zwingend) — aktuell (Stand 2026-08-07) ohne Live-Keys unnötiger Aufwand, das
kippt aber mit dem ersten Broker-Zugangsdaten-File.

## Protokoll- und Datenartefakte

Damit "laufende Daten verbessern den Algo" ein Mechanismus bleibt, keine Absicht:

- `algo/PLAN.md` — Backlog + chronologisches Log (Datum, Ereignis) für alles, was in `algo/`
  passiert: neue Thesen, Backtest-Ergebnisse, Bugfixes mit Zahlen-Auswirkung. Primäres
  Protokoll für die Algo-Arbeit, feingranularer als `wiki/log.md`.
- `wiki/synthesis/*.md` mit `(laufend)` im Namen — aggregierte, sich mit wachsendem
  Datenbestand aktualisierende Auswertungsseiten (z.B. `Muster-Validierung (laufend).md`,
  `Statistische Muster jenseits der ICT-Konzepte (laufend).md`). Werden bei jedem neuen
  Backtest-Lauf überschrieben/erweitert, nicht als Schnappschuss stehen gelassen.
- `algo/seasonal_tendency.json` — versionierte Kennzahlen-Datenbank (Wochentag/Monat/
  Turn-of-Month/Woche-im-Monat), gedacht für Jahr-über-Jahr-Vergleiche statt Neuberechnung bei
  jeder Frage.
- `algo/README.md` — ein Abschnitt pro Modul (Was/Wie/Warum/bekannte Grenzen), gepflegt bei
  jeder inhaltlichen Code-Änderung, damit der Nutzer ohne Code-Lesen nachschlagen kann.
- `algo/live/<datum>/` + `algo/live/<datum>-status-log.md` — transiente Live-Ziehung
  (gitignored) plus versioniertes Text-Protokoll der `/algo-live-status`-Läufe.

## Domänenkontext: algo (MNQ-Backtesting)

`algo/` enthält den gesamten Backtesting-/Validierungs-Stack für Layer 0 (siehe `algo/README.md`
für die Modul-für-Modul-Doku, `algo/PLAN.md` für Stand/Backlog/Log). Kernkomponenten: `pnl.py`
(Punktwert-Präzisionsschicht), `rules.py`/`signals.py` (Regel-/Signal-Schicht),
`backtest_bt.py`/`backtest_ensemble.py` (Trade-Simulation), `validate.py`/`stress_test.py`
(Validierung), `live_status.py` (Live-Loop), `selfcheck.py` (Regressionscheck). Symbol-Punktwerte
aktuell: MNQ=$2, NQ=$20, ES=$50 — ein neues Symbol braucht einen neuen Eintrag in `pnl.py`, bevor
`real_pnl`/`risk_size` dafür nutzbar sind.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- For broad navigation use `wiki/index.md` (the curated catalog) rather than raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
