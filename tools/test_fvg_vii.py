"""Self-check: FVG-Grenzen muessen die volle VII einbeziehen (Close/Open), nicht nur
den Wick -- siehe wiki/concepts/Volume Imbalance (VII).md. Aufruf: python tools/test_fvg_vii.py
"""
from datetime import datetime

from analyze_ohlc import Bar, fvgs

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


if __name__ == "__main__":
    test_bisi_uses_vii_edges_not_wicks()
    test_sibi_uses_vii_edges_not_wicks()
    test_no_vii_falls_back_to_wick()
    print("OK")
