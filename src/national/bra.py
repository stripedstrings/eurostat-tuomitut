"""Brå (Ruotsi) — erillinen kansallinen moduuli.

Määritelmä (lukittu): Brån julkinen epäiltyraportointi käyttää
**inrikes / utrikes bakgrund** (syntymämaa ja/tai vanhempien syntymämaa),
**ei** Eurostatin NAT/FOR-kansalaisuutta. Tuomitut × kansalaisuus -CSV:ää
ei ole API:ssa. Ei yhdistetä EU-aggregaattiin eikä K1-asteisiin.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config import FIGURES_DIR, ROOT
from src.national.common import NATIONAL_DIR, NATIONAL_TABLES, kirjaa_manifest, tallenna_kuvio

URL = "https://bra.se/om-bra/om-webbplatsen/data-fran-bra"
LAHDE = "Brå (Brottsförebyggande rådet)"
MAARITELMA = (
    "syntymämaa / inrikes–utrikes bakgrund (vanhempien syntymämaa mukaan lukien); "
    "ei kansalaisuus (NAT/FOR)"
)
RAJOITE = (
    "Brå-moduuli: määritelmä = syntymämaa / bakgrund, ei kansalaisuus. "
    "Julkista API:a tuomituille × kansalaisuus ei ole. Brån 2021-tyyppinen "
    "raportointi koskee epäiltyjä ja inrikes/utrikes bakgrund. "
    "Sijoita käsin ladattu CSV/XLSX: data/national/se_bra.csv. "
    "PDF-lukuja ei kopioida. Ei EU-aggregaattiin, ei K1-selittäjäksi."
)


def loyda_tiedosto() -> Path | None:
    for nimi in ("se_bra.csv", "se_bra.xlsx", "bra.csv", "bra.xlsx"):
        p = NATIONAL_DIR / nimi
        if p.exists() and p.stat().st_size > 0:
            return p
    return None


def meta_taulu(polku: Path | None) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "moduuli": "bra",
                "maa": "SE",
                "lahde": LAHDE,
                "url": URL,
                "maaritelma": MAARITELMA,
                "yksikko": "epäillyt (jos raportti); tuomitut×kansalaisuus ei saatavilla CSV:nä",
                "tiedosto": polku.name if polku else "",
                "saatavuus": "kylla" if polku else "ei",
                "eu_aggregaattiin": "ei",
                "k1_selittaja": "ei",
                "huom": RAJOITE,
            }
        ]
    )


def aja() -> pd.DataFrame:
    NATIONAL_TABLES.mkdir(parents=True, exist_ok=True)
    polku = loyda_tiedosto()
    kirjaa_manifest(
        polku.name if polku else "(puuttuu)",
        LAHDE,
        URL,
        RAJOITE if polku is None else f"ladattu {polku.name}; {MAARITELMA}",
    )
    meta = meta_taulu(polku)
    meta.to_csv(NATIONAL_TABLES / "bra_meta.csv", index=False)
    pd.DataFrame({"rajoite": [RAJOITE], "tiedosto": [polku.name if polku else ""], "maaritelma": [MAARITELMA]}).to_csv(
        NATIONAL_TABLES / "se_rajoite.csv", index=False
    )

    readme = ROOT / "data" / "national" / "BRA_README.md"
    readme.write_text(
        "\n".join(
            [
                "# Brå-moduuli (Ruotsi)",
                "",
                f"**Määritelmä:** {MAARITELMA}.",
                "",
                "Ei Eurostat NAT/FOR. Ei EU-aggregaattiin.",
                "",
                f"Lähde: {LAHDE}. {URL}",
                "",
                "Tiedosto (jos ladattu käsin): `data/national/se_bra.csv`.",
                "Meta: `output/tables/national/bra_meta.csv`.",
                "",
                RAJOITE,
                "",
            ]
        ),
        encoding="utf-8",
    )

    if polku is None:
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(11, 4))
        ax.axis("off")
        ax.set_title("Brå (SE): CSV puuttuu — määritelmä syntymämaa, ei kansalaisuus")
        ax.text(0.5, 0.55, RAJOITE, ha="center", va="center", wrap=True, fontsize=9)
        ax.text(0.5, 0.15, f"Määritelmä: {MAARITELMA}", ha="center", va="center", fontsize=9)
        tallenna_kuvio(
            fig,
            FIGURES_DIR / "09_se_rajoite.png",
            f"Lähde: {LAHDE}. {URL}. Määritelmä: syntymämaa/bakgrund, ei kansalaisuus. Ei EU-aggregaattiin.",
        )
        print(RAJOITE)
        return pd.DataFrame()

    if polku.suffix.lower() == ".csv":
        df = pd.read_csv(polku)
    else:
        df = pd.read_excel(polku)
    df.to_csv(NATIONAL_TABLES / "se_bra.csv", index=False)
    print(f"Brå luettu {polku} rivit={len(df)}; määritelmä={MAARITELMA}")
    return df


if __name__ == "__main__":
    aja()
