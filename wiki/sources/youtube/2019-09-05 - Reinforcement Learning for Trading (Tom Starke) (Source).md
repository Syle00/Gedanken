---
tags: [source, algo-methodology, machine-learning, reinforcement-learning, youtube]
created: 2026-08-08
updated: 2026-08-08
raw: "[[yt-c0gpgCyjTM8-transcript]]"
raw_path: "raw/algo-ml/yt-c0gpgCyjTM8-transcript.md"
---

# Reinforcement Learning for Trading — Practical Examples and Lessons Learned (Source)

Quelle: YouTube, Kanal **Quantopian**, veröffentlicht 2019-09-05, Länge 43:34.
Vortragender: **Dr. Tom Starke** — Physik-Promotion, algorithmischer Händler bei einem
Eigenhandelshaus in Sydney, zuvor Lehrbeauftragter für Computersimulation in Oxford.

> Praktikerbericht mit ausdrücklichem „Lessons Learned"-Anspruch. Wertvoll gerade wegen der
> Offenheit über das, was **nicht** funktioniert hat. Zitat aus der Einleitung:
> *„I can't give you the Holy Grail unfortunately."*

## Kernaussagen (gefiltert)

### 1. Was nicht funktioniert hat

Auf echten, ungeglätteten Kursreihen erzeugt der Reinforcement Learner **keine** konsistenten
Gewinne. Die konkreten Fehlerbilder, die Starke benennt:

- **Lokale Optima.** Das System bleibt in Zwischenlösungen hängen, läuft eine Weile gut und hört
  dann auf.
- **Nicht reproduzierbar.** Ergebnisse schwanken zwischen Läufen so stark, dass sie schwer
  wiederholbar sind.
- **Stichprobenhunger.** RL ist ausgesprochen dateneffizienzschwach — es braucht sehr viele
  Beispiele.
- **Rauschen ist der eigentliche Gegner.** *„LSTMs and all these other fancy machine learning
  tools are really not designed to deal with a lot of noise. Image recognition doesn't have a lot
  of noise."*

### 2. Der Befund, der auf dieses Projekt passt

Ersetzt man die rohe Kursreihe durch eine **geglättete** (5-Perioden-Durchschnitt), erkennt der
Reinforcement Learner die Struktur plötzlich und erzeugt brauchbare Ergebnisse. Starkes Schluss:
Man solle der Kursreihe erst eine **geometrische Bedeutung** geben und das Lernverfahren darauf
ansetzen, statt es auf rohes Rauschen loszulassen.

> ⚠️ **Eigener Einwand gegen diesen Befund, nicht von Starke selbst genannt.** Ein gleitender
> Durchschnitt ist konstruktionsbedingt autokorreliert — er *muss* leichter vorhersagbar sein als
> die Rohreihe. Entscheidend ist aber: Man handelt nicht zum geglätteten Preis, sondern zum
> echten. Ein Ergebnis auf der geglätteten Reihe ist deshalb erst dann belastbar, wenn die
> Abrechnung zu den **tatsächlichen** Kursen erfolgt. Andernfalls ist es eine klassische
> Selbsttäuschung. Der Grundgedanke — Struktur extrahieren statt Rohdaten füttern — bleibt davon
> unberührt richtig.

### 3. Zeitmerkmale verbessern das Ergebnis spürbar

Unter den Eingangsmerkmalen hebt Starke ausdrücklich hervor:

> *„One of the interesting ones, and this is I think quite a game-changer, is to use time of day,
> day of week, time of year … often that will improve things quite a bit."*

Das ist unabhängige Bestätigung für [[ICT Killzones]] und den Projektgrundsatz „Time before Price"
— aus einer Ecke, die von ICT nichts weiß.

### 4. Belohnungsfunktion ist das eigentliche Problem

Reine P&L als Belohnung führt zur Entartung: Auf einer langfristig steigenden Aktie (sein Beispiel:
Apple) lernt das System schlicht **Kaufen und Halten** und hört auf zu handeln. Gegenmittel, die er
nennt:

- Bestrafung für zu lange Haltedauer
- P&L **pro Zeiteinheit** statt absolute P&L
- Belohnung für erkannte Richtung statt für den Gewinn selbst
- Belohnung für korrekt erkanntes Marktregime

Zusätzliches Problem: Belohnung nur beim Trade-Ende erzeugt **spärliche** Rückmeldung, was das
Lernen erschwert.

### 5. Testmethodik: erst Kunstdaten, dann Markt

Starkes Vorgehen, das er ausdrücklich empfiehlt: zuerst Sinuskurven und reine Trends, dann dieselben
mit Rauschen, dann künstliche autokorrelierte Reihen, **erst danach** echte Kursdaten.
Begründung: Auf einer echten Finanzzeitreihe, die überwiegend einem Zufallspfad gleicht, lässt sich
gar nicht feststellen, ob das Verfahren überhaupt tut, was es soll.

Bemerkenswerter Einzelbefund: Bei einer Sinuskurve, die auf halber Strecke in einen Trend
umgeschaltet wird, erkennt das System den Regimewechsel nach kurzem Zögern und handelt weiter
profitabel — auf sauberen Daten.

### 6. Einfachere Verfahren schlagen komplexere

*„I found simple neural nets are just as good as anything."* Für überwachtes Lernen im Handel
nennt er **Support Vector Machines** als das Verfahren, das bei ihm über Jahre am
zuverlässigsten funktioniert hat — ohne erklären zu können, warum.

### 7. Adaptive-Markets-Vorbehalt

Falls RL im Handel je breit funktioniere und alle es einsetzten, verschwinde der Vorteil wieder
oder der Markt verändere sich grundlegend. Deckt sich mit
[[Machine Learning für den Algo — Bewertung (laufend)]] und dem Edge-Zerfall-Befund von
Neely/Weller.

## Bewusst ausgefiltert

Live-Code-Durchgang durch sein GitHub-Repository (Experience Replay, Q-Learning-Schleife,
Bellman-Gleichung) — Umsetzungsdetails ohne eigenständige Handelsaussage, im Transkript ohne
sichtbaren Bildschirm ohnehin nur bruchstückhaft. Ebenso die einleitende Lehrbuchdarstellung von
Zustand/Aktion/Belohnung/Policy.

## Verwandt

- [[Machine Learning für den Algo — Bewertung (laufend)]] — Gesamteinordnung
- [[2022-07-05 - Two Sigma - Machine Learning Models of Financial Data (Source)|Two Sigma — Machine Learning Models of Financial Data (Source)]] — institutionelles Gegenstück
- [[Meta-Labeling (López de Prado)]] — die Bauform, die Starkes Kernproblem umgeht
- [[ICT Killzones]] — unabhängige Bestätigung der Zeitmerkmale
