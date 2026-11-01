"""Suodatus, yhdistäminen, peittävyys ja EU-aggregaatti. Puuttuvia ei täytetä."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.config import EU27, MAAN_NIMET, YEARS_ABS, YEARS_AVG, YEARS_RATE


def _to_year(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").astype("Int64")


def suodata_tuomitut(crime: pd.DataFrame) -> pd.DataFrame:
    """Vain tuomitut (PER_CNV) ja kappalemäärät (NR). NAT, FOR, TOTAL, ei P_HTHAB."""
    df = crime.copy()
    df["TIME_PERIOD"] = _to_year(df["TIME_PERIOD"])
    df["OBS_VALUE"] = pd.to_numeric(df["OBS_VALUE"], errors="coerce")

    mask = (
        (df["leg_stat"] == "PER_CNV")
        & (df["unit"] == "NR")
        & (df["geo"].isin(EU27))
        & (df["TIME_PERIOD"].isin(YEARS_ABS))
        & (df["citizen"].isin(["NAT", "FOR", "TOTAL"]))
    )
    out = df.loc[mask, ["geo", "TIME_PERIOD", "citizen", "OBS_VALUE", "OBS_FLAG"]].copy()
    out = out.rename(columns={"TIME_PERIOD": "vuosi", "OBS_VALUE": "tuomitut"})
    return out


def suodata_vaesto(pop: pd.DataFrame) -> pd.DataFrame:
    """
    Väestö 1.1. kansalaisuusryhmittäin.
    API-tarkistus: c_birth=TOTAL, sex=T, unit=NR, citizen in NAT/FOR/UNK/TOTAL.
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
        & (df["TIME_PERIOD"].isin(YEARS_RATE + [2025]))
        & (df["citizen"].isin(["NAT", "FOR", "UNK", "TOTAL", "STLS"]))
    )
    out = df.loc[mask, ["geo", "TIME_PERIOD", "citizen", "OBS_VALUE", "OBS_FLAG"]].copy()
    out = out.rename(columns={"TIME_PERIOD": "vuosi", "OBS_VALUE": "vaesto"})
    return out


def _pivot_group(df: pd.DataFrame, arvo: str, prefiksi: str) -> pd.DataFrame:
    p = df.pivot_table(
        index=["geo", "vuosi"],
        columns="citizen",
        values=arvo,
        aggfunc="first",
    )
    p.columns = [f"{prefiksi}_{c}" for c in p.columns]
    return p.reset_index()


def yhdista(tuomitut: pd.DataFrame, vaesto: pd.DataFrame) -> pd.DataFrame:
    """Täysi maa×vuosi-ruudukko; puuttuvat jäävät NaN:iksi (ei interpolointia)."""
    runko = pd.MultiIndex.from_product(
        [EU27, YEARS_ABS], names=["geo", "vuosi"]
    ).to_frame(index=False)

    t = _pivot_group(tuomitut, "tuomitut", "tuomitut")
    v = _pivot_group(vaesto, "vaesto", "vaesto")

    df = runko.merge(t, on=["geo", "vuosi"], how="left")
    df = df.merge(v, on=["geo", "vuosi"], how="left")
    df["maa"] = df["geo"].map(MAAN_NIMET)

    # Tuntematon kansalaisuus: TOTAL − NAT − FOR, vain kun kaikki kolme on ilmoitettu.
    # Negatiivista jäännöstä ei käytetä (jätetään NaN).
    if {"tuomitut_TOTAL", "tuomitut_NAT", "tuomitut_FOR"}.issubset(df.columns):
        jannos = df["tuomitut_TOTAL"] - df["tuomitut_NAT"] - df["tuomitut_FOR"]
        df["tuomitut_UNK"] = np.where(jannos >= 0, jannos, np.nan)
    else:
        df["tuomitut_UNK"] = np.nan

    # Suhteelliset luvut vain 2009–2024 ja vain kun sekä tuomitut että väestö > 0.
    df["per_100k_NAT"] = np.where(
        (df["vuosi"] >= 2009) & (df["vaesto_NAT"] > 0),
        df["tuomitut_NAT"] / df["vaesto_NAT"] * 100_000,
        np.nan,
    )
    df["per_100k_FOR"] = np.where(
        (df["vuosi"] >= 2009) & (df["vaesto_FOR"] > 0),
        df["tuomitut_FOR"] / df["vaesto_FOR"] * 100_000,
        np.nan,
    )
    df["suhde_FOR_NAT"] = np.where(
        df["per_100k_NAT"] > 0,
        df["per_100k_FOR"] / df["per_100k_NAT"],
        np.nan,
    )
    return df.sort_values(["geo", "vuosi"]).reset_index(drop=True)


