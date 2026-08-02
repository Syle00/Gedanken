---
tags: [concept, ict, trading-ict, core]
created: 2026-08-01
updated: 2026-08-02
sources: ["[[Blending IPDA Data Ranges & PD Arrays (Source)]]"]
---

# PD Array

Premium/Discount Array — Sammelbegriff für die Kurszonen (Order Block, FVG,
[[Volume Imbalance (VII)|Volume Imbalance]], Liquidity Pool etc.), auf die Preis reagiert. Grundbaustein für [[ICT Daily Range Session Timing]], [[New Week Opening Gap (NWOG) Bias]]
und praktisch jedes ICT-Modell.

## Kernregeln

- Eine PD Array ist **einmalig nutzbar**: Sobald Price hineingetradet ist *und* davon reagiert hat,
  gilt sie als verbraucht und wird nicht erneut verwendet. Beispiel: Bullish Order Block im Premium
  wird angelaufen, Preis reagiert und tradet zurück ins Discount → OB ist "aufgebraucht".

![[image 183.png]]
*Bullish OB wird angelaufen, Preis reagiert und tradet zurück ins Discount — die PD Array ist danach
verbraucht.*

- Zielauswahl: Die **Discount PD Array liegt immer einen Timeframe niedriger** als das Premium-High,
  das sie bedient — als Target gilt immer der nächst-niedrigere Timeframe.

![[image 188.png]]
*Market Maker Manipulation Template (Tuesday High auf der Week): Discount PD Array liegt einen
Timeframe niedriger als das Premium-High.*
- Wird eine PD Array durchbrochen statt zu reagieren, ist die nächsthöhere Timeframe-PD das neue Ziel.

## 3 Komponenten einer starken PD (Kurz Notizen)

Drei Bedingungen MÜSSEN gleichzeitig erfüllt sein, damit eine PD Array als stark gilt:

1. **Time of the Day**: passende Session bzw. [[ICT Macros & Leading Candles|Macro]]-Zeit.
2. Die **PD Array bildet sich** überhaupt (FVG, OB, etc.).
3. Die PD Array bildet sich **auf einem gegradeten Level** einer bestehenden Imbalance, eines
   [[New Week Opening Gap (NWOG) Bias|NWOG]], [[ORG (Opening Range Gap) & 1st Presented FVG|ORG]] o.ä.

![[Kurz Notizen - Strong PD Array Example.png]]
*Beispiel einer starken PD Array: alle 3 Komponenten (Timing, Bildung, gegradetes Level) treffen zusammen.*

Sind extrem kleine Candle-Bodys am unteren/oberen Ende einer Imbalance vorhanden, wertet ICT das
laut Quelle nicht als bedeutend — der bestehende Bias bleibt maßgeblich.

## Verwandt

- [[Equilibrium Vs. Discount]] — Premium/Discount-Einteilung der Range
- [[IPDA Data Ranges]] — Lookback-Fenster, in denen PD Arrays gesucht werden
- [[Chain of Custody (Q-Validation)]] — Q-Level als zusätzliche Validierung einer PD Array
- [[Kurz Notizen (Source)]]
- ⚠️ Noch offen: eigene Seiten für Order Block, Fair Value Gap (FVG), Liquidity Pool als konkrete
  PD-Array-Typen — bislang nur implizit über Quellen wie [[Reeinforced Orderblock Theory]] referenziert.
