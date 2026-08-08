# Algo-Zielbild — Design-Spec

**Datum:** 2026-08-08
**Status:** Entwurf, wartet auf Freigabe durch Jannes
**Entstanden aus:** Interview-Session (`/superpowers:brainstorming`), 22 Einzelentscheidungen

---

## 1. Zweck dieses Dokuments

Bis heute existierte im Vault keine Seite, die das **Zielbild** des Algorithmus beschreibt.
`CLAUDE.md` hält den Arbeitsrahmen fest, `algo/PLAN.md` den Umsetzungsstand und das Backlog,
`docs/superpowers/specs/` sechs abgeschlossene Einzelprojekte. Die Frage „Wie soll das fertige
System aussehen, und was ist ausdrücklich nicht gewollt?" war nirgends beantwortet und wurde bei
jeder Aufgabe neu geraten.

Dieses Dokument beantwortet sie. Es ist die Prüfinstanz, gegen die spätere Entscheidungen laufen.

---

## 2. Zielbild

Ein **instrumentenunabhängiger, vollautonomer Handelsalgorithmus**, der über Interactive Brokers
selbstständig handelt. Devisen zuerst, weil das verfügbare Kapital nichts anderes zulässt;
Index-Futures und weitere Märkte später über dasselbe Regelwerk.

Das System stützt sich auf Jannes' ICT-Wiki als Regelquelle, prüft aber **jede** Regel
statistisch, bevor sie echtes Geld anfasst — ICT-Regeln ohne Sonderbehandlung. Parallel sucht es
eigenständig nach Mustern, die ICT nicht lehrt; solche Funde durchlaufen dasselbe Prüfverfahren.

### 2.1 Abweichung von CLAUDE.md

`CLAUDE.md` Layer 0 und `algo/PLAN.md` legen das Projekt bisher auf **MNQ** fest. Das gilt ab
Freigabe dieser Spec nicht mehr. Beide Dokumente sind entsprechend anzupassen:

- Zielinstrument: nicht MNQ, sondern **instrumentenunabhängig, Devisen zuerst**
- Begründung: Bei einem Konto unter $5.000 ist MNQ mit der 1%-Regel nicht handelbar
  (ein Kontrakt bei 30 Punkten Stop = $60 Risiko = 1,5% bei $4.000). Devisen erlauben frei
  skalierbare Positionsgrößen und lösen das Problem vollständig.

---

## 3. Getroffene Entscheidungen

| # | Frage | Entscheidung | Begründung |
|---|---|---|---|
| 1 | Kontrolle | Voll autonom, nur Not-Aus | Kein Eingriff in Einzeltrades, hält die Auswertung sauber |
| 2 | Kapital | Unter $5.000, nicht endgültig fest | Bestimmt Instrumentenwahl |
| 3 | Märkte | Ziel: alle. Start: Devisen | Positionsgröße frei skalierbar; CME-Nano-Kontrakte als Beobachtungspunkt |
| 4 | Signalquelle | ICT zuerst, Explorationsschicht daneben | Beide durch dasselbe Gate |
| 5 | Zeiten | Beobachtung 24/5, Handel London + NY | Asia ist Eingangsgröße für London (CBDR, Judas), auch ohne dort zu handeln |
| 6 | Reihenfolge | Datenschicht zuerst | Null Devisen-Kerzen vorhanden; jedes Modell wäre unbelegbar |
| 7 | Datenquelle | IBKR, zunächst nur lesend | Keine Datenquellen-Drift zwischen Backtest und Ausführung |
| 8 | Infrastruktur | Lokal starten, Ziel Raspberry Pi | Erzwingt Linux-/bildschirmlosen Code von Anfang an |
| 9 | Instrumente | EURUSD, GBPUSD, USDJPY + Bestand | Löst den offenen PLAN.md-Punkt „SMT braucht zweites Symbol" |
| 10 | Historie | Gestaffelt: 6 Monate, dann tiefer | Fehler in Zeitlogik fällt nach einer Stunde auf, nicht nach zwölf |
| 11 | Risikomodell | Struktur fest, alle Zahlen gemessen | Siehe Abschnitt 5 |
| 12 | Schmerzgrenze | 35% Drawdown vom Höchststand | Ab ~50% ist eine Verdopplung nur zum Ausgleich nötig |
| 13 | Bei Abweichung | Halbe Größe, dann Stopp | Pechsträhne wirft nicht raus, Defekt wird gestoppt |
| 14 | Umstellung Sizing | Ab 100 OOS-Trades | Darunter sind Bootstrap-Schranken nicht brauchbar |
| 15 | Live-Freigabe | Zahlen + mind. 3 Monate Papierhandel | Zeitkomponente verhindert, dass Glückssträhne als Beweis gilt |
| 16 | Haltedauer | Nur Intraday, abends flat | Schließt Wochenendlücke und Finanzierungskosten aus |
| 17 | Red-Folder-News | Nicht gehandelt, ±20 Min positionsfrei | Siehe Abschnitt 6.1 — Abweichung vom Wiki |
| 18 | Verbote | Siehe Abschnitt 5.8 | Hart verdrahtet, keine Strategie kann sie umgehen |
| 19 | Erfolgsmaß | 35% Drawdown bindend, Ertrag folgt daraus | 10%/Monat und 35% Drawdown schließen sich aus |
| 20 | Prüfgate | Gleiches Verfahren für ICT und Eigenfunde | Auch ICT-Regeln können durchfallen |
| 21 | Sekundenauflösung | Nur Einstiegsverfeinerung | Sekundenhistorie existiert nicht → nicht validierbar |
| 22 | Feiertage | Bankfeiertage + Börsenfeiertage | Ohne Zinsmärkte kann die Triad nicht bestätigen |

