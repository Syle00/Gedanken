---
tags: [concept, algo-methodology, transaktionskosten, risikomanagement, referenz]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[The Science of Algorithmic Trading and Portfolio Management (Source)]]"]
---

# Transaktionskosten-Taxonomie (Kissell)

Zehn getrennte Kostenkomponenten statt „Kommission und Spread". Aus
[[The Science of Algorithmic Trading and Portfolio Management (Source)]] (Kissell, Kap. 3, nach
Kissell 2003/2006).

Relevanz für dieses Projekt: `algo/PLAN.md` hält seit dem 2026-08-07 einen offenen Punkt fest —
das Kommissionsmodell in `backtest_bt.py` ist notional-proportional (Aktienlogik) statt
$/Kontrakt (Futures-Realität) und erzeugt dadurch bei 20× Hebel **$46.065 Gebühren**. Diese Seite
ist die Systematik, die zur Korrektur fehlt.

## Die zehn Komponenten

| # | Komponente | Was es ist | Bei MNQ relevant? |
|---|---|---|---|
| 1 | **Commission** | Zahlung an den Broker für Ausführung, Order-Routing, Risikomanagement. Je Kontrakt/Aktie **oder** als Basispunkte des Transaktionswerts | **ja** — bei Futures $/Kontrakt, **nicht** notional |
| 2 | **Fees** | Börsengebühren, Clearing, Settlement, Aufsichtsabgaben. Broker bündeln sie oft in die Kommission | **ja**, klein aber fix je Kontrakt |
| 3 | **Taxes** | Steuern auf realisierte Gewinne; Sätze variieren nach Anlage- und Ertragsart | außerhalb des Backtests |
| 4 | **Rebates** | Maker-Taker: wer Liquidität stellt, bekommt Rabatt; wer sie nimmt, zahlt. Invertiert bei Taker-Maker | bei CME-Futures kaum |
| 5 | **Spreads** | Brief minus Geld. Entschädigt Market Maker für Inventarrisiko und **adverse selection**. Gibt die Round-Trip-Kosten **kleiner** Orders wieder, **nicht** die großer Blöcke | **ja** — bei MNQ meist 1 Tick |
| 6 | **Delay Cost** | Wertverlust zwischen **Anlageentscheidung** und **Ordereingabe** | **ja**, im Backtest oft unsichtbar |
| 7 | **Price Appreciation** | natürliche Kursbewegung ohne Unsicherheit (Trend, Drift, Momentum, Alpha) | **ja** |
| 8 | **Market Impact** | die vom eigenen Auftrag verursachte Kursbewegung | **nein** bei einstelligen Kontraktzahlen |
| 9 | **Timing Risk** | Unsicherheit **um die Kostenschätzung herum** | **ja** |
| 10 | **Opportunity Cost** | entgangener Gewinn durch nicht ausgeführte Stücke | **ja**, bei Limit-Entries |

### Die drei, die man am ehesten übersieht

**Delay Cost** — fünf Entstehungsgründe, von denen vier vermeidbar sind: Zögern beim Absenden;
Unsicherheit, welcher Broker geeignet ist; bewusstes Abwarten auf bessere Preise (bei
gegenläufigem Momentum teuer); ungewollte **Informationsweitergabe** über Absicht und Ordergröße.
Der fünfte ist nicht vermeidbar: die **Übernacht-Kursbewegung** vom Schluss zur Eröffnung — daran
kann der Investor nicht teilnehmen, es entsteht ein Sunk Cost oder eine Ersparnis.

> Das ist exakt die Größe, die die ICT-Konzepte des Vaults als **Gap** behandeln —
> [[ORG (Opening Range Gap) & 1st Presented FVG]], [[New Week Opening Gap (NWOG) Bias]]. Kissell
> nennt sie aus Kostensicht: eine unvermeidbare Kostenkomponente.

**Timing Risk** — nicht die Kosten selbst, sondern die **Streuung um die Kostenschätzung**. Drei
Bestandteile:

```
Timing Risk  =  Preisvolatilitaet            (Kurs liegt hoeher/tiefer als geschaetzt)
              + Liquiditaetsrisiko           (schwankende Zahl der Gegenparteien)
              + Parameterschaetzfehler       (Standardfehler der Market-Impact-Parameter)
```

**Market Impact** — die Definition ist prinzipiell nicht messbar: die Differenz zwischen dem
tatsächlichen Kursverlauf **mit** dem Auftrag und dem, der **ohne** ihn eingetreten wäre. Man kann
nie beide gleichzeitig beobachten. Kissell nennt das die *„Heisenberg uncertainty principle of
trading"*.

## Zwei Klassifikationen

**Nach Beeinflussbarkeit und Transparenz:**

```
                FIX (nicht steuerbar)        VARIABEL (steuerbar)
SICHTBAR        Commission                   Spreads
                Fees                         Taxes
                Rebates
VERBORGEN       —                            Delay Cost
                                             Price Appreciation
                                             Market Impact
                                             Timing Risk
                                             Opportunity Cost
```

> **Die verborgenen Komponenten machen den größten Anteil der Gesamtkosten aus und bieten das
> größte Verbesserungspotenzial.** Werden sie nicht kontrolliert, können sie „superior investment
> opportunities" auf marginal profitabel drücken oder profitable ins Minus kippen.

Sichtbar heißt: die Gebührenstruktur ist **vorab bekannt**. Verborgen heißt: sie steht erst nach
der Ausführung fest und muss **statistisch geschätzt** werden (Market Impact typischerweise per
nichtlinearer Regression).

**Nach Phase im Investmentzyklus:**

