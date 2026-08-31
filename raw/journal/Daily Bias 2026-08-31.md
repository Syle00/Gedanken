# Daily Bias 2026-08-31

> Weekly Bias: [[Weekly Bias KW36 2026]]
> Montag, KW 36

## News (Red/Orange Folder)

⚠️ News-Abruf fehlgeschlagen (`URLError: <urlopen error Tunnel connection failed: 403 Forbidden>`),
manuell auf forexfactory.com prüfen. Sowohl ForexFactory (`nfs.faireconomy.media`) als auch der
TradingView-Fallback (`economic-calendar.tradingview.com`) wurden vom Netzwerk-Proxy dieser
Cloud-Session mit HTTP 403 abgewiesen (Egress-Policy-Ablehnung, kein transienter Fehler — bestätigt
über `$HTTPS_PROXY/__agentproxy/status`, beide Hosts stehen dort unter `recentRelayFailures`).
Beide Hosts sind für diese Session nicht freigegeben.

Bereits verifizierte Mo-31.08.-Termine stehen in [[Weekly Bias KW36 2026]] (Quelle `tradingview`,
dort am 28.08.2026 ohne Fehler abgerufen):

❌ keine USD-Termine

Zur Sicherheit trotzdem gegen forexfactory.com/tradingview gegenprüfen — dieselbe Wochendatei
vermerkt einen offenen Vorbehalt zum NFP-Termin (Fr 04.09., nicht diesen Montag betreffend), als
Beleg dafür, dass der Kalender an dieser Feed-Grenze lückenhaft sein kann.

## Levels

**Datenlage:** 20 Handelstage mit 1s-Daten (2026-07-27 – 2026-08-21), kein Tag nur auf 1m, keine
in `1s-abdeckung.csv` registrierten Tage ohne Datei. Abgleich 1s gegen TradingView-1m:
max. Abweichung 2,50 Punkte (2026-08-20), sonst ≤ 2,00 Punkte — unauffällig. Symbol: NQ.

⚠️ **Lücke, weiterhin aktiv (dritter Bias-Bericht in Folge mit demselben Befund — 27.08., 28.08.,
dieser):** Die 1s-Daten enden nach wie vor am 21.08. (Fr, KW34). Für die komplette KW35
(Mo 24.08. – Fr 28.08.) liegen weiterhin keine Marktdaten vor — weder in `raw/marktdaten/` noch
als frischer Commit (letzter marktdatenrelevanter Commit weiterhin 2026-08-26, ein reiner
Setup-Commit ohne neue OHLC-Dateien). Die neue KW36 startet dadurch ohne Anschluss: Weekly Range
für KW36 ist zu diesem Zeitpunkt zwar ohnehin `null` (die Woche beginnt erst heute, das allein
wäre normal), aber selbst der `yesterday_range`-Fallback scheitert für alle Werktage zwischen
24.08. und 28.08. an fehlenden Intraday-Daten und fällt auf die 1d-Reihe zurück, die ihrerseits
seit 13.08. nicht aktualisiert wurde. Live-Preis und ORG-C.E. fehlen zusätzlich, weil
`live_status.py` in dieser Session kein IBKR-Gateway erreicht (siehe unten). Der Nachlad-Job
(1s-Anbindung) sollte geprüft werden — die Lücke schließt sich nicht von selbst.

| Level | Datum | Close (17:00) | Open (18:00) | Gap | C.E. | Status |
|---|---|---|---|---|---|---|
| NWOG | 2026-08-02 | 28287,00 | 28565,00 | +278,00 | 28426,00 | **offen** |
| NDOG | 2026-08-20 | 29317,25 | 29327,00 | +9,75 | 29322,00 | gefüllt |
| NDOG | 2026-08-19 | 29561,00 | 29561,50 | +0,50 | 29561,25 | gefüllt |
| NDOG | 2026-08-18 | 29559,50 | 29566,50 | +7,00 | 29563,00 | gefüllt |
| NDOG | 2026-08-17 | 30078,25 | 30077,00 | −1,25 | 30077,50 | gefüllt |
| NWOG | 2026-08-16 | 30154,00 | 30170,00 | +16,00 | 30162,00 | gefüllt |
| NDOG | 2026-08-13 | 30214,25 | 30210,75 | −3,50 | 30212,50 | gefüllt |
| NDOG | 2026-08-12 | 29805,75 | 29825,00 | +19,25 | 29815,50 | gefüllt |
| NDOG | 2026-08-11 | 29646,75 | 29657,75 | +11,00 | 29652,25 | gefüllt |
| NDOG | 2026-08-10 | 29764,25 | 29764,50 | +0,25 | 29764,50 | gefüllt |

