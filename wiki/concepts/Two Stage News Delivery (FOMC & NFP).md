---
tags: [concept, ict, trading-ict, macro, news-driven, hypothesis]
created: 2026-08-07
updated: 2026-08-10
sources: ["[[FOMC (Federal Open Market Committee)]]", "raw/journal/Daily Bias 2026-08-07.md", "raw/marktdaten/2026/08/07.08.2026/MNQ 2026-08-07 1m.csv", "[[2026-08-07 - Case Study With NonFarm Payroll & NQ Futures (Source)|Case Study With NonFarm Payroll & NQ Futures (Source)]]", "[[ICT Gems - Non-Farm Payroll Profile + Macros (Source)]]"]
---

# Two Stage News Delivery (FOMC & NFP)

> ⚠️ **Offene Hypothese, n=1.** Noch nicht über mehrere Events verifiziert — bei jedem künftigen
> FOMC- und NFP-Termin gegenprüfen und diese Seite nachführen (siehe [[Algo: proaktiv
> gegenprüfen]] in `wiki/log.md`-Konvention).

Beobachtung des Nutzers: der große Newsdriver liefert Preis nicht in einem Zug, sondern in
**zwei zeitlich getrennten Stages**, die in entgegengesetzte Richtungen laufen können — die
erste unmittelbar an der News, die zweite deutlich später (in etwa im Fenster der
[[Silver Bullet Model|NY-AM-Silver-Bullet]]-/[[NY Lunch Macro Model|Lunch-Macro]]-Session).
Bislang war das nur als fehlende Quelle bekannt: **Lektion 02 der [[MentorShip 2025]]-Reihe**
heißt *"Trading FOMC Two Stage Delivery"*, liegt aber nicht in `raw/`. Diese Seite trägt die
erste live beobachtete, datengeprüfte Instanz des Musters — für FOMC noch unbelegt, aber am
07.08.2026 explizit an einem **NFP**-Termin beobachtet, was nahelegt, dass es kein
FOMC-exklusives Muster ist, sondern generell für High-Impact-Red-News gilt.

## Beobachtete Instanz: NFP 2026-08-07 (MNQ)

Gegen die 1-Minuten-Daten aus `raw/marktdaten/2026/08/07.08.2026/MNQ 2026-08-07 1m.csv` geprüft:

| Zeit (NY) | Preis | Ereignis |
|---|---|---|
| ~04:00–08:00 | Range 29.596–29.612 | Pre-Market-Sellside-Pool bildet sich (mehrfach getestete Tiefs) |
| **08:29** (unmittelbar vor dem 8:30-Print) | Low **29.596,00** | Sellside-Sweep der Pre-Market-Range — erster Griff der News |
| **08:30–08:49** | High **29.854,50** | **Stage 1**: massive Buyside-Expansion, +258 Punkte in 19 Minuten |
| 09:40–10:11 | Preis dreht, fällt zurück Richtung 29.640 | Übergang / Aufbau zu Stage 2 |
| **10:12** | Low **29.564,25** | **Stage 2**: zweiter, deutlich tieferer Sellside-Sweep — unterbietet sogar das Stage-1-Tief |
| ab ~10:20 | Erholung Richtung 29.720–29.750 | Stage 2 endet, Range beruhigt sich |

⚠️ Der Nutzer notierte den Pre-Market-Tiefpunkt als „5:53 Low 29.600,50" — die CSV-Daten zeigen
diesen Preisbereich (29.600,5 exakt getroffen um 04:05, danach mehrfach zwischen 29.599–29.612
zwischen 04:00 und 08:00 retestet), aber nicht exakt um 05:53. Zeit/Preis dürften vom
Charting-Feed des Nutzers stammen und minimal von diesem Datensatz abweichen — die
**strukturelle Aussage (Pre-Market-Tief als Sellside-Pool, an der News gesweept) ist bestätigt**,
nur der exakte Zeitstempel nicht 1:1 reproduzierbar.

## Generalisiertes Muster (Arbeitshypothese)

1. **Vor der News** baut sich ein erkennbarer Liquidity Pool auf (hier: Pre-Market-Low als
   [[External vs. Internal Range Liquidity|External Range Liquidity]]).
2. **Stage 1 — an der News selbst** (8:30 bei NFP, 14:00 bei FOMC): Sweep der naheliegenden
   Pool-Seite, dann scharfe Umkehr und Expansion in die Gegenrichtung. Läuft wie ein
   verschärfter [[Judas Swing]] / [[Market Protraction]]-Ausschlag, nur größenordnungsmäßig
   stärker als die üblichen getakteten Fensters.
3. **Pause/Konsolidierung** in den ~45–60 Minuten danach.
4. **Stage 2 — zeitlich versetzt** (hier ~1h42min nach der News, im Fenster von
   [[NY Lunch Macro Model|10-Uhr-Linie]]/Silver-Bullet-NY-AM): zweite, oft stärkere Bewegung in
   die **Gegenrichtung von Stage 1**, die das Stage-1-Extrem unterbietet/überbietet. Das ist die
   eigentliche „Two Stage Delivery" — zwei getrennte algorithmische Lieferungen, keine einzelne
   News-Reaktion.

## Warum das relevant ist

Falls sich das Muster bestätigt, heißt das für [[FOMC (Federal Open Market Committee)]]- und
NFP-Tage: **die unmittelbare News-Reaktion (Stage 1) ist nicht zwangsläufig die Tagesrichtung.**
Das deckt sich mit der bestehenden Linie in [[Low Resistance Liquidity Run]] (FOMC-Wochen =
High-Resistance/Chop-Kandidat) und mit der bereits im Journal notierten Vorsicht, an NFP-Tagen
keinen belastbaren Daily Bias zu halten (siehe `raw/journal/Daily Bias 2026-08-07.md`).

