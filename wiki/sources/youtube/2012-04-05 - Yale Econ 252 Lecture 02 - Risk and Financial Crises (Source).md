---
tags: [source, quant-finance, yale-econ252, risikomanagement]
created: 2026-08-12
updated: 2026-08-12
sources: ["[[Value at Risk, CoVaR & Unabhängigkeitsannahme (Yale Econ 252)]]"]
---

# Yale Econ 252 — Lecture 2: Risk and Financial Crises (Source)

Quelle: YouTube, Kanal YaleCourses, veröffentlicht 2012-04-05, Länge 1:09:44. Open Yale Courses,
Economics 252, Robert Shiller.
Rohtranskript: `raw/financial-markets-2011-with-robert-shiller/yt-QbosMr2JVrc-transcript.md`.

## Zusammenfassung

Wahrscheinlichkeits-Grundlagen (Erwartungswert, Varianz, Kovarianz, Korrelation), angewendet auf
die Finanzkrise 2007–2009. **Risikomanagement-Kernvorlesung**: These, dass die Krise durch den
Bruch zweier Annahmen erklärbar ist — Unabhängigkeit von Risiken und Normalverteilung
(fat tails). Vollständig ausgearbeitet in
[[Value at Risk, CoVaR & Unabhängigkeitsannahme (Yale Econ 252)]].

## Kernpunkte

- VaR (nach 1987 entstanden) und ihre Nachfolgerin CoVaR (Brunnermeier) — Grundproblem: VaR-Modelle
  unterschätzten systematisch Tail-Risiken, weil sie (implizite) Unabhängigkeit annahmen.
- Gesetz der großen Zahlen als gemeinsames Fundament von Diversifikation und Versicherung — bricht
  in Krisen, weil Korrelationen dann stark ansteigen.
- Fat-Tail-Verteilungen (Lévy/Mandelbrot): Crash 19.10.1987 (−20,47 % an einem Tag) hätte unter
  Normalverteilung eine Wahrscheinlichkeit von `10⁻⁷¹` — beweist empirisch das Versagen der
  Normalverteilungsannahme.
- Apple-Fallstudie: Beta ≈ 1,45, aber idiosynkratisches Risiko dominiert Einzelbewegungen
  (Steve-Jobs-Gesundheitsgerücht 2008 überdeckte kurzzeitig sogar den Lehman-Crash-Effekt).

## Bezug

Siehe [[Value at Risk, CoVaR & Unabhängigkeitsannahme (Yale Econ 252)]] für die vollständige
Herleitung und den Projektbezug zu `algo/validate.py`/`algo/stress_test.py`.
