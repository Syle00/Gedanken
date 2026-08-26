---
tags: [lernen, cs50, obsidian, howto]
created: 2026-08-26
updated: 2026-08-26
sources: []
---

# CS50 — Karteikarten & Handy-Sync einrichten

Zwei getrennte Baustellen, die morgen in der Bahn abgearbeitet werden können.
Teil A geht **am Desktop** (10 Min), Teil B braucht Desktop **und** iPhone (20–30 Min).

> **Warum kein Anki:** Die iOS-App AnkiMobile ist kostenpflichtig (Einmalkauf, ca. 30 €).
> Obsidian ist auf iOS kostenlos, und mit dem Plugin *Spaced Repetition* bekommst du
> denselben Lernalgorithmus (SM-2, wie bei Anki) direkt im Vault.

---

## Teil A — Karteikarten in Obsidian anlegen

### A1. Plugin installieren (Desktop)

1. Obsidian öffnen → unten links **Zahnrad** (Einstellungen).
2. Links **Community-Plugins** anklicken.
3. Falls „Eingeschränkter Modus / Restricted Mode" **an** ist: **ausschalten**.
   (Obsidian warnt einmal, dass Plugins Code ausführen — bestätigen.)
4. **Durchsuchen / Browse** → im Suchfeld `Spaced Repetition` eingeben.
5. Den Treffer von **st3v3nmw** (Stephen Mwangi) wählen → **Installieren** → **Aktivieren**.

> Es gibt mehrere Flashcard-Plugins. Nimm genau dieses — es ist das ausgereifteste und
> das einzige mit gutem Mobile-Support. Das Alternativplugin *Flashcards* exportiert
> nur nach Anki und bringt dir hier nichts.

### A2. Karten schreiben — die Syntax

Eine Karteikarte ist **eine Zeile in einer ganz normalen Markdown-Notiz**. Kein extra
Editor, keine Datenbank. Die Datei braucht nur irgendwo den Tag `#flashcards`.

| Was du willst | Wie du es schreibst |
|---|---|
| Einfache Karte (nur Vorderseite → Rückseite) | `Frage::Antwort` |
| Karte in **beide** Richtungen abgefragt | `Frage:::Antwort` |
| Mehrzeilige Karte | Frage, dann `?` allein in einer Zeile, dann Antwort |
| Mehrzeilig, beide Richtungen | dasselbe, aber `??` statt `?` |
| Lückentext (Cloze) | Text mit `==markierter Stelle==` — die wird abgefragt |

Beispiel, so sieht eine fertige Datei aus:

```markdown
---
tags: [flashcards]
---

# CS50 Python

Was liefert `input()` immer zurück?::Einen **String**, nie eine Zahl.

Was ergibt `int(3.9)`?::`3` — `int()` schneidet ab, es rundet nicht.

Was ist der Unterschied zwischen `/` und `//`?
?
`/` liefert immer einen float (`6 / 3` → `2.0`),
`//` liefert die Ganzzahldivision (`7 // 2` → `3`).
```

### A3. Stapel (Decks) sortieren

Der Tag bestimmt den Stapel. Unterstapel mit Schrägstrich:

- `#flashcards/cs50/python` → Stapel „cs50" mit Unterstapel „python"
- `#flashcards/trading/ict` → getrennter Stapel fürs Trading-Material

So wächst später alles im selben Vault, ohne sich zu vermischen.

### A4. Lernen starten

- Linke Seitenleiste: neues Icon (Stapel-Symbol) → **Review flashcards**
- Oder: `Strg + P` → `Spaced Repetition: Review flashcards` tippen

Beim Abfragen bewertest du dich selbst mit **Hard / Good / Easy** — daraus berechnet das
Plugin, wann die Karte wieder drankommt. Nichts weiter einzustellen.

> **Startdatei liegt schon bereit:** [[CS50 Python — Karteikarten]] — rund 30 fertige
> Karten zu `int`, `input()`, Strings und Funktionen. Einfach öffnen und lernen.

---

## Teil B — Vault aufs iPhone bringen

### B0. Wichtig zuerst: nicht den Hauptvault synchronisieren

