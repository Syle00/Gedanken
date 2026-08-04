# Algo Live-Status-Loop — Design

**Datum:** 2026-08-04
**Status:** Approved, bereit fuer Implementierungsplanung

## Ziel

Waehrend einer offenen Claude-Code-Session soll sich MNQ-Kursdaten alle 10 Minuten
automatisch aktualisieren lassen, damit Claude einen Statusbericht geben kann: wo
stehen wir, deckt sich das mit den vom Algo erkannten Signalen (Erwartung), und was
ist die Einschaetzung fuer den naechsten Schritt. Das Werkzeug (Skript + Slash-Command)
soll dauerhaft im Repo liegen und jederzeit — auch weit in der Zukunft — mit einem
einzigen Aufruf aktivierbar sein. Es soll NICHT rund um die Uhr im Hintergrund laufen;
Start/Stop ist manuell.

## Nicht-Ziele (YAGNI, bewusst ausgeschlossen)

- Kein automatischer Session-Start oder Hintergrund-Betrieb unabhaengig von einer
  offenen Claude-Code-Session.
- Kein Claude-Cloud-Schedule (`CronCreate`): Minimum-Takt dort ist 1 Stunde (keine
  10-Minuten-Intervalle moeglich) und die Cloud-Sandbox hat keinen Zugriff auf lokale
  Dateien (`raw/marktdaten/`) — muesste ueber GitHub laufen und wuerde bei jedem Lauf
  Log-Commits erzeugen. Passt nicht zum Anforderungsprofil.
- Kein neuer allgemeiner Skill nach `writing-skills`-Muster (SKILL.md) — das ist
  projektspezifisches Tooling fuer dieses Vault, keine wiederverwendbare, technologie-
  uebergreifende Technik.
- Kein Schreiben in `raw/marktdaten/` durch den Live-Loop — dieser Layer bleibt
  unveraenderlich und ist fuer finale (TradingView-/yfinance-Backfill-)Exporte reserviert.

## Architektur

Drei Teile, die bestehende Bausteine wiederverwenden statt sie zu duplizieren:

| Teil | Datei | Aufgabe |
|---|---|---|
| Fetch + Detect | `algo/live_status.py` (neu) | Zieht den heutigen Handelstag (alle 6 Timeframes: 1m/5m/15m/1h/4h/1d) per `yfinance`, analog zu `algo/fetch_yfinance.py`, aber nach `algo/live/<datum>/` statt `raw/marktdaten/` — **ueberschreibt bei jedem Lauf** (kein Immutability-Konflikt, weil ausserhalb von `raw/`). Baut `Bar`-Objekte direkt aus dem yfinance-DataFrame (kompatibel zu `tools/analyze_ohlc.py::Bar`), damit dieselben Detektor-Funktionen ohne CSV-Umweg laufen: `fvgs`, `sweeps`, `structure_breaks`, `macro_windows`, `untouched_levels` aus `tools/analyze_ohlc.py` auf den 5m-Daten, sowie `algo/rules.py::plan_trade(bars, now)` fuer ein aktuelles Silver-Bullet-Setup. Vergleicht das Ergebnis mit dem vorherigen Snapshot (`algo/live/<datum>/state.json`), um nur **neue Ereignisse seit dem letzten Lauf** herauszuarbeiten (neuer Sweep, neues FVG, Fenster betreten/verlassen, Setup entstanden/entfallen). Gibt eine kompakte JSON-Zusammenfassung auf stdout aus — reine Fakten, keine Prosa. |
| Report | `.claude/commands/algo-live-status.md` (neu) | Slash-Command: ruft das Skript auf, liest die JSON-Ausgabe plus die letzten Zeilen von `algo/live/<datum>-status-log.md` fuer Kontinuitaet, und laesst Claude daraus einen deutschen Statusbericht schreiben (Stand / Abgleich mit Algo-Signalen / Einschaetzung naechster Schritt). Wird an das Log angehaengt. |
| Takt | `/loop 10m /algo-live-status` | Nutzt den bestehenden `loop`-Skill (self-pacing via `ScheduleWakeup`), laeuft nur waehrend einer offenen Session. Start/Stop manuell per Zuruf ("starte den Live-Loop" / "stoppen"). Persistenz ist automatisch erfuellt, sobald Skript und Slash-Command normal ins Repo committed sind — kein zusaetzlicher Mechanismus noetig. |

## Datenfluss pro Zyklus

1. yfinance-Fetch fuer den heutigen NY-Handelstag (alle 6 Timeframes).
2. Schreiben nach `algo/live/<datum>/MNQ <datum> <tf>.csv` (ueberschreibend).
3. Detektoren auf den 5m-`Bar`-Liste (`fvgs`, `sweeps`, `structure_breaks`,
   `macro_windows`, `untouched_levels`) + `plan_trade(bars, now)`.
4. Diff gegen `algo/live/<datum>/state.json` → Liste neuer Ereignisse seit letztem Lauf.
5. JSON-Summary (aktueller Preis, aktives Makro-/Silver-Bullet-Fenster, neue Ereignisse,
   `plan_trade`-Ergebnis oder `null`) auf stdout.
6. Claude liest JSON + letzte Log-Zeilen, schreibt Bericht, haengt ihn an
   `algo/live/<datum>-status-log.md` an, aktualisiert `state.json`.

## Vergleichsbasis fuer "war das erwartet?"

Ausschliesslich die vom Algo erkannten Signale (Makro-Fenster-Expansion, Sweeps,
Structure Breaks, FVGs, `plan_trade`-Setup) — **nicht** der manuelle Journal-Daily-Bias.
Der Bericht stellt die neuen Live-Ereignisse den bereits vom Algo erwarteten Mustern
gegenueber (z.B. "Sweep im NY-AM-Fenster wie erwartet" vs. "Kein FVG im Fenster
entstanden, Setup entfaellt").

## Umfang

Der Report laeuft durchgehend alle 10 Minuten, auch ausserhalb der drei
Silver-Bullet-Fenster (London 3-4, NY AM 10-11, NY PM 14-15 Uhr NY) — dann ohne
Setup-Teil, nur Struktur/Sweeps/Preis-Kontext.

## Fehlerbehandlung

- Markt geschlossen (Wochenende/Feiertag/Sonntagabend-Luecke) oder leere
  yfinance-Antwort: Skript meldet das explizit im JSON (`"market_data": null` +
  Grund), der Report vermerkt "Markt geschlossen" / "Datenabruf fehlgeschlagen,
  letzter Stand: HH:MM NY" statt zu interpolieren.
- yfinance-Timeout: gleiche Behandlung wie leere Antwort, kein Crash des Loops.

## Testing

`python algo/live_status.py --dry-run <datum>` gegen einen bereits abgeschlossenen
Handelstag aus `raw/marktdaten/` (z.B. 31.07.2026), um Detektor-Aufruf, Diff-Logik
und JSON-Struktur ohne Live-Yahoo-Abhaengigkeit zu verifizieren — analog zum
Selbstcheck in `algo/rules.py` (`demo()`).

## Offene Entscheidungen fuer die Implementierungsplanung

Keine — alle Kernfragen sind durch die Brainstorming-Antworten geklaert. Feinschliff
(genaues JSON-Schema, exakter Diff-Algorithmus, Log-Zeilenformat) gehoert in den
Implementierungsplan, nicht in dieses Design-Dokument.
