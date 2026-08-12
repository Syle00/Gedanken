---
tags: [concept, quant-finance, risikomanagement, zinstheorie, leverage, yale-econ252]
created: 2026-08-12
updated: 2026-08-12
sources: ["[[2012-04-05 - Yale Econ 252 Lecture 08 - Theory of Debt, Its Proper Role, Leverage Cycles (Source)]]"]
---

# Fisher-Zinstheorie & Leverage-Zyklen (Yale Econ 252)

Shillers Herleitung der Irving-Fisher-Zinstheorie (1930) plus Diskussion von Verschuldung/Usury.
**Risikomanagement-relevant** wegen der Leverage-Diskussion, die strukturell mit
[[Kelly-Formel & optimales Leverage (Chan)]] und den Kelly/CPPI-Seiten dieses Vaults verwandt ist.

## Drei Ursachen des Zinssatzes (von Böhm-Bawerk, formalisiert von Fisher)

1. **Technischer Fortschritt**: Produktivitätssteigerung erlaubt höhere reale Renditen.
2. **Umwegproduktivität** ("roundaboutness"): mehr Zeit erlaubt produktivere (indirekte)
   Produktionsverfahren.
3. **Zeitpräferenz**: Menschen bevorzugen Konsum heute gegenüber morgen (Ungeduld).
- Fishers Zwei-Perioden-Modell (Konsum heute vs. morgen, Produktionsmöglichkeitengrenze ×
  Indifferenzkurven-Tangente) zeigt formal: der Marktzins ergibt sich aus dem Zusammenspiel von
  Technologie (Produktionsmöglichkeitengrenze) **und** Präferenzen (Indifferenzkurven) — weder
  allein reicht als Erklärung.

## Präsentwert-Formelwerk (direkt übertragbar)

- Diskontanleihe: `P = 100 / (1+r)^T`.
- Perpetuität/Konsol: `PV = Coupon / r`.
- Annuität: `PV = (x/r)·[1 − 1/(1+r)^T]` — Grundlage jeder Hypothekenberechnung.
- Forward Rate (Hicks 1939): `1+f = (1+r₂)²/(1+r₁)` — aus der Zinsstrukturkurve implizit
  ableitbar, Erwartungstheorie der Zinsstruktur: `Forward Rate ≈ erwarteter künftiger Spot-Zins +
  Risikoprämie`.

## Leverage — mechanisches Grundmodell

- Zwei-Asset-Fall (riskante Anlage + risikoloser Zins): Verdoppelung des Kapitaleinsatzes über
  Kredit verdoppelt sowohl erwartete Überrendite als auch Standardabweichung — eine
  gebrochene Gerade im Risiko-Rendite-Diagramm (Grundlage der Capital-Allocation-Line, siehe
  [[Markowitz-Portfoliotheorie & Diversifikation (Yale Econ 252)]]).
- Historisches Beispiel VOC (1602): frühester dokumentierter Short-Seller-Skandal (Isaac Le Maire,
  1609) — Leerverkauf drückt Preise, Amsterdamer Börse verbot Short-Selling 2 Jahre lang (1609–
  1611), dann wieder freigegeben. Frühestes Beispiel für regulatorische Reaktion auf
  Leverage-/Leerverkaufsrisiko.

## Usury/Verschuldungs-Ethik als Risikomanagement-Frage

- Historische Kreditverbote (biblisch/koranisch) als frühe, unpräzise Regulierung gegen
  ausbeuterische Kreditvergabe — Kernproblem bis heute ungelöst: wann ist ein Kredit sinnvolle
  Konsumglättung (Fisher-Modell, "beide Seiten profitieren"), wann ausbeuterisches "Predatory
  Lending"? Elizabeth Warrens Kritik (führte zur Gründung des Consumer Financial Protection Bureau
  im Dodd-Frank Act) als moderne Fortsetzung derselben Debatte.

## Bezug zu diesem Projekt

- Die Forward-Rate-/Zinsstruktur-Formeln ergänzen bereits vorhandenes quant-finance-Material
  ([[Bond-Mathematik & Zinskurven]]) um die historische Herleitung — kein neuer Formelbedarf für
  `algo/`, da MNQ keine Zinsprodukt-Bewertung braucht, aber relevant für makroökonomische
  Kontext-Features (Zinsstruktur als Regime-Indikator, vgl.
  [[Makro-FRED-Zusammenhaenge (Eigene Daten, laufend)]]).
- Das Leverage-Grunddiagramm (Rendite/Risiko linear mit Hebel) bestätigt algebraisch, warum
  Positionsgrößen-Regeln wie [[Risikomanagement (1% pro Trade)]] und
  [[Kelly-Formel & optimales Leverage (Chan)]] notwendig sind: ohne explizite Hebel-Obergrenze
  lässt sich mit MNQ-Futures (bereits gehebelt über die Kontraktstruktur) jede beliebige erwartete
  Rendite bei proportional steigendem Ruinrisiko konstruieren.
