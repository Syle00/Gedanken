# Marktdaten-Schicht — Design-Spec

- **Datum:** 2026-08-12
- **Status:** entworfen, nicht umgesetzt
- **Auslöser:** Jannes möchte vollständige 1m-Historie über Jahrzehnte, einen einheitlichen Zugang
  zu allen Datenquellen und einen manuell auslösbaren Skill, der die tagesaktuellen Daten für MNQ,
  Forex und DXY selbstständig nachzieht.
- **Vorgänger:** `2026-08-08-algo-zielbild-design.md` §4.3 (Datenhaltung) und §4.5 (zweistufige
  Datenbeschaffung). Diese Spec setzt den dort beschlossenen 1m-Vorrang erstmals in Code um.

---

## 1. Bestandsaufnahme (gemessen, nicht geschätzt)

Grundlage aller Entscheidungen unten. Erhoben am 2026-08-12 über `raw/marktdaten/`.

| Symbol | 1m | 1h | 1d | Zeitraum 1d |
|---|---|---|---|---|
| MNQ | **25** | 83 | 883 | — |
| ES | 35 | 83 | 252 | — |
| NQ | — | — | 211 | — |
| je Forex-Paar (10 Stück) | **33** | ~1.045 | 5.264–6.928 | ab 2000 |
| DXY | **0** | 0 | 0 | existiert nicht |

**Der zentrale Befund:** Tief ist ausschließlich der 1d-Bestand. Die 1m-Abdeckung von 25–35 Tagen
ist exakt das rollierende 30-Tage-Fenster von yfinance. Eine 1m-Historie über Jahrzehnte existiert
im Vault nicht — sie muss beschafft werden und ist nicht bloß aufzuräumen.

**Nebenbefunde derselben Erhebung:**

- **Mitternachtslücken bei MNQ.** 06.08.: `23:58 → 00:09` (11 Kerzen fehlen), 10.08.:
  `23:58 → 00:00`, 11.08.: `23:58 → 00:09`. Betroffen ist der **Midnight Opening Price** (00:00 NY),
  auf dem [[Midnight Opening Range]], STD-Projektionen und ORG-Auswertungen aufsetzen.
  Gegenprobe: EURUSD/GBPUSD/USDJPY zeigen an denselben Tagen **keine** Mitternachtslücke
  (1.380/1.408 Kerzen, vollständig). Der Effekt ist also MNQ-spezifisch und vermutlich echte
  Marktstille im dünn gehandelten Micro-Kontrakt — yfinance schreibt für Minuten ohne Trade keine
  Kerze. Deckt sich mit Jannes' eigener Notiz vom 10.08. („die Lücke war echt, kein Anzeigefehler").
- **Abgebrochener Download.** `MNQ 2026-08-07 1m.csv` hat 617 statt ~1.380 Kerzen und beginnt erst
  um 00:09 statt 18:00. Das ist kein Marktphänomen, sondern ein unvollständiger Abruf — und er ist
  nirgends als solcher gekennzeichnet.
- **Beide Fälle sehen in der Datei identisch aus.** Keine Datei trägt ihre Herkunft, ihren
  Vollständigkeitsstand oder den Grund einer fehlenden Kerze. Das ist das eigentliche Problem, das
  diese Spec löst.
- **Dukascopy antwortet mit HTTP 429** (geprüft 2026-08-12, ~28 h nach dem abgebrochenen Bulk-Lauf
  vom 11.08.). Der sequenzielle Downloader bräuchte rechnerisch ~40 h je Paar (24 Stunden-Requests
  × ~6.100 Tage × 1 s Pause), also ~400 h für zehn Paare — er erreicht sein Ziel nie.
- **Der TradingView-MCP-Server taugt nicht für CME-Index-Futures.** `futures_category_snapshot`
  lieferte für `equity_index` 1 von 6 angefragten Kontrakten (nur Nikkei); ES, NQ, RTY, YM, EMD
  fehlten, bei über 120 s Laufzeit. Das Fehlen wird nicht als Fehler gemeldet, sondern nur über
  `"returned": 1` — dieselbe Klasse stiller Lücke, die diese Spec verhindern soll. `yahoo_price`
  desselben Servers funktioniert, ist aber dieselbe Quelle wie `algo/fetch_yfinance.py` und damit
  kein Zugewinn.

---

## 2. Entscheidungen

