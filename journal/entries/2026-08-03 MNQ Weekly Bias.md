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

3. **COT ✅ — geklaert, und er lag richtig.** *(Zweifach nachgetragen am 2026-08-03. Erst sein Hinweis: rot = Commercials, gruen = Large Speculators — mein Verdacht, er habe die Linien vertauscht, war falsch. Dann sein 12-Monats-Chart `raw/COT 12 monate.PNG`, der auch meine zweite Aussage widerlegt.)*

   Commercials stehen bei **−14,95 K und fallen**, Large Specs bei **+4,91 K und steigen** — Smart Money hat also verkauft, genau wie er schreibt. Ich hatte daraus **bearish** abgeleitet, weil der Wert unter null liegt. Das war falsch: massgeblich ist das **EQ der 12-Monats-Range**, nicht die Null. Sein Indikator zieht diese Linie bei rund **−27 K** (12M-High ≈ +15 K, 12M-Low ≈ −68 K). **−14,95 K liegt darueber, im gruenen Bereich** — der Indikator gibt fuer 12 Monate ausdruecklich **BUY** aus. Der COT stuetzt seinen Bullish-Bias also, statt ihm zu widersprechen. `wiki/concepts/COT (Commitment of Traders) Data.md` ist entsprechend praezisiert worden; die Seite war an dieser Stelle selbst unscharf (Punkt 1 nennt das EQ, Punkt 2 die 0-Linie).

   **Was bleibt:** die Horizonte widersprechen sich. Sein Indikator gibt gleichzeitig aus —
   **3M SELL · 6M SELL · 12M BUY · 2Y BUY · 4Y SELL**. Sein "etwas abgeschwaecht, Smart Money hat verkauft" beschreibt korrekt die **kurzen** Horizonte, der Bullish-Bias steht auf dem **12-Monats**-Horizont. Beides stimmt. Fuer einen **Wochen**-Bias liegen 3M/6M naeher am Zeithorizont des Trades als 12M — das ist die eigentliche offene Frage, nicht "bullish oder bearish".

4. **"...was absolut zur Price Action der letzten Woche passt."** Nur zur ersten Haelfte. Die Vorwoche war zweigeteilt: Abverkauf bis 27.208 am 30.07. — dazu passt der Commercial-Verkauf — danach eine der groessten Tageskerzen des Charts nach oben und Wochen-Close bei 28.284. Commercials, die in diese Rally hinein weiter short gehen, sind kein Beleg fuer die Aufwaertsbewegung, sondern das Gegenteil. Der Satz liest sich wie Bestaetigung, ist aber Widerspruch — siehe Punkt 3.

5. **ORG 23.07 — nachgerechnet.** *(Nachtrag 2026-08-03: er hat die RTH-Daten geliefert, `raw/marktdaten/31.07.2026/MNQ 2026-07-31 15m RTH.csv`, 15m RTH 14.07.–31.07. Mein Verdacht, er habe ORG und NDOG verwechselt, faellt damit weg — das ORG existiert, er hatte den RTH-Chart offen.)*

   Gerechnet nach der Wiki-Definition (letzter RTH-Close des Vortages → 09:30-Open):

   | | Wert |
   |---|---|
   | ORG 23.07 (Do) | **29.249,75 → 28.718,00**, Gap **down**, 531,75 Punkte |
   | C.E. | **28.983,88** — bis heute **nicht** erreicht |
   | bereits abgearbeitet | **150,25 P** von unten, bis **28.868,25** (28 % des Gaps) |
   | offener Rest | **28.868,25 – 29.249,75** |

   **Korrektur:** "noch komplett offen" stimmt nicht — 28 % sind zu. Sein struktureller Punkt haelt aber: der offene Rest endet bei 29.249,75 und liegt damit **unterhalb des DOL 29.363,50** ✅. Der Weg zum DOL fuehrt durch den ORG-Rest, dann durch die NDOG-Level 29.107,50 / 29.168,75, die **innerhalb** dieser ORG-Zone liegen. Beide Gaps existieren, sie ueberlappen sich nur.

   > ⚠️ Caveat aus dem eigenen Wiki: `ORG (Opening Range Gap) & 1st Presented FVG` fuehrt fuer Gaps von **"mehreren 100 Punkten"** die Erwartung, dass der Preis **nicht** ins Gap zurueckkehrt, sondern in Gap-Richtung weiterlaeuft. 531,75 Punkte fallen klar in diese Klasse. Ein solches ORG als Aufwaerts-Magnet zu benutzen, laeuft der Tabelle entgegen — moeglicherweise zu Recht, aber es gehoert begruendet.

   **Nicht erwaehnt, aber relevant:** das **ORG 30.07 (Do) 27.299,25 → 27.876,75** (577,50 P, gap up) ist in den Daten das einzige **voellig unberuehrte** ORG des Zeitraums — ein offener Magnet **unterhalb** des Preises. Als Downside-Ziel taucht es im Wochenplan nicht auf.

