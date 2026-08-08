---
tags: [concept, algo-methodology, ausfuehrung, risikomanagement, referenz]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[The Science of Algorithmic Trading and Portfolio Management (Source)]]"]
---

# Trader's Dilemma & Efficient Trading Frontier

Warum sich Ausführungskosten und Ausführungsrisiko **nicht gleichzeitig** minimieren lassen. Aus
[[The Science of Algorithmic Trading and Portfolio Management (Source)]] (Kissell, Kap. 1), nach
Almgren & Chriss (1997/1999/2000).

## Das Dilemma

```
AGGRESSIV handeln (schnell)   →  Market Impact HOCH,   Timing Risk NIEDRIG
PASSIV handeln (langsam)      →  Market Impact NIEDRIG, Timing Risk HOCH
```

Market Impact und Timing Risk sind **gegenläufige Größen**. Es gibt kein Minimum beider zugleich —
nur einen Trade-off, den man **bewusst nach der eigenen Risikoneigung** wählen muss. Kissell nennt
das den *„trader's dilemma"*; beide zusammen bilden den größten Teil der handelsbezogenen Kosten.

Zur Erinnerung, was die beiden Größen sind (Details auf
[[Transaktionskosten-Taxonomie (Kissell)]]): Market Impact ist die vom eigenen Auftrag
verursachte Kursbewegung — immer nachteilig. Timing Risk ist die **Unsicherheit um die
Kostenschätzung**, zusammengesetzt aus Preisvolatilität, Liquiditätsrisiko und
Parameterschätzfehler.

## Die Efficient Trading Frontier

Löst man das Optimierungsproblem für **verschiedene Risikoniveaus**, entsteht eine Schar optimaler
Strategien: jede hat die niedrigsten Kosten für ihr Risikoniveau und das niedrigste Risiko für
ihre Kostenhöhe. Die Menge dieser Punkte ist die **Efficient Trading Frontier**.

```
Market Impact
     ▲
   A │●                      A  aggressiv:  hohe Kosten, niedriges Risiko
     │  ●                    B  normal:     mittel / mittel
   B │    ●                  C  passiv:     niedrige Kosten, hohes Risiko
     │       ● C
     │              ● D      D  IRRATIONAL: es existiert eine Alternative mit
     │                          gleichem Risiko bei geringeren Kosten,
     └──────────────────►       geringerem Risiko bei gleichen Kosten,
             Timing Risk        oder beidem
```

> **Punkt D ist die eigentliche Pointe.** Eine Strategie unterhalb/rechts der Frontier ist nicht
> „konservativer" oder „anders gewichtet" — sie ist **dominiert** und liefert nie Best Execution.
> Der Analogieschluss zur Portfoliotheorie ist beabsichtigt: dieselbe Logik wie bei der
> Effizienzlinie im Rendite-Risiko-Raum.

Wer welchen Punkt wählt:

| Akteur | Wahl | Begründung |
|---|---|---|
| **informierter** Trader mit Kurserwartung | aggressiv (POV ≈ 30 %) | höhere Kosten, dafür Sicherheit über den Ausführungspreis — die Information ist verderblich |
| **Indexer** | passiv (POV ≈ 5 %) oder risikoneutral | Kostenminimierung, kein Zeitdruck |
| risikoaverser Mischfall | mittlerer Punkt | bewusste Abwägung |
| „mit dem Volumen mitlaufen" | VWAP-Strategie | Benchmark ist der Tagesdurchschnitt |

## POV — Percentage of Volume

Die gebräuchlichste Ausführungsvorgabe: mit einem festen **Anteil am Marktvolumen** handeln.

```
POV = 20 %  ⟹  von jeden 10.000 im Markt gehandelten Stueck sind 2.000 die eigenen
```

Eigenschaft: Ein *konstanter* POV-Satz führt automatisch zu **schnellerem Handeln bei hohem
Volumen** und langsamerem bei niedrigem — die Ausführung passt sich der Liquidität an, ohne dass
man einen Zeitplan vorgeben muss.

Rechenbeispiel aus dem Buch für die Ebene darunter: Bei `POV = 10 %` und einer Prognose von
10.000 Stück Marktvolumen in der nächsten Minute müssen 1.000 eigene Stück ausgeführt werden. Der
Limit-Order-Mix könnte bei einem Markt von $30,00–$30,10 so aussehen:

```
Limit  200 @ $29,95
Limit  300 @ $30,00
Limit  300 @ $30,05
Market 200 @ $30,10        ← sichert die Zielrate ab
```

