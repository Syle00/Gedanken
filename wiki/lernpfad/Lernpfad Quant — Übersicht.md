---
tags: [lernpfad, meta, python, mathematik, statistik, machine-learning]
created: 2026-08-24
updated: 2026-08-24
zeitraum: 2026-08-24 bis 2027-08-29
---

# Lernpfad Quant — Übersicht

Persönlicher 12-Monats-Lernpfad: Python, Mathematik, Statistik und Machine Learning —
aufgebaut um ein einziges Projekt, das eigene Handelsmodell auf Basis der ICT-Konzepte
aus [[Smart Money Concepts (SMC)]].

**Zeitraum:** 24.08.2026 – 29.08.2027 · **Pensum:** 11 h/Woche · **Gesamt:** ca. 572 h

> Vollständige Fassung mit Grafiken, Kursen und Quellen: [[Quant-Roadmap 12 Monate.pdf]]

> [!warning] Das PDF trägt noch die alten Stundenzahlen
> Im PDF stehen 10,5 h/Woche und 555 h gesamt. Beides war falsch: Der Wochenplan dort summierte
> sich tatsächlich auf 12 h (Samstag 4 h). Diese Seite ist die korrigierte Fassung mit dem
> tatsächlichen Rhythmus (Samstag 3 h). Bis das PDF neu gebaut ist, gelten die Zahlen hier.

## Das Ziel

Selbstständig und zielstrebig arbeiten können, ohne bei jedem zweiten Schritt nachschlagen
zu müssen. Nicht Zertifikate, sondern Können, das im Kopf bleibt.

Der Lernpfad ist **Unterbau für das Ziel aus [[../../CLAUDE.md|CLAUDE.md]]** — einen autonomen
Handelsalgorithmus für NQ und ES über IBKR. Bei einem Zielkonflikt entscheidet das Algo-Ziel,
nicht der Lernplan.

## Die sechs Phasen

| Phase | Wochen | Zeitraum | Thema | Stunden |
| --- | --- | --- | --- | --- |
| Phase 0 | 1–6 | 24.08. – 04.10.2026 | Fundament: CS50P + Mathe-Auffrischung | 66 h |
| Phase 1 | 7–12 | 05.10. – 15.11.2026 | Daten & Handwerk: NumPy, pandas, Git, pytest | 66 h |
| Phase 2 | 13–20 | 16.11.2026 – 10.01.2027 | Mathe-Kern: Lineare Algebra + Analysis | 88 h |
| Phase 3 | 21–30 | 11.01. – 21.03.2027 | Statistik & Zeitreihen | 110 h |
| Phase 4 | 31–40 | 22.03. – 06.06.2027 | Machine Learning | 110 h |
| Phase 5 | 41–52 | 07.06. – 29.08.2027 | Financial ML & Live | 132 h |

Fortschritt und harte Nachweise: [[Lernpfad — Meilensteine]]

## Der Wochenrhythmus

| Tag | Dauer | Block |
| --- | --- | --- |
| Montag | 1,5 h | Code — Python / Kurs |
| Dienstag | 1,5 h | Mathe — Stift und Papier |
| Mittwoch | 1,5 h | Code — Python / Kurs |
| Donnerstag | 1,5 h | Mathe — Stift und Papier |
| Freitag | 1 h | Freies Coden — Mini-Skript ohne Anleitung |
| Samstag | 3 h | Vertiefung (1,5 h) + Projekt ICT-Modell (1,5 h, ab Woche 7) |
| Sonntag | 1 h | Review — Blank-Page-Test, Karten, Wochenrückblick |

**Summe: 11 h pro Woche.** Code und Mathe liegen bewusst an getrennten Tagen: Beides im selben
Block zu mischen kostet jedes Mal rund 15 Minuten Umschaltzeit.

### Uhrzeiten sind nicht fix

Jannes hat wechselnde Arbeitszeiten (Dienstplan im Google Kalender, immer 8:06, aber Start um
7:55, 8:55 oder 9:55). **Die Blöcke wiederholen sich deshalb nicht automatisch** — sie werden
jede Woche neu gesetzt und einzeln im Kalender **Lernsession** eingetragen.

Welche Fenster wann nutzbar sind, welche Ausbaustufen es gibt und wo die Schlafgrenze liegt,
steht vollständig in [[Lernpfad — Zeitfenster & Ausbaustufen]]. Die Kurzfassung:

- **Bahn an Büro-Tagen (6:40–7:25)** — 45 Min pro Fahrt, geschenkte Zeit. Karten und Videos,
  kein Papier, kein Code.
- **HO-Tage mit 9:55-Start** — Morgenblock 8:00–9:30 ohne Schlafverlust. Hier gehört Mathe hin.
- **Büro-Tage ab 16:01** — früher Feierabend, Block 18:30–20:00.
- **HO-Mittagspause** — 30 Min reine Kartenwiederholung.

Gym ist spontan und meist abends. Deshalb haben Morgen-, Bahn- und Mittagsfenster Vorrang —
sie kollidieren nie damit. Fällt eine Woche kürzer aus, gilt Regel 3: nichts nachholen, der
Plan verschiebt sich.

## Die vier Regeln

