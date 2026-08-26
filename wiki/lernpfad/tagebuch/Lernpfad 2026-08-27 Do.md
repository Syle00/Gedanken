---
tags: [lernpfad, tagebuch, phase-0, python, howto, obsidian]
created: 2026-08-24
updated: 2026-08-26
datum: 2026-08-27
woche: 1
phase: Phase 0
block: Übung
geplant_min: 105
status: offen
karten: 0
---

# Lernpfad 2026-08-27 Do

**Woche 1 · Phase 0 · Büro-Tag · zwei Blöcke, 105 Min** · [[Lernpfad — Woche 01]]

> [!info] Warum heute kein Mathe steht
> Du bist seit 4:30 wach und seit 6:00 unterwegs. Um 20 Uhr ist dein Kopf nach vierzehn Stunden
> nicht in der Verfassung, Logarithmen zu lernen — und Mathe ist ohnehin dein schwächstes Fach.
> Der Mathe-Block liegt deshalb auf **Freitag**, einem HO-Tag ohne 4:30-Wecker.
> Heute nur Wiederholung und Übung: fordernd genug, aber kein neuer Stoff.

## Block 1 — Bahn, 06:40–07:25 (45 Min)

Geschenkte Zeit. Nur Handy und Kopfhörer, kein Papier, kein Laptop.

> [!warning] Heute abweichend: Einrichtung statt Wiederholung
> Der Karten-Sync steht noch nicht — am 26.08. waren weder Karten angelegt noch das Handy
> verbunden. Block 1 geht deshalb einmalig für die Einrichtung drauf, Schritt B3 aus
> [[Lernpfad — Karteikarten & Handy-Sync einrichten]]. **Voraussetzung:** Teil A und B0–B2
> müssen am Vorabend am Desktop erledigt sein, sonst liegt nichts in der Cloud.

- [ ] **15 Min:** Obsidian aufs iPhone, Vault `Lern-Vault` (Name exakt gleich!),
      Remotely Save + Dropbox verbinden, einmal syncen — Schritt B3
- [ ] **10 Min:** Plugin *Spaced Repetition* am Handy aktivieren, erste Runde aus
      [[Lernpfad — CS50P Karten Woche 0]] durchgehen
- [ ] **20 Min:** CS50P-Vorlesung weiterschauen, ohne mitzucoden — nur zuhören und verstehen

Ab übermorgen ist Block 1 wieder der normale 15/30-Rhythmus aus [[Lernpfad — Woche 01]].

