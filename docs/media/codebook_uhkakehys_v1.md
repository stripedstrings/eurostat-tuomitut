# Koodikirja uhkakehys-v1 (TUTKIVA)

Ei esirekisteröity. Ei korvaa `koodaus-v1`:tä eikä H4:ää.
Avaimet lukittu tässä ennen osuuslaskentaa. Ei ihmiskoodausta.

Yksikkö: etusivuotsikko (`tietueet_otsikko.csv`). Puuttuva HTML = ei riviä.

## Kentät (erilliset)

| Kenttä | Kyllä jos |
|---|---|
| terveysuhka | vähintään yksi terveysavain |
| uhkakehys | vähintään yksi kehysavain |

Ristiin: `molemmat`, `vain_terveys`, `vain_kehys`, `ei_kumpaakaan`.
Tyhjä otsikko ei saa luokkaa (ei täyttöä).

## Terveysuhka (aihe)

Osuma pienaakkosissa:

`terveysuhka`, `epidemia`, `pandemia`, `koronavirus`, `korona`, `covid`,
`influenssa`, `tartunta`, `rokote`, `tehohoito`, `kuolemaan johtav`

Ei pelkkää `virus`. Ei `maahanmuuttaja`.

`korona` yksin = terveysuhka, ei uhkakehys.

## Uhkakehys (kärjistys, aiheesta riippumatta)

`tappaa`, `tuhoaa`, `tuhoisa`, `katastrofi`, `hengenvaara`, `tunkeutu`,
`kaapata`, `romahdus`, `kaaos`, `paniikki`, `pelottel`, `voi tappaa`,
`kaikki kuol`

## Koodaaja

`koodaaja=saanto-uhkakehys-v1`, `koodakirja_versio=uhkakehys-v1`.
