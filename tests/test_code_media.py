"""Sääntökoodaus koodikirjan esimerkeillä. Ei ihmiskoodia."""

from src.code_media import arvo_otos, koodaa_aihe, koodaa_savy


def test_aihe_v1_m1_avaimet():
    assert koodaa_aihe("Putin puhui Moskovassa pitkään", "v1") == "putin"
    assert koodaa_aihe("Zelenskyi vieraili Suomessa", "v1") == "zelenskyi"
    assert koodaa_aihe("Tasavallan presidentti tapasi vieraan", "v1") == "presidentti"
    assert koodaa_aihe("Pelkkä presidentti ei riitä", "v1") == "muu"
    assert koodaa_aihe("Pakolaisleiri laajenee", "v1") == "maahanmuutto"
    assert koodaa_aihe("Rikosilmoitus jätettiin eilen", "v1") == "rikollisuus"
    assert koodaa_aihe("Influenssaepidemia alkanut", "v1") == "terveys"


def test_aihe_jarjestys_putin_ennen_rikosta():
    assert koodaa_aihe("Putin ja rikosväite otsikossa", "v1") == "putin"


def test_savy_ei_tayta_neutraalia():
    assert koodaa_savy("Eduskunta kokoontui tänään", "v1") == ""
    assert koodaa_savy("Uhkailu jatkui illalla", "v1") == "uhka"
    assert koodaa_savy("Hyökkäys jatkui illalla", "v1") == ""
    assert koodaa_savy("Hyökkäys jatkui illalla", "v1b") == "uhka"


def test_otos_siemen_ja_koko():
    rivit = [
        {"media": "iltalehti_etusivu", "otsikko": f"IL otsikko numero {i:03d} xyz"}
        for i in range(300)
    ] + [
        {"media": "yle_uutiset", "otsikko": f"Yle otsikko numero {i:03d} xyz"}
        for i in range(300)
    ]
    a = arvo_otos(rivit, n=500, siemen=20261103)
    b = arvo_otos(rivit, n=500, siemen=20261103)
    assert len(a) == 500
    assert a == b
    assert sum(1 for r in a if r["media"] == "iltalehti_etusivu") == 250
    assert sum(1 for r in a if r["media"] == "yle_uutiset") == 250
    tyhjat = [{"media": "yle_uutiset", "otsikko": ""}]
    assert arvo_otos(tyhjat, n=10) == []
