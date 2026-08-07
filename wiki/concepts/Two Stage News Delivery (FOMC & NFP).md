---
tags: [concept, ict, trading-ict, macro, news-driven, hypothesis]
created: 2026-08-07
updated: 2026-08-07
sources: ["[[FOMC (Federal Open Market Committee)]]", "raw/journal/Daily Bias 2026-08-07.md", "raw/marktdaten/2026/08/07.08.2026/MNQ 2026-08-07 1m.csv"]
---

# Two Stage News Delivery (FOMC & NFP)

> ⚠️ **Offene Hypothese, n=1.** Noch nicht über mehrere Events verifiziert — bei jedem künftigen
> FOMC- und NFP-Termin gegenprüfen und diese Seite nachführen (siehe [[Algo: proaktiv
> gegenprüfen]] in `wiki/log.md`-Konvention).

Beobachtung des Nutzers: der große Newsdriver liefert Preis nicht in einem Zug, sondern in
**zwei zeitlich getrennten Stages**, die in entgegengesetzte Richtungen laufen können — die
erste unmittelbar an der News, die zweite deutlich später (in etwa im Fenster der
[[Silver Bullet Model|NY-AM-Silver-Bullet]]-/[[NY Lunch Macro Model|Lunch-Macro]]-Session).
Bislang war das nur als fehlende Quelle bekannt: **Lektion 02 der [[MentorShip 2025]]-Reihe**
heißt *"Trading FOMC Two Stage Delivery"*, liegt aber nicht in `raw/`. Diese Seite trägt die
erste live beobachtete, datengeprüfte Instanz des Musters — für FOMC noch unbelegt, aber am
07.08.2026 explizit an einem **NFP**-Termin beobachtet, was nahelegt, dass es kein
FOMC-exklusives Muster ist, sondern generell für High-Impact-Red-News gilt.

## Beobachtete Instanz: NFP 2026-08-07 (MNQ)

Gegen die 1-Minuten-Daten aus `raw/marktdaten/2026/08/07.08.2026/MNQ 2026-08-07 1m.csv` geprüft:

| Zeit (NY) | Preis | Ereignis |
|---|---|---|
| ~04:00–08:00 | Range 29.596–29.612 | Pre-Market-Sellside-Pool bildet sich (mehrfach getestete Tiefs) |
| **08:29** (unmittelbar vor dem 8:30-Print) | Low **29.596,00** | Sellside-Sweep der Pre-Market-Range — erster Griff der News |
| **08:30–08:49** | High **29.854,50** | **Stage 1**: massive Buyside-Expansion, +258 Punkte in 19 Minuten |
| 09:40–10:11 | Preis dreht, fällt zurück Richtung 29.640 | Übergang / Aufbau zu Stage 2 |
| **10:12** | Low **29.564,25** | **Stage 2**: zweiter, deutlich tieferer Sellside-Sweep — unterbietet sogar das Stage-1-Tief |
| ab ~10:20 | Erholung Richtung 29.720–29.750 | Stage 2 endet, Range beruhigt sich |

⚠️ Der Nutzer notierte den Pre-Market-Tiefpunkt als „5:53 Low 29.600,50" — die CSV-Daten zeigen
diesen Preisbereich (29.600,5 exakt getroffen um 04:05, danach mehrfach zwischen 29.599–29.612
zwischen 04:00 und 08:00 retestet), aber nicht exakt um 05:53. Zeit/Preis dürften vom
Charting-Feed des Nutzers stammen und minimal von diesem Datensatz abweichen — die
**strukturelle Aussage (Pre-Market-Tief als Sellside-Pool, an der News gesweept) ist bestätigt**,
nur der exakte Zeitstempel nicht 1:1 reproduzierbar.

## Generalisiertes Muster (Arbeitshypothese)

1. **Vor der News** baut sich ein erkennbarer Liquidity Pool auf (hier: Pre-Market-Low als
   [[External vs. Internal Range Liquidity|External Range Liquidity]]).
2. **Stage 1 — an der News selbst** (8:30 bei NFP, 14:00 bei FOMC): Sweep der naheliegenden
   Pool-Seite, dann scharfe Umkehr und Expansion in die Gegenrichtung. Läuft wie ein
   verschärfter [[Judas Swing]] / [[Market Protraction]]-Ausschlag, nur größenordnungsmäßig
   stärker als die üblichen getakteten Fensters.
3. **Pause/Konsolidierung** in den ~45–60 Minuten danach.
4. **Stage 2 — zeitlich versetzt** (hier ~1h42min nach der News, im Fenster von
   [[NY Lunch Macro Model|10-Uhr-Linie]]/Silver-Bullet-NY-AM): zweite, oft stärkere Bewegung in
   die **Gegenrichtung von Stage 1**, die das Stage-1-Extrem unterbietet/überbietet. Das ist die
   eigentliche „Two Stage Delivery" — zwei getrennte algorithmische Lieferungen, keine einzelne
   News-Reaktion.

## Warum das relevant ist

Falls sich das Muster bestätigt, heißt das für [[FOMC (Federal Open Market Committee)]]- und
NFP-Tage: **die unmittelbare News-Reaktion (Stage 1) ist nicht zwangsläufig die Tagesrichtung.**
Das deckt sich mit der bestehenden Linie in [[Low Resistance Liquidity Run]] (FOMC-Wochen =
High-Resistance/Chop-Kandidat) und mit der bereits im Journal notierten Vorsicht, an NFP-Tagen
keinen belastbaren Daily Bias zu halten (siehe `raw/journal/Daily Bias 2026-08-07.md`).

## Nächste Schritte

- Bei jedem künftigen NFP (1. Freitag im Monat) und FOMC-Termin dieselbe Zwei-Stufen-Prüfung
  fahren und hier eintragen (Datum, Stage-1-/Stage-2-Zeiten, Preise, Richtung).
- Sobald ≥3 Instanzen vorliegen: Kandidat für ein `algo/backtest_*.py`-Skript, das NFP-/FOMC-Termine
  gegen `raw/marktdaten/` automatisiert auf dieses Zwei-Stufen-Muster prüft (Datumsliste der
  Termine fehlt aktuell noch im Repo).
- Bei Gelegenheit prüfen, ob Lektion 02 der MentorShip-2025-Reihe („Trading FOMC Two Stage
  Delivery") doch noch als Notion-Export auftaucht — würde diese Hypothese direkt mit
  Primärquelle unterlegen.

## Verwandt

- [[FOMC (Federal Open Market Committee)]]
- [[MentorShip 2025]] — Lektion 02, die namensgebende fehlende Quelle
- [[Market Protraction]], [[Judas Swing]] — verwandte getaktete Manipulationsfenster
- [[Silver Bullet Model]], [[NY Lunch Macro Model]] — das Stage-2-Zeitfenster
- [[External vs. Internal Range Liquidity]] — der Pre-Market-Pool als External Liquidity
- [[Low Resistance Liquidity Run]] — FOMC/NFP als Chop-Kandidat
