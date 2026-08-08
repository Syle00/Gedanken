---
tags: [concept, algo-methodology, marktdaten, futures, referenz]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[Algorithmic Trading - Winning Strategies and Their Rationale (Source)]]"]
---

# Futures-Datenaufbereitung & Backtesting-Fallstricke (Chan)

Der Teil aus [[Algorithmic Trading - Winning Strategies and Their Rationale (Source)]] (Chan,
Kap. 1), der `raw/marktdaten/` unmittelbar betrifft. Grundregel des Kapitels: **fast jeder
Fallstrick bläht die Backtest-Performance auf** statt sie zu drücken — das macht sie besonders
gefährlich.

## Continuous Contracts: die Back-Adjustment-Falle

Futures haben Verfallstermine, eine Strategie auf „MNQ" handelt also über die Zeit viele
verschiedene Kontrakte. Datenanbieter liefern deshalb *continuous contracts*. Der erste Schritt
dabei — die Front-Month-Preise aneinanderhängen — erzeugt aber **Preissprünge am Rolltag** und
damit falsche Renditen.

```
p(T)     Schlusskurs des Frontkontrakts am Tag T
p(T+1)   Schlusskurs DESSELBEN Kontrakts am Tag T+1
q(T+1)   Schlusskurs des naechsten Kontrakts am Tag T+1
T+1      = Rolltag

KORREKT:      P&L    = p(T+1) − p(T)
              Rendite = (p(T+1) − p(T)) / p(T)

UNBEREINIGT:  die Reihe zeigt p(T) bei T und q(T+1) bei T+1
              ⟹ faelschlich  q(T+1) − p(T)   bzw.  (q(T+1) − p(T))/p(T)
```

**Die zwei Bereinigungsverfahren — und warum man nur eines haben kann:**

```
PREIS-Back-Adjustment:
    zu jedem Preis p(t) mit t ≤ T addiere  (q(T+1) − p(T+1))
    ⟹ P&L bei T+1 korrekt:  q(T+1) − (p(T) + q(T+1) − p(T+1)) = p(T+1) − p(T)   ✔
    ⟹ Rendite dann FALSCH:  (p(T+1) − p(T)) / (p(T) + q(T+1) − p(T+1))          �’

RENDITE-Back-Adjustment:
    multipliziere jeden Preis p(t) mit t ≤ T mit  q(T+1)/p(T+1)
    ⟹ Rendite korrekt, P&L falsch
```

> **Man kann nicht beides haben.** Wer die Bequemlichkeit einer durchgehenden Reihe will, muss
> sich für **eine** Kennzahl entscheiden — P&L **oder** Rendite. Nur wer gegen die einzelnen
> Kontrakte backtestet und das Rollen selbst abbildet, bekommt beide gleichzeitig korrekt.

**Welches Verfahren wann:**

| Situation | Verfahren |
|---|---|
| Signale aus **Preisdifferenzen** zweier Kontrakte (Spreads) | **Preis**-Back-Adjustment — sonst ist die Differenz falsch und erzeugt falsche Signale |
| **Kalenderspreads** (gleiches Underlying, verschiedene Verfallstermine) | **Preis** — hier ist die Bereinigung noch wichtiger: der Spread ist eine kleine Zahl gegenüber dem Kurs eines Beins, ein Rollfehler ist also prozentual riesig |
| Signale aus **Preisverhältnissen** | **Rendite**-Back-Adjustment |

**Nebenwirkung des Preisverfahrens:** In ferner Vergangenheit können die Preise **negativ**
werden. Übliche Abhilfe: eine Konstante auf alle Preise addieren.

Anbieterverhalten laut Buch: `csidata.com` nutzt ausschließlich Preis-Back-Adjustment mit
optionaler additiver Konstante; `tickdata.com` lässt die Wahl, bietet aber keine Konstante gegen
negative Preise.

## Settlement- statt Schlusskurs

Der von Datenanbietern gelieferte Tagesschlusskurs eines Futures ist **normalerweise der
Settlement-Preis**, nicht der letzte gehandelte Kurs. Wichtig:

- Ein Future hat **jeden Tag** einen Settlement-Preis (von der Börse festgestellt), auch wenn er
  an dem Tag gar nicht gehandelt wurde.
- Wurde gehandelt, weicht der Settlement-Preis im Allgemeinen trotzdem vom letzten Trade ab.

