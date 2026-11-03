# Koodikirja koodaus-v1 (vaihe 4)

Lukittu ennen otoksen koodausta. Ihmiskoodaus: `media/CODEBOOK.md`
(lomakkeet, α, H4/H6). Tämä tiedosto = sääntöavaimet saanto-v1/v1b.
Yksikkö: yksi etusivuotsikko (`tietueet_otsikko.csv`).

## Otos

- Koko ≥ 500. Siemen `20261103`. Tasakiintiö medioittain (250 + 250).
- Vain rivit, joissa `otsikko` ei ole tyhjä. Puuttuvaa otsikkoa ei keksitä.
- Kaksoiskoodaus: kaksi **sääntökoodaajaa** koko otokselle (`saanto-v1`,
  `saanto-v1b`). Ihmiskentät `aihe_ihminen_*` / `savy_ihminen_*` tyhjiä.
- Ihmis-α = tyhjä, kunnes kaksi ihmistä koodaa saman otoksen.

## Aihe (yksi luokka / otsikko)

Järjestys (ensimmäinen osuma voittaa): `putin`, `zelenskyi`, `presidentti`,
`maahanmuutto`, `rikollisuus`, `terveys`, muuten `muu`.

Osuma = merkkijono otsikon pienaakkosissa (kuten vaihe 3).

### saanto-v1 (MEDIA_README M1)

| Luokka | Avaimet |
|---|---|
| putin | putin |
| zelenskyi | zelenskyi, zelenskyy, zelenskiy, zelensky, zelenski |
| presidentti | tasavallan presidentti, suomen presidentti |
| maahanmuutto | maahanmuutto, pakolais, siirtolais |
| rikollisuus | rikollis, rikos, tuomittu, tuomitut |
| terveys | terveysuhka, epidemia, pandemia |
| muu | ei osumaa |

`presidentti` ei täyty pelkästä sanasta "presidentti" (liian lavea; vain M1:n
kaksi fraasia).

### saanto-v1b (taivutus, lukittu tässä)

Sama järjestys. Avaimet = v1 **plus**:

| Luokka | Lisäavaimet |
|---|---|
| presidentti | presidentti niinistö, presidentti stubb, tasavallan pres. |
| maahanmuutto | turvapaikka, maahanmuuttaja, pakolainen |
| rikollisuus | syytteeseen, henkirikos, rikosepäily |
| terveys | koronavirus, covid |

Ei rikoslajeja (esim. raiskaus) ilman M1-listaa.

## Sävy (M3)

Luokat: `uhka`, `pelko`, `viha`. Tyhjä = ei merkkiosumaa, **ei** `neutraali`
(neutraali vain ihmiskoodauksessa). Järjestys: uhka > pelko > viha.

### saanto-v1

| Luokka | Avaimet |
|---|---|
| uhka | uhka, uhkail |
| pelko | pelko, pelott |
| viha | viha, vihain |

### saanto-v1b

v1 plus:

| Luokka | Lisäavaimet |
|---|---|
| uhka | hyökkäys, terrori, pommi-isku |
| pelko | kauhu, paniikki |
| viha | raivo, vihamiel |

Sota/kuolema eivät ole sävyavaimia (aihe voi olla muu; sävy vaatii M3-sanan).

## Koodaajat

| Tunnus | Rooli |
|---|---|
| saanto-v1 | sääntö, koodikirja-v1 |
| saanto-v1b | sääntö, laajennuslistat |
| ihminen | tyhjä tässä ajossa |

`koodakirja_versio=koodaus-v1`.

## Yhtäpitävyys

Krippendorffin α (nominaali, kaksi koodaajaa). Puuttuva sävy jätetään α:sta
pois (pari, jossa jompikumpi tyhjä). Aiheessa `muu` on luokka, ei puuttuva.

Tarkkuus/saanti/F1: saanto-v1b vs. viite saanto-v1, merkitään
`TUTKIVA (ei esirekisteröity)` — ei ihmisvalidointia.
