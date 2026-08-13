---
tags: [concept, ict, trading-ict, pd-array]
created: 2026-08-13
updated: 2026-08-13
sources: ["[[2026-08-13 MNQ Daily Bias]]"]
---

# New Day Opening Gap (NDOG)

Das tägliche Pendant zum [[New Week Opening Gap (NWOG) Bias|NWOG]]: das Kursgap zwischen dem
gestrigen Session-Close und der heutigen Session-Open. Wie das NWOG ein PD Array, nur auf
Daily- statt Weekly-Ebene.

## Gültigkeitsdauer

- **NDOG**: bleibt mindestens **5 Handelstage** aktiv.
- **NWOG**: bleibt mindestens **5 Handelswochen** aktiv.

Beide sind laut Nutzerbeobachtung (2026-08-13) auch **über diese Mindestdauer hinaus** noch
nutzbar — sie verfallen nicht, sondern bleiben als [[Draw on Liquidity (DOL)|DOL]] einsetzbar,
solange sie nicht durchhandelt wurden. Universeller Einsatz als
[[AMD Cycle (Accumulation – Manipulation – Distribution)|DOL]], nicht nur als kurzfristiges
Bias-Signal.

> ⚠️ Bislang nur als Nutzeraussage festgehalten, noch nicht gegen `raw/marktdaten/` gebacktestet
> — siehe [[Algo-Trading: Arbeitsstandards]] ("jede neue These wird automatisch geloggt und
> gebacktestet"). Backtest-Kandidat: Trefferquote/Reaktionsrate an NDOG/NWOG-Levels in
> Abhängigkeit vom Alter (< 5 Perioden vs. älter).

## Praxisbezug

In `algo/live_status.py` und wiederkehrend in [[ICT Macros & Leading Candles]] tauchen
NDOG-Level als konkrete Preiszonen auf (z.B. NDOG-05.08-Level 29.819,50 im Beispiel vom
2026-08-10). Wird in Journal-Einträgen regelmäßig als PD Array neben dem NWOG geführt, siehe
[[2026-08-11 MNQ Daily Bias]], [[2026-08-13 MNQ Daily Bias]].

## Verwandt

[[New Week Opening Gap (NWOG) Bias]], [[PD Array]], [[Chain of Custody (Q-Validation)]],
[[IPDA Data Ranges]]
