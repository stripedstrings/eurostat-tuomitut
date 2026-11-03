"""Nominaali-α tunnetuilla esimerkeillä."""

import math

from src.krippendorff import krippendorff_alpha_nominal, pari_alpha


def test_taaydellinen_yksimielisyys():
    assert krippendorff_alpha_nominal([["a", "a"], ["b", "b"], ["a", "a"]]) == 1.0


def test_puuttuva_pari_ohitetaan():
    got = krippendorff_alpha_nominal([["a", "a"], ["b", ""], ["a", None]])
    assert got == 1.0


def test_liian_vaham_nan():
    assert math.isnan(krippendorff_alpha_nominal([["a", ""]]))
    assert math.isnan(pari_alpha([], []))


def test_kaksi_koodaajaa_yksi_erimielisyys_kasin():
    # 9 paria, yksi erimielisyys (1 vs 2). D_o = 1/9, D_e = 230/306, α = 1 − 306/2070.
    a = ["1", "2", "3", "3", "2", "1", "4", "1", "2", None, None]
    b = ["1", "2", "3", "3", "2", "2", "4", "1", "2", "5", None]
    got = pari_alpha(a, b)
    assert abs(got - (1 - 306 / 2070)) < 1e-12
