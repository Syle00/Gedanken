---
tags: [concept, ict, trading-ict]
created: 2026-08-01
updated: 2026-08-02
sources: ["[[Mitigation Blocks (Source)]]"]
---

# Mitigation Block

Order-Block-Variante nach einem **Failure Swing**: Bestätigung, dass Smart Money sich (z.B. Short)
positioniert hat und tiefere Preise wahrscheinlicher werden.

![[image 44.png]]
*Failure Swing als Bestätigung, dass Smart Money short positioniert ist.*

## Definition

- Fokus liegt auf der **letzten bearishen Candle** vor der Bewegung, innerhalb derer noch aktiv
  gekauft wurde ("Buying stattgefunden hat") — das macht sie zum bearishen Level für einen Short.

![[image 45.png]]
*Fokus auf die letzte bearishe Candle — innerhalb dieser fand noch Buying statt, das macht sie zum bearishen Level.*

- Kehrt Preis zu dieser Candle zurück (Market Structure Shift Return), ist das typischerweise der
  Moment, in dem Smart Money Verluste begrenzt oder auf Breakeven setzt.
- Danach wird erwartet, dass sich die Bewegung fortsetzt bis zum letzten (vorherigen) Low.

## Verwandt

- [[PD Array]]
- ⚠️ Verwandte Order-Block-Typen (Reclaimed, Breaker, Rejection Block) noch nicht ingested — siehe
  `raw/trading-ict/Core Content/Reclaimed ICT Orderblock.md` und die
  `Reeinforced Orderblock Theory ...`-Dateien.
