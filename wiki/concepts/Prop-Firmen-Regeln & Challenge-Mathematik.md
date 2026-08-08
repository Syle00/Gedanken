---
tags: [concept, algo-methodology, risikomanagement, prop-trading, referenz]
created: 2026-08-08
updated: 2026-08-08
sources: []
---

# Prop-Firmen-Regeln & Challenge-Mathematik

Regelwerk und mathematische Besonderheiten von Prop-Firmen-Challenges. Relevant, weil der Algo
laut Zielbild-Spec vom 2026-08-08 auch Challenges handeln können soll — deren Regeln sind **harte
Nebenbedingungen**, kein Optimierungsziel.

> ⚠️ **Alle Zahlen hier sind Größenordnungen aus Marktübersichten, keine verbindlichen Werte.**
> Prop-Firmen ändern ihre Regeln häufig und unterscheiden sich erheblich. Vor jeder Challenge sind
> die Bedingungen der tatsächlich gewählten Firma zu lesen.

## Die Regelfamilien

| Regel | Typische Ausprägung |
|---|---|
| Tagesverlustgrenze | 4–5 % des Kontos; manche Futures-Firmen ohne |
| Maximaler Drawdown | 8–12 % |
| Gewinnziel | ~8–10 % zum Bestehen |
| Mindesthandelstage | oft 5–10 |
| Konsistenzregel | bester Tag höchstens ~30 % des Gesamtgewinns |
| Verbotene Techniken | HFT, Latenzarbitrage, Tick-Scalping, Martingale, Copy-Trading |

## Statisch, trailing, intraday oder end-of-day

Der wichtigste Unterschied, und der am häufigsten unterschätzte:

- **Statischer Drawdown** — der Verlustboden liegt fest beim Startguthaben und bewegt sich nie.
- **Trailing Drawdown** — der Boden wandert mit jedem neuen Kontohoch nach oben mit. Er
  **sinkt nie wieder**. Beispiel: 5 % auf 100.000 → Boden bei 95.000. Steigt das Konto auf
  105.000, wandert der Boden auf 100.000. Fällt es danach auf 99.999, ist das Konto verloren —
  obwohl noch Gewinn gegenüber dem Start besteht.

Und innerhalb von „trailing" die entscheidende Verzweigung:

| Art | Was den Boden hebt |
|---|---|
| **Intraday-Trailing** | Jedes Zwischenhoch der Equity, auch **unrealisiert** |
| **End-of-Day-Trailing** | Nur das **Schlussguthaben** des Tages |

Bei Intraday-Trailing verkleinert eine offene Position, die zwischenzeitlich 3.000 im Plus steht und
auf 1.500 zurückfällt, den Puffer bereits um 3.000 — obwohl nie etwas gebucht wurde.

## Der Konflikt mit dem ICT-Skalierungsmodell

**Direkte Folge für dieses Vault:** Das Modell aus
[[Partial Profit-Taking & R-Multiple-Skalierung]] — erste Hälfte bei 3:1 sichern, zweite Hälfte bis
9R–15R laufen lassen — ist unter **Intraday-Trailing gefährlich**. Genau das Laufenlassen
verbrennt dort dauerhaft Puffer, sobald der Runner zwischendurch zurückkommt.

Unter End-of-Day-Trailing oder statischem Drawdown besteht der Konflikt nicht.

Konsequenz im Algo: Bei Intraday-Trailing wird die Runner-Komponente abgeschaltet und an festen
Zielen realisiert.

## Warum eine Challenge ein anderes Problem ist

Das übrige Risikomodell des Projekts optimiert **langfristiges Wachstum**
([[Kelly-Formel & optimales Leverage (Chan)]], [[CPPI (Constant Proportion Portfolio Insurance)]]).

Eine Challenge fragt etwas anderes: *Wie erreiche ich +8 % bevor ich −10 % erreiche?* Das ist ein
**Erstüberschreitungs-Problem**, kein Wachstumsproblem — und es hat ein anderes Optimum.

