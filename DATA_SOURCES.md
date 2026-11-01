# Datalähteet ja datasanakirja

Koodit on luettu Eurostat SDMX-CSV:stä (`python -m src.fetch`, 2026-11-01).
Koodeja ei ole keksitty. Täydet unique-listat: `data/interim/dimensiot_*.txt`.

API (SDMX 2.1, CSV):
`https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/<koodi>?format=SDMX-CSV`

Windows-haku: `curl.exe -fsSL` (`src/fetch.py`), koska Pythonin SSL ei löytänyt CA-ketjua.

## Eurostat — vaiheen 1 aineistot

### crim_just_ctz — Suspects and offenders by citizenship

| | |
|---|---|
| Rivimäärä | 7 801 |
| LAST UPDATE | 29/04/26 11:00:00 |
| Välimuisti | `data/raw/crim_just_ctz.csv` (644 113 t) |

Sarakkeet: `DATAFLOW`, `LAST UPDATE`, `freq`, `leg_stat`, `citizen`, `unit`, `geo`, `TIME_PERIOD`, `OBS_VALUE`, `OBS_FLAG`, `CONF_STATUS`.

**Ei saraketta `sex` eikä `age`.** Rikostilastoa ei voi vakioida iän tai sukupuolen mukaan tästä datasetistä.

| Dimensio | Arvot |
|---|---|
| freq | A |
| leg_stat | PER_CNV, PER_PRSC, PER_SUSP |
| citizen | FOR, NAT, TOTAL |
| unit | NR, P_HTHAB |
| geo | AL, AT, BA, BE, BG, CH, CY, CZ, DE, DK, EE, EL, ES, FI, FR, HR, HU, IE, IS, IT, LI, LT, LU, LV, ME, MK, MT, NL, NO, PL, PT, RO, RS, SE, SI, SK, TR, UKC-L, UKM, UKN, XK (41; ei EU27_2020-aggregaattia; UK jaettu) |
| TIME_PERIOD | 2008–2024 |
| OBS_FLAG, CONF_STATUS | kaikki tyhjiä |

`P_HTHAB` on Eurostatin oma 100 000 asukasta kohti -luku. Oma osoittaja/nimittäjä -laskenta käyttää `NR` + väestöä.

### migr_pop5ctz — Population on 1 January by sex, citizenship and group of country of birth

| | |
|---|---|
| Rivimäärä | 387 617 |
| LAST UPDATE | 25/09/26 23:00:00 |
| Välimuisti | `data/raw/migr_pop5ctz.csv` (29 147 755 t) |

Sarakkeet: `DATAFLOW`, `LAST UPDATE`, `freq`, `c_birth`, `citizen`, `unit`, `sex`, `geo`, `TIME_PERIOD`, `OBS_VALUE`, `OBS_FLAG`, `CONF_STATUS`.

**Ei saraketta `age`.** Sukupuoli on (`F`, `M`, `T`).

| Dimensio | Arvot |
|---|---|
| freq | A |
| c_birth | EU27_2007_FOR, EU27_2020_FOR, EU28_FOR, EXT_EU27_2007, FOR, NAT, NEU27_2007_FOR, NEU27_2020_FOR, NEU28_FOR, TOTAL, UNK |
| citizen | 281 koodia (maakoodit + aggregaatit). Mukana: NAT, FOR, TOTAL, UNK, STLS |
| unit | NR |
| sex | F, M, T |
| geo | 42, mukana EU27_2020 ja FI; ei UK-koodia tässä otoksessa |
| TIME_PERIOD | 2009–2025 |
| OBS_FLAG | b, be, bep, e, ep, p (suurin osa tyhjä) |
| CONF_STATUS | N tai tyhjä |

NAT/FOR-väestö vaatii filtterin: `citizen` ∈ {NAT, FOR} (ja tyypillisesti `c_birth=TOTAL`, `sex=T`). Älä sekoita `c_birth=FOR` ja `citizen=FOR`.

Vaihe 7: `citizen`-aggregaatit `EU27_2020_FOR` ja `NEU27_2020_FOR` ovat unique-listassa (myös `EU15_FOR`, `NEU27_2007_FOR` ym.). K1-asteisiin niitä ei yhdistetä, koska `crim_just_ctz` ei erota FOR-osoittajaa.

### migr_pop1ctz — Population on 1 January by age group, sex and citizenship

| | |
|---|---|
| Rivimäärä | 8 795 902 |
| LAST UPDATE | 25/09/26 23:00:00 |
| Välimuisti | `data/raw/migr_pop1ctz.csv` (642 514 888 t) |

Sarakkeet: `DATAFLOW`, `LAST UPDATE`, `freq`, `citizen`, `age`, `unit`, `sex`, `geo`, `TIME_PERIOD`, `OBS_VALUE`, `OBS_FLAG`, `CONF_STATUS`.

