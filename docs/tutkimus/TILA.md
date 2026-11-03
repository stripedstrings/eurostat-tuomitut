# Tutkimuksen tila

Generoitu: 2026-11-03. Commit: `077c40a`.

Tämä sivu on tilannekuva (commit, esirekisteröinti, haku, peitto, testit,
ei testattavat). **Ei johtopäätöksiä.**

| osio | avain | arvo | huom |
|---|---|---|---|
| meta | sivu_paivitetty | 2026-11-03 | tila-sivun generointi |
| meta | git_commit | 077c40a | HEAD lyhyt hash generointihetkellä |
| esirekisterointi | K1_PREREGISTRATION | 2026-11-01 | PREREGISTRATION.md; ei sokko (tutkiva visualisointi ennen) |
| esirekisterointi | MEDIA_PREREGISTRATION | 2026-11-01 | lisäys ihmiskoodaus/mediat 2026-11-03 ennen täyttöä |
| data_haku | eurostat_MANIFEST_hakupaivat | 2026-11-01 | K1/K2 Eurostat-välimuisti |
| data_haku | FI_migr_HAETTU | 2026-11-03 | src/fi_migr/paths.py HAETTU; StatFin/Migri |
| data_haku | media_vaiheet | 2026-11-01…2026-11-03 | CDX/HTML/koodaus/analyysi; ks. MEDIA_DATA_SOURCES.md |
| kattavuus | K1_coverage_matrix | output/tables/coverage_matrix.csv | maa × vuosi × muuttuja |
| kattavuus | FI_peitto_matriisi | output/tables/fi_migr/fi_migr_peitto_matriisi.csv | indikaattori × vuosi; tyhjät mukana |
| kattavuus | media_coverage_vuosi_aukot | media/output/tables/coverage_media_vuosi_aukot.csv | CDX vs HTML; ei täyttöä |
| testit | pytest | ok | 57 passed in 3.35s |
| ei_testattavat | K1_S2 | ei_dataa | citizen vain FOR,NAT,TOTAL — s2_s7_tila.csv |
| ei_testattavat | K1_S7 | ei_dataa | ei naturalisaatiota rikosaineistossa |
| ei_testattavat | K1_S4 | ei_dataa | unit=NR,P_HTHAB; henkilö vs tapaus ei dimensiossa |
| ei_testattavat | Media_H3 | ei_testattavissa | ei julkaisijan klikkianalytiikkaa |
| ei_testattavat | Media_H4 | ei_testattavissa | odottaa ihmis-sävyn kaksoiskoodausta |
| ei_testattavat | Media_H6 | ei_testattavissa | ei tuho/tuhoutuminen-luokkia + odottaa koodausta |
| ei_testattavat | Media_H7_paa | ei_testattavissa | ei aihekoodia 2015–2025; entropia TUTKIVA erillään |
| ei_testattavat | Media_ihmis_koodaus | kesken | lomakkeet A/B valmiina; n_ihminen=0 |
| ei_testattavat | Brå_CSV | ei | määritelmä syntymämaa/bakgrund; CSV puuttuu |
