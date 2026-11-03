"""M4-avaimet: kansalaisuus ≠ maaotsikko, ei täyttöä."""

from src.m4_media import kansalaisuus_luokka, on_rikosotsikko


def test_kansalaisuus_avaimet():
    assert kansalaisuus_luokka("Ulkomaalaisepäilty vangittiin eilen") == "FOR"
    assert kansalaisuus_luokka("Suomalaisnainen tuomittiin varkaudesta") == "NAT"
    assert kansalaisuus_luokka("Rikosilmoitus jätettiin Helsingissä") == ""
    assert kansalaisuus_luokka("Maahanmuuttaja ei ole kansalaisuus") == ""
    assert kansalaisuus_luokka("Venäjä ei ole FOR-avain tässä koodissa") == ""


def test_rikosotsikko_entiteetti_tai_avain():
    assert on_rikosotsikko({"entiteetti": "rikos", "otsikko": "x" * 20})
    assert on_rikosotsikko({"entiteetti": "", "otsikko": "Tuomitut vapautettiin eilen"})
    assert not on_rikosotsikko({"entiteetti": "putin", "otsikko": "Putin puhui pitkään Moskovassa"})
