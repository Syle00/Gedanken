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
   **Nur USD** -- `bias_levels.py` filtert das bereits, gehandelt werden NQ/ES.
   Kein WebFetch auf forexfactory.com -- die HTML-Seite antwortet Bots mit HTTP 403.

2. **News-Abschnitt.** Drei Faelle, sauber auseinanderhalten:

   - `news.error` **gesetzt** -> `⚠️ News-Abruf fehlgeschlagen (<news.error>), manuell auf
     forexfactory.com pruefen`. Weitermachen, nie abbrechen, nie Events erfinden.
   - `news.events` **leer, aber `news.error` ist `null`** -> `Keine USD-Termine mit Red-/
     Orange-Impact.` Das ist **kein Fehler**, sondern ein newsarmer Tag und eine verwertbare
     Aussage. Nie als Abruf-Fehler ausgeben.
   - sonst **`news.block` unveraendert uebernehmen** -- **kein** Codeblock, keine Tabelle,
     nichts selbst formatieren. Kommt fertig aus `bias_levels.py::news_block()`: je Termin
     eine Zeile plus Leerzeile, Impact als 🔴/🟠 (**keine** Schriftfarbe -- am 2026-08-16 kurz
     eingebaut und auf Nutzerwunsch wieder entfernt), Uhrzeiten als `14:00 NY / 20:00 DE`,
     Tage ohne Termine mit `❌ keine USD-Termine`.

   `news.source` mit ausgeben: normalerweise `forexfactory`, bei einem Zieltag ausserhalb der
   laufenden FF-Woche (Sonntagslauf fuer Montag) `tradingview` plus `news.hinweis` -- kein
   Fehler, nur eine andere Quelle. TradingView stuft mehr Events als Red ein als
   ForexFactory; die Uhrzeiten beider Quellen sind deckungsgleich geprueft.

3. **NDOG/NWOG aus den Marktdaten.** Stehen bereits in `gaps` aus Schritt 1 -- gerechnet aus
   `raw/marktdaten/`, **1s bevorzugt** (Nutzervorgabe), 1m nur wo kein 1s vorliegt. Nicht aus
   dem Live-Feed, deshalb am Wochenende genauso belastbar wie unter der Woche. Je Eintrag:
   `close`/`close_t` (letzter Print vor 17:00 NY), `open`/`open_t` (erster ab 18:00 NY),
   `gap`, `ce`, `filled`, `quelle`.

   `gaps.datenlage` **immer auswerten und in einer Zeile ausweisen**: `tage_1s`/`tage_nur_1m`
   (nicht "1s-Daten" behaupten, wenn die Mehrheit 1m ist), `registriert_ohne_datei` (in
   `1s-abdeckung.csv` protokolliert, aber keine Parquet-Datei -- stiller Datenverlust, **aktiv
   melden**) und `abgleich_1s_vs_1m` (1s gegen TradingView-1m gegengerechnet; grosse
   Abweichung = eine Quelle stimmt nicht, dann kein Level daraus bauen).

   `gaps.offen` sind die **noch ungefuellten** Gaps -- handelbare PD Arrays und DOL-Kandidaten,
   die wichtigsten Level des Abschnitts. `gaps.symbol` und ein evtl. `gaps.hinweis` mit
   ausgeben (faellt NQ mangels Historie auf MNQ zurueck, muss das dranstehen).

   **Nie erwaehnen, dass das kommende NWOG-Open noch nicht feststeht.** Es wird das
   hinterlegt, was in den Daten steht; ueber noch nicht gehandelte Opens wird nicht spekuliert
   und auch nicht darauf hingewiesen, dass sie fehlen.

4. **ORG-C.E. + aktueller Preis.** `python algo/live_status.py` ausfuehren (frischer Lauf --
   niemals einen aelteren Lauf wiederverwenden, siehe CLAUDE.md "Frische Live-Daten").
   Nur noch `org_ce` und `price` entnehmen; NDOG/NWOG kommen aus Schritt 3.
   Bei `market_data: false` die ORG-Zeile schlicht weglassen -- keine Warnung, kein Platzhalter.

5. **Levels-Tabelle bauen** (immer Tabelle, nie Fliesstext):

   | Level | Datum | Close (17:00) | Open (18:00) | Gap | C.E. | Status |
   |---|---|---|---|---|---|---|
   | NWOG | ... | ... | ... | ... | ... | offen / gefuellt |
   | NDOG | ... | ... | ... | ... | ... | offen / gefuellt |

   Reihenfolge: **offene Gaps zuerst** (`gaps.offen`, neueste oben), danach die NDOGs der
   vergangenen Handelswoche. Darunter Weekly Range (High/Low aus Schritt 1), gestrige Daily
   Range H/L/C (Schritt 1) und ORG-C.E. (Schritt 4).
   Fehlende Werte (`null`): Zeile weglassen statt Zahl erfinden.
   Alle Preise aufs 0,25-Tickraster.

   **Zu jedem offenen Gap zusaetzlich die volle Qs/Os/Hs-Tabelle** (steht fertig in `hs`,
   `qs`, `os`, `ce` je Eintrag -- nicht selbst rechnen, ist bereits aufs Raster gerundet):

   | | Level |
   |---|---|
   | High (Open) | ... |
   | O7 / O6 / O5 | ... |
   | Q3 | ... |
   | **C.E. (= H1 = Q2 = O4)** | ... |
   | Q1 | ... |
   | O3 / O2 / O1 | ... |
   | Low (Close) | ... |

   Immer von oben nach unten lesbar. C.E. hervorheben -- es ist der meistgenutzte Bezugspunkt.

6. **Weekly-Bias-Rueckverlinkung.** ISO-KW von `<ZIEL>` bestimmen, nach
   `Weekly Bias KW<NN> <JAHR>.md` globben -- erst in `raw/journal/`, dann in
   `raw/journal/bias/weekly/` (schon einsortiert). Existiert sie: Wikilink
   `[[Weekly Bias KW<NN> <JAHR>]]`. Sonst `_(noch kein Weekly Bias fuer diese Woche)_` --
   keinen toten Link setzen.

7. **Wiki-Bezug.** Immer [[Weekly Range Trading Model]], plus die zum Wochentag passenden
   Daily-Range-Seiten aus `wiki/concepts/` (z.B. [[ICT Daily Range Session Timing]],
   [[Midnight Opening Range]], [[ORG (Opening Range Gap) & 1st Presented FVG]]) -- eigenes
   fachliches Urteil, montags zusaetzlich NWOG-Seiten.

8. **Einschaetzung (Claude).** Eigener Abschnitt mit kurzer Richtungs-/Wahrscheinlichkeits-
   aussage, gestuetzt auf `algo/seasonal_tendency.json` (Wochentag-Kennzahl), laufende
   `wiki/synthesis/*(laufend)*`-Seiten und -- bei Red-Folder-Events -- `algo/backtest_fred_events.py`.
   Ist `org_ce` gesetzt, die ORG-C.E.-70%-These als *laufend beobachtete* Hypothese erwaehnen
   (empirisch bislang 35-43%, laut Nutzerentscheid nicht als widerlegt abhaken).
   Klar getrennt vom Nutzerbereich.

9. **Datei schreiben** nach `raw/journal/Daily Bias <ZIEL>.md`:

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

10. Kurz bestaetigen: Pfad + je eine Zeile zu News-Abruf und Live-Daten. Kein `push.ps1`.
