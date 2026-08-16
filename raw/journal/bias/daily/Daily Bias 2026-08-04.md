Daily Bias 
Gestriger Tag stark bullish wie antizipiert wir haben das NWOG fast komplett gefilled mit Price Action also der Daily Wick. Genau das wollte ich sehen ich bin gespannt ob das auch die Weekly Wick ist und das das low der WOche ist? 

DAs NWOG war groß aber nicht extrem groß, sodass wir davon ausgegangen das dieses gefilled wird. Wenn Gaps enorm groß sind also mehrere 100 Punkte bei z.b dem ORG NDOG oder NWOG sinkt die wahrscheinlichkeit das dieses gefilled und wir antizipieren ehr eine expansion ohne das dass gap gefilled wird.

Wir haben gestern knapp unterhalb des C.E des Suspensionsblock geclosed 
![Daily](journal-2026-08-04-1D.png)

Geöffnet haben wir heute knapp unter dem c.e und sind bis jetzt weiterhin Bullish expandierend Richtung meines DOL Buyside.

Im 4h chart zeigen wir bis jetzt respekt gegenüber dem C.E das ist weiterhin Bullish für mich. WIr stehen unterhalb des NDOG 23.07 und haben wahrscheinlich das C.E des NDOG 23.07 respektier? ja nein? nutze die marktdaten.
![4h](journal-2026-08-04-4h.png)

Im 1h chart zeigen wir gro0e wicks zur uppside das sieht für mich nach respekt nach obenhin aus wir stehen aber auch vor der NY Pre Market Session was Sinn macht für mich ist das wir jetzt langsam ein Retracement erhalten aber spätestens beim ORG um dan weiter zum DOL zu expandieren
![1h](journal-2026-08-04-1h.png)
Das C.E des ORG vom Mittwoch 22.07 bei 28,984,00 wurde ebenfalls genutzt
![15m](journal-2026-08-04-15m.png) interessant wie das NDOG respektiert wird, das sind klare algorytmgische anzeichen genau nach sowas suche ich und möchte sie nutzen
Asia Range war wieder stark mit 217,75 Punkten wohin gegen wir in Lodon wenig Bewegung erhalten haben mit nur 95 Punkten. WIr haben bis jetzt keine heutige SEssion Liqudität genommen. Wir haben in London also sichtlich consolidiert und warten wohl ab. 
![5m](journal-2026-08-04-5m.png)
![1m](journal-2026-08-04-1m.png)
Mein heutiger Bias ist also ähnlich zu gestern Bullish mit warten auf sweep sellside also judas. Ich korigiere ich sehe asia hat das low der gestrigen NY PM Session genommen und es wurde london low genommen

---

## Verifikation gegen yfinance-Marktdaten (MNQ=F, frisch gezogen)

> ⚠️ **Datenintegrität:** `raw/marktdaten/2026/08/` ist aktuell beschädigt — die pro-Tag benannten
> Dateien (z.B. `MNQ 2026-08-04 1h.csv`) enthalten für 1h/4h/1d (und teils 15m) nicht nur den
> jeweiligen Tag, sondern Monate an History (1h-Datei für 04.08. reicht z.B. bis 16.07. zurück).
> Nur die 1m-Dateien sind sauber pro Tag geschnitten. Für diese Verifikation wurde daher direkt
> per `yfinance` neu gezogen statt den Cache zu nutzen (wie gewünscht — "neu ziehen tue das immer").
> Die Cache-Pipeline (`algo/fetch_yfinance.py`) sollte bei Gelegenheit separat geprüft werden,
> das ist kein reines Anzeigeproblem, die Dateien selbst sind falsch beschriftet.

**NWOG-Fill (Frage: "ist das auch das Weekly Low?"):** Bestätigt, mit Präzisierung. Freitag
31.07 schloss bei 28.284,00, Montag 03.08 eröffnete bei 28.567,50/28.602,75 (Premium). Montags
Tagestief lag bei **28.313,00** (03.08, 09:00 NY) — das NWOG (28.284–28.567) wurde damit bis auf
29 Punkte an den unteren Rand angefahren, aber **nicht vollständig** gefüllt (dafür hätte es unter
28.284 gehen müssen). "Fast komplett gefilled" trifft es also genau. Und ja: 28.313,00 ist nach
aktuellem Stand (Di. 04.08., ~06:30 NY, bisheriges Tagestief heute 28.968,50) weiterhin das
**Wochentief**.

