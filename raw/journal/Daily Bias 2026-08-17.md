# Daily Bias 2026-08-17

> Weekly Bias: _(noch kein Weekly Bias fuer diese Woche geschrieben)_

## News (Red/Orange Folder)
⚠️ News-Abruf fehlgeschlagen, manuell auf forexfactory.com pruefen (HTTP 403 beim WebFetch-Versuch auf forexfactory.com/calendar?day=aug17.2026)

## Levels
⚠️ Live-Daten nicht verfuegbar (Markt geschlossen oder Datenfehler) -- `algo/live_status.py` liefert `market_data: false` (Stand des Laufs: 2026-08-13T18:06 NY, Markt am Wochenende geschlossen). NDOG/NWOG/ORG-C.E. fuer den 17.08. daher noch nicht bestimmbar; kurz vor Sessionstart erneut laufen lassen.

| Level | Open | Close |
|---|---|---|
| Weekly Range (laufende Woche) | -- | -- |

- Weekly Range: nicht verfuegbar (`algo/bias_levels.py 2026-08-17` liefert `weekly_range: null` -- neue Handelswoche beginnt erst mit diesem Tag, noch keine abgeschlossenen Tage)
- Gestrige Daily Range (13.08.2026, letzter Handelstag vor dem Wochenende): High 30267.0 / Low 29780.5 / Close 30223.5

## Wiki-Bezug
- [[Weekly Range Trading Model]]
- [[New Week Opening Gap (NWOG) Bias]] -- Montag: NWOG ist der zentrale wochenoeffnende Level, besonders relevant
- [[ICT Daily Range Session Timing]]
- [[Midnight Opening Range]]
- [[ORG (Opening Range Gap) & 1st Presented FVG]]

## Einschaetzung (Claude)
Live-Levels (NDOG/NWOG/ORG-C.E.) sind fuer diesen Lauf nicht verfuegbar, da der Markt zum
Zeitpunkt der Datenziehung (Freitagabend NY) geschlossen war -- vor Sessionstart am Montag sollte
`algo/live_status.py` erneut laufen, um NWOG (montags gesetzt) und ORG-C.E. tatsaechlich zu
bestimmen.

Saisonale Kennzahl aus `algo/seasonal_tendency.json` fuer Montage (n=28, Datenbasis
`raw/marktdaten/`): 78.6% der Montage bullisch, durchschnittliche Tagesrendite +0.711%,
Median-Range 551 Punkte. Das ist eine auffaellig starke Bullish-Neigung im Vergleich zu den
uebrigen Wochentagen (Di–Fr liegen alle nahe 48–52% bullisch) -- passt zur ICT-These, dass die
Wochenoeffnung (NWOG) oft Richtung fuer die Woche vorgibt, ist aber mit n=28 noch eine
begrenzte Stichprobe und kein Ersatz fuer eine Setup-spezifische Regel.

Da `org_ce` in diesem Lauf nicht gesetzt ist, wird die ORG-C.E.-70%-These hier nicht neu
bewertet (laufend beobachtete Hypothese, aktuell 35-43% im eigenen Backtest, siehe
[[Muster-Validierung (laufend)]] -- Konvention: nicht abhaken, weiter beobachten) -- das holt der
naechste Lauf mit frischen Live-Daten nach.

Kein Red/Orange-Folder-Event bekannt (News-Abruf fehlgeschlagen), daher keine
`backtest_fred_events.py`-gestuetzte Aussage moeglich.

## Mein Bias

