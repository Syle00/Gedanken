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

- **Marktdaten-Lücken, nur mit neuem TradingView-Export lösbar** (yfinance-Backfill scheidet
  aus, weil er fremde Vendor-Preise in eine TradingView-Datei mischen würde — Quelle:
  `log-archiv-bis-2026-08.md:2215`, Eintrag 2026-08-13 "Marktdaten-Nachzug"): **ES 12.08.**
  573 von 1.380 Kerzen, **YM** 10./11./12.08. 875/1.326/509 von je 1.380, **DXY** 10./11./12.08.
  203/1.337/519 von je 1.380. Betrifft keine der beiden Kernserien (MNQ/NQ, ES-Historie sonst
  vollständig) direkt kritisch, aber laut [[Algo-Trading: Arbeitsstandards]] gelten
  Marktdaten-Lücken als nulltoleranzpflichtig und explizit aufzulisten — dieser Punkt war in
  keiner anderen Datei (`wiki/`, `algo/PLAN.md`, `algo/README.md`) auffindbar.

- **ICT-Videos mit `[Silent]` im Titel sind mit dem aktuellen Setup nicht ingestierbar.** Sie
  haben keine Auto-Captions (`Subtitles are disabled for this video`), und der einzige Fallback
  wäre Whisper — dafür fehlt **`ffmpeg` auf diesem Rechner** (`where ffmpeg` findet nichts).
  Erster konkreter Fall: `ICT Obsidian NQ Short 08/17/2026 \ Silent` (`UJU7MZzTSM4`,
  2026-08-18, 2:10:30) — 130 Minuten dokumentierte Chartarbeit zum selben NQ-Short, den
  [[2026-08-18 - Trade Management & Removing The Need To Be Right (Source)|Trade Management & Removing The Need To Be Right (Source)]]
  nur teilweise abdeckt. Kein Einzelfall, sondern eine ganze Videoklasse des Kanals; hier
  gelistet, weil es keine Wiki-Seite gibt, der die Lücke gehört. Auflösbar durch eine
  `ffmpeg`-Installation, dann Whisper-Fallback über
  `.claude/skills/yt-ict-ingest/SKILL.md` Schritt 2.

## Offen: Paper-Konto und Live-Konto laufen im Journal in derselben Geldstatistik

Der Trade vom 2026-08-19 (siehe `journal/entries/2026-08-19 ES 1011 Silver Bullet.md`) lief auf
einem **Paper-Trading-Konto** in ES, während `journal/config.yaml` das Lucid-Live-Konto (25 000 $,
MNQ) beschreibt. Das Journal kennt dafür kein Trennmerkmal: `modus` unterscheidet nur `live` und
`replay`, und `replay` ist sachlich falsch — die Marktdaten waren echt, nur das Geld nicht.

Zwei Folgen, beide noch ungelöst:

1. **Die Geldbilanz vermischt sich.** `report.py` summiert `ergebnis_betrag` über alle
   `live`-Einträge; die −700 $ Papiergeld stehen damit neben echten Lucid-Ergebnissen.
2. **R01/R08/R09 rechnen gegen die falschen Grenzen.** Die Flags sind für diesen Trade
   automatisch gesetzt worden, obwohl kein echtes Risiko-Limit verletzt wurde. Auf der
   Eintragsseite ist das als ⚠️-Block eingeordnet, aber die CSV-Spalte `fehler` trägt sie
   ungefiltert.

Bewusst **nicht** eigenmächtig gelöst — ob Paper-Trades eine eigene `modus`-Stufe, ein zweites
Konto in der Config oder gar keine Sonderbehandlung bekommen, ist eine Entscheidung über die
Auswertung und gehört Jannes. Bis dahin: Paper-Einträge tragen den Hinweis im Fließtext.

Verwandt: [[Kontraktspezifikation MNQ (Tick, Punktwert)]] — R09 hat hier zusätzlich nicht
angeschlagen, weil das Skript Kontrakte instrumentneutral zählt (2 ES = 50 MNQ im Punktwert).
