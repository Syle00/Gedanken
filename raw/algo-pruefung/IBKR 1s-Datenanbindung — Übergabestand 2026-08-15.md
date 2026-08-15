# IBKR 1s-Datenanbindung — Übergabestand 2026-08-15

> **Zweck dieses Dokuments.** Vollständiger Wissensstand aus der Cowork-Session vom 2026-08-15
> zur Frage „wie bekomme ich autonom 1-Sekunden-Daten für MNQ". Geschrieben so, dass ein anderes
> LLM ohne den Chatverlauf auf gleichem Stand weiterbauen kann. Enthält Entscheidungen samt
> Begründung, verworfene Alternativen samt Grund, verifizierte Zahlen und die offenen Schritte.
>
> ⚠️ **Ablageort ist bewusst suboptimal.** Diese Datei hat keinen Rohquellen-Charakter und
> gehört nach `CLAUDE.md` eigentlich in `algo/` (als Abschnitt in `algo/PLAN.md` bzw.
> `algo/README.md`), nicht unter `raw/`. Sie liegt hier auf ausdrücklichen Nutzerwunsch.
> **Empfehlung an das nächste Modell:** Inhalte nach `algo/PLAN.md` (Log-Eintrag) und
> `algo/README.md` (Modul-Abschnitt) überführen und diese Datei danach löschen, statt sie als
> zweite Wahrheitsquelle neben `PLAN.md` weiterzupflegen.

---

## 1. Ausgangsfrage und Entscheidung

**Frage des Nutzers:** 1-Sekunden-Daten der Future-Börsen autonom beschaffen. Bisheriger Weg
(TradingView-Export von Hand, ggf. über Browser-Automatisierung) sollte durch etwas ersetzt
werden, das ohne manuelles Bestätigen von Downloads läuft.

**Entscheidung: Interactive Brokers (IBKR) TWS/Gateway-API.**
Zeitbereich: **volle ETH-Session (23h)**, nicht nur RTH — vom Nutzer explizit so gewählt, weil
Asia-/London-Killzones und NDOG/NWOG sonst wegfallen.

---

## 2. Verworfene Wege (mit Begründung — nicht erneut aufrollen)

### 2.1 TradingView automatisieren — abgelehnt, wird nicht gebaut

Zwei unabhängige Gründe:

1. **Nutzungsbedingungen.** TradingViews ToS verbieten automatisierte Datenextraktion
   (Scripts, Scraping, Bots, APIs) ausdrücklich und lizenzieren die Marktdaten **display-only**.
   Explizit ausgeschlossen sind: automatisierter Handel, Order-Generierung, algorithmische
   Entscheidungsfindung, Risk-Management-Programme — also genau Layer 0 dieses Repos.
   Durchgesetzt wird das über Account-Sperren.
   Quelle: <https://www.tradingview.com/policies/>
2. **Technisch ohnehin Sackgasse.** TradingView hält für Sekunden-Auflösung nur eine sehr kurze
   Historie vor. Selbst perfekt automatisiert entstünde kein wachsendes Archiv, sondern ein
   Rolling Window von wenigen Tagen.

**Folge für das nächste Modell:** Keinen TradingView-Auto-Export bauen, auch nicht auf
Nachfrage. Manuelle TradingView-Exporte bleiben dagegen wie bisher zulässig und sind die
**Referenzquelle für die Gegenprüfung** (siehe Abschnitt 6).

### 2.2 Databento — zurückgestellt, nicht verworfen

`GLBX.MDP3` (CME Globex MDP 3.0), Python-API, Schema `ohlcv-1s` oder gleich MBO/Tick, Historie
viele Jahre zurück, für Non-Display/algorithmischen Einsatz lizenzierbar.

- CME Standard aktuell ~**$199/Monat** (Stand 2026-06-22: $179 für Bestandskunden 12 Monate,
  danach $199). Usage-based für den historischen Teil zusätzlich möglich.
- Usage-based Pricing für CME **Live**-Daten wurde zum 2025-04-16 eingestellt.