### 3.1 Der Zielkonflikt bei Punkt 19

Jannes' ursprüngliche Zielangabe war „mindestens 10% pro Monat". Das ist mit einer 35%-Drawdown-
Grenze mathematisch unvereinbar, weil beide aus derselben Größe folgen — dem Risiko pro Trade:

| Risiko/Trade | ≈ Monatsertrag | Drawdown bei 10 Verlusten in Folge |
|---|---|---|
| 1% | 2–4% | ~10% |
| 2% | 4–7% | ~20% |
| 4% | ~10% | ~40% |
| 6% | ~15% | ~60% |

Zehn Verluste in Folge sind bei 50% Trefferquote über einige hundert Trades statistisch zu
erwarten, nicht außergewöhnlich. Zum Vergleich: Renaissance Medallion, der bestdokumentierte
Handelsfonds der Geschichte, liegt langfristig bei rund 66% **pro Jahr**; 10% monatlich entspricht
+214% pro Jahr.

**Entscheidung:** Die Drawdown-Grenze ist bindend, das Ertragsziel entfällt als Vorgabe.

---

## 4. Architektur

Grundprinzip: **Beobachten, Entscheiden und Ausführen sind getrennt.** Die Beobachtung läuft
immer und überall. Die Entscheidung greift nur auf validierte Regeln zu. Die Ausführung kommt an
keiner Stelle am Risiko-Wächter vorbei.

```
   IBKR (nur lesend in Stufe 1)
        │
   ┌────▼──────────────┐
   │ 1 Marktdaten      │  Minutenkerzen als einzige Wahrheit
   └────┬──────────────┘
        │                    ┌──────────────────────┐
   ┌────▼──────────────┐     │ 2 Instrument-Register│
   │ 3 Beobachtung     │◄────┤ Pip-Wert, Mindest-   │
   │   24/5, handelt   │     │ größe, Sessionzeiten │
   │   NICHT           │     └──────────────────────┘
   └────┬──────────────┘
        │  erkannte Strukturen
   ┌────▼──────────────────────────────┐
   │ 4 Regelregister                   │
   │   ICT-Regeln │ Explorationsfunde  │
   │   Status: Kandidat→validiert→live │
   └────┬──────────────────────────────┘
        │            ▲
        │       ┌────┴─────────────────┐
        │       │ 5 Validierungs-Gate  │
        │       └──────────────────────┘
   ┌────▼──────────────┐
   │ 6 Risiko-Wächter  │  KEIN Weg vorbei
   └────┬──────────────┘
   ┌────▼──────────────┐
   │ 7 Ausführung      │
   └────┬──────────────┘
   ┌────▼──────────────┐
   │ 8 Betriebs-       │
   │   protokoll       │──── zurück in 3 und 5
   └───────────────────┘
```

### 4.1 Warum diese Schnitte

- **Baustein 2** ist der Grund, warum „marktweit" möglich ist. Alles Instrumentenspezifische lebt
  ausschließlich dort. Kein anderer Baustein weiß, ob er EURUSD oder MNQ vor sich hat. Ein neues
  Instrument ist ein Tabelleneintrag, kein Umbau.
- **Baustein 3** handelt nicht und kann deshalb risikofrei über alle Instrumente und Zeiten laufen.
- **Baustein 4/5**: ICT-Regeln und Eigenfunde liegen im selben Register und durchlaufen dasselbe
  Gate. Kein Vertrauensvorschuss, kein Malus.
- **Baustein 6** ist bewusst eigenständig, nicht Teil der Strategie. Wäre die Risikoprüfung Teil
  der Strategie, könnte eine neue Strategie sie vergessen.

### 4.2 Bausteine und Dateien

