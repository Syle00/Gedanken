---
tags: [source, ict, trading-ict, mentorship-2022, youtube]
created: 2026-08-14
updated: 2026-08-14
sources: []
---

# 2022-02-18 - 2022 ICT Mentorship Episode 10 (Source)

Quelle: raw/2022-ict-mentorship/yt-S9ORTYmXwdE-transcript.md (YouTube, https://www.youtube.com/watch?v=S9ORTYmXwdE)
Kanal: The Inner Circle Trader | Veröffentlicht: 2022-02-18 | Länge: 1:06:46

Direkte Fortsetzung von [[2022-02-16 - 2022 ICT Mentorship Episode 9 (Source)|Episode 9]] —
vertieft **Power Three** und führt den **Opening Range**-Begriff (Open bis zum ersten Extrem)
sowie die Rolle des Wirtschaftskalenders ein. Meistgestellte Frage laut ICT über all die Jahre:
"kannst du mir den Daily Bias beibringen" — diese Episode ist seine Antwort in voller Länge.

## Zusammenfassung

Zwei Bausteine: (1) der Wirtschaftskalender (forexfactory.com) als Pflichtlektüre vor jedem
Handelstag, mit 8:30 NY als "News-Embargo"-Zeitpunkt; (2) eine sehr ausführliche Herleitung von
**Power Three** über die klassische Open-High-Low-Close-Bar, inkl. der **Opening-Range**-Technik
zur Projektion der Setup-Zone.

## Kernpunkte

- **Swing-Definition**: Ein Swing High/Low braucht nur **drei Candles** (höhere/tiefere Nachbarn
  links und rechts) — explizit **keine** Williams-Fraktale ("that's way too many candles and
  you've missed the move"). Relevant für alle Struktur-Detektoren in `tools/analyze_ohlc.py`.
- **Opening Range definiert** (neuer Begriff, nicht deckungsgleich mit
  [[Midnight Opening Range]], die sich auf 0:00–0:30 NY bezieht): die Range vom **Opening Price**
  (8:30 NY) bis zum ersten Extrem in die Gegenrichtung (Judas Swing). Diese Range wird
  **vom Opening Price aus in die erwartete Richtung gespiegelt/projiziert** — dort liegen laut
  ICT praktisch alle Premium Arrays (FVGs, Stop-Raids, OTE) für den Tag. "Close proximity
  entries" = Entries knapp unter/über dem Opening Price, wenn der Judas Swing verpasst wurde.
- **Opening-Price-Hierarchie**: primär **8:30 NY** (Equity-News-Embargo), nicht Mitternacht — im
  Gegensatz zur Betonung von 0:00 NY in [[Midnight Opening Range]] und
  [[ICT 2022 - Episode 11 Important Dealing Range (Source)]] (0:00 für den ganzen Tag, 8:30 nur
  für NY AM). ICT nutzt hier für Power Three auf dem **Daily**-Chart explizit 8:30 als Referenz;
  siehe aber [[2026-04-21 - 2022 ICT Mentorship Episode 19 (Source)|Episode 19]] für die spätere,
  präzisere Kombination beider Referenzpunkte.
- **Fibonacci-Projektionstechnik**: Range von einer Imbalance-Hoch zu -Tief nehmen, **×2** vom
  Opening Price aus projizieren, um die Short-/Long-Zielzone zu bestimmen — konkret am Beispiel
  gezeigt und funktionierte "nicht cherry-picked" laut ICT.
- **Bevorzugte Timeframe**: 15 Minuten als "Bellweather Chart" — "if I was held to a decision of
  what time frame would you be forced to trade with... the 15-minute time frame". Für
  Top-down-FVG-Suche: 5→4→3→2→1 Minute, beim ersten Treffer stoppen (keine tiefere TF nötig).
- **Margin-Risiko-Warnung** (konkrete Zahlen): TDMR-Broker-Margin für einen NQ-Mini ≈ $22.000,
  Discount-Broker teils nur ≈ $1.500–2.000/Kontrakt verlangt — ICT nennt das explizit
  fahrlässig; Beispielrechnung eines 100-Punkte-Slippage-Verlusts bei 8 Kontrakten = $8.000+.
  Empfohlenes Mindestkapital: $10.000–15.000 für NASDAQ-Futures (Stand 2022, nominal, nicht auf
  MNQ übertragbar).
- Nebenbemerkung: steigende Exchange-Margin-Anforderungen interpretiert ICT als Signal für
  bevorstehende große Bewegungen ("the exchange tipping their hand").

## Verwandt

- [[2022-02-16 - 2022 ICT Mentorship Episode 9 (Source)|2022 ICT Mentorship Episode 9 (Source)]] (Vorgänger)
- [[ICT 2022 - Episode 11 Important Dealing Range (Source)]] (0:00 vs. 8:30, direkter Vergleich)
- [[ICT MentorShip 2022 (Source)]] (Serien-Navigation)
- [[AMD Cycle (Accumulation – Manipulation – Distribution)]], [[Midnight Opening Range]],
  [[Optimal Trade Entry (OTE)]], [[Judas Swing]], [[ICT Daily Range Session Timing]]
