---
tags: [concept, quant-finance, risikomanagement, futures, yale-econ252]
created: 2026-08-12
updated: 2026-08-12
sources: ["[[2012-04-05 - Yale Econ 252 Lecture 15 - Forward and Futures Markets (Source)]]"]
---

# Forward- & Futures-Märkte (Contango, Backwardation, Yale Econ 252)

Shillers Vorlesung zu Futures-Märkten, historisch hergeleitet vom japanischen Reismarkt in Dojima
(1673) bis zu modernen Index-Futures. Besonders relevant für dieses Projekt, weil MNQ selbst ein
Future ist — dieser Ingest ergänzt die Mechanik hinter dem gehandelten Instrument.

## Warum Futures Forwards ablösten: Gegenparteirisiko

- Forward-Kontrakte (bilateral, individuell) leiden unter **Gegenparteirisiko** — eine Seite kann
  bei Preisänderung den Vertrag brechen. Futures-Börsen lösen das durch standardisierte Kontrakte
  + **tägliche Margin-Abrechnung (Mark-to-Market)**: Verluste/Gewinne werden täglich verrechnet,
  bei unzureichender Margin schließt der Broker die Position automatisch — die Gegenpartei ist
  effektiv die Börse selbst, nicht der ursprüngliche Handelspartner.
- Historische Kuriosität: erste bekannte Futures-Börse war Dojima/Osaka (1673, Reis) — feste
  Handelszeiten wurden durch eine brennende Zündschnur signalisiert, Nachzügler wurden mit
  Wassereimern verjagt; Handzeichen ersetzten Zurufe bei zu hohem Lärmpegel.

## Contango vs. Backwardation — das Fair-Value-Modell

- **Grundformel (Lagerkosten-Modell)**: `Futures-Preis = (1 + r + s) × Kassapreis`, wobei `r` der
  Zins bis zur Fälligkeit und `s` die Lagerkosten sind. Bei positiven Lagerkosten ist der
  Futures-Preis normalerweise über dem Kassapreis — **Contango**.
- **Backwardation** (Futures-Preis fällt mit der Laufzeit): tritt auf, wenn niemand das
  zugrunde liegende Gut aktiv für die Zukunft einlagern will — z. B. Öl-Futures während einer
  akuten Angebotskrise (Kurs im Beispiel des Kurses: 2011er Ölkurve mit Spitze im Dezember 2011,
  danach fallend bis 2015 — Markterwartung, dass die damalige Nahost-Krise sich bis dahin auflöst).
  Erklärt über den Begriff **Convenience Yield**: wer physisch produzieren/verbrauchen muss
  (Raffinerie), hält Bestände auch bei Backwardation, weil ein leerer Tank Produktionsausfälle
  riskiert — das entspricht effektiv negativen Lagerkosten.
- **Finanz-/Index-Futures-Sonderfall**: `Futures-Preis = (1 + r − y) × Kassapreis`, wobei `y` die
  Dividendenrendite ist (negative "Lagerkosten", weil Aktien Dividenden zahlen statt Lagerkosten zu
  verursachen). Für Aktienindex-Futures ist die Fair-Value-Beziehung fast immer sehr genau erfüllt
  (kein physisches Lagerproblem) — der Futures-Kurvenverlauf selbst enthält daher **kaum**
  zusätzliche Prognoseinformation über den künftigen Indexstand.

## Ölpreis-Geschichte (1871–heute) als Fallstudie für strukturelle Regimewechsel

- Stabile Ölpreise 1940er–1973 durch die Texas Railroad Commission (Quasi-Kartell); Zusammenbruch
  dieser Stabilisierung + OPEC-Gründung (1961ff.) führte zur ersten Ölkrise 1973/74 (Jom-Kippur-
  Krieg, Embargo) — Auslöser für die Entstehung moderner Öl-Futures-Märkte. Zweite Ölkrise 1979/80
  (iranische Revolution). Jede der großen Ölpreis-Spitzen (1973, 1979/80, 2003 Irak-Krieg, 2008)
  fiel mit einer Weltrezession zusammen.

## Bezug zu diesem Projekt

- Direkt anschlussfähig an [[Kontraktspezifikation MNQ (Tick, Punktwert)]]: die
  Fair-Value-Formel für Index-Futures erklärt, warum MNQ nahe am Kassaindex (NQ/Nasdaq-100) notiert
  und der Roll-Effekt zwischen Kontrakten (Front-Month vs. nächster Verfall) systematisch klein,
  aber nicht null ist — relevant für `algo/fetch_yfinance.py`-Datenpflege bei Kontraktwechseln.
- Die Contango/Backwardation-Logik ist konzeptionell verwandt mit
  [[Roll Return, Contango & Backwardation]] (bereits im Vault, aus Chan-Buch) — diese Vorlesung
  liefert die intuitive/historische Herleitung derselben Mechanik, kein neuer Formelbedarf, aber
  gute Zusatzquelle für die Erklärung im README oder bei Nutzerfragen zu Rollover-Effekten.
- Margin-Mark-to-Market-Mechanik ist die Basis jeder korrekten Punktwert-P&L-Simulation in
  `algo/pnl.py` — bestätigt indirekt, warum das Projekt zurecht "echten Punktwert statt
  Notional-Prozent" als Pflichtstandard führt (siehe Algo-Trading-Arbeitsstandards).
