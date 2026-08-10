---
tags: [concept, ict, trading-ict, core-content, month-09, daily-range, trade-management]
created: 2026-08-10
updated: 2026-08-10
sources: ["[[ICT Mentorship Core Content - Month 09 - Bread & Butter Sell Setups (Source)]]", "[[ICT Mentorship Core Content - Month 09 - Bread & Butter Buy Setups (Source)]]", "[[ICT Mentorship Core Content - Month 09 - Trading Market Reversals (Source)]]"]
---

# Average Daily Range (5-Tage-ADR)

Die durchschnittliche Tagesrange der **letzten fünf Tage**, projiziert als ADR-High und ADR-Low auf
den laufenden Tag. In Month 09 ist sie ICTs Standardwerkzeug für die **Reichweite** eines Daytrades
— komplementär zu [[Filling The Numbers (4 Level pro Tag)]], das dieselbe Frage über Level statt
über einen Durchschnitt beantwortet.

## Die Grundwarnung

> **Die ADR ist ein Durchschnitt, keine Barriere.** ICT ausdrücklich: *"the average daily range is
> not a barrier, it's not a force field, it's not going to stop price."* Sie muss nicht gefüllt
> werden, kann knapp verfehlt oder deutlich überschossen werden.

Wer alles am ADR-High glattstellt, verzichtet systematisch auf die Tage mit doppelter Range.

## Wann die ADR verdoppelt wird

Konkrete Bedingungen für einen Tag mit ~2× ADR:

- Ein **längerfristiger Trend** läuft **und** ein Intermediate-Term-Swing hat gerade begonnen →
  ein großer Impuls-Swing kann die Tagesrange verdoppeln.
- Besonders wahrscheinlich, wenn die **ADR unter 60 Pips** liegt — ICTs eigener Erfahrungswert und
  Filterwert ("60 Pips is like a number I like").
- **Kapitulation**: Ein Intermediate-Term-Swing vollendet sich an einer HTF-Array und trifft auf
  High-Impact-News — die Bewegung holt das Ziel in *einem* Tag und läuft weit über die ADR hinaus.

## Timing-Signale aus dem Füllzeitpunkt

Wann die ADR gefüllt wird, sagt mehr aus als ob:

| Füllzeitpunkt | Lesart |
|---|---|
| **Noch nicht gefüllt beim NY-Open, gefüllt erst im London Close** | Idealfall — Range-Expansion steht noch aus, der Tag hat noch Weg |
| **Bereits am/vor dem NY-Open gefüllt** | ADR wird sehr wahrscheinlich **überschritten**, besonders bei High-Impact-News nach dem Aktien-Open (9:30 NY) |
| **ADR-Ziel vor 10:00 NY erreicht** | 80 % der Position realisieren, Rest für Range-Expansion laufen lassen |

## ICTs Exit-Modell: 15 Pips vor der ADR

Die praktisch wichtigste Regel dieser Seite:

> **Den Großteil der Position rund 15 Pips *vor* dem ADR-High/-Low realisieren.**

Begründung ist explizit ein **Datenqualitäts-Argument**, kein Handelsgefühl: Die Tages-Highs/-Lows
unterscheiden sich zwischen Datenanbietern und Brokern; niemand hat den absoluten Wert. Ein Puffer
von 15 Pips macht den Exit unabhängig von dieser Streuung. ICTs Formulierung: *"It's not about
being right, it's about being profitable."*

> Für den Vault-Kontext relevant: Das ist dasselbe Argument, das hinter der Nulltoleranz bei
> Marktdaten in diesem Projekt steht — Anbieter-Drift an den Extremen ist real und muss im Modell
> abgefedert werden, statt ignoriert zu werden.

## Als Filter für den London-Close-Scalp

Die ADR ist die Eintrittskarte für den Retracement-Scalp am London Close (Details in
[[Market Reversal Types]] und [[Bread & Butter Setups]]):

- Voraussetzung: NY und London liefen **in dieselbe Richtung** und die ADR wurde erreicht bzw.
  überschritten.
- Zeitfenster **10:30–13:00 NY**, Ziel **20–30 % der Tagesrange** als Retracement.

> ⚠️ **Zahlen-Abweichung innerhalb desselben Monats.** Die Reversal-Lektion nennt für denselben
> Trade **10:00–12:00 NY**, ein Retracement von **~20 %** und einen ADR-Überschuss von
> **1,25–1,33×**; die beiden Bread-&-Butter-Lektionen nennen **10:30–13:00 NY** und **20–30 %**
> ohne festen Überschuss-Faktor. Beide Fassungen stammen von ICT aus Month 09 — hier bewusst
> nebeneinander stehengelassen statt eine zu bevorzugen; für einen Backtest sind beide Varianten
> zu prüfen.

## Verwandt

- [[Filling The Numbers (4 Level pro Tag)]] — Reichweite über Level statt über Durchschnitt
- [[Bread & Butter Setups]] — nutzt die ADR als Ziel und als Exit-Trigger
- [[Market Reversal Types]] — London-Close-Scalp mit ADR-Filter
- [[ICT Daily Range Session Timing]], [[Flout (15-00 NY Range)]]
- [[20 Pips Per Day]] — "ADR noch offen" als Pflichtbedingung des NY-Expansion-Musters
