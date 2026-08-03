# Algo-Trading-Projekt — Planungsdokument

Status: **Planungsphase, kein Code.** Ziel dieses Ordners: aus den taeglich wachsenden
OHLC-Daten in `raw/marktdaten/` einen eigenen, regelbasierten Handelsalgorithmus fuer MNQ
ableiten — nicht durch neue Theorie, sondern durch Muster, die sich ueber viele Tage
statistisch bestaetigen.

## Datengrundlage

- `raw/marktdaten/<dd.mm.jjjj>/` — ein Ordner pro Handelstag, TradingView-Exporte in
  1m/5m/15m/1h/4h/1d. Konvention: [[OHLC-Datenanalyse (Workflow)]].
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
