# Workflow-Kompaktierung — Design

**Datum:** 2026-08-16
**Status:** freigegeben (Brainstorming abgeschlossen, Umsetzungsplan folgt)
**Auslöser:** Nutzerwunsch — Ablauf optimieren, Zeit sparen, kompakter machen; explizit
einschließlich `CLAUDE.md`.

## Ziel

Den täglichen Ablauf verschlanken, ohne die Korrektheits-Standards aus
[[Algo-Trading: Arbeitsstandards]] anzutasten. Drei Hebel: weniger Kontext pro Session,
weniger redundante Protokollierung, weniger Handgriffe pro Handelstag.

Nicht-Ziel: neue Handelslogik, neue Strategien, Optik. Layer-0-Ziel (autonomer
IBKR-Handelsalgorithmus) bleibt unverändert; dieses Dokument betrifft ausschließlich den
Unterbau.

## Ausgangslage (gemessen am 2026-08-16)

| Kennzahl | Wert | Problem |
|---|---|---|
| `CLAUDE.md` | 488 Zeilen | lädt vollständig in *jede* Session, auch reine Wiki-Arbeit |
| Commits letzte 30 Tage | 539 | Message durchgehend `wiki update <Datum>` — Historie nicht auswertbar |
| `wiki/log.md` | 2769 Zeilen | Nutzer liest sie nicht |
| `algo/PLAN.md` | 857 Zeilen | Nutzer liest sie nicht |
| `algo/backtest_*.py` | 28 Dateien | je eigenes `main()`/argparse, laufen nach Erstellung nie wieder |
| echte `import yfinance` | 2 Dateien | Rest sind Kommentare/Warntexte in 15 weiteren Dateien |
| Gedanken-Clone | Stand 15.08., 21 uncommittete Dateien | Datenverlustrisiko |

## Entscheidungen des Nutzers

Aus dem Brainstorming-Dialog, verbindlich:

1. `CLAUDE.md` in zwei Dateien aufteilen (Haupt + `algo/CLAUDE.md`).
2. Aussagekräftige Commit-Messages, dafür seltener pushen (1×/Tag).
3. Weder `log.md` noch `PLAN.md` werden vom Nutzer gelesen — er fragt stattdessen nach.
4. Backtests auf eine Registry mit `--these <name>` konsolidieren.
5. Alle Tagesaufgaben (Daten, Bias, Journal, Backtest, Ingest, Live-Status) sind gleichrangig
   — keine darf durch die Umbauten langsamer werden.
6. Antwortlänge: knapp bei Routine, ausführlich bei Backtest-Ergebnissen.
7. yfinance komplett aus dem Projekt entfernen.
8. Session-Start-Check immer, als 3-Zeilen-Statuszeile.
9. Dual-Vault-Abgleich automatisieren.
10. Autonomie bleibt wie bisher (Ingest autonom, Rest nachfragen).

## Sektion 1 — `CLAUDE.md`-Split

Claude Code lädt eine `CLAUDE.md` aus einem Unterverzeichnis automatisch nach, sobald eine
Datei darin gelesen oder bearbeitet wird. Das trägt den Split ohne zusätzliche Mechanik.

**`CLAUDE.md` (~300 Zeilen)** behält: Sprache, Layer 1–3 (`raw/`, `wiki/`, `site/`),
Automatische Einsortierung, Seitenkonventionen, Versionskontrolle, Kontinuierliches Wachstum,
Operationen (Ingest/Query/Lint), `index.md`- und `log.md`-Format, Domänenkontext
`trading-ict`, graphify.

Layer 0 bleibt darin als **Kurzfassung von vier Zeilen** stehen — Zielsatz plus Verweis auf
`algo/CLAUDE.md`. Grund: Layer 0 begründet, warum das Wiki überhaupt existiert; fällt es aus
reinen Wiki-Sessions ganz heraus, verliert die Wiki-Arbeit ihren Zweckbezug.

**`algo/CLAUDE.md` (~185 Zeilen)** übernimmt vollständig: Layer 0 (Langfassung),
Algo-Trading: Arbeitsstandards, Roadmap zur IBKR-Anbindung, Protokoll- und Datenartefakte,
Domänenkontext `algo`.

Beide Dateien verlinken wechselseitig aufeinander, damit kein Standard unauffindbar wird.

