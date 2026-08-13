"""Self-check: FVG-Grenzen muessen die volle VII einbeziehen (Close/Open), nicht nur
den Wick -- siehe wiki/concepts/Volume Imbalance (VII).md. Aufruf: python tools/test_fvg_vii.py
"""
from datetime import datetime

from analyze_ohlc import Bar, fvgs, viis

T = datetime(2026, 1, 1, 9, 0)


def bar(o, h, l, c):
    return Bar(t=T, o=o, h=h, l=l, c=c)


def test_bisi_uses_vii_edges_not_wicks():
    # Candle 1 hat einen Wick UEBER dem Close (H=29827.00 > C=29826.00) -- ohne Fix wuerde
    # dieser Wick als Grenze genutzt statt des VII-Rands (Close1).
    c1 = bar(29820.00, 29827.00, 29819.00, 29826.00)
    # VII #1: Open2 (29826.50) > Close1 (29826.00)
    c2 = bar(29826.50, 29830.50, 29826.00, 29830.00)
    # VII #2: Open3 (29830.75) > Close2 (29830.00); Candle 3 hat Wick UNTER dem Open
    # (L=29829.50 < O=29830.75) -- ohne Fix wuerde dieser Wick genutzt statt Open3.
    c3 = bar(29830.75, 29833.50, 29829.50, 29833.25)

    out = fvgs([c1, c2, c3])
    assert len(out) == 1, out
    g = out[0]
    assert g["side"] == "bullish"
    assert g["lo"] == 29826.00, g  # Close Candle1, nicht Wick-High 29827.00
    assert g["hi"] == 29830.75, g  # Open Candle3, nicht Wick-Low 29829.50


def test_sibi_uses_vii_edges_not_wicks():
    c1 = bar(29830.00, 29831.00, 29823.00, 29826.00)
    # VII #1: Open2 (29825.50) < Close1 (29826.00)
    c2 = bar(29825.50, 29825.50, 29819.50, 29820.00)
    # VII #2: Open3 (29819.25) < Close2 (29820.00)
    c3 = bar(29819.25, 29821.00, 29817.00, 29817.50)

    out = fvgs([c1, c2, c3])
    assert len(out) == 1, out
    g = out[0]
    assert g["side"] == "bearish"
    assert g["lo"] == 29819.25, g  # Open Candle3, nicht Wick-High 29821.00
    assert g["hi"] == 29826.00, g  # Close Candle1, nicht Wick-Low 29823.00


def test_no_vii_falls_back_to_wick():
    # Kein VII: Open2 <= Close1 und Close2 <= Open3 -- alter Wick-basierter Fall bleibt.
    c1 = bar(29820.00, 29826.00, 29819.00, 29825.00)
    c2 = bar(29825.00, 29830.50, 29826.00, 29830.00)
    c3 = bar(29830.00, 29833.50, 29830.50, 29833.25)

    out = fvgs([c1, c2, c3])
    assert len(out) == 1, out
    g = out[0]
    assert g["lo"] == 29826.00, g  # Wick-High Candle1
    assert g["hi"] == 29830.50, g  # Wick-Low Candle3


def test_gegenkerze_1_nutzt_koerper_oberkante():
    """MNQ 13.08.2026 00:01-00:03, vom Nutzer im Chart eingezeichnet: Kerze 1 ist BEARISH,
    ihre Koerper-Oberkante ist Open (29877.25), nicht Close (29877.00). Die VII liegt zwischen
    29877.25 und 29877.75 -- eine Grenze bei 29877.00 wuerde den Koerper von Kerze 1
    faelschlich zur Imbalance erklaeren."""
    c1 = bar(29877.25, 29878.00, 29876.50, 29877.00)
    c2 = bar(29877.75, 29879.50, 29876.75, 29879.25)
    c3 = bar(29879.25, 29886.25, 29879.00, 29881.50)

    g = fvgs([c1, c2, c3])[0]
    assert g["side"] == "bullish"
    assert g["lo"] == 29877.25, g
    assert g["hi"] == 29879.00, g


def test_gegenkerze_3_hat_keine_vii():
    """MNQ 13.08.2026 12:24-12:26, vom Nutzer im Chart eingezeichnet: Kerze 3 ist BEARISH,
    ihre Koerper-Unterkante ist Close (30180.50) und liegt UNTER der Oberkante von Kerze 2
    (30184.00) -- die Koerper ueberlappen also, es gibt keine VII. Grenze bleibt der Wick
    (Low 30180.00); Open 30184.50 waere die falsche Kante."""
    c1 = bar(30163.75, 30169.25, 30162.75, 30165.25)
    c2 = bar(30165.50, 30185.50, 30163.75, 30184.00)
    c3 = bar(30184.50, 30185.75, 30180.00, 30180.50)

    g = fvgs([c1, c2, c3])[0]
    assert g["side"] == "bullish"
    assert g["lo"] == 30165.25, g
    assert g["hi"] == 30180.00, g


