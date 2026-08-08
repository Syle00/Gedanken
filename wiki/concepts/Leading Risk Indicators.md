---
tags: [concept, algo-methodology, risikomanagement, referenz]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[Algorithmic Trading - Winning Strategies and Their Rationale (Source)]]"]
---

# Leading Risk Indicators

Der **proaktive** Teil des Risikomanagements: nicht erst nach dem Verlust die Größe reduzieren,
sondern riskante Perioden von vornherein meiden. Aus
[[Algorithmic Trading - Winning Strategies and Their Rationale (Source)]] (Chan, Kap. 8).

Alle anderen Verfahren im Risikokapitel sind **reaktiv** — man senkt die Ordergröße nach einem
Verlust ([[Kelly-Formel & optimales Leverage (Chan)]]), oder man stellt bei erreichtem Drawdown
den Handel ein ([[CPPI (Constant Proportion Portfolio Insurance)]]). Deutlich vorteilhafter wäre
es, die Verlustperioden vorher zu umgehen.

**Entscheidende Unterscheidung:** Ein *leading* Risikoindikator sagt vorher, ob die **nächste**
Periode riskant wird. Ein gewöhnlicher Risikoindikator ist mit der riskanten Periode nur
**gleichzeitig** — und damit nutzlos für die Vermeidung.

## Es gibt keinen universellen Risikoindikator

> **Was für die eine Strategie eine riskante Periode ist, kann für die andere die profitabelste
> sein.** Derselbe Indikator, dieselbe Schwelle, gegensätzliche Schlussfolgerung.

