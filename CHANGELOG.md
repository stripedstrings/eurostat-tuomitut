# Muutosloki
Kirjaa tähän jokainen poikkeama PREREGISTRATION.md:stä: pvm, muutos, perustelu,
tehtiinkö ennen vai jälkeen tulosten näkemisen.

- 2026-11-01. Esirekisteröinti täytetty. **Poikkeama:** ennen tätä päivää on
  ajettu tutkiva visualisointi (`crim_just_ctz`, `migr_pop5ctz`: asteet,
  suhdeluvut, kaaviot, GitHub Pages) ilman lukittua esirekisteröintiä.
  K1:n suunta on siis jo nähty. Esirekisteröinti ei ole sokko. Perustelu:
  työ alkoi visualisointina; tutkimusprotokolla tuotiin mukaan jälkikäteen.
  Aiempi sivusto merkitään tutkivaksi (`docs/`). Jatkossa noudatetaan
  `PREREGISTRATION.md`:tä; uudet analyysit (Poisson-CI, SIR, S1–S7)
  kirjataan erikseen.

- 2026-11-01. GitHub Pages -etusivu (`docs/index.html`) on esirekisteröity
  raportti (`output/RAPORTTI.md` ja `output/figures/01`–`09`). Tutkiva
  visualisointi on merkitty TUTKIVA-nauhaalla; Suomi on `docs/maat/fi.html`.
  Perustelu: etusivu ei saa näyttää tutkivaa visualisointia rekisteröidyn
  raportin sijaan.

- 2026-11-01. Raportin etusivulle palautettu maavalikko ja FI/EN-liput.
  Maasivut ovat edelleen merkitty tutkiviksi. Kaaviot pysyvät suomenkielisinä.

- 2026-11-01. Mediahaara esirekisteröity (`MEDIA_PREREGISTRATION.md`) ennen
  datan hakua. Sivustolle välilehdet Maahanmuutto ja Media. Media-lähteitä
  ei ole testattu (vaihe 1). K1:tä ei yhdistetä mediaan.

- 2026-11-01 (vaihe 1). Lähteet testattu pienellä näytteellä.
  `MEDIA_DATA_SOURCES.md`. Ei koko-arkistoa. GDELT 429; Media Cloud API
  ei DNS:ää; Yle-artikkeli-API ei julkinen.

- 2026-11-02 (vaihe 2, ennen otsikkopoimintaa). CDX-peitto on kalenteripäivän
  ensimmäinen osuma (`collapse=timestamp:8`), ei kaikkien snapshotien lista
  eikä täyttö. Perustelu: Poisson/osuuslaskenta tulee päiväyksikölle;
  puuttuva päivä jää tyhjäksi. HTML:ää ei ladattu (vaihe 3).

- 2026-11-03 (TUTKIVA, uhkakehys). Uusi koodikirja terveysuhka vs. uhkakehys
  merkkijono-osumina kaikille havaituille otsikoille. Ei korvaa H4:ää eikä
  koodaus-v1:tä. Avaimet lukittu `codebook_uhkakehys_v1.md`:ään ennen
  osuuslaskentaa. Perustelu: esirekisteröity sävy ei kata kärjistettyä
  vaarakieltä. Merkitään tutkivaksi.

- 2026-11-03 (vaihe 8). `media/output/RAPORTTI_MEDIA.md`: tulokset erillään
  osiosta Tulkinta ja rajat. Ei uusia lukuja; ei menetelmän vaihtoa.

- 2026-11-03 (vaihe 7). M4: rikosotsikon NAT/FOR-avaimet vs. K1 FI tuomitut
  yhteisillä vuosilla. Demonyymejä ei keksitty. Maahanmuuttaja-avainta ei
  käytetty (tausta ≠ kansalaisuus). EU-aggregaattia ei yhdistetty. Ei syytä.

- 2026-11-03 (vaihe 6). S1–S7 kuten METHODS ennen vaihetta 5. S4 vain
  otoksessa 500 (ruudukon `aihe` tyhjä). S5-täyttö merkitty tutkivaksi.
  Ei M4. Perustelu: määritelmät lukittu ennen P1-lukuja.

- 2026-11-03 (vaihe 5, ennen S1–S7). P1 käyttää vaihe 3 -entiteettiosumia,
  ei ihmiskoodausta. Nimittäjä = havaittu HTML, ei kalenteri. H3/H4/H6 ja
  H7-pää, P2-pää, P3, P5 merkitty ei testattaviksi aineiston vuoksi, ei
  tuloksen vuoksi. M4 ei. Perustelu: METHODS ennen ajoa.

- 2026-11-03 (vaihe 4, ennen P1–P5). Esirekisteröinti vaatii ihmiskoodauksen
  (≥500, kaksoiskoodaus, Krippendorff α). **Poikkeama:** kahta ihmiskoodaajaa
  ei ole. Otos 500 (siemen 20261103) koodattiin kahdella lukitulla säännöllä;
  ihmiskentät tyhjiä; ihmis-α tyhjä. Sääntö-α/F1 merkitään tutkiviksi.
  Perustelu: koodeja ei keksitä ihmisen nimissä. Automaatiota ei validoida
  ilman ihmisviitettä.

- 2026-11-02 (vaihe 3, ennen ihmiskoodausta). Wayback-HTML haettu osittain;
  Internet Archive katkaisi rinnakkaiset yhteydet. Puuttuvat päivät jätettiin
  tyhjiksi. Otsikot konepoiminnalla; `aihe`/`savy` tyhjiä. Perustelu:
  esikäsittely ei täytä aukkoja eikä koodaa sävyä. IL 2023-HTML:ssä ei
  `h1`/`otsikko`; luokat luettu snapshotista (`front-title` ym.).

- 2026-11-01 (vaihe 4, ennen kaavioiden piirtoa). Forest-kaavion 2020–2024-RR
  on yhteenlaskettu kelpoisista vuosista (summa osoittajista ja nimittäjistä),
  ei aritmeettinen keskiarvo vuosittaisista RR-luvuista. Perustelu: Poisson-CI
  määritellään lukumäärille; puuttuvia vuosia ei täytetä. Tutkiva `docs/`-sivusto
  käytti vuosiasteiden keskiarvoa.
