# Synteesi: kolme erillistä haaraa

Päiväys: 2026-11-03.  
Hub: `docs/tutkimus/`. Tila: `docs/tutkimus/tila.html`.  
Aikajanat (ei päättelyyn): `docs/tutkimus/aikajana.html`.

**Tämä asiakirja ei tee yhteistä johtopäätöstä.** Haarat eivät yhdisty
yhdeksi selitykseksi. Jokainen osio vastaa vain oman haaransa kysymyksiin.

---

## 1. K1 — EU tuomitut kansalaisuuden mukaan (esirekisteröity)

Lähde: `output/RAPORTTI.md`, `PREREGISTRATION.md`. Eurostat `crim_just_ctz` /
`migr_pop5ctz` (haettu 2026-11-01).

### Mitä haara näyttää

- Kelpoisissa EU-27 maa–vuosissa NAT- ja FOR-tuomitsemisasteet per 100 000
  eivät ole samat (RR-väli ei sisällä 1 lähes kaikilla kelpoisilla riveillä).
- Poolattu RR 2020–2024 (18 maata, 77 maa–vuotta): noin 3,12 (3,116–3,125).
- Maiden suunta vaihtelee (RR > 1 tai < 1); kaikki raportoidaan.
- Herkkyydet S1, S3, S5, S6 on laskettu; peitto ja rajoitteet dokumentoitu.

### Mitä haara ei näytä

- Syy-yhteyttä kansalaisuuden ja rikollisuuden välillä.
- Maahanmuuttotaustaa, syntymämaata tai pakolaisuutta (muuttuja = kansalaisuus).
- Ikä–sukupuolivakioitua eroa (SIR = NaN).
- EU-sisäiset vs. kolmas maa tuomioasteina (**S2 = ei_dataa**).
- Naturalisaatiokorjausta (**S7 = ei_dataa**).
- Politiikkajohtopäätöstä; K2 ei selitä K1:tä.

### Avoimet kysymykset (K1)

- Mikä osa RR:stä liittyy ikään, oleskeluaikaan, matkailijoihin, laskentayksikköön
  tai ilmoitus-/syyttäjäkäytäntöön?
- Maat ilman kelpoista 2020–2024-aineistoa.
- Brå (SE): CSV puuttuu; määritelmä bakgrund ≠ NAT/FOR.

---

## 2. FI-maahanmuuttopaneeli (TUTKIVA)

Lähde: `output/RAPORTTI_FI_MIGR.md`, peitto `fi_migr_peitto_matriisi.csv`.
Haettu 2026-11-03. Ei yhdistetty K1:een.

### Mitä haara näyttää

- Suomen tulovirtoja (StatFin 11a8), väestöosuuksia, ikä×sukupuoli×syntyperä,
  LFS-työllisyys/koulutus (FI), oleskelulupia, Migri-kiintiösaapumisia.
- Peittomatriisin: mitkä indikaattori×vuosi -solut ovat täynnä / tyhjiä.
- Kiintiön asettaja (valtioneuvosto/eduskunta) + hakupäivä; `paatos_pvm` tyhjä
  jos ei lähteessä.

### Mitä haara ei näytä

- Yhteyttä K1-tuomioasteisiin (kielletty sekoitus).
- Kielitaidon oppimisaikaa tai kotoutumisindikaattoreita (ei avointa aikasarjaa).
- Eurostat `migr_imm*` / `migr_asy*` FI-suodatusta (HTTP 413).
- Yhteismitallista “kokonaisfaktalukua” eri lähteistä.
- Politiikkajohtopäätöstä kiintiön “oikeellisuudesta”.

### Avoimet kysymykset (FI)

- Voidaanko Migri-tilastopalvelusta / kotoutumis-PxWebistä myöhemmin hakea
  koneluettavaa aikasarjaa ilman imputointia?
- Vuosikohtaiset päätetyt kiintiöt ja päätöspäivämäärät virallisista päätöksistä
  (ei arvioita).

---

## 3. Media — uutisagenda

Lähde: `media/output/RAPORTTI_MEDIA.md`, `MEDIA_PREREGISTRATION.md`.
Mediat: Iltalehti, Yle (Wayback). Ei motiivi- tai kontrolliväitettä.

### Mitä haara näyttää

- CDX/HTML-peiton ja aukot (ei täyttöä); entiteettiosuuksia (merkkijono) Wilson-
  väleineen havaituissa snapshoteissa.
- H1/H2-tyyppisiä esiintymislukuja; M4: FI-tuomiot vs. rikosotsikon NAT/FOR-
  avaimet (**eri yksiköt**).
- Sääntökoodausotoksen (N=500) valmistelun; ihmislomakkeet A/B.

### Mitä haara ei näytä

- “Agendan kontrollia”, propagandaa tai journalismin motiiveja.
- Lukijavaikutuksia.
- H3 (klikit), H4 (ihmis-sävy ajassa), H6 (tuho/tuhoutuminen): **ei testattavissa**
  kunnes ehdot täyttyvät.
- Validoitua LLM-/sääntökoodausta koko aineistoon (ihmis-α puuttuu).
- HS/MTV-aineistoa (esirekisteröity lisäys; ei vielä haettu tässä synteesissä).

### Avoimet kysymykset (Media)

- Ihmiskaksoiskoodaus (A/B) ja α / F1 per luokka.
- M2: suhde ulkoisiin tapahtumaindikaattoreihin (usein puuttuu).
- Laajempi mediajoukko ja parempi HTML-peitto (esim. Yle 2016).

---

## 4. Hub (meta)

- **Tila-sivu:** commit, esirekisteröinti, haku, peitto, pytest, ei-testattavat.
- **Aikajanat:** small multiples; **ei päättelyyn** (`PREREGISTRATION.md`).

---

## 5. Mitä synteesi tietoisesti jättää tekemättä

- Ei yhteistä mallia “media + FI-tulot → K1”.
- Ei korrelaatioita hub-aikajanoista.
- Ei politiikkasuosituksia.
- Ei väitettä, että haarat vahvistavat tai kumoavat toisiaan.

Lukija voi lukea kunkin haaran raportin erikseen ja muodostaa oman tulkinnan
rajojen sisällä.
