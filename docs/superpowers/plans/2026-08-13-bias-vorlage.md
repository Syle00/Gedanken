# Bias-Vorlage Implementation Plan

> **Status 2026-08-15: Task 1-4 umgesetzt. Zwei Abweichungen vom Plantext unten -- der ist ab
> hier historisch, massgeblich sind `algo/README.md` und die beiden Command-Dateien.**
>
> 1. **News kommen nicht per WebFetch.** Der geplante WebFetch auf
>    `forexfactory.com/calendar?day=...` liefert **HTTP 403** (Cloudflare-Botschutz,
>    reproduziert 2026-08-15) -- dieser Weg haette nie funktioniert. Ersetzt durch den
>    offiziellen JSON-Feed `nfs.faireconomy.media/ff_calendar_thisweek.json`, abgerufen von
>    `algo/bias_levels.py` selbst. Die Commands rufen daher **ein** Skript statt Skript +
>    WebFetch auf, und `bias_levels.py` bestimmt auch das Zieldatum (`--next` / `--weekly`)
>    statt `date -d tomorrow` im Command-Prompt.
> 2. **Zweite News-Quelle statt verschobener Cron-Zeit.** ForexFactory veroeffentlicht nur die
>    *laufende* Woche (`ff_calendar_nextweek.json` -> HTTP 404), kennt freitags abends also die
>    Zielwoche nicht. Der Nutzer will den Weekly-Lauf aber ausdruecklich **freitags 20:00**
>    (Entscheid 2026-08-15). Geloest ueber einen Fallback auf den
>    **TradingView-Wirtschaftskalender** (beliebiger Datumsbereich); Zeitstempel beider Quellen
>    auf KW33 gegengeprueft und deckungsgleich. Cron-Zeiten daher wie urspruenglich geplant:
>    Daily **So-Do 20:07**, Weekly **Fr 20:07**.
>
> **Task 4 konkret:** zwei Cloud-Routinen, `trig_01RqWifxLRoF1cMSXntn8SDN` (Daily) und
> `trig_01HuaCqVbDB6MXfqb7tR9hff` (Weekly). Sie laufen in einem eigenen Cloud-Checkout und
> **committen + pushen** ihre Datei nach `main` -- ohne das waere sie nach dem Lauf verloren.
> Das weicht bewusst von der Spec-Regel "kein Push" ab (Nutzerentscheid 2026-08-15).

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Automatisch vorbefüllte Daily-/Weekly-Bias-Dateien (News, Marktdaten-Levels, Wiki-Bezug, Claude-Einschätzung) per Scheduled Cron erzeugen, damit der Nutzer nur noch seinen eigenen Bias-Text ergänzt.

**Architecture:** Ein neues Python-Skript `algo/bias_levels.py` liefert Wochen-/Vortages-Range als JSON (reuse von `algo/backtest_common.py::load_rows`). Zwei neue Slash-Commands (`.claude/commands/bias-vorlage-daily.md`, `.claude/commands/bias-vorlage-weekly.md`) orchestrieren pro Lauf: `algo/live_status.py` (NDOG/NWOG/org_ce, bereits vorhanden), `algo/bias_levels.py` (Wochen-/Vortages-Range), ForexFactory-WebFetch (News), Wiki-Wikilinks, eigene Einschätzung — und schreiben die Zieldatei nach `raw/journal/`. Zwei Scheduled Cloud Agents (via `schedule`-Skill) rufen die Commands werktags bzw. freitags um 20:00 auf.

**Tech Stack:** Python 3 (stdlib + bereits vorhandene `algo/`-Module), Markdown-Slash-Commands (`.claude/commands/`), `schedule`-Skill für Cron.

**Spec:** `docs/superpowers/specs/2026-08-13-bias-vorlage-design.md`

## Global Constraints

- Levels immer als Tabelle darstellen (Nutzerkonvention).
- Fehlschlagender News-Abruf darf den Lauf nicht abbrechen — Datei wird trotzdem erzeugt, mit `⚠️`-Platzhalter im News-Abschnitt.
- Kein automatischer `git add`/`push.ps1`-Aufruf aus dem Skill/Command heraus — das Schreiben der Datei ist der einzige Effekt (siehe Spec, "Nicht Teil dieser Spec").
- `algo/`-Konventionen befolgen: Punktwert-/Zeit-Standards aus `algo/README.md` gelten unverändert weiter, hier nicht neu betroffen (kein P&L-Code).
- Bestehende Module wiederverwenden statt duplizieren: `algo/backtest_common.py::load_rows`, `algo/live_status.py` CLI-Ausgabe.

