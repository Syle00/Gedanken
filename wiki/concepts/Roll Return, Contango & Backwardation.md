---
tags: [concept, algo-methodology, futures, referenz]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[Algorithmic Trading - Winning Strategies and Their Rationale (Source)]]"]
---

# Roll Return, Contango & Backwardation

Die zentrale Besonderheit von Futures gegenüber Aktien — und laut
[[Algorithmic Trading - Winning Strategies and Their Rationale (Source)]] (Chan, Kap. 5 und 6)
die **Hauptursache für Momentum in Futures**.

## Die Zerlegung

```
Futures-Gesamtrendite  =  Spot-Rendite  +  Roll-Rendite
```

| Begriff | Bedeutung | Roll-Rendite | Kurvenform |
|---|---|---|---|
| **Backwardation** | ferne Kontrakte **billiger** als nahe | **positiv** | fallend |
| **Contango** | ferne Kontrakte **teurer** als nahe | **negativ** | steigend |

**Wichtig gegen ein verbreitetes Missverständnis:** Die Roll-Rendite wirkt **jeden Tag auf jeden
Kontrakt**. Sie ist *keine* Folge des Rollvorgangs — sie entsteht nicht dadurch, dass man den
Kontrakt wechselt.

Direkte Konsequenz: **Mean Reversion des Spotpreises erzeugt nicht zwangsläufig Mean Reversion
des Futurespreises.** Die Roll-Komponente kann den Spot-Effekt überlagern oder umkehren.

## Warum daraus Momentum wird

Chan nennt vier Ursachen für Momentum; die erste ist futures-spezifisch:

1. **Persistenz des Vorzeichens der Roll-Renditen** ← diese Seite
2. langsame Diffusion, Analyse und Akzeptanz neuer Information
3. erzwungene Käufe/Verkäufe verschiedener Fondstypen
4. Marktmanipulation durch Hochfrequenzhändler

Der Mechanismus: Das **Vorzeichen** der Roll-Rendite ändert sich selten — Futures bleiben über
lange Zeiträume in Contango oder Backwardation. Die **Spot**-Rendite dagegen wechselt Vorzeichen
und Größe schnell. Hält man einen Future lange genug, dominiert die mittlere Roll-Rendite die
mittlere Gesamtrendite — und **daraus** entsteht die serielle Korrelation der Gesamtrenditen.

Das erklärt zugleich, warum Futures-Momentum auf **langen** Zeitskalen auftritt (Monate) und
nicht intraday: die Roll-Rendite ist pro Tag zu klein und zu wenig volatil, um intraday zu wirken.

**Verifizierbare Vorhersage:** Momentum sollte genau bei den Kontrakten funktionieren, deren
Roll-Rendite betragsmäßig größer ist als ihre Spot-Rendite. Chan bestätigt das für BR, HG und TU —
und räumt eine Ausnahme ein, die er nicht erklären kann (C, Mais, hat die größte relative
Roll-Rendite, aber die Strategie funktioniert dort nicht).

## Das saubere Signal: Roll-Rendite statt Gesamtrendite

Wenn Momentum aus der Persistenz der Roll-Rendite kommt, sollte man direkt darauf handeln statt
auf die verrauschte Gesamtrendite:

```
Roll-Rendite (annualisiert) > +Schwelle   →  long
Roll-Rendite (annualisiert) < −Schwelle   →  short
sonst                                     →  flat
```

Ergebnis auf TU mit einer Schwelle von **3 % annualisierter Roll-Rendite**:

| Variante | Zeitraum | APR | Sharpe | max. Drawdown |
|---|---|---|---|---|
| Signal = 250-Tage-Gesamtrendite | 01.06.2004 – 11.05.2012 | 1,7 % | 1,04 | −2,5 % |
| **Signal = Roll-Rendite** | 02.01.2009 – 13.08.2012 | **2,5 %** | **2,1** | **−1,1 %** |

Sharpe verdoppelt, Drawdown halbiert — allein durch das sauberere Signal.

> **Zur Einordnung der niedrigen APR:** Sie ist auf den **Nominalwert** des Kontrakts bezogen
> (bei TU ca. $200.000), während die Margin nur ca. **$400** beträgt. Der Hebel ist also
> gewaltig — genau deshalb ist die Frage nach dem *richtigen* Hebel entscheidend, siehe
> [[Kelly-Formel & optimales Leverage (Chan)]].

## Roll-Rendite direkt abschöpfen: Future gegen ETF

Wenn Gesamtrendite = Spot + Roll, dann isoliert man die Roll-Rendite so:

```
Contango       (Roll < 0):   Underlying LONG   +  Future SHORT
Backwardation  (Roll > 0):   Underlying SHORT  +  Future LONG
```

Funktioniert, solange das Vorzeichen der Roll-Rendite stabil bleibt — was es üblicherweise tut.
Vorteil gegenüber dem reinen Halten des Futures: **kürzere Haltedauer und geringeres Risiko**, weil
man nicht darauf warten muss, dass sich die verrauschte Spot-Rendite herausmittelt.

**Praktisches Hindernis:** Das Underlying muss handelbar sein. ETFs, die den Rohstoff **physisch**
halten, gibt es nur bei Edelmetallen (Lagerkosten) — GLD hält echtes Gold.

**Warnbeispiel GLD/GC**, das zeigt, wie man sich verrechnet: Long GLD + Short GC brachte
03.08.2007–02.08.2010 **1,9 % p.a.** bei nur 0,8 % Drawdown. Sieht nach 5–6× Hebel attraktiv aus —
ist es aber nicht: Das Halten von GLD verursacht **Finanzierungskosten**, die im Backtestzeitraum
kaum von 1,9 % abwichen. Die Überschussrendite ist damit **praktisch null**.

