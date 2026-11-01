"""Staattiset GitHub Pages -alasivut maittain."""

from __future__ import annotations

import json
import math
import shutil
from html import escape
import pandas as pd

from src.config import DOCS_DIR, EU27, MAAN_NIMET, OUTPUT_DIR, YEARS_ABS

CDN = "https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"


def _n(x):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return None
    try:
        if pd.isna(x):
            return None
    except TypeError:
        pass
    if isinstance(x, (int,)) and not isinstance(x, bool):
        return int(x)
    v = float(x)
    if math.isfinite(v) and v == int(v) and abs(v) < 1e15:
        return int(v)
    return v


def _sarja(df: pd.DataFrame, col: str) -> list:
    if col not in df.columns:
        return [None] * len(df)
    return [_n(v) for v in df[col].tolist()]


def rakenna_json(df: pd.DataFrame, avg: pd.DataFrame, eu: pd.DataFrame) -> dict:
    maat = [{"geo": "FI", "nimi": "Suomi", "tiedosto": "index.html"}]
    muut = sorted((g for g in EU27 if g != "FI"), key=lambda g: MAAN_NIMET[g])
    for g in muut:
        maat.append({"geo": g, "nimi": MAAN_NIMET[g], "tiedosto": f"maat/{g.lower()}.html"})

    sarjat = {}
    for geo in EU27:
        s = df[df["geo"] == geo].sort_values("vuosi")
        a = avg[avg["geo"] == geo]
        a_t = a[a["vaihe"] == "tuomitut"].iloc[0].to_dict() if len(a[a["vaihe"] == "tuomitut"]) else {}
        a_e = a[a["vaihe"] == "epaillyt"].iloc[0].to_dict() if len(a[a["vaihe"] == "epaillyt"]) else {}
        sarjat[geo] = {
            "geo": geo,
            "nimi": MAAN_NIMET[geo],
            "vuodet": [int(v) for v in s["vuosi"].tolist()],
            "vaesto_NAT": _sarja(s, "vaesto_NAT"),
            "vaesto_FOR": _sarja(s, "vaesto_FOR"),
            "vaesto_UNK": _sarja(s, "vaesto_UNK"),
            "vaesto_STLS": _sarja(s, "vaesto_STLS"),
            "tuomitut_NAT": _sarja(s, "tuomitut_NAT"),
            "tuomitut_FOR": _sarja(s, "tuomitut_FOR"),
            "tuomitut_TOTAL": _sarja(s, "tuomitut_TOTAL"),
            "tuomitut_UNK": _sarja(s, "tuomitut_UNK"),
            "tuomitut_per_100k_NAT": _sarja(s, "tuomitut_per_100k_NAT"),
            "tuomitut_per_100k_FOR": _sarja(s, "tuomitut_per_100k_FOR"),
            "tuomitut_suhde": _sarja(s, "tuomitut_suhde_FOR_NAT"),
            "epaillyt_NAT": _sarja(s, "epaillyt_NAT"),
            "epaillyt_FOR": _sarja(s, "epaillyt_FOR"),
            "epaillyt_per_100k_NAT": _sarja(s, "epaillyt_per_100k_NAT"),
            "epaillyt_per_100k_FOR": _sarja(s, "epaillyt_per_100k_FOR"),
            "epaillyt_suhde": _sarja(s, "epaillyt_suhde_FOR_NAT"),
            "syyteeseen_NAT": _sarja(s, "syyteeseen_NAT"),
            "syyteeseen_FOR": _sarja(s, "syyteeseen_FOR"),
            "keskiarvo_tuomitut": {
                "n_vuotta": _n(a_t.get("n_vuotta")),
                "vuodet": a_t.get("vuodet") or "",
                "per_100k_NAT": _n(a_t.get("per_100k_NAT")),
                "per_100k_FOR": _n(a_t.get("per_100k_FOR")),
                "suhde": _n(a_t.get("suhde_FOR_NAT")),
            },
            "keskiarvo_epaillyt": {
                "n_vuotta": _n(a_e.get("n_vuotta")),
                "vuodet": a_e.get("vuodet") or "",
                "per_100k_NAT": _n(a_e.get("per_100k_NAT")),
                "per_100k_FOR": _n(a_e.get("per_100k_FOR")),
                "suhde": _n(a_e.get("suhde_FOR_NAT")),
            },
        }

    eu_out = []
    for _, r in eu.iterrows():
        eu_out.append({k: _n(v) if k != "maat_abs" and k != "maat_aste" and k != "vaihe" else v for k, v in r.items()})
    return {"maat": maat, "sarjat": sarjat, "eu": eu_out, "vuodet": YEARS_ABS}


