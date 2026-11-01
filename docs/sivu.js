
const I18N = {
  fi: {
    kicker: "Tuomitut ja epäillyt EU-maissa",
    lead: "Oman maan kansalaiset ja ulkomaan kansalaiset, 2008–2024.",
    maa: "Maa",
    raportti_kicker: "Esirekisteröity raportti",
    raportti_h1: "Tuomitut kansalaisuuden mukaan, EU-27",
    raportti_lead: "K1: asteet NAT vs FOR, 2008–2024. Ei täyttöä, ei syy-yhteyttä.",
    raportti_title: "Tuomitut kansalaisuuden mukaan, EU-27, 2008–2024",
    raportti_alaviite: "Lähde: Eurostat crim_just_ctz, migr_pop5ctz, haettu 2026-11-01. Ei ikä- ja sukupuolivakioitu (SIR = NaN). Kansalaisuus ei kuvaa maahanmuuttotaustaa tai pakolaisuutta. Laskentayksikkö vaihtelee maittain; maiden välinen vertailu on rajallinen. Katkos viivassa = data puuttuu.",
    lahteet_otsikko: "Lähteet",
    lahteet_ingressi: "Luvut perustuvat Euroopan unionin tilastoviraston (Eurostat) julkisiin tilastoaineistoihin. Aineistot ovat EU:n virallisia, avoimesti saatavia tilastoja.",
    lahde_crim: "Suspects and offenders by citizenship. Eurostat, virallinen EU-tilasto. DOI: 10.2908/crim_just_ctz.",
    lahde_pop: "Population on 1 January by sex, citizenship and group of country of birth. Eurostat, virallinen EU-tilasto.",
    lahde_meta: "Crime and criminal justice (crim), Eurostatin metatieto.",
    lahteet_huom: "Tämä sivusto ei ole Eurostatin eikä Euroopan komission julkaisu. Esitetyt asteet on laskettu edellä mainituista aineistoista.",
    luokat_otsikko: "Kansalaisuusluokat",
    luokat_p1: "Aineisto crim_just_ctz erittelee henkilöt kolmeen luokkaan. Kansalaisuusmaittaista jakoa ei ole.",
    luokat_nat: "Ilmoittavan maan kansalaiset. Tällä sivulla:",
    luokat_for: "Muut kansalaisuudet yhteensä. Ryhmään voi sisältyä myös henkilöitä, jotka eivät kuulu vakituiseen väestöön.",
    luokat_total: "Yhteensä. Tuntematon kansalaisuus = TOTAL − NAT − FOR, kun kaikki kolme on ilmoitettu. Tuntematonta ei sijoiteta NAT- eikä FOR-lukuun.",
    luokat_p2: "NAT ja FOR eivät ole syntymämaan tai etnisyyden luokkia. Väestönimittäjä on vakituinen väestö 1. tammikuuta (migr_pop5ctz, c_birth = TOTAL, sex = T). Kansalaisuudettomat (STLS) on jätetty pois molemmista ryhmistä.",
    aste_otsikko: "Tuomitsemisaste, 100 000 asukasta kohden",
    aste_p: "Aste = tuomitut / saman kansalaisuusryhmän väestö × 100 000. Vuodelta 2008 väestöä ei ole. Puuttuva arvo näkyy katkoksena, ei nollana.",
    suhde_otsikko: "Suhdeluku",
    suhde_p1: "Suhde = ulkomaan kansalaisten tuomitsemisaste / oman maan kansalaisten tuomitsemisaste, sama vuosi.",
    suhde_li1: "Suhde 1: asteet ovat yhtä suuret.",
    suhde_li2: "Suhde 2,25: FOR-aste oli 2,25-kertainen NAT-asteeseen. Luku on kirjattujen tuomioiden suhde asukaslukuun. Se ei ole arvio tehdyistä rikoksista eikä yksittäisen henkilön riskistä.",
    suhde_ka: "Keskiarvo 2020–2024 on aritmeettinen keskiarvo vuosilta, joilta molemmat asteet on laskettu. Puuttuvia vuosia ei täytetä.",
    suhde_raja: "Lukuja ei ole vakioitu iän tai sukupuolen mukaan. Osoittajaan voi sisältyä henkilöitä, jotka eivät ole vakituista väestöä.",
    lkm_otsikko: "Tuomittujen lukumäärä",
    vaiheet_otsikko: "Oikeusprosessin vaiheet",
    vaiheet_p1: "Eurostat erottaa kolme vaihetta:",
    vaihe_susp: "Epäillyt.",
    vaihe_prsc: "Syytteeseen asetetut.",
    vaihe_cnv: "Tuomitut.",
    vaiheet_p2: "Vaiheet eivät kuvaa saman henkilöjoukon etenemistä. Epäiltyjen ja tuomittujen osamäärää ei pidä tulkita syyllisyysosuudeksi.",
    epailly_otsikko: "Epäilyaste, 100 000 asukasta kohden",
    epailly_p: "Sama väestönimittäjä kuin tuomituilla. Puuttuva arvo = katkos.",
    pylvas_otsikko: "Lukumäärät vaiheittain",
    pylvas_p: "Rinnakkaiset lukumäärät. Ei saman henkilöjoukon putki.",
    taulu_otsikko: "Vuosittaiset luvut",
    alaviite: "Ei ikä- ja sukupuolivakioitu. Laskentayksikkö vaihtelee maittain (henkilöitä tai tapauksia). Lähde: Eurostat.",
    vertailu_h1: "EU-vertailu",
    vertailu_lead: "Kaikki maat. Yksittäinen maa valitaan valikosta.",
    eu_otsikko: "EU-aggregaatti",
    eu_p: "Kunkin vuoden summa koostuu maista, joilta NAT ja FOR on ilmoitettu samana vuonna. Sarja ei ole virallinen EU-27-luku. Maiden joukko voi vaihtua vuodesta toiseen.",
    cap1: "Tuomitut / 100 000. Maat, joilta NAT ja FOR samana vuonna.",
    cap2: "Suhde = FOR-aste / NAT-aste. Keskiarvo vuosilta 2020–2024, joilta molemmat asteet on laskettu.",
    cap4: "Tuomittujen lukumäärä. Vuosi 2008 ilman väestönimittäjää.",
    avain: "Avainluvut",
    aste_tuom: "Tuomitsemisaste 2020–2024",
    aste_ep: "Epäilyaste 2020–2024",
    vuotta: "vuotta",
    oma: "oman maan kansalaiset",
    ulk: "ulkomaan kansalaiset",
    suhde: "suhde",
    esimerkki: "Vuosi",
    ei_suhdetta: "Suhdetta ei voi laskea: NAT- tai FOR-aste puuttuu kaikilta vuosilta.",
    nat: "Oman maan kansalaiset",
    for: "Ulkomaan kansalaiset",
    th: ["Vuosi","Väestö NAT","Väestö FOR","Tuomitut NAT","Tuomitut FOR","Tuomitut/100k NAT","Tuomitut/100k FOR","Suhde","Epäillyt NAT","Epäillyt FOR","Epäillyt/100k NAT","Epäillyt/100k FOR"],
    bar: ["Epäillyt, NAT","Epäillyt, FOR","Syytteeseen, NAT","Syytteeseen, FOR","Tuomitut, NAT","Tuomitut, FOR"]
  },
  en: {
    kicker: "Convicted and suspected persons in EU countries",
    lead: "National citizens and foreign citizens, 2008–2024.",
    maa: "Country",
    raportti_kicker: "Preregistered report",
    raportti_h1: "Convicted persons by citizenship, EU-27",
    raportti_lead: "K1: rates NAT vs FOR, 2008–2024. No filling, no causal claims.",
    raportti_title: "Convicted persons by citizenship, EU-27, 2008–2024",
    raportti_alaviite: "Source: Eurostat crim_just_ctz, migr_pop5ctz, retrieved 2026-11-01. Not age- and sex-standardised (SIR = NaN). Citizenship is not migrant background or refugee status. The counting unit varies by country; cross-country comparison is limited. A break in a line = missing data.",
    lahteet_otsikko: "Sources",
    lahteet_ingressi: "The figures are based on public statistical datasets of Eurostat, the statistical office of the European Union. These are official EU statistics and are publicly available.",
    lahde_crim: "Suspects and offenders by citizenship. Eurostat, official EU statistic. DOI: 10.2908/crim_just_ctz.",
    lahde_pop: "Population on 1 January by sex, citizenship and group of country of birth. Eurostat, official EU statistic.",
    lahde_meta: "Crime and criminal justice (crim), Eurostat metadata.",
    lahteet_huom: "This website is not a publication of Eurostat or the European Commission. The rates shown are calculated from the datasets listed above.",
    luokat_otsikko: "Citizenship categories",
    luokat_p1: "Dataset crim_just_ctz classifies persons into three categories. There is no breakdown by individual country of citizenship.",
    luokat_nat: "Citizens of the reporting country. On this page:",
    luokat_for: "All other citizenships combined. The group may include persons who are not usual residents.",
    luokat_total: "Total. Unknown citizenship = TOTAL − NAT − FOR when all three are reported. Unknown is not assigned to NAT or FOR.",
    luokat_p2: "NAT and FOR are not categories of country of birth or ethnicity. The population denominator is usual residents on 1 January (migr_pop5ctz, c_birth = TOTAL, sex = T). Stateless persons (STLS) are excluded from both groups.",
    aste_otsikko: "Conviction rate per 100 000",
    aste_p: "Rate = convicted persons / population of the same citizenship group × 100 000. Population is not available for 2008. Missing values appear as gaps, not as zeros.",
    suhde_otsikko: "Ratio",
    suhde_p1: "Ratio = conviction rate of foreign citizens / conviction rate of national citizens, same year.",
    suhde_li1: "Ratio 1: the rates are equal.",
    suhde_li2: "Ratio 2.25: the FOR rate was 2.25 times the NAT rate. The figure is the ratio of recorded convictions to population. It is not an estimate of offences committed and not an individual risk.",
    suhde_ka: "The 2020–2024 mean is the arithmetic mean of years for which both rates are available. Missing years are not filled in.",
    suhde_raja: "The figures are not standardised by age or sex. The numerator may include persons who are not usual residents.",
    lkm_otsikko: "Number of convicted persons",
    vaiheet_otsikko: "Stages of the criminal justice process",
    vaiheet_p1: "Eurostat distinguishes three stages:",
    vaihe_susp: "Persons suspected.",
    vaihe_prsc: "Persons prosecuted.",
    vaihe_cnv: "Persons convicted.",
    vaiheet_p2: "The stages do not follow the same cohort of persons. The ratio of suspects to convicted persons is not a guilt rate.",
    epailly_otsikko: "Suspect rate per 100 000",
    epailly_p: "Same population denominator as for convictions. Missing values appear as gaps.",
    pylvas_otsikko: "Counts by stage",
    pylvas_p: "Parallel counts. Not a flow of the same persons.",
    taulu_otsikko: "Annual figures",
    alaviite: "Not age- or sex-standardised. The counting unit varies by country (persons or cases). Source: Eurostat.",
    vertailu_h1: "EU comparison",
    vertailu_lead: "All countries. Select a country from the menu.",
    eu_otsikko: "EU aggregate",
    eu_p: "Each yearly sum includes only countries that reported both NAT and FOR in that year. The series is not an official EU-27 figure. The set of countries may change from year to year.",
    cap1: "Convicted per 100 000. Countries with NAT and FOR in the same year.",
    cap2: "Ratio = FOR rate / NAT rate. Mean of 2020–2024 years for which both rates are available.",
    cap4: "Number of convicted persons. 2008 without a population denominator.",
    avain: "Summary",
    aste_tuom: "Conviction rate 2020–2024",
    aste_ep: "Suspect rate 2020–2024",
    vuotta: "years",
    oma: "national citizens",
    ulk: "foreign citizens",
    suhde: "ratio",
    esimerkki: "Year",
    ei_suhdetta: "The ratio cannot be calculated: the NAT or FOR rate is missing for all years.",
    nat: "National citizens",
    for: "Foreign citizens",
    th: ["Year","Pop. NAT","Pop. FOR","Convicted NAT","Convicted FOR","Convicted/100k NAT","Convicted/100k FOR","Ratio","Suspected NAT","Suspected FOR","Suspected/100k NAT","Suspected/100k FOR"],
    bar: ["Suspected, NAT","Suspected, FOR","Prosecuted, NAT","Prosecuted, FOR","Convicted, NAT","Convicted, FOR"]
  }
};

