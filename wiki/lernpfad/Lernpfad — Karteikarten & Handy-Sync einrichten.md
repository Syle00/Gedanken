---
tags: [lernpfad, howto, obsidian, cs50]
created: 2026-08-26
updated: 2026-08-26
sources: []
---

# Lernpfad — Karteikarten & Handy-Sync einrichten

Einmalige Einrichtung für den Bahn-Slot aus [[Lernpfad — Zeitfenster & Ausbaustufen]].
Ohne sie läuft der 15-Minuten-Kartenblock in Block 1 von [[Lernpfad 2026-08-27 Do]] ins Leere.

> [!warning] Reihenfolge beachten
> **Teil A und B1–B2 gehen nur am Desktop und müssen heute Abend passieren.**
> Morgen in der Bahn ist nur noch Teil B3 (Handy) übrig — der braucht keinen Laptop.
> Machst du B2 nicht vorher, liegt morgen nichts in der Cloud, das das Handy holen könnte.

> **Warum kein Anki:** AnkiMobile für iOS ist ein kostenpflichtiger Einmalkauf (ca. 30 €).
> Obsidian ist auf iOS kostenlos, und das Plugin *Spaced Repetition* nutzt denselben
> SM-2-Algorithmus wie Anki — direkt im Vault, ohne zweite App.

---

## Teil A — Plugin und Kartensyntax (Desktop, ~10 Min)

### A1. Plugin installieren

1. Obsidian öffnen → unten links **Zahnrad** (Einstellungen).
2. Links **Community-Plugins**.
3. Steht dort „Eingeschränkter Modus / Restricted Mode" auf **an** → **ausschalten**
   und die Warnung bestätigen.
4. **Durchsuchen / Browse** → Suchfeld: `Spaced Repetition`.
5. Treffer von **st3v3nmw** (Stephen Mwangi) → **Installieren** → **Aktivieren**.

> Es gibt mehrere Flashcard-Plugins. Nimm genau dieses — es ist das ausgereifteste und
> das einzige mit brauchbarem Mobile-Support. Das Plugin namens *Flashcards* exportiert
> nur nach Anki und nützt dir hier nichts.

### A2. Die Syntax

Eine Karte ist **eine Zeile in einer normalen Markdown-Notiz**. Kein Extra-Editor, keine
Datenbank. Die Datei braucht nur irgendwo den Tag `#flashcards`.

| Was du willst | Wie du es schreibst |
|---|---|
| Einfache Karte (Vorderseite → Rückseite) | `Frage::Antwort` |
| Karte in **beide** Richtungen abgefragt | `Frage:::Antwort` |
| Mehrzeilige Karte | Frage, dann `?` allein in einer Zeile, dann Antwort |
| Mehrzeilig, beide Richtungen | dasselbe, aber `??` statt `?` |
| Lückentext (Cloze) | Text mit `==markierter Stelle==` — die wird abgefragt |

Das entspricht genau der Syntax, die in [[Lernpfad 2026-08-26 Mi]] als Tagesaufgabe steht.

### A3. Stapel sortieren

Der Tag bestimmt den Stapel, Unterstapel per Schrägstrich:

- `#flashcards/python` — die Konvention aus dem Lernpfad, dabei bleiben
- `#flashcards/mathe`, `#flashcards/statistik` — für die späteren Phasen

### A4. Lernen starten

- Linke Seitenleiste: neues Stapel-Icon → **Review flashcards**
- Oder `Strg + P` → `Spaced Repetition: Review flashcards`

Beim Abfragen bewertest du dich selbst mit **Hard / Good / Easy**; daraus berechnet das
Plugin den nächsten Termin. Sonst ist nichts einzustellen.

> **Startstapel liegt bereit:** [[Lernpfad — CS50P Karten Woche 0]], rund 30 fertige Karten
> zu `int`, `input()`, Strings und Funktionen.

---

## Teil B — Vault aufs iPhone

### B0. Nicht den Hauptvault synchronisieren (Desktop, 2 Min)

`VS Folder 1` enthält `raw/` mit rund 190 MB Screenshots plus die Marktdaten-CSVs. Das aufs
Handy zu spiegeln ist langsam, frisst Speicher und geht beim Sync regelmäßig schief.