def _valikko(geo: str | None, juuri: bool) -> str:
    osat = ['<label for="maa">Maa</label>', '<select id="maa" onchange="location.href=this.value">']
    for g in ["FI"] + sorted((x for x in EU27 if x != "FI"), key=lambda x: MAAN_NIMET[x]):
        if g == "FI":
            href = "index.html" if juuri else "../index.html"
        else:
            href = f"maat/{g.lower()}.html" if juuri else f"{g.lower()}.html"
        sel = " selected" if g == geo else ""
        osat.append(f'<option value="{href}"{sel}>{escape(MAAN_NIMET[g])}</option>')
    vert = "vertailu.html" if juuri else "../vertailu.html"
    sel_eu = " selected" if geo is None else ""
    osat.append(f'<option value="{vert}"{sel_eu}>EU-vertailu</option>')
    osat.append("</select>")
    return "\n".join(osat)


def _sivu(geo: str, juuri: bool) -> str:
    nimi = MAAN_NIMET[geo]
    pre = "" if juuri else "../"
    return f"""<!DOCTYPE html>
<html lang="fi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(nimi)} — tuomitut ja epäillyt kansalaisuuden mukaan</title>
  <link rel="stylesheet" href="{pre}tyyli.css">
</head>
<body>
  <header>
    <div class="wrap">
      <p class="kicker"><a href="{pre}index.html">Tuomitut ja epäillyt EU-maissa</a></p>
      <h1>{escape(nimi)}</h1>
      <p class="lead">Oman maan kansalaiset ja ulkomaan kansalaiset, Eurostat 2008–2024.</p>
      <div class="valitsin">{_valikko(geo, juuri)}</div>
    </div>
  </header>
  <main class="wrap">
    <section class="kortti">
      <h2>Ketä nämä ryhmät ovat?</h2>
      <p>Eurostatin oikeustilasto <code>crim_just_ctz</code> ei erittele yksittäisiä kansalaisuuksia
      (esimerkiksi virolaisia, irakilaisia tai ruotsalaisia). Se tuntee vain kolme luokkaa:</p>
      <ul>
        <li><strong>NAT — oman maan kansalaiset.</strong> Sen maan kansalaiset, joka ilmoittaa tilaston (tällä sivulla: {escape(nimi)}).</li>
        <li><strong>FOR — ulkomaan kansalaiset.</strong> Kaikki muut kansalaisuudet <em>yhdessä</em>, yksi summa. Mukana voi olla EU-kansalaisia, EU:n ulkopuolisia, turisteja, kausityöntekijöitä ja muita ei-asukkaita. Datasta ei näe, mitä passeja joukossa on.</li>
        <li><strong>TOTAL — yhteensä.</strong> Jos TOTAL on suurempi kuin NAT + FOR, erotus on tuntematon kansalaisuus. Sitä ei laiteta kumpaankaan ryhmään.</li>
      </ul>
      <p>Nämä eivät ole etnisiä tai syntymämaaluokkia. Väestönimittäjä on vakituinen väestö 1.&nbsp;tammikuuta
      (<code>migr_pop5ctz</code>, NAT ja FOR). Kansalaisuudettomat (STLS) on jätetty pois molemmista ryhmistä.</p>
    </section>

    <section class="kortti avain" id="avainluvut"></section>

    <section>
      <h2>Tuomitsemisaste, 100&nbsp;000 asukasta kohden</h2>
      <p>Aste = tuomitut / saman kansalaisuusryhmän väestö × 100&nbsp;000. Vuosi 2008 näkyy vain lukumäärinä, koska väestöä ei ole. Katkos viivassa on puuttuva tieto, ei nolla.</p>
      <canvas id="kaavio-tuomitut-aste"></canvas>
    </section>

    <section class="kortti">
      <h2>Mitä suhdeluku tarkoittaa?</h2>
      <p>Suhde <strong>ulkomaat / oma maa</strong> = ulkomaan kansalaisten tuomitsemisaste jaettuna oman maan kansalaisten tuomitsemisasteella <em>samana vuonna</em>.</p>
      <ul>
        <li><strong>Suhde 1</strong> tarkoittaa, että molemmissa ryhmissä tilastoitiin yhtä monta tuomiota 100&nbsp;000 asukasta kohden.</li>
        <li><strong>Suhde 2,3</strong> tarkoittaa, että ulkomaan kansalaisten aste oli 2,3-kertainen oman maan kansalaisiin nähden. Se ei tarkoita, että “ulkomaalaiset tekevät 2,3 kertaa enemmän rikoksia”, vaan että <em>kirjatut tuomiot suhteessa asukaslukuun</em> erosivat näin.</li>
      </ul>
      <p id="suhde-esimerkki"></p>
      <p><strong>2020–2024 keskiarvo</strong> on tavallinen aritmeettinen keskiarvo niistä vuosista, joilla <em>molemmat</em> asteet ovat olemassa. Jos jokin vuosi puuttuu, sitä ei arvata eikä korvata. Keskiarvo voi siis perustua 1–5 vuoteen; käytetyt vuodet kerrotaan sivulla.</p>
      <p>Suhde ei vakioi ikää, sukupuolta, oleskelun pituutta eikä sitä, asuuko henkilö maassa. Tuomioihin voi sisältyä ihmisiä, jotka eivät ole vakituista väestöä.</p>
    </section>

    <section>
      <h2>Tuomittujen lukumäärä</h2>
      <canvas id="kaavio-tuomitut-lkm"></canvas>
    </section>

    <section class="kortti">
      <h2>Kannattaako epäillyt ottaa mukaan?</h2>
      <p><strong>Kyllä, mutta eri lukuna — ei todisteena syyllisyydestä.</strong> Eurostat erottaa kolme vaihetta:</p>
      <ol>
        <li><strong>Epäillyt (PER_SUSP)</strong> — henkilöt, jotka poliisi on tilastoinut epäillyiksi / viralliseen kontaktiin rikoksen vuoksi.</li>
        <li><strong>Syytteeseen asetetut (PER_PRSC)</strong> — syyteharkinta on aloitettu.</li>
        <li><strong>Tuomitut (PER_CNV)</strong> — tuomioistuin on todennut syylliseksi.</li>
      </ol>
      <p>Datasta <em>ei näe, miksi</em> joku jäi “vain epäillyksi”: näyttö ei riittänyt, syyte peruttiin, syyteharkinta siirtyi seuraavaan vuoteen, henkilö vapautettiin, tai kyseessä oli eri laskentatapa. Sama ihminen voi olla epäiltynä vuonna T ja tuomittuna vuonna T+1. Siksi epäiltyjä ei saa jakaa tuomituilla ja kutsua sitä “syyllistymisprosentiksi”.</p>
      <p>Epäilyaste kertoo silti jotain: sen, miten usein ryhmä päätyy poliisin kirjaamaksi epäillyksi suhteessa asukaslukuun. Se mittaa kontaktia rikosprosessin alkuun, ei tuomioita.</p>
    </section>

    <section>
      <h2>Epäilyaste, 100&nbsp;000 asukasta kohden</h2>
      <p>Sama väestönimittäjä kuin tuomituilla. Puuttuvat vuodet jätetään tyhjiksi.</p>
      <canvas id="kaavio-epaillyt-aste"></canvas>
    </section>

    <section>
      <h2>Lukumäärät vaiheittain (oma maa vs. ulkomaat)</h2>
      <p>Nämä pylväät ovat rinnakkain vertailua varten. Ne eivät ole saman henkilöjoukon eteneminen putkessa.</p>
      <canvas id="kaavio-vaiheet"></canvas>
    </section>

    <section>
      <h2>Vuosittaiset luvut</h2>
      <div class="taulu-wrap"><table id="taulu"></table></div>
    </section>

    <p class="alaviite">Ei ikä- ja sukupuolivakioitu. Laskentayksikkö vaihtelee maittain (henkilöitä vs. tapauksia). Lähde: Eurostat, crim_just_ctz ja migr_pop5ctz. Ei virallinen EU-julkaisu.</p>
  </main>
  <script src="{CDN}"></script>
  <script>window.SIVUN_MAA = "{geo}"; window.DATA_URL = "{pre}data.json";</script>
  <script src="{pre}sivu.js"></script>
</body>
</html>
"""


