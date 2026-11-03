# Raportti: mediahaara (Iltalehti, Yle), 2015–2025

Esirekisteröinti: `MEDIA_PREREGISTRATION.md` (2026-11-01).  
Aineisto: Wayback CDX (haettu 2026-11-02); HTML-snapshotteja tihennetty 2026-11-03 (TUTKIVA); K1-osuus M4:ssä Eurostat `crim_just_ctz` / `migr_pop5ctz` (haettu 2026-11-01).  
Kaikki luvut ovat taulukoista `media/output/tables/` ja `output/tables/asteet.csv`. Puuttuva = tyhjä / NaN, ei täyttöä.

**Tämä tulososio ei sisällä tulkintaa.** Tulkinta on osiossa 12.

Mediat (vain vaiheessa 1 vastanneet URL:t): `iltalehti_etusivu` (`www.iltalehti.fi/`), `yle_uutiset` (`yle.fi/uutiset`). Kalenteri: 2015-01-01 … 2025-12-31 (4018 päivää / media). Muita medioita tai maita ei ole.

---

## 1. Peitto (vaihe 2)

Lähde: `coverage_media_yhteenveto.csv`. CDX `collapse=timestamp:8` (ensimmäinen osuma päivältä). Puuttuva päivä on puuttuva.

| media | n_paivaa | n_cdx | n_cdx_200 | n_puuttuu_cdx | n_puuttuu_200 |
|---|---:|---:|---:|---:|---:|
| iltalehti_etusivu | 4018 | 3286 | 3159 | 732 | 859 |
| yle_uutiset | 4018 | 3741 | 3686 | 277 | 332 |

RSS (2026-11-02): ei historiaruudukossa. GDELT, Media Cloud ja Yle-artikkeli-API: ei aineistossa.

---

## 2. Esikäsittely (vaihe 3)

Lähde: `tietueet_yhteenveto.csv`. HTML Wayback-snapshotit; otsikot etusivun merkeistä, ei `<title>` / `og:title`.

| media | n_paivaa | n_tiedosto | n_otsikko_paiva | n_otsikkoa | n_ilman_otsikkoa |
|---|---:|---:|---:|---:|---:|
| iltalehti_etusivu | 4018 | 913 | 913 | 61914 | 0 |
| yle_uutiset | 4018 | 933 | 933 | 15944 | 0 |

TUTKIVA HTML-tihennys (2026-11-03): prioriteettivuodet 2017–2022 ja 2024–2025 vuorotellen; CDX `status=200` -päivät. Peitto media×vuosi: `coverage_media_vuosi.csv`. Yle 2016: n_html=0 (ei vielä haettu; ei nollaosuutta). HTML ≪ CDX edelleen useina vuosina.

Entiteetti = merkkijono-osuma M1-avaimista. `aihe` ja `savy` koko ruudukossa tyhjiä.

---

## 3. Koodaus (vaihe 4)

Lähde: `koodaus_yhteenveto.csv`. Siemen `20261103`. Otos 500 (250 + 250). Ihmiskoodaajia: 0. Ihmis-α: tyhjä.

Sääntö-α (TUTKIVA, ei ihmisvalidointi): aihe 1,00; sävy 1,00 (vain parit, joissa molemmilla luokka; n=7). Sävyn F1 v1b vs. v1 ei ole 1, koska v1b merkitsee rivejä, jotka v1 jättää tyhjiksi.

Sääntöaihe v1 otoksessa: muu 482; putin 7; rikollisuus 6; zelenskyi 2; maahanmuutto 2; terveys 1; presidentti 0. Sävy v1: tyhjä 493; uhka 5; pelko 2; viha 0.

Automaatiota ei viety koko ruudukkoon.

---

## 4. P1 entiteettiosuudet (vaihe 5)

