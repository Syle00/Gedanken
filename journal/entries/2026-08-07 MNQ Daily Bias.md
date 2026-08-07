---
tags:
  - Daily-Bias
Bias:
  - Neutral
Date: 2026-08-07
NQ/ES: MNQ
id: 2026-08-07-01
typ: daily-bias
modus: live
kw: 2026-W32
wochentag: Freitag
modell: "kein Trade (NFP-Freitag laut eigener Regel, nur Beobachtung)"
liquidity_ziel: "Kein aktiver Bias. Falls doch: ORG 04.08 (offen, 28.927,25-29.234,25, DOL-Kandidat abwaerts) vs. REH-Cluster 30.062,50-30.094,00 (weiterhin offen aufwaerts, siehe 06.08.-Eintrag)"
pd_arrays: [ORG (Opening Range Gap) & 1st Presented FVG, New Week Opening Gap (NWOG) Bias, IFVG (Inverse Fair Value Gap), BISI & SIBI (Buyside-Sellside Imbalance), TGIF (Thank God its Friday), Fair Value Gap (FVG)]
fehler: []
---

# 2026-08-07 MNQ Daily Bias

## Bias

**Kein Bias** — explizit, wegen NFP. Heute wird nur beobachtet, nicht gehandelt.

**Sein Plan (Original in `raw/journal/Daily Bias 2026-08-07.md`):** Gestern (06.08) über C.E. des
Daily IFVG (16.07) und zusätzlich über C.E. des Daily BISI (04.08) geclosed — genau das wollte er
für weiter bullishe Preise sehen. Das erwartete Retracement kam in London/NY-Premarket. Für heute
kein echter Bias, da NFP-Tag (Red News). TGIF-Retracement unklar, da das Weekly bereits über die
letzten beiden Tage retraced hat. Vorgestern (05.08) wurde das NWOG High KW29 erreicht — knapp,
aber präzise genug als algorithmisches Signal gewertet. Aktuell (Stand 01:00 NY) enge Konsolidierung,
Fokus auf die gestrige Daily Discount Wick (fib Qs/Os). 4H: High des Daily-BISI (04.08) wird
respektiert, bullish. 1H: die ganze Börse wartet auf die News — Frage, ob das ein "2 Drives"-Pattern
ist. Das ORG von gestern (06.08) wurde komplett gefüllt. ORG vom Dienstag (04.08) und vom Donnerstag
30.06 sind offen; das vom Dienstag als möglicher DOL, aber nicht bis zum ORG vom 30.06 — das wäre ein
MSB (Market Structure Break). DXY wurde vernachlässigt.

---

## Nachgerechnet

Datenbasis: `raw/marktdaten/2026/08/` 5m-Serie 03.08.–07.08. (Stand 07.08. 06:20 NY, Tag läuft noch —
London-Session gelaufen, NY AM/Lunch/PM stehen aus). **Wichtig:** die 05.08./06.08.-Dateien waren
beim Ingest noch auf dem Stand von deren jeweiligem Fetch-Zeitpunkt eingefroren (06.08. brach z.B.
bei 02:05 NY ab, obwohl der Tag längst vorbei ist — `write_day()` überschreibt nie bestehende
Dateien). Vor der Prüfung frisch gezogen (`algo/fetch_yfinance.py`, nach Löschen der veralteten
Stand-Dateien für 04.08./05.08./06.08./07.08), sonst wären mehrere der Aussagen unten gegen einen
unvollständigen Handelstag geprüft worden.

**Bestätigt ✅**

- **Close über beiden C.E. — bestätigt.** Handelstag-Close 06.08. (letzte 5m-Kerze 16:55–17:00 NY):
  **29.504,50**. Klar über IFVG-C.E. **29.308,38** und über BISI-C.E. **29.370,25** (beide Zonen aus
  dem 06.08.-Eintrag). Kein Close seit dem 06.08. unter dem IFVG-C.E.
- **Retracement in London/Premarket — bestätigt.** 06.08. London-Range-Low 29.444,25 (04:10),
  London-Lunch-Low 29.437,75 (05:10), Premarket-Low 29.327,50 (09:25), Tagestief **29.241,00** genau
  um 09:30 (RTH-Open) — danach Rally bis 29.686,25 (11:10). Die tiefste Reaktion lag technisch exakt
  auf der Grenze Premarket/RTH-Open, nicht rein "London", aber die Größenordnung und Richtung passen.
- **NWOG KW29 erreicht — bestätigt, Differenz genau beziffert.** NWOG KW29 High = **29.956,75**
  (bereits im 05.08.-Tape-Reading-Eintrag dokumentiert). Tageshoch 05.08. lag bei **29.985,00** (03:04
  NY) — **28,25 Punkte** darüber. "Wenige Punkte Unterschied" trifft es.
