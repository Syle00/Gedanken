# Main-Agent ("Wachhund") — Design

**Datum:** 2026-08-25
**Status:** entworfen, nicht implementiert
**Ziel:** Ein Aufseher über alle geplanten Läufe des Vaults — startet sie, misst Korrektheit,
Aktivität und Laufzeit, und repariert Fehlschläge selbstständig.

## Problem

Die Commands unter `.claude/commands/` beschreiben in ihrem Text bereits einen Zeitplan
("für den Cron So–Do 20:00"), aber es gibt keinen. `CronList` ist leer, es existiert kein
Windows-Task. Läuft ein Command nicht, fällt das erst auf, wenn die Bias-Datei fehlt.
Die Cowork-Briefings (Claude Desktop, "Geplante Aufgaben", laufen lokal in diesem Ordner)
hinterlassen keine Spur im Repo — am 2026-08-25 wurde der 7:00-Lauf übersprungen und der
Ausfall war nirgends ablesbar.

## Entscheidungen

| Frage | Entscheidung |
|---|---|
| Rolle | Dirigent **und** Wächter |
| Quelle für Zeitplan/Erfolgskriterium | Frontmatter im Command selbst (eine Quelle der Wahrheit) |
| Zeitgeber | **Ein** Windows-Aufgabenplaner-Eintrag alle 10 min → `tools/agent_tick.py` |
| Arbeitsteilung | Dickes Python, LLM nur im Fehlerfall (grüner Tick = 0 Token) |
| Cowork | Datei als Brücke, beide Richtungen |
| Reparatur-Autonomie | Autofix erlaubt, gebunden an vier Regeln (siehe unten) |

## Architektur

Drei neue Dateien:

    tools/agent_tick.py            Taktgeber. Kein LLM.
    .claude/commands/wachhund.md   Reparatur-Agent. Nur im Fehlerfall gerufen.
    algo/live/agent-runs.csv       Lauf-Register (append-only).

Ablauf eines Ticks:

    1. .claude/commands/*.md und .claude/skills/*/SKILL.md einlesen
       -> alle Einträge mit `schedule:` bilden den Zeitplan
    2. agent-runs.csv lesen -> wann lief was zuletzt?
    3. nichts fällig/verpasst -> exit 0, null Token
    4. claude -p "/<command>" starten, Stoppuhr mitlaufen lassen
    5. prüfen: exit-code | Laufzeit vs. timeout | expect erfüllt?
    6. Zeile nach agent-runs.csv
    7. rot -> claude -p "/wachhund <befund-json>"

**Verantwortungsgrenze:** `agent_tick.py` entscheidet und misst, urteilt nie.
`/wachhund` urteilt und repariert, plant nie. Deshalb ist `agent_tick.py` vollständig
ohne Modellstart testbar — Schritt 4 ist eine Zeile, die im Trockenlauf entfällt.

## Frontmatter-Vertrag

Vier optionale Schlüssel, rein additiv. Bestehende Commands funktionieren unverändert
weiter, solange niemand einen Kopf ergänzt.

    ---
    description: ...              # bleibt wie es ist
    schedule: "0 20 * * 0-4"      # Cron-Syntax. Fehlt er -> wird nie gestartet
    expect: "raw/journal/Daily Bias {next_trading_day}.md"
    timeout: 15m                  # Überschreitung = rot. Default 30m
    extern: true                  # optional: von anderswo geplant, nur beobachten
    ---

`expect` kennt zwei Formen:

| Form | Bedeutung |
|---|---|
| `pfad/datei.md` | Datei existiert danach |
| `changed: pfad/datei.csv` | Datei ist seit Laufbeginn jünger geworden |
| *fehlt* | nur Exit-Code und Laufzeit zählen |

Platzhalter: `{today}`, `{yesterday}`, `{next_trading_day}`, `{next_kw}`, `{next_year}`.
Aufgelöst über `next_trading_day()` / `next_monday()` aus `algo/bias_levels.py` —
dieselbe Logik, die die Bias-Commands zur Erzeugung benutzen, damit Erwartung und
Erzeugung nicht auseinanderlaufen können.

**Auto-Integration:** Der Scan liest Commands *und* Skills. Ein neuer Skill mit
`schedule:` ist beim nächsten Tick im Zeitplan, ohne dass irgendwo etwas registriert
werden muss. Ohne `schedule:` wird er still ignoriert.

