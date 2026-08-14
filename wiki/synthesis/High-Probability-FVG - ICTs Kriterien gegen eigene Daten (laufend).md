---
tags: [synthesis, ict, fvg, backtest, laufend, high-probability]
created: 2026-08-14
updated: 2026-08-14
sources: ["[[2025-01-19 - ICT Private Mentorship - High Probability FVGs Masterclass (Source)|High Probability FVG's (Masterclass)]]", "[[2024-09-16 - ICT 2024 Mentorship - How To Trade ICT FVGs Correctly (Source)|How To Trade ICT FVGs Correctly]]", "[[Fair Value Gap (FVG)]]"]
---

# High-Probability-FVG - ICTs Kriterien gegen eigene Daten (laufend)

ICT nennt in zwei Lectures konkrete, prüfbare Kriterien für ein „High Probability FVG". Diese
Seite hält fest, was davon in **MNQ-1m-Daten** messbar übrig bleibt. Sie wird bei wachsendem
Datenbestand überschrieben, nicht ergänzt.

**Stand: 7.375 FVGs / 7.107 simulierte Trades aus `raw/marktdaten/`, Skript
`algo/backtest_hp_fvg.py`.**

## Testaufbau

ICTs eigene Ausführungsregeln, nicht selbst erfundene: Limit-Entry **einen Tick vor der nahen
Gap-Kante** (Kerze 3), Stop **hinter Kerze 2**, 1 Kontrakt, echter Punktwert (2 $/Punkt MNQ),
−1,24 $ Round Turn. Zwei Zielvarianten:

- **20 Punkte fest** — ICTs eigene Untergrenze für den Bewegungsraum.
- **2R** — nötig für den fairen Vergleich zwischen Killzones (siehe Confound unten).

Stop und Ziel in derselben 1m-Kerze zählen konservativ als Verlust (`dubious`).

> ⚠️ **Der Bias ist ein Proxy.** ICT setzt den Draw on Liquidity von Hand. Automatisiert wird
> hier die Premium/Discount-Lage des **Midnight Open** zur Vortages-Equilibrium genommen (unter
> EQ → bearish, darüber → bullish). Lookahead-frei, aber *nicht* ICTs Bias. Die Zeile „nur
> Bias-Proxy" steht deshalb einzeln in der Tabelle.

## Ergebnis bei 2R (die vergleichbare Variante)

| Gruppe | n | Trades | Win % | $/Trade netto | dubious % |
|---|---|---|---|---|---|
| alle FVG | 7.375 | 7.107 | 36,3 | +0,49 | 4,2 |
| nur Killzone | 4.128 | 4.050 | 36,2 | +0,58 | 4,4 |
| nur Vortageshälfte | 3.855 | 3.717 | 37,2 | +1,13 | 4,3 |
| **nur Bias-Proxy** | 3.822 | 3.667 | **37,7** | **+1,79** | 4,2 |
| Zone + Killzone | 2.121 | 2.073 | 36,3 | +0,85 | 4,6 |
| **HP (alle drei)** | 1.921 | 1.875 | 36,6 | **+1,51** | 4,6 |
| HP + sofortiges Rebalance | 927 | 927 | 34,0 | **−0,66** | 2,5 |

Breakeven bei 2R liegt bei 33,3 %.

### Was hält

**Die Kombination hilft, aber wenig.** ICTs drei Kriterien verdreifachen den Erwartungswert je
Trade (0,49 → 1,51 $), heben die Trefferquote aber kaum (36,3 → 36,6 %). Der Effekt kommt aus
besseren Gewinnern, nicht aus mehr Gewinnern.

**Die Vortageshälfte ist das stärkste der drei ICT-Kriterien** (37,2 %, +1,13 $) — das ist die
Regel „bearishes FVG gehört unter das Equilibrium der Vortagesrange". Sie hält als eigenständiger
Filter.

### Was nicht hält

**Die Killzone allein bringt nichts** (36,2 % gegen 36,3 % ohne Filter, +0,58 gegen +0,49 $).
Als Zeitfilter über alle FVGs hinweg ist sie in MNQ nicht messbar.

**Das sofortige Rebalance ist negativ.** ICT: *„if the next candle number four drops in and it
starts running, chances are stronger that this lower half will stay open."* Gemessen dreht es
+1,51 $ in **−0,66 $** je Trade. Ein FVG, das sofort wieder angelaufen wird, ist in diesen Daten
**schlechter** als eines, das erst später berührt wird.

**Die 98-%-Behauptung ist nicht reproduzierbar.** ICT nennt in der Masterclass *„a 98 % strike
rate"*. Gemessen: 36–38 % bei 2R, 42 % bei 20-Punkte-Ziel. Auch bei wohlwollendster Auslegung
(nur HP-FVGs, nur Killzone, strittige Fälle als Gewinner) bleibt der Abstand zu 98 % um ein
Vielfaches zu groß.

