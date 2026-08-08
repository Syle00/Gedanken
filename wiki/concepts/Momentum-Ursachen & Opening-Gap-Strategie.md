---
tags: [concept, algo-methodology, momentum, futures, referenz]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[Algorithmic Trading - Winning Strategies and Their Rationale (Source)]]"]
---

# Momentum-Ursachen & Opening-Gap-Strategie

Aus [[Algorithmic Trading - Winning Strategies and Their Rationale (Source)]] (Chan, Kap. 6 und
7). Die **Opening-Gap-Strategie** ist die für dieses Projekt direkt anschlussfähigste Regel des
ganzen Buches — eine Futures-Breakout-Regel am Handelsstart.

## Die fünf Ursachen von Momentum

| # | Ursache | Zeitskala |
|---|---|---|
| 1 | Persistenz des Vorzeichens der **Roll-Renditen** (nur Futures) | Monate — siehe [[Roll Return, Contango & Backwardation]] |
| 2 | **langsame Diffusion**, Analyse und Akzeptanz neuer Information | Tage bis intraday |
| 3 | **erzwungene** Käufe/Verkäufe von Fonds | intraday bis Tage |
| 4 | **Manipulation** durch Hochfrequenzhändler | Sekunden |
| 5 | **Auslösen von Stop-Ordern** (nur kurzfristig) | Minuten |

Ursache 1 wirkt **nicht** intraday: Größe und Volatilität der Roll-Rendite sind dafür zu klein.
Alle anderen vier wirken auch auf kurzen Zeitskalen — deshalb Chans Präferenz für **intraday**
Momentum: kürzere Haltedauer bedeutet mehr unabhängige Signale, höhere Sharpe Ratio und höhere
statistische Signifikanz, und Intraday-Momentum litt nicht unter der mehrjährigen Momentum-Baisse
nach 2008.

## Zeitreihen-Momentum messen

Momentum bedeutet: vergangene Renditen sind **positiv** mit künftigen korreliert. Man berechnet
also schlicht den Korrelationskoeffizienten samt P-Wert — aber über ein **Gitter** aus Lookback-
und Haltedauer, weil das Optimum selten bei gleichen Zeiträumen liegt.

> **Pflichtdetail: keine überlappenden Daten verwenden.**
> ```
> Lookback ≥ Haltedauer :  um die HALTEDAUER weiterschieben
> Lookback < Haltedauer :  um den LOOKBACK weiterschieben
> ```
> Sonst sind die Renditepaare nicht unabhängig und die P-Werte wertlos — derselbe Fehlertyp wie
> die Varianz-Inflation in [[Walk-Forward Guard Buffer & Varianz-Inflation]].

Ergebnis für TU (2-jährige US-Treasury-Note, CME), Auszug:

| Lookback | Haltedauer | Korrelation | P-Wert |
|---|---|---|---|
| 25 | 1 | −0,0140 | 0,5353 |
| 60 | 10 | 0,1718 | **0,0169** |
| 60 | 25 | 0,2592 | **0,0228** |
| 250 | 10 | 0,1784 | **0,0185** |
| 250 | 25 | 0,2719 | **0,0238** |
| 250 | 60 | 0,4245 | **0,0217** |
| 250 | 120 | 0,5112 | 0,0617 |
| 250 | 250 | 0,4873 | 0,3269 |

**Es gibt einen Zielkonflikt** zwischen Korrelationshöhe und P-Wert: lange Haltedauern korrelieren
stärker, haben aber wegen weniger unabhängiger Beobachtungen schlechtere P-Werte. Die besten
Kompromisse sind (60, 10), (60, 25), (250, 10), (250, 25), (250, 60), (250, 120) — und aus
Trader-Sicht ist die **kürzeste** Haltedauer vorzuziehen, weil sie die beste Sharpe Ratio liefert.

**Alternative:** statt der Renditen die **Vorzeichen** der Renditen korrelieren — passend, wenn
nur „Aufwärts folgt auf Aufwärts" interessiert und die Größe egal ist. Ergebnis war hier kaum
verschieden: (60, 10), (250, 10), (250, 25).

**Warnung zum Hurst-Exponenten:** Für dieselbe TU-Reihe ergab sich H = 0,44 und der
Variance-Ratio-Test konnte den Random Walk **nicht** verwerfen — obwohl die Korrelationstabelle
deutliches Momentum zeigt. Auflösung: Die Reihe hat Momentum **und** Mean Reversion auf
**verschiedenen Zeitskalen**; Hurst und Variance Ratio mitteln darüber hinweg und können den
spezifischen Zeitrahmen nicht auflösen. **Beide Tests ersetzen die Gitteranalyse nicht.**

## Zeitreihen-Momentum-Strategien auf Futures

Grundregel (nach Moskowitz/Yao/Pedersen): kaufe bei positiver 12-Monats-Rendite, halte 1 Monat.
Chans Modifikation: **täglich** entscheiden und jeweils 1/25 des Kapitals einsetzen, statt
monatlich alles.

