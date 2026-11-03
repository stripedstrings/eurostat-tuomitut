"""Media × vuosi -peitto: CDX vs HTML. Aukot raportoidaan, ei täytetä."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config import ROOT

TABLES = ROOT / "media" / "output" / "tables"
SRC = TABLES / "coverage_media_vuosi.csv"
OUT_AUKOT = TABLES / "coverage_media_vuosi_aukot.csv"
OUT_MD = ROOT / "media" / "output" / "COVERAGE_AUKOT.md"


def aja() -> pd.DataFrame:
    if not SRC.exists():
        raise FileNotFoundError(SRC)
    df = pd.read_csv(SRC)
    for col in ("n_cdx", "n_cdx_200", "n_html", "n_otsikko_paiva", "n_otsikkoa", "n_paivaa"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["html_puuttuu_kokonaan"] = df["n_html"].fillna(0).eq(0)
    df["osuus_html_per_cdx200"] = df["n_html"] / df["n_cdx_200"].replace(0, pd.NA)
    df["osuus_html_per_kalenteri"] = df["n_html"] / df["n_paivaa"].replace(0, pd.NA)
    # Aukko = HTML < CDX-200; ei täytetä nollaksi osuuslaskentaan
    df["aukko_html_vs_cdx200"] = (df["n_cdx_200"] - df["n_html"]).clip(lower=0)
    df["huom_aukko"] = ""
    tyhja = df["html_puuttuu_kokonaan"]
    df.loc[tyhja, "huom_aukko"] = "n_html=0; ei täytetä nollaksi"
    ohut = (~tyhja) & (df["osuus_html_per_cdx200"].lt(0.5))
    df.loc[ohut, "huom_aukko"] = "HTML << CDX-200; peitto vajaata"
    df.loc[df["n_cdx_200"].isna(), "huom_aukko"] = "CDX puuttuu"

    cols = [
        "media",
        "vuosi",
        "n_paivaa",
        "n_cdx",
        "n_cdx_200",
        "n_html",
        "n_otsikko_paiva",
        "n_otsikkoa",
        "aukko_html_vs_cdx200",
        "osuus_html_per_cdx200",
        "osuus_html_per_kalenteri",
        "html_puuttuu_kokonaan",
        "huom_aukko",
    ]
    out = df[cols].sort_values(["media", "vuosi"])
    TABLES.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_AUKOT, index=False)

    rivit = [
        "# Coverage-aukot: media × vuosi (CDX / HTML)",
        "",
        "Lähde: `coverage_media_vuosi.csv`. Puuttuvaa ei täytetä.",
        "HS ja MTV: ei vielä haettu (esirekisteröinti 2026-11-03).",
        "",
        "| media | vuosi | n_cdx_200 | n_html | aukko | huom |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for r in out.itertuples(index=False):
        auk = "" if pd.isna(r.aukko_html_vs_cdx200) else int(r.aukko_html_vs_cdx200)
        rivit.append(
            f"| {r.media} | {int(r.vuosi)} | {int(r.n_cdx_200) if pd.notna(r.n_cdx_200) else ''} "
            f"| {int(r.n_html) if pd.notna(r.n_html) else ''} | {auk} | {r.huom_aukko} |"
        )
    kokonaan = out.loc[out["html_puuttuu_kokonaan"], ["media", "vuosi"]]
    rivit.extend(
        [
            "",
            "## Vuodet ilman HTML:ää",
            "",
        ]
    )
    if kokonaan.empty:
        rivit.append("(ei yhtään)")
    else:
        for r in kokonaan.itertuples(index=False):
            rivit.append(f"- {r.media} {int(r.vuosi)}")
    OUT_MD.write_text("\n".join(rivit) + "\n", encoding="utf-8")
    return out


if __name__ == "__main__":
    t = aja()
    print("kirjoitettu", OUT_AUKOT, "rivit", len(t))
    print("kirjoitettu", OUT_MD)
