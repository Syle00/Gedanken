---
tags: [concept, ict, trading-ict, core]
created: 2026-08-01
updated: 2026-08-16
sources: ["[[Low Resistance Liquidity Runs Part 1 (Source)]]", "[[Low Resistance Liquidity Runs Part 2 (Source)]]", "[[Post US Holiday Monday Followup (Source)]]", "[[2026-07-31 - ICT Algorithmic Time & Price Grids (Source)|ICT Algorithmic Time & Price Grids (Source)]]", "[[ICT Mentorship Core Content - Month 1 - Liquidity Runs (Source)]]", "[[2026-08-10 - Navigating High Resistance Liquidity Run Conditions (Source)|Navigating High Resistance Liquidity Run Conditions (Source)]]", "[[2022-05-04 - 2022 ICT Mentorship Episode 23 (Source)]]", "[[2026-07-06 - Weekend US Holiday Volume Protocol (Source)|Weekend US Holiday Volume Protocol (Source)]]"]
---

# Low Resistance Liquidity Run

Zielbild jeder Range-Analyse: ein Preislauf mit möglichst wenig Widerstand von einer [[PD Array]] zur
nächsten. Zentrales Suchziel in [[Classic Swing Trading Approach]].

## Verschachtelte EQ-Messung

- Consolidierende Range zuerst grob per PD-Matrix einordnen (High to Low, EQ bestimmen).
- Innerhalb der Premium-Hälfte erneut EQ messen → "Premium innerhalb des Premium" (analog für
  Discount) — die Range wird rekursiv in Quadranten aufgeteilt, bis hinunter zu 4H/1H.
- Alle PD Arrays von Monthly bis Daily innerhalb der Range identifizieren, um die Consolidierung zu
  deuten und Targets/Profit-Targets abzuleiten.

![[image 190.png]]
*Rekursive EQ-Messung: Premium innerhalb des Premium (analog Discount innerhalb des Discount).*

## Kernregeln

- Eine bereits genutzte PD Array ist **nicht mehr gültig** — Preis läuft zur nächsten.
- Die Range muss korrekt aufgeteilt sein, sonst droht Liquidation der eigenen Position.
- Befindet sich Preis genau am EQ der Gesamtrange und ist der Open Float nicht klar erkennbar: lieber
  abwarten, statt zu raten — die Wahrscheinlichkeit, ausgestoppt zu werden, ist in dieser Lage hoch.

## Umsetzung für 50-75 Pip Runs (Part 2)

- Praktische Anwendung im **4H-Chart** in Kombination mit Monthly/Weekly/Daily PD Arrays — für
  [[One Shot One Kill Model|One-Shot-One-Kill]]-Setups gut geeignet, um 50–75 Pips zu erreichen.

![[image 199.png]]
*One-Shot-One-Kill im 4H-Chart: 50–75-Pip-Run bei High-Probability-Setup aus klarem Discount mit starkem bullishem Bias.*
- Auf High-Probability-Trades beschränken: klarer Discount-Bereich + starker bullisher Bias
  (spiegelbildlich für Shorts).
- Weekly Range wird immer antizipiert; verpasste M/W/D-PDs erlauben einen Reentry — bevorzugt an der
  jeweils höheren PD.
- **30–50 % Wahrscheinlichkeit**, dass sich das Wochen-High/Low unter Trending Conditions bereits am
  **Mittwoch** bildet.

## Setup-Erkennung: leere Zone zwischen zwei Daily PD Arrays (2026-Ergänzung)

Liegen zwei Daily-[[Suspension Block|Suspension Blocks]] (oder andere Daily-PD-Arrays) **ohne
Überlappung** übereinander und eröffnet die Session **innerhalb der leeren Zone dazwischen**, ist ein
schneller, "sauberer" Lauf zum entfernteren Block wahrscheinlich — große Candles, hohe Geschwindigkeit,
kaum Gegenreaktion. Davon zu unterscheiden ist das **effiziente Buy-/Sell-Program** (siehe
[[Buy & Sell Program]]): eng getaktete, kleine Candles ohne Pullback, die genauso schwer zu shorten/
longen sind, aber optisch das Gegenteil zeigen (langsam statt schnell). Quelle:
[[2026-07-31 - ICT Algorithmic Time & Price Grids (Source)|ICT Algorithmic Time & Price Grids (Source)]].