Nimittäjä = havaittu HTML (etusivu, `n_otsikkoa`>0, tai otsikko). Wilson 95 %. D<10 merkitty. Lähde: `p1_entiteetti_osuus_havaittu.csv`. Kaavio: `figures/01_entiteetti_osuus.png`. Vuosittain: `figures/02_entiteetti_vuosi.png` (katkos = ei HTML:ää).

### Etusivupäivä

| media | ryhmä | x / n | osuus | Wilson 95 % | D<10 |
|---|---|---:|---:|---|---|
| Iltalehti | Putin | 83 / 165 | 50,3 % | 42,8–57,8 % | ei |
| Iltalehti | Zelenskyi | 15 / 165 | 9,1 % | 5,6–14,5 % | ei |
| Iltalehti | presidentti | 1 / 165 | 0,6 % | 0,1–3,4 % | kyllä |
| Iltalehti | maahanmuutto | 41 / 165 | 24,8 % | 18,9–32,0 % | ei |
| Iltalehti | rikollisuus | 45 / 165 | 27,3 % | 21,1–34,5 % | ei |
| Iltalehti | terveys | 5 / 165 | 3,0 % | 1,3–6,9 % | kyllä |
| Yle | Putin | 27 / 81 | 33,3 % | 24,0–44,1 % | ei |
| Yle | Zelenskyi | 15 / 81 | 18,5 % | 11,6–28,3 % | ei |
| Yle | presidentti | 0 / 81 | 0,0 % | 0,0–4,5 % | kyllä |
| Yle | maahanmuutto | 8 / 81 | 9,9 % | 5,1–18,3 % | kyllä |
| Yle | rikollisuus | 17 / 81 | 21,0 % | 13,5–31,1 % | ei |
| Yle | terveys | 4 / 81 | 4,9 % | 1,9–12,0 % | kyllä |

### Otsikko (pääyksikkö S1:ssä)

| media | ryhmä | x / n | osuus | Wilson 95 % | D<10 |
|---|---|---:|---:|---|---|
| Iltalehti | Putin | 126 / 10545 | 1,19 % | 1,00–1,42 % | ei |
| Iltalehti | Zelenskyi | 17 / 10545 | 0,16 % | 0,10–0,26 % | ei |
| Iltalehti | presidentti | 1 / 10545 | 0,01 % | 0,00–0,05 % | kyllä |
| Iltalehti | maahanmuutto | 73 / 10545 | 0,69 % | 0,55–0,87 % | ei |
| Iltalehti | rikollisuus | 66 / 10545 | 0,63 % | 0,49–0,80 % | ei |
| Iltalehti | terveys | 5 / 10545 | 0,05 % | 0,02–0,11 % | kyllä |
| Yle | Putin | 32 / 3526 | 0,91 % | 0,64–1,28 % | ei |
| Yle | Zelenskyi | 21 / 3526 | 0,60 % | 0,39–0,91 % | ei |
| Yle | presidentti | 0 / 3526 | 0,00 % | 0,00–0,11 % | kyllä |
| Yle | maahanmuutto | 11 / 3526 | 0,31 % | 0,17–0,56 % | ei |
| Yle | rikollisuus | 21 / 3526 | 0,60 % | 0,39–0,91 % | ei |
| Yle | terveys | 4 / 3526 | 0,11 % | 0,04–0,29 % | kyllä |

Vuosirivit: `p1_entiteetti_osuus.csv` (kaikki mediat, kaikki vuodet, joilla n>0).

---

## 5. H1–H7

Lähde: `h1_h7.csv`. Kaavio H1/H2: `figures/03_h1_h2.png`.

