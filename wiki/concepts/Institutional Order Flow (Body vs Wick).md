---
tags: [concept, ict, trading-ict, core]
created: 2026-08-01
updated: 2026-08-05
sources: ["[[Institutional Order Flow (Source)]]", "[[ICT Price Action Chronicles - MOC Crushing The Buying & Selling Pressure Myth (Source)]]", "[[Predicting Session Low & High With Executions (Source)]]", "[[Market Review NQ July 31, 2026 (Source)]]"]
---

# Institutional Order Flow (Body vs Wick)

Kernregel für die Lesart von Preisreaktionen an einer [[PD Array]]: Das relevante (institutionelle)
Volumen steckt in den **Candle Bodys**, nicht in den Wicks — ein Liquidity Run muss deshalb nicht
zwangsweise über die Wicks laufen.

![[image 18.png]]
*Die Haupt-Liquidität liegt bereits in den Candle-Bodys — ein Run muss deshalb nicht zwingend
über die Wicks laufen; Wicks dürfen einen OB nicht komplett überschießen.*

## Kernregeln

- Wicks dürfen einen Order Block nicht **komplett** überschießen — auch wenn der Body darunter/darüber
  closed, darf der Wick nicht vollständig über die Referenz-Candle hinausgehen.
- Passiert es doch (Wick durchbricht komplett), muss der Orderflow geprüft werden: gab es ein
  [[CISD (Change in State of Delivery)|CISD]] oder einen Shift?
- Nach einem Sellside-Sweep ist das nächste logische Ziel die Buyside — respektiert der Preis dabei
  einen Bullish OB über die Bodys (auch wenn die Wicks kurz durchgehen), bleibt das Setup gültig.
- Markt bewegt sich "back and forth": Liquidity nehmen → PD Array erreichen/nutzen → Gegenseite Liq
  nehmen → wiederholt sich.

![[DCD7BD7A-9F2B-43B0-B61E-B72363979EDE.png]]
*Back-and-forth-Prinzip: hin und her, sobald Liquidität und eine PD Array (oder die
gegensätzliche Liquidität) genommen wurden.*

## Wick-Counting: Reentry vs. Sellside/Buyside-Liquidity (Kurz Notizen)

Wie viele Wicks ein Low (bzw. High) bilden, entscheidet über die Lesart:

- **1 Wick/Low (z.B. 5-Min)** → aggressiver **Reentry**: darunter wird keine relevante Liquidity
  vermutet.
- **2 Wicks/Lows** → darunter liegt **Sellside-Liquidity**, ein Retracement nach oben wird erwartet.
  (Spiegelbildlich für Highs: 2 Wicks = Buyside-Liquidity darüber, Retracement nach unten erwartet.)

![[Kurz Notizen - Double Wick Sellside Liquidity Example.png]]
*2 Wicks bilden ein Low → Sellside-Liquidity darunter, Retracement nach oben erwartet (bei nur 1 Wick: aggressiver Reentry).*

## Candle-Charakter als Signal

- Candles mit großen Wicks und schlagartiger Bildung sind oft **Stop Raids**, um Liquidity zu nehmen.

![[Kurz Notizen - Stop Raid Wick Example.png]]

- Wichtige Fragen zur Orderflow-Qualität: Wird Liquidity **schnell und explosiv** genommen oder muss
  sich Preis **hart und mühsam** vorarbeiten? Werden die PD Arrays respektiert? Ist genug Kraft/
  Bewegung im Markt vorhanden? Ist das nicht gegeben, gilt: Finger vom Markt lassen.
- **Market Structure Switch**: Zeigt sich ein MSS entgegen dem eigenen Bias (z.B. bullish MSS trotz
  bearishem Bias), sollte das eigene Momentum mitswitchen — dann nach höheren Preisen suchen (und
  umgekehrt).

![[Kurz Notizen - Market Structure Switch Example.png]]

- Ein Swing High/Low, das **energetisch** (mit Kraft, via [[Market Reversal Types|MSS/BOS]])
  genommen wird, ist ein positives Zeichen dafür, dass der Move weitergeht.

## MOC-Order-Flow-Bestätigung (Candlestick-only, 2026-Ergänzung)

Regel für die Bias-Bestätigung **ausschließlich über Candlesticks** — keine Indikatoren, kein Volume
Profile, kein Level 2, keine Heatmaps, kein Wyckoff, keine Pitchforks:

1. Candle **rallyt in ein (Inversion-)FVG** hinein.
2. Sie **berührt dessen C.E. (Consequent Encroachment) nicht**.
3. Sie **closed unterhalb ihres eigenen Lows**, wobei genau dort eine
   [[Volume Imbalance (VII)|Volume Imbalance]] liegt.

Sind alle drei Punkte erfüllt, gilt der **bearishe Bias als bestätigt** (spiegelbildlich: Rally in
ein Gap, C.E. nicht berührt, Close über dem eigenen High mit VII → bullish bestätigt). Praxisbeispiel
und Einbettung ins Setup: [[Market on Close (MOC) Macro Model]].

> Schlägt diese Regel in der Praxis fehl, ist laut Quelle fast immer der **Bias falsch angenommen**
> worden — nicht die Regel selbst defekt. Siehe [[Signal-Following & Crowd Liquidity Risk]].

## "Mohawk"-Wick am IFVG (2026-Ergänzung)

Ein Wick an einem [[IFVG (Inverse Fair Value Gap)|IFVG]], dessen Candle-Bodies sich **nicht**
innerhalb der IFVG-Zone halten können (Bodies bleiben komplett außerhalb/oberhalb, nur der Wick
taucht kurz hinein) — benannt nach der Optik (schmaler Wick, Bodies "frisiert" außen dran vorbei.
Gilt als bullisches Bestätigungssignal für einen Reversal: die Bodies "wollen" nicht in die Zone,
also fehlt Verkaufsdruck dort. Spiegelbildlich für bearishe Reversals (Bodies bleiben unterhalb).

## Order-Flow-Testeinsatz (Single-Contract-Probe, 2026-Ergänzung)

Vor dem eigentlichen Einstieg einen einzelnen (Micro-)Kontrakt platzieren, um am realen Order Flow
zu lesen, ob der antizipierte Level hält — ausdrücklich auch am Demo-Konto möglich, wenn kein
Live-Konto verfügbar ist. Erst wenn diese Rückmeldung (Preis respektiert das Level, PD Arrays
bilden sich wie erwartet) passt, wird die Position aufgebaut. Quelle:
[[Market Review NQ July 31, 2026 (Source)]].

## Verwandt

- [[PD Array]], [[CISD (Change in State of Delivery)]]
- [[Open Float & Liquidity Pools]]
- [[Order Block]], [[Market Reversal Types]]
- [[Market on Close (MOC) Macro Model]], [[Volume Imbalance (VII)]], [[IFVG (Inverse Fair Value Gap)]]
- [[Kurz Notizen (Source)]]
- [[Predicting Session Low & High With Executions (Source)]]
