---
description: Ein Live-Status-Zyklus fuer MNQ -- frische Daten ziehen, mit den Algo-Signalen abgleichen, Bericht schreiben (fuer /loop 10m /algo-live-status)
---

Fuehre einen einzelnen Live-Status-Zyklus fuer MNQ aus.

1. `python algo/live_status.py` ausfuehren und die JSON-Ausgabe lesen.
2. Falls `market_data: false`: kurz vermerken, dass der Markt vermutlich geschlossen ist
   (oder der Datenabruf fehlgeschlagen ist) und den Zyklus damit beenden -- keinen
   Bericht erfinden.
3. Die letzten Zeilen von `algo/live/<day>-status-log.md` lesen (falls vorhanden;
   `<day>` ist das `day`-Feld aus der JSON-Ausgabe), um an die letzte Einschaetzung
   anzuknuepfen.
4. Einen kurzen deutschen Statusbericht schreiben mit drei Teilen:
   - **Stand**: aktueller Preis, aktives Makro-/Silver-Bullet-Fenster (falls eins aktiv ist).
   - **Abgleich**: die Eintraege in `new_events` gegen das, was die Algo-Signale fuer
     diese Fenster/Uhrzeit erwarten lassen wuerden -- deckt sich das oder nicht?
     Bei leerem `new_events`: kurz sagen, dass sich seit dem letzten Lauf nichts
     Neues ergeben hat.
   - **Ausblick**: eigene Einschaetzung, was als naechstes plausibel ist (z.B. naechstes
     Zeitfenster, offenes `setup`-Target, unberuehrte Liquiditaet in der Naehe).

   Ist `first_run: true`, das explizit sagen und `new_events` als Startaufnahme des
   ganzen Handelstages behandeln, nicht als Liste dessen, was gerade eben passiert ist.
5. Den Bericht mit Zeitstempel an `algo/live/<day>-status-log.md` anhaengen (Datei
   anlegen, falls sie noch nicht existiert) und ihn auch im Chat ausgeben.