| H | Tila | Tulos |
|---|---|---|
| H1 | laskettu | Iltalehti 2023, Putin, etusivu: 47 / 84 = 56,0 % (45,3–66,1 %). Otsikko: 74 / 1833 = 4,0 % (3,2–5,0 %). 84 päivää ≠ 365. |
| H2 | laskettu | Havaittu etusivu, presidentti vs. Putin vs. Zelenskyi: ks. jakso 4. Presidentti-fraasit D<10. |
| H3 | ei testattavissa | Ei julkaisijan analytiikkaa. |
| H4 | ei testattavissa | Ei ihmis-sävyn aikasarjaa. |
| H5 | laskettu | Pearson-r kuuden entiteettiosuuden vektoreille, kaksi mediaa: etusivu 0,871; otsikko 0,788 (`p4_mediavertailu.csv`). Ei maiden vertailua. |
| H6 | ei testattavissa | Ei tuho/tuhoutuminen-luokkia. |
| H7 | ei testattavissa (pää) | Ei aihekoodia 2015–2025. |

P2 pää, P3 ja P5: ei testattavissa (`p3_p5_tila.csv`). P5:n ulkoiset indikaattorit: M4 on erillinen (jakso 8).

### H7 TUTKIVA (ei esirekisteröity)

Entropia ensisijaisesta entiteetistä tai `muu`, vain vuodet n>0. Lähde: `h7_entropia_tutkiva.csv`.

| media | vuosi | n otsikkoa | entropia (bitti) | n_luokkaa |
|---|---|---:|---:|---:|
| Iltalehti | 2015 | 3718 | 0,208 | 6 |
| Iltalehti | 2016 | 4994 | 0,165 | 5 |
| Iltalehti | 2023 | 1833 | 0,379 | 6 |
| Yle | 2015 | 102 | 0,218 | 3 |
| Yle | 2023 | 3424 | 0,220 | 6 |

---

## 6. Herkkyys S1–S7 (vaihe 6)

Pää = P1 otsikko, havaittu jakso, Wilson, molemmat mediat. Lähde: `herkkyys_media_yhteenveto.csv`, rivit `herkkyys_media_S1_S7.csv`.

| S | Vertailu | ero min | ero max |
|---|---|---:|---:|
| S1 | etusivupäivä vs. otsikko | 0,000 | 0,491 |
| S2 | Yle vs. IL (kumpaakaan ei pudoteta) | −0,004 | 0,004 |
| S3 | vain 2023 vs. havaittu jakso | −0,006 | 0,028 |
| S4 | sääntöaihe vs. entiteetti, otos 500 (TUTKIVA) | 0,000 | 0,000 |
| S5 | tyhjä→neutraali vs. vain merkitty (täyttö ei pää) | −0,704 | 0,000 |
| S6 | pituus ≥40 vs. ≥18 | ≈ 0 | ≈ 0 |
| S7 | Clopper–Pearson vs. Wilson | osuus sama | väli vaihtuu |

---

## 7. M4 media vs. K1 (vaihe 7)

Lähde: `m4_media_vs_k1.csv`, `m4_varoitukset.csv`. Kaavio: `figures/04_m4_media_vs_k1.png`. Koodikirja: `codebook_m4_v1.md`.

Vain **FI**-tuomitut. EU-aggregaatti ei mukana. Yhteiset vuodet (kelpoinen K1 ja rikos-HTML): 2015, 2016, 2023.

| lähde | yksikkö | n | n_FOR | osuus FOR | Wilson 95 % | D<10 |
|---|---|---:|---:|---:|---|---|
| K1 FI | tuomitut | 415860 | 49940 | 12,0 % | ei otanta-CI | ei |
| media | rikosotsikko | 87 | 0 | 0,0 % | 0,0–4,2 % | kyllä |
| media | rikosotsikko, ehdollinen | 0 | 0 | tyhjä | — | kyllä |

Iltalehti 66 rikosotsikkoa, Yle 21; FOR-avaimia 0 molemmissa. Avaimet: NAT `suomalais`, `suomen kansal`; FOR `ulkomaalais`, `vierasmaalais`. Ei demonyymejä, ei `maahanmuuttaja`.

---

## 8. Poikkeamat esirekisteröinnistä