function kieli() {
  return localStorage.getItem("kieli") === "en" ? "en" : "fi";
}

function t(key) {
  return I18N[kieli()][key];
}

function asetaKieli(lang) {
  localStorage.setItem("kieli", lang);
  location.reload();
}

function kaytKieli() {
  const lang = kieli();
  document.documentElement.lang = lang;
  document.querySelectorAll("[data-i18n]").forEach(el => {
    const v = I18N[lang][el.getAttribute("data-i18n")];
    if (v !== undefined) el.textContent = v;
  });
  const otsikko = document.querySelector("title[data-i18n]");
  if (otsikko) {
    const v = I18N[lang][otsikko.getAttribute("data-i18n")];
    if (v) document.title = v;
  }
  document.querySelectorAll(".kieli-fi").forEach(el => { el.hidden = lang !== "fi"; });
  document.querySelectorAll(".kieli-en").forEach(el => { el.hidden = lang !== "en"; });
  document.querySelectorAll("#maa option").forEach(opt => {
    const label = lang === "en" ? opt.getAttribute("data-en") : opt.getAttribute("data-fi");
    if (label) opt.textContent = label;
  });
  document.querySelectorAll(".lippu").forEach(b => {
    b.setAttribute("aria-pressed", b.getAttribute("data-lang") === lang ? "true" : "false");
  });
  document.querySelectorAll(".kieli-img").forEach(img => {
    img.src = lang === "en" ? img.getAttribute("data-en") : img.getAttribute("data-fi");
  });
  document.querySelectorAll("#otsikko-maa, #luokka-maa").forEach(el => {
    const label = lang === "en" ? el.getAttribute("data-en") : el.getAttribute("data-fi");
    if (label) el.textContent = label;
  });
  const loc = lang === "en" ? "en-GB" : "fi-FI";
  window.fmt = (v, d=1) => (v === null || v === undefined) ? "—" : Number(v).toLocaleString(loc, {maximumFractionDigits:d});
}