| Dimensio | Arvot |
|---|---|
| freq | A |
| citizen | 287 koodia. Mukana: NAT, TOTAL, UNK, STLS, FOR_STLS. **Aggregaattia FOR ei ole unique-listassa.** |
| age | TOTAL, UNK, Y_LT5, Y5-9, Y10-14, Y15-19, Y15-64, Y20-24, Y25-29, Y30-34, Y35-39, Y40-44, Y45-49, Y50-54, Y55-59, Y60-64, Y65-69, Y70-74, Y75-79, Y80-84, Y85-89, Y90-94, Y95-99, Y_GE100, Y_GE65, Y_GE85, Y_LT15 |
| unit | NR |
| sex | F, M, T |
| geo | 45, mukana EU27_2020, FI, UK |
| TIME_PERIOD | 1998–2025 |
| OBS_FLAG | b, be, bep, bp, e, ep, ip, p |
| CONF_STATUS | N tai tyhjä |

Ikä × sukupuoli × kansalaisuus on tässä, mutta rikosaineistossa ei. SIR crim_just_ctz:stä ei ole mahdollinen ilman ulkopuolista ikäjakaumaa rikoksille.

### migr_pop3ctb — Population on 1 January by age group, sex and country of birth

| | |
|---|---|
| Rivimäärä | 7 100 600 |
| LAST UPDATE | 25/09/26 23:00:00 |
| Välimuisti | `data/raw/migr_pop3ctb.csv` (519 240 179 t) |

Sarakkeet: `DATAFLOW`, `LAST UPDATE`, `freq`, `c_birth`, `age`, `unit`, `sex`, `geo`, `TIME_PERIOD`, `OBS_VALUE`, `OBS_FLAG`, `CONF_STATUS`.

| Dimensio | Arvot |
|---|---|
| freq | A |
| c_birth | 307 koodia. Mukana: NAT, FOR, TOTAL, UNK |
| age | sama 27 koodia kuin migr_pop1ctz |
| unit | NR |
| sex | F, M, T |
| geo | 45, mukana EU27_2020, FI, UK |
| TIME_PERIOD | 1998–2025 |
| OBS_FLAG | b, be, bep, bp, e, ep, ip, p |
| CONF_STATUS | N tai tyhjä |

Syntymämaa ≠ kansalaisuus. crim_just_ctz on kansalaisuus (NAT/FOR).

## Vaihe 6 (S2, S4, S7) — mitä data ei salli

Luettu `crim_just_ctz.csv`-sarakkeista (ei arvattu):

- S2: `citizen` = FOR, NAT, TOTAL. Ei EU-sisäistä / kolmansien maiden jakoa osoittajassa.
- S4: `unit` = NR, P_HTHAB. Ei henkilö vs. tapaus -dimensiota.
- S7: ei naturalisaatiota tai entistä kansalaisuutta.

## Vaihe 8 K2 (haettu 2026-11-01, koodit unique-listasta)

Kuvaileva, ei K1-selittäjä. Täydet listat: `data/interim/dimensiot_k2.txt`.

| Koodi | Dimensiot (poiminta) |
|---|---|
| lfsa_ergan | unit=PC; citizen NAT, FOR, EU27_2020_FOR, NEU27_2020_FOR, NRP, STLS, TOTAL, EU27_2020; age mm. Y15-64 |
| lfsa_urgan | unit=PC; citizen NAT, FOR, EU27_2020_FOR, NEU27_2020_FOR, NRP, STLS, TOTAL; ei EU27_2020-citizen |
| edat_lfs_9911 | unit=PC; isced11 ED0-2, ED3-8, ED34_44, ED35_45, ED3_4, ED5-8; citizen kuten urgan; age mm. Y25-64 |
| migr_resfirst | reason EDUC, EMP, FAM, OTH, TOTAL; duration M3-5, M6-11, M_GE12, TOTAL; unit=PER; citizen ISO-maat (ei NAT/FOR) |
| migr_resvalid | reason EDUC, EMP, FAM, OTH, RFG, SPROT, TOTAL; muuten kuten first |

K2-suodatus: LFS sex=T, age Y15-64 (asteet) / Y25-64 ja isced11 ∈ {ED0-2, ED3_4, ED5-8} (koulutus). Luvat: duration=TOTAL, citizen=TOTAL, geo EU-27 + EU27_2020.

## Muut (ei haettu)

| Koodi | Sisältö | Huomio |
|---|---|---|
| crim_pris_ctz | Vangit kansalaisuuden mukaan | ei vaiheessa 8 |
| crim_hom_soff | Henkirikokset, seksuaalirikokset | ei kansalaisuutta; ei yhdistettävissä K1:een |
| migr_asydcfsta | Turvapaikkapäätökset | ei haettu; luvat kattavat OTH/RFG/SPROT |

## Kansalliset (maakohtaiset tapaustutkimukset)

- Tanska: Danmarks Statistik
- Ruotsi: Brå
- Suomi: Tilastokeskus, Poliisi, Rikosseuraamuslaitos
- Alankomaat: CBS
- Saksa: BKA, Polizeiliche Kriminalstatistik

Kansalliset aineistot eivät ole keskenään yhteismitallisia. Älä yhdistä EU-aggregaattiin.

## MANIFEST (data/raw/MANIFEST.csv)

Sarakkeet: tiedosto, lähde, URL, hakupäivä, kuvaus, huomiot.

Raaka-CSV:t (`data/raw/*.csv` paitsi MANIFEST) ovat git-ignorissa koon vuoksi.
