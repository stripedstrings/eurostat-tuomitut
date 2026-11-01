# Tuomitut EU-maissa kansalaisuuden mukaan (2008–2024)

**Lue selaimessa:** [https://stripedstrings.github.io/eurostat-tuomitut/](https://stripedstrings.github.io/eurostat-tuomitut/) (oletus: Suomi; valikosta muut EU-maat ja [EU-vertailu](https://stripedstrings.github.io/eurostat-tuomitut/vertailu.html))

Python-projekti hakee Eurostatin SDMX 2.1 -rajapinnasta tuomittujen määrät kansalaisuuden mukaan ja suhteuttaa ne saman kansalaisuusryhmän väestöön (per 100 000).

## Ajokomennot

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
pip install -r requirements.txt
python -m src.main
```

Uudelleenhaku (ohittaa `cache/`-välimuistin):

```bash
python -m src.main --refresh
```

Tulosteet syntyvät kansioon `output/`. API-vastaukset tallennetaan kansioon `cache/`, jotta dataa ei haeta joka ajolla.

## Datalähteet

Molemmat haetaan muodossa `format=SDMX-CSV`:

| Koodi | Sisältö | Rajaus tässä projektissa |
| --- | --- | --- |
| `crim_just_ctz` | Suspects and offenders by citizenship | `leg_stat=PER_CNV` (tuomitut), `unit=NR`, `citizen` ∈ {NAT, FOR, TOTAL} |
| `migr_pop5ctz` | Väestö 1.1. kansalaisuuden ja syntymämaan mukaan | `c_birth=TOTAL`, `sex=T`, `unit=NR`, `citizen` ∈ {NAT, FOR, UNK, TOTAL} |

Dimensioiden koodit on luettu datasta (`.nunique()` / `.unique()`), ei arvattu. Täysi listaus: `output/dimensiot.txt`.

### Datasetin vastaavuus

- `crim_just_ctz` vastaa odotettua: tuomitut 2008–2024, kansalaisuus `NAT` / `FOR` / `TOTAL`. Tuntematonta kansalaisuutta (`UNK`) **ei ole** erillisenä luokkana; jäännös lasketaan vain kun `TOTAL`, `NAT` ja `FOR` ovat kaikki ilmoitettu (`TOTAL − NAT − FOR`, negatiivinen jäännös jätetään NaN:iksi).
- `migr_pop5ctz` on voimassa. Kansalaisuusryhmät `NAT` ja `FOR` ovat `citizen`-dimensiossa. `c_birth` pitää rajata arvoon `TOTAL`, muuten väestö pilkkoutuisi syntymämaan mukaan. Aikasarja alkaa **2009** (ei 2008), kuten tehtävässä oletettiin.
- Vertailun vuoksi: `migr_pop2ctz` (väestö iän, sukupuolen ja *laajan* kansalaisuusryhmän mukaan) käyttää ulkomaalaisille koodia `FOR_STLS` (ulkomaat + kansalaisuudettomat) ja sisältää myös vuoden 2008. Sitä **ei käytetä**, koska tehtävä nimesi nimittäjäksi `migr_pop5ctz`.

## Laskenta

- Luku = tuomitut / kansalaisuusryhmän väestö × 100 000.
- Vuosi 2008: vain absoluuttiset määrät (erillinen kaavio). Suhteelliset luvut 2009–2024.
- Puuttuvia arvoja ei interpoloida, estimoida eikä täytetä. Kaavioissa NaN näkyy katkoksena.
- **EU-aggregaatti** ei ole virallinen EU-27-luku eikä mediaani. Kullekin vuodelle summataan **vain ne maat, joilla on data molemmille ryhmille (NAT ja FOR) kyseisenä vuonna**. Absoluuttisiin lukuihin riittävät tuomitut; suhteellisiin vaaditaan lisäksi molempien ryhmien väestö. Joukko vaihtelee (sarakkeet `maat_abs` / `maat_aste`).
- **2020–2024 keskiarvo** maittain: aritmeettinen keskiarvo niistä vuosista, joilla *molemmat* ryhmät ovat saatavilla. Puuttuvia vuosia ei täytetä. Käytettyjen vuosien lukumäärä on sarakkeessa `n_vuotta`.

## Rajoitteet ja tulkinta

- **Ei ikä- ja sukupuolivakioitu.** Ikä- ja sukupuolirakenne eroaa kansalaisuusryhmien välillä ja vaikuttaa raakalukuihin. Alaviite on jokaisessa kaaviossa.
- Oikeuslaitostilastojen **laskentayksikkö vaihtelee maittain** (henkilöitä vs. tapauksia / prosesseja). Eurostat suosittelee henkilöitä, mutta kansalliset rekisterit poikkeavat. Maat eivät ole suoraan vertailukelpoisia.
- Tuomitut voivat sisältää myös ei-asukkaita (esim. matkailijat); väestönimittäjä on *vakituinen väestö 1.1.*
- `FOR` väestössä (`migr_pop5ctz`) ei sisällä kansalaisuudettomia (`STLS`); nämä on jätetty pois molemmista ryhmistä.
- Malta: ei tuomittuja kansalaisuuden mukaan koko jaksolla. Kypros, Viro, Irlanti, Liettua, Alankomaat ja Ruotsi: ei NAT/FOR-tuomittuja (vain TOTAL tai ei mitään).
- Espanja 2009: `NAT` ja `FOR` on merkitty nolliksi vaikka `TOTAL` > 0. Nollia ei muuteta NaN:iksi; rivi on merkitty coverage-taulukkoon.

## Tulosteet (`output/`)

1. `01_eu_per_100000.png` — EU-aggregaatti per 100 000, 2009–2024
2. `02_suhdeluku_maittain.png` — ulkomaalaisten / kansalaisten suhde (2020–2024 keskiarvo)
3. `03_pienoiskaaviot_maittain.png` — small multiples 2009–2024
4. `04_absoluuttiset_maarat.png` — absoluuttiset määrät 2008–2024
5. `yhdistetty_data.csv`, `coverage_matrix.csv` — puhdistettu data ja puuttuvuus
6. Lisäksi: `eu_aggregaatti.csv`, `keskiarvo_2020_2024.csv`, `dimensiot.txt`

## Riippuvuudet

`pandas`, `matplotlib`, `requests` (ks. `requirements.txt`).
