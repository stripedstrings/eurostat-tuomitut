"""Kansalliset lataajat: koodeja ei arvata, EU-aggregaattia ei tuoda."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.national.dk import puhdista as dk_puhdista
from src.national.fi import puhdista as fi_puhdista
from src.national.se import loyda_tiedosto


def test_dk_ryhmat_dst_koodeista():
    df = pd.DataFrame(
        {
            "STATSB": ["DANSK", "VEST", "IKKEVEST"],
            "OVERTRÆD": ["1", "1", "1"],
            "TID": [2020, 2020, 2020],
            "INDHOLD": [10, 2, 3],
        }
    )
    out = dk_puhdista(df)
    assert set(out["ryhma"]) == {"DANSK", "VEST", "IKKEVEST"}
    assert "FOR" not in set(out["ryhma"])
    assert out["lkm"].sum() == 15


def test_fi_kaksi_saraketta():
    df = pd.DataFrame(
        {
            "Vuosi": [2020, 2020],
            "Kansalaisuus": ["Suomi", "Ulkomaat yhteensä"],
            "Oikeudessa tuomitut, rangaistusmääräyssakot ja rikesakot yhteensä (lkm)": [
                100,
                20,
            ],
            "Oikeudessa tuomitut (lkm)": [10, 4],
        }
    )
    out = fi_puhdista(df)
    assert list(out["kansalaisuus"]) == ["Suomi", "Ulkomaat yhteensä"]
    assert out.loc[out["kansalaisuus"] == "Suomi", "oikeudessa_tuomitut"].iloc[0] == 10


def test_national_ei_tuo_eu_aggregaattia():
    import src.national.dk as dk
    import src.national.fi as fi
    import src.national.se as se

    for m in (dk, fi, se):
        assert "eu_aggregaatti" not in dir(m)
        assert "laske_asteet" not in dir(m)


def test_se_puuttuva(tmp_path, monkeypatch):
    import src.national.se as se

    monkeypatch.setattr(se, "NATIONAL_DIR", tmp_path)
    assert se.loyda_tiedosto() is None
