---
tags:
  - Daily-Bias
Bias:
  - Bullish
Date: 2026-08-03
NQ/ES: MNQ
id: 2026-08-03-02
typ: daily-bias
modus: live
kw: 2026-W32
wochentag: Montag
modell: "NY PM Silver Bullet"
liquidity_ziel: "Buyside-Cluster 28.725,75–28.763,75 (Freitags-High 31.07 + Montags-High 27.07)"
pd_arrays: [Volume Imbalance (VII), New Week Opening Gap (NWOG) Bias, Judas Swing, Open Float & Liquidity Pools, ORG (Opening Range Gap) & 1st Presented FVG, Equilibrium Vs. Discount, ICT Daily Range Session Timing]
fehler: [S08]
---

# 2026-08-03 MNQ Daily Bias

## Bias

**Bullish** für den Tag

**Sein Plan (Original in `raw/Daily Bias 03.08.md`):** Montag im Daily schwierig, deshalb Liquiditaeten im 15m-Chart ('Bellweather Chart') suchen. Sehr weit im Premium geoeffnet, das NWOG ist stand jetzt eine VII — ein Drop dorthin nicht auszuschliessen. Buyside bei 28.763,75 als moegliches Target, dazu das Freitags-High. Ablauf: **erst Drop ins NWOG, dann Judas Swing Richtung Sellside, danach bullish weiter.** Gehandelt wird nur die NY PM Silver Bullet.

---

## Nachgerechnet

**Bestaetigt ✅**

- **News:** 10:00 ISM Manufacturing PMI (red) + ISM Manufacturing Prices (orange) — exakt so im Kalender. Zweiter Tag in Folge, an dem die News vor Sessionbeginn stehen.
- **Die VII-Einordnung des NWOG ist nach seiner eigenen Definition richtig.** `wiki/concepts/Volume Imbalance (VII).md`: Luecke zwischen **Close** einer Candle und **Open** der naechsten, Koerper beruehren sich nicht, **Wicks ueberlappen**. Hier: Freitag-Close **28.284,00** → Sonntag-Open **28.567,50**, 283,5 Punkte Koerperluecke; Freitags Range (H 28.725,75 / L 28.079,75) ueberlappt die heutige (ab ~28.340) massiv. Beide Bedingungen erfuellt. Und das Wiki fuehrt die VII ausdruecklich **als eigenstaendige PD Array und Draw** — sein "nicht auszuschliessen, dass wir dort runter gehen" ist damit gedeckt, nicht geraten.
- **28.763,75 stimmt auf den Tick.** Das ist das ETH-Tageshigh von **Montag 27.07**, gemacht um **05:45 NY**. Aus `raw/marktdaten/31.07.2026/MNQ 2026-07-31 15m.csv` verifiziert.
- **Freitags Daily High = 28.725,75**, gemacht am 31.07 um **09:30 zum RTH-Open** — ETH- und RTH-High sind identisch. Er nennt die Zahl nicht, aber der Punkt traegt: die beiden Highs liegen nur **38 Punkte** auseinander und bilden zusammen einen **Buyside-Cluster 28.725,75–28.763,75 mit zwei Highs**. Das erfuellt seinen eigenen Checklistenpunkt *"Target Liquiditaet min. 2 H/L"* — der im Altbestand nur 43 % der Zeit gesetzt war.
- **Er hat die Luecke von heute morgen selbst geschlossen.** Im Weekly Bias fehlte die Sequenz zwischen "bullish" und "NWOG fillen". Hier steht sie: Drop ins NWOG → Judas zur Sellside → dann aufwaerts. Genau der fehlende Teil, ohne Aufforderung nachgeliefert.
- **NWOG-Label auf dem Chart von 31 auf 32 korrigiert** (Screenshots 02:28 und 02:32).

**Korrekturen ⚠️**

1. **Widerspruch zum eigenen Weekly Bias von 33 Minuten vorher.** Um 01:55: *"laut meinen unterlagen heisst das der heutige Montag gute Price action liefern sollte"*. Um 02:28: *"Im Daily Chart ist es am Montag Schwierig"*. Beides steht im Wiki — aber als **Regel und Ausnahme**: `wiki/models/ICT Day Trade Routine.md` sagt, Montag sei normalerweise der schwerste Tag, **Ausnahme: in einer NFP-Woche ist er vergleichsweise einfach zu handeln**. Heute ist NFP-Woche, also greift die Ausnahme. Innerhalb einer halben Stunde ist er von der Ausnahme zurueck auf die Grundregel gefallen. Das ist der teuerste Fehler dieses Eintrags, weil er die Erwartungshaltung fuer den ganzen Tag senkt — und eine gesenkte Erwartung fuehrt dazu, dass man das Setup kleiner handelt oder gar nicht.

