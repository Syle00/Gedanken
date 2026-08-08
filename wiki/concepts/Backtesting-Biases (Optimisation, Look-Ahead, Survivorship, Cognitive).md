---
tags: [concept, algo-methodology, validation]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[Successful Algorithmic Trading (Source)]]"]
---

# Backtesting-Biases (Optimisation, Look-Ahead, Survivorship, Cognitive)

Katalog der vier wichtigsten systematischen Verzerrungen, die einen Backtest **immer optimistischer
erscheinen lassen, als die Strategie live tatsächlich ist**. Aus
[[Successful Algorithmic Trading (Source)]] (Michael Halls-Moore). Grundregel: ein Backtest ist
bestenfalls eine idealisierte Obergrenze der echten Performance, nie eine Punktschätzung.

## 1. Optimisation Bias (Curve-Fitting / Data-Snooping)

Parameter werden so lange angepasst, bis die Backtest-Performance attraktiv aussieht — live
verhält sich die Strategie dann oft deutlich anders. Je mehr Parameter (Entry/Exit-Kriterien,
Lookbacks, Glättungsperioden, Volatilitätsfenster), desto größer das Risiko. Gegenmaßnahmen:
möglichst wenige Parameter, möglichst viele Datenpunkte im Trainingsset (mit Vorsicht — ältere
Daten können aus einem anderen Marktregime stammen und irrelevant sein). Konkretes Werkzeug:
**Sensitivitätsanalyse** — Parameter systematisch variieren und die Performance als "Fläche"
plotten. Eine glatte Fläche deutet auf ein echtes Phänomen hin, eine sehr sprunghafte Fläche
darauf, dass ein Parameter nur ein Artefakt der Testdaten ist statt eines echten Effekts.

## 2. Look-Ahead Bias

Zukunftsdaten fließen versehentlich in einen Zeitpunkt der Simulation ein, an dem sie real noch
nicht verfügbar gewesen wären. Drei konkrete, oft subtile Fehlerquellen:

- **Technical Bugs** — Off-by-one-Fehler bei Array-/Vektor-Indizes.
- **Parameter-Berechnung auf dem Gesamtdatensatz** — z.B. eine lineare Regression zwischen zwei
  Zeitreihen wird auf dem kompletten Datensatz (inkl. Zukunft) berechnet und dann rückwirkend
  als Strategie-Parameter verwendet.
- **Ungelaggte Maxima/Minima** — High/Low einer Periode stehen erst am Periodenende fest; werden
  sie WÄHREND der laufenden Periode verwendet, entsteht Look-Ahead. Muss immer um mindestens eine
  Periode verzögert werden.

Gilt als häufigster Grund, warum eine Strategie live deutlich schlechter performt als im
Backtest. Deckt sich mit der bereits etablierten Projektregel "kein Lookahead, nur
`bars[t<=when]`" ([[Algo-Trading: Arbeitsstandards]]) — dieser Katalog liefert die konkreten
Fehlerklassen dazu, gegen die jeder neue Detektor/jede neue Regel geprüft werden sollte.

## 3. Survivorship Bias

Entsteht, wenn ein Backtest nur auf Assets läuft, die bis heute "überlebt" haben (z.B.
Aktienauswahl vor/nach einer Krise, ohne die zwischenzeitlich pleitegegangenen Unternehmen).
Eigentlich ein Spezialfall von Look-Ahead-Bias — man nutzt implizit das Wissen, welche Assets
später erfolgreich waren. Explizit genannt: **Yahoo-Finance-Daten sind NICHT
survivorship-bias-frei**. Gegenmaßnahmen: teure survivorship-bias-freie Datensätze kaufen, auf
Asset-Klassen ausweichen, die davon nicht betroffen sind (z.B. bestimmte Rohstoffe/Futures), oder
selbst ab sofort survivorship-bias-freie Daten sammeln (nach 3-4 Jahren hat man einen solchen
Datensatz).

## 4. Cognitive Bias

Der einzige explizit **psychologische** Bias in der Liste, im Kontext von quantitativem statt
diskretionärem Trading selten diskutiert. Ein Backtest über mehrere Jahre mit einem
Maximum-Drawdown von z.B. 25% über 4 Monate wirkt am Papier erträglich — live ist ein
gleich großer Drawdown psychologisch weit schwerer auszuhalten. Der Bias entsteht dadurch, dass
eine eigentlich erfolgreiche Strategie während einer echten Drawdown-Phase abgeschaltet wird,
obwohl genau diese Phase im Backtest bereits vorhergesagt war — die Strategie "verliert" dadurch
nicht am Modell, sondern an der eigenen Reaktion darauf. Konsequenz: Backtest-Drawdown-Größe und
-Dauer sollten als reale Erwartung für Live-Betrieb verstanden werden, nicht als Papierwert.

## Bezug zu diesem Projekt

Ergänzt/systematisiert die bereits etablierten Standards aus
[[Algo-Trading: Arbeitsstandards]] und [[Vier-Stufen-Strategieentwicklung (Masters)]]: Punkt 1
(Optimisation Bias) wird bereits durch Walk-Forward/Parameter-Sensitivität in `algo/validate.py`
adressiert, Punkt 2 (Look-Ahead) durch die bestehende `bars[t<=when]`-Regel. Punkt 3
(Survivorship Bias) betrifft dieses Projekt kaum, da MNQ ein einzelnes, durchgängig existierendes
Instrument ist, keine Aktienauswahl aus einem Universum. Punkt 4 (Cognitive Bias) ist bisher
nirgends im Vault dokumentiert — relevant für die spätere Live-Phase (Roadmap-Punkt 5+6 in
[[Algo-Trading: Roadmap zur IBKR-Anbindung]]): ein Backtest-Drawdown wie der aus dem
2026-08-05-Walk-Forward-Log (bis zu -3,50% kumuliert über 5 Folds) sollte als reale
Live-Erwartung behandelt werden, nicht als bloße Kennzahl.
