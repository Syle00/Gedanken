---
tags: [concept, ict, trading-ict, bias]
created: 2026-08-01
updated: 2026-08-23
sources: ["[[Essentials To ICT Daytrading (Source)]]", "[[Intraweek Market Reversals & Overlapping Models (Source)]]", "[[2026-08-18 - Trade Management & Removing The Need To Be Right (Source)|Trade Management & Removing The Need To Be Right (Source)]]"]
---

# New Week Opening Gap (NWOG) Bias

Der NWOG (Kursgap zwischen Freitag-Close und Sonntag-/Montag-Open) dient als wöchentlicher
Bias-Anker für [[ICT Daily Range Session Timing|Daytrades]].

## Regel

- Bleibt der Kurs die gesamte Handelswoche **unterhalb** des NWOG → Bias **bearish**, es werden
  praktisch nur Shorts gesucht.
- Bleibt der Kurs die gesamte Handelswoche **oberhalb** des NWOG → Bias **bullish**, es werden
  praktisch nur Longs gesucht.
- Wird das NWOG intraweek durchbrochen → möglicher **major Intraday/Weekly Shift**, Bias kippt.
- Ausnahme: Trades in ein höher timeframiges Discount-PD-Array werden gegen die NWOG-Bias-Richtung
  gesucht — dort danach wieder die eigentliche Bias-Richtung suchen (visaversa bei Premium-PD-Array).

![[image 232.png]]
*NWOG-Bias-Regel: unterhalb des NWOG nur Shorts, oberhalb nur Longs gesucht.*

## Timing-Beobachtung

- Das Weekly High/Low bildet sich im Normalfall bereits **Montag**, wenn der Preis am Montag
  über/unter dem NWOG tradet.
- **Donnerstag** ist ein wahrscheinlicher Kandidat für ein Reversal, wenn die Woche bis dahin
  konsistent auf einer Seite des NWOG geblieben ist.

![[image 231.png]]
*Donnerstag als typischer Reversal-Kandidat bei konsistenter NWOG-Seite über die Woche.*

![[image 234.png]]
*Das Weekly High/Low bildet sich oft schon am Montag, wenn Preis über/unter dem NWOG tradet.*

## Intraweek Reversal (Montag/Dienstag)

- Tradet Preis bereits Montag/Dienstag **schnell und mit großen Candles** in eine PD, ist das oft ein
  Reversal-Signal (im Verbund mit Bias und Trending Conditions). Dann eine HTF-PD suchen — mindestens
  Daily, bevorzugt Weekly.
- Speed + Magnitude deuten auf Repricing durch große Player hin (Zinsentscheide, Notenbanken, oder
  Spekulation).
- Beispielmuster: großer bearish Candle am Montag erreicht eine PD, Preis kehrt zur "Balanced Price
  Range" zurück, um ein **[[MMXM (Market Maker Buy & Sell Model)|MMXM]]** (Market Maker Buy/Sell Model) zu bilden — ein Lower High am
  Dienstag verringert die Wahrscheinlichkeit etwas, spricht aber oft trotzdem stark dafür.

![[image 206.png]]
*Intraweek Reversal: Preis erreicht innerhalb von 2 Tagen eine tiefere PD — Montag große bearishe
Candle, Dienstag erreicht die PD.*

![[image 209.png]]
*Preis kehrt oft zur Balanced Price Range zurück, um ein MMXM zu bilden.*

## Das NWOG als Montags-Ziel („easiest framework for a Monday")

Aus [[2026-08-18 - Trade Management & Removing The Need To Be Right (Source)|Trade Management & Removing The Need To Be Right (Source)]]
(Live-Trade Montag 17.08.2026, NQ). **Wichtig: das ist nicht die Bias-Regel oben.** Dort ist das
NWOG ein *Richtungsfilter* (Kurs oberhalb → nur Longs), hier ist es ein **Ziel** — ein DOL, auf
den zugehandelt wird, unabhängig davon, von welcher Seite man kommt.

**Vorbedingungen (alle drei):**