Chan belegt das mit zwei Strategien aus seinem eigenen Buch und **demselben** Indikator
(VIX > 35, eine gängige Schwelle für „hochriskant"):

| Strategie | Zeitraum | normale APR | Sharpe | nach VIX > 35 am Vortag | Sharpe | Schluss |
|---|---|---|---|---|---|---|
| Buy-on-Gap (Aktien, Mean Reversion, Kap. 4) | 11.05.2006 – 24.04.2012 | 8,7 % | 1,5 | **17,2 %** | 1,4 | Risiko **nutzen** |
| FSTX Opening-Gap (Futures, Momentum, Kap. 7) | 16.07.2004 – 17.05.2012 | 13 % | 1,4 | **2,6 %** | 0,16 | Handel **aussetzen** |

Die Mean-Reversion-Strategie **verdoppelt** ihre Rendite in genau den Phasen, in denen die
Momentum-Strategie praktisch aufhört zu funktionieren. Wer den Indikator ohne eigenen Test
übernimmt, macht mit 50 % Wahrscheinlichkeit das Gegenteil des Richtigen.

## Der Katalog

| Indikator | Was er misst | Anmerkungen |
|---|---|---|
| **VIX** | implizite Volatilität des S&P 500 | gängige Schwelle 35; siehe Tabelle oben |
| **TED-Spread** | 3-Monats-LIBOR minus 3-Monats-T-Bill → **Risiko von Bankenausfällen** | Rekord **457 Basispunkte** in der Kreditkrise 2008. Vorteil: der Kreditmarkt wird von institutionellen Akteuren dominiert, die vermutlich besser informiert sind als der von Herdentrieb geprägte Aktienmarkt. Die LIBOR-Manipulation der Banken ist unschädlich, weil nur die **relative** Entwicklung zählt, nicht der Absolutwert. |
| **HYG** | ETF auf Hochzinsanleihen | Risikoaktivum als Proxy |
| **MXN** | mexikanischer Peso | wurde in der Europa-Schuldenkrise 2011 auffallend empfindlich für schlechte Nachrichten, **obwohl die mexikanische Wirtschaft durchgehend gesund war** — Händler benutzten ihn als Stellvertreter für Risikoaktiva allgemein |
| **ONN / OFF** | ETFs, die einen Korb von Risikoaktiva halten (ONN) bzw. dessen Spiegelbild (OFF) | hoher OFF-Wert = möglicher Risikoindikator. Zum Zeitpunkt des Buches erst ~7 Monate Historie, also **unbestätigt** |
| **Order Flow** | vorzeichenbehaftetes Transaktionsvolumen | siehe unten |
| **Rohstoffpreise** | strategiespezifisch | Ölpreis ist ein guter Leading Indicator für das Paar GLD/GDX (Kap. 4); Goldpreis analog für ETFs von Förderländern/-unternehmen |
| **Baltic Dry Index** | Frachtraten | möglicher Leading Indicator für ETFs/Währungen exportorientierter Länder |

## Order Flow — laut Chan der aussichtsreichste

Auf kurzen Zeitskalen erkennt, wer Zugriff auf Order-Flow-Informationen hat, eine **plötzliche
große Veränderung im Orderfluss**. Die deutet meist darauf hin, dass wichtige Information in den
Besitz institutioneller Händler gelangt ist.

```
Risikoaktivum (Aktien, Rohstoffe, riskante Waehrungen):   grosse NEGATIVE Aenderung = Risiko
Sicherer Hafen (US-Treasuries, USD, JPY, CHF):            grosse POSITIVE Aenderung = Risiko
```

Order Flow ist ein Prädiktor künftiger Preisänderungen (Lyons, 2001) und wirkt, **bevor** sich
die Information breiter im Markt verteilt und den Preis stärker bewegt.

Definition und Messung (aus Kap. 7): Order Flow ist **vorzeichenbehaftetes Transaktionsvolumen**.
Kauft ein Händler 100 Einheiten zum Briefkurs, ist der Order Flow +100; verkauft er zum Geldkurs,
−100. Für Aktien und Futures selbst berechenbar: jeden Tick aufzeichnen und bestimmen, ob die
Transaktion am Geld- oder am Briefkurs stattfand. Für Devisen schwierig, weil die meisten Dealer
keine Transaktionspreise melden — dort auf Währungs-Futures ausweichen.

Chans Einschätzung: *„As the order flow indicator works at higher frequency, it may turn out to
be the most useful of them all."*

## Die methodische Warnung

> Finanzpaniken und -krisen sind **selten**. Genau deshalb ist es beim Backtesten von
> Risikoindikatoren besonders leicht, Data-Snooping-Bias zum Opfer zu fallen — es gibt schlicht
> zu wenige Ereignisse, um eine Regel abzusichern.

Und: **kein Finanzindikator kann Natur- oder sonstige nichtfinanzielle Katastrophen vorhersagen.**

Die passenden Gegenmittel stehen an anderer Stelle im Vault:
[[Monte Carlo Permutation Test (MCPT)]] und [[Training Bias & Selection Bias]] — gerade bei
wenigen Ereignissen ist ein P-Wert aus einem Permutationstest aussagekräftiger als eine
Trefferquote.

## Bezug zu diesem Projekt

Der Vault hat bereits einen Makro-Datenstrang, der genau hier andockt:
[[Makro-FRED-Zusammenhaenge (Eigene Daten, laufend)]] wertet **VIX, DGS10 und WALCL** gegen MNQ
aus und fand eine Korrelation von **−0,743** zwischen VIX-Änderung und Tagesrendite. Das ist
allerdings eine **gleichzeitige** Korrelation — also genau der Typ „general risk indicator", den
Chan von einem *leading* Indikator abgrenzt.

Der Test, der daraus folgt und bisher fehlt: **Bedingte Auswertung statt Korrelation.** Also
nicht „wie korreliert VIX mit der Tagesrendite", sondern:

```
Wie schneidet die Silver-Bullet-Regel an Tagen ab,
an denen der VIX des VORTAGS ueber Schwelle X lag —
verglichen mit allen anderen Tagen?
```

Das ist exakt die Auswertung aus Chans Tabelle oben, ist mit `algo/fetch_fred.py` +
`algo/backtest_bt.py` ohne neue Datenquelle machbar, und beantwortet die Frage, ob MNQ-Setups zu
den Strategien gehören, die von hoher Volatilität **profitieren** (wie Buy-on-Gap) oder darunter
**leiden** (wie FSTX). Wegen der geringen Zahl von Hoch-VIX-Tagen in der aktuellen Datenbasis ist
dabei die Data-Snooping-Warnung oben besonders ernst zu nehmen.

Order Flow ist im Projekt bisher nicht verfügbar — `raw/marktdaten/` enthält OHLC ohne Bid/Ask.
Über die IBKR-Anbindung (Roadmap-Stufe 4 in [[Algo-Trading: Arbeitsstandards]]) wäre
Tick-mit-Quote-Daten grundsätzlich beschaffbar; das wäre die Voraussetzung für den laut Chan
aussichtsreichsten Indikator.

Weiterführend: [[Kelly-Formel & optimales Leverage (Chan)]],
[[CPPI (Constant Proportion Portfolio Insurance)]],
[[Stop Loss bei Mean Reversion vs. Momentum]].