`CHANGELOG.md` (media):

1. Wayback-HTML on osittainen (IA-yhteydet). Puuttuva päivä tyhjä.
2. Ihmiskoodaajia ei ole; ihmis-α tyhjä. Sääntö-α/F1 merkitty tutkiviksi.
3. P2/P3/P5 ja H3/H4/H6/H7 (pää) merkitty ei testattaviksi aineiston, ei tuloksen, vuoksi.
4. M4: avaimet eivät osuneet 87 rikosotsikkoon; osuus 0 ei ole täyttö. Yksiköt (tuomio vs. otsikko) eivät täsmää.

---

## 9. Tiedostot ja toisto

| Polku | Sisältö |
|---|---|
| `media/output/tables/coverage_media_*.csv` | CDX-peitto |
| `media/output/tables/tietueet_*.csv` | etusivu ja otsikot |
| `media/output/tables/koodaus_*.csv` | otos 500 |
| `media/output/tables/p1_*.csv` | P1 |
| `media/output/tables/h1_h7.csv` | H1–H7 |
| `media/output/tables/herkkyys_media_*.csv` | S1–S7 |
| `media/output/tables/m4_*.csv` | M4 |
| `media/output/figures/01`–`04` | kaaviot (200 dpi, suomenkieliset alaviitteet) |
| `output/tables/asteet.csv` | K1 (M4) |

Komennot (Python 3.11+, `requirements.txt`; HTML-snapshotit `media/data/raw/snapshots/`, git-ignorissa):

1. `python -m src.parse_media --vain-parse` (tai `python -m src.parse_media --tyot 1` jos snapshotteja puuttuu)
2. `python -m src.code_media`
3. `python -m src.analyze_media`
4. `python -m src.plot_media`
5. `python -m src.sensitivity_media`
6. `python -m src.m4_media`
7. `python -m src.threat_media`
8. `python -m src.pages`

CDX-indeksi: `python -m src.fetch_media`. Testit: `pytest tests/test_wilson.py tests/test_parse_media.py tests/test_code_media.py tests/test_analyze_media.py tests/test_sensitivity_media.py tests/test_m4_media.py tests/test_krippendorff.py tests/test_threat_media.py`.

---

## 10. TUTKIVA (ei esirekisteröity): peitto media × vuosi ja entiteetit vuodittain

Lähde: `coverage_media_vuosi.csv`, `p1_entiteetti_osuus.csv` (yksikkö = otsikko). Wilson 95 %. Puuttuva HTML ≠ nolla. HTML-päivät ovat osajoukko CDX-200-päivistä.

| media | vuosi | n_cdx_200 | n_html | n_otsikko_paiva | n_otsikkoa |
|---|---:|---:|---:|---:|---:|
| iltalehti_etusivu | 2015 | 113 | 41 | 41 | 3718 |
| iltalehti_etusivu | 2016 | 288 | 40 | 40 | 4994 |
| iltalehti_etusivu | 2017 | 277 | 171 | 171 | 20764 |
| iltalehti_etusivu | 2018 | 257 | 81 | 81 | 9396 |
| iltalehti_etusivu | 2019 | 290 | 88 | 88 | 2946 |
| iltalehti_etusivu | 2020 | 257 | 82 | 82 | 2976 |
| iltalehti_etusivu | 2021 | 221 | 65 | 65 | 1737 |
| iltalehti_etusivu | 2022 | 363 | 85 | 85 | 2388 |
| iltalehti_etusivu | 2023 | 363 | 84 | 84 | 1833 |
| iltalehti_etusivu | 2024 | 365 | 86 | 86 | 5730 |
| iltalehti_etusivu | 2025 | 365 | 90 | 90 | 5432 |
| yle_uutiset | 2015 | 276 | 1 | 1 | 102 |
| yle_uutiset | 2016 | 334 | 0 | 0 | 0 |
| yle_uutiset | 2017 | 341 | 229 | 229 | 2744 |
| yle_uutiset | 2018 | 339 | 91 | 91 | 946 |
| yle_uutiset | 2019 | 329 | 84 | 84 | 882 |
| yle_uutiset | 2020 | 298 | 90 | 90 | 1346 |
| yle_uutiset | 2021 | 334 | 106 | 106 | 306 |
| yle_uutiset | 2022 | 365 | 86 | 86 | 1000 |
| yle_uutiset | 2023 | 360 | 80 | 80 | 3424 |
| yle_uutiset | 2024 | 356 | 85 | 85 | 3698 |
| yle_uutiset | 2025 | 354 | 81 | 81 | 1496 |

