"""Esirekisteröidyt peruskaaviot suomeksi, 200 dpi. Ei täyttöä."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.config import (
    ASTEET_PATH,
    DPI_KUVA,
    EU27,
    EU_AGGR_PATH,
    FIGURES_DIR,
    KAUSI_RR_PATH,
    MANIFEST_PATH,
    VARIT,
    YEARS_ABS,
    YEARS_RATE,
)


def hakupaiva() -> str:
    man = pd.read_csv(MANIFEST_PATH)
    rivit = man[man["tiedosto"].isin(["crim_just_ctz.csv", "migr_pop5ctz.csv"])]
    return str(rivit["hakupäivä"].max())


def alaviitteet() -> str:
    pvm = hakupaiva()
    return (
        f"Lähde: Eurostat crim_just_ctz, migr_pop5ctz, haettu {pvm}. "
        "Ei ikä- ja sukupuolivakioitu. "
        "Kansalaisuus ei kuvaa maahanmuuttotaustaa tai pakolaisuutta. "
        "Laskentayksikkö vaihtelee maittain; maiden välinen vertailu on rajallinen. "
        "Katkos viivassa = data puuttuu. "
        "Epäluotettavat (D<10) merkitään erikseen; maita ei poisteta."
    )


def _tallenna(fig: plt.Figure, polku: Path) -> None:
    fig.text(0.5, 0.01, alaviitteet(), ha="center", va="bottom", fontsize=7, wrap=True)
    fig.tight_layout(rect=[0.03, 0.10, 0.99, 0.96])
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(polku, dpi=DPI_KUVA)
    plt.close(fig)


def kaavio_eu_per_100k(eu: pd.DataFrame, polku: Path) -> None:
    d = eu[eu["vuosi"].isin(YEARS_RATE)].set_index("vuosi").reindex(YEARS_RATE)
    fig, (ax, ax2) = plt.subplots(
        2, 1, figsize=(11, 8), sharex=True, gridspec_kw={"height_ratios": [3, 1.2]}
    )
    ax.plot(d.index, d["aste_NAT"], marker="o", color=VARIT["NAT"], label="Oman maan kansalaiset")
    ax.plot(d.index, d["aste_FOR"], marker="o", color=VARIT["FOR"], label="Ulkomaan kansalaiset")
    ax.set_title(
        "Tuomitut 100 000 asukasta kohden, EU-aggregaatti 2009–2024\n"
        "Mukana vain maat, joilla NAT- ja FOR-osoittaja ja -nimittäjä samana vuonna"
    )
    ax.set_ylabel("Tuomittuja / 100 000 asukasta")
    ax.legend()
    ax.grid(True, alpha=0.3)

    ax2.plot(d.index, d["n_maata_aste"], marker="s", color="#333333", label="Maiden lukumäärä")
    ax2.set_ylabel("Maita")
    ax2b = ax2.twinx()
    ax2b.plot(
        d.index,
        d["vaesto_osuus"] * 100,
        marker="^",
        color="#6a3d9a",
        label="Väestöosuus %",
    )
    ax2b.set_ylabel("Väestöosuus (%)")
    ax2.set_xlabel("Vuosi")
    ax2.set_xticks(YEARS_RATE)
    ax2.tick_params(axis="x", rotation=45)
    ax2.grid(True, alpha=0.3)
    h1, l1 = ax2.get_legend_handles_labels()
    h2, l2 = ax2b.get_legend_handles_labels()
    ax2.legend(h1 + h2, l1 + l2, loc="upper left", fontsize=8)
    _tallenna(fig, polku)


def kaavio_rr_forest(kausi: pd.DataFrame, polku: Path) -> None:
    d = kausi.copy()
    d["on_data"] = d["RR"].notna()
    jarj = d[d["on_data"]].sort_values("RR")
    tyhja = d[~d["on_data"]].sort_values("maa")
    d = pd.concat([tyhja, jarj], ignore_index=True)
    y = np.arange(len(d))
    fig, ax = plt.subplots(figsize=(11, 10))
    ax.axvline(1.0, color="gray", linestyle="--", linewidth=1, label="RR = 1")
    mask = d["on_data"].to_numpy()
    xerr = np.vstack(
        [
            d.loc[mask, "RR"] - d.loc[mask, "RR_lo"],
            d.loc[mask, "RR_hi"] - d.loc[mask, "RR"],
        ]
    )
    ax.errorbar(
        d.loc[mask, "RR"],
        y[mask],
        xerr=xerr,
        fmt="o",
        color=VARIT["FOR"],
        ecolor="#555555",
        capsize=3,
        label="RR (yhteenlasketut kelpoiset vuodet 2020–2024)",
    )
    epa_mask = mask & d["epaluotettava"].fillna(False).to_numpy()
    if epa_mask.any():
        ax.scatter(
            d.loc[epa_mask, "RR"],
            y[epa_mask],
            marker="D",
            color="black",
            zorder=5,
            label="D<10",
        )
    if (~mask).any():
        ax.scatter(
            np.full((~mask).sum(), 1.0),
            y[~mask],
            marker="x",
            color="#888888",
            label="Ei kelpoista vuotta 2020–2024",
        )
    nimet = [
        f"{r.maa} ({int(r.n_vuotta)} v)" if r.on_data else f"{r.maa} (ei dataa)"
        for r in d.itertuples()
    ]
    ax.set_yticks(y)
    ax.set_yticklabels(nimet)
    ax.set_xlabel("RR = aste(FOR) / aste(NAT), 95 % Poisson-väli (log-skaala)")
    ax.set_title(
        "Tuomitsemisasteiden suhde maittain, 2020–2024\n"
        "Yhteenlasketut kelpoiset vuodet (puuttuvia ei täytetä). Kaikki EU-27-maat."
    )
    ax.grid(True, axis="x", alpha=0.3)
    ax.legend(loc="upper left", fontsize=8)
    _tallenna(fig, polku)


def kaavio_pienoiskaaviot(asteet: pd.DataFrame, polku: Path) -> None:
    n = len(EU27)
    ncols = 4
    nrows = int(np.ceil(n / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(14, 16), sharex=True)
    axes = axes.ravel()
    for i, geo in enumerate(EU27):
        ax = axes[i]
        s = asteet[asteet["geo"] == geo].set_index("vuosi").reindex(YEARS_RATE)
        ax.plot(s.index, s["aste_NAT"], color=VARIT["NAT"], linewidth=1.4)
        ax.plot(s.index, s["aste_FOR"], color=VARIT["FOR"], linewidth=1.4)
        epa = s[s["epaluotettava"] == True]  # noqa: E712
        if len(epa):
            ax.scatter(epa.index, epa["aste_FOR"], marker="D", color="black", s=18, zorder=5)
        maa = s["maa"].dropna().iloc[0] if s["maa"].notna().any() else geo
        ax.set_title(maa, fontsize=9)
        ax.grid(True, alpha=0.25)
        if s["aste_NAT"].isna().all() and s["aste_FOR"].isna().all():
            ax.set_yticks([])
            ax.text(0.5, 0.5, "Ei dataa", ha="center", va="center", transform=ax.transAxes)
    for j in range(n, len(axes)):
        axes[j].axis("off")
    fig.suptitle(
        "Tuomitut 100 000 asukasta kohden maittain, 2009–2024\n"
        "Sininen = oman maan kansalaiset, oranssi = ulkomaan kansalaiset. Musta timantti = D<10.",
        y=0.995,
        fontsize=12,
    )
    fig.supylabel("Tuomittuja / 100 000")
    _tallenna(fig, polku)


def kaavio_absoluuttiset(eu: pd.DataFrame, polku: Path) -> None:
    d = eu[eu["vuosi"].isin(YEARS_ABS)].set_index("vuosi").reindex(YEARS_ABS)
    fig, ax = plt.subplots(figsize=(11, 6.5))
    ax.plot(d.index, d["tuomitut_NAT"], marker="o", color=VARIT["NAT"], label="Oman maan kansalaiset")
    ax.plot(d.index, d["tuomitut_FOR"], marker="o", color=VARIT["FOR"], label="Ulkomaan kansalaiset")
    nmin, nmax = int(d["n_maata_abs"].min()), int(d["n_maata_abs"].max())
    ax.set_title(
        "Tuomittujen lukumäärä, EU-aggregaatti 2008–2024\n"
        "Summa maista, joilla NAT- ja FOR-lukumäärä samana vuonna (vuosi 2008 ilman väestöä)"
    )
    ax.set_xlabel("Vuosi")
    ax.set_ylabel("Tuomittuja")
    ax.set_xticks(YEARS_ABS)
    ax.tick_params(axis="x", rotation=45)
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.text(
        0.01,
        0.99,
        f"Mukana olevien maiden lukumäärä: {nmin}–{nmax}. Joukon muutos tekee vuosista ei-vertailukelpoisia.",
        transform=ax.transAxes,
        va="top",
        fontsize=8,
    )
    _tallenna(fig, polku)


def aja() -> None:
    plt.switch_backend("Agg")
    from src.rates import aja as aja_asteet

    aja_asteet()
    asteet = pd.read_csv(ASTEET_PATH)
    eu = pd.read_csv(EU_AGGR_PATH)
    kausi = pd.read_csv(KAUSI_RR_PATH)

    kaavio_eu_per_100k(eu, FIGURES_DIR / "01_eu_per_100000.png")
    kaavio_rr_forest(kausi, FIGURES_DIR / "02_rr_forest_2020_2024.png")
    kaavio_pienoiskaaviot(asteet, FIGURES_DIR / "03_small_multiples.png")
    kaavio_absoluuttiset(eu, FIGURES_DIR / "04_absoluuttiset.png")
    print(f"Kaaviot: {FIGURES_DIR}")
    print(eu[["vuosi", "n_maata_aste", "n_maata_abs", "vaesto_osuus"]].to_string(index=False))
    print(f"Forest: maita datalla={int(kausi['RR'].notna().sum())} / {len(kausi)}")


if __name__ == "__main__":
    aja()
