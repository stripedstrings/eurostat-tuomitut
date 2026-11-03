"""Hub: rinnakkaiset aikajanat (small multiples). Ei korrelaatioita, ei päättelyä."""

from __future__ import annotations

import html
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.config import DOCS_DIR, DPI_KUVA, FIGURES_DIR, ROOT, TABLES_DIR

OUT_FIG = FIGURES_DIR / "10_hub_aikajana_small_multiples.png"
OUT_HTML = DOCS_DIR / "tutkimus" / "aikajana.html"
OUT_CSV = TABLES_DIR / "hub_aikajana_paneelit.csv"
VAROITUS = (
    "TUTKIVA hub-aikajana. Eri yksiköt, eri akselit. Ei päällekkäisiä käyriä "
    "eikä korrelaatioita. Sivua ei käytetä päättelyyn (PREREGISTRATION)."
)


def _k1_fi_for() -> pd.DataFrame:
    a = pd.read_csv(TABLES_DIR / "asteet.csv")
    fi = a[a["geo"] == "FI"].copy()
    fi["vuosi"] = pd.to_numeric(fi["vuosi"], errors="coerce")
    fi = fi.sort_values("vuosi")
    # yksi sarja / paneeli: FOR-aste; puuttuva jää NaN
    return fi[["vuosi", "aste_FOR"]].rename(columns={"aste_FOR": "arvo"})


def _fi_tulot_ulk() -> pd.DataFrame:
    t = pd.read_csv(TABLES_DIR / "fi_migr" / "fi_migr_tulot_vuosi.csv")
    u = t[t["kansalaisuus"] == "ULKOMAAT YHTEENSÄ"].copy()
    u["vuosi"] = pd.to_numeric(u["vuosi"], errors="coerce")
    u = u.sort_values("vuosi")
    return u[["vuosi", "maahanmuutto"]].rename(columns={"maahanmuutto": "arvo"})


def _media_putin_il_otsikko() -> pd.DataFrame:
    p = ROOT / "media" / "output" / "tables" / "p1_entiteetti_osuus.csv"
    d = pd.read_csv(p)
    m = d[
        (d["media"] == "iltalehti_etusivu")
        & (d["yksikko"] == "otsikko")
        & (d["ryhma"] == "putin")
        & d["jakso"].astype(str).str.fullmatch(r"20\d{2}")
    ].copy()
    m["vuosi"] = pd.to_numeric(m["jakso"], errors="coerce")
    m = m.sort_values("vuosi")
    # osuus * 100 = prosenttia; NaN jos puuttuu
    m["arvo"] = pd.to_numeric(m["osuus"], errors="coerce") * 100.0
    return m[["vuosi", "arvo"]]


def _fi_kiintio() -> pd.DataFrame:
    k = pd.read_csv(TABLES_DIR / "fi_migr" / "fi_migr_kiintio.csv")
    k["vuosi"] = pd.to_numeric(k["vuosi"], errors="coerce")
    k = k.sort_values("vuosi")
    return k[["vuosi", "arvo"]]


PANEELIT = [
    {
        "id": "A",
        "haara": "FI-paneeli",
        "otsikko": "FI: ulkomaan kansalaisten maahanmuutto",
        "yksikko": "henkilöä / vuosi (StatFin 11a8)",
        "varoitus": "Syntyperä/kansalaisuus ≠ pakolaisuus. Ei K1-selittäjä.",
        "lataa": _fi_tulot_ulk,
        "vari": "#2c5aa0",
    },
    {
        "id": "B",
        "haara": "K1",
        "otsikko": "K1 FI: tuomitsemisaste FOR",
        "yksikko": "tuomitut / 100 000 FOR-asukasta",
        "varoitus": "Kansalaisuus ≠ maahanmuuttotausta. Ei ikä-sukupuolivakioitu.",
        "lataa": _k1_fi_for,
        "vari": "#c45c26",
    },
    {
        "id": "C",
        "haara": "Media",
        "otsikko": "Media IL: Putin-osuus otsikoissa",
        "yksikko": "% havaituista otsikoista (Wilson-pääanalyysi erillään)",
        "varoitus": "HTML ≪ CDX; puuttuva vuosi = katkos, ei nolla. Ei motiivia.",
        "lataa": _media_putin_il_otsikko,
        "vari": "#4daf4a",
    },
    {
        "id": "D",
        "haara": "FI-paneeli",
        "otsikko": "FI: saapuneet kiintiöpakolaiset",
        "yksikko": "henkilöä / vuosi (Migri)",
        "varoitus": "Kiintiö ≠ kaikki maahanmuutto. Asettaja: valtioneuvosto/eduskunta.",
        "lataa": _fi_kiintio,
        "vari": "#984ea3",
    },
]