Putin-merkkijono otsikoissa (P1, avain `putin`), vuodet joilla n&gt;0:

| media | vuosi | osuus (Wilson 95 %) |
|---|---|---|
| iltalehti_etusivu | 2015 | 27/3718 = 0,73 % (0,50–1,05 %) |
| iltalehti_etusivu | 2016 | 25/4994 = 0,50 % (0,34–0,74 %) |
| iltalehti_etusivu | 2017 | 134/20764 = 0,65 % (0,55–0,76 %) |
| iltalehti_etusivu | 2018 | 48/9396 = 0,51 % (0,39–0,68 %) |
| iltalehti_etusivu | 2019 | 9/2946 = 0,31 % (0,16–0,58 %), D&lt;10 |
| iltalehti_etusivu | 2020 | 8/2976 = 0,27 % (0,14–0,53 %), D&lt;10 |
| iltalehti_etusivu | 2021 | 9/1737 = 0,52 % (0,27–0,98 %), D&lt;10 |
| iltalehti_etusivu | 2022 | 135/2388 = 5,65 % (4,80–6,65 %) |
| iltalehti_etusivu | 2023 | 74/1833 = 4,04 % (3,23–5,04 %) |
| iltalehti_etusivu | 2024 | 121/5730 = 2,11 % (1,77–2,52 %) |
| iltalehti_etusivu | 2025 | 96/5432 = 1,77 % (1,45–2,15 %) |
| yle_uutiset | 2015 | 0/102 = 0,00 % (0,00–3,63 %), D&lt;10 |
| yle_uutiset | 2017 | 26/2744 = 0,95 % (0,65–1,38 %) |
| yle_uutiset | 2018 | 11/946 = 1,16 % (0,65–2,07 %) |
| yle_uutiset | 2019 | 3/882 = 0,34 % (0,12–1,00 %), D&lt;10 |
| yle_uutiset | 2020 | 7/1346 = 0,52 % (0,25–1,07 %), D&lt;10 |
| yle_uutiset | 2021 | 5/306 = 1,63 % (0,70–3,77 %), D&lt;10 |
| yle_uutiset | 2022 | 57/1000 = 5,70 % (4,43–7,31 %) |
| yle_uutiset | 2023 | 32/3424 = 0,93 % (0,66–1,32 %) |
| yle_uutiset | 2024 | 36/3698 = 0,97 % (0,70–1,34 %) |
| yle_uutiset | 2025 | 21/1496 = 1,40 % (0,92–2,14 %) |

Kaaviot: `06_entiteetti_vuosi.png` (kaikki P1-ryhmät paneeleina). Kuukausijaksot (`YYYY-MM`) ovat `p1_entiteetti_osuus.csv`:ssä; peitto kuukausittain on harvaa.

---

## 11. TUTKIVA (ei esirekisteröity): terveysuhka ja uhkakehys

Koodikirja `codebook_uhkakehys_v1.md`, lukittu ennen osuuslaskentaa. Yksikkö = havaittu etusivuotsikko. Puuttuva HTML ei ole nolla. Kaksi erillistä kenttää: terveysuhka (aihe) ja uhkakehys (kärjistys, aiheesta riippumatta). Tämä ei ole H4 eikä korvaa koodaus-v1:tä. Ihmiskoodausta ei ole.

