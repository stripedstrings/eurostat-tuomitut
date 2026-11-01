"""Kaikki kaaviot suomeksi; NaN = katkos viivassa."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.config import ALAVIITE, EU27, MAAN_NIMET, OUTPUT_DIR, VARIT, YEARS_ABS, YEARS_RATE


def _alaviite(fig: plt.Figure) -> None:
    fig.text(0.5, 0.012, ALAVIITE, ha="center", va="bottom", fontsize=7.5, wrap=True)


def _tallenna(fig: plt.Figure, polku: Path) -> None:
    fig.tight_layout(rect=[0.02, 0.08, 0.99, 0.96])
    fig.savefig(polku, dpi=150, bbox_inches="tight")
    plt.close(fig)


def kaavio_eu_per_100k(eu: pd.DataFrame, polku: Path) -> None:
    d = eu[eu["vuosi"].isin(YEARS_RATE)].set_index("vuosi").reindex(YEARS_RATE)
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.plot(
        d.index,
        d["per_100k_NAT"],
        marker="o",
        color=VARIT["NAT"],
        label="Oman maan kansalaiset",
    )
    ax.plot(
        d.index,
        d["per_100k_FOR"],
        marker="o",
        color=VARIT["FOR"],
        label="Ulkomaan kansalaiset",
    )
    ax.set_title(
        "Tuomitut 100 000 asukasta kohden, EU-aggregaatti\n"
        "(vain maat, joilla data molemmille ryhmille kyseisenä vuonna)"
    )
    ax.set_xlabel("Vuosi")
    ax.set_ylabel("Tuomittuja / 100 000 asukasta")
    ax.set_xticks(YEARS_RATE)
    ax.tick_params(axis="x", rotation=45)
    ax.legend()
    ax.grid(True, alpha=0.3)
    nmin, nmax = int(d["n_maata_aste"].min()), int(d["n_maata_aste"].max())
    ax.text(
        0.01,
        0.99,
        f"Mukana olevien maiden lukumäärä vaihtelee: {nmin}–{nmax} (ei virallinen EU-27-luku).",
        transform=ax.transAxes,
        va="top",
        fontsize=8,
    )
    _alaviite(fig)
    _tallenna(fig, polku)


def kaavio_suhdeluku(avg: pd.DataFrame, polku: Path) -> None:
    d = avg.dropna(subset=["suhde_FOR_NAT"]).sort_values("suhde_FOR_NAT")
    fig, ax = plt.subplots(figsize=(11, 8))
    ax.barh(d["maa"], d["suhde_FOR_NAT"], color=VARIT["FOR"])
    ax.axvline(1.0, color="gray", linestyle="--", linewidth=1, label="Suhde = 1")
    ax.set_title(
        "Ulkomaan kansalaisten ja oman maan kansalaisten tuomitsemisasteen suhde\n"
        "2020–2024 keskiarvo (vain vuodet, joilla molemmat ryhmät saatavilla)"
    )
    ax.set_xlabel("Suhde (ulkomaat / oman maan kansalaiset)")
    ax.legend(loc="lower right")
    ax.grid(True, axis="x", alpha=0.3)
    _alaviite(fig)
    _tallenna(fig, polku)


def kaavio_pienoiskaaviot(df: pd.DataFrame, polku: Path) -> None:
    n = len(EU27)
    ncols = 4
    nrows = int(np.ceil(n / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(14, 16), sharex=True)
    axes = axes.ravel()
    for i, geo in enumerate(EU27):
        ax = axes[i]
        s = df[df["geo"] == geo].set_index("vuosi").reindex(YEARS_RATE)
        ax.plot(s.index, s["per_100k_NAT"], color=VARIT["NAT"], linewidth=1.4)
        ax.plot(s.index, s["per_100k_FOR"], color=VARIT["FOR"], linewidth=1.4)
        ax.set_title(MAAN_NIMET[geo], fontsize=9)
        ax.grid(True, alpha=0.25)
        if s["per_100k_NAT"].isna().all() and s["per_100k_FOR"].isna().all():
            ax.set_yticks([])
            ax.text(0.5, 0.5, "Ei dataa", ha="center", va="center", transform=ax.transAxes)
    for j in range(n, len(axes)):
        axes[j].axis("off")
    fig.suptitle(
        "Tuomitut 100 000 asukasta kohden maittain, 2009–2024\n"
        "Sininen = oman maan kansalaiset, oranssi = ulkomaan kansalaiset",
        y=0.995,
        fontsize=12,
    )
    fig.supylabel("Tuomittuja / 100 000")
    _alaviite(fig)
    _tallenna(fig, polku)


def kaavio_absoluuttiset(eu: pd.DataFrame, polku: Path) -> None:
    d = eu[eu["vuosi"].isin(YEARS_ABS)].set_index("vuosi").reindex(YEARS_ABS)
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.plot(
        d.index,
        d["tuomitut_NAT"],
        marker="o",
        color=VARIT["NAT"],
        label="Oman maan kansalaiset",
    )
    ax.plot(
        d.index,
        d["tuomitut_FOR"],
        marker="o",
        color=VARIT["FOR"],
        label="Ulkomaan kansalaiset",
    )
    ax.set_title(
        "Tuomittujen absoluuttinen määrä, EU-aggregaatti 2008–2024\n"
        "(2008 vain absoluuttisina: väestöä ei ole migr_pop5ctz-aineistossa)"
    )
    ax.set_xlabel("Vuosi")
    ax.set_ylabel("Tuomittuja (lukumäärä)")
    ax.set_xticks(YEARS_ABS)
    ax.tick_params(axis="x", rotation=45)
    ax.legend()
    ax.grid(True, alpha=0.3)
    nmin, nmax = int(d["n_maata_abs"].min()), int(d["n_maata_abs"].max())
    ax.text(
        0.01,
        0.99,
        f"Mukana olevien maiden lukumäärä vaihtelee: {nmin}–{nmax}. "
        "Summa ei ole vertailukelpoinen vuosien välillä, jos joukko muuttuu.",
        transform=ax.transAxes,
        va="top",
        fontsize=8,
    )
    _alaviite(fig)
    _tallenna(fig, polku)
