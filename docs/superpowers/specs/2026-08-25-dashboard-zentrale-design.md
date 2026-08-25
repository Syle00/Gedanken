# Dashboard „Zentrale" — Design

**Datum:** 2026-08-25
**Status:** Design abgenommen, Implementierung offen
**Umfang dieser Spec:** Schnitt 1 (Rahmen + Panels HEUTE und MARKT). Schnitt 2 (Agents) und
Schnitt 3 (Planung, Lernpfad) sind am Ende skizziert, aber nicht Teil dieser Spec.

## Ziel

Eine lokale Web-Oberflaeche, von der aus Jannes arbeitet und plant: Cowork-Briefing samt
Terminen, die Marktdaten des Handelstags, spaeter Agent-Laeufe und Planung. Sie liest und
schreibt ausschliesslich Dateien im Vault — dieselben Dateien, die Cowork, Obsidian und Claude
Code sehen.

Nicht-Ziele: Charts (dafuer TradingView), Mehrbenutzerbetrieb, Zugriff von aussen, mobile
Ansicht, eine eigene Datenhaltung neben dem Vault.

## Architektur

Zwei Dateien, keine neue Dependency:

- `tools/dashboard_serve.py` — stdlib `http.server`, `json`, `subprocess`. Bindet an
  `127.0.0.1:8787`. Start: `python tools/dashboard_serve.py`.
- `tools/dashboard.html` — eine Seite, Vanilla JS, kein Build-Schritt.

Drei Endpunkte:

| Endpunkt | Zweck |
|---|---|
| `GET /api/state` | Ein JSON-Blob mit allem, was die Panels brauchen. Frontend pollt alle 5 s und rendert neu. |
| `POST /api/write` | Schreibt eine Markdown-Datei im Vault (Pfad-Whitelist). |
| `POST /api/run` | Startet `claude -p "<prompt>"` als Subprozess, Log nach `.dashboard/runs/<id>.log`. |

**Alle drei Endpunkte entstehen in Schnitt 1** — sie sind zusammen keine 80 Zeilen und der
Briefing-Nachhol-Button braucht `/api/run` sofort. Was in Schnitt 2 und 3 dazukommt, sind
Panels, keine neue Serverlogik.

Bewusst kein Endpunkt pro Panel und kein Client-State: das Frontend haelt nichts, was es nicht
aus dem letzten `/api/state` neu bauen kann. Polling statt SSE — bei einem Nutzer auf localhost
ist der Unterschied ein paar Sekunden Log-Verzoegerung.

`.dashboard/` (transiente Run-Logs) gehoert in `.gitignore`, analog `algo/live/*/`.

### Antwortform von `/api/state`

Pro Panel ein Objekt mit `data`, `error`, `age_s`. Ein Fehler in einer Quelle darf die anderen
Panels nicht mitreissen:

```json
{
  "now": {"iso": "2026-08-25T07:14:00-04:00", "ny": "07:14", "weekday": "Dienstag"},
  "briefing": {"data": {}, "error": null, "age_s": 860},
  "markt":    {"data": {}, "error": "ForexFactory Timeout", "age_s": 4300},
  "daten":    {"data": {"nq_bis": "2026-08-24", "es_bis": "2026-08-24", "luecke_tage": 0},
               "error": null, "age_s": 0}
}
```

## Datenquellen

Alles Lesen aus vorhandenen Artefakten, nichts neu erfunden:

| Panel | Quelle | Schnitt |
|---|---|---|
| Briefing + Termine | `briefings/<datum>-{morgen,abend}.md` | 1 |
| Marktdaten (Levels, News, Bias) | `python algo/bias_levels.py` (JSON) + neueste `raw/journal/Daily Bias *.md` | 1 |
| Datenabdeckung (Kopfzeile) | `raw/marktdaten/1s-abdeckung.csv` | 1 |
| Cron-/Routine-Status | `.claude/commands/*.md` + Mtime der erzeugten Artefakte (`algo/live/`, `raw/journal/`) | 2 |
| Agent-Laeufe | `.dashboard/runs/*.log` + `~/.claude/projects/<slug>/` Transcripts | 2 |
| Skill-Katalog | `.claude/skills/*/SKILL.md` + `.claude/commands/*.md` Frontmatter | 2 |
| Quant-Lernpfad | `wiki/lernpfad/*.md` | 3 |

`bias_levels.py` zieht News ueber HTTP und braucht Sekunden. Deshalb Cache im Serverprozess mit
Mindestalter **15 min** — nicht bei jedem Poll aufrufen. Der Cache wird nie als aktuell
ausgegeben: `age_s` sagt immer, wie alt der Wert wirklich ist.

## Externe Voraussetzung: Cowork schreibt Dateien

Die Briefing-Texte liegen heute nur in der ChatGPT-Cowork-App, nicht im Vault. Damit das
HEUTE-Panel Inhalt hat, muessen die Cowork-Anweisungen „Daily briefing" und „Abend briefing" um
einen Satz erweitert werden:

> Schreibe das Briefing zusaetzlich nach `briefings/<JJJJ-MM-TT>-morgen.md` (bzw. `-abend.md`),
> inklusive der Termine des Tages als Liste.

Diese Aenderung nimmt Jannes in Cowork vor; sie ist nicht Teil der Implementierung. Ohne sie
zeigt das Panel korrekt „kein Briefing vorhanden" — das Dashboard ist dadurch nicht blockiert.

Format der Datei: Markdown mit Frontmatter, Termine als Liste unter `## Termine` im Format
`- HH:MM — Titel`. Der Parser ist absichtlich tolerant: fehlt der Abschnitt, bleibt die
Terminliste leer, der Fliesstext wird trotzdem angezeigt.

