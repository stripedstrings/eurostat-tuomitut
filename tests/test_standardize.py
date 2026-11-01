"""Käsin lasketut SIR-esimerkit ja puuttuvan ikä×sukupuoli -datan sääntö."""

from __future__ import annotations

import math

import pandas as pd
from scipy.stats import chi2

from src.rates import ALPHA
from src.standardize import (
    odotettu_tapaukset,
    on_ika_sukupuoli_rikoksessa,
    osuus_erosta,
    sir_ci,
    sir_luku,
)


def test_odotettu_kaksi_stratumia():
    r_nat = pd.Series([0.01, 0.02], index=["Y15-24_M", "Y25-64_M"])
    pop_for = pd.Series([500.0, 500.0], index=["Y15-24_M", "Y25-64_M"])
    e = odotettu_tapaukset(r_nat, pop_for)
    assert abs(e - (0.01 * 500 + 0.02 * 500)) < 1e-12


def test_odotettu_nan_jos_stratum_puuttuu():
    r_nat = pd.Series([0.01, float("nan")], index=["a", "b"])
    pop_for = pd.Series([500.0, 500.0], index=["a", "b"])
    assert math.isnan(odotettu_tapaukset(r_nat, pop_for))


def test_sir_ja_osuus_kasin():
    e = 10.0
    o = 20.0
    sir = sir_luku(o, e)
    assert sir == 2.0
    rr = 2.25
    assert abs(osuus_erosta(rr, sir) - (2.25 - 2.0) / 2.25) < 1e-12
    assert math.isnan(osuus_erosta(rr, float("nan")))


def test_sir_ci_garwood():
    o, e = 20.0, 10.0
    lo, hi = sir_ci(o, e)
    lo_o = chi2.ppf(ALPHA / 2, 40) / 2
    hi_o = chi2.ppf(1 - ALPHA / 2, 42) / 2
    assert abs(lo - lo_o / e) < 1e-10
    assert abs(hi - hi_o / e) < 1e-10


def test_ei_ika_sukupuolta_ilman_sarakkeita():
    assert on_ika_sukupuoli_rikoksessa(["geo", "citizen", "leg_stat"]) is False
    assert on_ika_sukupuoli_rikoksessa(["geo", "age", "sex", "citizen"]) is True
