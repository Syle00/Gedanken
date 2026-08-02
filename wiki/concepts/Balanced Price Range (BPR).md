---
tags: [concept, ict, trading-ict]
created: 2026-08-02
updated: 2026-08-02
sources: ["[[Kurz Notizen (Source)]]", "[[Algorithmic Price Delivery Continuum (Source)]]"]
---

# Balanced Price Range (BPR)

Preiszone innerhalb eines [[Fair Value Gap (FVG)|FVG]], die entsteht, wenn man **mindestens eine
Timeframe tiefer** geht, um zu sehen, wie Preis sich innerhalb des FVG tatsächlich verhalten hat.

## Regel

- Eine BPR ist erst **valide**, wenn zuvor bereits Liquidity genommen wurde — ohne vorherigen
  Liquidity-Sweep gilt die BPR nicht als belastbar.
- Bei einem [[BISI & SIBI (Buyside-Sellside Imbalance)|SIBI]] mit einer BPR in der **oberen Hälfte**
  heißt das: Preis wird **nicht weiter nach oben** traden.
- Bei einem **BISI** mit einer BPR in der **unteren Hälfte** gilt spiegelbildlich: Preis wird
  **nicht weiter nach unten** traden.
- Bildet sich im 15- oder 5-Min-Chart gar kein FVG, befinden wir uns in **High Resistance** — warten,
  bis wieder ein FVG entsteht. Sobald wieder ein FVG da ist, den Lower Timeframe nutzen, um zu
  prüfen, ob dieses FVG eine BPR enthält oder nicht.

## Wodurch eine BPR entsteht

[[Algorithmic Price Delivery Continuum (Source)]] ist die Lecture hinter den Merksätzen oben und
liefert den Mechanismus — entscheidend ist die **verbrachte Zeit**, nicht die reine Berührung:

> Wird in der oberen Hälfte eines SIBI **länger** hoch und runter getradet und der Preis dabei
> gehalten, macht das diese Hälfte zur Balanced Price Range. Spiegelbildlich beim BISI.

![[ICT 2025 - APDC 03.png]]
*15M-SIBI mit Balanced Price Range über dem C.E — die obere Hälfte ist abgearbeitet.*

## Antizipieren, ob ein FVG offen bleibt

Daraus folgt die praktische Anwendung:

- Ist eine Hälfte **imbalanced** — nur eine einzige Candle ist stark durchgelaufen — während in der
  anderen **viel Zeit** verbracht wurde, wird erwartet, dass Preis die imbalanced Hälfte **füllt**
  und die andere **offen bleibt**.
- Bei einem **Higher-Timeframe-FVG** deshalb immer prüfen, **was am 50-%-Level (C.E) passiert ist**:
  liegt dort eine BPR oder nicht? Ohne BPR ist eher mit Fill oder sogar Durchschießen zu rechnen.

![[ICT 2025 - APDC 05.png]]
*Untere Hälfte imbalanced, obere mit viel verbrachter Zeit — Fill unten erwartet, oben bleibt offen.*

## Verwandt

- [[Algorithmic Price Delivery Continuum]] — die Lesemethode, in der die BPR-Prüfung ihren Platz hat
- [[Fair Value Gap (FVG)]], [[BISI & SIBI (Buyside-Sellside Imbalance)]]
- [[Chain of Custody (Q-Validation)]]
- [[How To Disqualify 1st Presented FVGs (Source)]] — die BPR als Ausschlusskriterium für Schein-FVGs
- [[Kurz Notizen (Source)]], [[Algorithmic Price Delivery Continuum (Source)]]
