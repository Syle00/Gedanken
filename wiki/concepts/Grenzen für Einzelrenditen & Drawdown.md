---
tags: [concept, algo-methodology, validation, risiko, drawdown]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[Testing and Tuning Market Trading Systems (Source)]]"]
---

# Grenzen für Einzelrenditen & Drawdown

Nicht der *Mittelwert* künftiger Renditen (dafür siehe
[[Konfidenzgrenzen für Renditen (t-Test, Bootstrap, BCa)]]), sondern **die einzelnen künftigen
Werte selbst** — und speziell der schlimmste anzunehmende Drawdown. Aus
[[Testing and Tuning Market Trading Systems (Source)]] (Kap. 6).

Der Hauptzweck ist **Überwachung im Livebetrieb**: eine Untergrenze für die Monats-/
Quartalsrendite, unter die das System im Normalbetrieb nur mit Wahrscheinlichkeit `p` fällt.
Fällt es öfter darunter, degradiert es.

## Untergrenze aus empirischen Quantilen

Verfahren: `n` OOS-Renditen aufsteigend sortieren, Fehlerrate `p` wählen (typisch 0,05–0,1),
`m = n·p` (konservativ) bzw. `m = (n+1)·p` (unverzerrt) bilden, abrunden — die `m`-kleinste
Rendite ist die Untergrenze. Für eine Obergrenze analog die `m`-größte.

Datenbedarf: **mindestens ~100 Renditen, besser mehrere hundert.** Bei Monatsrenditen heißt das
über zehn Jahre OOS. Der Kompromiss ist unangenehm: kürzere Renditeperioden liefern mehr
Datenpunkte, aber höhere Streuung und damit so niedrige Grenzen, dass sie nutzlos werden.

## Warum die Grenze selbst unsicher ist

Die eigene OOS-Sammlung ist mit Sicherheit optimistisch **oder** pessimistisch verzerrt (siehe
den „Unbiased"-Abschnitt in [[Training Bias & Selection Bias]]). Also ist auch die berechnete
Grenze zu hoch oder zu tief. Beide Richtungen sind gefährlich, aber unterschiedlich:

- **Grenze zu hoch** → wird häufiger verletzt als die gewünschten `p`, man vermutet Degradation,
  wo keine ist. Der zugehörige „pessimistische" `q > p` beantwortet: *Wie wahrscheinlich ist es,
  dass meine 0,1-Grenze in Wahrheit die 0,15-Grenze ist?*
- **Grenze zu tief** → wird seltener verletzt, echte Degradation wird **nicht erkannt**. Der
  „optimistische" `q < p` beantwortet die Gegenfrage.

Berechnet wird beides über die **unvollständige Beta-Verteilung**: die Wahrscheinlichkeit, dass
der `m`-kleinste von `n` Werten über dem `q`-Quantil liegt, ist `1 − I_q(m, n−m+1)`
(bei Masters `orderstat_tail()`). Umgekehrt liefert `quantile_conf()` zu einer vorgegebenen
kleinen Wahrscheinlichkeit den zugehörigen `q`.

Zahlenbeispiel (n=200, p=0,1, also `m`=20): mit `q`=0,07 beträgt die Wahrscheinlichkeit 0,0692,
mit `q`=0,12 beträgt sie 0,1638. Umgekehrt bei vorgegebenem `p_of_q`=0,05: optimistisches
`q`=0,0673, pessimistisches `q`=0,1363 — es gibt also je 5 % Chance, dass die wahre Fehlerrate
unter 6,7 % bzw. über 13,6 % liegt statt bei den gewünschten 10 %.

**Obergrenzen sind hier ausdrücklich nützlich** — anders als beim Mittelwert. Ein System
degradiert nämlich nicht nur, indem es zu schlechte Trades produziert, sondern auch, indem die
guten ausbleiben. Deshalb setzt man für die Obergrenze eine **große** „Fehlerrate" an (z.B.
`p`=0,4: 40 % der künftigen Renditen sollten die Obergrenze übertreffen) und wird misstrauisch,
wenn dieser Anteil deutlich sinkt.

Masters' `BND_RET`-Lauf auf OEX (Quartalsrenditen, MA-Crossover): 1,021 % annualisiert — „a
mighty poor trading system". 10 % der künftigen Quartale sollten schlechter als −38,942 %
annualisiert sein, 40 % besser als +9,043 %. Bei nur 124 Renditen sind die Grenzen aber
eingestandenermaßen wackelig.

## Drawdown: der naive Bootstrap ist gefährlich falsch

Die intuitive und **falsche** Argumentationskette:

1. Die Returns sind OOS und damit unverzerrt.
2. *Also* repräsentieren sie die Zukunft fair. ← **hier bricht es**
3. Drawdown hängt von der Reihenfolge ab.
4. Die Zukunft unterscheidet sich nur durch Zusammensetzung und Reihenfolge.
5. Also: mit Zurücklegen aus den OOS-Returns ziehen, Drawdown je Stichprobe berechnen, das
   5 %-Quantil ist die 95 %-Drawdown-Grenze.

Schritt 2 ist der Fehler: die OOS-Stichprobe **ist** verzerrt, man weiß nur nicht in welche
Richtung. Der naive Bootstrap ignoriert diese Variationsquelle völlig. Und die Verzerrung wirkt
beim Drawdown **asymmetrisch** — optimistische Stichproben schaden mehr, als pessimistische
nützen.

