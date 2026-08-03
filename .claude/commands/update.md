---
description: Holt den neuesten Stand des Gedanken-Vaults von GitHub (für Arbeit auf mehreren Rechnern)
---

Synchronisiere das lokale Repo mit `origin/main` auf GitHub (https://github.com/Syle00/Gedanken),
damit dieser Rechner auf dem neuesten Stand ist.

1. `git status` prüfen. Bei uncommitteten Änderungen: `git stash push -u -m "auto-stash vor /update"`.
2. `git pull origin main` ausführen.
   - Bei Merge-Konflikten: nicht automatisch auflösen, sondern dem Nutzer die
     betroffenen Dateien nennen und um Anweisung bitten.
3. Falls in Schritt 1 gestasht wurde: `git stash pop`. Bei Konflikten beim Pop: Zustand
   erklären, nichts verwerfen.
4. Kurz zusammenfassen, was reingekommen ist (`git log HEAD@{1}..HEAD --oneline`, falls
   es einen Fast-Forward/Merge gab) — z.B. neue Ingests, Wiki-Änderungen.

Kein Rebuild nötig: `push.ps1` baut `site/` bereits vor jedem Push, der gepullte Stand
ist also konsistent.
