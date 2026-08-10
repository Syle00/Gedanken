# Macro-Datenbank & Statistik-Skill — Design-Spec

**Datum:** 2026-08-10
**Status:** Entwurf, wartet auf Freigabe durch Jannes
**Entstanden aus:** Interview-Session (`/superpowers:brainstorming`)
**Betrifft:** neues Modul `algo/macro_db.py`, neuer Skill `.claude/skills/macro-db/`,
Folgekorrektur an `algo/backtest_macro.py`

---

## 1. Zweck

Jedes Macro-Fenster jedes Handelstags soll als **ein Datensatz** erfasst werden: was davor
passierte (Liquidity Sweep, MSS, Displacement, offene FVGs, offene Level), was im Fenster geschah
(Range, Nettoweg, Geradlinigkeit, Richtung), **wann** der Move einsetzte, und **welche Level**
dabei genommen wurden. Aus diesem Bestand beantwortet ein Skill Fragen der Form *"wie oft und wann
tritt Fall X ein"* — mit der Disziplin eines Datenanalysten, nicht mit einer freihändigen
Prozentzahl.

Abgrenzung zum Bestehenden: `algo/backtest_macro.py` beantwortet **eine** Frage (sind Macro-Blöcke
anders als ihre Nachbarblöcke?) und aggregiert sofort. Diese Spec baut die **Zwischenschicht**, die
dort fehlt: eine Zeile pro Fenster, aus der sich beliebige Folgefragen rechnen lassen, ohne die
Rohdaten erneut zu durchlaufen.

Einordnung in `CLAUDE.md`: Unterbau für Layer 0. Roadmap-Stufe 2 (Regel-Schicht) und 3
(Validierung) — die Datenbank liefert die Kennzahlen, aus denen Entry-Regeln abgeleitet und
geprüft werden können.

---

## 2. Getroffene Entscheidungen

| # | Frage | Entscheidung |
|---|---|---|
| 1 | Primärer Zweck | **Forschung/Nachschlagewerk.** Offline-Auswertung über die Historie. Live-Nutzung und Algo-Regeln bauen später darauf auf, sind aber nicht Teil dieser Spec. |
| 2 | Datenbasis | **Nur echte MNQ-Daten** aus `raw/marktdaten/`, täglich mitwachsend. Kein Fremd-Proxy — auch nicht der geprüfte und verfügbare Dukascopy-Nasdaq-CFD (siehe 9.1). |
| 3 | Spooling-Definition | **Nicht vorab festlegen.** Mehrere Kandidat-Kennzahlen werden mitgeschrieben, die Auswertung zeigt, welche mit gerichteter Expansion zusammenhängt — und meldet ehrlich, wenn keine es tut. |
| 4 | Zielereignis | **Zwei:** (a) gerichtete Expansion samt Startminute, (b) Level erreicht. |
| 5 | Fensterumfang | **Jedes Macro-Fenster des Handelstags**, nicht nur die Killzone-Macros. |
| 6 | Vollständigkeit | **Nur vollständig erfasste Fenster** gehen in die Statistik (siehe 4.2). |

---

## 3. Datenrealität (in dieser Session gemessen, nicht angenommen)

Diese Zahlen stammen aus direkter Messung über `raw/marktdaten/` und begründen mehrere
Designentscheidungen. Sie sind der Stand vom 2026-08-10 und veralten mit wachsendem Bestand.

### 3.1 Der Handelstag hat 23 Macro-Fenster, nicht 24

Die 1m-Exporte folgen der CME-Konvention: `MNQ 2026-07-09 1m.csv` enthält
**2026-07-08 18:00 → 2026-07-09 17:00**. Der Handelstag beginnt um 18:00 des Vorabends und läuft
über den Datumswechsel. Zwischen 17:00 und 18:00 liegt die Globex-Pause — das Fenster **17:50 gibt
es nicht**. Damit bleiben 23 Fenster: `18:50, 19:50, … 23:50, 00:50, … 16:50`.

### 3.2 Datenbestand (23 Dateien, Stand 2026-08-10)

