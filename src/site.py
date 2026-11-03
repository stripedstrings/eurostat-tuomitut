"""Staattiset GitHub Pages -alasivut maittain, suomi ja englanti."""

from __future__ import annotations

import json
import math
from html import escape

import pandas as pd

from src.config import DOCS_DIR, EU27, MAAN_NIMET, MAAN_NIMET_EN, YEARS_ABS

CDN = "https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"

LIPUT = """
<nav class="kielet">
  <button type="button" class="lippu" data-lang="fi" title="Suomi" aria-label="Suomi">
    <svg viewBox="0 0 18 11" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><rect width="18" height="11" fill="#fff"/><rect y="4" width="18" height="3" fill="#002f6c"/><rect x="5" width="3" height="11" fill="#002f6c"/></svg>
  </button>
  <button type="button" class="lippu" data-lang="en" title="English" aria-label="English">
    <svg viewBox="0 0 60 30" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><rect width="60" height="30" fill="#012169"/><path d="M0,0 60,30 M60,0 0,30" stroke="#fff" stroke-width="10"/><path d="M0,0 60,30 M60,0 0,30" stroke="#C8102E" stroke-width="6"/><path d="M30,0 v30 M0,15 h60" stroke="#fff" stroke-width="10"/><path d="M30,0 v30 M0,15 h60" stroke="#C8102E" stroke-width="6"/></svg>
  </button>
</nav>
"""


def _nav_polut(sijainti: str) -> dict[str, str]:
    """Suhteelliset polut sivun kansiosta: juuri | media | fi_migr | maat | tutkimus."""
    taulu = {
        "juuri": {
            "tutkimus": "tutkimus/index.html",
            "k1": "index.html",
            "fi": "maahanmuutto-fi/index.html",
            "media": "media/index.html",
        },
        "media": {
            "tutkimus": "../tutkimus/index.html",
            "k1": "../index.html",
            "fi": "../maahanmuutto-fi/index.html",
            "media": "index.html",
        },
        "fi_migr": {
            "tutkimus": "../tutkimus/index.html",
            "k1": "../index.html",
            "fi": "index.html",
            "media": "../media/index.html",
        },
        "maat": {
            "tutkimus": "../tutkimus/index.html",
            "k1": "../index.html",
            "fi": "../maahanmuutto-fi/index.html",
            "media": "../media/index.html",
        },
        "tutkimus": {
            "tutkimus": "index.html",
            "k1": "../index.html",
            "fi": "../maahanmuutto-fi/index.html",
            "media": "../media/index.html",
        },
    }
    if sijainti not in taulu:
        raise ValueError(sijainti)
    return taulu[sijainti]


def aihe_nav(
    *,
    juuri: bool = True,
    aktiivinen: str = "maahanmuutto",
    media_sivu: bool = False,
    sijainti: str | None = None,
) -> str:
    """Yläpalkki: Tutkimus | Maahanmuutto | FI | Media."""
    if sijainti is None:
        if media_sivu:
            sijainti = "media"
        elif juuri:
            sijainti = "juuri"
        else:
            sijainti = "maat"
    p = _nav_polut(sijainti)

    def luokka(nimi: str) -> str:
        return ' class="aktiivinen"' if aktiivinen == nimi else ""

    return f"""<nav class="aiheet" aria-label="Aiheet">
  <a href="{p['tutkimus']}"{luokka("tutkimus")}>Tutkimus</a>
  <a href="{p['k1']}"{luokka("maahanmuutto")} data-i18n="nav_maahanmuutto">Maahanmuutto</a>
  <a href="{p['fi']}"{luokka("fi_migr")}>Maahanmuutto FI (TUTKIVA)</a>
  <a href="{p['media']}"{luokka("media")} data-i18n="nav_media">Media</a>
</nav>
"""


def ristiviittaukset(*, aktiivinen: str, sijainti: str = "juuri") -> str:
    """Haarojen väliset linkit; ei yhdistä aineistoja."""
    p = _nav_polut(sijainti)
    kohteet = [
        ("tutkimus", "Tutkimus-hubi", p["tutkimus"], "Kolme haaraa samalla kartalla."),
        (
            "maahanmuutto",
            "K1: EU tuomitut (esirekisteröity)",
            p["k1"],
            "Tuomitsemisasteet kansalaisuuden mukaan.",
        ),
        (
            "fi_migr",
            "Maahanmuutto FI (TUTKIVA)",
            p["fi"],
            "Tulot, kiintiöt, työllisyys ym. vain Suomi. Ei yhdistetty K1:een.",
        ),
        (
            "media",
            "Media-agenda (TUTKIVA / esirek.)",
            p["media"],
            "Näkyvyys ja kehykset; ei motiivi- tai kontrolliväitettä. M4 ≠ K1-yksikkö.",
        ),
    ]
    li = []
    for avain, otsikko, href, teksti in kohteet:
        if avain == aktiivinen:
            continue
        li.append(
            f'<li><a href="{href}"><strong>{otsikko}</strong></a> — {teksti}</li>'
        )
    return f"""<aside class="ristiviittaukset kortti" aria-label="Ristiviittaukset">
  <h2>Muut tutkimushaarat</h2>
  <ul>
    {"".join(li)}
  </ul>
  <p>Haarat ovat erillisiä. FI-paneelia ei yhdistetä K1:een. Media ei ole K1:n
  selittäjä; M4 vertaa eri yksiköitä. Motiiveja tai “agendan kontrollia” ei päätellä datasta.</p>
</aside>
"""


