# Esirekisteröinti, mediahaara (lukitaan ennen datan hakua)

Päivämäärä: 2026-11-01

Tämä haara on erillinen K1:stä. Media- ja rikostilastoa ei yhdistetä ennen
vaihetta 7 (`MEDIA_CURSOR_TASKS.md`). Tätä päivämäärää ennen ei ole haettu
media-aineistoa.

## Kysymykset (MEDIA_README.md)

- **M1 (näkyvyys):** osuus etusivuista/kansista ja otsikoista, joissa esiintyy
  tietty henkilö, aihe tai kehys; muutos ajassa.
- **M2 (suhteutus tapahtumiin):** seuraako näkyvyys ulkoisia indikaattoreita
  vai poikkeaako.
- **M3 (kehys ja sävy):** otsikoiden tunnesävy mediasta ja aiheesta toiseen.
- **M4 (media vs. tilasto):** rikosuutisten kansalaisuusmaininnat vs. K1.
  Ei ennen vaihetta 7.
- **M5 (vertailu):** erot medioiden ja maiden välillä.

## Hypoteesit H1–H7

Muotoilu: `MEDIA_README.md` §3. Esimerkkitekstin luvut (87 %, 252, 3–7×)
eivät ole lähde; ne todennetaan aineistosta tai merkitään puuttuviksi.

- **H3:** ei testattavissa ilman julkaisijan analytiikkaa. Ellei analytiikkaa
  ole, tulos = ei testattavissa (NaN), ei arvausta.
- Goebbels-sitaattia ei käytetä lähteenä ilman alkuperäisviitettä.

## Rajaukset

- Puuttuva päivä tai otsikko = puuttuva, ei täyttöä.
- Kaikki valitut mediat ja kaikki päivät raportoidaan; ei kirsikanpoimintaa.
- Otsikot ja URL:t; kokoteksti vain julkaisijan ehdoin.
- Tulkinta erilliseen osioon. Ei motiiveja, ei lukijavaikutuksia, ei
  propaganda-väitettä ilman erillistä näyttöä.

## Tulosmuuttujat (lukitaan menetelmässä ennen analyysiä)

Osuudet Wilson-väleineen; sävy- ja aiheluokat koodikirjan mukaan;
koodaajien välinen yhtäpitävyys (Krippendorff α) ihmisotokselle (≥500).

Herkkyydet S1–S7 määritellään `MEDIA_METHODS.md`:ssä ennen vaihetta 5.
Niitä ei keksitä tuloksen perusteella.