- **19 volle Tage.** Vier Fragmente: `2026-07-08` (ab 00:09), `2026-08-03` (nur 11:19–16:18,
  300 Kerzen), `2026-08-05` (ab 00:09), `2026-08-07` (nur bis 10:25).
- **Kein Volumen.** Die TradingView-Exporte haben ausschließlich `time,open,high,low,close`.
  Jede volumenbasierte Kennzahl ist damit unmöglich — betrifft insbesondere die naheliegende
  Spooling-Definition "enge Kerzen bei steigendem Volumen".
- **Systematische Lücke am Datumswechsel:** an 15 von 19 vollen Tagen fehlen die Minuten
  **23:59–00:08**. Immer dieselben zehn Minuten. MNQ handelt dort durchgehend (Asia-Session),
  zehn tickfreie Minuten sind praktisch ausgeschlossen — das ist ein **TradingView-Exportartefakt**,
  kein Marktverhalten. Betrifft genau das Fenster 23:50–00:10.

### 3.3 Verwertbare Fenster bei strikter Vollständigkeit

Kriterium: 20 von 20 Minuten im Fenster **und** 10 von 10 Minuten im Vorlauf.

| | |
|---|---|
| Theoretisch möglich | 23 Tage × 23 Fenster = 529 |
| **Strikt vollständig** | **440** (83 %) |
| Pro Fenster | 18–22 Tage |
| **16:50** | **0** — das Fenster ragt über den Sessionschluss 17:00 hinaus |
| **23:50** | **1** — Exportartefakt aus 3.2 |
| **Nutzbar** | **21 Fenster, ~440 Zeilen, +21 pro Handelstag** |

---

## 4. Datenmodell

Eine Zeile = ein Macro-Fenster eines Handelstags. Ablage: `algo/results/macro_db.csv`
(versioniert, CSV statt SQLite — bei dieser Größe genügt pandas-Filterung, und CSV bleibt im Git
diffbar).

### 4.1 Spalten

**Identität** — `symbol`, `session_day` (Datum des Session-*Endes*, wie der Dateiname),
`window` (`09:50`), `weekday`, `session` (Asia / London / NY-AM / Lunch / NY-PM / Overnight).

**Vorgeschichte** — ausschließlich aus Bars mit `t < Fensterstart`.

*Spooling-Kandidaten (10 Minuten vor dem Fenster, alle preisbasiert):*
- `pre_range_rel` — Range der 10 Min ÷ **rollierendem Median der 12 vorangegangenen
  10-Minuten-Blöcke** (= 2 Stunden Rückschau). Bewusst *nicht* gegen den Tagesmedian normiert:
  der enthielte Bars nach dem Fenster und wäre damit Lookahead (siehe 4.3).
- `pre_wick_frac` — Dochtanteil an der Gesamtrange
- `pre_streak` — längste Serie gleichgerichteter Closes
- `pre_contraction` — schrumpfen die Kerzenranges monoton?

*Ereignisse (aus vorhandenen Detektoren in `tools/analyze_ohlc.py`, keine Neuimplementierung):*
- `sweep_age`, `sweep_dir` — Minuten seit dem letzten Liquidity-Sweep und dessen Richtung
- `mss_age`, `mss_dir` — dito für Market Structure Shift
- `displacement_age`
- `fvg_open_dist` — Abstand zum nächsten offenen Fair Value Gap

*Offene Level:* Abstand zu PDH/PDL, NDOG, NWOG, ORG, Session-Hoch/-Tief
(`ndog_gap`, `nwog_gap`, `org_gap`, `session_windows`, `untouched_levels`).

**Verlauf im Fenster** — `range`, `netto`, `dir` (identisch definiert wie in
`backtest_macro.py`), `direction`, `expansion` (Zielereignis a: `dir` ≥ Schwelle **und** `netto` ≥
Punkte-Schwelle, beide CLI-Parameter; Startwerte **`dir` ≥ 0,60** und **`netto` ≥ 30 Punkte**,
abgeleitet aus den Medianwerten in `backtest_macro.py`: Macro-Median `dir` 0,52 / `netto` 31,50 —
die Schwelle soll also etwas über dem Median liegen, damit "Expansion" nicht die Hälfte aller
Fenster umfasst), `levels_hit` (Zielereignis b: welche der *vor* dem Fenster
offenen Level wurden *im* Fenster berührt).