def kaavio() -> pd.DataFrame:
    plt.switch_backend("Agg")
    n = len(PANEELIT)
    fig, axes = plt.subplots(n, 1, figsize=(10, 2.8 * n), sharex=False)
    if n == 1:
        axes = [axes]
    meta_rivit = []
    for ax, p in zip(axes, PANEELIT):
        df = p["lataa"]()
        df = df.dropna(subset=["vuosi"]).copy()
        # Älä täytä aukkoja: plottaa vain havaitut; katkos = ei viivaa aukon yli
        vuodet = df["vuosi"].to_numpy(dtype=float)
        arvot = pd.to_numeric(df["arvo"], errors="coerce").to_numpy(dtype=float)
        # katkaise viiva NaN-kohdissa
        ax.plot(vuodet, arvot, marker="o", color=p["vari"], linewidth=1.6, markersize=4)
        ax.set_ylabel(p["yksikko"], fontsize=8)
        ax.set_title(f"{p['id']}. {p['otsikko']}", fontsize=11, loc="left")
        ax.grid(True, alpha=0.3)
        # yksikkövaroitus paneeliin
        ax.text(
            0.01,
            0.02,
            p["varoitus"],
            transform=ax.transAxes,
            fontsize=7,
            color="#333333",
            va="bottom",
        )
        if len(vuodet):
            ax.set_xlim(vuodet.min() - 0.5, vuodet.max() + 0.5)
        meta_rivit.append(
            {
                "paneeli": p["id"],
                "haara": p["haara"],
                "otsikko": p["otsikko"],
                "yksikko": p["yksikko"],
                "n_pistetta": int(np.isfinite(arvot).sum()),
                "vuosi_min": int(vuodet.min()) if len(vuodet) else "",
                "vuosi_max": int(vuodet.max()) if len(vuodet) else "",
                "varoitus": p["varoitus"],
            }
        )
    axes[-1].set_xlabel("Vuosi")
    fig.suptitle(
        "Rinnakkaiset aikajanat (small multiples) — ei yhteistä akselia, ei korrelaatiota",
        fontsize=12,
        y=0.995,
    )
    fig.text(0.5, 0.004, VAROITUS, ha="center", va="bottom", fontsize=7, wrap=True)
    fig.tight_layout(rect=[0.02, 0.04, 0.98, 0.97])
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_FIG, dpi=DPI_KUVA)
    plt.close(fig)
    meta = pd.DataFrame(meta_rivit)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    meta.to_csv(OUT_CSV, index=False, encoding="utf-8")
    return meta


def aja() -> Path:
    from src.site import aihe_nav, ristiviittaukset

    meta = kaavio()
    docs_fig = DOCS_DIR / "tutkimus" / "figures"
    docs_fig.mkdir(parents=True, exist_ok=True)
    import shutil

    shutil.copy2(OUT_FIG, docs_fig / OUT_FIG.name)
    shutil.copy2(OUT_CSV, DOCS_DIR / "tutkimus" / OUT_CSV.name)

    taulu = meta.to_html(index=False, border=0, classes="taulu", escape=True)
    sivu = f"""<!DOCTYPE html>
<html lang="fi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Rinnakkaiset aikajanat (ei päättelyyn)</title>
  <link rel="stylesheet" href="../tyyli.css">
</head>
<body class="raportti">
  <header>
    <div class="wrap">
      {aihe_nav(sijainti="tutkimus", aktiivinen="tutkimus")}
      <h1>Rinnakkaiset aikajanat</h1>
      <p class="lead">Small multiples: yksi sarja per paneeli, <strong>omat akselit</strong>,
      ei päällekkäisiä käyriä, <strong>ei korrelaatioita</strong>.</p>
    </div>
  </header>
  <main class="wrap">
    <aside class="kortti" aria-label="Päättelykielto">
      <p><strong>Esirekisteröity rajoitus:</strong> tätä sivua <em>ei käytetä päättelyyn</em>
      (ks. <code>PREREGISTRATION.md</code>). Paneelit ovat erillisten haarojen
      aikasarjoja rinnakkain. Yksiköt eivät ole yhteismitallisia.</p>
      <p>{html.escape(VAROITUS)}</p>
      <p><a href="index.html">← Tutkimus-hubi</a> · <a href="tila.html">Tila</a></p>
    </aside>
    <figure>
      <img src="figures/{html.escape(OUT_FIG.name)}" alt="Small multiples -aikajanat"
           style="max-width:100%">
      <figcaption>Lähteet paneeleittain: StatFin 11a8; Eurostat crim_just_ctz / migr_pop5ctz (FI);
      media P1 IL otsikko; Migri kiintiö. Katkos = data puuttuu. 200 dpi.</figcaption>
    </figure>
    <h2>Paneelit</h2>
    {taulu}
    {ristiviittaukset(aktiivinen="tutkimus", sijainti="tutkimus")}
  </main>
  <script src="../sivu.js"></script>
</body>
</html>
"""
    OUT_HTML.write_text(sivu, encoding="utf-8")
    print("kirjoitettu", OUT_FIG)
    print("kirjoitettu", OUT_HTML)
    return OUT_HTML


if __name__ == "__main__":
    aja()
