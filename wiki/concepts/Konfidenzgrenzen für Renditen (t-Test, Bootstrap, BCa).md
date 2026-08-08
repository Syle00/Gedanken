---
tags: [concept, algo-methodology, validation, statistik]
created: 2026-08-08
updated: 2026-08-08
sources: ["[[Testing and Tuning Market Trading Systems (Source)]]"]
---

# Konfidenzgrenzen für Renditen (t-Test, Bootstrap, BCa)

Wie man aus einer Sammlung von OOS-Renditen eine **Untergrenze für die wahre mittlere Rendite**
ableitet — die Zahl, um die künftige Renditen streuen werden. Aus
[[Testing and Tuning Market Trading Systems (Source)]] (Kap. 6).

Kernargument: ein guter Backtest-Mittelwert reicht nicht. Bei genug Bars findet jeder
Hypothesentest auch den winzigsten echten Edge — eine statistisch gesicherte Rendite von 0,5 %
p.a. will trotzdem niemand handeln. Also braucht man nicht „ist der Edge echt?", sondern „wie
klein könnte er sein?".

## Was zuerst geklärt sein muss

Ein P-Wert sagt: *falls* das System wertlos ist, wie wahrscheinlich wäre ein so gutes Ergebnis
durch Glück. Er sagt **nicht**, wie wahrscheinlich es ist, dass das System wertlos ist. Masters'
Hunde-Analogie dazu: 1 % aller Hunde haben weniger als vier Beine, also ist ein Zweibeiner
wahrscheinlich kein Hund — außer der Anrufer kommt aus einem Hundeheim und ruft *nur* wegen
Hunden an, dann liegt man jedes Mal falsch. Der P-Wert ist bedingt und sagt nichts über die
Grundgesamtheit der geprüften Systeme.

Ebenso: ein *nicht* kleiner P-Wert erlaubt **nie** den Schluss, das System sei wertlos. Vielleicht
wurde nur zu wenig getestet.

## Weg 1: parametrisch (Student-t)

Mit `Mean` und `StdDev` der `n` OOS-Renditen:

- t-Score unter H₀ (wahrer Mittelwert = 0): `t = √n · Mean / StdDev`
- P-Wert: `1 − CDF_t(n−1, t)`
- **Untergrenze** bei Konfidenz `p`: `LowerBound = Mean − StdDev · t_p / √n`
  mit `t_p = InvCDF_t(n−1, p)`

Praktische Abkürzung, die Masters betont: **die Nullhypothese wird genau dann verworfen, wenn
die Untergrenze positiv ist.** Man braucht also gar keinen separaten Hypothesentest — es genügt,
die Untergrenze zu berechnen.

Beispielrechnung: n=100, Mean=8, StdDev=5, p=0,95 → `t_p ≈ 1,66` →
`8 − 5·1,66/√100 = 7,17`.

Für ein beidseitiges Intervall muss die Fehlerwahrscheinlichkeit gesplittet werden (90 %-Intervall
= je 5 % oben und unten, also p=0,95 für **beide** Grenzen).

**Die eine Bedingung:** der t-Test ist robust gegen moderate Schiefe und mäßig schwere
Verteilungsenden, aber **ein einziger wilder Ausreißer macht ihn wertlos**. Liegen die Renditen
zwischen −5 und +5 und eine bei 50, ist die Zahl Müll. Deshalb: **vor jedem t-Test ein Histogramm
der Renditen ansehen.**

## Weg 2: Bootstrap

Grundidee (Efron): die eigene OOS-Stichprobe so behandeln, als wäre sie die Grundgesamtheit, und
daraus mit Zurücklegen tausende Stichproben gleicher Größe ziehen. Die Streuung der daraus
berechneten Kennzahlen schätzt die Streuung, der die Originalstichprobe selbst unterlag.

Drei Verfahren:

- **Pivot-Methode** — intuitiv (die Verzerrung Sample→Bootsample wird auf Population→Sample
  übertragen), in Masters' Tests aber durchweg **die schlechteste**. Grenzen entstehen aus den
  Perzentil-Grenzen: `PivotLower = 2·Param − PctileUpper`.