2. **Judas Swing — Zeitfenster pruefen.** `wiki/concepts/Judas Swing.md` traegt dazu eine ausdrueckliche Praezisierung: die Judas bildet sich **zwischen 0 und 5 Uhr NY**, und der Manipulationsmove zum **US-Sessionstart ist ein *zweiter* Punkt, aber nicht die Judas im Sinne der Definition**. Er schreibt um 02:28 — meint er das laufende 0–5-Fenster, ist der Begriff korrekt. Meint er den NY-Open (was zu "bis zur NY PM SB abwarten" besser passt), ist es genau die Verwechslung, die auf der Seite schon einmal korrigiert wurde. `vermutet`.

3. **Immer noch keine Invalidierung — jetzt aber praezise machbar.** "Judas Richtung Sellside" braucht eine Zahl, sonst ist jeder Abverkauf im Nachhinein eine Judas:
   - Sweep unter **28.284,00** (NWOG-Low), maximal bis **28.210,25** (NDOG 28.07 c/o), mit **sofortigem Reclaim** = Judas, Bias intakt.
   - Preis bleibt unter 28.284,00 = keine Judas, sondern der NWOG-Bruch, der laut `wiki/concepts/New Week Opening Gap (NWOG) Bias.md` den Bias kippt.

4. **Timing-Konflikt, den er nicht benennt.** `wiki/concepts/ICT Daily Range Session Timing.md`: *"Ein High-Impact-News-Driver um 10 Uhr verlaengert die NY-Killzone bis 11:00/11:30."* Der ISM-PMI um 10:00 treibt also mit hoher Wahrscheinlichkeit die **AM**-Session — er handelt aber erst **14:00–15:00**. Das ist kein Fehler, sondern seine Zeitrestriktion. Es gehoert nur notiert, weil sonst beim Rueckblick nicht zu trennen ist, ob heute **kein Setup da war** oder ob der Move **um 11:00 schon durch war**.

5. **Zwei DOLs, keine Rangfolge.** Weekly-DOL 29.363,50, Daily-DOL 28.725,75–28.763,75. Dazwischen liegt der offene ORG-Rest 28.868,25–29.249,75 mit C.E. 28.984,00 — auf seinem 15m-Chart bereits als rote 0,5-Linie eingezeichnet, im Text aber nicht erwaehnt. Wenn der Buyside-Cluster faellt, ist das der naechste Halt, nicht direkt das Weekly-DOL.

6. **"Bellweather Chart"** hat keine Wiki-Seite. Sein Begriff fuer den 15m als DOL-Finder. Beim dritten Auftreten gehoert er als Konzeptseite angelegt.

---

## Zu pruefen nach Sessionende

| # | Vorhersage | Pruefung |
|---|---|---|
| 1 | Bias **Bullish** | Tages-Close ueber Open 28.567,50? |
| 2 | DOL **28.725,75–28.763,75** erreicht | Tages-High >= 28.725,75? |
| 3 | Drop ins NWOG kam **zuerst** | Tages-Low <= 28.567,50 vor dem High? |
| 4 | Judas zur Sellside mit Reclaim | Low zwischen 28.210,25 und 28.284,00, danach Rueckeroberung? |
| 5 | NWOG haelt | Kein Close unter 28.284,00? |
| 6 | Nur NY PM SB gehandelt | Entry-Zeit im Fenster 14:00–15:00? |
| 7 | War die AM-Session der Tagesmove? | Lag das Tagesextrem vor 11:30? |

### MNQ

**Pre trade**

![[2026-08-03-06.png]]

*02:28 — **4H.** Buyside-Target **28.763,75** rot auf der Preisachse markiert. NWOG-Label jetzt korrekt **NWOG 32**. Darueber die NDOG-Zone 28.708–29.168,75, darunter die NWOG-Fib 0 = 28.258,50 / 0,5 = 28.399,25 / 1 = 28.539,75.*

![[2026-08-03-07.png]]

*02:32 — **15m RTH** — sein 'Bellweather Chart'. Rote 0,5-Linie bei **28.984,00** = C.E. des ORG 23.07; meine Rechnung aus den RTH-Daten ergab 28.983,88, also deckungsgleich. Unten die 30.07-Fib 0 = 27.859,25 bis 1 = 27.300,25.*

