# Backtest-Korrektheits-Audit & Praezisions-Layer fuer `algo/` — Design

Status: Design, genehmigt am 2026-08-06. Teilprojekt A von zwei — Teilprojekt B
(Wiki-gestuetzte Strategie-Findung, taegliche Erinnerung) ist ein eigener, spaeterer Spec.

## Ziel

Der Nutzer plant, mit den Ergebnissen aus `algo/` eine echte Handelsstrategie mit echtem
Geld zu entwickeln. Aktuell hat die Backtest-Kette (`backtest_bt.py`, `backtest_ensemble.py`,
`validate.py`, `stress_test.py`, `backtest_walkforward.py`, `dashboard.py`, plus die aelteren
`backtest_*.py`-Explorationsskripte) zwei bereits im Code dokumentierte, aber nie behobene
Praezisionsluecken:

1. Die `backtesting`-Bibliothek rechnet P&L wie eine Aktie (Notional-Kapital x
   Prozent-Kommission), nicht mit dem echten Punktwert eines Futures-Kontrakts (MNQ = $2/Punkt).
   Ueber Zeitraeume mit stark unterschiedlichem Preisniveau (Stress-Test 2008 vs. 2026) fuehrt
   das zu Positionsgroessen, die nicht dem realen Risiko eines festen Kontrakts entsprechen.
2. Reproduziert am 2026-08-06 (`backtest_walkforward.py`, siehe Log): die Bibliothek markiert
   einen erheblichen Teil der Trades als "dubious", weil Stop und Ziel in derselben 5m-Kerze
   liegen und die Fill-Reihenfolge unbekannt ist. Bisher wird das nur als Warnung geloggt
   (Textwiederholung, die den Nutzer verwirrt hat), nicht als Kennzahl gefuehrt oder konservativ
   aufgeloest.

Ziel dieses Audits: jede Datei in `algo/`, die an Backtest-Zahlen beteiligt ist, einzeln
durchgehen, echte Fehler direkt reparieren, beide oben genannten Luecken schliessen, und pro
Datei eine kurze, verstaendliche Erklaerung hinterlegen (was/wie/warum getestet), damit der
Nutzer Fehler erkennen kann, bevor reales Kapital daran haengt.

**Nicht Teil dieses Designs**: neue Strategien aus dem Wiki ableiten, taegliche
Erinnerungsmechanik, Bloomberg-Terminal-artige Optik von `dashboard.py` (explizit vom Nutzer
auf spaeter verschoben).

## Teil 1 — Praezisions-Layer (`algo/pnl.py`, neu)

Duenne Schicht **ueber** der bestehenden `backtesting`-Bibliothek, ersetzt sie nicht (die Lib
macht Order-/Equity-/Drawdown-Verwaltung bereits richtig).

```python
POINT_VALUE = {"MNQ": 2.0, "NQ": 20.0, "ES": 50.0}  # nur tatsaechlich genutzte Symbole

def real_pnl(trades: pd.DataFrame, symbol: str, contracts: int = 1) -> pd.DataFrame:
    """Trades-DataFrame (stats._trades) -> Kopie mit Spalte 'RealPnL_USD',
    berechnet aus (ExitPrice - EntryPrice) * Richtung * POINT_VALUE[symbol] * contracts."""

def flag_dubious(trades: pd.DataFrame, bars: pd.DataFrame) -> pd.DataFrame:
    """Markiert Trades, deren SL/TP im selben Bar wie der Entry liegen (Spalte 'Dubious'),
    und wertet sie konservativ als Verlust (Exit=Stop) statt der Bibliothek die Wahl zu
    ueberlassen. Gibt zusaetzlich `dubious_pct` zurueck (Anteil an allen Trades)."""
```

`dubious_pct` wird ab jetzt in jedem Backtest-/Validierungs-Report als Pflichtzeile ausgegeben
(Report ohne diese Zahl gilt als unvollstaendig).

**Test:** `demo()`-Selbstcheck mit synthetischen Trades — 1 Punkt MNQ-Bewegung x 1 Kontrakt
muss $2 ergeben; ein synthetischer Trade mit SL/TP im selben Bar muss als Verlust markiert
werden.