## Gegenstück: High Resistance Liquidity Run

Chop-artige Seek-&-Destroy-Bedingungen statt eines glatten Runs — typisch **nach großen
US-Feiertags-Wochenenden** (z.B. 4. Juli auf Sa/So: Montag meist schwierige, schlechte Price
Action → am Montag lieber nicht traden, erst Dienstag wieder einsteigen) und **vor
Zinsentscheiden/FOMC-Meetings**.

### Warum Feiertage HRLR erzeugen — der Mechanismus (2026-Ergänzung)

Aus [[2026-07-06 - Weekend US Holiday Volume Protocol (Source)|Weekend US Holiday Volume Protocol (Source)]],
der ausführlichen Fassung der bislang nur als Kurznotiz vorhandenen Warnregel
([[Post US Holiday Monday Followup (Source)]]). ICT begründet sie erstmals — es ist **keine
Kalender-Heuristik, sondern ein Partizipationsargument**:

- Große Adressen wissen, dass das Volumen dünn bleibt (Abwesenheit, Sommermonate). Damit fehlt der
  Anlass für große Ranges: *„There's **no need for them** to start spreading the market higher or
  lower on a great big range, because there isn't enough interest to make it reasonable to assume
  why the market went that high."*
- **Sie können Teilnahme auch nicht erzwingen** — *„he won't be able to engineer participation,
  cuz there's a vacuum of interest."*
- **Die entscheidende Konsequenz**: *„They don't need to have the market to be that **precise**."*
  Die PD Arrays verschwinden nicht, sie werden **unschärfer**. Wer an einem solchen Tag auf die
  gewohnte Tick-Präzision setzt, handelt gegen die Bedingungen — nicht gegen die Methode.
- Beantwortet damit auch den häufigen Einwand, ein *US*-Feiertag könne einen global gehandelten
  Kontrakt nicht betreffen.

**Erkennungsmerkmale im laufenden Handel** (dieselbe Quelle):

| Tell | Normalfall zum Vergleich |
|---|---|
| **Index-Entkopplung** (Dow scharf runter, ES gemischt, NQ anders) | Gleichlauf aller drei = *„no-brainer"*, siehe [[SMT (Smart Money Divergence)]] |
| News nimmt zwar ein Tief mit, **berührt das erste signifikante FVG aber gar nicht** | FVG wird angelaufen |
| Preis steht **mittig** in der 15-Min-Range, beide Seiten offen | klare Premium-/Discount-Lage |
| Failures to launch, träge Kerzen, sofortiges Zurückrollen nach Ausbruch | Displacement trägt |

**Die Empfehlung ist eindeutig**: *„I've lost more money trading after holidays like this than in
any other thing."* — und *„**Enough is not trading at all on a day like today.** That's the right
answer."* Das Protokoll für den Fall, dass man trotzdem teilnimmt, steht auf
[[Low Probability Day Probing]].

> **Was am schlechten Tag trotzdem trug**: Quadranten- und C.E.-Level blieben im Live-Beispiel
> präzise (Umkehr exakt am unteren Quadranten, [[Event Horizon]] auf den Punkt). Unschärfer wurde
> die *Erzählung*, nicht das Raster — die Levels hielten, nur die Wege dorthin waren zäh.

### Mechanik (2022er Video-Ergänzung)

Aus [[ICT Mentorship Core Content - Month 1 - Liquidity Runs (Source)]] — die konkrete
Preis-Struktur-Erklärung, warum manche Highs/Lows "verteidigt" sind:

- **High Resistance**: liegen zwischen dem aktuellen Preis und dem anvisierten alten High/Low
  bereits **viele weitere Zwischenhochs/-tiefs**, muss Preis erst durch all diese Widerstände, bevor
  das eigentliche Ziel überhaupt erreichbar wird — solche Levels sind gut verteidigt und werden
  meist nur durch einen echten Katalysator gebrochen (NFP, FOMC, unerwartete Zinsentscheidung,
  Black-Swan-Ereignis), nicht durch normale Preisbewegung.
