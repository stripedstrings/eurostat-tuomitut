"""K2-suodatus: ei täyttöä, ei K1-saraketta."""

from __future__ import annotations

import pandas as pd

from src.k2 import lupa_osuudet, suodata_lfs


def test_lfs_suodatus_ika_ja_pc():
    df = pd.DataFrame(
        {
            "unit": ["PC", "PC", "THS"],
            "sex": ["T", "T", "T"],
            "age": ["Y15-64", "Y15-24", "Y15-64"],
            "citizen": ["NAT", "NAT", "NAT"],
            "geo": ["FI", "FI", "FI"],
            "TIME_PERIOD": [2020, 2020, 2020],
            "OBS_VALUE": [70.0, 40.0, 99.0],
            "OBS_FLAG": [None, None, None],
        }
    )
    out = suodata_lfs(df, age="Y15-64", citizen=["NAT"], geos=["FI"])
    assert len(out) == 1
    assert out["arvo"].iloc[0] == 70.0


def test_lupa_osuus_ei_tayta():
    df = pd.DataFrame(
        {
            "geo": ["EU27_2020", "EU27_2020", "EU27_2020"],
            "vuosi": [2020, 2020, 2021],
            "reason": ["EMP", "TOTAL", "EMP"],
            "lkm": [30.0, 100.0, 40.0],
        }
    )
    p = lupa_osuudet(df)
    r0 = p[(p["vuosi"] == 2020)].iloc[0]
    assert abs(r0["osuus_EMP"] - 0.3) < 1e-12
    r1 = p[(p["vuosi"] == 2021)].iloc[0]
    assert pd.isna(r1["osuus_EMP"])


def test_k2_moduuli_ei_tuo_asteita():
    import src.k2 as k2

    assert not hasattr(k2, "laske_asteet")
    assert "RR" not in dir(k2)
