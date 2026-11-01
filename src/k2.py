"""K2: työllisyys, koulutus, oleskelulupa. Kuvaileva; ei K1-selittäjä."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from src.config import (
    DPI_KUVA,
    EU27,
    FIGURES_DIR,
    MAAN_NIMET,
    MANIFEST_PATH,
    TABLES_DIR,
    YEARS_RATE,
)
from src.fetch import K2_DATASETS, load_dataset

LFS_CITIZEN = ["NAT", "FOR", "EU27_2020_FOR", "NEU27_2020_FOR"]
LUPA_SYYT_FIRST = ["EDUC", "EMP", "FAM", "OTH"]
LUPA_SYYT_VALID = ["EDUC", "EMP", "FAM", "OTH", "RFG", "SPROT"]

RAJOITE = (
    "K2 on kuvaileva eikä sitä yhdistetä K1:n tuomitsemisasteisiin selittäjäksi "
    "(ekologinen virhepäätelmä). LFS (lfsa_ergan, lfsa_urgan, edat_lfs_9911) on "
    "otantatutkimus; citizen-koodit NAT/FOR/EU27_2020_FOR/NEU27_2020_FOR. "
    "crim_just_ctz erottaa vain NAT/FOR/TOTAL. Oleskeluluvat (migr_resfirst, "
    "migr_resvalid) koskevat kolmansien maiden kansalaisia, ei EU-kansalaisia."
)

SYY_NIMET = {
    "EDUC": "Koulutus",
    "EMP": "Työ",
    "FAM": "Perhe",
    "OTH": "Muu",
    "RFG": "Pakolaisasema",
    "SPROT": "Toissijainen suojelu",
    "TOTAL": "Yhteensä",
}
CIT_NIMET = {
    "NAT": "Oman maan kansalaiset",
    "FOR": "Ulkomaan kansalaiset",
    "EU27_2020_FOR": "EU27-kansalaiset (ulkomaalaisia)",
    "NEU27_2020_FOR": "EU27:n ulkopuolisten maiden kansalaiset",
}
VARIT_CIT = {
    "NAT": "#2c5aa0",
    "FOR": "#c45c26",
    "EU27_2020_FOR": "#4daf4a",
    "NEU27_2020_FOR": "#984ea3",
}


def _vuosi(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce").astype("Int64")


def suodata_lfs(
    df: pd.DataFrame, *, age: str, citizen: list[str], geos: list[str]
) -> pd.DataFrame:
    x = df.copy()
    x["TIME_PERIOD"] = _vuosi(x["TIME_PERIOD"])
    x["OBS_VALUE"] = pd.to_numeric(x["OBS_VALUE"], errors="coerce")
    mask = (
        (x["unit"] == "PC")
        & (x["sex"] == "T")
        & (x["age"] == age)
        & (x["citizen"].isin(citizen))
        & (x["geo"].isin(geos))
        & (x["TIME_PERIOD"].isin(YEARS_RATE))
    )
    out = x.loc[mask, ["geo", "TIME_PERIOD", "citizen", "OBS_VALUE", "OBS_FLAG"]].copy()
    return out.rename(columns={"TIME_PERIOD": "vuosi", "OBS_VALUE": "arvo"})


def suodata_koulutus(df: pd.DataFrame, geos: list[str]) -> pd.DataFrame:
    x = df.copy()
    x["TIME_PERIOD"] = _vuosi(x["TIME_PERIOD"])
    x["OBS_VALUE"] = pd.to_numeric(x["OBS_VALUE"], errors="coerce")
    mask = (
        (x["unit"] == "PC")
        & (x["sex"] == "T")
        & (x["age"] == "Y25-64")
        & (x["isced11"].isin(["ED0-2", "ED3_4", "ED5-8"]))
        & (x["citizen"].isin(LFS_CITIZEN))
        & (x["geo"].isin(geos))
        & (x["TIME_PERIOD"].isin(YEARS_RATE))
    )
    out = x.loc[mask, ["geo", "TIME_PERIOD", "citizen", "isced11", "OBS_VALUE", "OBS_FLAG"]].copy()
    return out.rename(columns={"TIME_PERIOD": "vuosi", "OBS_VALUE": "arvo"})


def suodata_luvat(df: pd.DataFrame, syyt: list[str], geos: list[str]) -> pd.DataFrame:
    x = df.copy()
    x["TIME_PERIOD"] = _vuosi(x["TIME_PERIOD"])
    x["OBS_VALUE"] = pd.to_numeric(x["OBS_VALUE"], errors="coerce")
    mask = (
        (x["duration"] == "TOTAL")
        & (x["unit"] == "PER")
        & (x["citizen"] == "TOTAL")
        & (x["reason"].isin(syyt + ["TOTAL"]))
        & (x["geo"].isin(geos))
        & (x["TIME_PERIOD"].isin(list(range(2008, 2025))))
    )
    out = x.loc[mask, ["geo", "TIME_PERIOD", "reason", "OBS_VALUE", "OBS_FLAG"]].copy()
    return out.rename(columns={"TIME_PERIOD": "vuosi", "OBS_VALUE": "lkm"})


def lupa_osuudet(df: pd.DataFrame) -> pd.DataFrame:
    p = df.pivot_table(index=["geo", "vuosi"], columns="reason", values="lkm", aggfunc="first")
    p = p.reset_index()
    if "TOTAL" not in p.columns:
        p["TOTAL"] = np.nan
    for c in p.columns:
        if c in {"geo", "vuosi", "TOTAL"}:
            continue
        p[f"osuus_{c}"] = np.where(
            p["TOTAL"].notna() & (p["TOTAL"] > 0) & p[c].notna(),
            p[c] / p["TOTAL"],
            np.nan,
        )
    return p


def _k2_alaviite() -> str:
    man = pd.read_csv(MANIFEST_PATH)
    rivit = man[man["tiedosto"].isin([f"{k}.csv" for k in K2_DATASETS])]
    pvm = str(rivit["hakupäivä"].max()) if len(rivit) else ""
    return (
        f"Lähde: Eurostat lfsa_ergan, lfsa_urgan, edat_lfs_9911, migr_resfirst, "
        f"migr_resvalid, haettu {pvm}. "
        "Kuvaileva K2: ei K1:n selittäjä (ekologinen virhepäätelmä). "
        "LFS-kansalaisuusluokat eivät ole samat kuin crim_just_ctz (NAT/FOR/TOTAL). "
        "Oleskeluluvat: vain kolmansien maiden kansalaiset. "
        "Katkos viivassa = data puuttuu. Ei täyttöä."
    )


def _tallenna(fig, polku: Path) -> None:
    import matplotlib.pyplot as plt

    fig.text(0.5, 0.01, _k2_alaviite(), ha="center", va="bottom", fontsize=7, wrap=True)
    fig.tight_layout(rect=[0.03, 0.12, 0.99, 0.96])
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(polku, dpi=DPI_KUVA)
    plt.close(fig)


def kaavio_tyollisyys(eu: pd.DataFrame, polku: Path) -> None:
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(11, 6.2))
    for cit in LFS_CITIZEN:
        s = eu[eu["citizen"] == cit].set_index("vuosi").reindex(YEARS_RATE)
        ax.plot(s.index, s["arvo"], marker="o", color=VARIT_CIT[cit], label=CIT_NIMET[cit])
    ax.set_title(
        "Työllisyysaste 15–64 v, Eurostat EU-27 (LFS)\nKuvaileva K2, ei tuomitsemisasteen selittäjä"
    )
    ax.set_xlabel("Vuosi")
    ax.set_ylabel("%")
    ax.set_xticks(YEARS_RATE)
    ax.tick_params(axis="x", rotation=45)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    _tallenna(fig, polku)


def kaavio_koulutus(eu: pd.DataFrame, polku: Path) -> None:
    import matplotlib.pyplot as plt

    korkea = eu[eu["isced11"] == "ED5-8"]
    fig, ax = plt.subplots(figsize=(11, 6.2))
    for cit in LFS_CITIZEN:
        s = korkea[korkea["citizen"] == cit].set_index("vuosi").reindex(YEARS_RATE)
        ax.plot(s.index, s["arvo"], marker="o", color=VARIT_CIT[cit], label=CIT_NIMET[cit])
    ax.set_title(
        "Korkea-asteen tutkinto (ISCED 5–8), 25–64 v, Eurostat EU-27 (LFS)\n"
        "Kuvaileva K2, ei tuomitsemisasteen selittäjä"
    )
    ax.set_xlabel("Vuosi")
    ax.set_ylabel("% väestöstä")
    ax.set_xticks(YEARS_RATE)
    ax.tick_params(axis="x", rotation=45)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    _tallenna(fig, polku)


def kaavio_luvat(osuus: pd.DataFrame, polku: Path) -> None:
    import matplotlib.pyplot as plt

    d = osuus[osuus["geo"] == "EU27_2020"].set_index("vuosi").reindex(list(range(2008, 2025)))
    fig, ax = plt.subplots(figsize=(11, 6.2))
    syyt = [c for c in LUPA_SYYT_FIRST if f"osuus_{c}" in d.columns]
    varit = ["#2c5aa0", "#c45c26", "#4daf4a", "#984ea3"]
    for c, col in zip(syyt, varit):
        ax.plot(d.index, d[f"osuus_{c}"] * 100, marker="o", color=col, label=SYY_NIMET[c])
    ax.set_title(
        "Ensimmäiset oleskeluluvat perusteen mukaan, EU-27 (osuus TOTAL:sta)\n"
        "Vain kolmansien maiden kansalaiset; ei K1-selittäjä. Katkos = puuttuva."
    )
    ax.set_xlabel("Vuosi")
    ax.set_ylabel("%")
    ax.legend(loc="lower left", fontsize=8)
    ax.grid(True, alpha=0.3)
    _tallenna(fig, polku)


def aja() -> dict[str, pd.DataFrame]:
    import matplotlib.pyplot as plt

    plt.switch_backend("Agg")
    geos = EU27 + ["EU27_2020"]
    ergan = load_dataset("lfsa_ergan")
    urgan = load_dataset("lfsa_urgan")
    edat = load_dataset("edat_lfs_9911")
    first = load_dataset("migr_resfirst")
    valid = load_dataset("migr_resvalid")

    tyo = suodata_lfs(ergan, age="Y15-64", citizen=LFS_CITIZEN, geos=geos)
    tyo["maa"] = tyo["geo"].map(lambda g: MAAN_NIMET.get(g, g))
    tyot = suodata_lfs(urgan, age="Y15-64", citizen=LFS_CITIZEN, geos=geos)
    tyot["maa"] = tyot["geo"].map(lambda g: MAAN_NIMET.get(g, g))
    kou = suodata_koulutus(edat, geos)
    kou["maa"] = kou["geo"].map(lambda g: MAAN_NIMET.get(g, g))
    lup_e = lupa_osuudet(suodata_luvat(first, LUPA_SYYT_FIRST, geos))
    lup_v = lupa_osuudet(suodata_luvat(valid, LUPA_SYYT_VALID, geos))

    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    tyo.to_csv(TABLES_DIR / "k2_tyollisyys.csv", index=False)
    tyot.to_csv(TABLES_DIR / "k2_tyottomyys.csv", index=False)
    kou.to_csv(TABLES_DIR / "k2_koulutus.csv", index=False)
    lup_e.to_csv(TABLES_DIR / "k2_luvat_ensimmaiset.csv", index=False)
    lup_v.to_csv(TABLES_DIR / "k2_luvat_voimassa.csv", index=False)
    pd.DataFrame({"rajoite": [RAJOITE]}).to_csv(TABLES_DIR / "k2_rajoite.csv", index=False)

    kaavio_tyollisyys(tyo[tyo["geo"] == "EU27_2020"], FIGURES_DIR / "08_k2_tyollisyys.png")
    kaavio_koulutus(kou[kou["geo"] == "EU27_2020"], FIGURES_DIR / "08_k2_koulutus.png")
    kaavio_luvat(lup_e, FIGURES_DIR / "08_k2_oleskeluluvat.png")
    print(RAJOITE)
    print(f"tyollisyys riveja={len(tyo)} koulutus={len(kou)} luvat_e={len(lup_e)}")
    return {"tyollisyys": tyo, "tyottomyys": tyot, "koulutus": kou, "luvat": lup_e}


if __name__ == "__main__":
    aja()
