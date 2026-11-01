"""Coverage: maa × vuosi, osoittaja ja nimittäjä molemmille ryhmille. Ei täyttöä."""

from __future__ import annotations

import pandas as pd

from src.clean import puhdista, tallenna
from src.config import COVERAGE_PATH, MAA_VUOSI_PATH, TABLES_DIR


def coverage_matrix(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(
        {
            "geo": df["geo"],
            "maa": df["maa"],
            "vuosi": df["vuosi"].astype(int),
            "tuomitut_NAT": df.get("tuomitut_NAT"),
            "tuomitut_FOR": df.get("tuomitut_FOR"),
            "tuomitut_TOTAL": df.get("tuomitut_TOTAL"),
            "tuomitut_UNK": df.get("tuomitut_UNK"),
            "epaillyt_NAT": df.get("epaillyt_NAT"),
            "epaillyt_FOR": df.get("epaillyt_FOR"),
            "vaesto_NAT": df.get("vaesto_NAT"),
            "vaesto_FOR": df.get("vaesto_FOR"),
            "vaesto_UNK": df.get("vaesto_UNK"),
            "vaesto_STLS": df.get("vaesto_STLS"),
        }
    )

    out["on_tuomitut_NAT"] = out["tuomitut_NAT"].notna()
    out["on_tuomitut_FOR"] = out["tuomitut_FOR"].notna()
    out["on_epaillyt_NAT"] = out["epaillyt_NAT"].notna()
    out["on_epaillyt_FOR"] = out["epaillyt_FOR"].notna()
    out["on_vaesto_NAT"] = out["vaesto_NAT"].notna()
    out["on_vaesto_FOR"] = out["vaesto_FOR"].notna()

    out["kelpoinen_aste"] = (
        out["on_tuomitut_NAT"]
        & out["on_tuomitut_FOR"]
        & out["on_vaesto_NAT"]
        & out["on_vaesto_FOR"]
        & (out["vaesto_NAT"] > 0)
        & (out["vaesto_FOR"] > 0)
    )
    out["epaluotettava_FOR_Dlt10"] = out["on_tuomitut_FOR"] & (out["tuomitut_FOR"] < 10)

    puuttuvat: list[str] = []
    kentat = [
        "tuomitut_NAT",
        "tuomitut_FOR",
        "epaillyt_NAT",
        "epaillyt_FOR",
        "vaesto_NAT",
        "vaesto_FOR",
    ]
    for _, r in out.iterrows():
        puuttuu = [k for k in kentat if pd.isna(r[k])]
        if int(r["vuosi"]) == 2008:
            puuttuu.append("vaesto_ei_saatavilla_2008")
        puuttuvat.append(";".join(puuttuu))
    out["puuttuvat_kentat"] = puuttuvat

    huom = []
    for _, r in out.iterrows():
        osat: list[str] = []
        if (
            pd.notna(r["tuomitut_TOTAL"])
            and r["tuomitut_TOTAL"] > 0
            and r["tuomitut_NAT"] == 0
            and r["tuomitut_FOR"] == 0
        ):
            osat.append("NAT_ja_FOR_nolla_vaikka_TOTAL>0")
        if pd.notna(r["tuomitut_UNK"]) and r["tuomitut_UNK"] > 0:
            osat.append(f"tuntematon_kansalaisuus_tuomitut={int(r['tuomitut_UNK'])}")
        huom.append(";".join(osat))
    out["huomautus"] = huom
    return out


def yhteenveto(cov: pd.DataFrame) -> str:
    n = len(cov)
    kelp = int(cov["kelpoinen_aste"].sum())
    dlt10 = int(cov["epaluotettava_FOR_Dlt10"].sum())
    kelp_dlt10 = int((cov["kelpoinen_aste"] & cov["epaluotettava_FOR_Dlt10"]).sum())
    return (
        f"rivejä={n} (EU27 × 2008–2024)\n"
        f"kelpoinen_aste={kelp}\n"
        f"epaluotettava_FOR_Dlt10={dlt10} (kelpoisista {kelp_dlt10})\n"
        f"crim_just_ctz: ei UNK-koodia; tuomitut_UNK = jäännös TOTAL−NAT−FOR jos ≥ 0"
    )


def aja(paneeli: pd.DataFrame | None = None) -> pd.DataFrame:
    if paneeli is None:
        if MAA_VUOSI_PATH.exists():
            paneeli = pd.read_csv(MAA_VUOSI_PATH)
        else:
            paneeli = puhdista()
            tallenna(paneeli)
    cov = coverage_matrix(paneeli)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    cov.to_csv(COVERAGE_PATH, index=False)
    print(f"Kirjoitettu {COVERAGE_PATH}")
    print(yhteenveto(cov))
    return cov


if __name__ == "__main__":
    aja()
