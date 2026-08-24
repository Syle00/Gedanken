---
tags: [concept, ict, trading-ict]
created: 2026-08-06
updated: 2026-08-16
sources: ["[[ICT Mentorship Core Content - Month 04 - Liquidity Voids (Source)]]", "[[2026-07-13 - How To Probe Low Probability RTH Opening Ranges (Source)|How To Probe Low Probability RTH Opening Ranges (Source)]]"]
---

# Liquidity Void

Bereich in der Preislieferung, in dem **nur eine Seite** des Marktes (Buy- oder Sellside) in Form
breiter, lang durchlaufender Candles geliefert wurde — meist auf dem **Lower Timeframe** sichtbar,
während dieselbe Range auf dem Higher Timeframe oft nur als eine einzige große Candle oder als
klassisches [[Fair Value Gap (FVG)|FVG]] erscheint. Preis will diese "poröse" Zone später erneut
besuchen.

## Entstehung

- Beginnt fast immer aus einer **Konsolidierung** (Price in Balance/Equilibrium) heraus: sobald
  Smart Money genug Kapital bewegt, um Preis aus der Range zu drücken, entsteht **Displacement** —
  eine plötzliche, einseitige Preis-Imbalance.
- Kein festes Zeitfenster, bis eine Void geschlossen wird — kann Monate offen bleiben oder
  innerhalb derselben Session gefüllt werden; abhängig vom sonstigen Preiskontext.
- Auf 1-Minute-Charts sichtbar als kleine Lücke zwischen den beiden größten Down-/Up-Candles eines
  aggressiven Ausbruchs aus der Konsolidierung — genau diese Lücke ist die Void.

## Warum die Void später geschlossen wird

Eine Void entsteht, weil eine Seite der Liquidität komplett gefehlt hat (z.B. reine
Sellside-Delivery ohne Gegenbewegung). Das ist unvollständige/unfaire Preislieferung — der Markt
sucht die fehlende Gegenseite später nach, indem er zurück in die Range läuft und sie mit einer
Bewegung in die Gegenrichtung "ausbalanciert". Erst wenn die Void komplett gefüllt ist, gilt die
Preislieferung als abgeschlossen.

## Präzisions-Entry: der "Common Gap" am Rand der Void

Beim Rücklauf in eine Void entsteht am Zielrand oft ein winziger zweiter Gap (im Quellbeispiel nur
**2 Pips**) zwischen zwei Candle-Bodies — dieser "Common Gap" liefert einen sehr präzisen
Limit-Preis:

- Limit-Order genau in diesem kleinen Gap platzieren (Verkauf beim Schließen einer Sellside-Void,
  Kauf beim Schließen einer Buyside-Void).
- Reaktion ist typischen minimal (wenige Pips Drawdown), weil der Preis exakt an der Kante der
  bereits ausgeglichenen Zone reagiert — danach läuft der Preis zügig in Richtung der nächsten
  Liquidität weiter.

## RTH schlägt ETH — eine Void kann sessionspezifisch sein (2026-Ergänzung)

Aus [[2026-07-13 - How To Probe Low Probability RTH Opening Ranges (Source)|How To Probe Low Probability RTH Opening Ranges (Source)]] —
die schärfste Formulierung dazu im Vault:

> *„There's no print at all in **regular trading hours** delivery. It doesn't matter if electronic
> trading hours posted through that. Because **regular trading hours has to balance out electronic
> trading hours** to be an efficiently delivered price."*

Kernaussage: Eine Zone kann über Nacht (ETH) vollständig durchhandelt worden sein und **in RTH
trotzdem eine echte Void** darstellen. Beide Sessions werden getrennt bewertet.

- **Gewichtung**: ICT legt mehr Gewicht auf RTH, weil RTH die Level nachliefert, die ETH über Nacht
  bereits gesehen hat — *„regular trading hours tends to overlap and redeliver to levels that
  electronic trading has already delivered overnight."*
- **Praktisch**: Der Chart muss auf **RTH** umgestellt werden, um diese Voids überhaupt zu sehen.
  Im ETH-Chart verschwinden sie, weil der Übernachthandel sie optisch füllt.
- Ineffizienzen, die nur in **einer** der beiden Sessions existieren, sind ausdrücklich vorgesehen
  (*„it can, and that creates imbalances that are only seen in one session"*) — sie sind kein
  Darstellungsartefakt.

Vgl. [[Eröffnungsauktion vs. 24x5-Markt]] für dieselbe Session-Abgrenzung im Forex-Kontext und
[[ORG (Opening Range Gap) & 1st Presented FVG]], das auf derselben RTH-Umstellung beruht.

## Zusammenspiel mit anderen PD Arrays

Void, [[Fair Value Gap (FVG)|FVG]], [[Open Float & Liquidity Pools|Liquidity Pool]] und
[[Order Block]] überlappen sich häufig an derselben Preiszone — ICT nennt das ausdrücklich einen
wiederkehrenden Zusammenhang: derselbe Level ist oft gleichzeitig Rand einer Void, Grenze eines
FVG und Ort eines Stop-Runs auf eine benachbarte Liquiditätszone. Ein Setup, das mehrere dieser
Bestätigungen am selben Level stapelt, ist stärker als jede einzelne für sich.

## Verwandt

- [[Fair Value Gap (FVG)]] — dieselbe Grundidee, meist auf höherem Timeframe als klarer Gap sichtbar
- [[Breakaway Gap]] — Sonderfall, wenn die Void durch ein Volatilitäts-Event entsteht
- [[Open Float & Liquidity Pools]], [[Order Block]], [[Turtle Soup]]
- [[ICT Mentorship Core Content - Month 04 - Liquidity Voids (Source)]]
