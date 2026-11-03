"""Wilson-väli tunnetulla esimerkillä."""

import math

from src.rates import Z_95
from src.wilson import clopper_pearson_ci, osuus, wilson_ci


def test_osuus_nan_kun_n_nolla():
    assert math.isnan(osuus(0, 0))
    lo, hi = wilson_ci(0, 0)
    assert math.isnan(lo) and math.isnan(hi)


def test_wilson_puolet_sadasta():
    lo, hi = wilson_ci(50, 100)
    z = Z_95
    z2 = z * z
    p = 0.5
    den = 1 + z2 / 100
    keski = (p + z2 / 200) / den
    puoli = z * math.sqrt(p * (1 - p) / 100 + z2 / 40000) / den
    assert abs(lo - (keski - puoli)) < 1e-12
    assert abs(hi - (keski + puoli)) < 1e-12
    assert lo < 0.5 < hi


def test_wilson_nolla_osuma():
    lo, hi = wilson_ci(0, 20)
    assert lo >= 0
    assert hi > lo


def test_clopper_pearson_nolla():
    lo, hi = clopper_pearson_ci(0, 10)
    assert lo == 0.0
    assert abs(hi - (1.0 - 0.025 ** (1.0 / 10.0))) < 1e-9


def test_clopper_pearson_nan_kun_n_nolla():
    lo, hi = clopper_pearson_ci(0, 0)
    assert math.isnan(lo) and math.isnan(hi)