**Warum zurückgestellt:** ~130× teurer als IBKR bei einem Vorteil, der aktuell nicht gebraucht
wird (tiefe Historie). Zweite Datenquelle bedeutet außerdem Quellen-Drift zwischen Backtest und
Live-Ausführung — genau das, wovor `CLAUDE.md` Roadmap-Punkt 1 warnt.

**Wann Databento doch:** sobald eine Regel nachweislich **mehr als 6 Monate** 1s-Historie zur
Validierung braucht (IBKR-Hartgrenze, siehe 4.2). Dann ist Databento der einzige Weg.

> **Hinweis:** Unter `raw/preview.csv` liegt bereits eine **Databento-Preview-Datei**
> (Spalten `ts_event,rtype,publisher_id,instrument_id,open,high,low,close,volume,symbol`,
> 2 Datenzeilen, Symbol `ESZ2`, 2022-01-03). Der Nutzer hat Databento also schon selbst
> angesehen. Siehe Abschnitt 8 (lose Dateien).

### 2.3 Sonstige — nicht weiterverfolgt

| Quelle | Grund der Ablehnung |
|---|---|
| CME DataMine | teuer, kein Live-Pfad, wieder eigene Quelle |
| Polygon / dxFeed | dritte Quelle, erneute Drift, kein Vorteil gegenüber IBKR |
| yfinance | liefert schon auf Minutenebene Tick-Abweichungen (`algo/PLAN.md`, Eintrag 2026-08-13). Auf 1s völlig unbrauchbar. |

---

## 3. Abo-Stand beim Nutzer — **erledigt, verifiziert**

### 3.1 Gebuchtes Paket

**CME Real-Time (NP,L1) — USD 1,55/Monat.**
Beschreibung im Portal: *„Provides top of book data for futures traded on CME. Examples - ES, NQ
and HE contracts."*
Gebührenhinweis: *„A monthly USD 1.55 fee will be waived whenever the monthly commissions
generated in the account reaches USD 20.00."*

Der Nutzer hat das Abo am 2026-08-15 gebucht und mit „fertig" bestätigt.

### 3.2 Verwechslungsgefahr — dokumentiert, weil zweimal fast passiert

| Paket | Inhalt | Für MNQ? |
|---|---|---|
| **CME Real-Time (NP,L1)** — $1,55 | CME Globex: ES, NQ, **MNQ**, HE | ✅ richtig |
| CBOT Real-Time (NP,L1) — $1,55 | Chicago Board of Trade: YM, ZB, ZC | ❌ falsche Börse |
| COMEX Real-Time (NP,L1) — $1,55 | GC, SI, HG | ❌ |
| Cboe One (NP,L1) — $1,00 | US-**Aktien**börsen | ❌ (war versehentlich angehakt) |
| CME Real-Time (L2) — $12,10 | CME + Markttiefe | nur bei Order-Book-Bedarf |
| US Securities Snapshot and Futures Value Bundle — $10,00 | Aktien-Snapshots + CBOT/CME/COMEX/NYMEX Top-of-Book | Overkill |

**CBOT ≠ CME.** Beide gehören zur CME Group, sind aber getrennte Börsen mit getrennten
Datenpaketen. MNQ läuft über CME.

**Level 1 genügt.** `reqHistoricalData` mit `whatToShow=TRADES` (oder BID/ASK/MIDPOINT) braucht
kein Level 2. L2 liefert bei IBKR nur aggregierte Tiefe, nicht das echte MBO-Tape — dafür wäre
ohnehin Databento die richtige Quelle.

### 3.3 Voraussetzungen — geprüft und erfüllt

Aus dem Client Portal des Nutzers verifiziert (Screenshot 2026-08-15):

- **Market Data Subscriber Status: Non-Professional** ✅ → der $1,55-Tarif gilt tatsächlich.
  Bei Einstufung „Professional" wäre es ein Vielfaches.
- **Market Data API access is enabled**, Acknowledgement-Formular unterschrieben am
  **2025-09-06** ✅ → das ist eine **separate** Freigabe. Ohne sie liefert `reqHistoricalData`
  keine Daten, auch bei bezahltem Abo.
