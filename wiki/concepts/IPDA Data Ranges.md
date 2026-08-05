---
tags: [concept, ict, trading-ict, core]
created: 2026-08-01
updated: 2026-08-02
sources: ["[[Blending IPDA Data Ranges & PD Arrays (Source)]]", "[[Using IPDA Data Ranges (Source)]]", "[[Advanced ICT Liquidity Concepts (Source)]]"]
---

# IPDA Data Ranges

Interbank Price Delivery Algorithm — die Lookback-Fenster (20/40/60 Tage), in denen nach relevanten
[[PD Array|PD Arrays]] (Highs/Lows, Order Blocks) gesucht wird.

## Kernregel

- Standard-Suchfenster ist **20 Tage**. Wird das markierte Low der 20-Tage-Range durchbrochen, ohne
  dass sich im 40-Tage-Abschnitt ein neues Lower Low gebildet hat, wird das Suchfenster auf
  **60 Tage** erweitert.
- Dient dazu, das jeweils relevante High/Low für die aktuelle Marktphase zu bestimmen, nicht beliebig
  weit zurückzuschauen.

![[image 184.png]]
*20-Tage-Low wird durchbrochen, ohne Lower Low im 40-Tage-Abschnitt → Erweiterung des Lookback auf
60 Tage.*

## IPDA — was der Algorithmus sucht

**IPDA = Interbank Price Delivery Algorithmus.** Sucht nach Buy-/Sellside-Liquidität: Wo liegt das
Equilibrium (siehe [[Equilibrium Vs. Discount]])? Gibt es darüber/darunter ein FVG bzw. BISI/SIBI
(Buyside-/Sellside-Imbalance, siehe [[Fair Value Gap (FVG)]])? Genau dorthin bewegt sich der Preis.
Der Algo schaut **60 Tage zurück**, um die Targets/Orders der großen Funds zu finden.

## Rückwirkende Gültigkeit von PD Arrays

Das 20/40/60-Fenster begrenzt nicht nur die Suche nach dem relevanten High/Low, sondern die
**Verwendbarkeit der [[PD Array|PD Arrays]] insgesamt**:

> Wie lange nutzen wir rückwirkend die PDs wie Imbalances, Wicks und Gaps? Wir nehmen die IPDA Data
> Ranges 20/40/60 Days — **PDs sind bis zu 60 Tage rückwirkend nutzbar.**

## Quarterly Shift als Ankerpunkt

- Alle 3–4 Monate (siehe [[Quarterly Shift]]) erfolgt ein Major Shift in der Marketstructure. Von
  diesem Shift-Zeitpunkt aus arbeitet man sich mit dem 20/40/60-Tage-Lookback/Forward-Fenster vor
  und zurück.
- Auch wenn ein Shift bereits erfolgt oder verpasst wurde, liefert die Analyse genug Information,
  um den bestehenden Bias (z.B. weiterhin bearish nach einem bearishen Shift) beizubehalten, bis ein
  neuer Shift eindeutig bestätigt ist.

## Open Interest als Shift-Bestätigung

- Major Market Shifts gehen mit einem **OI-Abfall** einher. Open Interest = alle offenen Long- und
  Short-Positionen im Markt.
- Zentralbanken stellen Währungen quasi als "Commodity/Ressource" bereit — sie treten selbst als
  Liquidität auf.
- **Regel**: Fällt/steigt das OI um **15 % oder mehr**, tritt die Zentralbank als Liquiditätsquelle
  auf. Ein starker OI-Abfall in wenigen Tagen bedeutet: kein großes Interesse mehr, viele
  Short-Positionen offen zu halten — die großen Funds nehmen Gewinne mit und kaufen ihre Shorts
  zurück (analog spiegelbildlich für Longs).

![[image 80.png]]
*OI-Abfall von 15% oder mehr: Zentralbank tritt als Liquiditätsquelle auf, Big Funds nehmen
Gewinne mit.*

## Kürzeres Lookback für Intraday-Scalping (2026-Ergänzung)

Für reines Daytrading/Intraday-Scalping genügt laut ICT ein **3-Tage-Lookback** statt der
20/40/60-Tage-HTF-Fenster — "das gesamte Universum an Liquidität und Ineffizienzen der letzten 3
Tage" reicht aus. Erst wenn die Range der letzten 3 Tage durchbrochen wird, muss weiter
zurückgeschaut werden. Praktische Anwendung: [[Daily High & Low Projektion (Konvergenz)]].

## Verwandt

- [[PD Array]], [[Fair Value Gap (FVG)]]
- [[Quarterly Shift]]
- [[Open Float & Liquidity Pools]]
- [[Daily High & Low Projektion (Konvergenz)]]
