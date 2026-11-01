"""Tanska: Danmarks Statistik STRFNA13. Ei EU-aggregaattiin."""

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

TAULU = "STRFNA13"
URL = "https://api.statbank.dk/v1/data"
LAHDE = "Danmarks Statistik, StatBank STRFNA13 (Skyldige personer efter statsborgerskab)"
CSV_NIMI = "dk_STRFNA13.csv"
RAJOITE = (
    "Tanska STRFNA13: statsborgerskab unique = DANSK, VEST, IKKEVEST "
    "(tanskalainen / länsimainen / ei-länsimainen). Ei Eurostatin NAT/FOR. "
    "OVERTRÆD=1 (strafferetlige afgørelser i alt). Lukumäärät, ei väestönimittäjää "
    "tässä taulussa. Ei yhdistetä EU-aggregaattiin."
)
ALAVIITE = (
    f"Lähde: {LAHDE}, haettu 2026-11-01. {RAJOITE} "
    "Kansalaisuus ei kuvaa maahanmuuttotaustaa tai pakolaisuutta. Katkos = data puuttuu."
)
NIMET = {
    "DANSK": "Tanskan kansalaiset",
    "VEST": "Länsimainen kansalaisuus (DST)",
    "IKKEVEST": "Ei-länsimainen kansalaisuus (DST)",
}
VARIT = {"DANSK": "#2c5aa0", "VEST": "#4daf4a", "IKKEVEST": "#c45c26"}


def lataa(polku: Path | None = None) -> pd.DataFrame:
    p = polku or (NATIONAL_DIR / CSV_NIMI)
    if not p.exists():
        raise FileNotFoundError(p)
    df = pd.read_csv(p, sep=";")
    df.columns = [c.strip() for c in df.columns]
    return df


def puhdista(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["vuosi"] = pd.to_numeric(out["TID"], errors="coerce").astype("Int64")
    out["lkm"] = pd.to_numeric(out["INDHOLD"], errors="coerce")
    out["ryhma"] = out["STATSB"].astype(str)
    out = out[out["OVERTRÆD"].astype(str) == "1"].copy()
    out["maa"] = "Tanska"
    out["lahde"] = TAULU
    return out[["maa", "vuosi", "ryhma", "lkm", "lahde"]].sort_values(["vuosi", "ryhma"])


def kaavio(df: pd.DataFrame, polku: Path) -> None:
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(11, 6.2))
    for k, nimi in NIMET.items():
        s = df[df["ryhma"] == k].set_index("vuosi").sort_index()
        ax.plot(s.index, s["lkm"], marker="o", color=VARIT[k], label=nimi)
    ax.set_title(
        "Tanska: syylliseksi todetut (DST STRFNA13)\nEi Eurostat-NAT/FOR; ei EU-aggregaattiin"
    )
    ax.set_xlabel("Vuosi")
    ax.set_ylabel("Henkilöitä")
    ax.legend()
    ax.grid(True, alpha=0.3)
    tallenna_kuvio(fig, polku, ALAVIITE)


def aja() -> pd.DataFrame:
    df = lataa()
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    (INTERIM_DIR / "dimensiot_dk_STRFNA13.txt").write_text(
        unique_sarakkeet(df, "STRFNA13"), encoding="utf-8"
    )
    kirjaa_manifest(CSV_NIMI, LAHDE, URL, RAJOITE)
    out = puhdista(df)
    NATIONAL_TABLES.mkdir(parents=True, exist_ok=True)
    out.to_csv(NATIONAL_TABLES / "dk_syylliset.csv", index=False)
    pd.DataFrame({"rajoite": [RAJOITE]}).to_csv(NATIONAL_TABLES / "dk_rajoite.csv", index=False)
    kaavio(out, FIGURES_DIR / "09_dk_syylliset.png")
    print(RAJOITE)
    print(out.to_string(index=False))
    return out


if __name__ == "__main__":
    aja()