| Symbol | Lookback | Haltedauer | APR | Sharpe | max. Drawdown |
|---|---|---|---|---|---|
| BR (CME) | 100 | 10 | 17,7 % | 1,09 | −14,8 % |
| HG (CME) | 40 | 40 | 18,0 % | 1,05 | −24,0 % |
| TU (CBOT) | 250 | 25 | 1,7 % | 1,04 | −2,5 % |

Weitere Einstiegssignale außer „Vorzeichen der Rendite": N-Tage-Hoch, Überschreiten des
N-Tage-(exponentiellen) gleitenden Durchschnitts, Überschreiten des oberen Bollinger-Bandes, mehr
Auf- als Abtage in einer gleitenden Periode.

**Alexander-Filter** (Fama & Blume, 1966): kaufe, wenn die Tagesrendite um mindestens x %
steigt; verkaufe und gehe short, wenn der Preis um mindestens x % von einem späteren Hoch fällt.

**Kombination Momentum + Mean Reversion** kann besser sein als jedes für sich. Chans CL-Beispiel:

```
Kaufe am Schluss, wenn Preis < Preis vor 30 Tagen  UND  Preis > Preis vor 40 Tagen
Umgekehrt fuer Short. Sonst flat.
→ APR 12 %, Sharpe 1,1
```

Das Hinzufügen eines Mean-Reversion-Filters zur reinen Momentum-Regel brachte zusätzlich IBX, KT,
SXF, US, CD, NG und W in die Tabelle und verbesserte auch die bestehenden Einträge.

Chans eigener Vorbehalt: Wegen der langen Haltedauern gibt es in den begrenzten Testdaten wenige
Trades — **Data-Snooping-Risiko**. Der echte Test bleibt Out-of-Sample.

## Die Opening-Gap-Strategie (Futures)

**Die praktisch relevanteste Regel des Buches für dieses Projekt.** Sie ist das *Spiegelbild* der
Buy-on-Gap-Regel für Aktien: Aktien mean-revertieren nach einem Gap, Futures und manche Währungen
laufen **weiter**.

```
Vorbereitung:
    stdret_90d = 90-Tage-gleitende Standardabweichung der Close-zu-Close-Tagesrenditen
                 (um einen Tag versetzt, damit kein Lookahead entsteht)
    entryZscore = 0,1

Einstieg am Open:
    Open  >  Vortages-HIGH × (1 + entryZscore × stdret_90d)   →  LONG
    Open  <  Vortages-LOW  × (1 − entryZscore × stdret_90d)   →  SHORT

Ausstieg: am selben Tag zum Close.
```

```python
std90 = pd.Series(close).pct_change().rolling(90).std().shift(1)
longs  = open_ >  high.shift(1) * (1 + 0.1 * std90)
shorts = open_ <  low.shift(1)  * (1 - 0.1 * std90)
pos = np.where(longs, 1, np.where(shorts, -1, 0))
ret = pos * (close - open_) / open_      # Einstieg Open, Ausstieg Close
```

Zwei Details, die man leicht falsch macht: Die Schwelle bezieht sich auf **Hoch bzw. Tief des
Vortages**, nicht auf dessen Schluss. Und `entryZscore = 0,1` ist sehr klein — es geht um jedes
Gap über das Vortagesextrem hinaus, nicht um große Gaps.

**Ergebnisse:**

| Instrument | Zeitraum | APR | Sharpe |
|---|---|---|---|
| **FSTX** (Dow Jones STOXX 50, Eurex) | 16.07.2004 – 17.05.2012 | **13 %** | **1,4** |
| GBPUSD (Close 17:00 ET, Open 05:00 ET = London-Open) | 23.07.2007 – 20.02.2012 | 7,2 % | 1,3 |

Für Devisen muss man „Open" und „Close" also **selbst definieren**; die natürlichste Lücke ist
Freitag 17:00 bis Sonntag 17:00 ET, wenn die meisten Devisenmärkte geschlossen sind.

**Warum Gaps Momentum auslösen** — und das ist der inhaltlich interessante Teil: Die lange
handelsfreie Periode führt dazu, dass der Eröffnungskurs deutlich vom Schlusskurs abweicht.
Dadurch werden **Stop-Orders auf ganz verschiedenen Preisniveaus gleichzeitig ausgelöst**. Deren
Ausführung erzeugt Momentum, weil ein **Kaskadeneffekt** weitere, noch weiter entfernte Stops
mitreißt. Zusätzlich können über Nacht relevante Nachrichten aufgelaufen sein.

## Weitere Intraday-Momentum-Quellen

