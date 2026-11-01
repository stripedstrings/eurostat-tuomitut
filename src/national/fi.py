"""Suomi: Tilastokeskus StatFin 15hh. Ei EU-aggregaattiin."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config import FIGURES_DIR, INTERIM_DIR
from src.national.common import (
    NATIONAL_DIR,
    NATIONAL_TABLES,
    kirjaa_manifest,
    tallenna_kuvio,
    unique_sarakkeet,
)

TAULU = "statfin_syyttr_pxt_15hh"
URL = "https://pxdata.stat.fi/PXWeb/api/v1/fi/StatFin/syyttr/15hh.px"
LAHDE = (
    "Tilastokeskus, StatFin 15hh: rangaistusten lukumäärä kansalaisuuden, "
    "asuinpaikan ja rikoksen mukaan"
)
CSV_NIMI = "fi_15hh.csv"
RAJOITE = (
    "Suomi 15hh: Kansalaisuus unique-listasta mm. Suomi (246) ja Ulkomaat yhteensä (ULK). "
    "Asuinpaikka=Yhteensä, rikosryhmä=Yhteensä. Yhteissarja sisältää rangaistus- ja "
    "rikesakot; oikeudessa tuomitut on erillinen sarake. Ei sama kuin crim_just_ctz. "
    "Sarja 'kaikki seuraamukset' laskee jyrkästi 2020–2021; oikeudessa tuomitut ei. "
    "Katkosta ei täytetä. Ei yhdistetä EU-aggregaattiin."
)
ALAVIITE = (
    f"Lähde: {LAHDE}, haettu 2026-11-01. {RAJOITE} "
    "Kansalaisuus ei kuvaa maahanmuuttotaustaa tai pakolaisuutta. "
    "Laskentayksikkö on rangaistus, ei välttämättä henkilö. Katkos = data puuttuu."
)


def lataa(polku: Path | None = None) -> pd.DataFrame:
    p = polku or (NATIONAL_DIR / CSV_NIMI)
    if not p.exists():
        raise FileNotFoundError(p)
    return pd.read_csv(p)


def puhdista(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out = out.rename(
        columns={
            "Vuosi": "vuosi",
            "Kansalaisuus": "kansalaisuus",
            "Oikeudessa tuomitut, rangaistusmääräyssakot ja rikesakot yhteensä (lkm)": "kaikki_seuraamukset",
            "Oikeudessa tuomitut (lkm)": "oikeudessa_tuomitut",
        }
    )
    out["vuosi"] = pd.to_numeric(out["vuosi"], errors="coerce").astype("Int64")
    out["kaikki_seuraamukset"] = pd.to_numeric(out["kaikki_seuraamukset"], errors="coerce")
    out["oikeudessa_tuomitut"] = pd.to_numeric(out["oikeudessa_tuomitut"], errors="coerce")
    out["maa"] = "Suomi"
    out["lahde"] = TAULU
    return out[
        ["maa", "vuosi", "kansalaisuus", "kaikki_seuraamukset", "oikeudessa_tuomitut", "lahde"]
    ].sort_values(["vuosi", "kansalaisuus"])


def kaavio(df: pd.DataFrame, polku: Path) -> None:
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(11, 6.2))
    for kans, vari in (("Suomi", "#2c5aa0"), ("Ulkomaat yhteensä", "#c45c26")):
        s = df[df["kansalaisuus"] == kans].set_index("vuosi").sort_index()
        ax.plot(
            s.index,
            s["oikeudessa_tuomitut"],
            marker="o",
            color=vari,
            label=f"{kans}, oikeudessa tuomitut",
        )
        ax.plot(
            s.index,
            s["kaikki_seuraamukset"],
            marker="s",
            linestyle="--",
            color=vari,
            alpha=0.6,
            label=f"{kans}, kaikki seuraamukset (ml. sakot)",
        )
    ax.set_title(
        "Suomi: rangaistukset kansalaisuuden mukaan (Tilastokeskus 15hh)\nEi EU-aggregaattiin"
    )
    ax.set_xlabel("Vuosi")
    ax.set_ylabel("Lukumäärä")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    tallenna_kuvio(fig, polku, ALAVIITE)


def aja() -> pd.DataFrame:
    df = lataa()
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    (INTERIM_DIR / "dimensiot_fi_15hh.txt").write_text(
        unique_sarakkeet(df, "15hh"), encoding="utf-8"
    )
    kirjaa_manifest(CSV_NIMI, LAHDE, URL, RAJOITE)
    out = puhdista(df)
    NATIONAL_TABLES.mkdir(parents=True, exist_ok=True)
    out.to_csv(NATIONAL_TABLES / "fi_rangaistukset.csv", index=False)
    pd.DataFrame({"rajoite": [RAJOITE]}).to_csv(NATIONAL_TABLES / "fi_rajoite.csv", index=False)
    kaavio(out, FIGURES_DIR / "09_fi_rangaistukset.png")
    print(RAJOITE)
    print(out.to_string(index=False))
    return out


if __name__ == "__main__":
    aja()
