---
tags:
  - Weekly-Bias
Bias:
  - Bullish
Date: 2026-08-03
NQ/ES: MNQ
id: 2026-08-03-01
typ: weekly-bias
modus: live
kw: 2026-W32
wochentag: Montag
liquidity_ziel: "Buyside Liquidity 29.363,50 (Daily) — ca. 727 Punkte ueber dem Montag-Open"
pd_arrays: [New Week Opening Gap (NWOG) Bias, BISI & SIBI (Buyside-Sellside Imbalance), IFVG (Inverse Fair Value Gap), Fair Value Gap (FVG), ORG (Opening Range Gap) & 1st Presented FVG, Equilibrium Vs. Discount, Open Float & Liquidity Pools, COT (Commitment of Traders) Data]
---

# 2026-08-03 MNQ Weekly Bias

## Bias

**Bullish** für die Woche

**Seine These (Original in `raw/Weekly Bias KW 31.md`):** bullish, DOL Buyside Liquidity 29.363,50. Begruendung: Premium-Open ueber dem C.E. der Daily Premium Wick Richtung SIBI, enorme Reaktion vom Daily BISI am Donnerstag, grosses offenes NWOG, offenes ORG vom 23.07 unterhalb des DOL, NFP-Woche mit hoher Volatilitaet.

---

## Was gegen die Unterlagen geprueft wurde

**Bestaetigt ✅**

- *"Laut meinen Unterlagen sollte der heutige Montag gute Price Action liefern."* — gedeckt durch `wiki/models/ICT Day Trade Routine.md`: Montag ist normalerweise der schwerste Tag, **Ausnahme: in einer NFP-Woche (News am Freitag) ist der Montag vergleichsweise einfach zu handeln.**
- Der News-Kalender stimmt exakt: Mo 10:00 ISM Manufacturing PMI (red), Fr 08:30 NFP, Unemployment Rate und Average Hourly Earnings (alle red).
- 23.07. war tatsaechlich ein Donnerstag, 30.07. (BISI-Reaktion) tatsaechlich Donnerstag der Vorwoche.
- Bullish oberhalb des NWOG entspricht `wiki/concepts/New Week Opening Gap (NWOG) Bias.md`: oberhalb des NWOG werden praktisch nur Longs gesucht.

**Korrekturen ⚠️**

1. **Wochennummer.** 03.–07.08.2026 ist **ISO-KW 32**, nicht KW 31. KW 31 war 27.07.–02.08. Die Chart-Labels "NWOG 31" sind Datums-Labels (31.07.), analog zu "NDOG 30.07" / "NDOG 23.07" — keine Wochennummern. Ohne Korrektur landet der Freitag-Rueckblick unter der falschen Woche und ist gegen die Vorwoche nicht vergleichbar.

2. **Bullish-Bias und NWOG-Fill widersprechen sich, solange kein Invalidierungslevel steht.** Sein eigenes Wiki: *"Wird das NWOG intraweek durchbrochen → moeglicher major Intraday/Weekly Shift, Bias kippt."* Gleichzeitig will er zusehen, "ob und wann wir versuchen dieses zu fillen". Beides geht nur mit einer Trennlinie:
   - Ruecklauf **in** das NWOG (bis C.E. 28.425,75) = Discount-PD, laut Wiki-Ausnahme sogar der bevorzugte Long-Bereich. Bias bleibt.
   - **Close unter 28.284,00** = NWOG durchbrochen, Bias bullish ist tot. Das ist die Zahl, die im Plan fehlt.

3. **COT-Lesart ist nicht gegen die eigene Methode geprueft.** `wiki/concepts/COT (Commitment of Traders) Data.md` schreibt die 12-Monats-Methode vor: High/Low der letzten 12 Monate, EQ bestimmen, Wert ueber der 0-Linie = bullish, darunter = bearish. Im Screenshot steht die gruene Linie bei **+4.914 und steigt seit Ende Juni**, die rote bei **−14.946 und faellt**. Sind die Commercials die gruene Linie, ist das smart money, das **kauft** — also Rueckenwind fuer den Bullish-Bias, nicht der Gegenwind, als der es notiert wurde. Bis das geklaert ist: `vermutet`, siehe Rueckfrage.

4. **"Smart Money hat verkauft, was absolut zur Price Action der letzten Woche passt."** Nur halb. Die Vorwoche war zweigeteilt: Abverkauf bis 27.208 am 30.07., danach eine der groessten Tageskerzen des Charts nach oben und ein Wochen-Close bei 28.284. Die zweite Haelfte spricht gegen Verteilung.