---

## Task 1: `algo/bias_levels.py` — Wochen-/Vortages-Range

**Files:**
- Create: `algo/bias_levels.py`
- Test: inline `demo()` im selben File (Projektkonvention, siehe `algo/backtest_common.py::demo()` — kein pytest im Repo für `algo/`-Skripte)

**Interfaces:**
- Consumes: `load_rows(symbol: str = "MNQ") -> list[dict]` aus `algo/backtest_common.py` (Felder: `day: date, open/close/high/low/range: float, ret_pct: float, bullish: bool`)
- Produces:
  - `week_range(rows: list[dict], target_day: date) -> dict | None` — `{"high": float, "low": float, "days": int}` oder `None`
  - `yesterday_range(rows: list[dict], target_day: date) -> dict | None` — `{"day": str, "high": float, "low": float, "close": float}` oder `None`
  - `compute(target_day: date, weekly: bool) -> dict` — `{"day": str, "weekly_range": ..., "yesterday_range": ...}` (Key `yesterday_range` fehlt wenn `weekly=True`)
  - CLI: `python algo/bias_levels.py [YYYY-MM-DD] [--weekly] [--demo]`, druckt JSON auf stdout (Default-Tag: heute)

- [ ] **Step 1: Skript mit Implementierung + `demo()`-Selbstcheck schreiben**

```python
#!/usr/bin/env python3
"""Wochen-/Tages-Range-Kennzahlen fuer die Bias-Vorlage (raw/journal/Daily Bias */Weekly
Bias *). Reuse: load_rows() aus backtest_common.py (Open/High/Low/Close pro Handelstag) --
kein eigenes CSV-Parsing.

Aufruf:
    python algo/bias_levels.py                  # Levels fuer heute (Daily-Modus)
    python algo/bias_levels.py 2026-08-14        # Levels fuer diesen Handelstag
    python algo/bias_levels.py 2026-08-14 --weekly  # nur Wochen-Range, keine Vortages-Range
    python algo/bias_levels.py --demo            # reiner Funktions-Selbstcheck
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from backtest_common import load_rows  # noqa: E402


def week_range(rows: list[dict], target_day: date) -> dict | None:
    """High/Low aller Handelstage in der ISO-Woche von target_day, bis einschliesslich
    des letzten verfuegbaren Tages <= target_day. None wenn kein Tag der Woche vorliegt
    (z.B. Montagfrueh vor dem ersten Tick)."""
    iso_week = target_day.isocalendar()[:2]
    week_rows = [r for r in rows
                 if r["day"] <= target_day and r["day"].isocalendar()[:2] == iso_week]
    if not week_rows:
        return None
    return {"high": max(r["high"] for r in week_rows),
            "low": min(r["low"] for r in week_rows),
            "days": len(week_rows)}


def yesterday_range(rows: list[dict], target_day: date) -> dict | None:
    """H/L/C des letzten Handelstages vor target_day. None wenn keiner vorliegt."""
    prior = [r for r in rows if r["day"] < target_day]
    if not prior:
        return None
    r = prior[-1]
    return {"day": r["day"].isoformat(), "high": r["high"], "low": r["low"], "close": r["close"]}


def compute(target_day: date, weekly: bool) -> dict:
    rows = load_rows("MNQ")
    out = {"day": target_day.isoformat(), "weekly_range": week_range(rows, target_day)}
    if not weekly:
        out["yesterday_range"] = yesterday_range(rows, target_day)
    return out


def demo() -> None:
    rows = [
        {"day": date(2026, 8, 10), "open": 100.0, "close": 105.0, "high": 106.0, "low": 99.0},
        {"day": date(2026, 8, 11), "open": 105.0, "close": 103.0, "high": 107.0, "low": 102.0},
        {"day": date(2026, 8, 12), "open": 103.0, "close": 110.0, "high": 111.0, "low": 103.0},
    ]
    wr = week_range(rows, date(2026, 8, 12))
    assert wr == {"high": 111.0, "low": 99.0, "days": 3}, wr
    yr = yesterday_range(rows, date(2026, 8, 12))
    assert yr == {"day": "2026-08-11", "high": 107.0, "low": 102.0, "close": 103.0}, yr
    assert week_range(rows, date(2026, 8, 3)) is None, "andere ISO-Woche muss None liefern"
    assert yesterday_range(rows, date(2026, 8, 10)) is None, "kein Vortag in rows -> None"
    print("demo ok")


def main(argv: list[str] | None = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("day", nargs="?", help="YYYY-MM-DD, Default: heute")
    ap.add_argument("--weekly", action="store_true", help="nur weekly_range berechnen")
    ap.add_argument("--demo", action="store_true", help="Funktions-Selbstcheck, kein Dateizugriff")
    a = ap.parse_args(argv)

    if a.demo:
        demo()
        return 0

    target = date.fromisoformat(a.day) if a.day else date.today()
    print(json.dumps(compute(target, a.weekly), default=str, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Selbstcheck laufen lassen**

Run: `python algo/bias_levels.py --demo`
Expected: `demo ok` wird gedruckt, Exit-Code 0.

- [ ] **Step 3: Realen Lauf gegen vorhandene Daten pruefen**

Run: `python algo/bias_levels.py 2026-08-13`
Expected: JSON mit `weekly_range` (high/low/days aus der KW32-Daten in `raw/marktdaten/`) und
`yesterday_range` (12.08.2026). Kein Traceback. Stimmen die Zahlen plausibel mit
`raw/journal/Weekly Bias KW32 2026.md` überein (grobe Prüfung, keine exakte Übereinstimmung
nötig, da dort andere Quelle).

- [ ] **Step 4: Commit**

```bash
git add algo/bias_levels.py
git commit -m "add | algo/bias_levels.py fuer Wochen-/Vortages-Range der Bias-Vorlage"
```

---

## Task 2: Command `bias-vorlage-daily`

**Files:**
- Create: `.claude/commands/bias-vorlage-daily.md`

**Interfaces:**
- Consumes: `algo/bias_levels.py` CLI (Task 1), `algo/live_status.py` CLI (bereits vorhanden, liefert `ndog_today`, `nwog_today`, `org_ce`, `ndog_open_history`, `nwog_open_history`, `price`)
- Produces: `raw/journal/Daily Bias YYYY-MM-DD.md` beim Ausführen von `/bias-vorlage-daily`

- [ ] **Step 1: Command-Datei schreiben**

```markdown
---
description: Erzeugt die vorbefuellte Daily-Bias-Datei fuer den naechsten Handelstag (News, Levels, Wiki-Bezug, eigene Einschaetzung) -- fuer den Scheduled Cron um 20:00 werktags oder manuellen Aufruf am Vorabend
---