| Baustein | Datei | Status |
|---|---|---|
| Marktdaten (IBKR) | `algo/broker_ibkr.py` | neu, Stufe 1 nur lesend |
| Instrument-Register | `algo/instruments.py` | neu, wächst aus `pnl.py` |
| Beobachtung 24/5 | `algo/observe.py` | neu, nutzt `tools/analyze_ohlc.py` unverändert |
| Datenprüfung | `algo/verify_data.py` | neu |
| Wirtschaftskalender + Feiertage | `algo/calendar_blocks.py` | neu |
| Regelregister | `algo/registry.py` | neu, klein |
| Regeln | `algo/rules.py`, `algo/signals.py` | vorhanden |
| Validierungs-Gate | `algo/validate.py`, `algo/backtest_walkforward.py`, Permutationstest | vorhanden bzw. spezifiziert |
| Risiko-Wächter | `algo/risk_guard.py` | neu |
| Ausführung | `algo/broker_ibkr.py` | später erweitert |
| Betriebsprotokoll | `algo/live/` | vorhanden, erweitert |
| Regressionscheck | `algo/selfcheck.py` | vorhanden, Eintrag pro neuem Baustein |

### 4.3 Datenhaltung

Die bestehende Struktur `raw/marktdaten/<jahr>/<monat>/<tag>/` bleibt, samt
`tools/sort_marktdaten.py`.

**Änderung:** Pro Instrument und Tag nur noch **eine** Datei mit Minutenkerzen, statt sechs
Dateien für sechs Zeiteinheiten. Alles Größere wird daraus gerechnet.

