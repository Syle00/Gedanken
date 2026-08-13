# Bias-Vorlage: automatische Daily/Weekly-Bias-Datei

## Ziel

Jeden Handelstag schreibt der Nutzer einen Daily Bias (`raw/journal/Daily Bias YYYY-MM-DD.md`),
am Wochenende einen übergeordneten Weekly Bias (`raw/journal/Weekly Bias KWxx YYYY.md`), der die
Wochenrichtung vorgibt. Beide Dateien werden bisher komplett von Hand geschrieben. Diese Spec
automatisiert das Vorbefüllen: News, Marktdaten-Levels, Wiki-Bezug und eine eigene
Wahrscheinlichkeits-Einschätzung entstehen automatisch, der Nutzer ergänzt nur noch seinen
eigenen Bias-Text.

Dient Layer 0 (autonomer Handelsalgorithmus) indirekt: bessere, konsistentere Bias-Dokumentation
verbessert die Datenbasis, aus der später Regeln abgeleitet werden — ist aber selbst kein
Algo-Code, sondern Werkzeug für den manuellen Trading-Alltag.

## Architektur

**Neuer Skill** `.claude/skills/bias-vorlage/SKILL.md`, analog zu `algo-live-status` aufgebaut
(ein Durchlauf, kein Loop). Wird über zwei Scheduled Cloud Agents (via `schedule`-Skill)
angestoßen:

- **Werktags 20:00** (Vorabend) → generiert die Daily-Bias-Datei für den nächsten Handelstag.
- **Freitags 20:00** → generiert zusätzlich die Weekly-Bias-Datei für die kommende Kalenderwoche.

Beide Läufe rufen denselben Skill mit einem Modus-Argument auf (`bias-vorlage daily` /
`bias-vorlage weekly`), damit Logik zwischen beiden geteilt wird (News-Abruf, Level-Tabelle).

## Bausteine

### 1. News (Red/Orange Folder)

WebFetch auf die ForexFactory-Kalenderseite für das Zieldatum (Daily) bzw. die Zielwoche
(Weekly). Extrahiere Events mit Impact-Farbe Red oder Orange: Uhrzeit (NY + umgerechnet DE-Zeit,
analog zum bestehenden Muster "PPI News um 14.30 DE Zeit also 8.30 Ny" aus
`raw/Daily Bias 13.08.md`), Event-Name, Impact-Stufe.

**Fehlerfall**: Schlägt der Abruf fehl (Layout-Änderung, Netzwerk, Rate-Limit) — Datei wird
trotzdem erzeugt, News-Abschnitt bekommt `⚠️ News-Abruf fehlgeschlagen, manuell auf
forexfactory.com prüfen` statt die Datei leer zu lassen oder den Lauf abzubrechen.

### 2. Marktdaten-Levels

Quelle: `algo/live_status.py` (frische Daten, siehe [[Immer frische Marktdaten]]-Regel) +
`raw/marktdaten/`. Tabelle mit (Nutzerkonvention: Levels immer als Tabelle, nicht als Fließtext):

| Level | Open | Close |
|---|---|---|
| NWOG (aktuell) | … | … |
| NDOG (aktuell) | … | … |

Plus separat: Weekly-Range High/Low (laufende Woche), gestrige Daily-Range High/Low/Close, Liste
offener ORGs (Datum + Grenzen) sofern vorhanden.

### 3. Wiki-Bezug

Kurzer Abschnitt mit Wikilinks auf die für den Tages-/Wochenkontext relevanten Core-Content-
Konzepte — mindestens [[Weekly Range Trading Model]], plus passende Seite(n) aus
`wiki/concepts/` zur Daily Range (z.B. [[ICT Daily Range Session Timing]],
[[Midnight Opening Range]]), je nachdem was für den Tag/die Woche zutrifft.

### 4. Claude-Einschätzung

Eigener, klar als solcher markierter Abschnitt ("## Einschätzung (Claude)") mit
Richtungs-/Wahrscheinlichkeitsaussage, begründet aus vorhandenen Backtest-/Statistik-Funden
(`algo/seasonal_tendency.json`, Wochentag-/Turn-of-Month-Muster, laufende
`wiki/synthesis/*(laufend)*`-Seiten, ggf. `macro_db`). Getrennt vom Nutzer-Bias-Text darunter,
damit klar bleibt, welche Zeilen automatisch von Claude stammen und welche vom Nutzer.

### 5. Weekly-Rückverlinkung (nur Daily-Modus)

Daily-Bias-Datei verlinkt oben per Wikilink auf die aktuell gültige Weekly-Bias-Datei der
laufenden Kalenderwoche, damit der Daily Bias nie isoliert vom übergeordneten Wochenbias
geschrieben wird.

### 6. Leerer Bereich für Nutzer-Bias

Abschnitt "## Mein Bias" bleibt leer — der Nutzer schreibt dort wie bisher seinen eigenen Text.

## Dateiformat

`raw/journal/Daily Bias YYYY-MM-DD.md`:

```markdown
# Daily Bias YYYY-MM-DD

> Weekly Bias: [[Weekly Bias KWxx YYYY]]

## News (Red/Orange Folder)
| Zeit (NY) | Zeit (DE) | Event | Impact |
|---|---|---|---|
| … | … | … | Red/Orange |

## Levels
| Level | Open | Close |
|---|---|---|
| NWOG | … | … |
| NDOG | … | … |

Weekly Range: High … / Low …
Gestrige Daily Range: H … / L … / C …
Offene ORGs: …

## Wiki-Bezug
- [[Weekly Range Trading Model]]
- [[…]]

## Einschätzung (Claude)
…

## Mein Bias

```

`raw/journal/Weekly Bias KWxx YYYY.md` analog, ohne Rückverlinkung, mit Wochen-News/-Levels statt
Tages-News/-Levels.

## Fehlerbehandlung & Datenqualität

Gilt [[Algo-Trading: Arbeitsstandards]] sinngemäß auch hier, weil Marktdaten-Levels aus
`raw/marktdaten/` gezogen werden: bei Zweifel an Vollständigkeit/Frische aktiv im generierten
Dokument warnen (`⚠️`-Zeile), statt stillschweigend zu füllen.

## Nicht Teil dieser Spec

- Automatischer Soll/Ist-Abgleich (Bias-Text vs. tatsächliche Daily Range am Folgetag) — als
  Idee vermerkt, kein Auftrag.
- Push/Commit der generierten Datei — folgt dem bestehenden Muster: der Nutzer committed über
  `push.ps1`, der Skill schreibt nur die Datei.