def _vertailu() -> str:
    return f"""<!DOCTYPE html>
<html lang="fi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>EU-vertailu — tuomitut kansalaisuuden mukaan</title>
  <link rel="stylesheet" href="tyyli.css">
</head>
<body>
  <header>
    <div class="wrap">
      <p class="kicker"><a href="index.html">Tuomitut ja epäillyt EU-maissa</a></p>
      <h1>EU-vertailu</h1>
      <p class="lead">Kaikkien maiden yhteenveto. Yksittäinen maa valitaan etusivun valikosta (oletus: Suomi).</p>
      <div class="valitsin">{_valikko(None, True)}</div>
    </div>
  </header>
  <main class="wrap">
    <section class="kortti">
      <h2>Miten EU-luku on laskettu</h2>
      <p>Kullekin vuodelle summataan vain ne EU-maat, joilla on data <em>molemmille</em> ryhmille kyseisenä vuonna. Se ei ole virallinen EU-27-luku eikä mediaani. Mukana olevien maiden joukko vaihtuu, joten viiva ei ole saman maan joukon kehitys.</p>
    </section>
    <figure>
      <img src="01_eu_per_100000.png" alt="EU-aggregaatti tuomitsemisasteista">
      <figcaption>Tuomitut / 100 000, maat joilla NAT ja FOR samana vuonna.</figcaption>
    </figure>
    <figure>
      <img src="02_suhdeluku_maittain.png" alt="Suhdeluku maittain">
      <figcaption>Suhde = ulkomaalaisten tuomitsemisaste / kansalaisten tuomitsemisaste, keskiarvo niistä vuosista 2020–2024 joilla molemmat asteet ovat olemassa.</figcaption>
    </figure>
    <figure>
      <img src="03_pienoiskaaviot_maittain.png" alt="Pienoiskaaviot maittain">
    </figure>
    <figure>
      <img src="04_absoluuttiset_maarat.png" alt="Absoluuttiset tuomitut">
    </figure>
    <p class="alaviite">Ei ikä- ja sukupuolivakioitu. Laskentayksikkö vaihtelee maittain. Lähde: Eurostat.</p>
  </main>
</body>
</html>
"""