document.querySelectorAll(".lippu").forEach(b => {
  b.addEventListener("click", () => asetaKieli(b.getAttribute("data-lang")));
});
kaytKieli();

function tutkivaNauha() {
  if (document.body.classList.contains("raportti")) return;
  let p = document.querySelector(".tutkiva-nauha");
  if (!p) {
    p = document.createElement("p");
    p.className = "tutkiva-nauha";
    document.body.insertBefore(p, document.body.firstChild);
  }
  const juuri = !/\/maat\//.test(location.pathname);
  const href = juuri ? "index.html" : "../index.html";
  p.innerHTML = kieli() === "en"
    ? `EXPLORATORY (not preregistered). <a href="${href}">Registered report</a>`
    : `TUTKIVA (ei esirekisteröity). <a href="${href}">Esirekisteröity raportti</a>`;
}
tutkivaNauha();

function viiva(id, labels, a, b, otsikkoA, otsikkoB) {
  const el = document.getElementById(id);
  if (!el || typeof Chart === "undefined") return;
  new Chart(el, {
    type: "line",
    data: {
      labels,
      datasets: [
        { label: otsikkoA, data: a, borderColor: "#2c5aa0", backgroundColor: "#2c5aa0", spanGaps: false, tension: 0.15 },
        { label: otsikkoB, data: b, borderColor: "#c45c26", backgroundColor: "#c45c26", spanGaps: false, tension: 0.15 }
      ]
    },
    options: { responsive: true, plugins: { legend: { position: "bottom" } }, scales: { y: { beginAtZero: true } } }
  });
}