Aus der klassischen Spieltheorie (Dubins & Savage, *How to Gamble If You Must*, 1965): **Bold
Play** — so groß setzen wie möglich — maximiert die Wahrscheinlichkeit, ein Ziel vor dem Ruin zu
erreichen, **nur im unfairen Spiel** (Gewinnwahrscheinlichkeit ≤ ½). Bei einem echten Vorteil gilt
das Gegenteil: **kleine Einsätze** maximieren die Bestehenswahrscheinlichkeit, weil die Zeit für
einen arbeitet.

Daraus folgt eine unbequeme Selbstprüfung:

> **Wenn große Positionen die Bestehenschance erhöhen, hat die Strategie keinen Vorteil.**

Wer in einer Challenge groß setzen muss, um sie zu bestehen, spielt — und scheitert spätestens auf
dem finanzierten Konto. Deckt sich mit Masters' Befund, dass Trefferquote allein nichts über den
Erwartungswert aussagt ([[Vier-Stufen-Strategieentwicklung (Masters)]]).

**Einschränkung:** Bei einem **Zeitlimit** existiert eine Untergrenze für die Positionsgröße,
unterhalb derer das Gewinnziel nicht rechtzeitig erreichbar ist. Diese Untergrenze wird gerechnet,
nicht geschätzt. Manche Firmen haben Zeitlimits abgeschafft — das ist je Firma zu prüfen.

## Die Konsistenzregel ist eine Obergrenze nach oben

Leicht zu übersehen: Manche Firmen lassen durchfallen, wenn ein einzelner Tag einen zu großen
Anteil am Gesamtgewinn ausmacht. Der Algo muss auf einem sehr guten Tag also **aufhören zu
gewinnen** — eine Bedingung, die in keinem gewöhnlichen Risikomodell vorkommt.

## Was aus dem bestehenden Projektstand bereits passt

| Bereits entschieden | Prop-Anforderung |
|---|---|
| Intraday flat, abends geschlossen | Viele Futures-Firmen verlangen genau das |
| Red-Folder-News gesperrt | Manche Firmen verlangen es, keine verbietet es |
| Kein Nachlegen in Verluste | Martingale ist verbreitet untersagt |
| Stop als echte Order beim Broker | Erfüllt jede Risikokontroll-Anforderung |
| CPPI mit Hochwasserstand | Bildet trailing Drawdown strukturell bereits ab |
| Keine Latenz-Strategien | HFT und Latenzarbitrage sind verbreitet untersagt |

Der Algo ist damit weitgehend prop-tauglich, ohne dass er dafür entworfen wurde. Was fehlt: das
Kontoprofil, die Konsistenzprüfung und die Runner-Abschaltung bei Intraday-Trailing.

## Vor dem Kauf einer Challenge zu klären

1. **Erlaubt die Firma automatisierten Handel auf ihrer vorgeschriebenen Plattform?** Manche
   schreiben eine eigene Plattform ohne externe Anbindung vor — das wäre ein Ausschlusskriterium.
2. Welche Drawdown-Art gilt, und wird auf Guthaben oder auf Equity gemessen?
3. Gibt es eine Konsistenzregel, und wie ist sie definiert?
4. Gibt es ein Zeitlimit?
5. Läuft die Firma über IBKR oder verlangt sie einen eigenen Broker?

## Verwandt

- [[CPPI (Constant Proportion Portfolio Insurance)]] — bildet trailing Drawdown strukturell ab
- [[Kelly-Formel & optimales Leverage (Chan)]] — das Wachstumsziel, gegen das die Challenge steht
- [[Partial Profit-Taking & R-Multiple-Skalierung]] — betroffen vom Intraday-Trailing-Konflikt
- [[Risikomanagement (1% pro Trade)]] — bleibt gültig, wird durch Profilgrenzen zusätzlich gedeckelt
- [[Erwartungswert & Reward-to-Risk-Modell]]
