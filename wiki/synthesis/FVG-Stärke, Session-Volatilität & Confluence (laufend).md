---
tags: [synthesis, ict, fvg, backtest, laufend]
created: 2026-08-13
updated: 2026-08-13
sources: ["[[Fair Value Gap (FVG)]]", "[[Volume Imbalance (VII)]]", "[[Market Structure Shift (MSS)]]"]
---

# FVG-Stärke, Session-Volatilität & Confluence (laufend)

Laufende Auswertung der Frage: **wann ist die Wahrscheinlichkeit am höchsten?** Grundlage sind
Jannes' Thesen vom 13.08.2026, geprüft mit `algo/backtest_fvg_strength.py` über alle
MNQ-1m-Daten in `raw/marktdaten/`.

**Stand: 27 Handelstage (08.07.–13.08.2026), 7.279 FVGs, 6.851 simulierte Trades.**
Diese Seite wird bei wachsendem Datenbestand überschrieben, nicht ergänzt.

## Die vier Thesen

| # | These | Ergebnis |
|---|---|---|
| T1 | FVG-Größe hängt an Session/Volatilität; nach 9:30 viel größer als London, Richtung NY PM zurück auf London-Niveau | **bestätigt** |
| T2 | Ein starkes FVG bricht einen Swing High/Low (MSS/BOS) | **nicht belegbar**, sobald die Größe kontrolliert wird |
| T3 | Groß + MSS/BOS = High Probability | **Größe ja, aber messbedingt** — siehe Vorbehalt unten |
| T4 | Überlappung mit Higher-TF-PD-Array (Qs) bzw. NDOG/NWOG hebt die Wahrscheinlichkeit | **HTF-Qs: ja, klein. NDOG: kein Beleg** |

## T1 — Session & Volatilität (klar bestätigt)

| Session | n FVG | Median FVG-Größe | Median 1m-Kerze | FVG ÷ Kerze |
|---|---|---|---|---|
| Asia (18:00–03:00) | 2.772 | 5,00 | 10,75 | 0,48 |
| London (03:00–08:30) | 1.776 | 4,75 | 10,12 | 0,47 |
| Premarket (08:30–9:30) | 348 | 5,25 | 11,75 | 0,47 |
| **NY Open (9:30–10:30)** | 368 | **13,50** | **29,38** | 0,47 |
| NY AM (10:30–12:00) | 495 | 7,50 | 24,88 | 0,32 |
| Lunch (12:00–13:30) | 500 | 6,00 | 17,00 | 0,41 |
| NY PM (13:30–16:00) | 748 | 5,75 | 13,00 | 0,44 |

- Der 9:30-Open trägt die **2,8-fache** FVG-Größe und die **2,9-fache** Kerzenrange von London.
- NY PM fällt zurück, aber nicht ganz auf London-Niveau: 5,75 vs. 4,75 Punkte (Kerze 13,00 vs.
  10,12), also rund 20–28 % darüber. Die Richtung der These stimmt, die Gleichsetzung „wieder
  ähnlich groß wie London" ist eine leichte Untertreibung.
- **Der wichtigste Befund steht in der letzten Spalte:** das Verhältnis FVG-Größe ÷ lokale
  Kerzenrange liegt in *jeder* Session bei 0,44–0,48 (Ausreißer NY AM mit 0,32). Ein FVG ist
  also **immer rund die halbe Kerzenrange groß** — was sich zwischen den Sessions ändert, ist
  nicht die FVG-Struktur, sondern nur der Maßstab.

> **Folge für den Algo:** „groß" darf nie eine absolute Punktzahl sein. Ein 8-Punkte-FVG ist in
> London riesig und um 9:35 unterdurchschnittlich. Der Schwellwert gehört auf
> `size / Median-Kerzenrange der letzten 30 Kerzen` (im Backtest `size_rel`, Median 0,45).

## T2–T4 — Trefferquote (mit hartem Vorbehalt)

Regel: Limit-Entry am **C.E.**, Stop an der fernen Kante, Ziel **2R**, echter Punktwert
($2/Punkt MNQ). Breakeven bei 2R liegt bei **33,3 %**.

