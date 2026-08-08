---
tags: [source, algo-methodology, machine-learning, youtube, deep-learning]
created: 2026-08-08
updated: 2026-08-08
raw: "[[yt-2bE2iyRBK1E-transcript]]"
raw_path: "raw/algo-ml/yt-2bE2iyRBK1E-transcript.md"
---

# Two Sigma — Machine Learning Models of Financial Data (Source)

Quelle: YouTube, Kanal **Two Sigma**, veröffentlicht 2022-07-05, Länge 1:00:34.
Vortragender: **Justin Sirignano** — Two Sigma Securities und Associate Professor für Mathematik
an der University of Oxford. Auto-generierte Untertitel, volle Abdeckung inkl. Q&A.

> Kein ICT-Material. Institutionelle Primärquelle zur Frage, ob und wie Machine Learning im
> Handel funktioniert — die zugehörige begutachtete Arbeit ist
> **Sirignano & Cont, „Universal features of price formation in financial markets"**,
> Quantitative Finance 19(9), 2019, [arXiv:1803.06917](https://arxiv.org/abs/1803.06917).

## Kernaussagen (gefiltert)

### 1. Die Warnung, die alles andere relativiert

> *„Even if a model can predict future price moves with an accuracy greater than 50 %, a trading
> strategy based upon that model may not be profitable and could in fact lose money."*

Sirignano rechnet es vor: Das Modell sagt einen steigenden Mid-Price voraus, die Vorhersage ist
**richtig**, der Mid-Price steigt — und der Trade verliert trotzdem $10, weil zum Ask gekauft und
zum Bid verkauft wurde. Die Spanne zwischen Geld- und Briefkurs frisst den Vorteil.

Das ist dieselbe Aussage wie [[Implementation Shortfall]] und
[[Transaktionskosten-Taxonomie (Kissell)]], hier aber aus der Feder eines Hochfrequenzhauses und
auf die Vorhersagegüte selbst bezogen: **Trefferquote ist keine Profitabilität.** Deckt sich mit
Masters' „Percent Wins Fallacy".

### 2. Universelles Modell schlägt instrumentspezifische Modelle

Der zentrale und für dieses Projekt wichtigste Befund — ausführlich unter
[[Universal Model & Instrument-Pooling]]:

- Ein **einziges** rekurrentes Netz, trainiert auf den zusammengelegten Daten von hunderten
  Aktien, schlägt durchgängig die einzeln je Aktie trainierten Modelle.
- Es verallgemeinert auf **nie gesehene** Aktien (Training auf ~500 Titeln, Test auf ~500 anderen).
- Es bleibt **über ein Jahr out-of-sample** stabil.
- In der begutachteten Fassung: *„The universal model most strongly outperforms the stock-specific
  models on stocks with less data."*

Begründung im Q&A: weniger Überanpassung durch mehr Daten, plus Transferlernen — ein Regime, das
Instrument A nie erlebt hat, hat Instrument B vielleicht erlebt.

### 3. Datengrößenordnung

Drei Jahre Event-für-Event-Orderbuchdaten für rund 1.000 Aktien, **hunderte Milliarden**
Datenpunkte. Training verteilt über **25 GPUs** mit asynchronem stochastischem Gradientenabstieg.
Deep-Learning-Modelle haben hunderttausende bis Millionen Parameter — bei zu wenig Daten führt das
zu Überanpassung.

Sirignano ergänzt aber ausdrücklich: Bei **mittelgroßen** Datensätzen kann ML mit passenden
Modellierungsansätzen weiterhin sinnvoll sein — man muss dann nur besonders sorgfältig prüfen, ob
Überanpassung auftritt.

### 4. Nichtlinearität zahlt sich aus

LSTM-Netze schlagen ein lineares Vergleichsmodell (Vektor-Autoregression) durchgängig über rund
500 Aktien. Das ist der Nachweis, dass in den Orderbuchdaten tatsächlich **nichtlineare**
Zusammenhänge stecken — sonst gäbe es keinen Unterschied.

### 5. Reinforcement Learning für die Orderausführung, nicht für die Richtung

Zweites Beispiel: RL entscheidet **wann** eine bereits beschlossene Order abgesetzt wird
(Marktorder sofort vs. warten; Limitorder mit adaptivem Abbruchzeitpunkt).

- Vergleichsmaßstab ist die sofortige Marktorder, definiert als Kostenersparnis null.
- Das RL-Modell erzielt über rund 100 Aktien durchgehend **positive** Kostenersparnis, in
  Basispunkten, mit erheblicher Streuung je Aktie.
- Längerer Zeithorizont (60 s statt 10 s) bringt mehr Ersparnis.
- Die Limitorder-Strategie schlägt die reine Marktorder-Strategie leicht.

Bemerkenswert: RL wird hier **nicht** zur Richtungsvorhersage eingesetzt, sondern zur Ausführung.

### 6. Offene Grenzen, von ihm selbst benannt

Auf die Frage nach Marktregime-Wechseln: Das Modell war ein Jahr out-of-sample stabil —
*„it's a good question whether for longer time periods it will remain stable."* Keine Behauptung
über längere Zeiträume.

## Bewusst ausgefiltert

Rekrutierungs-Q&A von Two Sigma (Bürostandorte, Praktikumszyklen, Homeoffice-Regelung,
Bewerbungstipps) — rund ein Drittel der Aufzeichnung, ohne fachlichen Gehalt. Ebenso der
rechtliche Haftungsausschluss und die Ratschläge zur Studienwahl.

## Verwandt

- [[Universal Model & Instrument-Pooling]] — der übertragbare Kernbefund
- [[Machine Learning für den Algo — Bewertung (laufend)]] — Gesamteinordnung
- [[Meta-Labeling (López de Prado)]] — die für dieses Projekt passende ML-Bauform
- [[Implementation Shortfall]], [[Transaktionskosten-Taxonomie (Kissell)]] — dieselbe Kostenwarnung
- [[Reinforcement Learning für Handel — Grenzen (Starke)]] — Gegenstück aus der Praxis