def tutkimus_hub_html() -> str:
    """docs/tutkimus/index.html sisältö + kehys."""
    nav = aihe_nav(sijainti="tutkimus", aktiivinen="tutkimus")
    return f"""<!DOCTYPE html>
<html lang="fi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Tutkimus kokonaisuutena</title>
  <link rel="stylesheet" href="../tyyli.css">
</head>
<body class="raportti">
  <header>
    <div class="wrap">
      {nav}
      <div class="yla">
        <p class="kicker"><a href="index.html">Tutkimus</a></p>
        {LIPUT}
      </div>
      <h1>Tutkimus kokonaisuutena</h1>
      <p class="lead">Kolme erillistä haaraa: rikostilasto (K1), Suomen maahanmuuttopaneeli
      ja uutisagenda. Niitä ei sekoiteta samaan analyysiin.</p>
      <p class="navi"><a href="tila.html">Tila</a> ·
        <a href="aikajana.html">Aikajanat</a> (ei päättelyyn)</p>
    </div>
  </header>
  <main class="wrap">
    <section class="kortti">
      <h2><a href="tila.html">Tila — hankkeen tilannekuva</a></h2>
      <p>Commit, esirekisteröintipäivä, datan hakupäivä, kattavuusmatriisit,
      pytest-tulos ja lista ei-testattavista. Ei johtopäätöksiä.</p>
    </section>
    <section class="kortti">
      <h2><a href="aikajana.html">Rinnakkaiset aikajanat (small multiples)</a></h2>
      <p>Yksi sarja per paneeli, eri akselit, ei korrelaatioita.
      <strong>Ei käytetä päättelyyn</strong> (esirekisteröity rajoitus).</p>
    </section>
    <section class="kortti">
      <h2><a href="../index.html">K1 — Maahanmuutto / tuomitut (esirekisteröity)</a></h2>
      <p>EU-27: tuomitsemisasteet oman maan ja ulkomaan kansalaisten välillä.
      Raportti ja maasivut. Tämä on pääprojektin esirekisteröity haara.</p>
    </section>
    <section class="kortti">
      <h2><a href="../maahanmuutto-fi/index.html">Maahanmuutto FI (TUTKIVA)</a></h2>
      <p>Vain Suomi: tulot, kiintiöpakolaiset (asettaja dokumentoituna), ikä/sukupuoli,
      työllisyys, koulutus, oleskeluluvat. Puuttuva merkitään tyhjäksi.
      <strong>Ei yhdistetty K1-rikostilastoon.</strong></p>
    </section>
    <section class="kortti">
      <h2><a href="../media/index.html">Media — uutisagenda</a></h2>
      <p>Mittaa otsikoiden ja etusivujen <em>näkyvyyttä</em> ja kehyksiä (frekvenssi,
      osuus, Wilson-välit). Vertaa tarvittaessa ulkoisiin indikaattoreihin (M4 vs K1:
      eri yksiköt). <strong>Ei todistakaan</strong> “agendan kontrollia”, propagandaa
      tai “journalismia vailla journalismia” — nuo ovat tulkintoja. Motiiveja ei päätellä.</p>
    </section>
    <section class="kortti">
      <h2>Mitä ei yhdistetä</h2>
      <ul>
        <li>FI-paneelin lukuja ei liitetä K1-tuomioasteisiin selittäjiksi.</li>
        <li>Mediaosuuksia ei käytetä K1:n syynä.</li>
        <li>Kansalaisuus ≠ maahanmuuttotausta ≠ pakolaisuus.</li>
      </ul>
    </section>
  </main>
  <script src="../sivu.js"></script>
</body>
</html>
"""


LAHTEET = """
<section class="kortti">
  <h2 data-i18n="lahteet_otsikko"></h2>
  <p data-i18n="lahteet_ingressi"></p>
  <ul>
    <li>
      <a class="link-crim" href="https://doi.org/10.2908/crim_just_ctz">crim_just_ctz</a>
      — <span data-i18n="lahde_crim"></span>
      (<a href="https://ec.europa.eu/eurostat/databrowser/view/crim_just_ctz/default/table?lang=en">Eurostat Data Browser</a>)
    </li>
    <li>
      <a href="https://ec.europa.eu/eurostat/databrowser/view/migr_pop5ctz/default/table?lang=en">migr_pop5ctz</a>
      — <span data-i18n="lahde_pop"></span>
    </li>
    <li>
      <a href="https://ec.europa.eu/eurostat/cache/metadata/en/crim_sims.htm">crim_sims</a>
      — <span data-i18n="lahde_meta"></span>
    </li>
  </ul>
  <p data-i18n="lahteet_huom"></p>
</section>
"""


def _n(x):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return None
    try:
        if pd.isna(x):
            return None
    except TypeError:
        pass
    if isinstance(x, (int,)) and not isinstance(x, bool):
        return int(x)
    v = float(x)
    if math.isfinite(v) and v == int(v) and abs(v) < 1e15:
        return int(v)
    return v


def _sarja(df: pd.DataFrame, col: str) -> list:
    if col not in df.columns:
        return [None] * len(df)
    return [_n(v) for v in df[col].tolist()]


