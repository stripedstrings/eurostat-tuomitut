# Koodikirja M4 v1 (media vs. K1)

Lukittu ennen osuuksien laskentaa. Ei ihmiskoodausta. Ei syy-yhteyttä.

## Vertailun yksiköt (eivät ole samat)

| Lähde | Yksikkö | NAT/FOR |
|---|---|---|
| K1 | Eurostat `crim_just_ctz` tuomitut, **Suomi (FI)** | `NAT` / `FOR` |
| Media | etusivuotsikko, jossa vaihe 3 -entiteetti `rikollisuus` | merkkijono-osuma |

EU-aggregaattia ei sekoiteta Suomen mediaan. Kansallisia aineistoja
(StatFin ym.) ei yhdistetä tähän tauluun.

## Uutisen kansalaisuusmaininta

Osuma otsikon pienaakkosissa. Ei maakuntia, ei demonyymejä (ei keksittyjä
itävaltalainen-luetteloita). Ei `maahanmuuttaja` (tausta ≠ kansalaisuus).

| Luokka | Avaimet |
|---|---|
| NAT | `suomalais`, `suomen kansal` |
| FOR | `ulkomaalais`, `vierasmaalais` |

Molemmat samassa otsikossa: `molemmat`. Ei kumpaakaan: tyhjä (ei NAT).

## Nimittäjät

- Uutinen ehdoton: rikosotsikot (`rikollis`/`rikos`/`tuomittu*`).
- Uutinen ehdollinen: rikosotsikot, joissa NAT- tai FOR-osuma.
- K1: `tuomitut_FOR / (tuomitut_NAT + tuomitut_FOR)` vuosille, joissa
  `kelpoinen_aste` ja media-HTML samana vuonna. Puuttuva vuosi pois, ei täyttöä.

## Varoitukset (aina)

- Uutiskynnys: etusivu ≠ kaikki rikokset.
- Tilaston laskentayksikkö vaihtelee maittain; tässä vain FI.
- Otos: HTML-peitto << kalenteri; D<10 merkitään.
- Kansalaisuus ≠ maahanmuuttotausta tai pakolaisuus.