- Abrechnung erfolgt in **EUR**. Bestand vor der Buchung: EUR 1,30/Monat gesamt (OPRA $1,50,
  Rest Fee Waived). Nach CME-Zubuchung grob EUR 2,60–2,80/Monat.

### 3.4 Navigationspfad im Client Portal (war schwer zu finden)

**Settings → Trading Platform → Market Data Subscriptions**
(in der Seitenleiste: *Settings → User Settings → Trading Platform → Subscribe to Market Data* —
**nicht** unter *Account Settings*).

Direkter Deep-Link nach Login:
`https://www.interactivebrokers.com/sso/resolver?action=UserSettings&config=MarketData`

Die Abo-Liste ist read-only; zum Hinzufügen das **⚙-Symbol** rechts oben in der Box
„Subscriptions" klicken.

### 3.5 Kostenbild

| Szenario | Kosten/Monat |
|---|---|
| Nur Datensammlung, kein Handel | ~$1,55 (EUR ~1,40) |
| Live-Betrieb mit ≥$20 Kommission | $0 |

Zum Vergleich: Databento ~$199. Der einmalige 6-Monats-Backfill kostet damit faktisch einen
einzigen Monatsbeitrag.

---

## 4. IBKR-Technik — harte Grenzen, alle aus der offiziellen Doku

Quelle: <https://interactivebrokers.github.io/tws-api/historical_limitations.html> und
<https://interactivebrokers.github.io/tws-api/historical_bars.html>

### 4.1 `reqHistoricalData` mit 1-Sekunden-Bars

- `barSizeSetting="1 secs"` ist ein gültiger Wert.
- **Max. 1800 S (30 Minuten) Daten pro Request.**
- **Bars ≤30s reichen nur 6 Monate zurück.** Harte Grenze, kein Trick umgeht sie.
  (Futures generell: 2 Jahre — gilt aber nur für gröbere Bars.)
- Pacing: keine identischen Requests binnen 15 s; max. 6 Requests für dieselbe
  Contract/Exchange/TickType-Kombination binnen 2 s; **max. 60 Requests je 10 Minuten**.

> ⚠️ **Noch nicht gegen den Account des Nutzers getestet.** Die 1s-Verfügbarkeit ist
> dokumentiert und aus der 6-Monats-Klausel logisch ableitbar, aber nach dem
> Nulltoleranz-Standard aus `CLAUDE.md` gilt sie erst nach einem echten Request als bestätigt.
> Das ist der erste offene Schritt (Abschnitt 7).

### 4.2 Durchsatzrechnung (verifiziert, nachrechenbar)

| Größe | Wert |
|---|---|
| Pacing-Limit | 60 Requests / 10 Min |
| Daten je Request | 30 Min |
| **Effektiver Durchsatz** | **30 h Daten je 10 Min Laufzeit** |
| Ein ETH-Tag (23 h) | 46 Requests ≈ **8 Min** |
| 4h-Lücke schließen | 8 Requests ≈ **80 Sek** |
| **6 Monate Backfill** (~130 Handelstage) | ~6.000 Requests ≈ **17 h Dauerlauf**, einmalig |

Der laufende Nachlad ist damit unkritisch: auch nach Tagen ohne Lauf ist der Rückstand in
Minuten aufgeholt.

### 4.3 ⚠️ Datenlücken sind strukturell, kein Bug

Bei `whatToShow="TRADES"` liefert IBKR **keine Kerze für Sekunden ohne Trade**. MNQ hat auf
1s-Ebene in der Asia-Session reichlich handelslose Sekunden.