### Das Signal, das keines ist

| Ausgangssignal | n | Win % | $/Trade |
|---|---|---|---|
| ferne Hälfte blieb offen | 111 | **99,1** | +72,15 |
| ferne Hälfte verletzt | 6.996 | 35,3 | −0,65 |

> ⚠️ **Nahezu tautologisch, nicht prognostisch.** „Die ferne Hälfte blieb offen" heißt, dass Preis
> nie über den C.E. hinaus ins Gap lief. Der Stop liegt hinter Kerze 2, also **jenseits der fernen
> Kante** — wer die ferne Hälfte nie erreicht, kann den Stop gar nicht treffen. Die 99,1 % sind
> deshalb eine *Beschreibung* eines gewonnenen Trades, keine Vorhersage. Der Wert der Regel liegt
> im **Trade-Management** (Prämisse hält / Prämisse bröckelt), nicht in der Selektion.
>
> Ehrlich bleibt: der Fall ist mit **111 von 7.107 Trades (1,6 %)** selten. ICTs „perfect world"
> ist der Ausnahme-, nicht der Normalfall.

## Confound: das feste Punktziel verzerrt den Killzone-Vergleich

Mit ICTs 20-Punkte-Ziel sah London Close (10:00–12:00 NY) nach einer riesigen Kante aus —
**63,9 % Win, +11,83 $/Trade** gegen London 36,8 % / +0,47 $. Die Ursache steht in der
Risikospalte: **Median-Stopabstand 20,25 Punkte** in London Close gegen 10,0–11,5 Punkte in allen
anderen Fenstern. Bei festem 20-Punkte-Ziel handelt London Close faktisch **1R**, alle anderen
**2R** — höhere Trefferquote bei kleinerem Vielfachen ist dann kein Befund, sondern Arithmetik.

Auf 2R normiert schrumpft der Vorsprung auf 38,2 % / +4,26 $:

| Killzone | Win % (2R) | $/Trade | Median-Risiko |
|---|---|---|---|
| Asia (19:00–00:30) | 36,0 | +0,09 | 10,75 |
| London (02:00–05:00) | 34,4 | **−1,07** | 10,00 |
| NY (07:00–09:00) | 37,9 | +0,92 | 11,25 |
| **London Close (10:00–12:00)** | **38,2** | **+4,26** | 20,25 |

London Close bleibt das beste Fenster, London das einzige mit negativem Erwartungswert. Beides
mit dem Vorbehalt unten.

**Methodische Lehre für künftige Backtests**: ein festes Punktziel über verschieden volatile
Zeitfenster hinweg ist kein neutraler Maßstab — es verschiebt das effektive RR entlang genau der
Achse, die verglichen werden soll.

## Vorbehalte

- FVGs innerhalb eines Tages sind stark korreliert; die Konfidenz ist deutlich niedriger, als
  n = 7.107 suggeriert. Wenige Marktregime im Datensatz.
- Der Bias-Proxy ist die schwächste Stelle. Dass ausgerechnet er der beste Einzelfilter ist,
  spricht eher für die Kraft von Premium/Discount als für die Güte des Proxys — mit ICTs echtem,
  handgesetztem Draw on Liquidity könnten alle Zahlen anders aussehen.
- ICTs Regeln stammen aus **Forex-** (Masterclass, AUD/USD 2019) und **NQ-Kontext**; hier laufen
  sie gegen MNQ. Die Killzone-Fenster sind auf Forex-Sessions zugeschnitten.
- Slippage ist nicht modelliert (Limit-Entry am Gap-Rand), Teilpositionen/Pyramiding auch nicht —
  ICTs Skalierungsschema (6/4/2 Kontrakte über Entry/Quadrant/C.E.) würde die Zahlen verändern.

## Umsetzung im Code

- `tools/analyze_ohlc.py::fvgs()` liefert pro FVG zusätzlich `entry`, `stop_c2`, `stop_c1`,
  `q25`/`q75`, `near_touches`, `far_touches`, `far_half_open`, `fast`.
- `tools/analyze_ohlc.py::hp_context()` prüft Vortageshälfte, Killzone und Bias.
- `algo/backtest_hp_fvg.py` misst; Regressionstests in `tools/test_fvg_vii.py`, eingebunden in
  `algo/selfcheck.py`.

## Verwandt

- [[Fair Value Gap (FVG)]] — Definition, Grenzen, Entry/Stop/Quadranten
- [[FVG-Stärke, Session-Volatilität & Confluence (laufend)]] — die ältere Auswertung zu Größe und Swing-Break
- [[ORG (Opening Range Gap) & 1st Presented FVG]], [[ICT Killzones]]
- [[Muster-Validierung (laufend)]]
