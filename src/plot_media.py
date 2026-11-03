"""Vaihe 5 -kaaviot suomeksi, 200 dpi. Ei täyttöä."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from src.config import DPI_KUVA, ROOT
from src.analyze_media import RYHMA_JARJESTYS

FIG = ROOT / "media" / "output" / "figures"
TABLES = ROOT / "media" / "output" / "tables"
NIMET = {
    "putin": "Putin",
    "zelenskyi": "Zelenskyi",
    "presidentti": "Suomen presidentti",
    "maahanmuutto": "Maahanmuutto",
    "rikollisuus": "Rikollisuus",
    "terveys": "Terveysuhka",
    "iltalehti_etusivu": "Iltalehti",
    "yle_uutiset": "Yle",
}


def alaviitteet() -> str:
    return (
        "Lähde: Wayback-snapshotit (Iltalehti, Yle), haettu 2026-11-02. "
        "Ei ikä- ja sukupuolivakioitu. "
        "Kansalaisuus ei kuvaa maahanmuuttotaustaa tai pakolaisuutta. "
        "Laskentayksikkö vaihtelee maittain; maiden välinen vertailu on rajallinen. "
        "Katkos viivassa = data puuttuu. "
        "Epäluotettavat (D<10) merkitään. "
        "Nimittäjä = HTML-etusivut tai otsikot; puuttuva päivä ei ole nolla."
    )


def _tallenna(fig: plt.Figure, polku: Path) -> None:
    fig.text(0.5, 0.01, alaviitteet(), ha="center", va="bottom", fontsize=7, wrap=True)
    fig.tight_layout(rect=[0.03, 0.12, 0.99, 0.96])
    FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(polku, dpi=DPI_KUVA)
    plt.close(fig)


def kaavio_p1_palkki(p1: pd.DataFrame, polku: Path) -> None:
    d = p1[(p1["jakso"] == "havaittu")].copy()
    fig, akselit = plt.subplots(1, 2, figsize=(11, 6), sharey=True)
    for ax, yksikko, ots in zip(
        akselit, ["etusivu", "otsikko"], ["Etusivupäivä", "Otsikko"]
    ):
        osat = d[d["yksikko"] == yksikko]
        x = list(range(len(RYHMA_JARJESTYS)))
        leveys = 0.38
        for i, media in enumerate(["iltalehti_etusivu", "yle_uutiset"]):
            m = osat[osat["media"] == media].set_index("ryhma").reindex(list(RYHMA_JARJESTYS))
            pos = [xi + (i - 0.5) * leveys for xi in x]
            y = pd.to_numeric(m["osuus"], errors="coerce") * 100
            lo = pd.to_numeric(m["wilson_ala"], errors="coerce") * 100
            hi = pd.to_numeric(m["wilson_yla"], errors="coerce") * 100
            yerr = [y - lo, hi - y]
            ax.bar(
                pos,
                y.fillna(0),
                width=leveys,
                yerr=yerr,
                capsize=3,
                label=NIMET[media],
                color=("#c45c26", "#2c5aa0")[i],
            )
            for px, yy, lippu in zip(pos, y, m["d_lt_10"]):
                if str(lippu) == "1" and pd.notna(yy):
                    ax.text(px, yy + 0.4, "D<10", ha="center", fontsize=7, rotation=90)
        ax.set_xticks(x)
        ax.set_xticklabels([NIMET[r] for r in RYHMA_JARJESTYS], rotation=35, ha="right")
        ax.set_title(ots)
        ax.set_ylabel("Osuus (%)")
        ax.grid(True, axis="y", alpha=0.3)
        ax.legend()
    fig.suptitle("P1: entiteettiosuudet havaituissa snapshotissa")
    _tallenna(fig, polku)


def kaavio_vuosi(p1: pd.DataFrame, polku: Path) -> None:
    d = p1[(p1["yksikko"] == "otsikko") & (p1["jakso"].str.fullmatch(r"\d{4}", na=False))].copy()
    d["vuosi"] = pd.to_numeric(d["jakso"], errors="coerce")
    vuodet = list(range(2015, 2026))
    fig, akselit = plt.subplots(2, 1, figsize=(11, 8), sharex=True)
    for ax, media in zip(akselit, ["iltalehti_etusivu", "yle_uutiset"]):
        for ryhma, vari in zip(
            RYHMA_JARJESTYS,
            ["#c45c26", "#2c5aa0", "#4d7c0f", "#7c3aed", "#b45309", "#0f766e"],
        ):
            m = (
                d[(d["media"] == media) & (d["ryhma"] == ryhma)]
                .set_index("vuosi")
                .reindex(vuodet)
            )
            y = pd.to_numeric(m["osuus"], errors="coerce") * 100
            ax.plot(vuodet, y, marker="o", label=NIMET[ryhma], color=vari)
        ax.set_title(NIMET[media])
        ax.set_ylabel("Osuus otsikoista (%)")
        ax.grid(True, alpha=0.3)
        ax.legend(ncol=3, fontsize=8)
    akselit[-1].set_xlabel("Vuosi")
    fig.suptitle("P1: entiteettiosuudet vuosittain (katkos = ei HTML:ää)")
    _tallenna(fig, polku)


def kaavio_h1_h2(p1: pd.DataFrame, polku: Path) -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5.5))
    h1 = p1[
        (p1["media"] == "iltalehti_etusivu")
        & (p1["ryhma"] == "putin")
        & (p1["jakso"] == "2023")
    ]
    nimet = []
    y = []
    lo_l = []
    hi_l = []
    liput = []
    for _, r in h1.iterrows():
        nimet.append(r["yksikko"])
        yy = float(r["osuus"]) * 100 if r["osuus"] else float("nan")
        y.append(yy)
        lo_l.append(yy - float(r["wilson_ala"]) * 100 if r["wilson_ala"] else float("nan"))
        hi_l.append(float(r["wilson_yla"]) * 100 - yy if r["wilson_yla"] else float("nan"))
        liput.append(r["d_lt_10"])
    ax1.bar(range(len(nimet)), y, yerr=[lo_l, hi_l], capsize=4, color="#c45c26")
    ax1.set_xticks(range(len(nimet)))
    ax1.set_xticklabels(nimet)
    ax1.set_ylabel("Osuus (%)")
    ax1.set_title("H1: Iltalehti 2023, Putin")
    for i, (yy, lip) in enumerate(zip(y, liput)):
        if str(lip) == "1":
            ax1.text(i, yy + 0.5, "D<10", ha="center", fontsize=8)
    ax1.grid(True, axis="y", alpha=0.3)

    h2 = p1[
        (p1["jakso"] == "havaittu")
        & (p1["yksikko"] == "etusivu")
        & (p1["ryhma"].isin(["presidentti", "putin", "zelenskyi"]))
    ]
    x = list(range(3))
    luokat = ["presidentti", "putin", "zelenskyi"]
    leveys = 0.38
    for i, media in enumerate(["iltalehti_etusivu", "yle_uutiset"]):
        m = h2[h2["media"] == media].set_index("ryhma").reindex(luokat)
        pos = [xi + (i - 0.5) * leveys for xi in x]
        yy = pd.to_numeric(m["osuus"], errors="coerce") * 100
        lo = pd.to_numeric(m["wilson_ala"], errors="coerce") * 100
        hi = pd.to_numeric(m["wilson_yla"], errors="coerce") * 100
        ax2.bar(
            pos,
            yy,
            width=leveys,
            yerr=[yy - lo, hi - yy],
            capsize=3,
            label=NIMET[media],
            color=("#c45c26", "#2c5aa0")[i],
        )
        for px, yv, lip in zip(pos, yy, m["d_lt_10"]):
            if str(lip) == "1" and pd.notna(yv):
                ax2.text(px, yv + 0.3, "D<10", ha="center", fontsize=7, rotation=90)
    ax2.set_xticks(x)
    ax2.set_xticklabels([NIMET[k] for k in luokat], rotation=20, ha="right")
    ax2.set_title("H2: etusivu, havaittu jakso")
    ax2.set_ylabel("Osuus (%)")
    ax2.legend()
    ax2.grid(True, axis="y", alpha=0.3)
    fig.suptitle("H1 ja H2 (Wilson 95 %)")
    _tallenna(fig, polku)


def kaavio_m4(m4: pd.DataFrame, polku: Path) -> None:
    jarj = [
        ("K1_FI", "tuomitut", "K1 FI tuomitut FOR"),
        ("media", "rikosotsikko", "Rikosotsikko, FOR-avain"),
        ("media", "rikosotsikko_ehdollinen", "Rikosotsikko, ehdollinen"),
    ]
    nimet, y, lo_e, hi_e, liput = [], [], [], [], []
    d = m4[m4["media"].fillna("").isin(["", "molemmat"])]
    for lahde, yksikko, nimi in jarj:
        r = d[(d["lahde"] == lahde) & (d["yksikko"] == yksikko)]
        if r.empty:
            continue
        row = r.iloc[0]
        nimet.append(nimi)
        yy = pd.to_numeric(row["osuus_FOR"], errors="coerce")
        y.append(float(yy) * 100 if pd.notna(yy) else float("nan"))
        if row["lahde"] == "K1_FI" or not str(row.get("wilson_ala", "")):
            lo_e.append(0.0)
            hi_e.append(0.0)
        else:
            lo_e.append(y[-1] - float(row["wilson_ala"]) * 100)
            hi_e.append(float(row["wilson_yla"]) * 100 - y[-1])
        liput.append(str(row.get("d_lt_10", "0")))
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.bar(range(len(nimet)), y, yerr=[lo_e, hi_e], capsize=4, color=["#2c5aa0", "#c45c26", "#b45309"][: len(nimet)])
    ax.set_xticks(range(len(nimet)))
    ax.set_xticklabels(nimet, rotation=18, ha="right")
    ax.set_ylabel("FOR-osuus (%)")
    ax.set_title("M4: K1 Suomi vs. rikosotsikon kansalaisuusmaininta")
    for i, (yy, lip) in enumerate(zip(y, liput)):
        if lip == "1" and pd.notna(yy):
            ax.text(i, yy + 0.5, "D<10", ha="center", fontsize=8)
    ax.grid(True, axis="y", alpha=0.3)
    _tallenna(fig, polku)


def aja() -> None:
    p1 = pd.read_csv(TABLES / "p1_entiteetti_osuus.csv", dtype=str)
    kaavio_p1_palkki(p1, FIG / "01_entiteetti_osuus.png")
    kaavio_vuosi(p1, FIG / "02_entiteetti_vuosi.png")
    kaavio_h1_h2(p1, FIG / "03_h1_h2.png")
    m4p = TABLES / "m4_media_vs_k1.csv"
    if m4p.exists():
        kaavio_m4(pd.read_csv(m4p, dtype=str), FIG / "04_m4_media_vs_k1.png")
    print("kirjoitettu", FIG / "01_entiteetti_osuus.png", flush=True)


if __name__ == "__main__":
    aja()
