# CODEBOOK — mediaotsikoiden ihmiskoodaus

Versio: koodaus-v1 (ihmiskentät). Lukittu `MEDIA_PREREGISTRATION.md`
lisäyksessä 2026-11-03 **ennen** ihmiskenttien täyttöä.

Sääntökoodauksen avaimet: `media/codebook_koodaus_v1.md` (saanto-v1 / v1b).
Tämä tiedosto ohjaa **ihmiskoodaajia** A ja B.

## Yksikkö

Yksi etusivuotsikko (`koodaus_otos.csv` / lomake `koodaus_lomake_*.csv`).
Älä koodaa kokotekstiä. Älä täytä puuttuvaa otsikkoa.

## Otos

- N = 500, siemen `20261103`, 250 Iltalehti + 250 Yle.
- Kaksoiskoodaus: koko otos, itsenäisesti (ei keskustelua ennen α-laskentaa).
- Kentät: `aihe_ihminen_a|b`, `savy_ihminen_a|b`, `koodaaja_ihminen_a|b`.

## Aihe (yksi luokka)

Sallitut: `putin` | `zelenskyi` | `presidentti` | `maahanmuutto` |
`rikollisuus` | `terveys` | `muu`.

Ensimmäinen sopiva luokka voittaa (sama järjestys kuin saanto-v1).
`presidentti` = Suomen tasavallan presidentti / nimetty presidentti Suomessa;
pelkkä sana “presidentti” muussa maassa → yleensä `muu` ellei selvästi FI.
Epäselvä → `muu` + lyhyt muistiinpano lomakkeeseen.

## Sävy (M3; H4 edellyttää tätä)

Sallitut: `uhka` | `pelko` | `viha` | `neutraali`.

- Koodaa otsikon **sävy**, ei aiheen vakavuutta (sota ≠ automaattisesti uhka).
- Jos sävyä ei ole pääteltävissä otsikosta → `neutraali` (ihminen; sääntö
  jättää tyhjäksi).
- H6 (tuho vs. tuhoutuminen): erillinen kenttä vasta kun α hyväksytty;
  toistaiseksi H6 = ei testattavissa.

## Kieltoja

- Älä päättele motiivia, propagandaa tai lukijavaikutusta.
- Älä käytä Goebbels-sitaattia ohjeena.
- LLM/agentti ei täytä ihmiskenttiä.

## Yhtäpitävyys ja LLM

Krippendorff α (nominaali). Kynnykset: `MEDIA_PREREGISTRATION.md`
(0,80 / 0,67). LLM tai sääntö koko aineistoon vain validoituna
ihmiskonsensusta vasten (tarkkuus, saanti, F1 per luokka).

## H3 / H4 / H6

| H | Tila kunnes… |
|---|---|
| H3 | julkaisijan klikkianalytiikka saatavilla → muuten `ei_testattavissa` |
| H4 | ihmis-sävy aikasarjana hyväksytyn α:n jälkeen |
| H6 | tuho/tuhoutuminen-luokat + ihmiskoodaus |
