---
description: Tagesbericht -- fasst zusammen, was heute im Vault/Algo erledigt wurde (Git-Historie), thematisch synthetisiert statt nur aufgelistet
---

Schreibe einen Tagesbericht fuer das Gedanken-Vault.

1. Datum bestimmen: heutiges Datum, außer im Aufruf steht ein anderes (z.B. `/tagesbericht 2026-08-04`
   fuer einen Bericht rueckwirkend).
2. Git-Historie des Tages holen:
   `git log --pretty=format:"%ad %s" --date=format:"%H:%M" --since="<Datum> 00:00" --until="<Datum> 23:59" --reverse -- . ':!site' ':!.obsidian'`
   Commits mit der Nachricht `wiki update <Datum>` herausfiltern -- das sind reine
   `push.ps1`-Checkpoints (Build-Artefakte), kein inhaltlicher Fortschritt.
3. Die Motivation hinter den Commits aus deren Messages ableiten. Seit 2026-08-16 sind sie
   aussagekraeftig (`<typ> | <worum ging es>`); `push.ps1` erzwingt das. Fuer Tage **vor** dem
   2026-08-16 stattdessen `wiki/log-archiv-bis-2026-08.md` nach `## [<Datum>]` durchsuchen --
   damals waren alle Commit-Messages `wiki update <Datum>` und damit wertlos.
4. Falls vorhanden, `algo/live/<Datum>-status-log.md` auf Live-Trading-Beobachtungen des Tages
   pruefen.
5. Daraus einen **thematisch gruppierten** Bericht auf Deutsch schreiben (nicht chronologisch
   auflisten, nicht 1:1 die Commit-Messages wiederholen) -- z.B. nach Themenbloecken wie
   "Algo/Backtest", "Wiki-Ingest", "Trading-Journal", "Korrekturen": was wurde gebaut/entschieden,
   was war die Motivation (aus den Commit-Messages bzw. dem Archiv), was ist am Ende offen
   geblieben. Kurz halten, keine
   Ueberschriften-Schlacht -- Ziel ist ein Ueberblick zum Vorlesen, keine Doku-Seite.
6. Nur im Chat ausgeben. Kein neuer wiki/log.md-Eintrag, keine neue Wiki-Seite, kein
   `push.ps1` -- reiner Status-Report ueber bereits erledigte Arbeit.