**Funktionierende Variante über einen Produzenten-Proxy:** ETFs von Rohstoffproduzenten
kointegrieren oft mit dem Spotpreis, weil der Rohstoff einen wesentlichen Teil ihres Vermögens
ausmacht.

```
Short USO + Long XLE   waehrend CL in Contango
Long  USO + Short XLE  waehrend CL in Backwardation
→ APR 16 %, Sharpe ≈ 1  (26.04.2006 – 09.04.2012)
```

(USO statt CL, weil XLE und CL verschiedene Schlusszeiten haben — der Fallstrick aus
[[Futures-Datenaufbereitung & Backtesting-Fallstricke (Chan)]].)

## Kalenderspreads

Mean Reversion von Futures-**Kalenderspreads** hängt an der Mean Reversion der **Roll-Renditen**.
Chans Beispiel auf CL (12-Monats-Spread, Halbwertszeit 36 Tage, Haltedauer 3 Monate, Rollen
10 Tage vor Verfall des nahen Kontrakts): **APR 8,3 %, Sharpe 1,3** (02.01.2008–13.08.2012).

Zwei Einschränkungen:

- Bei Rohstoffen ist **Saisonalität** ausgeprägt — oft mean-revertieren nur Kalenderspreads
  bestimmter Monatskombinationen.
- Die zugrunde liegende Formel gilt nur für Futures, deren **Underlying ein handelbares Asset**
  ist. **VIX ist keines** — die Log-Preise der VX-Futures liegen nicht auf einer Geraden über der
  Restlaufzeit. Für VX bleibt nur die empirische Beobachtung: ein ADF-Test auf das Verhältnis
  back/front ist mit 99 % stationär, und die lineare Mean-Reversion-Strategie darauf (15 Tage
  Lookback) liefert **APR 17,7 %, Sharpe 1,5** (27.10.2008–23.04.2012) — davor deutlich
  schlechter, was auf einen Regimewechsel in der VIX-Dynamik um 2008 hindeutet.

## Intermarket-Spreads sind meist keine gute Idee

Chans systematische Suche verlief weitgehend ergebnislos:

- **Crack Spread** (long 3 CL, short 2 RB, short 1 HO — die Hedge-Ratios kommen daher, dass drei
  Barrel Rohöl etwa zwei Barrel Benzin und ein Barrel Heizöl ergeben): ADF-Test 20.05.2002 –
  04.05.2012 zeigt **keine** Mean Reversion; die lineare Strategie darauf verliert.
- **CL gegen BZ** 1:1, obwohl beide Rohöl sind: weit von stationär entfernt. BZ hat CL dauerhaft
  outperformt — US-Förderausweitung, Pipeline-Engpass in Cushing, Iran-Embargo 2012.

Die eine Ausnahme, die funktioniert, ist ein ungewöhnliches Paar: **Volatilitäts- gegen
Aktienindex-Futures.**

```
(5.11)  ES × 50 = −0,3906 × VX × 1.000 + $77.150
        Standardabweichung der Residuen: $2.047
```

Die Multiplikatoren sind Pflicht, weil ein Punkt bei VX **$1.000** und bei ES **$50** wert ist —
ohne sie beschreibt die Hedge Ratio nicht das Kontraktverhältnis. Ein Portfolio aus **0,3906
VX-Kontrakten long und 1 ES-Kontrakt long** ist stationär; eine Bollinger-artige Strategie darauf
liefert **APR 12,3 %, Sharpe 1,4** (29.07.2010–08.05.2012).

**Methodisch wichtiger als das Ergebnis:** Der Scatterplot ES gegen VX zeigt **zwei getrennte
Regime** (2004–Mai 2008 und August 2008–2012); im zweiten ist die Volatilität für ein gegebenes
Indexniveau merklich niedriger, die Bandbreite der Volatilitäten aber größer. Eine Regression
oder ein Johansen-Test über **beide** Regime hinweg wäre schlicht falsch. Chan rechnet deshalb
nur auf dem zweiten.

## Bezug zu diesem Projekt

Der Vault handelt **MNQ** — einen Aktienindex-Future. Damit:

- **Roll-Rendite ist vorhanden, aber klein.** Aktienindex-Futures stehen typischerweise in
  leichtem Contango (Finanzierungskosten minus Dividenden). Für die Intraday-Strategien des
  Projekts (Silver Bullet, Macro-Fenster) ist der Effekt vernachlässigbar — für jede Auswertung
  über Wochen/Monate nicht, siehe [[Seasonal Tendency (Eigene Daten, laufend)]].
- **Der Regime-Befund ist übertragbar und wichtig:** Vor jeder Regression oder Kointegration über
  einen längeren Zeitraum prüfen, ob mehrere Regime vorliegen. Der Vault hat dafür bereits einen
  Anknüpfungspunkt in [[Makro-FRED-Zusammenhaenge (Eigene Daten, laufend)]] (VIX-Korrelation
  −0,743 gegen MNQ) — dieselben zwei Größen, die Chan hier untersucht.
- Der VX/ES-Zusammenhang ist der einzige im Buch bestätigte Intermarket-Spread und betrifft mit
  ES direkt einen der drei im Projekt hinterlegten Punktwerte (`pnl.py`: MNQ $2, NQ $20, ES $50).

Weiterführend: [[Momentum-Ursachen & Opening-Gap-Strategie]],
[[Futures-Datenaufbereitung & Backtesting-Fallstricke (Chan)]],
[[Halbwertszeit der Mean Reversion & Kointegration (Chan)]].
