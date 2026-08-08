---
tags: [source, algo-methodology, transaktionskosten, buch, referenz]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[The Science of Algorithmic Trading and Portfolio Management, Robert Kissell]]"]
---

# The Science of Algorithmic Trading and Portfolio Management (Source)

**Robert Kissell, Ph.D., Elsevier/Academic Press 2014.**
Rohquelle: `raw/The Science of Algorithmic Trading and Portfolio Management, Robert Kissell.md`
(42.871 Zeilen, aus dem beiliegenden PDF extrahiert).

Institutionelle Perspektive: **Transaktionskostenanalyse (TCA)**, Market-Impact-Modelle,
Implementation Shortfall, Ausführungsalgorithmen und Portfolio-Optimierung. Damit adressiert das
Buch eine Risikoart, die die anderen beiden Bücher des Vaults nicht behandeln — **Ausführungs-
und Kostenrisiko** statt Modell- und Hebelrisiko.

## ⚠️ Qualitätswarnung zur Rohquelle: Mathematik ist chiffriert

Das Quell-PDF hat eine **defekte Font-Kodierung** (kaputte ToUnicode-CMap). In Formeln stehen
Ziffern und Satzzeichen anstelle von Operatoren. Gegen einen zweiten Extraktor (`pdftotext`)
verifiziert — es ist also kein Konvertierungsfehler unserer Pipeline, sondern steckt im PDF:

```
2  =  −          ,  =  <
1  =  +          .  =  >
5  =  =          ½  =  [
:  =  .
(cid:N)          nicht aufloesbares Zeichen, bewusst stehengelassen
```

**Fließtext, Kapitelstruktur und Tabellenbeschriftungen sind korrekt** — nur Gleichungen,
Variablenindizes und Zahlenwerte innerhalb von Formeln sind betroffen.

**Vorgehen bei diesem Ingest:** Jede übernommene Formel wurde dekodiert **und arithmetisch
gegengeprüft**, wo das Buch ein Rechenbeispiel mitliefert. Beispiele für die Verifikation:

```
Rohtext:  $55,000 2 $52,500 2 $100 5 $2400
Dekodiert: $55.000 − $52.500 − $100 = $2.400          ✓ stimmt

Rohtext:  IS 5 $5000 2 $2400 5 $2600
Dekodiert: IS = $5.000 − $2.400 = $2.600               ✓ stimmt

Rohtext:  1 2 e20:5Á1 5 0:3935
Dekodiert: 1 − e^(−0,5·1) = 0,3935                     ✓ stimmt (1 − 0,6065)

Rohtext:  130 bp / 230 bp          → +30 bp / −30 bp
Rohtext:  POV 5 30%                → POV = 30 %
```

**Formeln ohne mitgeliefertes Rechenbeispiel wurden NICHT ins Wiki übernommen.** Wer sie braucht,
muss `raw/The Science of Algorithmic Trading and Portfolio Management, Robert Kissell.pdf`
danebenlegen. Das betrifft insbesondere das I-Star-Market-Impact-Modell mit seinen kalibrierten
Parametern und die Herleitungen zur Effizienzgrenze.

## Umfang dieses Ingests

Das Buch hat 42.871 Zeilen und deckt Marktmikrostruktur, Ausführungsalgorithmen, Market-Impact-
Kalibrierung, Portfolio-Optimierung, Risikomodelle und High-Frequency-Trading ab. **Ingestet
wurden gezielt die Teile, die für ein Ein-Instrument-Futures-Projekt anwendbar sind:**

| Kapitel/Thema | Wiki-Seite | Warum |
|---|---|---|
| Kap. 3: Zehn Kostenkomponenten, Klassifikation, TCA-Phasen | [[Transaktionskosten-Taxonomie (Kissell)]] | schließt eine bekannte Lücke im Projekt (Kommissionsmodell) |
| Kap. 3: Implementation Shortfall | [[Implementation Shortfall]] | die korrekte Definition von „Slippage" |
| Kap. 1: Trader's Dilemma, Efficient Trading Frontier, POV, Adaptionstaktiken | [[Trader's Dilemma & Efficient Trading Frontier]] | Ausführungsrisiko, relevant ab der IBKR-Anbindung |

**Bewusst nicht ingestet**, mit Begründung:

