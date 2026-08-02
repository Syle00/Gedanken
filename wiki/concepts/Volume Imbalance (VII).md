---
tags: [concept, ict, trading-ict, core, fvg, pd-array]
created: 2026-08-02
updated: 2026-08-02
sources: ["[[Enigma FVG Projections (Source)]]", "[[Alltime Highs und TGIF (Source)]]"]
---

# Volume Imbalance (VII)

Die Lücke zwischen dem **Close** einer Candle und dem **Open** der nächsten — die Körper berühren
sich nicht, obwohl die Wicks überlappen. Im Vault durchgehend als **VII** abgekürzt.

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

## Verwandt

- [[Fair Value Gap (FVG)]] — die VII entscheidet über dessen Grenzen
- [[BISI & SIBI (Buyside-Sellside Imbalance)]], [[PD Array]]
- [[Enigma FVG Projection]] — VII als Fib-Anker
- [[Balanced Price Range (BPR)]], [[Institutional Order Flow (Body vs Wick)]]
- [[Smart Money Concepts (SMC)]]
