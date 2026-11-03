"""docs/k2/ — kuvaileva K2 erillään K1:stä."""

from __future__ import annotations

import html
import shutil
from pathlib import Path

import pandas as pd

from src.config import DOCS_DIR, FIGURES_DIR, TABLES_DIR

DOCS_K2 = DOCS_DIR / "k2"


def _taulu(path: Path, max_rows: int = 25) -> str:
    if not path.exists():
        return "<p>Taulu puuttuu.</p>"
    df = pd.read_csv(path)
    return df.head(max_rows).to_html(index=False, border=0, classes="taulu")


def aja() -> None:
    from src.site import aihe_nav, ristiviittaukset

    DOCS_K2.mkdir(parents=True, exist_ok=True)
    fig_dir = DOCS_K2 / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    for nimi in (
        "08_k2_tyollisyys.png",
        "08_k2_koulutus.png",
        "08_k2_oleskeluluvat.png",
    ):
        src = FIGURES_DIR / nimi
        if src.exists():
            shutil.copy2(src, fig_dir / nimi)
    for csv_nimi in (
        "k2_tyollisyys.csv",
        "k2_tyottomyys.csv",
        "k2_koulutus.csv",
        "k2_luvat_ensimmaiset.csv",
        "k2_luvat_voimassa.csv",
        "k2_rajoite.csv",
        "s2_s7_tila.csv",
        "herkkyys_S1_S7.csv",
        "eu_vs_kolmas_rajoite.csv",
    ):
        src = TABLES_DIR / csv_nimi
        if src.exists():
            shutil.copy2(src, DOCS_K2 / csv_nimi)

    rajoite = ""
    rp = TABLES_DIR / "k2_rajoite.csv"
    if rp.exists():
        rajoite = html.escape(str(pd.read_csv(rp).iloc[0].get("rajoite", "")))

    kuvat = ""
    for nimi, otsikko in (
        ("08_k2_tyollisyys.png", "Työllisyysaste (EU-27 LFS)"),
        ("08_k2_koulutus.png", "Korkea-asteen koulutus (EU-27 LFS)"),
        ("08_k2_oleskeluluvat.png", "Ensimmäiset oleskeluluvat syittäin"),
    ):
        if (fig_dir / nimi).exists():
            kuvat += (
                f'<figure><img src="figures/{nimi}" alt="{html.escape(otsikko)}" '
                f'style="max-width:100%"><figcaption>{html.escape(otsikko)}. '
                f"Kuvaileva; ei K1-selittäjä. Katkos = puuttuva.</figcaption></figure>\n"
            )

    sivu = f"""<!DOCTYPE html>
<html lang="fi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>K2 — työllisyys, koulutus, oleskeluluvat (kuvaileva)</title>
  <link rel="stylesheet" href="../tyyli.css">
</head>
<body class="raportti">
  <header>
    <div class="wrap">
      {aihe_nav(sijainti="maat", aktiivinen="maahanmuutto")}
      <h1>K2 — kuvaileva (erillään K1:stä)</h1>
      <p class="lead">Työllisyys, työttömyys, koulutus ja oleskeluluvat kansalaisuusryhmittäin.
      Esitetään kuvailevasti. <strong>Ei K1-tuomioasteiden selittäjä</strong>
      (ekologinen virhepäätelmä).</p>
    </div>
  </header>
  <main class="wrap">
    <aside class="kortti">
      <p>{rajoite}</p>
      <p>LFS-luokat (NAT / FOR / EU27_2020_FOR / NEU27_2020_FOR) ≠
      <code>crim_just_ctz</code> (NAT / FOR / TOTAL). Oleskeluluvat: vain
      kolmansien maiden kansalaiset. Puuttuva = tyhjä, ei täyttöä.</p>
      <p><a href="../index.html">← K1-raportti</a> ·
      <a href="s2_s7_tila.csv">S2/S7 ei dataa</a> ·
      <a href="../national/bra.html">Brå-moduuli (SE)</a></p>
    </aside>
    <h2>Kaaviot (EU-27)</h2>
    {kuvat}
    <h2>Rajoite</h2>
    {_taulu(TABLES_DIR / "k2_rajoite.csv")}
    <h2>S2 ja S7 (K1-herkkyys): ei dataa</h2>
    <p>Dokumentoitu syineen; ei lasketa arvauksella.</p>
    {_taulu(TABLES_DIR / "s2_s7_tila.csv")}
    <h2>Otos tauluista</h2>
    <h3>Työllisyys</h3>
    {_taulu(TABLES_DIR / "k2_tyollisyys.csv")}
    <h3>Koulutus (ote)</h3>
    {_taulu(TABLES_DIR / "k2_koulutus.csv")}
    <h3>Oleskeluluvat (ensimmäiset)</h3>
    {_taulu(TABLES_DIR / "k2_luvat_ensimmaiset.csv")}
    {ristiviittaukset(aktiivinen="maahanmuutto", sijainti="maat")}
  </main>
  <script src="../sivu.js"></script>
</body>
</html>
"""
    (DOCS_K2 / "index.html").write_text(sivu, encoding="utf-8")
    print("kirjoitettu", DOCS_K2 / "index.html")


if __name__ == "__main__":
    aja()