function pylvaat(id, labels, datasets) {
  const el = document.getElementById(id);
  if (!el || typeof Chart === "undefined") return;
  new Chart(el, {
    type: "bar",
    data: { labels, datasets },
    options: { responsive: true, plugins: { legend: { position: "bottom" } }, scales: { y: { beginAtZero: true } } }
  });
}

if (window.DATA_URL && window.SIVUN_MAA) {
  fetch(window.DATA_URL).then(r => r.json()).then(data => {
    const s = data.sarjat[window.SIVUN_MAA];
    if (!s) return;
    const lang = kieli();
    const nimi = lang === "en" ? s.nimi_en : s.nimi;
    const ots = document.getElementById("otsikko-maa");
    if (ots) ots.textContent = nimi;
    const lm = document.getElementById("luokka-maa");
    if (lm) lm.textContent = nimi;
    const y = s.vuodet;
    viiva("kaavio-tuomitut-aste", y, s.tuomitut_per_100k_NAT, s.tuomitut_per_100k_FOR, t("nat"), t("for"));
    viiva("kaavio-tuomitut-lkm", y, s.tuomitut_NAT, s.tuomitut_FOR, t("nat"), t("for"));
    viiva("kaavio-epaillyt-aste", y, s.epaillyt_per_100k_NAT, s.epaillyt_per_100k_FOR, t("nat"), t("for"));

    const idx = [];
    for (let i = 0; i < y.length; i++) {
      if (s.tuomitut_NAT[i] != null || s.epaillyt_NAT[i] != null || s.syyteeseen_NAT[i] != null) idx.push(i);
    }
    const lastYears = idx.slice(-8);
    const bar = t("bar");
    pylvaat("kaavio-vaiheet", lastYears.map(i => y[i]), [
      { label: bar[0], data: lastYears.map(i => s.epaillyt_NAT[i]), backgroundColor: "#93c5fd" },
      { label: bar[1], data: lastYears.map(i => s.epaillyt_FOR[i]), backgroundColor: "#fdba74" },
      { label: bar[2], data: lastYears.map(i => s.syyteeseen_NAT[i]), backgroundColor: "#2c5aa0" },
      { label: bar[3], data: lastYears.map(i => s.syyteeseen_FOR[i]), backgroundColor: "#c45c26" },
      { label: bar[4], data: lastYears.map(i => s.tuomitut_NAT[i]), backgroundColor: "#1e3a5f" },
      { label: bar[5], data: lastYears.map(i => s.tuomitut_FOR[i]), backgroundColor: "#7c2d12" }
    ]);

    const ka = s.keskiarvo_tuomitut;
    const ke = s.keskiarvo_epaillyt;
    const av = document.getElementById("avainluvut");
    av.innerHTML = `<h2>${t("avain")}, ${nimi}</h2>
      <p>${t("aste_tuom")} (${ka.n_vuotta || 0} ${t("vuotta")}${ka.vuodet ? ": " + ka.vuodet : ""}):
        ${t("oma")} <strong>${fmt(ka.per_100k_NAT)}</strong> / 100 000,
        ${t("ulk")} <strong>${fmt(ka.per_100k_FOR)}</strong> / 100 000,
        ${t("suhde")} <strong>${fmt(ka.suhde, 2)}</strong>.</p>
      <p>${t("aste_ep")} (${ke.n_vuotta || 0} ${t("vuotta")}${ke.vuodet ? ": " + ke.vuodet : ""}):
        ${t("oma")} <strong>${fmt(ke.per_100k_NAT)}</strong>,
        ${t("ulk")} <strong>${fmt(ke.per_100k_FOR)}</strong>,
        ${t("suhde")} <strong>${fmt(ke.suhde, 2)}</strong>.</p>`;

    const ex = document.getElementById("suhde-esimerkki");
    let pick = null;
    for (let i = y.length - 1; i >= 0; i--) {
      if (s.tuomitut_suhde[i] != null && s.tuomitut_per_100k_NAT[i] && s.tuomitut_per_100k_FOR[i]) { pick = i; break; }
    }
    if (pick !== null) {
      ex.innerHTML = `${t("esimerkki")} <strong>${y[pick]}</strong> (${nimi}):
        ${t("oma")} ${fmt(s.tuomitut_NAT[pick], 0)} / ${fmt(s.vaesto_NAT[pick], 0)}
        → ${fmt(s.tuomitut_per_100k_NAT[pick])} / 100 000.
        ${t("ulk")} ${fmt(s.tuomitut_FOR[pick], 0)} / ${fmt(s.vaesto_FOR[pick], 0)}
        → ${fmt(s.tuomitut_per_100k_FOR[pick])} / 100 000.
        ${t("suhde")} ${fmt(s.tuomitut_per_100k_FOR[pick])} ÷ ${fmt(s.tuomitut_per_100k_NAT[pick])} = <strong>${fmt(s.tuomitut_suhde[pick], 2)}</strong>.`;
    } else {
      ex.textContent = t("ei_suhdetta");
    }

    const th = t("th");
    const tbl = document.getElementById("taulu");
    let html = "<thead><tr>" + th.map(h => `<th>${h}</th>`).join("") + "</tr></thead><tbody>";
    for (let i = 0; i < y.length; i++) {
      html += `<tr><td>${y[i]}</td><td>${fmt(s.vaesto_NAT[i],0)}</td><td>${fmt(s.vaesto_FOR[i],0)}</td>
        <td>${fmt(s.tuomitut_NAT[i],0)}</td><td>${fmt(s.tuomitut_FOR[i],0)}</td>
        <td>${fmt(s.tuomitut_per_100k_NAT[i])}</td><td>${fmt(s.tuomitut_per_100k_FOR[i])}</td>
        <td>${fmt(s.tuomitut_suhde[i],2)}</td>
        <td>${fmt(s.epaillyt_NAT[i],0)}</td><td>${fmt(s.epaillyt_FOR[i],0)}</td>
        <td>${fmt(s.epaillyt_per_100k_NAT[i])}</td><td>${fmt(s.epaillyt_per_100k_FOR[i])}</td></tr>`;
    }
    tbl.innerHTML = html + "</tbody>";
  });
}