**Timing** — `start_min`: die Minute im Fenster mit dem Extrem **entgegen** der Netto-Richtung.
Läuft das Fenster netto aufwärts, ist es die Minute des Tiefs. Deterministisch, schwellenfrei, und
misst genau die Manipulation-vor-Expansion-Sequenz aus dem 09:50-Beispiel in
`wiki/concepts/ICT Macros & Leading Candles.md` (Fenster öffnet, läuft erst gegen die spätere
Richtung, schließt am Extrem).

### 4.2 Vollständigkeitsregel

Es werden **nur vollständige Fenster** geschrieben: 20/20 Minuten im Fenster, 10/10 im Vorlauf.
Unvollständige Fenster erscheinen **nicht** in der CSV, sondern in einer Ausschlussliste, die
`build` ausgibt und `stats` im Report wiederholt: Fenster, Tag, Grund, Anzahl. Damit verschwindet
nichts stillschweigend (`CLAUDE.md`: Marktdaten wie Gold behandeln), ohne dass jede Auswertung
einen Qualitätsfilter mitschleppen muss.

Fragmenttage werden nicht pauschal verworfen — sie liefern gültige Zeilen für die Stunden, die
sie vollständig abdecken.

### 4.3 Kein Lookahead

Jede Vorgeschichte-Spalte sieht ausschließlich `bars[t < Fensterstart]`, jede Verlaufsspalte
ausschließlich `bars[Fensterstart ≤ t < Fensterende]`. Der Selfcheck prüft das explizit: er baut
einen synthetischen Tag, in dem nach dem Fenster ein extremer Ausschlag liegt, und stellt sicher,
dass keine Vorgeschichte-Spalte sich dadurch ändert.

---

## 5. Modul

`algo/macro_db.py` mit drei Subcommands plus Selfcheck nach Vault-Konvention:

```
python algo/macro_db.py build       # CSV neu bauen, Ausschlussliste ausgeben
python algo/macro_db.py stats [...] # Auswertung mit Bedingungsfiltern
python algo/macro_db.py plot        # drei PNGs + Wiki-Seite
python algo/macro_db.py --selfcheck
```

`build` rechnet **immer alles neu**. Bei 440 Zeilen dauert das Sekunden; eine Inkrementell-Logik
wäre Code für ein Problem, das nicht existiert.

**Fenster relativ zur Session, nicht zum Kalendertag.** Das ist der Punkt, an dem
`backtest_macro.py` heute falsch liegt (siehe 9.2) — die Datenbank darf den Fehler nicht erben.
Der Selfcheck deckt ihn ab: die Fensterlogik muss für einen Handelstag genau **23** Fenster
erzeugen, beginnend bei 18:50 des Vorabends. Nicht zu verwechseln mit den **21** nutzbaren aus
3.3 — 23 ist die Zahl der existierenden Fenster, 21 das, was nach der Vollständigkeitsregel (4.2)
mit den heutigen Daten übrig bleibt.

---

## 6. Statistik-Schicht

Vier Regeln, die das Script in der **Ausgabe erzwingt** — nicht als Stilhinweis im SKILL.md:

1. **Keine Quote ohne Intervall.** Wilson-Score-Intervall (Formel aus der Standardbibliothek,
   keine neue Abhängigkeit). Bei kleinem n deutlich ehrlicher als das Normal-Intervall.
2. **Keine Quote ohne Basisrate.** `P(Ereignis | Bedingung)` steht immer neben `P(Ereignis)`
   gesamt. Überlappen die Intervalle, lautet die Ausgabe **"kein Unterschied nachweisbar"** —
   nicht "leicht erhöht".
3. **Unter n = 20 keine Prozentzahl.** Ausgabe ist dann `n=7 — zu wenig`. Das ist in den ersten
   Monaten die häufigste ehrliche Antwort und muss der einfachste Pfad sein.