| # | Entscheidung | Begründung |
|---|---|---|
| 1 | Tiefe 1m-Historie nur für **Forex**, MNQ bleibt beim laufend wachsenden Bestand | Für CME-Futures gibt es keine kostenlose 1m-Tiefhistorie. Deckt sich mit Zielbild §4.5: Strukturstatistik auf Fremdhistorie, pip-genaue Validierung später auf IBKR. |
| 2 | Tagesaktuelle Daten kommen aus **TradingView** | Jannes' Vertrauen in die Richtigkeit; es ist zudem der einzige Bestand im Vault, der je gegen eine unabhängige Quelle geprüft wurde. |
| 3 | Export nur noch als **1m**, alle höheren Zeiteinheiten werden daraus gerechnet | TradingView exportiert ein Chart und eine Zeiteinheit pro Vorgang. 12 Symbole × 6 Zeiteinheiten wären 72 Exporte täglich; mit 1m sind es 12. Setzt zugleich Zielbild §4.3 um. |
| 4 | **Herkunftsnachweis** statt Migration des Altbestands | Fehlende Manifest-Zeile bedeutet „Herkunft unbekannt". Kostet drei Zeilen je Schreiber statt eines Migrationsprojekts über ~76.000 Dateien. |
| 5 | Bestehende Zeiteinheiten-Dateien werden **nicht gelöscht** | Der Loader bevorzugt den aus 1m gerechneten Wert; die alte Datei bleibt als Gegenprobe liegen. Löschen ohne belegte Deckungsgleichheit wäre Vertrauen statt Beleg. |
| 6 | Der Torwächter **blockiert nicht** | Ein Backtest auf mangelhaften Daten wird nicht verhindert, aber der Bericht sagt es vorher. Ein blockierendes Gate wird erfahrungsgemäß umgangen. |
| 7 | Dukascopy und Tiefhistorie laufen **separat** | Ausdrücklicher Wunsch. Der 429-Block macht daraus ein eigenes Problem (Drosselung, Wiederaufnahme, ggf. HistData als Ersatzweg). |

---

## 3. Architektur

Vier Bausteine, drei davon klein. Alles baut auf Vorhandenem auf.

```
Export (TradingView, 1m)  ──┐
yfinance-Nachlad          ──┼──> sort_marktdaten.py ──> raw/marktdaten/<j>/<m>/<t>/
HistData / Dukascopy      ──┘                                    │
                                                                 v
                                              data_gate.py  (prüft, urteilt nie endgültig)
                                                                 │
                                     ┌───────────────────────────┼───────────────────┐
                                     v                           v                   v
                        marktdaten_manifest.jsonl        data_gate.json         Klartextbericht
                                     ^
                                     │  liest Herkunft
                        backtest_common.load_range()  ──> alle Auswertungsskripte
```

### 3.1 `algo/data_gate.py` — der Torwächter

Prüft einen Tagesbestand und meldet, was nicht stimmt. Sechs Prüfungen je Datei:

| Prüfung | Fängt |
|---|---|
| Zeitstempel streng monoton, keine Dubletten | Resampling- und Zeitzonenfehler |
| Lückenliste (> 1 Kerze Abstand, ausgegeben in NY-Zeit) | fehlende Minuten wie die 00:00-Lücke |
| Kerzenzahl gegen Sollwert des Marktprofils | abgebrochene Downloads wie den 07.08. (617 statt ~1.380) |
| OHLC-Plausibilität: `h ≥ max(o,c)`, `l ≤ min(o,c)`, `h ≥ l`, kein Preis ≤ 0 | verstümmelte oder falsch geparste Zeilen |
| **Tick-Raster**: MNQ/NQ/ES nur Vielfache von 0,25 | krumme Preise aus Resampling oder falscher Quelle |
| **Querprobe 1m → 5m/15m/1h** desselben Tages | „Zeit vor Preis"-Drift zwischen Zeiteinheiten |

Die Querprobe ist die wertvollste: Liegen 1m und eine höhere Zeiteinheit für denselben Tag vor,
muss die aus 1m gerechnete Kerze der gespeicherten entsprechen. Tut sie es nicht, laufen zwei
Zeiteinheiten desselben Tages auseinander — der von `CLAUDE.md` als schädlichster benannte
Fehlertyp. Bisher prüft das nichts.

**Einstufung der Funde:**

- `fehler` — Zeitfolge kaputt, Tick-Raster verletzt, Zeiteinheiten widersprechen sich
- `warnung` — Lücke ohne Bestätigung, unvollständiger Tag, Kerzenzahl unter Soll
- `info` — Herkunft unbekannt (kein Manifest-Eintrag)

