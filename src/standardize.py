"""Epäsuora ikä×sukupuolivakiointi (SIR). Ei täyttöä, ei arvattuja rikoslukuja."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.config import (
    CACHE_DIR,
    CRIME_DATASET,
    EU27,
    FIGURES_DIR,
    KAUSI_RR_PATH,
    SIR_PATH,
    SIR_RAJOITE_PATH,
    TABLES_DIR,
)
from src.plots import _tallenna
from src.rates import garwood_lkm_ci

RAJOITE = (
    "SIR ei ole laskettavissa Eurostatin crim_just_ctz-aineistosta: "
    "sarakkeita age ja sex ei ole. migr_pop1ctz sisältää ikä×sukupuoli×kansalaisuus "
    "-väestön, mutta NAT-ryhmän ikä-sukupuolikohtaisia tuomitsemisasteita ei ole. "
    "Osoittajaa ei ole arvattu eikä jaettu ikäryhmiin. "
    "Vaihtoehto: kansalliset aineistot (vaihe 9), jos niissä on virallinen vakiointi."
)


def rikosaineiston_sarakkeet() -> list[str]:
    polku = CACHE_DIR / f"{CRIME_DATASET}.csv"
    return list(pd.read_csv(polku, nrows=0).columns)


def on_ika_sukupuoli_rikoksessa(sarakkeet: list[str] | None = None) -> bool:
    cols = sarakkeet if sarakkeet is not None else rikosaineiston_sarakkeet()
    lower = {c.lower() for c in cols}
    return "age" in lower and "sex" in lower


def odotettu_tapaukset(r_nat: pd.Series, vaesto_for: pd.Series) -> float:
    """E = Σ r_NAT(a,s) * Pop_FOR(a,s). Jos tarvittava stratum puuttuu → NaN."""
    r = pd.to_numeric(r_nat, errors="coerce")
    p = pd.to_numeric(vaesto_for, errors="coerce")
    r, p = r.align(p, join="outer")
    tarvitsee = p.notna() & (p > 0)
    if not bool(tarvitsee.any()):
        return float("nan")
    if bool(r.loc[tarvitsee].isna().any()):
        return float("nan")
    ok = r.notna() & p.notna()
    return float((r.loc[ok] * p.loc[ok]).sum())


def sir_luku(havaittu_for: float, odotettu: float) -> float:
    if (
        havaittu_for is None
        or odotettu is None
        or not np.isfinite(havaittu_for)
        or not np.isfinite(odotettu)
        or odotettu <= 0
    ):
        return float("nan")
    return float(havaittu_for / odotettu)


def sir_ci(havaittu_for: float, odotettu: float) -> tuple[float, float]:
    """Garwood O:lle, jaettuna E:llä (E kiinteä, METHODS §3)."""
    if not np.isfinite(odotettu) or odotettu <= 0 or not np.isfinite(havaittu_for):
        return float("nan"), float("nan")
    lo, hi = garwood_lkm_ci(pd.Series([havaittu_for]))
    return float(lo.iloc[0] / odotettu), float(hi.iloc[0] / odotettu)


def osuus_erosta(rr: float, sir: float) -> float:
    """(RR_raaka − SIR) / RR_raaka. Ei lasketa, jos SIR puuttuu."""
    if not np.isfinite(rr) or rr == 0 or not np.isfinite(sir):
        return float("nan")
    return float((rr - sir) / rr)


def sir_taulu_tyhja(kausi: pd.DataFrame, rajoite: str) -> pd.DataFrame:
    """Kaikki maat säilyvät; SIR = NaN."""
    out = kausi.copy()
    if "geo" not in out.columns:
        out["geo"] = EU27
    out["SIR"] = np.nan
    out["SIR_lo"] = np.nan
    out["SIR_hi"] = np.nan
    out["osuus_erosta"] = np.nan
    out["rajoite"] = rajoite
    return out


def kaavio_rr_vs_sir(taulu: pd.DataFrame, polku) -> None:
    import matplotlib.pyplot as plt

    d = taulu.copy()
    d["on_rr"] = d["RR"].notna()
    jarj = pd.concat(
        [d[~d["on_rr"]].sort_values("maa"), d[d["on_rr"]].sort_values("RR")],
        ignore_index=True,
    )
    y = np.arange(len(jarj))
    fig, ax = plt.subplots(figsize=(11, 10))
    ax.axvline(1.0, color="gray", linestyle="--", linewidth=1, label="arvo 1")
    mask = jarj["on_rr"].to_numpy()
    ax.scatter(
        jarj.loc[mask, "RR"],
        y[mask],
        color="#2c5aa0",
        marker="o",
        label="Raaka RR (ei vakioitu)",
        zorder=3,
    )
    ax.scatter(
        [],
        [],
        color="#c45c26",
        marker="s",
        label="SIR (ei laskettavissa)",
    )
    ax.set_yticks(y)
    ax.set_yticklabels(jarj["maa"].tolist())
    ax.set_xlabel("Suhdeluku")
    ax.set_title(
        "Raaka RR ja SIR maittain, 2020–2024\n"
        "SIR puuttuu: crim_just_ctz ei sisällä ikää eikä sukupuolta"
    )
    ax.grid(True, axis="x", alpha=0.3)
    ax.legend(loc="lower right", fontsize=8)
    _tallenna(fig, polku)


def aja() -> pd.DataFrame:
    sarakkeet = rikosaineiston_sarakkeet()
    ika_sex = on_ika_sukupuoli_rikoksessa(sarakkeet)
    rajoite = RAJOITE if not ika_sex else ""
    if ika_sex:
        raise RuntimeError(
            "crim_just_ctz sisältää nyt age ja sex; SIR-putki on päivitettävä, "
            "älä käytä tyhjää taulua."
        )
    kausi = pd.read_csv(KAUSI_RR_PATH)
    taulu = sir_taulu_tyhja(kausi, rajoite)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    taulu.to_csv(SIR_PATH, index=False)
    pd.DataFrame(
        {
            "ehto": ["age_ja_sex_crim_just_ctz"],
            "tayttyy": [ika_sex],
            "sarakkeet": [",".join(sarakkeet)],
            "rajoite": [rajoite],
        }
    ).to_csv(SIR_RAJOITE_PATH, index=False)
    import matplotlib.pyplot as plt

    plt.switch_backend("Agg")
    kaavio_rr_vs_sir(taulu, FIGURES_DIR / "05_rr_vs_sir.png")
    print(f"Kirjoitettu {SIR_PATH} ja {SIR_RAJOITE_PATH}")
    print(rajoite)
    print(f"SIR-arvoja: {int(taulu['SIR'].notna().sum())} / {len(taulu)}")
    return taulu


if __name__ == "__main__":
    aja()
