---
description: Erzeugt die vorbefuellte Weekly-Bias-Datei fuer die kommende Handelswoche (News, Levels, Wiki-Bezug, eigene Einschaetzung) -- fuer den Cron freitags 20:00 oder manuellen Aufruf
---

Erzeuge `raw/journal/Weekly Bias KW<NN> <JAHR>.md` fuer die kommende Handelswoche.

> Ablage bewusst flach in `raw/journal/`: frische Bias-Dateien bleiben dort sichtbar, solange
> sie aktuell sind. `tools/sortiere_bias.py` raeumt sie nach Ablauf der Woche selbst nach
> `raw/journal/bias/weekly/` -- nicht selbst dorthin schreiben.

1. **Zielwoche + Levels + News holen.** `python algo/bias_levels.py --weekly` ausfuehren.
   Die JSON-Ausgabe liefert `target_week` (`monday`, `kw`, `year` -- daraus `<NN>`/`<JAHR>`
   fuer den Dateinamen), `letzte_woche` (High/Low/Tage der auslaufenden Woche als Referenz)
   und `news` (alle Red-/Orange-Folder-Events Mo-Fr der Zielwoche, NY- und DE-Zeit fertig).
   **Nur USD** -- `bias_levels.py` filtert das bereits, gehandelt werden NQ/ES.
   Kein WebFetch auf forexfactory.com -- HTTP 403 fuer Bots.

2. **News-Abschnitt.** Tabelle
   `| Tag | NY | DE | Event | Impact | Forecast | Previous |`, Red-Folder-Termine
   (NFP, CPI, FOMC) hervorheben. Keine Waehrungsspalte -- es ist durchgaengig USD.

   `news.source` **immer mit ausgeben** (eine Zeile unter der Tabelle). Freitags abends kennt
   ForexFactory die kommende Woche noch nicht, dann steht dort `tradingview` plus ein
   `news.hinweis` -- das ist der Normalfall fuer diesen Command, kein Fehler. Wichtig fuer
   dich beim Lesen: TradingView stuft mehr Events als Red ein als ForexFactory (z.B. Retail
   Sales, Michigan Sentiment); die *Uhrzeiten* beider Quellen sind deckungsgleich geprueft.

   Ist `news.error` gesetzt (beide Quellen tot):
   `⚠️ News-Abruf fehlgeschlagen (<news.error>), manuell auf forexfactory.com pruefen`
   eintragen und weitermachen -- nie abbrechen, nie Events erfinden.

   Sind `news.events` **leer, aber `news.error` ist `null`**: `Keine USD-Termine mit Red-/
   Orange-Impact in dieser Woche.` Das ist **kein Fehler**, sondern eine newsarme Woche --
   seit dem USD-Filter ein realistischer Fall. Nie als Abruf-Fehler ausgeben.

3. **NDOG/NWOG aus den Marktdaten.** Stehen bereits in `gaps` aus Schritt 1 -- gerechnet aus
   `raw/marktdaten/` (1s wo vorhanden, sonst 1m), nicht aus dem Live-Feed. Deshalb am
   Wochenende, wenn dieser Command laeuft, genauso belastbar wie unter der Woche.
   Je Eintrag: `close`/`close_t` (letzter Print vor 17:00 NY), `open`/`open_t` (erster ab
   18:00 NY), `gap`, `ce`, `filled`, `quelle`.

   `gaps.offen` sind die **noch ungefuellten** Gaps -- die DOL-Kandidaten fuer die kommende
   Woche und damit der wichtigste Teil des Abschnitts. `gaps.symbol` und ein evtl.
   `gaps.hinweis` mit ausgeben (faellt NQ mangels Historie auf MNQ zurueck, muss dranstehen).

   **Nie erwaehnen, dass das kommende NWOG-Open noch nicht feststeht.** Es wird hinterlegt,
   was in den Daten steht; ueber noch nicht gehandelte Opens wird nicht spekuliert und auch
   nicht darauf hingewiesen, dass sie fehlen.

4. **Levels-Tabelle bauen** (immer Tabelle):

   | Level | Datum | Close (17:00) | Open (18:00) | Gap | C.E. | Status |
   |---|---|---|---|---|---|---|
   | NWOG | ... | ... | ... | ... | ... | offen / gefuellt |
   | NDOG | ... | ... | ... | ... | ... | offen / gefuellt |

   Reihenfolge: **offene Gaps zuerst** (`gaps.offen`, neueste oben) -- das sind die DOL-
   Kandidaten --, darunter die NWOGs der letzten Wochen und die NDOGs der auslaufenden Woche.
   Danach die Range der auslaufenden Woche (aus `letzte_woche`).
   Preise aufs 0,25-Tickraster.

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

5. **Wiki-Bezug.** Immer [[Weekly Range Trading Model]] und [[IPDA Data Ranges]], plus nach
   eigenem Urteil z.B. [[Using Monthly & Weekly Ranges (Source)]] (Monatswechsel, NFP-Woche).

6. **Einschaetzung (Claude).** Wochenrichtung + Wahrscheinlichkeit, gestuetzt auf
   `algo/seasonal_tendency.json` (Wochen-/Turn-of-Month-Muster), `algo/backtest_nwog.py`
   (Bias-intakt-Quote nur 7% -- diese Einschraenkung bei jeder NWOG-Richtungsaussage nennen)
   und die Red-Folder-Events aus Schritt 2 (NFP-Woche -> `algo/backtest_nfp_week.py`).

7. **Datei schreiben** nach `raw/journal/Weekly Bias KW<NN> <JAHR>.md`:

   ```markdown
   # Weekly Bias KW<NN> <JAHR>

   ## News (Red/Orange Folder), ganze Woche
   ## Levels
   ## Wiki-Bezug
   ## Einschaetzung (Claude)
   ## Mein Bias
   ```

   Existiert die Datei schon: fragen statt ueberschreiben.

8. Kurz bestaetigen: Pfad + Status von News-Abruf und Live-Daten. Kein `push.ps1`.
