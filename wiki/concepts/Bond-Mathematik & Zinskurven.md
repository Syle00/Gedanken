---
tags: [concept, quant-finance, bond-math, zinsen, mit-ocw]
created: 2026-08-12
updated: 2026-08-12
sources: ["[[2025-12-03 - MIT 15.S08 Lecture 1 Part III - Bond Mathematics (Source)]]", "[[2025-12-03 - MIT 15.S08 Lecture 7 - Linear Rates, Products, and Models (Source)]]"]
---

# Bond-Mathematik & Zinskurven

Formelsammlung aus MIT-15.S08-Vorlesung 1-III (Vasily Strela, Grundlagen) und Vorlesung 7 (Andrew
Gunstensen/Mizuho, Praxis: SOFR, Swaps, Kurvenkonstruktion).

## Zins, Diskontierung, Zero-Coupon-Bond

- Diskrete Verzinsung über n Perioden: `(1+r)ⁿ`. Bei m Teilperioden pro Jahr:
  `(1+r/m)^(m·n)`. Grenzwert `m→∞` (stetige Verzinsung): `e^(r·n)` — historisch die erste
  Herleitung der Eulerschen Zahl `e` (Bernoulli, 1683, im Kontext von Zinseszins).
- No-Arbitrage-Diskontfaktor (annualisiert): `Z(n) = 1/(1+r)ⁿ`. Stetige Diskontierung:
  `Z(n) = e^(−r·n)`.
- **Funding = Discounting**: der korrekte Diskontsatz für zukünftige Cashflows ist der eigene
  Finanzierungssatz — jede Abweichung zwischen Finanzierungs- und Diskontsatz wäre eine
  risikolose Arbitrage (No-Arbitrage-Argument, siehe Herleitung in
  [[2025-12-03 - MIT 15.S08 Lecture 7 - Linear Rates, Products, and Models (Source)]]).
- Zero-Coupon-Bond-Preis: `P = N·Z(T)` (N = Notional).
- Coupon-Bond-Preis (geometrische Reihe der diskontierten Cashflows):
  `P = Σₜ C·Z(t) + N·Z(T)` (C = periodischer Coupon).

## Yield, Preis-Yield-Relation, Duration/Convexity

- Yield: die eine konstante Zinsrate, die den beobachteten Marktpreis über obige
  Diskontierungsformel reproduziert. Bei Zero-Coupon-Bonds algebraisch invertierbar, bei
  Coupon-Bonds nur numerisch lösbar.
- Preis und Yield stehen in inverser Beziehung (Yield steht im Diskontfaktor-Nenner): höherer
  Coupon → höherer Yield bei gleicher Laufzeit; höherer Yield → niedrigerer Preis.
- **Duration** = 1. Ableitung des Preises nach dem Yield (skaliert durch den Preis) — Maß für die
  lineare Preissensitivität gegenüber Zinsänderungen.
- **Convexity** = 2. Ableitung — Korrektur der Duration-Näherung für größere Zinsbewegungen
  (nichtlinearer Preis-Yield-Zusammenhang).
- Zinsstrukturkurve (Yield Curve): meist ansteigend (mehr Yield für längere Bindung verlangt),
  historisch aber invertiert vor Rezessionsphasen (u.a. 2007, 2021/22 im Vorlesungsmaterial
  diskutiert) — als empirisch beobachtetes Muster erwähnt, nicht formal bewiesen.

## SOFR, Funding-Raten, Swap-Bewertung

- SOFR-Compounding (tägliche Sätze zu einem Zeitraum-Satz verdichtet):
  `(1+r/360)`-Produkt über alle Tage minus 1, alternativ ein einfacher Tage-gewichteter
  Durchschnitt.
- Zinsswap-Bewertung (Festbein vs. variables Bein):
  - Festbein: `PV_fix = Σᵢ C·Δᵢ·Z(tᵢ)` (C = Fixkupon, Δᵢ = Accrual-Fraktion, Z = Diskontfaktor).
  - Variables Bein: `PV_float = Σᵢ fᵢ·Δᵢ·Z(tᵢ)` (fᵢ = Forward-Rate für Periode i, aus der
    Diskontkurve selbst impliziert über ein No-Arbitrage-Argument mit fiktiven Bond-Kassenflüssen).
  - **Par-Swap-Rate**: die Coupon-Rate C, bei der `PV_fix = PV_float`, also `PV = 0` bei Abschluss
    — der beim Handelsabschluss übliche Standardfall.
- Futures-Preis-Konvention für Zins-Futures: `Preis = 100 − Zinssatz` (steigt bei fallenden Zinsen).

## Zinskurven-Konstruktion

- Knotenpunkte typischerweise an Laufzeiten der Kalibrierungsinstrumente **oder** an
  Zentralbank-Sitzungsterminen (Tagessätze ändern sich nur an diesen Terminen materiell — ein
  "Constant-Daily-Forward"-Modell mit FOMC-Knoten bildet reale SOFR-Zeitreihen treppenförmig ab).
- Interpolationsmethoden: "Constant Daily Forward" (lokal, stufig, robust/schnell) vs. Cubic
  Spline (global, glatt, aber Hedges "verschmieren" über die gesamte Kurve). Trade-off: lokale,
  robuste Hedges vs. glatte, global-sensitive Hedges — je nach Anwendungsfall zu wählen.
- Kalibrierung als (ggf. gewichtetes) Least-Squares-Problem: Preis jedes Kalibrierungsinstruments
  als Funktion der vorgeschlagenen Kurve, Fehler minimieren; bei n Knoten = n Instrumenten exakt
  lösbar (Bootstrapping), sonst Least-Squares mit optionalen Glattheits-Zusatzbedingungen.

## Bezug zu diesem Projekt

- "Funding = Discounting" ist relevant für eine künftig präzisere `algo/pnl.py`-Behandlung von
  Übernachtfinanzierungskosten (Margin-Zinsen) bei gehaltenen MNQ-Futures-Positionen — aktuell
  laut `algo/README.md` nicht Teil des P&L-Modells.
- Zinskurven-Konstruktionsprinzipien (lokale vs. globale Interpolation, Knoten an
  strukturell bedeutsamen Zeitpunkten) sind konzeptionell auf `algo/rules.py` übertragbar, wenn
  dort künftig ICT-Killzone-/Macro-Zeitfenster als "Knotenpunkte" eines Intraday-Preismodells
  gedacht werden — allerdings **nur als Analogie**, kein direkt übernehmbarer Code.
- ⚠️ Nur sinnvoll, wenn direkt auf eine ausführbare `algo/rules.py`-Regel hinarbeitend — reine
  Zinskurven-PCA/-Fitting-Spielerei ohne MNQ-Bezug wäre Layer-0-Verstoß.
