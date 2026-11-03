# Mediahaaran tehtävälista Cursorille

Noudata .cursor/rules/project.mdc ja .cursor/rules/media.mdc.
Pysähdy jokaisen vaiheen jälkeen, tulosta yhteenveto ja odota hyväksyntää.

## Vaihe 0: Esirekisteröinti
- Täytä päivämäärä MEDIA_PREREGISTRATION.md:hen, commit ENNEN datan hakua.

## Vaihe 1: Lähteiden selvitys
- Selvitä, mitkä lähteet ovat oikeasti saatavilla (Wayback CDX, Yle API,
  GDELT, Media Cloud, RSS). Testaa pienellä näytteellä. Raportoi
  kattavuus, ehdot, rajoitteet. Älä arvaa.
- Päivitä MEDIA_DATA_SOURCES.md.

## Vaihe 2: Haku
- src/fetch_media.py: hae etusivut/otsikot valituille medioille koko ajalta.
  Välimuisti, MANIFEST.csv. Älä täytä aukkoja.
- Coverage matrix: media x päivä (mitä on, mitä puuttuu).

## Vaihe 3: Esikäsittely
- Poimi otsikot, kuvatekstit, entiteetit (nimi/kuva). Tallenna jäsennetty
  tietue koodikirjan kentillä.

## Vaihe 4: Koodaus
- Ihmiskoodauksen otos (≥500), kaksoiskoodaus, Krippendorff alfa.
- Mahdollinen automaattinen koodaus validoidaan ihmisotosta vasten ja
  raportoidaan tarkkuus/saanti/F1 luokittain. Kirjaa koodaaja ja versio.

## Vaihe 5: Analyysi P1–P5
- Entiteettiosuudet ja Wilson-luottamusvälit, aiheosuudet, sävy ajassa,
  mediavertailu, suhde ulkoisiin indikaattoreihin.
- H1–H7 testataan MEDIA_README.md:n mukaan. Ei testattavat merkitään.

## Vaihe 6: Herkkyysanalyysit S1–S7
- Taulukko: pääanalyysi vs. jokainen S.

## Vaihe 7: M4 (media vs. tilasto)
- Yhdistä rikosuutiskoodaus pääprojektin kansalaisuusdataan. Vertaa
  uutisissa mainitun kansalaisuuden jakaumaa tilastoon (K1) varoituksin:
  uutiskynnys, tilaston laskentayksiköt, otoskoko.

## Vaihe 8: Raportti
- media/output/RAPORTTI_MEDIA.md: tulokset kuvineen, kaikki mediat, kaikki
  jaksot, epävarmuudet. Erillinen "Tulkinta ja rajat" -osio.
- Lukijalle: miten toistaa (komennot, data).
- Ajettu 2026-11-03.