**Nicht angetastet:** `CLAUDE.2.0.md` und `CLAUDE.1.0.md` bleiben als Rollback-Punkte
unverändert liegen. Der Split entsteht als neue Fassung, nicht durch Überschreiben der
Historie.

## Sektion 2 — Commit-Messages und Protokolle

Sektion 2 und 3 hängen zusammen: Weil der Nutzer die Protokolldateien nicht liest, ist die
Git-Historie die einzige Chronik, die noch jemand konsultiert. Also muss sie aussagekräftig
werden, und die Dateien dürfen schrumpfen.

**`push.ps1`:** Der Fallback `"wiki update <Datum>"` entfällt. Ohne `-Message` bricht das
Skript ab und schlägt eine Message aus `git diff --cached --shortstat` plus den geänderten
Pfaden vor. Bewusst ein Abbruch statt einer automatisch generierten Message: eine geratene
Message ist genauso wertlos wie `wiki update` und verdeckt das Problem nur.

**Push-Rhythmus:** Ingest-Schritt 7 in `CLAUDE.md` ändert sich von „nach jedem Ingest pushen"
auf „einmal am Ende der Session". Der Ingest gilt weiterhin erst mit Push als abgeschlossen —
nur der Zeitpunkt verschiebt sich ans Sessionende.

**`wiki/log.md`:** Der chronologische Verlauf wandert in die Git-Historie. Die Datei behält
nur, was kein Commit ausdrückt: offene Fragen, bewusste Abweichungen von den Konventionen,
Widerspruchsmarker. Bestehende Einträge werden **nicht gelöscht**, sondern nach
`wiki/log-archiv-bis-2026-08.md` verschoben — die 2769 Zeilen enthalten Entstehungsgründe, die
in keinem Commit stehen.

**`algo/PLAN.md`:** behält Backlog und Zustand, verliert die Log-Tabelle. Deren Inhalt wandert
ebenfalls ins Archiv (`algo/PLAN-archiv-bis-2026-08.md`).

**Folgeänderung:** `/tagesbericht` liest künftig `git log --since`, nicht mehr `wiki/log.md`.
Ohne diese Anpassung würde der Tagesbericht nach dem Umbau leer laufen.

**Unberührt:** Die Pflicht aus den Arbeitsstandards, jede neue These und jedes
Backtest-Ergebnis zu protokollieren, bleibt bestehen. Sie erfüllt sich künftig über
Commit-Message plus `PLAN.md`-Backlogeintrag statt über eine wachsende Log-Tabelle.

## Sektion 3 — Backtest-Registry

**Neu:** `algo/backtest.py` als einziger Einstiegspunkt.

```
python algo/backtest.py --these org_ce
python algo/backtest.py --these all
python algo/backtest.py --liste
```

Die 28 bestehenden `backtest_*.py` wandern nach `algo/thesen/` und melden sich über einen
Dekorator an:

```python
@these("org_ce", beschreibung="ORG C.E. wird zu X% angelaufen")
def run(bars, args): ...
```

**Bewusst mechanisch:** Das Innenleben der 28 Scripts bleibt unverändert. Nur `main()`/
argparse werden durch den Dekorator ersetzt. Eine inhaltliche Vereinheitlichung der Scripts
ist ausdrücklich nicht Teil dieses Umbaus — sie würde Zahlen verändern, und Zahlen zu
verändern ist bei einem reinen Aufräum-Schritt nicht zulässig.

**Pflichtprüfung:** Für jede migrierte These muss der Output vor und nach der Migration
identisch sein. Weicht eine Zahl ab, ist die Migration dieser These fehlerhaft und wird
zurückgenommen, nicht die Zahl akzeptiert.

`algo/selfcheck.py` wird um einen Registry-Check erweitert (jede registrierte These ist
aufrufbar, `--liste` deckt sich mit dem Dateibestand).

## Sektion 4 — yfinance entfernen

**Befund:** Nur `algo/fetch_yfinance.py` und `algo/live_status.py` importieren yfinance
tatsächlich. Die 15 weiteren Treffer sind Kommentare und Warntexte.

**Entscheidung des Nutzers:** TWS läuft ohnehin für den Datenbezug; `live_status.py` wird auf
den IBKR-Pfad umgestellt, wie ihn `/daten-1s` bereits nutzt.

