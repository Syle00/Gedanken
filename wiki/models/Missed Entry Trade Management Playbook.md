---
tags: [model, ict, trading-ict, 2026, execution]
created: 2026-08-01
updated: 2026-08-16
sources: ["[[Missed Entry How To Navigate The Same Trade Idea (Source)]]", "[[2026-07-02 - Missed Entry How To Navigate The Same Trade Idea (Source)|Missed Entry How To Navigate The Same Trade Idea (Source, Video)]]", "[[2026-08-04 - ICT Price Action Chronicles - Market On Close Macro (Source)|ICT Price Action Chronicles - Market On Close Macro (Source)]]", "[[2026-08-01 - Part 2 High Precision Secrets To Intraday Price Action (Source)|Part 2 High Precision Secrets To Intraday Price Action (Source)]]"]
---

# Missed Entry / Trade Management Playbook

Ablauf, wenn eine Limit-Order nicht gefüllt wird, plus generelles Skalierungs-/Exit-Schema.

## Warum es überhaupt zum Missed Entry kommt

> *„When your analysis is perfect, your executions could not execute. So **perfection will yield
> missed trades**. That's the oxymoron there."*
> — [[2026-07-02 - Missed Entry How To Navigate The Same Trade Idea (Source)|Videofassung]]

Der Missed Entry ist hier **kein Fehler**, sondern die systematische Nebenwirkung einer präzisen
Limit-Order: Sie liegt am bestmöglichen Punkt, und genau deshalb wird sie oft nicht erreicht. Im
dokumentierten Fall lag das Limit knapp über der C.E. des FVG, Preis lief bis exakt zum **Low des
FVG** — der **Spread** verhinderte den Fill. Daraus folgt die Grundhaltung des Playbooks: Der Plan
für den nicht erfolgten Fill wird **vorher** gefasst, nicht improvisiert.

## Vor dem Fill: Limit-Order-Disziplin

- **Nicht nachjagen.** *„Let it come to you. Don't chase it."* Auch bei feststehender Richtung wird
  nicht früher eingestiegen — ein zu früher Short kostet **needless drawdown**, wenn Preis noch
  einmal retraced.
- **Kein Fill-Zwang.** *„It's real important that you don't get crazy and think that you have to
  have the fill."* Der ausgebliebene Fill ist ein normaler Ausgang, kein Anlass zur Panik-Order.

## Entry

Bei verpasster Limit-Order: die **Wick als Entry** nutzen (bei einer Short-Idee die Premium-Wick).
Genutzt wird konkret das **Opening der Wick**.

