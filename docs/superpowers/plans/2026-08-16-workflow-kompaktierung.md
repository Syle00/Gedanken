# Workflow-Kompaktierung Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Den Kontext pro Session halbieren, die Git-Historie wieder auswertbar machen und
yfinance durch den IBKR-Pfad ersetzen — ohne eine einzige Backtest-Zahl zu verändern.

**Architecture:** Fünf voneinander unabhängige Eingriffe. `CLAUDE.md` wird an der Layer-Grenze
in zwei Dateien geteilt (`algo/CLAUDE.md` lädt Claude Code automatisch beim Zugriff auf
`algo/`). Die Chronik wandert aus `wiki/log.md`/`algo/PLAN.md` in die Git-Historie, weshalb
`push.ps1` aussagekräftige Messages erzwingt. `live_status.py` verliert seinen yfinance-Feed und
liest stattdessen über die bestehende Schicht `algo/marktdaten.py`, die IBKR-1s-Parquets bereits
versteht.

**Tech Stack:** Python 3 (pandas, pyarrow, ib_insync), PowerShell 5.1, Markdown.

**Spec:** `docs/superpowers/specs/2026-08-16-workflow-kompaktierung-design.md`

## Scope-Hinweis

Dieser Plan deckt **Sektionen 1, 2, 4, 5, 6 und 7** der Spec ab. **Sektion 3
(Backtest-Registry, 28 Dateien)** ist ein eigenes Subsystem mit eigenem Risikoprofil
(Zahlen-Regression über 28 Thesen) und bekommt einen eigenen Plan. Sie steht in der Spec
ohnehin als letzter Umsetzungsschritt — dieser Plan läuft vollständig ohne sie.

## Global Constraints

- **Antwort- und Codesprache:** Kommentare und Docstrings auf Deutsch ohne Umlaute im
  Quelltext-Kommentar, wie im Bestand (`fetch_ibkr.py`, `marktdaten.py`). Bezeichner englisch
  oder deutsch nach Bestandsmuster.
- **Keine Zahlen-Änderung:** Kein Schritt in diesem Plan darf ein Backtest-Ergebnis verändern.
  Tritt eine Abweichung auf, ist das ein Fehler des Schritts, nicht ein neues Ergebnis.
- **Testkonvention `algo/`:** Kein pytest. Jedes Modul trägt ein `demo()`, `_demo()` oder
  `selfcheck()` mit `assert`, das in `algo/selfcheck.py` importiert und aufgerufen wird.
  Verifikation immer über `python algo/selfcheck.py`.
- **Testkonvention `tools/`:** pytest-Dateien `tools/test_*.py` (Bestand:
  `test_fetch_yt_playlist.py`, `test_fvg_vii.py`).
