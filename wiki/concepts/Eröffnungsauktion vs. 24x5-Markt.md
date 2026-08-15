---
tags: [concept, ict, forex, futures]
created: 2026-08-15
updated: 2026-08-15
sources: []
---

# Eröffnungsauktion vs. 24x5-Markt

Futures (MNQ, ES, ...) haben einen täglichen Handelsschluss und eine Wiedereröffnung (bei MNQ:
17:00 NY Schluss, 18:00 NY Globex-Reopen). Genau dieser Schluss-/Eröffnungswechsel erzeugt die
Konzepte, die auf ihm aufbauen:

- [[ORG (Opening Range Gap) & 1st Presented FVG]] — Gap zwischen Vortagesschluss (~16:14) und
  9:30-Eröffnung.
- [[New Day Opening Gap (NDOG)]] — Gap zwischen letztem Kerzen-Close und erster Kerze des Tages.
- Das "erste FVG nach 9:30" und der Open Drive setzen ebenfalls eine Eröffnungsauktion voraus.

Forex-Paare (EURUSD, GBPUSD, ...) handeln 24x5 durchgehend (So 17:01 NY bis Fr 17:00 NY) — es
gibt keinen täglichen Schluss, also strukturell **kein** ORG, **kein** NDOG und **kein** "erstes
FVG nach 9:30" im ICT-Sinn. Was in Forex weiterhin existiert: das **[[New Week Opening Gap (NWOG)
Bias|NWOG]]** — der reale Wochenend-Gap zwischen Freitagsschluss und Sonntagsöffnung.

**Implementierung:** `tools/analyze_ohlc.py::SESSION_TYP` markiert jedes Symbol als
`futures_rth` oder `24x5`; `org_gap()`/`ndog_gap()` liefern für `24x5`-Symbole `None`, statt
eine plausibel aussehende, aber bedeutungslose Zahl zu berechnen (siehe
`docs/superpowers/specs/2026-08-14-forex-backtesting-design.md` §4).

Nutzerkorrektur, die diese Unterscheidung ausgelöst hat (2026-08-14): *"in forex gibt es kein
opening range gap ... ndog gibt es nicht aber nwog gibt es."*
