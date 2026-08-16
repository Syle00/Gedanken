---
tags: [model, ict, trading-ict, daytrade, sessions]
created: 2026-08-02
updated: 2026-08-16
sources: ["[[Kurz Notizen]]", "[[ICT Silver Bullet (Source)]]", "[[2023-06-20 - ICT Executions June 20, 2023 NQ Short Silver Bullet (Source)]]", "[[2023-06-08 - ICT Executions June 8, 2023 ES Long Silver Bullet (Source)]]", "[[2024-09-13 - ICT Executions September 13, 2024 NQ Short Silver Bullet (Source)]]", "[[2026-08-15 - The Week In The Life Cycle Of Price (Source)|The Week In The Life Cycle Of Price (Source)]]"]
---

# Silver Bullet Model

Reines **Time-based Model** — nur innerhalb der drei festen Zeitfenster tradebar. Der eigentliche
Silver-Bullet-Move beginnt **innerhalb des Macros vor** dem eigentlichen Silver-Bullet-Fenster,
nicht erst mit dessen Beginn.

## Die drei Fenster (NY Zeit)

| Fenster | Zeit | Session |
|---|---|---|
| London Silver Bullet | **3:00–4:00 Uhr** | London |
| NY AM Silver Bullet | **10:00–11:00 Uhr** | NY-Session |
| NY PM Silver Bullet | **14:00–15:00 Uhr** | NY PM |

Das Zeitfenster ist nur für den **Einstieg** relevant — der Trade muss nicht innerhalb des Windows
fertig sein und darf über die Stunde hinaus weiterlaufen. ICT nutzt bevorzugt den **5-Min-Chart**
für den Entry, kombiniert mit PD Arrays aus dem 15-Min- und 1H-Chart. Muss zusätzlich mit
**Confluenz** abgesichert werden: andere PD Arrays/Targets wie NWOG/NDOG, Midnight Opening Fibs
oder das 1. presented FVG. Siehe [[ICT Silver Bullet (Source)]].

## Ablauf

- Referenzbeispiel: das [[ICT Macros & Leading Candles|Macro]] **9:50–10:10** liefert Displacement +
  [[Fair Value Gap (FVG)|FVG]]. Danach wird dieses FVG als [[IFVG (Inverse Fair Value Gap)|IFVG]] in
  die **entgegengesetzte Richtung** genutzt — der sogenannte **"2022 Entry"** (typischerweise im
  5-Min-Chart).
- Der Move innerhalb dieses vorgelagerten Macros ist **selten der vollständige Move** — er startet
  lediglich. Laut ICT läuft der eigentliche Move über die **volle folgende Stunde**, wodurch
  theoretisch auch ein deutlich späterer Einstieg möglich ist, solange der Move über die Stunde
  weiterläuft.
- Der Move endet an einem logischen Level — Liquidity oder ein Quadrant eines FVG (siehe
  [[Chain of Custody (Q-Validation)]]).
- ICT würde laut Quelle auch dann noch shorten, wenn der Price-Run bereits fast vollendet wirkt (z.B.
  kurz vor halb 11) — solange ein klarer Liquidity Pool als Ziel erkennbar bleibt.

![[Kurz Notizen - Late Shorting Liquidity Pool Example.png]]
*ICT würde hier trotz fast vollendetem Price Run noch shorten, da kurz davor ein offensichtlicher Liquidity Pool liegt.*

## Trade Management (eigene Ausführungsregel, kein ICT-Quellenzitat)

Zusatzregel zur reinen Entry-Logik oben, so wie im Algo-Backtest (`algo/rules.py::plan_trade`,
`algo/backtest_ensemble.py::EnsembleStrategy`) umgesetzt:

- **Mindestziel:** Setup wird nur genommen, wenn zwischen Entry und Target mindestens
  **10 Handle/Punkte** Potenzial liegen. Ohne genug Abstand: kein Trade, unabhängig davon, ob
  sonst alle Kriterien (Fenster, FVG, Zielliquidität) erfüllt sind.
- **Partial:** am **ersten Swing-Hoch** (long) bzw. **ersten Swing-Tief** (short), das nach dem
  Entry entsteht, wird ein Teil der Position geschlossen (Backtest-Default 50%, siehe
  `EnsembleStrategy.partial_portion` — die genaue Aufteilung war nicht vorgegeben).
- **Breakeven:** sobald das Partial genommen wurde, wandert der Stop auf den Entry-Preis. Der
  Rest der Position läuft drawdown-frei bis Stop oder Target weiter.
- **Positionsgröße:** richtet sich nach dem Kontoguthaben, nicht nach fixer Kontraktzahl —
  siehe [[Risikomanagement (1% pro Trade)]] (`EnsembleStrategy._risk_size`).

Diese Regel ist reines Trade-Management, keine ICT-Quellenaussage — sie ergänzt, ersetzt aber
nicht die Entry-Kriterien aus dem Abschnitt oben.