def rakenna_json(df: pd.DataFrame, avg: pd.DataFrame, eu: pd.DataFrame) -> dict:
    maat = [{"geo": "FI", "nimi": "Suomi", "nimi_en": "Finland", "tiedosto": "maat/fi.html"}]
    muut = sorted((g for g in EU27 if g != "FI"), key=lambda g: MAAN_NIMET[g])
    for g in muut:
        maat.append(
            {
                "geo": g,
                "nimi": MAAN_NIMET[g],
                "nimi_en": MAAN_NIMET_EN[g],
                "tiedosto": f"maat/{g.lower()}.html",
            }
        )

    sarjat = {}
    for geo in EU27:
        s = df[df["geo"] == geo].sort_values("vuosi")
        a = avg[avg["geo"] == geo]
        a_t = a[a["vaihe"] == "tuomitut"].iloc[0].to_dict() if len(a[a["vaihe"] == "tuomitut"]) else {}
        a_e = a[a["vaihe"] == "epaillyt"].iloc[0].to_dict() if len(a[a["vaihe"] == "epaillyt"]) else {}
        sarjat[geo] = {
            "geo": geo,
            "nimi": MAAN_NIMET[geo],
            "nimi_en": MAAN_NIMET_EN[geo],
            "vuodet": [int(v) for v in s["vuosi"].tolist()],
            "vaesto_NAT": _sarja(s, "vaesto_NAT"),
            "vaesto_FOR": _sarja(s, "vaesto_FOR"),
            "vaesto_UNK": _sarja(s, "vaesto_UNK"),
            "vaesto_STLS": _sarja(s, "vaesto_STLS"),
            "tuomitut_NAT": _sarja(s, "tuomitut_NAT"),
            "tuomitut_FOR": _sarja(s, "tuomitut_FOR"),
            "tuomitut_TOTAL": _sarja(s, "tuomitut_TOTAL"),
            "tuomitut_UNK": _sarja(s, "tuomitut_UNK"),
            "tuomitut_per_100k_NAT": _sarja(s, "tuomitut_per_100k_NAT"),
            "tuomitut_per_100k_FOR": _sarja(s, "tuomitut_per_100k_FOR"),
            "tuomitut_suhde": _sarja(s, "tuomitut_suhde_FOR_NAT"),
            "epaillyt_NAT": _sarja(s, "epaillyt_NAT"),
            "epaillyt_FOR": _sarja(s, "epaillyt_FOR"),
            "epaillyt_per_100k_NAT": _sarja(s, "epaillyt_per_100k_NAT"),
            "epaillyt_per_100k_FOR": _sarja(s, "epaillyt_per_100k_FOR"),
            "epaillyt_suhde": _sarja(s, "epaillyt_suhde_FOR_NAT"),
            "syyteeseen_NAT": _sarja(s, "syyteeseen_NAT"),
            "syyteeseen_FOR": _sarja(s, "syyteeseen_FOR"),
            "keskiarvo_tuomitut": {
                "n_vuotta": _n(a_t.get("n_vuotta")),
                "vuodet": a_t.get("vuodet") or "",
                "per_100k_NAT": _n(a_t.get("per_100k_NAT")),
                "per_100k_FOR": _n(a_t.get("per_100k_FOR")),
                "suhde": _n(a_t.get("suhde_FOR_NAT")),
            },
            "keskiarvo_epaillyt": {
                "n_vuotta": _n(a_e.get("n_vuotta")),
                "vuodet": a_e.get("vuodet") or "",
                "per_100k_NAT": _n(a_e.get("per_100k_NAT")),
                "per_100k_FOR": _n(a_e.get("per_100k_FOR")),
                "suhde": _n(a_e.get("suhde_FOR_NAT")),
            },
        }

    eu_out = []
    for _, r in eu.iterrows():
        eu_out.append(
            {k: _n(v) if k not in ("maat_abs", "maat_aste", "vaihe") else v for k, v in r.items()}
        )
    return {"maat": maat, "sarjat": sarjat, "eu": eu_out, "vuodet": YEARS_ABS}


def _valikko(geo: str | None, juuri: bool) -> str:
    osat = ['<label for="maa" data-i18n="maa"></label>', '<select id="maa" onchange="location.href=this.value">']
    rap = "index.html" if juuri else "../index.html"
    sel_r = " selected" if geo == "RAPORTTI" else ""
    osat.append(
        f'<option value="{rap}" data-fi="Raportti" data-en="Report"{sel_r}>Raportti</option>'
    )
    for g in ["FI"] + sorted((x for x in EU27 if x != "FI"), key=lambda x: MAAN_NIMET[x]):
        href = f"maat/{g.lower()}.html" if juuri else f"{g.lower()}.html"
        sel = " selected" if g == geo else ""
        osat.append(
            f'<option value="{href}" data-fi="{escape(MAAN_NIMET[g])}" '
            f'data-en="{escape(MAAN_NIMET_EN[g])}"{sel}>{escape(MAAN_NIMET[g])}</option>'
        )
    vert = "vertailu.html" if juuri else "../vertailu.html"
    sel_eu = " selected" if geo is None else ""
    osat.append(
        f'<option value="{vert}" data-fi="EU-vertailu" data-en="EU comparison"{sel_eu}>EU-vertailu</option>'
    )
    osat.append("</select>")
    return "\n".join(osat)


def _sivu(geo: str, juuri: bool) -> str:
    nimi = MAAN_NIMET[geo]
    nimi_en = MAAN_NIMET_EN[geo]
    pre = "" if juuri else "../"
    return f"""<!DOCTYPE html>
<html lang="fi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(nimi)} — {escape(nimi_en)}</title>
  <link rel="stylesheet" href="{pre}tyyli.css">
</head>
<body>
  <header>
    <div class="wrap">
      {aihe_nav(juuri=juuri, aktiivinen="maahanmuutto")}
      <div class="yla">
        <p class="kicker"><a href="{pre}index.html" data-i18n="kicker"></a></p>
        {LIPUT}
      </div>
      <h1 id="otsikko-maa" data-fi="{escape(nimi)}" data-en="{escape(nimi_en)}">{escape(nimi)}</h1>
      <p class="lead" data-i18n="lead"></p>
      <div class="valitsin">{_valikko(geo, juuri)}</div>
    </div>
  </header>
  <main class="wrap">
    {LAHTEET}
    <section class="kortti">
      <h2 data-i18n="luokat_otsikko"></h2>
      <p data-i18n="luokat_p1"></p>
      <ul>
        <li><strong>NAT.</strong> <span data-i18n="luokat_nat"></span> <span id="luokka-maa" data-fi="{escape(nimi)}" data-en="{escape(nimi_en)}">{escape(nimi)}</span>.</li>
        <li><strong>FOR.</strong> <span data-i18n="luokat_for"></span></li>
        <li><strong>TOTAL.</strong> <span data-i18n="luokat_total"></span></li>
      </ul>
      <p data-i18n="luokat_p2"></p>
    </section>

    <section class="kortti avain" id="avainluvut"></section>

    <section>
      <h2 data-i18n="aste_otsikko"></h2>
      <p data-i18n="aste_p"></p>
      <canvas id="kaavio-tuomitut-aste"></canvas>
    </section>

    <section class="kortti">
      <h2 data-i18n="suhde_otsikko"></h2>
      <p data-i18n="suhde_p1"></p>
      <ul>
        <li data-i18n="suhde_li1"></li>
        <li data-i18n="suhde_li2"></li>
      </ul>
      <p id="suhde-esimerkki"></p>
      <p data-i18n="suhde_ka"></p>
      <p data-i18n="suhde_raja"></p>
    </section>

    <section>
      <h2 data-i18n="lkm_otsikko"></h2>
      <canvas id="kaavio-tuomitut-lkm"></canvas>
    </section>

    <section class="kortti">
      <h2 data-i18n="vaiheet_otsikko"></h2>
      <p data-i18n="vaiheet_p1"></p>
      <ol>
        <li><strong>PER_SUSP.</strong> <span data-i18n="vaihe_susp"></span></li>
        <li><strong>PER_PRSC.</strong> <span data-i18n="vaihe_prsc"></span></li>
        <li><strong>PER_CNV.</strong> <span data-i18n="vaihe_cnv"></span></li>
      </ol>
      <p data-i18n="vaiheet_p2"></p>
    </section>

    <section>
      <h2 data-i18n="epailly_otsikko"></h2>
      <p data-i18n="epailly_p"></p>
      <canvas id="kaavio-epaillyt-aste"></canvas>
    </section>

    <section>
      <h2 data-i18n="pylvas_otsikko"></h2>
      <p data-i18n="pylvas_p"></p>
      <canvas id="kaavio-vaiheet"></canvas>
    </section>

    <section>
      <h2 data-i18n="taulu_otsikko"></h2>
      <div class="taulu-wrap"><table id="taulu"></table></div>
    </section>

    <p class="alaviite" data-i18n="alaviite"></p>
  </main>
  <script src="{CDN}"></script>
  <script>window.SIVUN_MAA = "{geo}"; window.DATA_URL = "{pre}data.json";</script>
  <script src="{pre}sivu.js"></script>
</body>
</html>
"""