**Regel: Settlement-Preis verwenden.** Wer live nahe dem Schluss handelt, kommt diesem Kurs am
nächsten; der letzte aufgezeichnete Trade kann Stunden alt sein.

Besonders kritisch bei **Paar-/Spread-Strategien**: Settlement-Preise sind garantiert
gleichzeitig (bei gleichem Underlying und damit gleicher Schlusszeit). Bildet man den Spread aus
letzten Trades, stammen die beiden Preise womöglich aus **weit auseinanderliegenden Zeitpunkten**
— das erzeugt unrealistisch große Spreads, darauf falsche Trades und unrealistisch hohe
Backtest-Gewinne.

**Intraday-Spreads:** Aus demselben Grund darf man den Spread nicht aus den Last-Prices der
einzelnen Beine je Bar bilden — bei illiquiden Kontrakten liegen die zugehörigen Transaktionen
zeitlich weit auseinander. Nötig sind entweder Bid/Ask beider Kontrakte oder die Intraday-Daten
des **Spreads selbst**, sofern die Börse ihn nativ führt.

**Intermarket-Spreads:** Kontrakte an verschiedenen Börsen haben verschiedene Schlusszeiten —
Schlusskurse dürfen dann gar nicht zu einem Spread verrechnet werden. Chans Beispiel: statt
Gold-Future GC (Settlement 13:30 ET) gegen den Goldminen-ETF GDX (16:00 ET) besser GLD gegen GDX,
beide an der Arca mit derselben Schlusszeit.

## Datenfehler treffen Mean Reversion und Momentum gegensätzlich

```
Echte Kurse 11:00 / 11:01 / 11:02:   100 / 100 / 100
Fehlerhaft aufgezeichnet:            100 / 110 / 100
```

| Strategieart | Wirkung im Backtest |
|---|---|
| **Mean Reversion** | shortet bei 110, deckt bei 100 → **fiktiver Gewinn von 10**. Performance wird **aufgebläht** — gefährlich. |
| **Momentum** | kauft bei 110, wird bei 100 ausgestoppt → Verlust. Performance wird **gedrückt** — ärgerlich, aber ungefährlich. |

Intraday-Daten sind besonders betroffen, weil sie um Größenordnungen mehr Gelegenheiten für
solche Fehler bieten. Seriöse Anbieter verarbeiten die **cancel-and-correct-Codes** der Börsen.

**Im Livebetrieb** lösen dieselben Fehler echte Verluste aus: Ein falscher Bid von $110 lässt das
Ausführungssystem eine Market-Sell-Order senden, die dann zu $100 gefüllt wird — der Bid von $110
existierte nie.

**Bei Spreads potenziert sich der Fehler**, weil der Spread eine kleine Differenz großer Zahlen
ist:

```
X Bid = $100,  Y Ask = $105   →  Spread $5   (zu klein zum Handeln)
Y Ask faelschlich $106        →  Spread $6   = +20 % Fehler  ⟹  Fehltrade
```

Chan berichtet, dass er dieses Problem live erlebte: ein Broker-Datenfeed löste regelmäßig
unerklärliche Verlusttrades aus, die verschwanden, als er auf einen Drittanbieter-Feed wechselte.

## Statistische Signifikanz: drei verschiedene Nullhypothesen

Chan zeigt am selben Beispiel (TU-Momentum: kaufe bei positiver 12-Monats-Rendite, halte 1 Monat)
drei Wege — mit **drastisch verschiedenen** Ergebnissen:

| # | Nullhypothese | Rechenweg | Ergebnis |
|---|---|---|---|
| 1 | Tagesrenditen sind gaußverteilt mit Mittelwert 0 | `mean(ret)/std(ret)·√n` gegen kritische Werte | Teststatistik **2,93** → H₀ mit > 99 % verworfen |
| 2 | Der Markt hat dieselben ersten vier Momente, aber **keine** Korrelationen | 10.000 simulierte Marktreihen per Pearson-System, Strategie darauf laufen lassen | **1.166 von 10.000** besser → H₀ nur mit **88 %** verworfen |
| 3 | Die Einstiegszeitpunkte sind zufällig (gleiche Anzahl Long/Short, gleiche Haltedauer) | 100.000 Permutationen der Entry-Tage über die **echte** Preisreihe | **0 von 100.000** besser → deutlichste Ablehnung |

Kritische Werte für `√n × tägliche Sharpe Ratio` (Test 1):