## Makro- und Mikroebene

| Ebene | Entscheidet | Wer setzt es |
|---|---|---|
| **Makro** | optimale Handelszeit/-rate, Adaptionstaktik, Limit-Order-Strategie, Smart-Order-Routing | der Investor |
| **Mikro** | konkrete Order-Submission-Regeln | im Algorithmus verdrahtet |

Die Mikroebene hat drei Ziele: der vorgegebenen Strategie folgen; **nur dann** davon abweichen,
wenn es im Interesse des Investors ist und von ihm definiert wurde; faire Preise erzielen, ohne
unnötigen Market Impact.

**Die Konsistenzregel, die daraus folgt:** Eine aggressive Makro-Vorgabe (POV = 40 %) **nur** mit
Limit-Orders umzusetzen ist widersprüchlich — Limit-Orders werden nicht garantiert ausgeführt, die
Zielrate wird verfehlt. Umgekehrt ist eine passive Vorgabe (POV = 5 %) mit vielen Limit-Orders
genau richtig, weil genug Zeit bleibt, den Spread zu vermeiden.

## Adaptionstaktiken

Wie der Algorithmus auf veränderte Bedingungen reagiert:

| Taktik | Regel |
|---|---|
| **Volume-based** | Tempo an die Marktliquidität koppeln (POV ist der Standardfall) |
| **Price-based** | **AIM** (Aggressive-in-the-Money): schneller bei günstigen Preisen, langsamer bei ungünstigen. **PIM** (Passive-in-the-Money): genau umgekehrt |
| **Time-based** | Fertigstellung bis zu einem Zeitpunkt garantieren (z.B. nicht später als der Schluss); früher ist erlaubt |
| **Probabilistic** | die Rate wählen, die die **höchste Wahrscheinlichkeit** liefert, das Anlageziel zu erreichen — nichtlineare Optimierung, z.B. Sharpe maximieren oder Tracking Error minimieren |
| **Optimization** | Zeitplan so nachführen, dass der erwartete Schlusspreis in einer Toleranz bleibt; meist über ein **z-Score-Maß**, das realisierte Kosten, Sunk Cost und erwarteten Preis verrechnet |
| **Cash Balancing** | Risikosteuerung der offenen Restposition oder Selbstfinanzierung (Verkäufe zahlen die Käufe) |

**AIM und PIM sind die interessante Gegenüberstellung:** Sie sind die Ausführungs-Entsprechung
des Gegensatzes zwischen Momentum und Mean Reversion aus
[[Stop Loss bei Mean Reversion vs. Momentum]] — AIM setzt auf Fortsetzung der günstigen Bewegung,
PIM auf Rückkehr.

## Bezug zu diesem Projekt

**Heute nur teilweise relevant, ab der IBKR-Anbindung voll.** Bei einstelligen MNQ-Kontraktzahlen
im liquidesten Index-Future ist der Market Impact praktisch null — das Dilemma ist damit stark
entschärft, und aggressive Ausführung ist nahezu kostenlos.

**Was trotzdem jetzt schon gilt:**

1. **Der Backtest unterstellt implizit eine Ausführungsstrategie.** `algo/backtest_bt.py` nimmt
   Fills zu Bar-Preisen an — das entspricht dem aggressiven Ende der Frontier (sofortige
   Ausführung, kein Timing Risk). Die Annahme ist bei MNQ vertretbar, sollte aber benannt sein.
2. **Die Konsistenzregel Makro/Mikro ist unmittelbar anwendbar:** `rules.py::plan_trade` liefert
   ein Setup mit engem Zeitfenster (Silver Bullet, eine Stunde). Das ist eine **aggressive**
   Makro-Vorgabe — sie mit Limit-Entries umzusetzen wäre der von Kissell beschriebene
   Widerspruch. Der Vault hat dazu eine Gegenposition aus dem ICT-Material
   ([[Optimal Trade Entry (OTE)]], Limit-Entries im Retracement), die sich sauber gegeneinander
   testen lässt.
3. **Das Vokabular für Roadmap-Stufe 4–6** ist damit gesetzt: `broker_ibkr.py` wird eine
   Order-Type-Entscheidung treffen müssen, und die Begriffe POV, AIM/PIM, Time-based sind der
   Rahmen dafür.

Weiterführend: [[Transaktionskosten-Taxonomie (Kissell)]],
[[Implementation Shortfall]] (die Kennzahl, an der sich die Wahl auf der Frontier messen lässt).