TYYLI = """
:root { --text:#1b1f24; --muted:#4b5563; --line:#d8dee6; --bg:#f4f1ea; --card:#fff; --nat:#2c5aa0; --for:#c45c26; }
* { box-sizing: border-box; }
body { margin:0; font-family:"Segoe UI", Georgia, serif; color:var(--text); background:var(--bg); line-height:1.55; }
.wrap { max-width:920px; margin:0 auto; padding:0 1.2rem; }
header { background:#1b1f24; color:#f4f1ea; padding:1.4rem 0 1.2rem; }
header h1 { margin:0.2rem 0 0.3rem; font-size:1.85rem; }
header a { color:#f4d2b0; }
.kicker { margin:0; font-size:0.85rem; letter-spacing:0.04em; text-transform:uppercase; }
.lead { margin:0 0 0.8rem; color:#d8dee6; }
.valitsin { display:flex; gap:0.6rem; align-items:center; }
.valitsin label { font-size:0.9rem; }
.valitsin select { font-size:1rem; padding:0.35rem 0.5rem; }
main { padding:1.4rem 0 3.5rem; }
h2 { font-size:1.25rem; margin:1.8rem 0 0.5rem; }
.kortti { background:var(--card); border:1px solid var(--line); border-radius:10px; padding:1rem 1.1rem; margin:1rem 0; }
canvas { background:var(--card); border:1px solid var(--line); border-radius:10px; padding:0.6rem; margin:0.6rem 0 1.2rem; max-height:380px; }
.taulu-wrap { overflow-x:auto; }
table { border-collapse:collapse; width:100%; font-size:0.88rem; background:var(--card); }
th, td { border-bottom:1px solid var(--line); padding:0.35rem 0.45rem; text-align:right; white-space:nowrap; }
th:first-child, td:first-child { text-align:left; }
.alaviite { font-size:0.88rem; color:var(--muted); margin-top:2rem; }
figure img { width:100%; height:auto; border:1px solid var(--line); border-radius:10px; background:#fff; }
figcaption { color:var(--muted); font-size:0.9rem; margin:0.4rem 0 1.4rem; }
.avain p { margin:0.35rem 0; }
code { font-size:0.9em; }
"""

