---
tags: [synthesis, algo, forex, backtest, laufend]
created: 2026-08-15
updated: 2026-08-15
sources: ["[[Silver Bullet Model]]", "[[ICT Daily Range Session Timing]]", "[[Fair Value Gap (FVG)]]"]
---

# Forex-Algo — ICT-Konzepte auf 23 Jahren (laufend)

Diese Seite hält fest, wie sich die ICT-Konzepte aus diesem Vault schlagen, wenn man sie **auf
zehn Währungspaare über 23 Jahre** loslässt statt auf die zweistellige MNQ-Tagesmenge. Sie wächst
mit jedem Lauf; ältere Zahlen werden ersetzt, nicht als Schnappschuss stehengelassen.

Technischer Unterbau: `algo/forex/` (Regel-, P&L- und Simulationsschicht), Spec
`docs/superpowers/specs/2026-08-15-forex-algo-phase2-design.md`. Die MNQ-Module bleiben davon
unberührt — beide Serien laufen getrennt.

## Was übertragen wurde und was nicht

Kriterium ist ein einziger Satz: **setzt das Konzept die 9:30-Eröffnung als Ereignis voraus?**
Ein 24/5-Markt hat weder Schluss noch Eröffnung.

**Läuft auf Forex:** [[Silver Bullet Model]] (1st presented FVG *im Fenster*), [[Fair Value Gap
(FVG)]] inkl. Stärke-Einstufung, Swings/MSS, High-Probability-FVG, Liquiditäts-Level,
[[IPDA]]-Fenster, [[ICT Killzones|Killzones]], [[Midnight Opening Range]], Macros, **NWOG**
(Wochenendgap Fr 17:00 → So 17:01 ist real und im Bestand belegt), 1 %-Risiko, Kill-Switch.

**Entfällt:** [[ORG (Opening Range Gap) & 1st Presented FVG|ORG]] und dessen C.E.,
ORG-Standardabweichungs-Extrema, 1.p FVG des Tages und der Woche, 1p-Mindestgröße, erstes FVG
nach 9:30, Open Drive, **NDOG**, alle RTH-Varianten.

> Folge für die [[ORG (Opening Range Gap) & 1st Presented FVG|ORG-C.E.-70-%-These]]: Sie lässt
> sich über Forex **nicht** breiter absichern und bleibt auf der MNQ-Stichprobe (dort aktuell
> 35–43 %). Jannes hat sie ausdrücklich als „weiter beobachten" markiert — sie bleibt bestehen
> und wird weiter kommentiert, nicht abgehakt.

## Erstes Ergebnis: Silver Bullet auf EURUSD (Stand 2026-08-15)

EURUSD, 5m, 2015-01-01 bis 2019-12-31, 372.971 Kerzen. Startkapital 100.000 USD, 1 % Risiko je
Trade — identisch zur MNQ-Seite, damit die Serien vergleichbar sind. Kill-Switch aus (mit ihm
misst ein Mehrjahres-Lauf überwiegend ihn selbst, siehe unten).

| Fenster | Trades | Netto USD | Treffer % |
|---|---:|---:|---:|
| KZ London Close (10–12) | 185 | −30.802 | 18,4 |
| NY AM Silver Bullet (10–11) | 164 | −26.192 | 17,7 |
| **London Silver Bullet (3–4)** | **160** | **+3.651** | **21,2** |
| KZ London (2–5) | 123 | −27.272 | 10,6 |
| KZ NY-Forex (7–10) | 98 | −5.788 | 20,4 |
| KZ NY (7–9) | 95 | −6.802 | 20,0 |
| NY PM Silver Bullet (14–15) | 45 | −1.724 | 22,2 |
| KZ Asia (nachts, 0:00–0:30) | 1 | −133 | 0,0 |
| **Gesamt** | **871** | **−95.062** | **18,3** |

**Lesart, ehrlich:** Der Silver Bullet in der von MNQ übernommenen Parametrierung **funktioniert
auf EURUSD 5m nicht**. Bei einem Chance-Risiko-Verhältnis um 3:1 läge die Break-even-Trefferquote
bei rund 25 %; erreicht werden 18,3 %. Das Konto wäre von 100.000 auf 4.938 USD gefallen.

### Einklammerung: liegt es an den unbestimmten Fills?

