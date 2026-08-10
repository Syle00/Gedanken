---
tags: [source, youtube, ict, trading-ict, ict-gems, fvg, bpr, 2025]
created: 2026-08-10
updated: 2026-08-10
---

# ICT Gems - Balanced Price Ranges Inside Fair Value Gaps (Source)

Quelle: https://www.youtube.com/watch?v=Eyp_XiYpB4A
Kanal: ICT Gems (Ausschnitte aus ICT-Originalvideos) | Veröffentlicht: 2025-02-10 | Länge: 15:38

> Rohtranskript: `raw/trading-ict/2026/yt-Eyp_XiYpB4A-transcript.md` (~2.900 Wörter,
> Auto-Captions, vollständig). **Inhaltlich der dichteste Ausschnitt der gesamten Playlist** —
> ICT nennt es selbst *"the highest tier of understanding order flow"*.

> **Kanalhinweis**: "ICT Gems" lädt Ausschnitte aus ICTs eigenen Videos hoch — unveränderte
> ICT-Lehre, nur zugeschnitten; entsprechend wie eine Primärquelle behandelt.

## Kernaussagen (trading-relevant, gefiltert)

**BPR innerhalb eines FVG** — ausgearbeitet in [[Balanced Price Range (BPR)]]

- **Welche Hälfte man untersucht**: bei einem **bearishen** FVG (SIBI) die **obere**, bei einem
  **bullishen** (BISI) die **untere**.
- **Warum sie "balanced" wird**: Läuft Preis dort im Lower Timeframe hin und her, ist diese Hälfte
  **effizient beliefert** — sie ist nicht mehr ineffizient und muss nicht erneut angeboten werden.
- **Die andere Hälfte ist die echte Ineffizienz**; sie sah nur einseitige Lieferung. Das Anliefern
  bis zum **Mittelpunkt** genügt: *"delivering price up to the halfway point satisfies the coding
  in that algorithm, it need not go any higher."*
- **Konsequenz**: Ein 15-Min-FVG muss seine balanced Hälfte **nicht** füllen — das "echte" FVG ist
  nur der andere Teil, auf dem 5-Min-Chart sichtbar.
- **Stop-Platzierung**: in den **oberen Quadranten** der balanced Zone (konservativer: knapp
  darüber) — **nicht** an die C.E., dort holen Spread und Wicks einen heraus.
- **Re-Entry nach Stopout**: Prämisse bleibt gültig, erneut einsteigen mit **halber Kontraktzahl**,
  Stop wieder oberer Quadrant oder knapp über dem High.

**Price Delivery Continuum Theory** — ausgearbeitet in [[Algorithmic Price Delivery Continuum]]

- Bei jedem 60-/15-/5-Min-Close zurück auf den jeweiligen Chart, dann wieder auf 1-Min zur
  Ausführung. *"I'm not living on those time frames… **it's not top-down analysis, it's cycling
  through continuously**."*
- **Universalität**: identisch auf NASDAQ, ES, Commodities und Bonds — *"everything that's traded
  uses this logic"*.

**Vier FVGs pro Stunde**

- In **jedem** Viertelstunden-Fenster (10:00–10:15, …, 10:45–11:00) bildet sich ein FVG auf 15M
  oder 5M → **vier Gelegenheiten pro Stunde**, von ICT als *"high frequency trading
  algorithmically"* bezeichnet.
- **Es muss sich nur bilden, nicht angehandelt werden** — der Algorithmus "postet" damit Bereiche,
  auf die er später zurückkommt.
- **Bleiben sie aus → High Resistance Liquidity Run**: 15 Minuten warten, dann nochmal 15, bis zum
  Sessionende. *"If the entire session was high resistance, you did nothing and you took no trade."*
  ICT nennt diese Prüfung ausdrücklich seine **"number one premise"**.
- **Richtungsfilter**: Zieht Preis zur Buyside, sucht man bullishe FVGs **oder** bearishe, die
  scheitern und zu [[IFVG (Inverse Fair Value Gap)|IFVGs]] werden.

**Anschluss an Gap-Typen**

- Bleibt die balanced Hälfte offen, ist das Gap ein [[Breakaway Gap]] — Erwartung: viel
  Folgebewegung. Auf halber Strecke folgt dann das **Measuring Gap** (siehe
  [[Implied Dealing Range]]).
- Der Konfluenz-Stack im Beispiel lief im **Macro 10:50–11:10** zusammen, zusammen mit der
  [[CISD (Change in State of Delivery)|CISD]] (niedrigster Opening Price aufeinanderfolgender
  Down-Close-Kerzen) und einem [[Institutional Order Flow Entry Drill (IOFED)|IOFED]].

## Bewusst ausgefiltert

Der Nebensatz, man hätte den NFP-Tag ohnehin nicht handeln sollen (bereits über
[[Two Stage News Delivery (FOMC & NFP)]] abgedeckt); rhetorische Zwischenrufe ("hello southbound
train baby").

## Verwandt

- [[Balanced Price Range (BPR)]], [[Algorithmic Price Delivery Continuum]]
- [[Fair Value Gap (FVG)]], [[BISI & SIBI (Buyside-Sellside Imbalance)]]
- [[Breakaway Gap]], [[Implied Dealing Range]], [[Low Resistance Liquidity Run]]
- [[Institutional Order Flow Entry Drill (IOFED)]], [[CISD (Change in State of Delivery)]]
- [[Verlust-Mitigation durch reduzierte Re-Entry-Size]]
