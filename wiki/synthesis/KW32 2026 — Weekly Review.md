---
tags: [synthesis, trading-ict, marktdaten, mnq, review]
created: 2026-08-07
updated: 2026-08-07
sources: ["[[../journal/entries/2026-08-03 MNQ Weekly Bias]]", "[[../journal/entries/2026-08-03 MNQ Daily Bias]]", "[[../journal/entries/2026-08-06 MNQ Daily Bias]]", "[[../journal/entries/2026-08-07 MNQ Daily Bias]]"]
---

# KW32 2026 — Weekly Review

Wochenübergreifende Zusammenfassung der bereits einzeln verifizierten Einträge in
`journal/entries/` (verwaltet vom `trading-journal`-Skill) für KW32 2026 (03.–07.08., MNQ).
Auf Nutzeranfrage erstellt ("gebe mir eine Einschätzung zu meinem Bias dieser Woche"). Diese
Seite fügt nichts an Datenprüfung hinzu, was die einzelnen Einträge nicht schon geleistet haben —
sie zieht nur den roten Faden über die Woche, den es bisher nicht gab (`journal/index.md` →
Berichte war für diese Woche noch leer).

## Weekly Bias — bestätigt

Gesetzt Montag 01:55 NY ([[../journal/entries/2026-08-03 MNQ Weekly Bias]]): **Bullish**,
DOL = Buyside Liquidity **29.363,50** (Daily Chart).

→ **Bestätigt, deutlich überschossen.** Wochenhoch KW32: **30.073,25** (Mi. 05.08., 09:45 NY) —
über 700 Punkte über dem DOL. Wochentief: **28.313,00** (Mo. 03.08., 09:30 NY, RTH-Open).
Wochenrange 1.760,25 Punkte. Handelstag-Close Freitag (Stand 07.08., 06:20 NY, Tag lief noch)
29.603,75 — deutlich über dem Wochen-Open 28.567,50.

## Daily Bias, Tag für Tag (aus den einzelnen Einträgen)

| Tag | Bias | Ergebnis | Fehler laut Journal |
|---|---|---|---|
| **Mo 03.08** | Bullish; Szenario: Drop ins NWOG (28.284–28.567,50), dann [[Judas Swing]]-Sweep sellside, danach weiter bullish. DOL 28.725,75–28.763,75 (Freitags-High + Montags-High 27.07) | **bias_korrekt: true.** Close 28.929,25 (+361,75 ggü. Open). DOL um 201 Pkt überschossen (High 28.965,00, 14:10 NY, exakt im geplanten SB-Fenster). Der Sweep blieb aber *innerhalb* des NWOG (Low 28.313,00, nie unter 28.284,00) — die Judas-Sequenz traf im Detail nicht zu, kostete aber nichts | Widerspruch zum eigenen Weekly Bias 33 Min. vorher ("Montag gute PA" vs. "im Daily schwierig") — laut Journal der teuerste Fehler des Tages, weil er die Erwartungshaltung senkt. Kein Invalidierungslevel für den Judas zunächst gesetzt (S08, nachträglich ergänzt) |
| **Di 04.08** | (kein separater Daily-Bias-Eintrag im Journal, nur Trade-Log "0958 Silver Bullet") | Handelstag-Close 29.044,00 — bullish, aber noch unter dem Wochen-DOL | — |
| **Mi 05.08** | (kein Daily-Bias-Eintrag, nur ein Tape-Reading-Eintrag) | Handelstag-Open 29.781,25 → Close 29.904,00, Tageshoch 30.073,25 (09:45 NY) = **Wochenhoch**, NWOG KW29 High (29.956,75) dabei um 28 Punkte überboten | — |
| **Do 06.08** | Bullish, aber bewusst **kein Trade** (Unemployment heute, NFP morgen). Bullish-Struktur an C.E. Daily-IFVG (16.07, ≈29.308,38) und C.E. Daily-BISI (04.08, ≈29.370,25) festgemacht; DOL zunächst fälschlich "High 26.07 30.094,00" benannt | **fehler: [] — laut Journal fehlerfrei.** Handelstag-Close 29.504,50, klar über beiden C.E.-Levels; Sweep der Di-NY-AM-Liquidität kam (Low 29.241,00), Reaktion zurück war vorhanden, wenn auch der Tag unter der Eröffnung schloss. Datumsfehler beim DOL selbst noch am selben Tag korrigiert: echtes Level ist ein **REH-Cluster 30.062,50–30.094,00** (06./10./15.07), nicht ein Doppel-Top 26.07 | Datumsverwechslung beim DOL (26.07 statt korrekt 06.07/10.07/15.07) — inhaltlich harmlos, weil das Level selbst korrekt war und die Zone durch die Korrektur sogar stärker belegt wurde |
| **Fr 07.08** | **Kein Bias** — explizit wegen NFP, nur Beobachtung | Bias-Richtung damit nicht bewertbar (gewollt). Alle geprüften Einzelaussagen (Close über beiden C.E., NWOG-KW29-Treffer, ORG 06.08 gefüllt, ORG 04.08 offen, TGIF-Zielzone 29.545–29.721 bereits erreicht) bestätigt | **Ein klarer Faktenfehler:** *"ORG vom Donnerstag 30.06 ist offen"* — falsch. Das ORG (30.020,00→30.047,00) wurde bereits am 01.07. gefüllt, ist seit über 5 Wochen zu. Die eigene Sorge ("nicht bis dahin durchlaufen, sonst MSB") bezog sich auf ein Level ohne offenes Ziel |