```
p-Wert          0,10    0,05    0,01    0,001
krit. Wert     1,282   1,645   2,326   3,091
```

**Die Lehre:** Die Nullhypothese ist **nicht eindeutig**, und verschiedene Nullhypothesen liefern
verschiedene Signifikanzaussagen. Test 2 fiel hier am schwächsten aus — was selbst
aufschlussreich ist: *jede* Renditeverteilung mit hoher Kurtosis begünstigt Momentum-Strategien,
der Erfolg lag also teilweise an der Verteilungsform und nicht an echter serieller Korrelation.

Und der prinzipielle Vorbehalt: Berechnet wird `P(R|H₀)` — die Wahrscheinlichkeit der
Teststatistik unter der Nullhypothese. Wissen will man `P(H₀|R)`. Die beiden sind selten gleich.
(Ausführlicher, mit derselben Warnung und dem Hunde-Beispiel:
[[Konfidenzgrenzen für Renditen (t-Test, Bootstrap, BCa)]].)

Test 3 ist strukturell derselbe Gedanke wie
[[Monte Carlo Permutation Test (MCPT)]] — nur werden dort die **Bars** permutiert statt der
Entry-Zeitpunkte.

## Wann man einen Backtest gar nicht erst anfängt

Chans Ausschlusskriterien, jeweils mit Begründung:

| Beschreibung | Warum nicht backtesten |
|---|---|
| 30 % APR, **Sharpe 0,3**, max. Drawdown-**Dauer 2 Jahre** | Kaum ein Trader hält zwei Jahre unter Wasser durch. Niedrige Sharpe + lange Drawdown-Dauer = inkonsistent; die hohe Rendite ist vermutlich Data-Snooping-Bias, und die Strategie besteht keinen Cross-Validation-Test. |
| Long-only Crude Oil, 20 % in 2007, Sharpe 1,5 | Buy-and-Hold des Frontkontrakts brachte im selben Jahr **47 %** bei Sharpe 1,7. **Immer gegen den passenden Benchmark messen** — bei Long-only ist das die Information Ratio, nicht die Sharpe Ratio. |
| „10 billigste Aktien kaufen", 388 % in 2001 | Survivorship Bias: ohne delistete Aktien wählt die Regel die zufälligen Überlebenden. |
| Neuronales Netz mit **100 Knoten**, Sharpe 6 | Parameterzahl proportional zur Knotenzahl — mit 100 Parametern lässt sich jede Zeitreihe fitten. |
| HFT auf ES, 200 % APR, Sharpe 6, Haltedauer 50 s | Ergebnis hängt an Ordertypen, Ausführung und Marktmikrostruktur. Selbst mit vollem Orderbuch bleibt die Reaktion anderer Teilnehmer offen — eine Art „Heisenberg-Unschärfe": das Platzieren der Order verändert das Verhalten der anderen. |

## Bezug zu diesem Projekt

**Direkt einschlägig für `raw/marktdaten/`.** Zwei Punkte, die im Vault bisher nirgends geprüft
sind:

1. **Welche Back-Adjustment-Methode liegt den TradingView-Exporten und dem
   `algo/fetch_yfinance.py`-Nachlad zugrunde?** yfinance liefert für `MNQ=F` eine fortlaufende
   Reihe — ob preis- oder renditebereinigt (oder gar unbereinigt mit Rollsprüngen), ist
   undokumentiert. Für die aktuellen Intraday-Strategien innerhalb eines Tages ist das folgenlos,
   für jede Auswertung über Rolltermine hinweg (Seasonal, NWOG/NDOG über Quartalswechsel) nicht.
   Das passt zur bestehenden Nulltoleranz-Regel für Marktdaten in
   [[Algo-Trading: Arbeitsstandards]].
2. **Settlement vs. letzter Trade:** Der Tagesschluss in den Exporten sollte der Settlement-Preis
   sein — zu verifizieren, insbesondere weil die ICT-Konzepte im Vault stark mit
   Tagesschlusskursen arbeiten ([[ORG (Opening Range Gap) & 1st Presented FVG]] nutzt explizit
   den 16:14-Close).

Der Abschnitt zu Datenfehlern verschärft eine bestehende Projektregel: Der Vault prüft Marktdaten
bereits „wie Gold" auf Zeit und Vollständigkeit — Chan ergänzt die **Preisplausibilität**, und
zwar mit dem Argument, dass Ausreißer je nach Strategieart in **entgegengesetzte** Richtungen
verzerren.
