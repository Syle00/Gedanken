---
description: Erzeugt die vorbefuellte Daily-Bias-Datei fuer den naechsten Handelstag (News, Levels, Wiki-Bezug, eigene Einschaetzung) -- fuer den Scheduled Cron um 20:00 werktags oder manuellen Aufruf am Vorabend
---

Erzeuge `raw/journal/Daily Bias YYYY-MM-DD.md` fuer den naechsten Handelstag.

1. **Zieldatum bestimmen.** `date -d tomorrow +%Y-%m-%d`. Faellt das Ergebnis auf Samstag
   oder Sonntag, stattdessen `date -d "next monday" +%Y-%m-%d` verwenden. Das Ergebnis ist
   `<ZIEL>` fuer den Rest dieses Laufs.

2. **News (Red/Orange Folder).** WebFetch auf
   `https://www.forexfactory.com/calendar?day=<ZIEL als "mmmDD.YYYY", z.B. aug14.2026>`
   mit dem Auftrag, alle Events mit Impact-Farbe Red oder Orange fuer diesen Tag als Liste
   (Uhrzeit NY, Event-Name, Impact) zu extrahieren. Uhrzeit zusaetzlich nach DE-Zeit umrechnen
   (Sommerzeit beachten, analog zum bestehenden Muster in `raw/Daily Bias 13.08.md`: "PPI News
   um 14.30 DE Zeit also 8.30 Ny"). Schlaegt der Abruf fehl oder liefert kein auswertbares
   Ergebnis (Layout-Aenderung, Netzwerkfehler): NICHT abbrechen, sondern im News-Abschnitt
   `⚠️ News-Abruf fehlgeschlagen, manuell auf forexfactory.com pruefen` eintragen und mit den
   naechsten Schritten weitermachen.

3. **NDOG/NWOG/ORG-Levels.** `python algo/live_status.py` ausfuehren (frischer Live-Lauf, siehe
   [[Immer frische Marktdaten]] -- niemals einen aelteren Lauf aus diesem oder einem frueheren
   Gespraech wiederverwenden). Aus der JSON-Ausgabe `ndog_today` (Open/Close), `nwog_today`
   (falls nicht null, nur montags gesetzt) und `org_ce` (Gap + C.E.-Level) entnehmen. Ist
   `market_data: false`, das im generierten Dokument als `⚠️ Live-Daten nicht verfuegbar (Markt
   geschlossen oder Datenfehler)` vermerken statt Platzhalter-Zahlen zu erfinden.

4. **Wochen-/Vortages-Range.** `python algo/bias_levels.py <ZIEL>` ausfuehren. `weekly_range`
   (high/low/days) und `yesterday_range` (high/low/close) aus der JSON-Ausgabe entnehmen.

5. **Levels-Tabelle bauen** (immer als Markdown-Tabelle, nicht als Fliesstext):

   | Level | Open | Close |
   |---|---|---|
   | NWOG | ... | ... |
   | NDOG | ... | ... |

   Darunter: Weekly Range (High/Low aus Schritt 4), gestrige Daily Range H/L/C (aus Schritt 4),
   ORG-C.E. (aus Schritt 3, falls vorhanden). Fehlt ein Wert (null/None), die Zeile weglassen
   statt eine erfundene Zahl einzutragen.

6. **Weekly-Bias-Rueckverlinkung.** ISO-Kalenderwoche von `<ZIEL>` bestimmen
   (`date -d <ZIEL> +%V`, Jahr `date -d <ZIEL> +%Y`). Nach
   `raw/journal/Weekly Bias KW<NN> <JAHR>.md` suchen (Glob). Existiert die Datei: Wikilink
   `[[Weekly Bias KW<NN> <JAHR>]]` einfuegen. Existiert sie nicht: den Hinweis
   `_(noch kein Weekly Bias fuer diese Woche geschrieben)_` einfuegen statt eines toten Links.

7. **Wiki-Bezug.** Immer [[Weekly Range Trading Model]] verlinken, plus die zum Wochentag
   passende(n) Daily-Range-Seite(n) aus `wiki/concepts/` (z.B. [[ICT Daily Range Session
   Timing]], [[Midnight Opening Range]], [[ORG (Opening Range Gap) & 1st Presented FVG]]) --
   eigenes fachliches Urteil, welche am Zieltag am relevantesten sind (z.B. Montag ->
   zusaetzlich NWOG-fokussierte Seiten).

8. **Einschaetzung (Claude).** Eigener, klar markierter Abschnitt `## Einschaetzung (Claude)`
   mit einer kurzen Richtungs-/Wahrscheinlichkeitsaussage. Stuetze sie auf vorhandene
   Backtest-/Statistik-Funde: `algo/seasonal_tendency.json` (Wochentag-Kennzahl fuer den
   Wochentag von `<ZIEL>`), laufende `wiki/synthesis/*(laufend)*`-Seiten, sowie -- falls im
   News-Block ein Red-Folder-Event steht -- ggf. `algo/backtest_fred_events.py`-Erkenntnisse.
   Erwaehne die ORG-C.E.-70%-These als laufend beobachtete Hypothese, wenn `org_ce` in Schritt 3
   gesetzt ist (siehe [[ORG-C.E. 70%-These]]-Konvention: nicht als erledigt/widerlegt
   abhaken). Diesen Abschnitt klar von Schritt 9 abgrenzen -- keine Vermischung mit dem
   Nutzertext.

9. **Datei schreiben** nach `raw/journal/Daily Bias <ZIEL>.md`:

   ```markdown
   # Daily Bias <ZIEL>

   > Weekly Bias: [[Weekly Bias KW<NN> <JAHR>]]  <!-- oder Platzhalter aus Schritt 6 -->

   ## News (Red/Orange Folder)
   <Tabelle aus Schritt 2, oder Warnzeile>

   ## Levels
   <Tabelle + Zeilen aus Schritt 5>

   ## Wiki-Bezug
   <Wikilinks aus Schritt 7>

   ## Einschaetzung (Claude)
   <Text aus Schritt 8>

   ## Mein Bias

   ```

   Existiert die Datei bereits (Command wurde fuer denselben Tag zweimal aufgerufen): fragen,
   ob ueberschrieben werden soll, statt stillschweigend zu ersetzen (koennte bereits
   Nutzertext enthalten).

10. Kurz im Chat bestaetigen: Pfad der geschriebenen Datei + eine Zeile, ob News-Abruf und
    Live-Daten erfolgreich waren oder eine Warnung gesetzt wurde. Kein `push.ps1`-Aufruf.
