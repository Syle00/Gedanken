---
tags: [concept, ict, trading-ict, core]
created: 2026-08-01
updated: 2026-08-06
sources: ["[[Defining Open Float Liquidity Pools (Source)]]", "[[Defining Open Float Liquidity Pools 2 (Source)]]", "[[Open Float (Source)]]", "[[ICT Mentorship Core Content - Month 04 - Liquidity Pools (Source)]]"]
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

## Stop-Run-Mechanik (Reinforcement-Ergänzung)

Aus [[ICT Mentorship Core Content - Month 04 - Liquidity Pools (Source)]] — konkrete Größenordnungen
und die Kehrseite jeder Liquidity-Pool-Aussage:

- **Grundprinzip gegen Retail gerichtet**: Smart Money verkauft **über** Marktpreis (in den Pool
  der Buy Stops über alten Hochs) und kauft **unter** Marktpreis (in den Pool der Sell Stops unter
  alten Tiefs) — das Gegenteil der retailtypischen Breakout-Käufe/-Verkäufe.
- **Sweep-Größe auf LTF (15/30 Min)**: typischerweise **10–20 Pips** über das alte Hoch/unter das
  alte Tief hinaus, bevor der Reversal einsetzt.
- **Stop-Weite für den Entry**: **30–50 Pips**, wenn der Entry unterhalb/oberhalb des Sweeps (nicht
  am oder über dem alten Level) gesetzt wird — das verhindert, vorzeitig durch normales Rauschen
  ausgestoppt zu werden.
- **Invalidierungs-Schwelle**: Läuft Preis mehr als **ca. 25 Pips** über den erwarteten Sweep hinaus,
  ist es wahrscheinlich **kein reiner Stop-Run mehr**, sondern eine echte Fortsetzung in diese
  Richtung — die These gilt dann als widerlegt, nicht nur als "noch nicht erfüllt".
- **Pairing-Logik**: Genommene Sellside-Liquidity (ausgelöste Sell-Stops = Market Sell Orders) wird
  von Smart Money direkt mit **Kaufpositionen** an derselben Stelle gepaart; genommene
  Buyside-Liquidity wird mit **Verkaufs-/Gewinnmitnahme-Orders** gepaart — dieselbe Rolle wie ein
  Market Maker/Liquidity Provider.

## Präzisere Definition (Open Float)

Open Float = das aktuelle Interesse (Open Interest) **über und unter** dem Marktpreis in Form von
Pending Orders (Buy Stops/Sell Stops) — das gesamte Long/Short-Interesse im Markt an einem
bestimmten High/Low.

## Verwandt

- [[IPDA Data Ranges]], [[PD Array]]
- [[SMT (Smart Money Divergence)]]
- [[Quarterly Shift]] — alle 3 Monate findet ein größerer Liquidity Run statt