Nein. Bei 28,6 % `dubious` liegt der Verdacht nahe, dass die konservative Auflösung das
Ergebnis macht. Gegengerechnet (unbestimmte Fills zugunsten des *Ziels* statt des Stops — nicht
die Handelsannahme, sondern die Gegengrenze):

| Auflösung unbestimmter Fills | Trades | Treffer % | Netto USD | London SB |
|---|---:|---:|---:|---:|
| konservativ (Stop gewinnt) | 871 | 18,3 | −95.062 | +3.651 |
| optimistisch (Ziel gewinnt) | 871 | 20,0 | −89.953 | +19.537 |

Die Spanne ist mit **−90k bis −95k** schmal. Die Fill-Ambiguität erklärt den Verlust nicht — sie
verschiebt ihn um 5 %. Das Ergebnis steht also unabhängig von dieser Annahme.

Beim London-Fenster ist der Hebel dagegen groß (+3.651 gegen +19.537): Genau dort, wo die
Stichprobe ohnehin zu klein für eine Aussage ist, hängt das Vorzeichen der *Größe* an einer
nicht messbaren Annahme. Ein weiterer Grund, es als Hypothese zu führen und nicht als Befund.

**Das eine positive Fenster ist noch kein Befund.** London Silver Bullet (+3.651 USD bei 160
Trades) ist der einzige Lichtblick, und er passt zur Erwartung, dass Forex-Volumen in London
liegt. Aber bei 21,2 % Trefferquote und dieser Stichprobe ist der Abstand zum Rauschen klein —
das ist eine Hypothese für den nächsten Lauf, kein Ergebnis. Erst Walk-Forward über die vollen
23 Jahre und die übrigen neun Paare entscheiden das.

### Drei Zahlen, ohne die die Tabelle irreführend wäre

- **`dubious_pct` = 28,6 %.** Bei über einem Viertel aller Trades liegt der Stop in der
  Entry-Kerze oder Stop und Ziel in derselben Kerze. Aus OHLC ist dort nicht rekonstruierbar,
  was zuerst geschah; aufgelöst wird zugunsten des Stops. Die Tabelle ist damit eine
  **Untergrenze**, keine Punktschätzung.
- **85 % aller Setups werden gar nicht gehandelt.** 5.895 von 6.964 Setups haben einen Stop
  unter 3 Pips — also enger als der Spread. Der MNQ-Parameter „10 % der FVG-Größe als Puffer"
  ergibt auf 5m-Forex Stops im Rauschbereich (Median 1,2 Pips, Minimum 0,2). Ohne diesen Filter
  misst der Backtest die Mikrostruktur des Datenfeeds, nicht die Regel.
- **Der Spread ist gesetzt, nicht gemessen.** Der Bestand ist reines Bid. Deshalb ist die
  belastbare Kennzahl der Break-even-Spread, nicht der $-Betrag.

## Macro-Fenster (:50–:10): größer ja, gerichteter nein (Stand 2026-08-15)

Zwei unabhängige Messungen über den vollen Bestand, beide mit Kontrollgruppe — was
`algo/macro_db.py` auf der MNQ-Seite fehlt, weil es Macro-Fenster nur untereinander vergleicht.

**1. Blockstudie** (`algo/forex/backtest_macro.py`, 10 Paare, 2000–2026, **3.983.412** 20-Minuten-Blöcke,
7.532 Handelstage). Jede Stunde zerfällt in drei Blöcke; die Kontrollen liegen direkt daneben:

| | Macro :50–:10 | Kontrolle | Mann-Whitney |
|---|---:|---:|---|
| median Range | 9,10 Pips | 8,60 Pips | p = 0,0000 |
| median Netto | 3,70 Pips | 3,40 Pips | p = 0,0000 |
| **dir (Geradlinigkeit)** | **0,448** | **0,455** | **p = 1,0000** |
| **Spooling-Quote** | **44,34 %** | **44,87 %** | **−0,52 pp** |

**2. Offset-Kontrollgruppe** (`algo/backtest_macro_forex.py`, sechs 20-Minuten-Fenster je Stunde,
~1,02 Mio. Macro-Fenster je Offset). Median-Delta der Expansionsquote über zehn Paare: **−0,03 pp**,
positiv bei 4 von 10, **trennbar bei 0 von 10** (95-%-Wilson-Intervalle überlappen durchweg).