```
Investment Costs   Taxes, Delay Cost              — von Entscheidung bis Orderfreigabe
Trading Costs      Commission, Fees, Rebates,     — waehrend der Ausfuehrung
                   Spreads, Price Appreciation,     (groesster Block)
                   Market Impact, Timing Risk
Opportunity Cost   Opportunity Cost               — was gar nicht ausgefuehrt wurde
```

Opportunity Cost ist konkret berechenbar:

```
Opportunity Cost = nicht ausgefuehrte Stueck × Kursaenderung waehrend die Order im Markt war
```

## Cost versus PnL — die Vorzeichenkonvention

Die Branche ist uneinheitlich; Kissell legt fest:

```
"Cost"   positiv = schlechter als der Benchmark      z.B. +30 bp = Underperformance
         negativ = besser als der Benchmark          z.B. −30 bp = Ersparnis

"PnL"    negativ = schlechter als der Benchmark      z.B. −5 bp = Underperformance
         positiv = besser als der Benchmark          z.B. +5 bp = Outperformance
```

Bei jeder übernommenen Kostenzahl aus fremder Quelle ist also **zuerst zu klären, welche der
beiden Konventionen gilt** — sonst dreht sich das Vorzeichen der Aussage um.

## Was eine Kostenkennzahl ist — und was nicht

Die für dieses Projekt schärfste Unterscheidung des Buches:

| Vergleich des Ausführungspreises mit … | ist … |
|---|---|
| **VWAP** über den Tag | **keine Kosten**, sondern ein **Performance-Proxy** |
| **Schlusskurs** des Tages | **keine Kosten**, sondern ein Proxy für **Tracking Error** |
| **Eröffnungskurs** bzw. Marktpreis bei Ordereingang | **echte Kosten** für den Fonds — sagt aber nichts über die Ausführungsqualität |

Daraus folgt: Kostenmessung und Performancebewertung sind **zwei verschiedene Auswertungen** und
brauchen **verschiedene Benchmarks**. Wer beides in eine Zahl presst, misst nichts Eindeutiges.

## Messen vs. Prognostizieren

```
Kostenmessung   ex post,  EIN Wert,  direkt aus Preisdaten,  positiv oder negativ

Kostenprognose  ex ante,  eine VERTEILUNG:
                Erwartungswert  = Market Impact + Price Appreciation
                                  (Impact immer positiv; Appreciation kann
                                   null, positiv oder negativ sein)
                Standardfehler  = Timing Risk
                                  (Preisvolatilitaet + Liquiditaetsrisiko + Parameterfehler)
```

## Die drei TCA-Phasen

| Phase | Zweck |
|---|---|
| **Pre-Trade** | Price Appreciation, Market Impact und Timing Risk prognostizieren, Alternativstrategien vergleichen, die zum Anlageziel passende auswählen |
| **Intraday** | Anpassung an die tatsächlichen Bedingungen. *„The only certainty in trading is that actual conditions will differ from expected."* |
| **Post-Trade** | **keine Entscheidung** — das Zeugnis. Waren die Pre-Trade-Modelle treffsicher? Waren die Entscheidungen konsistent mit dem Anlageziel? |

> *„Best execution is determined more on decisions made pre-trade than post-trade. Most analysts
> are very good Monday morning quarterbacks. However, investors need a quality coach who can make
> and execute decisions under pressure with unknown conditions."*

Ein guter Post-Trade-Report sollte nach Kategorien aufschlüsseln: große/kleine Orders,
günstige/ungünstige Kursbewegung, hohe/niedrige Volatilität, steigender/fallender Markt — plus
Trendanalyse über die Zeit.

## Bezug zu diesem Projekt

**Der offene Backlog-Punkt zum Kommissionsmodell.** Kissells Komponente 1 sagt, worin der Fehler
besteht: Futures-Kommission ist **$/Kontrakt** (fix, sichtbar), nicht ein Prozentsatz des
Nominalwerts. Bei MNQ mit ~$2 Punktwert und 20× Hebel treibt das Notional-Modell die Gebühren um
Größenordnungen nach oben — die gemessenen $46.065 im MNQ-Lauf sind ein Artefakt des falschen
Modells, keine reale Kostenschätzung.

**Was in `algo/` realistisch modellierbar ist:**

```
Commission   $/Kontrakt, fix          → ersetzt commission=0.0002
Fees         $/Kontrakt, fix          → in die Kommission einrechnen
Spread       1 Tick MNQ = 0,25 Pkt    → bei Market-Entry als halber/ganzer Spread ansetzen
Delay Cost   Signalzeit → Orderzeit   → im Backtest = 0, live nicht
Market Impact ≈ 0                     → bei einstelligen Kontraktzahlen vernachlaessigbar
Opportunity Cost                      → relevant, sobald Limit-Entries genutzt werden
```

**Was daraus folgt und bisher fehlt:** Die Berichte in
[[Ensemble-Strategie — Backtest-Ergebnis & Commission-Verzerrung (laufend)]] weisen einen
Gesamtkostenblock aus, aber keine **Zerlegung**. Erst die Aufteilung zeigt, welcher Teil fix und
unvermeidbar ist und welcher durch andere Ausführung beeinflussbar wäre.

Und der Punkt zur Benchmark-Wahl ist unmittelbar anwendbar: `algo/`-Auswertungen vergleichen
Ausführungen bisher nicht systematisch gegen einen definierten Referenzpreis. Nach Kissell wäre
der **Preis zum Signalzeitpunkt** der richtige Kosten-Benchmark — nicht der Tagesschluss und nicht
der VWAP.

Weiterführend: [[Implementation Shortfall]] (die zusammenfassende Kennzahl über alle
Komponenten), [[Trader's Dilemma & Efficient Trading Frontier]] (warum Impact und Timing Risk
nicht gleichzeitig minimierbar sind), [[Performance-Kennzahlen-Katalog]].