- **Market-Impact-Modelle (Kap. 4) im Formeldetail** — die Kalibrierungsparameter sind durch die
  Font-Störung unbrauchbar, und für die Ordergrößen dieses Projekts (einstellige
  MNQ-Kontraktzahlen im liquidesten Index-Future) ist Market Impact praktisch null. Das
  *Konzept* steht auf [[Trader's Dilemma & Efficient Trading Frontier]].
- **Portfolio-Optimierung und Multi-Asset-Risikomodelle** — das Projekt handelt ein einzelnes
  Instrument.
- **Broker-/Algorithmus-Vergleich mit nichtparametrischen Tests** (Wilcoxon Signed-Rank,
  Mann-Whitney/Rangsummen; Kap. 5) — methodisch interessant und auf den Vergleich zweier
  *Strategien* übertragbar, aber im Vault durch
  [[Monte Carlo Permutation Test (MCPT)]] und [[Training Bias & Selection Bias]] bereits
  abgedeckt, und dort ohne Chiffre-Risiko.
- **Marktmikrostruktur-Details des US-Aktienmarkts** (Rebates, Maker-Taker, Dark Pools, Smart
  Order Routing, Reg NMS) — für einen einzelnen Futures-Kontrakt an einer Börse gegenstandslos.
  Der Rebate-Mechanismus ist auf der Taxonomie-Seite kurz erfasst, weil er erklärt, warum
  Broker-Anreize von Kundeninteressen abweichen können.
- **High Frequency Trading und Black-Box-Modelle (Kap. 13)** — setzt Kolokation voraus.

## Die zentralen Aussagen

**1. Zehn getrennte Kostenkomponenten**, nicht „Kommission und Spread": Commission, Fees, Taxes,
Rebates, Spreads, Delay Cost, Price Appreciation, Market Impact, Timing Risk, Opportunity Cost.
Die **nicht-transparenten** Komponenten machen den größten Teil aus und bieten das größte
Verbesserungspotenzial. → [[Transaktionskosten-Taxonomie (Kissell)]]

**2. Der Trader's Dilemma:** Market Impact und Timing Risk sind **gegenläufig**. Aggressiv
handeln = hoher Impact, niedriges Timing-Risiko. Passiv = umgekehrt. Es gibt kein Optimum ohne
Festlegung der Risikoneigung. → [[Trader's Dilemma & Efficient Trading Frontier]]

**3. Was eine Kostenkennzahl ist und was nicht** — die für dieses Projekt schärfste Unterscheidung
des Buches:

> Der Vergleich des Ausführungspreises mit dem **VWAP** ist **keine Kostenkennzahl**, sondern ein
> Performance-Proxy. Der Vergleich mit dem **Schlusskurs** ist ein Proxy für Tracking Error. Nur
> der Vergleich mit dem **Eröffnungskurs bzw. dem Marktpreis bei Ordereingang** ist eine echte
> Kostenkennzahl — und sagt umgekehrt nichts über die Ausführungsqualität aus.

**4. Vorzeichenkonvention**, weil die Branche uneinheitlich ist:

```
"Cost"        positiv = Underperformance,  negativ = besser als Benchmark
"PnL"         negativ = Underperformance,  positiv = besser als Benchmark
```

**5. TCA hat drei Phasen:** *pre-trade* (Strategie wählen), *intraday* (Anpassung an tatsächliche
Bedingungen — „the only certainty in trading is that actual conditions will differ from
expected"), *post-trade* (Zeugnis, keine Entscheidung). Kissells Pointe dazu: *„Best execution is
determined more on decisions made pre-trade than post-trade. Most analysts are very good Monday
morning quarterbacks."*

## Bezug zu diesem Projekt

Der direkteste Treffer betrifft ein **offenes Problem aus `algo/PLAN.md`** (Eintrag 2026-08-07):

> „`commission=0.0002` ist Notional-proportional (Aktien-Modell) statt $/Kontrakt
> (Futures-Realität) und erzeugt bei 20x Hebel die $46k Gebühren — sollte vor jeder
> Kapitalentscheidung auf ein realistisches Futures-Kommissionsmodell umgestellt werden."

Kissells Kapitel 3 ist genau die Systematik, die dafür fehlt: welche Kostenarten es gibt, welche
fix und welche variabel sind, welche sich überhaupt beeinflussen lassen. Details und die
Übertragung auf MNQ stehen auf [[Transaktionskosten-Taxonomie (Kissell)]].

Ergänzt die Kostenbetrachtung der anderen Quellen: Chan lässt Transaktionskosten in allen
Beispielen bewusst weg
([[Algorithmic Trading - Winning Strategies and Their Rationale (Source)]]), Masters ebenso
([[Testing and Tuning Market Trading Systems (Source)]]) — beide, um den Blick auf die Statistik
zu lenken. Kissell ist die Quelle, die diese Lücke füllt.
