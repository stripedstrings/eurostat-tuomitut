"""docs/maahanmuutto-fi/ -paneeli. TUTKIVA."""

from __future__ import annotations

import html
import shutil
from pathlib import Path

import pandas as pd

from src.config import ROOT
from src.fi_migr.paths import DOCS, FIGURES, TABLES


def _df_html(path: Path, max_rows: int = 40) -> str:
    if not path.exists():
        return "<p>Taulu puuttuu.</p>"
    df = pd.read_csv(path)
    return df.head(max_rows).to_html(index=False, border=0, classes="taulu")


def aja() -> None:
    DOCS.mkdir(parents=True, exist_ok=True)
    fig_dir = DOCS / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    for png in FIGURES.glob("*.png"):
        shutil.copy2(png, fig_dir / png.name)
    for csv in TABLES.glob("*.csv"):
        shutil.copy2(csv, DOCS / csv.name)
    for nimi in ("FI_MIGR_README.md", "FI_MIGR_DATA_SOURCES.md", "output/RAPORTTI_FI_MIGR.md"):
        src = ROOT / nimi if not nimi.startswith("output") else ROOT / nimi
        if src.exists():
            shutil.copy2(src, DOCS / src.name)

    raportti = ROOT / "output" / "RAPORTTI_FI_MIGR.md"
    body = ""
    if raportti.exists():
        # yksinkertainen md→html (otsikot + kappaleet)
        lines = []
        for ln in raportti.read_text(encoding="utf-8").splitlines():
            if ln.startswith("## "):
                lines.append(f"<h2>{html.escape(ln[3:])}</h2>")
            elif ln.startswith("# "):
                lines.append(f"<h1>{html.escape(ln[2:])}</h1>")
            elif ln.startswith("|"):
                lines.append(f"<pre>{html.escape(ln)}</pre>")
            elif ln.strip() == "":
                lines.append("")
            else:
                lines.append(f"<p>{html.escape(ln)}</p>")
        body = "\n".join(lines)

    from src.fi_migr.coverage_matrix import MONIVERTAILU
    from src.site import aihe_nav, ristiviittaukset

    kuvat = "".join(
        f'<figure><img src="figures/{p.name}" alt="{p.stem}" style="max-width:100%">'
        f"<figcaption>{html.escape(p.stem)}</figcaption></figure>"
        for p in sorted(FIGURES.glob("*.png"))
    )
    sivu = f"""<!DOCTYPE html>
<html lang="fi">
<head>
  <meta charset="utf-8">
  <title>Suomi maahanmuutto (TUTKIVA)</title>
  <link rel="stylesheet" href="../tyyli.css">
</head>
<body class="raportti">
  <header><div class="wrap">
  {aihe_nav(sijainti="fi_migr", aktiivinen="fi_migr")}
  </div></header>
  <main class="wrap">
    <p class="tutkiva">TUTKIVA (ei esirekisteröity). Ei yhdistetty K1-rikostilastoon.</p>
    <aside class="kortti" aria-label="Monivertailuvaroitus">
      <p><strong>Monivertailuvaroitus.</strong> {html.escape(MONIVERTAILU)}</p>
      <p>Puuttuvaa ei korvata välittäjämuuttujalla. Katkos / tyhjä solu = data puuttuu.</p>
    </aside>
    {body}
    <h2>Kaaviot</h2>
    {kuvat}
    <h2>Peitto (indikaattori × vuosi)</h2>
    <p>Yhteenveto ja <a href="FI_MIGR_PEITTO.md">FI_MIGR_PEITTO.md</a>.
    Laaja matriisi: <a href="fi_migr_peitto_matriisi.csv">fi_migr_peitto_matriisi.csv</a>
    (1 = peitto, tyhjä = aukko; myös tyhjät indikaattorit mukana).</p>
    {_df_html(TABLES / "fi_migr_peitto.csv", max_rows=40)}
    <h2>Kiintiöt: asettaja ja päivämäärä</h2>
    <p>Asettaja + hakupäivä; <code>paatos_pvm</code> vain jos lähteessä (muuten tyhjä).
    <a href="fi_migr_kiintio_meta.csv">fi_migr_kiintio_meta.csv</a>.</p>
    {_df_html(TABLES / "fi_migr_kiintio_meta.csv", max_rows=20)}
    <p>CSV-tiedostot tässä kansiossa. Lähteet: <a href="FI_MIGR_DATA_SOURCES.md">FI_MIGR_DATA_SOURCES.md</a>.</p>
    {ristiviittaukset(aktiivinen="fi_migr", sijainti="fi_migr")}
  </main>
</body>
</html>
"""
    (DOCS / "index.html").write_text(sivu, encoding="utf-8")
    print("kirjoitettu", DOCS / "index.html", flush=True)


if __name__ == "__main__":
    aja()