6. **Entry-Ebene ✅ geklaert, kein Fehler.** *(Nachtrag 2026-08-03.)* Der Einwand "Long-Bias aus dem Premium ohne definierten Discount-Einstieg" (S09) ist erledigt: er ist **Scalper** und arbeitet im Minuten-/Sekunden-Chart. Der Weekly Bias ist bei ihm ein **Richtungsrahmen**, kein Entry-Plan — ein Entry ist zum Zeitpunkt der Analyse gar nicht bestimmbar. Das ist eine bewusste, begruendete Arbeitsweise und keine Abweichung. Heute (Mo 03.08.) handelt er ausschliesslich die **NY PM Silver Bullet, 14:00–15:00 NY** (`wiki/models/NY PM Trend.md`: PM-Session 13–16 Uhr, PM Opening Range 13:30–14:00, SB ab 14:00). Fuer die Fehlerpruefung heisst das: Premium/Discount ist auf **Trade-Ebene** zu pruefen, nicht am Wochenbias.

7. **Preis-Tippfehler:** NWOG-Open notiert als 28.567,**60**. MNQ tickt in 0,25er-Schritten, .60 existiert nicht — laut Chart 28.567,**50**.

8. **Eigene Regel fehlt im Wochenplan.** `wiki/models/ICT Day Trade Routine.md`: *"NFP Week: an Donnerstag und Freitag der NFP-Woche generell nicht traden — beide Tage meiden."* Der Plan nennt den NFP-Freitag als Volatilitaetstreiber, aber nicht die Konsequenz. Wenn Do/Fr wegfallen, ist die Woche **Montag bis Mittwoch** — und damit ist die Montag-bis-Mittwoch-Range aus `wiki/models/Weekly Range Trading Model.md` das eigentliche Arbeitsgeraet, nicht ein 727-Punkte-DOL bis Freitag.

---

## Pruefliste fuer Freitag (fuer den Wochenrueckblick)

Jede Zeile ist mit einem Preis beantwortbar — genau das fehlte im Altbestand bei 156 Bias-Eintraegen:

| # | Vorhersage | Pruefung | Stand 2026-08-04 (Di, vor RTH-Open — Woche laeuft noch) |
|---|---|---|---|
| 1 | Bias **Bullish** | Weekly-Close ueber 28.567,50? | Zwischenstand: letzter Preis 29.045,50 (04.08. 01:50 NY) — **darueber**, noch kein Wochenschluss |
| 2 | DOL **29.363,50** erreicht | Wochen-High >= 29.363,50? | Noch nicht — Wochen-High bislang 29.074,75 (04.08. 01:35 NY), 288,75 P entfernt |
| 3 | NDOG 23.07 (29.107,50 / 29.168,75) vorher gefuellt | ja/nein | Noch nicht — Hoch bislang 29.074,75 liegt knapp darunter |
| 4 | NWOG bleibt intakt | kein Daily-Close unter 28.284,00? | ✅ bisher intakt — Montag-Close 28.929,25 |
| 5 | Weekly High/Low bildet sich Montag (NWOG-Regel) | Wochen-Extrem am 03.08.? | ⚠️ **Bisher widerlegt fuer das High:** Wochen-Low kam Montag 09:30 (28.313,00), das Wochen-High bislang aber erst Dienstagfrueh 01:35 (29.074,75) — noch nicht final, da die Woche laeuft |
| 6 | Montag "gute Price Action" (NFP-Woche) | Montag-Range vs. Ø der letzten 4 Montage | Montag-Range 652,0 P vs. Ø der 4 Vor-Montage 690,5 P (795,0 / 656,0 / 485,75 / 825,25) — **im Rahmen**, nicht auffaellig ueber- oder unterdurchschnittlich |
| 7 | Donnerstag als Reversal-Kandidat (NWOG-Regel) | Richtungswechsel am 06.08.? | offen — Donnerstag steht noch aus |
| 8 | Do/Fr nicht gehandelt (eigene NFP-Regel) | Trades am 06./07.08. im Journal? | offen |
| 9 | **COT-Horizonte:** 12M sagt BUY, 3M/6M sagen SELL | Welcher Lookback trug die Woche — Wochen-Close ueber oder unter dem Montag-Open 28.567,50? | offen, tendenziell 12M (Preis bisher klar ueber 28.567,50) |
| 10 | ORG 23.07: offener Rest **28.868,25 – 29.249,75** | Wochen-High >= 28.868,25 / C.E. 28.983,88 / 29.249,75? | ✅ 28.868,25 und C.E. 28.983,88 bereits ueberschritten (High 29.074,75); Zonen-Obergrenze 29.249,75 noch nicht erreicht |
| 11 | ORG 30.07 **27.299,25 – 27.876,75** (unberuehrt) | Wochen-Low <= 27.876,75? | ✅ weiterhin unberuehrt — Wochen-Low 28.313,00 liegt weit darueber |
| 12 | Nur NY PM Silver Bullet gehandelt (14:00–15:00 NY) | Entry-Zeiten der Trades dieser Woche | offen |

