"""Eurostat SDMX-CSV -haku, välimuisti data/raw, MANIFEST.csv."""

from __future__ import annotations

import csv
import subprocess
from datetime import date
from pathlib import Path

import pandas as pd

from src.config import CACHE_DIR, INTERIM_DIR, MANIFEST_PATH, SDMX_CSV_URL

DIM_COLS = (
    "freq",
    "leg_stat",
    "citizen",
    "c_birth",
    "unit",
    "sex",
    "age",
    "geo",
    "TIME_PERIOD",
    "OBS_FLAG",
    "CONF_STATUS",
)

DATASETS = {
    "crim_just_ctz": "Suspects and offenders by citizenship",
    "migr_pop5ctz": "Population on 1 January by sex, citizenship and group of country of birth",
    "migr_pop1ctz": "Population on 1 January by age group, sex and citizenship",
    "migr_pop3ctb": "Population on 1 January by age group, sex and country of birth",
}

USER_AGENT = "eu-rikollisuus-kansalaisuus/0.1 (tutkimuskäyttö)"


def cache_path(dataset_code: str) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / f"{dataset_code}.csv"


def _kirjaa_manifest(tiedosto: str, url: str, kuvaus: str, huomiot: str) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    kentat = ["tiedosto", "lähde", "URL", "hakupäivä", "kuvaus", "huomiot"]
    rivit: list[dict[str, str]] = []
    if MANIFEST_PATH.exists() and MANIFEST_PATH.stat().st_size > 0:
        with MANIFEST_PATH.open(encoding="utf-8", newline="") as f:
            rivit = list(csv.DictReader(f))
    rivit = [r for r in rivit if r.get("tiedosto") != tiedosto]
    rivit.append(
        {
            "tiedosto": tiedosto,
            "lähde": "Eurostat",
            "URL": url,
            "hakupäivä": date.today().isoformat(),
            "kuvaus": kuvaus,
            "huomiot": huomiot,
        }
    )
    with MANIFEST_PATH.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=kentat)
        w.writeheader()
        w.writerows(rivit)


def fetch_sdmx_csv(dataset_code: str, refresh: bool = False) -> Path:
    path = cache_path(dataset_code)
    url = SDMX_CSV_URL.format(code=dataset_code)
    kuvaus = DATASETS.get(dataset_code, dataset_code)
    if path.exists() and path.stat().st_size > 0 and not refresh:
        _kirjaa_manifest(
            path.name,
            url,
            kuvaus,
            f"välimuisti; koko_tavua={path.stat().st_size}",
        )
        return path
    # Windows: Pythonin SSL ei aina löydä järjestelmän CA-ketjua; curl löytää.
    subprocess.run(
        ["curl.exe", "-fsSL", "-A", USER_AGENT, "-o", str(path), url],
        check=True,
    )
    _kirjaa_manifest(
        path.name,
        url,
        kuvaus,
        f"koko_tavua={path.stat().st_size}",
    )
    return path


def load_dataset(dataset_code: str, refresh: bool = False) -> pd.DataFrame:
    path = fetch_sdmx_csv(dataset_code, refresh=refresh)
    return pd.read_csv(path, low_memory=False)


def inspect_dimensions(df: pd.DataFrame, nimi: str) -> str:
    """Tulosta .nunique() ja .unique() dimensioille. Koodeja ei arvata."""
    lines = [f"=== {nimi} ===", f"rivit={len(df)} sarakkeet={list(df.columns)}"]
    for col in df.columns:
        nun = int(df[col].nunique(dropna=False))
        lines.append(f"\n{col}: nunique={nun}")
        if col not in DIM_COLS and col not in {"DATAFLOW", "LAST UPDATE"}:
            continue
        values = sorted(df[col].dropna().astype(str).unique().tolist())
        if len(values) > 80:
            lines.append("unique (80 ensimmäistä): " + ", ".join(values[:80]) + " ...")
            avain = [
                v
                for v in (
                    "NAT",
                    "FOR",
                    "TOTAL",
                    "UNK",
                    "STLS",
                    "FOR_STLS",
                    "PER_CNV",
                    "PER_SUSP",
                    "PER_PRSC",
                    "NR",
                    "P_HTHAB",
                    "T",
                    "Y_LT15",
                    "TOTAL",
                )
                if v in values
            ]
            if avain:
                lines.append("avainkoodit: " + ", ".join(dict.fromkeys(avain)))
        else:
            lines.append("unique: " + ", ".join(values) if values else "unique: (tyhjä)")
        nan_n = int(df[col].isna().sum())
        if nan_n:
            lines.append(f"NaN-rivejä: {nan_n}")
    return "\n".join(lines) + "\n"


def hae_kaikki(refresh: bool = False) -> None:
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    osat: list[str] = []
    for koodi, kuvaus in DATASETS.items():
        print(f"Haetaan {koodi} ({kuvaus})...", flush=True)
        df = load_dataset(koodi, refresh=refresh)
        teksti = inspect_dimensions(df, koodi)
        (INTERIM_DIR / f"dimensiot_{koodi}.txt").write_text(teksti, encoding="utf-8")
        osat.append(teksti)
        print(teksti)
    (INTERIM_DIR / "dimensiot.txt").write_text("\n".join(osat), encoding="utf-8")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    hae_kaikki(refresh=args.refresh)