5. **ORG vs. NDOG.** Er schreibt "IM RTH Chart ist das ORG Donnerstag 23 Juli noch komplett offen". Unter den fuenf Screenshots ist kein RTH-Chart (4H/1H/15m stehen auf ETH), und die genannten Level 29.168,75 / 29.107,50 sind auf seinem eigenen Chart als **NDOG 23.07** beschriftet. ORG (16:15-Close → 09:30-RTH-Open) und NDOG (Globex-Open) sind zwei verschiedene Gaps — die Aussage "liegt unterhalb des DOL" stimmt fuer beide, der Begriff aber nur fuer eins.

6. **Preis-Tippfehler:** NWOG-Open notiert als 28.567,**60**. MNQ tickt in 0,25er-Schritten, .60 existiert nicht — laut Chart 28.567,**50**.

7. **Eigene Regel fehlt im Wochenplan.** `wiki/models/ICT Day Trade Routine.md`: *"NFP Week: an Donnerstag und Freitag der NFP-Woche generell nicht traden — beide Tage meiden."* Der Plan nennt den NFP-Freitag als Volatilitaetstreiber, aber nicht die Konsequenz. Wenn Do/Fr wegfallen, ist die Woche **Montag bis Mittwoch** — und damit ist die Montag-bis-Mittwoch-Range aus `wiki/models/Weekly Range Trading Model.md` das eigentliche Arbeitsgeraet, nicht ein 727-Punkte-DOL bis Freitag.

---

## Pruefliste fuer Freitag (fuer den Wochenrueckblick)

Jede Zeile ist mit einem Preis beantwortbar — genau das fehlte im Altbestand bei 156 Bias-Eintraegen:

| # | Vorhersage | Pruefung |
|---|---|---|
| 1 | Bias **Bullish** | Weekly-Close ueber 28.567,50? |
| 2 | DOL **29.363,50** erreicht | Wochen-High >= 29.363,50? |
| 3 | NDOG 23.07 (29.107,50 / 29.168,75) vorher gefuellt | ja/nein |
| 4 | NWOG bleibt intakt | kein Daily-Close unter 28.284,00? |
| 5 | Weekly High/Low bildet sich Montag (NWOG-Regel) | Wochen-Extrem am 03.08.? |
| 6 | Montag "gute Price Action" (NFP-Woche) | Montag-Range vs. Ø der letzten 4 Montage |
| 7 | Donnerstag als Reversal-Kandidat (NWOG-Regel) | Richtungswechsel am 06.08.? |
| 8 | Do/Fr nicht gehandelt (eigene NFP-Regel) | Trades am 06./07.08. im Journal? |

### MNQ

**Pre trade**

![[2026-08-03-01.png]]

*01:55 — **Weekly** MNQU2026. Open auf dem 0,25er der Premium Wick, NWOG-Baender 28.284,00 / 28.567,50 als graue Zone rechts.*

![[2026-08-03-02.png]]

*02:00 — **Daily.** Rote Linie = DOL Buyside Liquidity 29.363,50. Darunter NDOG 23.07 (29.168,75 / 29.107,50), NWOG 29 bei 29.956,75 / 30.069,00. Donnerstag 30.07. als grosse gruene Kerze aus 27.208 heraus.*

![[2026-08-03-03.png]]

*02:00 — **4H** (ETH). Der Weg zum DOL fuehrt durch die NDOG-Zone 29.107,50–29.168,75 und die graue Range 28.708–29.168.*

![[2026-08-03-04.png]]

*02:01 — **1H.** Preis 28.637, oberhalb NWOG 31 (28.567,50). Fib der NWOG-Range: 0 = 28.258,50, 0.5 = 28.399,25, 1 = 28.539,75.*

![[2026-08-03-05.png]]

*02:01 — **15m.** Sonntag-Open mit Gap ueber das Freitag-Close, seither steigende Struktur ohne Ruecklauf ins NWOG.*

**Ende**

---

**Entry**

**Target**

**5min**

**Besonderheiten**

![[2026-08-03-newskalender.png]]

*02:01 — Wochen-Kalender. Red Folder: Mo 10:00 ISM Manufacturing PMI, Fr 08:30 Average Hourly Earnings + Non-Farm Employment Change (88K erwartet vs. 57K zuvor) + Unemployment Rate 4,2 %. Nicht im Plan erwaehnt: Di 10:00 JOLTS, Mi 08:15 ADP (71K vs. 98K), Mi 10:00 ISM Services PMI, Do 08:30 Unemployment Claims.*

![[2026-08-03-cot.png]]

