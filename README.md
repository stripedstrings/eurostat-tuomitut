# EU-maiden tuomitut kansalaisuuden mukaan 2008–2024

**Tutkimus-hubi** (kolme erillistä haaraa): [tutkimus/](https://stripedstrings.github.io/eurostat-tuomitut/tutkimus/) — K1 EU-tuomitut, FI-maahanmuuttopaneeli (TUTKIVA), media-agenda. Haaroja ei yhdistetä samaan analyysiin.  
**Tila:** [tutkimus/tila.html](https://stripedstrings.github.io/eurostat-tuomitut/tutkimus/tila.html) (commit, esirekisteröinti, haku, peitto, testit, ei testattavat).  
**Aikajanat (ei päättelyyn):** [tutkimus/aikajana.html](https://stripedstrings.github.io/eurostat-tuomitut/tutkimus/aikajana.html).

Esirekisteröity raportti: [GitHub Pages](https://stripedstrings.github.io/eurostat-tuomitut/) ([`output/RAPORTTI.md`](output/RAPORTTI.md)).  
Tutkiva visualisointi (ei esirekisteröity): [maasivut](https://stripedstrings.github.io/eurostat-tuomitut/maat/fi.html).  
Mediahaara (agenda: näkyvyys/kehykset; ei motiivi- tai kontrolliväitettä): [`MEDIA_README.md`](MEDIA_README.md), [Media-välilehti](https://stripedstrings.github.io/eurostat-tuomitut/media/).  
FI-paneeli: [maahanmuutto-fi/](https://stripedstrings.github.io/eurostat-tuomitut/maahanmuutto-fi/).
Ks. `CHANGELOG.md`.

Avoin, toistettava ja dataan perustuva tarkastelu siitä, eroavatko oman maan
kansalaisten ja ulkomaan kansalaisten tuomitsemisasteet EU-maissa, ja kuinka
suuri osa erosta säilyy, kun ikä ja sukupuoli huomioidaan.

> **Periaate:** Kysymys on asetettu avoimeksi. Tulokset raportoidaan siitä
> riippumatta, mihin suuntaan ne osoittavat. Johtopäätökset kirjoitetaan vasta
> tulosten jälkeen, ja vain siltä osin kuin data niitä tukee.

## 1. Tutkimuskysymykset

Projekti jaetaan kahteen erilliseen kysymykseen, joita ei sekoiteta.

**K1 (rikostilasto, tämän projektin ydin):**
Eroavatko tuomitut per 100 000 asukasta oman maan ja ulkomaan kansalaisten
välillä EU-maittain vuosina 2008/2009–2024? Kuinka suuri osa erosta selittyy
ikä- ja sukupuolirakenteella?

**K2 (valinnainen laajennus, raportoidaan erikseen):**
Mitä aineisto kertoo työllisyydestä, koulutuksesta ja oleskeluluvan perusteesta
kansalaisuusryhmittäin? Kuvaileva sivu: [`docs/k2/`](https://stripedstrings.github.io/eurostat-tuomitut/k2/).
S2/S7 (ei dataa): `output/tables/s2_s7_tila.csv`. Brå (SE, syntymämaa ≠ kansalaisuus):
[`docs/national/bra.html`](https://stripedstrings.github.io/eurostat-tuomitut/national/bra.html).

**Mitä projekti EI väitä ratkaisevansa:** onko EU:n turvapaikka-, pakolais- tai
kiintiöpolitiikka perusteltua. Se on normatiivinen ja monitekijäinen kysymys
(oikeudelliset velvoitteet, työmarkkinat, julkinen talous, demografia,
humanitaariset näkökohdat). Rikostilasto on vain yksi osa-alue.

## 2. Esirekisteröidyt säännöt

Katso `PREREGISTRATION.md`. Kysymykset, menetelmät ja tulkintasäännöt on
lukittu ennen tulosten katsomista. Poikkeamat kirjataan `CHANGELOG.md`:hen
perusteluineen.

## 3. Datalähteet

Yksityiskohdat: `DATA_SOURCES.md`. Dimensiokoodit tarkistetaan datasta, ei
arvata.

| Tarve | Eurostat-koodi (tarkistettava) |
|---|---|
| Tuomitut/epäillyt kansalaisuuden mukaan | `crim_just_ctz` |
| Väestö kansalaisuuden mukaan | `migr_pop5ctz` |
| Väestö ikä x sukupuoli x kansalaisuus | `migr_pop1ctz` |
| Väestö syntymämaan mukaan | `migr_pop3ctb` |
| Vankilaväestö kansalaisuuden mukaan | `crim_pris_ctz` |
| Koulutus, työllisyys | `edat_lfs_*`, `lfsa_ergan`, `lfsa_urgan` |
| Oleskeluluvat | `migr_resfirst`, `migr_resvalid` |
| Turvapaikkapäätökset | `migr_asydcfsta` |

Kansalliset lisäaineistot (maakohtaiset tapaustutkimukset, ei EU-aggregaattiin):
Tanska (Danmarks Statistik), Ruotsi (Brå), Suomi (Tilastokeskus), Alankomaat
(CBS), Saksa (BKA PKS).

## 4. Menetelmät

Yksityiskohdat: `METHODS.md`.

1. Raaka-aste: tuomitut / ryhmän väestö x 100 000, maittain ja vuosittain.
2. Suhdeluku (ulkomaat / oma maa) Poisson-luottamusväleineen.
3. Epäsuora ikä-sukupuolivakiointi (SIR), jos ikä x sukupuoli -data on
   saatavilla molemmille ryhmille.
4. Jaottelu: EU-sisäiset vs. kolmansien maiden kansalaiset, jos data sallii.
5. EU-aggregaatti vain maista, joilta on data molemmille ryhmille samana vuonna.
6. Herkkyysanalyysit (katso `PREREGISTRATION.md`).

## 5. Tunnetut rajoitteet (näytetään jokaisessa kaaviossa)

- **Kansalaisuus ≠ maahanmuuttotausta ≠ pakolaisuus.** "Ulkomaan kansalaiset"
  sisältää työperäiset, opiskelijat, EU-sisäiset muuttajat, perheenyhdistämiset
  ja turvapaikan saaneet. Naturalisoituneet siirtyvät "oman maan kansalaisiin".
- **Epäillyt vs. tuomitut.** Ne mittaavat eri asioita (poliisin kohdentaminen,
  syyttäjäkäytäntö, tuomioistuinten käytäntö).
- **Laskentayksiköt vaihtelevat** maittain (henkilöt, tapaukset, tuomiot).
- **Oikeusjärjestelmien erot** rajoittavat maiden välistä vertailua.
- **Matkailijat ja ei-asukkaat** voivat esiintyä rikostilastossa mutta ei
  asukasväestössä, mikä vääristää nimittäjää.
- **Ekologinen virhepäätelmä:** maatason aggregaatit eivät kerro yksilötason
  syistä.
- **Ei ikä- ja sukupuolivakioitu**, ellei kaaviossa nimenomaisesti toisin sanota.
- **Puuttuva data** jätetään puuttuvaksi (ei interpolointia).

## 6. Rakenne

```
eu-rikollisuus-kansalaisuus/
├── README.md
├── PREREGISTRATION.md
├── METHODS.md
├── DATA_SOURCES.md
├── CURSOR_TASKS.md
├── CHANGELOG.md
├── requirements.txt
├── .cursor/rules/project.mdc
├── data/
│   ├── raw/          # API-vastaukset (välimuisti), ei muokata käsin
│   ├── interim/
│   └── processed/
├── src/
│   ├── fetch.py      # Eurostat-haku + välimuisti
│   ├── clean.py
│   ├── rates.py      # asteet, suhdeluvut, Poisson-CI
│   ├── standardize.py# SIR
│   ├── coverage.py   # coverage matrix
│   ├── plots.py
│   └── national/     # dk.py, se.py, fi.py (erillään EU-aggregaatista)
├── tests/
├── output/
│   ├── figures/
│   └── tables/
└── notebooks/
```

## 7. Ajaminen

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m src.fetch        # hakee ja välimuistittaa datan
python -m src.clean
python -m src.rates
python -m src.standardize
python -m src.coverage
python -m src.plots
python -m src.national     # DK/SE/FI, ei EU-aggregaattiin
pytest
```

Jos Eurostatin rajapinta ei vastaa, lataa CSV käsin kansioon `data/raw/` ja
kirjaa tiedoston lataus pvm ja URL tiedostoon `data/raw/MANIFEST.csv`.

## 8. Toistettavuus ja avoimuus

- Koodi ja data julkisesti versionhallinnassa.
- Jokaisen raakatiedoston hakupäivä ja URL kirjataan `MANIFEST.csv`:ään.
- Satunnaisuutta ei käytetä; jos käytetään (bootstrap), siemen kirjataan.
- Kaikki maat ja kaikki vuodet raportoidaan, ei vain valikoituja.
- Kaikki kaaviot ja taulukot tuotetaan koodista, ei käsin.

## 9. Kansalliset tapaustutkimukset (erillään EU-aggregaatista)

Ajo: `python -m src.national`. Tiedostot: `data/national/`. **Ei lisätä `eu_aggregaattiin`.**

**Tanska (Danmarks Statistik STRFNA13).** Syylliseksi todetut 2018–2025. Kansalaisuus unique: `DANSK`, `VEST`, `IKKEVEST` (tanskalainen / länsimainen / ei-länsimainen). Ei Eurostatin NAT/FOR. Taulukossa ei ole väestönimittäjää. Lähde: StatBank API.

**Ruotsi (Brå).** Ei julkista API:a tuomituille × kansalaisuus. Brån 2021-raportti koskee epäiltyjä ja inrikes/utrikes bakgrund (syntymämaa), ei NAT/FOR-tuomittuja. CSV/XLSX voi sijoittaa nimellä `data/national/se_bra.csv`. Lukuja ei kopioida PDF:stä.

**Suomi (Tilastokeskus StatFin 15hh).** Rangaistukset 2009–2024, kansalaisuus unique-listasta `Suomi` ja `Ulkomaat yhteensä`. Kaksi saraketta: oikeudessa tuomitut vs. kaikki seuraamukset (ml. rangaistus- ja rikesakot). Laskentayksikkö on rangaistus. Poliisin ja Rikosseuraamuslaitoksen aineistoja ei ole tässä vaiheessa.

Maiden tilastot eivät ole yhteismitallisia keskenään eivätkä Eurostatin `crim_just_ctz`:n kanssa.

## 10. Lisenssi ja lähdeviitteet

Koodi: MIT (tai valittu). Eurostat-data: Eurostatin uudelleenkäyttöehdot,
mainittava lähde. Kansalliset aineistot: kunkin tilastoviranomaisen ehdot.
