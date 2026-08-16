---
description: Erzeugt die vorbefuellte Daily-Bias-Datei fuer den naechsten Handelstag (News, Levels, Wiki-Bezug, eigene Einschaetzung) -- fuer den Cron So-Do 20:00 oder manuellen Aufruf am Vorabend
---

Erzeuge `raw/journal/Daily Bias <ZIEL>.md` fuer den naechsten Handelstag.

> Ablage bewusst flach in `raw/journal/`: frische Bias-Dateien bleiben dort sichtbar, solange
> sie aktuell sind. `tools/sortiere_bias.py` raeumt sie nach Ablauf des Tages selbst nach
> `raw/journal/bias/daily/` -- nicht selbst dorthin schreiben.

1. **Levels + News holen.** `python algo/bias_levels.py --next` ausfuehren. Die JSON-Ausgabe
   liefert alles auf einmal: `day` (= `<ZIEL>`, Sa/So sind schon auf Montag geschoben),
   `weekday`, `weekly_range`, `yesterday_range` und `news` (Red-/Orange-Folder-Events aus dem
   offiziellen ForexFactory-JSON-Feed, NY- und DE-Zeit bereits umgerechnet).
   Kein WebFetch auf forexfactory.com -- die HTML-Seite antwortet Bots mit HTTP 403.

2. **News-Abschnitt.** Ist `news.error` gesetzt oder `news.events` leer, im News-Abschnitt
   `⚠️ News-Abruf fehlgeschlagen (<news.error>), manuell auf forexfactory.com pruefen`
   eintragen und weitermachen -- nie abbrechen, nie Events erfinden. Sonst Tabelle:
   `| NY | DE | Waehrung | Event | Impact | Forecast | Previous |`, Red-Folder-Events (USD
   zuerst) hervorheben.

   `news.source` mit ausgeben: normalerweise `forexfactory`, bei einem Zieltag ausserhalb der
   laufenden FF-Woche (Sonntagslauf fuer Montag) `tradingview` plus `news.hinweis` -- kein
   Fehler, nur eine andere Quelle. TradingView stuft mehr Events als Red ein als
   ForexFactory; die Uhrzeiten beider Quellen sind deckungsgleich geprueft.

3. **NDOG/NWOG/ORG-Levels.** `python algo/live_status.py` ausfuehren (frischer Lauf --
   niemals einen aelteren Lauf aus diesem oder einem frueheren Gespraech wiederverwenden,
   siehe CLAUDE.md "Frische Live-Daten"). `ndog_today`, `nwog_today` (nur montags gesetzt)
   und `org_ce` entnehmen. Ist `market_data: false`, statt Zahlen
   `⚠️ Live-Daten nicht verfuegbar (Markt geschlossen oder Datenfehler)` eintragen.

4. **Levels-Tabelle bauen** (immer Tabelle, nie Fliesstext):

   | Level | Open | Close |
   |---|---|---|
   | NWOG | ... | ... |
   | NDOG | ... | ... |

   Darunter Weekly Range (High/Low aus Schritt 1), gestrige Daily Range H/L/C (Schritt 1),
   ORG-C.E. (Schritt 3). Fehlende Werte (`null`): Zeile weglassen statt Zahl erfinden.
   Alle Preise aufs 0,25-Tickraster (MNQ).

5. **Weekly-Bias-Rueckverlinkung.** ISO-KW von `<ZIEL>` bestimmen, nach
   `Weekly Bias KW<NN> <JAHR>.md` globben -- erst in `raw/journal/`, dann in
   `raw/journal/bias/weekly/` (schon einsortiert). Existiert sie: Wikilink
   `[[Weekly Bias KW<NN> <JAHR>]]`. Sonst `_(noch kein Weekly Bias fuer diese Woche)_` --
   keinen toten Link setzen.

6. **Wiki-Bezug.** Immer [[Weekly Range Trading Model]], plus die zum Wochentag passenden
   Daily-Range-Seiten aus `wiki/concepts/` (z.B. [[ICT Daily Range Session Timing]],
   [[Midnight Opening Range]], [[ORG (Opening Range Gap) & 1st Presented FVG]]) -- eigenes
   fachliches Urteil, montags zusaetzlich NWOG-Seiten.

7. **Einschaetzung (Claude).** Eigener Abschnitt mit kurzer Richtungs-/Wahrscheinlichkeits-
   aussage, gestuetzt auf `algo/seasonal_tendency.json` (Wochentag-Kennzahl), laufende
   `wiki/synthesis/*(laufend)*`-Seiten und -- bei Red-Folder-Events -- `algo/backtest_fred_events.py`.
   Ist `org_ce` gesetzt, die ORG-C.E.-70%-These als *laufend beobachtete* Hypothese erwaehnen
   (empirisch bislang 35-43%, laut Nutzerentscheid nicht als widerlegt abhaken).
   Klar getrennt vom Nutzerbereich.

8. **Datei schreiben** nach `raw/journal/Daily Bias <ZIEL>.md`:

   ```markdown
   # Daily Bias <ZIEL>

   > Weekly Bias: [[Weekly Bias KW<NN> <JAHR>]]

   ## News (Red/Orange Folder)
   ## Levels
   ## Wiki-Bezug
   ## Einschaetzung (Claude)
   ## Mein Bias
   ```

   Existiert die Datei schon: fragen statt ueberschreiben (koennte Nutzertext enthalten).

9. Kurz bestaetigen: Pfad + je eine Zeile zu News-Abruf und Live-Daten. Kein `push.ps1`.