**Noch kein `bias_korrekt`** — die Woche ist erst Dienstagfrueh vor RTH-Open, Punkte 7/8/9/12 brauchen Donnerstag/Freitag. Auffaelligster Zwischenbefund: Punkt 5 (Weekly-Extrem bildet sich am Montag) haelt bislang nur fuer das Low, nicht fuer das High — der eigentliche Hochpunkt lief bis in die Dienstagfrueh-Session weiter.

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

*02:01 — COTLC auf NQU26 (barchart, 6M). **Rot = Commercials −14.946 und fallend, Gruen = Large Speculators +4.914 und steigend** (von ihm bestaetigt). Auf 6 Monaten allein nicht entscheidbar — siehe naechstes Bild.*

![[2026-08-03-cot-12m.png]]

*Nachgereicht — COT-12-Monats-Indikator auf NQ (Aug 2025 – Aug 2026). Die Trennlinie gruen/rot liegt bei rund **−27 K** = EQ aus 12M-High ≈ +15 K und 12M-Low ≈ −68 K, **nicht** bei null. Aktuell **−14,95 K**, also im gruenen Bereich. Panel oben rechts: 3M **SELL** · 6M **SELL** · 12M **BUY** · 2Y **BUY** · 4Y **SELL**. Der 12-Monats-Horizont — der, den das Wiki vorschreibt — stuetzt den Bullish-Bias.*

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

- ~~**S09**~~ — **verworfen 2026-08-03.** Er ist Scalper; der Weekly Bias ist Richtungsrahmen, kein Entry-Plan. Premium/Discount gehoert auf Trade-Ebene geprueft. Siehe Korrektur 6.
- ~~**S08**~~ — **verworfen 2026-08-03.** RTH-Daten nachgeliefert, das ORG 23.07 existiert und ist korrekt benannt. Sachlich falsch war nur "komplett offen" (28 % sind zu). Siehe Korrektur 5.

## Was gut lief

- Wochenanalyse vor Wochenstart fertig — Markup um 01:55 NY, lange vor London.
- Vollstaendige Top-Down-Kaskade Weekly → Daily → 4H → 1H → 15m, alle fuenf dokumentiert.
- News-Kalender vor der Woche geprueft, alle drei Red-Folder-Termine korrekt erfasst (T05 vermieden).
- Konkretes benanntes DOL mit Preis (29.363,50) statt nur einer Richtung (S05 vermieden).
- NWOG, NDOG und ORG aktiv im Markup beruecksichtigt (S08 im Ansatz vermieden).
- Der Montag-Schluss ist wiki-gedeckt und wurde als solcher gekennzeichnet ('laut meinen Unterlagen') statt als Bauchgefuehl.

## Datenlücken

*Nicht bewertbar, weil die Information fehlt — beim nächsten Mal mitloggen.*

- P09: bias_korrekt bleibt bis Freitag leer — die Pruefliste unten macht es diesmal objektiv entscheidbar statt nach Gefuehl. **Zwischenstand 2026-08-04 in der Pruefliste ergaenzt** (Punkte 1/2/3/4/6/10/11 bereits mit Marktdaten beantwortbar, 5/7/8/9/12 erst nach Do/Fr).
- P09: Bias noch nicht nachgehalten — nach Sessionende eintragen, ob er aufging. Ohne das bleibt die Trefferquote des Bias unbekannt.
- Kein Invalidierungslevel fuer den Bullish-Bias genannt — vorgeschlagen: Daily-Close unter 28.284,00.
- Kein RTH-Chart unter den Screenshots, obwohl im Text darauf Bezug genommen wird.
- DXY / SMT fehlen, obwohl 'DXY zuerst' Schritt 2 der eigenen ICT Day Trade Routine ist.
- Seasonal Tendency fehlt, obwohl das Wiki COT ausdruecklich mit Seasonals und SMT kombiniert.
- ~~COT-Screenshot zeigt nur 6 Monate~~ — **geschlossen 2026-08-03**, 12-Monats-Ansicht nachgeliefert (`raw/COT 12 monate.PNG`): 12M **BUY**, aber 3M/6M **SELL**. Offen bleibt, welcher Horizont fuer einen Wochenbias massgeblich ist.
- ~~Kein RTH-Chart~~ — **geschlossen 2026-08-03**, RTH-15m-Daten nachgeliefert und ausgewertet.
- Der ORG-Rest 28.868,25–29.249,75 ist im Markup nicht als eigenes Level eingezeichnet, nur als "ORG offen" im Text.
- '0,25 der Premium Wick' im Weekly ohne Preisangabe — nicht nachpruefbar.
- Kein Plan fuer Dienstag bis Donnerstag; die Woche ist nur ueber Montag und Freitag gedacht.
- Keine Angabe zur Gefuehlslage beim Erstellen des Bias.

## Verwandt

[[New Week Opening Gap (NWOG) Bias]], [[BISI & SIBI (Buyside-Sellside Imbalance)]], [[IFVG (Inverse Fair Value Gap)]], [[Fair Value Gap (FVG)]], [[ORG (Opening Range Gap) & 1st Presented FVG]], [[Equilibrium Vs. Discount]], [[Open Float & Liquidity Pools]], [[COT (Commitment of Traders) Data]]
