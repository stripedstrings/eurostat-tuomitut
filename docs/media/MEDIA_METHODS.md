# Mediahaaran menetelmät

Vaihe 1 (saatavuus) 2026-11-01. Vaihe 2 (CDX-indeksi) 2026-11-02.
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

## Koodikirjan kentät (tyhjä aineisto)

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

Koodaussäännöt ja ihmisotos (≥500, kaksoiskoodaus, Krippendorff α)
vaiheessa 4. Automaattinen koodaus vain, jos se validoidaan otosta vasten
(tarkkuus/saanti/F1 luokittain).

## P1–P5 ja H1–H7

Analyysi vaiheessa 5. Ei testattavat (esim. H3 ilman analytiikkaa)
merkitään. S1–S7 taulukko vaiheessa 6; määritellään ennen vaihetta 5.

## M4

Vasta vaihe 7. Uutiskynnys, tilaston laskentayksikkö ja otoskoko
varoitusina. Ei syy-yhteyttä.