### Der Größenvorteil gehört der vollen Stunde, nicht der :50

Die zwei Studien schienen sich zu widersprechen. Die Auflösung steht in der Offset-Tabelle:

| Offset | Fenster | med_range | Expansionsquote |
|---|---|---:|---:|
| **:50** | :50–:10 | **6,33** | 29,90 % |
| **:00** | :00–:20 | **6,30** | **30,72 %** |
| :10 | :10–:30 | 5,87 | 29,47 % |
| :20 | :20–:40 | 5,98 | 29,57 % |
| :30 | :30–:50 | 6,00 | 29,74 % |
| :40 | :40–:00 | 5,98 | 29,98 % |

Erhöht sind **genau die beiden Fenster, die den Stundenwechsel berühren** — :50–:10 enthält ihn,
:00–:20 beginnt an ihm. Die vier mittstündigen Offsets liegen geschlossen bei 5,87–6,00. Die
Blockstudie misst den Vorteil nur deshalb, weil ihre beiden Kontrollen (:10–:30, :30–:50) beide
mittstündig liegen; mit :00–:20 als drittem Vergleich verschwindet er. Nach Expansionsquote
schlägt :00 das Macro sogar.

### Was daraus folgt — und was nicht

**Widerlegt für Forex:** Die :50 ist als Uhrzeit nichts Besonderes. Was sich messen lässt, ist ein
Stundenwechsel-Effekt, den das Macro-Fenster zufällig mitnimmt, weil es über die volle Stunde
läuft.

**Und für Spooling:** Nach der Definition dieses Vaults ist Spooling der gerichtete Lauf, gemessen
über `dir` (siehe [[ICT Macros & Leading Candles]]). Genau dort zeigt sich **kein** Vorteil — die
Geradlinigkeit im Macro liegt mit p = 1,0000 nicht über der Kontrolle, die Spooling-Quote sogar
0,52 pp darunter. Auf 3,98 Millionen Blöcken ist das keine Frage der Stichprobengröße mehr.

**Nicht widerlegt ist die MNQ-Aussage.** Der Index-Futures-Bestand kann ein Eigenverhalten haben —
dort schließen Kontrakte, dort liegt eine Eröffnungsauktion, dort sind die Teilnehmer andere. Der
Forex-Befund heißt: *falls* ein interbank-weiter Algorithmus zur :50 den Preis ausdehnt, hinterlässt
er im FX-Spot über 24 Jahre keine Spur. ICTs eigene Begründung für Macros unterstellt aber genau
einen solchen marktübergreifenden Mechanismus — das ist der Punkt, an dem der Befund weh tut.

> ⚠️ **Vorbehalt zur Blockstudie:** Sie enthält die DST-verdächtigen Tage (siehe unten).
> Gegengerechnet ohne diese 97.448 Blöcke ändern sich alle Kennzahlen erst in der vierten
> Nachkommastelle (Spooling-Delta −0,525 → −0,506 pp). Die gepoolte Aussage hängt also nicht daran.
> Für die **stundenweise** Aufschlüsselung bleibt die Reparatur Vorbedingung.

## Offene Hypothesen (werden mit jedem Lauf aktualisiert)

- **London Silver Bullet trägt, die NY-Fenster nicht.** Einziges positives Fenster im ersten
  Lauf. Zu prüfen: hält das über 23 Jahre und über die anderen neun Paare?
- **NY-Killzone 7–9 oder 7–10?** `analyze_ohlc.KILLZONES` sagt 7–9, [[ICT Daily Range Session
  Timing]] sagt für Forex ausdrücklich 7–10. Beide laufen als getrennte Fenster mit. Erster
  Lauf: 7–10 verliert weniger (−5.788 gegen −6.802) bei mehr Trades — kein Unterschied, der
  etwas beweist.
- **Ist die Parametrierung schuld oder das Konzept?** Die 3-Pips-Untergrenze legt nahe, dass
  `stop_buffer_pct` für Forex neu bestimmt werden muss statt von MNQ übernommen zu werden. Eine
  Sensitivitätsanalyse steht aus.
