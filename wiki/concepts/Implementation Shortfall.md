---
tags: [concept, algo-methodology, transaktionskosten, kennzahlen, referenz]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[The Science of Algorithmic Trading and Portfolio Management (Source)]]"]
---

# Implementation Shortfall

Die zusammenfassende Kennzahl für **die gesamten Kosten der Umsetzung einer Handelsidee**.
Eingeführt von Perold (1988), hier nach
[[The Science of Algorithmic Trading and Portfolio Management (Source)]] (Kissell, Kap. 3).
Umgangssprachlich **Slippage**.

> Alle Formeln unten sind aus der chiffrierten Rohquelle dekodiert **und an den mitgelieferten
> Rechenbeispielen arithmetisch verifiziert** — siehe die Erläuterung zur Font-Kodierung auf der
> Quellenseite.

## Die Definition

```
(3.1)  IS = Paper Return − Actual Return
```

**Paper Return** — was die Idee gebracht hätte, wenn alle Stücke zum Entscheidungspreis
ausgeführt worden wären, **ohne jede Transaktionskosten**:

```
(3.2)  Paper Return = S · Pn − S · Pd

       S  = Gesamtzahl zu handelnder Stuecke
       Pd = Entscheidungspreis des Managers (decision price)
       Pn = Preis am Ende der Periode n
```

Bewusst ohne Kosten: Der Paper Return soll das **volle Potenzial der Auswahlentscheidung**
abbilden.

**Actual Portfolio Return** — was tatsächlich herauskam:

```
(3.3)  Actual Return = (Σ sⱼ) · Pn − Σ sⱼpⱼ − fees

       sⱼ, pⱼ = Stueckzahl und Preis der j-ten Teilausfuehrung
       (Σ sⱼ)·Pn = Endwert des Portfolios
       Σ sⱼpⱼ    = tatsaechlich gezahlter Erwerbspreis
       fees      = feste Gebuehren: Kommission, Ticket Charges, Steuern,
                   Clearing/Settlement, Rebates
```

**Zusammengesetzt:**

```
(3.4)  IS = [ S·Pn − S·Pd ]  −  [ (Σ sⱼ)·Pn − Σ sⱼpⱼ − fees ]
            └── Paper Return ──┘  └──── Actual Portfolio Return ────┘
```

## Das durchgerechnete Beispiel

Kissells Zahlen, Schritt für Schritt:

```
Entscheidung:  5.000 Stueck kaufen, Kurs steht bei $10
Tatsaechlich:  Durchschnittlicher Ausfuehrungspreis $10,50  (Market Impact, Price Appreciation)
Tagesende:     Kurs $11
Gebuehren:     $100

PAPER RETURN
  Wert bei Entscheidung   5.000 × $10   = $50.000
  Wert am Tagesende       5.000 × $11   = $55.000
  Paper Return                          = $5.000

ACTUAL RETURN
  Tatsaechlich investiert 5.000 × $10,50 = $52.500
  Wert am Tagesende                      = $55.000
  minus Gebuehren                        = −$100
  Actual Return  = $55.000 − $52.500 − $100 = $2.400

IMPLEMENTATION SHORTFALL
  IS = $5.000 − $2.400 = $2.600
```

Gelesen: Von den $5.000, die die Idee wert war, sind **$2.400 angekommen** — $2.600 sind in der
Umsetzung verloren gegangen. Das sind **52 % der Idee**, bei einem Ausführungspreis, der nur 5 %
über dem Entscheidungspreis lag.

> **Das ist die eigentliche Lehre der Kennzahl:** Ein scheinbar kleiner Ausführungsnachteil frisst
> einen großen Teil des Ideenwerts, weil er sich am **erwarteten Gewinn** misst, nicht am
> Ordervolumen. Genau deshalb ist IS die Kennzahl, die Portfoliomanager und Trader
> gleichermaßen betrifft: sie misst Auswahlfähigkeit **und** Ausführungskosten in einer Zahl.

## Drei Ausprägungen

| Variante | Situation |
|---|---|
| **Complete Execution** | die gesamte Order wurde ausgeführt, `Σ sⱼ = S` — der einfachste Fall (Beispiel oben) |
| **Opportunity Cost** (Perold) | ein Teil bleibt unausgeführt; die nicht gehandelten Stücke gehen als entgangener Gewinn in die Kennzahl ein |
| **Expanded Implementation Shortfall** (Wagner) | zerlegt zusätzlich nach den Phasen des Investmentzyklus, insbesondere um die **Delay Cost** getrennt auszuweisen |

## Bezug zu diesem Projekt

**Die Kennzahl fehlt in `algo/` vollständig** — und sie ist die passende Antwort auf eine Frage,
die im Projekt offen ist: Wie viel des theoretischen Signalwerts kommt tatsächlich an?

Übersetzt auf die Silver-Bullet-Regel:

```
Pd  = Preis zum Zeitpunkt, an dem plan_trade() das Setup erkennt
pⱼ  = tatsaechlicher Fuellpreis (im Backtest: die Annahme der backtesting-Lib)
Pn  = Preis beim Exit (Ziel, Stop oder Fensterende)
fees = echte $/Kontrakt-Kommission  (siehe [[Transaktionskosten-Taxonomie (Kissell)]])
```

Damit ließe sich zerlegen, wie viel des Ergebnisses am **Signal** hängt und wie viel an der
**Ausführungsannahme** — genau die Trennung, die der Präzisions-Audit vom 2026-08-06/07 an anderer
Stelle schon erzwungen hat (`dubious_pct` als Maß der Fill-Unsicherheit, Margin-Deckel,
Commission-Abzug).

**Besonders relevant vor der IBKR-Anbindung** (Roadmap-Stufe 4 in
[[Algo-Trading: Arbeitsstandards]]): Sobald echte Orders laufen, ist IS die Kennzahl, an der sich
Backtest-Annahme und Realität direkt vergleichen lassen — und laut Kissell diejenige, mit der man
Broker und Ausführungsalgorithmen bewertet.

Und ein Detail, das mit den ICT-Konzepten des Vaults zusammenfällt: Der **Delay Cost**-Anteil
zwischen Signal und Order enthält bei Übernacht-Positionen zwangsläufig die Gap-Bewegung — siehe
[[New Week Opening Gap (NWOG) Bias]] und [[ORG (Opening Range Gap) & 1st Presented FVG]]. Was der
Vault als handelbares PD Array behandelt, ist aus Kostensicht eine unvermeidbare Komponente.

Weiterführend: [[Transaktionskosten-Taxonomie (Kissell)]] (die zehn Einzelkomponenten, aus denen
sich IS zusammensetzt), [[Trader's Dilemma & Efficient Trading Frontier]],
[[Performance-Kennzahlen-Katalog]].
