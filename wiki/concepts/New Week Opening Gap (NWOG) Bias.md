---
tags: [concept, ict, trading-ict, bias]
created: 2026-08-01
updated: 2026-08-02
sources: ["[[Essentials To ICT Daytrading (Source)]]", "[[Intraweek Market Reversals & Overlapping Models (Source)]]"]
---

# New Week Opening Gap (NWOG) Bias

Der NWOG (Kursgap zwischen Freitag-Close und Sonntag-/Montag-Open) dient als wöchentlicher
Bias-Anker für [[ICT Daily Range Session Timing|Daytrades]].

## Regel

- Bleibt der Kurs die gesamte Handelswoche **unterhalb** des NWOG → Bias **bearish**, es werden
  praktisch nur Shorts gesucht.
- Bleibt der Kurs die gesamte Handelswoche **oberhalb** des NWOG → Bias **bullish**, es werden
  praktisch nur Longs gesucht.
- Wird das NWOG intraweek durchbrochen → möglicher **major Intraday/Weekly Shift**, Bias kippt.
- Ausnahme: Trades in ein höher timeframiges Discount-PD-Array werden gegen die NWOG-Bias-Richtung
  gesucht — dort danach wieder die eigentliche Bias-Richtung suchen (visaversa bei Premium-PD-Array).

![[image 232.png]]
*NWOG-Bias-Regel: unterhalb des NWOG nur Shorts, oberhalb nur Longs gesucht.*

## Timing-Beobachtung

- Das Weekly High/Low bildet sich im Normalfall bereits **Montag**, wenn der Preis am Montag
  über/unter dem NWOG tradet.
- **Donnerstag** ist ein wahrscheinlicher Kandidat für ein Reversal, wenn die Woche bis dahin
  konsistent auf einer Seite des NWOG geblieben ist.

![[image 231.png]]
*Donnerstag als typischer Reversal-Kandidat bei konsistenter NWOG-Seite über die Woche.*

![[image 234.png]]
*Das Weekly High/Low bildet sich oft schon am Montag, wenn Preis über/unter dem NWOG tradet.*

## Intraweek Reversal (Montag/Dienstag)

- Tradet Preis bereits Montag/Dienstag **schnell und mit großen Candles** in eine PD, ist das oft ein
  Reversal-Signal (im Verbund mit Bias und Trending Conditions). Dann eine HTF-PD suchen — mindestens
  Daily, bevorzugt Weekly.
- Speed + Magnitude deuten auf Repricing durch große Player hin (Zinsentscheide, Notenbanken, oder
  Spekulation).
- Beispielmuster: großer bearish Candle am Montag erreicht eine PD, Preis kehrt zur "Balanced Price
  Range" zurück, um ein **MMBM/MMSM** (Market Maker Buy/Sell Model) zu bilden — ein Lower High am
  Dienstag verringert die Wahrscheinlichkeit etwas, spricht aber oft trotzdem stark dafür.

![[image 206.png]]
*Intraweek Reversal: Preis erreicht innerhalb von 2 Tagen eine tiefere PD — Montag große bearishe
Candle, Dienstag erreicht die PD.*

![[image 209.png]]
*Preis kehrt oft zur Balanced Price Range zurück, um ein MMXM zu bilden.*

## Offene Punkte

- ⚠️ "Discount PD Array" und "PD Array" sind hier vorausgesetzt, aber noch nicht als eigene
  Konzept-Seite erfasst — Kandidat für eine spätere `wiki/concepts/PD Array.md` Seite (taucht in
  `raw/trading-ict/Core Content/` mehrfach auf, z.B. in "Blending IPDA Data Ranges & PD Arrays.md",
  "Equilibrium Vs. Discount.md").

## Backtest gegen echte Daten

[[Statistische Muster jenseits der ICT-Konzepte (laufend)]]#5 prüft die Bias-Regel und beide
Timing-Behauptungen hier gegen n=28 Wochen MNQ-Daten: Bias-intakt-Quote nur 7,1 % (das NWOG
wird fast immer wieder erreicht), Wochen-Low bevorzugt tatsächlich Montag, Wochen-High aber
nicht, und die Donnerstag-Reversal-These wird klar widerlegt (Donnerstag ist der
unwahrscheinlichste Tag für beide Extreme). `algo/live_status.py` liefert montags ein
`nwog`-Feld live mit.
