"""EU vs. kolmas maa: K1 kielletty ilman rikosjakoa; väestöjäännös ilman täyttöä."""

from __future__ import annotations

import math

import pandas as pd

from src.config import CITIZEN_EU27_FOR, CITIZEN_NEU27_FOR
from src.eu_third import k1_jako_mahdollinen, paneeli_vaesto


def test_k1_ei_mahdollinen_ilman_eu_koodeja():
    assert k1_jako_mahdollinen(["NAT", "FOR", "TOTAL"]) is False
    assert k1_jako_mahdollinen(["NAT", "FOR", CITIZEN_EU27_FOR]) is True


def test_vaesto_jaannos_ei_taytto():
    pop = pd.DataFrame(
        {
            "c_birth": ["TOTAL"] * 6,
            "sex": ["T"] * 6,
            "unit": ["NR"] * 6,
            "geo": ["FI"] * 6,
            "TIME_PERIOD": [2023] * 6,
            "citizen": [
                "NAT",
                "FOR",
                CITIZEN_EU27_FOR,
                CITIZEN_NEU27_FOR,
                "STLS",
                "UNK",
            ],
            "OBS_VALUE": [5_000_000.0, 100.0, 40.0, 60.0, 1.0, 0.0],
        }
    )
    df = paneeli_vaesto(pop)
    r = df[(df["geo"] == "FI") & (df["vuosi"] == 2023)].iloc[0]
    assert r["vaesto_EU27_FOR"] == 40.0
    assert r["vaesto_NEU27_FOR"] == 60.0
    assert r["vaesto_FOR_jaannos"] == 0.0
    assert r["osuus_EU_FOR"] == 0.4
    assert math.isnan(r["RR_EU_vs_NEU"])


def test_negatiivinen_jaannos_nan():
    pop = pd.DataFrame(
        {
            "c_birth": ["TOTAL"] * 4,
            "sex": ["T"] * 4,
            "unit": ["NR"] * 4,
            "geo": ["FI"] * 4,
            "TIME_PERIOD": [2020] * 4,
            "citizen": ["NAT", "FOR", CITIZEN_EU27_FOR, CITIZEN_NEU27_FOR],
            "OBS_VALUE": [5_000_000.0, 100.0, 80.0, 40.0],
        }
    )
    df = paneeli_vaesto(pop)
    r = df[(df["geo"] == "FI") & (df["vuosi"] == 2020)].iloc[0]
    assert math.isnan(r["vaesto_FOR_jaannos"])
