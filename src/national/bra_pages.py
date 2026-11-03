"""docs/national/bra.html — Brå-moduulin kuvaussivu."""

from __future__ import annotations

import html
import shutil
from pathlib import Path

import pandas as pd

from src.config import DOCS_DIR, FIGURES_DIR
from src.national.bra import LAHDE, MAARITELMA, RAJOITE, URL
from src.national.common import NATIONAL_TABLES

DOCS_NAT = DOCS_DIR / "national"


def aja() -> None:
    from src.site import aihe_nav, ristiviittaukset

    DOCS_NAT.mkdir(parents=True, exist_ok=True)
    meta_p = NATIONAL_TABLES / "bra_meta.csv"
    rajoite_p = NATIONAL_TABLES / "se_rajoite.csv"
    for p in (meta_p, rajoite_p):
        if p.exists():
            shutil.copy2(p, DOCS_NAT / p.name)
    fig = FIGURES_DIR / "09_se_rajoite.png"
    if fig.exists():
        shutil.copy2(fig, DOCS_NAT / fig.name)

    meta_html = (
        pd.read_csv(meta_p).to_html(index=False, border=0, classes="taulu")
        if meta_p.exists()
        else "<p>Meta puuttuu — aja <code>python -m src.national.bra</code>.</p>"
    )
    kuv = ""
    if (DOCS_NAT / "09_se_rajoite.png").exists():
        kuv = (
            '<figure><img src="09_se_rajoite.png" alt="Brå rajoite" style="max-width:100%">'
            "<figcaption>Brå: CSV puuttuu tai rajoite. Ei EU-aggregaattiin.</figcaption></figure>"
        )

    sivu = f"""<!DOCTYPE html>
<html lang="fi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Brå-moduuli (Ruotsi)</title>
  <link rel="stylesheet" href="../tyyli.css">
</head>
<body class="raportti">
  <header>
    <div class="wrap">
      {aihe_nav(sijainti="maat", aktiivinen="maahanmuutto")}
      <h1>Brå-moduuli (Ruotsi)</h1>
      <p class="lead">Kansallinen aineisto erillään EU-aggregaatista ja K1:stä.</p>
    </div>
  </header>
  <main class="wrap">
    <aside class="kortti">
      <p><strong>Määritelmä:</strong> {html.escape(MAARITELMA)}.</p>
      <p>Tämä <em>ei</em> ole Eurostatin kansalaisuus (NAT/FOR). Lukuja ei yhdistetä
      K1-tuomioasteisiin eikä EU-aggregaattiin.</p>
      <p>Lähde: {html.escape(LAHDE)}.
      <a href="{html.escape(URL)}">{html.escape(URL)}</a></p>
      <p>{html.escape(RAJOITE)}</p>
      <p><a href="../k2/index.html">K2 (kuvaileva)</a> ·
      <a href="../index.html">K1</a></p>
    </aside>
    <h2>Meta</h2>
    {meta_html}
    {kuv}
    <p>Käsintaulu (jos saatavilla): <code>data/national/se_bra.csv</code>.
    README: <code>data/national/BRA_README.md</code>.</p>
    {ristiviittaukset(aktiivinen="maahanmuutto", sijainti="maat")}
  </main>
  <script src="../sivu.js"></script>
</body>
</html>
"""
    (DOCS_NAT / "bra.html").write_text(sivu, encoding="utf-8")
    print("kirjoitettu", DOCS_NAT / "bra.html")


if __name__ == "__main__":
    aja()