- **Datetime-Auflösung:** immer explizit `.as_unit("s")`, nie manuelle Division
  (Arbeitsstandard „Zeit vor Preis").
- **Tick-Raster:** Jeder abgeleitete Preis liegt auf 0,25 (NQ/ES/MNQ).
- **Rollback-Punkte unangetastet:** `CLAUDE.2.0.md` und `CLAUDE.1.0.md` werden in keinem Schritt
  verändert.
- **Push bleibt manuell:** Kein Task führt `git push` aus. Commits ja, Push macht der Nutzer.

---

### Task 1: Gedanken-Clone sichern

**Files:**
- Modify: `C:\Users\Jannes\Desktop\Gedanken` (zweiter Git-Clone von `github.com/Syle00/Gedanken`)
- Keine Datei in `VS Folder 1` wird berührt.

**Interfaces:**
- Consumes: nichts.
- Produces: nichts. Reine Sicherungsmaßnahme, von allen anderen Tasks unabhängig.

**Warum zuerst:** 21 uncommittete Dateien existieren nur dort — kein Push, kein Backup. Der
Rest des Plans hat Zeit, das hier nicht.

- [ ] **Step 1: Bestand aufnehmen, nichts anfassen**

```bash
cd /c/Users/Jannes/Desktop/Gedanken
git status --short
git log -1 --pretty="%h %ad %s" --date=short
```

Erwartet: 21 Zeilen, Stand 2026-08-15. Jede Zeile in eine der drei Klassen einordnen und die
Zuordnung notieren:
- **Marktdaten** (`raw/*.csv` mit TradingView-Namensmuster wie `CME_MINI_ESU2026, 1.csv`)
- **Projektfremd** (`Claude Setup.exe`, `err.log`, `.obsidian/graph.json`)
- **Unklar** — bleibt liegen, wird gemeldet, nicht geraten (Regel „Automatische Einsortierung"
  in `CLAUDE.md`)

- [ ] **Step 2: Marktdaten einsortieren statt blind committen**

```bash
cd /c/Users/Jannes/Desktop/Gedanken
python tools/sort_marktdaten.py
git status --short
```

Erwartet: Die TradingView-CSVs sind aus `raw/` in `raw/marktdaten/<Jahr>/<Monat>/<TT.MM.JJJJ>/`
verschoben. Dateien, deren Timeframe das Skript nicht erkennt, bleiben in `raw/` liegen — das
ist gewolltes Verhalten, kein Fehler.

- [ ] **Step 3: Verschobene Daten gegen die Zeitachse prüfen**

Pflicht aus dem Arbeitsstandard „Marktdaten wie Gold behandeln". Für jede neu einsortierte
Datei erste und letzte Zeile gegen den Ordnernamen prüfen:

```bash
cd /c/Users/Jannes/Desktop/Gedanken
for f in $(git status --short raw/marktdaten | awk '{print $2}'); do
  echo "--- $f"; head -2 "$f"; tail -1 "$f"
done
```

Erwartet: Der Datumsanteil in erster/letzter Zeile liegt im Tagesordner, in dem die Datei nun
liegt. Weicht ein Datum ab, die Datei zurück nach `raw/` legen und in Step 5 melden — nicht
committen.

- [ ] **Step 4: Projektfremdes ausschließen**

```bash
cd /c/Users/Jannes/Desktop/Gedanken
grep -n "Claude Setup.exe\|err.log" .gitignore || printf '\nClaude Setup.exe\nerr.log\n' >> .gitignore
git status --short
```

Erwartet: `Claude Setup.exe` und `err.log` erscheinen nicht mehr als untracked.
`.obsidian/graph.json` ist eine Obsidian-Laufzeitdatei — ebenfalls in `.gitignore` aufnehmen,
falls dort noch nicht enthalten.

- [ ] **Step 5: Committen, nicht pushen**

```bash
cd /c/Users/Jannes/Desktop/Gedanken
git add -A
git commit -m "daten | TradingView-Exporte YM/ES/MNQ vom Zweitrechner einsortiert"
git log -1 --pretty="%h %s"
git status --short
```

Erwartet: Commit angelegt. `git status --short` zeigt nur noch bewusst liegengelassene
Zweifelsfälle. Diese im Abschlussbericht namentlich auflisten.

**Kein Push in diesem Task.** Der Clone ist einen Tag hinter `origin`; ein Push ohne
vorherigen Rebase erzeugt einen non-fast-forward. Das Nachziehen macht der Nutzer über
`/update`.

---

### Task 2: `CLAUDE.md` teilen und Verhaltensregeln nachtragen

**Files:**
- Create: `algo/CLAUDE.md`
- Modify: `CLAUDE.md` (entfernt Zeilen 16–43, 315–479; ergänzt Kurzfassung + zwei Absätze)

**Interfaces:**
- Consumes: nichts.
- Produces: `algo/CLAUDE.md` als Ablageort aller Algo-Standards. Task 6, 7 und 8 verweisen
  darauf statt auf `CLAUDE.md`.

**Deckt Spec-Sektion 1 und 7 ab.** Beides sind Edits an derselben Datei; getrennt zu
committen brächte nur einen zweiten Reviewzyklus für dieselbe Datei.

Zeilenzuordnung im Bestand (`grep -n "^## " CLAUDE.md`):

| Abschnitt | Zeilen | Ziel |
|---|---|---|
| Layer 0 | 16–43 | nach `algo/CLAUDE.md`, Kurzfassung bleibt |
| Algo-Trading: Arbeitsstandards | 315–407 | nach `algo/CLAUDE.md` |
| Algo-Trading: Roadmap zur IBKR-Anbindung | 408–449 | nach `algo/CLAUDE.md` |
| Protokoll- und Datenartefakte | 450–469 | nach `algo/CLAUDE.md` |
| Domänenkontext: algo | 470–479 | nach `algo/CLAUDE.md` |

- [ ] **Step 1: `algo/CLAUDE.md` anlegen**

Die fünf Abschnitte **wörtlich** aus `CLAUDE.md` übernehmen — kein Umformulieren, kein Kürzen.
Der Umbau ist ein Umzug, keine Überarbeitung. Datei beginnt mit:

```markdown
# Algo-Kontext — NQ/ES-Handelsalgorithmus

> Diese Datei lädt automatisch, sobald eine Datei in `algo/` gelesen oder bearbeitet wird.
> Sie enthält die Algo-spezifischen Standards, die bis 2026-08-16 in der Haupt-`CLAUDE.md`
> standen. Für Wiki-, `raw/`- und `site/`-Regeln gilt weiterhin `../CLAUDE.md`.

<!-- Es folgen wörtlich: Layer 0, Algo-Trading: Arbeitsstandards,
     Algo-Trading: Roadmap zur IBKR-Anbindung, Protokoll- und Datenartefakte,
     Domänenkontext: algo -->
```

- [ ] **Step 2: Abschnitte aus `CLAUDE.md` entfernen und Kurzfassung einsetzen**

An Stelle des alten Layer-0-Blocks (Zeile 16–43) tritt:

```markdown
## Layer 0 — Übergeordnetes Ziel: autonomer IBKR-Handelsalgorithmus

Verfolge als Ziel von allem in diesem Repo einen Handelsalgorithmus für NQ und ES, der
selbstständig und allein über Interactive Brokers handelt. Behandle Wiki-System, Datenpflege
und Backtesting als **Unterbau für dieses eine Ziel**, nicht als eigenständige Ziele — bei
einem Zielkonflikt entscheide zugunsten des Algo-Ziels.

> Die vollständigen Algo-Standards (Arbeitsstandards, IBKR-Roadmap, Protokollartefakte,
> Domänenkontext) stehen in [`algo/CLAUDE.md`](algo/CLAUDE.md) und laden automatisch, sobald
> du eine Datei in `algo/` anfasst. Arbeitest du am Algo, lies sie zuerst.
```

Die vier Abschnitte ab Zeile 315 ersatzlos entfernen und durch einen Einzeiler ersetzen:

```markdown
## Algo-Trading

Siehe [`algo/CLAUDE.md`](algo/CLAUDE.md) — Arbeitsstandards, IBKR-Roadmap, Protokollartefakte
und Domänenkontext liegen dort und laden automatisch bei Zugriff auf `algo/`.
```

- [ ] **Step 3: Antwortlänge und Autonomie ergänzen (Spec-Sektion 7)**

Direkt hinter den Abschnitt `## Sprache` einfügen:

```markdown
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
```

- [ ] **Step 4: Vollständigkeit prüfen**

```bash
cd "C:/Users/Jannes/Desktop/VS Folder 1"
wc -l CLAUDE.md algo/CLAUDE.md
grep -c "^## " CLAUDE.md algo/CLAUDE.md
grep -n "Silver Bullet\|dubious_pct\|Paper-Trading\|seasonal_tendency" CLAUDE.md algo/CLAUDE.md
```

Erwartet: `CLAUDE.md` rund 300 Zeilen, `algo/CLAUDE.md` rund 185. Jeder der vier gesuchten
Begriffe taucht **genau einmal** auf, und zwar in `algo/CLAUDE.md` — findet `grep` einen davon
noch in `CLAUDE.md`, wurde ein Abschnitt doppelt stehengelassen; findet er ihn nirgends, ist
beim Umzug Inhalt verloren gegangen.

- [ ] **Step 5: Commit**

```bash
cd "C:/Users/Jannes/Desktop/VS Folder 1"
git add CLAUDE.md algo/CLAUDE.md
git commit -m "claude.md | Algo-Standards nach algo/CLAUDE.md ausgelagert, Antwortlaenge und Autonomie ergaenzt"
```

---

### Task 3: `push.ps1` erzwingt aussagekräftige Commit-Messages

**Files:**
- Modify: `push.ps1` (Block „3. Commit", der `$Message`-Fallback)
- Modify: `CLAUDE.md` (Ingest-Schritt 7, Abschnitt `## Operationen`)

**Interfaces:**
- Consumes: nichts.
- Produces: `push.ps1` ohne Auto-Message. Task 4 setzt darauf auf, weil die Git-Historie danach
  die Chronik trägt.

- [ ] **Step 1: Ist-Verhalten festhalten**

```powershell
cd "C:\Users\Jannes\Desktop\VS Folder 1"
Select-String -Path push.ps1 -Pattern 'wiki update'
```

Erwartet: genau ein Treffer, die Fallback-Zeile
`if (-not $Message) { $Message = "wiki update $(Get-Date -Format 'yyyy-MM-dd')" }`.

- [ ] **Step 2: Fallback durch Abbruch mit Vorschlag ersetzen**

Diese Zeile ersetzen durch:

```powershell
    if (-not $Message) {
        # Bewusst ein Abbruch statt einer generierten Message: eine geratene Message ist
        # genauso wertlos wie "wiki update" und verdeckt nur, dass niemand hingesehen hat.
        Write-Host "`nKeine Commit-Message angegeben." -ForegroundColor Yellow
        Write-Host "  Geaendert: $(git diff --cached --shortstat)"
        Write-Host "  Bereiche:  $((git diff --cached --name-only | ForEach-Object { ($_ -split '/')[0] } | Sort-Object -Unique) -join ', ')"
        Fail "Bitte mit -Message '<typ> | <worum ging es>' erneut aufrufen. Es wurde nichts committet."
    }
```

- [ ] **Step 3: Abbruch verifizieren**

```powershell
cd "C:\Users\Jannes\Desktop\VS Folder 1"
"test" | Out-File -Encoding utf8 test-push-guard.txt
.\push.ps1 -NoPush
```

Erwartet: Ausgabe endet mit `FEHLER: Bitte mit -Message ...`, Exit-Code 1, **kein** neuer
Commit. Prüfen mit `git log -1 --pretty="%s"` — die Message muss unverändert die aus Task 2
sein.

- [ ] **Step 4: Erfolgsfall verifizieren, Testdatei entfernen**

```powershell
cd "C:\Users\Jannes\Desktop\VS Folder 1"
Remove-Item test-push-guard.txt
.\push.ps1 -Message "test | push-guard geprueft" -NoPush
git log -1 --pretty="%s"
```

Erwartet: Commit entsteht mit exakt dieser Message. Falls durch das Entfernen der Testdatei
nichts mehr zu committen ist, meldet das Skript „Keine Aenderungen" und beendet sich mit 0 —
auch das ist ein bestandener Durchlauf.

- [ ] **Step 5: Ingest-Schritt 7 in `CLAUDE.md` auf Sessionende umstellen**

Im Abschnitt `## Operationen`, Ingest-Schritt 7, den Text ersetzen durch:

```markdown
7. **Führe `.\push.ps1 -Message "<typ> | <worum ging es>"` am Ende der Session selbst aus** —
   das baut die HTML-Website neu, erstellt einen Checkpoint-Commit und pusht ins private
   Repo. Ein Aufruf pro Session genügt, nicht einer pro Ingest. Ohne diesen Schritt ist der
   Ingest nicht abgeschlossen; frag **nicht erst nach**. `push.ps1` verweigert seit
   2026-08-16 den Dienst ohne `-Message` — die Git-Historie ist die Chronik des Projekts,
   siehe `## log.md`-Format.
```

- [ ] **Step 6: Commit**

```bash
cd "C:/Users/Jannes/Desktop/VS Folder 1"
git add push.ps1 CLAUDE.md
git commit -m "push | Commit-Message ist Pflicht, Push einmal pro Session statt pro Ingest"
```

---

### Task 4: Protokolle archivieren, `/tagesbericht` auf Git umstellen

**Files:**
- Create: `wiki/log-archiv-bis-2026-08.md`
- Create: `algo/PLAN-archiv-bis-2026-08.md`
- Modify: `wiki/log.md`, `algo/PLAN.md`
- Modify: `.claude/commands/tagesbericht.md`
- Modify: `CLAUDE.md` (Abschnitt `## log.md`-Format)

**Interfaces:**
- Consumes: `push.ps1` mit Message-Pflicht aus Task 3 — ohne die wäre die Git-Historie kein
  tragfähiger Ersatz für die Log-Tabellen.
- Produces: nichts, was spätere Tasks brauchen.

**Kritisch:** Die 2769 Zeilen `wiki/log.md` werden **verschoben, nicht gelöscht**. Sie
enthalten Entstehungsgründe, die in keinem Commit stehen.

- [ ] **Step 1: Vollständige Kopien anlegen, bevor irgendetwas gekürzt wird**

```bash
cd "C:/Users/Jannes/Desktop/VS Folder 1"
cp wiki/log.md wiki/log-archiv-bis-2026-08.md
cp algo/PLAN.md algo/PLAN-archiv-bis-2026-08.md
wc -l wiki/log.md wiki/log-archiv-bis-2026-08.md algo/PLAN.md algo/PLAN-archiv-bis-2026-08.md
```

Erwartet: Archiv und Original haben exakt gleiche Zeilenzahl (2769 bzw. 857). Weicht sie ab,
abbrechen — dann hat das Kopieren nicht funktioniert.

- [ ] **Step 2: Archiv-Kopfzeilen ergänzen**

An den Anfang beider Archivdateien:

```markdown
> **Archiv.** Chronologische Einträge bis einschließlich 2026-08-16. Ab diesem Datum trägt
> die Git-Historie den Verlauf (`git log`); hier wird nichts mehr angehängt. Diese Datei
> bleibt erhalten, weil sie Entstehungsgründe festhält, die in keiner Commit-Message stehen.
```

- [ ] **Step 3: `wiki/log.md` auf den laufenden Teil kürzen**

`wiki/log.md` behält ausschließlich: den Kopf/die Formatbeschreibung, offene Fragen, bewusste
Abweichungen von den Konventionen und Widerspruchsmarker (`⚠️`/`✅`). Vorher auffinden, was
davon überhaupt vorhanden ist:

```bash
cd "C:/Users/Jannes/Desktop/VS Folder 1"
grep -n "⚠️\|✅\|offen\|Abweichung" wiki/log.md | head -40
```

Alle so gefundenen Zeilen samt ihres `## [Datum]`-Kopfes in der gekürzten `wiki/log.md`
behalten. Alles Übrige entfällt dort (es steht vollständig im Archiv). Neuer Dateikopf:

```markdown
# Wiki-Log (laufend)

> Der chronologische Verlauf steht seit 2026-08-16 in der Git-Historie (`git log`).
> Hier stehen nur noch Dinge, die kein Commit ausdrückt: offene Fragen, bewusste Abweichungen
> von den Konventionen und Widerspruchsmarker. Ältere Einträge:
> [[log-archiv-bis-2026-08]].
```

- [ ] **Step 4: `algo/PLAN.md` auf Backlog und Zustand kürzen**

Die Log-Tabelle entfernen, Backlog und Zustandsbeschreibung behalten. Kopfzeile ergänzen:

```markdown
> Die chronologische Log-Tabelle steht seit 2026-08-16 in `PLAN-archiv-bis-2026-08.md` und
> wird nicht fortgeführt — neue Ereignisse stehen in der Commit-Message. Hier bleiben Backlog
> und aktueller Zustand.
```

- [ ] **Step 5: `/tagesbericht` auf Git umstellen**

In `.claude/commands/tagesbericht.md` Schritt 3 (`wiki/log.md` durchsuchen) ersetzen:

```markdown
3. Die Motivation hinter den Commits aus deren Messages ableiten. Seit 2026-08-16 sind sie
   aussagekräftig (`<typ> | <worum ging es>`); `push.ps1` erzwingt das. Für Tage **vor** dem
   2026-08-16 stattdessen `wiki/log-archiv-bis-2026-08.md` nach `## [<Datum>]` durchsuchen —
   damals waren alle Commit-Messages `wiki update <Datum>` und damit wertlos.
```

Zusätzlich die `description:` im Frontmatter anpassen: `(Git-Historie + wiki/log.md)` wird zu
`(Git-Historie)`.

- [ ] **Step 6: `/tagesbericht` gegen einen alten und einen neuen Tag prüfen**

```bash
cd "C:/Users/Jannes/Desktop/VS Folder 1"
git log --pretty=format:"%ad %s" --date=format:"%H:%M" --since="2026-08-16 00:00" --reverse -- . ':!site' ':!.obsidian'
grep -c "## \[2026-08-14\]" wiki/log-archiv-bis-2026-08.md
```

Erwartet: Der `git log`-Aufruf liefert die Commits dieses Plans mit sprechenden Messages. Der
`grep` findet die Einträge des 14.08. im Archiv — der Rückgriffpfad für alte Tage funktioniert.

- [ ] **Step 7: `## log.md`-Format in `CLAUDE.md` nachziehen**

Im Abschnitt `## log.md`-Format ergänzen:

```markdown
Seit 2026-08-16 trägt die Git-Historie den chronologischen Verlauf. Hänge an `wiki/log.md`
nur noch an, was keine Commit-Message ausdrückt: offene Fragen, bewusste Abweichungen von den
Konventionen, Widerspruchsmarker. Alles Übrige gehört in die Commit-Message, die `push.ps1`
seither erzwingt.
```

- [ ] **Step 8: Commit**

```bash
cd "C:/Users/Jannes/Desktop/VS Folder 1"
git add wiki/log.md wiki/log-archiv-bis-2026-08.md algo/PLAN.md algo/PLAN-archiv-bis-2026-08.md .claude/commands/tagesbericht.md CLAUDE.md
git commit -m "log | Chronik in Git-Historie verlagert, Altbestand nach log-archiv-bis-2026-08 gesichert"
```

---

### Task 5: `trading_day`, `flatten` und `resample_bars` nach `marktdaten.py`

**Files:**
- Modify: `algo/marktdaten.py` (drei neue öffentliche Funktionen, `_forex_bars` nutzt eine davon)
- Test: `algo/marktdaten.py::_demo` (bestehende Funktion erweitern)

**Interfaces:**
- Consumes: nichts.
- Produces:
  - `trading_day(ts: pd.Timestamp, daily: bool = False) -> date` — Globex-Handelstag
    (18:00 NY des Vortags bis 17:00 NY). Task 6 nutzt sie.
  - `flatten(df: pd.DataFrame) -> pd.DataFrame` — MultiIndex-Spalten plätten. Task 6 nutzt sie.
  - `resample_bars(bars: list[Bar], tf: str) -> list[Bar]` — Bar-Liste auf einen gröberen
    Timeframe verdichten, NY-Mitternacht als Anker. Task 6 nutzt sie.

**Warum vorgezogen:** `live_status.py` importiert `trading_day` und `flatten` aus
`fetch_yfinance.py`. Ohne diesen Umzug lässt sich `fetch_yfinance.py` in Task 7 nicht löschen.

- [ ] **Step 1: Fehlschlagenden Selbstcheck schreiben**

In `algo/marktdaten.py` innerhalb `_demo()` ergänzen:

```python
    # --- trading_day: Globex-Grenze 18:00 NY -------------------------------
    ts_abend = pd.Timestamp("2026-08-13 18:30", tz=NY)
    ts_morgen = pd.Timestamp("2026-08-13 09:30", tz=NY)
    assert trading_day(ts_abend) == date(2026, 8, 14), "18:30 NY gehoert zum Folgetag"
    assert trading_day(ts_morgen) == date(2026, 8, 13), "09:30 NY gehoert zum selben Tag"
    assert trading_day(ts_abend, daily=True) == date(2026, 8, 13), "daily=True nimmt das Kalenderdatum"

    # --- flatten: MultiIndex-Spalten plaetten ------------------------------
    multi = pd.DataFrame([[1.0]], columns=pd.MultiIndex.from_tuples([("close", "NQ")]))
    assert list(flatten(multi).columns) == ["close"], "flatten muss die zweite Ebene entfernen"

    # --- resample_bars: 1m -> 5m, OHLC-Aggregation korrekt -----------------
    basis = [Bar(datetime(2026, 8, 13, 9, 30 + i, tzinfo=NY), 100.0 + i, 101.0 + i,
                 99.0 + i, 100.5 + i) for i in range(5)]
    fuenf = resample_bars(basis, "5m")
    assert len(fuenf) == 1, f"5 1m-Kerzen ergeben 1 5m-Kerze, nicht {len(fuenf)}"
    assert fuenf[0].o == 100.0, "open = erste Kerze"
    assert fuenf[0].h == 105.0, "high = Maximum"
    assert fuenf[0].l == 99.0, "low = Minimum"
    assert fuenf[0].c == 104.5, "close = letzte Kerze"
```

Der Import `from datetime import datetime, date` muss oben in `marktdaten.py` vorhanden sein —
prüfen und ggf. ergänzen.

- [ ] **Step 2: Selbstcheck laufen lassen, Fehlschlag bestätigen**

```bash
cd "C:/Users/Jannes/Desktop/VS Folder 1"
python algo/marktdaten.py
```

Erwartet: `NameError: name 'trading_day' is not defined`. Ein anderer Fehler bedeutet, dass der
Selbstcheck falsch geschrieben ist — erst den korrigieren.

- [ ] **Step 3: Die drei Funktionen implementieren**

`trading_day` und `flatten` **wörtlich** aus `algo/fetch_yfinance.py` (Zeilen 55–64) übernehmen
— identisches Verhalten ist hier Pflicht, nicht Stilfrage:

```python
def trading_day(ts: pd.Timestamp, daily: bool = False):
    """Globex-Handelstag: 18:00 NY des Vortages bis 17:00 NY. Uebernommen aus
    fetch_yfinance.py (dort 2026-08-16 entfallen) -- quellenunabhaengig, gilt fuer
    IBKR-Daten genauso."""
    if daily:
        return ts.date()
    ts = ts.tz_convert(NY)
    return ts.date() + timedelta(days=1) if ts.hour >= 18 else ts.date()


def flatten(df: pd.DataFrame) -> pd.DataFrame:
    """MultiIndex-Spalten auf die erste Ebene reduzieren."""
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df
```

`resample_bars` zieht die Resample-Logik aus `_forex_bars` (Zeilen 89–96) heraus:

```python
def resample_bars(bars_in: list[Bar], tf: str) -> list[Bar]:
    """Bar-Liste auf einen groeberen Timeframe verdichten. Anker an NY-Mitternacht ueber
    origin='start_day' -- der Index ist NY-lokalisiert, ohne den Anker lägen die Buckets an
    UTC-Mitternacht. Fuer WANDUHR_TF (4h) wird tz-naiv resampled und danach re-lokalisiert."""
    if not bars_in:
        return []
    df = pd.DataFrame(
        {"open": [b.o for b in bars_in], "high": [b.h for b in bars_in],
         "low": [b.l for b in bars_in], "close": [b.c for b in bars_in]},
        index=pd.DatetimeIndex([b.t for b in bars_in]),
    )
    if tf in WANDUHR_TF:
        res = df.tz_localize(None).resample(
            PANDAS_FREQ[tf], label="left", closed="left").agg(OHLC).dropna()
        res.index = res.index.tz_localize(NY, ambiguous=True, nonexistent="shift_forward")
        df = res
    else:
        df = df.resample(PANDAS_FREQ[tf], label="left", closed="left",
                         origin="start_day").agg(OHLC).dropna()
    idx_py = df.index.to_pydatetime()
    opens, highs, lows, closes = (df[c].to_numpy() for c in ("open", "high", "low", "close"))
    return [Bar(t, float(o), float(h), float(l), float(c))
            for t, o, h, l, c in zip(idx_py, opens, highs, lows, closes)]
```

- [ ] **Step 4: Selbstcheck grün, Forex-Pfad unverändert**

```bash
cd "C:/Users/Jannes/Desktop/VS Folder 1"
python algo/marktdaten.py
python algo/selfcheck.py
```

Erwartet: beide laufen ohne `AssertionError` durch. `selfcheck.py` prüft über
`marktdaten._demo` und `_demo_dst` mit, dass der Forex-Resample-Anker (Sommer-/Winterzeit)
unverändert ist.

- [ ] **Step 5: `_forex_bars` auf die neue Funktion umstellen**

Zeilen 89–96 in `_forex_bars` durch den Aufruf ersetzen — dieselbe Logik darf nicht zweimal
im Modul stehen. Achtung auf die Reihenfolge: `_forex_bars` filtert **nach** dem Resampling auf
`von`/`bis`, das muss so bleiben, sonst fehlen Randkerzen.

```bash
python algo/selfcheck.py
```

Erwartet: unverändert grün. Schlägt jetzt etwas fehl, ist die Extraktion nicht
verhaltensgleich — dann Step 5 zurücknehmen und `_forex_bars` unangetastet lassen; die
Duplizierung ist das kleinere Übel gegenüber veränderten Forex-Zahlen.

- [ ] **Step 6: Commit**

```bash
cd "C:/Users/Jannes/Desktop/VS Folder 1"
git add algo/marktdaten.py
git commit -m "marktdaten | trading_day, flatten und resample_bars aus fetch_yfinance/_forex_bars herausgeloest"
```

---

### Task 6: `live_status.py` auf NQ über IBKR umstellen

**Files:**
- Modify: `algo/live_status.py` (Zeilen 31–33 Imports, `_download`, `fetch_today`,
  `_bars_from_df`, `DISPLAY_SYMBOL`)
- Test: `algo/live_status.py::selftest` (bestehende Funktion, Zeile 251)

**Interfaces:**
- Consumes: `marktdaten.trading_day`, `marktdaten.flatten`, `marktdaten.resample_bars`,
  `marktdaten.bars(symbol, tf, von, bis)` (Task 5); `fetch_ibkr.main(argv) -> int` mit den
  Optionen `--backfill VON BIS`, `--symbol NQ`, `--kein-fenster`. `main()` startet das Gateway
  intern über `_gateway_sicherstellen()` — diese private Funktion wird **nicht** direkt
  aufgerufen.
- Produces: nichts für spätere Tasks.

**Datenlage, vorab geprüft:**
- `NQ` hat 6540 1d-Tagesdateien in `raw/marktdaten/` (MNQ nur 1885) — die NDOG/NWOG-Historie in
  `open_gap_history()` wird durch den Wechsel **länger**, nicht kürzer.
- 1s-Parquets liegen für NQ an 19 Tagen vor, für ES an 18 — reicht für den heutigen Tag, den
  `live_status` allein braucht.
- 5m/15m/1h-CSVs existieren für NQ **nicht**. Der Intraday-Teil muss deshalb aus 1s über
  `resample_bars` entstehen; das ist der Grund, warum Task 5 vorgezogen wurde.

- [ ] **Step 1: Fehlschlagenden Selbstcheck ergänzen**

In `selftest()` (ab Zeile 251) ergänzen:

```python
    # --- Symbol und Datenquelle ------------------------------------------
    assert DISPLAY_SYMBOL == "NQ", f"live_status laeuft auf NQ, nicht {DISPLAY_SYMBOL}"
    assert "yfinance" not in sys.modules, "live_status darf yfinance nicht mehr importieren"

    # --- 1s -> 5m ohne Netz: resample_bars liefert BASE_TF ----------------
    eine_min = [Bar(datetime(2026, 8, 14, 9, 30, s, tzinfo=NY), 23000.0 + s, 23001.0 + s,
                    22999.0 + s, 23000.5 + s) for s in range(0, 300, 1)]
    fuenf = resample_bars(eine_min, "5m")
    assert len(fuenf) == 1, f"300 1s-Kerzen ergeben 1 5m-Kerze, nicht {len(fuenf)}"
    assert fuenf[0].h == max(b.h for b in eine_min), "high der 5m-Kerze = Maximum der 1s-Kerzen"
```

- [ ] **Step 2: Fehlschlag bestätigen**

```bash
cd "C:/Users/Jannes/Desktop/VS Folder 1"
python algo/live_status.py --selftest
```

Erwartet: `AssertionError: live_status laeuft auf NQ, nicht MNQ`.

- [ ] **Step 3: Imports und Symbol umstellen**

Zeilen 31–36 ersetzen:

```python
import pandas as pd

from marktdaten import trading_day, flatten, resample_bars, bars as markt_bars  # noqa: E402
import fetch_ibkr  # noqa: E402

DISPLAY_SYMBOL = "NQ"
```

`import yfinance as yf` und `from fetch_yfinance import ...` entfallen ersatzlos. `SYMBOL_TICK`
bleibt an `DISPLAY_SYMBOL` gekoppelt und stimmt damit automatisch — NQ läuft wie MNQ in
0,25-Schritten.

- [ ] **Step 4: `_download` durch den IBKR-Pfad ersetzen**

```python
def _download_1s(day: date) -> list[Bar]:
    """Heutigen Handelstag als 1s-Balken holen. Zuerst aus raw/marktdaten/ -- hat /daten-1s
    den Tag schon gezogen, kostet das keinen IBKR-Request. Sonst denselben Weg nehmen, den
    /daten-1s nutzt: fetch_ibkr.main() schreibt die Tagesdatei (und startet dabei selbst das
    Gateway), danach wird sie gelesen. Bewusst der Umweg ueber die Datei statt eines direkten
    Rueckgabewerts: Live-Betrieb und Backtest sehen so garantiert dieselben Bytes.
    Fehler duerfen den Loop nicht abbrechen -- dann bleibt die Liste leer und der Aufrufer
    meldet 'keine Daten', statt zu raten."""
    vorhanden = markt_bars(DISPLAY_SYMBOL, "1s", von=day, bis=day)
    if vorhanden:
        return vorhanden
    try:
        fetch_ibkr.main(["--backfill", day.isoformat(), day.isoformat(),
                         "--symbol", DISPLAY_SYMBOL, "--kein-fenster"])
    except Exception as exc:
        print(f"  ! 1s: IBKR-Abruf fehlgeschlagen ({exc})", file=sys.stderr)
        return []
    return markt_bars(DISPLAY_SYMBOL, "1s", von=day, bis=day)
```

**Offener Punkt, der in Step 7 zu klären ist:** `--backfill` ohne Argumente zieht laut Hilfetext
„bis gestern". Ob ein explizites `VON BIS` auf den *heutigen*, noch laufenden Tag durchgeht,
entscheidet `_backfill_zeitraum()` in `fetch_ibkr.py` — das im Trockenlauf prüfen. Lehnt es den
heutigen Tag ab, ist das **kein** Anlass, die Prüfung zu umgehen: dann `_backfill_zeitraum` um
den laufenden Tag erweitern und den Grund im Commit festhalten. Ein stillschweigender Rückfall
auf gestrige Daten wäre in einem Live-Status genau der Fehler, den der Arbeitsstandard
„Frische Live-Daten" verbietet.

- [ ] **Step 5: `fetch_today` und `_bars_from_df` auf Bar-Listen umstellen**

`fetch_today` gibt künftig `dict[str, list[Bar]]` statt `dict[str, pd.DataFrame]` zurück:

```python
def fetch_today(target_day: date) -> dict[str, list[Bar]]:
    """Alle INTERVALS aus dem 1s-Strom des Tages, 1d aus dem CSV-Bestand. Die Globex-Session
    startet 18:00 NY am Vortag -- markt_bars/_load_1s_parquet liefern bereits NY-lokalisierte
    Zeitstempel, die Tagesdatei enthaelt genau einen Handelstag, deshalb entfaellt die
    frueher noetige trading_day()-Nachfilterung des yfinance-Kalenderschnitts."""
    eins = _download_1s(target_day)
    out: dict[str, list[Bar]] = {}
    for tf in ("1m", "5m", "15m", "1h", "4h"):
        out[tf] = resample_bars(eins, tf) if eins else []
    out["1d"] = markt_bars(DISPLAY_SYMBOL, "1d", bis=target_day)
    return out
```

`_bars_from_df` entfällt ersatzlos — `markt_bars` liefert bereits `Bar`-Objekte. Alle
Aufrufstellen von `_bars_from_df` auf den direkten Listenzugriff umstellen.

- [ ] **Step 6: Alle Aufrufstellen finden und nachziehen**

```bash
cd "C:/Users/Jannes/Desktop/VS Folder 1"
grep -n "_bars_from_df\|fetch_today\|_download\|\.empty\|DataFrame" algo/live_status.py
```

Jede Fundstelle prüfen: `.empty` gilt für DataFrames, für Listen ist es `if not liste`. Die
Fehlermeldung in `_live_run` (Zeile 388) von „keine 5m-Daten (Markt geschlossen oder
yfinance-Fehler)" auf „keine 5m-Daten (Markt geschlossen oder IBKR-Gateway nicht erreichbar)"
ändern.

- [ ] **Step 7: Selbstcheck und Trockenlauf**

```bash
cd "C:/Users/Jannes/Desktop/VS Folder 1"
python algo/live_status.py --selftest
python algo/live_status.py --dry-run 2026-08-14
python -c "
import sys; sys.path.insert(0, 'algo')
from datetime import date
from fetch_ibkr import _backfill_zeitraum
heute = date.today().isoformat()
try:
    print('heutiger Tag akzeptiert:', _backfill_zeitraum([heute, heute]))
except ValueError as exc:
    print('heutiger Tag ABGELEHNT:', exc)
"
```

Erwartet: Selbstcheck grün. Der Trockenlauf auf den 14.08. liefert einen Bericht — für diesen
Tag liegen `NQ 2026-08-14 1s.parquet` und die 1d-Historie vor, er läuft also ohne Netz.

Der dritte Aufruf beantwortet den offenen Punkt aus Step 4. Meldet er „ABGELEHNT", vor dem
Weitermachen `_backfill_zeitraum()` um den laufenden Tag erweitern — sonst holt `live_status`
im Echtbetrieb nie frische Daten und fällt stillschweigend auf den Bestand zurück.

- [ ] **Step 8: Zeitachse gegen eine unabhängige Quelle prüfen**

Pflicht aus dem Arbeitsstandard „Zeit vor Preis". Der 14.08. hat sowohl `NQ ... 1s.parquet` als
auch `MNQ 2026-08-14 5m.csv` (TradingView-Export) im selben Ordner:

```bash
cd "C:/Users/Jannes/Desktop/VS Folder 1"
python -c "
from pathlib import Path; import sys; sys.path.insert(0, 'algo')
from marktdaten import bars, resample_bars
eins = bars('NQ','1s')
fuenf = [b for b in resample_bars(eins,'5m') if b.t.date().isoformat()=='2026-08-14']
for b in fuenf[:3]: print(b.t, b.o, b.h, b.l, b.c)
"
head -4 "raw/marktdaten/2026/08/14.08.2026/MNQ 2026-08-14 5m.csv"
```

Erwartet: Die Zeitstempel der resampelten NQ-5m-Kerzen stimmen mit denen des
MNQ-TradingView-Exports **auf die Minute** überein. Die Preise unterscheiden sich nicht (NQ und
MNQ notieren identisch) — weicht ein Zeitstempel ab, ist der Resample-Anker falsch und Task 5
Step 3 muss korrigiert werden, bevor es weitergeht.

- [ ] **Step 9: Commit**

```bash
cd "C:/Users/Jannes/Desktop/VS Folder 1"
git add algo/live_status.py
git commit -m "live_status | von yfinance/MNQ auf IBKR-1s/NQ umgestellt, 1d-Historie waechst von 1885 auf 6540 Tage"
```

---

### Task 7: yfinance entfernen

**Files:**
- Delete: `algo/fetch_yfinance.py`, `algo/backfill_yfinance.py`
- Modify: `algo/PLAN.md` (Herkunftsvermerk), `CLAUDE.md` (Warnblöcke),
  `.claude/commands/algo-live-status.md`, `algo/README.md`, `algo/selfcheck.py`
- Modify: 15 Dateien mit yfinance-Erwähnungen in Kommentaren

**Interfaces:**
- Consumes: Task 5 (Helfer umgezogen) und Task 6 (letzter echter Importeur entfernt).
- Produces: nichts.

- [ ] **Step 1: Herkunft der Daten sichern, bevor das Modul verschwindet**

Tage, die ausschließlich per yfinance ins Depot kamen, erkennt man am fehlenden
`(2)`/`(3)`-Suffix (kein manueller TradingView-Export im selben Ordner):

```bash
cd "C:/Users/Jannes/Desktop/VS Folder 1"
for d in raw/marktdaten/*/*/*; do
  if ls "$d"/MNQ*\ 1m.csv >/dev/null 2>&1 && ! ls "$d"/*\(2\)*.csv >/dev/null 2>&1; then
    basename "$d"
  fi
done | sort | tee /tmp/yfinance-only-tage.txt | wc -l
```

Das Ergebnis als Abschnitt in `algo/PLAN.md` eintragen:

```markdown
## Datenherkunft: yfinance-Tage (Stand 2026-08-16)

`algo/fetch_yfinance.py` wurde am 2026-08-16 entfernt. Die folgenden Tage in
`raw/marktdaten/` stammen ausschließlich aus dem yfinance-Feed und sind **nicht tickgenau** —
am 2026-08-12 wich der Feed am 9:30-Open um 0,5 Punkte von der Broker-Quelle ab. Bei
präzisionskritischen Auswertungen (C.E., Quadranten, FVG-Grenzen) auf diesen Tagen gegen die
Chart-Quelle gegenprüfen:

<hier die Liste aus /tmp/yfinance-only-tage.txt einfügen>
```

- [ ] **Step 2: Prüfen, dass niemand mehr importiert**

```bash
cd "C:/Users/Jannes/Desktop/VS Folder 1"
grep -rn "import yfinance\|from yfinance\|from fetch_yfinance\|import fetch_yfinance\|backfill_yfinance" --include="*.py" .
```

Erwartet: **nur** Treffer in `algo/fetch_yfinance.py` und `algo/backfill_yfinance.py` selbst.
Jeder andere Treffer muss vor dem Löschen aufgelöst werden.

- [ ] **Step 3: Module löschen und Selbstcheck entkoppeln**

```bash
cd "C:/Users/Jannes/Desktop/VS Folder 1"
grep -n "yfinance" algo/selfcheck.py
git rm algo/fetch_yfinance.py algo/backfill_yfinance.py
python algo/selfcheck.py
```

Erwartet: `selfcheck.py` läuft grün durch. Bricht es mit `ModuleNotFoundError` ab, ist dort noch
ein Import auf die gelöschten Module — entfernen und erneut laufen lassen.

- [ ] **Step 4: Kommentar-Erwähnungen bereinigen**

```bash
cd "C:/Users/Jannes/Desktop/VS Folder 1"
grep -rn "yfinance" --include="*.py" . | grep -v "^./algo/PLAN"
```

Für jeden Treffer entscheiden: beschreibt der Kommentar noch die Realität? Beispiel
`marktdaten.py` — dort ist „yfinance-DataFrame" zu „OHLC-DataFrame" zu ändern. **Nicht**
löschen, sondern korrigieren: Der Hinweis in `ingest_tvexport.py`, dass yfinance-Tage
tickungenau sind, bleibt inhaltlich richtig und wird auf „Tage aus der yfinance-Ära (bis
2026-08-16), siehe PLAN.md" umgeschrieben.

- [ ] **Step 5: `CLAUDE.md`-Warnblöcke entfernen**

Die beiden Absätze „**Bekannte Grenze: yfinance kann auch auf Tick-Ebene vom Preis
abweichen**" und den yfinance-Teil von „**Frische Live-Daten bei Zukunftsfragen**" ersetzen.
Sie stehen nach Task 2 in `algo/CLAUDE.md`. Neuer Text für den zweiten:

```markdown
**Frische Live-Daten bei Zukunftsfragen.** Führe bei einer Frage des Nutzers zum aktuellen
oder zukünftigen Marktstand **immer zuerst `python algo/live_status.py` neu aus** — verlass
dich nie auf zuvor gelesene `raw/marktdaten/`-Dateien oder einen älteren Live-Lauf im selben
Gespräch, auch nicht bei Wiederholung der Frage. Die Daten kommen seit 2026-08-16 per IBKR-1s;
ist das Gateway nicht erreichbar, meldet der Lauf das explizit — gib in dem Fall **keine**
Zahlen aus dem Bestand als aktuellen Stand aus.
```

Der Tick-Abweichungs-Absatz wird zu einem Zweizeiler, der auf den PLAN.md-Abschnitt aus
Step 1 verweist, statt yfinance als laufende Quelle zu beschreiben.

- [ ] **Step 6: Roadmap-Punkt 1 nachziehen**

In `algo/CLAUDE.md`, Abschnitt „Roadmap zur IBKR-Anbindung", Punkt 1: den Halbsatz
„(TradingView-Export + `algo/fetch_yfinance.py`-Nachlad), begrenzt durch yfinance-Limits (1m
~30 Tage, 5m/15m ~60 Tage, 1d unbegrenzt zurück)" ersetzen durch „(TradingView-Export +
`algo/fetch_ibkr.py`-Nachlad über `/daten-1s`)".