## Der korrekte Doppel-Bootstrap

```
für 'outer' Wiederholungen:
    äußere Bootstrap-Stichprobe aus den OOS-Returns ziehen (Größe = ganze OOS-Menge)
    für 'inner' Wiederholungen:
        innere Stichprobe daraus ziehen (Größe = n_trades der Drawdown-Periode)
        DD_inner[inner] = Drawdown dieser inneren Stichprobe
    DD_inner sortieren; DD_outer[outer] = DD_inner[ DD_conf · inner ]
DD_outer sortieren
Bound = DD_outer[ Bound_conf · outer ]
```

Zwei Konfidenzen, die man auseinanderhalten muss:

- `DD_conf` — Wahrscheinlichkeit, dass ein künftiger Drawdown die Grenze **nicht** überschreitet
  (z.B. 0,9).
- `Bound_conf` — Konfidenz, dass die berechnete Grenze mindestens so groß ist wie die wahre,
  unbekannte `DD_conf`-Grenze (z.B. 0,7).

Also: *„Mit 70 % Sicherheit liegt die Grenze, die zu 90 % nicht überschritten wird, bei höchstens
69 %."* Eine Grenze für eine Grenze. Faustregel des Autors: bei extremen `DD_conf` (0,99 / 0,999)
`Bound_conf` anheben, bei Routine-Drawdowns (0,9) reichen 0,7.

Wichtig zur Auslegung: die Grenze gilt für **einen im Voraus festgelegten Zeitraum** (typisch das
kommende Jahr) und nur für Equity-Veränderungen *innerhalb* dieses Zeitraums — nicht für „jemals"
und nicht für die Fortsetzung eines laufenden Drawdowns.

Der Drawdown wird in Prozent ausgedrückt über `100·(1 − exp(−dd))`, weil die Returns Log-Größen
sind.

## Wie schlimm der Fehler ist (DRAWDOWN-Experimente, Gewinnwahrscheinlichkeit 0,6)

Jede Zelle: Faktor, um den die **tatsächliche** Verletzungsrate die angenommene übersteigt.
1,0 wäre perfekt; > 1,0 ist gefährlich (Drawdown tritt öfter ein als gedacht), < 1,0 nur
konservativ.

| p | OOS | DD-Periode | naiv | korrekt (0,5) | korrekt (0,6) | korrekt (0,8) |
|---|---|---|---|---|---|---|
| 0,001 | 63 | 63 | **13,65** | 4,49 | 3,42 | 1,64 |
| 0,01 | 63 | 63 | 4,29 | 1,74 | 1,37 | 0,71 |
| 0,05 | 63 | 63 | 2,16 | 2,15 | 1,65 | 0,85 |
| 0,10 | 63 | 63 | 1,66 | 1,66 | 1,31 | 0,72 |
| 0,001 | 252 | 252 | 5,84 | 1,81 | 1,35 | 0,59 |
| 0,01 | 252 | 252 | 2,55 | 1,02 | 0,80 | 0,41 |
| 0,05 | 252 | 252 | 1,62 | 1,62 | 1,26 | 0,64 |
| 0,10 | 252 | 252 | 1,36 | 1,37 | 1,10 | 0,61 |
| 0,001 | 2520 | 252 | 1,54 | 0,79 | 0,68 | 0,45 |
| 0,01 | 2520 | 252 | 1,16 | 0,76 | 0,68 | 0,51 |
| 0,05 | 2520 | 252 | 1,06 | 1,06 | 0,95 | 0,72 |
| 0,10 | 2520 | 252 | 1,04 | 1,03 | 0,94 | 0,75 |

Ablesbar:

- Der naive Bootstrap **unterschätzt in jeder einzelnen Zeile** die Verletzungsrate — nie
  konservativ.
- Mit 63 OOS-Returns und p=0,001 unterschätzt er Katastrophen-Drawdowns um **Faktor 13,65**.
- Mit 2.520 OOS-Returns (10 Jahre Tagesdaten) und moderatem p ist er brauchbar (1,04–1,16) —
  das ist die einzige Konstellation, in der man ihn (z.B. innerhalb einer Optimierungsschleife,
  wo der korrekte Doppel-Bootstrap mit ~10⁸ Iterationen zu teuer ist) verantworten kann.
- Der korrekte Algorithmus mit `Bound_conf`=0,8 ist außer im Extremfall (63/0,001) durchweg
  konservativ, und zwar ohne übertrieben zu werden (schlechtester Wert 0,41).

## Bezug zu diesem Projekt

`algo/validate.py` liefert bereits Monte-Carlo-Drawdown-Verteilungen aus dem Mischen realer
Trades — **das ist genau der naive Bootstrap aus Schritt 5 oben.** Bei der aktuellen
Datenbasis (wenige Dutzend Trades, `raw/marktdaten/` wächst erst seit August 2026) fällt das in
die schlechteste Zeile der Tabelle. Die dort berichteten Drawdown-Zahlen sind also **zu
optimistisch**, und zwar möglicherweise um eine Größenordnung. Das ist vor jeder Kapitalfreigabe
relevant, siehe Roadmap-Stufe 5/6 in [[Algo-Trading: Arbeitsstandards]].
