---
tags: [model, ict, trading-ict, 2026, macro, sessions, moc]
created: 2026-08-05
updated: 2026-08-10
sources: ["[[2026-08-05 - ICT Price Action Chronicles - MOC Crushing The Buying & Selling Pressure Myth (Source)|ICT Price Action Chronicles - MOC Crushing The Buying & Selling Pressure Myth (Source)]]", "[[2026-08-04 - ICT Price Action Chronicles - Market On Close Macro (Source)|ICT Price Action Chronicles - Market On Close Macro (Source)]]", "[[ICT Gems - How to Trade the Final Hour Macro (Source)]]", "[[ICT Gems - When To Anticipate Price Spooling (Source)]]"]
---

# Market on Close (MOC) Macro Model

Setup für die **letzten 10 Minuten des RTH-Handelstags (15:50–16:00 Uhr NY)** — analog zum
[[NY Lunch Macro Model]], nur am Tagesende statt zur Mittagszeit. Laut Quelle **nicht
NASDAQ-exklusiv**: das Beispiel läuft am E-Mini S&P (ES), dieselbe Logik gilt index-übergreifend.

## Die letzte Stunde hat ein eigenes Macro-Raster (2024-Ergänzung)

Aus [[ICT Gems - When To Anticipate Price Spooling (Source)]] und
[[ICT Gems - How to Trade the Final Hour Macro (Source)]]: In der letzten Handelsstunde gilt das
sonst durchgängige `:50–:10`-Raster (siehe [[ICT Macros & Leading Candles]]) **nicht**. ICT nennt
stattdessen:

| Fenster | Bezeichnung |
|---|---|
| **15:15–15:45** | Final Hour Macro |
| **15:45–16:00** | **Market on Close** |
| 16:01 (nur Earnings-Saison) | eigener Algorithmus feuert, danach Run bis **16:15** |

> ⚠️ **Widerspruch zur Fensterlänge oben — Stand nach vollständigem Playlist-Ingest: 2:1 für
> 15:50.** Diese Seite datiert das MOC-Fenster auf **15:50–16:00 (10 Minuten)** nach den 2026er
> Chronicles-Lectures. Die Gems-Fassung
> [[ICT Gems - When To Anticipate Price Spooling (Source)|When To Anticipate Price Spooling]] sagt
> ausdrücklich das Gegenteil: *"it's not 10 minutes, it's 15 minutes, 3:45 to 4:00."* Eine dritte
> ICT-Quelle, [[ICT Gems - Algorithmic Timings With Opening Ranges (Source)]], nennt dagegen wieder
> **15:50** (*"that's the 3:50 little price run that usually takes off"*) und beschreibt 15:15–15:45
> als das **vorgelagerte** 30-Minuten-Macro, in dem man das Setup *sucht*, das dann in den
> MOC-Run mündet.
>
> **Lesart, die alle drei Aussagen zusammenbringt** (nicht als gesichert markiert): 15:15–15:45 =
> Setup-Fenster, 15:45/15:50–16:00 = Ausführung. Der Unterschied 15:45 vs. 15:50 bleibt offen.
> Für einen Backtest weiterhin **beide Fensterlängen** prüfen.

ICT nennt außerdem eine Zahl: *"there's four of four macros in that last hour"* — enumeriert
werden im Transkript aber nur die beiden oberen mit klaren Zeiten (plus die
Earnings-Erweiterung als bedingter dritter/vierter Teil). Die vollständige Aufzählung liefert
die Quelle nicht — Wortlaut geprüft in `raw/trading-ict/2026/yt-VH7Dh1OONj4-transcript.md`
("ICT Gems - When To Anticipate Price Spooling"), keine weitere Quelle im Vault ergänzt die
fehlenden zwei.

`algo/macro_db.py` bildet seit 2026-08-11 drei eigenständige Fenster ab (`LAST_HOUR_WINDOWS`):
`15:15` (30 Min, Final Hour Macro, unstrittig), sowie **beide** MOC-Lesarten nebeneinander —
`15:45` (15 Min, Gems-Quelle) und `15:50` (10 Min, 2:1-Mehrheit der Chronicles-Quellen) — statt
den Streit einseitig aufzulösen oder sie im generischen `:50`-Raster als eine Zeile `15:50`
(20 Min) zu verschmelzen, die über den RTH-Schluss 16:00 hinauslief. Der bedingte
Earnings-Season-Teil (16:01/bis 16:15) fließt nicht in die Datenbank ein — aus OHLC allein
nicht von einem normalen Handelstag unterscheidbar.

**Position bis 16:00 glattstellen**: *"the final candle at 1600 — you want to have your position
squared by then."*

### Wann das Final-Hour-Macro ausfällt

Konkrete Ausfallbedingung statt Allgemeinplatz: Hat der Markt **bereits in der Tagesmitte oder
direkt nach der Lunch-Session viel gelaufen** und dabei seine Liquiditätsaufgabe erledigt, ist die
letzte Stunde häufig *"listless, choppy, not really doing too much at all"*. Das Macro ist dann
nicht falsch — es hat schlicht nichts mehr zu holen.

