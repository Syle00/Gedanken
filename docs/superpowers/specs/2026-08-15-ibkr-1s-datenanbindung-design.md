# IBKR 1s-Datenanbindung für NQ und ES — Design

**Datum:** 2026-08-15
**Status:** entworfen, nicht implementiert
**Vorgänger:** `raw/algo-pruefung/IBKR 1s-Datenanbindung — Übergabestand 2026-08-15.md`
(wird nach Umsetzung gelöscht, sein Inhalt geht in `algo/PLAN.md` und `algo/README.md` auf)

---

## 1. Ziel

Sekundengenaue OHLC-Daten für **NQ** (E-mini Nasdaq-100) und **ES** (E-mini S&P 500)
autonom über die Interactive-Brokers-TWS/Gateway-API beschaffen, im bestehenden
`raw/marktdaten/`-Baum ablegen und über `algo/marktdaten.py::bars()` für Backtests
verfügbar machen.

**Abgrenzung.** Dieses Design deckt ausschließlich den *Daten*pfad ab. Die
Order-Ausführung (`algo/broker_ibkr.py`, Roadmap-Punkt 4) bleibt unberührt, ebenso die
Reihenfolge Regel-Schicht → Validierung → Adapter → Paper-Trading → Live. Die Sperre
gegen echtes Kapital ohne gesonderte Nutzerfreigabe wird durch dieses Design nicht
gelockert, sondern technisch verstärkt (§9).

---

## 2. Getroffene Entscheidungen

| # | Entscheidung | Begründung | Verworfen |
|---|---|---|---|
| E1 | **IBKR** als Quelle | ~$1,55/Monat, dieselbe Quelle wie die spätere Ausführung, keine Quellen-Drift zwischen Backtest und Live | Databento (~$199/Mon., zweite Quelle); TradingView-Automatisierung (ToS-Verstoß + nur Rolling Window); yfinance (schon auf 1m tick-unsicher) |
| E2 | **NQ und ES**, kein MNQ | Beide vom gebuchten CME-L1-Paket abgedeckt; deutlich liquider als MNQ, also weniger handelslose Sekunden; Bestand an Vergleichsdaten größer (6.927 ES-, 6.559 NQ- gegen 2.640 MNQ-Dateien). MNQ ist derselbe Index mit derselben Tickgröße — sein Wegfall kostet keine Information | MNQ (Ausgangsplan) |
| E3 | **Punktwert NQ = $20, ES = $50** | Daten und gehandeltes Instrument sind dasselbe. Erfordert Nachzug von `CLAUDE.md` Layer 0 (§12) | Signale aus NQ, P&L in MNQ ($2) |
| E4 | **`whatToShow="TRADES"`**, Lücken bleiben leer | Echte gehandelte Preise, kein erfundener Datenpunkt. Handelslose Sekunden fehlen schlicht | Forward-Fill mit Marker-Spalte; MIDPOINT (kein Trade-Preis, kein Volumen, systematischer Versatz) |
| E5 | **Front-Monat-Einzelkontrakt** | Exakt das gehandelte Instrument, keine geschätzte Roll-Konvention. Innerhalb eines Handelstags ohnehin genau ein Kontrakt | IBKR-CONTFUT (andere Verkettung als TradingViews `1!`, und gehandelt wird trotzdem der Einzelkontrakt) |
| E6 | **Tages-Parquet im bestehenden Ordner**, versioniert | Gleiche Struktur wie heute; jede Datei wird genau einmal geschrieben, also git-freundlich; ~400–600 MB/Jahr statt ~1,7 GB als CSV | Eigener Baum `raw/marktdaten-1s/`; nur gitignorierter Cache (Totalverlust-Risiko wegen IBKRs 6-Monats-Grenze); CSV |
| E7 | **Kein Parquet-Cache-Layer** | Tagesdateien sind bereits Parquet, ein Backtest liest nur seinen Datumsbereich. Cache für ein ungemessenes Problem ist Vorratsbau | Analogon zu `build_parquet.py` (Empfehlung des Übergabestands) |
| E8 | **Ein Modul `algo/fetch_ibkr.py`** | `fetch_yfinance.py` macht dieselben Dinge in 190 Zeilen. `ib_async` verbindet in drei Zeilen — eine Client-Schicht für einen künftigen zweiten Nutzer ist Vorratsbau | Geschichtet (`ibkr_client.py` + Fetcher + Cache-Builder); Roh-Ablage getrennt |
| E9 | **Verbindung über Paper-Gateway (Port 4002), `readonly=True`** | Der Datenpfad hat konstruktionsbedingt keinen Weg zu echtem Kapital | Live-Port 4001 (nur als dokumentierte Rückfallebene, §9) |
| E10 | **Täglicher Windows-Task**, IB Gateway + IBC | Kein Fremdrechner, keine laufenden Kosten; Nachlad holt selbst eine Woche Rückstand in Minuten auf | Nur manuell (Lückenrisiko wegen 6-Monats-Grenze); Dauerlauf; VPS |
| E11 | **`ib_async`**, nicht `ib_insync` | `ib_insync` wird nicht mehr gepflegt | — |

