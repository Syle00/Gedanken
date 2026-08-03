# Algo-Trading-Projekt — Planungsdokument

## Schicht 1 — Übergeordnetes Ziel

**Das ist das Ziel von allem hier** — Wiki, `raw/marktdaten/`, `tools/analyze_ohlc.py`, dieser
Ordner: ein Handelsalgorithmus, der **selbststaendig und allein ueber Interactive Brokers**
(TWS/IB-Gateway-API) handelt. Kein Signal-Geber fuer einen Menschen, kein Backtest-Spielzeug —
am Ende steht eine laufende, autonome Ausfuehrung. Alles andere in diesem Dokument (Fundament,
offene Punkte, Backtesting) ist **Unterbau fuer dieses eine Ziel**, keine eigenstaendigen Ziele.

Status: **Planungsphase, kein Code.** Der Weg dahin fuehrt ueber echte, wachsende Datenbasis
statt ueber vorschnelle Regeln: aus den taeglich wachsenden OHLC-Daten in `raw/marktdaten/`
einen regelbasierten Handelsalgorithmus fuer MNQ ableiten, der sich per IBKR-API selbststaendig
ausfuehrt.

## Datengrundlage

- `raw/marktdaten/<jjjj>/<mm>/<dd.mm.jjjj>/` — ein Ordner pro Handelstag, TradingView-Exporte in
  1m/5m/15m/1h/4h/1d. Jahr/Monat verschachteln sich von selbst beim Wechsel, damit der Ordner
  bei taeglichen Exporten nicht flach mit hunderten Tagesordnern volllaeuft. Konvention:
  [[OHLC-Datenanalyse (Workflow)]].
- Ab jetzt taeglich neu: TradingView-Export flach nach `raw/marktdaten/` legen,
  `tools/sort_marktdaten.py` raeumt automatisch ein (laeuft auch vor jedem `push.ps1` und
  vor jedem `analyze_ohlc.py`-Aufruf).
- Bisher eingesammelte Tage: siehe Log unten.

## Bereits vorhandenes Fundament

`tools/analyze_ohlc.py` rechnet pro Tag bereits:

