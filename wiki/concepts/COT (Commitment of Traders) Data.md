---
tags: [concept, ict, trading-ict]
created: 2026-08-01
updated: 2026-08-23
sources: ["[[One Shot One Kill Model (Source)]]"]
---

# COT (Commitment of Traders) Data

Positionierungsdaten großer Marktteilnehmer (Commercials), genutzt zur Bias-Bestätigung im Verbund
mit [[Seasonal Tendency]] und [[SMT (Smart Money Divergence)|SMT]].

## COT Hedging Program (12-Monats-Methode)

- High und Low der letzten **12 Monate** nehmen, das EQ (Equilibrium) bestimmen.
- Liegt der aktuelle COT-Wert **über** der 12M-0-Linie → bullish; **darunter** → bearish.

> ⚠️ **Präzisierung (2026-08-03, aus der Praxis).** Die zwei Punkte oben sind unscharf: Punkt 1
> nennt das **EQ der 12-Monats-Range**, Punkt 2 die **0-Linie**. Das sind zwei verschiedene Linien,
> und bei Index-Futures liegen sie weit auseinander — Commercials sind dort strukturell netto short,
> das 12M-EQ liegt also tief im Negativen. Maßgeblich ist das **EQ der 12-Monats-Range**, nicht die
> Null.
>
> Beleg: Jannes' `COT 12 monate`-Indikator auf NQ (Aug 2025 – Aug 2026) zeichnet genau diese
> Trennlinie bei rund **−27 K** — dem EQ aus 12M-High ≈ +15 K und 12M-Low ≈ −68 K. Der aktuelle
> Wert **−14,95 K** liegt darüber, also im grünen Bereich, und der Indikator gibt für die
> 12-Monats-Sicht **BUY** aus — obwohl der Wert deutlich **unter null** liegt. Nach der wörtlichen
> Lesart von Punkt 2 wäre dieselbe Lage „bearish". Wer die 0-Linie nimmt, liest bei Indizes fast
> immer bearish und damit fast immer dasselbe.
>
> Der Indikator liefert zugleich mehrere Horizonte gleichzeitig (3M / 6M / 12M / 2Y / 4Y). Die
> stimmen regelmäßig **nicht** überein — am 03.08.2026 stand NQ auf 3M SELL, 6M SELL, **12M BUY**,
> 2Y BUY, 4Y SELL. Ein COT-Urteil ohne Angabe des Horizonts ist damit nicht überprüfbar; notiere
> immer, welcher Lookback gemeint ist.
- Beispiel: EU macht ein Higher High, während Commercials stark Short gehen, kombiniert mit
  bearisher [[Seasonal Tendency]] → starkes Bias-Signal für Shorts trotz des Higher High.

![[image 219.png]]
*COT Hedging Program: High/Low der letzten 12 Monate und die 0-Linie als Bullish-/
Bearish-Trennlinie.*

![[image 220.png]]
*Bearish-Einschätzung, da der aktuelle COT-Wert unter der 12-Monats-0-Linie liegt.*

## Automatisiert seit 2026-08-16: `algo/cot.py`

