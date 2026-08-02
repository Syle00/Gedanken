---
tags: [concept, ict, trading-ict, sessions]
created: 2026-08-01
updated: 2026-08-02
sources: ["[[Essentials To ICT Daytrading (Source)]]", "[[Defining The Daily Range (Source)]]", "[[Kurz Notizen (Source)]]", "[[Trading Premarket and Regular Session Liquidity (Source)]]", "[[ICT 2022 - Episode 11 Important Dealing Range (Source)]]", "[[ICT 2022 - Episode 17 FX Anwendung (Source)]]", "[[ICT 2022 - Episode 05 Intraday Orderflow & Swing H-L 8.30-13.30 (Source)]]"]
---

# ICT Daily Range Session Timing

Ablauf der Sessions, die zusammen die Daily Range formen. Ergänzt die Timeframe-Hierarchie
(Monthly → Weekly → Daily, wobei der Daily Chart fürs Daytrading am wichtigsten ist).

> **Killzone ≠ Session.** Die handelbaren Eröffnungsfenster mit ihren Pip-Erwartungen stehen auf
> [[ICT Killzones]] (London 2–5, NY 7–9, London Close 10–12, Asia ab 19/20 Uhr NY). Diese Seite
> beschreibt die *Sessions*, die jeweils deutlich länger laufen: Asia reicht über Mitternacht hinaus,
> London bis 7 Uhr, NY bis 14 Uhr.

## Erwartungsanker: 5-Tage-Range

Die Range der letzten 5 Handelstage ist der Referenzwert — es wird eine Daily Candle ähnlicher
Größe erwartet.

![[image 227.png]]
*Die Range der letzten 5 Handelstage als Erwartungsanker für die kommende Daily Candle.*

## Session-Ablauf

| Session | Zeitfenster | Bedeutung |
|---|---|---|
| London | 1–5 Uhr | Bildet oft High/Low des Tages |
| NY AM | nach London | Wird nur vermieden, wenn London bereits 80% der Daily Range gebildet hat (selten) |
| London Close | 10–12 | Praktisch nicht relevant als Trendsession — als **Ende der Tagesmanipulation** aber sehr wohl, siehe [[ICT Killzones]] |
| NY PM / Close | 2–3 Uhr | Ab 3 Uhr schließen die Bond-Märkte (Silver-Bullet-Fenster); danach ist Daily Range meist fertig, Retracement erwartet |
| Asia Open | 8 Uhr | Yen/AUD/NZD bilden oft High/Low des Tages, analog zu London |
| London Lunch | 5–7 Uhr | Ruhiger Markt, Retracement/Konsolidierung als Vorbereitung auf NY |

*(Zeitangaben wie in der Rohquelle übernommen, keine Zeitzone explizit angegeben — beim nächsten
Ingest verwandter Quellen prüfen und ggf. präzisieren.)*

![[image 229.png]]
*Sessionabfolge London → NY AM → NY PM/Close → Asia Open → London Lunch, die zusammen die Daily Range formt.*

## Präzise Session-Fenster (NY Standard Time)

Aus `Defining The Daily Range` — feinere Session-Grenzen als oben, gleiche Struktur:

| Session | Fenster (NY Zeit) |
|---|---|
| Asian Range | 20–24 Uhr |
| London Range | 1–5 Uhr |
| NY AM | 7–10 Uhr |
| London Close | 10–12 Uhr (nicht mehr wirklich relevant) |
| **IPDA True Range** | **0–15 Uhr** — die "wahre" 24h-Interbank-Handelstag-Range |

![[image 246.png]]
*Die IPDA True Range geht von 12am – 15 Uhr NY Standard Time — die wahre 24h-Range des
Interbank-Handels.*

- Um 3 Uhr (15 Uhr NY) schließen die Bond-Märkte — starker Einfluss auf Währungen über die
  Interest Rate; FOMC-Meetings liegen meist ebenfalls um diese Zeit.
- Wenn ICT von "NY Close" spricht, meint er den **3pm IPDA True Day Close**, nicht den
  Handelsschluss der Börse.

## RTH vs. PM High/Low & Manipulationsfenster (Kurz Notizen)

- Das **RTH-High/-Low** bildet sich in der **NY-AM-Session**; die Wahrscheinlichkeit, dass sich dort
  auch das Tages-High/-Low bildet, ist nicht gering — dennoch bleibt London die bevorzugte Session
  dafür.
- Die **NY-PM-Session** bildet dagegen fast immer das Low bzw. High des Tages (RTH, oft auch ETH) —
  darüber lässt sich der Tag zuverlässiger framen, als nur auf London zu spekulieren.
- Die eigentliche **Manipulation des Tages** findet zwischen **0–5 Uhr NY** statt — meist bildet sich
  dabei in London (teils auch in Tokio) das Low/High des Tages.
- Die **Asia Range (19–24 Uhr)** soll konsolidieren — dadurch steigt die Wahrscheinlichkeit für einen
  anschließend großen, klaren Bull-/Bear-Move.

## Welcher Opening Price gilt wann (MentorShip 2022)

ICT nutzt **zwei** Opening-Preise als **Manipulations-Indikator**:

| Preis | Gilt für |
|---|---|
| **0:00 Midnight** | die **gesamte Daily Session** — und für London |
| **8:30** | **ausschließlich die NY-AM/Morning-Session** |