### Startbelegung

| Eintrag | schedule | expect |
|---|---|---|
| `bias-vorlage-daily` | `0 20 * * 0-4` | `raw/journal/Daily Bias {next_trading_day}.md` |
| `bias-vorlage-weekly` | `0 20 * * 5` | `raw/journal/Weekly Bias KW{next_kw} {next_year}.md` |
| `daten-1s` | `0 23 * * 1-5` (nach US-Handelsschluss) | `changed: raw/marktdaten/1s-abdeckung.csv` |
| `update` | `30 6 * * *` (vor dem Morgenbriefing) | *(keins — Exit-Code genügt)* |
| `briefing-morgens` | `0 7 * * *`, `extern: true` | `algo/live/briefing-{today}-morgens.md` |
| `briefing-abends` | `0 20 * * *`, `extern: true` | `algo/live/briefing-{today}-abends.md` |

Zwei Commands bekommen bewusst **kein** `schedule`:

- `algo-live-status` — ein `/loop`-Command für Zeiten, in denen der Nutzer am Rechner sitzt
  und der Markt offen ist. Ihn zu planen hieße, dauernd "Markt geschlossen"-Läufe zu
  protokollieren.
- `tagesbericht` — gibt laut Schritt 6 seines Commands **nur im Chat** aus und schreibt
  keine Datei. Ein headless geplanter Lauf schriebe ins Leere, und `expect` wäre nicht
  formulierbar. Soll er geplant werden, muss er zuerst eine Datei schreiben — eine eigene
  Änderung, nicht Teil dieses Designs. Das Cowork-Abendbriefing deckt den Zweck ab.

## Lauf-Register

`algo/live/agent-runs.csv`, append-only. Eine Spalte je Prüffrage:

    zeit_start,command,ausloeser,dauer_s,exit,expect_ok,status,notiz
    2026-08-25T20:00,bias-vorlage-daily,plan,86,0,1,gruen,
    2026-08-25T20:10,daten-1s,plan,912,0,0,rot,"expect verfehlt: 1s-abdeckung.csv unveraendert"
    2026-08-26T07:00,briefing-morgens,extern,,,0,rot,"ausgeblieben (Cowork uebersprungen)"

`ausloeser` ist eines von `plan`, `nachhol`, `extern`.

**Aktivität hängt am `expect`, nicht an der Registerzeile.** Ruft der Nutzer `/daten-1s`
selbst in einer Session auf, sieht der Tick davon nichts — er dürfte daraus also nicht
"seit 48 h inaktiv" folgern. Ist die erwartete Datei da, ist alles gut, egal wer sie
erzeugt hat. Das Register protokolliert, `expect` urteilt.

## Eskalation

| Befund | Reaktion | Modellstart |
|---|---|---|
| Verpasst (Rechner war aus) | Beim nächsten Tick nachholen | nein |
| Exit ungleich 0 | 2x wiederholen; hilft das, grün | nein |
| Exit ungleich 0 nach 2 Versuchen | Wachhund | **ja** |
| Timeout überschritten | Prozess beenden, Wachhund | **ja** |
| `expect` verfehlt | Wachhund | **ja** |
| Datenlücke in `1s-abdeckung.csv` | Wachhund -> `/daten-1s backfill <von> <bis>` | **ja** |
| Externer Lauf ausgeblieben | Nur in den Report | nein |

Coworks Planer ist von außen nicht steuerbar — ein ausgebliebenes Briefing kann der
Wachhund melden, aber nicht starten.

## Autofix — vier Regeln

1. **Nie auf `main`.** Arbeit auf `agent/autofix-<datum>`, Commit dort. `push.ps1` ist
   bereits branch-aware (`git push -u origin $branch`, Zeile 141–146) und schiebt den
   Branch, nicht `main`. Gemergt wird nichts ohne den Nutzer. Der Morgenreport nennt den
   Branch zur Freigabe.
2. **Reparatur zählt nur, wenn der Lauf danach grün ist.** Fixen, Command erneut starten,
   `expect` ein zweites Mal prüfen. Bleibt es rot: Fix verwerfen (`git checkout`), nur
   Traceback und Diagnose berichten. So überlebt keine Reparatur, die nur plausibel aussah.
