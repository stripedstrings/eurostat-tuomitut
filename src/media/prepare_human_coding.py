"""Valmistele ihmiskoodauslomakkeet otoksesta. Ei täytä ihmiskenttiä."""

from __future__ import annotations

import shutil
from pathlib import Path

import pandas as pd

from src.config import ROOT

TABLES = ROOT / "media" / "output" / "tables"
OTOS = TABLES / "koodaus_otos.csv"
LOMAKE_A = TABLES / "koodaus_lomake_ihminen_a.csv"
LOMAKE_B = TABLES / "koodaus_lomake_ihminen_b.csv"
STATUS = TABLES / "koodaus_ihminen_tila.csv"
DOCS = ROOT / "docs" / "media"


def aja() -> None:
    if not OTOS.exists():
        raise FileNotFoundError(OTOS)
    df = pd.read_csv(OTOS)
    if len(df) < 500:
        raise ValueError(f"otos < 500: {len(df)}")

    # Varmista ihmiskentät tyhjinä (ei agenttitäytöä)
    for c in (
        "aihe_ihminen_a",
        "savy_ihminen_a",
        "koodaaja_ihminen_a",
        "aihe_ihminen_b",
        "savy_ihminen_b",
        "koodaaja_ihminen_b",
    ):
        if c not in df.columns:
            df[c] = pd.NA
        else:
            # älä ylikirjoita jos jo täytetty ihmisellä
            pass

    n_a = int(df["aihe_ihminen_a"].notna().sum()) if "aihe_ihminen_a" in df.columns else 0
    n_b = int(df["aihe_ihminen_b"].notna().sum()) if "aihe_ihminen_b" in df.columns else 0

    pohja = df[
        ["media", "paiva", "jarjestys", "otsikko", "snapshot_url", "koodakirja_versio"]
    ].copy()
    pohja.insert(0, "otos_id", range(1, len(pohja) + 1))
    pohja["aihe"] = pd.NA
    pohja["savy"] = pd.NA
    pohja["koodaaja"] = pd.NA
    pohja["muistiinpano"] = pd.NA
    pohja["ohje"] = "CODEBOOK.md; yksi aihe + yksi sävy; neutraali sallittu sävyssä"

    a = pohja.copy()
    a["koodaaja_tunnus"] = "ihminen-A"
    b = pohja.copy()
    b["koodaaja_tunnus"] = "ihminen-B"
    a.to_csv(LOMAKE_A, index=False)
    b.to_csv(LOMAKE_B, index=False)

    tila = pd.DataFrame(
        [
            {"tunnus": "n_otos", "arvo": len(df), "huom": "siemen 20261103; CODEBOOK.md"},
            {"tunnus": "n_kaksoiskoodaus_tavoite", "arvo": len(df), "huom": "100 %"},
            {
                "tunnus": "n_aihe_ihminen_a_taytetty",
                "arvo": n_a,
                "huom": "tyhjä = odottaa ihmistä",
            },
            {
                "tunnus": "n_aihe_ihminen_b_taytetty",
                "arvo": n_b,
                "huom": "tyhjä = odottaa ihmistä",
            },
            {
                "tunnus": "llm_validointi",
                "arvo": "ei",
                "huom": "kielletty ennen ihmis-α + F1 per luokka",
            },
            {
                "tunnus": "H3",
                "arvo": "ei_testattavissa",
                "huom": "ei julkaisijan analytiikkaa",
            },
            {
                "tunnus": "H4",
                "arvo": "ei_testattavissa",
                "huom": "odottaa ihmis-sävyn kaksoiskoodausta",
            },
            {
                "tunnus": "H6",
                "arvo": "ei_testattavissa",
                "huom": "ei tuho/tuhoutuminen-luokkia + odottaa koodausta",
            },
        ]
    )
    tila.to_csv(STATUS, index=False)

    # Päivitä yhteenveto: ihmiset edelleen 0
    yht = TABLES / "koodaus_yhteenveto.csv"
    if yht.exists():
        y = pd.read_csv(yht)
        # päivitä vain n_ihminen -rivi jos on
        mask = y["tunnus"] == "n_ihminen"
        if mask.any():
            y.loc[mask, "arvo"] = "0"
            y.loc[mask, "huom"] = "ihmiskentät tyhjiä; lomakkeet valmiina"
        y.to_csv(yht, index=False)

    DOCS.mkdir(parents=True, exist_ok=True)
    for p in (LOMAKE_A, LOMAKE_B, STATUS, OTOS):
        if p.exists():
            shutil.copy2(p, DOCS / p.name)

    print("lomakkeet", LOMAKE_A, LOMAKE_B)
    print("tila", STATUS, "n_a", n_a, "n_b", n_b)


if __name__ == "__main__":
    aja()