**C.E. NDOG 23.07 (29.107,50–29.168,75, C.E. ≈ 29.138,13) — "respektiert? ja/nein":**
Noch offen, nicht "ja" wie im Entwurf vermutet. Bisheriges Hoch heute liegt bei **29.132,25**
(04:00 NY) — das ist knapp **unterhalb** des C.E., rund 6 Punkte davor. Der Test hat also noch
nicht stattgefunden; von "respektiert" zu sprechen ist verfrüht, solange der C.E. nicht erreicht
und zurückgewiesen wurde. Beobachten, ob beim nächsten Anlauf dort eine Reaktion kommt.

**C.E. ORG Mi. 22.07 (28.984,00):** Plausibel. Preis lief in der Nacht zum 04.08. (~00:00–01:00
NY) durch dieses Level, auf Stundenbasis ohne sauber sichtbare Reaktion — auf 5m/15m (siehe
Chart) zeigt sich ein kurzes Zögern in dem Bereich. Kein klarer Widerspruch zur Beobachtung.

**Asia Range (217,75 Punkte):** Exakt bestätigt. Fenster 20:00–00:00 NY (03.08.→04.08.): Hoch
29.049,25 (21:50 NY), Tief 28.831,50 (21:00 NY) → Range 217,75.

**London Range (95 Punkte):** Exakt bestätigt, mit dem Fenster 03:00–05:00 NY: Hoch 29.132,25
(04:20 NY), Tief 29.037,25 (03:10 NY) → Range 95,00.

**Selbstkorrektur "Asia hat NY-PM-Low genommen":** Bestätigt. NY-PM-Session gestern
(13:30–16:00 NY) hatte ihr Tief bei 28.865,75 (15:55 NY). Asias Tief (28.831,50) liegt klar
darunter — Sweep bestätigt.

**Selbstkorrektur "London Low wurde genommen":** ✅ Bestätigt (Nutzer-Korrektur war richtig,
meine erste Prüfung falsch). Mein 03:00–05:00-Fenster war zu eng geschnitten und endete genau vor
dem Sweep. Um **05:06 NY** fiel der Preis auf ein Tief von **29.032,75** — das liegt unter dem
vorherigen London-Tief von 29.037,25 (03:10 NY). Sweep bestätigt, nur ~5 Minuten außerhalb meines
ursprünglichen Fensters.

## ForexFactory Economic Calendar — Di. 04.08.2026 (NY Time)

> ⚠️ ForexFactory blockiert direkten Zugriff (403 bei jedem Versuch). Die Impact-Spalte unten kam
> ursprünglich von tradingeconomics.com als Ersatzquelle — deren Einstufung entspricht nicht den
> FF-Ordnerfarben. Nutzer-Korrektur vor Ort auf forexfactory.com: **Trade Balance = Yellow**,
> **JOLTs Job Openings = Orange**. Übernommen unten. Factory Orders / restliche Zeilen sind weiterhin
> ungeprüft gegen die echte FF-Seite — bei Bedarf bitte ebenfalls gegenchecken.

| Zeit (NY) | Event | Impact (FF, korrigiert) |
|---|---|---|
| 06:00 | LMI Logistics Managers Index (Jul) | Mittel (ungeprüft) |
| 08:30 | Balance of Trade (Jun), Forecast -73,0B | **Yellow (Low)** ✅ korrigiert |
| 08:30 | Exports / Imports (Jun) | Mittel (ungeprüft) |
| 10:00 | JOLTs Job Openings (Jun), Forecast 7,3M vs. 7,4M prev. | **Orange (Medium)** ✅ korrigiert |
| 10:00 | Factory Orders MoM (Jun), Forecast 0,4% vs. 0,2% prev. | Ungeprüft (ursprünglich als Hoch/Red gemeldet — Vorsicht) |
| 10:00 | JOLTs Job Quits (Jun) | Mittel (ungeprüft) |
| 11:30 | 52-Week / 6-Week Bill Auction | Niedrig (ungeprüft) |
| 16:30 | API Crude Oil Stock Change | Mittel (ungeprüft) |

Mit der Korrektur gibt es heute **kein bestätigtes Red-Folder-Event** mehr um 08:30/10:00 (Yellow/
Orange statt Red) — die ursprüngliche Idee unten ("Judas-Swing um die Red-Folder-News") war auf
einer falschen Prämisse aufgebaut und damit zu verwerfen. Ohne Red-Folder-Katalysator ist eine
Volatilitätsspitze zu diesen Uhrzeiten weniger wahrscheinlich; der Judas-Swing/Sweep-Sellside-Bias
sollte eher aus der reinen Price-Action (C.E. NDOG 23.07 bei 29.138, noch offen) hergeleitet werden
als aus der News-Erwartung.