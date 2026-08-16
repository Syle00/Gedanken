---
description: Erzeugt die vorbefuellte Weekly-Bias-Datei fuer die kommende Handelswoche (News, Levels, Wiki-Bezug, eigene Einschaetzung) -- fuer den Cron freitags 20:00 oder manuellen Aufruf
---

Erzeuge `raw/journal/bias/weekly/Weekly Bias KW<NN> <JAHR>.md` fuer die kommende Handelswoche.

1. **Zielwoche + Levels + News holen.** `python algo/bias_levels.py --weekly` ausfuehren.
   Die JSON-Ausgabe liefert `target_week` (`monday`, `kw`, `year` -- daraus `<NN>`/`<JAHR>`
   fuer den Dateinamen), `letzte_woche` (High/Low/Tage der auslaufenden Woche als Referenz)
   und `news` (alle Red-/Orange-Folder-Events Mo-Fr der Zielwoche, NY- und DE-Zeit fertig).
   Kein WebFetch auf forexfactory.com -- HTTP 403 fuer Bots.

2. **News-Abschnitt.** Tabelle
   `| Tag | NY | DE | Waehrung | Event | Impact | Forecast | Previous |`, Red-Folder-Termine
   (NFP, CPI, FOMC) hervorheben.

   `news.source` **immer mit ausgeben** (eine Zeile unter der Tabelle). Freitags abends kennt
   ForexFactory die kommende Woche noch nicht, dann steht dort `tradingview` plus ein
   `news.hinweis` -- das ist der Normalfall fuer diesen Command, kein Fehler. Wichtig fuer
   dich beim Lesen: TradingView stuft mehr Events als Red ein als ForexFactory (z.B. Retail
   Sales, Michigan Sentiment); die *Uhrzeiten* beider Quellen sind deckungsgleich geprueft.

   Ist `news.error` gesetzt (beide Quellen tot) oder `news.events` leer:
   `⚠️ News-Abruf fehlgeschlagen (<news.error>), manuell auf forexfactory.com pruefen`
   eintragen und weitermachen -- nie abbrechen, nie Events erfinden.

3. **NWOG-Levels.** `python algo/live_status.py` ausfuehren (frischer Lauf). `nwog_today`
   (Open/Close) und `nwog_open_history` (noch offene NWOG-Level der letzten 5 Wochen als
   DOL-Kandidaten) entnehmen. Bei `market_data: false`:
   `⚠️ Live-Daten nicht verfuegbar (Wochenende/Datenfehler)` statt Zahlen.

4. **Levels-Tabelle bauen** (immer Tabelle):

   | Level | Open | Close |
   |---|---|---|
   | NWOG (aktuell) | ... | ... |

   Darunter Range der auslaufenden Woche (aus `letzte_woche`) und die offenen NWOG-Level
   (Datum + Level) aus Schritt 3, falls nicht leer. Preise aufs 0,25-Tickraster.

5. **Wiki-Bezug.** Immer [[Weekly Range Trading Model]] und [[IPDA Data Ranges]], plus nach
   eigenem Urteil z.B. [[Using Monthly & Weekly Ranges (Source)]] (Monatswechsel, NFP-Woche).

6. **Einschaetzung (Claude).** Wochenrichtung + Wahrscheinlichkeit, gestuetzt auf
   `algo/seasonal_tendency.json` (Wochen-/Turn-of-Month-Muster), `algo/backtest_nwog.py`
   (Bias-intakt-Quote nur 7% -- diese Einschraenkung bei jeder NWOG-Richtungsaussage nennen)
   und die Red-Folder-Events aus Schritt 2 (NFP-Woche -> `algo/backtest_nfp_week.py`).

7. **Datei schreiben** nach `raw/journal/bias/weekly/Weekly Bias KW<NN> <JAHR>.md`:

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
