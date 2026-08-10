---
tags: [concept, ict, trading-ict, core-content, month-09, daytrade, daily-range]
created: 2026-08-10
updated: 2026-08-10
sources: ["[[ICT Mentorship Core Content - Month 09 - Filling The Numbers (Source)]]", "[[Filling The Numbers (Source)]]"]
---

# Filling The Numbers (4 Level pro Tag)

ICTs Methode, die **Reichweite der Tagesrange** zu bestimmen — nicht die Richtung. Grundthese:
IPDA handelt pro Tag zu **vier Leveln** ("numbers") in Richtung der Tagesrange. Vier ist dabei
eine **Faustregel, keine Obergrenze** — an großen Range-Tagen werden fünf oder mehr gefüllt.

Das ist die direkte Antwort auf die Layer-0-Frage "wie weit geht der Tag", ergänzend zum
Richtungs-Bias aus [[Institutional Order Flow (Body vs Wick)]] und [[PD Array]].

## Die Zählregel

Gezählt wird **ab dem eigenen Entry**, in Handelsrichtung:

- Long → die nächsten vier Level **über** dem Entry.
- Short → die nächsten vier Level **unter** dem Entry.

Beispiel aus der Lektion: Short-Entry nahe **R2** → die vier Ziele sind M4, R1, M3, Central Pivot.

## Vier Messlatten — dieselbe Zählung, andere Skala

ICT nutzt vier voneinander unabhängige Werkzeuge, um diese Level zu definieren.

### 1. Floor Trader Pivots (0 GMT)

Klassische Pivots, aber **inklusive der Midpoints**: von unten nach oben
S3, M0, S2, M1, S1, M2, **Central Pivot**, M3, R1, M4, R2, M5, R3 — jedes M ist der 50-%-Punkt
zwischen den beiden benachbarten Hauptleveln.

- Begründung ist nicht Pivot-Mystik, sondern **"staged orders"**: Retail *und* Fonds platzieren
  Orders an diesen Leveln, also handelt IPDA dorthin und hindurch, um Liquidität abzugreifen. Ob
  dort gekauft oder verkauft wird, ist egal — entscheidend ist, dass Orders liegen.
- Retail liest sie falsch herum: "alles unter dem Central Pivot ist ein Kauf". Genau deshalb ist
  ein Rücklauf nach S1/S2 in einer bereits nach unten expandierenden Tagesrange oft ein
  **Continuation-Sell**.
- ICT nutzt Pivots **nicht für Entries**, ausschließlich für die Reichweitenmessung.

### 2. CBDR-Standardabweichungen

Basis: [[Central Bank Dealers Range (CBDR)]]. Beim Short **über** dem CBDR-Low zählt das
**CBDR-Low selbst als Level 1**, sobald Preis es durchhandelt; danach wird jede weitere nach unten
projizierte STD der CBDR zu Level 2, 3, 4. Spiegelbildlich beim Long über das CBDR-High.

### 3. Asian-Range-Standardabweichungen

Identische Mechanik mit der [[Asian Range]]: Beim Kauf **unter** der Asia Range zählt das
**Asia-High als Level 1**, danach jede nach oben gestackte Range-Projektion.

### 4. Flout

Siehe [[Flout (15-00 NY Range)|Flout]] — die Projektionseinheit ist dort **die halbe** Flout-Range,
nicht die volle. Wichtigster Fehlerfall der ganzen Lektion.

## Welche Messlatte gilt heute?

Ehrliche Antwort von ICT: **vorher weiß man es nicht.**

> *"You never know for certain before the day begins what IPDA is going to use to fulfill its
> daily range."*

Das Verfahren ist deshalb kein Auswählen, sondern ein **Überlagern**:

1. Alle vier Messlatten projizieren — nicht nur die Lieblingsmethode.
2. Auf **Konfluenz** prüfen: Wo überlappen zwei oder mehr Projektionen?
3. Diese Überlappung mit **Tageszeit** ([[ICT Daily Range Session Timing]]) und der
   **PD-Array-Matrix** verschneiden — bleibt überhaupt noch genug Zeit im Tag, um dorthin zu laufen?
4. Mit fortschreitendem Handelstag wird das Bild schärfer: Die **New Yorker Session** verrät
   in der Regel, welche Messlatte IPDA an diesem Tag tatsächlich benutzt.

Einzeln genommen bedeuten die Projektionen laut ICT **nichts** — erst die Konfluenz macht sie
verwertbar.

## Positionsmanagement an den vier Leveln

- Sind vier Level gefüllt, sollen **75–80 % der Position** realisiert sein.
- **25–30 % bleiben stehen** für den Fall eines großen Range-Tags — ausdrücklich, weil man sich
  in der Reichweite irren *kann* und dieser Irrtum hier zugunsten der Position ausfällt.
- Relevanter Sonderfall: Sind die vier Level bereits **innerhalb der London Session** gefüllt, gilt
  dieselbe Regel — New York kann danach eine völlig eigene Expansion liefern.

Deckt sich mit [[Partial Profit-Taking & R-Multiple-Skalierung]], hier aber an
**Range-Leveln** statt an R-Multiples festgemacht.

## Zusätzliche Tagesreferenzen

Unabhängig von den vier Messlatten gelten als Daytrade-Grundinventar: **PDH/PDL** sowie die
**Highs/Lows der letzten drei Tage** (jeweils das markanteste). Erwartung ist ein Retest oder
Durchhandeln eines dieser Level — nicht garantiert, denn die Tagesrange kann schlicht zu klein
ausfallen.

## Der Rundzahl-Vorlauf

Praxisregel aus dem Worked Example (EUR, Mai 2017): Die Projektion **M5** lag bei **10933**. ICT
nahm nicht 10933, sondern die **nächstliegende Rundzahl davor — 10930** — als Ziel. Tatsächliches
Tageshoch: **10935**.

> Regel: vor der berechneten Projektion aussteigen, an der nächsten runden Zahl davor. Das Level
> ist eine Zone, kein Tick.

## Harte Voraussetzung: Displacement

Ohne Volatilität keine Präzision. *"If the markets do not move and have volatility you cannot get
precision because there has to be displacement."* An Tagen ohne Displacement ist die gesamte
Methode nicht anwendbar — dann fehlt die Expansion, die die Level überhaupt erst füllt.

## Verwandt

- [[Flout (15-00 NY Range)|Flout]], [[Central Bank Dealers Range (CBDR)]], [[Asian Range]]
- [[Daily High & Low Projektion (Konvergenz)]] — dieselbe Konfluenz-Logik, andere Werkzeuge
- [[ICT Daily Range Session Timing]], [[PD Array]]
- [[The Sentiment Effect]] — liefert den Entry, diese Seite die Ziele
- [[Partial Profit-Taking & R-Multiple-Skalierung]]
- [[Filling The Numbers (Source)]] (Notion-Kurzfassung),
  [[ICT Mentorship Core Content - Month 09 - Filling The Numbers (Source)]] (Video-Vollfassung)
