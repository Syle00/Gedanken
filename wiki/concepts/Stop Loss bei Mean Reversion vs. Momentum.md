---
tags: [concept, algo-methodology, risikomanagement, stoploss, referenz]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[Algorithmic Trading - Winning Strategies and Their Rationale (Source)]]"]
---

# Stop Loss bei Mean Reversion vs. Momentum

Warum derselbe Stop Loss bei der einen Strategieklasse logisch zwingend und bei der anderen ein
Widerspruch in sich ist — und wie man ihn trotzdem einsetzt. Aus
[[Algorithmic Trading - Winning Strategies and Their Rationale (Source)]] (Chan, Kap. 8).

## Zwei verschiedene Dinge, die „Stop Loss" heißen

| Variante | Was passiert | Bewertung |
|---|---|---|
| **Positions-Stop** (üblich) | einzelne Position schließen, wenn ihr unrealisierter Verlust eine Schwelle unterschreitet. Danach darf man **neu einsteigen**, auch in dieselbe Richtung. Kumulierter P&L/Drawdown der Strategie spielt keine Rolle. | Gegenstand dieser Seite |
| **Strategie-Stop** (selten) | die gesamte Strategie abschalten, wenn der Drawdown eine Schwelle unterschreitet. | „Awkward" — kann im Leben einer Strategie nur **einmal** feuern, und idealerweise nie. Deshalb ist [[CPPI (Constant Proportion Portfolio Insurance)]] dafür vorzuziehen. |

## Wann ein Stop Loss überhaupt funktioniert

Ein Stop Loss begrenzt den unrealisierten Verlust **nur dann** zuverlässig, wenn der Markt
durchgehend offen ist, solange man eine Position hält. Also: kein Halten über den Marktschluss,
oder Handel in Devisen/Futures mit fast durchgehendem elektronischem Handel (außer Wochenenden
und Feiertagen).

Sonst gilt: **Gapt der Preis bei Wiedereröffnung, wird der Stop zu einem viel schlechteren Kurs
ausgeführt**, als die eigene Verlustgrenze vorsah. Das einzige Gegenmittel sind Optionen, die
aber teuer sind und sich nur bei planbarer Handelspause lohnen.

