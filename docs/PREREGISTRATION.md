# Esirekisteröinti (lukitaan ennen tulosten katsomista)

Päivämäärä: 2026-11-01

Poikkeama (ks. CHANGELOG.md): tätä päivämäärää ennen on tehty tutkiva
visualisointi samoista Eurostat-aineistoista. Esirekisteröinti ei ole sokko.

## Kysymykset
K1: Eroavatko tuomitut per 100 000 oman maan ja ulkomaan kansalaisten
välillä EU-maittain? Kuinka paljon ikä- ja sukupuolivakiointi pienentää tai
muuttaa eroa?
K2 (erillinen): Miten työllisyys, koulutus ja oleskeluluvan peruste jakautuvat
kansalaisuusryhmittäin?

## Aineisto ja rajaukset
- Ajanjakso: 2008–2024 absoluuttiset luvut; suhteelliset 2009–2024
  (nimittäjä alkaa 2009).
- Pääasiallinen mittari: tuomitut (convicted). Epäillyt analysoidaan
  erikseen ja merkitään selvästi.
- Ryhmät: oma maa (NAT), ulkomaat (FOR), tuntematon erikseen.
- Jos mahdollista: FOR jaetaan EU-sisäisiin ja kolmansien maiden kansalaisiin.
- Maa-vuosi otetaan mukaan vain, jos sekä osoittaja että nimittäjä ovat
  molemmille ryhmille saatavilla.
- Poissulkusääntö: maa-vuosi, jossa ulkomaalaisten tuomittujen määrä < 10,
  merkitään "epäluotettava" ja näytetään erikseen (ei poisteta).

## Tulosmuuttujat
1. Raaka-aste per 100 000 ryhmittäin.
2. Suhdeluku RR = aste(FOR) / aste(NAT), 95 % luottamusväli (Poisson).
3. Vakioitu suhdeluku SIR (epäsuora ikä x sukupuoli), 95 % luottamusväli.
4. Muutos: (RR_raaka - SIR) / RR_raaka, eli kuinka suuri osa erosta
   selittyy ikä-sukupuolirakenteella.

## Tulkintasäännöt (sovittu etukäteen)
- Eroa pidetään tilastollisesti havaittavana, jos 95 % luottamusväli ei
  sisällä arvoa 1.
- Eroa ei tulkita syy-yhteydeksi eikä ryhmän ominaisuudeksi.
- Jos luottamusvälit ovat leveät, tulos raportoidaan "ei riittävää näyttöä
  kumpaankaan suuntaan".
- Tulokset raportoidaan kaikille maille riippumatta suunnasta.
- Maatason kontrollit (koulutus, työllisyys) esitetään kuvailevasti, ei
  selittävinä tekijöinä (ekologinen virhepäätelmä).
- Politiikkajohtopäätöksiä ei tehdä pelkästä K1:stä.

## Herkkyysanalyysit (kaikki ajetaan)
S1. Vain maat, joilla täysi kattavuus 2020–2024.
S2. EU-sisäiset ja kolmansien maiden kansalaiset erikseen.
S3. Epäillyt vs. tuomitut.
S4. Maat, joilla laskentayksikkö on "henkilö", erikseen.
S5. Pienten lukujen maat (<10) pois / mukana.
S6. Painotettu (väestöllä) vs. painottamaton EU-keskiarvo.
S7. Naturalisaation vaikutus: arvio siitä, miten tulos muuttuisi, jos
    viimeaikaiset naturalisoituneet laskettaisiin ulkomaalaisiin (jos data
    sallii; muuten kirjataan rajoitteeksi).

## Mitä EI tehdä
- Ei poisteta maita tai vuosia tuloksen perusteella.
- Ei vaihdeta menetelmää tuloksen perusteella ilman kirjausta CHANGELOG.md:hen.
- Ei interpoloida eikä arvioida puuttuvia arvoja.
- Ei tehdä jälkikäteen uusia "merkitseviä" alaryhmiä ilman merkintää
  "tutkiva analyysi".

## Tutkivat analyysit
Kaikki esirekisteröinnin ulkopuoliset analyysit merkitään kaavioissa ja
taulukoissa tekstillä "TUTKIVA (ei esirekisteröity)".

## Hub-aikajana (small multiples) — ei päättelyyn
Sivu `docs/tutkimus/aikajana.html` asettaa K1-, FI- ja mediahaarojen
aikasarjoja rinnakkain (omat akselit, ei päällekkäisiä käyriä, ei
korrelaatioita). **Sivua ei käytetä päättelyyn:** se ei ole K1:n, K2:n
eikä mediahaaran hypoteesitesti, eikä se yhdistä haaroja selittäjä–
vastemuuttuja -suhteeseen. Yksikkövaroitus jokaisessa paneelissa.
