"""P1-osuus ja ensisijainen entiteetti ilman täyttöä."""

from src.analyze_media import _ensimmainen, _kelpaa_etusivu, p1_osuudet


def test_etusivu_vaatii_otsikot():
    assert not _kelpaa_etusivu({"http_tiedosto": "100", "n_otsikkoa": "0"})
    assert not _kelpaa_etusivu({"http_tiedosto": "", "n_otsikkoa": "10"})
    assert _kelpaa_etusivu({"http_tiedosto": "100", "n_otsikkoa": "3"})


def test_ensimmainen_jarjestys():
    assert _ensimmainen({"putin", "rikos"}) == "putin"
    assert _ensimmainen(set()) == "muu"


def test_p1_ei_tayta_puuttuvaa_html():
    etu = [
        {
            "media": "yle_uutiset",
            "paiva": "2023-01-01",
            "http_tiedosto": "",
            "n_otsikkoa": "",
            "entiteetti": "putin",
        },
        {
            "media": "yle_uutiset",
            "paiva": "2023-01-02",
            "http_tiedosto": "9",
            "n_otsikkoa": "2",
            "entiteetti": "putin",
        },
    ]
    ots = [
        {
            "media": "yle_uutiset",
            "paiva": "2023-01-02",
            "otsikko": "Putin otsikko tässä kokeessa",
            "entiteetti": "putin",
        }
    ]
    rivit = p1_osuudet(etu, ots)
    hav = [
        r
        for r in rivit
        if r["yksikko"] == "etusivu" and r["jakso"] == "havaittu" and r["ryhma"] == "putin"
    ]
    assert hav[0]["n"] == "1"
    assert hav[0]["x"] == "1"
