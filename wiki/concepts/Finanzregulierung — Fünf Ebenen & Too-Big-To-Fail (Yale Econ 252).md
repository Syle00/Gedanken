---
tags: [concept, quant-finance, risikomanagement, regulierung, yale-econ252]
created: 2026-08-12
updated: 2026-08-12
sources: ["[[2012-04-05 - Yale Econ 252 Lecture 12 - Misbehavior, Crises, Regulation and Self Regulation (Source)]]", "[[2012-04-05 - Yale Econ 252 Lecture 18 - Monetary Policy (Source)]]"]
---

# Finanzregulierung — Fünf Ebenen & Too-Big-To-Fail (Yale Econ 252)

Shillers Systematik der Finanzregulierung (Firmenebene bis International) plus die
Basel-III-Kapitalanforderungen aus der Zentralbank-Vorlesung. Institutionelles Gegenstück zu den
verhaltensbasierten Erkenntnissen in
[[Behavioral Finance (Prospect Theory & Kognitive Verzerrungen, Yale Econ 252)]].

## Fünf Regulierungsebenen (von innen nach außen)

1. **Innerhalb der Firma**: Board of Directors als "interner Regulator" — Pflichten: *Duty of
   Care* (Sorgfaltspflicht, informierte Überwachung statt reines Anwesenheitsritual) und *Duty of
   Loyalty* (gegenüber Aktionären). Katalog von "Tunneling"-Risiken, gegen die ein Board wachen
   muss: verdeckte Vorzugsgeschäfte bei Asset-Verkäufen, überteuerte Verträge an Nahestehende,
   überhöhte Managervergütung, Abzweigen von Geschäftschancen, Insiderhandel.
2. **Branchenverbände / Selbstregulierung**: historisches Beispiel New York Stock Exchange
   (Buttonwood Agreement 1792) — ursprünglich eine Preisabsprache (Mindestprovision), erst 1975
   ("Mayday") durch die SEC dereguliert; parallel entstand das National Market System zur
   Sicherstellung bestmöglicher Ausführungspreise.
3. **Lokal/Bundesstaat**: US-Blue-Sky-Laws (ab Kansas 1911) — erste staatliche Wertpapieraufsicht,
   scheiterte an grenzüberschreitenden Betrugsmaschen ("Boiler Rooms").
4. **National**: SEC (1934, New-Deal-Ära) mit dem Grundprinzip **Disclosure statt Verbot**
   ("Sunshine is the best disinfectant", Louis Brandeis) — Unterscheidung öffentlich (streng
   reguliert, IPO-Pflichten) vs. privat (Hedgefonds: max. 99 "akkreditierte" Investoren bei
   3(c)(1), 500 "super-akkreditierte" bei 3(c)(7), kein Werbeverbot-Verstoß).
5. **International**: Bank for International Settlements (Basel, 1930), Basel-Ausschuss (1974),
   G7→G20 (2008 erweitert um China/Indien u. a.), Financial Stability Board — beratende Funktion
   ohne bindende Rechtskraft, aber hoher Einfluss über nationale Umsetzung.

## Too-Big-To-Fail und Macro- vs. Micro-Prudential-Regulierung

- **Micro-prudential**: schützt einzelne Anleger/Institute (klassische SEC-Rolle).
- **Macro-prudential**: schützt das Gesamtsystem — reagiert auf die "Too-Big-To-Fail"-Dynamik:
  große systemrelevante Firmen genießen eine implizite Staatsgarantie, was ihnen einen Anreiz zu
  höherem Risiko gibt als kleinen Firmen (moral hazard auf Systemebene). Dodd-Frank (2010)
  verschiebt den Schwerpunkt explizit von micro- zu macro-prudential (Financial Stability
  Oversight Council, FSOC).

## Basel-III-Kapitalanforderungen — vereinfachtes Rechenbeispiel

- Unterscheidung **Reserve Requirements** (Anteil der Transaktionskonten, die als Bargeld/
  Fed-Einlage gehalten werden müssen — historisch gegen Bank Runs) vs. **Kapitalanforderungen**
  (Anteil der **risikogewichteten Aktiva**, der durch Eigenkapital gedeckt sein muss — schützt
  gegen Kreditausfälle).
- Basel III: 4,5 % Common-Equity-Minimum + 2,5 % Kapitalerhaltungspuffer = 7 % Ziel; Regulatoren
  können bei erkannter Blasenbildung antizyklisch bis zu 9,5 % verlangen.
- **Prozyklisches Grundproblem, das Shiller explizit kritisiert**: Banken müssen in der Krise genau
  dann neues Eigenkapital aufnehmen oder Kredite verkaufen, wenn das am schwierigsten ist (Investoren
  meiden angeschlagene Banken, alle Banken verkaufen gleichzeitig) — ohne Zentralbank als Lender of
  Last Resort kollabiert das System in genau diesem Moment.

## Bezug zu diesem Projekt

- Kein direkter Regelbezug für `algo/` (Regulierung betrifft Broker/Institutionen, nicht die
  Handelsregeln selbst), aber relevant als Kontextwissen für die IBKR-Anbindung (Roadmap-Punkt 4):
  Interactive Brokers unterliegt selbst SEC-/CFTC-Aufsicht, Kundengelder sind über SIPC
  (Pendant zur im Vorlesungstext genannten "Securities Investor Protection Corporation") bis zu
  einem Limit abgesichert — relevant, sobald echtes Kapital eingesetzt wird (siehe Security-Gate
  in CLAUDE.md).
- Die Too-Big-To-Fail-/Moral-Hazard-Logik ist eine allgemeine Warnung, keine spezifische
  Backtest-Regel — dient primär als Hintergrundwissen für Markstruktur-Interpretation (z. B.
  warum Zentralbank-Interventionen wie FOMC-Entscheidungen so marktbewegend sind, siehe
  [[FOMC (Federal Open Market Committee)]]).
