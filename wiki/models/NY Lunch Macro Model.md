---
tags: [model, ict, trading-ict, lecture-2025, daytrade, macro, sessions]
created: 2026-08-02
updated: 2026-08-10
sources: ["[[NY Lunch Macro Rules & PM Session & Final RTH Hour (Source)]]", "[[ICT Gems - When To Anticipate Price Spooling (Source)]]"]
---

# NY Lunch Macro Model

Konkretes Intraday-Setup rund um die NY-Lunch-Stunde. Das Lunch Macro ist ein **Retracement
innerhalb der Daily Range** — bei einem bearishen Tag bzw. einer bearishen Opening Range ein
Retracement **nach oben zur Buyside**, bei einer bullishen Opening Range eines **zur Sellside**.

Bei einer sehr großen, extrem einseitigen Opening Range, in der keine Minor Liquidity genommen
wurde, wird das Retracement zum **offensichtlichen Minor Liquidity Pool** erwartet.

## Ablauf

1. **Ab 10:00 Uhr NY** läuft Preis zum nächstliegenden **Liquidity Pool oder einer PD Array** — bei
   einem bearishen Gap zur Buyside, bei einem bullishen zur Sellside.

   > **Diesen Move handelt man noch nicht.**

2. Dadurch bildet sich ein **neues High/Low mit Minor Buy-/Sellside-Liquidität**. Genau dieses
   High/Low ist später das **Target**.
3. Gewartet wird auf das **Macro 10:50–11:10** — dort liegt das eigentliche Trade-Setup.
4. Bestätigung: das darauffolgende **Swing High/Low muss failen** und es **nicht schaffen, die
   Liquidität zu nehmen**. Das ist das starke Anzeichen dafür, dass es zurück zum vorher gebildeten
   Swing High/Low mit Liquidität geht.

**Faustregel:** *ab 10:00 Uhr NY nach rechts schauen — das nächste High oder Low, das sich bildet,
ist das Target.*

## Die vier Regeln

1. **9:30–10:00 Uhr**: ein Rutsch, d.h. **kein** Short-Term-High/-Low wurde attackiert — **kein**
   Minor Buyside Pool bei bearishem, **kein** Minor Sellside Pool bei bullishem Bias.
2. **Ab der 10-Uhr-Linie nach rechts schauen**: bei einem vorangegangenen **bearishen** Move auf das
   **erste High**, bei einem **bullishen** Move auf das **erste Low** nach 10 Uhr.
3. Hat sich dieses **Low** (bearisher Move) bzw. **High** (bullisher Move) gebildet, darf es
   **nicht genommen werden** — die Liquidität muss **intakt** bleiben.
4. **Execution optimal im Macro 10:50–11:10.**

![[ICT 2025 - Lunch Macro 06.png]]
*Intaktes Low — es wurde nicht genommen; die Struktur wird als [[Rejection Block]] PD Array gelesen.*

Punkt 3 ist der Kern des Modells: das Setup lebt davon, dass die frisch gebildete Liquidität
**unangetastet** bleibt. Wird sie genommen, ist das Setup weg.

![[ICT 2025 - Lunch Macro 01.png]]
*Lunch Macro als Retracement innerhalb der Daily Range zur gegenüberliegenden Liquidität.*

## Die 11:30-Variante: "gegen den, der im Geld ist" (2024-Ergänzung)

Aus [[ICT Gems - When To Anticipate Price Spooling (Source)]] — eine **mechanisch formulierte**
Fassung desselben Gedankens, die ohne die Vier-Regeln-Kette oben auskommt. Sie setzt die
Macro-Funktionsdefinition (*"they roll against who's in the money right now"*, siehe
[[ICT Macros & Leading Candles]]) direkt in einen Ablauf um:

1. **Um 11:30** rückwärts schauen und fragen: **Wer verdient gerade Geld** — die Longs oder die
   Shorts? (Beispiel: Markt läuft seit 9:30 nach oben → die Longs.)
2. Der Algorithmus zielt dann auf die **nachgezogenen Stops der Gewinnerseite**, also bei Longs auf
   die Sellside darunter.
3. **Welches Level genau**: von 11:30 aus rückwärts das **erste Low** suchen — mit der harten
   Zusatzbedingung, dass es **nach 10:00 Uhr** entstanden sein muss.
4. Genau dorthin läuft Preis. Im Beispiel deckte sich dieses Low zusätzlich mit dem
   [[New Week Opening Gap (NWOG) Bias|NWOG]] der Woche — solche Überlagerungen erhöhen die
   Erwartung.

**Warum die 10:00-Grenze?** Sie klammert alles aus, was der [[Silver Bullet Model|Silver Bullet]]
und die Protraction davor erzeugt haben. Übrig bleibt das Low, an das die Masse tatsächlich ihre
Stops nachgezogen hat.

**Zeitfenster**: Das Lunch Macro beginnt in dieser Fassung **11:30** und kann **bis 13:30** laufen.
Es *muss* nicht abverkaufen — läuft Preis einfach weiter, gibt es kein Setup. Erst wenn ein
Abverkauf einsetzt, greift die Suche nach dem ersten Low.

**Nach 13:30** endet der Zeitdruck, Stops zu nehmen. Preis ist dann frei, die ursprüngliche
Tagesrichtung wieder aufzunehmen — im Beispiel die Rallye zum Tageshoch in der letzten Stunde.

> ⚠️ **Abweichender Startzeitpunkt.** Der obere Teil dieser Seite (Lecture-2025-Fassung) legt die
> Execution ins Macro **10:50–11:10**; die Gems-Fassung nennt **11:30** als Beginn des Lunch
> Macros. Beide stammen von ICT und beschreiben dieselbe Idee (Retracement gegen die Morgenrichtung
> zur nachgezogenen Liquidität), datieren sie aber unterschiedlich. Nicht aufgelöst — für einen
> Backtest beide Startzeiten getrennt prüfen.

### Positionsführung: nicht abwürgen

Direkte Handlungsanweisung für eine Position, die aus dem Morgen läuft: **Stop nicht laufend
nachziehen** (*"you do not strangle it by running your stop loss up"*) — gerade weil man den
11:30-Rücklauf gegen die Morgenrichtung **erwartet**. Wer den Stop eng nachzieht, wird von genau
dem Move herausgenommen, den das Modell vorhersagt.

## PM Session

- Die **Opening Range der PM Session** geht von **13:30–14:00 Uhr NY**; auch hier wird das
  **1. presented FVG** der Session gesucht (siehe
  [[ORG (Opening Range Gap) & 1st Presented FVG]]).
- Die Quelle notiert an anderer Stelle **13:30 bis 14:00** als PM-Opening-Range — das deckt sich mit
  der bereits im Wiki stehenden Angabe „1:30–2 Uhr NY".

![[ICT 2025 - Lunch Macro 05.png]]
*Opening Range der PM Session ab 13:30 NY.*

> ⚠️ Der Abschnitt **„RTH Final Hour Of Trading"** ist in der Rohquelle nur als Überschrift
> vorhanden und **inhaltlich leer** — trotz des Seitentitels gibt es dazu nichts. Ebenso bricht die
> PM-Regel-Liste nach Punkt 1 ab.

## Verwandt

- [[ICT Daily Range Session Timing]] — der Intraday-Fahrplan, in den dieses Modell greift
- [[ICT Macros & Leading Candles]], [[Silver Bullet Model]]
- [[NY PM Trend]] — die PM-Session-Regeln
- [[ORG (Opening Range Gap) & 1st Presented FVG]], [[Rejection Block]]
- [[Smart Money Concepts (SMC)]]
