# Tehtävälista Cursorille

Työskentele järjestyksessä. Pysähdy jokaisen vaiheen jälkeen, tulosta
yhteenveto ja odota hyväksyntää. Noudata .cursor/rules/project.mdc-sääntöjä.

## Vaihe 0: Alustus
- Luo kansiorakenne README.md:n mukaan, venv ja requirements.
- Alusta git. Tee commit PREREGISTRATION.md:n täytöllä (päivämäärä) ENNEN
  analyysikoodin ajamista tuloksiin.

## Vaihe 1: Haku ja dimensioiden tarkistus
- src/fetch.py: hae crim_just_ctz, migr_pop5ctz, migr_pop1ctz, migr_pop3ctb
  (SDMX-CSV), välimuisti data/raw, MANIFEST.csv.
- Tulosta jokaiselle datasetille sarakkeet, .nunique() ja .unique() dimensioille.
- Päivitä DATA_SOURCES.md oikeilla koodeilla.
- Raportoi: sisältääkö crim_just_ctz sukupuolen ja iän? Mitkä leg_stat-arvot
  (epäillyt, tuomitut) ovat olemassa? Mikä on unit?

## Vaihe 2: Puhdistus ja coverage
- src/clean.py: yhtenäistä sarakkeet, rajaa NAT/FOR/UNK, tuomitut/epäillyt.
- src/coverage.py: coverage matrix maa x vuosi (osoittaja ja nimittäjä
  molemmille ryhmille) → output/tables/coverage_matrix.csv.
- Ei täyttöä.

## Vaihe 3: Asteet ja suhdeluvut (K1 perus)
- src/rates.py: rate per 100 000, RR, Poisson-CI (log-skaala; Garwood pienille).
- Merkitse D<10 epäluotettavaksi.
- Testit: tunnetuilla käsin lasketuilla esimerkeillä.

## Vaihe 4: Kaaviot (perus)
1. EU-aggregaatti: oma maa vs. ulkomaat per 100 000, 2009–2024.
   Näytä mukana olevien maiden lukumäärä ja väestöosuus per vuosi.
2. Maittain RR 2020–2024 keskiarvo, luottamusvälit (forest plot), kaikki maat.
3. Small multiples maittain 2009–2024.
4. Absoluuttiset määrät 2008–2024.

## Vaihe 5: Ikä-sukupuolivakiointi (SIR)
- Vain jos ikä x sukupuoli -data molemmissa. Muuten kirjaa rajoite.
- src/standardize.py: SIR + CI (METHODS.md §3).
- Kaavio: raaka RR vs. SIR rinnakkain maittain.
- Taulukko: "kuinka suuri osa erosta selittyy iällä ja sukupuolella".

## Vaihe 6: Herkkyysanalyysit S1–S7
- Aja kaikki PREREGISTRATION.md:n herkkyysanalyysit.
- Esitä tulokset yhdessä taulukossa: tulos pääanalyysissä vs. kussakin S:ssä.

## Vaihe 7: EU-sisäiset vs. kolmansien maiden kansalaiset
- Jos crim_just_ctz tai väestödata sallii. Muuten kirjaa rajoite.

## Vaihe 8: K2 (kuvaileva, erillinen)
- Työllisyys, koulutus ja oleskeluluvan peruste kansalaisuusryhmittäin.
- Ei yhdistetä K1:n selittäjiksi. Merkitse ekologinen virhepäätelmä.

## Vaihe 9: Kansalliset tapaustutkimukset (erillään)
- src/national/dk.py, se.py, fi.py: lataa käsin CSV:t, dokumentoi lähde.
- Ei EU-aggregaattiin. Kunkin maan rajoitteet README-osioon.

## Vaihe 10: Raportti
- output/RAPORTTI.md: tulokset, kaikki maat, epävarmuus, rajoitteet.
- Tulososio ensin ilman tulkintaa. Sitten erillinen "Tulkinta ja rajat" -osio:
  mitä data tukee, mitä ei, mitä jää avoimeksi.
- Kirjaa kaikki poikkeamat esirekisteröinnistä.

## Jatkuvat tarkistukset
- Testit läpi (pytest).
- Jokainen kaavio sisältää pakolliset alaviitteet.
- Ei kovakoodattuja lukuja. Ei keksittyä dataa.
- Kysy minulta, jos dimensiot tai koodit eivät vastaa odotettua.