**Post-Earnings Announcement Drift (PEAD).** Seit 1968 bekannt und immer noch nicht wegarbitriert,
wenn auch verkürzt. Regel: am Open nach einer Ankündigung, die **nach** dem Vortagesschluss und
**vor** dem heutigen Open erfolgte, kaufen bei sehr positiver bzw. shorten bei sehr negativer
Overnight-Rendite; zum selben Close glattstellen. Schwelle: `|retC2O| ≥ 0,5 × stdC2O` (90 Tage).
S&P-500-Universum, 03.01.2011–24.04.2012: **APR 6,7 %, Sharpe 1,5**.

Bemerkenswert: Die Regel braucht **keine Interpretation** der Zahlen — weder ob die Earnings
„gut" sind noch ob sie über den Analystenerwartungen liegen. Der Markt sagt es einem. Und: Über
Nacht halten bringt **negative** Zusatzrenditen; der Drift ist auf intraday geschrumpft, während
Studien vor 10–20 Jahren mehrtägige Drifts fanden.

**Andere Ereignisse mit Drift:** Earnings Guidance, Analystenratings, Same-Store-Sales, Airline
Load Factors, M&A (rein technisch ca. 3 % APR — wobei entgegen der landläufigen Meinung der Kurs
des **Übernahmeziels** stärker fällt als der des Käufers), Indexzusammensetzungsänderungen.

**Makro-Ereignisse:** Chan fand für FOMC-Zinsentscheidungen und CPI **kein** signifikantes
Momentum in EURUSD. Clare & Courtenay fanden dagegen für britische Makrodaten und
Bank-of-England-Entscheidungen Momentum in GBPUSD für mindestens 10 Minuten (Daten bis 1999).

**Gehebelte ETFs.** Ein 3× gehebelter ETF muss nahe dem Schluss rebalancieren — bei fallendem
Index verkaufen, bei steigendem kaufen (siehe die Zwangslogik in
[[Kelly-Formel & optimales Leverage (Chan)]]). Das erzeugt Momentum im Basiswert. Testregel:
DRN kaufen, wenn die Rendite vom Vortagesschluss bis 15 Minuten vor Schluss > 2 % ist, verkaufen
bei < −2 %, Glattstellung zum Schluss. **APR 15 %, Sharpe 1,8** (12.10.2011–25.10.2012). Ein
1-%-Zug im SPX erfordert laut Cheng/Madhavan Umsätze von rund **17 % des
Market-on-Close-Volumens** — mit entsprechendem Marktimpact. Wichtig: Long- **und** Short-ETFs
kaufen bei steigendem Markt, der Effekt addiert sich also.

**Stop Hunting.** Sind Unterstützungs- oder Widerstandsniveaus einmal durchbrochen, laufen die
Kurse eine Weile weiter (Osler, 2000/2001, für Devisen) — wegen der dort geballten Stop-Orders.
Solche Niveaus sind entweder die von Banken/Brokern täglich veröffentlichten **oder schlicht
runde Zahlen** in der Nähe des aktuellen Kurses. Hochfrequenzhändler erzeugen den Durchbruch
teils künstlich, um die Kaskade auszulösen.

> Das ist derselbe Mechanismus, den die ICT-Konzepte im Vault als **Liquidity Sweep** beschreiben
> — siehe [[Open Float & Liquidity Pools]], [[Turtle Soup]],
> [[Market Maker Trap - False Breakout]]. Chan liefert dafür die akademische Referenz und die
> Formulierung als Momentum-Ursache.

## Bezug zu diesem Projekt

**Die Opening-Gap-Regel ist unmittelbar backtestbar** — sie braucht nur Tages-OHLC aus
`raw/marktdaten/`, hat **einen** Parameter (`entryZscore`), keinen Lookahead (die
Standardabweichung ist um einen Tag versetzt) und eine feste Haltedauer bis zum Schluss. Damit
erfüllt sie die Anforderungen aus [[Algo-Trading: Arbeitsstandards]] an eine testbare These
praktisch out of the box.

Inhaltlich überschneidet sie sich mit mehreren ICT-Konzepten des Vaults, die dieselbe Tageszeit
behandeln — [[ORG (Opening Range Gap) & 1st Presented FVG]], [[Judas Swing]],
[[Midnight Opening Range]] — sagt aber etwas **anderes** voraus: Chans Futures-Regel erwartet
**Fortsetzung** des Gaps, während die ICT-Konzepte überwiegend eine **Manipulation mit
anschließender Umkehr** beschreiben. Das ist ein sauber falsifizierbarer Gegensatz, der sich auf
MNQ direkt messen lässt.

Zusätzlich anschlussfähig: die **Gitteranalyse** (Lookback × Haltedauer mit nicht überlappenden
Renditepaaren) ist ein Werkzeug, das `algo/` bisher nicht hat, aber mit
`algo/backtest_common.py` leicht zu bauen wäre — und die Warnung, dass Hurst-Exponent und
Variance-Ratio-Test das Ergebnis **verfehlen** können, ist eine direkte Ergänzung zu
[[Mean-Reversion-Tests (ADF, Hurst-Exponent, Kointegration)]].
