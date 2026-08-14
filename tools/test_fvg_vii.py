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


def test_entry_und_stops_nach_ict_regel():
    """ICT 2024 Mentorship: Entry einen Tick VOR der nahen Kante (Kerze 3), Stop hinter
    Kerze 2 (aggressiv) bzw. Kerze 1 (konservativ). Quadranten muessen auf dem Raster
    liegen."""
    # bullish: Luecke 100.00 (High Kerze 1) -> 104.00 (Low Kerze 3)
    c1 = bar(99.00, 100.00, 98.00, 99.75)
    c2 = bar(99.75, 105.00, 99.50, 104.75)
    c3 = bar(104.75, 106.00, 104.00, 105.50)
    g = fvgs([c1, c2, c3], tick=0.25)[0]
    assert (g["lo"], g["hi"]) == (100.00, 104.00), g
    assert g["entry"] == 104.25, g                       # hi + 1 Tick, Fill vor dem Gap
    assert g["stop_c2"] == 99.25, g                      # unter Low Kerze 2 (99.50)
    assert g["stop_c1"] == 97.75, g                      # unter Low Kerze 1 (98.00)
    assert (g["q25"], g["ce"], g["q75"]) == (101.00, 102.00, 103.00), g

    # bearish spiegelbildlich: Luecke 96.00 (High Kerze 3) -> 100.00 (Low Kerze 1)
    d1 = bar(101.00, 102.00, 100.00, 100.25)
    d2 = bar(100.25, 100.50, 95.00, 95.25)
    d3 = bar(95.25, 96.00, 94.00, 94.50)
    h = fvgs([d1, d2, d3], tick=0.25)[0]
    assert h["side"] == "bearish" and (h["lo"], h["hi"]) == (96.00, 100.00), h
    assert h["entry"] == 95.75, h                        # lo - 1 Tick
    assert h["stop_c2"] == 100.75, h                     # ueber High Kerze 2 (100.50)
    assert h["stop_c1"] == 102.25, h                     # ueber High Kerze 1 (102.00)


def test_ferne_haelfte_offen_ist_das_staerkesignal():
    """Bullishes FVG: nur die obere Haelfte wird gehandelt -> far_half_open. Sobald eine
    Kerze unter den C.E. laeuft, faellt das Signal weg."""
    c1 = bar(99.00, 100.00, 98.00, 99.75)
    c2 = bar(99.75, 105.00, 99.50, 104.75)
    c3 = bar(104.75, 106.00, 104.00, 105.50)
    nur_oben = bar(105.00, 106.00, 103.00, 105.75)       # Low 103.00 > C.E. 102.00
    g = fvgs([c1, c2, c3, nur_oben], tick=0.25)[0]
    assert g["touched"] and g["far_half_open"], g
    assert (g["near_touches"], g["far_touches"]) == (1, 0), g
    assert g["fast"], g                                  # Kerze 4 laeuft sofort hinein

    bis_unter_ce = bar(105.00, 106.00, 101.50, 105.75)   # Low 101.50 < C.E. 102.00
    h = fvgs([c1, c2, c3, bis_unter_ce], tick=0.25)[0]
    assert not h["far_half_open"] and h["far_touches"] == 1, h

    # Ohne jede Beruehrung ist far_half_open False ("unbekannt"), nicht True
    weit_weg = bar(110.00, 111.00, 109.00, 110.50)
    k = fvgs([c1, c2, c3, weit_weg], tick=0.25)[0]
    assert not k["touched"] and not k["far_half_open"] and not k["fast"], k


def test_hp_context_vortageshaelfte_und_killzone():
    """Masterclass: bearishes HP-FVG liegt in der UNTEREN Haelfte der Vortagesrange und
    entsteht in einer Killzone."""
    from datetime import datetime

    from analyze_ohlc import hp_context, killzone_of

    assert killzone_of(datetime(2026, 1, 1, 3, 0)) == "London"
    assert killzone_of(datetime(2026, 1, 1, 13, 0)) is None

    g = {"side": "bearish", "ce": 90.0, "t": datetime(2026, 1, 1, 3, 30)}
    r = hp_context(g, prev_hi=120.0, prev_lo=80.0, bias="bearish")   # Equilibrium 100
    assert r["zone_ok"] and r["kz_ok"] and r["bias_ok"] and r["hp"], r

    r2 = hp_context({**g, "ce": 110.0}, 120.0, 80.0, "bearish")      # obere Haelfte
    assert not r2["zone_ok"] and not r2["hp"], r2

    r3 = hp_context({**g, "t": datetime(2026, 1, 1, 13, 0)}, 120.0, 80.0, "bearish")
    assert r3["zone_ok"] and not r3["kz_ok"] and not r3["hp"], r3

    # Ohne Bias bleibt bias_ok None ("unbekannt") und hp faellt auf False
    r4 = hp_context(g, 120.0, 80.0)
    assert r4["bias_ok"] is None and not r4["hp"], r4


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
    test_entry_und_stops_nach_ict_regel()
    test_ferne_haelfte_offen_ist_das_staerkesignal()
    test_hp_context_vortageshaelfte_und_killzone()
    print("OK")
