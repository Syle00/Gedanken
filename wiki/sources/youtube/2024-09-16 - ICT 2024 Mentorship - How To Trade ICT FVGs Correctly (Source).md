---
tags: [source, youtube, ict, trading-ict, fvg, entry, stop-loss, mentorship-2024]
created: 2026-08-14
updated: 2026-08-14
raw_path: "raw/trading-ict/2026/yt-HhgWGduQZQY-transcript.md"
---

# ICT 2024 Mentorship - How To Trade ICT FVGs Correctly (Source)

Quelle: https://www.youtube.com/watch?v=HhgWGduQZQY
Kanal: The Inner Circle Trader | Veröffentlicht: 2024-09-16 | Länge: 2:12:08

> Rohtranskript: `raw/trading-ict/2026/yt-HhgWGduQZQY-transcript.md` (~105.000 Zeichen,
> Auto-Captions, durchgehend bis zum Streamende).

Live-Stream am Montag **16.09.2024**, NQ 1-Minuten- und 15-Sekunden-Chart, als Unterricht für
seinen Sohn Caleb aufgesetzt. Es ist die **Ausführungs**-Lecture zum FVG: wo genau der Entry
liegt, wo der Stop, wie die Zone gerastert wird — und am Ende ein live ausgeführter Long mit
Fill-Nachweis. Ergänzt die Auswahlregeln aus
[[2025-01-19 - ICT Private Mentorship - High Probability FVGs Masterclass (Source)|High Probability FVG's (Masterclass)]].

## Kernaussagen (trading-relevant, gefiltert)

### Die drei Kerzen bekommen feste Rollen

| Kerze | Rolle |
|---|---|
| **1** | linke Gap-Kante; konservativer Stop dahinter |
| **2** | Displacement-/**Trigger**-Kerze — sie *ist* das FVG; aggressiver Stop dahinter |
| **3** | rechte Gap-Kante; **liefert den Entry** |

### Entry: einen Tick vor der nahen Kante

> **Bullish**: *„you're going to use this candlestick number 3's low **plus one tick** — that's my
> entry, that's how ICT enters it."*
> **Bearish**: *„I would be short **one tick below** this candlestick's high."*

Der Fill sitzt damit bewusst **bevor** Preis ins Gap läuft — *„I want to make sure I get filled,
I don't like missing my entries."* Wird der Moment verpasst, geht er per Market-Order rein, sobald
er den Chart wieder sieht: *„it's not like I'm chasing — it's offering me a better price than I
was willing to pay."*

### Stop: zwei Varianten, bewusst getrennt

- **Aggressiv (maximaler Hebel)**: hinter **Kerze 2** — *„number two candle is where your stop loss
  is, that's your… if you're really trying to use the most leverage."*
- **Konservativ (1 Kontrakt)**: hinter **Kerze 1** — *„where you're not overleveraging… you don't
  want to be scared out, you don't want to be worrying about every fluctuation."*
- **Verfeinerung (Extra Credit)**: hat Kerze 1 selbst einen Wick, der ein eigenes Gap bildet
  („two layers of gaps"), reicht **ein Tick jenseits des C.E. dieses Wicks** als Stop. Danach
  trailen: nach dem Bruch des Hochs Stop in die Nähe des **unteren Quadranten** des FVG.

### „Wir handeln keine Zonen"

> *„We are not supply and demand… **we don't deal with zones**. There are specific price levels."*

Die Level sind: **Kerze-3-Kante ∓ 1 Tick** (Entry) → **oberer/unterer Quadrant** → **C.E.**
Skalierung im Beispiel: 6 Kontrakte am Entry, +4 am Quadranten, +2 am C.E. — *„you have to always
**grade your inefficiencies**."*

### Das Stärkesignal: die ferne Hälfte bleibt offen

> **Bullish**: *„the best perfect scenario is the market only drops into the **upper half** of the
> gap, it leaves that **lower half untouched**, and that's indicating that it's extremely bullish.
> You're on side, you don't need to be afraid of getting stopped out."*
> **Bearish** gespiegelt: die obere Hälfte bleibt offen.

Dosierung: *„we don't want to see it spending a lot of time in there — **one, at most two times**,
better if it's just once."* Und ein Tempo-Signal: *„as soon as the candlestick creates the fair
value gap, if the **next candle number four** drops in and it starts running, chances are stronger
that this lower half will stay open."*

> ⚠️ Die eigene Messung zeigt, dass dieses Signal **kein Eingangsfilter** ist — siehe
> [[High-Probability-FVG - ICTs Kriterien gegen eigene Daten (laufend)]]. „Ferne Hälfte offen"
> heißt bei einem Stop hinter Kerze 2 fast zwangsläufig „Stop nie erreicht": die 99 % Trefferquote
> ist eine *Beschreibung* des Gewinners, keine Vorhersage. Das schnelle Rebalance („fast") schneidet
> in den Daten sogar **schlechter** ab als der Durchschnitt.

### Dieselbe Logik für Wicks und Order Blocks

> *„Anything that acts like an inefficiency — like a wick — if the wick is going to be bullish, we
> want to see the upper half of the wick keep price from trading into the lower half."* Wick über
> Preis = Premium Array, Wick unter Preis = Discount Array.
> Beim [[Order Block]]: bullish darf **keine Kerze unter dem Mean Threshold schließen** — ein Stich
> durch ist tolerierbar, ein Close nicht. *„If it trades to its middle point, it indicates it's
> weak."*

### VII gehört in die Grenze — sonst stimmt der C.E. nicht

> *„If you're drawing this fair value gap here you **can't just use the wick** — that's not valid.
> You want to use the **volume imbalance** that's part of and inside of it… you'll have better
> determination of the **consequent encroachment** level, which is the most important level."*

Deckt sich mit [[Volume Imbalance (VII)]] und der Implementierung in `tools/analyze_ohlc.py::fvgs`.

### Mindest-Bewegungsraum: 20 Handles

> *„It's got to have at least this much movement potential… **20 handles** is what's being shown
> here — 19.360 to 19.340, that's 20 handles, or 80 ticks."* Daraus soll ein Ziel von **15 Handles**
> realistisch sein.
> Und ausdrücklich **gegen** kleinere Ziele: *„I don't like the 10 handle stuff… 10 handles is
> static price action, you can get stopped out and be right. That's not what I want my son to do."*

### Weitere Regeln aus dem Stream

- **Das 1.p FVG kann nicht auf der 9:30-Kerze liegen** — er korrigiert sich live: *„it can't be on
  your 9:30 candle, it can **only appear at 9:31 or after**."* Bestätigt die Fensterregel auf
  [[ORG (Opening Range Gap) & 1st Presented FVG]].
- **70-%-Regel bestätigt**: der Mid Gap (C.E.) des [[ORG (Opening Range Gap) & 1st Presented FVG|ORG]]
  wird zu 70 % in den ersten 30 Minuten getroffen — *„we've seen one or two times where it hasn't
  done it, but eventually it gets hit."*
- **Ein FVG in der unteren Hälfte des Eröffnungs-Impulses ist eine Falle**: der Drop von 9:30 in
  das erste Swing Low ist ein [[Judas Swing]]; ein SIBI **innerhalb der unteren Hälfte dieses
  Beins** ist kein Short, sondern das Gegenteil — *„that gap is not something to go short on, it is
  something you expected to go higher."*
- **Stop-out = Information, kein Unfall**: *„if you get stopped out with a fair value gap, it tells
  you you're probably watching the formation of an [[IFVG (Inverse Fair Value Gap)|inversion fair
  value gap]]"* — Gegenrichtung mit halber Größe handelbar.
- **Primary vs. minor Liquidität**: nimmt ein Move das Tages-Low, wird die darunterliegende Sellside
  von *minor* zu *primary* — dasselbe spiegelbildlich für Highs.
- **Zwei Ausstiegsstufen**: erstes Partial an der nächstliegenden Liquidität („low hanging fruit"),
  danach ein Terminus. *„Get in, get his, and go home."*
- **Journal-Vorgabe**: pro Übungstrade Zeit bis Ziel, Zeit bis Stop und maximalen Drawdown („heat")
  mitschreiben. Im Live-Beispiel: Fill 19.342 (ideal wären 19.339,50 gewesen), Tief 19.334,25 =
  **1,75 Handles Heat**, Ziel nach **10 Minuten** erreicht, im Macro **10:50–11:10**.
- **Kontraktwerte** (Gegenprobe zu `algo/pnl.py`): MES 5 $/Punkt, MNQ 2 $/Punkt, NQ Mini
  20 $/Punkt. ✅ stimmt mit dem Repo überein.

## Bewusst ausgefiltert

Audio-Check und Streaming-Technik, ausgedehnte Abrechnungen mit Plagiatoren und anderen Mentoren,
Kontraktrollover-Anekdote, Erziehungs- und Mindset-Passagen an seinen Sohn, Warnung gegen
Nachhandeln seiner Trades.

## Verwandt

- [[Fair Value Gap (FVG)]] → „Entry, Stop und Quadranten"
- [[2025-01-19 - ICT Private Mentorship - High Probability FVGs Masterclass (Source)|High Probability FVG's (Masterclass)]] — die Auswahlregeln
- [[High-Probability-FVG - ICTs Kriterien gegen eigene Daten (laufend)]] — die eigene Messung
- [[Volume Imbalance (VII)]], [[Order Block]], [[IFVG (Inverse Fair Value Gap)]]
- [[ORG (Opening Range Gap) & 1st Presented FVG]], [[Judas Swing]], [[ICT Macros & Leading Candles]]
- [[Institutional Order Flow Entry Drill (IOFED)]], [[Partial Profit-Taking & R-Multiple-Skalierung]]