> ✅ **Teilweise durch eine Quelle gedeckt (2026-08-10).** Die 10-Handle-Schwelle war bislang als
> reine Eigenregel markiert. [[ICT Gems - ICT Teaches how to Scalp Every 1 Hour Candle (Source)]]
> nennt für NASDAQ-Scalps **exakt dieselbe Zahl**: *"if I can't at least make 10 handles, I'm not
> willing to take the trade."* Für den **Silver Bullet speziell** nennt ICT dagegen
> [[ICT Gems - Blending Silver Bullets and Macros (Source)|an anderer Stelle]] nur **5 Handles**.
> Die Eigenregel ist damit nicht widerlegt, sondern **konservativer** als ICTs SB-Vorgabe — das ist
> eine bewusste Entscheidung und bleibt so.

## Was der Silver Bullet ausdrücklich *nicht* ist (2024-Ergänzung)

Aus [[ICT Gems - Blending Silver Bullets and Macros (Source)]] — ICT korrigiert dort zwei
verbreitete Überdehnungen des Modells:

- **Das Ziel sind 5 Handles, nicht die Tagesrange.** *"You're not demanding that you capture the
  daily range, you're not demanding that it goes to your technical target — you're only expecting
  it to give you your five handles."* Dass daraus manchmal das Tagestief und ein Lauf über Stunden
  wird, ist Zugabe, nicht Anspruch.
- **Das Setup gilt als erfüllt, wenn die Range da war — auch ohne Zielerreichung.** Liefert der
  Trade über 5 Handles, erreicht aber den anvisierten Liquidity Pool nicht, ist das Modell
  **nicht** gebrochen. ICT: *"you don't need to be right about your levels, you just need to be
  right about: does it offer the range?"*

**Präzisierung der Entry-Bedingung**: Das FVG muss **entgegengesetzt** zur erwarteten Zielrichtung
liegen. Bearish: Displacement nach unten → Retracement **hinauf** ins FVG → dann Lauf zur Sellside.
Bullish spiegelbildlich: Displacement nach oben hinterlässt ein FVG **unter** Markt → Rücklauf
hinein → dann Lauf zur noch unberührten Buyside.

**Einzelnes Low vs. Relative Equal Lows**: Liegt unter dem Einstieg nur ein **einzelnes** Low, ist
ein aggressiver Entry vertretbar. Liegen **Relative Equal Lows** vor, ist dort Sellside gebunkert —
dann ist damit zu rechnen, dass sie zuerst abgeholt wird, bevor der eigentliche Move läuft.

**Zeitliche Einordnung**: Das SB-Fenster 10–11 Uhr ist laut ICT der **letzte Abschnitt** des
AM-Session-Moves (8:30–11:00, ausdehnbar bis 12:00) — man sitzt "im Herzen der Bewegung", ohne
deren Inception erwischt zu haben. Genau deshalb funktioniert das Modell ohne Einstieg am
Bewegungsanfang.

## Bezug zu Nachbar-Fenstern

- Das **NY-AM-Fenster (10–11 Uhr)** überlappt mit dem Vorlauf zum [[NY Lunch Macro Model|NY Lunch
  Macro]] (Ausführung 10:50–11:10) — beide liegen im selben Vormittagsblock, sind aber getrennte
  Setups.