def test_zeitstempel_ist_die_displacement_kerze():
    """Das FVG traegt die Zeit der MITTLEREN Kerze (Displacement), nicht der dritten --
    so heisst es auch im Chart. `t_start`/`t_end` spannen die drei Kerzen auf."""
    from datetime import timedelta
    b = [Bar(t=T + timedelta(minutes=k), o=o, h=h, l=lo, c=c) for k, (o, h, lo, c) in
         enumerate([(29877.25, 29878.00, 29876.50, 29877.00),
                    (29877.75, 29879.50, 29876.75, 29879.25),
                    (29879.25, 29886.25, 29879.00, 29881.50)])]
    g = fvgs(b)[0]
    assert g["t"] == b[1].t, g
    assert (g["t_start"], g["t_end"]) == (b[0].t, b[2].t), g


def test_starkes_fvg_braucht_swing_break():
    """Nutzerregel: stark = Displacement schliesst durch einen bestaetigten Swing High/Low.
    Dieselben drei Kerzen, einmal mit einem alten Swing High darunter (Break -> stark),
    einmal mit einem Swing High darueber (kein Break -> normal)."""
    from datetime import timedelta

    flat = (29870, 29871, 29869, 29870)

    def seq(swing_high):
        # Swing an Index 2, damit das Fraktal (n=2) links und rechts Nachbarn hat und bis
        # Kerze 1 des FVG (Index 5) bestaetigt ist.
        rows = [flat, flat, (29870, swing_high, 29869, 29870.5), flat, flat]
        rows += [(29877.25, 29878.00, 29876.50, 29877.00),
                 (29877.75, 29879.50, 29876.75, 29879.25),
                 (29879.25, 29886.25, 29879.00, 29881.50)]
        return [Bar(t=T + timedelta(minutes=k), o=o, h=h, l=lo, c=c)
                for k, (o, h, lo, c) in enumerate(rows)]

    def gap(swing_high):   # das FVG aus den letzten drei Kerzen, Displacement = Index 6
        return next(g for g in fvgs(seq(swing_high)) if g["i"] == 6)

    # Swing 29878.50 liegt ueber Kerze 1 (Close 29877.00), erst das Displacement
    # (Close 29879.25) schliesst durch -> stark.
    assert gap(29878.50)["broke"] == "close"
    assert gap(29878.50)["strong"] is True
    assert gap(29999.00)["strong"] is False             # Swing unerreicht
    assert gap(29999.00)["swing"] == 29999.00


def test_size_rel_misst_gegen_die_lokale_kerzenrange():
    """`size_rel` = FVG-Groesse / Median-Range der Kerzen davor. Zwei identische FVGs in
    unterschiedlicher Volatilitaet muessen unterschiedliche size_rel bekommen -- genau das
    macht absolute Punktschwellen unbrauchbar. Zu wenig Vorlauf -> None statt Scheinwert."""
    from datetime import timedelta
    from analyze_ohlc import VOL_MIN_BARS

    def seq(ruhe_range):
        rows = [(100, 100 + ruhe_range, 100, 100)] * 12          # Vorlauf mit fester Range
        rows += [(100, 101, 99, 100), (101, 110, 100, 109), (109, 112, 108, 111)]
        return [Bar(t=T + timedelta(minutes=k), o=o, h=h, l=lo, c=c)
                for k, (o, h, lo, c) in enumerate(rows)]

    ruhig = next(g for g in fvgs(seq(2)) if g["i"] == 13)
    wild = next(g for g in fvgs(seq(20)) if g["i"] == 13)
    assert ruhig["size"] == wild["size"], "gleiche FVG-Groesse als Ausgangspunkt"
    assert ruhig["size_rel"] > wild["size_rel"], (ruhig["size_rel"], wild["size_rel"])
    assert abs(ruhig["size_rel"] - ruhig["size"] / 2) < 1e-9    # Median-Range = 2

    # Weniger als VOL_MIN_BARS Vorlaufkerzen -> None, keine Scheingenauigkeit.
    # Die Displacement-Kerze landet bei Index VOL_MIN_BARS-1, hat also genau eine Kerze
    # zu wenig Vorlauf.
    kurz = [bar(100, 101, 99, 100)] * (VOL_MIN_BARS - 2)
    kurz += [bar(101, 110, 100, 109), bar(109, 112, 108, 111)]
    g = fvgs(kurz)
    assert g and g[0]["i"] == VOL_MIN_BARS - 2, g
    assert g[0]["size_rel"] is None, g


def test_vii_misst_koerper_gegen_koerper():
    """viis(): dieselbe Gegenkerze wie oben -- die Luecke geht von der Koerper-Oberkante
    (29877.25), nicht vom Close (29877.00)."""
    v = viis([bar(29877.25, 29878.00, 29876.50, 29877.00),
              bar(29877.75, 29879.50, 29876.75, 29879.25)])
    assert len(v) == 1, v
    assert (v[0]["lo"], v[0]["hi"]) == (29877.25, 29877.75), v


if __name__ == "__main__":
    test_bisi_uses_vii_edges_not_wicks()
    test_sibi_uses_vii_edges_not_wicks()
    test_no_vii_falls_back_to_wick()
    test_gegenkerze_1_nutzt_koerper_oberkante()
    test_gegenkerze_3_hat_keine_vii()
    test_zeitstempel_ist_die_displacement_kerze()
    test_starkes_fvg_braucht_swing_break()
    test_size_rel_misst_gegen_die_lokale_kerzenrange()
    test_vii_misst_koerper_gegen_koerper()
    print("OK")
