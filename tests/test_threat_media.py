"""TUTKIVA uhkakehys: tunnetut esimerkkilauseet."""

from src.threat_media import luokittele


def test_korona_tappaa_molemmat():
    t, k, r = luokittele("Korona tappaa kaikki ihmiset")
    assert t and k and r == "molemmat"


def test_hakkerit_vain_kehys():
    t, k, r = luokittele("Hakkerit voivat tunkeutua pakastimeesi")
    assert (not t) and k and r == "vain_kehys"


def test_rokote_vain_terveys():
    t, k, r = luokittele("Koronarokote saapuu Suomeen")
    assert t and (not k) and r == "vain_terveys"


def test_eduskunta_ei_kumpaakaan():
    t, k, r = luokittele("Eduskunta kokoontui tänään")
    assert (not t) and (not k) and r == "ei_kumpaakaan"


def test_tyhja_ei_taytto():
    t, k, r = luokittele("   ")
    assert (not t) and (not k) and r == ""


def test_virus_ei_riita():
    t, k, r = luokittele("Tietokoneen virus hidastaa konetta")
    assert (not t) and (not k) and r == "ei_kumpaakaan"