Lähde: `uhkakehys_osuus.csv`. Wilson 95 %. D&lt;10 merkitty.

Havaittu jakso (tihennetty HTML):

| media | n | terveysuhka | uhkakehys |
|---|---:|---|---|
| iltalehti_etusivu | 61914 | 965/61914 = 1,56 % (1,46–1,66 %) | 534/61914 = 0,86 % (0,79–0,94 %) |
| yle_uutiset | 15944 | 557/15944 = 3,49 % (3,22–3,79 %) | 90/15944 = 0,56 % (0,46–0,69 %) |

Vuodet (terveysuhka | uhkakehys):

| media | vuosi | n | terveysuhka | uhkakehys |
|---|---|---:|---|---|
| iltalehti_etusivu | 2015 | 3718 | 7/3718 = 0,19 % (0,09–0,39 %), D&lt;10 | 22/3718 = 0,59 % (0,39–0,89 %) |
| iltalehti_etusivu | 2016 | 4994 | 4/4994 = 0,08 % (0,03–0,21 %), D&lt;10 | 35/4994 = 0,70 % (0,50–0,97 %) |
| iltalehti_etusivu | 2017 | 20764 | 20/20764 = 0,10 % (0,06–0,15 %) | 151/20764 = 0,73 % (0,62–0,85 %) |
| iltalehti_etusivu | 2018 | 9396 | 21/9396 = 0,22 % (0,15–0,34 %) | 108/9396 = 1,15 % (0,95–1,39 %) |
| iltalehti_etusivu | 2019 | 2946 | 2/2946 = 0,07 % (0,02–0,25 %), D&lt;10 | 42/2946 = 1,43 % (1,06–1,92 %) |
| iltalehti_etusivu | 2020 | 2976 | 537/2976 = 18,04 % (16,70–19,47 %) | 37/2976 = 1,24 % (0,90–1,71 %) |
| iltalehti_etusivu | 2021 | 1737 | 243/1737 = 13,99 % (12,44–15,70 %) | 23/1737 = 1,32 % (0,88–1,98 %) |
| iltalehti_etusivu | 2022 | 2388 | 103/2388 = 4,31 % (3,57–5,20 %) | 25/2388 = 1,05 % (0,71–1,54 %) |
| iltalehti_etusivu | 2023 | 1833 | 9/1833 = 0,49 % (0,26–0,93 %), D&lt;10 | 11/1833 = 0,60 % (0,34–1,07 %) |
| iltalehti_etusivu | 2024 | 5730 | 9/5730 = 0,16 % (0,08–0,30 %), D&lt;10 | 43/5730 = 0,75 % (0,56–1,01 %) |
| iltalehti_etusivu | 2025 | 5432 | 10/5432 = 0,18 % (0,10–0,34 %) | 37/5432 = 0,68 % (0,49–0,94 %) |
| yle_uutiset | 2015 | 102 | 1/102 = 0,98 % (0,17–5,35 %), D&lt;10 | 0/102 = 0,00 % (0,00–3,63 %), D&lt;10 |
| yle_uutiset | 2017 | 2744 | 4/2744 = 0,15 % (0,06–0,37 %), D&lt;10 | 16/2744 = 0,58 % (0,36–0,95 %) |
| yle_uutiset | 2018 | 946 | 4/946 = 0,42 % (0,16–1,08 %), D&lt;10 | 9/946 = 0,95 % (0,50–1,80 %), D&lt;10 |
| yle_uutiset | 2019 | 882 | 2/882 = 0,23 % (0,06–0,82 %), D&lt;10 | 2/882 = 0,23 % (0,06–0,82 %), D&lt;10 |
| yle_uutiset | 2020 | 1346 | 429/1346 = 31,87 % (29,44–34,41 %) | 13/1346 = 0,97 % (0,57–1,65 %) |
| yle_uutiset | 2021 | 306 | 47/306 = 15,36 % (11,75–19,83 %) | 1/306 = 0,33 % (0,06–1,83 %), D&lt;10 |
| yle_uutiset | 2022 | 1000 | 36/1000 = 3,60 % (2,61–4,94 %) | 3/1000 = 0,30 % (0,10–0,88 %), D&lt;10 |
| yle_uutiset | 2023 | 3424 | 22/3424 = 0,64 % (0,42–0,97 %) | 24/3424 = 0,70 % (0,47–1,04 %) |
| yle_uutiset | 2024 | 3698 | 7/3698 = 0,19 % (0,09–0,39 %), D&lt;10 | 18/3698 = 0,49 % (0,31–0,77 %) |
| yle_uutiset | 2025 | 1496 | 5/1496 = 0,33 % (0,14–0,78 %), D&lt;10 | 4/1496 = 0,27 % (0,10–0,69 %), D&lt;10 |

