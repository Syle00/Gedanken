---
tags: [concept, ict, trading-ict, 2026]
created: 2026-08-01
updated: 2026-08-10
sources: ["[[From Vision To Execution (Source)]]", "[[2026-07-31 - Market Review NQ July 31, 2026 (Source)|Market Review NQ July 31, 2026 (Source)]]", "[[2026-08-07 - Case Study With NonFarm Payroll & NQ Futures (Source)|Case Study With NonFarm Payroll & NQ Futures (Source)]]"]
---

# ICT Macros & Leading Candles

Zu bestimmten Uhrzeiten innerhalb der Handelssession ("Macros", Beispiel aus der Quelle:
**9:50–10:10**) achtet ICT gezielt auf **Leading Candlesticks** — Candles, die sich durch
ungewöhnliche Größe auszeichnen und sich genau zur "richtigen" Zeit gebildet haben. Diese gelten
als besonders aussagekräftig für die weitere Preisrichtung.

![[image 3.png]]
*Leading Candlesticks innerhalb der Macro-Zeit 9:50–10:10.*

## Zusatzregeln (aus derselben Quelle)

- **Overnight-Liquidity**: es wird **immer** davon ausgegangen, dass sie genommen wird, außer Preis
  zeigt eindeutig etwas anderes. Bilden sich Equal Highs/Lows über Nacht, ist das der erste
  [[AMD Cycle (Accumulation – Manipulation – Distribution)|DOL]] für die (NQ-)Session.
- **Schwaches FVG**: sehr klein **und** ohne genommene Liquidity dahinter = ein gewöhnliches Gap,
  keine belastbare PD Array.

  ![[image 4.png]]
  *Nicht starkes FVG: sehr klein und ohne genommene Liquidity — für ICT nur ein gewöhnliches Gap.*
- Ein FVG mit **Purge** (vorheriger Liquidity-Sweep) innerhalb der [[IPDA Data Ranges]] gilt als
  besonders starke PD Array.

## 8:30 als algorithmischer Fixzeitpunkt (2026-Ergänzung)

Unabhängig vom regulären 20-Minuten-Macro-Raster (xx:50–x0:10) ist **8:30 Uhr NY** ein feststehender
News-Release-Zeitpunkt (z.B. viele US-Konjunkturdaten) und dadurch verlässlich volatil — auch ohne
dass ein Macro-Fenster dort offiziell benannt ist. Quelle: [[2026-07-31 - Market Review NQ July 31, 2026 (Source)|Market Review NQ July 31, 2026 (Source)]].

## Macro-Zeit als Reversal-Check nach News-Expansion (2026-Ergänzung)

Aus [[2026-08-07 - Case Study With NonFarm Payroll & NQ Futures (Source)|Case Study With NonFarm
Payroll & NQ Futures (Source)]]: an einem NFP-Freitag rallyt Preis nach dem 8:30-Print bis in die
Macro-Zeit **8:50–9:10** hinein. Diese Macro-Zeit dient hier nicht als Entry-Trigger, sondern als
**Prüfpunkt für eine bereits laufende Position** — läuft eine Long-Position mit deutlicher
Stage-1-Expansion (siehe [[Two Stage News Delivery (FOMC & NFP)]]) genau in eine Macro-Zeit hinein,
ist das der Moment, Teilgewinne zu sichern, bevor ein Reversal einsetzt. Bestätigt zusätzlich per
Standard-Deviation-Projektion der Pre-News-Range (siehe [[Central Bank Dealers Range (CBDR)]]).

## Anzeichen einer aktiven Macro-Phase: "Spooling"/Energie-Aufbau (2026, offene Hypothese)

Nutzerbeobachtung (laufend, noch nicht gegen Daten geprüft): Am **Start eines Macro-Fensters**
(konkreter Anlass: **10:50**, Beginn des [[NY Lunch Macro Model|Lunch Macros]]) baut Preis
sichtbar **Kraft/Energie auf**, bevor der eigentliche Move einsetzt — im Chart als "Spooling"
beschrieben. Noch offen, wie sich das konkret operationalisieren lässt (Kandidaten: engere
Candle-Ranges mit steigendem Volumen direkt vor dem Fenster, mehrere kleine Same-Direction-Closes
in Folge, sinkende Wick-Anteile). Bis zur Präzisierung als **offene Hypothese** behandelt, nicht
als bestätigte Regel — bei mehr Beispielen/Daten hier ergänzen und in `algo/PLAN.md` backtesten.

### Erstes Beispiel (2026-08-10, MNQ 1min)

Vom Nutzer per Chart-Screenshot geliefert (TradingView, MNQU2026, 1min, Montag 2026-08-10,
09:30–12:30 NY): Preis fällt ab ~10:00 aus einem Hoch bei ~29.890 in eine Zone um ~29.790–29.810
(brauner Band-Bereich im Chart, vermutlich FVG/OB) und **verbringt anschließend die gesamte
10:50–11:10-Macro-Zeit dort in kleinen, überlappenden Candles ohne klare Nettobewegung** — genau
das "Spooling"-Bild: viele kleine Pushes, kaum Fortschritt. Erst **nach** dem Macro-Fenster (ab
ca. 11:15–11:30) löst sich die Kompression in eine echte Expansion nach oben auf, bis zu den
NWOG-33-Leveln bei 29.841,00 / 29.851,50. Deckt sich mit dem generellen Chain-of-Custody-Muster
"Konsolidierung zwischen zwei Q/O-Leveln kündigt keinen Trade an, aber oft eine folgende
Expansion" — hier speziell an die Macro-Uhrzeit gekoppelt. Einzelbeispiel, noch kein Beleg.

![[MNQ 2026-08-10 - 10-50 Macro Spooling.png]]
*MNQU2026 1min, 2026-08-10: Spooling in der 10:50–11:10-Macro-Zeit (gelb markiert) knapp über der
NDOG-Zone, danach Expansion Richtung NWOG 33.*

## Verwandt

- [[AMD Cycle (Accumulation – Manipulation – Distribution)]]
- [[NY Lunch Macro Model]] — konkretes Setup rund um das 10:50-Macro
- [[Fair Value Gap (FVG)]], [[IPDA Data Ranges]]
- [[Modell 22]] — Displacement nach [[Turtle Soup]] muss laut Quelle konsequent in die Zukunft
  ausgemalt werden, relevant für spätere Price-Runs (reclaimed FVG oder IFVG).
- [[Two Stage News Delivery (FOMC & NFP)]], [[Central Bank Dealers Range (CBDR)]]
- [[2026-08-07 - Case Study With NonFarm Payroll & NQ Futures (Source)|Case Study With NonFarm Payroll & NQ Futures (Source)]]