**Umstellung von `live_status.py`:** Betroffen sind vier Stellen — `_download()` (`yf.download`),
der Import von `trading_day`/`flatten`/`SYMBOL` aus `fetch_yfinance`, `fetch_today()` und
`_bars_from_df()`. Ersatz aus `algo/fetch_ibkr.py`, das die nötigen Bausteine bereits
mitbringt: `_gateway_sicherstellen()` (startet das Gateway bei Bedarf selbst),
`fetch_symbol_day()`, `front_month()`, `day_windows()`.

**Abhängigkeit, die zuerst aufgelöst werden muss:** `live_status.py` importiert `trading_day`
und `flatten` aus `fetch_yfinance.py`. Diese Helfer sind quellenunabhängig und wandern nach
`algo/marktdaten.py`, bevor `fetch_yfinance.py` gelöscht wird.

**Symbolwechsel:** `live_status.py` läuft bisher auf `MNQ=F` (Micro, yfinance) und wird auf
**NQ** umgestellt — den E-mini-Nasdaq-100-Future, Punktwert $20, in `algo/pnl.py` bereits
hinterlegt. Nur NQ, nicht zusätzlich ES: der Live-Status bleibt ein Ein-Symbol-Zyklus, wie
bisher. Das deckt sich mit der Layer-0-Entscheidung vom 2026-08-15 (NQ/ES statt MNQ) und mit
der IBKR-1s-Abdeckung, die für NQ vorliegt.

> Begriffsklärung: „Mini NQ" ist hier der **E-mini** (`NQ`, $20/Punkt), nicht der Micro E-mini
> (`MNQ`, $2/Punkt). Die Kurse beider Kontrakte sind identisch — unterschieden sich nur
> Punktwert und Kontraktgröße. Sollte doch der Micro gemeint sein, ändern sich ausschließlich
> Symbolname und `pnl.py`-Eintrag, nicht der Datenpfad.

**Mitzuziehen:** `.claude/commands/algo-live-status.md` beschreibt den Zyklus in Titel und
Rumpf als „fuer MNQ". Die Beschreibung wird auf NQ/ES angepasst — sonst beschreibt der Skill
nach der Umstellung etwas anderes, als er tut.

**Löschen:** `algo/fetch_yfinance.py`, `algo/backfill_yfinance.py`, die yfinance-Warnblöcke in
`CLAUDE.md` (~15 Zeilen), die Kommentar-Erwähnungen in den 15 übrigen Dateien.

**Bewusst behalten:** Die Memory-Notiz zur Tick-Abweichung des yfinance-Feeds und der
Vault-Eintrag dazu bleiben als historischer Befund bestehen. Sie erklären, warum
`raw/marktdaten/`-Tage aus der yfinance-Ära weiterhin mit Vorsicht zu behandeln sind — die
Daten von damals liegen ja noch im Depot.

**Verifikationspflicht:** Vor dem Löschen von `fetch_yfinance.py` muss geklärt sein, welche
Tage in `raw/marktdaten/` ausschließlich aus yfinance stammen. Diese Tage werden in
`algo/PLAN.md` als „Herkunft yfinance, nicht tickgenau" vermerkt, damit die Information nicht
mit dem Modul verschwindet.

## Sektion 5 — Session-Start-Statuszeile

Regel in `CLAUDE.md`, kein neues Script. Zu Beginn jeder Session, ungefragt, drei Zeilen:

```
raw/:     <lose Dateien -> einsortiert / nichts offen>
Daten:    <Abdeckung NQ/ES 1s bis Datum | Lücken>
Offen:    <PLAN-Backlog kurz | Gedanken-Clone-Stand>
```

Die Prüfungen selbst existieren bereits (`tools/sort_marktdaten.py`, `tools/sort_bilder.py`,
die Abdeckungsprüfung aus `/daten-1s`). Neu ist nur, dass ihr Ergebnis unaufgefordert und in
fester Form am Sessionanfang erscheint.

**Grenze:** Die Statuszeile berichtet, sie repariert nicht. Findet sie eine Datenlücke, wird
sie gemeldet — geschlossen wird sie erst auf Ansage, gemäß Autonomie-Entscheidung (10c).
Ausnahme bleibt das Einsortieren loser Dateien, das laut `CLAUDE.md` ohnehin autonom läuft.

