# Suomi: maahanmuuton avoin tietopaneeli (TUTKIVA)

Ei esirekisteröity. Ei yhdistetä K1-rikostilastoon. Vain Suomi.

## Tavoite

Koota avoimista lähteistä vuosittaiset tulot (maahanmuutto, turvapaikka,
kiintiöpakolaiset, oleskeluluvat), ikä- ja sukupuolijakauma, työllisyys,
koulutus sekä saatavilla olevat kotoutumis-/kielimittarit. Puuttuva = NaN /
`saatavuus=ei`, ei täyttöä.

## Mitä paneeli EI tee

- Ei EU-vertailua (tässä vaiheessa).
- Ei politiikkajohtopäätöksiä kiintiön “oikeellisuudesta”.
- Ei estimoi kielitaidon oppimisaikaa, jos avointa aikasarjaa ei ole.
- Ei sekoita kansalaisuutta, maahanmuuttotaustaa ja pakolaisuutta.

## Tiedostot

- Lähteet: `FI_MIGR_DATA_SOURCES.md`
- Koodi: `src/fi_migr/`
- Taulut: `output/tables/fi_migr/`
- Kaaviot: `output/figures/fi_migr/`
- Raportti: `output/RAPORTTI_FI_MIGR.md`
- Sivusto: `docs/maahanmuutto-fi/`

## Komennot

```text
python -m src.fi_migr.probe
python -m src.fi_migr.fetch_clean
python -m src.fi_migr.plot
python -m src.fi_migr.pages
```