- Opening Prices (Midnight/8:30/9:30/13:30), Session-Level (Asia/London/NY AM/PM/...)
- Liquidity Sweeps (mit Levelalter + Penetration + Bestaetigungsfenster)
- Market Structure Breaks (BOS/CHoCH, sequenziell)
- Displacement-Kerzen, Fair Value Gaps (Groesse, CE, Fuellstatus)
- Macro-Fenster-Expansion (Jannes' XX:50–XX+1:10-Raster)
- Consolidation-Phasen, unangetastete Liquiditaet am Datenende
- Setup-Checkliste gegen einen Zeitpunkt (`--at HH:MM`), 7 von 8 Punkten objektiv pruefbar

Das ist die Rohmasse fuer den Algorithmus — noch keine Handelslogik, nur Erkennung.

## Was fuer einen Algorithmus noch fehlt

1. **Backtesting-Harness.** Die Detektoren muessen ueber viele Tage laufen und aggregiert
   werden (Trefferquote/Erwartungswert je Muster), statt Tag fuer Tag einzeln gelesen zu
   werden. Existiert noch nicht.
2. **Harte Entry-/Exit-/Stop-/Target-Regeln.** Die 8er-Checkliste ist eine manuelle
   Pruefliste fuer einen Menschen ("Entry bleibt deine Entscheidung"). Ein Algorithmus
   braucht stattdessen eine deterministische Regel, die aus denselben Daten einen
   Trigger + Stop + Ziel ableitet.
3. **Stichprobengroesse.** Aktuell liegen 2 Handelstage vor (31.07., 03.08.2026). Fuer
   belastbare Aussagen zu Killzone-Trefferquote, Macro-Expansion-Rate oder
   Silver-Bullet-Fenstern braucht es Wochen bis Monate. Vor Regel-Festlegung: weiter
   sammeln, nicht auf 2 Tage ueberfitten.
4. **Risk-/Money-Management.** Positionsgroesse, Stop-Distanz relativ zur gesweepten
   Liquiditaet, Max-Trades/Tag — bisher nirgends im Vault spezifiziert.
5. **Pattern-Prioritaet.** Kandidaten aus dem Wiki, sobald genug Tage vorliegen:
   [[Silver Bullet Model]], [[NY Lunch Macro Model]], [[Judas Swing]] / AM-Reversal,
   [[Midnight Opening Range]] STD-Projektion, [[ORG (Opening Range Gap) & 1st Presented FVG]].

## Code-Ideen (Backlog — notiert, noch nicht umgesetzt)

Ideen werden hier gesammelt, sobald sie auftauchen, statt verloren zu gehen oder verfrueht
implementiert zu werden. Kein Punkt hier ist beauftragt — erst wenn genug Tage vorliegen
(siehe oben), wird priorisiert und gebaut.

1. **`tools/backtest_ohlc.py`** — laeuft ueber alle `raw/marktdaten/<jjjj>/<mm>/<dd.mm.jjjj>/`-
   Ordner, ruft je Tag dieselben Detektoren aus `analyze_ohlc.py` auf (`sweeps`,
   `structure_breaks`, `displacements`, `macro_windows`) statt sie neu zu schreiben, und
   aggregiert Trefferquote/Erwartungswert je Muster (z.B. "Sweep + Displacement im
   09:50-Macro") ueber alle Tage. Erst sinnvoll ab ~20-30 Handelstagen.
2. **Regel-Schicht statt Checkliste.** Die 8er-Checkliste in `analyze_ohlc.py` prueft nur
   Ja/Nein. Eine Handelsregel braucht zusaetzlich Entry-Preis, Stop (z.B. hinter dem
   gesweepten Level) und Ziel (naechstes Level aus `untouched_levels()`). Idee: eine Funktion
   `plan_trade(bars, at) -> TradeSetup | None`, die genau diese drei Zahlen liefert, aufbauend
   auf den bestehenden Detektoren statt neuer Logik.
3. **IBKR-Anbindung als eigener, duenner Adapter** (`algo/broker_ibkr.py`, noch nicht
   angelegt): Order-Ausfuehrung ueber die Interactive-Brokers-API (TWS/IB-Gateway, z.B. per
   `ib_insync` oder offiziellem `ibapi`) hinter einer schmalen Schnittstelle
   (`place_order`, `get_position`, `cancel`), damit die Regel-Schicht broker-unabhaengig
   bleibt. Erst nach Punkt 1+2, und zuerst gegen ein Paper-Trading-Konto, nie direkt live.
4. **Backtest-Ergebnisse als Datenartefakt**, nicht nur als Konsolenausgabe: eine Zeile pro
   erkanntem Setup (Datum, Zeit, Muster, Richtung, Entry/Stop/Target, Ausgang) in einer
   CSV/JSON unter `algo/`. Das ist die Bruecke, ueber die "laufende Daten + Wiki verbessern
   den Algo" konkret wird — sonst bleibt der Satz eine Absicht ohne Mechanismus.
5. Detektor-Schwellen (`CFG` in `analyze_ohlc.py`: `min_age`, `min_pen`, `disp_factor`,
   `confirm`) bleiben die **eine** Quelle fuer Parameter, die Tagesreport und spaeterer
   Backtest teilen — nicht doppelt pflegen.

## Naechster Schritt

Kein Code, bis genug Tage vorliegen, um eine erste Musterhypothese (z.B. "Macro-Expansion
nach einem Sweep des RTH-Opens") an echten Daten zu pruefen statt an zwei Tagen zu raten.
Jeder neue Tag wird wie bisher als `wiki/synthesis/MNQ <Datum> — Datenbasierter
Tagesrueckblick.md` dokumentiert; dieses Dokument haelt zusaetzlich fest, welche Muster
sich ueber mehrere Tage wiederholen.

## Log

| Datum | Ereignis |
|---|---|
| 2026-08-03 | Projekt angelegt. Datengrundlage: 31.07.2026, 03.08.2026 (03.08. Handelstag noch nicht beendet, Daten bis 16:18 NY). Bug in `tools/analyze_ohlc.py` gefixt: HTF-Kontext ("Vortag") behandelte die noch laufende Tageskerze faelschlich als Historie. |
| 2026-08-03 | Nutzer praezisiert das Ziel: **Schicht 1 = autonomer IBKR-Handelsalgorithmus**, alles andere hier ist Unterbau. `raw/marktdaten/` auf Jahr/Monat-Verschachtelung umgestellt (`tools/sort_marktdaten.py`, `tools/analyze_ohlc.py` mitgezogen); bestehende Tage nach `2026/07/31.07.2026` bzw. `2026/08/03.08.2026` migriert. Erste Code-Ideen als Backlog notiert (Backtest-Harness, Regel-Schicht, IBKR-Adapter, Backtest-Ergebnis-Artefakt). |
