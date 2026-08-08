# Algo-Zielbild — Design-Spec

**Datum:** 2026-08-08
**Status:** Entwurf, wartet auf Freigabe durch Jannes
**Entstanden aus:** Interview-Session (`/superpowers:brainstorming`), 25 Einzelentscheidungen
**Revision 2 (2026-08-08):** Gegengeprüft gegen den vollständigen Wiki-Bestand, den ICT Core
Content und die akademische Literatur. Sieben inhaltliche Korrekturen, vier neue Pflichtbausteine.
Zielmarkt auf **Forex und CME** erweitert (Nutzerentscheidung).

---

## 1. Zweck dieses Dokuments

Bis heute existierte im Vault keine Seite, die das **Zielbild** des Algorithmus beschreibt.
`CLAUDE.md` hält den Arbeitsrahmen fest, `algo/PLAN.md` den Umsetzungsstand, `docs/superpowers/specs/`
sechs abgeschlossene Einzelprojekte. Die Frage „Wie soll das fertige System aussehen, und was ist
ausdrücklich nicht gewollt?" war nirgends beantwortet und wurde bei jeder Aufgabe neu geraten.

Dieses Dokument beantwortet sie. Es ist die Prüfinstanz, gegen die spätere Entscheidungen laufen.

---

## 2. Zielbild

Ein **instrumentenunabhängiger, vollautonomer Handelsalgorithmus** über Interactive Brokers, der
**Devisen und CME-Index-Futures** abdeckt.

Das System stützt sich auf Jannes' ICT-Wiki als Regelquelle, prüft aber **jede** Regel
statistisch, bevor sie echtes Geld anfasst — ICT-Regeln ohne Sonderbehandlung. Parallel sucht es
eigenständig nach Mustern, die ICT nicht lehrt; solche Funde durchlaufen dasselbe Prüfverfahren.

### 2.1 Warum beide Märkte

| | Devisen | CME-Index-Futures |
|---|---|---|
| Positionsgröße | frei skalierbar, 1%-Regel jederzeit einhaltbar | ab **E-nano** (24.08.2026, ~$0,20/Punkt Nasdaq) ebenfalls |
| Vorhandene Daten | **keine** | 394 Handelstage |
| Wiki-Kalibrierung | teilweise (ICT stammt ursprünglich aus FX) | vollständig |
| Akademische Absicherung | stark (siehe Abschnitt 11) | schwächer, überwiegend FX-Studien |
| Datenkosten IBKR | **kein Abo nötig**, kein gefundetes Konto | CME-Abo nötig |
| Bekanntes Risiko | Edge-Zerfall (Neely/Weller) | E-nano-Liquidität unbekannt, Tick doppelt so grob |

Die beiden ergänzen sich in genau den Punkten, in denen der jeweils andere schwach ist. Die
Architektur trägt beide ohne Mehraufwand, weil alles Instrumentenspezifische in einem Register
liegt (Abschnitt 4.1).

### 2.2 Abweichung von CLAUDE.md

`CLAUDE.md` Layer 0 und `algo/PLAN.md` legen das Projekt bisher auf **MNQ** fest. Das gilt ab
Freigabe dieser Spec nicht mehr: **instrumentenunabhängig, Devisen und CME**. Beide Dokumente sind
anzupassen.

---

## 3. Getroffene Entscheidungen

| # | Frage | Entscheidung | Begründung |
|---|---|---|---|
| 1 | Kontrolle | Voll autonom, nur Not-Aus | Kein Eingriff in Einzeltrades, hält die Auswertung sauber |
| 2 | Kapital | Unter $5.000, nicht endgültig fest | Bestimmt Instrumentenwahl |
| 3 | Märkte | **Devisen und CME** | Siehe 2.1 |
| 4 | Signalquelle | ICT zuerst, Explorationsschicht daneben | Beide durch dasselbe Gate |
| 5 | Zeiten | Beobachtung 24/5, Handel London + NY | Asia ist Eingangsgröße für London (CBDR, Judas), auch ohne dort zu handeln |
| 6 | Reihenfolge | Datenschicht zuerst | Null Devisen-Kerzen vorhanden |
| 7 | Datenquelle | IBKR, zunächst nur lesend | Keine Datenquellen-Drift zwischen Backtest und Ausführung |
| 8 | Infrastruktur | Lokal starten, Ziel Raspberry Pi | Erzwingt Linux-/bildschirmlosen Code von Anfang an |
| 9 | Instrumente | Siehe Abschnitt 7.1 | Löst den offenen PLAN.md-Punkt „SMT braucht zweites Symbol" |
| 10 | Historie | Gestaffelt: 6 Monate, dann tiefer | Fehler in der Zeitlogik fällt nach einer Stunde auf, nicht nach zwölf |
| 11 | Risikomodell | Struktur fest, alle Zahlen gemessen | Abschnitt 5 |
| 12 | Schmerzgrenze | 35% Drawdown vom Höchststand | Ab ~50% ist eine Verdopplung nur zum Ausgleich nötig |
| 13 | Bei Abweichung | Halbe Größe, dann Stopp | Pechsträhne wirft nicht raus, Defekt wird gestoppt |
| 14 | Umstellung Sizing | Ab 100 OOS-Trades | Darunter sind Bootstrap-Schranken nicht brauchbar |
| 15 | Live-Freigabe | Zahlen + mind. 3 Monate Papierhandel | Zeitkomponente verhindert, dass eine Glückssträhne als Beweis gilt |
| 16 | Haltedauer | Nur Intraday, abends flat | Schließt Wochenendlücke und Finanzierungskosten aus |
| 17 | Red-Folder-News | Nicht gehandelt, ±20 Min positionsfrei | Abschnitt 6.1 |
| 18 | Verbote | Abschnitt 5.9 | Hart verdrahtet |
| 19 | Erfolgsmaß | **35% Drawdown bindend**, Ertrag folgt | Abschnitt 3.1 |
| 20 | Prüfgate | Gleiches Verfahren für ICT und Eigenfunde | Auch ICT-Regeln können durchfallen |
| 21 | Sekundenauflösung | Nur Einstiegsverfeinerung | Sekundenhistorie existiert nicht → nicht validierbar |
| 22 | Feiertage | Bankfeiertage + Börsenfeiertage | Ohne Zinsmärkte kann die Triad nicht bestätigen |
| 23 | Marktumfang | Forex **und** CME, nicht entweder-oder | Siehe 2.1 |
| 24 | Konto | **Eigenes Konto nur für den Algo**, getrennt vom manuellen Handel | Sonst kollidieren manuelle Positionen mit denen des Algos und lösen dauernd „unbekannte Position → Stopp" aus. Nebeneffekt: Die Leistung des Algos ist sauber messbar, ohne dass manuelle Trades die Zahlen verfälschen — Voraussetzung für den Annahme-Wächter (5.6) und für CPPI (5.5), das ohnehin ein Ein-Strategie-Konto verlangt |
| 25 | Trades pro Tag | **Unbegrenzt**, bis das Risikomodul eingreift | Siehe 5.9 — eine Tagesgrenze ist eine Psychologieregel |

### 3.1 Ertragsziel — Korrektur gegenüber Revision 1

Revision 1 behauptete, „10% pro Monat" und „35% Drawdown" schlössen sich aus. **Das war falsch.**
Es unterstellte, hoher Ertrag komme nur über hohes Risiko pro Trade.