- **Perzentil-Methode** — schlicht: das 5. Perzentil der Bootstrap-Verteilung ist die 95 %-
  Untergrenze. Funktioniert überraschend oft gut. Kurios: Pivot und Perzentil liefern spiegelbildliche
  Intervalle.
- **BCa** („bias corrected and accelerated") — Masters' Empfehlung. Vier Schritte:
  1. **Bias-Korrektur** `z₀ = Φ⁻¹( #[θ̂ᵇ < θ̂] / B )` — wie viele Bootstrap-Schätzungen unter
     der Originalschätzung liegen.
  2. **Acceleration** `â` über ein Jackknife (jeden Fall einmal weglassen, Kennzahl neu rechnen);
     `â = Σ(θ̄₍·₎−θ̂₍ᵢ₎)³ / (6·[Σ(θ̄₍·₎−θ̂₍ᵢ₎)²]^{3/2})`.
  3. Fraktilpunkte verschieben:
     `α' = Φ( z₀ + (z₀ + Φ⁻¹(α)) / (1 − â·(z₀ + Φ⁻¹(α))) )`.
  4. Aus den sortierten Bootstrap-Werten die verschobenen Fraktile ziehen (`k = α'(B+1)`,
     abgerundet; obere Grenze bei Element `B+1−k`).

  Sind `z₀` und `â` beide null, ist BCa identisch mit der Perzentil-Methode.

`nboot = 10.000` nennt Masters als vernünftige Mindestgröße.

## Warnung: Verhältniskennzahlen bootstrappen schlecht

Sharpe Ratio und Profit Factor haben einen Nenner, der klein werden kann — und dann explodiert
die Kennzahl. Masters' `BOOT_RATIO`-Experiment (Systeme mit Gewinnwahrscheinlichkeit 0,5, also
wertlos) zeigt:

- Die Pivot-Methode versagt am deutlichsten: bei 50 Trades und 2,5 % Sollfehlerrate wird die
  Profit-Factor-**Untergrenze nie** verletzt (also unbrauchbar niedrig), während die Obergrenze
  fast **viermal so oft** verletzt wird wie erlaubt.
- Profit Factor verhält sich schlechter als Sharpe.
- **Lösung: den Logarithmus des Profit Factors bootstrappen**, nicht den Profit Factor selbst.
  Das zähmt das rechte Verteilungsende, und die Untergrenze — die einzige, die interessiert —
  wird deutlich zuverlässiger. Verallgemeinert: bei schwerem Verteilungsende immer erst
  transformieren.

## Was das an einem echten Beispiel bedeutet

`BOUND_MEAN` auf SPX, 23.557 Tage, MA-Breakout, Walk-Forward mit 1.000 Trainings-/100 Testbars:
Die annualisierte mittlere Rendite über Bars mit offener Position beträgt **9,91 %** — isoliert
betrachtet beeindruckend. Der zugehörige t-Test-P-Wert liegt bei **0,1000**, und die
90 %-Untergrenze für den wahren Mittelwert ist **−0,0022**, also negativ. Alle drei
Bootstrap-Varianten liefern ähnlich ernüchternde Grenzen.

> Genau darum geht es auf dieser Seite: eine zweistellige Backtest-Rendite kann eine
> Untergrenze unter null haben. Für `algo/` heißt das, dass Reports wie
> [[Ensemble-Strategie — Backtest-Ergebnis & Commission-Verzerrung (laufend)]] neben Profit
> Factor und Return eine Untergrenze ausweisen sollten — sonst fehlt die Information, ob die
> Zahl überhaupt von null unterscheidbar ist.

## Voraussetzung: die richtige Rendite-Sorte

Alle Verfahren hier setzen **unabhängige** Beobachtungen voraus. Welche Renditen man dafür
nimmt, ist keine Nebensache — siehe [[Profit pro Bar vs. pro Trade]] und, für die
Unabhängigkeit, [[Walk-Forward Guard Buffer & Varianz-Inflation]]. Masters' Favorit ist die
**mittlere Bar-Rendite über Bars mit offener Position**.

Für Grenzen um **einzelne** künftige Renditen statt um deren Mittelwert siehe
[[Grenzen für Einzelrenditen & Drawdown]].
