"""S1 vertaa etusivua otsikkoon; ei täytä nollalla."""

from src.analyze_media import p1_osuudet
from src.sensitivity_media import _hae, _vertailu


def test_s1_ero_etusivu_miinus_otsikko():
    etu = [
        {
            "media": "yle_uutiset",
            "paiva": "2023-01-02",
            "http_tiedosto": "9",
            "n_otsikkoa": "2",
            "entiteetti": "putin",
        }
    ]
    ots = [
        {
            "media": "yle_uutiset",
            "paiva": "2023-01-02",
            "otsikko": "Putin otsikko tässä kokeessa aaa",
            "entiteetti": "putin",
        },
        {
            "media": "yle_uutiset",
            "paiva": "2023-01-02",
            "otsikko": "Urheiluillan tulos ilman nimeä xyz",
            "entiteetti": "",
        },
    ]
    p1 = p1_osuudet(etu, ots)
    paa = _hae(
        p1,
        yksikko="otsikko",
        media="yle_uutiset",
        ryhma="putin",
        jakso="havaittu",
    )
    et = _hae(
        p1,
        yksikko="etusivu",
        media="yle_uutiset",
        ryhma="putin",
        jakso="havaittu",
    )
    assert paa is not None and et is not None
    r = _vertailu("S1", "t", "yle_uutiset", "putin", paa, int(et["x"]), int(et["n"]), "")
    assert r["n_paa"] == "2"
    assert r["n_s"] == "1"
    assert float(r["ero"]) == 0.5
