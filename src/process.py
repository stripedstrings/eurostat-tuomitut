"""Suodatus, yhdistäminen, peittävyys ja EU-aggregaatti. Puuttuvia ei täytetä."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.config import EU27, MAAN_NIMET, VAIHEET, YEARS_ABS, YEARS_AVG, YEARS_RATE


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


def _asteet(df: pd.DataFrame, prefiksi: str) -> pd.DataFrame:
    nat = f"{prefiksi}_NAT"
    frn = f"{prefiksi}_FOR"
    if {nat, frn, "vaesto_NAT", "vaesto_FOR"}.issubset(df.columns):
        df[f"{prefiksi}_per_100k_NAT"] = np.where(
            (df["vuosi"] >= 2009) & (df["vaesto_NAT"] > 0),
            df[nat] / df["vaesto_NAT"] * 100_000,
            np.nan,
        )
        df[f"{prefiksi}_per_100k_FOR"] = np.where(
            (df["vuosi"] >= 2009) & (df["vaesto_FOR"] > 0),
            df[frn] / df["vaesto_FOR"] * 100_000,
            np.nan,
        )
        df[f"{prefiksi}_suhde_FOR_NAT"] = np.where(
            df[f"{prefiksi}_per_100k_NAT"] > 0,
            df[f"{prefiksi}_per_100k_FOR"] / df[f"{prefiksi}_per_100k_NAT"],
            np.nan,
        )
    return df


def yhdista(vaiheet: dict[str, pd.DataFrame], vaesto: pd.DataFrame) -> pd.DataFrame:
    """Täysi maa×vuosi-ruudukko; puuttuvat jäävät NaN:iksi (ei interpolointia)."""
    runko = pd.MultiIndex.from_product(
        [EU27, YEARS_ABS], names=["geo", "vuosi"]
    ).to_frame(index=False)

    df = runko.merge(_pivot_group(vaesto, "vaesto", "vaesto"), on=["geo", "vuosi"], how="left")
    for nimi, taulu in vaiheet.items():
        df = df.merge(_pivot_group(taulu, nimi, nimi), on=["geo", "vuosi"], how="left")
        df = _asteet(df, nimi)

        total, nat, frn = f"{nimi}_TOTAL", f"{nimi}_NAT", f"{nimi}_FOR"
        if {total, nat, frn}.issubset(df.columns):
            jannos = df[total] - df[nat] - df[frn]
            df[f"{nimi}_UNK"] = np.where(jannos >= 0, jannos, np.nan)

    df["maa"] = df["geo"].map(MAAN_NIMET)
    # Vanhat sarakenimet tuomittujen EU-kaavioita varten
    if "tuomitut_per_100k_NAT" in df.columns:
        df["per_100k_NAT"] = df["tuomitut_per_100k_NAT"]
        df["per_100k_FOR"] = df["tuomitut_per_100k_FOR"]
        df["suhde_FOR_NAT"] = df["tuomitut_suhde_FOR_NAT"]
    return df.sort_values(["geo", "vuosi"]).reset_index(drop=True)


def coverage_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Maa- ja vuosikohtainen puuttuvuus (ei täytetä)."""
    rows = []
    for _, r in df.iterrows():
        puuttuu = []
        for vaihe in VAIHEET.values():
            for grp in ("NAT", "FOR"):
                col = f"{vaihe}_{grp}"
                if col in df.columns and pd.isna(r.get(col)):
                    puuttuu.append(col)
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
            huom.append(f"tuntematon_kansalaisuus_tuomitut={int(r['tuomitut_UNK'])}")

        rows.append(
            {
                "geo": r["geo"],
                "maa": r["maa"],
                "vuosi": int(r["vuosi"]),
                "on_tuomitut_NAT": bool(pd.notna(r.get("tuomitut_NAT"))),
                "on_tuomitut_FOR": bool(pd.notna(r.get("tuomitut_FOR"))),
                "on_epaillyt_NAT": bool(pd.notna(r.get("epaillyt_NAT"))),
                "on_epaillyt_FOR": bool(pd.notna(r.get("epaillyt_FOR"))),
                "on_syyteeseen_NAT": bool(pd.notna(r.get("syyteeseen_NAT"))),
                "on_syyteeseen_FOR": bool(pd.notna(r.get("syyteeseen_FOR"))),
                "on_vaesto_NAT": bool(pd.notna(r.get("vaesto_NAT"))),
                "on_vaesto_FOR": bool(pd.notna(r.get("vaesto_FOR"))),
                "on_tuomitut_suhde": bool(pd.notna(r.get("tuomitut_suhde_FOR_NAT"))),
                "puuttuvat_kentat": ";".join(puuttuu) if puuttuu else "",
                "huomautus": ";".join(huom),
            }
        )
    return pd.DataFrame(rows)