1. **Termin statt Vorsatz.** Ein Block, der nicht im Kalender steht, findet nicht statt.
2. **Immer im selben Zustand aufhören.** Jede Session endet mit einer Notiz „hier weiter".
3. **Ausgefallen ist ausgefallen.** Nichts wird nachgeholt, der Plan verschiebt sich um eine Woche.
   Aufhol-Marathons sind der häufigste Grund, warum Lernpläne sterben.
4. **Minimum-Tag statt Nulltag.** An schlechten Tagen 15 Minuten Karten. Die Kette ist wichtiger
   als jeder einzelne Tag.

## Wie hier dokumentiert wird

Vier Ebenen, jede mit einem klaren Zweck. Wer alles in eine Datei schreibt, findet später nichts
wieder — und wer fünf Systeme pflegt, pflegt am Ende keins.

### 1. Tagebuch — was passiert ist

Ein Eintrag pro Lerntag unter `wiki/lernpfad/tagebuch/`, benannt
`Lernpfad JJJJ-MM-TT Tag.md`. **Vor** der Session liest du den Eintrag, **nach** der Session
füllst du drei Felder aus:

- **Gelernt** — in eigenen Worten, ein bis drei Sätze
- **Hängengeblieben** — was nicht klar wurde (das wird zur Karte)
- **Hier weiter** — der genaue Einstiegspunkt fürs nächste Mal

Das dritte Feld ist das wichtigste. Es spart beim nächsten Mal zehn Minuten Wiedereinstieg.
Vorlage: [[Lernpfad — Tagesvorlage]]

### 2. Konzept-Seiten — was du verstanden hast

Sobald ein Konzept sitzt, bekommt es eine eigene Seite in `wiki/concepts/` — nach denselben
Seitenkonventionen wie alles andere im Vault (Frontmatter, Wikilinks, Widerspruchsmarker).
Kein eigener Lernpfad-Ordner dafür: Ein verstandenes Konzept ist Wissen, kein Tagebucheintrag,
und gehört dorthin, wo du es später suchst.

Tag-Konvention für Seiten aus dem Lernpfad: `#lernpfad` zusätzlich zu den fachlichen Tags,
damit sich beides trennen lässt.

**Regel:** Nicht abschreiben. Erklären, als würdest du es jemandem beibringen, mit einem eigenen
Beispiel und eigenem Code. Was du nur zitieren kannst, hast du nicht verstanden.

### 3. Karten — was abrufbar bleibt

Wiederholt wird mit dem Obsidian-Plugin **Spaced Repetition** (Stephen Mwangi), nicht mit Anki.
Grund: Die Karten leben direkt in den Notizen, die du ohnehin schreibst — ein System statt zwei,
und kein Bruch zwischen „Notiz" und „Karte". Auf dem iPhone läuft dasselbe über die kostenlose
Obsidian-App, synchronisiert per *Remotely Save* gegen OneDrive.

**Drei bis fünf eigene Karten nach jeder Session, täglich zehn Minuten wiederholen.** Keine
fertigen Decks: Das Formulieren der Karte ist der halbe Lerneffekt. Gute Karten sind Fragen,
keine Definitionen — „Wie berechne ich in pandas einen 20-Perioden-Durchschnitt?" statt
„Was ist ein Moving Average?".

**Syntax** (direkt in jede Wiki-Seite schreibbar):

| Kartentyp | Schreibweise |
| --- | --- |
| Einzeilig | `Frage::Antwort` |
| Einzeilig, beidseitig | `Begriff:::Definition` |
| Mehrzeilig | Frage, neue Zeile `?`, neue Zeile Antwort |
| Lückentext | `Der ADF-Test prüft auf ==Stationarität==.` |

Jede Karte braucht den Tag `#flashcards`, Unterdecks über `#flashcards/python`,
`#flashcards/mathe`, `#flashcards/statistik` und so weiter. Abgefragt wird über das
Karten-Symbol in der linken Leiste.

> [!tip] Karten gehören zur Konzeptseite, nicht ins Tagebuch
> Schreib die Karte dorthin, wo das Wissen steht — auf die Seite in `concepts/`. Das Tagebuch
> hält nur fest, **wie viele** Karten an dem Tag entstanden sind (Feld `karten` im Frontmatter).

### 4. Code — was du gebaut hast

Der Code selbst gehört ins Git-Repo, nicht ins Wiki. Übungscode aus den Kursen in einen eigenen
Ordner `quant-lab/`, Projektcode später nach `algo/` unter den dort geltenden Standards
(siehe [[../../algo/CLAUDE.md|algo/CLAUDE.md]]).

## Aktuelle Woche

[[Lernpfad — Woche 01]] · 24.08. – 30.08.2026 · Phase 0

## Verwandte Seiten

- [[Lernpfad — Meilensteine]] — die neun Prüfpunkte mit Fälligkeitsdatum
- [[Lernpfad — Zeitfenster & Ausbaustufen]] — Dienstplan-Muster, nutzbare Fenster, Schlafgrenzen
- [[Lernpfad — Mathe-Videothek]] — deutschsprachige Erklärvideos zu jeder Mathe-Aufgabe
- [[Lernpfad — Tagesvorlage]] — Vorlage für neue Tageseinträge
- [[Datenbeschaffung für Backtests (Optionen & Grenzen)]] — warum Datenmenge nicht der Engpass ist
- [[Backtesting-Biases (Optimisation, Look-Ahead, Survivorship, Cognitive)]] — Phase 5 vertieft das
