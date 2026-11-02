"""Otsikkopoiminta tunnetuista HTML-esimerkeistä."""

from src.parse_media import entiteetti_osumat, poimi_otsikot


def test_poimi_otsikot_ei_kayta_title_tai_og_title():
    html = """
    <html><head><title>Iltalehti.fi</title>
    <meta property="og:title" content="Iltalehti">
    <meta property="og:image" content="https://example.invalid/kuva.png">
    </head><body>
    <h1 class="otsikko">Presidentti tapasi vieraan Helsingissä</h1>
    <span class="otsikko">Pakolaisleiri laajenee rajalla tänä vuonna</span>
    <h2 class="saa_otsikko">Sää tunti tunnilta Helsingissä</h2>
    <h3>Lisää aiheesta</h3>
    <figcaption>Kuva rajalta aamulla</figcaption>
    </body></html>
    """
    otsikot, kuvateksti, kuva = poimi_otsikot(html)
    assert "Iltalehti.fi" not in otsikot
    assert "Iltalehti" not in otsikot
    assert "Presidentti tapasi vieraan Helsingissä" in otsikot
    assert "Pakolaisleiri laajenee rajalla tänä vuonna" in otsikot
    assert not any("Sää tunti tunnilta" in o for o in otsikot)
    assert kuvateksti == "Kuva rajalta aamulla"
    assert kuva.endswith("kuva.png")


def test_poimi_otsikot_il_2023_luokat():
    html = """
    <html><body>
    <div class="front-title a-title-font"><a href="/x"><span>Venäjän hyökkäys Ukrainaan jatkuu yhä</span></a></div>
    <div class="latest-pala-title">Putin kommentoi tilannetta Moskovassa</div>
    </body></html>
    """
    otsikot, _, _ = poimi_otsikot(html)
    assert "Venäjän hyökkäys Ukrainaan jatkuu yhä" in otsikot
    assert "Putin kommentoi tilannetta Moskovassa" in otsikot


def test_poimi_otsikot_ei_minimalheadlines_osamerkkijonoa():
    html = """
    <html><body>
    <h3>Tampereella mahdollinen ampumatapaus hotellin alueella</h3>
    <div class="MinimalHeadlines__Texts-sc-zhu28g-3">Yritykset Tampereella mahdollinen ampumatapaus hotellin alueella</div>
    </body></html>
    """
    otsikot, _, _ = poimi_otsikot(html)
    assert otsikot == ["Tampereella mahdollinen ampumatapaus hotellin alueella"]


def test_entiteetti_osumat_avainlista():
    hit = entiteetti_osumat(["Putin puhui", "epidemia leviää"])
    assert "putin" in hit.split(";")
    assert "epidemia" in hit.split(";")
    assert entiteetti_osumat(["Urheiluillan tulos"]) == ""