---

## 3. Modul `algo/fetch_ibkr.py`

Drei Betriebsarten:

```
python algo/fetch_ibkr.py --verify [--symbol NQ]      # ein 30-Min-Fenster, schreibt nichts
python algo/fetch_ibkr.py --backfill 2026-02-17 2026-08-14
python algo/fetch_ibkr.py                             # Nachlad: letzter Registereintrag bis gestern
```

Default-Symbole: `NQ,ES` (über `--symbol` einschränkbar).

### 3.1 Ablauf je Handelstag und Symbol

1. **Verbinden.** `IB().connect("127.0.0.1", 4002, clientId=…, readonly=True)`.
2. **Kontrakt bestimmen** (§3.2).
3. **Tag zerlegen** in 46 Fenster à 1800 s: 18:00 NY des Vortages bis 17:00 NY.
   Tagesgrenze über `trading_day()` — Logik unverändert aus `fetch_yfinance.py`
   übernommen, damit die Zuordnung mit dem Bestand identisch ist.
4. **Bereits abgedeckte Fenster überspringen** (Register, §5).
5. **Requests** mit Pacing-Limiter (§3.3):
   `reqHistoricalData(contract, endDateTime=<UTC>, durationStr="1800 S",
   barSizeSetting="1 secs", whatToShow="TRADES", useRTH=False, formatDate=2)`.
   `useRTH=False` ist zwingend — sonst fällt die gesamte ETH-Session weg.
   `formatDate=2` liefert UNIX-Sekunden in UTC, damit entfällt jede
   Zeitzonen-Umrechnung und mit ihr der schädlichste Fehlertyp dieses Projekts.
6. **Zusammensetzen**: nach `time` sortieren, Duplikate an den Fensterrändern
   verwerfen (`keep="first"`).
7. **Gate**: `pruefe_kerzen(rows, symbol, dateiname)`. Wirft es `OHLCDefekt`,
   entsteht **keine** Datei, es werden **keine** Registerzeilen geschrieben, und der
   Fehler wird gemeldet. Weiche Hinweise werden ausgegeben, blockieren aber nicht.
8. **Schreiben** (§4), niemals überschreiben — `dest.exists()`-Regel wie `write_day()`.
9. **Register anhängen**: eine Zeile je erfolgreich geholtem Fenster.

### 3.2 Front-Monat-Auflösung

NQ und ES laufen quartalsweise: H (März), M (Juni), U (September), Z (Dezember).

- **Verfall** = 3. Freitag des Verfallsmonats.
- **Roll** = Verfall − 8 Tage (2. Donnerstag).
- **Front-Monat für Datum `d`** = erster Quartalskontrakt, dessen Roll-Termin nach `d` liegt.

