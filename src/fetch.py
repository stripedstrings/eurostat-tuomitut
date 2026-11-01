"""Eurostat SDMX-CSV -haku paikallisella välimuistilla."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests

from src.config import CACHE_DIR, SDMX_CSV_URL

# Dimensiosarakkeet, joista tulostetaan unique-arvot.
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


def cache_path(dataset_code: str) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / f"{dataset_code}.csv"


def fetch_sdmx_csv(dataset_code: str, refresh: bool = False) -> Path:
    """Hae koko datasetti SDMX-CSV:nä. Käytä välimuistia, ellei refresh=True."""
    path = cache_path(dataset_code)
    if path.exists() and path.stat().st_size > 0 and not refresh:
        return path

    url = SDMX_CSV_URL.format(code=dataset_code)
    headers = {"User-Agent": "eurostat-tuomitut/1.0 (tutkimuskäyttö)"}
    response = requests.get(url, headers=headers, timeout=180)
    response.raise_for_status()
    path.write_bytes(response.content)
    return path


def load_dataset(dataset_code: str, refresh: bool = False) -> pd.DataFrame:
    path = fetch_sdmx_csv(dataset_code, refresh=refresh)
    return pd.read_csv(path, low_memory=False)


def inspect_dimensions(df: pd.DataFrame, nimi: str) -> str:
    """Palauta .nunique() ja .unique() jokaiselle dimensiolle (ei arvata koodeja)."""
    lines = [f"=== {nimi} ===", f"rivit={len(df)} sarakkeet={list(df.columns)}"]
    for col in df.columns:
        nun = int(df[col].nunique(dropna=False))
        lines.append(f"\n{col}: nunique={nun}")
        if col not in DIM_COLS and col not in {"DATAFLOW", "LAST UPDATE"}:
            continue
        # Pitkät koodilistat (esim. citizen-maakoodit) katkaistaan luettavuuden vuoksi.
        values = sorted(df[col].dropna().astype(str).unique().tolist())
        if len(values) > 80:
            lines.append("unique (80 ensimmäistä): " + ", ".join(values[:80]) + " ...")
            avain = [v for v in ("NAT", "FOR", "TOTAL", "UNK", "STLS", "FOR_STLS") if v in values]
            if avain:
                lines.append("avainkoodit citizen/c_birth: " + ", ".join(avain))
        else:
            lines.append("unique: " + ", ".join(values) if values else "unique: (tyhjä)")
        nan_n = int(df[col].isna().sum())
        if nan_n:
            lines.append(f"NaN-rivejä: {nan_n}")
    return "\n".join(lines) + "\n"