**Zweiter, kleiner Vault nur fürs Lernen:**

1. Ordner anlegen: `C:\Users\Jannes\Desktop\Lern-Vault`
2. Obsidian → unten links Vault-Symbol → **Andere Vaults verwalten** →
   **Ordner als Vault öffnen** → neuen Ordner wählen.
3. [[Lernpfad — CS50P Karten Woche 0]] dorthin **kopieren** (nicht verschieben — die
   Fassung hier im Repo bleibt als versionierte Sicherung liegen).

### B1. Sync-Weg wählen

| Weg | Kosten | Urteil |
|---|---|---|
| **Remotely Save + Dropbox** | kostenlos | **Empfohlen.** Läuft unter Windows und iOS. |
| Obsidian Sync (offiziell) | Abo | Am zuverlässigsten, kostet aber — und du sparst dir gerade Anki. |
| iCloud für Windows | kostenlos | **Nicht nehmen.** Unter Windows gibt es wiederholt Berichte über doppelte und beschädigte Dateien. Auf reinen Apple-Geräten wäre es der einfachste Weg, du bist aber auf Windows. |
| Git + Working Copy (iOS) | App kostet fürs Pushen | Naheliegend, weil du Git ohnehin nutzt. Die Gratis-Version kann nur klonen und ziehen, nicht pushen. |

### B2. Remotely Save am Desktop (heute Abend, ~10 Min)

1. Dropbox-Konto anlegen, falls nicht vorhanden (kostenlos, 2 GB — für Textnotizen reichlich).
2. In Obsidian **im Lern-Vault**: Einstellungen → Community-Plugins → Durchsuchen →
   `Remotely Save` → Installieren → Aktivieren.
3. Einstellungen → **Remotely Save** → *Remote Service* auf **Dropbox** stellen.
4. **Auth** klicken → Browser öffnet Dropbox → anmelden → Zugriff erlauben → den
   angezeigten Code zurück in Obsidian einfügen.
5. In der linken Seitenleiste erscheint ein **Sync-Symbol** → einmal anklicken.
   Der Vault landet in Dropbox unter `Apps/remotely-save/Lern-Vault`.

> Falls die Dropbox-Anmeldung hakt: dasselbe Plugin kann auch **OneDrive**, und als
> Windows-Nutzer hast du ohnehin ein Microsoft-Konto. Ablauf identisch.

### B3. Remotely Save am iPhone (morgen in der Bahn, ~10 Min)

1. **Obsidian** aus dem App Store laden (kostenlos).
2. App öffnen → **Create new vault**.
3. Als Namen **exakt** `Lern-Vault` eingeben, Groß- und Kleinschreibung identisch.
   > [!warning] Häufigster Fehler
   > Heißt der Vault am Handy anders, legt das Plugin einen **zweiten, getrennten Ordner**
   > in der Dropbox an. Beide Seiten synchronisieren dann fleißig — nur nie miteinander.
4. „Store in iCloud" kann **aus** bleiben.
5. In der App: Zahnrad → **Community Plugins** → eingeschränkten Modus aus →
   `Remotely Save` suchen → installieren → aktivieren.
6. Dropbox genauso authentifizieren wie in B2.
7. Sync-Symbol antippen → die Karten erscheinen.
8. Zum Schluss **Spaced Repetition** auch am Handy installieren und aktivieren.

### B4. Danach

Vor dem Aussteigen am Handy einmal **Sync** antippen, am Desktop nach dem Öffnen ebenso.
Automatisch geht auch: Plugin-Einstellungen → *Schedule for auto run* → z. B. „every 5 minutes".

---

## Checkliste

**Heute Abend, Desktop:**

- [ ] A1 Spaced-Repetition-Plugin installiert
- [ ] A4 einmal eine Runde Karten abgefragt
- [ ] B0 Lern-Vault angelegt, Kartendatei hineinkopiert
- [ ] B2 Remotely Save mit Dropbox verbunden, einmal gesynct

**Morgen, Bahn (Block 1):**

- [ ] B3 Obsidian am iPhone, Vault-Name identisch, gesynct
- [ ] B3.8 Spaced Repetition am Handy aktiviert
- [ ] Erste Runde Karten unterwegs