Begründung: Sechs getrennte Zeiteinheiten können auseinanderlaufen — dieselbe Kerze mit zwei
verschiedenen Zeitstempeln. Laut `CLAUDE.md` („Zeit vor Preis") ist genau das der schädlichste
Fehlertyp im Projekt. Eine Quelle, alles abgeleitet, schließt ihn aus.

**Devisen-Tagesgrenze:** Der Handelstag im Devisenmarkt beginnt **17:00 New Yorker Zeit am
Vortag**, nicht um Mitternacht. Die Tagesdateien folgen dieser Grenze. Andernfalls stimmen die
abgeleiteten Tageskerzen nicht mit IBKRs eigenen überein, und jede Tagesrange-Auswertung wäre
still falsch.

### 4.4 Zwei Betriebsarten

Dieselben Regeln, zwei Datenwege:

- **Stapelbetrieb** — Historie, Beobachtung, Backtest, Validierung. Minutenkerzen.
- **Live-Schleife** — Kursstrom, Sekundenauflösung, Einstiegsverfeinerung, Risiko-Wächter,
  Ausführung.

Beide greifen auf **dasselbe** Regelregister zu. Zwei getrennte Umsetzungen driften auseinander,
und man merkt es erst, wenn Geld fehlt.

**Latenzbudget** (Richtwerte, beim Bau gegen die echte Schnittstelle zu prüfen):

| Glied | Zeit |
|---|---|
| IBKR-Kursaktualisierung (Devisen) | ~250 ms |
| Regelauswertung | wenige ms |
| Order raus, Bestätigung zurück | ~100–500 ms |
| **Ereignis bis Order im Markt** | **~0,5–1 s** |

Das genügt: ICT-Setups entstehen über Sekunden bis Minuten. Das System konkurriert nicht über
Geschwindigkeit — der Spread ist bei kleinen Konten der bestimmende Kostenfaktor, nicht die Latenz.

**Sekundenauflösung nur zur Einstiegsverfeinerung.** IBKR liefert Sekundenhistorie nur in sehr
kleinen Häppchen bei gedrosselter Abfragerate; Monate davon zu ziehen ist praktisch nicht machbar.
Daraus folgt: Regeln auf Sekundenbasis könnten das Prüfgate nie durchlaufen. Das Signal entsteht
deshalb auf 1m/5m/15m, der Sekundenstrom bestimmt nur den genauen Moment innerhalb der bereits
beschlossenen Zone.

**Einstieg und Stop gehen als verbundene Order gemeinsam raus**, nie nacheinander — sonst
existiert ein Zeitfenster mit ungesicherter Position.

---

## 5. Risikomodell

Grundsatz von Jannes: **„Risikomanagement vor Gewinn, immer."**

### 5.0 Warum das ICT-Risikomodell nicht unverändert übernommen wird

Jannes' Einwand, hier festgehalten weil er die Herleitung ändert: Das ICT-Regelwerk ist für einen
**menschlichen** Trader geschrieben. Die 1%-Regel wird in Month 02 ausdrücklich mit Angst und
Verlustaversion begründet — die Quelle heißt wörtlich „No Fear Of Losing". Ein Algorithmus hat
keine Angst.

Daraus folgt eine Unterscheidung, die im gesamten Projekt gilt:

- **Strukturregeln** — Killzones, Session-Logik, PD Arrays, „Time before Price". Beschreiben
  Marktverhalten. Gelten für den Algo unverändert.
- **Psychologieregeln** — „nicht mehr als 2 Trades am Tag", „nach zwei Verlusten aufhören",
  „nur High-Probability-Setups". Schützen einen Menschen vor sich selbst. Der Algo braucht sie
  nicht, und sie kosten ihn Erwartungswert.

Belegt durch Masters, „The Percent Wins Fallacy": In einem reinen Zufallsmarkt lässt sich eine
Trefferquote von 90% erzeugen, indem man das Ziel 1 Punkt und den Stop 9 Punkte entfernt setzt —
der Erwartungswert bleibt exakt null. Zitat: *„If someone brags about how often their trading
system wins, ask them about the size of their wins and losses. Neither exists in isolation."*
Trefferquote allein ist damit **kein** Qualitätsmaß.

Die 1%-Regel steht zwischen beiden Kategorien: als Disziplinregel entstanden, aber mit echter
mathematischer Funktion (Begrenzung des Ruinrisikos). Die Funktion bleibt, die Herleitung ändert
sich.

### 5.1 Schicht 0 — Kein Handel ohne bestandene Validierung

Bevor eine Regel echtes Geld anfasst, muss sie Walk-Forward und Permutationstest bestehen.
Masters' Kernaussage: Die größte Gefahr ist nicht der Drawdown, sondern eine Regel zu handeln,
die nie einen Vorteil hatte. Ein Stop-Loss schützt davor nicht.

### 5.2 Schicht 1 — Positionsgröße

- **1% des aktuellen Guthabens pro Trade ist eine harte Obergrenze**, die nie überschritten wird.
- Formel unverändert aus `wiki/concepts/Risikomanagement (1% pro Trade).md`:
  `Größe = floor(Guthaben × 1% / Stop-Abstand)`
- Ab 100 Out-of-Sample-Trades wird die Größe aus der gemessenen Verteilung abgeleitet. Diese
  Messung darf die Größe **nur senken, nie anheben**.
- Halber Kelly bleibt zusätzliche Obergrenze (siehe
  `wiki/concepts/Kelly-Criterion & Value-at-Risk (Money Management).md`: direkte Kelly-Nutzung
  kann zum Totalverlust führen, weil reale Returns nicht normalverteilt sind).

### 5.3 Schicht 2 — Korrelationsdeckel

**Neu, und der wichtigste Zusatz gegenüber dem bestehenden Wiki-Stand.**

Die bestehende Seite sagt ausdrücklich: *„Jeder Trade wird unabhängig von anderen Trades desselben
Tages auf 1% Risiko bemessen."* Bei einem Instrument ist das richtig. Bei EURUSD, GBPUSD und
USDJPY ist es falsch — diese drei sind überwiegend **eine** Wette auf den Dollar. Drei
gleichgerichtete Positionen sind nicht dreimal 1%, sondern annähernd 3% auf denselben Gedanken.

Regel: maximal **2% gleichzeitig offenes Risiko**, gewichtet mit der **gemessenen** Kopplung
zwischen den beteiligten Instrumenten. Die Kopplung wird aus den eigenen Daten bestimmt, nicht
angenommen.

### 5.4 Schicht 3 — Tageslimit als Anomalie-Bremse

Ein Tagesverlustlimit hat für einen Algo keine statistische Rechtfertigung — er tiltet nicht. Es
bekommt deshalb eine andere Aufgabe: nicht „heute ist genug verloren", sondern „heute ist mehr
verloren, als der Backtest für möglich hält, also ist wahrscheinlich etwas kaputt".

Schwelle abgeleitet aus der simulierten Tagesverlust-Verteilung, nicht gewählt.

### 5.5 Schicht 4 — Drawdown-Grenze nach Masters' Doppel-Bootstrap

Bindende Grenze: **35% vom Höchststand** (nicht vom Startkapital).

Das Verfahren zur Ableitung der zulässigen Positionsgröße daraus stammt aus Masters, „Bounding
Drawdown". Zentrale Warnung von dort, die den naheliegenden Weg ausschließt: Wer einfach seine
Out-of-Sample-Ergebnisse neu mischt und daraus den Drawdown schätzt, **unterschätzt katastrophale
Drawdowns um mehr als das Zehnfache** — weil die eigene Testperiode selbst eine Zufallsstichprobe
ist. Masters legt deshalb einen zweiten Bootstrap darum (Doppel-Bootstrap mit `DD_conf` und
`Bound_conf`).

Zitat zur Fehlerrichtung: *„Optimistic OOS samples work against us far more strongly than
pessimistic samples work for us."*

### 5.6 Schicht 5 — Annahme-Wächter

Masters liefert auch das Werkzeug: Schranken für gruppierte Ergebnisse (monatlich/quartalsweise)
berechnen und den Live-Betrieb dagegen laufen lassen — *„we can then use these bounds to track
ongoing performance and detect deterioration."*

Reaktion bei Auslösung: **erst halbe Positionsgröße, bei weiterer Verschlechterung Stopp.**
Meldung an den Nutzer in beiden Stufen.

### 5.7 Schicht 6 — Ausführungskosten (Kissell)

Kissells Marktwirkungs-Modelle sind für Ordergrößen gebaut, die den Markt bewegen — bei diesem
Kontostand nicht zutreffend. Übertragbar ist sein Grundmaß **Implementation Shortfall**: die
Differenz zwischen dem Preis, bei dem entschieden wurde, und dem tatsächlichen Füllpreis.

Wird pro Trade protokolliert und gegen die Backtest-Annahme geprüft. Weicht es systematisch ab,
ist der Backtest wertlos.

### 5.8 Harte Verbote

Im Risiko-Wächter verdrahtet, von keiner Strategie umgehbar:

1. **Keine Vergrößerung einer Verlustposition.** Kein Nachkaufen, kein Verdoppeln nach Verlust.
2. **Nie ohne Stop.** Der Stop liegt als echte Order beim Broker, nicht als Absicht im Programm.
   Grund: Bei Verbindungsabbruch oder Absturz schützt eine Absicht im Programm nichts.
3. **Stop nur in Gewinnrichtung verschiebbar**, nie weiter weg.

Zusätzlich gilt das ICT-Regelwerk als Strukturschicht darüber.

### 5.9 Prüfreihenfolge im Risiko-Wächter

Jede Order durchläuft der Reihe nach:

1. Stop vorhanden?
2. Position im selben Instrument bereits offen?
3. Größe ≤ 1% des aktuellen Guthabens?
4. Korrelationsdeckel (2%) eingehalten?
5. Tagesverlust unter Anomalieschwelle?
6. Drawdown unter 35% vom Höchststand?
7. Annahme-Wächter ruhig?
8. Sperrkalender abrufbar?
9. Red-Folder-News innerhalb der nächsten 20 Minuten?
10. Bankfeiertag oder Börsenfeiertag?
11. Handelsende (Intraday-Flat) in Reichweite?

Fällt eine Prüfung durch, entsteht kein Trade — und der Grund wird protokolliert, damit später
auswertbar ist, wie oft welche Bremse gegriffen hat.

**Abgrenzung zum Triad-Veto:** Die Interest Rate Triad (Abschnitt 7.2) und der Regime-Filter sind
**keine** Risikoprüfungen, sondern Teil der Regelschicht — sie entscheiden, ob ein Setup überhaupt
gültig ist, nicht ob es tragbar ist. Reihenfolge: Regelschicht erzeugt einen Vorschlag → Triad und
Regime-Filter können ihn verwerfen → erst der überlebende Vorschlag geht in die elf Prüfungen
oben. Grund für die Trennung: Der Risiko-Wächter muss für jede künftige Strategie unverändert
gelten, auch für solche, die keine Benchmark-Bestätigung kennen.

---

## 6. Sperrquellen

### 6.1 Red-Folder-News

**Keine Positionen von 20 Minuten vor bis 20 Minuten nach dem Termin.** Nicht „läuft mit Stop
weiter" — offene Positionen werden vor dem Fenster geschlossen.

> ⚠️ **Bewusste Abweichung vom Wiki.** `wiki/concepts/ICT Killzones.md` sagt: *„News (Red Folder)
> liefern die Volatilität für die größten Moves des Tages."* Bei ICT sind News der Treibstoff, auf
> den man wartet. Diese Spec entscheidet dagegen — Begründung: ICT beschreibt die **Preisrichtung**,
> die Sperre schützt vor der **Ausführung**. In den Sekunden der Veröffentlichung weitet sich der
> Spread um ein Vielfaches, und der Backtest kennt das nicht. Der Widerspruch wird im Wiki markiert,
> nicht überschrieben.

**Bekannter Preis dieser Regel:** Die wichtigen US-Termine liegen 8:30 und 14:00 New Yorker Zeit,
also mitten in NY AM und NY PM. An Tagen mit Arbeitsmarktdaten oder Zinsentscheidung fällt ein
spürbarer Teil der Killzone weg.

Die Beobachtungsschicht zeichnet diese Fenster weiter auf. Die Entscheidung ist damit später
anhand echter Zahlen überprüfbar, ohne je Kapital darin riskiert zu haben.

### 6.2 Feiertage

Gesperrt wird an **US-Bankfeiertagen UND Börsenfeiertagen** (Vereinigungsmenge).

Begründung für die Vereinigung: Karfreitag ist kein Bankfeiertag, aber Anleihemärkte sind zu — die
Interest Rate Triad (Abschnitt 7.2) hätte keine Daten und könnte nichts bestätigen. Umgekehrt sind
Columbus Day und Veterans Day Bankfeiertage bei geöffneter Börse, aber mit dünnem Handel.

### 6.3 Fail-Closed

**Ist ein Sperrkalender nicht abrufbar, wird nicht gehandelt.** Ein Algo, der nicht weiß, wann
News kommen oder ob heute Feiertag ist, kann die Regeln nicht einhalten. Im Zweifel aus.

---

## 7. Instrument-Register

### 7.1 Umfang

| Zweck | Instrumente |
|---|---|
| **Gehandelt** | EURUSD, GBPUSD, USDJPY |
| **Benchmark** | DXY (gerechnet, siehe 7.3) |
| **Bestätigung (Interest Rate Triad)** | ZB (30J), ZN (10J), ZF (5J) |
| **DXY-Bestandteile** | USDCAD, USDSEK, USDCHF |
| **Beobachtet** | MNQ, ES, NQ |

Die Trennung „gehandelt" gegen „nur beobachtet" existiert im Architekturschnitt bereits und trägt
diese Erweiterung ohne Umbau.

### 7.2 Interest Rate Triad als Bestätigungsfilter

Aus `wiki/concepts/Intermarket Relationships.md`, Abschnitt „Interest Rate Triad":

- Triad = die drei US-Zins-Futures 30-Jahre, 10-Jahre, 5-Jahre.
- **Distribution (bearish):** Benchmark macht höheres Hoch, mindestens einer der drei Zinsmärkte
  macht niedrigeres Hoch.
- **Akkumulation (bullish):** Benchmark macht niedrigeres Tief, mindestens einer macht höheres Tief.
- **Eine** Divergenz unter dreien genügt.
- **Workflow:** Trifft der Preis auf der Benchmark einen vorab markierten Order Block, Liquidity
  Pool oder FVG, wird die Triad geprüft. Zeigt sie keine Divergenz, wird das Setup **verworfen**
  statt gehandelt.

Das ist ein Veto und gehört damit in dieselbe Kette wie der Risiko-Wächter.

**Regime-Filter, ebenfalls aus derselben Seite:** Laufen USDX und Bonds **zusammen** statt
entgegengesetzt, fehlen Trending Conditions und der Markt konsolidiert wahrscheinlich. Kann
Setups ganzer Tage aussortieren, bevor sie entstehen.

**Paarauswahl vor Chartanalyse:** *„Zuerst den USDX auf klare Divergenz prüfen, dann das Paar
wählen."* Der Algo prüft nicht drei Paare parallel und nimmt, was zuerst feuert.

### 7.3 DXY wird gerechnet, nicht gekauft

Der Dollar Index wird aus seinen sechs Bestandteilspaaren nach der öffentlichen Formel berechnet,
statt als Indexlizenz bezogen.

Vorteile: keine zusätzliche Datenlizenz; Minutenauflösung über den gesamten Zeitraum statt der
Beschränkungen einer Indexlizenz; alle Bestandteile laufen über denselben Devisen-Zugang.

**Pflichtprüfung vor Verwendung:** Der gerechnete Wert wird gegen eine unabhängige Referenz
geprüft. Der Unterschied zwischen Kassa-Index und Futures-Kontrakt (Basis/Carry) ist real und
muss benannt werden, auch wenn er Divergenzbetrachtungen nicht stört.

### 7.4 Offenes Datenrisiko: Zins-Futures

Die drei Zins-Futures laufen an der CBOT. Ob der IBKR-Zugang das abdeckt, ist **nicht geprüft**.
Kommt in den Vorabtest (Abschnitt 10.1).

Falls nicht verfügbar: Die vorhandenen FRED-Daten enthalten die 10-Jahres-Rendite, aber nur als
Tageswert. Für eine Divergenzprüfung im Moment des Levelkontakts reicht das nicht. Dann ist ein
anderer Weg nötig, und das ist zu melden, bevor darauf aufgebaut wird.

---

## 8. Fehlerbehandlung

Grundregel überall: **Im Zweifel nicht handeln.** Ein verpasster Trade kostet nichts, ein Trade
auf falscher Grundlage schon.

| Störung | Reaktion |
|---|---|
| Verbindung zu IBKR weg | Keine neuen Trades. Laufende Positionen geschützt, weil der Stop als echte Order beim Broker liegt. Bei Rückkehr: Abgleich |
| Programm stürzt ab / Strom weg | Dasselbe. Beim Neustart wird der Zustand **vom Broker gelesen**, nie aus lokaler Datei rekonstruiert |
| Sperrkalender nicht abrufbar | Kein Handel |
| Lücke im Kursstrom | Kein Handel im betroffenen Instrument, andere laufen weiter |
| Unbekannte Position im Konto | Sofortiger Stopp + Meldung. Bedeutet immer, dass eine Annahme falsch ist |
| **Uhr des Rechners falsch** | Sofortiger Stopp |

### 8.1 Zeitprüfung

Killzone-Fenster, Macro-Fenster und das 20-Minuten-News-Fenster sind Zeitfenster. Geht die Uhr des
Raspberry Pi zwei Minuten falsch, handelt der Algo systematisch im falschen Moment — und **keine
Zahl im Protokoll sieht auffällig aus.**

Prüfung gegen eine externe Zeitquelle beim Start und laufend im Betrieb. Abweichung über einer
Sekunde bedeutet Stopp.

### 8.2 Der Broker ist die Wahrheit

Was der Algo zu besitzen glaubt, ist eine Vermutung; was IBKR meldet, ist der Stand. Bei jedem
Abgleich gewinnt IBKR. Das ist die Stelle, an der selbstgebaute Systeme Geister-Positionen doppelt
öffnen.

### 8.3 Not-Aus

Eine Datei, deren bloßes Vorhandensein den Algo stoppt — funktioniert auch dann, wenn er sonst
nicht mehr reagiert. Zusätzlich bleibt immer der direkte Weg über TWS. Ein Not-Aus, der nur
innerhalb des Programms funktioniert, ist keiner.

---

## 9. Validierung

Vier Ebenen, von billig nach teuer:

1. **`algo/selfcheck.py`** — jeder neue Baustein bekommt einen Eintrag. Nach jeder Änderung.
2. **Risiko-Wächter gegen erfundene Extremfälle** — Nullgröße, Stop auf Einstiegspreis, Konto im
   Minus, zehn Signale in derselben Sekunde, Kalender liefert Unsinn. Wichtiger als
   Strategietests: Eine schlechte Strategie kostet Geld, ein kaputter Risiko-Wächter das Konto.
3. **Bestehende Backtest-Standards** aus `CLAUDE.md` bleiben Pflicht — echter Punktwert statt
   Prozentnäherung, konservative Auflösung bei Stop und Ziel in derselben Kerze (`dubious_pct`
   als Pflichtkennzahl), kein Lookahead.
4. **Live-Schleife gegen aufgezeichnete Daten**, Trades mit denen des Backtests verglichen.
   Unterschiedliche Trades bei identischen Daten heißt: einer der beiden ist falsch. Das ist der
   Grund, warum beide dasselbe Regelregister benutzen müssen.

Danach: drei Monate Papierhandel, Ergebnisse innerhalb der berechneten Schranken.

---

## 10. Erste Ausbaustufe

**Ziel:** Belegen, ob sich die ICT-Konzepte auf Devisen übertragen. Gemessen, nicht vermutet. Es
wird kein einziger Trade ausgeführt, auch kein simulierter.

### 10.1 Vorabtest, vor allem anderen

Ein Test von wenigen Minuten: **Kommt über den IBKR-Zugang Devisen-Historie herein, und sind die
CBOT-Zins-Futures verfügbar?** Ein Papierkonto genügt; es muss kein Geld bei IBKR liegen.

Reicht die Marktdaten-Berechtigung nicht, ist der Rest hinfällig und ein anderer Weg nötig.
Dieser Test läuft, **bevor** eine Zeile Aufbau entsteht.

### 10.2 Umfang

| # | Was | Ergebnis |
|---|---|---|
| 1 | `algo/instruments.py` | Register mit dreizehn Einträgen (Abschnitt 7.1) |
| 2 | `algo/broker_ibkr.py` | Nur lesend. Verbinden, Historie holen, Kerzen streamen. **Keine Order-Funktion vorhanden** — nicht abgeschaltet, sondern nicht geschrieben |
| 3 | Datenimport | 6 Monate Minutenkerzen für Devisen + Zins-Futures |
| 4 | DXY-Berechnung | Aus den sechs Bestandteilen, gegen Referenz geprüft |
| 5 | `algo/verify_data.py` | Prüfroutine — der eigentliche Wert dieser Stufe |
| 6 | `algo/observe.py` | Bestehende Detektoren über alle Instrumente, 24/5 |
| 7 | Erster Bericht | Wie sehen die ICT-Strukturen im Devisenmarkt aus? |

### 10.3 Abnahmekriterien

- Die aus Minutenkerzen gerechneten **Tageskerzen stimmen mit IBKRs eigenen überein** — alle
  Instrumente, gesamter Zeitraum. Prüft die 17:00-Grenze und die Zeitzonenlogik gleichzeitig.
- **Jede** Lücke ist aufgelistet und erklärt (Wochenende, Feiertag, Broker-Wartung). Keine
  unerklärte Lücke bleibt stehen.
- Stichprobe von Zeitstempeln gegen vorhandene TradingView-Exporte passt.
- Der gerechnete DXY stimmt mit der unabhängigen Referenz überein, Abweichungen sind erklärt.
- Beobachtung läuft über sechs Monate und alle Instrumente durch und erzeugt ein Strukturprotokoll.
- `algo/selfcheck.py` hat einen Eintrag pro neuem Baustein.
- `algo/README.md` und `algo/PLAN.md` gepflegt; `CLAUDE.md` auf das neue Zielbild angepasst
  (Abschnitt 2.1).

### 10.4 Was der erste Bericht beantwortet

- Bilden sich FVGs im Devisenmarkt gleich häufig wie bei Index-Futures, oder seltener?
- Funktionieren die Killzone-Fenster dort, oder liegen die Bewegungen zu anderen Zeiten?
- Wie oft folgt auf einen Sweep tatsächlich ein Strukturbruch?
- Wie stark laufen EURUSD und GBPUSD wirklich im Gleichschritt? Daraus entsteht der
  Korrelationsdeckel aus Abschnitt 5.3.
- Wie oft zeigt die Interest Rate Triad Divergenz an einem Levelkontakt — und wie oft nicht?
- SMT-Divergenz wird zum ersten Mal überhaupt messbar (offener PLAN.md-Punkt).

Das sind **keine Handelsregeln**, sondern die Grundlage, auf der die erste Regel entsteht.

### 10.5 Nicht in Stufe 1

Regelregister, Validierungs-Gate, Risiko-Wächter, Sperrkalender, Live-Schleife, jede Form von
Order-Code. Stufe 2 wäre Regelregister und Gate, Stufe 3 Risiko-Wächter und Papierhandel. Beide
werden jetzt nicht spezifiziert — was in Stufe 1 herauskommt, ändert vermutlich ihren Zuschnitt.

---

## 11. Folgearbeiten im Wiki

Nach Freigabe dieser Spec zu erledigen (Pflicht laut `CLAUDE.md`, „Kontinuierliches Wachstum"):

- **Neue Synthesis-Seite** zur Unterscheidung Strukturregeln gegen Psychologieregeln
  (Abschnitt 5.0) — betrifft das gesamte ICT-Material und ist keine Algo-Interna.
- **`wiki/concepts/Risikomanagement (1% pro Trade).md`** — Korrelationsdeckel ergänzen. Die
  bestehende Formulierung „unabhängig von anderen Trades desselben Tages" ist bei mehreren
  korrelierten Instrumenten irreführend.
- **`wiki/concepts/ICT Killzones.md`** — Red-Folder-Abweichung als Widerspruch markieren
  (Abschnitt 6.1), nicht überschreiben.
- **Neue Concept-Seite** zu Masters' Drawdown-Bounding und der Percent-Wins-Fallacy.
- **`wiki/models/Meine Strategien (Übersicht).md`** — Verweis auf diese Spec als übergeordnetes
  Zielbild.
- **`wiki/log.md`** — Eintrag vom Typ `synthesis`.

---

## 12. Offene Punkte

| # | Punkt | Wann geklärt |
|---|---|---|
| 1 | Reicht die IBKR-Marktdatenberechtigung für Devisen-Historie? | Vorabtest, Abschnitt 10.1 |
| 2 | Sind die CBOT-Zins-Futures verfügbar? | Vorabtest |
| 3 | Genaue IBKR-Grenzen für Minuten- und Sekundenhistorie | Beim Bau, gegen die echte Schnittstelle |
| 4 | Endgültige Kontogröße | Vor Live-Freigabe |
| 5 | Gemessene Kopplung zwischen den Devisenpaaren | Erster Bericht, Abschnitt 10.4 |
| 6 | Konkrete Zahlen für Anomalieschwelle und Positionsgröße | Nach 100 OOS-Trades |
| 7 | CME-Nano-Kontrakte — Verfügbarkeit ungeprüft | Beobachtungspunkt, nichts baut darauf auf |

---

## 13. Bewusst nicht enthalten

Keine Nutzeroberfläche, kein Dashboard, keine Datenbank (Dateien genügen bei dieser Datenmenge),
keine Broker-Abstraktion für mehrere Broker, keine Warteschlange oder Nachrichtenschicht zwischen
den Bausteinen.

Alles davon ist später nachrüstbar und würde jetzt Bauzeit kosten, bevor überhaupt etwas läuft.
`CLAUDE.md` stuft Optik-Wünsche ohnehin ausdrücklich als nachrangig ein.