## Teil 2 — Datei-Reihenfolge des Audits

Von der Basis nach oben, damit ein Fix unten sich nicht unbemerkt nach oben durchzieht:

| # | Datei | Fokus |
|---|---|---|
| 1 | `algo/pnl.py` (neu) | Praezisions-Layer selbst, siehe Teil 1 |
| 2 | `algo/backtest_bt.py`, `algo/rules.py` | Basis-Engine + erste Strategie (Silver Bullet), `pnl.py` einhaengen |
| 3 | `algo/signals.py` | Kein Lookahead in den Signalfunktionen (jede nutzt nur Daten bis Vortag) |
| 4 | `algo/backtest_ensemble.py` | Bias-Modell-Fit strikt auf Vorlauf-Daten, `pnl.py` einhaengen |
| 5 | `algo/validate.py` | Monte-Carlo-/Walk-Forward-Methodik, `dubious_pct` in jede Ausgabe |
| 6 | `algo/stress_test.py` | Krisenfenster-Logik, `pnl.py` fuer NQ=F/ES=F-Punktwerte |
| 7 | `algo/backtest_walkforward.py` | Regressionscheck nach Refactor (siehe Docstring-Hinweis) |
| 8 | `algo/dashboard.py` | Der vom Nutzer gemeldete Fehler (Traceback wird nachgereicht) |
| 9 | uebrige `backtest_*.py` (daily_patterns, fred_events, ndog, nwog, seasonal, tgif, org_ce, fvg_specialness, midnight_range_std/judas) | gleiche Kriterien, geringere Prioritaet (Exploration, nicht Kern-Engine) |

Bei jeder Datei: Lookahead-Bias, Punktwert-/Kommissions-Annahmen, Fill-Realismus,
Daten-Ausrichtung (Timezones/Sessions), sowie generell Code-Qualitaet pruefen und direkt
reparieren (keine separate Freigabe-Schleife, siehe Nutzer-Entscheidung).

## Teil 3 — Deliverables

- **Direkte Fixes** pro Datei, committet mit Beschreibung was/warum.
- **`algo/README.md`** (neu): ein Abschnitt pro Modul — was wird getestet, wie (Methodik),
  warum genau so (welche Wiki-These/Hypothese), bekannte Grenzen. Zielgruppe: der Nutzer selbst,
  der schnell nachschlagen koennen muss, ohne Code zu lesen.
- **`algo/PLAN.md`**-Log-Eintrag am Ende: Zusammenfassung aller gefundenen und behobenen
  Probleme (bestehende Log-Konvention, siehe Datei).
- **`algo/selfcheck.py`** (neu): buendelt alle `demo()`-Selbstchecks aus den auditierten Dateien
  zu einem einzigen Kommando + ein paar Kennzahlen-Plausibilitaets-Checks (Win Rate in [0,100],
  keine NaN/Inf in `RealPnL_USD`, `dubious_pct` vorhanden). Laeuft in Sekunden (buendelt nur
  bestehende kleine Checks, kein neuer Backtest-Lauf). Gedacht als taeglicher
  Regressions-Baustein — die Ausloese-Mechanik (Erinnerung/Loop) ist Teil von Teilprojekt B,
  nicht dieses Designs.
- **Security-Scan** (Secrets/unsichere Patterns, z.B. `algo/.secrets.yaml`): einmalig jetzt als
  Teil dieses Audits, danach woechentlich bzw. sobald eine echte Broker-Anbindung (IBKR-Keys)
  dazukommt — taeglich waere hier unnoetiger Aufwand, da aktuell nichts live handelt.

## Fehlerbehandlung

Wo eine Datei nicht sauber reparierbar ist ohne die zugrunde liegende Strategie neu zu bewerten
(z.B. wenn `pnl.py` zeigt, dass eine bisher "profitable" Strategie in echten Dollar tatsaechlich
verliert), wird das **explizit im Fund-Bericht und im PLAN.md-Log markiert**, nicht
stillschweigend uebernommen — analog zur Widerspruchs-Konvention im Wiki (`CLAUDE.md`).