def _vertailu() -> str:
    return f"""<!DOCTYPE html>
<html lang="fi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>EU</title>
  <link rel="stylesheet" href="tyyli.css">
</head>
<body>
  <header>
    <div class="wrap">
      {aihe_nav(juuri=True, aktiivinen="maahanmuutto")}
      <div class="yla">
        <p class="kicker"><a href="index.html" data-i18n="kicker"></a></p>
        {LIPUT}
      </div>
      <h1 data-i18n="vertailu_h1"></h1>
      <p class="lead" data-i18n="vertailu_lead"></p>
      <div class="valitsin">{_valikko(None, True)}</div>
    </div>
  </header>
  <main class="wrap">
    {LAHTEET}
    <section class="kortti">
      <h2 data-i18n="eu_otsikko"></h2>
      <p data-i18n="eu_p"></p>
    </section>
    <figure>
      <img class="kieli-img" data-fi="01_eu_per_100000.png" data-en="01_eu_per_100000_en.png" alt="">
      <figcaption data-i18n="cap1"></figcaption>
    </figure>
    <figure>
      <img class="kieli-img" data-fi="02_suhdeluku_maittain.png" data-en="02_suhdeluku_maittain_en.png" alt="">
      <figcaption data-i18n="cap2"></figcaption>
    </figure>
    <figure>
      <img class="kieli-img" data-fi="03_pienoiskaaviot_maittain.png" data-en="03_pienoiskaaviot_maittain_en.png" alt="">
    </figure>
    <figure>
      <img class="kieli-img" data-fi="04_absoluuttiset_maarat.png" data-en="04_absoluuttiset_maarat_en.png" alt="">
      <figcaption data-i18n="cap4"></figcaption>
    </figure>
    <p class="alaviite" data-i18n="alaviite"></p>
  </main>
  <script src="sivu.js"></script>
</body>
</html>
"""


TYYLI = """
:root { --text:#1b1f24; --muted:#4b5563; --line:#d8dee6; --bg:#f4f1ea; --card:#fff; }
* { box-sizing: border-box; }
body { margin:0; font-family:"Segoe UI", Georgia, serif; color:var(--text); background:var(--bg); line-height:1.55; }
.wrap { max-width:920px; margin:0 auto; padding:0 1.2rem; }
header { background:#1b1f24; color:#f4f1ea; padding:1.2rem 0 1.1rem; }
.yla { display:flex; justify-content:space-between; align-items:center; gap:1rem; }
header h1 { margin:0.35rem 0 0.3rem; font-size:1.85rem; }
header a { color:#f4d2b0; }
.kicker { margin:0; font-size:0.85rem; letter-spacing:0.04em; text-transform:uppercase; }
.lead { margin:0 0 0.8rem; color:#d8dee6; }
.kielet { display:flex; gap:0.4rem; }
.lippu { background:transparent; border:1px solid transparent; padding:3px; cursor:pointer; line-height:0; border-radius:3px; }
.lippu svg { width:30px; height:18px; display:block; box-shadow:0 0 0 1px rgba(255,255,255,0.25); }
.lippu[aria-pressed="true"] { border-color:#f4d2b0; }
.valitsin { display:flex; gap:0.6rem; align-items:center; }
.valitsin label { font-size:0.9rem; }
.valitsin select { font-size:1rem; padding:0.35rem 0.5rem; }
main { padding:1.4rem 0 3.5rem; }
h2 { font-size:1.25rem; margin:1.8rem 0 0.5rem; }
.kortti { background:var(--card); border:1px solid var(--line); border-radius:10px; padding:1rem 1.1rem; margin:1rem 0; }
.kortti h2 { margin-top:0; }
canvas { background:var(--card); border:1px solid var(--line); border-radius:10px; padding:0.6rem; margin:0.6rem 0 1.2rem; max-height:380px; }
.taulu-wrap { overflow-x:auto; }
table { border-collapse:collapse; width:100%; font-size:0.88rem; background:var(--card); }
th, td { border-bottom:1px solid var(--line); padding:0.35rem 0.45rem; text-align:right; white-space:nowrap; }
th:first-child, td:first-child { text-align:left; }
.alaviite { font-size:0.88rem; color:var(--muted); margin-top:2rem; }
figure img { width:100%; height:auto; border:1px solid var(--line); border-radius:10px; background:#fff; }
figcaption { color:var(--muted); font-size:0.9rem; margin:0.4rem 0 1.4rem; }
.avain p { margin:0.35rem 0; }
code { font-size:0.9em; }
.tutkiva-nauha { margin:0; padding:0.45rem 1.2rem; background:#5c2e0a; color:#fff; font-size:0.9rem; text-align:center; }
.tutkiva-nauha a { color:#f4d2b0; }
.raportti header .navi { margin:0.6rem 0 0; }
.raportti header .navi a { margin-right:0.2rem; }
.raportti h3 { font-size:1.05rem; margin:1.2rem 0 0.4rem; }
.raportti hr { border:0; border-top:1px solid var(--line); margin:1.6rem 0; }
.aiheet { display:flex; gap:1.1rem; margin:0 0 0.7rem; font-size:0.95rem; }
.aiheet a { text-decoration:none; color:#f4d2b0; padding-bottom:0.15rem; border-bottom:2px solid transparent; }
.aiheet a.aktiivinen { border-bottom-color:#f4d2b0; }
"""

