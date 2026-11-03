# FI maahanmuuttopaneeli — datalähteet (TUTKIVA)

Probe + haku 2026-11-03. Koodeja ei arvattu. Puuttuva = puuttuva.

## Saatavuus (yhteenveto)

| lähde | koodi / URL | saatavuus | huom |
|---|---|---|---|
| StatFin | `muutl/11a8.px` | kyllä | maahan-/maastamuutto |
| StatFin | `vaerak/11rt.px` | kyllä | ikä × sukupuoli × syntyperä |
| StatFin | `vaerak/159t.px` | kyllä | ulkomaalaistaustaisten osuudet |
| Eurostat | `lfsa_ergan`, `lfsa_urgan`, `edat_lfs_9911` | kyllä (välimuisti, geo=FI) | LFS |
| Eurostat | `migr_resfirst`, `migr_resvalid` | kyllä (välimuisti, geo=FI) | oleskeluluvat |
| Eurostat | `migr_imm1ctz`, `migr_asy*` | ei | HTTP 413 |
| Migri | `https://migri.fi/kiintiopakolaistilastot` | kyllä (HTML) | saapuneet + asettaja-meta |
| Migri | `https://tilastot.migri.fi/` | sivu kyllä | ei koneluettavaa API:a tässä ajossa |
| Kotoutuminen PxWeb | kototietokannat.stat.fi | ei | ei vastausta |
| — | kieli_oppimisaika_kk | ei | ei avointa aikasarjaa |

## Kiintiön asettaja

Suomen valtioneuvosto / eduskunta hyväksyy vuosittaisen pakolaiskiintiön.
UNHCR ehdottaa uudelleensijoitettavia henkilöitä. Lähde: Migri kiintiösivu;
ks. `fi_migr_kiintio_meta.csv`.

## Taulut

`output/tables/fi_migr/*.csv`. Peitto: `fi_migr_saatavuus.csv`, `fi_migr_peitto.csv`.
