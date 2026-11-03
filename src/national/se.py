"""Ruotsi: ohjaa Brå-moduuliin (`src.national.bra`)."""

from __future__ import annotations

import pandas as pd

from src.national import bra


def aja() -> pd.DataFrame:
    return bra.aja()


if __name__ == "__main__":
    aja()