- [ ] **Step 7: Skill-Beschreibung auf NQ umstellen**

In `.claude/commands/algo-live-status.md` Zeile 2 und 5: „fuer MNQ" wird „fuer NQ".

- [ ] **Step 8: `algo/README.md` nachziehen**

```bash
cd "C:/Users/Jannes/Desktop/VS Folder 1"
grep -n "yfinance\|fetch_yfinance\|backfill_yfinance" algo/README.md
```

Die Modul-Abschnitte zu `fetch_yfinance.py` und `backfill_yfinance.py` entfernen, den Abschnitt
zu `live_status.py` auf die neue Datenquelle und das Symbol NQ umschreiben.

- [ ] **Step 9: Gesamtprüfung**

```bash
cd "C:/Users/Jannes/Desktop/VS Folder 1"
grep -rn "yfinance" --include="*.py" --include="*.md" . | grep -v "PLAN.md\|log-archiv\|PLAN-archiv\|docs/superpowers"
python algo/selfcheck.py
python algo/live_status.py --selftest
```

Erwartet: Der `grep` liefert **keine** Treffer — verbleibende Erwähnungen stehen nur noch in
PLAN.md (Herkunftsvermerk), den Archiven und den Spec-/Plandokumenten, wo sie historisch
korrekt sind. Beide Python-Läufe grün.

