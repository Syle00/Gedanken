---
tags: [concept, algo-methodology, validation]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[Claude Opus 5 + MCP = New King of Algo Trading! (Source)]]"]
---

# Rule Significance Test (RST)

Validierungsschritt, der **nur die reine Entry-Regel** einer Strategie auf statistische
Signifikanz gegen Zufall/Rauschen prüft — bevor Position-Sizing, Stop-Loss oder Zielsetzung
überhaupt entworfen werden. Aus [[Claude Opus 5 + MCP = New King of Algo Trading! (Source)]]
(Jesse-Framework-Feature, dort ohne offengelegte interne Formel gezeigt).

## Grundidee

Reihenfolge-Prinzip, nicht ein spezifischer Algorithmus: teste zuerst, ob das Entry-Signal
(long/short/flat) überhaupt eine Vorhersagekraft hat, die über Zufall hinausgeht — erst danach
lohnt sich jeder weitere Entwicklungsaufwand (Sizing, Exits, Optimierung). Begründung aus der
Quelle wörtlich: "if the entry rules of the strategy don't have an actual edge, then everything
else that we do is pointless." Fällt der Test durch, wird die Regel verworfen, ohne Zeit in
Sizing/Stop/Ziel-Feintuning zu investieren, das das eigentliche Problem (kein Signal) nur
kaschieren würde.

## Abgrenzung zu bestehenden Verfahren in diesem Vault

- **Nicht dasselbe wie [[Monte Carlo Permutation Test (MCPT)]]**: MCPT testet die VOLLSTÄNDIGE,
  bereits optimierte Strategie gegen permutierte Preisdaten (Data-Mining-Bias der Optimierung).
  RST testet nur das rohe Entry-Signal, bevor überhaupt optimiert oder eine vollständige Strategie
  gebaut wurde — ein Schritt davor.
- **Nicht dasselbe wie `algo/validate.py::monte_carlo()`**: das ist Trade-Order-Resampling einer
  bereits fertigen Trade-Liste, setzt also voraus, dass Entry+Exit+Sizing schon existieren.
- Passt zeitlich VOR Stufe 1 ("In-Sample Excellence") von
  [[Vier-Stufen-Strategieentwicklung (Masters)]] — ein zusätzlicher, noch früherer Filter, den
  das Masters-Verfahren in dieser Form nicht kennt.

## Bezug zu diesem Projekt

`algo/rules.py::plan_trade()` und `algo/backtest_bt.py` testen aktuell direkt die vollständige
`TradeSetup`-Regel (Entry+Stop+Ziel zusammen) — es gibt noch keinen isolierten Test nur des
Entry-Triggers (z.B. "FVG im Silver-Bullet-Fenster" für sich genommen, ohne Stop/Ziel-Logik).
Kein akuter Backlog-Punkt, aber ein möglicher zusätzlicher Frühfilter für künftige neue Regeln,
bevor der volle `backtest_bt.py`/`validate.py`-Aufwand investiert wird — insbesondere relevant,
da mehrere bisherige `algo/backtest_*.py`-Läufe erst nach vollständiger Implementierung robust
negative Erwartung zeigten (siehe `algo/PLAN.md`-Log 2026-08-05, Silver-Bullet-Basisregel).
