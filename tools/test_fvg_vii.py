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
    test_vii_misst_koerper_gegen_koerper()
    print("OK")
