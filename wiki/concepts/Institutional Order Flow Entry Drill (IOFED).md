---
tags: [concept, ict, trading-ict, 2024, entry, macros]
created: 2026-08-10
updated: 2026-08-10
sources: ["[[ICT Gems - How Price Behaves At Specific Times (Source)]]", "[[ICT Gems - Algorithmic Timings With Opening Ranges (Source)]]", "[[ICT Gems - When To Anticipate Price Spooling (Source)]]"]
---

# Institutional Order Flow Entry Drill (IOFED)

Eigenes, benanntes Entry-Modell von ICT für einen sehr spezifischen Fall: ein
[[Fair Value Gap (FVG)|FVG]], von dem man **erwartet, dass es *nicht* vollständig gefüllt wird**.
Statt auf die volle Füllung zu warten (die dann nie kommt), wird ein **Teil-Entry an der Oberkante**
platziert.

> ICT: *"an institutional order flow entry drill is a partial entry into a fair value gap that you
> believe strongly is not likely to completely fill in."*

## Der Mechanismus: ein Tick genügt

Der Trigger ist die Kerze, die das Gap bildet:

- **Limit-Order exakt auf das Low dieser Kerze** legen (bei einem bullishen Setup).
- Es braucht **nur einen einzigen Tick darunter**, um gefüllt zu werden — genau das ist der
  "Drill". Preis muss nicht in das Gap hineinlaufen.
- Ziel ist das darüberliegende Draw on Liquidity, Stop unterhalb des Gaps.

Das nutzt dieselbe Bid/Ask-Mechanik, die ICT auch für Volume Imbalances beschreibt: Um ein Level
tatsächlich zu handeln, muss Preis wegen der Spanne zwischen Bid und Ask **mindestens einen Tick
darüber hinaus** — dieser eine Tick ist der Fill.

## Die Fill-Zone: obere Hälfte, nie die Unterkante

Regel für alle Entries in ein solches Gap, unabhängig vom Drill:

| Zone | Fill-Wahrscheinlichkeit |
|---|---|
| **C.E. (Mittelpunkt) bis Gap-High** | **beste Fills** — hier wird gearbeitet |
| untere Hälfte | unwahrscheinlichster Fill |

> ICT ausdrücklich: *"I am never trying to get a fill at the low end"* — entweder läuft Preis gar
> nicht so tief, oder er läuft hinein, ohne wegen des Spreads zu füllen. Ein Limit an der
> Unterkante ist damit eine Einladung zur Frustration, kein besserer Einstieg.

Der Stop liegt trotzdem jenseits des kompletten Gaps — enger Fill, nicht enger Stop.

## Woran man erkennt, dass das Gap offen bleibt

Die Prognose "dieses Gap füllt nicht" ist keine Intuition, sondern hat ein Kriterium:

**Das Gap entstand beim Ausbruch aus einer Konsolidierung** — idealerweise, nachdem die Stops an
der Konsolidierungsgrenze abgeholt wurden. Dann verhält es sich als
[[Breakaway Gap|Breakaway Gap]] und bleibt offen.

> *"The inefficiencies that stay open are going to act like real support or resistance."*

Gegenprobe vor dem Entry: Stößt Preis das Level ab und beginnt zu brechen, statt es zu
respektieren? Dann fällt die Prämisse und man wechselt in eine tiefere Timeframe (ICT nennt den
**15-Sekunden-Chart**), um die Struktur neu zu lesen.

## Der beste Vorbote: eine BPR im Ziel-FVG

Die klarste Antizipationsregel, aus
[[ICT Gems - Algorithmic Timings With Opening Ranges (Source)]]:

> *"The easiest way to anticipate the institutional order flow entry drill is **if there's a
> balanced price range in the fair value gap that it's trading up into**. **Nine times out of ten**,
> if you're bearish, it's not going to completely close that in."*

Damit hängt der Drill nicht an einem Bauchgefühl, sondern an einer prüfbaren Struktur: Enthält die
relevante Hälfte des Ziel-FVG bereits eine [[Balanced Price Range (BPR)]], ist sie abgearbeitet und
wird nicht erneut gefüllt. Genau dann reicht ein **sehr flacher Lauf über das High** als Einstieg —
statt auf C.E. oder volle Füllung zu warten.

Praktische Reihenfolge:

1. Ziel-FVG bestimmen, in das Preis hineinläuft.
2. Eine Timeframe tiefer prüfen: Liegt in der relevanten Hälfte eine BPR?
3. Wenn ja → Limit knapp jenseits des Extrems, Drill statt Tiefenwarten.

## Skalierung über die Quadranten

Ist das Gap breit genug, wird der Drill zum ersten von mehreren Teilen. ICTs eigenes Beispiel:

1. **6 Kontrakte** per IOFED an der Gap-Oberkante.
2. **+4 Kontrakte**, wenn Preis in den oberen Quadranten oder bis zur C.E. eintaucht.
3. **+5 Kontrakte** bei **einem Tick unter der C.E.** — bewusst, obwohl die ersten beiden Tranchen
   dann leicht im Minus stehen.

Die Logik ist dieselbe wie bei der verteilten IFVG-Bestückung in
[[IFVG (Inverse Fair Value Gap)]]: Der Durchschnittspreis entsteht über das Gap hinweg, nicht auf
einem einzelnen Tick.

## Wenn kein Gap da ist

Der Drill setzt eine Ineffizienz voraus. Fehlt sie (die Kerzen überlappen lückenlos), ist die
Alternative der [[Order Block]] — konkret die Down-Close-Kerze, die Preis nach einem Retracement
abstößt. Siehe die Auswahlregel unter
[[ICT Macros & Leading Candles]] ("Gap oder Order Block oder Short-Term Low").

## Verwandt

- [[Fair Value Gap (FVG)]], [[Breakaway Gap]], [[Volume Imbalance (VII)]]
- [[Order Block]], [[CISD (Change in State of Delivery)]]
- [[ICT Macros & Leading Candles]] — der Drill wird bevorzugt **innerhalb** eines Macro-Fensters ausgeführt
- [[Optimal Trade Entry (OTE)]] — das allgemeinere Entry-Modell daneben
- [[ICT Gems - How Price Behaves At Specific Times (Source)]]
