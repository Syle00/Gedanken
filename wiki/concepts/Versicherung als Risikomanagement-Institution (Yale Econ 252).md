---
tags: [concept, quant-finance, risikomanagement, versicherung, yale-econ252]
created: 2026-08-12
updated: 2026-08-12
sources: ["[[2012-04-05 - Yale Econ 252 Lecture 05 - Insurance, the Archetypal Risk Management Institution (Source)]]", "[[2012-04-05 - Yale Econ 252 Lecture 14 - Guest Speaker Maurice Hank Greenberg (Source)]]"]
---

# Versicherung als Risikomanagement-Institution (Yale Econ 252)

Shillers Vorlesung über Versicherung als "archetypische Risikomanagement-Institution" plus
Hank Greenbergs (AIG-Gründer-Nachfolger) Insider-Bericht zum AIG-Kollaps 2008. **Risikomanagement-
Kernseite**: zeigt, wie Risikopooling in der Praxis versagt, wenn die Unabhängigkeitsannahme
bricht — dieselbe Schwachstelle wie bei [[Value at Risk, CoVaR & Unabhängigkeitsannahme]].

## Risikopooling — Grundprinzip und seine Voraussetzung

- Versicherung beruht auf dem **Gesetz der großen Zahlen**: bei `n` unabhängigen, identisch
  verteilten Risiken sinkt die Standardabweichung des Durchschnitts mit `1/√n` gegen 0. Historisch
  intuitiv erfasst (Aristoteles, Anonymus-Brief an Graf Oldenburg 1609 zur Feuerversicherung),
  formalisiert erst mit der Wahrscheinlichkeitstheorie ab ca. 1600.
- **Das Pooling funktioniert nur, wenn die Einzelrisiken tatsächlich unabhängig sind.** Das ist die
  zentrale, immer wiederkehrende Schwachstelle: Naturkatastrophen, Immobilienpreise, systemische
  Finanzrisiken sind gerade **nicht** unabhängig — sie korrelieren in Krisen stark positiv
  miteinander (Covariance-Explosion). Genau dieser Bruch der Unabhängigkeitsannahme war laut
  Shiller die strukturelle Ursache sowohl der Finanzkrise 2008 als auch des AIG-Kollapses.

## Vier Konstruktionsprobleme, die eine Versicherung "richtig" machen müssen

1. **Moral Hazard**: Versicherung verändert das Verhalten des Versicherten (z. B. Brandstiftung
   nach Feuerversicherung). Gegenmaßnahme: Versicherungssumme strikt unter dem tatsächlichen Wert
   halten (kein Brandstiftungs-Anreiz), bestimmte Todesursachen/Ereignisse ausschließen.
2. **Selection Bias (adverse Selektion)**: Wer weiß, dass er hohes Risiko trägt, versichert sich
   bevorzugt (Todkranke kaufen Lebensversicherung) — treibt Prämien hoch, verdrängt gesunde
   Käufer. Lösung u. a.: Versicherungspflicht für alle (z. B. US-Gesundheitsreform 2010: Pflicht +
   Strafsteuer bei Nichtversicherung, um den Pool zu durchmischen).
3. **Präzise Schadensdefinition**: z. B. Hurrikan Katrina — Wind- vs. Flutschaden waren separat
   versichert, was zu Rechtsstreitigkeiten führte, weil beide Ursachen gleichzeitig wirkten.
4. **Belastbare Statistikbasis**: erste Sterbetafeln erst im 17. Jh.; ohne verlässliche
   Wahrscheinlichkeiten keine korrekte Prämienkalkulation.

## AIG-Fallstudie: wie die Unabhängigkeitsannahme brach