- [ ] **Step 10: Commit**

```bash
cd "C:/Users/Jannes/Desktop/VS Folder 1"
git add -A
git commit -m "yfinance | Modul entfernt, Herkunft der Altdaten in PLAN.md vermerkt, IBKR ist alleinige Intraday-Quelle"
```

---

### Task 8: Session-Start-Statuszeile

**Files:**
- Modify: `CLAUDE.md` (neuer Abschnitt nach `## Autonomie`)

**Interfaces:**
- Consumes: `tools/sort_marktdaten.py`, `tools/sort_bilder.py`, `/daten-1s --verify`,
  `algo/PLAN.md`.
- Produces: nichts.

Kein neues Skript — die Prüfungen existieren alle. Neu ist nur die feste Form am Sessionanfang.

- [ ] **Step 1: Abschnitt in `CLAUDE.md` einfügen**

```markdown
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
```

- [ ] **Step 2: Die drei Quellen einmal von Hand durchspielen**

```bash
cd "C:/Users/Jannes/Desktop/VS Folder 1"
python tools/sort_marktdaten.py --quiet && echo "sort_marktdaten ok"
python tools/sort_bilder.py --quiet && echo "sort_bilder ok"
tail -3 raw/marktdaten/1s-abdeckung.csv
grep -n "^- \[ \]" algo/PLAN.md | head -5
```

