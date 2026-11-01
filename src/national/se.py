"""Ruotsi: Brå. Ei julkista CSV-API:a; tiedosto data/national/ tai rajoite."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config import FIGURES_DIR
from src.national.common import NATIONAL_DIR, NATIONAL_TABLES, kirjaa_manifest, tallenna_kuvio

URL = "https://bra.se/om-bra/om-webbplatsen/data-fran-bra"
LAHDE = "Brå (Brottsförebyggande rådet)"
RAJOITE = (
    "Ruotsi: Brå:lla ei ole julkista API:a kansalaisuus- tai syntymämaakohtaisille "
    "tuomituille. Virallinen rikosstatistiikka (anmälda brott, lagförda) ei erittele "
    "Eurostatin NAT/FOR-luokkia CSV:nä. Brån raportti 2021 (misstänkta, inrikes/utrikes "
    "bakgrund) on epäillyt ja syntymämaa/vanhempien syntymämaa, ei tuomitut × kansalaisuus. "
    "Sijoita käsin ladattu CSV/XLSX kansioon data/national/ nimellä se_bra.csv. "
    "Ei yhdistetä EU-aggregaattiin. Lukuja ei ole kopioitu PDF:stä."
)


def loyda_tiedosto() -> Path | None:
    for nimi in ("se_bra.csv", "se_bra.xlsx", "se.xlsx", "se.csv"):
        p = NATIONAL_DIR / nimi
        if p.exists() and p.stat().st_size > 0:
            return p
    return None


def aja() -> pd.DataFrame:
    NATIONAL_TABLES.mkdir(parents=True, exist_ok=True)
    polku = loyda_tiedosto()
    kirjaa_manifest(
        polku.name if polku else "(puuttuu)",
        LAHDE,
        URL,
        RAJOITE if polku is None else f"ladattu {polku.name}",
    )
    if polku is None:
        pd.DataFrame({"rajoite": [RAJOITE], "tiedosto": [""]}).to_csv(
            NATIONAL_TABLES / "se_rajoite.csv", index=False
        )
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(11, 4))
        ax.axis("off")
        ax.set_title("Ruotsi (Brå): kansallista CSV:tä ei ole")
        ax.text(0.5, 0.5, RAJOITE, ha="center", va="center", wrap=True, fontsize=9)
        tallenna_kuvio(
            fig,
            FIGURES_DIR / "09_se_rajoite.png",
            f"Lähde: {LAHDE}. {URL}. Ei EU-aggregaattiin. Lukuja ei keksitty.",
        )
        print(RAJOITE)
        return pd.DataFrame()
    if polku.suffix.lower() == ".csv":
        df = pd.read_csv(polku)
    else:
        df = pd.read_excel(polku)
    df.to_csv(NATIONAL_TABLES / "se_bra.csv", index=False)
    pd.DataFrame({"rajoite": [RAJOITE], "tiedosto": [polku.name]}).to_csv(
        NATIONAL_TABLES / "se_rajoite.csv", index=False
    )
    print(f"Luettu {polku} rivit={len(df)}")
    return df


if __name__ == "__main__":
    aja()
