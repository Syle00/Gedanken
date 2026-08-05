# Live-Status-Log MNQ — 2026-08-05

## 03:39 ET (Startaufnahme)

**Stand**: Letzter Preis 29923.5 (03:25 ET). Aktiv ist das **London-Silver-Bullet-Fenster
(03:00–04:00 ET)**, kein Makro-Fenster, kein offenes `setup`. `org_ce` ist noch `null` — die
NY-Eröffnungslücke entsteht erst um 09:30 ET, die C.E.-Beobachtung (ICT-These 70 % Fill, empirisch
bislang eher 35–43 %) beginnt also erst in rund sechs Stunden. **NDOG**: Vortages-Close 29890.0
(23:20 ET), heutiger Open 29896.25, Gap **+6.25 Punkte** (sehr klein, deutlich unterdurchschnittlich)
— **bereits gefüllt um 00:10 ET**, also innerhalb von ~40 Minuten. Das passt zur empirischen
Fill-Quote von 86 %, die gerade bei kleinen Gaps praktisch die Regel ist (die 74-%-Ausnahme betrifft
überdurchschnittlich große Gaps). `nwog` ist `null` — heute ist Mittwoch, korrekt.

**Abgleich**: `first_run: true`, das hier ist die **Startaufnahme des gesamten Handelstages**
(Globex-Start 18:00 ET am 04.08.) und keine Liste dessen, was gerade eben passiert ist. Nachtrag zum
gestrigen Log: die dort vermerkte Lücke „`live_status.py` liefert keine NDOG/NWOG-Felder" ist
geschlossen — beide Felder sind jetzt vorhanden und NDOG ist in diesem Lauf befüllt.

Was die Nacht zeigt: 24 FVGs, davon **23 bereits gefüllt** — die schnelle Nachfüllung aus der
gestrigen Session setzt sich unverändert fort. Die Struktur lief in zwei Wellen: erst bearish nach
unten (BOS 18:40 ET auf 29810.25, MSS 21:20 ET auf 29816.5), ab dem Sellside-Sweep um 21:15 ET
(29816.5, 19.75 Punkte Penetration, im selben Bar zurückerobert) dann klar bullish — MSS 23:20 ET
(29889.0), BOS 00:40 ET (29898.25), BOS 01:00 ET (29909.5), BOS 01:45 ET (29949.0). Das ist
lehrbuchmäßig: Sweep der Sellside-Liquidität mit sofortigem Reclaim, danach Trendumkehr nach oben.

Der Buyside-Sweep um 00:55 ET (29909.5, 25.75 Punkte, ebenfalls sofort zurückerobert) hat den
Aufwärtsschub dagegen **nicht** beendet — der Preis lief danach noch bis knapp 29990. Erst der
**MSS 02:20 ET nach unten** (Level 29961.0, Close 29938.0) hat die Serie bullischer Breaks gebrochen,
begleitet von einer großen bearishen FVG 29941.75–29962.75 (21 Punkte), die binnen 10 Minuten
gefüllt war. Seither steht der Preis mit 29923.5 unter diesem MSS-Level — die Struktur ist also
kurzfristig gekippt, während das London-Silver-Bullet-Fenster läuft. Ein Algo-`setup` ist daraus
noch nicht entstanden, was konsistent ist: der MSS liegt zeitlich vor dem Fensterbeginn und es fehlt
bislang ein sauberer Retrace in eine unberührte FVG innerhalb des Fensters.

**Ausblick**: Direkt unter dem Preis liegt unberührte Sellside-Liquidität bei **29920.25** (01:35 ET)
— nur ~3 Punkte entfernt, das wahrscheinlichste unmittelbare Ziel und im laufenden Silver-Bullet-
Fenster ein klassischer Kandidat für einen Sweep-und-Reclaim. Darunter staffeln sich 29883.0
(00:50 ET) und 29859.25 (00:20 ET). Die einzige **noch offene FVG** ist die bullische von 00:30 ET
(29872.75–29888.0, C.E. 29880.375, weder C.E. getroffen noch gefüllt) — sie deckt sich fast exakt
mit dem Sellside-Cluster bei 29883.0 und ist damit die sauberste Long-Zone, falls das Fenster nach
unten läuft. Nach oben liegt Buyside bei **29987.25** (03:00 ET) und 29990.75 (02:10 ET), rund 64–67
Punkte entfernt — für eine Rückeroberung müsste erst der MSS-Level 29961.0 zurückgeholt werden.
Bis 04:00 ET läuft das London-Silver-Bullet-Fenster, danach ist bis zum NY-Open Ruhe; die nächsten
strukturell relevanten Marken sind der 09:30-Open mit der dann entstehenden ORG und das
NY-Silver-Bullet-Fenster 10:00–11:00 ET.
