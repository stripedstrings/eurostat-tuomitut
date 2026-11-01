"""Puhdistus: yhtenäiset sarakkeet, NAT/FOR/UNK, täysi maa×vuosi. Ei täyttöä."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.config import (
    CRIME_DATASET,
    EU27,
    MAA_VUOSI_PATH,
    MAAN_NIMET,
    POP_DATASET,
    PROCESSED_DIR,
    VAIHEET,
    YEARS_ABS,
    YEARS_RATE,
)
from src.fetch import load_dataset


def _to_year(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").astype("Int64")


def suodata_oikeus(crime: pd.DataFrame, leg_stat: str, arvo: str) -> pd.DataFrame:
    """Kappalemäärät (NR) yhdelle oikeusvaiheelle. NAT, FOR, TOTAL."""
    df = crime.copy()
    df["TIME_PERIOD"] = _to_year(df["TIME_PERIOD"])
    df["OBS_VALUE"] = pd.to_numeric(df["OBS_VALUE"], errors="coerce")

    mask = (
        (df["leg_stat"] == leg_stat)
        & (df["unit"] == "NR")
        & (df["geo"].isin(EU27))
        & (df["TIME_PERIOD"].isin(YEARS_ABS))
        & (df["citizen"].isin(["NAT", "FOR", "TOTAL"]))
    )
    out = df.loc[mask, ["geo", "TIME_PERIOD", "citizen", "OBS_VALUE", "OBS_FLAG"]].copy()
    out = out.rename(columns={"TIME_PERIOD": "vuosi", "OBS_VALUE": arvo})
    return out


def suodata_vaesto(pop: pd.DataFrame) -> pd.DataFrame:
    """
    Väestö 1.1. kansalaisuusryhmittäin.
    c_birth=TOTAL, sex=T, unit=NR; UNK ja STLS erillään, ei lisätä FOR:iin.
    """
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
        & (df["citizen"].isin(["NAT", "FOR", "UNK", "TOTAL", "STLS"]))
    )
    out = df.loc[mask, ["geo", "TIME_PERIOD", "citizen", "OBS_VALUE", "OBS_FLAG"]].copy()
    out = out.rename(columns={"TIME_PERIOD": "vuosi", "OBS_VALUE": "vaesto"})
    return out


def pivot_ryhma(df: pd.DataFrame, arvo: str, prefiksi: str) -> pd.DataFrame:
    p = df.pivot_table(
        index=["geo", "vuosi"],
        columns="citizen",
        values=arvo,
        aggfunc="first",
    )
    p.columns = [f"{prefiksi}_{c}" for c in p.columns]
    return p.reset_index()


def _jannos_unk(df: pd.DataFrame, prefiksi: str) -> pd.DataFrame:
    """crim_just_ctz:ssä ei ole UNK-koodia; jäännös TOTAL−NAT−FOR jos ≥ 0."""
    total, nat, frn = f"{prefiksi}_TOTAL", f"{prefiksi}_NAT", f"{prefiksi}_FOR"
    if not {total, nat, frn}.issubset(df.columns):
        return df
    jannos = df[total] - df[nat] - df[frn]
    df[f"{prefiksi}_UNK"] = np.where(jannos >= 0, jannos, np.nan)
    return df


def yhdista_paneeli(
    vaiheet: dict[str, pd.DataFrame], vaesto: pd.DataFrame
) -> pd.DataFrame:
    """EU27 × 2008–2024; puuttuvat NaN (ei interpolointia). Ei asteita."""
    runko = pd.MultiIndex.from_product(
        [EU27, YEARS_ABS], names=["geo", "vuosi"]
    ).to_frame(index=False)

    df = runko.merge(pivot_ryhma(vaesto, "vaesto", "vaesto"), on=["geo", "vuosi"], how="left")
    for nimi, taulu in vaiheet.items():
        df = df.merge(pivot_ryhma(taulu, nimi, nimi), on=["geo", "vuosi"], how="left")
        df = _jannos_unk(df, nimi)

    df["maa"] = df["geo"].map(MAAN_NIMET)
    return df.sort_values(["geo", "vuosi"]).reset_index(drop=True)


def puhdista(refresh: bool = False) -> pd.DataFrame:
    crime = load_dataset(CRIME_DATASET, refresh=refresh)
    pop = load_dataset(POP_DATASET, refresh=refresh)
    vaiheet = {
        suomi: suodata_oikeus(crime, koodi, suomi) for koodi, suomi in VAIHEET.items()
    }
    vaesto = suodata_vaesto(pop)
    return yhdista_paneeli(vaiheet, vaesto)


def tallenna(df: pd.DataFrame, polku=MAA_VUOSI_PATH) -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(polku, index=False)


if __name__ == "__main__":
    paneeli = puhdista()
    tallenna(paneeli)
    print(f"Kirjoitettu {MAA_VUOSI_PATH} ({len(paneeli)} riviä)")