Erwartet: Alle vier Aufrufe liefern Ausgabe ohne Fehler. Damit ist belegt, dass die
Statuszeile aus vorhandenen Quellen füllbar ist und kein neues Werkzeug braucht.

- [ ] **Step 3: Commit**

```bash
cd "C:/Users/Jannes/Desktop/VS Folder 1"
git add CLAUDE.md
git commit -m "session | Statuszeile am Sessionanfang aus vorhandenen Pruefungen"
```

---

### Task 9: `push.ps1` meldet den Stand des Gedanken-Clones

**Files:**
- Modify: `push.ps1` (neuer Block nach „4. Push")

**Interfaces:**
- Consumes: Task 3 (`push.ps1` bereits angefasst).
- Produces: nichts.

Kein Kopier-Sync, kein automatisches Ziehen. Nur eine Meldung — das Nachziehen macht `/update`.

- [ ] **Step 1: Prüfblock ans Ende von `push.ps1` einfügen**

Vor die Schlusszeile `Write-Host "`nFertig. Website: ..."`:

```powershell
# --- 5. Zweitrechner-Clone im Blick behalten -------------------------------
# "Gedanken" ist ein zweiter Clone desselben Repos, kein separater Ordner. Haengt er
# zurueck, liegen dort schnell uncommittete Marktdaten, die nirgends gesichert sind.
# Bewusst nur melden, nicht ziehen: ein Pull in einem fremden Arbeitsverzeichnis kann
# dort laufende Aenderungen zerschiessen. Nachziehen macht /update.
$zweit = "C:\Users\Jannes\Desktop\Gedanken"
if (Test-Path (Join-Path $zweit '.git')) {
    $offen = (git -C $zweit status --porcelain | Measure-Object -Line).Lines
    $dort = git -C $zweit rev-parse HEAD 2>$null
    $hier = git rev-parse HEAD
    if ($dort -ne $hier -or $offen -gt 0) {
        Write-Host "`nGedanken-Clone weicht ab:" -ForegroundColor Yellow
        if ($dort -ne $hier) { Write-Host "  anderer Stand als hier - mit /update nachziehen" }
        if ($offen -gt 0)    { Write-Host "  $offen uncommittete Datei(en) - dort sichern" }
    }
}
```

- [ ] **Step 2: Prüfen, dass der Block meldet und nichts verändert**

```powershell
cd "C:\Users\Jannes\Desktop\VS Folder 1"
$vorher = git -C "C:\Users\Jannes\Desktop\Gedanken" rev-parse HEAD
.\push.ps1 -Message "test | gedanken-check geprueft" -NoPush
$nachher = git -C "C:\Users\Jannes\Desktop\Gedanken" rev-parse HEAD
if ($vorher -eq $nachher) { "Zweitclone unveraendert - korrekt" } else { "FEHLER: Zweitclone wurde angefasst" }
```

Erwartet: Die Warnung erscheint (die Stände unterscheiden sich), und der zweite Clone ist
nachweislich unverändert.

- [ ] **Step 3: Verhalten ohne zweiten Clone prüfen**

```powershell
cd "C:\Users\Jannes\Desktop\VS Folder 1"
Rename-Item "C:\Users\Jannes\Desktop\Gedanken" "Gedanken-temp-aus"
.\push.ps1 -Message "test | ohne zweitclone" -NoPush
Rename-Item "C:\Users\Jannes\Desktop\Gedanken-temp-aus" "Gedanken"
```

Erwartet: Das Skript läuft ohne Fehler durch und gibt schlicht keine Warnung aus. Ein fehlender
Zweitclone darf den Publish nie blockieren.

**Falls der Rename scheitert** (offene Datei, Obsidian läuft): Schritt überspringen und
stattdessen `$zweit` testweise auf einen nicht existierenden Pfad setzen, das Skript laufen
lassen und den Pfad zurückändern.

- [ ] **Step 4: Commit**

```bash
cd "C:/Users/Jannes/Desktop/VS Folder 1"
git add push.ps1
git commit -m "push | meldet abweichenden Stand des Gedanken-Clones, ohne dort einzugreifen"
```

---

## Abschluss

- [ ] **Gesamtverifikation**

```bash
cd "C:/Users/Jannes/Desktop/VS Folder 1"
python algo/selfcheck.py
python algo/live_status.py --selftest
python tools/build_site.py
wc -l CLAUDE.md algo/CLAUDE.md
git log --oneline -12
```

Erwartet: Beide Python-Läufe grün, der Site-Build ohne neue unauflösbare Wikilinks,
`CLAUDE.md` rund 300 statt 488 Zeilen, und zwölf Commits mit sprechenden Messages statt
`wiki update`.

- [ ] **Bericht an den Nutzer**

Enthält zwingend: die in Task 1 liegengebliebenen Zweifelsfälle namentlich, die Anzahl der in
Task 7 als yfinance-only markierten Tage, und das Ergebnis des Zeitachsen-Abgleichs aus Task 6
Step 8.

- [ ] **Push** — macht der Nutzer selbst, einmal am Sessionende.

## Nicht in diesem Plan

**Spec-Sektion 3 (Backtest-Registry).** Eigener Plan, nach Abschluss dieses hier. Grund: 28
Thesen-Migrationen mit Zahlen-Regressionsprüfung sind ein eigenes Risikoprofil und würden
diesen Plan verdoppeln, ohne dass die anderen Sektionen davon abhängen.