**Letzter verfügbarer Daily-Bar** (2026-08-13, Quelle 1d — nicht „gestern", siehe Lücke oben):
H 30272,75 / L 29780,50 / C 30188,50

_Weekly Range KW36: keine Daten — Zeile ausgelassen (Woche beginnt erst heute, zusätzlich von der
Lücke oben betroffen)._

### Offenes Gap — NWOG 2026-08-02 (Qs/Os/Hs)

Spanne 278,00 Punkte, Close 28287,00 (2026-07-31 16:59:59) → Open 28565,00 (2026-08-02 18:00:00).

| | Level |
|---|---|
| High (Open) | 28565,00 |
| O7 | 28530,25 |
| O6 / Q3 | 28495,50 |
| O5 | 28460,75 |
| **C.E. (= H1 = Q2 = O4)** | **28426,00** |
| O3 | 28391,25 |
| O2 / Q1 | 28356,50 |
| O1 | 28321,75 |
| Low (Close) | 28287,00 |

## Wiki-Bezug

- [[Weekly Range Trading Model]] — übergeordneter Rahmen für den Wochenstart
- [[ICT Daily Range Session Timing]]
- [[Midnight Opening Range]]
- [[ORG (Opening Range Gap) & 1st Presented FVG]]
- [[New Day Opening Gap (NDOG)]]
- [[New Week Opening Gap (NWOG) Bias]] — Wochenauftakt, dazu das nach wie vor offene
  278-Punkte-Gap vom 2026-08-02
- [[Average Daily Range (5-Tage-ADR)]]
- [[Using Monthly & Weekly Ranges (Source)]] — Mo 31.08. ist zugleich der letzte Handelstag im
  August; das Turn-of-Month-Fenster beginnt mit diesem Tag

## Einschaetzung (Claude)

**Wochentag-Statistik (MNQ, n=376 Montage, 2019-05-06 – 2026-08-14, Quelle
`algo/seasonal_tendency.json`):** bullish 61,4 %, Ø-Return +0,194 %, Median-Range 263,88 Punkte,
Ø-Range 311,22 Punkte. Montag ist damit der **stärkste Einzelwochentag der gesamten Serie** —
sowohl die höchste Bullish-Quote als auch der höchste durchschnittliche Return aller fünf
Wochentage. Das ist der robusteste saisonale Fingerzeig, der in einem Daily-Bias-Bericht
vorkommen kann, aber weiterhin nur eine Tendenz (61,4 % ≠ Gewissheit), keine Vorhersage für
diesen einzelnen Tag.

**Week-of-Month gegenläufig, schwächer:** Der 31.08. fällt kalendarisch noch in „Woche 5" von
August (n=152, bullish 46,1 %, Ø-Return +0,099 %, Median-Range 251,12 Punkte) — das ist die
schwächste der fünf Week-of-Month-Klassen und liegt unter der 50-%-Marke. Turn-of-Month-Fenster
(heute beginnt es): 53,6 % bullish (n=349, Ø +0,078 %) gegen 54,3 % im Rest (n=1533, Ø +0,071 %)
— praktisch kein Unterschied, wie schon in [[Weekly Bias KW36 2026]] festgehalten. Netto: der
starke Montags-Effekt trifft auf einen leicht gegenläufigen, aber deutlich schwächeren
Week-of-Month-Effekt — in der Summe eher ein moderater Bullish-Tilt als eine klare Kante.

**News:** Kein einziger USD-Termin mit Red-/Orange-Impact laut der bereits verifizierten
KW36-Datei (heutiger Abruf technisch blockiert, siehe oben) — kein `backtest_fred_events.py`-Pfad
nötig. Praktische Konsequenz: der gesamte Handelstag ist strukturell frei von Makro-Katalysatoren,
anders als der kommende Freitag (möglicher NFP-Termin, siehe Weekly-Bias-Vorbehalt). Bewegung
sollte heute also aus Struktur/PD Arrays kommen, nicht aus News.

**Offenes NWOG 2026-08-02 (28287,00–28565,00, C.E. 28426,00):** weiterhin das einzige offene Gap
im gesamten Fenster. Laut [[Weekly Bias KW36 2026]] lag es zum letzten bekannten Preis
(Fr 21.08. Close 29374,00) rund 948 Punkte im Discount — für einen einzelnen Handelstag kein
Intraday-Ziel, sondern ein Wochen-/Monatsziel. `algo/backtest_nwog.py` misst eine
Bias-intakt-Quote von nur 9,6 % (36/375 Wochen) für ein NWOG, das intraweek nicht wieder erreicht
wird — das Level ist also eher ein Referenzpunkt als ein Richtungsfilter.

**ORG-C.E.:** Für diesen Lauf liegen keine Live-Marktdaten vor (siehe Lücke oben), also kein
ORG-Level. Die ORG-C.E.-70%-These bleibt als *laufend beobachtete* Hypothese offen — eigene
Messungen liegen bislang bei 35–43 % und damit deutlich unter der Lehrmeinung; laut
Nutzerentscheid nicht als widerlegt abgehakt, sondern weiter erhoben.

**Fazit:** Datenqualität für diesen Bericht weiterhin eingeschränkt (kein aktueller Preis, keine
Weekly Range, News nur aus einer drei Tage alten Quelle nachgetragen) — die zugrunde liegende
Marktdaten-Lücke besteht jetzt seit drei aufeinanderfolgenden Bias-Berichten unverändert und
sollte auf Nachlad-Ebene geprüft werden. Der saisonale Fingerzeig ist heute ungewöhnlich klar für
einen Wochentag allein (stärkster Montags-Effekt der Serie), wird aber durch den schwächeren
Week-of-Month-Effekt etwas gedämpft — moderater Bullish-Tilt, kein News-Risiko, NWOG-C.E.
28426,00 bleibt das übergeordnete, aber weit entfernte Downside-Level.

## Mein Bias

<!-- Jannes -->