Die Auswertung läuft jetzt im Weekly Bias mit (`/bias-vorlage-weekly`, Abschnitt „COT"), Quelle
ist der CFTC-Legacy-Report über das Paket [`cot_reports`](https://github.com/NDelventhal/cot_reports).

**Marktreihe zählt.** Die CFTC führt NQ dreifach, mit deutlich verschiedenen Zahlen. Maßgeblich
ist **`NASDAQ MINI`** — das ist die Reihe, die Jannes' Indikator abbildet:

| CFTC-Reihe | Commercials net (Report 2026-07-28) |
|---|---|
| **NASDAQ MINI** | **−14.946** ← entspricht dem oben belegten Indikatorwert −14,95 K |
| NASDAQ-100 Consolidated | −8.044 |
| MICRO E-MINI NASDAQ-100 | +69.021 |

Für ES gilt analog `E-MINI S&P 500`. Wer die falsche Reihe nimmt, rechnet still an der
Chart-Quelle vorbei.

**Validierung der EQ-Lesart.** Für den oben dokumentierten Stand (03.08.2026, Report 2026-07-28)
reproduziert `algo/cot.py` alle fünf Horizonte des Indikators exakt: 3M SELL, 6M SELL,
**12M BUY**, 2Y BUY, 4Y SELL — bei einem 12M-EQ von −26.471 (Seite oben: „rund −27 K") und einer
12M-Range von −66.754 bis +13.812 (Seite oben: „−68 K … +15 K"). Damit ist die Präzisierung
„EQ statt 0-Linie" nicht nur begründet, sondern nachgerechnet. Der Fall ist als Regressionscheck
in `cot.py::demo()` festgehalten.

Ausgewertet werden nach ICT-Lesart **nur Commercials gegen Large Speculators** (Non-Commercials);
Small Specs bleiben außen vor. `gegenlaeufig` markiert den interessanten Zustand, in dem beide
Gruppen auf verschiedenen Seiten stehen.

## ⚠️ Bestand vs. Veränderung — `gegenlaeufig` misst nur den Bestand

Aufgefallen bei der Bias-Erstellung für KW35 (2026-08-23), Report-Stand 2026-08-18.

`gegenlaeufig` vergleicht die **Vorzeichen der Netto-Positionen**. Stehen Commercials und Large
Specs beide netto short, meldet das Feld `false` — auch dann, wenn beide Gruppen in der
Berichtswoche **gegenläufig gehandelt** haben. Genau dieser Fall lag am 18.08. vor:

| NQ (NASDAQ MINI) | 2026-08-11 | 2026-08-18 | Veränderung |
|---|---|---|---|
| Commercials | +17.475 | −12.347 | **−29.822** |
| Large Specs | −39.302 | −10.416 | **+28.886** |

Die beiden Gruppen bewegen sich fast spiegelbildlich — das ist die Konstellation, auf die ICT
abstellt. Der Bestand sagt `gegenlaeufig: false`, der **Fluss** sagt das Gegenteil. −29.822 ist
zugleich die größte bearishe Wochenbewegung der Commercials in der 2026er-NQ-Reihe (zweitgrößte
Bewegung überhaupt nach +30.388 am 04.08.).

**Und der Fluss kann zwischen NQ und ES auseinanderlaufen, obwohl der Bestand dasselbe sagt:**

| ES (E-MINI S&P 500) | 2026-08-11 | 2026-08-18 | Veränderung |
|---|---|---|---|
| Commercials | −142.440 | −113.553 | **+28.887** |
| Large Specs | +11.280 | −10.560 | −21.840 |

ES-Commercials haben ihren Short in derselben Woche um gut 20 % **abgebaut** — und zwar von
**−142.440, exakt dem Low der 3M-/6M-Range**, also vom Extrem weg. Im Bestand liest ES über alle
fünf Horizonte bearish, im Fluss war es die Gegenrichtung zu NQ.

**Praktische Folge:** Bestand und Fluss sind zwei verschiedene Aussagen und dürfen nicht
vermischt werden. Die auf dieser Seite belegte und nachgerechnete EQ-Lesart betrifft
ausschließlich den **Bestand**. Eine Aussage wie „die Commercials bauen schnell Shorts auf, also
fällt der Preis" stützt sich dagegen auf den **Fluss** — der ist bislang **nicht gebacktestet**.
`algo/backtest_cot_divergenz.py` prüft die *Bestands*-Divergenz zwischen NQ und ES, nicht die
Fluss-Divergenz.

> **Offen, Kandidat für einen eigenen Lauf:** Sagt die Wochenveränderung der Commercials
> (allein oder gegen die der Large Specs) etwas über die Folgewoche? Gleiche Zeitachse wie in
> `backtest_cot_divergenz.py` beachten — Report-Stand Dienstag, Veröffentlichung Freitag, handelbar
> ab Montag der Folgewoche, sonst Lookahead.

**Kein Wirkmechanismus.** Der COT-Report ist ein Positionierungs-Snapshot vom Dienstag, der
freitags nach Börsenschluss erscheint. Er **drückt** den Preis nicht — Formulierungen wie „der COT
drückt Price runter" beschreiben eine Korrelationsthese, keinen Kausalzusammenhang, und schon gar
keine intraweek wirkende Kraft.

## Verwandt

- [[One Shot One Kill Model]]
- [[Seasonal Tendency]]
- [[SMT (Smart Money Divergence)]]