## Sektion 6 — Dual-Vault-Abgleich

**Befund:** `C:\Users\Jannes\Desktop\Gedanken` ist kein separater Ordner, sondern ein zweiter
Git-Clone desselben Repos (`github.com/Syle00/Gedanken`), Stand 2026-08-15, mit 21
uncommitteten Dateien — darunter frische TradingView-CSVs, die nur dort existieren.

**Konsequenz für den ursprünglichen Plan:** Ein Datei-Kopier-Sync wäre schädlich, weil er am
Git vorbei arbeitet und beim nächsten Pull Konflikte oder stille Überschreibungen erzeugt.
Der Abgleich ist ein Git-Problem, kein Kopier-Problem.

**Umsetzung:** `push.ps1` prüft nach erfolgreichem Push, ob der Gedanken-Clone hinter `origin`
liegt, und meldet das. Das eigentliche Nachziehen übernimmt der bestehende `/update`-Skill —
es entsteht kein neues Werkzeug.

**Sofortmaßnahme, unabhängig vom Rest:** Die 21 uncommitteten Dateien im Gedanken-Clone
werden gesichert. Kein pauschales `git add -A`: die TradingView-CSVs gehören nach dem
etablierten Muster in `raw/marktdaten/` einsortiert (`tools/sort_marktdaten.py`), und
projektfremde Dateien wie `Claude Setup.exe` gehören überhaupt nicht ins Repo. Jede der 21
Dateien wird einzeln zugeordnet, Zweifelsfälle bleiben liegen und werden gemeldet — wie es
die Einsortierungsregel in `CLAUDE.md` vorschreibt.

## Sektion 7 — Antwortlänge und Autonomie

Zwei Absätze in `CLAUDE.md`:

**Antwortlänge.** Routineaufgaben (Datennachlad, Einsortieren, Ingest, Statusabfragen) werden
knapp berichtet: Ergebnis, Zahl, eine Zeile Begründung. Details folgen auf Nachfrage.
Backtest-Ergebnisse, Datenqualitätswarnungen und alles mit Zahlen-Auswirkung auf den Algo
bleiben ausführlich — dort ist Kürze ein Korrektheitsrisiko.

**Autonomie.** Unverändert: Ingest und Einsortieren autonom, alles Übrige auf Ansage. Die
harte Sperre für Live-Handel mit echtem Geld aus der IBKR-Roadmap bleibt in jedem Fall
bestehen und wird von dieser Regel nicht berührt.

## Reihenfolge der Umsetzung

1. **Gedanken-Clone sichern** (Sektion 6, Sofortmaßnahme) — Datenverlustrisiko, unabhängig
   vom Rest, deshalb zuerst.
2. **Sektionen 1, 2, 7** — reine Textarbeit an `CLAUDE.md`, `push.ps1`, den Protokollen.
   Sofortiger Kontextgewinn, kein Risiko für Zahlen.
3. **Sektionen 4, 5, 6** — Code-Änderungen mit überschaubarem Umfang.
4. **Sektion 3** — größter Aufwand, kleinster Sofortnutzen, deshalb zuletzt.

## Risiken

| Risiko | Gegenmaßnahme |
|---|---|
| Backtest-Migration verändert Zahlen | Output-Vergleich vor/nach je These; Abweichung = Migration zurücknehmen |
| `live_status.py` ohne laufendes Gateway | `_gateway_sicherstellen()` startet es; schlägt das fehl, klare Fehlermeldung statt stiller Leerausgabe |
| `/tagesbericht` läuft nach Log-Umbau leer | Umstellung auf `git log` ist Teil von Sektion 2, nicht Folgearbeit |
| Herkunftswissen zu yfinance-Tagen geht verloren | Vermerk in `algo/PLAN.md` vor dem Löschen des Moduls |
| Gespaltene `CLAUDE.md`, Standard wird übersehen | Wechselseitige Verlinkung; `algo/CLAUDE.md` lädt bei jedem Zugriff auf `algo/` |

## Offene Punkte

Keine. Die TWS-Frage aus Sektion 4 ist geklärt (TWS läuft für den Datenbezug, `/daten-1s` ist
der Pfad).