Kaaviot: `05_uhkakehys.png`, `07_uhkakehys_vuosi.png`, `08_uhkakehys_kuukausi.png` (TUTKIVA; kuukausissa vain n&gt;0).

---

## 12. Tulkinta ja rajat

Tämä osio on erillään tulosluvuista. Data tukee kuvauksia osuuksista **havaituissa** snapshotissa. Se ei tue motiiveja, lukijavaikutuksia, propaganda-väitettä eikä politiikkajohtopäätöstä.

Mitä luvut kuvaavat:

- Etusivupäivän Putin-osuus tarkoittaa, että kyseisenä arkistopäivänä vähintään yksi poimittu otsikko sisälsi avaimen `putin`. Otsikko-osuus on eri yksikkö (S1).
- H1:n 56 % on 47 päivää 84:stä Iltalehden 2023-snapshotista, ei osuus kaikista vuoden 2023 päivistä.
- H5:n korrelaatio on kuuden osuuden välinen, kahdella medialla. Se ei ole maiden vertailu eikä todiste samasta toimituksellisesta linjasta.
- M4: K1:n 12 % on tuomioiden NAT/FOR-jakauma Suomessa kolmelta vuodelta. Median 0/87 on lukittujen merkkijonojen osuma rikosotsikoissa. Nämä eivät ole sama satunnaismuuttuja.
- Ihmiskoodauksen puute rajaa sävyn, aiheen ja H4/H7-pään.
- TUTKIVA uhkakehys on merkkijono-osuma. Se ei ole validoitu H4. Se ei osoita “pelon lietsontaa tarkoituksella”.
- Ennakkohypoteesi “Putin ei trendannut 2019–2021”: havaituissa Iltalehti-otsikoissa Putin-osuus oli 2019–2021 noin 0,3–0,5 % (D&lt;10 osumissa) ja 2022–2023 noin 4–6 %. Ylellä 2022 oli korkea (~5,7 %), 2019–2020 matala; 2021:n n on pieni. Tämä on osittaista peittoa (HTML ≪ CDX), ei kalenterivuoden täysi otos. Ei syy-yhteyttä tapahtumiin ilman erillistä indikaattoria (P5).
- Terveysuhka-avaimet nousivat 2020–2021 (korona-sanat lukitussa listassa). Uhkakehys-osuus pysyi matalana (~0,5–1,5 %) useimpina vuosina havaituissa otsikoissa; kuukausipeitto on edelleen harvaa, joten “joka kuukausi samanlaista” ei ole testattavissa täytenä kausivaihteluna.

Mitä jää avoimeksi: täysi HTML-peitto (erityisesti Yle 2016 ja loput CDX-200-päivät), kaksi ihmiskoodaajaa, julkaisijan analytiikka (H3), ulkoiset tapahtumaindikaattorit, muut mediat ja 2000–2014.
