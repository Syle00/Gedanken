---
tags: [model, ict, trading-ict, daytrade]
created: 2026-08-01
updated: 2026-08-10
sources: ["[[Bread & Butter Buy Setups (Source)]]", "[[Bread & Butter Sell Setups (Source)]]", "[[ICT Mentorship Core Content - Month 09 - Bread & Butter Buy Setups (Source)]]", "[[ICT Mentorship Core Content - Month 09 - Bread & Butter Sell Setups (Source)]]"]
---

# Bread & Butter Setups

Kern-Daytrade-Modell für Buy- und Sell-Setups (Sell ist strukturell das Spiegelbild von Buy).

## Buy-Variante (Bias bullish)

1. **Sweep-Entry**: Sell-Stops/Liquidity unter einem alten Low werden genommen, Target eine höher
   liegende Higher-Timeframe-PD.
2. **Turtle-Soup-Entry**: [[Turtle Soup]] in ein FVG/Retracement, das Buyer mit engem SL aus dem Markt
   drängt, Target ebenfalls die höhere PD.

Typisches Muster: [[Accumulation & Reaccumulation Model|Accumulation]] (Low genommen → schnelle
Expansion) oder Reaccumulation (Dip zurück ins Discount für Reentry).

### Session-Fahrplan (bullish)

- Kleine Asia-Session (je kleiner desto besser).
- London bildet die [[Judas Swing|Judas]]-Bewegung und das Tages-Low, oder nimmt die Asia-Liquidität.
- Bestätigt London den bullishen Bias + kleine Asia-Session + Judas ab 0 Uhr nach unten → Erwartung:
  weiter bullish in NY, außer eine Higher-Timeframe-PD liegt im Weg.
- **08:20 NY (CME Open)**: klassisches Judas-Fenster.
- Target: 60-Min- oder 4H-PD, daher ist der 1H-Chart entry-relevant.
- Waren London **und** NY AM beide bullish, wird in **London Close (10:30–13:00)** nach Shorts gesucht.
- Asia Open selbst gilt als zeitlich nicht relevanter Faktor.

## Sell-Variante (Bias bearish, spiegelbildlich)

- **Offset Distribution**: altes High wird genommen → bearish.
- **Redistribution**: Retracement in ein (Daily-)FVG vor Fortsetzung nach unten.
- Erwartetes Retracement 5–7 Uhr vor dem NY-Move.
- Judas erneut um 08:20 NY (CME Open).

## Die vier Price Engine Models (Video-Vollfassung 2022)

Aus den beiden Video-Lektionen
[[ICT Mentorship Core Content - Month 09 - Bread & Butter Buy Setups (Source)|Buy Setups]] und
[[ICT Mentorship Core Content - Month 09 - Bread & Butter Sell Setups (Source)|Sell Setups]]. ICT
benennt die Mechanik hinter den oben skizzierten Mustern als **Price Engine Models** — je zwei pro
Programmrichtung. IPDA fährt in einem Buy Program *eines von beiden*, nie etwas anderes.

**Buy Program**

| Modell | Mechanik | Zweck |
|---|---|---|
| **Offset Accumulation** | Repricing **unter ein altes Low**; die dort liegenden Sell-Stops werden ausgelöst und liefern die Gegenpartei-Verkäufer | Bestehende Long-Holder auszahlen bzw. neue Verkäufer zu Discount-Preisen induzieren |
| **Re-accumulation** | Repricing **tiefer in eine Fair-Value-Discount-Array**; zu eng gestoppte Longs werden herausgedrückt | Neue Long-Positionen zu Discount aufbauen; folgt oft direkt auf einen Sell-Stop-Raid |

**Sell Program** (exakte Spiegelung)

| Modell | Mechanik | Zweck |
|---|---|---|
| **Offset Distribution** | Repricing **über ein altes High**; Buy-Stops werden zu Market-Orders und liefern die Käufer | Bestehende Short-Holder auszahlen bzw. Käufer zu Premium-Preisen induzieren |
| **Redistribution** | Repricing **höher in eine Premium-Array**; zu eng gestoppte Shorts werden herausgedrückt | Neue Shorts zu Premium aufbauen; folgt oft auf einen Buy-Stop-Raid |

Beide Offset-Modelle **laufen schnell ab** und müssen an markanten Intraday-Highs/-Lows
antizipiert werden. Die Re-/Redistribution-Variante entspricht typischerweise einem
[[Optimal Trade Entry (OTE)|OTE]]. Über den Open Float, der das überhaupt ermöglicht, siehe
[[Open Float & Liquidity Pools]].

## Realistische Scalp-Kennzahlen

ICT nennt sie explizit als Erwartungsrahmen — nützlich als Sanity-Check für jede Umsetzung:

- **Haltedauer**: 1–2 Stunden, meist deutlich weniger; 2 Stunden als Obergrenze.
- **Ertrag**: 15–30 Pips pro Trade.
- **Timing-Chart**: 5 Minuten.
- **Frequenz**: rund **eine Gelegenheit pro Session** (London / NY / London Close / Asia), aber
  nicht in jedem Paar — daher einen Korb von **4–5 Paaren** beobachten.
- **RR**: typischerweise **1:1**. ICT beschönigt das nicht: *"which isn't hot"*.
- **Risiko**: 0,5 % bis 1 % pro Trade; 1 % erst mit wachsender Routine.
- **Orderart**: Entries mit **Market-Orders**, Exits mit Limit-Orders.
- **Nur in Killzones** handeln — bei Limit-Entries kann ein Fill sonst in die tote Zone rutschen
  (London Lunch 5:00–7:00 NY oder nach 10:00 NY).

## Session-Fahrplan eines Up-Close-Tags

Ergänzt den Fahrplan oben um Größenordnungen:

