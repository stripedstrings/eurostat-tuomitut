"""Kaikki kaaviot suomeksi; NaN = katkos viivassa."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.config import EU27, MAAN_NIMET, MAAN_NIMET_EN, OUTPUT_DIR, VARIT, YEARS_ABS, YEARS_RATE

ALAVIITE = {
    "fi": (
        "Ei ikä- ja sukupuolivakioitu. Laskentayksikkö vaihtelee maittain "
        "(henkilöitä tai tapauksia). Lähde: Eurostat (crim_just_ctz, migr_pop5ctz)."
    ),
    "en": (
        "Not age- or sex-standardised. The counting unit varies by country "
        "(persons or cases). Source: Eurostat (crim_just_ctz, migr_pop5ctz)."
    ),
}


def _alaviite(fig: plt.Figure, kieli: str = "fi") -> None:
    fig.text(0.5, 0.012, ALAVIITE[kieli], ha="center", va="bottom", fontsize=7.5, wrap=True)


def _tallenna(fig: plt.Figure, polku: Path) -> None:
    fig.tight_layout(rect=[0.02, 0.08, 0.99, 0.96])
    fig.savefig(polku, dpi=150, bbox_inches="tight")
    plt.close(fig)


def kaavio_eu_per_100k(eu: pd.DataFrame, polku: Path, kieli: str = "fi") -> None:
    d = eu[eu["vuosi"].isin(YEARS_RATE)].set_index("vuosi").reindex(YEARS_RATE)
    fig, ax = plt.subplots(figsize=(11, 6))
    if kieli == "en":
        lab_n, lab_f = "National citizens", "Foreign citizens"
        title = (
            "Convicted persons per 100 000, EU aggregate\n"
            "(countries with data for both groups in that year)"
        )
        xlab, ylab = "Year", "Convicted per 100 000"
        huom = f"Number of countries included: {int(d['n_maata_aste'].min())}–{int(d['n_maata_aste'].max())} (not an official EU-27 series)."
    else:
        lab_n, lab_f = "Oman maan kansalaiset", "Ulkomaan kansalaiset"
        title = (
            "Tuomitut 100 000 asukasta kohden, EU-aggregaatti\n"
            "(maat, joilla data molemmille ryhmille kyseisenä vuonna)"
        )
        xlab, ylab = "Vuosi", "Tuomittuja / 100 000 asukasta"
        huom = f"Mukana olevien maiden lukumäärä: {int(d['n_maata_aste'].min())}–{int(d['n_maata_aste'].max())} (ei virallinen EU-27-sarja)."
    ax.plot(d.index, d["per_100k_NAT"], marker="o", color=VARIT["NAT"], label=lab_n)
    ax.plot(d.index, d["per_100k_FOR"], marker="o", color=VARIT["FOR"], label=lab_f)
    ax.set_title(title)
    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)
    ax.set_xticks(YEARS_RATE)
    ax.tick_params(axis="x", rotation=45)
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.text(0.01, 0.99, huom, transform=ax.transAxes, va="top", fontsize=8)
    _alaviite(fig, kieli)
    _tallenna(fig, polku)


def kaavio_suhdeluku(avg: pd.DataFrame, polku: Path, kieli: str = "fi") -> None:
    d = avg.dropna(subset=["suhde_FOR_NAT"]).copy()
    nimet = MAAN_NIMET_EN if kieli == "en" else MAAN_NIMET
    d["nimi"] = d["geo"].map(nimet)
    d = d.sort_values("suhde_FOR_NAT")
    fig, ax = plt.subplots(figsize=(11, 8))
    ax.barh(d["nimi"], d["suhde_FOR_NAT"], color=VARIT["FOR"])
    if kieli == "en":
        ax.axvline(1.0, color="gray", linestyle="--", linewidth=1, label="Ratio = 1")
        ax.set_title(
            "Ratio of conviction rates, foreign / national citizens\n"
            "2020–2024 mean (years with both groups only)"
        )
        ax.set_xlabel("Ratio (foreign / national)")
    else:
        ax.axvline(1.0, color="gray", linestyle="--", linewidth=1, label="Suhde = 1")
        ax.set_title(
            "Tuomitsemisasteiden suhde, ulkomaan kansalaiset / oman maan kansalaiset\n"
            "Keskiarvo 2020–2024 (vuodet, joilta molemmat ryhmät on laskettu)"
        )
        ax.set_xlabel("Suhde (ulkomaat / oman maan kansalaiset)")
    ax.legend(loc="lower right")
    ax.grid(True, axis="x", alpha=0.3)
    _alaviite(fig, kieli)
    _tallenna(fig, polku)


def kaavio_pienoiskaaviot(df: pd.DataFrame, polku: Path, kieli: str = "fi") -> None:
    n = len(EU27)
    ncols = 4
    nrows = int(np.ceil(n / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(14, 16), sharex=True)
    axes = axes.ravel()
    nimet = MAAN_NIMET_EN if kieli == "en" else MAAN_NIMET
    tyhja = "No data" if kieli == "en" else "Ei dataa"
    for i, geo in enumerate(EU27):
        ax = axes[i]
        s = df[df["geo"] == geo].set_index("vuosi").reindex(YEARS_RATE)
        ax.plot(s.index, s["per_100k_NAT"], color=VARIT["NAT"], linewidth=1.4)
        ax.plot(s.index, s["per_100k_FOR"], color=VARIT["FOR"], linewidth=1.4)
        ax.set_title(nimet[geo], fontsize=9)
        ax.grid(True, alpha=0.25)
        if s["per_100k_NAT"].isna().all() and s["per_100k_FOR"].isna().all():
            ax.set_yticks([])
            ax.text(0.5, 0.5, tyhja, ha="center", va="center", transform=ax.transAxes)
    for j in range(n, len(axes)):
        axes[j].axis("off")
    if kieli == "en":
        fig.suptitle(
            "Convicted persons per 100 000 by country, 2009–2024\n"
            "Blue = national citizens, orange = foreign citizens",
            y=0.995,
            fontsize=12,
        )
        fig.supylabel("Convicted per 100 000")
    else:
        fig.suptitle(
            "Tuomitut 100 000 asukasta kohden maittain, 2009–2024\n"
            "Sininen = oman maan kansalaiset, oranssi = ulkomaan kansalaiset",
            y=0.995,
            fontsize=12,
        )
        fig.supylabel("Tuomittuja / 100 000")
    _alaviite(fig, kieli)
    _tallenna(fig, polku)


def kaavio_absoluuttiset(eu: pd.DataFrame, polku: Path, kieli: str = "fi") -> None:
    d = eu[eu["vuosi"].isin(YEARS_ABS)].set_index("vuosi").reindex(YEARS_ABS)
    fig, ax = plt.subplots(figsize=(11, 6))
    nmin, nmax = int(d["n_maata_abs"].min()), int(d["n_maata_abs"].max())
    if kieli == "en":
        lab_n, lab_f = "National citizens", "Foreign citizens"
        title = (
            "Number of convicted persons, EU aggregate 2008–2024\n"
            "(2008 counts only: migr_pop5ctz has no population for that year)"
        )
        xlab, ylab = "Year", "Convicted persons"
        huom = (
            f"Number of countries included: {nmin}–{nmax}. "
            "The sum is not comparable across years if the set of countries changes."
        )
    else:
        lab_n, lab_f = "Oman maan kansalaiset", "Ulkomaan kansalaiset"
        title = (
            "Tuomittujen lukumäärä, EU-aggregaatti 2008–2024\n"
            "(vuosi 2008 vain lukumäärinä: migr_pop5ctz ei sisällä vuoden 2008 väestöä)"
        )
        xlab, ylab = "Vuosi", "Tuomittuja"
        huom = (
            f"Mukana olevien maiden lukumäärä: {nmin}–{nmax}. "
            "Summa ei ole vertailukelpoinen, jos maiden joukko muuttuu."
        )
    ax.plot(d.index, d["tuomitut_NAT"], marker="o", color=VARIT["NAT"], label=lab_n)
    ax.plot(d.index, d["tuomitut_FOR"], marker="o", color=VARIT["FOR"], label=lab_f)
    ax.set_title(title)
    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)
    ax.set_xticks(YEARS_ABS)
    ax.tick_params(axis="x", rotation=45)
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.text(0.01, 0.99, huom, transform=ax.transAxes, va="top", fontsize=8)
    _alaviite(fig, kieli)
    _tallenna(fig, polku)
