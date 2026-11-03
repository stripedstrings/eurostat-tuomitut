"""Suomenkieliset FI-maahanmuuttokaaviot. TUTKIVA."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd

from src.config import DPI_KUVA
from src.fi_migr.paths import FIGURES, HAETTU, TABLES

ALAVIITE = (
    f"TUTKIVA (ei esirekisteröity). Lähteet: Tilastokeskus StatFin, Eurostat (geo=FI), "
    f"Migri; haettu {HAETTU}. Kansalaisuus ≠ maahanmuuttotausta ≠ pakolaisuus. "
    "Katkos = data puuttuu; ei täyttöä. Ei yhdistetty K1-rikostilastoon."
)


def _tallenna(fig: plt.Figure, nimi: str) -> None:
    fig.text(0.5, 0.01, ALAVIITE, ha="center", va="bottom", fontsize=7, wrap=True)
    fig.tight_layout(rect=[0.03, 0.14, 0.99, 0.96])
    FIGURES.mkdir(parents=True, exist_ok=True)
    polku = FIGURES / nimi
    fig.savefig(polku, dpi=DPI_KUVA)
    plt.close(fig)
    print("kirjoitettu", polku, flush=True)


def kaavio_tulot() -> None:
    df = pd.read_csv(TABLES / "fi_migr_tulot_vuosi.csv")
    fig, ax = plt.subplots(figsize=(11, 6))
    for kans, vari in (
        ("YHTEENSÄ", "#333333"),
        ("ULKOMAAT YHTEENSÄ", "#c45c26"),
        ("Suomi", "#2c5aa0"),
    ):
        s = df[df["kansalaisuus"] == kans].sort_values("vuosi")
        if s.empty:
            continue
        ax.plot(s["vuosi"], s["maahanmuutto"], marker="o", label=kans, color=vari)
    ax.set_title("Maahanmuutto Suomeen kansalaisuuden mukaan (StatFin 11a8)")
    ax.set_ylabel("Henkilöä")
    ax.set_xlabel("Vuosi")
    ax.grid(True, alpha=0.3)
    ax.legend()
    _tallenna(fig, "01_maahanmuutto_vuosi.png")


def kaavio_osuudet() -> None:
    df = pd.read_csv(TABLES / "fi_migr_vaesto_osuudet.csv")
    # osuus-sarakkeet
    fig, ax = plt.subplots(figsize=(11, 6))
    for mittari, nimi, vari in (
        ("Ulkomaalaistaustaisten osuus, %", "Ulkomaalaistaustaiset %", "#c45c26"),
        ("Ulkomaan kansalaisten osuus, %", "Ulkomaan kansalaiset %", "#2c5aa0"),
        ("Vieraskielisten osuus, %", "Vieraskieliset %", "#4d7c0f"),
    ):
        # mittari may be full column title from StatFin
        osat = df[df["mittari"].astype(str).str.contains(mittari.split(",")[0][:20], case=False, na=False)]
        if osat.empty:
            # try exact finnish names in mittari
            osat = df[df["mittari"].astype(str).str.contains(nimi.split()[0], case=False, na=False)]
        # Prefer rows whose mittari endswith osuus
        cand = df[df["mittari"].astype(str).str.contains("osuus", case=False, na=False)]
        # map by keyword
        key = {
            "Ulkomaalaistaustaiset %": "tausta_ulk_p",
            "Ulkomaan kansalaiset %": "kansa_ulk_p",
            "Vieraskieliset %": "kieli_ulk_p",
        }[nimi]
        osat = cand[cand["mittari"].astype(str).str.contains(key.replace("_p", ""), case=False, na=False)]
        if key == "tausta_ulk_p":
            osat = cand[cand["mittari"].astype(str).str.contains("tausta_ulk_p|Ulkomaalaistaustaisten osuus", case=False, na=False)]
        elif key == "kansa_ulk_p":
            osat = cand[cand["mittari"].astype(str).str.contains("kansa_ulk_p|Ulkomaan kansalaisten osuus", case=False, na=False)]
        else:
            osat = cand[cand["mittari"].astype(str).str.contains("kieli_ulk_p|Vieraskielisten osuus", case=False, na=False)]
        osat = osat.sort_values("vuosi")
        if osat.empty:
            continue
        ax.plot(osat["vuosi"], osat["arvo"], marker="o", label=nimi, color=vari)
    ax.set_title("Ulkomaalaistaustaisten / kansalaisten / vieraskielisten osuus (StatFin 159t)")
    ax.set_ylabel("% väestöstä")
    ax.grid(True, alpha=0.3)
    ax.legend()
    _tallenna(fig, "02_vaesto_osuudet.png")


def kaavio_tyollisyys() -> None:
    df = pd.read_csv(TABLES / "fi_migr_tyollisyys.csv")
    d = df[df["mittari"] == "tyollisyysaste_pct"].copy()
    fig, ax = plt.subplots(figsize=(11, 6))
    for cit, nimi, vari in (
        ("NAT", "Oman maan kansalaiset", "#2c5aa0"),
        ("FOR", "Ulkomaan kansalaiset", "#c45c26"),
        ("NEU27_2020_FOR", "EU27:n ulkopuoliset", "#984ea3"),
    ):
        s = d[d["citizen"] == cit].sort_values("vuosi")
        if s.empty:
            continue
        ax.plot(s["vuosi"], s["arvo"], marker="o", label=nimi, color=vari)
    ax.set_title("Työllisyysaste FI (Eurostat lfsa_ergan, LFS)")
    ax.set_ylabel("%")
    ax.grid(True, alpha=0.3)
    ax.legend()
    _tallenna(fig, "03_tyollisyysaste.png")


def kaavio_koulutus() -> None:
    df = pd.read_csv(TABLES / "fi_migr_koulutus.csv")
    d = df[(df["isced11"] == "ED5-8")].copy()
    fig, ax = plt.subplots(figsize=(11, 6))
    for cit, nimi, vari in (
        ("NAT", "Oman maan kansalaiset", "#2c5aa0"),
        ("FOR", "Ulkomaan kansalaiset", "#c45c26"),
    ):
        s = d[d["citizen"] == cit].sort_values("vuosi")
        if s.empty:
            continue
        ax.plot(s["vuosi"], s["arvo_pct"], marker="o", label=nimi, color=vari)
    ax.set_title("Korkea-asteen koulutus (ISCED 5–8), 25–64 v, FI")
    ax.set_ylabel("%")
    ax.grid(True, alpha=0.3)
    ax.legend()
    _tallenna(fig, "04_koulutus_korkea.png")


def kaavio_luvat() -> None:
    df = pd.read_csv(TABLES / "fi_migr_luvat.csv")
    d = df[(df["lupa"] == "ensimmaiset") & (df["reason"] != "TOTAL")].copy()
    fig, ax = plt.subplots(figsize=(11, 6))
    nimet = {
        "EDUC": "Koulutus",
        "EMP": "Työ",
        "FAM": "Perhe",
        "OTH": "Muu",
        "RFG": "Pakolaisasema",
        "SPROT": "Toissijainen suojelu",
    }
    for reason, vari in zip(
        ["EMP", "FAM", "EDUC", "OTH", "RFG", "SPROT"],
        ["#2c5aa0", "#c45c26", "#4d7c0f", "#7c3aed", "#b45309", "#0f766e"],
    ):
        s = d[d["reason"] == reason].sort_values("vuosi")
        if s.empty:
            continue
        ax.plot(s["vuosi"], s["arvo"], marker="o", label=nimet.get(reason, reason), color=vari)
    ax.set_title("Ensimmäiset oleskeluluvat syittäin (Eurostat migr_resfirst, FI)")
    ax.set_ylabel("Lukumäärä")
    ax.grid(True, alpha=0.3)
    ax.legend(ncol=2, fontsize=8)
    _tallenna(fig, "05_oleskeluluvat.png")


def kaavio_ika_sukupuoli() -> None:
    df = pd.read_csv(TABLES / "fi_migr_ika_sukupuoli.csv")
    # viimeisin vuosi, ulkomaalaistaustaiset, miehet/naiset, ei Yhteensä-ikää
    vuosi = int(df["vuosi"].max())
    d = df[
        (df["vuosi"] == vuosi)
        & (df["syntypera"].str.contains("Ulkomaalaistaustaiset", na=False))
        & (df["sukupuoli"].isin(["Miehet", "Naiset"]))
        & (~df["ika"].str.contains("Yhteensä", na=False))
    ].copy()
    if d.empty:
        return
    ika_jarj = sorted(d["ika"].unique(), key=lambda x: (x.replace(" - ", "-"), x))
    fig, ax = plt.subplots(figsize=(11, 6))
    import numpy as np

    x = np.arange(len(ika_jarj))
    w = 0.38
    for i, (suk, vari) in enumerate((("Miehet", "#2c5aa0"), ("Naiset", "#c45c26"))):
        s = d[d["sukupuoli"] == suk].set_index("ika").reindex(ika_jarj)
        ax.bar(x + (i - 0.5) * w, s["vaesto"], width=w, label=suk, color=vari)
    ax.set_xticks(x)
    ax.set_xticklabels(ika_jarj, rotation=45, ha="right")
    ax.set_title(f"Ulkomaalaistaustainen väestö iän ja sukupuolen mukaan {vuosi} (StatFin 11rt)")
    ax.set_ylabel("Henkilöä")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)
    _tallenna(fig, "06_ika_sukupuoli.png")


def aja() -> None:
    kaavio_tulot()
    kaavio_osuudet()
    kaavio_tyollisyys()
    kaavio_koulutus()
    kaavio_luvat()
    kaavio_ika_sukupuoli()


if __name__ == "__main__":
    aja()