**Alternative aus der Videofassung — Entry im Order Block**: Statt der Wick nutzte ICT die
**untere Hälfte des bearishen [[Order Block|Order Blocks]]**, also dessen
**Premium-Sensitivity-Hälfte** (*„notice my entries in the lower half of the order block on this
fill"*). Auslöser war ein [[CISD (Change in State of Delivery)|CISD]]: *„We have change in state
delivery right here. So I can do a short if it touches that."* Beide Wege sind derselbe Gedanke —
statt des perfekten Levels wird die nächstbeste PD Array in Richtung der Idee genommen.

## SL-Placement

SL zunächst auf den vorherigen gewollten Fill-Punkt, danach angepasst, sobald die bullishe Candle
als [[CISD (Change in State of Delivery)|CISD]]/[[Rejection Block]] identifiziert wird.

![[image 28.png]]
*SL-Anpassung nachdem die bullishe Candle als CISD/Rejection Block bestätigt wurde.*

> ✅ **Offene Frage geklärt (2026-08-16).** In der Notiz-Fassung
> [[Missed Entry How To Navigate The Same Trade Idea (Source)]] stand an dieser Stelle
> *„SL zieht ICT auf den vorherigen gewollten Fill (**verstehe ich noch nicht**)"*. Die
> [[2026-07-02 - Missed Entry How To Navigate The Same Trade Idea (Source)|Videofassung]] löst das
> auf — es sind **drei Stufen**, nicht eine:
>
> 1. **Initial über der [[Volume Imbalance (VII)|Volume Imbalance]]**, die über dem FVG liegt —
>    *„Stop loss above the volume balance."* Nicht „über dem gewollten Fill", sondern über der
>    nächsten PD Array darüber; der gewollte Fill lag lediglich in derselben Zone, daher die
>    Verwechslung in der Mitschrift.
> 2. **Auf den [[Rejection Block]]**, sobald dieser sich gebildet hat — ausdrücklich als
>    Risikoreduktion: *„I'll use a rejection block on this. **Reduce some of the stop risk**."*
> 3. **Weiter nachgezogen** über das jeweils neue Hoch: *„I'll lower the stop down just above this
>    high."*
>
> Das Risiko bleibt zwischen Stufe 2 und dem ersten Partial **unverändert** (*„I'll hold the risk
> at 1920 till I get first partial"*) — erst der Teilgewinn löst das weitere Nachziehen aus, nicht
> die reine Preisbewegung.

## Reentry / Skalierung

- **1. Reentry**: den CISD-Rejection-Block nutzen, um die Position zu vergrößern (z.B. um die
  Hälfte der aktuellen Positionsgröße).
- **2. Reentry**: weitere Positionen über denselben CISD aufbauen, z.B. wenn man sich in der
  NY-AM-Silver-Bullet befindet und der gesamte vorherige Move nach oben als [[Judas Swing|Judas]]
  mit sauber hinterlassener Sellside als Ziel erkannt wird.

## Target & Exit

- Immer ein **klares, einfaches Target** definieren — idealerweise gestackte Liquidity.
- **1. Exit**: der bereits ausgemalte [[AMD Cycle (Accumulation – Manipulation – Distribution)|DOL]],
  SL danach weit ins Plus nachziehen.
- **2. Exit**: nach Erreichen des DOL den [[Event Horizon]] nutzen, um weitere Partials zu sichern
  (TP-Erreichen ist Best-Case, kein Muss).
- **Last Exit**: fällt das anschließende Retracement zu stark aus (subjektive Einschätzung), wird
  die gesamte Position geschlossen.

### Skalierungs-Details und die Re-Entry-Sperre (Videofassung)

- **Staffelung**: dreimal 3 Kontrakte abgebaut, 6 als Runner gehalten, zum Schluss einzelne
  Kontrakte. Die Partials hängen an den Ziel-Leveln, nicht an R-Vielfachen — vgl.
  [[Partial Profit-Taking & R-Multiple-Skalierung]].
- **Ziel-Staffel**: Relative Equal Lows als Best Case, davor zwei Zwischen-Lows als
  Zwischenstationen (siehe [[Open Float & Liquidity Pools]]).
- **Partial *vor* dem [[Event Horizon]]**, wenn dieser knapp unter einem alten Low liegt —
  Begründung auf der Event-Horizon-Seite.
- **Harte Re-Entry-Sperre nach dem Ausstieg.** Die wichtigste Disziplinregel des Videos: Ist die
  Position geschlossen, wird **nicht** wieder eingestiegen, auch wenn die Bewegung sichtbar
  weiterläuft:
  > *„I can't reenter it. Even if this thing drops down into 29,230s. I can't do it. **There has to
  > be rules.**"*
  Begründung: Die Idee war „long in the tooth" — zeitlich und strukturell ausgereizt. Ein Re-Entry
  wäre ein *neuer* Trade ohne eigenes Setup, nur getrieben davon, den Rest der Bewegung nicht zu
  verpassen.
- **Vorzeitiger Komplettausstieg** ist explizit erlaubt und wurde hier genutzt: *„Too much of a
  retracement on my part for the trade I was in."* — deckt sich mit „Last Exit" oben.

### Kontext-Filter: Feiertagsvolumen

ICT weist während der laufenden Ausführung ungefragt darauf hin, dass der 2. Juli (vor dem 4. Juli)
**Feiertagsvolumen** hat: *„It's holiday volume, by the way. So yeah, things can get squirrely."*
Erwartungsmanagement statt Setup-Kriterium — die Regeln bleiben gleich, die Erwartung an sauberes
Verhalten sinkt.

## Exit-Präzision vs. Entry-Präzision (2026-Ergänzung, MOC-Video)

- **Exit-Präzision ist unwichtiger als Entry-Präzision**: Teilgewinne bereits **über** 50 % der
  erwarteten Range zu nehmen zählt laut ICT bereits als "Präzision" — nicht das exakte Tick-Ziel zu
  treffen.
- **SL-Anker an High-Probability-Wicks statt Tick-genauer Level**: SL wird an eine Wick gehängt, die
  über mehrere Fib-Level (Oktant **und** Quadrant) bestätigt ist, plus 1–2 Ticks — mit bewusster
  Toleranz für Drawdown, solange die Wick-Bodies die Zone respektieren.
- Stop-outs und verpasste Moves sind **Lerngelegenheiten**, kein Grund, das Setup infrage zu stellen
  — man wird nicht besser dadurch, dass Trades aufgehen, sondern durch die Analyse, was beim
  Verfehlen übersehen wurde.

## Single-Contract-Probe + Pyramiding in Drawdown (2026-Ergänzung)

- **Entry-Test**: vor dem eigentlichen Aufbau einen einzelnen (Mikro-)Kontrakt am oberen Quadranten/
  Midpoint einer Referenz-Wick platzieren (siehe [[Institutional Order Flow (Body vs Wick)]]).
- **Pyramiding in Drawdown erlaubt**: läuft Preis zunächst gegen die Position, aber bleibt der Wick-
  Bereich respektiert, wird an tieferen Wick-Leveln **nachgekauft/-verkauft** — ausdrücklich auch
  während die erste Teilposition im Minus steht. Nicht mit den meisten Prop-Firm-Regeln vereinbar,
  ICT selbst handelt ohne Prop-Firm-Constraints.
- **SL-Nachziehen in Stufen**: initial oberhalb C.E. der Entry-Wick → sobald Preis unter das Low der
  Entry-Candle closed, SL auf C.E. des genutzten FVG → danach weiter Richtung High der Struktur
  nachziehen, bis das erste Ziel (Half Gap) erreicht ist.
- **Volatilitäts-Faustregel**: ist der nötige SL-Abstand an einem hochvolatilen Tag entsprechend groß,
  auf **Micro-Kontrakte** ausweichen statt die Positionsgröße/den Stop zu verzerren.

## Verwandt

- [[Event Horizon]], [[CISD (Change in State of Delivery)]], [[Rejection Block]]
- [[Judas Swing]]
- [[Market on Close (MOC) Macro Model]]
- [[Institutional Order Flow (Body vs Wick)]], [[ORG (Opening Range Gap) & 1st Presented FVG]]
- [[2026-08-01 - Part 2 High Precision Secrets To Intraday Price Action (Source)|Part 2 High Precision Secrets To Intraday Price Action (Source)]]
