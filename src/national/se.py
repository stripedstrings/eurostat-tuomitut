"""Ruotsi: ohjaa Brå-moduuliin (`src.national.bra`)."""

from __future__ import annotations

import pandas as pd

from src.national import bra
from src.national.bra import loyda_tiedosto  # noqa: F401 — testit / vanha API
from src.national.common import NATIONAL_DIR  # noqa: F401 — testit patchaavat

RAJOITE = bra.RAJOITE
URL = bra.URL
LAHDE = bra.LAHDE


def aja() -> pd.DataFrame:
    return bra.aja()


if __name__ == "__main__":
    aja()