SIVU_JS = r"""
const fmt = (v, d=1) => (v === null || v === undefined) ? "—" : Number(v).toLocaleString("fi-FI", {maximumFractionDigits:d});

function viiva(id, labels, a, b, otsikkoA, otsikkoB) {
  const el = document.getElementById(id);
  if (!el) return;
  new Chart(el, {
    type: "line",
    data: {
      labels,
      datasets: [
        { label: otsikkoA, data: a, borderColor: "#2c5aa0", backgroundColor: "#2c5aa0", spanGaps: false, tension: 0.15 },
        { label: otsikkoB, data: b, borderColor: "#c45c26", backgroundColor: "#c45c26", spanGaps: false, tension: 0.15 }
      ]
    },
    options: {
      responsive: true,
      plugins: { legend: { position: "bottom" } },
      scales: { y: { beginAtZero: true } }
    }
  });
}

function pylvaat(id, labels, datasets) {
  const el = document.getElementById(id);
  if (!el) return;
  new Chart(el, {
    type: "bar",
    data: { labels, datasets },
    options: {
      responsive: true,
      plugins: { legend: { position: "bottom" } },
      scales: { y: { beginAtZero: true } }
    }
  });
}

function viimeinen(arr) {
  for (let i = arr.length - 1; i >= 0; i--) if (arr[i] !== null && arr[i] !== undefined) return { i, v: arr[i] };
  return null;
}

fetch(window.DATA_URL).then(r => r.json()).then(data => {
  const s = data.sarjat[window.SIVUN_MAA];
  if (!s) return;
  const y = s.vuodet;
  viiva("kaavio-tuomitut-aste", y, s.tuomitut_per_100k_NAT, s.tuomitut_per_100k_FOR, "Oman maan kansalaiset", "Ulkomaan kansalaiset");
  viiva("kaavio-tuomitut-lkm", y, s.tuomitut_NAT, s.tuomitut_FOR, "Oman maan kansalaiset", "Ulkomaan kansalaiset");
  viiva("kaavio-epaillyt-aste", y, s.epaillyt_per_100k_NAT, s.epaillyt_per_100k_FOR, "Oman maan kansalaiset", "Ulkomaan kansalaiset");

  const idx = [];
  for (let i = 0; i < y.length; i++) {
    if (s.tuomitut_NAT[i] != null || s.epaillyt_NAT[i] != null || s.syyteeseen_NAT[i] != null) idx.push(i);
  }
  const lastYears = idx.slice(-8);
  pylvaat("kaavio-vaiheet", lastYears.map(i => y[i]), [
    { label: "Epäillyt, oma maa", data: lastYears.map(i => s.epaillyt_NAT[i]), backgroundColor: "#93c5fd" },
    { label: "Epäillyt, ulkomaat", data: lastYears.map(i => s.epaillyt_FOR[i]), backgroundColor: "#fdba74" },
    { label: "Syytteeseen, oma maa", data: lastYears.map(i => s.syyteeseen_NAT[i]), backgroundColor: "#2c5aa0" },
    { label: "Syytteeseen, ulkomaat", data: lastYears.map(i => s.syyteeseen_FOR[i]), backgroundColor: "#c45c26" },
    { label: "Tuomitut, oma maa", data: lastYears.map(i => s.tuomitut_NAT[i]), backgroundColor: "#1e3a5f" },
    { label: "Tuomitut, ulkomaat", data: lastYears.map(i => s.tuomitut_FOR[i]), backgroundColor: "#7c2d12" }
  ]);

  const t = s.keskiarvo_tuomitut;
  const e = s.keskiarvo_epaillyt;
  const av = document.getElementById("avainluvut");
  av.innerHTML = `<h2>Avainluvut, ${s.nimi}</h2>
    <p>Tuomitsemisaste 2020–2024 (keskiarvo, ${t.n_vuotta || 0} vuotta${t.vuodet ? ": " + t.vuodet : ""}):
      oma maa <strong>${fmt(t.per_100k_NAT)}</strong> / 100 000,
      ulkomaat <strong>${fmt(t.per_100k_FOR)}</strong> / 100 000,
      suhde <strong>${fmt(t.suhde, 2)}</strong>.</p>
    <p>Epäilyaste 2020–2024 (keskiarvo, ${e.n_vuotta || 0} vuotta${e.vuodet ? ": " + e.vuodet : ""}):
      oma maa <strong>${fmt(e.per_100k_NAT)}</strong>,
      ulkomaat <strong>${fmt(e.per_100k_FOR)}</strong>,
      suhde <strong>${fmt(e.suhde, 2)}</strong>.</p>`;

  const ex = document.getElementById("suhde-esimerkki");
  let pick = null;
  for (let i = y.length - 1; i >= 0; i--) {
    if (s.tuomitut_suhde[i] != null && s.tuomitut_per_100k_NAT[i] && s.tuomitut_per_100k_FOR[i]) { pick = i; break; }
  }
  if (pick !== null) {
    ex.innerHTML = `Esimerkki vuodelta <strong>${y[pick]}</strong> (${s.nimi}):
      oman maan kansalaisia tuomittiin ${fmt(s.tuomitut_NAT[pick], 0)} henkeä ${fmt(s.vaesto_NAT[pick], 0)} asukasta kohden
      → ${fmt(s.tuomitut_per_100k_NAT[pick])} / 100 000.
      Ulkomaan kansalaisia tuomittiin ${fmt(s.tuomitut_FOR[pick], 0)} henkeä ${fmt(s.vaesto_FOR[pick], 0)} asukasta kohden
      → ${fmt(s.tuomitut_per_100k_FOR[pick])} / 100 000.
      Suhde ${fmt(s.tuomitut_per_100k_FOR[pick])} ÷ ${fmt(s.tuomitut_per_100k_NAT[pick])} = <strong>${fmt(s.tuomitut_suhde[pick], 2)}</strong>.`;
  } else {
    ex.textContent = "Tälle maalle ei ole vuotta, jossa sekä NAT- että FOR-tuomitsemisaste olisi laskettavissa, joten suhdetta ei näytetä.";
  }

  const tbl = document.getElementById("taulu");
  let html = "<thead><tr><th>Vuosi</th><th>Väestö NAT</th><th>Väestö FOR</th><th>Tuomitut NAT</th><th>Tuomitut FOR</th><th>Tuomitut/100k NAT</th><th>Tuomitut/100k FOR</th><th>Suhde</th><th>Epäillyt NAT</th><th>Epäillyt FOR</th><th>Epäillyt/100k NAT</th><th>Epäillyt/100k FOR</th></tr></thead><tbody>";
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
"""