`VS Folder 1` enthält `raw/` mit rund 190 MB Screenshots plus die Marktdaten-CSVs.
Das aufs Handy zu spiegeln ist langsam, frisst Speicher und geht beim Sync gerne schief.

**Leg einen zweiten, kleinen Vault nur fürs Lernen an.** Der Trading-Vault bleibt
unangetastet auf dem Desktop und in seinem Git-Repo.

1. Neuen Ordner anlegen: `C:\Users\Jannes\Desktop\CS50-Vault`
2. Obsidian → unten links **Vault-Symbol** → **Andere Vaults verwalten** →
   **Ordner als Vault öffnen** → den neuen Ordner wählen.
3. Karteikartendatei aus Teil A dorthin kopieren.

### B1. Sync-Weg wählen (Windows + iPhone)

| Weg | Kosten | Urteil |
|---|---|---|
| **Remotely Save + Dropbox** | kostenlos | **Empfohlen.** Funktioniert unter Windows und iOS. |
| Obsidian Sync (offiziell) | Abo | Am zuverlässigsten, aber kostet — und du wolltest ja gerade sparen. |
| iCloud für Windows | kostenlos | **Nicht empfehlen.** Unter Windows gibt es wiederholt Berichte über doppelte und beschädigte Dateien. Auf reinen Apple-Geräten wäre es der einfachste Weg — du bist aber auf Windows. |
| Git + Working Copy (iOS) | App kostet für Push | Naheliegend, weil du Git ohnehin nutzt. Die Gratis-Version von Working Copy kann nur klonen/ziehen, nicht pushen. |

### B2. Remotely Save einrichten — Desktop

1. Dropbox-Konto anlegen (kostenlos, 2 GB — für Textnotizen mehr als genug).
2. In Obsidian im **CS50-Vault**: Einstellungen → Community-Plugins → Durchsuchen →
   `Remotely Save` → Installieren → Aktivieren.
3. Einstellungen → **Remotely Save** → bei *Remote Service* **Dropbox** wählen.
4. **Auth** anklicken → Browser öffnet sich → mit Dropbox anmelden → Zugriff erlauben →
   den angezeigten Code zurück in Obsidian kopieren.
5. Links in der Seitenleiste erscheint ein **Sync-Symbol** → einmal anklicken.
   Der Vault landet in Dropbox unter `Apps/remotely-save/CS50-Vault`.

> Falls die Dropbox-Anmeldung zickt: dasselbe Plugin kann auch **OneDrive** — du hast als
> Windows-Nutzer ohnehin ein Microsoft-Konto. Der Ablauf ist identisch.

### B3. Remotely Save einrichten — iPhone

1. **Obsidian** aus dem App Store laden (kostenlos).
2. App öffnen → **Create new vault**.
3. Als Namen **exakt** `CS50-Vault` eingeben — Groß-/Kleinschreibung identisch.
   ⚠️ Das ist der Schritt, an dem es am häufigsten scheitert: heißt der Vault am Handy
   anders, legt das Plugin einen zweiten, getrennten Ordner in der Dropbox an und nichts
   findet zusammen.
4. „Store in iCloud" darf **aus** bleiben.
5. In der App: Einstellungen (Zahnrad) → **Community Plugins** → Eingeschränkten Modus aus
   → `Remotely Save` suchen → installieren → aktivieren.
6. Dropbox genauso authentifizieren wie in B2.
7. Sync-Symbol antippen → deine Karten erscheinen.
8. Zum Schluss noch **Spaced Repetition** auch am Handy installieren und aktivieren.

### B4. Ab dann

Vor dem Aussteigen am Handy einmal auf **Sync** tippen, am Desktop nach dem Öffnen
ebenfalls. Das Plugin kann auch automatisch synchronisieren — in den Plugin-Einstellungen
unter *Schedule for auto run* z. B. „every 5 minutes" setzen.

---

## Checkliste für morgen

- [ ] A1 Spaced-Repetition-Plugin installiert
- [ ] A4 einmal eine Runde Karten abgefragt
- [ ] B0 CS50-Vault angelegt
- [ ] B2 Remotely Save am Desktop verbunden, einmal gesynct
- [ ] B3 Obsidian am iPhone installiert, gleicher Vault-Name, gesynct
- [ ] B3.8 Spaced Repetition am Handy aktiviert
