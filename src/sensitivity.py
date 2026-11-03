"""Herkkyysanalyysit S1–S7. Ei täyttöä; rajoite merkitään, ei arvata koodeja."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from src.config import (
    CACHE_DIR,
    CRIME_DATASET,
    FIGURES_DIR,
    HERKKYYS_PATH,
    MAA_VUOSI_PATH,
    TABLES_DIR,
    YEARS_AVG,
)
from src.plots import _tallenna
from src.rates import kausi_rr, laske_asteet, poolaa

S2_RAJOITE = (
    "crim_just_ctz.citizen unique = FOR, NAT, TOTAL. EU-sisäisiä ja kolmansien "
    "maiden kansalaisia ei voi erottaa rikososoittajasta."
)
S4_RAJOITE = (
    "crim_just_ctz.unit unique = NR, P_HTHAB. Laskentayksikköä henkilö vs. tapaus "
    "ei ole dimensiossa; maakohtaista listaa ei arvata."
)
S7_RAJOITE = (
    "Rikosaineistossa ei ole naturalisaatiota tai entistä kansalaisuutta. "
    "Tuomittuja ei voi siirtää NAT→FOR ilman oletusta; S7 jätetään rajoitteeksi."
)


def _rivi(
    tunnus: str,
    kuvaus: str,
    asteet: pd.DataFrame | None,
    huom: str,
    rr: float | None = None,
    rr_lo: float | None = None,
    rr_hi: float | None = None,
    aste_nat: float | None = None,
    aste_for: float | None = None,
    n_maata: int = 0,
    n_maa_vuotta: int = 0,
) -> dict[str, object]:
    if asteet is not None:
        p = poolaa(asteet)
        n_mv = int(asteet["kelpoinen_aste"].sum()) if "kelpoinen_aste" in asteet.columns else 0
        n_maa = int(asteet.loc[asteet["kelpoinen_aste"], "geo"].nunique()) if n_mv else 0
        return {
            "analyysi": tunnus,
            "kuvaus": kuvaus,
            "n_maata": n_maa,
            "n_maa_vuotta": n_mv,
            "aste_NAT": p["aste_NAT"],
            "aste_FOR": p["aste_FOR"],
            "RR": p["RR"],
            "RR_lo": p["RR_lo"],
            "RR_hi": p["RR_hi"],
            "huomautus": huom,
        }
    return {
        "analyysi": tunnus,
        "kuvaus": kuvaus,
        "n_maata": n_maata,
        "n_maa_vuotta": n_maa_vuotta,
        "aste_NAT": aste_nat if aste_nat is not None else np.nan,
        "aste_FOR": aste_for if aste_for is not None else np.nan,
        "RR": rr if rr is not None else np.nan,
        "RR_lo": rr_lo if rr_lo is not None else np.nan,
        "RR_hi": rr_hi if rr_hi is not None else np.nan,
        "huomautus": huom,
    }


def crime_unique(col: str) -> list[str]:
    df = pd.read_csv(CACHE_DIR / f"{CRIME_DATASET}.csv", usecols=[col])
    return sorted(df[col].dropna().astype(str).unique().tolist())


def asteet_vaihe(paneeli: pd.DataFrame, prefiksi: str) -> pd.DataFrame:
    tmp = paneeli.copy()
    tmp["tuomitut_NAT"] = tmp[f"{prefiksi}_NAT"]
    tmp["tuomitut_FOR"] = tmp[f"{prefiksi}_FOR"]
    return laske_asteet(tmp)


def taulu_s1_s7(paneeli: pd.DataFrame | None = None) -> pd.DataFrame:
    if paneeli is None:
        paneeli = pd.read_csv(MAA_VUOSI_PATH)
    asteet = laske_asteet(paneeli)
    kausi = kausi_rr(asteet)
    paa = asteet[asteet["vuosi"].isin(YEARS_AVG)].copy()

    taydet = kausi.loc[kausi["n_vuotta"] == len(YEARS_AVG), "geo"].tolist()
    s1 = paa[paa["geo"].isin(taydet)]

    epaillyt = asteet_vaihe(paneeli, "epaillyt")
    s3 = epaillyt[epaillyt["vuosi"].isin(YEARS_AVG)]

    s5_pois = paa[~paa["epaluotettava"]].copy()

    citizen = crime_unique("citizen")
    unit = crime_unique("unit")
    s2_ok = set(citizen) >= {"NAT", "FOR"} and any(
        c.startswith("EU") or c in {"EXT", "NEU"} for c in citizen
    )
    s4_ok = "PERSON" in {u.upper() for u in unit}

    maa_rr = kausi.loc[kausi["RR"].notna(), "RR"]
    painottamaton = float(maa_rr.mean()) if len(maa_rr) else float("nan")

    rivit = [
        _rivi(
            "paa",
            "Pääanalyysi: tuomitut, kelpoiset maa–vuodet 2020–2024, poolattu RR",
            paa,
            "Kaikki kelpoiset maa–vuodet; D<10 merkitty ei poistettu",
        ),
        _rivi(
            "S1",
            "Vain maat, joilla kelpoinen aste kaikkina vuosina 2020–2024",
            s1,
            f"maat={','.join(taydet) if taydet else '(ei)'}",
        ),
        _rivi(
            "S2",
            "EU-sisäiset vs. kolmansien maiden kansalaiset",
            None,
            S2_RAJOITE + f" citizen={','.join(citizen)}",
        ),
        _rivi(
            "S3",
            "Epäillyt (PER_SUSP), sama kelpoisuussääntö 2020–2024",
            s3,
            "Ei sama henkilöjoukko kuin tuomituissa; ei syyllisyysosuus",
        ),
        _rivi(
            "S4",
            "Vain maat, joiden laskentayksikkö on henkilö",
            None,
            S4_RAJOITE + f" unit={','.join(unit)}",
        ),
        _rivi(
            "S5_mukana",
            "Pienet luvut (D<10) mukana (kuten pääanalyysi)",
            paa,
            f"epaluotettavia_riveja={int(paa['epaluotettava'].sum())}",
        ),
        _rivi(
            "S5_pois",
            "Pienet luvut (D<10) pois kelpoisista riveistä",
            s5_pois,
            "Poisto vain D<10-merkitty; ei tuloksen perusteella",
        ),
        _rivi(
            "S6_painotettu",
            "Väestöllä painotettu EU-RR (poolaus = pääanalyysi)",
            paa,
            "Painotus: summa osoittajista ja nimittäjistä",
        ),
        _rivi(
            "S6_painottamaton",
            "Painottamaton keskiarvo maiden poolatuista RR-luvuista 2020–2024",
            None,
            f"n_maata={int(maa_rr.shape[0])}; ei Poisson-CI (keskiarvo suhdeluvuista)",
            rr=painottamaton,
            n_maata=int(maa_rr.shape[0]),
        ),
        _rivi(
            "S7",
            "Naturalisoituneet laskettu ulkomaalaisiin",
            None,
            S7_RAJOITE,
        ),
    ]
    if s2_ok or s4_ok:
        raise RuntimeError("S2/S4-dimensio ilmestyi dataan; herkkyysputki päivitettävä.")
    out = pd.DataFrame(rivit)
    out["paa_RR"] = out.loc[out["analyysi"] == "paa", "RR"].iloc[0]
    out["ero_paa"] = out["RR"] - out["paa_RR"]
    return out


def kaavio_herkkyys(taulu: pd.DataFrame, polku) -> None:
    import matplotlib.pyplot as plt

    d = taulu.copy()
    fig, ax = plt.subplots(figsize=(11, 6.5))
    y = np.arange(len(d))
    on = d["RR"].notna().to_numpy()
    ax.axvline(d.loc[d["analyysi"] == "paa", "RR"].iloc[0], color="#2c5aa0", linestyle="--", label="Pääanalyysin RR")
    xerr = None
    if on.any():
        lo = d.loc[on, "RR"] - d.loc[on, "RR_lo"]
        hi = d.loc[on, "RR_hi"] - d.loc[on, "RR"]
        lo = lo.fillna(0)
        hi = hi.fillna(0)
        xerr = np.vstack([lo.to_numpy(), hi.to_numpy()])
        ax.errorbar(
            d.loc[on, "RR"],
            y[on],
            xerr=xerr,
            fmt="o",
            color="#c45c26",
            capsize=3,
            label="RR (95 % väli, jos Poisson)",
        )
    ax.set_yticks(y)
    ax.set_yticklabels(d["analyysi"].tolist(), fontsize=9)
    ax.set_xlabel("RR")
    ax.set_title("Herkkyys S1–S7: poolattu RR 2020–2024 (tuomitut, ellei toisin)")
    ax.grid(True, axis="x", alpha=0.3)
    ax.legend(loc="lower right", fontsize=8)
    xmax = float(np.nanmax(d["RR"].to_numpy())) * 1.2
    ax.set_xlim(0, xmax)
    for yi, r in zip(y, d.itertuples()):
        if pd.isna(r.RR):
            ax.text(xmax * 0.52, yi, "ei laskettavissa", va="center", fontsize=8, color="#555555")
    ax.invert_yaxis()
    _tallenna(fig, polku)


def kirjoita_s2_s7_tila(citizen: list[str] | None = None, unit: list[str] | None = None) -> Path:
    """S2/S7: tila = ei_dataa + syy (ei arvata ulottuvuuksia)."""
    if citizen is None:
        citizen = crime_unique("citizen")
    if unit is None:
        unit = crime_unique("unit")
    polku = TABLES_DIR / "s2_s7_tila.csv"
    pd.DataFrame(
        [
            {
                "analyysi": "S2",
                "tila": "ei_dataa",
                "syy": S2_RAJOITE,
                "citizen_unique": ",".join(citizen),
                "unit_unique": ",".join(unit),
                "viite": "PREREGISTRATION S2; eu_vs_kolmas_rajoite.csv; herkkyys_S1_S7.csv",
            },
            {
                "analyysi": "S7",
                "tila": "ei_dataa",
                "syy": S7_RAJOITE,
                "citizen_unique": ",".join(citizen),
                "unit_unique": ",".join(unit),
                "viite": "PREREGISTRATION S7; herkkyys_S1_S7.csv",
            },
        ]
    ).to_csv(polku, index=False)
    return polku


def aja() -> pd.DataFrame:
    import matplotlib.pyplot as plt

    plt.switch_backend("Agg")
    taulu = taulu_s1_s7()
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    taulu.to_csv(HERKKYYS_PATH, index=False)
    tila = kirjoita_s2_s7_tila()
    kaavio_herkkyys(taulu, FIGURES_DIR / "06_herkkyys.png")
    print(taulu[["analyysi", "n_maata", "n_maa_vuotta", "RR", "RR_lo", "RR_hi"]].to_string(index=False))
    print(f"Kirjoitettu {HERKKYYS_PATH}")
    print(f"Kirjoitettu {tila}")
    return taulu


if __name__ == "__main__":
    aja()