| Gruppe | n FVG | Trades | Win % | Win % ohne strittige | $/Trade | dubious % |
|---|---|---|---|---|---|---|
| alle | 7.279 | 6.851 | 34,0 | 69,6 | 1,94 | 51,1 |
| normal (kein Swing-Break) | 3.799 | 3.604 | 31,5 | 71,5 | 1,26 | 55,9 |
| stark (Swing-Break) | 3.480 | 3.247 | 36,8 | 67,9 | 2,69 | 45,8 |
| nur groß (≥ Median `size_rel`) | 3.640 | 3.428 | 45,6 | 62,8 | 4,25 | 27,3 |
| stark + groß | 2.075 | 1.941 | 45,8 | 62,3 | 4,63 | 26,5 |
| **stark + groß + HTF-Qs** | 1.016 | 942 | **47,9** | 62,7 | **6,33** | 23,7 |
| stark + groß + NDOG | 152 | 144 | 44,4 | 55,2 | 4,89 | 19,4 |
| nur HTF-Qs | 2.583 | 2.427 | 39,1 | 66,9 | 3,20 | 41,6 |

### ⚠️ Der Vorbehalt, der die halbe Tabelle relativiert

`dubious %` = Anteil der Trades, bei denen **Stop und Ziel in derselben 1m-Kerze** liegen. Die
Reihenfolge ist auf 1m-Daten nicht feststellbar; konservativ zählen sie als Verlust
(`CLAUDE.md`, Korrektheitsstandard). Bei kleinen FVGs betrifft das **56 %** aller Trades, bei
großen nur 27 %.

Rechnet man die strittigen Fälle heraus (Spalte „Win % ohne strittige"), **dreht sich die
Rangfolge um**: kleine/normale FVGs stünden dann bei 71,5 % gegen 62,3 % bei den großen. Die
Wahrheit liegt zwischen beiden Zahlen und ist mit Minutendaten **nicht entscheidbar**.

Was daraus trotzdem folgt, und zwar unabhängig von der Regel:

1. **Kleine FVGs sind auf 1m nicht handelbar-messbar.** Wenn Stop und Ziel in einer Kerze
   liegen, hängt das Ergebnis am Sekundenverlauf. Für den Algo heißt das: eine Mindestgröße ist
   nicht (nur) eine Wahrscheinlichkeitsfrage, sondern eine **Ausführbarkeitsfrage**.
2. **Fairer Vergleich nur bei ähnlicher `dubious`-Quote.** Die einzigen sauber vergleichbaren
   Paare:
   - `nur groß` (27,3 %) vs. `stark + groß` (26,5 %): 45,6 → 45,8 % bzw. 62,8 → 62,3 %.
     **Der Swing-Break bringt bei kontrollierter Größe nichts Messbares.** Damit ist T2 in der
     Form „Swing-Break macht das FVG stark" mit diesen Daten nicht belegt — die Größe erklärt
     den Effekt.
   - `stark + groß` (26,5 %) vs. `stark + groß + HTF-Qs` (23,7 %): 45,8 → 47,9 % und
     4,63 → 6,33 $/Trade. **T4 (Higher-TF-Qs) hält als kleiner, konsistenter Zusatzeffekt** —
     der beste $/Trade-Wert der ganzen Tabelle.
   - `stark + groß + NDOG` liegt auf beiden Metriken *unter* `stark + groß` (44,4 %/55,2 %).
     **Für die NDOG-Confluence gibt es in 27 Tagen keinen Beleg**, bei n=144 aber auch keinen
     belastbaren Gegenbeweis.

### Was den Vorbehalt auflösen würde

Ausführungsdaten feiner als 1m (Sekunden oder Ticks). Kommt mit der IBKR-Anbindung
(Roadmap-Punkt 4) ins Haus; bis dahin bleibt die konservative Zahl der Maßstab und die
optimistische die Obergrenze.

## Offene Punkte

- 27 Handelstage sind viele FVGs, aber **wenige Marktregime**; FVGs innerhalb eines Tages sind
  stark korreliert. Die Konfidenz ist niedriger, als n=6.851 suggeriert.
- NY AM fällt mit `size_rel` 0,32 aus der Reihe (alle anderen 0,41–0,48) — noch unerklärt.
- NWOG-Confluence ist mangels Montagen im Datensatz noch nicht getrennt ausgewertet.
- Die Higher-TF-Confluence prüft bisher nur die **Qs** von 15m-/1h-FVGs. Order Blocks,
  Session-Ranges und [[New Week Opening Gap (NWOG) Bias|NWOG]] fehlen als Quelle.

## Verwandt

- [[Fair Value Gap (FVG)]] — Definition, Grenzen, Einstufung stark/normal
- [[Market Structure Shift (MSS)]], [[New Day Opening Gap (NDOG)]]
- [[Muster-Validierung (laufend)]]
