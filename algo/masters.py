#!/usr/bin/env python3
"""Python-Portierung der Validierungsverfahren aus Timothy Masters, *Testing and Tuning
Market Trading Systems* (Apress 2018) -- siehe
`wiki/sources/Testing and Tuning Market Trading Systems (Source).md` fuer die Herleitungen,
Formelnummern und Referenzzahlen.

Das Buch druckt seinen C++-Code nur in Fragmenten; die vollstaendigen .CPP-Dateien liegen
nicht im EPUB. Dieses Modul portiert die algorithmische Substanz und delegiert alles, wofuer
es fertige Numerik gibt (t-/Beta-Verteilung, BCa-Bootstrap, Sortieren, SVD), an scipy/numpy --
Masters' STATS.CPP/SVDCMP.CPP/QSORTD.CPP werden also NICHT nachgebaut.

Bewusst NICHT enthalten (Begruendung je Punkt):
  * CoordinateDescent (Elastic Net)  -> sklearn.linear_model.ElasticNetCV.
    ACHTUNG Namensfalle: sklearns `alpha` ist Masters' lambda, sklearns `l1_ratio` sein alpha.
  * Differential Evolution           -> scipy.optimize.differential_evolution.
  * PARAMCOR (Hessian-Analyse)       -> haengt an einer DE-Endpopulation, die es hier nicht gibt.

Alle Renditen sind LOG-Renditen (Differenzen von Log-Preisen), wie im ganzen Buch. Damit
heben sich +10 %/-10 % exakt auf, statt ~1 % Scheingewinn zu erzeugen.

Selbstcheck:  python algo/masters.py
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Iterator, Sequence

import numpy as np
from scipy import stats
from scipy.special import betainc

__all__ = [
    "guard_buffer", "walkforward",
    "entropy", "clean_tails", "gap_analyze",
    "drawdown", "dd_to_pct", "drawdown_quantiles", "drawdown_bound", "drawdown_bound_naive",
    "find_quantile", "return_bound", "orderstat_tail", "quantile_conf",
    "lower_bound_t", "lower_bound_bca", "log_profit_factor", "profit_factor", "sharpe_ratio",
    "permute_prices", "permute_bars", "permute_multi",
    "cscv", "stoc_bias", "partition_return", "Partition",
    "bar_returns_from_trades",
]


# --------------------------------------------------------------------------------------
# Kapitel 5 -- Walk-Forward mit Guard Buffer
# --------------------------------------------------------------------------------------

def guard_buffer(lookback: int, lookahead: int) -> int:
    """OMIT = min(LOOKAHEAD, LOOKBACK) - 1, nie negativ.

    So viele juengste Faelle muessen am Ende des Trainingsblocks gestrichen werden, damit
    keine Information ueber den Testblock ins Training leckt. Nur noetig, wenn Indikatoren
    UND Ziel seriell korreliert sind -- ist der Lookahead 1, ist das Ergebnis 0.

    `lookback` = groesster Lookback ueber ALLE Indikatoren.

    Masters' Zahl zur Groessenordnung: ohne Puffer erreicht ein wertloses System auf reinen
    Random-Walk-Daten einen Median-t-Score von 74,64 statt 0; mit omit=8 statt der noetigen 9
    immer noch 1,88. Es gibt kein "fast genug gepuffert"."""
    return max(min(lookback, lookahead) - 1, 0)


def walkforward(n: int, ntrain: int, ntest: int = 1, omit: int = 0,
                extra: int = 0) -> Iterator[tuple[slice, slice]]:
    """Liefert (train_slice, test_slice) je Fold.

    Gegen Varianz-Inflation bei Lookahead > 1: ntest=1 und extra=LOOKAHEAD-1 setzen, damit
    sich die OOS-Faelle keine Kursinformation teilen. Sonst werden praktisch alle
    Signifikanztests anti-konservativ (P-Werte zu klein, Konfidenzintervalle zu eng).

    Der letzte Fold wird gekuerzt, wenn die Historie nicht aufgeht."""
    if ntrain <= omit:
        raise ValueError(f"ntrain={ntrain} muss groesser als omit={omit} sein")
    start = ntrain
    while start < n:
        nt = min(ntest, n - start)
        yield slice(start - ntrain, start - omit), slice(start, start + nt)
        start += nt + extra


# --------------------------------------------------------------------------------------
# Kapitel 2 -- Indikator-Vorpruefung
# --------------------------------------------------------------------------------------

def entropy(x: Sequence[float], nbins: int = 20) -> float:
    """Relative Entropie (Gleichung 2-1, normiert auf log(nbins)) -> [0, 1].

    Der Wertebereich wird in gleich BREITE Bins geteilt, nicht in gleich volle -- letzteres
    ergaebe immer 1. Masters' Schwellen: >= 0,5 brauchbar, < 0,5 verdaechtig, < 0,1 kritisch.

    Warnsignal: aendert sich das Ergebnis bei leicht anderer Bin-Zahl stark, stimmt etwas mit
    dem Indikator nicht -- dann Histogramm ansehen.

    Die beiden Epsilons stammen aus dem Original: -1e-10 im Zaehler verhindert, dass der
    Maximalwert in einen nicht existierenden Bin hinter dem letzten faellt, +1e-60 im Nenner
    die Division durch null, falls alle Werte gleich sind."""
    a = np.asarray(x, dtype=float)
    if nbins < 2:
        raise ValueError("nbins muss mindestens 2 sein")
    lo, hi = float(a.min()), float(a.max())
    factor = (nbins - 1e-10) / (hi - lo + 1e-60)
    counts = np.bincount(((a - lo) * factor).astype(int), minlength=nbins)
    p = counts[counts > 0] / a.size
    return float(-(p * np.log(p)).sum() / math.log(nbins))


def clean_tails(raw: Sequence[float], tail_frac: float = 0.05) -> np.ndarray:
    """Monotones Tail-Cleaning: nur die Enden werden komprimiert, der Innenbereich bleibt
    BIT-IDENTISCH.

    "Tail" wird datengetrieben definiert -- gesucht wird das zusammenhaengende Fenster mit
    der Abdeckung (1 - 2*tail_frac), das die KLEINSTE Spannweite hat; alles ausserhalb ist
    Tail. Das ist robuster als feste Perzentile.

    Truncation (Kappen auf einen Grenzwert) waere die naheliegende Alternative und ist
    ausdruecklich schlecht: sie zerstoert die Ordnung und damit die Eigenschaft, dass eine
    trennende Schwelle vor der Transformation auch danach existiert.

    Wirkung im Buch: hebt den RawJump-Indikator von relativer Entropie 0,484 auf 0,958,
    ohne sonst irgendetwas zu aendern."""
    x = np.asarray(raw, dtype=float).copy()
    n = x.size
    if not 0.0 < tail_frac < 0.5:
        raise ValueError("tail_frac muss in (0, 0.5) liegen")
    cover = 1.0 - 2.0 * tail_frac
    w = np.sort(x)

    istop = min(int(cover * (n + 1)) - 1, n - 1)
    istop = max(istop, 0)
    spans = w[istop:] - w[:n - istop]          # alle Fensterpositionen auf einmal
    a = int(np.argmin(spans))
    minval, maxval = w[a], w[a + istop]
    if maxval <= minval:                        # seltener Pathologiefall
        maxval *= 1.0 + 1e-10
        minval *= 1.0 - 1e-10

    limit = (maxval - minval) * (1.0 - cover)   # Heuristik des Autors
    scale = -1.0 / (maxval - minval)
    lo, hi = x < minval, x > maxval
    x[lo] = minval - limit * (1.0 - np.exp(scale * (minval - x[lo])))
    x[hi] = maxval + limit * (1.0 - np.exp(scale * (x[hi] - maxval)))
    return x


GAP_SIZES = (1, 2, 4, 8, 16, 32, 64, 128, 256, 512)


def gap_analyze(x: Sequence[float], thresh: float,
                gap_sizes: Sequence[int] = GAP_SIZES) -> list[int]:
    """STATN-Gap-Analyse: wie lange bleibt der Indikator am Stueck auf derselben Seite von
    `thresh` (ueblich: dem Median)? Zaehlt die Lauflaengen in Bins 1,2,4,...,512,>512.

    Viele lange Laeufe = gefaehrliches langsames Wandern. Masters' Befund fuer OEX: die rohe
    Volatilitaet blieb sechsmal ueber 512 Bars (mehr als vier Jahre) auf derselben
    Median-Seite -- klassische Stationaritaetstests dagegen sind sinnlos, weil sie immer
    hochsignifikant ausfallen.

    Gegenmittel (in aufsteigender Haerte): gegen den eigenen Lag oszillieren, kurzer minus
    langer Lookback, rollendes Fenster normieren."""
    a = np.asarray(x, dtype=float)
    counts = [0] * (len(gap_sizes) + 1)
    count = 1
    above = bool(a[0] >= thresh)
    for i in range(1, a.size + 1):
        new_above = (not above) if i == a.size else bool(a[i] >= thresh)  # Array-Ende = Wechsel
        if new_above == above:
            count += 1
        else:
            j = next((j for j, g in enumerate(gap_sizes) if count <= g), len(gap_sizes))
            counts[j] += 1
            count, above = 1, new_above
    return counts


# --------------------------------------------------------------------------------------
# Kapitel 6 -- Kennzahlen
# --------------------------------------------------------------------------------------

def profit_factor(returns: Sequence[float]) -> float:
    """Summe der Gewinne / Summe der Verluste -- auf BAR-Basis zu rechnen, nicht auf
    Trade-Basis. Masters' Beispiel: zwei Trades mit je +101/-100 Punkten intern (netto je +1)
    ergeben trade-basiert einen Profit Factor von unendlich und bar-basiert 1,01."""
    r = np.asarray(returns, dtype=float)
    return float((r[r > 0].sum() + 1e-60) / (-r[r < 0].sum() + 1e-60))


def log_profit_factor(returns: Sequence[float]) -> float:
    """log(Profit Factor). Fuer JEDEN Bootstrap zwingend statt des rohen Profit Factors:
    dessen rechtes Verteilungsende ist so schwer (winziger Nenner -> Explosion), dass die
    Konfidenzgrenzen sonst versagen. Masters' BOOT_RATIO-Test: bei 50 Trades und 2,5 %
    Sollfehlerrate wird die Pivot-Untergrenze NIE verletzt (also wertlos), waehrend die
    Obergrenze fast viermal so oft verletzt wird wie erlaubt."""
    return float(math.log(profit_factor(returns)))


def sharpe_ratio(returns: Sequence[float]) -> float:
    """Roher Sharpe (Mittel / Standardabweichung), ohne risikofreien Zins -- wie im Buch."""
    r = np.asarray(returns, dtype=float)
    sd = r.std(ddof=1)
    return float(r.mean() / (sd + 1e-60))


def lower_bound_t(returns: Sequence[float], p: float = 0.95) -> tuple[float, float, float, float]:
    """(mean, t, p_value, lower_bound) nach den Gleichungen 6-1 bis 6-4 und 6-9.

    Praktische Abkuerzung, die Masters betont: die Nullhypothese "wahrer Mittelwert <= 0"
    wird GENAU DANN auf dem Niveau 1-p verworfen, wenn lower_bound > 0. Ein separater
    Hypothesentest ist ueberfluessig.

    VORBEDINGUNG: vorher ein Histogramm der Renditen ansehen. Der t-Test ist robust gegen
    moderate Schiefe und maessig schwere Enden, aber EIN einziger wilder Ausreisser macht ihn
    wertlos -- dann lower_bound_bca() nehmen."""
    r = np.asarray(returns, dtype=float)
    n = r.size
    if n < 2:
        raise ValueError("mindestens 2 Renditen noetig")
    mean = float(r.mean())
    sd = float(r.std(ddof=1))
    t = math.sqrt(n) * mean / (sd + 1e-60)                      # (6-3)
    pval = float(1.0 - stats.t.cdf(t, df=n - 1))                # (6-4)
    lower = mean - sd * float(stats.t.ppf(p, df=n - 1)) / math.sqrt(n)   # (6-9)
    return mean, t, pval, lower


def lower_bound_bca(returns: Sequence[float],
                    statistic: Callable[[np.ndarray], float] = np.mean,
                    p: float = 0.95, n_resamples: int = 10_000,
                    rng: np.random.Generator | None = None) -> float:
    """Einseitige BCa-Bootstrap-Untergrenze (Gleichungen 6-10 bis 6-13), delegiert an
    scipy.stats.bootstrap -- Masters' bevorzugtes Verfahren, weil es Bias UND
    Verteilungsschiefe korrigiert.

    `n_resamples=10_000` nennt er als Minimum fuer ernsthafte Tests.

    Bei Verhaeltniskennzahlen `statistic=log_profit_factor` uebergeben, nicht
    `profit_factor` -- siehe dort."""
    r = np.asarray(returns, dtype=float)
    res = stats.bootstrap(
        (r,), lambda a, axis=-1: np.apply_along_axis(statistic, axis, a),
        method="BCa", confidence_level=p, alternative="greater",
        n_resamples=n_resamples, random_state=rng,
    )
    return float(res.confidence_interval.low)


# --------------------------------------------------------------------------------------
# Kapitel 6 -- Grenzen fuer Einzelrenditen
# --------------------------------------------------------------------------------------

def find_quantile(sorted_data: np.ndarray, frac: float) -> float:
    """Unverzerrter Quantilschaetzer k = int(frac*(n+1)) - 1 auf aufsteigend sortierten Daten."""
    k = int(frac * (sorted_data.size + 1)) - 1
    return float(sorted_data[max(k, 0)])


def return_bound(returns: Sequence[float], p: float, upper: bool = False,
                 unbiased: bool = True) -> float:
    """Empirische Quantilgrenze fuer EINZELNE kuenftige Renditen (nicht fuer deren
    Mittelwert -- dafuer lower_bound_t/lower_bound_bca).

    Gedacht fuer die Live-Ueberwachung: faellt die Monats-/Quartalsrendite oefter als mit
    Wahrscheinlichkeit p unter diese Grenze, degradiert das System.

    Fuer die OBERgrenze ein grosses p waehlen (z.B. 0,4): man erwartet, dass 40 % der
    kuenftigen Renditen darueber liegen. Bleiben die guten Trades aus, ist das genauso ein
    Degradationssignal wie zu viele schlechte.

    Datenbedarf: mindestens ~100 Renditen, besser mehrere hundert."""
    s = np.sort(np.asarray(returns, dtype=float))
    n = s.size
    m = max(int((n + 1) * p) if unbiased else int(n * p), 1)
    return float(s[n - m] if upper else s[m - 1])


def orderstat_tail(n: int, q: float, m: int) -> float:
    """P{ m-kleinster von n Werten liegt UEBER dem q-Quantil } = 1 - I_q(m, n-m+1).

    Damit quantifiziert man, wie sehr man der eigenen Grenze trauen darf. Zwei Richtungen:
      pessimistisch (q > p): Grenze zu hoch -> wird oefter verletzt als gedacht
      optimistisch  (q < p): Grenze zu tief -> echte Degradation wird NICHT erkannt,
                             dafuer  1 - orderstat_tail(...)  rechnen."""
    return float(1.0 - betainc(m, n - m + 1, q))


def quantile_conf(n: int, m: int, conf: float) -> float:
    """Umkehrung von orderstat_tail(): zu welcher Fehlerrate q gehoert diese Konfidenz?"""
    return float(stats.beta.ppf(1.0 - conf, m, n - m + 1))


# --------------------------------------------------------------------------------------
# Kapitel 6 -- Drawdown
# --------------------------------------------------------------------------------------

def drawdown(returns: Sequence[float]) -> float:
    """Groesster Rueckgang der kumulierten Log-Rendite vom laufenden Hoch.

    Bewusst ABSOLUT statt "Prozent vom Maximalkapital": das vermeidet die Willkuer eines
    Startkapitals, wirkt ueber das Zeitintervall gleichfoermig und funktioniert auch bei
    negativem Eigenkapital (gehebelte Futures)."""
    r = np.asarray(returns, dtype=float)
    if r.size == 0:
        return 0.0
    cum = np.cumsum(r)
    return float(np.max(np.maximum.accumulate(cum) - cum))


def dd_to_pct(dd: float) -> float:
    """Log-Drawdown -> Prozent Kapitalverlust: 100*(1-exp(-dd)).
    Start 1, Peak 3, Tal 2 -> dd = log3-log2 -> 33,3 %."""
    return 100.0 * (1.0 - math.exp(-dd))


def drawdown_quantiles(changes: np.ndarray, n_trades: int, nboot: int,
                       rng: np.random.Generator,
                       quantiles: Sequence[float] = (0.999, 0.99, 0.95, 0.90)) -> list[float]:
    """Mehrere Drawdown-Quantile in EINEM Durchlauf -- das Sortieren ist der teure Teil,
    zusaetzliche Quantile kosten praktisch nichts."""
    work = np.empty(nboot)
    for i in range(nboot):
        work[i] = drawdown(rng.choice(changes, size=n_trades, replace=True))
    work.sort()
    return [find_quantile(work, q) for q in quantiles]


def drawdown_bound_naive(oos_returns: Sequence[float], n_trades: int, dd_conf: float = 0.95,
                         nboot: int = 5_000,
                         rng: np.random.Generator | None = None) -> float:
    """Der von Masters als "incorrect" bezeichnete einfache Bootstrap.

    UNTERSCHAETZT das Risiko in JEDER getesteten Konstellation -- nie konservativ. Bei 63
    OOS-Renditen und dd_conf=0,999 um Faktor 13,65. Grund: er erfasst Zusammensetzung und
    Reihenfolge kuenftiger Trades, ignoriert aber, dass die OOS-Stichprobe SELBST eine
    Zufallsziehung ist (und optimistische Stichproben schaden mehr, als pessimistische
    nuetzen).

    Vertretbar nur bei grosser OOS-Stichprobe UND moderatem dd_conf (bei 2520 Renditen und
    dd_conf=0,9 liegt der Faktor bei 1,04) -- dann aber sehr nuetzlich, weil er
    Groessenordnungen schneller ist als drawdown_bound() und in eine Optimierungsschleife
    passt.

    ACHTUNG: das ist exakt das Verfahren, das algo/validate.py heute nutzt."""
    rng = rng or np.random.default_rng()
    r = np.asarray(oos_returns, dtype=float)
    return drawdown_quantiles(r, n_trades, nboot, rng, (dd_conf,))[0]


def drawdown_bound(oos_returns: Sequence[float], n_trades: int, dd_conf: float = 0.95,
                   bound_conf: float = 0.8, outer: int = 500, inner: int = 1_000,
                   rng: np.random.Generator | None = None) -> float:
    """Korrekter Doppel-Bootstrap.

    Zwei Konfidenzen, die man auseinanderhalten muss:
      dd_conf     Wahrscheinlichkeit, dass ein kuenftiger Drawdown die Grenze NICHT
                  ueberschreitet (0,9 / 0,95 / 0,99 / 0,999)
      bound_conf  Konfidenz, dass die BERECHNETE Grenze mindestens so gross ist wie die
                  wahre, unbekannte dd_conf-Grenze (0,7 Routine, 0,9+ bei Extremen)

    Also: "mit bound_conf Sicherheit liegt die Grenze, die zu dd_conf nicht ueberschritten
    wird, bei hoechstens X." Eine Grenze fuer eine Grenze.

    Die Grenze gilt fuer EINEN im Voraus festgelegten Zeitraum von `n_trades` Bars (typisch
    252 = kommendes Jahr) und nur fuer Equity-Aenderungen innerhalb dieses Zeitraums -- nicht
    fuer "jemals" und nicht fuer die Fortsetzung eines laufenden Drawdowns.

    Formal ist nur die AEUSSERE Schleife ein Bootstrap (Perzentil-Methode); die innere
    schaetzt lediglich die Statistik -- das gewuenschte Quantil -- aus der empirischen
    Verteilung der aeusseren Stichprobe.

    Kosten: outer*inner Drawdown-Berechnungen. Masters nutzt 5000 x 10000; die Defaults hier
    sind bewusst kleiner (interaktiv nutzbar), fuer belastbare Zahlen hochsetzen."""
    rng = rng or np.random.default_rng()
    r = np.asarray(oos_returns, dtype=float)
    n = r.size
    outer_q = np.empty(outer)
    for b in range(outer):
        sample = rng.choice(r, size=n, replace=True)          # Faktor 1: Stichprobenunsicherheit
        outer_q[b] = drawdown_quantiles(sample, n_trades, inner, rng, (dd_conf,))[0]
    outer_q.sort()
    return find_quantile(outer_q, bound_conf)


# --------------------------------------------------------------------------------------
# Kapitel 7 -- Permutation
# --------------------------------------------------------------------------------------

def permute_prices(log_prices: Sequence[float], rng: np.random.Generator,
                   offset: int = 1) -> np.ndarray:
    """Permutiert eine einfache Log-Preisreihe ab `offset`.

    Preise duerfen nicht direkt getauscht werden (eine Aktie, die bei 20 startet und bei 800
    endet, wuerde unsinnig) -- also in Aenderungen zerlegen, mischen, neu aufbauen. Und weil
    Differenzen bei hohen Kursen groesser sind als bei niedrigen, wird auf LOG-Preisen
    gerechnet.

    Der Fall bei offset-1 ist die unveraenderte "Basis"; Start- und Endpreis bleiben damit
    exakt erhalten und der GESAMTTREND bleibt konstant. Genau darauf beruht
    partition_return()."""
    p = np.asarray(log_prices, dtype=float).copy()
    if not 0 < offset < p.size:
        raise ValueError("offset muss in (0, len) liegen")
    changes = np.diff(p[offset - 1:])
    rng.shuffle(changes)
    p[offset:] = p[offset - 1] + np.cumsum(changes)
    return p


def permute_bars(o: np.ndarray, h: np.ndarray, l: np.ndarray, c: np.ndarray,
                 rng: np.random.Generator,
                 preserve_oo: bool = False) -> tuple[np.ndarray, ...]:
    """Permutiert OHLC-Bars (LOG-Preise). Bar 0 bleibt unveraendert.

    Vier Bedingungen sind einzuhalten: Open/Close nie ausserhalb High/Low; Verteilung von
    High/Low relativ zum Open erhalten; Verteilung der Open-zu-Close-Aenderungen erhalten;
    Verteilung der Inter-Bar-Gaps erhalten.

    Die ersten drei loest man, indem alles relativ zum Open ausgedrueckt und das Tripel
    (High, Low, Close) ZUSAMMENGEHALTEN wird. Punkt 4 ist die Falle: permutiert man naiv die
    Open-zu-Open-Aenderungen, trifft regelmaessig ein grosser Open-Sprung auf eine Bar mit
    grossem Open-zu-Close-Verfall -- Bar schliesst bei 98, naechstes Open bei 102, ein
    4-Punkte-Gap, das real nahezu unmoeglich ist. Deshalb werden Intra-Bar- und Inter-Bar-
    Aenderungen GETRENNT gemischt.

    preserve_oo: nimmt die erste Close-zu-Open- und die letzte Open-zu-Close-Aenderung von
    der Permutation aus. Noetig, wenn Trades konservativ auf dem Open der Folgebar ausgefuehrt
    werden UND partition_return() genutzt wird -- nur so bleibt der so definierte Gesamttrend
    ueber alle Permutationen identisch."""
    o, h, l, c = (np.asarray(a, dtype=float).copy() for a in (o, h, l, c))
    rel_open = o[1:] - c[:-1]        # Gap: Close der Vorbar -> Open
    rel_high = h[1:] - o[1:]         # Intrabar, relativ zum Open
    rel_low = l[1:] - o[1:]
    rel_close = c[1:] - o[1:]

    off = 1 if preserve_oo else 0
    n = rel_open.size
    tail = n - off if preserve_oo else n

    gap = rel_open[off:].copy()
    rng.shuffle(gap)
    rel_open[off:] = gap

    idx = rng.permutation(tail)      # EINE Permutation fuer das ganze Tripel
    rel_high[:tail] = rel_high[:tail][idx]
    rel_low[:tail] = rel_low[:tail][idx]
    rel_close[:tail] = rel_close[:tail][idx]

    for i in range(1, o.size):       # sequenziell neu aufbauen
        o[i] = c[i - 1] + rel_open[i - 1]
        h[i] = o[i] + rel_high[i - 1]
        l[i] = o[i] + rel_low[i - 1]
        c[i] = o[i] + rel_close[i - 1]
    return o, h, l, c


def permute_multi(data: np.ndarray, rng: np.random.Generator, offset: int = 1) -> np.ndarray:
    """Permutiert mehrere Maerkte (Zeilen = Maerkte, Spalten = Bars, LOG-Preise) mit
    DERSELBEN Permutation.

    Sonst entstehen Konstellationen -- hochkorrelierte Maerkte laufen gegeneinander --, die
    es real nicht gaebe, und die Grundannahme "jede Permutation ist unter H0 gleich
    wahrscheinlich" bricht.

    Werden mehrere Abschnitte getrennt permutiert (Nested Walkforward: erster Trainingsblock,
    erster Level-1-OOS-Block, Voll-OOS-Block), duerfen sie sich NICHT ueberlappen -- der
    Basis-Fall bei offset-1 gehoert mit zum belegten Bereich.

    Voraussetzung: jeder Markt hat zu jedem Datum einen Preis; fehlende Tage muessen vorher
    bei ALLEN Maerkten entfernt werden."""
    d = np.asarray(data, dtype=float).copy()
    nmkt, nc = d.shape
    if not 0 < offset < nc:
        raise ValueError("offset muss in (0, ncols) liegen")
    changes = np.diff(d[:, offset - 1:], axis=1)
    perm = rng.permutation(changes.shape[1])
    changes = changes[:, perm]
    d[:, offset:] = d[:, offset - 1][:, None] + np.cumsum(changes, axis=1)
    return d


# --------------------------------------------------------------------------------------
# Kapitel 5 -- CSCV
# --------------------------------------------------------------------------------------

def cscv(returns: np.ndarray, n_blocks: int,
         criter: Callable[[np.ndarray], float]) -> float:
    """Dominanz-Test: Wahrscheinlichkeit, dass der IS-beste Parametersatz OOS UNTER dem
    Median seiner Konkurrenten landet. Klein ist gut; ~0,5 bedeutet, dass das Training
    keinen Wert schafft.

    `returns`: Matrix (n_systems x n_cases), eine Zeile je Kandidat, eine Spalte je Bar.
    `n_blocks`: gerade Zahl (10-12 in Masters' Beispielen). Es werden alle
    C(n_blocks, n_blocks/2) Aufteilungen durchgespielt -- 252 bei 10, 924 bei 12 Bloecken.

    Voraussetzungen:
      * partitioniert werden BAR-Renditen, nie Preise (Rekombination von Preisbloecken
        erzeugt Sprungstellen)
      * die Kandidaten muessen UNABHAENGIG voneinander entstanden sein -- Grid Search oder
        Zufallsparameter, KEIN Hill-Climbing und keine genetische Optimierung
      * Ein-Bar-Lookahead

    Das Ergebnis ist vollstaendig relativ zum Konkurrentenfeld: verwaessert man es mit
    offensichtlich unsinnigen Parametersaetzen, bekommt schon ein mittelmaessiges System
    einen unverdient guten Wert; verengt man es auf lauter aehnlich gute, dominiert keiner.
    Der Parameterraum muss gruendlich, aber realistisch abgedeckt sein."""
    from itertools import combinations

    r = np.asarray(returns, dtype=float)
    n_systems, ncases = r.shape
    n_blocks = (n_blocks // 2) * 2
    if n_blocks < 2:
        raise ValueError("n_blocks muss >= 2 und gerade sein")

    bounds, start = [], 0
    for i in range(n_blocks):                       # gleich oder fast gleich grosse Bloecke
        length = (ncases - start) // (n_blocks - i)
        bounds.append((start, start + length))
        start += length

    nless = ncombo = 0
    all_blocks = range(n_blocks)
    for train_idx in combinations(all_blocks, n_blocks // 2):
        train_set = set(train_idx)
        train_cols = np.concatenate([np.arange(*bounds[b]) for b in train_idx])
        test_cols = np.concatenate([np.arange(*bounds[b]) for b in all_blocks
                                    if b not in train_set])
        is_crit = np.array([criter(r[s, train_cols]) for s in range(n_systems)])
        oos_crit = np.array([criter(r[s, test_cols]) for s in range(n_systems)])
        ibest = int(np.argmax(is_crit))
        rel_rank = int(np.sum(oos_crit[ibest] >= oos_crit)) / (n_systems + 1)
        if rel_rank <= 0.5:
            nless += 1
        ncombo += 1
    return nless / ncombo


# --------------------------------------------------------------------------------------
# Kapitel 4 / 7 -- Bias-Schaetzung und Zerlegung
# --------------------------------------------------------------------------------------

def stoc_bias(returns_matrix: np.ndarray) -> tuple[float, float, float]:
    """Billige Trainings-Bias-Schaetzung (StocBias) aus einer Menge ZUFAELLIG erzeugter
    Kandidaten. Liefert (IS_return, OOS_return, bias).

    `returns_matrix`: Zeile je Kandidat, Spalte je Bar.

    ZULAESSIGKEIT: nur zufaellig oder per Grid gezogene Parametersaetze. Keine Mutations-/
    Crossover-Kinder -- die stammen aus gerichteter Suche und zerstoeren das Verfahren.

    Idee: fuer JEDE Bar wird sie gedanklich als einzige OOS-Bar ausgelassen; der Kandidat mit
    dem hoechsten Return ueber alle ANDEREN Bars gewinnt, und sein Return auf der
    ausgelassenen Bar ist der ehrliche OOS-Wert. Weil IS_i = Gesamtsumme - return_i gilt,
    kostet das kaum mehr als eine Summe je Kandidat.

    SELBSTTEST: liegt der zurueckgegebene IS_return deutlich unter dem Optimum, das der echte
    Optimierer gefunden hat, waren es zu wenige Kandidaten -- dann ist die Schaetzung
    unbrauchbar. Masters nutzt mehrere tausend."""
    m = np.asarray(returns_matrix, dtype=float)
    if m.ndim != 2:
        raise ValueError("returns_matrix muss 2-dimensional sein (Kandidaten x Bars)")
    n = m.shape[1]
    is_all = m.sum(axis=1, keepdims=True) - m       # IS-Return je (Kandidat, ausgelassener Bar)
    best = np.argmax(is_all, axis=0)                # bester Kandidat je ausgelassener Bar
    cols = np.arange(n)
    is_return = float(is_all[best, cols].sum() / (n - 1))   # kommensurabel: Summe ueber n-1 Bars
    oos_return = float(m[best, cols].sum())
    return is_return, oos_return, is_return - oos_return


@dataclass(frozen=True)
class Partition:
    """Zerlegung nach Gleichung 7-2: TotalReturn = Skill + Trend + TrainingBias."""
    total_return: float
    trend: float
    training_bias: float
    unbiased_return: float
    skill: float
    p_value: float


def partition_return(original_return: float, original_nlong: int, original_nshort: int,
                     trend_per_return: float,
                     permuted: Sequence[tuple[float, int, int]]) -> Partition:
    """Zerlegt das Backtest-Ergebnis in Koennen, Markttrend und gelerntes Rauschen.

        (7-1)  Trend          = (NumLong - NumShort) * TrendPerReturn
        (7-2)  TotalReturn    = Skill + Trend + TrainingBias
        (7-3)  TrainingBias   = PermutedTotalReturn - Trend        (je Permutation)
        (7-4)  UnbiasedReturn = TotalReturn - mean(TrainingBias)
        (7-5)  Skill          = UnbiasedReturn - Trend(original)

    `trend_per_return` = (log(Endpreis) - log(Startpreis)) / Anzahl Preisaenderungen,
    gemessen ab dem ersten Bar, an dem eine Entscheidung moeglich ist.
    `permuted` = je Permutation (Return, n_long, n_short) aus einer VOLLEN Reoptimierung.

    In der Permutation ist Skill per Konstruktion null (die Muster sind zerstoert) und
    trend_per_return unveraendert (dieselben Aenderungen in anderer Reihenfolge) -- was ueber
    den Trendanteil hinausgeht, muss also Training Bias sein.

    Zwei Zahlen mit unterschiedlicher Aussage: `unbiased_return` ENTHAELT den Trendanteil
    (richtig, wenn man Trendmitnahme fuer legitim haelt), `skill` ist die strengere Zahl --
    um wie viel schlaegt das System einen Muenzwurf mit derselben Long/Short-Bilanz?"""
    if not permuted:
        raise ValueError("mindestens eine Permutation noetig")
    orig_trend = (original_nlong - original_nshort) * trend_per_return          # (7-1)
    biases = [ret - (nl - ns) * trend_per_return for ret, nl, ns in permuted]   # (7-3)
    mean_bias = float(np.mean(biases))
    unbiased = original_return - mean_bias                                      # (7-4)
    count = 1 + sum(1 for ret, _, _ in permuted if ret >= original_return)
    return Partition(
        total_return=original_return,
        trend=orig_trend,
        training_bias=mean_bias,
        unbiased_return=unbiased,
        skill=unbiased - orig_trend,                                            # (7-5)
        p_value=count / (len(permuted) + 1),
    )


# --------------------------------------------------------------------------------------
# Bruecke zur bestehenden algo/-Infrastruktur
# --------------------------------------------------------------------------------------

def bar_returns_from_trades(trades, bars, only_open: bool = True) -> np.ndarray:
    """Rechnet `stats._trades` der `backtesting`-Bibliothek in BAR-Renditen um.

    Loest den Kernkritikpunkt aus Kapitel 6: die Lib liefert nur Trade-Renditen, und darauf
    berechnete Kennzahlen sind systematisch extremer als bar-basierte (Profit Factor kann
    unendlich statt 1,01 sein). Erst mit Bar-Renditen sind lower_bound_t/lower_bound_bca,
    return_bound und cscv sinnvoll anwendbar.

    `trades` braucht die Spalten 'EntryBar', 'ExitBar', 'Size' (Vorzeichen = Richtung),
    `bars` eine Spalte 'Close' in derselben Reihenfolge, die an Backtest() ging.

    Bewertet Mark-to-Market Close-zu-Close, solange eine Position offen ist.
    only_open=True liefert nur Bars mit offener Position (Masters' Favorit), False alle Bars
    inklusive Nullrenditen -- letzteres macht Mittelwert und Sharpe empfindlich dafuer, wie
    oft das System ueberhaupt im Markt ist."""
    close = np.asarray(bars["Close"], dtype=float)
    pos = np.zeros(close.size)
    for entry, exit_, size in zip(trades["EntryBar"], trades["ExitBar"], trades["Size"]):
        pos[int(entry):int(exit_)] = np.sign(size)
    logret = np.diff(np.log(close))
    ret = pos[:-1] * logret
    return ret[pos[:-1] != 0] if only_open else ret


# --------------------------------------------------------------------------------------

def demo() -> None:
    """Selbstcheck. Prueft die Eigenschaften, die den Verfahren ihren Sinn geben --
    nicht nur, dass sie durchlaufen."""
    rng = np.random.default_rng(20260808)

    # --- Guard Buffer: die Formel, um die es geht -------------------------------------
    assert guard_buffer(50, 80) == 49          # Buchbeispiel: min(50,80)-1
    assert guard_buffer(100, 1) == 0           # Lookahead 1 -> kein Puffer noetig
    assert guard_buffer(3, 10) == 2

    # --- Walk-Forward: Trainingsblock endet omit Faelle vor dem Test ------------------
    folds = list(walkforward(n=20, ntrain=10, ntest=1, omit=3, extra=2))
    tr, te = folds[0]
    assert (tr.start, tr.stop) == (0, 7) and (te.start, te.stop) == (10, 11)
    assert folds[1][1].start == 13             # ntest + extra = 3 weiter
    assert all(t.stop <= 20 for _, t in folds)

    # --- Entropie: Gleichverteilung ~1, Konstante ~0 ----------------------------------
    assert entropy(np.linspace(0, 1, 10_000)) > 0.99
    assert entropy(np.concatenate([np.zeros(999), [1.0]])) < 0.05

    # --- Tail-Cleaning: Innenbereich unveraendert, monoton, Entropie steigt -----------
    raw = np.concatenate([rng.normal(size=1000), [50.0, -50.0]])
    cleaned = clean_tails(raw, 0.05)
    interior = (raw > np.quantile(raw, 0.20)) & (raw < np.quantile(raw, 0.80))
    assert np.allclose(raw[interior], cleaned[interior])
    assert np.all(np.diff(cleaned[np.argsort(raw)]) >= -1e-12)      # ordnungserhaltend
    assert entropy(cleaned) > entropy(raw)

    # --- Gap-Analyse: 6 Wechsel bei alternierenden Bloecken der Laenge 3 --------------
    counts = gap_analyze(np.array([1, 1, 1, -1, -1, -1] * 3), 0.0)
    assert sum(counts) == 6 and counts[2] == 6                      # Bin "4" fasst Laenge 3

    # --- Drawdown -------------------------------------------------------------------
    assert math.isclose(drawdown([1.0, -0.5, -0.25, 2.0]), 0.75)
    assert math.isclose(dd_to_pct(math.log(3) - math.log(2)), 100 * (1 - 2 / 3))

    # --- Der naive Bootstrap unterschaetzt gegenueber dem Doppel-Bootstrap ------------
    oos = rng.normal(0.001, 0.01, size=63)
    naive = drawdown_bound_naive(oos, n_trades=63, dd_conf=0.99, nboot=400, rng=rng)
    correct = drawdown_bound(oos, n_trades=63, dd_conf=0.99, bound_conf=0.8,
                             outer=60, inner=200, rng=rng)
    assert correct > naive, f"Doppel-Bootstrap muss konservativer sein ({correct} vs {naive})"

    # --- t-Grenze: Aequivalenz Hypothesentest <-> Vorzeichen der Untergrenze ----------
    good = rng.normal(0.02, 0.01, size=200)
    mean, t, pval, lower = lower_bound_t(good, p=0.95)
    assert (pval < 0.05) == (lower > 0)
    _, _, pval0, lower0 = lower_bound_t(rng.normal(0.0, 0.01, size=200), p=0.95)
    assert (pval0 < 0.05) == (lower0 > 0)
    assert lower_bound_bca(good, p=0.95, n_resamples=999, rng=rng) < mean

    # --- Profit Factor: Masters' Trade-vs-Bar-Beispiel --------------------------------
    per_bar = [101.0, -100.0, 101.0, -100.0]
    assert math.isclose(profit_factor(per_bar), 1.01, rel_tol=1e-6)
    assert profit_factor([1.0, 1.0]) > 1e50                          # trade-basiert: "unendlich"

    # --- Quantilgrenzen ---------------------------------------------------------------
    sample = np.arange(1.0, 201.0)
    assert return_bound(sample, 0.1) == 20.0                         # m = (n+1)*p = 20
    assert return_bound(sample, 0.1, upper=True) == 181.0
    assert 0.0 < orderstat_tail(200, 0.12, 20) < 1.0
    assert quantile_conf(200, 20, 0.05) > 0.1                        # pessimistisches q > p

    # --- Permutation: Preisreihe ------------------------------------------------------
    prices = np.log(np.cumprod(1 + rng.normal(0.0005, 0.01, size=500)) * 100)
    perm = permute_prices(prices, rng, offset=1)
    assert math.isclose(perm[0], prices[0]) and math.isclose(perm[-1], prices[-1])
    assert np.allclose(np.sort(np.diff(perm)), np.sort(np.diff(prices)))
    assert not np.allclose(perm, prices)

    # --- Permutation: Bars bleiben strukturell gueltig ---------------------------------
    o = prices[:-1]
    c = prices[1:]
    h = np.maximum(o, c) + 0.001
    l = np.minimum(o, c) - 0.001
    po, ph, pl, pc = permute_bars(o, h, l, c, rng)
    assert np.all(ph >= np.maximum(po, pc) - 1e-12)                  # Bedingung 1
    assert np.all(pl <= np.minimum(po, pc) + 1e-12)
    assert np.allclose(np.sort(ph - po), np.sort(h - o))             # Bedingung 2
    assert np.allclose(np.sort(pc - po), np.sort(c - o))             # Bedingung 3
    assert np.allclose(np.sort(po[1:] - pc[:-1]), np.sort(o[1:] - c[:-1]))   # Bedingung 4
    assert math.isclose(po[0], o[0]) and math.isclose(pc[-1], c[-1])

    # --- Permutation: mehrere Maerkte identisch gemischt -> Korrelation bleibt ---------
    a = np.log(np.cumprod(1 + rng.normal(0, 0.01, size=400)) * 100)
    b = a + rng.normal(0, 0.0005, size=400)                          # fast perfekt korreliert
    pm = permute_multi(np.vstack([a, b]), rng, offset=1)
    corr_before = np.corrcoef(np.diff(a), np.diff(b))[0, 1]
    corr_after = np.corrcoef(np.diff(pm[0]), np.diff(pm[1]))[0, 1]
    assert abs(corr_after - corr_before) < 0.02, (corr_before, corr_after)

    # --- CSCV: ein echt ueberlegenes System muss dominieren ---------------------------
    n_cases = 240
    edge = np.vstack([
        rng.normal(0.004, 0.01, size=n_cases),                       # echter Edge
        *[rng.normal(0.0, 0.01, size=n_cases) for _ in range(7)],    # wertlos
    ])
    assert cscv(edge, 8, np.mean) < 0.10
    noise = rng.normal(0.0, 0.01, size=(8, n_cases))                 # alle wertlos
    assert cscv(noise, 8, np.mean) > 0.20

    # --- StocBias: bei echtem Bias positiv, Selbsttest-Groesse plausibel ---------------
    cands = rng.normal(0.0, 0.01, size=(400, 60))                    # nur Rauschen
    is_ret, oos_ret, bias = stoc_bias(cands)
    assert bias > 0 and is_ret > oos_ret

    # --- Partitionierung: die Identitaet aus (7-2) muss exakt aufgehen -----------------
    part = partition_return(
        original_return=2.6710, original_nlong=600, original_nshort=400,
        trend_per_return=0.0005,
        permuted=[(0.4, 550, 450), (0.6, 520, 480), (0.5, 600, 400)],
    )
    assert math.isclose(part.trend, (600 - 400) * 0.0005)
    assert math.isclose(part.total_return,
                        part.skill + part.trend + part.training_bias, rel_tol=1e-12)
    assert 0.0 < part.p_value <= 1.0

    print("masters.py: alle Selbstchecks bestanden")


if __name__ == "__main__":
    demo()