def coverage_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Maa- ja vuosikohtainen puuttuvuus (ei täytetä)."""
    rows = []
    for _, r in df.iterrows():
        puuttuu = []
        if pd.isna(r.get("tuomitut_NAT")):
            puuttuu.append("tuomitut_NAT")
        if pd.isna(r.get("tuomitut_FOR")):
            puuttuu.append("tuomitut_FOR")
        if r["vuosi"] >= 2009:
            if pd.isna(r.get("vaesto_NAT")):
                puuttuu.append("vaesto_NAT")
            if pd.isna(r.get("vaesto_FOR")):
                puuttuu.append("vaesto_FOR")
        else:
            puuttuu.append("vaesto_ei_saatavilla_2008")

        huom = []
        total = r.get("tuomitut_TOTAL")
        nat = r.get("tuomitut_NAT")
        frn = r.get("tuomitut_FOR")
        if pd.notna(total) and total > 0 and nat == 0 and frn == 0:
            huom.append("NAT_ja_FOR_nolla_vaikka_TOTAL>0")
        if pd.notna(r.get("tuomitut_UNK")) and r["tuomitut_UNK"] > 0:
            huom.append(f"tuntematon_kansalaisuus={int(r['tuomitut_UNK'])}")

        rows.append(
            {
                "geo": r["geo"],
                "maa": r["maa"],
                "vuosi": r["vuosi"],
                "on_tuomitut_NAT": bool(pd.notna(r.get("tuomitut_NAT"))),
                "on_tuomitut_FOR": bool(pd.notna(r.get("tuomitut_FOR"))),
                "on_tuomitut_molemmat": bool(
                    pd.notna(r.get("tuomitut_NAT")) and pd.notna(r.get("tuomitut_FOR"))
                ),
                "on_vaesto_NAT": bool(pd.notna(r.get("vaesto_NAT"))),
                "on_vaesto_FOR": bool(pd.notna(r.get("vaesto_FOR"))),
                "on_per_100k_NAT": bool(pd.notna(r.get("per_100k_NAT"))),
                "on_per_100k_FOR": bool(pd.notna(r.get("per_100k_FOR"))),
                "on_suhde": bool(pd.notna(r.get("suhde_FOR_NAT"))),
                "puuttuvat_kentat": ";".join(puuttuu) if puuttuu else "",
                "huomautus": ";".join(huom),
            }
        )
    return pd.DataFrame(rows)


def eu_aggregaatti(df: pd.DataFrame, vuodet: list[int]) -> pd.DataFrame:
    """
    EU-luku vain maista, joilla on kyseisenä vuonna data MOLEMMILLE ryhmille.
    Absoluuttiset: molemmat tuomitut-sarjat. Suhteelliset: lisäksi molemmat väestöt.
    Summataan; ei mediaania.
    """
    rows = []
    for y in vuodet:
        slice_y = df[df["vuosi"] == y]
        molemmat_tuom = slice_y[
            slice_y["tuomitut_NAT"].notna() & slice_y["tuomitut_FOR"].notna()
        ]
        molemmat_aste = molemmat_tuom[
            molemmat_tuom["vaesto_NAT"].notna() & molemmat_tuom["vaesto_FOR"].notna()
        ]

        tu_nat = molemmat_tuom["tuomitut_NAT"].sum(min_count=1)
        tu_for = molemmat_tuom["tuomitut_FOR"].sum(min_count=1)

        row = {
            "vuosi": y,
            "n_maata_abs": int(len(molemmat_tuom)),
            "maat_abs": ",".join(molemmat_tuom["geo"].tolist()),
            "tuomitut_NAT": tu_nat,
            "tuomitut_FOR": tu_for,
            "n_maata_aste": int(len(molemmat_aste)),
            "maat_aste": ",".join(molemmat_aste["geo"].tolist()),
            "vaesto_NAT": np.nan,
            "vaesto_FOR": np.nan,
            "per_100k_NAT": np.nan,
            "per_100k_FOR": np.nan,
        }
        if y >= 2009 and len(molemmat_aste):
            ve_nat = molemmat_aste["vaesto_NAT"].sum(min_count=1)
            ve_for = molemmat_aste["vaesto_FOR"].sum(min_count=1)
            tu_nat_a = molemmat_aste["tuomitut_NAT"].sum(min_count=1)
            tu_for_a = molemmat_aste["tuomitut_FOR"].sum(min_count=1)
            row["vaesto_NAT"] = ve_nat
            row["vaesto_FOR"] = ve_for
            row["per_100k_NAT"] = (
                tu_nat_a / ve_nat * 100_000 if pd.notna(ve_nat) and ve_nat > 0 else np.nan
            )
            row["per_100k_FOR"] = (
                tu_for_a / ve_for * 100_000 if pd.notna(ve_for) and ve_for > 0 else np.nan
            )
        rows.append(row)
    return pd.DataFrame(rows)


def keskiarvo_2020_2024(df: pd.DataFrame) -> pd.DataFrame:
    """
    Viiden vuoden keskiarvo maittain. Vain vuodet, joilla molemmat ryhmät ovat
    ei-NaN; puuttuvia vuosia ei täytetä. Keskiarvo voi perustua alle viiteen vuoteen.
    """
    rows = []
    for geo in EU27:
        s = df[(df["geo"] == geo) & (df["vuosi"].isin(YEARS_AVG))]
        molemmat = s[s["per_100k_NAT"].notna() & s["per_100k_FOR"].notna()]
        n = int(len(molemmat))
        if n == 0:
            rows.append(
                {
                    "geo": geo,
                    "maa": MAAN_NIMET[geo],
                    "n_vuotta": 0,
                    "vuodet": "",
                    "per_100k_NAT": np.nan,
                    "per_100k_FOR": np.nan,
                    "suhde_FOR_NAT": np.nan,
                }
            )
            continue
        nat = molemmat["per_100k_NAT"].mean()
        frn = molemmat["per_100k_FOR"].mean()
        rows.append(
            {
                "geo": geo,
                "maa": MAAN_NIMET[geo],
                "n_vuotta": n,
                "vuodet": ",".join(str(int(v)) for v in molemmat["vuosi"]),
                "per_100k_NAT": nat,
                "per_100k_FOR": frn,
                "suhde_FOR_NAT": frn / nat if pd.notna(nat) and nat > 0 else np.nan,
            }
        )
    return pd.DataFrame(rows)