3. **Sperrliste** — nie angefasst, auch nicht auf einem Branch:
   - `raw/**` (Inhalt laut `CLAUDE.md` unveränderlich; Marktdaten "wie Gold")
   - `algo/.secrets.yaml`, `journal/.secrets.yaml`
   - alles auf dem IBKR-Order-Pfad (harte Live-Handels-Sperre bleibt)
   - `CLAUDE.md`, `algo/CLAUDE.md`, `push.ps1`
   - Merge-Konflikte (`/update` sagt: melden, nicht auflösen)
4. **Ein Autofix-Versuch pro Command und Nacht.** Kein Reparaturkreisel.

**Wer schreibt `algo/live/agent-status.md`:** grundsätzlich `agent_tick.py`, bei **jedem**
Tick neu — sonst läse das Morgenbriefing nach einer grünen Nacht einen veralteten Stand.
Der Tick schreibt den deterministischen Teil (Zusammenfassung des Registers: was lief, wie
lange, was ist grün/rot, welche Datenlücken bestehen). Lief ein Wachhund, hängt dieser
seinen Teil an: Diagnose, was repariert wurde, welcher Branch auf Freigabe wartet.

## Cowork-Brücke

    Cowork 7:00  --schreibt--> algo/live/briefing-2026-08-26-morgens.md
                                          ^
                                          | prüft: da? pünktlich?
                                          |
    agent_tick.py --schreibt--> algo/live/agent-status.md
                                          |
    Cowork 7:00  <----liest---------------+

Zwei Schritte **manuell in Claude Desktop** (von außen nicht erreichbar):

1. Je ein Satz in die Anweisung beider Briefings: Briefing zusätzlich nach
   `algo/live/briefing-<YYYY-MM-DD>-<morgens|abends>.md` schreiben; zu Beginn
   `algo/live/agent-status.md` lesen und offene Punkte in einen Abschnitt "Vault & Algo"
   übernehmen.
2. **Duplikate aufräumen.** Stand 2026-08-25 existieren vier geplante Aufgaben für zwei
   Zwecke ("Daily briefing" / "Morgen-Briefing 06:00", "Abend briefing" /
   "Abend-Briefing 20:00"). Bleiben alle vier, meldet der Wächter täglich zwei Ausfälle,
   die keine sind — und es ist die wahrscheinlichste Erklärung für das "Übersprungen"
   um 7:00.

## Test

Beide Schalter ohne Modellstart:

- `python tools/agent_tick.py --dry-run` — zeigt, was jetzt fällig wäre, wie die
  Platzhalter aufgelöst wurden und ob `expect` gerade erfüllt ist. Startet nichts.
  Auch das Werkzeug zum Prüfen eines neu eingehängten Skill-Kopfes.
- `python tools/agent_tick.py --selftest` — `assert`-Selbstcheck gegen ein temporäres
  Verzeichnis mit festen Zeitstempeln: Cron-Auswertung, Platzhalter, `expect` in beiden
  Formen, Verpasst-Erkennung, Timeout. Kein Framework, eine Datei.

## Rollout

Vier Stufen, jede für sich nützlich:

1. `agent_tick.py` + Frontmatter für die vier geplanten Einträge, **nur `--dry-run`**. Ein paar Tage
   beobachten, ob die Fälligkeiten stimmen.
2. Windows-Task an, Wachhund-Aufruf deaktiviert. Es wird gestartet und protokolliert,
   Probleme landen nur im Register.
3. `/wachhund` scharf, aber ohne Autofix — nur Diagnose, Backfill und Report.
4. Autofix an.

Zeigt Stufe 2, dass `expect` bei `/daten-1s` falsch gedacht war, fällt das auf, bevor
nachts jemand anfängt, Code zu reparieren.

## Bewusst weggelassen

- **Keine Erfassung manueller Läufe.** Bräuchte einen Session-Hook; `expect` deckt den
  Zweck ab (siehe Lauf-Register).
- **Kein eigener Scheduler.** Ein Windows-Task-Eintrag, der Rest ist Cron-Syntax in
  Frontmatter.
- **Keine Registry-Datei.** Der Ordner-Scan *ist* die Registry.
- **Keine Weboberfläche/Dashboard.** `agent-runs.csv` und `agent-status.md` genügen;
  das Morgenbriefing ist die Ansicht.