SIVU_JS = r"""
const I18N = {
  fi: {
    kicker: "Tuomitut ja epäillyt EU-maissa",
    lead: "Oman maan kansalaiset ja ulkomaan kansalaiset, 2008–2024.",
    maa: "Maa",
    nav_maahanmuutto: "Maahanmuutto",
    nav_media: "Media",
    raportti_kicker: "Esirekisteröity raportti",
    raportti_h1: "Tuomitut kansalaisuuden mukaan, EU-27",
    raportti_lead: "K1: asteet NAT vs FOR, 2008–2024. Ei täyttöä, ei syy-yhteyttä.",
    raportti_title: "Tuomitut kansalaisuuden mukaan, EU-27, 2008–2024",
    raportti_alaviite: "Lähde: Eurostat crim_just_ctz, migr_pop5ctz, haettu 2026-11-01. Ei ikä- ja sukupuolivakioitu (SIR = NaN). Kansalaisuus ei kuvaa maahanmuuttotaustaa tai pakolaisuutta. Laskentayksikkö vaihtelee maittain; maiden välinen vertailu on rajallinen. Katkos viivassa = data puuttuu.",
    lahteet_otsikko: "Lähteet",
    lahteet_ingressi: "Luvut perustuvat Euroopan unionin tilastoviraston (Eurostat) julkisiin tilastoaineistoihin. Aineistot ovat EU:n virallisia, avoimesti saatavia tilastoja.",
    lahde_crim: "Suspects and offenders by citizenship. Eurostat, virallinen EU-tilasto. DOI: 10.2908/crim_just_ctz.",
    lahde_pop: "Population on 1 January by sex, citizenship and group of country of birth. Eurostat, virallinen EU-tilasto.",
    lahde_meta: "Crime and criminal justice (crim), Eurostatin metatieto.",
    lahteet_huom: "Tämä sivusto ei ole Eurostatin eikä Euroopan komission julkaisu. Esitetyt asteet on laskettu edellä mainituista aineistoista.",
    luokat_otsikko: "Kansalaisuusluokat",
    luokat_p1: "Aineisto crim_just_ctz erittelee henkilöt kolmeen luokkaan. Kansalaisuusmaittaista jakoa ei ole.",
    luokat_nat: "Ilmoittavan maan kansalaiset. Tällä sivulla:",
    luokat_for: "Muut kansalaisuudet yhteensä. Ryhmään voi sisältyä myös henkilöitä, jotka eivät kuulu vakituiseen väestöön.",
    luokat_total: "Yhteensä. Tuntematon kansalaisuus = TOTAL − NAT − FOR, kun kaikki kolme on ilmoitettu. Tuntematonta ei sijoiteta NAT- eikä FOR-lukuun.",
    luokat_p2: "NAT ja FOR eivät ole syntymämaan tai etnisyyden luokkia. Väestönimittäjä on vakituinen väestö 1. tammikuuta (migr_pop5ctz, c_birth = TOTAL, sex = T). Kansalaisuudettomat (STLS) on jätetty pois molemmista ryhmistä.",
    aste_otsikko: "Tuomitsemisaste, 100 000 asukasta kohden",
    aste_p: "Aste = tuomitut / saman kansalaisuusryhmän väestö × 100 000. Vuodelta 2008 väestöä ei ole. Puuttuva arvo näkyy katkoksena, ei nollana.",
    suhde_otsikko: "Suhdeluku",
    suhde_p1: "Suhde = ulkomaan kansalaisten tuomitsemisaste / oman maan kansalaisten tuomitsemisaste, sama vuosi.",
    suhde_li1: "Suhde 1: asteet ovat yhtä suuret.",
    suhde_li2: "Suhde 2,25: FOR-aste oli 2,25-kertainen NAT-asteeseen. Luku on kirjattujen tuomioiden suhde asukaslukuun. Se ei ole arvio tehdyistä rikoksista eikä yksittäisen henkilön riskistä.",
    suhde_ka: "Keskiarvo 2020–2024 on aritmeettinen keskiarvo vuosilta, joilta molemmat asteet on laskettu. Puuttuvia vuosia ei täytetä.",
    suhde_raja: "Lukuja ei ole vakioitu iän tai sukupuolen mukaan. Osoittajaan voi sisältyä henkilöitä, jotka eivät ole vakituista väestöä.",
    lkm_otsikko: "Tuomittujen lukumäärä",
    vaiheet_otsikko: "Oikeusprosessin vaiheet",
    vaiheet_p1: "Eurostat erottaa kolme vaihetta:",
    vaihe_susp: "Epäillyt.",
    vaihe_prsc: "Syytteeseen asetetut.",
    vaihe_cnv: "Tuomitut.",
    vaiheet_p2: "Vaiheet eivät kuvaa saman henkilöjoukon etenemistä. Epäiltyjen ja tuomittujen osamäärää ei pidä tulkita syyllisyysosuudeksi.",
    epailly_otsikko: "Epäilyaste, 100 000 asukasta kohden",
    epailly_p: "Sama väestönimittäjä kuin tuomituilla. Puuttuva arvo = katkos.",
    pylvas_otsikko: "Lukumäärät vaiheittain",
    pylvas_p: "Rinnakkaiset lukumäärät. Ei saman henkilöjoukon putki.",
    taulu_otsikko: "Vuosittaiset luvut",
    alaviite: "Ei ikä- ja sukupuolivakioitu. Laskentayksikkö vaihtelee maittain (henkilöitä tai tapauksia). Lähde: Eurostat.",
    vertailu_h1: "EU-vertailu",
    vertailu_lead: "Kaikki maat. Yksittäinen maa valitaan valikosta.",
    eu_otsikko: "EU-aggregaatti",
    eu_p: "Kunkin vuoden summa koostuu maista, joilta NAT ja FOR on ilmoitettu samana vuonna. Sarja ei ole virallinen EU-27-luku. Maiden joukko voi vaihtua vuodesta toiseen.",
    cap1: "Tuomitut / 100 000. Maat, joilta NAT ja FOR samana vuonna.",
    cap2: "Suhde = FOR-aste / NAT-aste. Keskiarvo vuosilta 2020–2024, joilta molemmat asteet on laskettu.",
    cap4: "Tuomittujen lukumäärä. Vuosi 2008 ilman väestönimittäjää.",
    avain: "Avainluvut",
    aste_tuom: "Tuomitsemisaste 2020–2024",
    aste_ep: "Epäilyaste 2020–2024",
    vuotta: "vuotta",
    oma: "oman maan kansalaiset",
    ulk: "ulkomaan kansalaiset",
    suhde: "suhde",
    esimerkki: "Vuosi",
    ei_suhdetta: "Suhdetta ei voi laskea: NAT- tai FOR-aste puuttuu kaikilta vuosilta.",
    nat: "Oman maan kansalaiset",
    for: "Ulkomaan kansalaiset",
    th: ["Vuosi","Väestö NAT","Väestö FOR","Tuomitut NAT","Tuomitut FOR","Tuomitut/100k NAT","Tuomitut/100k FOR","Suhde","Epäillyt NAT","Epäillyt FOR","Epäillyt/100k NAT","Epäillyt/100k FOR"],
    bar: ["Epäillyt, NAT","Epäillyt, FOR","Syytteeseen, NAT","Syytteeseen, FOR","Tuomitut, NAT","Tuomitut, FOR"]
  },
  en: {
    kicker: "Convicted and suspected persons in EU countries",
    lead: "National citizens and foreign citizens, 2008–2024.",
    maa: "Country",
    nav_maahanmuutto: "Immigration",
    nav_media: "Media",
    raportti_kicker: "Preregistered report",
    raportti_h1: "Convicted persons by citizenship, EU-27",
    raportti_lead: "K1: rates NAT vs FOR, 2008–2024. No filling, no causal claims.",
    raportti_title: "Convicted persons by citizenship, EU-27, 2008–2024",
    raportti_alaviite: "Source: Eurostat crim_just_ctz, migr_pop5ctz, retrieved 2026-11-01. Not age- and sex-standardised (SIR = NaN). Citizenship is not migrant background or refugee status. The counting unit varies by country; cross-country comparison is limited. A break in a line = missing data.",
    lahteet_otsikko: "Sources",
    lahteet_ingressi: "The figures are based on public statistical datasets of Eurostat, the statistical office of the European Union. These are official EU statistics and are publicly available.",
    lahde_crim: "Suspects and offenders by citizenship. Eurostat, official EU statistic. DOI: 10.2908/crim_just_ctz.",
    lahde_pop: "Population on 1 January by sex, citizenship and group of country of birth. Eurostat, official EU statistic.",
    lahde_meta: "Crime and criminal justice (crim), Eurostat metadata.",
    lahteet_huom: "This website is not a publication of Eurostat or the European Commission. The rates shown are calculated from the datasets listed above.",
    luokat_otsikko: "Citizenship categories",
    luokat_p1: "Dataset crim_just_ctz classifies persons into three categories. There is no breakdown by individual country of citizenship.",
    luokat_nat: "Citizens of the reporting country. On this page:",
    luokat_for: "All other citizenships combined. The group may include persons who are not usual residents.",
    luokat_total: "Total. Unknown citizenship = TOTAL − NAT − FOR when all three are reported. Unknown is not assigned to NAT or FOR.",
    luokat_p2: "NAT and FOR are not categories of country of birth or ethnicity. The population denominator is usual residents on 1 January (migr_pop5ctz, c_birth = TOTAL, sex = T). Stateless persons (STLS) are excluded from both groups.",
    aste_otsikko: "Conviction rate per 100 000",
    aste_p: "Rate = convicted persons / population of the same citizenship group × 100 000. Population is not available for 2008. Missing values appear as gaps, not as zeros.",
    suhde_otsikko: "Ratio",
    suhde_p1: "Ratio = conviction rate of foreign citizens / conviction rate of national citizens, same year.",
    suhde_li1: "Ratio 1: the rates are equal.",
    suhde_li2: "Ratio 2.25: the FOR rate was 2.25 times the NAT rate. The figure is the ratio of recorded convictions to population. It is not an estimate of offences committed and not an individual risk.",
    suhde_ka: "The 2020–2024 mean is the arithmetic mean of years for which both rates are available. Missing years are not filled in.",
    suhde_raja: "The figures are not standardised by age or sex. The numerator may include persons who are not usual residents.",
    lkm_otsikko: "Number of convicted persons",
    vaiheet_otsikko: "Stages of the criminal justice process",
    vaiheet_p1: "Eurostat distinguishes three stages:",
    vaihe_susp: "Persons suspected.",
    vaihe_prsc: "Persons prosecuted.",
    vaihe_cnv: "Persons convicted.",
    vaiheet_p2: "The stages do not follow the same cohort of persons. The ratio of suspects to convicted persons is not a guilt rate.",
    epailly_otsikko: "Suspect rate per 100 000",
    epailly_p: "Same population denominator as for convictions. Missing values appear as gaps.",
    pylvas_otsikko: "Counts by stage",
    pylvas_p: "Parallel counts. Not a flow of the same persons.",
    taulu_otsikko: "Annual figures",
    alaviite: "Not age- or sex-standardised. The counting unit varies by country (persons or cases). Source: Eurostat.",
    vertailu_h1: "EU comparison",
    vertailu_lead: "All countries. Select a country from the menu.",
    eu_otsikko: "EU aggregate",
    eu_p: "Each yearly sum includes only countries that reported both NAT and FOR in that year. The series is not an official EU-27 figure. The set of countries may change from year to year.",
    cap1: "Convicted per 100 000. Countries with NAT and FOR in the same year.",
    cap2: "Ratio = FOR rate / NAT rate. Mean of 2020–2024 years for which both rates are available.",
    cap4: "Number of convicted persons. 2008 without a population denominator.",
    avain: "Summary",
    aste_tuom: "Conviction rate 2020–2024",
    aste_ep: "Suspect rate 2020–2024",
    vuotta: "years",
    oma: "national citizens",
    ulk: "foreign citizens",
    suhde: "ratio",
    esimerkki: "Year",
    ei_suhdetta: "The ratio cannot be calculated: the NAT or FOR rate is missing for all years.",
    nat: "National citizens",
    for: "Foreign citizens",
    th: ["Year","Pop. NAT","Pop. FOR","Convicted NAT","Convicted FOR","Convicted/100k NAT","Convicted/100k FOR","Ratio","Suspected NAT","Suspected FOR","Suspected/100k NAT","Suspected/100k FOR"],
    bar: ["Suspected, NAT","Suspected, FOR","Prosecuted, NAT","Prosecuted, FOR","Convicted, NAT","Convicted, FOR"]
  }
};

function kieli() {
  return localStorage.getItem("kieli") === "en" ? "en" : "fi";
}

function t(key) {
  return I18N[kieli()][key];
}

function asetaKieli(lang) {
  localStorage.setItem("kieli", lang);
  location.reload();
}

function kaytKieli() {
  const lang = kieli();
  document.documentElement.lang = lang;
  document.querySelectorAll("[data-i18n]").forEach(el => {
    const v = I18N[lang][el.getAttribute("data-i18n")];
    if (v !== undefined) el.textContent = v;
  });
  const otsikko = document.querySelector("title[data-i18n]");
  if (otsikko) {
    const v = I18N[lang][otsikko.getAttribute("data-i18n")];
    if (v) document.title = v;
  }
  document.querySelectorAll(".kieli-fi").forEach(el => { el.hidden = lang !== "fi"; });
  document.querySelectorAll(".kieli-en").forEach(el => { el.hidden = lang !== "en"; });
  document.querySelectorAll("#maa option").forEach(opt => {
    const label = lang === "en" ? opt.getAttribute("data-en") : opt.getAttribute("data-fi");
    if (label) opt.textContent = label;
  });
  document.querySelectorAll(".lippu").forEach(b => {
    b.setAttribute("aria-pressed", b.getAttribute("data-lang") === lang ? "true" : "false");
  });
  document.querySelectorAll(".kieli-img").forEach(img => {
    img.src = lang === "en" ? img.getAttribute("data-en") : img.getAttribute("data-fi");
  });
  document.querySelectorAll("#otsikko-maa, #luokka-maa").forEach(el => {
    const label = lang === "en" ? el.getAttribute("data-en") : el.getAttribute("data-fi");
    if (label) el.textContent = label;
  });
  const loc = lang === "en" ? "en-GB" : "fi-FI";
  window.fmt = (v, d=1) => (v === null || v === undefined) ? "—" : Number(v).toLocaleString(loc, {maximumFractionDigits:d});
}

document.querySelectorAll(".lippu").forEach(b => {
  b.addEventListener("click", () => asetaKieli(b.getAttribute("data-lang")));
});
kaytKieli();

function tutkivaNauha() {
  if (document.body.classList.contains("raportti")) return;
  let p = document.querySelector(".tutkiva-nauha");
  if (!p) {
    p = document.createElement("p");
    p.className = "tutkiva-nauha";
    document.body.insertBefore(p, document.body.firstChild);
  }
  const juuri = !location.pathname.includes("/maat/");
  const href = juuri ? "index.html" : "../index.html";
  p.innerHTML = kieli() === "en"
    ? `EXPLORATORY (not preregistered). <a href="${href}">Registered report</a>`
    : `TUTKIVA (ei esirekisteröity). <a href="${href}">Esirekisteröity raportti</a>`;
}
tutkivaNauha();

function viiva(id, labels, a, b, otsikkoA, otsikkoB) {
  const el = document.getElementById(id);
  if (!el || typeof Chart === "undefined") return;
  new Chart(el, {
    type: "line",
    data: {
      labels,
      datasets: [
        { label: otsikkoA, data: a, borderColor: "#2c5aa0", backgroundColor: "#2c5aa0", spanGaps: false, tension: 0.15 },
        { label: otsikkoB, data: b, borderColor: "#c45c26", backgroundColor: "#c45c26", spanGaps: false, tension: 0.15 }
      ]
    },
    options: { responsive: true, plugins: { legend: { position: "bottom" } }, scales: { y: { beginAtZero: true } } }
  });
}

function pylvaat(id, labels, datasets) {
  const el = document.getElementById(id);
  if (!el || typeof Chart === "undefined") return;
  new Chart(el, {
    type: "bar",
    data: { labels, datasets },
    options: { responsive: true, plugins: { legend: { position: "bottom" } }, scales: { y: { beginAtZero: true } } }
  });
}

if (window.DATA_URL && window.SIVUN_MAA) {
  fetch(window.DATA_URL).then(r => r.json()).then(data => {
    const s = data.sarjat[window.SIVUN_MAA];
    if (!s) return;
    const lang = kieli();
    const nimi = lang === "en" ? s.nimi_en : s.nimi;
    const ots = document.getElementById("otsikko-maa");
    if (ots) ots.textContent = nimi;
    const lm = document.getElementById("luokka-maa");
    if (lm) lm.textContent = nimi;
    const y = s.vuodet;
    viiva("kaavio-tuomitut-aste", y, s.tuomitut_per_100k_NAT, s.tuomitut_per_100k_FOR, t("nat"), t("for"));
    viiva("kaavio-tuomitut-lkm", y, s.tuomitut_NAT, s.tuomitut_FOR, t("nat"), t("for"));
    viiva("kaavio-epaillyt-aste", y, s.epaillyt_per_100k_NAT, s.epaillyt_per_100k_FOR, t("nat"), t("for"));

    const idx = [];
    for (let i = 0; i < y.length; i++) {
      if (s.tuomitut_NAT[i] != null || s.epaillyt_NAT[i] != null || s.syyteeseen_NAT[i] != null) idx.push(i);
    }
    const lastYears = idx.slice(-8);
    const bar = t("bar");
    pylvaat("kaavio-vaiheet", lastYears.map(i => y[i]), [
      { label: bar[0], data: lastYears.map(i => s.epaillyt_NAT[i]), backgroundColor: "#93c5fd" },
      { label: bar[1], data: lastYears.map(i => s.epaillyt_FOR[i]), backgroundColor: "#fdba74" },
      { label: bar[2], data: lastYears.map(i => s.syyteeseen_NAT[i]), backgroundColor: "#2c5aa0" },
      { label: bar[3], data: lastYears.map(i => s.syyteeseen_FOR[i]), backgroundColor: "#c45c26" },
      { label: bar[4], data: lastYears.map(i => s.tuomitut_NAT[i]), backgroundColor: "#1e3a5f" },
      { label: bar[5], data: lastYears.map(i => s.tuomitut_FOR[i]), backgroundColor: "#7c2d12" }
    ]);

    const ka = s.keskiarvo_tuomitut;
    const ke = s.keskiarvo_epaillyt;
    const av = document.getElementById("avainluvut");
    av.innerHTML = `<h2>${t("avain")}, ${nimi}</h2>
      <p>${t("aste_tuom")} (${ka.n_vuotta || 0} ${t("vuotta")}${ka.vuodet ? ": " + ka.vuodet : ""}):
        ${t("oma")} <strong>${fmt(ka.per_100k_NAT)}</strong> / 100 000,
        ${t("ulk")} <strong>${fmt(ka.per_100k_FOR)}</strong> / 100 000,
        ${t("suhde")} <strong>${fmt(ka.suhde, 2)}</strong>.</p>
      <p>${t("aste_ep")} (${ke.n_vuotta || 0} ${t("vuotta")}${ke.vuodet ? ": " + ke.vuodet : ""}):
        ${t("oma")} <strong>${fmt(ke.per_100k_NAT)}</strong>,
        ${t("ulk")} <strong>${fmt(ke.per_100k_FOR)}</strong>,
        ${t("suhde")} <strong>${fmt(ke.suhde, 2)}</strong>.</p>`;

    const ex = document.getElementById("suhde-esimerkki");
    let pick = null;
    for (let i = y.length - 1; i >= 0; i--) {
      if (s.tuomitut_suhde[i] != null && s.tuomitut_per_100k_NAT[i] && s.tuomitut_per_100k_FOR[i]) { pick = i; break; }
    }
    if (pick !== null) {
      ex.innerHTML = `${t("esimerkki")} <strong>${y[pick]}</strong> (${nimi}):
        ${t("oma")} ${fmt(s.tuomitut_NAT[pick], 0)} / ${fmt(s.vaesto_NAT[pick], 0)}
        → ${fmt(s.tuomitut_per_100k_NAT[pick])} / 100 000.
        ${t("ulk")} ${fmt(s.tuomitut_FOR[pick], 0)} / ${fmt(s.vaesto_FOR[pick], 0)}
        → ${fmt(s.tuomitut_per_100k_FOR[pick])} / 100 000.
        ${t("suhde")} ${fmt(s.tuomitut_per_100k_FOR[pick])} ÷ ${fmt(s.tuomitut_per_100k_NAT[pick])} = <strong>${fmt(s.tuomitut_suhde[pick], 2)}</strong>.`;
    } else {
      ex.textContent = t("ei_suhdetta");
    }

    const th = t("th");
    const tbl = document.getElementById("taulu");
    let html = "<thead><tr>" + th.map(h => `<th>${h}</th>`).join("") + "</tr></thead><tbody>";
    for (let i = 0; i < y.length; i++) {
      html += `<tr><td>${y[i]}</td><td>${fmt(s.vaesto_NAT[i],0)}</td><td>${fmt(s.vaesto_FOR[i],0)}</td>
        <td>${fmt(s.tuomitut_NAT[i],0)}</td><td>${fmt(s.tuomitut_FOR[i],0)}</td>
        <td>${fmt(s.tuomitut_per_100k_NAT[i])}</td><td>${fmt(s.tuomitut_per_100k_FOR[i])}</td>
        <td>${fmt(s.tuomitut_suhde[i],2)}</td>
        <td>${fmt(s.epaillyt_NAT[i],0)}</td><td>${fmt(s.epaillyt_FOR[i],0)}</td>
        <td>${fmt(s.epaillyt_per_100k_NAT[i])}</td><td>${fmt(s.epaillyt_per_100k_FOR[i])}</td></tr>`;
    }
    tbl.innerHTML = html + "</tbody>";
  });
}
"""


def kirjoita_sivusto(df: pd.DataFrame, avg: pd.DataFrame, eu: pd.DataFrame) -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    (DOCS_DIR / "maat").mkdir(exist_ok=True)
    payload = rakenna_json(df, avg, eu)
    (DOCS_DIR / "data.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    (DOCS_DIR / "tyyli.css").write_text(TYYLI, encoding="utf-8")
    (DOCS_DIR / "sivu.js").write_text(SIVU_JS, encoding="utf-8")
    (DOCS_DIR / "vertailu.html").write_text(_vertailu(), encoding="utf-8")
    for geo in EU27:
        (DOCS_DIR / "maat" / f"{geo.lower()}.html").write_text(_sivu(geo, juuri=False), encoding="utf-8")
    from src.pages import kirjoita as kirjoita_raportti

    kirjoita_raportti()
    (DOCS_DIR / ".nojekyll").write_text("", encoding="utf-8")
