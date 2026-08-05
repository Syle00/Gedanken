---
tags: [model, ict, trading-ict, 2026, execution]
created: 2026-08-01
updated: 2026-08-05
sources: ["[[Missed Entry How To Navigate The Same Trade Idea (Source)]]", "[[ICT Price Action Chronicles - Market On Close Macro (Source)]]", "[[Part 2 High Precision Secrets To Intraday Price Action (Source)]]"]
---

# Missed Entry / Trade Management Playbook

Ablauf, wenn eine Limit-Order nicht gefüllt wird, plus generelles Skalierungs-/Exit-Schema.

## Entry

Bei verpasster Limit-Order: die **Wick als Entry** nutzen (bei einer Short-Idee die Premium-Wick).
Genutzt wird konkret das **Opening der Wick**.

## SL-Placement

SL zunächst auf den vorherigen gewollten Fill-Punkt, danach angepasst, sobald die bullishe Candle
als [[CISD (Change in State of Delivery)|CISD]]/[[Rejection Block]] identifiziert wird.

![[image 28.png]]
*SL-Anpassung nachdem die bullishe Candle als CISD/Rejection Block bestätigt wurde.*

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
- [[Part 2 High Precision Secrets To Intraday Price Action (Source)]]