- **ORG von gestern (06.08.) komplett gefüllt — bestätigt.** `org_gap()`: Gap **29.335,25 (Open) ↔
  29.572,25 (Vortagesschluss 16:14)**, 237 Punkte, C.E. 29.453,75. Tageshoch 06.08. **29.686,25**
  liegt über dem vollen Gap-Rand 29.572,25 — vollständig gefüllt (nicht nur C.E. erreicht).
- **ORG vom Dienstag (04.08.) weiterhin offen — bestätigt.** `org_gap()`: Gap **28.927,25 (Vortag
  16:14) → 29.234,25 (Open)**, 307 Punkte (Gap up), C.E. **29.080,75**. Seit dem 05.08. nie wieder
  berührt — tiefstes Low seither 29.241,00, liegt 160 Punkte über der C.E. Als abwärtiger DOL-Kandidat
  weiterhin gültig.
- **IFVG-C.E. (29.308,38) gehalten.** Kein 5m-Close seit dem 06.08. darunter; das Tagestief 29.241,00
  war nur ein Docht.
- **Daily-BISI-Zone (28.965,00–29.775,50) nicht verletzt.** Weder Ober- noch Unterkante seit dem
  06.08. berührt (Hoch bislang 29.686,25, Tief 29.241,00) — Preis bewegt sich innerhalb der Zone.

**Korrekturen ⚠️**

1. **"ORG vom Donnerstag 30.06 ist offen" — falsch, seit über fünf Wochen gefüllt.**
   > ⚠️ Nachgerechnet mit `org_gap()` auf sauberer 5m-Basis: ORG 30.06. war **30.020,00 (Vortag
   > 16:14) → 30.047,00 (Open)**, nur 27 Punkte (Gap up), C.E. 30.033,50. Bereits am **darauffolgenden
   > Handelstag 01.07. um 16:00 NY** lief das Tagestief auf 30.009,25 — **unter** dem vollen
   > Gap-Rand 30.020,00. Das ORG ist seit dem 01.07. vollständig gefüllt, nicht offen. (Eine erste
   > Prüfung über die 1h-Cache-Datei zeigte zwar ebenfalls einen Touch am 01.07., das 1h/4h-Cache ist
   > laut `wiki/log.md` [2026-08-04] aber für Fremd-Historie bekannt — deshalb hier zusätzlich gegen
   > die 5m-Serie mit korrekter Handelstag-Zuordnung bestätigt, nicht blind übernommen.) Praktische
   > Folge: seine eigene Sorge ("nicht bis zum ORG vom Donnerstag 30.06 gehen, sonst MSB") bezieht sich
   > auf ein Level, das gar kein offenes Ziel mehr ist — ein MSB in diese Richtung bräuchte einen ganz
   > anderen Auslöser als "unbeantwortetes ORG".