Die ICT-Quelle [[ICT Mentorship Core Content - Month 02 - How Traders Make 10% Per Month (Source)]]
rechnet einen anderen Weg vor: **2% Risiko pro Trade**, erste Hälfte bei 3:1 gesichert, zweite
Hälfte bis 9R–15R laufen lassen. Ein einziger solcher Trade ergibt rechnerisch über 10% im Monat.
Kernsatz: *„It's not having big risk that makes the money, it's having small risk."* Bei 2% Risiko
liegen zehn Verluste in Folge bei −20%, also innerhalb der 35%-Grenze.

**Arithmetisch sind beide Ziele also vereinbar** — über hohe R-Vielfache, nicht über hohes Risiko.

Was offen bleibt, ist empirisch, nicht rechnerisch: **Wie häufig entsteht tatsächlich ein
9R–15R-Runner?** Genau davor warnt Masters' Percent-Wins-Fallacy — hohe R-Vielfache erkauft man
mit niedriger Trefferquote, und beide existieren nie unabhängig voneinander. Die Runner-Häufigkeit
ist damit eine **Pflichtkennzahl im ersten Backtest**, keine Annahme.

Bindend bleibt die Drawdown-Grenze. Das Ertragsziel ist Beobachtungsgröße, keine Vorgabe.

---

## 4. Architektur

Grundprinzip: **Beobachten, Entscheiden und Ausführen sind getrennt.** Beobachtung läuft immer und
überall. Die Entscheidung greift nur auf validierte Regeln zu. Die Ausführung kommt an keiner
Stelle am Risiko-Wächter vorbei.

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
        │       │ 5 Validierungs-Gate  │  Abschnitt 9
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

- **Baustein 2** macht „marktweit" erst möglich. Alles Instrumentenspezifische lebt ausschließlich
  dort. Kein anderer Baustein weiß, ob er EURUSD, MNQ oder einen E-nano vor sich hat. Ein neues
  Instrument ist ein Tabelleneintrag.
- **Baustein 3** handelt nicht und kann deshalb risikofrei über alle Instrumente und Zeiten laufen.
- **Baustein 4/5**: ICT-Regeln und Eigenfunde im selben Register, dasselbe Gate, kein
  Vertrauensvorschuss.
- **Baustein 6** ist bewusst eigenständig. Wäre die Risikoprüfung Teil der Strategie, könnte eine
  neue Strategie sie vergessen.

### 4.2 Bausteine und Dateien

| Baustein | Datei | Status |
|---|---|---|
| Marktdaten (IBKR) | `algo/broker_ibkr.py` | neu, Stufe 1 nur lesend |
| Instrument-Register | `algo/instruments.py` | neu, wächst aus `pnl.py` |
| Beobachtung 24/5 | `algo/observe.py` | neu, nutzt `tools/analyze_ohlc.py` unverändert |
| Datenprüfung | `algo/verify_data.py` | neu |
| Sperrkalender (News + Feiertage) | `algo/calendar_blocks.py` | neu |
| Regelregister | `algo/registry.py` | neu, klein |
| Regeln | `algo/rules.py`, `algo/signals.py` | vorhanden |
| Validierungs-Gate | `algo/validate.py`, `backtest_walkforward.py`, `masters.py` | teils vorhanden, Ausbau nach Abschnitt 9 |
| Risiko-Wächter | `algo/risk_guard.py` | neu |
| Ausführung | `algo/broker_ibkr.py` | später erweitert |
| Betriebsprotokoll | `algo/live/` | vorhanden, erweitert |
| Regressionscheck | `algo/selfcheck.py` | vorhanden, Eintrag pro neuem Baustein |

### 4.3 Datenhaltung

Die bestehende Struktur `raw/marktdaten/<jahr>/<monat>/<tag>/` bleibt, samt
`tools/sort_marktdaten.py`.