**Konsequenz — muss explizit entschieden und dokumentiert werden:** leer lassen vs. forward-fill.
Ein stillschweigendes Auffüllen verfälscht jede Zeitfenster-Statistik; ein stillschweigendes
Weglassen lässt Lückenzähler falsch anschlagen. Nach `CLAUDE.md` („Marktdaten wie Gold
behandeln") ist die Zahl der handelslosen Sekunden eine **Pflichtkennzahl im Report**, nicht
eine Randnotiz.

Alternative für tickgenaue Arbeit: `reqHistoricalTicks` (echte Trades, 1000 je Request) —
empfohlen zusätzlich für präzisionskritische Levels (ORG-C.E., FVG-Grenzen, Qs/Os/Hs).

### 4.4 Laufzeitumgebung

- **Eine lokale Broker-Instanz ist zwingend.** Für Privatkonten gibt es keinen gatewaylosen
  Weg: IBKRs OAuth-Direktzugang ist institutionellen Kunden vorbehalten; Retail braucht den
  Client Portal Gateway bzw. TWS/IB Gateway.
- **IB Gateway statt TWS** — schlanke Java-App ohne Charts, geringer RAM, reine
  API-Schnittstelle. Headless auf Linux/VPS lauffähig.
- **IBC (ib-controller)** automatisiert Login und den von IBKR erzwungenen Tages-Restart
  (~Mitternacht ET) sowie das Samstags-Wartungsfenster. Danach ist nur noch **einmal pro Woche**
  eine Authentifizierung nötig (nach Sonntag 01:00 ET).
  <https://github.com/ib-controller/ib-controller>
- **Python-Client: `ib_async`**, nicht `ib_insync` — letzteres wird nicht mehr gepflegt,
  `ib_async` ist der aktive Nachfolger. Muss in `algo/requirements.txt` ergänzt werden.
- ⚠️ **60-Tage-Regel:** IBKR kündigt Marktdaten-Abos automatisch, wenn 60 Tage lang kein Login
  in TWS erfolgt ist. Gateway-Logins zählen mit — aber wenn die Anbindung nach dem Backfill
  monatelang ruht, ist das Abo weg und muss neu bestellt werden.

### 4.5 ⚠️ Sandbox-Grenze für LLM-Agenten

Die Cowork-/Claude-Code-Sandbox ist eine **isolierte Linux-VM ohne Netzzugriff auf die
TWS/Gateway-Instanz des Nutzers**. Der Verifikations-Test und der Backfill können daher
**nicht** aus der Agenten-Umgebung ausgeführt werden — sie müssen auf dem Windows-Rechner des
Nutzers laufen. Das nächste Modell sollte das Skript bauen und den Nutzer den Lauf ausführen
lassen, statt zu versuchen, selbst zu verbinden.

---

## 5. Repo-Konventionen, die der neue Fetcher einhalten muss

Aus `algo/fetch_yfinance.py`, `algo/marktdaten.py`, `algo/build_parquet.py` und
`tools/analyze_ohlc.py` gelesen (Stand 2026-08-15).

### 5.1 Ablage und Dateiformat (bestehender Bestand)

```
raw/marktdaten/<YYYY>/<MM>/<DD.MM.YYYY>/<SYMBOL> <YYYY-MM-DD> <tf>.csv
```

Beispiel-Tagesordner `raw/marktdaten/2026/08/14.08.2026/`:
```
ES 2026-08-14 1m.csv        MNQ 2026-08-14 1h.csv       MNQ 2026-08-14 5m.csv
MNQ 2026-08-14 15m.csv      MNQ 2026-08-14 1m (2).csv   NQ 2026-08-14 1m.csv
MNQ 2026-08-14 1d.csv       MNQ 2026-08-14 1m.csv       MNQ 2026-08-14 4h.csv
```

Das Suffix `(2)`/`(3)` markiert einen zusätzlichen **manuellen TradingView-Export** desselben
Tages. Dessen An-/Abwesenheit ist laut `CLAUDE.md` das Erkennungsmerkmal dafür, ob ein Tag nur
per `fetch_yfinance.py` ins Depot kam (und damit tick-unsicher ist).

**CSV-Schema:** `time,open,high,low,close` — `time` als **UNIX-Sekunden** (int64).

### 5.2 Pflicht-Fallstricke aus den Arbeitsstandards

| Regel | Umsetzung |
|---|---|
| Zeitauflösung **immer** `.as_unit("s")` | nie manuelle Division; stiller Pandas-ns/us/s-Wechsel ist der schädlichste Fehlertyp hier |
| Handelstag = **18:00 NY Vortag bis 17:00 NY** (Globex) | `fetch_yfinance.py::trading_day()` als Vorlage übernehmen |
| Nie überschreiben | `write_day()` prüft `dest.exists()` und überspringt |
| Nulltoleranz-Gate **vor** dem Schreiben | `tools.analyze_ohlc.pruefe_kerzen(kerzen, symbol, quelle)` — wirft `OHLCDefekt` bei harten Verstößen, gibt weiche Auffälligkeiten als Liste zurück. Anlass: 71 degenerierte Daily-Bars, die zwei Wochen unbemerkt im Depot lagen. |
| Gegenprüfung gegen unabhängige Quelle | `tools.analyze_ohlc.pruefe_gegen_referenz(kerzen, referenz, toleranz=0.01)` — beide Argumente `{ts: (o,h,l,c)}`. **Vergleicht bewusst nur O/H/L**, nicht Close: der Close weicht zwischen Feeds systematisch ab (Settlement vs. letzter Trade), Fehlschluss vom 2026-08-13. |

Nützliche Konstanten in `tools/analyze_ohlc.py`:
`NY = ZoneInfo("America/New_York")`, `DATA_DIR`, `TICK_SIZE["MNQ"] = 0.25`,
`SESSION_TYP["MNQ"] = "futures_rth"`, `TF_MINUTES`.

### 5.3 ⚠️ 1s gehört **nicht** ins Tages-CSV-Schema

Mengengerüst: ~**82.800 Kerzen/Tag** (23 h ETH). 6 Monate ≈ **10,8 Mio. Zeilen**, als CSV grob
500 MB, als Parquet ~200–400 MB.

Das bestehende Ein-CSV-pro-Tag-Schema kippt bei dieser Menge (Parsing-Zeit pro Backtest-Lauf).
**Vorlage existiert bereits im Repo:** `algo/build_parquet.py` verdichtet den
histdata-Forex-Bestand (73.105 CSVs, 92 Mio. Zeilen) zu 10 Parquet-Dateien, weil
„92 Mio. Zeilen als CSV zu parsen kostet Minuten pro Backtest-Lauf, Parquet Sekunden".
`algo/cache/` ist gitignored und jederzeit aus `raw/` neu baubar.

**Empfehlung:** analoge eigene Ebene für 1s, nicht in `raw/marktdaten/<tag>/` einsortieren.
Einstiegspunkt für Backtests bleibt `algo/marktdaten.py::bars(symbol, tf, von, bis)` — dort
müsste `1s` als Timeframe ergänzt werden, damit kein Detektor den Unterschied merkt.

### 5.4 Verwandte bestehende Module

| Modul | Relevanz |
|---|---|
| `algo/fetch_yfinance.py` | Strukturvorlage für den neuen Fetcher (Chunking, `write_day`, Gate) |
| `algo/ingest_tvexport.py` | splittet TradingView-Exporte nach Handelstagen, merged in den Bestand. Konfliktregel: bei gleichem Zeitstempel gewinnt der **neue** Export (TradingView revidiert nach: 7,7 % der Kerzen, fast nur open/close, meist 1 Tick). Auf `1d` nicht nutzbar. |
| `algo/fetch_dukascopy.py` | schreibt bewusst **Mid** — laut `PLAN.md` explizit „für den IBKR-Abgleich" |
| `algo/build_parquet.py` | Vorlage für die 1s-Verdichtung |
| `algo/marktdaten.py` | einheitlicher Zugriff `bars()`; hier muss `1s` andocken |
| `algo/selfcheck.py` | 26 Regressions-Selbstchecks, vor größeren Refactors laufen lassen. Eingefrorene Baseline: `algo/results/mnq_baseline_2026-08-15.txt` |

---

## 6. Verifikationsplan (der erste auszuführende Schritt)

**Vor** dem 17-Stunden-Backfill steht ein Einzeltest. Begründung: `CLAUDE.md` verlangt
Zeitverifikation gegen eine unabhängige Quelle, bevor Daten als fertig gemeldet werden — und
17 Stunden auf einer ungeprüften Annahme sind teuer.

**Testumfang: ein einzelner 30-Minuten-Abruf MNQ 1s.** Zu prüfen:

1. **Liefert IBKR überhaupt 1s-Bars?** (bestätigt die Doku-Annahme aus 4.1)
2. **Zeitstempel** gegen einen bestehenden TradingView-Export desselben Fensters — auf 1m
   aggregiert, damit vergleichbar. Kein Offset, keine DST-Verschiebung.
3. **Preise auf Tick-Ebene** via `pruefe_gegen_referenz(..., toleranz=0.01)`, nur O/H/L.
   Referenzwert: `TICK_SIZE["MNQ"] = 0.25`. Anlass für diese Prüfung: der yfinance-Feed wich
   am 2026-08-12 am 9:30-Open um 0,5 Punkte von der Chart-/Broker-Quelle ab
   (`PLAN.md` 2026-08-13) — kein Pipeline-Bug, der Feed selbst.
4. **Handelslose Sekunden zählen** (siehe 4.3) und als Quote ausweisen.
5. `pruefe_kerzen()` muss grün sein.

Erst wenn alle fünf Punkte sauber sind, lohnt der Backfill.

---

## 7. Offene Schritte

| # | Schritt | Status |
|---|---|---|
| 1 | `ib_async` in `algo/requirements.txt` ergänzen | offen |
| 2 | `algo/fetch_ibkr.py` bauen: 1800s-Chunking, Pacing-Limiter (60/10 Min), `.as_unit("s")`, Lückenerkennung über letzten Timestamp im Archiv, `pruefe_kerzen`-Gate, `--verify`-Modus für den Einzeltest | offen |
| 3 | Verifikations-Test **auf dem Windows-Rechner des Nutzers** laufen lassen (nicht in der Agenten-Sandbox, siehe 4.5) | offen |
| 4 | Bei grünem Test: 6-Monats-Backfill (~17 h), volle ETH | offen |
| 5 | 1s-Ebene in `algo/marktdaten.py::bars()` andocken (Parquet-Pfad analog `build_parquet.py`) | offen |
| 6 | IB Gateway + IBC für den unbeaufsichtigten täglichen Nachlad einrichten | offen |
| 7 | Log-Eintrag in `algo/PLAN.md`, Modul-Abschnitt in `algo/README.md`, Eintrag in `wiki/log.md` | offen |

**Bewusst noch nicht angefasst:** `algo/broker_ibkr.py` (Order-Ausführung, Roadmap-Punkt 4).
Der Datenpfad zieht die IBKR-Anbindung zeitlich vor, ersetzt aber nicht die Reihenfolge
Regel-Schicht → Validierung → Adapter → **Paper-Trading** → Live. Die Sperre gegen echtes
Kapital ohne gesonderte Nutzerfreigabe bleibt unberührt.

**Security-Gate:** Sobald IBKR-Zugangsdaten in Dateien landen (IBC speichert Credentials im
Klartext in seiner Config!), greift das Security-Gate aus `CLAUDE.md` — Secret-Scan auf festes
Intervall umstellen (mind. wöchentlich), IBC-Config und `algo/.secrets.yaml` in `.gitignore`
prüfen **bevor** der erste Lauf stattfindet.

---

## 8. ⚠️ Lose Dateien in `raw/` — nicht einsortiert, bewusst liegen gelassen

Beim Session-Start gefunden (`CLAUDE.md`, Abschnitt „Automatische Einsortierung"). **Nicht**
verschoben, weil alle drei Fälle eine Entscheidung brauchen, die nicht geraten werden sollte:

| Datei | Inhalt | Warum liegen geblieben |
|---|---|---|
| `raw/CME_MINI_MNQ1!, 1_b84a2.csv` | MNQ 1m, **2026-08-12 21:00 NY → 2026-08-14 16:59 NY**, 2.580 Kerzen | Mehrtägiger TradingView-Export. Gehört über `algo/ingest_tvexport.py <datei> MNQ --tf 1m` eingespielt, nicht per Dateiverschiebung — der Bestand hat für diese Tage bereits `MNQ 2026-08-14 1m.csv` **und** `MNQ 2026-08-14 1m (2).csv`. Merge-Konfliktregel greift. |
| `raw/CME_MINI_MNQ1!, 15_6fcfd.csv` | MNQ 15m, **2026-07-01 20:00 NY → 2026-08-14 16:45 NY**, 2.920 Kerzen | dito, `--tf 15m`. Deckt ~6 Wochen ab, überlappt breit mit dem Bestand. |
| `raw/preview.csv` | **Databento**-Preview: `ts_event,rtype,publisher_id,instrument_id,open,high,low,close,volume,symbol`, 2 Datenzeilen, Symbol `ESZ2`, 2022-01-03 | Kein Marktdaten-Bestand, sondern ein Evaluierungs-Artefakt zur Databento-Entscheidung (Abschnitt 2.2). Gehört nach `raw/algo-pruefung/` oder gelöscht. |

**Aufgabe für das nächste Modell:** Punkt 1 und 2 mit `ingest_tvexport.py` einspielen (der
zählt Abweichungen und berichtet sie), Punkt 3 mit dem Nutzer klären.

---

## 9. Kontext aus `algo/PLAN.md`, der hier hineinspielt

Nicht Teil dieser Aufgabe, aber für ein Modell relevant, das im Repo weiterarbeitet — **zwei
`raw/`-Schreibläufe warten auf Nutzerfreigabe** (Stand 2026-08-15):

1. `python algo/repair_dst_2019.py --apply` — histdata stempelt ab 2019 an EU- statt
   US-Umstellungsterminen, 1.962.205 von 81,7 Mio. Kerzen (2,40 %) eine Stunde zu früh.
   Trockenlauf grün, 0 Grenzüberschreitungen.
2. `python algo/fill_luecken_dukascopy.py --apply` — Feb–Jul 2023 fehlen im Forex-Bestand
   ~30 % aller Kerzen (Quellenschaden bei histdata, aus Dukascopy heilbar).
3. Danach zwingend `python algo/build_parquet.py`.

**Harte Reihenfolge:** 1 vor 2, sonst verschiebt die DST-Reparatur das frisch Gefüllte
fälschlich mit. Betrifft nur Forex, **nicht** den MNQ-1s-Pfad — aber wer `raw/` anfasst, sollte
davon wissen.

**Nebenbefund:** In `.git/index.lock` liegt eine leere Sperrdatei aus einem abgebrochenen
git-Aufruf. Blockiert den nächsten Commit bzw. `push.ps1` — vor dem nächsten Push von Hand
entfernen.

---

## 10. Quellen

- [TWS API: Historical Data Limitations](https://interactivebrokers.github.io/tws-api/historical_limitations.html)
- [TWS API: Historical Bar Data](https://interactivebrokers.github.io/tws-api/historical_bars.html)
- [IBKR Market Data Pricing](https://www.interactivebrokers.com/en/pricing/market-data-pricing.php)
- [IBKR Client Portal User Guide: Subscribe to Market Data](https://www.ibkrguides.com/clientportal/usersettings/marketdatasubscriptions.htm)
- [IBKR Client Portal Web API](https://interactivebrokers.github.io/cpwebapi/)
- [IBC / ib-controller](https://github.com/ib-controller/ib-controller)
- [TradingView Terms of Service](https://www.tradingview.com/policies/)
- [Databento GLBX.MDP3](https://databento.com/datasets/GLBX.MDP3)
- [Databento: Introducing new CME pricing plans](https://databento.com/blog/introducing-new-cme-pricing-plans)

---

*Erstellt 2026-08-15. Kontoidentifikatoren des Nutzers sind bewusst nicht enthalten.*