### Standardabweichungen als Ziel-Mechanik

Der Final-Hour-Trade nutzt dieselbe STD-Projektion wie das MOC-Fib oben, aber mit einem klar
benannten **Trigger-Punkt**:

1. Ein **Market Structure Shift** in der letzten Stunde entsteht, sobald Preis **einen Tick über**
   das vorherige Short-Term-High handelt — ein Close darüber ist **nicht** erforderlich.
2. Der vorangegangene Abverkauf ist der Anker: Fib von diesem **Low** bis zum **Short-Term-High vor
   dem Retracement** ziehen.
3. Die projizierten STD-Level darüber sind die Ziele; gewählt wird das Level, das **über** dem
   angepeilten Buyside-Pool liegt.
4. **Bid/Ask-Zuschlag einplanen**: Der Markt hält nicht exakt am Tick, weil zwischen Bid und Ask
   eine Spanne liegt — im Beispiel lag das Hoch einen Tick über dem berechneten Ziel. Vgl. die
   Mohawk-Regel in [[Institutional Order Flow (Body vs Wick)]].

## Grundidee

Ab **15:00 Uhr** (Beginn der letzten RTH-Stunde) wird beobachtet, wie sich Preis relativ zur
**Dealing Range des Tages** verhält (PM-Opening-Range-Low ab 13:30 Uhr bis Tageshoch). Ziel ist,
**in einem 10-Minuten-Fenster** eine chirurgisch präzise Entscheidung zu treffen — kein
"Hold for hundreds of handles", sondern ein kleiner, gezielter Move.

> Bei einem Tag, der bereits **lange in eine Richtung gelaufen ist** ("long in the tooth"), wird vor
> dem Close eher **Konsolidierung oder ein Retracement** erwartet als eine weitere Fortsetzung.

## Zwei Ranges, nicht eine

Die Grundlagen-Lecture ([[2026-08-04 - ICT Price Action Chronicles - Market On Close Macro (Source)|ICT Price Action Chronicles - Market On Close Macro (Source)]]) trennt
explizit zwei Ebenen, die leicht verwechselt werden:

1. **Daily Range** (grob): Morning-Low bis Post-13:30-Uhr-High. Liefert die **groben
   Oktanten-/Quadranten-Level** — im NQ-Beispiel den ersten Oktant bei 28.883,00.
2. **Final Hour RTH Dealing Range** (fein): High und Low, die sich **innerhalb** der letzten Stunde
   (15:00–16:00 Uhr) selbst neu bilden. Genau **diese** kleinere Range wird gefibbt (Anker High → Low,
   0,5-Extension-Level) und liefert das eigentliche 10-Minuten-Ziel des MOC-Fensters.

Beide Ranges werden parallel verfolgt — die große gibt den Kontext (wie weit kann es realistisch
gehen), die kleine liefert das konkrete Preisziel.

## Ablauf

1. **Dealing Range bestimmen**: PM-Opening-Range-Low (13:30 Uhr) bis Tageshoch — das ist der große
   Rahmen. Innerhalb davon eine **kleinere Dealing Range** suchen, die dicht ans Equilibrium
   herangehandelt hat (Discount, ohne den Midpoint zu brechen) und ein Buyside-Balance-Sellside-
   Inefficiency respektiert (siehe [[Equilibrium Vs. Discount]]).
2. **Fib-Grid anlegen**: Low → High dieser kleineren Range, inkl. **negativem -0,5-Level** (Setting
   wie bei [[Midnight Opening Range]] gewohnt). Daraus ergibt sich ein Levelpaar (Q/O-Raster, siehe
   unten).
