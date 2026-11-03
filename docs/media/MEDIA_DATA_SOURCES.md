# Mediahaaran datalähteet

Testattu 2026-11-01, pieni näyte (`curl.exe`, ei koko-arkistoa).
Koodeja tai kattavuutta ei ole arvattu. Puuttuva = puuttuva.
HTTP-loki: `media/output/tables/lahteet_vaihe1.csv`.
Näytteet: `media/data/raw/` (git-ignorissa paitsi MANIFEST).

Yhteenveto:

| Ehdokas | Testi | Tila 2026-11-01 |
|---|---|---|
| Wayback Machine CDX | `web.archive.org/cdx/search/cdx` | **saatavilla** (indeksi). Ensimmäinen IL-kysely 503; uusinta 200. |
| Yle API | `developer.yle.fi`, `external.api.yle.fi` | **ei artikkelidataa**. Julkinen API = teksti-TV. |
| GDELT DOC 2.0 | `api.gdeltproject.org/api/v2/doc/doc` | **päätepiste vastaa**; tämä isäntä sai **429**, ei JSON-artikkeleita. |
| Media Cloud | `api.mediacloud.org`, `search.mediacloud.org` | **ei avointa JSON-API:a tässä verkossa**. `api.mediacloud.org` ei resolvoitunut. |
| RSS | Yle `feeds.yle.fi`, IL `/rss.xml` (etusivun href) | **saatavilla tuoreet otsikot**. Ei historiallista etusivuarkistoa. |

Koko ajanjakson (esim. 2015–2025) peittävyyttä ei laskettu.

---

## Wayback Machine CDX

- URL: `https://web.archive.org/cdx/search/cdx`
- Ehdot: Internet Archiven CDX-palvelu; snapshotit ovat arkiston, ei median, otoksia.

Näyte `limit=3`, `output=json` (HTTP 200):

- `url=yle.fi/` sarakkeet: `urlkey`, `timestamp`, `original`, `mimetype`, `statuscode`, `digest`, `length`. Vanhin rivi näytteessä: timestamp `19961228111503`.
- `url=www.iltalehti.fi/` + `fl=original,timestamp,statuscode,mimetype`. Vanhin rivi näytteessä: `19961106151341`.

Näyte `from=20230101&to=20230107&limit=15` (HTTP 200):

- `www.iltalehti.fi/`: 15 riviä, alkaen `20230101001214`. Mukana `200`, `301`, `warc/revisit`.
- `yle.fi/uutiset`: 15 riviä, alkaen `20230101005046`, `statuscode=200`.

Rajoitteet: `limit=15` ei ole viikon täysi lista. Ei todistetta jokaiselle päivälle 2015–2025. CDX ei palauta otsikkokenttiä; otsikko vaatii snapshotin HTML:n (erillinen haku, vaiheet 2–3). Ensimmäinen IL-kutsu samana päivänä: HTTP 503, koko 0.

---

## Yle API

Dokumentti `https://developer.yle.fi/en/api/index.html` (HTTP 200): *There is no public API for media, program schedule, or article data.* Avoin rajapinta: teksti-TV. Avaimet: Yle Tunnus. Lisenssi: ei väärinkäyttöä / edelleenjakelua; ei kaupalliseen käyttöön (yhteenvedetty dokumentista).

Testi `https://external.api.yle.fi/v1/teletext/pages/100.json`:

- ilman `app_id`/`app_key`: HTTP **403**, runko `Invalid app_id or app_key`
- `app_id=x&app_key=x`: HTTP **200**, JSON-avain `teletext` (sivu 100). Tämä ei ole uutis-API.

Artikkelihakua ei testattu kolmannen osapuolen avaimilla. Niitä ei käytetä.

---

## GDELT DOC 2.0

- URL: `https://api.gdeltproject.org/api/v2/doc/doc`
- Dokumentti: GDELT-blogi (DOC 2.0). Avainta ei vaadita dokumentaatiossa.

Testi `query=domain:yle.fi` / `query=yle.fi`, `mode=ArtList`, `format=json`, `maxrecords=1` tai `3`: molemmat HTTP **429**. Runko: *Please limit requests to one every 5 seconds...*. JSON-artikkelilistaa ei saatu. Uusintaväli 6 s ei riittänyt tälle isännälle.

---

## Media Cloud

Dokumentti: `https://www.mediacloud.org/documentation/search-api-guide` (HTTP 200). Vanhempi v2: `https://api.mediacloud.org/api/v2/...` vaatii `key` (readthedocs).

Tämä kone:

- `api.mediacloud.org`: DNS, ei A/AAAA-tietuetta. curl host not found. Ei HTTP-koodia.
- `search.mediacloud.org`: HTTP 200, SPA. Sivun asetuksissa `earliestAvailableDate = "2008-01-01"`, `availableProviders = ['onlinenews-mediacloud']`. Tarinoita ei haettu ilman tiliä.

Tila: JSON-haku **ei todennettu**. Avainta ei ole.

---

## RSS

### Yle

