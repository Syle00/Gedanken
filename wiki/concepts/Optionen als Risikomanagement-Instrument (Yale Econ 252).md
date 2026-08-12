---
tags: [concept, quant-finance, risikomanagement, optionen, yale-econ252]
created: 2026-08-12
updated: 2026-08-12
sources: ["[[2012-04-05 - Yale Econ 252 Lecture 17 - Options Markets (Source)]]"]
---

# Optionen als Risikomanagement-Instrument (Yale Econ 252)

Shillers Optionsvorlesung, fokussiert auf die Risikomanagement-Funktion von Optionen (nicht nur
Spekulation). Ergänzt die bestehende Herleitung in
[[Black-Scholes & Risikoneutrale Bewertung]] um die ökonomische Begründung, warum Optionsmärkte
gesamtwirtschaftlich wertvoll sind, plus die praktische Volatilitäts-Kennzahl VIX.

## Warum Optionsmärkte volkswirtschaftlich wichtig sind

- **Preisfindung für Zustände der Welt** (Kenneth Arrow, 1964 / Steven Ross, 1976): ohne
  Optionsmärkte fehlen Preise für bedingte Ereignisse ("was ist der Wert, wenn Zustand X
  eintritt?") — die Wirtschaft trifft dann Investitionsentscheidungen "blind". Praxisbeispiel im
  Kurs: eine Kaufoption auf ein Grundstück zwingt Käufer und Verkäufer, ihre implizite
  Preiseinschätzung offenzulegen, bevor eine reale Investition (Bau) erfolgt.
- **Verhaltensökonomische Funktion**: Mitarbeiteraktienoptionen wirken über **Salienz** (Kahneman/
  Tversky) — sie lenken Aufmerksamkeit auf den Firmenwert, auch wenn ihr ökonomischer Wert klein
  ist. Versicherung ist strukturell eine Put-Option (Hausbrand = Preis fällt auf 0) — der
  psychologische Nutzen ("peace of mind") ist Teil der Nachfrage, nicht nur die reine
  Erwartungswert-Absicherung.

## Formelwerk (Ergänzung zu Black-Scholes)

- **Put-Call-Parität**: `S = C − P + PV(Exercise Price) + PV(Dividenden)`. Erlaubt es, aus
  Call-Preisen direkt Put-Preise abzuleiten, ohne den Markt separat zu beobachten.
- **Binomialmodell (No-Arbitrage-Herleitung)**: mit Hedge-Ratio `H = (Cu − Cd) / [(u−d)·S]` lässt
  sich ein risikoloses Portfolio aus Aktie + Option konstruieren — der resultierende Optionspreis
  enthält **keine** Eintrittswahrscheinlichkeit, sondern folgt allein aus der No-Arbitrage-
  Bedingung. Zentrale Einsicht: Optionsbewertung braucht keine subjektive Wahrscheinlichkeits-
  schätzung, nur Volatilität, Zins und die Auszahlungsstruktur.
- **Amerikanische Calls werden nie vorzeitig ausgeübt** (Optionswert liegt vor Verfall stets über
  dem inneren Wert `max(S−E, 0)`) — bei amerikanischen Puts kann vorzeitige Ausübung dagegen unter
  bestimmten Umständen optimal sein.

## VIX / Implied Volatility als historisches Stressbarometer

- Implizite Volatilität (aus Black-Scholes rückwärts aus dem Marktpreis extrahiert) ist "die
  Meinung des Optionsmarktes über die künftige Volatilität" — im Gegensatz zur historischen
  (realisierten) Volatilität rein zukunftsgerichtet.
- Historische VIX-Spitzen: Crash 1987 (Sprung auf ~60 %), Asienkrise Mitte-1990er, Finanzkrise
  2008 (zweithöchster Wert nach der Weltwirtschaftskrise). Langzeitreihe der realisierten
  Volatilität (S&P Composite seit 1871) zeigt: außer der Weltwirtschaftskrise der 1930er ist die
  Aktienmarkt-Volatilität über 150 Jahre bemerkenswert stabil — die Finanzkrise 2008 war die
  zweitgrößte Ausnahme seit Beginn der Aufzeichnungen.

## Shillers eigener Risikomanagement-Vorschlag: strukturelle Put-Optionen für Häuser

- Shiller schlägt vor, Hypotheken standardmäßig mit eingebauten Put-Optionen auf den Hauswert zu
  koppeln ("Home Equity Insurance") — ein an der CME 2006 gestartetes Hauspreis-Futures-/
  Options-Experiment (auf Basis des Case-Shiller-Index) blieb allerdings illiquide und
  wirkungslos. Konkretes Beispiel dafür, dass ein theoretisch sinnvolles Risikomanagement-Produkt
  an mangelnder Marktakzeptanz scheitern kann.

## Bezug zu diesem Projekt

- Die No-Arbitrage-Herleitung (Optionswert unabhängig von subjektiver Erfolgswahrscheinlichkeit)
  ist eine methodische Erinnerung: Backtest-Kennzahlen, die implizit auf "geschätzten"
  Wahrscheinlichkeiten beruhen (statt auf beobachteten Preisstrukturen), sind fehleranfälliger als
  arbitragefreie Beziehungen — relevant für die Diskussion um
  [[Erwartungswert & Reward-to-Risk-Modell]].
- Der VIX als historisches Stressbarometer liefert eine zusätzliche externe Datenquelle
  (potenziell über FRED/CBOE abrufbar) für Regime-Erkennung, ergänzend zu den bereits genutzten
  Makro-Indikatoren in [[Makro-FRED-Zusammenhaenge (Eigene Daten, laufend)]].
