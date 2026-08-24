---
tags: [model, ict, trading-ict, mentorship-2020, quadranten, cisd]
created: 2026-08-02
updated: 2026-08-23
sources: ["[[CISD Mini Serie - Lecture 2 (Source)]]"]
---

# Graded Price Swings

Ein Modell, das die **Swing Highs/Lows „gradet"** — also die antizipierte Range in Viertel teilt und
sich die Level einzeichnen lässt (25 %, 50 %, 75 %). Es macht Aussagen darüber, **welche Reaktion an
welchem Level** zu erwarten ist.

![[CISD Mini Serie - Graded Price Swings 25 50 75.png]]
*EURUSD 4H: „Buy Program" am Tief, darüber die eingezeichneten Level 25 % Grade, 50 % Grade und
75 % Grade.*

## Reaktion je Level

- Am **50-%-Level** ist eine **Consolidation** zu erwarten.
- An den **übrigen Quadranten** meist ein **kleineres Retracement**.

Das ist der eigentliche Nutzen: nicht jedes Level bedeutet dasselbe, und die Erwartungshaltung wird
vorab festgelegt statt im Nachhinein erklärt. Zur Quadranten-Logik allgemein siehe
[[Chain of Custody (Q-Validation)]] und [[Equilibrium Vs. Discount]].

## Das 50-%-Level im Detail

Kommt Preis in einem Buy Program am **50 % der antizipierten Range** an, entscheidet sich das
weitere Vorgehen an der Frage, ob dort eine Imbalance liegt:

- **Imbalance kurz unter 50 %** → sie wird **meistens zum [[Breakaway Gap]]**.
- **Keine Imbalance vorhanden** → stattdessen wird das **nächstliegende Short Term Low** genommen.
- **Oberhalb des 50-%-Levels** gilt dasselbe Spiel: Gaps werden oft zu Breakaway Gaps, oder Short
  Term Lows werden genommen. Spiegelbildlich im Sell Program.

![[CISD Mini Serie - Graded Price Swings Detail.png]]
*Dieselben Grade-Level im Detail — das 50 % Grade als Konsolidierungszone auf dem Weg nach oben.*

## CISD als Schalter

Der Wechsel zwischen Buy- und Sell-Programm passiert über das
[[CISD (Change in State of Delivery)|CISD]]: Preis **closed über dem Swing High** (bzw. unter dem
Swing Low) — damit switcht das Programm.

## Verhältnis zum MMXM

> **Es sind laut Quelle nur zwei Modelle.** Das Graden der Price Swings ist ein **eigenständiges
> Modell neben dem [[MMXM (Market Maker Buy & Sell Model)|MMXM]]** (Market Maker Buy/Sell Model): schaut ICT nicht nach einem MMXM-Setup,
> schaut er nach diesem. *„Mehr Models gibt es nicht es sind diese beiden!"*

> ⚠️ Diese Aussage steht quer zum übrigen Vault, der unter `wiki/models/` inzwischen über 20 Seiten
> führt ([[One Shot One Kill Model]], [[Silver Bullet Model]], [[Weekly Range Trading Model]] …).
> Vermutlich ist „Modell" hier enger gemeint — im Sinne eines **übergeordneten Deliverungs-Rahmens**,
> nicht eines Setups. Nicht aufgelöst, nur markiert.
>
> ✅ **Erledigt (2026-08-23)**: MMXM hat jetzt eine eigene Seite — [[MMXM (Market Maker Buy & Sell Model)|MMXM]].
> Dort sind beide Kurvenhälften, die ITH/ITL-Abgrenzung und die HTF-Reihenfolge belegt.

## Verwandt

- [[CISD (Change in State of Delivery)]] — der Schalter zwischen den Programmen
- [[Buy & Sell Program]], [[Algorithmic Order Flow]]
- [[Breakaway Gap]] — was aus der Imbalance am 50-%-Level wird
- [[Chain of Custody (Q-Validation)]], [[Equilibrium Vs. Discount]]
- [[Market Maker Manipulation Templates]] — die Manipulations-Profile, nicht das MMXM selbst
- [[Smart Money Concepts (SMC)]]
