---
tags: [concept, ict, trading-ict, 2026, risiko, psychologie]
created: 2026-08-05
updated: 2026-08-05
sources: ["[[ICT Price Action Chronicles - MOC Crushing The Buying & Selling Pressure Myth (Source)]]"]
---

# Signal-Following & Crowd Liquidity Risk

Mechanik, warum das **öffentliche Teilen von Live-Entries/Stops/Targets die eigene Edge zerstört** —
und warum das **Kopieren fremder Signale mit echtem Geld** ein eigenständiges Risiko ist, unabhängig
von der Qualität des zugrundeliegenden Konzepts.

## Die Mechanik

1. Ein Trader mit großer Reichweite teilt einen konkreten Level (Entry, Stop, Target).
2. Ein relevanter Anteil der Follower platziert **echte Orders** genau dort — auch wenn explizit vor
   dem Nachahmen gewarnt wird oder es sich um ein Paper-Trading-Konto handelt (Follower kopieren mit
   echtem Kapital trotzdem).
3. Dadurch entsteht an genau diesem Level **reale, sichtbare Liquidität** — die für andere
   Marktteilnehmer manuell angreifbar wird (kurzzeitiges Spread-Widening, gezielte Mini-Runs auf
   nahe Liquidity Pools).
4. Ergebnis: der Level funktioniert **schlechter**, je mehr Leute ihn öffentlich kennen und darauf
   handeln — die Größe des eigenen Publikums wird zum Gegner der eigenen Methode.

> **Diminishing Return**: je größer die Followerschaft, desto geringer der Nutzen, live zu
> signalisieren — ab einem gewissen Punkt ist es reiner Nachteil.

## Konkrete Mechanik: manuelle Intervention (Whisper-Nachtrag)

Aus der vollständigen Audiospur (siehe Quelle) präzisiert ICT, **wie** ein öffentlich geteiltes Level
gezielt angreifbar wird — kein diffuses Marktrisiko, sondern konkrete Mechanismen:

- **Spread-Widening**: kurzzeitig wird der Spread über einer bekannten, dicht gedrängten
  Liquiditätszone verbreitert.
- **Gezielte Mini-Runs**: kurze, kleine Preisläufe genau bis knapp über/unter das bekannte Level,
  um dort geparkte Limit-Orders zu triggern, bevor der Preis wieder zurückdreht — beschrieben am
  eigenen Beispiel: eine eigene Partial-Limit-Order wirkte, als hätte sie "gerade eben" gefüllt,
  bevor der Preis sofort zurückdrehte.
- **Bereits kleine Beteiligung reicht**: ICT schätzt, dass schon **ein Bruchteil eines Prozents**
  seiner Reichweite (er nennt als Beispiel ein Viertel Prozent), der auf ein geteiltes Level Orders
  legt, genug konzentrierte, sichtbare Liquidität erzeugt, um sie manuell angreifbar zu machen —
  das Prinzip gilt genauso für kleinere Discord-/Signal-Service-Betreiber mit wenigen hundert
  Followern.

## Regulatorischer Hintergrund (CFTC, Whisper-Nachtrag)

ICT nennt explizit den Grund, warum er grundsätzlich **keine direkten Handelsempfehlungen** gibt,
sondern nur Preis-Analyse lehrt: die **Commodity Futures Trading Commission (CFTC)** kontaktierte
ihn in den 1990ern, weil er ohne entsprechende Lizenz öffentlich Trade-Meinungen geäußert hatte. Seit
diesem Vorfall trennt er strikt zwischen "Ich zeige/erkläre Preisverhalten" (erlaubt) und "Ich sage
dir, wann du einsteigen sollst" (vermieden) — deckt sich mit dem bestehenden Grundsatz "du gehst nie
in einen Trade, weil ich es dir sage" unten.

## Praktische Konsequenz

- **Analyse privat halten**, nicht öffentlich Entries/Stops/Targets in Echtzeit teilen.
- Wird ein Stop einmal gesetzt bzw. nachgezogen, **nicht mehr zurückändern**, nachdem die Position
  offen ist — Disziplin schlägt Reaktion auf kurzfristiges Noise, auch wenn der bereits nachgezogene
  Stop danach getroffen wird.
- Bei geteilten Signalen mit vielen Followern: **nicht jeder bekommt eine Füllung** zum selben Preis
  — reine Marktmechanik (begrenzte Liquidität an einem Preis), kein Bug.

## Operator-Fehler vs. Konzept-Fehler

Schlägt ein Setup fehl, ist das laut Quelle in der überwältigenden Mehrheit ein **Bias-Fehler des
Traders** (falsche Richtung angenommen), nicht ein Versagen der zugrundeliegenden Order-Flow-Logik.
Die Regeln selbst ändern sich nicht — die Fähigkeit, den Bias korrekt zu bestimmen, ist die eigentliche
Lernkurve.

## Verwandt

- [[Risikomanagement (1% pro Trade)]] — Positionsgrößen-Regel, unabhängig von diesem Konzept
- [[Market on Close (MOC) Macro Model]] — Ursprungskontext (öffentliches MOC-Beispiel mit Fill-Risiko)
- [[Trading Journal & DOL Checklist]]
- [[ICT Price Action Chronicles - MOC Crushing The Buying & Selling Pressure Myth (Source)]]
