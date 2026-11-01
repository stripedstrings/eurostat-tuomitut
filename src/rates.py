"""Aste per 100 000, RR ja Poisson-luottamusvälit. Ei täyttöä."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import chi2, norm

from src.config import ASTEET_PATH, MAA_VUOSI_PATH, TABLES_DIR

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
    n = len(out)
    kelp = int(out["kelpoinen_aste"].sum())
    epa = int(out["epaluotettava"].sum())
    pieni = int(out["varoitus_pieni_D"].sum())
    print(f"Kirjoitettu {ASTEET_PATH} ({n} riviä)")
    print(f"kelpoinen_aste={kelp} epaluotettava_Dlt10={epa} varoitus_Dlt20={pieni}")
    return out


if __name__ == "__main__":
    aja()