1. Der Sonntags-Open läuft **vom NWOG weg**.
2. Das NWOG wird **weder in der Asia-Session (Sonntagabend) noch in London** wieder gehandelt.
3. Keine ausufernde Runaway-Bewegung in eine Richtung.

**Dann** ist der Montags-Trade schlicht der Lauf zurück ins NWOG — ICT: *„a no-brainer type
thing", „it doesn't require a whole lot of thought process."* Zielpunkt ist die **NWOG-Kante**
(das High bei einem Short von oben), nicht C.E. oder Gegenseite.

> ⚠️ **Präzisierung gegen den Wortlaut der Quelle.** ICT formuliert Bedingung 2 als *„it hasn't
> traded to it since it formed"*. Der Abgleich mit eigenen 1s-Daten zum selben Tag zeigt, dass das
> so nicht stimmt: Der Preis fiel **44 Sekunden nach der Sonntagseröffnung auf 30.163,75**, also
> 6,25 Punkte in das Gap (30.154,00–30.170,00) hinein, und lief erst danach weg. **Gefüllt** war es
> nie. Brauchbar ist die Bedingung deshalb nur in der Form **„NWOG noch nicht gefüllt"** — ein
> Antippen der Kante entwertet das Setup nicht.

**Verlauf am 17.08.2026 (eigene 1s-Daten, `raw/marktdaten/2026/08/17.08.2026/`):**

| Ereignis | Zeit (ET) | Preis |
|---|---|---|
| NWOG-High (Sonntags-Open) | So 18:00:00 | 30.170,00 |
| Dip in die Gap-Oberkante | So 18:00:44 | 30.163,75 |
| Wochenhoch (London) | Mo 03:00–08:30 | 30.343,00 |
| **NWOG-High erreicht (Ziel)** | **Mo 09:39:32** | **30.170,00** |
| NWOG vollständig gefüllt | Mo 13:08:58 | 30.154,00 |
| Tagestief | Mo 16:47:45 | 30.054,50 |

Das Setup lieferte, und zwar innerhalb der ersten Handelsstunde — **rund 14 Minuten nachdem ICTs
Aufnahme endete**, in der er die Erreichung noch mit „60 zu 40 dagegen" bewertete.

**Konvergenz mit dem eigenen Backtest.** Die Bias-Regel oben scheitert im Backtest an einer
Bias-intakt-Quote von **7,1 %** — *weil das NWOG fast immer wieder erreicht wird*. Genau das ist
die Prämisse dieses Frameworks. **Derselbe Befund widerlegt die eine Lesart und stützt die
andere**: Das NWOG taugt schlecht als Richtungsfilter und gut als Draw on Liquidity. Für den Algo
(Layer 0) ist damit die Ziel-Lesart die verwertbare, nicht die Filter-Lesart.

> Noch nicht systematisch geprüft: wie oft der Rücklauf **am Montag** (statt irgendwann in der
> Woche) stattfindet und wie oft die drei Vorbedingungen überhaupt zusammen auftreten. Kandidat
> für einen eigenen Lauf in `algo/backtest_nwog.py`.

## Offene Punkte

- ✅ **Erledigt (2026-08-06)**: "PD Array" hat inzwischen eine eigene Seite ([[PD Array]]),
  "Discount PD Array" ist über [[Equilibrium Vs. Discount]] abgedeckt.

## Backtest gegen echte Daten

[[Statistische Muster jenseits der ICT-Konzepte (laufend)]]#5 prüft die Bias-Regel und beide
Timing-Behauptungen hier gegen n=28 Wochen MNQ-Daten: Bias-intakt-Quote nur 7,1 % (das NWOG
wird fast immer wieder erreicht), Wochen-Low bevorzugt tatsächlich Montag, Wochen-High aber
nicht, und die Donnerstag-Reversal-These wird klar widerlegt (Donnerstag ist der
unwahrscheinlichste Tag für beide Extreme). `algo/live_status.py` liefert montags ein
`nwog`-Feld live mit.
