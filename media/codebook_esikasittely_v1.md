# Koodikirja esikäsittely-v1 (vaihe 3)

Ei ihmiskoodausta. `aihe` ja `savy` tyhjiä (vaihe 4).

## Yksiköt

- `tietueet_etusivu.csv`: yksi rivi / media / kalenteripäivä 2015–2025, myös ilman snapshotia.
- `tietueet_otsikko.csv`: yksi rivi / poimittu etusivuotsikko. Päivää ilman HTML:ää ei keksitä.

## Otsikon poiminta

HTML Wayback-snapshotista (`on_cdx` ja tiedosto levyllä):

- luokat täysi tokeni: `otsikko`, `headline`, `article-title`, `front-title`,
  `a-title-font`, `latest-pala-title`, `big-title`, `newsticker-title-text`
- ei osamerkkijonoa (`MinimalHeadlines` ≠ `headline`)
- `h1`–`h3`, pituus 18–180
- pois: `saa_otsikko`, `list-title`, `vignette`, navigaatiotekstit (`Pääuutiset`, `Lisää aiheesta`, …)

Sivun `<title>` / `og:title` ei ole uutisotsikko (brändi).

## Kuvateksti ja kuva

- `kuvateksti`: ensimmäinen `figcaption`, jos pituus ≥ 8 eikä navigaatiota
- `kuva_url`: `og:image` tai `twitter:image` (usein brändikuva)

## Entiteetti

Merkkijono-osuma otsikoissa, avaimet `MEDIA_README.md` M1:stä
(putin, zelensky*, tasavallan/suomen presidentti, maahanmuutto, pakolais,
siirtolais, rikollis/rikos, tuomittu*, terveysuhka, epidemia, pandemia).
Ei kehystä eikä sävyä. Tyhjä = ei osumaa, ei “ei esiintynyt ihmiskoodauksessa”.

`koodaaja=kone`, `koodikirja_versio=esikasittely-v1`.
