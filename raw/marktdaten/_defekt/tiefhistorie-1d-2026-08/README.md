# Defekte MNQ-Tiefhistorie 1d (aussortiert 2026-08-13)

Diese beiden Sammel-Dateien lagen urspruenglich in
`2026/07/31.07.2026/` bzw. `2026/08/03.08.2026/` und enthielten je ~290 Daily-Bars
(2025-06-08 bis 2026-07-30 / 2026-08-02).

**Warum aussortiert:** Alle Bars sind falsch, nicht nur die auffaelligen.

1. **71 degenerierte Bars** (2025-06-09 .. 2025-12-18) mit `open == high` und `low == close` —
   keine echten OHLC-Werte, Premium-/Discount-Wick rechnerisch 0 Punkte.
2. **Alle 230 mit einem frischen Abruf ueberlappenden Bars weichen ab**, auch die formal
   gesunden. Beispiel 2025-06-23: Datei O 23 150,00 vs. frisch O 21 648,25 (~1 500 Punkte).
3. **Kein einziger** der 290 Bars findet sich im frischen Abruf wieder — auch nicht an einem
   anderen Datum. Eine reine Datumsverschiebung ist damit ausgeschlossen; es sind andere Preise.

**Welche Quelle stimmt:** Der frische `MNQ=F`-Abruf deckt sich fuer den 04.08.–13.08.2026 in
Open/High/Low **exakt** mit den gegen TradingView verifizierten Einzeltagesdateien. Die
Sammel-Dateien decken sich mit nichts. Vermutete Ursache: eine back-adjustierte bzw. auf einen
anderen Kontrakt zeigende Yahoo-Serie zum Abrufzeitpunkt (vgl. die B-ADJ-Falle bei
TradingView-Exporten).

Ersetzt durch Einzeltagesdateien aus `algo/fetch_yfinance.py --intervals 1d`.
Nicht wieder in den aktiven Bestand zurueckschieben.
