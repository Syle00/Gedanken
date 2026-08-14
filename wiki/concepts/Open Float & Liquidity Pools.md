---
tags: [concept, ict, trading-ict, core]
created: 2026-08-01
updated: 2026-08-14
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

## REH / REL (Relative Equal Highs / Lows)

Aus dem 2026er-Material mehrfach als DOL-Bezeichnung verwendet, ohne dort selbst definiert zu sein
(`raw/trading-ict/2026/Enigma FVG Projections.md`, `Midnight ET Principles In Relationship To
PreMarket Session.md`, `NQ Futures Weekly Range Market Wizardry.md`). Kein eigenes YouTube-Video auf
dem echten Kanal [@InnerCircleTrader](https://www.youtube.com/@InnerCircleTrader) gefunden — eine
Suche förderte nur ein gleichnamiges Video auf einem **anderen** Kanal ("The Inner Circle Trader AKA
The ALGO Trader", andere Channel-ID) zutage, das bewusst **nicht** genutzt wurde, da es nicht der
Vault-Konvention (nur der verifizierte Original-Kanal zählt als Quelle) entspricht.

- **REH = Relative Equal High(s)**, **REL = Relative Equal Low(s)**: mehrere Hochs bzw. Tiefs, die
  **nahezu**, aber nicht exakt auf demselben Preis liegen (im Gegensatz zu echten "Equal Highs/Lows").
  Genau wie ein exaktes Doppel-Top/-Bottom (siehe
  [[Double Top & Bottom (Algorithmische Range-Projektion)]]) baut sich dort ein Pool aus
  Stop-Liquidity auf — Buy Stops über einem REH-Cluster, Sell Stops unter einem REL-Cluster.
  Funktional identisch zur allgemeinen Liquidity-Pool-Logik oben, nur mit gelockerter
  "exakt gleich"-Anforderung.
- Alle drei 2026er-Belegstellen nutzen den Begriff konsistent als **DOL-Kandidat** (Draw on
  Liquidity) — z.B. "ein DOL mit REL ist vorhanden" bei mehrfach per Wick genommenen, aber nicht
  exakt identischen Tiefs.

### Welches der beiden Extreme zählt als noch unberührt (Nutzerregel, 2026-08-14)

Bei einem REH/REL-Paar (zwei nahe, aber nicht exakt gleiche Extreme) zählt für die **linke**
(zeitlich frühere) Marke nur dann noch Liquidität, wenn sie **weiter außen** liegt als die
rechte — sonst hat die rechte sie bereits genommen:

- **REH**: das **linke** High muss **höher** sein als das rechte → die rechte Bewegung ist am
  linken (höheren) High noch nicht angekommen, dessen Stops liegen also noch offen. Ist das
  linke High dagegen niedriger, hat das rechte es bereits gerissen — kein gültiger Pool mehr.
- **REL**: spiegelbildlich, das **linke** Low muss **tiefer** sein als das rechte, sonst ist es
  vom rechten bereits genommen.

Praxisbeispiel (14.08., Daily-Chart, MNQ): REH-Paar 16.06. (30 975,50) und 22.06. (30 967,75) —
16.06. ist links **und** höher → gültiger, noch unberührter Pool ist **30 975,50** (16.06.), nicht
das rechte, niedrigere 22.06.-High.



## Präzisere Definition (Open Float)

Open Float = das aktuelle Interesse (Open Interest) **über und unter** dem Marktpreis in Form von
Pending Orders (Buy Stops/Sell Stops) — das gesamte Long/Short-Interesse im Markt an einem
bestimmten High/Low.

## Hierarchie der Referenz-Levels (Begleitvideo-Ergänzung)

Aus dem Begleitvideo zu [[Open Float (Source)]]: Protective Stops konzentrieren sich nicht nur am
20/40/60-Tage-Level, sondern an mehreren gestaffelten Zeitrahmen gleichzeitig — je länger der
Zeitrahmen, desto größer i.d.R. der resultierende Move nach dem Run:

- Weekly High/Low, Monthly High/Low
- 3-Monats-High/Low (= Quarterly-Bezug, siehe [[Quarterly Shift]])
- 6-Monats-High/Low
- 12-Monats-High/Low

Praxishinweis: ein 12-Monats-Hoch/Tief kann auch **schnell** erreicht werden, wenn der Preis schon
nah dran notiert — die Zeitangabe ist nur der Lookback-Horizont der Marke, kein Wartezeitraum bis
zum nächsten Run.

## Session Liquidity: Previous Day/Week High/Low (Nutzer-These, 2026-08-14)

Jannes' Ergänzung zur obigen Hierarchie: **wann** sich ein Pool gebildet hat, ist selbst ein
Qualitätsmerkmal. Previous Day High/Low und Previous Week High/Low gelten als besonders starke,
high-probability [[PD Array|Draw on Liquidity]] — feste, jedem Marktteilnehmer bekannte
Referenzpunkte, im Gegensatz zu beliebigen Swing-Points, die erst durch die eigene
Fraktal-Erkennung entstehen.

> ⚠️ **Erster Backtest negativ/unbrauchbar (2026-08-14).** `algo/backtest_sb_session_liq.py` hat
> PDH/PDL/PWH/PWL als feste Ziel-Liquidität für den Silver Bullet getestet (Entry/Stop
> unverändert). 47 Tage, 118 Fenster: Baseline (Swing-Level) 112 Trades/17,0 % Win/+3,97 $/Trade;
> **PDH/PDL** 75 Trades/**2,7 % Win**/-14,57 $/Trade — klar negativ; **PWH/PWL** 82 Trades/2,4 %
> Win/+34,35 $/Trade — nur **2 von 82 Trades gewinnen**, und der größere Gewinner erreicht sein
> Ziel erst 4 Handelstage später (kein Silver-Bullet-Zeitrahmen mehr, sondern eine unbegrenzt
> offen gehaltene Position) — dieses Ergebnis ist ein Methodenartefakt (fehlender Zeit-Cap in der
> Simulation, siehe `algo/PLAN.md` Backlog), keine Bestätigung. **Widerlegt die allgemeine These
> nicht**, zeigt nur: als Ziel *speziell für den Silver Bullet* (der einen kurzen Zeitrahmen
> erwartet) taugen diese fixen Session-Level hier nicht — bleibt offene Hypothese, siehe
> `algo/PLAN.md` [2026-08-14].

## Intermediate-Term High/Low

Ein **Intermediate-Term High** ist ein Hoch, dem sowohl links **als auch rechts** ein niedrigeres
Short-Term-High vorausgeht bzw. folgt (Analogie: Kopf einer Schulter-Kopf-Schulter-Formation).
Spiegelbildlich für ein **Intermediate-Term Low**. Eine Kette **fallender** Intermediate-Term-Highs
bei gleichzeitig fallenden Intermediate-Term-Lows liefert direktionalen Bias auf dem Daily-Chart —
jede Rally scheitert daran, ein neues Hoch zu etablieren, jeder Sell-off unterbietet das vorherige
Tief. Vertiefung erwartet in [[Institutional Swing Point]] (Begleitvideo „Defining Institutional
Swing Points" zu Month 05 — YouTube-Fetch aktuell blockiert, siehe `wiki/log.md`).

## Timeframe-Wahl zur Pool-Erkennung (Nutzer-Arbeitsweise, 2026-08-14)

Eigene Praxisregel des Nutzers, nicht aus einer ICT-Quelle zitiert:

- **15-Min-Chart als "Bellwether Chart"** für Intraday-Modelle (z.B. [[Silver Bullet Model]] und
  künftige Intraday-Modelle) — der bevorzugte Referenz-Timeframe, um relevante Liquidity Pools
  einzuordnen, bevor auf eine niedrigere Auflösung für den Entry gewechselt wird.
- **Kein Timeframe ist exklusiv** — Liquidität wird grundsätzlich auf jedem Timeframe gesucht.
- **1-Min-Chart eignet sich besonders gut, um große/gute Liquidity Pools zu erkennen** — auf dieser
  Auflösung treten die größeren, klarer abgegrenzten Pools deutlicher hervor als auf höheren
  Timeframes.

Passt zusammen mit der bestehenden SB-Regel oben ("ICT nutzt bevorzugt den 5-Min-Chart für den
Entry, kombiniert mit PD Arrays aus dem 15-Min- und 1H-Chart") — der Nutzer ergänzt hier speziell
die **Pool-Erkennung** (nicht den Entry-Trigger) um 15M als Referenzebene und 1M als
Detailebene für große Pools.

> ⚠️ **Offene Hypothese, erster Backtest schwach/negativ (2026-08-14).** `algo/backtest_sb_bellwether.py`
> hat für den Silver Bullet getestet, ob die Ziel-Liquidität statt aus 5m aus 15m bzw. 1m gezogen
> eine bessere Trefferquote liefert (Entry/Stop bleiben unverändert auf 5m). Ergebnis über 27 Tage
> mit gleichzeitig 1m+5m+15m-Daten (63 Fenster): **5m-Baseline** 62 Trades/22,6 % Win/+9,71 $/Trade;
> **15m** 42 Trades/9,5 % Win/**-1,95 $/Trade** — schlechter, nicht besser; **1m** 62 Trades/
> 30,6 % Win/+9,83 $/Trade, aber bei höherem dubious-Anteil (12,9 % gegen 4,8 %). Bei n=42-62 ist
> keine Variante von Rauschen unterscheidbar. Die 1m-These bekommt damit eine schwache erste
> Stütze, die 15m-Bellwether-These für die *Ziel*-Auswahl (nicht die generelle Pool-Erkennung)
> eher nicht — bleibt laufend beobachtet, siehe `algo/PLAN.md` [2026-08-14].

## Verwandt

- [[IPDA Data Ranges]], [[PD Array]]
- [[SMT (Smart Money Divergence)]]
- [[Quarterly Shift]] — alle 3 Monate findet ein größerer Liquidity Run statt
- [[Institutional Swing Point]] — vertieft die Intermediate-Term-High/Low-Definition (noch offen)
- [[Silver Bullet Model]] — nutzt diese Timeframe-Hierarchie zur Pool-Erkennung
