---
tags: [lernpfad, tagebuch, vorlage]
created: 2026-08-24
updated: 2026-08-24
---

# Lernpfad — Tagesvorlage

Vorlage für neue Tageseinträge unter `wiki/lernpfad/tagebuch/`.
Dateiname: `Lernpfad JJJJ-MM-TT Xx.md` (z. B. `Lernpfad 2026-09-01 Di.md`).

Sieben neue Einträge legst du jeden Sonntag im Review-Block an — oder du lässt sie dir vom
täglichen Briefing anlegen.

## Vorlage zum Kopieren

```markdown
---
tags: [lernpfad, tagebuch, phase-0]
created: JJJJ-MM-TT
updated: JJJJ-MM-TT
datum: JJJJ-MM-TT
woche: 1
phase: Phase 0
block: Code
geplant_min: 90
status: offen
karten: 0
---

# Lernpfad JJJJ-MM-TT Xx

**Woche 1 · Phase 0 · Block: Code · 90 Min**

## Geplant

- [ ] Aufgabe 1
- [ ] Aufgabe 2

**Quelle:** …

## Nach der Session

**Gelernt:**

**Hängengeblieben:**

**Hier weiter:**

**Karten angelegt:**
```

## Feldbedeutungen

| Feld | Werte | Zweck |
| --- | --- | --- |
| `status` | `offen`, `erledigt`, `teilweise`, `ausgefallen` | Für die Wochenbilanz und das tägliche Briefing |
| `block` | `Code`, `Mathe`, `Frei`, `Vertiefung`, `Projekt`, `Review`, `Setup` | Woran gearbeitet wurde |
| `geplant_min` | Zahl | Geplante Minuten laut Wochenrhythmus |
| `phase` | `Phase 0` … `Phase 5` | Für Auswertungen über längere Zeiträume |

`ausgefallen` ist ein völlig legitimer Status. Er wird **nicht** nachgeholt — siehe Regel 3 in
[[Lernpfad Quant — Übersicht]]. Ein ehrliches `ausgefallen` ist mehr wert als ein Eintrag, der
so tut, als wäre er erledigt.

`teilweise` nutzt du, wenn ein Block angefangen, aber nicht zu Ende gebracht wurde. Schreib
dann unter „Hier weiter" genau, was noch offen ist. Auch hier gilt: Der Rest wird nicht in den
nächsten Lernblock gequetscht, sondern entweder bewusst neu eingeplant oder gestrichen.

## Die drei Felder nach der Session

**Gelernt** — in eigenen Worten, ein bis drei Sätze. Wenn du es nicht in eigenen Worten
zusammenfassen kannst, hast du es nicht verstanden. Das ist eine Information, kein Vorwurf.

**Hängengeblieben** — jede Stelle, an der du nachschlagen musstest oder ratlos warst. Diese
Liste ist die Quelle deiner Wiederholungskarten und, über Wochen gelesen, die ehrlichste
Auswertung deines Fortschritts.

Die Karten selbst schreibst du auf die Konzeptseite in `concepts/`, mit Tag `#flashcards`
und der Syntax `Frage::Antwort`. Ins Tagebuch kommt nur die Anzahl (Feld `karten`).

**Hier weiter** — so konkret, dass du beim nächsten Mal ohne Nachdenken loslegen kannst.
Nicht „bei Schleifen weitermachen", sondern „CS50P Woche 1, Minute 34, `while`-Schleife".