![[2026-08-03-daily-markup.png]]

*02:33 — **Daily-Markup** aus dem Bias-Text. Buyside Liquidity 29.363,50 (rot), NDOG 23.07, NWOG-Zone als graues Band bis ca. 10.08.*

**Ende**

---

**Entry**

**Target**

**5min**

**Besonderheiten**

![[2026-08-03-08.png]]

*02:33 — **Daily NQ1! mit COT-12M-Panel.** Aktuell −14,95 K, im gruenen Bereich oberhalb des 12M-EQ (~ −27 K). Panel: 3M SELL · 6M SELL · **12M BUY** · 2Y BUY · 4Y SELL.*

**Reaktion**

**Macro Start**

**Macro Ende**

## Timeline (NY)

- **02:28** — 4H-Markup. Buyside-Target 28.763,75 auf der Achse markiert. NWOG-Label auf dem Chart von 31 auf 32 korrigiert.
- **02:32** — 15m RTH-Chart. ORG-23.07-C.E. als rote 0,5-Linie bei 28.984,00 eingezeichnet. Der 15m ist sein 'Bellweather Chart' zur DOL-Findung.
- **02:33** — Daily + COT-12M-Panel. Bias Bullish, aber Plan: erst Drop ins NWOG, dann Judas Richtung Sellside, danach bullish weiter.

## Fehleranalyse

**Belegt:**

- **S08** — Kein Invalidierungslevel fuer den 'Judas Richtung Sellside'. Ohne Zahl ist jeder Abverkauf im Nachhinein eine Judas. Vorgeschlagen: Sweep 28.284,00 → max. 28.210,25 mit sofortigem Reclaim = Judas; Verbleib darunter = NWOG-Bruch, Bias kippt.

**Zu prüfen:**

- **T03** — 'Judas Swing' ohne Zeitangabe. Wiki: Judas bildet sich 0–5 Uhr NY; der Move zum US-Open ist laut ausdruecklicher Praezisierung auf der Seite ein zweiter Manipulationspunkt, aber nicht die Judas. Welches Fenster ist gemeint?

## Was gut lief

- VII-Einordnung des NWOG ist nach der eigenen Wiki-Definition exakt richtig — Koerperluecke 283,5 P, Wicks ueberlappen. Und die VII ist laut Wiki selbst ein Draw, die Schlussfolgerung traegt.
- 28.763,75 stimmt auf den Tick mit dem Montags-High vom 27.07 (05:45 NY) ueberein.
- Zwei Highs als Target statt einem — Freitag 28.725,75 und Montag 28.763,75, nur 38 P auseinander. Erfuellt den eigenen Checklistenpunkt 'Target Liquiditaet min. 2 H/L'.
- Sequenzierung nachgeliefert (Drop ins NWOG → Judas → bullish), die im Weekly Bias heute morgen noch fehlte — ohne Aufforderung.
- NWOG-Label auf dem Chart von 31 auf 32 korrigiert.
- ORG-23.07-C.E. bei 28.984,00 war bereits eingezeichnet, bevor danach gefragt wurde.
- News-Termine erneut vor Sessionbeginn geprueft und korrekt nach Impact getrennt (red vs. orange).

## Datenlücken

*Nicht bewertbar, weil die Information fehlt — beim nächsten Mal mitloggen.*

- P09: bias_korrekt nach Sessionende setzen. Die 7-Zeilen-Pruefliste oben macht es mit Preisen entscheidbar.
- P09: Bias noch nicht nachgehalten — nach Sessionende eintragen, ob er aufging. Ohne das bleibt die Trefferquote des Bias unbekannt.
- Keine Angabe zur Gefuehlslage.
- 'Bellweather Chart' hat keine Wiki-Seite — beim dritten Auftreten anlegen.
- Keine Rangfolge zwischen Daily-DOL (28.725,75–28.763,75), ORG-Rest (bis 29.249,75) und Weekly-DOL (29.363,50).
- Kein Plan fuer den Fall, dass der Tagesmove in der AM-Session ablaeuft und um 14:00 nichts mehr steht.

## Verwandt

[[Volume Imbalance (VII)]], [[New Week Opening Gap (NWOG) Bias]], [[Judas Swing]], [[Open Float & Liquidity Pools]], [[ORG (Opening Range Gap) & 1st Presented FVG]], [[Equilibrium Vs. Discount]], [[ICT Daily Range Session Timing]], [[NY PM Silver Bullet]]