def eu_aggregaatti(df: pd.DataFrame, vuodet: list[int], prefiksi: str = "tuomitut") -> pd.DataFrame:
    """
    EU-luku vain maista, joilla on kyseisenä vuonna data MOLEMMILLE ryhmille.
    Absoluuttiset: molemmat lukumäärät. Suhteelliset: lisäksi molemmat väestöt.
    """
    nat_c, for_c = f"{prefiksi}_NAT", f"{prefiksi}_FOR"
    rows = []
    for y in vuodet:
        slice_y = df[df["vuosi"] == y]
        molemmat = slice_y[slice_y[nat_c].notna() & slice_y[for_c].notna()]
        molemmat_aste = molemmat[molemmat["vaesto_NAT"].notna() & molemmat["vaesto_FOR"].notna()]

        n_nat = molemmat[nat_c].sum(min_count=1)
        n_for = molemmat[for_c].sum(min_count=1)
        row = {
            "vuosi": y,
            "vaihe": prefiksi,
            "n_maata_abs": int(len(molemmat)),
            "maat_abs": ",".join(molemmat["geo"].tolist()),
            "tuomitut_NAT": n_nat,
            "tuomitut_FOR": n_for,
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
            tu_nat_a = molemmat_aste[nat_c].sum(min_count=1)
            tu_for_a = molemmat_aste[for_c].sum(min_count=1)
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


def keskiarvo_2020_2024(df: pd.DataFrame, prefiksi: str = "tuomitut") -> pd.DataFrame:
    """Keskiarvo vuosista, joilla molemmat ryhmät ovat ei-NaN. Puuttuvia ei täytetä."""
    nat_c = f"{prefiksi}_per_100k_NAT"
    for_c = f"{prefiksi}_per_100k_FOR"
    rows = []
    for geo in EU27:
        s = df[(df["geo"] == geo) & (df["vuosi"].isin(YEARS_AVG))]
        molemmat = s[s[nat_c].notna() & s[for_c].notna()] if nat_c in s.columns else s.iloc[0:0]
        n = int(len(molemmat))
        if n == 0:
            rows.append(
                {
                    "geo": geo,
                    "maa": MAAN_NIMET[geo],
                    "vaihe": prefiksi,
                    "n_vuotta": 0,
                    "vuodet": "",
                    "per_100k_NAT": np.nan,
                    "per_100k_FOR": np.nan,
                    "suhde_FOR_NAT": np.nan,
                }
            )
            continue
        nat = molemmat[nat_c].mean()
        frn = molemmat[for_c].mean()
        rows.append(
            {
                "geo": geo,
                "maa": MAAN_NIMET[geo],
                "vaihe": prefiksi,
                "n_vuotta": n,
                "vuodet": ",".join(str(int(v)) for v in molemmat["vuosi"]),
                "per_100k_NAT": nat,
                "per_100k_FOR": frn,
                "suhde_FOR_NAT": frn / nat if pd.notna(nat) and nat > 0 else np.nan,
            }
        )
    return pd.DataFrame(rows)
