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

1. **Backtesting-Harness. Erste Version existiert:** `algo/backtest_ohlc.py`. Laeuft ueber
   alle Handelstage in `raw/marktdaten/`, importiert dieselben Detektoren aus
   `tools/analyze_ohlc.py` (`fvgs`, `viis`, `sweeps`, `structure_breaks`, `macro_windows` —
   keine Neuimplementierung) und schreibt die Aggregation nach
   `wiki/synthesis/Muster-Validierung (laufend).md`. Bleibt bewusst Standardbibliothek wie
   `analyze_ohlc.py` selbst — die Aggregation ist eine Handvoll Zaehler, kein
   DataFrame-Problem. **Wichtige Falle, auf die man achten muss:** `analyze_ohlc.py` skaliert
   `min_age`/`confirm` beim CLI-Aufruf mit dem Timeframe (in `main()`); wer die Detektoren
   direkt importiert, muss dieselbe Skalierung von Hand anwenden, sonst laufen Tagesreport
   und Backtest mit verschiedenen Schwellen und liefern nicht vergleichbare Zahlen (genau
   dieser Fehler ist beim ersten Entwurf passiert und wurde noch am selben Tag gefixt).
   **Werkzeugentscheidung pandas/matplotlib** bleibt fuer den Explorations-/Visualisierungs-
   Layer (`algo/viz_prototype.py` + `.html`, Zeitzonen/Fenster-Slicing sind dort eine Zeile
   statt einer Schleife) — beide Wege liefern dieselben Zahlen (Macro-Range 175,00 Pkt
   deckungsgleich). Abhaengigkeiten fuer den pandas-Pfad: `algo/requirements.txt`.
   **Naechster Ausbauschritt (Nutzerwunsch "alle PD Arrays, das gesamte Wiki"):** siehe
   Abdeckungs-Tabelle in der generierten Seite selbst — Order-Block-Varianten, IFVG, BPR,
   CBDR, NWOG/NDOG, OTE, Breakaway Gap, Suspension Block, Judas-Swing-Zeitfenster und
   SMT (zweites Symbol noetig) haben noch keinen Detektor.
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

1. ~~`tools/backtest_ohlc.py`~~ **erledigt, siehe oben** — liegt unter `algo/backtest_ohlc.py`
   statt `tools/`, sonst wie geplant: laeuft ueber alle Tagesordner, aggregiert die
   bestehenden Detektoren, schreibt nach `wiki/synthesis/Muster-Validierung (laufend).md`.
   Nutzer wollte es sofort mit den vorhandenen 2 Tagen starten statt auf 20-30 Tage zu
   warten — die Seite selbst warnt jetzt explizit vor der kleinen Stichprobe, statt zu warten.
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

**Korrektur (2026-08-03):** Der urspruengliche Plan war, mit dem Backtest zu warten, bis
genug Tage vorliegen. Nutzerwunsch war ausdruecklich das Gegenteil — sofort mit den
vorhandenen Daten anfangen und bei jedem neuen Tag weiterlaufen lassen, damit sich die
Aussagekraft von selbst aufbaut, statt eine willkuerliche Wartegrenze abzuwarten. Umgesetzt:
`algo/backtest_ohlc.py` existiert und wird ab jetzt bei jedem neuen Handelstag erneut
ausgefuehrt (siehe [[../wiki/models/OHLC-Datenanalyse (Workflow)|OHLC-Datenanalyse (Workflow)]]).
Jeder neue Tag bekommt weiterhin zusaetzlich seinen eigenen
`wiki/synthesis/MNQ <Datum> — Datenbasierter Tagesrueckblick.md`; die Muster-Validierungs-Seite
aggregiert alle Tage zusammen. Naechster Ausbauschritt ist mehr Detektoren (siehe Punkt 1
oben), nicht mehr Warten.

## Log

| Datum | Ereignis |
|---|---|
| 2026-08-03 | Projekt angelegt. Datengrundlage: 31.07.2026, 03.08.2026 (03.08. Handelstag noch nicht beendet, Daten bis 16:18 NY). Bug in `tools/analyze_ohlc.py` gefixt: HTF-Kontext ("Vortag") behandelte die noch laufende Tageskerze faelschlich als Historie. |
| 2026-08-03 | Nutzer praezisiert das Ziel: **Schicht 1 = autonomer IBKR-Handelsalgorithmus**, alles andere hier ist Unterbau. `raw/marktdaten/` auf Jahr/Monat-Verschachtelung umgestellt (`tools/sort_marktdaten.py`, `tools/analyze_ohlc.py` mitgezogen); bestehende Tage nach `2026/07/31.07.2026` bzw. `2026/08/03.08.2026` migriert. Erste Code-Ideen als Backlog notiert (Backtest-Harness, Regel-Schicht, IBKR-Adapter, Backtest-Ergebnis-Artefakt). |
| 2026-08-03 | Frage beantwortet: pandas eignet sich fuer den Backtest-/Aggregations-Layer (kein eigenes Backtesting-Framework, aber die richtige Grundlage fuer Punkt 1 oben). pandas + matplotlib installiert. Beleg gebaut: `algo/viz_prototype.py` laedt den 03.08.-5m-Chart per pandas, `algo/viz_prototype.html` zeigt ihn interaktiv (Preislinie, Sweep/Displacement/Macro-Expansion annotiert, Hover-Tooltip) — Macro-Range 175,00 Pkt deckt sich exakt mit `tools/analyze_ohlc.py`. `algo/requirements.txt` neu (pandas, matplotlib; `tools/analyze_ohlc.py` bleibt Stdlib-only). |
| 2026-08-03 | Nutzerwunsch: alle Daten (CISD, ORG, "alle PD Arrays", "das gesamte Wiki") sollen jetzt schon und laufend gegen echte Daten geprueft werden, konkrete Frage: "wird das C.E eines ORG zu 70% gefuellt?". Ergebnis: dieser 70%-Wert steht in keiner ingesteten Quelle im Vault (gezielt gesucht, nur False-Positives zur "70%-Wednesday-Regel" gefunden) — vermutlich allgemeines ICT-Wissen von aussen, nicht aus dem hier vorliegenden Material. `algo/backtest_ohlc.py` gebaut: aggregiert `fvgs`/`viis`/`sweeps`/`structure_breaks`/`macro_windows` ueber alle Tagesordner, schreibt `wiki/synthesis/Muster-Validierung (laufend).md`. **Bug im ersten Entwurf gefunden und gefixt**: CFG-Skalierung (`min_age`/`confirm` je Timeframe) wird nur in `analyze_ohlc.py`s CLI (`main()`) angewendet, nicht wenn man die Detektoren direkt importiert — dadurch waren Struktur-Break-Zahlen vor dem Fix ca. 5x zu niedrig. Neuer Detektor `viis()` in `tools/analyze_ohlc.py` (Volume Imbalance, 2-Kerzen-Luecke Close→Open) ergaenzt, als erster Schritt Richtung "alle PD Arrays" — vollstaendige Liste der noch fehlenden PD Arrays (Order-Block-Varianten, IFVG, BPR, CBDR, NWOG/NDOG, OTE, Breakaway Gap, Suspension Block, Judas-Zeitfenster, SMT) in der generierten Seite und hier im Backlog festgehalten, nicht in einem Schritt geraten. Ergebnis bei n=2 Tagen (**nicht belastbar**, nur Statusbericht): C.E erreicht bei grossen FVGs 78%, komplett gefuellt 67% — in der Naehe der kursierenden 70%, aber bei 2 Tagen reiner Zufall moeglich. |
