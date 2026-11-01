
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