## Layout

Ein Bildschirm, CSS-Grid mit `auto-fit`, Panels als gleichartige Kacheln. Bis die Panels der
spaeteren Schnitte existieren, fuellen die vorhandenen die Breite — keine Sonderbehandlung.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  Dienstag, 25.08.2026 · NY 07:14        [Daten: NQ/ES bis 24.08. OK]  [5s]   │
├────────────────────────┬───────────────────────┬─────────────────────────────┤
│  HEUTE            (1)  │  MARKT           (1)  │  AGENTS              (2)    │
│ Morgen-Briefing 07:00  │ NQ  PDH 30.283,00     │ * algo-live-status  laeuft  │
│ gelaufen               │     PDL 30.112,25     │ + bias-daily   gestern 20:00│
│ » Briefingtext         │     NWOG 30.170,00    │ ~ bias-weekly     Fr 20:00  │
│ ── Termine ──          │ News (USD, NY)        │ ! daten-1s      2 Tage alt  │
│ 09:00  Uni Mathe       │ 08:30 rot  Core PCE   │ ── starten ──               │
│ 14:30  Call Quant      │ Bias heute: Bullish   │ [live-status] [bias] [1s]   │
├────────────────────────┴───────────────────────┼─────────────────────────────┤
│  PLANUNG                                  (3)  │  QUANT-LERNPFAD       (3)   │
│ [ ] Backtest ORG-C.E. neu rechnen              │ Woche 01  ###....  3/7      │
└────────────────────────────────────────────────┴─────────────────────────────┘
```

(1) Schnitt 1 · (2) Schnitt 2 · (3) Schnitt 3

Gestaltung:

- Ein Panel = eine JS-Funktion, die aus ihrem Teil des State-JSON HTML macht. Kein Framework.
- Dunkel per `prefers-color-scheme`; Farbe ausschliesslich fuer Signalzustaende
  (gruen gelaufen / gelb faellig / rot Fehler).
- Serifenlos, `font-variant-numeric: tabular-nums` fuer Preise — Levels muessen untereinander
  lesbar sein.
- Jedes Panel zeigt das Alter seiner Quelle. Ein Briefing von gestern, das aussieht wie das von
  heute, ist der teuerste Fehler, den dieses Dashboard machen kann.
- Levels als vollstaendige Tabelle (PDH/PDL/NWOG/Asia, Qs/Os/Hs wo vorhanden), nicht als
  Einzelwert — stehende Nutzervorgabe.

## Fehlerverhalten

Jedes Panel scheitert fuer sich, sichtbar. Ein Panel mit fehlender, kaputter oder veralteter
Quelle rendert seinen Fehlertext **an der Stelle des Inhalts** — nie leer, nie der letzte gute
Wert.

| Fall | Verhalten |
|---|---|
| Briefing-Datei fuer heute fehlt (Cowork lief nicht oder wurde uebersprungen) | „Kein Briefing fuer <Datum> — letztes: <Datum>" + Button, den Lauf per `claude -p` nachzuholen |
| `bias_levels.py` wirft oder braucht > 20 s | Timeout; Panel zeigt Fehlertext + Zeitstempel des letzten erfolgreichen Abrufs |
| 1s-Marktdaten aelter als der letzte Handelstag | Kopfzeile rot: „NQ 1s bis <Datum>, N Tage Luecke" — **melden, nicht nachladen** (Autonomie-Regel aus CLAUDE.md) |
| `claude`-Subprozess stirbt oder haengt | Run als `fehlgeschlagen` mit Exit-Code, Log bleibt liegen; kein automatischer Neustart |

## Schreiben

`POST /api/write` nimmt `{path, content}`:

1. Zielpfad gegen Whitelist pruefen — **nach** `Path.resolve()`, damit `../` und absolute Pfade
   nicht durchrutschen. Erlaubt: `planung/`, `raw/journal/`, `wiki/lernpfad/`.
2. Niemals nach `raw/marktdaten/` schreiben — unter keinen Umstaenden.
3. Atomar schreiben: temporaere Datei im Zielverzeichnis, dann `os.replace`. Ein abgebrochener
   Schreibvorgang darf keine halbe Journal-Datei hinterlassen.

## Test

`tools/test_dashboard.py`, vier Asserts, kein Framework, Aufruf `python tools/test_dashboard.py`:

1. Pfad-Whitelist lehnt `../`-Pfade und absolute Pfade ab.
2. `/api/state` liefert bei fehlender Briefing-Datei `error` statt einer Exception.
3. Stale-Erkennung schlaegt bei manipulierter Mtime an.
4. Atomarer Write hinterlaesst bei simuliertem Abbruch keine Teildatei.

## Bewusst weggelassen

Auth (bindet nur an 127.0.0.1) · Historie/Datenbank (Git ist die Historie) · Konfigdatei (Port
als Konstante) · Mobilansicht · Charts · SSE/WebSockets.

## Ausblick: Schnitt 2 und 3

- **Schnitt 2 — Agents:** Panel mit laufenden und letzten Runs, Cron-Status (wann zuletzt, was
  als naechstes faellig), Skill-/Command-Katalog mit Start-Button, Output-Artefakte. Nutzt
  `POST /api/run`, das in Schnitt 1 bereits entsteht.
- **Schnitt 3 — Planung:** Tagesplan/Todos nach `planung/<datum>.md`, Journal-Kurznotizen nach
  `raw/journal/`, Lernpfad-Fortschritt nach `wiki/lernpfad/`. Nutzt `POST /api/write`.

Jeder Schnitt bekommt seinen eigenen Plan; diese Spec deckt nur Schnitt 1.