**Änderung:** Pro Instrument und Tag nur noch **eine** Datei mit Minutenkerzen statt sechs Dateien
für sechs Zeiteinheiten. Alles Größere wird daraus gerechnet. Begründung: Sechs getrennte
Zeiteinheiten können auseinanderlaufen — dieselbe Kerze mit zwei Zeitstempeln. Laut `CLAUDE.md`
(„Zeit vor Preis") der schädlichste Fehlertyp im Projekt.

**Devisen-Tagesgrenze:** Der Handelstag im Devisenmarkt beginnt **17:00 New Yorker Zeit am
Vortag**. Die Tagesdateien folgen dieser Grenze, sonst stimmen die abgeleiteten Tageskerzen nicht
mit IBKRs eigenen überein und jede Tagesrange-Auswertung wäre still falsch.

**Futures-Besonderheiten** (aus [[Futures-Datenaufbereitung & Backtesting-Fallstricke (Chan)]]):

- **Back-Adjustment:** Man kann entweder den Preis oder die Rendite korrekt haben, **nie beides**.
  Welche Variante gilt, wird pro Auswertung explizit festgelegt und protokolliert.
- **Settlement- statt Schlusskurs** verwenden.
- **Rollover** ist ein eigener Vorgang mit eigenem Datum, nicht eine stille Verkettung.
- IBKR liefert **abgelaufene Futures nur bis 2 Jahre nach Verfall**. Für ältere Index-Historie
  bleiben die TradingView-Exporte notwendig — IBKR ersetzt sie nicht.

### 4.4 Zwei Betriebsarten

Dieselben Regeln, zwei Datenwege:

- **Stapelbetrieb** — Historie, Beobachtung, Backtest, Validierung. Minutenkerzen.
- **Live-Schleife** — Kursstrom, Sekundenauflösung, Einstiegsverfeinerung, Risiko-Wächter,
  Ausführung.

Beide greifen auf **dasselbe** Regelregister zu. Zwei getrennte Umsetzungen driften auseinander,
und man merkt es erst, wenn Geld fehlt.

**Latenzbudget** (Richtwerte, beim Bau gegen die Schnittstelle zu prüfen):

| Glied | Zeit |
|---|---|
| IBKR-Kursaktualisierung (Devisen) | ~250 ms |
| Regelauswertung | wenige ms |
| Order raus, Bestätigung zurück | ~100–500 ms |
| **Ereignis bis Order im Markt** | **~0,5–1 s** |

Ausreichend: ICT-Setups entstehen über Sekunden bis Minuten. Das System konkurriert nicht über
Geschwindigkeit — bei kleinen Konten ist der Spread der bestimmende Kostenfaktor, nicht die Latenz.

**Sekundenauflösung nur zur Einstiegsverfeinerung.** Verifiziert an der IBKR-Dokumentation:
1-Sekunden-Bars sind auf **60 Sekunden pro Abfrage** begrenzt, Bars ≤30 Sekunden sind **nur
6 Monate rückwärts** verfügbar, und es gelten max. 60 Abfragen pro 10 Minuten. Eine nennenswerte
Sekundenhistorie ist damit nicht beschaffbar. Regeln auf Sekundenbasis könnten das Prüfgate nie
durchlaufen. Das Signal entsteht auf 1m/5m/15m, der Sekundenstrom bestimmt nur den Moment
innerhalb der beschlossenen Zone.

**Einstieg und Stop gehen als verbundene Order gemeinsam raus**, nie nacheinander.

**Betriebsauflage:** IB-Gateway trennt die Verbindung nach etwa 24 Stunden. Ein täglicher
automatischer Neustart ist Pflicht, nicht optional. Auf dem Raspberry Pi zusätzlich: 64-Bit-Debian,
ARM-JDK 17, `xvfb` als Ersatz-Bildschirm, IBC für die automatische Anmeldung.

---

## 5. Risikomodell

Grundsatz von Jannes: **„Risikomanagement vor Gewinn, immer."**

### 5.0 Warum das ICT-Risikomodell nicht unverändert übernommen wird

Jannes' Einwand, der die Herleitung ändert: Das ICT-Regelwerk ist für einen **menschlichen** Trader
geschrieben. Die 1%-Regel wird in Month 02 ausdrücklich mit Angst und Verlustaversion begründet —
die Quelle heißt wörtlich „No Fear Of Losing". Ein Algorithmus hat keine Angst.

Chan formuliert dieselbe Haltung aus der Quant-Seite:
> *„Our goal should be the maximization of long-term equity growth, and we avoid risk only insofar
> as it interferes with this goal."*

Daraus folgt eine Unterscheidung, die im gesamten Projekt gilt:

- **Strukturregeln** — Killzones, Session-Logik, PD Arrays, „Time before Price". Beschreiben
  Marktverhalten. Gelten für den Algo unverändert.
- **Psychologieregeln** — „nicht mehr als 2 Trades am Tag", „nach zwei Verlusten aufhören", „nur
  High-Probability-Setups". Schützen einen Menschen vor sich selbst. Der Algo braucht sie nicht,
  und sie kosten ihn Erwartungswert.

Belegt durch Masters, „The Percent Wins Fallacy": In einem reinen Zufallsmarkt lässt sich eine
Trefferquote von 90% erzeugen (Ziel 1 Punkt entfernt, Stop 9 Punkte), Erwartungswert exakt null.
**Trefferquote allein ist kein Qualitätsmaß.**

Die 1%-Regel steht dazwischen: als Disziplinregel entstanden, mit echter mathematischer Funktion
(Begrenzung des Ruinrisikos). Die Funktion bleibt, die Herleitung ändert sich.

### 5.1 Schicht 0 — Kein Handel ohne bestandene Validierung

Siehe Abschnitt 9. Masters' Kernaussage: Die größte Gefahr ist nicht der Drawdown, sondern eine
Regel zu handeln, die nie einen Vorteil hatte. Ein Stop-Loss schützt davor nicht.

### 5.2 Schicht 1 — Positionsgröße und harte Obergrenzen

- **1% des aktuellen Guthabens pro Trade ist eine harte Obergrenze**, nie überschritten.
  Formel unverändert aus [[Risikomanagement (1% pro Trade)]]:
  `Größe = floor(Guthaben × 1% / Stop-Abstand)`
- Ab 100 Out-of-Sample-Trades wird die Größe aus der gemessenen Verteilung abgeleitet. Diese
  Messung darf die Größe **nur senken, nie anheben**.
- **Halber Kelly** als zweite Obergrenze. Chan begründet Half-Kelly damit, dass Schätzfehler
  asymmetrisch tödlich sind: Ein zu hohes `f` endet im Ruin, ein zu niedriges kostet nur Wachstum.
- **`f_ruin = 1 / |schlechteste Einzelrendite|`** als dritte, **modellfreie** Obergrenze. Eine
  Zeile Code, im Projekt bisher nicht vorhanden. Bei `f > f_ruin` ist die Wachstumsrate −1, also
  Totalverlust.

> **Korrektur gegenüber Revision 1:** Dort stand eine Tabelle, die Risiko pro Trade und Drawdown
> linear verknüpfte. **Das ist falsch.** Chan zeigt an Zahlen: Um den Drawdown zu halbieren, musste
> das Leverage durch **7** geteilt werden (simulierte Renditen) bzw. durch 1,5 (historische). Die
> Umrechnung ist nicht linear und wird gerechnet, nicht geschätzt. Chans Kompromiss: ein Leverage
> zwischen dem Ergebnis auf simulierten und dem auf historischen Renditen wählen.

**Warnsignal aus dem eigenen Bestand:** Laut `algo/PLAN.md`-Log vom 2026-08-07 handelt die
Silver-Bullet-Strategie „praktisch durchgehend am Margin-Limit" bei 20-fachem Hebel. Ob dieses
Leverage gegen Kelly und `f_ruin` vertretbar ist, wurde nie geprüft. **Pflichtprüfung vor jedem
weiteren Schritt.**

### 5.3 Schicht 2 — Dollar-Faktor-Deckel

**Ersetzt den paarweisen Korrelationsdeckel aus Revision 1.**

Die bestehende Wiki-Seite sagt: *„Jeder Trade wird unabhängig von anderen Trades desselben Tages
auf 1% Risiko bemessen."* Bei einem Instrument richtig. Bei mehreren dollargetriebenen Instrumenten
falsch — EURUSD, GBPUSD, USDJPY **und** die US-Index-Futures sind überwiegend eine Wette auf den
Dollar.

Paarweise Korrelationen zu messen greift zu kurz, sobald zwei Anlageklassen im Spiel sind.
Lustig/Roussanov/Verdelhan (2011, Review of Financial Studies) identifizieren den **Dollar-Faktor**
als gemeinsamen Risikofaktor, der einen Großteil der Mitbewegung erklärt. Bemerkenswert: Das ist
dieselbe Größe, die ICT „zuerst den USDX prüfen" nennt (siehe [[Intermarket Relationships]]) —
akademische Finanzmarktforschung und das ICT-Regelwerk beschreiben dasselbe Objekt.

**Regel:** Jede offene Position wird auf ihre gemessene Dollar-Empfindlichkeit umgerechnet; die
**Summe** der gleichgerichteten Dollar-Exponierung ist gedeckelt (Ausgangswert 2% des Guthabens,
Zahl wird aus den eigenen Daten bestimmt). Ein Maß statt einer Matrix, gültig über Anlageklassen
hinweg.

### 5.4 Schicht 3 — Tageslimit als Anomalie-Bremse

Ein Tagesverlustlimit hat für einen Algo keine statistische Rechtfertigung — er tiltet nicht. Es
bekommt eine andere Aufgabe: nicht „heute ist genug verloren", sondern „heute ist mehr verloren,
als der Backtest für möglich hält, also ist wahrscheinlich etwas kaputt". Schwelle abgeleitet aus
der simulierten Tagesverlust-Verteilung, nicht gewählt.

### 5.5 Schicht 4 — CPPI statt hartem Stopp

**Ersetzt den harten Abschaltpunkt aus Revision 1.** Aus
[[CPPI (Constant Proportion Portfolio Insurance)]] (Chan, Kap. 8) — laut dieser Seite hat der Vault
bisher **überhaupt keinen** Drawdown-Deckel, weder als Regel noch im Code.

```
D = 0,35 (maximal erlaubter Drawdown)

Trading-Subkonto :  D   × Gesamt-Equity
Cash-Konto       : (1−D) × Gesamt-Equity   — wird nie angetastet

Neues Allzeithoch → Subkonto auf D × Gesamt-Equity zurücksetzen
Verluste          → KEIN Transfer
Subkonto leer     → Strategie abschalten
```

Effektives Leverage = `D · f · (1 + drawdown)`. Der Faktor `(1 + drawdown)` ist 1 am Höchststand
und geht gegen 0, wenn sich der Drawdown `−D` nähert. Das Leverage schrumpft **automatisch und
stetig**, ohne dass man eine Regel dafür formulieren müsste — und macht es laut Chan „almost
impossible", die Grenze überhaupt zu erreichen.

Der Preis ist praktisch null: In Chans Simulation über 100.000 Tage liegt die Wachstumsrate bei
0,002484 gegen 0,002525 ohne CPPI — bei 0,5 statt 0,9 maximalem Drawdown.

Nebeneffekt, den Chan hervorhebt: ein **geordneter Weg, eine verlierende Strategie stillzulegen**,
statt sie am emotionalen Zusammenbruch scheitern zu lassen.

**Die eine Einschränkung, die uns trifft:** CPPI funktioniert nur bei **Ein-Strategie-Konten** —
sonst subventionieren profitable Strategien die kaputten quer, der Drawdown wird nie groß genug,
und die kaputte Strategie bleibt unbemerkt am Leben. **Konsequenz für dieses Projekt: pro Strategie
ein eigener CPPI-Hochwasserstand mit eigenem Subkonto-Anteil**, nicht einer fürs Gesamtkonto.

Die zweite Einschränkung (kein Schutz über Nacht) trifft uns nicht — Intraday-Flat ist Pflicht.

Zur Ehrlichkeit der Drawdown-Schätzung selbst siehe [[Grenzen für Einzelrenditen & Drawdown]]:
Masters' Doppel-Bootstrap, weil der naive Bootstrap katastrophale Drawdowns um mehr als das
Zehnfache unterschätzt. *„Optimistic OOS samples work against us far more strongly than pessimistic
samples work for us."*

### 5.6 Schicht 5 — Annahme-Wächter

Schranken für gruppierte Ergebnisse (monatlich/quartalsweise) berechnen und den Live-Betrieb
dagegen laufen lassen — *„we can then use these bounds to track ongoing performance and detect
deterioration."*

Reaktion: **erst halbe Positionsgröße, bei weiterer Verschlechterung Stopp.** Meldung in beiden
Stufen.

> **Verstärkte Begründung gegenüber Revision 1.** Dort war diese Schicht nur ein Defekt-Melder.
> Neely/Weller (Adaptive Markets Hypothesis) zeigen für den Devisenmarkt: Die Überrenditen
> technischer Regeln der 70er und 80er waren **echt**, kein Data Mining — aber bis Anfang der 90er
> verschwunden. Weniger untersuchte Regeln sind zurückgegangen, aber wahrscheinlich nicht ganz weg.
> **Edges sterben planmäßig, nicht nur bei Defekt.** Laufende Nachvalidierung ist damit strukturell
> notwendig. Nebenaussage, die für ICT spricht: Gerade *weniger* verbreitete Regelwerke behalten
> laut dieser Untersuchung eher Rest-Edge als die kanonischen Standardindikatoren.

### 5.7 Schicht 6 — Ausführungskosten

Kissells Marktwirkungs-Modelle sind für Ordergrößen gebaut, die den Markt bewegen — bei diesem
Kontostand nicht zutreffend. Übertragbar ist **Implementation Shortfall**: die Differenz zwischen
Entscheidungs- und Füllpreis. Siehe die bestehende Wiki-Seite
[[Implementation Shortfall]] — im dortigen Buchbeispiel gehen **52% des Ideenwerts** in der
Ausführung verloren.

**Kostenannahmen im Backtest** (nach Recherche zu realistischen Retail-Werten): Für Retail-Futures
sind **15–25 Basispunkte Round-Trip** realistisch, gegenüber etwa 7 Basispunkten für
institutionelle Ausführung. Die Kostenannahme wird **konservativ** gesetzt und laufend gegen die
gemessenen Ist-Werte geprüft. Modellierung nach
[[Transaktionskosten-Taxonomie (Kissell)]] (zehn Komponenten, fix/variabel und sichtbar/verborgen).

**Das ist im Projekt bereits einmal schiefgegangen:** Laut
[[Ensemble-Strategie — Backtest-Ergebnis & Commission-Verzerrung (laufend)]] fraßen $19.757
Kommission (Prozent-vom-Notional-Modell statt Futures-Fixbetrag) eine Brutto-Edge von ~+18,9%
vollständig auf. Ein korrektes Kostenmodell ist damit kein Nebenaspekt, sondern der bislang
größte gemessene Profitabilitätshebel des Projekts.

### 5.8 Schicht 7 — Steuern und Kontowährung

Für die Beurteilung, ob eine Strategie sich lohnt, zählt der Nettoertrag.

**Kontowährung.** Das Konto lautet auf Euro, gehandelt werden überwiegend US-Dollar-Produkte. Jeder
Gewinn und Verlust entsteht damit zunächst in Dollar und trägt eine zusätzliche
Währungsempfindlichkeit, die nichts mit der Strategie zu tun hat. Zwei Konsequenzen: Der Backtest
rechnet in der **Produktwährung**, nicht in Euro, damit Strategieergebnis und Wechselkurseffekt
nicht vermischt werden. Und der Wechselkurseffekt wird im Betriebsprotokoll **getrennt** ausgewiesen.
Eine Absicherung ist bei dieser Kontogröße nicht sinnvoll — aber sie muss sichtbar sein, statt still
in die Strategiezahlen zu wandern.

- Die **Verlustverrechnungsbeschränkung für Termingeschäfte** (§20 Abs. 6 EStG, 20.000 € Deckel)
  wurde mit dem Jahressteuergesetz 2024 aufgehoben, verpflichtend umgesetzt seit **1. Januar 2026**.
  Verluste sind wieder vollumfänglich mit Kapitalerträgen verrechenbar. Hätte die Regel Bestand
  gehabt, wäre eine Strategie mit vielen Trades steuerlich kaum tragfähig gewesen.
- **IBKR führt als ausländischer Broker keine Kapitalertragsteuer ab.** Erklärung erfolgt selbst
  über die Anlage KAP.
- Backtest-Berichte weisen Brutto aus; die Netto-Betrachtung erfolgt separat und wird nicht in die
  Optimierung gezogen.

### 5.9 Handelsfrequenz — keine Obergrenze

**Es gibt keine Höchstzahl an Trades pro Tag.** Der Algo handelt so oft, wie gültige Setups
entstehen, bis eine Schicht des Risikomodells eingreift. Das ist die direkte Anwendung des
Prinzips aus 5.0: „Maximal zwei Trades am Tag" ist eine Psychologieregel, die einen Menschen vor
Übermüdung und Rachehandel schützt. Ein Algorithmus wird nicht müde.

Zwei Auflagen dazu:

1. **Erst nach ausreichendem Backtesting.** Bis dahin gilt eine vorläufige Begrenzung, weil eine
   unbegrenzt handelnde, unvalidierte Regel den schnellstmöglichen Weg zum Drawdown darstellt. Die
   Aufhebung ist an dieselbe Bedingung geknüpft wie die Umstellung der Positionsgröße: gemessene
   Verteilung statt Annahme.
2. **Technische Sicherung gegen pathologisches Wiederholen.** Das ist ausdrücklich *keine*
   Tagesgrenze, sondern ein Schutz gegen einen Programmfehler: Wenn dieselbe Struktur bei jedem
   Kerzenschluss neu erkannt wird, feuert der Algo denselben Trade zwanzigmal, ohne dass es
   zwanzig Gelegenheiten gäbe. Jedes Setup bekommt deshalb eine Kennung; ein bereits gehandeltes
   Setup löst kein zweites Mal aus. Ohne diese Sicherung ist „unbegrenzt" kein Freiheitsgrad,
   sondern ein Fehlerverstärker — und die Kosten aus 5.7 skalieren linear mit.

**Das Risikomodul bleibt bewusst offen für Verfeinerung.** Die sieben Schichten sind eine
Ausgangsfassung, kein Endzustand. Jede Verfeinerung wird in `algo/PLAN.md` protokolliert und geht
durch dieselben Extremfall-Tests aus 9.7 wie die Erstfassung — der Risiko-Wächter ist die
Komponente, an der ein Fehler das Konto kostet, nicht nur einen Trade.

### 5.10 Harte Verbote

Im Risiko-Wächter verdrahtet, von keiner Strategie umgehbar:

1. **Keine Vergrößerung einer Verlustposition.** Kein Nachkaufen, kein Verdoppeln nach Verlust.
2. **Nie ohne Stop.** Der Stop liegt als echte Order beim Broker, nicht als Absicht im Programm —
   bei Verbindungsabbruch oder Absturz schützt eine Absicht nichts.
3. **Stop nur in Gewinnrichtung verschiebbar**, nie weiter weg.

Zusätzlich gilt das ICT-Regelwerk als Strukturschicht darüber.

### 5.11 Prüfreihenfolge im Risiko-Wächter

1. Stop vorhanden?
2. Setup bereits gehandelt (Kennung aus 5.9)?
3. Position im selben Instrument bereits offen?
4. Größe ≤ 1% des aktuellen Guthabens?
5. Größe ≤ halber Kelly und ≤ `f_ruin`?
6. Dollar-Faktor-Deckel eingehalten?
7. Tagesverlust unter Anomalieschwelle?
8. CPPI-Subkonto der Strategie noch gedeckt?
9. Annahme-Wächter ruhig?
10. Sperrkalender abrufbar?
11. Red-Folder-News innerhalb der nächsten 20 Minuten?
12. Bankfeiertag oder Börsenfeiertag?
13. Handelsende (Intraday-Flat) in Reichweite?
14. Uhrzeit des Rechners verifiziert?

Fällt eine Prüfung durch, entsteht kein Trade — und der Grund wird protokolliert, damit auswertbar
bleibt, wie oft welche Bremse gegriffen hat.

**Abgrenzung zum Triad-Veto:** Die Interest Rate Triad (Abschnitt 7.2) und der Regime-Filter sind
**keine** Risikoprüfungen, sondern Teil der Regelschicht — sie entscheiden, ob ein Setup gültig
ist, nicht ob es tragbar ist. Reihenfolge: Regelschicht erzeugt einen Vorschlag → Triad und
Regime-Filter können ihn verwerfen → erst der überlebende Vorschlag geht in die vierzehn Prüfungen.
Grund: Der Risiko-Wächter muss für jede künftige Strategie unverändert gelten, auch für solche
ohne Benchmark-Bestätigung.

---

## 6. Sperrquellen

### 6.1 Red-Folder-News

**Keine Positionen von 20 Minuten vor bis 20 Minuten nach dem Termin.** Offene Positionen werden
vor dem Fenster geschlossen, nicht mit Stop weiterlaufen gelassen.

> ⚠️ **Bewusste Abweichung vom Wiki.** [[ICT Killzones]] sagt: *„News (Red Folder) liefern die
> Volatilität für die größten Moves des Tages."* Bei ICT sind News der Treibstoff. Diese Spec
> entscheidet dagegen — Begründung: ICT beschreibt die **Preisrichtung**, die Sperre schützt vor der
> **Ausführung**. In den Sekunden der Veröffentlichung weitet sich der Spread um ein Vielfaches, und
> der Backtest kennt das nicht. Der Widerspruch wird im Wiki markiert, nicht überschrieben.

**Bekannter Preis:** Die wichtigen US-Termine liegen 8:30 und 14:00 NY-Zeit, also mitten in NY AM
und NY PM. An Tagen mit Arbeitsmarktdaten oder Zinsentscheidung fällt ein Teil der Killzone weg.

**Wechselwirkung mit der Zwei-Stufen-Hypothese.** [[Two Stage News Delivery (FOMC & NFP)]]
dokumentiert am NFP vom 07.08.2026: Stage 1 um 08:30, **Stage 2 um 10:12** — also rund 1h42min
später, mitten im Silver-Bullet-Fenster NY AM. Ein Fenster von ±20 Minuten um 08:30 erfasst Stage 2
**nicht**, und das ist beabsichtigt: Stage 2 läuft bei normalen Spreads. Festgehalten, damit es
nicht als Lücke missverstanden wird. Die Beobachtungsschicht markiert beide Stufen getrennt.

**Nebeneffekt:** Der Wirtschaftskalender schließt den auf jener Seite notierten offenen Punkt
„Datumsliste der Termine fehlt aktuell noch im Repo".

### 6.2 Feiertage

Gesperrt wird an **US-Bankfeiertagen UND Börsenfeiertagen** (Vereinigungsmenge). Karfreitag ist
kein Bankfeiertag, aber Anleihemärkte sind zu — die Interest Rate Triad hätte keine Daten.
Umgekehrt sind Columbus Day und Veterans Day Bankfeiertage bei geöffneter Börse, aber mit dünnem
Handel.

**Zeitumstellung:** USA und EU wechseln an unterschiedlichen Terminen. Alle Zeitfenster sind in
**New Yorker Zeit** definiert und werden nie in lokaler Zeit gerechnet.

### 6.3 Fail-Closed

**Ist ein Sperrkalender nicht abrufbar, wird nicht gehandelt.** Ein Algo, der nicht weiß, wann News
kommen oder ob heute Feiertag ist, kann die Regeln nicht einhalten.

---

## 7. Instrument-Register

### 7.1 Umfang

| Zweck | Instrumente |
|---|---|
| **Gehandelt (Devisen)** | EURUSD, GBPUSD, USDJPY |
| **Gehandelt (CME)** | MNQ, MES — später E-nano, sobald Liquidität gemessen |
| **Benchmark** | DXY (gerechnet, siehe 7.3) |
| **Bestätigung (Interest Rate Triad)** | ZB (30J), ZN (10J), ZF (5J) |
| **DXY-Bestandteile** | USDCAD, USDSEK, USDCHF |
| **Beobachtet** | ES, NQ |

**Killzone-Zeiten unterscheiden sich je Anlageklasse** und werden pro Instrument im Register
hinterlegt, nicht global. Für Devisen laut Market Maker Primer: London 2–5 NY (EUR/GBP, 25–50 Pips),
New York 7–9 NY (Majors, 20–30 Pips), London Close 10–12 NY (Majors, 10–20 Pips). Die
Index-Futures-Fenster (Silver Bullet 3–4 / 10–11 / 14–15) sind davon getrennt zu führen.

### 7.2 Interest Rate Triad als Bestätigungsfilter

Aus [[Intermarket Relationships]]:

- Triad = 30-Jahre, 10-Jahre, 5-Jahre US-Zins-Futures.
- **Distribution (bearish):** Benchmark höheres Hoch, mindestens einer der drei niedrigeres Hoch.
- **Akkumulation (bullish):** Benchmark niedrigeres Tief, mindestens einer höheres Tief.
- **Eine** Divergenz unter dreien genügt.
- **Workflow:** Trifft der Preis auf der Benchmark einen vorab markierten Order Block, Liquidity
  Pool oder FVG, wird die Triad geprüft. Keine Divergenz → Setup **verworfen**.

**Regime-Filter:** Laufen USDX und Bonds **zusammen** statt entgegengesetzt, fehlen Trending
Conditions. Kann Setups ganzer Tage aussortieren.

**Paarauswahl vor Chartanalyse:** *„Zuerst den USDX auf klare Divergenz prüfen, dann das Paar
wählen."* Ergänzend aus [[SMT Smart Money Technique (Source)]]: *„im Forex immer gegen den DXY,
Paare sollen failen."*

### 7.3 DXY wird gerechnet, nicht gekauft

Berechnung aus den sechs Bestandteilspaaren nach der öffentlichen Formel. Vorteile: keine
Datenlizenz; Minutenauflösung über den gesamten Zeitraum; alle Bestandteile über denselben
Devisen-Zugang, der bei IBKR **kein Marktdaten-Abo** erfordert.

**Pflichtprüfung vor Verwendung:** Gegen eine unabhängige Referenz prüfen. Der Unterschied zwischen
Kassa-Index und Futures-Kontrakt (Basis/Carry) ist real und muss benannt werden.

### 7.4 Offene Datenrisiken

| Risiko | Klärung |
|---|---|
| CBOT-Zins-Futures im IBKR-Zugang enthalten? | Vorabtest, Abschnitt 10.1 |
| CME-Abo für MNQ/MES vorhanden? | Vorabtest |
| E-nano: Liquidität, Spread, IBKR-Unterstützung | Ab 24.08.2026 messen, nicht annehmen |

**Zu E-nano im Besonderen:** Der Multiplikator ist ein Zehntel des Micro E-mini (~$0,20/Punkt
Nasdaq), aber **die Tick-Inkremente sind doppelt so grob**. In Punkten kostet jeder Trade damit
relativ mehr Spread, und Einstiege auf FVG-Mittelpunkte werden gröber aufgelöst. Ob der Vorteil bei
der Positionsgröße den Nachteil bei der Auflösung überwiegt, wird **gemessen**, sobald die
Kontrakte laufen. Bis dahin baut nichts darauf auf.

Falls die Zins-Futures fehlen: Die vorhandenen FRED-Daten enthalten die 10-Jahres-Rendite, aber nur
als Tageswert — für eine Divergenzprüfung im Moment des Levelkontakts reicht das nicht.

---

## 8. Fehlerbehandlung

Grundregel: **Im Zweifel nicht handeln.** Ein verpasster Trade kostet nichts, ein Trade auf falscher
Grundlage schon.

| Störung | Reaktion |
|---|---|
| Verbindung zu IBKR weg | Keine neuen Trades. Laufende Positionen geschützt, weil der Stop als echte Order beim Broker liegt. Bei Rückkehr: Abgleich |
| Programm stürzt ab / Strom weg | Dasselbe. Beim Neustart wird der Zustand **vom Broker gelesen**, nie aus lokaler Datei rekonstruiert |
| Sperrkalender nicht abrufbar | Kein Handel |
| Lücke im Kursstrom | Kein Handel im betroffenen Instrument, andere laufen weiter |
| Unbekannte Position im Konto | Sofortiger Stopp + Meldung |
| **Uhr des Rechners falsch** | Sofortiger Stopp |
| IB-Gateway-Trennung nach ~24 h | Automatischer Neustart, danach Zustandsabgleich |

### 8.1 Zeitprüfung

Killzone-, Macro- und News-Fenster sind Zeitfenster. Geht die Uhr zwei Minuten falsch, handelt der
Algo systematisch im falschen Moment — und **keine Zahl im Protokoll sieht auffällig aus.** Prüfung
gegen eine externe Zeitquelle beim Start und laufend; Abweichung über einer Sekunde bedeutet Stopp.

### 8.2 Der Broker ist die Wahrheit

Was der Algo zu besitzen glaubt, ist eine Vermutung; was IBKR meldet, ist der Stand. Bei jedem
Abgleich gewinnt IBKR.

### 8.3 Not-Aus

Eine Datei, deren bloßes Vorhandensein den Algo stoppt — funktioniert auch, wenn er sonst nicht
mehr reagiert. Zusätzlich immer der direkte Weg über TWS.

---

## 9. Validierungs-Gate

**Vollständig überarbeitet gegenüber Revision 1**, wo nur vage „Walk-Forward und Permutationstest"
stand.

### 9.1 Vorprüfung der Indikatoren

Vor der Strategie kommt der Indikator. Aus [[Indikator-Stationarität & Entropie]]: STATN-Analyse
gegen langsames Wandern, relative Entropie ≥ 0,5, monotones Tail-Cleaning. Ein instationärer oder
informationsarmer Indikator kann keine tragfähige Regel ergeben.

### 9.2 Der Vier-Stufen-Prozess (Masters)

Aus [[Vier-Stufen-Strategieentwicklung (Masters)]]:

1. **In-Sample Excellence.** Optimierung auf Entwicklungsdaten. Zwei Leitfragen: Ist das Ergebnis
   exzellent? Ist es offensichtlich overfittet? (Verdächtig gute Zahlen deuten fast immer auf
   Future-Leak hin.)
2. **In-Sample MCPT.** Prüft, ob die Exzellenz auf echten Mustern beruht oder auf Data-Mining-Bias.
   Erst bei P < 1% lohnt es sich, Validierungsdaten anzufassen.
3. **Walk-Forward** mit **Guard Buffer** `OMIT = min(Lookahead, Lookback) − 1`. Ohne Puffer
   erreicht ein wertloses System auf Zufallsdaten `t = 74,64` — siehe
   [[Walk-Forward Guard Buffer & Varianz-Inflation]].
4. **Walk-Forward MCPT.**

Gehandelt wird nur bei sehr niedrigen P-Werten in **Stufe 2 und 4** — unabhängig davon, wie gut die
Rohkennzahlen aussehen. Eine mittelmäßige, aber abgesicherte Strategie schlägt eine exzellente,
nicht abgesicherte.

**Kennzahlen auf Bar-Granularität**, nicht auf Trade-Basis. Aus [[Profit pro Bar vs. pro Trade]]:
Trade-basierte Kennzahlen sind unbrauchbar (Profit Factor ∞ statt 1,01).

### 9.3 Nested Walkforward — Pflicht, nicht optional

Aus [[Nested Walkforward]], wörtlich: Solange die Gewichtung **statisch** ist, greift das Kapitel
nicht. *Sobald daraus eine Auswahl wird — „heute handelt die Regel, die zuletzt am besten lief" —,
reicht der einschichtige Walk-Forward nicht mehr aus, und alle dort berichteten Zahlen wären
selection-biased.*

**Das Regelregister dieser Spec ist genau so eine Auswahl.** Damit ist Nested Walkforward
verbindlich. `algo/masters.py::permute_multi` liefert den Permutationsteil bereits; die drei
Segmentgrenzen müssen getrennt permutiert werden.

Ebenso zu beachten: [[Training Bias & Selection Bias]] — Stufe 3/4 beseitigen nur die erste der
beiden Verzerrungen.

### 9.4 Mehrfachtest-Korrektur — neuer Pflichtbaustein

**Fehlte in Revision 1 vollständig und ist im gesamten Vault nicht vorhanden.**

Das Projekt wird sehr viele Regeln testen: das gesamte ICT-Regelwerk plus alle Explorationsfunde.
Masters' MCPT behandelt den Data-Mining-Bias **einer** Strategie. Er behandelt **nicht** das
Problem, aus vielen getesteten Regeln die beste auszuwählen.

- **Sullivan/Timmermann/White (1999, Journal of Finance)** — genau dieser Aufbau, empirisch
  geprüft: Aus einem großen Universum technischer Regeln war die beste selbst nach
  Data-Snooping-Korrektur in-sample überlegen, **in den folgenden zehn Jahren aber nicht mehr**.
  Bei S&P-500-Futures kein Beleg für Überlegenheit, sobald Data-Snooping berücksichtigt wurde.
- **Harvey/Liu (2015, Journal of Portfolio Management)** — Haircut für Mehrfachtests. Kernbefund:
  Der Abschlag ist **nichtlinear**; hohe Sharpe Ratios werden moderat, marginale stark bestraft.
  Wörtlich: *„it is a serious mistake to use the rule of thumb 50% haircut."* Liefert zusätzlich
  eine Ertragsschwelle, die eine Strategie überschreiten muss.
- **Bailey/López de Prado — Deflated Sharpe Ratio** — korrigiert gleichzeitig für Selektionsbias
  bei Mehrfachtests, Stichprobenlänge und Nicht-Normalverteilung der Renditen.

**Anforderung an die Umsetzung:** Die Zahl der getesteten Regelvarianten wird **gezählt und
protokolliert** — sonst ist keine dieser Korrekturen berechenbar. Das gilt auch für verworfene
Versuche. Ohne diese Buchführung sind alle späteren Signifikanzaussagen wertlos.

### 9.5 Entry-Regel isoliert testen

Aus [[Rule Significance Test (RST)]]: Signifikanztest **nur der Entry-Regel**, vor Sizing, Stop und
Ziel. Sonst lässt sich nicht unterscheiden, ob der Vorteil aus dem Einstieg oder aus dem
Trade-Management stammt.

### 9.6 Markierter Widerspruch: Cross-Validation

> ⚠️ **Zwei Autoritäten widersprechen sich, bewusst nicht aufgelöst.**
> [[Cross Validation vs. Walk-Forward (Masters)]] rät von Cross-Validation auf Marktdaten ab.
> López de Prado hält sie mit **Purging und Embargo** für tragfähig und baut darauf CPCV
> (Combinatorial Purged CV) auf, das mehrere Testpfade erzeugt statt eines.
>
> Bemerkenswert: López de Prados **Embargo** und Masters' **Guard Buffer** sind derselbe
> Mechanismus unter zwei Namen. Zwei unabhängige Autoren kommen auf dieselbe Lösung — das spricht
> stark für den Mechanismus, unabhängig davon, wer im Streit um CV recht hat.
>
> **Vorgehen für dieses Projekt:** Walk-Forward als Hauptverfahren (Masters), CPCV als
> Zweitmeinung, wo die Datenmenge knapp ist. Kein Verfahren allein entscheidet.

### 9.7 Vier Test-Ebenen im Code

1. **`algo/selfcheck.py`** — Eintrag pro neuem Baustein, nach jeder Änderung.
2. **Risiko-Wächter gegen erfundene Extremfälle** — Nullgröße, Stop auf Einstiegspreis, Konto im
   Minus, zehn Signale in derselben Sekunde, Kalender liefert Unsinn. Wichtiger als
   Strategietests: Eine schlechte Strategie kostet Geld, ein kaputter Risiko-Wächter das Konto.
3. **Bestehende Backtest-Standards** aus `CLAUDE.md` — echter Punktwert, konservative Auflösung bei
   Stop und Ziel in derselben Kerze (`dubious_pct` als Pflichtkennzahl), kein Lookahead.
4. **Live-Schleife gegen aufgezeichnete Daten**, Trades mit denen des Backtests verglichen.
   Unterschiedliche Trades bei identischen Daten heißt: einer der beiden ist falsch.

Danach: drei Monate Papierhandel, Ergebnisse innerhalb der berechneten Schranken.

---

## 10. Erste Ausbaustufe

**Ziel:** Belegen, ob sich die ICT-Konzepte auf Devisen übertragen. Gemessen, nicht vermutet. Kein
einziger Trade, auch kein simulierter.

### 10.1 Vorabtest, vor allem anderen

Kommt über den IBKR-Zugang Devisen-Historie herein? Sind CBOT-Zins-Futures und CME-Index-Futures
verfügbar? Ein Papierkonto genügt; Devisendaten erfordern laut IBKR **kein Abo und kein gefundetes
Konto**.

Reicht die Berechtigung nicht, ist der Rest hinfällig. Dieser Test läuft, **bevor** eine Zeile
Aufbau entsteht.

### 10.2 Umfang

| # | Was | Ergebnis |
|---|---|---|
| 1 | `algo/instruments.py` | Register nach Abschnitt 7.1, mit Killzone-Zeiten je Anlageklasse |
| 2 | `algo/broker_ibkr.py` | Nur lesend. **Keine Order-Funktion vorhanden** — nicht abgeschaltet, sondern nicht geschrieben |
| 3 | Datenimport | 6 Monate Minutenkerzen, Devisen + Zins-Futures |
| 4 | DXY-Berechnung | Aus den sechs Bestandteilen, gegen Referenz geprüft |
| 5 | `algo/verify_data.py` | Prüfroutine — der eigentliche Wert dieser Stufe |
| 6 | `algo/observe.py` | Bestehende Detektoren über alle Instrumente, 24/5 |
| 7 | Erster Bericht | Abschnitt 10.4 |

### 10.3 Abnahmekriterien

- Aus Minutenkerzen gerechnete **Tageskerzen stimmen mit IBKRs eigenen überein** — alle
  Instrumente, gesamter Zeitraum. Prüft 17:00-Grenze und Zeitzonenlogik gleichzeitig.
- **Jede** Lücke aufgelistet und erklärt (Wochenende, Feiertag, Broker-Wartung).
- Stichprobe von Zeitstempeln gegen vorhandene TradingView-Exporte passt.
- Gerechneter DXY stimmt mit unabhängiger Referenz überein, Abweichungen erklärt.
- Beobachtung läuft über sechs Monate und alle Instrumente durch.
- `algo/selfcheck.py` hat einen Eintrag pro neuem Baustein.
- `algo/README.md`, `algo/PLAN.md` gepflegt; `CLAUDE.md` auf das neue Zielbild angepasst.

### 10.4 Was der erste Bericht beantwortet

- Bilden sich FVGs im Devisenmarkt gleich häufig wie bei Index-Futures?
- Funktionieren die Killzone-Fenster dort, oder liegen die Bewegungen zu anderen Zeiten?
- Wie oft folgt auf einen Sweep tatsächlich ein Strukturbruch?
- **Rundzahl-Test.** Osler (2003) findet im Devisenmarkt starke Häufung von Take-Profit-Orders *an*
  runden Zahlen und von Stop-Losses *knapp jenseits* davon. Das eigene Wiki
  ([[Statistische Muster jenseits der ICT-Konzepte (laufend)]]) fand bei MNQ **keinen**
  Rundzahl-Magnetismus. Erster Test mit starker akademischer Erwartung — und ein direkter
  Prüfstein, ob sich Devisen und Index-Futures hier grundsätzlich unterscheiden.
- Wie groß ist die Dollar-Empfindlichkeit je Instrument? Daraus entsteht der Deckel aus 5.3.
- Wie oft zeigt die Interest Rate Triad Divergenz an einem Levelkontakt — und wie oft nicht?
- **Runner-Häufigkeit:** Wie oft entsteht ein 9R–15R-Lauf? Entscheidet über die Machbarkeit des
  Ertragsziels aus 3.1.
- SMT-Divergenz wird zum ersten Mal überhaupt messbar.

Das sind **keine Handelsregeln**, sondern die Grundlage, auf der die erste Regel entsteht.

### 10.5 Nicht in Stufe 1

Regelregister, Validierungs-Gate, Risiko-Wächter, Sperrkalender, Live-Schleife, Order-Code.
Stufe 2 wäre Regelregister und Gate, Stufe 3 Risiko-Wächter und Papierhandel. Beide werden jetzt
nicht spezifiziert — was in Stufe 1 herauskommt, ändert vermutlich ihren Zuschnitt.

---

## 11. Akademische Absicherung

Ergebnis der Gegenprüfung: Was von den ICT-Grundannahmen trägt akademisch, was nicht.

| ICT-Annahme | Akademischer Befund | Bewertung |
|---|---|---|
| Liquidity Pools, Sweeps, Stop-Jagd | **Osler (2003, Journal of Finance)**: Take-Profit-Orders häufen sich an runden Zahlen, Stop-Losses knapp dahinter; Stop-Losses erzeugen selbstverstärkende Preiskaskaden. Aus echten Bank-Orderbüchern | **Gestützt**, und zwar speziell für Devisen |
| „Time before Price" | **Andersen/Bollerslev (1998, Journal of Finance)**: ausgeprägte Tageszeit-Muster und starke News-Effekte in DEM/USD-5-Minuten-Renditen | **Teilweise gestützt** — belegt ist die Periodizität der **Volatilität**, nicht der **Richtung**. ICT behauptet beides |
| DXY zuerst prüfen | **Lustig/Roussanov/Verdelhan (2011, RFS)**: Dollar-Faktor als gemeinsamer Risikofaktor | **Gestützt** — dasselbe Objekt unter anderem Namen |
| Technische Regeln funktionieren dauerhaft | **Neely/Weller**: FX-Überrenditen der 70er/80er echt, aber bis Anfang der 90er verschwunden; weniger untersuchte Regeln nur teilweise zurückgegangen | **Eingeschränkt** — Edges zerfallen. Begründet Schicht 5 |
| Beste Regel aus vielen auswählen | **Sullivan/Timmermann/White (1999)**: beste Regel aus großem Universum hielt out-of-sample nicht | **Warnung** — begründet Abschnitt 9.4 |

**Was daraus folgt:** Der ICT-Ansatz ist nicht akademisch haltlos — die Mikrostruktur-Literatur
stützt die Kernmechanik in Devisen überraschend direkt. Die Einschränkungen liegen woanders:
Richtungsvorhersage aus Zeit allein ist nicht belegt, Edges zerfallen, und die Auswahl der besten
aus vielen Regeln ist der gefährlichste Schritt im gesamten Vorhaben.

---

## 12. Folgearbeiten im Wiki

Nach Freigabe zu erledigen (Pflicht laut `CLAUDE.md`, „Kontinuierliches Wachstum"):

- **Neue Concept-Seite** Deflated Sharpe Ratio / Harvey-Liu-Haircut / Reality Check — im Vault
  komplett fehlend, obwohl der Rest der Validierungsliteratur dicht abgedeckt ist.
- **Neue Concept-Seite** Purged CV & Embargo (López de Prado), mit dem markierten Widerspruch zu
  Masters und dem Hinweis auf die Äquivalenz Embargo ↔ Guard Buffer.
- **Neue Concept-Seite** Marktmikrostruktur-Belege (Osler, Andersen/Bollerslev,
  Lustig/Roussanov/Verdelhan) — die akademische Unterfütterung der ICT-Liquiditätskonzepte.
- **Neue Synthesis-Seite** Strukturregeln gegen Psychologieregeln (Abschnitt 5.0).
- **[[Risikomanagement (1% pro Trade)]]** — Dollar-Faktor-Deckel ergänzen. Die Formulierung
  „unabhängig von anderen Trades desselben Tages" ist bei mehreren dollargetriebenen Instrumenten
  irreführend.
- **[[ICT Killzones]]** — Red-Folder-Abweichung als Widerspruch markieren.
- **[[Statistische Muster jenseits der ICT-Konzepte (laufend)]]** — Osler-Erwartung zum
  Rundzahl-Magnetismus als offene Hypothese eintragen (bisheriger Befund stammt nur aus MNQ).
- **[[Meine Strategien (Übersicht)]]** — Verweis auf diese Spec als übergeordnetes Zielbild.
- **[[Two Stage News Delivery (FOMC & NFP)]]** — Verweis, dass der Sperrkalender die dort notierte
  fehlende Terminliste liefert.
- **`wiki/log.md`** — Eintrag vom Typ `synthesis`.

---

## 13. Offene Punkte

| # | Punkt | Wann geklärt |
|---|---|---|
| 1 | IBKR-Berechtigung für Devisen-Historie | Vorabtest, 10.1 |
| 2 | CBOT-Zins-Futures und CME-Index-Futures verfügbar? | Vorabtest |
| 3 | E-nano: Liquidität, Spread, IBKR-Unterstützung | ab 24.08.2026 messen |
| 4 | Endgültige Kontogröße | vor Live-Freigabe |
| 5 | Gemessene Dollar-Empfindlichkeit je Instrument | erster Bericht |
| 6 | Konkrete Zahlen für Anomalieschwelle und Positionsgröße | nach 100 OOS-Trades |
| 7 | Kelly und `f_ruin` für die bestehende Silver-Bullet-Strategie | **vor jedem weiteren Schritt** — 20× Hebel am Margin-Limit ist ungeprüft |
| 8 | Runner-Häufigkeit (9R–15R) | erster Bericht |
| ~~9~~ | ~~Manueller Handel auf demselben Konto?~~ | **Geklärt 2026-08-08: eigenes Konto nur für den Algo** (Entscheidung 24) |
| 10 | Silver Bullet überarbeiten, bevor die Strategie ins Regelregister wandert | Kalendereintrag 2026-09-01, siehe Abschnitt 13.1 |

---

### 13.1 Terminierte Folgearbeit

**Silver Bullet überarbeiten** — Kalendereintrag 2026-09-01, 10:00–11:30 (Platzhalter nach
Abschluss der Datenschicht). [[Silver Bullet Model]] ist bisher die einzige vollständig geregelte
Strategie im Vault und wandert **nicht** unverändert ins Regelregister. Zu klären:

1. Kelly und `f_ruin` berechnen (offener Punkt 7 — 20-facher Hebel am Margin-Limit, ungeprüft).
2. Übertragbarkeit auf Devisen: Die drei Fenster (London 3–4, NY AM 10–11, NY PM 14–15) stammen
   aus dem Index-Kontext; die FX-Killzones liegen anders (2–5, 7–9, 10–12 NY-Zeit).
3. Durch das Validierungs-Gate aus Abschnitt 9 schicken, nicht als validiert übernehmen.
4. Kostenmodell korrigieren (siehe 5.7).

---

## 14. Bewusst nicht enthalten

Keine Nutzeroberfläche, kein Dashboard, keine Datenbank (Dateien genügen), keine
Broker-Abstraktion für mehrere Broker, keine Warteschlange zwischen den Bausteinen.

Alles davon ist später nachrüstbar und würde jetzt Bauzeit kosten, bevor etwas läuft. `CLAUDE.md`
stuft Optik-Wünsche ausdrücklich als nachrangig ein.
