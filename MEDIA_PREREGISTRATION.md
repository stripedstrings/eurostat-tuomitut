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
- **H4 ja H6:** ei testattavissa ennen ihmiskaksoiskoodauksen valmistumista
  (sävy / tuho–tuhoutuminen). Siihen asti tila = `ei_testattavissa`, ei
  avainsanaosuutta H4/H6:n tilalle.
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

---

## Lisäys 2026-11-03: ihmiskoodaus ja mediaexpansio (ennen koodausta)

Lukittu ja commitoitu **ennen** ihmiskoodauksen täyttöä. Poikkeama
alkuperäisestä 2026-11-01-päivästä: vaiheiden 1–8 aineistoa on jo haettu
(`CHANGELOG.md`); tämä lisäys lukitsee vain koodausprotokollan ja
lisämediat, ei avaa uudelleen M1–M5-kysymyksiä.

### Koodausotos

| Parametri | Lukittu arvo |
|---|---|
| Otoksen koko | **N = 500** otsikkoa (tasakiintiö: 250 Iltalehti + 250 Yle) |
| Kehikkopopulaatio | `tietueet_otsikko.csv`, vain ei-tyhjät `otsikko` |
| Siemen | `20261103` (sama kuin olemassa oleva `koodaus_otos.csv`) |
| Koodikirja | `media/CODEBOOK.md` (= `codebook_koodaus_v1.md` + ihmiskentät) |
| Kaksoiskoodaus | **100 %** otoksesta: kaksi itsenäistä ihmiskoodaajaa |
| Yksikkö | yksi etusivuotsikko |

### Koodaajat

| Tunnus | Rooli | Tila |
|---|---|---|
| `ihminen-A` | ensisijainen ihmiskoodaaja | nimetään ennen täyttöä; ei agentti |
| `ihminen-B` | toinen ihmiskoodaaja (riippumaton) | nimetään ennen täyttöä; ei agentti |
| `saanto-v1` / `saanto-v1b` | merkkijonosäännöt (ei korvaa ihmistä) | jo ajettu otokselle |

Agentti tai LLM **ei** täytä `aihe_ihminen_*` / `savy_ihminen_*` -kenttiä.

### Alfa-tavoite (Krippendorff α, nominaali)

| Kynnys | Seuraus |
|---|---|
| α ≥ **0,80** | hyväksytään; erimielisyydet sovitetaan; LLM-validointi sallittu |
| 0,67 ≤ α < 0,80 | alustava; raportoidaan varauksin; LLM vain TUTKIVA |
| α < **0,67** | ei automaattista koodausta koko aineistoon; koodikirjaa tarkennetaan |

α lasketaan aiheelle ja äänelle erikseen. Puuttuva sävy (ei luokkaa) jätetään
α-parin ulkopuolelle, jos jompikumpi koodaaja jättää tyhjäksi *ennen*
sovitusta. Sovituksen jälkeen jokaisella rivillä on yksi konsensusluokka
tai dokumentoitu `erimielisyys`.

### LLM- / sääntökoodaus

LLM tai sääntölaajennus koko aineistoon **vain**, jos:

1. ihmis-α täyttää yllä olevan kynnyksen, ja
2. validointi ihmiskonsensusta vasten raportoi **tarkkuus, saanti ja F1
   per luokka** (aihe ja sävy erikseen).

Ilman tätä validointia automaattikoodia ei viedä pääanalyysiin.

### Lisättävät mediat (ennen uutta CDX/HTML-hakua)

Nykyiset: `iltalehti_etusivu` (kaupallinen iltapäivälehti), `yle_uutiset`
(julkinen palvelu).

| Media | Perustelu (M5) |
|---|---|
| **Helsingin Sanomat** (`hs_etusivu`) | Suomen suurin tilattava sanomalehti; laadukkaan lehdistön vertailukohta IL/Yle-parille |
| **MTV Uutiset** (`mtv_uutiset`) | Kaupallinen TV-/verkkomedia; toinen kaupallinen kanava ilman iltapäivälehtiformaattia |

Ei vielä haeta tässä commitissa. Haku vasta tämän lisäyksen commitin jälkeen
(`media.mdc`). Maiden välinen vertailu (muu EU) ei kuulu tähän lisäykseen.

### Peitto

Coverage-matriisi **media × vuosi** (CDX vs. HTML) raportoidaan; aukot
jätetään tyhjiksi / NaN, ei täytetä nolliksi osuuslaskennassa.

### Hub-aikajana

`docs/tutkimus/aikajana.html` voi näyttää mediaosuuden rinnakkain muiden
haarojen kanssa. **Sivua ei käytetä päättelyyn** (ks. myös
`PREREGISTRATION.md`). Ei korrelaatioita media↔K1.