**Ausgabe:** `algo/results/data_gate.json` (maschinenlesbar, nach bestehender
`backtest_common.write_result()`-Konvention) plus Klartextbericht auf der Konsole.

### 3.2 `algo/results/marktdaten_manifest.jsonl` — der Herkunftsnachweis

Append-only, eine Zeile je Schreibvorgang:

```json
{"symbol": "MNQ", "tag": "2026-08-12", "tf": ["1m"], "quelle": "tradingview",
 "kerzen": 1380, "luecken": [], "status": "bestaetigt", "geschrieben": "2026-08-12T22:14:03Z"}
```

`quelle` ist eines von `tradingview`, `yfinance`, `histdata`, `dukascopy`, `1d-original`.
`status` ist `bestaetigt` (TradingView) oder `unbestaetigt` (alles andere).

**Kein Nachtragen für den Altbestand.** Eine fehlende Zeile bedeutet „Herkunft unbekannt", und der
Bericht sagt das so. Das erspart eine Migration über ~76.000 Dateien, deren Herkunft ohnehin nicht
mehr rekonstruierbar wäre.

**Vorrangregel bei Konflikt:** TradingView überschreibt yfinance für denselben Tag und dieselbe
Zeiteinheit; die Abweichung wird ins Manifest und in den Bericht geschrieben statt verschluckt.
Umgekehrt nie — `fetch_yfinance.py` überschreibt weiterhin grundsätzlich nicht.

### 3.3 1m-Vorrang und Resampling

**Regel:** Liegt für einen Tag 1m vor, ist es die einzige Wahrheit; 5m/15m/1h/4h/1d werden daraus
gerechnet. Nur wo kein 1m existiert, gilt die gespeicherte Datei.

Das betrifft den Bestand ungleich: Die 1m-Basis reicht ~33 Tage zurück, die Tiefhistorie ab 2000
ist reines 1d. Diese alten Tageskerzen bleiben gültige Quelle für sich und werden im Manifest als
`quelle: 1d-original` geführt — nie als abgeleitet, damit nie der Eindruck entsteht, sie stammten
aus Minutendaten.

**Kerzengrenzen richten sich am Sessionstart aus, nicht an Mitternacht UTC:** 18:00 NY für Futures,
17:00 NY für Devisen. `fetch_yfinance.py` resampled 4h heute naiv ab Tagesbeginn (dokumentiert als
`ponytail:`-Notiz im Code) — das ergibt andere 4h-Kerzen als jeder Chart. Mit diesem Umbau fällt
der Fehler weg.

Die Resampling-Funktion bleibt **Standardbibliothek** (Bucketing über Epoch-Sekunden mit
Session-Anker), wie `tools/analyze_ohlc.py` selbst — kein pandas im Kernpfad.

### 3.4 `backtest_common.load_range(symbol, tf, von, bis)`

Der einheitliche Zugang. Löst intern auf: 1m vorhanden → daraus rechnen; sonst gespeicherte Datei.
`find_1d_days()` bleibt als dünne Hülle bestehen, damit die rund 30 vorhandenen
Auswertungsskripte unverändert weiterlaufen.

### 3.5 Skill `/marktdaten`

Manuell ausgelöst, ein Durchlauf:

1. **Holen** — falls die Browser-Werkzeuge verbunden sind: MNQ, die Forex-Paare und DXY je als 1m
   aus TradingView exportieren. Sonst oder bei einem gescheiterten Chart: benennen, welches, und
   mit dem Rest weitermachen — kein Abbruch.
2. **Einräumen** — `tools/sort_marktdaten.py` sortiert flach Abgelegtes nach `<jahr>/<monat>/<tag>/`.
3. **Nachziehen** — Forex und MNQ per yfinance für Tage ohne TradingView-Datei, im Manifest als
   `unbestaetigt` geführt.
4. **Prüfen** — Torwächter über alle berührten Tage.
5. **Fortschreiben** — Manifest, `algo/PLAN.md`, `wiki/log.md`.
6. **Berichten** — welche Tage fehlen, welche sind unbestätigt, welche verdächtig.

---

## 4. Marktprofile und Sollwerte