Erzeuge `raw/journal/Daily Bias YYYY-MM-DD.md` fuer den naechsten Handelstag.

1. **Zieldatum bestimmen.** `date -d tomorrow +%Y-%m-%d`. Faellt das Ergebnis auf Samstag
   oder Sonntag, stattdessen `date -d "next monday" +%Y-%m-%d` verwenden. Das Ergebnis ist
   `<ZIEL>` fuer den Rest dieses Laufs.

2. **News (Red/Orange Folder).** WebFetch auf
   `https://www.forexfactory.com/calendar?day=<ZIEL als "mmmDD.YYYY", z.B. aug14.2026>`
   mit dem Auftrag, alle Events mit Impact-Farbe Red oder Orange fuer diesen Tag als Liste
   (Uhrzeit NY, Event-Name, Impact) zu extrahieren. Uhrzeit zusaetzlich nach DE-Zeit umrechnen
   (Sommerzeit beachten, analog zum bestehenden Muster in `raw/Daily Bias 13.08.md`: "PPI News
   um 14.30 DE Zeit also 8.30 Ny"). Schlaegt der Abruf fehl oder liefert kein auswertbares
   Ergebnis (Layout-Aenderung, Netzwerkfehler): NICHT abbrechen, sondern im News-Abschnitt
   `⚠️ News-Abruf fehlgeschlagen, manuell auf forexfactory.com pruefen` eintragen und mit den
   naechsten Schritten weitermachen.

3. **NDOG/NWOG/ORG-Levels.** `python algo/live_status.py` ausfuehren (frischer Live-Lauf, siehe
   [[Immer frische Marktdaten]] -- niemals einen aelteren Lauf aus diesem oder einem frueheren
   Gespraech wiederverwenden). Aus der JSON-Ausgabe `ndog_today` (Open/Close), `nwog_today`
   (falls nicht null, nur montags gesetzt) und `org_ce` (Gap + C.E.-Level) entnehmen. Ist
   `market_data: false`, das im generierten Dokument als `⚠️ Live-Daten nicht verfuegbar (Markt
   geschlossen oder Datenfehler)` vermerken statt Platzhalter-Zahlen zu erfinden.

4. **Wochen-/Vortages-Range.** `python algo/bias_levels.py <ZIEL>` ausfuehren. `weekly_range`
   (high/low/days) und `yesterday_range` (high/low/close) aus der JSON-Ausgabe entnehmen.

5. **Levels-Tabelle bauen** (immer als Markdown-Tabelle, nicht als Fliesstext):

   | Level | Open | Close |
   |---|---|---|
   | NWOG | ... | ... |
   | NDOG | ... | ... |

   Darunter: Weekly Range (High/Low aus Schritt 4), gestrige Daily Range H/L/C (aus Schritt 4),
   ORG-C.E. (aus Schritt 3, falls vorhanden). Fehlt ein Wert (null/None), die Zeile weglassen
   statt eine erfundene Zahl einzutragen.

6. **Weekly-Bias-Rueckverlinkung.** ISO-Kalenderwoche von `<ZIEL>` bestimmen
   (`date -d <ZIEL> +%V`, Jahr `date -d <ZIEL> +%Y`). Nach
   `raw/journal/Weekly Bias KW<NN> <JAHR>.md` suchen (Glob). Existiert die Datei: Wikilink
   `[[Weekly Bias KW<NN> <JAHR>]]` einfuegen. Existiert sie nicht: den Hinweis
   `_(noch kein Weekly Bias fuer diese Woche geschrieben)_` einfuegen statt eines toten Links.

7. **Wiki-Bezug.** Immer [[Weekly Range Trading Model]] verlinken, plus die zum Wochentag
   passende(n) Daily-Range-Seite(n) aus `wiki/concepts/` (z.B. [[ICT Daily Range Session
   Timing]], [[Midnight Opening Range]], [[ORG (Opening Range Gap) & 1st Presented FVG]]) --
   eigenes fachliches Urteil, welche am Zieltag am relevantesten sind (z.B. Montag ->
   zusaetzlich NWOG-fokussierte Seiten).

8. **Einschaetzung (Claude).** Eigener, klar markierter Abschnitt `## Einschaetzung (Claude)`
   mit einer kurzen Richtungs-/Wahrscheinlichkeitsaussage. Stuetze sie auf vorhandene
   Backtest-/Statistik-Funde: `algo/seasonal_tendency.json` (Wochentag-Kennzahl fuer den
   Wochentag von `<ZIEL>`), laufende `wiki/synthesis/*(laufend)*`-Seiten, sowie -- falls im
   News-Block ein Red-Folder-Event steht -- ggf. `algo/backtest_fred_events.py`-Erkenntnisse.
   Erwaehne die ORG-C.E.-70%-These als laufend beobachtete Hypothese, wenn `org_ce` in Schritt 3
   gesetzt ist (siehe [[ORG-C.E. 70%-These]]-Konvention: nicht als erledigt/widerlegt
   abhaken). Diesen Abschnitt klar von Schritt 9 abgrenzen -- keine Vermischung mit dem
   Nutzertext.

9. **Datei schreiben** nach `raw/journal/Daily Bias <ZIEL>.md`:

   ```markdown
   # Daily Bias <ZIEL>

   > Weekly Bias: [[Weekly Bias KW<NN> <JAHR>]]  <!-- oder Platzhalter aus Schritt 6 -->

   ## News (Red/Orange Folder)
   <Tabelle aus Schritt 2, oder Warnzeile>

   ## Levels
   <Tabelle + Zeilen aus Schritt 5>

   ## Wiki-Bezug
   <Wikilinks aus Schritt 7>

   ## Einschaetzung (Claude)
   <Text aus Schritt 8>

   ## Mein Bias

   ```

   Existiert die Datei bereits (Command wurde fuer denselben Tag zweimal aufgerufen): fragen,
   ob ueberschrieben werden soll, statt stillschweigend zu ersetzen (koennte bereits
   Nutzertext enthalten).

10. Kurz im Chat bestaetigen: Pfad der geschriebenen Datei + eine Zeile, ob News-Abruf und
    Live-Daten erfolgreich waren oder eine Warnung gesetzt wurde. Kein `push.ps1`-Aufruf.
```

- [ ] **Step 2: Manueller Testlauf**

Command im Chat ausführen: `/bias-vorlage-daily`
Erwartet: `raw/journal/Daily Bias <naechster Handelstag>.md` wird angelegt, enthält alle sechs
Abschnitte, Levels-Tabelle hat plausible Zahlen (mit Step 3 aus Task 1 grob vergleichen), kein
Traceback/Fehlermeldung im Chat.

- [ ] **Step 3: Commit**

```bash
git add ".claude/commands/bias-vorlage-daily.md"
git commit -m "add | Slash-Command bias-vorlage-daily fuer automatische Daily-Bias-Vorlage"
```

Hinweis: die generierte Testdatei aus Step 2 selbst NICHT mitcommitten (ist echter, ggf.
unfertiger Journal-Eintrag des Nutzers) -- nur die Command-Datei.

---

## Task 3: Command `bias-vorlage-weekly`

**Files:**
- Create: `.claude/commands/bias-vorlage-weekly.md`

**Interfaces:**
- Consumes: gleiche CLIs wie Task 2 (`algo/live_status.py`, `algo/bias_levels.py --weekly`)
- Produces: `raw/journal/Weekly Bias KW<NN> <JAHR>.md` beim Ausführen von `/bias-vorlage-weekly`

- [ ] **Step 1: Command-Datei schreiben**

```markdown
---
description: Erzeugt die vorbefuellte Weekly-Bias-Datei fuer die kommende Handelswoche (News, Levels, Wiki-Bezug, eigene Einschaetzung) -- fuer den Scheduled Cron freitags 20:00 oder manuellen Aufruf
---

Erzeuge `raw/journal/Weekly Bias KW<NN> <JAHR>.md` fuer die kommende Handelswoche.

1. **Zielwoche bestimmen.** `date -d "next monday" +%Y-%m-%d` liefert `<MONTAG>`. ISO-Woche
   `date -d "next monday" +%V` -> `<NN>`, Jahr `date -d "next monday" +%Y` -> `<JAHR>`.

2. **News (Red/Orange Folder), ganze Woche.** WebFetch auf
   `https://www.forexfactory.com/calendar?week=<MONTAG als "mmmDD.YYYY">` mit dem Auftrag,
   alle Events Mo-Fr mit Impact-Farbe Red oder Orange als Liste (Wochentag, Uhrzeit NY + DE,
   Event-Name, Impact) zu extrahieren -- Red-Folder-Termine (z.B. NFP, CPI, FOMC) besonders
   hervorheben. Bei Fehlschlag: gleiche Regel wie im Daily-Command (Schritt 2 dort) --
   `⚠️ News-Abruf fehlgeschlagen, manuell auf forexfactory.com pruefen`, Lauf fortsetzen.

3. **NDOG/NWOG/ORG-Levels.** `python algo/live_status.py` ausfuehren (frischer Lauf, siehe
   [[Immer frische Marktdaten]]). `nwog_today` (Open/Close des aktuellen NWOG) und
   `nwog_open_history` (noch offene NWOG-Level der letzten 5 Wochen als DOL-Kandidaten,
   siehe [[New Day Opening Gap (NDOG)]]) entnehmen.

4. **Wochen-Range (Vorwoche als Referenz).** `python algo/bias_levels.py <heutiges Datum>
   --weekly` ausfuehren (heute = Freitag, damit die soeben abgeschlossene Woche erfasst wird).
   `weekly_range` (High/Low/Anzahl Tage) entnehmen.

5. **Levels-Tabelle bauen** (immer als Tabelle):

   | Level | Open | Close |
   |---|---|---|
   | NWOG (aktuell) | ... | ... |

   Darunter: Range der auslaufenden Woche (High/Low aus Schritt 4), offene NWOG-Level der
   letzten 5 Wochen (aus Schritt 3, als Liste Datum+Level, falls nicht leer).

6. **Wiki-Bezug.** Immer [[Weekly Range Trading Model]] verlinken, plus [[IPDA Data Ranges]]
   und ggf. [[Using Monthly & Weekly Ranges (Source)]] -- eigenes fachliches Urteil, welche
   Seite(n) fuer die anstehende Woche (z.B. Monatswechsel, NFP-Woche) zusaetzlich relevant sind.

7. **Einschaetzung (Claude).** Eigener Abschnitt `## Einschaetzung (Claude)`: Wochenrichtung +
   Wahrscheinlichkeit, gestuetzt auf `algo/seasonal_tendency.json` (Wochenmuster/Turn-of-Month
   falls die Woche betroffen ist), NWOG-Bias-Statistik aus `algo/backtest_nwog.py`
   (empirisch: Bias-intakt-Quote nur 7 %, wie in [[New Day Opening Gap (NDOG)]] dokumentiert --
   bei einer NWOG-basierten Richtungsaussage diese Einschraenkung nennen), und Red-Folder-Events
   aus Schritt 2 (z.B. NFP-Woche -> historisch hoehere Volatilitaet Montag, siehe
   `algo/backtest_nfp_week.py`).

8. **Datei schreiben** nach `raw/journal/Weekly Bias KW<NN> <JAHR>.md`:

   ```markdown
   # Weekly Bias KW<NN> <JAHR>

   ## News (Red/Orange Folder), ganze Woche
   <Tabelle aus Schritt 2, oder Warnzeile>

   ## Levels
   <Tabelle + Zeilen aus Schritt 5>

   ## Wiki-Bezug
   <Wikilinks aus Schritt 6>

   ## Einschaetzung (Claude)
   <Text aus Schritt 7>

   ## Mein Bias

   ```

   Existiert die Datei bereits: fragen statt stillschweigend ueberschreiben (gleiche Regel wie
   im Daily-Command).

9. Kurz im Chat bestaetigen: Pfad der geschriebenen Datei + Status von News-Abruf/Live-Daten.
   Kein `push.ps1`-Aufruf.
```

- [ ] **Step 2: Manueller Testlauf**

Command im Chat ausführen: `/bias-vorlage-weekly`
Erwartet: `raw/journal/Weekly Bias KW<naechste Woche> <Jahr>.md` wird angelegt, alle fünf
Abschnitte vorhanden, Levels plausibel, kein Traceback.

- [ ] **Step 3: Commit**

```bash
git add ".claude/commands/bias-vorlage-weekly.md"
git commit -m "add | Slash-Command bias-vorlage-weekly fuer automatische Weekly-Bias-Vorlage"
```

Testdatei aus Step 2 wieder nicht mitcommitten.

---

## Task 4: Scheduled Cron-Jobs einrichten

**Files:** keine (Konfiguration über den `schedule`-Skill / `CronCreate`-Tool, kein Repo-File)

**Interfaces:**
- Consumes: `/bias-vorlage-daily` (Task 2), `/bias-vorlage-weekly` (Task 3)
- Produces: zwei aktive Scheduled Cloud Agents

- [ ] **Step 1: Werktags-Cron fuer den Daily Bias anlegen**

`schedule`-Skill (bzw. `CronCreate`-Tool direkt) aufrufen mit: Zeitplan Mo-Fr 20:00 (lokale
Zeitzone des Nutzers, gleiche Zeitzone wie sonst im Vault verwendet -- bei Unklarheit im
`schedule`-Skill-Dialog nachfragen), Prompt `/bias-vorlage-daily`, Zielverzeichnis dieses Repos.

- [ ] **Step 2: Freitags-Cron fuer den Weekly Bias anlegen**

Gleiches Vorgehen, Zeitplan nur Freitag 20:00, Prompt `/bias-vorlage-weekly`.

- [ ] **Step 3: Beide Jobs verifizieren**

`CronList` (oder Aequivalent im `schedule`-Skill) ausfuehren, beide neuen Jobs mit korrektem
Zeitplan und Prompt in der Ausgabe bestaetigen.

- [ ] **Step 4: Dem Nutzer kurz bestaetigen**

Im Chat: beide Cron-Jobs sind aktiv, naechster Lauf-Zeitpunkt fuer jeden, Hinweis dass der
erste echte Lauf den News-Abruf und die Level-Tabelle in der Praxis zeigt (Testlaeufe aus
Task 2/3 waren manuell ausgeloest).

---

## Self-Review-Notizen (bereits erledigt)

- Spec-Abdeckung: Bausteine 1-6 der Spec sind auf Tasks 1-3 verteilt (News/Levels/Wiki/
  Einschaetzung/Rueckverlinkung/leerer Nutzerbereich), Trigger auf Task 4, Fehlerbehandlung
  in beiden Command-Dateien (Schritt 2 bzw. Schritt 2) verankert. "Nicht Teil dieser Spec"
  (Soll/Ist-Abgleich, Push) bewusst ausgelassen.
- Keine Platzhalter/TBD in Code- oder Command-Bloecken.
- Funktionsnamen konsistent: `week_range`/`yesterday_range`/`compute` aus Task 1 werden in
  Task 2/3 nur ueber die CLI (JSON auf stdout) konsumiert, nicht per Import -- kein
  Namens-Mismatch-Risiko zwischen Tasks.
