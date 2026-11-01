# Menetelmät

## 1. Aste
rate_g = (convicted_g / population_g) * 100000,  g ∈ {NAT, FOR}

## 2. Suhdeluku ja luottamusväli
RR = rate_FOR / rate_NAT.
Luottamusväli log-skaalalla: ln(RR) ± 1.96 * sqrt(1/D_FOR + 1/D_NAT),
missä D on tuomittujen lukumäärä (Poisson-oletus). Pienillä luvuilla
(D < 20) käytä täsmällistä (Garwood) väliä asteille ja raportoi varoitus.
Väestön epävarmuus oletetaan merkityksettömäksi.

## 3. Epäsuora vakiointi (SIR)
Ehto: ikäryhmä x sukupuoli -tuomitut JA -väestö molemmille ryhmille.
1. Laske NAT-ryhmän ikä-sukupuolikohtaiset asteet r_NAT(a,s).
2. Odotettu FOR-tuomittujen määrä: E = Σ_{a,s} r_NAT(a,s) * Pop_FOR(a,s).
3. SIR = O_FOR / E, missä O_FOR on havaittu määrä.
4. CI: täsmällinen Poisson (Byar tai Garwood) havaitulle O:lle, jaettuna E:llä.
Jos crim_just_ctz ei sisällä ikä- tai sukupuolierittelyä, SIR ei ole
mahdollinen Eurostatin aggregaateilla. Kirjaa tämä, älä korvaa arvauksella.
Vaihtoehto: kansalliset aineistot (esim. Tanska), joissa vakiointi on tehty
virallisesti.

## 4. Vähimmäisehdot
- Nimittäjä > 0 molemmille ryhmille.
- Jos D < 10, merkitse "epäluotettava".
- Puuttuva arvo = NaN. Ei täyttöä.

## 5. EU-aggregaatti
Summaa osoittajat ja nimittäjät vain maista, joilla molemmat ryhmät ovat
mukana kyseisenä vuonna. Raportoi mukana olevien maiden lukumäärä ja
väestöosuus vuosittain. Vaihtoehtoisesti raportoi maiden mediaani ja
kvartiilit (merkitse selvästi).

## 6. Koulutus, työllisyys, oleskelulupa (K2)
Maatason kuvailevia muuttujia. Esitä rinnakkain, älä käytä selittäjinä
yksilötason rikollisuudelle. Käytä EU-LFS:n kansalaisuus- tai
syntymämaaluokkia ja kirjaa luokittelun ero rikostilastoon nähden.

## 7. Mahdollinen myöhempi malli (vain jos mikrodata tai riittävän tarkka data)
Poisson- tai negatiivinen binomi-regressio, offset = log(väestö),
kontrollit: ikä, sukupuoli, koulutus, työllisyys, asumisaika, alue.
Ei ajeta Eurostatin aggregaateilla.

## 8. Vääristymälähteet (kirjataan jokaiseen raporttiin)
Poliisin kohdentaminen, ilmoitusalttius, syyttäjä- ja tuomioistuinkäytännöt,
oikeusjärjestelmän erot, laskentayksiköt, matkailijat ja ei-asukkaat,
naturalisaatio, rekisteröimätön väestö, rikostyyppien koostumus.