| Profil | Handelstag | Soll-1m-Kerzen |
|---|---|---|
| Futures (MNQ/ES/NQ) | 18:00 NY Vortag → 17:00 NY, Pause 17–18 Uhr | 1.380 |
| Forex | 17:00 NY → 17:00 NY, durchgehend | 1.440 |
| DXY | **unbekannt** | erst messen, dann eintragen |

Bei DXY wird nicht geraten. Der Torwächter meldet die ersten Tage nur Lücken ohne Sollwert-Urteil;
sobald mehrere vollständige Tage vorliegen, wird das Profil daraus abgeleitet und hier eingetragen.

Feiertage und verkürzte Handelstage senken den Sollwert. Erste Ausbaustufe: Unterschreitung ist
`warnung`, nicht `fehler` — ein Feiertagskalender kommt erst, wenn die Warnungen zeigen, dass er
gebraucht wird.

---

## 5. Harte Regeln

- **Fehlende Kerzen werden nie aufgefüllt.** Kein Interpolieren, kein Vorwärtsfüllen. Eine
  erfundene Kerze ist im Backtest ein erfundener Trade. Der Torwächter meldet Lücken, er repariert
  sie nicht.
- **Der Torwächter blockiert nicht**, er stuft ein (siehe 3.1).
- **Nichts wird gelöscht** — weder alte Zeiteinheiten-Dateien noch vermeintlich überholte Exporte.

---

## 6. Ungeprüfte Annahmen

Alles hier ist **nicht verifiziert** und muss vor der Umsetzung geprüft werden. Bewusst als eigener
Abschnitt geführt, damit keine Annahme still zur Tatsache wird.

1. **Browsersteuerung über Brave.** Die Claude-Erweiterung ist installiert, war in dieser Sitzung
   aber nicht freigeschaltet (`/chrome`). Ob sie in Brave läuft, ist offen — Brave ist
   Chromium-basiert und nimmt Erweiterungen aus dem Chrome Web Store an, getestet wurde es hier
   nicht. **Rückfallebene ist fest eingeplant:** Jannes exportiert von Hand, der Skill macht den
   Rest. Der Browserweg ist Bequemlichkeit, nicht Grundlage.
2. **TradingViews Exportgrenzen.** Wie viele 1m-Kerzen ein Export liefert, hängt vom Tarif und den
   im Chart geladenen Balken ab. Ob ein voller Handelstag in einem Vorgang herauskommt, ist zu
   messen, bevor der Sollwert von 1.380 als Maßstab taugt.
3. **DXY-Handelszeiten** (siehe Abschnitt 4).
4. **Ursache der MNQ-Mitternachtslücken.** Die Gegenprobe gegen Forex legt echte Marktstille nahe,
   beweist sie aber nicht. Ein TradingView-Export desselben Tages entscheidet es — und ist damit
   der erste echte Nutzen des Herkunftsnachweises.

---

## 7. Prüfbarkeit

`data_gate.py` bekommt einen `demo()`-Selbstcheck nach bestehender Vault-Konvention (siehe
`backtest_common.demo()`) mit synthetischen Kerzen:

- eine Lücke → muss als `warnung` erscheinen
- ein krummer Tick (z.B. 29.708,80 bei MNQ) → muss als `fehler` erscheinen
- ein Widerspruch zwischen 1m und gespeicherter 5m-Datei → muss als `fehler` erscheinen
- ein vollständiger, sauberer Tag → darf **nichts** melden (Gegenprobe gegen Fehlalarme)

Eingehängt in `algo/selfcheck.py`.

---

## 8. Nicht in dieser Spec

- Dukascopy-Wiederaufnahme, Drosselung, HistData-Massenimport, überhaupt jede Tiefhistorie
  (eigener Schritt, ausdrücklicher Wunsch)
- IBKR-Anbindung
- Löschen bestehender Zeiteinheiten-Dateien
- Nachtragen der Herkunft für den Altbestand
- Der TradingView-MCP-Server — nach Messung für CME-Index-Futures unbrauchbar, wird nicht in die
  Pipeline genommen

---

## 9. Offene Punkte

1. Browserweg testen, sobald `/chrome` freigeschaltet ist (Abschnitt 6.1). Ergebnis hier eintragen.
2. DXY-Profil messen und in Abschnitt 4 eintragen.
3. Nach den ersten Läufen prüfen, ob die Querprobe 1m→5m auf dem Altbestand systematisch abweicht.
   Falls ja, ist das ein eigener Befund mit Wirkung auf alle bisherigen Backtest-Zahlen und gehört
   nach `algo/PLAN.md`.