1. **Open** liegt am oder nahe dem **Low** der Tagesrange; ein kleiner Rutsch unter den Opening
   Price ist normal (0 GMT bzw. Midnight-Candle NY).
2. **London Open** setzt das erste Bein nach oben und liefert **40–60 % der Tagesrange** bis
   5:00 NY.
3. **5:00–7:00 NY (London Lunch)**: Retracement oder Konsolidierung.
4. **NY Open** setzt fort, Expansion typischerweise bis **10:00 NY**.
5. **10:00–12:00 NY**: Tages-High bildet sich am oder über dem projizierten
   [[Average Daily Range (5-Tage-ADR)|ADR]]-High, danach Retracement und Close unter dem High.

> ICT relativiert Punkt 5 selbst: An hochexplosiven Tagen stoppt weder 10:00 noch 11:00 noch 13:00
> den Preis — er kann bis zum **Bond Close (15:00 NY)** durchlaufen.

## Judas-Fenster je Session

Jede Session hat ihre eigene Protraction — das ist der eigentliche Entry-Taktgeber:

| Session | Judas-Fenster (bullisher Tag) |
|---|---|
| **Asia** | 0 GMT / 20:00 NY — kleiner Rutsch unter ein spätes Swing-Low der Vorsession |
| **London** | nach der Midnight-Candle NY |
| **New York** | **8:20 NY (CME Open)** — Judas nach unten, danach kaufen |
| **London Close** | Rally **nach 10:00 NY** bildet das Tages-High (Sell-Seite) |

## Trade-Management an der ADR

- **ADR-Ziel vor 10:00 NY erreicht** → **80 % realisieren**, kleinen Rest für eine mögliche
  Verdopplung der Range laufen lassen.
- Grundsätzlich den Großteil **15 Pips vor** dem ADR-Level schließen (Datenanbieter-Streuung,
  siehe [[Average Daily Range (5-Tage-ADR)]]).

## London-Close-Scalp im Detail

- **Bedingungen**: NY und London liefen **in dieselbe Richtung**, das ADR-Level wurde erreicht
  (idealerweise überschritten), und es ist mindestens **10:30 NY**.
- **Fenster**: 10:30–13:00 NY.
- **Entry**: 5-Min-**Failure Swing** am Tages-High plus [[Order Block|Bearish Order Block]]
  (spiegelbildlich am Low mit Bullish OB).
- **Stop**: 10 Pips über dem Tages-High.
- **Ziel**: **20–30 % der gesamten Tagesrange** als Retracement — auf einem Fib vom Tages-/London-Low
  bis zum ADR-High sind das die Level **0,20 und 0,30**.
- **Deckel**: 1:1 RR, **nicht mehr als 20 Pips** anstreben.
- Nebenprodukt derselben Messung: An einem Up-Close-Tag liegt der **Tagesschluss** in der Regel
  zwischen dem 0,20- und 0,30-Fib — oder direkt am High.

> ICT handelt den London Close im Forex **selbst nicht mehr** (zu wenig Ertrag, zu oft ausgestoppt)
> und lehrt ihn der Vollständigkeit halber; auf dem **S&P** hält er ihn für deutlich attraktiver.
> Für die Zahlen-Abweichung zur Reversal-Lektion siehe [[Average Daily Range (5-Tage-ADR)]].

## Asia-Scalp — mit ausdrücklicher Warnung

- Entry am oder knapp jenseits des 0-GMT-Opening-Price, Erwartung **15–20 Pips**.
- **Volle Exits**, kein Teilverkauf, kein zweites Bein erwarten.
- ICTs eigener Einwand: Man verlangt hier Ertrag von genau der Range, von der man gleichzeitig
  hofft, dass sie **eng** bleibt (siehe [[Asian Range]]) — ein Zielkonflikt in den eigenen Regeln.
  Er handelt Asia nur, wenn ein HTF-Discount-/Premium-Level in NY knapp verfehlt wurde und Asia den
  Rest liefern kann.

## Scalping als Werkzeug, nicht als Stil

- **Zeitfenster mit der höchsten Trefferwahrscheinlichkeit**: **Montag, Dienstag, Mittwoch**, in
  London Open und NY Open — nicht London Close, nicht Asia.
- **Als Hedge**: Statt eine laufende größere Position bei erwartetem Retracement zu schließen, ein
  **korreliertes Paar** in Gegenrichtung scalpen.
- **Als "save all"**: Wurde der ideale Entry am Tages-High verpasst, auf den 5-Min-Chart wechseln
  und über FVG/Bearish OB doch noch einsteigen.
- **Kontowachstum**: 1 % Risiko bei 1:1 in London **und** in NY = 2 % an einem Tag. ICTs Rahmen
  dazu: 25–30 Pips pro Woche verdoppeln das Konto über ein Jahr.
- **Reihenfolge-Warnung**: Der 5-Min-Chart kommt **zuletzt**. HTF-PD-Arrays sind der Katalysator,
  der Preis zieht; die Intraday-Arrays liefern nur Timing und Preis. Ohne den HTF-Unterbau ist
  Scalping laut ICT "not the answer but a problem".

## Verwandt

- [[Turtle Soup]], [[Judas Swing]], [[Accumulation & Reaccumulation Model]]
- [[ICT Daily Range Session Timing]]
- [[Average Daily Range (5-Tage-ADR)]], [[Filling The Numbers (4 Level pro Tag)]]
- [[Optimal Trade Entry (OTE)]], [[Open Float & Liquidity Pools]], [[ICT Killzones]]
- [[ICT Mentorship Core Content - Month 09 - Bread & Butter Buy Setups (Source)]],
  [[ICT Mentorship Core Content - Month 09 - Bread & Butter Sell Setups (Source)]]
