---
tags: [concept, ict, trading-ict, 2026]
created: 2026-08-01
updated: 2026-08-16
sources: ["[[From Vision To Execution (Source)]]", "[[ICT 2026 Smart Money Concepts Lecture - January 02, 2026 (Source)]]", "[[Kurz Notizen (Source)]]", "[[Opening Range Theory - 1st Presented FVG Logic (Source)]]", "[[2026-08-10 - Navigating High Resistance Liquidity Run Conditions (Source)|Navigating High Resistance Liquidity Run Conditions (Source)]]", "[[2026-05-13 - Turning Loss Into Gain - Market Alchemy (Source)|Turning Loss Into Gain - Market Alchemy (Source)]]"]
---

# IFVG (Inverse Fair Value Gap)

Ein [[Fair Value Gap (FVG)]], das seine Polarität wechselt, nachdem Preis komplett durch das Gap
gehandelt hat — ein ursprünglich bullishes FVG (BISI) fungiert danach als bearishe Referenzzone
(und umgekehrt). Wird bevorzugt gegenüber der gegenüberliegenden PD Array der schwächeren
Buy-/Sellside-Curve genutzt (siehe [[Modell 22]]).

![[image 1.png]]
*Displacement-Sequenz nach einem Turtle Soup, die auch für spätere reclaimed FVGs oder IFVGs maßgeblich bleibt.*

## Validierungsbedingung (Kurz Notizen)

Ein FVG wird nur dann zu einem echten IFVG, wenn zuvor **entweder** sein High/Low **oder** sein C.E
respektiert wurde — eines von beiden MUSS gegeben sein. Ohne diesen vorherigen Respekt handelt es
sich nicht um ein valides IFVG.

## Mehrfach-Qualifizierung vor dem Entry (Live-Trade 2026-08-10)

Die Validierungsbedingung oben sagt, *wann* ein FVG überhaupt ein IFVG ist. Der Live-Trade in
[[2026-08-10 - Navigating High Resistance Liquidity Run Conditions (Source)|Navigating High Resistance Liquidity Run Conditions (Source)]]
zeigt, wie oft es sich **bestätigen** muss, bevor ICT tatsächlich einsteigt:

1. Bearishes FVG bei bullishem Kontext, Preis handelt komplett durch → Close **über** dem Gap =
   1. Qualifizierung ("qualifies and confirms").
2. Preis handelt wieder **zurück durch** das Gap (bei IFVGs normal), rallyt und schließt erneut
   darüber = 2. Qualifizierung.
3. Erst jetzt gilt es als brauchbare Entry-Zone: *"that qualifies two times this inversion FVG
   after it gives you what you're looking for before you anticipate utilizing it for entries."*

**Entries über das ganze Gap verteilen, nicht auf einen Preis.** Konkrete Skalierung im Trade:
Start 4 Kontrakte, +2 beim erneuten "Kiss" des Gap-Highs, weitere Adds im **tiefen Ende** des Gaps
und im oberen Quadranten — Endgröße 12 Kontrakte, Durchschnittspreis ≈ **High des IFVG**. Danach
Stop auf **IFVG-Low − 1 Tick** (Anker = das bereits qualifizierte Gap-High, nicht ein beliebiges
Swing-Level).

Stärkezeichen währenddessen: Der Rücklauf erreicht das **C.E. des IFVG nicht** (im Beispiel Low
29.796,25 gegen C.E. 29.796,25 — knapp darüber gedreht). Zusätzlich gilt die
Body-über-Wick-C.E.-Regel aus [[Institutional Order Flow (Body vs Wick)]].

## Das 1. Presented FVG ist meist ein IFVG

**90 % der Zeit ist das erste FVG einer Session ein IFVG** — Voraussetzung ist ein sauberer Bias.
Das erste starke Displacement nach dem Liquidity Sweep im Opening-Range-Fenster reißt das FVG, das
dann invertiert und in die Gegenrichtung liefert. Details und Chartbeispiel:
[[ORG (Opening Range Gap) & 1st Presented FVG]].

## Gescheiterte „First Utilization" — wie ein SIBI zum bullishen IFVG wird (2026-05-13)

Aus [[2026-05-13 - Turning Loss Into Gain - Market Alchemy (Source)|Turning Loss Into Gain — Market Alchemy (Source)]]
die klarste Formulierung des Umkipp-Moments im Vault:

> *„Remember, the **first presented utilization** is that they're SIBIs. So price going up into them
> should offer bearish prices. **It didn't do it here. And it didn't do it here.** So these two have
> failed in their initial role of first utilization."*

Ein SIBI hat also eine **erste, vorgesehene Rolle** (Preis von oben abweisen). Erfüllt er sie beim
ersten Anlauf **nicht**, ist er damit invertiert — die Inversion ist ein *ausgebliebenes*
Verhalten, kein zusätzliches Ereignis. Spiegelbildlich für ein BISI, das nicht mehr stützt.

**Haltebedingung danach** (mehrfach im Video wiederholt, deckt sich mit
[[Institutional Order Flow (Body vs Wick)]]):

- Solange Preis **in** der Zone ist: **Bodies bleiben in der oberen Hälfte** (bullish gelesen).
- Sobald Preis die Zone **verlassen** hat: in der unteren Hälfte sind **gar keine Bodies** mehr
  zulässig. Ein Wick hinein ist erlaubt — der „Mohawk" — *„it can touch the high, wick into this a
  little bit, but then it needs to really start traveling higher."*
- Kommt Preis zurück hinein, muss der Body **wieder über die C.E. des Referenz-Wicks** schließen,
  bevor die These weiterhin trägt.

Praxisfolge fürs Stop-Placement: Der Stop gehört **unter die C.E. des Wicks**, nicht unter den Wick
selbst — *„underneath the midpoint of this wick, allowing for that little Mohawk."*

## Verwandt

- [[Fair Value Gap (FVG)]], [[BISI & SIBI (Buyside-Sellside Imbalance)]]
- [[ORG (Opening Range Gap) & 1st Presented FVG]]
- [[Modell 22]], [[Silver Bullet Model]]
- [[Chain of Custody (Q-Validation)]] — nutzt IFVGs auch im Higher Timeframe
- [[Kurz Notizen (Source)]], [[Opening Range Theory - 1st Presented FVG Logic (Source)]]