*02:01 — COTLC auf NQU26 (barchart, 6M). Gruene Linie +4.914 und seit Ende Juni steigend, rote Linie −14.946 und fallend. Die 12-Monats-Methode aus dem Wiki wurde darauf noch nicht angewandt.*

**Reaktion**

**Macro Start**

**Macro Ende**

## Timeline (NY)

- **01:55** — Weekly-Markup (07:55 MESZ). NWOG offen: Freitag-Close 28.284,00 / Sonntag-Open 28.567,50 — 283,5 Punkte breit, C.E. bei 28.425,75. Weekly-Open auf dem 0,25er der Premium Wick.
- **02:00** — Daily: Open ueber dem C.E. der Daily Premium Wick, Richtung hoeherliegendes SIBI. Donnerstag (30.07.) enorme Reaktion vom Daily BISI aus 27.208 heraus — davor viel Liquiditaet absorbiert. Frage fuer heute: wird das alte BISI (zuvor IFVG) zum reclaimed BISI?
- **02:00** — 4H: Buyside Liquidity 29.363 als DOL gesetzt. Darunter offene NDOG 23.07 (29.168,75 / 29.107,50) als Zwischenmagnet.
- **02:01** — 1H + 15m: Preis 28.637, also oberhalb des NWOG-Highs. NDOG 24.07 / 28.07 c/o / 29.07 / 30.07 als weitere offene Gaps eingezeichnet.
- **02:01** — News-Kalender + COT geprueft. Mo 10:00 ISM Manufacturing PMI (red), Fr 08:30 NFP + Unemployment Rate + Average Hourly Earnings (red). COT: leicht abgeschwaecht.

## Fehleranalyse

**Zu prüfen:**

- **S09** — Long-Bias bei einem als Premium erkannten Open, ohne definierten Discount-Einstieg. Der Ruecklauf ins NWOG (C.E. 28.425,75) waere laut Wiki-Ausnahme genau dieser Bereich — steht aber nicht im Plan.
- **S08** — ORG 23.07 genannt, auf dem Chart sind die Level als NDOG 23.07 beschriftet und kein RTH-Chart liegt vor. Begriffe moeglicherweise vermischt.

## Was gut lief

- Wochenanalyse vor Wochenstart fertig — Markup um 01:55 NY, lange vor London.
- Vollstaendige Top-Down-Kaskade Weekly → Daily → 4H → 1H → 15m, alle fuenf dokumentiert.
- News-Kalender vor der Woche geprueft, alle drei Red-Folder-Termine korrekt erfasst (T05 vermieden).
- Konkretes benanntes DOL mit Preis (29.363,50) statt nur einer Richtung (S05 vermieden).
- NWOG, NDOG und ORG aktiv im Markup beruecksichtigt (S08 im Ansatz vermieden).
- Der Montag-Schluss ist wiki-gedeckt und wurde als solcher gekennzeichnet ('laut meinen Unterlagen') statt als Bauchgefuehl.

## Datenlücken

*Nicht bewertbar, weil die Information fehlt — beim nächsten Mal mitloggen.*

- P09: bias_korrekt bleibt bis Freitag leer — die Pruefliste unten macht es diesmal objektiv entscheidbar statt nach Gefuehl.
- P09: Bias noch nicht nachgehalten — nach Sessionende eintragen, ob er aufging. Ohne das bleibt die Trefferquote des Bias unbekannt.
- Kein Invalidierungslevel fuer den Bullish-Bias genannt — vorgeschlagen: Daily-Close unter 28.284,00.
- Kein RTH-Chart unter den Screenshots, obwohl im Text darauf Bezug genommen wird.
- DXY / SMT fehlen, obwohl 'DXY zuerst' Schritt 2 der eigenen ICT Day Trade Routine ist.
- Seasonal Tendency fehlt, obwohl das Wiki COT ausdruecklich mit Seasonals und SMT kombiniert.
- '0,25 der Premium Wick' im Weekly ohne Preisangabe — nicht nachpruefbar.
- Kein Plan fuer Dienstag bis Donnerstag; die Woche ist nur ueber Montag und Freitag gedacht.
- Keine Angabe zur Gefuehlslage beim Erstellen des Bias.

## Verwandt

[[New Week Opening Gap (NWOG) Bias]], [[BISI & SIBI (Buyside-Sellside Imbalance)]], [[IFVG (Inverse Fair Value Gap)]], [[Fair Value Gap (FVG)]], [[ORG (Opening Range Gap) & 1st Presented FVG]], [[Equilibrium Vs. Discount]], [[Open Float & Liquidity Pools]], [[COT (Commitment of Traders) Data]]
