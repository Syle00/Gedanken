---
tags: [concept, ict, trading-ict, core]
created: 2026-08-01
updated: 2026-08-02
sources: ["[[Defining Open Float Liquidity Pools (Source)]]", "[[Defining Open Float Liquidity Pools 2 (Source)]]", "[[Open Float (Source)]]"]
---

# Open Float & Liquidity Pools

Open Float = alle offenen Orders/Stops im Markt. Liquidity Pools sind die Kurszonen, an denen sich
die Stops der großen Funds konzentrieren (Highest High / Lowest Low der letzten 20/40/60 Tage,
siehe [[IPDA Data Ranges]]) — dorthin bewegt sich Preis, weil sie targetiert werden.

## Kernregeln

- Systematisches Vorgehen: 20-Tage-High/Low = Swing/kurz-mittelfristig relevant, 60-Tage-Lookback
  für die größeren Open-Float-Level (v.a. ab Daily-Timeframe monatlich geprüft).

![[image 63.png]]
*60-Tage-Lookback-High/Low = Open Float.*

- **Alle 20 Tage bildet sich ein neuer Liquidity Pool.** Ist er genommen, wird der nächste gesucht.

![[image 92.png]]
*Alle 20 Tage bildet sich ein neuer Liquidity Pool — nach dessen Einnahme wird der nächste Pool
gesucht.*

- Orderflow-Lesart: Werden wiederholt Buy-Stops gehittet und kaum Sell-Stops → Orderflow bullish
  (und umgekehrt).

![[image 90.png]]
*Werden wiederholt Buystops gehittet und kaum Sellstops, ist der Orderflow bullish.*

## Open Interest (OI) als Bestätigung

- Ein starker OI-Rückgang, während Sellside-Liquidität genommen wird, zeigt: große Player sind
  nicht mehr bereit, weiter Short zu gehen → kurzfristig noch bearish bis zum logischen Sellside-Level,
  danach ist ein längerfristiger Shift absehbar.
- Fallendes OI generell = große Funds positionieren sich eher long (und umgekehrt) — wird auch in
  [[Commodity Mega-Trades]] als Bestätigungsfaktor genutzt.

![[image 69.png]]
*Ein starker OI-Abfall zeigt: große Funds wollen nicht stark Short gehen, sondern positionieren
sich eher Long (und umgekehrt).*

## Präzisere Definition (Open Float)

Open Float = das aktuelle Interesse (Open Interest) **über und unter** dem Marktpreis in Form von
Pending Orders (Buy Stops/Sell Stops) — das gesamte Long/Short-Interesse im Markt an einem
bestimmten High/Low.

## Verwandt

- [[IPDA Data Ranges]], [[PD Array]]
- [[SMT (Smart Money Divergence)]]
- [[Quarterly Shift]] — alle 3 Monate findet ein größerer Liquidity Run statt
