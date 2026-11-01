"""Käsin lasketut esimerkit asteille, RR:lle ja Garwood-väleille."""

from __future__ import annotations

import math

import pandas as pd
from scipy.stats import chi2, norm

from src.rates import (
    ALPHA,
    Z_95,
    aste_ci,
    aste_per_100k,
    garwood_lkm_ci,
    laske_asteet,
    rr_log_ci,
)


def test_aste_per_100k_tunnettu():
    d = pd.Series([100.0, 50.0])
    pop = pd.Series([1_000_000.0, 200_000.0])
    got = aste_per_100k(d, pop)
    assert got.iloc[0] == 10.0
    assert got.iloc[1] == 25.0


def test_aste_nan_kun_nimittaja_nolla_tai_puuttuu():
    d = pd.Series([10.0, 10.0, float("nan")])
    pop = pd.Series([0.0, float("nan"), 1000.0])
    got = aste_per_100k(d, pop)
    assert got.isna().all()


def test_rr_log_ci_kasin():
    # D_NAT=100, pop_NAT=1e6 -> 10; D_FOR=225, pop_FOR=1e6 -> 22.5; RR=2.25
    rr = pd.Series([2.25])
    d_nat = pd.Series([100.0])
    d_for = pd.Series([225.0])
    lo, hi = rr_log_ci(rr, d_nat, d_for)
    se = math.sqrt(1 / 225 + 1 / 100)
    ln_rr = math.log(2.25)
    z = float(norm.ppf(0.975))
    assert abs(Z_95 - z) < 1e-12
    assert abs(lo.iloc[0] - math.exp(ln_rr - z * se)) < 1e-12
    assert abs(hi.iloc[0] - math.exp(ln_rr + z * se)) < 1e-12


def test_garwood_k9():
    d = pd.Series([9.0])
    lo, hi = garwood_lkm_ci(d)
    assert abs(lo.iloc[0] - chi2.ppf(ALPHA / 2, 18) / 2) < 1e-10
    assert abs(hi.iloc[0] - chi2.ppf(1 - ALPHA / 2, 20) / 2) < 1e-10


def test_garwood_k0():
    d = pd.Series([0.0])
    lo, hi = garwood_lkm_ci(d)
    assert lo.iloc[0] == 0.0
    assert abs(hi.iloc[0] - chi2.ppf(1 - ALPHA / 2, 2) / 2) < 1e-10


def test_aste_ci_skaalaa_vaestolla():
    d = pd.Series([9.0])
    pop = pd.Series([100_000.0])
    lo, hi = aste_ci(d, pop)
    lo_d, hi_d = garwood_lkm_ci(d)
    assert abs(lo.iloc[0] - lo_d.iloc[0] / 100_000 * 100_000) < 1e-10
    assert abs(hi.iloc[0] - hi_d.iloc[0]) < 1e-10


def test_laske_asteet_merkitsee_eika_poista():
    paneeli = pd.DataFrame(
        {
            "geo": ["AA", "BB", "CC"],
            "maa": ["A", "B", "C"],
            "vuosi": [2010, 2010, 2010],
            "tuomitut_NAT": [100.0, 5.0, 50.0],
            "tuomitut_FOR": [225.0, 8.0, 40.0],
            "vaesto_NAT": [1_000_000.0, 500_000.0, 0.0],
            "vaesto_FOR": [1_000_000.0, 80_000.0, 10_000.0],
        }
    )
    out = laske_asteet(paneeli)
    assert len(out) == 3
    assert out.loc[0, "aste_NAT"] == 10.0
    assert out.loc[0, "aste_FOR"] == 22.5
    assert abs(out.loc[0, "RR"] - 2.25) < 1e-12
    assert bool(out.loc[0, "kelpoinen_aste"]) is True
    assert bool(out.loc[0, "epaluotettava"]) is False
    assert bool(out.loc[1, "kelpoinen_aste"]) is True
    assert bool(out.loc[1, "epaluotettava"]) is True
    assert bool(out.loc[1, "varoitus_pieni_D"]) is True
    assert bool(out.loc[2, "kelpoinen_aste"]) is False
    assert pd.isna(out.loc[2, "RR"])
    assert pd.isna(out.loc[2, "aste_NAT"])


def test_eu_aggregaatti_vain_molemmat_ryhmat():
    from src.rates import eu_aggregaatti

    paneeli = pd.DataFrame(
        {
            "geo": ["AT", "BE", "FI"],
            "maa": ["Itävalta", "Belgia", "Suomi"],
            "vuosi": [2010, 2010, 2010],
            "tuomitut_NAT": [100.0, 80.0, 50.0],
            "tuomitut_FOR": [225.0, float("nan"), 10.0],
            "vaesto_NAT": [1_000_000.0, 1_000_000.0, 1_000_000.0],
            "vaesto_FOR": [1_000_000.0, 100_000.0, 0.0],
            "vaesto_TOTAL": [2_000_000.0, 1_100_000.0, 1_000_000.0],
        }
    )
    asteet = laske_asteet(paneeli)
    eu = eu_aggregaatti(asteet, paneeli)
    r = eu.loc[eu["vuosi"] == 2010].iloc[0]
    assert int(r["n_maata_abs"]) == 2  # AT ja FI; BE:ltä puuttuu FOR
    assert int(r["n_maata_aste"]) == 1  # vain AT: nimittäjä > 0 molemmille
    assert r["aste_NAT"] == 10.0
    assert r["aste_FOR"] == 22.5
    assert abs(r["vaesto_osuus"] - 2_000_000.0 / 4_100_000.0) < 1e-12


def test_kausi_rr_ei_tayta_puuttuvia_vuosia():
    from src.rates import kausi_rr

    paneeli = pd.DataFrame(
        {
            "geo": ["FI", "FI", "FI", "FI", "FI"],
            "maa": ["Suomi"] * 5,
            "vuosi": [2020, 2021, 2022, 2023, 2024],
            "tuomitut_NAT": [100.0, 100.0, float("nan"), 100.0, 100.0],
            "tuomitut_FOR": [50.0, 50.0, 50.0, 50.0, 50.0],
            "vaesto_NAT": [1_000_000.0] * 5,
            "vaesto_FOR": [100_000.0] * 5,
        }
    )
    asteet = laske_asteet(paneeli)
    kausi = kausi_rr(asteet)
    fi = kausi.loc[kausi["geo"] == "FI"].iloc[0]
    assert int(fi["n_vuotta"]) == 4
    assert fi["vuodet"] == "2020,2021,2023,2024"
    assert fi["tuomitut_NAT"] == 400.0
    assert abs(fi["RR"] - 5.0) < 1e-12