→ Die vollständige Schritt-für-Schritt-Anleitung steht unten in diesem Dokument:
[Anleitung — Handy verbinden + Karteikarten](#anleitung--obsidian-aufs-handy--karteikarten).

Auf der Rückfahrt (ca. 16:15–17:00) dasselbe, falls du Lust hast. Wenn nicht: völlig in Ordnung,
das ist ein Bonus, kein Pflichtblock.

## Block 2 — Abends, 18:30–19:30 (60 Min)

Zu Hause gegen 17:50. Erst essen, dann eine Stunde.

- [ ] Problem Set 0 zu Ende bringen: *Einstein*, *Tip Calculator*
- [ ] Alle Lösungen in `quant-lab/cs50p/woche0/` ablegen
- [ ] Zwei bis drei Karten aus dem anlegen, was diese Woche gehakt hat

**Um 19:30 ist Schluss.** Bett um 21:30 bedeutet sieben Stunden Schlaf. Was du nach 20 Uhr an
einem solchen Tag noch reinpresst, kostet dich am nächsten Tag mehr, als es bringt.

## Wenn der Tag zu viel war

Dann machst du nur die Bahn-Wiederholung und lässt den Abendblock ausfallen. Trag `ausgefallen`
im Frontmatter ein und geh früher ins Bett. Das ist kein Rückschritt, das ist die Regel — siehe
Regel 3 in [[Lernpfad Quant — Übersicht]].

## Nach der Session

**Gelernt:**

**Hängengeblieben:**

**Hier weiter:**

**Karten angelegt:**

---

# Anleitung — Obsidian aufs Handy + Karteikarten

> [!warning] ⚠️ Widerspruch zu [[Lernpfad — Karteikarten & Handy-Sync einrichten]]
> Diese Anleitung beschreibt den **iCloud**-Weg mit dem Hauptvault. Die Einrichtungsnotiz
> rät für Windows davon ab (Berichte über doppelte und beschädigte Dateien) und empfiehlt
> stattdessen einen separaten `Lern-Vault` über **Remotely Save + Dropbox**, weil der
> Hauptvault mit `raw/` rund 190 MB Screenshots enthält. Entscheide dich morgen für **einen**
> der beiden Wege und streiche den anderen — beide parallel zu synchronisieren geht schief.

## Teil 1 — Vault aufs iPhone bringen

### Weg A: iCloud (kostenlos, empfohlen für ein Gerät + iPhone)

**Am Mac/PC zuerst:**

1. Obsidian öffnen → dein Vault muss in iCloud Drive liegen.
   - Mac-Pfad: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/`
   - Windows: iCloud für Windows installieren, Vault-Ordner nach
     `iCloudDrive\iCloud~md~obsidian\Documents\` verschieben.
2. Liegt der Vault noch woanders: Obsidian schließen, Ordner dorthin verschieben,
   Obsidian neu öffnen → **Open folder as vault** → neuen Ort wählen.
3. Warten bis iCloud fertig synchronisiert hat (keine Wolken-Symbole mehr mit Pfeil).

**Am iPhone:**

1. Einstellungen → Apple-ID → iCloud → **iCloud Drive** an.
2. App Store → **Obsidian** installieren → öffnen.
3. „Create new vault" **NICHT** drücken. Stattdessen: **Open folder as vault** →
   dein Vault-Ordner unter iCloud Drive → Obsidian auswählen.
4. Öffnen. Fertig — Änderungen syncen automatisch in beide Richtungen.

> [!warning] Nicht auf beiden Geräten gleichzeitig dieselbe Notiz bearbeiten.
> iCloud kann sonst Konfliktkopien anlegen.

### Weg B: Obsidian Sync (kostenpflichtig, ca. 4–5 $/Monat)

Nur nötig, wenn du mehrere Geräte, Versionsverlauf und Ende-zu-Ende-Verschlüsselung willst.

1. Desktop → Einstellungen → **Sync** → Konto anlegen → *Create remote vault*.
2. iPhone → Obsidian → Einstellungen → **Sync** → einloggen → *Connect to remote vault* →
   denselben Vault wählen.

### Check am Ende

1. Auf dem iPhone eine Testnotiz `Handy-Test.md` anlegen.
2. Am Desktop nach ~30 Sekunden nachschauen, ob sie auftaucht. Wenn ja: läuft.

### Wenn's klemmt

| Problem | Lösung |
|---|---|
| Vault-Ordner nicht auffindbar am iPhone | Dateien-App öffnen → prüfen ob Ordner „Obsidian" unter iCloud Drive existiert. Wenn nicht: Desktop-Sync noch nicht fertig. |
| Änderungen kommen nicht an | iPhone: Obsidian ganz schließen (App-Switcher hochwischen) und neu öffnen. |
| Plugins fehlen am Handy | Einstellungen → Community Plugins → dort einzeln aktivieren (der Ordner `.obsidian` synct mit, aber Plugins müssen mobil freigeschaltet werden). |

---

## Teil 2 — Karteikarten erstellen

### Variante 1: Plugin „Spaced Repetition" (alles in Obsidian, auch mobil)

**Installation**

1. Einstellungen → Community Plugins → *Turn on community plugins*.
2. **Browse** → nach `Spaced Repetition` suchen (von **st3v3nmw**) → Install → Enable.
3. In den Plugin-Einstellungen: Flashcard-Tag steht standardmäßig auf `#flashcards`.

**Karten schreiben** — einfach in eine ganz normale Notiz:

| Typ | Syntax | Beispiel |
|---|---|---|
| Einzeilig | `Frage::Antwort` | `Was heißt Kürzen?::Zähler und Nenner durch dieselbe Zahl teilen` |
| Beidseitig | `Frage:::Antwort` | wird auch rückwärts abgefragt |
| Mehrzeilig | Frage, dann `?`, dann Antwort | siehe unten |
| Lücke (Cloze) | `==markiert==` | `Beim Multiplizieren rechnet man ==Zähler mal Zähler== und ==Nenner mal Nenner==` |

Mehrzeilig sieht so aus:

```
Wie wandelt man eine gemischte Zahl in einen unechten Bruch um?
?
Nenner × Ganze + Zähler, das Ergebnis kommt in den Zähler.
Der Nenner bleibt gleich.
```

**Abfragen:** Linke Seitenleiste → Icon mit den Karten → *Review flashcards*.
Nach jeder Karte: **Hard / Good / Easy** — daraus berechnet das Plugin den nächsten Termin.

### Variante 2: Obsidian + Anki (wenn du in Anki lernen willst)

1. Anki am Desktop installieren + Add-on **AnkiConnect** (Code `2055492159`), Anki neu starten.
2. In Obsidian das Community Plugin **Obsidian_to_Anki** installieren.
3. Anki muss beim Export geöffnet sein.
4. Karten in Obsidian schreiben, z. B.:

```
START
Basic
Front: Was ist 3/4 + 1/4?
Back: 1 (bzw. 4/4)
Tags: bruchrechnen
END
```

5. Kommandopalette (`Strg/Cmd+P`) → *Obsidian_to_Anki: Scan Vault* → Karten landen in Anki.

Am iPhone lernst du dann in **AnkiMobile** (kostenpflichtig) — nicht in Obsidian.

> **Kurz entschieden:** Mobil ohne Zusatzkosten lernen → **Variante 1**.
> Ankis Lernalgorithmus und Statistiken → **Variante 2**.

---

## Teil 3 — Fertige Karten: Bruchrechnen

Neue Notiz anlegen: `Karteikarten/Bruchrechnen.md`, folgenden Block hineinkopieren.

````markdown
---
tags: flashcards
---

# Bruchrechnen

## Grundbegriffe

Wie heißt die Zahl über dem Bruchstrich?::Zähler
Wie heißt die Zahl unter dem Bruchstrich?::Nenner
Was bedeutet der Nenner anschaulich?::In wie viele gleiche Teile das Ganze zerlegt ist
Was bedeutet der Zähler anschaulich?::Wie viele dieser Teile genommen werden

## Kürzen und Erweitern

Was ist die eine Regel beim Kürzen?::Zähler UND Nenner durch dieselbe Zahl teilen — niemals nur einen von beiden
Woran erkenne ich, dass ein Bruch vollständig gekürzt ist?::Es gibt keine Zahl außer 1 mehr, durch die Zähler und Nenner beide teilbar sind
Was ist die Gegenprobe beim Kürzen?::Das Ergebnis wieder mit derselben Zahl multiplizieren — es muss der Ausgangsbruch herauskommen

Kürze 12/18 vollständig
?
Beide durch 6 → 2/3.
Achtung: Bei 6/9 (nur durch 2 geteilt) wäre man einen Schritt zu früh stehengeblieben.

Ändert Kürzen den Wert eines Bruchs?::Nein — nur die Schreibweise

## Addieren und Subtrahieren

Was braucht man zum Addieren von Brüchen?::Einen gemeinsamen Nenner
Wie addiert man 1/4 + 2/4?::Zähler addieren, Nenner bleibt: 3/4

Was macht man bei ungleichen Nennern?
?
Erweitern auf den kleinsten gemeinsamen Nenner, dann die Zähler addieren.
Beispiel: 1/2 + 1/3 → 3/6 + 2/6 = 5/6

Werden beim Addieren die Nenner addiert?::Nein — der Nenner bleibt stehen

## Multiplizieren und Dividieren

Wie multipliziert man zwei Brüche?::==Zähler mal Zähler==, ==Nenner mal Nenner==

2/3 · 3/4 = ?
?
6/12 = 1/2 (kürzen nicht vergessen)

Wie dividiert man durch einen Bruch?::Mit dem Kehrwert multiplizieren
Was ist der Kehrwert von 3/5?::5/3

1/2 : 1/4 = ?
?
1/2 · 4/1 = 4/2 = 2

## Gemischte Zahlen

Wie wandelt man eine gemischte Zahl in einen unechten Bruch um?
?
==Nenner × Ganze + Zähler== → Ergebnis in den Zähler, Nenner bleibt gleich.
Beispiel: 2 3/4 → 4·2+3 = 11 → 11/4

Wandle 5 1/12 in einen unechten Bruch um
?
12·5 + 1 = 61 → 61/12

Wie kommt man vom unechten Bruch zurück zur gemischten Zahl?
?
Zähler durch Nenner teilen mit Rest.
Beispiel: 11/4 → 11:4 = 2 Rest 3 → 2 3/4

Was ist die Zwei-Schritt-Methode bei gemischten Zahlen?
?
1. In unechte Brüche umwandeln
2. Rechnen (ggf. gleichnamig machen)
3. Zurück in gemischte Zahl, dann kürzen

Was ist ein unechter Bruch?::Ein Bruch, dessen Zähler größer oder gleich dem Nenner ist
````

---

## Teil 4 — Leere Vorlage zum Weitermachen

Als `Karteikarten/_Vorlage.md` speichern und für jedes neue Thema kopieren.

````markdown
---
tags: flashcards
---

# [Thema]

## [Unterthema]

<!-- Einzeilig -->
Frage::Antwort

<!-- Beidseitig (wird auch rückwärts abgefragt) -->
Begriff:::Definition

<!-- Mehrzeilig -->
Frage über mehrere Zeilen?
?
Antwort Zeile 1
Antwort Zeile 2

<!-- Lückentext -->
Die Regel lautet: ==erster Teil== und dann ==zweiter Teil==
````

---

## Checkliste für morgen

- [ ] Vault liegt in iCloud Drive
- [ ] Obsidian am iPhone installiert
- [ ] Vault am iPhone via „Open folder as vault" geöffnet
- [ ] Testnotiz syncte in beide Richtungen
- [ ] Plugin „Spaced Repetition" installiert und aktiviert (Desktop und iPhone)
- [ ] `Karteikarten/Bruchrechnen.md` angelegt und befüllt
- [ ] `Karteikarten/_Vorlage.md` angelegt
- [ ] Erste Review-Runde am Handy durchgeklickt

**Offen aus der letzten Mathe-Session:** `5 1/12 + 2 2/3` zu Ende rechnen.