- Das **PM-Fenster (14–15 Uhr)** bestätigt [[NY PM Trend]] ("Beginnt typischerweise um 2 Uhr =
  Silver Bullet").
- ✅ Damit ist der bisher offene Punkt geklärt, dass die AM-/Lunch-Fenster noch nicht als eigene
  Zeiten belegt waren.

## Chart-Label-Bestätigung & Positionsgröße (ICT Executions, mehrere 2023/2024)

[[2023-06-20 - ICT Executions June 20, 2023 NQ Short Silver Bullet (Source)]] zeigt eine im Chart
eingezeichnete Box, beschriftet **"ICT AM Silver Bullet"**, exakt im 10:00–11:00-ET-Fenster —
direkteste bisherige Primärquellen-Bestätigung der Fensterbezeichnung. Drei Executions-Beispiele
([[2023-06-08 - ICT Executions June 8, 2023 ES Long Silver Bullet (Source)]] 20 Kontrakte,
[[2024-09-13 - ICT Executions September 13, 2024 NQ Short Silver Bullet (Source)]] 18 Kontrakte,
[[2023-06-20 - ICT Executions June 20, 2023 NQ Short Silver Bullet (Source)]] 10 Kontrakte) zeigen
durchweg zweistellige Kontraktzahlen — konsistent höher als die meisten reinen Macro-Fenster-Trades
in [[Partial Profit-Taking & R-Multiple-Skalierung]].

## Vollständige Entry-Anatomie (Live-Trade 15.08.2026, NQ Short)

Aus [[2026-08-15 - The Week In The Life Cycle Of Price (Source)|The Week In The Life Cycle Of Price (Source)]] —
der am detailliertesten dokumentierte SB-Entry im Vault, weil ICT jede einzelne Bestätigungsstufe
benennt statt nur das Ergebnis zu zeigen. **Bearisher SB im AM-Fenster**, obwohl die Woche bullish
war: Ziel war die [[TGIF (Thank God its Friday)|TGIF]]-Zone.

**Kontext vor dem Fenster** — Preis stand in einem Daily Premium FVG, hatte alle Aufwärtsziele der
Woche erreicht, und über dem Freitags-Vormittagshoch lagen **guarded** Relative Equal Highs
(im Macro 9:50–10:10 nicht genommen, siehe [[Open Float & Liquidity Pools]]).

**Die Bestätigungskette, in dieser Reihenfolge:**

1. **Body-Close unter dem 9:30-Opening-Price** — erste Bestätigung, dass die REH nicht angesteuert
   werden. Danach Struktur High → Lower High → Lower High.
2. **[[Rejection Block]] wird verletzt**: Preis läuft an ihn heran, kann aber keinen Body darüber
   schließen → *„check in the box that says okay, now we're starting to see it likely to be failing."*
3. **BISI wird überhandelt → [[IFVG (Inverse Fair Value Gap)|IFVG]]**: Das darunterliegende
   Buyside-Balance-Gap wird von oben durchhandelt und kehrt seine Rolle um. Bestätigungskerze:
   öffnet, läuft hoch, **berührt das High der IFVG nicht**, schließt tiefer und außerhalb — die
   bearishe Spiegelung der [[Gladhanding]]-Regel.
4. **Zweite Testkerze** — dieselbe Reaktion nochmal. Erst danach steigt ICT ein, ausdrücklich wegen
   der guarded Liquidity darüber: *„I just want to have a little bit more behind me."*
5. **Entry an der C.E. eines [[Suspension Block|Suspension Blocks]]** (kleines FVG) statt am
   naheliegenden großen FVG, zusätzlich orientiert an der C.E. des längsten Wicks links davon.
6. **Nach dem Entry**: Der Wick oberhalb wirkt als Body-Grenze — keine Bodies in seiner oberen
   Hälfte, siehe [[Institutional Order Flow (Body vs Wick)]]. Die Konsolidierung darunter war
   „errant price action", kein Setup-Bruch.

**Ausführung und Größe:**

- **2 Kontrakte, Ein- und Ausstieg in einem Stück** — die Größe ergab sich **allein aus der nötigen
  Stop-Weite** (Stop musste bis zur C.E. reichen): *„because the stop, it kind of warrants me only
  using two contracts."* Bestätigt [[Risikomanagement (1% pro Trade)]]: Stop-Distanz bestimmt
  Kontraktzahl, nicht umgekehrt — und erklärt die Abweichung zu den zweistelligen Kontraktzahlen
  der 2023/2024-Beispiele oben.
- **Ziel ~25 % der Weekly Range** (Mitte der TGIF-Zone), zusammenfallend mit dem Vormonats-High.
  Das letzte Ziel wurde bewusst liegen gelassen — *„low hanging fruit", „get the big piece of the
  meat in the middle"* — wegen Headline-Risiko.
- **Bei größerer Position** hätte ICT gestaffelt: Teilgewinne an 20 %, am Midpoint, unter dem Low
  und an 30 %. Vgl. [[Partial Profit-Taking & R-Multiple-Skalierung]].

**Zeitfenster-Präzisierung**: Der Entry lag bei **10:11 ET**, also *eine Minute nach* dem Macro
9:50–10:10. ICT hält das ausdrücklich für unproblematisch — liegt eine PD Array so nah am
Macro-Ende, ist der Einstieg dort legitim. Ein [[CISD (Change in State of Delivery)|CISD]]/Order
Block außerhalb des Macros wäre ein gültiger Pyramiding-Entry gewesen.

> **Modell-Auswahl statt Modell-Zwang**: ICT betont, dass nicht jedes Modell an jedem Tag
> funktioniert — nicht weil es versagt, sondern weil die Marktbedingungen nicht passen
> („a tool for every procedure"). Welches Modell in Frage kommt, entscheidet er **vorab** über das
> erwartete Wochenprofil (siehe [[Market Maker Manipulation Templates]]). Reversal-Modelle fallen
> in einem Continuation-Umfeld weg. Relevant für `algo/backtest_ensemble.py`: ein Ensemble, das
> alle Modelle jeden Tag gleich gewichtet, bildet diese Vorauswahl nicht ab.

## Verwandt

- [[ICT Macros & Leading Candles]], [[Fair Value Gap (FVG)]], [[IFVG (Inverse Fair Value Gap)]]
- [[Modell 22]] — ebenfalls ein MSS+SIBI/IFVG-basierter Trigger
- [[NY PM Trend]], [[ICT Daily Range Session Timing]], [[ICT Killzones]]
- [[Kurz Notizen (Source)]], [[ICT Silver Bullet (Source)]]
- [[Meine Strategien (Übersicht)]], [[Risikomanagement (1% pro Trade)]]
- [[Open Float & Liquidity Pools]] — Timeframe-Hierarchie zur Pool-Erkennung (15M Bellwether, 1M für große Pools)
