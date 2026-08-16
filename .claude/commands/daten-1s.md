---
description: 1s-Datenanbindung fuer NQ/ES ueber IBKR -- Nachlad, Verify oder Backfill, je nach Argument (Design docs/superpowers/specs/2026-08-15-ibkr-1s-datenanbindung-design.md)
---

Fuehre einen Datenabruf ueber `algo/fetch_ibkr.py` aus. Argumente (siehe `$ARGUMENTS`,
alle optional, Default = Nachlad):

- kein Argument: Nachlad (letzter Registereintrag bis gestern, beide Symbole)
- `verify`: Einzelfenster-Verifikation, schreibt nichts
- `NQ` oder `ES`: schraenkt jede Betriebsart auf ein Symbol ein
- `backfill`: **gesamte verfuegbare 1s-Historie** (letzte 183 Tage bis zum letzten
  Handelstag -- so weit reicht IBKRs 1s-Vorhaltung)
- `backfill <von> <bis>`: Backfill fuer einen bestimmten Zeitraum (ISO-Daten, z.B.
  `2026-02-17 2026-08-14`)

Kombinierbar, z.B. `verify ES` oder `backfill 2026-02-17 2026-08-14 NQ`.

Jeder Backfill ist beliebig oft wiederholbar und setzt von selbst fort: Tage, deren
Parquet-Datei schon existiert, werden ohne einen einzigen Request uebersprungen. Ein
abgebrochener Lauf wird also einfach neu gestartet -- es braucht keine Datumsangabe, um
"dort weiterzumachen, wo es aufhoerte".

1. Pruefe, ob Port 4002 (IB Gateway, Paper) erreichbar ist (z.B. per kurzem TCP-Connect-Test).
   Nicht erreichbar: melde, dass IB Gateway nicht laeuft, und brich ab -- lauf nicht in
   einen Timeout.
2. Baue daraus den passenden Aufruf von `python algo/fetch_ibkr.py [--verify|--backfill [VON BIS]]
   [--symbol SYM]` und starte ihn. Bei `backfill`: im Hintergrund, weil die Laufzeit in
   Stunden liegt (siehe Design SS3.4) -- nicht auf den Abschluss warten, sondern das Anlaufen
   bestaetigen und mitteilen, wie der Fortschritt spaeter geprueft werden kann (Registerzeilen
   in `raw/marktdaten/1s-abdeckung.csv`). Das Skript oeffnet dabei selbst ein zweites
   Konsolenfenster, das jeden Fenster-Download live mitschreibt (Log:
   `algo/live/fetch_ibkr-<datum>.log`) -- weise darauf hin, statt eine eigene
   Fortschrittsanzeige zu bauen. `--kein-fenster` unterdrueckt es fuer unbeaufsichtigte Laeufe.
3. Verdichte die Konsolenausgabe zu einem Bericht statt sie durchzureichen: geholte Fenster
   je Symbol, geschriebene Tagesdateien, Kerzenzahl, Quote handelsloser Sekunden je Session
   (falls ausgegeben), alle Hinweise aus `pruefe_kerzen()`, fehlgeschlagene Fenster,
   verbleibende Luecken laut Register.
4. Kein `push.ps1` -- Veroeffentlichen bleibt manuell (siehe CLAUDE.md, Versionskontrolle).