## Fehleranalyse — was diese Woche wirklich falsch lief

Anders als eine erste grobe Durchsicht der rohen Notizen (`raw/journal/`) nahelegt, ist die Woche
in `journal/entries/` bereits präzise gegen Marktdaten geprüft. Die tatsächlichen, belegten Fehler
sind kleiner als "Bias falsch" — es sind Präzisions- und Konsistenzfehler:

1. **Montag: Bias-Inkonsistenz innerhalb von 33 Minuten.** Weekly Bias (01:55) sagt "Montag sollte
   gute Price Action liefern" (korrekt, da NFP-Woche laut [[ICT Day Trade Routine]]), Daily Bias
   (02:28) sagt "im Daily ist Montag schwierig" (die Grundregel ohne die NFP-Ausnahme). Beides ist
   für sich wiki-gedeckt, der Wechsel *zwischen* den beiden ist die eigentliche Inkonsistenz — und
   laut Journal der Fehler mit dem größten potenziellen Preis, weil eine gesenkte Erwartungshaltung
   dazu führt, ein Setup kleiner zu handeln oder ganz zu verpassen.
2. **Wiederkehrendes Muster: Invalidierungslevel fehlen im Erstentwurf.** Sowohl der Weekly Bias
   (Close < 28.284,00) als auch der Montags-Judas (Sweep 28.284,00→28.210,25 mit Reclaim) hatten
   im Originaltext keine Zahl — beide wurden erst nachträglich vom Journal-System ergänzt. Kein
   Fehler, der etwas gekostet hat (kein Level wurde gerissen), aber eine Lücke, die sich durch die
   Woche zieht.
3. **Freitag: ein stehengelassener, veralteter Referenzpunkt.** Die Sorge um das "offene ORG vom
   30.06." beruhte auf einem Level, das seit fünf Wochen gefüllt ist. Einziger echter Faktenfehler
   der Woche, der über eine reine Formulierungs-Ungenauigkeit hinausgeht — allerdings folgenlos,
   weil ohnehin kein Trade geplant war (NFP-Freitag).
4. **Kleinigkeiten:** KW-Nummer im Weekly Bias falsch (KW31 statt KW32), NWOG-Open als 28.567,60
   statt 28.567,50 notiert (MNQ tickt nur in 0,25-Schritten) — beides folgenlose Tippfehler.

## Was gut lief

- Weekly Bias und der einzige vollständig geprüfte Daily Bias (Montag) waren beide **bias_korrekt:
  true**, mit prozentual sauber überschossenen Zielen (DOL +201 Pkt am Montag, Weekly-DOL +710 Pkt
  zur Wochenmitte).
- No-Trading-Regel um NFP konsequent angewendet: Donnerstag (Vortag von NFP) und Freitag (NFP
  selbst) bewusst ohne Trade, trotz weiterhin bullisher Neigung — genau die eigene Regel aus
  [[ICT Day Trade Routine]] befolgt statt umgangen.
- Konkrete, benannte Invalidierungslevel ab Donnerstag (C.E. Daily-BISI 29.370,25) statt reiner
  Richtungs-Vibes — eine direkte Verbesserung gegenüber dem Montag, wo dieses Level fehlte.

## Verwandt

- [[../journal/entries/2026-08-03 MNQ Weekly Bias]], [[../journal/entries/2026-08-03 MNQ Daily Bias]], [[../journal/entries/2026-08-06 MNQ Daily Bias]], [[../journal/entries/2026-08-07 MNQ Daily Bias]] — die geprüften Originaleinträge, jeweils mit vollständiger Fehleranalyse
- [[Weekly Range Trading Model]], [[TGIF (Thank God its Friday)]], [[Judas Swing]], [[New Week Opening Gap (NWOG) Bias]]
- [[Journal-Auswertung]] — aggregierte Checklisten-Erfüllungsquote über den alten Notion-Export (`raw/journal/`), nicht deckungsgleich mit dem neuen `journal/entries/`-System