- `https://feeds.yle.fi/uutiset/v1/majorHeadlines/YLE_UUTISET.rss` HTTP **200**, `rss version="2.0"`.
- Kanava: `Yle Uutiset | Pääuutiset`. Itseviite: `https://yle.fi/rss/uutiset/paauutiset`.
- Näytteessä **12** `<item>`-elementtiä. Kentät itemissä: `title`, `link`, `description`, `category` (useita), `guid`, `pubDate`.
- Käyttöehdot (linkki syötteessä): `https://yle.fi/aihe/a/20-10008076` HTTP 200, otsikko *Ylen RSS-syötteen käyttöehdot* (päivitetty 2026-04-01 sivun metassa).
- `https://feeds-eks-prod.eks-c1.yle.fi/...`: DNS ei resolvoitunut (HTTP 000).

Rajoite: pääuutisten tuore lista, ei etusivuarkistoa vuodelle 2023.

### Iltalehti

Etusivun HTML:ssä href `/rss.xml` (ei arvattu). `https://www.iltalehti.fi/rss.xml` HTTP **200**, `Content-Type: application/rss+xml`. Kanava: *Iltalehti.fi tuoreimmat uutiset*; kuvaus: *Iltalehden 20 tuoreinta uutista*. Näytteessä **20** `<item>`. Itseviite: `https://www.iltalehti.fi/rss`.

Rajoite: 20 tuoreinta, ei kansiarkistoa 2023.

Muiden medioiden RSS-osoitteita ei haettu.

---

## Mitä vaihe 2 voi käyttää (vain testatun mukaan)

- CDX-indeksi etusivu-URL:ille (yle.fi, yle.fi/uutiset, www.iltalehti.fi), aukot = NaN.
- Yle- ja IL-RSS vain nykyhetkeen; ei täytä historiallisia päiviä.
- Yle-artikkeli-API: ei.
- GDELT: uusi testi / hitaampi tahti; 429 ≠ tyhjä aineisto eikä peittävyys.
- Media Cloud: ei ennen avainta ja onnistunutta API-kutsua.

H3 (klikit) = ei testattavissa näillä lähteillä.

---

## Vaihe 2 (haettu 2026-11-02)

CDX koko jaksolle 2015–2025, `python -m src.fetch_media`. Ruudukko:
`media/output/tables/coverage_media_paiva.csv` (puuttuva päivä tyhjä, ei täyttöä).
Yhteenveto: `coverage_media_yhteenveto.csv`.

| media | n_paivaa | n_cdx | n_cdx_200 | n_puuttuu_cdx | n_puuttuu_200 |
|---|---:|---:|---:|---:|---:|
| iltalehti_etusivu | 4018 | 3286 | 3159 | 732 | 859 |
| yle_uutiset | 4018 | 3741 | 3686 | 277 | 332 |

Luvut CDX-vastauksesta. IL:n ensimmäinen `statuscode=200`-päivä näytteessä 2015-04-28;
Ylen 2015-01-02. Viimeiset 200-rivit 2025-12-31.

RSS 2026-11-02: IL 20 item, Yle 13 item. Ei historiaruudukossa.

HTML-snapshotteja ei haettu. GDELT/Media Cloud/Yle-artikkeli-API ei.

---

## Vaihe 3 (esikäsittely, 2026-11-02)

HTML Wayback-snapshotit: `python -m src.parse_media`. Tiedostot
`media/data/raw/snapshots/{media}/{paiva}.html` (git-ignorissa).
Jäsennys: `tietueet_etusivu.csv`, `tietueet_otsikko.csv`,
`tietueet_yhteenveto.csv`. Koodikirja: `media/codebook_esikasittely_v1.md`.

Rinnakkainen haku (5 työntekijää) katkaisi IA-yhteyksiä (curl 7 / HTTP 0).
Jatko: yksi työntekijä, 1,5 s tauko. Ei täyttöä. Päivä ilman tiedostoa:
tyhjät otsikkokentät. `aihe` ja `savy` tyhjiä.

| media | n_paivaa | n_tiedosto | n_otsikko_paiva | n_otsikkoa | n_ilman_otsikkoa |
|---|---:|---:|---:|---:|---:|
| iltalehti_etusivu | 4018 | 165 | 165 | 10545 | 0 |
| yle_uutiset | 4018 | 81 | 81 | 3526 | 0 |

HTML-kattavuus << CDX. Jatko: `python -m src.parse_media --tyot 1`. GDELT/Media Cloud/Yle-artikkeli-API ei. RSS ei täytä historiaa.

---

## Vaihe 4 (koodaus, 2026-11-03)

Otos `koodaus_otos.csv`: 500 otsikkoa vaihe 3 -taulusta, siemen 20261103,
250 IL + 250 Yle. Ei uutta HTML-hakua. Ihmiskoodit tyhjiä.
Yhteenveto: `koodaus_yhteenveto.csv`. F1 (sääntö vs. sääntö): `koodaus_f1.csv`.

---

## Vaihe 5 (analyysi, 2026-11-03)

Ei uutta hakua. Taulut: `p1_entiteetti_osuus.csv`, `h1_h7.csv`,
`p4_mediavertailu.csv`, `p3_p5_tila.csv`. Ulkoisia indikaattoreita ei.

---

## Vaihe 6 (herkkyys, 2026-11-03)

Ei uutta hakua. `herkkyys_media_S1_S7.csv`, `herkkyys_media_yhteenveto.csv`.

---

## Vaihe 7 (M4, 2026-11-03)

Ei uutta mediahakua. K1: `output/tables/asteet.csv` geo=FI (haettu 2026-11-01).
Taulut: `m4_media_vs_k1.csv`, `m4_varoitukset.csv`.
