---
tags: [concept, ict, trading-ict, sessions, bias, core]
created: 2026-08-02
updated: 2026-08-23
sources: ["[[Implementing The Asian Range (Source)]]", "[[Asia Session (Source)]]", "[[Understanding The ICT Judas Swing (Source)]]", "[[Trading The Key Swing Points (Source)]]", "[[2026-08-18 - Trade Management & Removing The Need To Be Right (Source)|Trade Management & Removing The Need To Be Right (Source)]]"]
---

# Asian Range

Die Konsolidierungsphase vor London — **7:00 PM bis 12:00 AM NY**, gemessen als **Highest High /
Lowest Low**. Sie ist kein Signalgeber, sondern der **Rahmen**, in dem ein bereits vorhandener Bias
seine Bestätigung findet.

Die Folie trennt dabei zwei Maße:

- **Höhe der Range** = Highest High bis Lowest Low zwischen 7:00 PM und Mitternacht.
- **Breite der Range** = die Dauer selbst, also 7:00 PM bis Mitternacht NY.

![[MMP - AsianRange 02.png]]
*„Defining The Asian Range": Beginn 7:00 pm NY, Ende Mitternacht NY; die Höhe ergibt sich aus
Highest High und Lowest Low, die Breite aus der Dauer.*

![[MMP - AsianRange 03.png]]
*Dieselbe Definition am Chart — dazwischen bauen sich Buy Orders oberhalb und Sell Orders unterhalb
auf: „Orders & Sentiment Build Up".*

## Ohne Bias keine Anwendung

> *„Die gesamte Theorie geht nur auf, wenn wir einen Bias haben!"*

Selbst ein sauberer Sweep des Asia Low mit anschließendem Lauf zur Buyside ist **keine
Trading-Option**, solange kein Bias vorliegt. Das ist die härteste Regel der Quelle — die Range
erklärt, sie entscheidet nicht.

## Konsolidierung = Trendtag

> **Consolidation Asia Range = Trending Tag.**

Eine enge, konsolidierende Range ist ein starkes Argument dafür, dass der Algorithmus am Folgetag
„abliefert". Die Folie formuliert es als *„a stillness in Price — many times right before the
Intraday Directional Impulse Swing"*. Ist der Markt nicht bereit zu laufen, konsolidiert er bis
Mitternacht NY.

**Ab 12 Uhr NY ist der Preis bereit sich zu bewegen** — Mitternacht ist der Start des Tages für den
Algorithmus.

## Ablaufmuster nach Bias

| Bias | Ablauf |
| --- | --- |
| **Bullish** | Preis geht **unter** die Range, dann darüber — und bleibt ab da bullish |
| **Bearish** | Preis geht **erst über** die Range, dann darunter — und bleibt darunter |

Der Sinn dahinter: In den meisten Fällen bildet **London** das High/Low des Tages, im schlimmsten
Fall **Asia** — deshalb ist ein Stop unter bzw. über der Asia Range geschützt.

## Die Range bleibt nach dem Sweep relevant

Die Folie „Utilization In Bullish Conditions" ist hier präziser als die Mitschrift:

> *„The periods when Price is Bullish — we can **extend the Asian Range High and Low into the
> future**. When Price returns back to the **Asian Range High** — we can anticipate **Institutional
> Buying**."*

Die Range wird also nicht nur beobachtet, sondern **als Level nach rechts verlängert**. Kehrt der
Preis im späteren Tagesverlauf dorthin zurück, ist institutionelles Kaufinteresse zu erwarten
(spiegelbildlich für Sells). Ein Sweep entwertet die Range nicht — sie bleibt ein PD-Bereich.

![[MMP - AsianRange 05.png]]
*„Utilization In Bullish Conditions": Asian Range High und Low werden in die Zukunft verlängert; die
Rückkehr an das Range High ist der Punkt, an dem institutionelles Kaufen erwartet wird.*

![[MMP - AsianRange 06.png]]
*Die Reaktion am verlängerten Range-Level im weiteren Tagesverlauf.*

## Zusammenspiel mit dem Judas Swing

Der [[Judas Swing]] (0:00–5:00 Uhr NY) arbeitet direkt an den Rändern dieser Range:

- **Bullish**: Sweep des **Asia High** zur Täuschung → Drop, um beide Seiten offset zu nehmen →
  Expansion zur Buyside.
- **Bearish**: enge Asia-Konsolidierung → Sweep des **Asia Low** → Run zur Buyside (die Judas) →
  Hauptmove zur Sellside.

## Handelbarkeit der Session selbst

Der Asian Open kann ein [[Optimal Trade Entry (OTE)|OTE]]-Muster aufsetzen (15–20 Pips), ideale
Paare sind **AUD, NZD, JPY** — siehe [[ICT Killzones]].

## ⚠️ Bei Index-Futures: 19:00–22:00 statt 19:00–24:00

> ⚠️ **Widerspruch zu [[Implementing The Asian Range (Source)]]** (und zur Definition oben):
> [[2026-08-18 - Trade Management & Removing The Need To Be Right (Source)|Trade Management & Removing The Need To Be Right (Source)]]
> setzt das Fenster für NQ auf **19:00–22:00 ET** und grenzt es ausdrücklich gegen die
> Forex-Definition ab:
>
> > *„…last Thursday's dealing range from **7:00 p.m. to 10:00 p.m.** Eastern time. **Not the Asian
> > range like when we're trading forex** — that's not what I'm referring to. What I'm referring to
> > is the time at which the best trading can be done, which is between 7:00 and 10:00 Eastern
> > time."*
>
> Beide Angaben sind gleichwertige ICT-Primärquellen; nicht überschrieben, sondern nebeneinander
> geführt. **Arbeitsannahme**: 19:00–24:00 für Forex (Bias-Rahmen, Judas-Swing-Kontext oben),
> **19:00–22:00 für Index-Futures**, wenn die Range als *Dealing Range zur Level-Ableitung* genutzt
> wird. Ungeprüft, welche der beiden Spannen an NQ die belastbareren Level liefert — ein
> Kandidat für einen Vergleichslauf gegen `raw/marktdaten/`.

**Verwendung als Dealing Range mit Oktanten.** In derselben Quelle wird die Range **nicht** als
Sentiment-Rahmen gelesen, sondern als [[Dealing Range]], auf die eine volle Qs/Os/Hs-Skala gelegt
wird — ICT nennt im Live-Trade den **„0.875 octant"** (= O7) als Zielbereich und legt Partials an
die **C.E.** der Range. Bemerkenswert daran: die Range stammt vom **Donnerstag der Vorwoche**, wird
also über mehrere Tage hinweg als Levelquelle weiterverwendet — konsistent mit der
Verlängerungs-Regel im Abschnitt oben.

## Abgrenzung

- Die [[Central Bank Dealers Range (CBDR)]] überlappt zeitlich, misst aber einen anderen Zweck
  (Standardabweichungs-Projektionen statt Sentiment-Rahmen).
- [[ICT Daily Range Session Timing]] führt die Asia Range mit **19–24 Uhr** bzw. **20–24 Uhr** —
  die Folie hier setzt sie auf **19–24 Uhr**, was zur Angabe *„Start um 19/20 Uhr NY"* in Jannes'
  Mitschrift passt.

## Verwandt

- [[ICT Killzones]], [[Judas Swing]], [[Midnight Opening Range]]
- [[AMD Cycle (Accumulation – Manipulation – Distribution)]] — die Range ist die Accumulation-Phase
- [[Central Bank Dealers Range (CBDR)]]