Und selbst bei offenem Markt kann der Stop wertlos werden, wenn **alle Liquiditätsanbieter
gleichzeitig aussteigen**. Beim Flash Crash am 6. Mai 2010 mussten Market Maker lediglich ein Gebot
von $0,01 stellen (die berüchtigte „stub quote") — eine Verkaufs-Stop-Order auf Accenture, ein
Unternehmen mit Milliardenumsatz, wurde an diesem Tag zu **$0,01 je Aktie** ausgeführt.

## Momentum: Stop Loss ist logisch Teil der Strategie

Verliert eine Momentum-Position, **hat sich das Momentum umgekehrt** — also ist Aussteigen genau
das, was die Strategielogik ohnehin verlangt, möglicherweise sogar Umdrehen der Position.

Daraus folgt: **ein laufend aktualisiertes Momentum-Signal ist bereits ein De-facto-Stop-Loss.**

Chan zählt Stop Losses deshalb zu den *Vorteilen* von Momentum-Strategien. Die beiden üblichen
Exit-Typen sind zeitbasiert (feste Haltedauer) und Stop Loss — beide begrenzen den Verlust
**einer** Position zuverlässig. Konsequenz: Momentum-Modelle haben **nicht** das Tail-Risiko von
Mean-Reversion-Modellen.

> Die Einschränkung, die Chan selbst anfügt: Das heißt nicht, dass die *kumulierten* Verluste
> vieler aufeinanderfolgender Verlust-Trades einen nicht ruinieren können.

## Mean Reversion: der eingebaute Widerspruch

Bei Mean Reversion widerspricht der Stop Loss der Einstiegslogik direkt: Fällt der Preis und man
geht long, fällt weiter und erzeugt Verlust — dann **erwartet man ja gerade den Anstieg**. Genau
dort auszusteigen ist unsinnig.

> *„Indeed, I have never backtested any mean-reverting strategy whose APR or Sharpe ratio is
> increased by imposing a stop loss."*

**Aber:** Dieser Satz enthält einen Denkfehler, den Chan selbst aufdeckt.

### Das Survivorship-Bias-Argument

Was passiert, wenn das Mean-Reversion-Modell **dauerhaft aufhört zu funktionieren**, während man
in einer Position sitzt? In der Finanzwelt sind Gesetze nicht unveränderlich: Eine
mean-revertierende Preisreihe kann einen **Regimewechsel** durchlaufen und für längere Zeit —
vielleicht für immer — trendend werden.

Und solche „Überläufer"-Reihen tauchen im eigenen Katalog profitabler Mean-Reversion-Strategien
**nie auf**, weil dieser Katalog nur Strategien enthält, die den Backtest bestanden haben.

> **Präzisierte Aussage:** Ein Stop Loss senkt die Performance von Mean-Reversion-Strategien
> **immer dann, wenn die Preise mean-revertierend bleiben** — und er verbessert sie **immer
> dann, wenn ein Regimewechsel zum Trend stattfindet.** Der pauschale Satz „Stop Loss schadet
> Mean Reversion" ist selbst ein Survivorship-Bias-Artefakt.

### Die praktische Auflösung

Da jede erfolgreich gebacktestete Mean-Reversion-Strategie diesem Bias unterliegt und mit Stop
Loss immer schlechter aussehen wird:

> **Setze den Stop Loss GRÖSSER als den maximalen Intraday-Drawdown des Backtests.**

Dann hätte er im Backtestzeitraum **nie ausgelöst** und kann die Backtest-Performance
definitionsgemäß nicht verschlechtert haben — verhindert aber trotzdem, dass ein künftiges
Black-Swan-Ereignis zum Ruin führt.

Das ist die praktisch wertvollste Einzelregel dieses Kapitels: eine Stop-Loss-Dimensionierung,
die **kostenlos** ist (kein Backtest-Verlust) und gleichzeitig das Katastrophenrisiko abschneidet.

## Warum Mean Reversion besonders gefährdet ist

Aus Kapitel 2, aber hier einschlägig: Gerade die **scheinbar hohe Konsistenz** von
Mean-Reversion-Strategien führt zu Überkonfidenz und in der Folge zu Überhebelung (Dever; man
denke an LTCM). Bricht eine solche Strategie plötzlich zusammen — oft aus einem Grund, der erst
im Rückblick erkennbar ist —, passiert das typischerweise, **während man nach einer ununterbrochenen
Serie von Gewinnen mit maximalem Leverage handelt**. Der seltene Verlust ist deshalb besonders
schmerzhaft und manchmal katastrophal.

## Bezug zu diesem Projekt

`algo/rules.py::plan_trade` (Silver Bullet) ist eine **Momentum-artige** Regel: Entry nach
Displacement in Richtung des Bias, Stop hinter der FVG-Gegenkante. Nach diesem Kapitel ist der
Stop dort **logisch konsistent** — er ist Teil der Strategie, nicht ein Fremdkörper.

Zwei konkrete Anschlusspunkte:

1. Der Stop-Puffer (10 % der FVG-Größe) war laut `algo/PLAN.md` oft **kleiner als das Rauschen
   einer einzelnen 5m-Kerze** und erzeugte massenhaft „dubious" Trades. Das ist das Gegenteil des
   hier empfohlenen Vorgehens — und die Sensitivitätsanalyse in `backtest_walkforward.py` prüft
   genau diese Größe.
2. Für **jede künftige Mean-Reversion-Regel** im Vault (etwa aus den ICT-Konzepten zu Rückkehr in
   FVGs oder zur Midnight Range) gilt die Regel oben: Stop größer als der maximale
   Intraday-Drawdown des Backtests ansetzen.

Wichtig für MNQ speziell: Futures handeln nahezu durchgehend, aber **nicht** über das Wochenende
und nicht während der täglichen Pause — der Gap-Vorbehalt oben gilt also. Das deckt sich mit den
ICT-Konzepten [[New Week Opening Gap (NWOG) Bias]] und
[[ORG (Opening Range Gap) & 1st Presented FVG]], die genau diese Lücken zum Thema haben.

Weiterführend: [[CPPI (Constant Proportion Portfolio Insurance)]] als das überlegene Instrument
für den Strategie-Stop, [[Kelly-Formel & optimales Leverage (Chan)]] für die Hebelfrage,
[[Leading Risk Indicators]] für den proaktiven statt reaktiven Ansatz.
