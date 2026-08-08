---
tags: [concept, algo-methodology, daten, validation, referenz]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[2022-07-05 - Two Sigma - Machine Learning Models of Financial Data (Source)|Two Sigma — Machine Learning Models of Financial Data (Source)]]"]
---

# Datenbeschaffung für Backtests (Optionen & Grenzen)

Antwort auf die Frage: **Wie komme ich an ähnlich viele Daten wie ein Fonds wie Two Sigma?**

## Die Unterscheidung, an der alles hängt

Two Sigmas „hunderte Milliarden Datenpunkte" sind **Orderbuch-Ereignisse** — jede Quote-Änderung,
jede Stornierung, jeder Trade. Davon passieren tausende **pro Sekunde und Instrument**.

Ein ICT-Setup ist etwas völlig anderes: Ein Silver Bullet im NY-AM-Fenster kann **höchstens einmal
pro Tag und Instrument** auftreten. Selbst mit unendlicher Historie wächst die Zahl der
Gelegenheiten nur mit der Zahl der Tage.

> **Die knappe Ressource ist nicht die Datenmenge, sondern die Zahl unabhängiger Vorkommen des
> eigenen Musters.**

Daraus folgt: Two Sigmas Datenberg ist nicht erreichbar — **und nicht nötig**, weil das Muster auf
einer gröberen Zeitskala definiert ist. Erreichbar und nötig ist eine Stichprobe, die für
Bootstrap-Verfahren, Permutationstests und Konfidenzgrenzen ausreicht. Das sind Größenordnungen von
Tausenden, nicht von Milliarden.

## „Öfter backtesten" — die gefährliche Doppeldeutigkeit

Zwei Dinge, die gleich klingen und gegensätzlich wirken:

| | Wirkung |
|---|---|
| **Eine feste Regel gegen viele synthetische Historien** (Permutation, Bootstrap) | **Gut.** Das ist ein Signifikanztest — er misst, ob das Ergebnis Zufall war. Beliebig oft möglich, ohne Strafe |
| **Viele Regelvarianten gegen eine Historie** | **Gefährlich.** Das ist Data Mining. Jede zusätzliche Variante erhöht die Wahrscheinlichkeit eines Zufallstreffers und damit den nötigen Abschlag |

Sullivan/Timmermann/White (Journal of Finance 1999) haben genau den zweiten Fall empirisch geprüft:
Die beste Regel aus einem großen Universum war in-sample überlegen — und in den folgenden zehn
Jahren nicht mehr. Der Abschlag dafür ist nichtlinear (Harvey/Liu), siehe
[[Vier-Stufen-Strategieentwicklung (Masters)]] und
[[Monte Carlo Permutation Test (MCPT)]].

**Wer öfter testen will, muss also sagen, welches der beiden gemeint ist.** Das erste ist kostenlos
und bereits über `algo/masters.py` verfügbar. Das zweite muss gezählt und bestraft werden.

## Bezugsquellen

> ⚠️ Preise und Historientiefe Stand 2026-08-08, recherchiert, nicht getestet. Vor einem Kauf beim
> Anbieter selbst prüfen.

| Quelle | Was | Tiefe | Kosten | Haken |
|---|---|---|---|---|
| **Dukascopy** | Devisen-Ticks | ab ~2003 | **kostenlos** | Feed **eines** Brokers, weicht von IBKR ab |
| **FirstRate Data** | Futures 1-Min-Bars, ~130 aktivste Kontrakte | ab **2007** | Einmalkauf, Preis nicht öffentlich | Bars, keine Ticks. Zwei-Wochen-Muster gratis |
| **Databento** | CME inkl. CBOT/NYMEX/COMEX, bis Orderbuchtiefe | 16+ Jahre | nutzungsbasiert $/GB, **$125 Startguthaben** | **Orderbuch-Schemata nur 1 Tag** im günstigen Tarif; tiefe Orderbuchhistorie erst ab ~$1.750/Monat |
| **Polygon / Massive** | Ticks, Level 2, breite Anlageklassen | mehrjährig | ab ~$0–79/Monat je Klasse | Tiefe je Tarif |
| **TrueFX** | Devisen-Ticks aus mehreren Quellen | mehrjährig | teils kostenlos | Aggregat, nicht handelbarer Feed |
| **LOBSTER** | Nasdaq-Orderbuch, rekonstruiert aus ITCH | seit 2013 | akademisch; 5 Aktien als Gratis-Muster | Aktien, keine Futures/FX |
| **IBKR** | Devisen + Futures | Devisen mehrjährig | im Konto enthalten | Abgelaufene Futures nur bis 2 Jahre nach Verfall |