3. **Erwartung ab ~15:50**: Preis läuft **erst** in Richtung Buyside (nimmt die Relative-Equal-Highs
   der kleineren Range), **dann erst** wird die eigentliche MOC-Richtung gehandelt — der erste Move
   ist noch **nicht** die Execution, sondern baut nur das Levelpaar auf (analog zur
   [[NY Lunch Macro Model|10-Uhr-Linie]] beim Lunch Macro: "erst entsteht das Target, dann wird
   gehandelt").
4. **Entry-Zone**: Alles zwischen dem gesweepten High und dem Midpoint der kleineren Range gilt als
   valide Short- (bzw. Long-)Zone — **aber erst nach Order-Flow-Bestätigung** (Schritt 5).
5. **Order-Flow-Bestätigung** (candlestick-only, siehe
   [[Institutional Order Flow (Body vs Wick)#MOC-Order-Flow-Bestätigung (Candlestick-only)|Detailregel]]):
   Candle rallyt in ein (Inversion-)FVG, berührt dessen C.E. nicht, closed unterhalb des eigenen Lows
   (das eine Volume Imbalance trägt) → bestätigt den bearishen Bias (spiegelbildlich bullish).
6. **Fortsetzung**: nach Bestätigung aggressiver Bruch durch minor Sellside-Pools (Relative Equal
   Lows), bis das projizierte Fib-Level erreicht wird.

## Fib-Feinraster: Quadrant → Oktant → 16tel

Ergänzt das bestehende Q/O-Raster ([[Chain of Custody (Q-Validation)]]):

| Ebene | Anteil der Range | Bezeichnung |
|---|---|---|
| Percentile | 100 % / Hälften | — |
| Quadrant (Q) | 25 % | bereits im Wiki |
| Oktant (O) | 12,5 % (halber Quadrant) | bereits im Wiki |
| **16tel** | **6,25 % (halber Oktant)** | **neu** |

## Relative Equal Lows/Highs — präzises Kriterium

Aus der Grundlagen-Lecture: das dem aktuellen Preis **nähere** Low muss **höher** sein als das
**weiter entfernte** Low, sonst ist es kein High-Probability-Draw-Kandidat (spiegelbildlich für
Highs: das nähere High muss **niedriger** sein). Nur wenn diese Reihenfolge stimmt, gilt der Pool
als valides Ziel für den MOC-Move.

## Wick vs. FVG — Vorrang bei geteiltem Bereich

Teilt sich ein **Wick** den Preisbereich mit einem **FVG** (Wick liegt links vom FVG, beide
überlappen), hat der **gesamte Wick Vorrang** — nicht nur das FVG. Präzisiert die bestehende Regel
"Wick schlägt FVG" auf [[Fair Value Gap (FVG)]]. Bleiben die Candle-Bodies dabei konsequent in der
unteren Hälfte dieses Wicks (Premium-Sensitivität, siehe
[[Institutional Order Flow (Body vs Wick)]]), gilt die Zone als **formidabler Widerstand** —
klassische Support/Resistance-Logik erklärt das laut ICT nicht, nur die Body-vs-Wick-Lesart.

## Stop-Loss-Philosophie: Drawdown-Toleranz statt Tick-Präzision

- **SL-Anker**: an die **High-Probability-Wick** (Confluence aus Oktant **und** Quadrant der
  Dealing Range) plus 1–2 Ticks — nicht an klassische Support/Resistance-Level.
- Bewusste **Toleranz für Drawdown**: solange die Wick-Bodies die Zone respektieren, darf der Preis
  bis knapp an den SL heranlaufen, ohne dass das Setup ungültig wird.
- **Exit-Präzision ist unwichtiger als Entry-Präzision**: einen Teil der Position bereits **über**
  50 % der erwarteten Range zu schließen zählt laut ICT bereits als "Präzision" — nicht das exakte
  Tick-Ziel zu treffen. Verluste/Stop-outs sind Lerngelegenheiten, kein Grund, das Setup infrage zu
  stellen. Siehe [[Missed Entry Trade Management Playbook]] für das allgemeine Exit-Schema.

## Zahlenbeispiele

**ES, 2026-08-04** (Folgevideo):
- Short-Entry am projizierten Midpoint: **7.786,00**
- Projiziertes 16tel-Level (Ziel/Reversal): **7.761,75**
- Tatsächliches Tagestief: **7.761,25** — Abweichung **2 Ticks**

**NQ, 2026-08-03** (Grundlagen-Lecture):
- Erster Oktant der Daily Range: **28.883,00**
- Projiziertes 0,5-Extension-Level der Final-Hour-Dealing-Range: **28.870,75**

Diente ICT beide Male als Präzisionsnachweis: die Level wurden **vor** dem Move berechnet, nicht im
Nachhinein angepasst.

## Risikohinweis aus der Quelle

Fills sind bei öffentlich geteilten Levels **nicht garantiert** — bei genug Followern, die dieselbe
enge Zone anlaufen, bekommt nicht jeder eine Füllung zum selben Preis (Marktmechanik, keine
Verschwörung). Siehe [[Signal-Following & Crowd Liquidity Risk]].

## Verwandt

- [[NY PM Trend]] — die übergeordnete PM-Session, in die das MOC-Fenster fällt
- [[NY Lunch Macro Model]] — strukturell identisches Prinzip zur Mittagszeit
- [[ICT Daily Range Session Timing]], [[ICT Macros & Leading Candles]]
- [[Dealing Range]], [[Equilibrium Vs. Discount]], [[Chain of Custody (Q-Validation)]]
- [[Institutional Order Flow (Body vs Wick)]], [[IFVG (Inverse Fair Value Gap)]]
- [[Signal-Following & Crowd Liquidity Risk]]
- [[2026-08-05 - ICT Price Action Chronicles - MOC Crushing The Buying & Selling Pressure Myth (Source)|ICT Price Action Chronicles - MOC Crushing The Buying & Selling Pressure Myth (Source)]]
- [[2026-08-04 - ICT Price Action Chronicles - Market On Close Macro (Source)|ICT Price Action Chronicles - Market On Close Macro (Source)]] — Grundlagen-Lecture (Vortag)
