"""Aste per 100 000, RR ja Poisson-luottamusvälit. Ei täyttöä."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import chi2, norm

from src.config import (
    ASTEET_PATH,
    EU27,
    EU_AGGR_PATH,
    KAUSI_RR_PATH,
    MAA_VUOSI_PATH,
    MAAN_NIMET,
    TABLES_DIR,
    YEARS_ABS,
    YEARS_AVG,
    YEARS_RATE,
)

Z_95 = float(norm.ppf(0.975))
ALPHA = 0.05
D_EPALUOTETTAVA = 10
D_GARWOOD = 20


def aste_per_100k(d: pd.Series, pop: pd.Series) -> pd.Series:
    d_n = pd.to_numeric(d, errors="coerce")
    p_n = pd.to_numeric(pop, errors="coerce")
    ok = d_n.notna() & p_n.notna() & (p_n > 0)
    out = pd.Series(np.nan, index=d.index, dtype="float64")
    out.loc[ok] = d_n.loc[ok] / p_n.loc[ok] * 100_000
    return out


def garwood_lkm_ci(d: pd.Series, alpha: float = ALPHA) -> tuple[pd.Series, pd.Series]:
    """Garwood (chi2) -väli Poisson-lukumäärälle. k=0: ala=0."""
    k = pd.to_numeric(d, errors="coerce").to_numpy(dtype=float)
    lo = np.full(k.shape, np.nan)
    hi = np.full(k.shape, np.nan)
    ok = np.isfinite(k) & (k >= 0)
    nolla = ok & (k == 0)
    pos = ok & (k > 0)
    lo[nolla] = 0.0
    lo[pos] = chi2.ppf(alpha / 2, 2.0 * k[pos]) / 2.0
    hi[ok] = chi2.ppf(1.0 - alpha / 2, 2.0 * (k[ok] + 1.0)) / 2.0
    idx = d.index
    return pd.Series(lo, index=idx), pd.Series(hi, index=idx)


def aste_ci(d: pd.Series, pop: pd.Series, alpha: float = ALPHA) -> tuple[pd.Series, pd.Series]:
    lo_d, hi_d = garwood_lkm_ci(d, alpha=alpha)
    p_n = pd.to_numeric(pop, errors="coerce")
    ok = p_n.notna() & (p_n > 0) & lo_d.notna()
    lo = pd.Series(np.nan, index=d.index, dtype="float64")
    hi = pd.Series(np.nan, index=d.index, dtype="float64")
    lo.loc[ok] = lo_d.loc[ok] / p_n.loc[ok] * 100_000
    hi.loc[ok] = hi_d.loc[ok] / p_n.loc[ok] * 100_000
    return lo, hi


def rr_log_ci(
    rr: pd.Series, d_nat: pd.Series, d_for: pd.Series
) -> tuple[pd.Series, pd.Series]:
    """ln(RR) ± z * sqrt(1/D_FOR + 1/D_NAT). Vaatii D>0 molemmissa."""
    dn = pd.to_numeric(d_nat, errors="coerce")
    df = pd.to_numeric(d_for, errors="coerce")
    r = pd.to_numeric(rr, errors="coerce")
    ok = r.notna() & (r > 0) & (dn > 0) & (df > 0)
    lo = pd.Series(np.nan, index=rr.index, dtype="float64")
    hi = pd.Series(np.nan, index=rr.index, dtype="float64")
    se = np.sqrt(1.0 / df.loc[ok] + 1.0 / dn.loc[ok])
    ln_rr = np.log(r.loc[ok])
    lo.loc[ok] = np.exp(ln_rr - Z_95 * se)
    hi.loc[ok] = np.exp(ln_rr + Z_95 * se)
    return lo, hi


def laske_asteet(paneeli: pd.DataFrame) -> pd.DataFrame:
    """Kaikki maa–vuodet säilyvät. Puuttuva = NaN."""
    df = paneeli.copy()
    d_n = df["tuomitut_NAT"]
    d_f = df["tuomitut_FOR"]
    p_n = df["vaesto_NAT"]
    p_f = df["vaesto_FOR"]

    df["aste_NAT"] = aste_per_100k(d_n, p_n)
    df["aste_FOR"] = aste_per_100k(d_f, p_f)
    df["aste_NAT_lo"], df["aste_NAT_hi"] = aste_ci(d_n, p_n)
    df["aste_FOR_lo"], df["aste_FOR_hi"] = aste_ci(d_f, p_f)

    kelp = (
        d_n.notna()
        & d_f.notna()
        & p_n.notna()
        & p_f.notna()
        & (p_n > 0)
        & (p_f > 0)
    )
    df["kelpoinen_aste"] = kelp
    df["RR"] = np.where(
        kelp & (df["aste_NAT"] > 0),
        df["aste_FOR"] / df["aste_NAT"],
        np.nan,
    )
    df["RR_lo"], df["RR_hi"] = rr_log_ci(df["RR"], d_n, d_f)

    d_n_ok = pd.to_numeric(d_n, errors="coerce")
    d_f_ok = pd.to_numeric(d_f, errors="coerce")
    df["epaluotettava"] = kelp & ((d_n_ok < D_EPALUOTETTAVA) | (d_f_ok < D_EPALUOTETTAVA))
    df["varoitus_pieni_D"] = kelp & ((d_n_ok < D_GARWOOD) | (d_f_ok < D_GARWOOD))
    return df


def eu_aggregaatti(asteet: pd.DataFrame, paneeli: pd.DataFrame) -> pd.DataFrame:
    """Summaa vain maat, joilla molemmat ryhmät (ja asteissa myös nimittäjät)."""
    rows: list[dict[str, object]] = []
    for y in YEARS_ABS:
        p_y = paneeli[paneeli["vuosi"] == y]
        abs_ok = p_y["tuomitut_NAT"].notna() & p_y["tuomitut_FOR"].notna()
        abs_df = p_y.loc[abs_ok]
        a_y = asteet[asteet["vuosi"] == y]
        aste_df = a_y.loc[a_y["kelpoinen_aste"]]

        eu_tot = pd.to_numeric(p_y.get("vaesto_TOTAL"), errors="coerce").sum(min_count=1)
        mukana_vaesto = (
            pd.to_numeric(aste_df["vaesto_NAT"], errors="coerce").sum(min_count=1)
            + pd.to_numeric(aste_df["vaesto_FOR"], errors="coerce").sum(min_count=1)
            if len(aste_df)
            else np.nan
        )
        osuus = (
            mukana_vaesto / eu_tot
            if pd.notna(mukana_vaesto) and pd.notna(eu_tot) and eu_tot > 0
            else np.nan
        )

        d_n = pd.to_numeric(aste_df["tuomitut_NAT"], errors="coerce").sum(min_count=1) if len(aste_df) else np.nan
        d_f = pd.to_numeric(aste_df["tuomitut_FOR"], errors="coerce").sum(min_count=1) if len(aste_df) else np.nan
        p_n = pd.to_numeric(aste_df["vaesto_NAT"], errors="coerce").sum(min_count=1) if len(aste_df) else np.nan
        p_f = pd.to_numeric(aste_df["vaesto_FOR"], errors="coerce").sum(min_count=1) if len(aste_df) else np.nan

        row: dict[str, object] = {
            "vuosi": y,
            "n_maata_abs": int(len(abs_df)),
            "maat_abs": ",".join(abs_df["geo"].tolist()),
            "tuomitut_NAT": pd.to_numeric(abs_df["tuomitut_NAT"], errors="coerce").sum(min_count=1),
            "tuomitut_FOR": pd.to_numeric(abs_df["tuomitut_FOR"], errors="coerce").sum(min_count=1),
            "n_maata_aste": int(len(aste_df)),
            "maat_aste": ",".join(aste_df["geo"].tolist()),
            "vaesto_NAT": p_n,
            "vaesto_FOR": p_f,
            "vaesto_EU27_TOTAL": eu_tot,
            "vaesto_osuus": osuus,
            "aste_NAT": np.nan,
            "aste_FOR": np.nan,
            "RR": np.nan,
        }
        if y in YEARS_RATE and len(aste_df):
            asteet_tmp = pd.DataFrame(
                {
                    "tuomitut_NAT": [d_n],
                    "tuomitut_FOR": [d_f],
                    "vaesto_NAT": [p_n],
                    "vaesto_FOR": [p_f],
                }
            )
            lask = laske_asteet(asteet_tmp)
            row["aste_NAT"] = lask["aste_NAT"].iloc[0]
            row["aste_FOR"] = lask["aste_FOR"].iloc[0]
            row["RR"] = lask["RR"].iloc[0]
        rows.append(row)
    return pd.DataFrame(rows)


def poolaa(asteet: pd.DataFrame) -> pd.Series:
    """Yksi RR: summa kelpoisista maa–vuosista. Tyhjä joukko → NaN."""
    s = asteet.loc[asteet["kelpoinen_aste"]].copy() if "kelpoinen_aste" in asteet.columns else asteet
    if len(s) == 0:
        return laske_asteet(
            pd.DataFrame(
                {
                    "tuomitut_NAT": [np.nan],
                    "tuomitut_FOR": [np.nan],
                    "vaesto_NAT": [np.nan],
                    "vaesto_FOR": [np.nan],
                }
            )
        ).iloc[0]
    tmp = pd.DataFrame(
        {
            "tuomitut_NAT": [pd.to_numeric(s["tuomitut_NAT"], errors="coerce").sum(min_count=1)],
            "tuomitut_FOR": [pd.to_numeric(s["tuomitut_FOR"], errors="coerce").sum(min_count=1)],
            "vaesto_NAT": [pd.to_numeric(s["vaesto_NAT"], errors="coerce").sum(min_count=1)],
            "vaesto_FOR": [pd.to_numeric(s["vaesto_FOR"], errors="coerce").sum(min_count=1)],
        }
    )
    out = laske_asteet(tmp).iloc[0]
    return out


def kausi_rr(asteet: pd.DataFrame, vuodet: list[int] | None = None) -> pd.DataFrame:
    """Yhteenlasketut kelpoiset vuodet (ei täyttöä). Poisson-CI summista."""
    if vuodet is None:
        vuodet = YEARS_AVG
    rows: list[dict[str, object]] = []
    for geo in EU27:
        s = asteet[(asteet["geo"] == geo) & (asteet["vuosi"].isin(vuodet)) & (asteet["kelpoinen_aste"])]
        n = int(len(s))
        d_n = pd.to_numeric(s["tuomitut_NAT"], errors="coerce").sum(min_count=1) if n else np.nan
        d_f = pd.to_numeric(s["tuomitut_FOR"], errors="coerce").sum(min_count=1) if n else np.nan
        p_n = pd.to_numeric(s["vaesto_NAT"], errors="coerce").sum(min_count=1) if n else np.nan
        p_f = pd.to_numeric(s["vaesto_FOR"], errors="coerce").sum(min_count=1) if n else np.nan
        tmp = pd.DataFrame(
            {
                "tuomitut_NAT": [d_n],
                "tuomitut_FOR": [d_f],
                "vaesto_NAT": [p_n],
                "vaesto_FOR": [p_f],
            }
        )
        lask = laske_asteet(tmp).iloc[0]
        rows.append(
            {
                "geo": geo,
                "maa": MAAN_NIMET[geo],
                "n_vuotta": n,
                "vuodet": ",".join(str(int(v)) for v in s["vuosi"]) if n else "",
                "tuomitut_NAT": d_n,
                "tuomitut_FOR": d_f,
                "vaesto_NAT": p_n,
                "vaesto_FOR": p_f,
                "aste_NAT": lask["aste_NAT"],
                "aste_FOR": lask["aste_FOR"],
                "RR": lask["RR"],
                "RR_lo": lask["RR_lo"],
                "RR_hi": lask["RR_hi"],
                "epaluotettava": bool(lask["epaluotettava"]) if n else False,
                "varoitus_pieni_D": bool(lask["varoitus_pieni_D"]) if n else False,
            }
        )
    return pd.DataFrame(rows)


def aja() -> pd.DataFrame:
    paneeli = pd.read_csv(MAA_VUOSI_PATH)
    df = laske_asteet(paneeli)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    sarakkeet = [
        "geo",
        "maa",
        "vuosi",
        "tuomitut_NAT",
        "tuomitut_FOR",
        "vaesto_NAT",
        "vaesto_FOR",
        "aste_NAT",
        "aste_NAT_lo",
        "aste_NAT_hi",
        "aste_FOR",
        "aste_FOR_lo",
        "aste_FOR_hi",
        "RR",
        "RR_lo",
        "RR_hi",
        "kelpoinen_aste",
        "epaluotettava",
        "varoitus_pieni_D",
    ]
    out = df[sarakkeet]
    out.to_csv(ASTEET_PATH, index=False)
    eu = eu_aggregaatti(out, paneeli)
    eu.to_csv(EU_AGGR_PATH, index=False)
    kausi = kausi_rr(out)
    kausi.to_csv(KAUSI_RR_PATH, index=False)
    n = len(out)
    kelp = int(out["kelpoinen_aste"].sum())
    epa = int(out["epaluotettava"].sum())
    pieni = int(out["varoitus_pieni_D"].sum())
    print(f"Kirjoitettu {ASTEET_PATH} ({n} riviä)")
    print(f"kelpoinen_aste={kelp} epaluotettava_Dlt10={epa} varoitus_Dlt20={pieni}")
    print(f"Kirjoitettu {EU_AGGR_PATH} ja {KAUSI_RR_PATH}")
    return out


if __name__ == "__main__":
    aja()