Deterministisch, netzfrei berechenbar, im Selbstcheck gegen bekannte Termine geprüft.
Für den Backfill über bereits verfallene Kontrakte (NQH2026, NQM2026, ESH2026, ESM2026)
setzt der Request `includeExpired=True`. **Ob IBKR 1s-Bars für verfallene Kontrakte
liefert, ist ungeprüft** — Prüfpunkt 2 der Verifikation (§6), siehe Risiko R1.

### 3.3 Pacing-Limiter

IBKR-Grenzen: max. 60 Requests je 10 Minuten; max. 6 Requests für dieselbe
Contract/Exchange/TickType-Kombination binnen 2 s; keine identischen Requests binnen 15 s.

Umsetzung: eine `deque(maxlen=60)` der letzten Request-Zeitpunkte (`time.monotonic()`).
Vor jedem Request warten, bis der älteste Eintrag mehr als 600 s zurückliegt, mindestens
aber 0,5 s seit dem letzten Request (deckt die 6-je-2-s-Regel mit Reserve ab).

Kein nebenläufiger Betrieb — 60 Requests je 10 Minuten sind im Mittel einer alle
10 Sekunden, Parallelität brächte nichts.

**Fehlerbehandlung je Fenster:** bis zu 3 Versuche, zwischen den Versuchen mindestens 15 s
Abstand (Regel „keine identischen Requests binnen 15 s"). Danach wird das Fenster als
fehlgeschlagen gemeldet und übersprungen; es fehlt dann im Register und wird beim nächsten
Lauf automatisch erneut versucht.

### 3.4 Durchsatz

| Größe | Wert |
|---|---|
| Daten je Request | 30 Min |
| Pacing | 60 Requests / 10 Min |
| Effektiver Durchsatz | 30 h Daten je 10 Min Laufzeit |
| Ein ETH-Tag, ein Symbol | 46 Requests ≈ 8 Min |
| Ein ETH-Tag, NQ + ES | 92 Requests ≈ 16 Min |
| 6 Monate Backfill, beide Symbole | ~12.000 Requests ≈ **34 h**, einmalig, unterbrechbar |

---

## 4. Dateiformat und Ablage

```
raw/marktdaten/<JJJJ>/<MM>/<TT.MM.JJJJ>/NQ <JJJJ-MM-TT> 1s.parquet
raw/marktdaten/<JJJJ>/<MM>/<TT.MM.JJJJ>/ES <JJJJ-MM-TT> 1s.parquet
```

| Spalte | Typ | Anmerkung |
|---|---|---|
| `time` | int64 | UNIX-Sekunden, UTC — identisch zum bestehenden CSV-Schema |
| `open`, `high`, `low`, `close` | float64 | |
| `volume` | int64 | kommt bei TRADES kostenlos mit; auf 1s die einzige Möglichkeit, dünnen Handel von echter Bewegung zu unterscheiden |
| `contract` | string | z.B. `NQU2026`; ohne das ist über einen Roll hinweg nicht rekonstruierbar, woher ein Preissprung stammt. Dictionary-kodiert praktisch gratis |

Größenordnung: ~0,5–1 MB je Symbol und Handelstag, also ~400–600 MB/Jahr in der
Git-Historie. `.git` liegt bereits bei 1,9 GB — siehe Risiko R4.

---

## 5. Abdeckungs-Register

`raw/marktdaten/1s-abdeckung.csv`, versioniert, append-only:

```
symbol,von,bis,kontrakt,kerzen,geholt_am
NQ,1786752000,1786753800,NQU2026,1743,1786838400
```

`von`/`bis`/`geholt_am` als UNIX-Sekunden. Eine Zeile je erfolgreich geholtem
30-Minuten-Fenster, ~92 pro Handelstag für beide Symbole.

Löst drei Probleme mit einer Datei:

- **„Kein Trade" vs. „nicht geholt".** Ohne Register ist eine fehlende Sekunde im
  Archiv nicht interpretierbar. Das ist die direkte Folge von Entscheidung E4 und
  nicht optional.
- **Wiederaufnahme.** Bricht der 34-Stunden-Backfill ab, macht der nächste Lauf dort
  weiter. Ersetzt eine getrennte Roh-Zwischenablage zum Preis einer CSV-Zeile.
- **Zustandsloser Nachlad.** Der tägliche Lauf braucht keinen eigenen Zustandsspeicher.

---

## 6. Verifikation (`--verify`)

Ein einzelnes 30-Minuten-Fenster je Symbol, schreibt nichts. **Vor** dem Backfill
auszuführen — 34 Stunden auf einer ungeprüften Annahme sind teuer.

1. **Liefert IBKR 1s-Bars?** Bestätigt die Doku-Annahme.
2. **Liefert IBKR 1s auch für verfallene Kontrakte** (`includeExpired=True`)?
   Fällt das negativ aus, reicht der Backfill nur bis zum letzten Roll zurück statt
   sechs Monate — siehe R1.
3. **Zeitstempel**: 1s auf 1m aggregiert gegen einen manuellen TradingView-Export
   desselben Fensters. Kein Offset, keine DST-Verschiebung.
4. **Preise**: `pruefe_gegen_referenz(eigen, referenz, toleranz=0.01)`, ausschließlich
   O/H/L. Bei 0,25 Tickgröße heißt jede Abweichung über 0,01 faktisch „mindestens ein
   Tick daneben".
5. **Handelslose Sekunden** als Quote, getrennt nach Asia / London / NY. Pflichtkennzahl
   in jedem Report, nicht Fußnote.
6. **`pruefe_kerzen()` grün.**

Zusätzlich als Eigenkonsistenz-Check: 1s aggregiert gegen IBKRs eigene 1m-Bars desselben
Fensters. Prüft nicht den Feed, deckt aber jeden Aggregationsfehler auf eigener Seite
sofort auf.

### 6.1 Voraussetzung: Referenzdaten fehlen

Im Bestand existiert **keine vertrauenswürdige Referenz für NQ oder ES**. Die
`(2)`/`(3)`-Suffixe — laut `CLAUDE.md` das Erkennungsmerkmal manueller
TradingView-Exporte — gibt es nur bei MNQ (3 Dateien) und EURUSD (2). Der gesamte
NQ/ES-Bestand stammt aus `fetch_yfinance.py`, und yfinance wich am 2026-08-12 am
9:30-Open um 0,5 Punkte ab (`algo/PLAN.md`, 2026-08-13).

**Erforderlich vor Prüfpunkt 3/4:** je ein manueller TradingView-1m-Export für NQ und ES
eines beliebigen der letzten Handelstage, abgelegt in `raw/`, eingespielt per
`python algo/ingest_tvexport.py <datei> NQ --tf 1m`.

---

## 7. Anpassung am Nulltoleranz-Gate

`tools/analyze_ohlc.py::pruefe_kerzen()` zählt eine Kerze als degeneriert bei
`open == high and low == close and open != close`. Auf Tagesebene ist das ein
Feed-Defekt. **Auf 1s-Ebene ist es der normale Abwärts-Tick**: erster Trade der Sekunde
ist der höchste, letzter der tiefste. Bei `DEGEN_MAX_ANTEIL = 0.05` erzeugte jede
Tagesdatei eine Warnung — Rauschen, das echte Warnungen begräbt.

**Änderung:** Der Degeneriert-Block wird übersprungen, wenn der Median-Abstand der
Zeitstempel ≤ 5 s beträgt. Der Median wird für diesen Block ohnehin schon berechnet
(`taeglich`-Zweig), die Änderung umfasst rund drei Zeilen. Alles Übrige am Gate — NaN,
`high < low`, Open außerhalb der Range, nicht steigende Zeitstempel, Tick-Raster —
bleibt unverändert und gilt für 1s genauso.

Regressionstest nagelt beide Seiten der Schwelle fest: 1s-Daten mit hohem
Degeneriert-Anteil müssen durchgehen, Daily-Daten mit demselben Anteil weiterhin
`OHLCDefekt` auslösen.

---

## 8. Anbindung an `algo/marktdaten.py`

`_futures_bars()` globt heute `f"{symbol} * {tf}.csv"`. Ergänzung: für `tf == "1s"`
stattdessen `f"{symbol} * 1s.parquet"` lesen und in `Bar`-Objekte wandeln
(`pd.to_datetime(df.time, unit="s", utc=True).dt.tz_convert(NY)`).

**Bewusst nicht gebaut:** automatisches Resampling von 1s auf höhere Timeframes.
Aggregierte 1m/5m-Daten aus IBKR wären eine *zweite* Serie neben dem TradingView-Bestand,
kein Ersatz für ihn — anderer Feed, und TradingView revidiert nachträglich (7,7 % der
Kerzen laut `ingest_tvexport.py`). Für Daily/Weekly kommt hinzu: IBKR reicht nur 6 Monate
zurück, und der offizielle Daily-Close eines Futures ist der Settlement-Preis, nicht der
letzte Trade. Daily/Weekly bleiben TradingView-Exporte.

---

## 9. Betrieb und Sicherheit

**Laufzeitumgebung.** IB Gateway (nicht TWS — schlanke Java-App ohne Charts) startet mit
Windows. IBC übernimmt Login und den von IBKR erzwungenen Tages-Restart gegen Mitternacht
ET sowie das Samstags-Wartungsfenster. Danach ist nur noch einmal wöchentlich eine
Authentifizierung nötig (nach Sonntag 01:00 ET).

**Zeitplan.** Geplante Windows-Aufgabe täglich **17:30 NY** — nach Sessionschluss (17:00),
vor dem Gateway-Restart.

**Zwei Absicherungen trennen den Datenpfad hart vom Handel:**

1. `readonly=True` in der Verbindung — der Prozess kann konstruktionsbedingt keine Order
   absetzen.
2. **Port 4002 (Paper), nicht 4001 (Live).** IBKR spiegelt das Marktdaten-Abo ins
   Paper-Konto, sobald im Client Portal „Share real-time market data with paper account"
   gesetzt ist — **einmalig vom Nutzer zu setzen**. Ergebnis: selbst bei völligem
   Programmversagen existiert kein Pfad zu echtem Kapital.
   *Rückfallebene:* Ist die Spiegelung nicht aktivierbar, läuft der Fetcher auf Port 4001
   mit `readonly=True`. Das ist ausdrücklich die zweite Wahl und muss in `PLAN.md`
   vermerkt werden, falls es dazu kommt.

**Secrets.** IBC legt das Passwort im Klartext in seiner Konfiguration ab. Die Datei liegt
außerhalb des Repos (`%USERPROFILE%\ibc\`); zusätzlich wird `algo/ibc/` in `.gitignore`
eingetragen, um einen versehentlichen Kopiervorgang abzufangen. Damit greift das
Security-Gate aus `CLAUDE.md`: Secret-Scan ab sofort **wöchentlich** statt gelegentlich,
vor jedem Live-Übergang zwingend.

**60-Tage-Regel.** IBKR kündigt Marktdaten-Abos, wenn 60 Tage kein Login erfolgt ist.
Gateway-Logins zählen mit; der tägliche Task hält das Abo damit automatisch aktiv.

---

## 10. Slash-Command `/daten-1s`

Datei: `.claude/commands/daten-1s.md` (Muster wie `/algo-live-status`, `/tagesbericht`).
Manueller Auslöser, wenn der Nutzer Daten außerhalb des Zeitplans ziehen will.

**Argumente** (alle optional, Default = Nachlad):

| Aufruf | Wirkung |
|---|---|
| `/daten-1s` | Nachlad: letzter Registereintrag bis gestern, beide Symbole |
| `/daten-1s verify` | Einzelfenster-Verifikation, schreibt nichts |
| `/daten-1s NQ` | Nachlad, nur NQ |
| `/daten-1s backfill 2026-02-17 2026-08-14` | Backfill für den Zeitraum |

Kombinierbar: ein Symbolname schränkt jede Betriebsart ein
(`/daten-1s verify ES`, `/daten-1s backfill 2026-02-17 2026-08-14 NQ`). Ohne Symbolangabe
laufen immer beide.

**Ablauf des Commands:**

1. Erreichbarkeit von Port 4002 prüfen. Nicht erreichbar → melden, dass IB Gateway nicht
   läuft, und abbrechen statt in einen Timeout zu laufen.
2. `python algo/fetch_ibkr.py <args>` starten. Bei Backfill: Hintergrundlauf, weil die
   Laufzeit in Stunden liegt.
3. **Bericht** — nicht die Konsolenausgabe durchreichen, sondern verdichten:
   geholte Fenster je Symbol, geschriebene Tagesdateien, Kerzenzahl,
   **Quote handelsloser Sekunden je Session**, alle Hinweise aus `pruefe_kerzen()`,
   fehlgeschlagene Fenster, verbleibende Lücken laut Register.
4. **Kein `push.ps1`.** Veröffentlichen bleibt manuell (`CLAUDE.md`, Versionskontrolle).

---

## 11. Prüfbarkeit

`_demo()` in `fetch_ibkr.py`, netzfrei, im Muster der übrigen Module:

- Front-Monat-Auflösung gegen bekannte Roll-Termine (u.a. Tag vor und nach einem Roll).
- Pacing-Limiter mit simulierter Uhr: 61 Requests dürfen nicht in unter 600 s durchgehen.
- Zerlegung eines Handelstags: genau 46 Fenster, erstes beginnt 18:00 NY des Vortages,
  letztes endet 17:00 NY; ein Tag über einen DST-Wechsel bleibt korrekt.
- Register-Resume: nach simuliertem Abbruch werden nur die fehlenden Fenster angefragt.
- Parquet-Roundtrip: Schreiben und Zurücklesen erhält Typen und Zeitstempel.

Dazu der Regressionstest zu §7 in `analyze_ohlc.py`. Beide werden in
`algo/selfcheck.py` aufgenommen.

---

## 12. Lieferumfang

| # | Artefakt | Art |
|---|---|---|
| 1 | `algo/requirements.txt` — `ib_async` ergänzen | Änderung |
| 2 | `algo/fetch_ibkr.py` | neu |
| 3 | `tools/analyze_ohlc.py` — Degeneriert-Check bei ≤5 s Median überspringen (§7) | Änderung |
| 4 | `algo/marktdaten.py` — `1s`-Parquet-Zweig in `_futures_bars()` (§8) | Änderung |
| 5 | `algo/selfcheck.py` — beide neuen Selbstchecks aufnehmen | Änderung |
| 6 | `.claude/commands/daten-1s.md` (§10) | neu |
| 7 | `.gitignore` — `algo/ibc/` | Änderung |
| 8 | IBC-Konfiguration + Windows-Aufgabe (§9) | Einrichtung |
| 9 | `algo/README.md` — Modulabschnitt `fetch_ibkr.py` | Änderung |
| 10 | `algo/PLAN.md` — Log-Eintrag, Backlog aktualisieren | Änderung |
| 11 | `wiki/log.md` — Eintrag Typ `setup` | Änderung |
| 12 | `CLAUDE.md` — Layer 0 und „Domänenkontext: algo" von MNQ auf NQ/ES (§12.1) | Änderung |
| 13 | `raw/algo-pruefung/IBKR 1s-Datenanbindung — Übergabestand 2026-08-15.md` löschen | Löschung |

### 12.1 CLAUDE.md-Anpassung

Betroffen sind die Stellen, die MNQ als Zielinstrument festschreiben:

- **Layer 0**, Überschrift und erster Absatz: „einen Handelsalgorithmus für MNQ" →
  NQ und ES, mit Begründung (Datenqualität auf 1s, Punktwerte NQ $20 / ES $50).
- **Layer 1**, `raw/marktdaten/`-Beschreibung: 1s-Ebene erwähnen.
- **Roadmap Punkt 1**: IBKR ist ab jetzt die Intraday-Quelle, nicht mehr nur
  „perspektivischer Kandidat".
- **Domänenkontext: algo**: „MNQ-Backtesting" → NQ/ES; Punktwertliste bleibt inhaltlich
  korrekt (MNQ $2, NQ $20, ES $50).

Die Sperre gegen Live-Handel ohne gesonderte Freigabe (Roadmap 5) bleibt wortgleich.

### 12.2 Reihenfolge

1. Lieferpunkte 1–3, 5 (Modul + Gate-Anpassung + Selbstchecks), Selbstchecks grün.
2. Nutzer: TradingView-1m-Export NQ und ES (§6.1), Client-Portal-Haken für
   Paper-Datenspiegelung (§9).
3. IB Gateway + IBC einrichten (Lieferpunkt 8).
4. **`--verify` auf dem Windows-Rechner des Nutzers** — nicht in der Agenten-Sandbox,
   die hat keinen Netzzugriff auf die Gateway-Instanz.
5. Erst bei grünem Ergebnis: Backfill (34 h, unterbrechbar).
6. Lieferpunkte 4, 6, 7 (Anbindung, Command, gitignore).
7. Dokumentation 9–13.

---

## 13. Risiken

| # | Risiko | Wirkung | Umgang |
|---|---|---|---|
| R1 | IBKR liefert 1s nicht für verfallene Kontrakte | Backfill reicht nur bis zum letzten Roll statt 6 Monate | Prüfpunkt 2 der Verifikation, **vor** dem Backfill. Bei Fehlschlag: Databento-Frage (§E1) neu bewerten |
| R2 | Paper-Konto bekommt keine gespiegelten Marktdaten | Port 4002 liefert nichts | Rückfallebene Port 4001 mit `readonly=True`, dokumentiert in `PLAN.md` |
| R3 | Handelslose Sekunden höher als erwartet | 1s-Reihe für Asia-Session dünn | Quote ist Pflichtkennzahl (§6.5); bei Bedarf `reqHistoricalTicks` für präzisionskritische Levels nachrüsten |
| R4 | Git-Wachstum ~400–600 MB/Jahr bei bereits 1,9 GB `.git` | Repo wird unhandlich | Bewusst in Kauf genommen: IBKR hält nur 6 Monate vor, ein gitignorierter Cache wäre Totalverlust bei Datenschaden. Bei Bedarf später auf jährliche Archiv-Repos aufteilen |
| R5 | 60-Tage-Regel kündigt das Abo | Neubestellung nötig | Täglicher Task hält Logins aktiv |
| R6 | IBC speichert Credentials im Klartext | Secret-Leak | Config außerhalb des Repos, `.gitignore`-Eintrag, wöchentlicher Secret-Scan (§9) |

---

## 14. Bewusst nicht gebaut

- **Parquet-Cache-Ebene** analog `build_parquet.py` — Vorratsbau, siehe E7. Kommt, sobald
  ein Backtest-Lauf messbar hängt.
- **Resampling 1s → höhere Timeframes** — würde zwei Serien vermischen, siehe §8.
- **`algo/ibkr_client.py`** als eigene Verbindungsschicht — Abstraktion für einen
  einzigen künftigen Nutzer. Herausziehen ist ein 20-Zeilen-Handgriff, wenn
  `broker_ibkr.py` tatsächlich entsteht.
- **CONTFUT / MIDPOINT / Forward-Fill / MNQ parallel** — jeweils in §2 begründet verworfen.
- **`algo/broker_ibkr.py`** — Roadmap-Punkt 4, eigener Vorgang.
