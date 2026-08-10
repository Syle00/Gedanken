---
tags: [concept, ict, trading-ict, ict-gems, projektion, 2025]
created: 2026-08-10
updated: 2026-08-10
sources: ["[[ICT Gems - Algorithmic Timings With Opening Ranges (Source)]]"]
---

# Implied Dealing Range

> **Definition (ICT)**: *"An implied dealing range is a price run that **has not completed yet**."*

Anders als die normale [[Dealing Range]], die zwischen zwei bereits existierenden Extremen
aufgespannt wird, verläuft die Implied Dealing Range vom **Startpunkt der Bewegung** bis zum
**antizipierten Ziel** (Terminus/Draw on Liquidity). Sie ist damit eine **Prognose-Range**, kein
Messobjekt — und genau deshalb nützlich: Man kann in ihr Level *vorhersagen*, bevor Preis dort war.

## Wozu sie dient: Gaps vorab verorten

Der eigentliche Zweck. Kennt man Start und Ziel der noch laufenden Bewegung, ergibt sich, **wo
unterwegs welche Gap-Sorte entstehen wird**:

| Anteil der Implied Dealing Range | Was dort entsteht |
|---|---|
| **20–30 %** | [[Breakaway Gap]] |
| **50 %** | **Measuring Gap** |

> *"Breakaway gaps are wonderful to anticipate near the 20 to 30 % of the price range that has yet
> to deliver, and then 50 % of it."*

Das dreht die übliche Reihenfolge um: Statt ein Gap zu finden und danach zu fragen, was es ist,
weiß man **vorab**, an welcher Stelle der erwarteten Strecke welches Gap fällig ist.

## Konstruktion

1. **Startpunkt** festlegen — dort, wo die Bewegung ansetzt (im Beispiel der Abverkaufspunkt).
2. **Ziel** festlegen — das begründete Liquiditätsziel (im Beispiel das Low einer
   [[Balanced Price Range (BPR)|Balanced Price Range]] aus zwei Wochen zuvor).
3. Fib grob über diese Strecke ziehen → 20–30 % und 50 % markieren.
4. **Verfeinern, während Preis liefert**: ICT betont, dass die grobe Projektion nur die Näherung
   ist — der Preislauf selbst schärft sie Kerze für Kerze nach.

## Gegenprobe: ist es wirklich ein Measuring Gap?

Ein sauberes Verifikationsverfahren, das gleichzeitig das Ziel liefert:

1. Fib am **High** der Bewegung ankern und nach unten ziehen.
2. So weit ziehen, bis das **50-%-Level exakt auf der C.E. des vermuteten Measuring Gaps** liegt.
3. Wo der Fib dann endet, ist das **projizierte Ziel** der Bewegung.

Deckt sich das 50-%-Level mit der Gap-Mitte, ist damit **beides** bestätigt: dass es ein Measuring
Gap ist, und wohin die Bewegung misst. Im Beispiel traf die Projektion so, dass die **Bodies** exakt
dort stoppten und nur die **Wicks** einen Tick darunter griffen — die übliche Body/Wick-Lesart
([[Institutional Order Flow (Body vs Wick)]]) als Bestätigung, dass die Messung sauber aufging.

## Verhältnis zum Grading von Price Swings

ICT stellt die Implied Dealing Range ausdrücklich neben das Grading eines Price Swings
([[Graded Price Swings]]): *"it's basically like the equilibrium or grading a price swing"* — nur
eben auf eine Strecke angewendet, die noch aussteht.

## Verwandt

- [[Dealing Range]] — die abgeschlossene Variante
- [[Breakaway Gap]] — enthält auch die Measuring-Gap-Definition
- [[Graded Price Swings]], [[Equilibrium Vs. Discount]]
- [[Daily High & Low Projektion (Konvergenz)]], [[Enigma FVG Projection]]
- [[ICT Gems - Algorithmic Timings With Opening Ranges (Source)]]
