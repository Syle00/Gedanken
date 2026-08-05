---
tags: [synthesis, algo, backtest, generiert, makro, fred]
created: 2026-08-05
updated: 2026-08-05
sources: ["[[../../algo/backtest_fred_events.py]]", "[[../../algo/fetch_fred.py]]"]
---

# Makro-FRED-Zusammenhaenge (Eigene Daten, laufend)

Ursprüngliche Frage: MNQ-Reaktion an CPI-/FOMC-Tagen. **Bewusst nicht gebaut** — siehe
Abschnitt "Nicht getestet" unten, statt eines Tests mit falsch datierten Ereignissen.

> **Datenbank**: `raw/marktdaten/fred/*.csv` (via `algo/fetch_fred.py`), ausgewertet von
> `algo/backtest_fred_events.py`. Skript einfach erneut laufen lassen, sobald `raw/marktdaten/`
> und die FRED-CSVs wachsen; diese Seite wird danach von Hand nachgezogen (kein Auto-Write).
>
> **Lösch-statt-Markier-Regel**: wie bei [[Seasonal Tendency (Eigene Daten, laufend)]] — stellt
> sich eine Zahl hier mit mehr Daten als Rauschen heraus, wird sie entfernt statt mit ⚠️ stehen
> gelassen.

Stand: 147 MNQ-Handelstage (2026-01-02 bis 2026-08-04). Kleines Fenster (7 Monate) — alle
Zahlen unten sind offene Hypothesen, keine belastbaren Ergebnisse.

## Nicht getestet: CPI-/FOMC-Reaktionstag

- **CPIAUCSL**: FREDs `date`-Feld ist der Referenzmonat, nicht das Veröffentlichungsdatum
  (das liegt ~2-3 Wochen später). Ohne verifizierten Release-Kalender wäre jeder
  "Reaktionstag" falsch datiert.
- **DFF** (Effective Fed Funds Rate) schwankt täglich in Basispunkten ohne FOMC-Bezug —
  reiner Marktzins, kein Zielsatz. Gegen Änderungstage zu testen wäre Rauschen als Ereignis
  verkauft.
- **DFEDTARU** (oberes Zielband) ändert sich nur bei echten FOMC-Entscheidungen — sauber,
  aber im MNQ-Fenster gab es laut FRED **keine einzige Änderung** (Rate blieb bei 3,75-4,00 %
  konstant), also n=0 zum Testen. Ein Termin-Kalender (auch "Hold"-Meetings sind Events)
  müsste aus einer verifizierten Quelle kommen — nicht aus geratenem Trainingswissen.

Offene Frage für später: eine verifizierte FOMC-Terminliste (z.B. vom Fed selbst) als
`raw/`-Quelle ablegen, dann sauber testbar.

## 1. VIX-Niveau-Regime (Sanity-Check)

| VIX-Terzil | n | Median-Range | Ø\|Tagesrendite\| |
|---|---|---|---|
| niedrig (14,5-17,0) | 49 | 447,0 | 0,79 % |
| mittel (17,1-18,9) | 49 | 528,0 | 1,20 % |
| hoch (19,1-31,1) | 49 | 476,0 | 1,25 % |

Erwartung (hoher VIX → größere Range) bestätigt sich nur zwischen niedrig und
mittel/hoch, nicht monoton hoch > mittel — mit n=49 je Terzil im aktuellen Fenster nicht
robust genug für eine klare Aussage.

## 2. VIX-Tagesänderung vs. MNQ-Tagesrendite

Korrelation **-0,743** (n=146). Deutlich negativ wie erwartet (VIX-Spike = Down-Tag) —
plausibilisiert die Datenpipeline, ist aber kein eigenständiger Fund (bekannter Zusammenhang).

## 3. DGS10-Tagesänderung (10J-Rendite) vs. MNQ-Tagesrendite

Korrelation **-0,281** (n=146). Schwach negativ — steigende Zinsen drücken tendenziell
MNQ, im aktuellen Fenster aber deutlich schwächer als der VIX-Zusammenhang.

## 4. WALCL (Fed-Bilanzsumme, wöchentlich) vs. MNQ-Wochenrendite

| Bilanz-Trend | n | Ø-Wochenrendite |
|---|---|---|
| wächst | 21 | +0,71 % |
| schrumpft | 6 | +0,46 % |

Unausgeglichene Gruppengrößen (n=21 vs. 6) — im aktuellen Fenster kein klarer
Unterschied, zu wenig Schrumpf-Wochen für eine Aussage.
