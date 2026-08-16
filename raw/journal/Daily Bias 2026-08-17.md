# Daily Bias 2026-08-17

*(Montag, erzeugt am 15.08.2026 durch `/bias-vorlage-daily`)*

> Weekly Bias: [[Weekly Bias KW34 2026]]

## News (Red/Orange Folder)

Quelle: **TradingView-Wirtschaftskalender** (`news.source: tradingview`) — ForexFactory kennt
den 17.08. am Samstag noch nicht (Feed deckt nur 09.–14.08. ab). Uhrzeiten beider Quellen sind
gegengeprüft und deckungsgleich; TradingView stuft nur mehr Events als Red ein. Nur US-Termine.

| NY | DE | Währung | Event | Impact | Forecast | Previous |
|---|---|---|---|---|---|---|
| 08:30 | 14:30 | USD | NY Empire State Manufacturing Index | Orange | 10.2 | 15.6 |
| 10:00 | 16:00 | USD | NAHB Housing Market Index | Orange | 33 | 34 |
| 16:00 | 22:00 | USD | Net Long-term TIC Flows | Orange | – | 232.7 |

**Kein Red-Folder-Termin.** Der Tag ist newsarm — kein Termin, der die Range vorgibt. Das
Empire-State-Release um 08:30 NY liegt vor dem Open, der Rest ist nachrangig. Der Wochentermin
ist FOMC Minutes am Mittwoch (siehe [[Weekly Bias KW34 2026]]).

## Levels