4. **Mehrfachvergleiche werden mitgezählt.** Bei 21 Fenstern × mehreren Bedingungen produziert
   reines Rauschen zuverlässig "signifikante" Treffer. Der Report nennt die Zahl der gerechneten
   Vergleiche und markiert p-Werte, die eine Bonferroni-Korrektur nicht überstehen.

**Pflicht-Vorbehalt in jedem Report:** Fenster desselben Handelstags sind nicht unabhängig, p-Werte
sind dadurch optimistisch. Derselbe Vorbehalt steht bereits in `backtest_macro.py` und gilt hier
unverändert.

**Spooling-Auswertung:** Die vier Kandidaten aus 4.1 werden gegen `expansion` und `dir` geprüft
(Rangkorrelation, plus Quotenvergleich oberstes vs. unterstes Quartil). Der Report benennt, welcher
Kandidat trägt — und stellt ausdrücklich fest, wenn keiner es tut. Ein Nullbefund ist hier ein
Ergebnis, kein Fehlschlag.

---

## 7. Diagramme

matplotlib → PNG, eingebettet in `wiki/synthesis/Macro-Datenbank (laufend).md`:

1. **Expansionsquote je Fenster** — Balken mit Wilson-Fehlerbalken, Basisrate als waagerechte
   Linie. Dass sich die meisten Balken überlappen werden, ist die Kernaussage, nicht ein Makel.
2. **Timing-Histogramm** der `start_min` (Minute 0–19) über alle Fenster. Die "wann"-Frage.
3. **Level-Trefferquote** je Level-Typ (PDH/PDL, NDOG, NWOG, ORG, Session-Extrem), mit
   Intervallen.

Die Wiki-Seite trägt `(laufend)` im Namen und wird bei jedem `plot`-Lauf überschrieben, nach der
Konvention der übrigen Auswertungsseiten.

---

## 8. Der Skill

`.claude/skills/macro-db/SKILL.md`, reines Markdown, kein eigener Code.

- **Auslöser:** Fragen nach Macro-Wahrscheinlichkeiten — "wie oft", "wann passiert X", "was war
  vor dem Macro", "spoolt es vorher", Fragen nach einem konkreten Fenster oder einer Bedingung.
- **Ablauf:** `build` bei Bedarf, dann `stats` mit den passenden Filtern, Antwort aus dem Report.
- **Antwortdisziplin:** n immer nennen. Intervall statt Punktschätzung. Basisrate danebenstellen.
  Bei zu kleinem n verweigern statt schätzen. Ungefragt mitliefern: die 23:50-Lücke, die
  Nicht-Unabhängigkeit der Fenster, die aktuelle Stichprobengröße.

Die Trennung ist bewusst: Das Script rechnet reproduzierbar, der Skill legt fest, **wie geantwortet
wird**. Ohne diese Schicht wäre das Ganze nur ein weiteres `backtest_*.py`.

---

## 9. Nebenbefunde aus dieser Session

### 9.1 Dukascopy liefert kostenlose Nasdaq-Historie (geprüft, bewusst nicht genutzt)

Direkter Ladetest gegen `datafeed.dukascopy.com`: **`USATECHIDXUSD`** (Nasdaq-100-CFD) liefert
Tickdaten für 2026-08-07 (168 KB/Stunde) **und** für 2012-06-12 (4,4 KB/Stunde).
`USA500IDXUSD` ebenso. Falsche Symbole antworten sauber mit HTTP 404, die übrigen Fehlschläge im
Test waren Rate-Limit-Timeouts. `algo/fetch_dukascopy.py` könnte die Daten ohne Umbau laden.

Das wären ~3.500 Handelstage statt 19. **Bewusst verworfen** (Entscheidung 2): CFD ≠ Futures,
Broker-Volumen ist wertlos, die frühen Jahre sind dünn (4 KB gegen 168 KB pro Stunde), und die
Proxy-Annahme müsste selbst erst validiert werden. Notiert für den Fall, dass die Stichprobe
später zum Engpass wird.