## Primärquellenbestätigung (ICT selbst, 2026-08-07)

Dieselbe NFP-Instanz wurde von ICT im selben Video live nacherzählt (siehe
[[2026-08-07 - Case Study With NonFarm Payroll & NQ Futures (Source)|Case Study With NonFarm Payroll
& NQ Futures (Source)]], nicht als eigene 2. Instanz zu zählen — es ist derselbe Handelstag, nur aus
Primärquellen-statt Rohdatensicht):

- ICT bestätigt exakt den hier dokumentierten Ablauf: Stage-1-Rallye vom 8:30-Print bis in die
  Macro-Zeit (8:50–9:10), danach ein Reversal, das er selbst zum Teilgewinn-Mitnehmen einer Long-
  Position nutzt.
- Er benennt den Mechanismus explizit als **"two-stage delivery like FOMC"** und beschreibt NFP damit
  aus eigener Wahrnehmung als generell zweistufig — deckt sich mit der oben unter "Generalisiertes
  Muster" formulierten Arbeitshypothese, jetzt zusätzlich durch die Primärquelle (statt nur eigene
  Datenanalyse) gestützt.
- Der Reversal-Punkt wird von ICT über eine **Standard-Deviation-Projektion der Pre-Market-Range**
  (7:00–8:30) antizipiert, nicht nur über die Uhrzeit allein — siehe
  [[Central Bank Dealers Range (CBDR)]] für dieselbe Projektionstechnik.

## Nächste Schritte

- Bei jedem künftigen NFP (1. Freitag im Monat) und FOMC-Termin dieselbe Zwei-Stufen-Prüfung
  fahren und hier eintragen (Datum, Stage-1-/Stage-2-Zeiten, Preise, Richtung).
- Sobald ≥3 Instanzen vorliegen: Kandidat für ein `algo/backtest_*.py`-Skript, das NFP-/FOMC-Termine
  gegen `raw/marktdaten/` automatisiert auf dieses Zwei-Stufen-Muster prüft (Datumsliste der
  Termine fehlt aktuell noch im Repo).
- Bei Gelegenheit prüfen, ob Lektion 02 der MentorShip-2025-Reihe („Trading FOMC Two Stage
  Delivery") doch noch als Notion-Export auftaucht — würde diese Hypothese direkt mit
  Primärquelle unterlegen.

## Das NFP-Profil in ICTs eigener Formulierung (2023)

Aus [[ICT Gems - Non-Farm Payroll Profile + Macros (Source)]] — die Regel, die das oben
beschriebene Zwei-Stufen-Muster für NFP auf einen Satz bringt:

> **Die Seite, auf die Preis beim 8:30-Print *zuerst* läuft, ist in der Regel der False Run.**
> *"Whatever side of the marketplace it goes for first as 8:30 news hits — usually, not always —
> that will be the false run."*

Die vollständige Sequenz, die ICT im Beispiel durchzählt:

1. Rally in die **Buyside** → Trader werden **long getrappt**, Shorts ausgestoppt.
2. Abverkauf **unter** die Relative Equal Lows → die frisch eingestiegenen Longs werden
   ausgestoppt, neue Shorts induziert.
3. Diese Shorts sitzen jetzt falsch → der Markt ist **frei**, in die eigentliche Richtung zu
   laufen (hier: Buyside und das übergeordnete Draw on Liquidity).

Spiegelbildlich möglich (erst Sellside, dann Buyside), oder — ausdrücklich genannt — schlicht *"a
choppy mess that non-farm payroll can many times be"*.

**Warum Preis danach frei ist**: *"no one's long, they got stopped out; anyone buying the breakout
was raked across the coals; anyone short below those relative equal lows is trapped — then the
market can go higher."*

### Breaker Blocks taugen an diesen Tagen weniger

Eigene Einschränkung von ICT: **NFP, CPI und FOMC** sind genau die Ereignisse, an denen
[[Breaker Block|Breakers]] *"not the cleanest points of rejection"* liefern. Wo er sonst
High–Low–Higher-High als Breaker lesen würde, liest er die Zone an solchen Tagen eher als
[[Balanced Price Range (BPR)]].

### Zusammenspiel mit den Macro-Fenstern

Im Beispiel läuft die Sequenz durch die Macros hindurch: **9:50–10:10** liefert die Balancierung
der Ineffizienz und danach die Protraction nach unten in die engineerte Sellside; der eigentliche
Lauf fällt in das **Silver-Bullet-Fenster 10:00–11:00**; **10:50–11:10** leitet in die
NY-Lunch-Phase über. Siehe [[ICT Macros & Leading Candles]].

## Verwandt

- [[FOMC (Federal Open Market Committee)]]
- [[MentorShip 2025]] — Lektion 02, die namensgebende fehlende Quelle
- [[Market Protraction]], [[Judas Swing]] — verwandte getaktete Manipulationsfenster
- [[Silver Bullet Model]], [[NY Lunch Macro Model]] — das Stage-2-Zeitfenster
- [[External vs. Internal Range Liquidity]] — der Pre-Market-Pool als External Liquidity
- [[Low Resistance Liquidity Run]] — FOMC/NFP als Chop-Kandidat
- [[2026-08-07 - Case Study With NonFarm Payroll & NQ Futures (Source)|Case Study With NonFarm Payroll & NQ Futures (Source)]] — Primärquellenbestätigung
- [[ICT Macros & Leading Candles]], [[Central Bank Dealers Range (CBDR)]]
