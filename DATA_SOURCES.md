# Datalähteet ja datasanakirja

HUOM: koodit ja dimensioarvot ovat muistinvaraisia. Tarkista ne API:sta
(`.unique()` jokaiselle dimensiolle) ja päivitä tämä tiedosto.

API (SDMX 2.1, CSV):
`https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/<koodi>?format=SDMX-CSV`

## Eurostat
| Koodi | Sisältö | Tarkista |
|---|---|---|
| crim_just_ctz | Epäillyt/tuomitut kansalaisuuden mukaan | dimensiot: leg_stat, citizen, sex, age, unit, geo; vuodet |
| migr_pop5ctz | Väestö kansalaisuuden mukaan | alkaa 2009; citizen-koodit |
| migr_pop1ctz | Väestö ikä x sukupuoli x kansalaisuus | ikäryhmien rajat |
| migr_pop3ctb | Väestö syntymämaan mukaan | |
| crim_pris_ctz | Vangit kansalaisuuden mukaan | |
| crim_hom_soff | Henkirikokset, seksuaalirikokset (ei kansalaisuutta) | ei yhdistettävissä |
| edat_lfs_*, lfsa_ergan, lfsa_urgan | Koulutus, työllisyys | kansalaisuus vs. syntymämaa |
| migr_resfirst, migr_resvalid | Oleskeluluvat perusteen mukaan | |
| migr_asydcfsta | Turvapaikkapäätökset | |

## Kansalliset (maakohtaiset tapaustutkimukset)
- Tanska: Danmarks Statistik (esim. indikaattorit lähtömaaryhmittäin, vakioitu)
- Ruotsi: Brå (Brottsförebyggande rådet)
- Suomi: Tilastokeskus, Poliisi, Rikosseuraamuslaitos
- Alankomaat: CBS
- Saksa: BKA, Polizeiliche Kriminalstatistik (epäillyt kansalaisuuden mukaan)
Kansalliset aineistot eivät ole keskenään yhteismitallisia. Älä yhdistä EU-aggregaattiin.

## MANIFEST (data/raw/MANIFEST.csv)
Sarakkeet: tiedosto, lähde, URL, hakupäivä, kuvaus, hakijan_huomiot.
