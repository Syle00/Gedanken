# Wiki-Log (laufend)

> Der chronologische Verlauf steht seit 2026-08-16 in der Git-Historie (`git log`).
> Hier stehen nur noch Dinge, die kein Commit ausdrückt: offene Fragen, bewusste Abweichungen
> von den Konventionen und Widerspruchsmarker. Ältere Einträge:
> [[log-archiv-bis-2026-08]].

## Hinweis zu Widerspruchsmarkern

Fast jeder ⚠️/✅-Marker, der früher hier chronologisch protokolliert wurde, lebt bereits
**dauerhaft direkt auf der betroffenen Wiki-Seite** (Seitenkonvention, siehe `CLAUDE.md`) — z.B.
der Widerspruch zur London Opening Range auf [[ORG (Opening Range Gap) & 1st Presented FVG]] und
[[Midnight Opening Range]], oder die widerlegte "98 % Strike Rate" auf [[Fair Value Gap (FVG)]].
Beim Kürzen dieser Datei (2026-08-16) wurde eine **Stichprobe** der Fundstellen aus
`log-archiv-bis-2026-08.md` gegen den aktuellen Wiki-Bestand geprüft (25 von 26 in einem
späteren Review lebten bereits auf einer Seite) — **keine vollständige Prüfung aller
Fundstellen**. Neue Widerspruchsmarker gehören deshalb **zuerst auf die betroffene Seite selbst**,
nicht (nur) hierher; hier landet nur, was auf keiner Seite unterkommt. Falls hier trotzdem mal
ein bereits andernorts dokumentierter Punkt auftaucht, ist das ein bekanntes Restrisiko der
Kürzung, kein Bug — im Zweifel im Archiv nachschlagen.

## Offene Punkte (nicht durch eine Wiki-Seite abgedeckt)

- **MMXM (Market Maker Buy/Sell Model) hat weiterhin keine eigene Wiki-Seite.** Seit dem ersten
  Ingest (2026-08-02) wiederholt als Lücke notiert (laut Quelle eines von nur zwei "echten"
  Modellen neben [[Graded Price Swings]]). Der Marker steht bereits einzeln auf
  [[Graded Price Swings]] und [[CISD Mini Serie - Lecture 2 (Source)]] ("MMXM hat im Vault
  bislang keine eigene Seite") — hier zusätzlich gelistet, weil `wiki/index.md`s eigene
  "Offene Punkte"-Liste diesen Punkt nicht führt und die Lücke sonst nur über die Volltextsuche
  auf einer der beiden Seiten auffindbar wäre. Kandidat für den nächsten ICT-Ingest.

- **Marktdaten-Lücken, nur mit neuem TradingView-Export lösbar** (yfinance-Backfill scheidet
  aus, weil er fremde Vendor-Preise in eine TradingView-Datei mischen würde — Quelle:
  `log-archiv-bis-2026-08.md:2215`, Eintrag 2026-08-13 "Marktdaten-Nachzug"): **ES 12.08.**
  573 von 1.380 Kerzen, **YM** 10./11./12.08. 875/1.326/509 von je 1.380, **DXY** 10./11./12.08.
  203/1.337/519 von je 1.380. Betrifft keine der beiden Kernserien (MNQ/NQ, ES-Historie sonst
  vollständig) direkt kritisch, aber laut [[Algo-Trading: Arbeitsstandards]] gelten
  Marktdaten-Lücken als nulltoleranzpflichtig und explizit aufzulisten — dieser Punkt war in
  keiner anderen Datei (`wiki/`, `algo/PLAN.md`, `algo/README.md`) auffindbar.