- **Low Resistance**: läuft Preis dagegen **einseitig glatt** (wenig Retracement) von einem
  gebrochenen Level weg, bleibt jeder neu gebildete Short-Term-Swing bis zum nächsten Extrem
  "unbelastet" von Zwischenständen — solche Runs sind die bevorzugten Trade-Bedingungen, weil jeder
  Rücklauf zum letzten Swing praktisch widerstandsfrei zum nächsten alten High/Low durchläuft.
- Je **mehr Preisaktion** (Candles, Konsolidierung) um ein Level herum stattgefunden hat, desto
  stärker ist es institutionell verteidigt — Faustregel für die Einschätzung ohne zusätzliche Tools.

### Navigieren statt Aussitzen (Live-Trade 2026-08-10)

Die bestehende Regel "kein FVG in 15M/5M → nicht handeln" (siehe
[[Algorithmic Price Delivery Continuum]], [[Balanced Price Range (BPR)]]) ist ein **Entry-Filter**.
[[2026-08-10 - Navigating High Resistance Liquidity Run Conditions (Source)|Navigating High Resistance Liquidity Run Conditions (Source)]]
ergänzt den Fall, dass man bereits in einem Lauf sitzt, der in eine widerstandsreiche Zone
hineinläuft — ICT handelt dort bewusst weiter, aber mit verändertem Management:

- **HRLR vorab erkennen**: mehrere ungetestete bzw. bereits invertierte Gaps übereinander zwischen
  Preis und Ziel, dazwischen der Midnight Opening Price, plus schwere News-Woche (im Beispiel
  CPI/PPI Mi+Do). Ansage vorab: *"see how I told you it can get a little messy in here?"* — die
  Unruhe wird antizipiert, nicht als Überraschung behandelt.
- **Ziele auf die nahen Pools staffeln**, nicht auf das Endziel setzen: erstes Partial knapp unter
  dem Midnight Opening Price ([[Midnight Opening Range]]), zweites am nächsten minoren
  Buyside-Pool. Danach gilt der Trade als bezahlt, unabhängig vom Ausgang des Rests.
- **Nicht "das Magazin leeren"**, solange das eigentliche Ziel (hier: relativ gleiche
  Overnight-Swing-Highs) noch weit entfernt ist — sonst fehlt Size für den Teil des Laufs, der die
  Widerstände tatsächlich durchbricht.
- Der Midnight Opening Price wirkt beim Anlaufen von unten selbst als **massiver Widerstand**
  ("offering a whole lot of initial resistance"), nicht nur als Magnet — genau das macht die Zone
  darüber zum HRLR-Abschnitt.
- Gegen sich laufende Bewegung: Teil-Stops statt Alles-oder-Nichts, siehe
  [[Partial Profit-Taking & R-Multiple-Skalierung]].

## "Running" vs. "Sweeping" (Terminologie, 2022 Mentorship Ep. 23)

[[2022-05-04 - 2022 ICT Mentorship Episode 23 (Source)]] führt eine explizite Begriffstrennung ein,
die bislang im Vault nicht kodifiziert war:

- **Sweeping**: Preis durchbricht ein Level nur **flach** (wenige Ticks) und dreht danach um — der
  klassische Liquidity Sweep vor einem [[Market Structure Shift (MSS)]].
- **Running**: Preis durchbricht ein Level und **läuft weiter** (Continuation) — kein Reversal-Signal,
  sondern Bestätigung des laufenden Low-Resistance-Runs.

Praktische Konsequenz: derselbe Level-Durchbruch wird je nach Nachfolgeverhalten unterschiedlich
gedeutet — ein "Run" widerlegt keine Bias, ein "Sweep" ist dagegen die Pflichtbedingung für einen MSS
(siehe [[Market Structure Shift (MSS)]]).

## Verwandt

- [[PD Array]], [[Equilibrium Vs. Discount]]
- [[Open Float & Liquidity Pools]]
- [[One Shot One Kill Model]]
- [[External vs. Internal Range Liquidity]] — dieselbe Unterscheidung, aus Range-Perspektive statt Preis-Struktur-Perspektive