- **Zwei Liquiditätsregime.** Bis 2011 haben 10–24 % der Minuten keinen Kursdruck, ab 2012 unter
  1 %. Ergebnisse aus beiden Zeiträumen sind nicht ohne Weiteres vergleichbar — künftige Läufe
  werden getrennt ausgewiesen.

## Strukturbefunde (unabhängig vom Ergebnis)

- **1h und gröber sind für fensterbasierte Setups unbrauchbar.** Ein Silver-Bullet-Fenster ist
  genau eine Stunde; auf 1h-Kerzen passt darin keine 3-Kerzen-FVG-Formation. Gemessen: 0 Trades.
  Praktische Untergrenze ist 15m (vier Kerzen je Fenster, also genau eine mögliche Formation).
- **Der Drawdown-Kill-Switch ist für Mehrjahresläufe untauglich.** Mit den MNQ-Defaults blockiert
  er 1.065 von 1.109 Setups — das ist sein eigenes dokumentiertes Verhalten (ohne offene Position
  bewegt sich die Equity nicht, also entsteht kein neues Hoch, also hebt er sich nie auf). Für
  die Frage „trägt die Regel?" gehört er aus, für „wäre das handelbar?" hinein.

## ⚠️ Datenvorbehalt: DST-Zeitversatz 2019–2026 (Stand 2026-08-15, Reparatur steht aus)

Der histdata-Bestand ist in den Wochen, in denen USA und EU zu **verschiedenen Terminen** auf
Sommerzeit umstellen, um eine Stunde zu früh gestempelt — **ab 2019**, davor korrekt. Der
Endpoint hat 2019 seine Umstellungstermine von der US- auf die EU-Regel gewechselt, ohne den
Offset zu ändern; in gewöhnlichen Wochen ist das unsichtbar, weil beide Regeln dort dasselbe
Ergebnis liefern.

Beleg ohne Fremdquelle: der 24x5-Markt schließt Freitag 17:00 NY, die letzte Freitagskerze muss
also auf 16:59 NY liegen. Über alle zehn Paare gemessen — Lücken-Woche 2007–2018: 16:59 ✓,
Lücken-Woche 2019–2026: **15:59**, gewöhnliche Woche: 16:59 ✓. Die Sonntagsöffnung zeigt
dasselbe Bild.

**Umfang:** 15 Fenster, 140 Handelstage je Paar, 1.962.205 von 81.676.600 Kerzen (2,40 %).

**Warum das hier steht und nicht nur im Protokoll:** die gesamte Regel-Schicht dieser Seite ist
**fensterbasiert** — Killzones, Silver-Bullet-Fenster, Midnight OR. Ein Stundenversatz schiebt
einen Trade nicht ein bisschen, sondern in die falsche Session. Solange die Reparatur
(`algo/repair_dst_2019.py --apply`, danach Cache-Neubau) nicht gelaufen ist, gelten alle Zahlen
dieser Seite für diese 2,40 % des Bestands als unbelastbar. Für den bisherigen EURUSD-Lauf
(2015–2019) sind es **20 der rund 1.250 Handelstage** — nur die beiden 2019er Fenster, weil die
Jahrgänge 2015–2018 noch der US-Regel folgen und damit korrekt sind. Der Lauf ist dadurch nicht
hinfällig; sobald die Auswertung aber ab 2019 reicht oder nach Fenstern aufgeschlüsselt wird,
ist die Reparatur Vorbedingung.

**Methodische Lehre, die über diesen Fall hinausgeht:** die ursprüngliche Zeitprüfung testete
zwei Sommertage und einen Wintertag. An solchen Tagen sind US- und EU-Sommerzeit gleichzeitig
aktiv — die beiden Regeln sind dort gar nicht unterscheidbar. Eine Zeitprüfung, die die
Umstellungswochen nicht ausdrücklich enthält, prüft den einzigen Fall nicht, in dem sie greifen
könnte. Vgl. [[Algo-Trading: Arbeitsstandards]] → „Zeit vor Preis".

## Verwandt

[[Silver Bullet Model]] · [[Fair Value Gap (FVG)]] · [[ICT Killzones]] ·
[[ICT Daily Range Session Timing]] · [[FVG-Stärke, Session-Volatilität & Confluence (laufend)]] ·
[[Muster-Validierung (laufend)]] · [[Risk-Management-Vergleich (laufend)]]
