# Mediahaaran menetelmät

Vaihe 1 (saatavuus) 2026-11-01. Vaihe 2 (CDX-indeksi) 2026-11-02.
Vaihe 3 (HTML-otsikot) 2026-11-02. Vaihe 4 (koodausotos) 2026-11-03.
Vaihe 5 (P1–P5, H1–H7) 2026-11-03.
Tätä ei muuteta tuloksen perusteella; poikkeamat `CHANGELOG.md`:hen.

## Yksikkö ja jakso (vaihe 2)

- Kalenteri: 2015-01-01 … 2025-12-31 (H7). Jokainen päivä rivi, myös puuttuvat.
- Mediat (vain vaiheessa 1 vastanneet URL:t): `iltalehti_etusivu` =
  `www.iltalehti.fi/`, `yle_uutiset` = `yle.fi/uutiset`.
- Wayback CDX, `collapse=timestamp:8` (ensimmäinen osuma kalenteripäivältä).
  Ei interpolointia. Päivä ilman CDX-riviä: `on_cdx=False`.
- `on_cdx_200`: sama, suodatin `statuscode:200`.
- RSS haetaan vain hakupäivältä; sitä ei kopioida tyhjiin historiapäiviin.
- Etusivujen HTML-snapshotteja ei ladattu vaiheessa 2 (otsikot = vaihe 3).
- GDELT, Media Cloud, Yle-artikkeli-API: ei haussa (vaihe 1).

## Esikäsittely (vaihe 3)

- Snapshot-URL = CDX-päivän ensimmäinen osuma. Ei id_-moodia (redirect-silmukka).
- Otsikot: HTML-luokan täysi tokeni (`otsikko`, `headline`, `article-title`,
  IL 2023 `front-title` / `a-title-font` / `latest-pala-title` / `big-title` /
  `newsticker-title-text`) ja `h1`–`h3`.
  Ei `<title>` / `og:title`. Ei osamerkkijonoa (`MinimalHeadlines` ≠ `headline`).
  Luokat luettu snapshotista.
- Kuvateksti: ensimmäinen `figcaption`. Kuva: `og:image`.
- Entiteetti: merkkijono-osuma M1-avaimista; ei ihmiskoodaus.
- `aihe`, `savy`, ihmis-`koodaaja` tyhjiä vaiheessa 3.
- Puuttuva HTML tai tyhjä poiminta = tyhjä, ei interpolointia.
- IA-rajoitus: HTML-kattavuus < CDX-kattavuus; katkos = puuttuva.

## Koodaus (vaihe 4, 2026-11-03)

- Koodikirja: `media/codebook_koodaus_v1.md`. Siemen `20261103`.
- Otos: 500 otsikkoa, 250 / media, vain ei-tyhjät otsikot.
- Sääntökoodaus `saanto-v1` ja `saanto-v1b` koko otokselle.
- Ihmiskoodaus: kentät tyhjiä (kaksi ihmistä puuttuu).
- Krippendorffin nominaali-α: `src/krippendorff.py`. Ihmis-α tyhjä.
- Sääntöjen välinen α ja F1 merkitään tutkiviksi; ei ihmisvalidointia.
- Sävy ilman merkkiosumaa = tyhjä, ei `neutraali`.
- Automaattista koodausta ei viedä koko aineistoon ennen ihmisotosta.

## Koodikirjan kentät (esikäsittely-v1)

| Kenttä | Sisältö |
|---|---|
| media | julkaisijan tunnus |
| url | lähdeosoite |
| paiva | kalenteripäivä |
| otsikko | otsikkoteksti |
| entiteetti | nimi tai kuva (koodattu) |
| aihe | aiheluokka (koodattu) |
| savy | sävyluokka (koodattu) |
| koodaaja | tunniste |
| koodikirja_versio | versio |

Koodaussäännöt: `media/codebook_koodaus_v1.md`. Ihmisotos (≥500) odottaa
kahta koodaajaa. Automaattinen koodaus ei ole validoitu ihmistä vasten.

## P1–P5 ja H1–H7 (vaihe 5, lukittu ennen ajoa)

Nimittäjä = havaitut HTML-etusivut (`n_otsikkoa` > 0) tai otsikot. Puuttuva
HTML ei ole nollaosuus. Wilson 95 % (`src/wilson.py`, z = scipy `norm.ppf(0.975)`).
D<10 merkitään. Molemmat mediat, kaikki vuodet joissa n>0.

- **P1:** entiteettiosuudet (vaihe 3 -avaimet, ryhmät: putin, zelenskyi,
  presidentti, maahanmuutto, rikollisuus, terveys). Etusivu ja otsikko
  rinnakkain.
- **P2:** aiheluokka. Pääanalyysi = ei testattavissa (ihmisaihe tyhjä;
  sääntöaihetta ei viety ruudukkoon). Otos 500 = TUTKIVA.
- **P3:** sävy ajassa. Ei testattavissa (ihmissävy tyhjä; sääntöä ei
  aikasarjana).
- **P4:** mediavertailu, P1-osuudet IL vs. Yle. Pearson-r kuuden
  entiteettiosuuden vektoreille (otsikko).
- **P5:** suhde ulkoisiin indikaattoreihin. Ei testattavissa (indikaattoreita
  ei haettu; M4 = vaihe 7).

| H | Pääanalyysi |
|---|---|
| H1 | IL 2023, putin, etusivu (ja otsikko rinnakkain), Wilson |
| H2 | samat nimittäjät: presidentti vs. putin vs. zelenskyi (lkm + osuus) |
| H3 | ei testattavissa |
| H4 | ei testattavissa |
| H5 | Pearson-r (P4) |
| H6 | ei testattavissa (ei tuho/tuhoutuminen-koodia) |
| H7 | ei testattavissa (ei aihekoodia 2015–2025). TUTKIVA: entiteetti+muu-entropia vuosittain, n>0 |

## Herkkyydet S1–S7 (lukittu ennen vaihetta 5)

Taulukko vaiheessa 6. Määritelmät eivät riipu P1–P5-luvuista.

- **S1:** otsikkoyksikkö (pää) vs. etusivupäivä (≥1 koodattu otsikko).
- **S2:** IL ja Yle erikseen (pääanalyysi pitää molemmat).
- **S3:** saatavilla oleva jakso vs. vain 2023.
- **S4:** vaihe 3 -entiteettiosuma vs. koodattu `aihe`.
- **S5:** sävy vain merkitty vs. tutkiva täyttö tyhjä→`neutraali` (ei pää).
- **S6:** otsikon pituus ≥ 18 (pää, poiminta) vs. ≥ 40.
- **S7:** Wilson 95 % vs. Clopper–Pearson 95 %.

## M4

Vasta vaihe 7. Uutiskynnys, tilaston laskentayksikkö ja otoskoko
varoitusina. Ei syy-yhteyttä.