⚠️ **Live-Daten nicht verfügbar** — `algo/live_status.py` meldet am Samstag `market_data: false`
(„keine 5m-Daten, Markt geschlossen"). NDOG, NWOG und ORG-C.E. brauchen den Montag-Open und
lassen sich erst ab Sonntag 18:00 NY bestimmen:

| Level | Open | Close |
|---|---|---|
| NWOG | _(offen bis So 18:00 NY)_ | 30154.75 |
| NDOG | _(offen bis So 18:00 NY)_ | 30154.75 |

Beide Gaps messen gegen denselben Freitag-Schluss, weil auf den Freitag direkt der
Sonntagabend-Open folgt.

**Vortages-Range (Fr 14.08.):**

| | Wert |
|---|---|
| Open | 30213.0 |
| High | 30287.25 |
| Low | 30025.0 |
| Close (letzter 1m-Print 16:59 NY) | 30154.75 |
| Range | 262,25 Punkte |

> ⚠️ **Korrigierte Werte.** `MNQ 2026-08-14 1d.csv` ist ein zu früh gezogener Snapshot und
> meldet High 30232.5 / Low 30124.25 (108,25 Punkte) — die 1m-Daten desselben Tages zeigen
> 262,25 Punkte, also **154 Punkte mehr**. Die Tabelle nutzt die 1m-Werte. Betroffen ist nur
> dieser eine Tag im gesamten Bestand.

**Weekly Range (KW34):** noch keine — Montag ist der erste Handelstag der Woche.
Referenz ist die KW33-Range 29533.5 – 30287.25 (753,75 Punkte), siehe
[[Weekly Bias KW34 2026]].

## Wiki-Bezug

- [[Weekly Range Trading Model]] — Montag als Wochenstart: setzt er das Wochen-High/-Low?
- [[New Day Opening Gap (NDOG)]] — montags relevant, weil NDOG und NWOG zusammenfallen
- [[Midnight Opening Range]] — Referenzpunkt für den Tagesverlauf
- [[ICT Daily Range Session Timing]] — Session-Struktur des Tages
- [[ORG (Opening Range Gap) & 1st Presented FVG]] — nach dem 9:30-Open, sobald ein Gap steht

## Einschätzung (Claude)

**Statistik.** Montag ist im MNQ-Bestand der stärkste Wochentag: **61,4 % bullish** bei n=376
Beobachtungen, avg. Return +0,194 %, Median-Range 263,88 Punkte
(`algo/seasonal_tendency.json`). Das ist die deutlichste Wochentagsabweichung in der Tabelle —
alle anderen Tage liegen zwischen 50,5 % und 55,3 %, also nahe am Münzwurf. Die Freitag-Range
von 262,25 Punkten liegt fast exakt auf diesem Montag-Median, also keine auffällige
Vorspannung in eine Richtung.

**Newsarmer Tag.** Ohne Red-Folder-Termin fehlt der Katalysator, der eine Range aufzieht.
Ein solcher Tag löst sich eher über Struktur und Liquidität als über eine Datenreaktion —
das nächstliegende Ziel nach oben ist das Freitag-/Wochen-High bei **30287.25** (~130 Punkte
über dem letzten Print), nach unten das Freitag-Low bei **30025.0**.

**NWOG-Vorbehalt.** Sobald das NWOG Sonntagabend steht: `algo/backtest_nwog.py` misst eine
Bias-intakt-Quote von nur **7 %** — als Richtungsfilter untauglich, als Level (DOL-Kandidat)
brauchbar. Entsprechend nicht die Montagsrichtung daran aufhängen.

**ORG-C.E.** Lässt sich erst nach dem 9:30-Open berechnen. Die ORG-C.E.-70-%-These bleibt
**laufend beobachtet** (eigener Backtest bislang 35–43 %, `algo/backtest_org_ce.py`) — sie
wird hier bewusst nicht als widerlegt behandelt, sondern bei jedem Lauf mitgeführt.

**Fazit:** Statistisch leichte Aufwärtsneigung (Montag, 61,4 %), aber ohne News-Katalysator
und ohne die Sonntagabend-Level ist das eine schwache Aussage. Der Tag ist eher über die
Reaktion auf das NWOG/NDOG zu lesen als über eine Vorab-Richtung.

## Mein Bias

### Targets und relevante PD Arrays (Mo 17.08.)

- **Target: PDH 30.283,00** — möglich.
- **Relevantes PD Array: SIBI vom 23.06.**
- **Höchster Buyside Pool, der für Montag und Dienstag gerade erkennbar ist: 30.599,75 (30.06.)**

Übernommen aus [[Weekly Bias KW34 2026]] — Montag ist bereits Teil dieser Woche, die
Wochenstruktur (Retracement ins BISI, Sellside 29.780,50 als DOL) gilt unverändert.

---

*Gegenprüfung (Claude, 16.08.2026):*

- **PDH 30.283,00 bestätigt** — High vom Fr 14.08., 09:05 NY, aus den NQ-Intraday-Daten.
  Der Freitag schloss bei 30.154,00, das Ziel liegt also **129 Punkte** über dem letzten Print.
  Tagesrange Freitag: H 30.283,00 / L 30.028,50 / C 30.154,00.
- **30.599,75 (30.06.) exakt bestätigt** als Tages-High. Liegt **445 Punkte** über dem
  Freitagsschluss — als Montagsziel weit, als Wochenziel erreichbar.
- Einordnung zur Erwartung „wenig Bewegung": Die Median-Tagesrange an newsarmen Tagen liegt bei
  **266,9 Punkten** (n=42, gemessen über 753 NQ-Handelstage). Vom Freitagsschluss aus reicht das
  rechnerisch für den PDH (129 Punkte), **nicht** für 30.599,75. Montag ist zudem mit
  61,4 % bullish (n=376) der stärkste Wochentag — beides zusammen stützt eher „PDH als
  Tagesziel, Buyside-Pool als Wochenziel".
- ⚠️ Der PDH stammt aus den Intraday-Daten. Die **1d-Reihe im Bestand enthält den 14.08. nicht**
  (letzter Eintrag 13.08., High 30.272,75) — wer den PDH von dort zieht, bekommt den falschen
  Tag und 10,25 Punkte zu wenig. `bias_levels.py::yesterday_range()` wurde am 16.08. auf die
  Intraday-Quelle umgestellt.