**Der wichtigste Befund in dieser Tabelle:** Die Orderbuchdaten, mit denen Two Sigma arbeitet, sind
auch käuflich — aber die *tiefe Historie* davon kostet vierstellig pro Monat. Genau der Teil, der
den Fonds-Datenberg ausmacht, ist der teure.

## Was das rechnerisch bringt

| | Instrumententage |
|---|---|
| Heute (`raw/marktdaten/`) | **394** |
| Devisen über Dukascopy, 3 Paare ab 2003 | ~18.000 |
| Futures über FirstRate, 3 Kontrakte ab 2007 | ~14.000 |
| **Zusammen, gepoolt** | **~30.000** |

Das ist rund das **Fünfundsiebzigfache** des heutigen Bestands. Wenn ein Setup an etwa jedem
fünften Tag qualifiziert, ergibt das mehrere tausend unabhängige Vorkommen — genug für
Konfidenzgrenzen, Bootstrap-Drawdownschranken und Minimum Track Record Length.

Nicht genug für Deep Learning. Aber Deep Learning ist ohnehin nicht das Ziel, siehe
[[Machine Learning für den Algo — Bewertung (laufend)]].

## Der Konflikt mit dem Grundsatz „eine Datenquelle"

Die Zielbild-Spec legt IBKR als **einzige** Quelle fest, damit Backtest und Ausführung nicht
auseinanderdriften. Dukascopy und FirstRate sind andere Feeds — leicht andere Hochs und Tiefs, und
damit leicht andere FVG-Grenzen und Sweep-Level.

**Auflösung in zwei Stufen, statt den Grundsatz aufzugeben:**

1. **Erkundung und Strukturstatistik** auf der tiefen Fremdhistorie. Fragen wie „wie oft folgt auf
   einen Sweep ein Strukturbruch", „gibt es Rundzahl-Häufung", „wie stark koppeln die Paare" sind
   gegenüber kleinen Feed-Unterschieden unempfindlich.
2. **Endgültige Validierung und Kostenkalibrierung** ausschließlich auf IBKR-Daten. Alles, was auf
   den Pip genau zählt — Fill-Annahmen, Spread, Stop-Abstände — wird nur dort gerechnet.

Eine Regel gilt erst als validiert, wenn sie **beide** Stufen besteht. Weicht das Ergebnis zwischen
den Feeds stark ab, ist die Regel zu empfindlich gegenüber Datendetails und damit ohnehin nicht
handelbar — das ist ein nützlicher Nebentest, kein Ärgernis.

## Optionen, die keine neuen Daten brauchen

Oft mit besserem Ertrag pro Aufwand als ein Datenkauf:

| Hebel | Wirkung |
|---|---|
| **Instrument-Pooling** | Vervielfacht die Stichprobe ohne einen Tag Wartezeit. Siehe [[Universal Model & Instrument-Pooling]] |
| **Bereichsbasierte Volatilität** | Yang-Zhang ist bis **14× effizienter** als Close-to-Close — dieselbe Genauigkeit mit einem Vierzehntel der Daten |
| **Permutation und Bootstrap** | Tausende synthetische Historien aus einer echten. Bereits in `algo/masters.py` |
| **Kennzahlen auf Bar- statt Trade-Ebene** | Viel mehr Datenpunkte aus denselben Trades, siehe [[Profit pro Bar vs. pro Trade]] |
| **Fremdmarkt-Gegenprobe** | Ein ICT-Konzept auf Märkten prüfen, für die ICT es nie gelehrt hat (Gold, Öl, Anleihen). Hält es auch dort, ist es sehr wahrscheinlich echt — das ist die stärkste verfügbare Evidenzform |
| **Papierhandel vorwärts** | Erzeugt echte, unverbrauchte Out-of-Sample-Daten. Langsam, aber unbestechlich |

## Verwandt

- [[Universal Model & Instrument-Pooling]] — der kostenlose Multiplikator
- [[Machine Learning für den Algo — Bewertung (laufend)]]
- [[Monte Carlo Permutation Test (MCPT)]], [[Vier-Stufen-Strategieentwicklung (Masters)]]
- [[Futures-Datenaufbereitung & Backtesting-Fallstricke (Chan)]] — Back-Adjustment bei
  Fremdquellen-Futures
- [[Grenzen für Einzelrenditen & Drawdown]] — was mit einer größeren Stichprobe möglich wird
