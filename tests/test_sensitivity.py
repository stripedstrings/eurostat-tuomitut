"""S1/S5/S6-säännöt tunnetulla paneelilla."""

from __future__ import annotations

import pandas as pd

from src.rates import laske_asteet, poolaa
from src.sensitivity import asteet_vaihe, taulu_s1_s7


def _paneeli() -> pd.DataFrame:
    vuodet = list(range(2020, 2025))
    rivit = []
    for y in vuodet:
        rivit.append(
            {
                "geo": "AT",
                "vuosi": y,
                "tuomitut_NAT": 100.0,
                "tuomitut_FOR": 50.0,
                "epaillyt_NAT": 200.0,
                "epaillyt_FOR": 80.0,
                "vaesto_NAT": 1_000_000.0,
                "vaesto_FOR": 100_000.0,
            }
        )
        rivit.append(
            {
                "geo": "BE",
                "vuosi": y,
                "tuomitut_NAT": 100.0 if y == 2020 else float("nan"),
                "tuomitut_FOR": 25.0 if y == 2020 else float("nan"),
                "epaillyt_NAT": 100.0,
                "epaillyt_FOR": 25.0,
                "vaesto_NAT": 1_000_000.0,
                "vaesto_FOR": 100_000.0,
            }
        )
    return pd.DataFrame(rivit)


def test_poolaa_vain_kelpoiset():
    a = laske_asteet(_paneeli())
    p = poolaa(a[a["vuosi"].between(2020, 2024)])
    # AT 5v: 500/5e6 ja 250/5e5; BE 1v: 100/1e6 ja 25/1e5
    # aste_NAT = 600/6e6*1e5 = 10; aste_FOR = 275/6e5*1e5 = 45.833...
    assert abs(p["aste_NAT"] - 10.0) < 1e-9
    assert abs(p["RR"] - (275 / 600_000) / (600 / 6_000_000)) < 1e-12


def test_s1_vain_taysi_kattavuus(monkeypatch):
    monkeypatch.setattr(
        "src.sensitivity.crime_unique",
        lambda col: ["NAT", "FOR", "TOTAL"] if col == "citizen" else ["NR", "P_HTHAB"],
    )
    t = taulu_s1_s7(_paneeli())
    paa = t.loc[t["analyysi"] == "paa"].iloc[0]
    s1 = t.loc[t["analyysi"] == "S1"].iloc[0]
    assert int(paa["n_maata"]) == 2
    assert int(s1["n_maata"]) == 1
    assert int(s1["n_maa_vuotta"]) == 5
    assert pd.isna(t.loc[t["analyysi"] == "S2", "RR"].iloc[0])
    assert pd.isna(t.loc[t["analyysi"] == "S4", "RR"].iloc[0])
    assert pd.isna(t.loc[t["analyysi"] == "S7", "RR"].iloc[0])
    s3 = t.loc[t["analyysi"] == "S3"].iloc[0]
    assert pd.notna(s3["RR"])
    s6u = t.loc[t["analyysi"] == "S6_painottamaton", "RR"].iloc[0]
    s6p = t.loc[t["analyysi"] == "S6_painotettu", "RR"].iloc[0]
    assert pd.notna(s6u) and pd.notna(s6p)


def test_asteet_vaihe_ei_ylikirjoita_vaarin():
    a = asteet_vaihe(_paneeli(), "epaillyt")
    at = a[(a["geo"] == "AT") & (a["vuosi"] == 2020)].iloc[0]
    assert at["tuomitut_NAT"] == 200.0
    assert at["aste_NAT"] == 20.0