- Faustregel: *„generell 8:30 für NY, 0 Uhr für London — aber auch in NY schauen wir auf 0 Uhr."*
- **Öffnen beide unterschiedlich**, gilt für **Shorts der tiefere** und für **Longs der höhere** der
  beiden Preise. Wer long ist, will möglichst nah am Open Price kaufen, idealerweise darunter.
- Als Manipulations-Linie gelesen: sind wir bearish und Preis steht **über** der Linie, gilt der Move
  noch als **Manipulation** — bis Preis **mit einer Imbalance unter die Linie** geht.

Siehe [[Midnight Opening Range]] für die 0:00–0:30-Range selbst.

## Lunch: kein Handelsfenster

**12 Uhr / Lunchtime ist ausdrücklich eine No-Trading-Time** — erst zur NY-PM-Session wird wieder
gehandelt. Das ergänzt das [[NY Lunch Macro Model]], dessen Ausführungsfenster (10:50–11:10) davor
liegt.

## Forex-Killzone & News-Verlängerung

- **7–10 Uhr NY ist die NY-Killzone für Forex.**
- Ein **High-Impact-News-Driver um 10 Uhr verlängert die NY-Killzone bis 11:00/11:30**. Stimmt der
  Bias, ist die Manipulation des Tages zu diesem Zeitpunkt bereits passiert und die Volatilität
  lässt sich nutzen.

## Liquidity-Priorität für die AM-Session

Reihenfolge der Relevanz für die NY-AM-Session: **Premarket-Liquidität (7–9:30 Uhr)** zuerst, danach
**London-Liquidität**, danach erst **Asia-Session-Liquidität**.

## Macro um 8:30

Um **8:30 Uhr** gibt es eine starke Market Protection — also ein [[ICT Macros & Leading Candles|Macro]].
Zwischen **8:30–11 Uhr** ist zudem eine Hauptzeit für Forex-Trading in NY.

## Intraday-Fahrplan 7:00 – 11:30 (MentorShip 2025)

Der konkrete Ablauf eines Handelstags, wie ihn
[[Trading Premarket and Regular Session Liquidity (Source)]] durchkommentiert — Leitsatz
**Time/Day – Price – Liquidität**:

| Zeit (NY) | Was passiert |
|---|---|
| **7:00** | Premarket startet (13 Uhr DE). Run auf die offensichtliche Buyside, die sich *vor* Premarket gebildet hat → Retail-Offset, Liquiditätsaufbau |
| **kurz vor 8:30** | News Driver bringt Volatilität: erst Buyside nehmen, dann große Expansion in eine Discount-PD; Target ist die Premarket-Sellside-Liquidität |
| **9:30** | [[ORG (Opening Range Gap) & 1st Presented FVG#Der 9:30-Fake-Drop\|Fake Drop]] über ORG und Minor Buyside Pool auf die Quadranten der Premium Wicks |
| **ab 10:00** | Die Liquidität, die sich ab hier bildet, wird zum Ziel des Lunch Macro |
| **NY Lunch Macro** | Meist ein Retracement; attackiert **das erste High/Low vor 10 Uhr** bzw. die erste PD — nach der Opening Range |
| **10:50–11:10** | Das Macro, in dem das Lunch-Setup ausgeführt wird → [[NY Lunch Macro Model]] |
| **ab 11:30** | Lunch Macro attackiert die **während der Lunch Hour** gebildete Liquidität. Bullishe Session → Sellside, bearishe Session → Buyside; genommen wird das **offensichtlichste** Swing Low/High |
| **13:30–14:00** | Opening Range der **PM Session**, ebenfalls mit 1. presented FVG |

Die [[ICT 2025 Lecture Series (Source)]] präzisiert das Lunch-Fenster: der Move **ab 10:00** zum
nächsten Liquidity Pool wird **noch nicht gehandelt** — er *erzeugt* erst das Target. Gehandelt wird
im Macro **10:50–11:10**, und zwar nur, solange die neu gebildete Liquidität **intakt** bleibt.
Vollständige Regeln auf [[NY Lunch Macro Model]].

Der Tages-Bias wird dabei über den Wochentag mitbestimmt: im Beispiel ein **Donnerstag**, der Tag
mit der höchsten Wahrscheinlichkeit für das High/Low der Woche (siehe
[[Weekly Range Trading Model]]) — der Premarket-Ablauf ist ein
[[AMD Cycle (Accumulation – Manipulation – Distribution)|Po3]] aus Accumulation von Shorts,
Manipulation auf Minor Buyside und Distribution zur Sellside.

## Verwandt

- [[New Week Opening Gap (NWOG) Bias]] — wöchentlicher Bias-Filter, der auf dieses Session-Timing aufsetzt
- [[ICT Macros & Leading Candles]], [[Silver Bullet Model]]
- [[NY Lunch Macro Model]] — das regelbasierte Setup im Lunch-Fenster
- [[Midnight Opening Range]] — 0:00–0:30, gilt samt STD-Leveln den ganzen Tag
- [[ORG (Opening Range Gap) & 1st Presented FVG]] — Opening Ranges für London (1:30–2:00) und NY Pre Session (7:00–7:30)
- [[Kurz Notizen (Source)]], [[Trading Premarket and Regular Session Liquidity (Source)]]
