"""EU-sisäiset vs. kolmansien maiden kansalaiset. Ei keksittyjä rikoslukuja."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.clean import _to_year, pivot_ryhma
from src.config import (
    CACHE_DIR,
    CITIZEN_EU27_FOR,
    CITIZEN_NEU27_FOR,
    CRIME_DATASET,
    EU27,
    EU_KOLMAS_PATH,
    EU_KOLMAS_RAJOITE_PATH,
    FIGURES_DIR,
    MAAN_NIMET,
    POP_DATASET,
    TABLES_DIR,
    VARIT,
    YEARS_RATE,
)
from src.fetch import load_dataset
from src.plots import _tallenna

RAJOITE_K1 = (
    "K1-asteita EU-sisäisille vs. kolmansien maiden kansalaisille ei voi laskea: "
    "crim_just_ctz.citizen unique = FOR, NAT, TOTAL. FOR-tuomittuja ei ole jaettu. "
    "Väestössä (migr_pop5ctz) citizen-koodit EU27_2020_FOR ja NEU27_2020_FOR ovat olemassa "
    "(c_birth=TOTAL, sex=T). Niitä ei käytetä rikososoittajan nimittäjänä, koska osoittaja "
    "on vain FOR-yhteensä."
)


def crime_citizen_koodit() -> list[str]:
    df = pd.read_csv(CACHE_DIR / f"{CRIME_DATASET}.csv", usecols=["citizen"])
    return sorted(df["citizen"].dropna().astype(str).unique().tolist())


def k1_jako_mahdollinen(koodit: list[str] | None = None) -> bool:
    k = set(koodit if koodit is not None else crime_citizen_koodit())
    return CITIZEN_EU27_FOR in k or CITIZEN_NEU27_FOR in k


def suodata_vaesto_eu_neu(pop: pd.DataFrame) -> pd.DataFrame:
    df = pop.copy()
    df["TIME_PERIOD"] = _to_year(df["TIME_PERIOD"])
    df["OBS_VALUE"] = pd.to_numeric(df["OBS_VALUE"], errors="coerce")
    df["citizen"] = df["citizen"].astype(str)
    mask = (
        (df["c_birth"] == "TOTAL")
        & (df["sex"] == "T")
        & (df["unit"] == "NR")
        & (df["geo"].isin(EU27))
        & (df["TIME_PERIOD"].isin(YEARS_RATE))
        & (
            df["citizen"].isin(
                ["NAT", "FOR", "UNK", "STLS", CITIZEN_EU27_FOR, CITIZEN_NEU27_FOR]
            )
        )
    )
    out = df.loc[mask, ["geo", "TIME_PERIOD", "citizen", "OBS_VALUE"]].copy()
    out = out.rename(columns={"TIME_PERIOD": "vuosi", "OBS_VALUE": "vaesto"})
    return out


def paneeli_vaesto(pop: pd.DataFrame) -> pd.DataFrame:
    runko = pd.MultiIndex.from_product(
        [EU27, YEARS_RATE], names=["geo", "vuosi"]
    ).to_frame(index=False)
    p = pivot_ryhma(suodata_vaesto_eu_neu(pop), "vaesto", "vaesto")
    df = runko.merge(p, on=["geo", "vuosi"], how="left")
    eu_c = f"vaesto_{CITIZEN_EU27_FOR}"
    neu_c = f"vaesto_{CITIZEN_NEU27_FOR}"
    if eu_c not in df.columns:
        df[eu_c] = np.nan
    if neu_c not in df.columns:
        df[neu_c] = np.nan
    df = df.rename(columns={eu_c: "vaesto_EU27_FOR", neu_c: "vaesto_NEU27_FOR"})
    jannos = df["vaesto_FOR"] - df["vaesto_EU27_FOR"] - df["vaesto_NEU27_FOR"]
    df["vaesto_FOR_jaannos"] = np.where(jannos >= 0, jannos, np.nan)
    df["kelpoinen_jako"] = df["vaesto_EU27_FOR"].notna() & df["vaesto_NEU27_FOR"].notna()
    df["osuus_EU_FOR"] = np.where(
        df["kelpoinen_jako"]
        & ((df["vaesto_EU27_FOR"] + df["vaesto_NEU27_FOR"]) > 0),
        df["vaesto_EU27_FOR"] / (df["vaesto_EU27_FOR"] + df["vaesto_NEU27_FOR"]),
        np.nan,
    )
    df["maa"] = df["geo"].map(MAAN_NIMET)
    df["RR_EU_vs_NEU"] = np.nan
    return df.sort_values(["geo", "vuosi"]).reset_index(drop=True)


def eu_summa(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for y in YEARS_RATE:
        s = df[(df["vuosi"] == y) & df["kelpoinen_jako"]]
        eu = pd.to_numeric(s["vaesto_EU27_FOR"], errors="coerce").sum(min_count=1)
        neu = pd.to_numeric(s["vaesto_NEU27_FOR"], errors="coerce").sum(min_count=1)
        rows.append(
            {
                "vuosi": y,
                "n_maata": int(len(s)),
                "vaesto_EU27_FOR": eu,
                "vaesto_NEU27_FOR": neu,
                "osuus_EU_FOR": (
                    eu / (eu + neu) if pd.notna(eu) and pd.notna(neu) and (eu + neu) > 0 else np.nan
                ),
            }
        )
    return pd.DataFrame(rows)


def kaavio_vaesto(eu: pd.DataFrame, polku) -> None:
    import matplotlib.pyplot as plt

    d = eu.set_index("vuosi").reindex(YEARS_RATE)
    fig, ax = plt.subplots(figsize=(11, 6.5))
    ax.plot(
        d.index,
        d["vaesto_EU27_FOR"] / 1e6,
        marker="o",
        color=VARIT["NAT"],
        label="EU27-kansalaiset (ulkomaalaisia asuinmaassa)",
    )
    ax.plot(
        d.index,
        d["vaesto_NEU27_FOR"] / 1e6,
        marker="o",
        color=VARIT["FOR"],
        label="EU27:n ulkopuolisten maiden kansalaiset",
    )
    ax.set_title(
        "Väestö kansalaisuuden mukaan, EU-aggregaatti 2009–2024\n"
        "Ei tuomitsemisastetta: rikosaineisto ei erota EU- ja kolmansien maiden kansalaisia"
    )
    ax.set_xlabel("Vuosi")
    ax.set_ylabel("Henkilöitä (miljoonaa)")
    ax.set_xticks(YEARS_RATE)
    ax.tick_params(axis="x", rotation=45)
    ax.legend()
    ax.grid(True, alpha=0.3)
    nmin, nmax = int(d["n_maata"].min()), int(d["n_maata"].max())
    ax.text(
        0.01,
        0.99,
        f"Mukana maat, joilla molemmat väestöryhmät: {nmin}–{nmax}. Katkos = data puuttuu.",
        transform=ax.transAxes,
        va="top",
        fontsize=8,
    )
    _tallenna(fig, polku)


def aja() -> pd.DataFrame:
    import matplotlib.pyplot as plt

    plt.switch_backend("Agg")
    koodit = crime_citizen_koodit()
    if k1_jako_mahdollinen(koodit):
        raise RuntimeError("crim_just_ctz sisältää EU/NEU-citizen-koodeja; K1-putki päivitettävä.")
    pop = load_dataset(POP_DATASET)
    df = paneeli_vaesto(pop)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(EU_KOLMAS_PATH, index=False)
    pd.DataFrame(
        {
            "ehto": ["citizen_EU_NEU_crim_just_ctz"],
            "tayttyy": [False],
            "crime_citizen": [",".join(koodit)],
            "vaesto_koodit": [f"{CITIZEN_EU27_FOR},{CITIZEN_NEU27_FOR}"],
            "rajoite": [RAJOITE_K1],
        }
    ).to_csv(EU_KOLMAS_RAJOITE_PATH, index=False)
    eu = eu_summa(df)
    kaavio_vaesto(eu, FIGURES_DIR / "07_vaesto_eu_vs_kolmas.png")
    n = int(df["kelpoinen_jako"].sum())
    print(RAJOITE_K1)
    print(f"Kirjoitettu {EU_KOLMAS_PATH} kelpoinen_jako={n}/{len(df)}")
    print(eu.to_string(index=False))
    return df


if __name__ == "__main__":
    aja()