Kostenpflichtige Alternativen mit echter Futures-Historie: FirstRateData (19 Jahre NQ/MNQ, ~$100/a),
Barchart Premier, Kibot, Portara. Kostenlos bei FirstRateData nur 2-Wochen-Samples bzw. 1 Jahr für
einzelne Datasets (QQQ, NDX) — RTH-only, damit für die Nacht-Macros unbrauchbar.

### 9.2 Sessionfehler in `backtest_macro.py` (Folgeaufgabe, nicht Teil dieser Spec)

`blocks(day)` startet bei **00:10 des Kalendertags** und deckt damit nur 00:00–17:00 ab. Die
Fenster **18:50 bis 23:50 fehlen systematisch** — 6 der 23 Macro-Fenster jedes Handelstags, also
die gesamte Abend- und frühe Asia-Session.

Betroffen sind die veröffentlichten Zahlen in `wiki/concepts/ICT Macros & Leading Candles.md`
(351 Macro-Blöcke, 1091 Blöcke, die drei Mann-Whitney-p-Werte, die Median-Rang-Aussage zu
09:50–10:10). Sie sind nicht falsch gerechnet, beruhen aber auf einem verkürzten Tag.

Nach `CLAUDE.md` ("Korrektheit vor Features", Bugs direkt beheben) ist das mit Vorrang zu
korrigieren — **vor** dem Bau dieser Datenbank, da beide dieselbe Fensterlogik brauchen und die
Datenbank sie sonst dupliziert. Die Wiki-Zahlen sind danach neu zu erzeugen.

### 9.3 Mitternachtslücke schließbar

Die Lücke 23:59–00:08 aus 3.2 ließe sich mit `algo/fetch_yfinance.py` (MNQ=F, 1m, ~30 Tage
rückwärts) auffüllen. Damit würde Fenster 23:50 nutzbar und der Bestand stiege um ~21 Zeilen.
Notiert als eigener Schritt, nicht Teil dieser Spec.

---

## 10. Ausdrücklich nicht enthalten

- **ES als zweites Symbol** (18 1m-Tage vorhanden). ES- und MNQ-Fenster derselben Uhrzeit sind
  hochkorreliert — das verdoppelt die Zeilenzahl, ohne die Aussagekraft zu verdoppeln, und täuscht
  ein größeres n vor.
- **5m-Daten** (45 Tage). Vier Kerzen pro Fenster: `start_min` wäre nicht messbar, die
  Spooling-Kandidaten ebenso wenig.
- **Live-Betrieb.** Der Skill ist Nachschlagewerk. Eine Live-Variante ("nächstes Macro in 8 Min,
  Vorbedingungen erfüllt") kann später auf derselben Datenbank aufsetzen.
- **Handelsregeln.** Die Datenbank liefert Kennzahlen, keine Entries. Ableitungen davon gehören
  in `algo/rules.py` und durchlaufen die Validierung nach Roadmap-Stufe 3.
- **Inkrementelles Bauen, SQLite, Dashboard-Optik.** Alle drei sind Lösungen für Probleme, die bei
  440 Zeilen nicht existieren.

---

## 11. Bekannte Grenzen

1. **Die Stichprobe trägt noch nicht.** Bei ~21 Tagen pro Fenster hat eine Quote von 62 % ein
   Wilson-Intervall von etwa [41 %, 79 %]. Fragen auf **Fenster-Ebene** sind auf Monate hinaus
   nicht belastbar. Fragen auf **Bedingungs-Ebene über alle Fenster** (geschätzt 100–150 Fälle mit
   Sweep davor) werden früher aussagekräftig. Der Skill muss diesen Unterschied benennen, statt
   beide gleich zu behandeln.
2. **Fenster desselben Tages sind nicht unabhängig.** Alle p-Werte sind dadurch optimistisch.
3. **Spooling kann sich als Nullbefund erweisen.** Vier preisbasierte Kandidaten, ohne Volumen.
   Trägt keiner, ist das das Ergebnis — und die Hypothese in
   `wiki/concepts/ICT Macros & Leading Candles.md` ist entsprechend zu korrigieren.
4. **Ein Symbol, ein Markt.** Kein Übertrag auf andere Instrumente behauptet.
