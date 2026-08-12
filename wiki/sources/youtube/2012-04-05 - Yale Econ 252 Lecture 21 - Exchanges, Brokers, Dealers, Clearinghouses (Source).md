---
tags: [source, quant-finance, yale-econ252, risikomanagement]
created: 2026-08-12
updated: 2026-08-12
sources: []
---

# Yale Econ 252 — Lecture 21: Exchanges, Brokers, Dealers, Clearinghouses (Source)

Quelle: YouTube, Kanal YaleCourses, veröffentlicht 2012-04-05, Länge 1:09:22. Open Yale Courses,
Economics 252, Robert Shiller.
Rohtranskript: `raw/financial-markets-2011-with-robert-shiller/yt-kAl8DezwLAE-transcript.md`.

## Zusammenfassung

Broker-vs-Dealer-Unterscheidung, Börsengeschichte (Rom → Amsterdam 1602 → NYSE 1792 → NASDAQ
1970er → elektronischer Handel), Order-Buch-Mechanik (Market/Limit/Stop-Orders), High-Frequency-
Trading und der Flash Crash vom 6. Mai 2010. **Risikomanagement-relevant**: das "Gambler's
Ruin"-Modell für Market Maker.

## Kernpunkte

- Broker (Agent, Kommission) vs. Dealer (Prinzipal, Spread/Markup) als Grundunterscheidung; NYSE
  = Broker-/Auktionsmarkt, NASDAQ = Dealer-Markt.
- Order-Typen: Market Order (kein Preis spezifiziert), Limit Order (Preis + Menge), Stop(-Loss)
  Order (Verkauf bei Unterschreitung eines Schwellenwerts) — Shiller warnt explizit vor
  Market Orders ohne Preislimit.
- Flash Crash 6. Mai 2010: S&P fiel binnen Minuten um weitere 6 % (nach bereits −4 %), erholte
  sich dann schnell — SEC/CFTC-Studie identifiziert Hochfrequenzhandel-Feedback-Schleifen als
  Ursache, nicht direkten Zusammenhang mit der Finanzkrise selbst.
- **Gambler's-Ruin-Formel für Dealer**: Ruinwahrscheinlichkeit `= [(1−p)/p]^S` bei
  Gewinnwahrscheinlichkeit `p` je Trade und Startkapital `S` — geht nie exakt auf null, selbst bei
  `p > 0,5`. Begründet, warum ein Dealer den Bid-Ask-Spread breit genug halten muss (informierte
  Gegenparteien "picken" ihn sonst systematisch ab), aber nicht beliebig breit (sonst kein
  Geschäft).

## Bezug

Die Gambler's-Ruin-Formel ist strukturell identisch mit der Ruin-Grenze in
[[Kelly-Formel & optimales Leverage (Chan)]] — Bestätigung derselben mathematischen Grundlogik
aus unabhängiger Quelle, kein neuer Formelbedarf.