- AIGs Risikomodell (unter Greenbergs Nachfolgern, nach dessen Abgang 2005) ging davon aus, dass
  Immobilienpreisrisiko **geografisch diversifizierbar** sei ("fällt in einer Stadt, nicht
  überall"). Als Immobilienpreise in den USA **flächendeckend gleichzeitig** fielen, brach genau
  diese Annahme zusammen.
- AIG Financial Products schrieb massiv **Credit Default Swaps (CDS)** auf CDOs. Ursprünglich
  lösten CDS erst bei tatsächlichem **Default** aus; die Vertragsbedingungen wurden verändert, so
  dass bereits ein **Wertverlust** (ohne Default) Nachschusspflichten (Collateral Calls) auslöste —
  das zwang AIG zu massiven Barmitteln, obwohl viele der zugrundeliegenden CDOs sich später
  wieder erholten. Greenbergs Fazit: CDS sollten nur bei echtem Default fällig werden, plus
  verpflichtende **Preisfindung über eine Börse** statt bilateraler Broker-Bewertung (Goldman
  Sachs setzte die niedrigsten Preise an und trieb damit die Collateral-Forderungen).
- Bailout-Bedingungen: $85 Mrd. Kredit der NY-Fed zu 14,5 % Zins gegen 79,9 % Eigenkapitalanteil
  (De-facto-Verstaatlichung), CDOs mussten zu 100 Cent auf den Dollar ausgezahlt werden (statt
  verhandelbaren 40–60 Cent) — Greenberg bewertet das als Fehlentscheidung, die AIG-Aktionäre
  (>90 % Wertverlust) unverhältnismäßig hart traf, während Gegenparteien wie Goldman Sachs voll
  ausgezahlt wurden.
- Bezug zu diesem Vault: AIG ist ein Lehrbuchbeispiel für [[Signal-Following & Crowd Liquidity
  Risk]] auf institutioneller Ebene — ein Modell, das "kann nicht überall gleichzeitig passieren"
  annimmt, versagt genau dann, wenn ein makro-systemischer Schock diese Annahme verletzt.

## Instrumente jenseits klassischer Versicherung

- **Terrorism Risk Insurance Act (TRIA, 2002)**: Terror-/Kriegsrisiko galt lange als
  unversicherbar (korrelierte Schäden), Lösung war eine Teil-Staatshaftung im Katastrophenfall.
- **Catastrophe Bonds ("Cat Bonds")**: Bsp. Mexiko 2006, $160 Mio., nur rückzahlbar, falls **kein**
  Erdbeben eintritt — verlagert konzentriertes Länderrisiko in ein globales, diversifiziertes
  Anlegerportfolio. Strukturell ein Options-/Versicherungshybrid.
- **Einlagensicherung für Versicherer**: US-State-Guarantee-Funds (seit 1941, NY zuerst), Limit
  meist $300–500k pro Police — schützt Kleinanleger, aber kein Schutz bei Mega-Versicherern wie
  AIG (deshalb der Sonderbailout statt regulärer Konkursabwicklung).

## Bezug zu diesem Projekt

- Die AIG-Lehre ("Pooling funktioniert nur bei echter Unabhängigkeit") ist eine
  Risikomanagement-Warnung auch für Multi-Symbol-/Multi-Strategie-Portfolios: mehrere MNQ-Setups,
  die alle auf denselben Makro-Trigger (z. B. FOMC, gleiche Session) reagieren, sind **nicht**
  unabhängig, auch wenn sie in einem Backtest wie separate "Wetten" aussehen — Diversifikations-
  gewinn ist dann eine Illusion. Direkt anschlussfähig an
  [[Kelly-Criterion & Value-at-Risk (Money Management)]] und die Portfolio-Formeln in
  [[Portfolio-Management & Sizing (Gain-Loss-Ratio)]].
- Die CDS-Collateral-Mechanik (Wertverlust statt Default löst Nachschuss aus) ist strukturell mit
  Margin Calls bei Futures-Positionen verwandt — eine konkrete Erinnerung, dass unrealisierte
  Buchverluste bei gehebelten Positionen echte Liquiditätsereignisse auslösen können, nicht nur
  ein "Papierverlust" sind.
