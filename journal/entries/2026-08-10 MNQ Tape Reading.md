---
tags:
  - Tapereading
  - NY-PM
Bias:
  - Bullish
Date: 2026-08-10
NQ/ES: MNQ
id: 2026-08-10-03
typ: tape-reading
modus: live
kw: 2026-W33
wochentag: Montag
modell: "Silver Bullet"
liquidity_ziel: "Sellside: Lunch Sellside Liquidity 29.730,25 und NY AM Sellside Liquidity 29.719,00 — beide nicht angegangen, Abstand zu gering"
checks_erfuellt: 4
pd_arrays: [Silver Bullet Model, ICT Macros & Leading Candles, Chain of Custody (Q-Validation), Open Float & Liquidity Pools, New Week Opening Gap (NWOG) Bias, Fair Value Gap (FVG)]
---

# 2026-08-10 MNQ Tape Reading

## Kurzfassung

| | |
|---|---|
| Zeit (NY) | — |
| Session / Macro | — / — |
| Modell | Silver Bullet |
| Bias / Richtung | Bullish / — |
| Resultat | — · — · — · — |
| Liquidity-Ziel | Sellside: Lunch Sellside Liquidity 29.730,25 und NY AM Sellside Liquidity 29.719,00 — beide nicht angegangen, Abstand zu gering |

## Setup-Checkliste

- [x] Liq Sweep 13:55

![[2026-08-10-pm-03.png]]

*13:55 — „Sweep Minor Buysdie" — die Minor Buyside oberhalb ~29.769 wird geholt.*

- [ ] Displacement

- [x] Anhaltende Consolidation 13:57

![[2026-08-10-pm-05.png]]

*13:57 — Qs/Os auf der Wick 29.753,00-29.763,25, C.E. 29.758,25. „Diese WIck schaue ich an nicht hoeher als C.E closen soll drunter bleiben".*

- [x] Richtige Zeitfenster

- [ ] MS Break

- [ ] Entry

- [ ] Macro Expansion

- [x] Target Liquidität min. 2 H/L 1m

**4/8 erfüllt**

### MNQ

**Pre trade**

**Ende**

![[2026-08-10-pm-09.png]]

*14:07 — „Ich bekomme zu wenig Punkte gerade mal 30 ab hier das lohnt sich nicht fuer mich zu viel risiko fuer zu wenig profit" — die Absage, mit Begruendung.*

---

**Entry**

**Target**

![[2026-08-10-pm-08.png]]

*14:06 — Zwei getrennte Sellside-Ziele beschriftet: Lunch Sellside Liquidity 29.730,25 und NY AM Sellside Liquidity 29.719,00.*

**5min**

**Besonderheiten**

![[2026-08-10-pm-01.png]]

*12:10 — MNQU2026 1min mit gelb markiertem Macro 10:50-11:10 — der Chart, auf dem die Spooling-Notiz vom Vormittag beruht. Gut sichtbar: das Fenster selbst liefert den Abverkauf von ~29.870 auf ~29.780, die Kompression liegt danach bei 11:10-11:30.*

**Reaktion**

![[2026-08-10-pm-06.png]]

*13:58 — Close 29.761,25 ueber dem C.E. „ok close drueber das will ich nicht sehen abwarten! aufs FVG oder eindeutige Anzeichen fuer Baerish Priceaction".*

**Macro Start**

![[2026-08-10-pm-02.png]]

*13:50 — „Silverbullet Macro start 13.50" und „Sellside ist mein Fokus". Sellside Liquidity bei 29.719,00 eingezeichnet, NDOG 05.08 bei 29.819,50 / 29.781,25, NWOG 33 bei 29.841,00 / 29.851,50.*

**Macro Ende**

![[2026-08-10-pm-07.png]]

*14:03 — „abwarten!" — das Macro 13:50-14:10 laeuft aus, ohne Displacement zu liefern.*

## Timeline (NY)

