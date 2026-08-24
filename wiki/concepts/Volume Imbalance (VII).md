---
tags: [concept, ict, trading-ict, core, fvg, pd-array]
created: 2026-08-02
updated: 2026-08-16
sources: ["[[Enigma FVG Projections (Source)]]", "[[Alltime Highs und TGIF (Source)]]", "[[2026-07-31 - Market Review NQ July 31, 2026 (Source)|Market Review NQ July 31, 2026 (Source)]]", "[[2026-07-02 - Missed Entry How To Navigate The Same Trade Idea (Source)|Missed Entry How To Navigate The Same Trade Idea (Source, Video)]]"]
---

# Volume Imbalance (VII)

Die Lücke zwischen den **Körpern** zweier aufeinanderfolgender Candles — die Körper berühren sich
nicht, obwohl die Wicks überlappen. Im Vault durchgehend als **VII** abgekürzt.

> **Präzisierung (2026-08-13):** Die verbreitete Formulierung „Close der einen gegen Open der
> nächsten" trifft nur zu, wenn beide Candles in Richtung des Moves schließen. Gemessen wird
> **Körperkante gegen Körperkante** — `max(o,c)` bzw. `min(o,c)`. Bei einer **Gegenkerze** liegt der
> Close *innerhalb* des Körpers, und die Close/Open-Variante meldet dann eine Lücke, die der
> Kerzenkörper selbst schon abgedeckt hat. Kontrolliert an 13 vom Nutzer eingezeichneten
> MNQ-Boxen (13.08.2026); Regressionstest `tools/test_fvg_vii.py`.

Zwei Rollen, beide wichtig:

1. **Als Hilfsmittel**, um ein [[Fair Value Gap (FVG)|FVG]] **korrekt einzuzeichnen**.
2. **Als eigenständige [[PD Array]]** — eine VII ist für sich genommen ein Level, auf das Preis
   reagiert.

## Die Einzeichnungsregel

> **Eine VII wird immer mit eingezeichnet, wenn sie vorhanden ist. Ist keine da, werden die Wicks
> genutzt.**

Deshalb gilt beim FVG: **immer auf Open und Close achten**, nicht nur auf die Wick-Extrema. Wer das
FVG allein über die Wicks aufzieht, verfehlt die Grenzen, sobald eine VII vorliegt.

### Beispiel

Drei Candles mit folgenden Werten:

| | Open | Close |
|---|---|---|
| Candle 1 | — | **28.450,25** |
| Candle 2 | **28.450,50** | **28.274,50** |
| Candle 3 | **28.275,00** | — |

Daraus ergeben sich **zwei VII**:

- **Oben**: Close Candle 1 (28.450,25) → Open Candle 2 (28.450,50) = **0,25 Lücke**
- **Unten**: Close Candle 2 (28.274,50) → Open Candle 3 (28.275,00) = **0,50 Lücke**

Beide werden beim Einzeichnen des FVG mitgenommen — die Begrenzung kommt also aus den VII, nicht aus
den Wicks.

> ⚠️ Die Beispielwerte stammen aus einer mündlichen Erläuterung, in der das Setup als **BISI**
> bezeichnet wurde. Die Zahlenfolge beschreibt aber eine **Abwärts**-Sequenz (Candle 2 fällt von
> 28.450,50 auf 28.274,50, Candle 3 eröffnet darunter) — nach der Definition auf
> [[BISI & SIBI (Buyside-Sellside Imbalance)]] also ein **SIBI**. Die Einzeichnungsregel ist
> richtungsunabhängig und davon nicht betroffen; nur das Label ist zu prüfen.

## Candle-Auswahl bei Level-Test (2026-Ergänzung)

Liegt an einer BISI/SIBI zusätzlich eine VII, zählt für die Gültigkeit eines Levels-Tests **nicht
irgendeine berührende Candle**, sondern ausschließlich diejenige Candle, die die VII tatsächlich
erzeugt hat. Quelle: [[2026-07-31 - Market Review NQ July 31, 2026 (Source)|Market Review NQ July 31, 2026 (Source)]].

## Als eigenständige PD Array

Über die Hilfsfunktion hinaus ist die VII ein Ziel wie jede andere [[PD Array]]. In
[[Alltime Highs und TGIF (Source)]] wird eine **Daily VII** angelaufen, danach folgt eine
**explosive Reaktion** — sie wirkt dort als Draw, nicht als Zeichenhilfe.

## Als Fib-Anker in der Projektion

[[Enigma FVG Projection]] misst wahlweise **mit** oder **ohne** VII:

- **Mit VII**: das Fib beginnt an der Candle **inklusive des VII-Open** der antizipierten mittleren
  Candle und läuft bis zum Low der Wick der nächsten Candle.
- **Ohne VII**: dasselbe ohne diesen Bezugspunkt.

Im DXY-Beispiel der Quelle ergibt das **101,805 mit** gegenüber **101,795 ohne** VII — eine Differenz
von 0,010, also genau die Größenordnung einer Close-Open-Lücke.

## VII als Stop-Anker (2026-Ergänzung)

Aus [[2026-07-02 - Missed Entry How To Navigate The Same Trade Idea (Source)|Missed Entry How To Navigate The Same Trade Idea (Source, Video)]]:
Bei einem Short mit Limit-Entry knapp über der C.E. eines FVG legt ICT den **initialen Stop über
die Volume Imbalance**, die über diesem FVG liegt — *„Stop loss above the volume balance."*

Die VII dient hier also nicht als Ziel oder Entry, sondern als **strukturelle Invalidierungsmarke**:
Handelt Preis über sie hinaus, ist die Prämisse gebrochen. Der Stop wandert danach in Stufen weiter
(Rejection Block, dann laufende Hochs) — vollständige Kaskade in
[[Missed Entry Trade Management Playbook]].

Konsistent mit der Einstufung als eigenständige PD Array oben: Eine VII ist ein Level, an dem eine
Reaktion erwartet wird, und taugt damit für beide Seiten des Trades.

## Verwandt

- [[Fair Value Gap (FVG)]] — die VII entscheidet über dessen Grenzen
- [[BISI & SIBI (Buyside-Sellside Imbalance)]], [[PD Array]]
- [[Enigma FVG Projection]] — VII als Fib-Anker
- [[Balanced Price Range (BPR)]], [[Institutional Order Flow (Body vs Wick)]]
- [[Smart Money Concepts (SMC)]]
