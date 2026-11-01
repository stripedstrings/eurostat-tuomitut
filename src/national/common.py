"""Kansalliset aineistot: erillään EU-aggregaatista. Ei täyttöä."""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

import pandas as pd

from src.config import DPI_KUVA, FIGURES_DIR, ROOT, TABLES_DIR

NATIONAL_DIR = ROOT / "data" / "national"
NATIONAL_MANIFEST = NATIONAL_DIR / "MANIFEST.csv"
NATIONAL_TABLES = TABLES_DIR / "national"


def kirjaa_manifest(tiedosto: str, lahde: str, url: str, huom: str) -> None:
    NATIONAL_DIR.mkdir(parents=True, exist_ok=True)
    kentat = ["tiedosto", "lähde", "URL", "hakupäivä", "huomiot"]
    rivit: list[dict[str, str]] = []
    if NATIONAL_MANIFEST.exists() and NATIONAL_MANIFEST.stat().st_size > 0:
        with NATIONAL_MANIFEST.open(encoding="utf-8", newline="") as f:
            rivit = list(csv.DictReader(f))
    rivit = [r for r in rivit if r.get("tiedosto") != tiedosto]
    rivit.append(
        {
            "tiedosto": tiedosto,
            "lähde": lahde,
            "URL": url,
            "hakupäivä": date.today().isoformat(),
            "huomiot": huom,
        }
    )
    with NATIONAL_MANIFEST.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=kentat)
        w.writeheader()
        w.writerows(rivit)


def unique_sarakkeet(df: pd.DataFrame, nimi: str) -> str:
    lines = [f"=== {nimi} ===", f"rivit={len(df)} sarakkeet={list(df.columns)}"]
    for col in df.columns:
        vals = sorted(df[col].dropna().astype(str).unique().tolist())
        lines.append(f"{col}: nunique={len(vals)}")
        if len(vals) <= 40:
            lines.append("unique: " + ", ".join(vals))
    return "\n".join(lines) + "\n"


def tallenna_kuvio(fig, polku: Path, alaviite: str) -> None:
    import matplotlib.pyplot as plt

    fig.text(0.5, 0.01, alaviite, ha="center", va="bottom", fontsize=7, wrap=True)
    fig.tight_layout(rect=[0.03, 0.12, 0.99, 0.96])
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(polku, dpi=DPI_KUVA)
    plt.close(fig)