def kirjoita_sivusto(df: pd.DataFrame, avg: pd.DataFrame, eu: pd.DataFrame) -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    (DOCS_DIR / "maat").mkdir(exist_ok=True)
    payload = rakenna_json(df, avg, eu)
    (DOCS_DIR / "data.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    (DOCS_DIR / "tyyli.css").write_text(TYYLI, encoding="utf-8")
    (DOCS_DIR / "sivu.js").write_text(SIVU_JS, encoding="utf-8")
    (DOCS_DIR / "index.html").write_text(_sivu("FI", juuri=True), encoding="utf-8")
    (DOCS_DIR / "vertailu.html").write_text(_vertailu(), encoding="utf-8")
    for geo in EU27:
        (DOCS_DIR / "maat" / f"{geo.lower()}.html").write_text(_sivu(geo, juuri=False), encoding="utf-8")
    for nimi in (
        "01_eu_per_100000.png",
        "02_suhdeluku_maittain.png",
        "03_pienoiskaaviot_maittain.png",
        "04_absoluuttiset_maarat.png",
    ):
        src = OUTPUT_DIR / nimi
        if src.exists():
            shutil.copy2(src, DOCS_DIR / nimi)
    (DOCS_DIR / ".nojekyll").write_text("", encoding="utf-8")
