---
tags: [concept, ict, trading-ict]
created: 2026-08-02
updated: 2026-08-10
sources: ["[[Kurz Notizen (Source)]]", "[[Algorithmic Price Delivery Continuum (Source)]]", "[[ICT Gems - Balanced Price Ranges Inside Fair Value Gaps (Source)]]", "[[ICT Gems - Algorithmic Timings With Opening Ranges (Source)]]"]
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

## Welche Hälfte man überhaupt anschaut (2025-Ergänzung)

Aus [[ICT Gems - Balanced Price Ranges Inside Fair Value Gaps (Source)]] — die Regel, welche
Hälfte des FVG untersucht wird, war oben implizit; hier steht sie explizit:

| FVG-Typ | zu untersuchende Hälfte |
|---|---|
| **bearish (SIBI)** | die **obere** Hälfte |
| **bullish (BISI)** | die **untere** Hälfte |

**Warum diese Hälfte "balanced" wird**: Läuft Preis dort im Lower Timeframe **hin und her** —
hinein, wieder heraus, erneut hinein, mit Bodies, die das Niveau respektieren — dann ist diese
Hälfte **effizient beliefert** worden. Sie ist damit **nicht** mehr ineffizient, und Preis hat
**keinen Grund**, dorthin zurückzukehren.

**Die andere Hälfte ist die eigentliche Ineffizienz**: Sie sah nur **einseitige** Lieferung (bei
einem SIBI nur Sellside) und ist deshalb der Teil, der noch angeboten werden muss. ICT: Das
Anliefern bis zum **Mittelpunkt** genügt, um das Coding des Algorithmus zu erfüllen —
*"delivering price up to the halfway point satisfies the coding in that algorithm, it need not go
any higher."*

> **Kernaussage**: Ein 15-Min-FVG muss seine obere Hälfte **nicht** füllen, wenn diese bereits
> balanced ist. Das "echte" FVG ist dann nur der untere Teil — auf dem 5-Min-Chart sichtbar. Wer
> auf die volle Füllung wartet, wartet auf etwas, das nicht kommt.

## Was man praktisch damit macht

### 1. Stop-Platzierung

Weil die balanced Hälfte nicht mehr gefüllt wird, darf der Stop **hinein**:

- **Oberer Quadrant** der balanced Zone — ICTs Standardwahl.
- **Konservativer**: knapp **über** der gesamten Zone.
- **Nicht an der C.E.** — zu nah; Spread und Wicks holen einen dort heraus (*"we allow the wick to
  do damage"*).

### 2. Re-Entry nach einem Stopout

Wird man trotzdem ausgestoppt, gilt die Prämisse weiter, **solange Preis in die andere (noch
ineffiziente) Hälfte zurückgehandelt hat** und die balanced Hälfte weiterhin nicht gefüllt werden
sollte:

> **Erneut einsteigen, aber mit der halben Kontraktzahl** des ursprünglichen Trades, Stop wieder im
> oberen Quadranten oder knapp über dem High.

Das ist eine ausdrücklich benannte Size-Reduktion beim Re-Entry — vgl.
[[Verlust-Mitigation durch reduzierte Re-Entry-Size]].

### 3. Die BPR macht das Gap zum Breakaway Gap

Bleibt der balanced Teil offen, ist das Gap ein [[Breakaway Gap]] — *"it's not likely to fill, so
we're going to likely see a lot of movement lower"*. Und weiter unten in derselben Bewegung folgt
dann auf halber Strecke das **Measuring Gap** (siehe [[Implied Dealing Range]]).

### 4. Sie ist der beste Vorbote eines IOFED

Die klarste Formulierung dieser Verbindung stammt aus
[[ICT Gems - Algorithmic Timings With Opening Ranges (Source)]]:

> *"The easiest way to anticipate the institutional order flow entry drill is **if there's a
> balanced price range in the fair value gap that it's trading up into**. **Nine times out of ten**,
> if you're bearish, it's not going to completely close that in."*

Praktisch heißt das: Statt auf C.E. oder volle Füllung zu warten, genügt ein **sehr flacher Lauf
über das High** als Einstieg — siehe [[Institutional Order Flow Entry Drill (IOFED)]].

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