- **13:50** — Chart-Notiz: „Silverbullet Macro start 13.50". Preis 29.748,50. Fokus notiert: „Sellside ist mein Fokus", Ziel Sellside Liquidity 29.719,00. 15m zeigt den ganzen Tag Abwaertsstruktur von ~29.860 herunter.
- **13:55** — Chart-Notiz: „Sweep Minor Buysdie" — Minor Buyside oberhalb ~29.769 geholt. Das ist der Sweep, auf dem das Short-Szenario aufbaut.
- **13:57** — Qs/Os auf die Wick 29.753,00 (0) bis 29.763,25 (1) gelegt, C.E. = 29.758,25. Chart-Notiz: „Diese WIck schaue ich an nicht hoeher als C.E closen soll drunter bleiben" — Bedingung vorab definiert.
- **13:58** — Close 29.761,25, also ueber dem C.E. Chart-Notiz: „ok close drueber das will ich nicht sehen abwarten! aufs FVG oder eindeutige Anzeichen fuer Baerish Priceaction". Bedingung verletzt -> kein Entry, statt sie umzudeuten.
- **14:03** — Chart-Notiz: „abwarten!". Preis 29.756,25, weiter Hin und Her ohne Displacement.
- **14:06** — Sellside sauber getrennt und beschriftet: Lunch Sellside Liquidity 29.730,25, NY AM Sellside Liquidity 29.719,00 — zwei 1m-Ziele statt eines pauschalen „nach unten".
- **14:07** — Entscheidung: kein Trade. Chart-Notiz: „Ich bekomme zu wenig Punkte gerade mal 30 ab hier das lohnt sich nicht fuer mich zu viel risiko fuer zu wenig profit".

## Fehleranalyse

Keine Regelverstöße erkennbar — Ausführung sauber, unabhängig vom Ergebnis.

## Was gut lief

- Kein Trade bei 4 von 8 Checks. Seine eigene Mindestschwelle liegt bei 6 (config.yaml: min_checks) — die Absage deckt sich mit der Regel, ohne dass er sie ausrechnen musste.
- C.E.-Bedingung um 13:57 vorab definiert und beim Bruch um 13:58 nicht umgedeutet, sondern abgewartet. Genau das ist der Punkt, an dem sonst nachtraeglich die Begruendung angepasst wird.
- RR selbst gerechnet statt das Setup schoenzureden: ~30 Punkte bis zum Ziel als zu wenig fuer das noetige Risiko eingestuft.
- Sellside in zwei benannte 1m-Ziele getrennt (Lunch 29.730,25 / NY AM 29.719,00) statt pauschal „nach unten" — das macht die RR-Rechnung ueberhaupt erst moeglich.

## Datenlücken

*Nicht bewertbar, weil die Information fehlt — beim nächsten Mal mitloggen.*

- Emotionslabels fehlen — aus „abwarten!" und der Absage laesst sich Ruhe vermuten, aber nicht belegen. Beim naechsten Mal ein Wort dazu.
- Kein Screenshot nach 14:07 — ob die Sellside 29.730,25 / 29.719,00 spaeter doch noch genommen wurde, ist aus dem Material nicht belegbar.
- Tagesbias (Bullish) noch nicht nachgehalten, Tag beim Erfassen nicht geschlossen. Auffaellig: im PM lag der Fokus auf Sellside, also gegen den eigenen Tagesbias — beim Rueckblick pruefen, ob das eine bewusste Anpassung an die Priceaction war oder ein stiller Bias-Wechsel.

## Hinweise

- Kein Trade genommen — die offenen Punkte (Displacement, MS Break, Entry, Macro Expansion) sind hier der Grund für das Aussteigen, kein Fehler. Genau so ist die Checkliste gemeint.
- Kein Trade genommen — Eintrag zählt als Beobachtung, nicht in Trefferquote oder R-Statistik.

## Verwandt

[[Silver Bullet Model]], [[ICT Macros & Leading Candles]], [[Chain of Custody (Q-Validation)]], [[Open Float & Liquidity Pools]], [[New Week Opening Gap (NWOG) Bias]], [[Fair Value Gap (FVG)]]