2. **BISI-C.E. wurde am 06.08. intraday kurz unterschritten — nicht auf Daily-Basis, aber knapp.**
   Zwischen 09:05–09:30 NY schlossen fünf 5m-Kerzen unter dem BISI-C.E. 29.370,25 (tiefster Close
   29.334,75 um 09:25). Der im 06.08.-Eintrag definierte Invalidierungslevel ("Close unter C.E.
   29.370,25") war als **Handelstag-Close** gemeint, nicht als Intrabar-Close — auf dieser Basis
   bleibt die bullishe These intakt (Handelstag-Close 29.504,50). Bei einer strengeren, intrabar-
   scharfen Lesart wäre die Regel für ~25 Minuten verletzt gewesen. Festgehalten, weil es zeigt, wie
   knapp die Zone zwischenzeitlich gehalten hat — kein Fehler im Bias, aber ein Beleg dafür, dass die
   Invalidierungsregel als "Daily-Close" präzisiert gehört, nicht implizit gelassen werden sollte.
3. **"4H: High des Daily-BISI respektiert" — Preis hat die Zonen-Oberkante noch nicht erreicht.**
   BISI-Oberkante liegt bei 29.775,50; das bisherige Hoch seit dem 04.08. ist 29.686,25 (06.08.,
   11:10) — rund 89 Punkte darunter. Gemeint ist damit vermutlich, dass die Zone insgesamt (bislang
   ausschließlich von oberhalb bzw. innerhalb) respektiert wird, nicht dass die Oberkante selbst schon
   getestet wurde — als Formulierung aber ungenau.
4. **TGIF-Zweifel ist durch Zahlen gedeckt — die Zielzone ist schon erreicht.** Weekly-Range KW32:
   High **30.073,25** (05.08., 09:45 NY), Low **28.313,00** (03.08., 09:30 NY, Wochenauftakt), Range
   **1.760,25 Punkte**. Die TGIF-Zielzone (20–30 % Retracement vom Hoch) liegt bei **29.545,17–
   29.721,20**. Letzter Preis (07.08., 06:20 NY): **29.603,75** — **liegt bereits innerhalb der
   Zielzone**, ganz ohne dass der Freitag überhaupt begonnen hat. Seine Beobachtung "wir haben das
   Retracement schon über die letzten beiden Tage bekommen" ist damit exakt richtig: die
   20–30-%-Bedingung aus [[TGIF (Thank God its Friday)]] ist bereits erfüllt, bevor die
   Freitag-Zeitkomponente überhaupt greift — ein zusätzliches TGIF-Retracement am Nachmittag wäre
   somit kein neues Signal, sondern höchstens eine Bestätigung der bereits erreichten Zone.

**Offen — nicht nachprüfbar**

- "Warten auf die News, ganze Börse in enger Konsolidierung" (1H) — plausibel angesichts der London-
  Lunch-Range (99,75 Punkte, deutlich unter dem NY-AM-Vortagsniveau), aber ohne definierte Schwelle
  nicht objektiv zu bestätigen oder zu widerlegen.
- **"2 Drives Pattern?"** — offene Frage im Original, keine Wiki-Seite zu diesem Begriff vorhanden.
  Nicht aus den vorliegenden Daten beantwortbar, ohne die exakte Chart-Struktur zu kennen, auf die er
  sich bezieht. Für eine spätere Seite vormerken, falls der Begriff wieder auftaucht (Konvention:
  beim dritten Auftreten anlegen).
- DXY/SMT — vom Nutzer selbst als vernachlässigt benannt, keine eigene Prüfung nachgeliefert (bereits
  als wiederkehrende Lücke in `wiki/index.md` und mehreren Vorgänger-Einträgen vermerkt).

---

## Timeline (NY)

- **06.08., 16:55–17:00** — Handelstag-Close 29.504,50, über beiden relevanten C.E.-Levels.
- **07.08., 00:15** — Sellside-Sweep 29.476,00 (Level seit 22:40 offen), sofort zurückerobert.
- **07.08., 04:00** — MSS bullish über 29.591,50, anschließend Rally bis Tageshoch 29.650,50 (05:25).
- **07.08., 05:55** — MSS bearish über 29.621,00, London-Lunch-Konsolidierung ab da (53 Punkte Range).
- Datenstand zum Zeitpunkt dieses Eintrags: **06:20 NY** — NY AM, Lunch und PM (inkl. NFP 08:30 NY)
  stehen noch aus, `bias_korrekt` bleibt bis zum Nachtrag offen.

## Was gut lief

- No-Trading-Regel um NFP konsequent benannt, ohne durch die eigene Bullish-Neigung zum Handeln
  verleitet zu werden.
- Konkrete, benannte PD-Arrays statt reiner Richtungs-Vibes: IFVG-C.E., BISI-C.E., NWOG KW29, zwei
  offene ORGs — alle mit Zahl im Kopf, nicht nur "irgendwo drüber/drunter".
- Offene Selbstzweifel (TGIF-Frage, DXY-Vernachlässigung, "2 Drives?"-Frage) explizit benannt statt
  eine falsche Sicherheit vorzutäuschen — genau die Fragen, die sich hier auch am ehesten nachrechnen
  ließen.

## Datenlücken

*Nicht bewertbar, weil die Information fehlt oder der Tag noch läuft.*

- Tag ist zum Zeitpunkt dieses Eintrags erst bis 06:20 NY (London-Ende) mit Daten hinterlegt — NY AM/
  Lunch/PM und `bias_korrekt` erst im Nachtrag bewertbar (Muster wie 08.03./08.06.).
- Kein Screenshot zu diesem Eintrag (reine Text-Notiz).
- "Weekly bereits zweimal retraced" — auf welche zwei Tage sich das genau bezieht, bleibt im Original
  unklar; die Weekly-Range-Rechnung oben deckt die Beobachtung im Ergebnis, nicht im Detail.

## Verwandt

[[ORG (Opening Range Gap) & 1st Presented FVG]], [[New Week Opening Gap (NWOG) Bias]], [[IFVG (Inverse Fair Value Gap)]], [[BISI & SIBI (Buyside-Sellside Imbalance)]], [[TGIF (Thank God its Friday)]], [[Fair Value Gap (FVG)]]
